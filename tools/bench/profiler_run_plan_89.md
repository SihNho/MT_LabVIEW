---
type: plan
status: current
date: 2026-09-26
card: 89-3
supersedes: []
tags: [profiler, PD195d, M8, run-plan]
---
# Profiler run plan (card 89-3): per-subVI time of the UNMODIFIED `D1_s1_copy.vi` with LabVIEW's own profiler

**Goal** (`docs/d1-loop12-17-split-plan.md` Pre-decided 195(d)): find WHERE the per-bead frame cost goes — kernel,
`check N bead pos v3-kimlab.vi`, median/FIR filters, Draw*/Flatten Pixmap display VIs, `N bead plot Z/dZ.vi`,
`save trace.vi` / `save N xyz traces.vi` (`docs/t0-instrumentation-plan.md:96-104`) — WITHOUT editing the VI (cards
89-1/89-2 showed the in-VI stamp routes need verbs this project lacks). Rule 1a is untouched: nothing is built.

## 0. Measured facts this plan rests on (card 89-3, 2026-09-26)

| # | fact | evidence |
|---|---|---|
| F1 | The profiler has NO scripted route (no VI Server method/property, no ini token, no CLI switch; only a hidden password-protected `_Profile Buffer Allocation.vi` that writes a binary BAP and blocks execution) | `tools/bench/diag_c89_profiler_search.md` (negative-search record; peer `archive/peer/2026-09-26-c89-profiler-fact.md:31-37`) |
| F2 | Save writes "a tab-delimited text spreadsheet file" of the currently DISPLAYED data; columns = VI Time, Sub VIs Time, Total Time, Project Library + (Timing statistics) # Runs, Average, Shortest, Longest + (Timing details) Diagram, Display, Draw, Tracking, Locals + (Memory usage) Avg/Min/Max Bytes, Avg/Min/Max Blocks; a "Time unit" selector (µs/ms/s) sets the unit — **ms is not fixed**; Snapshot must precede Save (Save saves what is displayed) | fact.md:41-44, NI https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/dialog-boxes/profile-performance-and-memory-window.html , https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019LT1SAM |
| F3 | The profiler measures **CPU time only** ("measures only CPU usage time"; waits register only entry/return); memory profiling "adds a significant amount of overhead … affects the accuracy of any timing statistics" → Memory usage stays OFF; NI states no timer resolution; historic 15.6 ms granularity, QueryPerformanceCounter since LV2017/2018 | fact.md:51-55 |
| F4 | NI documents NO "Allow debugging" precondition for profiling; the property exists (`Execution:Allow Debugging`, ActiveX `VirtualInstrument.AllowDebugging`, R/W, not settable while running) | fact.md:48, `…-c89-profiler-fact2.md:28-31` |
| F5 | **`D1_s1_copy.vi` HAS debugging allowed**: LVSR `instrState` u32 @0x18 = `0x40800210`, pylabview `VI_IN_ST_FLAGS.DebugCapable = 1<<9` SET (set = allowed). Same word on the ORIGINAL and on `D1_s1_kswap_…`; cross-check: NI's `vi.lib\Utility\High Resolution Relative Seconds.vi` decodes DebugCapable=False, LibProtected=True (NI ships vi.lib locked and non-debuggable) — the decode discriminates | `tools/bench/diag_c89_profiler_lvsr.log` (15 gates / 0 fail), decode source fact2.md:37-39 |
| F6 | Dynamically loaded (sub-panel) VIs show 0.0; the profiler lists "all the VIs in memory" of the application instance; reentrant-clone aggregation is undocumented | fact.md:60-65 |
| F7 | Uninstrumented S1 references for the overhead statement (Total Lost Frames, 120 s, ~89 fps ≈ 10,680 frames): **15 picks 3,776** (cycle 88 same-session S1 control, STATUS:71), **3,331 / 3,161** (cycle 83 `tools/bench/m8_load_83.json:279`, repeat); **8 picks 16 / 12** (`m8_load_83.json:55,167`) | STATUS.md:71,100 |

## 1. Leg integration — where the profiler acts sit in the existing driver

Driver = `tools/bench/drive_m8.py --leg s1 --picks N --run-s 120` (cycle 83/88 pattern, `drive_m8_load83.py:62`). It
copies `D1_s1_copy.vi` → `claudeDev\D1_s1_copy_run_<ts>.vi` (M1 md5 check), then `v5.main()`:
G0 motor gate start → G3 COM open of the copy (`d0.com.call("open")`, panel not shown) → `leg("run1")` = L1 Run →
L2–L5 picks + done (GUI, `-Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`) → L6–L8 bandpass →
L9 save dialog → L11 120 s frame count → **L12 stop (VI Server)** → L13 trace file → `cleanup()` (CloseFrontPanel,
release, **LabVIEW exit / Stop-Process G92**, motor gate end).

**New file, nothing existing edited:** `tools/bench/diag_c89_profiler_leg.py` (≤120 lines) — pre-imports
`drive_original_copy_v5 as v5`, wraps `v5.leg` as `profiled_leg`, sets `sys.argv` and calls `drive_m8.main()`
(`drive_m8.main` captures `real_leg = v5.leg` at `drive_m8.py:88`, so a wrapper installed BEFORE `main()` is what
runs). The wrapper:

```
profiled_leg(tag, n, base_path, cal_wait):
    P-A .. P-F   (before the VI runs: open the Profile window, tick Timing statistics, Start)
    ok = real_leg(...)               # L1..L13 unchanged; L12 stops the VI by VI Server
    P-G .. P-K   (after the stop: Snapshot, Save → our path, verify the file)
    return ok
```

Order matters: NI's procedure is Start **before** the VI runs ("start profiling while the application is not running
to measure only complete runs", fact.md:54); Snapshot + Save happen after L12 while the VI is idle and LabVIEW still
open (cleanup closes LabVIEW afterwards — the Profile window is not closed by us; Stop-Process ends it).

Output per leg: `tools/bench/diag_c89_profiler_out/profile_s1_p<N>_<ts>.txt` (tab-delimited) + the leg's
`m8_s1_p<N>.json` (Total Lost Frames, frame counter series). Two legs, one bgrun each (`--max-min 25`; cycle-83 legs
took ≈8–10 min), **15 picks first, then 8 picks**, both 90 Hz (150 Hz unreachable without an `.icd`/VI change,
STATUS:101). Retry cap: 2 LabVIEW runs of this stage per cycle (`tools/stage_prerun.py:1262`) = exactly these two legs;
a failed leg is NOT rerun in the same cycle without a judgement card.

Gates of the wrapper (each a `rec(...)` row, C6 `RESULT` line at the end): W1 profile file exists, >0 B, first line
contains `VI Time` (tab-delimited header); W2 a row whose name starts with the kernel VI's name and rows for every
group VI of t0-plan Step 1 are present (list them by basename; the MISSING names are printed — inlined / vi.lib /
password-protected VIs may legitimately have no row (review §5) — and W2 fails only if the kernel row is missing);
W0 pre-run facts: ActiveX `IsReentrant` / `ReentrancyType` of every group VI recorded (clone aggregation, F6); W3 `# Runs` of
the kernel row ≥ frames counted in L11 × picks − 1 % (sanity: the profiler saw the whole run); W4 the COM liveness
check P-F passed; W5 LabVIEW gone after cleanup (`M6`); W6 `D1_s1_copy.vi` md5 unchanged (`M7`).

## 2. EVERY GUI act, enumerated (capture → locate → act → capture → confirm; Pre-decided 9: no remembered coordinates)

Common: every act goes through `tools/lv_gui.ps1` from the project root, as `d0.gui(...)` does
(`drive_original_copy_v2.py:297-303`). Diagnostic actions (`windows`, `rect`, `shot`, `shotwin`, `crop`, `focus`,
`key esc`) need no exception. State-changing acts on the profiler carry
`-Exception NegativeSearch -Evidence tools/bench/diag_c89_profiler_search.md`; the bead-pick acts inside `real_leg`
keep their own `Approved` evidence. Locating is done on the capture taken immediately before (template = text label
crop; `d0_locate.py` has `locate_red_yes_button` / `locate_image_display` / `count_red_markers` — a small
`locate_label(png, rect, text)` for the menu/button labels is written in the wrapper's helper, verified on the
first capture of the run; if a label cannot be located the act is NOT performed and the leg is aborted as
RECOVERY_LOCKED (CLAUDE.md §3 "Failed batch")).

| id | window / target | act | predicted observable (contract) | on failure |
|---|---|---|---|---|
| P-A | the copy's front panel `D1_s1_copy_run_<ts>` (title substring `d0.COPY_TITLE`) | `focus -Title <title>` → `key esc` (skill: focus taps Alt, Esc leaves menu mode) → `shot` | foreground title strip (crop of the title bar) contains the copy's name, NOT the original's | abort leg (never click on an unverified window) |
| P-B | its menu bar, `Tools` | locate the `Tools` label in the strip captured in P-A (skill offset `(+220,+41)` is the SEARCH HINT only, never the click) → `click` (NegativeSearch) → `shot` | a drop-down appears below `Tools` whose capture contains the row label `Profile` | `key esc`, one retry from a fresh capture, then abort |
| P-C | the `Profile` row of the open Tools menu | locate `Profile` in the P-B capture → `hover` (skill: hover, never click, to descend) → `shot` | a submenu appears containing `Performance and Memory...` | esc + abort |
| P-D | `Performance and Memory...` submenu row | locate in the P-C capture → `click` (NegativeSearch) → poll `windows` ≤ 10 s | a new top-level window whose title contains `Profile Performance and Memory` is listed; `rect -Title` returns a rectangle; `shotwin` of it shows buttons `Start`, `Snapshot`, `Save` and checkboxes `Timing statistics`, `Timing details`, `Memory usage` | abort (RECOVERY_LOCKED: capture + `dialogs` only) |
| P-E | `Timing statistics` checkbox in that window | locate the label in the P-D capture; crop the 16×16 box left of it; if UNCHECKED → `click` (NegativeSearch) → re-crop | box pixels change from unchecked to checked (the crop's dark-pixel count rises); `Timing details` left as found (review A3 proposes ON — judgement); BOTH memory boxes — `Profile memory usage` (pre-Start) and `Memory usage` (display) — are ASSERTED unchecked from their crops (Memory OFF — F3); the `Time unit` ring's text is captured and RECORDED (ms expected; if not ms the value is recorded and the file's unit is taken from the ring capture, never assumed; review A3 proposes µs — judgement) | abort |
| P-F | `Start` button | locate `Start` in a fresh capture → `click` (NegativeSearch) → capture; then **COM liveness**: `d0.com.call("state")`/ExecState read must answer within 10 s | the SAME button's label crop changes `Start` → `Stop` (review: one button that relabels; unverified for 2026 — if instead a separate `Stop` button enables, record which and continue); ExecState still 1 (idle) and the COM read returns; if COM hangs → the Profile window blocks COM and the route is dead for unattended use (this is the discriminating test the card asked for; RECOVERY_LOCKED + report) | abort before Run |
| — | `real_leg(...)` runs L1..L13 unchanged (bead picks by the standing Approved evidence; VI stopped at L12 by VI Server) | | | |
| P-G | Profile window | `focus -Title 'Profile Performance and Memory'` → `key esc` → `shotwin` | title verified; table area captured (may still be empty) | abort post-run acts, leg data (lost frames) still valid |
| P-H | `Snapshot` button | locate → `click` (NegativeSearch) → `shotwin` after 2 s | the table area's capture differs from P-G (rows appear); the first column shows VI names including the copy's name | one retry, then record "no snapshot" and skip Save |
| P-I | `Save` button | locate → `click` (NegativeSearch) → poll `windows` ≤ 15 s | a file dialog appears (title read LIVE from `windows`; predicted to contain `Save`); its rect is read | esc + record |
| P-J | the file dialog's name field | `focus` → `keys ^a` → `keys <absolute path>` → `shot` → `keys {ENTER}` (the `d0.answer_save_dialog` pattern, `drive_original_copy_v2.py:522-560`; keyboard only, no coordinate) | the dialog closes within 16 s (`windows` no longer lists it); the file exists, > 0 B, header line contains `VI Time` and `# Runs` | if still open: `shot`, `key esc`, record; the leg's frame data stands |
| P-K | the P-F button, now labelled `Stop` (optional, tidy) | locate `Stop` → `click` (NegativeSearch) | its label crop reads `Start` again; never click the title-bar X (skill: no blind X clicks) | ignore — cleanup's LabVIEW exit ends it |

GUI action count per leg: 6–7 new state-changing acts (P-B, P-D, P-E?, P-F, P-H, P-I, P-J keys, P-K) + the
bead-pick acts already approved. All are logged to `tools/gui_actions.log` by `lv_gui.ps1`.

## 3. Prediction contract for the RESULT (what the two files must show)

- R1 the kernel VI (`Find xy center with sock corr.vi` / `Track xy and profile.vi` lineage — the name as it appears in the
  table is read from the file, not assumed) has `# Runs` ≈ frames × picks (per-bead call) or ≈ frames (per-frame
  call) — which of the two tells whether the kernel is called per bead (t0-plan Step 1 assumption).
- R2 `Average` (VI Time / # Runs) per group, converted to **ms per frame** = Average × calls-per-frame, tabulated for
  15 and 8 picks; the group whose ms/frame grows ~2× from 8 to 15 picks is the per-bead lever PD195(d) asks for.
- R3 the sum of the per-frame groups is compared with the frame period 11.1 ms (90 Hz): a sum ≥ 11 ms at 15 picks and
  < 11 ms at 8 picks is consistent with the lost-frame jump (16 → 3,331); a sum far below 11 ms at 15 picks means the
  loss is NOT CPU time in these subVIs (waits, UI thread, display drawing, which the profiler's CPU-only clock does
  not see — F3) and the next measurement must be a wall-clock one.
- R4 `Sub VIs Time` of the top-level copy ≈ Σ VI Time of its subVIs (consistency of the table).

## 4. Overhead of profiling itself — how it is stated

Profiling adds CPU work to every subVI call. It is stated, not assumed, by three numbers per leg written into the
leg JSON and into `archive/benchmarks/INDEX.md` (new row):
1. **Total Lost Frames of the profiled leg** vs the uninstrumented references F7: 15 picks 3,776 (cycle 88) and
   3,331 / 3,161 (cycle 83); 8 picks 16 / 12. The difference is the profiler's cost in frames — the only number that
   matters for the user's constraint (rule 1c). A profiled 8-pick leg that loses ≫ 16 frames means the profiler itself
   perturbs the regime it measures, and the 15-pick numbers are then upper bounds only.
2. **Frame counter delta over 120 s** (L11 series) vs ≈ 10,680 at ~89 fps.
3. **Profiled total CPU time of the top-level VI** vs the wall time of the run (120 s + calibration): the ratio
   bounds how much of the wall clock the profiler even sees (CPU only, F3).
Per-VI times are **CPU ms**, aggregated over clones (undocumented, F6) — they rank groups; they are not the per-frame
wall-clock cost. A wall-clock stamp inside the loop (89-1/89-2's route) remains the only way to measure waits.

## 5. What this card does NOT do (rules)
No leg is run here. The wrapper is written and DRY-RUN (`--dry`, `m8_dry.stub` pattern, `drive_m8.py:87`) in the next
card; the first real leg is the next card's act, after the LabVIEW Error List check and motor session start the
runner performs. Never edit/save `D1_s1_copy.vi`, the originals or the L2-A1 bed.

## 6. Peer review disposition — `archive/peer/2026-09-26-c89-profiler-plan-hyp.md` (claude/hypothesis, opus-5-5 high, ANSWERED 206 s)

Verdict: **the claim does not hold as written** — the profiler ranks named subVIs, but (i) everything inline on the
top-level diagram (17 For loops, 3 While loops, indicator writes, the 19 property-node `Value` accesses) is ONE
undivided row; (ii) Start-before-L1 mixes the picking loop, ~2 min of z-stack calibration and the bandpass phase
into the same totals with no phase breakdown; (iii) R2's "grows ~2×" test returns EVERY per-bead group by
construction; (iv) the 195(c) kernel-swap verdict is inside the ±300-frame control spread, so the kernel is still a
candidate; (v) UI-thread/display contention would appear in no subVI row (or be misplaced — how blocked time is
counted is unsettled; the timer is QueryPerformanceCounter, LAVA 15007).

**Applied in this file (prediction-contract corrections, no design change):** P-F/P-K — `Start` is (per the review,
unverified for 2026) ONE button that relabels to `Stop`; the contract is now "the button's label crop changes
Start→Stop", and P-K clicks that same button; P-E — TWO memory checkboxes exist (`Profile memory usage`, set before
Start, and `Memory usage`); the contract asserts BOTH are unchecked; W2 lists the missing expected rows by name
instead of failing blindly; a cheap ActiveX `IsReentrant`/`ReentrancyType` read of each group VI is added to the
wrapper's pre-run facts (clone aggregation is undocumented, F6).

**NOT applied — judgement decides (design changes to the measurement; `result_89-3.json` `open`):**
- A1 idle GUI+COM liveness test first (30 s, no leg): open copy → Profile window → Start → ExecState +
  SetControlValue round trip → Snapshot → Save → check header/unit/precision.
- A2 discriminating leg BEFORE any profiler leg: one 15-pick leg with the front panel MINIMIZED after L10 via the
  existing COM path (`OpenFrontPanel`/`FPState`); loss ≪ 3,300 ⇒ display/UI thread is the lever and the profiler is
  the wrong instrument.
- A3 if the profiler legs run: Timing details ON (Display/Draw columns); Time unit **µs**; Snapshot+Save at L10 AND
  after L12 and DIFFERENCE the two files (experiment window only); 8-pick leg FIRST (at ~10.1 of 11.1 ms it is the
  overhead-sensitive one; at 15 picks overhead is resolvable only above ~600 frames).
- A4 the plan's R2 replaced by "largest absolute ms per bead"; R3 only over the differenced window.
- Falsifier stated by the review: named subVIs ≪ the ~5 ms/frame the 15-pick loss implies, or the minimized-panel
  leg collapsing the loss ⇒ lever is display or inline code, not a subVI row.
