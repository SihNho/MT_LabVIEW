---
type: decision
kind: topic
status: current
date: 2026-10-02
parent: docs/d1/INDEX.md
tags: [d1, ring-buffer, p3b, pre-decided]
---

# Ring buffer P3b (P3b-1 / P3b-2) — decisions from 268 on

Scope: the slot writes of loop 1.1 (IMAQ Copy + error guard, per-slot `TransPos`/`RotPos`/`FrameIdx`, `Num(i)`,
`Latest`), split into P3b-1 and P3b-2 by predicted memory. Everything decided up to 267 is in the frozen
`docs/d1-loop12-17-split-plan.md` (PD258–267 at :2749–2973); its in-force lines are in `docs/d1/INDEX.md`.

How to add: see the 5-line note at the top of `docs/d1/INDEX.md` (next number = 1 + the highest `NNN.` in
`docs/d1/*.md`, never below 268; a `USER-RULES:` line in every item; one line added to the index).

## Pre-decided

269. **(cycle 130 judgement, 2026-10-02 — after 130-5 FAIL 3/1, `plan_ring_p3b_split_c130_5.log`, `diag_c130_5_frames.log`)**
     USER-RULES: U1, U9 (relied on: the FINAL graph is unchanged — split end == unsplit 70, 10244 objects / 5933
     terminals / 1974 wires; only the cut point between two never-run intermediates moves; none contradicted).
     - **(a) Memory cut ACCEPTED:** P3b-1 = N 31, BIND 18, R 20, predicted 663.4 MB; P3b-2 = N 39, BIND 14, R 16,
       664.3 MB (both ≤ 675, X10 model PD268(a)). Split self-test 12/0. The cut moves FS frame f0's `Num(i)=-1` group
       (9 rows) into P3b-2; only 4 cuts were valid and the 2 under 675 both do that (next best keeping f0: 687.1).
     - **(b) An EMPTY f0 after P3b-1 is accepted** (f0 0 / f1 16 / f2 18 terminals in the simulated end state). P3b-1 is
       broken by design and never run; PD238(c)'s order (−1 → copy → values → BufNum → Latest) holds in the FINAL graph,
       which P3b-2 completes. PD261(d)'s "IMAQ Copy + guard together" holds (both in P3b-1).
     - **(c) P3b-1's FS/FU recipe gates compare each frame's terminal count with the simulator's predicted end state**
       (from the finalized plan/pred, never typed) instead of "every frame holds rows" (`stage_d1_ring_p3b1.py:51-52,66`);
       docstring `:1-11` updated to the new cut. Same change for P3b-2's gates when it is rebased.
     - **(d)** Broken-file count unchanged: P3b-1 = 3, P3b-2 = 4 of 6.
272. **(cycle 131 judgement, 2026-10-02 05:4x — after 131-3 FAIL 1/1, `stage_d1_ring_p3b1_scratch_pin4.log:446-447`)**
     USER-RULES: U1 (relied on; a memory margin on a never-run intermediate — no computation, no design change).
     - **(a) Scratch pin4 is ACCEPTED as the structural pass of P3b-1:** 22/0 gates, every checkpoint == sim through op 31,
       FS [0,16,18], both crossing names as predicted (`Image Out`, `current image number`, `pin4.log:522-543`), bed
       unchanged. The only miss is memory: the X10 model hit the op-31 meter exactly (663.4 MB) but the FINAL whole-VI read
       added +17.4 MB (vs ~+4.1 for earlier reads) ⇒ measured peak 680.8 MB, over the planning threshold 675.
     - **(b) Launch margin re-decided from the measurement:** 675 (PD266(b)) was a PLANNING margin for an unmeasured model
       against LabVIEW's memory error at ~695 MB (129-4, error 2) and MEMSTOP 700. With the same sequence now measured at
       680.8, P3b-1's launch-time measured-memory stop (`plan_ring_p3b1_pred.json` `fail_above`) is **690 MB**; X10's model
       threshold stays 675 for PLANNING. A launch that stops at 690 is a clean FAIL on a copy (bed untouched), not damage.
       No re-cut: P3b-2 (664.3 model) would carry the same final-read term, and a third half is the user's (PD266(b)).
     - **(c) Next card does S3 (scratch Error List count-only, deletes the scratch) → S4 (measured census into pred, dry +
       prerun) → ONE launch → final full Error List read + expected file**, returning at the first miss. P3b-2 gets the
       same 690 stop when rebased.
     - **(d) Tooling carry (with fp-19/20/21, after the launch):** X10 lacks the final-read term (+17.4 MB measured once);
       add it with its log citation so P3b-2/P4/P5 sizing predicts the real peak.
273. **(cycle 131 judgement, 2026-10-02 06:0x — after 131-4 FAIL 16/3, `stage_d1_ring_p3b1_el_scratch.log:183-190`)**
     USER-RULES: U1, U9 (relied on: a loose-end wire has no sink and executes nothing, so clearing one changes no
     computation; no contradiction).
     - **(a) Hypothesis (unverified):** the scratch's Error List is 53, not 54, because one `wire_remove_loose_ends` row
       (PD255(b)) cleared the new stub AND one pre-existing ORIGINAL stub on the same net — RemoveLooseEnds acts on the
       whole wire. Only the class `wire has loose ends` differs (22 vs 23); the reader names no item.
     - **(b) Proceed under it (CLAUDE.md 2c), non-destructive:** the next card names the missing item offline (diff the P3a
       expected 55 vs the scratch read 53 by class + location; map it to the P3b-1 RLE rows' target nets), dispatches the
       owed hypothesis review with that evidence, writes census + expected 53 + `fail_above` 690 into the pred, and makes the
       ONE launch. The launch does NOT wait on the naming result; the bed moves only after judgement reads it.
     - **(c) The runtime stop stays stagexec's `MEM_STOP_MB` 700** (`stage_d1_ring_p3b1.py:41`); 690 is the post-run check
       in the pred. No recipe edit for it (a recipe edit would re-open dry/prerun for no safety gain: LabVIEW errors at ~695).
     - **(d) If the named stub is NOT on an RLE-targeted net, the launched file is NOT accepted as the bed** until judgement
       decides; the launch costs one copy, never the bed.
274. **(cycle 131 judgement, 2026-10-02 06:3x — after 131-5 FAIL 4/1: launch PASS 22/0, final read not made)**
     USER-RULES: U1, U9 (relied on: loose ends execute nothing; the saved file's computation-bearing graph == sim end).
     - **(a) P3b-1 LAUNCHED:** `claudeDev\D1_ring_p3b1_20261002_060910.vi`, md5 `9d7bf287…`, 22/0 gates, FS [0,16,18] == sim,
       census == pred, peak 680.4 MB (≤ 690), bed P3a unchanged (`stage_d1_ring_p3b1.log:430-474`). The wires the plan
       retires are `[653, 3040, 3747]` — ALL on nets the plan rebuilds and RLEs (`plan_ring_p3b1.json:476-486`; review
       `archive/peer/2026-10-02-hyp-c131-5-el53.md` names w653/w3747 as the alternative). PD273(d)'s non-acceptance case
       ("stub NOT on an RLE-targeted net") is therefore excluded by both explanations; which of the three it was is not needed.
     - **(b) Error List debit is by CLASS, not by entry:** `stage_d1_ring_p3b1_el.py:38-45` debits `pred.removed` from the
       LAST `wire has loose ends` entry and went negative. The expected file for a final read states the CLASS total
       (loose ends 22, total 53); per-entry counts are re-pinned from the measured final read, never predicted. Same for P3b-2.
     - **(c) Bed acceptance condition:** the final full read of the launched file = 53 items AND its per-class counts equal
       P3a's except `wire has loose ends` −2 (24 → 22). Met ⇒ `current-bed:` moves to the P3b-1 file (broken-file count 3 of 6).
     - **(d) Carry:** the recipe has no explicit tunnel-name gate (names are covered only through E1 checkpoint == sim) —
       add one for P3b-2 with the X10 final-read term (PD272(d)) in the stage_prerun tooling card.
278. **(cycle 132 judgement, 2026-10-02 07:4x — after 132-4 FAIL 3/1, `stage_prerun_c132_4_rebase_p3b2.log:3`, `diag_c132_4_rebind_keys.log:4-7`)**
     USER-RULES: U1, U9 (relied on: a rebind must map every plan-referenced terminal to the SAME physical terminal — a wrong
     map, e.g. Unbundler `code` for `status`, would change what the guard selects on; the rule below forbids that; none contradicted).
     - **(a) Facts accepted:** real P3b-1 graph `graph_ring_p3b1_20261002_073225.json` (6cfa6ecb; bed md5 unchanged); wire uids
       1958/1958 real vs sim, `#6810` nets 9/9 wires with the same terminals, 0 swapped loose ends (answers 131-6's open point);
       memory after load 584.1 / after read 599.9 MB.
     - **(b) The rebase refusal is a SIMULATOR LABEL gap, not a graph difference:** the rebind key includes `term_name`
       (`stage_prerun.py:2896`) and stagesim labels FS inner tunnels `''` (real `error out`, PD276(a)) and the donor Unbundler's
       outputs `element` (real `code`/`source`/`status`).
     - **(c) Rebind rule:** bind created terminals by CONNECTIVITY first (a terminal on a wire whose other end is already bound
       takes that wire's real terminal), then by (class, owner, frame, direction, position among same-owner terminals); names are
       LOGGED as label diffs, never keyed. A terminal the P3b-2 plan REFERENCES must bind uniquely by connectivity or by a
       measured map, else REFUSE. The Unbundler's `status` output must bind to the terminal wired to the `Select` (self-test
       asserts it on the real graph). Not modelling the names in stagesim (labels only, two classes, PD276(a)).
     - **(d) Card 132-5:** rebind rule + self-test → `--rebase` → dry 39/39 + prerun → expected-EL range → `--scratch-required` →
       full scratch run of P3b-2 on a byte copy (D-2026-10-01-01; stop 690, name gate, Error List count-only in the range).
       The ONE launch + final read is the next cycle's first act (dispatch cap).
279. **(cycle 132 judgement, 2026-10-02 07:5x — after 132-5 FAIL 2/1, `stage_prerun_c132_5_rebase_p3b2.log:3-10,35-36`)**
     USER-RULES: U1 (relied on; rebase/simulator plumbing only — the plan's actions are unchanged; none contradicted).
     - **(a) Rebind rule accepted** (`stage_prerun.py:2890`, `selftest_rebind_c132_5` 7/0: Unbundler `-29 status` → `28082` by
       connectivity, wired to `Select` 10579; a referenced name address / position-only terminal refuses; chat_p1 46/0).
     - **(b) The re-sim stop at step 24 is the FS frame map, not the plan:** stagesim routes FS borders only via `fs_frames` +
       `owners[frame] = [FS, uid]` (`stagesim.py:402-410,1139-1145`); the real graph JSON has no `fs_frames` and frame owners
       `['FlatSequenceFrame', 0]`. Rule: `--rebase` CARRIES the provisional base's FS map through the binding (FS −1 → real FS
       uid; frames −2/−3/−4 → 27641/32464/27722; owners set to the real FS uid). The graph reader is not changed now.
     - **(c) A rebase whose re-sim fails must NOT write the plan** (it wrote 31bea1c5 over b25c1ecb). Fix + self-test. Recover the
       provisional plan by re-finalizing `plan_ring_p3b2_in.json` on the provisional base (same stagesim; md5 reported, expected
       b25c1ecb or the difference explained), then rebase it — never re-simulate the half-rebased 31bea1c5 in place.
     - **(d) Card 132-6 (last dispatch of cycle 132):** (b)+(c) → `--rebase` PASS (all 39 steps) → dry 39/39 + prerun → EL range →
       `--scratch-required` → full scratch run on a byte copy (PD278(d)). Launch = cycle 133.
280. **(cycle 132 judgement, 2026-10-02 08:0x — after 132-6 FAIL 1/1, `stage_prerun_c132_6_rebase_p3b2.log:36,51,76-77`)**
     USER-RULES: U1 (relied on; rebase/route-check plumbing only, the plan's 39 actions unchanged; none contradicted).
     - **(a) Accepted:** `stage_prerun.carry_fs` (FS −1 → 27509, frames → 27641/32464/27722, twin −43 → 28333) and the
       no-write-on-failure rebase (`selftest_rebase_c132_6` 8/0; rebind 7/0; chat_p1 46/0). Recovered provisional P3b-2
       `plan_ring_p3b2.json` 98992a59 has the SAME 39 actions as b25c1ecb's rebase (`diag_c132_6_actions.log`); the
       half-rebased 31bea1c5 is kept as `plan_ring_p3b2_rebased_c132_5.json`, never launched.
     - **(b) Remaining gap = the ROUTE CHECK, not the plan or the simulator:** re-sim on the real base runs 39/39, cdiff 16; the
       route check (collecting backend) after op 24 `p3b_x_i_f1` (`cfw`) cannot bind the FS OUTER tunnel created on the carried
       FS (sim −50 / −51 / −52 vs backend 10000052 / 53 / 54). Three rebase stops in this cycle were three DIFFERENT plumbing
       gaps (name keys → FS map → route-check binding), each closed and self-tested — not one failure repeated.
     - **(c) Cycle 133 first card (offline):** make the route check bind objects created inside a CARRIED FS the same way it does
       inside a plan-created FS (P3b-1's route check passed that way); self-test = the op-24 case; and MEASURE whether the
       `stagexec.compare` 'unbound' refusal on a provisional base (`stagexec.py:786,1864-1869`) predates card 132-1's 07:02
       stagexec edit (`git diff 83dd0e70 -- tools/stagexec.py`) — a regression from 132-1 is reverted, a pre-existing one is
       logged as fp. Then `--rebase` → dry 39/39 + prerun → EL range → `--scratch-required`. Card 2 = P3b-2 scratch run
       (PD278(d)); card 3 = ONE launch + final read; bed moves → 4 of 6.
     - **(d) If the route-check binding cannot be closed in ONE card**, fall back to finalizing `plan_ring_p3b2_in.json`
       DIRECTLY on `sim/ring_p3b2_base_real_fsmap.json` (the real graph + carried FS map), as P3b-1 was finalized on P3a's real
       graph — the rebase path is pipeline tooling, P3b-2 does not need it.
281. **(cycle 132 judgement, 2026-10-02 08:1x — after `archive/peer/2026-10-02-retrospective-cycle132.md`, `VIOLATION: wrong-ordering` 9 min)**
     USER-RULES: U1 (relied on; card ordering and a memory margin — no computation; none contradicted).
     - **(a) Ordering rule:** a LabVIEW card whose script needs `stage_prerun` dry/prerun records is never dispatched beside a
       card that edits `stage_prerun.py` / `stagexec.py` / `stagesim.py`; it follows it.
     - **(b) FIRST check of cycle 133:** X10 with the MEASURED start term for a stage starting from P3b-1 (584.1 MB after load,
       `diag_c132_2_graph_p3b1.log:24`; model start 570.0, `memory_model.json:6`) ⇒ P3b-2 ≈ 681.7 + 14.1 = 695.8 > 690. Recompute
       from the code, not by hand; > 690 ⇒ PD266(b): no third half without the user → `decisions_pending.json`, stop.
     - **(c) Widened PD280(c):** the recovered P3b-2 plan 98992a59 is `final: false` (its own finalize refused,
       `stagesim_c132_6_recover_p3b2.log:42-44`) although cycle 131 finalized b25c1ecb — measure whether 132-1's `stagexec.py`
       or 132-6's `stagesim.py` edit regressed finalize (git 83dd0e70). Route-check ALL 39 ops; fp-21 and the op-24 stop are one
       class (binding simulator-made uids). Rerun `diag_c131_5_stubs.py` and record its result whatever it is.
282. **(cycle 133 judgement, 2026-10-02 08:3x — at cycle start, before cards 133-1 / 133-2; steer `tools/bench/cards/steer_132.json` FOLLOWED)**
     USER-RULES: U1 (relied on: card order, tool plumbing and where a verification read runs; the plan's 39 actions and the
     final graph are unchanged; none contradicted).
     - **(a) Steer followed:** this cycle's work is the P3b-2 build (the ring that loop 1.2 reads from, M3); the next act written
       at cycle end is a build or run of the deliverable, never tooling. A third half of P3b, if it is ever needed, is a user
       question and goes to `decisions_pending.json` (PD281(b)); no other user question is waiting.
     - **(b) Cards:** 133-1 (offline, material) = PD280(c)(d) + PD281(c) through dry/prerun, plus the gate-fp drain (fp-21 is the
       route-check binding class, PD281(c); fp-28 needs a `gate_fp.py` close verb, PD276(d)) — ONE card answers the DUE gate-fp
       line. 133-2 (log-reader, read-only) beside it = the memory meter sequence of P3b-1's launch and scratch pin4, the X10
       start term's definition, 132-4's reader numbers, every recorded error-2 point.
     - **(c) Refines PD281(b):** before a third half is asked, judgement checks a launch FORM that keeps ONE stage file — the
       heavy end-of-run reads (last checkpoint read, CEN2 census) run in a FRESH LabVIEW instance on the saved file (rule-6 GUI
       save first; the file becomes the bed only if those gates pass, as PD274(c) already requires of the final Error List
       read). Decided on 133-2's facts (PD283), built in 133-3, with X10 modelling the launch instance from the MEASURED load
       of its input file (P3b-1: 584.1 MB, `diag_c132_2_graph_p3b1.log:24`).
     - **(d) `wrong-ordering` device decided** (`docs/violation-decisions.md` 2026-10-02 08:25): guard_session pairing check,
       built in an offline card beside this cycle's LabVIEW card, never as the first act.
283. **(cycle 133 judgement, 2026-10-02 08:5x — after 133-1 FAIL 2/1 (`stage_prerun_c133_1_p3b2_dry.log`, `diag_c133_1_pred_p3b2.log`) and 133-2 PASS 4/0)**
     USER-RULES: U1 (relied on: the 39 actions and the final graph are unchanged; only the number of LabVIEW sessions that
     apply them changes; none contradicted). The 6-file cap (CLAUDE.md "AT MOST 6", user 2026-09-29) is asked as D-2026-10-02-02.
     - **(a) Accepted from 133-1:** 98992a59's `final: false` is NOT a regression (b25c1ecb was finalized with
       `route_check=False`, `plan_ring_p3b_split.py:174`; the CLI uses True, `stagesim.py:2031`); 'unbound' on a provisional
       base dates from 2026-09-25 (`stagexec.py:786`) = fp-21's class, by construction; the op-24 stop was compile_plan
       placing FS wires from the plan only — fixed by `finalized.fs_routes` (`selftest_c133_1_fsroutes` 6/0, regressions
       green). Rebased P3b-2 `plan_ring_p3b2.json` 04204133 is final, route 39/39, BIND 22, R 24. Open: L0 refuses it because
       the rebase records its temp copy as `plan_in` (`plan_ring_p3b2.json:637-640`, `stage_d1_ring_p3b2.py:33`).
     - **(b) Memory (133-2):** X10's start 570.0 = pin2's k0 = P3a load + op-0 read (`memory_model.json:6`); P3b-1 loads at
       584.1 (`diag_c132_2_graph_p3b1.log:24`) and an op-0 read adds ~5.9 (`stage_d1_ring_p3b1.log:42-43`) ⇒ P3b-2 starts
       ≈ 590. X10 = 701.9 MB at start 570 (`diag_c133_1_pred_p3b2.log`) ⇒ ≈ 722 at 590; without the final read still ≈ 704.
       ONE LabVIEW session cannot apply P3b-2 under 690 MB, and P4/P5 start from bigger files. PD282(c)'s form is not enough.
     - **(c) DECIDED, under an assumption (CLAUDE.md 2c — safe, copies only, useful under every answer):** P3b-2 is applied in
       TWO LabVIEW sessions with a saved in-between file, from tools already exercised: split by memory (130-5), rebase onto a
       real graph (133-1), graph read (132-4). Part a = actions 1..k on the bed, part b = the rest on a's saved file; k from X10
       per session ≤ 690 with start 590 for a and, for b, a's predicted load + op-0 read (re-checked with the MEASURED load of
       a's file before b's prerun). Both parts together give 04204133's end graph (cdiff 16). **ASSUMPTION: the in-between file
       is part of step P3b-2, not counted toward the 6-file cap**; never a bed, never the input of another step, deleted after
       the step's final file is accepted (md5 kept). The final file is the same under every answer to D-2026-10-02-02.
     - **(d) One scratch covers both sessions on byte copies (D-2026-10-01-01): a on a bed copy → save → graph read → `--rebase`
       b → dry + prerun → b → save → Error List count-only in the range of `errorlist_expect_p3b2.py`; then ONE launch of both.**
       Bed moves to the step's final file → 4 of 6 (under the assumption).
     - **(e) Card 133-3 (offline):** X10 start from the measured load of the input file (cited per file); `--rebase` records the
       ORIGINAL `plan_in` (L0); the cut; a finalized on `sim/ring_p3b2_base_real_fsmap.json` with `fs_routes`, b provisional on
       a's sim end; recipes `stage_d1_ring_p3b2a.py` / `stage_d1_ring_p3b2b.py` from the P3b-2 recipe; a's dry + prerun PASS;
       gate-fp: fp-28 closed (correct refusal, PD276(d)), fp-21 closed (by design: a provisional base gets its dry only after
       `--rebase`, PD264(b)); `diag_c131_5_stubs.py` rerun recorded. 04204133 and `stage_d1_ring_p3b2.py` stay as the
       one-session reference, never launched.
284. **(cycle 133 judgement, 2026-10-02 09:0x — after 133-3 PASS 5/0 and 133-4 FAIL 3/1, `tools/bench/cards/result_133-{3,4}.json`)**
     USER-RULES: U1 (relied on: the cut keeps the 39 actions and 04204133's end graph — 10334 objects / 5933 terminals /
     1974 wires, cdiff 16; none contradicted).
     - **(a) 133-3 accepted:** X10 start = measured load of the input file + op-0 read 5.9 (`memory_model.json` load_by_vi,
       `stage_prerun.py:1945,1957`; P3b-1 re-modelled 678.5 vs 680.4 measured). Cut by units: a = actions 1-7, 14-19, 24-27,
       32-35 (N 21, X10 671.8 at 590.0), b = the rest (N 18, 677.7 at 605.1 = a's predicted load 599.2 + 5.9); a final on the
       FS-map base (route 21 rows, 0 unbound), dry 21/21, prerun 15/0; b final on a's simulated end (provisional); EL range of
       the step's final file 49..52 (loose ends 18..21, `errorlist_expect_p3b2ab.json`); `--rebase` keeps the ORIGINAL
       plan_in. Gate-fp queue drained (fp-21, fp-28 closed).
     - **(b) X10 must REFUSE an unmeasured input load, not fall back to 570** (133-3 open 1: b today 642.6 vs 677.7) — a
       silent pass on an unmeasured start is the `device-failed` class of 2026-10-02 02:57. Fixed in the next offline tooling
       slot, never inside a LabVIEW card; until then the scratch/launch card CHECKS that b's X10 line names the measured
       load of a's file (load_by_vi entry + its log line).
     - **(c)** `load_growth` 0.719 MB/op (one pair, P3a → P3b-1) is accepted as a PLANNING term only; b's real start is
       measured by the graph read of a's file before b's prerun.
     - **(d) 133-4 accepted:** the pairing check is live (`guard_session.py:75,238,426,432`; 10/10, payload test, 27/27,
       25/25). Glob semantics accepted: a card whose write glob CAN match a stage tool counts. `selftest_chat_p1` S3-S6 went
       red because its fixture prep card writes `tools/**` — narrowed to a realistic prep list (`tools/bench/**`,
       `tools/recipes/**`) as step 0 of card 133-5, which reruns it (46/46 expected).
     - **(e) Carries (tooling, after the deliverable):** (b); `selftest_rebase_c132_6` / `selftest_rebind_c132_5` fixtures
       (the provisional plan, now rebased in place) re-pointed to `git show 53737825:tools/bench/plan_ring_p3b2.json`;
       `diag_c131_5_stubs.py` FAIL 1/1 (our-script-bug, not on P3b-2's path); `guard_session` CARD_RE reads an absolute card
       path with a space as unreadable — dispatch with the relative path (as done).
     - **(f) Card 133-5 = the two-session scratch of PD283(d).** Launch = card 133-6 if the scratch passes and time allows,
       else the next cycle's first act.
285. **(cycle 133 judgement, 2026-10-02 09:3x — after 133-5 FAIL 12/2, `stage_d1_ring_p3b2a_scratch.log:346-350`)**
     USER-RULES: U1 (relied on: a recipe GATE is corrected, the 21 edits ran real == sim; no computation or design change).
     - **(a) Scratch a ran all 21 ops with E1 real == simulated and the name gate PASS (`:348-349`), then stopped at the
       recipe's FR gate (fatal, before save):** FR builds the set of base frames from terminal rows only
       (`stage_d1_ring_p3b2a.py:55-57`; same code `stage_d1_ring_p3b2b.py:57-59`), and frame f0 #27641 has 0 terminals BY
       DESIGN (PD269(b)), so it was taken for a new frame. 27641 is a base frame (`graph_ring_p3b1_20261002_073225.json`
       fs_frames 27509: [27641, 32464, 27722]). Our gate's bug, not a graph difference. Bed unchanged, scratch deleted.
     - **(b) Fix:** FR's base-frame set = the base graph's FS frame lists (fs_frames / the plan base's FS map) ∪ the frames of
       terminal rows; nothing else in the gate changes; both recipes; dry + prerun again (offline, seconds).
     - **(c) Memory fact:** in the STAGE context the P3b-1 file starts at 564.4 MB, 570.4 after the op-0 read
       (`stage_d1_ring_p3b2a_scratch.log:50-51`) = the model's old 570, not the reader-context 584.1 + 5.9 = 590 that
       `load_by_vi` now uses; a's peak 646.7 MB at k21 incl. the final read (`:346`) vs X10 671.8 (−25.1, conservative by the
       start). At the stage start the unsplit P3b-2 is still 701.9 > 690 (133-1), so the two-session split stands.
       **Carry:** `load_by_vi` from stage-context METER lines (start/k0), not reader loads — reader loads would force
       needless splits in P4/P5.
     - **(d)** The "within 10 MB of X10" check is one-sided: above X10 + 10 is the `device-failed` case; below is conservative.
     - **(e) Card 133-6 (the cycle's last dispatch, `retry_of_card` 133-5):** FR fix → a dry/prerun → the owed review if
       guard_peer holds → scratch a again (2nd run, within RETRY_CAP) → 133-5's steps 2-4. The launch is the next cycle's first
       act.
286. **(cycle 133 judgement, 2026-10-02 09:5x — after 133-6 FAIL 3/1, `stage_prerun_c133_6_rebase_p3b2b.log:3-4`; cycle closes on the 6-dispatch cap)**
     USER-RULES: U1 (relied on: binding plumbing only; b's 18 actions and the end graph are unchanged; none contradicted).
     - **(a) Accepted:** FR fix (`stage_d1_ring_p3b2a.py:30,56`, `_p3b2b.py:32,58`; `selftest_c133_6_fr` 9/0); review
       `archive/peer/2026-10-02-c133-6-fr-p3b2a.md` confirms our-script-bug and corrects one citation (the P3b-1 graph JSON has
       NO fs_frames; 27641 = f0 only through carry_fs binding by elimination). **Session a of P3b-2 PASSED as a scratch:**
       20/0 gates incl. FR, peak 650.9 MB (X10 671.8), bed unchanged (`stage_d1_ring_p3b2a_scratch_c133_6.log:348,386-392`).
       Its in-between file `claudeDev\scratch_c133_6_ring_p3b2a_20261002_093837.vi` (md5 6cc69221) is KEPT for session b's
       scratch — a scratch, never a bed, deleted when P3b-2 is accepted. Graph read of it: 588.5 MB after load (reader
       context), `graph_ring_p3b2a_20261002_094927.json`, `load_by_vi` entry `memory_model.json:16`.
     - **(b) Session b's rebase refused:** REBIND bound 11 nodes and 13 terminals (8 by connection, 5 by position) but left a's
       created terminals [-2, -4, -5, -6, -7, -9, -11, -30] unbound; -30 (the source terminal of a's FS outer tunnel -28, made by
       `p3b_x_i_f1`, border entry `27401|27641`) is in the FS map ⇒ FS-CARRY refuses. Fifth distinct rebase plumbing gap in two
       cycles (name keys, FS map, route binding, plan_in, created tunnel terminals) — each closed, none repeated.
     - **(c) Next cycle card 1 (kind build, offline steps first, then LabVIEW):** rebind binds a created terminal through its
       BOUND owner node by (direction, face/frame, position among that node's terminals) — PD278(c)'s second key, which -30
       never reached — refusing when ambiguous; self-test on the recorded pair (`sim/ring_p3b2b_base_provisional.json` ↔
       `graph_ring_p3b2a_20261002_094927.json`): -30 and the 7 others bind, an ambiguous case still refuses → `--rebase` b →
       b dry + prerun (X10 ≤ 690 at a's measured load) → scratch b on a COPY of the kept in-between → save → Error List
       count-only in 49..52 → measured census into both preds. If the rebind cannot be closed in that card, it returns and the
       FS reader of (e) becomes the next act.
     - **(d) Card 2:** ONE launch of both sessions from the bed: a → save in-between → graph read → `--rebase` b (compare with the
       scratch's rebased b: equal uids = LabVIEW's uid allocation measured deterministic) → b dry/prerun → b → save → full Error
       List read; bed moves → 4 of 6 (assumption, D-2026-10-02-02); both in-between files deleted after acceptance.
     - **(e) Carries (tooling, after the deliverable):** the graph reader records FS frames and border tunnels (one
       `OpFsDiagrams_v0` read of FS #27509, the review's cheapest test) so FS maps are measured, not bound by elimination;
       `load_by_vi` from stage-context METER lines (PD285(c)); X10 refuses an unmeasured load (PD284(b)); stale fixtures and
       CARD_RE (PD284(e)); `decisions_pending.json` item D-2026-09-28-01's question is 613 chars > the validator's 300, so
       `protocol.py validate` fails the whole file (never re-word an item — the validator needs a legacy exemption).
287. **(cycle 133 judgement, 2026-10-02 10:1x — after `archive/peer/2026-10-02-retrospective-cycle133.md`: `repeated-failure-class` 20 min, `wrong-ordering` 13 min; SUPERSEDES PD286(c))**
     USER-RULES: U1 (relied on: a dry rule, a graph READER and where b is finalized; b's 18 actions and the end graph are
     unchanged; none contradicted).
     - **(a) Dry rule device first** (`docs/violation-decisions.md` 2026-10-02 10:10): a gate FALSE on simulated data fails the
       dry; only stub-input gates may be UNVERIFIED and they block the launch unless named; an empty declared census prints
       UNPREDICTED. Without it session b's dry would run under the rule that hid FR.
     - **(b) The FS READER replaces a sixth binder patch (CLAUDE.md "guessed twice, build the reader"; retrospective finding
       1(b)/2):** four of the five rebase gaps and the FR bug were facts about Flat Sequence frames and border tunnels the graph
       reader does not record (frame owner error 1055, `diag_c132_2_graph_p3b1.log:82`; f0 = 27641 bound by elimination). The
       graph reader records, per Flat Sequence, its frames in order (one `OpFsDiagrams_v0` read) and each border tunnel's
       faces with their frames, into the graph JSON as `fs_frames` / border entries; stagesim takes them from the real graph.
     - **(c) Session b is finalized DIRECTLY on the real graph of a's file read that way** (PD280(d)'s path; b names nothing a
       creates, PD284(a)), not rebased from a's simulated end — no simulator uid of a's objects (−30) is left to bind. Check:
       b's simulated end == 04204133's end (10334 objects / 5933 terminals / 1974 wires, cdiff 16). PD286(c) (rebind via the
       owner node) is SUPERSEDED; it is the fallback only if the reader cannot read frames.
     - **(d) Slot rule (judgement, no device):** an offline card that may run beside a LabVIEW card goes in the PREP slot; a
       judgement that departs from its own written decision writes the reason here BEFORE the dispatch.
     - **(e) Cycle 134 cards:** 1 (kind build) = (a) + (b) + graph read of the kept `claudeDev\scratch_c133_6_ring_p3b2a_20261002_093837.vi`
       (md5 6cc69221; measured f0 reported) + (c) + b dry + prerun (X10 ≤ 690); 2 = scratch b on a COPY of that file → save →
       Error List count-only 49..52 → census into both preds; 3 = ONE launch: a from the bed → in-between → FS-reader graph read
       → b finalized on it → dry/prerun → b → full Error List read; bed → 4 of 6 (assumption, D-2026-10-02-02). Card 2 and the
       tooling carries of PD286(e) go in the prep slot where they can.
288. **(cycle 134 judgement, 2026-10-02 10:5x — after 134-1 FAIL 5/2, `tools/bench/cards/result_134-1.json`)**
     USER-RULES: U1 (relied on: gate scoping and dry bookkeeping only; b's 18 actions and the end graph unchanged; none contradicted).
     - **(a) Accepted:** dry rule device (FALSE on simulated data fails; `DRY PASS-UNVERIFIED <names>` refused at launch unless
       named; empty census → UNPREDICTED; `selftest_c134_1_dry` 11/0, 133-3's bytes rebuilt to md5 ababd4ed and FAIL on FR).
       FS reader: graph JSON `fs_measured {fs_frames, borders}`, stagesim uses it (fixture 6/0). **f0 of FS #27509 is MEASURED =
       27641** (left-to-right [27641, 32464, 27722], `graph_ring_p3b2a_fs_20261002_102553.json`), no longer bound by elimination.
     - **(b) Gate B is SCOPED, not widened:** 7 of 68 outer tunnels belong to the NESTED FS 14682 (both faces on FS frames) and
       the derivation cannot classify them. They are listed `UNMEASURED` in the graph JSON and never used for binding; gate B
       FAILS only when a plan action, route or carried map entry references one. Not a PASS-on-nothing: the gate verifies every
       border the plan uses, and names the rest. Measuring nested borders (an `Outer Tunnels[]` read) is a carry for the first
       plan that routes through a nested FS (check P4 when it is planned).
     - **(c) check_launch requires `dry_rule == 2`** on the dry record: a dry recorded under the old rule does not launch. Re-dry is
       offline, seconds.
     - **(d) a4 debts first in card 134-2:** rerun `selftest_c130_5` (first_fail ordering changed to executor-stop-first) and the
       stageplan self-test (rc=1 in 0 s, cause unread), plus c125_1_offline_measure; green or a named our-script-bug fix.
     - **(e) Then finalize b on the measured graph** with `diag_c134_1_finalize_b.py`: base_state loading all 22 FS frame lists
       may move other routes vs 04204133 — any difference from 04204133's end is LISTED and returned, not absorbed (rule 1a).
289. **(cycle 134 judgement, 2026-10-02 11:3x — after 134-2 FAIL 3/1, `tools/bench/cards/result_134-2.json`)**
     USER-RULES: U1 (relied on: base-graph owner bookkeeping only; b's 18 actions and the end graph unchanged; none contradicted).
     - **(a) Accepted:** stageplan self-test stub fixed (12/0), `selftest_dry_c130_5` 3/0, c125_1 5/0; gate B scoped
       (`stagesim.fs_border_gate`, B1-B7); check_launch drops dry records without `dry_rule` 2 (D1-D4). Correction to PD288(b):
       the 7 UNMEASURED tunnels sit on FS 14682, FS 2499 and frames 43928/44169 — none on FS 27509, none used by b.
     - **(b) Finalize on the measured graph stops at action 15/18** (`diag_c134_2_finalize_b.log:6`: no common diagram of #639
       and #32464): in `graph_ring_p3b2a_fs_20261002_102553.json` FS 27509's frames carry owner `['FlatSequenceFrame', 0]` and FS
       27509 has NO owner entry, so the frame → FS → diagram chain is broken; the provisional base had it from simulation.
       Sixth gap, and the same kind as the five before it: the base graph lacked an owner/frame fact. The reader exists now, so
       the fix goes into the reader → base_state conversion, not into another binder.
     - **(c) Rule:** every FS frame's owner is its FS, and every FS's owner is the diagram its node row was read on — both
       from MEASURED rows of that graph (the reader's per-diagram traversal), never from the simulator or a carried map. If the
       graph JSON does not hold FS 27509's diagram, the card RETURNS (a one-read reader fix is then the next card, LabVIEW).
       Self-test: the measured graph's owner chain for all 22 FS reaches a loop/case/VI diagram; frames' owner = their FS uid.
     - **(d)** `plan_ring_p3b2b.json` is restored to 1451ba90 from git (`git show HEAD:<path>` written by a script) before
       finalize; the failed d2bbd289 copy stays as `_c134_2_fail.json`.
     - **(e) Card 134-3** = (c) + (d) + finalize b + b dry/prerun; scratch b and the launch follow as 134-4 / 134-5 if the cycle
       has time, else NEXT.
     - **(f) (after 134-3 returned at step 1, `diag_c134_3_owners.log`)** The graph's `owners` dict holds no FS (filled from
       `Diagram` rows only, `diag_c134_1_graph.py:40-46`); FS 27509's row carries owner class `'Diagram'` without uid. Two
       MEASURED links exist and are accepted as the owner facts of (c): FS → frames = `fs_measured.fs_frames` (OpFsDiagrams read),
       and FS → diagram = the `frame_diagram` of its border tunnels' OUTER faces (terminal rows read by LabVIEW; a tunnel's outer
       face lies on the diagram that holds the structure). FS 27509: 8/8 outer faces on 27219 (case 22694 → 639 → While 637).
       Rule: frames' owner = their FS from fs_frames; FS's diagram from outer faces only when ALL agree; an FS with no border or
       disagreeing faces is `UNMEASURED` and gates like PD288(b). The broken frame owner `['FlatSequenceFrame', 0]` is replaced,
       never used. Reading the FS node's Owner in LabVIEW is not needed for b. Card 134-4 = 134-3's steps 2-5 under this rule.
290. **(cycle 134 judgement, 2026-10-02 12:1x — after 134-4 BLOCKED 4/0 on gate-fp fp-30, `tools/bench/cards/result_134-4.json`)**
     USER-RULES: U1 (relied on: b's 18 actions unchanged, cdiff equal to the unsplit plan's; none contradicted).
     - **(a) Accepted: session b FINALIZED on the measured graph** — `plan_ring_p3b2b.json` ae6b6111: 18/18, route check 18/0
       unbound, fs_routes 4, cdiff 16 == 04204133's; dry PASS rule 2 unverified 0; prerun 15/0; X10 peak 667.0 ≤ 690 from a's
       MEASURED load 588.5 + 5.9. stagesim owner chain (PD289(f)) `selftest_c134_4_owners` 7/0; FS 2499/14682/43914 UNMEASURED.
     - **(b) The object-count difference +29 (10363 vs 10334) is ACCEPTED as a representation difference, not a computation one:**
       they are Wire/Terminal object rows of a's REAL read for objects a created, which the simulator does not emit as object rows;
       node classes equal (`diag_c134_4_objdiff2.log` Q1), terminals 5933 / wires 1974 / owners 1763 equal, cdiff equal. Rule for
       real-vs-simulated base comparisons: compare node classes + terminals + wires + cdiff; total object rows are not compared.
     - **(c) fp-30** (`labview: none` refuses `selftest_c134_1_dry.py` for its `import stagekit`) stays queued; the self-test runs
       as step 0 of the LabVIEW card 134-5.
     - **(d) Cards:** 134-5 (LabVIEW) = scratch b on a COPY of the kept in-between 6cc69221 → save → Error List count-only 49..52
       → census into both preds. Beside it, PREP card 134-P1 (offline) = the launch runner for cycle 135: both sessions from the
       bed in ONE chained runner; after a, the in-between graph read is compared with `graph_ring_p3b2a_fs_20261002_102553.json`
       by node classes/terminals/wires/FS fields — equal ⇒ plan b ae6b6111 is used as is (LabVIEW uid allocation measured
       deterministic); different ⇒ b is finalized on the new read (134-4's script) + dry/prerun before b runs; then b, save, the
       FULL Error List read of the final file, expected file. The launch itself is cycle 135's first act.
291. **(cycle 134 judgement, 2026-10-02 12:5x — after 134-5 FAIL 4/1 and prep 134-P1 PASS 5/0)**
     USER-RULES: U1 (relied on: launch bookkeeping and gate scoping only; no action or end graph changes; none contradicted).
     - **(a) Scratch b ACCEPTED structurally** (`stage_d1_ring_p3b2b_scratch_c134_5.log:360-366`): 20/0, E1 18 ops real == sim,
       PB cdiff 16, peak 629.0 MB (X10 667.0, start 572.5), Error List 51 in 49..52 with every class in range
       (`diag_c134_5_el2.log`). b's census MEASURED into `plan_ring_p3b2b_pred.json` (1ad11cce). **P3b-2 is launch-ready.**
     - **(b) a's census = the class-count difference of the two REAL graph reads** (bed P3b-1 `graph_ring_p3b1_20261002_073225.json`
       vs `graph_ring_p3b2a_fs_20261002_102553.json`, same reader, object rows by class), written into
       `plan_ring_p3b2a_pred.json` by a script citing both files; the launch's CEN2 for a must equal it. Not a simulator number,
       not left UNPREDICTED.
     - **(c) Which 2 of P3b-1's 53 Error List items vanish is named BEFORE the launch** by the review's offline item-level test
       (`archive/peer/2026-10-02-c134-5-el-classrange.md`, `_hit` with OCR fallback on the unmatched entries of the scratch read
       `errorlist_scratch_c134_5_ring_p3b2b_20261002_112928_20261002_113807.json`); they must be loose ends on nets b rebuilds,
       as in P3b-1 (PD274). Anything else ⇒ no launch, judgement.
     - **(d) No failing log by design:** the graph read's gate B follows PD288(b) (UNMEASURED listed, PASS unless used); the launch
       runner's special case accepting rc=1 (`launch_p3b2_c135.py:42`) is removed. Recipe b's expected-file write of P3b-1's 53
       (`stage_d1_ring_p3b2b.py:83-92`) is not used for the final; the new bed's expected file = the launch's full final read.
     - **(e) Equal-branch provenance accepted:** plan b (base = the scratch in-between's graph) runs on the launched in-between
       when the runner's compare (uid+class rows, terminals, wire→terms, fs_frames, borders) is EQUAL — equality is exactly the
       condition under which the base file is irrelevant. Different ⇒ re-finalize, as written.
     - **(f) Cycle 135 card 1 (LabVIEW, `gui: true`):** offline step 0 = (b)(c)(d) if card 134-6 did not close them; then the ONE
       launch `py tools/bgrun.py --material --max-min 200 --log tools/bench/launch_p3b2_c135.log -- py -u
       tools/bench/launch_p3b2_c135.py --launch`; bed → 4 of 6 (assumption, D-2026-10-02-02); both in-between files deleted
       after acceptance (6cc69221 and the launch's).
292. **(cycle 134 judgement, 2026-10-02 12:3x — after 134-6 PASS 4/0, `tools/bench/cards/result_134-6.json`)**
     USER-RULES: U1 (relied on: acceptance bookkeeping only; none contradicted).
     - **(a) PD291(b)(c)(d) closed:** a's census = new uids of the two real graph reads (Terminal 18, Wire 10 created / 2
       removed, Local 5, FSOuterTunnel 2, GrowableFunction 2, InnerTerm 2, OuterTerm 1, SelectorTunnel 1, DigitalNumericConstant 1;
       `diag_c134_6_census.log`) in `plan_ring_p3b2a_pred.json` 45eb0b67; graph-read gate B scoped, runner rc=1 case removed
       (`selftest_c134_p1` 18/0, runner dry 17/0); runner `launch_p3b2_c135.py` 16e941a6.
     - **(b) The vanished Error List items are accepted at CLASS level** (PD274's precedent for P3b-1): the only unmatched entry of
       P3b-1's 53 is the aggregated `Wire: Wire has loose ends` 22 → 20; every other entry matched (`diag_c134_6_el_items.log`).
       Neither Error List read carries uids (no `Selection List[]` op), so nets are not named; not built for this step.
     - **(c) a's CEN2 in the launch:** the pred comes from the graph reader, CEN2 counts with stagekit's own maps. Cycle 135 step 0
       (offline, code read): if CEN2 is fatal BEFORE the save and the two instruments key/count differently (created uids by
       class), the launch card names CEN2 of session a as an expected unverified gate and the launch records the measured set
       (PD261(c): the census prediction is not a P3b launch precondition); if they agree, CEN2 gates as written.
