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
275. **(cycle 132 judgement, 2026-10-02 — at cycle start, before cards 132-1 / 132-2)**
     USER-RULES: U1 (relied on; gate thresholds and tool code only — no computation, no design change; none contradicted).
     - **(a) X10 gets the FINAL whole-VI read term** (+17.4 MB measured once, `stage_d1_ring_p3b1_scratch_pin4.log:446-447`;
       launch 680.4 MB `stage_d1_ring_p3b1.log:430`), each coefficient cited in `memory_model.json`. Self-test: P3b-1's
       bytes predict 680.4 ± 3 MB.
     - **(b) Once the model carries that term, its FAIL threshold is 690 MB** (PD272(b)'s launch stop), not 675: 675 was the
       planning margin for a model that LACKED the final read; a model that predicts the measured peak is compared with the
       measured-peak stop. MEMSTOP 700 and LabVIEW's ~695 error are unchanged. A predicted peak > 690 = re-cut (third half =
       user, PD266(b)).
     - **(c) The tunnel-name gate is per-op and data-driven:** after each crossing op the recipe compares every NEW tunnel's
       name with the simulator's predicted name for that op (read from the finalized plan/sim files, never typed); a
       mismatch stops the run like E1. Built for P3b-2 now; P4/P5 reuse it.
     - **(d) P3b-2's expected Error List is COMPUTED** by a script from the simulator's retired/loose-end wire set and the
       P3b-1 expected file (class totals, PD274(b)), never typed (retrospective-cycle131 carry).
     - **(e) gate-fp drain:** fp-19/20/21 fixed in this card with self-tests; fp-28 closed as a CORRECT refusal, no code change
       (retrospective-cycle131).
276. **(cycle 132 judgement, 2026-10-02 — after 132-1 FAIL 3/1, 132-2 BLOCKED)**
     USER-RULES: U1 (relied on; tool scope and prediction form only — no computation, no design change).
     - **(a) 132-1 A/B/C accepted:** X10 + final read 17.4 MB, FAIL 690: P3b-1 bytes 680.8 vs measured 680.4; P3b-2 681.7
       (provisional). Name gate `stagexec.tunnel_name_check` (self-test 5/0) scoped to `fs_border` crossing ops; the
       FS INNER tunnel naming (`fs_frame_to_frame`, real `error out` vs sim `''`, pin4 NEWOBJ 28340-28371) is unmodelled
       — a label only, accepted, not gated. c106e E1 re-pin to the X10 model accepted (15/0). fp-19/20 drained.
     - **(b) fp-21 is NOT on P3b-2's path:** PD264(b) already orders P3b-2's dry AFTER `--rebase` onto the real graph. Binding a
       provisional base's negative uids (`stagexec.py:786,1851`) is tooling for the NEXT pipeline prep (P4), stays open.
     - **(c) P3b-2's expected Error List is a RANGE** (total 50..52, loose ends 19..21, every other class = P3b-1's; computed by
       `errorlist_expect_p3b2.py`, P3b-1 calibration brackets its own read). The scratch read must fall in it; its measured
       per-class counts then become the launch's expected file (as PD274(b)). No extra LabVIEW act to pin w3268/w30592.
     - **(d) fp-28 stays open only because `gate_fp.py` has no close verb** — not a defect of the gate; add the verb in the
       next tooling card. 132-2's block was my card's own rule (no stage_prerun), not a gate fault: re-issued as 132-3.
277. **(cycle 132 judgement, 2026-10-02 07:2x — after 132-3 BLOCKED on fp-29, `diag_c132_2_graph_p3b1_prerun.log:21,25`)**
     USER-RULES: U1 (relied on; gate code only).
     - **(a) fp-29 is a real false positive:** X10 (`stage_prerun.py:1984-1987`) returns UNMEASURED for a script with no
       Executor plan, which includes read-only readers — it blocks the run that would record the meter. Rule: a script with
       NO Executor plan whose prerun shows 0 edit ops (X5: 0 create / wire / delete / RLE; `discard_work` = close without
       save) is modelled as N = 0, R = its whole-VI reads, + the final-read term; FAIL > 690 as PD275(b). A script with edit
       ops and no Executor plan stays UNMEASURED = FAIL (PD268(a) unchanged). Self-test both sides; drain fp-29.
     - **(b) Card 132-4 chains:** fix → reader dry/prerun → graph read → offline diff → `--rebase` P3b-2 → dry 39/39 + prerun
       → `errorlist_expect_p3b2.py` on the rebased plan → `--scratch-required`. Scratch and launch are cards 132-5 / 132-6.
327. **(chat card chat-S2, 2026-10-03 — USER: "가, 나 둘 다 적용" · "+-1개는 너무 적은듯")** STOP gates vs LOG-only gates.
     USER-RULES: the user approved the design and the tolerance; the chat may change the numbers only with the user.
     - **(a) One table, `tools/gateclass.py`**, imported by `stagekit.Stage.gate` / `census_gate`, `stagexec` (NAME-GATE,
       binding), `stage_prerun` (dry gate, X15 census), `census_predict`, `errorlist_check` and `hooks/guard_peer.py`.
     - **(b) STOP (unchanged):** PRIM/X17 class, Is Broken?/ExecState, cdiff (E3, PB), lost data wires (D, W1, TD's
       `unwired`), input/bed md5, MEMSTOP, Error List per class except loose ends, any count difference of a SEMANTIC class.
       Fail-closed: a class not in `NON_SEMANTIC_CLASSES`, a gate id not in `GATE_TABLE`, an unreadable detail = STOP.
     - **(c) LOG-only:** names (NG, NAME-GATE, BINDING-NAME); non-semantic counts (Terminal, Inner/Outer/ParameterTerminal,
       Invoke, loose ends) within max(5, 25 % of the predicted delta); labels ARITH (the check script's own arithmetic) and
       FIXTURE (stale fixture). Printed `  SOFT  `, never fatal, not a fail; one line each in `tools/bench/gate_soft_log.jsonl`
       (cycle, card, script, gate, expected, measured, class, rule) for the cycle-end batch review. Beyond tolerance = STOP.
     - **(d) guard_peer:** a log whose only FAIL lines are LOG-only owes no hypothesis review; any STOP line, exception,
       STOP-at-gate or timeout still owes one. Self-test `tools/bench/selftest_gateclass_s2.py` 12/0.
     - **(e) Replay of 130-141** (`tools/bench/s2_replay.log`): 49 non-PASS → 6 LOG (would continue), 38 STOP, 5 not a gate.
