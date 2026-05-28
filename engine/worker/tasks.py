"""Celery tasks for compliance scanning."""

import asyncio
import json
import os
import time
from datetime import datetime
from decimal import Decimal
from pathlib import Path

import httpx

from worker.celery_app import (
    QUEUE_CONTROLS_GRAPH,
    QUEUE_CONTROLS_POWERSHELL,
    QUEUE_DEFAULT,
    celery_app,
)
from worker.config import settings
from worker.db import (
    get_db_session,
    get_scan,
    get_pending_scan_results,
    update_scan_status,
    increment_scan_progress,
    increment_scan_error_count,
    increment_scan_skipped_count,
    update_scan_result,
    finalize_scan_if_complete,
)


def load_metadata(framework: str, benchmark: str, version: str) -> dict:
    """Load control metadata from the policies directory.

    Args:
        framework: Framework name (e.g., "cis")
        benchmark: Benchmark slug (e.g., "microsoft-365-foundations")
        version: Version (e.g., "v3.1.0")

    Returns:
        The metadata dict containing controls list.
    """
    metadata_path = Path(settings.POLICIES_DIR) / framework / benchmark / version / "metadata.json"
    if not metadata_path.exists():
        raise FileNotFoundError(f"Metadata not found: {metadata_path}")

    with open(metadata_path) as f:
        return json.load(f)


def get_control_metadata(metadata: dict, control_id: str) -> dict | None:
    """Get control metadata by control_id from the metadata dict."""
    for control in metadata.get("controls", []):
        if control["control_id"] == control_id:
            return control
    return None


# Same prefix split used in _evaluate_control_async to choose the M365 client.
# Tasks routed to controls.powershell run on workers with --pool=prefork and a
# small concurrency, since the powershell-service is the bottleneck. Graph
# tasks run on workers with --pool=gevent and high concurrency since they're
# IO-bound HTTP calls.
_POWERSHELL_PREFIXES = ("exchange.", "compliance.", "teams.")
_POWERSHELL_PREFIX_EXCEPTIONS = ("exchange.dns.",)


def queue_for_collector(collector_id: str | None) -> str:
    """Return the Celery queue name for a control's collector.

    Graph collectors are IO-bound and parallel-friendly; PowerShell collectors
    are bounded by the powershell-service and should not flood it.
    """
    if not collector_id:
        return QUEUE_DEFAULT
    if collector_id.startswith(_POWERSHELL_PREFIX_EXCEPTIONS):
        return QUEUE_CONTROLS_GRAPH
    if collector_id.startswith(_POWERSHELL_PREFIXES):
        return QUEUE_CONTROLS_POWERSHELL
    return QUEUE_CONTROLS_GRAPH


@celery_app.task(name="worker.tasks.run_scan", queue=QUEUE_DEFAULT)
def run_scan(scan_id: int) -> dict:
    """Orchestrator task: Dispatches control evaluation tasks.

    This task:
    1. Updates scan status to "running"
    2. Gets pending ScanResult records
    3. Dispatches evaluate_control tasks for each pending result
    4. Returns immediately (fire-and-forget)

    Each evaluate_control task writes results directly to PostgreSQL.
    The last task to complete will finalize the scan.

    Args:
        scan_id: The scan ID to process

    Returns:
        Summary dict with dispatch info
    """
    with get_db_session() as session:
        # Get scan details
        scan = get_scan(session, scan_id)
        if not scan:
            raise ValueError(f"Scan {scan_id} not found")

        # Update status to running
        update_scan_status(session, scan_id, status="running")
        session.commit()

        # Get pending scan results (controls that need to be evaluated)
        pending_results = get_pending_scan_results(session, scan_id)

    total_pending = len(pending_results)

    if total_pending == 0:
        # No controls to evaluate - scan was created with all controls skipped
        with get_db_session() as session:
            update_scan_status(
                session,
                scan_id,
                status="completed",
                finished_at=datetime.utcnow(),
                compliance_score=Decimal("100.00"),
            )
            session.commit()
        return {"scan_id": scan_id, "status": "completed", "total_pending": 0}

    # Load metadata to get control details
    metadata = load_metadata(scan["framework"], scan["benchmark"], scan["version"])

    # Build credentials dict for passing to tasks
    credentials = {
        "tenant_id": scan["tenant_id"],
        "client_id": scan["client_id"],
        "client_secret": scan["client_secret"],
    }

    # Dispatch all tasks for parallel execution (fire-and-forget)
    dispatched = 0
    skipped = 0

    for result in pending_results:
        control = get_control_metadata(metadata, result["control_id"])
        if not control:
            # Control not found in metadata (possible ID format mismatch)
            with get_db_session() as session:
                update_scan_result(
                    session,
                    result_id=result["id"],
                    status="error",
                    message=f"Control {result['control_id']} not found in metadata",
                )
                increment_scan_error_count(session, scan_id)
                session.commit()
            continue

        # Check automation_status before dispatching
        status = control.get("automation_status", "ready")
        collector_id = control.get("data_collector_id") or ""

        if status == "ready":
            # Optional fast-scan mode: allow skipping slow PowerShell-based controls only when
            # explicitly disabled via ENABLE_POWERSHELL_CONTROLS=false.
            if (
                settings.ENABLE_POWERSHELL_CONTROLS is False
                and collector_id.startswith(("exchange.", "compliance.", "teams."))
                and not collector_id.startswith("exchange.dns.")
            ):
                with get_db_session() as session:
                    update_scan_result(
                        session,
                        result_id=result["id"],
                        status="skipped",
                        message="Skipped (fast scan): PowerShell-based controls disabled (ENABLE_POWERSHELL_CONTROLS=false).",
                    )
                    increment_scan_skipped_count(session, scan_id)
                    session.commit()
                skipped += 1
                continue

            # Verify collector exists before dispatching
            if not control.get("data_collector_id"):
                with get_db_session() as session:
                    update_scan_result(
                        session,
                        result_id=result["id"],
                        status="error",
                        message="Control marked ready but has no data_collector_id",
                    )
                    increment_scan_error_count(session, scan_id)
                    session.commit()
                continue

            evaluate_control.apply_async(
                kwargs={
                    "scan_id": scan_id,
                    "result_id": result["id"],
                    "control": control,
                    "credentials": credentials,
                    "framework": scan["framework"],
                    "benchmark": scan["benchmark"],
                    "version": scan["version"],
                },
                queue=queue_for_collector(collector_id),
            )
            dispatched += 1
        else:
            # Skip non-ready controls (deferred, blocked, manual, not_started)
            with get_db_session() as session:
                update_scan_result(
                    session,
                    result_id=result["id"],
                    status="skipped",
                    message=f"Control {status}: {control.get('notes') or 'Not yet automatable'}",
                )
                increment_scan_skipped_count(session, scan_id)
                session.commit()
            skipped += 1

    # If no tasks were dispatched, finalize the scan immediately
    # (all controls were skipped due to automation_status)
    if dispatched == 0:
        with get_db_session() as session:
            finalize_scan_if_complete(session, scan_id)
            session.commit()
        return {
            "scan_id": scan_id,
            "status": "completed",
            "dispatched": dispatched,
            "skipped": skipped,
        }

    # Return immediately - don't wait for results
    # Each evaluate_control task will update PostgreSQL directly
    # The last task to complete will finalize the scan
    return {
        "scan_id": scan_id,
        "status": "running",
        "dispatched": dispatched,
        "skipped": skipped,
    }


@celery_app.task(
    name="worker.tasks.evaluate_control",
    bind=True,
    max_retries=3,
    default_retry_delay=60,
    # Default queue used only if a caller forgets to pass queue= to apply_async;
    # run_scan always routes via queue_for_collector(), so this is a safety net.
    queue=QUEUE_CONTROLS_GRAPH,
)
def evaluate_control(
    self,
    scan_id: int,
    result_id: int,
    control: dict,
    credentials: dict,
    framework: str,
    benchmark: str,
    version: str,
) -> dict:
    """Evaluate a single control.

    This task:
    1. Collects data using the appropriate collector
    2. Evaluates the policy using OPA
    3. Updates the ScanResult record with the outcome
    4. Updates scan progress counters
    5. If this was the last pending control, finalizes the scan

    Args:
        scan_id: The scan ID
        result_id: The scan_result.id to update
        control: Control metadata dict from metadata.json
        credentials: M365 credentials dict
        framework: Framework name (e.g., "cis")
        benchmark: Benchmark slug (e.g., "microsoft-365-foundations")
        version: Version string (e.g., "v3.1.0")

    Returns:
        Result dict with control evaluation outcome
    """
    control_id = control["control_id"]
    collector_id = control.get("data_collector_id")
    policy_file = control.get("policy_file")

    try:
        # Run async collector and OPA evaluation
        result = asyncio.run(
            _evaluate_control_async(
                control_id=control_id,
                collector_id=collector_id,
                policy_file=policy_file,
                credentials=credentials,
                framework=framework,
                benchmark=benchmark,
                version=version,
            )
        )

        # Update database based on result
        with get_db_session() as session:
            if result.get("compliant", False):
                # Control passed
                update_scan_result(
                    session,
                    result_id=result_id,
                    status="passed",
                    message=result.get("message", "Control is compliant"),
                    evidence=result.get("details"),
                )
                increment_scan_progress(session, scan_id, passed=True)
            else:
                # Control failed
                update_scan_result(
                    session,
                    result_id=result_id,
                    status="failed",
                    message=result.get("message", "Control is non-compliant"),
                    evidence=result.get("details"),
                )
                increment_scan_progress(session, scan_id, passed=False)

            # Check if this was the last control and finalize scan if complete
            finalize_scan_if_complete(session, scan_id)
            session.commit()

        return {
            "control_id": control_id,
            "compliant": result.get("compliant", False),
            "message": result.get("message"),
        }

    except Exception as exc:
        # Retry on failure
        try:
            raise self.retry(exc=exc)
        except self.MaxRetriesExceededError:
            # Max retries exceeded - mark as error
            with get_db_session() as session:
                update_scan_result(
                    session,
                    result_id=result_id,
                    status="error",
                    message=f"Control evaluation failed after retries: {str(exc)}",
                )
                increment_scan_error_count(session, scan_id)

                # Check if this was the last control and finalize scan if complete
                finalize_scan_if_complete(session, scan_id)
                session.commit()
            return {
                "control_id": control_id,
                "compliant": None,
                "error": str(exc),
            }


async def _evaluate_control_async(
    control_id: str,
    collector_id: str,
    policy_file: str,
    credentials: dict,
    framework: str,
    benchmark: str,
    version: str,
) -> dict:
    """Async helper to collect data and evaluate policy.

    Args:
        control_id: The control ID (e.g., "CIS-1.1.1")
        collector_id: The data collector ID from registry
        policy_file: The Rego policy filename (e.g., "1.1.1_admin_cloud_only.rego")
        credentials: M365 credentials
        framework: Framework name (e.g., "cis")
        benchmark: Benchmark slug (e.g., "microsoft-365-foundations")
        version: Version string (e.g., "v3.1.0")

    Returns:
        OPA evaluation result
    """
    # Import here to avoid circular imports
    from collectors.registry import get_collector
    from collectors.graph_client import GraphClient
    from collectors.powershell_client import PowerShellClient
    from opa_client import opa_client

    # Get collector
    collector = get_collector(collector_id)

    # Determine client type based on collector_id prefix.
    #
    # Most Exchange and Compliance collectors require PowerShell, but a few Exchange
    # collectors use Graph (e.g. domain metadata).
    if collector_id.startswith(("exchange.", "compliance.")) and not collector_id.startswith(
        "exchange.dns."
    ):
        client = PowerShellClient(
            tenant_id=credentials["tenant_id"],
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            service_url=settings.POWERSHELL_SERVICE_URL,
        )
    else:
        # Entra and other collectors use Graph API
        client = GraphClient(
            tenant_id=credentials["tenant_id"],
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
        )

    # Collect data using the appropriate client
    collected_data = await collector.collect(client)

    # Build OPA package path to match the Rego package declaration
    # Rego package: "cis.microsoft_365_foundations.v3_1_0.control_1_1_1"
    # OPA REST API path: "cis/microsoft_365_foundations/v3_1_0/control_1_1_1"
    #
    # Transform:
    # - framework: "essential-eight" -> "essential_eight"
    # - benchmark: "microsoft-365-foundations" -> "microsoft_365_foundations"
    # - version: "v3.1.0" -> "v3_1_0"
    # - control_id: "1.1.1" -> "control_1_1_1", "E8-MAC-2.1" -> "control_e8_mac_2_1"
    framework_normalized = framework.replace("-", "_")
    benchmark_normalized = benchmark.replace("-", "_")
    version_normalized = version.replace(".", "_")

    # Convert control_id to a valid Rego identifier (lowercase, hyphens/dots to underscores)
    control_suffix = control_id.replace(".", "_").replace("-", "_").lower()
    control_package = f"control_{control_suffix}"

    package_path = f"{framework_normalized}/{benchmark_normalized}/{version_normalized}/{control_package}"

    # Evaluate policy with OPA
    result = await opa_client.evaluate_policy(package_path, collected_data)

    return result


# --- Synthetic load lever ---------------------------------------------------
#
# Drives the worker / powershell-service scaling demos without needing real
# M365 credentials. Gated by SYNTHETIC_ENABLED env var; the chart only sets
# this when synthetic.enabled=true. The task does NOT touch the database, so
# enqueueing a million of them is cheap.


def _synthetic_enabled() -> bool:
    return os.environ.get("SYNTHETIC_ENABLED", "").lower() in {"1", "true", "yes"}


@celery_app.task(name="worker.tasks.synthetic_evaluate")
def synthetic_evaluate(
    sleep_ms: int = 1000,
    cpu_burn_ms: int = 0,
    call_powershell_service: bool = False,
    call_opa: bool = True,
) -> dict:
    """No-op evaluator that simulates a real control evaluation's wall time
    and downstream hops.

    Used by the synthetic-scan endpoint to drive worker / powershell-service
    / OPA scaling without needing real M365 credentials. Mirrors what a real
    `evaluate_control` task does at the I/O level: optional collector-side
    hop (powershell-service) and an OPA decision call.

    `call_opa=True` issues a POST to OPA's `/v1/data/<package>/result` with
    a stub input so OPA's HTTP histogram + decision logs see real traffic.
    The package path defaults to a known-existing CIS M365 control; override
    with the `SYNTHETIC_OPA_PACKAGE_PATH` env var if a different one is
    baked into the OPA image.
    """
    if not _synthetic_enabled():
        return {"skipped": True, "reason": "SYNTHETIC_ENABLED not set"}

    if cpu_burn_ms > 0:
        deadline = time.monotonic() + cpu_burn_ms / 1000.0
        while time.monotonic() < deadline:
            pass  # busy loop — drives CPU-based HPA on the worker pod

    if call_powershell_service:
        url = settings.POWERSHELL_SERVICE_URL
        if url:
            try:
                with httpx.Client(timeout=30.0) as client:
                    client.post(
                        f"{url.rstrip('/')}/execute/synthetic",
                        json={"sleep_ms": sleep_ms, "cpu_burn_ms": cpu_burn_ms},
                    )
            except Exception:
                # The point is to drive load — failures here are expected
                # under demo load and shouldn't fail the task.
                pass
    else:
        time.sleep(sleep_ms / 1000.0)

    called_opa = False
    if call_opa:
        opa_url = settings.OPA_URL
        package_path = os.environ.get(
            "SYNTHETIC_OPA_PACKAGE_PATH",
            "cis/microsoft_365_foundations/v6_0_0/control_1_1_1",
        )
        if opa_url:
            try:
                with httpx.Client(timeout=10.0) as client:
                    client.post(
                        f"{opa_url.rstrip('/')}/v1/data/{package_path}/result",
                        json={"input": {}},
                    )
                called_opa = True
            except Exception:
                # Same rationale — load generation, swallow failures.
                pass

    return {
        "ok": True,
        "sleep_ms": sleep_ms,
        "cpu_burn_ms": cpu_burn_ms,
        "called_powershell": call_powershell_service,
        "called_opa": called_opa,
    }
