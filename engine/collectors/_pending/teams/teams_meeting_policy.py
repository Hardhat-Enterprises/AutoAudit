"""Teams meeting policy collector.

STATUS: PENDING - MicrosoftTeams module AccessTokens auth not working
REASON: Connect-MicrosoftTeams with -AccessTokens parameter returns
        "Not supported tenant type" error. This is a known bug in the
        MicrosoftTeams PowerShell module affecting certain tenant configurations.
        See: https://techcommunity.microsoft.com/discussions/teamsdeveloper/authenticating-with-an-access-token-connect-microsoftteams/2233794
TO ENABLE: Either wait for Microsoft to fix the module, or implement
           certificate-based auth. Then move this collector back to
           collectors/teams/ and register it.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 8.5.1, 8.5.2, 8.5.3, 8.5.4, 8.5.5, 8.5.6, 8.5.7, 8.5.8, 8.5.9

Connection Method: Microsoft Teams PowerShell (via Docker container)
Authentication: AccessTokens auth currently broken - certificate auth may work
Required Cmdlets: Get-CsTeamsMeetingPolicy
Required Permissions: Teams.ManageAsApp + Teams Admin role
"""

from typing import Any

from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient


class TeamsMeetingPolicyDataCollector(BasePowerShellCollector):
    """Collects Teams meeting policies for CIS compliance evaluation.

    This collector retrieves meeting settings including lobby, anonymous
    users, recording, and presenter controls.
    """

    async def collect(self, client: PowerShellClient) -> dict[str, Any]:
        """Collect Teams meeting policy data.

        Returns:
            Dict containing:
            - meeting_policies: List of meeting policies
            - global_policy: The global meeting policy
        """
        policies = await client.run_cmdlet("Teams", "Get-CsTeamsMeetingPolicy")

        # Handle single policy vs list
        if isinstance(policies, dict):
            policies = [policies]

        # Find global policy
        global_policy = next(
            (p for p in policies if p.get("Identity") == "Global"),
            None
        )

        return {
            "meeting_policies": policies,
            "total_policies": len(policies),
            "global_policy": global_policy,
            # Key settings for CIS controls
            "allow_anonymous_users_to_join": global_policy.get("AllowAnonymousUsersToJoinMeeting") if global_policy else None,
            "allow_anonymous_users_to_start": global_policy.get("AllowAnonymousUsersToStartMeeting") if global_policy else None,
            "auto_admitted_users": global_policy.get("AutoAdmittedUsers") if global_policy else None,
            "allow_pstn_users_to_bypass_lobby": global_policy.get("AllowPSTNUsersToBypassLobby") if global_policy else None,
            "meeting_chat_enabled_type": global_policy.get("MeetingChatEnabledType") if global_policy else None,
            "designated_presenter_role_mode": global_policy.get("DesignatedPresenterRoleMode") if global_policy else None,
            "allow_cloud_recording": global_policy.get("AllowCloudRecording") if global_policy else None,
            "allow_external_participant_give_request_control": global_policy.get("AllowExternalParticipantGiveRequestControl") if global_policy else None,
        }
