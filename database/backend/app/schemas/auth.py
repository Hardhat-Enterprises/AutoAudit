from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True  # Pydantic v2 (works like orm_mode)

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: str | None = None
