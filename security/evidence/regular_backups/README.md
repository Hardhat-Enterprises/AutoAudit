\# Regular Backups — sample evidence



Use these files with the Evidence Scanner.



| File | Purpose | Expected test(s) | Result |

|---|---|---|---|

| backup\_success.txt | Recent backup | ML1-RB-01 | PASS |

| backup\_failed.txt | No recent backup | ML1-RB-01 | FAIL |

| offsite\_backup.txt | Offsite or immutable | ML1-RB-02 | PASS |

| restore\_test.txt | Restore tested | ML1-RB-03 | PASS |

| Restore\_failed.txt | Restore failed | ML1-RB-03 | FAIL |

| Encrypted\_backup.txt | Encrypted backups | ML1-RB-05 | PASS |

| access\_admin\_only.txt | Access restricted | ML1-RB-06 | PASS |

| repo\_audit\_pass.txt | Only backup-admins succeeded | ML2-RB-01 | PASS |

| repo\_audit\_fail.txt | Non-member succeeded | ML2-RB-01 | FAIL |

| restore\_report\_ml2\_pass.txt | Common point restore success | ML2-RB-02 | PASS |

| restore\_report\_ml2\_fail.txt | Restore test failed | ML2-RB-02 | FAIL |

| policy\_ml2\_pass.txt | Retention + immutability enforced | ML2-RB-03 | PASS |

| policy\_ml2\_fail.txt | Immutability disabled | ML2-RB-03 | FAIL |



