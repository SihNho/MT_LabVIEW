# priorart-fstunnel-reader

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.3903  in 38 / out 37889 / cache-create 301390 / cache-read 2857971  (520s, 33 turn(s))
- **date:** 2026-09-18 03:13:17
- **outcome:** ANSWERED (524s)
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
# PLAN under review: `OpFsTunnelTerm_v0.vi` ??the UID-addressed flat-sequence tunnel reader

Recipe: `tools/recipes/build_opfstunnelterm_v0.py` (written, not yet run). Cycle 20 step 2,
`docs/cycle20-plan.md:36-48`.

## What is built, exactly

    IN  : vi path + the UID of a FlatSequenceOuterTunnel
    OUT : OuterTerminal uid, InnerTerminal uid, and for the OUTER terminal its `Is Source?`, its
          CONNECTED WIRE uid (the hop that crosses the flat-sequence border) and its OWNER class + uid

Chain: `uid -> UID to GObject Reference.vi -> To More Specific Class(FlatSequenceOuterTunnel) ->
FlatSequenceOuterTunnel[Outer Terminal 3195B800 | Inner Terminal 3195B801] -> Terminal{Is Source? /
Connected Wire -> UID / Owner -> Class Name / Owner -> cast -> UID}`.

## Why it exists

`docs/vi-server-ids.json:142` records the gap in this project's own words: *"_NOT_YET_MEASURED: A LIVE READ of
any of these properties on a real instance. Attaching an id to a class proves membership, NOT that a runtime
reference casts to that class ... That read needs UID -> To More Specific Class(FlatSequence*Tunnel) -> property
node, i.e. a new op."* The cycle-19 backward walk from the startup ASI move stopped at hop 1 on
`FlatSequenceOuterTunnel uid 43605` (`tools/bench/probe_flatseq_walk_run2.log:82-83`) because no reader can
address that object.

## What is reused rather than rebuilt (the audit done before writing the recipe)

* property ids MEASURED, not re-derived: `3195B800 OuterTerminal`, `3195B801 InnerTerminal`
  (`tools/bench/probe_flatseq_outer.log:20-22`), `632A813 GObject.UID`, `634A000 Terminal.Connected Wire`,
  `6327806 Generic.Owner` (`docs/vi-server-ids.json:61-63,137-139`).
* DONOR `OpWireSource_v5.vi`: its BACK HALF (Terminal -> Is Source? / Connected Wire -> UID / Owner -> Class Name
  / Owner -> cast -> UID) is exactly this op's output set and is kept unchanged, with its existing indicator
  labels (`tools/bench/opwiresource_v5_labels.json`). Only the FRONT changes: `TMSC(Wire) -> Wire.Terms[] ->
  Index Array` is deleted and replaced by `TMSC(FlatSequenceOuterTunnel) -> OuterTerminal`.
* THE SEED for the cast: no class-specifier constant, no GUI, no NI example. The donor's two casts are already
  typed by refnum CONTROLS (`seedW`/`seedG` = "reference 2"/"reference 3"); the FSOT-typed control is made the
  way `tools/recipes/build_oploopcast_v0.py:201-202` makes a ForLoop-typed one ??`create_control` on a
  FlatSequenceOuterTunnel property node's `reference` INPUT takes that terminal's type.
* gscript helpers unchanged: `node_terms_uid`, `report_all/uids/count`, `delete_object`,
  `remove_bad_wires_scripted`, `build_property`, `create_control`, `create_indicator`, `wire`, `wire_control`,
  `set_auto_error_handling`, `save`, `exec_state`, `tunnels`.
* the known-good fixture (`LoopTunnel #28343 -> Max Trans Pos.vi 쨌 'Magnet position output'`,
  `docs/frame-loop-wire-graph.md:264`) is resolved with the EXISTING `gscript.tunnels()` + `OpWireSource_v5`,
  not with the new op ??and is also used as a DELIBERATE BAD INPUT for it (a LoopTunnel must be refused by a
  FlatSequenceOuterTunnel cast).
* `archive/peer/` was searched first (cycle-20 Pre-decided 5). The only prior-art review of a tunnel reader is
  `2026-09-17-priorart-tunnelsource-onehop.md`; all five of its findings were accepted and disposed, and its
  closing paragraph names THIS gap as still open.

## Prediction contract (each line machine-checked in the recipe)

* I1 IDENTITY measured first, because getting it wrong invalidates the run: for BOTH the V6 working copy and the
  3StateClamping ORIGINAL, whether uid 28343 is a LoopTunnel, whether 43605 is a FlatSequenceOuterTunnel and
  whether 44036 is a SubVI (STATUS.md:59-61 records the census keyed to the ORIGINAL and the node/terminal cache
  keyed to the COPY).
* I2 the fixture resolves to `Max Trans Pos.vi 쨌 Magnet position output` through the existing ops.
* B1-B5 donor copy legal; front section deleted and every back-half `reference` sink BARE before anything is
  wired; exactly one new CONTROL from `create_control`; the FSOT property node ACCEPTS the cast output
  (ExecState 1 ??if the seed did not type the cast this is where it shows); ExecState 1 before the single save
  and again cold in a fresh LabVIEW.
* L1 LIVE READ on uid 43605 returns a non-zero OuterTerminal uid, a connected wire and an owner, with no error.
* L2/L3 REFUSALS: uid 28343 (a LoopTunnel) and uid 999999 (nonexistent) are both refused.
* L4 the backward walk from d10 uid 44036 T[8] (wire 44089) advances PAST the border that stopped cycle 19; hop
  count recorded.
* I0/L5 both originals' md5 before AND after, handle count before and after, one scratch VI created and deleted
  in the same run, no motor, no serial port, no camera (cycle-20 Pre-decided 1).

## The question for this review

Has this reader ??or this composition, or this seed trick applied to a flat-sequence class ??already been built,
already been measured, or already FAILED here under another name? And is any fact cited above contradicted by
our own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??`archive/2026-09-18-status-cycle19-flatseq.md` (latest) + the `archive/2026-09-1[678]-status-*.md` set. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.
## START HERE
1. **Cycle plan = `docs/cycle20-plan.md`** (P1 plan `docs/motor-limit-assurance-plan.md` **짠A.1**; master
   `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`; **`-Dual` = FAILED-PREDICTION reviews ONLY** (CLAUDE.md:554), never `-Kind fact` / prose / ingest ??it doubles cost (opus arm ??1.86/call).
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌
   `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# Cycle-19's 4 probes held it 01:35-02:08 and cycle-17's census 23:29-23:53; both RELEASED, both READ-ONLY ??
# both originals' md5 unchanged before AND after every run (3state c39f36e0?? V6 2a78e17c??, nothing saved, no
# motor, no serial port, one scratch VI per run deleted in the same run. Verbatim ??the cycle19-flatseq archive 짠4.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py`
inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state
change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies
`tools/bench/camera_contract.py`. **No beads on the rig.**
?뵶 **P1 IS STRICTER THAN THE RIG STATE AND P1 WINS:** in P1 (see `## NEXT`) **no motor moves and no motor port is
opened for writing** ??`motor_gate.py --execute` is not to be called at all.
?넅 **SAFE MOTION ENVELOPE (user, 2026-09-17 ??says what is SAFE, not when motors are allowed; motors ARE allowed
while assembled INSIDE it, conditional on it being really enforced as refusing code):** ASI z free 쨌 ASI x/y
**never home/origin, ??.0 mm from `tools/bench/motor_anchor.json`** 쨌 PI magnet **0??9 mm only** (`Max Trans Pos`
= 40.94 is a **coerce** in the original and `TMX 52` ??**the controller protects nothing**; our scripts bypass the
coerce). ??`tools/motor_gate.py` = the ONE gateway, 70/70 self-test, default-deny; first live PI + ASI moves
passed; rotor transmit **NOT built** ??`archive/2026-09-17-status-motor-gate-live-moves.md`.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand
?넅 **CYCLE 19 CLOSED ??measurement and a re-design; NOTHING WAS BUILT.** Check A's method is now
`docs/motor-limit-assurance-plan.md` **짠A.1** (43-93), written after the prior-art review
`archive/peer/2026-09-18-priorart-check-a-wiring.md` (01:12:34). Its four `FIXED:` lines (:365-368) **VALIDATE** ??
`_released`=True, 4/4 slugs, 0 rejected; a SAME-DAY fix counts because that review carries a date **and a time**.
**The launch still REFUSES**, for an unrelated reason: `motor_wiring_check` (under `tools/`, never written) is not on disk, so the
release cannot be stamped to any bytes ??it allows on the first run after the file exists. Gate text verbatim + a
3-case negative proof (all REFUSED, plus a releasing control), 10/10: `tools/bench/c19_close_release_probe.log`.
?넅 **MEASURED (4 read-only runs): THE FLAT SEQUENCE IS NOT A BARRIER ??IT IS A MISSING READER** (`Diagram.Nodes[]`
addressing is what blocks; the stop objects sit outside `Nodes[]` yet are Traverse-visible and UID-addressable;
tunnel property ids ??`docs/vi-server-ids.json`) 쨌 **the motion subVIs hold NO limiting construct** and
`Max Trans Pos.vi` has no nodes at all 쨌 **the census's 97/43 sites are keyed to the 3State ORIGINAL while every
cached node/terminal index is keyed to the V6 COPY** 쨌 ?좑툘 **still no LIVE read.** Numbers, text and logs ??
**`archive/2026-09-18-status-cycle19-flatseq.md` 짠1**; cycle 18 verbatim in its **짠2** (stop record + launch gate
BUILT/PROVEN 쨌 `device-failed` DISCHARGED 쨌 census CLOSED 97/43 쨌 `ASI_adjust focus-subvi.vi` is called on
diagram 43 = the FRAME LOOP). **THE GAP stands: 174 ops, 123 recipes, 235 peers ??zero runnable experimental VIs.**

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
32. ?뵶?뵶 **outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive ??the work stops for a re-plan with the USER.** Not answerable by a device. Stands above everything else here.
38. ?뵶 D1 route-B run 3 changed NOTHING (63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0); `SR_QUEUE_AUTHORISED` / `TEMP_SINK_AUTHORISED` = False. **`docs/d1-route-b-plan.md` 짠11/짠11a**; archive 짠3.
39. ?뵶 `VI.Get Errors` 452 NOT built ??prior-art stopped it on `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED.
41. ?뵶 **judgement only ??the stall watchdog's liveness test.** Both arms (ANSWERED) REFUSE "false positive"; remedy not built. `archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`.
42. ?좑툘 39 archived reviews undisposed (`doc_lint` L6 FAIL standalone, pre-2026-09-15 legacy; under `audit_cycle` L6 defers to **A4**, which sees 14 of 80 in its 24 h window). ?좑툘 **`audit_cycle` A2/A3 are SELF-REFERENTIAL** ??they failed cycle 19 naming only `c19_audit*.log`, the audit's own rc=1 output; same family as "review logs are evidence, never the thing under test" (CLAUDE.md:487-489). Not yet fixed.
43. ??**FIXED 2026-09-18 02:47 (cycle 20 step 1).** `guard_cycle.fixed_claim()` (new) reads the newest review's claim on the recipe BEFORE the mtime rule: valid `FIXED:` ??allow, claim that fails 449(a/b/c) ??**REFUSE**, no claim ??unchanged. **T1?밫6 PASS + B1 REFUSED / B2 ALLOWED** (verbatim gate text) ??`tools/bench/selftest_guard_cycle_fixed.log`; no regression: `selftest_guard_cycle_rerun` 4/4 incl. C4.
47. ?뵶 **JUDGEMENT ??cycle-19's audit `c19_audit2.log` A1/A2/A3: the remedy is NOT a `logclass` entry.** Dual review both ANSWERED (`archive/peer/2026-09-18-c20-audit-a1-motorgate-{codex,opus}.md`, disposed). MEASURED: `tools/bgrun.py` has **no `BGRUN_LOG`** (0 hits) while `audit_cycle.py:186-197` reads it ??the own-log exemption is **unreachable code**; `motor_gate.log` carries live `SENT rc=` records, so excluding it by filename would **hide execution evidence**. opus reads this as `device-failed` (threshold 1).
44+45. ??**RETIRED 2026-09-18, both answered:** the check-A prior-art review is disposed and its release VALIDATES
   (only the unwritten `motor_wiring_check` (under `tools/`, never written) keeps the launch gate refusing), and the UID-addressed tunnel reader IS to be built ??`docs/cycle20-plan.md` step 2.
46. ?좑툘 **USER-FACING FACT, not a build task: `SetCommand_signed.vi` DOES NOT EXIST ANYWHERE ON DISK.** Glob `**/SetCommand*.vi`
   under `G:\??MinLab` ??**0 hits**; `??LabVIEW 2026\instr.lib\Autonics Motor\` holds only `Close.vi`, `Configure.vi`, `SetCommand.vi`. CLAUDE.md rule 1b says the new VI uses it.

## NEXT
**CYCLE 20 STARTS HERE ??`docs/cycle20-plan.md` (`status: current`) + its `## Pre-decided`. STEP 1: fix
`guard_cycle.py:379` to implement CLAUDE.md:449(b) and make the self-test WRITE
`tools/bench/selftest_guard_cycle_fixed.log` ??T1?밫6 PASS plus a deliberate-bad-input refusal. STEP 2: the
UID-addressed tunnel reader, proven by a LIVE read on an instance.** Check A is CYCLE 21, in 짠A.1's order
(ORIGINAL's own sweep ??forward reachability from the 3 coerces ??control **Data-Entry ranges** ??the 3
comparator mutation negatives); 짠A.1 is SETTLED ??do not redesign it or re-open its release. ?좑툘 `prior_art_review`
REFUSES without `--recipe`; a non-`novel` verdict arms the launch gate; `CYCLE_GUARD_OFF` is never the answer.

?뵶 **THE RUNNER'S ORDERS (user, 2026-09-17 23:4x): "紐⑦꽣 ?묐룞 泥댄겕 ?꾧퉴吏??紐⑤뱺 ?몄뀡 ?뚮젮蹂?寃? ?댄썑 ?닿? ?먮━??
?덈뒗 ?곹솴?먯꽌 紐⑦꽣 ?곹븳 ?섑븳 泥댄겕 寃利? ?댄썑 ?섎㉧吏???섎꽕??猷⑦봽 ?????덈룄濡?.**
**P1 (runner, unattended, NOW):** `docs/motor-limit-assurance-plan.md` 짠D order ??census ????A ??B ??broken-VI
proof ??C + record hook ??one step per cycle, material sub-sessions do the work. **NO MOTOR MAY MOVE AND NO MOTOR
PORT MAY BE OPENED FOR WRITING in P1** (`motor_gate.py --execute` is not to be called; stubs only); LabVIEW +
camera allowed (rig 議곕┰). Takes precedence over OPEN 41 and the D1 build.
**P1 ENDS when the only work left needs a real motor or the user** (or the failure budget is spent) ??that cycle
writes a line starting `STOP` in this file's first 60 lines. **P2 (USER PRESENT):** live limit verification.
**P3:** the user restarts the runner for the rest. 짠D's checker `.claude/agents/motor-limit-checker.md` is
WRITTEN; its tools, the hash-record gate, the record-write hook and the broken-VI proof are **NOT BUILT**.
?뱥 **Each cycle's closing session writes the NEXT `docs/cycle<N>-plan.md` with its `## Pre-decided` and flips its
own off `status: current`.** `docs/cycle15-plan.md` stays `paused`; D1/route-B state:
`archive/2026-09-18-status-cycle1-census.md` 짠4. **OPEN 32 stands above all.**

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled this session (as in the 2026-09-17 prior-art dispatch), so the review is delivered here in full — which is what `peer.ps1` archives.

**4 findings, 0 `novel`.** The *core* is genuinely unbuilt — no op casts to either flat-sequence tunnel class and the FSOT cast has executed zero times here. What is already in our files and did not make it into the contract: the op reads the sibling class that owns 1 of the 15 measured non-node crossings; the accepted dual review's direction test is absent and L4 would score a *non-advancing* hop as a crossing; the L4 walk re-implements a helper §A.1 item 5 names, dropping that helper's guard; and the `owner uid` half of the OUT is already measured to fail silently at a flat-sequence frame.

---

# PART A — THE DIRECTION

## A1 — cleared, the direction is authorised, not settled against
`docs/motor-limit-assurance-plan.md:66-67` (§A.1 item 3, SETTLED per STATUS): check A *"needs one new primitive, the **UID-addressed tunnel reader** (`UID → TMSC(FlatSequence*Tunnel) → Outer/Inner terminal`), which is built and proven on a live instance BEFORE check A runs."* `docs/cycle20-plan.md:36-48` makes it step 2. No slug.

## A2 — cleared, no surviving refutation; the outer read is what the reviewers prescribed
`archive/peer/2026-09-18-walk-run2-flatseq-crossing-codex.md:94-103` prescribes exactly `internal wire → source Terminal → owner FlatSequenceOuterTunnel → Outer Terminal (3195B800) → Connected Wire (634A000) → that wire's source`, and `:141-153` says *"Do not build the inner-tunnel reader first."* No slug.

## A3 `contradicted` — the op reads the class that owns ONE of fifteen measured crossings, while both documents it cites say `FlatSequence*Tunnel`

- The artifact is `FlatSequenceOuterTunnel`-only: `FSOT = "VI Server:FlatSequenceOuterTunnel"` (`tools/recipes/build_opfstunnelterm_v0.py:103`), one cast (`:418`, `:449`), and gate L2 *requires* every non-FSOT uid to be REFUSED (`:579-582`).
- `docs/cycle20-plan.md:39` — step 2 is *"`UID → TMSC(FlatSequence*Tunnel) → OuterTerminal / InnerTerminal` **(and the inner-tunnel `LeftTerm` / `RightTerm`)**"*; `docs/motor-limit-assurance-plan.md:66-67` likewise `FlatSequence*Tunnel`.
- The measured population: `docs/d1-build-plan.md:735-738` — of the 18 rows whose outer wire's single source terminal is a non-node object, **14 are `FlatSequenceInnerTunnel`**, 2 `LeftShiftRegister`, 1 `SubVI`, 1 *does not advance*. `docs/vi-server-ids.json:141` — on the same V6 copy, FSIT **518** vs FSOT **58**. And `tools/bench/probe_flatseq_outer.log:24` is the proof this op cannot reach them: `1C3A9000` REFUSED 1077 on the outer class.

**Scope:** covers the claim that this op is *the* primitive and that step 2's "Done when" is met. It does NOT say the FSOT reader is wrong, unnecessary, or that both classes must ship in one build.

## A4 `unread-evidence` — the dual review's direction test (T2) is not in the contract, and L4 cannot tell "crossed" from "did not advance"

`archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md`, ACCEPTED, its other two tests run the same session:
- `:109-112` — the outer tunnel has two faces and which one you arrived on is undetermined: *"A reader that hardcodes one side is right half the time and silently returns a wrong origin the other half. For a motor-safety trace that is worse than stopping."*
- `:130` falsifier **(c)**: *"The far face's `Connected Wire` returns the same wire uid you arrived on; the hop does not advance."* Measured precedent: `docs/d1-build-plan.md:738`, *"the hop does not advance (`#376` t7)"*.
- `:144` **T2**: read the arrived terminal's UID, then 3195B800 **and** 3195B801 — *"whichever matches names the face you are standing on; the other is the continuation."*
- `:187-192` disposition: *"NOT done, and reported to the judgement session as the one open question: T2's live read of 3195B800 / 3195B801 on uid 43605"* — T2 is what this op was authorised to close.

The recipe wires the entire back half (`Is Source?` / `Connected Wire` / `Owner`) from **OuterTerminal only** (`:463-466`); InnerTerminal yields a bare UID and no wire (`:449-460`). The walk takes `nxt = r["recip_wire"]` unconditionally (`:626-632`), and `crossed` (`:649-652`) is true for any non-zero `recip_wire` — falsifier (c) reads as PASS. L1 (`:573-576`) has the same shape.

**Scope:** gates L1/L4 and the single-face back half. It does NOT claim OuterTerminal is the wrong face for uid 43605 — `archive/2026-09-18-status-cycle19-flatseq.md:48-49` records 44036's owner structure as `FlatSequenceFrame`, which makes OuterTerminal right *there*; that is exactly why a one-site pass would generalise a half-right reader into check A.

---

# PART B — THE ARTIFACT

## B1 — cleared, nothing under another name
106 `Op*.vi` in `claudeDev`: no `*FsTunnel*` / `*FlatSeq*` / `*OuterTunnel*`. `OpTunnelRead_v0` casts to `Tunnel` (`docs/toolkit-capabilities.md:71`) and `probe_flatseq_outer.log:25` measured `634A002` REFUSED 1077 on the outer class, so it cannot serve.

## B2 — cleared, never attempted
`docs/vi-server-ids.json:142` and the opus arm `:128` — *"The cast claim 2 rests on has executed zero times."* Nearest live contact: `tools/bench/diag_d1_step0.log:23`, an FSOT (uid 16579) resolved as a wire's source owner through `Generic.Owner` + cast(**GObject**) — never cast to FSOT.

**Also cleared, and stronger than the plan's own citation:** the seed. The plan cites `build_oploopcast_v0.py:201-202`, the expensive NI-example + `copy_into` route (`:162-168`). The *direct* route it actually uses is already built and measured twice — `docs/toolkit-capabilities.md:70` (`OpConnectFromWire_v0`: a Wire-typed seed from a `"VI Server:Wire"` property node's own `reference`; `build_opconnectfromwire_v0.py:243-251`, including the gate that the seed **arrives wired**) and `:68` (`OpConnectNested_v1`). Gates B3/B4 are a re-confirmation, not a first test.

## B3 `helper-exists` — the L4 walk re-implements the helper §A.1 item 5 names, minus its guard
`docs/motor-limit-assurance-plan.md:72-76`: *"**Reuse the two helpers instead of hand-rolling the join:** `tools/bench/diag_tunnelsource_onehop.py` (the cross-border hop, already built and run)…"* That loop is `diag_tunnelsource_onehop.py:198-233` — one hop at a time from Python, owner located from the `main_vi_nodeterms.json` / `d1_step0_census.json` caches (`:161-163`, `:224`), and at **`:230`** the explicit *"tunnel … does not advance the hop"* refusal. `build_opfstunnelterm_v0.py:600-652` rebuilds all of it (own hop loop, own cache load `:603-609`, own stop strings) and drops that refusal — the very guard A4 asks for.

**Scope:** the L4 walk loop only. It does NOT claim the op is redundant: `resolve()` hops only through `LoopTunnel`s (`tunnel_map`, `:193-197`), which is why it stopped at the flat sequence.

## B4 `already-measured` — "owner class + uid" is measured to fail SILENTLY at a flat-sequence frame, and no gate reads the uid
The OUT promises, for the outer terminal, *"its OWNER class + uid"* (`build_opfstunnelterm_v0.py:5-6`), from the donor's `Owner → Class Name` / `Owner → cast(GObject) → UID` branch — the branch `OpOwnerChain_v1` is made of (`docs/toolkit-capabilities.md:61`). Its behaviour at this boundary is on disk: `tools/bench/diag_ownerchain_hop.log:7` — `uid 686 -> owner 'FlatSequenceFrame' uid 0 | self 'Diagram'#686 | 482 says 'FlatSequenceFrame' cast '' | error 1055`, written up as *"an owner chain terminates silently at a flat-sequence frame"*. L1 (`:573-576`) asserts `outer_term_uid != 0`, `err_outer == ''` and `ownercls` non-empty — it never reads `owner_uid`, never reads the `errs` column the recipe itself collects (`:557-559`). The documented silent mode passes L1 as a success, on the one run whose purpose is to certify the read.

**Scope:** L1 and the owner-uid half of the OUT. It does NOT claim the terminal's owner *is* a `FlatSequenceFrame` — that is unmeasured.

---

## Cleared on inspection
- **Fixture keying:** `tools/bench/d1_step0_census.json:2` `"md5": "2a78e17c449cacdaf5da389818526859"` = the **V6 copy**, which is the recipe's target, so index 65 is keyed correctly; `STATUS.md:59-61`'s ORIGINAL-vs-COPY warning is about the motor call-site census, a different artefact.
- `archive/peer/2026-09-14-optunnels-v0-plan.md:45` (*"do not use the unrelated `FlatSequenceOuterTunnel.Inner Terminal`, ID `3195B801`"*) warns against using it **on a LoopTunnel**; this op uses it on its own class.
- Ids, class strings, the 1077 discriminator and the Traverse counts are first-hand (`probe_flatseq_outer.log:17-29`, `vi-server-ids.json:126-141`) and cited correctly. No prior flat-sequence-reader review exists; `2026-09-17-priorart-tunnelsource-onehop.md:391-399` names this gap as still open, as the plan says.

---

```
PRIOR-ART: contradicted      (A3 — tools/recipes/build_opfstunnelterm_v0.py:103,:418,:579-582 vs docs/cycle20-plan.md:39 + docs/motor-limit-assurance-plan.md:66-67 + docs/d1-build-plan.md:735-738 + docs/vi-server-ids.json:141 + tools/bench/probe_flatseq_outer.log:24 — covers the claim that this op is THE primitive and that step 2 is complete: it casts only to FlatSequenceOuterTunnel while both authorising documents say FlatSequence*Tunnel and 14 of the 18 measured non-node crossings are FlatSequenceInnerTunnel-owned, a class the 1077 discriminator proves this op cannot read; does NOT claim the FSOT reader is wrong or that both classes belong in one build)
PRIOR-ART: unread-evidence   (A4 — archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md:109-112,:130,:144,:187-192 + …-codex.md:153 + docs/d1-build-plan.md:738 vs tools/recipes/build_opfstunnelterm_v0.py:463-466,:573-576,:626-632,:649-652 — covers gates L1/L4 and the single-face back half: the accepted review's T2 (compare the arrived terminal against BOTH faces) is the open question this op was authorised to close and is absent, and L4 scores falsifier (c) — a hop returning the wire it arrived on — as CROSSED; does NOT claim OuterTerminal is the wrong face for uid 43605)
PRIOR-ART: helper-exists     (B3 — docs/motor-limit-assurance-plan.md:72-76 + tools/bench/diag_tunnelsource_onehop.py:161-163,:193-197,:198-233,:230 vs tools/recipes/build_opfstunnelterm_v0.py:600-652 — covers the L4 walk loop only: §A.1 item 5 names that helper as the one to reuse, its resolve() already implements the one-hop-from-Python loop, cache-based owner lookup, max-hops and the "does not advance the hop" refusal, and the recipe rebuilds all of it without that refusal; does NOT claim the op itself is redundant, since resolve() hops only through LoopTunnels)
PRIOR-ART: already-measured  (B4 — tools/bench/diag_ownerchain_hop.log:7 + docs/toolkit-capabilities.md:61 vs tools/recipes/build_opfstunnelterm_v0.py:5-6,:557-559,:573-576 — covers the owner-uid half of the OUT and gate L1: the donor's Owner→cast→UID branch is already measured to return the class but uid 0 with error 1055 at a FlatSequenceFrame, silently, while L1 gates on ownercls only and never on owner_uid or the errs column the recipe itself collects; does NOT claim the outer terminal's owner IS a FlatSequenceFrame)
```

**The two that change what happens next.** **A4** is cheapest and most load-bearing: one extra branch (InnerTerminal → `Connected Wire` → `UID`) plus one comparison against the arrival wire turns L4 from "a non-zero wire came back" into the test both review arms asked for — without it the run can pass on uid 43605 and leave the direction question open. **A3** decides what cycle 20 may claim when it passes: an outer-only reader closes 1 of 15 measured non-node crossings, so either the FSIT cast joins this build (the seed route is identical) or step 2's "Done when" and check A's `UNTRACED` default get restated in writing.

## Sources

(extract from answer)

## What was done with it

**ALL FOUR FINDINGS WERE ACCEPTED AND FIXED IN THE RECIPE; THE `FIXED:` RELEASE LINES BELOW ARE VALID AND THE
LAUNCH GATE IS RELEASED.** Whether the build has since been RUN is tracked in `STATUS.md`, not here. Four
findings, zero `novel`, so the launch gate was first armed against `tools/recipes/build_opfstunnelterm_v0.py`
(sha `de04c05f5f65`) and the recipe was not launched at the time this section was written. Cycle-20 Pre-decided 4
is explicit that writing a release line is the judgement session's call and never a material session's, so the
material session wrote none; the four release lines below were added afterwards by the judgement session.

What the material session did instead, on 2026-09-18 03:15-03:17 (`tools/bench/diag_uid_identity.log`,
`BGRUN END rc=0 after 54s`, gates 3/3): ran the two measurements that do NOT depend on the stopped artifact, as a
separate READ-ONLY diagnostic containing no build, no new op and no scratch VI — `tools/bench/diag_uid_identity.py`.

- **The identity question the brief ordered first is answered.** `uids()` on BOTH VIs: uid 28343 is a
  `LoopTunnel` in the V6 copy AND in the 3StateClamping ORIGINAL; 43605 is a `FlatSequenceOuterTunnel` in both;
  44036 is a `SubVI` in both. **The uid space is shared, so a uid does not name a VI.** What is keyed to the V6
  copy are the CACHES — `main_vi_nodeterms.json`'s own `vi` field and `d1_step0_census.json`'s
  `md5 2a78e17c449cacdaf5da389818526859` — which is also this review's "Cleared on inspection" point about
  fixture keying, now measured rather than read off a file. The two VIs differ where the census said they would:
  **97 SubVIs in the ORIGINAL vs 98 in V6** (1898 vs 1902 wires, 170 diagrams each).
- **The known-good fixture resolves through the ops that already exist**, so B3's "reuse, do not re-implement"
  is what was actually done for this half: `gscript.tunnels(V6, 65)` → uid 28343, `out_name` *Magnet position
  output*, out_wire 28392; `OpWireSource_v5` on 28392 → `Terms[0] is_source=True owner SubVI #27605`, which
  `main_vi_subvis.json` names `Max Trans Pos.vi` (diagram 19).
- Rule 1: both originals' md5 (`c39f36e0…`, `2a78e17c…`) and the donor op's (`5dc45a04…`) unchanged before AND
  after; handles 30,325 → 30,541; nothing saved; no motor, no serial port, no camera.

Carried to `STATUS.md` OPEN 48 as the one judgement question: A3 (one class or both), A4 (the T2 face test and
L4's non-advancing-hop falsifier), B3 (reuse `diag_tunnelsource_onehop.resolve()` rather than a second hop loop)
and B4 (gate `owner_uid` and the `errs` column, not `ownercls` alone).

**RELEASED 2026-09-18 by the cycle-20 judgement session: all four findings ACCEPTED, the recipe changed first.**

FIXED: contradicted - tools/recipes/build_opfstunnelterm_v0.py:137 - the op now casts FlatSequenceInnerTunnel (1C3A9000-3, LeftTerm/RightTerm) alongside FlatSequenceOuterTunnel, so it reaches the 14 of 18 measured crossings the FSOT-only version could not.
FIXED: unread-evidence - tools/recipes/build_opfstunnelterm_v0.py:739 - gate T2 now reads both 3195B800 and 3195B801 and requires the arrived terminal to match one, and L4 scores "the hop does not advance" as a falsifier rather than CROSSED.
FIXED: helper-exists - tools/recipes/build_opfstunnelterm_v0.py:617 - L4 now calls diag_tunnelsource_onehop.resolve() instead of re-implementing the hop loop, inheriting its "does not advance" refusal.
FIXED: already-measured - tools/recipes/build_opfstunnelterm_v0.py:657 - gate L1 now reads owner_uid and errs as well as ownercls, so the measured silent mode (uid 0 + error 1055) fails the gate instead of passing it.
