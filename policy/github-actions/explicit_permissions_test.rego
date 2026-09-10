package main

import rego.v1

test_workflow_permissions_are_compliant if {
	messages := deny with input as {
		"permissions": {"contents": "read"},
		"jobs": {"lint": {"runs-on": "ubuntu-latest"}},
	}
	count(messages) == 0
}

test_job_permissions_are_compliant if {
	messages := deny with input as {
		"jobs": {
			"lint": {
				"permissions": {"contents": "read"},
			},
		},
	}
	count(messages) == 0
}

test_empty_job_permissions_are_compliant if {
	messages := deny with input as {
		"jobs": {
			"quick-job": {
				"permissions": {},
			},
		},
	}
	count(messages) == 0
}

test_missing_permissions_are_reported if {
	messages := deny with input as {
		"jobs": {
			"lint": {"runs-on": "ubuntu-latest"},
		},
	}
	`job "lint" relies on default GITHUB_TOKEN permissions; declare permissions at workflow or job level` in messages
	count(messages) == 1
}

test_each_unconfigured_job_is_reported if {
	messages := deny with input as {
		"jobs": {
			"lint": {"runs-on": "ubuntu-latest"},
			"test": {"runs-on": "ubuntu-latest"},
		},
	}
	count(messages) == 2
}
