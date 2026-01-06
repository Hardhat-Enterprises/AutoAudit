# Manual Collector Testing

You can run collectors directly against a live M365 tenant to see what data they return. This is useful when developing OPA/Rego policies, since you'll need to know the exact JSON structure to write your policy rules against.

## Before you start

Make sure you've run `uv sync` from the `engine` directory to install dependencies.

You'll also need access to an M365 test tenant with an app registration that has the appropriate Graph API permissions.

## Set your environment variables

The test script authenticates using three environment variables.

On Windows (PowerShell):
```powershell
$env:M365_TENANT_ID="your-tenant-id"
$env:M365_CLIENT_ID="your-client-id"
$env:M365_CLIENT_SECRET="your-client-secret"
```

On macOS or Linux:
```bash
export M365_TENANT_ID="your-tenant-id"
export M365_CLIENT_ID="your-client-id"
export M365_CLIENT_SECRET="your-client-secret"
```

## Run a collector

From the `engine` directory, run:

```bash
uv run python -m scripts.test_collector -c entra.roles.cloud_only_admins
```

The JSON response will be printed to the console.

To see what collectors are available, run:

```bash
uv run python -m scripts.test_collector --list
```

If you want to save the output to a file instead, add the `-o` flag with a directory:

```bash
uv run python -m scripts.test_collector -c entra.roles.cloud_only_admins -o ./samples/
```
