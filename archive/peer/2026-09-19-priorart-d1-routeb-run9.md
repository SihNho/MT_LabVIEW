# priorart-d1-routeb-run9

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.2179  in 28 / out 28705 / cache-create 266698 / cache-read 1666345  (403s, 25 turn(s))
- **date:** 2026-09-19 05:21:19
- **outcome:** ANSWERED (404s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

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
# PLAN UNDER REVIEW ??`tools/recipes/build_d1_routeb_v6.py` (run 9), cut from v5's bytes with EXACTLY TWO edits

Cycle 41, 2026-09-19. The recipe is `tools/recipes/build_d1_routeb_v6.py`, sha256 `07c6b5d6a37e0fee??
(md5 `9035029214449dd893ce56ab53618b56`), 2551 lines. It is a byte-for-byte copy of
`tools/recipes/build_d1_routeb_v5.py` (md5 `0a240fc35472e5d1ad42331ed23f39cc`, the recipe that produced
`tools/bench/build_d1_routeb_v5_run8.log`, `BGRUN END rc=1 after 1822s`, 80 PASS / 0 FAIL) with two edits and
nothing else. The launch command will be:

    py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v6_run9.log -- py -u tools/recipes/build_d1_routeb_v6.py

## EDIT 1 (E1) ??un-invert the `Z/dZ` temp-sink gate

`build_d1_routeb_v6.py:1849`: `_b_ok = (_wddelta == 0)` becomes `_b_ok = (_wddelta == 1)`, and the comment at
`:1601-1613` is rewritten. v5's comment claimed "every write in the bracket is a BRANCH off an existing net ??
so the expected delta is 0". The claim is false at its premise: the branch runs only under `if not zw`
(`:1597`), so the before-count at `:1613` is taken while the source control is still bare; `wire_control` at
`:1668` CREATES the sink wire; `OpConnectFromWire_v0` only BRANCHES that same net at delta 0
(`docs/toolkit-capabilities.md:70`); and the wire SURVIVES the delete
(`tools/bench/build_d1_routeb_v5_run8.log:358`). One new wire is exactly what the bracket is for, so the null
is +1. Binding decision: `docs/cycle27-plan.md` Pre-decided 19 (cycle-40 judgement session). Run 8's `:418`
already reads the row as WIRED ??(a) source identity True, (b) per-diagram delta +1, (c) `Is Broken? False`,
(d) sink read back 29238 ??i.e. only the gate said otherwise.

## EDIT 2 (E2) ??re-instrument K3's survival census

`build_d1_routeb_v6.py:2128-2215`: the census that read `set(o["uid"] for o in g.report_all(TARGET,"Wire"))` is
replaced by a walk-based readback. `report_all(Wire)` is itself an `error 2` victim ??run 8 raised
`error 2 ??Traverse for GObjects.vi->OpReportAll_v0.vi | Class Operator:Traverse (Traverse Failed)` after 50
uids had been claimed (`tools/bench/build_d1_routeb_v5_run8.log:364`), so the one measurement run 8 existed to
produce came back UNREAD and its `WIRED 53` is still an attempt count. The replacement walks the four diagrams
the build touches (the loop bodies + `FRAME_BODY_UID` 639 + `SIBLING_DIAG_UID` 686; run 8 read them as
20 / 21 / 24 / 56) with the recipe's own `wmap(TARGET, d, fresh=True)` and, for every row in the S3w ledger,
asserts `wmap(TARGET,d)[node][2][t]["wire"] == claimed_uid`, the address parsed from the row's own ledger tag
`#<uid> t<i> ?? (built at `:1956`) through `RETARGET`. It prints a NUMBER (claimed uids that read back at
their own terminal) plus every mismatching row with its (diagram, node, terminal) and what that terminal
actually reads, and stays in the same place ??immediately after the S3w PRE-SETTLE ledger line, not after S5,
because no route-B run has ever reached S5. Binding: `docs/cycle27-plan.md` Pre-decided 18 as amended by the
cycle-40 judgement session. `gscript.net_map` is NOT used and is BANNED as a counter (Pre-decided 17: it calls
`remove_bad_wires_scripted` internally, `tools/gscript.py:2507-2516`, `:2568-2588`).

## What is deliberately NOT changed

No third edit. The per-bead maths is untouched (rule 1a). `error 2` is NOT addressed by either edit and is
expected to recur. No VI-wide remove-broken-wires is added or moved (Pre-decided 17). No new op is introduced;
both edits use helpers the recipe already holds (`wmap`, `diag_index`, `diagram_wire_count`, `claim_wire`).

## PREDICTIONS for run 9 (written before the run)

1. `Z/dZ` t0 PASSES its J2 gate at per-diagram delta +1.
2. The survival census READS and returns a number (no `error 2` in that block).
3. `#2222` t2 / t3 / t4 / t5 stay WIRED.
4. `error 2` still occurs elsewhere (E1/E2 do not address it).

## Already ruled out / already measured ??do not re-raise these as findings unless the citation is wrong

- The handle-count explanation of `error 2` is REFUTED by our own logs (healthy at 51,349 / 51,353 handles,
  crashed at 35,551 / 35,555 ??`archive/peer/2026-09-19-routeb-run8-predictions.md` Q3).
- The four `SCRATCH_routeb_*_crash_*` copies are byte-identical to the ORIGINAL and are worthless as evidence
  (run 8 S0, Q4 of the same review).
- `VI.Get Errors` (method 452) is NOT built, is probably unreachable over this COM path, and is not authorised.
- `docs/d1-route-b-plan.md` 짠10 is NOT authorised; `SR_QUEUE_AUTHORISED` stays False; `TEMP_SINK_AUTHORISED` is
  True for the `Z/dZ` row only (Pre-decided 13 + 13a).

## The question for this review

Has either edit ??the +1 null for a create?뭕ranch?뭗elete bracket, or a walk-based per-terminal wire readback
census over named diagrams ??already been built, measured or refuted in this project under another name?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle39-judgement.md` (latest ??why the `#2222` rows regressed, H4's refutation, the run-8 test)** + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
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
  status: released   # ?뵷 **D1 ROUTE-B v5 RUN 8 RAN, 2026-09-19 03:58:14 ??04:28:36** ??`tools/bench/build_d1_routeb_v5_run8.log`, `BGRUN END rc=1 after 1822s`, **80 PASS / 0 FAIL**. ?뵶 **EVERY PREDICTION MISSED**: `#2222` t3/t4/t5 all WIRED (`:411-:413`), `Z/dZ` t0 FAILED on J2 reading (b) with per-diagram delta **+1** (`:418`); ledger 66/53/12/1 (`:363`); K3's SURVIVAL CENSUS **UNREAD** ??`report_all(Wire)` died of `error 2` (`:364`); the same `error 2` crash in `settle_index_modes` at 35,555 handles (`:431-:432`), victims 6 ??**11**. Original md5 unchanged (`:13`, `:440`). Its mandatory failed-prediction review is IN and **UNDISPOSED**: `archive/peer/2026-09-19-routeb-run8-predictions.md` (ANSWERED, claude/hypothesis opus max, $4.4847, 676 s) ??it calls run 8 a **regression** (WIRED 54 ??53, FAILED 9 ??12), says the `+1` is the wire the bracket exists to create so **the J2(b) null is inverted**, and identifies `error 2` as LabVIEW **"Memory is full"** with the handle count neither cause nor symptom. FULL RECORD ??`archive/2026-09-19-status-cycle39-run8.md` 짠7 (run 8) 쨌 짠4 (run 7) 쨌 짠5 (cycle 38) 쨌 짠6 (cycle-37 machinery) 쨌 짠3 (v5 build) 쨌 짠1/짠2 (runs 6 and 5).
  owner:     # released 2026-09-19 04:28 KST after run 8 ended (BGRUN END rc=1 after 1822s)
  since:
  purpose:   # RUN 8 RAN 03:58:14 -> 04:28:36, log tools/bench/build_d1_routeb_v5_run8.log
  purpose_c38:   # RELOCATED VERBATIM (rule 4, 2026-09-19) ??`archive/2026-09-19-status-cycle39-run8.md` 짠5 ??cycle-38 prior art over the edited bytes (`archive/peer/2026-09-19-priorart-d1-routeb-run6.md`, NOT NOVEL, F1?밊4 all disposed), the four P1?밣4 patches, and why `--recipe` is mechanically unusable.
  purpose_c38d5: # RELOCATED VERBATIM (rule 4, 2026-09-19) ??`archive/2026-09-19-status-cycle39-run8.md` 짠5 ??run 6's failed-prediction review (`archive/peer/2026-09-19-routeb-run6-regression.md`, ANSWERED, $3.6636) and its Q-A/Q-B1/Q-B2/Q-B3 findings.
  purpose_c37:   # RELOCATED VERBATIM (rule 4, 2026-09-19) ??`archive/2026-09-19-status-cycle39-run8.md` 짠6 ??the cycle-37 `lv_stallcheck.ps1` clauses, their self-test, and the review that refuted the justification. ?좑툘 ITS PROPOSED REPAIR IS NOW APPLIED: `tools/lv_stallcheck.ps1:273` writes the gating `stall_pid*.log` ONLY on `VERDICT: BLOCKED` (cycle-40 dispatch; self-test `tools/bench/repair_c37_stall_selftest.py` G7/G8, first run 4/4 FAIL on an observability defect in the new gates, re-run BLOCKED by `guard_peer`).
  purpose_now:   # ??**N1 IS ACCEPTED (cycle-34 judgement) ??D1 IS UNBLOCKED**: pre-bead-loss window k<10018 = ZERO exceedances over 50,201 valid bead-frames (max |dx| 4.857e-07 / |dy| 4.677e-07 / |dz| 1.279e-05 vs tol 1e-6 x,y and ~1e-4 z); the VI-level run reproduces the DLL numbers exactly, so the LabVIEW wrapper is numerically transparent (`tools/bench/n1_gpuk_vi_fixture.log`, 7/7, rc=0). ?좑툘 TWO items FLAGGED TO THE USER, NOT closed: (a) acceptance is on the PRE-BEAD-LOSS WINDOW, not the whole fixture; (b) the single z-LUT index flip at k1679/bead 4 (dz -4.667e-03, above the z tolerance) excluded by the FLIP mask. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠2; record ??`archive/2026-09-18-status-cycle34-n1.md` 짠1/짠4.  RELOCATED PROSE: cycle-35/36 lock prose ??`archive/2026-09-18-status-cycle36-relocate.md` 짠1/짠2. cycle-34/32/30 ??`archive/2026-09-18-status-cycle34-n1.md` 짠1 쨌 23 ???쫈ycle23-close.md 짠1/짠2/짠3 쨌 22 ???쫈ycle22-close.md 짠1 쨌 21 ???쫈ycle21-wire-semantics.md 짠8/짠9/짠9a 쨌 20 ???쫈ycle20-close.md.
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

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
??**CLOSED ??all five VERBATIM in `archive/2026-09-18-status-cycle36-relocate.md`**: **32** D0 delivered 18:13, 짠5 (?좑툘 the next outcome review judges whether it answers "zero runnable VIs" ??do NOT close it unilaterally) 쨌 **55** `tmx_from` rule 4 deleted, 17/0, 짠6 쨌 **56** `audit_cycle` C7 repointed at the `status: current` plan, 짠7 (?좑툘 **STILL OPEN from retrospective-cycle31 F4: C4 understates spend** ??judgement `claude -p` sessions carry no COST line) 쨌 **51/52/52a** 짠8 쨌 **53's mechanical half** (16:0x, retest 10/10, self-test 76/76) 짠9.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.

## NEXT
?뵶 **USER, 2026-09-18 21:3x (after watching the D0 copy run its experiment loop live ??"?곷떦??怨좊Т?곸씤??吏湲덉? 萸?
?섍퀬?덈뒗嫄곗엫?"): TWO CYCLES SINCE D0 HAVE NOT TOUCHED D1. The next cycle's FIRST ACT is a D1 BUILD dispatch
(`docs/cycle27-plan.md` Pre-decided 1/6; route B per `docs/d1-route-b-plan.md`, ExecState read WITH the original
preloaded ??Pre-decided 14a/16). NO machinery repairs, NO watchdog reviews, NO audit fixes, NO doc relocation
before that dispatch has RUN; those go AFTER the D1 dispatch returns, or into the retrospective as findings. A
cycle that ends without a D1 build log is a wrong-ordering cycle by definition.**
?? **FIRST ACT ??BUILD AND LAUNCH RUN 9 as `tools/recipes/build_d1_routeb_v6.py`, cut from v5's bytes.** Exactly
TWO edits; do not add a third, and do not touch the per-bead maths (rule 1a):
**E1 ??UN-INVERT THE `Z/dZ` GATE**: `build_d1_routeb_v5.py:1842` `_b_ok = (_wddelta == 0)` ??`== 1`, and correct
the false premise in the comment at `:1601-1605`. MEASURED and binding: **`docs/cycle27-plan.md` Pre-decided 19**
??the before-count at `:1613` is taken while the control is still bare (`if not zw`, `:1597`), `wire_control`
`:1668` then CREATES w29238, `OpConnectFromWire_v0` only BRANCHES it at delta 0, and it SURVIVES the delete
(`?쫞un8.log:358`). **`Z/dZ` t0 was ALREADY WIRED in run 8** ??identity True, `Is Broken? False`, read back 29238;
only the gate said otherwise. Do not re-open the route on the strength of that FAILED label.
**E2 ??RE-INSTRUMENT K3's SURVIVAL CENSUS**: drop `report_all(Wire)` (`:2120`) ??it is itself an `error 2` victim
(`?쫞un8.log:364`, died after 50 claimed uids, so run 8's `WIRED 53` is STILL an attempt count) ??and assert
`wmap(TARGET, d)[node][2][t]["wire"] == claimed_uid` over diagrams 20/21/24/56 instead. Binding: **Pre-decided 18
as amended**.
Arm AND release a stop record for v6's own sha, then:
`py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v6_run9.log -- py -u tools/recipes/build_d1_routeb_v6.py`
**PREDICTIONS for run 9** ??any miss ??failed prediction ??`-Agent claude -Role hypothesis` SINGLE arm
(Pre-decided 7): `Z/dZ` t0 PASSES J2 at delta +1 쨌 the survival census READS and returns a number 쨌 `#2222`
t2/t3/t4/t5 stay WIRED 쨌 `error 2` still occurs (E1/E2 do not address it).
?뵶 **`error 2` IS NOW THE DOMINANT FAULT, AND ITS HANDLE EXPLANATION IS DEAD.** Run 8: victims **6 ??11**
(10 `report_all(Diagram)` + 1 `report_all(WhileLoop)`, `?쫞un8.log:419-429`), it killed `report_all(Wire)` (`:364`)
and still crashes `count(LoopTunnel)` in `settle_index_modes` (`:432`, `:454`). **The handle premise is REFUTED by
our own logs** ??both runs ran healthy at 51,349 / 51,353 handles and crashed at 35,551 / 35,555
(`archive/peer/2026-09-19-routeb-run8-predictions.md` Q3) ??so never again attribute `error 2` to a handle count.
LabVIEW `error 2` = memory / reference allocation. UNCONFIRMED, to be tested rather than assumed: cumulative
allocation failure inside one instance, cleared by restarting between phases. ?좑툘 **K1/K2 are candidate CAUSES of
the 6 ??11 worsening**: run 8 was billed as a ONE-LINE discriminator and was not one, because K2's `fresh=True`
re-walk at `:1613` adds traverse work per row.
?뵮 **UNRUN, and it is what settles Pre-decided 17** ??the K1 separator, AFTER run 9 launches, never before: on a
scratch copy, `terms_of(copy,24,2222,fresh=True)` + `count(Tunnel)`/`count(Wire)` ??
`remove_bad_wires_scripted(copy)` ??repeat. If t3/t4/t5 vanish, K1 is confirmed and item 17 must be re-worded to
"anywhere between the first cut and the last rewire".
??**RUN 8 RAN, AND ITS MANDATORY REVIEW IS IN AND FULLY DISPOSED** ??`tools/bench/build_d1_routeb_v5_run8.log`,
`BGRUN END rc=1 after 1822s`, 80 PASS / 0 FAIL gates, ledger `:363` 66 attempted / 53 WIRED / 12 FAILED /
1 NO-ROUTE (11 of the 12 FAILED rows carry `error 2`; the 12th is `Z/dZ`'s inverted gate). Original md5 unchanged
`:13`/`:440`; ExecState S1 cold 0 = UNREAD `:37`, live copy PRELOADED 1 `:437`. Review
`archive/peer/2026-09-19-routeb-run8-predictions.md` (ANSWERED, claude/hypothesis opus/max, $4.4847, 678 s).
?뵶 **Its headline correction stands, and it is this cycle's own framing error: run 8 was a REGRESSION overall, not
an improvement** (WIRED 54 ??53, FAILED 9 ??12, NO-ROUTE 3 ??1). The 3 gained rows are ALL `#2222`, while 4 rows
run 7 had wired fell to `error 2`. Judging the run by `#2222` alone ??the rows the predictions happened to name ??
is what made a regression look like progress. ??Q4 also CLOSES a carried item: the four crash copies are
**worthless as evidence** ??run 8's S0 measured the newest one's md5 as the ORIGINAL's, so no run ever saved into
one, and the Q-B3 "read-only 5-step pass over a preserved crash copy" is retired. Nothing deletes them; they
simply are not evidence.
?좑툘 **STILL BINDING: `docs/cycle27-plan.md` Pre-decided 17 + 18** ??no VI-wide remove-broken-wires inside a row
loop; **`gscript.net_map` is BANNED as a counter** (it calls that reaper itself); a ledger reports SURVIVING
wires. Cycle-39 reasoning chain ??`archive/2026-09-19-status-cycle39-judgement.md`.
?뵩 **THE STALL WATCHDOG REPAIR IS DONE AND PROVEN ??do not redo it.** `tools/lv_stallcheck.ps1:273` now writes the
gating `stall_pid*.log` ONLY when the dialog check returns `VERDICT: BLOCKED`; self-test
`tools/bench/repair_c40_stall_selftest.log` **8 PASS / 0 FAIL**. Its discharge review went to **gemini, not
opus** ??`archive/peer/2026-09-19-stall-selftest-c39-g78b.md` (ANSWERED) ??because an assertion-string bug does
not warrant a $4.5 arm and gemini is an authorised discharging agent. Gemini's Q1 ("the repair removed a
capability") is REFUTED by that 8/0 run: `flagged` flipped False ??True with `lv_stallcheck.ps1` untouched.
?좑툘 **ONE THING LEFT ??one read, no new device**: gemini's Q2, that `$record` set to the sentinel string
`NOT WRITTEN - ?? stays TRUTHY in PowerShell. Census every consumer of `$record` after `:273` for a truthy test
or a path API (`Test-Path`/`Get-Item`/`Remove-Item` would throw on the `:` in the sentinel); fix only if one is
found.
??**RETROSPECTIVE-CYCLE40 IS IN AND FULLY DISPOSED** ??`archive/peer/2026-09-19-retrospective-cycle40.md`
(ANSWERED, 239 s), **`VIOLATION: none`**: "this cycle was run well and was worth its cost ??I found no structural
fault that changed what the cycle cost, produced, or whether it produced anything." Its findings were acted on in
the same cycle: the stale crash-copy pointer is deleted from NEXT (F2b/F6), Pre-decided 18 is amended (F2a), the
watchdog figure is corrected to 0 of **6** (F6), and the $4.48 run-8 review ??archived undisposed when the audit
ran ??now carries its full disposition (F4). `py tools/violations.py --due` therefore has nothing new to raise.
?뵎 **HOW TO WAIT FOR YOUR OWN RETROSPECTIVE ??this is what cycles 37 and 38 got wrong and died on.** Background
the bgrun, then hold the turn with repeated **bounded** `py tools/wait_logs.py <task-output-file> --seconds 25`
(flag is `--seconds`, NOT `--max-min`); `guard_bash` refuses any foreground wait over 30 s, which is why a single
long wait fails and why backgrounding-and-exiting kills the child. ?좑툘 `tools/bench/retro.log` is **APPEND-SHARED
across cycles** ??grepping it for `BGRUN END` matches OLD runs; wait on the task's own output file.
`peer.ps1` runs ONLY inside `py tools/bgrun.py ??-- powershell -Command "& 'tools/peer.ps1' ??`. N1's acceptance
and its two caveats are in the lock block; do not re-derive them.

??**DONE IN EARLIER CYCLES ??do NOT redo.** Pointer block relocated verbatim ??`archive/2026-09-19-status-cycle40-close.md` 짠1 (cycle-35 `Count` census 쨌 run 4 + its review 쨌 STEP 0 machinery repairs 5/0 쨌 retrospective-cycle36). Cycle 40's own record is 짠5 of the same file.
?뱦 **Still owed, no gate**: **`doc_ingest.py --full --model opus` has NEVER run, overdue** 쨌 `doc_lint` L6/A4 (47 blank dispositions) 쨌 D0 짠4 pre-read before the first D1 click 쨌 ~57,800-handle reading 쨌 `logclass.is_build_log` counts `wait_logs.py` WAITER logs as builds (that is what blocked run 8 for a cycle) ??deliberately LEFT ALONE under the user's "no more ?μ튂" order, see FOR THE USER 4 쨌 `doc_ingest`'s stale `STATUS.md:10` citations at `CLAUDE.md:352-353` and `docs/violation-decisions.md:333-336` ??cite the user's 08:53 order **by DATE**, never by a STATUS line number, which every relocation moves (done already in `violation-decisions.md:392-393`) 쨌 ?좑툘 **THIS FILE IS 156 LINES vs the ~100 rule.** Cycle 40 relocated four blocks (??`archive/2026-09-19-status-cycle40-close.md`) and that cut CHARACTERS, not lines ??the narrative sits on a few very long single lines, so line-count is the wrong meter for it. What is actually left to move: the `## START HERE` operating hints (lines 12-15) and the hardware banner's envelope numbers (35-39), both of which belong in `docs/`. Do it in a cycle that has a dispatch budget, not at the close of one.
?좑툘 `.claude/agents/material.md:26-29` still mandates the DEAD `MATERIAL=1` prefix, so **every material brief must
carry** `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>`.
?뵶 Carried forward: **`audit_cycle`'s C3/C5 cost figures are PHANTOM ??quote no cost number from that audit.**

### FOR THE USER ??calls to overturn if you disagree
1. ?봽 **I REVERSED HALF OF MY OWN "off permanently" CALL, on measurement.** Cycle 35 said both route-B flags stay False for good. Run 4 confirmed the shift-register half exactly as decided, so `SR_QUEUE_AUTHORISED` stays off for good. But the `Z/dZ` half rested on a "reorder the wire" plan that the machine has now refuted twice ??it has no by-index route, and it was aimed at the wrong cut. So `TEMP_SINK_AUTHORISED` goes **True for that one row, as a test**. It builds nothing new: the path is already written and uses only ops we built weeks ago. Say so if you would rather `Z/dZ` stayed unwired than see that flag on.
1a. ?넅 **Two more rule-1a calls I made rather than stopping the cycle for:** moving the six structures with `GObject.Move` is **scheduling, not computation** (a move carries its frames intact, measured 171??71), so it is allowed; and **N1 does NOT by itself carry the 18 R1 rows** ??it compared the GPU kernel to the CPU one, not the assembled D1 VI, so a D1-level numeric fixture run is still required before D1 is accepted.
1b. ?좑툘 **The two shift registers that moved carry NO initial value**, while the original's are fed by `Initialize Array` (`#8953` w9051 / `#28124` w29122). That may be a real computation change. It applies to all ten registers together, not these two, so I did not wire two of ten ??it must be settled for the whole set before D1 is accepted.
2. ?넅 **A sub-session created `tools/wait_logs.py` and I kept it.** Under `claude -p` a material session had NO permitted way to wait for its own background job ??the `until grep ??sleep` loop its own agent file mandates AND the Monitor tool are both refused by the allow list ??which is exactly the hole that killed two paid peer cells in cycle 33, and which I hit myself this cycle. I judged it plumbing, not one of the process "?μ튂" you told me to stop building. Say if you want it gone, or the allow list widened instead.
4. ?넅 **Cycle 39 ??`Z/dZ` is WIRED and the wire is now MEASURED, not argued.** Your flag call in item 1 paid off:
the source control's own wire 29238 IS the sink wire, exactly one reciprocal source terminal, `Is Broken? False`.
Three calls of mine this cycle you may want to overturn: (a) I **retired a gate** that had failed three runs in a
row ??it demanded `Z/dZ` be wired BEFORE the `#403` reparent, which is the route your own Pre-decided 13a
replaced, so it was asserting a plan we no longer follow; (b) I **deleted the VI-wide remove-broken-wires call
from inside the wiring loop** and put nothing back, because run 5 accidentally proved the point (it never reached
that call and everything wired), and because a reaper that deletes 96 wires mid-build is deleting wires the
original has ??the opposite of the "don't change the computation" rule; (c) when a peer told us to use `net_map`
for a safer per-diagram count, I **refused its own advice** on measurement ??`net_map` calls that same reaper
internally, so following it would have fired the thing we were removing, twice per row. And one I deliberately did
NOT do: `logclass` miscounts waiter logs as builds, which is what blocked run 8, and I left it alone rather than
build past your "no more ?μ튂" order. Say if you would rather that one were just fixed.
4a. You told me to stop building ?μ튂. While you were away I approved a one-line change to the existing watchdog script ??the one that is supposed to notice when LabVIEW has frozen. It has fired six times and been wrong all six times; the latest false alarm was 2026-09-19 04:16, on a job that finished normally at 04:28. Each false alarm blocks the next build until a paid peer review clears it, which has cost $6.16 so far. The change makes the script write its blocking record only when it actually finds a stuck dialog box, and its self-test now passes 8 of 8. I read your order as "stop building NEW machinery", not "leave a broken one breaking things", and I scheduled the fix after the main build launched, never before it. If I read your order wrong, this is the call to overturn.
5. The main build (run 8) ran 30 minutes and every prediction written down beforehand was wrong. I first called that good news because the four rows the predictions named all improved, but a paid review ($4.48) showed the run went backwards overall ??54 wired rows became 53, and 9 failed rows became 12. I had judged the run by only the rows the predictions happened to name; that mistake is now written into the status file. The genuinely useful result: the test that had failed the "Z/dZ" connection four runs in a row was itself wrong ??it demanded the wire count come back unchanged after a temporary helper part is deleted, but the whole purpose of that step is to leave exactly one new wire behind. I did not take the reviewer's word for it; I confirmed in our own code that the connection is made ??it checks out by identity, is not broken, and reads back as the same wire. Second: the one measurement the run existed to produce could not be read, because the command that lists every wire hits the same LabVIEW memory error that crashes the run; the next run will read the individual connection points instead, which is cheaper and tells us more. The old "too many open handles" explanation for that error is dead ??runs were healthy at 51,349 handles and crashed at 35,555. Four saved "crash copies" turned out byte-for-byte identical to the untouched original and were cleared out. The cycle's own review found no violations: "this cycle was run well and was worth its cost." Nothing blocks the next step. One other call you may want to overturn: to clear a gate blocked by a trivial typo in a test, I spent a cheap Gemini review instead of a $4.50 Opus one.
3. **Unchanged from cycle 34, still yours to overturn:** the harness RECORDS all 60 front-panel controls and SETS none (inventing values would be a rule-1a computation change); the VI moved the PI magnet 0 ??30.000 mm under its own control inside 0??9 with `TMX?=39` / `TMN?=0` holding; and I accepted the GPU kernel on the **pre-bead-loss window** ??over the whole fixture max |dy| is 3.135e-05, 31횞 your 1e-6, but all 19 exceedances are bead 4 at k??0023, after that bead's own first loss at k=10018, the other four clean at identical k; plus **1 bead-frame of 50,215** where CPU and GPU sit on adjacent z-lookup indices (k1679, dz ??.667e-03), excluded by the FLIP mask. Say so if any of it is too loose.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

**Verdict: NOT NOVEL.** E1 is clean — nothing in these files refutes it. E2 (the walk-based survival census) is hit four times. Full review below; every finding names a file and line, and none touches E1, the per-bead maths, or the launch command.

---

# PART A — THE DIRECTION

## A1 SETTLED ALREADY — **no finding** (the settlements *authorise* this work)

Both edits are verbatim executions of binding decisions, and the citations check out:

- E1 = `docs/cycle27-plan.md:233-250` (Pre-decided 19, cycle-40 judgement): *"The `Z/dZ` temp-sink bracket's correct Wire-count null is `+1`, NOT `0` — so `build_d1_routeb_v5.py:1842` asserts an inverted null and must read `_b_ok = (_wddelta == 1)`."*
- E2 = `docs/cycle27-plan.md:223-232` (Pre-decided 18 as amended): *"the census may NOT be read with `report_all(Wire)` … assert `wmap(TARGET, d)[node][2][t]["wire"] == claimed_uid` over the four diagrams the build touches (20 / 21 / 24 / 56)."*

A decision that authorises the work is not prior art against it. No slug.

## A2 REFUTED ALREADY — nothing kills E1

I searched for an archived argument that the bracket's null is 0 (that the delete should take the wire with it). There is none; the opposite is measured — `tools/bench/build_d1_routeb_v5_run8.log:358` *"after deleting the temporary sink, #2222 t0 carries wire 29238"*, with `:360` reading (a) True, (c) `Is Broken? False`, (d) 29238 and only (b) failing at +1.

One loose citation, **not** a finding: `build_d1_routeb_v6.py:1608-1609` cites `docs/toolkit-capabilities.md:70` for *"`OpConnectFromWire_v0` only BRANCHES that same net, at delta 0"*. That row records `sink wire 0 → 229 … LoopTunnel 0 → 1` and says nothing about a wire delta; the delta-0-branch sentence is at `:67` (`OpConnectNested_v0`). The claim is independently measured at `…run8.log:356` (`delta 0`), which the comment also cites, so the conclusion stands on its own evidence. Fix the pointer; do not re-open the decision.

## A3 CONTRADICTED (i) — the review E2 rests on contradicts itself, and predictions 2 and 4 inherit both halves

`archive/peer/2026-09-19-routeb-run8-predictions.md` is the accepted source of Pre-decided 18-as-amended. Two of its own paragraphs cannot both be true of run 9:

> `:155` — **"6 → 11 victims is a change in *when* exhaustion arrives, not in *what* fails. The failing call sites are the same."**

> `:175` — **"Cost: at most one walk per diagram actually touched (20, 21, 24, 56) — most already cached at that point … and it degrades gracefully: a diagram that raises leaves its rows `UNREAD` rather than killing the whole census as `:364` did."**

If the fault is an exhaustion state that takes whatever traverse runs next (`:155`), swapping `report_all(Wire)` for other traverse calls at the same point in the same instance changes which call carries the error, not whether the census is readable. The plan's **prediction 2** rests on `:175`; **prediction 4** rests on `:155`. Neither the plan nor Pre-decided 18 reconciles them, so run 9 cannot miss prediction 2 without the disposition having been pre-argued both ways.

## A3 CONTRADICTED (ii) — the artifact contradicts its own gate 16 lines later

`build_d1_routeb_v6.py:1849` is E1: `_b_ok = (_wddelta == 1)`. The message that *reports* that gate was not edited:

- `build_d1_routeb_v6.py:1865` — `f"b(PER-DIAGRAM Wire delta 0)={_b_ok}"`

So if the `Z/dZ` row fails for any reason, run 9's log states the **old, refuted** null as the criterion. This is the shape that has already cost this project a cycle twice: `…run8.log:418` made `Z/dZ` look machine-failed when only the gate was wrong (`docs/cycle27-plan.md:245-247`), and `WIRED 53` was read as a survival count (`docs/cycle27-plan.md:226-227`). One string.

## A4 UNREAD EVIDENCE — none

The two documents bearing on E2 are both cited in the recipe: `archive/peer/2026-09-17-rbw-deleted-wires-run9.md` at `build_d1_routeb_v6.py:1176`, and route A's pattern at `:272-273`. The evidence was read; B4 shows its *consequence* was not carried into the census's readout. No slug.

---

# PART B — THE ARTIFACT

## B2 ALREADY FAILED — this census, at this point, has already failed, for a cause E2 does not remove

Attempted at `tools/recipes/build_d1_routeb_v5.py:2125`, run 8:

> `tools/bench/build_d1_routeb_v5_run8.log:364` — *"S3w K3 SURVIVAL CENSUS UNREAD (RuntimeError: report_all(Wire) … error 2 … Traverse for GObjects.vi->OpReportAll_v0.vi …) — reported, not hidden; 50 uid(s) had been claimed"*

The recorded cause is **not** "`report_all(Wire)` is too big" — it is the traverse layer, proved on three call sites with no `Wire` class involved: `…run8.log:419-429` (ten rows killed by `report_all(Diagram)`, one by `report_all(WhileLoop)`) and `…run8.log:432`/`:454` (`count(LoopTunnel)` → `OpReport_v3.vi`, Traverse Failed). All eleven of those rows are processed **immediately before** the census point — the ledger prints after the row loop (`v6:2125-2127`).

E2 keeps that layer at that same point and adds to it:

| E2 call | what it runs | measured status at the census point |
|---|---|---|
| `diag_index(TARGET,_du)` ×4 — `v6:2155` | `[o["uid"] for o in g.report_all(target,"Diagram")]` — `build_d1_v0.py:357-358`, `gscript.py:488-504` | the **dominant error-2 victim**, 10 rows, `…run8.log:419-429` |
| `wmap(TARGET,_di,fresh=True)` ×4 — `v6:2164` | `build_track_v6_core.py:84-92` = one `node_labels` + up to 80 `node_terms_uid`, each a `Class Name='Diagram'` traverse op (`gscript.py:587-605`, `:870-895`) | same op family; ~0.8 s per node call already measured (`build_d1_v0.py:365-368`) |

Two cheap closures:

1. **The cache the peer assumed is not used.** `:175` says *"most already cached at that point"*; `v6:2164` passes `fresh=True`, re-walking all four. `fresh=True` re-walking is already on record as a candidate cause of the 6 → 11 worsening (STATUS NEXT, on K2's `:1613`).
2. **The four indices are already in hand** — resolved repeatedly during the pass (`v6:1600`, `:1668-1669`, `:2033-2034`) and printed as `D[24]`/`D[20]`/`D[21]`/`D[56]` in every ledger row (`…run8.log:365-417`). Caching them removes four `report_all(Diagram)` calls without changing what the census measures.

**And if `diag_index` raises for all four, the census does not report UNREAD — it reports a number.** `v6:2157` logs "has NO index" and `continue`s, `_maps` stays empty, every row falls through `:2179-2186` with `_read=None`, `_hit=False`, into `_bad`; the headline at `:2194-2196` then reads *"53 wire uid(s) claimed … 0 READ BACK AT THE CLAIMED TERMINAL, 53 did NOT"* — a total-loss verdict produced by an unread instrument. That is precisely the failure Pre-decided 18 exists to end (`docs/cycle27-plan.md:226-227`), sign-flipped.

## B4 ALREADY MEASURED — "the uid at this terminal changed" has already been measured NOT to mean "the wire is gone"

E2's comparison is `_hit = (_read == _u)` (`v6:2186`). Route A ran the identical comparison — `next((x["wire"] for x in g.node_terms(TARGET, sd, sn) if x["i"]==st), 0) == wire` (`tools/recipes/build_d1_v0.py:1119-1121`) — and its verdict was measured wrong:

> `tools/bench/build_d1_v0_run9.log:268-269` — *"8 made, 5 SURVIVED … 3 deleted by it"*, of which `RBW-DELETED #1359 t4 '' <- same-loop 8885  wire 26189 -> 26412` — a **non-zero** wire.

> `archive/peer/2026-09-17-rbw-deleted-wires-run9.md:88` — *"That terminal was not observed becoming disconnected. The classifier called it 'deleted' solely because its current wire object differed. Therefore '3 deleted by RBW' is not established."* `:90` — *"The strongest alternative is net canonicalization plus index drift."*

> `docs/toolkit-capabilities.md:68` — *"the 'survives RBW' check at `build_d1_v0.py:1118-1121` IS uid equality … it measures object identity, not survival. **Do not cite RBW-survival as evidence a wire is good.**"* — and, on this very build's wires, *"LabVIEW creates the border tunnels itself (`LoopTunnel 0 → 2`, wire delta 3), so the sink and source wire uids **differ** — a cross-boundary wire is several segments."* Route B makes exactly those (`…run8.log:388`, `:396`, `:406`).

v6 is **better instrumented** than route A — it prints what the terminal actually reads and where the claimed uid is seen (`:2197-2199`) — so the fix is confined to the headline: a terminal carrying a *different non-zero* wire is a third category (re-segmented/canonicalised), not a member of `_bad`, and `:2194-2196` must not become quotable as "N wires survived".

## B3 HELPER EXISTS — `_tag_addr` re-parses an address `sink_addr` already returned

`v6:2141-2150` recovers `(sink uid, terminal index)` by splitting the formatted ledger tag, then re-finds the diagram by scanning `_maps` (`:2181-2185`). The row loop already holds it: `sink_addr(...)` returns *"(body diagram index, node index, terminal index) for a sink, re-resolved NOW"* (`v6:1173-1177`), printed as `D[{d}].N[{n}].T[{t}]` at `:1870`. `claim_wire(tag, kind, uid)` (`:1130-1137`) simply does not carry it. Cost of the hand-roll: any tag not in `#<uid> t<i>` shape yields `_su=None → _read=None → _bad`, indistinguishable from destruction — the same conflation as B2. Passing `(d,n,t)` at the ten `claim_wire` sites (`:1227`, `:1478-1479`, `:1581`, `:1869`, `:1941`, `:2005`, `:2073`, `:2109`) removes the parser, the `RETARGET` re-application at `:2180` and the `_maps` scan.

## B1 ALREADY BUILT — the pattern, yes; the recipe says so

`build_d1_v0.py:1115-1128` is the same check and `v6:272-273` names it. Folded into B3 — the objection is the hand-rolled address, not the pattern.

---

## What releases each finding

- **A3(i)** — reconcile `:155` with `:175` in one sentence in the plan (e.g. "an UNREAD census while traverse is already failing is a result, not a prediction miss"), or refute one.
- **A3(ii)** — one string at `v6:1865`.
- **B2** — cache the four already-resolved diagram indices; report an unwalked diagram's rows as `UNREAD`, never `MISMATCH`.
- **B4** — split "terminal carries a different non-zero wire" out of `_bad` in `:2194`.
- **B3** — carry `(d,n,t)` in `claim_wire`, or show a row kind where it is unavailable.

```
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: already-failed
PRIOR-ART: already-measured
PRIOR-ART: helper-exists
```

I took no lock, opened no VI, built and ran nothing; every claim is a read of `docs/cycle27-plan.md`, `docs/toolkit-capabilities.md`, `tools/recipes/build_d1_routeb_v{5,6}.py`, `tools/recipes/build_d1_v0.py`, `tools/recipes/build_track_v6_core.py`, `tools/gscript.py`, `tools/bench/build_d1_routeb_v5_run8.log`, `tools/bench/build_d1_v0_run9.log` and the two archived peer files cited. (The plan file could not be written — the Write tool is disabled this session — so this reply is the review.)

## Sources

(extract from answer)

## What was done with it

**ALL FIVE FINDINGS ACCEPTED AS RIGHT; NONE REFUTED.** Disposed by the cycle-41 judgement session and applied
by its material session 2026-09-19 05:2x. The two `contradicted` findings are disambiguated below by their
A3 sub-number, because one slug covers two different contradictions.

FIXED: contradicted - STATUS.md:79 - A3(i): the run-8 review's `:155` ("same failing call sites, only later")
and `:175` ("most already cached, degrades gracefully") were the two halves old predictions 2 and 4 rested on,
so the `## NEXT` PREDICTIONS block is replaced by five predictions whose P5 makes the contradiction itself the
discriminator - `error 2` victim count >= 6 keeps the `:155` half, a count below 6 refutes it and makes
traverse VOLUME the driver.
FIXED: contradicted - tools/recipes/build_d1_routeb_v6.py:1883 - A3(ii): the J2 failure string still printed
`b(PER-DIAGRAM Wire delta 0)` while `_b_ok` demanded `_wddelta == 1`, so it asserted the very null E1 exists to
remove; the label now reads `b(PER-DIAGRAM Wire delta +1, ONE new wire is what the bracket makes)`, and the E1
comment's mis-citation of `docs/toolkit-capabilities.md:70` is corrected to `:67` at `:1623`.
FIXED: already-failed - tools/recipes/build_d1_routeb_v6.py:2160 - B2: the census no longer folds "that diagram
was never walked", "that address will not resolve" and "the terminal is bare" into one list - the four diagrams
are walked ONCE each inside their own try/except that stores the map or the exception text, every row is
classified UNREAD / BARE / EXACT / SEGMENTED, UNREAD is never counted as a lost wire, and the census cannot
raise, so a dead traverse can no longer print a false "0 survived".
FIXED: already-measured - tools/recipes/build_d1_routeb_v6.py:2242 - B4: a terminal reading a DIFFERENT
NON-ZERO uid is now the SEGMENTED bucket and counts as survival (a cross-boundary wire is several segments,
`docs/toolkit-capabilities.md:68`), so uid inequality is no longer reported as a mismatch or a failure; the
headline "survived" number is EXACT + SEGMENTED.
FIXED: helper-exists - tools/recipes/build_d1_routeb_v6.py:1147 - B3: `claim_wire` now stamps every ledger row
with the (diagram index, sink node uid, terminal index) address `sink_addr` already resolved for that row
(parked at `:1217`), with no change at any of the ten call sites; the hand-rolled `_tag_addr` tag parser is
demoted to a fallback whose failure yields UNREAD rather than a phantom destroyed wire.
