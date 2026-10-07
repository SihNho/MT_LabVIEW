---
type: facts
status: current
date: 2026-10-07
---
# Card 145-a2-1 facts: s04 adopted, expected-EL 58, graph read; requiredness UNREAD (no reader, card forbids a VI save) -> BLOCKED

## Done
- Inputs md5 all as pinned (brief step 1). Adopt `tools/bench/diag_c145_2_adopt.py` (unchanged, by import): 3/0, `diag_c145_2_adopt.log`;
  adopted `claudeDev\D1_ring_p4s04_20261007_215031.vi` md5 95e408ff14a406edd3f16b32ba7324f1 (no rename: adopt_scratch copies nothing).
- Graph plan `diag_c145_2_mkgraph.py` (unchanged): 3/0, `diag_c145_2_graph_plan.json` 0273c8d8.
- Expected EL `tools/bench/diag_c145_a2_1_elexp.py` (new, copy of diag_c144_2_elexp.py; pred NOT written): 6/0, `diag_c145_a2_1_elexp.log`;
  `errorlist_expected_D1_ring_p4s04_20261007_215031.json` md5 1a28fe86, total 58, 14 entries, compare(read 5e53096a) extra [] missing [].
  Entries = s03's minus While-cond, Local re-labelled + 1 empty-raw local row + Index Array x3. No new EL read.
- Graph read `diag_c145_2_graph.py` (unchanged; dry/prerun needed `--graph graph_ring_p4s03_20261007_205535.json` as for 144-a2-1):
  15/0 `diag_c145_2_graph.log`, 175 s; `graph_ring_p4s04_20261007_223245.json` md5 094ba298ba7b2c1d69f92c84d8ecb626, 6038 rows, 10515 objs.
  MEM after load 605.4 MB, after read 617.0 MB. Handles 45647 -> 45931 (+284; 144-a2-1 read +274, 143 read +278: same pattern, not flat +-100).

## Step 5 table (`tools/bench/diag_c145_a2_1_table.log`, 3/0; pane index from build_ringpickslot_v2.log:128, build_ringseqcheck_v0.log:216)
| VI | input | pane | requiredness | wired at drop | source |
|---|---|---|---|---|---|
| RingPickSlot_v0 (PS1 #29719) | Num | 11 | UNREAD | yes (w30038) | diag_c145_a2_1_table.log:17 |
| RingPickSlot_v0 (PS1 #29719) | last | 10 | UNREAD | yes (w30049) | diag_c145_a2_1_table.log:16 |
| RingSeqCheck_v0 (SQ1 #29724) | n1 | 11 | UNREAD | yes (w30078) | diag_c145_a2_1_table.log:31 |
| RingSeqCheck_v0 (SQ1 #29724) | n2 | 10 | UNREAD | NO | diag_c145_a2_1_table.log:30 |
| RingSeqCheck_v0 (SQ1 #29724) | last | 9 | UNREAD | yes (w30081) | diag_c145_a2_1_table.log:29 |
| RingSeqCheck_v0 (SQ1 #29724) | Latest | 8 | UNREAD | NO | diag_c145_a2_1_table.log:28 |
| RingSeqCheck_v0 (SQ1 #29724) | discards | 7 | UNREAD | NO | diag_c145_a2_1_table.log:27 |
- PS1 has NO unwired assigned input; its 7 other input rows are unassigned pane slots (name '', wire 0). The pred's PS1 input item [-1]
  therefore cannot come from an assigned input at all, whatever its requiredness.
- Unwired assigned inputs at the drops = SQ1 n2, Latest, discards only.

## Why requiredness is UNREAD
- API (fact peer `archive/peer/2026-10-07-c145-a2-1-conpane-required-claude.md`, ANSWERED, $0.76; gemini arm ERROR): ConnectorPane
  `WiringRules[]` 239A8405 (1 Required, 2 Recommended, 3 Optional, 4 Dynamic) / `Wiring Rule:Get` 239A8007. Labviewwiki only.
- No op carries it: grep `WiringRule|239A8405|239A8007` over tools/ docs/ = 0; `gscript.conpane` reads Controls[] only (gscript.py:3365).
- Building a reader op needs a saved VI; brief "Never: save any VI except through the adopt path" + card rule "no second scratch".
- Builds never set a rule (no Wiring Rule:Set in build_ringpickslot_v2.py / build_ringseqcheck_v0.py): the settings are LabVIEW's defaults
  for a scripted Assign Control To Terminal (value not measured).

## Not done: step 6 (abb76d41 + resume record NOT deleted; brief: only after requiredness succeeded).
## After: `diag_c145_a2_1_check.log` 11/0: s03 282301ca, bed 39511877, s04 95e408ff, subVIs, plan, pred, recipes unchanged; no LabVIEW process.
