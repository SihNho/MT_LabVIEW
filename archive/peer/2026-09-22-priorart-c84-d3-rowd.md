# priorart-c84-d3-rowd

- **agent:** claude
- **role:** priorart
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.2316  in 34 / out 23692 / cache-create 225643 / cache-read 2765416  (298s, 32 turn(s))
- **date:** 2026-09-22 13:58:27
- **outcome:** ANSWERED (302s)
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
# D-3 of M3a-3b ??`OpFsInnerTunnelConnect_v1.vi` (roles exchanged) and the missing cell

Recipe under review: `tools/recipes/build_d1_m3a3b_d3.py`
The judgement session has already taken the route decision after reading the c83 2횞2; it is NOT open in
this dispatch. What is open is whether any of the work below has already been built, measured or refuted
in this project's own files.

## What is being built

1. **`claudeDev\OpFsInnerTunnelConnect_v1.vi`** ??`OpFsInnerTunnelConnect_v0.vi` (md5
   `50a1e58a4825c2ce030ed9a41e204931`, never modified, never deleted) with **the two Invoke feeds
   EXCHANGED**: the `Terminal.Connect Wire` 6349C03 Invoke sits on the FSIT `LeftTerm` (uid ??
   `UID to GObject Reference.vi` ??`To More Specific Class`(FlatSequenceInnerTunnel) ??`Left Terminal`
   1C3A9000), and the terminal named by the (diagram, `Nodes[]`, `Terminals[]`) INDEX TRIPLE is passed as
   `Wire Source`. v0's repaired error path is kept (the Invoke's OWN `error out` reaches `error out 7`),
   and `Auto Route?` is exposed as a front-panel control.
   The construction is not new: `tools/bench/diag_c83_connect2x2_r2.py:340` `make_swap` already built this
   exact swap as a SCRATCH and it was legal (`diag_c83_connect2x2_r2.log:36-46` ??nets w572 and w1337
   exchanged, the two other consumers `#241.reference` / `#187.reference` re-branched, Remove Bad Wires
   removed 0, ExecState 1). This recipe re-cuts it against the LIVE topology so it can be SAVED as v1.

2. **The measurement nobody has run**: the same op called with wire **7506 LEFT ALIVE** ??i.e. the Invoke
   on the SINK terminal while that sink is still wired. Every wire-alive cell so far (R0/R0b) put the
   Invoke on the SOURCE terminal and BRANCHED; every swapped cell (R3/R4) had 7506 deleted first and
   returned `error 1055` because the deletion makes `#7468` unresolvable.

3. **If, and only if, a cell passes**: Row D landed as a NEW file `claudeDev\D1_s3b_m3a3b_<stamp>.vi`,
   built from the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 `33ef524e??, 306,951 B), which stays
   byte-unchanged.

## The gates

B1?밄5 build v1: the copy at ExecState 1 with both Invoke feeds wired ??both nets deleted ??the two crossed
feeds + every other consumer re-branched, each verified by the SAME wire uid on both ends ??Remove Bad
Wires removes 0 (so the crossed feeds are not type-broken) ??`Auto Route?` control ??ExecState 1 ??script
save ??ExecState 1 RE-READ ??labels JSON ??the donor v0's md5 unchanged.
G2 20 consecutive calls leave the handle count flat 짹100 (regression check against the S0 baseline
`docs/toolkit-capabilities.md:460-478`; private-bytes drift reported beside it per `:484-485`); the junk
`Invoke` rate is measured and purged.
G3 both uid echoes on every call: `uid_back` == 7468 (input side, Pre-decided 125) and `term_uid` == 7488.

**GATE S**, per cell (S-T `Auto Route?` TRUE, S-F FALSE), each on its OWN dated scratch copy of the bed
with 7506 alive, each printing the value compared:
(a) the FSIT `LeftTerm`'s net has EXACTLY ONE source terminal and its OWNER is `RightShiftRegister #23868`
    (`OpWireSource_v5`; owner identity decides, never a wire count or delta ??Pre-decided 117 as corrected
    by 120);
(b) `#4334` is OFF that net;
(c) PD85 violations 0 on the walk;
(d) `Wire.Is Broken?` False on that wire, AND the diagram-wide broken-wire count is not HIGHER than the
    same count on the bed's bytes before the call. The count is taken as
    `wires before ??wires after Remove Bad Wires` (`gscript.remove_bad_wires_scripted`, VI method 410),
    which MUTATES ??so the baseline runs on its own byte-identical control copy that is then discarded,
    the cell's number is taken as that scratch's last act, and on the artefact the probe runs on a
    THROWAWAY COPY OF THE SAVED FILE. The bed is broken BY DESIGN, so absolute `ExecState` is not a gate.
(e) the FSIT `Right Terminal` `#7471` still carries its inner wire 7448 (the Row C lesson ??a dropped
    consumer is a silent failure).
Step 3 re-asserts (a)??e) on the artefact plus the ORDERED IDEMPOTENT SECOND PASS of Pre-decided 106
(`wire_delta` 0 on an identical second connect, identity read on THAT pass).

## Constraints

* The bed is READ-ONLY: md5-pinned at entry AND exit, never opened for execution.
* `OpFsInnerTunnelConnect_v0.vi` is never modified or deleted; wire 7506 is never deleted anywhere.
* Rig 議곕┰: no motor, no ASI, no camera. VI Scripting and COM only. LabVIEW restarted first.
* One `bgrun`, one notification; handles before/after; refs opened/closed/live; every scratch deleted.
* If NEITHER cell passes GATE S: nothing is saved, and the run stops. No third configuration is
  improvised, no terminal is removed from a net, no tunnel is re-created, `Wire.Disconnect Terminal` is
  not touched ??those are judgement's and none is authorised.
* Save route: script when `ExecState` is 1, else `save(allow_broken=True)` ??`gui_save`, the approved
  broken-intermediate route (CLAUDE.md 짠3 item 6, user 2026-09-22).

## What the reviewer is asked

Has any of this already been built, measured or refuted in this project's own files ??in particular:
a SAVED op with the connect roles exchanged (as opposed to c83's scratch); a call of any connect op onto
an ALREADY-WIRED sink terminal on this VI or any other, and what it did; a diagram-wide broken-wire count
already implemented somewhere other than `remove_bad_wires_scripted`; a measurement that already says the
swapped-with-wire-alive configuration cannot work; or an existing artefact that already lands Row D?
Cite `file:line`.


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
  status: released
  owner:
  since: 2026-09-22 13:40
  purpose: ?윟?윟 **CYCLE-83 MATERIAL, D-2b OF M3a-3b: THE SEPARATION IS DONE AND THE ANSWER IS NONE OF (a)/(b) ??THE VERB WAS NEVER SILENT, ITS ERROR WAS BEING SWALLOWED BY `Clear Errors.vi`, AND WHAT IT SAYS IS `error 1055` BECAUSE DELETING WIRE 7506 MAKES FSIT `#7468` UNRESOLVABLE.** Two runs, both on dated scratch COPIES deleted in the same run: `tools/bench/diag_c83_connect2x2.log` (37/5, rc=1, 173 s) and `tools/bench/diag_c83_connect2x2_r2.log` (27/14, rc=1, 151 s ??the 14 ARE the measurement). ??**STEP 0 DELIVERED IN TWO MOVES AND THE SECOND ONE IS THE ONE THAT MATTERS:** run 1 put an indicator on the first free `error out` in the Invoke's chain, which is `Clear Errors.vi #399`, 3 hops downstream ??**empty by construction**; run 2 deleted that feed and BRANCHED the Invoke's OWN `error out` (w1027) onto the same indicator with `gscript.wire_indicators`:1786. **`claudeDev\OpFsInnerTunnelConnect_v0.vi` is now md5 `50a1e58a4825c2ce030ed9a41e204931`, 18,521 B, `ExecState` 1 re-read after the save** (was `c0d5efe3?? ??`cda1e36e?? ??this); `err_invoke: "error out 7"` added to `tools/bench/opfsinnertunnelconnect_v0_labels.json`. Roles, `Auto Route?` and the address route were NOT touched. ?뵶 **THE RAW VERDICT, read for the first time: `error 1055: Invoke Node in OpFsInnerTunnelConnect_v0.vi | Method Name: Connect Wire`** ??identical in ALL FOUR configurations on the real pair, alongside `error 1055: To More Specific Class in UID to GObject Reference.vi` on the source half. ?뵶 **THE CAUSE IS THE DELETE, MEASURED BY A CONTROL CELL: with wire 7506 ALIVE the same call has NO error, `term_uid` 7488, `uid_back` 7468, `UID 2` 7506 and the border terminal goes 0 ??7506 (i.e. it BRANCHES the existing net, `wire_delta` 0, `Is Broken?` True); with 7506 DELETED the FSIT uid 7468 no longer resolves and nothing is written.** Poison ON vs OFF is identical (R0 vs R0b) ??the review's artefact hypothesis is REFUTED on the machine. ?윟 **(a) AND (b) ARE BOTH REFUTED, each twice.** On four FRESH TRIVIAL VIs (two bare `VI Server:GObject` Property nodes, driven through a scratch copy of `OpConnect_v0.vi` carrying a created `Auto Route?` control) **ALL FOUR cells created the wire** ??`wire_delta` 1, the SAME wire uid 93 on both ends, 0 junk. On the real pair all four cells behave identically (no wire, same 1055), **including the two with the roles EXCHANGED**: run 2 BUILT a legal swapped copy (`ExecState` 1, Remove Bad Wires removed 0 ??the crossed feeds are not type-broken) after re-branching the two other consumers of the deleted nets (`#241.reference`, `#187.reference`) that made run 1's copy `ExecState` 0. ?좑툘 **A GATE THIS PROJECT HAS BEEN READING FOR THREE CYCLES IS NOT A MEASUREMENT**: the border-terminal row carries `wire_err: 1055` whenever the terminal is BARE (and 0 when wired), so `wire: 0` there is the error path's default ??it tracks bareness perfectly in these 6 cells, but it is a REFUSAL, not a read (the review's strongest point, accepted). The mandatory failed-prediction review is ANSWERED and DISPOSED in full (`archive/peer/2026-09-22-c83-2x2-swap-1055-r2.md`, claude/`hypothesis`/opus max, 403 s; a first dispatch at `-TimeoutSec 840` ended TIMEOUT and told us nothing ??`archive/peer/2026-09-22-c83-2x2-swap-1055.md`); its four accepted tests were all built into run 2, its three unacted findings are listed under `## What was done with it` for judgement. Hygiene: LabVIEW restarted at the head of both runs (33,960 ??33,987; 34,566 after the work; 33,989 at exit), refs 37/37/0 live, **bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? BYTE-UNCHANGED at both ends of BOTH runs, all five pins hold, `OpConnect_v0.vi` and `EMPTY_v0.vi` md5-unchanged (only copied), every scratch deleted, `THE FILES THIS RUN LEFT ON DISK: []`** (the op is edited in place, not added). The bed was never opened for execution. No motor, no ASI, no camera. PREVIOUS PURPOSE, unchanged and still true ???윟?뵶 **CYCLE-82 MATERIAL, D-2 OF M3a-3b: THE OP IS BUILT, SAVED AND LEGAL ??AND THE END-TO-END EXERCISE FAILED, WHICH IS THE POINT OF PUTTING IT IN D-2.** `tools/bench/build_opfsinnertunnelconnect_v0.log`, **45 gates pass / 2 fail** (the 2 are one gate, G4f, plus its STOP echo), `BGRUN END rc=1 after 324s`. ??**ARTEFACT: `claudeDev\OpFsInnerTunnelConnect_v0.vi`, md5 `c0d5efe3389b0dea388ee565433fb683`, 17,881 B, `ExecState` 1 re-read AFTER the save**; labels `tools/bench/opfsinnertunnelconnect_v0_labels.json`; donor `OpConnectFromWire_v0.vi` md5 `b545279e?? unchanged. Gates: **G1 PASS** (ExecState 1) 쨌 **G2 PASS** (20 consecutive calls, handles 42,461 ??42,555, delta **+94** ??짹100; private-bytes drift **0.03 MB**; refs 22/22/0) 쨌 **G3 PASS** (`term_uid` **7488** on 20/20 calls) 쨌 **G3a PASS** (the INPUT-side echo `uid_back` **7468** on 20/20 ??Pre-decided 125 implemented at both ends after the prior-art review's A3) 쨌 **G4 FAILS AT G4f**. ?뵶 **THE MEASUREMENT, AND IT IS A NEW FACT: `Terminal.Connect Wire` 6349C03 IS A SILENT NO-OP WHEN THE TERMINAL HANDED TO `Wire Source` IS BARE.** Arm 1 (wire 7506 ALIVE, the 20-call scratch): every call returned `sink_wire=7506`, `is_broken=True`, `err=''` ??the verb fires and BRANCHES, exactly as `c80_rowd_routeA_r2.log:253-261`. Arm 2 (wire 7506 DELETED, both ends bare, `build_opfsinnertunnelconnect_v0.log:315-342`): `err=''`, every per-stage error column `''`, `term_uid` 7488, `uid_back` 7468, **`UID 2` 0, `wire_delta` 0, border t1 still wire 0** ??and one junk `Invoke` WAS minted, so the Invoke executed. So the source half is proven (the FSIT LeftTerm resolves from a BARE tunnel terminal) and the WRITE is the thing that declines. Ruled out on the machine, not by argument: addressing (node uid echo 23032 MATCH, t1 `'Outgoing Handle'`, `wire == 0` asserted by G4c immediately before), source resolution (both echoes, all error columns empty, on the same call), stale readouts (every indicator poisoned per call, `Is Broken?` poisoned True), already-wired sink, and op legality. **Junk-node rate MEASURED for the first time: 1.00 stray `Invoke` per call (Node 635 ??655 over 20), purged in-run** (the prior-art review's B3). ?뵶 **THE MANDATORY FAILED-PREDICTION REVIEW IS ANSWERED AND IT REFUTES THIS SESSION'S READING** (`archive/peer/2026-09-22-c82-bare-source.md`, claude/`hypothesis`/opus max, `tools/bench/peer_c82_bare_source.log` rc=0, 424 s; disposed in full): **`tools/bench/build_harness_copyloop2.log:31-40` already records 6349C03 CREATING a wire between two BARE terminals ??wire census 9 ??10, both ends on wire 346, `ExecState` 0 ??1 ??and a +1 count cannot be a branch (`gscript.py:2521-2522`).** So "the method declines on a bare `Wire Source`" is FALSE as a property of the method, and arm 1 vs arm 2 differ in THREE ways at once (wired?봟are 쨌 join?봠reate 쨌 polarity undetermined?봡etermined), so this run cannot attribute the failure. Its three live alternatives, RECORDED NOT ACTED ON (judgement's): (a) **the ROLES ARE INVERTED** ??`Wire Source` is documented as *"the original source of the wire"*, #7488 is `is_source=False` (the true SINK) and the Invoke sat on a `is_source=True` terminal, so a CREATE has two sources and no sink; **this makes Pre-decided 119 an OVER-GENERALISATION ??`c80_rowd_routeA_r2.log:244` proved role exchange when JOINING, not when creating**; (b) `Auto Route?` is at default FALSE and no op in the fleet wires it; (c) the Invoke's own `error out` is not shown to reach the op's `error out`, so "silent" is so far only "quiet". **Its cheapest test was NOT run (the brief forbids improvising after a failed gate): a 2횞2 on a TRIVIAL scratch VI with `gscript.connect_terminals` alone, T1 (invoke on bare INPUT, source bare OUTPUT) vs T4 (arm 2's polarity) ??~2 min, no bed, nothing built.** Its follow-on (swap the op's halves so the Invoke sits on the true SINK ??a ONE-WIRE change at `build_opfsinnertunnelconnect_v0.py:509`, not a new op) is a design decision and was returned untouched. Prior-art review `archive/peer/2026-09-22-priorart-c82-fsitconnect.md` ANSWERED, 3 slugs (`contradicted`, `helper-exists`, `already-measured`), ALL THREE ACCEPTED and fixed BEFORE the run, dispositions written under `## What was done with it`. Hygiene: LabVIEW restarted at phase [1] (33,931 ??33,988; 31,258 after the work; 33,996 at exit), refs 22 opened / 22 closed / 0 live, **bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? BYTE-UNCHANGED at both ends, all five pins hold**, both scratches deleted, `THE FILES THIS RUN LEFT ON DISK: ['OpFsInnerTunnelConnect_v0.vi']`. The bed was never opened for execution. No motor, no ASI, no camera. PREVIOUS PURPOSE, unchanged and still true ???윟 **CYCLE-81 MATERIAL, D-1 OF M3a-3b IS MEASURED AND THE ANSWER IS YES ??NOTHING WAS BUILT, NOTHING SAVED, NOTHING MUTATED** (Pre-decided 121/122; read-only on dated scratch COPIES, both deleted in their own run). Two runs, `tools/bench/diag_c81_uidref.log` (7/0, rc=0, 125 s) and `tools/bench/diag_c81_uidref_r2.log` (7/0, rc=0, 126 s); bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? byte-unchanged at BOTH ends of BOTH runs, all five pins hold, `THE FILES THIS RUN LEFT ON DISK: []`, refs 3/3/0 live, handles 33,986 ??33,972 (restart) ??33,967 at exit. LabVIEW 2026 **26.3.1f1**, 64-bit, `C:\Program Files\National Instruments\LabVIEW 2026`; the VI actually called is `??vi.lib\VIServer\UID to GObject Reference.vi` (subVI uid #990 in BOTH probing ops). ?윟 **`UID to GObject Reference.vi` DOES RESOLVE A TERMINAL UID.** `#7488` ??`Class Name` **`'Terminal'`**, uid echo OK, every error column EMPTY, owner `'FlatSequenceInnerTunnel'#7468` ??and that owner AGREES with the structural route that produced #7488 (`FlatSequenceInnerTunnel #7468`.`Left Terminal`), so it is two independent addressings denoting one object, not a self-echo. `#23906` (TARGET B, RE-DERIVED) ??`Class Name` **`'OuterTerminal'`**, uid echo OK, owner **`'RightShiftRegister'#23868`** ??**Pre-decided 120 CONFIRMED: the owner is the register, NOT `WhileLoop #23032`.** Controls answer as expected (`#7468`??'FlatSequenceInnerTunnel'`, w`7506`??'Wire'`, `#686`??'Diagram'`, all echoes OK). ?뵶 **THE ONE COLUMN THAT COULD NOT BE MEASURED: a literal TMSC to `Terminal`. NO op on disk carries a `Terminal`-seeded `To More Specific Class`** (the only class seeds that exist are `FlatSequenceInnerTunnel`, `FlatSequenceOuterTunnel`, `Wire`, `GObject`), and building one is exactly what this dispatch forbids. The two casts that DO exist were run on every uid: TMSC??GObject` succeeds on both terminals (`#7488`??'FlatSequenceInnerTunnel'`, `#23906`??'RightShiftRegister'`, no error), TMSC??FlatSequenceInnerTunnel` refuses a terminal with **`error 1055: Property Node`**. ?뵶?뵶 **NEGATIVE CONTROL, AND IT IS THE MOST IMPORTANT LINE HERE (`diag_c81_uidref.log:85`): on a NEVER-ALLOCATED uid (999983) the resolver returns a reference with EVERY ERROR COLUMN EMPTY whose class and uid are those of a DIFFERENT, previously-resolved object (`'Wire'#7506` ??the uid probed immediately before). The uid echo (`uid_back != uid_in`) is the ONLY column that catches it.** Any future uid-addressed writer that does not echo-check is a silent-wrong-object hazard = a rule-1a computation change. The mandatory failed-prediction review for `c80_rowd_routeA_r2.log` was dispatched and **ANSWERED** (`archive/peer/2026-09-22-c81-uidref-probe.md`, claude / `hypothesis` / opus max, 533 s, $3.4884, `tools/bench/peer_c81_uidref.log` rc=0) and is DISPOSED in full; its three measurement findings were applied in run 2 (negative controls, `err_bcw` attribution, cross-route identity) and its FIVE design findings were returned to judgement untouched ??chiefly *"do not gate D-2 on D-1: the NO branch is already open, and `OpConnectByUid`'s donor `OpConnectNested_v2.vi` IS NOT ON DISK"*, plus *"`Wire.Disconnect Terminal` 6370C0D is NOT the method labviewwiki marks '(Not Implemented)' ??those markers sit on 6370C02/03/04/09"*. No motor, no ASI, no camera; no op, verb or device built. PREVIOUS PURPOSE, unchanged and still true ???윟?뵶 **CYCLE-69/80 MATERIAL (M3a-3b = ROW D, ROUTE A) ??THE VERB WORKS, THE ROW DOES NOT LAND, NO ARTEFACT EXISTS, AND THE REMAINING STEP IS A DESIGN DECISION.** `tools/recipes/build_d1_m3a3.py` was RE-CUT IN PLACE to the SWAPPED `OpConnectFromWire_v0` call (Pre-decided 116-A: the op's already-uid-addressed SOURCE half takes FSIT terminal **#7488** = the true SINK; the index triple takes loop #23032 `Nodes[21]` t1 = the true SOURCE, so the Invoke sits on the BARE terminal); astcheck `ASTCHECK OK` 10 gates (`tools/bench/c80_astcheck_m3a3b_r3.log`). TWO RUNS, both on DATED SCRATCH copies that were deleted in the same run ??`tools/bench/c80_rowd_routeA.log` (47/5, rc=1, 112 s) and `tools/bench/c80_rowd_routeA_r2.log` (49/5, rc=1, 110 s). ?윟 **THE DECISIVE MEASUREMENT (`c80_rowd_routeA_r2.log:253-261`): immediately after the swapped connect and BEFORE any delete, net **7506** has **THREE** source terminals ??`RightShiftRegister #23868` (THE INTENDED NEW SOURCE), `FlatSequenceInnerTunnel #7468`, `RightShiftRegister #4334` (the OLD source) ??PD85 violations 0, and the loop border t1 `'Outgoing Handle'` went BARE ??**wire 7506** (`:244`). SO THE SWAPPED CALL DOES CONNECT: Pre-decided 116-A is NOT refuted and no new writer op is needed for the CONNECT.** ?뵶 What it does NOT do is REPLACE the old source: the net ends with three sources, hence `Wire.Is Broken?` **True** and `ExecState` 0, and deleting wire 7506 destroys the whole net (measured in both runs: #7488 and the border both go BARE). **Row D therefore needs ONE more step nobody has authorised ??remove the OLD `#4334` terminal from the net without destroying it ??and `Wire.Disconnect Terminal` 6370C0D is reported by labviewwiki as "(Not Implemented)" (c80-r2 review), which CONTRADICTS `docs/NAMES.md:1035`. That is a DESIGN DECISION, judgement's.** Arm A1 (delete-then-connect, Pre-decided 106's ordering) is DEAD and why is measured: with 7506 gone the op's `Wire.Terms[]` read raises `error 1055: Property Node in OpConnectFromWire_v0.vi`, `UID 2` 0, `wire_delta` 0, #7488 stays BARE (`c80_rowd_routeA_r2.log:119`). **ALSO MEASURED: Pre-decided 117's LITERAL uid is WRONG** ??`OpWireSource_v5` names the SHIFT REGISTER (`#23868`), never `WhileLoop #23032`, exactly as the delivered Row C read (`build_d1_m3a3_run2.log:182`). The mandatory failed-prediction review is **ANSWERED and disposed**: `archive/peer/2026-09-22-c80-rowd-routeA-swapped-r2.md` (claude/hypothesis, opus max, 689 s) ??it REFUTED this session's "Route A is dead" reading, named arm A2's own instrumentation as the fault, and its cheapest test was built and run in the same dispatch; a first dispatch at `-TimeoutSec 780` ended **TIMEOUT** and told us nothing (`archive/peer/2026-09-22-c80-rowd-routeA-swapped.md`, disposed as a non-result). Hygiene: LabVIEW restarted at phase [0] (34,160 ??30,684 ??31,281 handles), refs 8/8/0 live, **bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? BYTE-UNCHANGED at both ends and all four pins hold, both scratch copies deleted, `THE FILES THIS RUN LEFT ON DISK: []`.** No motor, no ASI, no camera; no op, verb or device built. PREVIOUS PURPOSE, unchanged and still true ???뵶 **CYCLE-69 MATERIAL, SECOND DISPATCH (the c79 failed-prediction review): NO LabVIEW WAS TOUCHED ??the instance left by cycle 68 (pid 30520) was NOT restarted, NOT opened, NOT read; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is byte-unchanged because nothing opened it, and NO op VI was built.** The brief's TASK 1 (the mandatory failed-prediction review of Pre-decided 111) ran and **ANSWERED**: `archive/peer/2026-09-22-c79-rowd-writer.md`, claude / role `hypothesis` / **opus effort max**, outcome `ANSWERED (554s)`, cost **$3.9166** (in 18 / out 40,945 / cache-create 236,321 / cache-read 944,181, 18 turns), `tools/bench/c79_rowd_writer_peer.log` `BGRUN END rc=0 after 554s`. **TASK 2 (build `OpFsInnerTunnelConnect_v0`) WAS NOT STARTED, BY THE BRIEF'S OWN HALT CONDITION** ??*"If the review names a concrete alternative route that works with existing ops, STOP and report it ??do not build"* ??and the review named one: **`OpConnectFromWire_v0` WITH THE ROLES SWAPPED** (`wire_uid=7506` + the `Wire.Terms[]` index of #7488 ??`Wire Source`; sink triple = `Diagram[19]` / `Nodes[21]` / `Terminals[1]`, the NEW loop's BARE `Outgoing Handle`), i.e. the Invoke sits on the BARE SOURCE terminal and receives the FSIT terminal as `Wire Source`. `tools/recipes/build_d1_m3a3.py`'s `WRITERS` table and gate W1 are UNCHANGED. What the review overturns: **`docs/NAMES.md:847`'s "6349C03 is invoked on the SINK" is labelled "labviewwiki, ADOPTED" and the wiki page does not say it** ??so `c78_rowd_writer.log:19`'s conclusion is an inference from our own one-donor lineage (`OpConnect2_v0 ??OpConnectNested_v0 ??_v1 ??_v2 ??OpConnectFromWire_v0`), not a fact about LabVIEW; the W1 census itself stands. What it CONFIRMS: ruled-out (a) survives (`FlatSequence` is `Generic ??GObject ??FlatSequence`, so no `Nodes[]` address for #7468/#7488 can exist); **`Tunnel.Inside Terminals[]` 6356000 / `Outside Terminal` 6356001 is DEAD BY CITATION** ??`FlatSequenceInnerTunnel` is NOT a `Tunnel`, so `OpTunnelRead_v0`'s cast can never address it, and its real properties are `Left Terminal` **1C3A9000** / `Right Terminal` **1C3A9001**; and no documented NI verb wires without a sink refnum (`Create Described Wire` is itself a `Terminal` method; `Node.Connect Wires` needs both ends to be `Node`s). ?뵶 **THE JUDGEMENT CALL "Row D gets a new writer op" IS NOW CONTESTED ON EVIDENCE** and, if a new op IS still needed, the review says the briefed shape is wrong twice over: donor should be `OpConnectNested_v2` (its source half already addresses a loop's own BORDER terminal), NOT `OpStopFromNode_v0` (source ladder anchored INSIDE the body), and **`OpConnectByUid`** (uid ??`UID to GObject Reference.vi` ??TMSC on a **Terminal** seed ??the Invoke's `reference`) is smaller than `OpFsInnerTunnelConnect_v0` ??no property node, no side selector, and it serves every future uid-addressed sink. **The review's own 4-step cheapest discriminating test (~2 min, a dated scratch COPY of the bed) was NOT RUN** ??it selects between three designs and the session was already halted; the gate it prescribes is `OpWireSource_v5`'s source-terminal OWNER == `WhileLoop #23032`, NEVER a wire delta, because a swapped connect could SILENTLY BRANCH wire 7506 (owner `#637`) and that passes a wire count while being a rule-1a computation change. PREVIOUS PURPOSE, unchanged and still true ???뵶 **CYCLE-69 MATERIAL (M3a-3b = ROW D): NO LabVIEW WAS TOUCHED, NOTHING WAS MUTATED, NO ARTEFACT EXISTS ??ROW D IS BLOCKED ON JUDGEMENT BECAUSE THE WRITER DOES NOT EXIST.** The LabVIEW instance left running by cycle 68 (pid 30520) was NOT opened, NOT restarted and NOT read; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is byte-unchanged (nothing opened it). **STEP 1 DELIVERED (Pre-decided 112):** `tools/logclass.py:is_recipe_build_log()` reads a log's OWN last `BGRUN START` **command** and counts it only when that command RAN a `tools/recipes/*.py`; `guard_cycle.py`'s `since` **budget set only** now uses it and `is_build_log` is untouched (guard_peer still arms the failed-prediction review off it). Self-test `tools/bench/selftest_logclass_recipebuild.py` **24 pass / 0 fail** (`tools/bench/c78_step1_selftest.log`, rc=0), covering the two named non-builds, the real recipe log, append/`cp`/prose/review/watchdog scoping, and guard_peer's own `selftest_guard_peer_jev.py` + `selftest_guard_peer_failre.py` re-run UNCHANGED. **MEASURED EFFECT (`tools/bench/c78_rowd_writer.log`, 5/0, rc=0): since the cycle-64 retrospective the budget set goes 20 logs / span 2.23 h / `overdue` TRUE ??2 logs / span 0.25 h / `overdue` FALSE**; the 2 are `build_d1_m3a3.log` and `build_d1_m3a3_run2.log`. **STEP 2 DELIVERED AS A FILE, NOT AS A RUN:** `tools/recipes/build_d1_m3a3.py` is re-cut **IN PLACE** to M3a-3b = Row D alone (bed as input, Row C carried as read-only precondition gate C0, sink by Pre-decided 109/111 via `OpFsInnerTunnelTerm_v0` uid 7468 ??LeftTerm #7488, delete-before-connect, acceptance = one source of ANY class + OLD #4334/#637 off the net on the ordered idempotent second pass, the `%`-format defect fixed by `_f()` and the `GetVIReference` `com_error` by `open_op()` = a NAMED gate failure with the raw error); pinned astcheck **10 gates PASS, `ASTCHECK OK`** (`tools/bench/c78_astcheck_m3a3b.log`, gate 10: 109 `%`-sites verified, 0 mismatch, 0 invalid). ?뵶 **IT WAS NOT RUN, AND THAT IS THE FINDING.** Its first gate W1 asks "is a writer bound to this row's sink kind?" and the answer is measured NO: `Terminal.Connect Wire` 6349C03 is invoked ON THE SINK TERMINAL (`docs/NAMES.md:245`), Row D's sink is a TERMINAL UID on a `FlatSequenceInnerTunnel`, and **all four label maps declaring method 6349C03 (`opconnectfromwire_v0`, `opconnectnested`, `opconnectnested_v1`, `opconnectnested_v2`) address their sink as (`index`, `index 2`, `index 3`) = (diagram, `Nodes[]`, `Terminals[]`); writers taking a UID-addressed sink = 0; `opfsinnertunnelterm_labels.json` declares NO `method` at all (`kind: IN` ??a READER)**. A `FlatSequence` is a `GObject`, never a `Node`, so no `Nodes[]` address for it exists or can exist. Running the recipe would have halted at W1 before opening LabVIEW, so it was not run and no decoy artefact was saved. Building that writer is a NEW OP and a design decision ??judgement's, not material's. PREVIOUS PURPOSE, unchanged and still true ????**CYCLE-68 MATERIAL MEASUREMENT DONE, NOTHING MUTATED ??`tools/bench/diag_c77_rowd_addr.log` (5 gates pass / 0 fail, rc=0, 144 s), read-only on a scratch COPY of the bed; the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` md5 `33ef524e?? is unchanged at both ends and all five pins hold.** LabVIEW restarted first (34,599 ??33,990; 34,941 after the reads; 33,996 at exit; refs 3 opened / 3 closed / 0 live). What the c76b review's cheapest test measured: (A) **`OpFsInnerTunnelTerm_v0` on uid 7468 RETURNS A TERMINAL REFERENCE with every error column empty ??`LeftTerm #7488` carries wire **7506**, `RightTerm #7471` wire 7448, self/cast echo `'FlatSequenceInnerTunnel'#7468`** (control read on FSIT #123 also answers), so the row-D SINK is addressable by uid today; (B) `find_node` MISSES on **#43914, #12938 AND #681** (173/173 diagrams, 635 nodes, 0 scan errors) ??the miss tracks the CLASS, not the owner and not #681; (B?? `owner_of(#681)` = **`'TopLevelDiagram' #536`**, NOT `'Diagram'`, and `diag_index(#681)` raises ??so **Pre-decided 107's route reads #681's table on a diagram that does not own it**, and #681 is absent from `Diagram #686`'s 27 `Nodes[]` rows ??the "how many entries carry wire 7506" question is UNREADABLE by that route, neither zero nor one; (C) `report_all('Diagram')` row 0 is still `TopLevelDiagram #536` (173 rows), #686 at idx 19; (D2, labelled secondary) exactly ONE terminal on `Diagram #686` carries wire 7506 ??`WhileLoop #637` `Nodes[4]` t10 `'Outgoing Handle'` is_source True, the wire's SOURCE side. c76b's disposition is written. PREVIOUS PURPOSE, unchanged and still true ????**M3a-3 ROW C IS DELIVERED (run 2, 26 gates pass / 2 fail ??both fails are the PRE-DECIDED Row-D deferral): `claudeDev\D1_s3b_m3a3_20260922_081056.vi`, md5 `33ef524e0b6b193a158c9221474c68e3`, 306,951 B** (`tools/bench/build_d1_m3a3_run2.log`). `Global #7202 'Global motor pos.vi'` t0 `'Focus position'` now reads the NEW loop's position register: sink net **25231** has exactly ONE source terminal of ANY class, `RightShiftRegister #23895`, PD85 violations 0, asserted on the ordered idempotent second pass (`wire_delta` 0); the OLD `#4256` is OFF the net. Junk `Invoke` purged (634??35??34). Refs 8/8/0 live; handles 34,592 ??30,689 (restart) ??33,833; all four md5 pins and the M3a-2 input unchanged. ?뵶 **ROW D IS DEFERRED TO M3a-3b ??a FAILED PREDICTION, reviewed** (`archive/peer/2026-09-22-c75-m3a3-run1-failpred.md`, ANSWERED, disposed): wire **7506 was NOT deleted** and nothing was improvised. ?좑툘 **RUN 1's ARTEFACT `claudeDev\D1_s3b_m3a3_20260922_075611.vi` (md5 `2461a749??) IS REJECTED AND MUST NOT BE USED AS A BED** ??its delete ran but the rebuild raised (`OpConnectNested_v2.vi` is not on disk), so `Global #7202` t0 is BARE = a dropped consumer; the rename to `_REJECTED_?? was refused by the permission layer, so it still carries the clean stage name. PREVIOUS PURPOSE, unchanged and still true ????**CYCLE-65 MATERIAL MEASUREMENT DONE, NOTHING MUTATED** ??`tools/bench/diag_c75_m3a3_rows.log` (6 gates pass / 0 fail, rc=0, 147 s) + `tools/bench/diag_c75b_loopterms.log` (5/0, rc=0, 4 s), both read-only on scratch COPIES of `D1_s3b_m3a2_20260922_023029.vi`; its md5 `3842f5e6?? is unchanged at both ends and all four STATUS pins hold. LabVIEW was RESTARTED first (42,570 ??34,322 handles; 34,336 at exit; refs opened==closed on both runs). PREVIOUS PURPOSE, unchanged and still true ????**M3a-2 IS DELIVERED AND INDEPENDENTLY VERIFIED** (15 gates pass / 0 fail) ??`claudeDev\D1_s3b_m3a2_20260922_023029.vi`, md5 `3842f5e6f128226235dc78353f26ef44`, **broken BY DESIGN** (`ExecState` 0; its missing rows belong to the next stage), never run and never cold-loaded. ?좑툘 **LabVIEW WAS LEFT RUNNING at 42,297 handles and MUST BE RESTARTED before the next batch.**
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

I read the recipe, the c83 logs, the plan's Pre-decided entries, the toolkit sources and the archive. Findings below; every one carries a file and line.

---

# PRIOR-ART REVIEW — D-3 of M3a-3b (`build_d1_m3a3b_d3.py`)

## PART A — THE DIRECTION

### A1 SETTLED ALREADY — the delete-before-connect ordering is a live Pre-decided entry that this recipe reverses without citing it

`docs/cycle27-plan.md:3294-3307` (**Pre-decided 106**, ADDED 2026-09-22, cycle 65):

> *"`connect_from_wire` into an **already-wired sink** is a measured **silent no-op** on this very VI … Therefore, in M3a-3: **the delete precedes every row** (mandatory, measured, older than cycle 62's re-cut)"*

and `docs/cycle27-plan.md:3364-3366` (**Pre-decided 111**, Row D's own acceptance clause):

> *"Acceptance is Pre-decided 106 unchanged and is **not** relaxed by this entry: the delete precedes the connect (an already-wired sink is a measured silent no-op)"*

D-3 does the opposite — `tools/recipes/build_d1_m3a3b_d3.py:54` *"on dated scratch COPIES of the bed with wire 7506 LEFT ALIVE"*, and `:63` *"wire 7506 is never deleted anywhere"*. The recipe's docstring (`:6-11`) explains why delete-first is now impossible, but nowhere does it name 106 or 111, and the plan document still carries both as current. `STATUS.md`'s own `## NEXT` still reads *"THEN D-3: Row D on the bed — **delete 7506**, connect `#23868`'s OUTER into `#7488`"*.

This is not an argument that D-3 is wrong. It is that D-3 is executing against a written decision that says the opposite, and the release path is to amend 106/111 in `docs/cycle27-plan.md` with c83's `error 1055` evidence — not to run past them silently.

### A2 REFUTED ALREADY — "wiring onto a wired input replaces the wire" is contradicted by this project's own measurement of that act, twice, and neither outcome was a clean replacement

The recipe's central premise, `tools/recipes/build_d1_m3a3b_d3.py:10-11`:

> *"in LabVIEW's editor, wiring a new source onto an input that is already wired REPLACES the existing wire. That is what this file measures."*

Against it:

1. **`docs/keystone-op-spec.md:444-446`** — the original measurement of `Terminal.Connect Wire` 6349C03 through `OpConnect_v0` (§28, 2026-09-06): *"Earlier 'no wire, VI breaks' runs targeted IA534, whose array input is already wired in GUIBENCH_v0: **Connect Wire on a wired sink re-routes and breaks** — only wire unwired sinks."* That is a measured outcome on an already-wired sink, and it is break, not replace.

2. **`archive/2026-09-16-status-gate-a1-delete-regression.md:94-97`** — a disposed peer review (`archive/peer/2026-09-16-ownerchain-b2-b3-failed-prediction.md`) verified against our own files, on a recipe that *"wired **four** already-wired sinks"*: *"a branch should PRESERVE the wire uid, so 1208 was an uncontrolled replacement, and 1444 is most likely a source-less fragment."* An uncontrolled replacement plus a source-less fragment — not the clean single-source net GATE S(a) expects.

Does it still apply? Both were measured on index-addressed sinks through `OpConnect_v0` / the A1 recipe, not on a uid-addressed `FlatSequenceInnerTunnel` `LeftTerm`. Nothing on file claims the addressing route changes the *method's* behaviour once it holds a terminal reference — so refuting this costs showing, in writing, why a uid-resolved reference makes 6349C03 behave differently from an index-resolved one on the same class of already-wired sink.

### A3 CONTRADICTED — the premise conflicts with the docstring of the wrapper family this recipe imports

`tools/gscript.py:2522-2523`, in `connect_terminals`, the wrapper for the very method under test:

> *"an already-wired source is BRANCHED (wire count unchanged, ExecState 0→1); an already-wired SINK is **not safe** (LabVIEW re-routes and the VI breaks) — wire only unwired sinks."*

Same sentence, independently, in the skill: `.claude/skills/labview-automation/references/vi-scripting.md:603` and `:627`. The recipe imports `gscript` at `:119` and its "WHAT ALREADY EXISTS" audit (`:13-35`) walks six source files without reaching this line.

Second contradiction, internal to the prior art: A2's two records disagree with **each other** — `docs/cycle27-plan.md:3295-3300` says the same act is a **silent no-op** (nothing happens), while `docs/keystone-op-spec.md:445` says it **re-routes and breaks**. Whichever is right, "REPLACES" is a third outcome that neither measurement produced. This matters concretely for GATE S(d2) (`build_d1_m3a3b_d3.py:579-581`): if the displaced wire survives as the source-less fragment of `…gate-a1-delete-regression.md:97`, the diagram-wide broken-wire count goes **up**, and (d2) is the gate that catches it — so the gate is well chosen, but the plan's expectation of it is not.

### A4 UNREAD EVIDENCE

- **`docs/keystone-op-spec.md:438-447`** — §28, where the already-wired-sink rule was actually *measured*, with the terminal-by-terminal outcomes. Cited nowhere in the recipe, nowhere in the review plan `tools/bench/priorart_plan_c84_d3.md`.
- **`tools/bench/build_d1_m3a1.log:1174`** and its sibling call line `:1147` — the four on-this-VI measurements of the exact act (see B4). The recipe's audit block (`:13-35`) imports `build_d1_m3a1` for helpers (`:31-32`) but never reads its log.
- **`archive/2026-09-16-status-gate-a1-delete-regression.md:94-97`** — the only record of what happened when four already-wired sinks were actually written.

Process note, not a slug: the mandatory failed-prediction review of the c83 log is **still in flight** — `tools/bench/peer_c84_replace.log:1` shows `BGRUN START 2026-09-22 13:53:17 … -Slug c84-replace-vs-branch` with no `BGRUN END` line and no file in `archive/peer/`. Its task (`tools/bench/task_c84_replace_vs_branch.md:35-48`) asks precisely claim 3. `guard_peer.py` should refuse the build until it lands; if it TIMEOUTs it told you nothing and must be re-dispatched.

---

## PART B — THE ARTEFACT

### B1 ALREADY BUILT — **no.** The op does not exist on disk

`claudeDev` holds `OpFsInnerTunnelConnect_v0.vi` and no `_v1`; there is no `OpConnectNested_v2.vi` either (directory listing of `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Op*.vi`, 111 files). c83's swapped copy was a scratch and was deleted in-run — `tools/bench/diag_c83_connect2x2_r2.log:123` *"H4 scratch deleted: C83bSWAP_20260922_133523.vi"*. No Row D artefact exists (`STATUS.md`: *"M3a-3b (ROW D) IS NOT DELIVERED — NO FILE"*). **No finding.**

### B2 ALREADY FAILED — the *construction* failed once, and the recipe already carries the fix

`tools/bench/diag_c83_connect2x2_r2.log:35-46`: run 1's swapped copy read `ExecState` 0; run 2 fixed it by re-branching the two other consumers of the deleted nets (`#241.reference`, `#187.reference`) and reached `ExecState` 1 with Remove Bad Wires removing 0. `build_d1_m3a3b_d3.py:405-409` reproduces exactly that re-branch loop. **No finding** — the cause is addressed, not repeated.

### B3 HELPER EXISTS — the "broken-wire count this project had no reader for" is already written, twice

`build_d1_m3a3b_d3.py:66-68` claims the count is *"the one measurement this project had no reader for"*, and `:224-234` implements `bad_wire_count` as `count("Wire")` → `remove_bad_wires_scripted` → difference.

That construction is already on disk: **`tools/bench/broken_probe2.py:12`** — `w0 = g.count(T, "Wire"); g.remove_bad_wires_scripted(T); print("… wires", w0, "->", g.count(T, "Wire"), "ExecState", g.exec_state(T))` — and is the stated method of **`tools/bench/bool_wire_probe.py:12`** (*"wire count and ExecState immediately after the wire, and again after remove_bad_wires"*).

Scope, stated precisely so this costs nothing it shouldn't: neither is a reusable helper, and the recipe's mutate-on-a-throwaway-copy discipline (`:69-72`) is a genuine improvement over both. What is wrong is the novelty claim at `:66-68`, and the cheap release is to cite `broken_probe2.py:12` there. Related caution the recipe does honour: `docs/toolkit-capabilities.md:68` — *"Do not cite RBW-survival as evidence a wire is good"* — the recipe uses a count delta, not uid survival, so that one does not bite.

### B4 ALREADY MEASURED — the cell the recipe calls "the measurement nobody has run" has been run four times on this VI

`build_d1_m3a3b_d3.py:9-10`: *"THE CELL NEVER RUN IS: Invoke on the SINK terminal with the wire ALIVE."*

`tools/bench/build_d1_m3a1.log:1174` (repeated at `:1875`, `:2593`, `:3311` — quoted as such in `docs/cycle27-plan.md:3296-3298`):

> *"THE SIXTH ROW: sink terminal t1 of CaseStructure #12589 carries wire 9113 ; CaseStructure WIRED-terminal count 3 -> 3 ; `Wire.Is Broken?` False ; **LANDED False**"*

and the call that produced it, `tools/bench/build_d1_m3a1.log:1147`:

> *"connect_from_wire(wire=23955, wire_term=0, sink_diag=48, sink_node=47, sink_term=1) -> {'wire_delta': 1, … 'UID 2': 9113, 'Is Broken?': False, …}"*

That is the same method (6349C03), the same op family (`OpConnectFromWire_v0`, whose sink is the index triple and therefore the Invoke's own object — `docs/toolkit-capabilities.md:70`), onto a sink that was **already wired**, with the source handed to `Wire Source` from a wire uid. The sink kept its OLD wire 9113, the readback echoed the old wire, and a stray wire appeared (`wire_delta 1`). Not a replacement.

The differences from D-3's cell are real and worth naming, because they are what a refutation must turn on: the sink there was a `CaseStructure`/`SelectorTunnel` terminal addressed by **index triple**, here it is a `FlatSequenceInnerTunnel` `LeftTerm` addressed by **uid** through `UID to GObject Reference.vi` → TMSC → `Left Terminal` 1C3A9000. What is *not* different is the thing under test: 6349C03 invoked on an already-wired sink terminal.

Note also `docs/toolkit-capabilities.md:70`, T2a/T2c2 — the one prior time this op wrote a wire whose source was owned by a `FlatSequenceInnerTunnel` (`#5818`, w5812), the created wire read **`Is Broken? TRUE`** with two terminals reporting `Is Source? TRUE`. GATE S(a)+(d1) is the right pair of gates for that failure mode; it is not an unobserved one.

---

## What would release this

Nothing here says D-3 cannot work, and two of the six findings (B1, B2) came back clean. What the citations block is running it while the file asserts the cell is unmeasured and the premise settled. The cheapest releases:

- **A1** → `FIXED:` amending `docs/cycle27-plan.md` Pre-decided 106/111 with c83's `error 1055` evidence that delete-first is unexecutable for this sink.
- **A2 / A3** → `REFUTED:` showing in writing why a uid-resolved terminal reference changes 6349C03's behaviour on a wired sink, or `FIXED:` restating the premise as the hypothesis under test rather than as editor fact.
- **B4** → `FIXED:` citing `build_d1_m3a1.log:1174` in the docstring and stating what makes this cell different (uid-addressed FSIT sink), which is a legitimate difference and the actual reason to run it.
- **B3** → `FIXED:` one citation at `:66-68`.

```
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
```

## Sources

(extract from answer)

## What was done with it

All six verdicts were ACCEPTED — none is refuted. Two of the six (A2/B4) also changed what this dispatch
EXPECTS: the prior art predicts a silent no-op or a merge, not a replacement, and GATE S (a) and (d) are the
gates that catch each. The cell is still run, because the one genuine difference — a uid-addressed
`FlatSequenceInnerTunnel` `LeftTerm` instead of an index-addressed structure terminal — is unmeasured, and
because the judgement session's brief pre-decided that the measurement is taken and the result reported,
never acted on. Dispositions, each citing the change:

FIXED: settled-already - docs/cycle27-plan.md:3372 - new entry 111a records that 106/111's delete-first
ordering is UNEXECUTABLE for Row D's sink (c83's `error 1055` on `#7468` once 7506 is gone), that 106's
acceptance is untouched, and that the c84 hypothesis review's competing cause for that 1055
(`remove_bad_wires_scripted` deleting the tunnel) is OPEN and judgement's - so the entries are no longer run
past in silence.

FIXED: refuted-already - tools/recipes/build_d1_m3a3b_d3.py:12 - the "wiring onto a wired input REPLACES"
premise is restated as the HYPOTHESIS UNDER TEST, with `docs/keystone-op-spec.md:444-446` ("re-routes and
breaks"), `tools/bench/build_d1_m3a1.log:1174` (silent no-op, four times) and
`archive/2026-09-16-status-gate-a1-delete-regression.md:94-97` (uncontrolled replacement + source-less
fragment) quoted against it, and with the review's own falsification table printed per cell.

FIXED: contradicted - tools/recipes/build_d1_m3a3b_d3.py:25 - `tools/gscript.py:2522-2523` and the skill's
`references/vi-scripting.md:603`/`:627` ("an already-wired SINK is not safe") are quoted in the docstring,
and the internal disagreement between "silent no-op" and "re-routes and breaks" is named, with the note that
"REPLACES" is a third outcome neither measurement produced.

FIXED: unread-evidence - tools/recipes/build_d1_m3a3b_d3.py:63 - the audit block gains an explicit entry for
the five files it did not reach (`docs/keystone-op-spec.md:438-447`, `tools/bench/build_d1_m3a1.log:1147`
and `:1174`, `archive/2026-09-16-status-gate-a1-delete-regression.md:94-97`, `tools/gscript.py:2522-2523`,
`tools/bench/broken_probe2.py:12`), each quoted where it bites.

FIXED: helper-exists - tools/recipes/build_d1_m3a3b_d3.py:102 - the novelty claim is withdrawn and replaced
by a citation of `tools/bench/broken_probe2.py:12` and `tools/bench/bool_wire_probe.py:12`; what this file
claims now is only the mutate-on-a-throwaway discipline. The same paragraph records the two caveats the
review's neighbourhood raises - `docs/cycle27-plan.md:1860-1862` refusing Remove Bad Wires on a deliverable
as a rule-1a hazard, and `docs/toolkit-capabilities.md:68` forbidding RBW-survival as evidence - and adds
NON-MUTATING companions (Wire census before/after, `wire_delta`, `ExecState` bracket, whether wire 7506
survives) so the gate is never the only reading.

FIXED: already-measured - tools/recipes/build_d1_m3a3b_d3.py:18 - "the cell never run" is withdrawn.
`tools/bench/build_d1_m3a1.log:1147`/`:1174` is quoted as the same act run four times on this very VI, and
the docstring now states exactly what is different (uid-addressed FSIT `LeftTerm` via
`UID to GObject Reference.vi` -> TMSC -> `Left Terminal` 1C3A9000, versus an index triple) and that this
difference is the only honest reason to fire the cell.

Process note answered: the failed-prediction review the reviewer saw in flight LANDED —
`archive/peer/2026-09-22-c84-replace-vs-branch.md`, claude / role `hypothesis` / opus max, outcome ANSWERED
(656 s, $4.9020), `tools/bench/peer_c84_replace.log` `BGRUN END rc=0 after 657s`. It REFUTES the replacement
claim on the same evidence this review cites plus NI's own Idea Exchange ("the wires merged instead of
switched"), and its §3 alternative cause for the 1055 is recorded in `docs/cycle27-plan.md:3372` as OPEN for
judgement, NOT acted on here — the brief forbids re-opening the route.
