import requests
import os

class ReputationChecker:
    def __init__(self, domain):
        self.domain = domain
        self.results = []

    def run_checks(self):
        """
        Check website reputation using RapidAPI 'website-security-audit'.
        """
        url = "https://website-security-audit.p.rapidapi.com/siteaudit/siteaudit/premium"

        headers = {
            "x-rapidapi-key": os.environ["XRAPID_API_KEY"],
            "x-rapidapi-host": os.environ["XRAPID_API_HOST"]
        }

        params = {"url": f"https://{self.domain.strip()}"}


        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            data = response.json()

            # Example structure — update field names based on actual API response
            malware = data.get("malwareDetected", False)
            phishing = data.get("phishingDetected", False)
            blacklisted = data.get("blacklisted", False)

            self.results.append({
                "name": "Website Malware Status",
                "status": "FAIL" if malware else "PASS",
                "details": data.get("malwareDescription", "No malware detected.")
            })

            self.results.append({
                "name": "Phishing Activity",
                "status": "FAIL" if phishing else "PASS",
                "details": data.get("phishingDescription", "No phishing detected.")
            })

            self.results.append({
                "name": "Blacklist Check",
                "status": "FAIL" if blacklisted else "PASS",
                "details": "Listed in blacklists." if blacklisted else "Not blacklisted."
            })

        except requests.HTTPError as http_err:
            self.results.append({
                "name": "API Request Error",
                "status": "FAILED",
                "details": f"HTTP error: {http_err} ({response.status_code})"
            })

        except requests.RequestException as e:
            self.results.append({
                "name": "API Request Error",
                "status": "FAILED",
                "details": str(e)
            })

        return self.results


# For standalone test
if __name__ == "__main__":
    checker = ReputationChecker("google.com")
    results = checker.run_checks()
    for r in results:
        print(r)
