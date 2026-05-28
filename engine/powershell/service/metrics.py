"""Prometheus metrics for the PowerShell service.

These metrics drive HPA scaling decisions and the Grafana scaling dashboard.
The gauge `pwsh_active_subprocesses` is the right signal for HPA's
custom-metrics path once a Prometheus Adapter is wired (a runspace pool would
make CPU a poor proxy because the pool would absorb concurrency without
bumping CPU); for now CPU is the simpler scaler and this gauge sits ready.
"""

from prometheus_client import Counter, Gauge, Histogram

# Active subprocesses currently running. Incremented at the start of each
# execute_cmdlet call and decremented in `finally`. Used for capacity-based
# scaling once HPA-on-custom-metrics is wired.
pwsh_active_subprocesses = Gauge(
    "pwsh_active_subprocesses",
    "Number of pwsh subprocesses currently executing in this pod.",
)

# Total invocations counter — broken down by module + outcome.
pwsh_executions_total = Counter(
    "pwsh_executions_total",
    "Total number of pwsh executions handled by this pod.",
    ["module", "outcome"],
)

# Execution duration histogram. Default buckets are tuned for cmdlet calls
# which dominate at 5–60 seconds (module-import + connect + cmdlet).
pwsh_execution_duration_seconds = Histogram(
    "pwsh_execution_duration_seconds",
    "Wall-time of pwsh subprocess execution (seconds).",
    ["module"],
    buckets=(0.5, 1.0, 2.5, 5.0, 10.0, 20.0, 30.0, 60.0, 90.0, 120.0),
)
