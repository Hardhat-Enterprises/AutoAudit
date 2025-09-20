# /checkers/http_checker.py

import requests

class HTTPChecker:
    def __init__(self, domain):
        self.domain = domain
        self.results = []
        self.headers = {}
        self.response = None

    def _make_request(self):
        try:
            # Check for HTTP to HTTPS redirection
            http_url = f'http://{self.domain}'
            http_response = requests.get(http_url, allow_redirects=False, timeout=10)
            if 300 <= http_response.status_code < 400 and http_response.headers.get('Location', '').startswith('https://'):
                self.results.append({'name': 'HTTP to HTTPS Redirect', 'status': 'PASS', 'details': 'HTTP requests are properly redirected to HTTPS.'})
            else:
                self.results.append({'name': 'HTTP to HTTPS Redirect', 'status': 'FAIL', 'details': 'No automatic redirect from HTTP to HTTPS.'})

            # Main request to HTTPS endpoint
            https_url = f'https://{self.domain}'
            self.response = requests.get(https_url, timeout=10)
            self.headers = self.response.headers

        except requests.exceptions.RequestException as e:
            self.results.append({'name': 'HTTPS Connection', 'status': 'ERROR', 'details': f'Could not connect to https://{self.domain}. Error: {e}'})
            return False
        return True

    def check_hsts(self):
        hsts_header = self.headers.get('Strict-Transport-Security')
        if hsts_header:
            self.results.append({'name': 'HSTS Enforced', 'status': 'PASS', 'details': f'HSTS header is present: {hsts_header}'})
            if 'includeSubDomains' in hsts_header:
                self.results.append({'name': 'HSTS includes SubDomains', 'status': 'PASS', 'details': 'HSTS header includes subdomains.'})
            else:
                self.results.append({'name': 'HSTS includes SubDomains', 'status': 'WARN', 'details': 'HSTS header does not include subdomains.'})
        else:
            self.results.append({'name': 'HSTS Enforced', 'status': 'FAIL', 'details': 'HSTS header is missing.'})

    def check_csp(self):
        csp_header = self.headers.get('Content-Security-Policy')
        if not csp_header:
            self.results.append({'name': 'CSP Implemented', 'status': 'FAIL', 'details': 'Content-Security-Policy header is not implemented.'})
            return

        checks = {
            'CSP contains unsafe-eval': ("'unsafe-eval'", "FAIL", "Presence of 'unsafe-eval' allows execution of strings as code."),
            'CSP contains unsafe-inline': ("'unsafe-inline'", "FAIL", "Presence of 'unsafe-inline' allows inline scripts/styles, increasing XSS risk."),
            'CSP insecure active sources': (("script-src http:", "script-src *"), "FAIL", "CSP allows insecure (http: or wildcard) active sources."),
            'CSP insecure passive sources': (("img-src http:", "img-src *", "style-src http:", "style-src *"), "FAIL", "CSP allows insecure passive sources."),
        }

        for name, (patterns, status, details) in checks.items():
            found = False
            if isinstance(patterns, tuple):
                for pattern in patterns:
                    if pattern in csp_header:
                        self.results.append({'name': name, 'status': status, 'details': details})
                        found = True
                        break
            elif patterns in csp_header:
                self.results.append({'name': name, 'status': status, 'details': details})
                found = True

            if not found:
                 self.results.append({'name': name.replace('contains', 'does not contain').replace('insecure', 'secure'), 'status': 'PASS', 'details': 'Policy appears secure regarding this check.'})

    def check_security_headers(self):
        headers_to_check = {
            'X-Frame-Options': ('X-Frame-Options to prevent clickjacking', "Header is present, protecting against clickjacking.", "Header is missing, vulnerable to clickjacking."),
            'X-Content-Type-Options': ('X-Content-Type-Options is nosniff', "Header is set to 'nosniff'.", "Header is missing or not 'nosniff'."),
            'Referrer-Policy': ('Referrer-Policy is secure', "A secure Referrer-Policy is set.", "Referrer-Policy is missing or potentially unsafe."),
        }
        for header, (name, pass_details, fail_details) in headers_to_check.items():
            if header in self.headers:
                self.results.append({'name': name, 'status': 'PASS', 'details': pass_details})
            else:
                self.results.append({'name': name, 'status': 'FAIL', 'details': fail_details})

        # Check for exposed information
        exposed_headers = ['Server', 'X-Powered-By', 'X-AspNet-Version']
        for header in exposed_headers:
            if header in self.headers:
                self.results.append({'name': f'{header} Header Exposed', 'status': 'WARN', 'details': f'Header is exposed: {self.headers[header]}'})
            else:
                self.results.append({'name': f'{header} Header Not Exposed', 'status': 'PASS', 'details': f'{header} header is not exposed.'})

    def check_secure_cookies(self):
        if 'Set-Cookie' in self.headers:
            cookie = self.headers['Set-Cookie']
            is_secure = 'secure' in cookie.lower()
            is_httponly = 'httponly' in cookie.lower()
            self.results.append({'name': 'Secure Cookies Used', 'status': 'PASS' if is_secure else 'FAIL', 'details': 'Cookie `Secure` flag is set.' if is_secure else 'Cookie `Secure` flag is missing.'})
            self.results.append({'name': 'HttpOnly Cookies Used', 'status': 'PASS' if is_httponly else 'FAIL', 'details': 'Cookie `HttpOnly` flag is set.' if is_httponly else 'Cookie `HttpOnly` flag is missing.'})
        else:
            self.results.append({'name': 'Secure Cookies Used', 'status': 'INFO', 'details': 'No cookies were set in the response.'})
            self.results.append({'name': 'HttpOnly Cookies Used', 'status': 'INFO', 'details': 'No cookies were set in the response.'})

    def run_checks(self):
        if self._make_request():
            self.check_hsts()
            self.check_csp()
            self.check_security_headers()
            self.check_secure_cookies()
        return self.results




