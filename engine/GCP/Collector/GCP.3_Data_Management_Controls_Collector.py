"""
GCP Data Protection Controls Collector

Covers CIS GCP Foundations / Control 3 Data Safeguards:

    3.1  – Establish and Maintain a Data Management Process
    3.2  – Establish and Maintain a Data Inventory
    3.3  – Configure Data Access Control Lists
    3.4  – Enforce Data Retention
    3.5  – Securely Dispose of Data
    3.6  – Encrypt Data on End-User Devices
    3.7  – Establish and Maintain a Data Classification Scheme
    3.8  – Document Data Flows
    3.9  – Encrypt Data on Removable Media
    3.10 – Encrypt Sensitive Data in Transit
    3.11 – Encrypt Sensitive Data at Rest
    3.12 – Segment Data Processing and Storage Based on Sensitivity
    3.13 – Deploy a Data Loss Prevention Solution
    3.14 – Log Sensitive Data Access

Primary GCP Data Sources:
    - Dataplex / Data Catalog
    - Cloud Asset Inventory
    - Cloud DLP
    - Cloud Storage
    - BigQuery
    - Cloud SQL
    - Cloud KMS
    - IAM
    - Cloud Logging / Cloud Audit Logs
    - VPC Service Controls
    - VPC Flow Logs
    - Load Balancers / HTTPS configuration
    - Certificate Manager
    - Cloud Scheduler
    - Cloud Workflows / automation where applicable

Endpoint-related sources:
    - Google Workspace Endpoint Management
    - Chrome Enterprise / endpoint compliance
    - Endpoint management system configured by the deployment

Required permissions may include:
    - roles/dataplex.viewer
    - roles/cloudasset.viewer
    - roles/dlp.viewer
    - roles/storage.viewer
    - roles/bigquery.metadataViewer
    - roles/cloudsql.viewer
    - roles/cloudkms.viewer
    - roles/iam.securityReviewer
    - roles/logging.viewer
    - roles/compute.viewer
    - roles/accesscontextmanager.policyReader
    - endpoint-management read permissions where applicable

Notes:
    This collector gathers evidence and derives control signals.
    It does not determine final compliance. Final compliance decisions
    are performed by the corresponding Rego controls.
"""

from datetime import datetime, timedelta
from typing import Any

from collectors.base import BaseDataCollector
from collectors.gcp_client import GCPClient


class GcpDataProtectionControlsCollector(BaseDataCollector):
    """Collects GCP evidence required by CIS Data Controls 3.1–3.14."""

    async def collect(
        self,
        client: GCPClient,
    ) -> dict[str, Any]:
        """Collect evidence and derived signals for Control 3."""

        # =========================================================
        # Core GCP Evidence Sources
        # =========================================================

        cai_assets = await client.get_cloud_asset_inventory()

        dataplex_assets = await client.get_dataplex_assets()
        dataplex_tags = await client.get_dataplex_tags()
        dataplex_lineage = await client.get_dataplex_lineage()

        dlp_findings = await client.get_dlp_findings()
        dlp_templates = await client.get_dlp_templates()
        dlp_jobs = await client.get_dlp_jobs()

        storage_buckets = await client.get_storage_buckets()
        storage_objects = await client.get_storage_objects()

        bigquery_datasets = await client.get_bigquery_datasets()
        bigquery_tables = await client.get_bigquery_tables()

        cloudsql_instances = await client.get_cloudsql_instances()

        kms_keys = await client.get_kms_keys()

        iam_policies = await client.get_iam_policies()

        audit_logs = await client.get_audit_logs()
        data_access_logs = await client.get_data_access_logs()

        logging_sinks = await client.get_logging_sinks()

        vpc_service_controls = (
            await client.get_vpc_service_controls()
        )

        vpc_flow_logs = await client.get_vpc_flow_logs()

        load_balancers = await client.get_load_balancers()
        certificates = await client.get_certificates()

        scheduled_jobs = await client.get_scheduled_jobs()

        access_reviews = await client.get_access_reviews()

        disposal_records = await client.get_disposal_records()

        retention_exceptions = (
            await client.get_retention_exceptions()
        )

        review_records = await client.get_data_review_records()

        endpoint_encryption = (
            await client.get_endpoint_encryption_status()
        )

        removable_media_controls = (
            await client.get_removable_media_controls()
        )

        endpoint_exceptions = (
            await client.get_endpoint_exceptions()
        )

        data_flow_documents = (
            await client.get_data_flow_documents()
        )

        data_flow_validation = (
            await client.get_data_flow_validation()
        )

        classification_reviews = (
            await client.get_classification_reviews()
        )

        segmentation_policies = (
            await client.get_data_segmentation_policies()
        )

        cross_tier_access = (
            await client.get_cross_tier_access_records()
        )

        remediation_records = (
            await client.get_remediation_records()
        )

        # =========================================================
        # Derived Evidence
        # =========================================================

        data_inventory = self._build_data_inventory(
            cai_assets,
            dataplex_assets,
            dataplex_tags,
        )

        sensitive_data_inventory = (
            self._extract_sensitive_data_inventory(
                dlp_findings,
                data_inventory,
            )
        )

        data_owners = self._extract_data_owners(
            dataplex_assets,
            dataplex_tags,
        )

        access_records = self._build_access_records(
            iam_policies,
            storage_buckets,
            bigquery_datasets,
            bigquery_tables,
            cloudsql_instances,
        )

        sensitive_access_records = self._filter_sensitive_access(
            access_records,
            sensitive_data_inventory,
        )

        retention_records = self._build_retention_records(
            storage_buckets,
            bigquery_datasets,
            bigquery_tables,
            cloudsql_instances,
        )

        disposal_evidence = self._build_disposal_evidence(
            disposal_records,
            audit_logs,
        )

        classification_records = self._build_classification_records(
            dataplex_tags,
            bigquery_tables,
            dlp_findings,
        )

        data_flow_records = self._build_data_flow_records(
            data_flow_documents,
            data_flow_validation,
            dataplex_lineage,
            cai_assets,
        )

        tls_records = self._build_tls_records(
            load_balancers,
            certificates,
        )

        encryption_at_rest = (
            self._build_encryption_at_rest_records(
                storage_buckets,
                bigquery_datasets,
                bigquery_tables,
                cloudsql_instances,
                kms_keys,
            )
        )

        segmentation_records = self._build_segmentation_records(
            segmentation_policies,
            vpc_service_controls,
            iam_policies,
            cross_tier_access,
        )

        dlp_records = self._build_dlp_records(
            dlp_templates,
            dlp_jobs,
            dlp_findings,
            remediation_records,
        )

        data_access_records = self._build_data_access_records(
            data_access_logs,
            sensitive_data_inventory,
        )

        review_history = self._build_review_history(
            review_records,
            scheduled_jobs,
            classification_reviews,
            access_reviews,
        )

        # =========================================================
        # Control Signals
        # =========================================================

        data = {
            # =====================================================
            # 3.1 Data Management Process
            # =====================================================

            "process_documented": client.config.get(
                "data_management_process_documented",
                False,
            ),
            "process_approved": client.config.get(
                "data_management_process_approved",
                False,
            ),
            "owners_defined": bool(data_owners),
            "handling_requirements_defined": client.config.get(
                "data_handling_requirements_defined",
                False,
            ),
            "retention_requirements_defined": client.config.get(
                "retention_requirements_defined",
                False,
            ),
            "disposal_requirements_defined": client.config.get(
                "disposal_requirements_defined",
                False,
            ),
            "annual_review_required": client.config.get(
                "data_management_annual_review",
                True,
            ),
            "annual_review_verified": self._review_verified(
                review_history,
                365,
            ),
            "data_management_review_timestamp": (
                self._latest_timestamp(review_history)
            ),
            "data_owners": data_owners,
            "data_management_evidence": review_records,

            # =====================================================
            # 3.2 Data Inventory
            # =====================================================

            "data_inventory_exists": bool(data_inventory),
            "inventory_scope_defined": client.config.get(
                "data_inventory_scope_defined",
                False,
            ),
            "inventory_required_fields_present": (
                self._validate_data_inventory(data_inventory)
            ),
            "inventory_refresh_schedule_defined": client.config.get(
                "data_inventory_refresh_schedule",
                False,
            ),
            "inventory_refresh_verified": (
                self._recent_execution_verified(
                    scheduled_jobs,
                    180,
                )
            ),
            "inventory_review_verified": self._review_verified(
                review_history,
                365,
            ),
            "data_inventory": data_inventory,
            "sensitive_data_inventory": sensitive_data_inventory,
            "dlp_inventory_linkage": bool(
                sensitive_data_inventory and data_inventory
            ),
            "inventory_last_review_timestamp": (
                self._latest_timestamp(review_history)
            ),

            # =====================================================
            # 3.3 Data Access Control Lists
            # =====================================================

            "access_policies_available": bool(iam_policies),
            "need_to_know_enforced": self._need_to_know_enforced(
                access_records
            ),
            "group_based_access": self._group_based_access(
                access_records
            ),
            "privileged_access_controlled": client.config.get(
                "privileged_data_access_controlled",
                False,
            ),
            "public_access_prevented": self._public_access_prevented(
                storage_buckets,
                iam_policies,
            ),
            "sensitive_access_report_available": bool(
                sensitive_access_records
            ),
            "access_review_schedule_defined": client.config.get(
                "data_access_review_schedule",
                False,
            ),
            "access_review_verified": self._review_verified(
                access_reviews,
                180,
            ),
            "access_records": access_records,
            "sensitive_access_records": sensitive_access_records,
            "access_reviews": access_reviews,

            # =====================================================
            # 3.4 Data Retention
            # =====================================================

            "retention_policy_documented": client.config.get(
                "retention_policy_documented",
                False,
            ),
            "minimum_retention_defined": client.config.get(
                "minimum_retention_defined",
                False,
            ),
            "maximum_retention_defined": client.config.get(
                "maximum_retention_defined",
                False,
            ),
            "retention_controls_configured": bool(
                retention_records
            ),
            "retention_alignment_verified": (
                self._retention_alignment_verified(
                    retention_records,
                    client.config,
                )
            ),
            "bucket_lock_evidence": self._bucket_lock_evidence(
                storage_buckets
            ),
            "bigquery_expiration_evidence": (
                self._bigquery_expiration_evidence(
                    bigquery_tables
                )
            ),
            "cloudsql_backup_retention_evidence": (
                self._cloudsql_retention_evidence(
                    cloudsql_instances
                )
            ),
            "retention_exceptions_managed": (
                self._exceptions_managed(
                    retention_exceptions
                )
            ),
            "retention_review_verified": self._review_verified(
                review_history,
                365,
            ),
            "retention_records": retention_records,
            "retention_exceptions": retention_exceptions,

            # =====================================================
            # 3.5 Secure Data Disposal
            # =====================================================

            "disposal_process_documented": client.config.get(
                "data_disposal_process_documented",
                False,
            ),
            "disposal_controls_configured": bool(
                disposal_evidence
            ),
            "backup_disposal_addressed": client.config.get(
                "backup_disposal_addressed",
                False,
            ),
            "replica_disposal_addressed": client.config.get(
                "replica_disposal_addressed",
                False,
            ),
            "legal_holds_managed": client.config.get(
                "legal_holds_managed",
                False,
            ),
            "crypto_shredding_approved": client.config.get(
                "crypto_shredding_approved",
                False,
            ),
            "completed_disposal_example": bool(
                disposal_evidence
            ),
            "disposal_audit_evidence": disposal_evidence,
            "disposal_review_verified": self._review_verified(
                review_history,
                365,
            ),

            # =====================================================
            # 3.6 Encrypt Data on End-User Devices
            # =====================================================

            "endpoint_management_in_scope": client.config.get(
                "endpoint_management_in_scope",
                False,
            ),
            "endpoint_encryption_policy": client.config.get(
                "endpoint_encryption_required",
                False,
            ),
            "endpoint_encryption_enforced": (
                self._endpoint_encryption_enforced(
                    endpoint_encryption
                )
            ),
            "endpoint_coverage_available": bool(
                endpoint_encryption
            ),
            "endpoint_noncompliance_handled": bool(
                endpoint_exceptions
            ),
            "endpoint_review_verified": self._review_verified(
                review_history,
                180,
            ),
            "endpoint_encryption_status": endpoint_encryption,
            "endpoint_exceptions": endpoint_exceptions,
            "endpoint_scope_statement": client.config.get(
                "endpoint_scope_statement",
                "",
            ),

            # =====================================================
            # 3.7 Data Classification Scheme
            # =====================================================

            "classification_scheme_defined": client.config.get(
                "classification_scheme_defined",
                False,
            ),
            "classification_labels_defined": client.config.get(
                "classification_labels_defined",
                False,
            ),
            "classification_tags_configured": bool(
                dataplex_tags
            ),
            "classification_applied": bool(
                classification_records
            ),
            "classification_coverage": self._classification_coverage(
                classification_records,
                data_inventory,
            ),
            "classification_coverage_verified": (
                self._classification_coverage_verified(
                    classification_records,
                    data_inventory,
                )
            ),
            "classification_review_verified": self._review_verified(
                classification_reviews,
                365,
            ),
            "classification_records": classification_records,
            "classification_reviews": classification_reviews,

            # =====================================================
            # 3.8 Document Data Flows
            # =====================================================

            "data_flow_documented": bool(
                data_flow_documents
            ),
            "data_flow_scope_defined": client.config.get(
                "data_flow_scope_defined",
                False,
            ),
            "data_flow_resources_linked": (
                self._data_flow_resources_linked(
                    data_flow_records,
                    cai_assets,
                )
            ),
            "data_flow_validation_available": bool(
                data_flow_validation
            ),
            "dataplex_lineage_available": bool(
                dataplex_lineage
            ),
            "data_flow_review_verified": self._review_verified(
                review_history,
                365,
            ),
            "data_flow_records": data_flow_records,
            "data_flow_validation": data_flow_validation,

            # =====================================================
            # 3.9 Encrypt Data on Removable Media
            # =====================================================

            "removable_media_in_scope": client.config.get(
                "removable_media_in_scope",
                False,
            ),
            "removable_media_encryption_policy": client.config.get(
                "removable_media_encryption_required",
                False,
            ),
            "removable_media_controls": removable_media_controls,
            "removable_media_enforced": bool(
                removable_media_controls
            ),
            "removable_media_exceptions_managed": bool(
                endpoint_exceptions
            ),
            "removable_media_review_verified": (
                self._review_verified(
                    review_history,
                    180,
                )
            ),
            "bulk_export_monitoring": self._bulk_export_monitoring(
                audit_logs
            ),
            "removable_media_scope_statement": client.config.get(
                "removable_media_scope_statement",
                "",
            ),

            # =====================================================
            # 3.10 Encrypt Sensitive Data in Transit
            # =====================================================

            "tls_policy_defined": client.config.get(
                "tls_policy_defined",
                False,
            ),
            "https_required": client.config.get(
                "https_required",
                True,
            ),
            "https_endpoints_present": bool(
                load_balancers
            ),
            "certificates_configured": bool(
                certificates
            ),
            "http_redirect_or_block_configured": (
                self._http_redirect_or_block_configured(
                    load_balancers
                )
            ),
            "internal_tls_required": client.config.get(
                "internal_tls_required",
                False,
            ),
            "internal_tls_enforced": client.config.get(
                "internal_tls_enforced",
                False,
            ),
            "plaintext_sensitive_endpoints": (
                self._plaintext_endpoints(
                    load_balancers
                )
            ),
            "tls_enforcement_verified": (
                self._tls_enforcement_verified(
                    tls_records
                )
            ),
            "tls_records": tls_records,

            # =====================================================
            # 3.11 Encrypt Sensitive Data at Rest
            # =====================================================

            "encryption_policy_defined": client.config.get(
                "encryption_at_rest_policy_defined",
                False,
            ),
            "encryption_at_rest_enabled": (
                self._encryption_at_rest_enabled(
                    encryption_at_rest
                )
            ),
            "customer_managed_keys_required": client.config.get(
                "customer_managed_keys_required",
                False,
            ),
            "customer_managed_keys_configured": bool(
                kms_keys
            ),
            "sensitive_resources_key_bound": (
                self._sensitive_resources_key_bound(
                    encryption_at_rest
                )
            ),
            "key_rotation_enabled": self._key_rotation_enabled(
                kms_keys
            ),
            "key_access_controlled": self._key_access_controlled(
                kms_keys
            ),
            "key_access_logging_enabled": (
                self._key_access_logging_enabled(
                    audit_logs
                )
            ),
            "encryption_at_rest_records": encryption_at_rest,
            "kms_keys": kms_keys,

            # =====================================================
            # 3.12 Segment Data Processing and Storage
            # =====================================================

            "sensitivity_tiers_defined": client.config.get(
                "sensitivity_tiers_defined",
                False,
            ),
            "tiered_folder_project_structure": client.config.get(
                "tiered_folder_project_structure",
                False,
            ),
            "tier_resource_placement_verified": (
                self._tier_resource_placement_verified(
                    segmentation_records
                )
            ),
            "vpc_service_controls_configured": bool(
                vpc_service_controls
            ),
            "restricted_services_configured": (
                self._restricted_services_configured(
                    vpc_service_controls
                )
            ),
            "tier_iam_separation": self._tier_iam_separation(
                iam_policies
            ),
            "tier_key_separation": client.config.get(
                "tier_key_separation",
                False,
            ),
            "cross_tier_access_controlled": (
                self._cross_tier_access_controlled(
                    cross_tier_access
                )
            ),
            "cross_tier_access_auditable": (
                self._cross_tier_access_auditable(
                    cross_tier_access
                )
            ),
            "segmentation_records": segmentation_records,
            "cross_tier_access": cross_tier_access,

            # =====================================================
            # 3.13 Data Loss Prevention
            # =====================================================

            "dlp_enabled": bool(dlp_templates),
            "dlp_policy_configured": bool(dlp_templates),
            "dlp_scope_defined": self._dlp_scope_defined(
                dlp_jobs
            ),
            "dlp_exclusions_documented": client.config.get(
                "dlp_exclusions_documented",
                False,
            ),
            "dlp_recent_findings": bool(dlp_findings),
            "dlp_findings": dlp_findings,
            "dlp_inventory_updates": self._dlp_inventory_updates(
                dlp_findings,
                data_inventory,
            ),
            "dlp_remediation_workflow": bool(
                remediation_records
            ),
            "dlp_remediation_verified": (
                self._remediation_verified(
                    remediation_records
                )
            ),
            "dlp_coverage": self._dlp_coverage(
                dlp_jobs
            ),
            "dlp_records": dlp_records,
            "remediation_records": remediation_records,

            # =====================================================
            # 3.14 Log Sensitive Data Access
            # =====================================================

            "data_access_logging_enabled": bool(
                data_access_logs
            ),
            "sensitive_data_access_logging": (
                self._sensitive_access_logging_enabled(
                    data_access_logs,
                    sensitive_data_inventory,
                )
            ),
            "organization_log_sink_configured": bool(
                logging_sinks
            ),
            "centralized_logging_enabled": (
                self._centralized_logging_enabled(
                    logging_sinks
                )
            ),
            "log_retention_configured": (
                self._log_retention_configured(
                    logging_sinks
                )
            ),
            "access_log_entries": data_access_records,
            "principal_traceability": (
                self._principal_traceability(
                    data_access_records
                )
            ),
            "high_risk_access_detection": (
                self._high_risk_access_detection(
                    audit_logs
                )
            ),
            "access_alert_or_investigation": (
                self._access_alert_or_investigation(
                    audit_logs,
                    remediation_records,
                )
            ),
            "data_access_logging_records": data_access_records,
            "logging_sinks": logging_sinks,

            # =====================================================
            # General Evidence
            # =====================================================

            "collection_timestamp": datetime.utcnow().isoformat(),

            "collection_summary": {
                "cai_assets": len(cai_assets),
                "dataplex_assets": len(dataplex_assets),
                "dlp_findings": len(dlp_findings),
                "storage_buckets": len(storage_buckets),
                "bigquery_datasets": len(bigquery_datasets),
                "bigquery_tables": len(bigquery_tables),
                "cloudsql_instances": len(cloudsql_instances),
                "kms_keys": len(kms_keys),
                "iam_policies": len(iam_policies),
                "audit_logs": len(audit_logs),
                "data_access_logs": len(data_access_logs),
                "data_flow_documents": len(data_flow_documents),
                "review_records": len(review_records),
            },
        }

        return data

    # =========================================================
    # 3.1 / 3.2 – Data Inventory and Ownership
    # =========================================================

    def _build_data_inventory(
        self,
        cai_assets,
        dataplex_assets,
        dataplex_tags,
    ):
        inventory = []
        seen = set()

        for asset in cai_assets:
            asset_type = asset.get("assetType", "")

            if not self._is_data_asset(asset_type):
                continue

            name = asset.get("name", "")

            if name in seen:
                continue

            seen.add(name)

            tags = self._find_tags(
                name,
                dataplex_tags,
            )

            inventory.append({
                "asset_name": name,
                "asset_type": asset_type,
                "project_id": asset.get("project", ""),
                "location": asset.get("location", ""),
                "owner": self._extract_owner(
                    tags,
                    asset,
                ),
                "classification": self._extract_classification(
                    tags
                ),
                "business_context": self._extract_business_context(
                    tags
                ),
                "last_review_date": self._extract_last_review(
                    tags
                ),
                "sensitive": self._is_sensitive(tags),
            })

        for asset in dataplex_assets:
            name = asset.get("name", "")

            if name in seen:
                continue

            seen.add(name)

            inventory.append({
                "asset_name": name,
                "asset_type": asset.get(
                    "asset_type",
                    "",
                ),
                "project_id": asset.get(
                    "project_id",
                    "",
                ),
                "location": asset.get(
                    "location",
                    "",
                ),
                "owner": asset.get(
                    "owner",
                    "",
                ),
                "classification": asset.get(
                    "classification",
                    "",
                ),
                "business_context": asset.get(
                    "business_context",
                    "",
                ),
                "last_review_date": asset.get(
                    "last_review_date",
                    "",
                ),
                "sensitive": asset.get(
                    "sensitive",
                    False,
                ),
            })

        return inventory

    def _extract_data_owners(
        self,
        dataplex_assets,
        dataplex_tags,
    ):
        owners = []

        for asset in dataplex_assets:
            owner = asset.get("owner", "")

            if owner:
                owners.append({
                    "asset": asset.get("name", ""),
                    "owner": owner,
                })

        for tag in dataplex_tags:
            owner = tag.get("owner", "")

            if owner:
                owners.append({
                    "asset": tag.get("asset", ""),
                    "owner": owner,
                })

        return owners

    def _validate_data_inventory(self, inventory):
        if not inventory:
            return False

        required = [
            "asset_name",
            "asset_type",
            "project_id",
            "location",
            "owner",
            "classification",
            "business_context",
            "last_review_date",
        ]

        return all(
            all(item.get(field) for field in required)
            for item in inventory
        )

    # =========================================================
    # 3.2 / 3.7 – Sensitive Data and Classification
    # =========================================================

    def _extract_sensitive_data_inventory(
        self,
        findings,
        inventory,
    ):
        results = []

        inventory_by_name = {
            item.get("asset_name")
            for item in inventory
        }

        for finding in findings:
            resource = finding.get(
                "resource",
                finding.get("resourceName", ""),
            )

            results.append({
                "resource": resource,
                "info_type": finding.get(
                    "infoType",
                    "",
                ),
                "severity": finding.get(
                    "severity",
                    "",
                ),
                "timestamp": finding.get(
                    "timestamp",
                    finding.get("eventTime", ""),
                ),
                "inventory_entry_exists": (
                    resource in inventory_by_name
                ),
            })

        return results

    def _build_classification_records(
        self,
        dataplex_tags,
        bigquery_tables,
        dlp_findings,
    ):
        records = []

        for tag in dataplex_tags:
            classification = tag.get(
                "classification",
                tag.get("value", ""),
            )

            if classification:
                records.append({
                    "asset": tag.get("asset", ""),
                    "classification": classification,
                    "source": "DATAPLEX",
                })

        for table in bigquery_tables:
            policy_tags = table.get(
                "policyTags",
                [],
            )

            for policy_tag in policy_tags:
                records.append({
                    "asset": table.get("name", ""),
                    "classification": policy_tag,
                    "source": "BIGQUERY_POLICY_TAG",
                })

        for finding in dlp_findings:
            records.append({
                "asset": finding.get("resource", ""),
                "classification": finding.get(
                    "infoType",
                    "",
                ),
                "source": "CLOUD_DLP",
            })

        return records

    def _classification_coverage(
        self,
        classified,
        inventory,
    ):
        if not inventory:
            return 0

        classified_assets = {
            record.get("asset")
            for record in classified
            if record.get("asset")
        }

        inventory_assets = {
            item.get("asset_name")
            for item in inventory
        }

        return round(
            (
                len(
                    classified_assets.intersection(
                        inventory_assets
                    )
                )
                / len(inventory)
            )
            * 100,
            2,
        )

    def _classification_coverage_verified(
        self,
        classified,
        inventory,
    ):
        return (
            bool(inventory)
            and self._classification_coverage(
                classified,
                inventory,
            )
            > 0
        )

    # =========================================================
    # 3.3 – Access Control
    # =========================================================

    def _build_access_records(
        self,
        iam_policies,
        storage_buckets,
        bigquery_datasets,
        bigquery_tables,
        cloudsql_instances,
    ):
        records = []

        for policy in iam_policies:
            for binding in policy.get("bindings", []):
                role = binding.get("role", "")

                for member in binding.get("members", []):
                    records.append({
                        "resource": policy.get(
                            "resource",
                            "",
                        ),
                        "principal": member,
                        "role": role,
                        "group_based": member.startswith(
                            "group:"
                        ),
                        "public": member in {
                            "allUsers",
                            "allAuthenticatedUsers",
                        },
                    })

        for resource in (
            storage_buckets
            + bigquery_datasets
            + bigquery_tables
            + cloudsql_instances
        ):
            records.extend(
                self._resource_iam_records(resource)
            )

        return records

    def _resource_iam_records(self, resource):
        records = []

        for binding in resource.get(
            "iam_bindings",
            [],
        ):
            for member in binding.get(
                "members",
                [],
            ):
                records.append({
                    "resource": resource.get(
                        "name",
                        "",
                    ),
                    "principal": member,
                    "role": binding.get(
                        "role",
                        "",
                    ),
                    "group_based": member.startswith(
                        "group:"
                    ),
                    "public": member in {
                        "allUsers",
                        "allAuthenticatedUsers",
                    },
                })

        return records

    def _filter_sensitive_access(
        self,
        records,
        sensitive_inventory,
    ):
        sensitive_resources = {
            item.get("resource")
            for item in sensitive_inventory
        }

        return [
            record
            for record in records
            if record.get("resource")
            in sensitive_resources
        ]

    def _need_to_know_enforced(self, records):
        if not records:
            return False

        return not any(
            record.get("public")
            for record in records
        )

    def _group_based_access(self, records):
        if not records:
            return False

        return any(
            record.get("group_based")
            for record in records
        )

    def _public_access_prevented(
        self,
        buckets,
        policies,
    ):
        for bucket in buckets:
            if bucket.get("public_access", False):
                return False

        for policy in policies:
            for binding in policy.get(
                "bindings",
                [],
            ):
                members = binding.get(
                    "members",
                    [],
                )

                if (
                    "allUsers" in members
                    or "allAuthenticatedUsers" in members
                ):
                    return False

        return True

    # =========================================================
    # 3.4 – Retention
    # =========================================================

    def _build_retention_records(
        self,
        buckets,
        datasets,
        tables,
        sql_instances,
    ):
        records = []

        for bucket in buckets:
            retention_policy = bucket.get(
                "retentionPolicy",
                {},
            )

            records.append({
                "resource": bucket.get(
                    "name",
                    "",
                ),
                "resource_type": "CLOUD_STORAGE",
                "retention_seconds": retention_policy.get(
                    "retentionPeriod",
                    0,
                ),
                "bucket_lock": retention_policy.get(
                    "isLocked",
                    False,
                ),
                "holds": bucket.get(
                    "holds",
                    [],
                ),
            })

        for table in tables:
            records.append({
                "resource": table.get(
                    "name",
                    "",
                ),
                "resource_type": "BIGQUERY",
                "expiration": table.get(
                    "expirationTime",
                    "",
                ),
                "partition_expiration": table.get(
                    "partitionExpirationMs",
                    "",
                ),
            })

        for instance in sql_instances:
            records.append({
                "resource": instance.get(
                    "name",
                    "",
                ),
                "resource_type": "CLOUD_SQL",
                "backup_retention": instance.get(
                    "backup_retention",
                    "",
                ),
                "point_in_time_recovery": instance.get(
                    "point_in_time_recovery",
                    False,
                ),
            })

        return records

    def _retention_alignment_verified(
        self,
        records,
        config,
    ):
        if not records:
            return False

        return config.get(
            "retention_configuration_aligned",
            False,
        )

    def _bucket_lock_evidence(self, buckets):
        return [
            {
                "bucket": bucket.get(
                    "name",
                    "",
                ),
                "locked": bucket.get(
                    "retentionPolicy",
                    {},
                ).get(
                    "isLocked",
                    False,
                ),
            }
            for bucket in buckets
        ]

    def _bigquery_expiration_evidence(self, tables):
        return [
            {
                "table": table.get(
                    "name",
                    "",
                ),
                "expiration": table.get(
                    "expirationTime",
                    "",
                ),
                "partition_expiration": table.get(
                    "partitionExpirationMs",
                    "",
                ),
            }
            for table in tables
        ]

    def _cloudsql_retention_evidence(self, instances):
        return [
            {
                "instance": instance.get(
                    "name",
                    "",
                ),
                "backup_retention": instance.get(
                    "backup_retention",
                    "",
                ),
                "pitr": instance.get(
                    "point_in_time_recovery",
                    False,
                ),
            }
            for instance in instances
        ]

    # =========================================================
    # 3.5 – Disposal
    # =========================================================

    def _build_disposal_evidence(
        self,
        disposal_records,
        audit_logs,
    ):
        results = []

        for record in disposal_records:
            results.append({
                "resource": record.get(
                    "resource",
                    "",
                ),
                "action": record.get(
                    "action",
                    "",
                ),
                "timestamp": record.get(
                    "timestamp",
                    "",
                ),
                "completed": record.get(
                    "completed",
                    False,
                ),
                "ticket": record.get(
                    "ticket",
                    "",
                ),
            })

        for log in audit_logs:
            method = log.get(
                "methodName",
                "",
            ).lower()

            if "delete" in method or "destroy" in method:
                results.append({
                    "resource": log.get(
                        "resourceName",
                        "",
                    ),
                    "action": method,
                    "timestamp": log.get(
                        "timestamp",
                        "",
                    ),
                    "completed": True,
                    "ticket": "",
                })

        return results

    # =========================================================
    # 3.6 – Endpoint Encryption
    # =========================================================

    def _endpoint_encryption_enforced(self, endpoints):
        if not endpoints:
            return False

        return all(
            endpoint.get(
                "encryption_enabled",
                False,
            )
            for endpoint in endpoints
        )

    # =========================================================
    # 3.8 – Data Flows
    # =========================================================

    def _build_data_flow_records(
        self,
        documents,
        validation,
        lineage,
        cai_assets,
    ):
        records = []

        for document in documents:
            records.append({
                "document": document.get(
                    "name",
                    "",
                ),
                "version": document.get(
                    "version",
                    "",
                ),
                "owner": document.get(
                    "owner",
                    "",
                ),
                "last_updated": document.get(
                    "last_updated",
                    "",
                ),
                "referenced_resources": document.get(
                    "resources",
                    [],
                ),
                "validation": False,
            })

        for item in validation:
            records.append({
                "document": item.get(
                    "document",
                    "",
                ),
                "version": item.get(
                    "version",
                    "",
                ),
                "owner": item.get(
                    "owner",
                    "",
                ),
                "last_updated": item.get(
                    "timestamp",
                    "",
                ),
                "referenced_resources": item.get(
                    "resources",
                    [],
                ),
                "validation": True,
            })

        for item in lineage:
            records.append({
                "document": "",
                "version": "",
                "owner": "",
                "last_updated": item.get(
                    "timestamp",
                    "",
                ),
                "referenced_resources": item.get(
                    "resources",
                    [],
                ),
                "validation": True,
            })

        return records

    def _data_flow_resources_linked(
        self,
        records,
        cai_assets,
    ):
        if not records or not cai_assets:
            return False

        known_resources = {
            asset.get("name")
            for asset in cai_assets
        }

        return any(
            resource in known_resources
            for record in records
            for resource in record.get(
                "referenced_resources",
                [],
            )
        )

    # =========================================================
    # 3.10 – TLS
    # =========================================================

    def _build_tls_records(
        self,
        load_balancers,
        certificates,
    ):
        records = []

        certificate_names = {
            cert.get("name", "")
            for cert in certificates
        }

        for load_balancer in load_balancers:
            for listener in load_balancer.get(
                "listeners",
                [],
            ):
                certificate = listener.get(
                    "certificate",
                    "",
                )

                records.append({
                    "load_balancer": load_balancer.get(
                        "name",
                        "",
                    ),
                    "protocol": listener.get(
                        "protocol",
                        "",
                    ),
                    "port": listener.get(
                        "port",
                        "",
                    ),
                    "certificate": certificate,
                    "certificate_valid": (
                        certificate in certificate_names
                    ),
                    "redirect_http": listener.get(
                        "redirect_http",
                        False,
                    ),
                })

        return records

    def _http_redirect_or_block_configured(
        self,
        load_balancers,
    ):
        return any(
            listener.get("redirect_http", False)
            for load_balancer in load_balancers
            for listener in load_balancer.get(
                "listeners",
                [],
            )
        )

    def _plaintext_endpoints(self, load_balancers):
        results = []

        for load_balancer in load_balancers:
            for listener in load_balancer.get(
                "listeners",
                [],
            ):
                protocol = listener.get(
                    "protocol",
                    "",
                ).upper()

                if protocol in {"HTTP", "TCP"}:
                    results.append({
                        "load_balancer": load_balancer.get(
                            "name",
                            "",
                        ),
                        "protocol": protocol,
                        "port": listener.get(
                            "port",
                            "",
                        ),
                    })

        return results

    def _tls_enforcement_verified(self, records):
        if not records:
            return False

        return not any(
            record.get(
                "protocol",
                "",
            ).upper() == "HTTP"
            and not record.get(
                "redirect_http",
                False,
            )
            for record in records
        )

    # =========================================================
    # 3.11 – Encryption at Rest / KMS
    # =========================================================

    def _build_encryption_at_rest_records(
        self,
        buckets,
        datasets,
        tables,
        sql_instances,
        kms_keys,
    ):
        records = []

        for bucket in buckets:
            records.append({
                "resource": bucket.get(
                    "name",
                    "",
                ),
                "resource_type": "CLOUD_STORAGE",
                "encrypted": True,
                "kms_key": bucket.get(
                    "kmsKeyName",
                    "",
                ),
            })

        for dataset in datasets:
            records.append({
                "resource": dataset.get(
                    "name",
                    "",
                ),
                "resource_type": "BIGQUERY",
                "encrypted": True,
                "kms_key": dataset.get(
                    "defaultEncryptionConfiguration",
                    {},
                ).get(
                    "kmsKeyName",
                    "",
                ),
            })

        for table in tables:
            records.append({
                "resource": table.get(
                    "name",
                    "",
                ),
                "resource_type": "BIGQUERY_TABLE",
                "encrypted": True,
                "kms_key": table.get(
                    "kmsKeyName",
                    "",
                ),
            })

        for instance in sql_instances:
            records.append({
                "resource": instance.get(
                    "name",
                    "",
                ),
                "resource_type": "CLOUD_SQL",
                "encrypted": instance.get(
                    "encryption_enabled",
                    True,
                ),
                "kms_key": instance.get(
                    "kms_key",
                    "",
                ),
            })

        return records

    def _encryption_at_rest_enabled(self, records):
        if not records:
            return False

        return all(
            record.get(
                "encrypted",
                False,
            )
            for record in records
        )

    def _sensitive_resources_key_bound(self, records):
        return any(
            record.get("kms_key")
            for record in records
        )

    def _key_rotation_enabled(self, keys):
        if not keys:
            return False

        return all(
            key.get("rotation_period")
            not in {None, "", 0}
            for key in keys
        )

    def _key_access_controlled(self, keys):
        if not keys:
            return False

        return all(
            bool(key.get("iam_bindings"))
            for key in keys
        )

    def _key_access_logging_enabled(self, logs):
        return any(
            (
                "cloudkms"
                in log.get(
                    "serviceName",
                    "",
                ).lower()
            )
            or
            (
                "crypto"
                in log.get(
                    "methodName",
                    "",
                ).lower()
            )
            for log in logs
        )

    # =========================================================
    # 3.12 – Segmentation
    # =========================================================

    def _build_segmentation_records(
        self,
        policies,
        vpc_service_controls,
        iam_policies,
        cross_tier_access,
    ):
        records = []

        for policy in policies:
            records.append({
                "tier": policy.get(
                    "tier",
                    "",
                ),
                "projects": policy.get(
                    "projects",
                    [],
                ),
                "folders": policy.get(
                    "folders",
                    [],
                ),
                "networks": policy.get(
                    "networks",
                    [],
                ),
                "restricted_services": policy.get(
                    "restricted_services",
                    [],
                ),
            })

        for perimeter in vpc_service_controls:
            records.append({
                "tier": perimeter.get(
                    "tier",
                    "",
                ),
                "projects": perimeter.get(
                    "projects",
                    [],
                ),
                "folders": perimeter.get(
                    "folders",
                    [],
                ),
                "networks": perimeter.get(
                    "networks",
                    [],
                ),
                "restricted_services": perimeter.get(
                    "restricted_services",
                    [],
                ),
            })

        return records

    def _tier_resource_placement_verified(self, records):
        return bool(
            records
            and any(
                record.get("projects")
                or record.get("folders")
                for record in records
            )
        )

    def _restricted_services_configured(
        self,
        perimeters,
    ):
        return any(
            perimeter.get("restricted_services")
            for perimeter in perimeters
        )

    def _tier_iam_separation(self, policies):
        tier_groups = set()

        for policy in policies:
            for binding in policy.get(
                "bindings",
                [],
            ):
                for member in binding.get(
                    "members",
                    [],
                ):
                    if member.startswith("group:"):
                        tier_groups.add(member)

        return len(tier_groups) > 1

    def _cross_tier_access_controlled(self, records):
        if not records:
            return False

        return all(
            record.get(
                "approved",
                False,
            )
            for record in records
        )

    def _cross_tier_access_auditable(self, records):
        if not records:
            return False

        return all(
            record.get("audit_record")
            for record in records
        )

    # =========================================================
    # 3.13 – DLP
    # =========================================================

    def _build_dlp_records(
        self,
        templates,
        jobs,
        findings,
        remediation,
    ):
        records = []

        for template in templates:
            records.append({
                "template": template.get(
                    "name",
                    "",
                ),
                "detectors": template.get(
                    "detectors",
                    [],
                ),
                "scope": template.get(
                    "scope",
                    [],
                ),
                "exclusions": template.get(
                    "exclusions",
                    [],
                ),
            })

        for job in jobs:
            records.append({
                "job": job.get(
                    "name",
                    "",
                ),
                "scope": job.get(
                    "scope",
                    [],
                ),
                "last_run": job.get(
                    "lastRun",
                    "",
                ),
                "status": job.get(
                    "status",
                    "",
                ),
            })

        return records

    def _dlp_scope_defined(self, jobs):
        return any(
            job.get("scope")
            for job in jobs
        )

    def _dlp_inventory_updates(
        self,
        findings,
        inventory,
    ):
        inventory_names = {
            item.get("asset_name")
            for item in inventory
        }

        return [
            finding
            for finding in findings
            if (
                finding.get("resource")
                in inventory_names
                or finding.get("resourceName")
                in inventory_names
            )
        ]

    def _dlp_coverage(self, jobs):
        return [
            {
                "job": job.get(
                    "name",
                    "",
                ),
                "scope": job.get(
                    "scope",
                    [],
                ),
                "last_run": job.get(
                    "lastRun",
                    "",
                ),
                "status": job.get(
                    "status",
                    "",
                ),
            }
            for job in jobs
        ]

    def _remediation_verified(self, records):
        if not records:
            return False

        return any(
            record.get("closed")
            or record.get("status") in {
                "CLOSED",
                "RESOLVED",
                "COMPLETE",
            }
            for record in records
        )

    # =========================================================
    # 3.14 – Data Access Logging
    # =========================================================

    def _build_data_access_records(
        self,
        logs,
        sensitive_inventory,
    ):
        sensitive_resources = {
            item.get("resource")
            for item in sensitive_inventory
        }

        records = []

        for log in logs:
            resource = log.get(
                "resourceName",
                log.get("resource", ""),
            )

            records.append({
                "principal": log.get(
                    "principalEmail",
                    log.get("principal", ""),
                ),
                "resource": resource,
                "action": log.get(
                    "methodName",
                    "",
                ),
                "timestamp": log.get(
                    "timestamp",
                    "",
                ),
                "source_ip": log.get(
                    "sourceIp",
                    "",
                ),
                "sensitive": resource in sensitive_resources,
            })

        return records

    def _sensitive_access_logging_enabled(
        self,
        logs,
        sensitive_inventory,
    ):
        if not logs or not sensitive_inventory:
            return False

        sensitive_resources = {
            item.get("resource")
            for item in sensitive_inventory
        }

        return any(
            log.get(
                "resourceName",
                log.get("resource", ""),
            )
            in sensitive_resources
            for log in logs
        )

    def _centralized_logging_enabled(self, sinks):
        return any(
            sink.get("destination")
            for sink in sinks
        )

    def _log_retention_configured(self, sinks):
        return any(
            sink.get("retention_days") is not None
            for sink in sinks
        )

    def _principal_traceability(self, records):
        return any(
            record.get("principal")
            and record.get("resource")
            and record.get("action")
            and record.get("timestamp")
            for record in records
        )

    def _high_risk_access_detection(self, logs):
        return any(
            log.get("high_risk", False)
            for log in logs
        )

    def _access_alert_or_investigation(
        self,
        logs,
        remediation,
    ):
        return (
            any(
                log.get("alert", False)
                or log.get("investigated", False)
                for log in logs
            )
            or
            any(
                record.get(
                    "security_investigation",
                    False,
                )
                for record in remediation
            )
        )

    # =========================================================
    # General Helpers
    # =========================================================

    def _is_data_asset(self, asset_type):
        data_types = {
            "storage.googleapis.com/Bucket",
            "bigquery.googleapis.com/Dataset",
            "bigquery.googleapis.com/Table",
            "sqladmin.googleapis.com/Instance",
        }

        return asset_type in data_types

    def _find_tags(
        self,
        asset_name,
        tags,
    ):
        return [
            tag
            for tag in tags
            if tag.get("asset") == asset_name
        ]

    def _extract_owner(
        self,
        tags,
        asset,
    ):
        for tag in tags:
            if tag.get("owner"):
                return tag.get("owner")

        return asset.get("owner", "")

    def _extract_classification(self, tags):
        for tag in tags:
            if tag.get("classification"):
                return tag.get("classification")

        return ""

    def _extract_business_context(self, tags):
        for tag in tags:
            if tag.get("business_context"):
                return tag.get("business_context")

        return ""

    def _extract_last_review(self, tags):
        for tag in tags:
            if tag.get("last_review_date"):
                return tag.get("last_review_date")

        return ""

    def _is_sensitive(self, tags):
        sensitive_classifications = {
            "SENSITIVE",
            "CONFIDENTIAL",
            "RESTRICTED",
            "HIGH",
        }

        return any(
            str(
                tag.get(
                    "classification",
                    "",
                )
            ).upper()
            in sensitive_classifications
            for tag in tags
        )

    def _exceptions_managed(self, exceptions):
        if not exceptions:
            return True

        return all(
            exception.get("approved", False)
            and exception.get("expiry")
            for exception in exceptions
        )

    def _review_verified(
        self,
        records,
        max_age_days,
    ):
        if not records:
            return False

        cutoff = (
            datetime.utcnow()
            - timedelta(days=max_age_days)
        )

        for record in records:
            timestamp = (
                record.get("timestamp")
                or record.get("review_date")
                or record.get("last_review")
            )

            if not timestamp:
                continue

            try:
                parsed = datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if parsed.tzinfo is not None:
                    parsed = parsed.replace(
                        tzinfo=None
                    )

                if parsed >= cutoff:
                    return True

            except (
                ValueError,
                TypeError,
            ):
                continue

        return False

    def _recent_execution_verified(
        self,
        jobs,
        max_age_days,
    ):
        cutoff = (
            datetime.utcnow()
            - timedelta(days=max_age_days)
        )

        for job in jobs:
            timestamp = job.get("lastRun")

            if not timestamp:
                continue

            try:
                parsed = datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )

                if parsed.tzinfo is not None:
                    parsed = parsed.replace(
                        tzinfo=None
                    )

                if (
                    parsed >= cutoff
                    and job.get("status")
                    in {
                        "SUCCESS",
                        "SUCCEEDED",
                        "COMPLETED",
                    }
                ):
                    return True

            except (
                ValueError,
                TypeError,
            ):
                continue

        return False

    def _latest_timestamp(self, records):
        parsed_timestamps = []

        for record in records:
            timestamp = (
                record.get("timestamp")
                or record.get("review_date")
                or record.get("last_review")
            )

            if not timestamp:
                continue

            try:
                parsed = datetime.fromisoformat(
                    timestamp.replace(
                        "Z",
                        "+00:00",
                    )
                )

                parsed_timestamps.append(
                    (parsed, timestamp)
                )

            except (
                ValueError,
                TypeError,
            ):
                continue

        if not parsed_timestamps:
            return ""

        return max(
            parsed_timestamps,
            key=lambda item: item[0],
        )[1]

    def _bulk_export_monitoring(self, logs):
        return [
            log
            for log in logs
            if (
                log.get("bulk_export", False)
                or "export"
                in log.get(
                    "methodName",
                    "",
                ).lower()
            )
        ]

    def _review_history(self, records):
        return [
            {
                "timestamp": record.get(
                    "timestamp",
                    record.get(
                        "review_date",
                        "",
                    ),
                ),
                "status": record.get(
                    "status",
                    "",
                ),
                "reviewer": record.get(
                    "reviewer",
                    "",
                ),
            }
            for record in records
        ]

    def _build_review_history(
        self,
        review_records,
        scheduled_jobs,
        classification_reviews,
        access_reviews,
    ):
        results = []

        results.extend(
            self._review_history(
                review_records
            )
        )

        results.extend(
            self._review_history(
                classification_reviews
            )
        )

        results.extend(
            self._review_history(
                access_reviews
            )
        )

        for job in scheduled_jobs:
            if job.get("lastRun"):
                results.append({
                    "timestamp": job.get(
                        "lastRun"
                    ),
                    "status": job.get(
                        "status",
                        "",
                    ),
                    "reviewer": "",
                })

        return results