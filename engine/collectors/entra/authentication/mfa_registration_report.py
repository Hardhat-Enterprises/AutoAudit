"""MFA registration report collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 5.2.3.4

Connection Method: Microsoft Graph API
Required Scopes: UserAuthenticationMethod.Read.All, AuditLog.Read.All
Graph Endpoint: /reports/authenticationMethods/userRegistrationDetails
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class MFARegistrationReportDataCollector(BaseDataCollector):
    """Collects MFA registration report for CIS compliance evaluation.

    This collector retrieves MFA capable user registration details
    to verify users have registered for multi-factor authentication.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect MFA registration report data.

        Returns:
            Dict containing:
            - registration_details: User MFA registration details
            - total_users: Total number of users
            - mfa_registered_count: Number of users registered for MFA
            - mfa_capable_count: Number of users capable of MFA
        """
        # Get user registration details for MFA
        registration_details = await client.get_all_pages(
            "/reports/authenticationMethods/userRegistrationDetails",
            beta=True,
        )

        # Count users by MFA status
        mfa_registered_count = 0
        mfa_capable_count = 0

        for user in registration_details:
            # isMfaRegistered indicates user has registered for MFA
            if user.get("isMfaRegistered"):
                mfa_registered_count += 1
            # isMfaCapable indicates user can use MFA
            if user.get("isMfaCapable"):
                mfa_capable_count += 1

        total_users = len(registration_details)

        return {
            "registration_details": registration_details,
            "total_users": total_users,
            "mfa_registered_count": mfa_registered_count,
            "mfa_capable_count": mfa_capable_count,
            "mfa_not_registered_count": total_users - mfa_registered_count,
            "mfa_registration_percentage": (
                round(mfa_registered_count / total_users * 100, 2)
                if total_users > 0
                else 0
            ),
        }
