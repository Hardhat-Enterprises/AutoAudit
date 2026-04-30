"""Mailboxes collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 1.2.2

Connection Method: Microsoft Graph API
Required Application Permissions: User.Read.All
Graph Endpoints:
    - GET /users (paginated)

Implementation note:
    Graph does not expose Exchange RecipientTypeDetails, so shared mailboxes
    cannot be identified with the same fidelity as Exchange Online PowerShell.
    Candidates are approximated as member users with a mail address and no
    assigned licenses. SignInBlocked is derived from accountEnabled. Licensed
    shared mailboxes and hybrid edge cases may be omitted; Exchange Online
    remains authoritative for BlockCredentials semantics.
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class MailboxesDataCollector(BaseDataCollector):
    """Collects shared mailbox sign-in posture using Microsoft Graph."""

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        users = await client.get_all_pages(
            "/users",
            params={
                "$select": (
                    "id,userPrincipalName,displayName,accountEnabled,"
                    "mail,userType,assignedLicenses"
                ),
            },
        )

        mailboxes: list[dict[str, Any]] = []
        for u in users:
            if u.get("userType") == "Guest":
                continue
            mail = u.get("mail") or u.get("userPrincipalName")
            if not mail:
                continue
            licenses = u.get("assignedLicenses") or []
            if licenses:
                continue

            ae = u.get("accountEnabled")
            sign_in_blocked = None if ae is None else (not ae)

            mailboxes.append(
                {
                    "UserPrincipalName": u.get("userPrincipalName"),
                    "DisplayName": u.get("displayName"),
                    "PrimarySmtpAddress": mail,
                    "accountEnabled": ae,
                    "SignInBlocked": sign_in_blocked,
                }
            )

        signin_blocked = [m for m in mailboxes if m.get("SignInBlocked") is True]
        signin_allowed = [m for m in mailboxes if m.get("SignInBlocked") is not True]

        return {
            "shared_mailboxes": mailboxes,
            "total_shared_mailboxes": len(mailboxes),
            "mailboxes_with_signin_blocked": len(signin_blocked),
            "mailboxes_with_signin_allowed": len(signin_allowed),
            "detection_method": "graph_user_heuristic_unlicensed_mail_members",
            "detection_limitations": (
                "Shared mailbox identification is approximate without Exchange "
                "recipient metadata. Only member users with mail and no "
                "assignedLicenses are evaluated; licensed shared mailboxes may "
                "be omitted."
            ),
        }
