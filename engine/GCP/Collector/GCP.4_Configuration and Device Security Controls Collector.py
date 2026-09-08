"""
GCP Configuration and Device Security Controls Collector

Covers CIS GCP Foundations Control 4 (mapped):

    4.1  – Establish and Maintain a Secure Configuration Process
    4.2  – Establish and Maintain a Secure Configuration Process for
           Network Infrastructure
    4.3  – Configure Automatic Session Locking on Enterprise Assets
    4.4  – Implement and Manage a Firewall on Servers
    4.5  – Implement and Manage a Firewall on End-User Devices
    4.6  – Securely Manage Enterprise Assets and Software
    4.7  – Manage Default Accounts on Enterprise Assets and Software
    4.8  – Uninstall or Disable Unnecessary Services on Enterprise Assets
           and Software
    4.9  – Configure Trusted DNS Servers on Enterprise Assets
    4.10 – Enforce Automatic Device Lockout on Portable End-User Devices
    4.11 – Enforce Remote Wipe Capability on Portable End-User Devices
    4.12 – Separate Enterprise Workspaces on Mobile End-User Devices

Control Theme:
    Establish and maintain secure configuration, network security,
    endpoint security, identity hardening, service minimization,
    DNS security, mobile security, and controlled administrative access.

Google Cloud implementation may include:

    - Organization Policy
    - VPC Firewall Rules
    - Hierarchical Firewall Policies
    - Cloud Armor
    - Cloud Logging
    - Cloud Audit Logs
    - Cloud DNS
    - OS Config / VM Manager
    - OS Login
    - Identity-Aware Proxy (IAP)
    - IAM
    - Compute Engine
    - Hardened VM Images
    - Instance Templates
    - Google Workspace / MDM
    - Android Enterprise
    - iOS Managed App Configuration
    - Context-Aware Access
    - Artifact Registry

Required Permissions may include:

    - roles/orgpolicy.policyViewer
    - roles/compute.viewer
    - roles/compute.securityAdmin
    - roles/logging.viewer
    - roles/dns.viewer
    - roles/osconfig.osPolicyAssignmentViewer
    - roles/iam.securityReviewer
    - roles/iam.serviceAccountViewer
    - roles/iap.settings.get
    - roles/monitoring.viewer
    - roles/asset.viewer

NOTE:
    Endpoint/mobile controls such as session locking, local firewall,
    device lockout, remote wipe, and work-profile separation may be
    enforced by an endpoint management / MDM platform rather than GCP.

    The collector therefore records these controls as evidence signals
    supplied by the organization's endpoint-management integration.
"""

from typing import Any
from datetime import datetime, timedelta

from collectors.base import BaseDataCollector
from collectors.gcp_client import GCPClient


class GcpConfigurationDeviceSecurityControlsCollector(
    BaseDataCollector
):
    """
    Collects configuration and device security evidence required
    for CIS Control 4 safeguards.
    """

    async def collect(
        self,
        client: GCPClient
    ) -> dict[str, Any]:

        # =========================================================
        # Core Data Sources
        # =========================================================

        organization_policies = (
            await client.get_organization_policies()
        )

        firewall_rules = (
            await client.get_vpc_firewall_rules()
        )

        hierarchical_firewall_policies = (
            await client.get_hierarchical_firewall_policies()
        )

        firewall_logs = (
            await client.get_firewall_logs()
        )

        cloud_armor_policies = (
            await client.get_cloud_armor_policies()
        )

        cloud_dns_policies = (
            await client.get_cloud_dns_policies()
        )

        dns_logs = (
            await client.get_dns_logs()
        )

        os_policy_assignments = (
            await client.get_os_policy_assignments()
        )

        os_policy_compliance = (
            await client.get_os_policy_compliance()
        )

        compute_instances = (
            await client.get_compute_instances()
        )

        instance_templates = (
            await client.get_instance_templates()
        )

        images = (
            await client.get_compute_images()
        )

        iam_bindings = (
            await client.get_iam_policy_bindings()
        )

        service_accounts = (
            await client.get_service_accounts()
        )

        service_account_keys = (
            await client.get_service_account_keys()
        )

        audit_logs = (
            await client.get_audit_logs()
        )

        iap_configuration = (
            await client.get_iap_configuration()
        )

        tls_policies = (
            await client.get_tls_policies()
        )

        change_records = (
            await client.get_change_records()
        )

        review_records = (
            await client.get_security_review_records()
        )

        # Endpoint / MDM evidence

        endpoint_policies = (
            await client.get_endpoint_management_policies()
        )

        endpoint_compliance = (
            await client.get_endpoint_compliance()
        )

        endpoint_exceptions = (
            await client.get_endpoint_exceptions()
        )

        mobile_policies = (
            await client.get_mobile_management_policies()
        )

        mobile_compliance = (
            await client.get_mobile_compliance()
        )

        wipe_events = (
            await client.get_remote_wipe_events()
        )

        lockout_events = (
            await client.get_device_lockout_events()
        )

        device_access_events = (
            await client.get_device_access_events()
        )

        # =========================================================
        # Derived Signals
        # =========================================================

        firewall_inventory = (
            self._build_firewall_inventory(
                firewall_rules,
                hierarchical_firewall_policies
            )
        )

        default_deny_verified = (
            self._verify_default_deny(
                firewall_inventory
            )
        )

        high_risk_logging_verified = (
            self._verify_firewall_logging(
                firewall_logs,
                firewall_inventory
            )
        )

        secure_protocols = (
            self._extract_secure_management_protocols(
                iap_configuration,
                tls_policies
            )
        )

        insecure_management_exposure = (
            self._detect_insecure_management_exposure(
                compute_instances,
                firewall_rules
            )
        )

        default_accounts = (
            self._extract_default_account_evidence(
                compute_instances,
                os_policy_assignments
            )
        )

        service_inventory = (
            self._build_service_inventory(
                os_policy_assignments,
                os_policy_compliance
            )
        )

        dns_configuration = (
            self._build_dns_configuration(
                cloud_dns_policies,
                dns_logs
            )
        )

        review_history = (
            self._extract_review_history(
                review_records,
                change_records
            )
        )

        remediation_history = (
            self._extract_remediation_history(
                change_records
            )
        )

        # =========================================================
        # Flags / Control Signals
        # =========================================================

        data = {

            # =====================================================
            # 4.1 Secure Configuration Process
            # =====================================================

            "4_1_secure_configuration_process_defined":
                client.config.get(
                    "secure_configuration_process_defined",
                    False
                ),

            "4_1_configuration_standard_approved":
                client.config.get(
                    "configuration_standard_approved",
                    False
                ),

            "4_1_annual_review_verified":
                self._annual_review_verified(
                    review_history
                ),

            "4_1_org_policy_guardrails_present":
                bool(organization_policies),

            "4_1_hardened_images_present":
                bool(images),

            "4_1_templates_present":
                bool(instance_templates),

            "4_1_drift_monitoring_present":
                bool(os_policy_compliance),

            "4_1_change_governance_verified":
                bool(change_records),

            "4_1_remediation_records":
                remediation_history,

            # =====================================================
            # 4.2 Network Infrastructure Configuration
            # =====================================================

            "4_2_network_configuration_standard_defined":
                client.config.get(
                    "network_configuration_standard_defined",
                    False
                ),

            "4_2_default_deny_verified":
                default_deny_verified,

            "4_2_firewall_policy_scope_defined":
                self._firewall_scope_defined(
                    firewall_inventory
                ),

            "4_2_firewall_logging_enabled":
                high_risk_logging_verified,

            "4_2_change_governance_verified":
                bool(change_records),

            "4_2_recertification_verified":
                self._recertification_verified(
                    review_history
                ),

            "4_2_firewall_rules":
                firewall_inventory,

            # =====================================================
            # 4.3 Automatic Session Locking
            # =====================================================

            "4_3_endpoint_session_lock_policy_defined":
                self._endpoint_policy_exists(
                    endpoint_policies,
                    "session_lock"
                ),

            "4_3_laptop_timeout_minutes":
                client.config.get(
                    "laptop_session_lock_timeout_minutes",
                    0
                ),

            "4_3_mobile_timeout_minutes":
                client.config.get(
                    "mobile_session_lock_timeout_minutes",
                    0
                ),

            "4_3_password_on_resume":
                client.config.get(
                    "password_on_resume",
                    False
                ),

            "4_3_endpoint_assignment_verified":
                bool(endpoint_compliance),

            "4_3_exceptions_controlled":
                self._exceptions_controlled(
                    endpoint_exceptions
                ),

            "4_3_os_config_compliance":
                bool(os_policy_compliance),

            # =====================================================
            # 4.4 Firewall on Servers
            # =====================================================

            "4_4_server_firewall_present":
                bool(firewall_inventory),

            "4_4_default_deny_verified":
                default_deny_verified,

            "4_4_high_risk_logging_enabled":
                high_risk_logging_verified,

            "4_4_cloud_armor_configured":
                bool(cloud_armor_policies),

            "4_4_host_firewall_in_scope":
                client.config.get(
                    "host_firewall_in_scope",
                    False
                ),

            "4_4_host_firewall_enforced":
                client.config.get(
                    "host_firewall_enforced",
                    False
                ),

            "4_4_rule_review_verified":
                self._recertification_verified(
                    review_history
                ),

            "4_4_firewall_rules":
                firewall_inventory,

            # =====================================================
            # 4.5 Firewall on End-User Devices
            # =====================================================

            "4_5_endpoint_firewall_policy_defined":
                self._endpoint_policy_exists(
                    endpoint_policies,
                    "firewall"
                ),

            "4_5_default_deny":
                client.config.get(
                    "endpoint_firewall_default_deny",
                    False
                ),

            "4_5_allowed_services_defined":
                client.config.get(
                    "endpoint_allowed_services_defined",
                    False
                ),

            "4_5_assignment_verified":
                bool(endpoint_compliance),

            "4_5_exceptions_controlled":
                self._exceptions_controlled(
                    endpoint_exceptions
                ),

            "4_5_context_aware_access_supporting":
                client.config.get(
                    "context_aware_access_enabled",
                    False
                ),

            # =====================================================
            # 4.6 Secure Management of Assets and Software
            # =====================================================

            "4_6_secure_management_standard_defined":
                client.config.get(
                    "secure_management_standard_defined",
                    False
                ),

            "4_6_os_login_enabled":
                client.config.get(
                    "os_login_enabled",
                    False
                ),

            "4_6_project_wide_ssh_keys_disabled":
                client.config.get(
                    "project_wide_ssh_keys_disabled",
                    False
                ),

            "4_6_iap_enabled":
                bool(iap_configuration),

            "4_6_secure_protocols_verified":
                bool(secure_protocols),

            "4_6_insecure_management_exposure":
                insecure_management_exposure,

            "4_6_tls_policy_verified":
                bool(tls_policies),

            "4_6_audit_traceability":
                bool(audit_logs),

            # =====================================================
            # 4.7 Default Accounts
            # =====================================================

            "4_7_os_login_enabled":
                client.config.get(
                    "os_login_enabled",
                    False
                ),

            "4_7_default_accounts_restricted":
                self._default_accounts_restricted(
                    default_accounts
                ),

            "4_7_root_remote_login_disabled":
                client.config.get(
                    "root_remote_login_disabled",
                    False
                ),

            "4_7_service_account_key_creation_restricted":
                client.config.get(
                    "service_account_key_creation_restricted",
                    False
                ),

            "4_7_existing_service_account_keys_reviewed":
                self._service_account_keys_reviewed(
                    service_account_keys
                ),

            "4_7_privileged_access_individual":
                self._privileged_access_individual(
                    iam_bindings
                ),

            "4_7_access_review_verified":
                self._recertification_verified(
                    review_history
                ),

            "4_7_default_account_evidence":
                default_accounts,

            # =====================================================
            # 4.8 Unnecessary Services
            # =====================================================

            "4_8_service_baseline_defined":
                client.config.get(
                    "service_baseline_defined",
                    False
                ),

            "4_8_prohibited_services_defined":
                client.config.get(
                    "prohibited_services_defined",
                    False
                ),

            "4_8_os_policy_enforced":
                self._os_policy_enforced(
                    os_policy_assignments
                ),

            "4_8_compliance_reporting_available":
                bool(os_policy_compliance),

            "4_8_unnecessary_services_detected":
                self._detect_unnecessary_services(
                    service_inventory
                ),

            "4_8_golden_image_baseline_present":
                bool(images),

            "4_8_exceptions_controlled":
                self._exceptions_controlled(
                    endpoint_exceptions
                ),

            "4_8_service_inventory":
                service_inventory,

            # =====================================================
            # 4.9 Trusted DNS
            # =====================================================

            "4_9_dns_policy_defined":
                bool(cloud_dns_policies),

            "4_9_dns_scope_defined":
                self._dns_scope_defined(
                    cloud_dns_policies
                ),

            "4_9_dns_logging_enabled":
                bool(dns_logs),

            "4_9_dns_bypass_restricted":
                client.config.get(
                    "dns_bypass_restricted",
                    False
                ),

            "4_9_approved_resolvers_defined":
                client.config.get(
                    "approved_dns_resolvers_defined",
                    False
                ),

            "4_9_dns_review_verified":
                bool(review_history),

            "4_9_dns_configuration":
                dns_configuration,

            # =====================================================
            # 4.10 Automatic Device Lockout
            # =====================================================

            "4_10_lockout_policy_defined":
                self._endpoint_policy_exists(
                    endpoint_policies,
                    "lockout"
                ),

            "4_10_laptop_threshold":
                client.config.get(
                    "laptop_lockout_threshold",
                    0
                ),

            "4_10_mobile_threshold":
                client.config.get(
                    "mobile_lockout_threshold",
                    0
                ),

            "4_10_lockout_assignment_verified":
                bool(endpoint_compliance),

            "4_10_lockout_testing_verified":
                bool(lockout_events),

            "4_10_exceptions_controlled":
                self._exceptions_controlled(
                    endpoint_exceptions
                ),

            "4_10_context_aware_access_supporting":
                client.config.get(
                    "context_aware_access_enabled",
                    False
                ),

            # =====================================================
            # 4.11 Remote Wipe
            # =====================================================

            "4_11_remote_wipe_capability_enabled":
                client.config.get(
                    "remote_wipe_enabled",
                    False
                ),

            "4_11_remote_wipe_assignment_verified":
                bool(mobile_policies),

            "4_11_test_wipe_verified":
                bool(wipe_events),

            "4_11_wipe_completion_verified":
                self._wipe_completion_verified(
                    wipe_events
                ),

            "4_11_lost_device_runbook_defined":
                client.config.get(
                    "lost_device_runbook_defined",
                    False
                ),

            "4_11_offboarding_runbook_defined":
                client.config.get(
                    "offboarding_runbook_defined",
                    False
                ),

            "4_11_iam_deprovisioning_verified":
                self._iam_deprovisioning_verified(
                    audit_logs
                ),

            "4_11_session_revocation_verified":
                self._session_revocation_verified(
                    audit_logs
                ),

            "4_11_wipe_events":
                wipe_events,

            # =====================================================
            # 4.12 Enterprise Workspace Separation
            # =====================================================

            "4_12_android_work_profile_enabled":
                client.config.get(
                    "android_work_profile_enabled",
                    False
                ),

            "4_12_ios_managed_configuration_enabled":
                client.config.get(
                    "ios_managed_configuration_enabled",
                    False
                ),

            "4_12_workspace_assignment_verified":
                bool(mobile_policies),

            "4_12_data_sharing_restrictions_enabled":
                client.config.get(
                    "mobile_data_sharing_restrictions_enabled",
                    False
                ),

            "4_12_copy_paste_restriction_enabled":
                client.config.get(
                    "mobile_copy_paste_restricted",
                    False
                ),

            "4_12_personal_backup_restricted":
                client.config.get(
                    "mobile_personal_backup_restricted",
                    False
                ),

            "4_12_conditional_access_enforced":
                client.config.get(
                    "mobile_conditional_access_enforced",
                    False
                ),

            "4_12_mobile_compliance_verified":
                bool(mobile_compliance),

            "4_12_exceptions_controlled":
                self._exceptions_controlled(
                    endpoint_exceptions
                ),

            # =====================================================
            # General Evidence
            # =====================================================

            "collection_timestamp":
                datetime.utcnow().isoformat(),

            "change_records":
                change_records,

            "review_history":
                review_history,

            "audit_log_count":
                len(audit_logs),

            "endpoint_compliance_count":
                len(endpoint_compliance),

            "mobile_compliance_count":
                len(mobile_compliance),
        }

        return data

    # =============================================================
    # Extraction Logic
    # =============================================================

    def _build_firewall_inventory(
        self,
        firewall_rules,
        hierarchical_policies
    ):
        inventory = []

        for rule in firewall_rules:
            inventory.append({
                "name": rule.get("name"),
                "direction": rule.get("direction"),
                "action": rule.get("action"),
                "priority": rule.get("priority"),
                "targets": rule.get("targets"),
                "source_ranges": rule.get(
                    "sourceRanges"
                ),
                "destination_ranges": rule.get(
                    "destinationRanges"
                ),
                "ports": rule.get("ports"),
                "protocols": rule.get(
                    "protocols"
                ),
                "logging_enabled": rule.get(
                    "loggingEnabled",
                    False
                ),
            })

        for policy in hierarchical_policies:
            inventory.append({
                "name": policy.get("name"),
                "direction": policy.get("direction"),
                "action": policy.get("action"),
                "priority": policy.get("priority"),
                "targets": policy.get("targets"),
                "source_ranges": policy.get(
                    "sourceRanges"
                ),
                "destination_ranges": policy.get(
                    "destinationRanges"
                ),
                "ports": policy.get("ports"),
                "protocols": policy.get(
                    "protocols"
                ),
                "logging_enabled": policy.get(
                    "loggingEnabled",
                    False
                ),
            })

        return inventory

    def _verify_default_deny(
        self,
        firewall_rules
    ):
        if not firewall_rules:
            return False

        for rule in firewall_rules:
            if (
                rule.get("direction") == "INGRESS"
                and rule.get("action") == "ALLOW"
                and self._broad_source(rule)
            ):
                return False

        return True

    def _broad_source(self, rule):
        sources = rule.get(
            "source_ranges",
            []
        )

        return (
            "0.0.0.0/0" in sources
            and not rule.get("targets")
        )

    def _verify_firewall_logging(
        self,
        firewall_logs,
        firewall_rules
    ):
        if not firewall_rules:
            return False

        high_risk_rules = [
            rule for rule in firewall_rules
            if self._is_high_risk_rule(rule)
        ]

        if not high_risk_rules:
            return False

        return any(
            rule.get("logging_enabled") is True
            for rule in high_risk_rules
        ) and bool(firewall_logs)

    def _is_high_risk_rule(
        self,
        rule
    ):
        ports = rule.get(
            "ports",
            []
        )

        risky_ports = {
            "22",
            "23",
            "3389",
            "80",
            "443"
        }

        return any(
            str(port) in risky_ports
            for port in ports
        )

    def _firewall_scope_defined(
        self,
        firewall_inventory
    ):
        if not firewall_inventory:
            return False

        return all(
            rule.get("targets")
            for rule in firewall_inventory
        )

    def _endpoint_policy_exists(
        self,
        policies,
        policy_type
    ):
        for policy in policies:
            if policy.get("type") == policy_type:
                return True

        return False

    def _exceptions_controlled(
        self,
        exceptions
    ):
        if not exceptions:
            return True

        for exception in exceptions:
            if not all([
                exception.get("justification"),
                exception.get("approver"),
                exception.get("expiry_date")
            ]):
                return False

        return True

    def _annual_review_verified(
        self,
        review_history
    ):
        if not review_history:
            return False

        cutoff = (
            datetime.utcnow()
            - timedelta(days=366)
        )

        for review in review_history:
            timestamp = review.get(
                "timestamp"
            )

            if timestamp:
                return True

        return False

    def _recertification_verified(
        self,
        review_history
    ):
        if not review_history:
            return False

        return any(
            review.get("status") == "APPROVED"
            or review.get("status") == "SUCCESS"
            for review in review_history
        )

    def _extract_secure_management_protocols(
        self,
        iap_configuration,
        tls_policies
    ):
        protocols = []

        if iap_configuration:
            protocols.append("IAP")

        if tls_policies:
            protocols.append("HTTPS/TLS")

        return protocols

    def _detect_insecure_management_exposure(
        self,
        instances,
        firewall_rules
    ):
        exposed = []

        for instance in instances:
            public_ip = instance.get(
                "public_ip"
            )

            if not public_ip:
                continue

            for rule in firewall_rules:
                ports = rule.get(
                    "ports",
                    []
                )

                if (
                    rule.get("direction")
                    == "INGRESS"
                    and rule.get("action")
                    == "ALLOW"
                    and any(
                        str(port) in {
                            "22",
                            "23",
                            "3389"
                        }
                        for port in ports
                    )
                ):
                    exposed.append({
                        "instance": instance.get(
                            "name"
                        ),
                        "public_ip": public_ip,
                        "rule": rule.get(
                            "name"
                        )
                    })

        return exposed

    def _extract_default_account_evidence(
        self,
        instances,
        os_policies
    ):
        evidence = []

        for instance in instances:
            evidence.append({
                "instance": instance.get(
                    "name"
                ),
                "root_remote_login":
                    instance.get(
                        "rootRemoteLogin"
                    ),
                "default_accounts":
                    instance.get(
                        "defaultAccounts",
                        []
                    )
            })

        return evidence

    def _default_accounts_restricted(
        self,
        accounts
    ):
        if not accounts:
            return False

        for account in accounts:
            if account.get(
                "root_remote_login"
            ) is True:
                return False

        return True

    def _service_account_keys_reviewed(
        self,
        keys
    ):
        if not keys:
            return True

        return all(
            key.get("reviewed") is True
            for key in keys
        )

    def _privileged_access_individual(
        self,
        bindings
    ):
        if not bindings:
            return False

        for binding in bindings:
            if binding.get(
                "shared_admin_identity"
            ) is True:
                return False

        return True

    def _os_policy_enforced(
        self,
        assignments
    ):
        if not assignments:
            return False

        return any(
            assignment.get(
                "enforcementMode"
            ) == "ENFORCE"
            for assignment in assignments
        )

    def _build_service_inventory(
        self,
        assignments,
        compliance
    ):
        services = []

        for assignment in assignments:
            services.append({
                "policy": assignment.get(
                    "name"
                ),
                "target": assignment.get(
                    "target"
                ),
                "desired_state":
                    assignment.get(
                        "desiredState"
                    ),
                "compliance":
                    assignment.get(
                        "compliance"
                    )
            })

        return services

    def _detect_unnecessary_services(
        self,
        services
    ):
        return [
            service
            for service in services
            if service.get(
                "compliance"
            ) == "NON_COMPLIANT"
        ]

    def _dns_scope_defined(
        self,
        policies
    ):
        if not policies:
            return False

        return all(
            policy.get("scope")
            for policy in policies
        )

    def _build_dns_configuration(
        self,
        policies,
        logs
    ):
        return {
            "policy_count": len(policies),
            "logging_enabled": bool(logs),
            "policies": policies
        }

    def _wipe_completion_verified(
        self,
        wipe_events
    ):
        if not wipe_events:
            return False

        return any(
            event.get("status") == "COMPLETED"
            for event in wipe_events
        )

    def _iam_deprovisioning_verified(
        self,
        audit_logs
    ):
        for event in audit_logs:
            action = str(
                event.get("action", "")
            ).lower()

            if any(
                keyword in action
                for keyword in [
                    "disable",
                    "remove",
                    "revoke"
                ]
            ):
                return True

        return False

    def _session_revocation_verified(
        self,
        audit_logs
    ):
        for event in audit_logs:
            action = str(
                event.get("action", "")
            ).lower()

            if "revoke" in action:
                return True

        return False

    def _extract_review_history(
        self,
        reviews,
        changes
    ):
        records = []

        for review in reviews:
            records.append({
                "type": "REVIEW",
                "name": review.get("name"),
                "timestamp": review.get(
                    "timestamp"
                ),
                "status": review.get(
                    "status"
                ),
                "owner": review.get(
                    "owner"
                )
            })

        for change in changes:
            records.append({
                "type": "CHANGE",
                "name": change.get("name"),
                "timestamp": change.get(
                    "timestamp"
                ),
                "status": change.get(
                    "status"
                ),
                "owner": change.get(
                    "approver"
                )
            })

        return records

    def _extract_remediation_history(
        self,
        changes
    ):
        remediation = []

        for change in changes:
            if change.get(
                "remediation"
            ):
                remediation.append({
                    "change_id":
                        change.get(
                            "name"
                        ),
                    "action":
                        change.get(
                            "remediation"
                        ),
                    "timestamp":
                        change.get(
                            "timestamp"
                        ),
                    "approver":
                        change.get(
                            "approver"
                        )
                })

        return remediation
		