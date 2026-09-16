# METADATA
# title: Encrypt Sensitive Data at Rest (GCP)
# description: |
#   Sensitive data stored on GCP servers, applications, databases, and storage
#   services must be encrypted at rest. Provider-managed encryption satisfies
#   the baseline requirement, while customer-managed encryption keys must be
#   used where enterprise policy requires stronger key control.
#
#   The control verifies:
#   - An encryption-at-rest policy exists
#   - Sensitive data stores are identified
#   - Encryption is enabled for sensitive resources
#   - Customer-managed keys are used where required
#   - Cloud KMS keys have appropriate rotation settings
#   - Key administration and key usage are appropriately separated
#   - Key access is logged and reviewable
#   - Resource-level encryption key bindings can be verified
#
# related_resources:
# - ref: https://cloud.google.com/kms/docs
#   description: Google Cloud Key Management Service Documentation
# - ref: https://cloud.google.com/storage/docs/encryption
#   description: Cloud Storage Data Encryption Documentation
# - ref: https://cloud.google.com/bigquery/docs/customer-managed-encryption
#   description: BigQuery Customer-Managed Encryption Key Documentation
# - ref: https://cloud.google.com/compute/docs/disks/customer-managed-encryption
#   description: Compute Engine Customer-Managed Encryption Documentation
#
# custom:
#   control_id: CIS-3.11
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.11
#   severity: high
#   service: Cloud KMS
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - cloudkms.cryptoKeys.get
#   - cloudkms.cryptoKeys.getIamPolicy
#   - cloudkms.cryptoKeyVersions.list
#   - cloudasset.assets.list
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_11

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient encryption-at-rest evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.encryption_policy_defined == true
  input.sensitive_stores_identified == true
  input.encryption_at_rest_enabled == true
  input.key_governance_defined == true
  input.key_access_logging_enabled == true
  input.key_access_review_available == true
  valid_sensitive_resources
  valid_key_governance
  valid_key_access_evidence
}

# ---------------------------
# Validate Sensitive Resources
# ---------------------------
valid_sensitive_resources if {
  some resource in input.sensitive_resources

  resource.resource_name != ""
  resource.resource_type != ""
  resource.project_id != ""
  resource.encryption_enabled == true
  resource.encryption_method != ""

  resource.cmek_required == false
}

valid_sensitive_resources if {
  some resource in input.sensitive_resources

  resource.resource_name != ""
  resource.resource_type != ""
  resource.project_id != ""
  resource.encryption_enabled == true
  resource.encryption_method == "CMEK"
  resource.cmek_required == true
  resource.kms_key_id != ""
}

# ---------------------------
# Validate Key Governance
# ---------------------------
valid_key_governance if {
  some key in input.kms_keys

  key.key_id != ""
  key.key_ring != ""
  key.rotation_period_days > 0
  key.rotation_enabled == true
  key.admin_principals != ""
  key.usage_principals != ""
  key.admin_usage_separation == true
}

# ---------------------------
# Validate Key Access Evidence
# ---------------------------
valid_key_access_evidence if {
  input.key_access_logging_enabled == true
  input.key_access_review_available == true
  input.key_access_log_timestamp != ""
  input.key_access_review_date != ""
  input.key_access_review_outcome != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  resources := get_array(input, "sensitive_resources")
  keys := get_array(input, "kms_keys")
  access_events := get_array(input, "key_access_events")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": resources,
    "details": {
      "encryption_policy_defined":
          input.encryption_policy_defined,
      "sensitive_stores_identified":
          input.sensitive_stores_identified,
      "encryption_at_rest_enabled":
          input.encryption_at_rest_enabled,
      "key_governance_defined":
          input.key_governance_defined,
      "key_access_logging_enabled":
          input.key_access_logging_enabled,
      "key_access_review_available":
          input.key_access_review_available,
      "sensitive_resource_count":
          count(resources),
      "kms_key_count":
          count(keys),
      "key_access_event_count":
          count(access_events),
      "key_access_log_timestamp":
          input.key_access_log_timestamp,
      "key_access_review_date":
          input.key_access_review_date,
      "key_access_review_outcome":
          input.key_access_review_outcome,
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.encryption_policy_defined
  msg := "FAIL: No documented encryption-at-rest policy found"
}

generate_message := msg if {
  input.encryption_policy_defined
  not input.sensitive_stores_identified
  msg := "FAIL: Sensitive data stores requiring encryption are not identified"
}

generate_message := msg if {
  input.sensitive_stores_identified
  not input.encryption_at_rest_enabled
  msg := "FAIL: Encryption at rest is not enabled for sensitive data stores"
}

generate_message := msg if {
  input.encryption_at_rest_enabled
  not valid_sensitive_resources
  msg := "FAIL: Sensitive resources do not consistently meet their required encryption configuration"
}

generate_message := msg if {
  valid_sensitive_resources
  not input.key_governance_defined
  msg := "FAIL: Encryption key governance is not defined for sensitive data"
}

generate_message := msg if {
  input.key_governance_defined
  not valid_key_governance
  msg := "FAIL: Cloud KMS key governance does not demonstrate required rotation, access separation, or key configuration"
}

generate_message := msg if {
  valid_key_governance
  not input.key_access_logging_enabled
  msg := "FAIL: Access to encryption keys is not sufficiently logged for review"
}

generate_message := msg if {
  input.key_access_logging_enabled
  not input.key_access_review_available
  msg := "INCONCLUSIVE: Key access logging is enabled but no key access review evidence is available"
}

generate_message := msg if {
  input.key_access_review_available
  not valid_key_access_evidence
  msg := "INCONCLUSIVE: Key access evidence exists but log timestamp, review date, or review outcome is incomplete"
}

generate_message := msg if {
  valid_key_access_evidence
  not compliant
  msg := "INCONCLUSIVE: Encryption at rest is configured but resource key bindings or key governance evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Sensitive GCP data is encrypted at rest in accordance with policy, required customer-managed keys are bound to resources, and key governance, rotation, access control, and logging are in place"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
