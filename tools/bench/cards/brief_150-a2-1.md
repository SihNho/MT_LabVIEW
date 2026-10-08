---
card: 150-a2-1
status: current
date: 2026-10-08
---
# Brief 150-a2-1 - `stage_prerun.rebind`: name-free old-terminal key (PD365(c)); offline, ALONE

Plan of record: `docs/d1/ring-p4c.md` PD365(c) (read lines 254-283 only), measured cause `tools/bench/diag_c150_a1_3_facts.md`.
This card EDITS `tools/stage_prerun.py` (function `rebind`, key + info list + docstring ONLY) and adds
`tools/bench/selftest_rebind_c150.py`. It runs ALONE: no other card beside it. No LabVIEW, no hook edit.

## The change (decided by the judgement session, PD365(c); do not redesign)
- Today `tkey` (stage_prerun.py ~:3829) = (term_uid, owner_uid, term_name); a terminal is OLD only when that triple is in N's base `before`.
  A pre-existing terminal renamed by LabVIEW (s06: #2626 t2832/t4160/t4165 'array'->'element'; #9503 t9505/t9508 'Value'->'') lands in `real_new`.
- New: old-terminal identity = (term_uid, owner_uid, term_class, direction[is_source]). A pre-existing terminal whose NAME differs between
  `before` and `real` is an INFO line: `RENAMED-OLD <uid> #<owner> '<a>'->'<b>'`, recorded in `info['renamed_old']` and logged by the `--rebase`
  CLI where it logs `REUSE-NOTED`. Never a refusal. `rebind` reads no licence.
- Everything else stays: uid_reuse, named-uid-on-another-owner, created-object shape, wire checks. Card 142-5's case (LabVIEW re-issues a deleted
  node's terminal uid to a NEW node) must still be told apart by the OWNER uid: (uid, owner) not in `before` => NEW.
- Edit scope: the key, the info list (add `renamed_old` to the `info.update` default dict), the CLI log line for it, the docstring. Nothing else.

## Self-test `tools/bench/selftest_rebind_c150.py` (<= 120 lines, on stagekit conventions where they exist; prints `R1..R4 PASS/FAIL` and a count line)
- R1: s06->s07 inputs (before = s06 plan `finalized.base`, prov = the s07 provisional end `plan_ring_p4_s07v18_prov148.json` family / its sim end - take the
  same inputs `diag_c150_a1_3_probe.py` used; real = `graph_ring_p4s06_20261008_192149.json`) REFUSE with BINDING (BuildArray x0/x1, LoopTunnel x2/x3) on the
  ORIGINAL code and bind on the new code. Prove "refuses on the old code" by running the check against `git show HEAD:tools/stage_prerun.py`
  exported to a temp module under `tools/bench/` (delete it after), or by a recorded pre-edit run - state which. R1 must be run BEFORE you edit.
- R2: `info['renamed_old']` lists exactly the 5 measured renames (t2832, t4160, t4165 on #2626; t9505, t9508 on #9503).
- R3: a synthetic term-class (or direction) change of an old terminal at the same (uid, owner) still REFUSES.
- R4: the s05->s06 inputs (creation map `plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl`; reuse the inputs of `prep_c147_a1_3_rebase.log:59`) bind to
  the SAME node map as before the edit (compare `info['map_nodes']`/N map against a pre-edit recorded run).

## Regression (rc 0, or the same pass/fail counts as before the edit; record the BEFORE counts first)
`py tools/bench/selftest_rebind_c142_5.py` (4/0), `selftest_rebind_c132_5.py`, `selftest_rebase_c132_6.py`, `selftest_rebase_uidreuse_c143_4.py`, then
`py -m py_compile tools/stage_prerun.py`. Run each under `py tools/bgrun.py --max-min 5 --log <file> -- <cmd>` if the hook asks for it.

## Invariants (md5 before = after, quote): stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, s06 VI 569ffbf5, s05 3f9ac26b,
bed 39511877, graph a3ecb92b, plan_ring_p4_s07v18.json 10a4f59a, memory_model 8eec443c, adopted_scratch. stage_prerun.py md5 CHANGES (quote old dcd45aba and new).
Do NOT run `stage_prerun.py --rebase` writing into `sim/ring_p4_s07v18` (the next card does that). No `tools/hooks/**` edit. No LabVIEW process.

## Return conditions
A protected md5 moved; R1 does not refuse on the old code (the diagnosis is then wrong - RETURN with the output); a regression self-test count worsens;
a hook false positive (log with `py tools/gate_fp.py log`, no env bypass, RETURN if it blocks the deliverable).

## Report `tools/bench/diag_c150_a2_1_facts.md` (<= 30 lines): old-code R1 output, diff summary (line ranges), R1-R4 results, regression counts before/after,
md5 table, `OPEN:` line. Facts only.
