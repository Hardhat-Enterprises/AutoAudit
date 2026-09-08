# METADATA
# title: Encrypt Sensitive Data in Transit (GCP)
# description: |
#   Sensitive data transmitted through GCP services must be protected using
#   encrypted transport protocols such as TLS. External entry points must
#   enforce HTTPS with valid certificates, and sensitive internal
#   service-to-service communication must use TLS or mutual TLS where
#   applicable.
#
#   The control verifies:
#   - HTTPS/TLS is enforced for external sensitive services
#   - Valid certificate configuration exists
#   - HTTP-to-HTTPS redirects or plaintext blocking are configured
#   - Internal service-to-service TLS or mutual TLS is configured where required
#   - Plaintext listeners are not exposed for sensitive services
#   - Transport encryption enforcement evidence exists
#
# related_resources:
# - ref: https://cloud.google.com/load-balancing/docs/ssl-certificates
#   description: Google Cloud Load Balancing SSL Certificate Documentation
# - ref: https://cloud.google.com/load-balancing/docs/https
#   description: Google Cloud HTTPS Load Balancing Documentation
# - ref: https://cloud.google.com/api-gateway/docs
#   description: Google Cloud API Gateway Documentation
# - ref: https://cloud.google.com/service-mesh/docs
#   description: Google Cloud Service Mesh Documentation
#
# custom:
#   control_id: CIS-3.10
#   framework: cis
#   benchmark: gcp-foundations
#   version: v2.0.0
#   safeguard: 3.10
#   severity: high
#   service: Network Security
#   asset_type: Data
#   implementation_group: 2
#   requires_permissions:
#   - compute.backendServices.get
#   - compute.targetHttpsProxies.get
#   - compute.sslCertificates.get
#   - compute.urlMaps.get
#   - apigateway.gateways.get
#   - apigateway.apis.get
#   - logging.viewer

package cis.gcp_foundations.v2_0_0.control_3_10

import rego.v1

# ---------------------------
# Default Result
# ---------------------------
default result := {
  "compliant": false,
  "message": "Evaluation failed: insufficient encryption-in-transit evidence",
  "details": {}
}

default compliant := false

# ---------------------------
# Compliance Logic
# ---------------------------
compliant if {
  input.external_tls_required == true
  input.https_listeners_configured == true
  input.certificates_configured == true
  input.plaintext_external_access_blocked == true
  input.internal_tls_required == true
  input.internal_tls_enforcement_verified == true
  input.transport_enforcement_evidence_available == true
  valid_external_tls
  valid_internal_tls
  valid_enforcement_evidence
}

# ---------------------------
# Validate External TLS
# ---------------------------
valid_external_tls if {
  some endpoint in input.external_endpoints

  endpoint.name != ""
  endpoint.service_type != ""
  endpoint.listener_protocol == "HTTPS"
  endpoint.certificate_id != ""
  endpoint.tls_version != ""
  endpoint.plaintext_allowed == false
}

# ---------------------------
# Validate Internal TLS
# ---------------------------
valid_internal_tls if {
  every service in input.internal_tls_services {
    service.source_service != ""
    service.destination_service != ""
    service.protocol != ""
    service.protocol in ["TLS", "mTLS"]
    service.plaintext_allowed == false
  }
}

# ---------------------------
# Validate Enforcement Evidence
# ---------------------------
valid_enforcement_evidence if {
  input.transport_enforcement_evidence_available == true
  input.enforcement_evidence_type != ""
  input.enforcement_evidence_date != ""
  input.enforcement_result != ""
}

# ---------------------------
# Result Output
# ---------------------------
result := output if {
  endpoints := get_array(input, "external_endpoints")
  internal_services := get_array(input, "internal_tls_services")
  plaintext_exceptions := get_array(input, "plaintext_exceptions")

  output := {
    "compliant": compliant,
    "message": generate_message,
    "affected_resources": endpoints,
    "details": {
      "external_tls_required":
          input.external_tls_required,
      "https_listeners_configured":
          input.https_listeners_configured,
      "certificates_configured":
          input.certificates_configured,
      "plaintext_external_access_blocked":
          input.plaintext_external_access_blocked,
      "internal_tls_required":
          input.internal_tls_required,
      "internal_tls_enforcement_verified":
          input.internal_tls_enforcement_verified,
      "transport_enforcement_evidence_available":
          input.transport_enforcement_evidence_available,
      "enforcement_evidence_type":
          input.enforcement_evidence_type,
      "enforcement_evidence_date":
          input.enforcement_evidence_date,
      "enforcement_result":
          input.enforcement_result,
      "external_endpoint_count":
          count(endpoints),
      "internal_tls_service_count":
          count(internal_services),
      "plaintext_exception_count":
          count(plaintext_exceptions),
      "requires_example_evidence": true
    }
  }
}

# ---------------------------
# Message Logic
# ---------------------------
generate_message := msg if {
  not input.external_tls_required
  msg := "FAIL: TLS is not required for external sensitive services"
}

generate_message := msg if {
  input.external_tls_required
  not input.https_listeners_configured
  msg := "FAIL: HTTPS listeners are not configured for external sensitive services"
}

generate_message := msg if {
  input.https_listeners_configured
  not valid_external_tls
  msg := "FAIL: External sensitive service endpoints do not consistently enforce HTTPS with TLS"
}

generate_message := msg if {
  valid_external_tls
  not input.certificates_configured
  msg := "FAIL: TLS certificates are not configured for external sensitive service endpoints"
}

generate_message := msg if {
  input.certificates_configured
  not input.plaintext_external_access_blocked
  msg := "FAIL: Plaintext HTTP access remains available for sensitive external services"
}

generate_message := msg if {
  input.plaintext_external_access_blocked
  not input.internal_tls_required
  msg := "FAIL: TLS or mutual TLS is not required for applicable sensitive internal service-to-service communication"
}

generate_message := msg if {
  input.internal_tls_required
  not input.internal_tls_enforcement_verified
  msg := "INCONCLUSIVE: Internal TLS is required but service-to-service enforcement evidence is missing"
}

generate_message := msg if {
  input.internal_tls_enforcement_verified
  not valid_internal_tls
  msg := "FAIL: Internal sensitive service paths include plaintext communication or lack valid TLS/mTLS configuration"
}

generate_message := msg if {
  valid_internal_tls
  not input.transport_enforcement_evidence_available
  msg := "INCONCLUSIVE: TLS configuration is present but enforcement evidence is missing"
}

generate_message := msg if {
  input.transport_enforcement_evidence_available
  not valid_enforcement_evidence
  msg := "INCONCLUSIVE: Transport encryption enforcement evidence is incomplete"
}

generate_message := msg if {
  valid_enforcement_evidence
  not compliant
  msg := "INCONCLUSIVE: Encryption-in-transit controls exist but protocol enforcement or internal TLS evidence could not be fully verified"
}

generate_message := msg if {
  compliant
  msg := "PASS: Sensitive GCP data is protected in transit through enforced HTTPS/TLS for external services and TLS/mTLS for applicable internal service paths"
}

# ---------------------------
# Helper Functions
# ---------------------------
get_array(obj, key) := value if {
  value := obj[key]
} else := []
