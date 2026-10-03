---
type: brief
status: current
date: 2026-10-03
---
# Brief 143-4 — rebase-path raw-uid keys: census + fix (PD334(b)(c), docs/d1/ring-p4b.md:187), then s03 rebase (OFFLINE, ALONE)

## The decision you implement (judgement, PD334(b))
`stagexec.uid_reuse` (`tools/stagexec.py:942-962`) is a guard for TWO consecutive reads around ONE op. `stage_prerun.py
--rebase` (`tools/stage_prerun.py:3453-3455`) applies it to the plan's base graph vs the real graph of the saved file,
many ops apart and across planned deletes, where LabVIEW re-issuing freed uids is expected. In `--rebase` ONLY: a re-issued
uid is FATAL when the plan being rebased NAMES that uid (in its actions or its bindings); otherwise log one line
`REUSE-NOTED <uid> <old>-><new>` and let binding go by (uid, owner, name) (PD332(a)). Execution-time callers of
`uid_reuse` are UNCHANGED.

## Steps
1. **Census** (read-only first): every place in `tools/stagexec.py`, `tools/stage_prerun.py`, `tools/stagekit.py` that
   compares terminals or owners of TWO different graphs keyed by raw uid. Per site: file:line, which two graphs, can a
   delete lie between them (yes/no), already (uid, owner, name)-keyed (yes/no). Write the table into the facts file.
2. **Fix** the rebase-path site of `uid_reuse` by the rule above, plus any other census site that is on the rebase/rebind
   path AND compares across a delete boundary with a raw key — same (uid, owner, name) rule. Other sites: listed, not
   changed.
3. **Self-test** `tools/bench/selftest_rebase_uidreuse_c143_4.py`: (i) this case (uid 23276, s01 graph
   `graph_ring_p4s01_20261002_234419.json` → s02 graph `graph_ring_p4s02_20261003_112505.json`, plan s03 that does not name
   23276) → REUSE-NOTED, rebase proceeds; (ii) a synthetic plan that DOES name a re-issued uid → refused; (iii) the
   28004/28979 case still binds as in `selftest_rebind_c142_5.py`. Rerun the old rebind/rebase self-tests
   (`selftest_rebind_c142_5`, `selftest_rebind_c132_5`, `selftest_rebase_c132_6`, `selftest_rebase_c133_3`) and
   `tools/bench/c125_1_offline_measure.py` (PD252(a)). Counts in the log.
4. **Then s03** (the rest of 143-3's steps): `--rebase tools/bench/plan_ring_p4_s03v18.json --graph
   tools/bench/graph_ring_p4s02_20261003_112505.json`; X10 at the measured start 596.0 (if > 680 → re-cut by PD320(c), report
   the new last op); run the already-written `tools/bench/prep_c143_3_pred.py` (fixed EL rule) → EL prediction + basis;
   `--dry` and `--prerun` on both s03v18 recipes; `--prerun ... --scratch-required` exit code.

Return at the first unexpected result. Never touch LabVIEW; never launch. Facts → `tools/bench/prep_c143_4_facts.md`.
