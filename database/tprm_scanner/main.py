import argparse
from datetime import datetime, timezone
from checkers.dns_checker import DNSChecker
from checkers.http_checker import HTTPChecker
from checkers.ssl_checker import SSLChecker
from checkers.server_checker import ServerChecker
from checkers.reputation_checker import ReputationChecker
from checkers.threat_intel_checker import get_virustotal_url_report
from checkers.rapidscan_checker import RapidScanChecker

from rich.console import Console
from rich.table import Table


def run_all_checks(domain, progress_callback=None):
    """Run all security checks for a given domain with progress updates."""
    all_results = [] # Renamed from 'results' to 'all_results' to avoid confusion with individual check results
    
    checkers = [
        ('DNS', DNSChecker),
        ('HTTP', HTTPChecker),
        ('SSL', SSLChecker),
        ('Server', ServerChecker),
        ('Reputation', ReputationChecker),
        ('RapidScan', RapidScanChecker)
    ]
    
    total_checks = len(checkers)
    completed_checks = 0
    
    for check_name, checker_class in checkers:
        current_check_name = check_name # Store name before potential modification by checker
        try:
            if progress_callback:
                progress_callback({
                    'status': 'running',
                    'message': f'Running {current_check_name} checks...',
                    'progress': (completed_checks / total_checks) * 100,
                    'checker': current_check_name
                })
            
            checker = checker_class(domain)
            individual_results = checker.run_checks() # Renamed to avoid confusion
            
            # Process and standardize results
            if isinstance(individual_results, list):
                # If the checker returns a list of findings for this check category
                for result_item in individual_results:
                    result_item['checker'] = current_check_name # Use stored name
                    result_item['timestamp'] = str(datetime.now(timezone.utc))
                    all_results.append(result_item) # Append each item individually
            elif isinstance(individual_results, dict):
                # If the checker returns a single dictionary for this check category
                individual_results['checker'] = current_check_name # Use stored name
                individual_results['timestamp'] = str(datetime.now(timezone.utc))
                all_results.append(individual_results) # Append the single dictionary
            else:
                # Handle unexpected return types, though ideally checkers always return list or dict
                error_result = {
                    'name': f'{current_check_name} Check',
                    'status': 'ERROR',
                    'severity': 'HIGH',
                    'details': f'Checker for {current_check_name} returned an unexpected data type: {type(individual_results).__name__}',
                    'raw_data': {'error': 'Unexpected data type', 'type': str(type(individual_results).__name__)},
                    'checker': current_check_name,
                    'timestamp': str(datetime.now(timezone.utc))
                }
                all_results.append(error_result)

            completed_checks += 1
            
            # The progress_callback should ideally not be adding to the main results list.
            # If it needs to show intermediate results, it should handle its own display.
            # For now, we'll just pass progress info. If results need to be passed for intermediate display,
            # that logic needs careful consideration to avoid duplication.
            if progress_callback:
                progress_callback({
                    'status': 'completed',
                    'message': f'Completed {current_check_name} checks',
                    'progress': (completed_checks / total_checks) * 100,
                    'checker': current_check_name,
                    # Do NOT pass 'results': all_results here if main() also displays the final results
                })
                
        except Exception as e:
            error_result = {
                'name': f'{current_check_name} Check',
                'status': 'ERROR',
                'severity': 'HIGH',
                'details': f'Error during {current_check_name} check: {str(e)}',
                'raw_data': {'error': str(e), 'type': str(type(e).__name__)},
                'checker': current_check_name,
                'timestamp': str(datetime.now(timezone.utc))
            }
            all_results.append(error_result)
            
            if progress_callback:
                progress_callback({
                    'status': 'error',
                    'message': f'Error in {current_check_name} check: {str(e)}',
                    'progress': (completed_checks / total_checks) * 100
                })
    
    # If no results were collected, add an error
    if not all_results:
        all_results.append({
            'name': 'Security Scan',
            'status': 'ERROR',
            'details': 'No security check results were collected',
            'raw_data': {'error': 'No results', 'type': 'EmptyResultsError'}
        })
    
    return all_results # Return the consolidated list

def main():
    parser = argparse.ArgumentParser(description='Perform a security checklist scan on a domain.')
    parser.add_argument('domain', help='The domain name to scan (e.g., example.com)')
    args = parser.parse_args()
    
    console = Console()
    console.print(f"[bold cyan]Starting security scan for {args.domain}...[/bold cyan]\n")

    # Define a simple progress callback for demonstration
    def simple_progress_callback(progress_info):
        # This callback just prints status updates to the console.
        # It does NOT append results to the main list.
        status = progress_info.get('status', 'INFO')
        message = progress_info.get('message', 'Processing...')
        progress_percent = progress_info.get('progress', 0)
        checker = progress_info.get('checker', 'N/A')
        
        if status == 'running':
            console.print(f"[yellow]Running ({checker}):[/yellow] {message} [{progress_percent:.0f}%]")
        elif status == 'completed':
            console.print(f"[green]Completed ({checker}):[/green] {message} [{progress_percent:.0f}%]")
        elif status == 'error':
            console.print(f"[red]Error ({checker}):[/red] {message} [{progress_percent:.0f}%]")

    try:
        # Pass the simple_progress_callback to run_all_checks
        results = run_all_checks(args.domain, progress_callback=simple_progress_callback)
        
        # Create results table
        table = Table(title=f"Security Scan Report for {args.domain}", show_header=True, header_style="bold magenta")
        table.add_column("Check Name", style="dim", width=50)
        table.add_column("Status", justify="center")
        table.add_column("Details")

        status_colors = {
            'CRITICAL': 'red bold',
            'HIGH': 'red',
            'MEDIUM': 'yellow',
            'LOW': 'green',
            'INFO': 'blue',
            'ERROR': 'red bold',
            'PASS': 'green',
            'FAIL': 'red',
            'WARN': 'yellow',
            'SKIPPED': 'dim'
        }

        # This loop iterates over the consolidated 'results' list once.
        for result in results:
            # Ensure status is a string and handle potential None values gracefully
            status_str = str(result.get('status', 'INFO'))
            status = status_str.upper() # Normalize to uppercase for color mapping
            
            color = status_colors.get(status, 'white')
            
            # Ensure details are strings
            details = str(result.get('details', 'No details available'))
            
            table.add_row(
                result.get('name', 'N/A'),
                f"[{color}]{status}[/{color}]",
                details
            )

        console.print(table)
        console.print("\n[bold]Scan Complete.[/bold]")
        return 0

    except Exception as e:
        console.print(f"[bold red]An unexpected error occurred during scan setup: {str(e)}[/bold red]")
        return 1


if __name__ == '__main__':
    main()