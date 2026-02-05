import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_users import exceptions
from fastapi.responses import RedirectResponse
from httpx_oauth.clients.google import GoogleOAuth2

from app.core.config import get_settings
from app.core.users import auth_backend, fastapi_users, get_jwt_strategy, get_user_manager
from app.schemas.user import UserRead, UserCreate, UserRegister, UserUpdate
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Registration endpoint (creates users in DB; stores hashed_password)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserRegister),
    prefix="",
)

# Login endpoint
router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="",
)

# User management endpoints
users_router = APIRouter(prefix="/users", tags=["Users"])

# Get current user info
@users_router.get("/me", summary="Get my user information", response_model=UserRead)
async def read_users_me(user: User = Depends(get_current_user)):
    """Get current authenticated user information."""
    return user


# Change password endpoint
from pydantic import BaseModel

class PasswordChange(BaseModel):
    current_password: str
    new_password: str


@users_router.post("/me/change-password")
async def change_password(
    password_data: PasswordChange,
    user: User = Depends(get_current_user),
):
    """Change current user's password."""
    from app.core.users import get_user_manager
    from app.db.session import get_async_session
    from fastapi import Request

    # Create a mock request object for fastapi-users
    request = Request(scope={"type": "http"})

    async for session in get_async_session():
        async for user_manager in get_user_manager(session):
            try:
                # Verify current password
                verified, updated_password_hash = user_manager.password_helper.verify_and_update(
                    password_data.current_password, user.hashed_password
                )
                if not verified:
                    raise exceptions.InvalidPasswordException()

                # Hash new password
                new_hashed_password = user_manager.password_helper.hash(password_data.new_password)

                # Update user password
                user.hashed_password = new_hashed_password
                await session.commit()

                return {"message": "Password changed successfully"}

            except exceptions.InvalidPasswordException:
                from fastapi import HTTPException
                raise HTTPException(status_code=400, detail="Invalid current password")


# Include users router
router.include_router(users_router)


GOOGLE_OAUTH_STATE_COOKIE = "google_oauth_state"


def _google_redirect_uri() -> str:
    settings = get_settings()
    return f"{settings.BACKEND_PUBLIC_URL}{settings.API_PREFIX}/auth/google/callback"


def _frontend_google_callback_url(fragment_params: dict[str, str]) -> str:
    settings = get_settings()
    base = settings.FRONTEND_URL.rstrip("/")
    fragment = urlencode(fragment_params)
    return f"{base}/auth/google/callback#{fragment}"


def _google_oauth_client() -> GoogleOAuth2:
    settings = get_settings()
    if not settings.GOOGLE_OAUTH_CLIENT_ID or not settings.GOOGLE_OAUTH_CLIENT_SECRET:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Google OAuth is not configured (missing GOOGLE_OAUTH_CLIENT_ID/SECRET).",
        )
    return GoogleOAuth2(
        settings.GOOGLE_OAUTH_CLIENT_ID,
        settings.GOOGLE_OAUTH_CLIENT_SECRET,
        scopes=["openid", "email", "profile"],
        name="google",
    )


@router.get("/google/authorize")
async def google_authorize() -> RedirectResponse:
    """Start Google OAuth (redirect to Google authorize URL)."""
    settings = get_settings()
    state = secrets.token_urlsafe(32)

    try:
        client = _google_oauth_client()
    except HTTPException as exc:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "oauth_not_configured",
                    "error_description": str(exc.detail),
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    authorize_url = await client.get_authorization_url(
        redirect_uri=_google_redirect_uri(),
        state=state,
        scope=["openid", "email", "profile"],
        # Don't force prompt=select_account; it adds an extra step and slows SSO.
        extras_params=None,
    )

    response = RedirectResponse(authorize_url, status_code=status.HTTP_302_FOUND)
    response.set_cookie(
        key=GOOGLE_OAUTH_STATE_COOKIE,
        value=state,
        max_age=600,
        httponly=True,
        secure=settings.BACKEND_PUBLIC_URL.startswith("https://"),
        samesite="lax",
        path=f"{settings.API_PREFIX}/auth/google/callback",
    )
    return response


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    user_manager=Depends(get_user_manager),
) -> RedirectResponse:
    """Google OAuth callback: exchange code, link/create user, mint AutoAudit JWT, redirect to FE."""
    settings = get_settings()

    cookie_state = request.cookies.get(GOOGLE_OAUTH_STATE_COOKIE)
    if not state or not cookie_state or state != cookie_state:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "invalid_state",
                    "error_description": "Invalid OAuth state. Please try again.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    if not code:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "missing_code",
                    "error_description": "Google did not return an authorization code.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    client = _google_oauth_client()

    try:
        token = await client.get_access_token(code, redirect_uri=_google_redirect_uri())
        google_access_token = token["access_token"]
    except Exception:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "token_exchange_failed",
                    "error_description": "Failed to exchange authorization code for tokens.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    # Fetch OIDC userinfo for email + verification + stable subject identifier (sub).
    try:
        async with httpx.AsyncClient(timeout=10.0) as http:
            resp = await http.get(
                "https://openidconnect.googleapis.com/v1/userinfo",
                headers={"Authorization": f"Bearer {google_access_token}"},
            )
        resp.raise_for_status()
        profile = resp.json()
    except Exception:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "userinfo_failed",
                    "error_description": "Failed to fetch Google user profile.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    email = profile.get("email")
    email_verified = profile.get("email_verified")
    sub = profile.get("sub")

    if not email or not sub:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "invalid_profile",
                    "error_description": "Google profile is missing required fields.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    # Link-by-email requires the email to be verified to avoid account takeover.
    if email_verified is not True:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "email_not_verified",
                    "error_description": "Google account email is not verified.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    try:
        user = await user_manager.oauth_callback(
            oauth_name="google",
            access_token=google_access_token,
            account_id=sub,
            account_email=email,
            expires_at=token.get("expires_at"),
            refresh_token=token.get("refresh_token"),
            request=request,
            associate_by_email=True,
            is_verified_by_default=True,
        )
    except Exception:
        return RedirectResponse(
            _frontend_google_callback_url(
                {
                    "error": "user_link_failed",
                    "error_description": "Failed to link Google account to user.",
                }
            ),
            status_code=status.HTTP_302_FOUND,
        )

    # fastapi-users JWTStrategy.write_token is async in the version used by the backend container.
    autoaudit_token = await get_jwt_strategy().write_token(user)
    redirect_url = _frontend_google_callback_url(
        {"access_token": autoaudit_token, "token_type": "bearer"}
    )

    response = RedirectResponse(redirect_url, status_code=status.HTTP_302_FOUND)
    response.delete_cookie(
        GOOGLE_OAUTH_STATE_COOKIE,
        path=f"{settings.API_PREFIX}/auth/google/callback",
    )
    return response
