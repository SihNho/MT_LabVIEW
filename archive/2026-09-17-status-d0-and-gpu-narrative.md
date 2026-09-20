---
type: archive
status: archived
date: 2026-09-17
tags: [status, narrative, d0, gpu, cycle15]
supersedes: []
---

# STATUS narrative relocated 2026-09-17 — D0 (items 15–18), the GPU N1 numbers, the lock-holder history, OPEN 1

Rule 4 relocation: `STATUS.md` had reached **268 lines** against the ~100-line threshold. Everything below is the
**verbatim** text that was in `STATUS.md` on 2026-09-17; nothing is rewritten, only moved. `STATUS.md` keeps one
line per item and points here. Companion archives: `archive/2026-09-16-status-cycles-11-13-narrative.md` and its
two siblings.

---

## 1. Lock-holder history (the "who held LabVIEW, what was created and deleted" comment block)

Verbatim from the `labview-lock` YAML block's trailing comments:

```yaml
# last held material/cycle15-D0-v3, 2026-09-17 02:29-02:49: d0_clickprobe.py (END rc=0, 177 s, 12/12) then
# drive_original_copy_v3.py (END rc=0, 230 s, 16 pass / 0 fail - THE FULL UNATTENDED CYCLE RAN). MAIN VI NEVER
# OPENED FOR EDIT, md5 2a78e17c449cacdaf5da389818526859 before AND after BOTH runs; scratch copies
# D0_MAINCOPY_20260917_{022955,024503}.vi created and DELETED in the same run; 2 041 TIFFs / 2.68 GB written in
# the 20 s window and ALL DELETED (run folder left holding only cal001 + tra001-000); 10 GUI actions, all logged
# with -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"; LabVIEW pid 24956 killed between the
# two runs (its instrument sessions were left dangling by the probe's Abort), and the v3 instance exited.
# last held material/cycle15-D0-v2, 2026-09-17 02:10-02:22: drive_original_copy_v2.py, BGRUN END rc=1 after
# 683 s, 18 pass / 13 fail. MAIN VI NEVER OPENED FOR EDIT, md5 2a78e17c449cacdaf5da389818526859 before AND
# after; scratch copy D0_MAINCOPY_20260917_021053.vi created and DELETED in the same run; ZERO TIFFs written
# (the VI never reached the frame loop) and the run folder was removed empty; LabVIEW pid 16520 killed after
# the run (Abort skips diagram 83, so IMAQdx/ASI Close never ran - do not leave that instance up).
# 10 GUI actions, all logged with -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1".
# last held material/cycle15-D0, 2026-09-17 01:35-02:05: drive_original_copy.py runs 1 (rc=1, 24 s, call-mechanism
# bug) and 2 (rc=1, 255 s), then a MANUAL GUI walk of the picking/calibration/save path on the still-running copy.
# MAIN VI NEVER OPENED FOR EDIT, md5 2a78e17c449cacdaf5da389818526859 before AND after; scratch copy
# D0_MAINCOPY_20260917_014823.vi created and deleted in the same run; LabVIEW pid 7816 KILLED (never saved).
# Instruments driven by the copy's startup: PI translation stage (diagrams 1-5), ASI TG-1000 (10/12), camera
# (1280x1024, live). Rig DISASSEMBLED, so all three are allowed (rule 1b). 11 GUI actions, all logged to
# tools/gui_actions.log with -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1" (13 rows dated
# 2026-09-17: 3 image-display clicks, 1 done button, 3 bandpass "Yes", 4 save-dialog actions, 1 abort, 1 ^a).
# last held material/cycle15-step1, 2026-09-16 22:05-22:14: diag_stop_save_seam.py (END rc=1, 117 s, 29/30 - P5 is a
# real failed prediction, reviewed) + diag_stop_condterm_panel.py (END rc=0, 30 s, 3/4). MAIN VI READ-ONLY, md5
# 2a78e17c449cacdaf5da389818526859 before AND after both runs; no scratch VI created; LabVIEW pids 4184/24232 exited.
# Earlier holders: archive/2026-09-16-status-cycles-11-13-narrative.md
# MAIN VI NEVER OPENED (scratch copy of EMPTY_v0, deleted in the same run, gate Z); no op saved; pid 17996 exited.
# Earlier holders: archive/2026-09-16-status-cycles-11-13-narrative.md
```

---

## 2. OPEN items 11–14 (retrospective v2, doc lint, the stop/save seam, the partly-disposed prior-art review)

Verbatim:

> 11. ✅ **Retrospective v2 ADOPTED; its five OPEN items A–E are all closed** — dispositions in
>    `tools/bench/retro_v2_comparison.md` §7. `violations.py --due` is **empty, rc=0**; cycle 11's review cost reads
>    **$0.0000 → $19.6411** after the regex repair; the cycle window is now **previous retrospective → this cycle's
>    retrospective dispatch** (cycle 11 = `14:33:20 .. 19:08:16`, which the plan-mtime window started at 17:38:44).
> 12. ✅ **Document lint + ingest BUILT, and the first backlog is CLEARED** (`docs/doc-lint-plan.md`).
>    `tools/doc_lint.py` runs inside `audit_cycle` as L-lines; `tools/doc_ingest.py` dispatches the sonnet
>    consistency read to `archive/ingest/` (invisible to all six gates; `-Role ingest`, registered in `logclass.py`).
>    **doc_lint 3 fail/3 warn/3 pass → 1 fail/3 warn/5 pass**: L2 and L4 fixed, only L6's 26 post-09-15 dispositions
>    left. The ingest's **7 contradictions: 6 resolved in the docs, 1 left to the user** (PAIR 4, rotor `SetCommand`).
>
> 13. 🟢 **Cycle 15 step 1(b)(c) MEASURED → `docs/main-vi-stop-and-save.md`** (new; the original's stop path, the
>    `save N xyz traces.vi` #6384 call site with every input's source, the diagram-83 shutdown calls, and the
>    16-terminal tracker seam #5058). 🟡 **One question left open there**: which of wire 3457's two `Diagram#639`
>    sinks is `WhileLoop#637`'s conditional terminal — one is indicator `TurnOff` #24423, the other is unnamed.
>    **Guessed twice ⇒ build the READER** (CLAUDE.md): (1) a RECURSIVE `ControlTerminal` census with
>    `Connected Wire` (`panel_wiring` is documented non-recursive — that is what made prediction Q2 unprovable),
>    then (2) `WhileLoop.Loop End Ref` **0x06362C00** only if (1) finds nothing. Two peer reviews, both ANSWERED and
>    disposed: `archive/peer/2026-09-16-stop-condterm-{failed-prediction,panel-fail2}.md`.
> 14. 🔴 **The cycle-15 prior-art review is only PARTLY disposed** —
>    `archive/peer/2026-09-16-priorart-priorart-cycle15-d1.md` (ANSWERED, 418 s, $3.28, 12 findings, 0 `novel`).
>    The material half is released there (`FIXED: already-measured`, `FIXED: unread-evidence`). **A1/A2
>    `settled-already` and A3–A6/B2 `contradicted` and A7/B3 `unread-evidence` are left BLOCKING on purpose**: they
>    say D1's construction method is the one `docs/decisions.md:19` excludes, that option A as the user answered it
>    is the inverse of D1, and that `SubVI.Replace` 635E001 (the swap primitive D1's build step assumes) is
>    UNVERIFIED and absent from `gscript`. Only a judgement session may refute or fix those.

---

## 3. Item 15 / 15b — `bgrun.py --detach`, and the orphaned-grandchild defect

Verbatim:

> 15. ✅ **`bgrun.py --detach` BUILT and MEASURED** (cycle 15 deliverable 1). The runner re-execs itself with
>    `DETACHED_PROCESS|CREATE_NEW_PROCESS_GROUP|CREATE_BREAKAWAY_FROM_JOB` and the caller returns at once, so a
>    sub-agent's exit can no longer kill the child (it did twice on 2026-09-16, leaving START with no END).
>    `tools/bench/detach_test.log`: parent returned 01:30:43, 40 s child → `BGRUN END rc=0 after 40s`, `mode=breakaway`.
>    `tools/bench/detach_timeout_test.log`: `--max-min 0.15` → `BGRUN TIMEOUT killed after 10s`. Deadline and the
>    END/TIMEOUT line survive detachment. Two defects the review found are fixed in the same file: the kill's result
>    is now on a **`BGRUN KILL taskkill rc=… still_listed=…`** line (it used to be discarded, so "killed" was
>    unconditional), and the detached copy's stdout+stderr go to **the log**, not DEVNULL (a pre-START crash used to
>    vanish). Peer: `archive/peer/2026-09-17-bgrun-detach-deadline.md` (ANSWERED 139 s, adopted).
> 15b. 🔴 **MEASURED: bgrun's deadline kill does NOT kill an orphaned grandchild** — `tools/bench/detach_canary.log`,
>    the peer's own decisive test. runner → A → B → C (B exits at once): `taskkill /F /T` rc=0 killed three
>    processes, `BGRUN TIMEOUT killed after 13s` at 01:41:51, and **C kept heart-beating at 01:41:57 / 01:42:05 /
>    01:42:13**. `taskkill /T` walks the live ancestry, so an intermediate exit removes the branch. **Pre-existing,
>    not caused by `--detach`**; bgrun's docstring "KILLS THE WHOLE TREE" is therefore conditional. The fix (a
>    runner-owned Job Object with `KILL_ON_JOB_CLOSE`) is a **judgement call** — it fights `CREATE_BREAKAWAY_FROM_JOB`
>    and would kill a LabVIEW.exe a workload expects to survive. Review: `…-bgrun-treekill-orphan.md`.

---

## 4. Item 16 — the GPU N1 full-fixture numbers

Verbatim:

> 16. 🔢 **GPU N1 — the 10,043-frame fixture comparison is RUN** (`tools/bench/gpu_n1_full_fixture.log`,
>    `N=10043 py tools/gpu/test_mt2.py`, 112 s wall, SM clock lock already registered + card at P0/1365 MHz):
>    **10,043 frames · max |Δx| 4.13e-06 px · |Δy| 3.13e-05 px · |Δz| 1.28e-05 µm · flips 1 · DLL median 1.67 ms.**
>    Acceptance in `docs/decisions.md:38` is x,y ≤ 1e-6 px and 0 flips ⇒ **x/y and the flip count are OUTSIDE it**;
>    z is inside the user-accepted ~1e-4 µm. The 200-frame record (4.9e-7 / 2.9e-6 / 0 flips) did not survive the
>    full fixture. 🔴 **Whether that is acceptable is a JUDGEMENT call, not made here.**

The **localisation** of that divergence (per bead, per axis, the flip's neighbourhood, clustering, run-to-run
reproducibility) was measured on 2026-09-17 and lives in `docs/gpu-backend.md` (dated MEASURED section) with the
raw per-frame deltas in `tools/bench/gpu_n1_deltas.json` (script `tools/bench/gpu_n1_deltas.py`,
log `tools/bench/gpu_n1_deltas.log`).

---

## 5. Items 17–17d — D0, the original VI's unattended path

Verbatim:

> 17. 🟡 **D0 — the original's UNATTENDED path is now MAPPED, and it is longer than the plan says.** Driver
>    `tools/bench/drive_original_copy.py` (+ `d0_probe.py`), logs `drive_original_copy{,_run2}.log`, screenshots
>    `tools/bench/d0_shots/`. **The original was never opened for edit; md5 `2a78e17c…` before AND after; the
>    scratch copy `D0_MAINCOPY_20260917_014823.vi` was deleted in the same run; LabVIEW pid 7816 killed without
>    saving.** What the run MEASURED:
>
>    | step | route | result |
>    |---|---|---|
>    | plain file copy into claudeDev loads | COM | **PASS** — `ExecState 1`, no "Find the VI" modal. Preloading the ORIGINAL read-only first puts `background VIs\` in memory by name |
>    | `Run(False)` starts it | COM | VI runs, camera live — **but the COM call never returned** (see below) |
>    | bead picking | **GUI, 3 clicks on the Image display** (uid 31543; screen rect **232,500–873,1013**) | **PASS** — each click plants a red marker |
>    | end picking | **GUI**, `Done Picking \nBeads?` "Yes" at **(1114, 915)** | **PASS** — calibration z-stack starts, `Count` 0→1 |
>    | **per-bead `choose bandpass v2.vi` panel** 🆕 | **GUI**, "Yes" at **(175, 353)**, **once per bead** | **PASS** — NOT in any plan; a 3-bead run needs 3 of these |
>    | **"Save cal cluster file" Windows dialog** 🆕 | **GUI**, type path + OK **(1541, 563)** | **PASS** — wrote `tools/bench/d0_out/d0cal001` (171 552 B). ⚠️ it opens in the **user's real data folder** |
>    | experiment loop runs | file evidence | **PASS** — **2 621 TIFFs / 3.28 GB in ~30 s**; frame numbers have gaps (lost frames) |
>    | stop through the VI's own control | — | **NOT TESTED** — had to Abort to stop the 118 MB/s TIFF flood |
>    | trace file | — | **none** — consistent with `main-vi-stop-and-save.md:80`: `save N xyz traces.vi` runs AFTER the frame loop, so an Abort produces no `traNNN` |
>    | restart | — | **NOT REACHED** |
>
>    🔴 **The "COM was blocked" reading is WITHDRAWN.** codex refuted it from our own source
>    (`archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md`): the driver has ONE COM worker thread, it was
>    stuck inside `Run(False)`, so the later calls never crossed COM at all — `"LabVIEW is blocked"` was the
>    harness's own sentence. **The real anomaly is that `vi.Run(False)` did not return**, and whether
>    Get/SetControlValue work during a run is **unmeasured**. Also recorded from that review: **`SetControlValue`
>    raises no Value Change event**, so it can never replace a click where the diagram waits on an event — which is
>    why the user's option 1 is the right mechanism, not a fallback.
> 17b. 🔴 **D0 v2 RAN (`tools/bench/drive_original_copy_v2.py`, log `…_v2.log`, END rc=1 683 s, 18 pass/13 fail).
>    The redesign WORKED where v1 died, and it is now blocked on ONE thing: a scripted click on the
>    `choose bandpass v2.vi` panel is not delivered.**
>    * ✅ **P3 — codex's falsification test is RUN and v1's "LabVIEW blocks COM" is DEAD.** A SECOND,
>      independently initialised COM apartment answered **7** `ExecState`/`GetControlValue` calls while the RUN
>      apartment had **not** returned from `Run(False)`. Polling during a run is fine; v1's single worker was the
>      whole problem.
>    * 🔴 **MEASURED TWICE: `vi.Run(False)` over ActiveX behaves as *Wait Until Done = TRUE*.** It returned only
>      when `Abort` fired — after **338.1 s** (run 1) and **310.8 s** (run 2), err=None both times. This is the
>      anomaly codex named, now a fact. **Issue Run on a thread nothing waits on; never inside the command queue.**
>    * ✅ GUI picking is solid: the panel window is found by title (rect −6,51–1930,1107), and the three measured
>      clicks in the Image display each planted a marker (screenshot `d0_shots_v2/…_run1_after_picks.png`); the
>      `Done Picking` click ended the picking loop in **27 s** (run 1).
>    * 🔴 **P6 FAILED, identically in both runs**: one click at the measured (175,353) — verified inside the
>      panel's own measured rect (29,72–1060,874) — left the panel unchanged, still reading `Bead # 1`, two
>      minutes later. Peer: `archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md` (codex, ANSWERED 213 s)
>      **REFUTED** my "event structure not ready" explanation (static events are registered at run-mode entry and
>      **queued**; a locked panel *defers*, never discards) and names the real gap: **`lv_gui` reports a click when
>      its function returns, not when a control receives it** — `mouse_event` has no return value, `Focus`
>      discards `SetForegroundWindow`'s result, and Windows can eat the activating click (`MA_ACTIVATEANDEAT`).
>    * 🔴 **P10 says NOTHING about the stop control** — the VI was parked inside the bandpass subVI, not in the
>      frame loop, so the stop Booleans were never read. Abort stopped it both times. **Requirement 5 is UNTESTED.**
>    * Operational facts: **Abort leaves the bandpass subVI panel on screen**, and run 2's P5 "pass" is spurious
>      because it detected that stale window — close it before any restart. `0c/0d` measured offline: **no
>      front-panel CONTROL gates the TIFF writer** (0/60 labels; `IMAQ Write TIFF File 2` uid 22700 sits directly
>      on the frame `WhileLoop`'s diagram, not in a Case) and **no CONTROL carries a save path** (`Cal File Path`
>      27930 / `Track File Path` 28450 are INDICATORS), so the Windows dialog is the only route.
> 17c. ✅ **SOLVED, and it INVERTS 17b: the bandpass click was ALWAYS DELIVERED. Our progress predicate was wrong.**
>    `tools/lv_gui.ps1 -Action clickprobe` (new, gated + logged like `click`) + `tools/bench/d0_clickprobe.py`
>    (`BGRUN END rc=0 after 177s`, 12 pass / 0 fail, md5 unchanged, copy deleted, 0 TIFFs, 6 GUI actions).
>    The record around ONE click on the Yes button, after the panel had been up 12 s:
>    `setforegroundwindow.ret=true` · `fg_after_sfw_is_target=true` · `fg_at_buttondown_is_target=true` ·
>    `WindowFromPoint(176,353).root == target` · `hwndCapture=0 hwndMenuOwner=0 flags=0` · **`after_500ms.alive
>    = FALSE` for the target hwnd 19728546**, and `fg_after_click.hwnd = 19794082` carrying the **identical
>    title** `choose bandpass v2.vi`. **So the panel DID close within 500 ms and a successor panel took its
>    place.** v2's test `win_present("choose bandpass")` is TITLE-based, so it read the successor as "the same
>    panel never closed". **H1 (foreground/z-order) and H2 (deferral) are BOTH refuted by the same record.**
>    The successor panel still reads `Bead # 1` but is POPULATED (cursors on `Cal image`, data in `Cal image with
>    chosen filter`) where the first was blank ⇒ **"one Yes per bead" is an assumption the machine has not
>    confirmed**; the count must be driven by the save dialog, not by `len(PICKS)`.
>    * 🟡 **Failure budget (2) SPENT on this one class.** Next step is the READER codex prescribed, not another
>      attempt: one probe logging, around a single click, `SetForegroundWindow`'s return · `GetForegroundWindow`
>      · `WindowFromPoint(x,y)` · `GUITHREADINFO` `hwndCapture`/menu flags, before and after — and a
>      **token-gated** click (never a blind retry: the panel reuses the same title, rect and Yes coordinate for
>      every bead, so a late click plus a retry can accept bead 1 then land on bead 2). Building that touches
>      `tools/lv_gui.ps1`, which carries the GUI gate ⇒ **judgement call**.
> 17d. ✅ **D0 IS CLOSED — the original's full unattended cycle RAN, 16 pass / 0 fail**
>    (`tools/bench/drive_original_copy_v3.py`, log `…_v3.log`, `BGRUN END rc=0 after 230s`). One mechanism changed
>    against v2: every panel click goes through `clickprobe` and **the token is the HWND, not the title**.
>    | step | mechanism | result |
>    |---|---|---|
>    | 3 bead picks · Done Picking | GUI click (measured coords) | PASS, 27 s to end the picking loop |
>    | 3 × `choose bandpass` Yes | **HWND-gated clickprobe** | **PASS — hwnds 2295998 → 2361534 → 2427070, each dead <500 ms, ONE click each, zero retries**; terminal state = the save dialog |
>    | `Save cal cluster file` | focus + ^a + type + ENTER | PASS → `cal001` 171 552 B **inside our run folder** |
>    | frame loop, 20 s | VI Server poll | PASS `current image number` 7232 → 8860, **lost = 32**, **2 041 TIFFs / 2.68 GB** |
>    | **stop (requirement 5, previously UNTESTED)** | **`SetControlValue('stop (end)'/'stop (end) 2', True)`** | ✅ **WORKS — idle after 2 s, ONE re-arm.** No Abort, no GUI |
>    | trace file | file check | PASS `tra001-000` 196 282 B, written by `save N xyz traces.vi` **because the VI stopped properly** |
>    | restart + 15 s + stop | COM | restart PASS; **the stop is a FALSE POSITIVE — see below** |
>    🔴 **The one real defect in v3: R11's stop heuristic.** A restarted run re-enters the **picking** loop, where the
>    stop Booleans are never read, so `current image number` is frozen simply because no frames are being taken. My
>    "frame counter frozen ⇒ the loop ended" rule scored that PASS while `ExecState` was still 2, and cleanup then
>    needed the Abort fallback (`stop[cleanup]: VI-Server stop did NOT idle in 60s`). **Read requirement 5 as: the
>    stop control works IN THE FRAME LOOP, and only there.**
>    🟡 Also unconfirmed: `Count` stayed **1** across all three bandpass clicks, so it is **not** a bead-progress
>    signal — gemini's proposed gate does not exist on this panel.
> 18. 🔴 **NEW COST FACT for the seven-loop design: the original saves EVERY FRAME as a 1.3 MB TIFF** next to the
>    cal file (`IMAQ Write TIFF File 2` #22700, diagram 43) — **~118 MB/s at 90 Hz**. Any unattended overnight
>    harness must bound this or the disk fills in minutes.

---

## 6. OPEN 1 and the other items' long form

Verbatim (the OPEN block as it stood before the relocation, items 1–10 and the NEXT/Where-to-look sections that
were compressed in place):

> 1. 🟡 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** Measured on the wire side: `ForLoop#1359`'s ten
>    terminals carry **no** `Auto-Reset` (wire 9806) and zero panel-control sources ⇒ **not gated at the wire level**.
>    Not final — a `Value` property read inside #1359 could still gate it; one read closes it (cycle 14 §5). Tables → narrative archive, OPEN 1.
> 2. 🟢 **Autofocus path CLOSED** — the switch that stops the piezo is `Auto-Focus` (uid 24266);
>    `CaseStructure #10407` fires every 25 frames ≈ 3.6 Hz. `docs/camera-acquisition-facts.md`.
> 2c. 🟢 **uid 9775 READS camera geometry; the size the VI WRITES is the front-panel display area, not the ROI** —
>    the 1280×1024 budget basis is safe. Do NOT widen to "the VI does not set frame size" (codex refuses it);
>    residual test: `Property Items[] → Is Write` over the 106 Property nodes.
> 3. 🟡 **Peer-archive dispositions** — 39 pre-2026-09-15 closed as `disposition: legacy` (`tools/mark_legacy_dispositions.py`,
>    4/4 gates; doc_lint L6 skips them); **26 dated ≥ 09-15 are real debt**. L1: 54 of 324 docs still lack frontmatter.
> 4. `Global motor pos.vi` — write-only here; **user: a readability container covering all motors, keep it**.
> 5. **Startup drives instruments** (ASI on diagrams 10/88, PI on 1/3/4/5 — `main-vi-startup.md:22-33`). Allowed
>    while apart; a hard blocker at assembly. Excise node-by-node in the build log, not wholesale (rule 1a).
> 6–8. ✅ RESOLVED — bgrun's failure regex narrowed (11/11), REVIEW logs skip the inner-failure scan, and the
>    `premature-build` / `scope-creep` devices are built and tested. → narrative archive.
> 9. 🟢 **A2 DONE** — owner semantics for all six structure classes (54/54); `FlatSequence` the one exception
>    (owner uid 0, error 1055). `docs/diagram-hierarchy.md`. → narrative archive for the three judgement calls.
> 10. 🟢 **A3 MEASURED for the 112 clean diagrams** (100 agree / 0 disagree; `tools/bench/diagram_tree_a3.json`).
>    Left: exactly the **57 `FlatSequenceFrame` diagrams**, and they ARE reachable — `FlatSequence.Diagrams[]` =
>    **3578BC00** measured attaching. 🟡 Walking it needs ONE new op VI: the judgement call cycle 13's STOP condition reserved. → narrative archive, OPEN 10.

The earlier OPEN-1 measurement tables were already relocated to
`archive/2026-09-16-status-cycles-11-13-narrative.md` (section "OPEN 1"); this file does not duplicate them.
