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
328. **(chat card chat-S3, 2026-10-03 — USER: "메모리 낮추고 터널 개수차이로 멈춤은 유지하고 터널 단자행만 다를 경우 기록하자")**
     Three answers after chat-M2 (LabVIEW error 2 measured at 704.8 MB private, `tools/bench/diag_chat_m1_mem.log:170-173`)
     and PD327's open items. USER-RULES: numbers changed only with the user.
     - **(a) Memory limits lower:** X10 FAIL threshold 690 → **680 MB**, run-time MEMSTOP 700 → **695 MB**. ONE source:
       `tools/bench/memory_model.json` `fail_above_mb` / `memstop_mb`; `stagexec.MEM_STOP_MB` / `X10_FAIL_MB` and
       `stage_prerun.X10_FAIL_MB` read it (missing entry = error at import). The P4 session-2 scratch recipe (not launched)
       sets its stop to `SX.X10_FAIL_MB`; recipes of finished/released stages (the s01 scratch is held by the prior-art
       launch gate's sha record) and archived bench scripts keep their literals (history, not re-run).
       Consequence: the cycle-131 P3b-1 bytes (predicted 683.6) would now be refused (`selftest_x10_c132_1.py` T1 re-pinned).
       The card-level launch limit 675 (PD321(c)) is below 680 and unchanged.
     - **(b) Tunnel OBJECT count differences stay STOP:** `gateclass.TUNNEL_OBJECT_CLASSES` (LoopTunnel,
       FlatSequenceInner/OuterTunnel, SelectorTunnel, Tunnel), asserted disjoint from `NON_SEMANTIC_CLASSES`.
     - **(c) E1 face-row-only diffs are LOG-only:** a step diff whose only entries are terminal rows on tunnel faces, every
       owner tunnel present with the same class on both sides, and no edge / dangling / unbound entry, is LOG-only
       (`gateclass.step_face_rows_verdict`, `stagexec.compare` → `face_rows`, Executor prints `  SOFT  E1 …` and writes one
       `gate_soft_log.jsonl` line per new row, the run continues; record mode classes it `log`). `bind_new` no longer counts
       a new row on a tunnel that existed before the op as a new object. Face rows + an extra tunnel object, or + a wire
       difference, or a row on a non-tunnel owner, STOP. Self-tests `selftest_gateclass_s3.py` 13/0, `stagexec selftest`
       141/0 (T120–T124).
329. **(chat card chat-S4, 2026-10-03 — USER: "A, B는 도입하는게 좋겠고 4번의 경우 한 싸이클 내에서는 계속 이어서 작업하는게
     좋겠음")** One mechanism in `tools/stagexec.py` (section "card chat-S4"), generic for a P4 session file or a small subVI
     file built in its own VI. Self-test `tools/bench/selftest_stagexec_s4.py` 24/0. STRUCTURAL + offline; no stage run yet.
     - **(a) ADOPT the scratch (A):** after the scratch run's BGRUN END, `py tools/stagexec.py adopt --script <scratch
       recipe> --log <its log> --artefact <saved file> --input <bed> --input-md5 <md5> --required E1,PB,PS,...` checks the
       log's last segment (RESULT line, no STOP-class FAIL by gateclass, no hard marker, every required step-end gate has a
       PASS line), the artefact (a claudeDev file, not the input) and the input md5, then appends `adopt/1` to
       `tools/bench/adopted_scratch.jsonl`. The scratch recipe must SAVE its work copy under the stage's normal name
       (`Stage(work_name=...)`, rule-6 GUI save) instead of deleting it. `stage_prerun` launch gate: a stage recipe (or its
       `_scratch` wrapper — one key) with an adoption for the SAME plan md5s is REFUSED (no second run on the bed); a judgement
       session withdraws a record by adding `"revoked": "<reason>"`.
     - **(b) RESUME within a cycle (R):** in a recipe's ExecStop handler `stagexec.save_for_resume(s, x, e)` saves the scratch
       as-is, keeps it, and writes `tools/bench/resume/resume_<stage>_<ts>.json` (`resume/1`: from_step k-1, the binding as
       Part A's, the actions-prefix fingerprint, file md5, cycle). A later card in the SAME cycle: `bd = load_resume(rec, plan,
       cycle)` then `Executor(plan, be, from_step=bd["stop_after"], binding=bd)` on a work copy of that file — the existing
       Part-B entry compares the whole-VI read with simulated step k-1 and stops (FROM-STEP BASE) if op k had already changed
       the file. Refused: another cycle, a changed file, the bed itself, a plan whose actions 1..k-1 or base changed (a plan
       changed only after the stop point is accepted). Shift registers created before the stop: no resume (load_binding rule).
     - **(c) PARTIAL READS (B), dry side only:** `Executor(partial_reads=True)` replaces a checkpoint's whole-VI read with
       `backend.read_owners(<owners the simulated step changed since the last read>)` patched into the last read, when every
       new owner is the op's returned uid; structure creates, multi-owner creates (tunnels) and the last op stay whole
       (`partial_fallbacks`). Dry: same binding and every step diff 0 vs whole reads on plan_disp (38 of 47 reads partial) and
       plan_ring_p4_s01 (3 of 4). Trade-off measured: a real change outside the simulated diff is missed by a partial read and
       caught at the next whole read (B4: junk at op 25, stop at op 31). X10: `x10_model_peak(partial=)` counts only whole reads
       in R (+ `part_read_mb`, 0 until measured); the dry run's `reads_partial` feeds it.
     - **(d) LabVIEW read cost, measured** (`tools/bench/diag_s4_readcost.log`, read-only copy of the P4 session-1 file, fresh
       LabVIEW): whole `read_live` 105.7 / 35.6 / 24.7 s and +4.3 / +7.4 / +5.2 MB (:37-39) — parts: GObject census 9.2 s
       (+1.2 MB first, then 0), OpAllTerms_v1 13.2 s (~0 MB) (:40-43). Nearest per-node route: Diagram list 0.41 s, node_labels
       ~0.25 s + node_terms_uids ~0.24 s, ~0 MB; rows equal the whole read for 11/11 addressable owners (Property, Function,
       ControlReferenceConstant, SubVI, IndexArray, GrowableFunction, InRangeAndCoerce). NOT addressable (19/30): numeric /
       boolean / string / GenClassTagRef constants, every tunnel class, shift registers, Diagram-owned control terminals; and
       the route returns no term_class / owner_class / frame_diagram, which binding needs. So `LVBackend` has NO `read_owners`
       yet: partial reads stay off on LabVIEW until an owner-uid reader op exists (a build card; OPEN in result_chat-S4).

**Tool change, card 142-5 (2026-10-03; applies PD330(d)/PD331(d), no new decision):** `stage_prerun.rebind` files a real terminal
as OLD only when its identity (term uid, owner uid, name) is in stage N's base (same key as `stagekit.term_key`, PD325(b)); a uid
LabVIEW re-issued to a created node binds like any created terminal and is logged as `re-issued uid(s)` on the REBIND line.
Self-test `tools/bench/selftest_rebind_c142_5.py` (142-P1's case): before 1/3 (`selftest_rebind_c142_5_before.log`), after 4/0.

337. **(chat card chat-S5, 2026-10-03 — USER: "좋아. 지금 수정 내용을 S1이라고 할게", after the chat measured cycles 142-143: ~44
     of ~175 min were our checkers refusing good work, results 143-1/3/4/5)** Brief `tools/bench/cards/brief_chat-S5.md`.
     OFFLINE, STRUCTURAL; replay `tools/bench/replay_s5.log` 8/0, self-test `tools/bench/selftest_s5.log` 21/0.
     USER-RULES: U1 (relied on; checker/binder/protocol code only — no computation, no design change; Jev stays advisory).
     - **(a) ADDRESS BY POSITION (143-4):** `tools/addrcheck.py` is tier (a). Selector order = stagesim's: name → `<name>#k` →
       inner/outer → `value` alias → the POSITION TRIPLE (owner uid, terminal index, terminal class, direction) that
       `stagesim.simulate` now records per resolved end in `finalized.addr_pos`. `stage_prerun.rebase` resolves by name as
       before and, when the name does not bind uniquely, by that rule on the provisional base AND then only when the bound real
       row sits at the same position (`real_match`: unique class+direction on both owners, or the same index) — logged
       `ADDRESS-RESOLVED`. Anything else is `ADDRESS-UNRESOLVED` with the real candidates and the rebase refuses as before
       (never a guess). `--prerun` prints one `ADDRESS-CHECK` fact line per stageplan (advisory; X2's load_final_plan already
       checks input md5s and the schema).
     - **(b) 3 TIERS:** (a) code as above; (b) Jev "same terminal?" per unresolved item with its candidates — MEASURED on
       `tools/bench/addrcheck_labelled.json` (18 items from cycles 128-143): accuracy 0.611, 7 unknown
       (`tools/bench/addrcheck_jev_measure.json`, `jev_addr_measure_s5.log`) < 0.85 → NOT switched on (advisory stays off;
       re-measure to switch it on); (c) every item without one confident YES prints `ADDRESS-LLM-OWED` for the judgement
       session — no card re-review. `gateclass.address_only` + `guard_peer.log_failure`: a failed run whose ONLY failures are
       address/format mismatches (`ADDRESS-UNRESOLVED`, "does not bind uniquely", a prose field over a length limit) owes no
       hypothesis review; a traceback, timeout, STOP or any other failing gate still does.
     - **(c) BY-DESIGN EL DIFFERENCE (143-1/143-2):** the fixed EL rule moved to `tools/elrule.py` (the bench file re-exports).
       `errorlist_check` on a MISMATCH that is not loose-ends: `by_design` re-derives the prediction from the bed's own plan
       step files; verdict OK + `EL-BYDESIGN` soft line only when nothing is missing, every extra is an unwired-Local or
       While-cond item, per class ≤ the re-derived new items, and re-derived total == measured. Otherwise STOP. Census
       differences stay under PD327's tolerance (unchanged).
     - **(d) PROSE vs MACHINE FIELDS (143-5, 143-1):** schemas mark prose fields `"x-prose": true`; the validator skips their
       length gate unless the schema also says `"x-limit": true` (kept on result/task/next/verdict/... as the communication
       budget; dropped on stageplan `why`/`goal`). `protocol.machine_view` / `prose_fields` are the one helper;
       `stage_prerun.negative_uids_left` replaces the per-script token scan (4 pred scripts patched). Releases: `py
       tools/protocol.py release <review> --kind FIXED|REFUTED --slug --path --line --what` writes a validated `release/1`
       record (`docs/protocol/release.json`; slug ∈ the review's own PRIOR-ART slugs; FIXED path exists and post-dates the
       review) + the legacy line, which guard_cycle/stop_record keep reading; nothing is written on a failed check.
     - **(e) BIND-TIME INPUT MD5 (143-P1):** `protocol.bind` refuses a NEW binding whose task/1 `inputs[].md5` differs from the
       file on disk (a re-bind of a started card is not re-checked).
     - Replay (offline, `replay_s5.log`): 143-3 + 143-4's plan ('value') rebases on eda9db40 with REUSE-NOTED 23276 and
       ADDRESS-RESOLVED (value-alias / unique-dir), actions == 143-5's rebased da66a030 in every machine field → 143-4 and
       143-5's fix card not needed; 143-5's 545-char why validates and its RB scan finds no negative uid → 143-5's two failures
       not needed; 143-1's read vs the 51-entry expectation → by-design log, re-derived 53 == 53 → no FAIL. 143-3 needed 143-4's
       PD334(b) uid fix as well (already in).
     - Existing self-tests (`run_selftests_s5.log`) 42/5; all 5 failures predate S5: stagekit J1 (same as
       `selftest_stagekit_c112d.log`), stage_prerun c106e E1 and c114 R4 (same in `s4_regress.log`, 08:18 today),
       `selftest_rebase_uidreuse_c143_4` (its fixture plan was rebased by 143-5: "base is not provisional"),
       `selftest_guard_peer_scan_tmp` (a throwaway census with a non-schema RESULT line).
338. **(chat card chat-E3, 2026-10-04 — USER: "훅 작동을 위해서는 프론트매터에 특정 플래그를 달도록 강제해야겠음" · "이번 훅을 넣는
     가장 큰 이유는 초장에 에러 발생을 극소화하여 시간 낭비를 최소화하는게 목적임" · "에러 잡는 훅도 만들어줘")** Catch errors at
     WRITE and LAUNCH time. OFFLINE, STRUCTURAL; self-test `tools/bench/selftest_c_e3.log` (fp-36..40 as regression cases),
     replay `tools/bench/replay_c_e3_142_143.log`, suite vs HEAD `tools/bench/selftest_c_e3_suite.log`.
     USER-RULES: U1 (relied on: hook / checker / protocol code only - no VI, no computation, no design change).
     - **(a) SCOPE HEADER on every tools/ script** (`tools/scope_header.py`): `# ---` / `# labview: none|read|build` /
       `# hardware: none|camera|motor` / optional `# offline-args: <argv tokens>` (+ required `# evidence:`) / `# ---`, at
       the top (12 lines) or the tail (8 lines). Migration APPENDED it to 1716 tracked scripts (mtime kept, so every
       `file:line` citation and every mtime-ordered gate is unchanged); inference: import closure (guard_peer v2) +
       subprocess invocations → none; LabVIEW but no recipe/save/GUI/Run → read; else build (unclear = build).
       `canonical_bytes` strips the block: `stop_record.sha256_of`, `stage_prerun.sha256` and task/1 input pins hash
       without it, so every release stamp and dry/prerun record written before still matches (58/58, 338/338 measured).
     - **(b) WRITE TIME** (`tools/hooks/guard_write.py`, PostToolUse Write|Edit|MultiEdit|NotebookEdit): header valid,
       compiles (py: compile(); ps1: the PowerShell parser), HONEST (`none` may not import gscript/COM, start a recipe,
       runpy a file, invoke lv_gui.ps1/LabVIEW.exe, or import stagekit/stagexec whose used part reaches LabVIEW without
       `evidence:`; `read` may not save/GUI/Run), JSON with a known schema validates (machine-field lengths; prose length
       stays ungated per PD337(d)), task/1 input md5s match, an OPEN card (no result, < 24 h) pinning the written file at
       another md5 is named (143-P1), a prior-art release line must use one of that review's verdict slugs (143-1).
     - **(c) LAUNCH TIME**: `protocol.check_command` judges every tools/ script a command RUNS by its header (declared ≤ card
       flags; offline-args applied to its own argv; missing/invalid header or a compile error refuses); text heuristics stay
       only for scripts outside tools/, and LV_CMD_RE only on segments a read-only program does not lead. `guard_bash`
       refuses a headerless/non-compiling tools script for every session. fp-39: `stagexec.py` declares `offline-args:
       selftest adopt`. fp-37: `stage_prerun.py` declares build with every offline mode listed (`--dry --prerun
       --scratch-required --rebase ...`); `stop_record.offline_checker` / `guard_cycle.offline_only` accept any program
       whose honest header makes THIS run labview none. fp-38: `git add` / `git commit` are read-only for the stop record.
       fp-36: bgrun puts the launching card into the child's env (CARD_ID / CARD_LABVIEW from the launch ledger) and
       `protocol.result_line` stamps `card`/`labview` into the RESULT line; `guard_peer` RULE-OTHER-CARD frees a BOUND card
       from a failing log another card launched (owner = RESULT `card`, else the newest ledger row not after the run's
       start); the judgement session and the owner are still gated. fp-40 (chat-A1): a NAME of lv_gui.ps1/LabVIEW.exe in a
       regex or message is not an invocation (23 migrated headers corrected; `protocol.py` = none); a .ps1 is build only when it
       INVOKES LabVIEW (`& ...lv_gui.ps1`, `-Action`, LabVIEW.exe, `ComObject LabVIEW`), so `peer.ps1` and the
       `peer_*.ps1` dispatchers are none; the stub-only `selftest_cycle_runner*.py` declare none with evidence.
     - **(d) WAITING** (`result/1` and `result-line/1` enum): `stage_prerun --dry/--prerun` on a PROVISIONAL base whose only
       failures are the base's unbound objects (prerun: only X1/X5/X10-provisional) prints RESULT WAITING, gates.fail 0,
       rc 0, records status WAITING (never a launch PASS); `protocol.result_failed` treats it as not failed → no review owed.
     - **(e) PRIOR-ART ON THE DIFF** (`tools/priorart_diff.py`): a recipe copied from the last APPROVED script of the same
       name pattern (digits masked; stop record released/novel for its current bytes) is diffed on CODE lines (docstrings
       and comments blanked); names/paths/numbers-only lines owe nothing; `guard_cycle` allows (PRIORART-DIFF line) when no
       substantive line and no new structure class remain, else its refusal names them and `prior_art_review.py
       --diff-from <sibling>` reviews only those. s03v18 vs s02v18: 9 parameter-only, 0 substantive, new class
       `create:WhileLoop` → only that class would be reviewed.
     - cycle_runner.py / guard_session.py belong to chat-A1: `scope_header.KNOWN` supplies cycle_runner's offline modes
       (`--dry-run --dry-cmd --no-motor-hooks`, allowed since 2026-09-24) until its owner adds them to its header.
339. **(chat card chat-F2, 2026-10-06 11:5x — USER: "그러면 1~3번 모두 적용할 가치가 있겠다. 적용하도록 하자", three ideas taken
     from CLI-Anything; purpose per PD338: catch errors at the START)** Per-function contracts, records and generated docs.
     OFFLINE, STRUCTURAL; self-test `tools/bench/selftest_fn_f2.log` 31/0; suite vs HEAD `tools/bench/selftest_f2_suite.log`
     70 tests, 0 NEW failures, 8 pre-existing (stagexec.py selftest included, passes).
     USER-RULES: U1 (relied on: wrapper / checker / records / doc generator only - no VI, no computation, no design change).
     - **(a) ONE STANDARD OUTCOME + DECLARED POSTCONDITIONS** (`tools/fncontract.py`): every call ends `ok | no_output |
       failed | timed_out`; `TABLE` holds one row per LabVIEW-touching public gscript function (113, AST closure) and per
       `Stage._op` verb (34) - `post` + `measure` (inline / result / existing-raise / caller) + `on_fail` (raise / record),
       or `none - <reason>` (coverage checked: none missing, none without a reason). The shared `check()` fails AT THE
       CALL with the measured numbers (old message text first). GENERALISED, not duplicated: gscript.delete_object's
       `expected 1 object gone` (gscript.py:2861) and term_index's 0/>1 match ValueError (gscript.py:5009, now
       PostconditionValueError, still a ValueError). gscript wraps every row at import (`FNCONTRACT_WRAPPED`,
       gscript.py:5218; `__wrapped__` kept). `Stage._op` stores `rec["outcome"]` (stagekit.py:620). NEW CHECKS:
       Stage.delete_object removed == 1 and Stage.delete_wire found == 1 (stagekit.py:656-669) - a DOUBLE delete used to
       return False silently and now stops at the call; delete_wire's removal is NOT re-read (an extra whole-VI Wire read
       per delete would move the X10 model) - stagexec's next step read covers it. `record` rows (wire_remove_loose_ends,
       set_control_label, the `_opcw_call` wirers, creators returning err) never raise: the dict-returning contract stays.
     - **(b) TEST PLAN FIRST, RECORD PER FUNCTION** (`tools/fn_records.py`, registry `tools/bench/fn_records/<fn>.json`,
       schema `fnrec/1`): 86 plans written (every function the P4 v18 plans route through + stagekit/stagexec direct calls +
       every Stage verb + the 5 recipe functions); 19 cite the old `scratch_verify` records as `legacy_evidence` (no source
       md5 → never FRESH). A record is fresh only while its `src_md5` == the def's current source md5. ADVISORY GATE:
       `stage_prerun.fn_record_gate` in `_check_units` (stage_prerun.py:4551) appends `FN-GATE ADVISORY | <unit> | n of m
       ...` to `tools/bench/fn_gate.log`; config `tools/bench/fn_records/gate_config.json` mode `advisory`, SWITCH
       CONDITION: every function of the 3 P4 v18 plans has a fresh PASS (card chat-F3); `auto: false` → a judgement session
       flips `mode` to `refuse` when the line says `switch condition MET`. Records are added by `--add-record` (plan
       required). The real-LabVIEW runs are card chat-F3.
     - **(c) CAPABILITY TABLE GENERATED FROM CODE** (`tools/gen_capabilities.py`): a marked block APPENDED at the end of
       docs/toolkit-capabilities.md (prose above byte-identical; 152 rows: name, args, contract, record, file:line);
       idempotent. doc_lint **L12** (WARN) reports drift: missing / gone rows, stale records, changed contract/record/line.
       docs/NAMES.md NOT generated: its terminal names are measured from LabVIEW, not derivable from code or records.
     - Gate false positive **fp-41** (`checker:stage_prerun:is_vi_modifying`): the first self-test imported stagekit with
       COM stubbed and was refused as a VI-modifying stage; queued, not patched; the self-test now executes the real defs
       from source (ast) without importing gscript/stagekit.
340. **(card chat-F3b, 2026-10-07 04:1x-04:5x, escalation rung 1 of chat-F3; applies the chat decisions of 2026-10-07 in
     `tools/bench/cards/brief_chat-F3b.md`)** Real-LabVIEW function records, part 2. LabVIEW ran ONCE (scratch only).
     USER-RULES: U1 (relied on: a wrapper check + scratch-only tests - no VI of the bed chain or original, no computation).
     - **(a) PRECONDITION AT THE CALL** (chat decision 1): `tools/fncontract.py` `PRE` (+ `precondition_error`,
       `PreconditionFailed`, `contract(fn, f, ns)`, `install` passes the module globals). gscript.loop_in declares
       `src_present == 1` = Traverse(src_cls or 'SubVI')[src_index] exists (gscript.py:1530). MEASURED ON THE FAILURE PATH
       ONLY: a call that succeeds reads nothing extra (X10's read count unchanged); a call that raised is re-examined and,
       when the precondition does not hold, fails with PreconditionFailed (a RuntimeError; the original 1055 text first,
       the reason appended; outcome `failed`); a held precondition re-raises the original error unchanged. gscript.py is
       untouched (loop_in's record stays fresh). Self-test `tools/bench/selftest_fn_f3b.log` 36/0 (P10 a-e new; P6d re-pinned
       to the chat-decision (2) rule: required_from = v18 + s03v18, mode advisory unless the switch condition is MET).
     - **(b) G1 run 3 NOT launched:** fntest_g1.py is at RETRY_CAP 2/2 for 'chat 2026-10-07' (stage_runs.jsonl:109-110) and
       this card carries no `retry_of` (`stage_prerun.py --check-launch` refusal, measured). The G1 create cases run instead
       as the BED BUILD of the new runner `tools/bench/fntest_g2.py` (117 lines, FNTEST-EXEMPT; helpers `fntest_lib.Bed` /
       `Kit`), in the P4 order: SubVI first, a While, a While inside its body, the P4 donors.
     - **(c) G2 run 1** (`tools/bench/fntest_g2.log`, 136 s): A1 drop_subvi, A2/A3 loop_in (While on D0, While in a While
       body - both PASS with a SubVI present), 15 create_primitive_nested with the P4 donors (PRIM-GATE read-back: Wait (ms) /
       Select class 'Function', Replace Array Subset 'GrowableFunction'), A5 fs_create - every case PASS; then STOPPED at the
       first `Bed.read()`: `fntest_lib.owners_of` (written in chat-F3) takes read_live objs' `owner` as a uid, the value is the
       owner's CLASS name ('WhileLoop') -> ValueError (our harness, fntest_lib.py:280). Records: 17 PASS written
       (runs/fntest_g2_20261007_043756.json); gscript.loop_in / stagekit.op:loop_in now fresh-PASS (chat-F3's no-SubVI FAIL
       kept as history). Hygiene: handles 34418 after work / 33995 at exit, scratch deleted, files left [], LabVIEW gone.
     - **(d) STATE after run 1 (superseded by (e)):** 16 fresh-pass, 0 fresh-fail, 42 planned of the 58; retry = the chat's.
     - **(e) CHAT DECISIONS 04:4x (to this card): (1) fix `owners_of`, rerun G2; (2) G2's bed-build records ARE the G1-run-3
       evidence, no retry card for fntest_g1.py; (3) PRE stays on the failure path.** `fntest_lib.owners_of` now resolves each
       Diagram's owner UID through `build_d1_v0.owner_of` (OpOwnerChain_v1), once per diagram (cache); a body/frame the runner
       created is bound by the create's own return (the Executor's `_bind_create` source) - FS frame #291 read no owner and took
       the create's ['FlatSequence', 281]; offline `tools/bench/selftest_fntest_owners.log` 4/0. **G2 run 2**
       (fntest_g2.log:298-853, 150 s, gates 22/0): every bed and route case PASS - const_sr, wire_sr LeftIn/RightIn, stop on a
       new and an outer While, nested in/out of a loop, cfw, branch off an output tunnel, connect_term_uid into an FS frame +
       RLE (broken_after False), 3 delete_wire, delete_object, ctlsink, wire_control, gscript.delete_object(verify=True),
       both negative double deletes outcome no_output - EXCEPT **B11 (FINDING): the 'indicator' route (a WIRED source -> a bare
       indicator terminal) on a bed that is broken by design: gscript.wire_indicators raises 'target BROKEN after wiring' (its
       ExecState check) and LVBackend.indicator stops because no sink gate was declared** (fntest_g2.log:737; stagexec.py:2844-2852
       - a P4 recipe that routes a wired source into an indicator must declare a sink gate, check_sink_gates). gscript.close_panel
       FAIL is OUR runner's double close: S1 closed the save scratch, then stagekit.drop_scratch (stagekit.py:538) closed it
       again -> LabVIEW 0x47D (fntest_g2.log:765). Handles: 33998 restart, 34013 start, 34743 after the bed, 35040 after the
       routes (+297 over 323 recorded calls = +18 per 20), 33995 at exit; scratches deleted, files left [], LabVIEW gone.
     - **(f) COVERAGE of the 58 (switch scope v18 + s03v18):** 55 fresh-pass, 3 fresh-fail (gscript.close_panel,
       gscript.wire_indicators, stagekit.op:wire_indicators), 0 without a record -> switch condition NOT met, gate_config.json
       stays ADVISORY (by the stated rule). All 86 plans: 59 fresh-pass, 3 fresh-fail, 24 planned (none in the switch scope).
       Capability block regenerated, drift none.

347. **(card chat-T3, 2026-10-07 — USER: "세 가지 다 고치도록", on `tools/bench/livebench/report_4arms.md`: every bench arm
     lost time to the same tool faults and fixed them only inside its own worktree.)** Numbered 347 because PD341–PD346 are
     the bench arms' own decisions in `V6_bench\<arm>\docs\d1\tooling.md` (cited by `docs/chat-handoff.md`); main skips them.
     - **(a) STOP lines; adopt reads structured lines only.** Every real stop prints `STOP {"schema":"stop-line/1","kind",
       "message"}` (`tools/protocol.py:354-394`): stagekit.run on a fatal gate / exception (`tools/stagekit.py:1536,1542`),
       its sys + thread excepthooks (:142,171), `stagexec.report_stop` (ExecStop / MEMSTOP), bgrun TIMEOUT
       (`tools/bgrun.py:332`), lv_stallcheck's STALL record. `stagexec.adopt_verdict` (`tools/stagexec.py:3969`) reads ONLY
       RESULT, STOP and stagekit's fixed-format gate lines: a docstring echo is prose; a STOP line, a STOP-class FAIL, or a
       failing RESULT not covered by LOG-class FAIL lines refuses. Gate-flip report (`tools/gate_flips.py`, ported from arm
       A): `tools/bench/gate_flips_chat_t3.json` + `_explained.json` - 5017 logs, 215 refused->accepted (prose 'ExecStop' /
       'MEMSTOP' x212, incl. all four arms' s03 scratch log), 184 accepted->refused (a FAILING RESULT the old adopt never read;
       no adopted log among them), soft_only / address_only 0 changed. Other free-text gates swept and LISTED there (guard_peer,
       audit_cycle, cycle_runner firefighter, gate_fp, jev); the launch path was already structured.
     - **(b) Created-object identity by RECORD.** The executor appends `sim id -> real uid (+ class, owner)` to
       `tools/bench/creation_map/<stage>_<plan md5[:8]>_<ts>.jsonl` the moment it binds (`Executor._cmap_record`,
       :1987; real backends only); `stage_prerun --rebase` finds the map by sim_of plan + md5 + the graph's VI (or
       `--creation-map`), binds from it FIRST and infers only the rest, one `FALLBACK` line each (`tools/stage_prerun.py:
       3665-3740,3850,3977`); rebind/rebase rows are dedupe'd (arm A13K's fix). In-VI TAG prepared, OFF
       (`tools/bench/creation_tag.json`; LabVIEW test plan `tools/bench/fn_records/planned/description_tag.json`).
     - **(c) Row-less While owner.** `loop_parent` takes a row-less loop's parent from the recorded owners map when nothing
       else places it (`tools/stagexec.py:1284`): While #16483 is listed on diagram 23166 only (was 179 of 180).
     - **(d) Bench cost collector.** `lb_collect.costs` counts a session only when its transcript started in the run window
       (`tools/bench/livebench/lb_collect.py:127-210`); A13 $234.23 -> $123.11 (three echoed 09-25/26, 10-02 sessions excluded);
       A, B, A13K unchanged; `report_4arms.md` corrected.
     - Self-tests: `tools/bench/selftest_t3.log` 22/0 (recorded s03 -> s04 graphs of arm A13K: rebind WITH the map binds all
       15 nodes + the row-less While, 0 node fallbacks; identical pairs swapped in the map -> refused). Owed after the
       experiment (LabVIEW): the first real stage run writing a creation map; the Description measurement; the s04 rebase's
       address stage (#-28.'inner', #-45.'cond' unresolved - arm A13K's addrcheck face fix is not in main).
     USER-RULES: U1 (relied on: checker / executor bookkeeping / rebase binding / collector code only - no VI, no stage
     computation, no design change; the executor's ops and their order are unchanged, the map is a side record) and U2
     (offline only: rig state 실험중, no LabVIEW opened).

348. **(card chat-T4, 2026-10-07 — fault 2 of the user's fix request, PD347 open item: the s04 rebase refused at ADDRESS
     #-28.'inner' and #-45.'cond'.)** Arm A13K's address fix (its card 145-a3-1, `V6_bench\A13K` diff vs 298a0030) PORTED,
     only the two address classes; A13K's bind-log seeding (145-a1-2) is NOT ported - main binds by the creation map (PD347(b)).
     - **(a) Face / 'cond' on the REAL side.** `tools/addrcheck.py:141-214` ADDS `real_face`, `cond_bind`, `cond_sinks`,
       `obj_class` (A13K's code, `resolve` / `real_match` untouched); `tools/stage_prerun.py:4300-4321` calls them in
       `rebase` after the name / position tiers and KEEPS the plan's name ('inner' / 'cond'). Face: the sim row is of that
       face class, bound by conn / map / map-pos, the real owner has exactly ONE row of that face and direction, and it IS
       the bound row. 'cond': only the PD316 form `{'uid': <While>, 'term': 'cond'}`, sim and real owners WhileLoops, exactly
       one cond_row sink in each body, the real one unnamed, consistent with any binding of the sim sink. Else UNRESOLVED
       as before. One translation: A13K's terminal mode `record` = main's `map-pos` (`BOUND_MODES`, addrcheck.py:148).
     - **(b) Evidence (offline, structural).** `tools/bench/selftest_t4.log` 19/0 on `tools/bench/fixtures/cmap_s03s04`:
       a13/a15 -> #29548.'inner' (row 29582, M[-32], mode map-pos), a20 -> #16483.'cond' (body 29699, sink 29710), no
       UNRESOLVED; rebase with re-simulation final, 49 uids, 23 steps, cdiff 16; negatives N1-N8 refused.
       `tools/bench/prep_t4_s04_sandbox.log` 8/0 (second run; the first died on the script's own missing mkdir): the s04
       pipeline on main's code in a %TEMP% sandbox - provisional simulate -> rebase (actions / open_rows / cdiff == A13K's
       rebased plan 4de3fa39) -> A13K's recipe a5268776 + pred 6a71540e with only paths / pins re-pointed -> DRY PASS (E1 19
       ops) and PRERUN 16/0 (WARN X13 x3, X14 23 > 15), as A13K measured. Main gets NO s04 plan / pred / recipe: main's s03
       has not run and A13K's s03 graph is not main's.
     - **(c) Regressions.** `tools/bench/selftest_t4_regress.log` (selftest_t3_regress driver): 7 PASS incl. selftest_t3
       22/0 (C7 now reaches carry_fs - given `out_root` %TEMP%), selftest_s5 21/0, stagexec 141/0; the 3 FAILs are PD347's
       carry, same messages at HEAD (c133_1, uidreuse_c143_4: 'base is not provisional'; c106e E1 X17); 2 skipped (labview: read).
     USER-RULES: U1 (rebase checker code only; no VI, no stage computation) and U2 (offline only, rig state 실험중).
349. **(card chat-T5, 2026-10-07 — USER "1번 진행", report_4arms faults 1 + 5; offline, structural)** (a) `tools/elrule.py` = arm A13K's rule (144-a2-2): SR class (RSR inner sink unwired) + A narrowed by terminal class (a C/SR row is never also A); s01 51 / s02 53 / s03 55 == the recorded reads (`tools/bench/selftest_elpred.log` 15/0, R1-R3; `selftest_s5` 22/0); over 45 finalized plans only s03v18 (+3 -> +2), l2b2a (0 -> -2 = recorded L2 b1->b2a SR 2 -> 0) and never-launched p4s1 change. (b) `tools/stagesim.py measured_term_class`: a created node's terminal class comes from `tools/bench/termclass_table.json` (27 real reads; Function = Parameter/OverridableParameterTerminal, never Terminal) when its terminal set is measured, else the declared class; `stagexec.bind_new` unchanged (exact). `selftest_t5_termclass.log` 7/0: the B/A13 op-2 p4_wait binds, a different real class stops; stagesim selftest 105/0. Real LabVIEW must still confirm: the next s03 run reads 55 with 2 SR items logged by design; s04 op 2 (p4_wait) and op p4_or_w1 bind. USER-RULES: U1 (checker / simulator code only; no VI, no stage computation) and U2 (offline only, rig state 실험중).
