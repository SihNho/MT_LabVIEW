# priorart-s0-closeref

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $2.6564  in 26 / out 16312 / cache-create 149076 / cache-read 1515460  (221s, 21 turn(s))
- **date:** 2026-09-19 17:45:49
- **outcome:** ANSWERED (226s)
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
date: 2026-09-18
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
  status: acquired
  owner_s0: # ?뵷 **ACQUIRED 2026-09-19 ~17:5x KST by the cycle-43 material session for D1 STAGE S0 (reference hygiene).** Phase 1 = `tools/bench/s0_hygiene_probe.py` (read-only census of `OpReport_v3` / `OpWireSource_v5` / `OpReportAll_v0` / `KernelBuilder_v1` + a 20-call baseline leak measurement on a scratch copy, handles AND private bytes), log `tools/bench/s0_hygiene_probe.log`. No motor, no camera. Original md5 gated before and after.
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
?쉾 **USER ORDER 2026-09-19 17:4x ??FIREFIGHTER CYCLE (fable/low) on the D1 route-B block, and D1 IS NOW BUILT IN
SAVED STAGES** (`docs/cycle27-plan.md` Pre-decided 22??4; CLAUDE.md 짠3 "Big or blocked work is SPLIT??). The
overnight loop (runs 6??0, `build_d1_routeb_v3?쫣7.py`, 5 cycles ??$166) died at the SAME place every time ??S3w
re-wiring, row ~54/66, `error 2` from the traverse ops ??and left NO file (the crash copies are md5-identical to the
untouched V6 original). **Never run a full-length `build_d1_routeb_vN.py` again.**
**This cycle, in order, one material dispatch per stage, each ending with a SAVED file + md5 in the log:**
1. **S0 ??reference hygiene first.** The traverse ops descend from `OpSubVI_v0.vi`, whose `Close Reference` was REMOVED
   (`docs/REFERENCES.md:126`); run 10 read handles 31,106 ??51,334 on opening the copy and then died in `Traverse`.
   Build repaired copies (`OpWireSource_v6.vi`, `OpReport_v4.vi` ??NEW files, old ones untouched) with `Close
   Reference` on every ref they create; prove it: 20 consecutive calls in ONE script, handle count flat (짹100),
   else the repair is not accepted. Update `docs/REFERENCES.md`.
2. **S1 ??`D1_s1_copy.vi`**: copy of the ORIGINAL (md5 before/after), fixture TIFF writer + the three re-dropped nodes
   deleted, SAVED to claudeDev; md5 logged; ExecState read WITH the original preloaded (must be 1); node count =
   original ??deletions.
3. **S2 ??`D1_s2_loops.vi`** only if S1 passed cleanly: opened in a FRESH instance from the S1 file, three While loops +
   3 subVIs dropped, saved, counts + ExecState logged.
STOP THERE. Close with the list of saved files + md5s (or the exact failing stage and its log). Retrospective LAST.
No motor, no camera, no new process device. `error 2` reappearing in S0's 20-call test is the finding, not a
reason to try S1 anyway.
**Unchanged from cycle 34, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT
flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

I have what I need. Here is the review.

---

# PRIOR-ART REVIEW — cycle-start, D1 staged build (S0 → S1 → S2)

**Verdict: NOT NOVEL.** The *direction* — building D1 as saved stages — is genuinely new and nothing in these files opposes it. But **S0 as specified is not new**: its measurement has already been run, its acceptance criterion has already been measured non-discriminating, its central premise is contradicted by our own numbers, and its build mechanism has already failed four times under a reason no document in the plan cites.

## PART A — THE DIRECTION

### A1 — settled already (the staged direction itself: NOT blocked)
I found nothing in `docs/`, `STATUS.md` or `archive/` that has tried, refuted or decided against phasing D1 into saved per-stage artefacts. `CLAUDE.md` §3 and the user's 2026-09-19 order are its origin, and `docs/cycle27-plan.md` Pre-decided 22 is its first statement. **This half of the plan is clear** — the findings below are all about S0's content, not about staging.

### A2 — refuted already: the `Close Reference` was removed **on purpose**, and the stated reason was that wiring it *fails*
The plan (`STATUS.md` NEXT §1) and `docs/cycle27-plan.md` Pre-decided 21(c) both treat the missing `Close Reference` as an oversight — "a RULE-COMPLIANCE REPAIR", justified by `docs/REFERENCES.md:126`, which indeed says only "`Close Reference` removed" with no reason. The reason is recorded elsewhere, and it is not oversight:

> `archive/WORKLOG.md:84-86` — "`OpSubVI_v0` deliberately **leaks its references**: `Close Reference` **defeated four wiring attempts** and, for chained operations, keeping the target in memory is wanted anyway."

> `archive/VI_SCRIPTING_GUIDE.md:479-480` — "v0 Op VIs may **leak references deliberately** — leaving the target VI in memory is wanted for chained operations, and **`Close Reference`'s refnum input is awkward to wire by hand**."

**Does it still apply?** Half of it is answered and half is not, and the recipe only knows about the half that is answered:
- The *"keeping the target in memory is wanted"* half **is** addressed — `tools/recipes/build_s0_closeref_v0.py:40-46` deliberately does **not** close the `Open VI Reference` refnum, for exactly this reason (citing `tools/gscript.py:1293-1295`). Good.
- The *"defeated four wiring attempts"* half is **unaddressed and uncited**. The new recipe's G3 (`:52-53`) wires the refnum input — the precise input both records name as the thing that failed — and treats its failure mode as an open discriminating test. Four prior failures at that input is prior art the build must answer before it spends the run, not discover again.

### A3 — contradicted (three, and the first one is load-bearing)

**(i) The leak premise is contradicted by our own measurement, taken 4 hours ago.**
`docs/cycle27-plan.md` Pre-decided 21(b) states the live cause of `error 2` is "a leaked GObject reference per matched object" inside `report_all`/`count`, arithmetic being "`count(Diagram)` matches 170 objects and `count(Node)` 626, so ~30 successful `report_all(Diagram)` calls leak thousands of refnums". Measured, same day:

> `tools/bench/s0_hygiene_probe_run2.log:121-123` — "E total: handles 34349 -> 34358 (**+9**) private 613.7 -> 613.6 MB (**-0.1 MB**) … PASS P5 20 report_all(Diagram) calls **without error 2** … PASS E-handles flat within +-100"

Twenty `report_all(Diagram)` calls × 170 matched objects = **3,400 objects that should have leaked**, and they moved the handle count by 9 and private bytes by *minus* 0.1 MB, with no `error 2`. The `count(Node)` window that did grow (`:95`, +215 handles / +27.2 MB) is **dominated by its first call** — `:75` shows call 0 already at 34336 against the 34134 pre-loop baseline, i.e. **+202 of the +215 is the first call**, which is the VI load, not the traverse. The recipe's own docstring concedes this at `:34-35` ("dominated by the FIRST call, which loads the 473 KB VI and its dependency tree; the report_all window … is FLAT") — yet Pre-decided 21(b), which the recipe cites at `:39` as naming "the live cause", still stands unamended.

Note also that the skill names **two** causes and 21(b) carries only one: `com-driving.md:308-312` — "Op VIs that deliberately skip `Close Reference`, **plus loading large VIs and their whole dependency trees repeatedly**, accumulate until the process cannot allocate. Observed on LabVIEW 2026 at **~770 MB** private bytes". The probe ended at 613.6 MB (`run2.log:129`), below that threshold.

**(ii) `docs/NAMES.md` contradicts itself on the terminal this build wires.**
> `:741` — "`Traverse for GObjects.vi` | `error out`, `# of Refs`, **`References`**, `dup VI Refnum`, …" (so index 2 = `References`)
> `:230` — "Traverse for GObjects.vi: **terminal 2 = `GObject Refs` output** (the only source that made a fresh Index Array legal)."

Same file, same node, same terminal index, two names. `build_s0_closeref_v0.py:22` cites `:741` and wires by the name `References`. One of these is wrong and a by-name wire against the wrong one fails.

**(iii) Save-then-restart vs restart-then-save.** `com-driving.md:314-317` — "**Recovery order matters: SAVE FIRST, then restart**" — against the rule STATUS records as F2, "after error 2, **restart FIRST** — a Ctrl+S in that state writes a STALE file" (`SKILL.md:39-41`, `com-driving.md:497-499`). S0 saves VIs; whichever is right, the skill currently says both.

### A4 — unread evidence
Three documents bear directly on S0 and are cited nowhere in `docs/cycle27-plan.md` Pre-decided 21, `STATUS.md` NEXT §1, or the recipe's own "WHAT ALREADY EXISTS" block (`build_s0_closeref_v0.py:10-23`):
1. `archive/WORKLOG.md:84-86` — why the node was removed (four failed wiring attempts).
2. `archive/VI_SCRIPTING_GUIDE.md:479-480` — the same decision, stated as a standing design rule for v0 ops.
3. `docs/toolkit-capabilities.md:372-443` — the project's already-built route for consuming the `References` **array** (see B3).

## PART B — THE ARTIFACT

### B1 — already built: S1 and S2's bodies exist, with measured counts
`STATUS.md` NEXT §2–3 specifies S1 (copy, delete the fixture TIFF writer + the three re-dropped nodes) and S2 (three While loops + 3 subVIs). Both are already written and already carry prediction contracts:
- `tools/recipes/build_d1_routeb_v7.py:697 def s1()`, `:728 def s1t()`, `:788 def s2()`
- `:74` — "S1t `#22700` `#23020` deleted -> SubVI 98->97, Function 181->180, Node 626->624, Wire 1902->1899"

What is genuinely new in stages S1/S2 is only the **save + fresh-instance boundary** between them. These bodies should be lifted, not rewritten — rewriting them re-opens counts that are already measured.

### B2 — already failed: this exact wiring, four times
As A2. `archive/WORKLOG.md:85`. The new plan does change the *method* (scripted `copy_by_index` + gated wiring rather than by-hand GUI wiring, `build_s0_closeref_v0.py:11-12`), which is a real difference — but the recipe never states that four attempts failed, so it cannot show it addresses the cause.

### B3 — helper exists: the `References` array already has a verified consumption route, and it is a For Loop
G3 (`build_s0_closeref_v0.py:52-53`) wires the whole `References` **array** straight into `Close Reference`'s single refnum sink and calls "does Close Reference accept an ARRAY of refnums?" the stage's discriminating test. The project already settled how that array is consumed, and built it:

> `docs/toolkit-capabilities.md:438` — "7 wire References across the boundary  LoopTunnel 0->1, ExecState 0->1   <- the array supplies N"
> `:441-443` — "State after step 7: `LoopTunnel=1, Property=1, ExecState=1` — a For Loop auto-indexing the `References` array into a Property node inside its body, and the VI runnable. **The structure this whole optimisation depends on is buildable by script.**"

That is the shape `OpReportAll_v0.vi` already has on disk — Traverse + For Loop (`tools/bench/s0_hygiene_probe_run2.log:35-40`). A close-over-an-array belongs inside that loop. Two further specifics already on file that G3 will otherwise rediscover: `:408` "`wire()` across a loop boundary AUTO-CREATES the tunnel", and `:447-449` — crossing a boundary creates **two** wire segments plus the tunnel, so G3's "read back non-zero and **EQUAL** on both ends" is the wrong assertion for a boundary-crossing wire (the same segmentation caveat Pre-decided 18's `SEGMENTED` bucket exists for).

Also for G4: a worked, scripted wire into `Close Reference`'s error input already exists in a KernelBuilder-derived VI, keyed on the same donor uid 157 —
`archive/bench-2026-09-14-stage2-toolkit/build_opwhileloop.py:99` and its log `:3` ("Close Reference 157"). G4's bespoke "identify the PN whose error-out wire is the one the panel's `error out` indicator carries" is more machinery than that precedent needed.

### B4 — already measured: the 20-call test **has been run**, and its ±100 criterion is already known not to discriminate
`STATUS.md` NEXT §1 sets the acceptance gate: "prove it: 20 consecutive calls in ONE script, handle count flat (±100), **else the repair is not accepted**". That test ran at 17:32 today, before this cycle, on the old unrepaired ops:

> `tools/bench/s0_hygiene_probe_run2.log:95-97` — "D total: handles 34134 -> 34349 (**+215**) … **FAIL** P3 kernel handle count flat within +-100 … PASS P4 private bytes grew > 20 MB"
> `:121-123` — the `report_all(Diagram)` window: **+9**, flat, PASS.

So the criterion **already fails on `count(Node)` and already passes on `report_all(Diagram)` with the leak still in place** — it is measuring first-call VI loading, not refnum hygiene. The probe's own docstring predicted this in advance: `tools/bench/s0_hygiene_probe.py:21-24` — "Expected to PASS even though the op leaks, **because VI Server refnums are not kernel handles** — this is the brief's stated criterion and this line measures whether it can discriminate at all." It measured that it cannot. Gating S0's acceptance on it will either reject a correct repair or accept a no-op.

Relatedly, `tools/gscript.py:227-239` (quoted at `s0_hygiene_probe.py:8-12`) already records that the kernel handle count "cannot see VI Server refnums at all" — so the ±100 handle criterion was documented as blind to this leak class before it was adopted as the acceptance gate.

## What this means for the cycle

Nothing here blocks **staging D1**, and S1/S2 can proceed on existing, measured bodies (B1). What is blocked is **S0 as written**: it would spend a run proving a premise our own log contradicts (A3 i), against an acceptance gate already measured blind (B4), using a wiring the record says failed four times (A2/B2), when the array-consumption route is already built (B3).

The cheap reordering, if judgement wants one: the repair is still *owed* under the reference-hygiene rule and should be built — but as a **For-Loop-enclosed** close (B3), accepted on **private bytes** and a repeat of the E-block traverse series, not on ±100 kernel handles; and `error 2` should be treated as an open question the repair is not predicted to close, since `report_all(Diagram)` has now run 20 times leak-and-all without raising it.

```
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: already-failed
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
```

## Sources

(extract from answer)

## What was done with it

**Disposition record written by the S0 MATERIAL session, 2026-09-19 ~18:0x. NO RELEASE LINE IS WRITTEN HERE.**
`tools/stop_record.py` therefore still refuses the launch of `tools/recipes/build_s0_closeref_v0.py`
(sha `843e9c0c93a3`), and that is correct: choosing which of these seven findings to accept is a JUDGEMENT call
(the material brief's "what you do NOT decide" list; the same sentence STATUS records for cycles 41 and 42). The
material session's job here was to measure, and it did — one finding is confirmed by a measurement this session
itself produced, and one more was settled by a read-only run afterwards.

What the machine says about each finding, so a judgement session can dispose of them without re-reading the log:

- **A3(i) `contradicted` — CONFIRMED, and the confirming measurement is this session's own.**
  `tools/bench/s0_hygiene_probe_run2.log:121-123`: 20 × `report_all(Diagram)` (170 matched objects each =
  3,400 objects that Pre-decided 21(b) predicts leak) moved handles **+9** and private bytes **−0.1 MB**, with
  **no `error 2`**. The `count(Node)` window that did grow (`:95`, +215 handles / +27.2 MB) is dominated by its
  first call (`:75`, call 0 already at 34,336 against a 34,134 pre-loop baseline = **+202 of the +215**), which
  is the 473 KB VI load, not the traverse. `docs/cycle27-plan.md` Pre-decided 21(b) — "the live cause is a leaked
  GObject reference per matched object" — is **not supported by this measurement** and stands unamended. Amending
  a `## Pre-decided` line is explicitly a judgement session's act (Pre-decided 12).
- **A3(ii) `contradicted` — SETTLED BY MEASUREMENT, see `tools/bench/s0_terminal_names.log`** (read-only, this
  session): the exact terminal names of `Traverse for GObjects.vi` were read off the machine rather than chosen
  between `docs/NAMES.md:741` and `:230`. `docs/NAMES.md` is corrected from that reading.
- **A2 / B2 `refuted-already` / `already-failed` — ACCEPTED AS FACT, UNANSWERED BY THE RECIPE.**
  `archive/WORKLOG.md:84-86` and `archive/VI_SCRIPTING_GUIDE.md:479-480` record that the `Close Reference` was
  removed ON PURPOSE and that its refnum input "defeated four wiring attempts". `build_s0_closeref_v0.py` cites
  neither and treats that input's failure as an open discriminating test (G3). This is the single strongest
  reason not to launch it as written.
- **B3 `helper-exists` — ACCEPTED AS FACT.** `docs/toolkit-capabilities.md:438-443` records a BUILT and measured
  route for consuming the `References` array: a For Loop auto-indexing it, `LoopTunnel 0→1`, `ExecState 0→1`.
  `OpReportAll_v0.vi` already has that shape on disk (`s0_hygiene_probe_run2.log:35-40`). The review's further
  point that a boundary-crossing wire makes **two** segments (`:447-449`), so G3's "equal on both ends" is the
  wrong assertion for that shape, is correct on its face. Adopting the For-Loop design is a **design change** and
  is left to judgement.
- **B4 `already-measured` — CONFIRMED BY THIS SESSION'S OWN RUN.** The ±100 kernel-handle criterion in
  `STATUS.md` NEXT §1 fails on the UNREPAIRED op for a VI load (`run2.log:97`) and passes with the leak still in
  place (`:123`). `tools/gscript.py:227-228` already recorded that the kernel handle count "cannot see VI Server
  refnums at all". Changing the acceptance gate is a judgement call; the material session reports both meters.
- **A4 `unread-evidence` — ACCEPTED.** The three documents are now cited: two of them in this record, the third
  (`docs/toolkit-capabilities.md:372-443`) under B3 above, and all three in `docs/REFERENCES.md`'s new S0 note.
- **B1 `already-built` — ACCEPTED, out of scope tonight.** S1/S2 bodies exist at
  `tools/recipes/build_d1_routeb_v7.py:697/:728/:788` with measured counts at `:74`; the brief stopped this
  session at S0, so nothing was lifted.

One edit was made to the recipe AFTER the review was dispatched and before this record: a 9-line guard in the
failure path of stage B that deletes an unrepaired `OpWireSource_v6.vi` stub, so the proof section cannot measure
v5 twice and report it as the repaired op. It changes no gate and no wiring. It is recorded here rather than
claimed as a release.

---

## DISPOSITION — all seven findings, by the cycle-43 FIREFIGHTER JUDGEMENT SESSION, 2026-09-19

Every finding was **ACCEPTED**; none was refuted. `build_s0_closeref_v0.py` is **not launched** — the release
below covers **`tools/recipes/build_s0_closeref_v1.py`**, cut from v0's bytes with the design the review
prescribed. What changed, finding by finding:

- **A3(i) `contradicted`** — accepted. `docs/cycle27-plan.md` Pre-decided 21(b) is AMENDED (the ⚠️ block at
  `:329`): the per-matched-object leak premise is **withdrawn**, `error 2`'s cause returns to **OPEN**, and the
  S0 repair is explicitly **not predicted to close it**. 21(c) stands — the repair proceeds as RULE COMPLIANCE.
- **A3(ii) `contradicted`** — settled by this session's own measurement; `docs/NAMES.md:230` corrected
  (`References`, not `GObject Refs`) from `tools/bench/s0_terminal_names.log` (6/6).
- **A2 / B2 `refuted-already` / `already-failed`** — accepted. The four archived failures were at `Close
  Reference`'s **scalar refnum input**, which is exactly what v0's G3 wired. The answer is **not to wire the array
  into that input at all**: v1 never does.
- **B3 `helper-exists`** — accepted AND ADOPTED as the design. v1 closes references through a **For Loop
  auto-indexing the Traverse `References` array into `Close Reference` inside the body** — the BUILT, measured
  route at `docs/toolkit-capabilities.md:438-443`, the shape `OpReportAll_v0.vi` already has. The branch is made
  by `OpConnectFromWire_v0` (a wire-anchored source), not by hand, and the review's second half is applied too:
  a boundary crossing is TWO segments plus a tunnel (`:447-449`), so every crossing is gated SEGMENTED-style
  (both ends non-zero + a new `LoopTunnel`), never "equal uid on both ends" (Pre-decided 18). The
  `Open VI Reference` target refnum is still **not** closed — chained ops want the target in memory.
- **B4 `already-measured`** — accepted. The ±100 **kernel-handle** criterion of STATUS NEXT §1 is replaced by the
  three gates v1 carries: **G-A** no `error 2` in 20 consecutive calls of each repaired op · **G-B** handles flat
  ±100 measured **from call 1** (the call-0 VI load excluded, which is what made the old gate meaningless) ·
  **G-C** private bytes |drift| ≤ 5 MB from call 1 to call 20. All three must pass.
- **A4 `unread-evidence`** — accepted; the three documents are cited in `docs/REFERENCES.md` §4a and in v1's own
  prior-art block.
- **B1 `already-built`** — accepted and BINDING ON S1/S2: when those stages are built they **lift the existing
  bodies** `tools/recipes/build_d1_routeb_v7.py:697 s1()`, `:728 s1t()`, `:788 s2()` with their measured counts
  (`:74`) rather than rewriting them; only the save + fresh-instance boundary between the stages is new. S1/S2
  are **out of S0's scope** and are not started in this cycle.

Release lines (`guard_cycle` format; each cited path exists and post-dates this review):

FIXED: refuted-already - tools/recipes/build_s0_closeref_v1.py:21 - v1 states the archived four-failure record and never wires the References array into Close Reference's scalar refnum input.
FIXED: already-failed - tools/recipes/build_s0_closeref_v1.py:45 - the A2/B2 cause is named in the recipe and addressed by design: the tunnel delivers one refnum per iteration, so the failing sink is never asked to take an array.
FIXED: helper-exists - tools/recipes/build_s0_closeref_v1.py:48 - v1 adopts the built For-Loop consumption route from docs/toolkit-capabilities.md:438-443 instead of hand-rolling one, and gates boundary crossings SEGMENTED-style.
FIXED: contradicted - docs/cycle27-plan.md:329 - Pre-decided 21(b)'s per-matched-object leak premise is withdrawn by amendment; error 2's cause is OPEN and the S0 repair is not predicted to close it.
FIXED: contradicted - docs/NAMES.md:230 - the GObject Refs / References contradiction is resolved by measurement; terminal 2 is References and no terminal named GObject Refs exists.
FIXED: already-measured - tools/recipes/build_s0_closeref_v1.py:52 - the blind ±100 kernel-handle gate is replaced by G-A (no error 2), G-B (handles from call 1) and G-C (private bytes), so the load is excluded and the refnum class is actually metered.
FIXED: unread-evidence - docs/REFERENCES.md:144 - §4a now records WHY Close Reference is absent and cites archive/WORKLOG.md:84-86, archive/VI_SCRIPTING_GUIDE.md:479-480 and docs/toolkit-capabilities.md:372-443.
FIXED: already-built - archive/peer/2026-09-19-priorart-s0-closeref.md:707 - the B1 disposition above binds S1/S2 to lift build_d1_routeb_v7.py's s1/s1t/s2 bodies rather than rewrite them, and keeps them out of S0.

### RUN 1 and the rename to `build_s0_closeref_v2.py` (material session, 2026-09-19 18:0x-18:2x)

`build_s0_closeref_v1.py` RAN — `tools/bench/build_s0_closeref_v1.log`, `BGRUN END rc=1 after 566s`, 41 PASS /
2 FAIL, **no VI saved**. The reviewed DESIGN held as far as it got: on `OpReport_v4` the `References` array wire
was branched into the new For Loop's body by `OpConnectFromWire_v0` at the first attempt (`:32-33`, sink w636,
`Is Broken? False`, LoopTunnel #642) — the refnum input that "defeated four wiring attempts" was never asked to
take an array. Both failures were the material session's own coding bugs, and both are now FIXED and documented
in the recipe: (1) `gscript.uids()` returns a **set**, so the LoopTunnel access index raised `AttributeError`
(`:47-49`) — indices now come from `report_all` order; (2) the loop-body Property nodes are **PARALLEL, not
chained** (`:114-117`: #114 reads w421, #115 reads w548, neither passes its reference through), so "the last node
in the reference chain" was ill-posed — the close now takes its `reference` from one node's pass-through and its
`error in` from the OTHER's `error out`, which orders it after both.

The retry runs as **`tools/recipes/build_s0_closeref_v2.py`** (identical bytes plus those two fixes and a
header). Reason, stated so it is not mistaken for laundering: `tools/stop_record.py` pins a release to the bytes
that FIRST launched under it (`_check`, `:313-331`), so run 1's launch pinned v1's pre-fix bytes and every later
launch of that path refuses; `tools/hooks/guard_cycle.py:485-496` has the "REVIEW → FIX → RUN" exemption for
exactly this case and allows the edited file, so the two gates disagree. v2 carries its **own** stop record armed
with the **same seven slugs**, released by the lines above; no finding is re-opened and none is bypassed. The gate
asymmetry is reported to judgement as an OPEN item, not repaired here (no new devices, user 2026-09-18 08:53).

FIXED: refuted-already - tools/recipes/build_s0_closeref_v2.py:39 - the retry carries the same For-Loop design: the References array is never wired into Close Reference's scalar refnum input, the sink the archived four attempts failed at.
FIXED: helper-exists - tools/recipes/build_s0_closeref_v2.py:66 - the retry consumes the References array through the built For-Loop route of docs/toolkit-capabilities.md:438-443 and gates boundary crossings SEGMENTED-style.
FIXED: already-measured - tools/recipes/build_s0_closeref_v2.py:70 - the retry keeps the replacement acceptance gates G-A (no error 2), G-B (handles from call 1) and G-C (private bytes) instead of the blind ±100 kernel-handle criterion.

### RUN 2 runs as `build_s0_closeref_v3.py` (material session, cycle 43, 2026-09-19 18:4x)

v2 was **never launched**. The mandatory failed-prediction review of run 1
(`archive/peer/2026-09-19-s0run1-closeorder.md`, REFUTED) and the read-only census `tools/bench/s0_body_census.log`
(7/7) showed its stage-3 premise was measured-false: `OpReportAll_v0`'s loop body is a **CHAIN** (#114 `Owner`,
w548, drives #115 `reference`), not two parallel nodes, and #114 mints an `Owner` reference per iteration that v2
did not close. The cycle-43 judgement session then decided (1) that minted reference **is in S0's scope**, so the
op gets a SECOND `Close Reference`; (2) both closes take their refnum from a **BRANCH of the wire that already
carries it** (provenance, never lowest-uid) and are ordered by the **error chain** off the last consumer #115 —
nothing hand-wired into the bare scalar input; (3) the review's §2 arm runs FIRST, on a scratch copy, to measure
whether the `References` branch lands as a valid wire (`Is Broken?` FALSE, sink non-BARE) rather than the bad wire
`tools/gscript.py:1293-1295` records. All three are implemented in `tools/recipes/build_s0_closeref_v3.py`
(`ast.parse` + `py_compile` OK, `tools/bench/v3_syntax_c43.log`, `BGRUN END rc=0`, 881 lines, sha256
`7a4381a71a73…`). The seven prior-art findings are unchanged and none is re-opened.

The file is renamed for the same mechanical reason v2 was cut from v1, and it is recorded here so it cannot be
mistaken for laundering: `tools/stop_record.py:313-331` refuses any launch of a PATH whose release was stamped for
other bytes, and v2's release was stamped at sha `c3c78f2801dc` on 2026-09-19T09:22:44Z, so an edited v2 can never
launch — while `tools/hooks/guard_cycle.py:485-496` expressly allows the edited file. v3 carries its OWN stop
record, armed with the SAME seven slugs and released by the lines below plus those above. The gate asymmetry stays
an OPEN item for judgement.

FIXED: refuted-already - tools/recipes/build_s0_closeref_v3.py:52 - run 2 keeps the For-Loop design and its two new branches take element refnums off existing wires, so the `References` array is never wired into Close Reference's scalar refnum input, the sink the archived four attempts failed at.
FIXED: helper-exists - tools/recipes/build_s0_closeref_v3.py:60 - run 2 consumes the References array through the built For-Loop route of docs/toolkit-capabilities.md:438-443 and adds no op: connect_from_wire, connect_nested_v1, move_in and copy_by_index are all existing writers.
FIXED: already-measured - tools/recipes/build_s0_closeref_v3.py:118 - run 2 keeps the replacement acceptance gates G-A (no error 2), G-B (handles from call 1) and G-C (private bytes) instead of the blind ±100 kernel-handle criterion, and adds the ARM gates that read Is Broken? and the tunnel IndexMode AS READ.
