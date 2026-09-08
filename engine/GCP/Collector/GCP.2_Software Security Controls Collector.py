"""
GCP Software Security Controls Collector

Covers CIS GCP Foundations (mapped):
    2.1 – Establish and Maintain a Software Inventory
    2.2 – Ensure Authorized Software is Currently Supported
    2.3 – Address Unauthorized Software
    2.4 – Utilize Automated Software Inventory Tools
    2.5 – Allowlist Authorized Software
    2.6 – Allowlist Authorized Libraries
    2.7 – Allowlist Authorized Scripts

Connection Methods:
    - Cloud Asset Inventory API
    - OS Config / VM Manager API
    - Artifact Registry API
    - Binary Authorization API
    - Cloud Build API
    - Cloud Logging API
    - BigQuery inventory exports

Required Permissions:
    - roles/cloudasset.viewer
    - roles/osconfig.inventoryViewer
    - roles/artifactregistry.reader
    - roles/binaryauthorization.policyViewer
    - roles/logging.viewer
    - roles/cloudbuild.viewer
"""

from typing import Any
from datetime import datetime, timedelta

from collectors.base import BaseDataCollector
from collectors.gcp_client import GCPClient


class GcpSoftwareSecurityControlsCollector(BaseDataCollector):
    """Collects Software Management data required for CIS 2.x controls."""

    async def collect(self, client: GCPClient) -> dict[str, Any]:
        """Main collection entry point."""

        # ---------------------------
        # Core Data Sources
        # ---------------------------

        cai_assets = await client.get_cloud_asset_inventory()

        vm_inventory = await client.get_os_inventory()

        artifact_images = await client.get_artifact_registry_images()

        binary_policies = await client.get_binary_authorization_policies()

        attestations = await client.get_binary_authorization_attestations()

        cloud_builds = await client.get_cloud_build_history()

        build_logs = await client.get_cloud_build_logs()

        os_policies = await client.get_os_policy_assignments()

        security_logs = await client.get_security_logs()

        scheduled_jobs = await client.get_scheduled_jobs()

        tickets = await client.get_security_tickets()


        # ---------------------------
        # Derived Signals
        # ---------------------------

        software_inventory = self._build_software_inventory(
            vm_inventory,
            artifact_images
        )

        unsupported_software = self._identify_unsupported_software(
            software_inventory,
            client.config
        )

        unauthorized_software = self._identify_unauthorized_software(
            software_inventory,
            client.config
        )

        inventory_exports = self._extract_inventory_exports(
            scheduled_jobs
        )

        blocked_deployments = self._extract_blocked_deployments(
            security_logs
        )

        script_events = self._extract_script_events(
            security_logs
        )

        library_events = self._extract_library_events(
            build_logs
        )

        review_history = self._extract_review_history(
            scheduled_jobs
        )


        # ---------------------------
        # Flags / Control Signals
        # ---------------------------

        data = {

            # ---------------------------
            # 2.1 Software Inventory
            # ---------------------------

            "software_inventory_exists":
                bool(software_inventory),

            "software_inventory_scope_defined":
                client.config.get(
                    "software_inventory_scope_defined",
                    False
                ),

            "software_inventory":
                software_inventory,

            "required_software_fields_present":
                self._validate_inventory_fields(
                    software_inventory
                ),

            "inventory_export_available":
                bool(inventory_exports),

            "review_schedule_defined":
                client.config.get(
                    "software_review_schedule",
                    False
                ),

            "review_execution_verified":
                bool(review_history),

            "review_frequency_days":
                client.config.get(
                    "software_review_frequency_days",
                    180
                ),

            "last_review_timestamp":
                self._latest_timestamp(
                    review_history
                ),



            # ---------------------------
            # 2.2 Supported Software
            # ---------------------------

            "support_status_tracked":
                client.config.get(
                    "software_support_tracking",
                    False
                ),

            "unsupported_software":
                unsupported_software,

            "unsupported_exception_register":
                self._extract_exceptions(
                    tickets,
                    "unsupported"
                ),

            "monthly_support_review":
                self._monthly_review_verified(
                    review_history
                ),



            # ---------------------------
            # 2.3 Unauthorized Software
            # ---------------------------

            "authorized_software_baseline_defined":
                client.config.get(
                    "authorized_software_baseline",
                    False
                ),

            "unauthorized_software":
                unauthorized_software,

            "unauthorized_detection_enabled":
                bool(
                    unauthorized_software
                ),

            "remediation_actions":
                self._extract_remediation_actions(
                    tickets
                ),

            "monthly_review_verified":
                self._monthly_review_verified(
                    review_history
                ),



            # ---------------------------
            # 2.4 Automated Inventory
            # ---------------------------

            "automated_inventory_enabled":
                client.config.get(
                    "os_inventory_enabled",
                    False
                ),

            "agent_coverage_verified":
                self._validate_agent_coverage(
                    vm_inventory
                ),

            "automated_exports_available":
                bool(
                    inventory_exports
                ),

            "inventory_run_history":
                review_history,



            # ---------------------------
            # 2.5 Software Allowlisting
            # ---------------------------

            "software_allowlist_enabled":
                client.config.get(
                    "software_allowlist_enabled",
                    False
                ),

            "allowlist_scope_defined":
                client.config.get(
                    "allowlist_scope_defined",
                    False
                ),

            "binary_authorization_enabled":
                bool(
                    binary_policies
                ),

            "binary_authorization_mode":
                self._get_binary_mode(
                    binary_policies
                ),

            "attestors":
                attestations,

            "blocked_deployments":
                blocked_deployments,



            # ---------------------------
            # 2.6 Library Allowlisting
            # ---------------------------

            "library_policy_defined":
                client.config.get(
                    "library_policy_defined",
                    False
                ),

            "approved_libraries":
                self._extract_libraries(
                    software_inventory
                ),

            "sbom_validation_enabled":
                client.config.get(
                    "sbom_validation",
                    False
                ),

            "dependency_policy_enabled":
                client.config.get(
                    "dependency_policy",
                    False
                ),

            "failed_dependency_builds":
                library_events,

            "library_exceptions":
                self._extract_exceptions(
                    tickets,
                    "library"
                ),



            # ---------------------------
            # 2.7 Script Allowlisting
            # ---------------------------

            "script_allowlist_defined":
                client.config.get(
                    "script_allowlist",
                    False
                ),

            "authorized_scripts":
                self._extract_scripts(
                    software_inventory
                ),

            "script_scope_defined":
                client.config.get(
                    "script_scope_defined",
                    False
                ),

            "os_policy_enabled":
                bool(
                    os_policies
                ),

            "os_policy_enforcement_mode":
                self._get_os_policy_mode(
                    os_policies
                ),

            "blocked_script_events":
                script_events,

            "script_exceptions":
                self._extract_exceptions(
                    tickets,
                    "script"
                ),



            # ---------------------------
            # General Evidence
            # ---------------------------

            "collection_timestamp":
                datetime.utcnow().isoformat()

        }

        return data


    # =========================================================
    # Extraction Logic
    # =========================================================

    def _build_software_inventory(
        self,
        vm_inventory,
        images
    ):
        inventory = []

        for vm in vm_inventory:
            for package in vm.get(
                "packages",
                []
            ):
                inventory.append({
                    "title":
                        package.get(
                            "name"
                        ),

                    "publisher":
                        package.get(
                            "publisher",
                            "unknown"
                        ),

                    "version":
                        package.get(
                            "version"
                        ),

                    "asset":
                        vm.get(
                            "instance"
                        ),

                    "install_date":
                        package.get(
                            "installDate"
                        ),

                    "source":
                        "OS Config"
                })

        for image in images:
            inventory.append({
                "title":
                    image.get(
                        "name"
                    ),

                "version":
                    image.get(
                        "digest"
                    ),

                "publisher":
                    "Artifact Registry",

                "source":
                    "container"
            })

        return inventory


    def _validate_inventory_fields(
        self,
        inventory
    ):
        required = [
            "title",
            "version",
            "publisher"
        ]

        return all(
            all(
                item.get(field)
                for field in required
            )
            for item in inventory
        )


    def _identify_unsupported_software(
        self,
        inventory,
        config
    ):
        return [
            item
            for item in inventory
            if item.get(
                "title"
            ) in config.get(
                "unsupported_products",
                []
            )
        ]


    def _identify_unauthorized_software(
        self,
        inventory,
        config
    ):
        allowed = config.get(
            "authorized_software",
            []
        )

        return [
            item
            for item in inventory
            if item.get(
                "title"
            ) not in allowed
        ]


    def _extract_inventory_exports(
        self,
        jobs
    ):
        return [
            job
            for job in jobs
            if "inventory"
            in job.get(
                "name",
                ""
            ).lower()
        ]


    def _extract_remediation_actions(
        self,
        tickets
    ):
        return [
            {
                "ticket":
                    t.get(
                        "id"
                    ),

                "action":
                    t.get(
                        "resolution"
                    ),

                "timestamp":
                    t.get(
                        "closed"
                    )
            }
            for t in tickets
        ]


    def _extract_blocked_deployments(
        self,
        logs
    ):
        return [
            log
            for log in logs
            if "DENIED"
            in log.get(
                "status",
                ""
            )
        ]


    def _extract_script_events(
        self,
        logs
    ):
        return [
            log
            for log in logs
            if "script"
            in log.get(
                "message",
                ""
            ).lower()
        ]


    def _extract_library_events(
        self,
        logs
    ):
        return [
            log
            for log in logs
            if "dependency"
            in log.get(
                "message",
                ""
            ).lower()
        ]


    def _extract_libraries(
        self,
        inventory
    ):
        return [
            item
            for item in inventory
            if item.get(
                "source"
            ) == "container"
        ]


    def _extract_scripts(
        self,
        inventory
    ):
        return [
            item
            for item in inventory
            if item.get(
                "title",
                ""
            ).endswith(
                (
                    ".py",
                    ".ps1"
                )
            )
        ]


    def _extract_exceptions(
        self,
        tickets,
        category
    ):
        return [
            ticket
            for ticket in tickets
            if category
            in ticket.get(
                "category",
                ""
            ).lower()
        ]


    def _validate_agent_coverage(
        self,
        inventory
    ):
        return len(
            inventory
        ) > 0


    def _get_binary_mode(
        self,
        policies
    ):
        if not policies:
            return ""

        return policies[0].get(
            "mode",
            ""
        )


    def _get_os_policy_mode(
        self,
        policies
    ):
        if not policies:
            return ""

        return policies[0].get(
            "mode",
            ""
        )


    def _monthly_review_verified(
        self,
        reviews
    ):
        cutoff = datetime.utcnow() - timedelta(days=31)

        for review in reviews:
            timestamp = review.get(
                "timestamp"
            )

            if timestamp:
                return True

        return False


    def _extract_review_history(
        self,
        jobs
    ):
        return [
            {
                "job":
                    job.get(
                        "name"
                    ),

                "timestamp":
                    job.get(
                        "lastRun"
                    ),

                "status":
                    job.get(
                        "status"
                    )
            }
            for job in jobs
        ]


    def _latest_timestamp(
        self,
        records
    ):
        if not records:
            return ""

        return records[-1].get(
            "timestamp",
            ""
        )
		