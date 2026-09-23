---
type: reference
status: current
date: 2026-09-16
tags: [decisions, architecture, settled]
---

# Settled decisions — the ones that must not be re-opened without the user

Moved out of `STATUS.md` on 2026-09-16, when that file reached 255 lines against a ~100-line budget (CLAUDE.md
rule 4). STATUS points here; nothing was rewritten in the move except where a later measurement had already
superseded a line, and each of those says so.

## The architecture, as decided

| question | decision |
|---|---|
| **acceptance bar** | **C** — camera acquisition, tracking, motor reading, scheduler and data merging/saving each in **their own loop**. The frame loop (diagram 43) emptied into the seven-loop target |
| **construction method** | restructure **inside a COPY of the original** — not a hot-path-only swap, not a fresh rebuild in an empty VI. Rule 1 unchanged: the original is never touched. Method proven end to end (`probe_migrate_v2` 3/3, `probe_migrate_v3` 5/5, `ExecState == 1`); **untested is SCALE and RUNTIME, not feasibility** |
| **camera readout** | `IMAQdx Get Image`, **`Buffer Number Mode = Last`** — newest buffer, never waits, cannot gate the camera. `Next` measured at 74.9 Hz vs `Last`'s 123.0 Hz under 8 ms of work |
| **the camera free-runs** | the PC is a **reader, never a gate**. No mechanism may throttle acquisition. No pool eviction, no `Lossy Enqueue Element`, no generation numbers |
| **frame handoff** | **pre-allocated image pool + slot index** (`frame-ownership-design.md:23-39`): one copy per frame, measured **0.12 ms**; start at **20 slots**; ring depth absorbs jitter only — 10/50/100 buffers all failed at the same delay. Pool authority is a bounded `Q_free`, invariant **free + queued + processing = 8** (`stage2-plan.md:64-67`) |
| **time axis** | the **buffer number**, never a software timestamp. Frame N happened at N/framerate because the frame rate is hardware-controlled; skipping gives a uniform grid with holes |
| **no free slot** | simply do not read this iteration. Gap accounting = the jump in `Buffer Number Out` |
| **overload, acq → tracking** | **lossy, latest-wins** — discard the backlog, take the newest frame. A stale sample corrupts the time series; an explicit gap does not |
| **overload, tracking → writer** | **lossless FIFO** — a computed result is never dropped or reordered |
| **frame identity** | every result carries its frame number; pixels and buffer number must change together or it is corruption (the user's acceptance test) |
| **scheduler → motor transport** | **local variables**, as agreed with the user (`restructure-plan-4.6.md:42`, `rotor-scheduler-design.md:66-75`) — they neither serialise the loops nor enter the UI thread. Publish **one cluster local** rather than four scalar locals, which removes the tearing a 2026-09-12 peer identified without introducing a queue |
| **the rotor row** | calls `SetCommand.vi` **exactly as the existing `Send to Rot` path does** — same `Baseline Startpoint`, same `Ring` — with only the commanded value coming from the schedule (`rotor-scheduler-design.md:143-148`, quoting the user: *"configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?"*). The signed variant is a separate hardware-verified artefact, **not** something the restructuring adopts. ⚠️ **SUPERSEDED 2026-09-24** by `docs/cycle27-plan.md` Pre-decided 133 and CLAUDE.md 1b (user 2026-09-16: the rotor is signed, the new VI uses `SetCommand_signed.vi`; hardware-verified `tools/bench/hw_rotor_signed_test.log`) |
| **no serial on the frame path** | CLAUDE.md rule 1c. The ASI/serial loop owns its VISA session exclusively and reaches the frame path only through a non-blocking handoff. A mechanism that *can* stall the frame loop is disqualified even if it usually does not |
| **fallback, authorised** | if the handoff cannot be made provably safe, acquisition and tracking stay in **one sequential loop**. Acquisition-parallel-to-tracking is NOT mandatory |

## The four decisions of 2026-09-16

| | decision |
|---|---|
| **camera** | **90 Hz; `ExposureTime` ≈ 5 556 µs = half the 11.111 ms period; `ExposureAuto` OFF.** Removes the dark-field auto-exposure hazard by the operating condition rather than by argument. **The dry-run frame budget is 10 ms**, the period minus ~1 ms of measured jitter margin. ⚠️ **A session open RESETS exposure** (measured; `camera-acquisition-facts.md`), so the acquisition loop must write and read back the contract itself — no external pre-pass can do it |
| **GPU** | our own interface is **built, callable via one CLFN, measured 1.14 ms/frame in a tight loop**, outputs inside tolerance (x,y 4.9e-7 px / z 2.9e-6 µm / 0 flips). ⚠️ At 90 Hz the card idles into **P8** and everything slows ~3.5× unless the SM clock is locked (`gpu-backend.md:225-241`); the lock script already exists (`tools/gpu/register_gpu_clock_lock.ps1`). **Whole-fixture (10,043 frames, `gpu-backend.md` §2026-09-17): first 10,018 frames inside tolerance; exceedances only on bead 4 in the post-loss tail; ONE z-slice tie-break one frame early at k1679 (Δz 4.7 nm, 1 frame). USER DECISION 2026-09-17: "현재로서는 통과" — accepted for now, to be revisited later.** |
| **order** | **the MAP comes first** — the user's standing instruction, *"내 지시였음."* |
| **backend** | **the GPU top level is built FIRST and is the default**; the CPU-parallel top level follows. Two separate VIs |

## The restructure order — measurement decides it, not assumption

| # | step | status |
|---|---|---|
| 1 | measure the **unconditional per-frame path**, p50 **and p99** | not done — this is what Phase A exists to enable |
| 2 | **one vertical slice**: acquisition → owned image handoff → queue core → frame-identified result, with stop, error, reseed, overload | not started |
| 3 | split whichever measured owner **dominates** | not started |
| 4 | scheduler, file writer — completes the 7-loop target | not started |

Target architecture and per-stage numeric acceptance: `restructure-plan-4.6.md` §3 and §5.
**Judgement returns at step 2, not before** — the split order depends on step 1's numbers.
