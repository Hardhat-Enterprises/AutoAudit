# main.py

import argparse
from checkers.dns_checker import DNSChecker
from checkers.http_checker import HTTPChecker
from checkers.ssl_checker import SSLChecker
from checkers.server_checker import ServerChecker
from checkers.reputation_checker import ReputationChecker
from checkers.threat_intel_checker import get_virustotal_url_report
from checkers.rapidscan_checker import RapidScanChecker

from rich.console import Console
from rich.table import Table


def main():
    parser = argparse.ArgumentParser(description='Perform a security checklist scan on a domain.')
    parser.add_argument('domain', help='The domain name to scan (e.g., example.com)')
    args = parser.parse_args()
    domain = args.domain

    console = Console()
    console.print(f"[bold cyan]Starting security scan for {domain}...[/bold cyan]\n")

    all_results = []

    try:
        with console.status("[bold green]Running DNS checks...[/bold green]"):
            dns_checker = DNSChecker(domain)
            all_results.extend(dns_checker.run_checks())

        with console.status("[bold green]Running HTTP/Header checks...[/bold green]"):
            http_checker = HTTPChecker(domain)
            all_results.extend(http_checker.run_checks())

        with console.status("[bold green]Running SSL/TLS checks...[/bold green]"):
            ssl_checker = SSLChecker(domain)
            all_results.extend(ssl_checker.run_checks())

        with console.status("[bold green]Running Server checks...[/bold green]"):
            server_checker = ServerChecker(domain)
            all_results.extend(server_checker.run_checks())

        with console.status("[bold green]Running Reputation checks...[/bold green]"):
            reputation_checker = ReputationChecker(domain)
            all_results.extend(reputation_checker.run_checks())

        with console.status("[bold green]Fetching VirusTotal report...[/bold green]"):
            vt_result = get_virustotal_url_report(domain)
            if isinstance(vt_result, list):
                all_results.extend(vt_result)
            else:
                all_results.append(vt_result)

        #with console.status("[bold green]Running RapidScan vulnerability checks...[/bold green]"):
        #   rapidscan_checker = RapidScanChecker(domain)
        #    all_results.extend(rapidscan_checker.run_checks())


    except Exception as e:
        all_results.append({
            'name': 'Fatal Error During Scan',
            'status': 'ERROR',
            'details': str(e)
        })

    # --- Print Report ---
    table = Table(title=f"Security Scan Report for {domain}", show_header=True, header_style="bold magenta")
    table.add_column("Check Name", style="dim", width=50)
    table.add_column("Status", justify="center")
    table.add_column("Details")

    status_colors = {
        'PASS': 'green',
        'FAIL': 'bold red',
        'WARN': 'yellow',
        'INFO': 'cyan',
        'ERROR': 'bold magenta',
        'SKIPPED': 'dim'
    }

    for result in all_results:
        status = result.get('status', 'INFO')
        color = status_colors.get(status, 'white')
        table.add_row(
            result.get('name', 'N/A'),
            f"[{color}]{status}[/{color}]",
            result.get('details', 'No details available.')
        )

    console.print(table)
    console.print("\n[bold]Scan Complete.[/bold]")


if __name__ == '__main__':
    main()

