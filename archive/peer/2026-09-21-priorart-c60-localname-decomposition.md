# priorart-c60-localname-decomposition

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $8.6086  in 32 / out 36080 / cache-create 567616 / cache-read 4060609  (437s, 25 turn(s))
- **date:** 2026-09-21 08:19:47
- **outcome:** ANSWERED (439s)
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

29. **THE ONLY SAVE ROUTE FOR A STAGE ARTEFACT IS `g.save()` UNDER PRELOAD ??16(b)'s "a step that never saves" is
    NARROWED, not discarded ??and STAGE BOUNDARIES MUST FALL AT LEGAL STATES.** Judgement, cycle 46, 2026-09-19,
    read from the CALLEE (Pre-decided 21(f)), never from a call site.
    - (a) **Measured.** `tools/gscript.py:2056-2071` holds the only COM writer: it refuses a path outside
      `claudeDev`/`SAVE_ALLOWLIST` (`:2062-2064`), then reads `exec_state(target)` (`:2065`, which opens its OWN
      reference by path ??`:1977-1979`); at 0 it diverts to `gui_save` when `allow_broken=True` (`:2066-2067`) and
      otherwise raises (`:2068`). `SaveInstrument` (`:2070`) is reachable ONLY at `ExecState != 0`.
    - (b) By Pre-decided 14a a copy of the original reads `ExecState` **0 COLD / 1 PRELOADED**. So in a
      non-preloaded instance **no copy of the main VI can ever reach `SaveInstrument`**, and the only other writer,
      `gui_save`, has failed at eight logged sites including run 10
      (`tools/bench/build_d1_routeb_v7_run10.log:367`). MEASURED, cycle 46: **no run in this project has ever saved
      a modified copy of the main VI** ??every `g.save(TARGET)` sits in an S5/S6 no route-B run reached
      (`tools/bench/build_d1_v0_run4.log:256`; `?쫞outeb_v5_run8.log:438`; `?쫣6_run9.log:492`).
    - (c) **Therefore Pre-decided 22's staged build is unexecutable under 16(b) as written.** 16(b) named two
      hazards and only one of them was ever measured. MASKING is answered, not denied: every stage artefact is
      re-read in a FRESH instance **cold AND preloaded, one condition per child process**
      (`tools/bench/diag_d1_execstate_preload.py:26-28`, `:96-97` ??four readings taken in one instance contaminate
      each other, because reading one copy loads the very hierarchy the next read would have had to resolve), and a
      preloaded 1 stays necessary-never-sufficient. CROSS-LINKING was never measured;
      `tools/recipes/stage_d1_s1.py` phases A/B measure it directly ??a no-edit COM save under preload, then the
      saved file's (cold, preloaded) pair against a pristine byte copy's. **Until that arm returns, preload-then-save
      is permitted ONLY for stage artefacts under `claudeDev`.**
    - (d) **`allow_broken=True` is BANNED in every stage script** ??it is the one flag that can reach `gui_save`.
    - (e) **Stage boundaries fall at LEGAL states.** A stage that deletes a node whose outputs are consumed leaves
      bare required inputs, i.e. an unsaveable VI, so **delete-and-re-drop is ONE stage**. S1 is therefore the
      fixture TIFF writer ONLY (`#22700`, `#23020` ??v7 `s1t()` `:728-751`, contract `:74-75`); v7 `s1d()`'s three
      re-dropped subVIs (`#5058 GPU_kernel_v1.vi`, `#48 ASI_adjust focus-subvi.vi`, `#376 save trace.vi`,
      `:754-784`) move into the stage that re-drops them. This reorders build operations only ??rule 1a untouched.
    - (f) **S1 deletes TWO of the four 2026-09-01 fixture nodes, deliberately** (prior-art A4,
      `archive/peer/2026-09-19-priorart-d1-s1-stage.md`). `#22703` / `#23175` (`docs/fixture-recording.md:15-20`)
      STAY, because every pinned count downstream ??SubVI 98??7, Function 181??80, Node 626??24, Wire 1902??899 ??
      is the measured contract of the two-node deletion, and widening it would invalidate the chain with no
      measurement behind it. Removing the other two is a later stage with its own contract, recorded as an OPEN
      item; it is not an oversight.
    - (g) ?뵶 **THE ACCEPTANCE REFERENCE FOR A STAGE ARTEFACT IS THE ORIGINAL'S SUBVI TABLE, NEVER A BYTE COPY ??
      gate B as first written compared against the defective side.** MEASURED, cycle 46
      (`tools/bench/s1_subvi_paths.log`, 15/0, three conditions each in its own child process and its own LabVIEW
      instance; artefact `tools/bench/s1_subvi_paths.json`): the COM-SAVED copy matches the ORIGINAL on **all 98
      SubVI calls, name and path, byte for byte**, with **zero** rows into `claudeDev\background VIs_COPY\`, while
      the PRISTINE BYTE COPY re-binds **22** calls into `claudeDev\background VIs_COPY\`, loses **8** outright and
      reads 7 rows as empty (uid 0, name `''`, path `''`) ??tables at `:369-395`. That is why a byte copy reads
      `ExecState 0` COLD and the saved copy reads 1: Pre-decided 14a's "a cold read measures subVI linkage" stands
      and now has its specific cause. **So `shutil.copy2(ORIGINAL, claudeDev\??` produces a SILENTLY RE-BOUND VI**,
      and every stage gate compares against the ORIGINAL, never against a copy. The byte copy stays as a logged
      control only. `claudeDev\background VIs_COPY\` holds 94 `.vi` files; the 17 names it shares with the
      original's own subVI locations are **md5-identical today** (`:397-450`), so nothing has computed differently
      yet ??it is an unmanaged duplicate hierarchy sitting on the build path, recorded as an OPEN item.
    - (h) **Rule 1a is de-risked on the linkage channel but NOT closed.** The mandatory failed-prediction review
      (`archive/peer/2026-09-19-s1-saved-copy-cold-execstate.md`, ANSWERED, claude/hypothesis opus max, $4.2400,
      590 s) named three ways a save could change computation: subVI re-binding ??now **measured excluded** by (g);
      typedef re-instantiation persisted on save; polymorphic/Express regeneration. The structural census is delta 0
      on all nine classes (`tools/bench/s1_savedcopy_census.log:55-64`) and the saved-version bytes are unchanged,
      but CLAUDE.md rule 1a says counts and `ExecState` prove nothing about computation. **The remaining channels are
      closed by the review's T2 ??an OFFLINE RSRC block-level diff of the two files, no LabVIEW and no lock ??which
      is the next cycle's first act.** Until T2 has run, no stage artefact is promoted beyond `claudeDev`.
    - (i) **The static audit's gate S6 is an unsound proxy, but item 17's actual constraint IS met ??judgement,
      cycle 46; do not re-open it.** The audit asserts "one `remove_bad_wires_scripted` outside any loop" by a
      spelling scan, and the mandatory peer (`archive/peer/2026-09-19-staticaudit-falsepos.md` 짠1b) measured that
      `tools/recipes/stage_d1_s1.py:654` sits inside `phase_c`, dispatched from the PHASE-SELECTOR `for` at
      `:788-789` ??so the scan establishes nothing. What item 17 actually bans is a VI-wide reaper called from
      inside the ROW LOOP of a multi-row wiring pass. Phase C has no row loop: it deletes two pinned uids and calls
      the reaper ONCE, which is precisely the shape item 17 EXONERATES (`build_d1_routeb_v5.py:694`, executed by
      run 5 with its rows wired). The recipe complies; the gate's WORDING is what is wrong ??it should read "not
      inside a row loop". Left as a known-weak check rather than rebuilt (user, 2026-09-18 08:53, no more devices).
    - (j) **A self-test that a gate itself mandated consumed the last build-budget slot and cost cycle 46 its
      deliverable.** `tools/logclass.py` counts `selftest_*.log` as a build (its docstring records that as known and
      deliberately unfixed), so the regression check for the stop-record repair took slot 10 of
      `guard_cycle.CYCLE_BUILD_BUDGET = 10` and `stage_d1_s1.py --phases CD` could not launch. Clearing the budget
      means running the retrospective, which permanently marks the session retro-done (OPEN 54(a)) ??so the run
      cannot happen in the same session. **The loop-breaking move is simply that the NEXT session launches it as its
      first act**, with the stop record already ALLOW. Recorded as a finding for the retrospective; NOT repaired,
      and no device built.

## Pre-decided ??ADDED 2026-09-20 (cycle 48, after S1 was DELIVERED)

30. **S1 IS DONE, and S2 IS THE DELETE + LOOPS + RE-DROP AS ONE STAGE, whose FIRST PHASE MEASURES WHETHER THAT
    STAGE CAN END LEGAL.** Judgement, cycle 48, 2026-09-20, from v7's own source and header contract ??not from a
    preference. S1's artefact is on disk: `claudeDev\D1_s1_copy.vi`, md5 `3e3d23cefd3a334001aa9d6156bf1aee`,
    474,202 B, 20/20 gates, `tools/bench/stage_d1_s1_cd.log:115-346`.
    - (a) **Contents and the net contract**, from `tools/recipes/build_d1_routeb_v7.py:76-84`: delete `#5058`,
      `#48`, `#376` (`s1d`, `:754-785`, SubVI 97??4, every wired terminal captured first at `:766`) 쨌 create 3
      While loops on `Diagram #686` (`s2`, `:788-813`, `WhileLoop 3??`, `Diagram 170??73`, `#637` still owning
      `#6810`/`#22082`/`#12589`/`#11639`/`ControlTerminal #642`) 쨌 re-drop the three into the three new loop
      bodies (`s2d`, `:815-848`, SubVI 94??7). ?뵶 **The NET over the stage is SubVI 97 ??97, WhileLoop +3,
      Diagram +3.** Pre-decided 22's row "+3 loops +3 subVIs" describes the `s2d` drops, not a net change; a gate
      asserting SubVI 100 would be wrong. `docs/d1-route-b-plan.md` 짠7's Diagram **174** counts a fourth, pool,
      loop that is not built ??173 is the number for this stage (`build_d1_routeb_v7.py:78-83`).
    - (b) **Why ONE stage.** Pre-decided 29(e): a stage that deletes a node whose outputs are consumed leaves bare
      required inputs, i.e. an unsaveable VI, so delete-and-re-drop is one stage. v7 separates them across three
      calls (`:2742` `s1d` ??`:2744` `s2` ??`:2746` `s2d`) and its uid-reuse note at `:850-855` depends on that
      order ??**the order is preserved INSIDE the stage; it is the stage boundary that moves, not the sequence.**
    - (c) **Input, output, skeleton.** Input is `claudeDev\D1_s1_copy.vi`, gated against md5
      `3e3d23cefd3a334001aa9d6156bf1aee` before any edit; output is `claudeDev\D1_s2_loops.vi`. The script is
      `tools/recipes/stage_d1_s2.py`, copied from `stage_d1_s1.py`'s skeleton ??`main()`/`--phases` `:763-800`,
      `gate()` `:258-265`, `class Preload` `:332-358`, `md5()`/`file_facts()`/`orig_gate()` `:272-375`,
      `fresh()` `:317-330`, `cold_subvi_table()`/`compare_subvi_tables()` `:377-428` ??with ONE substantive
      change: `:623-625`'s `shutil.copy2(ORIGINAL, TARGET)` becomes a copy **from the S1 artefact**. The ORIGINAL
      stays the acceptance reference for everything S1 did not change (29(g)); the S1 artefact is the reference
      only for the two deleted fixture nodes.
    - (d) ?뵶 **PHASE A IS A MEASUREMENT AND EDITS NOTHING ??it is written and run BEFORE phases C/D exist.** This
      is the shape that made S1 work (phases A/B measured the save route; C/D built). Four facts, all read on
      `D1_s1_copy.vi` with the ORIGINAL preloaded read-only (Pre-decided 14a), saved as a DATA artefact
      `tools/bench/s2a_legality.json` + its log:
      - **A1 ??why delete-and-re-drop at all?** The other 21 nodes are relocated with `move_in`; these three are
        deleted and re-dropped. Read what `move_in` does to a SubVI node's owner chain and wires versus
        `drop_subvi`, from our own measured capability files, and say whether `move_in` reaches `Diagram #686`'s
        new loop bodies. **If it does, S2 ends legal with no scaffolding at all** ??that is the cheapest possible
        stage boundary and it must be checked before the expensive one is built.
      - **A2 ??the connector panes.** For `#5058` (`claudeDev\GPU_kernel_v1.vi`), `#48`
        (`<vi.lib>\Madcity\ASI_adjust focus-subvi.vi`) and `#376` (`<vi.lib>\background VIs\save trace.vi`):
        every connector-pane terminal and whether it is **Required / Recommended / Optional**. A freshly dropped
        subVI breaks the VI only on an unwired **Required** input; Recommended and Optional do not.
      - **A3 ??the loops' own legality.** Three new While loops with unwired conditional terminals are a
        compile-time break (Pre-decided 16(a)). Report which ALREADY-BUILT ops reach a While loop's conditional
        terminal and place a Boolean constant on a diagram ??by name, from `docs/toolkit-capabilities.md` and
        `docs/NAMES.md`. **No new op and no new device** (Pre-decided 2); if the existing set cannot do it, that
        is an `OPEN:` for judgement, not a licence to build one.
      - **A4 ??the starting state.** `D1_s1_copy.vi`'s md5 and its `ExecState` COLD and PRELOADED, each in its own
        child process (29(c)). S1 measured COLD **1** and PRELOADED **1** (`stage_d1_s1_cd.log:153`, `:155`) ??
        confirm it has not moved.
    - (e) **BOTH BRANCHES ARE DECIDED HERE, so the material session applies whichever A returns without coming
      back for judgement** (the Pre-decided 28 pattern):
      - **A1 says `move_in` reaches the new loop bodies** ??S2 is `s2` (loops) then `move_in` for the three, no
        delete and no re-drop. Contract: SubVI 97 unchanged throughout, WhileLoop 3??, Diagram 170??73.
      - **A1 says it does not, and A2 finds no unwired Required input on any of the three** ??S2 is
        `s1d` ??`s2` ??`s2d` as in (a), with the (f) scaffold, saving `D1_s2_loops.vi`.
      - **A2 finds an unwired Required input on one of the three** ??that one is LEFT ALONE in S2 ??neither
        deleted nor re-dropped ??and its delete + re-drop + wire become their own later stage, because splitting
        its pair is exactly what 29(e) forbids. S2's contract becomes SubVI 97 ??97?뭟 ??97 for the k it handles.
      - **A3 finds no built route to the conditional terminal** ??S2 stops after phase A and saves the DATA
        artefact; the boundary question comes to judgement. This is the only branch that ends without a VI.
    - (f) **The temporary conditional-terminal constant is `True`, never `False`.** Where a new While loop must be
      left unwired until S3w, its conditional terminal carries a temporary Boolean constant so the VI stays
      saveable, and S3w removes it when the real stop wiring lands. **`True`** because if the scaffold ever
      survives into a run, a loop that executes once is a visible, harmless failure, while `False` on a
      "Stop if True" terminal is an instrument that hangs. This is scaffolding on loops the original does not
      have ??rule 1a is untouched, no per-bead maths and no original wire is involved.
    - (g) **Legality is not optional and it is not `allow_broken`.** `tools/gscript.py:2065-2071` reaches
      `SaveInstrument` only at `ExecState != 0`, `allow_broken=True` is banned (29(d)), and `gui_save` has failed
      at eight logged sites. A stage that cannot end legal saves a DATA file (Pre-decided 25 finding B1) and says
      so in its log ??it does not save a broken VI and it does not pretend it saved one.

31. **S2 IS BRANCH 1 ??LOOPS, THEN `move_in`. Phase A shrinks from a measurement to a RECORDING, because the
    prior-art review found every one of its four questions already answered in our own files.** Judgement, cycle 49,
    2026-09-20, disposing `archive/peer/2026-09-20-priorart-d1-s2-stage.md` (ANSWERED, opus/high, eight slugs, no
    `novel`). All eight findings were accepted; none was refuted. 30 stands as written ??this fixes the recipe that
    implements it and fixes one factual error inside 30(d).
    - (a) ?뵶 **`#5058` IS THE CPU KERNEL, NOT THE GPU KERNEL. 30(d)'s parenthesis `(claudeDev\GPU_kernel_v1.vi)`
      IS WRONG and is corrected here** (`refuted-already`, citing `docs/d1-route-b-plan.md:135` and
      `docs/d1-build-plan.md:287`): in the ORIGINAL ??and therefore in `D1_s1_copy.vi`, which changed only the TIFF
      fixture ??uid `#5058` is the **CPU** kernel `Track N beads four-fold over-kernel-v3.vi`. Relocating it is
      correct and is what S2 must do; **logging it as `GPU_kernel_v1.vi` is not**, and a log that misnames what it
      moved is the `unreported-fact` class. So: the recipe carries the true name, and a gate reads the VI name at
      `#5058` on the artefact and **FAILS the stage** if it is not `Track N beads four-fold over-kernel-v3.vi`.
      **Swapping the CPU kernel for `GPU_kernel_v1.vi` is its own later stage** with its own rule-1a argument; it is
      not smuggled inside a loop restructure, and nothing in S2 assumes it has happened.
    - (b) **A1 is SETTLED, not measured** (`settled-already`): `move_in` already lands nodes into loop bodies created
      in the SAME run ??21 such landings, `tools/bench/build_d1_routeb_v7_run10.log:116-173` and `:70-76`,
      `docs/d1-build-plan.md:931` (re-measured 2026-09-20, was `:873`). That is 30(e)'s **branch 1**, and 30(e) says to take it whenever it is available:
      **S2 = create the three While loops, scaffold them, then `move_in` the three nodes. No delete, no re-drop, no
      scaffold subVI.** Phase A RECORDS this with its citation instead of re-measuring it. One thing phase A must
      still read from that same log, because it is the question 30(d) A1 actually asked: **whether `#5058` / `#48` /
      `#376` were among the 21 or were excluded, and if excluded, the reason v7 gave.** An exclusion with a stated
      cause is the only thing that can send S2 back to the delete-and-re-drop shape.
    - (c) **A2 is MOOT under branch 1 and is recorded as such.** Required-ness only bites a freshly dropped subVI;
      branch 1 drops nothing and the three keep their wires. The fail-closed `a2_required_readable=False` reading
      stays *true* (no built op reads the Required/Recommended/Optional flag, and building that reader is forbidden
      by Pre-decided 2) but it is no longer load-bearing, so it must not select a branch. `unread-evidence` also
      names files that already answer it for the input that matters ??`docs/d1-route-b-plan.md:148`, `:154`,
      `:158-159`; `docs/d1-build-plan.md:523-536`; `docs/NAMES.md:564-565` ??which phase A cites rather than probes.
    - (d) ?뵶 **A3's `a3_route_exists = FALSE` PREDICTION WAS WRONG** (`contradicted`): three routes from a Boolean to
      a While loop's conditional terminal are already measured at `ExecState 1`, and the recipe's candidate list
      (`stage_d1_s2.py:573-581`) simply omitted the obvious one ??**`OpExitWhile_v0`, `docs/toolkit-capabilities.md:31`**
      (also `:63`, `:64`, `:66`). **`OpExitWhile_v0` is the scaffold of record for 30(f)**, applied to each NEW
      loop's own conditional terminal. The recipe's `_boolean_sink` (`:831-843`) is DELETED: it chose a sink by a
      regex over terminal *names* among the dropped subVIs, which under branch 1 has no sink to find at all ??that
      is the `already-failed` finding, and it is why "three empty While loops" is measured at `ExecState 0`
      (`docs/toolkit-capabilities.md:67`). The gate is unchanged and absolute: **each of the three new loops has its
      conditional terminal wired to a constant TRUE before the stage saves.**
    - (e) **30(f)'s `True` is a requirement on the VALUE delivered at the conditional terminal, not on the object
      being a literal constant.** Any ALREADY-BUILT route qualifies if it (i) leaves the terminal wired, (ii)
      delivers constant TRUE, and (iii) adds no new unwired Required input of its own. The reason in 30(f) is
      physical ??a scaffold that survives into a run must execute the loop once and exit, never hang ??and a node
      that computes TRUE satisfies it exactly as a `True` constant does. A route that can only deliver **FALSE**
      does NOT satisfy 30(f) and is refused; that is the hang the clause exists to forbid.
    - (f) **A4 drops its two ExecState child processes** (`already-measured`): the pair is already recorded on this
      exact md5 at `tools/bench/stage_d1_s1_cd.log:153` (COLD 1) and `:155` (PRELOADED 1), and the md5 gate on
      `3e3d23cefd3a334001aa9d6156bf1aee` already proves the file has not moved. Phase A keeps the md5 gate and cites
      those two lines; the PRELOADED state is read anyway inside C/D, where the save route needs it (29(d)).
    - (g) **Phase C reuses v7's already-passing step functions rather than re-deriving them** (`already-built`,
      `helper-exists`): the construction steps have passed their gates in the real VI
      (`tools/bench/build_d1_routeb_v7_run10.log:70-76`, `:106`). What is genuinely new ??and what this stage is
      *for* ??is the **stage boundary**: copy from the S1 artefact, gate on its md5, save `D1_s2_loops.vi`.
    - (h) **The net contract is unchanged from 30(a) and is now the contract of branch 1 exactly: SubVI 97 ??97
      (no subVI is created or destroyed at any point in the stage), WhileLoop 3 ??6, Diagram 170 ??173.** Every
      comparison is against the ORIGINAL, never against a copy (29(g)).
    - (i) **If the stage cannot end legal it saves `tools/bench/s2a_legality.json` and says so** (30(g)). It never
      saves a broken VI, never uses `allow_broken=True`, and never invents an op to get past a gate (Pre-decided 2).

32. **THE SCAFFOLD GOES ON AFTER `move_in`, AND `OpExitWhile_v0` IS REFUSED FOR IT.** Judgement, cycle 49,
    2026-09-20, answering the two `OPEN:` lines the material session raised while applying 31. This replaces 31(d)'s
    naming of `OpExitWhile_v0` as "the scaffold of record"; everything else in 30 and 31 stands.
    - (a) ?뵶 **`OpExitWhile_v0` MUST NOT be the S2 scaffold.** Measured: it sources the conditional terminal from a
      **front-panel Boolean control by name** (`tools/gscript.py:1083-1114`). That fails 31(e) twice over ??it
      delivers the operator's value, which is **FALSE at load** (the exact "instrument that hangs" 30(f) forbids),
      and it would add readers of an ORIGINAL front-panel control in three new places, which is the original's
      wiring and not scaffolding. **Do not wire `"stop (end)"`, or any other original control, into a new loop.**
      The assumption the material session proceeded under (`SCAFFOLD_STOP_CONTROL = "stop (end)"`) is OVERTURNED.
    - (b) **The order inside the stage is: create the three loops ??`move_in` the three nodes ??scaffold the three
      conditional terminals ??save.** This dissolves the whole difficulty. The body-node-addressed routes
      (`OpCreateConstOnTerm_v0`, `OpCreateEqual_v0` ??`OpStopFromNode_v0`) were unreachable only because an empty
      body has no node to address; after `move_in` each new body holds its relocated node. **Intermediate
      illegality inside a stage is expected and permitted** ??only the SAVE requires `ExecState != 0`
      (`tools/gscript.py:2065-2071`, 29(d)), and that is the whole reason 29(e)/30(b) make this one stage.
    - (c) **A3 goes back to being a real MEASUREMENT, over every built op, not a one-op availability check.** Phase
      A reports, for each candidate ??`OpCreateConstOnTerm_v0`, `OpCreateConst_v0`, `OpCreateEqual_v0`,
      `OpStopFromNode_v0`, `OpExitWhile_v0`, and anything else in `docs/toolkit-capabilities.md` that writes a While
      loop's conditional terminal or creates a constant ??(i) its exact inputs, (ii) what it addresses (a terminal
      reference, a body node, or a panel-control name), (iii) whether the Boolean it delivers is a **constant** and
      whether its value can be set **TRUE** by that op or by another already-built op, (iv) the measured evidence
      line. No new op and no new device (Pre-decided 2); phase A still edits nothing.
    - (d) **Selection rule, applied mechanically by the recipe from A3's own table** ??judgement is already spent
      here, so the material session does not come back: **(1)** an op that puts a Boolean **constant TRUE** on the
      conditional terminal wins; **(2)** failing that, `OpCreateEqual_v0` ??`OpStopFromNode_v0`, and **only if** its
      delivered value is provably constant TRUE from its own measured record (`tools/bench/build_opsentinel_ops_run3.log`
      F5c/F6) ??a comparison whose value is not provable from that record does not qualify; **(3)** nothing else.
      **If neither qualifies, the stage STOPS after phase A and saves `tools/bench/s2a_legality.json`** (30(e)
      branch 4, 31(i)). That is a legitimate end to this cycle: it leaves a file, which is what the user's binding
      rule of 2026-09-19 asks of every cycle, and it hands judgement a real measurement instead of a guess.
    - (e) **v7's exclusion of `#5058` / `#48` / `#376` from its 21 `move_in` landings does NOT send S2 back to
      delete-and-re-drop.** 31(b) said only an exclusion *with a stated cause* could; the cause v7 states
      (`tools/bench/build_d1_routeb_v7_run10.log:53`, `docs/d1-route-b-plan.md:62-72`) is that a fresh drop removes
      32 named re-wire rows from the cut census ??a **bookkeeping preference about which wires route B wants cut
      later**, not a finding that `move_in` fails on these nodes. Judgement goes the other way on rule 1a: keeping
      the existing wires is strictly safer than destroying and hand-rebuilding 32 of them, and hand re-wiring at
      that scale is the exact stage that killed v3?뭭7 ten times over five cycles. **The 32 rows are S3w's work,
      which is the re-wiring stage, and they are not smuggled into S2 by deleting nodes early.**
    - (f) **Rule 1a, stated for this stage:** `move_in` turns each crossing wire into a While-loop tunnel, and While
      loop tunnels do not auto-index unless explicitly told to, so values pass through unchanged. Phase D RECORDS
      the indexing state of every new tunnel if any built op can read it, and says plainly in the log if none can.
      The three loops are empty of logic, run once under the TRUE scaffold, and S3w removes the scaffold ??no
      per-bead maths and no original wire is altered by S2. ?좑툘 **(f)'s first sentence is WRONG ??see 33(a).**

33. **CORRECTION TO 32, FROM THE ROUND-2 PRIOR-ART REVIEW: `move_in` SEVERS WIRES, IT DOES NOT TUNNEL THEM.**
    Judgement, cycle 49, 2026-09-20, from `archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1250` citing
    `docs/d1-route-b-plan.md:57-58` and `:67`. A wrong sentence in a `Pre-decided` section is worse than no
    sentence, so it is corrected here rather than left for a later session to trip over.
    - (a) **32(f)'s "turns each crossing wire into a While-loop tunnel, so values pass through unchanged" is FALSE.**
      A move severs the node's wires; the relocated node lands in the new body **unwired**. The tunnel-indexing
      reading stays worth taking (`gscript.tunnels` / `OpTunnels_v0` returns `index_mode`,
      `tools/gscript.py:941-978`) ??it simply has nothing to read when no tunnel is created, and the recipe must say
      that rather than imply a pass-through that does not happen.
    - (b) **32(e)'s CONCLUSION survives; its REASON does not.** Branch 1 is still right, but not because it
      "preserves 32 wires" ??it preserves none. It is right because it **keeps the node's identity**: `move_in`
      carries uid, configuration and connector state across, while delete-and-re-drop destroys and re-creates the
      call (SubVI 97 ??94 ??97) and makes every gate that counts subVIs a moving target. The 32 named re-wire rows
      are S3w's work under **either** route, which is exactly why v7's stated reason for excluding these three
      (`tools/bench/build_d1_routeb_v7_run10.log:53`, `docs/d1-route-b-plan.md:62-72`) is a bookkeeping preference
      and not a finding against `move_in`.
    - (c) ?뵶 **THE STAGE BOUNDARY IS RE-OPENED, and phase A is what closes it.** If a moved node lands unwired, then
      branch 1 meets the same wall 29(e) named for delete-and-re-drop: bare required inputs ??`ExecState 0` ??
      `gscript.save()` cannot reach `SaveInstrument` (`tools/gscript.py:2065-2071`) ??**the stage cannot end legal,
      whatever is done to the conditional terminals.** So A2's required-ness question is load-bearing again after
      all, and 31(c)'s "moot" is withdrawn. **Phase A must answer, from already-measured files and without editing
      anything: does a `move_in`'d node land unwired, and does an unwired Required input on any of `#5058` / `#48` /
      `#376` follow from it?** Until that is read, no S2 shape is authorised beyond phase A.
    - (d) **This does not license a bigger stage.** If phase A shows S2 cannot end legal in any shape, the stage
      stops after A with `tools/bench/s2a_legality.json` (30(e) branch 4, 31(i)) and judgement re-cuts the boundary
      ??the likely answer being that the loops, the moves and their re-wiring are one stage, which is 29(e) applied
      honestly rather than a scope increase. Never `allow_broken=True`, never a new op (Pre-decided 2).

## Pre-decided ??ADDED 2026-09-20 (cycle 50): the boundary re-cut 33(d) asked for

34. **S2 IS SMALLER THAN ANY SHAPE CONSIDERED SO FAR: THREE EMPTY WHILE LOOPS, EACH SCAFFOLDED BY
    `OpCreateEqual_v0` ??`OpStopFromNode_v0`, SAVED ??NO `move_in`, NO QUEUES, NO RE-WIRING.** Judgement, cycle 50,
    2026-09-20, from the mandatory failed-prediction review
    `archive/peer/2026-09-20-d1-s2-boundary-recut.md` (ANSWERED, claude/hypothesis opus max, $3.3597, 492 s), which
    refuted **both** of this cycle's own claims. Everything in 30/31/32/33 that this item does not name stands.
    - (a) ?뵶 **`stop_after_a` FALLS: 32(d) rule (2) WAS NEVER EVALUATED, AND IT QUALIFIES.** Cycle 49 concluded S2
      cannot end legal because rule (1) ??an op that places a Boolean *constant* TRUE on a conditional terminal ??
      has no winner. That is still true, and it is beside the point: rule (2)'s pair is **already measured at
      `ExecState` 1**. `docs/toolkit-capabilities.md:63-64` records `OpCreateEqual_v0` placing `Equal?` with **both
      operands taken from one existing node's output terminals** and `OpStopFromNode_v0` driving a While loop's
      conditional terminal from its Boolean (term 119, wire 0 ??387), on a scratch that reads `ExecState` 1;
      `OpCreateEqual_v0` is 23/0 and T5 is closed by measurement in `tools/bench/build_opsentinel_ops_run3.log`
      (F5c/F6). `x == x` is constant TRUE for every non-NaN scalar, which is exactly the provability 32(d) rule (2)
      demands, and it is the harmless-once-through direction 30(f)/31(e) require ??never FALSE, never a hang.
    - (b) ?뵶 **AND THE OPERANDS MAY SIT ON THE OUTER DIAGRAM** (`docs/toolkit-capabilities.md:64`, measured
      `LoopTunnel 0 ??2`). So the scaffold does **not** need a node inside the body, and **32(b)'s premise is
      false**: "the body-node-addressed routes were unreachable only because an empty body has no node to address"
      was never true of this pair. A loop can therefore be created, scaffolded and **saved while its body is still
      empty**, before any node moves. 32(b)'s ordering (loops ??`move_in` ??scaffold ??save) is superseded by:
      **loops ??scaffold ??save.**
    - (c) **The operand must be SCALAR.** An array operand yields a Boolean **array**, which a conditional terminal
      cannot take (round-2 prior art B2; `docs/frame-loop-wire-graph.md:171` measures `#5058` t3
      `Bead is good? array out` as an ARRAY ??the ordinal-picked operand cycle 49 removed for the same reason).
      Pick the operand by NAME from a measured scalar output on `Diagram #686`, never by ordinal.
    - (d) **My own re-cut ??"one complete loop per stage, stop wiring included" ??is REFUTED and withdrawn.** It
      ended each span at the *real* stop condition instead of at a scaffold, inflating ~3 operations into ~20 and
      pulling the re-wiring pass that killed v3?뭭7 back inside the first stage. The peer named it as a smuggled
      premise and it was.
    - (e) **The chain after S2, one atomic step per relocated node.** `move_in` severs wires (33(a)), so a moved
      node lands unwired and may bare a Required input: the move and that node's re-wiring cannot be split, but
      **different nodes can**. Order `#48` (7 cut rows) ??`#376` (12) ??`#5058` (13) ??smallest first, which is
      safe because the inter-loop dependency is **runtime only, not build-time**: all eight `Obtain`s sit at top
      level on `Diagram #686` (`docs/d1-build-plan.md:568-569` 짠9 Scope + the `S1q` gate at `:651` ??re-measured 2026-09-20, was `:593`; `tools/recipes/build_d1_routeb_v7.py:100`), so `#48`'s
      loop builds with `#5058`'s absent. Row counts and every cut terminal are measured in
      `tools/bench/d1_rewire_sources.json` (109 cut terminals, 109 resolved; 32 rows over these three nodes,
      `docs/d1-route-b-plan.md:67`).
    - (f) ?뵶 **NO INTERMEDIATE ARTEFACT MAY EVER BE RUN.** A loop whose real stop condition is a sentinel on a
      queue with no producer blocks forever; a loop still on its `x == x` scaffold runs once and exits. Both are
      legal to SAVE and neither is legal to RUN. Every stage script states this in its log, and no harness may
      open an intermediate `D1_s*.vi` and press Run.
    - (g) ?뵶 **THE DESIGN GAP IS REAL, BUT IT IS NOT "no element types were designed" ??IT IS THAT SIX OF THE EIGHT
      QUEUES HAVE NO `src_name` THAT EXISTS ON THIS COPY.** This cycle opened by measuring that the element types
      ARE on file ??`docs/d1-build-plan.md:544-558` 짠9 (the eight-queue table), `:623-639` 짠9a (re-measured 2026-09-20, was `:565-581`) (the sentinel
      convention), adopted verbatim at `docs/cycle15-plan.md:118-123`, with a producer-consumer core actually built
      at `docs/stage2-assembly-step-c.md:18-30` ??and concluded that
      `tools/recipes/build_d1_routeb_v7.py:131-135`'s "undesigned row" was a stale comment. **That conclusion is
      overturned by the same review.** `queue_node('obtain')` types a queue from a `(node, named output terminal)`
      pair (`tools/gscript.py:1122`), and 짠9 resolves to such a pair for **at most 3 of 8**: "the kernel's own
      outputs" is not a `src_name`; ~~`#10757 .element` names a `Dequeue` the build has yet to create~~ ?뵶 **THAT HALF-SENTENCE IS WRONG ??CORRECTED BY 34(m) BELOW (cycle-51 judgement, 2026-09-20); the strike-through keeps the original readable** ??which is
      where run 3 died (`tools/recipes/build_d1_routeb_v7.py:113-116`); and `docs/cycle15-plan.md:120-121` sources
      `Q_res`/`Q_good` from the **GPU** kernel, a node S2 never places (31(a)). The two files also disagree on a
      type: `Q_focusback` is 1 DBL at `docs/d1-build-plan.md:555` and Bool at `docs/cycle15-plan.md:122`.
      **RESOLVED HERE: 1 DBL.** `#10407` t6 is `position [internal units]`, measured numeric
      (`docs/frame-loop-wire-graph.md:410`), and it is the wire that feeds `#48` t4 `In position` through the
      original's own shift register ??a position, not a flag. The binding document was the wrong one.
      ??**The queue design work owed is a RESOLUTION TABLE, not a new design**: for each of the eight queues, the
      `(uid, exact terminal name, diagram)` that exists at the moment its `Obtain` is placed, or the stage that
      must run first for it to exist. It is a document, it needs no LabVIEW, and it is owed **before the sentinel
      stages** ??not before S2, which uses no queue at all.
    - (h) **The strongest rival explanation for the ten v3?뭭7 deaths is ADDRESS INVALIDATION BY SELF-MUTATION**, and
      it is now a binding constraint on every re-wiring stage: rows addressed by terminal/diagram **INDEX** while
      the build's own tunnel creation and wire severing drift those indices (`docs/toolkit-capabilities.md:70` T2c2,
      a stale index silently wiring a wrong-but-valid source past the sink rule ??
      `archive/peer/2026-09-17-priorart-priorart-routeb-build.md:301`; and Pre-decided 21(d)'s measured **+13**
      index shift inside one instance with no restart). It predicts the observed pattern AND predicts that (e)'s
      finer boundary does **not** help by itself. So: **every address is a uid or an exact name, re-read
      immediately before use and never cached across a mutation.** "Resolve every name up front" (the work-cycle
      rule) is sound for NAMES and unsound for INDICES; the two are not the same instruction.
    - (i) **`tools/recipes/stage_d1_s2.py` is NOT launched and NOT reviewed again on its current bytes.** Its
      1956 lines implement the superseded ordering of 32(b) and its A3 table answers a question (a) has now
      settled. It is kept for its measurement code, not re-armed: paying a third prior-art round on bytes that
      encode a withdrawn boundary is what cost cycle 49 its launch. The next build is a SHORT script.
    - (j) **The discriminating test the review named is the next build, and it is a DIAGNOSTIC, not a stage.** On a
      scratch copy of `claudeDev\D1_s1_copy.vi` (md5 `3e3d23cefd3a334001aa9d6156bf1aee`), built ops only, four
      calls: create one While loop on `Diagram #686` ??`OpCreateEqual_v0` with both operands from ONE measured
      **scalar** output terminal of a `Diagram #686` node ??`OpStopFromNode_v0` onto the loop's conditional
      terminal ??read `ExecState` (ORIGINAL preloaded read-only, 14a) ??`move_in` `#48` ??read `ExecState` again.
      Either branch leaves a file: the readings, plus the saved copy whenever the state is legal. A first reading
      of 1 **falsifies** "S2 cannot end legal"; a second reading of 1 would mean even the move separates from the
      re-wiring and the stages cut finer still.
    - (l) ??**(a)/(b)/(e) ARE NOW MEASURED, NOT CITED ??the test of (j) RAN, 2026-09-20.**
      `tools/bench/diag_s2_scaffold.py` ??`tools/bench/diag_s2_scaffold.log`, `??diag_s2_scaffold.json`, 13 pass /
      1 fail (the one FAIL is step 7's save, which is the expected reading, not a defect):
      - ONE new While loop **#23032** (body Diagram **#23058**) on `Diagram #686`, conditional terminal **#23080**
        driven through wire **23145** by Comparison **#23035**, both operands from the single scalar output of
        node **#8486 `x+1`** ??**`ExecState` 1**, and `gscript.save()` reached `SaveInstrument`:
        `claudeDev\DIAG_s2scaffold_030829.vi`, md5 `eddb3e15e5b0aa673fc2bf59eadd67e2`, 475,422 B, re-read in a
        fresh process **COLD 1 / PRELOADED 1**. **"S2 cannot end legal" is FALSIFIED by the machine.**
      - Then `move_in` `#48` (7 terminals, all 7 wired beforehand) into that body ??**`ExecState` 0**, and the save
        was refused verbatim (`refusing to save a BROKEN VI - SaveInstrument blocks forever on one`);
        `allow_broken` never set, `gui_save` never called. **(e)'s atomicity of move+re-wire is measured, not
        assumed.** ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after; refs 8 opened / 8 closed /
        0 live; no VI was run.
      - ?좑툘 **The operand pre-selected in the brief was WRONG and the census-order fallback is what found the right
        one.** `#637 'frame index'` is not a named source terminal on `Diagram #686` ??`#637`'s outer feed is an
        UNNAMED tunnel (`out_name ''`) ??so a name resolved from a *wire* table is not automatically a `src_name`.
        Resolve operands from the diagram's own output-terminal census, as the diagnostic does.
      - ??**A substitution judgement CONFIRMS:** readings 1 and 2 were taken **in-instance under `Preload`**, not
        in a child process, because the child form restarts LabVIEW and can therefore only read a file on disk ??
        an UNSAVED in-memory edit cannot survive it. That is correct and is now the rule: **the child-process
        `ExecState` read of 29(c) applies to SAVED files; an unsaved intermediate is read in-instance under
        preload.** The saved artefact was read both ways and agreed (1 / 1).
    - (k) **Operating note carried from the cycle-48 retrospective:** `tools/hash_probe.py` is the read-only
      md5/sha256/size probe for exactly these gates ??`py tools/bgrun.py --material ??-- python -u
      tools/hash_probe.py <path> ??, one `HASH <path> | exists= | size= | md5= | sha256=` line per path, no COM and
      no LabVIEW. Use it for every artefact md5 a stage must record.
    - (m) ?뵶 **CORRECTION to (g), by the cycle-51 judgement session, 2026-09-20 ??`#10757 .element` is NOT an
      unbuilt `Dequeue`.** DECISION: the struck half-sentence at `docs/cycle27-plan.md:916` was wrong on the
      mechanism. `#10757` **is** an `Index Array [array, element, index]` ??MEASURED: `element` is one of its three
      real, named terminals (`docs/frame-loop-wire-graph.md:86`), so `.element` IS a named output terminal and
      `queue_node('obtain')`'s `(node, named output terminal)` requirement (`tools/gscript.py:1122`) is satisfiable
      by it in principle. **The obstacle is the DIAGRAM, not the name**: `#10757` is a body node of `#637` that
      relocates into loop 1.2 (`docs/d1-build-plan.md:295`), so it is not on `Diagram #686` at the moment `Q_focus`'s
      `Obtain` is placed, and on `#686` the same family exports only the ARRAY (`#637` t24 `pos in cal image out`).
      `Q_focus` therefore stays state **C** for a different reason than (g) gave (`docs/d1-build-plan.md:584`).
      Everything else in (g) ??"at most 3 of 8", the `Q_focusback` 1-DBL resolution, and the resolution table being
      the work owed ??stands unchanged. The original sentence is struck, not deleted, so the record stays readable.

35. **THE QUEUE `element data type` DONOR MUST EXIST BEFORE THE LOOPS START, AND THE SCAFFOLDS MUST BE REMOVED BY
    THE SENTINEL STAGES.** Judgement, cycle 51, 2026-09-20, added after the `Obtain` resolution table was written
    into `docs/d1-build-plan.md:560-616` and the cycle-51 prior-art review of the S2 recipe came back
    (`archive/peer/2026-09-20-priorart-d1-s2-loops.md`, ANSWERED). 34 stands as written; this constrains what the
    queue stages may do with it.
    - (a) ?뵶 **DONOR CONSTRAINT ??a queue's `element data type` comes from a source available BEFORE the loops
      start (a constant or a pre-loop node), NEVER from a tunnel out of `#637`.** DECISION: every state-**A** pair
      in the new 짠9 table (`docs/d1-build-plan.md:576-585`) sources from `#637`'s **outer** terminals ??output
      tunnels and right shift registers' outside terminals ??which carry **post-loop** values only. `element data
      type` is a *wired* input on the created `Obtain Queue` node, so an `Obtain` typed from one of them could not
      produce its refnum until the frame loop had ended, while the loops that need that refnum wait on it: a
      structurally legal `ExecState 1` with a **guaranteed runtime deadlock** (the R1 risk already written at
      `docs/d1-build-plan.md:596-602`). **Rule 1a is NOT engaged**: `Obtain Queue` discards the donor's *value* and
      keeps only its *type*, so changing the donor changes no computation ??no per-bead maths and no original wire
      is touched.
    - (b) **WHAT REMAINS IS A MEASUREMENT, NOT A DECISION.** Which donor *shapes* `queue_node('obtain')`
      (`tools/gscript.py:1122`) can actually accept is unknown: the op requires a **named** output terminal, and a
      LabVIEW diagram constant's terminal is **unnamed** ??the same `out_name ''` failure cycle 50 hit on `#637`'s
      outer feed (34(l), `docs/cycle27-plan.md:961-964`). So a "use a constant instead" instruction is not yet
      executable. **Until that is measured, NO queue stage is written**; the measurement is a diagnostic under
      `tools/bench/`, not a recipe, and its result comes back to judgement as facts (the material session does not
      pick the donor).
    - (c) ?뵶 **SCAFFOLD REMOVAL IS PART OF EACH LOOP'S SENTINEL STAGE, NOT A SEPARATE PASS.** Each `x == x`
      scaffold (34(a)/(b)) adds one `Equal?` and one border tunnel, and **no document named the stage that takes
      them out** ??as written they would ride into the delivered VI. DECISION: when a loop's real stop condition is
      wired (the end-of-stream sentinel of 짠9a, `docs/d1-build-plan.md:623-639`), that same stage **deletes that
      loop's `Equal?` and its border tunnel**, and its gate asserts **`Comparison` ?? and `LoopTunnel` ?? for that
      loop**, measured against the stage's own before-census. **No scaffold survives into the delivered VI.**
    - (d) **TWO GATE REQUIREMENTS NOW BIND EVERY LATER STAGE**, both accepted from the cycle-51 prior-art review
      (`archive/peer/2026-09-20-priorart-d1-s2-loops.md`): (1) a value returned **beside a non-zero error column**
      is reported **UNREAD** ??never as a value and never as a silent FAIL (14, `docs/cycle27-plan.md:147-150`);
      (2) **SubVI acceptance is a TABLE comparison against the ORIGINAL, never a class COUNT**, because
      `shutil.copy2` re-binds 22 calls and loses 8 while leaving the count intact (29(g),
      `docs/cycle27-plan.md:629-641`; the built FATAL instrument is `tools/recipes/stage_d1_s1.py:182-188` and
      `:377-400`).

## Pre-decided ??ADDED 2026-09-20 (cycle 52): S2 accepted 쨌 the donor rule 쨌 S3's forced shape

36. **THE QUEUE DONOR MUST BE A NODE ??"USE A CONSTANT" AND "USE A FRONT-PANEL CONTROL" ARE BOTH MEASURED
    UNEXECUTABLE, AND THE TYPE CENSUS 35(b) ASKED FOR CANNOT BE TAKEN BY THE BUILT FLEET.** Judgement, cycle 52,
    2026-09-20, from `tools/bench/diag_queue_donor.{py,log,json}` (12/0), `??diag_queue_donor2.*` (16 gates) and
    `??diag_donor_census.*` (14/0). 35(a)'s ban on `#637` outer terminals stands; 35(b) is answered as far as the
    fleet can answer it.
    - (a) ?뵶 **`queue_node('obtain')` accepts only an object that is in `AbstractDiagram.Nodes[]` AND exposes a
      named source terminal ??i.e. a real NODE.** Measured REFUSED, all four shapes: a diagram constant on `#686`
      (`error 1057: To More Specific Class in OpQueueObtain_v0.vi`; the placed constant `#23258` is not in
      `Nodes[]`); a **scalar** front-panel ControlTerminal (`#23124`) and a **cluster** one (`#23493`) ??both born
      on `TopLevelDiagram #536`, both relocated onto `#686` by `move_in` with no error, both absent from `Nodes[]`
      with `out_name` empty, both refused with the same 1057; and `OpCreateConstOnTerm_v0` on a `Diagram` container
      (`invoke error 1055`, created uid 0), whose positive control INSIDE `WhileLoop #637` created constant `#23716`
      cleanly ??**the restriction is that op's `Loop.Diagram` downcast, intrinsic to the container class, not the
      call.** Measured ACCEPTED: a node's named output (`#8486 'x+1'` ??`Obtain Queue #23032`) and a `#637` outer
      terminal (`current image number`), which 35(a) forbids.
    - (b) **A newly placed donor node is not a free fallback ??it must be fully wired or the VI never saves.**
      `build_index_array` alone, one unwired Index Array on the top-level diagram, took a legal scratch from
      `ExecState` 1 to 0, and **deleting the node did not restore it** (`tools/bench/diag_qdonor2_ia.log:17,26-27`).
      The explanation first offered was refuted on its own falsification criterion by the peer-prescribed test
      (`archive/peer/2026-09-20-qdonor2-p8-no-saved-artefact.md`, ANSWERED, claude/hypothesis opus max); the
      surviving alternative ??a `Connect Wire`-family (1304) op run perturbing compile state,
      `docs/NAMES.md:912-921` ??is **UNVERIFIED and OPEN**. It sits on the queue path, not the move path, so it
      blocks no D1 stage.
    - (c) ?뵶 **NO BUILT OP READS `Terminal.DataType`** ??`node_terms` gives name/is_source/wire, `report_all` gives
      class/uid/pos/owner, `node_info` gives `Node.Style` for TOP-LEVEL nodes only and `#686` is not top level. A
      reader would be a new op, which Pre-decided 2 forbids. What WAS measured on `Diagram #686`: **24 `Nodes[]`**
      (21 originals + the three S2 loops); **18 of the 24 are independent of `#637`** (`8486, 7201, 781, 250, 6951,
      6409, 8953, 9342, 9179, 28124, 27605, 28670, 25380, 25091, 25149, 23032, 10170, 23041`); the three new loops
      expose **0** named outputs; and all five state-**A** queues name `#637` ??the one node that is NOT
      independent of it ??while `Q_free`/`Q_work` (IMAQ image refnum) and `Q_focus` (DBL scalar) have no
      `(node, named output terminal)` pair on `#686` at all.
    - (d) **DECISION ??the donor is found BY CONSTRUCTION, not by a type reader.** The machine will not report a
      terminal's type, but `queue_node('obtain')` itself either accepts a donor or refuses it, and a created
      `Obtain Queue` can be read back. So the next donor step is a **trial census** over the 18 independent nodes'
      named outputs: attempt the `Obtain`, read back what the queue is typed as. No new op, no inference. It is
      **not on the critical path ??no queue stage is written before it, and it waits behind S3.**

37. **S2 IS ACCEPTED, AND S3 IS ATOMIC BY THE MACHINE'S OWN CONSTRAINT: THE WHOLE 1.5 NODE SET MOVES AND IS
    RE-WIRED IN ONE SAVED STAGE.** Judgement, cycle 52, 2026-09-20, from `tools/bench/verify_d1_s2.{log,json}`
    (23/0), `??diag_movein_set.*` (13/1) and a read of `tools/bench/d1_rewire_sources.json`.
    - (a) ??**D1 STAGE S2 IS DELIVERED**: `claudeDev\D1_s2_loops.vi`, md5 `6ff19497f2309e007a214660bb64b911`,
      475,707 B. Re-read FROM THE SAVED FILE: `ExecState` COLD **1** / PRELOADED **1**; census Diagram 173 쨌
      WhileLoop 6 쨌 SubVI 97 쨌 Comparison 17 쨌 LoopTunnel 135 쨌 Wire 1905. **Verification level: STRUCTURAL** ??no
      VI was run, and 34(f) forbids running an intermediate.
      ??**Accepted on TWO independent runs, not one:** cycle 51's own `tools/bench/stage_d1_s2_loops.log` ends
      **35 pass / 0 fail** with `G15 FATAL PASS` and `BGRUN END rc=0 after 776s` (300 lines, written to 04:06), and
      cycle 52's `tools/bench/verify_d1_s2.{log,json}` reaches the same numbers at **23/0**. ?좑툘 Cycle 52 dispatched
      that second run believing the first had been killed ??it had not; see **37(j)**. The duplication was the
      cost of the error, but the doubled evidence is genuine.
    - (b) ?뵶 **`#10170` IS A NEW LOOP THAT REUSED A FREED LOW uid** (`tools/gscript.py:2353-2356`), and rule 1a is
      intact. S1's While loops are `{637, 15173, 25380}`; S2 adds **exactly** `{10170, 23032, 23041}`, all owned by
      `Diagram #686`. Ownership by traversal, never by index: `#23080 ??Diagram #23058 ??WhileLoop #23032` 쨌
      `#23246 ??#23166 ??#10170` 쨌 `#23456 ??#23405 ??#23041`. Every pre-existing loop's conditional terminal and
      the wire on it are **identical in S1 and S2** (`637 ??#648/w3457` 쨌 `15173 ??#15276/w19456` 쨌
      `25380 ??#25410/w1737`), so **no original stop condition was touched**. The three new `Equal?`s each drive one
      new conditional terminal, and all three read back **READ** with empty error columns.
      ?좑툘 **The alarm was raised by a REPORTING defect, not a build defect:** `stage_d1_s2_loops.py`'s closing report
      re-read the loops **by array index** ??the very thing 34(h) forbids ??and printed a pre-existing loop's uid
      beside a new loop's conditional terminal. **Every stage report re-reads by uid or by ownership traversal.**
      ?좑툘?좑툘 **And the warning was already on file, unread:** `tools/gscript.py:2353-2356` says verbatim *"Nodes[] is
      CREATION order ??Newly created nodes reuse low uids (90, 98 seen 2026-09-06 20:0x) and go to the END of
      Nodes[]"*. Both halves of this cycle's scare ??a new loop wearing a low uid, and an index read returning the
      wrong object ??are that one docstring. Read it before writing any census-order or index-order code.
    - (c) **The SubVI table's one missing row is REQUIRED, not tolerated.** `(diagram 639, node 22700)` is
      `IMAQ Write TIFF File 2`, inserted into the working copy for fixture recording on 2026-09-01
      (`docs/d1-build-plan.md:310`, `docs/fixture-recording.md:17`); the true original has no such node.
      `tools/recipes/stage_d1_s1.py:245-246` hard-codes `PIN_SUBVI_ROWS = 98` and `TIFF_SUBVI_KEY`, `:729` passes it
      as the expected-missing set, and `:738-741` gates ORIGINAL == 98 and artefact == 97. S2 reuses that instrument
      (`stage_d1_s2_loops.py:361`) and reads missing 0 / extra 0 / changed 0, 0 rows into `background VIs_COPY`.
    - (d) ?뵶 **`move_in` TAKES ONE NODE PER CALL AND SEVERS EVERY WIRE ON IT, IN EITHER ORDER ??there is no "move
      the set and keep its internal wires".** Measured on the real pair `#3529 '- Inc (PgDn)' ??#48
      '-Inc reference'` (wire 4833), moving the SOURCE first and the SINK second into body `Diagram #23058`: after
      move 1 `#3529` goes 1 ??**0** wired and w4833 reads 1 terminal; after move 2 `#48` goes 7 ??**0** wired and
      w4833 reads **0**. The op's `'UID 3'` control is a scalar int (`is_sequence False`) and no array form exists
      ??`move_in` is not in `gscript.py` at all, it is `tools/recipes/build_d1_v0.py:318`
      `def move_in(target, uid, dest_diagram_index, position)`, one uid per call. `ExecState` 0 afterwards; the
      save was refused.
    - (e) ?뵶?뵶 **A WIRE COUNT CAN NEVER DETECT A CUT ??every re-wiring gate counts WIRED TERMINALS.** The whole-VI
      `Wire` census stayed **1905 ??1905 ??1905** across both moves and uid **4833 is still in the Wire list**, with
      zero terminals: `move_in` detaches terminals and leaves the Wire object behind. Any stage gated on a Wire
      delta would have reported all green with its wires cut ??a live candidate contributor to the v3?뭭7 deaths.
      S2's `Wire 1899 ??1905` line was REPORTED, not gated, which is why it did no harm.
    - (f) **TWO ADDRESSES CORRECTED, measured:** `#48` and `#3529` sit on **`Diagram #639`** ??`WhileLoop #637`'s
      body ??**not on `#686`**, and `#3529` is a **`ControlReferenceConstant`**, not a function node. A gate
      assertion written the other way was a drafting error the machine corrected, and it is 34(h)'s own lesson: an
      address is read, never assumed. ~~**No hypothesis review is owed for it** ??no explanatory hypothesis drove
      any work, and the observation agrees with `docs/d1-build-plan.md:250`.~~ ?뵶 **THAT RULING IS WITHDRAWN by the
      cycle-52 retrospective** (`archive/peer/2026-09-20-retrospective-cycle52.md`, `VIOLATION: device-failed`,
      evidence `tools/bench/diag_movein_set.log:57`): excusing a failed prediction because it looks like a drafting
      error is judgement overriding a mechanical rule, and CLAUDE.md is explicit that one's own successful
      discriminating test does not discharge the mandate. **The P6 review IS owed and is a prerequisite to the S3
      build** ??`-Agent claude -Role hypothesis`. The strike-through keeps the withdrawn reasoning readable.
    - (g) ?뵶 **DECISION ??S3 = `claudeDev\D1_s3_loop15.vi`: move the WHOLE 1.5 FOCUS node set into loop a and
      re-wire it, in ONE script with ONE save.** There is no smaller legal unit: all 7 of `#48`'s cut rows are
      internal to the 1.5 set (`#3529`, `#3560`, `#3447`, `CaseStructure #10407`, and the two shift registers
      `#4334/#4344` VISA and `#4256/#4274` position), **none** of its sources stays on `#686`
      (`docs/d1-build-plan.md:250, :306, :330-332, :340, :359-360`), (d) severs every wire whichever order is used,
      and an intermediate at `ExecState` 0 cannot be saved ??so a part-moved set leaves no file, which the split
      rule forbids outright. **The stage is atomic because the machine makes it so, not by choice.** Inside it the
      split rule is honoured the way it can be: a census + readings JSON after each phase, re-wiring in batches of
      10??5 rows, each batch gated on **wired-terminal counts** per (e), and the single `g.save()` at the end with
      `allow_broken` False.
    - (h) **LOOP IDENTITY IS ASSIGNED HERE, because no document assigned it** (a grep over `docs/` for
      `23032|10170|23041` returns one hit, `docs/cycle27-plan.md:951`, about cycle 50's diagnostic loop). The S2
      recipe's labels are a = `#23032` body `#23058` @(2600,2600) 쨌 b = `#10170` body `#23166` @(2600,3400) 쨌
      c = `#23041` body `#23405` @(2600,4200). **DECISION: loop a `#23032` (body `#23058`) IS loop 1.5 FOCUS.**
      b and c are assigned when their node sets are named. The assignment is arbitrary but **binding** ??cite this
      line, never re-derive it.
    - (i) ?뵶 **`guard_peer` IS BLIND TO THE NEW DIAGNOSTICS' FAILURES, AND THE REPAIR IS AT BOTH ENDS.** Verified
      here, not taken on report: `guard_peer.py:73`'s `FAILURE_RE` ends `^\s*(?:->\s*)?FAIL\b` and `:71` documents
      the fleet's gate format as `  FAIL  `, which it matches ??but the cycle-50/52 diagnostics print
      `  **FAIL**  ` (`tools/bench/diag_movein_set.log:57`, and `bgrun`'s own INNER FAILURE line at `:128` repeats
      the bolded form), which it does not. So the mandatory-review gate silently passed a failing run. ?좑툘 **The
      material session proposed widening the regex alone; that is the wrong half on its own**, because it leaves
      every new script free to invent a third format. Fix BOTH: make the diagnostics emit the documented `  FAIL  `,
      and widen `FAILURE_RE` to tolerate `\*{0,2}FAIL`. This is the REPAIR of an existing gate, not a new device.
    - (j) ?뵶 **A LOG READ WHILE ITS RUN MAY STILL BE IN FLIGHT IS NOT A READING ??the terminal `BGRUN END` /
      `BGRUN TIMEOUT` line is the only proof a run finished.** Cycle 52 opened by reading `tail -c 3000` of
      `tools/bench/stage_d1_s2_loops.log` when the file was **12,978 B, mtime 03:55**, saw it stop mid-sentence
      inside a cold re-read with no terminal line, and concluded the session exit had killed the child. It had not:
      bgrun's **breakaway detach** kept the child alive and it finished at **04:06** at 50,905 B / 300 lines,
      `35 pass / 0 fail`, `BGRUN END rc=0 after 776s`. The session then spent an 825 s re-verification on gates that
      were passing as it read. Named by the cycle-52 retrospective as
      `VIOLATION: inference-over-measurement | loss_min=10 | evidence=tools/bench/stage_d1_s2_loops.log:300`,
      accepted in full after re-reading the file. **Before drawing any conclusion from a log, check that its
      terminal line is present; if it is not, the run is live and the file is not yet evidence.** Size and mtime are
      the cheap tell ??a log whose mtime is within a minute of now is being written.
      ?좑툘 What this does NOT excuse: 54(b) was still breached at 03:55:17 ??a session ended with a child running ??
      and the work survived only because a mechanism covered for a broken rule. **Hold the turn open until the child
      lands** remains binding; the detach is a safety net, not a licence.
      ?뵶 **VARIANT FOUND THE HARD WAY, cycle 53: ON AN APPEND-MODE LOG, "the terminal line is present" IS NOT A
      TEST.** `tools/bench/retro.log` accumulates across cycles, so a watcher of the form
      `until grep -q "BGRUN END" retro.log` returns **instantly**, satisfied by the *previous* cycle's END line,
      and a grep of its matching lines then reports the previous cycle's `VIOLATION:` verdicts as if they were
      this cycle's. Cycle 53 armed exactly that watcher, was handed cycle 50's `VIOLATION: none` and cycle 52's
      two violations, and caught it only by reading the run's own `bgrun` task file. **Wait on the run's OWN
      output (the `bgrun` task file, or a per-run log), never on a shared append-mode log; and when a log is
      shared, the test is a terminal line NEWER THAN THIS RUN'S `BGRUN START`, not the presence of one.** Same
      fault class as 37(j) and it defeats 37(j)'s own stated remedy, which is why it is written here.

## Pre-decided ??ADDED 2026-09-20 (cycle 53): S3 withdrawn and re-cut 쨌 the measured 1.5 row table

38. **37(g) IS WITHDRAWN. S3 WAS A FULL-LENGTH RETRY WEARING A DECOMPOSITION'S NAME, AND THE NEXT BUILD IS A
    DIAGNOSTIC, NOT A STAGE.** Judgement, cycle 53, 2026-09-20, from three ANSWERED reviews ??the owed P6
    hypothesis review (`archive/peer/2026-09-20-movein-p6-diagram-misprediction.md`), the prior-art review of the
    S3 recipe (`??priorart-d1-s3-focus.md`, 6 slugs, accepted in full) and `??c53-g2b-caseselector.md` ??plus the
    row classification `tools/bench/c53_row_class.{py,log,json}`. Every disposition is written into the review
    files themselves. 34, 35, 36 stand; this replaces 37(g) and corrects 37(e)'s acceptance criterion.
    - (a) ?뵶 **WHAT WAS WRONG WITH 37(g).** Cycle 52's re-split trigger had already fired (STATUS `owner_c52m2`),
      and CLAUDE.md's split rule clause 3 answers that trigger with *a decomposition plan whose sub-steps each
      name a saved file* ??explicitly **not** "a full-length retry under a new file name". 37(g) answered it with
      one script and one save and called the shape forced. Two of its supports failed: the recipe's own contract
      printed `PREDICTED 0` / `PREDICTED REFUSED` (`tools/recipes/stage_d1_s3_focus.py:149-151`), i.e. a step that
      predicts it leaves no file, which `CLAUDE.md:383` forbids; and my acceptance criterion ??*"per moved node the
      count of WIRED TERMINALS returns to its pre-move value"* ??**was never sound for a move stage**, because two
      rows are queue endpoints excluded by construction (`tools/recipes/build_d1_v0.py:943`, `:976-977`). The
      recipe is **kept unlaunched** for its measurement code, as `stage_d1_s2.py` was; it is not re-armed on these
      bytes and its prior-art STOP RECORD stays armed.
    - (b) **THE MEASURED ROW TABLE ??the decomposition's input, and nobody on the record had it right.**
      `tools/bench/c53_row_class.json`, confirmed three ways (the rewire JSON, the netmap wire table, and
      `main_vi_nodeterms.json` ??a third census by a different op). **17 cut terminals**: `#10407` t0?뱓6, `#48`
      t0?뱓6, and `#3529`/`#3560`/`#3447` t0. By action: `cross-loop:1.2->1.5` **2** 쨌 `from-tunnel` 1 쨌
      `same-loop` 5 쨌 `to-sr` 2 쨌 `from-sr` 2 쨌 `source-side` 5. Sources on `#639` **7**, ~~on `#686` **0**~~,
      far end planned for loop 1.2 **2**, SR-created rows **4**, orphaned counterparts **3**.
      ?뵶 **"SOURCES ON `#686` = 0" IS UNSOUND AND IS STRUCK** ??it is a *negative* claim drawn from
      `main_vi_netmap.json`'s `wires` table, which (h) below measures as TRUNCATED. Re-derive it from
      `main_vi_nodeterms.json` before any stage depends on it. Everything else in this table comes from the
      rewire JSON and nodeterms and survives; G6 passed, all 17 rows agreeing across two independent censuses.
      The two deferred rows are `tools/bench/d1_rewire_sources.json:1748` ??**`#10407` t0, the CASE SELECTOR**,
      fed by `#10686 'x .and. y?'` ??and `:1793` (`#10407` t2, fed by `#10757 'element'`); both far ends sit on
      `#639` today and are planned for row **1.2**, which does not exist. `:1892` is **not** a third crossing:
      `#10407` t6 `position [internal units]` is a **source** whose label reads `to-sr`, far end `#12589` t1, kept
      on row 1.1 by 짠11c (`docs/d1-build-plan.md:398`) ??but **짠6 names no construction verb for it**, so it is a
      real and unclosed gap under a different name. Scoreboard: 37(g) predicted **0** crossings, the P6 review
      predicted **3**, the machine says **2**.
    - (c) ?뵶 **`Required` IS UNKNOWN ON ALL 17 AND IS MEASURED BY CONSTRUCTION, NEVER BY A READER.** No built op
      reports terminal Required-ness and Pre-decided 2 forbids building one ??the same wall 36(c) hit on
      `Terminal.DataType`, and 36(d) settled it the same way: **let the machine answer by accepting or refusing.**
      This matters because `#10407` t0 is a case selector, and "an unwired case selector obviously breaks the VI"
      is precisely the shape of claim that `inference-over-measurement` counts (11 occurrences, recorded
      `docs/violation-decisions.md`, 2026-09-20 06:48). **It is not assumed here in either direction.**
    - (d) ?뵶 **DECISION ??the next build is `tools/bench/diag_s3_focus_trial.py`, a DIAGNOSTIC under
      `tools/bench/`, never a recipe.** This is the 34(j) pattern that carried S2: a cheap run whose *reading* is
      the deliverable and whose saved file is a bonus. On a dated scratch copy of `claudeDev\D1_s2_loops.vi`
      (`6ff19497??): move the five movable nodes into body `Diagram #23058` of loop a `#23032` (37(h), binding);
      create the two SR pairs on loop a with `add_shift_reg`/`wire_sr`, the verb `docs/d1-build-plan.md:402-403`
      gives them; wire every row whose source exists at that moment, using **`OpConnectFromWire_v0.vi`** for the
      from-tunnel row `#10407` t1 (`docs/toolkit-capabilities.md:70` ??the only built writer whose source need not
      be a node, which the withdrawn recipe never imported); leave the two deferred rows and the unnamed `to-sr`
      row bare; then **read `ExecState`**. Save if legal. Either branch leaves
      `tools/bench/diag_s3_focus_trial.json`.
    - (e) ?뵶 **EVERY `move_in` RE-RESOLVES ITS DESTINATION INDEX IMMEDIATELY BEFORE THE CALL.** `move_in(target,
      uid, dest_diagram_index, position)` (`tools/recipes/build_d1_v0.py:318`) addresses its destination by
      **traverse index**, not uid, and relocating a structure relocates its frame diagrams inside that array ??so
      in a multi-move script a later index can be silently wrong and **the op cannot report it**
      (`tools/recipes/build_d1_v0.py:325` writes `SetControlValue("index", int(dest_diagram_index))`; `:358`
      resolves it as `[o['uid'] for o in report_all(target,'Diagram')].index(uid)`).
      ??**MEASURED, AND THE DRIFT HYPOTHESIS IS FALSIFIED FOR `move_in`** ??`tools/bench/diag_destidx_drift.py`
      ??`.log` / `.json`, **15 pass / 0 fail**, `BGRUN END rc=0 after 76s`, every gate REPORTED rather than
      required so no outcome was smuggled in. Across two real `move_in` calls on a scratch copy of S2:
      `idx(#23058)` = **[22, 22, 22]**, `idx(#639)` = **[46, 46, 46]**, Diagram class count = **[173, 173, 173]**,
      traverse order unchanged after both moves, and the explicit stale-index probe says a script that had cached
      `dest_diagram_index=22` would **still address `#23058` correctly**. `owner_of` confirms both nodes landed on
      `#23058`. **So the P6 review's mechanism ??which this item adopted as "the strongest surviving explanation
      for the ten v3?뭭7 deaths" ??does not occur for `move_in`, and that sentence is withdrawn.** Index
      invalidation remains measured for *terminal* and *tunnel* indices (21(d)'s +13 shift, `toolkit-capabilities`
      T2c2); it is the DIAGRAM traverse array that is stable here.
      **The practice stands anyway, now as cheap defence rather than as a fix:** locate `#23058` by uid in a
      freshly-read traverse list before every call and gate that the resolved index still owns it. It costs one
      read and it is the only thing that would detect the behaviour changing.
      ?좑툘 Two further readings from the same run, both consistent with 37(d)/(e): `move_in` echoed uid **23035**
      for *both* calls ??the echo is not the moved object ??and **`ExecState` was 0 after only two of the five
      nodes had moved**, with `g.save()` refused (`allow_broken` False, `gui_save` never called). A move stage
      that does not wire as it goes cannot save, which is exactly what (d) is built to measure.
    - (f) ?뵶 **THE BRANCH IS DELIBERATELY NOT PRE-DECIDED.** A reading of **1** means loop 1.5 can exist before the
      queue stage and (d)'s bytes become the S3 stage next cycle. A reading of **0** means the ordering itself is
      wrong ??the prior-art review's `A2 refuted-already` already showed that "1.5 is buildable alone" was
      authorised by a premise 36(d) removed ??and the queue-donor **trial census** of 36(d), today parked *behind*
      S3, moves in front of it. Writing that branch now would be deciding before the evidence exists, which is the
      one thing a delegation brief may never do.
    - (g) ?뵶 **A CONSTRUCTION THAT IS BANNED BY NAME, because it passes every gate we have.** Do **not** close
      1.5's inputs by tunnelling out of `#637`, wiring on `#686` and tunnelling into `#23032`. It restores every
      wired-terminal count, it compiles to `ExecState` 1, and it **changes the computation** ??autofocus would run
      once after acquisition ends instead of once per frame. Rule 1a, found by the P6 review, and the only
      green-building rule-1a violation identified so far on this path.
    - (h) ?뵶 **THE NETMAP IS NOT A TERMINAL CENSUS.** `tools/bench/sweep_netmap_main.py:63-64` writes
      `"terms": [[t, w] for _ti, t, w in terms if t]` ??an unnamed-terminal filter applied to **every node of every
      class** that also **discards the real terminal index**. 156 unnamed-and-wired terminals exist, `WhileLoop
      #637` t37 among them (`tools/bench/main_vi_nodeterms.json:6868-6872`). Count wired terminals from
      `node_terms`, never from `main_vi_netmap.json`, and never read a terminal index out of it.
      ?뵶 **THE `if t` ACCOUNT IS SECONDARY ??THE REAL MECHANISM IS TRUNCATION, MEASURED 2026-09-20**
      (`archive/peer/2026-09-20-c53-netmap-terms-truncation.md`, ANSWERED, after the 626-node test came back
      **574/626**, not 626/626): `net_map` iterates `for t in range(max_terms)` with **`max_terms=40`**
      (`tools/gscript.py:2549`) and additionally breaks after **three consecutive unnamed+unwired terminals**
      (`:2557-2560`). **`WhileLoop #637` HAS 59 TERMINALS** (`tools/bench/main_vi_nodeterms.json:6424-7131`) ??
      12 of i0?밿39 unnamed, 40 ??12 = 28 named = exactly the netmap array's length. **The one node the entire
      restructure turns on is the one the census silently truncates.** The `empties >= 3` stop explains the other
      51, including the dropped trailing `error out` on `#30804`/`#4620`.
      ?뵶?뵶 **AND `nets` IS BUILT INSIDE THE SAME TRUNCATED LOOP (`:2570-2572`), SO THE `wires` TABLE IS
      TRUNCATED TOO** ??Diagram 19 is missing all of `#637`'s i40?밿58 wire ends (9051, 9000, 9649, 11253, 16421,
      29006, 29122, 28392, 29081, 29106, 32583, 32344), *the border wires of the loop being rebuilt*. Any fact
      about `#637`'s border taken from the netmap is suspect; `docs/frame-loop-wire-graph.md` is the most exposed
      document and its `#637` rows are to be re-derived from nodeterms.
      ?뵶 **THE RULE THIS BUYS, which is broader than the netmap: a NEGATIVE claim ??"nothing else carries this
      wire", "no such terminal exists" ??may NEVER be drawn from a census whose own completeness has not been
      measured.** This cycle used exactly such a claim to reject a *correct* peer finding
      (`archive/peer/2026-09-20-movein-p6-diagram-misprediction.md`, rejection withdrawn the same day), and only
      a second reviewer caught it. ?좑툘 The cap and the early stop were **measured and written down on
      2026-09-14**; prior art existed and was not consulted. This is the third
      confidently-wrong reader in three cycles ??after 37(b)'s index-order read and 37(d)/(e)'s wire count that
      cannot see a cut ??and all three would have passed a green build. **A reader's contract is measured before
      it is used as a gate.**

## Pre-decided ??ADDED 2026-09-20 (cycle 54): the 1.5 trial ran 쨌 the machinery is sound 쨌 the BOUNDARY is not

39. **38(f) RESOLVES TO THE `0` BRANCH ??BUT FOR A DIFFERENT REASON THAN 38(f) EXPECTED, AND THE DIFFERENCE IS
    THE WHOLE RESULT.** Judgement, cycle 54, 2026-09-20, from `tools/bench/diag_s3_focus_trial.{py,log,json}`
    (`BGRUN END rc=0 after 106s`, 43 pass / 0 fail) and `tools/bench/replay_netmap_truncation.{py,log,json}`
    (20 pass / 1 fail, the fail reviewed and disposed). 34??8 stand; this resolves 38(f) and amends 38(b).
    - (a) ?럦 **THE MOVE-AND-REWIRE MACHINERY IS SOUND ??MEASURED END TO END FOR THE FIRST TIME ON REAL ROWS.**
      All five movable nodes (`#10407`, `#48`, `#3529`, `#3560`, `#3447`) moved from `Diagram #639` into body
      `Diagram #23058` of loop a `#23032`; owners re-read by uid confirm all five. **9 of 9 attempted rows wired,
      machine error empty on every one**: five `OpConnectNested_v1` jobs (`#48` t0/t1/t2, `#10407` t3/t5, each
      `wire_delta 1`), three `wire_sr` sides, and ?럦 **`OpConnectFromWire_v0.vi` ACCEPTED the from-tunnel row** ??
      `#10407` t1 bare ??wire **24667**, `Is Broken? 'False'`. The two SR pairs were **created**, not moved
      (`RightShiftRegister #23898` VISA, `#23936` POSITION). `#48` is back to **7/7** wired terminals. The
      destination index re-resolved to **22 on all five calls**, traverse length 173 each time ??38(e)'s drift is
      absent again. **Nothing the trial attempted failed.** After ten v3?뭭7 deaths and five cycles that left no
      file, this is the first positive evidence that the D1 re-wiring path works.
    - (b) ?뵶 **`ExecState` = 0 AND `g.save()` REFUSED** (`RuntimeError: refusing to save a BROKEN VI`,
      `allow_broken` False, `gui_save` never called); scratch `DIAG_s3focus_20260920_072957.vi` is byte-identical
      to S2. Census reported never gated: LoopTunnel 135 ??137, Wire 1905 ??1915. Refs 11/11/**0**.
    - (c) ?뵶 **THE `0` IS OVER-DETERMINED, AND THAT IS NOT A DEFECT OF THE TRIAL ??IT IS THE ANSWER.** Five things
      are simultaneously true of it and the run separated none: `#10407` t0 (case selector) bare, t2 bare, t6 bare,
      the POSITION register's right inside terminal unwired **because** t6 is bare, and `#637`'s old SR pairs now
      orphaned. **Do NOT record "the unwired case selector broke it"** ??38(c) named that exact sentence as the
      shape `inference-over-measurement` counts, `Required` is still unmeasured on all 17 rows, and no built op
      reports it. The `0` is not evidence about any one row.
    - (d) ?뵶 **DECISION ??S3-AS-LOOP-1.5-ALONE IS CLOSED, AND THE FAULT IS THE STAGE BOUNDARY, NOT THE MACHINERY.**
      Every row the trial could wire, it wired; the only holes are the rows whose sources are **not in the set**:
      `#10407` t0 and t2, fed by `#10686 'x .and. y?'` and `#10757 'element'`, both planned for loop **1.2, which
      does not exist** (38(b)), plus t6, for which 짠6 names no construction verb at all. An intermediate at
      `ExecState` 0 cannot be saved ??measured now four times (cycles 50, 52, 53, 54). Therefore: **a saved D1
      stage's node set must be CLOSED UNDER ITS WIRE SOURCES.** 1.5 alone is not, so no ordering of the existing
      stage list makes it savable. This is a stronger and cheaper result than 38(f) anticipated, because it was
      reached without guessing at any row's Required-ness.
    - (e) ?뵶 **CONSEQUENCE ??the queue-donor TRIAL CENSUS of 36(d) moves IN FRONT**, as 38(f)'s `0` branch says,
      and now with a reason of its own: the two open rows are exactly the 1.2 ??1.5 crossings, and a crossing is
      closed by a queue or by 1.2 existing. 36(d)'s trial census is the only thing standing between this project
      and any queue at all, and it is fully specified there. It is no longer parked behind S3.
    - (f) ?뵶 **38(g)'s BANNED CONSTRUCTION IS NOW MORE TEMPTING, NOT LESS ??RE-READ IT.** A green `ExecState` 1 is
      three tunnels away: tunnel out of `#637`, wire on `#686`, tunnel into `#23032`. It would restore every count
      and compile clean, and it would move autofocus off the per-frame path (rule 1a). **It stays banned by name.**
      The same applies to any "temporary stand-in" that closes t0/t2 just to see the VI go green ??a diagnostic
      that manufactures a 1 manufactures the trap.
    - (g) **38(b)'s STRUCK CLAIM IS UN-STRUCK FOR WIRES 4185 / 7506 ONLY, AND ON POSITIVE IDENTIFICATION.** Their
      far ends were on disk all along: `LeftShiftRegister #4344` (4185) and `RightShiftRegister #4334` (7506),
      `tools/bench/main_vi_shiftregs_v1.json` ??both shift registers of `#637`, neither on `#686`. That is a
      positive naming of the carriers, not a census failing to find others, which is why it is allowed. ?뵶 **The
      general prohibition stands and is now quantified: `main_vi_nodeterms.json` enumerates `Node` terminals ONLY**
      ??shift registers (`tools/gscript.py:948`), Constants, 132 LoopTunnel and 114 ControlTerminal are outside it,
      and **800 of 1376 wires have exactly one node carrier**. It licenses no negative claim. "The complete census"
      is retired as a phrase for it.
    - (h) **THE NETMAP TRUNCATION IS FULLY ATTRIBUTED AND `docs/frame-loop-wire-graph.md` WAS NEVER EXPOSED.** All
      **52** shortfalls reproduced from files, 0 unexplained: `max_terms=40` cap = **1** (exactly `WhileLoop #637`),
      `empties>=3` = **51**, `if t` = 0 length-shortfalls though it drops 156 unnamed-and-wired terminals
      census-wide. 574/626 and 59/28 both CONFIRMED. The feared document does not contain the string `netmap` ??
      both its generators read nodeterms, and re-running `stitch_state_carriers.py:40-45` over the full 59-row
      record gives **0 differing names of 12**, so **no row changed**; one dated block was added recording the
      re-derivation. ?좑툘 **Two cycle-54 reviews disagree on a detail and it blocks nothing:**
      `archive/peer/2026-09-20-c54-netmap-wires-table-restatement.md` MEASURED **36** of `#637`'s ends in netmap
      Diagram 19, all at i<40, 0 unattributed; `??c54-netmap-wires-g12.md` asserts **40** with 12 unattributed and
      was never run. **A measurement outranks an unrun verdict**, so 36 is recorded ??and both agree on the only
      load-bearing point: **none of i40?밿58 is present.**
      ??**CORRECTED AT THE CYCLE'S CLOSE ??it is SETTLED, not merely better-supported.** Calling it "reported,
      not resolved" was wrong: run 2's own output reads `n=4 ends=36`
      (`tools/bench/replay_netmap_truncation.log:431`) and the third review states the resolution explicitly. The
      deciding measurement was already in hand when the dispute was recorded, which is the same error class as
      concluding from an unread file. ?좑툘 Note also that the restatement review was recorded "ACCEPTED IN FULL" by
      a material session and a later review **REFUTED parts of it** (disposed in 40(g)); "accepted in full" is not
      the last word on it. ?뵶 **STILL OPEN, cheap and files-only:** the census agreement was measured in ONE
      direction only ??the reverse walk (netmap ??nodeterms) was never computed, and three files put the netmap at
      **635** nodes against 626. It bears on `c53_row_class.json`, an input to the 1.5 row table, so it is in NEXT.
    - (i) ?좑툘 **PROCESS, PAID FOR IN CASH: TWO MATERIAL SESSIONS MUST NOT RUN CONCURRENTLY WHEN BOTH WRITE
      `STATUS.md`.** Cycle 54 dispatched them in parallel for wall-clock. Both wrote lock keys to the same file
      (one flagged "STATUS.md changed on disk mid-session"), and both independently dispatched an opus/max
      hypothesis review of the SAME G12 question ??two reviews, one of them redundant, ??2.8 of it avoidable.
      Parallel material dispatch is allowed only when the two briefs touch disjoint files.

40. **36(d) IS SUPERSEDED: `queue_node('obtain')` IS A SHAPE TEST, NOT A TYPE TEST, AND THE QUEUE IT CREATES IS
    UNREADABLE. THE TYPE TEST IS CONNECTION.** Judgement, cycle 54, 2026-09-20, from
    `tools/bench/diag_queue_trial_census.{py,log,json}` (`BGRUN END rc=0 after 114s`, 16 pass / 0 fail). 36(a),
    36(b) and 36(c) stand unchanged; only 36(d)'s method is replaced.
    - (a) ?뵶 **THE MEASUREMENT: 18 donors attempted, 18 ACCEPTED, 0 REFUSED ??the refusal set is EMPTY.** The 18
      `(node, named output terminal)` pairs span 12 of the 18 independent nodes (6 expose no named output at all:
      `6951, 6409, 28670, 23032, 10170, 23041`) and cover numerics, an IMAQdx session refnum, initialized arrays,
      error clusters, sizes and motor positions. `#637` was absent from the donor list by construction, so 35(a)
      held. **So the `error 1057` that 36(a) measured four times was never about the donor's TYPE ??it was about
      its SHAPE**: in `AbstractDiagram.Nodes[]` with a named source terminal, or refused. Every shape that passes
      that test is accepted whatever it carries.
    - (b) ?뵶?뵶 **AND ALL 18 ACCEPTANCES READ BACK IDENTICALLY.** One signature for every one: `report_all` =
      `{class 'Function', owner 'Diagram', owner_of ('Diagram', 686)}`, label `'Obtain Queue'`, and the same eight
      `node_terms` rows (`name (unnamed)` 쨌 `element data type` 쨌 `create if not found? (T)` 쨌 `error in` 쨌
      `max queue size` 쨌 `queue out`(src) 쨌 `created new?`(src) 쨌 `error out`(src)). Only `uid` and caller-chosen
      `pos` differ. **A queue typed by an array donor is indistinguishable from one typed by a refnum, an error
      cluster or a scalar.** 36(d)'s premise ??"a created `Obtain Queue` can be read back" ??holds for EXISTENCE
      only. The trial census therefore has **no discriminating power**, and running more of it would buy nothing.
    - (c) ?뵶 **DECISION ??TYPE IS TESTED BY CONNECTION, AND LABVIEW IS THE TYPE CHECKER.** We cannot read a
      terminal's type (36(c)) and we cannot read a queue's element type (b). But a type MISMATCH is visible the
      moment two things are wired together, and the reader for that is **already built and already measured**:
      `Wire.Is Broken?` **6371004** (`docs/NAMES.md:902-911`, built 2026-09-17; CLAUDE.md names it as the reader
      to use instead of inferring why a wire is bad). Wire a candidate queue to the consumer its data must
      actually reach and read `Is Broken?`. No new op, so Pre-decided 2 is respected; no inference, so 38(c)'s
      trap is avoided. The donor's type never has to be *named* ??only matched.
    - (d) ?뵶 **BUT THE INSTRUMENT IS VALIDATED BEFORE IT IS USED AS A GATE** ??38(h)'s own closing rule, and the
      lesson of three confidently-wrong readers in three cycles. Before any donor is chosen, run a **matched /
      mismatched control pair** and read `Is Broken?` on both. **If the mismatched wire does not read broken, the
      connection test has no discriminating power either and the queue path needs a different idea entirely** ??
      that is a first-class outcome and must be reported as one, not worked around.
      ?뵶 **THE CONTROL PAIR NEEDS NO QUEUES, AND MUST NOT USE ANY.** Validate the *reader* on the simplest shape
      that can exhibit a type mismatch: two **node-to-node** connections made with `OpConnectNested_v1` ??the op
      that went 5 for 5 this cycle ??one plainly matched and one plainly mismatched, using donors already measured
      to differ (`#250 'IMAQdx Session'`, a refnum, against `#8486 'x+1'`, a numeric). Building queues first would
      put the untested instrument and the untested subject in the same experiment, and would additionally require
      an enqueue/dequeue op whose existence in the built fleet is **not established** ??check
      `docs/toolkit-capabilities.md` before assuming one, and if none exists say so rather than building one
      (Pre-decided 2). Queues enter only after `Is Broken?` has been shown to discriminate.
    - (e) ?좑툘 **WHAT THIS DOES NOT LICENSE.** Do not conclude from (a) that any donor will do. It shows only that
      the op will not stop us; the queue still carries whatever the donor carries, and a wrongly-typed queue will
      surface later as a broken wire or ??worse ??as a silently wrong transfer. Equally, do not read a type off a
      terminal's NAME: `'x+1'` does not prove DBL and `'initialized array'` does not prove which element type.
      Names are labels, and 36(c) remains the measurement that no op reports the type.
    - (f) ??**THE RUN LEFT AN OPENABLE FILE**, as the 4th outcome review requires of every cycle:
      `claudeDev\DIAG_qtrial_20260920_075310_1.vi`, md5 `ada51e8441e1a82ed081ab021abdbbe5`, **481,777 B**, saved
      legally at `ExecState` 1 with `allow_broken` False and `gui_save` never called; LV2026 bytes `26 00 80 00`.
      `ExecState` was **1 ??1 and none of the 18 attempts moved it**, so 36(b)'s "an unwired donor node takes a
      scratch from 1 to 0" did NOT recur ??recorded as an observation, not resolved. Wire 1905 ??**1907** for 18
      added nodes, because two donor terminals were themselves bare (`#25380` t2, t9): reported, not attributed.
      ?좑툘 Traverse class must be resolved **by membership, not by `cls_of`** ??`#25380` is a `WhileLoop` that
      `cls_of` calls "Function", and `#781`/`#8953`/`#28124` are in `Node` but not `Function`.
    - (g) **DISPOSITION of `archive/peer/2026-09-20-c54-g12-after-rerun.md`** (claude/hypothesis opus max,
      ANSWERED, forced by `guard_peer` on the other session's re-run log), which the material session correctly
      recorded without accepting, netmap work not being its brief: **ACCEPTED IN PART by judgement.** Accepted ??
      G12b as phrased was *entailed by* the terminal table printed in the same run rather than independently
      measured, so it is recorded as a derivation, not a measurement; and 짠3's circularity caution is real and is
      adopted as a standing rule: **never validate `main_vi_netmap.json` using an ordering that `net_map` itself
      produced.** Rejected as to consequence ??the load-bearing conclusion, *none of `#637`'s i40?밿58 ends appear
      in the netmap*, follows directly from the measured `max_terms=40` cap (`tools/gscript.py:2549`) and does not
      depend on G12b's phrasing or on any inversion. 39(h) stands unchanged. 짠4's data-contamination point does
      not reach the queue census: that script contains no `netmap` string and reads no netmap-derived datum.

41. **A MATERIAL BRIEF MUST SAY WHAT TO DO WITH A REVIEW THAT ARRIVES MID-RUN ??THREE SENTENCES THAT WOULD HAVE
    PREVENTED THIS CYCLE'S ONLY STRUCTURAL FAULT.** Judgement, cycle 54, 2026-09-20, from its own retrospective
    (`archive/peer/2026-09-20-retrospective-cycle54.md`, `VIOLATION: judgement-in-material | loss_min=9 |
    loss_usd=3.2380`, ACCEPTED IN FULL).
    - (a) **WHAT HAPPENED.** `guard_peer` forced a hypothesis review on a material session mid-run. The session
      collected it, **accepted it in full, wrote its disposition, built its 짠4 discriminating test and re-ran the
      measurement** ??four judgement acts. Twenty-four minutes later a second material session met the same
      situation and wrote *"Accepting or rejecting its findings is a judgement call ??and a material session does
      not make it"*, returning all five objections undecided. **The difference was the brief, not the session.**
      Neither of mine said what to do with an arriving review; one filled the gap, one did not.
    - (b) ?뵶 **THE RULE, to be pasted into every material brief from now on:** *"Any peer review you are FORCED to
      dispatch is RECORDED, never accepted or rejected. Write the exchange to the archive, report its verdict as
      a fact, and return its findings on your `OPEN:` line. Do not act on them: do not redesign a gate, do not
      rebuild a measurement, and do not re-run on the strength of one. The judgement session disposes it."* This
      is a sentence in a brief, not a device ??the user's 2026-09-18 08:53 no-new-device order is respected.
    - (c) **AND TWO PRACTICES THAT COST 9 MINUTES AND $3.24 TOGETHER.** (1) **A gate whose wording a review has
      already falsified is DEMOTED TO A FACT LINE, not re-emitted as a `FAIL`.** G12's false wording fired twice
      after two reviews had measured why it is false; the bgrun FAIL-scan plus `guard_peer`'s mtime-only rule then
      converted that into a third paid review of the same fact. Run 2 treated G16 correctly and G12 incorrectly in
      the same file. (2) **Sequence a run that is expected to retain a `FAIL` LAST**, after anything it could
      block ??the queue census reads nothing netmap-derived and was stalled nine minutes by an unrelated gate.
      ?좑툘 The retrospective's sharpest observation is not the violation: **STATUS now routinely carries "rc=1 ??not
      a crash" annotations, which is the first step toward a working device being bypassed as noise.** The answer
      is to stop producing spurious FAILs, never to get better at explaining them.
    - (d) **NOT BUILT, and recorded as the user's call:** `guard_peer` compares mtimes and has no notion of
      *failure identity*, so an ANSWERED review cannot discharge a re-occurrence of the gate line it reviewed four
      minutes earlier, though `cycle_runner.py` already computes "same first failing GATE line, uids stripped".
      A real repair and a real toll ??but the next cycle's first act is a measurement on the deliverable, and the
      no-new-device order stands.

## Pre-decided ??ADDED 2026-09-20 (cycle 55): the type checker is VALIDATED 쨌 the row table is NOT cleared 쨌 STOP

42. **40(d) RESOLVES TO ITS POSITIVE BRANCH: `Wire.Is Broken?` DISCRIMINATES A TYPE MISMATCH, AND `ExecState`
    DOES NOT.** Judgement, cycle 55, 2026-09-20, from `tools/bench/diag_typectl_v2.{py,log,json}`
    (`BGRUN END rc=0 after 88s`, 19 pass / 0 fail) and, for the withdrawn first attempt,
    `tools/bench/diag_queue_typetest_control.{py,log,json}`. 34??1 stand; this resolves 40(d) and corrects
    two citations in 40.
    - (a) ?럦 **THE CONTROL PAIR, one variable differing.** Same sink terminal, same diagram, same op, same run:
      **leg M (matched)** `#8486` t0 `'x+1'` (numeric) ??`#2048 'Array Subset'` t4 `'index'` read `Is Broken?`
      **False**; **leg X (mismatched)** `#250` t1 `'IMAQdx Session'` (refnum) ??the same `#2048` t4 read
      **True**. Op error column `''` on both; `owner_of` = `('Diagram', 686)` measured for all three nodes.
      **So the instrument discriminates, and 40(d)'s "if the mismatched wire does not read broken the queue path
      needs a different idea entirely" DOES NOT FIRE.** Type is tested by connection (40(c)), now validated
      rather than proposed.
    - (b) ?뵶?뵶 **AND IT CARRIES A CONTRACT THAT MUST BE OBEYED, OR ITS DEFAULT READING IS THE WRONG ONE.** In the
      **writing pass** `Is Broken?` read **False on BOTH legs** ??the naive read calls a type-mismatched
      connection fine. The discriminating value appeared only on an **ordered second, idempotent re-connect**
      (`wire_delta 0`). **RULE: `Is Broken?` is never read in the same pass that makes the connection.** This is
      38(h)'s "validate the instrument before using it as a gate" earning its whole cost ??a fourth
      confidently-wrong reader was one pass away, and the trap is `docs/NAMES.md:905-911`'s, already on disk.
    - (c) ?뵶 **`ExecState` IS NOT A TYPE DISCRIMINATOR AND MUST NEVER BE USED AS ONE.** It fell **1 ??0 on the
      MATCHED leg too**. That refutes, by measurement rather than by argument, the peer suggestion that
      `connect_terminals`' `ExecState 1??` is a less noisy discriminator than `Is Broken?`. Reading both was
      what settled it; a single-signal run would have adopted the wrong one.
    - (d) ?좑툘 **THE MATCHED LEG'S `0` IS OVER-DETERMINED ??do NOT record "the matched connection broke the VI."**
      Both legs were **branches of the donor's existing net, not new wires**: each sink wire uid equals the
      source terminal's pre-existing wire (23519 / 6910) and `Wire` count held 1905 ??1905. A 0 may come from the
      branch, from `#2048` t4's own downstream, or elsewhere; the run separated none. Same shape as 39(c) and
      38(c). ?뵶 **SCOPE LIMIT, binding:** what is validated is `Is Broken?` **on a branched net, read in a
      separate ordered pass**. Behaviour on a *newly created* wire ??the queue case ??is UNMEASURED. It does not
      block, but the first queue connection that disagrees with its construction is checked against this line
      before anything is concluded.
    - (e) **WITHDRAWN, with its reason: the "bare numeric arithmetic input" sink rule was self-defeating.**
      Attempt 1 found **zero** bare named inputs on all five nodes it named, because **"no bare required input"
      is ENTAILED by `ExecState == 1`** ??the rule could not have succeeded on any working VI. Disposition of
      `archive/peer/2026-09-20-c55-sinkrule-no-bare-input.md` (claude/hypothesis opus max, ANSWERED):
      **ACCEPTED** on the entailment and on "the rule never required a *type-constrained* sink" ??the needed
      property was constrained-and-optional, which `#2048` t4/t5 have and an arithmetic primitive's inputs never
      can. Attempt 1's own `Diagram #686` census is what supplied the fix, so it is not a wasted run.
    - (f) **TWO CITATIONS IN 40 ARE WRONG AND ARE CORRECTED HERE.** (1) `Wire.Is Broken?` 6371004 is at
      **`docs/NAMES.md:902-911`**, not `:888-897` (that range is the case-structure property-ID block); 40(c)
      and CLAUDE.md both carried the wrong one ??CLAUDE.md is fixed, 40(c) is corrected by this line. (2) 40(d)
      said enqueue/dequeue ops' existence in the built fleet is "not established": **they exist**
      (`tools/gscript.py:1117-1118`, `docs/toolkit-capabilities.md:32`). Also measured: `connect_terminals`
      `:2407` and `connect2` `:2633` both require a TOP-LEVEL end, so neither reaches `Diagram #686`;
      `OpConnectNested_v1` was used same-diagram.

43. **THE REVERSE CENSUS WALK IS CLEAN, `walk()` IS COMPLETE ??AND `c53_row_class.json` IS STILL NOT CLEARED,
    BECAUSE BOTH TESTS MEASURED THE WRONG GRAIN.** Judgement, cycle 55, from
    `tools/bench/reverse_census_walk.{py,log,json}` (26 pass / 1 fail) and
    `archive/peer/2026-09-20-c55-reverse-census-r14.md` (claude/hypothesis opus max, ANSWERED).
    - (a) ??**THE 635-vs-626 DISCREPANCY IS FULLY ATTRIBUTED AND CLOSES.** Reverse walk (netmap ??nodeterms):
      only uid **22963** absent ??`net_map`'s own junk Invoke ??on 9 diagrams, so 635 = 626 + 9. Forward walk:
      **0** absent, reproducing cycle 54. `diagram_tree_main.json` carries the same junk uid on **11 OTHER,
      disjoint** diagrams always at the last `Nodes[]` index (637 = 626 + 11), and `sweep_nodeterms_main.py:56-59`
      reads UID 0 and **breaks** ??626. Diagram `"0"` holds 0 nodes in both; no class filter contributes. 39(h)'s
      remaining one-directional item is closed.
    - (b) ??**`walk()`'s COMPLETENESS IS MEASURED ??shortfall 0.** Its two stops are
      `tools/recipes/build_opstopfromnode_v0.py:132` (`for n in range(limit)`) and `:134-135` (`if not u: break`);
      the caller passed `limit=200`, so the cap was not binding. `walk_n_nodes` **24** = nodeterms d19's **21** +
      S2's three loops `#23032/#10170/#23041`; terminals **139 = 136 + 3**; **0** per-node terminal-count
      differences on all 21 shared nodes. One more census moves from "unmeasured" to "measured", which is the
      only thing that licenses using it.
    - (c) ?뵶 **BUT THE 17-ROW 1.5 TABLE IS NOT CLEARED, AND MY OWN SECOND ACT ASKED THE WRONG QUESTION.**
      Disposition of the R14 review: **ACCEPTED on its point (e)** ??`c53_row_class.json` is a **TERMINAL**
      table resolved out of the netmap `wires` tables, and `#637` is the VI's single `max_terms=40` cap site with
      shortfall **31** (`tools/bench/c53_row_class.json:267-272`), so **a wire reaching `#637` at t ??40 is absent
      while every node uid still resolves.** Node-uid presence ??what both R5/R6/R7 and R14 tested ??was never
      the right grain. Also **ACCEPTED**: (a) a falsifiable 12/12 gate over `nodeterms ??
      tools/bench/main_vi_shiftregs_v1.json` was available in the same function, so R14 as written could not pass
      against any correct census; (c) the SRs' OUTER terminals **are** in the census as `#637` t11/t10 (wires
      4185/7506), confirming 39(g) ??the objects are outside, the dependency is not; (d) three censuses are three
      reads of one `Nodes[]` array and bound nothing about excluded classes.
    - (d) ?뵶 **R14 IS DEMOTED TO A FACT LINE AND IS NOT RE-RUN (41(c)).** Its wording is falsified, so re-emitting
      it as a `FAIL` would buy a third paid review of a known fact; the material session was right to revert the
      un-run rewrite rather than ship it. **And no required 12/12 gate is added** ??the no-new-device order
      stands (user, 2026-09-18 08:53) and, more to the point, the right test is not node-level at all.
    - (e) **ONE CITATION WITHDRAWN, THE CLAIM SURVIVING ON DIRECT MEASUREMENT.** 39(g) cited
      `tools/gscript.py:947-948` for "shift registers are outside the nodeterms census"; that line is the
      `tunnels()` docstring and distinguishes SRs from `LoopTunnel`s only, so **the citation is withdrawn** ??it
      was `inference-over-measurement` wearing a `file:line`. The claim itself stands on the run's own reading:
      `[4256, 4274, 4334, 4344]` absent from nodeterms, 8 of 12 present.
    - (f) **THE DISCRIMINATING TEST, ADOPTED BUT NOT RUN THIS CYCLE** (the review's own, files-only, ~10 lines):
      all 14 register uids of `tools/bench/main_vi_shiftregs_v1.json` against `diagram_tree_main.json`'s `uids` ??
      **0/14 ??class exclusion, 0 &lt; k &lt; 14 ??selective loss.** It settles (e)'s mechanism cheaply.
    - (g) ?좑툘 **A QUIET LOSS, NAMED: a cycle's `## NEXT` is DESTROYED when the next cycle rewrites it.**
      `archive/2026-09-20-status-cycle54-relocate.md` 짠4 records that cycle 53's NEXT has **no verbatim source on
      disk** ??rewritten in place, only cycle 50's archived, and this is **not a git repository**. Rule 4 says
      nothing is deleted, only moved, and NEXT has been silently exempt. **Habit, not a device: the closing
      session copies the outgoing NEXT into its relocation file before rewriting it.** (The outcome review's
      `git init` recommendation is the real fix and is the user's call ??see 44.)

44. **THE 5th OUTCOME REVIEW FIRED SIX VIOLATIONS AND THE WORK STOPS FOR A RE-PLAN WITH THE USER.** Judgement,
    cycle 55, from `archive/peer/2026-09-20-outcome-review-20260920.md` (claude/outcome, fable medium thin,
    ANSWERED, $3.2236, 199 s), routed by `tools/outcome_review.py:191-192` ??already the 2026-09-18 trial
    routing, nothing patched.
    - (a) **THE VERDICT, verbatim and in order:** `OUTCOME-VIOLATION: goal-requirement-not-advanced` 쨌
      `product-not-runnable` 쨌 `tooling-over-delivery` 쨌 `decision-starved` 쨌 `ordering-stale` 쨌
      `measurement-without-product`. `scope-inflation` explicitly NOT flagged. Q1: *"The user can RUN nothing
      today that they could not run at the last outcome review."* Q2: requirements **1, 2.2, 2.3, 2.4, 2.5, 3**
      have produced nothing runnable since the project began; req 1 not moved for the **4th** consecutive review.
      Q3: *"Not defensible."* Q6: *"The original VI ??the same verdict as all five previous reviews."*
    - (b) ?뵶 **DECISION ??`STOP`.** CLAUDE.md 짠5: an outcome violation makes the next cycle a **delivery** cycle,
      *"and on repetition the work stops for a re-plan with the user."* Delivery cycles HAVE been run since the
      last violation ??S1 (cycle 48) and S2 (cycle 51) both delivered saved files ??and the verdict repeated
      anyway, which is exactly the repetition clause. The reviewer whose only job is "was this worth doing" says
      the ratio is not defensible and names the re-plan as owed. **Continuing on my own judgement would be the
      drift this layer exists to catch**, so the runner is stopped and the question goes to the user.
    - (c) **AND IT IS NOT ANSWERED BY BUILDING ANYTHING.** CLAUDE.md 짠5 forbids answering an outcome violation
      with a device, and the user's 2026-09-18 08:53 no-new-device order stands independently. Nothing was built
      in response to this verdict.
    - (d) **WHAT THE NEXT SESSION RUNS THE MOMENT THE USER SAYS CONTINUE** ??so a "keep going" costs nothing and
      re-derives nothing. The review's own item 2 and 39(d) agree on the shape: **the next act is a STAGE, not a
      diagnostic** ??the minimal loop set that is **CLOSED UNDER ITS WIRE SOURCES**. Concretely that is loop
      **1.2 together with 1.5**, because 1.5's only open rows (`#10407` t0 fed by `#10686 'x .and. y?'`, t2 fed
      by `#10757 'element'`) are exactly the 1.2 ??1.5 crossings, and t6 still needs the construction verb 짠6
      never named. Pre-work, files-only and cheap, in this order: (1) re-derive the 17 rows at **terminal grain**
      from `main_vi_nodeterms.json` (all 59 of `#637`'s terminals) instead of the truncated netmap `wires` table,
      and diff ??43(c); (2) the 14-register class-exclusion test ??43(f). Then the stage, with every connection
      type-checked by `Is Broken?` **on a second ordered pass** ??42(b).
    - (e) ?좑툘 **OPERATIONAL, MEASURED TWICE THIS CYCLE AND UNEXPLAINED: ??0,000 handles are added per ~80-second
      scripting run while `ref_counts` reads 0 live.** 34,207 ??63,416 (attempt 1) and 34,166 ??60,591
      (attempt 2), each after its own restart. **The client-side reference gate cannot see this**, so CLAUDE.md's
      "20 runs leave the handle count flat (짹100)" acceptance is not measuring what it believes. Recorded as a
      FINDING, not a build (no-new-device order). Until it is explained, **restart LabVIEW before every batch**,
      mechanically.

45. **THE USER ANSWERED THE STOP (2026-09-20 ~09:40): CONTINUE ??and 1.5 FOCUS crosses from 1.2 by LOCAL VARIABLES,
    NOT by wires; 1.5 is NOT merged into 1.2.** Interactive chat judgement on the user's words: *"1.5 猷⑦봽???ъ떎
    ?곗씠?곗뿉 ?꾪? ?⑥? ?딅뒗 遺遺꾩씠??local variable ?ъ슜?대룄 臾몄젣媛 ?놁쓣 寃?媛숈?????1.2? ?⑹튂?붽쾶 醫뗭쓣吏, ?꾨땲硫?
    wiring???꾨땶 local variable ?ъ슜??醫뗭쓣吏 ?먮떒?댁꽌 吏꾪뻾?섎룄濡?"* The user also had `git init` run (local only,
    no remote) ??the folder is a repository from this commit on.
    - (a) **NOT merged.** 1.5 carries the ASI serial call (`#48`, VISA). Putting it inside 1.2 (tracking) puts a
      VISA call on the per-frame tracking path ??the exact shape rule 1c disqualifies (*"a mechanism that CAN stall
      the frame loop is disqualified even if it usually does not"*). Separate loop stands.
    - (b) **Local variables ARE the project's recorded latest-value transport for this class of channel** ??
      `docs/decisions.md:28` (scheduler ??motor: *"local variables, as agreed with the user"*),
      `restructure-plan-4.6.md:55`. Prior art exists; this is not a new device. Focus output never enters the
      saved traces (user's domain statement), so a lost or repeated read changes no number the experiment keeps.
    - (c) **What crosses.** 1.5's two open rows are `#10407` t0 ??`#10686 'x .and. y?'` (the every-25-frames
      schedule, BOOLEAN) and `#10407` t2 ??`#10757 .element` (index of closest cal-image slice, bead 2 ??the focus
      PAYLOAD). Construction: on the S2 artefact, create two INDICATORS on the copy's panel, wired at the sources
      **where they are today** (both still in loop 1.1 `#637`, since 1.2 does not exist yet); in loop 1.5
      (`#23032`, 37(h)) read them as LOCAL VARIABLES into t0 / t2. When 1.2 is built later the indicator terminals
      move with their source nodes (one node per `move_in`, 37(d)); the local variables in 1.5 need no change.
      **This makes S3 = 1.5 alone CLOSED UNDER ITS SOURCES ??no 1.2 needed first.** 44(d)'s "1.2 together with
      1.5" is superseded.
    - (d) **Cadence is preserved by an edge, not by luck.** A free-running 1.5 could read the schedule boolean
      twice (double autofocus) or zero times (missed) per 25-frame window. So 1.5 also reads a third local
      variable ??the frame counter that already drives `#10686` ??and acts when `schedule == TRUE AND counter !=
      last-handled counter` (one shift register). Rule 1a reading: the per-bead maths and the ASI command are
      untouched; only WHEN the existing command fires is now decided in another loop, and the user has declared
      that channel data-free. A `Wait (ms)` of 1 ms in 1.5 so it does not spin.
    - (e) **Still forbidden**: the 38(g) tunnel construction (autofocus once after acquisition). Local variables
      are not that: they are read every iteration of a loop that runs concurrently with acquisition.
    - (f) **Stage plan (split rule): S3a** = indicators created and wired at the sources + saved
      (`claudeDev\D1_s3a_focus_ind.vi`, ExecState 1 preloaded, md5 logged) 쨌 **S3b** = the five 1.5 nodes moved into
      `#23032`, internal 7 rows re-wired, t0/t2/t6 fed from local variables / the counter shift register, saved
      (`claudeDev\D1_s3_loop15.vi`). Prior-art review once per stage script; diagnostics under `tools/bench/`
      first when a construction verb (a local variable placed by scripting, `#10407` t6) is unmeasured.
    - (g) **Open for the user, not a blocker**: t6 of `#10407` (짠6 names no construction verb) is resolved by the
      same local-variable route if it is a value, by measurement if it is not.

## Pre-decided ??ADDED 2026-09-20 (cycle 56): the panel-object verb WORKS 쨌 45(c)(iii) corrected 쨌 Pre-decided 2 mis-cited

46. **THE TRANSPORT IS REACHABLE AND ITS FIRST HALF IS BUILT: A FREE-STANDING FRONT-PANEL INDICATOR CAN BE CREATED
    BY SCRIPTING ON THIS VI, AND A SAVED FILE PROVES IT.** Judgement, cycle 56, 2026-09-20, from
    `tools/bench/diag_s56_transport3.{py,log,json}` (21 pass / 7 fail), `?쫡ransport3b.*` (11/3),
    `tools/bench/diag_s56_transport2.*` (13/5), `tools/bench/diag_s3a_ind_transport.*` (6/2, `BGRUN TIMEOUT`) and
    `tools/bench/diag_c56_topdiagram_files.*` (7/0). 34??5 stand; this resolves 45(f)'s diagnostic-first clause,
    corrects 45(c)(iii), and corrects a mis-citation of Pre-decided 2 that ran through all five of the cycle's briefs.
    - (a) ?럦 **THE ROUTE THAT WORKS, measured end to end and SAVED.** `build_index_array` on the
      `VI ??Block Diagram` head places `IndexArray #23486` with `owner_of` = **`('TopLevelDiagram', 536)`**, error
      `''`; `node_info(max_n=40)` goes **0 ??1** (`[(0,'Index Array','Index Array')]`);
      `create_indicator(Nodes[0].Terminals[2])` produces `ControlTerminal` **#23541**, census **114 ??115**, error
      `''`; `delete_object(IndexArray[0])` returns `ExecState` **1** (`remove_bad_wires` not needed). Artefact:
      **`claudeDev\DIAG_s56_t3_p2_20260920_221901.vi`, md5 `cbe9ddd5690983fae2919b3027264d4b`, 476,182 B,
      `26 00 80 00`**, saved legally (`allow_broken` False, `gui_save` never called). The route is
      `docs/NAMES.md:476-478` + `docs/stage2-assembly-step-b.md:49-50`, never before tried on this VI.
      **So the empty top-level `Nodes[]` was EMPTY, not DEAD** ??of the three readings cycle 56 could not separate
      from the files, the measurement picks the first.
    - (b) **`Diagram #536` IS the top-level diagram, and `#686` is NOT.** Live: `Traverse Diagram[0]` =
      `{'class':'TopLevelDiagram','uid':536,'owner':''}`, `diag_index(#536) = 0`. `#686` is a
      **`FlatSequenceFrame`**, and the owner chain `#639 ??WhileLoop #637 ??Diagram #686 ??FlatSequenceFrame #? ??
      STOP` dies in one hop ??the frame's uid is unreadable (`error 1055` on the direct read, `error 1092` for
      `FlatSequenceFrame` as a Traverse class), so `#536` is reached by elimination, never by a walk.
      `diagram_tree_main.json`'s `"0"` row is **neither a diagram nor a placeholder but an index whose identity was
      discarded** (`diagram_tree_main.py:51-52` keeps only `d["owner"]`); `net_map`'s *"0 = top level"*
      (`tools/gscript.py:2505`) was a docstring assumption until this cycle corroborated it.
    - (c) ?뵶 **ALL 114 PRE-EXISTING `ControlTerminal`s ARE OWNED BY CLASS `Diagram`, NOT `TopLevelDiagram`**
      (`tools/bench/diag_s56_transport3b.log:15`, `{'Diagram': 114}`) ??the original's panel terminals all sit
      inside structures, and the top-level diagram held **zero** of them until we made one. This is why
      `wire_indicators` fails: three attempts, at the source's diagram and at `diagram_index=0`, all returned
      `error 5001: LV-Scripting.lvlib:Wire Indicators.vi<ERR> | Control <label> not found` for an indicator the same
      run had just read on the same VI. Target wire **0 ??0**, `#10686` t0 **3/3 wired** before and after, `#637`
      **59 ??59 terminals / 48 ??48 wired**, no tunnel or border object appeared (37(e) grain throughout).
    - (d) ?뵶 **THE ONE REMAINING UNKNOWN FOR S3a IS NOW SINGLE: how to wire a `ControlTerminal` to a node terminal
      on a NESTED diagram.** Candidates, in the order they are to be tried, cheapest first:
      (1) **a pure READ ??does a nested diagram's `Nodes[]` enumerate `ControlTerminal`s at all?**
      `docs/d1-build-plan.md:1227,:1230-1231` records six `ControlTerminal`s on `#639` and `Get Controls.vi`
      returning 5001 at index 0 but succeeding at 43, so the question is answerable from the files and the existing
      censuses. If they ARE enumerated, `OpConnectNested_v1` can address the terminal by index and the connect is
      an ordinary same-diagram one. (2) `move_in` of `ControlTerminal #23541` into `#639` ??37(d)'s severing cost
      does **not** apply, because a freshly created terminal has no wires to cut ??then wire same-diagram.
      (3) `connect_ctl` (`gscript.py:983`, which has run clean before with a top-level `Nodes[]` source) now that a
      node can demonstrably be placed at top level. ?뵶 **Do not spend a fourth `wire_indicators` attempt before (1).**
    - (e) ?뵶 **45(c)(iii) IS CORRECTED: THERE IS NO COUNTER FEEDING `#10686`, AND `'current image number'` IS NOT A
      PER-FRAME COUNTER.** `#3191` is a **`CaseStructure`** ??no function name ??and **all four** of its terminals
      are `is_source=False`: t0 `''` w3050 (selector, from `#3057 'x = 0?'`), t1 `''` w3268, t2
      `'current image number'` w3747, t3 `'LastBufferNumber'` w3356 (`main_vi_nodeterms.json` diagram 43). Wire
      3747's only source in the whole census is **`#6810` t10 = `get buff image-lost frames.vi`**, the camera
      acquisition subVI (`docs/NAMES.md:80-87`; panel row 103, `docs/main-vi-panel-map.md:383`, control 34200), so
      that indicator carries the **camera buffer number, which jumps by more than 1 across lost frames** ??an edge
      on it does NOT fire once per acquired frame. The real frame counter is wire **3268**, which has **0 sources**
      in the census (six sink endpoints: `#376` t7, `#1114` t0, `#2136` t3, `#3191` t1, `#10068` t3, `#29240` t3)
      and arrives from a shift register or border object (`docs/frame-loop-wire-graph.md:161`). **Consequence for
      45(d): the cadence edge is built either on the schedule boolean's own rising edge or on wire 3268 obtained at
      its real source, and which of those is right is NOT decided here** ??the third indicator of 45(c) is
      WITHDRAWN, and S3a creates TWO.
    - (f) **THE SWALLOW IS REPAIRED ??ACCEPTED, and it was the cycle's most expensive lesson.** `gscript.py`'s
      `create_control` and `create_indicator` classified LabVIEW's **error 1055** modal dialog as `"modal dialog"`
      and returned an empty list with `exception None`. Twenty such calls cost **1502 s (a `BGRUN TIMEOUT`) and
      $4.94** before a watchdog screenshot of the dialog explained it. Repaired at both sites in the shape
      `delete_object:2264-2272` already carried, and PROVEN: the same call now raises
      `RuntimeError: run blocked behind a modal dialog (dismissed by watchdog after 8s); screenshot(s): ??.
      **A wrapper that hides the machine's error is worse than no wrapper** ??the sibling of "when a diagnosis is
      guessed twice, build the reader".
    - (g) ?뵶 **AND THE FRAMING THAT COST THE MOST WAS MINE.** Dispatch 3's `L1`/`L2` FAILs made **zero calls to the
      machine** ??they restated a rule as if it were a reading ??and I built the next peer question on top of them
      ("the transport verbs are unreachable, so a new op VI is unavoidable").
      `archive/peer/2026-09-20-c56-transport-verbs-unreachable.md` (claude/hypothesis opus max, ANSWERED, $4.1928)
      refuted it at exactly that point ??*"the claim is not supported by the run that produced it"* ??and named
      `build_index_array ??create_indicator ??delete_object`, `copy_by_index(cls='Local', duplicate=True)` and
      `Control ??Create:Local Variable` 6331C02. **DISPOSITION: ACCEPTED on the decisive point; the "unreachable"
      framing is WITHDRAWN**, and (a) above is that review's own second test, run and passed.
      ?뵶 **RULE for every later brief and every later gate: a gate that makes no call to the machine is not a
      `FAIL`, it is a note, and it may never be listed among measured gates.** Same family as 41(c).
    - (h) **`copy_by_index(cls='Local', duplicate=True)` IS NOT USABLE AS IT STANDS.** It cleared the
      "nothing was copied" check and then raised `RuntimeError: copy_by_index: Target still broken after finish
      (ExecState 0) - not saved` (`gscript.py:1548-1551`): the op works through the shipped
      `NIScriptingExamples\Moving Objects\` fixtures, where ~94 of the main VI's subVI paths do not resolve, and it
      has **no destination-diagram control**, so `move_in` to `#23058` was never reachable through it. Both fixtures
      were left holding md5 `cbe9ddd5??; the documented protocol restores them at the next copy's start. Recorded,
      not repaired, not re-run.
    - (i) **NO GENERIC PROPERTY READER EXISTS**, so the 8 existing `Local` objects' bindings cannot be read: every
      reader in the fleet is purpose-built with a hard-wired ID, and `6355400` (`Local.Control Name`) appears **0
      times** in `docs/vi-server-ids.json` and **0 times** in `tools/gscript.py`. The 8 uids are 2143, 2991, 3097,
      3160, 4277, 11574, 16942, 25805, all owner `Diagram`, count 8 ??8 across the cycle.
    - (j) ?좑툘 **HANDLES ??44(e)'s unexplained growth measured a THIRD and FOURTH time:** 30,684 ??54,367 over 330 s
      and 30,691 ??**63,517** over 78 s, each after the run's own restart, with `ref_counts` reading 26/26/0 and
      13/13/0 live. The client-side reference gate still cannot see it. LabVIEW was left UP (pid 8856) at cycle
      close, so **the next batch restarts first, mechanically.**
    - (k) ?뵶?뵶 **PRE-DECIDED 2 SAYS "NO FURTHER PROCESS DEVICE" ??NOT "NO NEW OP VI" ??AND I MIS-CITED IT IN ALL
      FIVE OF THIS CYCLE'S BRIEFS.** `docs/cycle27-plan.md:31` reads *"**No further process device** (user, 08:53)
      ??still the standing order. A retrospective naming one is a finding."* A **process device** is gate and
      retrospective machinery; an **op VI** is deliverable-construction tooling, and every stage of D1 so far was
      built with them (+17 by the 5th outcome review's own count). So the order does not reach an op VI that places
      a Local Variable, and **the S3b transport needs no decision from the user**: if `Control ??Create:Local
      Variable` 6331C02 through `build_invoke` is the route, it is simply built. The mis-citation is what turned
      (g)'s two no-call gates into FAILs and what sent a $4.19 review out to attack a rule instead of a machine.
      **Cite Pre-decided 2 by its words, never by its remembered shape.**

## Pre-decided ??ADDED 2026-09-20 (cycle 57): the transport is SOLVED for location and addressing 쨌 the blocker is TYPE

47. **THE S3a TRANSPORT RAN END TO END FOR THE FIRST TIME. `move_in` TOP-LEVEL ??NESTED WORKS, AND
    `wire_indicators` GIVEN THE INDICATOR'S OWN DIAGRAM MAKES THE CONNECTION WITH NO 5001.** Judgement, cycle 57,
    2026-09-20, from `tools/bench/diag_s57_ctmove_wire.{py,log,json}` (`BGRUN END rc=1 after 123s`, 27 pass /
    2 fail), the files-only read behind it, and `archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md`
    (claude/priorart, ANSWERED, $7.2933, verdict **NOT novel**, 5 slugs ??all disposed in that file's
    `## What was done with it`). 34??6 stand; this resolves 46(d), closes the three 5001s, and names the one
    thing that actually blocks S3a.
    - (a) ?럦 **THE ROUTE, measured step by step.** On a scratch of `D1_s2_loops.vi`: `build_index_array` on the
      `VI ??Block Diagram` head ??`owner_of` `('TopLevelDiagram',536)`, `node_info` **0 ??1** ??
      `create_indicator(Nodes[0].Terminals[2])` ??`ControlTerminal` **#23541**, census **114 ??115** ??
      `delete_object(IA)` ??`ExecState` **1** (46(a) reproduced exactly, all error columns `''`) ??
      **`move_in(#23541, dest = the LIVE index of `#639`)` ??`owner_of` `('TopLevelDiagram',536)` ??
      `('Diagram',639)`, census 115 ??115, panel rows 115 ??115, `ExecState` STILL 1.** Top-level ??nested had
      never been tried on any terminal, let alone a freshly created one. It leaves one junk `Invoke` uid (the uid
      the deleted Index Array released); purge it in-run.
    - (b) ?럦 **THE THREE 5001s ARE EXPLAINED AND CLOSED ??IT WAS ALWAYS THE ARGUMENT, NEVER THE VERB.**
      `tools/gscript.py:1787-1789` feeds `Diagram in` from `diagram_index`, which scopes the **INDICATOR**
      lookup and never the source. All three cycle-56 attempts named pre-existing indicators whose terminals sit
      on other nested diagrams, so no index passed could have matched. Given `diagram_index` = the diagram where
      the indicator's terminal actually lives, `wire_indicators` **wired**: target wire **0 ??10799**, whole-VI
      `Wire` delta **0** (a branch onto the existing net), `#10686` t0 `'x .and. y?'` **3/3 wired before and
      after**, and **`#637` 59 ??59 terminals / 48 ??48 wired, NO tunnel and NO border object** (37(e) grain).
      The identical fault class was closed once before by measurement ??`docs/d1-build-plan.md:1231`,
      `'Auto-Reset'` at `src_diagram_index=0` ??5001 from `Get Controls.vi`, the same label at 43 ??wired,
      `:1251` "CLOSED by measurement: wrong `src_diagram_index`". **Excluding a verb that has never been given a
      correct argument is the repeat, not a fourth attempt.**
    - (c) ?뵶 **THE 38(g) SEMANTICS OBJECTION IS ACCEPTED, AND IT DECIDES THE ORDER OF THE BUILD.** A top-level
      `ControlTerminal` wired to a source inside `WhileLoop #637` crosses the loop border as a tunnel, and a
      while-loop output tunnel delivers ONE value when the loop ends ??legal, `ExecState` 1, and useless to a
      local-variable read in loop 1.5 that must see the value every iteration. **So `move_in` into `#639` is not
      a fallback, it is the only acceptable route**, and it matches the VI's own practice: all 114 pre-existing
      `ControlTerminal`s are owned by class `Diagram`. The shape is now measured rather than argued ??(b)'s
      59/59 쨌 48/48 쨌 no border object. `tunnel_indicator` (`tools/gscript.py:1882-1903`) is **REJECTED for
      S3a for the same reason**: it builds the indicator off a `Tunnel.'Outer Term'`, i.e. it IS the banned shape.
    - (d) ?뵶 **THE REMAINING BLOCKER IS TYPE, AND NOBODY HAD NAMED IT.** `Terminal.Create Indicator` **6349C02
      takes no type argument**, so a created indicator inherits the type of the terminal it is created from. The
      indicator built by (a) came off the carrier Index Array's `index` terminal ??its label read back off the
      machine as **`'index'`** (hex `696e646578`, no newline, no duplicate) ??i.e. a NUMERIC. Wiring it to the
      **BOOLEAN** `'x .and. y?'` left `ExecState` **1 ??0** and, on the ordered second pass (42(b), idempotent
      re-connect, `wire_delta` 0, op error `''`), **`Is Broken? = True`** ??the signature 42(a) validated for a
      type mismatch. **Competing reading, RECORDED not dismissed** (`archive/peer/2026-09-20-c57-transport-typebreak.md`,
      claude/hypothesis opus max, ANSWERED, $3.7974, 41(b)): that `Is Broken?` also reads True on a two-source
      wire and that 10799 sinks at a structure border, so the break may be the shape rather than the type. The
      two are separated by a control pair on ONE variable ??same verbs, same diagram, same branch-onto-an-existing-net
      shape, numeric source `#10757` t1 `'element'` (wire 10990) in place of the Boolean ??which is 42(a)'s own
      design and is what cycle 57's second build act ran. **?럦 IT RAN, 35 pass / 0 fail, AND THE TYPE READING WINS:**
      `tools/bench/diag_s57_typepair.{py,log,json}` (`BGRUN END rc=0 after 242s`). Identical creation route,
      identical label `'index'`, identical `move_in` into `#639` @46, identical `wire_indicators` call shape, and
      the same branch onto an existing net feeding the same structure-border sink ??**only the source's TYPE
      differed**. Result: op error column **`''`**, indicator wire **0 ??10990**, whole-VI `Wire` **1905 ??1905**,
      `#10757` **3/3 wired before and after**, `#637` **59 ??59 / 48 ??48, no tunnel, no border object**,
      `ExecState` **1 ??1**, and on the ordered second pass (`wire_delta` 0, op error `''`)
      **`Is Broken?` = False on wire 10990**. **The competing shape reading is REFUTED BY MEASUREMENT** ??leg 2
      carries that shape exactly and reads clean ??so the Boolean?뭤umeric mismatch is the cause, and
      `Is Broken?`'s True/False split is again the instrument 42(a) validated.
    - (h) ?럦 **S3a's NUMERIC HALF IS DELIVERED, AND THE SAVE-FIRST ORDER OF (e) IS WHAT MADE IT SURVIVE.** Two
      openable artefacts, both saved legally (`ExecState` 1 at each save point, `allow_broken` False, `gui_save`
      never called), both LV2026 `26 00 80 00`:
      **`claudeDev\D1_s3a_ind_placed_20260920_234341.vi`** md5 `0b9a070289a08a22a8843e287b183398`, 476,209 B ??
      the indicator created and `move_in`-ed onto `Diagram #639`, **unwired**; and
      **`claudeDev\D1_s3a_num_ind_20260920_234341.vi`** md5 `fceaa0a1d068622596842435b830bffe`, 476,146 B ??the
      same, wired to `#10757` t1 `'element'`, the payload source of 45(c). The placed artefact was **reopened
      COLD in a freshly restarted LabVIEW and read `ExecState` 1 with `owner_of(#23541) = ('Diagram',639)`**, so
      the move survives a save/reload and is not an in-memory artefact. Verification level: **STRUCTURAL**, never
      functional ??no VI was run (34(f)).
    - (i) ?뵶 **WHAT IS LEFT OF S3a IS EXACTLY ONE THING: A BOOLEAN-TYPED CARRIER.** Since 6349C02 takes no type
      argument (d), the schedule indicator for `#10686` t0 `'x .and. y?'` must be created from a terminal that is
      already Boolean. `#10757`'s own class was measured `IndexArray` (Traverse index 20 of 47) with terminals
      `[(0,'array',sink,121),(1,'element',SOURCE,10990),(2,'index',sink,10947)]`, and the carrier used so far is
      an unwired Index Array whose `index` terminal is numeric. Two routes, and the **cheap one is tried first**:
      **(1) NO NEW TOOLING ??find an existing builder that places a node with a BOOLEAN terminal at top level**
      (`build_property` `tools/gscript.py:2194` and `build_invoke` `:2159` both already take a `diagram_index`,
      and a Boolean-valued property yields a Boolean output terminal), then create ??`move_in` ??wire by the now
      proven route. **(2) THE DURABLE FIX, permitted and named but NOT built this cycle ??ONE new op VI** that
      calls `Terminal.Create Indicator` on a **nested** diagram's `Nodes[n].Terminals[t]`: a splice of
      `OpConnectNested_v1`'s ladder (`tools/recipes/build_opconnectnested_v1.py:419-420`) with
      `OpCreateIndicator_v0`'s call. It would make the indicator **born correctly typed, correctly located and
      already wired**, retiring `move_in` and `wire_indicators` from this path entirely, and it is allowed ??
      46(k): Pre-decided 2 forbids a further PROCESS DEVICE, not an op VI. Route (1) is first only because it
      costs one diagnostic and no gate; if it fails, (2) is the answer and is not to be deferred again.
    - (j) ?좑툘 **NO READER IN THIS FLEET RETURNS A DATA TYPE.** Measured across 12 hits: the only representation
      reader is `OpConstValueN_v1.vi` (`NumericConstant.Representation` 5DCFC00, `docs/toolkit-capabilities.md:59`,
      `docs/NAMES.md:969`) and it reads a numeric CONSTANT. So a type mismatch is not predictable before wiring
      and can only be read AFTER, through `Is Broken?` on an ordered second pass. **Until a type reader exists,
      every new connection is type-checked by 42(b), never assumed** ??and (d) is the first time that instrument
      has paid for itself on a real build rather than on a calibration pair.
    - (k) ?좑툘 **OPERATIONAL, AND IT COST A RUN: a sub-agent that backgrounds its batch and ENDS ITS TURN kills the
      batch.** Dispatch 4 returned "holding until it lands" and exited; a relaunch then restarted LabVIEW under
      the still-live first run, which died in phase A (`com_error -2147023170 / -2147023174 RPC`) and was logged
      as a **NON-RESULT**, not a budget failure. This is OPEN 54(b) firing exactly as written. **Every material
      brief that backgrounds a run must say: stay in the turn until the log carries its final `BGRUN END`/
      `TIMEOUT` line.** Handles across the two legs: 63,313 ??30,688 ??60,291 ??30,695 ??**63,533**, with
      `ref_counts` 22/22/0 live ??44(e)'s unexplained growth recurs a fifth and sixth time.
    - (e) ?뵶 **A FAULT IN MY OWN BRIEF, AND IT IS THE USER'S 2026-09-19 RULE: THE RUN HELD A LEGAL ARTEFACT AND
      SPENT IT.** `ExecState` was **1** immediately after the `move_in` and the brief's phase order put the wire
      before the save, so a run in which **every transport verb succeeded** ended at `ExecState` 0, saved
      nothing, and left **no file to open**. *"A step is not done until it has left a file."* **RULE for every
      later stage: the save goes at the last point the VI is measured legal, not at the end of the script**, and
      a stage that reaches `ExecState 1` and proceeds past it without saving is a failed stage however well its
      verbs ran. The corrected order is create ??`move_in` ??**save** ??reopen COLD ??wire ??save again.
    - (f) **THE PRIOR-ART REVIEW EARNED ITS $7.29 AND IS DISPOSED IN FULL** ??`contradicted`, `unread-evidence`,
      `refuted-already`, `helper-exists` ACCEPTED (two candidates withdrawn before a call was spent on them,
      the winning verb identified, the 38(g) objection turned into the build order); `already-measured` ACCEPTED
      on its cost and REFUTED on its citation, because the lines it called "a different question" are exactly the
      prior art for the verb that worked. ?좑툘 **The `FIXED:`/`REFUTED:` lines are written but their ACCEPTANCE BY
      `guard_cycle` IS UNVERIFIED** ??the review is stamped 2026-09-20 23:00:54 and `docs/cycle27-plan.md` carries
      a day-granular frontmatter date, which cannot postdate it; the plan date was **deliberately not rolled
      forward to satisfy a gate**. Check with a dry run before the recipe launch.
    - (g) ?좑툘 **CHARGED TO THIS CYCLE: the FIRST ACT re-measured something already on disk.** "Does a nested
      diagram's `Nodes[]` enumerate `ControlTerminal`s?" was answered in four route-B run logs
      (`build_d1_routeb_v*_run*.log:179-180`, `Nodes[None] with terminals []`) and, more strongly, at
      `tools/bench/diag_queue_donor2.log:48,:55`, which measured it **after** a `move_in` into a nested diagram ??
      the exact post-condition that kills candidate (2)'s second half. What the act did add and was needed: the
      verb-addressing table, `move_in`'s uid-addressing and its one prior `ControlTerminal` success
      (`probe_move_ctlterm_v0.log:130-133`), and the `d1-build-plan.md:1231` prior art that produced the route.
      **Before commissioning a read, grep the bench logs for the reading first.**

## Pre-decided ??ADDED 2026-09-21 (cycle 58): the Boolean carrier EXISTS 쨌 route 1's block is STRUCTURAL and has one named fix

48. **A BOOLEAN CARRIER EXISTS AND 47(i) ROUTE 1 IS NOT DEAD ??BUT IT CANNOT REACH 47(e)'s SAVE POINT AS 47(i)
    SPECIFIED IT, AND THE REASON IS A TENSION NOBODY HAD NAMED.** Judgement, cycle 58, 2026-09-21, from
    `tools/bench/diag_s58_boolcarrier.py` and its two runs (`??run1.log` `BGRUN END rc=1 after 229s`, 51 pass /
    9 fail; `??run2.log` `BGRUN END rc=1 after 248s`, 54 pass / 9 fail ??the SAME 9 gates both times).
    34??7 stand; this resolves 47(i) route 1's first half and re-cuts its second.
    - (a) ?럦 **THE CARRIER QUESTION IS ANSWERED: `build_property` (`tools/gscript.py:2194`) IS THE ONLY FLEET VERB
      WITH A BOOLEAN-BY-CONSTRUCTION OUTPUT TERMINAL, AND IT WORKS.** Three candidates placed at the top-level
      diagram with every error column `''`, `owner_of` `('TopLevelDiagram',536)`, `node_info` **0 ??1**,
      ControlTerminal census **114 ??115**: C1 `('VI Server:VI',[291,292])` carrier t4 ??indicator label read off
      the machine **`'Metrics:Front Panel Loaded'`**; C2 `('VI Server:VI',[242])` carrier `'Def Err Handling'` ??
      **`'Automatic Error Handling'`**; C3 `('VI Server:Wire',[6371004])` carrier `'Broken?'` ??**`'Is Broken?'`**
      (so the class string `VI Server:Wire` resolves). `build_invoke` `:2159` is OUT ??no Boolean-returning method
      exists in `docs/vi-server-ids.json`. Every loop/exit verb is out: the conditional terminal is a SINK.
    - (b) ?뵶 **THE BLOCK, AND IT IS STRUCTURAL: A BOOLEAN TYPE NEEDS A *SOURCE* TERMINAL, AND
      `create_indicator` ON A SOURCE TERMINAL MAKES A REAL WIRE.** Whole-VI `Wire` **1905 ??1905 ??1906**: the
      indicator is born wired to the carrier (uid **23586** on C1, **23576** on C2), and that wire is
      **STILL ALIVE after `delete_object(carrier)`**, with 0 pre-existing wire uids removed. `ExecState` therefore
      reads 1 ??1 (after `build_property`) ??1 (after `create_indicator`) ??**0 (after the carrier delete)**
      ???좑툘 **on C1 and C2 ONLY; C3 never reaches that timeline because it breaks at placement, see (c)**, and the
      first writing of this line omitted that qualifier (caught by `archive/peer/2026-09-21-c58-boolwire-dangling.md`
      짠0 and corrected here, cycle 58, by the judgement session). So
      47(e)'s save point is unreachable and all three candidates left **ZERO artefacts**. Cycle 57's route escaped
      this only because its carrier terminal was the Index Array's `index`, a **SINK** ??no wire is created from a
      sink, which is also exactly why that indicator came out NUMERIC. **The two requirements pull against each
      other: the type comes from a source, and the source is what ties the indicator to the carrier.** That is a
      finding about the verb, not a missed call.
    - (c) ?좑툘 **C3 IS WITHDRAWN ON ITS OWN EVIDENCE:** `build_property('VI Server:Wire', ??` takes the VI to
      `ExecState` **0 at placement**, before any delete. C2 is the carrier of record (one property, `ExecState` 1
      throughout, label non-duplicate and newline-free); C1 is its only alternate.
    - (d) ?뵶 **THE DISPOSITION ??ROUTE 1 IS COMPLETED BY ONE NAMED VERB CALL, DECOMPOSED INTO THREE SAVED STEPS,
      AND ROUTE 2 IS NOT TAKEN THIS CYCLE.** The wire that blocks the save is **ours**, created seconds earlier,
      and its uid is held; deleting it before the carrier leaves both ends unwired and should return the VI to the
      state cycle 57 saved from. Of the three dispositions material #1 put on the table, `remove_bad_wires_scripted`
      is **REFUSED** ??it has a measured over-removal on this VI (`archive/2026-09-17-status-d1-route-b-2.md:45`,
      *"DELETES THE TUNNEL"*), which is a rule-1a hazard, and a named-uid delete is strictly narrower. 47(i)
      route 2 (the one op VI, `Terminal.Create Indicator` on a nested `Nodes[n].Terminals[t]`) **remains correct,
      remains permitted (46(k)), and becomes the automatic next act if (e) fails at the same place** ??it is
      deferred here because the 5th outcome review flagged `tooling-over-delivery` and `measurement-without-product`
      verbatim, and a one-call fix that ends in a file beats a new op VI that ends in a self-test.
    - (e) **THE DECOMPOSITION (the user's 2026-09-19 rule: a step is not done until it has left a file). Three
      sub-steps, three artefacts, three pass criteria, each starting from the previous FILE in a FRESH LabVIEW:**
      **S3a-B1** from `claudeDev\D1_s2_loops.vi` ??place C2 ??`create_indicator` on its Boolean source ??**delete
      the created wire by its uid** ??delete the carrier ??pass criterion `ExecState` **1** ??save
      `claudeDev\D1_s3a_boolcarrier_b1_<stamp>.vi`.
      **S3a-B2** from B1, cold ??`move_in(CT ??Diagram #639 @ its LIVE index)`, purge the junk `Invoke` ??pass
      criterion `owner_of` `('Diagram',639)` **and** `ExecState` 1 ??save `??b2_<stamp>.vi`. **This is 47(e)'s save
      point and it comes before any wiring.**
      **S3a-B3** from B2, cold ??`wire_indicators(??#10686 t0 'x .and. y?', diagram_index = the LIVE index of the
      diagram the INDICATOR lives on)` ??ordered second pass (42(b)) ??pass criterion **`Is Broken?` = False** ??
      save `??b3_<stamp>.vi`. A `True` here is the type reading again and sends the next cycle to route 2.
    - (f) ?좑툘 **NO SECOND PRIOR-ART REVIEW IS SPENT ON THIS RE-CUT, AND THAT IS AN ASSUMPTION THE USER MAY
      OVERTURN.** `archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md` ($7.29, verdict NOT novel, 5 slugs, all
      disposed in its `## What was done with it`) reviewed **this same stage** one day ago; (e) changes how the
      stage is CUT, not what is built, and rule 5's archiving exception says to check `archive/peer/` before
      re-asking. Recorded here rather than decided quietly.
      ?뵶 **OVERTURNED THE SAME CYCLE, BY MEASUREMENT, BY THE SESSION THAT WROTE IT.** `guard_cycle`'s
      `premature-build` device refuses the launch verbatim ??*"this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN
      ITSELF"*, recipe last changed **2026-09-21 01:19**, newest prior-art review **2026-09-20 23:00** ??and the
      exemption it offers ("a recipe that HAS already run once under the newest review") does not apply, because
      this recipe has never run. The premise of (f) is simply false: the 2026-09-20 review reviewed a recipe that
      **did not exist**, which is why its stop record reads `sha (none)` (48(g)); it cannot have covered the 1,699
      lines now on disk, so this is not rule 5's "same question re-asked". **A second review IS spent**, and that is
      the right outcome: `CYCLE_GUARD_OFF` is never the answer, and the two releases the gate accepts (`REFUTED:` /
      `FIXED:`) both require a review that saw these bytes. Cost ??$7, against a deliverable one run away.
    - (g) ?좑툘 **`guard_cycle` REFUSES ONE STEP EARLIER THAN 47(f) EXPECTED, AND FOR A DIFFERENT REASON.** Exit **2**
      comes from `tools/stop_record.py`, verbatim: *"this recipe has a released stop record, but the file itself
      cannot be read, so the release cannot be matched to any bytes"*, `unreadable:
      tools/recipes/stage_d1_s3a_focus_ind.py`. So the prior-art review's 4 `FIXED:` + 1 `REFUTED:` lines were
      **never tested** ??the stop record is keyed to the recipe's BYTES, and the gate cannot reach that question
      while the recipe does not exist. **The recipe must be WRITTEN before the gate can be dry-run at all**; no
      date was rolled and `CYCLE_GUARD_OFF` was not set.
    - (h) ?좑툘 **TWO HYPOTHESIS REVIEWS, ANSWERED, RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), NOTHING ACTED
      ON:** `c58-typepair-a1-nonresult` ($3.9606) names three instrument defects (a gate-boundary swallow;
      `diag_s57_typepair.log:37`'s canned reason from an unconditioned `else`; run 1's JSON destroyed by an
      unstamped OUT) ??4 proposals, none implemented. `c58-delete-execstate0` ($3.6322) argued *"the dangling wire
      is not established by this log"* and stated its own falsifier ??*"if uid 23586 is alive after the delete, I
      am wrong"*. **B3d read it alive on all three candidates, so the falsifier fired against the review** and (b)
      stands. The one thing acted on was a REMOVAL: a `remove_bad_wires_scripted` step was written into run 2 and
      **deleted before launch**, correctly ??see (d).
    - (i) ?좑툘 **THE STAGE HAS NOW FAILED TWICE AT THE SAME PLACE AND LEFT NO FILE, WHICH IS THE USER'S OWN
      RE-SPLIT TRIGGER.** (e) IS that re-split; a third full-length retry of the 47(i)-route-1 script under a new
      name is forbidden. Handles 30,965 ??30,687 (own pre-batch restart) ??60,292; refs 33/33/0 live; ORIGINAL
      `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged before and after both
      runs; no recipe, no op VI, no VI run (34(f)), no GUI, no motor/ASI/camera.
    - (j) ?럦 **(e) RAN AND S3a's BOOLEAN HALF IS DELIVERED ??36 pass / 0 fail, THREE FILES, `Is Broken?` FALSE.**
      `tools/bench/diag_s58_boolwire.{py,log,json}`, `BGRUN END rc=0 after 306s`. The named fix of (d) is CONFIRMED
      by measurement: `delete_object(target,'Wire',1664,verify=True)` on uid **#23576** returned `gone [23576]`,
      error `''`, **`[]` pre-existing wire uids removed** ??there is no by-uid form, so the uid was resolved to a
      Traverse index off the live `Wire` census, and `verify=True` proved exactly one wire vanished.
      `remove_bad_wires_scripted` was neither imported nor called (AST-checked). **B1 `ExecState` 1 ??1 ??1 ??1
      (wire delete) ??1 (carrier delete)** ??48(b)'s 0 is gone. Artefacts, all LV2026 `26 00 80 00`, each saved at
      the last point the VI was measured legal: **`claudeDev\D1_s3a_boolcarrier_b1_20260921_010034.vi`** md5
      `7237b2c1e150ebeaf0f32940b07abcfb` 476,241 B (carrier gone, indicator bare at top level) 쨌
      **`??b2_20260921_010034.vi`** md5 `148050141085bc00ffc1e94e9977ea24` 476,245 B (47(e)'s save point ??
      `move_in(#23555 ??#639 @ live 46)` error `''`, `owner_of` `('TopLevelDiagram',536) ??('Diagram',639)`,
      `ExecState` 1 ??1, junk `Invoke` #23490 purged in-run) 쨌 **`??b3_20260921_010034.vi`** md5
      `dc14dd000dfe90c0426b30fa6b69cbc2` 476,169 B (wired). B3: `wire_indicators(Function[102],
      ['x .and. y?'] ??['Automatic Error Handling'], diagram_index=46)` error column **`''`**, indicator wire
      **0 ??10799** (a branch ??whole-VI `Wire` 1905 ??1905, delta 0), `ExecState` **1 ??1**, `#10686` **3/3 wired
      before and after**, `#637` **59 ??59 / 48 ??48, increase 0, no tunnel, no border object** (37(e)), and the
      ordered second pass (42(b), `wire_delta` 0, op error `''`) read **`Is Broken?` = False on wire 10799**.
      Verification level **STRUCTURAL**, never functional ??no VI was run (34(f)). **So both legs of S3a now exist,
      each in its own file, built by the same verbs: numeric (cycle 57) and Boolean (here). What does NOT yet
      exist is ONE file carrying BOTH**, which is the recipe `tools/recipes/stage_d1_s3a_focus_ind.py`.
    - (k) ?좑툘 **THE HYPOTHESIS REVIEW `guard_peer` FORCED IS ARCHIVED AND DISPOSED, AND ITS LOAD-BEARING OBJECTION
      WAS OVERTAKEN BY THE MACHINE.** `archive/peer/2026-09-21-c58-boolwire-dangling.md` (claude/hypothesis opus
      max + web, ANSWERED 588 s, `$4.3192`) returned *"REFUTED in its load-bearing sentence ??the run never measured
      that the indicator is 'left sourced by a wire whose node is gone', and the only post-delete reading of that
      terminal in the whole log says it is bare."* **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)); nothing in it
      was acted on**, and the script was written in full before the dispatch and unchanged after. Its 짠0 documentation
      correction IS adopted ??that is (b)'s qualifier above, and it is adopted because it is a fact about our own
      text, not a claim about the machine. Whether the rest of it should be adopted is **left open**: the run it
      criticised passed 36/0 and delivered three files, so nothing in it is load-bearing for the next act.
    - (l) ?좑툘 **A HOUSE-STYLE HABIT SILENTLY BREAKS A GATE, AND IT COST THIS CYCLE A ROUND-TRIP.** STATUS.md writes
      approximate times as `23:5x` / `01:5x`, and the two `docs/violation-decisions.md` blocks that answer
      `guard_cycle`'s threshold refusal were first written with that spelling. `tools/violations.py:94`'s `DEC_RE`
      requires `(?:[ T]+(\d{2}:\d{2}))?`, so the literal `x` makes the optional time group fail and the block is
      read as **date-only**; `:116` then requires a date-only decision to fall on a strictly LATER day than the
      retrospective that raised the slug, and `archive/peer/2026-09-21-retrospective-cycle57.md` is the same day.
      Both blocks were therefore on disk, correct and unread. **Rule: a `docs/violation-decisions.md` heading
      carries a REAL `HH:MM`, never the `5x` approximation** ??the time is what discharges a same-day slug
      (`:115`). Fixed to the files' true write time `01:24`; no date was rolled, no gate patched,
      `CYCLE_GUARD_OFF` never set.
    - (m) ?뵶 **A REVIEW THAT CANNOT CHANGE THE BUILD IT GATES IS A RECEIPT, NOT A REVIEW ??AND CYCLE 58 REPEATED
      CYCLE 57'S VERSION OF THIS.** `archive/peer/2026-09-21-retrospective-cycle57.md` finding 5(a) caught it in
      cycle 57: `diag_s57_ctmove_wire.py` was written and AST-checked *before* the ctowner review that gated it was
      dispatched, and "was NOT changed afterwards", so $3.8922 and 546 s bought a review structurally unable to
      affect anything. Cycle 58 did the same with `diag_s58_boolwire.py` and `c58-boolwire-dangling` ($4.3192).
      **MANDATORY in every brief from now on: a review that GATES a build is dispatched BEFORE the script is
      written, or the brief says in writing that the script will be revised on the review's findings.** This is a
      brief sentence, not a device ??the standing order of 2026-09-18 08:53 forbids the latter, not the former.
    - (n) ?좑툘 **THE GATE CHAIN COST THIS CYCLE FOUR DRY RUNS AND AN $8.03 REVIEW, AND THE ORDERING IS THE FINDING.**
      `guard_cycle` refuses in sequence ??`stop_record` ??`violations --due` ??`outcome_review --due` ??
      `premature_build()` ??the retrospective gate ??and each refusal is visible only after the one before it is
      cleared, so a single launch was refused four times for four unrelated reasons (a stop record keyed to bytes
      that did not exist; two slugs at threshold; a heading written `01:5x` where `tools/violations.py:94` needs
      `\d{2}:\d{2}`; no prior-art review newer than the recipe). **Every refusal was answered on its own terms ??
      no date rolled, no gate patched, `CYCLE_GUARD_OFF` never set** ??and each answer was real work, not
      paperwork: the recipe got written, two threshold slugs got substantive decisions, three stale doc lines got
      repaired. The last refusal is the structural one: **the retrospective gate compares the newest BUILD LOG
      against the newest RETROSPECTIVE, so once a cycle has run any build log it cannot launch a recipe in that
      same cycle.** That is why S3a's combined build is cycle 59's first act and not cycle 58's last: clearing it
      mid-cycle would have meant running the retrospective early, which is the exact trap OPEN 54(a) documents and
      which cost cycle 29 its entire cycle.

## Pre-decided ??ADDED 2026-09-21 (cycle 59): S3a IS DELIVERED as one file 쨌 S3b's transport DOES NOT EXIST and is built

49. **S3a IS ACCEPTED AND CLOSED, AND THE NEXT STAGE'S TRANSPORT WAS MEASURED TO BE ABSENT FROM THE WHOLE FLEET.**
    Judgement, cycle 59, 2026-09-21, from `tools/bench/cycle59_s3a_recipe.log` (`BGRUN END rc=0 after 596s`, **64
    gates pass / 0 fail**), a files-only verb census, and `archive/peer/2026-09-21-s3b-local-variable-route.md`.
    34??8 stand; this closes S3a and re-cuts S3b before any of it is built.
    - (a) ?럦 **S3a IS DELIVERED AS ONE FILE, AT THE STRUCTURAL LEVEL, AND THE RECIPE WAS NOT TOUCHED TO GET THERE.**
      `claudeDev\D1_s3a_focus_ind.vi`, md5 **`eef91c1d91f16b034707e4d1285ca8cb`**, 476,172 B, LV2026 `26 00 80 00`
      (`tools/bench/cycle59_s3a_recipe.log:322`). `ExecState` **1** at the B3 save (`:304`) **and 1 on the Z0 COLD
      reopen in a freshly restarted LabVIEW** (`:324`); **BOTH** ControlTerminals read `owner_of` `('Diagram',639)`
      on that cold reopen ??numeric #23541 `'index'`, Boolean #23576 `'Automatic Error Handling'` (`:328`); census
      **116** (`:333`), i.e. 114 at the S2 baseline +1 per leg, which is the number the prior-art review said
      nothing on disk had produced; both ORDERED `Is Broken?` readings **False** ??wire 10990 (`:147`) and wire
      10799 (`:311`). Six sub-step artefacts on disk, each saved at the last point the VI was measured legal
      (`:347`). Refs **60 opened / 60 closed / 0 live** (`:344`); all three originals byte-unchanged before AND
      after (`:340`). `tools/recipes/stage_d1_s3a_focus_ind.py` sha256 identical before and after ??
      `1986626FB6F16CD0??, the bytes the prior-art review saw, so the stop record still matches. No hook refused
      the launch, `CYCLE_GUARD_OFF` was never set, no gate was patched. **DECISION: S3a is CLOSED. Verification is
      STRUCTURAL and is never called functional ??no VI was run (34(f)).**
    - (b) ?뵶 **THE S3b TRANSPORT DOES NOT EXIST TODAY ??MEASURED, NOT INFERRED, AND 45(f)'s ROUTE IS CLOSED AS
      WRITTEN.** `local` occurs **once** in `tools/gscript.py`, in a comment (`:830`): **no verb creates a Local
      Variable.** The only vehicle for `Control ??Create:Local Variable` **6331C02** is `build_invoke`
      (`tools/gscript.py:2159`), whose `reference` input is **deliberately left UNWIRED** (`:2164-2166`: a wired
      reference makes the erdosmiller creator write the object's bare class name and fail silently). No `Op*.vi`
      in `claudeDev` (108 files) carries `Local` in its name, and `vi.lib\Erdos Miller\LV-Scripting\Create*.vi`
      is **50 files, none a local-variable creator**. `Local` is grep-absent from `docs/vi-server-ids.json`.
      Neither `docs/NAMES.md` nor `docs/toolkit-capabilities.md` records a creator in any state; the only rows are
      readers and the unverified wiki pair at `docs/NAMES.md:260`.
    - (c) ?좑툘 **AND THE METHOD'S OWN SHAPE IS WHY `build_invoke` CANNOT BE THE VEHICLE.** The external fact
      dispatch (`archive/peer/2026-09-21-s3b-local-variable-route.md`, claude/fact fable-low thin +web, ANSWERED
      79 s, `$1.3397`) returns, CITED to labviewwiki, that `Create:Local Variable` **6331C02 takes NO input
      parameters** and returns only a Local refnum ??so **the control instance the method is invoked on IS the
      binding**. Two established halves (a method with no parameters; a wrapper that never wires the reference)
      meet, and they do not meet in a place where anything can be addressed. Its further claims ??that such a
      call returns error 1055, and that `New VI Object` style **2061** + a write to `Local.Control Name`
      **6355400** is the alternative ??are the peer's own flagged INFERENCE, and its negative finding is that
      **no NI reference page exists for 6331C02, style 2061, or 6355400/6355401/6355403 at all**; wiki, LAVA and
      one 2013 forum thread are the only sources anywhere. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b));
      nothing in it is acted on except (d)'s choice of which route is probed FIRST.**
    - (d) **DECISION: S3b GETS ONE NEW OP VI, AND THE AUTHORISATION IS 46(k), NOT A NEW USER DECISION.**
      `docs/cycle27-plan.md:31` is *"no further **process device**"*; `:1697-1705` already settled that this does
      not reach an op VI that places a Local Variable and that such an op *"is simply built"*. Shape, fixed here
      so no material session designs it: **`OpCreateLocal_v0.vi`** ??in: VI ref, the control's owned LABEL, the
      destination diagram, a position; internals: `VI.Panel` ??`Panel.Controls[]` **6348801**
      (`docs/vi-server-ids.json:47`, already the measured route inside `OpFPLabels_v0`) ??per control
      `Control.Label` **6332005** (`docs/vi-server-ids.json:21`) ??`Text.Text` ??match the requested label ??on
      **that live Control reference** Invoke `Create:Local Variable` **6331C02** with no parameters ??read back
      the new object's uid, class and bound name; relocate afterwards only if the readback says it was not born
      on the destination diagram. Out: uid, class, bound label, the error cluster. **It closes every reference it
      opens** ??reference hygiene is a precondition of a staged build, not an afterthought (CLAUDE.md), so the
      op's self-test includes 20 consecutive calls with the handle count flat 짹100. **Why route A first and not
      the `New VI Object` 2061 route:** A is one call on a reference we already know how to obtain ??it reuses
      `OpFPLabels_v0`'s measured `Panel.Controls[]` ??`Control.Label` walk and adds one Invoke ??whereas B needs
      TWO unverified IDs (a style constant from LAVA and a property write the wiki alone documents). B is the
      fallback, and the self-test REPORTS whether 2061 and 6355400 resolve on this machine as a measurement,
      never as a repair attempt. ?좑툘 **AND THE SAME APPLIES TO ROUTE A's OWN PREMISE ??added on the cycle-59
      retrospective's finding 3:** *"6331C02 takes no parameters"* comes from a wiki page that **self-declares
      its parameter table incomplete**, so if the method turns out to take parameters after all, that is a
      **MEASUREMENT L0 RECORDS, not a failure of the sub-step.** L0 is never scored against an assumption the
      sources never supported.
    - (e) **THE DECOMPOSITION ??five sub-steps, five artefacts, five pass criteria, each starting from the
      previous FILE in a FRESH LabVIEW (the user's 2026-09-19 rule).** ?좑툘 **The order INVERTS NEXT's sentence
      order deliberately (see (f)).**
      **S3b-L0** ??build `OpCreateLocal_v0.vi` and self-test it on a **SCRATCH copy, never on
      `D1_s3a_focus_ind.vi`**: create one local bound to a named control, read back uid/class/bound label, 20
      consecutive calls, handles flat 짹100. Pass: the local exists, bound to the label asked for, `ExecState` 1,
      refs 0 live. Artefacts: the op VI + its self-test log.
      **S3b-M1** from `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d??), cold ??create the TWO locals, one per new
      indicator (`'index'`, `'Automatic Error Handling'`), left UNWIRED ??save
      `claudeDev\D1_s3b_m1_locals_<stamp>.vi`. Pass: `Local` census **8 ??10**
      (`docs/toolkit-capabilities.md:284` is the 8), both bound labels read off the machine, `ExecState` 1.
      ?좑툘 **MEASURE, DO NOT ASSUME, whether an unwired Local leaves the VI legal.** If `ExecState` is 0 with the
      locals unwired there is no legal save point here, and M1 folds into M2 (create **and** wire in one step) ??
      that is a fact the sub-step REPORTS; the folding is judgement's call on the next brief, not a branch a
      material session takes.
      **S3b-M2** from M1, cold ??wire the two locals into `#10407` t0/t2 ??save `??m2_fed_<stamp>.vi`. Pass:
      `ExecState` 1, **`Is Broken?` False on both new wires** via the ordered second pass (42(b), after the save),
      `#10407` wired-terminal count **+2**, and `#637` terminal/wired counts **unchanged ??no tunnel, no border
      object** (37(e)). **This is the step that closes the boundary cycle 54 died on.**
      **S3b-M3** from M2, cold ??move the five 1.5 nodes into `#23032`'s body `Diagram #23058`
      (`docs/cycle27-plan.md:1127-1129`; ?좑툘 `:1037`'s `Obtain Queue #23032` is a different object reusing the
      uid), ONE `move_in` per node, junk purged in-run, then re-wire the rows from the MEASURED table
      (`docs/cycle27-plan.md:1182-1188`, whose "sources on `#686` = 0" clause is STRUCK at `:1188`; cycle 54's
      9/9 at `:1283-1290`) ??save `claudeDev\D1_s3b_m3_moved_<stamp>.vi`. Pass: all five `owner_of` = `#23058`
      AND `ExecState` 1.
      **S3b-M4** from M3, cold ??frame-counter edge shift register + `Wait (ms)` 1 ??save
      `claudeDev\D1_s3_loop15.vi`. Pass: `ExecState` 1 preloaded AND on a cold reopen. 38(g) stays banned.
    - (f) **WHY THE LOCALS COME BEFORE THE MOVES ??a judgement call, recorded as one.** NEXT's sentence orders
      S3b as *move the five nodes, re-wire the rows, then feed `#10407` from locals*. Taken literally that puts
      the one step that BREAKS the VI first and the two independently-savable steps last, and cycle 54 already
      ran that order: 5/5 moves, 9/9 rows, **`ExecState` still 0**, no file (`:1283-1290`). Creating and wiring
      the locals first is savable at `ExecState` 1 twice over while the diagram is still in its known-good S3a
      shape, and it means M3 starts from a VI whose `#10407` inputs are ALREADY satisfied ??which is precisely
      the boundary defect cycle 54 diagnosed. A failure in M3 then still leaves two new files and a closed
      boundary instead of nothing.
    - (g) **DECISION: THE TWO INHERITED LABELS STAY, AND NO RENAMER IS BUILT ??but the user is told, because it
      is their panel.** The indicators carry `'index'` and `'Automatic Error Handling'`, the names LabVIEW derived
      from the carriers. **No verb in this fleet can rename a front-panel control or indicator** (measured,
      cycle 58: `set_node_label` writes `Node.Label` on `Diagram[d].Nodes[n]` and a `ControlTerminal` is not in
      `Nodes[]`; every other label path is a reader), so a rename means a SECOND new op against
      `Control.Label` 6332005. It buys nothing structural: a label is cosmetic, it changes no computation
      (rule 1a untouched), and local variables bind by label, so both names WORK ??each is measured
      non-duplicate and newline-free. `'Automatic Error Handling'` on a tracking Boolean is nevertheless
      misleading to a human reading the panel, and renaming two labels by hand in the editor is seconds for the
      user against an op VI plus self-test for us. **Flagged in `## NEXT` as the user's to overturn; if they want
      us to do it, the `Control.Label` writer is a one-cycle build.**
    - (h) ?좑툘 **THE RE-SPLIT TRIGGER FOR M3, STATED IN ADVANCE SO NOBODY HAS TO NOTICE IT.** If M3 ends at
      `ExecState` 0 ??i.e. leaves NO file ??the next cycle's FIRST act is M3's own decomposition, cut
      **node-with-its-rows** (each node moved and its severed rows re-wired before the next node is touched), and
      the tunnel question becomes explicit at that point rather than implicit. A full-length retry of M3 under a
      new file name is FORBIDDEN (the user's 2026-09-19 rule 3; `cycle_runner.py` counts renamed recipes as the
      same recipe).
    - (i) ?좑툘 **48(m) IS SATISFIED BY CONSTRUCTION FOR L0, AND THAT IS THE POINT OF DOING IT THIS CYCLE.** The
      gating research for the op ??the external API fact ??was dispatched and archived BEFORE one line of the op
      exists, so the review cannot be a receipt for a script already written. Cost `$1.3397`. The brief that
      builds L0 must still say in writing that the op will be revised on any review that gates it.

## Pre-decided ??ADDED 2026-09-21 (cycle 60): L0 RAN 쨌 the creator works 쨌 the binding has NO READER, so the reader is built

50. **S3b-L0 IS MEASURED. `OpCreateLocal_v0.vi` CREATES LOCALS RELIABLY; WHAT DOES NOT EXIST IS ANY WAY TO READ
    WHAT A LOCAL IS BOUND TO.** Judgement, cycle 60 (attempt 2), 2026-09-21, from
    `tools/bench/diag_s3b_l0_createlocal.log` (`BGRUN END rc=1 after 106s`, **30 pass / 2 fail**) and
    `archive/peer/2026-09-21-c60-l0-readback-none.md` (claude/hypothesis opus max, ANSWERED 504 s, `$4.3505`,
    disposed in full in its own `## What was done with it`). 34??9 stand; this settles L0 and re-cuts 49(e)'s M1.
    - (a) ?좑툘 **CYCLE 60 ATTEMPT 1 WAS A USAGE-LIMIT NON-RESULT AT THE CYCLE LEVEL, BUT THE L0 RUN INSIDE IT IS A
      RESULT AND IS NOT RE-RUN.** The runner recorded *"usage-limit attempt 1, non-result; sleeping 238 min
      (renewal + 2 min) then RERUNNING this cycle"* (`tools/bench/cycle_runner_main_20260921a.log`, cycle 47 row,
      02:38:44 ??03:03:39). CLAUDE.md's usage-limit rule 3 invalidates a benchmark or build **interrupted
      mid-run**; L0 was not interrupted ??it started 02:51:44 and ended on its own `BGRUN END` line 106 s later
      with a complete gate table, ~10 min before the limit was hit. **DECISION: L0's readings stand as
      measurements and no part of it is repeated.** What the limit cost was the cycle's remaining work and its
      retrospective, nothing else.
    - (b) ?럦 **THE CREATOR HALF OF 49(d) IS DELIVERED AND IS SOUND.** `claudeDev\OpCreateLocal_v0.vi`, md5
      `58275b212dfa040685613e3edbf403f2`, 9,688 B, LV2026 `26 00 80 00`, `ExecState` 1. Invoking
      `Create:Local Variable` **6331C02** on a live front-panel Control reference returned error cluster
      `(False, 0, '')` and a new `Local` (uid 23507, owner `('TopLevelDiagram',536)` ??the normal birthplace,
      `docs/toolkit-capabilities.md:275`). **20 consecutive calls: 20/20 produced one new Local each, 0 errors,
      1.6 s, handle count 51,418 ??51,418 (delta 0), refs 12 opened / 12 closed / 0 live** ??reference hygiene is
      met as a precondition, not an afterthought. The scratch was a copy of `D1_s3a_focus_ind.vi`, was never
      saved, and was deleted in the same run (`exists=False`); all four md5 gates on the originals PASSED before
      AND after. ?좑툘 **AND 49(d)'s RIDER FIRED AS WRITTEN: the node has SIX terminals, not four** ??`i=4`
      `'Create Local'` (sink) and `i=5` `'Create Local'` (source), both left unwired. That is a MEASUREMENT the
      run recorded, never a failure of the sub-step.
    - (c) ?뵶 **THE TWO FAILING GATES ARE AN ABSENT INSTRUMENT, NOT A FAILED BINDING ??AND THAT DISTINCTION IS THE
      WHOLE OF S3b.** `L0_b5` (`bound None`) and `L0_b6` (`None vs 'index'`) were read with `node_labels()`, which
      returns `Node.Label` **6359001** ??the node's OWN label (`tools/gscript.py:588-594`). All **eight** of the
      main VI's pre-existing Locals return the VI's FILE NAME through that path
      (`tools/bench/main_vi_node_labels.json`; the two Globals likewise return `"Global motor pos.vi"`), so it can
      never answer "what is this Local bound to" for any Local, new or old. **DECISION: the fleet's inability to
      read a binding is the blocker, and CLAUDE.md's "when a diagnosis is GUESSED twice, build the READER" applies
      ??so cycle 60's deliverable became the reader**, `claudeDev\OpLocalName_v0.vi`: Traverse `Local` by index ??
      `Local.Control Name` **6355400** ??string + error cluster, donor `OpNodeLabels_v0.vi`, every reference
      closed, validated against those same eight ground-truth Locals before it is believed about a new one.
      Authorisation is **46(k)** (`:1697-1705`) ??Pre-decided 2 forbids a further **process device**, not an op VI.
    - (d) **READING `Control Name` IS NOT "ROUTE B", AND 49(d) NEVER FENCED IT.** 49(d) fences route B as a
      *creation* mechanism ??`New VI Object` style **2061** *plus a write* to `Local.Control Name`. A **read** of
      that property, to verify what route A actually produced, is a different act. Run 1 measured
      `Local.Control Name` **6355400 resolves = True, error `''`** (`tools/bench/diag_s3b_l0_createlocal.log:115`),
      which is what makes the reader buildable today; style **2061** was **not probed at all** because no verb in
      `tools/gscript.py` passes a style number (`:118-119`), so B remains unbuilt and unmeasured on its creation
      half.
    - (e) ?뵶 **49(e)'s M1 FOLDS INTO M2 ??the judgement call 49(e) reserved, made here on the measurement it asked
      for.** 49(e) said in advance: *"MEASURE, DO NOT ASSUME, whether an unwired Local leaves the VI legal ??if
      `ExecState` is 0 there, M1 folds into M2, and that folding is the next judgement session's call."* L0
      measured it on this very VI lineage: the scratch copy of `D1_s3a_focus_ind.vi` read `ExecState` **1 before
      the call and 0 after it**, with one Local created and unwired. **DECISION: S3b-M1 and S3b-M2 become ONE
      sub-step ??create BOTH locals (`'index'`, `'Automatic Error Handling'`) AND wire them into `#10407` t0/t2
      before the save.** Pass criteria are 49(e)'s M2 criteria plus `Local` census **8 ??10**: `ExecState` 1 at the
      save, `Is Broken?` **False** on both new wires via the ordered second pass (42(b), after the save), `#10407`
      wired-terminal count **+2**, `#637` terminal/wired counts **unchanged ??no tunnel, no border object**
      (37(e)). ?좑툘 **This does NOT weaken the user's 2026-09-19 rule**: the folded step still ends in a saved file,
      and it is the *first* point on this path where a legal save exists. M3 and M4 are unchanged, and **48(h)'s
      re-split trigger for M3 stands**.
    - (f) ?좑툘 **ONE HALF OF THIS IS NOW SETTLED AND THE OTHER IS NOT.** Until the reader returns a string,
      **nobody may state that the new Local is bound to `'index'`** ??that it must be, because 6331C02 is an
      instance method, is exactly the inference this cycle exists to replace. But the six-terminal question IS
      answered; see (g).
    - (g) ?럦 **THE SIX-TERMINAL QUESTION IS SETTLED BY MEASUREMENT, AND THE WIKI WAS RIGHT: 6331C02 TAKES NO INPUT
      PARAMETERS.** The separator the cycle-60 hypothesis review named was run report-only against Invoke nodes
      this fleet had already built with methods of KNOWN signature
      (`tools/bench/diag_s3b_l0_localname_run2.log:70-78`): `OpMoveIn_v0.vi` #741 ??**12** terminals, pairs
      `(4,5) 'Move'`, `(6,7) 'position'`, `(8,9) 'owner'`, `(10,11) 'duplicate'`; `OpConPaneAssign_v0.vi` #99 ??
      **10** terminals, `(4,5) 'AssignCtrlToTerm'`, `(6,7) 'Control'`, `(8,9) 'TermIdx'`; `OpCreateLocal_v0.vi`
      #306 ??**6** terminals, `(4,5) 'Create Local'` **only**. The pattern is exact and it reads off two known
      signatures: the METHOD row occupies one (sink, source) pair named after the method, and **each parameter
      occupies one further pair**. `Create Local` has the method pair and nothing else. **DECISION: 49(d)'s rider
      is discharged ??the `i=4` sink is layout, not an omitted input, and the wiki's incomplete parameter table
      happened to be right here.** Leaving both terminals unwired was correct, and no future run is scored against
      a missing 6331C02 parameter. (All three op VIs byte-unchanged by the reading.)
    - (h) **DECISION: THE READER IS BUILT WITH A `To More Specific Class` CAST SEEDED TO `Local`, FOLLOWING THE
      DONOR'S OWN MECHANISM ??not a new technique, and not a donor substitution.** Cycle 60's first reader attempt
      measured the block to one cast: `build_property('VI Server:Local', [('6355400', False)])` **RESOLVES** on
      this machine ??error column `''`, Property census 7??, short name **`CtrlName`**, terminal i=4 SOURCE
      (`tools/bench/diag_s3b_l0_localname_run2.log:50-56`), the **first resolution of 6355400 here** ??but wiring
      its `reference` straight from `Traverse for GObjects.vi` ??`Index Array .element` gives `ExecState` **0**
      with the `CtrlName` row intact (no silent class re-adaptation, `:59-64`), because Traverse yields a
      **GObject** and `Local` sits two classes below it. `OpNodeLabels_v0.vi` already carries the answer:
      **`To More Specific Class` #683**, seeded by wire **772, produced by no node on its diagram** (`:29-45`).
      The reader reproduces that seed with target class `Local`. ?좑툘 **The seed's construction is to be READ off the
      donor and reported verbatim ??it has never been measured ??and if it cannot be reproduced for class `Local`
      that is a FACT with an `OPEN:` line, never a donor substitution and never the alternative Invoke-seeded
      variant the review proposed.** Nothing on disk was lost to the first attempt: it saved no VI by design
      (`ExecState` 0, `allow_broken` False, `gui_save` never called), deleted its scratch, and left all four md5
      pins and both donors byte-unchanged.
    - (j) ?뵶 **THE READER STAGE HAS NOW ENDED TWICE WITH NO FILE, SO IT IS RE-SPLIT ??THE TRIGGER IS THE USER'S,
      NOT A FEELING.** Attempt 1 (`tools/bench/diag_s3b_l0_localname_run2.log`) and attempt 2
      (`tools/bench/diag_s3b_l0_localname_v2.log`, `BGRUN END rc=1 after 101s`, 29 pass / **1 fail** ??
      `S2_b10 ExecState == 1 after the indicator`) both ended `ARTEFACTS ON DISK: []`. The user's 2026-09-19 rule
      3: *"the same stage failing twice at the same place, or a stage that ends without a saved artefact ??the
      next cycle's FIRST act is a decomposition plan for that stage ??A full-length retry under a new file name is
      forbidden."* **DECISION: no third full-length build. The decomposition is 51, written here so the next
      session executes instead of planning.** What the two attempts bought is real and is not lost: the property
      resolves, the cast route is built end to end with every error column `''`, and the fault is narrowed to
      three candidates ??but **this cycle saved no VI, and that is its honest cost.**
    - (k) ?럦 **THE SEED MECHANISM IS NOW THE PLAN'S, CITED: `docs/toolkit-capabilities.md:84-93`, the typed-control
      seed, SOLVED 2026-09-14.** A refnum CONTROL created by `Terminal.Create Control` on a property node's
      `reference` input IS the seed for a `To More Specific Class`. It was on disk the whole time and attempt 2
      mis-cited its own file ??the cycle-60 cast-seed review
      (`archive/peer/2026-09-21-c60-cast-seed-execstate0.md`, claude/hypothesis opus max, ANSWERED 643 s,
      `$4.8363`) refuted the diagnosis on exactly that ground, and it was right. It is CONFIRMED LIVE, not just
      cited: on `claudeDev\OpLoopCast_v0.vi`, `ExecState` **1**, the TMSC's `target class` is wire **333**, carried
      by a front-panel **control** `{'label':'reference','uid':297,'is_source':True}` with **0 node producers**
      (`tools/bench/diag_c60_castseed_probe.log:50`). The donor `OpNodeLabels_v0`'s own seed (wire **772**, 0 node
      producers, 0 of 19 `panel_wiring` rows ??`diag_s3b_l0_localname_v2.log:46-69`) is the same shape read
      through an instrument that cannot see it. ?좑툘 **`gscript.loop_cast` (`tools/gscript.py:626`) CANNOT be used
      here** ??it dispatches only to `OpLoopCast_v0/v1` and `OpWhileCast_v0` and raises otherwise;
      `OpLocalCast_v0.vi` does not exist, so the TMSC is hand-built.
    - (l) **WHAT IS MEASURED OUT, so 51 does not re-test it.** The `ExecState` timeline was
      `1 ??0 after build_property ??1 after the seed control ??0 after the birth-wire delete ??0 thereafter`
      (`diag_s3b_l0_localname_v2.log:83-126`). The middle two transitions are the property node's `reference`
      input going unwired ??wired ??unwired, which is ordinary. **Step b7 is EXONERATED by an isolated probe on a
      throwaway donor copy: `ExecState` 1 ??0 (wire 645 deleted) ??**1** again after `create_control` on
      `#235.reference` (`tools/bench/diag_c60_castseed_probe.log:74-80`, 19 pass / 0 fail, 3 s).** So the residual
      0 is one of exactly three things: **wire 1030** (the Local-typed seed into `target class`), **wire
      1085/#1025** (the cast output into the `VI Server:Local` node), or **no structural break at all**.
    - (i) ?좑툘 **AND THE READER IS NOT OPTIONAL BOOKKEEPING ??IT IS A RULE-1a INSTRUMENT.** S3b feeds `#10407`
      t0/t2 from two Local Variables. If the creator's label walk ever matched the wrong control, loop 1.5 would
      be fed from the wrong source with no wire broken and no gate failing ??*"parameters must arrive by the same
      route with the same values"* (CLAUDE.md 1a), and a same-type mis-binding is invisible to `Is Broken?`, which
      checks TYPE. The panel carries many numerics, so type alone does not fence `'index'`. **DECISION: the folded
      M1+M2 step does not run until the binding can be READ, and the readback of both locals' `Control Name` is a
      GATE of that step, not a diagnostic afterthought.**

## Pre-decided ??ADDED 2026-09-21 (cycle 60): the DECOMPOSITION of the binding reader, four steps, four artefacts

51. **THE RE-SPLIT 50(j) TRIGGERS. `OpLocalName_v0` is cut into four sub-steps, each with its own saved file and
    its own pass criterion, to be run one per material dispatch and never chained into one long build.** This is
    the plan the user's 2026-09-19 rule 3 demands; it is **prior-art-reviewed once before L1 executes**, and after
    that a material session may run each step without asking. A full-length retry of the v2 build under any new
    name is FORBIDDEN.
    - (a) **L1 ??READ WHICH CONNECTION IS BROKEN. No build, no save, ~3 minutes of machine time.** On a throwaway
      copy of `OpNodeLabels_v0.vi`, rebuild to the exact point attempt 2 reached (property `CtrlName` ??seed
      control from the `reference` SINK ??birth wire deleted ??seed wired into `target class` ??cast output wired
      into `reference`), then run the **ORDERED second pass** (42(b)) and read **`Is Broken?` on BOTH** the seed
      wire and the cast-output wire, plus `#1025`'s full terminal table. ?좑툘 **Resolve both wires by CONSTRUCTION
      ORDER, never by the literal uids 1030 / 1085** ??they will differ on a fresh build, and reusing a remembered
      number is the mistake `diag_s3b_l0_createlocal.py:608` already made once. The `Is Broken?` read perturbs
      `ExecState` (`docs/NAMES.md:912-918`); that costs nothing here because `ExecState` is already 0 and nothing
      is being saved. **Pass: a True/False reading for BOTH wires.** A `False`/`False` pair is a legitimate and
      informative outcome ??it would mean 50(l)'s third candidate, *no structural break at all*, and the next
      step becomes a save attempt rather than a repair. **Artefact: `tools/bench/diag_c60_l1_whichwire.{log,json}`.**
    - (b) **L2 ??REPAIR THE ONE CONNECTION L1 NAMES, AND SAVE.** Build the same chain with that one connection
      made differently, and **save `claudeDev\OpLocalName_v0.vi` at `ExecState` 1**. **Pass: `ExecState` 1 at the
      save AND on a COLD reopen in a freshly restarted LabVIEW.** **Artefact: the op VI + its md5.** If `ExecState`
      is still 0 here, STOP ??do not try a third construction; report which connection was changed and what the
      reading was, and let judgement cut again (50(j) applies to this step in its own right).
    - (c) **L3 ??VALIDATE THE INSTRUMENT AGAINST GROUND TRUTH BEFORE ANYONE BELIEVES IT.** On a **SCRATCH copy**
      of `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d??), never the artefact, read `Control Name` for **every**
      pre-existing `Local` (census 8, `docs/toolkit-capabilities.md:284`) and report **every uid ??string pair
      verbatim**. **Pass: at least one non-empty string that is NOT a `.vi` file name** ??that is the whole point,
      since `node_labels` returns the file name for all eight (50(c)). **Artefact: the readings JSON.** A run of
      eight `.vi` file names or eight empty strings means 6355400 is not the binding either, which is a result and
      must be reported as one.
    - (d) **L4 ??ANSWER THE QUESTION THE WHOLE CYCLE WAS FOR.** On the same scratch, create a Local with
      `OpCreateLocal_v0.vi` from the front-panel control whose owned label reads `'index'` (**read the label off
      the machine, never retype it**), then read its `Control Name`. Report the string verbatim, the error
      cluster, `Local` census 8 ??9, and `ExecState` before and after. Then 20 consecutive reader calls, **handles
      flat 짹100, refs opened == closed, 0 live**, scratch deleted with `exists=False`. **Pass: a string is
      returned and the hygiene numbers hold** ??whatever the string SAYS is the measurement, and a name other than
      `'index'` is a finding, not a failure.
    - (e) **THEN, AND ONLY THEN, S3b's FOLDED M1+M2 (50(e)) RUNS, WITH THE READBACK AS A GATE (50(i)).** If L3 or
      L4 shows that the binding cannot be read at all, the folded step does **not** silently proceed on type
      checking alone ??that is a rule-1a call and it returns to judgement.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
?럦 **D0 IS DELIVERED** (cycle 31) 쨌 **N1 IS ACCEPTED** (cycle 34) 쨌 **D1 STAGE S1 IS DELIVERED** (cycle 48 ??`claudeDev\D1_s1_copy.vi`, md5 `3e3d23ce??, 20/0) 쨌 **D1 STAGE S2 IS DELIVERED** (cycle 51, ACCEPTED cycle 52 ??`claudeDev\D1_s2_loops.vi`, md5 `6ff19497??, COLD/PRELOADED ExecState 1) 쨌 ?럦 **S3a's NUMERIC HALF IS DELIVERED (cycle 57 ??`claudeDev\D1_s3a_num_ind_20260920_234341.vi`, md5 `fceaa0a1??: an indicator on `Diagram #639` wired to `#10757` t1 `'element'`, `ExecState` 1, `Is Broken?` False; the placed-only artefact `D1_s3a_ind_placed_?? md5 `0b9a0702?? reopens COLD at `ExecState` 1. Only the BOOLEAN carrier is left ??Pre-decided 47(i))** 쨌 ?럦 **AND THE BOOLEAN HALF IS NOW BUILT TOO (cycle 58 material #2, 36 pass / 0 fail, Pre-decided 48(e)'s three saved sub-steps: `claudeDev\D1_s3a_boolcarrier_b1_20260921_010034.vi` md5 `7237b2c1?? 쨌 `??b2_?? md5 `14805014?? ??47(e)'s pre-wiring save point 쨌 `??b3_?? md5 `dc14dd00??, the indicator on `Diagram #639` wired to `#10686` t0 `'x .and. y?'` wire 10799, `ExecState` 1 throughout and **`Is Broken?` = False**. The fix was deleting the wire `create_indicator` makes on a SOURCE terminal BY UID before deleting the carrier; `remove_bad_wires_scripted` stayed REFUSED)** **??S3 AS 37(g) DEFINED IT IS WITHDRAWN (cycle 53), AND CYCLE 54 MEASURED WHY: the move-and-rewire MACHINERY WORKS (5/5 moves, 9/9 rows, `ExecState` still 0) ??the fault is the STAGE BOUNDARY, so S3-as-loop-1.5-alone is CLOSED and `queue_node('obtain')` is a SHAPE test, not a type test. **CYCLE 55 THEN VALIDATED THE TYPE CHECKER ??`Is Broken?` reads False on a matched and True on a mismatched connection, but ONLY on a second ordered pass ??the runner was STOPPED on the 5th outcome review and the user answered CONTINUE (Pre-decided 45). **CYCLE 56 THEN MEASURED THE TRANSPORT: a free-standing panel indicator CAN be created by scripting on this VI ??saved artefact `claudeDev\DIAG_s56_t3_p2_20260920_221901.vi` ??wiring it to a source on a NESTED diagram is the one open verb, and 45(c)'s third indicator is WITHDRAWN. Read `docs/cycle27-plan.md` Pre-decided 46 first, then 42 + 43 + 44.** Banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
?넅 **USER RULE 17:5x = `docs/cycle27-plan.md` Pre-decided 9 ??EVERY GUI action is capture ??locate ??act ??capture ??confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.

## START HERE
1. **Cycle plan = `docs/cycle27-plan.md`** (cycle20/21 plans `superseded`; motor plan `docs/motor-limit-assurance-plan.md` **짠A.1 + "P2 live findings"**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`. ?넅 **2026-09-18 (user, TRIAL): codex's roles ??claude roles** ??failed prediction = `-Agent claude -Role hypothesis` SINGLE arm (`-Dual` only for a second opinion on our own tools); `-Kind fact`/`-Kind prose` with no `-Agent` ??fable/low thin; `outcome_review.py` ??fable/medium thin. Check routing free with `-DryRun`.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌 `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**. ?좑툘 `BUILD_RE` also fires on a plain `cp a.py tools/recipes/b.py` ??quote both paths (cycle23-close 짠3).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released   # ??**RELEASED 2026-09-21 08:1x ??cycle 60 (ATTEMPT 2) material #2. TWO DIAGNOSTICS under `tools/bench/`, no recipe (48(n)), `tools/recipes/` **158 files before and after, diff `[]`**. RUN 1 `tools/bench/diag_s3b_l0_localname_v2.{py,log,json}` (1,403 lines, 46 gate sites, AST OK `tools/bench/c60c_astcheck.log` 10/10) ??**`BGRUN END rc=1 after 101s`, 29 pass / 1 fail**, the one FAIL being the op's own pass criterion `S2_b10 ExecState == 1` ??**0**. ?뵶 **S1 ANSWERED THE SEED QUESTION AND THE ANSWER IS THAT THIS FLEET CANNOT SEE THE DONOR'S SEED AT ALL:** TMSC **#683** (found by its terminal names, never by uid) takes `target class` from **wire 772**, produced by **0 nodes** on that diagram AND carried by **0 of the 19 front-panel rows** `panel_wiring` returns (every row printed verbatim, `:46-69`); the Wire object's own row is `{'i': 25, 'uid': 772, 'class': 'Wire', 'owner': 'TopLevelDiagram', 'pos': (617, 250)}`, `Constant` census **7**, `ControlTerminal` **19**. The existing cast verb was checked **against the file, not the peer's word**: `gscript.loop_cast` `:626` exists, dispatches only to `OpLoopCast_v0/v1` + `OpWhileCast_v0` (all three on disk) and **raises for any other class ??`OpLocalCast_v0.vi` does not exist**, so it cannot read a `Local`. **S2 built the cast route anyway, every step verified BY EFFECT:** `build_property('VI Server:Local',[('6355400',False)])` ??#1025, error `''`, `CtrlName` i=4 SOURCE 쨌 `create_control` on its `reference` SINK ??the Local-TYPED seed **#1076 labelled `'reference'`**, ControlTerminal 19??0, **ExecState still 1** 쨌 its birth wire 1086 deleted by uid (`gone [1086]`, no collateral) 쨌 TMSC's old seed wire **772 deleted** (`gone [772]`, no collateral) 쨌 `wire_control(['reference'] ??Function[0].'target class')` error `''`, row afterwards `wire 1030` 쨌 the cast output wire **645 fed exactly ONE sink** (#235 `reference`), deleted, and that sink given its own control **#1083 `'reference 2'`** 쨌 `wire Function[0].'specific class reference' ??Property[0].'reference'` error `''`, row afterwards `wire 1085`, and **the `CtrlName` row SURVIVED** (the false-pass separator) 쨌 `create_indicator` ??**#1102, ONE new panel label `'Control Name'` read off the machine**. **ExecState timeline: 1 ??0 after `build_property` ??1 after the seed control ??0 after the birth-wire delete ??0 through everything after.** ?좑툘 **THE OP WAS THEREFORE NOT SAVED, the unsaved copy was REMOVED, nothing was repaired** (`remove_bad_wires_scripted`/`remove_bad_wires`/`gui_save` neither imported nor called, `allow_broken` never True), **no donor switched, no Invoke-seeded variant built, no third route invented** ??the brief's instruction for exactly this reading. **ARTEFACTS ON DISK: []**; S3/S4/S5 NOT attempted (no reader to validate). ?좑툘 **THE FORCED HYPOTHESIS REVIEW IS ARCHIVED AND DISPOSED IN FULL: `archive/peer/2026-09-21-c60-cast-seed-execstate0.md`** (claude/hypothesis **opus effort max + web**, `OUTCOME: ANSWERED (643s)`, **`COST: $4.8363`** in 26 / out 49,081 / cache-create 264,904 / cache-read 1,799,250, 23 turns; log `tools/bench/peer_c60_castseed.log`, `BGRUN END rc=0 after 643s`). Verdict: **REFUTED on its conclusion** ??`docs/toolkit-capabilities.md:84-93` heads that section *"### ~~The one missing seed~~ SOLVED 2026-09-14 ??the typed-control seed (INDEX row 28)"* and says a refnum CONTROL made by `Terminal.Create Control` on a property node's `reference` input IS the seed, i.e. this session **mis-cited its own file**; it also notes the 0 first appears at **b1**, not b4. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)).** ?럦 **ITS TWO NAMED MEASUREMENTS WERE RUN ??the discriminating test the devil's-advocate rule requires ??as `tools/bench/diag_c60_castseed_probe.{py,log,json}` (AST OK `tools/bench/c60d_astcheck.log`), `BGRUN END rc=0 after 3s`, **19 pass / 0 fail**, building nothing and saving nothing: (1) `claudeDev\OpLoopCast_v0.vi` reads `ExecState` **1** and its TMSC's `target class` **wire 333 IS carried by a FRONT-PANEL CONTROL** ??`{'label': 'reference', 'indicator': False, 'uid': 297, 'is_source': True, 'wire': 333}` with 0 node producers (`:50`) ??so a typed CONTROL demonstrably seeds a working TMSC in this fleet, on the machine; (2) **b7 IS EXONERATED**: on a throwaway copy of the donor, `ExecState` **1 ??0** (cast output wire 645 deleted by uid, `gone [645]`, no collateral) **??1** (`create_control` on the orphaned `#235.reference` ??#1039 `'reference'`), `:74-80`. The review's 짠4 second step (b5+b6 alone) and its 짠3 falsifier 3 (ordered `Is Broken?` on wires 1030/1085) were **NOT run** ??taking a review's conditional next step is accepting the review, which is judgement's. **FOUR md5 GATES PASS BEFORE AND AFTER BOTH RUNS** (ORIGINAL `2a78e17c??, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497??, `D1_s3a_focus_ind` `eef91c1d??), donors `OpNodeLabels_v0` `376ff125??, `OpCreateLocal_v0` `58275b21?? and `OpLoopCast_v0` byte-unchanged, both scratches `exists=False`. Handles 34,016 ??30,7xx (own pre-batch restart, 44(e)) ??30,781; refs **12 opened / 12 closed / 0 live**. No VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰), no new process device, no recipe, no new gscript verb, no new op VI on disk. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). **No route chosen or recommended; `docs/cycle27-plan.md` and `## NEXT` untouched.** LabVIEW left UP at pid 24388. The acquire note, verbatim: ?뵏 **ACQUIRED 2026-09-21 08:0x ??cycle 60 (ATTEMPT 2) material #2. ONE DIAGNOSTIC under `tools/bench/`, never a recipe (48(n)): `tools/bench/diag_s3b_l0_localname_v2.{py,log,json}`. It executes the judgement decision of cycle 60 ??**build `claudeDev\OpLocalName_v0.vi` WITH A `To More Specific Class` CAST TO `Local`, following the DONOR'S OWN measured seed mechanism**, authorisation **46(k)** (`docs/cycle27-plan.md:1697-1705`, quoted verbatim in the script header: Pre-decided 2 forbids a further **process device**, not an op VI) and **49(i) stated in writing (the op will be revised on any review that gates it)**. **S1** MEASURES the seed off the machine first (which object carries TMSC #683's `target class` wire, its class, diagram, whether Constant / ControlTerminal / tunnel, what it holds; plus whether `tools/gscript.py` already has a verb ??`loop_cast` `:626` is verified by file, not by the peer's name). **S2** builds: `build_property('VI Server:Local',[('6355400',False)])` ??`create_control` on its `reference` SINK = the Local-TYPED seed ??re-seed TMSC `target class` ??TMSC `specific class reference` ??the property's `reference` ??`create_indicator` on `CtrlName` ??save at `ExecState` 1. **If the seed mechanism cannot be reproduced for class `Local`, that is a FACT reported with an `OPEN:` line ??NO donor switch, NO Invoke-seeded variant, NO third route.** **S3** validates against ground truth on `claudeDev\SCRATCH_LN2_<stamp>.vi` (a duplicate of `D1_s3a_focus_ind.vi` md5 `eef91c1d??, never the artefact itself, 49(e), deleted in the same run): `Control Name` for EVERY pre-existing `Local`, uid ??string verbatim. **S4** creates a Local from the `'index'` control via `OpCreateLocal_v0.vi` and reads it back. **S5** 20 consecutive calls, handles 짹100, refs 0 live. Four md5 gates before AND after (ORIGINAL `2a78e17c?? FATAL, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497?? FATAL, `D1_s3a_focus_ind` `eef91c1d?? FATAL) plus both donors byte-unchanged. Static gate `tools/bench/c60c_astcheck.{py,log}` (the predecessor's 8 checks kept). Own pre-batch restart (44(e); LabVIEW was up at pid 8284). Command: `py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_s3b_l0_localname_v2.log -- py -u tools/bench/diag_s3b_l0_localname_v2.py`; turn held open to the `BGRUN END` line (OPEN 54(b)). No VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰), no new process device, no recipe, no new gscript verb. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). No route chosen or recommended; `docs/cycle27-plan.md` and `## NEXT` untouched.**
  owner_c60m1_attempt2: # ??**RELEASED 2026-09-21 07:3x ??cycle 60 (ATTEMPT 2) material #1. TWO RUNS of ONE DIAGNOSTIC, `tools/bench/diag_s3b_l0_localname.{py,json}` (1,156 lines, 42 gate sites, AST OK `tools/bench/c60b_astcheck{,2}.log` `BGRUN END rc=0 after 0s`).** Run 1 `tools/bench/diag_s3b_l0_localname.log` **`BGRUN END rc=1 after 112s`, 17 pass / 1 fail** ??the one FAIL was MY OWN GATE (`R0_a3 exactly ONE IndexArray`, copied from attempt 1's donor `OpFPLabels_v0`, which has one; the donor of record `OpNodeLabels_v0.vi` has **THREE**, and that is the DOCUMENTED shape, `tools/recipes/build_opnodelabels_v0.py:11-12`). Run 2 `tools/bench/diag_s3b_l0_localname_run2.log` **`BGRUN END rc=0 after 81s`, GATES 24 pass / 0 fail**, with the selector derived from the wiring (`Traverse for GObjects.vi` #124 `References` **wire 600** ??the IndexArray whose `array` carries wire 600 = **#308**; the other two are `array` 884 and 485). ?뵶 **THE ANSWER IS MEASURED AND IT IS NEGATIVE: THE DONOR OF RECORD CANNOT CARRY A ONE-PROPERTY READ ON A TRAVERSE-SELECTED OBJECT.** In order, all off the machine: **`build_property('VI Server:Local', [('6355400', False)])` RESOLVES** ??error column **`''`**, Property census 7 ??8, new #1025, and the SHORT NAME of `Local.Control Name` 6355400 on this machine is **`CtrlName`** (terminal i=4, SOURCE) ??the first time that ID has been resolved here. `IA #308 .element` ??`PN #1025 .reference` **LANDED**: error column `''`, Wire census **30 ??30** (a BRANCH), the `reference` terminal carrying **wire 605** afterwards. The `CtrlName` row **SURVIVED** the wire (so LabVIEW did **not** silently re-adapt the node's class ??the false-pass case the peer review named). **AND `ExecState` READ 0.** The op was therefore **NOT SAVED**, the unsaved copy was **REMOVED**, nothing was repaired (`remove_bad_wires_scripted`/`remove_bad_wires`/`gui_save` neither imported nor called, `allow_broken` never True), **no other donor was substituted and no different op was designed** ??the brief's instruction for exactly this reading. **ARTEFACTS ON DISK: []** ??`claudeDev\OpLocalName_v0.vi` does NOT exist. R1/R2/R3 were NOT attempted (no reader to validate). ?좑툘 **REPORT ONLY, no conclusion drawn:** the donor's `To More Specific Class` #683 takes its `target class` from **wire 772, which NO node on that diagram produces** (a panel object or a constant), i.e. the cast's type is seeded, not computed. ??**R4 DELIVERED (report only, no build), the three Invoke tables side by side:** `OpMoveIn_v0.vi` #741 at Nodes[13] ??**12 terminals**, the method's parameters appearing as SINK/SOURCE PAIRS: (4,5) `Move`, (6,7) `position`, (8,9) `owner`, (10,11) `duplicate`; `OpConPaneAssign_v0.vi` #99 at Nodes[7] ??**10 terminals**, (4,5) `AssignCtrlToTerm`, (6,7) `Control`, (8,9) `TermIdx`; `OpCreateLocal_v0.vi` #306 at Nodes[8] ??**6 terminals**, (4,5) `Create Local` and nothing else. All three read byte-unchanged. ?좑툘 **`guard_peer` FORCED a hypothesis review of run 1's FAIL before run 2 could launch: `archive/peer/2026-09-21-c60-ia-count-gate.md`** (claude/hypothesis **opus effort max + web**, `OUTCOME: ANSWERED (449s)`, **`COST: $3.5990`** in 16 / out 34,202 / cache-create 227,460 / cache-read 808,101, 14 turns; log `tools/bench/peer_c60_ia_count.log`, `BGRUN END rc=0 after 449s`). Verdict: the selector repair is conceded as unique and correct, but *"it repairs the thermometer"* ??the structural blocker is that `Traverse for GObjects.vi` yields a **generic GObject** and `Local` sits two classes below it (Generic ??GObject ??Node ??Local), so a TMSC is required. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)); its `## What was done with it` is written IN FULL.** Acted on: **one free READING only** ??its 짠4 reading 2, asserting the `CtrlName` row survived the wire (gate `R0_a7b`), data the run already captured. **NOT acted on:** its 짠2 donor substitution, its 짠1/짠4 constructive route (seed a TMSC with a Local-typed reference in the `loop_cast` pattern, candidate seed `OpCreateLocal_v0.vi`'s Invoke terminal i=5 `Create Local` SOURCE) ??**not built, not prototyped, not probed** ??and its third reading (`Wire.Is Broken?` 6371004 on the new wire), which on this fleet needs an ORDERED `Terminal.Connect Wire` inside the op, i.e. new construction. Handles 34,281 ??30,704 (own pre-batch restart, 44(e)) ??34,331; refs **5 opened / 5 closed / 0 live**. **FOUR md5 GATES PASS BEFORE AND AFTER BOTH RUNS** (ORIGINAL `2a78e17c??, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497??, `D1_s3a_focus_ind` `eef91c1d??), donor `OpNodeLabels_v0.vi` `376ff125?? and `OpCreateLocal_v0.vi` `58275b21?? byte-unchanged, scratch `exists=False`, nothing written under `tools/recipes/`. No VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰), no new process device, no recipe, no new gscript verb. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). **No route chosen or recommended; `docs/cycle27-plan.md` and `## NEXT` untouched.** LabVIEW left UP at pid 23444. The acquire note, verbatim: ?뵏 **ACQUIRED 2026-09-21 03:2x ??cycle 60 (ATTEMPT 2) material #1. ONE DIAGNOSTIC under `tools/bench/`, never a recipe (48(n)): `tools/bench/diag_s3b_l0_localname.{py,log,json}`. It BUILDS `claudeDev\OpLocalName_v0.vi` ??the ONE-PROPERTY READER for a Local Variable's binding: copy the DONOR OF RECORD `claudeDev\OpNodeLabels_v0.vi` (Traverse class by index ??property ??string indicator), add ONE `build_property('VI Server:Local', [('6355400', False)])` = `Local.Control Name`, BRANCH the donor's existing `IndexArray.element` (the Traverse-selected object) into its `reference`, `create_indicator` on the property's output terminal, save at `ExecState` 1. Authorisation **46(k)** (`docs/cycle27-plan.md:1697-1705`, quoted verbatim in the script: a **process device** is forbidden, an **op VI** is not); reading 6355400 is NOT route B (route B is `New VI Object` style 2061 **plus a write**), so 49(d) does not fence it. **49(i) stated in writing in the script: THIS OP WILL BE REVISED ON ANY REVIEW THAT GATES IT.** ?좑툘 **KNOWN HAZARD WRITTEN DOWN BEFORE THE RUN:** the erdosmiller Traverse returns GENERIC GObject references and this fleet's established way to read a class-specific property off one is `To More Specific Class` seeded by a TYPED wire (`tools/gscript.py:626-635`, `:946`), while `tools/gscript.py:2415` says *"Type mismatches make a broken wire"* ??so `element ??reference` may land and still leave `ExecState` 0. **That reading IS the measurement: if the donor's measured shape does not support a one-property read on a Traverse-selected object, the run REPORTS it, leaves the copy unsaved and removes it ??no other donor is substituted, no different op is designed, nothing is repaired.** Then it measures on `claudeDev\SCRATCH_LN_<stamp>.vi`, a duplicate of `D1_s3a_focus_ind.vi` (md5 `eef91c1d??, gated BEFORE and AFTER ??never the artefact itself, 49(e)), deleted in the same run: **R1** `Control Name` for ALL pre-existing `Local`s (uid ??string verbatim; plainly whether any string is a `.vi` file name) 쨌 **R2** create a Local from the panel control whose owned label reads `'index'` (label taken from `fp_labels`' own bytes, hex recorded) via `OpCreateLocal_v0.vi`, then read it back with the NEW reader; census + ExecState before/after 쨌 **R3** 20 consecutive reader calls, handles 짹100, refs 0 live 쨌 **R4 REPORT ONLY, no build**: the full Invoke terminal tables of `OpMoveIn_v0.vi` / `OpConPaneAssign_v0.vi` beside `OpCreateLocal_v0.vi`'s 6331C02 node (i=4 sink / i=5 source, both `'Create Local'`), **no conclusion drawn**. Four md5 gates before AND after (ORIGINAL `2a78e17c?? FATAL, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497?? FATAL, `D1_s3a_focus_ind` `eef91c1d?? FATAL) plus the donor and `OpCreateLocal_v0` byte-unchanged. `move_in` NOT called at all; every diagram index resolved from the machine (`diag_index` by uid / the op's own top-level read back), never hard-coded; every owner comparison accepts BOTH `'Diagram'` and `'TopLevelDiagram'` (attempt 1's defect at `diag_s3b_l0_createlocal.py:608`, machine-checked absent by AST gate 8). AST OK: `tools/bench/c60b_astcheck.{py,log}` ??every `g.<verb>` already a `def` in `tools/gscript.py`, **NO new verb**; `remove_bad_wires_scripted`/`remove_bad_wires`/`gui_save` neither imported nor called, `allow_broken=True` never passed. Own pre-batch restart (44(e); LabVIEW was up at pid 8292). Command: `py tools/bgrun.py --material --max-min 35 --log tools/bench/diag_s3b_l0_localname.log -- py -u tools/bench/diag_s3b_l0_localname.py`; turn held open to the `BGRUN END` line (OPEN 54(b)). No VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰), no new process device, no recipe. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). No route chosen or recommended, `docs/cycle27-plan.md` and `## NEXT` untouched.** The previous key's released note: ??**RELEASED 2026-09-21 03:1x ??cycle 60 ATTEMPT 1 material #1** (the run the usage limit cut short at 03:03). ONE run, `py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_s3b_l0_createlocal.log -- py -u tools/bench/diag_s3b_l0_createlocal.py` ??**`BGRUN END rc=1 after 106s`**, **30 pass / 2 fail** (`L0_b5 bound None`, `L0_b6 None vs 'index'`). ?럦 **`claudeDev\OpCreateLocal_v0.vi` IS BUILT AND WORKS AS A CREATOR ??md5 `58275b212dfa040685613e3edbf403f2`, 9,688 B, LV2026 `26 00 80 00`**: `build_invoke('VI Server:Control','6331C02')` ??Invoke #306 with SIX terminals (`reference` sink / `reference out` source / `error in (no error)` / `error out` / **i=4 `'Create Local'` sink / i=5 `'Create Local'` SOURCE** ??the 49(d)-rider measurement), `IA.element ??INV.reference` branch landed (wire 193), `ExecState` 1, saved. Self-test on `SCRATCH_L0_20260921_025144.vi` (byte-identical to `eef91c1d?? at creation, **deleted in the same run**): CALL 1 error cluster **`(False, 0, '')`**, op `Text` read `'index'` off the machine, `Local` census **8 ??9**, NEW uid **[23507]**, owner `('TopLevelDiagram', 536)`, `ExecState` after **0**; 20/20 consecutive calls each added exactly one Local; **handles 34,167 ??30,687 (own pre-batch restart) ??51,418 (flat, delta 0, across the 20 calls) ??34,761**; refs **12 opened / 12 closed / 0 live**. **Four md5 gates PASS BEFORE AND AFTER** (ORIGINAL `2a78e17c??, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497??, `D1_s3a_focus_ind` `eef91c1d??), donor `OpFPLabels_v0.vi` byte-unchanged, nothing written under `tools/recipes/`. The two FAILs are an **ABSENT INSTRUMENT, not a failed binding** ??`read_back()` used `node_labels()`, which reads `Node.Label` 6359001 = the node's OWN label (`tools/gscript.py:588-594`), and all eight pre-existing Locals return the VI's FILE NAME there (`tools/bench/main_vi_node_labels.json`); the forced hypothesis review `archive/peer/2026-09-21-c60-l0-readback-none.md` (claude/hypothesis opus max, ANSWERED 504 s, `$4.3505`) is **disposed by the judgement session**, which re-aimed cycle 60 onto the READER above. `L0_d1` also measured, REPORT ONLY: `build_property('VI Server:Local',[('6355400',False)])` **RESOLVES, error column `''`** (probe node #23496 created and deleted again); style 2061 not probeable with existing verbs.
  owner_c60m1_attempt1: # ?뵏 **ACQUIRED 2026-09-21 02:5x ??cycle 60 material #1, the FIRST ACT of `## NEXT` line 75: S3b-L0. ONE DIAGNOSTIC under `tools/bench/`, never a recipe (48(n)): `tools/bench/diag_s3b_l0_createlocal.{py,log,json}` (966 lines, 32 gate sites, **AST OK** `tools/bench/c60_astcheck2.log` `BGRUN END rc=0 after 0s` ??every `g.<verb>` it calls already exists as a `def` in `tools/gscript.py`, **NO new verb**; `remove_bad_wires_scripted`/`remove_bad_wires`/`gui_save` neither imported nor called, `allow_broken=True` never passed). It BUILDS `claudeDev\OpCreateLocal_v0.vi` exactly as Pre-decided 49(d) fixes it ??copy donor `OpFPLabels_v0.vi`, `build_invoke('VI Server:Control','6331C02')`, branch the live Control reference (the donor's `IndexArray.element`) into the Invoke's `reference`, save at `ExecState` 1 ??authorisation **46(k)** (`docs/cycle27-plan.md:1697-1705`), quoted verbatim in the script; **49(i): the op will be revised on any review that gates it.** Then SELF-TESTS on `claudeDev\SCRATCH_L0_<stamp>.vi`, a duplicate of `D1_s3a_focus_ind.vi` (md5 `eef91c1d??) ??never the artefact itself (49(e)) ??and DELETES the scratch in the same run. Four md5 gates before AND after (ORIGINAL `2a78e17c?? FATAL, `D1_s1_copy` `3e3d23ce??, `D1_s2_loops` `6ff19497?? FATAL, `D1_s3a_focus_ind` `eef91c1d?? FATAL). Own pre-batch restart (44(e); LabVIEW was up at pid 24856). Command: `py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_s3b_l0_createlocal.log -- py -u tools/bench/diag_s3b_l0_createlocal.py`; turn held open to the `BGRUN END` line (OPEN 54(b)). ?좑툘 **49(d)'s RIDER IS BINDING ON SCORING: "6331C02 takes no parameters" comes from a wiki page that self-declares its parameter table incomplete ??if the method takes parameters, that is a MEASUREMENT the run RECORDS, not a failure.** Route B (`New VI Object` style 2061 + `Local.Control Name` 6355400) is NOT built; the run only REPORTS whether those two resolve. No VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰), no new process device, no recipe. `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). No route chosen or recommended, `docs/cycle27-plan.md` and `## NEXT` untouched.** The previous key's released note, VERBATIM: ??**RELEASED 2026-09-21 02:1x ??cycle 59 material #1. ?럦 **S3a IS DELIVERED AS ONE FILE: `claudeDev\D1_s3a_focus_ind.vi`, md5 `eef91c1d91f16b034707e4d1285ca8cb`, 476,172 B, version bytes `26 00 80 00`.** ONE run, the recipe UNEDITED (sha256 `1986626F??770`, 102,232 B, identical before and after): `py tools/bgrun.py --material --max-min 45 --log tools/bench/cycle59_s3a_recipe.log -- py -u tools/recipes/stage_d1_s3a_focus_ind.py` ??**`BGRUN END rc=0 after 596s`**, **GATES 64 pass / 0 fail**. Six saved sub-steps, each cold from the previous FILE in a freshly restarted LabVIEW: N1 `D1_s3a_focus_ind_n1_20260921_020123.vi` md5 `f186a1dd?? 476,215 B (owner_of(#23541) `('TopLevelDiagram',536)`??('Diagram',639)`, ExecState 1) 쨌 N2 `??n2_?? md5 `5dcf6cbe?? 476,171 B (wire 10990, ORDERED `Is Broken?` **False**) 쨌 B1 `??b1_?? md5 `6cfdbc8f?? 476,439 B (created wire 23606 deleted BY UID, ExecState 1) 쨌 B2 `??b2_?? md5 `63cf3ff4?? 476,431 B (owner_of(#23576)??('Diagram',639)`, ExecState 1) 쨌 B3 = the deliverable's own path, md5 `eef91c1d?? (wire 10799, ORDERED `Is Broken?` **False**) 쨌 Z0 cold read-only reopen: **ExecState 1**, owner_of of BOTH ControlTerminals `('Diagram',639)` (#23541 numeric `'index'`, #23576 boolean `'Automatic Error Handling'`), ControlTerminal census **116** (114 at the S2 baseline, +1 per leg). Refs 60 opened / 60 closed / **0 live**. Handles 34,162 before ??30,680 after the pre-batch restart ??47,353 after everything (LabVIEW up, pid 24856, 34,203 at release). ORIGINALS UNTOUCHED before AND after: ORIGINAL `2a78e17c449cacdaf5da389818526859`, `D1_s1_copy.vi` `3e3d23cefd3a334001aa9d6156bf1aee`, `D1_s2_loops.vi` `6ff19497f2309e007a214660bb64b911` (gates T1/T1b/T2 and Z1 all PASS). No motor / ASI / camera, no VI run, no GUI action, no new op VI, no `remove_bad_wires_scripted` / `gui_save` / `allow_broken`. `retrospective.py` / `audit_cycle.py` / `violations.py` NOT run here (OPEN 54(a)). Readings JSON: `tools/bench/stage_d1_s3a_focus_ind_20260921_020123.json`.** Previous acquire note, verbatim: ?뵏 **ACQUIRED 2026-09-21 02:0x ??cycle 59 material #1, `## NEXT` line 72's FIRST ACT minus the (already-done) disposition: LAUNCH `tools/recipes/stage_d1_s3a_focus_ind.py` UNEDITED (sha256 `1986626FB6F16CD08B68053339F1D040B170AF4310BE754C0E7FA32F783F5770`, 102,232 B, verified at launch) under `py tools/bgrun.py --material --max-min 45 --log tools/bench/cycle59_s3a_recipe.log`. Six fresh LabVIEW instances (N1 N2 B1 B2 B3 Z0); the recipe does its own pre-batch restart (44(e)). LabVIEW BEFORE the launch: pid 8388, 34,162 handles, started 01:04:22. See `owner_c59m1_acquired`. The previous key's released note, verbatim: # ??**NEVER ACQUIRED 2026-09-21 01:2x ??cycle 58 material #3 (the SECOND ACT of `## NEXT` line 72: S3a as a RECIPE). NO LabVIEW was touched: the recipe was WRITTEN, AST-checked and the launch gates DRY-RUN, and the gate refused, so nothing was launched.** ?럦 **`tools/recipes/stage_d1_s3a_focus_ind.py` NOW EXISTS** ??1,699 lines, 102,232 B, sha256 `1986626f??, **57 gate sites**, AST OK (`tools/bench/c58c_astcheck.{py,log}`, `BGRUN END rc=0 after 0s`): every `gscript` verb it calls (`build_index_array`, `build_property`, `create_indicator`, `delete_object`, `wire_indicators`, `node_info`, `node_terms_uid`, `panel_wiring`, `fp_labels`, `report_all`, `uids`, `count`, `exec_state`, `save`, `open_panel`, `close_panel`, `op`, `ref_counts`, `reset`) was machine-checked to already exist as a `def` in `tools/gscript.py` ??**NO new verb, NO new op VI, NO new device**; guards **ALL CLEAR** (`gui_save` never called, `allow_broken` never True, **`remove_bad_wires_scripted` neither imported nor called** ??48(d)). It builds ONE file `claudeDev\D1_s3a_focus_ind.vi` in **six saved sub-steps, each cold from the previous FILE in a fresh LabVIEW** (N1 place+create+delete+`move_in`+SAVE 쨌 N2 wire `#10757` t1 `'element'`+SAVE+ordered pass 쨌 B1 `build_property('VI Server:VI',[242])`+create on t4+delete the created wire BY UID+delete the carrier+SAVE 쨌 B2 `move_in`+SAVE 쨌 B3 wire `#10686` t0+SAVE **as the deliverable's own path**+ordered pass 쨌 Z0 COLD read-only reopen: `ExecState` 1, BOTH CTs `('Diagram',639)`, census 116). ?좑툘 **STEP 2 ??THE GATE DRY RUN, VERBATIM (`tools/bench/c58c_gatecheck.{py,log}`, `BGRUN END rc=0 after 0s`): GATE 1 NOW PERMITS AND GATE 2 REFUSES FOR A DIFFERENT REASON.** `tools/stop_record.py check_command(...)` ??**`ALLOW = True`, message empty**; the standing record now reads `tools/recipes/stage_d1_s3a_focus_ind.py  sha (none)  RELEASED` ??so cycle 58 dispatch 1's *"the file itself cannot be read, so the release cannot be matched to any bytes"* is **CLOSED by the bytes existing**, and the prior-art review's 4 `FIXED:` + 1 `REFUTED:` lines are accepted. But `tools/hooks/guard_cycle.py`, fed the real PreToolUse payload, **exits 2** on the VIOLATION-THRESHOLD condition, stderr VERBATIM: *"BLOCKED by tools/hooks/guard_cycle.py: a retrospective violation has reached its threshold."* ??`DUE repeated-failure-class: 18 occurrences (threshold 3) ??[reported loss: 318 min, $52.85, from 12 of 18 occurrence(s)]` and `DUE device-failed: 14 occurrences (threshold 1) ??[reported loss: 200 min, $32.13, from 14 of 14]`, both naming `2026-09-21-retrospective-cycle57.md` as their newest evidence, both ending *"Answer it in docs/violation-decisions.md: a dated block with `DECISION: device` or `DECISION: no-device` and the reason. Dated AFTER the retrospective above."* The newest block in `docs/violation-decisions.md` is **2026-09-20 09:30 (cycle 55, judgement)** and EVERY recent block is signed "judgement" ??so writing it is **NOT a material act** and was NOT taken. **`CYCLE_GUARD_OFF` was never set, no frontmatter date was edited, no review was rewritten, the gate was not patched, and the recipe was NOT launched** ??the written recipe plus this verbatim refusal is the dispatch's outcome. ??**STEP 4 CENSUS (files only, nothing built, nothing renamed): NO verb and NO `Op*.vi` in this fleet renames a front-panel CONTROL or INDICATOR.** `set_node_label` (`tools/gscript.py:2659`, `OpSetLabel_v0`) writes `Node.Label` 6359001 ??`Text.Text` 632D800 on `Diagram[d].Nodes[n]` ??a **node** writer; a front-panel `ControlTerminal` is **not in `Nodes[]`** (measured seven times: `tools/bench/build_d1_routeb_v{1..7}_run*.log:162/163/179` *"on Diagram[56] it is Nodes[None] with terminals []"*, and restated by `diag_s56_transport{2,3}` / `diag_s57_ctmove_wire.json:345`), so it CANNOT reach one. Every other label path is a READER: `fp_labels` (`OpFPLabels_v0`: `Panel.Controls[]` 6348801 ??`Control.Label` ??`Text.Text`), `panel_wiring` (`OpPanelWiring_v0`), `node_labels` (`OpNodeLabels_v0`), and `create_control` v1, which only REPORTS the label LabVIEW assigned (`gscript.py:2365-2366`). `move_by_label` / `delete_by_label` / `copy_into` SELECT by label, never write it. `conpane_assign` assigns a control to a connector-pane terminal, not a name. **`OpSetName_v0.vi` DOES exist in `claudeDev` but is referenced by NO `.py` in the project** (grep: only `archive/` narrative), and its target `Set Name.vi` is measured at `docs/NAMES.md:50` as writing *"a property literally called `Name` ??NOT the owned label"*; `OpNewFPArray_v0` (the one plan that used it, `docs/stage2-assembly-step-b.md:93`) is **not on disk**. So S3b's by-name Local Variables would inherit `'index'` and `'Automatic Error Handling'` unless something new addresses `Control.Label` ??REPORTED ONLY, nothing built. Handles/refs: **no LabVIEW process was contacted**, so none were read. ORIGINAL `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? **untouched ??no VI was opened at all**. No VI run (34(f)), no GUI action, no motor/ASI/camera. ?좑툘 **SECOND DRY RUN 01:24:30, AFTER the judgement session wrote the two blocks into `docs/violation-decisions.md` at 01:24:04 (`## repeated-failure-class ??2026-09-21 01:5x (cycle 58, judgement)` / `## device-failed ??2026-09-21 01:5x ??, both `DECISION: **no-device**`): `tools/bench/c58c_gatecheck2.log` ??GATE 1 still `ALLOW = True`, **GATE 2 STILL EXIT 2, THE IDENTICAL STDERR**. THE CAUSE IS MEASURED AND IS ONE CHARACTER: `DEC_RE` at `tools/violations.py:94` is `^##\s*([a-z0-9-]+)\s*[-??\s*(\d{4}-\d{2}-\d{2})(?:[ T]+(\d{2}:\d{2}))?` ??**`01:5x` is not `\d{2}:\d{2}`**, so the time is dropped and each block is read as date-ONLY `2026-09-21`; `tools/violations.py:116` then requires a date-only decision to fall on a **strictly later day** than the retrospective that raised the slug, and `2026-09-21-retrospective-cycle57.md` is the SAME day. A real `HH:MM` in both headings would discharge both. **NOT EDITED ??the blocks are the judgement session's file and its act (41(b) grain); no gate patched, `CYCLE_GUARD_OFF` never set, recipe still NOT launched.** ??**THIRD DRY RUN 01:26:19 (`tools/bench/c58c_gatecheck3.log`), after the judgement session rewrote both headings to `2026-09-21 01:24`: THE VIOLATION-THRESHOLD GATE IS CLEAR ??`guard_cycle` ADVANCED PAST it (and past the outcome layer, which runs next in `main()`), GATE 1 still `ALLOW = True`. ?뵶 **BUT IT NOW REFUSES ONE STEP FURTHER ON, THE `premature-build` DEVICE, stderr VERBATIM: *"BLOCKED by tools/hooks/guard_cycle.py: this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN ITSELF."* ??`recipe : tools/recipes/stage_d1_s3a_focus_ind.py (last changed 2026-09-21 01:19)` 쨌 `newest priorart review : archive\peer\2026-09-20-priorart-d1-s3a-focus-ind.md (2026-09-20 23:00)`; *"Either no prior-art review has run for this build, or the recipe was edited AFTER the review that saw it AND it has never run under that review. (A recipe that HAS already run once under the newest prior-art review is exempt??"*. The remedy it names is a fresh `py tools/prior_art_review.py --plan-file <plan> --slug <slug> --trigger cycle-start --recipe tools/recipes/stage_d1_s3a_focus_ind.py` under bgrun, **launched from PowerShell (the gate says the Bash tool returns rc 127 for this one today)**. ?좑툘 **THAT DISPATCH WAS NOT MADE: `docs/cycle27-plan.md` Pre-decided 48(f) states in writing that NO second prior-art review is spent on this re-cut and flags it as an assumption the user may overturn ??so spending one is judgement's call, not a material act.** Recipe unchanged throughout (sha256 `1986626f??, 102,232 B). No bypass of any kind. ??**THE JUDGEMENT SESSION THEN OVERTURNED 48(f) AND THE PRIOR-ART REVIEW WAS DISPATCHED AND LANDED: `archive/peer/2026-09-21-priorart-d1-s3a-recipe.md`** (claude/priorart **opus effort high**, `OUTCOME: ANSWERED (537s)`, **`COST: $8.0285` in 36 / out 38,278 / cache-create 503,584 / cache-read 4,071,094, 535s, 26 turns**, log `tools/bench/priorart_d1_s3a_recipe.log`, `BGRUN END rc=0 after 537s`). **Verdict word: `NOT novel`, 4 findings ??`contradicted` 쨌 `unread-evidence` 쨌 `already-built` 쨌 `already-measured`**, and a new STOP RECORD is armed against **sha `1986626fb6f1`**. Its one sentence: *"the recipe is right about what to build and right about how ??what the record already answers is WHERE IT STARTS"* (B1 `already-built`: `b1/b2/b3` are on disk from 01:00, so the chain rule points the numeric leg at `??b3_20260921_010034.vi` and turns six sub-steps into two + Z0). It also states what is **genuinely NOT covered**: both legs on ONE file has never been done, `Z0_d`'s census **116** is a number nothing on disk has produced (the b1/b2 cold reopens read **115**, `diag_s58_boolwire.log:106`), and Z0's cold read with BOTH terminals on `('Diagram',639)` is a first. ?좑툘 **NOTHING DISPOSED ??the `## What was done with it` section is left `(Claude fills in)`; writing the `FIXED:`/`REFUTED:` lines is a judgement act (41(b) grain) and was explicitly reserved by the judgement session.** The recipe was **NOT touched** (the gate's own readback now says `reviewed sha: 1986626fb6f1`, i.e. the on-disk bytes still hash to what was reviewed) and **NOT launched**. ??**THE JUDGEMENT SESSION THEN DISPOSED ALL FOUR (recipe STANDS as written, `already-built` REFUTED on the bench-scratch/never-cold-read ground) AND THE THREE DOC REPAIRS ARE DONE ??01:40??1:41, all three mtimes postdating the 01:36:46 review, so a `FIXED:` citation validates:** **A** `docs/NAMES.md:475` ??the *"STILL UNMEASURED ??error 5001"* line replaced by the measured truth (`diagram_index` = the INDICATOR's own diagram, `gscript.py:1787-1789`; numeric `Is Broken?` **False** `diag_s57_typepair.log:195`, Boolean **False** `diag_s58_boolwire.log:151-154`, and `diag_s57_ctmove_wire.log:83`'s raise named as the TYPE mismatch it is). **B** `docs/toolkit-capabilities.md:274` ??*"no op ??never built"* replaced by the measured route (carrier on the `VI ??Block Diagram` head ??`create_indicator` ??delete carrier ??`move_in`) with the two grains that decide it (SINK ??no wire but the SINK's type; SOURCE ??right type but a REAL wire that must be deleted first, `delete_object(target,'Wire',<idx>,verify=True)`, no by-uid form) and the three b1/b2/b3 md5s. **C** `docs/toolkit-capabilities.md:275` ??NEW adjacent row: two created `ControlTerminal`s coexisting and relocating in ONE run is MEASURED (`diag_queue_donor2.log:41-55`), with the scope limit that donor2 never wired either, so two `wire_indicators` calls on one file stays unmeasured. **D** `docs/d1-build-plan.md` ??rows **:295** (`#10757`) and **:304** (`#10686`) now flag that the 1.2 move SEVERS each S3a indicator's wire, and new **짠5a-ter at :344** (sentence at **:346**) states plainly that both indicators go bare across the move, gives the two re-wire rows (w10990 off `#10757` t1 `'element'`; w10799 off `#10686` t0 `'x .and. y?'`), says they belong to **1.2 not S3a**, and records that this **corrects 45(c)** (`docs/cycle27-plan.md:1588-1589` vs 37(d) `:1093` / 33(a) `:843`). `doc_lint` **L2 PASS ??1,430 citations checked, none dangling**; STATUS 80 lines (L3 PASS). Recipe still untouched, still unlaunched. ?뵶 **FOURTH DRY RUN 01:43:42 (`tools/bench/c58c_gatecheck4.log`), after all four dispositions were written: GATE 1 `ALLOW = True` (the record now carries BOTH rows ??`sha (none) RELEASED` and **`sha 1986626fb6f16cd0 RELEASED`**, so the new review's `FIXED:`/`REFUTED:` lines ARE accepted and `premature-build` is SATISFIED). BUT GATE 2 STILL EXITS 2, ON THE NEXT GATE IN LINE ??THE RETROSPECTIVE:** *"BLOCKED by tools/hooks/guard_cycle.py (CLAUDE.md: every cycle ends with a RETROSPECTIVE review). newest build log : tools\bench\c58c_gatecheck4.log 쨌 newest retrospective : archive\peer\2026-09-21-retrospective-cycle57.md ??The previous cycle's execution has not been reviewed as a cycle - only its individual hypotheses were."* ?좑툘 **AND IT IS NOT AN ARTEFACT OF THE DRY-RUN INSTRUMENT ??MEASURED: the retrospective is stamped `2026-09-21 00:00:07`, while cycle 58's OWN dispatch-2 build log `tools/bench/diag_s58_boolwire.log` is `01:05:40`** and `tools/bench/priorart_d1_s3a_recipe.log` is `01:36:46`; both already postdate it, so deleting every `c58c_gatecheck*.log` would change nothing. **What is missing is the CYCLE-58 retrospective.** ?뵶 **NOT RUN, and it cannot be run to clear this: OPEN 54(a) ??`guard_bash.py:226-227` marks a session retro-done on ANY `retrospective.py` in command position and `guard_session` then refuses every later dispatch, so running it would END the cycle rather than release the launch.** Reported, no bypass: `CYCLE_GUARD_OFF` never set, no gate patched, no log deleted, no date rolled, recipe sha still `1986626fb6f1`, not launched. **No route chosen or recommended, no plan document edited, `## NEXT` untouched.**
  owner_c59m1_acquired: # ?뵏 **ACQUIRED 2026-09-21 02:0x ??cycle 59 material #1. ONE ACT: launch `tools/recipes/stage_d1_s3a_focus_ind.py` with NOT ONE BYTE EDITED (sha256 re-verified `1986626F??770` at launch, 102,232 B ??an edit would re-arm `guard_cycle`'s `premature-build` device against `archive/peer/2026-09-21-priorart-d1-s3a-recipe.md`, already disposed). Command: `py tools/bgrun.py --material --max-min 45 --log tools/bench/cycle59_s3a_recipe.log -- py -u tools/recipes/stage_d1_s3a_focus_ind.py`. The recipe builds `claudeDev\D1_s3a_focus_ind.vi` from `claudeDev\D1_s2_loops.vi` in six sub-steps (N1 N2 B1 B2 B3 Z0), each cold from the previous FILE in a freshly restarted LabVIEW, and gates the three ORIGINAL md5s itself (T1 `2a78e17c?? FATAL, T1b `3e3d23ce??, T2 `6ff19497?? FATAL; Z1 re-checks all three after everything). NO motor / ASI / camera (rig 議곕┰), no VI run, no new op VI, no GUI action, no `remove_bad_wires_scripted` / `gui_save` / `allow_broken`. Turn held open to the `BGRUN END` line (OPEN 54(b)). `retrospective.py` / `audit_cycle.py` / `violations.py` NOT run here (OPEN 54(a)).**
  owner_c59m3: # ??**NEVER ACQUIRED 2026-09-21 02:2x ??cycle 59 material #3, ONE act: ONE peer question, archived. NO LabVIEW contacted (no process, no VI, no recipe, no diagnostic, no op VI, no handles/refs read), no motor/ASI/camera, nothing built or patched, `## NEXT` and `docs/cycle27-plan.md` untouched.** STEP 0 first: `archive/peer/2026-09-20-c56-localvar-scripting.md` ALREADY answers Q1's name / Q2 / Q3 / Q4, so it was attached as already-known and the question was pointed at what it does NOT answer ??the method's parameter list and return type, whether any NI *reference* page exists, and Q5 (an invoke whose target reference is UNWIRED). **DISPATCHED: `py tools/bgrun.py --max-min 18 --log tools/bench/peer_s3b_localvar.log -- powershell -NoProfile -File tools/peer.ps1 -Kind fact -Slug s3b-local-variable-route -TimeoutSec 900 -TaskFile tools/bench/peer_s3b_localvar_task.md` ??`BGRUN END rc=0 after 80s`; `OUTCOME: ANSWERED (79s)`, **claude / role fact / fable effort low**, `COST: $1.3397` in 14 / out 4,063 / cache-create 40,850 / cache-read 223,316 (78s, 10 turns). Archive: **`archive/peer/2026-09-21-s3b-local-variable-route.md`**, `verdict: unverified`. The two things it adds: (1) the wiki's parameter table for `Control ??Create:Local Variable` **6331C02** lists **NO input parameters**, return **Local Refnum** only (page stamped *"Parameters Table is incomplete"*; sibling `Create:Invoke Node` 6331C04 identical); (5) it is an **instance method**, so the control instance is the ONLY identifier of the binding, every example wires a live control reference, and **no name-string or class-name overload is documented anywhere** ??from there INFERRED (its own flag) that an unwired reference cannot address a control and would give error 1055. It also states plainly that **NO NI reference page exists** for 6331C02, style 2061 or 6355400/6355401/6355403, and that **no better or contradicting source** was found for any archived fact. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)); its `## What was done with it` is written in full and NOTHING in it was acted on ??no route chosen or recommended.** `retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run.
  owner_c59m2: # ??**NEVER ACQUIRED 2026-09-21 02:3x ??cycle 59 material #2, a FILES-ONLY census for S3b. NO LabVIEW was contacted: no process touched, no VI opened, no recipe, no diagnostic, no op VI, no handles/refs read, no motor/ASI/camera, `## NEXT` and `docs/cycle27-plan.md` untouched.** Six answers: **(1) NO verb in `tools/gscript.py` creates a Local Variable** ??the word `local` occurs once, in a comment (`:830`); the only vehicle for `Control ??Create:Local Variable` **6331C02** is `build_invoke(target, cls, method_id, location, diagram_index=0)` `:2159`, whose `reference` input is **deliberately UNWIRED** (`:2164-2166`, "with a reference the erdosmiller creator writes the object's bare class name and fails silently"), so it cannot address a front-panel control BY LABEL at all. `create_control :2360` / `create_indicator :2388` take `(target, node_index, terminal_index)` ??no label, no `diagram_index`. `copy_by_index(donor, cls, index, target, expect_uid=None, finish=None)` `:1479` selects by INDEX (no `duplicate` parameter exists ??46(h)'s `duplicate=True` does not match the on-disk signature) and has no destination diagram. `copy_into(donor, label, target, prepare=None)` `:1399` / `move_by_label :1561` select by label in the DONOR. `wire_control(target, control_names, dst_cls, dst_i, dst_terms, branch=False, src_diagram_index=0)` `:1928` is the ONE verb that targets panel controls BY LABEL, but it WIRES an existing control terminal and `Get Controls` only sees terminals on `src_diagram_index` (`:1947-1949`). **(2) NO `Op*.vi` in `claudeDev` (108 files) has `Local` in its name.** Panel-object creators that exist: `OpCreateControl_v1` + `OpCreateIndicator_v0` (live, `gscript.py:2348-2349`), `OpCreateControl_v0` (donor only, `build_opconnect.py:3,13,18`), `OpCreateConst_v0` / `OpCreateConstOnTerm_v0` / `OpCreateEqual_v0` (referenced by recipes), `OpFP_v0` (`build_keystone.py:29`), `OpPanelWiring_v0` (`gscript.py:822`). ?뵶 **TWO ORPHANS ??on disk, referenced by NO `.py` and NO `docs/`: `OpSetName_v0.vi` (only `tools/bench/build_keystone.log:2260,2289`) and `OpCreatePropNode_v0.vi` (0 hits anywhere outside `claudeDev`).** ?좑툘 **AND THE DONOR LIBRARY HAS NO LOCAL-VARIABLE CREATOR: `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Create*.vi` = 50 files, none named `Create Local Variable.vi`** (`build_opcreator.py:14` is the path of record). **(3) THE ROUTE IS NOT IN `docs/vi-server-ids.json`** ??grep for `Local` returns **0 lines**, and `6331C02` appears **nowhere** in `docs/` except `docs/cycle27-plan.md:1678` and `:1703` (both quoting the cycle-56 peer). Every `Control`-matching key: `:8` `"Control": "VI Server:Control"` 쨌 `:21` `Control.Label 6332005` 쨌 `:23` `Control.Indicator 6332007` 쨌 `:24` `Control.Value 633200D` (+ `:148` "TRIED AND FAILED 2026-09-12 ??the ID is not resolving for this class") 쨌 `:45`/`:70` `Terminal.Create Control 6349C01` 쨌 `:47` `Panel.Controls[] 6348801` 쨌 `:51` `ConnectorPane.Controls[] 239A8403` 쨌 `:164` `ControlTerminal.Control 6353000  UNVERIFIED`. **(4) `build_invoke` and `build_property` BOTH carry `diagram_index`** (`:2159`, `:2194`) ??so a 6331C02 Invoke could be placed directly on a NESTED diagram; `drop_subvi :1225`, `queue_node :1122`, `loop_in :1155`, `wire_indicators :1756-1757`, `net_map :2505` also carry one. Top-level-only (no `diagram_index`, per the cycle-58 phase-A census in `STATUS.md` `owner_c58m1`): `build_index_array :2322`, `build_case :2824`, `build_clfn :2699`, `while_loop :1191`, `for_loop :1210`, `loop_kernel :1804`, `build_kernel :2082`; plus `create_control :2360` / `create_indicator :2388`. `move_in(target, uid, dest_diagram_index, position)` is NOT in gscript ??it lives at `tools/recipes/build_d1_v0.py:318`. **(5) `#23032` IS A `WhileLoop`** (body `Diagram #23058`), owned by `Diagram #686`, first measured by cycle 50's `tools/bench/diag_s2_scaffold.py` (`docs/cycle27-plan.md:951`) and created as a stage artefact by **S2** (`claudeDev\D1_s2_loops.vi`, md5 `6ff19497??); the S2 recipe's labels and the binding assignment are `docs/cycle27-plan.md:1127-1129` ??*"DECISION: loop a `#23032` (body `#23058`) IS loop 1.5 FOCUS"*, `:1074` records S2 adding exactly `{10170, 23032, 23041}`. ?좑툘 `:1037`'s `Obtain Queue #23032` is a DIFFERENT object reusing the uid in another VI ??do not conflate. **The MEASURED 1.5 row table: `docs/cycle27-plan.md:1182-1188`** (cycle 53, `tools/bench/c53_row_class.json`, 17 cut terminals, `#10407` t0?뱓6 + `#48` t0?뱓6 + `#3529`/`#3560`/`#3447` t0; `cross-loop:1.2->1.5` 2 쨌 `from-tunnel` 1 쨌 `same-loop` 5 쨌 `to-sr` 2 쨌 `from-sr` 2 쨌 `source-side` 5; ?좑툘 its *"sources on `#686` = 0"* clause is **STRUCK as unsound** at `:1188`), **and cycle 54's 9/9 rows at `docs/cycle27-plan.md:1283-1290`**. **(6) NEITHER `docs/NAMES.md` NOR `docs/toolkit-capabilities.md` RECORDS A LOCAL VARIABLE CREATOR ??NOT AT ALL, measured or unmeasured.** Both record `Local` only as a READ/traverse class: `docs/NAMES.md:260` *"`Local`: `Control` 6355403, `Control Name` 6355400"* inside a block headed *"LabVIEW Wiki, 2026-09-14; **not yet verified on this machine**"*; `docs/NAMES.md:337` lists `LocalVariable` among *"Class names that Traverse rejects"*; `docs/toolkit-capabilities.md:284` *"**Valid:** `Local` (8) ??* and `:289` *"**Invalid (error 109):** `LocalVariable` ??*; `docs/toolkit-capabilities.md:547` *"Sequence locals (7) | all report `uid 0`; not placeable at all by current means"*. `docs/cycle27-plan.md:1690-1692` already records that **no generic property reader exists**, so the 8 existing `Local` objects' bindings cannot be read and `6355400` appears 0 times in both `docs/vi-server-ids.json` and `tools/gscript.py`. **NOTHING BUILT, nothing renamed, no plan edited, no gate run (`retrospective.py`/`audit_cycle.py`/`violations.py`/`doc_ingest.py`/`prior_art_review.py` all NOT run).**
  owner_c58m2: # ??**RELEASED 2026-09-21 01:1x ??cycle 58 material #2. ONE DIAGNOSTIC under `tools/bench/`, never a recipe: `tools/bench/diag_s58_boolwire.{py,log,json}` (AST OK 1375 lines, 39 gate sites, guards ALL CLEAR ??`tools/bench/c58b_astcheck.log`; `gscript` verbs used are all pre-existing, `delete_object` has ONE call site, `remove_bad_wires*` neither imported nor called). ONE RUN, `BGRUN END rc=0 after 306s`, **36 PASS / 0 FAIL.** ?럦 **PRE-DECIDED 48(e) EXECUTED END TO END: ALL THREE SUB-STEPS MET THEIR PASS CRITERIA AND ALL THREE LEFT A FILE.** ?럦 **S3a's BOOLEAN HALF IS BUILT AND `Is Broken?` READS FALSE.** ??**THE ONE CHANGED VERB CALL WORKED, AND IT WAS NARROW:** signature `delete_object(target, cls, index, verify=True)` (`tools/gscript.py:2240` ??there is no by-uid form; `Wire` IS a live Traverse class, so the uid was resolved as `[o['uid'] for o in g.report_all(target,'Wire')].index(uid)` and `verify=True` returned the uid SET that vanished). **`delete_object(target, 'Wire', 1664, verify=True)` on uid #23576 (of 1906 members) ??`gone [23576]`, error column `''`**; the set that disappeared IS EXACTLY the wire `create_indicator` added, **PRE-EXISTING wire uids that disappeared: `[]`**, ControlTerminal **115 ??115** across the delete. Then `delete_object(target,'Property',0,verify=True)` on the carrier #23486 ??`gone [23486]`, error `''`. **`remove_bad_wires_scripted` was REFUSED throughout (48(d)) ??not imported, not called; the GUI form `gscript.py:1629` not called; no VI was mutated to make it legal.** ?럦 **B1 ??`ExecState` TIMELINE `1 (baseline) ??1 (after build_property) ??1 (after create_indicator) ??1 (after the WIRE delete) ??1 (after the CARRIER delete)`, i.e. 48(b)'s ExecState-0 IS GONE.** Live, nothing cached (34(h)): `diag_index(#639)=46`, `(#536)=0`, `(#686)=19`; `owner_of(#10686)=('Diagram',639)`; `#10686` Nodes[25], terminals `[(0,'x .and. y?',SOURCE,10799),(1,'y',sink,9105),(2,'x',sink,3050)]`. Carrier C2 `build_property(target,'VI Server:VI',[('242',False)],(6200,5200),diagram_index=0)` ??`Property #23486`, `owner_of ('TopLevelDiagram',536)`, error `''`; `node_info` **0 ??1** `[(0,'Property Node','Property Node')]`; FULL terminal table `[(0,'reference',sink),(1,'reference out',SOURCE),(2,'error in (no error)',sink),(3,'error out',SOURCE),(4,'Def Err Handling',SOURCE)]` ??chosen t4 `'Def Err Handling'`. `create_indicator(Nodes[0].Terminals[4])` ??**`ControlTerminal #23555`**, census **114 ??115**, error `''`; whole-VI `Wire` **1905 ??1905 ??1906**, the added uid **[23576]** (48(b) reproduced exactly). **LABEL READ OFF THE MACHINE, never retyped: `'Automatic Error Handling'` (hex `4175746f6d61746963204572726f722048616e646c696e67`), no newline, not a duplicate, and equal to dispatch 1's reading.** **ARTEFACT `claudeDev\D1_s3a_boolcarrier_b1_20260921_010034.vi`, md5 `7237b2c1e150ebeaf0f32940b07abcfb`, 476,241 B, LV2026 `26 00 80 00`.** ?럦 **B2 ??47(e)'s SAVE POINT, BEFORE ANY WIRING.** The B1 file reopened **COLD in a fresh LabVIEW (own restart) at `ExecState` 1**; `move_in(#23555 ??Diagram #639 @ LIVE index 46, (120,4000))` returned 3447, error `''`; **`owner_of(#23555)` `('TopLevelDiagram',536) ??('Diagram',639)`, `ExecState` 1 ??1**, ControlTerminal **115 ??115**, panel rows **115 ??115**; ONE junk `Invoke` **#23490** left and purged in-run (`delete_object(target,'Invoke',1,verify=True)` ??`gone [23490]`, error `''` ??PREDICTED RISK (i)). **ARTEFACT `??b2_20260921_010034.vi`, md5 `148050141085bc00ffc1e94e9977ea24`, 476,245 B, LV2026.** ?럦 **B3 ??THE TYPE QUESTION IS ANSWERED AND IT IS FALSE.** The B2 file reopened COLD at `ExecState` 1, `owner_of(#23555)=('Diagram',639)`; `#10686` live membership `Function` index **102** of 183; **`wire_indicators(Function[102], ['x .and. y?'] -> ['Automatic Error Handling'], diagram_index=46)` error column `''`** (47(b): 46 is the INDICATOR's diagram, `gscript.py:1787-1789`); the indicator's wire **0 ??10799** (a BRANCH: whole-VI `Wire` **1905 ??1905**, delta 0); **`ExecState` 1 ??1 across the wiring**; `#10686` **3/3 wired before and after**; `#637` **59 ??59 terminals / 48 ??48 wired ??increase 0, NO tunnel and NO border object (37(e) grain, explicit)**. Saved at `ExecState` 1 BEFORE the read: **ARTEFACT `??b3_20260921_010034.vi`, md5 `dc14dd000dfe90c0426b30fa6b69cbc2`, 476,169 B, LV2026.** Then the ORDERED second pass (42(b), idempotent re-connect `#10686` t0 ??`#10407` t0, `wire_delta` **0**, op error `''`): **`Is Broken?` = `False` on wire uid 10799** (`ExecState` after that read 0 ??the `docs/NAMES.md:912-918` perturbation, which is why the save came first). ?좑툘 **`guard_peer` BLOCKED the build over dispatch 1's `diag_s58_boolcarrier_run2.log` `FAIL C1 B3b ExecState after the delete == 1  0` (the 00:29 review being OLDER than the 00:34 log), so the review it demands was dispatched and is archived: `archive/peer/2026-09-21-c58-boolwire-dangling.md`** (claude/hypothesis opus max + web, **ANSWERED 588 s, `$4.3192`**, `BGRUN END rc=0 after 588s`, log `tools/bench/peer_c58_boolwire.log`), verdict **`REFUTED in its load-bearing sentence ??the run never measured that the indicator is "left sourced by a wire whose node is gone", and the only post-delete reading of that terminal in the whole log says it is bare`** ??**RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), disposition written IN FULL in its `## What was done with it`, and NOTHING IN IT ACTED ON.** Ordering, for the record: `diag_s58_boolwire.py` was written IN FULL **before** the review was dispatched and was **NOT changed afterwards** ??not one line; four of its points (assert `gone == {uid}`; recompute the uid from the `uids(Wire)` diff, never hard-code it; save before the `Is Broken?` read; no new op) coincide with what the file already did. Its cheapest test (`panel_wiring` immediately after the carrier delete), its ExecState re-reads, its Wire-uid-set-after-the-move and its wider census across the wire delete are **NOT IMPLEMENTED**; its 짠0 correction that 48(b) states the C1/C2 timeline more generally than 48(c) allows is **RECORDED, no plan document edited**; `gscript.py` and `OpDelete_v0` untouched. Refs **30 opened / 30 closed / 0 live**; handles 30,977 ??30,690 (own pre-batch restart, 44(e)) ??60,278 ??30,699 (B2's restart) ??47,917 ??30,689 (B3's restart) ??**63,523**. ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged before AND after. ??Gate **Z3 PASS**: the stop-recorded S3a recipe `exists=False` at the START and at the END ??reported, never written, never launched. No new op VI (47(i) route 2 NOT built), no new device, no VI run (34(f)), no GUI action, no motor/ASI/camera. **No route chosen or recommended, no plan document edited, `## NEXT` untouched.**
  owner_c58m2_acquired: # ?뵏 **ACQUIRED 2026-09-21 01:0x ??cycle 58 material #2, executing `docs/cycle27-plan.md` Pre-decided 48(e): S3a's BOOLEAN half in THREE saved sub-steps, each starting from the PREVIOUS FILE in a FRESH LabVIEW instance. ONE DIAGNOSTIC under `tools/bench/`, never a recipe: `tools/bench/diag_s58_boolwire.{py,log,json}` (AST OK, `tools/bench/c58b_astcheck.log`; guards assert `gui_save` never called, `allow_broken` never True, and `remove_bad_wires_scripted` neither imported nor called ??48(d) REFUSES it). THE ONE CHANGED VERB CALL vs dispatch 1: the wire `create_indicator` makes on a SOURCE terminal (48(b)) is deleted BY UID, BEFORE the carrier, through `delete_object(target, cls, index, verify=True)` (`tools/gscript.py:2240` ??there is no by-uid form; `Wire` IS a live Traverse class, so the uid is resolved to its index over `report_all(target,"Wire")` and `verify=True` returns the uid SET that disappeared). Carrier of record C2 `build_property('VI Server:VI',[242])` (48(c); C3 withdrawn). B1 from `D1_s2_loops.vi` ??`??b1_<stamp>.vi` (pass: `ExecState` 1); B2 cold from B1 ??`??b2_<stamp>.vi` (pass: `owner_of`=('Diagram',639) AND `ExecState` 1 ??**47(e)'s save point, BEFORE any wiring**); B3 cold from B2 ??wire to `#10686` t0 + ordered 42(b) pass (pass: `Is Broken?` False). No recipe (the stop-recorded S3a recipe must still not exist at the end, gate Z3), no new op VI (47(i) route 2 is NOT built), no new device, no VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰). ?좑툘 `guard_peer` BLOCKED the build over dispatch 1's `diag_s58_boolcarrier_run2.log:?? `FAIL C1 B3b ExecState after the delete == 1` (the 00:29 review is OLDER than the 00:34 log), so the review it demands was dispatched FIRST: slug `c58-boolwire-dangling`, `-Agent claude -Role hypothesis`, log `tools/bench/peer_c58_boolwire.log`. No route chosen or recommended, no plan document edited, `## NEXT` untouched.
  owner_c58m1: # ??**RELEASED 2026-09-21 00:3x ??cycle 58 material #1, the FIRST ACT of `## NEXT` (47(i) route 1). ONE DIAGNOSTIC under `tools/bench/`, never a recipe: `tools/bench/diag_s58_boolcarrier.py` (AST OK 1438 lines, 32 gate sites, 14/14 guard assertions clear ??`tools/bench/c58_astcheck{,2}.log`). ??`tools/recipes/stage_d1_s3a_focus_ind.py` exists=False at the START and at the END (gate `Z3` PASS) ??reported, never written, never launched. TWO RUNS, THE BUDGET SPENT: run 1 `tools/bench/diag_s58_boolcarrier_run1.{log,json}` `BGRUN END rc=1 after 229s`, **51 pass / 9 fail**; run 2 `tools/bench/diag_s58_boolcarrier_run2.log` + `diag_s58_boolcarrier.json` `BGRUN END rc=1 after 248s`, **54 pass / 9 fail** ??the SAME 9 (`B3b`/`B4d`/`B5` 횞 C1,C2,C3).** ?럦 **PHASE A (files only) SETTLES THE CENSUS: `build_property` (`tools/gscript.py:2194`) IS THE ONLY VERB IN THE FLEET WITH A BOOLEAN-BY-CONSTRUCTION OUTPUT TERMINAL.** `build_invoke` `:2159` has no Boolean-returning method nameable from `docs/vi-server-ids.json`'s `methods` block; `queue_node` `:1122` yields a refnum + error cluster; `loop_in` `:1155` / `exit_while` `:1083` / `exit_loop` `:1721` expose the conditional terminal as a SINK; `drop_subvi` `:1225` would need a donor VI and adds a SubVI dependency (29(g)). Top-level-only placers (no `diagram_index`): `build_index_array :2322`, `build_case :2824`, `build_clfn :2699`, `while_loop :1191`, `for_loop :1210`, `loop_kernel :1804`, `build_kernel :2082`. ?럦 **ALL THREE CANDIDATES PLACED AND ALL THREE PRODUCED A BOOLEAN-NAMED INDICATOR, EVERY ERROR COLUMN `''`:** `owner_of` `('TopLevelDiagram',536)`, `node_info` **0 ??1**, `ControlTerminal` **114 ??115**, labels READ OFF THE MACHINE (never retyped), none with a newline, none a duplicate ??**C1** `build_property('VI Server:VI',[('291',False),('292',False)])` ??terminal table `[(0,'reference',sink),(1,'reference out',SOURCE),(2,'error in (no error)',sink),(3,'error out',SOURCE),(4,'PanelLoaded',SOURCE),(5,'DiagramLoaded',SOURCE)]`, carrier t4 `'PanelLoaded'` (the 2026-09-16 prediction MATCHED), indicator `'Metrics:Front Panel Loaded'` (hex `4d6574726963733a46726f6e742050616e656c204c6f61646564`); **C2** `('VI Server:VI',[('242',False)])` ??carrier `'Def Err Handling'`, indicator `'Automatic Error Handling'`; **C3** `('VI Server:Wire',[('6371004',False)])` ??carrier `'Broken?'`, indicator `'Is Broken?'` (so the class string `VI Server:Wire`, never passed to `build_property` before, RESOLVES). `move_in` also worked on all three ??`owner_of` `('TopLevelDiagram',536) ??('Diagram',639)`, census 115 ??115, panel rows 115 ??115, one junk `Invoke` purged each, error `''`. ?뵶 **BUT NOT ONE REACHED A LEGAL SAVE POINT, AND RUN 2'S ADDED READING (`B3d`) NAMES THE MUTATION INSTEAD OF INFERRING IT: `ExecState` 1 ??1 (after `build_property`) ??1 (after `create_indicator`) ??**0 (after `delete_object`)** on C1 AND C2; on C3 it is 1 ??**0 after `build_property` itself**. Whole-VI `Wire` **1905 ??1905 ??1906 ??1906**: `create_indicator` adds a REAL wire object (uid **23586** C1, **23576** C2/C3) and **that uid is STILL ALIVE after the carrier is deleted**, with **0** pre-existing wire uids removed.** So the created indicator is left sourced by a wire whose node is gone. `ExecState` was 0 at every `B5`, `g.save()` was therefore NOT ATTEMPTED (`allow_broken` False, `gui_save` never called) and **`ARTEFACTS ON DISK: []` ??three candidates, zero files, which is the run's real cost under the user's 2026-09-19 rule.** `B6`..`B8` never ran, so **`Is Broken?` HAS NO READING THIS CYCLE and 47(i) route 1 is UNANSWERED.** ?좑툘 **PHASE C, VERBATIM AND NOT WHAT THE BRIEF EXPECTED: `guard_cycle` DRY RUN ON `py -u tools/recipes/stage_d1_s3a_focus_ind.py` ??exit 2, REFUSES ??but the refusal comes from `tools/stop_record.py`, the prior-art LAUNCH GATE, and its reason is `"this recipe has a released stop record, but the file itself cannot be read, so the release cannot be matched to any bytes"` with `reviewed sha: (none)` and `unreadable: tools/recipes/stage_d1_s3a_focus_ind.py`. The review's 4 `FIXED:` + 1 `REFUTED:` lines were therefore NEVER TESTED ??the gate cannot reach that question while the recipe does not exist. NO DATE WAS EDITED, `CYCLE_GUARD_OFF` WAS NEVER SET, THE GATE WAS NOT PATCHED.** ?좑툘 **TWO `guard_peer` HYPOTHESIS REVIEWS, both FORCED, both ANSWERED, both RECORDED NEITHER ACCEPTED NOR REJECTED (41(b)) with dispositions written in full:** (a) `archive/peer/2026-09-21-c58-typepair-a1-nonresult.md` ??the review cycle 57's `diag_s57_typepair.log:33` owed, which blocked run 1 (claude/hypothesis opus max + web, **ANSWERED 484 s, `$3.9606`**, log `tools/bench/peer_c58_typepair_a1.log`); verdict **`REFUTED ??the causal half survives; the two load-bearing clauses do not`**, naming three instrument defects on disk (the `except ??None` swallow at the gate boundary; `diag_s57_typepair.log:37`'s canned "phase E did not save (ExecState None)" from the unconditioned `else:` at `:1080-1082`; and run 1's JSON destroyed by run 2 because `OUT` carries no stamp at `:164`). Its four proposals (exception class in the gate detail, an `A0` PID/StartTime witness, a stamped JSON name, an `O_CREAT|O_EXCL` single-flight lock in `bgrun.py`) were **ALL RECORDED AND NONE IMPLEMENTED**; `bgrun.py`/`gscript.py`/`bench_prep.py`/`diag_s57_typepair.py` untouched. (b) `archive/peer/2026-09-21-c58-delete-execstate0.md` ??the review run 1's `B3b` owed (claude/hypothesis opus max + web, **ANSWERED 381 s, `$3.6322`**, log `tools/bench/peer_c58_delete_execstate0.log`); verdict **`REFUTED ??the "dangling wire" is not established by this log`**, because `gscript.py:829-830` defines `wire 0 / wire_err 1055 / term_err 0` as the **BARE** signature and `diag_s57_typepair.log:116,:140` shows cycle 57's clean 35/0 run producing the same row at `ExecState` 1. ?뵶 **ONE THING IT SAID WAS ACTED ON AND IT WAS A REMOVAL: a `B3c` step calling `remove_bad_wires_scripted` had been written into run 2 and was DELETED BEFORE LAUNCH** ??that verb has a MEASURED over-removal on this machine (`archive/2026-09-17-status-d1-route-b-2.md:45`: it "DELETES THE TUNNEL"), which is a rule-1a hazard, and taking that risk is judgement's call. **No repair of any kind was attempted; run 2's only addition is READINGS.** ?좑툘 **AND THE MEASUREMENT ANSWERED THE REVIEWER'S OWN FALSIFIER AGAINST HIM** ??he wrote "if uid 23586 is alive after the delete, I am wrong about the mechanism and the claim's cause stands"; `B3d` reads it **ALIVE** on all three. Its 짠6 ROUTE proposals (don't delete the carrier before the save; or an `OpCreateConstOnTerm_v0`-shaped op addressing a NESTED node's terminal = 47(i) route 2) are **NOT TAKEN** and are judgement's to dispose. Refs **33 opened / 33 closed / 0 live**; handles 30,965 ??30,687 (own pre-batch restart) ??**60,292**. ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged before AND after BOTH runs. No VI run (34(f)), no new op (47(i) route 2 NOT built), no new device, no recipe, no GUI action, no motor/ASI/camera. No route chosen or recommended, no plan document edited, `## NEXT` untouched.
  owner_c58m1_acquired: # ?뵏 **ACQUIRED 2026-09-21 00:1x ??cycle 58 material #1, the FIRST ACT of `## NEXT` (47(i) route 1). ONE DIAGNOSTIC under `tools/bench/`, never a recipe: `tools/bench/diag_s58_boolcarrier.{py,log,json}` (AST OK 1343 lines, 31 gate sites, 14/14 guard assertions clear ??`tools/bench/c58_astcheck.log`). Question: WHICH existing gscript builder places a node at the TOP-LEVEL diagram whose OUTPUT terminal is BOOLEAN, such that an indicator created from it, `move_in`-ed onto `Diagram #639` and wired to `#10686` t0 `'x .and. y?'`, reads `Is Broken? = False`? Phase A (files only) ranked THREE candidates, all `build_property` (`tools/gscript.py:2194`) ??the only verb in the fleet with a Boolean-BY-CONSTRUCTION output terminal ??headed by `('VI Server:VI', [('291',False),('292',False)])`, already VERIFIED on this machine (`docs/vi-server-ids.json` `_metrics_291_292_VERIFIED_2026-09-16`; terminal table and two successful `create_indicator` calls at `tools/bench/diag_load_vs_editmode.log:11,13-14`). Run under `py tools/bgrun.py --material --max-min 25`, own pre-batch restart (44(e), handles stood at 63,533). ?좑툘 `guard_peer` FORCED a hypothesis review of `diag_s57_typepair.log:33` before this could launch: `archive/peer/2026-09-21-c58-typepair-a1-nonresult.md` (claude/hypothesis opus max + web, **ANSWERED 484 s, `$3.9606`**, `BGRUN END rc=0 after 484s`, log `tools/bench/peer_c58_typepair_a1.log`), verdict **`REFUTED ??the causal half survives; the two load-bearing clauses do not`** ??**RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), disposition written in full, NOTHING IN IT ACTED ON**; the diagnostic was written and AST-checked BEFORE the review was dispatched and was not changed afterwards. No recipe (`tools/recipes/stage_d1_s3a_focus_ind.py` must still not exist at the end, asserted by gate Z3), no new op VI, no new device, no VI run (34(f)), no GUI action, no motor/ASI/camera (rig 議곕┰). No route chosen or recommended; `## NEXT` untouched.
  owner_c57m4: # ??**RELEASED 2026-09-20 23:5x ??cycle 57 material #4, the cycle's SECOND and LAST build act. ONE DIAGNOSTIC under `tools/bench/`, never a recipe: `tools/bench/diag_s57_typepair.{py,log,json}` (AST OK 1151 lines, 36 gate sites, 13/13 guard assertions clear ??`tools/bench/c57d4_astcheck.log`). ??`tools/recipes/stage_d1_s3a_focus_ind.py` exists=False on disk ??reported, never written, never launched.** ?럦 **RUN 2 (`BGRUN END rc=0 after 242s`) IS 35 PASS / 0 FAIL, AND BOTH THINGS THE BRIEF ASKED FOR LANDED.** (1) **A SAVED ARTEFACT AT THE LEGAL POINT, BEFORE ANY WIRING:** `claudeDev\D1_s3a_ind_placed_20260920_234341.vi`, md5 **`0b9a070289a08a22a8843e287b183398`**, **476,209 B**, LV2026 `26 00 80 00` ??`ExecState` **1** at the save point, `allow_broken` False, `gui_save` never called; it reopened **COLD in a fresh LabVIEW instance (own restart, nothing preloaded) at `ExecState` 1** with `owner_of(#23541) = ('Diagram', 639)`. (2) ?럦 **THE MATCHED-TYPE PAIR WIRED CLEAN:** `wire_indicators(IndexArray[20], ['element'] -> ['index'], diagram_index=46)` error column **`''`**, indicator wire **0 ??10990** (a BRANCH: whole-VI `Wire` 1905 ??1905, delta 0), **`ExecState` 1 ??1 across the wiring**, `#10757` **3/3 wired before and after**, `#637` **59 ??59 terminals / 48 ??48 wired** (37(e): increase 0, no tunnel, no border object) ??and the ORDERED second pass (42(b), after the save, idempotent re-connect `#10757` t1 ??`#10407` t2 `'Index of closest\ncal image slice, bead 2'`, `wire_delta` **0**, op error `''`) read **`Is Broken?` = False on wire 10990**. Second artefact saved legally: `claudeDev\D1_s3a_num_ind_20260920_234341.vi`, md5 **`fceaa0a1d068622596842435b830bffe`**, **476,146 B**, LV2026. **The ONE difference from dispatch 3 was the source** (NUMERIC `#10757` t1 `'element'` wire 10990 instead of BOOLEAN `#10686` t0). LIVE indices, nothing cached (34(h)): `diag_index(#639)=46`, `(#536)=0`, `(#686)=19`; `owner_of(#10757)=owner_of(#10686)=('Diagram',639)`; **`#10757`'s own class is `IndexArray`, Traverse index 20 of 47** (`Bundle`/`Unbundle`/`ArraySubset` refused the scan, error 1092, recorded); terminals `[(0,'array',sink,121),(1,'element',SOURCE,10990),(2,'index',sink,10947)]`. 46(a) reproduced exactly: `node_info` 0 ??1, `IndexArray #23486` owner `('TopLevelDiagram',536)`, `create_indicator` ??`ControlTerminal #23541`, census 114 ??115, delete ??`ExecState` 1; label READ off the machine **`'index'`** (hex `696e646578`, no newline, not a duplicate); `move_in(#23541 ??#639)` error `''`, owner `('TopLevelDiagram',536) ??('Diagram',639)`, census 115 ??115, panel rows 115 ??115, **`ExecState` 1 ??1**, ONE junk `Invoke` #23486 purged (PREDICTED RISK (i)), error `''`. ?좑툘 **RUN 1 IS A NON-RESULT, NOT A BUDGET FAILURE:** the first launch (`BGRUN START 23:42:25`) was still alive when the session re-launched, and run 2's own pre-batch restart killed LabVIEW under it ??run 1 died in phase A with `com_error: (-2147023170, ??` / `(-2147023174, 'RPC ??)`, 6 pass / 1 fail (`A1`), saved nothing, and its scratch was removed. ?좑툘 **PHASE J, reported not interpreted: no reader in this fleet returns a TERMINAL's or a CONTROL's data type** ??12 hits, the only representation reader is `OpConstValueN_v1.vi` (`NumericConstant.Representation` 5DCFC00, `docs/toolkit-capabilities.md:59`, `docs/NAMES.md:969`), which reads a numeric CONSTANT; `docs/vi-server-ids.json:42` has `"VI.Create from Data Type": "49D"` (a creator). NOTHING WAS BUILT. Refs **22 opened / 22 closed / 0 live**; handles 63,313 ??30,688 (own pre-batch restart) ??60,291 ??30,695 (the phase-F restart) ??**63,533**. ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged before AND after. No VI run (34(f)), no new op (Pre-decided 2), no new device, no recipe, no GUI action, no motor/ASI/camera, no peer forced (0 failing gates). No route chosen, no plan document edited, `## NEXT` untouched.
  owner_c57m3: # ??**RELEASED 2026-09-20 23:2x ??cycle 57 material #3, the cycle's BUILD act. ONE run of the 2-run budget: `tools/bench/diag_s57_ctmove_wire.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe ??`BGRUN END rc=1 after 123s`, GATES **27 pass / 2 fail** (`P5a`, `P6`).** ??`tools/recipes/stage_d1_s3a_focus_ind.py` **DOES NOT EXIST on disk** (exists=False, mtime=None) ??reported, not written, not launched (guard_cycle would refuse a recipe build this cycle). ?럦 **THE S3a TRANSPORT EXECUTED END TO END FOR THE FIRST TIME, AND EVERY TRANSPORT VERB RETURNED AN EMPTY ERROR COLUMN.** (1) LIVE indices, nothing cached (34(h)): `diag_index(#639) = 46`, `diag_index(#536) = 0`, `diag_index(#686) = 19`, `owner_of(#639) = ('WhileLoop', 637)`, `owner_of(#10686) = ('Diagram', 639)`, `#10686` at Traverse `Function` index **102** of 183. (2) 46(a) REPRODUCED: `node_info` **0 ??1** (`[(0,'Index Array','Index Array')]`), `IndexArray #23486` owner **`('TopLevelDiagram', 536)`**, `create_indicator(Nodes[0].Terminals[2])` ??**`ControlTerminal #23541`**, census **114 ??115**, `delete_object` removed #23486, **ExecState 1** after the delete. (3) **THE LABEL, READ OFF THE MACHINE AND NEVER RETYPED: `'index'`** (utf-8 hex `696e646578`), panel row `{'label':'index','indicator':True,'uid':23525,'is_source':False,'wire':0,'term_err':0,'wire_err':1055}` ??**no newline, not a duplicate** of any existing panel label. ?럦 (4) **`move_in` TOP-LEVEL ??NESTED WORKS ??NEVER TRIED BEFORE:** `move_in(#23541 ??Diagram #639 @ index 46, (120,4000))` error `''`, `owner_of(#23541)` **`('TopLevelDiagram',536)` ??`('Diagram',639)`**, ControlTerminal census **115 ??115**, panel rows **115 ??115**, **ExecState still 1 after the move**. It left ONE junk `Invoke` (uid **23486**, the uid the deleted IndexArray had just released), purged in the same run, error `''` (PREDICTED RISK (i), written before the run). ?뵶 (5) **`wire_indicators` FOUND THE LABEL AT THE NESTED INDEX AND MADE THE CONNECTION, AND THE CONNECTION IS BROKEN:** the target's wire uid went **0 ??10799** (the source's own wire ??a BRANCH; whole-VI `Wire` count **1905 ??1905**, delta 0), but `ExecState` went **1 ??0** and the op raised, error column VERBATIM **`RuntimeError: wire_indicators: target BROKEN after wiring - a source terminal was probably unwired (WI then extends an unrelated wire; revert the target)`** ??while `#10686` t0 `'x .and. y?'` read **3/3 wired before AND after** and `#637` read **59 ??59 terminals / 48 ??48 wired**, i.e. **NO tunnel and NO border object appeared** (37(e) grain, explicit: increase 0). ??(6) ORDERED SECOND PASS (42(b), idempotent re-connect of the EXISTING `#10686` t0 ??`#10407` t0 net, `wire_delta` **0**, op error column `''`): **`Is Broken?` = `True` on wire uid 10799**. ?뵶 (7) **NO ARTEFACT: `ExecState` 0 at the save point ??`g.save()` NOT ATTEMPTED** (`allow_broken` stayed False, `gui_save` never called) ??a legitimate outcome under the brief; the scratch was never saved and was therefore removed from inside the run (`error VERBATIM ''`), so **this cycle left no file to open**. ?좑툘 **TWO `guard_peer` HYPOTHESIS REVIEWS, both ANSWERED, both RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), dispositions written in full, NOTHING IN EITHER ACTED ON:** (a) `archive/peer/2026-09-20-c57-ctowner-5001.md` ??the review cycle 56's `diag_s56_transport3b.log` owed, which BLOCKED this build (claude/hypothesis opus max + web, **ANSWERED 546 s, `$3.8922`**, log `tools/bench/peer_c57_ctowner_5001.log`); verdict **`REFUTED ??the census is sound, the bridge from it to the 5001 is not`** (the 5001 comes from `Wire Indicators.vi` while the diagram-scope mechanism was measured on `Get Controls.vi` via `wire_control`; its alternative is **panel-scope, not diagram-scope**; it proposed a cheaper arm at `diagram_index=0` with **no `move_in`**). ?좑툘 **ORDERING, for the record: `diag_s57_ctmove_wire.py` was written and AST-checked (`tools/bench/c57_astcheck.log`, `AST OK 882 lines, 30 gate sites`, guard assertions ALL CLEAR) BEFORE that review was dispatched, and was NOT changed afterwards** ??the reviewer read the file and criticised it (짠5: "it is not a test of 46(c)"), and the brief's phase list was run unedited. (b) `archive/peer/2026-09-20-c57-transport-typebreak.md` ??the review THIS run's `P5a` owed (claude/hypothesis opus max + web, **ANSWERED 568 s, `$3.7974`**, log `tools/bench/peer_c57_transport_typebreak.log`); verdict **`REFUTED on the load-bearing half`** ??it does not dispute the Boolean/numeric type mismatch (already on disk at `docs/camera-acquisition-facts.md:189-191`) but refuses "therefore the transport is proven", because the run held a saveable artefact at `ExecState 1` right after the move and spent it, `Is Broken?` is calibrated `True` on a two-source wire as well, wire 10799 is `CaseStructure #10407`'s **t0 selector** wire on a structure-border sink (`tools/gscript.py:2415`: an already-wired SINK is not safe), and a wire count can never detect a cut (`docs/cycle27-plan.md:1101-1105`). It also establishes: **no existing verb can create an indicator of a CHOSEN type** (`Terminal.Create Indicator` 6349C02 takes no type argument), and the 5001 story is **not** closed (uid 6 / `'Image'` were never re-attempted). Refs **13 opened / 13 closed / 0 live**; handles 34,159 ??**30,681** (the run's own pre-batch restart, `lv_restart rc=0`, dialogs clear) ??**60,299**. ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? all byte-unchanged before AND after. No VI run (34(f)), no new op (Pre-decided 2), no new device, no recipe, no GUI action, no motor/ASI/camera. No route chosen, no plan document edited, `## NEXT` untouched.
  owner_c56m5_prev: # cycle 56 material #3 finished 2026-09-20 21:4x; the batch did its own pre-batch restart (44(e)) and LabVIEW is UP afterwards at 60,179 handles
  owner_c56m5: # ??**RELEASED 2026-09-20 22:4x ??cycle 56 material #5, the cycle's LAST build act. TWO runs (the failure budget, spent): `tools/bench/diag_s56_transport3.{py,log,json}` ??`BGRUN END rc=1 after 330s`, GATES **21 pass / 7 fail** (`A1`,`A2`,`A3`,`C3`,`C4`,`C5`,`C6`) ??and, after the forced review, `tools/bench/diag_s56_transport3b.{py,log,json}` ??`BGRUN END rc=1 after 78s`, GATES **11 pass / 3 fail** (`E0`,`E3`,`E4`). Both DIAGNOSTICS under `tools/bench/`, never recipes.** ?럦 **PHASE 2 IS THE RESULT: THE TOP-LEVEL HEAD IS HEALTHY AND `create_indicator` WORKS ON THIS VI ??THE EMPTY `Nodes[]` WAS EMPTY, NOT DEAD.** `build_index_array` on the `VI ??Block Diagram` head placed **IndexArray #23486** with `owner 'TopLevelDiagram'`, error column `''`, and `owner_of(#23486)` read **`('TopLevelDiagram', 536)`**; `node_info(max_n=40)` went **0 entries ??1** (`[(0, 'Index Array', 'Index Array')]`) the moment a node existed there; `create_indicator(Nodes[0].Terminals[2])` then produced **ControlTerminal #23541**, census **114 ??115**, error `''`; `ExecState` 1 ??0 (unwired IA inputs) ??**1 again after `delete_object(IndexArray[0])` removed #23486** ??`remove_bad_wires` was NOT needed. Artefact saved legally (`ExecState` 1 ??1, `allow_broken` False, `gui_save` never called): **`claudeDev\DIAG_s56_t3_p2_20260920_221901.vi`, md5 `cbe9ddd5690983fae2919b3027264d4b`, 476,182 B, LV2026 `26 00 80 00`.** So `docs/NAMES.md:476-478`'s IA?뭖reate?뭗elete route EXECUTES on the main VI, and dispatch 3's "`create_indicator` can never reach this VI" reading is **narrowed to a scope limit, not a dead reference**. ?뵶 **BUT THE `wire_indicators` ADDRESSING HYPOTHESIS IS MEASURED DEAD, AND ITS OWN FALSIFIER FIRED: ALL 114 `ControlTerminal`s READ OWNER CLASS `Diagram`, NOT `TopLevelDiagram`** (`diag_s56_transport3b.log:15`, `{'Diagram': 114}` over 114 objects) ??i.e. every pre-existing front-panel terminal sits on a STRUCTURE subdiagram and the top-level diagram holds **zero** of them (the one exception is #23541, which phase 2 had just created there). Run 1 made **0** `wire_indicators` calls because the brief's rule had no resolvable value: **`owner_of(#6) = ('Panel', 3)`** and `diag_index(#3)` ??`ValueError: 3 is not in list`, since `panel_wiring`'s `uid` column is the **PANEL CONTROL's** uid (`tools/gscript.py:849,:859`), not its diagram terminal's. Run 2 then spent 2 of 3 attempts at `diagram_index=0`: **both 5001, VERBATIM `error 5001: LV-Scripting.lvlib:Wire Indicators.vi<ERR> | Control File # Saved not found | <b>Complete call chain:</b> | LV-Scripting.lvlib:Wire Indicators.vi | OpWireInd_v0.vi`** and the same for `Control Image not found`; target wire **0 ??0** both times, whole-VI `Wire` delta **0**, `ExecState` **1 ??1**, `#10686` t0 `'x .and. y?'` **3/3 wired throughout**, `#637` **59 ??59 terminals / 48 ??48 wired** (no tunnel or border object, 37(e)). ??**LIVE CONFIRMATION OF A FILES-ONLY CLAIM: `Traverse Diagram[0] = {'class': 'TopLevelDiagram', 'uid': 536, 'pos': (-17474, 102), 'owner': ''}` and `diag_index(#536) = 0`** ??dispatch 4 had this only by elimination. ??Two ordered-second-pass `Is Broken?` reads (42(b), AFTER each save so the artefacts survive the known ExecState perturbation): **False** on wire 10799 both times, op error column `''`, `wire_delta` **0**. ?뵶 **PHASE 3 ??`copy_by_index('Local'[0] uid 2991, duplicate=True, expect_uid=2991)` REACHED THE OP AND RAISED PAST the "nothing was copied" check: `RuntimeError: copy_by_index: Target still broken after finish (ExecState 0) - not saved`** (`gscript.py:1548-1551`), so an object WAS added to the fixture Target and nothing was written back to the scratch. The PREDICTED RISK in the script's docstring is the cause on the table: the protocol byte-substitutes `claudeDev\NIScriptingExamples\Moving Objects\Test - Moving Objects {Source,Target}.vi` with 476,182-B copies of a main-VI scratch and loads them from THAT folder, where ~94 subVI relative paths do not resolve ??its `ExecState == 1` precondition may be unsatisfiable for a main-VI-sized target there. **Both fixtures are LEFT holding md5 `cbe9ddd5690983fae2919b3027264d4b`** (the documented protocol restores them at the START of the next copy, `gscript.py:1466-1469`; repairing them under a possibly-loaded VI is what needs a restart) ??RECORDED, not repaired. ??**C7, the pure read judgement asked for: NO generic property READER exists in this fleet** ??every reader is a purpose-built op with its IDs hard-wired (`OpReport_v3`, `OpPanelWiring_v0`, `OpFPLabels_v0`, `OpNodeInfo_v0`, `OpNodeTerms_v0`, `OpOwnerChain_v1`, `OpConnectNested_v1`), `gscript` has only the WRITERS `set_index_mode`/`set_auto_error_handling`/`set_node_label` plus `build_property` (:2194) which CREATES a node whose value could only be read by RUNNING the VI (34(f) forbids), and **ID 6355400 appears 0 times in `docs/vi-server-ids.json` and 0 times in `tools/gscript.py`** ??so the binding of the 8 `Local`s (uids 2143, 2991, 3097, 3160, 4277, 11574, 16942, 25805, all owner `Diagram`, count 8 ??8) CANNOT be read today without a new op VI. ??**ARTEFACTS ON DISK (rule: a step is not done until it has left a file):** `DIAG_s56_t3_p1_20260920_221901.vi` md5 `1286f1c8ee34feb866f38dda387874bf` 475,726 B 쨌 **`DIAG_s56_t3_p2_20260920_221901.vi` `cbe9ddd5690983fae2919b3027264d4b` 476,182 B (the phase-2 result)** 쨌 `DIAG_s56_t3b_p1_20260920_223816.vi` `bbbc2850b5b1899ac10c6438dfc3891d` 475,727 B, all LV2026 `26 00 80 00`; `DIAG_s56_t3_p3_20260920_221901.vi` exists as an unmodified copy of the p2 artefact (phase 3 wrote nothing back). ??**THE OWED CLEANUP IS DONE from inside the run** ??both `DIAG_s56_{wireind,localvar}_20260920_214454.vi` removed on the first attempt, `error VERBATIM ''`. ?좑툘 `guard_peer` FORCED a hypothesis review of run 1's failed prediction before run 2 could launch: **`archive/peer/2026-09-20-c56-panelowner-addressing.md`** (claude/hypothesis, opus effort max + web, **ANSWERED 520 s, `$3.4378`**, in 20 / out 40,441 / cache-create 186,008 / cache-read 1,078,610, 22 turns; `BGRUN END rc=0 after 521s`, log `tools/bench/peer_c56_panelowner_addressing.log`) ??**RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), disposition written in full; NOTHING IN IT WAS ACTED ON** (run 2 was written and AST-checked BEFORE the review was dispatched, its `E0` census included, and was left unchanged ??including the `'Image'` probe the review calls worthless). Its own falsifier is the one the machine then fired. Refs 26/26/0 live and 13/13/0 live; handles 30,939 ??30,684 (own restart) ??54,367, then 34,508 ??30,691 (own restart) ??**63,517**. ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged after BOTH runs. No VI run (34(f)), no new op (Pre-decided 2), no new device, no recipe, no GUI action, no motor/ASI/camera. `## NEXT` untouched.
  owner_c56m4: # ??**RELEASED 2026-09-20 22:0x ??cycle 56 material #4, the cycle's LAST material act. LabVIEW WAS NEVER TOUCHED: no `.vi` opened, no COM call, no `gscript` import, no GUI, no motor/ASI/camera, no VI run (34(f)), no new op (Pre-decided 2), no new device, no recipe. Refs 0 opened / 0 closed / 0 live; handles neither read nor changed. FILES ONLY + one peer dispatch.** ??**J1 ??THE DISCRIMINATING TEST IS ANSWERED FROM FILES ALONE, AND THE MAIN VI'S TOP-LEVEL DIAGRAM NOW HAS A UID: `tools/bench/diag_c56_topdiagram_files.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe ??`BGRUN END rc=0 after 0s`, GATES 7 pass / 0 fail.** ?럦 **`Diagram #536` IS THE TOP-LEVEL DIAGRAM, AND IT IS TRAVERSE INDEX 0.** Identified by ELIMINATION across two caches that nobody had joined before: `diagram_tree_main.json` has exactly **ONE** of its 170 rows with an empty owner ??idx **0**, `uids [22963]` = net_map's own junk node, **0 real nodes** (`J1`/`J2` PASS) ??and the owner census accounts for every other row by a structure (`CaseStructure 76 쨌 FlatSequenceFrame 57 쨌 ForLoop 17 쨌 Sequence 11 쨌 EventStructure 5 쨌 WhileLoop 3`, and the structures census 3/17/37/4/2 matches frame-for-frame); `diagram_hierarchy.json` (129 resolved / 41 unresolved = 170) carries the diagram **UIDs**, and its ONLY row with `owner_class ''` is **`{"diagram_uid": 536, "owner_class": "", "why": "no structure of that class"}`** ??the same single row, from the same `g.report(WORK,"Diagram")` ordering. This matches `docs/cycle27-plan.md:1033`'s `TopLevelDiagram #536` independently. ?뵶 **`Diagram #686` IS A FLAT-SEQUENCE FRAME, NOT THE TOP LEVEL, AND ITS UPWARD WALK DIES IN ONE HOP.** Its owner CLASS reads `FlatSequenceFrame` in both files; its owner UID is **UNKNOWN** ??`diagram_hierarchy.json` leaves it `unresolved` (*"ambiguous: nearest 1098, runner-up 1310"*, a POSITION heuristic, `build_diagram_hierarchy.py:13-16,97`), and the direct read was already measured dead: `diag_ownerchain_hop.log:7` gave owner uid **0** + `error 1055` + an EMPTY cast-class echo (`docs/cycle12-plan.md:91`), with `FlatSequenceFrame` refused as a Traverse class, `error 1092` (`build_diagram_hierarchy_run3.log:8`). So the top of the chain is an UNIDENTIFIABLE FlatSequenceFrame and `#536` is never reached by measurement. ??**`Diagram #639` = Traverse index 43** (not 46 ??46 is `{"diagram_uid": 32067, "owner_class": "EventStructure", "owner_uid": 10153}` in the ORIGINAL's cache; the log's "46" was re-resolved LIVE on the S2 scratch, whose 3 added loops shift the Traverse order), `owner_class WhileLoop`, **`owner_uid 637`** ??and `#637` sits on tree idx **19** = `#686` (`build_d1_routeb_v0.log:53`), so the full chain is **`#639 ??WhileLoop #637 ??Diagram #686 ??FlatSequenceFrame #? ??STOP`**. `#10686` and `#3191` both live on tree idx **43**. ?뵶 **THE H1/H2 VERDICT: THE FILES SUPPORT H1 ONLY FOR A NARROWER STATEMENT THAN DISPATCH 3 DREW, AND THEY CANNOT SEPARATE H1 FROM H2 FOR THE CREATE LADDER.** What IS twice-measured: Traverse `Diagram[0]` = `#536` enumerates **0 nodes** through TWO different ops on a Traverse-obtained reference ??`main_vi_netmap.json` idx 0 = `{"owner":"","nodes":{},"wires":{}}` (OpNetInfo_v1) and `main_vi_nodeterms.json` idx 0 = 0 nodes (OpNodeTerms, `J8` PASS) ??i.e. a head INDEPENDENT of the `VI ??Block Diagram` head H2 accuses. What is NOT established: (1) `node_info` does **NOT** call `ensure_loaded` (`tools/gscript.py:2462-2481`) while `create_indicator` DOES (`:2386`), so `node_info == []` is not a same-conditions proxy for the create ladder; (2) `error 1055` is documented BOTH as the out-of-range signature (`docs/NAMES.md:986` "until error 1055 = past the end") AND as the invalid-reference signature (`:181`, `:488`, `:854`, `:961`), so the watchdog screenshots cannot tell an empty `Nodes[]` from a dead head; (3) a **third** reading survives both: the outermost FlatSequence structures must sit on `#536`, yet `FlatSequence` is absent from every census (Traverse `error 1092`) and appears on no diagram's node list ??so "0 nodes" may mean `Nodes[]` cannot ENUMERATE FlatSequence on this VI, which would make `#536` a normal diagram whose only contents are invisible to our readers. Readings consistent with ALL THREE: `node_info == []`, `node_terms_uid(??0,i) ??node_uid 0` for i=0,1,2, the 20 횞 1055, and idx 0's single junk uid. ?뵶 **AND `diagram_tree_main.json`'s `"0"` IS NEITHER A REAL DIAGRAM NOR A PLACEHOLDER ??IT IS AN INDEX WITH ITS IDENTITY THROWN AWAY.** The sweeps DECIDE nothing: `diagram_tree_main.py:51-52` takes `g.report(WORK,"Diagram")` in Traverse order and keeps **only** `d["owner"]`, discarding each object's own `class` (which would have read `TopLevelDiagram`) and `uid` (`J3`/`J6` PASS); `:67` reads diagram `k` by INDEX; `:76` stores `{owner, uids}`; the string "top" appears **once in the whole pipeline**, as a cosmetic print fallback for an empty owner at `sweep_nodeterms_main.py:79` (`TREE[...]['owner'] or 'top'`), and `J4` confirms **0** occurrences of any top-level identification in `diagram_tree_main.py`. `net_map`'s docstring claim *"0 = top level"* (`tools/gscript.py:2505`) is an ASSUMPTION written into a docstring; this dispatch is the first thing on disk that CORROBORATES it, and it does so by elimination, not by reading a class. ??**J2 ??THE MANDATORY REVIEW THE FAILING LOG OWED IS ARCHIVED AND DISPOSED IN FULL: `archive/peer/2026-09-20-c56-transport-verbs-unreachable.md`** (claude / hypothesis, opus effort max + web, **ANSWERED 600 s, `$4.1928`**, in 30 / out 46,445 / cache-create 201,481 / cache-read 1,868,318, 31 turns; `BGRUN END rc=0 after 600s`, log `tools/bench/peer_c56_transport_unreachable.log`), so `guard_peer`'s block over `diag_s56_transport2.log` (first failing gate `L1`) is LIFTED. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)); NOTHING WAS ACTED ON** ??no gate redesigned, no measurement rebuilt, nothing re-run, no op built, no `diagram_index` changed, `gscript.py` untouched. Its verdict in one line: **"the claim is not supported by the run that produced it"** ??`L1`/`L2` made **0 calls** and merely restate Pre-decided 2, so half the claim is policy not measurement; `docs/NAMES.md:476-478` already records the fleet's own answer to an empty top-level `Nodes[]` (`build_index_array` ??`create_control` on its `index` terminal ??delete the IA; proven again at `docs/stage2-assembly-step-b.md:49-50`) and it was never tried; `docs/toolkit-capabilities.md:274` is about creating panel objects *from nothing*, `tools/gscript.py:1406-1412` says in writing that the style-ring blocker was REMOVED on 2026-09-01, and `docs/stage2-assembly-step-b.md:34` ??cited by the diagnostic as a measurement ??is a peer review's OPINION. Verbs it names that the claim missed: **`copy_into`** (`:1399-1445`, by label, built to transplant an `error out` INDICATOR), **`copy_by_index`** (`:1479-1558`, `GObject.Move` with `duplicate = True` at `:1527`, class a FREE STRING at `:1526`, so `cls='Local'` is legal today against the 8 Locals), `move_in` (`tools/recipes/build_d1_v0.py:318`), `owner_of` (`:338`), `diag_index` (`:357`), `move_out` (`tools/gscript.py:2677-2689`), `build_invoke`/`build_property` (both already take `diagram_index`, `:2159`/`:2194`). On (ii) it redirects the route: `Control` ??**Create:Local Variable, ID 6331C02** (LV2018+, no scripting-licence auth) makes the Local **born bound**, so `Local.Control Name` 6355400 need never be written. On the 5001 it gives a cheaper cause: NI reserves 5000??999 for user-defined codes, `Indicator Names` are looked up **on `Diagram in`** (`archive/2026-08-29-status-sweep-opexitloop-opwireind.md:33-35`, fed from `diagram_index` at `tools/gscript.py:1787-1788`), and the call passed the diagram owning the **SOURCE**, not the indicator's terminal ??ranked above label-string mismatch (six prior 5001s on this VI, *"2 names carry newlines"*, still open at `docs/d1-build-plan.md:762`) and above caption/tab qualification (weakened: `panel_wiring` is non-recursive, `tools/gscript.py:834`, yet listed the row). Its alternative framing: **"an addressing failure, not a capability gap"**, plus a less charitable second reading ??the run was built to confirm a conclusion its own brief contained. Its three discriminating tests are recorded in the archive file's `## What was done with it` and **NOT RUN**. ?좑툘 **J3 ??THE OWED DELETE WAS REFUSED BY THE PERMISSION LAYER, ONE ATTEMPT, NO WORKAROUND:** `Remove-Item` on `claudeDev\DIAG_s56_wireind_20260920_214454.vi` (byte-identical to S2) returned *"was blocked. For security, Claude Code may only access files in the allowed working directories for this session"* ??so it is **STILL OWED** and can only be removed from inside a script run that already holds a LabVIEW batch. ORIGINAL / `D1_s1_copy.vi` / `D1_s2_loops.vi` not read and not touched (no `.vi` was opened at all). `## NEXT` untouched.
  owner_c56m3: # ??**RELEASED 2026-09-20 21:4x ??cycle 56 material #3. ONE batch, ONE run: `tools/bench/diag_s56_transport2.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe ??`BGRUN END rc=1 after 102s` (rc=1 = the inner-failure flag on 5 gates, not a crash), GATES 13 pass / 5 fail (`L1`, `L2`, `I0`, `I1`, `I2b`).** ??**THE SWALLOW IS REPAIRED AND THE REPAIR IS PROVEN.** `gscript.create_control:2360` and `create_indicator:2385` no longer swallow the modal-dialog `RuntimeError` ??the two `try/except RuntimeError: if "modal dialog" not in str(e): raise` blocks are replaced by a bare `_run(vi)` plus the measured reason, mirroring `delete_object:2264-2272`; nothing else in `gscript.py` was touched. Gate **P1 PASS**: the same call that returned an empty list with `exception None` 20 times in dispatch 2 now raises `RuntimeError: run blocked behind a modal dialog (dismissed by watchdog after 8s); screenshot(s): %TEMP%\gscript_dialog_1789908387.png` (log `:46-47`). ?뵶 **TEST I ??`create_indicator` CANNOT EVER REACH THIS VI, AND THE REASON IS ONE NUMBER: THE TOP-LEVEL DIAGRAM HOLDS ZERO NODES.** `g.node_info(target, max_n=40)` ??which walks the SAME `VI ??Block Diagram ??Nodes[]` ladder `OpCreateIndicator_v0` uses ??returned **`[]`**, and `node_terms_uid(target, 0, i)` read `node_uid 0` (= index out of range) for i = 0, 1, 2 (log `:42-44`). The whole main VI lives inside a flat sequence: `diagram_tree_main.json` diagram `"0"` (owner `''`) holds only net_map's junk uid 22963, all 626 real nodes sit on the 169 structure-owned diagrams. So `docs/NAMES.md:278-282`'s "TOP-LEVEL `Nodes[]` only" is not a narrow scope on this target, it is an EMPTY one ??`create_indicator`/`create_control`/`connect_terminals`/`connect_ctl` have no addressable node here at all, and dispatch 2's 20 횞 error 1055 "Object reference is invalid" is exactly that. ?뵶 **AND THE DOCUMENTED REMEDY REFUSED TOO, for a NEW reason worth recording: `wire_indicators` returned error `5001: LV-Scripting.lvlib:Wire Indicators.vi<ERR> | Control File # Saved not found`** (log `:56`) on `Function[102]` (`#10686`, read live: Traverse index 102 of 183 `Function` members, t0 `'x .and. y?'` carrying wire **10799**, `I2a` PASS) ??indicator `'File # Saved'` (uid 6, the first `wire 0` indicator row read live, panel row 7) with `diagram_index=46` (= `Diagram #639`; `Diagram #686` reads 19). The indicator EXISTS ??`panel_wiring` read it on the same scratch in the same phase ??so 5001 is a LOOKUP failure inside erdosmiller's `Wire Indicators.vi`, not a missing control. Its wire stayed **0 ??0** (`I2b` FAIL), `#10686` wired terminals **3 ??3**, and `#637` **59 ??59 terminals / 48 ??48 wired** (`I2d` PASS ??no tunnel or border object appeared). ??**THE ORDERED SECOND PASS ANSWERED:** `Is Broken?` = **False** on wire **10799**, `wire_delta` **0**, op error column `''`, read by an IDEMPOTENT re-connect of the EXISTING `#10686` t0 ??`#10407` t0 connection (a ControlTerminal is not in `Nodes[]`, so no 6371004 carrier can address the indicator end ??the same NET was read instead). ?좑툘 `ExecState` **1 ??1** across the wiring, then **0** after that read ??`docs/NAMES.md:912-918`'s perturbation, so Test I's save was correctly NOT ATTEMPTED and its scratch `claudeDev\DIAG_s56_wireind_20260920_214454.vi` is byte-identical to S2 (deleting it needs a script run, so it is OWED). ?뵶 **TEST L ??BOTH PEER ROUTES ARE UNREACHABLE WITHOUT A NEW OP VI, AND 0 CALLS WERE MADE.** L1: **108** `Op*.vi` in `claudeDev`, **0** gscript wrappers write a `style` control, and `docs/stage2-assembly-step-b.md:34` already measured why ??*"a `New VI Object` op cannot be parameterised: style is a typed ring, unretargetable by scripting"* (`docs/toolkit-capabilities.md:274` says the same). L2: no op carries an Invoke node for `Control ??Create:Local Variable`, Python cannot pass a LabVIEW Control reference into a method, and the binding writes `Local.Control Name` 6355400 / `Local.Write?` 6355401 have no generic property WRITER (gscript has only `set_index_mode`, `set_auto_error_handling`, `set_node_label`). `build_invoke` would build either one ??that is a NEW OP VI, which Pre-decided 2 forbids. ??**WHAT TEST L DID ESTABLISH:** the bind target's label was READ OFF THE MACHINE, not retyped ??ControlTerminal uid **34200** reads `'current image number'` (indicator, wire 3747); and the VI already carries **8 `Local` objects** (uids 2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805, all owner `Diagram`), unchanged 8 ??8 (`L3` PASS). ??**OPENABLE ARTEFACT, saved legally** (`ExecState` **1 ??1**, `allow_broken` False, `gui_save` never called): `claudeDev\DIAG_s56_localvar_20260920_214454.vi`, md5 **`d41e17f34a7250c5fa4f493a0f49eafb`**, **475,729 B**, LV2026 bytes `26 00 80 00`. ??**DISPATCH 2'S OWED CLEANUP IS DONE** ??both `DIAG_s3aind_20260920_204915_{A-nomove,B-movedin}.vi` removed on the first attempt from inside the run, `error VERBATIM ''`. Handles 60,122 ??**30,694** (the run's own restart, `lv_restart rc=0`, dialogs clear) ??**60,179** (??9,500 added in 102 s while `ref_counts` read **16 opened / 16 closed / 0 live** ??the client-side gate still cannot see it). ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? all byte-unchanged before AND after (`Z1` PASS). No VI run (34(f)), no new op, no new device, no motor/ASI/camera, no GUI action, no route chosen, no peer dispatched (none was forced: no build followed). `## NEXT` untouched.
  owner_c56m2: # ??**RELEASED 2026-09-20 21:3x ??cycle 56 material #2, the cycle's BUILD act: `tools/bench/diag_s3a_ind_transport.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe. ONE run: `BGRUN TIMEOUT killed after 1502s (limit 25.0 min)`, GATES 6 pass / 2 fail (`G2`/`G3`, route A).** ?뵶 **THE HEADLINE ??NEITHER TRANSPORT ROUTE WAS EVER REACHED, AND THE MACHINE HAD ALREADY PHOTOGRAPHED WHY.** `create_indicator` returned an EMPTY ControlTerminal list on **20 consecutive calls** on route A (and on route B until the deadline), each with `exception None`. Reading two of the run's **113** watchdog screenshots settles it: `%TEMP%\gscript_dialog_1789905146.png` shows **`OpCreateIndicator_v0.vi`'s own block diagram** ??ladder `vi path ??VI.`**`TopLvlDiag`**`??Nodes[] ??IA(index) ??Node.Terms[] ??IA(index 2) ??Term.Create Indicator` ??under *"**Error 1055** occurred at Property Node in OpCreateIndicator_v0.vi 쨌 LabVIEW: (Hex 0x41F) **Object reference is invalid**"*; `??1789905137.png` shows the SAME 1055 naming **`OpFPLabels_v0.vi`** (the diagnostic's own `fp_labels`, called twice per attempt). **They were ERROR DIALOGS, not silent declines ??`gscript.create_indicator:2396-2400` swallows them because the message contains "modal dialog".** ?뵶 **AND IT WAS ALREADY DOCUMENTED: `docs/NAMES.md:278-282` says verbatim that `connect_terminals`/`connect_ctl`/`create_control`/`create_indicator` "address the TOP-LEVEL diagram's `Nodes[]` only", names the 8-s out-of-range dialog as the signature, and gives the remedy ??`wire_indicators(??node_class='Function', diagram_index=frame)`, whose "Traverse-class indices span all diagrams"; `:474-475` repeats it.** The run re-derived a documented fact for 1502 s and a $4.94 review; **NOT read before launching** ??recorded against this cycle. ??**WHAT WAS MEASURED AND STANDS:** `owner_of(#10686) = ('Diagram', 639)` on both scratches (class `Function`, label `'And'`, Nodes[] index **25** of a **73**-node walk, t0 `'x .and. y?'` a SOURCE carrying wire **10799** ??G0/G1 PASS on both routes); `#637` reads **59 terminals, 48 wired**; census before/after identical (Diagram 173 쨌 WhileLoop 6 쨌 SubVI 97 쨌 LoopTunnel 135 쨌 Wire 1905 쨌 ControlTerminal **114 ??114**); `ExecState` **1** before, never changed. ?뵶 **M1, FILES ONLY AND CONCLUSIVE ??THE BRIEF'S PREMISE ABOUT `#3191` IS FALSE.** `#3191` is a **CaseStructure** (`diagram_tree_main.json[structures]`), so it has NO function name; all FOUR of its terminals are `is_source=False` ??t0 `''` w3050 (selector, sourced by `#3057 'x = 0?'`), t1 `''` w3268, t2 `'current image number'` w3747, t3 `'LastBufferNumber'` w3356. **t2 is a SINK, not an output**: wire 3747's ONLY source in the whole census is **`#6810` t10 `'current image number'`** = subVI **`get buff image-lost frames.vi`**, the camera acquisition node (`docs/NAMES.md:80-87`), and the panel indicator is panel row 103, terminal 3747 / control **34200** (`docs/main-vi-panel-map.md:383`). Wire **3268** has **0 sources** in the census (sink-only at `#376` t7, `#1114` t0, `#2136` t3, `#3191` t1, `#10068` t3, `#29240` t3 ??it arrives from a shift register/border object, matching `docs/frame-loop-wire-graph.md:161`). So the indicator is the camera BUFFER NUMBER per acquisition, not a function of the counter at `#3191` t1; whether it strictly changes every iteration needs a RUN, which 34(f) forbids. ?좑툘 **NO ARTEFACT: `g.save()` was never reached** (no wiring was ever attempted), `allow_broken` stayed False, `gui_save` never called; the two dated scratches `claudeDev\DIAG_s3aind_20260920_204915_{A-nomove,B-movedin}.vi` are **byte-identical to S2** (`6ff19497??, 475,707 B) ??an attempted delete was refused by the permission layer (outside the working directory), so their cleanup is OWED. ?좑툘 **ATTEMPT 2 WAS WRITTEN AND THEN DISARMED, NOT RUN** ??`tools/bench/diag_s3a_ind_transport2.py` carries a NEVER-RUN banner: its repaired candidate list is drawn from `Diagram #639`, which the screenshot proves `create_indicator` cannot address, so launching it would be a third grind (failure budget = 2). ?좑툘 `guard_peer` forced a hypothesis review of the failed prediction ??`archive/peer/2026-09-20-c56-createind-silent.md` (claude/hypothesis opus max, **ANSWERED 644 s, $4.9446**), **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), disposition written in full**; `gscript.py` was NOT patched and `tunnel_indicator` was NOT substituted. ??**M4, the MANDATORY external search: `archive/peer/2026-09-20-c56-localvar-scripting.md`** (claude/fact, fable low thin + web, **ANSWERED 107 s, $1.5883**) ??creation **style string `Local Variable`** (ID 2061) vs **traverse class `Local`**; a second route `Control` ??`Create:Local Variable` (bound at creation, LV2018+); binding property **`Local.Control Name`, ID 6355400, String, R/W**; direction **`Local.Write?`, ID 6355401, Boolean**; nested diagrams **YES**, passing the frame's own `Diagram` reference; no version caveat found either way. **RECORDED AS FACTS, UNVERIFIED on this machine, acted on in no way.** Handles 34,163 ??**30,971** (own restart) ??LabVIEW left UP after the kill; ORIGINAL `2a78e17c?? 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? all **byte-unchanged, verified after the kill**. No VI run (34(f)), no new op (Pre-decided 2), no new device, no motor/ASI/camera, no GUI action. `## NEXT` untouched.
  owner_c55m4: # ??**RELEASED 2026-09-20 09:1x ??cycle 55 material #4, the CLOSING ACT: the 5th OUTCOME REVIEW, which was DUE. LabVIEW WAS NEVER TOUCHED: no `.vi` opened, no COM call, no GUI action, no motor/ASI/camera; `gscript` never imported; refs 0 opened / 0 closed / 0 live; handles neither read nor changed (still 60,591).** ONE batch: `py tools/bgrun.py --material --max-min 25 --log tools/bench/outcome_review_c55.log -- py -u tools/outcome_review.py` ??**`BGRUN END rc=0 after 200s`**. ??**ROUTING IS THE 2026-09-18 TRIAL, NOT codex ??`outcome_review.py:191-192` dispatches `-Agent claude -Role outcome -Kind fact`, `peer.ps1:61` puts that role at fable / medium + web and `:486` adds `--safe-mode`; nothing was patched.** Exchange **ANSWERED (199 s), `$3.2236`, in 14 / out 13,751 / cache-create 104,582 / cache-read 444,292, 16 turns** ??`archive/peer/2026-09-20-outcome-review-20260920.md` (its `## What was done with it` at `:168-170` is still `(Claude fills in)` ??**disposing it is a JUDGEMENT act, deliberately not done here**). ?뵶 **SIX `OUTCOME-VIOLATION` LINES, verbatim and in order: `goal-requirement-not-advanced` 쨌 `product-not-runnable` 쨌 `tooling-over-delivery` 쨌 `decision-starved` 쨌 `ordering-stale` 쨌 `measurement-without-product`** (`scope-inflation` explicitly NOT flagged). Its answers, one line each: **(1) the user can RUN nothing today that they could not at the 5th review** ??the interval's two saved files are banned from running by 34(f) and the deliverable line (`Track_v6_CPU_core_v0.vi` / `Track_v6_CPU_queue_v0.vi`) is unchanged for the third review running; **(2) requirements 1, 2.2, 2.3, 2.4, 2.5 and 3 have produced nothing runnable since the project began** ??req 1 NOT MOVED for the fourth consecutive review, req 2.1 owes nothing; **(3) the cost ratio is "Not defensible"** (+17 op VIs, +9 recipes, +33 peer exchanges, +7 retrospectives, +0 benchmark rows, +0 runnable deliverables in 0.6 days), naming as skippable the STATUS relocation ritual (*"`git init` is one command"*), cycle 55 material #3 in its entirety, the retrospective-disposal cadence and the second queue trial census; **(4) ordering is stale ??the standing NEXT is EXECUTED and exhausted, and it argues the next act is a STAGE (the minimal loop set CLOSED UNDER ITS WIRE SOURCES), not another diagnostic**; **(5) OPEN 53, requirement 1 and OPEN 46 are decision-starved because STATUS labels them "NOT blockers"; it also JUDGED the OPEN 32 rider ??D0 closes as a delivered HARNESS, not as a closed product gap**; **(6) the experiment test still answers THE ORIGINAL VI, the sixth such verdict in a row**; (7) its termination list is 5 items ending *"or the re-plan conversation with the user is owed in full"*. ?좑툘 **RECORDED, NEITHER ACCEPTED NOR REJECTED (Pre-decided 41(b)) ??nothing was redesigned, rebuilt or re-run on it, and an `OUTCOME-VIOLATION` is never answered by building a device (CLAUDE.md 짠5; user 2026-09-18 08:53).** ??**`guard_cycle.py:563-574` IS NOW SATISFIED** ??`py tools/outcome_review.py --due` read **`DUE: 7 cycle retrospectives ??** before and **`not due: 0/5 cycles, 0.0/7 days since 2026-09-20-outcome-review-20260920.md`** (rc=0) after; `py tools/violations.py --due` prints nothing (0 slugs awaiting), so neither gate in that block blocks the next recipe build. `## NEXT` and `docs/cycle27-plan.md` untouched; no new op, no recipe, no device.
  owner_c55m3: # ??**RELEASED 2026-09-20 09:0x ??cycle 55 material #3, SECOND ACT + owed bookkeeping. LabVIEW WAS NEVER TOUCHED: no `.vi` opened, no COM call, no GUI action, no motor/ASI/camera; `gscript` never imported; refs 0 opened / 0 closed / 0 live. Handles NOT read and NOT changed (still 60,591).** `tools/bench/reverse_census_walk.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe. **ONE run: `BGRUN END rc=1 after 1s`, GATES 26 pass / 1 fail.** ?럦 **JOB 1 ??THE REVERSE WALK IS CLEAN AND THE 635-vs-626 DISCREPANCY IS FULLY MECHANICAL.** Reverse (netmap ??nodeterms): the ONLY node uid in `main_vi_netmap.json` absent from `main_vi_nodeterms.json` is **22963**; forward (nodeterms ??netmap): **0** absent, so cycle 54's one-directional claim is reproduced independently. `(diagram, uid)` pairs: netmap-only **9**, every one uid 22963 (diagrams 23, 80, 118, 136, 137, 146, 149, 166, 167); nodeterms-only **0**. Totals 635 / 626 entries, 627 / 626 distinct uids, same 170 diagram keys. **MECHANISM, read out of the files:** uid 22963 is `net_map`'s own junk Invoke node ??the netmap holds it on 9 diagrams (635 = 626 + 9) and **`diagram_tree_main.json` holds it on 11 OTHER, DISJOINT diagrams (0, 3, 5, 31, 53, 69, 75, 84, 128, 143, 151), ALWAYS as the LAST `Nodes[]` index** (637 = 626 + 11); `sweep_nodeterms_main.py:56-59` reads UID 0 there, logs "node index out of range" and **BREAKS**, which is why nodeterms stops at 626 and why its 11 `mismatches` rows are all uid 22963. Class filters and diagram `"0"` contribute nothing (diagram `"0"` holds 0 nodes in both). The three on-disk 635 assertions are `docs/instrument-libraries.md:103`, `docs/main-vi-panel-map.md:401`, `tools/bench/analyse_netmap_cache.py:3` (+ a 4th, GENERATED: `tools/bench/analyse_nodeterms_main.py:89` writes the panel-map heading, so that one is not an independent count). ?뵶 **THE RED QUESTION ANSWERED ??NO: `tools/bench/c53_row_class.json` keys NO uid in the disagreeing set.** Its 8 node uids `[48, 3447, 3529, 3560, 10407, 10686, 10757, 12589]` all resolve in nodeterms, `22963` does not occur anywhere in the file's text, and 22963 lives on none of the diagrams (19, 43) the table covers. ?럦 **JOB 2 ??`walk()` DID NOT TRUNCATE on `Diagram #686`, and now it is MEASURED.** Truncation mechanism read out of the source: TWO stops, `build_opstopfromnode_v0.py:132` `for n in range(limit)` and `:134-135` `if not u: break`; the caller `diag_queue_typetest_control.py:300` passed **`limit=200`**, so the cap was not binding. `walk_n_nodes` **24** == census length 24 == nodeterms d19's **21** nodes + the **3** While loops stage S2 added to that diagram ??`#23032` loop a / `#10170` loop b / `#23041` loop c, each named with `owner Diagram #686` at `tools/bench/stage_d1_s2_loops.log:47,61,75`, 1 terminal each. **SHORTFALL = 0** (nodeterms ??census is empty), terminals **139 = 136 + 3**, and **0 per-node terminal-count differences on all 21 shared nodes**. Completeness is established for THIS diagram only ??both stops are still live and a diagram with more than `limit` nodes would still truncate silently. ??**JOB 3 ??THE OWED RULE-4 RELOCATION IS DONE.** `owner_c54m3` / `owner_c54m2` / `owner_c54m` moved **byte-identically by a copy, never retyped** ??`archive/2026-09-20-status-cycle54-relocate.md` 짠1?벬? (13,678 B); sha256 captured from STATUS BEFORE the write (`0722af1aed52?? 3569 B 쨌 `579a80a8412c?? 3807 B 쨌 `7f1d51c7f4be?? 3410 B) and re-verified in the archive AFTER the STATUS rewrite, 3/3. STATUS **81 ??79 lines**, one `lock_relocated_c54:` pointer left. Cycle-55 keys and the whole `## NEXT` section untouched (both verified). ?뵶 **BUT cycle 53's `## NEXT` HAS NO VERBATIM SOURCE ON DISK** ??STATUS's NEXT is rewritten in place each cycle, the only archived `## NEXT` outside peer transcripts is cycle 50's, and this is not a git repo; 짠4 of the new file RECORDS that rather than reconstructing it. ?좑툘 **THE ONE RETAINED FAIL, AND IT IS MINE: gate `R14 every uid c53_row_class.json keys is present in nodeterms` predicted 8/8 and measured `8/12 present; missing [4256, 4274, 4334, 4344]`** (`tools/bench/reverse_census_walk.log:49`) ??I had folded `c53_row_class.json`'s `sr_pairs` SHIFT-REGISTER uids into a node-uid gate. A 41(c) demotion to a FACT line was drafted **and REVERTED UNRUN**; the `.py` on disk is the code that produced the log, and **nothing was re-run** (a second FAIL would have charged the next cycle another mandatory review). **Demote-vs-keep-as-a-required-12/12-gate is a DESIGN decision and is left to judgement.** ?좑툘 `guard_peer` forced the review: `archive/peer/2026-09-20-c55-reverse-census-r14.md` (claude/hypothesis opus max, **ANSWERED, `rc=0 after 402s`, $2.9744**), **RECORDED, NEITHER ACCEPTED NOR REJECTED, disposition written in full** (Pre-decided 41(b)) ??its points (the 12/12 gate over `nodeterms ??main_vi_shiftregs_v1.json` was available; `gscript.py:947-948` is the `tunnels()` docstring and does not establish "not a Node"; the SRs' OUTER terminals ARE in the census under `#637` t11/t10; and "c53_row_class is unaffected" does not follow because the table is a TERMINAL table and `#637` is the VI's single `max_terms=40` cap site, shortfall 31) are **for judgement to dispose, not this session.** ??**JOB 4 bookkeeping, reported not acted on:** `py tools/violations.py` **0 slugs awaiting** (largest: `repeated-failure-class` 17, `device-failed` 13, `inference-over-measurement` 11, all answered `no-device` under the user's 2026-09-18 08:53 suspension); **`py tools/outcome_review.py --due` says DUE ??`7 cycle retrospectives since 2026-09-19-outcome-review-20260919.md (every 5)`, i.e. ~1 day but 7 cycles, so `guard_cycle.py:563-574` WILL BLOCK the next RECIPE build until one is run and annotated ??NOT RUN HERE**; `py tools/doc_lint.py` went **`2 fail, 4 warn, 4 pass` ??`1 fail, 4 warn, 5 pass`** because L2's single dangling citation (`STATUS.md:76 ??archive/2026-09-20-status-cycle54-relocate.md`) was closed by the relocation ??the remaining FAIL is L6 (48 blank dispositions, 39 pre-2026-09-15 `legacy`), and L2b `docs/NAMES.md:1022` still points past the end of `docs/toolkit-capabilities.md`. ??**ONE DOC EDIT, exactly as the brief ordered:** `CLAUDE.md` "When a diagnosis is GUESSED twice" ??`docs/NAMES.md:888-897` ??**`:902-911`** (verified: 884-898 is the case-structure property-ID block; `Wire.Is Broken?` 6371004 is at 902-911). `docs/cycle27-plan.md:1374` carries the same wrong citation and was **LEFT for judgement**. ORIGINAL / `D1_s1_copy.vi` / `D1_s2_loops.vi` not read and not touched (no `.vi` was opened at all). No new op, no new device, no recipe (Pre-decided 2).
  owner_c55m2: # ??**RELEASED 2026-09-20 08:40 ??cycle 55 material #2, FIRST ACT second attempt (Pre-decided 40(c)+(d)): `tools/bench/diag_typectl_v2.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe. `BGRUN END rc=0 after 88s`, GATES 19 pass / 0 fail (REPORTED, not required ??the 34(j)/37(e) pattern).** Attempt 1's FIXED sink rule was WITHDRAWN by judgement; the SINKS were GIVEN ??`#2048 'Array Subset'` Nodes[7] t4 `'index'` / t5 `'length'`, re-verified LIVE on both legs as bare (`wire 0`), NAMED, non-source. Writer `OpConnectNested_v1` same-diagram (`connect_terminals` `:2407` / `connect2` `:2633` both need a TOP-LEVEL end and `Diagram #686` is not top level); `owner_of` read **`('Diagram', 686)` for #250, #2048 and #8486 on BOTH legs**. ?뵶 **THE READING ??THE TWO DISCRIMINATORS DISAGREE, AND NOBODY HERE INTERPRETS THAT.** Leg **M (matched)** `#8486` t0 `'x+1'` ??`#2048` t4: op error column `''`, sink wire **23519**, `wire_delta` **0**, `ExecState` **1 ??0**, ORDERED `Is Broken?` **False**. Leg **X (mismatched)** `#250` t1 `'IMAQdx Session'` ??the SAME `#2048` t4: op error column `''`, sink wire **6910**, `wire_delta` **0**, `ExecState` **1 ??0**, ORDERED `Is Broken?` **True**. So `Is Broken?` separated the pair (False/True) while `ExecState` did **not** (0 on both). ?좑툘 Both connections were **BRANCHES of the donor's existing net, not new wires** ??each sink wire uid equals that source terminal's pre-existing wire (`#8486` t0 = 23519, `#250` t1 = 6910) and the `Wire` count stayed **1905 ??1905** on both legs. ?좑툘 **The pass-1 (writing-pass) `Is Broken?` read `False` on BOTH legs** ??the `docs/NAMES.md:905-911` ordering trap is real and the ORDERED pass-2 idempotent re-connect (`wire_delta 0`) is what produced the discriminating value. ?좑툘 Cited as `docs/NAMES.md:902-911`; the plan's `:888-897` is WRONG (that range is the case-structure property-ID block). ?뵶 **NO ARTEFACT WAS SAVED: both legs ended at `ExecState` 0, so `g.save()` was NOT ATTEMPTED** (`allow_broken` stayed False, `gui_save` never called) ??an expected, legitimate outcome under this brief; the scratch on disk is byte-identical to S2. ?좑툘 **DEVIATION, REPORTED: the two legs' scratch file names collided** (`DIAG_typectl_v2_20260920_083912_A_t4.vi` ??the template omits the leg name), so leg X deleted and re-copied the same path rather than using a second file. **It did NOT contaminate**: leg X's T3 gate re-verified md5 `6ff19497?? at creation, its `ExecState` BEFORE read **1** (leg M had left 0) and its live walk read `#2048` t4 bare again (leg M had left wire 23519), so leg X ran on a fresh load of S2. The t5 substitution rule did not trigger (matched leg wired at t4 with an empty error column). Refs **17 opened / 17 closed / 0 live**; handles 34,166 ??30,689 (own restart) ??**60,591**, i.e. ??9,900 added in 88 s ??**attempt 1's ??2,700-per-run growth RECURS** and `ref_counts` still cannot see it. ORIGINAL `2a78e17c?? / 473,317 B, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? all byte-unchanged. NO QUEUE NODE CREATED (40(d) ??`queue_node` never imported), no VI run (34(f)), no new op (Pre-decided 2), no motor/ASI/camera/GUI. No peer review was forced (no failed prediction: 19/0).
  owner_c55m1: # ??**RELEASED 2026-09-20 08:32 ??cycle 55 material, FIRST ACT (Pre-decided 40(c)+(d)): `tools/bench/diag_queue_typetest_control.{py,log,json}`, a DIAGNOSTIC under `tools/bench/`, never a recipe. TWO runs, both in the SAME append-mode log.** ?뵶 **THE HEADLINE: THE CONTROL PAIR WAS NEVER ATTEMPTED, because the brief's FIXED sink rule has NO CANDIDATE ??all five numeric-arithmetic nodes it names expose ZERO bare named input terminals on `Diagram #686`** (`#7201 'Multiply'` Nodes[1] 쨌 `#8486 'Increment'` Nodes[0] 쨌 `#9179 'Decrement'` Nodes[14] 쨌 `#25091 'Multiply'` Nodes[19] 쨌 `#25149 'Subtract'` Nodes[20]). **`Is Broken?` therefore has NO reading this cycle, matched or mismatched ??the instrument is still unvalidated and 40(d)'s question is still open.** ??**RUN 2 (`BGRUN END rc=0 after 78s`, 12 pass / 0 fail) LEFT THE MATERIAL THE NEXT SINK RULE NEEDS: the FULL terminal census of `Diagram #686` ??24 nodes, 139 terminals, every `(i, name, is_source, wire)` triple ??in `tools/bench/diag_queue_typetest_control.json` under `diagram_686_terminal_census`.** From it, the ONLY nodes on that diagram with a bare NAMED input are `#250 'Property Node'` t2 쨌 `#637 'While Loop'` t44 쨌 `#2048 'Array Subset'` t4,t5 쨌 `#25380 'While Loop'` t6,t8; the only bare UNNAMED inputs are on `#6384 'save N xyz traces.vi'` t0,t2,t3,t4. **No sink is chosen here ??that is a DESIGN decision and Pre-decided 40's closing line reserves it for judgement.** ??Everything else resolved: both SOURCES found on the live walk ??`#8486` Nodes[0] t0 `'x+1'` (wire 23519) and `#250` Nodes[3] t1 `'IMAQdx Session'` (wire 6910) ??and `owner_of` read **`('Diagram', 686)` for all six nodes**, so the same-diagram requirement is MEASURED, not inferred. ??**OPENABLE ARTEFACT, saved legally** (`ExecState` **1 ??1**, `allow_broken` False, `gui_save` never called): `claudeDev\DIAG_qtypectl_20260920_083038.vi`, md5 **`dc6b96d175a77cd7571ae4ed9ac18bf2`**, **475,741 B**, LV2026 bytes `26 00 80 00`. Census 173/6/97/17/135/**Wire 1905 unchanged** (nothing was wired). Refs 6 opened / 6 closed / **0 live**; ORIGINAL `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged after both runs. NO QUEUE NODE CREATED (40(d) ??`queue_node` never called), no VI run (34(f)), no new op (Pre-decided 2), no motor/ASI/camera/GUI. ?좑툘 **RUN 1 (`rc=1 after 78s`, 9/2) retained two FAILs; run 2 demoted them to recordings under 41(c)** after the measurement falsified their premise, and the only other change was adding the census. ?좑툘 **HANDLES: 34,207 ??30,678 (own restart) ??63,416 in 78 s, and again 34,160 ??30,684 ??63,422 ????2,700 added per 78-second run while `ref_counts` read 6/6/0 live. The client-side ref gate CANNOT see this.** ?좑툘 A mandatory `guard_peer` review was forced by run 1 ??`archive/peer/2026-09-20-c55-sinkrule-no-bare-input.md` (claude/hypothesis opus max, **ANSWERED, `rc=0 after 511s`**), **RECORDED NOT ACCEPTED, disposition written in full** (Pre-decided 41(b)). Its eight findings ??chiefly that `gscript.py:2412` already records *"Type mismatches make a broken wire"*, that "0 bare inputs" was ENTAILED by `ExecState == 1` so the rule could not succeed on any non-broken VI, that the rule never required a **type-constrained** sink, that a bare typed sink can be MADE with existing ops (`build_index_array` `:2322`, `drop_subvi` `:1225`, `build_property` `:2194`), and that `connect_terminals`' `ExecState 1 ??0` may be the less noisy instrument than `Is Broken?` ??are **for judgement to dispose, not this session.**
  owner_c55m1_run1: # ?뵏 **RUN 1 detail, superseded by the key above:** `BGRUN END rc=1 after 78s`, 9 pass / 2 fail, and THE CONTROL PAIR WAS NEVER ATTEMPTED.** ?뵶 **THE READING: the brief's FIXED sink rule has NO CANDIDATE on this target ??all five numeric-arithmetic nodes it names expose ZERO bare named input terminals on `Diagram #686`** (`#7201 'Multiply'` Nodes[1] 쨌 `#8486 'Increment'` Nodes[0] 쨌 `#9179 'Decrement'` Nodes[14] 쨌 `#25091 'Multiply'` Nodes[19] 쨌 `#25149 'Subtract'` Nodes[20], each `0 bare named input(s)`), because their inputs are live and already wired ??corroborated OFF-LINE against the ORIGINAL's own census, `tools/bench/main_vi_nodeterms.json:6256-6295`: `#7201` t1 `'y'` wire 8385, t2 `'x'` wire 8518, both non-zero. ??Everything ELSE the brief asked for resolved: both SOURCES found on the live walk (24 nodes) ??`#8486` Nodes[0] t0 `'x+1'` (wire 23519) and `#250 'Property Node'` Nodes[3] t1 `'IMAQdx Session'` (wire 6910) ??and `owner_of` read **`('Diagram', 686)` for all six nodes**, so the same-diagram requirement holds by direct measurement. Scratch `claudeDev\DIAG_qtypectl_20260920_081715.vi` SAVED LEGALLY at `ExecState` **1 ??1**, `g.save` returned **475,741 B**, no exception (`allow_broken` False, `gui_save` never called). Refs 6/6/**0 live**. ?좑툘 handles 34,207 ??30,678 (own restart) ??**63,416** ??one 78-second run added ??2,700. ORIGINAL `2a78e17c??, `D1_s1_copy.vi` `3e3d23ce??, `D1_s2_loops.vi` `6ff19497?? byte-unchanged. `guard_peer` then forced a hypothesis review of the failed prediction (slug `c55-sinkrule-no-bare-input`) ??**RECORDED, never accepted** (Pre-decided 41(b)). Run 2 adds the FULL `Diagram #686` terminal census (pure measurement) and demotes G2/G3 to recordings under 41(c); **no alternative sink is chosen ??that is judgement's.**
  lock_relocated_c54: # ?뵷 **THREE LOCK KEYS RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle54-relocate.md` 짠1?벬?** ??`owner_c54m3` (the queue trial census, 18 donors / 18 ACCEPTED), `owner_c54m2` (the files-only netmap replay + the cycle-51..53 relocation) and `owner_c54m` (the S3 focus trial, 43/0, `ExecState` 0, save refused). Nothing deleted, only moved; each key's sha256 was verified against STATUS before AND after the write. ?좑툘 **Cycle 53's `## NEXT` section has NO verbatim source on disk** ??STATUS's NEXT is rewritten in place every cycle and no snapshot of cycle 53's was archived, so 짠4 of that file RECORDS the gap rather than reconstructing it.
  lock_relocated_c51_c53: # ?뵷 **FIVE LOCK KEYS RELOCATED VERBATIM (rule 4) ??`archive/2026-09-20-status-cycle53-relocate.md` 짠1?벬?** ??`owner_c53` (cycle 53: S3 withdrawn, the netmap truncation measured), `owner_c52m3` / `owner_c52m2` / `owner_c52m1` (cycle 52's three material rounds) and `owner_c51m2` (cycle 51's S2 build, released). Nothing deleted, only moved; the relocation STATUS's NEXT recorded as owed.
  owner_c51m1: # ??**RELEASED 2026-09-20 03:4x ??LabVIEW WAS NEVER TOUCHED: no `.vi` opened, no COM call, no GUI action, no motor/ASI/camera.** Cycle 51 material, D1 stage S2 (Pre-decided 34) WRITTEN BUT **NOT LAUNCHED**: `tools/recipes/stage_d1_s2_loops.py`, **311 lines, sha256 `7eb482beab051629d0e8b8c7bf7e0a3c51750aafbf6c1eee658d625c3583d993`**, AST OK (`tools/bench/c51_astcheck.log`, 19 gate sites) ??three While loops on `Diagram #686` at (2600,2600)/(2600,3400)/(2600,4200), each scaffolded `OpCreateEqual_v0`(operand BY NAME `#8486 'x+1'`) ??`OpStopFromNode_v0`, ONE `g.save()`, no `move_in`/queue/re-wiring/new op, no VI run. ?뵶 **THE PRIOR-ART LAUNCH GATE REFUSES IT**: `archive/peer/2026-09-20-priorart-d1-s2-loops.md` (ANSWERED, opus/high, **$4.7775, 530 s**, log `tools/bench/priorart_d1-s2-loops.log`) returned `PRIOR-ART: contradicted` + `PRIOR-ART: unread-evidence` ??(A3) the imported `LOOP_END_REF` readback drops `OpLoopEndRef_v0`'s `err`/`errs` columns that Pre-decided 14 (`docs/cycle27-plan.md:147-150`) requires be reported UNREAD, and (A4) the stage gates SubVI by class COUNT where 29(g) (`docs/cycle27-plan.md:629-641`) makes the ORIGINAL's SubVI **table** the acceptance reference (the built FATAL instrument is `stage_d1_s1.py:182-188`/`:377-400`). One review round only; **the `REFUTED:`/`FIXED:` release is the judgement session's call, not a material session's.** ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after (`tools/bench/c51_facts.log`); S1 artefact `3e3d23ce?? 474202 B untouched; `claudeDev\D1_s2_loops.vi` does **NOT** exist; refs opened 0 / closed 0 / live 0.
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
?럦 **CYCLE 59 (runner cycle 46) DELIVERED S3a AS ONE FILE ??THE STAGE IS CLOSED.** `claudeDev\D1_s3a_focus_ind.vi`, md5 `eef91c1d91f16b034707e4d1285ca8cb`, 476,172 B, LV2026: the recipe ran **64 gates pass / 0 fail** (`tools/bench/cycle59_s3a_recipe.log`, `BGRUN END rc=0 after 596s`), `ExecState` **1** at the save AND on the Z0 **COLD** reopen in a fresh LabVIEW, **BOTH** ControlTerminals `owner_of ('Diagram',639)` (numeric #23541 `'index'`, Boolean #23576 `'Automatic Error Handling'`), census **116**, both ORDERED `Is Broken?` **False** (wires 10990 and 10799), refs 60/60/**0 live**, all three originals byte-unchanged. `tools/recipes/stage_d1_s3a_focus_ind.py` sha256 `1986626FB6F16CD0?? identical before and after ??**not one byte edited**, so the stop record still matches the reviewed bytes; no hook refused the launch, `CYCLE_GUARD_OFF` never set. Verification **STRUCTURAL**, never functional (34(f)). Details: `docs/cycle27-plan.md` **Pre-decided 49(a)**.
?뵶 **FIRST ACT ??S3b-L0, THE ONE OP VI THE NEXT STAGE CANNOT START WITHOUT: build `OpCreateLocal_v0.vi` exactly as `docs/cycle27-plan.md` Pre-decided 49(d) specifies it, and self-test it ON A SCRATCH COPY ??never on `D1_s3a_focus_ind.vi`.** Why it is needed at all is MEASURED, not assumed (49(b)): **nothing in this fleet creates a Local Variable** ??`local` appears once in `tools/gscript.py`, in a comment (`:830`); the only vehicle for `Control ??Create:Local Variable` **6331C02** is `build_invoke` (`tools/gscript.py:2159`), whose `reference` input is deliberately UNWIRED (`:2164-2166`); no `Op*.vi` in `claudeDev` has `Local` in its name; and `vi.lib\Erdos Miller\LV-Scripting\Create*.vi` is 50 files with no local-variable creator. The external fact answer (`archive/peer/2026-09-21-s3b-local-variable-route.md`, `$1.3397`) adds the shape that closes `build_invoke` for good: **6331C02 takes NO input parameters and returns only a Local refnum, so the Control instance it is invoked on IS the binding.** The op therefore walks `Panel.Controls[]` **6348801** ??`Control.Label` **6332005** ??`Text.Text`, matches the label, and Invokes on **that live reference**; 20 consecutive calls, handles flat 짹100, every reference closed. Authorisation is **46(k)** (`docs/cycle27-plan.md:1697-1705`): Pre-decided 2 forbids a further **process device**, not an op VI ??cite it by its words. The `New VI Object` style **2061** + `Local.Control Name` **6355400** route is the FALLBACK only, and the self-test merely REPORTS whether those two unverified IDs resolve.
?뵶 **SECOND ACT ??S3b-M1, then M2 if M1 leaves a file** (`docs/cycle27-plan.md` **Pre-decided 49(e)**, which RE-CUTS 45(f) into five saved sub-steps and **deliberately inverts its order ??locals BEFORE the node moves, reasoning in 49(f)**): **M1** from `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d??), cold ??create the TWO locals, one per new indicator (`'index'`, `'Automatic Error Handling'`), left UNWIRED ??save `claudeDev\D1_s3b_m1_locals_<stamp>.vi`; pass: `Local` census **8 ??10**, both bound labels read off the machine, `ExecState` 1. ?좑툘 **Whether an unwired Local leaves the VI legal is to be MEASURED and REPORTED, not assumed** ??if `ExecState` is 0 there, M1 folds into M2, and that folding is the next judgement session's call, not a material session's. **M2** wires the two locals into `#10407` t0/t2 ??save; pass: `ExecState` 1, `Is Broken?` False on both new wires (ordered pass, after the save), `#10407` +2 wired terminals, `#637` counts unchanged (no tunnel, no border object). M3 (the five node moves into `#23032`'s body `Diagram #23058`) and M4 (frame-counter SR + `Wait (ms)` 1 ??`claudeDev\D1_s3_loop15.vi`) follow in 49(e); **M3's re-split trigger is written in advance at 49(h)** ??end at `ExecState` 0 with no file and the next cycle cuts it node-with-its-rows, never a retry under a new name. 38(g) stays banned. ?좑툘 A RECIPE build is refused in any cycle that has already produced a build log (48(n)), so L0/M1 run as diagnostics under `tools/bench/`, as every S3a sub-step did.
?좑툘 Restart LabVIEW before the first batch. No motor, no camera, no new process device. The retrospective is the LAST act, under bgrun, in the background (the runner re-runs one that dies at session exit). `git commit` at cycle close.
??**THE CYCLE-59 RETROSPECTIVE RAN AND IS DISPOSED ??`VIOLATION: none`, the first one in the record** (`archive/peer/2026-09-21-retrospective-cycle59.md`, fable/medium, `ANSWERED 229s`, `$3.7437`, `BGRUN END rc=0 after 230s`; *"the shortest, cheapest, and most productive cycle in the record"*, AUDIT PASS on every line, 0 failure markers). **No `docs/violation-decisions.md` block is owed for cycle 59**; cycle 58's `device-failed` is answered at **2026-09-21 02:34 (cycle 59)**, `DECISION: no-device`, its claim REFUTED by this cycle's own 64/0 launch. Both gates that refused cycle 58 **PERMITTED correctly here on the first attempt** ??the half of their behaviour nobody had observed.
?뵶 **THREE THINGS THE NEXT SESSION OWES, NONE OF THEM BLOCKING THE BUILD:** (1) **`git commit` for cycle 59 was NOT made** ??`git` is not on this non-interactive session's allowlist and both `git add -A` and `git commit` came back *"requires approval"*, so the cycle's files (`STATUS.md`, `docs/cycle27-plan.md` Pre-decided 49, `docs/violation-decisions.md`, both disposed retrospectives, `tools/bench/cycle59_s3a_recipe.log`) are on disk and UNCOMMITTED; commit them with the next cycle's close. (2) **One-line repair to `tools/retrospective.py`, material work:** its prompt names a per-cycle plan file by cycle number (for this cycle, a `docs/cycle`-N-`plan.md` spelling that has never existed) and `audit_cycle`'s C7 silently fell back to the frontmatter-`current` plan ??resolve the plan by `status: current`, never by cycle number. A repair to an existing device, so the 2026-09-18 08:53 order does not bar it. (3) ?좑툘 **FOR THE USER, a runner event nobody would learn by reading STATUS otherwise:** a **FIREFIGHTER cycle (fable/low) was triggered at 01:52:56** against the `retro:repeated-failure-class` block (`tools/bench/cycle_46.log:1,62-63`) and was **abandoned with no `BGRUN END` line** when a fresh runner started at 01:55:01 (`tools/bench/cycle_runner_main_20260921a.log:1`), superseded by the opus/max session that ran this cycle. ??3 min lost, nothing produced or damaged, and the trigger is moot ??that slug was decided **no-device** at 01:24 and cycle 59 recurred no failure at all.
**Unchanged, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none; `background VIs_COPY` (94 files) untouched.
?넅 **ONE THING FOR THE USER, COSMETIC ONLY (Pre-decided 49(g)):** S3a's two new panel indicators carry the labels LabVIEW derived from their carriers ??**`'index'`** and **`'Automatic Error Handling'`** ??and the second one is misleading on a tracking Boolean. Nothing in this fleet can rename a front-panel control or indicator (measured cycle 58), so a rename means a second new op against `Control.Label` **6332005**. **DECISION: the labels STAY and no renamer is built** ??a label changes no computation (rule 1a untouched), local variables bind by label, and both names are measured non-duplicate and newline-free, so S3b works as-is. Renaming them by hand in the editor is seconds for the user; say the word and the writer is a one-cycle build.
## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled for this session, so — correctly, per AGENTS.md rule 2 — the review **is** my answer. No file was created or edited; no `.vi` was opened; no LabVIEW, peer or lock was touched.

---

# PRIOR-ART REVIEW — cycle-start · `docs/cycle27-plan.md` Pre-decided 50 + 51

**Verdict: NOT novel. 7 findings.**

Under review: build `claudeDev\OpLocalName_v0.vi`, a reader for a Local Variable's binding, decomposed into L1 (read which connection is broken) → L2 (repair + save) → L3 (validate against the 8 pre-existing Locals) → L4 (create + read back), with S3b's folded M1+M2 gated on that readback (50(i)).

**Headline: the binding is already readable with a built verb, and all eight answers L3 would produce are on disk in an ACTIVE doc, measured 2026-09-14.**

---

## PART A — THE DIRECTION

### A1 · SETTLED ALREADY — the project chose the terminal-name route and *explicitly parked* `Local.Control Name`

`archive/peer/2026-09-14-nodeterms-full-sweep-plan.md:14`, the plan review's own disposition, verbatim:

> "(d) Traverse class 'Local' counted first … **the terminal-name rule for locals is recorded as OBSERVED; 'Local.Control Name' noted as the identity route if a cast ever becomes available**"

Both routes were on the table seven days ago. One was taken and produced an answer; 6355400 was parked as a *conditional future* option. Pre-decided 50(c)/51 re-open the parked branch without citing either the decision or the route that was taken.

### A3 · CONTRADICTED — the plan's blocker claim against an active doc

| | |
|---|---|
| `docs/cycle27-plan.md` **50(c)** | "**the fleet's inability to read a binding is the blocker** … so cycle 60's deliverable became the reader" |
| `docs/main-vi-panel-map.md:405` | "**A local-variable node's single terminal is NAMED after its control** — an observed rule (it held on every local below and on all seven globals…). **`Is Source?` TRUE = the local is READ, FALSE = WRITTEN.**" |

Both active. The second is not a stray note: it heads a machine-generated block (`:399` `<!-- locals-section:begin -->`, regenerated by `tools/bench/analyse_nodeterms_main.py:29`).

### A4 · UNREAD EVIDENCE — `docs/main-vi-panel-map.md:401-416`

Heading `:401` — "*Local variables and `Value` property nodes — measured 2026-09-14 (`OpNodeTerms_v0` sweep of all 635 nodes)*". Table `:409-416`:

| uid | control (terminal name) | direction |
|---:|---|---|
| 2991 | `Total Lost Frames` | WRITE |
| 4277 | `File # Saved` | WRITE |
| 11574 | `Focus Pos (Track)` | WRITE |
| 3160 | `Rot pos (deg)` | READ |
| 3097 | `Trans Pos (mm)` | READ |
| 2143 | `Total Lost Frames` | WRITE |
| 16942 | `Picture` | WRITE |
| 25805 | `Color table` | READ |

Raw source re-verified in this review: `tools/bench/main_vi_nodeterms.json:11-28` (#2991 → `"name": "Total Lost Frames"`, `is_source false`), `:30513-30530` (#16942 → `"Picture"`), `:44020-44037` (#25805 → `"Color table"`, `is_source true`). The rule is stated independently at `docs/NAMES.md:335`. The names are real panel objects: `docs/main-vi-panel-map.md:281` (`Total Lost Frames`, control 421) · `:349` (`Color table`) · `:363` (`Picture`).

Why it was missed is worth naming, because it is a near-miss rather than carelessness: cycle 60 used `node_labels` (`Node.Label` 6359001, `tools/gscript.py:588-594`) — the node's **own** label, a `.vi` file name for all eight. The adjacent verb `node_terms` (`Node.Terms[]` → terminal name) is the one that answers. The forced hypothesis review hardened the blind spot instead of catching it: its own source note, `archive/peer/2026-09-21-c60-l0-readback-none.md:140`, says `Local` "*does appear in `Diagram.Nodes[]` — **the reader reaches it and still cannot answer**" — true of `node_labels`, false of `node_terms`.

### A2 · REFUTED ALREADY — the *construction class* L1/L2 re-enter has failed 6 times and never once succeeded

"Splice a property chain into an existing op VI by hand, every wiring gate passes, end at `ExecState` 0, save nothing":

- **S0 close-reference op, ×4** — `docs/cycle27-plan.md` Pre-decided 25: "*post-wiring `ExecState 0` on every repaired op stub, replicated ×4 in fresh instances with every wiring gate PASSING*" (`tools/bench/build_s0_closeref_v3.log` 87/5; `…v1.log` 41/2). Never solved; S0 closed by measuring its premise away (27/28), not by fixing the construction.
- **L0 localname, ×2** — `tools/bench/diag_s3b_l0_localname_run2.log`, `…_v2.log`, both `ARTEFACTS ON DISK: []` (50(j)).

The **additive-on-a-donor** route, by contrast, has shipped five saved `ExecState`-1 ops: `docs/toolkit-capabilities.md:62`, `:63`, `:66`, `:68`, `:70`. This does not condemn 51 — 51 *is* the decomposition the user's 2026-09-19 rule 3 demands — but the sub-steps should **port** a proven sequence, not discover one.

---

## PART B — THE ARTIFACT

### B1 · ALREADY BUILT — `gscript.node_terms` returns the bound control name **and** the direction

`tools/gscript.py:870` `node_terms(target, diagram_index, node_index)` → `[{i, name, is_source, wire, …}]` in one op run; `:925` `node_terms_uid` adds the node's uid. Built by `tools/recipes/build_opnodeterms_v0.py` from donor `OpNetInfo_v1` with the junk-dropping creator deleted — "*0 junk per call*". `docs/toolkit-capabilities.md:535-537` records it as reading "*every terminal of every `Nodes[]` node with direction and wire*", and the node-class census names `Local` among them.

No cast, no seed, no TMSC, no new op. `is_source` supplies the direction `Local.Write?` 6355401 would have been built to read.

### B4 · ALREADY MEASURED — L3's pass criterion is met 8/8

51(c)'s criterion is "*at least one non-empty string that is NOT a `.vi` file name*". The table above returns eight, each cross-checked against the panel map.

The one thing genuinely **not** measured — and it is a *read*, not a build: whether the rule holds for a **newly created** Local. L0 created 21 and never called `node_terms` on one (`tools/bench/diag_s3b_l0_createlocal.log:66-69` uses `owner_of` and `node_labels` only; `:139` "BOUND LABEL None"). A new Local is born on `TopLevelDiagram #536` (`:67`), whose `Nodes[]` was measured empty but **not dead** — 0 → 1 the moment a node was placed (46(a)). So L3+L4 together reduce to: create the local, then one `node_terms(target, diag_index(#536), n)`.

### B2 · ALREADY FAILED — and the step it died at is absent from the proven recipe

Two things the record already says about *why*, neither of which L1 is aimed at:

1. **#683 is the donor's own load-bearing `Diagram` cast.** `tools/recipes/build_opnodelabels_v0.py:11-12`: "*DONOR: OpNetInfo_v1 … Traverse 'Diagram' by `index` → IA → **TMSC → Diagram → PN Nodes[]***". Attempt 2 re-pointed that cast at `Local`, cut its output wire 645, and re-fed the orphaned `Nodes[]` node #235 from a new control — three re-plumbings of a live chain in one ungated pass.
2. `docs/toolkit-capabilities.md:93-94` already states the constraint: "*A seed casts exactly its class … **so one op per concrete class***" — the fleet's answer is a *separate* cast op per class (`OpLoopCast_v0`, `OpWhileCast_v0`), not a re-seeded shared one.

### B3 · HELPER EXISTS — the ordered, gated seed construction is on disk

`tools/recipes/build_oploopcast_v0.py:12-27` (summary `docs/toolkit-capabilities.md:84-97`), steps 3–7 verbatim:

```
3  drop Create For Loop.vi; the ForLoop-typed OUTPUT chosen by name
4  create_control on that terminal -> seed control label L        new control
5  delete the Create For Loop node (+RBW); L still on the panel   ExecState 1
6  delete wire W (Wire index by uid)                              ExecState 0 or 1
7  wire_control([L] -> TMSC 'target class')                       ExecState 1
```

Four differences from attempt 2:

- **Step 5 deletes the node the seed came from before the TMSC is touched**, gating `ExecState 1` there. Attempt 2 kept `#1025` alive and deleted only its wire.
- **Step 6 PREDICTS `ExecState 0 or 1`** — an intermediate 0 at the wire delete is *expected*. 50(l)/51 treat exactly that reading as a mystery to hunt wire-by-wire.
- **Step 7 is the recovery gate** — one re-plumbing, then a gate. Attempt 2 did the seed re-wire *and* the cast-output re-plumbing before re-reading.
- The seed comes off a node **dropped for the purpose and then deleted**, leaving no live consumer to satisfy.

Also unnamed by L1 and required by it: **an `Is Broken?` read costs a re-connect.** `docs/NAMES.md:912-918` — the readout is ordered after the Invoke, so "*the only way to make it run is to perform `Terminal.Connect Wire`*", idempotently. L1's seed wire is sourced by a front-panel `ControlTerminal`, which is **not in `Nodes[]`** (measured seven times, `tools/bench/build_d1_routeb_v{1..7}_run*.log:162/163/179`, restated in STATUS `owner_c58m3`), so `OpConnectNested_v1` cannot address it. The only writer whose source need not be a node is **`OpConnectFromWire_v0`** (`docs/toolkit-capabilities.md:70`: source = `UID 3` wire uid + `index 7` terminal). L1 names no op; without that one it cannot take its reading at all.

---

## What this does not claim

Nothing here forbids `OpLocalName_v0`. 6355400 is the *authoritative* property; the terminal name is "*an observed rule … not an NI contract*" (`docs/main-vi-panel-map.md:405`) — n = 8 locals + 7 globals, zero counterexamples on disk. But the gate 50(i) actually asks for — catching a binding that silently resolved to the **wrong control**, a rule-1a hazard invisible to `Is Broken?`, which checks type — is satisfied by a census that prints the bound control's name. That census exists, and costs one op call.

```
PRIOR-ART: settled-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: refuted-already
PRIOR-ART: already-built
PRIOR-ART: already-measured
PRIOR-ART: helper-exists
```

## Sources

(extract from answer)

## What was done with it

Disposed by the cycle-60 (attempt 2) judgement session, 2026-09-21. **All seven findings are ACCEPTED. This
review found that the instrument the cycle was building already existed, and it changed the work inside the same
cycle.** No stop record was armed (explicit `--no-recipe`; there is no recipe and none was created), so nothing
here is a release — these are dispositions of record.

FIXED: b1-already-built - `docs/cycle27-plan.md`:51 - Pre-decided 51 is rewritten to WITHDRAW L1/L2/L3 and the
whole `OpLocalName_v0` / TMSC route, because `gscript.node_terms` (`tools/gscript.py:870`) and `node_terms_uid`
(`:925`) already read a Local's binding: the node's single terminal is NAMED after its bound control, with
`is_source` giving READ vs WRITTEN. The cycle's remaining dispatch is a READ with that verb, not a build.

FIXED: a4-unread-evidence - `docs/cycle27-plan.md`:51 - L3 ("validate the reader against the 8 ground-truth
Locals") is withdrawn as already answered: `docs/main-vi-panel-map.md:401-416` tabulates all eight bindings
(2991 `Total Lost Frames` W · 4277 `File # Saved` W · 11574 `Focus Pos (Track)` W · 3160 `Rot pos (deg)` R ·
3097 `Trans Pos (mm)` R · 2143 `Total Lost Frames` W · 16942 `Picture` W · 25805 `Color table` R), re-verified in
`tools/bench/main_vi_nodeterms.json`. The miss is named exactly: cycle 60 reached for `node_labels`
(`tools/gscript.py:588-594`) and never for `node_terms`, and the hypothesis review that examined the failure
attacked only the `node_labels` framing, so it hardened the error instead of catching it.

FIXED: a3-contradicted - `docs/cycle27-plan.md`:51 - 50(c)'s sentence *"the fleet's inability to read a binding is
the blocker"* is WRONG as written and is corrected in place; `docs/main-vi-panel-map.md:405` has said since
2026-09-14 that a local-variable node's terminal is named after its control. 50(c)'s other half — that
`node_labels` cannot answer the question — stands and is unaffected.

FIXED: a1-settled-already - `docs/cycle27-plan.md`:51 - `archive/peer/2026-09-14-nodeterms-full-sweep-plan.md:14`
already took the terminal-name route and parked `Local.Control Name` as *"the identity route if a cast ever
becomes available"*. 50/51 reopened the parked branch citing neither document. The parking is reinstated: 6355400
is now explicitly the FALLBACK, not the path.

ACCEPTED, RECORDED AS A STANDING LESSON, NOT ACTED ON THIS CYCLE: **a2-refuted-already** — splicing a property
chain into an EXISTING op has failed 6 times and succeeded 0 (S0 ×4, Pre-decided 25 and
`tools/bench/build_s0_closeref_v3.log` 87/5; L0 ×2, this cycle), while additive-on-a-donor has shipped five saved
ops (`docs/toolkit-capabilities.md:62,:63,:66,:68,:70`). The review is explicit that this does not condemn 51, and
it does not: 51 is withdrawn for a different and better reason. But it explains both of this cycle's failures at
once and belongs in the plan as a rule the next builder reads.
**b2-already-failed** — `#683` is the donor `OpNodeLabels_v0`'s OWN load-bearing `Diagram` cast
(`tools/recipes/build_opnodelabels_v0.py:11-12`), and `docs/toolkit-capabilities.md:93-94` states that *"a seed
casts exactly its class … one op per concrete class"*. Attempt 2 re-plumbed a cast the donor needs, for a class it
was never meant to serve — a defect independent of the `ExecState` 0 it was chasing.
**b3-helper-exists** — the ordered, gated seed already exists as a recipe
(`tools/recipes/build_oploopcast_v0.py:12-27`, summarised `docs/toolkit-capabilities.md:84-97`), with four
differences from attempt 2 (delete the seed node before touching the TMSC; predict `ExecState 0 or 1` rather than
assert 1; one re-plumbing then a gate). Not acted on because the cast route is withdrawn; it is the shape to reuse
**if** the fallback in the next paragraph is ever needed.

**THE ONE THING KEPT ALIVE, ON THE REVIEW'S OWN CAVEAT.** It states plainly that nothing forbids
`OpLocalName_v0`, that **6355400 is the authoritative property**, and that the terminal-name rule is *"observed …
not an NI contract"* — n = 8 Locals + 7 Globals, 0 counterexamples. So the terminal-name read is adopted as the
instrument on evidence, not on a guarantee. **If the newly-created Local's terminal name is not the control asked
for — or is empty — the 6355400 route returns as the FALLBACK, built additively on a donor per a2, seeded per b3,
never by re-plumbing another op's cast per b2.** That contingency is written into Pre-decided 51 so no future
session has to rediscover it.

NOT ACTED ON: nothing in `tools/gscript.py`, `OpNodeLabels_v0`, `OpLoopCast_v0` or `OpCreateLocal_v0` was modified
on this review's say-so; `OpCreateLocal_v0.vi` (md5 `58275b21…`) stands as built and is used unchanged by the
read this review redirected the cycle to.


## Launch gate - NO RECIPE (explicit opt-out)

No stop record was armed for this review. `tools/prior_art_review.py` was run with `--no-recipe`,
and its mandatory reason is recorded here verbatim:

    NO-RECIPE: Pre-decided 51 is a four-step DECOMPOSITION PLAN (L1-L4) for the OpLocalName_v0 reader, required by the user 2026-09-19 re-split rule; no recipe file exists for it and none may be created this cycle (48(n)), so there is nothing to arm a launch gate against.

This is an opt-out, not a release. It frees no recipe and discharges no verdict; the only release
lines are the two `guard_cycle.py` already validates, and neither of them is this.
