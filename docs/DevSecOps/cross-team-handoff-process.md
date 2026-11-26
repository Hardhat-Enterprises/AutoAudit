# Cross-team handoff process

**Owner:** DevSecOps (B. Holloway, S. Duzevich) | **Status:** Living document, T3 2026 | **Created:** 21 Nov 2026
**Related:** `.github/ISSUE_TEMPLATE/cross-team-handoff.md`, decision note 26T3-DEC-BH-013

## 1. Why this exists

AutoAudit is split into subgroups, and a finding often lands with a team that does not own the affected code. For example, DevSecOps finds vulnerable dependencies in `backend-api`, but the Backend team owns the fix. This process gives a consistent, traceable way to hand work across, so details are not lost in chat and nobody has their workload set for them.

The team rule it builds on: the subgroup that owns the code fixes it. The group that finds the problem advises and tracks.

## 2. When to use it

Use it when you find something that:
- needs work in code another subgroup owns, and
- is safe to describe publicly (see section 6).

Don't use it for tasks inside your own subgroup, or for questions that a quick chat message can settle.

## 3. The steps

1. **Write a GitHub issue** using the "Cross-team handoff" template: what is wrong, where, why it matters, a suggested fix if you have one, how you found it, and who to contact.
2. **Add area labels** for the receiving team (for example `area: backend-api`, `area: engine`), and remove labels for your own team if the issue isn't yours.
3. **Create a Planner card** for the receiving team, with the GitHub issue number in the title (Planner only searches titles). Put the details or a link in the notes.
4. **Post in the AutoAudit chat:** mention the receiving team lead, link the issue, and add one line on why it matters and what urgency you suggest.
5. **Receiving lead acknowledges** and assigns an owner, or handles it however their team handles work.
6. **Follow up** if there is no reply after a few days.

## 4. Conventions

- **Suggest urgency, don't set it.** The receiving team owns its own workload. Say what you think matters and why, and let them decide.
- **Leave the Planner card unassigned.** The usual rule is never to assign other people. The receiving lead assigns the owner. Say so in the card notes so it doesn't look like an orphan.
- **One issue per problem.** Group related findings in one issue only if the same people will fix them together.
- **Keep the issue the source of truth** and link to it from the card, chat message and any PRs.
- **Close the loop.** When the fix merges, comment on the issue and tell the original reporter.

## 5. Planner card title and notes

Title: `[Task ID] – [Clear action] (GitHub #NNN)`

Notes should cover: what, why it matters, suggested fix, suggested urgency, what "done" looks like, who is waiting for an owner, and who to ask for questions.

## 6. What must NOT go in a public issue

Anything that would help an attacker or expose a secret. This repository is public. Report these privately to the relevant team lead in Teams instead:
- credentials, keys, tokens (post where they are, never the value)
- exploitable vulnerability detail in AutoAudit's own code
- CVE-level detail beyond what the issue needs

Package names and versions are fine, since lockfiles are already public.

## 7. Chat message template

> Hi @[lead] :) Handing over issue #[N]: [one-line summary]. Suggested urgency (your call): [when]. I'll put a Planner card on your board linking the issue. Could you acknowledge and assign an owner when you can? Happy to help if anything is unclear.

## 8. Worked example: issue #432

Grype reported 19 Critical dependency findings on `main`, all with fixes available. DevSecOps added a per-lockfile breakdown (Backend owned most of it, Engine owned its transitive copies), relabelled the issue, created one Planner card per receiving team, and pinged the Backend and Engine leads in the AutoAudit chat with suggested urgency. Lesson learned: check which lockfile each package actually lives in before deciding who owns it.

## 9. Lessons learned (add as we go)

- Check whether an issue already exists before creating a new one.
- Which team owns a package depends on which manifest or lockfile declares it, not on which team found it.
- A real vulnerability in our own code goes to the team lead privately, not into a public issue.

## 10. To tidy at end of trimester

Link this document from `docs/GETTING_STARTED.md` and `CONTRIBUTING.md`, and update the current subgroup leads.
