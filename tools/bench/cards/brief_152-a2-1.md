---
card: 152-a2-1
status: current
date: 2026-10-09
---
# Brief 152-a2-1 - stagesim takes the measured FS owner read (docs/d1/ring-p4d.md PD368(c)); OFFLINE, no LabVIEW

Why: card 152-a1-1 measured FS #29721's owner = class `Diagram`, uid 23166, echo `FlatSequence` #29721 (`tools/bench/diag_c152_a1_1_facts.md`, owner.log:25,29,32,33) and stored it in the DERIVED graph
`tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json` e26b4d90 (top-level key `fs_owner_read` {"29721": ["Diagram", 23166]} + `fs_owner_read_cite`). `stagesim` still lists 29721 in `fs_unmeasured`
(`stagesim.py:354`) and refuses the chain at `stagesim.py:1805-1807`. This card teaches `stagesim` to use that read, nothing else. PD368(c) is implemented LITERALLY (class string `Diagram` only).

## Read first
`docs/d1/ring-p4d.md` PD368(c); `tools/stagesim.py:339-357` (the `fs_measured` branch of `base_state`), `:374-440` (`fs_measured_state`, its `fs_parent`), `:1795-1815` (`_diag_chain`);
`tools/bench/selftest_c134_4_owners.py` (the 7 existing owner cases, 7/0) and its fixture style; the derived file's `fs_owner_read_cite` (what the echo record looks like).

## Change (stagesim.py only; md5 748bbf30 changes by this item, authorised)
In `fs_measured_state` (or at its call site `:343-354`) add: for each FS uid in `graph["fs_owner_read"]` take it into `fs_parent` ONLY when ALL hold -
(1) the read entry is class exactly `Diagram` with a non-zero uid; (2) the cite records an echo of the SAME FS uid (class `FlatSequence`, uid == the FS) - no echo record, or a different uid = UNMEASURED;
(3) the FS has NO border tunnel outer face (`par[fs]` empty); if border faces exist too, they must be exactly one outer frame equal to the read uid, else the FS stays UNMEASURED (faces unchanged = existing rule);
(4) nothing else is an owner source (carried maps, creation map, simulator: PD289(c)). A graph WITHOUT `fs_owner_read` must give byte-identical `fs_measured_state` output and `base_state` as before.
`st["owners"][str(fs)] = ["Diagram", uid]` and removal from `fs_unmeasured` follow from `fs_parent` as for faced FS - do not add a second code path in `_diag_chain`.

## Steps
1. Before: md5 inventory (copy `diag_c152_a1_1_inv.py` -> `diag_c152_a2_1_inv.py`, names only; pins: stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, s08 f99e8414, graph 44858dbf, derived e26b4d90).
   Baseline: `selftest_c134_4_owners.py` 7/0, `selftest_c134_1_fsmap.py`, `selftest_c134_1_dry.py`, `selftest_c134_2_gates.py`, `selftest_c134_2_regress.py` results quoted (run them first, as they are).
   Save `fs_measured_state` + `base_state` output for graphs 44858dbf and `graph_ring_p4s07_20261008_224835.json` (71935a84) as JSON for the before/after identity check.
2. Edit `stagesim.py` (Edit tool, not a heredoc). Prior-art/peer gates apply as for any stage-tool change; a stage-tool edit has NO LabVIEW card beside it (none is live).
3. New self-test `tools/bench/selftest_c152_fsowner.py` (do NOT edit `selftest_c134_4_owners.py`), cases on small fixtures: (i) no-border FS resolved by a valid read -> in `fs_parent`, owners entry, not in `fs_unmeasured`;
   (ii) read disagrees with border faces -> UNMEASURED; (iii) class not `Diagram` (e.g. `TopLevelDiagram`) -> UNMEASURED; (iv) uid 0 -> UNMEASURED; (v) echo missing / echo uid != FS / echo class wrong -> UNMEASURED;
   (vi) read present but faces agree -> resolved; (vii) graph without `fs_owner_read` -> identical to the saved before-output. Then the REAL files: derived graph -> 29721 resolved, `fs_unmeasured` becomes [2499, 14682, 43914]; graph 44858dbf (no key) -> still [2499, 14682, 29721, 43914];
   `_diag_chain` from frame #29869 walks to Diagram #23166 on the derived graph (quote the chain) and still raises on the original graph.
4. After: re-run the five baseline self-tests (same counts as before or better; a changed count is a RETURN) and the identity check for the two graphs; md5 inventory after (only `stagesim.py` differs; quote its new md5).
5. No `tools/hooks` edit, no other stage-tool edit, no LabVIEW. A refusal by a gate on a correct edit is a gate false positive: `py tools/gate_fp.py log` and go on; never an env bypass.

## Report (`tools/bench/diag_c152_a2_1_facts.md`, <= 30 lines)
Baseline vs after counts of the 5 self-tests + the new one; identity check result; new stagesim md5 + diff size; the `fs_unmeasured` lists on both graphs; the `_diag_chain` walk; md5 inventory before/after. `OPEN:` line. Facts only.
