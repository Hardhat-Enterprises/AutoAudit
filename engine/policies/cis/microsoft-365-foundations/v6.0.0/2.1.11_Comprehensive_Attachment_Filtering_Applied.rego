# METADATA
# title: Ensure comprehensive attachment filtering is applied
# description: |
#   The Common Attachment Types Filter lets a user block known and custom malicious file types
#   from being attached to emails. The policy provided by Microsoft covers 53 extensions
#   and an additional custom list of extensions can be defined.
#  
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-2.1.11
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_2_1_11

<<<<<<< HEAD
import rego.v1
=======
default result := {"compliant": false, "message": "Evaluation failed"}
>>>>>>> c645864 (added all controls for section 2)

attach_exts := [
    "7z","a3x","ace","ade","adp","ani","app","appinstaller","applescript","application",
    "appref-ms","appx","appxbundle","arj","asd","asx","bas","bat","bgi","bz2","cab",
    "chm","cmd","com","cpl","crt","cs","csh","daa","dbf","dcr","deb","desktopthemepackfile",
    "dex","diagcab","dif","dir","dll","dmg","doc","docm","dot","dotm","elf","eml","exe",
    "fxp","gadget","gz","hlp","hta","htc","htm","html","hwpx","ics","img","inf","ins","iqy",
    "iso","isp","jar","jnlp","js","jse","kext","ksh","lha","lib","library-ms","lnk","lzh",
    "macho","mam","mda","mdb","mde","mdt","mdw","mdz","mht","mhtml","mof","msc","msi","msix",
    "msp","msrcincident","mst","ocx","odt","ops","oxps","pcd","pif","plg","pot","potm","ppa",
    "ppam","ppkg","pps","ppsm","ppt","pptm","prf","prg","ps1","ps11","ps11xml","ps1xml","ps2",
    "ps2xml","psc1","psc2","pub","py","pyc","pyo","pyw","pyz","pyzw","rar","reg","rev","rtf",
    "scf","scpt","scr","sct","searchConnector-ms","service","settingcontent-ms","sh","shb",
    "shs","shtm","shtml","sldm","slk","so","spl","stm","svg","swf","sys","tar","theme","themepack",
    "timer","uif","url","uue","vb","vbe","vbs","vhd","vhdx","vxd","wbk","website","wim","wiz",
    "ws","wsc","wsf","wsh","xla","xlam","xlc","xll","xlm","xls","xlsb","xlsm","xlt","xltm","xlw",
    "xnk","xps","xsl","xz","z"
]

passing_value := 0.9

missing_exts[policy_identity] = missing if {
    policy := input.malware_filter_policies[_]
<<<<<<< HEAD
    policy_identity := policy.Identity

    missing := [ext |
        ext := attach_exts[_]
        not ext in policy.FileTypes
=======
    policy_identity := policy.identity

    missing := [ext |
        ext := attach_exts[_]
        not ext in policy.file_types
>>>>>>> c645864 (added all controls for section 2)
    ]
}

is_compliant[policy_identity] if {
    policy := input.malware_filter_policies[_]
<<<<<<< HEAD
    policy_identity := policy.Identity
=======
    policy_identity := policy.identity

    rule := input.malware_filter_rules[_]
    rule.malware_filter_policy == policy.id
>>>>>>> c645864 (added all controls for section 2)

    missing := missing_exts[policy_identity]
    fail_threshold := count(attach_exts) * (1 - passing_value)

    count(missing) <= fail_threshold
<<<<<<< HEAD
    policy.EnableFileFilter == true
=======
    policy.enable_file_filter == true
    rule.state == "Enabled"
}

policy_report[report] if {
    policy := input.malware_filter_policies[_]
    rule := input.malware_filter_rules[_]
    rule.malware_filter_policy == policy.id

    missing := missing_exts[policy.identity]
    compliant := is_compliant[policy.identity]

    report := {
        "policy_name": policy.identity,
        "is_cis_compliant": compliant,
        "enable_file_filter": policy.enable_file_filter,
        "state": rule.state,
        "missing_count": count(missing),
        "missing_extensions": missing,
        "extension_count": count(policy.file_types)
    }
}

any_policy_compliant if {
    some i
    compliant := is_compliant[input.malware_filter_policies[i].identity]
    compliant == true
>>>>>>> c645864 (added all controls for section 2)
}

generate_message(true) := "Attachment filtering policy is correctly configured and enforced"
generate_message(false) := "Attachment filtering policy is misconfigured or not enforced"

generate_affected_resources(true, _) := []

generate_affected_resources(false, data_input) := [
<<<<<<< HEAD
    pol.Identity |
    pol := data_input.malware_filter_policies[_]
]

policies := object.get(input, "malware_filter_policies", [])
has_policies := count(policies) > 0

non_compliant_policies := [
    pol.Identity |
    pol := policies[_]
    not is_compliant[pol.Identity]
]

result := {
    "compliant": false,
    "message": "No malware filter policies found",
    "affected_resources": ["MalwareFilterPolicy"],
    "details": {
        "malware_filter_policies_evaluated": 0,
        "passing_threshold": passing_value,
        "total_known_extensions": count(attach_exts)
    }
} if {
    not has_policies
}

result := {
    "compliant": count(non_compliant_policies) == 0,
    "message": generate_message(count(non_compliant_policies) == 0),
    "affected_resources": generate_affected_resources(count(non_compliant_policies) == 0, input),
    "details": {
        "malware_filter_policies_evaluated": count(policies),
        "non_compliant_policies": non_compliant_policies,
        "passing_threshold": passing_value,
        "total_known_extensions": count(attach_exts)
    }
} if {
    has_policies
=======
    pol.identity |
    pol := data_input.malware_filter_policies[_]
]

result := {
    "compliant": any_policy_compliant,
    "message": generate_message(any_policy_compliant),
    "affected_resources": generate_affected_resources(any_policy_compliant, input),
    "details": {
        "malware_filter_policies_evaluated": count(input.malware_filter_policies),
        "malware_filter_rules_evaluated": count(input.malware_filter_rules),
        "passing_threshold": passing_value,
        "total_known_extensions": count(attach_exts)
    }
>>>>>>> c645864 (added all controls for section 2)
}
