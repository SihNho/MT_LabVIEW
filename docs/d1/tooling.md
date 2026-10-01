---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, tooling, gates, simulator, pre-decided]
---

# D1 tooling — gate, simulator, prerun and op decisions from 268 on

Scope: decisions about `tools/stage_prerun.py` (X-lines), `tools/stagexec.py` / `tools/stagesim.py`, ops and their
hygiene records, gate false positives, and other tools on the D1 path. Violation-slug DEVICE decisions still go to
`docs/violation-decisions.md` (append-only; its footer names the readers).

How to add: see the 5-line note at the top of `docs/d1/INDEX.md`.

## Pre-decided

268. **(cycle 130 judgement, 2026-10-02 — after 130-1 BLOCKED 4/3, 130-3 BLOCKED, 130-4 FAIL 2/1)**
     USER-RULES: U1 (relied on; gate code only, no computation or design change).
     - **(a) X10 memory MODEL ACCEPTED and LIVE** (PD267(b) done): `tools/stage_prerun.py` `x10_model_peak`/`x10_gate`
       (:1861, :1882) with coefficients from `tools/bench/memory_model.json` (each number cites its log line); FAIL > 675,
       FAIL UNMEASURED. Self-test `selftest_x10_c130_1.py` 9/0 (`tools/bench/selftest_x10_c130_4.log`): 129-1 bytes
       728.9 FAIL, 129-8 bytes 688.5 FAIL, no-plan UNMEASURED, P3a recipe 654.6 PASS. It stayed live while its self-test
       was red (judgement: the gate is the decided device; reverting would re-open the 129 hole).
     - **(b) `--dry` must FAIL when the executor stopped before the plan's last op.** Today a dry stopped at op 48 of 63
       PASSes (`stage_prerun.py:869-871`; review `archive/peer/2026-10-02-hyp-c130-4-c128b.md`). Built in card 130-5,
       self-tested on that case. A dry that does not cover every op is no evidence for a launch.
     - **(c) `selftest_stage_prerun_c128b` red (3/2) is fixture staleness, not X10:** its fixture is the unsplit
       `plan_ring_p3b.json` (4003eaa5), finalized before stagesim's 129-7 naming rule (PD265(a)) and STALE by PD263(a).
       The unsplit 70 is re-finalized from `plan_ring_p3b_in.json` under the current stagesim as a REFERENCE (never
       launched) — the split's equivalence check needs that end graph anyway — and c128b is re-pinned to it.
     - **(d) 130-2 ACCEPTED (PASS 6/0):** fp-23 (stop record judges python segments by the script they RUN), fp-15..18
       drained, card_clock in `protocol.py validate`, gemini empty answer falls back. Still open for a tooling drain:
       fp-20, fp-21 (stage_prerun), fp-22 (guard_peer follows function-local imports), fp-24 (guard_peer judges a DRY
       self-test LabVIEW-touching), fp-25 (peer_role_of on read-only commands), `guard_cycle.py:40` BUILD_RE `\bpy` on
       a `.py` extension, stop_record holes H1–H3 (`diag_c130_2_baseline.log`).
270. **(cycle 130 judgement, 2026-10-02 04:5x — after 130-6 FAIL 3/1, `stage_d1_ring_p3b1_scratch_pin3.log:370`)**
     USER-RULES: U1 (relied on; simulator/binder only — tunnel names are labels, no computation changes).
     - **(a) PD265(a)'s tunnel-name rule is REFUTED as general:** pin3 ran ops 1–25 equal to the simulator (STEPX diff 0,
       `pin3.log:309,328,347`), then op 26 (`p3b_x_img_src`, `#6810` Image Out → CP1 Image Src, `plan_ring_p3b1.json:473-479`)
       created an FS outer tunnel that LabVIEW named `Image Out` where the simulator said `''`. Same class as 129-4 op 33
       and 130-5's op-48 dry stop. The rule was GUESSED from one net; it has now failed on a second ⇒ CLAUDE.md "guessed
       twice, build the reader": **no third scratch run until the naming rule is MEASURED** from every recorded crossing.
     - **(b) Next card (offline):** a table, one row per crossing ever run (B1, A_bn, pin2 op 33 and its `''` rows, pin3
       ops 1–26, the `cross.log`/`fs.log` cases of PD265(a)): source node class + uid, source TERMINAL name, net's existing
       tunnel names, border kind, resulting tunnel name — every value cited to a log/graph line, unknowns left unknown. The
       simulator's rule is rewritten to explain every row (self-test = the table), P3b-1 + P3b-2 re-simulated and
       re-finalized, P3b-1 dry/prerun. If no rule explains every row, the card returns with the table (judgement then
       decides a name-insensitive binder key for created tunnels).
     - **(c) Carry:** after an E1 stop `close_panel` hung ~7 min and LabVIEW had to be killed (pin3 `:374-394`; pin2 ~16 min
       FAIL hygiene) — a bounded close in stagekit's FAIL path is tooling debt, not ahead of P3b-1.
     - **(d)** Measured on the way: pin3 peak 650.4 MB at op 26 (pred 663.4 for all 31); prior-art c130-6 `novel`; dry
       31/31 FS [0,16,18] == sim; `--scratch-required` exit 3.
271. **(cycle 131 judgement, 2026-10-02 — after 131-1 PASS 3/0, 131-2 PASS 4/0)**
     USER-RULES: U1 (relied on; simulator naming and hook classification only — no computation, no design change).
     - **(a) Tunnel-naming rule ACCEPTED** (`stagesim.py:1499-1543,1668`, table `tools/bench/fs_tunnel_naming_table.json`,
       18 crossings, self-test 16/0, stagesim 105/0): a crossing-created tunnel takes the SOURCE TERMINAL's name for a SubVI
       source (`''` for a Function); a wired source names every face, an unwired one only the face it feeds. pin3 op 26
       (`#6865` `Image Out`, alone on w3040) is explained. The rival rule ("an indexing For exit drops the name") fits the
       same rows and gives the same P3b names, so the choice does not change P3b; the first recorded crossing that
       separates them decides — the binder's name gate catches a wrong guess at that op, as it did at op 26.
     - **(b) P3b-2's `p3b_x_rot` name `Value` (`#4580` Property, net w4878 without tunnels) is a graph-read prediction,
       not a run fact;** it is measured on P3b-2's own scratch run, not before. No extra LabVIEW act for it.
     - **(c) P3b-1 / P3b-2 re-finalized** (`plan_ring_p3b1.json` edbdba99, pred e4bba5b3; `plan_ring_p3b2.json` b25c1ecb;
       unsplit reference `plan_ring_p3b.json` 747d712e, c128b re-pinned 6/0); P3b-1 dry 31/31 + prerun 15/0, X10 663.4 /
       664.3 MB; `--scratch-required` exit 3 (census unpredicted, 31 rows) ⇒ scratch `pin4` per D-2026-10-01-01, then ONE launch.
     - **(d) guard_peer offline rule v2 ACCEPTED** (`guard_peer.py:236-386`, AST, measured before switch-on: fp-16/17/18/22/24
       5/5 pass, 53/53 recorded LabVIEW launches still held; 153 bench scripts flip to offline, 5 flip to LabVIEW, 0
       recipes). Not following subprocess/runpy is accepted: a real launch goes through a recipe/bgrun path that is still
       held. fp-27 (the tool's own measurement log, before the fix landed) is not `device-failed`. Open gate-fp: fp-19/20/21
       (stage_prerun) — drained by ONE stage_prerun tooling card after P3b-1's launch, never while a stage card is live.
