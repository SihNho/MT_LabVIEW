---
type: plan
kind: index
status: current
date: 2026-10-02
parent: docs/d1-loop12-17-split-plan.md
supersedes: [docs/d1-loop12-17-split-plan.md, docs/cycle27-plan.md]
tags: [d1, ring-buffer, loop-split, index, pre-decided]
---

# D1 ring buffer / loop split — INDEX of what is in force (card chat-D1, 2026-10-02)

The current plan. One line per decision still in force, each with a link to the full text in a FROZEN file (frozen
2026-10-02: old lines and line numbers unchanged, footer appended). Read the linked line only when the one-liner is
not enough. Long history stays where it was; nothing here replaces the full text, it only says which of it applies.

**How to add a decision (5 lines):**
1. Pick the topic file below (`docs/d1/ring-p3b.md`, `ring-p4.md`, `tooling.md`); a new step gets a new file `docs/d1/<step>.md` with the same frontmatter, then a row in "Topic files".
2. Number = 1 + the highest `NNN.` item in `docs/d1/*.md`, never below 268 (`grep -hoE "^[0-9]{3}\. " docs/d1/*.md | sort -n | tail -1`).
3. Write it under that file's `## Pre-decided`, as `NNN. **(cycle N judgement, date — after <cards>)**` + a `USER-RULES:` line (doc_lint L9).
4. Add ONE line for it to "Pre-decided — in force" below (`- PDNNN(x) <one line> — docs/d1/<file>.md:<line>`); mark a superseded line `(SUPERSEDED by PDmmm)`, never delete it.
5. Never append to a frozen file (`docs/d1-loop12-17-split-plan.md`, `docs/cycle27-plan.md`, `docs/d1-build-plan.md`, `docs/d1-route-b-plan.md`); `docs/violation-decisions.md` is the one append-only exception (its footer says why).

## Current state

- **Work VI (bed):** `claudeDev\D1_ring_p3b2b_20261002_130007.vi`, md5 `395118775a52bc90073f4449b99f899d` (STATUS `current-bed:`; PD297 — [ring-p3b](ring-p3b.md)). Error List 51 items, expected file `tools/bench/errorlist_expected_D1_ring_p3b2b_20261002_130007.json`. STRUCTURAL, `ExecState` 0 by design, never run. (Before: P3b-1 `D1_ring_p3b1_20261002_060910.vi` `9d7bf287…`, 53 items.)
- **Broken-intermediate count (CLAUDE.md "AT MOST 6"):** 4 of 6 (P2b 1, P3a 2, P3b-1 3, P3b-2 4). P4 measured at 93 actions (PD293) — how many files it may use is the open user decision D-2026-10-02-03; P6 must run (PD261(d) — [split-plan:2847](../d1-loop12-17-split-plan.md)).
- **Plan of record for the frame handoff:** `docs/ring-buffer-design.md` (user design 2026-09-28; PD238(a)). User rules checked by every design item: `docs/user-rules.md`.
- **P4 in progress (cycle 141, PD326):** session 1 of 11 saved as the in-between file `claudeDev\D1_ring_p4s01_20261002_232547.vi` (dc61e193, EL 51, not counted); plan v17 `plan_ring_p4_v17.json` e19d7e14; session 2 plan `plan_ring_p4_s02.json` 5e483ea6 (provisional, rebase on `graph_ring_p4s01_20261002_234419.json`).
- **Next act (cycle 142):** PD326(e) — P4 session 2: rebase → cut check at 596.5 → dry/prerun → ONE scratch → gated launch → load + graph read; beside it session 3 prep.
- (history) **Next act (cycle 141):** PD322 — offline card ALONE: created-node prim gate + P4 v16 (the 5 Insert-Into-Array bed slot writes swapped to `DonorRAS1D_v0.vi` uid 175 first, then v15) + session-1 re-cut and dry/prerun/X10; then the LabVIEW session-1 scratch → gated launch (PD320(e)). (Cycle 140: X10 session table, cut rule PD320; RLE 1055 → v15 PD321; ALL ring slot writes are Insert Into Array — rule-1a defect, repair decided PD322; 1-D RAS donor built and run.)

## Ring-buffer step table (PD238(g) — [split-plan:2260](../d1-loop12-17-split-plan.md))

| step | content | state | where |
|---|---|---|---|
| P1 | buffer-mode measurement, no VI | DONE — `Last` + `Wait (ms)` 1 adopted | PD238(i) :2262 |
| P2a | remove the pool's queue nodes, keep the 20 images | DELIVERED `D1_ring_p2a_20260928_191739.vi` (`c22a473f…`) | PD238(l) :2266 |
| P2b | `Num`/`TransPos`/`RotPos`/`FrameIdx`/`Latest` + their init on FS1 `#4866` | DELIVERED `D1_ring_p2b_20261001_140658.vi` (`652b1447…`) | PD246(a) :2397 |
| P3a | loop-1.1 control: wait, two registers, `Equal?`, case, counter, mod 20 | DELIVERED `D1_ring_p3a_20261001_180540.vi` (`4dfa44aa…`) | PD251(a) :2552 |
| P3b-1 | slot writes part 1 (IMAQ Copy + error guard; 31 actions) | DELIVERED `D1_ring_p3b1_20261002_060910.vi` (`9d7bf287…`) = bed; 680.4 MB, EL 53 | PD271–274 (tooling.md:56, ring-p3b.md:35–64) |
| P3b-2 | slot writes part 2 (TransPos/RotPos/FrameIdx groups, Latest); 39 actions applied in TWO LabVIEW sessions (a 21 / b 18) by memory | DELIVERED `D1_ring_p3b2b_20261002_130007.vi` (`39511877…`) = bed; a 645.7 / b 620.6 MB, EL 51 | PD283–297 (ring-p3b.md:155–) |
| P4 | tracking-loop 1.2 reader (seqlock, `last`, jump, rollback Selects, `BufDiff` 5th per-slot array, 1.2 stop) | IN PROGRESS — plan v17 (`plan_ring_p4_v17.json` e19d7e14, 235 actions incl. the 50-action Insert-Into-Array → Replace Array Subset repair, 11 sessions by X10); session 1 SAVED `D1_ring_p4s01_20261002_232547.vi` (dc61e193, in-between, not counted); one counted file at the end (CLAUDE.md, D-02/D-04 answered) | PD293–PD322 (ring-p4.md, frozen), PD323–326 (ring-p4b.md) |
| P5 | results queue 1.2 → 1.7 (lossless FIFO) | NOT STARTED | PD238(d) :2257 |
| P6 | recorded-frame replay (X/Y/Z bit-identical) + real ABBA at 90/150 Hz | NOT STARTED — first RUN of the chain | PD238(f) :2259 |
| after P6 | ONE interface-contract step (every loop's published/read locals) | NOT STARTED | STATUS `## NEXT` parallelism rule |

## Open user decisions (`tools/bench/decisions_pending.json`)

- **None open** (file read by the cycle-141 judgement session: all 20 items `answered`). The three lines below are history.
- D-2026-10-02-03 (answered; P4 = one counted file, built over several sessions, CLAUDE.md "Big or blocked work" item 2): P4 is 93 edits — raise the 6-file cap to 8, allow one 93-edit step in ~5 LabVIEW sessions, or run the chain first?
- **D-2026-10-02-02 (open):** do in-between files count toward the 6-file cap (we proceed as "no").
- **D-2026-10-02-01 (open):** a check that stops a helper agent finishing while its own LabVIEW run is live (129-2's run was killed that way).
- D-2026-10-01-01 ANSWERED 2026-10-01 (option 1): ≤ ~40 edit operations per ring step, full scratch run before each, 6-file cap kept (PD261 — [split-plan:2827](../d1-loop12-17-split-plan.md)).
- D-2026-09-28-01 ANSWERED by user rule U13 (jump to the newest slot; PD238(a)).

## Pre-decided — in force

Links are `docs/d1-loop12-17-split-plan.md:<line>` (frozen; "split-plan" below). "(done)" = an accepted fact or a
delivered step that later items build on; it is in force as a fact, not as an order.

### PD238 — the ring buffer is the plan of record (cycle 121) — [split-plan:2252](../d1-loop12-17-split-plan.md)
- PD238(a) Plan of record `docs/ring-buffer-design.md`; the pool QUEUES (PD233(f)(g) carriers, 234, 235(e), 236(c)(e), 237(a)(b)(d)(e)(f)(h)(i)(k)(l)(n)) are SUPERSEDED; KEPT: the 20 pool images + names constant, 237(j)/(m) facts, 233(f)(1)(2), 236(b) — :2254
- PD238(b) Slot write = COPY (`#6810` keeps its own Image In); duplicate BufNum skipped before any slot is touched — :2255 (image source corrected by PD242(c))
- PD238(c) Camera loop 1.1 per NEW BufNum: `Num(i)=-1` → copy → per-slot values → `Num(i)=BufNum` → `Latest=BufNum`; order by data dependency — :2256
- PD238(d) Transport = front-panel objects, one writer, read by LOCAL variables; image refnums by tunnel; no queue 1.1→1.2; results 1.2→1.7 stay a FIFO — :2257
- PD238(e) Tracking loop 1.2: `last` register, smallest `Num > last`, seqlock n1==n2>=0 else discard+count, overwrite ⇒ jump to `Latest`, 1 ms own wait — :2258
- PD238(f) Rule-1a acceptance = recorded-frame replay bit-identical + real ABBA (P6); structural gates are never acceptance — :2259
- PD238(g) Build order P1→P2a→P2b→P3→P4→P5→P6, each a saved claudeDev file (row cap now PD261(d)/D-2026-10-01-01) — :2260
- PD238(i) P1 measured: `#6810` stays `Last`; loop 1.1 gets `Wait (ms)` 1 + duplicate skip; `LastNew` only as P6 fallback — :2262
- PD238(j)(l) (done) P2a: queue LoopTunnel `#25898` removal accepted; P2a delivered — :2263, :2266
- PD238(k) Launch-gate rule: skip only segments whose START runs `tools/stage_prerun.py`; time filter rejected — :2264–2265
- PD239 NO SCRATCH BUILD ON A PROVEN PATTERN (`--scratch-required` exit 0), except new structure class or after a failed launch — :2267 (D-2026-10-01-01 now requires a full scratch run before every ring step)

### PD240–245 — P2b (cycle 122)
- PD240(a) Five INDICATORS `Num`/`TransPos`/`RotPos`/`FrameIdx`/`Latest`, types from `facts_c120_types.json`; a used label is a plan FAIL — :2281
- PD240(b) Initial values written by the diagram every run (−1 / 0.0) — :2287; initialiser may be an ARRAY CONSTANT (PD241(b) :2319)
- PD240(c) Placement on an earlier FS1 frame, outside loops = `#4866` (PD244(c) :2366) — :2292
- PD241(d) P3 binding: IMAQ Copy Src = `#6810` Image Out t6865; ordering by NEW sinks only; pool refnums leave For `#23093` by a new indexing tunnel — :2327
- PD242(a)(b) (done) `OpConstInd_v0` accepted; creator hygiene = ≥ 2,000 calls, 0 errors, handles ±100 at equal VI state — :2334, :2339
- PD242(c) Image into `#6810` = panel `IMAQimage` from `IMAQ Create #20436` (not `'Cam'`) — :2343 (its OPEN closed by PD246(b))
- PD243(a) (done) `OpConstInd_v0` hygiene record + `DonorRingConst_v0` accepted — :2350
- PD244(b) An FS-frame owner check uses `owner_of(strict=False)` — :2364
- PD244(e) A saved donor is declared through stagekit, not a gate exemption (carry) — :2371
- PD245(b′) An ArrayConstant adds its element DigitalNumericConstant (census rule) — :2387

### PD246–249 — P3 design and tools (cycle 123)
- PD246(a) (done) P2b delivered — :2397
- PD246(b) No pixel conversion: all three IMAQ Create image types are value 0 / representation 6 — :2403
- PD246(c) P3 design A1–A5: 3-frame Flat Sequence in the new-frame case; local read → Replace Array Subset → local write; both registers on While `#637` initialised from constants on `686`; `Equal?`; counter incremented in False frame, `i = count mod 20` from LEFT value — :2408–2426
- PD246(d) P3 = P3a + P3b (P3b size later set by PD261(d)) — :2427
- PD247(a)(b) (done) SR-init route `const_sr`; measured `$work` donors; For exit by route `nested` is indexing — :2445, :2452
- PD247(c) `case_in` NOT usable (selector found by label raised a modal dialog) — :2457
- PD247(d) New-frame counter I32 initial 0; previous-BufNum follows BufNum's type (I32, PD249(b)) — :2460
- PD247(e) / PD249(a) Census device in force: prerun X15 FAIL on derived ≠ declared; `CENSUS-UNPREDICTED` ⇒ `--scratch-required` exit 3 — :2463, :2492
- PD248(b) A branch onto an existing net is gated by `Is Broken?` False + that wire's sink count +1, never a wire COUNT — :2475
- PD249(b) (done) Real P2b terminals: `Num` t35255, `TransPos` t35215, `RotPos` t35319, `FrameIdx` t27025, `Latest` t35418 — :2500
- PD249(c)(f) A5 is NOT redesigned; case-tunnel inner-face tool built instead — :2504, :2520

### PD250–257 — P3a delivered, P3b prepared (cycles 124–126)
- PD250(a)(b) (done) `OpConnectTermUid_v0`, `connect_term_uid`, `case_inner_face`, `case_frame_wire`; stageplan `frame` field — :2532, :2541
- PD250(c) A crossing from a register inner face compiles to `connect_term_uid`; 2nd sink on a used inner face = `case_frame_wire` variant `branch`, census {} — :2544
- PD251(a) (done) P3a delivered = the bed — :2552
- PD251(b) / PD252(a) Prerun X16 refuses a primitive create without `term_class` (skips `const_donor`) — :2558, :2572
- PD252(a) Rule for cards: a card that edits `stagexec.py`, `stagekit.py` or a listed self-test reruns `tools/bench/c125_1_offline_measure.py` — :2578
- PD252(d)/PD253(d)/PD255(a) The 55th Error List item = stub `w27378` from our `connect_term_uid`; removed by `wire_remove_loose_ends` (55 → 54) — :2593, :2632, :2671
- PD252(e)/PD253(a) (done) Flat Sequence creator = new ops `OpFsAddFrame_v0` + `OpFsDiagrams_v0`, addressed by Traverse index + UID echo — :2604, :2611
- PD253(b)/PD254(a) Every op hygiene check goes through `gscript.hygiene_run` (recycle copies; quote PD242(b)'s equal-state clause) — :2618, :2645
- PD254(b) (done) stagexec routes `fs_create`/`fs_frame`/`fs_frame_to_frame`; FS faces addressed by owner uid + frame — :2651
- PD254(c) Stub removal uses Wire method `6370C08` RemoveLooseEnds (not CleanUpWire) — :2656
- PD254(d) P3b frame 3 takes `Num` by a SECOND local read — :2662
- PD255(b)/PD256(b) A `wire_remove_loose_ends` row after EVERY new crossing wire, plus one for `w27378` — :2679, :2705
- PD255(e)/PD257(a) Per-slot `TransPos` ← `#30117` Value, `RotPos` ← `#4580` Value (confirmed in the ORIGINAL; the open w4878 is by design since PD182) — :2687, :2725
- PD256(a) (done) Every crossing kind P3b needs is MEASURED; `connect_term_uid` takes multi-border crossings — :2699
- PD256(c) A crossing from an already-wired source RE-CREATES the net's wire: rows address terminals, never an old wire uid; `computation_diff` must keep every old sink — :2707
- PD256(d) Graph rows are deduped at load (`V.dedupe_rows`), gate `nonidentical == []` — :2710
- PD257(d)/PD258(a) 2nd+ sink into an FS frame already entered = `connect_term_uid(sink, inner-face terminal)` (branches, no second tunnel) — :2740, :2751

### PD258–263 — P3b plan, guard, split (cycles 127–128)
- PD258(a) RULE: ONE Error List GUI read at the END of a diagnostic, never one per step (~7 min each) — :2758
- PD258(b) Automatic Error Handling is not readable over COM; not needed — :2760
- PD258(c) `IMAQ Copy` error in ← `#6810` error out (branch); error out → status → `Select` (−1 : BufNum) → `Num(i)` element; `Latest=BufNum` unconditional; original error chain unchanged — :2762
- PD259(a) IMAQ Copy terminals measured; repeated unnamed sinks paired in read order — :2783
- PD260(a) (done) `_fs_entries_remap`; `SIM-INTERNAL:` FAIL instead of an escaping SimError — :2802
- PD260(b) Multi-object binder is FRAME-KEYED per border, never uid order — :2807
- PD261(a) Guard form C1: `Unbundler` from `DonorErrSel_ErrToWarning.vi` (#157) + `Select` from `DonorErrSel_MergeErrors.vi` (#529) — :2828
- PD261(b)/PD262(a) X5 compares wiring rows and RLE rows 1:1 (fp-19) — :2837, :2858
- PD261(c) The census prediction is NOT a launch precondition for P3b; the scratch's measured census is the prediction — :2843
- PD261(d) P3b SPLIT: each ≤ 40 actions, dependency-closed, IMAQ Copy + guard in the same step, each RLE with its loose end; no slack for a further split without the user — :2847
- PD262(b)/PD263(a) A repeated terminal name of ONE node is addressed `name#k` in `Terminals[]` read order (`element#0` = status) — :2862, :2879
- PD262(c) `selftest_stage_prerun_c106e` E1 red since X16 (a `Local` create); queued as a gate-fp candidate (fp-20) — :2870
- PD263(a) `plan_ring_p3b.json` (4003eaa5), its `_pred` and `stage_d1_ring_p3b.py` are STALE — never launch them — :2883

### PD264–267 — P3b-1/P3b-2, memory (cycle 129)
- PD264(a) P3b-1 40 / P3b-2 30 actions replay to the same end graph as the unsplit 70 (cut being re-balanced, PD266(b)) — :2891
- PD264(b) P3b-2's dry/prerun run after `--rebase` onto the real graph of P3b-1's saved file — :2898
- PD264(c) The scratch run's measured census is written into `plan_ring_p3b1_pred.json` by a script citing the log line — :2903
- PD264(e) Two LabVIEW cards: scratch (no launch), then ONE launch + final Error List + expected file — :2908
- PD265(a) A crossing's new tunnel takes the name of named tunnels already on the SOURCE net, else `''` (one net measured; the next scratch tests it) — :2916
- PD265(b) Memory: whole-VI checkpoint read +2.53 MB, edit +0.58 MB, close frees nothing; only a restart frees — :2925
- PD265(c) P3b-1/P3b-2 use PD193(a)'s checkpoint set `{0, len(ops)} | BIND` (690 threshold there SUPERSEDED by PD266(b)) — :2931
- PD266(a) (done) Predicted peaks P3b-1 688.5 MB, P3b-2 641.8 MB — :2942
- PD266(b) P3b-1 NOT run at 688.5; re-balance the split by predicted memory (570 + R×2.53 + N×1.4); pass = larger peak ≤ 675 MB; no valid cut ⇒ return (third half = user) — :2946
- PD266(c) Broken-file count P3b-1 = 3, P3b-2 = 4 of 6 — :2953
- PD267(b) Cycle 130 FIRST card = X10 fix (cross-recipe peak, FAIL > 675 and FAIL UNMEASURED) then the re-cut X10 must PASS (replaces PD266(d)'s separate script) — :2966
- PD267(c) Cards 2/3 (P3b-1 scratch, ONE launch) per PD266(d); briefs quote `.claude/agents/material.md:92-98`; card 4 adds the stop-record predicate fix (fp-22) — :2971

### PD268+ — topic files (cycle 130 on)
- PD268(a) X10 memory model live (FAIL > 675 / UNMEASURED), self-test 9/0 — docs/d1/tooling.md:22
- PD268(b) `--dry` FAILS when the executor stopped before the last op (130-5) — docs/d1/tooling.md:27
- PD268(c) c128b red = stale unsplit fixture; re-finalize the unsplit 70 as a reference, re-pin c128b — docs/d1/tooling.md:30
- PD269(a) P3b re-cut accepted: P3b-1 N31 663.4 MB, P3b-2 N39 664.3 MB; f0's `Num(i)=-1` group moves to P3b-2 — docs/d1/ring-p3b.md:20
- PD269(b)(c) Empty f0 after P3b-1 accepted; FS/FU gates compare per-frame counts with the simulated end state — docs/d1/ring-p3b.md:26
- PD270(a)(b) PD265(a)'s tunnel-name rule refuted at pin3 op 26 (`Image Out`); MEASURE the rule from every recorded crossing before a third scratch run — docs/d1/tooling.md:39
- PD271(a)-(d) Tunnel-naming rule measured + accepted (SubVI source terminal name; 18-crossing table); P3b-1/P3b-2 re-finalized (edbdba99 / b25c1ecb); guard_peer offline rule v2 accepted; fp-19/20/21 after P3b-1 launch — docs/d1/tooling.md:56
- PD272(a)-(d) Scratch pin4 accepted structurally (22/0, names right); peak 680.8 MB (final read +17.4) ⇒ launch memory stop 690, X10 planning stays 675; X10 final-read term = tooling carry — docs/d1/ring-p3b.md:35
- PD273(a)-(d) Scratch Error List 53 (pred 54, one extra loose end): hypothesis = RLE cleared an original stub on the same net; launch proceeds, missing item named offline, bed moves only after judgement — docs/d1/ring-p3b.md:50
- PD274(a)-(d) P3b-1 LAUNCHED `D1_ring_p3b1_20261002_060910.vi` (9d7bf287, 22/0, 680.4 MB); Error List debit by CLASS; bed moves when final read = 53 with loose ends 24→22 only — docs/d1/ring-p3b.md:64
- PD275(a)-(e) X10 final-read term (+17.4) and FAIL threshold 690 once the term is in; per-op tunnel-name gate from sim; P3b-2 expected EL computed; fp-19/20/21 fixed, fp-28 closed — docs/d1/tooling.md:74
- PD276(a)-(d) 132-1 accepted (X10 680.8/681.7, name gate fs_border only); fp-21 not on P3b-2's path (dry after rebase); P3b-2 expected EL = range 50..52 checked by scratch; fp-28 needs a close verb — docs/d1/tooling.md:92
- PD277(a)(b) X10 models a 0-edit reader without Executor plan as N=0 + reads + final read (fp-29); card 132-4 chain read → rebase → dry/prerun — docs/d1/tooling.md:109
- PD278(a)-(d) real P3b-1 graph read (6cfa6ecb, no swapped loose ends); rebase refusal = sim label gap; rebind by connectivity, names logged, plan-referenced terminals unique (Unbundler status ↔ Select); card 132-5 → scratch — docs/d1/ring-p3b.md:78
- PD279(a)-(d) rebind accepted (7/0); `--rebase` carries the provisional FS frame map; a failed re-sim never writes the plan; recover provisional P3b-2, rebase, dry/prerun, scratch (card 132-6) — docs/d1/ring-p3b.md:95
- PD280(a)-(d) carry_fs + no-write rebase accepted (8/0); recovered P3b-2 98992a59 = same 39 actions; remaining gap = route-check binding in a carried FS (op 24); cycle 133 card 1 closes it (or finalizes P3b-2 directly on the real+FS-map base), then scratch, launch — docs/d1/ring-p3b.md:109
- PD281(a)-(c) no LabVIEW card beside a card editing its pre-check tools; cycle 133 FIRST recomputes X10 with the measured P3b-1 start 584.1 MB (≈695.8 > 690 ⇒ user); recovered P3b-2 is final=false — check for a finalize regression, route-check all 39 ops — docs/d1/ring-p3b.md:130
- PD282(a)-(d) steer_132 followed (P3b-2 build); 133-1 offline readiness + gate-fp drain ‖ 133-2 memory facts; before a third half, try ONE-file launch form with end reads in a fresh instance (PD283); wrong-ordering device = guard_session pairing check — docs/d1/ring-p3b.md:138
- PD283(a)-(e) fs_routes fix accepted (04204133 final, route 39/39, BIND 22/R 24); X10 ≈ 722 MB at the measured start 590 ⇒ P3b-2 in TWO LabVIEW sessions with an in-between file (assumption: not counted toward the 6-file cap, D-2026-10-02-02); one scratch of both sessions, then ONE launch — docs/d1/ring-p3b.md:155
- PD284(a)-(f) cut a 21 / b 18 (X10 671.8 / 677.7), a final + dry 21/21 + prerun 15/0, b provisional, EL 49..52; X10 must refuse an unmeasured input load (carry; card checks it meanwhile); pairing check live, chat_p1 fixture narrowed; card 133-5 = two-session scratch — docs/d1/ring-p3b.md:184
- PD285(a)-(e) scratch a: 21 ops real == sim, stopped by our FR gate (base frames from terminal rows; empty f0 #27641 by design) → fix FR in a and b; stage-context start 570.4 (not reader 590), a peak 646.7 vs X10 671.8; split stands (unsplit 701.9); card 133-6 = scratch rerun — docs/d1/ring-p3b.md:209
- PD286(a)-(e) session a of P3b-2 PASSED as scratch (20/0, 650.9 MB), in-between scratch file kept (6cc69221); b's rebase refused on a's created tunnel terminal -30; (c) rebind via owner node (SUPERSEDED by PD287) — docs/d1/ring-p3b.md:228
- PD287(a)-(e) dry rule device first (FALSE on simulated data fails the dry); Flat Sequence frame/border READER instead of a sixth binder patch; b finalized DIRECTLY on a's real graph; prep-slot rule; cycle 134 cards 1-3 — docs/d1/ring-p3b.md:256
- PD288(a)-(e) dry rule device + FS reader accepted (f0 == 27641 MEASURED); gate B scoped to borders the plan uses (nested FS 14682's 7 tunnels UNMEASURED, carry); check_launch needs dry_rule 2; a4 self-test debts then finalize b on the measured graph, diffs listed — docs/d1/ring-p3b.md:278
- PD289(a)-(e) 134-2's tool fixes accepted; finalize-on-measured stops at b action 15 (FS 27509 has no measured owner, frames owner 0); owners of FS frames/FS from MEASURED rows only, else return; plan b restored to 1451ba90 — docs/d1/ring-p3b.md:300
- PD290(a)-(d) session b FINALIZED on the measured graph (ae6b6111, 18/18, cdiff 16, dry rule 2 + prerun 15/0, X10 667.0); object-row +29 = representation (compare node classes/terminals/wires/cdiff); fp-30 queued; 134-5 scratch b ‖ prep 134-P1 launch runner — docs/d1/ring-p3b.md:317
- PD291(a)-(f) scratch b ACCEPTED (20/0, 629.0 MB, EL 51); a's census from the two real graph reads; name the 2 vanished EL items offline before launch; no failing-by-design graph log; equal-branch provenance accepted; cycle 135 = ONE launch via launch_p3b2_c135.py — docs/d1/ring-p3b.md:337
- PD292(a)-(c) launch preconditions closed (a's census from graph-read uids; gate B scoped; runner 16e941a6); vanished EL items accepted at class level (loose ends 22→20, PD274 precedent); a's CEN2 instrument check offline before launch — docs/d1/ring-p3b.md:361
- PD294(a)-(e) launch session a ACCEPTED as in-between (49cf7f77, 20/0); compare DIFFERENT = reader annotation only → re-annotate both sides; plan b restored to ae6b6111; finalize-writes-only-on-success + completeness gate built now; resume runner (no finalize branch) then ONE resume launch of session b — docs/d1/ring-p3b.md:374
- PD297(a)-(c) P3b-2 DELIVERED = bed `D1_ring_p3b2b_20261002_130007.vi` 39511877, EL 51 (loose ends 22→20), expected file from the final read; broken count 4 of 6; next = P4 — docs/d1/ring-p3b.md:409
- PD296(a)-(d) plan b applies to the a-file (same actions; step diffs = base-file identity only); resume memory gate kept (≤ 677); fp-30 stays queued (its self-test fails 10/1 on content); card 135-4 = ONE resume launch — docs/d1/ring-p3b.md:396
- PD295(a)-(e) `#5119` value is SAVED ⇒ 5th per-slot array `BufDiff` in P4; `#11608`/`#1359` display only (display track); 1.2's x==x scaffold stop replaced by the program stop; n2 ordered by a one-frame FS on a `#5058` output (amends PD293(e)); scratch verification of 5 unmeasured routes before P4 plans — docs/d1/ring-p4.md:46
- PD293(a)-(f) P4 sized (93 actions, X10 824 MB; ≤40-action steps, file count = D-2026-10-02-03); torn/stale frame rolls back every 1.2 register (Select) and is not handed to 1.7; valid = n1==n2 AND n1>last; W1 wait-for-new with stop exit; n2 ordered by data dependency; facts owed (#5119/#11608 use in the original, 1.2 stop, 6 unmeasured routes) — docs/d1/ring-p4.md:21
- PD298(a)-(g) P4 v2 = 159 actions (rollback 43), load 600.2 measured; pool crossing via explicit #10170 tunnel; n2 FS input + one no-effect consumer; values leaving 1.2 take the rolled-back value, display stays raw; W1/1.2 stop by local of `stop (end)` or a `StopAll` writer if latch; re-measure the 700 MB stop (error 2 ~770 = leaked refs); D-2026-10-02-04 — docs/d1/ring-p4.md:63
- PD299(a)-(d) X10 edit-diagnostic branch accepted (fp-33); bed load 600.2 into memory_model; reads counted from source call sites; c132_1 T3 stale fixture; Stop If True? read on the machine — docs/d1/ring-p4.md:93
- PD300(a)-(c) P4 v3 163 actions, replay to step 101 on the real graph; reseed flag keeps its last value on an invalid frame; MEMORY binds (0.543 MB/op, empty session > 675 after ~86 ops, P4 164) ⇒ next LabVIEW act = error-2 re-measure, then re-base X10 or re-plan P4 — docs/d1/ring-p4.md:105
- PD301(a)-(e) MEMORY WALL REFUTED: 64-bit LabVIEW, fresh 567.7 MB, bed load +9 MB, memory resets per session ⇒ P4 feasible in fresh sessions (PD300(c) re-plan not taken); error 2 not seen to 653.5 MB, stops unchanged; patch 136-3's lookup + rerun routes; build a read-only Stop If True?/Mechanical Action op; diagnose stagesim step 102 — docs/d1/ring-p4.md:120
- PD302(a)-(c) cycle 137 cards (routes rerun, offline step-102/session/route-class/one-sided-wire facts, stop-mode op); OpLoopEndRef pattern path is tools/recipes/; review c135e disposed (bed stays; item-level wire test owed) — docs/d1/ring-p4.md:134
- PD303(a)-(d) step 102 = plan addressed CTs by owner diagram ⇒ v4 re-addresses 5 CT ends (no tool change); sessions 12/11 at 600.2/675, U05 re-cut; 17 route classes left → one scratch run after 137-1; review c135e §4 settled, bed stays — docs/d1/ring-p4.md:144
- PD304(a)(b) 2nd failure on the new-While-body node lookup ⇒ scratch-VI verification (137-3) of every read method before any route run — docs/d1/ring-p4.md:161
- PD305(a) v4 a30f7700 accepted; #10170 border crossings get explicit tunnel actions (PD298(b) precedent) → v5 — docs/d1/ring-p4.md:169
- PD306(a)-(d) v5 91f6476e (2 #10170 tunnels, replay to 103); drop the 2 RLEs after tunnel crossings (v6); step 3 = 41 accepted under "≤ ~40"; p4_x_n2_out not a #10170 crossing — docs/d1/ring-p4.md:175
- PD307(a)(b) MEASURED: a const in a new While body is not in Diagram.Nodes[] (node_labels / Stage.address blind), read_terms by owner uid finds it ⇒ diagnostics use read_terms; every plan replay also runs stagexec.compile_plan — docs/d1/ring-p4.md:186
- PD308(a)(b) v6 99586b73 (165 actions, replay to 163, compile 1–157); decide p4_dec_reseed = PD300(b) option 2 → v7; FS-exit p4_x_n2_out = stagesim row modelled on U6's measured census (next tooling card, alone) — docs/d1/ring-p4.md:196
- PD309(a)-(d) routes A2/U1/U2/W1-Or/U5 PASS, U3 (Select on Boolean array, KMX DBL) and U6 (FS exit) FAIL → 137-7 types/endpoints; FS-exit route built in stagesim AND stagexec from a passing U6, never a loop tunnel on an FS; stop-mode op → cycle 138 — docs/d1/ring-p4.md:206
- PD310(a)-(c) v7 01ab0893 = current P4 plan (172 actions, compile_plan ALL 160 ops); #10465 raw re-wire stays; replay stop 159 after delete_wire = stagesim defect → same tooling card as FS exit — docs/d1/ring-p4.md:218
- PD311(a)-(e) Select takes a SCALAR s only (measured + NI) ⇒ smallest-Num>last via For loop + scalar Select + Array Min (MAX I32 by const_donor); FS exit works with a typed source (U6′); Select out name 's? t:f'; cycle-138 order — docs/d1/ring-p4.md:226
- PD312(a)-(e) stagesim FS-exit + delete_wire fix, stagexec fs_exit, X10 source-counted reads accepted; v8 059b5296 (For + scalar Select, Greater? outside) accepted; ONE I32-MAX donor for both constants; IndexMode gates per tunnel; stop (end) is a latch ⇒ StopAll writer (PD298(e)) — docs/d1/ring-p4.md:245
- PD313(a)-(e) DonorI32Max uid 127 measured; #10465 survives delete_wire (EL 51→52, item unnamed); latch-local break confirmed; For-group rerun inside a While body; v9 rejected (copied positional fs_routes) → v10 regenerates it + StopAll init False on #4866 — docs/d1/ring-p4.md:273
- PD314(a)-(f) item 52 = "Case Structure: Unwired selector" (#10465, re-wired at once); v10 accepted; StopAll born on a False const on #4866 (P2b form) + Local write in #639 ⇒ v11 e398c447 current; loop_in needs a SubVI in the VI; fp-31 drained; p4_w_stop12/p4_t_last join the route run — docs/d1/ring-p4.md:293
- PD315(a)-(d) For group in a While body MEASURED (runs correct); DonorBoolF_v0 uid 126; the separate route run is replaced by each P4 step's scratch run; p4_w_stop12/p4_t_last re-addressed like W1-Or (v12) — docs/d1/ring-p4.md:314
- PD316(a)-(c) v12 831d899b accepted (KSF1 126, p4_w_last_gt moved to step 2); p4_w_stop12 = TOOL GAP (stop onto an existing loop's cond) → tooling card 139-5 alone, then step-1 scratch on v13 — docs/d1/ring-p4.md:327
- PD317(a)-(d) stop onto an EXISTING loop's cond built (self-test 13/0); v13 88e3f336 0 UNROUTABLE; maker step-copy bug ⇒ v14; a step plan declares only the cdiff rows its own actions make — docs/d1/ring-p4.md:338
- PD318(a)-(c) v14 22f58271 accepted; step 2 = 43 RE-CUT (steps 2-5 ≤ 41), step 1 (39) proceeds; step-0 base rows accepted only as P3b-2b's declared open rows — docs/d1/ring-p4.md:350
- PD319(a)-(c) step-1 plan e6992800 FINAL (0 new cdiff rows) but X10 750.7 > 690 (R 29 BIND reads) ⇒ P4 sessions cut by X10, not by meta steps (PD318(a) re-cut SUPERSEDED); measure whole-P4 session table + mergeable BIND reads first — docs/d1/ring-p4.md:358
- PD320(a)-(e) X10 reproduced; table A read model (9 sessions), no bind-merge tool; cut = longest ≤ 675 prefix splitting no `of` pair; session 1 = v14 ops 1..16 (673.4); start = measured load of the input file; session-1 card scratch → gated launch, session-2 prep beside it — docs/d1/ring-p4.md:372
- PD321(a)-(e) scratch op 3 RLE w23255 → 1055 (hypothesis: whole wire removed); v15 = delete_wire w23255 then delete_object #10171, gated on w23255's sinks ⊆ #10171; launch 678.5 accepted (< 690) if scratch peak ≤ 675; s02 = ops 17..31, dry after rebase — docs/d1/ring-p4.md:390
- PD322(a)-(e) ALL 6 ring slot writes are Insert Into Array (donor #29157) where the design says Replace Array Subset — repair toward the design: 1-D RAS donor `DonorRAS1D_v0.vi` built + run first, then the 5 bed nodes replaced FIRST in P4 v16; created-node prim gate owed; EL rule = one item per node — docs/d1/ring-p4.md:408
- PD323(a)-(f) bed repair form per node (delete wires/node, create from DonorRAS1D uid 175, reconnect by name); prim gate run-time + offline; X10 not recalibrated (scratch-peak gate); cycle 141 = 141-1 alone, then session-1 scratch → gated launch ‖ session-2 prep; repair functional only at P6 — docs/d1/ring-p4b.md:19
- PD324(a)-(d) v16 36981c83 + prim gates accepted; CREATE-FIRST repair order ratified (delete-first unroutable on FS faces); p4_eq_seq gets a surviving bed `Equal?` donor (v17, ops 1..24 unchanged); s01 f4831031 24 actions, X10 669.3/674.4, EL 51 — docs/d1/ring-p4b.md:43
- PD325(a)-(e) s01 scratch real == sim, prim gate 3/3, peak 601.4; TD FAIL = LabVIEW re-used deleted uids → key terminals by (uid, owner, name) + self-test; measured census into s01 pred; retry 141-3 then gated launch; v17 e19d7e14 / s02 5e483ea6 accepted, s02 cut re-checked after rebase — docs/d1/ring-p4b.md:55
- PD326(a)-(e) P4 SESSION 1 DELIVERED `D1_ring_p4s01_20261002_232547.vi` dc61e193 (EL 51 OK, peak 605.0, graph `graph_ring_p4s01_20261002_234419.json`, load 596.5); term_identity_gates accepted; X10 not recalibrated yet (start 596.5 for s02); binding raw-uid carry; cycle 142 = s02 rebase → scratch → gated launch ‖ s03 prep — docs/d1/ring-p4b.md:73
- PD268(d) 130-2 accepted; open tooling queue fp-20/21/22/24/25, guard_cycle:40, stop_record H1–H3 — docs/d1/tooling.md:34

### Older items that PD238+ cite as still applying
- PD182 record-build inputs left open for QRT by design (cited by PD257(a)) — :721
- PD193(a) Checkpoint set: whole-VI read/diff only at the set `{0, len} | BIND` (cited by PD265(c)) — :968
- PD224(d) Rule-1a acceptance precedent: recorded-frame replay, X/Y/Z bit-identical (cited by PD238(f)) — :1915
- PD232 Rows per step ≤ 15 / ~25 on a proven pattern (only OTHER stages count) — :2116; for ring steps overridden by D-2026-10-01-01 (≤ ~40, PD261(d))
- PD233(f)(1)(2) Each result carries its own frame's values (now via the per-slot arrays; kept by PD238(a)) — :2134–2137
- PD236(a) (done) Pool bed and the 20 images `Cam_pool00`…`19` — :2217
- PD236(b) Build-step handle gate = refs balanced AND open→save within the recorded band (≤ ~+700) — :2218
- PD237(g) MOVE `#10068`/`#29240` into 1.2 — re-check when P4 is planned (PD238(a)) — :2229
- PD237(j)/(m) facts: FS crossing = route `nested` + stray-`Invoke` census rule; reader `OpTermDataType_v0`; `#5058`/`#6810` terminal facts — :2232–2236, :2243–2249

## In force from other frozen documents

- `docs/cycle27-plan.md` Pre-decided 9 — EVERY GUI action is capture → locate → act → capture → confirm (cited by STATUS) — [cycle27-plan:62](../cycle27-plan.md)
- `docs/violation-decisions.md` (append-only, see its footer): device-failed 2026-10-02 02:57 (X10 fix + stop-record predicate; cycle 130 cards 1 and 4) — [:1748](../violation-decisions.md); inference-over-measurement 2026-10-02 01:01 (`tools/card_clock.py` → `protocol.py validate`) — [:1720](../violation-decisions.md); repeated-failure-class 2026-10-01 20:12 (`hygiene_run`) — [:1705](../violation-decisions.md); inference-over-measurement 2026-10-01 13:56 (census device) — [:1679](../violation-decisions.md); rule-evaded 2026-09-28 10:37 (op hygiene record ≥ 2,000 calls, cited by PD242(b)) — [:1657](../violation-decisions.md)
- `docs/d1-build-plan.md` §9 (pool queues) is SUPERSEDED by `docs/ring-buffer-design.md`; `docs/d1-route-b-plan.md` was `paused` and is frozen (no item in force).

## UNSURE (judgement to classify)

- PD238(b) "a separate scratch image is added only if P2 finds another writer/reader of `'Cam'`" — still a live condition for P3b/P4? (:2255)
- PD238(h), PD240(e)(f), PD243(b), PD249(d), PD250(d), PD251(c)(d), PD253(c)(e), PD254(e), PD255(c)(d)(g), PD257(b)(c)(e), PD258(d)(e), PD259(b)(c), PD260(c)(d), PD261(e), PD262(d), PD263(b), PD264(d), PD265(d), PD266(d): card-order / cycle-scoped items, assumed DONE or superseded by a later item — listed so judgement can confirm none still binds.
- PD245(c) "repeated class noted for the retrospective" — history or still an open note? (:2392)
- PD253(c) "`gscript.fs_donor` / `fs_frames` / `fs_add_frame` NOT machine-tested yet" — still true after PD254(a)? (:2630)
- PD256(e)/(f) — answered by PD257(a) / PD258(c); kept out of the in-force list.
- `docs/cycle27-plan.md` Pre-decided 1–126 other than 9 (e.g. 12 "Pre-decided lines are edited by JUDGEMENT sessions", :87; 13 cycle15-plan binding, :89) — not re-classified here.
- `docs/violation-decisions.md` decision blocks before 2026-09-28 10:37 — devices built and in code; not re-listed (the retrospective dispatcher extracts them mechanically).
- PD210 (display loop fed by locals) — in force for the display track, but not cited by PD238+ (:1569).

## Topic files (new decisions, numbering from 268)

| file | scope |
|---|---|
| `docs/d1/ring-p3b.md` | P3b-1 / P3b-2: split, memory, scratch, launch |
| `docs/d1/ring-p4.md` | P4 tracking loop 1.2, PD293–PD322 — FROZEN 2026-10-02 (429 lines) |
| `docs/d1/ring-p4b.md` | P4 tracking loop 1.2 from PD323 (and P5/P6 until they get their own file) |
| `docs/d1/tooling.md` | gates, simulator, prerun, ops and other tool decisions on the D1 path |
