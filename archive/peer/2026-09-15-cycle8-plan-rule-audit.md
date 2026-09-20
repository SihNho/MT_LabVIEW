# cycle8-plan-rule-audit

- **agent:** claude
- **model:** sonnet (peer.ps1 default)
- **kind:** review
- **date:** 2026-09-15
- **outcome:** ANSWERED (244s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

THE PLAN (attack it; it will drive the next several cycles and I have been wrong three times today on adjacent
readings, each time by quoting a summary without reading the section that qualified it).

GOAL, set by the user today: acceptance is the requirement in project-requirements/parallelization-requirement.md
in FULL - camera acquisition, tracking, motor reading, the scheduler and data merging/saving each running in its own
parallel loop. The main VI today has three While loops: diagram 20 (motor control), diagram 43 (the frame loop,
which holds everything else), diagram 99 (display/UI). The target is the seven-loop architecture in
docs/restructure-plan-4.6.md section 3.

METHOD: do the restructuring INSIDE A COPY of the original VI (rule 1: the original is never modified), so bead
picking, calibration, the controls and the experiment workflow survive rather than being rebuilt.

OVERLOAD POLICY, decided by the user today: acquisition -> tracking is LOSSY and LATEST-WINS (pool exhausted =>
abandon the oldest unprocessed frame, reuse its slot, never block acquisition), while tracking -> file writer stays
LOSSLESS and FIFO, and every result carries its frame number so gaps are explicit. The user's reason was the rigor
of the time series: a result computed from a stale frame is a sample attached to the wrong moment.

WORK QUEUE, all of it possible with the rig DISASSEMBLED (reassembly costs the user 2+ hours of sample prep, so
every rig-bound measurement is deferred and batched into one later session):
 1. OpOwnerChain_v0 - a reader taking a UID and returning its owner UID and class. Donor: the existing
    OpWireSource_v5 with its Wire cast removed. The semantics are already MEASURED and recorded at docs/NAMES.md
    line 823: a node's Generic.Owner is its frame Diagram, and that Diagram's Owner is the structure.
 2. The full diagram hierarchy for all 170 diagrams -> docs/diagram-hierarchy.md plus JSON.
    tools/bench/diagram_tree_main.json already has each diagram's owner CLASS and node uid list, but NO parent
    link, so nobody knows what is nested inside what.
 3. Which loop encloses the 11 PI motor / rotor call sites (MOV.vi x7 on diagrams 3,36,40,69,121,125,129; VEL.vi x4
    on 5,69,91,129; POS?/TMN?/TMX?/GOH on 5,91; Magnet2Force on 42,74). The requirement calls motor READING a
    frame-rate bottleneck, and I have not established which loop those sites are in.
 4. Census of Case #10445's frames, and the frame loop's TRUE membership - my earlier "6 subVIs in the frame loop"
    counted only diagram 43's body, not its 10 nested Case structures, 4 For loops and 1 Event structure.
 5. The unconditional per-frame path: what executes every iteration versus conditionally.
 6. Fixture timing: instrument a copy, replay all 10,043 recorded frames, report p50 AND p99 per stage.
 7. One vertical slice: acquisition -> owned image handoff -> queue core -> frame-identified result, including stop,
    error, reseed and overload. Reseed is testable on the fixture's 13 real lost-bead frames.

WHAT IS ALREADY BUILT AND VERIFIED: Track_v6_CPU_queue_v0.vi runs all 10,043 fixture frames in 7.5 s with the first
10,018 (those before the first bead loss) bit-identical to the reference; it is a replay artefact with FOR loops and
no live acquisition. A fleet of ~168 scripting op VIs exists.
YOUR SPECIFIC JOB (you are this project's rule and consistency auditor, not the framing adversary): check this plan
against CLAUDE.md and against what the project's own files actually say. Quote the file and line you rely on.
 - Rule 1: is "work inside a copy" genuinely safe, and does any step risk touching or re-saving an original?
 - Rule 1a: the overload policy changes behaviour under overflow. Is calling that "not a computation change"
   defensible, given the original's own get buff image-lost frames.vi? Where else does this plan quietly change the
   original's computation?
 - Rule 1b and the hardware rules: does anything in steps 1-7 touch the ASI piezo, the motor, or the camera?
 - The GUI gate: does any step need a GUI action, and is it enumerated?
 - The verification-level rule (structural vs functional): does every step state which level it is accepted at, and
   does any step claim functional acceptance from a structural check?
 - Contradictions: does this plan contradict anything currently written in STATUS.md, docs/restructure-plan-4.6.md,
   docs/stage2-plan.md or docs/NAMES.md? Name the file and line.

--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

claude.exe : Permission deny rule (.claude\settings.json): Write(**/*.vi) is not matched by file permission checks ??on
ly Edit(path) rules are. Use Edit(**/*.vi) instead (Edit rules cover all file-editing tools).
위치 줄:5 문자:36
+     Get-Content $promptFile -Raw | & $exe @exeArgs 2>&1 | Out-String
+                                    ~~~~~~~~~~~~~~~~~~~~
    + CategoryInfo          : NotSpecified: (Permission deny...editing tools).:String) [], RemoteException
    + FullyQualifiedErrorId : NativeCommandError
 
Permission deny rule (.claude\settings.json): Write(**/*.ctl) is not matched by file permission checks ??only Edit(path
) rules are. Use Edit(**/*.ctl) instead (Edit rules cover all file-editing tools).
Permission deny rule (.claude\settings.json): Write(**/*.lvlib) is not matched by file permission checks ??only Edit(pa
th) rules are. Use Edit(**/*.lvlib) instead (Edit rules cover all file-editing tools).
Permission deny rule (.claude\settings.json): Write(**/*.lvproj) is not matched by file permission checks ??only Edit(p
ath) rules are. Use Edit(**/*.lvproj) instead (Edit rules cover all file-editing tools).
**The plan does not hold as currently worded ??step 7 schedules building/testing an overload mechanism that this project's own prior peer review already found broken, and the fix was never incorporated.**

### 1. Strongest reason the plan is wrong

The plan restates STATUS.md's OVERLOAD POLICY verbatim ("latest-wins... abandon the oldest unprocessed frame, reuse its slot") and schedules step 7 to build/test it. But **three of this project's own design documents still specify the opposite mechanism**, unrevised:

| doc | mechanism |
|---|---|
| `docs/frame-ownership-design.md:77` ??"if no free slot is available, acquisition **drops the new frame** and counts it" | drop-new |
| `docs/restructure-plan-4.6.md:386` ??"the acquisition loop **drops the new frame and counts it**" | drop-new |
| `docs/stage2-plan.md:47-48` ??`Q_img` timeout 0 ??"counted as dropped **by the tracker**" | drop-new |
| `STATUS.md:161` / this plan ??"abandon the **oldest unprocessed** frame, reuse its slot" | drop-old / evict |

STATUS.md:166 documents a revision to `restructure-plan-4.6.md`'s transport table, but only on the "lossless vs. order-preserving" label ??it never touches this mechanism conflict, so it *looks* settled but isn't.

**This exact conflict is already peer-reviewed and on file, unresolved.** `archive/peer/2026-09-15-cycle8-plan-attack.md` (dispatched against essentially this same plan, one cycle earlier) answered: *"The overload-policy change invalidated `frame-ownership-design.md`... Reusing the oldest queued slot is a different state machine... Step 7 says 'including overload,' but overload is now an architectural redesign, not merely another test case... The latest-wins decision silently superseded the already-reviewed free/work-queue ownership protocol."* It named a candidate primitive (`Lossy Enqueue Element.vi`) and a candidate ownership fix (an extra FILLING slot, generation numbers/sentinels against stale reuse) ??**none of which appear in `docs/toolkit-capabilities.md`, `docs/NAMES.md`, or `docs/stage2-*.md`**. Nobody has checked whether the fleet can even build drop-old semantics.

The rule-1a defense at STATUS.md:167-169 ("not a rule-1a break, the original already loses frames") only covers *whether* loss may happen ??it doesn't cover *which frame* gets discarded, and an unsafe evict-oldest design risks something worse than the original ever did: a result silently computed from the **wrong frame's pixels** (stale slot reuse), not just a missing one. The fixture's bit-identical result ??the plan's headline evidence ??is silent on this, since STATUS.md:169 itself admits "on the fixture there is no overflow."

### 2. Alternative explanation

STATUS.md's wording may be a **policy statement** (no stale frame is ever saved), not a **mechanism mandate**. The existing drop-new design guarantees the same outcome by refusing new arrivals instead of evicting old ones, and with a shallow pool (N=8 at 150 Hz ??53 ms backlog) the two may be **numerically indistinguishable**. If so this is a wording slip in STATUS.md, not a real design fork.

### 3. What would falsify which reading

A forced-overload synthetic test where drop-new and drop-old discard the *same* frame in practice (pool drains fast enough that oldest-queued ??newest-arriving) falsifies "real conflict" and downgrades this to a wording fix. Any stale-slot reuse, duplicate/lost slot return, or frame-number/pixel mismatch confirms the cycle-8 review's reading.

### 4. Cheapest discriminating test

Exactly what the cycle-8 review already specified (`archive/peer/2026-09-15-cycle8-plan-attack.md:166`), no rig needed: a synthetic image-pool test, slow consumer, unique frame IDs embedded in both descriptor and pixel buffer, enough production to force hundreds of evictions/refusals ??run once under literal drop-new, once under literal drop-old, diff the ID-accounting logs. This also settles whether `Lossy Enqueue Element.vi` is even reachable from this fleet (not currently in `OpQueue_v0`'s donor list).

**I don't believe the plan holds as worded for step 7** until either the ownership-protocol redesign the cycle-8 review demanded is written and reviewed, or the test above shows the two mechanisms are equivalent at this pool depth (in which case keep the existing drop-new design and just fix STATUS.md's wording).

---

**Secondary findings (not blocking):**
- **A.** `OpOwnerChain_v0` (work-queue item 1) is donor-evidenced only for owner chains *inside a Case frame* (`docs/NAMES.md:823`), but item 2 plans to use it across all 170 diagrams' full nesting (While/For/Event/Sequence too) ??untested generalization, and `restructure-plan-4.6.md:277-279` already flags a related gap (7 `SequenceLocal`s with `uid 0`). Test against one node under each structure type before running it project-wide.
- **B.** Rule 1 / 1b / 1c / GUI gate: **clean**. All 7 steps are read-only reads of the original or work on an explicit copy; none imply GUI; none touch the ASI piezo, motor, or live camera (fixture replay only).
- **C.** The work-queue table states each item's *dependency* but not its *acceptance level* (structural vs. functional), which the verification-level rule requires. Step 7 in particular conflates a genuinely-functional reseed test with an overload claim that can't be functionally verified on the fixture as scoped ??split its acceptance line before dispatch.



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
