#!/usr/bin/env bash
# One-time setup: Workload Identity Federation for GitHub Actions -> GCP.
#
# Replaces the old pattern (a long-lived service account JSON key stored as
# the GCP_CREDENTIALS GitHub secret) with short-lived, per-run credentials.
# GitHub issues a signed OIDC token for each workflow run; GCP is configured
# here to trust that token ONLY when it asserts it came from this exact
# repository, and to let it impersonate a purpose-built, read-only service
# account for the duration of the job. No key file is ever created,
# downloaded, or stored anywhere.
#
# Run this once, by whoever has GCP IAM admin access to the target project.
# Requires: gcloud CLI, authenticated as a user with
#   roles/iam.workloadIdentityPoolAdmin, roles/iam.serviceAccountAdmin,
#   roles/resourcemanager.projectIamAdmin (or broader, e.g. Owner).
#
# Usage:
#   ./setup-workload-identity.sh
#
# After it finishes, take the two printed values and add them as
# repository VARIABLES (not secrets - they aren't sensitive) at:
#   https://github.com/Hardhat-Enterprises/AutoAudit/settings/variables/actions
#     GCP_WORKLOAD_IDENTITY_PROVIDER = <printed provider resource name>
#     GCP_SERVICE_ACCOUNT_EMAIL      = <printed service account email>
#
# Then, separately: delete the old GCP_CREDENTIALS secret from repo
# settings and revoke/delete the key it contains in GCP IAM, once you've
# confirmed nothing else still depends on it.

set -euo pipefail

PROJECT_ID="coastal-stone-470308-a0"
REPO="Hardhat-Enterprises/AutoAudit"
POOL_ID="github-actions-pool"
PROVIDER_ID="github-actions-provider"
SERVICE_ACCOUNT_NAME="github-actions-readonly"
SERVICE_ACCOUNT_EMAIL="${SERVICE_ACCOUNT_NAME}@${PROJECT_ID}.iam.gserviceaccount.com"

echo "== Project: ${PROJECT_ID} =="
PROJECT_NUMBER="$(gcloud projects describe "${PROJECT_ID}" --format='value(projectNumber)')"
echo "Project number: ${PROJECT_NUMBER}"

echo
echo "== 1. Enabling required APIs =="
gcloud services enable \
  iamcredentials.googleapis.com \
  sts.googleapis.com \
  --project="${PROJECT_ID}"

echo
echo "== 2. Creating Workload Identity Pool: ${POOL_ID} =="
gcloud iam workload-identity-pools create "${POOL_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --display-name="GitHub Actions Pool" \
  --description="Trust anchor for short-lived GitHub Actions OIDC tokens"

echo
echo "== 3. Creating OIDC Provider: ${PROVIDER_ID} (scoped to ${REPO} only) =="
# The attribute-condition is the critical security control here: without it,
# any GitHub repository anywhere could mint a token this pool would accept.
gcloud iam workload-identity-pools providers create-oidc "${PROVIDER_ID}" \
  --project="${PROJECT_ID}" \
  --location="global" \
  --workload-identity-pool="${POOL_ID}" \
  --display-name="GitHub Actions Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository,attribute.repository_owner=assertion.repository_owner,attribute.ref=assertion.ref" \
  --attribute-condition="assertion.repository == '${REPO}'"

echo
echo "== 4. Creating a new, minimally-scoped service account: ${SERVICE_ACCOUNT_NAME} =="
# Deliberately NOT reusing the old sa-noperms account - it was already
# exposed (its key leaked into git history) and held roles/editor, which
# is far broader than this collector actually needs. Starting clean.
gcloud iam service-accounts create "${SERVICE_ACCOUNT_NAME}" \
  --project="${PROJECT_ID}" \
  --display-name="GitHub Actions - read-only CI collector"

echo
echo "== 5. Granting read-only roles matching what GCPAccess.py actually calls =="
# This is a best-effort least-privilege set based on reading the API calls
# in engine/legacy/engine/GCPAccess.py (IAM policy, networks, firewalls,
# compute instances, Cloud SQL, BigQuery metadata, Dataproc, DNS, bucket
# IAM policies). It has NOT been tested against live API calls - whoever
# runs this should verify each call succeeds and narrow further if a
# broader role turns out to be unnecessary, or add roles/iam.securityReviewer
# if the project-level getIamPolicy call is denied.
ROLES=(
  "roles/viewer"
  "roles/iam.securityReviewer"
)
for ROLE in "${ROLES[@]}"; do
  gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
    --member="serviceAccount:${SERVICE_ACCOUNT_EMAIL}" \
    --role="${ROLE}" \
    --condition=None \
    --quiet
done

echo
echo "== 6. Allowing ONLY ${REPO}'s workflows to impersonate this service account =="
gcloud iam service-accounts add-iam-policy-binding "${SERVICE_ACCOUNT_EMAIL}" \
  --project="${PROJECT_ID}" \
  --role="roles/iam.workloadIdentityUser" \
  --member="principalSet://iam.googleapis.com/projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/attribute.repository/${REPO}"

echo
echo "== Done =="
echo "Add these as repository VARIABLES (Settings > Secrets and variables > Actions > Variables tab) - not secrets, these are not sensitive:"
echo
echo "  GCP_WORKLOAD_IDENTITY_PROVIDER = projects/${PROJECT_NUMBER}/locations/global/workloadIdentityPools/${POOL_ID}/providers/${PROVIDER_ID}"
echo "  GCP_SERVICE_ACCOUNT_EMAIL      = ${SERVICE_ACCOUNT_EMAIL}"
echo
echo "Next: confirm ops.collector.yml runs successfully via workflow_dispatch with these values set,"
echo "then revoke the old GCP_CREDENTIALS key in GCP IAM and delete the GCP_CREDENTIALS GitHub secret."
