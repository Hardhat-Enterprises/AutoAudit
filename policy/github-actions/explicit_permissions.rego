package main

import rego.v1

# Workflows without an explicit permissions declaration rely on the repository
# default GITHUB_TOKEN permissions. A workflow-level declaration applies to all
# of its jobs; otherwise each job must declare its own permissions.
has_permissions(config) if {
	object.get(config, "permissions", null) != null
}

deny contains msg if {
	jobs := object.get(input, "jobs", {})
	not has_permissions(input)
	some name, job in jobs
	not has_permissions(job)
	msg := sprintf("job %q relies on default GITHUB_TOKEN permissions; declare permissions at workflow or job level", [name])
}
