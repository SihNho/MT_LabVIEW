---
card: 166-a1-6
status: current
date: 2026-10-12
---
# Brief 166-a1-6 (assignment 166-1) - E5 + REUSE DETECTORS BY NODE IDENTITY, drain fp-87/fp-88, OFFLINE

Plan: `docs/d1/ring-p5c.md:175-180` (PD400(d)), carried by PD403(d)(4) (`:271-272`). Read `docs/script-writing.md` (calls into the shared module; new/changed function = docstring that names its self-test).
Offline only, no LabVIEW, no `tools/hooks/**` edit. **Stricter only. An adopted row that a tightened rule blocks is not loosened: RETURN with the row.**

## The two false positives (read both in `tools/bench/gate_fp_queue.jsonl`, lines 87-88)
- **fp-87** (`checker:diag_graph:E5`, card 164-3-5): E5 tests the plan's deleted nodes by uid only (`diag_c164_a3_5_graph.py` line ~65, `deleted_nodes_present = [u for u in deleted_nodes if u in cls]`). LabVIEW re-used uid 23501 for another node, so E5 said "present" for a node that is gone.
- **fp-88** (`checker:stagekit:term_identity_gates:reuse`): `reuse_noted` checks deleted WIRE uids only and `recycled` checks position keys of the base node (`tools/stagekit.py` `term_identity_gates`, ~`:1391-1520`); neither sees an object/terminal uid re-used by another node.

## What to build (shared module; find the E5 check's home and `term_identity_gates` by `grep "def "`; do not copy)
1. **Identity function in the shared module** (`tools/stagekit.py`, or the module that already holds the E5 deleted-node check if that is a shared one): `(class, owner class, owner uid, pos)` per object, exactly as `tools/bench/prep_c164_a3_7_ident.py` `ident()` does it (tunnel owner via `stagexec.tunnel_owner`, else the `frame_diagram` of its rows). Move it, do not re-write it differently; the prep script may then import it (do not edit the prep script's logic, it is a stored diag).
2. **E5 (deleted nodes present):** a deleted node counts as PRESENT only if a node of the same identity exists in the after-graph; a uid that now belongs to a node of another identity is reported as `uid_reused` (INFO, with the old and new identity), not as present.
3. **Reuse detectors:** `reuse_noted` / `recycled_uids` also see an object or terminal uid re-used by a node of a different identity (new list `uid_reused`, INFO plus a RECORD line), in addition to what they see now. Existing outputs stay byte-equal on the stored plans.
4. **Stricter only:** a deleted node whose identity SURVIVES (same class, owner, owner uid, position) is still a BLOCK. Nothing that blocked before may pass.

## Self-test (new `tools/bench/selftest_c166_ident.py`, scope header, RESULT line; docstrings of the functions name it)
- Positive on the stored step-4 data used by `prep_c164_a3_7_ident.py` (`graph_ring_p5s02c_20261010_131658.json` base, `graph_ring_p5s02d_20261010_154830.json` adopted, plan `diag_c164_a3_5_graph_plan.json`): I1 (#23501 identity gone) and I2 (#23042 identity gone) PASS, and the uid-reuse of 23501/23481 is reported as `uid_reused`. Quote the lines.
- Negative: a planted survivor (a copy of the adopted graph with a node of the deleted node's identity added back under another uid) is CAUGHT. Quote it.
- Stricter-only proof: run old vs new on every stored adopted graph pair the E5 check has seen (grep `diag_c16*_graph*.py` / `graph_ring_p5*`); no old-BLOCK becomes PASS; a newly BLOCKED adopted row = RETURN with the row (file, step, uid).

## Then
- **Drain fp-87 and fp-88**: `py tools/gate_fp.py drain --id fp-87 --fixed "<function:line>" --selftest "<file + result line>"`, same for fp-88. Read each entry first; if the tightened rule does not address it, log that honestly and leave it open.
- **Stored plans:** `plan_ring_p5s01a/b.json`, `plan_ring_p5s02a` .. `e` compile and dry byte-equal after ALL tooling edits of this assignment (cards 3, 4 and this one) - use the checks that card 166-a1-4 used (`tools/bench/diag_c166_a1_4_dry.py`, `diag_c166_a1_4_facts.md`); quote the command and line. The known pre-existing p5s02d dry rc 1 (CEN2 vs pred census) is the same under the old stagekit (`tools/bench/diag_c166_a1_4_stagekit_pre.txt`): state that it is unchanged, do not fix it.
- Run the existing self-tests a gate RUNS that touch what you changed; list pins that drifted (no mass re-pin).
- fn description: docstring on any NEW function, `docs/fn_descriptions.json` for old ones.
- Facts `tools/bench/diag_c166_a1_6_facts.md` (<= 40 lines, file:line each). Hash the seven VIs (75773b0d, 7f2582ae, eb1d0f31, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d) before/after: unchanged; no LabVIEW process. Do NOT touch PB (done by 166-a1-4), the EL advisory / elpredict (166-a1-3), STATUS, INDEX, the plan.
