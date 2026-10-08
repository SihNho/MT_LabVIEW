---
card: 147-b1-1
status: current
date: 2026-10-08
---
# Brief 147-b1-1 - offline RE-SCORE of the s06 retry end read by the PD356(b) rules (no tool edit)

Offline only. No LabVIEW, camera or motor. NO edit of any file under `tools/` except a new scratch script `tools/bench/diag_c147_b1_1_rescore.py` (yours). `tools/stagekit.py` is read-only here: the gate FIX is the next card's job.

## Background (facts, from the machine)
Retry scratch 147-a1-8 (log `tools/bench/diag_c147_p4s06v18_scratch.log`, whole-file lines from :341; stored reads `tools/bench/diag_c147_p4s06v18_scratch.json`, `real_end_rows` + base rows) failed three END gates with E1 real == sim at every op: D (:652 new wires 15 vs sim 16, lost 7 vs 8), TD (:657), PB (:659, 'missing open pairs 2626|Terminal|array|0..3', FATAL before save). Review `archive/peer/2026-10-08-c147-a1-8-re1.md` says: terminals 2832/4160/4165 on #2626 were renamed 'array'->'element', 9505/9508 on #9503 'Value'->'' (same uid, same owner, still wired), and wire uid 23807 was re-used on the same source t5171. Its open question: why PB lists FOUR missing 'array' rows while only three terminals were renamed (4168 stays 'array').

## The PD356(b) rules to score by (do not implement them in stagekit; apply them in your script on the stored rows)
- TD / PB key: a terminal is identified by (uid, owner). A NAME change is a pass ONLY if the licence file lists that uid (today's licence lists 2832/4160/4165 on node 2626 only, as 'rename_by_uid'; it does NOT yet list the #9503 uids - report what the verdict is with the 5 measured renames listed, and what it is with only today's licence).
- D: a plan-deleted wire uid that is present at the end counts as REUSE-NOTED (not a lost/new mismatch) only if its sources AND sinks equal a wire of the simulator's end state and every sink the simulator removed from it is gone from the real wire.

## To measure
1. Re-run the three scorers on the stored base rows / sim end / real end rows, with the PD356(b) rules above. Find how the existing gates build their inputs (`tools/stagekit.py` `wire_keys` :1360, `term_identity_gates` :1374, `d4_pb` :1458, and the code that logs D at the scratch's :652) by READING them; copy the call shapes, do not infer. Report D, TD, PB verdicts (PASS/FAIL + counts) under both licence variants.
2. PB's '4 missing rows for 3 renamed': trace with `file:line` (stagekit and the scratch log / json row ids) where the fourth missing row comes from (4168? index 0..3 of `2626|Terminal|array|i` pairs?). Say whether the fourth row is a real graph difference or the same key defect.
3. Wire 23807: quote the sources and sinks of 23807 in the BASE read and in the REAL END rows (terminal uids + owner + names), and the sim's end wire with the same source (`tools/bench/sim/ring_p4_s06v18/step_25_wire.json` or the summary). Say whether the sets are equal and which sinks the sim removed.
4. Verdict line: `ALL PASS` (all three scorers under the 5-rename licence) or the first scorer that still fails with its values.

## Report (`tools/bench/diag_c147_b1_1_facts.md`, <= 40 lines)
Verdicts per scorer per licence variant; the PB fourth-row explanation with `file:line`; the 23807 base/end sink lists; the md5 of `tools/stagekit.py`, `stagexec.py`, `gscript.py`, `elrule.py` after (must equal 9a3fceaf / 1bab9cf9 / 1a80236e / a5ee7d5c). `OPEN:` line for anything unsettled. A tool defect is reported with `file:line`, not edited.
