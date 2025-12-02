# /checkers/server_checker.py

import socket
import requests

class ServerChecker:
    def __init__(self, domain):
        self.domain = domain
        self.ip = socket.gethostbyname(domain)
        self.results = []

    def check_open_ports(self):
        # A full port scan is slow and noisy. We'll check a few common ones.
        # The user's list is unusual (e.g., 179 for BGP).
        common_ports = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP', 53: 'DNS', 80: 'HTTP',
            110: 'POP3', 143: 'IMAP', 443: 'HTTPS', 445: 'SMB',
            3306: 'MySQL', 3389: 'RDP', 5900: 'VNC', 8080: 'HTTP-alt'
        }
        
        open_ports = []
        for port, service in common_ports.items():
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.ip, port))
            if result == 0:
                open_ports.append(f'{port} ({service})')
            sock.close()

        # Check specific ports from the user's list
        if 179 not in common_ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            if sock.connect_ex((self.ip, 179)) == 0:
                 self.results.append({'name': 'Port 179 (BGP) Open', 'status': 'WARN', 'details': 'Port 179 is open. This is unusual for a standard web server.'})
            sock.close()

        if '443 (HTTPS)' in open_ports:
             self.results.append({'name': 'HTTPS Port Open', 'status': 'PASS', 'details': 'Port 443 is open, as expected.'})
             open_ports.remove('443 (HTTPS)') # Don't report it twice
        else:
             self.results.append({'name': 'HTTPS Port Open', 'status': 'FAIL', 'details': 'Port 443 is closed. HTTPS will not work.'})

        if open_ports:
            self.results.append({'name': 'Unnecessary Ports Open', 'status': 'WARN', 'details': f'Potentially unnecessary ports are open: {", ".join(open_ports)}'})
        else:
            self.results.append({'name': 'Unnecessary Ports Open', 'status': 'PASS', 'details': 'No common unnecessary ports detected open.'})


    def check_directory_listing(self):
        try:
            url = f'https://{self.domain}/'
            response = requests.get(url, timeout=5)
            if 'index of /' in response.text.lower() or 'parent directory' in response.text.lower():
                self.results.append({'name': 'Directory Listing', 'status': 'FAIL', 'details': 'Directory listing is enabled on the web server.'})
            else:
                self.results.append({'name': 'Directory Listing', 'status': 'PASS', 'details': 'Directory listing seems to be disabled.'})
        except requests.RequestException:
             self.results.append({'name': 'Directory Listing', 'status': 'ERROR', 'details': 'Could not check for directory listing.'})

    def run_checks(self):
        self.check_open_ports()
        self.check_directory_listing()
        return self.results



