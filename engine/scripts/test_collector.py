"""Standalone collector test script for live M365 tenant testing.

This script bypasses the worker/OPA flow to test collectors directly
and document actual API response payloads.

Usage:
    cd engine
    python -m scripts.test_collector --list
    python -m scripts.test_collector -c entra.roles.cloud_only_admins
    python -m scripts.test_collector -c entra.conditional_access.policies -o ./samples/

Environment Variables:
    M365_TENANT_ID: Azure AD tenant ID
    M365_CLIENT_ID: App registration client ID
    M365_CLIENT_SECRET: App registration client secret
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports when running as module
sys.path.insert(0, str(Path(__file__).parent.parent))

from collectors.registry import DATA_COLLECTORS, get_collector
from collectors.graph_client import GraphClient
from collectors.powershell_base import BasePowerShellCollector
from collectors.powershell_client import PowerShellClient, PowerShellExecutionError
from collectors.sharepoint_client import SharePointClient


def list_collectors() -> None:
    """Print all registered collectors."""
    print("Available collectors:")
    print("-" * 50)
    for collector_id in sorted(DATA_COLLECTORS.keys()):
        collector_class = DATA_COLLECTORS[collector_id]
        doc = collector_class.__doc__ or "No description"
        # Get first line of docstring
        doc_line = doc.strip().split("\n")[0]
        print(f"  {collector_id}")
        print(f"    {doc_line}")
        print()


def get_credentials() -> tuple[str, str, str]:
    """Get M365 credentials from environment variables."""
    tenant_id = os.environ.get("M365_TENANT_ID")
    client_id = os.environ.get("M365_CLIENT_ID")
    client_secret = os.environ.get("M365_CLIENT_SECRET")

    missing = []
    if not tenant_id:
        missing.append("M365_TENANT_ID")
    if not client_id:
        missing.append("M365_CLIENT_ID")
    if not client_secret:
        missing.append("M365_CLIENT_SECRET")

    if missing:
        print("Error: Missing required environment variables:")
        for var in missing:
            print(f"  - {var}")
        print("\nSet these variables before running the script:")
        print("  export M365_TENANT_ID=<your-tenant-id>")
        print("  export M365_CLIENT_ID=<your-client-id>")
        print("  export M365_CLIENT_SECRET=<your-client-secret>")
        sys.exit(1)

    return tenant_id, client_id, client_secret


def get_sharepoint_client(tenant_id: str, client_id: str, client_secret: str) -> SharePointClient:
    """Build a SharePoint client, requiring tenant name for the admin URL."""
    tenant_name = os.environ.get("SHAREPOINT_TENANT_NAME")
    if not tenant_name:
        print("Error: Missing required environment variable for SharePoint:")
        print("  - SHAREPOINT_TENANT_NAME (e.g., 'contoso' for contoso-admin.sharepoint.com)")
        sys.exit(1)
    return SharePointClient(tenant_id, client_id, client_secret, tenant_name)


async def test_collector(
    collector_id: str,
    output_dir: Path | None = None,
    verbose: bool = False,
    service_url: str | None = None,
) -> dict:
    """Run a collector and return/save results.

    Args:
        collector_id: The collector ID to run (e.g., 'entra.roles.cloud_only_admins')
        output_dir: Optional directory to save JSON output
        verbose: If True, print additional debug info
        service_url: Optional PowerShell HTTP service URL

    Returns:
        Dict containing collector_id, timestamp, elapsed_seconds, and data
    """
    # Validate collector exists
    if collector_id not in DATA_COLLECTORS:
        print(f"Error: Unknown collector '{collector_id}'")
        print("\nAvailable collectors:")
        for cid in sorted(DATA_COLLECTORS.keys()):
            print(f"  {cid}")
        sys.exit(1)

    # Get credentials
    tenant_id, client_id, client_secret = get_credentials()

    if verbose:
        print(f"Tenant ID: {tenant_id}")
        print(f"Client ID: {client_id}")
        if service_url:
            print(f"Using PowerShell service: {service_url}")
        print()

    # Create collector and appropriate client
    collector = get_collector(collector_id)
    client = None
    graph_client = None
    ps_client = None

    if isinstance(collector, BasePowerShellCollector):
        client = PowerShellClient(tenant_id, client_id, client_secret, service_url=service_url)
    elif collector_id.startswith("sharepoint."):
        client = get_sharepoint_client(tenant_id, client_id, client_secret)
    elif collector_id == "exchange.protection.priority_accounts":
        graph_client = GraphClient(tenant_id, client_id, client_secret)
        ps_client = PowerShellClient(tenant_id, client_id, client_secret, service_url=service_url)
        client = graph_client
    else:
        client = GraphClient(tenant_id, client_id, client_secret)

    # Run collection
    print(f"Running collector: {collector_id}")
    print(f"Collector class: {collector.__class__.__name__}")
    print("-" * 50)

    start = datetime.now()
    try:
        try:
            result = await collector.collect(client)
        except Exception as e:
            # Priority accounts: fall back to PowerShell if Graph path fails
            if collector_id == "exchange.protection.priority_accounts" and ps_client:
                result = await collector.collect(ps_client)
            else:
                raise e

        elapsed = (datetime.now() - start).total_seconds()
        print(f"Collection completed in {elapsed:.2f}s")
    except NotImplementedError:
        print("Error: This collector is not yet implemented (stub only)")
        sys.exit(1)
    except PowerShellExecutionError as e:
        print(f"PowerShell Error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error during collection: {type(e).__name__}: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

    # Build output structure
    output = {
        "collector_id": collector_id,
        "timestamp": datetime.now().isoformat(),
        "elapsed_seconds": round(elapsed, 3),
        "data": result,
    }

    # Pretty print to console
    print("-" * 50)
    print("Result:")
    print(json.dumps(output, indent=2, default=str))

    # Save to file if output_dir specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{collector_id.replace('.', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        with open(filepath, "w") as f:
            json.dump(output, f, indent=2, default=str)
        print()
        print(f"Saved to: {filepath}")

    return output


async def test_all_collectors(
    output_dir: Path | None = None,
    service_url: str | None = None,
) -> None:
    """Test all registered collectors and report status."""
    print("Testing all registered collectors...")
    if service_url:
        print(f"Using PowerShell service: {service_url}")
    print("=" * 60)

    tenant_id, client_id, client_secret = get_credentials()
    graph_client = GraphClient(tenant_id, client_id, client_secret)
    ps_client = None  # Lazy init PowerShell client
    priority_ps_client = None

    results = []
    for collector_id in sorted(DATA_COLLECTORS.keys()):
        print(f"\n{collector_id}:")
        collector = get_collector(collector_id)

        # Use appropriate client based on collector type
        if isinstance(collector, BasePowerShellCollector):
            if ps_client is None:
                ps_client = PowerShellClient(tenant_id, client_id, client_secret, service_url=service_url)
            client = ps_client
        elif collector_id.startswith("sharepoint."):
            client = get_sharepoint_client(tenant_id, client_id, client_secret)
        elif collector_id == "exchange.protection.priority_accounts":
            # Try Graph first; if it fails, fall back to PowerShell
            client = graph_client
            if priority_ps_client is None:
                priority_ps_client = PowerShellClient(tenant_id, client_id, client_secret, service_url=service_url)
        else:
            client = graph_client

        start = datetime.now()
        try:
            try:
                result = await collector.collect(client)
            except Exception:
                if collector_id == "exchange.protection.priority_accounts" and priority_ps_client:
                    result = await collector.collect(priority_ps_client)
                else:
                    raise

            elapsed = (datetime.now() - start).total_seconds()
            status = "OK"
            error = None
            print(f"  Status: OK ({elapsed:.2f}s)")
        except NotImplementedError:
            status = "NOT_IMPLEMENTED"
            error = "Stub only"
            elapsed = 0
            print(f"  Status: NOT_IMPLEMENTED (stub)")
        except PowerShellExecutionError as e:
            status = "POWERSHELL_ERROR"
            error = str(e)
            elapsed = 0
            print(f"  Status: POWERSHELL_ERROR - {e}")
        except Exception as e:
            status = "ERROR"
            error = str(e)
            elapsed = 0
            print(f"  Status: ERROR - {e}")

        results.append({
            "collector_id": collector_id,
            "status": status,
            "elapsed_seconds": round(elapsed, 3) if elapsed else None,
            "error": error,
        })

    # Print summary
    print("\n" + "=" * 60)
    print("Summary:")
    ok_count = sum(1 for r in results if r["status"] == "OK")
    stub_count = sum(1 for r in results if r["status"] == "NOT_IMPLEMENTED")
    ps_error_count = sum(1 for r in results if r["status"] == "POWERSHELL_ERROR")
    error_count = sum(1 for r in results if r["status"] == "ERROR")
    print(f"  OK: {ok_count}")
    print(f"  Not Implemented: {stub_count}")
    print(f"  PowerShell Errors: {ps_error_count}")
    print(f"  Other Errors: {error_count}")

    # Save summary if output_dir specified
    if output_dir:
        output_dir.mkdir(parents=True, exist_ok=True)
        filepath = output_dir / f"test_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filepath, "w") as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "ok": ok_count,
                    "not_implemented": stub_count,
                    "powershell_errors": ps_error_count,
                    "errors": error_count,
                },
                "results": results,
            }, f, indent=2)
        print(f"\nSummary saved to: {filepath}")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Test M365 collectors against live tenant",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m scripts.test_collector --list
  python -m scripts.test_collector -c entra.roles.cloud_only_admins
  python -m scripts.test_collector -c entra.roles.cloud_only_admins -o ./samples/
  python -m scripts.test_collector --all -o ./samples/

  # Use PowerShell HTTP service instead of local Docker
  python -m scripts.test_collector -c exchange.organization.organization_config --use-service http://localhost:8001

Environment Variables:
  M365_TENANT_ID      Azure AD tenant ID
  M365_CLIENT_ID      App registration client ID
  M365_CLIENT_SECRET  App registration client secret
        """,
    )
    parser.add_argument(
        "--collector", "-c",
        help="Collector ID to run (e.g., 'entra.roles.cloud_only_admins')",
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output directory for JSON files",
    )
    parser.add_argument(
        "--list", "-l",
        action="store_true",
        help="List available collectors",
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Test all collectors and report status",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output including credentials (masked) and stack traces",
    )
    parser.add_argument(
        "--use-service",
        type=str,
        default=None,
        metavar="URL",
        help="Use PowerShell HTTP service instead of Docker (e.g., http://localhost:8001)",
    )

    args = parser.parse_args()

    if args.list:
        list_collectors()
        return

    if args.all:
        asyncio.run(test_all_collectors(args.output, args.use_service))
        return

    if not args.collector:
        parser.error("--collector is required (or use --list to see available collectors)")

    asyncio.run(test_collector(args.collector, args.output, args.verbose, args.use_service))


if __name__ == "__main__":
    main()
