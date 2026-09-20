# priorart-d1-s2-loops

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7775  in 46 / out 36535 / cache-create 220574 / cache-read 3316240  (526s, 29 turn(s))
- **date:** 2026-09-20 03:41:54
- **outcome:** ANSWERED (530s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

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
# PLAN under review ??D1 stage S2, `tools/recipes/stage_d1_s2_loops.py` (cycle 51, 2026-09-20)

## What the recipe does, in full

Start from `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\D1_s1_copy.vi`
(md5 `3e3d23cefd3a334001aa9d6156bf1aee`, 474202 B ??the delivered S1 artefact). Copy it to
`claudeDev\D1_s2_loops.vi`. On `Diagram #686` create **three empty While loops** at (2600,2600),
(2600,3400), (2600,4200); scaffold each one `OpCreateEqual_v0` (both operands from ONE named scalar
output terminal ??node **#8486 `x+1`**, picked BY NAME from the diagram's own output-terminal census)
??`OpStopFromNode_v0` onto that loop's conditional terminal; read `ExecState` in-instance with the
ORIGINAL preloaded read-only; **one** `gscript.save()`; then re-read the saved file's `ExecState` in a
fresh child process, COLD and PRELOADED. 311 lines, AST OK, sha256
`7eb482beab051629d0e8b8c7bf7e0a3c51750aafbf6c1eee658d625c3583d993`.

**NOT in this stage:** no `move_in`, no queues, no re-wiring, no new op, no new device, no VI is ever
RUN, no motor / ASI / camera / GUI action, `allow_broken` never set, `gui_save` never called.

## Prediction contract (14 gate groups, printed and machine-checked)

Diagram 170 ??173 쨌 WhileLoop 3 ??6 쨌 SubVI 97 ??97 unchanged 쨌 Comparison 14 ??17 쨌 all three
conditional terminals re-read BY UID at the end still carrying the wire the driving Comparison
sources 쨌 `ExecState` 1 before the save 쨌 saved file COLD 1 / PRELOADED 1 in a fresh process 쨌
ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` unchanged before and after (`tools/hash_probe.py`) 쨌
refs live 0.

## Why this shape, and what it is built out of

- `docs/cycle27-plan.md` Pre-decided **34(a)/(b)**: `x == x` from one scalar output is a provably-TRUE
  conditional, the operands may sit on the OUTER diagram, so a loop can be created, scaffolded and
  saved with an EMPTY body ??32(b)'s ordering (loops ??`move_in` ??scaffold) is superseded by
  loops ??scaffold ??save.
- `docs/cycle27-plan.md` Pre-decided **34(l)**: that exact shape was MEASURED on 2026-09-20 by
  `tools/bench/diag_s2_scaffold.py` (log `tools/bench/diag_s2_scaffold.log`, readings
  `tools/bench/diag_s2_scaffold.json`, 13 pass / 1 fail): ONE loop scaffolded this way reads
  `ExecState` 1 and SAVES (`claudeDev\DIAG_s2scaffold_030829.vi`, md5
  `eddb3e15e5b0aa673fc2bf59eadd67e2`, 475,422 B, re-read COLD 1 / PRELOADED 1). **This recipe is that
  measured shape times three and nothing else.**
- It **imports** the diagnostic's helpers (`Preload`, `fresh`, `file_facts`, `census_686`,
  `candidates_from`, `try_candidate`, `read_state`, `try_save`) instead of re-typing them, so the
  bytes that ran are the bytes that run. Loop creation is `gscript.loop_in` (`tools/gscript.py:1155`);
  the conditional-terminal reader is `build_opstopfromnode_v0.loop_end_ref`; hashing is
  `tools/hash_probe.py` (Pre-decided 34(k)). Nothing new is built.
- Operand selection is BY NAME, never by ordinal (34(c)) and never from a wire table (34(l) measured
  that the previously pre-selected `#637 'frame index'` is not a named source terminal on `#686`).
- Every address is a uid or an exact name, re-read immediately before use (34(h)): `diag_index`, the
  WhileLoop class index and the operand's class index are re-resolved inside each of the three
  iterations, never cached across a mutation.
- `tools/recipes/stage_d1_s2.py` (1956 lines) is **retired by 34(i)** ??not launched, not edited, not
  re-reviewed; it encodes the withdrawn 32(b) ordering.

## The questions this review should attack

1. Has "three scaffolded empty While loops, saved" already been built, measured or refused here under
   another name?
2. Does any file contradict the counts 170/3/97/14 ??173/6/97/17 for `D1_s1_copy.vi`?
3. Is importing a `tools/bench/` diagnostic module from a `tools/recipes/` stage recipe something the
   project has already ruled against?
4. Is there a helper this recipe hand-rolls that the toolkit already provides?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?럦 **D0 IS DELIVERED** (cycle 31) 쨌 **N1 IS ACCEPTED** (cycle 34) 쨌 **D1 STAGE S1 IS DELIVERED** (cycle 48 ??`claudeDev\D1_s1_copy.vi`, md5 `3e3d23ce??, 20/0) **??S2 is next.** Banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.
## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner_c51m1: # ?뵏 **ACQUIRED 2026-09-20 03:3x ??cycle-51 material session, D1 stage S2 (Pre-decided 34): `tools/recipes/stage_d1_s2_loops.py` (311 lines, sha256 `7eb482beab0516??), prior-art review `d1-s2-loops`, log `tools/bench/stage_d1_s2_loops.log`, readings `tools/bench/stage_d1_s2_loops.json`, artefact `claudeDev\D1_s2_loops.vi`. NO `move_in`, no queue, no re-wiring, no VI run, no motor/ASI/camera/GUI.**
  owner_c50m1: # ??**RELEASED 2026-09-20 03:1x ??cycle-50 material session, Pre-decided 34(j) DIAGNOSTIC `tools/bench/diag_s2_scaffold.py` (NOT a recipe, never under `tools/recipes/`), log `tools/bench/diag_s2_scaffold.log`, readings `tools/bench/diag_s2_scaffold.json`, `BGRUN END rc=1 after 246s` (rc=1 = bgrun's INNER-FAILURE flag on gate G12, not a crash). GATES 13 pass / 1 fail.** ?럦 **READING 1 = ExecState 1**: on a scratch copy of `D1_s1_copy.vi`, ONE new While loop on `Diagram #686` (WhileLoop **#23032**, body Diagram **#23058**) scaffolded by `OpCreateEqual_v0` + `OpStopFromNode_v0` reads **ExecState 1** with the ORIGINAL preloaded and **SAVES**: `claudeDev\DIAG_s2scaffold_030829.vi`, md5 **`eddb3e15e5b0aa673fc2bf59eadd67e2`**, **475,422 B**. Operand: node **#8486 `x+1`** (Function, Nodes[0] of #686) ??the brief's pre-selected `#637 'frame index'` is NOT a named source terminal there (#637's outer feed is an UNNAMED tunnel), so the pre-decided census-order walk took the first scalar-shaped name on the first attempt. Conditional terminal **#23080, wire 0 ??23145**, same uid the Comparison **#23035** sources. ?뵶 **READING 2 = ExecState 0** after `move_in #48` (7 terminals, all 7 wired, SEVERED by the move) into that body ??`g.save()` refused (`RuntimeError: refusing to save a BROKEN VI`), `allow_broken` never set, `gui_save` never called; the on-disk file is still reading 1's bytes. Child-process re-reads of that saved file: COLD **1**, PRELOADED **1**. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after; refs opened 8 / closed 8 / live 0; handles 34278 ??34140 (30976 after the run's own restart). NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.
  owner_c49s3: # ??**RELEASED ??LabVIEW WAS NEVER TOUCHED. No .vi opened, no COM call, no GUI action, no peer, no review, no launch.** Cycle 49 material pass 2: `tools/recipes/stage_d1_s2.py` now carries all FIVE round-2 prior-art fixes plus Pre-decided 33's A5 ??**1956 lines, sha256 `789a5c965ded3942d45f149868bd40571e6519941c33d58b8f1c291674743eda`** (was `71f12e121f95`). A3's table 10 ??**16 rows covering all 14 ops the completeness scan names** (the scan now reads WHOLE lines: at `_grep`'s 400-char truncation it saw 5 ops, MEASURED `tools/bench/c49s3_capscan.log`); the six added ops are all READERS/CREATORS, so **32(d) rule (1) still has no winner and `stop_after_a` stands**. Dead citations replaced (`docs/s0-diff.md:46` was the D22 row; `a move CUTS` matched nothing) by `docs/d1-route-b-plan.md:57-58` + `:67`; the absence-assertion at the `OpStopFromNode_v0` row replaced by the three files that MEASURE "Nodes[] excludes constants"; the scaffold operand no longer picked by ordinal (`#5058` t3 is `Bead is good? array out`, an ARRAY ??`docs/frame-loop-wire-graph.md:171`) and C6 is now C6s+C6/C6w+**C8 FATAL ExecState 1 before the save**; v7's own advance statement (`build_d1_routeb_v7.py:131-135`) cited as the stage's real blocker. Contract re-counted from the file's own `gate(` sites: **A 17 쨌 ACD-full 74**. Verified by `tools/bench/c49s3_astcheck2.log` (AST OK) and `c49s3_citecheck.log` (23/23 citation greps match, 0 EMPTY). ?뵶 THE RECIPE WAS NOT LAUNCHED (round 3 runs next cycle).
  owner_c49s2: # ??**RELEASED ??LabVIEW WAS NEVER TOUCHED THIS CYCLE.** Cycle 49 material: `tools/recipes/stage_d1_s2.py` now implements Pre-decided **32** (scaffold AFTER `move_in`; `OpExitWhile_v0` REFUSED and `SCAFFOLD_STOP_CONTROL` deleted; A3 rebuilt as a measured table over 10 candidate ops + 32(d)'s selection rule; `stop_after_a` branch; 32(f) tunnel-IndexMode read in phase D), AST-checked, sha256 `71f12e121f95`. ?뵶 **THE RUN NEVER LAUNCHED: the prior-art LAUNCH GATE refuses the edited bytes** ??verbatim refusal + the measured mechanism in `archive/2026-09-20-status-cycle49-relocate.md` 짠2. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after (`tools/bench/c49_facts.log`); S1 artefact untouched (`3e3d23ce??, 474202 B); `D1_s2_loops.vi` does NOT exist; refs opened 0 / closed 0 / live 0; handles 34276. No motor, no ASI, no camera, no GUI action.
  owner_c48s1cd: # ??RELEASED ??cycle 48's S1 delivery record RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle49-relocate.md` 짠1. Summary: S1 phases C+D 20 pass / 0 fail, `BGRUN END rc=0 after 679s`, `claudeDev\D1_s1_copy.vi` md5 `3e3d23cefd3a334001aa9d6156bf1aee` 474202 B, ORIGINAL md5 unchanged, D5 FATAL PASS.
  lock_history: # ?뵷 **FIVE LOCK KEYS RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle48-lockkeys.md` 짠1?벬?** ??`owner_c47s1` (cycle 47's REFUSED S1 launch; ?좑툘 superseded in fact by `owner_c48s1cd` above, and its "the ORIGINAL cannot be read" claim is FALSE), `owner_c47t2` (T2's offline RSRC block diff: 45 blocks, 43 identical, only `LIvi`/`LIbd` +920 B), `owner_c46s1cd`, `owner_c46_closed` (the three released cycle-46 keys) and the previous `lock_history` (eight older keys). Four of the five were already pointers into the cycle-36/39/44/45/46/47 relocation files.
  motor:     # limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed; an 18:13 D0 run then moved the magnet to 30 mm and they held. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; detail ??`archive/2026-09-18-status-cycle34-n1.md` 짠1.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py` inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state change**.
Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies `tools/bench/camera_contract.py`. **No beads on the rig.**
?넅 **SAFE MOTION ENVELOPE = THE CONTROLLER LIMITS + the gate's command-class denies** (user, 2026-09-18 15:2x at the
rig). PI `SPA 1 0x15/0x30` ??TMN 0 / TMX 39 (RAM, **never WPA**) 쨌 ASI `SL/SU` absolute mm X ??.8475??.1525, Y ??.7744?╈닋0.7744 (persistent, **never SS Z**),
written+verified by `py tools/motor_gate.py --session start|end` from the user-editable `tools/bench/motor_limits.json`; `--execute` refuses without `tools/bench/motor_session.json` **and** a fresh matching readback.
The gate still refuses ?ㅽ뿕以? every ASI home/zero/save, PI GOH/FRF/DFH/RON/POS/SPA/WPA and all rotor motion (self-test `selftest_motor_gate2.py` 74/74).
??The 15:37 run (8/10, L4 a FALSE PASS) is SUPERSEDED by the 16:0x retest ??`??cycle29-retro-trap.md` 짠7. Limits LEFT ON (PI TMN 0 / TMX 39 **in RAM**, ASI SL/SU persistent); **an 18:13 D0 run then moved the magnet to 30 mm and they held**.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??the three ??lines VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md` 짠4
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1 (lock block above). **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Earlier: `archive/2026-09-18-status-cycle22-close.md` 짠2 쨌 `?쫈ycle20-close.md` 짠1?벬? 쨌 `?쫈ycle21-wire-semantics.md` 짠9/짠9a/짠10 쨌 `?쫈ycle19-flatseq.md`.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.

## NEXT
?럦 **S2's LEGALITY IS SETTLED BY MEASUREMENT ??cycle 49's "S2 CANNOT END LEGAL" IS FALSIFIED.** Cycle 50 ran the discriminating test on a scratch copy of the S1 artefact (`tools/bench/diag_s2_scaffold.py` ??`tools/bench/diag_s2_scaffold.log`, `tools/bench/diag_s2_scaffold.json`, 13 pass / 1 fail, the FAIL being the expected reading): one new While loop on `Diagram #686` scaffolded by `OpCreateEqual_v0` (both operands from ONE scalar output) ??`OpStopFromNode_v0` reads **ExecState 1** and **SAVES** ??`claudeDev\DIAG_s2scaffold_030829.vi`, md5 `eddb3e15e5b0aa673fc2bf59eadd67e2`, 475,422 B, re-read in a fresh process COLD 1 / PRELOADED 1. After `move_in #48` the same copy reads **ExecState 0** and the save is refused. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` unchanged; refs 8 opened / 8 closed / 0 live; no VI was run.
?뵶 **FIRST ACT ??BUILD S2 AS `docs/cycle27-plan.md` Pre-decided 34 NOW DEFINES IT: three While loops on `Diagram #686`, each scaffolded, saved as `claudeDev\D1_s2_loops.vi`. NO `move_in`, NO queues, NO re-wiring.** Contract: Diagram 170 ??173 쨌 WhileLoop 3 ??6 쨌 SubVI 97 ??97 unchanged 쨌 Comparison +3 쨌 all three conditional terminals wired and read back by uid. Start from `claudeDev\D1_s1_copy.vi` (md5 `3e3d23cefd3a334001aa9d6156bf1aee`), gate on it, and copy the proven shape out of `tools/bench/diag_s2_scaffold.py` ??four op calls per loop, already measured. Keep the script SHORT: the 1956-line `tools/recipes/stage_d1_s2.py` is RETIRED (34(i)) and must not be re-armed, edited or reviewed again.
?뵶 **THE SCAFFOLD OPERAND IS PICKED BY NAME FROM A MEASURED SCALAR, NEVER BY ORDINAL (34(c)).** The one that worked is `#8486 x+1` on `Diagram #686`, first attempt, no op error. The pre-selected `#637 'frame index'` did NOT work: `#637`'s outer feed is an UNNAMED tunnel (`out_name ''`), so a name read from a wire table is not automatically a `src_name`. Take operands from the diagram's own output-terminal census, as the diagnostic does.
?뵶 **SECOND ACT ??THE QUEUE `src_name` RESOLUTION TABLE (34(g)): a DOCUMENT, zero LabVIEW.** The element types ARE on file, but SIX OF EIGHT queues have no `(node, named output terminal)` that exists on this copy at the moment their `Obtain` is placed. Write that table ??uid 쨌 exact terminal name 쨌 diagram 쨌 or the stage that must run first ??into `docs/d1-build-plan.md` 짠9, and record there that `Q_focusback` is **1 DBL**, which resolves the Bool-vs-DBL contradiction against `docs/cycle15-plan.md:122`. Owed before the sentinel stages, not before S2.
?윞 **AFTER S2 THE CHAIN IS ONE NODE PER STAGE, AND MOVE + RE-WIRE IS ATOMIC** (34(e), now measured): a moved node lands unwired, so a stage that moves one must also re-wire it before it can save. Order `#48` (7 cut rows) ??`#376` (12) ??`#5058` (13); all 109 cut terminals are already resolved in `tools/bench/d1_rewire_sources.json`.
?뵶 **EVERY ADDRESS IS A uid OR AN EXACT NAME, RE-READ IMMEDIATELY BEFORE USE (34(h)).** Address invalidation by self-mutation is the strongest rival explanation for the ten v3?뭭7 deaths. "Resolve every name up front" is sound for NAMES and unsound for INDICES; they are not the same instruction.
?뵶 **NO INTERMEDIATE ARTEFACT IS EVER RUN** (34(f)) ??a scaffolded loop runs once, a sentinel loop with no producer blocks forever. Both are legal to SAVE; neither is legal to RUN.
?뵶 **No new op, no new device** (Pre-decided 2; user 2026-09-18 08:53). **The retrospective is the LAST thing a session runs**, in the background: `py tools/bgrun.py --max-min 20 --log tools/bench/retro.log -- py tools/retrospective.py --cycle <N>`. Never run one early and never pay a previous cycle's retro debt up front (OPEN 54(a)).
?윞 **Two `doc_lint` items left open deliberately**: `L6`'s 48 blank dispositions are ALL pre-2026-09-15 ??the three reviews of 2026-09-20 are disposed; `L2b` `docs/NAMES.md:1022` points past the end of `docs/toolkit-capabilities.md`. Neither gates anything.
?뮠 **FOR THE USER ??two cost facts, not faults.** (1) Judgement-session spend dominates peer/review spend about 8 : 1 and `audit_cycle`'s C4 bucket understates it roughly 7횞: cycle 49's real session cost was **$61.07** (`tools/bench/cycle_runner.log:62`) against an audited $9.54. (2) Cycle 49 spent two paid prior-art rounds on a recipe this cycle retired unlaunched; the measured route that replaced it cost one $3.36 review plus a 246 s diagnostic. Only you can act on the first; the second is already closed by 34(i).
- ?뵷 **Cycle 49's NEXT relocated VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle50-relocate.md` 짠1.** Earlier ones: `archive/2026-09-20-status-cycle49-relocate.md` 짠2/짠3 쨌 `archive/2026-09-20-status-cycle48-lockkeys.md` 쨌 `archive/2026-09-19-status-cycle46-relocate.md` 짠2?벬? ??all unchanged and still current.
- ?숋툘 **Operating facts, keep:** the ORIGINAL is readable via `py tools/bgrun.py --material ??-- python -u <script>`; `tools/hash_probe.py` is the read-only md5/sha256/size probe (34(k)); and an UNSAVED in-memory edit can be read ONLY in-instance under `Preload` ??the child-process `ExecState` read applies to files on disk (34(l)).
- ?좑툘 **BINDING from the 4th outcome review:** every cycle must end with saved files and md5s in a log. Cycle 50 met it with `claudeDev\DIAG_s2scaffold_030829.vi` (`eddb3e15e5b0aa673fc2bf59eadd67e2`) and `tools/bench/diag_s2_scaffold.json`. **Three USER-ONLY decisions remain open and are NOT blockers**: OPEN 53's physical-zero question before any D1 motor-moving run; schedule-or-descope requirement 1; place-or-descope the item at its `:126`.
- ?윟 **Cycle 46's measurements are `docs/cycle27-plan.md` Pre-decided 29(a)??j); do not restate them here.** The two that bind every stage: `gscript.save()` reaches `SaveInstrument` ONLY at `ExecState != 0` (`allow_broken=True` banned), and `shutil.copy2(ORIGINAL, claudeDev\??` SILENTLY RE-BINDS 22 SubVI calls and loses 8 ??**every stage gate compares to the ORIGINAL, never to a copy** (29(g)).
- ?넅 **OPEN from cycle 46, all live:** (a) `claudeDev\background VIs_COPY\` = 94 `.vi`, an unmanaged duplicate hierarchy on the build path; (b) `logclass.py` counts `selftest_*.log` as a build; (c) `gui_save`'s Ctrl+S bypasses `lv_gui.ps1`. **Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

No LabVIEW was touched: no `.vi` opened, no COM call, no lock, nothing built, edited or run. I read `docs/`, `archive/` (peer exchanges included), `tools/recipes/`, `tools/bench/` logs and JSON.

---

# PRIOR-ART REVIEW — `tools/recipes/stage_d1_s2_loops.py` (D1 stage S2, cycle 51), sha256 `7eb482beab05…`

## PART A — THE DIRECTION

### A1 — SETTLED ALREADY? **No slug.** The direction *is* the settlement, and it is dated and measured

`docs/cycle27-plan.md:868-887` (Pre-decided **34(a)/(b)**, 2026-09-20) decides exactly this shape — "THREE EMPTY WHILE LOOPS, EACH SCAFFOLDED BY `OpCreateEqual_v0` → `OpStopFromNode_v0`, SAVED — NO `move_in`, NO QUEUES, NO RE-WIRING" — and `:948-969` (**34(l)**) records the measurement that falsified the rival ("S2 cannot end legal"). The readings are on file at `tools/bench/diag_s2_scaffold.json:453-476` (`1_loop_scaffolded_no_move: 1`, save 475,422 B, `S2DIAG-COLD 1 / S2DIAG-PRELOAD 1`). Citing this as `settled-already` would be over-broad: it settles the direction *in favour of* the build.

### A2 — REFUTED ALREADY? **No slug — and I am saying so explicitly so it is not re-raised**

Round 1 of this stage's prior art killed a state with almost the same name: `archive/peer/2026-09-20-priorart-d1-s2-stage.md:1019-1021` — "**B2 ALREADY FAILED — 'three empty While loops' is a state already measured at `ExecState 0`**", resting on `docs/toolkit-capabilities.md:67` ("a fresh While loop's **unwired** conditional terminal is a broken VI by itself"), and its accepted disposition at `:1067` says the fix was that "the unsaveable 'three empty While loops' path no longer exists".

**That finding does not cover this plan.** Its whole force is the word *unwired*; the same capability file at `:64` records `OpCreateEqual_v0` 23/0 with "Operands may sit on an outer diagram: LabVIEW makes the tunnels", and `:63` records `OpStopFromNode_v0`'s T5 closed by measurement (conditional terminal `wire 0 → 387`, scratch then `ExecState 1`). 34(l) then measured the composite on a copy of the actual S1 artefact. A future reviewer re-raising round-1 B2 against these bytes would be citing the unwired case against a wired one.

### A3 — CONTRADICTED. 🔴 **The conditional-terminal readback — the plan's headline gate — is taken from a reader whose error columns the imported code throws away, against Pre-decided 14**

Side one, the plan's contract: "all three conditional terminals re-read BY UID at the end still carrying the wire the driving Comparison sources".

Side two, the project's own rule, `docs/cycle27-plan.md:147-150` (Pre-decided 14):

> "**A value returned beside an error has measured nothing**: run 3's three conditional terminals read `wire 0` *with* `error 1055: Property Node in **OpLoopEndRef_v0.vi**` attached (`…run3.log:416-418`), so that 0 is UNREAD, not zero, and must be reported as UNREAD."

The reader this stage uses is that same op, and it returns the error columns precisely so this rule can be applied:

- `tools/recipes/build_d1_v0.py:848-853` — `loop_end_ref` poisons every output, then returns `…, err=err, errs=errs` from the four per-property error columns; its docstring `:823-824` says they are read "because 'no error out' is not a verdict that a property resolved".
- `tools/recipes/build_opstopfromnode_v0.py:340-344` — the wrapper the recipe imports as `LOOP_END_REF`: "…returns the four per-property error columns in `errs`, which this file's earlier hand-rolled copy dropped. **T3/T3b/T4 are scored on `errs` being empty, so a silently unresolved property can no longer read as 'not wired yet'.**"

And the imported code drops them anyway: `tools/bench/diag_s2_scaffold.py:270-274` and `:312-316` keep only `cond_term_uid` / `cond_wire_uid`; `:322-327` computes `att["ok"]` from those alone; `err`/`errs` appear nowhere in the file. The diagnostic's own fact line — "conditional terminal BEFORE = #23080 wire 0 (**0 is EXPECTED**)" (`tools/bench/diag_s2_scaffold.json:745`) — is character-for-character the run-3 shape Pre-decided 14 forbids reporting as a zero.

Scope, stated fairly: `att["ok"]` cross-checks the wire uid against the Comparison's own `terms_of` read, so a poisoned value fails closed rather than passing. The exposure is therefore a **false FAIL reported as a real one** — on three loops the op is driven 6–9 times instead of once, and a single 1055 turns a legal artefact into `BGRUN END rc≠0`, which under CLAUDE.md §5 buys a mandatory peer review and, under §3, counts toward the firefighter ladder. The fix is two lines inside the imported helper's caller: read `err`/`errs`, and when non-empty classify the row **UNREAD**, never FAIL.

**Refutation path, if you disagree:** show in writing that `OpLoopEndRef_v0`'s four error columns cannot be non-empty on this call shape, or that the `terms_of` cross-check alone discharges Pre-decided 14's "must be reported as UNREAD".

### A4 — UNREAD EVIDENCE. 🔴 **The stage saves an artefact but drops the acceptance gate the previous stage carried — 29(g)'s SubVI *table*, reduced here to a class *count***

The plan's contract for subVIs is one number: "SubVI 97 → 97 unchanged". The document the plan's own count line descends from says that is not the acceptance reference:

- `docs/cycle27-plan.md:629-641` (Pre-decided **29(g)**): "🔴 **THE ACCEPTANCE REFERENCE FOR A STAGE ARTEFACT IS THE ORIGINAL'S SUBVI TABLE, NEVER A BYTE COPY** … the COM-SAVED copy matches the ORIGINAL on **all 98 SubVI calls, name and path, byte for byte**, with **zero** rows into `claudeDev\background VIs_COPY\`, while the PRISTINE BYTE COPY re-binds **22** calls … **So `shutil.copy2(ORIGINAL, claudeDev\…)` produces a SILENTLY RE-BOUND VI**, and every stage gate compares against the ORIGINAL, never against a copy."
- `docs/cycle27-plan.md:790` — the very line that fixes the counts this plan quotes: "Every comparison is against the ORIGINAL, never against a copy (29(g))."

And the instrument is built, was FATAL one stage ago, and passed:

- `tools/recipes/stage_d1_s1.py:182-188` — gate **D5**, "**THE ARTEFACT'S SubVI TABLE AGAINST THE ORIGINAL'S, BOTH COLD, ONE CONDITION PER CHILD PROCESS AND PER LabVIEW INSTANCE** (Pre-decided 29(g)) … **FATAL**".
- `tools/recipes/stage_d1_s1.py:377-400` `cold_subvi_table()` — "Nothing is read here: this CALLS the BUILT `tools/bench/s1_subvi_paths.py` `run_condition()`"; `:408` `compare_subvi_tables(got, reference, expect_missing)` already takes the "this stage legitimately removed a row" argument, and `:243-247` pins `PIN_SUBVI_ROWS = 98` with `TIFF_SUBVI_KEY` as the one expected absence.
- STATUS records that gate as part of the delivery: the `owner_c48s1cd` lock key, relocated verbatim to `archive/2026-09-20-status-cycle49-relocate.md` §1 — "20 pass / 0 fail … **D5 FATAL PASS**".

This stage does `shutil.copy2` of a claudeDev VI and then a COM save under `Preload`, i.e. the two operations 29(g) and 29(c) were written about, and its 14 gate groups contain no path-level check of the result. `expect_missing` makes the reference straightforward: the ORIGINAL's 98-row table minus `TIFF_SUBVI_KEY`, which is exactly the S1 artefact's 97.

**Refutation path:** cite the measurement that makes the path table redundant for a *re-save of an already-verified artefact* (a candidate is `tools/bench/s1_subvi_paths.log` 15/0 plus `docs/cycle27-plan.md:613-616`, which permits preload-then-save for claudeDev stage artefacts), and show in writing that a COLD `ExecState 1` reading covers what a 97-row name+path diff would have covered.

---

## PART B — THE ARTEFACT

### B1 — ALREADY BUILT, and correctly reused. **No slug** (following round 2's own precedent)

The three-loop creation is not new and is not claimed to be: `tools/recipes/build_d1_routeb_v7.py:788-805` creates the loops on `Diagram #686` at **the identical coordinates** `(2600,2600) / (2600,3400) / (2600,4200)` with the identical gates, and it passed in the real VI — `tools/bench/build_d1_routeb_v7_run10.log:70-76`, ending "PASS S2 WhileLoop 3 -> 6 and Diagram 170 -> 173  WhileLoop 6, Diagram 173". Round 2 met this same reuse and declined to slug it (`archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1195`, "ALREADY BUILT, and correctly reused. No slug"); the genuinely new part is still the stage boundary plus the scaffold-then-save. Worth adding to the plan's citation list beside the diagnostic, since v7's version of these four lines is the one with a real-VI pass behind it.

### B2 — ALREADY FAILED? **No slug.** The ten v3→v7 deaths are at the re-wiring pass this stage excludes by construction

`docs/cycle27-plan.md:927-935` (34(h)) names address invalidation across self-mutation as the strongest rival for those deaths, and the recipe re-resolves `diag_index`, the WhileLoop index and the operand class index inside each iteration. The one failure that *has* landed on this exact call is the `OpLoopEndRef_v0` 1055 of run 3 — folded into **A3** rather than double-counted here.

### B3 — HELPER EXISTS? **No slug.** Two notes for the record

The recipe imports rather than hand-rolls (`gscript.loop_in` `tools/gscript.py:1155`; `WALK`/`cls_of`/`idx`/`loop_end_ref` from `build_opstopfromnode_v0.py:129/147/158/340`; `move_in`/`diag_index`/`terms_of` from `build_d1_v0.py`). Importing a `tools/bench/` module from a recipe is established practice, not a prohibition: `build_d1_routeb_v0.py:157-160` through `v7.py:372-375` all do `sys.path.insert(… "tools","bench")` + `from bench_prep import labview_handles`, and the diagnostic's own header ban (`tools/bench/diag_s2_scaffold.py:3-4`) is about *moving* the file under `tools/recipes/`, not about importing it.

Two small overlaps, neither worth stopping a build:
1. `file_facts`/`md5` (`diag_s2_scaffold.py:127-152`) hashes in-process while `docs/cycle27-plan.md:970-973` (34(k)) says `tools/hash_probe.py` is the probe to "use for every artefact md5 a stage must record". Pick one per artefact so the log has a single provenance.
2. The imported `census_686`/`try_candidate`/`read_state`/`try_save` write their results into the **diagnostic module's** globals (`R`, `facts`, `passes`, `fails` — `diag_s2_scaffold.py:102-106`, `:345`, `:362`), not the recipe's. The printed FACT lines still reach the log, but a recipe that dumps its own JSON will find `readings`/`saves` empty unless it reads them out of `diag_s2_scaffold.R`.

### B4 — ALREADY MEASURED? **No slug.** One loop is measured; three is not

`tools/bench/diag_s2_scaffold.json` holds the single-loop case only (`loop:` `:601-608`, one entry in `attempts` `:401-451`). The plan's own description — "that measured shape times three" — is accurate, and the 3-loop save has no reading on file. The re-read gates it does repeat (S1 md5/size, the 170/3/97/14 census) are boundary gates, not re-measurements.

---

## Not slugged, but on the record

- **The scaffold is not free structure.** `docs/toolkit-capabilities.md:64` measured `LoopTunnel 0 → 2` for an outer-diagram operand, and the real VI measured `LoopTunnel 132 → 133` plus `Wire 1899 → 1901` (`tools/bench/diag_s2_scaffold.json:503-507`, `:711-718`). So each scaffold **branches the original's `x+1` net through a new border tunnel**, and no document on file yet names the stage that removes the three `Equal?`s and their tunnels once the real sentinels arrive — 34(e) `docs/cycle27-plan.md:896-903` covers move+re-wire only. That is a later stage's contract, not a defect in this one, but it should be written down before it is inherited.
- **uid reuse after deletion is already on file** (`.claude/skills/labview-automation/references/vi-scripting.md:601`; `archive/peer/2026-09-17-d1-s3b-uid-reuse-after-delete.md`; and visibly in `build_d1_routeb_v7_run10.log:71`, where the new WhileLoop took uid **#48** after v7 had deleted the subVI of that uid). It does not touch this stage, which deletes nothing — but the 34(e) chain addresses `#48` by uid, so keep the no-delete property of S2 in view when that stage is written.

---

## MACHINE-READABLE

```
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
```

**Citations, one per finding, for the disposition:**

- `contradicted` — `docs/cycle27-plan.md:147-150` (Pre-decided 14) and `tools/recipes/build_d1_v0.py:848-853` + `tools/recipes/build_opstopfromnode_v0.py:340-344` (the `err`/`errs` contract) **vs** `tools/bench/diag_s2_scaffold.py:270-274`, `:312-316`, `:322-327` (error columns discarded) and `tools/bench/diag_s2_scaffold.json:745` ("wire 0 (0 is EXPECTED)").
- `unread-evidence` — `docs/cycle27-plan.md:629-641` (29(g)) and `:790` (31(h)) **vs** the plan's SubVI-count-only contract; the built, already-FATAL instrument at `tools/recipes/stage_d1_s1.py:182-188`, `:377-400`, `:408`, `:243-247`, whose pass is recorded in `archive/2026-09-20-status-cycle49-relocate.md` §1.

## Sources

(extract from answer)

## What was done with it

Both findings were ACCEPTED by the cycle-51 judgement session; neither is refuted. The recipe was changed to
answer them, and the two changes are the release lines below.

FIXED: contradicted - tools/recipes/stage_d1_s2_loops.py:177 - every conditional-terminal readback now goes through `cond_read()`, which reads `OpLoopEndRef_v0`'s four per-property error columns (`err` + `errs`) and reports a non-empty column as a third outcome UNREAD that no gate accepts, on all three loops and on the final by-uid re-read, as Pre-decided 14 requires.
FIXED: unread-evidence - tools/recipes/stage_d1_s2_loops.py:350 - the SubVI class-COUNT gate was demoted to a reported observation (G8s) and the acceptance gate is now S1's built COLD SubVI-TABLE comparison against the ORIGINAL (`cold_subvi_table`/`compare_subvi_tables`, D5-style FATAL G15 with S1's `expect_missing` key), as Pre-decided 29(g) requires.

Not slugged, and recorded rather than acted on: the two small overlaps of B3 (hash provenance, and the imported
diagnostic's globals) and the two "on the record" items — the scaffold's three `Equal?`s plus their border
tunnels owing a removal stage, and uid reuse after deletion — belong to the later stages, not to S2.
