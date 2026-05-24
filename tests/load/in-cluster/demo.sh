#!/usr/bin/env bash
# End-to-end scaling demo orchestrator.
#
# Fires the two k6 scripts back-to-back so the dashboard shows:
#   1. backend-api scaling (HPA on CPU)        — api-baseline.js
#   2. wait WAIT_BETWEEN_SECS for backend-api HPA to scale back to min
#   3. worker / KEDA / powershell-service / OPA scaling — scan-fanout.js
#
# Usage:
#   bash tests/load/in-cluster/demo.sh
#
#   # tune per-pulse sizes for the worker phase if you want bigger curves
#   N_GRAPH=80 N_POWERSHELL=30 bash tests/load/in-cluster/demo.sh
#
# Env knobs (with defaults):
#   WAIT_BETWEEN_SECS  - pause between the two phases (default 60, matches
#                        the HPA scaleDown stabilizationWindow so backend-api
#                        returns to min before the second phase starts)
#   N_GRAPH            - synthetic tasks per pulse on controls.graph (default 80)
#   N_POWERSHELL       - synthetic tasks per pulse on controls.powershell (default 20)

set -euo pipefail

WAIT_BETWEEN_SECS="${WAIT_BETWEEN_SECS:-60}"
N_GRAPH="${N_GRAPH:-150}"
N_POWERSHELL="${N_POWERSHELL:-50}"

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
RUN="${REPO_ROOT}/tests/load/in-cluster/run.sh"

echo "============================================================"
echo "Phase 1/2 — backend-api HPA scaling (api-baseline.js, 5 min)"
echo "============================================================"
bash "$RUN" api-baseline.js

echo
echo "============================================================"
echo "Cooling down ${WAIT_BETWEEN_SECS}s so backend-api HPA returns to min"
echo "============================================================"
sleep "$WAIT_BETWEEN_SECS"

echo
echo "============================================================"
echo "Phase 2/2 — worker / KEDA / powershell-service / OPA scaling"
echo "  scan-fanout.js  N_GRAPH=${N_GRAPH}  N_POWERSHELL=${N_POWERSHELL}"
echo "============================================================"
bash "$RUN" scan-fanout.js -e "N_GRAPH=${N_GRAPH}" -e "N_POWERSHELL=${N_POWERSHELL}"

echo
echo "Demo complete. Check Grafana for the full picture."
