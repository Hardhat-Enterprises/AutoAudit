package main

import rego.v1

complete_service := {
	"deploy": {
		"resources": {
			"limits": {
				"memory": "256M",
				"cpus": "0.5",
			},
		},
	},
	"healthcheck": {
		"test": ["CMD", "service", "health"],
	},
}

test_complete_service_is_compliant if {
	messages := deny with input as {"services": {"api": complete_service}}
	count(messages) == 0
}

test_missing_resource_limits_is_reported if {
	service := object.remove(complete_service, ["deploy"])
	messages := deny with input as {"services": {"db": service}}
	`service "db" must define deploy.resources.limits.memory and deploy.resources.limits.cpus` in messages
	count(messages) == 1
}

test_missing_memory_limit_is_reported if {
	service := {
		"deploy": {
			"resources": {
				"limits": {
					"cpus": "0.5",
				},
			},
		},
		"healthcheck": {
			"test": ["CMD", "service", "health"],
		},
	}
	messages := deny with input as {"services": {"redis": service}}
	`service "redis" must define deploy.resources.limits.memory and deploy.resources.limits.cpus` in messages
	count(messages) == 1
}

test_missing_healthcheck_is_reported if {
	service := object.remove(complete_service, ["healthcheck"])
	messages := deny with input as {"services": {"worker": service}}
	`service "worker" must define a healthcheck with a test command` in messages
	count(messages) == 1
}

test_empty_healthcheck_test_is_reported if {
	service := object.union(complete_service, {
		"healthcheck": {
			"test": [],
		},
	})
	messages := deny with input as {"services": {"worker": service}}
	`service "worker" must define a healthcheck with a test command` in messages
	count(messages) == 1
}

test_disabled_healthcheck_is_reported if {
	service := object.union(complete_service, {
		"healthcheck": {
			"test": ["NONE"],
		},
	})
	messages := deny with input as {"services": {"worker": service}}
	`service "worker" must define a healthcheck with a test command` in messages
	count(messages) == 1
}

test_incomplete_healthcheck_command_is_reported if {
	service := object.union(complete_service, {
		"healthcheck": {
			"test": ["CMD"],
		},
	})
	messages := deny with input as {"services": {"worker": service}}
	`service "worker" must define a healthcheck with a test command` in messages
	count(messages) == 1
}
