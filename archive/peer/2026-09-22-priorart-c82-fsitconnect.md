# priorart-c82-fsitconnect

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.8719  in 44 / out 36606 / cache-create 219972 / cache-read 3513683  (532s, 34 turn(s))
- **date:** 2026-09-22 12:27:24
- **outcome:** ANSWERED (535s)
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
# D-2 of M3a-3b ??build, SAVE and EXERCISE `OpFsInnerTunnelConnect_v0.vi`

Recipe under review: `tools/recipes/build_opfsinnertunnelconnect_v0.py`
Decision already taken by the judgement session: `docs/cycle27-plan.md` Pre-decided 127 (with 124/125/126
for why). The CHOICE of op is NOT open in this dispatch; what is open is whether any of the work below has
already been done, measured or refuted in this project's own files.

## What is being built

`OpFsInnerTunnelConnect_v0.vi` in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`,
as the SMALLEST possible edit of the existing `OpConnectFromWire_v0.vi`:

* **Only the source-half acquisition changes.** Where `OpConnectFromWire_v0` derives a terminal from
  (`wire_uid`, `Wire.Terms[]` 6371003, index), the new op derives it from
  (`fsit_uid` ??`UID to GObject Reference.vi` ??`To More Specific Class` seeded
  `VI Server:FlatSequenceInnerTunnel` ??**`Left Terminal` 1C3A9000** = the `LeftTerm` output).
  That is the reading half of `OpFsInnerTunnelTerm_v0.vi`, already on disk and already measured
  (Pre-decided 109/118).
* **Everything else keeps its role exactly.** The Invoke still carries `Terminal.Connect Wire` 6349C03,
  still sits on the terminal named by the (diagram index, `Nodes[]` index, `Terminals[]` index) TRIPLE,
  and still receives the other terminal as `Wire Source` ??the binding the machine already accepted
  (`tools/bench/c80_rowd_routeA_r2.log:244`, Pre-decided 119).
* **LEFT terminal only.** No side selector, no second property, no extra inputs beyond `fsit_uid` +
  the index triple + the house error/status convention the sibling ops use.
* **One addition beyond the swap:** a `VI Server:GObject` + `632A813` (`GObject.UID`) property node
  branched off `LeftTerm`, with an indicator. Pre-decided 125 makes the uid echo a RULE for every
  uid-addressed op (`diag_c81_uidref.log:85`: a never-allocated uid returned a DIFFERENT previously
  resolved object with every error column empty), and Pre-decided 127's gate (3) asks for that value.

## The build steps (each one a named gate in the recipe)

B0 donor `OpConnectFromWire_v0.vi` on disk at `ExecState` 1, md5 recorded (never written).
B1 copy ??the new op; the source ladder found BY WIRE TOPOLOGY from the Invoke's `Wire Source`
   (Invoke ??Index Array ??`Wire.Terms[]` PN ??TMSC ??`UID to GObject Reference.vi`), never by uid;
   a stale-in-memory guard asserts the copy carries none of this build's own additions.
B2 delete the Invoke's `Wire Source` net; that terminal reads 0.
B3 delete the Index Array and the `Wire.Terms[]` property node; the TMSC's `target class` and
   `specific class reference` both read 0.
B4 `build_property("VI Server:FlatSequenceInnerTunnel", 1C3A9000)` ??one node whose single data output
   is read back and must be `LeftTerm`.
B5 `create_control` on that node's `reference` ??exactly ONE new control = the FSIT-typed SEED; its own
   wire deleted; the seed re-wired to the TMSC's `target class` (the shape
   `build_opfstunnelterm_v2.py:617-636` uses).
B6/B7 TMSC `specific class reference` ??the FSIT node's `reference`; `LeftTerm` ??the Invoke's
   `Wire Source`.
B8 `build_property("VI Server:GObject", 632A813)`; `LeftTerm` BRANCHED into its `reference`; an
   indicator on its `UID` output and one on each new `error out`.
B9 auto error handling OFF; `ExecState` 1; `save()` by script; labels JSON; donor md5 unchanged.

## Acceptance ??all four, each printing the value it compared (Pre-decided 127)

1. `ExecState` 1 on the SAVED op, re-read after the save.
2. **20 consecutive calls leave LabVIEW's handle count flat 짹100** (CLAUDE.md reference hygiene), on a
   dated scratch copy of the bed.
3. A call with `fsit_uid` 7468 returns the LeftTerm reference whose OWN uid echoes **#7488**.
4. ONE end-to-end exercise on a DATED SCRATCH COPY of the bed
   `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 `33ef524e??, 306,951 B): delete wire **7506**; call
   the op with `fsit_uid` 7468 and the index triple for the NEW loop's shift-register OUTER terminal
   (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, resolved LIVE with a uid echo); then assert with
   `OpWireSource_v5` that the net's SOURCE TERMINAL OWNER is **`RightShiftRegister #23868`** and that
   **`#4334` is OFF the net**, PD85 violations 0, `Wire.Is Broken?` False. Owner identity decides ??
   never a wire count, never a wire delta (Pre-decided 117 as corrected by 120). Scratch deleted,
   nothing saved from it.

## Constraints this recipe operates under

* The bed is READ-ONLY: md5-pinned at entry AND exit, never opened for execution.
* Rig state 議곕┰: no motor, no ASI, no camera. VI Scripting and COM only.
* LabVIEW restarted before the batch; handles reported before/after; refs opened/closed/live reported.
* One `bgrun` for the whole thing; files patched with Edit/Write, never a heredoc.
* A failed gate is the dispatch's result: no improvised second route, no variant op.

## What the reviewer is asked

Has any of this already been built, measured or refuted in this project's own files ??in particular:
an op that reaches a `FlatSequenceInnerTunnel` terminal AND writes a wire; a `Terminal`-seeded or
`FlatSequenceInnerTunnel`-seeded connect; a uid-echo indicator on a connect-class op; or a measurement
that says this swap cannot work? Cite `file:line`.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-20
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this. Narrative ??**`archive/2026-09-19-status-cycle47-relocate.md` (latest ??T2's block diff and what it closes, the readable-ORIGINAL correction, the five killed retrospectives)** + `archive/2026-09-19-status-cycle39-judgement.md` + `archive/2026-09-18-status-cycle34-n1.md` + `??cycle23-close.md` + the `archive/2026-09-1[678]-status-*.md` set.
??**DELIVERED:** D0 (cycle 31) 쨌 N1 ACCEPTED (cycle 34) 쨌 D1 **S1** `claudeDev\D1_s1_copy.vi` md5 `3e3d23ce?? 쨌 D1 **S2** `claudeDev\D1_s2_loops.vi` md5 `6ff19497?? 쨌 D1 **S3a** both halves (`??boolcarrier_b3_20260921_010034.vi` md5 `dc14dd00??, `ExecState` 1, `Is Broken?` False) 쨌 D1 **S3b rows 1 and 2**. ?뵷 **THE CURRENT BED IS `claudeDev\D1_s3b_row2_20260921_160311.vi`, md5 `26c54ff7??** ??every next stage starts FROM THAT FILE. ??**M3a-1 DELIVERED (cycle-63 firefighter, run 5, 2026-09-22 01:0x): `claudeDev\D1_s3b_m3a_BROKEN_20260922_005732.vi` md5 `6b3c1f3c??, 22 gates pass / 0 fail, bytes DIFFER from the bed.** ??**M3a-2 DELIVERED AND INDEPENDENTLY VERIFIED (cycle 64, 2026-09-22 02:3x??2:5x): `claudeDev\D1_s3b_m3a2_20260922_023029.vi` md5 `3842f5e6f128226235dc78353f26ef44`, 303,823 B, 25 gates pass / 0 fail on the build and 15/0 on a separate read-only check anchored at the REGISTER UID. ?뵷 EVERY NEXT STAGE STARTS FROM THAT FILE.** ?뵶 **M3a-3b (ROW D) IS **NOT** DELIVERED ??NO FILE, and deliberately so: the recipe is re-cut and astcheck-clean but its W1 gate measures that NO writer on disk can address a `FlatSequenceInnerTunnel` terminal sink (`tools/bench/c78_rowd_writer.log`). THE BED IS STILL `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e??, 306,951 B.** Both initial-value rows land the predicted source (`FlatSequenceInnerTunnel #4194` ??LEFT `#23880`; `#3974` ??LEFT `#23909`), the originals stay on their nets, `Wire.Is Broken?` False in a separate ordered pass, PD85 violations 0 on every walk. Still BROKEN BY DESIGN and NEVER RUN (34(f)); `ExecState` 0's cause is formally OPEN and is neither gated on nor reasoned from. The artefact is BROKEN BY DESIGN (uninitialised SRs ??initial values are stage M3a-2) and is NEVER RUN (34(f)). Two root causes were repaired and MEASURED on the way: the identity reader `wire_source_owner` (history-echo, now error-checked + uid-echo-verified, acceptance `diag_c68_echo_accept.log` 8/0) and `gscript._lv_gui` (unquoted spaced args = PowerShell parse error, so NO Evidence-carrying GUI action had EVER dispatched ??`archive/peer/2026-09-22-c72-guisave-foreground-r2.md`). The bed is byte-unchanged and all four md5 pins hold. S3-as-37(g)-defined is WITHDRAWN (cycle 53). **Read `docs/cycle27-plan.md` Pre-decided 84??0 BEFORE 78??3 (78/80/81/82 are WITHDRAWN)**, then 46, 42, 43, 44. Full chronicle VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠2; banner VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠3; facts `??cycle31-d0-delivered.md` 짠1?벬? (read **짠4** before the first D1 click).
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
  owner: cycle-82 material (D-2 of M3a-3b, Pre-decided 127)
  since: 2026-09-22 12:5x
  purpose: ?뵷 **RUNNING NOW ??D-2: build, SAVE and EXERCISE `OpFsInnerTunnelConnect_v0.vi`** (`tools/recipes/build_opfsinnertunnelconnect_v0.py` ??`tools/bench/build_opfsinnertunnelconnect_v0.log`). LabVIEW restarted at phase [1]; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is md5-pinned at entry AND exit and is NEVER opened for execution; two dated scratch copies (`C82SCRATCH_H_*`, `C82SCRATCH_E_*`) are created and deleted in the same run. No motor, no ASI, no camera. PREVIOUS PURPOSE, unchanged and still true ???윟 **CYCLE-81 MATERIAL, D-1 OF M3a-3b IS MEASURED AND THE ANSWER IS YES ??NOTHING WAS BUILT, NOTHING SAVED, NOTHING MUTATED** (Pre-decided 121/122; read-only on dated scratch COPIES, both deleted in their own run). Two runs, `tools/bench/diag_c81_uidref.log` (7/0, rc=0, 125 s) and `tools/bench/diag_c81_uidref_r2.log` (7/0, rc=0, 126 s); bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? byte-unchanged at BOTH ends of BOTH runs, all five pins hold, `THE FILES THIS RUN LEFT ON DISK: []`, refs 3/3/0 live, handles 33,986 ??33,972 (restart) ??33,967 at exit. LabVIEW 2026 **26.3.1f1**, 64-bit, `C:\Program Files\National Instruments\LabVIEW 2026`; the VI actually called is `??vi.lib\VIServer\UID to GObject Reference.vi` (subVI uid #990 in BOTH probing ops). ?윟 **`UID to GObject Reference.vi` DOES RESOLVE A TERMINAL UID.** `#7488` ??`Class Name` **`'Terminal'`**, uid echo OK, every error column EMPTY, owner `'FlatSequenceInnerTunnel'#7468` ??and that owner AGREES with the structural route that produced #7488 (`FlatSequenceInnerTunnel #7468`.`Left Terminal`), so it is two independent addressings denoting one object, not a self-echo. `#23906` (TARGET B, RE-DERIVED) ??`Class Name` **`'OuterTerminal'`**, uid echo OK, owner **`'RightShiftRegister'#23868`** ??**Pre-decided 120 CONFIRMED: the owner is the register, NOT `WhileLoop #23032`.** Controls answer as expected (`#7468`??'FlatSequenceInnerTunnel'`, w`7506`??'Wire'`, `#686`??'Diagram'`, all echoes OK). ?뵶 **THE ONE COLUMN THAT COULD NOT BE MEASURED: a literal TMSC to `Terminal`. NO op on disk carries a `Terminal`-seeded `To More Specific Class`** (the only class seeds that exist are `FlatSequenceInnerTunnel`, `FlatSequenceOuterTunnel`, `Wire`, `GObject`), and building one is exactly what this dispatch forbids. The two casts that DO exist were run on every uid: TMSC??GObject` succeeds on both terminals (`#7488`??'FlatSequenceInnerTunnel'`, `#23906`??'RightShiftRegister'`, no error), TMSC??FlatSequenceInnerTunnel` refuses a terminal with **`error 1055: Property Node`**. ?뵶?뵶 **NEGATIVE CONTROL, AND IT IS THE MOST IMPORTANT LINE HERE (`diag_c81_uidref.log:85`): on a NEVER-ALLOCATED uid (999983) the resolver returns a reference with EVERY ERROR COLUMN EMPTY whose class and uid are those of a DIFFERENT, previously-resolved object (`'Wire'#7506` ??the uid probed immediately before). The uid echo (`uid_back != uid_in`) is the ONLY column that catches it.** Any future uid-addressed writer that does not echo-check is a silent-wrong-object hazard = a rule-1a computation change. The mandatory failed-prediction review for `c80_rowd_routeA_r2.log` was dispatched and **ANSWERED** (`archive/peer/2026-09-22-c81-uidref-probe.md`, claude / `hypothesis` / opus max, 533 s, $3.4884, `tools/bench/peer_c81_uidref.log` rc=0) and is DISPOSED in full; its three measurement findings were applied in run 2 (negative controls, `err_bcw` attribution, cross-route identity) and its FIVE design findings were returned to judgement untouched ??chiefly *"do not gate D-2 on D-1: the NO branch is already open, and `OpConnectByUid`'s donor `OpConnectNested_v2.vi` IS NOT ON DISK"*, plus *"`Wire.Disconnect Terminal` 6370C0D is NOT the method labviewwiki marks '(Not Implemented)' ??those markers sit on 6370C02/03/04/09"*. No motor, no ASI, no camera; no op, verb or device built. PREVIOUS PURPOSE, unchanged and still true ???윟?뵶 **CYCLE-69/80 MATERIAL (M3a-3b = ROW D, ROUTE A) ??THE VERB WORKS, THE ROW DOES NOT LAND, NO ARTEFACT EXISTS, AND THE REMAINING STEP IS A DESIGN DECISION.** `tools/recipes/build_d1_m3a3.py` was RE-CUT IN PLACE to the SWAPPED `OpConnectFromWire_v0` call (Pre-decided 116-A: the op's already-uid-addressed SOURCE half takes FSIT terminal **#7488** = the true SINK; the index triple takes loop #23032 `Nodes[21]` t1 = the true SOURCE, so the Invoke sits on the BARE terminal); astcheck `ASTCHECK OK` 10 gates (`tools/bench/c80_astcheck_m3a3b_r3.log`). TWO RUNS, both on DATED SCRATCH copies that were deleted in the same run ??`tools/bench/c80_rowd_routeA.log` (47/5, rc=1, 112 s) and `tools/bench/c80_rowd_routeA_r2.log` (49/5, rc=1, 110 s). ?윟 **THE DECISIVE MEASUREMENT (`c80_rowd_routeA_r2.log:253-261`): immediately after the swapped connect and BEFORE any delete, net **7506** has **THREE** source terminals ??`RightShiftRegister #23868` (THE INTENDED NEW SOURCE), `FlatSequenceInnerTunnel #7468`, `RightShiftRegister #4334` (the OLD source) ??PD85 violations 0, and the loop border t1 `'Outgoing Handle'` went BARE ??**wire 7506** (`:244`). SO THE SWAPPED CALL DOES CONNECT: Pre-decided 116-A is NOT refuted and no new writer op is needed for the CONNECT.** ?뵶 What it does NOT do is REPLACE the old source: the net ends with three sources, hence `Wire.Is Broken?` **True** and `ExecState` 0, and deleting wire 7506 destroys the whole net (measured in both runs: #7488 and the border both go BARE). **Row D therefore needs ONE more step nobody has authorised ??remove the OLD `#4334` terminal from the net without destroying it ??and `Wire.Disconnect Terminal` 6370C0D is reported by labviewwiki as "(Not Implemented)" (c80-r2 review), which CONTRADICTS `docs/NAMES.md:1035`. That is a DESIGN DECISION, judgement's.** Arm A1 (delete-then-connect, Pre-decided 106's ordering) is DEAD and why is measured: with 7506 gone the op's `Wire.Terms[]` read raises `error 1055: Property Node in OpConnectFromWire_v0.vi`, `UID 2` 0, `wire_delta` 0, #7488 stays BARE (`c80_rowd_routeA_r2.log:119`). **ALSO MEASURED: Pre-decided 117's LITERAL uid is WRONG** ??`OpWireSource_v5` names the SHIFT REGISTER (`#23868`), never `WhileLoop #23032`, exactly as the delivered Row C read (`build_d1_m3a3_run2.log:182`). The mandatory failed-prediction review is **ANSWERED and disposed**: `archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md` (claude/hypothesis, opus max, 689 s) ??it REFUTED this session's "Route A is dead" reading, named arm A2's own instrumentation as the fault, and its cheapest test was built and run in the same dispatch; a first dispatch at `-TimeoutSec 780` ended **TIMEOUT** and told us nothing (`archive/peer/2026-09-22-c80-rowd-routeA-swapped.md`, disposed as a non-result). Hygiene: LabVIEW restarted at phase [0] (34,160 ??30,684 ??31,281 handles), refs 8/8/0 live, **bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? BYTE-UNCHANGED at both ends and all four pins hold, both scratch copies deleted, `THE FILES THIS RUN LEFT ON DISK: []`.** No motor, no ASI, no camera; no op, verb or device built. PREVIOUS PURPOSE, unchanged and still true ???뵶 **CYCLE-69 MATERIAL, SECOND DISPATCH (the c79 failed-prediction review): NO LabVIEW WAS TOUCHED ??the instance left by cycle 68 (pid 30520) was NOT restarted, NOT opened, NOT read; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is byte-unchanged because nothing opened it, and NO op VI was built.** The brief's TASK 1 (the mandatory failed-prediction review of Pre-decided 111) ran and **ANSWERED**: `archive/peer/2026-09-22-c79-rowd-writer.md`, claude / role `hypothesis` / **opus effort max**, outcome `ANSWERED (554s)`, cost **$3.9166** (in 18 / out 40,945 / cache-create 236,321 / cache-read 944,181, 18 turns), `tools/bench/c79_rowd_writer_peer.log` `BGRUN END rc=0 after 554s`. **TASK 2 (build `OpFsInnerTunnelConnect_v0`) WAS NOT STARTED, BY THE BRIEF'S OWN HALT CONDITION** ??*"If the review names a concrete alternative route that works with existing ops, STOP and report it ??do not build"* ??and the review named one: **`OpConnectFromWire_v0` WITH THE ROLES SWAPPED** (`wire_uid=7506` + the `Wire.Terms[]` index of #7488 ??`Wire Source`; sink triple = `Diagram[19]` / `Nodes[21]` / `Terminals[1]`, the NEW loop's BARE `Outgoing Handle`), i.e. the Invoke sits on the BARE SOURCE terminal and receives the FSIT terminal as `Wire Source`. `tools/recipes/build_d1_m3a3.py`'s `WRITERS` table and gate W1 are UNCHANGED. What the review overturns: **`docs/NAMES.md:847`'s "6349C03 is invoked on the SINK" is labelled "labviewwiki, ADOPTED" and the wiki page does not say it** ??so `c78_rowd_writer.log:19`'s conclusion is an inference from our own one-donor lineage (`OpConnect2_v0 ??OpConnectNested_v0 ??_v1 ??_v2 ??OpConnectFromWire_v0`), not a fact about LabVIEW; the W1 census itself stands. What it CONFIRMS: ruled-out (a) survives (`FlatSequence` is `Generic ??GObject ??FlatSequence`, so no `Nodes[]` address for #7468/#7488 can exist); **`Tunnel.Inside Terminals[]` 6356000 / `Outside Terminal` 6356001 is DEAD BY CITATION** ??`FlatSequenceInnerTunnel` is NOT a `Tunnel`, so `OpTunnelRead_v0`'s cast can never address it, and its real properties are `Left Terminal` **1C3A9000** / `Right Terminal` **1C3A9001**; and no documented NI verb wires without a sink refnum (`Create Described Wire` is itself a `Terminal` method; `Node.Connect Wires` needs both ends to be `Node`s). ?뵶 **THE JUDGEMENT CALL "Row D gets a new writer op" IS NOW CONTESTED ON EVIDENCE** and, if a new op IS still needed, the review says the briefed shape is wrong twice over: donor should be `OpConnectNested_v2` (its source half already addresses a loop's own BORDER terminal), NOT `OpStopFromNode_v0` (source ladder anchored INSIDE the body), and **`OpConnectByUid`** (uid ??`UID to GObject Reference.vi` ??TMSC on a **Terminal** seed ??the Invoke's `reference`) is smaller than `OpFsInnerTunnelConnect_v0` ??no property node, no side selector, and it serves every future uid-addressed sink. **The review's own 4-step cheapest discriminating test (~2 min, a dated scratch COPY of the bed) was NOT RUN** ??it selects between three designs and the session was already halted; the gate it prescribes is `OpWireSource_v5`'s source-terminal OWNER == `WhileLoop #23032`, NEVER a wire delta, because a swapped connect could SILENTLY BRANCH wire 7506 (owner `#637`) and that passes a wire count while being a rule-1a computation change. PREVIOUS PURPOSE, unchanged and still true ???뵶 **CYCLE-69 MATERIAL (M3a-3b = ROW D): NO LabVIEW WAS TOUCHED, NOTHING WAS MUTATED, NO ARTEFACT EXISTS ??ROW D IS BLOCKED ON JUDGEMENT BECAUSE THE WRITER DOES NOT EXIST.** The LabVIEW instance left running by cycle 68 (pid 30520) was NOT opened, NOT restarted and NOT read; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is byte-unchanged (nothing opened it). **STEP 1 DELIVERED (Pre-decided 112):** `tools/logclass.py:is_recipe_build_log()` reads a log's OWN last `BGRUN START` **command** and counts it only when that command RAN a `tools/recipes/*.py`; `guard_cycle.py`'s `since` **budget set only** now uses it and `is_build_log` is untouched (guard_peer still arms the failed-prediction review off it). Self-test `tools/bench/selftest_logclass_recipebuild.py` **24 pass / 0 fail** (`tools/bench/c78_step1_selftest.log`, rc=0), covering the two named non-builds, the real recipe log, append/`cp`/prose/review/watchdog scoping, and guard_peer's own `selftest_guard_peer_jev.py` + `selftest_guard_peer_failre.py` re-run UNCHANGED. **MEASURED EFFECT (`tools/bench/c78_rowd_writer.log`, 5/0, rc=0): since the cycle-64 retrospective the budget set goes 20 logs / span 2.23 h / `overdue` TRUE ??2 logs / span 0.25 h / `overdue` FALSE**; the 2 are `build_d1_m3a3.log` and `build_d1_m3a3_run2.log`. **STEP 2 DELIVERED AS A FILE, NOT AS A RUN:** `tools/recipes/build_d1_m3a3.py` is re-cut **IN PLACE** to M3a-3b = Row D alone (bed as input, Row C carried as read-only precondition gate C0, sink by Pre-decided 109/111 via `OpFsInnerTunnelTerm_v0` uid 7468 ??LeftTerm #7488, delete-before-connect, acceptance = one source of ANY class + OLD #4334/#637 off the net on the ordered idempotent second pass, the `%`-format defect fixed by `_f()` and the `GetVIReference` `com_error` by `open_op()` = a NAMED gate failure with the raw error); pinned astcheck **10 gates PASS, `ASTCHECK OK`** (`tools/bench/c78_astcheck_m3a3b.log`, gate 10: 109 `%`-sites verified, 0 mismatch, 0 invalid). ?뵶 **IT WAS NOT RUN, AND THAT IS THE FINDING.** Its first gate W1 asks "is a writer bound to this row's sink kind?" and the answer is measured NO: `Terminal.Connect Wire` 6349C03 is invoked ON THE SINK TERMINAL (`docs/NAMES.md:245`), Row D's sink is a TERMINAL UID on a `FlatSequenceInnerTunnel`, and **all four label maps declaring method 6349C03 (`opconnectfromwire_v0`, `opconnectnested`, `opconnectnested_v1`, `opconnectnested_v2`) address their sink as (`index`, `index 2`, `index 3`) = (diagram, `Nodes[]`, `Terminals[]`); writers taking a UID-addressed sink = 0; `opfsinnertunnelterm_labels.json` declares NO `method` at all (`kind: IN` ??a READER)**. A `FlatSequence` is a `GObject`, never a `Node`, so no `Nodes[]` address for it exists or can exist. Running the recipe would have halted at W1 before opening LabVIEW, so it was not run and no decoy artefact was saved. Building that writer is a NEW OP and a design decision ??judgement's, not material's. PREVIOUS PURPOSE, unchanged and still true ????**CYCLE-68 MATERIAL MEASUREMENT DONE, NOTHING MUTATED ??`tools/bench/diag_c77_rowd_addr.log` (5 gates pass / 0 fail, rc=0, 144 s), read-only on a scratch COPY of the bed; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is unchanged at both ends and all five pins hold.** LabVIEW restarted first (34,599 ??33,990; 34,941 after the reads; 33,996 at exit; refs 3 opened / 3 closed / 0 live). What the c76b review's cheapest test measured: (A) **`OpFsInnerTunnelTerm_v0` on uid 7468 RETURNS A TERMINAL REFERENCE with every error column empty ??`LeftTerm #7488` carries wire **7506**, `RightTerm #7471` wire 7448, self/cast echo `'FlatSequenceInnerTunnel'#7468`** (control read on FSIT #123 also answers), so the row-D SINK is addressable by uid today; (B) `find_node` MISSES on **#43914, #12938 AND #681** (173/173 diagrams, 635 nodes, 0 scan errors) ??the miss tracks the CLASS, not the owner and not #681; (B?? `owner_of(#681)` = **`'TopLevelDiagram' #536`**, NOT `'Diagram'`, and `diag_index(#681)` raises ??so **Pre-decided 107's route reads #681's table on a diagram that does not own it**, and #681 is absent from `Diagram #686`'s 27 `Nodes[]` rows ??the "how many entries carry wire 7506" question is UNREADABLE by that route, neither zero nor one; (C) `report_all('Diagram')` row 0 is still `TopLevelDiagram #536` (173 rows), #686 at idx 19; (D2, labelled secondary) exactly ONE terminal on `Diagram #686` carries wire 7506 ??`WhileLoop #637` `Nodes[4]` t10 `'Outgoing Handle'` is_source True, the wire's SOURCE side. c76b's disposition is written. PREVIOUS PURPOSE, unchanged and still true ????**M3a-3 ROW C IS DELIVERED (run 2, 26 gates pass / 2 fail ??both fails are the PRE-DECIDED Row-D deferral): `claudeDev\D1_s3b_m3a3_20260922_081056.vi`, md5 `33ef524e0b6b193a158c9221474c68e3`, 306,951 B** (`tools/bench/build_d1_m3a3_run2.log`). `Global #7202 'Global motor pos.vi'` t0 `'Focus position'` now reads the NEW loop's position register: sink net **25231** has exactly ONE source terminal of ANY class, `RightShiftRegister #23895`, PD85 violations 0, asserted on the ordered idempotent second pass (`wire_delta` 0); the OLD `#4256` is OFF the net. Junk `Invoke` purged (634??35??34). Refs 8/8/0 live; handles 34,592 ??30,689 (restart) ??33,833; all four md5 pins and the M3a-2 input unchanged. ?뵶 **ROW D IS DEFERRED TO M3a-3b ??a FAILED PREDICTION, reviewed** (`archive/peer/2026-09-22-c75-m3a3-run1-failpred.md`, ANSWERED, disposed): wire **7506 was NOT deleted** and nothing was improvised. ?좑툘 **RUN 1's ARTEFACT `claudeDev\D1_s3b_m3a3_20260922_075611.vi` (md5 `2461a749??) IS REJECTED AND MUST NOT BE USED AS A BED** ??its delete ran but the rebuild raised (`OpConnectNested_v2.vi` is not on disk), so `Global #7202` t0 is BARE = a dropped consumer; the rename to `_REJECTED_?? was refused by the permission layer, so it still carries the clean stage name. PREVIOUS PURPOSE, unchanged and still true ????**CYCLE-65 MATERIAL MEASUREMENT DONE, NOTHING MUTATED** ??`tools/bench/diag_c75_m3a3_rows.log` (6 gates pass / 0 fail, rc=0, 147 s) + `tools/bench/diag_c75b_loopterms.log` (5/0, rc=0, 4 s), both read-only on scratch COPIES of `D1_s3b_m3a2_20260922_023029.vi`; its md5 `3842f5e6?? is unchanged at both ends and all four STATUS pins hold. LabVIEW was RESTARTED first (42,570 ??34,322 handles; 34,336 at exit; refs opened==closed on both runs). PREVIOUS PURPOSE, unchanged and still true ????**M3a-2 IS DELIVERED AND INDEPENDENTLY VERIFIED** (15 gates pass / 0 fail) ??`claudeDev\D1_s3b_m3a2_20260922_023029.vi`, md5 `3842f5e6f128226235dc78353f26ef44`, **broken BY DESIGN** (`ExecState` 0; its missing rows belong to the next stage), never run and never cold-loaded. ?좑툘 **LabVIEW WAS LEFT RUNNING at 42,297 handles and MUST BE RESTARTED before the next batch.**
```
?뵷 **THE WHOLE CHAINED `purpose:` NARRATIVE ("PREVIOUS PURPOSE, unchanged and still true ????, cycles up to 64, 12,560 bytes on one line) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-22-status-cycle64-locknotes.md` 짠1** ??nothing deleted, nothing rewritten; the `purpose:` key above now states only the CURRENT state.
?뵷 **ALL 50 HISTORICAL LOCK-BLOCK ENTRIES (cycles 48??7: 48 `owner_*`/`lock_*` keys, the superseded `status:` line, and the `motor:` key) RELOCATED VERBATIM (rule 4) ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠1** ??that file also carries the three older `lock_relocated_*` pointers (into `??cycle5556-relocate.md`, `??cycle54-relocate.md`, `??cycle5153-relocate.md`, `??cycle49-relocate.md`, `??cycle48-lockkeys.md`). **Motor state, unchanged and still true:** limits LEFT ON since 2026-09-18 15:37 (PI TMN 0 / TMX 39 in RAM, ASI SL/SU 짹2 mm), ports closed.
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
??tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38, ?좑툘 **do NOT re-run the recipe, run 1 is the record**) 쨌 ??the "ZERO runnable experimental VIs" gap is BROKEN ??`tools/bench/drive_original_copy_v5.py` drives a plain copy of the original unattended end to end, twice 쨌 ??N1 accepted ??the GPU kernel is cleared for D1. **Order is D0 ??D1 ??D2** (`docs/cycle27-plan.md` Pre-decided 1). Prose VERBATIM ??`archive/2026-09-21-status-cycle67-locknotes.md` 짠3; earlier ??`archive/2026-09-18-status-cycle22-close.md` 짠2.

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; the five CLOSED items (32 쨌 55 쨌 56 쨌 51/52/52a 쨌 53's mechanical half) VERBATIM in `archive/2026-09-19-status-cycle46-relocate.md` 짠5, which forwards to `??026-09-18-status-cycle36-relocate.md` 짠5?벬?. ?좑툘 Two riders survive there: 32 is NOT to be closed unilaterally (the next outcome review judges it), and `audit_cycle` C4 still understates spend (retrospective-cycle31 F4). Only the live items below.
38/39/41. ?윞 **LIVE PART ONLY: `SR_QUEUE_AUTHORISED` stays False for good; `TEMP_SINK_AUTHORISED` is True for the `Z/dZ` row only** (Pre-decided 13 + 13a), and `Z/dZ` is now MEASURED WIRED (Pre-decided 19). `VI.Get Errors` 452 NOT built and `docs/d1-route-b-plan.md` 짠10 NOT AUTHORISED. ??the stall-watchdog liveness item is CLOSED by cycle 40's repair. Full text + run-3 history ??`archive/2026-09-19-status-cycle40-close.md` 짠2.
53. ?뵶 **The JUDGEMENT half STAYS OPEN, both review arms:** `POS` only declares the present location to be a coordinate and PI's `0x15/0x30` are relative to that zero, so **nothing we can read proves the controller zero still equals the ORIGINAL physical zero** ??i.e. that 0??9 still fences the intended physical window. VERBATIM ??`archive/2026-09-18-status-cycle36-relocate.md` 짠9; dispositions `archive/peer/2026-09-18-pi-err5-unreferenced-{codex,opus}.md`.
54. ?뵶 **TWO RULES YOU MUST FOLLOW, reasoning relocated ??`archive/2026-09-19-status-cycle40-close.md` 짠3.** (a) **The retrospective is the LAST thing a session runs** ??`guard_bash.py:226-227` marks the session retro-done on ANY `retrospective.py` in command position, and `guard_session` then refuses every later dispatch; nothing clears the mark. (b) **Dispatch in the FOREGROUND and wait; when something must run in the background, HOLD THE TURN OPEN until it lands** ??a `claude -p` session cannot take results as they arrive, and ending the turn kills the child. Repair named, deliberately NOT BUILT.
42/43/46/47. ?윞 **LIVE PART ONLY** ??42 ?좑툘 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed (?좑툘 A4 counts a whole DAY, so it charges the previous cycle's files to this one ??retrospective-cycle40 F4) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry.** 43 and 48/48a/49/50 ??CLOSED. Full text ??`archive/2026-09-19-status-cycle40-close.md` 짠4.
57. ?윞 **NEEDS JUDGEMENT RATIFICATION (cycle 68, material):** `guard_peer.py` now (a) formats its refusal through a drive-safe `_rel()` ??the same helper `guard_cycle.py:518` has carried since 2026-09-17; without it the hook RAISED instead of refusing when the failing log sat on another drive (`tools/bench/jev_discharge.log:21-26`, rc=99) ??and (b) skips a failing log whose LAST `BGRUN START` command is a **Jev script**, the other half of the user's 2026-09-22 "Jev??硫댁젣" exemption (until now wired only into `RUNNER_RE`, the COMMAND side, so a Jev self-test bundle's fixture text ??`STOP:`/`FAIL` by construction ??armed the gate against every other run). Scoped by the COMMAND, never the filename. Self-test `tools/bench/selftest_guard_peer_jev.py` **17 pass / 0 fail**, two new cases: C7 (a newer Jev log does not become the blocking log) and C7b (a non-Jev build that merely MENTIONS a Jev script still gates).

## NEXT
??**RESUMED 2026-09-22 (user confirmed after the Jev review): Jev gates in force** ??review discharge ACTIVE at p??.80 (`guard_peer`), firefighter veto ACTIVE at p??.30 (runner), triage (`tools/jev_triage.py`, log-reader first line), NEXT-quality and prior-art-dup ADVISORY. Jev scripts are exempt from the failed-prediction and material gates. Gemini is retired from every fallback (roles ??claude). `docs/jev-integration-plan.md` has the numbers.
?윟 **ROUTE A's VERB IS PROVEN (cycle 65 close, `tools/bench/c80_rowd_routeA_r2.log`, 49/5, rc=1; review `archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md` ANSWERED, verdict `ROUTE-A-ALIVE`):** the swapped `OpConnectFromWire_v0` call **DOES** attach the intended new source ??loop `#23032` `Nodes[21]` t1 went BARE ??wire **7506**, and a pre-delete walk of net 7506 shows THREE sources `('RightShiftRegister', 23868)` / `('FlatSequenceInnerTunnel', 7468)` / `('RightShiftRegister', 4334)`, PD85 0 (`:244`, `:253-261`). **So no new WRITER op is needed for the connect** (Pre-decided 119). Row D still does not land for ONE narrow reason: the connect **BRANCHES** instead of replacing (`Is Broken?` True, `ExecState` 0) and the delete-first ordering is refused at `Wire.Terms[]` with `error 1055`, `UID 2` 0 (`:119`) ??a dead wire uid cannot supply a terminal, and deleting 7506 leaves BOTH ends bare (measured twice). The missing capability is exactly **"address a BARE terminal by UID at the Invoke"**. Bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? unchanged at entry AND exit, `FILES THIS RUN LEFT ON DISK: []`, scratches deleted, refs 8/8/0. **Route A's arms are NOT to be re-run.**
?뵶 **FIRST ACT ??D-1, READ-ONLY, ~2 min, AND NOTHING IS BUILT IN THE SAME DISPATCH (Pre-decided 121/122):** does `UID to GObject Reference.vi` resolve a **TERMINAL** uid (it is proven only on tunnel and wire uids)? Call it on `#7488` (the `FlatSequenceInnerTunnel #7468` LeftTerm) and on the new loop's t1 terminal uid, on a dated scratch COPY of the bed, and report the returned class and whether a TMSC to `Terminal` succeeds ??`tools/bench/diag_c81_uidref.log`; delete the scratch. **That answer selects the op and nobody else decides it:** YES ??`OpConnectByUid` (donor `OpConnectNested_v2`, general, serves every future uid-addressed sink); NO ??the FSIT-head op on `Left Terminal` **1C3A9000** (donor `OpFsInnerTunnelTerm_v0`, whose reader half is already measured, so it has no unmeasured primitive).
?뵷 **THEN D-2, its own dispatch: build and SAVE the selected op** ??acceptance `ExecState` 1 + 20 consecutive calls with handles flat 짹100 + a call on `#7488` returning its terminal reference. **THEN D-3: Row D on the bed** ??delete 7506, connect `#23868`'s OUTER into `#7488`, save `claudeDev\D1_s3b_m3a3b_<stamp>.vi` (script save at `ExecState` 1, else the approved broken-intermediate `gui_save` ??say which). Acceptance = Pre-decided 106 + 111 + **117 CORRECTED BY 120: the source terminal's owner is `RightShiftRegister #23868`, NOT `WhileLoop #23032`** (the delivered Row C set that precedent, `build_d1_m3a3_run2.log:182`). Owner identity decides, never a wire count or delta.
??**Do NOT spend a cycle on `Wire.Disconnect Terminal` 6370C0D** (Pre-decided 123): the c80-r2 review cites labviewwiki marking it "(Not Implemented)" and `Terminals[]` read-only, contradicting `docs/NAMES.md:1035`, but delete-then-connect needs no disconnect verb. Do not edit that line on a citation alone.
??**DONE 2026-09-22 11:4x (material, no LabVIEW): `audit_cycle`'s C3/C4 cost split is REPAIRED and C4c added.** `logclass.is_judgement_session_log()` classifies by the log's own `BGRUN START` COMMAND (program `claude.exe` = a cycle_runner judgement session; `powershell ?쫜eer.ps1` is NOT), `audit_cycle.cost_split()` feeds C4/C4c. On cycle 64's own window the broken `C4 125 min 45 s; $63.9903 from 4 log(s)` / `reviews are 94%` is now `C3 7 min 11 s` 쨌 `C4 24 min 50 s; $12.3687 from 3` 쨌 `C4c 100 min 55 s; $51.6216 from cycle_59.log` 쨌 `C5 132 min 56 s (builds 5%, reviews 18%, judgement 75%)` ??C5 unchanged, nothing dropped (`tools/bench/audit_cycle_c81.log:14-20`). Self-test `tools/bench/selftest_audit_c4c_split.py` **33/0** (`??r2.log`), neighbours re-run UNCHANGED (logclass_recipebuild 24/0, guard_peer_jev 17/0, guard_peer_failre 26/0, audit_cost_window 7/0). 24 h view: judgement sessions are **$495.5670 across 12 `cycle_*.log`**, previously all charged to reviews (`audit_cycle_c81_default.log:17-20`). The original request line follows ???윝 **repair `audit_cycle`'s C3/C4 cost split** (cycle-64 retrospective `VIOLATION: device-failed`, accepted in full, disposition in `archive/peer/2026-09-22-retrospective-cycle64.md`). C4 reported reviews at `$63.9903` / 94 % of wall-clock, but `$51.6216` of that is the JUDGEMENT SESSION's own bgrun (`tools/bench/cycle_59.log:62`), not a review ??the three real reviews are $12.37 and ~24 min of ~133. Fix: exclude `cycle_*.log` from the review-cost set and add a separate **C4c judgement-session cost** line, with a self-test asserting the split on cycle 59's literal numbers. This is a CLASSIFIER REPAIR to an existing device (precedent Pre-decided 112/113), **not** a new device, so the 2026-09-18 08:53 no-new-device order is not touched.
?윞 **THEN `tools/stagekit.py`** per Pre-decided 93 ??the shared stage skeleton + self-test on a scratch of `D1_s2_loops.vi`; acceptance = re-cut ONE existing diagnostic on the kit with identical gate outcomes. ?좑툘 It is also the ONLY thing `doc_lint` FAILs L2 on: `STATUS.md:56` and `CLAUDE.md:363` cite a file that does not exist yet.
?뱱 **Cycle-65 doc work is DONE, do not redo it:** `docs/NAMES.md:850-860` marks 6349C03's "invoked on the SINK" an ADOPTED CONVENTION not a measurement (Pre-decided 115); `docs/NAMES.md:1130-1152` = the FSIT dead-ends table (6356000/6356001 ?? `Left/Right Terminal` 1C3A9000/1C3A9001 ?? Pre-decided 118); `docs/toolkit-capabilities.md:549-562` = the `find_node`-misses-the-`FlatSequence`-CLASS fact and "`diag_index` is not a membership test" (Pre-decided 110); c75 쨌 c76 쨌 c76b 쨌 c79 쨌 c80 쨌 c80-r2 reviews all disposed. Still placeholder (`doc_lint` L6, 51/489): `c74-m3a2-fmt.md`, `outcome-review-20260922.md`, `retrospective-cycle64.md`.
?좑툘 Restart LabVIEW before the first batch (left at 31,281 handles). No motor, no camera. Write `## NEXT` BEFORE launching the retrospective (the gate refuses otherwise); ending your turn kills your background children ??hold it until every `BGRUN END`. `git commit` at cycle close. The `## RUNNER STOPPED` heading at the foot of this file is a **historical 09:58 record**, not a live stop ??the runner has since resumed.
**Unchanged, still the user's to overturn:** N1 accepted on the pre-bead-loss window; the bead-4 z-LUT flip excluded by the FLIP mask; the harness RECORDS all 60 front-panel controls and SETS none; `background VIs_COPY` (94 files) untouched; the two new indicators keep their inherited labels (cosmetic).
## Where to look ??`CLAUDE.md` 쨌 `docs/secrets-and-handover.md` (API keys, ?ъ슜??援먯껜 泥댄겕由ъ뒪?? 쨌 `docs/jev-integration-plan.md` (Jev ?쎌엯 ?먮━, 2026-09-22) 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.

## RUNNER STOPPED 2026-09-22 09:58:16 ??the judgement session exited non-zero twice in a row (last exit 1, log cycle_61.log) - a repeat failure is a judgement matter, not something to retry


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Nothing was built, run, opened or locked; this is a read-only prior-art review. Findings below, each with a citation you can open.

---

# PRIOR-ART REVIEW — c82, `OpFsInnerTunnelConnect_v0` (D-2 of M3a-3b)

## PART A — THE DIRECTION

### A1 — SETTLED ALREADY, and settled **the way this dispatch proposes**. No slug.

The choice is decided at `docs/cycle27-plan.md:3548-3562` (Pre-decided 126, 2026-09-22) and its shape at `:3563-3580` (127). The plan cites both.

Worth recording because it is **older than every review the plan cites and is uncited**: this op's exact shape was designed on 2026-09-17. `archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md:68` — *"read `FlatSequenceInnerTunnel.Left Terminal` or `Right Terminal` once, then call the sink terminal's `Connect Wire` once with that returned reference"* — and its disposition `:94-97` says it was **deliberately not built** only because no op was authorised at the time: *"That is a new op (a fused `OpWireSource_v5` front half + `OpConnectNested_v1` back half) … so a material session may not take it."* The property ids the plan uses (`1C3A9000`/`1C3A9001`) come from that exchange (`:59-62`) and have since been measured (`docs/NAMES.md:1141`). So the direction is five days old, was blocked on authorisation rather than on evidence, and nothing in the record argues against it.

### A2 — REFUTED ALREADY, and the refutation is answered in writing. No slug.

`archive/peer/2026-09-22-c79-rowd-writer.md:251` — *"REFUTED/WITHDRAWN — candidate C, `OpFsInnerTunnelConnect_v0`"*, on two grounds: wrong donor (`OpStopFromNode_v0`) and a needlessly specific shape with a side selector (`:219-221`). Both are fixed in what is now proposed — donor is `OpConnectFromWire_v0`, LEFT terminal only, no selector — and the third ground (*"`OpConnectByUid` is smaller"*) is killed on direct inspection at `docs/cycle27-plan.md:3548-3554`: the donor `OpConnectNested_v2.vi` is not on disk. I checked that independently: no `opconnectnested_v2` op file exists, only `tools/bench/opconnectnested_v2_labels.json`. Nothing survives to block on.

### A3 — `contradicted`: the uid echo the plan adds is on the **wrong end**, so Pre-decided 125's rule is cited but not implemented

Both sides, quoted:

- `docs/cycle27-plan.md:3543-3545` (Pre-decided 125): *"any op or diagnostic that resolves an object BY UID must **re-read the returned reference's own UID and assert it equals the uid passed in**, as a named gate, before any value it produces is used or believed."* And why an error check is not enough: *"an error check does not, and a class-name check does not"* — the negative control is `tools/bench/diag_c81_uidref.log:85`.
- The recipe: `tools/recipes/build_opfsinnertunnelconnect_v0.py:425-439` branches `GObject.UID` **off `LeftTerm`**, and the gate compares it to a hard-coded literal — `:141` `LEFT_TERM_EXPECT = 7488`, asserted at `:585-586` and `:660-661`. The resolved object (`fsit_uid` → `UID to GObject Reference.vi`, input label `"UID 3"`, `:482`) is **never re-read**. The op's label map has no `uid_back`.

For `fsit_uid = 7468` the literal masks it. For any other FSIT there is no expected LeftTerm uid to compare against, so the history-echo mode has no gate at all — and the `To More Specific Class` does not cover it, because a stale echo of *another* `FlatSequenceInnerTunnel` (there are 518 in this VI, `docs/vi-server-ids.json:141`) casts cleanly and yields a valid-looking LeftTerm. That is the silent-wrong-object hazard 125 was written for, i.e. a rule-1a computation change that passes every gate in the recipe.

The correct shape is already on disk in the very VI whose reading half is being copied: `tools/bench/opfsinnertunnelterm_labels.json:7-9` — `"uid_in": "UID 2"`, `"uid_back": "UID 3"`, `"cls_back": "Class Name 5"` — and it is what `c80_rowd_routeA_r2.log:104` prints as `uid 7468 -> self 'FlatSequenceInnerTunnel'#7468`.

**To release:** either add the input-side echo (one more `GObject.UID` node off the resolver's `GObject`/TMSC output plus an indicator, and gate `uid_back == fsit_uid`), or open `docs/cycle27-plan.md:3538-3546` and show in writing that a `FlatSequenceInnerTunnel`-seeded TMSC cannot return a different FSIT's `LeftTerm` for a stale uid.

### A4 — UNREAD EVIDENCE: reported, no slug.

`docs/toolkit-capabilities.md:70` is the donor's own capability row and carries the **first** measurement of this exact capability, uncited anywhere in the plan: *"T2a: on a copy of the real VI it ACCEPTED a source terminal owned by `FlatSequenceInnerTunnel` **#5818** (wire w5812) and created a wire, op error `''`, sink **0 → 1231** — the capability §11s.1 said did not exist."* The plan rests the binding on `c80_rowd_routeA_r2.log:244` alone; this is an independent, five-days-older confirmation on a *different* FSIT. It strengthens the direction rather than blocking it, which is why there is no slug — but the acceptance narrative should carry it.

---

## PART B — THE ARTEFACT

### B1 — NO FINDING. Nothing on disk does this, and the two existing halves cannot be composed.

No op reaches an FSIT terminal **and** writes a wire. Only four label maps declare `"method": "6349C03"` — `opconnectnested`, `opconnectnested_v1`, `opconnectnested_v2`, `opconnectfromwire_v0` — and all four address their sink by `(diagram, Nodes[], Terminals[])`; `opfsinnertunnelterm_labels.json` declares no method at all. No `Terminal`-seeded or `FlatSequenceInnerTunnel`-seeded connect exists (the only TMSC seeds in the fleet are `FlatSequenceInnerTunnel`, `FlatSequenceOuterTunnel`, `Wire`, `GObject` — `docs/cycle27-plan.md:3531-3533`).

And the obvious "just call the reader, then the writer" composition is refuted in our own files: a refnum cannot cross COM between op calls — `docs/toolkit-capabilities.md:65`, *"its `Terminal` output is NOT returned to the caller (a refnum dies with the op's dataflow)"*. Fusing the halves into one VI is the only route, which is what this builds.

### B2 — ALREADY FAILED once, and the recipe addresses the recorded cause. Reported, no slug.

The donor has exactly one recorded failure at this operation: `docs/toolkit-capabilities.md:70` — *"T2c2 FAILED: that wire reads `Is Broken? TRUE`, and w1231 has TWO terminals reporting `Is Source? TRUE`"*, because *"terminal index 1 came from a census of the RESTRUCTURED copy and was applied to an UNRESTRUCTURED one"*. The cause was then partly withdrawn: `archive/peer/2026-09-17-cfw-t2c2-broken-wire.md:153-165` — *"the CONCLUSION survives, the CAUSE I gave does not"* — leaving the mechanism as **a sink that was already a source of another net**, the same multi-source shape that produced `Is Broken? True` again on 2026-09-22 (`tools/bench/c80_rowd_routeA_r2.log:259`, three sources).

The recipe addresses both: the triple is resolved **live** with a node-uid echo that raises on mismatch (`build_opfsinnertunnelconnect_v0.py:598-616`), and `G4c` refuses to connect unless the border terminal reads wire 0 (`:649-650`) — which is what `tools/gscript.py:2522-2523` requires (*"an already-wired SINK is not safe … wire only unwired sinks"*). No slug.

### B3 — `helper-exists`: the junk-`Invoke` census-and-purge is imported and not called

Every member of this writer family mints a stray node in the **target** VI. Measured, in the run the plan cites for its binding: `tools/bench/c80_rowd_routeA_r2.log:275-276` — *"CENSUS DIFF: Node 635 -> 636 ; 1 new uid(s): [(25312, 'Invoke', …)]"*, landing on `Diagram idx 19, Nodes[27]`. The delivered Row C had to deal with it (STATUS: *"Junk `Invoke` purged (634→635→634)"*).

The helper exists and is **already imported by this recipe**: `tools/recipes/build_d1_m3a1.py:614` `census_and_purge(path, nodes_before, tag, hints, keep_uids=())`, documented at `:615-616` as *"after EVERY move_in and EVERY connect_nested_v1, diff the `Node` census and purge the junk BY UID"* — imported as `M` at `build_opfsinnertunnelconnect_v0.py:107`, from which the recipe already takes `pd85_violations` and `print_walk` (`:676-677`). The sibling copy is `build_d1_m3a3.py:579` `purge_junk`, whose docstring names it *"The measured junk shape of the OpConnect\* family"*. It is a Pre-decided rule, not a nicety: `build_d1_m3a1.py:59` (55(c), *"after EVERY border write"*) and `:65` (71, *"the junk `Invoke` the call mints is FACT-logged with its uid"*).

`grep -n 'purge\|census' tools/recipes/build_opfsinnertunnelconnect_v0.py` returns only the Diagram census inside `resolve_triple`. So gate (4) — the dispatch's own "discriminating test for the op's parameter binding", the one Pre-decided 127 put in D-2 precisely so *"Row D … must not be attempted a sixth time on an unexercised op"* — does not measure whether the new op mints the family's junk node, and gate (2)'s 20 consecutive calls would accumulate 20 of them unobserved. D-3 writes to the **bed**, where that node is saved into the artefact.

**To release:** add the `M.census_and_purge` call (or a Node-count FACT line) around the G4 call and the G2 loop, or state in the plan that junk-node characterisation is deliberately deferred to D-3 and why that is safe there.

### B4 — `already-measured`: acceptance (2) was measured on 2026-09-19, on three ops including this op's own front half

Acceptance (2) — *"20 consecutive calls leave LabVIEW's handle count flat ±100"* — is treated as an open question. It is not. `docs/toolkit-capabilities.md:460-478`, **"⚖️ S0 CLOSED, 2026-09-19 — the traverse ops are ACCEPTED WITHOUT a `Close Reference`, on measurement"**, with the table at `:468-472`:

| arm | 20 calls of | handles | private bytes | evidence |
|---|---|---|---|---|
| traverse-only | `report_all(Diagram)` | **+9** | −0.1 MB | `tools/bench/s0_hygiene_probe_run2.log:121-123` |
| traverse + mutate | … → **`OpWireSource_v5`** → `build_property` | **−19** | +34.6 MB | `tools/bench/s0b_refleak_profile.log:61-64` |
| mutate-only | same, traverse legs removed | **−12** | +34.5 MB | `tools/bench/s0b_mutonly_profile.log:61-65` |

`OpWireSource_v5` carries the same `UID to GObject Reference.vi` → TMSC → property-node → Index Array front half this op is built from (`docs/toolkit-capabilities.md:60`), and `:474-475` attributes the +34.6 MB to the VI growing by 20 Property nodes, **not** to a reference leak. `:477` records that `docs/cycle27-plan.md` Pre-decided 25(iv)+27+28 accept ops without `Close Reference` on that measurement.

Two things the plan should take from it rather than re-derive. First, the criterion is a **pair**: `:476` — *"G-A no `error 2` · G-B handles ±100 from call 1 · **G-C private drift ≤ 5 MB**"*; the plan keeps G-B and drops G-C. Second, and this is the part that matters: `:484-485` — *"'The ops do not leak measurably' is not 'the ops cannot exhaust anything': **the kernel handle count is blind to VI Server refnums** (`tools/gscript.py:227-228`), which is why G-C exists beside G-B."* So gate (2) alone cannot establish that the new op closes what it opens; and the hygiene repair itself has a recorded price — `tools/recipes/build_s0_closeref_v3.py:20`, *"`Close Reference` DEFEATED FOUR WIRING ATTEMPTS"* — across a three-version stage (`build_s0_closeref_v0.py` / `_v3.py`) that ended in no repair being built at all.

**To release:** cite the S0 table as the prior measurement and either add G-C (private-bytes drift) beside G-B, or write in the plan that gate (2) is a regression check against that baseline, not a hygiene proof — and say what D-2 does if it fails, given that the recipe's own contract is *"A failed gate is the dispatch's result: no improvised second route."*

---

Nothing here argues against building the op. Two of the three shrink or correct a gate; A3 is the one that would otherwise ship a uid-addressed writer with the hazard Pre-decided 125 was written three hours earlier to prevent.

```
PRIOR-ART: contradicted      (A3 — docs/cycle27-plan.md:3543-3545 vs tools/recipes/build_opfsinnertunnelconnect_v0.py:141,:425-439,:585-586,:660-661 + tools/bench/opfsinnertunnelterm_labels.json:7-9 — covers ONLY the uid-echo gate's placement (output side, against a literal, instead of input side against fsit_uid); does NOT touch the op's donor, its shape, its binding or gate (4))
PRIOR-ART: helper-exists     (B3 — tools/recipes/build_d1_m3a1.py:614,:59,:65 imported as M at tools/recipes/build_opfsinnertunnelconnect_v0.py:107, measured instance tools/bench/c80_rowd_routeA_r2.log:275-276 — covers the missing junk-Invoke census/purge in gates G2 and G4; does NOT claim the junk node breaks the acceptance the recipe already checks)
PRIOR-ART: already-measured  (B4 — docs/toolkit-capabilities.md:460-478,:484-485 + tools/bench/s0_hygiene_probe_run2.log:121-123 + tools/bench/s0b_refleak_profile.log:61-64 + tools/recipes/build_s0_closeref_v3.py:20 — covers acceptance (2), its dropped companion criterion G-C, and the recorded blindness of the handle count to VI Server refnums; does NOT assert gate (2) will fail)
```

## Sources

(extract from answer)

## What was done with it

All three slugs are ACCEPTED and the recipe was changed before it ran. Nothing was refuted; A1/A2/B1/B2
needed no action, and A4's unread citation was added to the recipe's docstring.

FIXED: contradicted - tools/recipes/build_opfsinnertunnelconnect_v0.py:434 - the build now creates TWO `GObject.UID` (632A813) nodes, the INPUT-side one branched off the resolver's own `GObject` output with indicator `uid_back`, and gate G3a asserts `uid_back == fsit_uid` on every one of the 20 calls, so Pre-decided 125's rule is implemented at the end it was written for and not only against the literal 7488.
FIXED: helper-exists - tools/recipes/build_opfsinnertunnelconnect_v0.py:231 - a `purge_junk` built from the already-imported `build_d1_m3a1.node_census` / `new_nodes` / `node_view` / `delete_by_uid` primitives now brackets BOTH the 20-call loop (junk rate printed as total/20) and the G4 call, so the family's stray `Invoke` is measured and purged in D-2 instead of being carried into D-3's write to the bed.
FIXED: already-measured - tools/recipes/build_opfsinnertunnelconnect_v0.py:213 - `private_bytes()` was added and its drift is reported beside the handle delta, and the G2 gate text now states that it is a REGRESSION CHECK against the S0 baseline `docs/toolkit-capabilities.md:460-478` rather than a hygiene proof, citing `:484-485` on the handle count's blindness to VI Server refnums.

Detail, per finding:

* **A1 / A2 — no action.** The direction they settle is the one Pre-decided 126/127 already took.
* **A3 `contradicted` — accepted in full.** The reviewer is right that the first cut echoed only the
  OUTPUT side, where the literal `LEFT_TERM_EXPECT = 7488` masks the hazard for this one FSIT and leaves
  it ungated for the other 517. The shape adopted is the one already on disk
  (`tools/bench/opfsinnertunnelterm_labels.json:7-9`, `uid_in` / `uid_back`). The op now carries both
  echoes; the label map gains `uid_back` and `err_uidback`; the wrapper poisons both before every run.
* **A4 — no slug, citation adopted.** `docs/toolkit-capabilities.md:70` (the donor accepting a source
  terminal owned by `FlatSequenceInnerTunnel #5818`, five days older than `c80_rowd_routeA_r2.log:244`)
  is now quoted in the recipe's docstring as the independent confirmation of the binding.
* **B1 / B2 — no action.** B1 confirms nothing on disk does this and the halves cannot be composed across
  COM; B2's recorded cause is already addressed by the live uid-echoed triple resolution and by gate G4c,
  which refuses to connect unless the border terminal reads wire 0.
* **B3 `helper-exists` — accepted in full.** `M.census_and_purge` itself is deliberately NOT called (it
  writes M's own JSON sidecar and appends to M's module state); the primitives underneath it are, in the
  shape `build_d1_m3a3.purge_junk` already uses. The census is kept OUT of the 20-call loop because a
  `report_all('Node')` on a 635-node VI moves the very handle count G2 measures - the rate is read as
  total / 20 immediately after the window closes.
* **B4 `already-measured` — accepted in full.** Gate (2) is kept (it is Pre-decided 127's wording and the
  op is new), but it is now explicitly scoped as a regression check against the S0 table, with the
  private-bytes companion REPORTED rather than gated: S0's own G-C threshold was set against ops that
  created 20 Property nodes in the target, which this op does not do, so importing the 5 MB number as a
  gate would be importing a threshold from a different experiment.
