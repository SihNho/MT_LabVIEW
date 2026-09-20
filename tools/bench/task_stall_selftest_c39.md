A self-test gate failed and I claim the failure is in the TEST, not in the code under test. Attack that claim.

CONTEXT: `tools/lv_stallcheck.ps1` is a watchdog that writes a gating record `tools/bench/stall_pid<N>.log` when it believes a LabVIEW client is stalled. Its measured precision is 0 of 6 — all six records were written while the job was alive and finished normally, and each record blocks the next build until a paid peer review clears it. The authorised repair is ONE line at `tools/lv_stallcheck.ps1:273`: write the record ONLY when the dialog check returns `VERDICT: BLOCKED`; otherwise `$record` is set to the string `NOT WRITTEN - the dialog check did not return VERDICT: BLOCKED ...`.

OBSERVED in `tools/bench/repair_c39_stall_selftest.log`: 4 PASS / 4 FAIL. Lines `:48-:49` directly measured both behaviours of the repaired line — a clear run left NO record on disk, and a `MODAL DIALOG PRESENT` run DID write one carrying `STALL:` and `dialog: MODAL DIALOG PRESENT`. The four FAILs are gates G2/G3/G7/G8, whose assertion looked for an UPPER-CASE marker while, with no record written, the marker survives only inside the advisory message as a LOWER-CASED bgrun job-log name. Verbatim: `-> FAIL G7 'no modal dialog' writes NO gating record (the leaf IS still flagged in the message) | flagged=False, record_exists=False; message says NOT WRITTEN`.

MY CLAIM, which you should try to break: the repair is correct as measured at `:48-:49`, and G2/G3/G7/G8 failed on their own case-sensitive assertion string, not on the watchdog's behaviour.

ALREADY RULED OUT: simply re-running the fixed self-test — the case fix is applied, but `guard_peer` refuses the launch while this failing log is the newest record. That is why you are being asked.

QUESTIONS:
1. Give the strongest reading under which G7's `flagged=False` is a REAL defect of the repaired watchdog rather than of the assertion: if a leaf is no longer flagged when there is no modal dialog, has the repair silently removed a capability the watchdog was meant to keep?
2. Name one way the `:48-:49` observation can be true and the repair still wrong in production — in particular any path where `$record` is consumed as a FILE PATH after being set to the string `NOT WRITTEN - ...`.
3. What is the cheapest test that discriminates "assertion bug" from "repair bug" WITHOUT running LabVIEW?
