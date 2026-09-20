# master-plan-attack

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-16
- **outcome:** ANSWERED (263s)
- **why asked:** to attack `docs/pre-rig-master-plan.md` before any of it is built — specifically its central claim
  that the "needs the rig" category splits into beads / motors+serial / camera, which is what moved live
  acquisition acceptance out of the deferred pile.
- **verdict:** unverified

## Question

ATTACK THIS PLAN. It is a master plan for restructuring a LabVIEW magnetic-tweezers tracking VI into seven
parallel loops, covering everything the team believes it can do BEFORE the physical rig is reassembled. The plan is
`docs/pre-rig-master-plan.md` in this project directory; read it, and read the files it cites.

Your job is to find where it is WRONG, not to summarise it. Specifically:

1. **The central claim to attack: the dependency split.** The plan asserts three separate physical dependencies ??   "needs beads in a mounted flow channel" (blocked), "needs motors/serial" (available now, window closes at
   reassembly), "needs the camera" (available now, no beads required). It uses this to move live camera
   acquisition acceptance (track C3) out of the deferred pile. **Is that split real?** Name anything in C1-C6 or
   E1-E5 that silently needs a mounted sample, a flow cell, fluid, a magnetic field, or a bead ??and anything in
   track F that does NOT need one and is therefore deferred for no reason.

2. **Track A6 is new and load-bearing.** The user states that ASI focus correction is issued by SOFTWARE when the
   image goes off focus, and that they have never adjusted it by hand during an experiment. Our own file
   `docs/camera-acquisition-facts.md` had inferred the opposite from the fact that the subVI's `+Inc`/`-Inc`/
   `Focus inc` inputs are control references. The plan now says "find every writer of those control references and
   the off-focus criterion". **Is that search well posed?** What would it miss ??a path that writes focus without
   touching those terminals, an autofocus living in another VI or in the ASI controller's own firmware, a
   hardware joystick path? How would you tell "no writer exists in this VI" from "we did not look in the right
   place"?

3. **Ordering.** The plan claims track C outranks track D because C's window closes. Attack that: what does
   starting hardware measurement before the map (track A) is finished cost, and is there a cheaper ordering?

4. **Acceptance.** E1 demands all 10,043 fixture frames bit-identical, where today only the first 10,018 (those
   before the first bead loss) pass. Is bit-identity through a reseed path even the right criterion, given the
   reseed is a re-initialisation rather than a continuation?

5. **What is missing entirely.** Name work that must happen before reassembly and appears in no track.

Context you must respect as given, not re-litigate: the original VI is never modified (work happens in a copy);
the per-bead maths must not change (scheduling may); the camera free-runs and nothing may gate its acquisition;
the ASI piezo stage must never be driven; and the buffer number, not a software timestamp, is the time axis.

State your strongest reason the dependency split in (1) is wrong, give an alternative explanation for why this work
was previously deferred, say what observation would falsify your objection, and name the cheapest test that
discriminates.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. Strongest reason the dependency claim is wrong

The assertion that ?쏿cquisition performance does not depend on what is in the image??is false for the present configuration. `ExposureAuto` is **Continuous**, and its permitted maximum is 15 ms?봫ore than twice the 6.67 ms period required at 150 Hz. A darker optical path, including a mounted flow cell, different illumination, or an obstructed field, can therefore change exposure and reduce the achievable camera cadence. This exact caveat is already recorded in [camera-acquisition-facts.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/camera-acquisition-facts.md:39>). JAI describes this camera?셲 automatic exposure as adapting to dynamic lighting conditions on its [official SP-5000M-USB page](https://www.jai.com/products/sp-5000m-usb).

Thus:

- A **driver-only** C3 benchmark needs no beads.
- A representative claim that the experimental optical path sustains 150 Hz may need the mounted optical configuration?봮r exposure must first be locked/bounded.
- E2, ?쐃very loop running,??is not merely a camera test. The tracking loop requires valid initial bead coordinates, calibration clusters, good flags, and reseed state, as shown in [stage2-plan.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-plan.md:17>). Blank live images can drive it immediately into bead-loss/reseed behavior rather than the normal tracking state.

A better explanation for the prior deferral is therefore: **the test was deferred because it was framed as system-level live acceptance, whose initialization, optical stimulus, tracking state, and autofocus behavior require a representative experiment?봭ot because the camera device itself requires beads.**

### Dependency audit

- **C1:** No sample needed, but the proposed measurement is not implementable as cited. C1 promises a real `WHERE`-length transaction; `serial_roundtrip_asi.ps1` sends only `/` and explicitly excludes `WHERE`. The recorded `/` result is a five-byte exchange, while the stated `WHERE` latency remains an extrapolation ([camera-acquisition-facts.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/camera-acquisition-facts.md:110>)).
- **C2:** No sample is intrinsically needed, but it cannot precede A7 because the relevant per-frame call sites are not yet fully identified.
- **C3:** Raw acquisition needs no beads, but it is sensitive to exposure/illumination configuration. Integrated acquisition-plus-tracking additionally needs a valid initialized tracking state.
- **C4:** No sample needed?봟ut it is not new work. The real camera was already swept with `Last` and `Next`; 74.9 versus 123.0 Hz was measured, not merely calculated ([camera-acquisition-facts.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/camera-acquisition-facts.md:64>)). Repeat only if the LabVIEW call path, rather than the camera/API behavior, is the intended subject.
- **C5/E3:** Command identity needs no sample. Physical completion timing measured with a disassembled/unloaded mechanism may not represent the reassembled mechanical load, so the plan must distinguish ?쐁ommand issue time??from ?쐌otion completed time.??- **C6:** This silently needs a usable focus signal?봟eads or another suitable optical target?봞nd likely cannot be ?쏿ctually firing??while also guaranteeing no ASI motion. The existing map already places an ASI `Move Axis Relative` call inside case #10407 ([diagram-hierarchy.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/diagram-hierarchy.md:43>)).
- **E1/E4:** Properly fixture-only.
- **E2:** Needs either a representative sample or an explicit hybrid test mode that injects fixture tracking inputs while exercising live acquisition.
- **E5:** Queue/acquisition back-pressure can be tested without beads using a synthetic consumer. A claim about normal tracking, autofocus, reseed, and file behavior cannot.

Track F also bundles deferrable and non-deferrable work:

- The **physical** real-bead-loss observation must wait, but live-path reseed transport, queue ordering, stop behavior, and counter behavior can be exercised now through deterministic fault injection.
- Physical force/extension measurement waits, but `Magnet2Force`, WLC, smoothing, data merging, and file-format behavior can be fixture-tested now.
- Most pilot mechanics?봲tartup, controlled stop, error propagation, partial-file handling, and UI workflow?봠an receive a dry-run before the supervised physical pilot.

## 2. A6 is not well posed

?쏤ind every writer of those control references??starts from the wrong sinks.

`+Inc`, `-Inc`, and `Focus Step` are control-reference constants passed into two instances of `ASI_adjust focus-subvi.vi`; the existing main-VI census found no local or implicit `Value` writer for them ([main-vi-panel-map.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/main-vi-panel-map.md:538>)). That does not prove autofocus is absent. It means the references may be read inside the callee.

The search would miss:

- A computed autofocus path using the separate `Auto-Focus`, `Focus Deviation from the Center`, `Focus Pos`, `min value`, or image inputs rather than emulating the three manual buttons.
- The already-known case #10407 path that reaches `Move Axis Relative` directly.
- A different VI that writes a target position or sends VISA without touching those controls.
- Dynamically loaded VIs or Call-by-Reference paths. NI documents that VIs can be configured for dynamic loading rather than ordinary static calls ([NI dynamic-call documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019NMCSA2&l=en-US)).
- Writes through aliases, references carried in clusters/variants, globals/shared variables, or `Value(Signaling)`.
- Controller-resident autofocus. This is not evidence that this rig has CRISP, but ASI?셲 Tiger command set does support controller-level `CRISP`/`TRACKING` autofocus functions, so firmware configuration must be excluded rather than assumed absent ([ASI Tiger documentation](https://docs.asiimaging.com/products/tiger)).
- The hardware joystick, which bypasses LabVIEW by the user?셲 own account.

NI?셲 caller search only establishes project references/callers; it is not a proof that every possible runtime source was inspected ([NI Find Callers documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MyPSAU)). Likewise, a local-variable census only covers front-panel objects in that VI; NI explicitly defines locals as belonging to a single VI ([NI local-variable documentation](https://www.ni.com/docs/en-US/bundle/labview/page/local-variables.html)).

A6 should instead be:

1. Enumerate every terminal hardware sink: ASI VISA Write, `Move Axis Relative`, and any target-position command.
2. Walk backward from each sink to its selector/criterion.
3. Separately enumerate all writers of every autofocus-related state object?봭ot only the three button controls.
4. Inventory static and dynamic callers and the controller?셲 configured autofocus modes.
5. With the ASI physically disconnected, instrument the command boundary and capture call chain, command bytes, and trigger state when software reports a correction.

Only failure of all five searches would support ?쐍o software writer exists.??
## 3. Ordering is too coarse

?쏞 outranks D because C?셲 window closes??is not a valid track-level rule. Some C items are prerequisites, some are already measured, and some cannot yield meaningful results until A or D exists.

Starting too early costs:

- Measuring `/` while claiming `WHERE`.
- Repeating the already-completed C4 camera comparison.
- Measuring blank-scene acquisition under uncontrolled auto-exposure.
- Moving motors before the scheduler?셲 exact command/timing contract is mapped.
- Trying C6 without knowing the trigger or without a safe command-boundary probe.

A cheaper ordering is:

1. Freeze the camera configuration contract, especially exposure mode/max, ROI, binning, and frame rate.
2. Finish only the A work needed to name hardware sinks and their exact commands: A3/A4/A6/A7.
3. Run standalone, low-risk hardware characterization whose command is already known.
4. Build D1?셲 telemetry-capable vertical slice.
5. Run integrated C3/E2 against that slice.
6. Run C5 only after D4 defines the command trace being compared; run C6 only with the stage disconnected and the command boundary instrumented.

Hardware scarcity should prioritize **irreproducible observations**, not every item carrying a C label.

## 4. E1 uses a necessary criterion as if it were sufficient

Reinitialization does not make bit identity inappropriate. Given identical frames, identical initializers, and the accepted deterministic current-frame rule, the restructured path should reproduce the original recorded result stream exactly. The fixture already establishes that the 13 loss triggers and the original `min(pos)<0` trigger coincide on this recording ([stage2-assembly-step-e.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-e.md:152>)).

The defect is that E1 treats one bit-identical trajectory as complete reseed acceptance. The fixture does not exercise:

- Periodic auto-reset; the cited document explicitly says it never fired.
- Manual `Reset Tracking`.
- `Auto-Reset` disabled.
- Reaching `Limit of Program`, including stop-and-save.
- Loss while acquisition has skipped buffers or the result queue is backlogged.
- Consecutive losses before a successful recovery.
- Correct reseed-event counts and state on both sides of the transition.

Retain 10,043-frame bit identity, but add an event oracle: for each injected scenario, compare `reseed?`, reset counter, state fed into the next kernel call, raw result saved for the current frame, buffer number, and terminal stop/save behavior.

## 5. Missing entirely

Before reassembly, the plan still needs:

- A frozen camera configuration and bright/dark exposure acceptance envelope.
- A startup/shutdown side-effect audit. The original startup contains motor initialization and focus-setting paths, so ?쏿ll loops running??is unsafe until startup is explicitly separated from normal operation ([main-vi-startup.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/main-vi-startup.md:24>)).
- Fault-injection tests for camera timeout/disconnect, VISA timeout, queue full, disk slow/full, writer failure, and stop during each blocked state.
- Buffer-number reset/wrap/reopen semantics and an acceptance rule distinguishing intentional `Last` gaps from corruption.
- A corrected C3 metric: with `Last`, the same buffer can be returned repeatedly; NI distinguishes `Last New` specifically because it suppresses duplicate frames ([NI explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000001DwvoCAC&l=en-US)). Therefore `Images Missed = 0` is not sufficient; the authoritative trace must be `Buffer Number Out`, including duplicates and gaps.
- Explicit construction and integrated acceptance of both experimental products. Track D describes one seven-loop restructuring, while E4 merely benchmarks ?쏞PU-parallel??and ?쏥PU?? it does not require a GPU seven-loop top-level VI with the same startup, stop, writer, scheduler, and hardware behavior.

## Falsifier

My dependency objection would be falsified by a two-condition measurement showing that, with the exact production camera configuration, changing from the current empty optical scene to the mounted-channel optical scene leaves exposure below 6.67 ms, preserves contiguous 150 Hz buffer numbers, and does not change acquisition-call tail latency?봶hile the complete VI remains in its normal tracking state rather than immediately entering reseed.

## Cheapest discriminating test

With no motors or ASI involved, run the existing camera reader at 150 Hz under `ExposureAuto=Continuous`, log `ExposureTime`, `Buffer Number Out`, duplicates/gaps, p99.9/max call latency, and then alternate the illumination between the present bright field and a deliberately dimmed field for 10??0 seconds each. If exposure rises past one frame period or buffer cadence changes, the plan?셲 ?쐇mage content does not affect acquisition??premise is false; if exposure stays bounded and the buffer trace is invariant, that specific objection is falsified.

## Sources

(extract from answer)

## What was done with it

**The central objection is SUSTAINED, and its evidence is our own measured file.** Four load-bearing claims were
checked against the sources rather than accepted, 2026-09-16:

| claim | verified? | what the source actually says |
|---|---|---|
| **auto-exposure breaks "image content does not affect acquisition"** | ✅ **sustained** | `docs/camera-acquisition-facts.md:39` — *"`ExposureAuto` is **Continuous**… auto-exposure raises it when the field dims and the achievable rate falls with it. A rate target is only safe with exposure bounded — `AutoShutterControlExposureMax` is currently 15 000 µs, which alone would cap the camera near **66 Hz**."* A disassembled rig **is** a dim field. C3 as written could have "measured" that 150 Hz is unreachable and blamed the software |
| **C4 is not new work** | ✅ **sustained** | `:60-70` carries a real sweep table (`Next` processed vs `Last` processed, per injected delay, at 150/200/90 Hz). It was **measured on this camera**, not modelled. The plan called it "modelled, not measured" — that was wrong |
| **C1 is not implementable with the cited tool** | ✅ **sustained** | `tools/bench/serial_roundtrip_asi.ps1:50` is `$SAFE = @('/')`, and its own comment at :46 lists *"Deliberately NOT whitelisted even though they are read-only: `WHERE`/`W`…"*. The script REFUSES a command absent from the whitelist, and the whitelist may only grow from an archived external confirmation. C1 needs that confirmation first, not "scoping" |
| **A6 starts from the wrong sinks** | ✅ **sustained** | `docs/main-vi-panel-map.md:538` records a measured census: **21 `ControlReferenceConstant` nodes, every one feeding a subVI's reference input**. The references are read **inside the callee**, so a hunt for `Value` writers in the main VI returns nothing and proves nothing — exactly the "did not look in the right place" failure the reviewer names |

**Accepted without separate verification** (consistent with files already read, and none drives an expensive step
on its own): `Images Missed = 0` is insufficient under `Last` because the same buffer can repeat, so the
authoritative trace is `Buffer Number Out` including duplicates and gaps; E2 is not a camera test because blank
live images drive the tracker straight into bead-loss/reseed; startup contains motor-initialisation and
focus-setting paths (`main-vi-startup.md:24`) so "all loops running" is unsafe until startup is separated; E1 is a
necessary but not sufficient reseed criterion and needs an event oracle (periodic auto-reset, manual reset,
auto-reset disabled, `Limit of Program` stop-and-save, loss during skipped buffers, consecutive losses); track F
bundles genuinely-deferred physical observations with work that can be fault-injected or fixture-tested now; and
the plan builds **one** seven-loop top level while the decided deliverable is **two** (CPU and GPU).

**Not yet accepted, flagged for the user:** the reviewer's alternative ordering subordinates the hardware window to
finishing the map. That is a direct trade against the user's stated priority, so it is presented as a decision
rather than adopted.

`docs/pre-rig-master-plan.md` is being rewritten against this. No part of it was executed — the review landed
before anything ran, which is what it is for.
