---
card: 169-a2-2
status: current
date: 2026-10-12
---
# Brief 169-a2-2 (assignment 169-2) - PD406(f): drain gate false positives fp-98, fp-100 (and fp-99 if its fix is outside tools/hooks/**)

Plan: `docs/d1/ring-p6.md` PD406(f), PD407. Offline tooling card; no LabVIEW, no hardware. It runs AFTER the deliverable card (169-a1-3) and the bed move.
The three entries are in `tools/bench/gate_fp_queue.jsonl` (lines 98, 99, 100; read each entry's `why`, it names the file:line):

- **fp-98** (`checker:stage_prerun:X5`): X5 counts the Stage._op verb `remove_bad_wires_scripted` as a WIRING op (`WIRE_VERB_RE` 'wire', `tools/stage_prerun.py:131,2715`) against plan `action=="wire"` rows;
  a VI-level Remove Bad Wires (method 410) makes no wire, and X5 has no RBW class although `DELETE_OPS` lists `remove_bad_wires` (:1601). Fix = give X5 an RBW class (the verb is not counted as a wiring op, and it
  must still be an allowed edit op for X10), narrow, in `tools/stage_prerun.py` (the editor tool, patch in place).
- **fp-100** (`checker:stage_prerun:dry R1`): `stage_prerun.find_graph` picked `graph_ring_p6rbw_20261012_191349.json` because its header md5 is 75773b0d, but it is the graph of an RBW'd in-memory copy (2066 Wire objs);
  the bed's real graph is 7815af09 (2091 wires). Fix = find_graph must not pick a graph whose header md5 equals the bed md5 when the file says it is a post-edit copy, or must prefer the graph of the bed itself.
  Read how `diag_c167_a1_1_rbw.py:112-113` writes that header (it sets `gr md5=BEDM`) and choose the narrowest rule that picks 7815af09 for the bed; the second half of the entry (D1 taint scoped to one statement, :622, :809) is
  fixed only if the first fix does not already make the dry PASS on the 168 script; say which.
- **fp-99** (`guard_bash`): the refusal text comes from a hook, but the FIX named in the entry is `tools/protocol.py:572` `RUN_VI_CMD_RE` (matches a bare file name anywhere in the command text, so a read-only grep of a `.py` driver is refused as running a VI).
  If the fix is in `tools/protocol.py` (outside `tools/hooks/**`) do it, with a self-test; if ANY part of the fix has to be in `tools/hooks/**`, do NOT touch it: leave the entry open and record the reason in the facts.

## Steps (stop at the first unexpected result and RETURN with the facts)
1. Hash the pins (card inputs). Drift = RETURN. `py tools/protocol.py requires <this card>` PASS.
2. For each entry: patch in place with the editor tool (`docs/script-writing.md` rules 10-15: no new option, no copy of a shared function, a `# shortcut:` comment only where there is a known limit).
3. A self-test per fix that RUNS the changed function on the stored fixtures: fp-98 -> X5 on `tools/bench/diag_c167_a1_1_rbw.py` passes with its one RBW and still FAILS on a plan with a real extra wiring op;
   fp-100 -> `find_graph` on the 168 script returns `graph_ring_p5s02e_20261012_173009.json` (7815af09) and still returns the right graph for an older stage script whose log is stored (name which); fp-99 -> the grep command text of the entry is accepted and a real VI run command is still refused.
   Put the checks in ONE new file `tools/bench/selftest_c169_fp98_100.py` (asserts, `RESULT {...}` line). Run the existing stage_prerun self-tests that the edit can touch (`tools/bench/selftest_stage_prerun_*.py`, `selftest_c148_prerun_fp.py`) through `py tools/bgrun.py --max-min 10 --log <file> -- <cmd>` and quote pass/fail counts before and after (they must not get worse).
4. Drain: `py tools/gate_fp.py` per its usage text, one call per entry, citing the self-test; entries whose fix landed are discharged, fp-99 only if the fix was outside `tools/hooks/**`.
5. fp-101, fp-102 and every hook entry are NOT drained here (fp-101 is a hook gate -> chat; fp-102 is not in the purpose). Do not log new entries except a provable false positive of this card's own work.
6. Facts `tools/bench/diag_c169_a2_2_facts.md` (<= 40 lines, every number with file:line): per entry the patch (file:line), the self-test result, the drain call and its output, the self-test counts before/after, a `skipped:` line.

## Not in this card
No LabVIEW, no tools/hooks/** edit, no STATUS/INDEX/plan edit, no recipe edit (`tools/recipes/stage_d1_ring_p6.py` is pinned by its prior-art review), no memory_model edit, no new option.
