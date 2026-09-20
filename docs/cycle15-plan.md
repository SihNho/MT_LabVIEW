---
type: plan
status: paused
date: 2026-09-16
paused: 2026-09-18 by the cycle-17 judgement session — the user's P1 order (STATUS `## NEXT`, 2026-09-17 23:4x)
  puts `docs/motor-limit-assurance-plan.md` ahead of the D1 build "for now". Its `## Pre-decided` section stays
  authoritative for the D1 queue/shift-register questions and is still cited from STATUS; nothing here is retracted.
cycle: 15
kind: delivery
tags: [plan, delivery, runnable-vi]
supersedes: [docs/cycle14-plan.md]
decided_by: user 2026-09-16 ("A로 진행하자")
---

# Cycle 15 — DELIVERY: the first runnable experimental VI

**Why this cycle is a delivery cycle.** Two outcome reviews in a row (2026-09-15, 2026-09-16) reached the same
verdict: zero runnable experimental VIs; the user would still run the original next week. CLAUDE.md's rule for a
repeated OUTCOME-VIOLATION is to stop and re-plan with the user. The user chose option A on 2026-09-16 — build the
smallest runnable VI from what is already known — and added the boundary: **"여기는 중간 과정일 뿐 결국에는 최종
스텝으로 나가야함."** So this cycle is *ordering*, not a new goal; the seven-loop restructure (GPU top level as
default, CPU-parallel second) remains the destination. `docs/cycle14-plan.md` (the `Diagrams[]` op, 170/170
hierarchy, A4) is superseded; A3 stands at 112/170 and is resumed only if D1 needs a diagram it does not have.

## CORRECTED 2026-09-17 — D1 is the FIRST SLICE of the seven-loop VI, not a hot-path swap

The section below ("The product, D1") is **withdrawn**: a tracker-only swap is the construction method
`docs/decisions.md:19` excludes, and the prior-art review (cycle15-d1) caught it. Explained to and approved by the
user 2026-09-17 (`archive/prose/2026-09-17-d1-d2-explained-r2.md`):

- **D1 = master plan rows 1.1 (acquisition) + 1.2 (tracking, GPU kernel) + 1.7 (file writer) + 1.8 (frame
  accounting) + 1.9 (stop/shutdown)**, built inside a copy of the original; stages 0–3 of the original (panel
  parameters → configure → bead-picking loop → button + calibration) stay exactly as they are.
- **D2 = rows 1.3 (scheduler) + 1.4 (motor, `SetCommand_signed.vi`) + 1.5 (ASI/focus) + 1.6 (display)**, then
  the Phase 2 dry-run checks.
- **Tracker: GPU first** (`GPU_kernel_v1.vi`); its acceptance record is 200 frames × 3, so **N1 requires the
  10,043-frame fixture comparison to be run first** (`N=10043 py tools/gpu/test_mt2.py` or equivalent). CPU
  top level afterwards.
- **Unattended (user requirement):** the harness drives the picking stage itself — scripted clicks on the image
  display (first = reference, rest = magnetic), the done button, save path + name — via `lv_gui.ps1`,
  `-Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`. Tracking errors without beads are
  expected and not a failure. **D0 (precondition, its own milestone):** the harness can take a plain copy of the
  original through stages 0→4 with nobody present, run it, stop it, and restart it. D1's F1/F2 reuse that driver.

### D1 spec decisions after the d1-build prior-art review (judgement, 2026-09-17)

1. **#10407 (autofocus, VISA) gets its own loop in D1** — a minimal row 1.5: the case and its VISA session in a
   loop of their own, woken every 25 frames by a *latest-result* notifier (lossy, non-blocking) from the tracking
   loop; its other inputs by the same route and values as today. Neither the tracking loop (a VISA stall would
   fill `Q_work` and lose frames — rule 1c) nor the acquisition loop (its input no longer exists) is legal.
2. **Writer = stream AND accumulate**: the 1.7 loop writes each result as it arrives (row 1.7's streaming
   requirement) *and* accumulates the arrays; at stop it calls the original `save N xyz traces.vi` #6384 with them,
   so the `.tra` format is byte-compatible.
3. **Stop nodes**: `stop (end)` #7 → `CompoundArithmetic` #11639 and `stop (end) 2` #19587 → #17883 →
   `Tunnel #22085` of `CaseStructure #22082` — two nodes, a fourth structure; the plan places #22082 explicitly.
4. **Structures in the kernel's forward slice** (#5540, #2222, #12589, #1359, #29874 and #10407) move by the
   documented **Make Selection → Copy Selection → Paste onto the subdiagram** route (`vi-scripting.md:323-325`),
   which has never been run — so it is **probed first** (`probe_move_into_v0.py`), never inside the D1 build.
5. **Precondition readers/devices (round-5 decisions):** `OpLoopEndRef_v0` (how #637 actually stops — D1's S4
   gate) and bgrun's `-> FAIL` scan.

## (withdrawn) The product, D1

**A copy of the original VI** (`restructure_inside_a_copy_of_the_original` decision) in which **only the per-frame
tracking call is swapped** for the tracker that already has a passed numeric-acceptance record on the fixture, with
everything else — live camera acquisition, bead picking, calibration, the original's file writer
(`save N xyz traces.vi`), its stop path and its instrument shutdown — **left exactly as the original has it**.

That is the smallest thing that is (a) runnable live, (b) rule-1a checkable (same inputs → same X/Y/Z on the
fixture, against the original), and (c) a real step toward the final restructure, because the tracker swap is the
core of it. It is deliberately NOT the reviewer's full slice (acquisition → GPU tracker → new writer → new
stop/restart): a new writer and a new stop protocol are two more untested parts, and each is a place to be wrong.
They come next (D2), once D1 runs.

## Acceptance for D1 — numeric and functional, stated before the build

| gate | what | level |
|---|---|---|
| N1 | On the recorded fixture (10,043 frames, 5 beads), D1's X/Y/Z equal the original's for the first 10,018 frames (before the first bead loss) to the tracker's recorded tolerance — the same statement STATUS makes for the replay VIs, now for the runnable one | numeric, rule 1a |
| F1 | D1 runs live on the camera at 90 Hz with no beads (rig disassembled; camera allowed) for ≥ 5 min, produces a data file through the original's writer, and the file reopens | functional |
| F2 | D1 stops through the original's stop path with no error 1122 / no orphaned camera session, and restarts clean | functional |
| F3 | The rotor path, if it is touched at all, uses **`SetCommand_signed.vi`** — user decision 2026-09-16: the rotor is signed by nature, LabVIEW's serial path lost the sign, the fix is believed found; follow the hardware number with its sign | rule, user |

`ExecState == 1` counts for nothing here.

## Order of work

1. **Measure before building** (this cycle's first material session; facts only, no build):
   a. Which trackers hold a **passed** numeric-acceptance record today, at what tolerance, against which reference
      (`archive/benchmarks/INDEX.md` rows 40–41 for the CPU queue tracker; `docs/gpu-backend.md` for the GPU
      one). The choice between them is a judgement made on that table — GPU is the intended default, but D1 uses
      whichever is *proven now*.
   b. How the original actually stops, closes instruments and writes its file — `docs/main-vi-state.md` and
      `main-vi-startup.md` do not say (log-reader, 2026-09-16: two matching lines in 211). Read the main VI
      headlessly: the stop Boolean's terminal and every node that reads it; the call site of `save N xyz
      traces.vi` and what feeds it; the camera-close / VISA-close nodes and which diagram owns them.
   c. The exact call site of the per-frame tracker in diagram 43 (already in `frame-loop-anatomy.md`; confirm uid
      and terminal names with `node_terms`).
2. Prior-art review (`--trigger direction-change`) on this plan, disposed.
3. Build recipe for D1 — one script, prediction contract N1/F1/F2/F3, on a copy in `user.lib\claudeDev`; the
   original untouched (md5 before/after).
4. Run N1 offline (fixture), then F1/F2 live (camera only; no motors are needed for D1).
5. Hand D1 to the user with the four gate values. Then D2 (writer + stop protocol of the seven-loop design).

## Freeze exceptions granted 2026-09-17 (closed at four ops — see d1-build-plan.md §11g/§11j/§11m)

`OpCreateEqual_v0` · `OpCreateConst_v0` · `OpCreateConstOnTerm_v0` (Terminal.Create Constant 6349C00) ·
`OpConnectNested_v0` (Terminal.Connect Wire 6349C03, both ends by index on nested diagrams). Each is a D1 part,
each additive on a proven ladder, each with one prior-art dispatch. Nothing else is unfrozen; the list is closed.

## Pre-decided

Decisions a material session **applies without asking**, citing the numbered item. Relocated VERBATIM from
STATUS.md on 2026-09-17 (rule 4: STATUS was 123 lines; the text is unchanged, only its home is). They were taken
by the judgement session of 2026-09-17 evening under the heading "✅ ALL THREE DECIDED — the next material session
BUILDS, it does not ask". CLAUDE.md §3 item 2 requires this section; `tools/doc_lint.py` L8 warns when it is missing.

1. **Queue element types = `docs/d1-route-b-plan.md` §9's table, verbatim** — the type source is the NAMED output
   terminal of the fresh-dropped node (queue_node's `src_name`): `Q_free`/`Q_work` ← `IMAQ Create`'s `New Image`
   sample (bounded 20); `Q_meta`/`Q_rmeta` ← `#6810 current image number` (DBL); `Q_res` ← GPU kernel `x,y,z
   array out` (DBL[]); `Q_good` ← `Bead is good? array out` (Bool[]); `Q_focus` (1-elem) ← `pos in cal image
   out` (DBL); `Q_focusback` (1-elem) ← `#10407` t6 (Bool — ⚠️ superseded by `docs/d1-build-plan.md` §9: **1 DBL**). Run `s1q` then `s4b` (the three `Equal?` +
   `OpStopFromNode_v0` exits) BEFORE the ExecState read — that alone is expected to turn ExecState 0 → 1.
2. **`#1359` / `#29874`'s shift registers MOVE WITH THEIR NODES into 1.2** (`add_shift_reg` + `wire_sr`, the decided
   mechanism, one writer per loop); keep `index_mode 1` on the auto-indexing sink exactly as the original has it.
   `SR_QUEUE_AUTHORISED` stays False.
3. **`Z/dZ` → `#2222` t0: REORDER** — wire `Z/dZ` to `#2222` t0 (by index, `OpConnectNested_v1`, sink is
   `is_source` FALSE) BEFORE the S3-ct reparent of `ControlTerminal #403`; no temporary sink, no renaming.
4. `OpGetErrors_v0` stays unbuilt until F1/F2 (the plan's own ordering). If ExecState is still 0 after 1–3, the
   bare-terminal census over all 173 diagrams is the reader.
5. **Session hygiene (why that judgement session got long):** a material session that returns "blocked-on-
   judgement" on a question the plan already answers costs a full turn there — before returning, grep the plan
   for the answer. The judgement session is closed after its cycle; the next one starts fresh from STATUS.md +
   `d1-route-b-plan.md` §9/§11 only (CLAUDE.md §3: one cycle per session, now spawned by `tools/cycle_runner.py`).

Unchanged and still blocking above all of these: **OPEN 32** — two consecutive outcome reviews demanding a
re-plan with the USER. No material session resolves that one.

## Frozen while D1 is built (outcome review Q7, adopted)

No new general-purpose op VIs, no hierarchy completion beyond what D1 needs, no lint/annotation cleanup, no new
benchmark themes, no display polish, no review-framework changes.
