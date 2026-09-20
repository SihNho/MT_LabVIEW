# priorart-d1-s1-stage

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.2474  in 38 / out 31479 / cache-create 205226 / cache-read 2815988  (433s, 30 turn(s))
- **date:** 2026-09-19 21:33:09
- **outcome:** ANSWERED (437s)
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
---
type: plan
status: current
date: 2026-09-19
cycle: 27
kind: build
supersedes: [docs/cycle21-plan.md]
tags: [d0, d1, d2, delivery, gpu, unattended]
---

# Cycle 27+ ??the user's re-plan answer: **D0 ??D1 ??D2, in that order**

**User, 2026-09-18 14:2x, answering the third consecutive outcome review:** *"D0, D1, D2 ?쒖꽌濡?吏꾪뻾?섎㈃ 醫뗭쓣??"*
Asked what "option 1" would even change when the original already has its stop path and `save N xyz traces.vi`,
the answer was: nothing ??option 1 as written was wrong. The real first step is **D0** from `docs/cycle15-plan.md`
(the plan the user approved 2026-09-17), then D1, then D2. This file names the order and the pre-decided points;
the content of D0/D1/D2 stays where it is written (`docs/cycle15-plan.md` 짠"D1 = ??, `docs/pre-rig-master-plan.md`
rows 1.1??.9, `docs/d1-route-b-plan.md`).

## The three deliverables (definitions unchanged)
- **D0** ??a **plain, unmodified copy** of the original under `claudeDev`, driven by the harness with nobody present
  through stages 0?? (panel parameters ??configure ??bead-pick clicks on the image display ??done button ??save
  path/name ??experiment loop), run, stopped, restarted. What is built is the **harness**, not the VI. (Rule 1c';
  `lv_gui.ps1 -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`.)
- **D1** ??inside that copy: acquisition loop 쨌 **GPU-kernel tracking loop** 쨌 file-writer loop 쨌 frame accounting 쨌
  stop/shutdown; stages 0?? untouched; N1 = the 10,043-frame fixture comparison of `GPU_kernel_v1.vi` first.
- **D2** ??scheduler 쨌 motor (`SetCommand_signed.vi`) 쨌 ASI/focus loop 쨌 display; then the Phase-2 dry-run checks.

## Pre-decided (apply, cite the number, do not re-ask)
1. **Order is D0 ??D1 ??D2.** No cycle works on D1 while D0's done-when is open, none on D2 while D1's is.
2. **No further process device** (user, 08:53) ??still the standing order. A retrospective naming one is a finding.
3. **D0 done-when** = a script (one runner, one bgrun, one log) that: copies the original (md5 before AND after,
   original untouched), opens the copy, sets panel parameters by VI Server, runs it, drives the pick stage by the
   approved GUI clicks, presses done, types the save path/name, lets the experiment loop run N seconds, stops it
   through the VI's own stop control, verifies the `.tra` output exists and is non-empty, closes, and repeats once
   (restart). Every step gated with a prediction contract.
4. **Motor boundary for D0 ??P2 IS DONE (2026-09-18 14:3x??6:0x, user present).** The user ran the plain copy
   (`claudeDev\Track_D0_copy_20260918.vi`) by hand through the pick stage into the experiment loop; the magnet
   bound was measured (panel Data-Entry range 0??0.84, nothing in front of `MOV`); **controller-side limits are
   now in force** ??PI `TMN 0 / TMX 39` (RAM; the gate's session-start hook re-applies and verifies them) and ASI
   `SL/SU` = live position 짹2 mm (persistent) ??and `tools/motor_gate.py --session start|end` + the live test
   10/10 (`tools/bench/motor_gate2_live.log`). **Unattended D0 runs may therefore start the VI**, on the
   ASSUMPTION (flagged for the user, rule 2c) that the controller limits are the protection the user meant by
   "洹몃윭硫??덉떖?????덉쓣 寃?媛숈???: every D0 run begins with `motor_gate.py --session start` (refuse the run if
   the readback fails) and ends with `--session end` is NOT called (limits stay on; the user's "release at end"
   applies to the interactive tool sessions, not to unattended runs). Known facts to re-check after the first
   unattended run: `TMX?` still 39 and `W X` unchanged (does the original's startup reload parameters or re-zero?).
   Opening the copy needs the original preloaded read-only (`tools/bench/p2_open_copy.py` pattern).
5. **Motor-limit check A** (`docs/motor-limit-assurance-plan.md` 짠A.1; its missing primitive is now BUILT:
   `OpFsTunnelTerm_v0.vi`, firefighter 2026-09-18 13:36, 38/38) runs **alongside D0 on the D0 copy** ??it is
   read-only and needs no motor. It is the precondition of the P2 live check, so it is not deferred behind D0.
6. **GPU first** in D1 (`GPU_kernel_v1.vi`); CPU top level is a later, second deliverable. Fixture comparison N1
   before any D1 build.
7. **Failed prediction ??a SINGLE `-Agent claude -Role hypothesis` arm** (opus / effort max, web on), which
   `guard_peer.py` accepts as discharging the failed prediction since the **CLAUDE.md 짠5 amendment of
   2026-09-18** ("Codex's roles move to Claude sub-sessions" + "D3 IS AMENDED"), taken because codex's weekly
   quota reached 9 %. **`-Dual` is NOT the default any more**: it stays available and is the right call only
   when a claim about our OWN tools needs a second opinion that does not share our priors. (This line said
   "Failed prediction ??`-Dual` review" until 2026-09-18 18:1x; corrected by the cycle-32 material session.)
   Firefighter ladder per CLAUDE.md 짠3 (runner-decided).
8. `docs/cycle21-plan.md` is superseded by this file; `docs/cycle15-plan.md` stays the content reference.
9. **EVERY GUI action is capture ??locate ??act ??capture ??confirm (user, 2026-09-18 17:5x, watching the live
   v4 run: *"GUI 而⑦듃濡?以묒뿉??諛섎뱶??罹≪쿂 ?대?吏 鍮꾧탳?섎뒗寃??꾩슂?좊벏"*).** Capture BEFORE and locate the target
   *in that capture* (colour/template match, OCR of the label, or the control's live screen rect); act; capture
   AFTER and CONFIRM the expected change (button state, a counter, a new window) before the next step. No change
   ??FAIL and stop. **Derived or remembered coordinates are never clicked blind** ??a coordinate that worked on
   another copy of the same VI is not evidence about this one, and a window-rect comparison says nothing about
   control positions inside the panel. Read the panel rect live (maximise first). Implemented by
   `tools/bench/d0_locate.py` + `clickprobe`; this is what turned v4's 13/3 into v5's 39/1: v4 reused v3's panel
   geometry and clicked the V6 copy's (1114,915) while this copy's button centre was (1177,862) ??the click
   landed at **(??3, +53) px** from the button, i.e. 63 px left and 53 px below it.
   <!-- MEASURED: 1114??177 = ??3, 915??62 = +53 (screen y grows downward). A SECOND, duplicate item numbered 9
        stated this deviation as "(??4, +51) px"; both components were wrong and the duplicate numbering made
        "cite the number" ambiguous. Merged into this item and the figure corrected by the cycle-34 judgement
        session, 2026-09-18, resolving doc_ingest contradiction P1 (archive/ingest/2026-09-18-ingest-2026-09-18.md). -->
10. **The live motor-gate test to cite is the 16:0x RETEST, 10/10** (`tools/motor_gate.py` session-start repairs
   the reference after `SPA` with `RON 1 0` + `POS 1 <same value>`; self-test 76/76). The earlier 15:37 run
   scored 8/10 with L4 a FALSE PASS and is **superseded** ??`tools/bench/motor_gate2_live.log` holds the 15:37
   numbers, so a citation of that file alone reads 8/10 and must say which run it means.
   <!-- Resolves doc_ingest contradiction P3 by labelling the runs rather than picking a winner: both numbers are
        true of different runs. Judgement session, cycle 34. -->
11. **One cycle number per run.** The 18:08??8:13 D0 v5 run is labelled "cycle 31" in one place and "cycle-32" in
   another because the runner's own counter (`tools/bench/cycle_runner.log`, cycles 19/20) and this narrative's
   counter disagree. A cycle number is only a label ??so **identify a run by its timestamp and
   log path, never by a cycle number alone**. Do not renumber history.
   <!-- Resolves doc_ingest contradiction P4. Judgement session, cycle 34. -->
12. **`## Pre-decided` lines are edited by JUDGEMENT sessions.** A material session that believes one is stale
   reports it and stops (retrospective-cycle31 F7, disposed).
13. **`docs/cycle15-plan.md`'s `## Pre-decided` 1?? (`:118-130`) BIND the next D1 build, and BOTH authorisation
   flags stayed `False` ???좑툘 REVISED FOR THE `Z/dZ` ROW BY 13a BELOW; read both.** Judgement, cycle 35, answering the route-B read-out's OPEN ("does a `status: paused` plan
   still bind?"). It does: that file's own frontmatter (`docs/cycle15-plan.md:5-7`) says the section "stays
   authoritative for the D1 queue/shift-register questions ??nothing here is retracted", and item 8 above already
   makes cycle15 the content reference. So, for the three NO-ROUTE rows of route-B run 3
   (`tools/bench/build_d1_routeb_v0_run3.log:385-387`): `#1359`/`#29874`'s shift registers **MOVE WITH THEIR
   NODES** into loop 1.2 (`add_shift_reg` + `wire_sr`, `index_mode 1` kept exactly as the original has it ??
   cycle15 item 2), and `Z/dZ` ??`#2222` t0 is **REORDERED** before the S3-ct reparent of `ControlTerminal #403`
   (by index, `OpConnectNested_v1`, sink `is_source` FALSE ??cycle15 item 3). The recipe's two constants
   (`tools/recipes/build_d1_routeb_v0.py:242`, `:247`) carry the comment "only the judgement session may turn it
   on": **the judgement session declines, and the answer is "no", not "not yet".** `SR_QUEUE_AUTHORISED` and
   `TEMP_SINK_AUTHORISED` stay `False`; a build that needs either to be True is the wrong build.
13a. **REVISED ??`TEMP_SINK_AUTHORISED` is `True` FOR THE `Z/dZ` ROW ONLY; `SR_QUEUE_AUTHORISED` stays `False`
   permanently.** Decided by the cycle-36 judgement session, which recorded it **only in STATUS** ??prior-art
   finding A1 (`archive/peer/2026-09-18-priorart-d1-routeb-run5.md:242-253`) was right that this binding file was
   never amended; the cycle-37 judgement session amends it here, per Pre-decided 12. Grounds, both MEASURED:
   - Item 13's shift-register half was **confirmed by run 4** ??both registers were created MOVED WITH THEIR NODES
     (`tools/bench/build_d1_routeb_v1_run4.log:315-316`). `SR_QUEUE_AUTHORISED` stays `False` for good; its grounds
     are now confirmed rather than assumed.
   - Item 13's `Z/dZ` half rested on the **REORDER**, which the machine has refuted twice: `ControlTerminal #403`
     has no node index on `Diagram[56]` and `OpConnectNested_v1` addresses `Diagram[].Nodes[].Terminals[]` only
     (`?쫞un4.log:163-164`) ??a fact already on file at `tools/recipes/build_opconnectctl_v0.py:9-14` and, with
     external sources, at `archive/peer/2026-09-17-zdz-wirecut-opus.md:130`; and the node moves at
     `build_d1_routeb_v1.py s3():617-631` cut w730, **not** the `#403` reparent
     (`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md`). A decision resting on a premise measured false is
     not preserved by leaving it alone.
   So the `Z/dZ` row runs through the **temporary-sink** path as the discriminating test. It authorises **no new op
   and no new device** (Pre-decided 2 untouched): `OpCreateEqual_v0` ??`wire_control` ??`OpConnectFromWire_v0` ??
   delete + `remove_bad_wires_scripted`, all built weeks ago.
   ?좑툘 **The flag alone is not sufficient.** Prior-art A3 (`?쫜riorart-d1-routeb-run5.md:269-287`) measured that the
   v1/B2 RETRY returns at `build_d1_routeb_v2.py:1278` whenever `node_index_on()` is `None` ??always true for a
   ControlTerminal ??so `:1296` is never evaluated and the flag is INERT. The RETRY is therefore kept **only as a
   logged control** (prior-art B4): it records its NO-ROUTE reason as a `fact` and **falls through** to the
   temporary sink instead of returning.
   ?좑툘 **The flag's stated grounds were mis-cited** (prior-art A2). `build_d1_routeb_v2.py:305-308` justifies the
   refusal with a 1055 modal from an invalid terminal refnum (`docs/NAMES.md:473-480`), but
   `docs/toolkit-capabilities.md:64` records that `OpCreateEqual_v0` fetches both operands INSIDE the op so no
   terminal refnum crosses COM ??the cited text is the **fix** for that defect, not evidence of it. The real hazard
   is different and **silent**: `src_names=()` ??`Names=[]` ??`Get Outputs` empty ??`Index Array[0]` returns a
   default refnum with no error. It is bounded: a silent bad refnum leaves the sink BARE, which the row's own
   discriminator reads ??a measurable outcome, not a modal that hangs an unattended run.
   **Why the created `Equal?` and not the `bare_named_sinks` variant** (prior-art B3): the created node is made and
   deleted inside one operation and borrows nothing live, so even a failed cleanup can only leave a broken wire that
   `remove_bad_wires_scripted` and the ExecState gate catch. The bare-named-sink variant borrows a **live** sink on
   the original's own body diagram, where an incomplete cleanup would leave the original's input wired to `Z/dZ` ??
   a rule-1a computation change on a path this build does not otherwise touch.
14. **A route-B run that ends at ExecState 0 MEASURES before it deletes.** Run 3 deleted its own working copy
   ("a broken VI is never written", `?쫞un3.log:487`) and destroyed the evidence with it, so the ExecState-0 cause
   on record (`tools/recipes/build_d1_routeb_v0.py:131-135`) is an advance INFERENCE, never a measurement ??the
   run's own census is explicitly labelled "not an explanation" (`?쫞un3.log:428`). From now on, before any delete
   and on the live broken VI, the recipe **re-reads `ExecState` with the ORIGINAL preloaded read-only** (item 14a
   below) and writes both readings to the log. ?좑툘 **Corrected within the same cycle, by measurement**: this item
   first mandated the `Wire.Is Broken?` reader (6371004) and cycle15 item 4's bare-terminal census. Both are now
   measured useless here and are **WITHDRAWN** ??the census returned an IDENTICAL 375 bare named input terminals
   over 170/170 diagrams on a KNOWN-GOOD copy, so it discriminates nothing
   (`tools/bench/diag_d0_execstate_preload.log:26-36`, `:65-75`), and `Wire.Is Broken?` cannot be run read-only:
   the only built readout follows a `Terminal.Connect Wire` **write**, which `docs/NAMES.md:898-909` measured
   turns an ExecState-1 scratch into 0. Capturing evidence before deleting a broken copy stays right; those two
   instruments are not it. **A value returned beside an error has
   measured nothing**: run 3's three conditional terminals read `wire 0` *with* `error 1055: Property Node in
   OpLoopEndRef_v0.vi` attached (`?쫞un3.log:416-418`), so that 0 is UNREAD, not zero, and must be reported as
   UNREAD. Deleting the working copy stays the rule; capturing the reading first is now part of it.
14a. **An `ExecState` read taken WITHOUT the ORIGINAL preloaded is UNREAD, not "broken".** MEASURED, cycle 35
   (`tools/bench/diag_d0_execstate_preload.log`, 9/9, rc=0): three BYTE-IDENTICAL files ??the original,
   `claudeDev\Track_D0_copy_20260918.vi`, and a copy made during the run (all md5
   `c39f36e0675339673b707c59f0784fee`, 471,257 B) ??each read **ExecState 0 opened cold** in a fresh instance
   (`:14`, `:53`) and **ExecState 1 in the same instance once the ORIGINAL had been opened read-only first**
   (`:44-45`, `:84`). A cold read therefore measures **subVI linkage**, not the legality of anything we built, and
   `Track_D0_copy_20260918.vi` is **not damaged** ??D0's delivery record stands. So: every `ExecState` gate opens
   the ORIGINAL read-only first (the `tools/bench/p2_open_copy.py` pattern, already required by Pre-decided 4 for
   *opening* a copy ??it governs *reading* one too), and any ExecState 0 taken cold is logged **UNREAD** and
   re-taken under preload before a single word of diagnosis. Cost of the preload, measured: ~+20k handles per
   condition versus ~+6k cold (`?쫜reload.log`), so restart LabVIEW between conditions.
16. **Route-B run 3's `ExecState 0` is NO LONGER EVIDENCE that the build produced a broken VI.**
   `tools/recipes/build_d1_routeb_v0.py` copies from `Min_Track N beads V6_ParallelLoop.vi` (`:172`) and **never
   preloads it** ??every other mention is `md5()` or `shutil.copy2` (`:285`, `:306`, `:462`, `:1413`), the working
   copy being opened directly at `:310` ??while its S5 gate is `g.exec_state(TARGET)` at `:1289`, i.e.
   `GetVIReference(??.ExecState` on an instance with nothing preloaded (`tools/gscript.py:1920-1921`). By item 14a
   that gate has been reading linkage. The advance attribution at `:131-135` ("these cannot produce `ExecState 1`")
   is therefore **read from a void gate**. ??**The control WAS repeated on route B's own original**
   (`tools/bench/diag_d1_execstate_preload.log`, 7/7, rc=0): a byte-identical claudeDev scratch copy of
   `Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, = the recipe's pinned
   `ORIG_MD5` at `:173`) read **COLD 0** (`:13`) and **preloaded 1** (`:33`). The effect is not specific to the
   3StateClamping family.
   ?좑툘 **THREE CORRECTIONS from the adversarial review** (`archive/peer/2026-09-18-execstate-linkage.md`, ANSWERED,
   opus/max, $2.8794), all ACCEPTED ??an earlier draft of this item said the run-3 attribution was "unsupported",
   which was too strong:
   (a) **ExecState 0 was OVER-DETERMINED, not unsupported.** The attribution never rested on ExecState alone:
       `s1q` was not executed (`:1255-1257`) and S4b/S4s were skipped (`:1274-1275`), leaving three While loops
       with unwired conditional terminals ??a compile-time break independent of any gate. What died is the
       *gate's* ability to discriminate, not the explanation. ?좑툘 But that independent support is itself
       **measured-with-error**: run 3 read those conditional terminals as `wire 0` *with* `error 1055: Property
       Node in OpLoopEndRef_v0.vi` attached (`?쫞un3.log:416-418`), and by item 14's own rule a value returned
       beside an error is UNREAD. So neither side is settled; the cheap test below is, correctly, what settles it.
   (b) **NO PRELOADED BUILD RUN.** The obvious remedy ??re-run the build with the original preloaded ??ADDS a
       hazard it does not remove: the working copy can CROSS-LINK to the in-memory original's subVIs and is then
       written by `g.save(TARGET)` at `:1291`. Preload stays confined to **read-only** ExecState diagnostics, in a
       step that never saves. A preload can also MASK a genuine break by supplying subVIs the saved VI would not
       resolve on its own, so a preloaded 1 is necessary, never sufficient. Rivals not yet excluded:
       `GetVIReference` options `0` vs the `0x10` search bit; our own ops measured flipping 1 ??0
       (`docs/NAMES.md:898-911`); load/compile settling.
   (c) **The cheapest discriminating test, and the next cycle's first act: restore the BASELINE ExecState read
       into route B's `s1()`.** `tools/recipes/build_d1_v0.py:461` has it; `build_d1_routeb_v0.py:302-316` dropped
       it. One line, no preload, no extra LabVIEW: it reads the untouched copy in the recipe's OWN instance and
       flow, separating "born 0" from "the build made it 0". Do this **before** spending another 9-minute run.
17. **NO VI-WIDE remove-broken-wires may run inside a multi-row build pass.** Decided by the cycle-39 judgement
   session on measurement, and it applies to every route, not just route B. The restructure deliberately leaves
   wires cut between S1d/S3 and S3w's rewiring pass (`tools/bench/build_d1_routeb_v4_run7.log:274-280` shows
   `#2222`'s inputs cut and awaiting rewiring), so a VI-wide reaper called from the row loop deletes the build's
   own scaffolding rather than debris. Measured cost: a **??6 VI-wide Wire delta** across a single row's
   temp-sink bracket (`?쫞un7.log:360`), with `#2222` t3/t4 afterwards reading `'<no such terminal>'` ??
   `.get()`'s ABSENT default, not a wrong-but-valid node. **Run 5 is the natural control**: it returned NO-ROUTE
   at `build_d1_routeb_v4.py:1606-1609` and so never reached the `delete_object`/reaper pair at `:1665-1669`, and
   its `#2222` t2/t3/t4/t5 ALL wired; runs 6 and 7 reached it and they failed. Removing the reaper moves the
   build TOWARD rule 1a ??it stops deleting wires the original has. Applied as K1 in
   `tools/recipes/build_d1_routeb_v5.py:1760`. **The ban is on a reaper called from INSIDE the row loop**, not on
   the operation: v5's two surviving VI-wide calls, the pre-pass one at `:694` and S5's at `:2242`, are EXONERATED
   by the same control ??run 5 executed both and its rows wired. Gate any future one route-A style
   (`tools/recipes/build_d1_v0.py:1112-1128` already treats it as hostile: it runs it once, then checks which of
   its own wires died). ?좑툘 **`gscript.net_map` is therefore BANNED as a wire-counting instrument** ??it
   calls `remove_bad_wires_scripted(target)` internally (`tools/gscript.py:2507-2516`, `:2568-2588`), so using it
   for a "safer per-diagram count" re-fires the very reaper this item removes, twice per row. Count per diagram
   with `build_track_v6_core.walk:84-92` instead, carrying its caveat (it sees only wires touching a terminal on
   that diagram). The diagram-scoped `AbstractDiagram.Remove Wire Loose Ends` (`RemWireLooseEnds`, method 6375409,
   class `AbstractDiagram` 16503) is NOT built and is not authorised by this item.
   ??**CONFIRMED BY REPLICATION, and the K1 separator is RETIRED from the critical path** (cycle-41 judgement,
   2026-09-19). The control is now 2 횞 2 and it is clean: the two runs WITH the in-loop reaper (runs 6 and 7) lost
   `#2222`'s terminals, and the two runs WITHOUT it ??run 8 (`?쫣5_run8.log:411-413`, t3/t4/t5) and run 9
   (`tools/bench/build_d1_routeb_v6_run9.log:464-468`, t0/t2/t3/t4/t5 with `Is Broken? FALSE` on t3 and t4) ??wired
   every one. A one-off no longer explains it. The scratch-copy K1 separator (`terms_of` + `count` ??
   `remove_bad_wires_scripted` ??repeat) was queued to settle this question and is **no longer worth a dispatch**:
   it would confirm a result two builds already replicate. Item 17 stands as written; do not re-open it, and do not
   re-word it to "anywhere between the first cut and the last rewire" ??that re-wording was conditional on a K1
   result that is no longer needed.
18. **A build ledger reports SURVIVING wires, never attempts.** Cycle-39 judgement, accepting
   `archive/peer/2026-09-19-routeb-run7-index-shift.md` Q4: route B's WIRED count was a mixture ??`wire_sr` and
   plain `wire` rows recorded no uid and no readback, and `wire_control`'s `next(..., 0)` collided "unwired" with
   "no such terminal", so a logged `wire 0 -> 0` was never evidence that a terminal exists. Every wiring row
   records the uid it created and reads it back with a `None` sentinel; every run prints a survival census
   (`set(o["uid"] for o in g.report_all(TARGET,"Wire"))` against the ledger's uids) immediately after the S3w
   ledger line ??**after the ledger, not after S5, because no route-B run has ever reached S5**. Applied as K3 in
   `build_d1_routeb_v5.py:1130`, `:2036`, `:2120`. A ledger number quoted without its survival census is a
   structural claim only (CLAUDE.md "structural is not functional").
   ?좑툘 **AMENDED by the cycle-40 judgement session, on measurement: the census may NOT be read with
   `report_all(Wire)`.** Run 8 proved that call is itself an `error 2` victim ??it raised
   `error 2 ??Traverse for GObjects.vi->OpReportAll_v0.vi | Class Operator:Traverse (Traverse Failed)` after 50
   uids had been claimed (`tools/bench/build_d1_routeb_v5_run8.log:364`), so the one measurement run 8 existed to
   produce came back UNREAD and the ledger's `WIRED 53` is still an attempt count. Read the census instead from the
   walk the recipe already holds ??assert `wmap(TARGET, d)[node][2][t]["wire"] == claimed_uid` over the four
   diagrams the build touches (20 / 21 / 24 / 56) ??which is cheaper than a VI-wide traverse and strictly more
   probative, because it names the terminal each claimed wire was supposed to land on
   (`archive/peer/2026-09-19-routeb-run8-predictions.md` Q4). The requirement of item 18 is unchanged; only the
   instrument is.
   ?좑툘 **AMENDED AGAIN by the cycle-41 judgement session ??a census reports FOUR buckets, and "unread" is one of
   them.** Prior art on run 9's recipe (`archive/peer/2026-09-19-priorart-d1-routeb-run9.md`, NOT NOVEL) raised two
   defects in the walk-based census as first cut, both accepted and both now binding on every future census:
   - **B2 ??an unreadable census must say UNREAD, never "gone".** `diag_index` IS `report_all(Diagram)`
     (`tools/recipes/build_d1_v0.py:357-358`), the very call `error 2` kills, so a census that lets it raise would
     print a confident `0 survived / 51 gone`. Run 9 proves this was not hypothetical: **all five** `diag_index`
     calls raised and the census printed `0 survived / 0 bare / 51 unread of 51 claimed`
     (`tools/bench/build_d1_routeb_v6_run9.log:365`, reasons `:366-:418`). The honest null is what made `error 2`
     the named blocker instead of a phantom wiring catastrophe.
   - **B4 ??uid inequality is NOT wire death.** A cross-boundary wire is several segments with different uids
     (`docs/toolkit-capabilities.md:68`), so a non-zero uid that differs from the claimed one is survival.
   **The contract**: every claimed row is classified `EXACT` (reads the claimed uid) 쨌 `SEGMENTED` (reads a different
   non-zero uid ??survival) 쨌 `BARE` (reads no wire ??the only genuine loss) 쨌 `UNREAD` (the walk raised, the address
   will not resolve, or the terminal entry is absent ??never counted as a loss). Headline =
   `CENSUS: <EXACT+SEGMENTED> survived / <BARE> bare / <UNREAD> unread of <claimed> claimed`, then one line per
   non-EXACT row. **The census must never raise.** The four diagram walks are taken ONCE and cached ??never per row:
   a per-row `fresh=True` re-walk is the traverse volume that is a candidate cause of run 8's 6 ??11 `error 2`
   worsening. Implemented in `tools/recipes/build_d1_routeb_v6.py:2160-2256`.
   ?좑툘 **A census of 51 UNREAD rows does not confirm survival and does not refute it.** Run 9's `BARE = 0` is
   VACUOUS ??nothing was read back ??so route B's `WIRED 54` is STILL an attempt count, exactly as it was after
   run 8. Do not quote it as a survival number.
19. **The `Z/dZ` temp-sink bracket's correct Wire-count null is `+1`, NOT `0` ??so `build_d1_routeb_v5.py:1842`
   asserts an inverted null and must read `_b_ok = (_wddelta == 1)`.** Decided by the cycle-40 judgement session
   from a read of our own code, not from the peer that raised it (`archive/peer/2026-09-19-routeb-run8-predictions.md`
   Q2 is a hypothesis; this item is the confirmation). The call order inside the bracket is `:1613` count ??
   `:1616` `create_equal` ??`:1668` `wire_control` ??`:1751` `OpConnectFromWire_v0` ??`:1774` `delete_object` ??
   `:1810` count ??`:1842` gate. The branch runs **only under `if not zw`** (`:1597`), i.e. only when the source
   control carried NO wire, so the before-count at `:1613` is taken while the control is still bare; `wire_control`
   at `:1668` then CREATES the sink wire, `OpConnectFromWire_v0` only BRANCHES that same net at delta 0
   (`docs/toolkit-capabilities.md:70`; run-8 log `:356`), and the wire SURVIVES the delete
   (`tools/bench/build_d1_routeb_v5_run8.log:358`). One new wire is exactly what a correct bracket is *for*.
   The comment at `:1601-1605` ??"every write in the bracket is a BRANCH off an existing net ??so the expected
   delta is 0" ??is therefore **false at its premise** and is corrected with the gate.
   ??**`Z/dZ` t0 WAS WIRED in run 8** and the J2 row was failed by the gate, not by the machine: `:418` reads
   (a) source identity True ??the control's own wire 29238 IS the sink wire, exactly one reciprocal source
   terminal ??(b) per-diagram delta +1 = the correct value, (c) `Is Broken? False`, (d) sink read back 29238.
   Do not re-open the `Z/dZ` route on the strength of that FAILED label. ?좑툘 This does **not** disturb run 7's
   `??6` VI-wide delta or item 17 that rests on it: ??6 is not +1, and a wrong null in one direction is not
   evidence about a deficit in the other.
   ??**CONFIRMED BY THE MACHINE, run 9, 2026-09-19** (`tools/bench/build_d1_routeb_v6_run9.log:360`, `:464`): with
   the gate reading `== 1` the `Z/dZ` t0 row **PASSES J2** ??`_wddelta == 1`, source identity True (the control's own
   wire 29238 IS the sink wire, exactly one reciprocal source terminal), per-diagram Diagram[24] `(31, 32, 1)`,
   `Is Broken? False`, sink read back 29238 ??and the row is logged WIRED. This item was decided from a code read in
   cycle 40 and is now a measurement; the `Z/dZ` route is CLOSED as a question. Item 19 needs no further test.
20. **`error 2` is the ONLY thing between route B and a delivered D1, and run 10 attacks it with the census it also
   needs ??ONE edit, one runner.** Cycle-41 judgement, from run 9. The state of the evidence:
   - It is **not** handles (refuted: healthy at 51,349 / 51,353, crashed at 35,551 / 35,555 ??
     `archive/peer/2026-09-19-routeb-run8-predictions.md` Q3). LabVIEW `error 2` = memory / reference allocation.
   - It is **not** the census instrument. Cycle 40 blamed `report_all(Wire)` and replaced it; run 9's replacement
     died the same death, five times over (`tools/bench/build_d1_routeb_v6_run9.log:364`). Every victim across runs
     8 and 9 is a **traverse** ??`report_all(Diagram)`, `report_all(WhileLoop)`, `report_all(Wire)`,
     `count(LoopTunnel)` ??i.e. `Traverse for GObjects.vi`, whatever the class.
   - It is **temporal within a run**: the same diagram walks that wire 54 rows early all fail by census time. That is
     the one asymmetry two runs agree on, and it is the only lead not yet tested.
   So run 10 = `tools/recipes/build_d1_routeb_v7.py`, cut from v6's bytes, with **ONE edit**: immediately after the
   S3w ledger line, **save the working copy, close it, RESTART LabVIEW (standing authority, CLAUDE.md 짠3), reopen the
   saved copy in the fresh instance, and run the four-bucket census there.** Nothing else changes ??not the wiring
   pass, not the gates, not the per-bead maths (rule 1a); saving and reopening changes no computation.
   **This is one action doing two jobs, which is why it is the right next build**: it is the only route to a census
   that can READ, and it is simultaneously the discriminating test for the cumulative-allocation hypothesis STATUS
   has carried as UNCONFIRMED for two cycles. A fresh-instance census that reads CONFIRMS it (and tells us the 11
   failing wire rows are fixed the same way ??by phasing the build across instances); one that still fails REFUTES
   it and moves the cause onto the VI or the traverse itself. Either answer is worth the run.
   ?좑툘 Do **not** "fix" the census by reading each wire at claim time. That is an attempt count with extra steps and
   item 18 exists to forbid exactly it ??a survival census must be read AFTER the wiring pass.
   ?좑툘 The save is of a **working copy under `claudeDev`**, mid-restructure and possibly broken; that is allowed and
   normal (rule 1 governs originals). Preload stays confined to read-only ExecState diagnostics (Pre-decided 16b), so
   the census step opens the saved copy WITHOUT preloading the original ??it needs diagram walks, not `ExecState`.
   If a mid-run restart turns out to be unreachable over our COM path, that is an `OPEN:` for judgement, not a
   licence to fall back to a same-instance census.
   ?뵶 **SUPERSEDED BY ITEM 21 ??run 10 ran and item 20's mechanism never executed.** The E3 save diverted to
   `gui_save` and died (`tools/bench/build_d1_routeb_v7_run10.log:367`), so no restart, no reopen and no
   fresh-instance census ever happened; phasing across instances is still UNTESTED. Its premise is also no longer
   the live one: item 21 replaces "temporal, therefore restart" with a named, testable CAUSE. Do not re-cut a
   save?뭨estart?뭨eopen build on the strength of item 20 alone.
21. **`error 2` is a REFNUM LEAK in our own traverse ops, and run 11 repairs it instead of working around it.**
   Cycle-42 judgement, from the mandatory failed-prediction review of run 10
   (`archive/peer/2026-09-19-routeb-run10-error2-class.md`, ANSWERED, claude/hypothesis opus max, $5.5451, 639 s),
   which REFUTED the cycle's own diagnosis on our own log lines. Five things now bind every future route-B build:
   - (a) **`error 2` is LabVIEW's generic "Memory is full"** (NI KB kA00Z0000019KhWSAU), and the meter for it is
     **LabVIEW's private bytes**, never the handle count. Every previous "handles refute memory" argument in this
     project ??including STATUS's "healthy at 51,349, crashed at 35,551" ??is a **category error, not a
     refutation**. Do not repeat it.
   - (b) **The live cause is a leaked GObject reference per matched object** inside `report_all` / `count`
     (`.claude/skills/labview-automation/references/com-driving.md:305-312`; `docs/REFERENCES.md:126` records the
     `Close Reference` that was REMOVED). `count(Diagram)` matches 170 objects and `count(Node)` 626, so ~30
     successful `report_all(Diagram)` calls leak thousands of refnums before the traverse that finally fails.
     ?좑툘 **AMENDED 2026-09-19 by the cycle-43 (firefighter) judgement session ??NOT SUPPORTED BY MEASUREMENT.**
     20 횞 `report_all(Diagram)` (= 3,400 matched objects that this line predicts leak) moved kernel handles **+9**
     and private bytes **??.1 MB**, with **no `error 2`** (`tools/bench/s0_hygiene_probe_run2.log:121-123`); the
     `count(Node)` window's +215 handles is +202 in call 0 = the 473 KB VI load, not the traverse (`:75`, `:95`).
     The per-matched-object leak arithmetic above is therefore withdrawn as "the live cause"; `error 2`'s cause
     returns to OPEN, and the S0 repair is NOT predicted to close it. (c) below is untouched ??the repair stays
     owed as rule compliance. The kernel handle count is blind to VI Server refnums (`tools/gscript.py:227-228`),
     so any future leak gate reads PRIVATE BYTES alongside handles, and handles from call 1 (excluding the load).
   - (c) **Closing those references is owed anyway.** CLAUDE.md's reference-hygiene rule already requires every VI
     Server reference to be closed by whoever opened it, so restoring the `Close Reference` is a RULE-COMPLIANCE
     REPAIR of an existing op ??not a speculative fix and not a new "?μ튂" under the user's 2026-09-18 08:53 order.
     It is applied unconditionally, whatever it does to `error 2`.
   - (d) **A traverse INDEX is not a stable key ??worse than the archived +1.** `FRAME_BODY_UID=639` reads index
     **43** at `tools/bench/build_d1_routeb_v7_run10.log:44` and **56** at `:352`, a shift of **+13 inside one
     instance with no restart**. Any census or route keyed on a diagram index is unsound. The key is the diagram
     **UID**; where uid?뭝ndex conversion is unavoidable it must be re-read, never cached across a mutation.
   - (e) **The cycle-42 traverse census was a SELECTION ARTEFACT and is withdrawn.** "`report_all(Diagram)` is
     0-for-21, it has never once succeeded" was produced by grepping for lines that PRINT `error 2`, which can only
     find failures; the successes are at `run10.log:39`, `:44`, `:69`, `:352`, `:354` and ~29 `move_in` calls at
     `:150-167`. A census whose instrument can only observe one outcome measures nothing ??the same error CLAUDE.md
     names under "absence in what you happen to be looking at is not evidence of absence".
   - (f) **A claim about what OUR OWN code does must quote the CALLEE, not the call site.** The reviewer's own
     proposed rule, and the one that would have prevented this cycle's `inference-over-measurement` violation: the
     cycle-42 `REFUTED:` lines said "v7 saves over COM with `g.save`, not `gui_save`" from v7's call site, while
     `tools/gscript.py:2065-2067` diverts `g.save(?? allow_broken=True)` to `gui_save()` on any cold `ExecState`
     read. Both `REFUTED:` and `FIXED:` releases, and any sentence of the form "our tools do/cannot do X", carry the
     callee's `file:line`. Form-checking cannot catch this ??`docs/violation-decisions.md` records why no device was
     built for it.
   **Run 11** = one runner, one log, three unconditional phases: (1) the review's own discriminating test ??repeat
   `report_all(TARGET,'Diagram')` on a pristine scratch copy in a clean instance, logging the iteration index AND
   private bytes, until it raises or a bounded count is reached; (2) the same measurement again with the
   `Close Reference` repair applied; (3) the route-B build from v7's bytes with **E3 removed** (no save, no restart,
   no reopen ??back to v6's in-instance census) and the repair in place. Nothing branches on a result.
15. **`Count` is NOT a bead count, and no harness may gate on it.** MEASURED, cycle 35
   (`tools/bench/diag_count_indicator_run4.log`, 16/0; now `docs/NAMES.md` 짠`Count`): `Count` is uid **28051**, a
   front-panel **CONTROL** (`indicator` False), not an indicator. Its terminal is a **SOURCE** driving wire 30530
   into `Comparison #29111` (`Equal?`, terminal `x`) and into `SelectorTunnel #31929` of `CaseStructure #28709`,
   both on Diagram #15795, inside `Sequence #15649` ??`EventStructure #15544`. It is **written** by two implicit
   `Property` nodes labelled `Count` whose `Value` is a SINK (#32191 on Diagram #12960, #30688 on Diagram #28741
   inside that same case structure). So it is a counter variable parked in a control and steered by the event
   structure ??which is why three registered picks leave it reading 1
   (`tools/bench/drive_original_copy_v4.log:790`, `?쫣5.log:181`). **That reading was never a fault**, and
   retrospective-cycle31 F6b is answered: v5's method ??counting the three red markers the VI draws ??stands, and
   D1 must neither gate on `Count` nor "fix" it. No other panel object is a bead count either (`Total cycle #`
   30309, `# of Points` 10008, `Bead Pos` 11831, `Total Lost Frames` 421, `# of Auto-Reset` 9768 ??`Bead Pos` is
   the only bead-related one). Not fully established, and not on D1's path: whether anything *else* writes it ??
   #32191's owner chain ends at a `FlatSequenceFrame` with `owner_uid 0`, and `report_all('GlobalVariable')`
   fails on this VI with **error 1092**.

## Pre-decided ??ADDED 2026-09-19 17:4x (user, after the overnight route-B loop): D1 IS BUILT IN SAVED STAGES
22. **CLAUDE.md 짠3 "Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact" applies to D1
    from now on.** No more full-length `build_d1_routeb_vN.py` runs. The D1 build is a CHAIN of stage scripts, each
    starting from the previous stage's SAVED file in a FRESH LabVIEW instance (original preloaded read-only for every
    ExecState read ??Pre-decided 14a/16), each ending with a save under `claudeDev` and an md5 in its log:
    | stage | saved file | pass criterion |
    |---|---|---|
    | **S0 hygiene** | repaired traverse ops (`OpWireSource_v6.vi` / `OpReport_*` with `Close Reference` restored; **new versions, the old files untouched**) | 20 consecutive calls in one script ??LabVIEW handle count flat (짹100); `docs/REFERENCES.md` updated |
    | S1 | `D1_s1_copy.vi` (copy of the original, fixture TIFF writer + the 3 re-dropped nodes deleted) | md5 recorded; ExecState 1 preloaded; node count = original ??deletions |
    | S2 | `D1_s2_loops.vi` (three fresh While loops + 3 subVIs dropped) | +3 loops +3 subVIs, ExecState read |
    | S3 | `D1_s3_moved.vi` (21 nodes + 8 control terminals moved, `Z/dZ` reorder, 8 shift registers) | counts per 짠2c; ExecState read |
    | S3w-a ??S3w-e | `D1_s3w_a.vi` ??(re-wiring in batches of ??5 rows of the 66) | each batch's rows WIRED (`Wire.Is Broken?` FALSE), ledger saved per batch |
    | S4?밪6 | `D1_s4_census.vi` ??`Track_v6_D1_GPU.vi` | census, ExecState 1 preloaded, saved |
23. **Two consecutive failures of one stage at the same place ??that stage is decomposed further before any retry**
    (CLAUDE.md 짠3 rule 3). The runner's firefighter trigger now ignores `_vN` suffixes.
24. The firefighter cycle ordered by the user on 2026-09-19 does S0 and S1 (and S2 if S1 passes cleanly) ??nothing
    beyond; it ends with the saved files listed and their md5s, or with the exact failing stage.
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

    ?좑툘 **AMENDED THE SAME DAY BY ITS OWN PRIOR-ART REVIEW ??`archive/peer/2026-09-19-priorart-s0-decomp.md`,
    NOT NOVEL, 8 findings, ALL EIGHT ACCEPTED AS `FIXED:` (cycle-44 judgement, 2026-09-19).** The direction survives
    (`:235`: a staged save-per-step S0 has never been tried and abandoned) but four of the five sub-steps duplicated
    work already on file. What binds from here is this block, not the table above:
    - ?뵶 **S0-a IS WITHDRAWN. Its premise is dead: the op stub reads `ExecState` 1 COLD in a fresh instance, measured
      SEVEN times** (`tools/bench/build_s0_closeref_v3.log:13-14` `PASS A2 ARM ??ExecState 1` immediately after
      `fresh(): new LabVIEW pid`, also `:60`, `:109`, `:168`; `??v1.log:15`, `:59`, `:103`;
      `build_opconnectfromwire_v0.log:49`). A cold-0 / preloaded-1 pair therefore **cannot occur** for these stubs,
      Pre-decided 14a does not reach them, and the conclusion is the opposite of the one S0-a was written to test:
      **the stub is born legal and OUR EDIT breaks it.** (Finding A1.)
    - ?윟 **THE POSITIVE CONTROL IS THE LEAD, and S0 has never used it.** This exact construction ??a For Loop +
      `Close Reference` around the same `References` array, on the same op family ??was built on 2026-09-13 and ended
      **`ExecState` 0 ??1**: `docs/toolkit-capabilities.md:400-402`, `:409`, `:432-438`, built by
      `tools/recipes/build_opreportall_v1.py` (instrumentation at `:87-90`, `:135-136`, `:158-160`, `:41`).
      (Findings A4, B3.) One build of this thing works and four do not, so the question is a **DIFF**, not a mystery.
    - **The chain is now 慣 ??棺 ??款, then b, then d/e:**
      | sub-step | what it does | saved artefact | pass criterion |
      |---|---|---|---|
      | **S0-慣 DIFF** ??no LabVIEW at all | diff `tools/recipes/build_opreportall_v1.py` (works, ends 1) against `tools/recipes/build_s0_closeref_v3.py` (fails, ends 0) and their logs; enumerate EVERY ordered construction difference ??node-vs-tunnel order (`build_opreportall_v1.py:28-29`, `docs/toolkit-capabilities.md:415-418` vs `build_s0_closeref_v3.log:74`,`:77`,`:80`), which terminals are wired and in what order, whether `remove_bad_wires_scripted` is called, what is saved and when | `docs/s0-diff.md` | the table exists and names each difference with both `file:line` sides. **This runs FIRST and costs no LabVIEW** |
      | **S0-棺 REPLICATE** | re-run the 2026-09-13 construction UNCHANGED on a fresh scratch copy; after EACH edit read `ExecState` **and then re-read `Wire.Is Broken?`** (the falsifier left unapplied at `archive/peer/2026-09-19-s0v3-execstate0.md:140-142`, with the wire census at `:130`/`:148`); save the result | the rebuilt op VI + md5, or ??if the state is illegal and cannot be saved ??the readings as a DATA file | ends `ExecState` 1 and the VI SAVES. **If it now reads 0, the positive control has rotted and THAT is the finding** |
      | **S0-款 PORT** | apply the differences S0-慣 named, **one difference per saved artefact**, until the repaired op is reached or one of them reproduces the 0 | one artefact per difference | the first difference that flips 1 ??0 is the cause, and its artefact is on disk |
      | **S0-b MEASURE** | unchanged in purpose, but it **EXTENDS `tools/bench/s0_hygiene_probe.py`** (`:80-91`, `:161-171`, `:185-193`; precedent `tools/bench/handle_audit.py:69-70`) ??only the mutation interleave is new | `tools/bench/s0b_refleak_profile.json` | completes and prints both meters per call. Measurement only (finding B2) |
      | **S0-d/e** | acceptance + record | the accepted op; `docs/REFERENCES.md` 짠4a **amended**, not authored (`:144` already exists) | the ONE criterion below |
    - **ONE S0 acceptance criterion, stated once** (finding A3 ??the plan carried three): **G-A no `error 2` 쨌 G-B
      kernel handles flat 짹100 counted FROM CALL 1 쨌 G-C LabVIEW private-byte drift ??5 MB.** Adopted by the
      cycle-43 disposition (`archive/peer/2026-09-19-priorart-s0-closeref.md:701-704`). The bare "짹100" of the
      Pre-decided 22 S0 row is **superseded by this line**; handles alone are blind to VI Server refnums
      (`tools/gscript.py:227-228`).
    - ?뵶 **NO STEP MAY SAVE A BROKEN VI** (finding B1). `tools/gscript.py:2065-2068` refuses or diverts to
      `gui_save`, which has failed at seven logged sites (`tools/bench/build_d1_routeb_v7_run10.log:367`,
      `build_keystone.log:903`, `cycle3b_toolkit.log:78`, `extract_chain.log:10`, `gpukernel_chain.log:227`,
      `keystone_discovery.log:29`, `label_copy_clfn.log:16`) ??and run 10 proved the one refutation of it wrong
      (`archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`). VI saves happen only at LEGAL states; where a step
      necessarily ends illegal, **its saved artefact is a DATA file** (readings, census, md5s). The user's rule says
      "intermediate VI/data", so this satisfies it ??but it is a narrowing of note (i) and is flagged to the user.
    - **An intermediate `ExecState 0` is EXPECTED and no longer stops the chain** (finding A2): a bare For Loop
      breaks the VI by design (`archive/WORKLOG.md:86-87`, `docs/toolkit-capabilities.md:412-413`, `:417`). Only the
      FINAL state must read 1. The original c1 criterion would have halted on normal behaviour and c2/c3/c4 would
      never have run.
    - **A `c4` at `ExecState 0` exonerates nothing**: `tools/gscript.py:1293-1295` ??`remove_bad_wires` does not
      clear a bad wire into a `reference` sink.

26. **S0-款 RUNS BEFORE S0-棺, and its FIRST ported difference is D2/D4 (node CREATED IN THE BODY, not copied and
    reparented).** Judgement, cycle 45, 2026-09-19, on the fact S0-慣 produced ??not on a preference. `docs/s0-diff.md`
    enumerates 23 ordered construction differences between the build that ends `ExecState` 1
    (`tools/recipes/build_opreportall_v1.py`, 2026-09-13) and the one that ends 0 four times
    (`tools/recipes/build_s0_closeref_v3.py`). Three grounds, in the order they bind:
    - (a) **The loop machinery is EXCLUDED as the common cause.** S0 run 2's stage 3 failed with **no loop created,
      no new tunnel and an EXACT branch** (`tools/bench/build_s0_closeref_v3.log:178`, `:190-192`, `:202`, `dw=0`) and
      still read `ExecState 0`. A cause common to all four failures therefore cannot be the For Loop. S0-棺 as written
      ("replicate the 2026-09-13 construction unchanged", `:449`) replicates precisely that machinery, so it is no
      longer the cheapest discriminating test ??it is re-ordered BEHIND 款, not cancelled. It remains the right test
      if 款 exhausts the diff without reproducing the flip, because then the positive control itself is in question.
    - (b) **D2/D4 is the only candidate present in every failure and absent from the success.** v3 COPIES the
      `Close Reference` node out of `KernelBuilder_v1.vi` and reparents it (`build_s0_closeref_v3.py:587` ??
      `tools/gscript.py:1479-1558`; `:528`/`:453` ??`tools/recipes/build_d1_v0.py:318-335`), where the working build
      CREATES it in the body (`build_opreportall_v1.py:144-149` ??`tools/gscript.py:2188`). This matches the observed
      signature exactly ??every wiring gate passes, the branch reads EXACT, `Is Broken? False`, and the VI is still
      illegal ??i.e. alternative #2 of the mandatory review (`archive/peer/2026-09-19-s0v3-execstate0.md`): **a broken
      NODE that a wire reader cannot see.** Per CLAUDE.md "when a diagnosis is GUESSED twice, build the reader", this
      is not another inference: porting the difference IS the measurement.
    - (c) **The other two candidates are worse first tests, for reasons already on file.** D1 (edits landing on the
      Move fixture `MOVE_DST`, `tools/gscript.py:1518`, `:1536-1543`, `:78-80`) has counter-evidence ??
      `tools/bench/build_opconnectfromwire_v0.log:58` reached `ExecState 1` inside that same hook, so D1 alone is not
      sufficient to break a VI. D7 (`remove_bad_wires_scripted` never called in v3; called twice at
      `build_opreportall_v1.py:130`, `:133`, recorded `docs/toolkit-capabilities.md:433`) can only CONFIRM, never
      exonerate, because `tools/gscript.py:1293-1295` says `remove_bad_wires` does not clear a bad wire into a
      `reference` sink. D7 is therefore the SECOND ported difference, not the first.
    **Binding on every 款 sub-step**: one difference per saved artefact; an intermediate `ExecState 0` is expected and
    does not stop the chain (finding A2); the FINAL state must read 1 before the VI is saved, and a step that ends
    illegal saves a DATA file of its readings instead (finding B1). The first difference that flips 1 ??0 is the
    cause and its artefact stays on disk.
    ?좑툘 **This cycle is bound by the outcome review's accepted condition** (`archive/peer/2026-09-19-outcome-review-20260919.md:153`,
    disposed at `:171`): a cycle that ends without S0 saved files and md5s in a log escalates the stop-and-re-plan.
    A 款 step that ends illegal satisfies it with its DATA artefact, not with prose.
    ?뵶 **26(b) IS SUPERSEDED BY ITEM 27 ??款1 was never launched and must not be re-cut as written.** 26(a) SURVIVES
    and is strengthened: the loop machinery is not merely unimplicated, it is already ON DISK and legal.

27. **THE POSITIVE CONTROL HAS NO ARTEFACT ??S0's remaining justification is rule compliance alone, so S0-b
    (MEASURE THE UNREPAIRED OPS) RUNS NEXT AND 款/棺 BOTH WAIT ON IT.** Judgement, cycle 45, 2026-09-19, from the
    Phase-1 census (`tools/bench/s0_op_census_run2.json` md5 `362f1e52??, 32 pass / 0 fail;
    `tools/bench/s0_op_census.log`). Four measurements, none of them inference:
    - (a) **`OpReportAll_v1.vi` DOES NOT EXIST** (`tools/bench/s0_op_census.log:98`). The build that
      `docs/toolkit-capabilities.md:400-402`, `:409`, `:432-438` records as the one that ended `ExecState` 0 ??1
      left nothing on disk. Pre-decided 25's finding A4/B3 ??"one build of this thing works and four do not, so the
      question is a DIFF" ??therefore rests on a **claim with no artefact behind it**, and item 26(b) inherited that.
    - (b) **The one on-disk relative carries the loop but NOT the node.** `OpReportAll_v0.vi` (md5 `ffcec2c7??) has
      `ForLoop #113`, body `Property #114??115`, `References` w524 ??`LoopTunnel #511` `IndexMode 1` (inner w421),
      and **no `Close Reference`** (`?쫈ensus.log:105-119`), reading `ExecState` **1** cold. This also EXPLAINS S0 run
      2's stage 3 ??"no loop created, no new tunnel, EXACT branch of w421" ??the loop and tunnel were already there
      and w421 is that tunnel's inner wire. The detector is not blind: it finds `#157 'Close Reference'` in
      `KernelBuilder_v1.vi` (`:295`, `:313-314`).
    - (c) **There is no built route to CREATE a `Close Reference` primitive.** `tools/gscript.py:2188` is
      `build_property` and creates a Property node (`:2195`, `:2198-2202`, `:2225-2227`); `docs/vi-server-ids.json`
      carries no `Close` id. So 26(b)'s "create in the body" is not one ported difference but four (it drags D1, D3
      and the node class), and as literally written it is **unexecutable**. Copy-and-reparent out of
      `KernelBuilder_v1.vi` has been the only route all along ??which is why all four failures share it.
      ?좑툘 Not settled, and not to be restated as impossible: prior art B3 measures that `OpCreateEqual_v0.vi` places a
      primitive on a NAMED SUBDIAGRAM, FUNCTIONAL 23/0 (`docs/toolkit-capabilities.md:64`, `:66`), so the capability
      CLASS exists. `tools/recipes/build_s0_gamma1.py:19-25` says "nothing in this fleet can" and that sentence is
      **over-broad** ??correct it if the recipe is ever revived.
    - (d) **款1's own prior art agrees and is ACCEPTED** (`archive/peer/2026-09-19-priorart-s0-gamma1.md`, NOT NOVEL,
      9 findings / 5 slugs, claude/priorart opus high, $4.1991): A2 ??26(a) excludes the loop machinery and 款1
      rebuilds it; A3 ??four differences, not one; A4/A4b ??the post-compile `Is Broken?` re-read is missing.
    **Therefore the order is corrected to what the cycle-43 disposition already ordered and three cycles have not
    done ??MEASURE FIRST.** S0's premise is measured unsupported (Pre-decided 21(b) as amended: 20 횞
    `report_all(Diagram)` moved handles +9 and private bytes ??.1 MB with no `error 2`), `Close Reference` may be a
    NO-OP on GObject refnums (note (v)), and the repair is owed only as rule compliance (21(c)). So:
    - **S0-b runs next**, EXTENDING `tools/bench/s0_hygiene_probe.py` (finding B2) with the mutation interleave only:
      the UNREPAIRED ops under a build-shaped workload, ??0 calls, kernel handles FROM CALL 1 and LabVIEW private
      bytes per call, against the single criterion **G-A no `error 2` 쨌 G-B handles flat 짹100 from call 1 쨌 G-C
      private-byte drift ??5 MB**.
    - **Pre-decided 25(iv) is now the live branch, not a hypothetical**: if the unrepaired ops meet G-A/G-B/G-C, the
      ops are **ACCEPTED AS THEY ARE with the measurement as the record**, S0 closes, and S1 begins. CLAUDE.md's
      hygiene rule states its acceptance as a measurement, so passing it is compliance, not evasion. **Only the user
      may overturn this reading of their own rule ??it is flagged in STATUS NEXT.**
    - Only if S0-b FAILS a meter does a node-creation route become worth its cost; then the first step is prior
      art's A2 form ??start from `OpReportAll_v0.vi`, which already has the loop and tunnel, and change ONLY the
      node's origin ??never 款1 as written.
    - **S0-棺 is withdrawn** in the same breath as (a): a construction whose output does not exist and whose
      distinguishing node is absent from its only on-disk relative cannot be "replicated unchanged".

28. **G-C IS EVALUATED ON TRAVERSE-ATTRIBUTABLE DRIFT, WHICH NEEDS A MUTATION-ONLY ARM ??S0-b's `+34.6 MB` is
    UNATTRIBUTED and must not be read as a leak.** Judgement, cycle 45, 2026-09-19, on S0-b's own numbers
    (`tools/bench/s0b_refleak_profile.json` md5 `b3ddf21fc39735e329c61477dbcac03e`;
    `tools/bench/s0b_refleak_profile.log:61-64`, 13 pass / 1 fail).
    - Measured: **G-A PASS** (no `error 2` from any call, `:62`) 쨌 **G-B PASS** (handles 54,619 ??54,600 = **??9**
      counted from call 1, `:61`, `:63`) 쨌 **G-C FAIL** (private 617.3 ??652.0 MB = **+34.6 MB** against a 5 MB
      limit, `:61`, `:64`).
    - **The confound is on the record and was reported by the measuring session, not discovered later**: the
      build-shaped interleave MUTATES ??20 Property nodes created, node count 626 ??645 ??so `+34.6 MB` is traverse
      leak AND VI growth together, ??.7 MB per created node if it is growth alone. The only contrast on file is
      traverse-only: **??.1 MB** over 20 calls (`tools/bench/s0_hygiene_probe_run2.log:121-123`).
    - **G-C's purpose is to ask whether OUR TRAVERSE OPS leak.** A workload that also grows the VI by 20 nodes does
      not measure that, so the criterion is not satisfied *or* violated until the growth is subtracted. Completing
      the measurement is not reinterpreting the gate; acting on `+34.6 MB` as a leak WOULD be
      `inference-over-measurement`, the very fault this item's parent (27) was written to stop.
    - **The discriminating arm, and the next act: MUTATION-ONLY.** The same 20-call loop, same scratch copy, same
      meters, with the `count`/`report_all` traverses REMOVED and the `build_property` mutations kept. Three arms
      then close the 2횞2: traverse-only **??.1 MB** (on file) 쨌 traverse+mutate **+34.6 MB** (on file) 쨌
      mutate-only (to measure).
      - mutate-only ??+34.6 MB ??the traverses contribute ~0, **G-C is met on traverse-attributable drift**, and
        Pre-decided 25(iv)+27 apply: the ops are ACCEPTED AS THEY ARE with the measurement as the record, S0 closes,
        S1 begins.
      - mutate-only ??0 ??the traverses DO leak under mutation pressure, G-C genuinely fails, the `Close Reference`
        repair is owed on measurement as well as on rule, and the route is 27's last bullet ??start from
        `OpReportAll_v0.vi`, change ONLY the node's origin.
    ?뵷 **IF THE REPAIR IS EVER REVIVED, THE FIRST PORTED DIFFERENCE IS D6, NOT D2/D4.** Recorded here by the cycle-45
    judgement session from `docs/s0-diff.md` D6, which the act-2 summary understated. The build that WORKS
    **DELETES the old consumers of `References` FIRST** ??`delete_object(OP,'IndexArray',0)` and both old Property
    nodes, `tools/recipes/build_opreportall_v1.py:129-133`, callee `tools/gscript.py:2234` ??and says why in its own
    source at `:127-128`: *"wiring it into a loop would need branch=True ??or, far better, delete the consumer FIRST
    and the source is free"* (recorded as steps 1?? at `docs/toolkit-capabilities.md:432-434`). The build that FAILS
    deletes **nothing**: diagram 0 still holds `Index Array #167`, `Property #241` and `Property #482` when the loop
    is built (`tools/bench/build_s0_closeref_v3.log:65`, `:70`). This fits the observed signature better than D2/D4
    does ??the S0 v3 짠2 arm measured the new branch as a **VALID** wire (sink w636 SEGMENTED, `Is Broken? False`,
    `LoopTunnel #642` `IndexMode 1` as read), which is exactly what a legal wire into an **illegal multi-consumer of
    a refnum array** would look like: no broken wire anywhere, and the VI still will not compile. D6 is also a
    genuinely single, cheap port (delete three nodes before wiring), unlike D2/D4 which drags D1 and D3.
    ?좑툘 This is a HYPOTHESIS built from a file diff, not a measurement ??it has never been run. It ranks the queue for
    a future cycle; it does not reopen S0, which closed on the three-arm result below.
    Both branches are decided here, so a material session applies whichever the arm returns; neither is a fresh
    judgement. ?좑툘 **Flagged to the user with 25(iv): accepting the ops on a completed G-C is judgement's reading of
    CLAUDE.md's hygiene rule, whose stated acceptance test is a measurement. Only the user may overturn it.**


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
  owner_c45m4: # ?윟 **RELEASED 2026-09-19 21:0x KST ??S0-b's MUTATION-ONLY ARM RAN AND S0 IS CLOSED.** `tools/bench/s0b_mutonly_profile.log` `BGRUN END rc=1 after 142s`, **13 PASS / 1 FAIL** (rc=1 IS the one FAIL, G-C on raw drift). `tools/bench/s0_hygiene_probe.py` extended a THIRD time (`--s0bmut`; prior-art B2 ??extend, never author): the `--s0b` 20-call loop with the three EXPLICIT traverse legs removed (`count(Node)` 626 matched/call 쨌 `report_all(Diagram)` 170/call 쨌 the UID-addressed `OpWireSource_v5` run) and `build_property` kept. Artefact **`tools/bench/s0b_mutonly_profile.json` md5 `6917c1cba61a403561de55a5ac0f5071`** (4,621 B); the `--s0b` artefact `b3ddf21f?? untouched. **THREE ARMS: traverse-only ??.1 MB 쨌 traverse+mutate +34.6 MB 쨌 mutate-only +34.5 MB** (`:61-65`, `:68-71`) ??they differ by **0.1 MB**, so the drift is VI growth (20 Property nodes, 626 ??645 ??1.7 MB each), not a traverse leak. G-A PASS (no `error 2`) 쨌 G-B PASS (handles ??2 from call 1) 쨌 G-C **MET on traverse-attributable drift**. ?좑툘 The arm is NOT traverse-free: `build_property` runs `report_all(Property)` twice internally (`tools/gscript.py:2196`, `:2225`) in BOTH arms, so those cancel. All three op md5s (`0743701a?? / `ffcec2c7?? / `5dc45a04??) and the original `2a78e17c?? UNCHANGED (`:78-81`); scratch `SCRATCH_s0bm_205858.vi` deleted; `ref_counts {'opened': 1, 'closed': 1, 'live': 0, 'cached_op_vis': 0}`; handles 33989 ??54394. `guard_peer` NOT armed (`FAILURE_RE` does not match `**FAIL**`).
  owner_c45m3: # ?윟 **RELEASED 2026-09-19 20:51 KST ??S0-b RAN AND SAVED ITS ARTEFACT.** `tools/bench/s0b_refleak_profile.log` `BGRUN END rc=1 after 157s`, **13 PASS / 1 FAIL** (rc=1 is the one FAIL, G-C). `tools/bench/s0_hygiene_probe.py` EXTENDED with a `--s0b` mode (prior-art B2: extend, never author). Artefact **`tools/bench/s0b_refleak_profile.json` md5 `b3ddf21fc39735e329c61477dbcac03e`** (6,487 B). Workload = 20 횞 (`count(Node)` ??`report_all(Diagram)` ??`OpWireSource_v5` UID-addressed ??`build_property` on the scratch copy), i.e. traverses INTERLEAVED with mutations. ?뵶 **G-A PASS (no `error 2`) 쨌 G-B PASS (handles 54619 ??54600, **??9**, counted from call 1) 쨌 G-C **FAIL** (private bytes 617.3 ??652.0 MB, **+34.6 MB**, limit 5 MB)** (`:61-64`, `:78`). Call 0 (the VI load) = handles 34289 / 609.5 MB, excluded as Pre-decided 27 requires. ?좑툘 **CONFOUND, unresolved and NOT decided here: the interleave MUTATES ??20 Property nodes were created (nodes 626 ??645), so the +34.6 MB is traverse-leak AND VI growth together; the traverse-only control (`s0_hygiene_probe_run2.log:121-123`, 20 횞 `report_all(Diagram)` = private ??.1 MB) is the contrast, not a decomposition.** All three op md5s and the original `2a78e17c?? UNCHANGED (`:71-74`); scratch `SCRATCH_s0b_204831.vi` deleted; `ref_counts {'opened': 1, 'closed': 1, 'live': 0, 'cached_op_vis': 0}`; handles 33992 ??54499. `guard_peer` is **NOT armed** by this log (`FAILURE_RE` does not match `**FAIL**`, checked). **S0-e was NOT done ??the brief makes it conditional on all three gates.**
  owner_c45m2_s0v3: # ?뵷 **BOTH RELEASED, RELOCATED VERBATIM (rule 4, cycle 45 act 3) ??`archive/2026-09-19-status-cycle45-relocate.md` 짠5 (`owner_c45m2`, the S0 phase-1 census) and 짠6 (`owner_s0v3`, S0 run 2 + its annotated `s0v3-execstate0` review).** One line each: the census artefact is `tools/bench/s0_op_census{,_run2}.json`; run 2 saved no VI and altered no op on disk.
  lock_history: # ?뵷 **RELOCATED VERBATIM (rule 4, cycle 44) ??`archive/2026-09-19-status-cycle44-relocate.md`** ??the superseded lock keys `owner_s0v1` / `owner_s0` (S0 runs 1 and 2) and `status_prev` / `owner_c42r10r` / `owner_c42r10` / `purpose_c41` / `purpose_c42` (D1 route-B runs 8, 9, 10 and the v6/v7 cuts). `owner_s0v3` below is the live one.
  owner:     # RELEASED 2026-09-19 06:01 KST ??run 9 ended `BGRUN END rc=1 after 1817s`, log `tools/bench/build_d1_routeb_v6_run9.log`. Acquired 2026-09-19 05:31 KST by the cycle-41 material session for **D1 ROUTE-B v6 RUN 9** ??`py tools/bgrun.py --material --max-min 45 --log tools/bench/build_d1_routeb_v6_run9.log -- py -u tools/recipes/build_d1_routeb_v6.py`. v6 sha256 `8dbb1e69ef83??, md5 `cb96a4df0ef71325880ff63aed47e8b9`, 2607 lines, `ast.parse` OK. Prior-art gate RELEASED (five `FIXED:` lines in `archive/peer/2026-09-19-priorart-d1-routeb-run9.md`, stop record RELEASED). Previous: released 2026-09-19 04:28 KST after run 8 ended (BGRUN END rc=1 after 1822s).
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
?뵷 **Cycle 43's firefighter header is DISCHARGED and RELOCATED VERBATIM (rule 4, cycle 45) ??
`archive/2026-09-19-status-cycle45-relocate.md` 짠3**: the one-page S0 decomposition plan exists (Pre-decided 25 +
26), S0-慣 is done, 款1 is written and reviewed. **S1/S2 still unstarted** (user's ordering, NEXT of 17:4x).
- ?뵷 **Cycle 43's three "what the machine knows" bullets RELOCATED VERBATIM (rule 4, cycle 45) ??
  `archive/2026-09-19-status-cycle45-relocate.md` 짠2**: the 횞4 post-wiring `ExecState 0`, the measured-unsupported
  leak premise (gates are now G-A/G-B/G-C), and the undisposed `s0v3-execstate0` conflict with its (a)/(b)/(c).
- ?뵷 **The S0 phase-1 census bullet and the 款1 prior-art disposition bullet are RELOCATED VERBATIM (rule 4, act 4)
  ??`archive/2026-09-19-status-cycle45-relocate.md` 짠9** (census artefacts `tools/bench/s0_op_census{,_run2}.json`;
  款1 review `archive/peer/2026-09-19-priorart-s0-gamma1.md`, 9 `FIXED:`, recipe WITHDRAWN, stop record RELEASED).
- ?윟 **S0 IS CLOSED (cycle 45, act 4) ??the unrepaired traverse ops are ACCEPTED AS THEY ARE, on measurement.**
  The mutation-only arm settles S0-b's confound: mutate-only **+34.5 MB** vs traverse+mutate **+34.6 MB**
  (traverse-only **??.1 MB**), i.e. the drift is VI growth, not a traverse leak ??**G-A/G-B/G-C all met on
  traverse-attributable drift**, and Pre-decided 25(iv)+27+**28's BRANCH-A** applies. Numbers and md5s: the
  released `owner_c45m4` lock key above. **RECORDED**, per 28: `docs/REFERENCES.md` 짠4a-bis (amended, not authored)
  and `docs/toolkit-capabilities.md` (after the `OpReportAll_v0` section) ??both carry the three-arm table with log
  paths and artefact md5s. **No `Close Reference` repair built, no new `_vN` op, every old op byte-identical.**
  ?좑툘 `error 2`'s cause stays OPEN (Pre-decided 21(b) as amended); the repair remains legitimate as rule compliance
  (21(c)) ??what the measurement removes is the claim that it fixes anything.
- ??**Retrospective cycle 43's `device-failed` (stop-record gate beaten by a rename) is DONE, cycle 44 ???뵷
  RELOCATED VERBATIM (rule 4, act 3) ??`archive/2026-09-19-status-cycle45-relocate.md` 짠8** (the repair itself: 짠1).
- Retrospective F1/F5: in the decomposition plan, the ARM (scratch discriminating test) becomes its own SAVED
  step whose FAIL stops the script ??run 2 spent three op stages replicating a failure the ARM had already measured.
- ??**The 4th outcome review IS DISPOSED ??the "undisposed" claim here was STALE and is corrected (cycle 45,
  measured).** `archive/peer/2026-09-19-outcome-review-20260919.md:171` carries a real prose disposition by the
  cycle-44 judgement session: **NOT a stop-and-re-plan**, because the review says so itself at `:153` ??*"the staged
  re-plan the rule demands has, in fact, already happened ??the user imposed it at 17:4x"* ??so CLAUDE.md 짠5's "on
  repetition the work stops for a re-plan" is discharged by the user's own staged-build order. ?좑툘 **What IS binding
  is the condition accepted in its place: "the next cycle must end with S0/S1 saved files and md5s in a log, or the
  stop-and-replan escalates to the project's continued existence."** Cycle 45 met it ??`s0_op_census_run2.json`
  (`362f1e52??), `s0b_refleak_profile.json` (`b3ddf21f??), `s0b_mutonly_profile.json` (`6917c1cb??), `docs/s0-diff.md`.
  **Three genuine USER-ONLY decisions from that review remain open and are NOT blockers**: OPEN 53's physical-zero
  question before any D1 motor-moving run; schedule-or-descope requirement 1; place-or-descope the item at its `:126`.
- ??The Pre-decided-25 prior-art bullet (`archive/peer/2026-09-19-priorart-s0-decomp.md`, NOT NOVEL, 8 findings,
  **ALL EIGHT DISPOSED/ACCEPTED** in cycle 44, gate verified) is ?뵷 **RELOCATED VERBATIM (rule 4, cycle 45) ??
  `archive/2026-09-19-status-cycle45-relocate.md` 짠4**, together with the deleted `SCRATCH_s0_180632.vi` note
  (6 `SCRATCH_routeb_*` crash copies remain, untouched). ?윟 **S0-慣 IS DONE ??`docs/s0-diff.md`: 23 ordered
  construction differences**, works (`build_opreportall_v1.py`) vs fails (`build_s0_closeref_v3.py`), both sides cited.
?뵷 **NEXT IS S1** (Pre-decided 22's stage table): from a copy of the original, delete the fixture TIFF writer + the
3 re-dropped nodes, save `claudeDev\D1_s1_copy.vi`, record md5, ExecState 1 preloaded. Its body already exists
measured (`build_d1_routeb_v7.py` s1/s1t, counts at `:74`) ??it is to be re-cut as a STAGE script, not a full run.
**FLAGGED FOR THE USER (rule 2c):** accepting the ops on a completed G-C is judgement's reading of CLAUDE.md's
hygiene rule, whose stated acceptance test is a measurement (Pre-decided 25(iv)/28). Only you may overturn it.
No motor, no camera, no new process device.
**Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT
flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled in this session, so the review is delivered here — which is the product anyway.

# PRIOR-ART REVIEW — S1 of the Pre-decided 22 stage chain

**slug:** `d1-s1-stage` · **trigger:** cycle-start · **verdict: NOT NOVEL — 5 findings**
**Under review:** `docs/cycle27-plan.md` Pre-decided 22's S1 row (`:386`) + `STATUS.md:93-95`, and the recipe the dispatch names, `tools/recipes/stage_d1_s1.py`.

---

## PART A — THE DIRECTION

### A1 — settled already? **No, and I am deliberately not firing this slug.**
Settled *in favour*: the user imposed the staged build 2026-09-19 17:4x (Pre-decided 22, `docs/cycle27-plan.md:381-388`), the S0-decomposition review found a staged save-per-step chain "has never been tried and abandoned" (`archive/peer/2026-09-19-priorart-s0-decomp.md:235`), and the outcome review's binding condition points the same way (`archive/peer/2026-09-19-outcome-review-20260919.md:153`, disposed `:171`). Nothing blocks the direction.

### A2 — refuted already? **No.** The *save route* was flagged unmeasured, not refuted.
Run 10's save died (`tools/bench/build_d1_routeb_v7_run10.log:367` — `gui_save` mtime never moved), generalised by priorart-s0-decomp finding B1 ("NO STEP MAY SAVE A BROKEN VI", seven logged `gui_save` failure sites). **The new stage addresses that cause instead of repeating it**: `stage_d1_s1.py:51-52` bans `allow_broken=True`, so `tools/gscript.py:2066-2067`'s divert is unreachable by construction. No slug.

### A3 — **CONTRADICTED.** The plan forbids the one mechanism the stage rests on, and has not been amended.

Both sides are inside the file under review:

> `docs/cycle27-plan.md` Pre-decided 16(b): *"**NO PRELOADED BUILD RUN** … the working copy can CROSS-LINK to the in-memory original's subVIs and is then written by `g.save(TARGET)`. **Preload stays confined to read-only ExecState diagnostics, in a step that never saves.**"* — restated verbatim at Pre-decided 20.

against

> `tools/recipes/stage_d1_s1.py:262-278` (phase A) and `:358-412` (phase C): `g.save(...)` is called **inside** `with Preload(...)`, which holds the ORIGINAL resident (`:222`).

Pre-decided 22's S1 row authorises the preload "for every **ExecState read**" (`:383`) — not for a save — so the stage table does not lift 16(b) either. The recipe argues its own licence at `:13-21` (16(b)'s cross-link hazard was "NEVER MEASURED"; phases A/B are that measurement). **That argument may well be right; it is simply not the recipe's to make** — Pre-decided 12: `## Pre-decided` lines are edited by judgement sessions, and a material session that believes one is stale reports it and stops.

Second half, undisposed: 16(b) also says *"a preload can MASK a genuine break … so a preloaded 1 is necessary, never sufficient."* Gate D2 (`:437`) and the S1 row's pass criterion (`:386`) are both exactly that preloaded 1.

### A4 — **UNREAD EVIDENCE.** The fixture is four nodes; S1 deletes two, and the decision saying so is cited nowhere.

`docs/fixture-recording.md:15-20` lists **four** nodes inserted 2026-09-01 — `#22700` IMAQ Write TIFF File 2, `#22703` Format Into String, `#23175` Strip Path, `#23020` Build Path — all inside the frame loop (`:12-13`). `docs/d1-build-plan.md:951-958` measured them as "the **whole** difference" from the true original. `TIFF_DELETE` removes two. Leaving the others is decided and defended:

> `docs/d1-build-plan.md:968-972` — *"`#22703` and `#23020`'s other feeder `#23175` … are **NOT** named for deletion here, and that is deliberate, not an oversight … they become dead-but-legal … **Reported in the run, left standing.**"*

Neither `docs/cycle27-plan.md:386` ("fixture TIFF writer … deleted") nor `stage_d1_s1.py:95-96` ("two FIXTURE nodes … are removed and nothing else changes, so the original's computation is untouched") cites §11h or says two of our own insertions survive into the D1 deliverable. Read alone, that docstring asserts the fixture is gone. It is not.

---

## PART B — THE ARTIFACT

### B1 — **ALREADY BUILT.** The S1 stage script exists in full.
`tools/recipes/stage_d1_s1.py` is a complete 489-line, four-phase, 17-gate script with its own prediction contract (`:67-97`). Its prior-art dispatch is already open — `tools/bench/priorart_d1_s1_stage.log:1` (`--slug d1-s1-stage --recipe tools/recipes/stage_d1_s1.py`, no `BGRUN END`). But `STATUS.md:94-95` still reads *"it is to be re-cut as a STAGE script"*, which a cold session will obey. **Nothing is to be re-cut.** The artefact itself does not exist: no `D1_s1_copy.vi` in `claudeDev` (only six `SCRATCH_routeb_*_crash_*.vi`).
*Not re-fired:* `archive/peer/2026-09-19-priorart-s0-closeref.md:579-584` ("lift, don't rewrite") is **satisfied** — `stage_d1_s1.py:30-33` lifts v7's bodies explicitly.

### B2 — already failed? **No** — see A2.

### B3 — **HELPER EXISTS**, and the hand-rolled version will read the wrong number.
Built helper: `tools/bench/diag_d1_execstate_preload.py` — one condition per **child process**, each with its own `lv_restart` (`:96-97`, driven `:202-203`), because "a `Find the VI named …` modal makes GetVIReference block with no dialog visible to the caller … the PROCESS-level deadline is the guarantee" (`:26-28`). Pre-decided 14a adopted the same rule: *"restart LabVIEW between conditions."*

`stage_d1_s1.py` phase B restarts once (`:299`) then takes four readings in that one instance: `:308`, `:309`, `:313-314`.

14a's own mechanism defeats it: *"A cold read therefore measures **subVI linkage**"*. `ARM` and `CTL` are byte copies calling the **same subVIs under the same qualified names** — reading `ARM` at `:308` loads that hierarchy, so `ctl_cold` at `:309` is a preloaded reading wearing a cold label. `g.exec_state` closes its `vi_ref` (`tools/gscript.py:1978`), which unloads nothing: `archive/peer/2026-09-17-d1-s1-stale-in-memory-copy.md:47` records NI's position that `Open VI Reference` returns/links already-resident VIs and that **closing is asynchronous**; `archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md:109` says reuse of one path requires waiting "until the VI is observably absent".

**The consequence is a false positive, not a null.** Gate B (`:318-321`) expects `(0,1)` for both and calls any difference *"the CROSS-LINKING FINDING Pre-decided 16(b) asked for"*. Expect arm `[0,1]` vs control `[1,1]` → gate B FAILs, the chain stops before phase C, and the log reports a cross-link that never happened — manufactured by the instrument rather than detected by it.

### B4 — **ALREADY MEASURED.** Phase C minus the save ran and passed on 2026-09-17.
`tools/bench/build_d1_v0_run6.log:19-26`:
> `:19` BEFORE `{'SubVI': 98, 'Function': 181, 'Node': 626, 'Wire': 1902}`, 28 bare named sinks, ExecState 0 · `:20-21` `#22700`/`#23020` GONE · `:22` newly bare `[]` · **`:23` ExecState unchanged `0 -> 0`** · `:24` AFTER `{97, 180, 624, 1899}` · `:25-26` `#23175`/`#22703` LEFT STANDING

Those are exactly the recipe's pinned `BEFORE` (`:132-133`), `AFTER_S1T` (`:134`) and gates C3/C4/C6/C7; summarised "✅ MEASURED … 4/4" at `docs/d1-build-plan.md:594`. So **only C9 (the save) and phase D are unmeasured** — the same conclusion as `archive/peer/2026-09-19-priorart-s0-closeref.md:584`. Two things to write down before the run, not after: C3/C4/C6/C7 are *replication* (a FAIL means something changed since 2026-09-17, not a discovery); and `:23` measured post-deletion **ExecState 0** cold while the S1 row's criterion is **1 preloaded** — say which number is the criterion.

---

```
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
```

**Cheapest release per finding**

| finding | release |
|---|---|
| A3 | judgement amends Pre-decided 16(b) to cover a save under preload whose artefact is re-read cold **and** preloaded in a fresh instance; recipe header cites it (`FIXED:`) |
| A4 | cite `docs/d1-build-plan.md:968-972` in the recipe docstring and the S1 row; state that `#22703`/`#23175` survive (`FIXED:`) |
| B1 | correct `STATUS.md:94-95` — the stage script exists, do not re-cut it (`FIXED:`) |
| B3 | phase B reuses `diag_d1_execstate_preload.py`'s child-per-condition, restart-per-condition shape (`FIXED:`) |
| B4 | label C3/C4/C6/C7 as replication of `build_d1_v0_run6.log:19-26`; name the pass-criterion reading (`FIXED:`) |

No new op, tool or device is implied (user's standing order, 2026-09-18 08:53). I took no lock, ran nothing, opened no `.vi`, and touched no motor or camera.

## Sources

(extract from answer)

## What was done with it

All five findings were ACCEPTED by the cycle-46 judgement session and applied by the cycle-46 material session
(act 3). One of them needed a code change (B3) and it is made; the other four are citations that were owed.

FIXED: contradicted - docs/cycle27-plan.md:595 - Pre-decided 29 narrows 16(b) from the callee: `gscript.py:2070` is reachable only at ExecState != 0, so a stage artefact can only be saved under preload; `allow_broken=True` is banned and masking is answered by a fresh-instance cold+preloaded re-read.
FIXED: unread-evidence - docs/cycle27-plan.md:623 - 29(f) records why S1 deletes two of the four fixture nodes and cites docs/fixture-recording.md:15-20; the recipe header now carries the same citation.
FIXED: already-built - STATUS.md:93 - STATUS no longer orders the stage script re-cut; it records that tools/recipes/stage_d1_s1.py exists with its md5 and prior-art verdict.
FIXED: helper-exists - tools/recipes/stage_d1_s1.py:353 - phase B now takes one condition per child process on the diag_d1_execstate_preload.py pattern, so no instance ever holds two copies of the main VI.
FIXED: already-measured - tools/recipes/stage_d1_s1.py:56 - the header records that C3-C7 replicate build_d1_v0_run6.log:19-26 deliberately, because that run saved nothing, and that its cold 0 is the 14a linkage reading.

Cycle 46, act 6 — a JUDGEMENT-ORDERED change to the same recipe, recorded here because the gate is on its bytes.
`docs/cycle27-plan.md` Pre-decided 29(g) re-specified the acceptance reference ON MEASUREMENT: `tools/bench/s1_subvi_paths.log` (15/0) found the PRISTINE BYTE COPY to be the defective side (22 SubVI calls re-bound into `claudeDev\background VIs_COPY\`, 8 lost, 7 empty) while the COM-saved copy matched the ORIGINAL on all 98 rows, name and path — so gate B had been comparing the artefact against the broken reference.

FIXED: helper-exists - tools/recipes/stage_d1_s1.py:754 - gate B's acceptance reference is re-specified to the ORIGINAL's SubVI table on measurement (29(g)); phase D gains gate D5, which compares the saved S1 artefact against the ORIGINAL cold, one condition per child process.
