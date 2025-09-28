"""
alert_simulation_test.py

Automated alert simulation tests for AutoAudit Prometheus alerting rules.
Simulates synthetic metrics to verify alert firing conditions.

Author: Senior Lead, AutoAudit DevSecOps Team
Last Updated: 2025-09-17

Prerequisites:
- Prometheus test instance running locally or in the test environment.
- Pushgateway or remote write enabled for synthetic metric injection.
- Python 3.8+ with 'requests' library installed.

Usage:
    python3 alert_simulation_test.py
"""

import requests
import time
import sys

#The URLs are placeholders. Please replace them.
PROMETHEUS_URL = "http://localhost:9090"
PUSHGATEWAY_URL = "http://localhost:9091"

def push_metric(metric_name: str, value: float, labels: dict = None):
    
    """
    Pushes a synthetic metric to Prometheus Pushgateway.
    """
    
    labels = labels or {}
    label_str = ",".join(f'{k}="{v}"' for k, v in labels.items())
    
    metric_line = f"{metric_name}{{{label_str}}} {value}\n"
    data = f"# TYPE {metric_name} gauge\n{metric_line}"
    
    response = requests.put(f"{PUSHGATEWAY_URL}/metrics/job/alert_simulation", data=data)
    response.raise_for_status()

def query_prometheus(query: str):
    
    """
    Queries Prometheus HTTP API with the given PromQL query.
    """
    
    response = requests.get(f"{PROMETHEUS_URL}/api/v1/query", params={'query': query})
    response.raise_for_status()
    
    result = response.json()
    
    if result['status'] != 'success':
        raise RuntimeError(f"Prometheus query failed: {result}")
    
    return result['data']['result']

def test_unauthorised_access_attempt():
    
    print("Simulating UnauthorisedAccessAttempt alert condition...")
    
    #Push synthetic failed login attempts > 10 over 5 minutes
    push_metric("auditd_logins_failed_total", 15, {"instance": "test-instance-1"})
    
    time.sleep(10)  #Wait for Prometheus scrape

    results = query_prometheus('sum by (instance) (rate(auditd_logins_failed_total[5m])) > 10')
    assert results, "UnauthorisedAccessAttempt alert did not fire as expected."
    
    print("UnauthorisedAccessAttempt alert simulation passed.")

def test_node_cpu_saturation():
    print("Simulating NodeCPUSaturation alert condition...")
   
    #Push synthetic low idle CPU to simulate saturation
    push_metric("node_cpu_seconds_total", 0.05, {"instance": "node-1", "mode": "idle"})
    time.sleep(10)
    
    query = '100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90'
    results = query_prometheus(query)
    assert results, "NodeCPUSaturation alert did not fire as expected."
    
    print("NodeCPUSaturation alert simulation passed.")

def main():
    
    try:
        test_unauthorised_access_attempt()
        test_node_cpu_saturation()
        print("All alert simulation tests passed successfully.")
    
    except AssertionError as e:
        print(f"Test failed: {e}")
        sys.exit(1)
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(2)

if __name__ == "__main__":
    main()
