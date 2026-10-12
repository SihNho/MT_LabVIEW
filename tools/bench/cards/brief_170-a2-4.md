---
card: 170-a2-4
status: current
date: 2026-10-13
---
# Brief 170-a2-4 (assignment 170-2) - PD410(c)+PD409(b): extend `m8b_replay_compare` (DISTINCT, MATCH, drop signature, cal field rule, other files) and self-test it on 110-7

Plan: `docs/d1/ring-p6.md` PD409(b) (lines 246-253), PD410(c) (301-309), PD409(f) self-test sentence (277-280). OFFLINE: no LabVIEW, no hardware, no motor. Python only.

## Build
1. Extend `tools/bench/m8b_replay_compare.py` (shared module; `tra`, `cal`, `main` stay and are CALLED, not copied). New functions in the same file, each with a scope-correct docstring line and a self-test
   (`py tools/bench/m8b_replay_compare.py --selftest`) that replays the stored 110-7 runs. Do not break the existing CLI `<run_dir_a> <run_dir_b> [--out]`.
2. What the compare reports (every item PASS/FAIL or a count, as a FACT; nothing is re-run or diagnosed):
   - (b) X/Y/Z bit-identical per row by f64 bits; NaN cells counted and the number of FINITE cells compared per bead reported; tra column 0 (time) excluded.
   - (b) `.cal`: whole-file byte compare, then the differing bytes mapped to the date/time field. The field offset/length come from the WALK of each file (`walk()` at
     `tools/bench/diag_c170_a2_1_cal.py:79-113`, rule in `p6_replay_facts.md` F4 lines 97-103), CALLED not copied: if it is not importable from there without side effects,
     EXTRACT it into the compare module (or a small shared module) with a self-test, switch `diag_c170_a2_1_cal.py` to the shared copy ONLY IF that file is inside this card's write globs (it is), and cite old and new file:line.
     Report: field offset, length, text per file; bytes differing outside the field (count + first offset) = a FACT returned, not diagnosed.
   - (b) trans/rot: report the boundary of the init segment (the first row after S1's LAST row where trans or rot changes from the previous row; report the row number); in the stationary segment (rows from the boundary) trans/rot bit-identical, count of rows differing;
     in the init segment every B-side row's trans/rot finite (count non-finite), inside the motor envelope (take the envelope constants from `tools/motor_gate.py` with file:line; if no single envelope is found there, report the envelope check as NOT-EVALUATED with the reason - do not invent numbers), and the init sequence's first and last values equal to A's (reported).
   - (b) every OTHER file in each run dir (name, size, md5) listed and compared by name (md5 equal / differ / only in one dir); none skipped.
   - (c) DISTINCT: for each compared row i, S1 (side A) row i differs bitwise in >= 1 FINITE X/Y/Z cell from each of A rows i+1..i+D; D is a parameter `--slots D` (default none: the run refuses without it). Report the count of rows passing and the first failing row.
     D = the ring's slot count: read it from the P6 graph `tools/bench/graph_ring_p6_20261012_212645.json` (md5 fbc7b7ee) by uid and quote the uid with file:line (PD379 / `ring-p4b.md:21` say 20 slots, counter mod 20: confirm in the graph, do not just copy the number).
   - (c) MATCH: all compared rows' X/Y/Z bit-identical (count of rows not identical). On the first mismatch: the row i and, for every d in 1..D, whether B row i == A row i+d (the drop signature), as a list of d values.
   - Counters as facts, not gates: tra 'actual data points' per leg (dims), common rows. ('Total Lost Frames' and frame-counter delta come from the legs' own files in card 170-a2-6; here only if they sit in a run dir file you can read - list the file and the value or say NOT FOUND.)
3. Self-test on the stored 110-7 run dirs: leg A = `tools/bench/m8_out/replay_s1_20260927_184651`; leg B = the `run_dir` of its `leg.json` (name the file:line you read it from; `p6_replay_facts.md:103` names `replay_s1_20260927_185846` for the cal pair, check it is the same leg).
   Expected (PD409(f)): 4443 common rows, 0 X/Y/Z rows differing (MATCH all rows), DISTINCT on all rows with the D you read, cal differing only inside the date/time field (5 bytes in the time text, `p6_replay_facts.md:103`). A different result is RETURNED as a fact, not tuned away.
4. Scripts: scope header (`# labview: none` / `# hardware: none`), `RESULT {...}` last line, shared functions called per `docs/script-writing.md` (it has a `line_of`/`find_line` rule: if you need a citation helper, IMPORT the existing one from one shared module; never a sixth copy).
   Run long steps under `py tools/bgrun.py --material --max-min 10 --log tools/bench/diag_c170_a2_4_selftest.log -- py -u tools/bench/m8b_replay_compare.py --selftest`.
5. Facts `tools/bench/diag_c170_a2_4_facts.md` (<= 40 lines, every number with file:line); hashes of the 110-7 inputs unchanged before and after.

## Not in this card
No LabVIEW, no leg, no new run dir, no fp-102, no hook/plan/STATUS edit. A self-test result that differs from the expected values = RETURN with the facts.
