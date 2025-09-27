# /checkers directory 
# dns_checker.py

# /checkers/dns_checker.py

import dns.resolver
from urllib.parse import urlparse

def get_base_domain(target):
    """Extracts the base domain from a URL or domain string."""
    if not target.startswith(('http://', 'https://')):
        target = 'http://' + target
    parsed_uri = urlparse(target)
    domain_parts = parsed_uri.netloc.split('.')
    if len(domain_parts) > 2:
        return '.'.join(domain_parts[-2:])
    return parsed_uri.netloc

class DNSChecker:
    def __init__(self, domain):
        self.base_domain = get_base_domain(domain)
        self.results = []

    def check_dmarc(self):
        try:
            dmarc_record = dns.resolver.resolve(f'_dmarc.{self.base_domain}', 'TXT')
            record_found = False
            policy_not_none = False
            for record in dmarc_record:
                record_text = record.to_text().strip('"')
                if 'v=DMARC1' in record_text:
                    record_found = True
                    if 'p=none' not in record_text:
                        policy_not_none = True
                    else:
                        # Check for sp=none as well, which is also weak
                        if 'sp=none' in record_text and 'p=quarantine' not in record_text and 'p=reject' not in record_text:
                            policy_not_none = False

            self.results.append({'name': 'DMARC Policy Exists', 'status': 'PASS' if record_found else 'FAIL', 'details': f'DMARC record found for {self.base_domain}' if record_found else f'No DMARC record found for {self.base_domain}'})
            self.results.append({'name': 'DMARC Policy Not p=none', 'status': 'PASS' if policy_not_none else 'FAIL', 'details': 'DMARC policy is stronger than p=none (e.g., quarantine or reject).' if policy_not_none else 'DMARC policy is p=none, which is for monitoring only.'})
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            self.results.append({'name': 'DMARC Policy Exists', 'status': 'FAIL', 'details': f'No DMARC record found for {self.base_domain}'})
            self.results.append({'name': 'DMARC Policy Not p=none', 'status': 'FAIL', 'details': 'No DMARC record exists.'})


    def check_mx_records(self):
        try:
            dns.resolver.resolve(self.base_domain, 'MX')
            self.results.append({'name': 'No Unregistered MX Records', 'status': 'PASS', 'details': 'MX records are present.'})
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            self.results.append({'name': 'No Unregistered MX Records', 'status': 'FAIL', 'details': 'No MX records found. This domain cannot receive email.'})

    def check_caa_enabled(self):
        try:
            dns.resolver.resolve(self.base_domain, 'CAA')
            self.results.append({'name': 'CAA Enabled', 'status': 'PASS', 'details': 'CAA (Certificate Authority Authorization) record is enabled.'})
        except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
            self.results.append({'name': 'CAA Enabled', 'status': 'WARN', 'details': 'No CAA record found. Any CA may issue certificates for this domain.'})

    def run_checks(self):
        self.check_dmarc()
        self.check_mx_records()
        self.check_caa_enabled()
        return self.results


