# priorart-d1-routeb-run5

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7737  in 42 / out 28505 / cache-create 267431 / cache-read 2773111  (418s, 32 turn(s))
- **date:** 2026-09-18 23:28:40
- **outcome:** ANSWERED (420s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: direction-change).

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
# D1 route-B ??RUN 5, the recipe `tools/recipes/build_d1_routeb_v2.py`

?좑툘 WHY A NEW FILE NAME. `build_d1_routeb_v1.py` carries a standing prior-art stop record released for its
hash 9ff90ded8f01; by design (`docs/cycle18-plan.md` Pre-decided 2) a changed hash means UNREVIEWED, and
`tools/stop_record.py` then refuses EVERY command naming it ??including the command that would review it. So
v1 was restored byte-for-byte to its released hash (the launch gate itself verified this by allowing the copy
command) and the four changes were applied to a byte copy, `build_d1_routeb_v2.py`, which is what this review
is about. Nothing else differs between the two files.


Run 4 (`tools/bench/build_d1_routeb_v1_run4.log`) ended 80 PASS / 1 FAIL and then crashed with LabVIEW
`error 2` (memory full) inside `settle_index_modes()`. Run 5 changes FOUR things and nothing else. All four
were decided by the cycle-36 judgement session after the mandatory failed-prediction review
(`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md`, claude/hypothesis opus-max, ANSWERED).

1. `TEMP_SINK_AUTHORISED = False -> True` (recipe `:285`-ish), authorising the TEMPORARY-SINK branch for the
   **`Z/dZ` row only**. The branch is already coded at `:1257-1278` and uses ONLY already-built ops:
   `OpCreateEqual_v0` -> `wire_control` -> `OpConnectFromWire_v0` -> `delete_object` +
   `remove_bad_wires_scripted`. No new op, no new device. `SR_QUEUE_AUTHORISED` stays `False` permanently.
   Grounds: the alternative (cycle15 Pre-decided 3's REORDER) has NO by-index route ??`ControlTerminal #403`'s
   node index on `Diagram[56]` is `None` (`build_d1_routeb_v1_run4.log:163-164`) ??and the review measured that
   the S3 node moves cut `w730`, not the `#403` reparent.
2. `fact(labview_handles())` inserted immediately BEFORE the `g.count(TARGET, "LoopTunnel")` call that raised
   `error 2`, because no handle reading brackets it and the SAME call succeeded at 51,284 handles at S1
   (`build_d1_routeb_v1_run4.log:26-27`).
3. The `done/failed/noroute` ledger print MOVED ABOVE `settle_index_modes()`, plus a counts `fact()`. Run 4
   lost all 66 `s3w` ledger rows because the print sat after the call that raised.
4. The `finally:` block RENAMES the working copy aside (`..._crash_<HHMMSS>.vi`) on the EXCEPTION path only;
   the normal path still deletes it. `s0()` removes any earlier `_crash_` copy so they cannot accumulate.

Unchanged: rule 1 (the original is copied, md5 gated before and after), the cold/preloaded `ExecState`
protocol (Pre-decided 14a/16), the SINK RULE, every gate, and the build order of `docs/d1-route-b-plan.md`.

QUESTION FOR THE PRIOR-ART REVIEW: has any of these four changes ??the temporary-sink `Z/dZ` route in
particular ??already been built, measured, refuted or settled in this project's own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??`archive/2026-09-18-status-cycle34-n1.md` (latest) + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?럦 **D0 IS DELIVERED** (cycle 31) 쨌 **N1 IS ACCEPTED** (cycle 34) **??D1 is open.** Banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.
## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released   # ?넅 **D1 ROUTE-B v1 RUN 4 RAN, cycle-36 MATERIAL, 2026-09-18 22:13??2:42** ??`tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`, **80 PASS / 1 FAIL** + a crash. **S1 BASELINE ExecState = 0 read COLD ??UNREAD** (`:25`); the S3w ledger was NEVER produced and S5 never ran, because `s3w ??settle_index_modes ??g.count(LoopTunnel)` raised **`error 2` (memory full)** at `:353`. ??Pre-decided 13 rows 1+2 HELD: both shift registers were created MOVED WITH THEIR NODES (`#26032` for `#1359`, `#26082` for `#29874`, `:315-316`; neither carries the original's `Initialize Array` initial value ??reported, not silently changed). ?뵶 Row 3 FAILED ??**the ONLY FAIL line**, `:164`. ??**`preload_reread()` FIRED BEFORE THE DELETE (Pre-decided 14) and the LIVE working copy read `ExecState 1` PRELOADED** (`:337`) against the cold baseline 0 ??so the cold gate is again shown to be reading linkage. Original md5 `2a78e17c449cacdaf5da389818526859` **UNCHANGED before and after** (`:4`, `:340`); working copy deleted. Handles 0 ??51,284 (copy open) ??30,682 (post-restart) ??49,062. ?좑툘 The error-2 instance was killed and a fresh LabVIEW 26.3.1f1 is up (`tools/lv_restart.py`). Prior text: cycle-35 dispatches 3+4 (read-only) finished 20:17 / 20:25, LabVIEW left killed, originals' md5 unchanged. MEASURED on BOTH originals: a byte-identical claudeDev copy reads **ExecState 0 COLD / 1 with the ORIGINAL preloaded read-only** ??the linkage artefact belongs to the READING INSTANCE, not the file (`tools/bench/diag_d0_execstate_preload.log` 9/0 rc=0; `tools/bench/diag_d1_execstate_preload.log` 7/0 rc=0). Prose VERBATIM (md5s, handle counts, per-dispatch detail) ??`archive/2026-09-18-status-cycle36-relocate.md` 짠1.
  owner:
  since:
  purpose_now:   # ??**N1 IS ACCEPTED (cycle-34 judgement) ??D1 IS UNBLOCKED**: pre-bead-loss window k<10018 = ZERO exceedances over 50,201 valid bead-frames (max |dx| 4.857e-07 / |dy| 4.677e-07 / |dz| 1.279e-05 vs tol 1e-6 x,y and ~1e-4 z); the VI-level run reproduces the DLL numbers exactly, so the LabVIEW wrapper is numerically transparent (`tools/bench/n1_gpuk_vi_fixture.log`, 7/7, rc=0). ?좑툘 TWO items FLAGGED TO THE USER, NOT closed: (a) acceptance is on the PRE-BEAD-LOSS WINDOW, not the whole fixture; (b) the single z-LUT index flip at k1679/bead 4 (dz -4.667e-03, above the z tolerance) excluded by the FLIP mask. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; record ??`archive/2026-09-18-status-cycle34-n1.md` 짠1/짠4.
  purpose_relocated:   # cycle-35/36 lock prose ??`archive/2026-09-18-status-cycle36-relocate.md` 짠1/짠2. cycle-34/32/30 ??`archive/2026-09-18-status-cycle34-n1.md` 짠1 쨌 23 ???쫈ycle23-close.md 짠1/짠2/짠3 쨌 22 ???쫈ycle22-close.md 짠1 쨌 21 ???쫈ycle21-wire-semantics.md 짠8/짠9/짠9a 쨌 20 ???쫈ycle20-close.md.
  motor:     # limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed; an 18:13 D0 run then moved the magnet to 30 mm and they held. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; detail ??`archive/2026-09-18-status-cycle34-n1.md` 짠1.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py`
inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state
change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies
`tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525,
Y ??.7744?╈닋0.7744 (persistent, **never SS Z**), written+verified by `py tools/motor_gate.py --session start|end`
from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json`
**and** a fresh matching readback. The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI
GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS) is SUPERSEDED by the 16:0x retest ??`??cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent); **an 18:13 D0 run then moved the magnet to 30 mm and they held**.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1 (lock block above). **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Earlier: `archive/2026-09-18-status-cycle22-close.md` 짠2 쨌 `?쫈ycle20-close.md` 짠1?벬? 쨌 `?쫈ycle21-wire-semantics.md` 짠9/짠9a/짠10 쨌 `?쫈ycle19-flatseq.md`.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
??**CLOSED ??all five VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md`**: **32** D0 delivered 18:13, 짠5 (?좑툘 the next outcome review judges whether it answers "zero runnable VIs" ??do NOT close it unilaterally) 쨌 **55** `tmx_from` rule 4 deleted, 17/0, 짠6 쨌 **56** `audit_cycle` C7 repointed at the `status: current` plan, 짠7 (?좑툘 **STILL OPEN from retrospective-cycle31 F4: C4 understates spend** ??judgement `claude -p` sessions carry no COST line) 쨌 **51/52/52a** 짠8 쨌 **53's mechanical half** (16:0x, retest 10/10, self-test 76/76) 짠9.
38/39/41. ?윞 **DECIDED cycle 35 ??the flags are no longer an open question: both stay False PERMANENTLY** (Pre-decided 13), and the 3 NO-ROUTE rows follow `docs/cycle15-plan.md` Pre-decided 1/2/3. Run 3 was 63 WIRED / 0 FAILED / 3 NO-ROUTE at ExecState 0, but that ExecState was read **cold and therefore measures subVI linkage** (Pre-decided 14a/16, two independent controls); it was equally **over-determined** by the skipped `s1q`/S4b, so run 3 is neither exonerated nor convicted until the baseline read lands ??**`docs/d1-route-b-plan.md` 짠11/짠11a**, archive 짠3 쨌 `VI.Get Errors` 452 NOT built (prior-art stopped it, `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED) 쨌 **judgement only ??the stall watchdog's liveness test**, both arms ANSWERED and REFUSING "false positive", remedy not built (`archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`).
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **`retro_done` is armed by an INTENTION, not by an answer** ??`guard_bash.py:226-227` marks the session closed the instant a `retrospective.py` command is typed, while the gate it mirrors, `guard_cycle.newest_retrospective()`, requires an **ANSWERED** archive; nothing ever clears the mark (`{"dispatches":0,"retro_done":true}` in **3 of 17** session files). **Repair NAMED, deliberately NOT BUILT**: `guard_session` should read `guard_cycle`'s own predicate. ?좑툘 The "over-trigger / gate deadlock" reading was REFUTED ??`retrospective.py:299` "END IS ALWAYS NOW"; **the retrospective is the LAST thing a session runs**, and a measurement dispatch never waits on one. ?넅 THE SAME TRAP WITH A DIFFERENT MOUTH ??**a `claude -p` session CANNOT "take results as they arrive"**: cycle 33 ended its turn on two backgrounded hypothesis peers, both paid opus/max cells were killed at 600 s with no `COST:` line, cycle 33 closed with no retrospective, and cycle 34 spent $5.88 re-asking. **THE RULE: dispatch in the FOREGROUND and wait ??and when something must run in the background, HOLD THE TURN OPEN until it lands.** An orphan detector is deliberately NOT built (Pre-decided 2). VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠10; reviews `archive/peer/2026-09-18-retro-closes-session.md` + `archive/peer/2026-09-18-retrospective-cycle34.md`.
42/43/46/47. **VERBATIM in `archive/2026-09-18-status-cycle20-open-items.md`** ??42 ?좑툘 39 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed 쨌 43 ??`guard_cycle.fixed_claim()` FIXED (step 1, T1?밫6 + B1/B2) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry; opus reads `device-failed`, threshold 1.** 쨌 48/48a/49/50 ??ALL FOUR CLOSED, verbatim in `archive/2026-09-18-status-cycle22-close.md` 짠3.

## NEXT
?뵶 **USER, 2026-09-18 21:3x (after watching the D0 copy run its experiment loop live ??"?곷떦??怨좊Т?곸씤??吏湲덉? 萸?
?섍퀬?덈뒗嫄곗엫?"): TWO CYCLES SINCE D0 HAVE NOT TOUCHED D1. The next cycle's FIRST ACT is a D1 BUILD dispatch
(`docs/cycle27-plan.md` Pre-decided 1/6; route B per `docs/d1-route-b-plan.md`, ExecState read WITH the original
preloaded ??Pre-decided 14a/16). NO machinery repairs, NO watchdog reviews, NO audit fixes, NO doc relocation
before that dispatch has RUN; those go AFTER the D1 dispatch returns, or into the retrospective as findings. A
cycle that ends without a D1 build log is a wrong-ordering cycle by definition.**
?뵷 **FIRST ACT OF THE NEXT SESSION ??RUN 5, one material dispatch, one runner, one log.** Everything it needs is
decided; nothing below is a question. Patch `tools/recipes/build_d1_routeb_v1.py` with the FOUR changes judgement
answered this cycle (the ??block under run 4): (1) `TEMP_SINK_AUTHORISED = True` at `:285` ??`Z/dZ` row only;
(2) `fact(labview_handles())` immediately before `:1170`; (3) move the ledger print `:1529` **above**
`settle_index_modes()` `:1517`; (4) `finally:` `:1793-1795` renames the copy aside on the **exception** path only.
Then run `py tools/bgrun.py --material --max-min 40 --log tools/bench/build_d1_routeb_v1_run5.log -- py -u
tools/recipes/build_d1_routeb_v1.py`. **What run 5 must return**: the S3w ledger (it survives the crash now), the
handle count bracketing `settle_index_modes()`, the `Z/dZ` discriminator at `:1288-1290`/`:1306`, and the S5/S6
`ExecState` with the preloaded re-read. A prior-art review is owed on the patched recipe before it launches
(`tools/stop_record.py` gates it) ??run it in the SAME dispatch, do not make it a separate cycle.
?좑툘 The retrospective is the **LAST** thing a session runs (OPEN 54); `peer.ps1` runs ONLY inside
`py tools/bgrun.py ??-- powershell -Command "& 'tools/peer.ps1' ??`. N1's acceptance and its two caveats are in the
lock block; do not re-derive them.

??**Cycle-35 dispatches 1 + 2, VERBATIM in `archive/2026-09-18-status-cycle36-d1-run4.md` 짠5.** In one line each:
`Count` is CONTROL uid 28051 written by the event structure, **never a bead count** (Pre-decided 15,
`docs/NAMES.md` 짠`Count`); and D1's two authorisation flags stay **False permanently** (Pre-decided 13), the three
NO-ROUTE rows being decided by `docs/cycle15-plan.md` Pre-decided 1/2/3. ?좑툘 **Run 4 measured that the `Z/dZ` half
of that disposition cannot be executed as written** ??the registers half held.

?뵶 **D1 ROUTE-B v1 RUN 4 IS THE CYCLE-36 BUILD LOG** ??`tools/bench/build_d1_routeb_v1_run4.log`, 80 PASS / 1 FAIL
then `error 2` (memory full) inside `settle_index_modes`. **The ONE open construction question**: `Z/dZ` ??`#2222`
t0 has **no by-index route** ??`ControlTerminal #403`'s node index on `Diagram[56]` is `None`, and
`OpConnectNested_v1` addresses `Diagram[].Nodes[].Terminals[]` (`?쫞un4.log:163-164`, MEASURED not inferred), so
cycle15 Pre-decided 3's REORDER cannot be executed as written. Every other fact of the run (baseline UNREAD 0,
preloaded live copy **1**, both shift registers moved with their nodes, md5 unchanged, handles) is VERBATIM in
**`archive/2026-09-18-status-cycle36-d1-run4.md` 짠4**.
?뵶 **THE MANDATORY FAILED-PREDICTION REVIEW LANDED AND REFUTED BOTH OF THOSE CLAIMS** ??`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md` (claude/hypothesis opus-max, ANSWERED 566 s, $3.9657, `tools/bench/peer_routeb_run4.log`). (1) The SAME `count(LoopTunnel)` call **succeeded at 51,284 handles** at S1 (`?쫞un4.log:26-27`), so the handle count is the control, not the cause; no reading brackets the failing call, and the **66 `s3w` rows that ran before the crash lost their whole ledger** because the print (`build_d1_routeb_v1.py:1529`) sits AFTER `settle_index_modes()` (`:1517`). (2) The `Z/dZ` route **is already coded in the recipe** at `:1257-1278` from built ops only and was skipped solely because `TEMP_SINK_AUTHORISED = False` (`:285`); and the **node moves at `s3():617-631` cut w730, not the `#403` reparent**. ??**ALL FOUR ANSWERED ??cycle-36 judgement. Apply without re-asking.** **(a)** The review is **ACCEPTED IN FULL**: both refutations are read off our own log lines, not asserted. **(b) Pre-decided 13 is REVISED FOR ROW 3 ONLY.** `SR_QUEUE_AUTHORISED` stays **False permanently** ??rows 1+2 did exactly what it decided, so its grounds are now *confirmed*, not merely assumed. `TEMP_SINK_AUTHORISED` becomes **True for the `Z/dZ` row, as the discriminating test**, because the premise of its refusal is measured false twice over: the REORDER has no by-index route (`?쫞un4.log:163`) and it was aimed at the wrong cut (the moves at `s3():617-631` cut w730, not the `#403` reparent). The temp-sink path uses only ALREADY-BUILT ops (`OpCreateEqual_v0` ??`wire_control` ??`OpConnectFromWire_v0` ??delete + `remove_bad_wires_scripted`), so this authorises **no new op and no new device** ??Pre-decided 2 is untouched. Read the discriminator the recipe already prints at `:1288-1290`/`:1306`. **(c) YES to both instrumentation lines**: `fact(labview_handles())` immediately before `:1170`, and move the `done/failed/noroute` ledger print (`:1529`) **ABOVE** `settle_index_modes()` (`:1517`) ??a run that loses 66 rows of ledger to an exception is the whole argument. **(d) YES, SCOPED**: on the **exception** path `finally:` (`:1793-1795`) **renames the copy aside** instead of deleting it ??Pre-decided 14's "measure before you delete" means nothing if a crash erases the state first; the normal path still deletes, and the renamed copy is removed by the next run.

??**STEP 0 WAS DONE IN CYCLE 36 ??do NOT redo it** (the earlier "none done in cycle 36" line was wrong; the user's 21:3x order arrived *after* STEP 0 had run). Both repairs green (`tools/bench/repair_c36_selftest.log`, 5/0): `lv_stallcheck.ps1` identity-bound to `(pid, CreationDate)` + skips leaves with no bgrun log; `bgrun.py` sets `BGRUN_LOG`. F1?밊4 RUN ??F1 not evaluable, **F2/F3/F4 False**, so the cycle-35 stall record is a measured false positive that repair (i) would NOT have prevented. `bgrun.py` now has the `try/finally` its docstring always promised: green record **`tools/bench/c36_close_runner.log:13-14`** (8/0) ???좑툘 do NOT cite `selftest_bgrun_final_line.log`, whose last line is `BGRUN END rc=1`. `wait_logs.py`'s cp949 crash-on-success fixed (its flag is `--seconds`, not `--timeout-min`). ?좑툘 **(e) is NOT closed and the class is narrower**: `wait_runner_exit` was never a failure; the other three were **external kills**, which no in-process handler reaches (test T1, `archive/peer/2026-09-18-c36-bgrun-finalline-selftest.md`).
?뱦 **Still owed, no gate**: ~57,800-handle reading 쨌 `doc_lint` L6/A4 (47 blank dispositions) 쨌 D0 짠4 pre-read before the first D1 click 쨌 **`doc_ingest.py --full --model opus` has NEVER run, overdue** 쨌 ?좑툘 **THIS FILE IS ~138 LINES again** (my own NEXT rewrite put it back over; relocate the run-4 and retrospective detail into `archive/2026-09-18-status-cycle36-d1-run4.md`, which already exists) 쨌 `doc_ingest`'s stale `STATUS.md:10` citations at `CLAUDE.md:352-353` and `docs/violation-decisions.md:333-336` ??cite the user's 08:53 order **by DATE**, never by a STATUS line number, which every relocation moves (done already in `violation-decisions.md:392-393`).
?좑툘 `.claude/agents/material.md:26-29` still mandates the DEAD `MATERIAL=1` prefix, so **every material brief must
carry** `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>`.
??**STEP 1 IS DONE AND RAN** ??the baseline `ExecState` read is in the v1 recipe and fired (`?쫞un4.log:25`);
짠2 of the archive keeps the original block.

??**RETROSPECTIVE-CYCLE36 IS IN AND BOTH ITS VIOLATIONS ARE DISPOSED** ??`archive/peer/2026-09-18-retrospective-cycle36.md`
(fable/medium, ANSWERED 424 s, $4.4824, `tools/bench/retro_c36.log`). `VIOLATION: wrong-ordering | loss_min=41 |
loss_usd=2.7466` and `VIOLATION: device-failed | loss_min=0` (threshold **1**) ??both answered `DECISION: no-device`
in `docs/violation-decisions.md` at 23:09, so **`py tools/violations.py --due` is SILENT and `guard_cycle` will not
block run 5.** Three findings carried forward, none a gate: (i) a fresh stall record fired **during run 4**
(`tools/bench/stall_pid11424_221324.log:1`) and was discharged only incidentally, because `peer_routeb_run4` happens
to be newer ??do not rely on that next time; (ii) ?뵶 **`audit_cycle`'s C3/C5 cost figures are PHANTOM** ??649 of the
758 claimed minutes are impossible inside a 143-minute window, so **quote no cost number from this cycle's audit
until that is measured**; (iii) the bad `selftest_bgrun_final_line.log` citation, fixed above.

### FOR THE USER ??calls to overturn if you disagree
1. ?봽 **I REVERSED HALF OF MY OWN "off permanently" CALL, on measurement.** Cycle 35 said both route-B flags stay
   False for good. Run 4 confirmed the shift-register half exactly as decided, so `SR_QUEUE_AUTHORISED` stays off
   for good. But the `Z/dZ` half rested on a "reorder the wire" plan that the machine has now refuted twice ??it
   has no by-index route, and it was aimed at the wrong cut. So `TEMP_SINK_AUTHORISED` goes **True for that one
   row, as a test**. It builds nothing new: the path is already written and uses only ops we built weeks ago.
   Say so if you would rather `Z/dZ` stayed unwired than see that flag on.
1a. ?넅 **Two more rule-1a calls I made rather than stopping the cycle for:** moving the six structures with
   `GObject.Move` is **scheduling, not computation** (a move carries its frames intact, measured 171??71), so it is
   allowed; and **N1 does NOT by itself carry the 18 R1 rows** ??it compared the GPU kernel to the CPU one, not the
   assembled D1 VI, so a D1-level numeric fixture run is still required before D1 is accepted.
1b. ?좑툘 **The two shift registers that moved carry NO initial value**, while the original's are fed by
   `Initialize Array` (`#8953` w9051 / `#28124` w29122). That may be a real computation change. It applies to all
   ten registers together, not these two, so I did not wire two of ten ??it must be settled for the whole set
   before D1 is accepted.
2. ?넅 **A sub-session created `tools/wait_logs.py` and I kept it.** Under `claude -p` a material session had NO
   permitted way to wait for its own background job ??the `until grep ??sleep` loop its own agent file mandates
   AND the Monitor tool are both refused by the allow list ??which is exactly the hole that killed two paid peer
   cells in cycle 33, and which I hit myself this cycle. I judged it plumbing, not one of the process "?μ튂" you
   told me to stop building. Say if you want it gone, or the allow list widened instead.
3. **Unchanged from cycle 34, still yours to overturn:** the harness RECORDS all 60 front-panel controls and SETS
   none (inventing values would be a rule-1a computation change); the VI moved the PI magnet 0 ??30.000 mm under
   its own control inside 0??9 with `TMX?=39` / `TMN?=0` holding; and I accepted the GPU kernel on the
   **pre-bead-loss window** ??over the whole fixture max |dy| is 3.135e-05, 31횞 your 1e-6, but all 19 exceedances
   are bead 4 at k??0023, after that bead's own first loss at k=10018, the other four clean at identical k; plus
   **1 bead-frame of 50,215** where CPU and GPU sit on adjacent z-lookup indices (k1679, dz ??.667e-03), excluded
   by the FLIP mask. Say so if any of it is too loose.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete. Verdict: **not novel — six findings, one of which is load-bearing** (change 1 cannot execute as written).

---

# PRIOR-ART REVIEW — `tools/recipes/build_d1_routeb_v2.py` (D1 route-B RUN 5)

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — the answer on file is still "no", and no binding document was amended

The question "may the temporary sink be used for the `Z/dZ` row?" was decided twice, and **both decisions are still the live text**:

- `docs/cycle27-plan.md:99-100` — *"the judgement session declines, and the answer is 'no', not 'not yet'. `SR_QUEUE_AUTHORISED` and `TEMP_SINK_AUTHORISED` stay `False`; **a build that needs either to be True is the wrong build**."* (Pre-decided 13, cycle 35)
- `docs/d1-route-b-plan.md:572-576` — *"**The temporary is DISARMED PERMANENTLY** (`TEMP_SINK_AUTHORISED = False`, Pre-decided 13 … only the judgement session could turn it on and it has declined)"*

The cycle-36 judgement did reverse half of this (`STATUS.md:110-115`), but **it reversed it only in STATUS**. Neither Pre-decided 13 nor §11a was edited, and `docs/cycle27-plan.md:87-88` (Pre-decided 12) says Pre-decided lines are edited by judgement sessions and *"a material session that believes one is stale reports it and stops."* So run 5 launches into a plan that forbids it, and the first material session to read §11a will stop.

Sharper: the v1 stop record was **released by the edit that wrote that sentence** — `tools/bench/stop_records.json:71` pays with `FIXED: settled-already - docs/d1-route-b-plan.md:475 - §9/§11/§11a now cite cycle27-plan Pre-decided 13 instead of reserving the questions`. v2 now contradicts the document whose amendment released v1.

*What this citation covers:* only that the binding documents were never amended. It does not say the cycle-36 decision was wrong. Cheap release: a judgement session records the revision in `cycle27-plan.md:89-100` and `d1-route-b-plan.md:563-576`, then cites those lines.

### A2 REFUTED ALREADY — the flag's stated grounds were refuted a day before run 4, and the real hazard is a different one

`archive/peer/2026-09-17-zdz-wirecut-opus.md:136` (ANSWERED, `-Dual`, accepted in full at `:160-184`) already demolished the citation both the recipe and the plan still repeat:

> *"`docs/NAMES.md:468` is the heading "OpBuildCase_v0 … SUPERSEDED by v1"; `:473-475` is about `SetControlValue` on that op's `Selector` refnum control … Worse, the row you cite as support says the opposite: `docs/toolkit-capabilities.md:52` describes `OpCreateEqual_v0` as "both operands are fetched INSIDE the op, so no terminal refnum crosses COM (**the fix for `docs/NAMES.md:473-475`**…)". You cited the fix as evidence of the defect it fixes."*

That text is **still verbatim in the file under review** at `build_d1_routeb_v2.py:305-308` and in the runtime refusal message at `:1297-1300`.

But the same paragraph (`:138`) replaces it with a hazard that is still open: `src_names=()` → `Names=[]` / `Names 2=[]` (`tools/recipes/build_opsentinel_ops.py:397,:400`) → `Get Outputs` empty → `Index Array[0]` returns **a default refnum with no error** → an invalid refnum reaches `Create Equal.vi`'s `x`/`y` from *inside*. *"Whether `Create Equal.vi` guards it … is not recorded anywhere in this project."*

So the plan's *"uses ONLY already-built ops … no new op, no new device"* is true of the op **inventory** and false of the **call shape**. `OpCreateEqual_v0`'s `FUNCTIONAL 23/0` (`docs/toolkit-capabilities.md:64`) was measured with both operand names supplied — its documented signature is `Names=[x source terminal]` / `Names 2=[y source terminal]`. The recipe's own docstring says so: `build_d1_routeb_v2.py:960-962` — *"calling it with an EMPTY name list is unmeasured."*

*What this covers:* the risk framing, not the decision. Running the test is defensible — but as `archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md:242` says, the interesting outcome is *"`OpCreateEqual_v0` cannot place a source-less `Equal?` — the one genuinely unmeasured step"*, and the plan should predict it rather than assert built-ness.

### A3 CONTRADICTED — **change 1 cannot reach the temporary-sink branch. Flipping the flag changes nothing.**

This is the finding that matters. The plan (and `…run4-error2-and-zdz.md:205`, `:239`, `:252`) states the branch *"did not run solely because `TEMP_SINK_AUTHORISED = False` (`:285`)"*. **The code has a guard above it that returns first.**

In `from_ctl_unnamed` there are two `not zw` branches, in this order:

| lines (v2 / v1) | branch | guard |
|---|---|---|
| `v2:1267-1295` / `v1:1222-1250` | the **v1/B2 RETRY** (`OpConnectNested_v1`, by index) | `not zw and (sink_uid,sink_t)==ZDZ_SINK and PREWIRED[ZDZ_SINK]["ct"]` |
| `v2:1296-1301` / `v1:1251-1256` | the `TEMP_SINK_AUTHORISED` refusal | `not zw and not TEMP_SINK_AUTHORISED` |
| `v2:1302-1326` / `v1:1257-1278` | **the temporary sink itself** | `not zw` |

`PREWIRED[ZDZ_SINK]["ct"]` is always set: `build_d1_routeb_v2.py:720` — `PREWIRED[ZDZ_SINK] = dict(before_reparent=zdz_wire, ct=zdz_ct)` — and run 4 resolved `zdz_ct = #403` (`tools/bench/build_d1_routeb_v1_run4.log:15`, `:162`). So whenever the sink is bare, the RETRY branch runs. Inside it, `n_src = node_index_on(bi, ct_uid)` (`v2:1271`) is **the same `Diagram[].Nodes[]` lookup that is measured to return `None` for a ControlTerminal**, so `:1274` appends `noroute` and `return False` at `:1278` — line `:1296` is never evaluated.

And if `zw` is non-zero, neither branch runs at all. **In every reachable state, `TEMP_SINK_AUTHORISED = True` is inert.** Run 5 would spend the LabVIEW lock and hand back the same NO-ROUTE row, with the discriminator at `:1288-1290`/`:1306` never printed.

Second contradiction, same family: the plan asserts what run 4 *"did not run … solely because"* — but run 4 cannot show that. Both branches append silently (`v2:1275-1278`, `:1297-1300`; no `print`), and the ledger was lost to the crash (`STATUS.md:89`, `…run4.log:348-353`). The claim is an inference from code that reads the other way.

*Required extra edit (not in the four):* the RETRY must **fall through** to the temp sink when `n_src is None` (record the NO-ROUTE reason as a `fact`, don't `return False`), or the RETRY's guard must add `and node_index_on(bi, ct_uid) is not None`. *What this citation does not cover:* whether the temp sink then works — that is precisely what run 5 should measure, once it is reachable.

### A3b CONTRADICTED (artefact hygiene) — run 5 overwrites run 4's own JSON record

`build_d1_routeb_v2.py:243` keeps `OUT = …/build_d1_routeb_v1.json`, and `:1869-1870` writes it inside `finally:` on **every** path including the crash path. `tools/bench/build_d1_routeb_v1.json` is on disk now. Change 4 exists because *"the state that crashed is gone; (a)/(b)/(c) can no longer be separated on existing evidence at any price"* (`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md:188`) and because Pre-decided 14 requires measuring before deleting (`docs/cycle27-plan.md:101-104`). Preserving the `.vi` while overwriting the `.json` of the run being diagnosed is self-defeating. `:1874`'s summary line also still prints `build_d1_routeb_v1`, which will mislabel the run-5 log under a gate keyed to path + hash.

### A4 UNREAD EVIDENCE — `archive/peer/2026-09-17-zdz-wirecut-{opus,codex}.md`

The plan cites exactly one exchange (`…-routeb-run4-error2-and-zdz.md`). The **`-Dual` exchange devoted to this single row**, whose conclusions were accepted in full and written back at `…zdz-wirecut-opus.md:160-184`, is not mentioned — and it contains (i) the refutation of the 1055 citation, (ii) the real hazard mechanism, (iii) the no-new-op alternative (B3 below), and (iv) `:130`, which already recorded — with external sources — that `Diagram.Nodes[]` cannot list a ControlTerminal. Reading it is also the cheapest route to A3: it is the document that already framed this row as an *ordering* question rather than a structural one (`:100`).

---

## PART B — THE ARTIFACT

### B4 ALREADY MEASURED — the RETRY branch re-asks a question answered on 2026-09-14

Run 4's single FAIL (`…run4.log:162-164`, *"MEASURED, not inferred"*) re-measured something already written in three places before it:

- `docs/d1-route-b-plan.md:239` — *"`Z/dZ` uid 47, a `ControlTerminal`, which `Diagram.Nodes[]` does not list (**R3**)"*
- `docs/main-vi-startup.md:64-66` — *"a front-panel object's diagram terminal is a **`ControlTerminal`, a Terminal, not a Node** — it is simply not in the walk"*
- `tools/recipes/build_opconnectctl_v0.py:4` — *"a ControlTerminal is a Terminal, not a Node"*, the reason `OpConnectCtl_v0` was built (`:9-14`), as `…run4-error2-and-zdz.md:209` itself points out

v2 keeps the RETRY unchanged, so run 5 pays for a **third** measurement of the same fact — and (per A3) pays for it *instead of* the test it was built to run.

### B3 HELPER EXISTS — a no-new-node version of the same shape, already enumerated by the toolkit

`archive/peer/2026-09-17-zdz-wirecut-opus.md:134`:

> *"A no-new-op option exists…: `wire_control` `Z/dZ` → any bare **named** input on 1.2's body (the build already enumerates them via `bare_named_sinks`, `build_d1_v0.py:482`), branch that wire onto `#2222` t0 with `OpConnectFromWire_v0`, then remove the temporary segment. It is the same temporary-sink shape with an existing node instead of a created one."*

`bare_named_sinks` is at `tools/recipes/build_d1_v0.py:482-491` and **v2 already imports it** (`:224-225`). This variant avoids the one genuinely unmeasured step (source-less `create_equal`, A2) while exercising the identical branch-and-delete question, and it inherits the same delete hazard the recipe already handles at `v2:1336-1351`. The plan does not weigh it.

*What this covers:* that an untried cheaper variant of the same test exists and is unmentioned. It does **not** say the created-`Equal?` route is wrong — `…opus.md:134` itself calls the alternative "worse" in one respect (it borrows a live sink).

### B1 ALREADY BUILT / B2 — the other three changes

- **Change 2** (`fact(labview_handles())`): `labview_handles` is already imported (`v2:222`) and already called at S0/S1/end (`v2:183`, `:387`, `:1867`). Reuse, no finding. Note the review's own caveat stands — *"that reading relocates the question rather than closing it"* (`…run4-error2-and-zdz.md:254`).
- **Change 3** (ledger print above `settle_index_modes()`): no prior art; it is the direct fix for the lost 66 rows. No finding.
- **Change 4** (rename aside on the exception path): implements `…run4-error2-and-zdz.md:188` verbatim, and `os.rename` is not a LabVIEW save, so *"a broken VI is never written"* (`v2:1861`, `docs/cycle27-plan.md:102`) is untouched. No finding — except A3b, which cancels half of its purpose.
- **The new-file-name manoeuvre** is legitimate under `docs/cycle18-plan.md:53-56` (a changed hash means unreviewed; v2 is being reviewed on its own bytes). I spot-checked "nothing else differs" at the four sites and the S0 cleanup (`v2:389-397`); I cannot run a diff, so that claim is verified by inspection, not mechanically.

---

## What would release this review

| finding | cheapest release |
|---|---|
| A3 (load-bearing) | **not refutable as written** — make the RETRY fall through when `n_src is None`, then `FIXED:` citing the patched line |
| A1 | judgement amends `cycle27-plan.md:89-100` + `d1-route-b-plan.md:563-576` to record the cycle-36 revision; `FIXED:` those lines |
| A2 | rewrite `v2:305-308` and `:1297-1300` to cite the real hazard (`…zdz-wirecut-opus.md:138`) and predict the source-less-`create_equal` outcome |
| A3b | point `OUT` at `build_d1_routeb_v2.json`; fix `:1874`'s label |
| A4 | cite `…zdz-wirecut-{opus,codex}.md` in the recipe docstring |
| B3 | one sentence saying why the created `Equal?` is preferred over the bare-named-sink variant |
| B4 | state that the RETRY is kept only as a logged control, or delete it |

```
PRIOR-ART: contradicted
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: unread-evidence
PRIOR-ART: already-measured
PRIOR-ART: helper-exists
```

The one sentence to carry forward if nothing else is read: **`TEMP_SINK_AUTHORISED = True` is inert while the v1/B2 RETRY at `build_d1_routeb_v2.py:1267-1295` returns before `:1296`, because `PREWIRED[ZDZ_SINK]["ct"]` is `#403` (`:720`, `…run4.log:162`) and a ControlTerminal has no `Diagram[].Nodes[]` index** — so run 5 as specified spends the lock and returns run 4's NO-ROUTE unchanged.

## Sources

(extract from answer)

## What was done with it

ACCEPTED IN FULL by the cycle-37 judgement session. The binding plan was amended (`docs/cycle27-plan.md`
Pre-decided 13a) and six code changes were applied to `tools/recipes/build_d1_routeb_v2.py` before run 5.

FIXED: settled-already - docs/cycle27-plan.md:101 - Pre-decided 13a records the cycle-36 revision in the binding plan (TEMP_SINK true for the Z/dZ row only, SR_QUEUE false permanently), so no material session now reads a plan that forbids this run.
FIXED: refuted-already - tools/recipes/build_d1_routeb_v2.py:332 - the flag comment and the runtime refusal no longer cite the 1055 modal of docs/NAMES.md:473-480; they cite the real silent hazard (src_names=() -> Names=[] -> Index Array[0] default refnum, no error) and predict a BARE sink as its signature.
FIXED: contradicted - tools/recipes/build_d1_routeb_v2.py:1311 - the v1/B2 RETRY now logs its NO-ROUTE reason as a fact and falls through to the temporary sink instead of returning False, so TEMP_SINK_AUTHORISED=True is reachable at all; and OUT plus the summary label now name build_d1_routeb_v2.json so run 5 cannot overwrite run 4's JSON record (A3b).
FIXED: unread-evidence - tools/recipes/build_d1_routeb_v2.py:219 - the recipe docstring now cites archive/peer/2026-09-17-zdz-wirecut-{opus,codex}.md, including :130's external-source finding that Diagram.Nodes[] cannot list a ControlTerminal.
FIXED: already-measured - tools/recipes/build_d1_routeb_v2.py:1312 - the RETRY is kept only as a logged control and no longer decides the row's outcome, so run 5 does not pay for a third measurement of the same fact instead of the test it was built to run.
FIXED: helper-exists - docs/cycle27-plan.md:130 - Pre-decided 13a states why the created Equal? is preferred to the bare_named_sinks variant: the created node borrows nothing live, while the variant risks leaving the original's input wired to Z/dZ, a rule-1a computation change.
