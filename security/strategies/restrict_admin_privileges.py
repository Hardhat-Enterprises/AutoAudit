import re
from .overview import Strategy

class RestrictAdminPrivileges(Strategy):
    id = "RAP"
    name = "Restrict Admin Privileges"
    def description(self) -> str:
        return "Privileged access to systems and applications are validated when requested and follow a proper procedure"

    # the common detection RAP rules to detect that the files are being enforced or blocked 
    ACTION_ENFORCE_RE = [
        r"\benforc(?:e|ed|ing)\b",
        r"\brules are enforced\b",
        r"\benforce rules\b",
        r"\brequir(?:e|ed|es)\b",
        r"\bapprov(?:al|e|ed|ing)\b",
        r"\bjustification\b",
        r"\bticket\b",
        r"\bworkflow\b",
        r"\bpim\b",  # Privileged Identity Management
    ]

    # the set of regex patterns based on testing 
    ACTION_BLOCK_RE = [
        r"\bblock(?:ed|ing)?\b",
        r"\bden(?:y|ied)\b",       # deny/denied
        r"\bden[vy]\b",            # denv
        r"\b[dbqgo]eny\b",         # beny/qeny/qdeny/qbeny
        r"\b[a-z]den[vy]\b",       # qdeny
        r"\b[a-z][dbqgo]eny\b",    # qbeny
        r"\baccess\s+denied\b",
        r"\bpolicy\s+violation\b",
        r"\byou\s+don'?t\s+have\s+permission\b",
        r"\berr[_-]?blocked[_-]?by[_-]?administrator\b",
        r"\bblocked\s+by\s+(?:your\s+)?administrator\b",
        r"\bnot\s+authori[sz]ed\b",
        r"\bfor\s+administrative\s+use\s+only\b",
    ]

    # labels for each file type
    LABELS = {
        "PROCESS": [
            "privileged access process", "approval workflow", "rbac",
            "role based access control", "access control", "privileged access",
            "privileged identity management", "authentication administrator",
            "privileged access request", "approval request", "access request",
            "access approval", "require justification", "require ticket information", "require approval",
        ],
        "NO_INTERNET": [
            "privileged account", "admin account", "firewall",
            "internet blocked", "block internet access", "url filtering",
            "your administrator has blocked this action", "err_blocked_by_administrator",
            "policy violation", "you dont have permission to access", "block incoming connections",
            "firewall active",
        ],
        "NO_MAILBOX": [
            "privileged account", "admin account", "mailbox permission",
            "no mailbox", "mailbox not found", "email address: (none)", "access denied",
        ],
        "ADMIN_ENV": [
            "privileged access workstation", "paw", "admin workstation",
            "admin network", "privileged network", "for administrative use only",
            "not authorised", "no authorization", "no authorisation", "no access",
        ],
        "DENY_UNPRIV_LOGON": [
            "group policy objects", "security settings",
            "deny logon locally", "deny log on through remote desktop services",
            "deny access", "access denied",
            "everyone", "domain users", "authenticated users", "authorised users",
        ],
        "PSREMOTE_DISABLED": [
            "get-pssessionconfiguration", "microsoft.powershell",
            "accessdenied", r"builtin\\administrators accessallowed",
            "remote management users: (no members", "winrm service: disabled",
        ],
        "DENY_PRIV_TO_WORKSTATIONS": [
            "user rights assignment", "local security policy",
            "domain admins", "enterprise admins",
            "deny logon locally", "deny log on through remote desktop services", "deny",
        ],
        "NO_ESCALATION": [
            "runas", "runas error", "logon failure", "access is denied",
            "user account control", "administrator credentials required",
            "an administrator has blocked", "whoami /groups",
            "not a member of administrators", "this operation requires elevation",
            "winrm access denied",
        ],
    }

    # rules according to the mapping: test_id, sub_strategy, priority, recommendation, label_key
    RULES = [
        ("ML1-RA-01", "Formal privileged access process is enforced", "High",
         "(1) Enforce a documented approval workflow for privileged access (2) Maintain an inventory of systems/applications requiring privileged access",
         "PROCESS"),
        ("ML1-RA-02", "Privileged accounts cannot access the Internet", "High",
         "(1) Configure Group Policy Objects (GPO) / firewall to block privileged accounts from internet browsing (2) Enforce technical controls (proxy/firewall) to prevent privileged accounts from bypassing restrictions (3) Regularly review policies",
         "NO_INTERNET"),
        ("ML1-RA-03", "Privileged accounts are not configured with mailboxes and email addresses", "Medium",
         "(1) Remove mailboxes from privileged accounts (2) Review privileged account regularly to confirm no mailbox/email licenses are assigned",
         "NO_MAILBOX"),
        ("ML1-RA-04", "Administrative activities occur in a separate admin environment", "Medium",
         "Ensure privileged accounts cannot be used on standard desktops except via separate environment",
         "ADMIN_ENV"),
        ("ML1-RA-05", "Unprivileged accounts must not be able to logon to systems in the privileged environment", "Medium",
         "Configure GPO to deny logon for unprivileged accounts on servers/admin systems (2) Audit AD groups with RDP access and restrict membership",
         "DENY_UNPRIV_LOGON"),
        ("ML1-RA-06", "Unprivileged user prevented from using the PowerShell remote PSRemote windows feature", "Medium",
         "Remove unprivileged accounts from “Remote Management Users",
         "PSREMOTE_DISABLED"),
        ("ML1-RA-07", "Privileged accounts cannot log on to standard workstations", "High",
         "Apply GPO settings to deny interactive/RDP logon to workstations for privileged accounts",
         "DENY_PRIV_TO_WORKSTATIONS"),
        ("ML1-RA-08", "An unprivileged account logged into a standard user workstation cannot raise privileges to a privileged user", "Low",
         "(1) Disable “runas” and escalation options for unprivileged users (2) Monitor failed privilege escalation attempts in logs (3) Enforce User Account Control (UAC) for all users",
         "NO_ESCALATION"),
    ]

    @staticmethod
    def _ml_level_from_test_id(test_id: str) -> int | None:
        m = re.match(r"ML(\d+)-", test_id)
        return int(m.group(1)) if m else None

    def emit_hits(self, raw_text: str, source_file: str = "", **kwargs):
        t = self.normalize(raw_text)

        enforce_hit = self._any_regex(t, self.ACTION_ENFORCE_RE)
        block_hit   = self._any_regex(t, self.ACTION_BLOCK_RE)

        rows = []
        for test_id, sub, priority, recommendation, label_key in self.RULES:
            label_hit = self._any_substr(t, self.LABELS[label_key])

            action_ok   = bool(enforce_hit or block_hit)
            evidence_ok = bool(label_hit) 

            if action_ok and evidence_ok:
                evidence = [x for x in (label_hit, enforce_hit, block_hit) if x]
                rows.append({
                    "test_id": test_id,
                    "sub_strategy": sub,
                    "detected_level": self._ml_level_from_test_id(test_id),
                    "pass_fail": "Pass",
                    "priority": priority,
                    "recommendation": recommendation,
                    "evidence": evidence
                })

        if rows:
            return rows

        # generic fail output
        return [{
            "test_id": "ML1-RA-01 to ML1-RA-08",
            "sub_strategy": "",
            "detected_level": 1,
            "pass_fail": "Fail",
            "priority": "High",
            "recommendation": (
                "- Enforce a formal, documented approval workflow for privileged access (ticket, justification, approver).\n"
                "- Maintain an inventory of systems/applications requiring privileged access.\n"
                "- Prevent privileged accounts from Internet access and from being used on standard desktops.\n"
                "- Remove mailboxes from privileged accounts.\n"
                "- Deny unprivileged logons to admin systems and prevent privilege escalation (UAC, remove runas paths).\n"
                "- Restrict PowerShell Remoting to admins; keep WinRM appropriately configured."
            ),
            "evidence": []
        }]

    # iterate each test_id
    def match(self, raw_text: str):
        outs = []
        for r in self.emit_hits(raw_text):
            if r.get("pass_fail") == "Pass":
                lvl = r.get("detected_level")
                outs.append(f"{r['test_id']} (ML{lvl}, {r['priority']}): {r['sub_strategy']} is enforced")
        return outs
