---
type: plan
status: current
date: 2026-09-19
cycle: 27
kind: build
supersedes: [docs/cycle21-plan.md]
tags: [d0, d1, d2, delivery, gpu, unattended]
---

# Cycle 27+ — the user's re-plan answer: **D0 → D1 → D2, in that order**

**User, 2026-09-18 14:2x, answering the third consecutive outcome review:** *"D0, D1, D2 순서로 진행하면 좋을듯."*
Asked what "option 1" would even change when the original already has its stop path and `save N xyz traces.vi`,
the answer was: nothing — option 1 as written was wrong. The real first step is **D0** from `docs/cycle15-plan.md`
(the plan the user approved 2026-09-17), then D1, then D2. This file names the order and the pre-decided points;
the content of D0/D1/D2 stays where it is written (`docs/cycle15-plan.md` §"D1 = …", `docs/pre-rig-master-plan.md`
rows 1.1–1.9, `docs/d1-route-b-plan.md`).

## The three deliverables (definitions unchanged)
- **D0** — a **plain, unmodified copy** of the original under `claudeDev`, driven by the harness with nobody present
  through stages 0→4 (panel parameters → configure → bead-pick clicks on the image display → done button → save
  path/name → experiment loop), run, stopped, restarted. What is built is the **harness**, not the VI. (Rule 1c';
  `lv_gui.ps1 -Exception Approved -Evidence "user 2026-09-17 bead-pick option 1"`.)
- **D1** — inside that copy: acquisition loop · **GPU-kernel tracking loop** · file-writer loop · frame accounting ·
  stop/shutdown; stages 0–3 untouched; N1 = the 10,043-frame fixture comparison of `GPU_kernel_v1.vi` first.
- **D2** — scheduler · motor (`SetCommand_signed.vi`) · ASI/focus loop · display; then the Phase-2 dry-run checks.

## Pre-decided (apply, cite the number, do not re-ask)
1. **Order is D0 → D1 → D2.** No cycle works on D1 while D0's done-when is open, none on D2 while D1's is.
2. **No further process device** (user, 08:53) — still the standing order. A retrospective naming one is a finding.
3. **D0 done-when** = a script (one runner, one bgrun, one log) that: copies the original (md5 before AND after,
   original untouched), opens the copy, sets panel parameters by VI Server, runs it, drives the pick stage by the
   approved GUI clicks, presses done, types the save path/name, lets the experiment loop run N seconds, stops it
   through the VI's own stop control, verifies the `.tra` output exists and is non-empty, closes, and repeats once
   (restart). Every step gated with a prediction contract.
4. **Motor boundary for D0 — P2 IS DONE (2026-09-18 14:3x–16:0x, user present).** The user ran the plain copy
   (`claudeDev\Track_D0_copy_20260918.vi`) by hand through the pick stage into the experiment loop; the magnet
   bound was measured (panel Data-Entry range 0…40.84, nothing in front of `MOV`); **controller-side limits are
   now in force** — PI `TMN 0 / TMX 39` (RAM; the gate's session-start hook re-applies and verifies them) and ASI
   `SL/SU` = live position ±2 mm (persistent) — and `tools/motor_gate.py --session start|end` + the live test
   10/10 (`tools/bench/motor_gate2_live.log`). **Unattended D0 runs may therefore start the VI**, on the
   ASSUMPTION (flagged for the user, rule 2c) that the controller limits are the protection the user meant by
   "그러면 안심할 수 있을 것 같은데": every D0 run begins with `motor_gate.py --session start` (refuse the run if
   the readback fails) and ends with `--session end` is NOT called (limits stay on; the user's "release at end"
   applies to the interactive tool sessions, not to unattended runs). Known facts to re-check after the first
   unattended run: `TMX?` still 39 and `W X` unchanged (does the original's startup reload parameters or re-zero?).
   Opening the copy needs the original preloaded read-only (`tools/bench/p2_open_copy.py` pattern).
5. **Motor-limit check A** (`docs/motor-limit-assurance-plan.md` §A.1; its missing primitive is now BUILT:
   `OpFsTunnelTerm_v0.vi`, firefighter 2026-09-18 13:36, 38/38) runs **alongside D0 on the D0 copy** — it is
   read-only and needs no motor. It is the precondition of the P2 live check, so it is not deferred behind D0.
6. **GPU first** in D1 (`GPU_kernel_v1.vi`); CPU top level is a later, second deliverable. Fixture comparison N1
   before any D1 build.
7. **Failed prediction ⇒ a SINGLE `-Agent claude -Role hypothesis` arm** (opus / effort max, web on), which
   `guard_peer.py` accepts as discharging the failed prediction since the **CLAUDE.md §5 amendment of
   2026-09-18** ("Codex's roles move to Claude sub-sessions" + "D3 IS AMENDED"), taken because codex's weekly
   quota reached 9 %. **`-Dual` is NOT the default any more**: it stays available and is the right call only
   when a claim about our OWN tools needs a second opinion that does not share our priors. (This line said
   "Failed prediction ⇒ `-Dual` review" until 2026-09-18 18:1x; corrected by the cycle-32 material session.)
   Firefighter ladder per CLAUDE.md §3 (runner-decided).
8. `docs/cycle21-plan.md` is superseded by this file; `docs/cycle15-plan.md` stays the content reference.
9. **EVERY GUI action is capture → locate → act → capture → confirm (user, 2026-09-18 17:5x, watching the live
   v4 run: *"GUI 컨트롤 중에는 반드시 캡처 이미지 비교하는게 필요할듯"*).** Capture BEFORE and locate the target
   *in that capture* (colour/template match, OCR of the label, or the control's live screen rect); act; capture
   AFTER and CONFIRM the expected change (button state, a counter, a new window) before the next step. No change
   ⇒ FAIL and stop. **Derived or remembered coordinates are never clicked blind** — a coordinate that worked on
   another copy of the same VI is not evidence about this one, and a window-rect comparison says nothing about
   control positions inside the panel. Read the panel rect live (maximise first). Implemented by
   `tools/bench/d0_locate.py` + `clickprobe`; this is what turned v4's 13/3 into v5's 39/1: v4 reused v3's panel
   geometry and clicked the V6 copy's (1114,915) while this copy's button centre was (1177,862) — the click
   landed at **(−63, +53) px** from the button, i.e. 63 px left and 53 px below it.
   <!-- MEASURED: 1114−1177 = −63, 915−862 = +53 (screen y grows downward). A SECOND, duplicate item numbered 9
        stated this deviation as "(−64, +51) px"; both components were wrong and the duplicate numbering made
        "cite the number" ambiguous. Merged into this item and the figure corrected by the cycle-34 judgement
        session, 2026-09-18, resolving doc_ingest contradiction P1 (archive/ingest/2026-09-18-ingest-2026-09-18.md). -->
10. **The live motor-gate test to cite is the 16:0x RETEST, 10/10** (`tools/motor_gate.py` session-start repairs
   the reference after `SPA` with `RON 1 0` + `POS 1 <same value>`; self-test 76/76). The earlier 15:37 run
   scored 8/10 with L4 a FALSE PASS and is **superseded** — `tools/bench/motor_gate2_live.log` holds the 15:37
   numbers, so a citation of that file alone reads 8/10 and must say which run it means.
   <!-- Resolves doc_ingest contradiction P3 by labelling the runs rather than picking a winner: both numbers are
        true of different runs. Judgement session, cycle 34. -->
11. **One cycle number per run.** The 18:08–18:13 D0 v5 run is labelled "cycle 31" in one place and "cycle-32" in
   another because the runner's own counter (`tools/bench/cycle_runner.log`, cycles 19/20) and this narrative's
   counter disagree. A cycle number is only a label — so **identify a run by its timestamp and
   log path, never by a cycle number alone**. Do not renumber history.
   <!-- Resolves doc_ingest contradiction P4. Judgement session, cycle 34. -->
12. **`## Pre-decided` lines are edited by JUDGEMENT sessions.** A material session that believes one is stale
   reports it and stops (retrospective-cycle31 F7, disposed).
13. **`docs/cycle15-plan.md`'s `## Pre-decided` 1–4 (`:118-130`) BIND the next D1 build, and BOTH authorisation
   flags stayed `False` — ⚠️ REVISED FOR THE `Z/dZ` ROW BY 13a BELOW; read both.** Judgement, cycle 35, answering the route-B read-out's OPEN ("does a `status: paused` plan
   still bind?"). It does: that file's own frontmatter (`docs/cycle15-plan.md:5-7`) says the section "stays
   authoritative for the D1 queue/shift-register questions … nothing here is retracted", and item 8 above already
   makes cycle15 the content reference. So, for the three NO-ROUTE rows of route-B run 3
   (`tools/bench/build_d1_routeb_v0_run3.log:385-387`): `#1359`/`#29874`'s shift registers **MOVE WITH THEIR
   NODES** into loop 1.2 (`add_shift_reg` + `wire_sr`, `index_mode 1` kept exactly as the original has it —
   cycle15 item 2), and `Z/dZ` → `#2222` t0 is **REORDERED** before the S3-ct reparent of `ControlTerminal #403`
   (by index, `OpConnectNested_v1`, sink `is_source` FALSE — cycle15 item 3). The recipe's two constants
   (`tools/recipes/build_d1_routeb_v0.py:242`, `:247`) carry the comment "only the judgement session may turn it
   on": **the judgement session declines, and the answer is "no", not "not yet".** `SR_QUEUE_AUTHORISED` and
   `TEMP_SINK_AUTHORISED` stay `False`; a build that needs either to be True is the wrong build.
13a. **REVISED — `TEMP_SINK_AUTHORISED` is `True` FOR THE `Z/dZ` ROW ONLY; `SR_QUEUE_AUTHORISED` stays `False`
   permanently.** Decided by the cycle-36 judgement session, which recorded it **only in STATUS** — prior-art
   finding A1 (`archive/peer/2026-09-18-priorart-d1-routeb-run5.md:242-253`) was right that this binding file was
   never amended; the cycle-37 judgement session amends it here, per Pre-decided 12. Grounds, both MEASURED:
   - Item 13's shift-register half was **confirmed by run 4** — both registers were created MOVED WITH THEIR NODES
     (`tools/bench/build_d1_routeb_v1_run4.log:315-316`). `SR_QUEUE_AUTHORISED` stays `False` for good; its grounds
     are now confirmed rather than assumed.
   - Item 13's `Z/dZ` half rested on the **REORDER**, which the machine has refuted twice: `ControlTerminal #403`
     has no node index on `Diagram[56]` and `OpConnectNested_v1` addresses `Diagram[].Nodes[].Terminals[]` only
     (`…run4.log:163-164`) — a fact already on file at `tools/recipes/build_opconnectctl_v0.py:9-14` and, with
     external sources, at `archive/peer/2026-09-17-zdz-wirecut-opus.md:130`; and the node moves at
     `build_d1_routeb_v1.py s3():617-631` cut w730, **not** the `#403` reparent
     (`archive/peer/2026-09-18-routeb-run4-error2-and-zdz.md`). A decision resting on a premise measured false is
     not preserved by leaving it alone.
   So the `Z/dZ` row runs through the **temporary-sink** path as the discriminating test. It authorises **no new op
   and no new device** (Pre-decided 2 untouched): `OpCreateEqual_v0` → `wire_control` → `OpConnectFromWire_v0` →
   delete + `remove_bad_wires_scripted`, all built weeks ago.
   ⚠️ **The flag alone is not sufficient.** Prior-art A3 (`…priorart-d1-routeb-run5.md:269-287`) measured that the
   v1/B2 RETRY returns at `build_d1_routeb_v2.py:1278` whenever `node_index_on()` is `None` — always true for a
   ControlTerminal — so `:1296` is never evaluated and the flag is INERT. The RETRY is therefore kept **only as a
   logged control** (prior-art B4): it records its NO-ROUTE reason as a `fact` and **falls through** to the
   temporary sink instead of returning.
   ⚠️ **The flag's stated grounds were mis-cited** (prior-art A2). `build_d1_routeb_v2.py:305-308` justifies the
   refusal with a 1055 modal from an invalid terminal refnum (`docs/NAMES.md:473-480`), but
   `docs/toolkit-capabilities.md:64` records that `OpCreateEqual_v0` fetches both operands INSIDE the op so no
   terminal refnum crosses COM — the cited text is the **fix** for that defect, not evidence of it. The real hazard
   is different and **silent**: `src_names=()` → `Names=[]` → `Get Outputs` empty → `Index Array[0]` returns a
   default refnum with no error. It is bounded: a silent bad refnum leaves the sink BARE, which the row's own
   discriminator reads — a measurable outcome, not a modal that hangs an unattended run.
   **Why the created `Equal?` and not the `bare_named_sinks` variant** (prior-art B3): the created node is made and
   deleted inside one operation and borrows nothing live, so even a failed cleanup can only leave a broken wire that
   `remove_bad_wires_scripted` and the ExecState gate catch. The bare-named-sink variant borrows a **live** sink on
   the original's own body diagram, where an incomplete cleanup would leave the original's input wired to `Z/dZ` —
   a rule-1a computation change on a path this build does not otherwise touch.
14. **A route-B run that ends at ExecState 0 MEASURES before it deletes.** Run 3 deleted its own working copy
   ("a broken VI is never written", `…run3.log:487`) and destroyed the evidence with it, so the ExecState-0 cause
   on record (`tools/recipes/build_d1_routeb_v0.py:131-135`) is an advance INFERENCE, never a measurement — the
   run's own census is explicitly labelled "not an explanation" (`…run3.log:428`). From now on, before any delete
   and on the live broken VI, the recipe **re-reads `ExecState` with the ORIGINAL preloaded read-only** (item 14a
   below) and writes both readings to the log. ⚠️ **Corrected within the same cycle, by measurement**: this item
   first mandated the `Wire.Is Broken?` reader (6371004) and cycle15 item 4's bare-terminal census. Both are now
   measured useless here and are **WITHDRAWN** — the census returned an IDENTICAL 375 bare named input terminals
   over 170/170 diagrams on a KNOWN-GOOD copy, so it discriminates nothing
   (`tools/bench/diag_d0_execstate_preload.log:26-36`, `:65-75`), and `Wire.Is Broken?` cannot be run read-only:
   the only built readout follows a `Terminal.Connect Wire` **write**, which `docs/NAMES.md:898-909` measured
   turns an ExecState-1 scratch into 0. Capturing evidence before deleting a broken copy stays right; those two
   instruments are not it. **A value returned beside an error has
   measured nothing**: run 3's three conditional terminals read `wire 0` *with* `error 1055: Property Node in
   OpLoopEndRef_v0.vi` attached (`…run3.log:416-418`), so that 0 is UNREAD, not zero, and must be reported as
   UNREAD. Deleting the working copy stays the rule; capturing the reading first is now part of it.
14a. **An `ExecState` read taken WITHOUT the ORIGINAL preloaded is UNREAD, not "broken".** MEASURED, cycle 35
   (`tools/bench/diag_d0_execstate_preload.log`, 9/9, rc=0): three BYTE-IDENTICAL files — the original,
   `claudeDev\Track_D0_copy_20260918.vi`, and a copy made during the run (all md5
   `c39f36e0675339673b707c59f0784fee`, 471,257 B) — each read **ExecState 0 opened cold** in a fresh instance
   (`:14`, `:53`) and **ExecState 1 in the same instance once the ORIGINAL had been opened read-only first**
   (`:44-45`, `:84`). A cold read therefore measures **subVI linkage**, not the legality of anything we built, and
   `Track_D0_copy_20260918.vi` is **not damaged** — D0's delivery record stands. So: every `ExecState` gate opens
   the ORIGINAL read-only first (the `tools/bench/p2_open_copy.py` pattern, already required by Pre-decided 4 for
   *opening* a copy — it governs *reading* one too), and any ExecState 0 taken cold is logged **UNREAD** and
   re-taken under preload before a single word of diagnosis. Cost of the preload, measured: ~+20k handles per
   condition versus ~+6k cold (`…preload.log`), so restart LabVIEW between conditions.
16. **Route-B run 3's `ExecState 0` is NO LONGER EVIDENCE that the build produced a broken VI.**
   `tools/recipes/build_d1_routeb_v0.py` copies from `Min_Track N beads V6_ParallelLoop.vi` (`:172`) and **never
   preloads it** — every other mention is `md5()` or `shutil.copy2` (`:285`, `:306`, `:462`, `:1413`), the working
   copy being opened directly at `:310` — while its S5 gate is `g.exec_state(TARGET)` at `:1289`, i.e.
   `GetVIReference(…).ExecState` on an instance with nothing preloaded (`tools/gscript.py:1920-1921`). By item 14a
   that gate has been reading linkage. The advance attribution at `:131-135` ("these cannot produce `ExecState 1`")
   is therefore **read from a void gate**. ✅ **The control WAS repeated on route B's own original**
   (`tools/bench/diag_d1_execstate_preload.log`, 7/7, rc=0): a byte-identical claudeDev scratch copy of
   `Min_Track N beads V6_ParallelLoop.vi` (md5 `2a78e17c449cacdaf5da389818526859`, = the recipe's pinned
   `ORIG_MD5` at `:173`) read **COLD 0** (`:13`) and **preloaded 1** (`:33`). The effect is not specific to the
   3StateClamping family.
   ⚠️ **THREE CORRECTIONS from the adversarial review** (`archive/peer/2026-09-18-execstate-linkage.md`, ANSWERED,
   opus/max, $2.8794), all ACCEPTED — an earlier draft of this item said the run-3 attribution was "unsupported",
   which was too strong:
   (a) **ExecState 0 was OVER-DETERMINED, not unsupported.** The attribution never rested on ExecState alone:
       `s1q` was not executed (`:1255-1257`) and S4b/S4s were skipped (`:1274-1275`), leaving three While loops
       with unwired conditional terminals — a compile-time break independent of any gate. What died is the
       *gate's* ability to discriminate, not the explanation. ⚠️ But that independent support is itself
       **measured-with-error**: run 3 read those conditional terminals as `wire 0` *with* `error 1055: Property
       Node in OpLoopEndRef_v0.vi` attached (`…run3.log:416-418`), and by item 14's own rule a value returned
       beside an error is UNREAD. So neither side is settled; the cheap test below is, correctly, what settles it.
   (b) **NO PRELOADED BUILD RUN.** The obvious remedy — re-run the build with the original preloaded — ADDS a
       hazard it does not remove: the working copy can CROSS-LINK to the in-memory original's subVIs and is then
       written by `g.save(TARGET)` at `:1291`. Preload stays confined to **read-only** ExecState diagnostics, in a
       step that never saves. A preload can also MASK a genuine break by supplying subVIs the saved VI would not
       resolve on its own, so a preloaded 1 is necessary, never sufficient. Rivals not yet excluded:
       `GetVIReference` options `0` vs the `0x10` search bit; our own ops measured flipping 1 → 0
       (`docs/NAMES.md:898-911`); load/compile settling.
   (c) **The cheapest discriminating test, and the next cycle's first act: restore the BASELINE ExecState read
       into route B's `s1()`.** `tools/recipes/build_d1_v0.py:461` has it; `build_d1_routeb_v0.py:302-316` dropped
       it. One line, no preload, no extra LabVIEW: it reads the untouched copy in the recipe's OWN instance and
       flow, separating "born 0" from "the build made it 0". Do this **before** spending another 9-minute run.
17. **NO VI-WIDE remove-broken-wires may run inside a multi-row build pass.** Decided by the cycle-39 judgement
   session on measurement, and it applies to every route, not just route B. The restructure deliberately leaves
   wires cut between S1d/S3 and S3w's rewiring pass (`tools/bench/build_d1_routeb_v4_run7.log:274-280` shows
   `#2222`'s inputs cut and awaiting rewiring), so a VI-wide reaper called from the row loop deletes the build's
   own scaffolding rather than debris. Measured cost: a **−96 VI-wide Wire delta** across a single row's
   temp-sink bracket (`…run7.log:360`), with `#2222` t3/t4 afterwards reading `'<no such terminal>'` —
   `.get()`'s ABSENT default, not a wrong-but-valid node. **Run 5 is the natural control**: it returned NO-ROUTE
   at `build_d1_routeb_v4.py:1606-1609` and so never reached the `delete_object`/reaper pair at `:1665-1669`, and
   its `#2222` t2/t3/t4/t5 ALL wired; runs 6 and 7 reached it and they failed. Removing the reaper moves the
   build TOWARD rule 1a — it stops deleting wires the original has. Applied as K1 in
   `tools/recipes/build_d1_routeb_v5.py:1760`. **The ban is on a reaper called from INSIDE the row loop**, not on
   the operation: v5's two surviving VI-wide calls, the pre-pass one at `:694` and S5's at `:2242`, are EXONERATED
   by the same control — run 5 executed both and its rows wired. Gate any future one route-A style
   (`tools/recipes/build_d1_v0.py:1112-1128` already treats it as hostile: it runs it once, then checks which of
   its own wires died). ⚠️ **`gscript.net_map` is therefore BANNED as a wire-counting instrument** — it
   calls `remove_bad_wires_scripted(target)` internally (`tools/gscript.py:2507-2516`, `:2568-2588`), so using it
   for a "safer per-diagram count" re-fires the very reaper this item removes, twice per row. Count per diagram
   with `build_track_v6_core.walk:84-92` instead, carrying its caveat (it sees only wires touching a terminal on
   that diagram). The diagram-scoped `AbstractDiagram.Remove Wire Loose Ends` (`RemWireLooseEnds`, method 6375409,
   class `AbstractDiagram` 16503) is NOT built and is not authorised by this item.
   ✅ **CONFIRMED BY REPLICATION, and the K1 separator is RETIRED from the critical path** (cycle-41 judgement,
   2026-09-19). The control is now 2 × 2 and it is clean: the two runs WITH the in-loop reaper (runs 6 and 7) lost
   `#2222`'s terminals, and the two runs WITHOUT it — run 8 (`…v5_run8.log:411-413`, t3/t4/t5) and run 9
   (`tools/bench/build_d1_routeb_v6_run9.log:464-468`, t0/t2/t3/t4/t5 with `Is Broken? FALSE` on t3 and t4) — wired
   every one. A one-off no longer explains it. The scratch-copy K1 separator (`terms_of` + `count` →
   `remove_bad_wires_scripted` → repeat) was queued to settle this question and is **no longer worth a dispatch**:
   it would confirm a result two builds already replicate. Item 17 stands as written; do not re-open it, and do not
   re-word it to "anywhere between the first cut and the last rewire" — that re-wording was conditional on a K1
   result that is no longer needed.
18. **A build ledger reports SURVIVING wires, never attempts.** Cycle-39 judgement, accepting
   `archive/peer/2026-09-19-routeb-run7-index-shift.md` Q4: route B's WIRED count was a mixture — `wire_sr` and
   plain `wire` rows recorded no uid and no readback, and `wire_control`'s `next(..., 0)` collided "unwired" with
   "no such terminal", so a logged `wire 0 -> 0` was never evidence that a terminal exists. Every wiring row
   records the uid it created and reads it back with a `None` sentinel; every run prints a survival census
   (`set(o["uid"] for o in g.report_all(TARGET,"Wire"))` against the ledger's uids) immediately after the S3w
   ledger line — **after the ledger, not after S5, because no route-B run has ever reached S5**. Applied as K3 in
   `build_d1_routeb_v5.py:1130`, `:2036`, `:2120`. A ledger number quoted without its survival census is a
   structural claim only (CLAUDE.md "structural is not functional").
   ⚠️ **AMENDED by the cycle-40 judgement session, on measurement: the census may NOT be read with
   `report_all(Wire)`.** Run 8 proved that call is itself an `error 2` victim — it raised
   `error 2 … Traverse for GObjects.vi->OpReportAll_v0.vi | Class Operator:Traverse (Traverse Failed)` after 50
   uids had been claimed (`tools/bench/build_d1_routeb_v5_run8.log:364`), so the one measurement run 8 existed to
   produce came back UNREAD and the ledger's `WIRED 53` is still an attempt count. Read the census instead from the
   walk the recipe already holds — assert `wmap(TARGET, d)[node][2][t]["wire"] == claimed_uid` over the four
   diagrams the build touches (20 / 21 / 24 / 56) — which is cheaper than a VI-wide traverse and strictly more
   probative, because it names the terminal each claimed wire was supposed to land on
   (`archive/peer/2026-09-19-routeb-run8-predictions.md` Q4). The requirement of item 18 is unchanged; only the
   instrument is.
   ⚠️ **AMENDED AGAIN by the cycle-41 judgement session — a census reports FOUR buckets, and "unread" is one of
   them.** Prior art on run 9's recipe (`archive/peer/2026-09-19-priorart-d1-routeb-run9.md`, NOT NOVEL) raised two
   defects in the walk-based census as first cut, both accepted and both now binding on every future census:
   - **B2 — an unreadable census must say UNREAD, never "gone".** `diag_index` IS `report_all(Diagram)`
     (`tools/recipes/build_d1_v0.py:357-358`), the very call `error 2` kills, so a census that lets it raise would
     print a confident `0 survived / 51 gone`. Run 9 proves this was not hypothetical: **all five** `diag_index`
     calls raised and the census printed `0 survived / 0 bare / 51 unread of 51 claimed`
     (`tools/bench/build_d1_routeb_v6_run9.log:365`, reasons `:366-:418`). The honest null is what made `error 2`
     the named blocker instead of a phantom wiring catastrophe.
   - **B4 — uid inequality is NOT wire death.** A cross-boundary wire is several segments with different uids
     (`docs/toolkit-capabilities.md:68`), so a non-zero uid that differs from the claimed one is survival.
   **The contract**: every claimed row is classified `EXACT` (reads the claimed uid) · `SEGMENTED` (reads a different
   non-zero uid — survival) · `BARE` (reads no wire — the only genuine loss) · `UNREAD` (the walk raised, the address
   will not resolve, or the terminal entry is absent — never counted as a loss). Headline =
   `CENSUS: <EXACT+SEGMENTED> survived / <BARE> bare / <UNREAD> unread of <claimed> claimed`, then one line per
   non-EXACT row. **The census must never raise.** The four diagram walks are taken ONCE and cached — never per row:
   a per-row `fresh=True` re-walk is the traverse volume that is a candidate cause of run 8's 6 → 11 `error 2`
   worsening. Implemented in `tools/recipes/build_d1_routeb_v6.py:2160-2256`.
   ⚠️ **A census of 51 UNREAD rows does not confirm survival and does not refute it.** Run 9's `BARE = 0` is
   VACUOUS — nothing was read back — so route B's `WIRED 54` is STILL an attempt count, exactly as it was after
   run 8. Do not quote it as a survival number.
19. **The `Z/dZ` temp-sink bracket's correct Wire-count null is `+1`, NOT `0` — so `build_d1_routeb_v5.py:1842`
   asserts an inverted null and must read `_b_ok = (_wddelta == 1)`.** Decided by the cycle-40 judgement session
   from a read of our own code, not from the peer that raised it (`archive/peer/2026-09-19-routeb-run8-predictions.md`
   Q2 is a hypothesis; this item is the confirmation). The call order inside the bracket is `:1613` count →
   `:1616` `create_equal` → `:1668` `wire_control` → `:1751` `OpConnectFromWire_v0` → `:1774` `delete_object` →
   `:1810` count → `:1842` gate. The branch runs **only under `if not zw`** (`:1597`), i.e. only when the source
   control carried NO wire, so the before-count at `:1613` is taken while the control is still bare; `wire_control`
   at `:1668` then CREATES the sink wire, `OpConnectFromWire_v0` only BRANCHES that same net at delta 0
   (`docs/toolkit-capabilities.md:70`; run-8 log `:356`), and the wire SURVIVES the delete
   (`tools/bench/build_d1_routeb_v5_run8.log:358`). One new wire is exactly what a correct bracket is *for*.
   The comment at `:1601-1605` — "every write in the bracket is a BRANCH off an existing net … so the expected
   delta is 0" — is therefore **false at its premise** and is corrected with the gate.
   ⇒ **`Z/dZ` t0 WAS WIRED in run 8** and the J2 row was failed by the gate, not by the machine: `:418` reads
   (a) source identity True — the control's own wire 29238 IS the sink wire, exactly one reciprocal source
   terminal — (b) per-diagram delta +1 = the correct value, (c) `Is Broken? False`, (d) sink read back 29238.
   Do not re-open the `Z/dZ` route on the strength of that FAILED label. ⚠️ This does **not** disturb run 7's
   `−96` VI-wide delta or item 17 that rests on it: −96 is not +1, and a wrong null in one direction is not
   evidence about a deficit in the other.
   ✅ **CONFIRMED BY THE MACHINE, run 9, 2026-09-19** (`tools/bench/build_d1_routeb_v6_run9.log:360`, `:464`): with
   the gate reading `== 1` the `Z/dZ` t0 row **PASSES J2** — `_wddelta == 1`, source identity True (the control's own
   wire 29238 IS the sink wire, exactly one reciprocal source terminal), per-diagram Diagram[24] `(31, 32, 1)`,
   `Is Broken? False`, sink read back 29238 — and the row is logged WIRED. This item was decided from a code read in
   cycle 40 and is now a measurement; the `Z/dZ` route is CLOSED as a question. Item 19 needs no further test.
20. **`error 2` is the ONLY thing between route B and a delivered D1, and run 10 attacks it with the census it also
   needs — ONE edit, one runner.** Cycle-41 judgement, from run 9. The state of the evidence:
   - It is **not** handles (refuted: healthy at 51,349 / 51,353, crashed at 35,551 / 35,555 —
     `archive/peer/2026-09-19-routeb-run8-predictions.md` Q3). LabVIEW `error 2` = memory / reference allocation.
   - It is **not** the census instrument. Cycle 40 blamed `report_all(Wire)` and replaced it; run 9's replacement
     died the same death, five times over (`tools/bench/build_d1_routeb_v6_run9.log:364`). Every victim across runs
     8 and 9 is a **traverse** — `report_all(Diagram)`, `report_all(WhileLoop)`, `report_all(Wire)`,
     `count(LoopTunnel)` — i.e. `Traverse for GObjects.vi`, whatever the class.
   - It is **temporal within a run**: the same diagram walks that wire 54 rows early all fail by census time. That is
     the one asymmetry two runs agree on, and it is the only lead not yet tested.
   So run 10 = `tools/recipes/build_d1_routeb_v7.py`, cut from v6's bytes, with **ONE edit**: immediately after the
   S3w ledger line, **save the working copy, close it, RESTART LabVIEW (standing authority, CLAUDE.md §3), reopen the
   saved copy in the fresh instance, and run the four-bucket census there.** Nothing else changes — not the wiring
   pass, not the gates, not the per-bead maths (rule 1a); saving and reopening changes no computation.
   **This is one action doing two jobs, which is why it is the right next build**: it is the only route to a census
   that can READ, and it is simultaneously the discriminating test for the cumulative-allocation hypothesis STATUS
   has carried as UNCONFIRMED for two cycles. A fresh-instance census that reads CONFIRMS it (and tells us the 11
   failing wire rows are fixed the same way — by phasing the build across instances); one that still fails REFUTES
   it and moves the cause onto the VI or the traverse itself. Either answer is worth the run.
   ⚠️ Do **not** "fix" the census by reading each wire at claim time. That is an attempt count with extra steps and
   item 18 exists to forbid exactly it — a survival census must be read AFTER the wiring pass.
   ⚠️ The save is of a **working copy under `claudeDev`**, mid-restructure and possibly broken; that is allowed and
   normal (rule 1 governs originals). Preload stays confined to read-only ExecState diagnostics (Pre-decided 16b), so
   the census step opens the saved copy WITHOUT preloading the original — it needs diagram walks, not `ExecState`.
   If a mid-run restart turns out to be unreachable over our COM path, that is an `OPEN:` for judgement, not a
   licence to fall back to a same-instance census.
   🔴 **SUPERSEDED BY ITEM 21 — run 10 ran and item 20's mechanism never executed.** The E3 save diverted to
   `gui_save` and died (`tools/bench/build_d1_routeb_v7_run10.log:367`), so no restart, no reopen and no
   fresh-instance census ever happened; phasing across instances is still UNTESTED. Its premise is also no longer
   the live one: item 21 replaces "temporal, therefore restart" with a named, testable CAUSE. Do not re-cut a
   save→restart→reopen build on the strength of item 20 alone.
21. **`error 2` is a REFNUM LEAK in our own traverse ops, and run 11 repairs it instead of working around it.**
   Cycle-42 judgement, from the mandatory failed-prediction review of run 10
   (`archive/peer/2026-09-19-routeb-run10-error2-class.md`, ANSWERED, claude/hypothesis opus max, $5.5451, 639 s),
   which REFUTED the cycle's own diagnosis on our own log lines. Five things now bind every future route-B build:
   - (a) **`error 2` is LabVIEW's generic "Memory is full"** (NI KB kA00Z0000019KhWSAU), and the meter for it is
     **LabVIEW's private bytes**, never the handle count. Every previous "handles refute memory" argument in this
     project — including STATUS's "healthy at 51,349, crashed at 35,551" — is a **category error, not a
     refutation**. Do not repeat it.
   - (b) **The live cause is a leaked GObject reference per matched object** inside `report_all` / `count`
     (`.claude/skills/labview-automation/references/com-driving.md:305-312`; `docs/REFERENCES.md:126` records the
     `Close Reference` that was REMOVED). `count(Diagram)` matches 170 objects and `count(Node)` 626, so ~30
     successful `report_all(Diagram)` calls leak thousands of refnums before the traverse that finally fails.
     ⚠️ **AMENDED 2026-09-19 by the cycle-43 (firefighter) judgement session — NOT SUPPORTED BY MEASUREMENT.**
     20 × `report_all(Diagram)` (= 3,400 matched objects that this line predicts leak) moved kernel handles **+9**
     and private bytes **−0.1 MB**, with **no `error 2`** (`tools/bench/s0_hygiene_probe_run2.log:121-123`); the
     `count(Node)` window's +215 handles is +202 in call 0 = the 473 KB VI load, not the traverse (`:75`, `:95`).
     The per-matched-object leak arithmetic above is therefore withdrawn as "the live cause"; `error 2`'s cause
     returns to OPEN, and the S0 repair is NOT predicted to close it. (c) below is untouched — the repair stays
     owed as rule compliance. The kernel handle count is blind to VI Server refnums (`tools/gscript.py:227-228`),
     so any future leak gate reads PRIVATE BYTES alongside handles, and handles from call 1 (excluding the load).
   - (c) **Closing those references is owed anyway.** CLAUDE.md's reference-hygiene rule already requires every VI
     Server reference to be closed by whoever opened it, so restoring the `Close Reference` is a RULE-COMPLIANCE
     REPAIR of an existing op — not a speculative fix and not a new "장치" under the user's 2026-09-18 08:53 order.
     It is applied unconditionally, whatever it does to `error 2`.
   - (d) **A traverse INDEX is not a stable key — worse than the archived +1.** `FRAME_BODY_UID=639` reads index
     **43** at `tools/bench/build_d1_routeb_v7_run10.log:44` and **56** at `:352`, a shift of **+13 inside one
     instance with no restart**. Any census or route keyed on a diagram index is unsound. The key is the diagram
     **UID**; where uid→index conversion is unavoidable it must be re-read, never cached across a mutation.
   - (e) **The cycle-42 traverse census was a SELECTION ARTEFACT and is withdrawn.** "`report_all(Diagram)` is
     0-for-21, it has never once succeeded" was produced by grepping for lines that PRINT `error 2`, which can only
     find failures; the successes are at `run10.log:39`, `:44`, `:69`, `:352`, `:354` and ~29 `move_in` calls at
     `:150-167`. A census whose instrument can only observe one outcome measures nothing — the same error CLAUDE.md
     names under "absence in what you happen to be looking at is not evidence of absence".
   - (f) **A claim about what OUR OWN code does must quote the CALLEE, not the call site.** The reviewer's own
     proposed rule, and the one that would have prevented this cycle's `inference-over-measurement` violation: the
     cycle-42 `REFUTED:` lines said "v7 saves over COM with `g.save`, not `gui_save`" from v7's call site, while
     `tools/gscript.py:2065-2067` diverts `g.save(…, allow_broken=True)` to `gui_save()` on any cold `ExecState`
     read. Both `REFUTED:` and `FIXED:` releases, and any sentence of the form "our tools do/cannot do X", carry the
     callee's `file:line`. Form-checking cannot catch this — `docs/violation-decisions.md` records why no device was
     built for it.
   **Run 11** = one runner, one log, three unconditional phases: (1) the review's own discriminating test — repeat
   `report_all(TARGET,'Diagram')` on a pristine scratch copy in a clean instance, logging the iteration index AND
   private bytes, until it raises or a bounded count is reached; (2) the same measurement again with the
   `Close Reference` repair applied; (3) the route-B build from v7's bytes with **E3 removed** (no save, no restart,
   no reopen — back to v6's in-instance census) and the repair in place. Nothing branches on a result.
15. **`Count` is NOT a bead count, and no harness may gate on it.** MEASURED, cycle 35
   (`tools/bench/diag_count_indicator_run4.log`, 16/0; now `docs/NAMES.md` §`Count`): `Count` is uid **28051**, a
   front-panel **CONTROL** (`indicator` False), not an indicator. Its terminal is a **SOURCE** driving wire 30530
   into `Comparison #29111` (`Equal?`, terminal `x`) and into `SelectorTunnel #31929` of `CaseStructure #28709`,
   both on Diagram #15795, inside `Sequence #15649` → `EventStructure #15544`. It is **written** by two implicit
   `Property` nodes labelled `Count` whose `Value` is a SINK (#32191 on Diagram #12960, #30688 on Diagram #28741
   inside that same case structure). So it is a counter variable parked in a control and steered by the event
   structure — which is why three registered picks leave it reading 1
   (`tools/bench/drive_original_copy_v4.log:790`, `…v5.log:181`). **That reading was never a fault**, and
   retrospective-cycle31 F6b is answered: v5's method — counting the three red markers the VI draws — stands, and
   D1 must neither gate on `Count` nor "fix" it. No other panel object is a bead count either (`Total cycle #`
   30309, `# of Points` 10008, `Bead Pos` 11831, `Total Lost Frames` 421, `# of Auto-Reset` 9768 — `Bead Pos` is
   the only bead-related one). Not fully established, and not on D1's path: whether anything *else* writes it —
   #32191's owner chain ends at a `FlatSequenceFrame` with `owner_uid 0`, and `report_all('GlobalVariable')`
   fails on this VI with **error 1092**.

## Pre-decided — ADDED 2026-09-19 17:4x (user, after the overnight route-B loop): D1 IS BUILT IN SAVED STAGES
22. **CLAUDE.md §3 "Big or blocked work is SPLIT into steps that each SAVE an intermediate artefact" applies to D1
    from now on.** No more full-length `build_d1_routeb_vN.py` runs. The D1 build is a CHAIN of stage scripts, each
    starting from the previous stage's SAVED file in a FRESH LabVIEW instance (original preloaded read-only for every
    ExecState read — Pre-decided 14a/16), each ending with a save under `claudeDev` and an md5 in its log:
    | stage | saved file | pass criterion |
    |---|---|---|
    | **S0 hygiene** | repaired traverse ops (`OpWireSource_v6.vi` / `OpReport_*` with `Close Reference` restored; **new versions, the old files untouched**) | 20 consecutive calls in one script ⇒ LabVIEW handle count flat (±100); `docs/REFERENCES.md` updated |
    | S1 | `D1_s1_copy.vi` (copy of the original, fixture TIFF writer + the 3 re-dropped nodes deleted) | md5 recorded; ExecState 1 preloaded; node count = original − deletions |
    | S2 | `D1_s2_loops.vi` (three fresh While loops + 3 subVIs dropped) | +3 loops +3 subVIs, ExecState read |
    | S3 | `D1_s3_moved.vi` (21 nodes + 8 control terminals moved, `Z/dZ` reorder, 8 shift registers) | counts per §2c; ExecState read |
    | S3w-a … S3w-e | `D1_s3w_a.vi` … (re-wiring in batches of ≤15 rows of the 66) | each batch's rows WIRED (`Wire.Is Broken?` FALSE), ledger saved per batch |
    | S4–S6 | `D1_s4_census.vi` → `Track_v6_D1_GPU.vi` | census, ExecState 1 preloaded, saved |
23. **Two consecutive failures of one stage at the same place ⇒ that stage is decomposed further before any retry**
    (CLAUDE.md §3 rule 3). The runner's firefighter trigger now ignores `_vN` suffixes.
24. The firefighter cycle ordered by the user on 2026-09-19 does S0 and S1 (and S2 if S1 passes cleanly) — nothing
    beyond; it ends with the saved files listed and their md5s, or with the exact failing stage.
25. **S0 IS DECOMPOSED — this table IS the one-page plan Pre-decided 23 demands** (judgement, cycle 44, 2026-09-19).
    S0 has now failed TWICE AT THE SAME PLACE: post-wiring `ExecState 0` on every repaired op stub, replicated ×4 in
    fresh instances with every wiring gate PASSING (`tools/bench/build_s0_closeref_v3.log`, 87/5;
    `…_v1.log`, 41/2). By CLAUDE.md §3 "Big or blocked work is SPLIT…" rule 3, **no full-length S0 retry may be cut
    under any filename**. S0 runs as five sub-steps, each its own short script, each starting FROM the previous
    step's saved file in a FRESH LabVIEW instance, each ending with a saved artefact and its md5 in the log.
    **The first FAIL stops the chain and leaves the file that shows the failure on disk.**

    | sub-step | what it does | saved artefact | pass criterion |
    |---|---|---|---|
    | **S0-a ARM** — baseline, **NO edit** | copy `OpReport_v3.vi` to a new name; read its `ExecState` twice: (i) COLD in a fresh instance, (ii) after opening `OpReport_v3.vi` itself read-only in that same instance (the op-stub analogue of Pre-decided 14a's "original preloaded" — it loads `Traverse for GObjects.vi` and the rest of the hierarchy). Edit nothing | `claudeDev\S0a_OpReport_base.vi` + md5 + BOTH readings, each labelled with its condition | both readings are TAKEN and logged. 🔴 **A cold-0 / preloaded-1 pair means S0's four `ExecState 0` failures were UNREAD (Pre-decided 14a), not broken — the chain STOPS there for judgement, and the three op stages of run 2 were replicating a measurement artefact** |
    | **S0-b MEASURE** — is the repair needed at all? | profile the **UNREPAIRED** ops under a BUILD-SHAPED workload (traverses interleaved with mutations, S3w-like), ≥20 calls, recording kernel handles **from call 1** (call 0 is the 473 KB VI load — `s0_hygiene_probe_run2.log:75`,`:95`) AND LabVIEW private bytes per call | `tools/bench/s0b_refleak_profile.json` + its log | the profile COMPLETES and prints both meters per call. Pure measurement — **no outcome of it fails this step** |
    | **S0-c EDIT — one edit per saved file** | c1 = For Loop only · c2 = + the `Close Reference` node inside it · c3 = + the `References` array branch wired in · c4 = + `remove_bad_wires_scripted` | `claudeDev\S0c1_…vi` … `S0c4_…vi`, each md5'd | each file SAVES, and each reads `ExecState` under the condition S0-a established. The first sub-step whose ExecState drops STOPS the chain — and **that file is on disk for the next session to open** |
    | **S0-d HYGIENE** | the accepted op, 20 consecutive calls in one script | the accepted op VI + log | handles flat ±100 **counted from call 1** AND private-byte drift ≤ 5 MB. The ±100 gate ALONE is blind to VI Server refnums (`tools/gscript.py:227-228`), so both meters or neither |
    | **S0-e RECORD** | update `docs/REFERENCES.md` + `docs/toolkit-capabilities.md`; old op files untouched | the doc diffs + md5s of the OLD ops | the old ops are byte-identical to before; the accepted ops carry new `_vN` names |

    Binding notes:
    - (i) **S0-a is the ARM, and the ARM is its own SAVED step** (retrospective-cycle43 F1/F5: run 2 spent three op
      stages replicating a failure the ARM had already measured). **No S0-c script may be cut before S0-a's two
      readings are on file.**
    - (ii) **Order inside S0 is the cycle-43 disposition's (c) then (a)**: settle WHY the insert leaves `ExecState 0`
      — `archive/WORKLOG.md:86-87` (a bare For Loop breaks the VI) and `remove_bad_wires_scripted` was never called —
      before any more close-wiring. S0-c1…c4 IS that test, decomposed one edit at a time.
    - (iii) **The array-into-scalar experiment stays a SCRATCH experiment only**, with a prediction contract citing
      `archive/WORKLOG.md:84-86` ("defeated four wiring attempts"). It is not a step of this chain.
    - (iv) ⚠️ **S0's original premise is MEASURED UNSUPPORTED** (Pre-decided 21(b) amended by cycle 43): the repair is
      owed as **rule compliance** (21(c)), not as an `error 2` fix. CLAUDE.md §3's hygiene rule states its acceptance
      test as "20 consecutive calls ⇒ handle count flat (±100)". **ASSUMPTION THIS CYCLE PROCEEDS UNDER, flagged to
      the user (rule 2c): if S0-a shows the `ExecState 0` was UNREAD and S0-b shows the UNREPAIRED ops already meet
      that test on both meters, judgement may ACCEPT THE OPS AS THEY ARE with the measurement as the record** — a
      legitimate outcome of S0, not a skipped step. Only the user may overturn this reading of their own rule.
    - (v) `Close Reference` on a GObject refnum may be a **NO-OP** — forum-grade, no version context
      (`archive/peer/2026-09-19-s0v3-execstate0.md`). S0-d's private-byte meter is what decides whether the repair
      does anything at all; a repair that moves neither meter is recorded as such, not celebrated.

    ⚠️ **AMENDED THE SAME DAY BY ITS OWN PRIOR-ART REVIEW — `archive/peer/2026-09-19-priorart-s0-decomp.md`,
    NOT NOVEL, 8 findings, ALL EIGHT ACCEPTED AS `FIXED:` (cycle-44 judgement, 2026-09-19).** The direction survives
    (`:235`: a staged save-per-step S0 has never been tried and abandoned) but four of the five sub-steps duplicated
    work already on file. What binds from here is this block, not the table above:
    - 🔴 **S0-a IS WITHDRAWN. Its premise is dead: the op stub reads `ExecState` 1 COLD in a fresh instance, measured
      SEVEN times** (`tools/bench/build_s0_closeref_v3.log:13-14` `PASS A2 ARM … ExecState 1` immediately after
      `fresh(): new LabVIEW pid`, also `:60`, `:109`, `:168`; `…_v1.log:15`, `:59`, `:103`;
      `build_opconnectfromwire_v0.log:49`). A cold-0 / preloaded-1 pair therefore **cannot occur** for these stubs,
      Pre-decided 14a does not reach them, and the conclusion is the opposite of the one S0-a was written to test:
      **the stub is born legal and OUR EDIT breaks it.** (Finding A1.)
    - 🟢 **THE POSITIVE CONTROL IS THE LEAD, and S0 has never used it.** This exact construction — a For Loop +
      `Close Reference` around the same `References` array, on the same op family — was built on 2026-09-13 and ended
      **`ExecState` 0 → 1**: `docs/toolkit-capabilities.md:400-402`, `:409`, `:432-438`, built by
      `tools/recipes/build_opreportall_v1.py` (instrumentation at `:87-90`, `:135-136`, `:158-160`, `:41`).
      (Findings A4, B3.) One build of this thing works and four do not, so the question is a **DIFF**, not a mystery.
    - **The chain is now α → β → γ, then b, then d/e:**
      | sub-step | what it does | saved artefact | pass criterion |
      |---|---|---|---|
      | **S0-α DIFF** — no LabVIEW at all | diff `tools/recipes/build_opreportall_v1.py` (works, ends 1) against `tools/recipes/build_s0_closeref_v3.py` (fails, ends 0) and their logs; enumerate EVERY ordered construction difference — node-vs-tunnel order (`build_opreportall_v1.py:28-29`, `docs/toolkit-capabilities.md:415-418` vs `build_s0_closeref_v3.log:74`,`:77`,`:80`), which terminals are wired and in what order, whether `remove_bad_wires_scripted` is called, what is saved and when | `docs/s0-diff.md` | the table exists and names each difference with both `file:line` sides. **This runs FIRST and costs no LabVIEW** |
      | **S0-β REPLICATE** | re-run the 2026-09-13 construction UNCHANGED on a fresh scratch copy; after EACH edit read `ExecState` **and then re-read `Wire.Is Broken?`** (the falsifier left unapplied at `archive/peer/2026-09-19-s0v3-execstate0.md:140-142`, with the wire census at `:130`/`:148`); save the result | the rebuilt op VI + md5, or — if the state is illegal and cannot be saved — the readings as a DATA file | ends `ExecState` 1 and the VI SAVES. **If it now reads 0, the positive control has rotted and THAT is the finding** |
      | **S0-γ PORT** | apply the differences S0-α named, **one difference per saved artefact**, until the repaired op is reached or one of them reproduces the 0 | one artefact per difference | the first difference that flips 1 → 0 is the cause, and its artefact is on disk |
      | **S0-b MEASURE** | unchanged in purpose, but it **EXTENDS `tools/bench/s0_hygiene_probe.py`** (`:80-91`, `:161-171`, `:185-193`; precedent `tools/bench/handle_audit.py:69-70`) — only the mutation interleave is new | `tools/bench/s0b_refleak_profile.json` | completes and prints both meters per call. Measurement only (finding B2) |
      | **S0-d/e** | acceptance + record | the accepted op; `docs/REFERENCES.md` §4a **amended**, not authored (`:144` already exists) | the ONE criterion below |
    - **ONE S0 acceptance criterion, stated once** (finding A3 — the plan carried three): **G-A no `error 2` · G-B
      kernel handles flat ±100 counted FROM CALL 1 · G-C LabVIEW private-byte drift ≤ 5 MB.** Adopted by the
      cycle-43 disposition (`archive/peer/2026-09-19-priorart-s0-closeref.md:701-704`). The bare "±100" of the
      Pre-decided 22 S0 row is **superseded by this line**; handles alone are blind to VI Server refnums
      (`tools/gscript.py:227-228`).
    - 🔴 **NO STEP MAY SAVE A BROKEN VI** (finding B1). `tools/gscript.py:2065-2068` refuses or diverts to
      `gui_save`, which has failed at seven logged sites (`tools/bench/build_d1_routeb_v7_run10.log:367`,
      `build_keystone.log:903`, `cycle3b_toolkit.log:78`, `extract_chain.log:10`, `gpukernel_chain.log:227`,
      `keystone_discovery.log:29`, `label_copy_clfn.log:16`) — and run 10 proved the one refutation of it wrong
      (`archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`). VI saves happen only at LEGAL states; where a step
      necessarily ends illegal, **its saved artefact is a DATA file** (readings, census, md5s). The user's rule says
      "intermediate VI/data", so this satisfies it — but it is a narrowing of note (i) and is flagged to the user.
    - **An intermediate `ExecState 0` is EXPECTED and no longer stops the chain** (finding A2): a bare For Loop
      breaks the VI by design (`archive/WORKLOG.md:86-87`, `docs/toolkit-capabilities.md:412-413`, `:417`). Only the
      FINAL state must read 1. The original c1 criterion would have halted on normal behaviour and c2/c3/c4 would
      never have run.
    - **A `c4` at `ExecState 0` exonerates nothing**: `tools/gscript.py:1293-1295` — `remove_bad_wires` does not
      clear a bad wire into a `reference` sink.

26. **S0-γ RUNS BEFORE S0-β, and its FIRST ported difference is D2/D4 (node CREATED IN THE BODY, not copied and
    reparented).** Judgement, cycle 45, 2026-09-19, on the fact S0-α produced — not on a preference. `docs/s0-diff.md`
    enumerates 23 ordered construction differences between the build that ends `ExecState` 1
    (`tools/recipes/build_opreportall_v1.py`, 2026-09-13) and the one that ends 0 four times
    (`tools/recipes/build_s0_closeref_v3.py`). Three grounds, in the order they bind:
    - (a) **The loop machinery is EXCLUDED as the common cause.** S0 run 2's stage 3 failed with **no loop created,
      no new tunnel and an EXACT branch** (`tools/bench/build_s0_closeref_v3.log:178`, `:190-192`, `:202`, `dw=0`) and
      still read `ExecState 0`. A cause common to all four failures therefore cannot be the For Loop. S0-β as written
      ("replicate the 2026-09-13 construction unchanged", `:449`) replicates precisely that machinery, so it is no
      longer the cheapest discriminating test — it is re-ordered BEHIND γ, not cancelled. It remains the right test
      if γ exhausts the diff without reproducing the flip, because then the positive control itself is in question.
    - (b) **D2/D4 is the only candidate present in every failure and absent from the success.** v3 COPIES the
      `Close Reference` node out of `KernelBuilder_v1.vi` and reparents it (`build_s0_closeref_v3.py:587` →
      `tools/gscript.py:1479-1558`; `:528`/`:453` → `tools/recipes/build_d1_v0.py:318-335`), where the working build
      CREATES it in the body (`build_opreportall_v1.py:144-149` → `tools/gscript.py:2188`). This matches the observed
      signature exactly — every wiring gate passes, the branch reads EXACT, `Is Broken? False`, and the VI is still
      illegal — i.e. alternative #2 of the mandatory review (`archive/peer/2026-09-19-s0v3-execstate0.md`): **a broken
      NODE that a wire reader cannot see.** Per CLAUDE.md "when a diagnosis is GUESSED twice, build the reader", this
      is not another inference: porting the difference IS the measurement.
    - (c) **The other two candidates are worse first tests, for reasons already on file.** D1 (edits landing on the
      Move fixture `MOVE_DST`, `tools/gscript.py:1518`, `:1536-1543`, `:78-80`) has counter-evidence —
      `tools/bench/build_opconnectfromwire_v0.log:58` reached `ExecState 1` inside that same hook, so D1 alone is not
      sufficient to break a VI. D7 (`remove_bad_wires_scripted` never called in v3; called twice at
      `build_opreportall_v1.py:130`, `:133`, recorded `docs/toolkit-capabilities.md:433`) can only CONFIRM, never
      exonerate, because `tools/gscript.py:1293-1295` says `remove_bad_wires` does not clear a bad wire into a
      `reference` sink. D7 is therefore the SECOND ported difference, not the first.
    **Binding on every γ sub-step**: one difference per saved artefact; an intermediate `ExecState 0` is expected and
    does not stop the chain (finding A2); the FINAL state must read 1 before the VI is saved, and a step that ends
    illegal saves a DATA file of its readings instead (finding B1). The first difference that flips 1 → 0 is the
    cause and its artefact stays on disk.
    ⚠️ **This cycle is bound by the outcome review's accepted condition** (`archive/peer/2026-09-19-outcome-review-20260919.md:153`,
    disposed at `:171`): a cycle that ends without S0 saved files and md5s in a log escalates the stop-and-re-plan.
    A γ step that ends illegal satisfies it with its DATA artefact, not with prose.
    🔴 **26(b) IS SUPERSEDED BY ITEM 27 — γ1 was never launched and must not be re-cut as written.** 26(a) SURVIVES
    and is strengthened: the loop machinery is not merely unimplicated, it is already ON DISK and legal.

27. **THE POSITIVE CONTROL HAS NO ARTEFACT — S0's remaining justification is rule compliance alone, so S0-b
    (MEASURE THE UNREPAIRED OPS) RUNS NEXT AND γ/β BOTH WAIT ON IT.** Judgement, cycle 45, 2026-09-19, from the
    Phase-1 census (`tools/bench/s0_op_census_run2.json` md5 `362f1e52…`, 32 pass / 0 fail;
    `tools/bench/s0_op_census.log`). Four measurements, none of them inference:
    - (a) **`OpReportAll_v1.vi` DOES NOT EXIST** (`tools/bench/s0_op_census.log:98`). The build that
      `docs/toolkit-capabilities.md:400-402`, `:409`, `:432-438` records as the one that ended `ExecState` 0 → 1
      left nothing on disk. Pre-decided 25's finding A4/B3 — "one build of this thing works and four do not, so the
      question is a DIFF" — therefore rests on a **claim with no artefact behind it**, and item 26(b) inherited that.
    - (b) **The one on-disk relative carries the loop but NOT the node.** `OpReportAll_v0.vi` (md5 `ffcec2c7…`) has
      `ForLoop #113`, body `Property #114→#115`, `References` w524 → `LoopTunnel #511` `IndexMode 1` (inner w421),
      and **no `Close Reference`** (`…census.log:105-119`), reading `ExecState` **1** cold. This also EXPLAINS S0 run
      2's stage 3 — "no loop created, no new tunnel, EXACT branch of w421" — the loop and tunnel were already there
      and w421 is that tunnel's inner wire. The detector is not blind: it finds `#157 'Close Reference'` in
      `KernelBuilder_v1.vi` (`:295`, `:313-314`).
    - (c) **There is no built route to CREATE a `Close Reference` primitive.** `tools/gscript.py:2188` is
      `build_property` and creates a Property node (`:2195`, `:2198-2202`, `:2225-2227`); `docs/vi-server-ids.json`
      carries no `Close` id. So 26(b)'s "create in the body" is not one ported difference but four (it drags D1, D3
      and the node class), and as literally written it is **unexecutable**. Copy-and-reparent out of
      `KernelBuilder_v1.vi` has been the only route all along — which is why all four failures share it.
      ⚠️ Not settled, and not to be restated as impossible: prior art B3 measures that `OpCreateEqual_v0.vi` places a
      primitive on a NAMED SUBDIAGRAM, FUNCTIONAL 23/0 (`docs/toolkit-capabilities.md:64`, `:66`), so the capability
      CLASS exists. `tools/recipes/build_s0_gamma1.py:19-25` says "nothing in this fleet can" and that sentence is
      **over-broad** — correct it if the recipe is ever revived.
    - (d) **γ1's own prior art agrees and is ACCEPTED** (`archive/peer/2026-09-19-priorart-s0-gamma1.md`, NOT NOVEL,
      9 findings / 5 slugs, claude/priorart opus high, $4.1991): A2 — 26(a) excludes the loop machinery and γ1
      rebuilds it; A3 — four differences, not one; A4/A4b — the post-compile `Is Broken?` re-read is missing.
    **Therefore the order is corrected to what the cycle-43 disposition already ordered and three cycles have not
    done — MEASURE FIRST.** S0's premise is measured unsupported (Pre-decided 21(b) as amended: 20 ×
    `report_all(Diagram)` moved handles +9 and private bytes −0.1 MB with no `error 2`), `Close Reference` may be a
    NO-OP on GObject refnums (note (v)), and the repair is owed only as rule compliance (21(c)). So:
    - **S0-b runs next**, EXTENDING `tools/bench/s0_hygiene_probe.py` (finding B2) with the mutation interleave only:
      the UNREPAIRED ops under a build-shaped workload, ≥20 calls, kernel handles FROM CALL 1 and LabVIEW private
      bytes per call, against the single criterion **G-A no `error 2` · G-B handles flat ±100 from call 1 · G-C
      private-byte drift ≤ 5 MB**.
    - **Pre-decided 25(iv) is now the live branch, not a hypothetical**: if the unrepaired ops meet G-A/G-B/G-C, the
      ops are **ACCEPTED AS THEY ARE with the measurement as the record**, S0 closes, and S1 begins. CLAUDE.md's
      hygiene rule states its acceptance as a measurement, so passing it is compliance, not evasion. **Only the user
      may overturn this reading of their own rule — it is flagged in STATUS NEXT.**
    - Only if S0-b FAILS a meter does a node-creation route become worth its cost; then the first step is prior
      art's A2 form — start from `OpReportAll_v0.vi`, which already has the loop and tunnel, and change ONLY the
      node's origin — never γ1 as written.
    - **S0-β is withdrawn** in the same breath as (a): a construction whose output does not exist and whose
      distinguishing node is absent from its only on-disk relative cannot be "replicated unchanged".

28. **G-C IS EVALUATED ON TRAVERSE-ATTRIBUTABLE DRIFT, WHICH NEEDS A MUTATION-ONLY ARM — S0-b's `+34.6 MB` is
    UNATTRIBUTED and must not be read as a leak.** Judgement, cycle 45, 2026-09-19, on S0-b's own numbers
    (`tools/bench/s0b_refleak_profile.json` md5 `b3ddf21fc39735e329c61477dbcac03e`;
    `tools/bench/s0b_refleak_profile.log:61-64`, 13 pass / 1 fail).
    - Measured: **G-A PASS** (no `error 2` from any call, `:62`) · **G-B PASS** (handles 54,619 → 54,600 = **−19**
      counted from call 1, `:61`, `:63`) · **G-C FAIL** (private 617.3 → 652.0 MB = **+34.6 MB** against a 5 MB
      limit, `:61`, `:64`).
    - **The confound is on the record and was reported by the measuring session, not discovered later**: the
      build-shaped interleave MUTATES — 20 Property nodes created, node count 626 → 645 — so `+34.6 MB` is traverse
      leak AND VI growth together, ≈1.7 MB per created node if it is growth alone. The only contrast on file is
      traverse-only: **−0.1 MB** over 20 calls (`tools/bench/s0_hygiene_probe_run2.log:121-123`).
    - **G-C's purpose is to ask whether OUR TRAVERSE OPS leak.** A workload that also grows the VI by 20 nodes does
      not measure that, so the criterion is not satisfied *or* violated until the growth is subtracted. Completing
      the measurement is not reinterpreting the gate; acting on `+34.6 MB` as a leak WOULD be
      `inference-over-measurement`, the very fault this item's parent (27) was written to stop.
    - **The discriminating arm, and the next act: MUTATION-ONLY.** The same 20-call loop, same scratch copy, same
      meters, with the `count`/`report_all` traverses REMOVED and the `build_property` mutations kept. Three arms
      then close the 2×2: traverse-only **−0.1 MB** (on file) · traverse+mutate **+34.6 MB** (on file) ·
      mutate-only (to measure).
      - mutate-only ≈ +34.6 MB ⇒ the traverses contribute ~0, **G-C is met on traverse-attributable drift**, and
        Pre-decided 25(iv)+27 apply: the ops are ACCEPTED AS THEY ARE with the measurement as the record, S0 closes,
        S1 begins.
      - mutate-only ≈ 0 ⇒ the traverses DO leak under mutation pressure, G-C genuinely fails, the `Close Reference`
        repair is owed on measurement as well as on rule, and the route is 27's last bullet — start from
        `OpReportAll_v0.vi`, change ONLY the node's origin.
    🔵 **IF THE REPAIR IS EVER REVIVED, THE FIRST PORTED DIFFERENCE IS D6, NOT D2/D4.** Recorded here by the cycle-45
    judgement session from `docs/s0-diff.md` D6, which the act-2 summary understated. The build that WORKS
    **DELETES the old consumers of `References` FIRST** — `delete_object(OP,'IndexArray',0)` and both old Property
    nodes, `tools/recipes/build_opreportall_v1.py:129-133`, callee `tools/gscript.py:2234` — and says why in its own
    source at `:127-128`: *"wiring it into a loop would need branch=True — or, far better, delete the consumer FIRST
    and the source is free"* (recorded as steps 1–3 at `docs/toolkit-capabilities.md:432-434`). The build that FAILS
    deletes **nothing**: diagram 0 still holds `Index Array #167`, `Property #241` and `Property #482` when the loop
    is built (`tools/bench/build_s0_closeref_v3.log:65`, `:70`). This fits the observed signature better than D2/D4
    does — the S0 v3 §2 arm measured the new branch as a **VALID** wire (sink w636 SEGMENTED, `Is Broken? False`,
    `LoopTunnel #642` `IndexMode 1` as read), which is exactly what a legal wire into an **illegal multi-consumer of
    a refnum array** would look like: no broken wire anywhere, and the VI still will not compile. D6 is also a
    genuinely single, cheap port (delete three nodes before wiring), unlike D2/D4 which drags D1 and D3.
    ⚠️ This is a HYPOTHESIS built from a file diff, not a measurement — it has never been run. It ranks the queue for
    a future cycle; it does not reopen S0, which closed on the three-arm result below.
    Both branches are decided here, so a material session applies whichever the arm returns; neither is a fresh
    judgement. ⚠️ **Flagged to the user with 25(iv): accepting the ops on a completed G-C is judgement's reading of
    CLAUDE.md's hygiene rule, whose stated acceptance test is a measurement. Only the user may overturn it.**

29. **THE ONLY SAVE ROUTE FOR A STAGE ARTEFACT IS `g.save()` UNDER PRELOAD — 16(b)'s "a step that never saves" is
    NARROWED, not discarded — and STAGE BOUNDARIES MUST FALL AT LEGAL STATES.** Judgement, cycle 46, 2026-09-19,
    read from the CALLEE (Pre-decided 21(f)), never from a call site.
    - (a) **Measured.** `tools/gscript.py:2056-2071` holds the only COM writer: it refuses a path outside
      `claudeDev`/`SAVE_ALLOWLIST` (`:2062-2064`), then reads `exec_state(target)` (`:2065`, which opens its OWN
      reference by path — `:1977-1979`); at 0 it diverts to `gui_save` when `allow_broken=True` (`:2066-2067`) and
      otherwise raises (`:2068`). `SaveInstrument` (`:2070`) is reachable ONLY at `ExecState != 0`.
    - (b) By Pre-decided 14a a copy of the original reads `ExecState` **0 COLD / 1 PRELOADED**. So in a
      non-preloaded instance **no copy of the main VI can ever reach `SaveInstrument`**, and the only other writer,
      `gui_save`, has failed at eight logged sites including run 10
      (`tools/bench/build_d1_routeb_v7_run10.log:367`). MEASURED, cycle 46: **no run in this project has ever saved
      a modified copy of the main VI** — every `g.save(TARGET)` sits in an S5/S6 no route-B run reached
      (`tools/bench/build_d1_v0_run4.log:256`; `…routeb_v5_run8.log:438`; `…v6_run9.log:492`).
    - (c) **Therefore Pre-decided 22's staged build is unexecutable under 16(b) as written.** 16(b) named two
      hazards and only one of them was ever measured. MASKING is answered, not denied: every stage artefact is
      re-read in a FRESH instance **cold AND preloaded, one condition per child process**
      (`tools/bench/diag_d1_execstate_preload.py:26-28`, `:96-97` — four readings taken in one instance contaminate
      each other, because reading one copy loads the very hierarchy the next read would have had to resolve), and a
      preloaded 1 stays necessary-never-sufficient. CROSS-LINKING was never measured;
      `tools/recipes/stage_d1_s1.py` phases A/B measure it directly — a no-edit COM save under preload, then the
      saved file's (cold, preloaded) pair against a pristine byte copy's. **Until that arm returns, preload-then-save
      is permitted ONLY for stage artefacts under `claudeDev`.**
    - (d) **`allow_broken=True` is BANNED in every stage script** — it is the one flag that can reach `gui_save`.
    - (e) **Stage boundaries fall at LEGAL states.** A stage that deletes a node whose outputs are consumed leaves
      bare required inputs, i.e. an unsaveable VI, so **delete-and-re-drop is ONE stage**. S1 is therefore the
      fixture TIFF writer ONLY (`#22700`, `#23020` — v7 `s1t()` `:728-751`, contract `:74-75`); v7 `s1d()`'s three
      re-dropped subVIs (`#5058 GPU_kernel_v1.vi`, `#48 ASI_adjust focus-subvi.vi`, `#376 save trace.vi`,
      `:754-784`) move into the stage that re-drops them. This reorders build operations only — rule 1a untouched.
    - (f) **S1 deletes TWO of the four 2026-09-01 fixture nodes, deliberately** (prior-art A4,
      `archive/peer/2026-09-19-priorart-d1-s1-stage.md`). `#22703` / `#23175` (`docs/fixture-recording.md:15-20`)
      STAY, because every pinned count downstream — SubVI 98→97, Function 181→180, Node 626→624, Wire 1902→1899 —
      is the measured contract of the two-node deletion, and widening it would invalidate the chain with no
      measurement behind it. Removing the other two is a later stage with its own contract, recorded as an OPEN
      item; it is not an oversight.
    - (g) 🔴 **THE ACCEPTANCE REFERENCE FOR A STAGE ARTEFACT IS THE ORIGINAL'S SUBVI TABLE, NEVER A BYTE COPY —
      gate B as first written compared against the defective side.** MEASURED, cycle 46
      (`tools/bench/s1_subvi_paths.log`, 15/0, three conditions each in its own child process and its own LabVIEW
      instance; artefact `tools/bench/s1_subvi_paths.json`): the COM-SAVED copy matches the ORIGINAL on **all 98
      SubVI calls, name and path, byte for byte**, with **zero** rows into `claudeDev\background VIs_COPY\`, while
      the PRISTINE BYTE COPY re-binds **22** calls into `claudeDev\background VIs_COPY\`, loses **8** outright and
      reads 7 rows as empty (uid 0, name `''`, path `''`) — tables at `:369-395`. That is why a byte copy reads
      `ExecState 0` COLD and the saved copy reads 1: Pre-decided 14a's "a cold read measures subVI linkage" stands
      and now has its specific cause. **So `shutil.copy2(ORIGINAL, claudeDev\…)` produces a SILENTLY RE-BOUND VI**,
      and every stage gate compares against the ORIGINAL, never against a copy. The byte copy stays as a logged
      control only. `claudeDev\background VIs_COPY\` holds 94 `.vi` files; the 17 names it shares with the
      original's own subVI locations are **md5-identical today** (`:397-450`), so nothing has computed differently
      yet — it is an unmanaged duplicate hierarchy sitting on the build path, recorded as an OPEN item.
    - (h) **Rule 1a is de-risked on the linkage channel but NOT closed.** The mandatory failed-prediction review
      (`archive/peer/2026-09-19-s1-saved-copy-cold-execstate.md`, ANSWERED, claude/hypothesis opus max, $4.2400,
      590 s) named three ways a save could change computation: subVI re-binding — now **measured excluded** by (g);
      typedef re-instantiation persisted on save; polymorphic/Express regeneration. The structural census is delta 0
      on all nine classes (`tools/bench/s1_savedcopy_census.log:55-64`) and the saved-version bytes are unchanged,
      but CLAUDE.md rule 1a says counts and `ExecState` prove nothing about computation. **The remaining channels are
      closed by the review's T2 — an OFFLINE RSRC block-level diff of the two files, no LabVIEW and no lock — which
      is the next cycle's first act.** Until T2 has run, no stage artefact is promoted beyond `claudeDev`.
    - (i) **The static audit's gate S6 is an unsound proxy, but item 17's actual constraint IS met — judgement,
      cycle 46; do not re-open it.** The audit asserts "one `remove_bad_wires_scripted` outside any loop" by a
      spelling scan, and the mandatory peer (`archive/peer/2026-09-19-staticaudit-falsepos.md` §1b) measured that
      `tools/recipes/stage_d1_s1.py:654` sits inside `phase_c`, dispatched from the PHASE-SELECTOR `for` at
      `:788-789` — so the scan establishes nothing. What item 17 actually bans is a VI-wide reaper called from
      inside the ROW LOOP of a multi-row wiring pass. Phase C has no row loop: it deletes two pinned uids and calls
      the reaper ONCE, which is precisely the shape item 17 EXONERATES (`build_d1_routeb_v5.py:694`, executed by
      run 5 with its rows wired). The recipe complies; the gate's WORDING is what is wrong — it should read "not
      inside a row loop". Left as a known-weak check rather than rebuilt (user, 2026-09-18 08:53, no more devices).
    - (j) **A self-test that a gate itself mandated consumed the last build-budget slot and cost cycle 46 its
      deliverable.** `tools/logclass.py` counts `selftest_*.log` as a build (its docstring records that as known and
      deliberately unfixed), so the regression check for the stop-record repair took slot 10 of
      `guard_cycle.CYCLE_BUILD_BUDGET = 10` and `stage_d1_s1.py --phases CD` could not launch. Clearing the budget
      means running the retrospective, which permanently marks the session retro-done (OPEN 54(a)) — so the run
      cannot happen in the same session. **The loop-breaking move is simply that the NEXT session launches it as its
      first act**, with the stop record already ALLOW. Recorded as a finding for the retrospective; NOT repaired,
      and no device built.

## Pre-decided — ADDED 2026-09-20 (cycle 48, after S1 was DELIVERED)

30. **S1 IS DONE, and S2 IS THE DELETE + LOOPS + RE-DROP AS ONE STAGE, whose FIRST PHASE MEASURES WHETHER THAT
    STAGE CAN END LEGAL.** Judgement, cycle 48, 2026-09-20, from v7's own source and header contract — not from a
    preference. S1's artefact is on disk: `claudeDev\D1_s1_copy.vi`, md5 `3e3d23cefd3a334001aa9d6156bf1aee`,
    474,202 B, 20/20 gates, `tools/bench/stage_d1_s1_cd.log:115-346`.
    - (a) **Contents and the net contract**, from `tools/recipes/build_d1_routeb_v7.py:76-84`: delete `#5058`,
      `#48`, `#376` (`s1d`, `:754-785`, SubVI 97→94, every wired terminal captured first at `:766`) · create 3
      While loops on `Diagram #686` (`s2`, `:788-813`, `WhileLoop 3→6`, `Diagram 170→173`, `#637` still owning
      `#6810`/`#22082`/`#12589`/`#11639`/`ControlTerminal #642`) · re-drop the three into the three new loop
      bodies (`s2d`, `:815-848`, SubVI 94→97). 🔴 **The NET over the stage is SubVI 97 → 97, WhileLoop +3,
      Diagram +3.** Pre-decided 22's row "+3 loops +3 subVIs" describes the `s2d` drops, not a net change; a gate
      asserting SubVI 100 would be wrong. `docs/d1-route-b-plan.md` §7's Diagram **174** counts a fourth, pool,
      loop that is not built — 173 is the number for this stage (`build_d1_routeb_v7.py:78-83`).
    - (b) **Why ONE stage.** Pre-decided 29(e): a stage that deletes a node whose outputs are consumed leaves bare
      required inputs, i.e. an unsaveable VI, so delete-and-re-drop is one stage. v7 separates them across three
      calls (`:2742` `s1d` → `:2744` `s2` → `:2746` `s2d`) and its uid-reuse note at `:850-855` depends on that
      order — **the order is preserved INSIDE the stage; it is the stage boundary that moves, not the sequence.**
    - (c) **Input, output, skeleton.** Input is `claudeDev\D1_s1_copy.vi`, gated against md5
      `3e3d23cefd3a334001aa9d6156bf1aee` before any edit; output is `claudeDev\D1_s2_loops.vi`. The script is
      `tools/recipes/stage_d1_s2.py`, copied from `stage_d1_s1.py`'s skeleton — `main()`/`--phases` `:763-800`,
      `gate()` `:258-265`, `class Preload` `:332-358`, `md5()`/`file_facts()`/`orig_gate()` `:272-375`,
      `fresh()` `:317-330`, `cold_subvi_table()`/`compare_subvi_tables()` `:377-428` — with ONE substantive
      change: `:623-625`'s `shutil.copy2(ORIGINAL, TARGET)` becomes a copy **from the S1 artefact**. The ORIGINAL
      stays the acceptance reference for everything S1 did not change (29(g)); the S1 artefact is the reference
      only for the two deleted fixture nodes.
    - (d) 🔴 **PHASE A IS A MEASUREMENT AND EDITS NOTHING — it is written and run BEFORE phases C/D exist.** This
      is the shape that made S1 work (phases A/B measured the save route; C/D built). Four facts, all read on
      `D1_s1_copy.vi` with the ORIGINAL preloaded read-only (Pre-decided 14a), saved as a DATA artefact
      `tools/bench/s2a_legality.json` + its log:
      - **A1 — why delete-and-re-drop at all?** The other 21 nodes are relocated with `move_in`; these three are
        deleted and re-dropped. Read what `move_in` does to a SubVI node's owner chain and wires versus
        `drop_subvi`, from our own measured capability files, and say whether `move_in` reaches `Diagram #686`'s
        new loop bodies. **If it does, S2 ends legal with no scaffolding at all** — that is the cheapest possible
        stage boundary and it must be checked before the expensive one is built.
      - **A2 — the connector panes.** For `#5058` (`claudeDev\GPU_kernel_v1.vi`), `#48`
        (`<vi.lib>\Madcity\ASI_adjust focus-subvi.vi`) and `#376` (`<vi.lib>\background VIs\save trace.vi`):
        every connector-pane terminal and whether it is **Required / Recommended / Optional**. A freshly dropped
        subVI breaks the VI only on an unwired **Required** input; Recommended and Optional do not.
      - **A3 — the loops' own legality.** Three new While loops with unwired conditional terminals are a
        compile-time break (Pre-decided 16(a)). Report which ALREADY-BUILT ops reach a While loop's conditional
        terminal and place a Boolean constant on a diagram — by name, from `docs/toolkit-capabilities.md` and
        `docs/NAMES.md`. **No new op and no new device** (Pre-decided 2); if the existing set cannot do it, that
        is an `OPEN:` for judgement, not a licence to build one.
      - **A4 — the starting state.** `D1_s1_copy.vi`'s md5 and its `ExecState` COLD and PRELOADED, each in its own
        child process (29(c)). S1 measured COLD **1** and PRELOADED **1** (`stage_d1_s1_cd.log:153`, `:155`) —
        confirm it has not moved.
    - (e) **BOTH BRANCHES ARE DECIDED HERE, so the material session applies whichever A returns without coming
      back for judgement** (the Pre-decided 28 pattern):
      - **A1 says `move_in` reaches the new loop bodies** ⇒ S2 is `s2` (loops) then `move_in` for the three, no
        delete and no re-drop. Contract: SubVI 97 unchanged throughout, WhileLoop 3→6, Diagram 170→173.
      - **A1 says it does not, and A2 finds no unwired Required input on any of the three** ⇒ S2 is
        `s1d` → `s2` → `s2d` as in (a), with the (f) scaffold, saving `D1_s2_loops.vi`.
      - **A2 finds an unwired Required input on one of the three** ⇒ that one is LEFT ALONE in S2 — neither
        deleted nor re-dropped — and its delete + re-drop + wire become their own later stage, because splitting
        its pair is exactly what 29(e) forbids. S2's contract becomes SubVI 97 → 97−k → 97 for the k it handles.
      - **A3 finds no built route to the conditional terminal** ⇒ S2 stops after phase A and saves the DATA
        artefact; the boundary question comes to judgement. This is the only branch that ends without a VI.
    - (f) **The temporary conditional-terminal constant is `True`, never `False`.** Where a new While loop must be
      left unwired until S3w, its conditional terminal carries a temporary Boolean constant so the VI stays
      saveable, and S3w removes it when the real stop wiring lands. **`True`** because if the scaffold ever
      survives into a run, a loop that executes once is a visible, harmless failure, while `False` on a
      "Stop if True" terminal is an instrument that hangs. This is scaffolding on loops the original does not
      have — rule 1a is untouched, no per-bead maths and no original wire is involved.
    - (g) **Legality is not optional and it is not `allow_broken`.** `tools/gscript.py:2065-2071` reaches
      `SaveInstrument` only at `ExecState != 0`, `allow_broken=True` is banned (29(d)), and `gui_save` has failed
      at eight logged sites. A stage that cannot end legal saves a DATA file (Pre-decided 25 finding B1) and says
      so in its log — it does not save a broken VI and it does not pretend it saved one.

31. **S2 IS BRANCH 1 — LOOPS, THEN `move_in`. Phase A shrinks from a measurement to a RECORDING, because the
    prior-art review found every one of its four questions already answered in our own files.** Judgement, cycle 49,
    2026-09-20, disposing `archive/peer/2026-09-20-priorart-d1-s2-stage.md` (ANSWERED, opus/high, eight slugs, no
    `novel`). All eight findings were accepted; none was refuted. 30 stands as written — this fixes the recipe that
    implements it and fixes one factual error inside 30(d).
    - (a) 🔴 **`#5058` IS THE CPU KERNEL, NOT THE GPU KERNEL. 30(d)'s parenthesis `(claudeDev\GPU_kernel_v1.vi)`
      IS WRONG and is corrected here** (`refuted-already`, citing `docs/d1-route-b-plan.md:135` and
      `docs/d1-build-plan.md:287`): in the ORIGINAL — and therefore in `D1_s1_copy.vi`, which changed only the TIFF
      fixture — uid `#5058` is the **CPU** kernel `Track N beads four-fold over-kernel-v3.vi`. Relocating it is
      correct and is what S2 must do; **logging it as `GPU_kernel_v1.vi` is not**, and a log that misnames what it
      moved is the `unreported-fact` class. So: the recipe carries the true name, and a gate reads the VI name at
      `#5058` on the artefact and **FAILS the stage** if it is not `Track N beads four-fold over-kernel-v3.vi`.
      **Swapping the CPU kernel for `GPU_kernel_v1.vi` is its own later stage** with its own rule-1a argument; it is
      not smuggled inside a loop restructure, and nothing in S2 assumes it has happened.
    - (b) **A1 is SETTLED, not measured** (`settled-already`): `move_in` already lands nodes into loop bodies created
      in the SAME run — 21 such landings, `tools/bench/build_d1_routeb_v7_run10.log:116-173` and `:70-76`,
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
      names files that already answer it for the input that matters — `docs/d1-route-b-plan.md:148`, `:154`,
      `:158-159`; `docs/d1-build-plan.md:523-536`; `docs/NAMES.md:564-565` — which phase A cites rather than probes.
    - (d) 🔴 **A3's `a3_route_exists = FALSE` PREDICTION WAS WRONG** (`contradicted`): three routes from a Boolean to
      a While loop's conditional terminal are already measured at `ExecState 1`, and the recipe's candidate list
      (`stage_d1_s2.py:573-581`) simply omitted the obvious one — **`OpExitWhile_v0`, `docs/toolkit-capabilities.md:31`**
      (also `:63`, `:64`, `:66`). **`OpExitWhile_v0` is the scaffold of record for 30(f)**, applied to each NEW
      loop's own conditional terminal. The recipe's `_boolean_sink` (`:831-843`) is DELETED: it chose a sink by a
      regex over terminal *names* among the dropped subVIs, which under branch 1 has no sink to find at all — that
      is the `already-failed` finding, and it is why "three empty While loops" is measured at `ExecState 0`
      (`docs/toolkit-capabilities.md:67`). The gate is unchanged and absolute: **each of the three new loops has its
      conditional terminal wired to a constant TRUE before the stage saves.**
    - (e) **30(f)'s `True` is a requirement on the VALUE delivered at the conditional terminal, not on the object
      being a literal constant.** Any ALREADY-BUILT route qualifies if it (i) leaves the terminal wired, (ii)
      delivers constant TRUE, and (iii) adds no new unwired Required input of its own. The reason in 30(f) is
      physical — a scaffold that survives into a run must execute the loop once and exit, never hang — and a node
      that computes TRUE satisfies it exactly as a `True` constant does. A route that can only deliver **FALSE**
      does NOT satisfy 30(f) and is refused; that is the hang the clause exists to forbid.
    - (f) **A4 drops its two ExecState child processes** (`already-measured`): the pair is already recorded on this
      exact md5 at `tools/bench/stage_d1_s1_cd.log:153` (COLD 1) and `:155` (PRELOADED 1), and the md5 gate on
      `3e3d23cefd3a334001aa9d6156bf1aee` already proves the file has not moved. Phase A keeps the md5 gate and cites
      those two lines; the PRELOADED state is read anyway inside C/D, where the save route needs it (29(d)).
    - (g) **Phase C reuses v7's already-passing step functions rather than re-deriving them** (`already-built`,
      `helper-exists`): the construction steps have passed their gates in the real VI
      (`tools/bench/build_d1_routeb_v7_run10.log:70-76`, `:106`). What is genuinely new — and what this stage is
      *for* — is the **stage boundary**: copy from the S1 artefact, gate on its md5, save `D1_s2_loops.vi`.
    - (h) **The net contract is unchanged from 30(a) and is now the contract of branch 1 exactly: SubVI 97 → 97
      (no subVI is created or destroyed at any point in the stage), WhileLoop 3 → 6, Diagram 170 → 173.** Every
      comparison is against the ORIGINAL, never against a copy (29(g)).
    - (i) **If the stage cannot end legal it saves `tools/bench/s2a_legality.json` and says so** (30(g)). It never
      saves a broken VI, never uses `allow_broken=True`, and never invents an op to get past a gate (Pre-decided 2).

32. **THE SCAFFOLD GOES ON AFTER `move_in`, AND `OpExitWhile_v0` IS REFUSED FOR IT.** Judgement, cycle 49,
    2026-09-20, answering the two `OPEN:` lines the material session raised while applying 31. This replaces 31(d)'s
    naming of `OpExitWhile_v0` as "the scaffold of record"; everything else in 30 and 31 stands.
    - (a) 🔴 **`OpExitWhile_v0` MUST NOT be the S2 scaffold.** Measured: it sources the conditional terminal from a
      **front-panel Boolean control by name** (`tools/gscript.py:1083-1114`). That fails 31(e) twice over — it
      delivers the operator's value, which is **FALSE at load** (the exact "instrument that hangs" 30(f) forbids),
      and it would add readers of an ORIGINAL front-panel control in three new places, which is the original's
      wiring and not scaffolding. **Do not wire `"stop (end)"`, or any other original control, into a new loop.**
      The assumption the material session proceeded under (`SCAFFOLD_STOP_CONTROL = "stop (end)"`) is OVERTURNED.
    - (b) **The order inside the stage is: create the three loops → `move_in` the three nodes → scaffold the three
      conditional terminals → save.** This dissolves the whole difficulty. The body-node-addressed routes
      (`OpCreateConstOnTerm_v0`, `OpCreateEqual_v0` → `OpStopFromNode_v0`) were unreachable only because an empty
      body has no node to address; after `move_in` each new body holds its relocated node. **Intermediate
      illegality inside a stage is expected and permitted** — only the SAVE requires `ExecState != 0`
      (`tools/gscript.py:2065-2071`, 29(d)), and that is the whole reason 29(e)/30(b) make this one stage.
    - (c) **A3 goes back to being a real MEASUREMENT, over every built op, not a one-op availability check.** Phase
      A reports, for each candidate — `OpCreateConstOnTerm_v0`, `OpCreateConst_v0`, `OpCreateEqual_v0`,
      `OpStopFromNode_v0`, `OpExitWhile_v0`, and anything else in `docs/toolkit-capabilities.md` that writes a While
      loop's conditional terminal or creates a constant — (i) its exact inputs, (ii) what it addresses (a terminal
      reference, a body node, or a panel-control name), (iii) whether the Boolean it delivers is a **constant** and
      whether its value can be set **TRUE** by that op or by another already-built op, (iv) the measured evidence
      line. No new op and no new device (Pre-decided 2); phase A still edits nothing.
    - (d) **Selection rule, applied mechanically by the recipe from A3's own table** — judgement is already spent
      here, so the material session does not come back: **(1)** an op that puts a Boolean **constant TRUE** on the
      conditional terminal wins; **(2)** failing that, `OpCreateEqual_v0` → `OpStopFromNode_v0`, and **only if** its
      delivered value is provably constant TRUE from its own measured record (`tools/bench/build_opsentinel_ops_run3.log`
      F5c/F6) — a comparison whose value is not provable from that record does not qualify; **(3)** nothing else.
      **If neither qualifies, the stage STOPS after phase A and saves `tools/bench/s2a_legality.json`** (30(e)
      branch 4, 31(i)). That is a legitimate end to this cycle: it leaves a file, which is what the user's binding
      rule of 2026-09-19 asks of every cycle, and it hands judgement a real measurement instead of a guess.
    - (e) **v7's exclusion of `#5058` / `#48` / `#376` from its 21 `move_in` landings does NOT send S2 back to
      delete-and-re-drop.** 31(b) said only an exclusion *with a stated cause* could; the cause v7 states
      (`tools/bench/build_d1_routeb_v7_run10.log:53`, `docs/d1-route-b-plan.md:62-72`) is that a fresh drop removes
      32 named re-wire rows from the cut census — a **bookkeeping preference about which wires route B wants cut
      later**, not a finding that `move_in` fails on these nodes. Judgement goes the other way on rule 1a: keeping
      the existing wires is strictly safer than destroying and hand-rebuilding 32 of them, and hand re-wiring at
      that scale is the exact stage that killed v3→v7 ten times over five cycles. **The 32 rows are S3w's work,
      which is the re-wiring stage, and they are not smuggled into S2 by deleting nodes early.**
    - (f) **Rule 1a, stated for this stage:** `move_in` turns each crossing wire into a While-loop tunnel, and While
      loop tunnels do not auto-index unless explicitly told to, so values pass through unchanged. Phase D RECORDS
      the indexing state of every new tunnel if any built op can read it, and says plainly in the log if none can.
      The three loops are empty of logic, run once under the TRUE scaffold, and S3w removes the scaffold — no
      per-bead maths and no original wire is altered by S2. ⚠️ **(f)'s first sentence is WRONG — see 33(a).**

33. **CORRECTION TO 32, FROM THE ROUND-2 PRIOR-ART REVIEW: `move_in` SEVERS WIRES, IT DOES NOT TUNNEL THEM.**
    Judgement, cycle 49, 2026-09-20, from `archive/peer/2026-09-20-priorart-d1-s2-stage-r2.md:1250` citing
    `docs/d1-route-b-plan.md:57-58` and `:67`. A wrong sentence in a `Pre-decided` section is worse than no
    sentence, so it is corrected here rather than left for a later session to trip over.
    - (a) **32(f)'s "turns each crossing wire into a While-loop tunnel, so values pass through unchanged" is FALSE.**
      A move severs the node's wires; the relocated node lands in the new body **unwired**. The tunnel-indexing
      reading stays worth taking (`gscript.tunnels` / `OpTunnels_v0` returns `index_mode`,
      `tools/gscript.py:941-978`) — it simply has nothing to read when no tunnel is created, and the recipe must say
      that rather than imply a pass-through that does not happen.
    - (b) **32(e)'s CONCLUSION survives; its REASON does not.** Branch 1 is still right, but not because it
      "preserves 32 wires" — it preserves none. It is right because it **keeps the node's identity**: `move_in`
      carries uid, configuration and connector state across, while delete-and-re-drop destroys and re-creates the
      call (SubVI 97 → 94 → 97) and makes every gate that counts subVIs a moving target. The 32 named re-wire rows
      are S3w's work under **either** route, which is exactly why v7's stated reason for excluding these three
      (`tools/bench/build_d1_routeb_v7_run10.log:53`, `docs/d1-route-b-plan.md:62-72`) is a bookkeeping preference
      and not a finding against `move_in`.
    - (c) 🔴 **THE STAGE BOUNDARY IS RE-OPENED, and phase A is what closes it.** If a moved node lands unwired, then
      branch 1 meets the same wall 29(e) named for delete-and-re-drop: bare required inputs ⇒ `ExecState 0` ⇒
      `gscript.save()` cannot reach `SaveInstrument` (`tools/gscript.py:2065-2071`) ⇒ **the stage cannot end legal,
      whatever is done to the conditional terminals.** So A2's required-ness question is load-bearing again after
      all, and 31(c)'s "moot" is withdrawn. **Phase A must answer, from already-measured files and without editing
      anything: does a `move_in`'d node land unwired, and does an unwired Required input on any of `#5058` / `#48` /
      `#376` follow from it?** Until that is read, no S2 shape is authorised beyond phase A.
    - (d) **This does not license a bigger stage.** If phase A shows S2 cannot end legal in any shape, the stage
      stops after A with `tools/bench/s2a_legality.json` (30(e) branch 4, 31(i)) and judgement re-cuts the boundary
      — the likely answer being that the loops, the moves and their re-wiring are one stage, which is 29(e) applied
      honestly rather than a scope increase. Never `allow_broken=True`, never a new op (Pre-decided 2).

## Pre-decided — ADDED 2026-09-20 (cycle 50): the boundary re-cut 33(d) asked for

34. **S2 IS SMALLER THAN ANY SHAPE CONSIDERED SO FAR: THREE EMPTY WHILE LOOPS, EACH SCAFFOLDED BY
    `OpCreateEqual_v0` → `OpStopFromNode_v0`, SAVED — NO `move_in`, NO QUEUES, NO RE-WIRING.** Judgement, cycle 50,
    2026-09-20, from the mandatory failed-prediction review
    `archive/peer/2026-09-20-d1-s2-boundary-recut.md` (ANSWERED, claude/hypothesis opus max, $3.3597, 492 s), which
    refuted **both** of this cycle's own claims. Everything in 30/31/32/33 that this item does not name stands.
    - (a) 🔴 **`stop_after_a` FALLS: 32(d) rule (2) WAS NEVER EVALUATED, AND IT QUALIFIES.** Cycle 49 concluded S2
      cannot end legal because rule (1) — an op that places a Boolean *constant* TRUE on a conditional terminal —
      has no winner. That is still true, and it is beside the point: rule (2)'s pair is **already measured at
      `ExecState` 1**. `docs/toolkit-capabilities.md:63-64` records `OpCreateEqual_v0` placing `Equal?` with **both
      operands taken from one existing node's output terminals** and `OpStopFromNode_v0` driving a While loop's
      conditional terminal from its Boolean (term 119, wire 0 → 387), on a scratch that reads `ExecState` 1;
      `OpCreateEqual_v0` is 23/0 and T5 is closed by measurement in `tools/bench/build_opsentinel_ops_run3.log`
      (F5c/F6). `x == x` is constant TRUE for every non-NaN scalar, which is exactly the provability 32(d) rule (2)
      demands, and it is the harmless-once-through direction 30(f)/31(e) require — never FALSE, never a hang.
    - (b) 🔴 **AND THE OPERANDS MAY SIT ON THE OUTER DIAGRAM** (`docs/toolkit-capabilities.md:64`, measured
      `LoopTunnel 0 → 2`). So the scaffold does **not** need a node inside the body, and **32(b)'s premise is
      false**: "the body-node-addressed routes were unreachable only because an empty body has no node to address"
      was never true of this pair. A loop can therefore be created, scaffolded and **saved while its body is still
      empty**, before any node moves. 32(b)'s ordering (loops → `move_in` → scaffold → save) is superseded by:
      **loops → scaffold → save.**
    - (c) **The operand must be SCALAR.** An array operand yields a Boolean **array**, which a conditional terminal
      cannot take (round-2 prior art B2; `docs/frame-loop-wire-graph.md:171` measures `#5058` t3
      `Bead is good? array out` as an ARRAY — the ordinal-picked operand cycle 49 removed for the same reason).
      Pick the operand by NAME from a measured scalar output on `Diagram #686`, never by ordinal.
    - (d) **My own re-cut — "one complete loop per stage, stop wiring included" — is REFUTED and withdrawn.** It
      ended each span at the *real* stop condition instead of at a scaffold, inflating ~3 operations into ~20 and
      pulling the re-wiring pass that killed v3→v7 back inside the first stage. The peer named it as a smuggled
      premise and it was.
    - (e) **The chain after S2, one atomic step per relocated node.** `move_in` severs wires (33(a)), so a moved
      node lands unwired and may bare a Required input: the move and that node's re-wiring cannot be split, but
      **different nodes can**. Order `#48` (7 cut rows) → `#376` (12) → `#5058` (13) — smallest first, which is
      safe because the inter-loop dependency is **runtime only, not build-time**: all eight `Obtain`s sit at top
      level on `Diagram #686` (`docs/d1-build-plan.md:568-569` §9 Scope + the `S1q` gate at `:651` — re-measured 2026-09-20, was `:593`; `tools/recipes/build_d1_routeb_v7.py:100`), so `#48`'s
      loop builds with `#5058`'s absent. Row counts and every cut terminal are measured in
      `tools/bench/d1_rewire_sources.json` (109 cut terminals, 109 resolved; 32 rows over these three nodes,
      `docs/d1-route-b-plan.md:67`).
    - (f) 🔴 **NO INTERMEDIATE ARTEFACT MAY EVER BE RUN.** A loop whose real stop condition is a sentinel on a
      queue with no producer blocks forever; a loop still on its `x == x` scaffold runs once and exits. Both are
      legal to SAVE and neither is legal to RUN. Every stage script states this in its log, and no harness may
      open an intermediate `D1_s*.vi` and press Run.
    - (g) 🔴 **THE DESIGN GAP IS REAL, BUT IT IS NOT "no element types were designed" — IT IS THAT SIX OF THE EIGHT
      QUEUES HAVE NO `src_name` THAT EXISTS ON THIS COPY.** This cycle opened by measuring that the element types
      ARE on file — `docs/d1-build-plan.md:544-558` §9 (the eight-queue table), `:623-639` §9a (re-measured 2026-09-20, was `:565-581`) (the sentinel
      convention), adopted verbatim at `docs/cycle15-plan.md:118-123`, with a producer-consumer core actually built
      at `docs/stage2-assembly-step-c.md:18-30` — and concluded that
      `tools/recipes/build_d1_routeb_v7.py:131-135`'s "undesigned row" was a stale comment. **That conclusion is
      overturned by the same review.** `queue_node('obtain')` types a queue from a `(node, named output terminal)`
      pair (`tools/gscript.py:1122`), and §9 resolves to such a pair for **at most 3 of 8**: "the kernel's own
      outputs" is not a `src_name`; ~~`#10757 .element` names a `Dequeue` the build has yet to create~~ 🔴 **THAT HALF-SENTENCE IS WRONG — CORRECTED BY 34(m) BELOW (cycle-51 judgement, 2026-09-20); the strike-through keeps the original readable** — which is
      where run 3 died (`tools/recipes/build_d1_routeb_v7.py:113-116`); and `docs/cycle15-plan.md:120-121` sources
      `Q_res`/`Q_good` from the **GPU** kernel, a node S2 never places (31(a)). The two files also disagree on a
      type: `Q_focusback` is 1 DBL at `docs/d1-build-plan.md:555` and Bool at `docs/cycle15-plan.md:122`.
      **RESOLVED HERE: 1 DBL.** `#10407` t6 is `position [internal units]`, measured numeric
      (`docs/frame-loop-wire-graph.md:410`), and it is the wire that feeds `#48` t4 `In position` through the
      original's own shift register — a position, not a flag. The binding document was the wrong one.
      ⇒ **The queue design work owed is a RESOLUTION TABLE, not a new design**: for each of the eight queues, the
      `(uid, exact terminal name, diagram)` that exists at the moment its `Obtain` is placed, or the stage that
      must run first for it to exist. It is a document, it needs no LabVIEW, and it is owed **before the sentinel
      stages** — not before S2, which uses no queue at all.
    - (h) **The strongest rival explanation for the ten v3→v7 deaths is ADDRESS INVALIDATION BY SELF-MUTATION**, and
      it is now a binding constraint on every re-wiring stage: rows addressed by terminal/diagram **INDEX** while
      the build's own tunnel creation and wire severing drift those indices (`docs/toolkit-capabilities.md:70` T2c2,
      a stale index silently wiring a wrong-but-valid source past the sink rule —
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
      calls: create one While loop on `Diagram #686` → `OpCreateEqual_v0` with both operands from ONE measured
      **scalar** output terminal of a `Diagram #686` node → `OpStopFromNode_v0` onto the loop's conditional
      terminal → read `ExecState` (ORIGINAL preloaded read-only, 14a) → `move_in` `#48` → read `ExecState` again.
      Either branch leaves a file: the readings, plus the saved copy whenever the state is legal. A first reading
      of 1 **falsifies** "S2 cannot end legal"; a second reading of 1 would mean even the move separates from the
      re-wiring and the stages cut finer still.
    - (l) ✅ **(a)/(b)/(e) ARE NOW MEASURED, NOT CITED — the test of (j) RAN, 2026-09-20.**
      `tools/bench/diag_s2_scaffold.py` → `tools/bench/diag_s2_scaffold.log`, `…/diag_s2_scaffold.json`, 13 pass /
      1 fail (the one FAIL is step 7's save, which is the expected reading, not a defect):
      - ONE new While loop **#23032** (body Diagram **#23058**) on `Diagram #686`, conditional terminal **#23080**
        driven through wire **23145** by Comparison **#23035**, both operands from the single scalar output of
        node **#8486 `x+1`** ⇒ **`ExecState` 1**, and `gscript.save()` reached `SaveInstrument`:
        `claudeDev\DIAG_s2scaffold_030829.vi`, md5 `eddb3e15e5b0aa673fc2bf59eadd67e2`, 475,422 B, re-read in a
        fresh process **COLD 1 / PRELOADED 1**. **"S2 cannot end legal" is FALSIFIED by the machine.**
      - Then `move_in` `#48` (7 terminals, all 7 wired beforehand) into that body ⇒ **`ExecState` 0**, and the save
        was refused verbatim (`refusing to save a BROKEN VI - SaveInstrument blocks forever on one`);
        `allow_broken` never set, `gui_save` never called. **(e)'s atomicity of move+re-wire is measured, not
        assumed.** ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` before and after; refs 8 opened / 8 closed /
        0 live; no VI was run.
      - ⚠️ **The operand pre-selected in the brief was WRONG and the census-order fallback is what found the right
        one.** `#637 'frame index'` is not a named source terminal on `Diagram #686` — `#637`'s outer feed is an
        UNNAMED tunnel (`out_name ''`) — so a name resolved from a *wire* table is not automatically a `src_name`.
        Resolve operands from the diagram's own output-terminal census, as the diagnostic does.
      - ✅ **A substitution judgement CONFIRMS:** readings 1 and 2 were taken **in-instance under `Preload`**, not
        in a child process, because the child form restarts LabVIEW and can therefore only read a file on disk —
        an UNSAVED in-memory edit cannot survive it. That is correct and is now the rule: **the child-process
        `ExecState` read of 29(c) applies to SAVED files; an unsaved intermediate is read in-instance under
        preload.** The saved artefact was read both ways and agreed (1 / 1).
    - (k) **Operating note carried from the cycle-48 retrospective:** `tools/hash_probe.py` is the read-only
      md5/sha256/size probe for exactly these gates — `py tools/bgrun.py --material … -- python -u
      tools/hash_probe.py <path> …`, one `HASH <path> | exists= | size= | md5= | sha256=` line per path, no COM and
      no LabVIEW. Use it for every artefact md5 a stage must record.
    - (m) 🔴 **CORRECTION to (g), by the cycle-51 judgement session, 2026-09-20 — `#10757 .element` is NOT an
      unbuilt `Dequeue`.** DECISION: the struck half-sentence at `docs/cycle27-plan.md:916` was wrong on the
      mechanism. `#10757` **is** an `Index Array [array, element, index]` — MEASURED: `element` is one of its three
      real, named terminals (`docs/frame-loop-wire-graph.md:86`), so `.element` IS a named output terminal and
      `queue_node('obtain')`'s `(node, named output terminal)` requirement (`tools/gscript.py:1122`) is satisfiable
      by it in principle. **The obstacle is the DIAGRAM, not the name**: `#10757` is a body node of `#637` that
      relocates into loop 1.2 (`docs/d1-build-plan.md:295`), so it is not on `Diagram #686` at the moment `Q_focus`'s
      `Obtain` is placed, and on `#686` the same family exports only the ARRAY (`#637` t24 `pos in cal image out`).
      `Q_focus` therefore stays state **C** for a different reason than (g) gave (`docs/d1-build-plan.md:584`).
      Everything else in (g) — "at most 3 of 8", the `Q_focusback` 1-DBL resolution, and the resolution table being
      the work owed — stands unchanged. The original sentence is struck, not deleted, so the record stays readable.

35. **THE QUEUE `element data type` DONOR MUST EXIST BEFORE THE LOOPS START, AND THE SCAFFOLDS MUST BE REMOVED BY
    THE SENTINEL STAGES.** Judgement, cycle 51, 2026-09-20, added after the `Obtain` resolution table was written
    into `docs/d1-build-plan.md:560-616` and the cycle-51 prior-art review of the S2 recipe came back
    (`archive/peer/2026-09-20-priorart-d1-s2-loops.md`, ANSWERED). 34 stands as written; this constrains what the
    queue stages may do with it.
    - (a) 🔴 **DONOR CONSTRAINT — a queue's `element data type` comes from a source available BEFORE the loops
      start (a constant or a pre-loop node), NEVER from a tunnel out of `#637`.** DECISION: every state-**A** pair
      in the new §9 table (`docs/d1-build-plan.md:576-585`) sources from `#637`'s **outer** terminals — output
      tunnels and right shift registers' outside terminals — which carry **post-loop** values only. `element data
      type` is a *wired* input on the created `Obtain Queue` node, so an `Obtain` typed from one of them could not
      produce its refnum until the frame loop had ended, while the loops that need that refnum wait on it: a
      structurally legal `ExecState 1` with a **guaranteed runtime deadlock** (the R1 risk already written at
      `docs/d1-build-plan.md:596-602`). **Rule 1a is NOT engaged**: `Obtain Queue` discards the donor's *value* and
      keeps only its *type*, so changing the donor changes no computation — no per-bead maths and no original wire
      is touched.
    - (b) **WHAT REMAINS IS A MEASUREMENT, NOT A DECISION.** Which donor *shapes* `queue_node('obtain')`
      (`tools/gscript.py:1122`) can actually accept is unknown: the op requires a **named** output terminal, and a
      LabVIEW diagram constant's terminal is **unnamed** — the same `out_name ''` failure cycle 50 hit on `#637`'s
      outer feed (34(l), `docs/cycle27-plan.md:961-964`). So a "use a constant instead" instruction is not yet
      executable. **Until that is measured, NO queue stage is written**; the measurement is a diagnostic under
      `tools/bench/`, not a recipe, and its result comes back to judgement as facts (the material session does not
      pick the donor).
    - (c) 🔴 **SCAFFOLD REMOVAL IS PART OF EACH LOOP'S SENTINEL STAGE, NOT A SEPARATE PASS.** Each `x == x`
      scaffold (34(a)/(b)) adds one `Equal?` and one border tunnel, and **no document named the stage that takes
      them out** — as written they would ride into the delivered VI. DECISION: when a loop's real stop condition is
      wired (the end-of-stream sentinel of §9a, `docs/d1-build-plan.md:623-639`), that same stage **deletes that
      loop's `Equal?` and its border tunnel**, and its gate asserts **`Comparison` −1 and `LoopTunnel` −1 for that
      loop**, measured against the stage's own before-census. **No scaffold survives into the delivered VI.**
    - (d) **TWO GATE REQUIREMENTS NOW BIND EVERY LATER STAGE**, both accepted from the cycle-51 prior-art review
      (`archive/peer/2026-09-20-priorart-d1-s2-loops.md`): (1) a value returned **beside a non-zero error column**
      is reported **UNREAD** — never as a value and never as a silent FAIL (14, `docs/cycle27-plan.md:147-150`);
      (2) **SubVI acceptance is a TABLE comparison against the ORIGINAL, never a class COUNT**, because
      `shutil.copy2` re-binds 22 calls and loses 8 while leaving the count intact (29(g),
      `docs/cycle27-plan.md:629-641`; the built FATAL instrument is `tools/recipes/stage_d1_s1.py:182-188` and
      `:377-400`).

## Pre-decided — ADDED 2026-09-20 (cycle 52): S2 accepted · the donor rule · S3's forced shape

36. **THE QUEUE DONOR MUST BE A NODE — "USE A CONSTANT" AND "USE A FRONT-PANEL CONTROL" ARE BOTH MEASURED
    UNEXECUTABLE, AND THE TYPE CENSUS 35(b) ASKED FOR CANNOT BE TAKEN BY THE BUILT FLEET.** Judgement, cycle 52,
    2026-09-20, from `tools/bench/diag_queue_donor.{py,log,json}` (12/0), `…/diag_queue_donor2.*` (16 gates) and
    `…/diag_donor_census.*` (14/0). 35(a)'s ban on `#637` outer terminals stands; 35(b) is answered as far as the
    fleet can answer it.
    - (a) 🔴 **`queue_node('obtain')` accepts only an object that is in `AbstractDiagram.Nodes[]` AND exposes a
      named source terminal — i.e. a real NODE.** Measured REFUSED, all four shapes: a diagram constant on `#686`
      (`error 1057: To More Specific Class in OpQueueObtain_v0.vi`; the placed constant `#23258` is not in
      `Nodes[]`); a **scalar** front-panel ControlTerminal (`#23124`) and a **cluster** one (`#23493`) — both born
      on `TopLevelDiagram #536`, both relocated onto `#686` by `move_in` with no error, both absent from `Nodes[]`
      with `out_name` empty, both refused with the same 1057; and `OpCreateConstOnTerm_v0` on a `Diagram` container
      (`invoke error 1055`, created uid 0), whose positive control INSIDE `WhileLoop #637` created constant `#23716`
      cleanly ⇒ **the restriction is that op's `Loop.Diagram` downcast, intrinsic to the container class, not the
      call.** Measured ACCEPTED: a node's named output (`#8486 'x+1'` → `Obtain Queue #23032`) and a `#637` outer
      terminal (`current image number`), which 35(a) forbids.
    - (b) **A newly placed donor node is not a free fallback — it must be fully wired or the VI never saves.**
      `build_index_array` alone, one unwired Index Array on the top-level diagram, took a legal scratch from
      `ExecState` 1 to 0, and **deleting the node did not restore it** (`tools/bench/diag_qdonor2_ia.log:17,26-27`).
      The explanation first offered was refuted on its own falsification criterion by the peer-prescribed test
      (`archive/peer/2026-09-20-qdonor2-p8-no-saved-artefact.md`, ANSWERED, claude/hypothesis opus max); the
      surviving alternative — a `Connect Wire`-family (1304) op run perturbing compile state,
      `docs/NAMES.md:912-921` — is **UNVERIFIED and OPEN**. It sits on the queue path, not the move path, so it
      blocks no D1 stage.
    - (c) 🔴 **NO BUILT OP READS `Terminal.DataType`** — `node_terms` gives name/is_source/wire, `report_all` gives
      class/uid/pos/owner, `node_info` gives `Node.Style` for TOP-LEVEL nodes only and `#686` is not top level. A
      reader would be a new op, which Pre-decided 2 forbids. What WAS measured on `Diagram #686`: **24 `Nodes[]`**
      (21 originals + the three S2 loops); **18 of the 24 are independent of `#637`** (`8486, 7201, 781, 250, 6951,
      6409, 8953, 9342, 9179, 28124, 27605, 28670, 25380, 25091, 25149, 23032, 10170, 23041`); the three new loops
      expose **0** named outputs; and all five state-**A** queues name `#637` — the one node that is NOT
      independent of it — while `Q_free`/`Q_work` (IMAQ image refnum) and `Q_focus` (DBL scalar) have no
      `(node, named output terminal)` pair on `#686` at all.
    - (d) **DECISION — the donor is found BY CONSTRUCTION, not by a type reader.** The machine will not report a
      terminal's type, but `queue_node('obtain')` itself either accepts a donor or refuses it, and a created
      `Obtain Queue` can be read back. So the next donor step is a **trial census** over the 18 independent nodes'
      named outputs: attempt the `Obtain`, read back what the queue is typed as. No new op, no inference. It is
      **not on the critical path — no queue stage is written before it, and it waits behind S3.**

37. **S2 IS ACCEPTED, AND S3 IS ATOMIC BY THE MACHINE'S OWN CONSTRAINT: THE WHOLE 1.5 NODE SET MOVES AND IS
    RE-WIRED IN ONE SAVED STAGE.** Judgement, cycle 52, 2026-09-20, from `tools/bench/verify_d1_s2.{log,json}`
    (23/0), `…/diag_movein_set.*` (13/1) and a read of `tools/bench/d1_rewire_sources.json`.
    - (a) ✅ **D1 STAGE S2 IS DELIVERED**: `claudeDev\D1_s2_loops.vi`, md5 `6ff19497f2309e007a214660bb64b911`,
      475,707 B. Re-read FROM THE SAVED FILE: `ExecState` COLD **1** / PRELOADED **1**; census Diagram 173 ·
      WhileLoop 6 · SubVI 97 · Comparison 17 · LoopTunnel 135 · Wire 1905. **Verification level: STRUCTURAL** — no
      VI was run, and 34(f) forbids running an intermediate.
      ✅ **Accepted on TWO independent runs, not one:** cycle 51's own `tools/bench/stage_d1_s2_loops.log` ends
      **35 pass / 0 fail** with `G15 FATAL PASS` and `BGRUN END rc=0 after 776s` (300 lines, written to 04:06), and
      cycle 52's `tools/bench/verify_d1_s2.{log,json}` reaches the same numbers at **23/0**. ⚠️ Cycle 52 dispatched
      that second run believing the first had been killed — it had not; see **37(j)**. The duplication was the
      cost of the error, but the doubled evidence is genuine.
    - (b) 🔴 **`#10170` IS A NEW LOOP THAT REUSED A FREED LOW uid** (`tools/gscript.py:2353-2356`), and rule 1a is
      intact. S1's While loops are `{637, 15173, 25380}`; S2 adds **exactly** `{10170, 23032, 23041}`, all owned by
      `Diagram #686`. Ownership by traversal, never by index: `#23080 → Diagram #23058 → WhileLoop #23032` ·
      `#23246 → #23166 → #10170` · `#23456 → #23405 → #23041`. Every pre-existing loop's conditional terminal and
      the wire on it are **identical in S1 and S2** (`637 → #648/w3457` · `15173 → #15276/w19456` ·
      `25380 → #25410/w1737`), so **no original stop condition was touched**. The three new `Equal?`s each drive one
      new conditional terminal, and all three read back **READ** with empty error columns.
      ⚠️ **The alarm was raised by a REPORTING defect, not a build defect:** `stage_d1_s2_loops.py`'s closing report
      re-read the loops **by array index** — the very thing 34(h) forbids — and printed a pre-existing loop's uid
      beside a new loop's conditional terminal. **Every stage report re-reads by uid or by ownership traversal.**
      ⚠️⚠️ **And the warning was already on file, unread:** `tools/gscript.py:2353-2356` says verbatim *"Nodes[] is
      CREATION order … Newly created nodes reuse low uids (90, 98 seen 2026-09-06 20:0x) and go to the END of
      Nodes[]"*. Both halves of this cycle's scare — a new loop wearing a low uid, and an index read returning the
      wrong object — are that one docstring. Read it before writing any census-order or index-order code.
    - (c) **The SubVI table's one missing row is REQUIRED, not tolerated.** `(diagram 639, node 22700)` is
      `IMAQ Write TIFF File 2`, inserted into the working copy for fixture recording on 2026-09-01
      (`docs/d1-build-plan.md:310`, `docs/fixture-recording.md:17`); the true original has no such node.
      `tools/recipes/stage_d1_s1.py:245-246` hard-codes `PIN_SUBVI_ROWS = 98` and `TIFF_SUBVI_KEY`, `:729` passes it
      as the expected-missing set, and `:738-741` gates ORIGINAL == 98 and artefact == 97. S2 reuses that instrument
      (`stage_d1_s2_loops.py:361`) and reads missing 0 / extra 0 / changed 0, 0 rows into `background VIs_COPY`.
    - (d) 🔴 **`move_in` TAKES ONE NODE PER CALL AND SEVERS EVERY WIRE ON IT, IN EITHER ORDER — there is no "move
      the set and keep its internal wires".** Measured on the real pair `#3529 '- Inc (PgDn)' → #48
      '-Inc reference'` (wire 4833), moving the SOURCE first and the SINK second into body `Diagram #23058`: after
      move 1 `#3529` goes 1 → **0** wired and w4833 reads 1 terminal; after move 2 `#48` goes 7 → **0** wired and
      w4833 reads **0**. The op's `'UID 3'` control is a scalar int (`is_sequence False`) and no array form exists
      — `move_in` is not in `gscript.py` at all, it is `tools/recipes/build_d1_v0.py:318`
      `def move_in(target, uid, dest_diagram_index, position)`, one uid per call. `ExecState` 0 afterwards; the
      save was refused.
    - (e) 🔴🔴 **A WIRE COUNT CAN NEVER DETECT A CUT — every re-wiring gate counts WIRED TERMINALS.** The whole-VI
      `Wire` census stayed **1905 → 1905 → 1905** across both moves and uid **4833 is still in the Wire list**, with
      zero terminals: `move_in` detaches terminals and leaves the Wire object behind. Any stage gated on a Wire
      delta would have reported all green with its wires cut — a live candidate contributor to the v3→v7 deaths.
      S2's `Wire 1899 → 1905` line was REPORTED, not gated, which is why it did no harm.
    - (f) **TWO ADDRESSES CORRECTED, measured:** `#48` and `#3529` sit on **`Diagram #639`** — `WhileLoop #637`'s
      body — **not on `#686`**, and `#3529` is a **`ControlReferenceConstant`**, not a function node. A gate
      assertion written the other way was a drafting error the machine corrected, and it is 34(h)'s own lesson: an
      address is read, never assumed. ~~**No hypothesis review is owed for it** — no explanatory hypothesis drove
      any work, and the observation agrees with `docs/d1-build-plan.md:250`.~~ 🔴 **THAT RULING IS WITHDRAWN by the
      cycle-52 retrospective** (`archive/peer/2026-09-20-retrospective-cycle52.md`, `VIOLATION: device-failed`,
      evidence `tools/bench/diag_movein_set.log:57`): excusing a failed prediction because it looks like a drafting
      error is judgement overriding a mechanical rule, and CLAUDE.md is explicit that one's own successful
      discriminating test does not discharge the mandate. **The P6 review IS owed and is a prerequisite to the S3
      build** — `-Agent claude -Role hypothesis`. The strike-through keeps the withdrawn reasoning readable.
    - (g) 🔴 **DECISION — S3 = `claudeDev\D1_s3_loop15.vi`: move the WHOLE 1.5 FOCUS node set into loop a and
      re-wire it, in ONE script with ONE save.** There is no smaller legal unit: all 7 of `#48`'s cut rows are
      internal to the 1.5 set (`#3529`, `#3560`, `#3447`, `CaseStructure #10407`, and the two shift registers
      `#4334/#4344` VISA and `#4256/#4274` position), **none** of its sources stays on `#686`
      (`docs/d1-build-plan.md:250, :306, :330-332, :340, :359-360`), (d) severs every wire whichever order is used,
      and an intermediate at `ExecState` 0 cannot be saved — so a part-moved set leaves no file, which the split
      rule forbids outright. **The stage is atomic because the machine makes it so, not by choice.** Inside it the
      split rule is honoured the way it can be: a census + readings JSON after each phase, re-wiring in batches of
      10–15 rows, each batch gated on **wired-terminal counts** per (e), and the single `g.save()` at the end with
      `allow_broken` False.
    - (h) **LOOP IDENTITY IS ASSIGNED HERE, because no document assigned it** (a grep over `docs/` for
      `23032|10170|23041` returns one hit, `docs/cycle27-plan.md:951`, about cycle 50's diagnostic loop). The S2
      recipe's labels are a = `#23032` body `#23058` @(2600,2600) · b = `#10170` body `#23166` @(2600,3400) ·
      c = `#23041` body `#23405` @(2600,4200). **DECISION: loop a `#23032` (body `#23058`) IS loop 1.5 FOCUS.**
      b and c are assigned when their node sets are named. The assignment is arbitrary but **binding** — cite this
      line, never re-derive it.
    - (i) 🔴 **`guard_peer` IS BLIND TO THE NEW DIAGNOSTICS' FAILURES, AND THE REPAIR IS AT BOTH ENDS.** Verified
      here, not taken on report: `guard_peer.py:73`'s `FAILURE_RE` ends `^\s*(?:->\s*)?FAIL\b` and `:71` documents
      the fleet's gate format as `  FAIL  `, which it matches — but the cycle-50/52 diagnostics print
      `  **FAIL**  ` (`tools/bench/diag_movein_set.log:57`, and `bgrun`'s own INNER FAILURE line at `:128` repeats
      the bolded form), which it does not. So the mandatory-review gate silently passed a failing run. ⚠️ **The
      material session proposed widening the regex alone; that is the wrong half on its own**, because it leaves
      every new script free to invent a third format. Fix BOTH: make the diagnostics emit the documented `  FAIL  `,
      and widen `FAILURE_RE` to tolerate `\*{0,2}FAIL`. This is the REPAIR of an existing gate, not a new device.
    - (j) 🔴 **A LOG READ WHILE ITS RUN MAY STILL BE IN FLIGHT IS NOT A READING — the terminal `BGRUN END` /
      `BGRUN TIMEOUT` line is the only proof a run finished.** Cycle 52 opened by reading `tail -c 3000` of
      `tools/bench/stage_d1_s2_loops.log` when the file was **12,978 B, mtime 03:55**, saw it stop mid-sentence
      inside a cold re-read with no terminal line, and concluded the session exit had killed the child. It had not:
      bgrun's **breakaway detach** kept the child alive and it finished at **04:06** at 50,905 B / 300 lines,
      `35 pass / 0 fail`, `BGRUN END rc=0 after 776s`. The session then spent an 825 s re-verification on gates that
      were passing as it read. Named by the cycle-52 retrospective as
      `VIOLATION: inference-over-measurement | loss_min=10 | evidence=tools/bench/stage_d1_s2_loops.log:300`,
      accepted in full after re-reading the file. **Before drawing any conclusion from a log, check that its
      terminal line is present; if it is not, the run is live and the file is not yet evidence.** Size and mtime are
      the cheap tell — a log whose mtime is within a minute of now is being written.
      ⚠️ What this does NOT excuse: 54(b) was still breached at 03:55:17 — a session ended with a child running —
      and the work survived only because a mechanism covered for a broken rule. **Hold the turn open until the child
      lands** remains binding; the detach is a safety net, not a licence.
      🔴 **VARIANT FOUND THE HARD WAY, cycle 53: ON AN APPEND-MODE LOG, "the terminal line is present" IS NOT A
      TEST.** `tools/bench/retro.log` accumulates across cycles, so a watcher of the form
      `until grep -q "BGRUN END" retro.log` returns **instantly**, satisfied by the *previous* cycle's END line,
      and a grep of its matching lines then reports the previous cycle's `VIOLATION:` verdicts as if they were
      this cycle's. Cycle 53 armed exactly that watcher, was handed cycle 50's `VIOLATION: none` and cycle 52's
      two violations, and caught it only by reading the run's own `bgrun` task file. **Wait on the run's OWN
      output (the `bgrun` task file, or a per-run log), never on a shared append-mode log; and when a log is
      shared, the test is a terminal line NEWER THAN THIS RUN'S `BGRUN START`, not the presence of one.** Same
      fault class as 37(j) and it defeats 37(j)'s own stated remedy, which is why it is written here.

## Pre-decided — ADDED 2026-09-20 (cycle 53): S3 withdrawn and re-cut · the measured 1.5 row table

38. **37(g) IS WITHDRAWN. S3 WAS A FULL-LENGTH RETRY WEARING A DECOMPOSITION'S NAME, AND THE NEXT BUILD IS A
    DIAGNOSTIC, NOT A STAGE.** Judgement, cycle 53, 2026-09-20, from three ANSWERED reviews — the owed P6
    hypothesis review (`archive/peer/2026-09-20-movein-p6-diagram-misprediction.md`), the prior-art review of the
    S3 recipe (`…-priorart-d1-s3-focus.md`, 6 slugs, accepted in full) and `…-c53-g2b-caseselector.md` — plus the
    row classification `tools/bench/c53_row_class.{py,log,json}`. Every disposition is written into the review
    files themselves. 34, 35, 36 stand; this replaces 37(g) and corrects 37(e)'s acceptance criterion.
    - (a) 🔴 **WHAT WAS WRONG WITH 37(g).** Cycle 52's re-split trigger had already fired (STATUS `owner_c52m2`),
      and CLAUDE.md's split rule clause 3 answers that trigger with *a decomposition plan whose sub-steps each
      name a saved file* — explicitly **not** "a full-length retry under a new file name". 37(g) answered it with
      one script and one save and called the shape forced. Two of its supports failed: the recipe's own contract
      printed `PREDICTED 0` / `PREDICTED REFUSED` (`tools/recipes/stage_d1_s3_focus.py:149-151`), i.e. a step that
      predicts it leaves no file, which `CLAUDE.md:383` forbids; and my acceptance criterion — *"per moved node the
      count of WIRED TERMINALS returns to its pre-move value"* — **was never sound for a move stage**, because two
      rows are queue endpoints excluded by construction (`tools/recipes/build_d1_v0.py:943`, `:976-977`). The
      recipe is **kept unlaunched** for its measurement code, as `stage_d1_s2.py` was; it is not re-armed on these
      bytes and its prior-art STOP RECORD stays armed.
    - (b) **THE MEASURED ROW TABLE — the decomposition's input, and nobody on the record had it right.**
      `tools/bench/c53_row_class.json`, confirmed three ways (the rewire JSON, the netmap wire table, and
      `main_vi_nodeterms.json` — a third census by a different op). **17 cut terminals**: `#10407` t0–t6, `#48`
      t0–t6, and `#3529`/`#3560`/`#3447` t0. By action: `cross-loop:1.2->1.5` **2** · `from-tunnel` 1 ·
      `same-loop` 5 · `to-sr` 2 · `from-sr` 2 · `source-side` 5. Sources on `#639` **7**, ~~on `#686` **0**~~,
      far end planned for loop 1.2 **2**, SR-created rows **4**, orphaned counterparts **3**.
      🔴 **"SOURCES ON `#686` = 0" IS UNSOUND AND IS STRUCK** — it is a *negative* claim drawn from
      `main_vi_netmap.json`'s `wires` table, which (h) below measures as TRUNCATED. Re-derive it from
      `main_vi_nodeterms.json` before any stage depends on it. Everything else in this table comes from the
      rewire JSON and nodeterms and survives; G6 passed, all 17 rows agreeing across two independent censuses.
      The two deferred rows are `tools/bench/d1_rewire_sources.json:1748` — **`#10407` t0, the CASE SELECTOR**,
      fed by `#10686 'x .and. y?'` — and `:1793` (`#10407` t2, fed by `#10757 'element'`); both far ends sit on
      `#639` today and are planned for row **1.2**, which does not exist. `:1892` is **not** a third crossing:
      `#10407` t6 `position [internal units]` is a **source** whose label reads `to-sr`, far end `#12589` t1, kept
      on row 1.1 by §11c (`docs/d1-build-plan.md:398`) — but **§6 names no construction verb for it**, so it is a
      real and unclosed gap under a different name. Scoreboard: 37(g) predicted **0** crossings, the P6 review
      predicted **3**, the machine says **2**.
    - (c) 🔴 **`Required` IS UNKNOWN ON ALL 17 AND IS MEASURED BY CONSTRUCTION, NEVER BY A READER.** No built op
      reports terminal Required-ness and Pre-decided 2 forbids building one — the same wall 36(c) hit on
      `Terminal.DataType`, and 36(d) settled it the same way: **let the machine answer by accepting or refusing.**
      This matters because `#10407` t0 is a case selector, and "an unwired case selector obviously breaks the VI"
      is precisely the shape of claim that `inference-over-measurement` counts (11 occurrences, recorded
      `docs/violation-decisions.md`, 2026-09-20 06:48). **It is not assumed here in either direction.**
    - (d) 🔴 **DECISION — the next build is `tools/bench/diag_s3_focus_trial.py`, a DIAGNOSTIC under
      `tools/bench/`, never a recipe.** This is the 34(j) pattern that carried S2: a cheap run whose *reading* is
      the deliverable and whose saved file is a bonus. On a dated scratch copy of `claudeDev\D1_s2_loops.vi`
      (`6ff19497…`): move the five movable nodes into body `Diagram #23058` of loop a `#23032` (37(h), binding);
      create the two SR pairs on loop a with `add_shift_reg`/`wire_sr`, the verb `docs/d1-build-plan.md:402-403`
      gives them; wire every row whose source exists at that moment, using **`OpConnectFromWire_v0.vi`** for the
      from-tunnel row `#10407` t1 (`docs/toolkit-capabilities.md:70` — the only built writer whose source need not
      be a node, which the withdrawn recipe never imported); leave the two deferred rows and the unnamed `to-sr`
      row bare; then **read `ExecState`**. Save if legal. Either branch leaves
      `tools/bench/diag_s3_focus_trial.json`.
    - (e) 🔴 **EVERY `move_in` RE-RESOLVES ITS DESTINATION INDEX IMMEDIATELY BEFORE THE CALL.** `move_in(target,
      uid, dest_diagram_index, position)` (`tools/recipes/build_d1_v0.py:318`) addresses its destination by
      **traverse index**, not uid, and relocating a structure relocates its frame diagrams inside that array — so
      in a multi-move script a later index can be silently wrong and **the op cannot report it**
      (`tools/recipes/build_d1_v0.py:325` writes `SetControlValue("index", int(dest_diagram_index))`; `:358`
      resolves it as `[o['uid'] for o in report_all(target,'Diagram')].index(uid)`).
      ✅ **MEASURED, AND THE DRIFT HYPOTHESIS IS FALSIFIED FOR `move_in`** — `tools/bench/diag_destidx_drift.py`
      → `.log` / `.json`, **15 pass / 0 fail**, `BGRUN END rc=0 after 76s`, every gate REPORTED rather than
      required so no outcome was smuggled in. Across two real `move_in` calls on a scratch copy of S2:
      `idx(#23058)` = **[22, 22, 22]**, `idx(#639)` = **[46, 46, 46]**, Diagram class count = **[173, 173, 173]**,
      traverse order unchanged after both moves, and the explicit stale-index probe says a script that had cached
      `dest_diagram_index=22` would **still address `#23058` correctly**. `owner_of` confirms both nodes landed on
      `#23058`. **So the P6 review's mechanism — which this item adopted as "the strongest surviving explanation
      for the ten v3→v7 deaths" — does not occur for `move_in`, and that sentence is withdrawn.** Index
      invalidation remains measured for *terminal* and *tunnel* indices (21(d)'s +13 shift, `toolkit-capabilities`
      T2c2); it is the DIAGRAM traverse array that is stable here.
      **The practice stands anyway, now as cheap defence rather than as a fix:** locate `#23058` by uid in a
      freshly-read traverse list before every call and gate that the resolved index still owns it. It costs one
      read and it is the only thing that would detect the behaviour changing.
      ⚠️ Two further readings from the same run, both consistent with 37(d)/(e): `move_in` echoed uid **23035**
      for *both* calls — the echo is not the moved object — and **`ExecState` was 0 after only two of the five
      nodes had moved**, with `g.save()` refused (`allow_broken` False, `gui_save` never called). A move stage
      that does not wire as it goes cannot save, which is exactly what (d) is built to measure.
    - (f) 🔴 **THE BRANCH IS DELIBERATELY NOT PRE-DECIDED.** A reading of **1** means loop 1.5 can exist before the
      queue stage and (d)'s bytes become the S3 stage next cycle. A reading of **0** means the ordering itself is
      wrong — the prior-art review's `A2 refuted-already` already showed that "1.5 is buildable alone" was
      authorised by a premise 36(d) removed — and the queue-donor **trial census** of 36(d), today parked *behind*
      S3, moves in front of it. Writing that branch now would be deciding before the evidence exists, which is the
      one thing a delegation brief may never do.
    - (g) 🔴 **A CONSTRUCTION THAT IS BANNED BY NAME, because it passes every gate we have.** Do **not** close
      1.5's inputs by tunnelling out of `#637`, wiring on `#686` and tunnelling into `#23032`. It restores every
      wired-terminal count, it compiles to `ExecState` 1, and it **changes the computation** — autofocus would run
      once after acquisition ends instead of once per frame. Rule 1a, found by the P6 review, and the only
      green-building rule-1a violation identified so far on this path.
    - (h) 🔴 **THE NETMAP IS NOT A TERMINAL CENSUS.** `tools/bench/sweep_netmap_main.py:63-64` writes
      `"terms": [[t, w] for _ti, t, w in terms if t]` — an unnamed-terminal filter applied to **every node of every
      class** that also **discards the real terminal index**. 156 unnamed-and-wired terminals exist, `WhileLoop
      #637` t37 among them (`tools/bench/main_vi_nodeterms.json:6868-6872`). Count wired terminals from
      `node_terms`, never from `main_vi_netmap.json`, and never read a terminal index out of it.
      🔴 **THE `if t` ACCOUNT IS SECONDARY — THE REAL MECHANISM IS TRUNCATION, MEASURED 2026-09-20**
      (`archive/peer/2026-09-20-c53-netmap-terms-truncation.md`, ANSWERED, after the 626-node test came back
      **574/626**, not 626/626): `net_map` iterates `for t in range(max_terms)` with **`max_terms=40`**
      (`tools/gscript.py:2549`) and additionally breaks after **three consecutive unnamed+unwired terminals**
      (`:2557-2560`). **`WhileLoop #637` HAS 59 TERMINALS** (`tools/bench/main_vi_nodeterms.json:6424-7131`) —
      12 of i0–i39 unnamed, 40 − 12 = 28 named = exactly the netmap array's length. **The one node the entire
      restructure turns on is the one the census silently truncates.** The `empties >= 3` stop explains the other
      51, including the dropped trailing `error out` on `#30804`/`#4620`.
      🔴🔴 **AND `nets` IS BUILT INSIDE THE SAME TRUNCATED LOOP (`:2570-2572`), SO THE `wires` TABLE IS
      TRUNCATED TOO** — Diagram 19 is missing all of `#637`'s i40–i58 wire ends (9051, 9000, 9649, 11253, 16421,
      29006, 29122, 28392, 29081, 29106, 32583, 32344), *the border wires of the loop being rebuilt*. Any fact
      about `#637`'s border taken from the netmap is suspect; `docs/frame-loop-wire-graph.md` is the most exposed
      document and its `#637` rows are to be re-derived from nodeterms.
      🔴 **THE RULE THIS BUYS, which is broader than the netmap: a NEGATIVE claim — "nothing else carries this
      wire", "no such terminal exists" — may NEVER be drawn from a census whose own completeness has not been
      measured.** This cycle used exactly such a claim to reject a *correct* peer finding
      (`archive/peer/2026-09-20-movein-p6-diagram-misprediction.md`, rejection withdrawn the same day), and only
      a second reviewer caught it. ⚠️ The cap and the early stop were **measured and written down on
      2026-09-14**; prior art existed and was not consulted. This is the third
      confidently-wrong reader in three cycles — after 37(b)'s index-order read and 37(d)/(e)'s wire count that
      cannot see a cut — and all three would have passed a green build. **A reader's contract is measured before
      it is used as a gate.**

## Pre-decided — ADDED 2026-09-20 (cycle 54): the 1.5 trial ran · the machinery is sound · the BOUNDARY is not

39. **38(f) RESOLVES TO THE `0` BRANCH — BUT FOR A DIFFERENT REASON THAN 38(f) EXPECTED, AND THE DIFFERENCE IS
    THE WHOLE RESULT.** Judgement, cycle 54, 2026-09-20, from `tools/bench/diag_s3_focus_trial.{py,log,json}`
    (`BGRUN END rc=0 after 106s`, 43 pass / 0 fail) and `tools/bench/replay_netmap_truncation.{py,log,json}`
    (20 pass / 1 fail, the fail reviewed and disposed). 34–38 stand; this resolves 38(f) and amends 38(b).
    - (a) 🎉 **THE MOVE-AND-REWIRE MACHINERY IS SOUND — MEASURED END TO END FOR THE FIRST TIME ON REAL ROWS.**
      All five movable nodes (`#10407`, `#48`, `#3529`, `#3560`, `#3447`) moved from `Diagram #639` into body
      `Diagram #23058` of loop a `#23032`; owners re-read by uid confirm all five. **9 of 9 attempted rows wired,
      machine error empty on every one**: five `OpConnectNested_v1` jobs (`#48` t0/t1/t2, `#10407` t3/t5, each
      `wire_delta 1`), three `wire_sr` sides, and 🎉 **`OpConnectFromWire_v0.vi` ACCEPTED the from-tunnel row** —
      `#10407` t1 bare → wire **24667**, `Is Broken? 'False'`. The two SR pairs were **created**, not moved
      (`RightShiftRegister #23898` VISA, `#23936` POSITION). `#48` is back to **7/7** wired terminals. The
      destination index re-resolved to **22 on all five calls**, traverse length 173 each time — 38(e)'s drift is
      absent again. **Nothing the trial attempted failed.** After ten v3→v7 deaths and five cycles that left no
      file, this is the first positive evidence that the D1 re-wiring path works.
    - (b) 🔴 **`ExecState` = 0 AND `g.save()` REFUSED** (`RuntimeError: refusing to save a BROKEN VI`,
      `allow_broken` False, `gui_save` never called); scratch `DIAG_s3focus_20260920_072957.vi` is byte-identical
      to S2. Census reported never gated: LoopTunnel 135 → 137, Wire 1905 → 1915. Refs 11/11/**0**.
    - (c) 🔴 **THE `0` IS OVER-DETERMINED, AND THAT IS NOT A DEFECT OF THE TRIAL — IT IS THE ANSWER.** Five things
      are simultaneously true of it and the run separated none: `#10407` t0 (case selector) bare, t2 bare, t6 bare,
      the POSITION register's right inside terminal unwired **because** t6 is bare, and `#637`'s old SR pairs now
      orphaned. **Do NOT record "the unwired case selector broke it"** — 38(c) named that exact sentence as the
      shape `inference-over-measurement` counts, `Required` is still unmeasured on all 17 rows, and no built op
      reports it. The `0` is not evidence about any one row.
    - (d) 🔴 **DECISION — S3-AS-LOOP-1.5-ALONE IS CLOSED, AND THE FAULT IS THE STAGE BOUNDARY, NOT THE MACHINERY.**
      Every row the trial could wire, it wired; the only holes are the rows whose sources are **not in the set**:
      `#10407` t0 and t2, fed by `#10686 'x .and. y?'` and `#10757 'element'`, both planned for loop **1.2, which
      does not exist** (38(b)), plus t6, for which §6 names no construction verb at all. An intermediate at
      `ExecState` 0 cannot be saved — measured now four times (cycles 50, 52, 53, 54). Therefore: **a saved D1
      stage's node set must be CLOSED UNDER ITS WIRE SOURCES.** 1.5 alone is not, so no ordering of the existing
      stage list makes it savable. This is a stronger and cheaper result than 38(f) anticipated, because it was
      reached without guessing at any row's Required-ness.
    - (e) 🔴 **CONSEQUENCE — the queue-donor TRIAL CENSUS of 36(d) moves IN FRONT**, as 38(f)'s `0` branch says,
      and now with a reason of its own: the two open rows are exactly the 1.2 → 1.5 crossings, and a crossing is
      closed by a queue or by 1.2 existing. 36(d)'s trial census is the only thing standing between this project
      and any queue at all, and it is fully specified there. It is no longer parked behind S3.
    - (f) 🔴 **38(g)'s BANNED CONSTRUCTION IS NOW MORE TEMPTING, NOT LESS — RE-READ IT.** A green `ExecState` 1 is
      three tunnels away: tunnel out of `#637`, wire on `#686`, tunnel into `#23032`. It would restore every count
      and compile clean, and it would move autofocus off the per-frame path (rule 1a). **It stays banned by name.**
      The same applies to any "temporary stand-in" that closes t0/t2 just to see the VI go green — a diagnostic
      that manufactures a 1 manufactures the trap.
    - (g) **38(b)'s STRUCK CLAIM IS UN-STRUCK FOR WIRES 4185 / 7506 ONLY, AND ON POSITIVE IDENTIFICATION.** Their
      far ends were on disk all along: `LeftShiftRegister #4344` (4185) and `RightShiftRegister #4334` (7506),
      `tools/bench/main_vi_shiftregs_v1.json` — both shift registers of `#637`, neither on `#686`. That is a
      positive naming of the carriers, not a census failing to find others, which is why it is allowed. 🔴 **The
      general prohibition stands and is now quantified: `main_vi_nodeterms.json` enumerates `Node` terminals ONLY**
      — shift registers (`tools/gscript.py:948`), Constants, 132 LoopTunnel and 114 ControlTerminal are outside it,
      and **800 of 1376 wires have exactly one node carrier**. It licenses no negative claim. "The complete census"
      is retired as a phrase for it.
    - (h) **THE NETMAP TRUNCATION IS FULLY ATTRIBUTED AND `docs/frame-loop-wire-graph.md` WAS NEVER EXPOSED.** All
      **52** shortfalls reproduced from files, 0 unexplained: `max_terms=40` cap = **1** (exactly `WhileLoop #637`),
      `empties>=3` = **51**, `if t` = 0 length-shortfalls though it drops 156 unnamed-and-wired terminals
      census-wide. 574/626 and 59/28 both CONFIRMED. The feared document does not contain the string `netmap` —
      both its generators read nodeterms, and re-running `stitch_state_carriers.py:40-45` over the full 59-row
      record gives **0 differing names of 12**, so **no row changed**; one dated block was added recording the
      re-derivation. ⚠️ **Two cycle-54 reviews disagree on a detail and it blocks nothing:**
      `archive/peer/2026-09-20-c54-netmap-wires-table-restatement.md` MEASURED **36** of `#637`'s ends in netmap
      Diagram 19, all at i<40, 0 unattributed; `…-c54-netmap-wires-g12.md` asserts **40** with 12 unattributed and
      was never run. **A measurement outranks an unrun verdict**, so 36 is recorded — and both agree on the only
      load-bearing point: **none of i40–i58 is present.**
      ✅ **CORRECTED AT THE CYCLE'S CLOSE — it is SETTLED, not merely better-supported.** Calling it "reported,
      not resolved" was wrong: run 2's own output reads `n=4 ends=36`
      (`tools/bench/replay_netmap_truncation.log:431`) and the third review states the resolution explicitly. The
      deciding measurement was already in hand when the dispute was recorded, which is the same error class as
      concluding from an unread file. ⚠️ Note also that the restatement review was recorded "ACCEPTED IN FULL" by
      a material session and a later review **REFUTED parts of it** (disposed in 40(g)); "accepted in full" is not
      the last word on it. 🔴 **STILL OPEN, cheap and files-only:** the census agreement was measured in ONE
      direction only — the reverse walk (netmap → nodeterms) was never computed, and three files put the netmap at
      **635** nodes against 626. It bears on `c53_row_class.json`, an input to the 1.5 row table, so it is in NEXT.
    - (i) ⚠️ **PROCESS, PAID FOR IN CASH: TWO MATERIAL SESSIONS MUST NOT RUN CONCURRENTLY WHEN BOTH WRITE
      `STATUS.md`.** Cycle 54 dispatched them in parallel for wall-clock. Both wrote lock keys to the same file
      (one flagged "STATUS.md changed on disk mid-session"), and both independently dispatched an opus/max
      hypothesis review of the SAME G12 question — two reviews, one of them redundant, ≈$2.8 of it avoidable.
      Parallel material dispatch is allowed only when the two briefs touch disjoint files.

40. **36(d) IS SUPERSEDED: `queue_node('obtain')` IS A SHAPE TEST, NOT A TYPE TEST, AND THE QUEUE IT CREATES IS
    UNREADABLE. THE TYPE TEST IS CONNECTION.** Judgement, cycle 54, 2026-09-20, from
    `tools/bench/diag_queue_trial_census.{py,log,json}` (`BGRUN END rc=0 after 114s`, 16 pass / 0 fail). 36(a),
    36(b) and 36(c) stand unchanged; only 36(d)'s method is replaced.
    - (a) 🔴 **THE MEASUREMENT: 18 donors attempted, 18 ACCEPTED, 0 REFUSED — the refusal set is EMPTY.** The 18
      `(node, named output terminal)` pairs span 12 of the 18 independent nodes (6 expose no named output at all:
      `6951, 6409, 28670, 23032, 10170, 23041`) and cover numerics, an IMAQdx session refnum, initialized arrays,
      error clusters, sizes and motor positions. `#637` was absent from the donor list by construction, so 35(a)
      held. **So the `error 1057` that 36(a) measured four times was never about the donor's TYPE — it was about
      its SHAPE**: in `AbstractDiagram.Nodes[]` with a named source terminal, or refused. Every shape that passes
      that test is accepted whatever it carries.
    - (b) 🔴🔴 **AND ALL 18 ACCEPTANCES READ BACK IDENTICALLY.** One signature for every one: `report_all` =
      `{class 'Function', owner 'Diagram', owner_of ('Diagram', 686)}`, label `'Obtain Queue'`, and the same eight
      `node_terms` rows (`name (unnamed)` · `element data type` · `create if not found? (T)` · `error in` ·
      `max queue size` · `queue out`(src) · `created new?`(src) · `error out`(src)). Only `uid` and caller-chosen
      `pos` differ. **A queue typed by an array donor is indistinguishable from one typed by a refnum, an error
      cluster or a scalar.** 36(d)'s premise — "a created `Obtain Queue` can be read back" — holds for EXISTENCE
      only. The trial census therefore has **no discriminating power**, and running more of it would buy nothing.
    - (c) 🔴 **DECISION — TYPE IS TESTED BY CONNECTION, AND LABVIEW IS THE TYPE CHECKER.** We cannot read a
      terminal's type (36(c)) and we cannot read a queue's element type (b). But a type MISMATCH is visible the
      moment two things are wired together, and the reader for that is **already built and already measured**:
      `Wire.Is Broken?` **6371004** (`docs/NAMES.md:902-911`, built 2026-09-17; CLAUDE.md names it as the reader
      to use instead of inferring why a wire is bad). Wire a candidate queue to the consumer its data must
      actually reach and read `Is Broken?`. No new op, so Pre-decided 2 is respected; no inference, so 38(c)'s
      trap is avoided. The donor's type never has to be *named* — only matched.
    - (d) 🔴 **BUT THE INSTRUMENT IS VALIDATED BEFORE IT IS USED AS A GATE** — 38(h)'s own closing rule, and the
      lesson of three confidently-wrong readers in three cycles. Before any donor is chosen, run a **matched /
      mismatched control pair** and read `Is Broken?` on both. **If the mismatched wire does not read broken, the
      connection test has no discriminating power either and the queue path needs a different idea entirely** —
      that is a first-class outcome and must be reported as one, not worked around.
      🔴 **THE CONTROL PAIR NEEDS NO QUEUES, AND MUST NOT USE ANY.** Validate the *reader* on the simplest shape
      that can exhibit a type mismatch: two **node-to-node** connections made with `OpConnectNested_v1` — the op
      that went 5 for 5 this cycle — one plainly matched and one plainly mismatched, using donors already measured
      to differ (`#250 'IMAQdx Session'`, a refnum, against `#8486 'x+1'`, a numeric). Building queues first would
      put the untested instrument and the untested subject in the same experiment, and would additionally require
      an enqueue/dequeue op whose existence in the built fleet is **not established** — check
      `docs/toolkit-capabilities.md` before assuming one, and if none exists say so rather than building one
      (Pre-decided 2). Queues enter only after `Is Broken?` has been shown to discriminate.
    - (e) ⚠️ **WHAT THIS DOES NOT LICENSE.** Do not conclude from (a) that any donor will do. It shows only that
      the op will not stop us; the queue still carries whatever the donor carries, and a wrongly-typed queue will
      surface later as a broken wire or — worse — as a silently wrong transfer. Equally, do not read a type off a
      terminal's NAME: `'x+1'` does not prove DBL and `'initialized array'` does not prove which element type.
      Names are labels, and 36(c) remains the measurement that no op reports the type.
    - (f) ✅ **THE RUN LEFT AN OPENABLE FILE**, as the 4th outcome review requires of every cycle:
      `claudeDev\DIAG_qtrial_20260920_075310_1.vi`, md5 `ada51e8441e1a82ed081ab021abdbbe5`, **481,777 B**, saved
      legally at `ExecState` 1 with `allow_broken` False and `gui_save` never called; LV2026 bytes `26 00 80 00`.
      `ExecState` was **1 → 1 and none of the 18 attempts moved it**, so 36(b)'s "an unwired donor node takes a
      scratch from 1 to 0" did NOT recur — recorded as an observation, not resolved. Wire 1905 → **1907** for 18
      added nodes, because two donor terminals were themselves bare (`#25380` t2, t9): reported, not attributed.
      ⚠️ Traverse class must be resolved **by membership, not by `cls_of`** — `#25380` is a `WhileLoop` that
      `cls_of` calls "Function", and `#781`/`#8953`/`#28124` are in `Node` but not `Function`.
    - (g) **DISPOSITION of `archive/peer/2026-09-20-c54-g12-after-rerun.md`** (claude/hypothesis opus max,
      ANSWERED, forced by `guard_peer` on the other session's re-run log), which the material session correctly
      recorded without accepting, netmap work not being its brief: **ACCEPTED IN PART by judgement.** Accepted —
      G12b as phrased was *entailed by* the terminal table printed in the same run rather than independently
      measured, so it is recorded as a derivation, not a measurement; and §3's circularity caution is real and is
      adopted as a standing rule: **never validate `main_vi_netmap.json` using an ordering that `net_map` itself
      produced.** Rejected as to consequence — the load-bearing conclusion, *none of `#637`'s i40–i58 ends appear
      in the netmap*, follows directly from the measured `max_terms=40` cap (`tools/gscript.py:2549`) and does not
      depend on G12b's phrasing or on any inversion. 39(h) stands unchanged. §4's data-contamination point does
      not reach the queue census: that script contains no `netmap` string and reads no netmap-derived datum.

41. **A MATERIAL BRIEF MUST SAY WHAT TO DO WITH A REVIEW THAT ARRIVES MID-RUN — THREE SENTENCES THAT WOULD HAVE
    PREVENTED THIS CYCLE'S ONLY STRUCTURAL FAULT.** Judgement, cycle 54, 2026-09-20, from its own retrospective
    (`archive/peer/2026-09-20-retrospective-cycle54.md`, `VIOLATION: judgement-in-material | loss_min=9 |
    loss_usd=3.2380`, ACCEPTED IN FULL).
    - (a) **WHAT HAPPENED.** `guard_peer` forced a hypothesis review on a material session mid-run. The session
      collected it, **accepted it in full, wrote its disposition, built its §4 discriminating test and re-ran the
      measurement** — four judgement acts. Twenty-four minutes later a second material session met the same
      situation and wrote *"Accepting or rejecting its findings is a judgement call … and a material session does
      not make it"*, returning all five objections undecided. **The difference was the brief, not the session.**
      Neither of mine said what to do with an arriving review; one filled the gap, one did not.
    - (b) 🔴 **THE RULE, to be pasted into every material brief from now on:** *"Any peer review you are FORCED to
      dispatch is RECORDED, never accepted or rejected. Write the exchange to the archive, report its verdict as
      a fact, and return its findings on your `OPEN:` line. Do not act on them: do not redesign a gate, do not
      rebuild a measurement, and do not re-run on the strength of one. The judgement session disposes it."* This
      is a sentence in a brief, not a device — the user's 2026-09-18 08:53 no-new-device order is respected.
    - (c) **AND TWO PRACTICES THAT COST 9 MINUTES AND $3.24 TOGETHER.** (1) **A gate whose wording a review has
      already falsified is DEMOTED TO A FACT LINE, not re-emitted as a `FAIL`.** G12's false wording fired twice
      after two reviews had measured why it is false; the bgrun FAIL-scan plus `guard_peer`'s mtime-only rule then
      converted that into a third paid review of the same fact. Run 2 treated G16 correctly and G12 incorrectly in
      the same file. (2) **Sequence a run that is expected to retain a `FAIL` LAST**, after anything it could
      block — the queue census reads nothing netmap-derived and was stalled nine minutes by an unrelated gate.
      ⚠️ The retrospective's sharpest observation is not the violation: **STATUS now routinely carries "rc=1 … not
      a crash" annotations, which is the first step toward a working device being bypassed as noise.** The answer
      is to stop producing spurious FAILs, never to get better at explaining them.
    - (d) **NOT BUILT, and recorded as the user's call:** `guard_peer` compares mtimes and has no notion of
      *failure identity*, so an ANSWERED review cannot discharge a re-occurrence of the gate line it reviewed four
      minutes earlier, though `cycle_runner.py` already computes "same first failing GATE line, uids stripped".
      A real repair and a real toll — but the next cycle's first act is a measurement on the deliverable, and the
      no-new-device order stands.

## Pre-decided — ADDED 2026-09-20 (cycle 55): the type checker is VALIDATED · the row table is NOT cleared · STOP

42. **40(d) RESOLVES TO ITS POSITIVE BRANCH: `Wire.Is Broken?` DISCRIMINATES A TYPE MISMATCH, AND `ExecState`
    DOES NOT.** Judgement, cycle 55, 2026-09-20, from `tools/bench/diag_typectl_v2.{py,log,json}`
    (`BGRUN END rc=0 after 88s`, 19 pass / 0 fail) and, for the withdrawn first attempt,
    `tools/bench/diag_queue_typetest_control.{py,log,json}`. 34–41 stand; this resolves 40(d) and corrects
    two citations in 40.
    - (a) 🎉 **THE CONTROL PAIR, one variable differing.** Same sink terminal, same diagram, same op, same run:
      **leg M (matched)** `#8486` t0 `'x+1'` (numeric) → `#2048 'Array Subset'` t4 `'index'` read `Is Broken?`
      **False**; **leg X (mismatched)** `#250` t1 `'IMAQdx Session'` (refnum) → the same `#2048` t4 read
      **True**. Op error column `''` on both; `owner_of` = `('Diagram', 686)` measured for all three nodes.
      **So the instrument discriminates, and 40(d)'s "if the mismatched wire does not read broken the queue path
      needs a different idea entirely" DOES NOT FIRE.** Type is tested by connection (40(c)), now validated
      rather than proposed.
    - (b) 🔴🔴 **AND IT CARRIES A CONTRACT THAT MUST BE OBEYED, OR ITS DEFAULT READING IS THE WRONG ONE.** In the
      **writing pass** `Is Broken?` read **False on BOTH legs** — the naive read calls a type-mismatched
      connection fine. The discriminating value appeared only on an **ordered second, idempotent re-connect**
      (`wire_delta 0`). **RULE: `Is Broken?` is never read in the same pass that makes the connection.** This is
      38(h)'s "validate the instrument before using it as a gate" earning its whole cost — a fourth
      confidently-wrong reader was one pass away, and the trap is `docs/NAMES.md:905-911`'s, already on disk.
    - (c) 🔴 **`ExecState` IS NOT A TYPE DISCRIMINATOR AND MUST NEVER BE USED AS ONE.** It fell **1 → 0 on the
      MATCHED leg too**. That refutes, by measurement rather than by argument, the peer suggestion that
      `connect_terminals`' `ExecState 1→0` is a less noisy discriminator than `Is Broken?`. Reading both was
      what settled it; a single-signal run would have adopted the wrong one.
    - (d) ⚠️ **THE MATCHED LEG'S `0` IS OVER-DETERMINED — do NOT record "the matched connection broke the VI."**
      Both legs were **branches of the donor's existing net, not new wires**: each sink wire uid equals the
      source terminal's pre-existing wire (23519 / 6910) and `Wire` count held 1905 → 1905. A 0 may come from the
      branch, from `#2048` t4's own downstream, or elsewhere; the run separated none. Same shape as 39(c) and
      38(c). 🔴 **SCOPE LIMIT, binding:** what is validated is `Is Broken?` **on a branched net, read in a
      separate ordered pass**. Behaviour on a *newly created* wire — the queue case — is UNMEASURED. It does not
      block, but the first queue connection that disagrees with its construction is checked against this line
      before anything is concluded.
    - (e) **WITHDRAWN, with its reason: the "bare numeric arithmetic input" sink rule was self-defeating.**
      Attempt 1 found **zero** bare named inputs on all five nodes it named, because **"no bare required input"
      is ENTAILED by `ExecState == 1`** — the rule could not have succeeded on any working VI. Disposition of
      `archive/peer/2026-09-20-c55-sinkrule-no-bare-input.md` (claude/hypothesis opus max, ANSWERED):
      **ACCEPTED** on the entailment and on "the rule never required a *type-constrained* sink" — the needed
      property was constrained-and-optional, which `#2048` t4/t5 have and an arithmetic primitive's inputs never
      can. Attempt 1's own `Diagram #686` census is what supplied the fix, so it is not a wasted run.
    - (f) **TWO CITATIONS IN 40 ARE WRONG AND ARE CORRECTED HERE.** (1) `Wire.Is Broken?` 6371004 is at
      **`docs/NAMES.md:902-911`**, not `:888-897` (that range is the case-structure property-ID block); 40(c)
      and CLAUDE.md both carried the wrong one — CLAUDE.md is fixed, 40(c) is corrected by this line. (2) 40(d)
      said enqueue/dequeue ops' existence in the built fleet is "not established": **they exist**
      (`tools/gscript.py:1117-1118`, `docs/toolkit-capabilities.md:32`). Also measured: `connect_terminals`
      `:2407` and `connect2` `:2633` both require a TOP-LEVEL end, so neither reaches `Diagram #686`;
      `OpConnectNested_v1` was used same-diagram.

43. **THE REVERSE CENSUS WALK IS CLEAN, `walk()` IS COMPLETE — AND `c53_row_class.json` IS STILL NOT CLEARED,
    BECAUSE BOTH TESTS MEASURED THE WRONG GRAIN.** Judgement, cycle 55, from
    `tools/bench/reverse_census_walk.{py,log,json}` (26 pass / 1 fail) and
    `archive/peer/2026-09-20-c55-reverse-census-r14.md` (claude/hypothesis opus max, ANSWERED).
    - (a) ✅ **THE 635-vs-626 DISCREPANCY IS FULLY ATTRIBUTED AND CLOSES.** Reverse walk (netmap → nodeterms):
      only uid **22963** absent — `net_map`'s own junk Invoke — on 9 diagrams, so 635 = 626 + 9. Forward walk:
      **0** absent, reproducing cycle 54. `diagram_tree_main.json` carries the same junk uid on **11 OTHER,
      disjoint** diagrams always at the last `Nodes[]` index (637 = 626 + 11), and `sweep_nodeterms_main.py:56-59`
      reads UID 0 and **breaks** ⇒ 626. Diagram `"0"` holds 0 nodes in both; no class filter contributes. 39(h)'s
      remaining one-directional item is closed.
    - (b) ✅ **`walk()`'s COMPLETENESS IS MEASURED — shortfall 0.** Its two stops are
      `tools/recipes/build_opstopfromnode_v0.py:132` (`for n in range(limit)`) and `:134-135` (`if not u: break`);
      the caller passed `limit=200`, so the cap was not binding. `walk_n_nodes` **24** = nodeterms d19's **21** +
      S2's three loops `#23032/#10170/#23041`; terminals **139 = 136 + 3**; **0** per-node terminal-count
      differences on all 21 shared nodes. One more census moves from "unmeasured" to "measured", which is the
      only thing that licenses using it.
    - (c) 🔴 **BUT THE 17-ROW 1.5 TABLE IS NOT CLEARED, AND MY OWN SECOND ACT ASKED THE WRONG QUESTION.**
      Disposition of the R14 review: **ACCEPTED on its point (e)** — `c53_row_class.json` is a **TERMINAL**
      table resolved out of the netmap `wires` tables, and `#637` is the VI's single `max_terms=40` cap site with
      shortfall **31** (`tools/bench/c53_row_class.json:267-272`), so **a wire reaching `#637` at t ≥ 40 is absent
      while every node uid still resolves.** Node-uid presence — what both R5/R6/R7 and R14 tested — was never
      the right grain. Also **ACCEPTED**: (a) a falsifiable 12/12 gate over `nodeterms ∪
      tools/bench/main_vi_shiftregs_v1.json` was available in the same function, so R14 as written could not pass
      against any correct census; (c) the SRs' OUTER terminals **are** in the census as `#637` t11/t10 (wires
      4185/7506), confirming 39(g) — the objects are outside, the dependency is not; (d) three censuses are three
      reads of one `Nodes[]` array and bound nothing about excluded classes.
    - (d) 🔴 **R14 IS DEMOTED TO A FACT LINE AND IS NOT RE-RUN (41(c)).** Its wording is falsified, so re-emitting
      it as a `FAIL` would buy a third paid review of a known fact; the material session was right to revert the
      un-run rewrite rather than ship it. **And no required 12/12 gate is added** — the no-new-device order
      stands (user, 2026-09-18 08:53) and, more to the point, the right test is not node-level at all.
    - (e) **ONE CITATION WITHDRAWN, THE CLAIM SURVIVING ON DIRECT MEASUREMENT.** 39(g) cited
      `tools/gscript.py:947-948` for "shift registers are outside the nodeterms census"; that line is the
      `tunnels()` docstring and distinguishes SRs from `LoopTunnel`s only, so **the citation is withdrawn** — it
      was `inference-over-measurement` wearing a `file:line`. The claim itself stands on the run's own reading:
      `[4256, 4274, 4334, 4344]` absent from nodeterms, 8 of 12 present.
    - (f) **THE DISCRIMINATING TEST, ADOPTED BUT NOT RUN THIS CYCLE** (the review's own, files-only, ~10 lines):
      all 14 register uids of `tools/bench/main_vi_shiftregs_v1.json` against `diagram_tree_main.json`'s `uids` —
      **0/14 ⇒ class exclusion, 0 &lt; k &lt; 14 ⇒ selective loss.** It settles (e)'s mechanism cheaply.
    - (g) ⚠️ **A QUIET LOSS, NAMED: a cycle's `## NEXT` is DESTROYED when the next cycle rewrites it.**
      `archive/2026-09-20-status-cycle54-relocate.md` §4 records that cycle 53's NEXT has **no verbatim source on
      disk** — rewritten in place, only cycle 50's archived, and this is **not a git repository**. Rule 4 says
      nothing is deleted, only moved, and NEXT has been silently exempt. **Habit, not a device: the closing
      session copies the outgoing NEXT into its relocation file before rewriting it.** (The outcome review's
      `git init` recommendation is the real fix and is the user's call — see 44.)

44. **THE 5th OUTCOME REVIEW FIRED SIX VIOLATIONS AND THE WORK STOPS FOR A RE-PLAN WITH THE USER.** Judgement,
    cycle 55, from `archive/peer/2026-09-20-outcome-review-20260920.md` (claude/outcome, fable medium thin,
    ANSWERED, $3.2236, 199 s), routed by `tools/outcome_review.py:191-192` — already the 2026-09-18 trial
    routing, nothing patched.
    - (a) **THE VERDICT, verbatim and in order:** `OUTCOME-VIOLATION: goal-requirement-not-advanced` ·
      `product-not-runnable` · `tooling-over-delivery` · `decision-starved` · `ordering-stale` ·
      `measurement-without-product`. `scope-inflation` explicitly NOT flagged. Q1: *"The user can RUN nothing
      today that they could not run at the last outcome review."* Q2: requirements **1, 2.2, 2.3, 2.4, 2.5, 3**
      have produced nothing runnable since the project began; req 1 not moved for the **4th** consecutive review.
      Q3: *"Not defensible."* Q6: *"The original VI — the same verdict as all five previous reviews."*
    - (b) 🔴 **DECISION — `STOP`.** CLAUDE.md §5: an outcome violation makes the next cycle a **delivery** cycle,
      *"and on repetition the work stops for a re-plan with the user."* Delivery cycles HAVE been run since the
      last violation — S1 (cycle 48) and S2 (cycle 51) both delivered saved files — and the verdict repeated
      anyway, which is exactly the repetition clause. The reviewer whose only job is "was this worth doing" says
      the ratio is not defensible and names the re-plan as owed. **Continuing on my own judgement would be the
      drift this layer exists to catch**, so the runner is stopped and the question goes to the user.
    - (c) **AND IT IS NOT ANSWERED BY BUILDING ANYTHING.** CLAUDE.md §5 forbids answering an outcome violation
      with a device, and the user's 2026-09-18 08:53 no-new-device order stands independently. Nothing was built
      in response to this verdict.
    - (d) **WHAT THE NEXT SESSION RUNS THE MOMENT THE USER SAYS CONTINUE** — so a "keep going" costs nothing and
      re-derives nothing. The review's own item 2 and 39(d) agree on the shape: **the next act is a STAGE, not a
      diagnostic** — the minimal loop set that is **CLOSED UNDER ITS WIRE SOURCES**. Concretely that is loop
      **1.2 together with 1.5**, because 1.5's only open rows (`#10407` t0 fed by `#10686 'x .and. y?'`, t2 fed
      by `#10757 'element'`) are exactly the 1.2 → 1.5 crossings, and t6 still needs the construction verb §6
      never named. Pre-work, files-only and cheap, in this order: (1) re-derive the 17 rows at **terminal grain**
      from `main_vi_nodeterms.json` (all 59 of `#637`'s terminals) instead of the truncated netmap `wires` table,
      and diff — 43(c); (2) the 14-register class-exclusion test — 43(f). Then the stage, with every connection
      type-checked by `Is Broken?` **on a second ordered pass** — 42(b).
    - (e) ⚠️ **OPERATIONAL, MEASURED TWICE THIS CYCLE AND UNEXPLAINED: ≈30,000 handles are added per ~80-second
      scripting run while `ref_counts` reads 0 live.** 34,207 → 63,416 (attempt 1) and 34,166 → 60,591
      (attempt 2), each after its own restart. **The client-side reference gate cannot see this**, so CLAUDE.md's
      "20 runs leave the handle count flat (±100)" acceptance is not measuring what it believes. Recorded as a
      FINDING, not a build (no-new-device order). Until it is explained, **restart LabVIEW before every batch**,
      mechanically.

45. **THE USER ANSWERED THE STOP (2026-09-20 ~09:40): CONTINUE — and 1.5 FOCUS crosses from 1.2 by LOCAL VARIABLES,
    NOT by wires; 1.5 is NOT merged into 1.2.** Interactive chat judgement on the user's words: *"1.5 루프는 사실
    데이터에 전혀 남지 않는 부분이라 local variable 사용해도 문제가 없을 것 같은데 — 1.2와 합치는게 좋을지, 아니면
    wiring이 아닌 local variable 사용이 좋을지 판단해서 진행하도록."* The user also had `git init` run (local only,
    no remote) — the folder is a repository from this commit on.
    - (a) **NOT merged.** 1.5 carries the ASI serial call (`#48`, VISA). Putting it inside 1.2 (tracking) puts a
      VISA call on the per-frame tracking path — the exact shape rule 1c disqualifies (*"a mechanism that CAN stall
      the frame loop is disqualified even if it usually does not"*). Separate loop stands.
    - (b) **Local variables ARE the project's recorded latest-value transport for this class of channel** —
      `docs/decisions.md:28` (scheduler → motor: *"local variables, as agreed with the user"*),
      `restructure-plan-4.6.md:55`. Prior art exists; this is not a new device. Focus output never enters the
      saved traces (user's domain statement), so a lost or repeated read changes no number the experiment keeps.
    - (c) **What crosses.** 1.5's two open rows are `#10407` t0 ← `#10686 'x .and. y?'` (the every-25-frames
      schedule, BOOLEAN) and `#10407` t2 ← `#10757 .element` (index of closest cal-image slice, bead 2 — the focus
      PAYLOAD). Construction: on the S2 artefact, create two INDICATORS on the copy's panel, wired at the sources
      **where they are today** (both still in loop 1.1 `#637`, since 1.2 does not exist yet); in loop 1.5
      (`#23032`, 37(h)) read them as LOCAL VARIABLES into t0 / t2. When 1.2 is built later the indicator terminals
      move with their source nodes (one node per `move_in`, 37(d)); the local variables in 1.5 need no change.
      **This makes S3 = 1.5 alone CLOSED UNDER ITS SOURCES — no 1.2 needed first.** 44(d)'s "1.2 together with
      1.5" is superseded.
    - (d) **Cadence is preserved by an edge, not by luck.** A free-running 1.5 could read the schedule boolean
      twice (double autofocus) or zero times (missed) per 25-frame window. So 1.5 also reads a third local
      variable — the frame counter that already drives `#10686` — and acts when `schedule == TRUE AND counter !=
      last-handled counter` (one shift register). Rule 1a reading: the per-bead maths and the ASI command are
      untouched; only WHEN the existing command fires is now decided in another loop, and the user has declared
      that channel data-free. A `Wait (ms)` of 1 ms in 1.5 so it does not spin.
    - (e) **Still forbidden**: the 38(g) tunnel construction (autofocus once after acquisition). Local variables
      are not that: they are read every iteration of a loop that runs concurrently with acquisition.
    - (f) **Stage plan (split rule): S3a** = indicators created and wired at the sources + saved
      (`claudeDev\D1_s3a_focus_ind.vi`, ExecState 1 preloaded, md5 logged) · **S3b** = the five 1.5 nodes moved into
      `#23032`, internal 7 rows re-wired, t0/t2/t6 fed from local variables / the counter shift register, saved
      (`claudeDev\D1_s3_loop15.vi`). Prior-art review once per stage script; diagnostics under `tools/bench/`
      first when a construction verb (a local variable placed by scripting, `#10407` t6) is unmeasured.
    - (g) **Open for the user, not a blocker**: t6 of `#10407` (§6 names no construction verb) is resolved by the
      same local-variable route if it is a value, by measurement if it is not.

## Pre-decided — ADDED 2026-09-20 (cycle 56): the panel-object verb WORKS · 45(c)(iii) corrected · Pre-decided 2 mis-cited

46. **THE TRANSPORT IS REACHABLE AND ITS FIRST HALF IS BUILT: A FREE-STANDING FRONT-PANEL INDICATOR CAN BE CREATED
    BY SCRIPTING ON THIS VI, AND A SAVED FILE PROVES IT.** Judgement, cycle 56, 2026-09-20, from
    `tools/bench/diag_s56_transport3.{py,log,json}` (21 pass / 7 fail), `…transport3b.*` (11/3),
    `tools/bench/diag_s56_transport2.*` (13/5), `tools/bench/diag_s3a_ind_transport.*` (6/2, `BGRUN TIMEOUT`) and
    `tools/bench/diag_c56_topdiagram_files.*` (7/0). 34–45 stand; this resolves 45(f)'s diagnostic-first clause,
    corrects 45(c)(iii), and corrects a mis-citation of Pre-decided 2 that ran through all five of the cycle's briefs.
    - (a) 🎉 **THE ROUTE THAT WORKS, measured end to end and SAVED.** `build_index_array` on the
      `VI → Block Diagram` head places `IndexArray #23486` with `owner_of` = **`('TopLevelDiagram', 536)`**, error
      `''`; `node_info(max_n=40)` goes **0 → 1** (`[(0,'Index Array','Index Array')]`);
      `create_indicator(Nodes[0].Terminals[2])` produces `ControlTerminal` **#23541**, census **114 → 115**, error
      `''`; `delete_object(IndexArray[0])` returns `ExecState` **1** (`remove_bad_wires` not needed). Artefact:
      **`claudeDev\DIAG_s56_t3_p2_20260920_221901.vi`, md5 `cbe9ddd5690983fae2919b3027264d4b`, 476,182 B,
      `26 00 80 00`**, saved legally (`allow_broken` False, `gui_save` never called). The route is
      `docs/NAMES.md:476-478` + `docs/stage2-assembly-step-b.md:49-50`, never before tried on this VI.
      **So the empty top-level `Nodes[]` was EMPTY, not DEAD** — of the three readings cycle 56 could not separate
      from the files, the measurement picks the first.
    - (b) **`Diagram #536` IS the top-level diagram, and `#686` is NOT.** Live: `Traverse Diagram[0]` =
      `{'class':'TopLevelDiagram','uid':536,'owner':''}`, `diag_index(#536) = 0`. `#686` is a
      **`FlatSequenceFrame`**, and the owner chain `#639 → WhileLoop #637 → Diagram #686 → FlatSequenceFrame #? →
      STOP` dies in one hop — the frame's uid is unreadable (`error 1055` on the direct read, `error 1092` for
      `FlatSequenceFrame` as a Traverse class), so `#536` is reached by elimination, never by a walk.
      `diagram_tree_main.json`'s `"0"` row is **neither a diagram nor a placeholder but an index whose identity was
      discarded** (`diagram_tree_main.py:51-52` keeps only `d["owner"]`); `net_map`'s *"0 = top level"*
      (`tools/gscript.py:2505`) was a docstring assumption until this cycle corroborated it.
    - (c) 🔴 **ALL 114 PRE-EXISTING `ControlTerminal`s ARE OWNED BY CLASS `Diagram`, NOT `TopLevelDiagram`**
      (`tools/bench/diag_s56_transport3b.log:15`, `{'Diagram': 114}`) — the original's panel terminals all sit
      inside structures, and the top-level diagram held **zero** of them until we made one. This is why
      `wire_indicators` fails: three attempts, at the source's diagram and at `diagram_index=0`, all returned
      `error 5001: LV-Scripting.lvlib:Wire Indicators.vi<ERR> | Control <label> not found` for an indicator the same
      run had just read on the same VI. Target wire **0 → 0**, `#10686` t0 **3/3 wired** before and after, `#637`
      **59 → 59 terminals / 48 → 48 wired**, no tunnel or border object appeared (37(e) grain throughout).
    - (d) 🔴 **THE ONE REMAINING UNKNOWN FOR S3a IS NOW SINGLE: how to wire a `ControlTerminal` to a node terminal
      on a NESTED diagram.** Candidates, in the order they are to be tried, cheapest first:
      (1) **a pure READ — does a nested diagram's `Nodes[]` enumerate `ControlTerminal`s at all?**
      `docs/d1-build-plan.md:1227,:1230-1231` records six `ControlTerminal`s on `#639` and `Get Controls.vi`
      returning 5001 at index 0 but succeeding at 43, so the question is answerable from the files and the existing
      censuses. If they ARE enumerated, `OpConnectNested_v1` can address the terminal by index and the connect is
      an ordinary same-diagram one. (2) `move_in` of `ControlTerminal #23541` into `#639` — 37(d)'s severing cost
      does **not** apply, because a freshly created terminal has no wires to cut — then wire same-diagram.
      (3) `connect_ctl` (`gscript.py:983`, which has run clean before with a top-level `Nodes[]` source) now that a
      node can demonstrably be placed at top level. 🔴 **Do not spend a fourth `wire_indicators` attempt before (1).**
    - (e) 🔴 **45(c)(iii) IS CORRECTED: THERE IS NO COUNTER FEEDING `#10686`, AND `'current image number'` IS NOT A
      PER-FRAME COUNTER.** `#3191` is a **`CaseStructure`** — no function name — and **all four** of its terminals
      are `is_source=False`: t0 `''` w3050 (selector, from `#3057 'x = 0?'`), t1 `''` w3268, t2
      `'current image number'` w3747, t3 `'LastBufferNumber'` w3356 (`main_vi_nodeterms.json` diagram 43). Wire
      3747's only source in the whole census is **`#6810` t10 = `get buff image-lost frames.vi`**, the camera
      acquisition subVI (`docs/NAMES.md:80-87`; panel row 103, `docs/main-vi-panel-map.md:383`, control 34200), so
      that indicator carries the **camera buffer number, which jumps by more than 1 across lost frames** — an edge
      on it does NOT fire once per acquired frame. The real frame counter is wire **3268**, which has **0 sources**
      in the census (six sink endpoints: `#376` t7, `#1114` t0, `#2136` t3, `#3191` t1, `#10068` t3, `#29240` t3)
      and arrives from a shift register or border object (`docs/frame-loop-wire-graph.md:161`). **Consequence for
      45(d): the cadence edge is built either on the schedule boolean's own rising edge or on wire 3268 obtained at
      its real source, and which of those is right is NOT decided here** — the third indicator of 45(c) is
      WITHDRAWN, and S3a creates TWO.
    - (f) **THE SWALLOW IS REPAIRED — ACCEPTED, and it was the cycle's most expensive lesson.** `gscript.py`'s
      `create_control` and `create_indicator` classified LabVIEW's **error 1055** modal dialog as `"modal dialog"`
      and returned an empty list with `exception None`. Twenty such calls cost **1502 s (a `BGRUN TIMEOUT`) and
      $4.94** before a watchdog screenshot of the dialog explained it. Repaired at both sites in the shape
      `delete_object:2264-2272` already carried, and PROVEN: the same call now raises
      `RuntimeError: run blocked behind a modal dialog (dismissed by watchdog after 8s); screenshot(s): …`.
      **A wrapper that hides the machine's error is worse than no wrapper** — the sibling of "when a diagnosis is
      guessed twice, build the reader".
    - (g) 🔴 **AND THE FRAMING THAT COST THE MOST WAS MINE.** Dispatch 3's `L1`/`L2` FAILs made **zero calls to the
      machine** — they restated a rule as if it were a reading — and I built the next peer question on top of them
      ("the transport verbs are unreachable, so a new op VI is unavoidable").
      `archive/peer/2026-09-20-c56-transport-verbs-unreachable.md` (claude/hypothesis opus max, ANSWERED, $4.1928)
      refuted it at exactly that point — *"the claim is not supported by the run that produced it"* — and named
      `build_index_array → create_indicator → delete_object`, `copy_by_index(cls='Local', duplicate=True)` and
      `Control → Create:Local Variable` 6331C02. **DISPOSITION: ACCEPTED on the decisive point; the "unreachable"
      framing is WITHDRAWN**, and (a) above is that review's own second test, run and passed.
      🔴 **RULE for every later brief and every later gate: a gate that makes no call to the machine is not a
      `FAIL`, it is a note, and it may never be listed among measured gates.** Same family as 41(c).
    - (h) **`copy_by_index(cls='Local', duplicate=True)` IS NOT USABLE AS IT STANDS.** It cleared the
      "nothing was copied" check and then raised `RuntimeError: copy_by_index: Target still broken after finish
      (ExecState 0) - not saved` (`gscript.py:1548-1551`): the op works through the shipped
      `NIScriptingExamples\Moving Objects\` fixtures, where ~94 of the main VI's subVI paths do not resolve, and it
      has **no destination-diagram control**, so `move_in` to `#23058` was never reachable through it. Both fixtures
      were left holding md5 `cbe9ddd5…`; the documented protocol restores them at the next copy's start. Recorded,
      not repaired, not re-run.
    - (i) **NO GENERIC PROPERTY READER EXISTS**, so the 8 existing `Local` objects' bindings cannot be read: every
      reader in the fleet is purpose-built with a hard-wired ID, and `6355400` (`Local.Control Name`) appears **0
      times** in `docs/vi-server-ids.json` and **0 times** in `tools/gscript.py`. The 8 uids are 2143, 2991, 3097,
      3160, 4277, 11574, 16942, 25805, all owner `Diagram`, count 8 → 8 across the cycle.
    - (j) ⚠️ **HANDLES — 44(e)'s unexplained growth measured a THIRD and FOURTH time:** 30,684 → 54,367 over 330 s
      and 30,691 → **63,517** over 78 s, each after the run's own restart, with `ref_counts` reading 26/26/0 and
      13/13/0 live. The client-side reference gate still cannot see it. LabVIEW was left UP (pid 8856) at cycle
      close, so **the next batch restarts first, mechanically.**
    - (k) 🔴🔴 **PRE-DECIDED 2 SAYS "NO FURTHER PROCESS DEVICE" — NOT "NO NEW OP VI" — AND I MIS-CITED IT IN ALL
      FIVE OF THIS CYCLE'S BRIEFS.** `docs/cycle27-plan.md:31` reads *"**No further process device** (user, 08:53)
      — still the standing order. A retrospective naming one is a finding."* A **process device** is gate and
      retrospective machinery; an **op VI** is deliverable-construction tooling, and every stage of D1 so far was
      built with them (+17 by the 5th outcome review's own count). So the order does not reach an op VI that places
      a Local Variable, and **the S3b transport needs no decision from the user**: if `Control → Create:Local
      Variable` 6331C02 through `build_invoke` is the route, it is simply built. The mis-citation is what turned
      (g)'s two no-call gates into FAILs and what sent a $4.19 review out to attack a rule instead of a machine.
      **Cite Pre-decided 2 by its words, never by its remembered shape.**

## Pre-decided — ADDED 2026-09-20 (cycle 57): the transport is SOLVED for location and addressing · the blocker is TYPE

47. **THE S3a TRANSPORT RAN END TO END FOR THE FIRST TIME. `move_in` TOP-LEVEL → NESTED WORKS, AND
    `wire_indicators` GIVEN THE INDICATOR'S OWN DIAGRAM MAKES THE CONNECTION WITH NO 5001.** Judgement, cycle 57,
    2026-09-20, from `tools/bench/diag_s57_ctmove_wire.{py,log,json}` (`BGRUN END rc=1 after 123s`, 27 pass /
    2 fail), the files-only read behind it, and `archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md`
    (claude/priorart, ANSWERED, $7.2933, verdict **NOT novel**, 5 slugs — all disposed in that file's
    `## What was done with it`). 34–46 stand; this resolves 46(d), closes the three 5001s, and names the one
    thing that actually blocks S3a.
    - (a) 🎉 **THE ROUTE, measured step by step.** On a scratch of `D1_s2_loops.vi`: `build_index_array` on the
      `VI → Block Diagram` head → `owner_of` `('TopLevelDiagram',536)`, `node_info` **0 → 1** →
      `create_indicator(Nodes[0].Terminals[2])` → `ControlTerminal` **#23541**, census **114 → 115** →
      `delete_object(IA)` → `ExecState` **1** (46(a) reproduced exactly, all error columns `''`) →
      **`move_in(#23541, dest = the LIVE index of `#639`)` → `owner_of` `('TopLevelDiagram',536)` →
      `('Diagram',639)`, census 115 → 115, panel rows 115 → 115, `ExecState` STILL 1.** Top-level → nested had
      never been tried on any terminal, let alone a freshly created one. It leaves one junk `Invoke` uid (the uid
      the deleted Index Array released); purge it in-run.
    - (b) 🎉 **THE THREE 5001s ARE EXPLAINED AND CLOSED — IT WAS ALWAYS THE ARGUMENT, NEVER THE VERB.**
      `tools/gscript.py:1787-1789` feeds `Diagram in` from `diagram_index`, which scopes the **INDICATOR**
      lookup and never the source. All three cycle-56 attempts named pre-existing indicators whose terminals sit
      on other nested diagrams, so no index passed could have matched. Given `diagram_index` = the diagram where
      the indicator's terminal actually lives, `wire_indicators` **wired**: target wire **0 → 10799**, whole-VI
      `Wire` delta **0** (a branch onto the existing net), `#10686` t0 `'x .and. y?'` **3/3 wired before and
      after**, and **`#637` 59 → 59 terminals / 48 → 48 wired, NO tunnel and NO border object** (37(e) grain).
      The identical fault class was closed once before by measurement — `docs/d1-build-plan.md:1231`,
      `'Auto-Reset'` at `src_diagram_index=0` → 5001 from `Get Controls.vi`, the same label at 43 → wired,
      `:1251` "CLOSED by measurement: wrong `src_diagram_index`". **Excluding a verb that has never been given a
      correct argument is the repeat, not a fourth attempt.**
    - (c) 🔴 **THE 38(g) SEMANTICS OBJECTION IS ACCEPTED, AND IT DECIDES THE ORDER OF THE BUILD.** A top-level
      `ControlTerminal` wired to a source inside `WhileLoop #637` crosses the loop border as a tunnel, and a
      while-loop output tunnel delivers ONE value when the loop ends — legal, `ExecState` 1, and useless to a
      local-variable read in loop 1.5 that must see the value every iteration. **So `move_in` into `#639` is not
      a fallback, it is the only acceptable route**, and it matches the VI's own practice: all 114 pre-existing
      `ControlTerminal`s are owned by class `Diagram`. The shape is now measured rather than argued — (b)'s
      59/59 · 48/48 · no border object. `tunnel_indicator` (`tools/gscript.py:1882-1903`) is **REJECTED for
      S3a for the same reason**: it builds the indicator off a `Tunnel.'Outer Term'`, i.e. it IS the banned shape.
    - (d) 🔴 **THE REMAINING BLOCKER IS TYPE, AND NOBODY HAD NAMED IT.** `Terminal.Create Indicator` **6349C02
      takes no type argument**, so a created indicator inherits the type of the terminal it is created from. The
      indicator built by (a) came off the carrier Index Array's `index` terminal — its label read back off the
      machine as **`'index'`** (hex `696e646578`, no newline, no duplicate) — i.e. a NUMERIC. Wiring it to the
      **BOOLEAN** `'x .and. y?'` left `ExecState` **1 → 0** and, on the ordered second pass (42(b), idempotent
      re-connect, `wire_delta` 0, op error `''`), **`Is Broken? = True`** — the signature 42(a) validated for a
      type mismatch. **Competing reading, RECORDED not dismissed** (`archive/peer/2026-09-20-c57-transport-typebreak.md`,
      claude/hypothesis opus max, ANSWERED, $3.7974, 41(b)): that `Is Broken?` also reads True on a two-source
      wire and that 10799 sinks at a structure border, so the break may be the shape rather than the type. The
      two are separated by a control pair on ONE variable — same verbs, same diagram, same branch-onto-an-existing-net
      shape, numeric source `#10757` t1 `'element'` (wire 10990) in place of the Boolean — which is 42(a)'s own
      design and is what cycle 57's second build act ran. **🎉 IT RAN, 35 pass / 0 fail, AND THE TYPE READING WINS:**
      `tools/bench/diag_s57_typepair.{py,log,json}` (`BGRUN END rc=0 after 242s`). Identical creation route,
      identical label `'index'`, identical `move_in` into `#639` @46, identical `wire_indicators` call shape, and
      the same branch onto an existing net feeding the same structure-border sink — **only the source's TYPE
      differed**. Result: op error column **`''`**, indicator wire **0 → 10990**, whole-VI `Wire` **1905 → 1905**,
      `#10757` **3/3 wired before and after**, `#637` **59 → 59 / 48 → 48, no tunnel, no border object**,
      `ExecState` **1 → 1**, and on the ordered second pass (`wire_delta` 0, op error `''`)
      **`Is Broken?` = False on wire 10990**. **The competing shape reading is REFUTED BY MEASUREMENT** — leg 2
      carries that shape exactly and reads clean — so the Boolean→numeric mismatch is the cause, and
      `Is Broken?`'s True/False split is again the instrument 42(a) validated.
    - (h) 🎉 **S3a's NUMERIC HALF IS DELIVERED, AND THE SAVE-FIRST ORDER OF (e) IS WHAT MADE IT SURVIVE.** Two
      openable artefacts, both saved legally (`ExecState` 1 at each save point, `allow_broken` False, `gui_save`
      never called), both LV2026 `26 00 80 00`:
      **`claudeDev\D1_s3a_ind_placed_20260920_234341.vi`** md5 `0b9a070289a08a22a8843e287b183398`, 476,209 B —
      the indicator created and `move_in`-ed onto `Diagram #639`, **unwired**; and
      **`claudeDev\D1_s3a_num_ind_20260920_234341.vi`** md5 `fceaa0a1d068622596842435b830bffe`, 476,146 B — the
      same, wired to `#10757` t1 `'element'`, the payload source of 45(c). The placed artefact was **reopened
      COLD in a freshly restarted LabVIEW and read `ExecState` 1 with `owner_of(#23541) = ('Diagram',639)`**, so
      the move survives a save/reload and is not an in-memory artefact. Verification level: **STRUCTURAL**, never
      functional — no VI was run (34(f)).
    - (i) 🔴 **WHAT IS LEFT OF S3a IS EXACTLY ONE THING: A BOOLEAN-TYPED CARRIER.** Since 6349C02 takes no type
      argument (d), the schedule indicator for `#10686` t0 `'x .and. y?'` must be created from a terminal that is
      already Boolean. `#10757`'s own class was measured `IndexArray` (Traverse index 20 of 47) with terminals
      `[(0,'array',sink,121),(1,'element',SOURCE,10990),(2,'index',sink,10947)]`, and the carrier used so far is
      an unwired Index Array whose `index` terminal is numeric. Two routes, and the **cheap one is tried first**:
      **(1) NO NEW TOOLING — find an existing builder that places a node with a BOOLEAN terminal at top level**
      (`build_property` `tools/gscript.py:2194` and `build_invoke` `:2159` both already take a `diagram_index`,
      and a Boolean-valued property yields a Boolean output terminal), then create → `move_in` → wire by the now
      proven route. **(2) THE DURABLE FIX, permitted and named but NOT built this cycle — ONE new op VI** that
      calls `Terminal.Create Indicator` on a **nested** diagram's `Nodes[n].Terminals[t]`: a splice of
      `OpConnectNested_v1`'s ladder (`tools/recipes/build_opconnectnested_v1.py:419-420`) with
      `OpCreateIndicator_v0`'s call. It would make the indicator **born correctly typed, correctly located and
      already wired**, retiring `move_in` and `wire_indicators` from this path entirely, and it is allowed —
      46(k): Pre-decided 2 forbids a further PROCESS DEVICE, not an op VI. Route (1) is first only because it
      costs one diagnostic and no gate; if it fails, (2) is the answer and is not to be deferred again.
    - (j) ⚠️ **NO READER IN THIS FLEET RETURNS A DATA TYPE.** Measured across 12 hits: the only representation
      reader is `OpConstValueN_v1.vi` (`NumericConstant.Representation` 5DCFC00, `docs/toolkit-capabilities.md:59`,
      `docs/NAMES.md:969`) and it reads a numeric CONSTANT. So a type mismatch is not predictable before wiring
      and can only be read AFTER, through `Is Broken?` on an ordered second pass. **Until a type reader exists,
      every new connection is type-checked by 42(b), never assumed** — and (d) is the first time that instrument
      has paid for itself on a real build rather than on a calibration pair.
    - (k) ⚠️ **OPERATIONAL, AND IT COST A RUN: a sub-agent that backgrounds its batch and ENDS ITS TURN kills the
      batch.** Dispatch 4 returned "holding until it lands" and exited; a relaunch then restarted LabVIEW under
      the still-live first run, which died in phase A (`com_error -2147023170 / -2147023174 RPC`) and was logged
      as a **NON-RESULT**, not a budget failure. This is OPEN 54(b) firing exactly as written. **Every material
      brief that backgrounds a run must say: stay in the turn until the log carries its final `BGRUN END`/
      `TIMEOUT` line.** Handles across the two legs: 63,313 → 30,688 → 60,291 → 30,695 → **63,533**, with
      `ref_counts` 22/22/0 live — 44(e)'s unexplained growth recurs a fifth and sixth time.
    - (e) 🔴 **A FAULT IN MY OWN BRIEF, AND IT IS THE USER'S 2026-09-19 RULE: THE RUN HELD A LEGAL ARTEFACT AND
      SPENT IT.** `ExecState` was **1** immediately after the `move_in` and the brief's phase order put the wire
      before the save, so a run in which **every transport verb succeeded** ended at `ExecState` 0, saved
      nothing, and left **no file to open**. *"A step is not done until it has left a file."* **RULE for every
      later stage: the save goes at the last point the VI is measured legal, not at the end of the script**, and
      a stage that reaches `ExecState 1` and proceeds past it without saving is a failed stage however well its
      verbs ran. The corrected order is create → `move_in` → **save** → reopen COLD → wire → save again.
    - (f) **THE PRIOR-ART REVIEW EARNED ITS $7.29 AND IS DISPOSED IN FULL** — `contradicted`, `unread-evidence`,
      `refuted-already`, `helper-exists` ACCEPTED (two candidates withdrawn before a call was spent on them,
      the winning verb identified, the 38(g) objection turned into the build order); `already-measured` ACCEPTED
      on its cost and REFUTED on its citation, because the lines it called "a different question" are exactly the
      prior art for the verb that worked. ⚠️ **The `FIXED:`/`REFUTED:` lines are written but their ACCEPTANCE BY
      `guard_cycle` IS UNVERIFIED** — the review is stamped 2026-09-20 23:00:54 and `docs/cycle27-plan.md` carries
      a day-granular frontmatter date, which cannot postdate it; the plan date was **deliberately not rolled
      forward to satisfy a gate**. Check with a dry run before the recipe launch.
    - (g) ⚠️ **CHARGED TO THIS CYCLE: the FIRST ACT re-measured something already on disk.** "Does a nested
      diagram's `Nodes[]` enumerate `ControlTerminal`s?" was answered in four route-B run logs
      (`build_d1_routeb_v*_run*.log:179-180`, `Nodes[None] with terminals []`) and, more strongly, at
      `tools/bench/diag_queue_donor2.log:48,:55`, which measured it **after** a `move_in` into a nested diagram —
      the exact post-condition that kills candidate (2)'s second half. What the act did add and was needed: the
      verb-addressing table, `move_in`'s uid-addressing and its one prior `ControlTerminal` success
      (`probe_move_ctlterm_v0.log:130-133`), and the `d1-build-plan.md:1231` prior art that produced the route.
      **Before commissioning a read, grep the bench logs for the reading first.**

## Pre-decided — ADDED 2026-09-21 (cycle 58): the Boolean carrier EXISTS · route 1's block is STRUCTURAL and has one named fix

48. **A BOOLEAN CARRIER EXISTS AND 47(i) ROUTE 1 IS NOT DEAD — BUT IT CANNOT REACH 47(e)'s SAVE POINT AS 47(i)
    SPECIFIED IT, AND THE REASON IS A TENSION NOBODY HAD NAMED.** Judgement, cycle 58, 2026-09-21, from
    `tools/bench/diag_s58_boolcarrier.py` and its two runs (`…_run1.log` `BGRUN END rc=1 after 229s`, 51 pass /
    9 fail; `…_run2.log` `BGRUN END rc=1 after 248s`, 54 pass / 9 fail — the SAME 9 gates both times).
    34–47 stand; this resolves 47(i) route 1's first half and re-cuts its second.
    - (a) 🎉 **THE CARRIER QUESTION IS ANSWERED: `build_property` (`tools/gscript.py:2194`) IS THE ONLY FLEET VERB
      WITH A BOOLEAN-BY-CONSTRUCTION OUTPUT TERMINAL, AND IT WORKS.** Three candidates placed at the top-level
      diagram with every error column `''`, `owner_of` `('TopLevelDiagram',536)`, `node_info` **0 → 1**,
      ControlTerminal census **114 → 115**: C1 `('VI Server:VI',[291,292])` carrier t4 → indicator label read off
      the machine **`'Metrics:Front Panel Loaded'`**; C2 `('VI Server:VI',[242])` carrier `'Def Err Handling'` →
      **`'Automatic Error Handling'`**; C3 `('VI Server:Wire',[6371004])` carrier `'Broken?'` → **`'Is Broken?'`**
      (so the class string `VI Server:Wire` resolves). `build_invoke` `:2159` is OUT — no Boolean-returning method
      exists in `docs/vi-server-ids.json`. Every loop/exit verb is out: the conditional terminal is a SINK.
    - (b) 🔴 **THE BLOCK, AND IT IS STRUCTURAL: A BOOLEAN TYPE NEEDS A *SOURCE* TERMINAL, AND
      `create_indicator` ON A SOURCE TERMINAL MAKES A REAL WIRE.** Whole-VI `Wire` **1905 → 1905 → 1906**: the
      indicator is born wired to the carrier (uid **23586** on C1, **23576** on C2), and that wire is
      **STILL ALIVE after `delete_object(carrier)`**, with 0 pre-existing wire uids removed. `ExecState` therefore
      reads 1 → 1 (after `build_property`) → 1 (after `create_indicator`) → **0 (after the carrier delete)**
      — ⚠️ **on C1 and C2 ONLY; C3 never reaches that timeline because it breaks at placement, see (c)**, and the
      first writing of this line omitted that qualifier (caught by `archive/peer/2026-09-21-c58-boolwire-dangling.md`
      §0 and corrected here, cycle 58, by the judgement session). So
      47(e)'s save point is unreachable and all three candidates left **ZERO artefacts**. Cycle 57's route escaped
      this only because its carrier terminal was the Index Array's `index`, a **SINK** — no wire is created from a
      sink, which is also exactly why that indicator came out NUMERIC. **The two requirements pull against each
      other: the type comes from a source, and the source is what ties the indicator to the carrier.** That is a
      finding about the verb, not a missed call.
    - (c) ⚠️ **C3 IS WITHDRAWN ON ITS OWN EVIDENCE:** `build_property('VI Server:Wire', …)` takes the VI to
      `ExecState` **0 at placement**, before any delete. C2 is the carrier of record (one property, `ExecState` 1
      throughout, label non-duplicate and newline-free); C1 is its only alternate.
    - (d) 🔴 **THE DISPOSITION — ROUTE 1 IS COMPLETED BY ONE NAMED VERB CALL, DECOMPOSED INTO THREE SAVED STEPS,
      AND ROUTE 2 IS NOT TAKEN THIS CYCLE.** The wire that blocks the save is **ours**, created seconds earlier,
      and its uid is held; deleting it before the carrier leaves both ends unwired and should return the VI to the
      state cycle 57 saved from. Of the three dispositions material #1 put on the table, `remove_bad_wires_scripted`
      is **REFUSED** — it has a measured over-removal on this VI (`archive/2026-09-17-status-d1-route-b-2.md:45`,
      *"DELETES THE TUNNEL"*), which is a rule-1a hazard, and a named-uid delete is strictly narrower. 47(i)
      route 2 (the one op VI, `Terminal.Create Indicator` on a nested `Nodes[n].Terminals[t]`) **remains correct,
      remains permitted (46(k)), and becomes the automatic next act if (e) fails at the same place** — it is
      deferred here because the 5th outcome review flagged `tooling-over-delivery` and `measurement-without-product`
      verbatim, and a one-call fix that ends in a file beats a new op VI that ends in a self-test.
    - (e) **THE DECOMPOSITION (the user's 2026-09-19 rule: a step is not done until it has left a file). Three
      sub-steps, three artefacts, three pass criteria, each starting from the previous FILE in a FRESH LabVIEW:**
      **S3a-B1** from `claudeDev\D1_s2_loops.vi` — place C2 → `create_indicator` on its Boolean source → **delete
      the created wire by its uid** → delete the carrier → pass criterion `ExecState` **1** → save
      `claudeDev\D1_s3a_boolcarrier_b1_<stamp>.vi`.
      **S3a-B2** from B1, cold — `move_in(CT → Diagram #639 @ its LIVE index)`, purge the junk `Invoke` → pass
      criterion `owner_of` `('Diagram',639)` **and** `ExecState` 1 → save `…_b2_<stamp>.vi`. **This is 47(e)'s save
      point and it comes before any wiring.**
      **S3a-B3** from B2, cold — `wire_indicators(→ #10686 t0 'x .and. y?', diagram_index = the LIVE index of the
      diagram the INDICATOR lives on)` → ordered second pass (42(b)) → pass criterion **`Is Broken?` = False** →
      save `…_b3_<stamp>.vi`. A `True` here is the type reading again and sends the next cycle to route 2.
    - (f) ⚠️ **NO SECOND PRIOR-ART REVIEW IS SPENT ON THIS RE-CUT, AND THAT IS AN ASSUMPTION THE USER MAY
      OVERTURN.** `archive/peer/2026-09-20-priorart-d1-s3a-focus-ind.md` ($7.29, verdict NOT novel, 5 slugs, all
      disposed in its `## What was done with it`) reviewed **this same stage** one day ago; (e) changes how the
      stage is CUT, not what is built, and rule 5's archiving exception says to check `archive/peer/` before
      re-asking. Recorded here rather than decided quietly.
      🔴 **OVERTURNED THE SAME CYCLE, BY MEASUREMENT, BY THE SESSION THAT WROTE IT.** `guard_cycle`'s
      `premature-build` device refuses the launch verbatim — *"this RECIPE HAS NO PRIOR-ART REVIEW NEWER THAN
      ITSELF"*, recipe last changed **2026-09-21 01:19**, newest prior-art review **2026-09-20 23:00** — and the
      exemption it offers ("a recipe that HAS already run once under the newest review") does not apply, because
      this recipe has never run. The premise of (f) is simply false: the 2026-09-20 review reviewed a recipe that
      **did not exist**, which is why its stop record reads `sha (none)` (48(g)); it cannot have covered the 1,699
      lines now on disk, so this is not rule 5's "same question re-asked". **A second review IS spent**, and that is
      the right outcome: `CYCLE_GUARD_OFF` is never the answer, and the two releases the gate accepts (`REFUTED:` /
      `FIXED:`) both require a review that saw these bytes. Cost ≈ $7, against a deliverable one run away.
    - (g) ⚠️ **`guard_cycle` REFUSES ONE STEP EARLIER THAN 47(f) EXPECTED, AND FOR A DIFFERENT REASON.** Exit **2**
      comes from `tools/stop_record.py`, verbatim: *"this recipe has a released stop record, but the file itself
      cannot be read, so the release cannot be matched to any bytes"*, `unreadable:
      tools/recipes/stage_d1_s3a_focus_ind.py`. So the prior-art review's 4 `FIXED:` + 1 `REFUTED:` lines were
      **never tested** — the stop record is keyed to the recipe's BYTES, and the gate cannot reach that question
      while the recipe does not exist. **The recipe must be WRITTEN before the gate can be dry-run at all**; no
      date was rolled and `CYCLE_GUARD_OFF` was not set.
    - (h) ⚠️ **TWO HYPOTHESIS REVIEWS, ANSWERED, RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)), NOTHING ACTED
      ON:** `c58-typepair-a1-nonresult` ($3.9606) names three instrument defects (a gate-boundary swallow;
      `diag_s57_typepair.log:37`'s canned reason from an unconditioned `else`; run 1's JSON destroyed by an
      unstamped OUT) — 4 proposals, none implemented. `c58-delete-execstate0` ($3.6322) argued *"the dangling wire
      is not established by this log"* and stated its own falsifier — *"if uid 23586 is alive after the delete, I
      am wrong"*. **B3d read it alive on all three candidates, so the falsifier fired against the review** and (b)
      stands. The one thing acted on was a REMOVAL: a `remove_bad_wires_scripted` step was written into run 2 and
      **deleted before launch**, correctly — see (d).
    - (i) ⚠️ **THE STAGE HAS NOW FAILED TWICE AT THE SAME PLACE AND LEFT NO FILE, WHICH IS THE USER'S OWN
      RE-SPLIT TRIGGER.** (e) IS that re-split; a third full-length retry of the 47(i)-route-1 script under a new
      name is forbidden. Handles 30,965 → 30,687 (own pre-batch restart) → 60,292; refs 33/33/0 live; ORIGINAL
      `2a78e17c…`, `D1_s1_copy.vi` `3e3d23ce…`, `D1_s2_loops.vi` `6ff19497…` byte-unchanged before and after both
      runs; no recipe, no op VI, no VI run (34(f)), no GUI, no motor/ASI/camera.
    - (j) 🎉 **(e) RAN AND S3a's BOOLEAN HALF IS DELIVERED — 36 pass / 0 fail, THREE FILES, `Is Broken?` FALSE.**
      `tools/bench/diag_s58_boolwire.{py,log,json}`, `BGRUN END rc=0 after 306s`. The named fix of (d) is CONFIRMED
      by measurement: `delete_object(target,'Wire',1664,verify=True)` on uid **#23576** returned `gone [23576]`,
      error `''`, **`[]` pre-existing wire uids removed** — there is no by-uid form, so the uid was resolved to a
      Traverse index off the live `Wire` census, and `verify=True` proved exactly one wire vanished.
      `remove_bad_wires_scripted` was neither imported nor called (AST-checked). **B1 `ExecState` 1 → 1 → 1 → 1
      (wire delete) → 1 (carrier delete)** — 48(b)'s 0 is gone. Artefacts, all LV2026 `26 00 80 00`, each saved at
      the last point the VI was measured legal: **`claudeDev\D1_s3a_boolcarrier_b1_20260921_010034.vi`** md5
      `7237b2c1e150ebeaf0f32940b07abcfb` 476,241 B (carrier gone, indicator bare at top level) ·
      **`…_b2_20260921_010034.vi`** md5 `148050141085bc00ffc1e94e9977ea24` 476,245 B (47(e)'s save point —
      `move_in(#23555 → #639 @ live 46)` error `''`, `owner_of` `('TopLevelDiagram',536) → ('Diagram',639)`,
      `ExecState` 1 → 1, junk `Invoke` #23490 purged in-run) · **`…_b3_20260921_010034.vi`** md5
      `dc14dd000dfe90c0426b30fa6b69cbc2` 476,169 B (wired). B3: `wire_indicators(Function[102],
      ['x .and. y?'] → ['Automatic Error Handling'], diagram_index=46)` error column **`''`**, indicator wire
      **0 → 10799** (a branch — whole-VI `Wire` 1905 → 1905, delta 0), `ExecState` **1 → 1**, `#10686` **3/3 wired
      before and after**, `#637` **59 → 59 / 48 → 48, increase 0, no tunnel, no border object** (37(e)), and the
      ordered second pass (42(b), `wire_delta` 0, op error `''`) read **`Is Broken?` = False on wire 10799**.
      Verification level **STRUCTURAL**, never functional — no VI was run (34(f)). **So both legs of S3a now exist,
      each in its own file, built by the same verbs: numeric (cycle 57) and Boolean (here). What does NOT yet
      exist is ONE file carrying BOTH**, which is the recipe `tools/recipes/stage_d1_s3a_focus_ind.py`.
    - (k) ⚠️ **THE HYPOTHESIS REVIEW `guard_peer` FORCED IS ARCHIVED AND DISPOSED, AND ITS LOAD-BEARING OBJECTION
      WAS OVERTAKEN BY THE MACHINE.** `archive/peer/2026-09-21-c58-boolwire-dangling.md` (claude/hypothesis opus
      max + web, ANSWERED 588 s, `$4.3192`) returned *"REFUTED in its load-bearing sentence — the run never measured
      that the indicator is 'left sourced by a wire whose node is gone', and the only post-delete reading of that
      terminal in the whole log says it is bare."* **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b)); nothing in it
      was acted on**, and the script was written in full before the dispatch and unchanged after. Its §0 documentation
      correction IS adopted — that is (b)'s qualifier above, and it is adopted because it is a fact about our own
      text, not a claim about the machine. Whether the rest of it should be adopted is **left open**: the run it
      criticised passed 36/0 and delivered three files, so nothing in it is load-bearing for the next act.
    - (l) ⚠️ **A HOUSE-STYLE HABIT SILENTLY BREAKS A GATE, AND IT COST THIS CYCLE A ROUND-TRIP.** STATUS.md writes
      approximate times as `23:5x` / `01:5x`, and the two `docs/violation-decisions.md` blocks that answer
      `guard_cycle`'s threshold refusal were first written with that spelling. `tools/violations.py:94`'s `DEC_RE`
      requires `(?:[ T]+(\d{2}:\d{2}))?`, so the literal `x` makes the optional time group fail and the block is
      read as **date-only**; `:116` then requires a date-only decision to fall on a strictly LATER day than the
      retrospective that raised the slug, and `archive/peer/2026-09-21-retrospective-cycle57.md` is the same day.
      Both blocks were therefore on disk, correct and unread. **Rule: a `docs/violation-decisions.md` heading
      carries a REAL `HH:MM`, never the `5x` approximation** — the time is what discharges a same-day slug
      (`:115`). Fixed to the files' true write time `01:24`; no date was rolled, no gate patched,
      `CYCLE_GUARD_OFF` never set.
    - (m) 🔴 **A REVIEW THAT CANNOT CHANGE THE BUILD IT GATES IS A RECEIPT, NOT A REVIEW — AND CYCLE 58 REPEATED
      CYCLE 57'S VERSION OF THIS.** `archive/peer/2026-09-21-retrospective-cycle57.md` finding 5(a) caught it in
      cycle 57: `diag_s57_ctmove_wire.py` was written and AST-checked *before* the ctowner review that gated it was
      dispatched, and "was NOT changed afterwards", so $3.8922 and 546 s bought a review structurally unable to
      affect anything. Cycle 58 did the same with `diag_s58_boolwire.py` and `c58-boolwire-dangling` ($4.3192).
      **MANDATORY in every brief from now on: a review that GATES a build is dispatched BEFORE the script is
      written, or the brief says in writing that the script will be revised on the review's findings.** This is a
      brief sentence, not a device — the standing order of 2026-09-18 08:53 forbids the latter, not the former.
    - (n) ⚠️ **THE GATE CHAIN COST THIS CYCLE FOUR DRY RUNS AND AN $8.03 REVIEW, AND THE ORDERING IS THE FINDING.**
      `guard_cycle` refuses in sequence — `stop_record` → `violations --due` → `outcome_review --due` →
      `premature_build()` → the retrospective gate — and each refusal is visible only after the one before it is
      cleared, so a single launch was refused four times for four unrelated reasons (a stop record keyed to bytes
      that did not exist; two slugs at threshold; a heading written `01:5x` where `tools/violations.py:94` needs
      `\d{2}:\d{2}`; no prior-art review newer than the recipe). **Every refusal was answered on its own terms —
      no date rolled, no gate patched, `CYCLE_GUARD_OFF` never set** — and each answer was real work, not
      paperwork: the recipe got written, two threshold slugs got substantive decisions, three stale doc lines got
      repaired. The last refusal is the structural one: **the retrospective gate compares the newest BUILD LOG
      against the newest RETROSPECTIVE, so once a cycle has run any build log it cannot launch a recipe in that
      same cycle.** That is why S3a's combined build is cycle 59's first act and not cycle 58's last: clearing it
      mid-cycle would have meant running the retrospective early, which is the exact trap OPEN 54(a) documents and
      which cost cycle 29 its entire cycle.

## Pre-decided — ADDED 2026-09-21 (cycle 59): S3a IS DELIVERED as one file · S3b's transport DOES NOT EXIST and is built

49. **S3a IS ACCEPTED AND CLOSED, AND THE NEXT STAGE'S TRANSPORT WAS MEASURED TO BE ABSENT FROM THE WHOLE FLEET.**
    Judgement, cycle 59, 2026-09-21, from `tools/bench/cycle59_s3a_recipe.log` (`BGRUN END rc=0 after 596s`, **64
    gates pass / 0 fail**), a files-only verb census, and `archive/peer/2026-09-21-s3b-local-variable-route.md`.
    34–48 stand; this closes S3a and re-cuts S3b before any of it is built.
    - (a) 🎉 **S3a IS DELIVERED AS ONE FILE, AT THE STRUCTURAL LEVEL, AND THE RECIPE WAS NOT TOUCHED TO GET THERE.**
      `claudeDev\D1_s3a_focus_ind.vi`, md5 **`eef91c1d91f16b034707e4d1285ca8cb`**, 476,172 B, LV2026 `26 00 80 00`
      (`tools/bench/cycle59_s3a_recipe.log:322`). `ExecState` **1** at the B3 save (`:304`) **and 1 on the Z0 COLD
      reopen in a freshly restarted LabVIEW** (`:324`); **BOTH** ControlTerminals read `owner_of` `('Diagram',639)`
      on that cold reopen — numeric #23541 `'index'`, Boolean #23576 `'Automatic Error Handling'` (`:328`); census
      **116** (`:333`), i.e. 114 at the S2 baseline +1 per leg, which is the number the prior-art review said
      nothing on disk had produced; both ORDERED `Is Broken?` readings **False** — wire 10990 (`:147`) and wire
      10799 (`:311`). Six sub-step artefacts on disk, each saved at the last point the VI was measured legal
      (`:347`). Refs **60 opened / 60 closed / 0 live** (`:344`); all three originals byte-unchanged before AND
      after (`:340`). `tools/recipes/stage_d1_s3a_focus_ind.py` sha256 identical before and after —
      `1986626FB6F16CD0…`, the bytes the prior-art review saw, so the stop record still matches. No hook refused
      the launch, `CYCLE_GUARD_OFF` was never set, no gate was patched. **DECISION: S3a is CLOSED. Verification is
      STRUCTURAL and is never called functional — no VI was run (34(f)).**
    - (b) 🔴 **THE S3b TRANSPORT DOES NOT EXIST TODAY — MEASURED, NOT INFERRED, AND 45(f)'s ROUTE IS CLOSED AS
      WRITTEN.** `local` occurs **once** in `tools/gscript.py`, in a comment (`:830`): **no verb creates a Local
      Variable.** The only vehicle for `Control → Create:Local Variable` **6331C02** is `build_invoke`
      (`tools/gscript.py:2159`), whose `reference` input is **deliberately left UNWIRED** (`:2164-2166`: a wired
      reference makes the erdosmiller creator write the object's bare class name and fail silently). No `Op*.vi`
      in `claudeDev` (108 files) carries `Local` in its name, and `vi.lib\Erdos Miller\LV-Scripting\Create*.vi`
      is **50 files, none a local-variable creator**. `Local` is grep-absent from `docs/vi-server-ids.json`.
      Neither `docs/NAMES.md` nor `docs/toolkit-capabilities.md` records a creator in any state; the only rows are
      readers and the unverified wiki pair at `docs/NAMES.md:260`.
    - (c) ⚠️ **AND THE METHOD'S OWN SHAPE IS WHY `build_invoke` CANNOT BE THE VEHICLE.** The external fact
      dispatch (`archive/peer/2026-09-21-s3b-local-variable-route.md`, claude/fact fable-low thin +web, ANSWERED
      79 s, `$1.3397`) returns, CITED to labviewwiki, that `Create:Local Variable` **6331C02 takes NO input
      parameters** and returns only a Local refnum — so **the control instance the method is invoked on IS the
      binding**. Two established halves (a method with no parameters; a wrapper that never wires the reference)
      meet, and they do not meet in a place where anything can be addressed. Its further claims — that such a
      call returns error 1055, and that `New VI Object` style **2061** + a write to `Local.Control Name`
      **6355400** is the alternative — are the peer's own flagged INFERENCE, and its negative finding is that
      **no NI reference page exists for 6331C02, style 2061, or 6355400/6355401/6355403 at all**; wiki, LAVA and
      one 2013 forum thread are the only sources anywhere. **RECORDED, NEITHER ACCEPTED NOR REJECTED (41(b));
      nothing in it is acted on except (d)'s choice of which route is probed FIRST.**
    - (d) **DECISION: S3b GETS ONE NEW OP VI, AND THE AUTHORISATION IS 46(k), NOT A NEW USER DECISION.**
      `docs/cycle27-plan.md:31` is *"no further **process device**"*; `:1697-1705` already settled that this does
      not reach an op VI that places a Local Variable and that such an op *"is simply built"*. Shape, fixed here
      so no material session designs it: **`OpCreateLocal_v0.vi`** — in: VI ref, the control's owned LABEL, the
      destination diagram, a position; internals: `VI.Panel` → `Panel.Controls[]` **6348801**
      (`docs/vi-server-ids.json:47`, already the measured route inside `OpFPLabels_v0`) → per control
      `Control.Label` **6332005** (`docs/vi-server-ids.json:21`) → `Text.Text` → match the requested label → on
      **that live Control reference** Invoke `Create:Local Variable` **6331C02** with no parameters → read back
      the new object's uid, class and bound name; relocate afterwards only if the readback says it was not born
      on the destination diagram. Out: uid, class, bound label, the error cluster. **It closes every reference it
      opens** — reference hygiene is a precondition of a staged build, not an afterthought (CLAUDE.md), so the
      op's self-test includes 20 consecutive calls with the handle count flat ±100. **Why route A first and not
      the `New VI Object` 2061 route:** A is one call on a reference we already know how to obtain — it reuses
      `OpFPLabels_v0`'s measured `Panel.Controls[]` → `Control.Label` walk and adds one Invoke — whereas B needs
      TWO unverified IDs (a style constant from LAVA and a property write the wiki alone documents). B is the
      fallback, and the self-test REPORTS whether 2061 and 6355400 resolve on this machine as a measurement,
      never as a repair attempt. ⚠️ **AND THE SAME APPLIES TO ROUTE A's OWN PREMISE — added on the cycle-59
      retrospective's finding 3:** *"6331C02 takes no parameters"* comes from a wiki page that **self-declares
      its parameter table incomplete**, so if the method turns out to take parameters after all, that is a
      **MEASUREMENT L0 RECORDS, not a failure of the sub-step.** L0 is never scored against an assumption the
      sources never supported.
    - (e) **THE DECOMPOSITION — five sub-steps, five artefacts, five pass criteria, each starting from the
      previous FILE in a FRESH LabVIEW (the user's 2026-09-19 rule).** ⚠️ **The order INVERTS NEXT's sentence
      order deliberately (see (f)).**
      **S3b-L0** — build `OpCreateLocal_v0.vi` and self-test it on a **SCRATCH copy, never on
      `D1_s3a_focus_ind.vi`**: create one local bound to a named control, read back uid/class/bound label, 20
      consecutive calls, handles flat ±100. Pass: the local exists, bound to the label asked for, `ExecState` 1,
      refs 0 live. Artefacts: the op VI + its self-test log.
      **S3b-M1** from `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d…`), cold — create the TWO locals, one per new
      indicator (`'index'`, `'Automatic Error Handling'`), left UNWIRED → save
      `claudeDev\D1_s3b_m1_locals_<stamp>.vi`. Pass: `Local` census **8 → 10**
      (`docs/toolkit-capabilities.md:284` is the 8), both bound labels read off the machine, `ExecState` 1.
      ⚠️ **MEASURE, DO NOT ASSUME, whether an unwired Local leaves the VI legal.** If `ExecState` is 0 with the
      locals unwired there is no legal save point here, and M1 folds into M2 (create **and** wire in one step) —
      that is a fact the sub-step REPORTS; the folding is judgement's call on the next brief, not a branch a
      material session takes.
      **S3b-M2** from M1, cold — wire the two locals into `#10407` t0/t2 → save `…_m2_fed_<stamp>.vi`. Pass:
      `ExecState` 1, **`Is Broken?` False on both new wires** via the ordered second pass (42(b), after the save),
      `#10407` wired-terminal count **+2**, and `#637` terminal/wired counts **unchanged — no tunnel, no border
      object** (37(e)). **This is the step that closes the boundary cycle 54 died on.**
      **S3b-M3** from M2, cold — move the five 1.5 nodes into `#23032`'s body `Diagram #23058`
      (`docs/cycle27-plan.md:1127-1129`; ⚠️ `:1037`'s `Obtain Queue #23032` is a different object reusing the
      uid), ONE `move_in` per node, junk purged in-run, then re-wire the rows from the MEASURED table
      (`docs/cycle27-plan.md:1182-1188`, whose "sources on `#686` = 0" clause is STRUCK at `:1188`; cycle 54's
      9/9 at `:1283-1290`) → save `claudeDev\D1_s3b_m3_moved_<stamp>.vi`. Pass: all five `owner_of` = `#23058`
      AND `ExecState` 1.
      **S3b-M4** from M3, cold — frame-counter edge shift register + `Wait (ms)` 1 → save
      `claudeDev\D1_s3_loop15.vi`. Pass: `ExecState` 1 preloaded AND on a cold reopen. 38(g) stays banned.
    - (f) **WHY THE LOCALS COME BEFORE THE MOVES — a judgement call, recorded as one.** NEXT's sentence orders
      S3b as *move the five nodes, re-wire the rows, then feed `#10407` from locals*. Taken literally that puts
      the one step that BREAKS the VI first and the two independently-savable steps last, and cycle 54 already
      ran that order: 5/5 moves, 9/9 rows, **`ExecState` still 0**, no file (`:1283-1290`). Creating and wiring
      the locals first is savable at `ExecState` 1 twice over while the diagram is still in its known-good S3a
      shape, and it means M3 starts from a VI whose `#10407` inputs are ALREADY satisfied — which is precisely
      the boundary defect cycle 54 diagnosed. A failure in M3 then still leaves two new files and a closed
      boundary instead of nothing.
    - (g) **DECISION: THE TWO INHERITED LABELS STAY, AND NO RENAMER IS BUILT — but the user is told, because it
      is their panel.** The indicators carry `'index'` and `'Automatic Error Handling'`, the names LabVIEW derived
      from the carriers. **No verb in this fleet can rename a front-panel control or indicator** (measured,
      cycle 58: `set_node_label` writes `Node.Label` on `Diagram[d].Nodes[n]` and a `ControlTerminal` is not in
      `Nodes[]`; every other label path is a reader), so a rename means a SECOND new op against
      `Control.Label` 6332005. It buys nothing structural: a label is cosmetic, it changes no computation
      (rule 1a untouched), and local variables bind by label, so both names WORK — each is measured
      non-duplicate and newline-free. `'Automatic Error Handling'` on a tracking Boolean is nevertheless
      misleading to a human reading the panel, and renaming two labels by hand in the editor is seconds for the
      user against an op VI plus self-test for us. **Flagged in `## NEXT` as the user's to overturn; if they want
      us to do it, the `Control.Label` writer is a one-cycle build.**
    - (h) ⚠️ **THE RE-SPLIT TRIGGER FOR M3, STATED IN ADVANCE SO NOBODY HAS TO NOTICE IT.** If M3 ends at
      `ExecState` 0 — i.e. leaves NO file — the next cycle's FIRST act is M3's own decomposition, cut
      **node-with-its-rows** (each node moved and its severed rows re-wired before the next node is touched), and
      the tunnel question becomes explicit at that point rather than implicit. A full-length retry of M3 under a
      new file name is FORBIDDEN (the user's 2026-09-19 rule 3; `cycle_runner.py` counts renamed recipes as the
      same recipe).
    - (i) ⚠️ **48(m) IS SATISFIED BY CONSTRUCTION FOR L0, AND THAT IS THE POINT OF DOING IT THIS CYCLE.** The
      gating research for the op — the external API fact — was dispatched and archived BEFORE one line of the op
      exists, so the review cannot be a receipt for a script already written. Cost `$1.3397`. The brief that
      builds L0 must still say in writing that the op will be revised on any review that gates it.

## Pre-decided — ADDED 2026-09-21 (cycle 60): L0 RAN · the creator works · the binding has NO READER, so the reader is built

50. **S3b-L0 IS MEASURED. `OpCreateLocal_v0.vi` CREATES LOCALS RELIABLY; WHAT DOES NOT EXIST IS ANY WAY TO READ
    WHAT A LOCAL IS BOUND TO.** Judgement, cycle 60 (attempt 2), 2026-09-21, from
    `tools/bench/diag_s3b_l0_createlocal.log` (`BGRUN END rc=1 after 106s`, **30 pass / 2 fail**) and
    `archive/peer/2026-09-21-c60-l0-readback-none.md` (claude/hypothesis opus max, ANSWERED 504 s, `$4.3505`,
    disposed in full in its own `## What was done with it`). 34–49 stand; this settles L0 and re-cuts 49(e)'s M1.
    - (a) ⚠️ **CYCLE 60 ATTEMPT 1 WAS A USAGE-LIMIT NON-RESULT AT THE CYCLE LEVEL, BUT THE L0 RUN INSIDE IT IS A
      RESULT AND IS NOT RE-RUN.** The runner recorded *"usage-limit attempt 1, non-result; sleeping 238 min
      (renewal + 2 min) then RERUNNING this cycle"* (`tools/bench/cycle_runner_main_20260921a.log`, cycle 47 row,
      02:38:44 → 03:03:39). CLAUDE.md's usage-limit rule 3 invalidates a benchmark or build **interrupted
      mid-run**; L0 was not interrupted — it started 02:51:44 and ended on its own `BGRUN END` line 106 s later
      with a complete gate table, ~10 min before the limit was hit. **DECISION: L0's readings stand as
      measurements and no part of it is repeated.** What the limit cost was the cycle's remaining work and its
      retrospective, nothing else.
    - (b) 🎉 **THE CREATOR HALF OF 49(d) IS DELIVERED AND IS SOUND.** `claudeDev\OpCreateLocal_v0.vi`, md5
      `58275b212dfa040685613e3edbf403f2`, 9,688 B, LV2026 `26 00 80 00`, `ExecState` 1. Invoking
      `Create:Local Variable` **6331C02** on a live front-panel Control reference returned error cluster
      `(False, 0, '')` and a new `Local` (uid 23507, owner `('TopLevelDiagram',536)` — the normal birthplace,
      `docs/toolkit-capabilities.md:275`). **20 consecutive calls: 20/20 produced one new Local each, 0 errors,
      1.6 s, handle count 51,418 → 51,418 (delta 0), refs 12 opened / 12 closed / 0 live** — reference hygiene is
      met as a precondition, not an afterthought. The scratch was a copy of `D1_s3a_focus_ind.vi`, was never
      saved, and was deleted in the same run (`exists=False`); all four md5 gates on the originals PASSED before
      AND after. ⚠️ **AND 49(d)'s RIDER FIRED AS WRITTEN: the node has SIX terminals, not four** — `i=4`
      `'Create Local'` (sink) and `i=5` `'Create Local'` (source), both left unwired. That is a MEASUREMENT the
      run recorded, never a failure of the sub-step.
    - (c) 🔴 **THE TWO FAILING GATES ARE AN ABSENT INSTRUMENT, NOT A FAILED BINDING — AND THAT DISTINCTION IS THE
      WHOLE OF S3b.** `L0_b5` (`bound None`) and `L0_b6` (`None vs 'index'`) were read with `node_labels()`, which
      returns `Node.Label` **6359001** → the node's OWN label (`tools/gscript.py:588-594`). All **eight** of the
      main VI's pre-existing Locals return the VI's FILE NAME through that path
      (`tools/bench/main_vi_node_labels.json`; the two Globals likewise return `"Global motor pos.vi"`), so it can
      never answer "what is this Local bound to" for any Local, new or old. 🔴 **CORRECTED 2026-09-21 by the
      cycle-60 judgement session, on its own prior-art review: the sentence that followed here — *"the fleet's
      inability to read a binding is the blocker, so cycle 60's deliverable became the reader
      `OpLocalName_v0`"* — was WRONG, and wrong against an active document.** `gscript.node_terms`
      (`tools/gscript.py:870`) already reads it: a local-variable node's single terminal is **named after its
      bound control**, `is_source` giving READ vs WRITTEN — `docs/main-vi-panel-map.md:405`, with all eight
      bindings tabulated at `:401-416` since **2026-09-14** and re-verified in
      `tools/bench/main_vi_nodeterms.json`. What `node_labels` cannot do, `node_terms` can, and the whole
      `OpLocalName_v0` / `Local.Control Name` 6355400 build was unnecessary. The half of (c) that stands is the
      half about the INSTRUMENT ACTUALLY USED: `node_labels` returns the node's own label — the VI's file name for
      every Local and Global — so `L0_b5`/`L0_b6` did report an absent measurement, and the two FAILs were
      correctly raised. **Disposition and citations: `archive/peer/2026-09-21-priorart-c60-localname-decomposition.md`
      (`NOT novel`, 7 findings, all accepted).**
    - (d) **READING `Control Name` IS NOT "ROUTE B", AND 49(d) NEVER FENCED IT.** 49(d) fences route B as a
      *creation* mechanism — `New VI Object` style **2061** *plus a write* to `Local.Control Name`. A **read** of
      that property, to verify what route A actually produced, is a different act. Run 1 measured
      `Local.Control Name` **6355400 resolves = True, error `''`** (`tools/bench/diag_s3b_l0_createlocal.log:115`),
      which is what makes the reader buildable today; style **2061** was **not probed at all** because no verb in
      `tools/gscript.py` passes a style number (`:118-119`), so B remains unbuilt and unmeasured on its creation
      half.
    - (e) 🔴 **49(e)'s M1 FOLDS INTO M2 — the judgement call 49(e) reserved, made here on the measurement it asked
      for.** 49(e) said in advance: *"MEASURE, DO NOT ASSUME, whether an unwired Local leaves the VI legal … if
      `ExecState` is 0 there, M1 folds into M2, and that folding is the next judgement session's call."* L0
      measured it on this very VI lineage: the scratch copy of `D1_s3a_focus_ind.vi` read `ExecState` **1 before
      the call and 0 after it**, with one Local created and unwired. **DECISION: S3b-M1 and S3b-M2 become ONE
      sub-step — create BOTH locals (`'index'`, `'Automatic Error Handling'`) AND wire them into `#10407` t0/t2
      before the save.** Pass criteria are 49(e)'s M2 criteria plus `Local` census **8 → 10**: `ExecState` 1 at the
      save, `Is Broken?` **False** on both new wires via the ordered second pass (42(b), after the save), `#10407`
      wired-terminal count **+2**, `#637` terminal/wired counts **unchanged — no tunnel, no border object**
      (37(e)). ⚠️ **This does NOT weaken the user's 2026-09-19 rule**: the folded step still ends in a saved file,
      and it is the *first* point on this path where a legal save exists. M3 and M4 are unchanged, and **48(h)'s
      re-split trigger for M3 stands**.
    - (f) ⚠️ **ONE HALF OF THIS IS NOW SETTLED AND THE OTHER IS NOT.** Until the reader returns a string,
      **nobody may state that the new Local is bound to `'index'`** — that it must be, because 6331C02 is an
      instance method, is exactly the inference this cycle exists to replace. But the six-terminal question IS
      answered; see (g).
    - (g) 🎉 **THE SIX-TERMINAL QUESTION IS SETTLED BY MEASUREMENT, AND THE WIKI WAS RIGHT: 6331C02 TAKES NO INPUT
      PARAMETERS.** The separator the cycle-60 hypothesis review named was run report-only against Invoke nodes
      this fleet had already built with methods of KNOWN signature
      (`tools/bench/diag_s3b_l0_localname_run2.log:70-78`): `OpMoveIn_v0.vi` #741 — **12** terminals, pairs
      `(4,5) 'Move'`, `(6,7) 'position'`, `(8,9) 'owner'`, `(10,11) 'duplicate'`; `OpConPaneAssign_v0.vi` #99 —
      **10** terminals, `(4,5) 'AssignCtrlToTerm'`, `(6,7) 'Control'`, `(8,9) 'TermIdx'`; `OpCreateLocal_v0.vi`
      #306 — **6** terminals, `(4,5) 'Create Local'` **only**. The pattern is exact and it reads off two known
      signatures: the METHOD row occupies one (sink, source) pair named after the method, and **each parameter
      occupies one further pair**. `Create Local` has the method pair and nothing else. **DECISION: 49(d)'s rider
      is discharged — the `i=4` sink is layout, not an omitted input, and the wiki's incomplete parameter table
      happened to be right here.** Leaving both terminals unwired was correct, and no future run is scored against
      a missing 6331C02 parameter. (All three op VIs byte-unchanged by the reading.)
    - (h) **DECISION: THE READER IS BUILT WITH A `To More Specific Class` CAST SEEDED TO `Local`, FOLLOWING THE
      DONOR'S OWN MECHANISM — not a new technique, and not a donor substitution.** Cycle 60's first reader attempt
      measured the block to one cast: `build_property('VI Server:Local', [('6355400', False)])` **RESOLVES** on
      this machine — error column `''`, Property census 7→8, short name **`CtrlName`**, terminal i=4 SOURCE
      (`tools/bench/diag_s3b_l0_localname_run2.log:50-56`), the **first resolution of 6355400 here** — but wiring
      its `reference` straight from `Traverse for GObjects.vi` → `Index Array .element` gives `ExecState` **0**
      with the `CtrlName` row intact (no silent class re-adaptation, `:59-64`), because Traverse yields a
      **GObject** and `Local` sits two classes below it. `OpNodeLabels_v0.vi` already carries the answer:
      **`To More Specific Class` #683**, seeded by wire **772, produced by no node on its diagram** (`:29-45`).
      The reader reproduces that seed with target class `Local`. ⚠️ **The seed's construction is to be READ off the
      donor and reported verbatim — it has never been measured — and if it cannot be reproduced for class `Local`
      that is a FACT with an `OPEN:` line, never a donor substitution and never the alternative Invoke-seeded
      variant the review proposed.** Nothing on disk was lost to the first attempt: it saved no VI by design
      (`ExecState` 0, `allow_broken` False, `gui_save` never called), deleted its scratch, and left all four md5
      pins and both donors byte-unchanged.
    - (j) 🔴 **THE READER STAGE HAS NOW ENDED TWICE WITH NO FILE, SO IT IS RE-SPLIT — THE TRIGGER IS THE USER'S,
      NOT A FEELING.** Attempt 1 (`tools/bench/diag_s3b_l0_localname_run2.log`) and attempt 2
      (`tools/bench/diag_s3b_l0_localname_v2.log`, `BGRUN END rc=1 after 101s`, 29 pass / **1 fail** —
      `S2_b10 ExecState == 1 after the indicator`) both ended `ARTEFACTS ON DISK: []`. The user's 2026-09-19 rule
      3: *"the same stage failing twice at the same place, or a stage that ends without a saved artefact ⇒ the
      next cycle's FIRST act is a decomposition plan for that stage … A full-length retry under a new file name is
      forbidden."* **DECISION: no third full-length build. The decomposition is 51, written here so the next
      session executes instead of planning.** What the two attempts bought is real and is not lost: the property
      resolves, the cast route is built end to end with every error column `''`, and the fault is narrowed to
      three candidates — but **this cycle saved no VI, and that is its honest cost.**
    - (k) 🎉 **THE SEED MECHANISM IS NOW THE PLAN'S, CITED: `docs/toolkit-capabilities.md:84-93`, the typed-control
      seed, SOLVED 2026-09-14.** A refnum CONTROL created by `Terminal.Create Control` on a property node's
      `reference` input IS the seed for a `To More Specific Class`. It was on disk the whole time and attempt 2
      mis-cited its own file — the cycle-60 cast-seed review
      (`archive/peer/2026-09-21-c60-cast-seed-execstate0.md`, claude/hypothesis opus max, ANSWERED 643 s,
      `$4.8363`) refuted the diagnosis on exactly that ground, and it was right. It is CONFIRMED LIVE, not just
      cited: on `claudeDev\OpLoopCast_v0.vi`, `ExecState` **1**, the TMSC's `target class` is wire **333**, carried
      by a front-panel **control** `{'label':'reference','uid':297,'is_source':True}` with **0 node producers**
      (`tools/bench/diag_c60_castseed_probe.log:50`). The donor `OpNodeLabels_v0`'s own seed (wire **772**, 0 node
      producers, 0 of 19 `panel_wiring` rows — `diag_s3b_l0_localname_v2.log:46-69`) is the same shape read
      through an instrument that cannot see it. ⚠️ **`gscript.loop_cast` (`tools/gscript.py:626`) CANNOT be used
      here** — it dispatches only to `OpLoopCast_v0/v1` and `OpWhileCast_v0` and raises otherwise;
      `OpLocalCast_v0.vi` does not exist, so the TMSC is hand-built.
    - (l) **WHAT IS MEASURED OUT, so 51 does not re-test it.** The `ExecState` timeline was
      `1 → 0 after build_property → 1 after the seed control → 0 after the birth-wire delete → 0 thereafter`
      (`diag_s3b_l0_localname_v2.log:83-126`). The middle two transitions are the property node's `reference`
      input going unwired → wired → unwired, which is ordinary. **Step b7 is EXONERATED by an isolated probe on a
      throwaway donor copy: `ExecState` 1 → 0 (wire 645 deleted) → **1** again after `create_control` on
      `#235.reference` (`tools/bench/diag_c60_castseed_probe.log:74-80`, 19 pass / 0 fail, 3 s).** So the residual
      0 is one of exactly three things: **wire 1030** (the Local-typed seed into `target class`), **wire
      1085/#1025** (the cast output into the `VI Server:Local` node), or **no structural break at all**.
    - (i) ⚠️ **AND THE READER IS NOT OPTIONAL BOOKKEEPING — IT IS A RULE-1a INSTRUMENT.** S3b feeds `#10407`
      t0/t2 from two Local Variables. If the creator's label walk ever matched the wrong control, loop 1.5 would
      be fed from the wrong source with no wire broken and no gate failing — *"parameters must arrive by the same
      route with the same values"* (CLAUDE.md 1a), and a same-type mis-binding is invisible to `Is Broken?`, which
      checks TYPE. The panel carries many numerics, so type alone does not fence `'index'`. **DECISION: the folded
      M1+M2 step does not run until the binding can be READ, and the readback of both locals' `Control Name` is a
      GATE of that step, not a diagnostic afterthought.**

## Pre-decided — ADDED 2026-09-21 (cycle 60): the DECOMPOSITION of the binding reader, four steps, four artefacts

51. 🔴 **WRITTEN, PRIOR-ART-REVIEWED, AND THEN CUT DOWN TO ONE STEP BY THAT REVIEW — ALL IN THE SAME CYCLE. READ
    (f) FIRST; (a)–(d) ARE THE RECORD OF WHAT WAS PLANNED, NOT INSTRUCTIONS.** The re-split 50(j) triggered and
    `OpLocalName_v0` was cut into four sub-steps below, each with its own saved file and pass criterion, as the
    user's 2026-09-19 rule 3 demands. That rule also says the decomposition is **prior-art-reviewed once, then
    executed** — the review ran (`archive/peer/2026-09-21-priorart-c60-localname-decomposition.md`, `NOT novel`,
    7 findings, `$8.6086`, all accepted and disposed) and found the instrument already built. **L1, L2 and L3 and
    the whole `OpLocalName_v0` / TMSC / `Local.Control Name` route are WITHDRAWN before a line of them ran. Only
    L4's question survives, and it is now a READ — see (f).** A full-length retry of the v2 cast build under any
    new name remains FORBIDDEN.
    - (a) **L1 — READ WHICH CONNECTION IS BROKEN. No build, no save, ~3 minutes of machine time.** On a throwaway
      copy of `OpNodeLabels_v0.vi`, rebuild to the exact point attempt 2 reached (property `CtrlName` → seed
      control from the `reference` SINK → birth wire deleted → seed wired into `target class` → cast output wired
      into `reference`), then run the **ORDERED second pass** (42(b)) and read **`Is Broken?` on BOTH** the seed
      wire and the cast-output wire, plus `#1025`'s full terminal table. ⚠️ **Resolve both wires by CONSTRUCTION
      ORDER, never by the literal uids 1030 / 1085** — they will differ on a fresh build, and reusing a remembered
      number is the mistake `diag_s3b_l0_createlocal.py:608` already made once. The `Is Broken?` read perturbs
      `ExecState` (`docs/NAMES.md:912-918`); that costs nothing here because `ExecState` is already 0 and nothing
      is being saved. **Pass: a True/False reading for BOTH wires.** A `False`/`False` pair is a legitimate and
      informative outcome — it would mean 50(l)'s third candidate, *no structural break at all*, and the next
      step becomes a save attempt rather than a repair. **Artefact: `tools/bench/diag_c60_l1_whichwire.{log,json}`.**
    - (b) **L2 — REPAIR THE ONE CONNECTION L1 NAMES, AND SAVE.** Build the same chain with that one connection
      made differently, and **save `claudeDev\OpLocalName_v0.vi` at `ExecState` 1**. **Pass: `ExecState` 1 at the
      save AND on a COLD reopen in a freshly restarted LabVIEW.** **Artefact: the op VI + its md5.** If `ExecState`
      is still 0 here, STOP — do not try a third construction; report which connection was changed and what the
      reading was, and let judgement cut again (50(j) applies to this step in its own right).
    - (c) **L3 — VALIDATE THE INSTRUMENT AGAINST GROUND TRUTH BEFORE ANYONE BELIEVES IT.** On a **SCRATCH copy**
      of `claudeDev\D1_s3a_focus_ind.vi` (md5 `eef91c1d…`), never the artefact, read `Control Name` for **every**
      pre-existing `Local` (census 8, `docs/toolkit-capabilities.md:284`) and report **every uid → string pair
      verbatim**. **Pass: at least one non-empty string that is NOT a `.vi` file name** — that is the whole point,
      since `node_labels` returns the file name for all eight (50(c)). **Artefact: the readings JSON.** A run of
      eight `.vi` file names or eight empty strings means 6355400 is not the binding either, which is a result and
      must be reported as one.
    - (d) **L4 — ANSWER THE QUESTION THE WHOLE CYCLE WAS FOR.** On the same scratch, create a Local with
      `OpCreateLocal_v0.vi` from the front-panel control whose owned label reads `'index'` (**read the label off
      the machine, never retype it**), then read its `Control Name`. Report the string verbatim, the error
      cluster, `Local` census 8 → 9, and `ExecState` before and after. Then 20 consecutive reader calls, **handles
      flat ±100, refs opened == closed, 0 live**, scratch deleted with `exists=False`. **Pass: a string is
      returned and the hygiene numbers hold** — whatever the string SAYS is the measurement, and a name other than
      `'index'` is a finding, not a failure.
    - (e) **THEN, AND ONLY THEN, S3b's FOLDED M1+M2 (50(e)) RUNS, WITH THE READBACK AS A GATE (50(i)).** If L3 or
      L4 shows that the binding cannot be read at all, the folded step does **not** silently proceed on type
      checking alone — that is a rule-1a call and it returns to judgement.
    - (f) 🎉 **WHAT 51 ACTUALLY IS, AFTER THE REVIEW: ONE READ, NO BUILD — `node_terms`.** `gscript.node_terms`
      (`tools/gscript.py:870`) and `node_terms_uid` (`:925`) read a Local's binding directly, because the node's
      single terminal is **named after its bound control** and `is_source` gives READ vs WRITTEN
      (`docs/main-vi-panel-map.md:405`; all eight bindings tabulated `:401-416`, re-verified in
      `tools/bench/main_vi_nodeterms.json`; rule restated `docs/NAMES.md:335`). **N1** re-reads those eight live on
      a scratch copy rather than trusting a table dated 2026-09-14; **N2/N3** create one Local each from the
      controls labelled `'index'` and `'Automatic Error Handling'` with `OpCreateLocal_v0.vi` and read the new
      nodes' terminal names — the one thing L0 never did, having made 21 Locals without once calling `node_terms`;
      **N4** is hygiene (20 calls, handles flat ±100, refs 0 live, scratch deleted). Artefact:
      `tools/bench/diag_c60_n4_localbinding.{log,json}`. **Nothing is built and no VI is saved.**
    - (g) ⚠️ **THE FALLBACK, KEPT ALIVE DELIBERATELY, BECAUSE THE TERMINAL-NAME RULE IS AN OBSERVATION AND NOT AN
      NI CONTRACT.** The review says so in as many words — n = 8 Locals + 7 Globals, 0 counterexamples — while
      `Local.Control Name` **6355400** is the authoritative property and is now MEASURED to resolve here
      (`tools/bench/diag_s3b_l0_localname_run2.log:50-56`, short name `CtrlName`, i=4 SOURCE). **If N2/N3 return a
      terminal name that is not the control asked for, or an empty one, the 6355400 route returns as the
      FALLBACK** — and then it is built **additively on a donor** (never spliced into an existing op, per (h)),
      seeded by the ordered recipe `tools/recipes/build_oploopcast_v0.py:12-27`, and as its **own** cast op, never
      by re-plumbing `OpNodeLabels_v0`'s `#683`, which that donor needs for its own `Diagram` cast
      (`docs/toolkit-capabilities.md:93-94`: *"a seed casts exactly its class … one op per concrete class"*).
    - (h2) 🎉 **51(f) RAN AND THE BINDING QUESTION IS ANSWERED — 27 gates pass / 0 fail, nothing built, nothing
      saved** (`tools/bench/diag_c60_n4_localbinding.log`, `BGRUN END rc=0 after 93s`; readings
      `…_n4_localbinding.json`).
      **N1 — the instrument is validated LIVE, not trusted from a table.** `node_terms` on all eight pre-existing
      `Local`s returned exactly ONE named terminal each, and the set is **IDENTICAL** to
      `docs/main-vi-panel-map.md:409-416` — 8/8 agree, 0 differ (`:27-45`): #2991 `'Total Lost Frames'` ·
      #4277 `'File # Saved'` · #11574 `'Focus Pos (Track)'` · #3160 `'Rot pos (deg)'` · #3097 `'Trans Pos (mm)'` ·
      #2143 `'Total Lost Frames'` · #16942 `'Picture'` · #25805 `'Color table'`.
      🎉 **N2/N3 — `OpCreateLocal_v0` BINDS TO THE CONTROL IT IS INVOKED ON, AND THAT IS NOW A MEASUREMENT.**
      From `'index'` (`Panel.Controls[114]`, label read off the machine): new Local **#23574**, error cluster
      `(False, 0, '')`, census 8 → 9, ONE terminal named **`'index'`** (hex `696e646578`). From
      `'Automatic Error Handling'` (`[115]`): new Local **#23579**, ONE terminal named **`'Automatic Error
      Handling'`**, census 9 → 10. `matches_the_label_asked_for: True` for both. **The instance-method inference
      49(c) rested on is retired — S3b's rule-1a instrument exists and it says the walk matched correctly.**
      **And L0's two FAILs are now fully explained by measurement:** the new Local's own `Node.Label` reads
      `'SCRATCH_C60N4_20260921_082820.vi'` (`:121`) — the VI file name, exactly as 50(c) said of `node_labels`.
      Hygiene: 20 consecutive `node_terms` calls in 1.1 s, handles 51,342 → 51,345 (delta **3**), refs 8/8/**0
      live**, scratch deleted `exists=False`, four md5 pins PASS before and after, `ARTEFACTS ON DISK: []` by
      design.
    - (h3) 🔴 **THE ONE NEW BLOCKER, AND IT IS THE NEXT CYCLE'S FIRST QUESTION: A NEWLY CREATED LOCAL IS BORN IN
      *WRITE* MODE, AND S3b NEEDS *READ*.** Both new Locals read **`is_source` False**, which
      `docs/main-vi-panel-map.md:405` defines as **WRITTEN** (`is_source` True = READ), with `wire` 0 — a bare
      sink. Of the eight pre-existing Locals, **3 are READ** (#3160, #3097, #25805) **and 5 are WRITE**, so both
      modes exist on this VI and the mode is READABLE. **Flipping one is UNMEASURED.** S3b's folded M1+M2 feeds
      `#10407` t0/t2 *from* the locals — a local that supplies a value must be in READ mode — so unless the
      direction can be set, the locals cannot serve their purpose however correctly they are bound. ⚠️ **Two
      things to establish before anything is built, in this order: (1) confirm the required direction against the
      MEASURED row table (`docs/cycle27-plan.md:1182-1188`, cycle 54's 9/9 at `:1283-1290`) rather than from this
      paragraph's reasoning; (2) measure whether the direction can be written at all.** The candidate property is
      **6355401** (the prior-art review's B1 notes `is_source` supplies what 6355401 would have read) on class
      `'VI Server:Local'`, which is measured to resolve here (`diag_s3b_l0_localname_run2.log:50-56`);
      `build_property`'s per-ID tuple already carries a writable flag. **Any op that follows is built ADDITIVELY
      ON A DONOR (h), never spliced, and it is one step with one saved artefact.**
    - (h4) ⚠️ **ONE STALE COLUMN, REPORTED AND DELIBERATELY NOT REPAIRED.** `docs/main-vi-panel-map.md`'s DIAGRAM
      indices no longer address this lineage — 73→76, 83→86, 99→102, 167→170 (1 and 17 unmoved); the **names and
      directions are unmoved**, so the binding table stands. Diagram indices are resolved **by uid via
      `diag_index`** everywhere anyway, which is why this cost nothing.
    - (h) 🔴 **A STANDING LESSON THE NEXT BUILDER READS BEFORE TOUCHING AN OP: DO NOT SPLICE A PROPERTY CHAIN INTO
      AN EXISTING OP — ADD TO A DONOR.** Counted by the prior-art review across the project's own logs: splicing
      has failed **6 times and succeeded 0** (S0 ×4 — Pre-decided 25, `tools/bench/build_s0_closeref_v3.log` 87/5,
      `…v1.log` 41/2; L0 ×2 — `tools/bench/diag_s3b_l0_localname_run2.log`, `…_v2.log`), while
      additive-on-a-donor has shipped **five** saved ops (`docs/toolkit-capabilities.md:62,:63,:66,:68,:70`). Both
      of cycle 60's dead builds are instances of the failing class. This is not a device and needs no gate — it is
      the sentence to read before the next op is designed.

## Pre-decided — ADDED 2026-09-21 (cycle 61): the direction is READ · the wrapper was the blocker · the op is SAVED

52. 🎉 **S3b's DIRECTION QUESTION IS CLOSED, AND IT IS CLOSED BY A SAVED INSTRUMENT: `OpCreateLocalRead_v0.vi`
    CREATES A LOCAL ALREADY IN THE RIGHT MODE.** Judgement, cycle 61, 2026-09-21, from
    `tools/bench/diag_c61_localdir.log` (32/0), `tools/bench/diag_c61_localdir_write.log` (38/1) and
    `tools/bench/diag_c61_localdir_write2.log` (38/0, `BGRUN END rc=0 after 169s`). 34–51 stand; this answers
    51(h3) in both its parts and re-cuts 50(e)'s pass criteria — see (h).
    - (a) **THE REQUIRED DIRECTION IS `READ`, TAKEN OFF THE MEASURED TABLES AS 51(h3) DEMANDED, NOT OFF PROSE.**
      `#10407` **t0**: `is_source` **False** (SINK), c53 `source_or_sink` "sink", wire **10799**, action
      `cross-loop:1.2->1.5`, far end `#10686` t0 `'x .and. y?'` `is_source` **True**. `#10407` **t2**: SINK,
      wire **10990**, far end `#10757` t1 `'element'` **True**. `c53_row_class.json`, the rewire JSON and
      `main_vi_nodeterms.json` agree on both rows, on the flags AND on the wires
      (`tools/bench/diag_c61_localdir.log:8-18`). Both sinks are fed from sources ⇒ **a Local taking over either
      feed must be a SOURCE at its own terminal = READ** (`docs/main-vi-panel-map.md:405`). No document
      disagreed. A newly created Local is born WRITE (51(h3)), so the mode must be set.
    - (b) **`Local.Write?` 6355401 EXISTS AND IS RESOLVED HERE FOR THE FIRST TIME** — class `'VI Server:Local'`,
      short name **`Write?`**, Boolean, terminal i=4: a **SINK** when the item is created write-mode, a SOURCE
      when read-mode (`diag_c61_localdir.log:84-101`). The ID had been carried as
      *"peer, UNVERIFIED"* since `tools/bench/diag_s56_transport2.py:91`; it is now measured.
    - (c) 🔴 **THE BLOCKER WAS OUR OWN WRAPPER, NOT LABVIEW — AND IT WOULD HAVE REFUSED EVERY WRITE THIS PROJECT
      EVER ATTEMPTS.** `build_property` asserted `Outputs count == items requested`; a write-mode item is an
      **input**, so it can never appear in Outputs, and the call raised
      *"creator error clean but Outputs count 0 != 1 requested - inconsistent, not trusted"* **while LabVIEW
      created the node correctly** — identically for the known-good 6355400, which is what proved the fault was
      mode-blindness and not the ID. **REPAIRED, narrowly and mode-aware** (`tools/gscript.py`, `build_property`
      only, +37/−2): read-mode items still assert against Outputs exactly as before; write-mode items assert
      against the node's non-standard **SINKS**. Self-test 5/5 — write 6355401 and 6355400 both yield the SINK
      row, read yields the SOURCE row, and the `VI Server:VI` 242 regression is unchanged
      (`diag_c61_localdir_write.log:28-97`). No other function touched, no verb added.
    - (d) 🎉 **NO `To More Specific Class` IS NEEDED ON THIS ROUTE — the cast that ended BOTH of cycle 60's builds
      is out of the path.** `Create:Local Variable` **6331C02**'s `i=5 'Create Local'` **SOURCE** wires straight
      into a `'VI Server:Local'` property node's `reference` SINK: error column `''`, and the ORDERED pass reads
      **`Is Broken?` False** on that wire (`diag_c61_localdir_write2.log`, wire 390). **50(g) is amended**: for
      `Create Local` the SOURCE half of the method pair carries the created object's reference, so the pair is not
      always layout. The seed problem 50(k) solved stays solved but is not needed here.
    - (e) 🎉 **THE ARTEFACT: `claudeDev\OpCreateLocalRead_v0.vi`, md5 `f695d97a36ae127cd2dd3ca6b1fc1089`,
      10,192 B, LV2026 `26 00 80 00`.** Built **additively on donor `OpCreateLocal_v0.vi`** (md5 `58275b21…`,
      byte-unchanged — 51(h)'s rule, and the first op to ship under it since it was written): property node #339
      write-mode, `reference` from Invoke #306 i=5, `create_control` on the `Write?` SINK → ControlTerminal #434
      labelled `'Write?'` (label read off the machine). `ExecState` **1 at the save and 1 COLD in a freshly
      restarted LabVIEW**. **Exercised on a scratch of `D1_s3a_focus_ind.vi`:** `Write?`=False → new Local bound
      to `'index'` (hex `696e646578`), `is_source` **True = READ**; `Write?`=True → `'index'`, **False = WRITE**;
      both error clusters `(False, 0, '')`, census 8→9→10. **The Boolean steers the mode** — that is the whole
      instrument S3b needed. Hygiene: 20 consecutive calls 0.9 s, handles +4, refs 26/26/**0 live**.
    - (f) ⚠️ **WHY THE FIRST BUILD OF THE SAME CHAIN FAILED, AND THE STANDING RULE IT RESTATES.** The `ExecState`
      1→0 after `build_property` is **transient and ordinary**: a write-mode property node with a bare `Write?`
      SINK is broken, and feeding that sink restores 1 (measured either side in
      `diag_c61_localdir_write2.log:23-63`). What made dispatch #2 stop was that it read `Is Broken?` **above**
      its save point, and that read perturbs `ExecState` (`docs/NAMES.md:912-918`). **STANDING: no `Is Broken?`
      is read above a save — the ordered pass runs AFTER the save, and preferably after a cold reopen**, which is
      what 42(b) already said and what `tools/recipes/stage_d1_s3a_focus_ind.py` passed 64/0 doing. The forced
      hypothesis review `archive/peer/2026-09-21-c61-localpn-execstate0.md` (claude/hypothesis opus max,
      ANSWERED 340 s, `$2.9786`) is **disposed in full in its own `## What was done with it`**: accepted on its
      central point and on the 242 confound, its perturbation sub-claim recorded as holding only for the later
      readings, its P1/P2 probes deliberately not run.
    - (g) **THE OPEN DISPATCH #3 RAISED IS ANSWERED AND NOTHING IS OWED.** The direction wire (ControlTerminal
      #434 → the `Write?` SINK, wire 462) has no `Is Broken?` route in this fleet, because the reader addresses a
      wire's source as a `Nodes[]` position and this source is a panel object. **DECISION: no reader is built and
      none is needed.** `ExecState` **1 on a COLD reopen is a statement about every wire in the VI**, strictly
      stronger than one wire's flag, and the op's two calls returned *different measured directions* — functional
      evidence a wire check cannot give. The gap is recorded, not filled.
    - (h) 🔴 **THE NEXT BLOCKER, SURFACED BY (a), NOT YET MEASURED, AND IT RE-CUTS 50(e): `#10407` t0/t2 ARE NOT
      BARE.** 50(e)'s criterion *"`#10407` wired-terminal count **+2**"* presumes two empty sinks. The machine
      says t0 carries wire **10799** and t2 wire **10990** — **the same two uids STATUS records for S3a's two
      indicator wires**, which means S3a most likely BRANCHED the existing cross-loop wires rather than creating
      new ones. ⚠️ **That last step is an INFERENCE from coinciding uids and it is the next cycle's FIRST
      measurement, not a fact to build on.** It matters because S3b exists to *replace* those feeds: if one Wire
      object carries both the indicator branch and the `#10407` sink, the sink must be freed without destroying
      the indicator's feed, and no verb here is measured to remove a single **branch** —
      `delete_object(target,'Wire',idx)` deletes the whole Wire object. **DECISION: 50(e)'s folded M1+M2 does NOT
      run until that is measured**, and its pass criteria are re-cut by judgement on the reading. Everything else
      in 50(e) stands (census 8→10, the `node_terms` readback as a rule-1a GATE per 50(i), `ExecState` 1 at the
      save, ordered `Is Broken?` after it, `#637` counts unchanged).
