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

- **Work VI (bed):** `claudeDev\D1_ring_p3b1_20261002_060910.vi`, md5 `9d7bf28738b7c154280e5e7c2c9d4961` (STATUS `current-bed:`; PD274 — [ring-p3b:64](ring-p3b.md)). Error List 53 items, expected file `tools/bench/errorlist_expected_D1_ring_p3b1_20261002_060910.json`. STRUCTURAL, `ExecState` 0 by design, never run. (Before: P3a `D1_ring_p3a_20261001_180540.vi` `4dfa44aa…`, 55 items.)
- **Broken-intermediate count (CLAUDE.md "AT MOST 6"):** 3 of 6 (P2b 1, P3a 2, P3b-1 3). After P3b-2: 4 of 6; P4 and P5 use 5 and 6; P6 must run (PD261(d) — [split-plan:2847](../d1-loop12-17-split-plan.md)).
- **Plan of record for the frame handoff:** `docs/ring-buffer-design.md` (user design 2026-09-28; PD238(a)). User rules checked by every design item: `docs/user-rules.md`.
- **Next act (cycle 134):** P3b-2 session b (PD287(e)) — card 1: dry rule device, Flat Sequence frame/border reader, graph read of `claudeDev\scratch_c133_6_ring_p3b2a_20261002_093837.vi`, b finalized directly on it, b dry/prerun; card 2: scratch b on a copy, Error List count-only 49..52; card 3: ONE launch of both sessions. (Cycle 133: fs_routes, P3b-2 cut into sessions a 21 / b 18 by memory, FR fix, session a scratch PASS 650.9 MB — PD282–286; user question D-2026-10-02-02.)

## Ring-buffer step table (PD238(g) — [split-plan:2260](../d1-loop12-17-split-plan.md))

| step | content | state | where |
|---|---|---|---|
| P1 | buffer-mode measurement, no VI | DONE — `Last` + `Wait (ms)` 1 adopted | PD238(i) :2262 |
| P2a | remove the pool's queue nodes, keep the 20 images | DELIVERED `D1_ring_p2a_20260928_191739.vi` (`c22a473f…`) | PD238(l) :2266 |
| P2b | `Num`/`TransPos`/`RotPos`/`FrameIdx`/`Latest` + their init on FS1 `#4866` | DELIVERED `D1_ring_p2b_20261001_140658.vi` (`652b1447…`) | PD246(a) :2397 |
| P3a | loop-1.1 control: wait, two registers, `Equal?`, case, counter, mod 20 | DELIVERED `D1_ring_p3a_20261001_180540.vi` (`4dfa44aa…`) | PD251(a) :2552 |
| P3b-1 | slot writes part 1 (IMAQ Copy + error guard; 31 actions) | DELIVERED `D1_ring_p3b1_20261002_060910.vi` (`9d7bf287…`) = bed; 680.4 MB, EL 53 | PD271–274 (tooling.md:56, ring-p3b.md:35–64) |
| P3b-2 | slot writes part 2 (TransPos/RotPos/FrameIdx groups, Latest); 39 actions applied in TWO LabVIEW sessions (a 21 / b 18) by memory | IN PROGRESS — session a scratch PASS (650.9 MB); session b: dry rule + FS reader, finalize on a's real graph, scratch; then ONE launch of both (stop 690, EL 49..52) | PD283–287 (ring-p3b.md:155–277) |
| P4 | tracking-loop 1.2 rows (seqlock read, `last` register, jump to `Latest`) | NOT STARTED — size it with the memory formula first | PD238(e) :2258, PD266(b) :2946 |
| P5 | results queue 1.2 → 1.7 (lossless FIFO) | NOT STARTED | PD238(d) :2257 |
| P6 | recorded-frame replay (X/Y/Z bit-identical) + real ABBA at 90/150 Hz | NOT STARTED — first RUN of the chain | PD238(f) :2259 |
| after P6 | ONE interface-contract step (every loop's published/read locals) | NOT STARTED | STATUS `## NEXT` parallelism rule |

## Open user decisions (`tools/bench/decisions_pending.json`)

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
| `docs/d1/ring-p4.md` | P4 tracking loop 1.2 (and P5/P6 until they get their own file) |
| `docs/d1/tooling.md` | gates, simulator, prerun, ops and other tool decisions on the D1 path |
