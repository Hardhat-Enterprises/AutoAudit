import re
from .overview import Strategy

class ApplicationControl(Strategy):
    id = "AC"
    name = "Application Control"

    def description(self) -> str:
        return ("Prevent the execution of executables, libraries, scripts, installers and other specific type of files on standard user/temp folders")

    # the common detection AC rules to detect that the files are being enforced or blocked 
    ENFORCE = ["enforce rules", "enforced", "rules are enforced"]
    BLOCK   = ["block", "blocked", "blocking", "deny", "denied", "disallowed", "disallow"]

    # tighten the detection for the keyword "deny" with its variants 
    BLOCK_REGEX = [
        r"\bden[vy]\b",     # denv / deny
        r"\b[dbqgo]eny\b",         # deny / beny / qeny / geny / oeny
        r"\b[a-z]den[vy]\b",       # qdeny
        r"\b[a-z][dbqgo]eny\b",    # qbeny 
    ]

    # Regex to match all the file extensions
    EXT_PATTERNS_BY_LABEL = {
        "EXEC":   [r"\b[\w-]+\s*\.\s*(?:exe|com)\b", r"\b(?:exe|com)\b"],
        "DLL":    [r"\b[\w-]+\s*\.\s*(?:dll|ocx)\b", r"\b(?:dll|ocx)\b"],
        "SCRIPT": [r"\b(?:bat|cmd|js|vbs|ps1|psm1|py|pl|php|scpt|wsf|wsh)\b"],
        "INST":   [r"\b[\w-]+\s*\.\s*(?:msi|msm|msp|mst|idt|cub|pcp)\b",
                   r"\b(?:msi|msm|msp|mst|idt|cub|pcp)\b"],
        "CHM":    [r"\b[\w-]+\s*\.\s*chm\b", r"\bchm\b"],
        "HTA":    [r"\b[\w-]+\s*\.\s*hta\b", r"\bhta\b"],
        "CPL":    [r"\b[\w-]+\s*\.\s*cpl\b", r"\bcpl\b"],
    }

    # labels for each file type
    LABELS = {
        "EXEC": ["executable rules", "executable files",
                 "block executable files", "block executable files from running"],
        "DLL":  ["dll rules", "software library files", "library rules"],
        "SCRIPT": ["script rules", "script files", "obfuscated scripts", "block execution of potentially obfuscated scripts"],
        "INST": ["windows installer rules", "installer rules", "installer files"],
        "CHM":  ["compiled html files", "chm"],
        "HTA":  ["html application files", "hta"],
        "CPL":  ["control panel applet", "control panel applets", "cpl"],
    }

    # rules according to the mapping: test_id, sub_strategy, priority, recommendation, label_key
    RULES = [
        ("ML1-AC-01", "Executables Files must be blocked", "High",
         "(1) Ensure executable files (EXE and COM files) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "EXEC"), 
        ("ML1-AC-02", "Software Library Files must be blocked", "Medium",
         "(1) Ensure software library files (DLL and OCX files) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "DLL"), 
        ("ML1-AC-03", "Unauthorised Scripts must be blocked", "High",
         "(1) Ensure script files (SH, BASH, CSH, KSH, BAT, CMD, JS, VBS, PY, PS1, PL, PHP, SCPT, WSF, OSTS) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "SCRIPT"),
        ("ML1-AC-04", "Installers Files must be blocked", "Medium",
         "(1) Ensure installer files (MSI, MSM, MSP, MST, IDT, CUB and PCP) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "INST"),
        ("ML1-AC-05", "Compiled HTML files must be blocked", "Low",
         "(1) Ensure compiled HTML files (CHM) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "CHM"),
        ("ML1-AC-06", "HTML Application Files (HTA) must be blocked", "Low",
         "(1) Ensure HTML application files (HTA) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "HTA"),
        ("ML1-AC-07", "Control Panel Applet (CPL) Files must be blocked", "Low",
         "(1) Ensure Control panel applet files (CPL) cannot be run from user or temp folders by standard users (2) Use AppLocker or Windows Defender Application Control rules",
         "CPL"),
    ]

    #scan the detected level from the test_id
    @staticmethod
    def _ml_level_from_test_id(test_id: str) -> int | None:
        m = re.match(r"ML(\d+)-", test_id)
        return int(m.group(1)) if m else None

    # main detection logic 
    def emit_hits(self, raw_text: str, source_file: str = "", **kwargs):
        t = self.normalize(raw_text)

        # avoids false positives like blocklist, unblocked etc.
        enforce_hit = self._any_regex(t, [r"\benforc(?:e|ed|ing)\b", r"\brules are enforced\b", r"\benforce rules\b"])
        block_hit   = self._any_regex(t, [r"\bblock(?:ed|ing)?\b"]) or self._any_regex(t, self.BLOCK_REGEX)

        rows = []

        # detection criteria i.e. require (enforce|block) AND (label OR extension)
        for test_id, sub, priority, recommendation, label_key in self.RULES:
            label_hit = self._any_substr(t, self.LABELS[label_key])
            ext_hit   = self._any_regex(t, self.EXT_PATTERNS_BY_LABEL[label_key])

            action_ok   = bool(enforce_hit or block_hit)
            evidence_ok = bool(label_hit or ext_hit)

            # if both are detected = pass output
            if action_ok and evidence_ok:
                evidence = [x for x in (label_hit, ext_hit, enforce_hit, block_hit) if x]
                rows.append({
                    "test_id": test_id,
                    "sub_strategy": sub,
                    "detected_level": self._ml_level_from_test_id(test_id),  # to be extracted from test_id
                    "pass_fail": "Pass",
                    "priority": priority,
                    "recommendation": recommendation,
                    "evidence": evidence
                })

        if rows:
            return rows

        # generic fail output
        return [{
            "test_id": "ML1-AC-01 to ML1-AC-07", # total of all test_ids
            "sub_strategy": "",
            "detected_level": 1,  # from ML1
            "pass_fail": "Fail",
            "priority": "High", # default to be high 
            "recommendation": (
                "(1) Use AppLocker or Windows Defender Application Control rules to block all listed file types "
                "from running in user or temporary folders. "
                "(2) Ensure rules are enforced on all workstations and reviewed periodically (ideally once per quarter)."
            ),
            "evidence": []
        }]

    # iterate each test_id
    def match(self, raw_text: str):
        outs = []
        for r in self.emit_hits(raw_text):
            if r.get("pass_fail") == "Pass":
                lvl = r.get("detected_level")
                outs.append(f"{r['test_id']} (ML{lvl}, {r['priority']}): {r['sub_strategy']} rules have been enforced")
        return outs