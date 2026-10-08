---
type: facts
status: current
date: 2026-10-09
card: 152-b1-3
---
# Card 152-b1-3 facts: LoopTunnel-source FS tunnel naming recorded (1 table row + stagesim rule), offline, all self-tests PASS
## 1. Table row (`fs_tunnel_naming_table.json:135`, run "152-b1-2 X", op `X #335 <- #249`)
- src LoopTunnel #243 outer face t249 'min slot', wired w237; cites checked against the log: `diag_c152_b1_2_cross.log:93` (FACES LT BEFORE X), :100 (FACES AFTER X), :105/:106 (FSOT #250 t258 / t255 'min slot'), :107 (LT faces unchanged), :99 (census: one FSOT), :86/:88 (P2 #290 <- #192, one LoopTunnel).
- New field `src_looptunnel` {loop_class WhileLoop, inner_name 'min slot', inner_src_class SubVI, inner_src_name 'min slot', scope = the one measured case}. `src_tunnel_renamed: false` (:107). `net_tunnel_names: []`; borders [in FlatSequence]; faces [FSOT in 'min slot' / out 'min slot'].
## 2. Rule diff (`tools/stagesim.py`)
- Before: `_cross_tunnel_name` refused any named source whose owner class is outside SubVI/Property/Local/Diagram (old :1891-1893). That included LoopTunnel.
- After: `CROSS_LOOPTUNNEL_MEASURED = ("WhileLoop", "SubVI")` :1886. `_looptunnel_measured` :1889-1899 is True only for one shape: the source is the OuterTerminal (is_source); its one InnerTerminal sits on a diagram whose `owners` entry is WhileLoop; that inner net's only source is a SubVI. Then the name is kept as for a SubVI source (:1907-1908). Anything else hits the old refusal.
- `naming_table_check` :1947-1959 builds the inner face, its SubVI source and the owners map from `src_looptunnel`. G78b :3384 now expects 16 rule rows (was 15).
- Real graph check (`diag_c152_b1_3_inspect.log`): #30179 t30192 OuterTerminal on #23166; inner t30183 on #29699 = WhileLoop #16483; the inner net w30197 source is SubVI #29719 'min slot'. So op 187 matches the measured shape. The replay is NOT run here (next card).
## 3. New md5s
- stagesim.py c24bd39a -> 128bacfb5710355fe76fabfdde567f38; fs_tunnel_naming_table.json 0c0ba43a -> 769ae8d0f4a9c6a273e7c899dc3496a7; selftest_stagesim_tunnel_naming.py 237c485d -> aca2daff0150cfa670180f76b04ab2ad.
## 4. Self-tests (bgrun logs `tools/bench/diag_c152_b1_3_st_*.log`, all rc=0)
- tunnel_naming 21/0 (16 rows + C1 + L1 'min slot' on both faces + L2 ForLoop, L3 Function inner source, L4 non-Outer face all refused UNMEASURED). c152_fsowner 15/0. c134_4_owners 7/0.
- stagesim selftest 106/0; fsexit_c138_1 14/0; k79 4/0; l2a1_80 13/0; pin 10/0; unflip_81 8/0. No pin drift: no self-test pins the stagesim md5.
## 5. Invariants
- `diag_c152_b1_3_pins.log` 12/0: stagekit, addrcheck, stagexec, gscript, stage_prerun, vigraph, memory_model, s08 f99e8414, graph 44858dbf, derived e26b4d90 and both frozen self-tests are unchanged.
- No LabVIEW process before or after (process count 0). No tools/hooks edit. No original touched.
OPEN: the rule covers only the one measured shape. A LoopTunnel on a ForLoop, a non-SubVI inner source, or an entry tunnel stays refused until a second row is measured.
