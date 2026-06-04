FROM mcr.microsoft.com/powershell:7.5-mariner-2.0

# Install PowerShell modules for M365 management
RUN pwsh -NoProfile -Command " \
    Set-PSRepository PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force; \
    Install-Module -Name MicrosoftTeams -Scope AllUsers -Force \
"

# Create non-root user for security
RUN tdnf install -y shadow-utils && tdnf clean all \
    && useradd --uid 1000 --create-home appuser

USER appuser

# Set entrypoint to PowerShell
ENTRYPOINT ["pwsh", "-NoProfile", "-NonInteractive", "-Command"]
