# METADATA
# title: Ensure mailbox audit actions are configured
# description: |
#   Mailbox auditing should capture comprehensive audit actions for Admin,
#   Delegate, and Owner operations. The default audit actions may not cover
#   all necessary activities for security investigations and compliance.
# related_resources:
# - ref: https://www.cisecurity.org/benchmark/microsoft_365
#   description: CIS Microsoft 365 Foundations Benchmark
# custom:
#   control_id: CIS-6.1.2
#   framework: cis
#   benchmark: microsoft-365-foundations
#   version: v6.0.0
#   severity: medium
#   service: Exchange
#   requires_permissions:
#   - Exchange.Manage

package cis.microsoft_365_foundations.v6_0_0.control_6_1_2

default result := {"compliant": false, "message": "Evaluation failed"}

# Required audit actions per CIS benchmark
required_admin_actions := {"ApplyRecord", "Copy", "Create", "FolderBind", "HardDelete", "Move", "MoveToDeletedItems", "SendAs", "SendOnBehalf", "SoftDelete", "Update", "UpdateCalendarDelegation", "UpdateFolderPermissions", "UpdateInboxRules"}
required_delegate_actions := {"ApplyRecord", "Create", "FolderBind", "HardDelete", "Move", "MoveToDeletedItems", "SendAs", "SendOnBehalf", "SoftDelete", "Update", "UpdateFolderPermissions", "UpdateInboxRules"}
required_owner_actions := {"ApplyRecord", "Create", "HardDelete", "MailboxLogin", "Move", "MoveToDeletedItems", "SoftDelete", "Update", "UpdateCalendarDelegation", "UpdateFolderPermissions", "UpdateInboxRules"}

# Check if a mailbox has required audit actions
mailbox_has_required_actions(mailbox) if {
    admin_actions := {a | some a in mailbox.AuditAdmin}
    delegate_actions := {a | some a in mailbox.AuditDelegate}
    owner_actions := {a | some a in mailbox.AuditOwner}

    count(required_admin_actions - admin_actions) == 0
    count(required_delegate_actions - delegate_actions) == 0
    count(required_owner_actions - owner_actions) == 0
}

result := output if {
    mailboxes := input.mailboxes
    total := count(mailboxes)

    # Find non-compliant mailboxes
    non_compliant := [m.UserPrincipalName | some m in mailboxes; not mailbox_has_required_actions(m)]

    compliant := count(non_compliant) == 0

    output := {
        "compliant": compliant,
        "message": generate_message(total, non_compliant),
        "affected_resources": non_compliant,
        "details": {
            "total_mailboxes": total,
            "compliant_mailboxes": total - count(non_compliant),
            "non_compliant_mailboxes": count(non_compliant)
        }
    }
}

generate_message(total, non_compliant) := msg if {
    count(non_compliant) == 0
    msg := sprintf("All %d mailbox(es) have required audit actions configured", [total])
}

generate_message(total, non_compliant) := msg if {
    count(non_compliant) > 0
    msg := sprintf("%d of %d mailbox(es) are missing required audit actions", [count(non_compliant), total])
}
