# Sample Benchmark - Control Status

This is a small sample of a controls.md file.

*Last Updated: 2026-01-15*

---

## Summary

| Metric | Count |
|--------|-------|
| **Total Controls** | 9 |
| **CIS Automated** | 8 |
| **CIS Manual** | 1 |

### Our Implementation Status

| Our Audit Type | Count | Description |
|----------------|-------|-------------|
| Automated | 4 | Fully automatable with current collectors |
| Deferred | 1 | Collector works but needs review |
| Blocked | 2 | Authentication issues prevent execution |
| Manual | 1 | No API available |
| Not Started | 1 | No collector implemented yet |

---

## Section 1: Sample Area One

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 1.1.1 | L1 | Ensure sample setting A is enabled | Automated | Automated | `entra.sample.a` | Implemented | Need a collector |
| 1.1.2 | L1 | Ensure sample setting B is reviewed | Automated | Deferred | `entra.sample.b` | Implemented | |
| 1.1.3 | L1 | Ensure sample setting C is enforced | Automated | Blocked | `exchange.sample.c` | Blocked | Needs certificate auth. |
| 1.1.4 | L2 | Ensure sample setting D is configured | Automated | Blocked | | Pending | |
| 1.1.5 | L1 | Ensure sample setting E is documented | Manual | Manual | | N/A | |
| 1.1.6 | L1 | Ensure sample setting F is restricted | Automated | Not Started | | Not Started | Written by hand, left alone |

## Section 2: Sample Area Two

| Control ID | Level | Title | CIS Suggested Audit Type | Our Audit Type | Collector ID | Status | Notes |
|------------|-------|-------|--------------------------|----------------|--------------|--------|-------|
| 2.1.1 | L1 | Ensure sample setting G is set | Automated | Automated | `sharepoint.sample.g` | Implemented | Collector raises NotImplementedError |
| 2.1.2 | L1 | Ensure sample setting H is already correct | Automated | Automated | `sharepoint.sample.h` | Implemented | Same note as the doc. |
| 2.9.9 | L1 | A control that was removed from the metadata | Automated | Automated | `sharepoint.sample.z` | Implemented | |

---

## Implementation Priority

Written by hand. The script does not change this part.
