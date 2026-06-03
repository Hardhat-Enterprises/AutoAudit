ARG TARGETPLATFORM
FROM --platform=$TARGETPLATFORM mcr.microsoft.com/powershell:7.5-mariner-2.0

# Install Python, curl (for healthcheck), tar (for uv installer), and awk (uv install script uses it)
RUN tdnf install -y python3 curl tar gawk && tdnf clean all

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Install PowerShell modules
RUN pwsh -NoProfile -Command " \
    Set-PSRepository PSGallery -InstallationPolicy Trusted; \
    Install-Module -Name ExchangeOnlineManagement -Scope AllUsers -Force; \
    Install-Module -Name MicrosoftTeams -Scope AllUsers -Force \
    "

# Create non-root user early, before any COPYs
RUN tdnf install -y shadow-utils && tdnf clean all \
    && useradd --uid 1000 --create-home appuser

# Copy service code and install Python dependencies
COPY --chown=appuser:appuser service/ /app/
WORKDIR /app
RUN uv pip install --system -r pyproject.toml \
    && chown -R appuser:appuser /app

# Expose port
EXPOSE 8001

USER appuser

# Run FastAPI service
CMD ["python3", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
