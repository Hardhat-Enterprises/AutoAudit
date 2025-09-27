import requests
import base64
import os

VIRUSTOTAL_API_URL = "https://www.virustotal.com/api/v3/urls"
VIRUSTOTAL_API_KEY = os.environ["VIRUSTOTAL_API_KEY"]

def get_virustotal_url_report(domain):
    try:
        # Step 1: Encode the actual domain or full URL 
        url = domain.strip()  
        encoded_url = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        # Step 2: Setup headers and make request
        headers = {"x-apikey": VIRUSTOTAL_API_KEY}
        response = requests.get(f"{VIRUSTOTAL_API_URL}/{encoded_url}", headers=headers)

        # Step 3: Interpret response
        if response.status_code == 200:
            data = response.json()
            stats = data["data"]["attributes"]["last_analysis_stats"]
            total = sum(stats.values())
            malicious = stats.get("malicious", 0)

            return {
                "name": "Not a suspected malware provider",
                "status": "PASS" if malicious == 0 else "FAIL",
                "details": f"{malicious} out of {total} scanners flagged this domain."
            }
        else:
            return {
                "name": "Not a suspected malware provider",
                "status": "ERROR",
                "details": f"VirusTotal API error: {response.status_code} - {response.text}"
            }
    except Exception as e:
        return {
            "name": "Not a suspected malware provider",
            "status": "ERROR",
            "details": f"Exception occurred: {str(e)}"
        }

if __name__ == "__main__":
    domain = "https://google.com"
    result = get_virustotal_url_report(domain)

    if isinstance(result, list):
        for item in result:
            print(item)
    else:
        print(result)
