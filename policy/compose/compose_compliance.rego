package main

import rego.v1

# Services need both CPU and memory limits to prevent one container from
# consuming capacity needed by the rest of the local AutoAudit stack.
has_resource_limits(service) if {
	deploy := object.get(service, "deploy", {})
	resources := object.get(deploy, "resources", {})
	limits := object.get(resources, "limits", {})
	memory := object.get(limits, "memory", "")
	cpus := object.get(limits, "cpus", "")
	memory != ""
	cpus != ""
}

# A healthcheck must include a command so Compose can distinguish a running
# container from a service that is ready to receive work.
has_healthcheck(service) if {
	healthcheck := object.get(service, "healthcheck", {})
	test := object.get(healthcheck, "test", [])
	count(test) > 0
}

deny contains msg if {
	some name, service in input.services
	not has_resource_limits(service)
	msg := sprintf("service %q must define deploy.resources.limits.memory and deploy.resources.limits.cpus", [name])
}

deny contains msg if {
	some name, service in input.services
	not has_healthcheck(service)
	msg := sprintf("service %q must define a healthcheck with a test command", [name])
}
