"""Security & Compliance collectors.

These collectors use the Security & Compliance PowerShell via IPPSSession.
Authentication uses client secret via MSAL to obtain access tokens,
which are passed to PowerShell cmdlets via the -AccessToken parameter.
"""
