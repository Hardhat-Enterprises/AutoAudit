#!/bin/bash
#promtool_validation.sh
#Validates all Prometheus alerting rules YAML files for syntax correctness.
#Usage: ./promtool_validation.sh
#Author: Senior Lead, AutoAudit DevSecOps Team
#Last Updated: 2025-09-17

set -euo pipefail

ALERTS_DIR="$(dirname "$0")/../"

echo "Starting Prometheus alerting rules syntax validation..."

for file in "$ALERTS_DIR"/*.yaml; do
  echo "Validating $file..."
  promtool check rules "$file"

done

echo "All alerting rules passed syntax validation."
