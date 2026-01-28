FROM mcr.microsoft.com/powershell:7.5-mariner-2.0

# Install Python, curl (for healthcheck), and tar (for uv installer)
RUN tdnf install -y python3 curl tar && tdnf clean all

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install PowerShell modules
RUN pwsh -NoProfile -Command " \
    Set-PSRepository PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force; \
    Install-Module -Name MicrosoftTeams -Scope AllUsers -Force \
"

# Copy service code and install Python dependencies
COPY service/ /app/
WORKDIR /app
RUN uv pip install --system -r pyproject.toml

# Expose port
EXPOSE 8001

# Run FastAPI service
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
