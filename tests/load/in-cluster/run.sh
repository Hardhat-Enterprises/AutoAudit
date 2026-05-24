#!/usr/bin/env bash
# Run a k6 script against the in-cluster Service.
#
# Usage:
#   bash tests/load/in-cluster/run.sh <script.js> [extra k6 args...]
#
# Examples:
#   bash tests/load/in-cluster/run.sh api-baseline.js
#   bash tests/load/in-cluster/run.sh scan-fanout.js -e N_GRAPH=20 -e N_POWERSHELL=10
#
# What it does:
#   1. Re-applies the k6-scripts ConfigMap from tests/load/*.js (always
#      in sync with the canonical scripts on disk).
#   2. Renders tests/load/in-cluster/k6-job.yaml with the chosen script and
#      kubectl-creates it (generateName, so re-runs do not collide).
#   3. Follows the resulting Job's pod logs until it finishes.

set -euo pipefail

SCRIPT="${1:?usage: run.sh <script.js> [extra k6 args...]}"
shift
EXTRA_ARGS="$*"

NAMESPACE="autoaudit"
BASE_URL="http://autoaudit-backend-api.${NAMESPACE}:8000"

# Slug for the Job name (controls.graph -> controls-graph etc).
SCRIPT_TAG=$(echo "$SCRIPT" | sed -E 's/\.js$//; s/[^a-z0-9-]+/-/g')

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SCRIPT_DIR="${REPO_ROOT}/tests/load"
JOB_TPL="${SCRIPT_DIR}/in-cluster/k6-job.yaml"

if [ ! -f "${SCRIPT_DIR}/${SCRIPT}" ]; then
  echo "Script ${SCRIPT_DIR}/${SCRIPT} not found." >&2
  exit 1
fi

# 1. ConfigMap.
echo ">> syncing k6-scripts ConfigMap"
kubectl -n "$NAMESPACE" create configmap k6-scripts \
  --from-file="${SCRIPT_DIR}/api-baseline.js" \
  --from-file="${SCRIPT_DIR}/scan-fanout.js" \
  --from-file="${SCRIPT_DIR}/sustained.js" \
  --dry-run=client -o yaml | kubectl apply -f -

# 2. Render + create the Job.
echo ">> creating Job (script=${SCRIPT}, base_url=${BASE_URL}, extra_args=${EXTRA_ARGS:-<none>})"
job_name=$(SCRIPT="$SCRIPT" SCRIPT_TAG="$SCRIPT_TAG" BASE_URL="$BASE_URL" EXTRA_ARGS="$EXTRA_ARGS" \
  envsubst '$SCRIPT $SCRIPT_TAG $BASE_URL $EXTRA_ARGS' < "$JOB_TPL" | kubectl create -f - -o jsonpath='{.metadata.name}')
echo ">> created job/${job_name}"

# 3. Wait for the pod to exist, then follow logs.
echo ">> waiting for pod ..."
for _ in $(seq 1 30); do
  pod=$(kubectl -n "$NAMESPACE" get pod -l job-name="$job_name" -o jsonpath='{.items[0].metadata.name}' 2>/dev/null || true)
  if [ -n "${pod:-}" ]; then break; fi
  sleep 1
done

if [ -z "${pod:-}" ]; then
  echo "Pod for job/${job_name} did not appear within 30s." >&2
  exit 1
fi

echo ">> waiting for init container to finish ..."
kubectl -n "$NAMESPACE" wait --for=condition=Initialized "pod/$pod" --timeout=2m || true

echo ">> init container (login) logs:"
kubectl -n "$NAMESPACE" logs "$pod" -c login

init_exit=$(kubectl -n "$NAMESPACE" get pod "$pod" -o jsonpath='{.status.initContainerStatuses[0].state.terminated.exitCode}' 2>/dev/null || true)
if [ "${init_exit:-1}" != "0" ]; then
  echo ">> init container failed (exit ${init_exit:-?}). Aborting." >&2
  exit 1
fi

echo ">> waiting for k6 container to start ..."
for _ in $(seq 1 30); do
  if kubectl -n "$NAMESPACE" logs "$pod" -c k6 --tail=0 >/dev/null 2>&1; then
    break
  fi
  sleep 1
done

echo ">> following k6 logs ..."
kubectl -n "$NAMESPACE" logs -f "$pod" -c k6
