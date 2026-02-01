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

import rego.v1

default result := {"compliant": false, "message": "Evaluation failed"}

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

policy := object.get(input, "default_policy", null)
has_policy := policy != null

enable_file_filter := object.get(policy, "EnableFileFilter", object.get(input, "enable_file_filter", null))
file_types := object.get(policy, "FileTypes", object.get(input, "file_types", []))

missing := [ext | ext := attach_exts[_]; not ext in file_types]
fail_threshold := count(attach_exts) * (1 - passing_value)
coverage_ok := count(missing) <= fail_threshold

compliant := true if {
    has_policy
    enable_file_filter == true
    coverage_ok
} else := false if { true }

result := {
    "compliant": compliant,
    "message": generate_message(compliant, has_policy),
    "affected_resources": generate_affected_resources(compliant, has_policy),
    "details": {
        "EnableFileFilter": enable_file_filter,
        "missing_count": count(missing),
        "missing_extensions": missing,
        "passing_threshold": passing_value,
        "known_extensions_count": count(attach_exts)
    }
}

generate_message(true, _) := "Comprehensive attachment filtering is applied and covers the expected set of extensions."
generate_message(false, false) := "No malware filter policy (default_policy) was found to evaluate attachment filtering."
generate_message(false, true) := "Comprehensive attachment filtering is not applied or does not cover enough extensions."

generate_affected_resources(true, _) := []
generate_affected_resources(false, _) := ["MalwareFilterPolicy"]
