# priorart-s0-decomp

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.1329  in 40 / out 28374 / cache-create 195030 / cache-read 2946159  (405s, 29 turn(s))
- **date:** 2026-09-19 19:35:38
- **outcome:** ANSWERED (409s)
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
# PLAN UNDER REVIEW ??the S0 DECOMPOSITION, `docs/cycle27-plan.md` Pre-decided 25

Trigger: S0 (the reference-hygiene repair of the traverse ops) has failed TWICE AT THE SAME PLACE, so
CLAUDE.md 짠3 "Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact" rule 3 forbids
another full-length retry under any filename and demands a one-page decomposition plan, prior-art-reviewed ONCE,
before any sub-step script is cut. **This text is that plan.** It is `docs/cycle27-plan.md:395-428` verbatim.

No recipe file exists yet for any sub-step ??this review gates whether they may be written at all.

## The record the plan is built on (for your citation checking)

- `tools/bench/build_s0_closeref_v3.log` ??87 PASS / 5 FAIL, `BGRUN END rc=1 after 601s`; no VI saved; the same
  failure four times: post-wiring `ExecState 1` read 0 on every repaired op stub, with EVERY wiring gate passing.
- `tools/bench/build_s0_closeref_v1.log` ??41 PASS / 2 FAIL, no VI saved.
- `archive/peer/2026-09-19-s0v3-execstate0.md` ??the failed-prediction review of run 2 (claude/hypothesis, opus
  max). UNDISPOSED.
- `archive/peer/2026-09-19-s0run1-closeorder.md` ??the failed-prediction review of run 1, REFUTED and measured.
- `tools/bench/s0_hygiene_probe_run2.log`, `tools/bench/s0_body_census.log`, `docs/REFERENCES.md` 짠4a,
  `docs/NAMES.md:230`.

## Pre-decided 25 ??VERBATIM

25. **S0 IS DECOMPOSED ??this table IS the one-page plan Pre-decided 23 demands** (judgement, cycle 44, 2026-09-19).
    S0 has now failed TWICE AT THE SAME PLACE: post-wiring `ExecState 0` on every repaired op stub, replicated 횞4 in
    fresh instances with every wiring gate PASSING (`tools/bench/build_s0_closeref_v3.log`, 87/5;
    `??v1.log`, 41/2). By CLAUDE.md 짠3 "Big or blocked work is SPLIT?? rule 3, **no full-length S0 retry may be cut
    under any filename**. S0 runs as five sub-steps, each its own short script, each starting FROM the previous
    step's saved file in a FRESH LabVIEW instance, each ending with a saved artefact and its md5 in the log.
    **The first FAIL stops the chain and leaves the file that shows the failure on disk.**

    | sub-step | what it does | saved artefact | pass criterion |
    |---|---|---|---|
    | **S0-a ARM** ??baseline, **NO edit** | copy `OpReport_v3.vi` to a new name; read its `ExecState` twice: (i) COLD in a fresh instance, (ii) after opening `OpReport_v3.vi` itself read-only in that same instance (the op-stub analogue of Pre-decided 14a's "original preloaded" ??it loads `Traverse for GObjects.vi` and the rest of the hierarchy). Edit nothing | `claudeDev\S0a_OpReport_base.vi` + md5 + BOTH readings, each labelled with its condition | both readings are TAKEN and logged. ?뵶 **A cold-0 / preloaded-1 pair means S0's four `ExecState 0` failures were UNREAD (Pre-decided 14a), not broken ??the chain STOPS there for judgement, and the three op stages of run 2 were replicating a measurement artefact** |
    | **S0-b MEASURE** ??is the repair needed at all? | profile the **UNREPAIRED** ops under a BUILD-SHAPED workload (traverses interleaved with mutations, S3w-like), ??0 calls, recording kernel handles **from call 1** (call 0 is the 473 KB VI load ??`s0_hygiene_probe_run2.log:75`,`:95`) AND LabVIEW private bytes per call | `tools/bench/s0b_refleak_profile.json` + its log | the profile COMPLETES and prints both meters per call. Pure measurement ??**no outcome of it fails this step** |
    | **S0-c EDIT ??one edit per saved file** | c1 = For Loop only 쨌 c2 = + the `Close Reference` node inside it 쨌 c3 = + the `References` array branch wired in 쨌 c4 = + `remove_bad_wires_scripted` | `claudeDev\S0c1_?쫣i` ??`S0c4_?쫣i`, each md5'd | each file SAVES, and each reads `ExecState` under the condition S0-a established. The first sub-step whose ExecState drops STOPS the chain ??and **that file is on disk for the next session to open** |
    | **S0-d HYGIENE** | the accepted op, 20 consecutive calls in one script | the accepted op VI + log | handles flat 짹100 **counted from call 1** AND private-byte drift ??5 MB. The 짹100 gate ALONE is blind to VI Server refnums (`tools/gscript.py:227-228`), so both meters or neither |
    | **S0-e RECORD** | update `docs/REFERENCES.md` + `docs/toolkit-capabilities.md`; old op files untouched | the doc diffs + md5s of the OLD ops | the old ops are byte-identical to before; the accepted ops carry new `_vN` names |

    Binding notes:
    - (i) **S0-a is the ARM, and the ARM is its own SAVED step** (retrospective-cycle43 F1/F5: run 2 spent three op
      stages replicating a failure the ARM had already measured). **No S0-c script may be cut before S0-a's two
      readings are on file.**
    - (ii) **Order inside S0 is the cycle-43 disposition's (c) then (a)**: settle WHY the insert leaves `ExecState 0`
      ??`archive/WORKLOG.md:86-87` (a bare For Loop breaks the VI) and `remove_bad_wires_scripted` was never called ??
      before any more close-wiring. S0-c1?쫈4 IS that test, decomposed one edit at a time.
    - (iii) **The array-into-scalar experiment stays a SCRATCH experiment only**, with a prediction contract citing
      `archive/WORKLOG.md:84-86` ("defeated four wiring attempts"). It is not a step of this chain.
    - (iv) ?좑툘 **S0's original premise is MEASURED UNSUPPORTED** (Pre-decided 21(b) amended by cycle 43): the repair is
      owed as **rule compliance** (21(c)), not as an `error 2` fix. CLAUDE.md 짠3's hygiene rule states its acceptance
      test as "20 consecutive calls ??handle count flat (짹100)". **ASSUMPTION THIS CYCLE PROCEEDS UNDER, flagged to
      the user (rule 2c): if S0-a shows the `ExecState 0` was UNREAD and S0-b shows the UNREPAIRED ops already meet
      that test on both meters, judgement may ACCEPT THE OPS AS THEY ARE with the measurement as the record** ??a
      legitimate outcome of S0, not a skipped step. Only the user may overturn this reading of their own rule.
    - (v) `Close Reference` on a GObject refnum may be a **NO-OP** ??forum-grade, no version context
      (`archive/peer/2026-09-19-s0v3-execstate0.md`). S0-d's private-byte meter is what decides whether the repair
      does anything at all; a repair that moves neither meter is recorded as such, not celebrated.

## What to check hardest

1. Has any of the FIVE sub-steps (S0-a ??S0-e) already been run, built, or measured under another name in
   `tools/bench/`, `tools/recipes/`, `docs/toolkit-capabilities.md` or `archive/`? In particular the cold-vs-
   preloaded `ExecState` reading and the "profile the unrepaired ops" measurement.
2. Has the cold-0 / preloaded-1 hypothesis of note (i) / S0-a already been decided, measured or refuted here?
3. Does the S0-c1?쫈4 ordering repeat a build that already failed, and does the plan address that cause?
4. Do the pass criteria (handles flat from call 1 + private bytes ??5 MB) contradict anything already written in
   STATUS.md, CLAUDE.md 짠3 or `docs/`?
5. Does the decomposition itself contradict any existing decision about how S0 must be run?


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
  status: released
  owner_s0v3: # ?뵶 **RELEASED 2026-09-19 19:1x KST. S0 RUN 2 RAN AND SAVED NO VI ??`tools/bench/build_s0_closeref_v3.log`, `BGRUN END rc=1 after 601s`, 87 PASS / 5 FAIL.** `tools/recipes/build_s0_closeref_v3.py` (cut from v2's bytes, sha256 `7a4381a71a73??, 881 lines, `py_compile` OK `tools/bench/v3_syntax_c43.log`; own stop record ARMED+RELEASED, release lines in `archive/peer/2026-09-19-priorart-s0-closeref.md` 짠"RUN 2"; renamed from v2 only because `stop_record.py:313-331` had already stamped v2's release at sha `c3c78f2801dc` ??the gate asymmetry with `guard_cycle.py:485-496` stays OPEN) applied all three cycle-43 judgement decisions. ?뵶 **ONE failure, four times: `G5 ??ExecState 1` read 0** (`:50` ARM, `:99`, `:158`, `:202`) ??EVERY wiring gate passed first. ?윟 **The review's 짠2 question is SETTLED: the `References` branch IS a valid wire** ??sink w636 SEGMENTED, `Is Broken? False`, LoopTunnel #642 **IndexMode 1 AS READ** (`:80-:86`); on the existing loop the w421 branch was **EXACT, wire delta 0** and the error chain #115??738 EXACT w865 (`:191-:199`); the measured body CHAIN was re-confirmed on the copy (`:183-:189`). ?넅 **REFMINT census (new)**: `OpReport_v3` 3 reference-returning property reads, `OpWireSource_v5` **15**, `OpReportAll_v0` 3 (`:62-64`, `:111-123`, `:170-172`). Original md5 `2a78e17c?? unchanged (`:224`); all three stubs deleted; no op VI on disk altered. ?뵶 **MANDATORY REVIEW IN AND ANNOTATED ??`archive/peer/2026-09-19-s0v3-execstate0.md` (ANSWERED, claude/hypothesis opus max, $2.5484, 472 s): H REFUTED, and it says the REPAIR ITSELF may be pointless ??`Close Reference` is reportedly a NO-OP on GObject refnums (NI-employee + Rolf forum statements, no version context), so the ref that needs closing is the VI refnum from `Open VI Reference` #43, which S0 deliberately does not close.** Its 3 alternatives (bad-wire fragment elsewhere 쨌 a broken NODE/structure a wire reader cannot see 쨌 `remove_bad_wires_scripted` never called) and its ordering (run `handle_audit.py` on the UNREPAIRED ops FIRST ??S0 may close by measurement) are JUDGEMENT's to accept; nothing was acted on. No motor, no camera, no new op, no S1.
  owner_s0v1: # ?뵶 **RELEASED 2026-09-19 18:4x KST. S0 RAN ONCE AND SAVED NO VI; THE RETRY IS BLOCKED ON JUDGEMENT ??the repair's stage-3 design is REFUTED BY MEASUREMENT.** RUN 1: `tools/recipes/build_s0_closeref_v1.py` (sha `e5d801e1745d`, 654 lines, the judgement-disposed For-Loop design, all 7 prior-art slugs released in `archive/peer/2026-09-19-priorart-s0-closeref.md` 짠DISPOSITION) ??`tools/bench/build_s0_closeref_v1.log`, **`BGRUN END rc=1 after 566s`, 41 PASS / 2 FAIL, NO VI SAVED** (`OpReport_v4`/`OpWireSource_v6`/`OpReportAll_v1` stubs deleted, old ops untouched, original md5 `2a78e17c?? unchanged `:139`). Both FAILs were the material session's own bugs: `gscript.uids()` returns a **SET** so `.index()` raised (`:47-49`), and gate G3c assumed the loop body's Property nodes are chained (`:114-118`). ?윟 The reviewed DESIGN reached further than any route-B run: at `:32-33` the `References` array wire was BRANCHED into the new For Loop body by `OpConnectFromWire_v0` at the first attempt (sink w636, `Is Broken? False`, LoopTunnel #642) ??the scalar refnum input that "defeated four wiring attempts" was never asked to take an array. ?뵶 **THE MANDATORY FAILED-PREDICTION REVIEW CAME BACK `REFUTED`** ??`archive/peer/2026-09-19-s0run1-closeorder.md` (ANSWERED, claude/hypothesis opus max, `tools/bench/peer_s0run1_closeorder.log` `BGRUN END rc=0 after 538s`) ??and **this session MEASURED it and the review is RIGHT**: `tools/bench/s0_body_census.py` (NEW, read-only, 7/7, rc=0, `?쫟0_body_census.log`) shows `OpReportAll_v0`'s body is a **CHAIN** ??`#114 'Owner'` (source, w548) drives `#115 'reference'` (`:47`,`:49`,`:60`), and w421's source is LoopTunnel #511 = the `References` tunnel, IndexMode 1 (`:58`,`:68`). So the two-wire repair's stated reason is false, its node choice is provenance-blind, and **`#114.Owner` mints a NEW reference per iteration that the repair does not close**. The review's 짠2 ??whether run 1's branch really succeeded, since ExecState stayed 0 and the created tunnel's IndexMode was never read ??is UNSETTLED and needs its scratch-copy arm. `tools/recipes/build_s0_closeref_v2.py` (sha `c3c78f2801dc` + a ?뵶 warning block, both run-1 bugs fixed, own stop record armed on the same 7 slugs) EXISTS and is **NOT LAUNCHED**. ?좑툘 MACHINERY DEFECT FOUND: `stop_record.py:313-331` pins a release to the bytes that FIRST launched, so a post-run bug fix can never relaunch under the same path, while `guard_cycle.py:485-496`'s disposition exemption explicitly ALLOWS that edit ??the two gates disagree, which is why the retry needed a new filename. No motor, no camera, no new op, no device.
  owner_s0: # ?뵶 **RELEASED 2026-09-19 17:48 KST. S0 IS BLOCKED AT THE PRIOR-ART GATE ??NO OP VI WAS BUILT OR SAVED.** `tools/recipes/build_s0_closeref_v0.py` (OpReport_v4 + OpWireSource_v6, new files, old ones untouched) is written, `ast.parse` OK, sha `843e9c0c93a3`; its mandatory prior-art review `archive/peer/2026-09-19-priorart-s0-closeref.md` (ANSWERED, opus/high, `tools/bench/priorart_s0_closeref.log` `BGRUN END rc=0 after 226s`) = **NOT NOVEL, 7 slugs**, and `tools/stop_record.py` refuses the launch until a `FIXED:`/`REFUTED:` line releases it ??**JUDGEMENT's call, not the material session's**, so none was written. ?뵶 **A3(i) `contradicted` IS CONFIRMED BY THIS SESSION'S OWN MEASUREMENT: `docs/cycle27-plan.md` Pre-decided 21(b) ("the live cause of `error 2` is a leaked GObject reference per matched object") is NOT SUPPORTED** ??20 횞 `report_all(Diagram)` = 3,400 matched objects moved handles **+9** and private bytes **??.1 MB** with no `error 2` (`tools/bench/s0_hygiene_probe_run2.log:121-123`). ?뵶 **A2/B2 `already-failed`: the `Close Reference` was removed ON PURPOSE ??`archive/WORKLOG.md:84-86` "defeated four wiring attempts"** ??and the recipe cites neither. ?뵶 **B4: the 짹100 handle criterion in NEXT 짠1 is BLIND to this reference class** (`gscript.py:227-228`); it FAILS on the unrepaired op for a VI load and PASSES with the leak in place. B3: the For-Loop close route is already built and measured (`docs/toolkit-capabilities.md:438-443`). ??SIDE RESULTS, both saved: `docs/NAMES.md:230` corrected by measurement (terminal 2 is **`References`**, not `GObject Refs`; `Close Reference`'s three terminals recorded for the first time) ??`tools/bench/s0_terminal_names.log`, 6/6, rc=0; `docs/REFERENCES.md` 짠4a written. Review annotated. Original md5 `2a78e17c?? unchanged before and after. PREVIOUS: ??**PHASE 1 DONE** ??`tools/bench/s0_hygiene_probe.py`, log `tools/bench/s0_hygiene_probe_run2.log` (`BGRUN END rc=1 after 158s`, 12 PASS / 1 FAIL). CENSUS: `OpReport_v3` = 5 nodes (Function#43 `Open VI Reference`, SubVI#124 `Traverse for GObjects.vi`, IndexArray#167, Property#241, Property#482), `OpWireSource_v5` = 19 nodes **containing that same chain**, `OpReportAll_v0` = 5 nodes ??**all three have ZERO Close Reference**; `KernelBuilder_v1.vi` HOLDS the donor, Function **#157 `Close Reference`**. BASELINE LEAK on a scratch copy of the route-B original: 20횞 `count(Node)` handles 34,134 ??34,349 (**+215**) / private 586.5 ??613.7 MB (**+27.2 MB**) ??but 20횞 `report_all(Diagram)` with the VI already loaded is **FLAT** (handles **+9**, private **??.1 MB**), so the +215/+27 MB is the FIRST call's load of the 473 KB VI, not a per-call leak. ?좑툘 The only FAIL is the brief's own 짹100 handle gate, failed by the UNREPAIRED op for a load, not a reference. PHASE 2 = `tools/recipes/build_s0_closeref_v0.py` (OpReport_v4 + OpWireSource_v6), prior-art review in flight. No motor, no camera. Original md5 gated before and after.
  status_prev: released   # ?뵷 **D1 ROUTE-B v6 RUN 9 RAN, 2026-09-19 05:31 ??06:01 KST** ??`tools/bench/build_d1_routeb_v6_run9.log`, `BGRUN END rc=1 after 1817s` (`:509`), **80 PASS / 0 FAIL**. **ALL FIVE PREDICTIONS HELD.** Ledger `:363` 66 attempted / **54 WIRED** / 11 FAILED / 1 NO-ROUTE (all 11 FAILED carry `error 2`, `:473-:483`). `CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:365`) ??the census RETURNED and did NOT print a false zero: `diag_index` itself calls `report_all(Diagram)`, which `error 2` killed for all five diagram uids (`:364`), exactly the review's B2 finding, so every row is UNREAD, never BARE. `Z/dZ` t0 **PASSES J2 with per-diagram delta +1** (`:360`: a=True w29238=w29238, 1 reciprocal source; b=True Diagram[24] 31??2 delta 1, VI-wide 1937??938; c=`Is Broken? False`; d=29238) and is WIRED (`:464`). `#2222` t2/t3/t4/t5 all WIRED (`:465-:468`). Original md5 `2a78e17c?? unchanged (`:13`, `:494`); ExecState S1 cold 0 = UNREAD (`:37`), live copy PRELOADED 1 (`:491`). Run 9's own crash is still `count(LoopTunnel)` in `settle_index_modes` (`:486`, `:508`). PREVIOUS: **D1 ROUTE-B v5 RUN 8 RAN, 2026-09-19 03:58:14 ??04:28:36** ??`tools/bench/build_d1_routeb_v5_run8.log`, `BGRUN END rc=1 after 1822s`, **80 PASS / 0 FAIL**. ?뵶 **EVERY PREDICTION MISSED**: `#2222` t3/t4/t5 all WIRED (`:411-:413`), `Z/dZ` t0 FAILED on J2 reading (b) with per-diagram delta **+1** (`:418`); ledger 66/53/12/1 (`:363`); K3's SURVIVAL CENSUS **UNREAD** ??`report_all(Wire)` died of `error 2` (`:364`); the same `error 2` crash in `settle_index_modes` at 35,555 handles (`:431-:432`), victims 6 ??**11**. Original md5 unchanged (`:13`, `:440`). Its mandatory failed-prediction review is IN and **UNDISPOSED**: `archive/peer/2026-09-19-routeb-run8-predictions.md` (ANSWERED, claude/hypothesis opus max, $4.4847, 676 s) ??it calls run 8 a **regression** (WIRED 54 ??53, FAILED 9 ??12), says the `+1` is the wire the bracket exists to create so **the J2(b) null is inverted**, and identifies `error 2` as LabVIEW **"Memory is full"** with the handle count neither cause nor symptom. FULL RECORD ??`archive/2026-09-19-status-cycle39-run8.md` 짠7 (run 8) 쨌 짠4 (run 7) 쨌 짠5 (cycle 38) 쨌 짠6 (cycle-37 machinery) 쨌 짠3 (v5 build) 쨌 짠1/짠2 (runs 6 and 5).
  owner_c42r10r: # ?뵶 **RELEASED 2026-09-19 07:25 KST ??RUN 10 RAN 06:55:08 ??07:25:43, `tools/bench/build_d1_routeb_v7_run10.log`, `BGRUN END rc=1 after 1835s` (`:514`), 80 PASS / 1 FAIL.** ?뵶 **R1, R2 and R5 ALL MISSED ??the E3 save NEVER HAPPENED.** `g.save(TARGET, allow_broken=True)` saw ExecState 0 and diverted to `gui_save` (`gscript.py:2065-2067`), and gui_save raised `file mtime did not move after Ctrl+S on every candidate window` (`:367`, `gscript.py:2043`) ??**exactly the review's F4 `already-failed` finding, which this cycle's release line REFUTED on the premise that "the save path is COM g.save, not gui_save".** So: no save, no restart, no fresh instance, `_md5_saved` never taken, reopen never timed. ?윟 **THE NEW CONTRACT HELD: `CENSUS: 0 survived / 0 bare / 51 unread of 51 claimed` (`:370`), `EXACT 0, SEGMENTED 0, BARE 0, UNREAD 51` (`:371`)** ??a save that never landed printed ZERO bare, not a wiring catastrophe, and the one FAIL is the new fresh-instance/proven-intact gate (`:368`). `error 2` had ALREADY killed `report_all(Diagram)` and `count(Node)` at the E3 entry (`:364`, `:365`, handles 35,541 `:366`), so the parked-UID map was NOT TAKEN either. R3 and R4 HELD: ledger `:363` **66 attempted / 54 WIRED / 11 FAILED / 1 NO-ROUTE**, all 11 FAILED carry `error 2` (`:478-:488`); `Z/dZ` t0 PASSES J2 with per-diagram delta +1 (`:360`) and is WIRED (`:469`); `#2222` t0/t2/t3/t4/t5 all WIRED (`:469-:473`). Terminal crash unchanged: `count(LoopTunnel)` in `settle_index_modes` (`:491`, `:513`). **S5 WAS NEVER REACHED ??no D1 VI was saved**; the working copy is renamed aside to `claudeDev\SCRATCH_routeb_065508_crash_072542.vi`. Original md5 `2a78e17c?? UNCHANGED before (`:13`) and after (S6b PASS). Handles 31,106 ??50,441.
  owner_c42r10: # ?뵷 **ACQUIRED 2026-09-19 ~06:5x KST by the cycle-42 material session (step 2) for D1 ROUTE-B v7 RUN 10.** v7 REPAIRED per the cycle-42 judgement disposition of the 7 prior-art findings (F1/F2/F5/F6/F7 applied inside the single E3 edit; F3/F4 REFUTED ???뵶 **and that refutation was WRONG: run 10 proved F4 RIGHT 30 min later, `gui_save` died at `run10.log:367`. CORRECTION at `archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`; full record `archive/2026-09-19-status-cycle42-run10.md` 짠3**): NEW sha256 `960452920708??, md5 `aac4f909cb7ce7246e2aad4b6fbc7134`, **2818 lines**, `py_compile` OK (`tools/bench/v7_syntax_c42.log`, `BGRUN END rc=0`). Diff vs v6 +251/??0 in 4 hunks; vs the reviewed v7 bytes (`d808e10ce4c1`, 2699 lines) +119 lines, all inside the docstring, the E3 block and the census. Gate arithmetic: v7 now adds FOUR gates to v6's 80 ??a clean run reads **84 PASS / 0 FAIL**. Prior-art gate RELEASED ??5 `FIXED:` + 2 `REFUTED:` lines under `## What was done with it` in `archive/peer/2026-09-19-priorart-d1-routeb-run10.md`; stop record re-armed on the NEW sha and RELEASED (`tools/stop_record.py list` ??`960452920708 RELEASED`). Launch: `py tools/bgrun.py --material --max-min 60 --log tools/bench/build_d1_routeb_v7_run10.log -- py -u tools/recipes/build_d1_routeb_v7.py`.
  owner:     # RELEASED 2026-09-19 06:01 KST ??run 9 ended `BGRUN END rc=1 after 1817s`, log `tools/bench/build_d1_routeb_v6_run9.log`. Acquired 2026-09-19 05:31 KST by the cycle-41 material session for **D1 ROUTE-B v6 RUN 9** ??`py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v6_run9.log -- py -u tools/recipes/build_d1_routeb_v6.py`. v6 sha256 `8dbb1e69ef83??, md5 `cb96a4df0ef71325880ff63aed47e8b9`, 2607 lines, `ast.parse` OK. Prior-art gate RELEASED (five `FIXED:` lines in `archive/peer/2026-09-19-priorart-d1-routeb-run9.md`, stop record RELEASED). Previous: released 2026-09-19 04:28 KST after run 8 ended (BGRUN END rc=1 after 1822s).
  purpose_c41:   # ?뵶 **CYCLE 41, 05:0x-05:22: `tools/recipes/build_d1_routeb_v6.py` IS CUT AND SYNTAX-CLEAN (sha256 `07c6b5d6a37e??, md5 `9035029214449dd893ce56ab53618b56`, 2551 lines, `ast.parse` OK) ??E1 at `:1849` (`_b_ok = (_wddelta == 1)`) + comment `:1601-1613`, E2 at `:2128-2215` (walk-based census). RUN 9 WAS NOT LAUNCHED AND NO LOCK WAS TAKEN: the prior-art gate stopped it.** `archive/peer/2026-09-19-priorart-d1-routeb-run9.md` (ANSWERED, opus/high, $4.2179, 404 s; log `tools/bench/priorart_d1_routeb_run9.log` `BGRUN END rc=0 after 405s`) = **NOT NOVEL**, 5 findings / 4 slugs ??`contradicted` 횞2 (A3(i) the run-8 review's `:155` vs `:175`; A3(ii) the unedited failure string `v6:1865` still says "delta 0"), `already-failed` (B2: the census point already kills `report_all(Diagram)`, which `diag_index` 횞4 calls), `already-measured` (B4: uid inequality ??wire gone), `helper-exists` (B3: `sink_addr` already returns (d,n,t)). E1 is CLEAN ??"nothing in these files refutes it". `stop_record` now refuses the run-9 launch (measured: reviewed sha `07c6b5d6a37e`, no release line). Writing `REFUTED:`/`FIXED:` is JUDGEMENT's call.
  purpose_c42:   # ?뵷 **CYCLE 42 step 1 (material), 2026-09-19 ~06:5x: `tools/recipes/build_d1_routeb_v7.py` IS CUT AND SYNTAX-CLEAN. RUN 10 IS NOT LAUNCHED** (step 2 launches it after judgement disposes the prior-art findings). v6 md5 `cb96a4df0ef71325880ff63aed47e8b9` VERIFIED before the cut; v7 sha256 `d808e10ce4c1??, md5 `c30f8ade3ce3a23645d2c779a9edcac1`, **2699 lines**, `ast.parse` + `py_compile` OK. Diff vs v6: **+92 / ?? lines, 2 INSERT hunks, no existing line touched** ??`v7:308-330` docstring (run-10 R1?밨5 contract) and `v7:2170-2238` the E3 block. `gate()` sites 52 ??54, so a clean run 10 reads **82 PASS / 0 FAIL**. E3 = Pre-decided 20 exactly: after the S3w ledger line and before the census, `g.save(TARGET, allow_broken=True)` ??`close_panel` ??`g.reset()` (proxies released while the instance lives) ??subprocess `tools/lv_restart.py` (the path this recipe already used twice) ??`g.reset()` + `D1._WALKS.clear()` ??`g.ensure_loaded(TARGET)`, then the EXISTING four-bucket census, unchanged. **No fallback**: if the restart/reopen raises, `_CENSUS_FRESH` is False, the new gate FAILS and the run ends rc=1. ?뵶 **THE PRIOR-ART GATE STOPPED RUN 10, AS IT STOPPED RUN 9.** `archive/peer/2026-09-19-priorart-d1-routeb-run10.md` (ANSWERED, opus/high, **$5.6462**, 469 s; log `tools/bench/priorart_d1_routeb_run10.log` `BGRUN END rc=0 after 470s`) = **NOT NOVEL, 7 findings / 6 slugs**. The DIRECTION survives ??"nothing in these files has tried, refuted or decided against phasing a route-B build across two LabVIEW instances" ??the MECHANISM does not. **F2 `contradicted`**: the skill's own law (`SKILL.md:39-41`, `com-driving.md:497-499`, measured `archive/2026-08-31-status-full-assembly-narrative.md:826-828`) is **"after error 2, restart FIRST ??a Ctrl+S in that state writes a STALE file"**, and E3 saves FIRST while run 9 shows 11 `error 2` rows already emitted *before* the insertion point (`run9.log:473-483` vs `:362-363`); the new md5 gate compares the file with itself and cannot see it, and a stale write would print ~51 **BARE** = a manufactured wiring catastrophe. **F5 `already-measured`**: the census matches a PRE-restart diagram INDEX against a POST-restart one (`v7:1238-1240` vs `:2318-2319`), which our own index-shift review forbids ??node/diagram **UIDs** are the safe key (`?쫛pwiresource-fail5-traverse-index-order-mismatch.md:26-30,:61,:104`). **F1 `already-measured`**: cold `GetVIReference` on a broken-saved VI = a measured **>8-min recompile spin**, and `ensure_loaded` reaches exactly that call. **F4 `already-failed`**: `gui_save` of a broken target has failed twice on the two signals it still trusts. **F3 `refuted-already`**: "no keystroke save of a broken intermediate" was adopted 2026-09-15. ?뵶 **BOTH WERE RIGHT AND CYCLE 42 REFUTED THEM ANYWAY** ??`g.save(allow_broken=True)` DIVERTS to `gui_save` at ExecState 0 (`gscript.py:2065-2067`), so E3 did attempt a keystroke save and died on it (`run10.log:367`); corrected at `?쫜riorart-d1-routeb-run10.md:499`. **F6 `already-built`**: checkpoint?뭨eopen?뭖ontinue already exists (`build_gpu_kernel.py:140-148` + `finish_gpu_kernel.py:24-27`) with the two guards v7 omits. **F7 `unread-evidence`**: the skill is cited nowhere in Pre-decided 20, STATUS NEXT or v7's own prior-art block. Stop record **ARMED, NOT RELEASED** (`tools/stop_record.py list` ??`build_d1_routeb_v7.py d808e10ce4c1 STOPPED`); writing `REFUTED:`/`FIXED:` is JUDGEMENT's call.
  since:
  purpose:   # RUN 8 RAN 03:58:14 -> 04:28:36, log tools/bench/build_d1_routeb_v5_run8.log
  purpose_c37_38: # RELOCATED VERBATIM (rule 4) ??`archive/2026-09-19-status-cycle39-run8.md` 짠5 (cycle-38 prior art + the P1?밣4 patches + why `--recipe` is unusable; run 6's failed-prediction review, $3.6636) and 짠6 (the cycle-37 `lv_stallcheck.ps1` clauses). ?좑툘 The 짠6 repair IS APPLIED: `tools/lv_stallcheck.ps1:273` writes the gating `stall_pid*.log` ONLY on `VERDICT: BLOCKED`.
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
?쉾 **Cycle 43 (firefighter, 2026-09-19 ~17:5x??0:0x) ran S0 and S0 FAILED TWICE AT THE SAME PLACE ??Pre-decided 23
fires: the NEXT session's FIRST act is a ONE-PAGE DECOMPOSITION PLAN for S0** (sub-steps, each with a saved file
name + pass criterion), prior-art-reviewed once, THEN executed step by step. **No S0 retry before that plan; S1/S2
stay unstarted** (user's ordering, NEXT of 17:4x). What the machine knows, for that plan:
- **The failing place, replicated 횞4 in fresh instances: post-wiring `ExecState 0` on every repaired op stub**
  (`tools/bench/build_s0_closeref_v3.log`, 87 pass / 5 fail ??every wiring gate PASSES, the 짠2 arm PASSES: the
  `References` branch lands as a VALID wire, auto-indexed IndexMode 1 as read). Nothing saved; originals + old ops
  untouched (md5s gated). Run 1 = `??v1.log`; body census `tools/bench/s0_body_census.log` (OpReportAll body is a
  CHAIN; #114 `Owner` mints a ref per iteration; REFMINT census: OpWireSource_v5 mints **15**/call).
- **The S0 leak premise is measured UNSUPPORTED** ??cycle27-plan Pre-decided 21(b) is AMENDED (20횞 report_all =
  handles +9, private ??.1 MB, no error 2, `s0_hygiene_probe_run2.log:121-123`); the 짹100-handle gate is blind to
  VI refnums (`gscript.py:227-228`) ??S0 gates are now G-A no error 2 / G-B handles flat from call 1 / G-C private
  bytes ?? MB drift (cycle-43 judgement).
- **Undisposed conflict for the decomposition plan** (`archive/peer/2026-09-19-s0v3-execstate0.md`): the review says
  `Close Reference` may be a NO-OP on GObject refnums (forum-grade) and the real consumer is the never-closed VI
  refnum from `Open VI Reference` #43 + repeated VI loads (`com-driving.md:308-312`); its cheapest test wires the
  array into the scalar sink that `archive/WORKLOG.md:84-86` says defeated four attempts. Cycle-43 judgement: (a)
  measure first ??`handle_audit.py`/private bytes on the UNREPAIRED ops under a build-shaped workload (traverses
  interleaved with mutations, S3w-like) before any more close-wiring; (b) the array-into-scalar test is allowed
  ONLY as a scratch experiment with a prediction contract citing WORKLOG; (c) first settle WHY the For-Loop insert
  leaves ExecState 0 ??`WORKLOG.md:86-87` (a bare For Loop breaks the VI) and `remove_bad_wires_scripted` was
  never called: that re-read is the cheapest discriminating test and comes first.
- ?뵶 **Retrospective cycle 43 = `device-failed` (threshold 1, recorded in `docs/violation-decisions.md`): the
  stop-record gate refused a judgement-released bug fix and was beaten by a rename (v2?뭭3), second day running.
  BEFORE any new stage script is cut: dispose `archive/peer/2026-09-19-stoprecord-release-deadlock-codex.md` (its
  supersession patch for `stop_record.py _check()`, `:91-107`, blank since 01:22) and apply it ??a REPAIR of an
  existing device. ?좑툘 User: does your 08:53 "no more devices" order cover repairs? We proceed as if it does not.**
- Retrospective F1/F5: in the decomposition plan, the ARM (scratch discriminating test) becomes its own SAVED
  step whose FAIL stops the script ??run 2 spent three op stages replicating a failure the ARM had already measured.
- ?좑툘 The 4th consecutive outcome review repeats all five goal-drift lines and ESCALATES ??"the stop-and-replan
  escalates to the project's continued existence" (`archive/peer/2026-09-19-outcome-review-20260919.md:153`,
  undisposed) ??the user should read it.
- ?㏏ `claudeDev\SCRATCH_s0_180632.vi` is an orphan scratch (workspace boundary blocked deletion) ??delete it.
**FLAGGED FOR THE USER (rule 2c):** S0's premise (op-leak ??error 2) is measured unsupported, and S1's body already
exists measured (`build_d1_routeb_v7.py` s1/s1t, counts at `:74`). If you want S1 to proceed while S0 is decomposed,
say so ??the current order (S0 gates S1) is yours and stands until you change it.
No motor, no camera, no new process device.
**Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT
flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

I read the plan against the project's files (`docs/`, `archive/peer/`, `archive/WORKLOG.md`, `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`). Findings below; every one carries a file and line.

---

# PRIOR-ART REVIEW — S0 decomposition (`docs/cycle27-plan.md` Pre-decided 25)

**The DIRECTION survives.** Decomposing a twice-failed stage into saved sub-steps is mandated, not prior-arted: CLAUDE.md §3 rule 3, `docs/cycle27-plan.md:391` (Pre-decided 23), and the cycle-43 retrospective's own verdict — *"Pre-decided 23 correctly forced a decomposition plan"* (`archive/peer/2026-09-19-retrospective-cycle43.md:212`). Nothing in these files has tried and abandoned a staged, save-per-step S0. What is already on file is **four of the five sub-steps' content**, and the plan's central mechanism has a failure record.

---

## PART A — THE DIRECTION

### A1 — `already-measured`: S0-a's cold reading has been taken SEVEN times, and it is **1**, not 0

S0-a exists to detect a "cold-0 / preloaded-1 pair" (`docs/cycle27-plan.md:405`). Its condition (i) — *a byte copy of `OpReport_v3.vi`, read COLD in a fresh LabVIEW instance, before any edit* — is exactly what both failed runs already did, immediately after killing and restarting LabVIEW:

> `tools/bench/build_s0_closeref_v3.log:10-12` — `fresh(): killing LabVIEW pid 9396` … `fresh(): new LabVIEW pid 20240`
> `:13-14` — `PASS A1 ARM: the scratch is a byte copy of OpReport_v3` … **`PASS A2 ARM: the scratch is RUNNABLE before anything is changed ExecState 1`**

The same pre-edit reading, each in its own freshly restarted instance: `:60` (`OpReport_v4`), `:109` (`OpWireSource_v6`), and `:168` (`OpReportAll_v1`, quoted in `archive/peer/2026-09-19-s0v3-execstate0.md:54`). Run 1 has three more: `tools/bench/build_s0_closeref_v1.log:15`, `:59`, `:103`. An unrelated op reads the same way — `tools/bench/build_opconnectfromwire_v0.log:49` `PASS W8 ExecState 1 before the copy`.

So the pair S0-a is armed to find **cannot occur**: the cold reading is 1, and the 0 appears after the edit *inside the same instance*. Pre-decided 14a's artefact (`docs/cycle27-plan.md:148-156`, `tools/bench/diag_d0_execstate_preload.log`) was measured on the 473 KB original and its 98 subVI call sites; these op stubs are 5-node VIs that link cold. Binding note (i)'s embargo — *"No S0-c script may be cut before S0-a's two readings are on file"* (`:413-414`) — is already discharged for the half that carries the verdict.

**To release this:** show that the `PASS G1/A2 … ExecState 1` lines above were *not* cold or *not* in a fresh instance. The `fresh(): new LabVIEW pid …` line immediately preceding each is what you must defeat.

### A2 — `contradicted`: S0-c's stop rule halts the chain on a state three files call NORMAL — including the plan's own note (ii)

> **Plan**, `docs/cycle27-plan.md:407` — "c1 = For Loop only … **The first sub-step whose ExecState drops STOPS the chain**"
> **`archive/WORKLOG.md:86-87`** — "**A bare For Loop makes its target show BROKEN afterwards — that is correct, not a defect**, since nothing has wired `N` or its tunnels yet."
> **`docs/toolkit-capabilities.md:412-413`** — "**ExecState was already 0 immediately after `for_loop`**, because an empty For Loop has no `N`. A broken VI mid-assembly is the *expected* state, not a failure."
> **`docs/toolkit-capabilities.md:417`** — "1. create the empty For Loop — **ExecState drops to 0, which is normal**"

The plan cites the first of these itself, two rows below the criterion it contradicts: note (ii), `docs/cycle27-plan.md:415-417`, "`archive/WORKLOG.md:86-87` (a bare For Loop breaks the VI)". As written, c1 reads 0, the chain stops, and c2/c3/c4 never execute — which also puts the probe `archive/peer/2026-09-19-retrospective-cycle43.md:192` calls *"exactly the discriminating test"* (`remove_bad_wires_scripted`-then-recheck) behind a gate that cannot be reached.

**To release this:** show the c1 criterion is not "ExecState must not drop" — e.g. by rewriting it as a *predicted* 0 with the pass condition on the artefact and the count, not on ExecState.

### A3 — `contradicted`: S0-d drops one of the three gates the cycle-43 disposition adopted, and Pre-decided 22 still states the superseded one

> **S0-d**, `docs/cycle27-plan.md:408` — "handles flat ±100 counted from call 1 **AND** private-byte drift ≤ 5 MB"
> **cycle-43 disposition**, `archive/peer/2026-09-19-priorart-s0-closeref.md:701-704` — "replaced by the three gates v1 carries: **G-A no `error 2` in 20 consecutive calls** of each repaired op · G-B handles flat ±100 from call 1 · G-C private bytes |drift| ≤ 5 MB. **All three must pass.**"
> **STATUS.md NEXT** — "S0 gates are now **G-A no error 2** / G-B handles flat from call 1 / G-C private bytes ≤5 MB drift (cycle-43 judgement)"

G-A is the gate that the released `FIXED: already-measured` line was written against (`…priorart-s0-closeref.md:719`). Separately, the same plan file still carries the criterion that disposition replaced: `docs/cycle27-plan.md:385` — S0's pass criterion "20 consecutive calls ⇒ LabVIEW handle count flat (±100)" — unamended, so the file now states three different S0 acceptance criteria at `:385`, `:408` and `:701-704` of the review it released.

**To release this:** restore G-A to S0-d, or show in writing why a repaired op that raises `error 2` in 20 calls should still be accepted.

### A4 — `unread-evidence`: `docs/toolkit-capabilities.md:400-443` and `tools/recipes/build_opreportall_v1.py` are the record of this exact construction, and S0-c consults neither

They appear in item 25 only as a file to *update* at S0-e (`:409`). They contain the answer S0-c is built to obtain (see B4), and one thing S0-c cannot get without them: a **positive control** — the same For-Loop-over-`References` construction, on this same op family, measured returning to `ExecState 1`.

Also unapplied, from a review the plan cites as its own record: the falsifier at `archive/peer/2026-09-19-s0v3-execstate0.md:140-142` (re-read `Wire.Is Broken?` *after* the `ExecState` read, which forces the compile — "two property reads", never taken) and the full-diagram wire census at `:130`, `:148`. S0-c's per-step instrumentation is `ExecState` alone, which is the instrumentation the same review closes by calling insufficient: *"this run's instrumentation could not see the failure it was measuring"* (`:164`).

---

## PART B — THE ARTIFACT

### B1 — `already-failed`: every S0-c step must SAVE a VI whose ExecState is 0, and that save path has failed repeatedly, most recently 12 hours ago

This is the finding that hits the decomposition's core promise — *"each ending with a saved artefact and its md5"*, *"The first FAIL stops the chain and leaves the file that shows the failure on disk"* (`docs/cycle27-plan.md:400-401`).

> `tools/gscript.py:2065-2068` — `if exec_state(target) == 0: if allow_broken: return gui_save(target)` / `raise RuntimeError("refusing to save a BROKEN VI - SaveInstrument blocks forever on one")`

c1's artefact is a bare For Loop, i.e. ExecState 0 by A2 above. So `g.save()` either refuses it or diverts to the keystroke save — whose failure record is long and current:

> `tools/bench/build_d1_routeb_v7_run10.log:367` — "`gui_save(SCRATCH_routeb_065508.vi): file mtime did not move after Ctrl+S on every candidate window`" (run 10, 2026-09-19 ~07:2x — the failure that killed E3)
> and the same error at `tools/bench/build_keystone.log:903`, `tools/bench/cycle3b_toolkit.log:78`, `tools/bench/extract_chain.log:10`, `tools/bench/gpukernel_chain.log:227`, `tools/bench/keystone_discovery.log:29`, `tools/bench/label_copy_clfn.log:16`

It is intermittent, not dead (`tools/bench/gpukernel_chain.log:320` "checkpoint saved"), which is worse for a chain whose contract is that a file always lands. Note the history: this was raised as F4 `already-failed` on run 10's prior art, **refuted by cycle 42, and the refutation was wrong** — corrected at `archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`, with the callee rule written into `docs/cycle27-plan.md:350-356` (Pre-decided 21(f)) precisely so this is quoted from the callee next time. Refuting it a second time would be the third pass over the same ground.

**To release this:** name, per S0-c sub-step, which save path persists an ExecState-0 file and what its evidence of success is — or re-order S0-c so every saved artefact is runnable.

### B2 — `helper-exists`: S0-b's profiler is built, and its traverse half is already measured

S0-b asks for "≥20 calls, kernel handles from call 1 AND private bytes per call" on the unrepaired ops, output to a new `tools/bench/s0b_refleak_profile.json`. That script exists:

> `tools/bench/s0_hygiene_probe.py:80-91` `mem()` → `(handles, private_bytes)`; `:161-171` the 20-call loop printing `call {i}: nodes={n} handles={h} private={pb/1e6} MB`; `:185-193` the same for `report_all(Diagram)`; run on a scratch copy of the route-B original, original md5 gated (`:151`, `:211`).

Its per-call series is already on disk — `tools/bench/s0_hygiene_probe_run2.log:75-97` (`count(Node)`) and `:101-123` (`report_all(Diagram)`, handles **+9**, private **−0.1 MB**, no `error 2`) — which is where the plan's own "call 0 is the 473 KB VI load" citation comes from. So the traverse-only half of S0-b needs no run; only the **"interleaved with mutations, S3w-like"** part is new, and even that has a precedent harness: `tools/bench/handle_audit.py:69-70` phase D, "10x drop_subvi + revert (a mutating erdosmiller op)", logged at `tools/bench/handle_audit.log:7`.

**To release this:** state that S0-b extends `s0_hygiene_probe.py` (adding the mutation interleave and the JSON dump) rather than writing a new profiler, and that the pure-traverse series is read from `run2.log` instead of re-run.

### B3 — `already-measured`: the per-step ExecState table S0-c would produce was produced on 2026-09-13, with its numbers

> `docs/toolkit-capabilities.md:400-402`
> ```
> empty for_loop              ForLoop=1 LoopTunnel=0 Wire=17 Property=2 ExecState=0
> build_property INSIDE loop  ForLoop=1 LoopTunnel=0 Wire=17 Property=3 ExecState=0
> wire() across the boundary  ForLoop=1 LoopTunnel=1 Wire=18 Property=3 ExecState=1
> ```
> `:409` — "the tunnel also **restored ExecState 1** | the auto-indexed array supplies `N`, which is why the loop was broken until then"
> `:432-438` — the full 1→7 build with `ExecState` per step, ending "7 wire References across the boundary LoopTunnel 0->1, **ExecState 0->1** <- the array supplies N"

That is c1 → c2 → c3 measured, on the same `References` array and the same op family, and it is the **positive control** the failing runs lack. The instrumentation is a recipe, not a one-off: `tools/recipes/build_opreportall_v1.py:87-90` (`snap()` prints every count plus `ExecState`), `:135-136` ("3 empty For Loop — predict: ForLoop 0->1; **ExecState 0 is EXPECTED** - an empty loop has no N"), `:158-160` ("predict: LoopTunnel 0->1, Wire +2 …, and **ExecState 0->1 because the array supplies N**"), `:41` ("Saves only when ExecState == 1").

The live question this makes visible — and which S0-c as written will not answer — is why the identical construction read `ExecState 1` at `toolkit-capabilities.md:438` and reads **0** at `tools/bench/build_s0_closeref_v3.log:87` after the branch landed with `LoopTunnel #642 IndexMode AS READ 1`. A c1→c4 chain with no reference to the passing instance measures the failing side twice.

**To release this:** show that the 2026-09-13 sequence differs from S0-c in a way that makes its numbers inapplicable — and if it does, that difference is the experiment, not c1.

### B4 — `already-failed`: S0-c preserves run 2's edit ORDER, which is the order the project's own recipe warns against

> `tools/recipes/build_opreportall_v1.py:28-29` — "**BUILD ORDER - tunnels before nodes. Nodes-first leaves the VI broken across more steps, which is what made an earlier probe misdiagnose itself.**"
> `docs/toolkit-capabilities.md:415-418` — "Build order (**the user corrected this — tunnels before nodes**): 1. create the empty For Loop … **2. wire the array into the loop** — the tunnel appears and `N` is resolved 3. build the Property nodes inside the body"

S0-c is c1 loop → c2 node inside it → **c3** the array branch: nodes before the tunnel. That is precisely run 2's sequence — `tools/bench/build_s0_closeref_v3.log:74` (loop created), `:77` (`Close Reference #324` reparented into the body), `:80` (the `References` branch) — split across four saves. Splitting a sequence does not change it; nothing in item 25 changes the order that failed twice.

I state the limit of this finding plainly: the executed 2026-09-13 sequence *also* placed its node inside the body before the boundary wire (`:437` step 6 → `:438` step 7) and still returned `ExecState 1`, so "nodes-first" is not itself proven fatal. What is unaddressed is that the plan keeps run 2's order while both the prose rule and the cycle-43 disposition (`archive/peer/2026-09-19-priorart-s0-closeref.md:694-699`) point at the built route.

**To release this:** show the order is deliberate and why, or reorder c2/c3 so the tunnel exists before the node is reparented.

---

## Not a finding, recorded so it is not rediscovered

- **S0-e's `docs/REFERENCES.md` half is already written**: `docs/REFERENCES.md:144` — "## 4a. `Close Reference` in the traverse ops — WHY IT IS ABSENT, and what was measured about it (2026-09-19)", with the measured op census at `:151-159` and the WORKLOG/VI_SCRIPTING_GUIDE citations at `:163-165`. S0-e should amend §4a, not author it.
- **c4's instrument has a recorded limit**: `tools/gscript.py:1293-1295` records a bad wire into a `reference` sink that "**`remove_bad_wires` does not clear**". A c4 that ends at ExecState 0 does not by itself exonerate the wires.

---

```
PRIOR-ART: already-measured
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-failed
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
PRIOR-ART: already-failed
```

## Sources

(extract from answer)

## What was done with it

All eight findings ACCEPTED (cycle-44 judgement, 2026-09-19). None refuted. Release lines:

FIXED: already-measured - docs/cycle27-plan.md:434 - S0-a is WITHDRAWN: the stub's cold ExecState is 1 in seven measured runs, so the cold-0/preloaded-1 hypothesis is dead and the chain starts from the positive control instead.
FIXED: contradicted - docs/cycle27-plan.md:465 - an intermediate ExecState 0 is expected and no longer stops the chain; only the final state must read 1.
FIXED: contradicted - docs/cycle27-plan.md:453 - S0 now states ONE acceptance criterion (G-A no error 2 / G-B handles flat from call 1 / G-C private bytes <= 5 MB), superseding the bare +/-100 row.
FIXED: unread-evidence - docs/cycle27-plan.md:440 - the 2026-09-13 positive control and the unapplied Wire.Is Broken? falsifier are now S0's first two sub-steps.
FIXED: already-failed - docs/cycle27-plan.md:458 - no step saves a broken VI; artefacts at illegal states are DATA files and VI saves happen only at legal states.
FIXED: helper-exists - docs/cycle27-plan.md:451 - S0-b extends tools/bench/s0_hygiene_probe.py instead of authoring a new profiler.
FIXED: already-measured - docs/cycle27-plan.md:449 - the 2026-09-13 c1->c3 ExecState table is adopted as the positive control and replicated, not re-derived.
FIXED: already-failed - docs/cycle27-plan.md:448 - the node-before-tunnel order is now a named diff candidate in S0-alpha, not a repeated construction choice.


## Launch gate - NO RECIPE (explicit opt-out)

No stop record was armed for this review. `tools/prior_art_review.py` was run with `--no-recipe`,
and its mandatory reason is recorded here verbatim:

    NO-RECIPE: no sub-step script for S0-a..S0-e exists yet; this review gates whether any of them may be cut - CLAUDE.md 3 split-big-work rule 3

This is an opt-out, not a release. It frees no recipe and discharges no verdict; the only release
lines are the two `guard_cycle.py` already validates, and neither of them is this.
