"""DNS security records collector.

CIS Microsoft 365 Foundations Benchmark Controls:
    v6.0.0: 2.1.8, 2.1.10

Connection Method: Microsoft Graph API + DNS queries
Required Scopes: Domain.Read.All
Graph Endpoint: /domains
DNS Records: SPF (TXT), DMARC (_dmarc.{domain} TXT)

Note: This collector uses a two-step approach:
    1. Retrieve tenant domains via Microsoft Graph API
    2. Query DNS for SPF and DMARC records for each verified domain
"""

from typing import Any

from collectors.base import BaseDataCollector
from collectors.graph_client import GraphClient


class DnsSecurityRecordsDataCollector(BaseDataCollector):
    """Collects DNS security records (SPF, DMARC) for CIS compliance evaluation.

    This collector retrieves all verified domains from the tenant via Graph API,
    then performs DNS lookups for SPF and DMARC records on each domain.
    """

    async def collect(self, client: GraphClient) -> dict[str, Any]:
        """Collect DNS security records for all tenant domains.

        Returns:
            Dict containing:
            - domains: List of domain records with SPF/DMARC status
            - total_domains: Number of verified domains checked
            - domains_with_spf: Count of domains with valid SPF records
            - domains_with_dmarc: Count of domains with valid DMARC records
            - domains_missing_spf: List of domains without SPF records
            - domains_missing_dmarc: List of domains without DMARC records
        """
        import dns.resolver

        # Step 1: Get domains from Graph API
        domains = await client.get_domains()

        # Step 2: Filter for verified domains
        verified_domains = [d for d in domains if d.get("isVerified", False)]

        domain_records = []
        for domain in verified_domains:
            domain_id = domain.get("id")

            record = {
                "domain": domain_id,
                "is_verified": True,
                "is_default": domain.get("isDefault", False),
                "is_initial": domain.get("isInitial", False),
                "authentication_type": domain.get("authenticationType"),
                "spf_record": None,
                "dmarc_record": None,
                "has_valid_spf": False,
                "has_valid_dmarc": False,
                "spf_error": None,
                "dmarc_error": None,
            }

            # Query SPF record (TXT record at domain root)
            try:
                answers = dns.resolver.resolve(domain_id, "TXT")
                for rdata in answers:
                    # TXT records may have multiple strings, join them
                    txt_value = "".join(s.decode() if isinstance(s, bytes) else s for s in rdata.strings)
                    if txt_value.startswith("v=spf1"):
                        record["spf_record"] = txt_value
                        record["has_valid_spf"] = True
                        break
            except dns.resolver.NXDOMAIN:
                record["spf_error"] = "Domain not found"
            except dns.resolver.NoAnswer:
                record["spf_error"] = "No TXT records"
            except dns.resolver.NoNameservers:
                record["spf_error"] = "No nameservers available"
            except dns.resolver.Timeout:
                record["spf_error"] = "DNS query timeout"
            except Exception as e:
                record["spf_error"] = str(e)

            # Query DMARC record (TXT record at _dmarc.{domain})
            dmarc_domain = f"_dmarc.{domain_id}"
            try:
                answers = dns.resolver.resolve(dmarc_domain, "TXT")
                for rdata in answers:
                    txt_value = "".join(s.decode() if isinstance(s, bytes) else s for s in rdata.strings)
                    if txt_value.startswith("v=DMARC1"):
                        record["dmarc_record"] = txt_value
                        record["has_valid_dmarc"] = True
                        # Parse DMARC policy
                        record["dmarc_policy"] = self._parse_dmarc_policy(txt_value)
                        break
            except dns.resolver.NXDOMAIN:
                record["dmarc_error"] = "DMARC record not found"
            except dns.resolver.NoAnswer:
                record["dmarc_error"] = "No DMARC TXT record"
            except dns.resolver.NoNameservers:
                record["dmarc_error"] = "No nameservers available"
            except dns.resolver.Timeout:
                record["dmarc_error"] = "DNS query timeout"
            except Exception as e:
                record["dmarc_error"] = str(e)

            domain_records.append(record)

        # Build summary
        domains_with_spf = [d for d in domain_records if d["has_valid_spf"]]
        domains_with_dmarc = [d for d in domain_records if d["has_valid_dmarc"]]
        domains_missing_spf = [d["domain"] for d in domain_records if not d["has_valid_spf"]]
        domains_missing_dmarc = [d["domain"] for d in domain_records if not d["has_valid_dmarc"]]

        return {
            "domains": domain_records,
            "total_domains": len(domain_records),
            "domains_with_spf": len(domains_with_spf),
            "domains_with_dmarc": len(domains_with_dmarc),
            "domains_missing_spf": domains_missing_spf,
            "domains_missing_dmarc": domains_missing_dmarc,
            "all_domains_have_spf": len(domains_missing_spf) == 0,
            "all_domains_have_dmarc": len(domains_missing_dmarc) == 0,
        }

    def _parse_dmarc_policy(self, dmarc_record: str) -> dict[str, str]:
        """Parse DMARC record into key-value pairs.

        Args:
            dmarc_record: Raw DMARC TXT record value

        Returns:
            Dict with DMARC policy settings (p, sp, rua, ruf, pct, etc.)
        """
        policy = {}
        # Split by semicolons and parse key=value pairs
        parts = dmarc_record.split(";")
        for part in parts:
            part = part.strip()
            if "=" in part:
                key, value = part.split("=", 1)
                policy[key.strip()] = value.strip()
        return policy
