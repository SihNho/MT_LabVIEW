# c89-profiler-plan-hyp

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.7096  in 26 / out 16660 / cache-create 124033 / cache-read 1521619  (202s, 24 turn(s))
- **date:** 2026-09-26 02:07:44
- **outcome:** ANSWERED (206s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this plan: tools/bench/profiler_run_plan_89.md (card tools/bench/cards/task_89-3.json, brief tools/bench/cards/brief_89-3.md). Read the plan file and the facts it cites (tools/bench/diag_c89_profiler_search.md, tools/bench/diag_c89_profiler_lvsr.log, archive/peer/2026-09-26-c89-profiler-fact.md, archive/peer/2026-09-26-c89-profiler-fact2.md).

CLAIM under attack: "Running LabVIEW's built-in Profile Performance and Memory window (GUI: Tools » Profile » Performance and Memory, Timing statistics ON, Memory usage OFF, Start before the VI runs, Snapshot + Save after the VI Server stop) over an unmodified run of D1_s1_copy.vi, at 15 and at 8 bead picks, 120 s at 90 Hz, will tell WHERE the per-bead frame cost goes (kernel vs check-N-bead-pos vs filters vs display VIs vs plot VIs vs save VIs), with an overhead that can be stated from Total Lost Frames against the uninstrumented references (3,776 / 3,331 / 3,161 at 15 picks; 16 / 12 at 8 picks). The Profile window is not scriptable (negative search), D1_s1_copy.vi has debugging allowed (LVSR DebugCapable bit set), and the enumerated GUI acts with capture->locate->act->capture->confirm are sufficient and safe to run unattended inside the existing drive_m8 leg driver."

PREDICTED by the plan: the saved tab-delimited file ranks the per-bead groups by CPU ms per frame and the 8-vs-15 pick comparison isolates the per-bead lever; profiling costs some frames but the 8-pick leg stays near 16 lost frames.

Already ruled out / known:
- In-VI tick-count instrumentation (cards 89-1, 89-2): needs verbs this project lacks (frame move; >=10 primitives via copy_by_index); a CLFN-based stamp (archive/peer/2026-09-26-c89-donor-census-hyp.md) is a judgement question, not this card's.
- The profiler measures CPU time only (NI); memory profiling is OFF because NI says it distorts timing.
- NI documents no programmatic route (negative search record with URLs).

Questions for the adversary: (1) the strongest reason the plan will NOT answer PD195(d) - e.g. the CPU-only clock missing UI-thread display cost, clone aggregation hiding per-bead work, the profiler perturbing the 15-pick regime, the kernel being a CLFN/DLL whose time is attributed to the caller, or the Profile window blocking COM (ExecState/SetControlValue) so the unattended driver stalls; (2) an alternative measurement that is cheaper or more discriminating with the SAME constraints (no VI edit, no new scripting verbs, unattended, LabVIEW 2026, Windows 10); (3) what result would falsify "the per-bead lever is in these subVIs"; (4) the cheapest discriminating test to run FIRST (e.g. one 30 s dry leg with the Profile window open to test COM liveness before the two 120 s legs); (5) any GUI act in section 2 whose predicted observable is wrong for LabVIEW 2026 (menu path, window title, button labels, checkbox defaults, Time unit default, the Save dialog's behaviour).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No, the claim does not hold as written. The plan as specified is unlikely to answer PD195(d). The profiler can rank named subVIs, but the question is which per-bead work in the frame loop costs the frames, and that is exactly what this run design blurs. I read the plan, the cited facts and the drivers. I could not fetch NI's own profiler pages through WebFetch; they returned only a navigation shell. So every claim below about the NI window is marked verified or unverified.

## 1. Strongest reason the claim is wrong: what the profiler attributes is not what PD195(d) asks

The plan's R2 and R3 reasoning assumes that summing subVI times gives one loop's cost per frame, during the experiment only. Three facts break that.

- **The whole top-level diagram is one row.** The profiler reports time per VI. Everything placed directly on `D1_s1_copy.vi`'s own diagram appears as a single "VI Time" for the top-level VI. That covers the 17 For loops, the 3 While loops (the frame loop 637 plus two others, `docs/g9-core-budget.md:60-63`), inline array work, the indicator writes and the 19 property-node `Value` accesses (`docs/t0-instrumentation-plan.md:85-86`). The t0 model's 4.7 ms fixed cost is back-calculated and has never been measured (`t0-instrumentation-plan.md:16,21-22`). If the per-bead cost is inline code rather than one of the named subVIs, it lands in that one undivided row, and the plan has no gate for this case. W2 and R4 check that the subVI rows exist, not how much sits outside them.
- **All loops and all phases are mixed together.** P-F starts profiling before L1. The totals therefore include the picking loop (running for minutes with display), about 2 minutes of z-stack calibration for 15 beads (`drive_original_copy_v5.py:368-370`), the bandpass dialogs and the 120 s run. Several of the named VIs (median/FIR filters, the kernel lineage, display) can run in more than one of those phases or loops. The table has no loop or phase breakdown, so "Average × calls-per-frame" is not a cost per frame of the frame loop. W3 (`# Runs ≥ frames×picks`) passes even when calls from other phases inflate the counts, so it cannot catch this.
- **R2's test cannot pick the lever.** Every per-bead group grows by about 15/8 = 1.875× by construction, so "the group that grows ~2×" returns all of them. The lever is the group with the largest cost in absolute ms per bead. And R3 (sum ≥ 11.1 ms) is only meaningful if every summed call sits in the frame loop, which is not established.

## 2. Alternative explanation for the 8 → 15 pick cliff (16 → about 3,300 lost frames)

- **UI-thread contention.** At 15 picks there are 15 markers, circles and text items, two N-bead plots and the IMAQ display, all redrawn per frame. Rendering happens on the UI thread, and the frame loop's property-node `Value` accesses must wait for that thread. That serializes the frame loop behind drawing. This time appears in no subVI's VI Time, or is misattributed. The "Display/Draw" columns come only with Timing details, which the plan leaves "as found", probably off.
- **Timer caveat.** The profiler uses QueryPerformanceCounter timestamps (NI's Rob Dye on LAVA, [lavag.org/topic/15007](https://lavag.org/topic/15007-profile-performance-and-memory-inaccurate-numbers/)), so it records wall-clock time per execution segment. NI's "CPU only" wording refers to Wait nodes. Nobody has stated how time spent blocked on UI-thread switches is counted, so the profiler may either miss or misplace exactly this cost. I could not settle this from the web.
- **The kernel-swap result is weaker than 195(c) says.**
  - At 15 picks the swap lost 3,410 / 3,490 frames against controls of 3,776, 3,331 and 3,161. That control spread is about ±300 frames.
  - The parallel kernel saves roughly 1 ms per frame (`g9-core-budget.md:42-43`). Under the t0 model that would reduce the loss by about 400–500 frames, which is inside that spread.
  - So the test could not have shown a kernel effect. "The kernel is not the lever" is not established; the kernel stays a candidate.

## 3. What would falsify "the per-bead lever is in these subVIs"

Measure over the experiment window only, from snapshots taken at L10 and after L12, then differenced:
- The named per-bead subVIs add up to well under the roughly 5 ms of extra per-frame time that the 15-pick loss implies (about 33% lost ⇒ about 16.5 ms effective against 11.1 ms), while the top-level VI's own time, or the time the profiler never sees, accounts for the difference.
- Or: hiding the panel during the run collapses the 15-pick loss (see §4).

Either result means the lever is display or inline code, not a subVI in the table.

## 4. Cheapest discriminating test, and what to change first

1. **Test the GUI and COM with nothing running (about 30 s, no frame regime at risk).** Open the copy, open the Profile window, Start, then read ExecState and do a SetControlValue round trip. Snapshot and Save while idle, and check the header, the unit and the file's decimal precision. This isolates P-A to P-J and W4. Liveness while idle does not prove liveness during a run, but the Profile window does not auto-refresh, so a stall during the run is unlikely.
2. **The discriminating run: one 15-pick leg with the panel minimized after L10.** Do the picks visible, then call `OpenFrontPanel(False, <minimized>)` (or set FPState) through the existing COM path. That is a change to the bench driver's argument, not a VI edit and not a new scripting verb, and it changes no computation. If lost frames fall far below about 3,300, display or UI-thread work is the lever and the profiler run is the wrong instrument. If they don't change, run the profiler legs with the fixes below.
3. **Fixes to the profiler legs if they run:**
   - Timing details ON, so Display and Draw are recorded.
   - Time unit set to **µs**, not ms. Save writes the displayed values, and per-call Averages of tens of µs would round to 0.0 or 0.1 ms. That precision loss is my inference and was not verified in LabVIEW 2026.
   - Either Start after L10, or Snapshot + Save at L10 and again after L12, then difference the two files. NI's "start before the run" advice is about complete runs of the top-level VI; per-subVI calls are complete either way.
   - Put the 8-pick leg first and read its loss before trusting any overhead statement. By the t0 model, 8 picks is about 10.1 ms against the 11.1 ms budget, so about 1 ms of profiling overhead would tip it over the cliff and collapse the comparison. At 15 picks the ±300-frame spread means overhead is only resolvable above about 600 frames.

## 5. GUI contract details likely wrong or unverified in §2 of the plan

- **P-F and P-K:** in my recollection (unverified; the NI page could not be fetched) Start is a single button that relabels to Stop, not two separate buttons. P-K's "locate `Stop` button" would then find the same button that P-F clicked, and "Start disabled, Stop enabled" is the wrong prediction.
- **P-E:** there are two memory checkboxes, `Profile memory usage` (set before Start) and `Memory usage` (display), per the fact file (`archive/peer/2026-09-26-c89-profiler-fact.md:53`). "Left as found" should assert that both are unchecked.
- **Unverified for 2026 (web docs unreachable):** the menu path and window title, whether vi.lib and password-protected VIs (IMAQ) get rows, and whether inlined subVIs get any row (my inference: they don't, since their code is copied into the caller). W2 should list which expected rows are missing, not fail on them blindly.
- **Clone aggregation is undocumented** (F6). It matters only if any group VI is reentrant, and the plan does not check that. The `IsReentrant` / `ReentrancyType` properties exist over ActiveX (`fact2.md:31`), so this is a cheap read.

## What would change my mind

A snapshot differenced over the experiment window in which:
- the named subVIs account for at least 80% of the per-frame time implied by the frame period,
- the top-level VI's own time is small, and
- the minimized-panel test leaves the 15-pick loss unchanged.

Then the profiler answers PD195(d) as the plan claims.

Sources:
- [LAVA 15007: profiler timing uses QueryPerformanceCounter since LV2017/18](https://lavag.org/topic/15007-profile-performance-and-memory-inaccurate-numbers/)
- [NI: Using the Profile Performance and Memory window](https://www.ni.com/docs/en-US/bundle/labview/page/using-the-profile-performance-and-memory-window.html) (not fetchable this session)
- [NI: Profile Performance and Memory window](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/dialog-boxes/profile-performance-and-memory-window.html) (not fetchable this session)
- [NI forum: Preallocated reentrant VI within a parallelized For loop](https://forums.ni.com/t5/LabVIEW/Preallocated-Reentrant-VI-within-Parallelized-For-Loop/td-p/3080639)
- [NI forum: Profiler with sub-panel VIs shows 0.0](https://forums.ni.com/t5/LabVIEW/Performance-Profiler-with-Sub-Panel-linked-VI-s/td-p/778154)

## Sources

(extract from answer)

## What was done with it

Card 89-3 (material, fable/low). Disposition written into `tools/bench/profiler_run_plan_89.md` §6. APPLIED there
(prediction-contract corrections only): P-F/P-K one Start→Stop button; P-E asserts both memory checkboxes unchecked;
W2 prints missing rows instead of failing blindly; W0 records IsReentrant/ReentrancyType per group VI. NOT APPLIED —
handed to the judgement session as `open` in `tools/bench/cards/result_89-3.json`, because they change the
measurement's design: A1 idle liveness test first, A2 minimized-panel discriminating leg before any profiler leg,
A3 Timing details ON + µs unit + L10/L12 snapshot differencing + 8-pick leg first, A4 R2/R3 rewrite. The review's
§2 point that the 195(c) kernel-swap verdict sits inside the ±300-frame control spread is reported as a fact.
