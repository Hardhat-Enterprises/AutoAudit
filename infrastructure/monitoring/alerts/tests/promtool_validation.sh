#!/bin/bash
#promtool_validation.sh
#Validates all Prometheus alerting rules YAML files for syntax correctness.
#Usage: ./promtool_validation.sh
#Author: Senior Lead, AutoAudit DevSecOps Team
#Last Updated: 2025-09-28

set -euo pipefail

ALERTS_DIR="$(dirname "$0")/../"

echo "Starting Prometheus alerting rules syntax validation..."

#Only validating *alerts.yaml and other rule files, exclude alertmanager.yaml
for file in "$ALERTS_DIR"/*alerts.yaml "$ALERTS_DIR"/*_errors.yaml "$ALERTS_DIR"/*health.yaml "$ALERTS_DIR"/*utilisation.yaml "$ALERTS_DIR"/*security.yaml; do
  if [[ -f "$file" ]]; then
    echo "Validating $file..."
    promtool check rules "$file"
  fi
done

echo "All Prometheus alerting rules passed syntax validation."
