"""
GCP Device Asset Management Controls Collector

Covers CIS GCP Foundations (mapped):
    1.1 – Establish and Maintain Enterprise Asset Inventory
    1.2 – Address Unauthorized Assets
    1.3 – Utilize an Active Discovery Tool
    1.4 – Use DHCP Logging to Update Enterprise Asset Inventory
    1.5 – Use a Passive Asset Discovery Tool

Connection Methods:
    - Cloud Asset Inventory API
    - Security Command Center API
    - Cloud Logging API
    - BigQuery scheduled queries
    - VPC Flow Logs
    - Packet Mirroring
    - OS Config (where applicable)

Required Permissions:
    - roles/cloudasset.viewer
    - roles/securitycenter.assetsViewer
    - roles/logging.viewer
    - roles/bigquery.metadataViewer
    - roles/compute.viewer
"""

from typing import Any
from datetime import datetime, timedelta, timezone

from collectors.base import BaseDataCollector
from collectors.gcp_client import GCPClient


class GcpDeviceAssetControlsCollector(BaseDataCollector):
    """Collects Device Asset Management data required for CIS 1.x controls."""

    async def collect(self, client: GCPClient) -> dict[str, Any]:
        """Main collection entry point."""

        # ---------------------------
        # Core Data Sources
        # ---------------------------

        cai_assets = await client.get_cloud_asset_inventory()
        scc_assets = await client.get_scc_assets()
        scc_findings = await client.get_scc_findings()

        flow_logs = await client.get_vpc_flow_logs()
        packet_mirroring = await client.get_packet_mirroring()

        dhcp_logs = await client.get_dhcp_logs()

        discovery_jobs = await client.get_scheduled_jobs()
        tickets = await client.get_security_tickets()

        # ---------------------------
        # Derived Signals
        # ---------------------------

        asset_inventory = self._build_asset_inventory(
            cai_assets
        )

        unauthorized_assets = self._extract_unauthorized_assets(
            scc_findings,
            cai_assets
        )

        active_discovery_results = self._extract_active_discovery(
            flow_logs,
            discovery_jobs
        )

        dhcp_events = self._extract_dhcp_events(
            dhcp_logs
        )

        passive_discovery_results = self._extract_passive_discovery(
            flow_logs,
            packet_mirroring
        )

        remediation_actions = self._extract_remediation_actions(
            tickets
        )

        review_history = self._extract_review_history(
            discovery_jobs
        )

        # ---------------------------
        # Flags / Control Signals
        # ---------------------------

        data = {

            # ---------------------------
            # 1.1 Asset Inventory
            # ---------------------------

            "cai_enabled": bool(cai_assets),
            "inventory_scope_defined":
                client.config.get(
                    "asset_inventory_scope_defined",
                    False
                ),

            "asset_export_available":
                client.config.get(
                    "asset_export_available",
                    False
                ),

            "required_metadata_present":
                self._validate_asset_metadata(
                    asset_inventory
                ),

            "assets": asset_inventory,

            "review_schedule_defined":
                client.config.get(
                    "inventory_review_schedule",
                    False
                ),

            "review_execution_verified":
                self._inventory_review_execution_verified(
                    review_history,
                    client.config.get(
                        "inventory_review_frequency_days",
                        180
                    )
                ),

            "review_frequency_days":
                client.config.get(
                    "inventory_review_frequency_days",
                    180
                ),

            "last_inventory_review_timestamp":
                self._latest_timestamp(review_history),


            # ---------------------------
            # 1.2 Unauthorized Assets
            # ---------------------------

            "scc_enabled":
                bool(scc_findings),

            "unauthorized_asset_detection":
                bool(unauthorized_assets),

            "unauthorized_assets":
                unauthorized_assets,

            "weekly_review_schedule_defined":
                client.config.get(
                    "unauthorized_asset_weekly_review",
                    False
                ),

            "weekly_review_verified":
                self._weekly_execution_verified(
                    review_history
                ),

            "triage_records":
                tickets,

            "remediation_actions":
                remediation_actions,


            # ---------------------------
            # 1.3 Active Discovery
            # ---------------------------

            "active_discovery_enabled":
                bool(flow_logs),

            "discovery_scope_defined":
                client.config.get(
                    "network_scope_defined",
                    False
                ),

            "daily_discovery_schedule":
                self._daily_job_exists(
                    discovery_jobs
                ),

            "daily_discovery_verified":
                bool(active_discovery_results),

            "observed_endpoints":
                active_discovery_results,

            "scc_assets":
                scc_assets,


            # ---------------------------
            # 1.4 DHCP Logging
            # ---------------------------

            "dhcp_logging_enabled":
                bool(dhcp_logs),

            "dhcp_sources_defined":
                client.config.get(
                    "dhcp_sources_defined",
                    False
                ),

            "dhcp_events":
                dhcp_events,

            "weekly_dhcp_review_defined":
                client.config.get(
                    "dhcp_weekly_review",
                    False
                ),

            "dhcp_inventory_updates":
                self._extract_inventory_updates(
                    tickets
                ),


            # ---------------------------
            # 1.5 Passive Discovery
            # ---------------------------

            "packet_mirroring_enabled":
                bool(packet_mirroring),

            "vpc_flow_logs_enabled":
                bool(flow_logs),

            "passive_discovery_scope_defined":
                client.config.get(
                    "passive_scope_defined",
                    False
                ),

            "passive_endpoints":
                passive_discovery_results,

            "passive_review_verified":
                bool(passive_discovery_results),

            "passive_triage_records":
                tickets,


            # ---------------------------
            # General Evidence
            # ---------------------------

            "collection_timestamp":
                datetime.now(timezone.utc).isoformat(),

        }

        return data


    # =========================================================
    # Extraction Logic
    # =========================================================

    def _build_asset_inventory(self, assets):
        inventory = []

        for asset in assets:
            inventory.append({
                "asset_name":
                    asset.get("name"),

                "asset_type":
                    asset.get("assetType"),

                "project_id":
                    asset.get("project"),

                "owner":
                    asset.get(
                        "labels",
                        {}
                    ).get(
                        "owner"
                    ),

                "network_address":
                    self._extract_network_address(asset),

                "approved_connection_status":
                    asset.get(
                        "approvedConnectionStatus",
                        "UNKNOWN"
                    ),
            })

        return inventory


    def _extract_network_address(self, asset):
        """Return a stable string network address from CAI asset data."""
        value = asset.get("networkInterface")
        if isinstance(value, str):
            return value.strip()
        if isinstance(value, dict):
            for key in ("networkAddress", "network_address", "ipAddress", "ip"):
                candidate = value.get(key)
                if isinstance(candidate, str) and candidate.strip():
                    return candidate.strip()
        if isinstance(value, list):
            for interface in value:
                if not isinstance(interface, dict):
                    continue
                for key in ("networkAddress", "network_address", "ipAddress", "ip"):
                    candidate = interface.get(key)
                    if isinstance(candidate, str) and candidate.strip():
                        return candidate.strip()
        return ""


    def _validate_asset_metadata(self, assets):
        if not assets:
            return False

        for asset in assets:
            required = [
                "asset_name",
                "asset_type",
                "project_id",
                "owner",
                "network_address",
                "approved_connection_status",
            ]

            if not all(
                asset.get(field)
                for field in required
            ):
                return False

        return True


    def _extract_unauthorized_assets(
        self,
        findings,
        assets
    ):
        results = []

        for finding in findings:
            if "UNAUTHORIZED" in finding.get(
                "category",
                ""
            ).upper():

                results.append({
                    "asset_id":
                        finding.get(
                            "resourceName"
                        ),

                    "severity":
                        finding.get(
                            "severity"
                        ),

                    "timestamp":
                        finding.get(
                            "eventTime"
                        ),
                })

        return results


    def _extract_active_discovery(
        self,
        flow_logs,
        jobs
    ):
        endpoints = []

        for flow in flow_logs:
            endpoints.append({
                "source_ip":
                    flow.get(
                        "srcIp"
                    ),

                "destination_ip":
                    flow.get(
                        "destIp"
                    ),

                "timestamp":
                    flow.get(
                        "timestamp"
                    ),
            })

        return endpoints


    def _extract_dhcp_events(
        self,
        logs
    ):
        return [
            {
                "hostname":
                    log.get(
                        "hostname"
                    ),

                "ip_address":
                    log.get(
                        "ip"
                    ),

                "lease_timestamp":
                    log.get(
                        "timestamp"
                    ),
            }
            for log in logs
        ]


    def _extract_passive_discovery(
        self,
        flow_logs,
        packet_mirroring
    ):
        endpoints = []

        for flow in flow_logs:
            endpoints.append({
                "source_ip":
                    flow.get(
                        "srcIp"
                    ),

                "destination_ip":
                    flow.get(
                        "destIp"
                    ),

                "traffic_observed":
                    True,

                "timestamp":
                    flow.get(
                        "timestamp"
                    ),
            })

        return endpoints


    def _extract_remediation_actions(
        self,
        tickets
    ):
        return [
            {
                "asset_id":
                    ticket.get(
                        "asset"
                    ),

                "action":
                    ticket.get(
                        "resolution"
                    ),

                "timestamp":
                    ticket.get(
                        "closed"
                    ),
            }
            for ticket in tickets
        ]


    def _extract_inventory_updates(
        self,
        tickets
    ):
        return [
            ticket
            for ticket in tickets
            if "inventory"
            in ticket.get(
                "description",
                ""
            ).lower()
        ]


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
                    ),
            }
            for job in jobs
        ]


    def _get_successful_review_time(self, review):
        """Return a successful review timestamp in UTC, or None."""
        if review.get("status") != "SUCCESS":
            return None

        timestamp = review.get("timestamp")
        if not timestamp:
            return None

        try:
            return datetime.fromisoformat(
                timestamp.replace("Z", "+00:00")
            ).astimezone(timezone.utc)
        except (TypeError, ValueError):
            return None


    def _weekly_execution_verified(
        self,
        reviews
    ):
        cutoff = datetime.now(timezone.utc) - timedelta(days=7)
        now = datetime.now(timezone.utc)

        for review in reviews:
            review_time = self._get_successful_review_time(review)
            if review_time is None:
                continue

            if cutoff <= review_time <= now:
                return True

        return False


    def _daily_job_exists(
        self,
        jobs
    ):
        for job in jobs:
            if job.get(
                "frequency"
            ) in [
                "DAILY",
                "HOURLY"
            ]:
                return True

        return False


    def _inventory_review_execution_verified(
        self,
        reviews,
        frequency_days
    ):
        """Verify that a successful inventory review occurred recently."""
        if not reviews or frequency_days is None:
            return False

        try:
            frequency_days = int(frequency_days)
        except (TypeError, ValueError):
            return False

        if frequency_days < 0 or frequency_days > 180:
            return False

        now = datetime.now(timezone.utc)
        cutoff = now - timedelta(days=frequency_days)

        for review in reviews:
            review_time = self._get_successful_review_time(review)
            if review_time is None:
                continue

            if cutoff <= review_time <= now:
                return True

        return False


    def _latest_timestamp(
        self,
        records
    ):
        """Return the most recent valid review timestamp."""
        timestamps = []

        for record in records or []:
            timestamp = record.get("timestamp")
            if not timestamp:
                continue
            try:
                parsed = datetime.fromisoformat(
                    timestamp.replace("Z", "+00:00")
                ).astimezone(timezone.utc)
                timestamps.append((parsed, timestamp))
            except (TypeError, ValueError):
                continue

        if not timestamps:
            return ""

        return max(timestamps, key=lambda item: item[0])[1]
		