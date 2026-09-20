# priorart-d1-routeb-run10

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.6462  in 50 / out 33726 / cache-create 298542 / cache-read 3634733  (468s, 43 turn(s))
- **date:** 2026-09-19 06:42:42
- **outcome:** ANSWERED (469s)
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
# UNDER REVIEW ??`tools/recipes/build_d1_routeb_v7.py`, D1 route-B RUN 10

## What the artefact is

`tools/recipes/build_d1_routeb_v7.py` was cut BYTE-EXACT from `tools/recipes/build_d1_routeb_v6.py`
(v6 md5 `cb96a4df0ef71325880ff63aed47e8b9`, sha256 `8dbb1e69ef83??, 2607 lines ??verified before the cut)
and carries **exactly one logic change**, plus a docstring prediction contract.

v7: md5 `c30f8ade3ce3a23645d2c779a9edcac1`, sha256 `d808e10ce4c152cba8e56a6f526af9351699396879a8cca0e598cc4351d9d692`,
2699 lines, `ast.parse` + `py_compile` clean. Diff vs v6: **92 lines added, 0 removed, 2 insert hunks** ??
`v7:308-330` (docstring, the run-10 prediction contract) and `v7:2170-2238` (the code block below).
No existing line of v6 was modified or deleted. `gate()` call sites 52 ??54.

## The ONE change ??E3

Binding decision: `docs/cycle27-plan.md` **Pre-decided 20** (cycle-41 judgement session), and STATUS.md's
`## NEXT` block. Immediately after the S3w PRE-SETTLE ledger line (`v7:2167-2168`) and **before** the
four-bucket survival census (`v7:2239-??), v7 now:

1. `g.save(TARGET, allow_broken=True)` ??saves the mid-restructure working copy (a VI at ExecState 0 is
   diverted to `gscript.gui_save`, because COM `SaveInstrument` blocks forever on a broken VI,
   `tools/gscript.py:1982-2068`); records size + md5.
2. `g.close_panel(TARGET)`, then `g.reset()` ??releases every COM proxy this process holds **while the
   instance is still alive** (`tools/gscript.py:262-269`).
3. Restarts LabVIEW by running the EXISTING `tools/lv_restart.py` as a subprocess (standing restart
   authority, CLAUDE.md 짠3). This recipe already called that script twice before this edit
   (`preload_reread`, and `main()` under `--restart`).
4. `g.reset()` again + `build_d1_v0._WALKS.clear()` ??rebinds the Application dispatch, empties the op-VI
   reference cache and the cached diagram walks, all of which named the dead instance.
5. `g.ensure_loaded(TARGET)` ??reopens the SAVED copy in the fresh instance (no preload of the original:
   the census needs diagram walks, not `ExecState` ??Pre-decided 16b/20).
6. Two new gates: (a) the reopened copy's md5 equals the md5 it was saved with; (b) `_CENSUS_FRESH` ??the
   census below really is running in a fresh instance.

The existing four-bucket census then runs **unchanged in logic**, and everything downstream of it
(`settle_index_modes`, S4, S5) continues against the reopened copy in the fresh instance.

**No fallback.** If the restart or the reopen raises, `_CENSUS_FRESH` stays False, the new gate FAILS, the run
ends rc=1 and says why. Pre-decided 20 explicitly forbids falling back to a same-instance census and quoting
it as the measurement.

## Why this edit and not another

- `error 2` is the only thing between route B and a delivered D1. Across runs 8 and 9 **every victim is a
  traverse** (`Traverse for GObjects.vi`): `report_all(Diagram)`, `report_all(WhileLoop)`,
  `report_all(Wire)`, `count(LoopTunnel)`.
- The handle-count explanation is **refuted**: healthy at 51,349 / 51,353 handles, crashed at 35,551 / 35,555
  (`archive/peer/2026-09-19-routeb-run8-predictions.md` Q3).
- The census instrument is **not** the cause: cycle 40 blamed `report_all(Wire)` and replaced it with the
  walk-based census; run 9's replacement died the same death five times
  (`tools/bench/build_d1_routeb_v6_run9.log:364`).
- The one asymmetry two runs agree on is **temporal within a run**: the same diagram walks that wire 54 rows
  early all fail by census time. A fresh instance is the only untried lead, it is the only route to a census
  that can READ, and it is simultaneously the discriminating test of the cumulative-allocation hypothesis.

## PREDICTIONS registered before the run

- **R1** the census READS in the fresh instance: UNREAD falls from run 9's 51 to 0.
- **R2** `BARE = 0` ??a real test this time rather than a vacuous one.
- **R3** the 11 `error 2` ledger rows still FAIL (the wiring pass is unchanged and still runs in one instance).
- **R4** `Z/dZ` t0 still PASSES J2 at `_wddelta == 1`; `#2222` t0/t2/t3/t4/t5 stay WIRED.
- **R5** the S3w save succeeds and the reopened copy's md5 equals what was written.
- Gate arithmetic: 80 PASS / 0 FAIL in run 9 ??**82 PASS / 0 FAIL** on a clean run 10.

## ALREADY RULED OUT ??do not re-raise these

1. **"Fix the census by reading each wire at claim time."** `docs/cycle27-plan.md` Pre-decided 18 forbids it:
   a claim-time read is an attempt count with extra steps; a survival census must be read AFTER the wiring pass.
2. **"It is the handle count."** Refuted by measurement (above, Q3). Never attribute `error 2` to handles.
3. **"Swap the census instrument again."** Done in cycle 40 and it died identically in run 9.
4. **The K1 scratch-copy separator and Pre-decided 17/19** are CLOSED by replication 2 횞 2 and by run 9's
   machine confirmation of the `Z/dZ` row; they are not re-opened here.

## What I am asking

Has this project ALREADY tried, measured, refuted or decided against a **mid-run LabVIEW restart inside a
build recipe** ??saving a mid-restructure working copy, restarting, reopening it in the fresh instance, and
continuing the same build against it? And is anything in our own files evidence that this specific edit cannot
produce a readable census (e.g. a measured failure to reopen a broken-saved copy, a recompile spin, a
`gui_save` that wrote a stale file after `error 2`, or a known cross-instance uid/index instability that would
make the reopened copy's diagram indices differ from the ones the ledger recorded)?


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
  status: released   # ?뵷 **D1 ROUTE-B v6 RUN 9 RAN, 2026-09-19 05:31 ??06:01 KST** ??`tools/bench/build_d1_routeb_v6_run9.log`, `BGRUN END rc=1 after 1817s` (`:509`), **80 PASS / 0 FAIL**. **ALL FIVE PREDICTIONS HELD.** Ledger `:363` 66 attempted / **54 WIRED** / 11 FAILED / 1 NO-ROUTE (all 11 FAILED carry `error 2`, `:473-:483`). `CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:365`) ??the census RETURNED and did NOT print a false zero: `diag_index` itself calls `report_all(Diagram)`, which `error 2` killed for all five diagram uids (`:364`), exactly the review's B2 finding, so every row is UNREAD, never BARE. `Z/dZ` t0 **PASSES J2 with per-diagram delta +1** (`:360`: a=True w29238=w29238, 1 reciprocal source; b=True Diagram[24] 31??2 delta 1, VI-wide 1937??938; c=`Is Broken? False`; d=29238) and is WIRED (`:464`). `#2222` t2/t3/t4/t5 all WIRED (`:465-:468`). Original md5 `2a78e17c?? unchanged (`:13`, `:494`); ExecState S1 cold 0 = UNREAD (`:37`), live copy PRELOADED 1 (`:491`). Run 9's own crash is still `count(LoopTunnel)` in `settle_index_modes` (`:486`, `:508`). PREVIOUS: **D1 ROUTE-B v5 RUN 8 RAN, 2026-09-19 03:58:14 ??04:28:36** ??`tools/bench/build_d1_routeb_v5_run8.log`, `BGRUN END rc=1 after 1822s`, **80 PASS / 0 FAIL**. ?뵶 **EVERY PREDICTION MISSED**: `#2222` t3/t4/t5 all WIRED (`:411-:413`), `Z/dZ` t0 FAILED on J2 reading (b) with per-diagram delta **+1** (`:418`); ledger 66/53/12/1 (`:363`); K3's SURVIVAL CENSUS **UNREAD** ??`report_all(Wire)` died of `error 2` (`:364`); the same `error 2` crash in `settle_index_modes` at 35,555 handles (`:431-:432`), victims 6 ??**11**. Original md5 unchanged (`:13`, `:440`). Its mandatory failed-prediction review is IN and **UNDISPOSED**: `archive/peer/2026-09-19-routeb-run8-predictions.md` (ANSWERED, claude/hypothesis opus max, $4.4847, 676 s) ??it calls run 8 a **regression** (WIRED 54 ??53, FAILED 9 ??12), says the `+1` is the wire the bracket exists to create so **the J2(b) null is inverted**, and identifies `error 2` as LabVIEW **"Memory is full"** with the handle count neither cause nor symptom. FULL RECORD ??`archive/2026-09-19-status-cycle39-run8.md` 짠7 (run 8) 쨌 짠4 (run 7) 쨌 짠5 (cycle 38) 쨌 짠6 (cycle-37 machinery) 쨌 짠3 (v5 build) 쨌 짠1/짠2 (runs 6 and 5).
  owner:     # RELEASED 2026-09-19 06:01 KST ??run 9 ended `BGRUN END rc=1 after 1817s`, log `tools/bench/build_d1_routeb_v6_run9.log`. Acquired 2026-09-19 05:31 KST by the cycle-41 material session for **D1 ROUTE-B v6 RUN 9** ??`py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v6_run9.log -- py -u tools/recipes/build_d1_routeb_v6.py`. v6 sha256 `8dbb1e69ef83??, md5 `cb96a4df0ef71325880ff63aed47e8b9`, 2607 lines, `ast.parse` OK. Prior-art gate RELEASED (five `FIXED:` lines in `archive/peer/2026-09-19-priorart-d1-routeb-run9.md`, stop record RELEASED). Previous: released 2026-09-19 04:28 KST after run 8 ended (BGRUN END rc=1 after 1822s).
  purpose_c41:   # ?뵶 **CYCLE 41, 05:0x-05:22: `tools/recipes/build_d1_routeb_v6.py` IS CUT AND SYNTAX-CLEAN (sha256 `07c6b5d6a37e??, md5 `9035029214449dd893ce56ab53618b56`, 2551 lines, `ast.parse` OK) ??E1 at `:1849` (`_b_ok = (_wddelta == 1)`) + comment `:1601-1613`, E2 at `:2128-2215` (walk-based census). RUN 9 WAS NOT LAUNCHED AND NO LOCK WAS TAKEN: the prior-art gate stopped it.** `archive/peer/2026-09-19-priorart-d1-routeb-run9.md` (ANSWERED, opus/high, $4.2179, 404 s; log `tools/bench/priorart_d1_routeb_run9.log` `BGRUN END rc=0 after 405s`) = **NOT NOVEL**, 5 findings / 4 slugs ??`contradicted` 횞2 (A3(i) the run-8 review's `:155` vs `:175`; A3(ii) the unedited failure string `v6:1865` still says "delta 0"), `already-failed` (B2: the census point already kills `report_all(Diagram)`, which `diag_index` 횞4 calls), `already-measured` (B4: uid inequality ??wire gone), `helper-exists` (B3: `sink_addr` already returns (d,n,t)). E1 is CLEAN ??"nothing in these files refutes it". `stop_record` now refuses the run-9 launch (measured: reviewed sha `07c6b5d6a37e`, no release line). Writing `REFUTED:`/`FIXED:` is JUDGEMENT's call.
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
?? **FIRST ACT ??BUILD AND LAUNCH RUN 10 as `tools/recipes/build_d1_routeb_v7.py`, cut from v6's bytes** (v6 md5
`cb96a4df0ef71325880ff63aed47e8b9`, sha256 `8dbb1e69ef83??, 2607 lines). **Binding: `docs/cycle27-plan.md`
Pre-decided 20**, which carries the full reasoning ??read it, do not re-derive it. **ONE edit; do not add a second,
and do not touch the per-bead maths (rule 1a):** immediately after the S3w ledger line (`v6:2125-2127`), **save the
working copy, close it, RESTART LabVIEW (standing authority, CLAUDE.md 짠3), reopen the saved copy in the fresh
instance, and run the existing four-bucket census (`v6:2160-2256`) there.** Nothing else changes.
Arm AND release a stop record for v7's own sha, then:
`py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v7_run10.log -- py -u tools/recipes/build_d1_routeb_v7.py`
**WHY THIS ONE EDIT AND NOT ANOTHER**: it is the only route to a census that can READ, *and* it is simultaneously
the discriminating test for the cumulative-allocation hypothesis STATUS has carried UNCONFIRMED for two cycles.
Either answer is worth the run. ?좑툘 Do **not** "fix" the census by reading each wire at claim time ??that is an
attempt count with extra steps, and Pre-decided 18 exists to forbid it.
**PREDICTIONS for run 10** ??any miss ??failed prediction ??`-Agent claude -Role hypothesis` SINGLE arm
(Pre-decided 7):
**R1.** The census READS in the fresh instance: UNREAD falls from 51 to 0.
**R2.** `BARE = 0` ??and this time it is a real test rather than a vacuous one.
**R3.** The 11 `error 2` ledger rows still FAIL: the wiring pass is unchanged and still runs in one instance.
**R4.** `Z/dZ` t0 still PASSES J2 and `#2222` t0/t2/t3/t4/t5 stay WIRED.
**R5.** The S3w save succeeds and the reopened copy's md5 equals what was written.
?좑툘 **EXPECT THIS AND DO NOT DIAGNOSE IT COLD ??retrospective-cycle41 F4's named residual risk.** `guard_peer` may
read run 9's `rc=1` log as an UNDISCHARGED failing build and refuse the run-10 build until a review newer than that
log is archived. **That refusal would be wrong on the merits and the answer is a written disposition, not a paid
review**: run 9 missed NO prediction, its `error 2` crash class was already reviewed at $4.48 in run 8's mandatory
review (`archive/peer/2026-09-19-routeb-run8-predictions.md`, ANSWERED), and this cycle PRE-REGISTERED its recurrence
as prediction P5, which HELD. If the gate fires, cite those three facts; buy a second hypothesis arm only if it
refuses them. `CYCLE_GUARD_OFF` is never the answer.
?좑툘 **RUN 9 RAN, CRASHED `rc=1` BEFORE S5 ??AND NO PREDICTION MISSED.** Lead with the crash, never with the gate
score: retrospective-cycle41 F6(a) found the earlier "80 PASS / 0 FAIL" headline is the sentence that gets quoted,
and it is the same fault class as cycle 40's "judged run 8 by the rows its predictions named". The run never reached
S5, so **it produced no VI**. `tools/bench/build_d1_routeb_v6_run9.log`, `BGRUN END rc=1 after 1817s`
(`:509`), 80 PASS / 0 FAIL gates, ledger `:363` **66 attempted / 54 WIRED / 11 FAILED / 1 NO-ROUTE** ??run 8's
regression is REVERSED (WIRED 53 ??54, FAILED 12 ??11). Original md5 `2a78e17c?? UNCHANGED `:13`/`:494`; nothing
saved, nothing run. ExecState S1 cold 0 = UNREAD `:37`, live copy PRELOADED 1 `:491`. No failed-prediction review
is owed.
??**E1 SETTLED THE `Z/dZ` ROUTE ON THE MACHINE** ??t0 **PASSES J2** at `_wddelta == 1` (`:360`), logged WIRED
(`:464`): identity True (w29238 is both the control's own wire and the sink wire, exactly one reciprocal source
terminal), Diagram[24] delta `(31,32,1)`, `Is Broken? False`, sink read back 29238. **`#2222` t0/t2/t3/t4/t5 ALL
WIRED** (`:464-:468`, `Is Broken? FALSE` on t3 and t4).
?뵶 **BUT P2 DID NOT PASS ??IT WAS UNTESTED, AND THAT DISTINCTION IS THIS CYCLE'S MAIN RESULT.** The census printed
`CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:365`) because all five `diag_index` calls raised
`report_all(Diagram) ??error 2` (`:364`). So `BARE = 0` is **VACUOUS** and **route B's `WIRED 54` is STILL an
attempt count**, exactly as after run 8. Do not quote it as survival (Pre-decided 18 as amended).
??**THE PRIOR-ART GATE PAID FOR ITSELF** ??`archive/peer/2026-09-19-priorart-d1-routeb-run9.md` (NOT NOVEL,
opus/high, $4.2179, 5 findings, all accepted, applied and released with `FIXED:` lines). B2 predicted that the
census as first cut would print a confident `0 survived / 51 gone` when its own walks died; B4 that uid inequality
is not wire death on cross-boundary wires. Run 9 hit B2's failure exactly ??and reported **51 UNREAD** instead of a
phantom wiring catastrophe. Contract now in Pre-decided 18.
?뵶 **`error 2` IS NOW THE WHOLE BLOCKER.** Run 9: **11 ledger rows** (`:473-:483`, 10 횞 `report_all(Diagram)` +
1 횞 `report_all(WhileLoop)`), **5 more** inside the census's `diag_index` (`:364`), and the terminal
`count(LoopTunnel)` crash in `settle_index_modes` (`:486`, `:508`) that makes rc=1 ??so **no route-B run has ever
reached S5, and none has ever produced a saved D1 VI.** Every victim across runs 8 and 9 is a **traverse**
(`Traverse for GObjects.vi`), whatever the class. **Never attribute it to a handle count**: healthy at
51,349 / 51,353, crashed at 35,551 / 35,555 (`archive/peer/2026-09-19-routeb-run8-predictions.md` Q3). The live
hypothesis ??cumulative allocation failure inside one instance ??is UNCONFIRMED and run 10 is its test.
??**CLOSED THIS CYCLE ??do not re-open:** Pre-decided **19** (`Z/dZ`) is machine-confirmed 쨌 Pre-decided **17** is
confirmed by replication 2 횞 2 (runs 6/7 with the in-loop reaper lost `#2222`'s terminals; runs 8/9 without it
wired every one) and **the K1 scratch-copy separator is RETIRED** ??it would only confirm what two builds already
replicate 쨌 Pre-decided **18** is amended with the four-bucket census contract. Run 8's narrative ??
`archive/2026-09-19-status-cycle39-run8.md` 짠7; cycle-39 chain ??`archive/2026-09-19-status-cycle39-judgement.md`.
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
?뱦 **Still owed, no gate**: **`doc_ingest.py --full --model opus` has NEVER run, overdue** 쨌 `doc_lint` L6/A4 (47 blank dispositions) 쨌 D0 짠4 pre-read before the first D1 click 쨌 ~57,800-handle reading 쨌 `logclass.is_build_log` counts `wait_logs.py` WAITER logs as builds (that is what blocked run 8 for a cycle) ??deliberately LEFT ALONE under the user's "no more ?μ튂" order, see FOR THE USER 4 쨌 `doc_ingest`'s stale `STATUS.md:10` citations at `CLAUDE.md:352-353` and `docs/violation-decisions.md:333-336` ??cite the user's 08:53 order **by DATE**, never by a STATUS line number, which every relocation moves (done already in `violation-decisions.md:392-393`) 쨌 ?좑툘 **THIS FILE IS 176 LINES vs the ~100 rule ??PARTLY ADDRESSED, NOT FIXED.** Retrospective-cycle41 rejected the previous entry's defence ("line-count is the wrong meter for it") as *a rationale for breaking rule 4, not a repair of it*, and that is accepted: do not restate it. Cycle 41 relocated `FOR THE USER` items 1/4/4a/5 verbatim (??`archive/2026-09-19-status-cycle41-user-items.md`), which removed ~17 lines of resolved narrative; the file still reads 176 because the same cycle added its own record. **What is left to move, and it is now the ONLY way this file gets under the rule:** the `## START HERE` operating hints (lines 12-15) and the hardware banner's envelope numbers (lines 35-39) ??`docs/`. Both are reference material, not state. Do it in a cycle that has a dispatch budget, not at the close of one.
?윟 **DECIDED cycle 41, do not chase it:** `doc_lint` now reports ONE new L2 dangling ??`STATUS.md:61` naming
`tools/recipes/build_d1_routeb_v7.py`, which run 10 has not cut yet (`doc_lint.py:182` exempts forward references
only in `*-plan.md`). **Leave it.** Naming the exact file the next cycle must cut is what NEXT is for, the reference
self-clears the moment run 10 cuts v7, and widening the exemption to STATUS would be building machinery to silence a
warning that is correct. ??Also cycle 41: gemini's Q2 `$record` census is CLOSED with **no defect and no change** ??
every consumer in `tools/lv_stallcheck.ps1` after `:273` is either behind the same branch that sets the sentinel
(`:273`, `:285`, `:286`) or pure interpolation (`:291`); there is no truthiness test anywhere. The only effect is
cosmetic: `:291` can print `STALL RECORD written: NOT WRITTEN - ??. ??`doc_ingest --cycle 41` named three citation
contradictions and all three are FIXED (`CLAUDE.md:55` ASI envelope now points at this banner instead of restating
"~1 mm"; `CLAUDE.md:353` cites the ?μ튂 order by DATE; `docs/cycle27-plan.md:84`'s stale "STATUS OPEN 54" pointer
dropped).
?좑툘 `.claude/agents/material.md:26-29` still mandates the DEAD `MATERIAL=1` prefix, so **every material brief must
carry** `py tools/bgrun.py --material --max-min N --log tools/bench/<name>.log -- py -u <script>`.
?뵶 Carried forward: **`audit_cycle`'s C3/C5 cost figures are PHANTOM ??quote no cost number from that audit.**

### FOR THE USER ??calls to overturn if you disagree
?뱚 **Items 1, 4, 4a and 5 are RESOLVED and relocated VERBATIM ??`archive/2026-09-19-status-cycle41-user-items.md`** (rule 4, answering retrospective-cycle41's L3; each carries its outcome there). In short: the `TEMP_SINK_AUTHORISED` test succeeded and `Z/dZ` is confirmed 쨌 the cycle-39 reaper call is confirmed by replication 2 횞 2 쨌 the watchdog repair's follow-up question closed with no defect 쨌 the cycle-40 report is superseded by item 6 below. The items below are the ones still open to you.
1a. ?넅 **Two more rule-1a calls I made rather than stopping the cycle for:** moving the six structures with `GObject.Move` is **scheduling, not computation** (a move carries its frames intact, measured 171??71), so it is allowed; and **N1 does NOT by itself carry the 18 R1 rows** ??it compared the GPU kernel to the CPU one, not the assembled D1 VI, so a D1-level numeric fixture run is still required before D1 is accepted.
1b. ?좑툘 **The two shift registers that moved carry NO initial value**, while the original's are fed by `Initialize Array` (`#8953` w9051 / `#28124` w29122). That may be a real computation change. It applies to all ten registers together, not these two, so I did not wire two of ten ??it must be settled for the whole set before D1 is accepted.
2. ?넅 **A sub-session created `tools/wait_logs.py` and I kept it.** Under `claude -p` a material session had NO permitted way to wait for its own background job ??the `until grep ??sleep` loop its own agent file mandates AND the Monitor tool are both refused by the allow list ??which is exactly the hole that killed two paid peer cells in cycle 33, and which I hit myself this cycle. I judged it plumbing, not one of the process "?μ튂" you told me to stop building. Say if you want it gone, or the allow list widened instead.
5a. ?윞 **STILL YOURS TO OVERTURN, carried out of relocated item 5**: to clear a gate blocked by a trivial typo in a test, I spent a cheap Gemini review instead of a $4.50 Opus one.
6. ?넅 **CYCLE 41 (2026-09-19, run 9)** ??written by `peer.ps1 -Kind prose` (`archive/prose/2026-09-19-c41-user-report.md`), shown as-is:
吏?쒕갇 ???ㅽ뿕 VI瑜??먮룞?쇰줈 留뚮뱶???묒뾽??30遺??숈븞 ?뚯븯?듬땲??9踰덉㎏ ?ㅽ뻾). ?대? ?먭? 80媛쒕뒗 ?꾨? ?듦낵?덇퀬 ?ㅽ뙣???놁뿀?듬땲?? 諛곗꽑 ?곌껐? 66媛쒕? ?쒕룄?댁꽌 54媛쒓? ?곌껐?섍퀬 11媛쒓? ?ㅽ뙣?덉쑝硫?1媛쒕뒗 寃쎈줈瑜?李얠? 紐삵뻽?듬땲?? 吏곸쟾 ?ㅽ뻾??53媛??깃났, 12媛??ㅽ뙣??쇰땲 吏???ъ씠?댁뿉 ?룰구?뚯낀??寃껋씠 ?대쾲???ㅼ떆 ?뚮났???덉엯?덈떎.
??踰??곗냽 ?ㅽ뙣濡?蹂닿퀬?섎뜕 "Z/dZ" ?곌껐? ?뚭퀬 蹂대땲 ?곌껐???꾨땲??寃??履쎌씠 ?섎せ?댁뿀?듬땲?? 洹??④퀎???먮옒 ???좎쓣 ?뺥솗???섎굹 ?④린??寃껋씠 紐⑹쟻?몃뜲, 寃?щ뒗 ?좎쓽 媛쒖닔媛 蹂?섏? ?딆븘???쒕떎怨??붽뎄?섍퀬 ?덉뿀?듬땲?? ?대쾲 ?ъ씠?댁뿉 寃?щ? 怨좎낀怨? ?댁젣 湲곌퀎媛 洹??곌껐????媛吏 ?낅┰?곸씤 諛⑸쾿?쇰줈 ?뺤씤?⑸땲?? ?묒そ ?앹씠 媛숈? ?좎씤吏, ?딆뼱吏吏 ?딆븯?붿?, ?쒕?濡??쏀엳?붿?, 洹몃━怨?媛쒖닔媛 ?뺥솗???섎굹 ?섏뿀?붿??낅땲?? ??臾몄젣???댁젣 醫낃껐?섏뿀?듬땲??
?ㅻ쭔 ?대쾲 ?ㅽ뻾???먮옒 ?살쑝?ㅻ뜕 ???섎굹??痢≪젙媛믪? ?쎌? 紐삵뻽?듬땲?? 54媛쒖쓽 ?좎씠 ?쒕룄留???寃껋씠 ?꾨땲???ㅼ젣濡??댁븘?⑥븯?붿? ?뺤씤?섎젮硫??ㅼ씠?닿렇????媛쒖쓽 ?댁슜???섏뿴?댁빞 ?섎뒗?? ?ㅼ꽢 踰??쒕룄 紐⑤몢 硫붾え由щ굹 李몄“ ?좊떦 臾몄젣瑜??삵븯??LabVIEW??"error 2"濡?二쎌뿀?듬땲?? 洹몃옒???ㅽ뻾 寃곌낵?먮뒗 ?レ옄 ???"51 unread"媛 湲곕줉?섏뿀怨? 54?쇰뒗 ?レ옄???ъ쟾???앹〈 媛쒖닔媛 ?꾨땲???쒕룄 媛쒖닔?낅땲?? ?ㅽ뻾 ?꾩뿉 $4.22瑜??ㅼ뿬 ?뚮┛ ?먮룞 寃?좉? ?뺥솗?????ㅽ뙣瑜??덉륫?덇퀬, 泥섏쓬 ?묒꽦??肄붾뱶?濡쒕씪硫?"0 survived, 51 gone"?대씪??嫄곗쭞 李몄궗瑜?蹂닿퀬?덉쓣 寃껋씠?쇰뒗 ?먮룄 ?덉륫?덉뒿?덈떎. 洹몃옒??"?쎌쓣 ???놁쓬"怨?"?щ씪吏????곕줈 蹂닿퀬?섎룄濡?誘몃━ 怨좎낀怨? 洹??뺣텇??吏?쒕갇 寃곌낵媛 臾댁꽌???ㅻ떟???꾨땲???뺤쭅??怨듬갚???섏뿀?듬땲?? ?댁젣 "error 2"留뚯씠 ?⑺뭹??留됯퀬 ?덉뒿?덈떎. ?닿쾬??諛곗꽑 ?쒕룄 11媛쒖? 痢≪젙 ?쒕룄 5媛쒕? ?꾨? 二쎌?怨?留덉?留??④퀎 吏곸쟾???ㅽ뻾 ?먯껜瑜?硫덉텛寃??덉뒿?덈떎. ??寃쎈줈???ㅽ뻾???앷퉴吏 媛??곸씠 ??踰덈룄 ?놁뼱????λ맂 ??VI???꾩쭅 ?놁뒿?덈떎. ?대┛ ?몃뱾???덈Т 留롮븘?쒕씪??湲곗〈 ?ㅻ챸? ?먭린?섏뿀?듬땲?? ?몃뱾??51,349媛쒖씪 ??硫姨≫뻽怨?35,555媛쒖씪 ??二쎌뿀湲??뚮Ц?낅땲?? ?먮낯 VI??嫄대뱶由ъ? ?딆븯?듬땲?? 泥댄겕?ъ씠 ?꾪썑 ?숈씪?섍퀬 ??λ룄 ?ㅽ뻾???놁뿀?듬땲??
?대쾲 ?ъ씠?댁뿉???좎깮?섏씠 ?ㅼ쭛?쇱떎 ???덈뒗 ?먮떒????媛吏 ?덉뿀?듬땲?? 泥レ㎏, 誘몃━ ?곸뼱 ???ㅼ꽢 媛吏 ?덉륫 以?"鍮좎쭊 ?좎? ?녿떎"????ぉ? ?뺤떇??留욎븯吏留??ㅼ젣濡??꾨Т寃껊룄 ?쎌뼱 ?뺤씤?섏? 紐삵뻽?쇰?濡??듦낵媛 ?꾨땲??UNTESTED濡?湲곕줉?덉뒿?덈떎. ?듦낵濡??몄뿀?ㅻ㈃ ?ъ씠?댁씠 ?ㅼ젣蹂대떎 ?깃났?곸쑝濡?蹂댁???寃껋엯?덈떎. ?섏㎏, ?湲?以묒씠??蹂꾨룄???ㅽ겕?섏튂 ?ㅽ뿕 ?섎굹瑜??뚮━吏 ?딄퀬 ??댁떆耳곗뒿?덈떎. 洹??ㅽ뿕??李얠쑝?ㅻ뜕 ?듭쓣 ?곗냽????踰덉쓽 鍮뚮뱶媛 ?대? ?묎컳??蹂댁뿬二쇨퀬 ?덉뼱?쒖씤?? ?먰븯?쒕㈃ 洹몃?濡??뚮┫ ???덉뒿?덈떎.
?뗭㎏, ?ㅼ쓬 ?ㅽ뻾???좎씪??蹂寃쎌? 諛섏? ?꾩꽦???щ낯????ν븯怨?LabVIEW瑜??ъ떆?묓븳 ???ㅼ떆 ?댁뼱 ???몄뀡?먯꽌 鍮좎쭊 痢≪젙???섎뒗 寃껋엯?덈떎. ?닿쾬??洹?痢≪젙媛믪쓣 ?살쓣 ?좎씪??湲몄씠??"error 2"媛 ???앷린?붿???????쒗뿕?닿린???⑸땲?? ?ㅻ쭔 鍮뚮뱶媛 ?먭린 ?ㅽ뻾 ?꾩쨷??LabVIEW瑜??ъ떆?묓븯寃??섎뒗?? ?ъ떆?묒뿉 ????곸떆 ?덇????덉?留?鍮뚮뱶濡쒖꽌???덈줈???됰룞?대씪 誘몃━ ?뚮젮 ?쒕┰?덈떎. ????媛吏 ?먮떒 以??대뒓 寃껋씠???ㅼ쭛怨??띠쑝?쒕㈃ 留먯???二쇱떗?쒖삤.
?뮥 **?대쾲 ?ъ씠??湲곌퀎瑜?吏異???$9.78** ????蹂몃Ц???멸툒???ъ쟾寃??$4.22 ?섎굹留뚯씠 ?꾨떃?덈떎. ?댁뿭: ?ъ쟾寃??$4.2179 쨌 ?뚭퀬 $3.1161 쨌 臾몄꽌 ?먭?(doc_ingest) $0.9838 쨌 蹂닿퀬臾??묒꽦 2嫄?$0.7029 + $0.7568. (?먮떒 ?몄뀡 ?먯껜??鍮꾩슜? ?대뒓 吏묎퀎?먮룄 ?≫엳吏 ?딆뒿?덈떎 ??OPEN 56.) ?뚭퀬媛 F6(b)濡?"?ъ슜?먭? ?쎈뒗 ?대뼡 臾몄꽌?먮룄 ?ㅼ젣 吏異쒖씠 ?곹엳吏 ?딅뒗??怨?吏?곹빐???대쾲遺???곸뒿?덈떎.
3. **Unchanged from cycle 34, still yours to overturn:** the harness RECORDS all 60 front-panel controls and SETS none (inventing values would be a rule-1a computation change); the VI moved the PI magnet 0 ??30.000 mm under its own control inside 0??9 with `TMX?=39` / `TMN?=0` holding; and I accepted the GPU kernel on the **pre-bead-loss window** ??over the whole fixture max |dy| is 3.135e-05, 31횞 your 1e-6, but all 19 exceedances are bead 4 at k??0023, after that bead's own first loss at k=10018, the other four clean at identical k; plus **1 bead-frame of 50,215** where CPU and GPU sit on adjacent z-lookup indices (k1679, dz ??.667e-03), excluded by the FLIP mask. Say so if any of it is too loose.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

# PRIOR-ART REVIEW — `tools/recipes/build_d1_routeb_v7.py`, D1 route-B RUN 10

**VERDICT: NOT NOVEL — 7 findings.**

The **direction** survives: nothing in these files has tried, refuted or decided against phasing a route-B build across two LabVIEW instances so the census runs in a fresh one. The **mechanism as written** does not: two of this project's own measured laws govern exactly the two steps E3 adds, and the census's address key is a cached index carried across a reload, which our own peer record forbids.

Answering the two questions put to me, directly, before the findings:

1. **Has a mid-run restart inside a build recipe already been done here?** The *restart* half, yes, and it works — `tools/recipes/diag_d1_full_route.py:514-532` runs `tools/lv_restart.py` as a subprocess from inside the recipe and gates on its rc; measured green at `tools/bench/diag_d1_full_route_run2.log:5` (`P0r: lv_restart.py rc=0 -> FRESH_INSTANCE_DONE=True`). The *carry mid-build edits across the restart* half also exists, under another name — see F6. So v7's own PRIOR-ART comment (`v7:2182-2191`) is accurate as far as it goes, and every helper it cites is real: `gscript.reset` at `tools/gscript.py:262-269`, `ref_counts` at `:233-240`, `ensure_loaded` at `:1268`, `bench_prep.restart_labview` at `tools/bench/bench_prep.py:74-79` (no COM-liveness wait, correctly rejected).
2. **Is anything in our files evidence this edit cannot produce a readable census?** Yes — three things, all measured here, and they are precisely the three hazards the brief asked about by name: the recompile spin (F1), the stale save after `error 2` (F2), and index instability across a reload (F5).

---

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — the ORDER of save and restart is settled, and E3 inverts it → `contradicted` (F2)

`.claude/skills/labview-automation/SKILL.md:39-41`, one of the five laws:

> *"Open the panel before editing, save before closing, and **never cold-load a broken-saved VI headless** (recompile spin). **After error 2 (memory full): restart FIRST — a Ctrl+S in that state can write a stale file.**"*

Expanded at `.claude/skills/labview-automation/references/com-driving.md:497-499`:

> *"**A Ctrl+S issued while LabVIEW is in error-2 (memory full) state writes a STALE file** — the mtime moves, the content is the previous save. Work was lost to a 'successful' save. **After any error 2: restart LabVIEW first, save after.**"*

Measured, not advisory — `archive/2026-08-31-status-full-assembly-narrative.md:826-828`: *"Ctrl+S during error 2 (memory full) writes a STALE file: mtime moves, content is the previous state — the first Decimate placement was lost this way despite a 'successful' save."*

`docs/cycle27-plan.md:296-299` (Pre-decided 20) and STATUS's `## NEXT` both mandate the opposite order — *"save the working copy, close it, RESTART LabVIEW … reopen"* — and `v7:2206-2216` implements it that way.

**This is not a hypothetical state.** In run 9 the `error 2` failures all land in the S3w wiring pass: `tools/bench/build_d1_routeb_v6_run9.log:473-483` (11 ledger rows, `report_all(Diagram)`/`report_all(WhileLoop)` → `error 2`), and the ledger line E3 inserts itself after is `:362-363`. So by the time `g.save(TARGET, allow_broken=True)` runs at `v7:2206`, the instance has already emitted `error 2` at least eleven times and is in exactly the state the law names.

**The new gate cannot catch it.** `v7:2231-2232` gates `_md5_reopen == _md5_saved` — both readings of the *same file after the save*. A stale write passes that gate by construction. Worse, a stale write of a copy that has never been saved before reproduces the as-copied original bytes, so the reopened VI carries **none** of the 54 wired rows, and the four-bucket census classifies `wire 0` as **BARE** = *"the row genuinely did not survive"* (`v7:2261-2263`). Run 10 would then report ~51 BARE and R2 would "fail" — a manufactured wiring catastrophe, the exact false-catastrophe class the previous prior-art review's B2 caught one cycle ago. The cheap detector is already in the file: `ORIG_MD5` is pinned in the recipe, and `_md5_saved == ORIG_MD5` is the stale-write signature.

`PRIOR-ART: contradicted`

### A2 REFUTED ALREADY — "serialize an intentionally broken intermediate" was dropped on 2026-09-15 (F3)

`archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:118-124`, under **What was done with it** (i.e. adopted, not merely advised):

> *"`gscript.copy_by_index` rewritten … the VI is then COM-saved ONCE only if `ExecState == 1` — **no keystroke save of a broken intermediate** … `Save.Instrument` on a broken VI stays unverified and unused."*

and the reviewer's reason at `:91`: *"This also removes the need to serialize an intentionally broken intermediate artifact."*

**Does that still apply?** Partly. It was decided for a case (copy a primitive, wire it, then save) where waiting for `ExecState 1` was possible; route B's copy is legitimately broken mid-restructure and cannot reach 1 before the census. So the *rule* does not transfer unchanged — but the *reason* does, and it is the reason F2 and F4 are about. The disposition to beat is on record and the plan does not mention it.

`PRIOR-ART: refuted-already`

### A3 CONTRADICTED — covered by F2 above (same finding, not double-counted).

### A4 UNREAD EVIDENCE — the LabVIEW skill (F7)

`CLAUDE.md`'s "Where to actually look" says `.claude/skills/labview-automation/` holds **all** LabVIEW technique and to invoke it before any LabVIEW work. Two of its five headline laws (`SKILL.md:39-41`) govern precisely the two steps E3 adds — the save and the reopen. Neither Pre-decided 20 (`docs/cycle27-plan.md:286-311`), nor STATUS's NEXT block, nor the artifact's own 20-line PRIOR-ART comment (`v7:2182-2198`) cites the skill once; the comment's prior-art search covered restart mechanisms only. `docs/cycle27-plan.md:307-309` does address the save, but only to establish that saving a claudeDev copy is permitted under rule 1 — it never reaches the question of whether the save will be *truthful*.

`PRIOR-ART: unread-evidence`

---

## PART B — THE ARTIFACT

### B1 ALREADY BUILT — checkpoint → reopen → continue exists, with the two guards v7 omits (F6)

`tools/recipes/build_gpu_kernel.py:140-148`:

> `# 4b. CHECKPOINT: everything above is ~10 min of scripted work; save it so the output-wiring stage can be probed on a copy`
> `print("checkpoint saved", g.save(OP, allow_broken=True), "->", os.path.basename(CKPT), …)`

and its continuation in a separate process, `tools/recipes/finish_gpu_kernel.py:24-27`:

```
shutil.copyfile(CKPT, OP); g.report(OP, "SubVI"); g.open_panel(OP); time.sleep(1.0)
print("checkpoint: nodes", …, "ExecState", g.exec_state(OP), flush=True)
if g.exec_state(OP) != 1:
    print("STOP: the checkpoint itself is broken", flush=True); return 3
```

Two guards there that E3 does not have: the reopened file is **proved intact before anything downstream runs** (`:26-27`), and the reopen is a **report + `open_panel` + settle** rather than a bare reference grab (`:24`). Its docstring (`:1`) also records that the checkpoint it carried was `ExecState 1` — this project has never yet carried a *broken* checkpoint across a restart.

`PRIOR-ART: already-built`

### B2 ALREADY FAILED — `gui_save` of a broken target, twice, by the same two signals E3 relies on (F4)

- `tools/bench/cycle3b_toolkit.log:78` — `plan C: OBSERVED EXC gui_save(Test - Moving Objects Target.vi): file mtime did not move after Ctrl+S on every candidate window.`
- `tools/bench/build_keystone.log:903` — the identical exception on `Create SubVI.vi`.

Cause, from the review of the first (`archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:32-38`): *"`gui_save()` trusts the text returned by `lv_gui focus`; it never verifies the actual foreground HWND immediately before `^s`"*, and *"mtime alone is weak proof … Check file hash, size, dirty flag … not only `mtime > before`."*

**Does the new plan address that cause or repeat it?** It repeats it. `tools/gscript.py:2009-2018` still decides the window by the `focus` call's **return string** — which `SKILL.md:44-45` explicitly says is not evidence (*"Trust the foreground TITLE PIXELS, not the focus call's return"*) — and `tools/gscript.py:2040-2044` still believes the save on **mtime alone**. The user's standing GUI rule (capture → locate → act → capture → confirm, `docs/cycle27-plan.md:62`) is not satisfied by any of the four state-changing keystrokes/clicks `gui_save` issues (Ctrl+E `:2012`, title-bar click `:2028`, Ctrl+S `:2033`, Esc `:2038`). v7 adds an md5 *after* `gui_save` returns, which is an improvement over mtime for "did the bytes change", and no help at all for "are they the right bytes" (F2).

Note also this save has **never once executed**: no route-B run has ever reached S5, so `g.save()` on this ~470 KB mid-restructure copy is entirely unexercised, and R5 is an untested prediction rather than a repeat of a known-good step.

`PRIOR-ART: already-failed`

### B3 — the reopen: cold-loading a broken-saved VI is measured as a >8-minute recompile spin (F1)

This is the brief's own "recompile spin" question, and the answer is in our files.

`archive/2026-08-31-status-full-assembly-narrative.md:822-825`:

> *"**Never cold-load a broken-saved VI headless**: `GetVIReference` on the 30 KB broken v3 sent LabVIEW into a 100%-CPU recompile spin (>8 min, killed). `open_panel()` first loads the same VI in 16 s. Also `lv()`/`op()`/`GetVIReference` are UNGUARDED COM calls — they hang the caller forever, outside the watchdog."*

Restated as a law at `com-driving.md:492-496`.

**Why it bites here.** `v7:2226` calls `g.ensure_loaded(TARGET)`, which calls `open_panel` (`tools/gscript.py:1335`), which enters `vi_ref(target)` (`:1253`), whose first act is `lv().GetVIReference(target, "", False, 0)` (`:253`). So the first call on the reopened file **is** a cold `GetVIReference` on a broken-saved VI, with no preload — cold by Pre-decided 20's own instruction (`docs/cycle27-plan.md:308-309`, *"the census step opens the saved copy WITHOUT preloading the original"*). The measured spin was on a **30 KB** VI; this target is the main tracking VI (route B's pinned original is 471 KB-class, `docs/cycle27-plan.md:152-154`). And the call sits outside every per-call guard, so the only stop is bgrun's process deadline — against a run that already consumed 1817 s of its 2700 s budget before E3 existed (`tools/bench/build_d1_routeb_v6_run9.log:509`).

I am not claiming the spin is certain — `finish_gpu_kernel.py:24` reopens a checkpoint through the same path without incident, on an `ExecState 1` file. The claim is that this is a *measured* failure mode for exactly the broken-saved case, it is in the brief's own list of things to check for, and the artifact neither cites it nor guards against it.

`PRIOR-ART: already-measured`

### B4 ALREADY MEASURED — the census's address key is a cached index carried across a reload (F5)

`archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:26-30`:

> *"There is no documented ordering contract for `Traverse for GObjects.vi` … **Do not assume a cached index remains stable across executions, reloads, edits, or sessions.** If index selection remains anywhere, retain the UID identity gate on every read."*

What v7 does: `sink_addr` parks `(d, u, t)` where **`d` is a diagram INDEX** resolved pre-restart by `diag_index` (`v7:1238-1240`, `:1214-1215`), `claim_wire` stamps it onto the ledger row (`v7:1162-1170`), and after the restart the census re-derives the index space from scratch (`v7:2280-2294`) and tests the **stale** index against the **fresh** map: `if _d not in _maps: _why = f"Diagram[{_d}] UNWALKED"` (`v7:2318-2319`). If the reload changes `Diagram` traverse order by even one position, every addressed row becomes UNREAD and **R1 fails for a reason that has nothing to do with `error 2`** — the run buys the restart and still learns nothing about the hypothesis it exists to test. That this index space does move under this recipe is measured: `archive/peer/2026-09-19-routeb-run7-index-shift.md:44` — *"Run 5 → run 6 moved every node index on Diagram[24] by +1."*

The good half of the same answer, and the fix: **UIDs do survive a save.** Same review, `:61` — *"NI documents that a GObject UID is unique within its VI; remains associated with the same object after saving … Thus a Wire UID obtained by `report_all` should resolve from another op against the same VI, **including after ordinary save/reload**"* — recorded again at `:104`. (The one caution to keep: `:59`, *"a deleted object's UID may later be reused"*; and `archive/peer/2026-09-15-opwiresource-v2-fail1-and-tunnelread-plan.md:47` notes NI does not *promise* stability across unload/reload, so the identity gate stays.) So parking the **diagram UID** instead of the index, and letting `diag_index` (`v7:2282`) re-resolve it after the restart, makes the census cross-restart-safe using only calls the recipe already owns — no new op, no second edit to the wiring pass.

`PRIOR-ART: already-measured`

---

## What I did NOT find, so it is not blocked

- No archived peer review, retrospective or superseded plan section argues against restarting LabVIEW mid-recipe, or against splitting a build across instances. `docs/cycle27-plan.md:310` is the only forward-looking line and it treats unreachability as an `OPEN:`, not a refutation.
- No measured failure to *reopen* a saved working copy in a fresh instance. The nearest evidence is positive (`finish_gpu_kernel.py:24-27`), and it was on an unbroken file.
- No cross-instance **UID** instability in our record — only index instability (F5).
- The recipe's claim that no new restart mechanism is built is true, and `reset()`/`ref_counts()`/`ensure_loaded()`/`lv_restart.py` all exist and behave as cited.

---

```
PRIOR-ART: already-measured      (F1  cold GetVIReference on a broken-saved VI = >8 min recompile spin;
                                      archive/2026-08-31-status-full-assembly-narrative.md:822-825,
                                      com-driving.md:492-496, reached via gscript.py:1335 -> :1253 -> :253)
PRIOR-ART: contradicted          (F2  save-then-restart vs "after error 2 restart FIRST, a Ctrl+S writes a
                                      STALE file"; SKILL.md:39-41 + com-driving.md:497-499 +
                                      archive/2026-08-31-status-full-assembly-narrative.md:826-828
                                      vs docs/cycle27-plan.md:296-299 and v7:2206-2216;
                                      error 2 precedes the insertion point — run9.log:473-483 vs :362-363)
PRIOR-ART: refuted-already       (F3  "no keystroke save of a broken intermediate" adopted 2026-09-15;
                                      archive/peer/2026-09-15-strtopath-fail4-gui-save-of-broken-target.md:91,:118-124)
PRIOR-ART: already-failed        (F4  gui_save of a broken target failed twice on the same two signals
                                      v7 still trusts; tools/bench/cycle3b_toolkit.log:78,
                                      tools/bench/build_keystone.log:903, gscript.py:2009-2018 and :2040-2044)
PRIOR-ART: already-measured      (F5  the census matches a PRE-restart diagram INDEX against a POST-restart
                                      one; v7:1238-1240 and v7:2318-2319 vs
                                      archive/peer/2026-09-15-opwiresource-fail5-traverse-index-order-mismatch.md:26-30,
                                      drift measured at archive/peer/2026-09-19-routeb-run7-index-shift.md:44;
                                      node UIDs are the safe key, same review :61 and :104)
PRIOR-ART: already-built         (F6  checkpoint -> reopen -> continue already exists with both missing guards;
                                      tools/recipes/build_gpu_kernel.py:140-148,
                                      tools/recipes/finish_gpu_kernel.py:1 and :24-27)
PRIOR-ART: unread-evidence       (F7  .claude/skills/labview-automation/SKILL.md:39-41 — the two laws that
                                      govern this exact edit, cited nowhere in Pre-decided 20, STATUS NEXT,
                                      or the artifact's own PRIOR-ART block at v7:2182-2198)
```

Each of the seven is releasable in the normal way: open the citation and show in writing that it does not cover this case, or change the artifact and release with `FIXED:`. F2 and F5 are the two I would not release on argument alone — F2 because the failure it predicts is silent and would be *read as a wiring catastrophe*, and F5 because it would spend the whole run and return UNREAD for an unrelated reason.

## Sources

(extract from answer)

## What was done with it

DISPOSED by the cycle-42 judgement session, 2026-09-19. All seven findings were accepted as correct about the
FACTS; five changed `tools/recipes/build_d1_routeb_v7.py` inside the single E3 edit (nothing outside E3 and its
census was touched — not the wiring pass, not a wiring gate, not the per-bead maths, rule 1a), and two are
refuted on what v7 actually does. Run 10's bgrun deadline is raised from 45 to 60 minutes because of F1.

FIXED: contradicted - tools/recipes/build_d1_routeb_v7.py:2280 - the save-first order is forced because the edits live only in RAM, so v7 now proves the saved bytes are not the original's and proves the reopened copy intact before the census may classify any row, and a failed proof yields UNREAD, never BARE.
FIXED: already-measured - tools/recipes/build_d1_routeb_v7.py:2396 - the census now resolves the four build diagrams by parked UID instead of by pre-restart index, and unresolvable UIDs are reported UNREAD, so a post-reload index shift can no longer misclassify a row.
FIXED: already-measured - tools/recipes/build_d1_routeb_v7.py:2303 - the post-restart reopen of the broken-saved copy is now timed and logged, turning the measured >8-minute recompile spin into a reported number, and run 10's deadline is raised to 60 minutes so that spin alone cannot kill the run.
FIXED: already-built - tools/recipes/build_d1_routeb_v7.py:2313 - the E3 block reuses the existing checkpoint-reopen guards from build_gpu_kernel.py:140-148 and finish_gpu_kernel.py:24-27 rather than adding a new mechanism.
FIXED: unread-evidence - tools/recipes/build_d1_routeb_v7.py:2229 - the E3 comment block now cites SKILL.md:39-41 as the source of the post-error-2 restart law it is answering.
REFUTED: refuted-already - tools/recipes/build_d1_routeb_v7.py:2276 says v7 saves over COM with g.save(TARGET, allow_broken=True), which does not cover the 2026-09-15 rule against a keystroke save of a broken intermediate because v7 issues no keystroke save at all.
REFUTED: already-failed - tools/recipes/build_d1_routeb_v7.py:2276 says the save path is COM g.save, not gui_save, which does not cover the two gui_save failures at cycle3b_toolkit.log:78 and build_keystone.log:903 because those failed on focus-string and mtime signals that v7 does not use — after this cycle's repair v7 verifies saved CONTENT (md5 inequality plus a reopened-copy intactness proof).

CORRECTION 2026-09-19, cycle-42 judgement: the REFUTED: already-failed line above is WRONG and run 10 disproved it 30 minutes after it was written. It asserted v7 saves over COM with g.save, not gui_save; gscript.py:2065-2067 shows g.save(target, allow_broken=True) DIVERTS to gui_save whenever exec_state(target) == 0, and run 10 took that divert and died on the exact mtime failure F4 named (build_d1_routeb_v7_run10.log:367). Finding F4 was RIGHT. The refutation was made from a call-site summary without reading the callee, which is the error CLAUDE.md names under "claims about our own tools are factual claims, the ones you are most likely to be wrong about".
