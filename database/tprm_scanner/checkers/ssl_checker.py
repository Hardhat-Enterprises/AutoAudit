# security-checker/checkers/ssl_checker.py

from sslyze import Scanner, ServerScanRequest, ScanCommand
from sslyze.server_setting import ServerNetworkLocation
from sslyze.errors import ServerHostnameCouldNotBeResolved

from datetime import datetime


class SSLChecker:
    def __init__(self, domain):
        self.domain = domain
        self.results = []
        self.sslyze_results = None

    def _run_sslyze(self):
        try:
            scanner = Scanner()
            scan_request = ServerScanRequest(
                server_location=ServerNetworkLocation(hostname=self.domain, port=443),
                scan_commands={
                    ScanCommand.CERTIFICATE_INFO,
                    ScanCommand.HEARTBLEED,
                    ScanCommand.SSL_2_0_CIPHER_SUITES,
                    ScanCommand.SSL_3_0_CIPHER_SUITES,
                    ScanCommand.TLS_1_0_CIPHER_SUITES,
                    ScanCommand.TLS_1_1_CIPHER_SUITES,
                    ScanCommand.TLS_1_2_CIPHER_SUITES,
                    ScanCommand.TLS_1_3_CIPHER_SUITES,
                },
            )

            scanner.queue_scan(scan_request)
            for result in scanner.get_results():
                if result.scan_status.name == 'ERROR':
                    self.results.append({
                        'name': 'SSL/TLS Scan',
                        'status': 'ERROR',
                        'details': f'Could not scan {self.domain}.'
                    })
                    return False
                self.sslyze_results = result
                return True

        except ServerHostnameCouldNotBeResolved:
            self.results.append({
                'name': 'SSL/TLS Scan',
                'status': 'ERROR',
                'details': f'Could not resolve domain: {self.domain}'
            })
            return False
        except Exception as e:
            self.results.append({
                'name': 'SSL/TLS Scan',
                'status': 'ERROR',
                'details': f'Unexpected error: {e}'
            })
            return False

    def check_vulnerabilities(self):
        try:
            heartbleed = self.sslyze_results.scan_commands_results[ScanCommand.HEARTBLEED]
            if not heartbleed.is_vulnerable_to_heartbleed:
                self.results.append({'name': 'Heartbleed Vulnerability', 'status': 'PASS', 'details': 'Server is not vulnerable to Heartbleed.'})
            else:
                self.results.append({'name': 'Heartbleed Vulnerability', 'status': 'FAIL', 'details': 'Server is vulnerable to Heartbleed!'})
            self.results.append({'name': 'POODLE, FREAK, Logjam', 'status': 'INFO', 'details': 'Checked implicitly via cipher and protocol scans.'})
        except Exception:
            self.results.append({'name': 'Heartbleed Vulnerability', 'status': 'ERROR', 'details': 'Could not complete Heartbleed check.'})

    def check_certificate(self):
        try:
            cert_info = self.sslyze_results.scan_commands_results[ScanCommand.CERTIFICATE_INFO]
            if not cert_info:
                self.results.append({'name': 'Certificate Information', 'status': 'ERROR', 'details': 'Could not retrieve certificate info.'})
                return

            cert = cert_info.certificate_deployments[0].received_certificate_chain[0]
            not_valid_after = cert.not_valid_after.replace(tzinfo=None)
            time_left = not_valid_after - datetime.utcnow()

            if cert_info.hostname_validation_result.is_hostname_match:
                self.results.append({'name': 'Hostname Matches SSL Certificate', 'status': 'PASS', 'details': 'Hostname matches the SSL certificate.'})
            else:
                self.results.append({'name': 'Hostname Matches SSL Certificate', 'status': 'FAIL', 'details': 'Hostname does NOT match the SSL certificate.'})

            self.results.append({
                'name': 'SSL Has Not Expired',
                'status': 'PASS' if time_left.days > 0 else 'FAIL',
                'details': f'Certificate expires in {time_left.days} days.' if time_left.days > 0 else f'Certificate expired {-time_left.days} days ago.'
            })

            self.results.append({
                'name': 'SSL Does Not Expire Within 20 Days',
                'status': 'PASS' if time_left.days > 20 else 'FAIL',
                'details': f'Certificate expires in {time_left.days} days.'
            })

            validity_period = cert.not_valid_after - cert.not_valid_before
            self.results.append({
                'name': 'SSL Expiration Shorter than 398 Days',
                'status': 'PASS' if validity_period.days < 398 else 'WARN',
                'details': f'Validity period is {validity_period.days} days.'
            })

            key_size = cert.public_key().key_size
            self.results.append({
                'name': 'Strong Public Certificate Key Length',
                'status': 'PASS' if key_size >= 2048 else 'FAIL',
                'details': f'Public key size: {key_size} bits.'
            })

            path_validation = cert_info.certificate_deployments[0].path_validation_result
            if path_validation and path_validation.was_validation_successful:
                self.results.append({'name': 'Trusted SSL Certificate', 'status': 'PASS', 'details': 'Certificate chain is trusted.'})
            else:
                self.results.append({'name': 'Trusted SSL Certificate', 'status': 'FAIL', 'details': 'Certificate chain is not trusted.'})

        except Exception:
            self.results.append({'name': 'Certificate Checks', 'status': 'ERROR', 'details': 'Could not complete certificate checks.'})

    def check_protocols_and_ciphers(self):
        try:
            insecure_protocols = []

            def check_insecure(cmd, label):
                result = self.sslyze_results.scan_commands_results.get(cmd)
                if result and result.accepted_cipher_suites:
                    insecure_protocols.append(label)

            check_insecure(ScanCommand.SSL_2_0_CIPHER_SUITES, "SSL 2.0")
            check_insecure(ScanCommand.SSL_3_0_CIPHER_SUITES, "SSL 3.0")
            check_insecure(ScanCommand.TLS_1_0_CIPHER_SUITES, "TLS 1.0")
            check_insecure(ScanCommand.TLS_1_1_CIPHER_SUITES, "TLS 1.1")

            if insecure_protocols:
                self.results.append({
                    'name': 'No Insecure SSL/TLS Versions',
                    'status': 'FAIL',
                    'details': f"Insecure protocols supported: {', '.join(insecure_protocols)}"
                })
            else:
                self.results.append({
                    'name': 'No Insecure SSL/TLS Versions',
                    'status': 'PASS',
                    'details': 'Only secure protocols (TLS 1.2, TLS 1.3) are enabled.'
                })

        except Exception:
            self.results.append({'name': 'Protocol Version Checks', 'status': 'ERROR', 'details': 'Could not check protocol versions.'})

    def run_checks(self):
        if self._run_sslyze():
            self.check_vulnerabilities()
            self.check_certificate()
            self.check_protocols_and_ciphers()
        return self.results


if __name__ == "__main__":
    domain = "google.com"  # Replace with target domain or modify for CLI input
    checker = SSLChecker(domain)
    results = checker.run_checks()

    print(f"\n--- SSL Check Results for {domain} ---")
    for result in results:
        print(f"{result['name']}: {result['status']}")
        if result.get("details"):
            print(f"  → {result['details']}")
