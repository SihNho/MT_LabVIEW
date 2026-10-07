---
type: brief
status: current
date: 2026-10-07
---
# Brief 145-a1-2 — RETRY of 145-a1-1: s04 scratch with SQ1's terminal list corrected

Card 145-a1-1 stopped in op 10 (SQ1 = RingSeqCheck_v0.vi drop) on BINDING: the plan row lists 8 terminals, the real VI has 12
(8 named + 4 unnamed `''` sinks t0, t4, t5, t6). Facts `tools/bench/diag_c145_1_facts.md` (9965456a), review
`archive/peer/2026-10-07-c145-1-sq1-bind.md` (ed55e578, ANSWERED). Cause: the plan row is PROVISIONAL (plan row `why`), the pane was
already measured (`diag_c142_4_facts.md:22-23`, `build_ringseqcheck_v0.log:216-217`: slots 0 and 4-6 free).

## Steps
1. Check inputs (plan 9ff46b0e, pred 90eff870, recipes fe3f630c / f5e4bdf8, s03 282301ca, bed 39511877). Read the failing log lines
   `diag_c144_p4s04v18_scratch.log:228-256` and the measured pane lines named above.
2. Correct ONLY the SQ1 row (`p4_s2_seqcheck`, class SubVI) of `plan_ring_p4_s04v18.json`: add the 4 unnamed sinks (`""`,
   is_source false, term_class Terminal) that the real drop shows, update its `why` (cite the log lines; no longer provisional).
   No other row, op or id changes. Check whether a later op references SQ1 terminals by index; if one does, the index must match
   the measured table (t0.. above), else RETURN.
3. Because a plan byte changed: re-derive what hangs on it with the existing tools only (stagesim end graph, pred EL by the PD349
   rule `prep_c143_3_elrule.py`, X10 incl. the 680 limit, census derivation, recipe pair if they pin the plan md5), then `--dry` and
   `--prerun` PASS on the new bytes and `--scratch-required`. Report old -> new md5 of every file you changed. EL must still be 60
   by the rule (basis stated), peak X10 reported against 680 (PD350(b) accepts the -0.1 MB margin).
4. ONE new scratch on a fresh byte copy of s03 (282301ca), exactly as in brief 145-a1-1 (`brief_145-a1-1.md` cb148... steps for the
   scratch, predictions, census into the pred, adopt by import, fresh load, graph read, EL + expected file, s03 + bed unchanged,
   LabVIEW gone). The earlier broken copy `D1_ring_p4s04_20261007_212230.vi` (abb76d41) and its resume record are NOT used and NOT
   deleted.
5. A stop at MEM 680, a third EL value, or a different binding refusal = RETURN with facts and the JEV-LADDER row; no second scratch.

## Never
- edit stage tools (stagexec / stagekit / stagesim / stage_prerun / gscript) — a prerun check for `subvi_path` create vs pane is NOT part of
  this card (report it as a gap only); a tool fault is a RETURN plus a gate-fp entry;
- launch more than ONE scratch; adopt a file from a run that did not reach full PASS; open the bed or s03 for editing;
- touch s05 files (`plan_ring_p4_s05v18*`, `prep_c145_p1*`) or any motor / camera.
