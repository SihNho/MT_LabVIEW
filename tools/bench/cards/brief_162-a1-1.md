---
card: 162-a1-1
status: current
date: 2026-10-10
---
# Brief 162-a1-1 - P5-2 STEP-2 SCRATCH (ONE run), adopt as `D1_ring_p5s02b_<ts>.vi`, add ONE `load_by_vi` entry, record the measured census into the pred; the ONE LabVIEW card

This is `tools/bench/cards/brief_161-b3-1.md` again (read it, and through it brief_158-a3-2 / 158-a2-2 / 156-a2-1 / 155-a3-1 / 155-a3-2 / 154-a3-3 / 3b) with ONLY the deltas below.
Card 161-b3-1 was never dispatched (handed back before launch), so nothing in the repo is left from it. Cycle 161 items 0-6 are accepted and are NOT redone
(`tools/bench/cards/assign_result_161_3.json:13-19`, facts `tools/bench/diag_c161_b2_1_facts.md`): PB, X10, dry, prerun, `--check-launch`, `--scratch-required` rc 3.

## Deltas against brief_161-b3-1
1. **Names:** every `c161` / `161-b3-1` name becomes `c162` / `162-a1-1`. Scratch log `tools/bench/diag_c162_p5s02b_scratch.log`; facts `tools/bench/diag_c162_a1_1_facts.md`; helper scripts
   `diag_c162_a1_1_*` / `prep_c162_a1_1_*` (copy by CALLING the shared functions; if you copy a helper, say which lines changed). The launch command is brief_161's with the new log name and
   `--unverified-card tools/bench/cards/task_162-a1-1.json`.
2. **Pre-checks, read only:** re-hash the inputs of this card IN THE MAIN TREE. All must equal the card. If one differs, explain it in the facts BEFORE any launch (a pin drift of a frozen
   self-test is explained and is not a RETURN; a differing stagekit / plan / pred / licence / EL / recipe md5 is a RETURN). Do NOT redo PB, X10, dry or prerun; run only
   `--check-launch` and `--scratch-required` on the final command text, expecting ALLOW and rc 3 as in `diag_c161_b2_1_facts.md`.
3. **ONE scratch** on a NEW byte copy of the adopted p5s02a file 94ffff94 (`claudeDev\D1_ring_p5s02a_20261010_023239.vi`, never edited). Quote the `SCRATCH-` peak line (`tools/stagekit.py:2841`) and the
   `GATE MEM:` line (`:2845`): peak <= 675 and every BLOCK gate PASS. **Any BLOCK gate FAIL, or a peak above 675, = RETURN with the facts: no adopt, no second run, the copy kept and never loaded.**
   CEN2 is UNPREDICTED (DRY-UNVERIFIED-OK): quote its measured per-class numbers as the measurement.
4. **`tools/bench/memory_model.json` (named by the purpose, ONE entry):** only after a structural PASS and adoption, add exactly ONE `load_by_vi` key = the adopted file's md5 (hashlib), in the
   format of the existing entries (`value` = the post-load MB that the load log line prints, `vi`, and a cite to that log line). Write it with a script that loads the JSON, adds the key and dumps.
   Then compare old vs new by JSON compare: the only difference is the one new key; `fail_above_mb` stays 680.0, `memstop_mb`, `formula`, `start_mb` and every other key are equal. Quote the compare.
   No other file of the memory model is touched.
5. **Adopt, Error List, graph, pred census:** as brief_161-b3-1 items 5 and 6 (adopted path + md5 on one line; Error List total and per class; item-by-item against
   `errorlist_predicted_D1_ring_p5s02b_end.json` 79ec3207, with the unpredicted A32 `w_gr` / A39 `w_hr` named and the differences listed; graph json + md5; measured census into
   `plan_ring_p5s02b_pred.json` by a script that cites the graph reads, census keys only, old -> new md5).
6. **End of card:** s09 eb1d0f31, P5-1 7f2582ae and 94ffff94 hashed unchanged with hashlib; no original opened; LabVIEW closed and verified gone (`tasklist`).
   No `tools/hooks/**` edit, no recipe / plan / licence / EL / stage-tool edit, no motor or camera. Concurrent cards: none.

## Report `tools/bench/diag_c162_a1_1_facts.md` (<= 45 lines)
Pre-check lines (hashes, `--check-launch`, `--scratch-required`); the `SCRATCH-` peak and `GATE MEM` lines; gates per op class; E1 per checkpoint; per-op + final measured census; adopted file
+ md5 + load MB; Error List total + per class + item diff vs 79ec3207; graph json + md5; the memory-model compare; pred old -> new md5 + key diff; invariants; LabVIEW gone. `OPEN:` lines
(measurements only). Dispatch a hypothesis peer only if a gate FAILS.
