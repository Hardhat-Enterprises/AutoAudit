# checkers/rapidscan_checker.py

import subprocess
import os

class RapidScanChecker:
    def __init__(self, domain):
        self.domain = domain
        self.results = []

    def run_checks(self):
        try:
            # Construct the full path to rapidscan.py
            script_path = os.path.join(os.path.dirname(__file__), "rapidscan", "rapidscan.py")

            # Run the script using subprocess
            result = subprocess.run(
                ["python3", script_path, self.domain],
                capture_output=True,
                text=True,
                timeout=180  # Reduce timeout if needed
            )

            # If command succeeded
            if result.returncode == 0:
                output = result.stdout.strip()
                self.results.append({
                    "name": "RapidScan Vulnerability Summary",
                    "status": "INFO",
                    "details": output[:1000] + "..." if len(output) > 1000 else output
                })
            else:
                # Capture error output
                self.results.append({
                    "name": "RapidScan Execution Error",
                    "status": "ERROR",
                    "details": result.stderr.strip() or "RapidScan returned a non-zero exit code."
                })

        except subprocess.TimeoutExpired:
            self.results.append({
                "name": "RapidScan Timeout",
                "status": "ERROR",
                "details": "RapidScan command timed out after 180 seconds."
            })

        except Exception as e:
            self.results.append({
                "name": "RapidScan Exception",
                "status": "ERROR",
                "details": str(e)
            })

        return self.results
