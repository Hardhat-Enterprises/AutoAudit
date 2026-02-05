"""Exchange Online collectors.

These collectors use Exchange Online PowerShell via the ExchangeOnlineManagement module.
Authentication uses client secret via MSAL to obtain access tokens,
which are passed to PowerShell cmdlets via the -AccessToken parameter.
"""
