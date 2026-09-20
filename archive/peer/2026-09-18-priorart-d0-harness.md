# priorart-d0-harness

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.3149  in 36 / out 33996 / cache-create 241966 / cache-read 2090297  (455s, 31 turn(s))
- **date:** 2026-09-18 17:06:00
- **outcome:** ANSWERED (456s)
- **why asked:** MANDATORY cycle-start PRIOR-ART review (CLAUDE.md §5, fourth layer) before building D0, the
  unattended harness for a plain copy of the original tracking VI. The recipe named in the brief,
  `tools/recipes/build_d0_harness_v0.py`, did not exist yet; `guard_cycle.premature_build()` refuses a recipe
  with no prior-art review newer than itself, so this dispatch was the cycle's longest pole.
- **verdict:** SEVEN slugs, all seven ACCEPTED IN FULL and acted on: `settled-already` · `contradicted` ·
  `unread-evidence` · `already-built` · `already-failed` · `helper-exists` · `already-measured`. The headline —
  "this harness exists and passed 16/16 as `drive_original_copy_v3.py`; what is new is a four-item delta, not a
  build" — was taken as correct and the planned recipe was ABANDONED. Released by the `FIXED:` lines below.

## Question

PRIOR-ART REVIEW (trigger: cycle-start).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
# WHAT IS UNDER REVIEW ??D0, the unattended harness for a plain copy of the original tracking VI

Source of record: `docs/cycle27-plan.md` (status: current, cycle 27) ??"The three deliverables", D0 row, and
`## Pre-decided` items 1, 3, 4, 5. Content reference: `docs/cycle15-plan.md`. This file restates D0 so the
prior-art question is asked about exactly this build and nothing else.

## The deliverable

**D0 is a HARNESS. The VI is NOT modified.** The harness drives a plain, unmodified copy of the original
tracking VI (`Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi`) through stages 0?? with **nobody present**:

0. set the front-panel parameters (bead ROI size, bead-calibration parameters) **by VI Server**, not by clicking;
1. let the VI's device-configure stage run;
2. drive the **bead-picking while loop** by scripted GUI mouse clicks on the live image display ??
   first click = reference bead, every later click = a magnetic bead
   (approved GUI use: `tools/lv_gui.ps1 -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`,
   rule 1c');
3. press the **`Done Picking Beads?`** button (uid 11819) to end that loop and run bead-profile calibration;
4. type the **save path / file name**, let the **experiment loop** run N seconds, then **stop it through the VI's
   OWN stop control**;
5. verify the trace output file **exists and is non-empty**; close the VI; **repeat once** (a restart cycle).

Every step carries a prediction contract (expected counts / states / tolerances) checked in the log.

## How it is built and run

- ONE runner, ONE `bgrun`, ONE log ??planned recipe path: **`tools/recipes/build_d0_harness_v0.py`**.
- The copy it drives already exists:
  `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Track_D0_copy_20260918.vi`.
  Opening it needs the original preloaded read-only (`tools/bench/p2_open_copy.py` pattern).
- md5 of the original before AND after; the original is never opened for writing and never saved (rule 1).
- Unattended runs begin with `py tools/motor_gate.py --session start` (cycle27-plan Pre-decided 4); the
  controller limits (PI `TMN 0 / TMX 39` in RAM, ASI `SL/SU`) are the protection and are left ON at the end.
- Rig state is **議곕┰ / ASSEMBLED**; no motor is commanded by the harness itself, the camera is allowed,
  and there are **no beads on the rig** ??garbage tracking output is expected and is NOT a failure
  (user, 2026-09-17: "Bead媛 ?녿뒗 ?곹솴?먯꽌 ?몃옒???먮윭媛 遺꾨챸???앷린寃좎쑝?? ?붾컮?댁뒪 ?듭떊 諛??꾨젅??泥댄겕
  ?⑸룄濡쒕뒗 臾대━ ?놁쓣 ??).

## Why it is being built now

Three consecutive outcome reviews found **zero runnable experimental VIs** (latest
`archive/peer/2026-09-18-outcome-review-20260918.md`). The user's answer to the re-plan (2026-09-18 14:2x) was
**"D0, D1, D2 ?쒖꽌濡?吏꾪뻾?섎㈃ 醫뗭쓣??**, so D0 is the only work that closes that violation, and D1 (the seven-loop
restructuring inside the copy) does not start until D0's done-when is met.

## The prior-art question, precisely

Has THIS already been done here ??has a harness that drives the original (or a copy of it) unattended through
the pick stage into the experiment loop and back out through its own stop control already been built, attempted,
measured, decided against, or is it hand-rolling something `tools/`, `tools/gscript.py`, `tools/recipes/`,
`tools/lv_gui.ps1` or an existing claudeDev VI already provides? Name file and line for every finding.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??`archive/2026-09-18-status-cycle23-close.md` (latest) + the `archive/2026-09-1[678]-status-*.md` set.
??**USER ANSWER 2026-09-18 14:2x to the re-plan: "D0, D1, D2 ?쒖꽌濡?吏꾪뻾?섎㈃ 醫뗭쓣?? ??`docs/cycle27-plan.md`
(`status: current`, supersedes cycle21-plan). Option 1 as the session wrote it was WRONG (the original already has its
stop path and `save N xyz traces.vi`); the real first step is D0 = plain copy driven unattended by the harness.
??**P2 DONE 16:0x (user present) and the RUNNER RESTARTED on D0 (cycle27-plan Pre-decided 4 updated).** Live gate
test 10/10 (`tools/bench/motor_gate2_live.log`): PI 5 mm moved, **40 refused by the controller (ERR 7)**, ASI 짹0.2 mm,
HOME refused by the gate, release/re-arm verified; limits LEFT ON. ?좑툘 **That same log ends `BGRUN END rc=1` ??a
KNOWN FALSE RED, not a failure**: bgrun's failure scan fires on the controller's *expected* ERR 7 refusal
(`motor_gate2_live.log:280`; retrospective-cycle28 `VIOLATION: device-failed`, recorded as a FINDING ??no device,
user's 08:53 order). Do not re-diagnose it. STOP narrative ??`archive/2026-09-18-status-cycle26-stop.md`.

?쉾 **FIREFIGHTER CYCLE 24 SUCCEEDED (13:36-13:44, 38/38, rc=0)** ??block cleared, runner back to opus/max; it also
discharged both launch gates (`inference-over-measurement` no-device decision + the due outcome review).
## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:   # free since cycle-24 firefighter rerun (13:36-13:44): build_opfstunnelterm_v2.py RUN 1 = 38/38 gates PASS, BGRUN END rc=0 after 431s (tools/bench/build_opfstunnelterm_v2_run1.log). Both ops SAVED to claudeDev (OpFsTunnelTerm_v0.vi 19,869 B / OpFsInnerTunnelTerm_v0.vi 19,870 B), cold-legal (B5 both 1). Handles 30,363->30,592; all three md5s identical BEFORE AND AFTER (original C39F36E0..., V6 2A78E17C..., donor 5DC45A04...); no motor/serial/camera; one scratch created and deleted.
  prev_note:   # cycle-24/23 dispatch lines (incl. the 894/1356 panel-object finding) RELOCATED VERBATIM -> archive/2026-09-18-status-motor-gate-rework.md 짠3
  motor:     # 2026-09-18 15:37 MOTOR PORTS (no LabVIEW): tools/bench/motor_gate2_live.log, 8/10 gates, five transmits, ASI +-0.2 mm moved and returned, PI did not move (FRF 0 / ERR 5). Controller limits LEFT ON (PI TMN 0 / TMX 39, ASI SL/SU +-2 mm). Ports closed.
# CYCLE 23 lock lines + "where things stand" VERBATIM ??archive/2026-09-18-status-cycle23-close.md 짠1/짠2 (짠3 = dispatch 3's own facts). CYCLE 22 lock lines RELOCATED VERBATIM ??archive/2026-09-18-status-cycle22-close.md 짠1 (build_opfstunnelterm_v1 RUN 1 gates 12/16 B4 ExecState 0 쨌 diag_fstunnel_orphans 8/8 쨌 the `-Dual` review, both arms now DISPOSED 쨌 handles 30,318??0,979 쨌 md5s identical BEFORE AND AFTER 쨌 no motor/serial/camera); cycle-21 ???쫈ycle21-wire-semantics.md 짠8/짠9/짠9a, cycle-20 ???쫈ycle20-close.md.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py`
inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state
change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies
`tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies (user, 2026-09-18 15:2x, at
the rig; P1's "no motor port" clause is spent ??P2 ran live with the user present).** PI `SPA 1 0x15/0x30` ??TMN 0
/ TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never
SS Z**), both written+verified by `py tools/motor_gate.py --session start|end` from the user-editable
`tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json` **and** a fresh
readback (inside the transmit's own port open, before it) matching that file. The gate still refuses ?ㅽ뿕以?
every ASI home/zero/save and PI GOH/FRF/DFH/RON/POS/SPA/WPA, and all rotor motion; the script-side numeric
envelope and `motor_anchor.json` are DELETED (self-test `tools/bench/selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS, no PI motion) is SUPERSEDED by the 16:0x retest above ??verbatim ??
`archive/2026-09-18-status-cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent).
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??VERBATIM in `archive/2026-09-18-status-cycle22-close.md` 짠2 (cycle-20 짠1?벬? in `?쫈ycle20-close.md`; cycle-21 짠9/짠9a/짠10 in `?쫈ycle21-wire-semantics.md`; cycle 19 in `?쫈ycle19-flatseq.md`)
??**TUNNEL OPS BUILT + FUNCTIONALLY VERIFIED** (cycle-24 firefighter, 38/38, rc=0): `OpFsTunnelTerm_v0.vi` +
`OpFsInnerTunnelTerm_v0.vi` in claudeDev, cold-legal. **Do NOT re-run the recipe ??run 1 is the record**
(`tools/bench/build_opfstunnelterm_v2_run1.log`; paragraph ??`archive/2026-09-18-status-cycle26-stop.md` 짠1).
?뵶 **THE GAP stands: 174 ops, 123 recipes, 235+ peers ??ZERO runnable experimental VIs** ??third consecutive failing
outcome review (13:35, `archive/peer/2026-09-18-outcome-review-20260918.md`, annotated); the user's answer was
D0?묭1?묭2, so **D0 is the only thing that closes it** (OPEN 32).

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
32. ?뵶?뵶 **outcome review: seven `OUTCOME-VIOLATION`s (2026-09-18 13:35), THIRD consecutive ??the work stops for a re-plan with the USER.** Not answerable by a device. Stands above everything else here. **Cycle 26 acted on it: `STOP` planted (line 9), question + 4 options in `## NEXT`, full text `archive/prose/2026-09-18-replan-cycle26.md`.** Closed only by the user's answer.
38/39/41. ?뵶 D1 route-B run 3 changed NOTHING (63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0), `SR_QUEUE_AUTHORISED`/`TEMP_SINK_AUTHORISED` = False ??**`docs/d1-route-b-plan.md` 짠11/짠11a**, archive 짠3 쨌 `VI.Get Errors` 452 NOT built (prior-art stopped it, `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED) 쨌 **judgement only ??the stall watchdog's liveness test**, both arms ANSWERED and REFUSING "false positive", remedy not built (`archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`).
51. ??**CLOSED** (cycle-24 firefighter run 1, 38/38) ??verbatim in `archive/2026-09-18-status-motor-gate-rework.md` 짠4.
52. ??**CLOSED 16:26 ??`audit_cycle` cost-window clipping VERIFIED: `SELFTEST 7 pass / 0 fail`, `BGRUN END rc=0 after 0s`** (`tools/bench/selftest_audit_cost_window.log`, T1/T2/T2b/T3/T4/T5/T6; T6 on the real `cycle_12.log`: OLD 19 min 59 s / $13.7777 ??NEW 0 runs / $0.0000). `audit_cycle` **imports cleanly**, so its import-time `_self_test()` passes and `retrospective.py`/`guard_cycle` are unbroken. Cost numbers are quotable again. Code: `tools/audit_cycle.py:96-128` (`window_runs()`) + `:305-327`. Verbatim history ??`archive/2026-09-18-status-motor-gate-rework.md` 짠4.
52a. ??**CLOSED ??the material-marker deadlock is broken; `--material` is the ONLY form that runs** (env prefixes are auto-denied by the permission layer under `claude -p`). Verbatim ??`??cycle29-retro-trap.md` 짠7; live summary ??`??cycle28-marker-fix.md` 짠3.
53. ??**CLOSED 16:0x** (session-start repairs the reference after `SPA`: `RON 1 0` + `POS 1 <same value>`; retest 10/10; self-test 76/76) ??verbatim ??`??cycle29-retro-trap.md` 짠7. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. Dispositions: `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **`retro_done` is armed by an INTENTION, not by an answer** ??`guard_bash.py:226-227` marks the session closed from a **PreToolUse** hook the instant a `retrospective.py` command is typed (under bgrun the Bash call succeeds at launch), while the gate it mirrors, `guard_cycle.newest_retrospective()`, requires an **ANSWERED** archive. Nothing ever clears the mark; `{"dispatches":0,"retro_done":true}` sits in **3 of 17** session files. **Repair NAMED, deliberately NOT BUILT** (its self-test is a `tools/bench/*.py` run = a material dispatch, and an unverified hook patch is worse than the fault): `guard_session` should read `guard_cycle`'s own predicate. Review + full disposition: `archive/peer/2026-09-18-retro-closes-session.md`. ?좑툘 **My "over-trigger / gate deadlock" reading was REFUTED**: `retrospective.py:299` "END IS ALWAYS NOW", so the run labelled `--cycle 28` actually reviewed 14:07:40??6:37:22 ??cycle 29's OWN closing window. A cycle number is just a label; **the retrospective is the last thing a session runs** (now in `tools/cycle_prompt.md`). Cycle 29 lost its D0 to this ??and the error under the error (retrospective-cycle29's counterfactual): `guard_cycle` gates only RECIPE BUILDS, while cycle 29's actual first dispatch was a read-only MEASUREMENT it never guarded, so **the gate never needed clearing at all. A measurement dispatch never waits on a retrospective.**
42/43/46/47. **VERBATIM in `archive/2026-09-18-status-cycle20-open-items.md`** ??42 ?좑툘 39 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed 쨌 43 ??`guard_cycle.fixed_claim()` FIXED (step 1, T1?밫6 + B1/B2) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry; opus reads `device-failed`, threshold 1.** 쨌 48/48a/49/50 ??ALL FOUR CLOSED, verbatim in `archive/2026-09-18-status-cycle22-close.md` 짠3.

## NEXT
?뵶 **CYCLE 30 = D0, AND ITS FIRST ACT IS DISPATCH 1 BELOW ??NOT A RETROSPECTIVE** (cycle 29 ran one first and lost
every material dispatch for it; OPEN 54, warning now in `tools/cycle_prompt.md`). Nothing holds D0: the
retrospective is ANSWERED and annotated (`archive/peer/2026-09-18-retrospective-cycle28.md`),
`py tools/violations.py` reports **0 slugs awaiting a response**, and `guard_cycle` fed a D0 recipe name refuses
nothing. ?넅 **From a `claude -p` cycle, `peer.ps1` runs ONLY inside
`py tools/bgrun.py ??-- powershell -Command "& 'tools/peer.ps1' ??`** ??the two forms in hint 3 above are BOTH
refused and `-DryRun` is unreachable (measured; `archive/2026-09-18-status-cycle29-retro-trap.md` 짠4).

**Dispatch 1 ??the D0 PRIOR-ART REVIEW, before anything else.** `guard_cycle.premature_build()` refuses a recipe
with no prior-art review newer than itself; **no D0 recipe and no D0 prior-art review exist**, so this is the
longest pole and nothing blocks it (measured this cycle: `guard_cycle` fed `py tools/recipes/build_d0_harness_v0.py`
refuses nothing *yet*). Run it while dispatch 2 measures ??the two do not depend on each other.

**Dispatch 2 (material) ??D0 measurement.** No VI run, no motor, no camera; read-only COM with the original
preloaded read-only (`tools/bench/p2_open_copy.py` pattern), md5 the original before AND after:
(a) **decision D-A ??PUT THE WORKING FORM IN THE BRIEF ITSELF**, because the agent's own system prompt
(`.claude/agents/material.md:26-29`) still mandates the DEAD `MATERIAL=1` prefix and an agent trusting it burns the
dispatch: the form is `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>`.
Have it rewrite those lines too (cycle 29 could not ??its permission layer refuses writes under `.claude/`);
(b) inventory `claudeDev\Track_D0_copy_20260918.vi` for stages
0?? ??label, class, panel bounds, control-vs-indicator for the image display the picks land on, `Done Picking
Beads?` (uid 11819), the save path/name control(s), the experiment-loop stop control, the panel parameters D0 sets;
(c) what under `tools/` already opens the copy, drives GUI clicks, or runs-then-stops a VI; (d) where the trace
file is written and what builds its name.
**Then decide the driver and build it in ONE runner** ??`docs/cycle27-plan.md` Pre-decided 3 (D0 done-when),
4 (unattended run behind `py tools/motor_gate.py --session start`), 5 (read-only motor-limit check A on the same
copy). ?좑툘 After anything that runs the original's device init: re-read `TMX?` ??the axis came back `FRF?=0` between
15:08 and 15:37 and the 39 mm ceiling is RAM only. `STOP` (`tools/cycle_runner.py:54`) ??**only the user removes it**.

**Owed, NOT a gate on D0**: `doc_lint` **L6 FAILs ??47 archived reviews still blank/placeholder** (six from cycle 28's window, audit A4); L3 wants STATUS ??10 lines; L1/L2c/L7 warn only.
**Cycles 26/28 did this, do not redo it** ??`??cycle28-marker-fix.md` 짠1?벬?; cycle 29's replaced NEXT ??`??cycle29-retro-trap.md` 짠6.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — D0, the unattended harness for a plain copy of the original tracking VI

slug `d0-harness` · trigger `cycle-start` · recipe under review `tools/recipes/build_d0_harness_v0.py`
(read-only; no lock taken, nothing built, nothing run. `Write` is disabled for this session, so this answer is the whole product.)

## THE HEADLINE

**This harness exists, ran, and passed 16/16 on 2026-09-17.** `tools/bench/drive_original_copy_v3.py` (+ `_v2.py`, imported wholesale) drove a plain file copy through every clause of cycle27-plan's D0 done-when in ONE bgrun with ONE log and a per-step prediction contract, `BGRUN END rc=0 after 230s`. An active plan already records it as built: `docs/d1-build-plan.md:166`. What is genuinely new in D0 is a **four-item delta**, not a build.

---

## PART A — THE DIRECTION

### A1 SETTLED-ALREADY — the central question was answered YES and recorded as CLOSED

`archive/2026-09-17-status-cycle15-narrative.md:49-51`:

> 17. ✅ **D0 CLOSED — the original's full unattended cycle RAN, 16 pass / 0 fail** (`drive_original_copy_v3.py`, HWND-gated clickprobe, `SetControlValue` stop → idle in 2 s, `tra001-000` written, md5 unchanged).

Carried into an active document, `docs/d1-build-plan.md:166`:

> \| unattended drive of a copy through stages 0→4, run, stop, restart \| built, 16/16 \| `tools/bench/drive_original_copy_v3.py` \|

So "can a plain copy be driven with nobody present from panel-set through the pick clicks and the done button into the experiment loop and back out through its own stop control?" is not an open question. It was answered **yes**, on the same day the user approved the plan D0 is taken from.

**Covers:** the feasibility question and the decision that it was closed. **Does NOT cover:** the four deltas in §B1 — and it does not claim the outcome violation is answered: D0 was already CLOSED on 09-17 and the 09-18 outcome review still counted zero runnable experimental VIs (`STATUS.md:63`, `archive/peer/2026-09-18-outcome-review-20260918.md`). A second harness pass that only reproduces v3 will not move that number either.

### A2 REFUTED-ALREADY — no finding

Nothing in `archive/` argues against driving a copy unattended; rule 1c' mandates it, and option 2 (the `.cal`-loading substitute VI) is what was rejected. What was refuted is v1/v2's *mechanism* — that is B2, not A2.

### A3 CONTRADICTED — "no in-VI clamp is needed for D0" vs the motor plan's own conclusion

**Side 1, the plan under review** (`docs/cycle27-plan.md:37-47`, Pre-decided 4): controller-side limits are the protection, therefore *"Unattended D0 runs may therefore start the VI"*; and D0 sets the panel parameters **by VI Server**.

**Side 2, `docs/motor-limit-assurance-plan.md:131-134`**, written from the P2 live session:

> Consequence: a Data-Entry range coerces only values typed on the panel. Values written by **VI Server**, local variables or wires are NOT coerced — exactly how the unattended harness sets panel values. So §A.1 item 7 is confirmed as the real limit mechanism, and **pre-decided 2 (the fixed clamp in front of the motor subVIs) is mandatory, not optional**, for every VI we run unattended.

With `:125-130`: the original's magnet bound is *only* the `Trans Step (mm)` control's Data-Entry range (0…40.84), "nothing in front of `MOV`". The two active documents give different answers to "may an unattended run start this VI with no clamp inside it".

**Secondary, same class:** `STATUS.md:87` — *"no D0 recipe and no D0 prior-art review exist"* — against `docs/d1-build-plan.md:166` *"built, 16/16"*. The **recipe** half is literally true (nothing under `tools/recipes/` matches; the harness lives in `tools/bench/`), but that sentence is what sent this cycle to build D0 from scratch.

**Covers:** the claim that no in-VI clamp is required because "no motor is commanded by the harness itself", and STATUS's "nothing exists" framing. **Does NOT cover:** whether the controller limits are adequate — they measured working (`docs/motor-limit-assurance-plan.md:137-139`, `MOV 1 40` → ERR 7, no motion). This is a documentary contradiction, not a safety verdict.

### A4 UNREAD-EVIDENCE — the only successful run of this exact cycle is cited nowhere in the brief

The brief cites `tools/bench/p2_open_copy.py` for opening the copy and asks, as an open measurement, "what under `tools/` already opens the copy, drives GUI clicks, or runs-then-stops a VI". The answer is `drive_original_copy_v3.py` + `_v2.py` + `drive_original_copy_v3.log`, and two facts in it are missing from the D0 step list — each a stall for a harness written from the spec alone:

1. **Three `choose bandpass` subVI panels sit between the done button and the save dialog.** `drive_original_copy_v3.py:34-35` — *"R5 EXACTLY 3 `choose bandpass` panels, each CLOSED by a token-gated click"*; `drive_original_copy_v3.log:44-52` — 3 panels closed, distinct hwnds `[2295998, 2361534, 2427070]`, the save dialog appearing only after the third. D0's step 3 goes straight to step 4.
2. **`stop (end)` has no screen coordinate.** `drive_original_copy_v3.py:39-44` — *"no screen coordinate for `stop (end)` has ever been measured (the control sits outside the panel window's visible area at 1920x1080 …), so the GUI fallback is unavailable and the recorded fallback is COM Abort"*. Step 4's "stop through the VI's OWN stop control" is a VI-Server write with Abort as the only fallback — settled by measurement.
3. **The next D0 step is already written out:** `archive/2026-09-17-status-cycle15-narrative.md:52-55` + `archive/peer/2026-09-17-d0v3-stop-heuristic.md:32,:53-56` — stops `False` + readback while idle → restart → one `True` each → poll both control values and `ExecState`, no re-arm, no GUI.

---

## PART B — THE ARTIFACT

### B1 ALREADY-BUILT — every clause of Pre-decided 3 has a passing line in one log

`tools/bench/drive_original_copy_v3.log` (2026-09-17 02:45, `16 pass, 0 fail`, `BGRUN END rc=0 after 230s`):

| Pre-decided 3 clause | where it already ran |
|---|---|
| one runner, one bgrun, one log | `:1-2` |
| copies the original, md5 before AND after, original untouched | `:3` `2a78e17c…`, `:4`, `:230` same md5 |
| opens the copy (original preloaded read-only) | `:7-8` preload `ExecState=1`, `:9-12` `R1` |
| runs it | `:17,:20` Run on its own never-joined thread, `R2 ExecState=2` |
| pick stage by approved GUI clicks | `:21-27` three clicks inside the Image display, `R3 PASS` |
| presses the done button | `:29-30`, `:42` `R4 picking loop ended` |
| types the save path / file name | `:53-59` `^a` + absolute path + `{ENTER}`, `R6 PASS` |
| experiment loop runs N seconds | `:62-73` `R8 current image number 7232 … 8860` |
| stops through the VI's own stop control | `:75-80` `R9 SetControlValue — idle after 2s, 1 re-arms` |
| verifies the trace output, non-empty | `:81` `R10 … 'tra001-000 (196282 B)'` |
| closes, repeats once (restart) | `:83-126` `R11 restart + 15s + stop`, `:226` `closepanel` |
| prediction contract per step | `drive_original_copy_v3.py:29-51` (R1…R12, written before the run) |

**What this citation does NOT cover — the real D0 delta:**

1. **Target VI.** v3 copied `Min_Track N beads V6_ParallelLoop.vi`, md5 `2a78e17c…` (`drive_original_copy_v2.py:109-111`) — the **V6 working copy**, not `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (md5 `C39F36E0…`, `STATUS.md:34`), whose copy is `claudeDev\Track_D0_copy_20260918.vi` (`p2_open_copy.py:13-14`). Two consequences: the V6 copy carries the inserted per-frame TIFF writer (2041 files / 2.68 GB in ~22 s, `…v3.log:81`) that the 4.5 original does not, and every coordinate, uid and control name in v3 must be re-verified against the 4.5 copy's panel.
2. **Panel parameters by VI Server.** v3 writes only `stop (end)`, `stop (end) 2`, `Done Picking \nBeads?` (`…v3.log:13-16`). Bead ROI and calibration parameters are set by nothing — D0 step 0 is new work.
3. **R11's stop gate (STATUS OPEN 17b).** `archive/2026-09-17-status-cycle15-narrative.md:52-55`: `rec(…, left2, …)` at `drive_original_copy_v3.py:415-418` scored the *restart*, not the stop, and `reset_controls()` is called once (line 248, before run 1), so "stoppable by its own control after a restart" is **UNPROVEN**; cleanup needed Abort (`…v3.log:219`).
4. **The `motor_gate.py --session start` wrapper** and the `TMX?` / `W X` readback did not exist on 09-17.

### B2 ALREADY-FAILED — two prior attempts, with causes a from-scratch v0 re-inherits

- **Run 1** (`archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md:32,:100-106`): a **single** COM worker entered `vi.Run(False)`, which over ActiveX behaves as Wait-Until-Done=TRUE (`…v3.log:20`, "measured twice in v2"), so every later `set`/`abort`/`closepanel` sat in the **Python** queue and the harness printed its own sentence "LabVIEW is blocked" as an observation. Fixed in v2/v3 by a second COM apartment + never-joined RunThread.
- **Run 2** (`archive/2026-09-17-status-d0-and-gpu-narrative.md:157`: *"D0 v2 RAN … END rc=1 683 s, 18 pass/13 fail"*): P6 failed identically twice because the bandpass predicate was **title-based** and each closed panel was replaced by a successor with the identical title (`…v3.py:118-127`), and because `lv_gui.ps1 -Action click` reports success when its function returns (`…v3.py:11-13`, from `archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md:9,:23-24,:195`).
- **Load-bearing for D0, refuted there:** `SetControlValue` raises no Value Change event, so it cannot substitute for a click where the diagram waits on an event — only for polled controls (`…d0-com-blocked-in-picking-loop.md:117-120`).

### B3 HELPER-EXISTS

| plan step | existing call |
|---|---|
| clicks whose delivery must be *proved* | `tools/lv_gui.ps1 -Action clickprobe` (`:32`, `:732-733`; gated exactly like `click`, `:629-631`) |
| the whole D0 driver as a library | `import drive_original_copy_v2 as d0` — v3 does this and reuses `rec/log/getv/state/shot` (`…v3.py:67,:72`) |
| preload original read-only, then open the copy | `drive_original_copy_v2.py:205-215`; `p2_open_copy.py:25-31` |
| Run without blocking the command queue | never-joined RunThread, `…v3.log:17,:77` |

### B4 ALREADY-MEASURED

`…v3.log`: frame counter 7232 → 8860 over 20 s, `lost=32` (`:73`); own-control stop idles the VI in 2 s with one re-arm (`:80`); `tra001-000` 196,282 B (`:81`); cal file 171,552 B at the typed absolute path with `Cal File Path` agreeing (`:61`); md5 identical before/after (`:3`, `:230`); TIFF cost 2041 files / 2,675,689,770 B (`:81`). The trace writer's identity and route: `docs/main-vi-stop-and-save.md:29,:102-106,:123-125` (`save N xyz traces.vi` #6384, diagram 19, after the frame loop; its path inputs come off the loop's tunnels, i.e. from the path the harness types — no second dialog).

---

## FINDINGS WITH NO SLUG

- **The motor block is name-shaped.** `tools/hooks/guard_bash.py:114-117` refuses a command whose script is literally `drive_original_copy.py`; that regex cannot match `drive_original_copy_v3.py` or `build_d0_harness_v0.py`. Its own text (`:155-156`) says a VI that moves a motor internally "cannot be gated command-by-command — that one needs a judgement decision, not a flag", and `docs/motor-limit-assurance-plan.md:31` says the block stands "until C exists". So the only thing between an unattended D0 run and the original's internal device init is Pre-decided 4's flagged assumption, not the hook.
- **No prior D0 prior-art review exists** — `tools/bench/priorart_d0_harness.log:1` is this dispatch, and `archive/peer/*priorart*d0*` is empty. STATUS is right about that half.

## VERDICT LINES

PRIOR-ART: settled-already   (A1 — archive/2026-09-17-status-cycle15-narrative.md:49-51 + docs/d1-build-plan.md:166 — covers "can a plain copy be driven unattended through pick → experiment loop → own-control stop": answered YES and recorded CLOSED; does NOT cover the four §B1 deltas, nor any claim that the outcome violation is thereby answered)
PRIOR-ART: contradicted      (A3 — docs/cycle27-plan.md:37-47 vs docs/motor-limit-assurance-plan.md:125-134; and STATUS.md:87 vs docs/d1-build-plan.md:166 — covers "no in-VI clamp is needed because the harness commands no motor" and "nothing D0 exists"; does NOT claim the controller limits are inadequate, which measured as ERR 7 at 40 mm)
PRIOR-ART: unread-evidence   (A4 — tools/bench/drive_original_copy_v3.py:34-35,:39-44 + tools/bench/drive_original_copy_v3.log:44-52 + archive/peer/2026-09-17-d0v3-stop-heuristic.md:32,:53-56 — covers the D0 step list's omission of the three `choose bandpass` panels, of `stop (end)` having no screen coordinate, and of the already-specified VI-Server-only stop test; does NOT cover the panel inventory of the 4.5 copy, which is genuinely unmeasured)
PRIOR-ART: already-built     (B1 — tools/bench/drive_original_copy_v3.py:29-51 + tools/bench/drive_original_copy_v3.log:1-4,:7-12,:17-30,:42,:53-59,:73,:80,:81,:126,:230 + docs/d1-build-plan.md:166 — covers every clause of cycle27-plan Pre-decided 3 as already executed 16/0 rc=0 on a plain copy; does NOT cover the 4.5 retarget, panel parameters by VI Server, R11's stop gate, or the motor_gate session wrapper)
PRIOR-ART: already-failed    (B2 — archive/peer/2026-09-17-d0-com-blocked-in-picking-loop.md:32,:100-106,:117-120 + archive/2026-09-17-status-d0-and-gpu-narrative.md:157 + archive/peer/2026-09-17-d0-bandpass-click-not-delivered.md:9,:23-24,:195 + tools/bench/drive_original_copy_v3.py:11-13,:118-127 — covers a from-scratch driver that uses one COM worker for Run, a title-based panel predicate, or an unverified click; does NOT cover a driver that inherits v2/v3's second apartment, never-joined RunThread and hwnd token)
PRIOR-ART: helper-exists     (B3 — tools/lv_gui.ps1:32,:629-631,:732-733 + tools/bench/drive_original_copy_v3.py:67,:72 + tools/bench/drive_original_copy_v2.py:205-215 + tools/bench/p2_open_copy.py:25-31 — covers re-implementing click-with-proof, the driver scaffold, and preload-then-open; does NOT cover new code for panel parameters or the motor-gate wrapper)
PRIOR-ART: already-measured  (B4 — tools/bench/drive_original_copy_v3.log:3,:61,:73,:80,:81,:230 + docs/main-vi-stop-and-save.md:29,:102-106,:123-125 — covers frame-counter advance, own-control stop latency, trace/cal file existence and size, md5 invariance and TIFF cost ON THE V6 COPY; does NOT cover any of these on claudeDev\Track_D0_copy_20260918.vi, where none has been measured)

## How to release this review cheaply

All seven release on one delta list, as `FIXED:` lines under `## What was done with it`, once the D0 plan says in writing that the build **starts from `tools/bench/drive_original_copy_v3.py`** and adds only: (1) `ORIGINAL`/`COPY` retargeted to `Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` / `claudeDev\Track_D0_copy_20260918.vi` with that md5, panel coordinates and control names re-verified against it; (2) bead-ROI and calibration parameters written by VI Server before the run; (3) R11 gated on the stop, with the peer's VI-Server-only stop test as its body; (4) `motor_gate.py --session start` first and `TMX?` / `W X` read back after; (5) the three `choose bandpass` panels kept as an explicit contract step. A `REFUTED:` release is available for exactly one — B4 — if the plan shows the V6 numbers are claimed only as a method check and never as facts about the 4.5 copy.

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL, and the build it was reviewing was ABANDONED.** `tools/recipes/build_d0_harness_v0.py` was
never created and does not exist. The review's headline — the harness already exists as
`tools/bench/drive_original_copy_v3.py` (+ `_v2.py`), 16/16, and what D0 needs is a four-item delta — was taken
as correct, so the work became a chain of retargets that each import v2/v3 **wholesale** rather than
re-implementing anything:

| when | file | what it is |
|---|---|---|
| 2026-09-18 17:25 | `tools/bench/drive_original_copy_v4.py` | v3 retargeted to the 4.5 copy + the four deltas |
| 2026-09-18 17:45 | `tools/bench/diag_d0_pickloop_liveness.py` | the discriminating measurement after v4's R4 failed |
| 2026-09-18 18:1x | `tools/bench/drive_original_copy_v5.py` | v4 + every click point LOCATED on this VI's own panel |

One `FIXED:` line per verdict slug (each path exists and was last changed AFTER this review's 17:06 timestamp):

FIXED: settled-already - tools/bench/drive_original_copy_v4.py:9 - the driver's own header states the delta ("NEW: the 4.5 retarget, the read-only PANEL PARAMETER RECORD, the explicit three-`choose bandpass` contract step, the VI-SERVER-ONLY stop test, the `motor_gate.py --session start` wrapper") instead of re-answering the settled feasibility question, exactly as A1 asked.
FIXED: contradicted - tools/bench/drive_original_copy_v5.py:5 - the STATUS.md:87 half ("no D0 recipe exists", the sentence that sent the cycle to build from scratch) is answered by building nothing new: v5 opens with "REUSED WHOLESALE, by import, exactly as v4 did" and no `tools/recipes/build_d0_harness_v0.py` was ever written. ⚠️ The OTHER half of A3 — `docs/cycle27-plan.md` Pre-decided 4 vs `docs/motor-limit-assurance-plan.md:125-134` on whether an unattended run needs an in-VI clamp because VI-Server writes are not coerced by a Data-Entry range — is NOT fixed here and is a judgement item, not a material one.
FIXED: unread-evidence - tools/bench/drive_original_copy_v4.py:48 - all three unread facts became contract steps: "DELTA 3 - THE THREE `choose bandpass` PANELS ARE AN EXPLICIT CONTRACT STEP" (:48-54) and "DELTA 4 - STOP IS VI-SERVER ONLY … `stop (end)` uid 7 has NO screen coordinate" (:55-64), the latter carrying the peer's own VI-Server-only stop test verbatim.
FIXED: already-built - tools/bench/drive_original_copy_v5.py:112 - `import drive_original_copy_v4 as d4` (which is itself `import drive_original_copy_v2 as d0`, `drive_original_copy_v4.py:129`): the already-built driver is imported as a library, so not one clause of Pre-decided 3 was re-implemented.
FIXED: already-failed - tools/bench/drive_original_copy_v5.py:183 - `probe_click()` routes EVERY click through `lv_gui.ps1 -Action clickprobe` and records the four delivery checks, and the bandpass panels are tracked by HWND token (`d4.gated_click_hwnd`), never by title - so B2's three named causes (one COM worker inside Run, a title-based panel predicate, an unverified click) are each structurally excluded rather than re-inherited.
FIXED: helper-exists - tools/bench/drive_original_copy_v5.py:113 - the only thing hand-rolled is the one helper the toolkit genuinely lacks, `tools/bench/d0_locate.py` (screenshot-based location of a red-captioned LabVIEW button and of the IMAQ display); its docstring records the prior-art check that `uitars_grounder.py`, `lv_gui.ps1 -Action crop` and `docs/toolkit-capabilities.md` offer nothing equivalent. Everything else - clickprobe, the driver scaffold, preload-then-open - is imported.
FIXED: already-measured - tools/bench/drive_original_copy_v5.py:59 - the V6 numbers are quoted only as provenance and are explicitly not clicked ("Those numbers are the REFERENCE PATCH's provenance and the expectation; they are NOT clicked"); every figure D0 relies on is re-measured on `Track_D0_copy_20260918.vi` itself and logged (`tools/bench/drive_original_copy_v4.log`, `…v5.log`).

**The review's most valuable finding was the one it did not have a slug for.** B1 delta 1 — "every coordinate,
uid and control name in v3 must be re-verified against the 4.5 copy's panel" — was written down and then NOT
done in v4, which reused v3's derived points and clicked (1114,915) for a button that sits at (1177,862) on this
copy. That cost a failed run and a hypothesis review
(`archive/peer/2026-09-18-d0v4-picking-loop-frozen.md`). v5 is the repair: `tools/bench/d0_locate.py` locates
every click point in a screenshot taken in the run itself.
