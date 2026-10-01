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
