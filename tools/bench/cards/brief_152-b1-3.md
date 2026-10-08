---
card: 152-b1-3
status: current
date: 2026-10-09
---
# Brief 152-b1-3 - RECORD the measured LoopTunnel-source FS tunnel naming: ONE table row + the stagesim rule, exactly as measured (docs/d1/ring-p4d.md PD369(e)); OFFLINE

Why: card 152-b1-2 measured it (`diag_c152_b1_2_facts.md` section 2, log lines `diag_c152_b1_2_cross.log:93,99-109`): a LoopTunnel source (inner source = SubVI terminal 'min slot') crossed into a 1-frame Flat Sequence with 0 border tunnels created ONE FlatSequenceOuterTunnel whose outer face (t258) AND inner face (t255)
are both named 'min slot' (the source LoopTunnel face's name); the source LoopTunnel's own faces were NOT renamed; the nets' wire uids changed (w237 gone, w261 + w240), which is not a naming matter. PD369(e) therefore takes its first option: a LoopTunnel source is named like a SubVI/Property/Local/Diagram source (the source face's name on both faces).
Edit nothing beyond what this one row shows (no generalisation to other LoopTunnel kinds: say in the row/rule comment that the measured case is a LoopTunnel on a WhileLoop whose inner source is a SubVI terminal).

## Read first
`docs/d1/ring-p4d.md` PD369(e); `tools/bench/diag_c152_b1_2_facts.md`; `tools/stagesim.py:1875-1895` (`_cross_tunnel_name`, the refusal at 1892, the named/empty class sets at 1882-1883); `tools/bench/fs_tunnel_naming_table.json` (the 18 existing rows: copy the exact row shape, columns and how rows cite a log);
`tools/bench/selftest_stagesim_tunnel_naming.py` (30 lines, reads the table).

## Steps
1. **Invariants before:** md5 of stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, memory_model a28b6dd7, s08 f99e8414, graph 44858dbf, derived e26b4d90; the PRE-EDIT md5 of stagesim (c24bd39a), the table (0c0ba43a), `selftest_stagesim_tunnel_naming.py` (237c485d), `selftest_c152_fsowner.py` (64918ff7), `selftest_c134_4_owners.py` (2d04ba97). No LabVIEW process (tasklist) before or after.
2. **Table row:** ONE new row in `fs_tunnel_naming_table.json` in the existing shape: source class LoopTunnel (owner WhileLoop, inner source kind SubVI terminal), outer face name, inner face name, source-net tunnel renamed: no, and the citation `tools/bench/diag_c152_b1_2_cross.log:93,100,105,106,107` (verify every cited line against the log before writing; use the real line numbers).
3. **Stagesim rule:** extend `_cross_tunnel_name` (and its class sets) so a LoopTunnel source yields the source face name on both faces, exactly as the row. Anything else (other owner classes, other inner source kinds, the refusal path for unmeasured classes) stays refused as before.
   Edit stagesim.py with the Edit tool (no heredoc patch). New md5 quoted. Copy-edit comments to one short line.
4. **Self-tests:** extend `selftest_stagesim_tunnel_naming.py` with the new row (its own case: a LoopTunnel source now resolves to 'min slot' on both faces; an UNMEASURED class still refuses). Run it, `selftest_c152_fsowner.py` (15/0 expected) and `selftest_c134_4_owners.py` (7/0 expected), and every other `selftest_stagesim*.py` the pin-check lists; quote pass/fail counts.
   A frozen self-test that fails ONLY because it pins stagesim's old md5 is a pin drift: quote it and log it with `py tools/gate_fp.py log`, do not edit it; any other failure is RETURNED with the log line.
5. **Replay (item 6 of the purpose is NOT yours):** do not rebase, make s09, or replay ops 185..190 here. The next card does.
6. **Invariants after:** every pin of step 1 except the three edited files unchanged (stagesim, table, tunnel_naming selftest: new md5s quoted). No tools/hooks edit; no LabVIEW. A gate refusing your OWN command text is a false positive: `py tools/gate_fp.py log` and go on; never an env bypass.

## Report `tools/bench/diag_c152_b1_3_facts.md` (<= 30 lines)
The row as written (with cited lines); the diff of the rule (before/after lines); new md5s; self-test counts per file; pin drifts if any; invariants; `OPEN:` line. Facts only.
