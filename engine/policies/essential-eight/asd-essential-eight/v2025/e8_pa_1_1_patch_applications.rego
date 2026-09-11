# METADATA
# title: Essential Eight - Patch Applications, Defender current and covered software within weakness threshold
# description: |
#   Checks whether Microsoft Defender's signature is current and real time
#   protection is active on each device, whether each device has reported
#   status within the last 24 hours, and whether covered category software
#   (office productivity, browser, email client, PDF) on each device has
#   no known weaknesses and is not past its vendor end of support date.
#   The 24 hour recency threshold matches AutoAudit's existing default
#   (see E8-BAK-1.1). The weakness threshold of 0 is a judgement call
#   reasoned from ACSC's two-week patch window wording, not an
#   ACSC-mandated figure, since no ACSC guidance prescribes a specific
#   number. UNVERIFIED: DVM software inventory field names and endpoint
#   shape have not been confirmed against a live tenant.
#   Research reference: 26T2-SEC-EG-003, 26T2-SEC-EG-004
# custom:
#   control_id: E8-PA-1.1
#   framework: essential-eight
#   benchmark: asd-essential-eight
#   version: v2025
#   severity: high
#   service: MicrosoftDefender
#   requires_permissions:
#   - DeviceManagementManagedDevices.Read.All
#   - UNVERIFIED (DVM permission, see dvm_client.py)

package essential_eight.asd_essential_eight.v2025.control_e8_pa_1_1

import rego.v1

# Default implementation thresholds. Not ACSC-mandated figures, see METADATA.
RECENT_WINDOW_NS := 24 * 60 * 60 * 1000000000 # 24 hours, matches E8-BAK-1.1

WEAKNESS_THRESHOLD := 0

# --- Defender protection state: current signature, real time protection, recent status ---

devices_signature_overdue := [d |
	some d in input.protection_states
	d.signatureUpdateOverdue == true
]

devices_realtime_protection_disabled := [d |
	some d in input.protection_states
	d.realTimeProtectionEnabled == false
]

devices_stale_status := [d |
	some d in input.protection_states
	d.lastReportedDateTime != null
	reported_ns := time.parse_rfc3339_ns(d.lastReportedDateTime)
	reported_ns < time.now_ns() - RECENT_WINDOW_NS
]

devices_no_status := [d |
	some d in input.protection_states
	d.lastReportedDateTime == null
]

# --- DVM software inventory: no weaknesses above threshold, not unsupported ---

software_exceeding_weakness_threshold := [s |
	some s in input.software_inventory
	s.numberOfWeaknesses != null
	s.numberOfWeaknesses > WEAKNESS_THRESHOLD
]

# UNVERIFIED: exact string value(s) DVM uses for an unsupported status
# have not been confirmed against a live tenant. Matching case
# insensitively against "unsupported" as a placeholder.
software_unsupported := [s |
	some s in input.software_inventory
	s.endOfSupportStatus != null
	status_lower := lower(s.endOfSupportStatus)
	contains(status_lower, "unsupported")
]

# --- Overall compliance ---

is_compliant if {
	count(devices_signature_overdue) == 0
	count(devices_realtime_protection_disabled) == 0
	count(devices_stale_status) == 0
	count(devices_no_status) == 0
	count(software_exceeding_weakness_threshold) == 0
	count(software_unsupported) == 0
}

default is_compliant := false

result := {
	"compliant": is_compliant,
	"message": message,
	"details": {
		"devices_signature_overdue": devices_signature_overdue,
		"devices_realtime_protection_disabled": devices_realtime_protection_disabled,
		"devices_stale_status": devices_stale_status,
		"devices_no_status": devices_no_status,
		"software_exceeding_weakness_threshold": software_exceeding_weakness_threshold,
		"weakness_threshold": WEAKNESS_THRESHOLD,
		"software_unsupported": software_unsupported,
		"total_devices": count(input.protection_states),
		"total_covered_software": count(input.software_inventory),
	},
}

message := "Patch Applications compliant: Defender is current and active on all devices, all recently reported, and covered software has no known weaknesses or unsupported status" if {
	is_compliant
}

message := sprintf(
	"Patch Applications non-compliant: Defender signature overdue on %d device(s)",
	[count(devices_signature_overdue)],
) if {
	count(devices_signature_overdue) > 0
}

message := sprintf(
	"Patch Applications non-compliant: real time protection disabled on %d device(s)",
	[count(devices_realtime_protection_disabled)],
) if {
	count(devices_signature_overdue) == 0
	count(devices_realtime_protection_disabled) > 0
}

message := sprintf(
	"Patch Applications non-compliant: %d device(s) have not reported status within the last 24 hours",
	[count(devices_stale_status) + count(devices_no_status)],
) if {
	count(devices_signature_overdue) == 0
	count(devices_realtime_protection_disabled) == 0
	(count(devices_stale_status) + count(devices_no_status)) > 0
}

message := sprintf(
	"Patch Applications non-compliant: %d covered software item(s) exceed the weakness threshold of %d",
	[count(software_exceeding_weakness_threshold), WEAKNESS_THRESHOLD],
) if {
	count(devices_signature_overdue) == 0
	count(devices_realtime_protection_disabled) == 0
	count(devices_stale_status) == 0
	count(devices_no_status) == 0
	count(software_exceeding_weakness_threshold) > 0
}

message := sprintf(
	"Patch Applications non-compliant: %d covered software item(s) are past vendor end of support",
	[count(software_unsupported)],
) if {
	count(devices_signature_overdue) == 0
	count(devices_realtime_protection_disabled) == 0
	count(devices_stale_status) == 0
	count(devices_no_status) == 0
	count(software_exceeding_weakness_threshold) == 0
	count(software_unsupported) > 0
}

default message := "Unable to evaluate Patch Applications: no protection state or software inventory data available"
