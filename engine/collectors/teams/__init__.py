"""Microsoft Teams collectors.

These collectors use Microsoft Teams PowerShell via the MicrosoftTeams module.
Authentication uses client secret via MSAL to obtain access tokens,
which are passed to PowerShell cmdlets via the -AccessTokens parameter.
"""
