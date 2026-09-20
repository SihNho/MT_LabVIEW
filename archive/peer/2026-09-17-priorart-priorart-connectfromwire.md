# priorart-priorart-connectfromwire

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.9003  in 34 / out 32743 / cache-create 292649 / cache-read 2310174  (460s, 29 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (464s)
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
# NEW OP to be built: `OpConnectFromWire_v0.vi` (route B item 1, `docs/d1-build-plan.md` 짠11t)

## What it must do
Create a wire whose SOURCE is a terminal taken from an EXISTING WIRE (`Wire.Terminals[]` 6371003 filtered by
`Terminal.Is Source?` 634A003), and whose SINK is a node terminal addressed purely by index
(`Diagram[d].Nodes[n].Terminals[t]`), using `Terminal.Connect Wire` 6349C03.

Inputs: `vi path`; the SOURCE wire's UID plus either a terminal index on that wire or "the one with Is Source?
TRUE"; the SINK as (diagram index, node index, terminal index). Output: the op's own `error out` on a panel
indicator, plus the sink terminal's resulting wire uid.

## Why it is wanted
18 of route A's 66 re-wire rows (and the same loop-invariant inputs in route B) have a SOURCE that is owned by
`FlatSequenceInnerTunnel` (14), `LeftShiftRegister` of `#637` (2) or a `LoopTunnel` ??classes that appear on NO
`Diagram.Nodes[]` enumeration, so no index-addressed writer can name them
(`tools/bench/build_d1_v0_run9.log:321-338`, `tools/bench/d1_tunnel_sources.json`).
`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md` (codex, ANSWERED) says `Connect Wire`'s
`Wire Source` accepts ANY Terminal reference, including one from `Wire.Terminals[]`.

## The construction I intend (front half + back half, both already on disk)
* FRONT HALF = `OpWireSource_v5.vi` (`tools/recipes/build_opwiresource_v5.py`): `UID to GObject Reference.vi`
  -> cast to `Wire` -> `Wire.Terms[]` -> `Index Array[term index]` -> a Terminal reference, plus `Is Source?`.
* BACK HALF = `OpConnectNested_v1.vi` (`tools/recipes/build_opconnectnested_v1.py`): the SINK ladder
  `Traverse('Diagram')[index] -> To More Specific Class -> AbstractDiagram.Nodes[] -> IA[index 2] ->
  Node.Terms[] -> IA[index 3]` feeding `Terminal.Connect Wire`'s `reference`.
* Intended build shape: copy `OpConnectNested_v1.vi`, delete the wire feeding the Invoke's `Wire Source` input
  and the now-dead SOURCE ladder (its second `To More Specific Class`, its `Nodes[]`/`Terms[]` property nodes and
  their Index Arrays, controls `index 4` / `index 5` / `index 6`), then bring the FRONT HALF's four nodes across
  with `gscript.copy_into` / `copy_by_index` from `OpWireSource_v5.vi` and wire the resulting Terminal reference
  into `Wire Source`.
* Functional test on a scratch: source = an existing wire on the outer diagram that feeds a loop tunnel; sink = a
  node terminal inside a NEW While loop. Gate = the created wire SURVIVES `remove_bad_wires_scripted` and the
  scratch reads `ExecState 1`. Second case: a source wire whose only visible owner is a `FlatSequenceInnerTunnel`.

## Questions for you
1. Has this op (a writer whose wire SOURCE comes from a wire-terminal reference) already been BUILT under another
   name in `tools/recipes/` or `C:\...\user.lib\claudeDev`?
2. Has the "can Connect Wire take a wire-terminal as Wire Source" question already been MEASURED or ANSWERED in
   our own files (docs, logs, archived peer exchanges)?
3. Has this been TRIED AND FAILED already, and is the failure recorded? In particular: is there a recorded
   failure of `copy_into`/`copy_by_index` for the nodes I plan to move, or of a second cast in this op family?
4. Does an existing helper in `tools/gscript.py` already do this, so the new op is redundant?
5. Which of my cited facts above are CONTRADICTED elsewhere in our own files?
Also: is the DELETE-then-copy shape above recorded as having failed before, and is the reverse (build additively
on `OpWireSource_v5.vi` by adding the sink ladder) recorded as cheaper or as having been tried?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??the `archive/2026-09-17-status-*.md` set (**`??d1-full-build-5.md` = the latest session**)
+ `archive/2026-09-16-??. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1q)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2), **짠11p is
   the USER's route-A decision and 짠11q is what its prior-art review changed and BLOCKS; 짠11n.2's "unbuildable"
   is WITHDRAWN**. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` /
   `peer_*` (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS
   need the target's FRONT PANEL open; a fixed op PATH is served from LabVIEW's MEMORY ??unique scratch name/run.
4. ??`guard_cycle` releases on a `FIXED: <slug> - <path>:<line> - ?? line under a prior-art archive's "What was
   done with it" (짠11g.3) ??ONE PER SLUG, or `REFUTED:` with the citation opened. 5. ?좑툘 `peer.ps1` only as
   `powershell -Command "& 'tools/peer.ps1' ??-Task (Get-Content -Raw <f>)"` ??`-File` loses a multi-line `-Task`;
   and `tools/prior_art_review.py` must be launched from **PowerShell**, not the Bash tool (rc 127 there today).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 13:5x-14:2x material/cycle15-d1-route-A-run-9: RELEASED. **짠11r's reader was NOT BUILT ??0 of its
# 2-build budget spent** ??its prior-art review (5 findings, 0 novel, all accepted) showed it is a COMPOSITION of
# `gscript.tunnels()` + `OpWireSource_v5` + an OFFLINE join. Runs: `d1_tunnel_chain.py` (no LabVIEW, 2/18) 쨌
# `diag_tunnelsource_onehop.log` 7/2, 111 s 쨌 `build_d1_v0_run9.log` **55/8, 203 s** (WIRED 35??*42**, FAILED
# 7??, NO-ROUTE 24??*18**; v1 made 8 wires, **5 survived RBW**, 3 deleted). ExecState 0, NOTHING SAVED, working
# copy deleted in the run. Original md5 2a78e17c449c... before AND after EVERY run; LabVIEW restarted once
# (handles 30,384 ??33,848); no GUI, no hardware, no scratch left behind. Peers: priorart-tunnelsource-onehop
# (ANSWERED, disposed) 쨌 flatseq-tunnel-source-addressing r1 TIMEOUT / r2 agy ERROR / **r3 ANSWERED, disposed**.
# 2026-09-17 13:1x-13:4x material/cycle15-d1-route-A-last: RELEASED. LabVIEW restarted TWICE (bench_prep, 31,3xx
# -> ~34,000 each). ??`OpConnectNested_v1.vi` BUILT + SAVED (14,666 B, ExecState 1 warm AND cold) ??the
# CROSS-DIAGRAM wire creator 짠11n called unbuildable. Runs: diag 10/0 쨌 build run 1 rc=1 (Python TypeError in the
# recipe's own hook, no LabVIEW fact) 쨌 build run 2 31/1 쨌 cold test 7/0. 3 scratches, ALL created and deleted in
# the same run, `claudeDev\SCRATCH*` verified empty. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859
# before AND after every run. Donor `OpConnectNested_v0` + NI example md5 unchanged. No GUI, no hardware.
# build_d1_v0 NOT run ??짠11p item 2 is blocked by its own prior-art review (see NEXT). Handles 31,270 -> 31,673.
# Earlier sessions, all RELEASED, originals md5 2a78e17c449... before AND after, no leftovers, no GUI, no hardware:
# open35-run-poison-fix (11/0) 쨌 d1-full-build-5 (OpConnectNested_v0 BUILT+SAVED, 14,234 B) 쨌 build-4
# (OpCreateConstOnTerm_v0 22/0, run 7 55/7) 쨌 build-3 (run 6 56/1) 쨌 phase-full-2 쨌 run 5 53/0. -> archive/
# 2026-09-17-status-d1-full-build-{4,5}.md (the two newest relocated VERBATIM at the END of -5).
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.
## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera
1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??
the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??**say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay** artefacts. **THE GAP:** 173 ops, 121 recipes, 231 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `??d1-phase-full-?? 짠0c)
1??, 5, 9??2 ??**archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (3.6 Hz) 쨌 27 undisposed peer
   archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3. **18 CLOSED by 짠11h ??no TIFF is
   written any more.** 13/14/15b/17b: ??stop measured (`#637` term **648 ??w3457 ??#11639**) 쨌 ?뵶 `bgrun --detach`
   misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*, so the stop is unproven.
16 쨌 19/25/26 쨌 20??3 쨌 27 쨌 28 쨌 28b 쨌 28c/d/e 쨌 29 쨌 30/30b/30c ????CLOSED, relocated VERBATIM to
   `archive/2026-09-17-status-d1-full-build-5.md`: GPU kernel accepted for now 쨌 PLAN = REV 4 + 짠11c?벬?1h,
   transport = queues only 쨌 relocation MEASURED (`WhileLoop 3??`, `Diagram 170??73`, 23 moves, 8 SRs, panel 114;
   **109 terminals / 24 uids**, source map **109/109**) 쨌 `OpCreateConstOnTerm_v0` 22/0 쨌 `diag_d1_full_route`
   retired ????**28c CLOSED 2026-09-17: the 1055 was the CALLER** (`diag_d1_full_route.py:265-273` never set the
   UID-addressed op's `UID 2`); `OpWireSource_v5` reproduced its published control first try 쨌 `OpStopFromNode_v0`
   T5 closed (0 ??387, ExecState 1) 쨌 짠11h: the TIFF writer is not original, F1 uncapped.
28f 쨌 31 쨌 32 쨌 34 ??**relocated VERBATIM to `archive/2026-09-17-status-open-28f-35.md`**, one line each:
28f. ?뵶 run 7, PHASE "full" stage 1: 66 routable rows ??**35 WIRED, 7 FAILED (5001), 24 NO-ROUTE** (17 `from-tunnel`),
   ExecState **0**, nothing saved ??**N1/F1/F2 still NOT RUN** (they need a saved ExecState 1).
31. ?뵶 retrospective still reviews the WRONG window (`retrospective.py:282-286`) ??reproduced a THIRD time today,
   and the cause is now named: `guard_cycle.stamp()` = `min(ctime, mtime)`, so RE-ARCHIVING an existing slug
   keeps the OLD ctime and the gate never sees the new review. No cycle-16 plan document yet.
32. ?뵶?뵶 outcome review 2026-09-17: **six `OUTCOME-VIOLATION`s, SECOND consecutive time** ??the work stops for a
   re-plan with the USER. Not answerable by a device. Zero new user-runnable deliverables.
33 쨌 34 쨌 35 ????CLOSED, **relocated VERBATIM to `archive/2026-09-17-status-d1-route-a-run9.md`**, one line each:
   `OpConnectNested_v1` BUILT + SAVED (14,666 B, warm AND cold) and now MEASURED in the real VI (run 9: 8 wires,
   **5 survive RBW**) 쨌 the acceptance gate is "the wire survives `remove_bad_wires_scripted`", not uid equality 쨌
   gscript's COM **poison flag** fixed + measured 11/0 (`test_run_poison.log`).
36. ?뵶 **NEW, MEASURED 2026-09-17 (짠11s) ??route A's remaining 24 rows are TWO problems, neither an addressing
   one.** (a) **16 `from-tunnel`**: the one hop was READ (`diag_tunnelsource_onehop.log` 7/2,
   `d1_tunnel_sources.json`) ??**14 sources are `FlatSequenceInnerTunnel`, 2 are `LeftShiftRegister` of `#637`**,
   1 is `SubVI #27605` (wired in run 9), 1 does not advance. A `FlatSequenceInnerTunnel` is on NO `Nodes[]`, so
   `OpConnectNested_v1` cannot name it; codex (r3, ANSWERED) says the API can ??`Connect Wire` takes any Terminal
   ref, incl. `Wire.Terminals[]` + `Is Source?` ??so what is missing is a **WRITER**, one fused op, **judgement**.
   (b) **6 `from-ctl` rows fail 5001 in `Get Controls.vi`** (panel-control source; 2 names carry newlines) and
   **no op addresses a panel source by index at all**. Run 9: **42 wired / 6 failed / 18 no-route of 66**; the v1
   op made 8 wires and **5 survived `remove_bad_wires_scripted`** (3 deleted ??two branches of `#8885`'s net and
   the cross-diagram `D[19]?묭[24]` one, unexplained and NOT chased). ExecState 0, nothing saved.

## NEXT
?뵶 **ONE JUDGEMENT QUESTION, and 짠11p's route-A verdict hangs on it ??but it is NOT the question 짠11q.2 posed.**
That question is **answered and gone** (see OPEN 36 and `docs/d1-build-plan.md` 짠11s): the reader was a
composition, it was read, and the 16 `from-tunnel` sources are **`FlatSequenceInnerTunnel` (14)** and
**`LeftShiftRegister` of `#637` (2)** ??the values enter the frame loop's diagram from the ENCLOSING FLAT
SEQUENCE, and neither class is a node any `Nodes[]` enumeration contains. Run 9 measured route A's reach with the
v1 op: **42 wired / 6 failed / 18 no-route of 66**, ExecState 0, nothing saved.
**The question now:** codex (ANSWERED, `archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md`) refutes
"unreachable" ??`Terminal.Connect Wire` 6349C03 accepts **any** Terminal reference, incl. `Wire.Terminals[]`
6371003 + `Is Source?` 634A003, which **`OpWireSource_v5` already holds**. So route A needs ONE more op, a WRITER
fused from two proven halves (`OpWireSource_v5` front + `OpConnectNested_v1` back). **Choose one:** (i) authorise
that one op and finish A's re-wire; (ii) declare **route A failed and switch to B** per 짠11p (the session brief
pre-scripted this ??a material session may not take it, CLAUDE.md 짠3, and did not); (iii) something else for the
6 `from-ctl` 5001 rows, which no op addresses either (panel source + `Get Controls.vi`).
?좑툘 Even with (i), PHASE "full" **stage 2** (8 queues, endpoints, sentinels, `#376`/`#6384` carriers, GPU kernel
13+6) is **still entirely unwritten**, and OPEN 32 stands: no diagnostic or framework cycle before F1/F2.
?좑툘 `build_d1_v0_run9.log` is a FAILING log ??`guard_peer` will demand a review newer than it before the next build.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** (new ops at the end
of the table) 쨌 **`docs/d1-build-plan.md`** = the build order 쨌 `tools/recipes/build_d1_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete. **6 findings, 0 `novel`.** The op does not exist and the delete-then-copy shape has a working precedent — but its **acceptance gate has already been reviewed and retired**, route B's own plan already offers a no-new-op answer for the same 18 rows, and three of the plan's supporting facts are contradicted inside our own files.

---

# PART A — THE DIRECTION

## A1 — settled, and correctly cited. **No slug.**
`docs/d1-build-plan.md:689-702` (§11t, judgement, 2026-09-17) already decides this op: *"The answer is the same single op in both routes — `OpConnectFromWire_v0`… (front half = `OpWireSource_v5`, back half = `OpConnectNested_v1`) … B's first item."* `archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md:94-100` names the same fusion and says it was deliberately not built because `docs/d1-build-plan.md:793` (§11p) forbids a further op *for route A*. The plan cites §11t. Nothing decides against it. No slug.

## A2 `refuted-already` — the back half's addressing scheme is under a standing objection raised twice, five months apart, and the plan answers neither
1. `archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:21-25` is a design review of **this exact artifact** — "OpWireRef_v0": obtain a Terminal refnum of an existing object, feed it to a connect-wire helper, to wire terminals that names cannot reach. Its verdict, `:31-38`: *"`(class, traversal index, terminal-array index)` is too brittle to be the persistent topology description… Score: generic `OpWireRef` 4/10; fused topology-specific creators 8/10"*, and `:77-89` lists the failure classes such an op must expose — including *"broken wire created instead of a rejected operation"*, which is precisely run 9's symptom. **Its "What was done with it" is still `(Claude fills in)` (`:169-171`)** — it was never dispositioned.
2. Independently, `archive/peer/2026-09-17-rbw-deleted-wires-run9.md:109` and `:193-198` name **terminal-INDEX drift** as a live alternative explanation of run 9: *"after tunnel creation/removal, does `T[4]` still identify the same logical loop terminal? … re-reading the same numeric index alone does not prove semantic identity."* LabVIEW creates and removes border tunnels as wires cross structures (`docs/toolkit-capabilities.md:56`: `LoopTunnel 0 → 2`).

The new op keeps index addressing on the **sink** side (`Diagram[d].Nodes[n].Terminals[t]`) and adds a wire-terminal source. The 2026-09-01 review's objection is to exactly that sink addressing; the 2026-09-17 review re-raised it against measured evidence. **Still applies**, and the plan's gate as written cannot detect it (see B4).
*Release is cheap if you disagree:* open `2026-09-01…opwireref-donor-plan-attack.md` and show it addressed a **generic** `(class, index, term index)` resolver rather than a fused two-endpoint writer, then write the disposition it never got.

## A3 `contradicted` — three conflicts, all inside our own current files
**(i) Whether RBW-survival is a valid gate.** `docs/toolkit-capabilities.md:56` states it as the decisive gate: *"the wire **SURVIVES `remove_bad_wires_scripted`** — the gate that uid equality cannot make."* `archive/peer/2026-09-17-rbw-deleted-wires-run9.md:141-151` (codex, ANSWERED, accepted **in full** at `:176`) states the opposite: *"A UID-equality gate over a net is not sound… UID reuse is even permitted after deletion"*, and `:183-188` shows the classifier at `tools/recipes/build_d1_v0.py:1118-1121` is exactly uid equality of two `Terminal.Connected Wire` reads. The plan adopts `toolkit-capabilities.md:56`'s side without citing the review that retired it.
⚠️ **The record that was supposed to prevent this was never written.** That review's own action list, `:203-205`, says *"the F1v gate is recorded as UNSOUND in `docs/d1-build-plan.md` §11u and `docs/d1-route-b-plan.md` §6 R2."* **Neither exists**: a grep of `docs/` for `11u` / `UNSOUND` returns nothing, and `docs/d1-route-b-plan.md:226-229` (§6 R2) is about `OpConnectNested_v0` not being ExecState-verified, with no mention of the gate.

**(ii) Whether route A is closed.** `docs/d1-build-plan.md:689-695` (§11t): *"Route A is closed; nothing more is built for it."* `STATUS.md:98-112` (same day, `status: current`) still poses it as open — *"**Choose one:** (i) authorise that one op and finish A's re-wire; (ii) declare route A failed and switch to B…"* — and `STATUS.md:14-15` still describes the plan as "REV 4 + §11c–§11q", unaware of §11r/§11s/§11t. `docs/d1-build-plan.md:14-18`'s own `build_status` frontmatter likewise still says the fourth op "is a FOURTH op, beyond §11j's authorisation - JUDGEMENT". The plan under review calls itself "route B item 1" while its justification opens from route A's 66 rows. A reader cannot tell which document is current.

**(iii) Whether the front half has an open defect.** `docs/toolkit-capabilities.md:51` carries *"🟡 T6 (`OpWireSource_v5` returned no terminals for w147) still open, as a reader question."* `docs/toolkit-capabilities.md:48`, **three rows earlier in the same file**, says the cause was the caller and names it: *"`build_opstopfromnode_v0.py:368-376` set `Class Name`+`index` (a Traverse index) and **never `UID 2`**, while this op is UID-addressed."* I opened that code: `tools/recipes/build_opstopfromnode_v0.py:373-376` sets `vi path`, `Class Name`, `index`, `term_index` — and no `UID 2`. So :51's open item is already closed by :48. (See B2.)

## A4 `unread-evidence` — route B's own plan already answers these 18 rows, with no new op, and is not cited
`docs/d1-route-b-plan.md:208-224` (§6 R1) is the project's written treatment of **exactly this set of rows** and offers two resolutions that use only built ops:
> *"**What B can offer that A could not** (ASSUMED, unmeasured): the value **is** readable as `#637`'s own **outer terminal**, which is a `Node` terminal index-addressable on `Diagram #686` — run 7 itself printed one (`{'kind':'node','diagram':'19','uid':637,'i':37,'name':'','is_source':True}`)… the wire is **same-diagram** and `OpConnectNested_v0` can express it"*, plus candidate (i): *"create the tunnel with `loop_in` from **any** named node output of the right type on `#686`, delete that wire, then re-point by index (§11k's proven create → delete → re-wire shape)."*

I checked the one row it generalises from — `tools/bench/build_d1_v0_run7.log:317` — and it is the `#376 t7` row, the one `docs/d1-build-plan.md:737` records as *"the hop does not advance"*. For the other 14, `tools/bench/d1_tunnel_sources.json:3-40` shows the outer wire's **source** terminal is owned by `FlatSequenceInnerTunnel`, i.e. `#637`'s own outer terminal on that wire is a **sink**, not a source — so R1's ASSUMED claim probably does not generalise. That is exactly why it must be **cited and disposed of in writing** rather than left unmentioned: this file is marked `prior_art_review: NOT DISPATCHED` (`docs/d1-route-b-plan.md:15`) and `authorises: nothing` (`:9`), and it is the document a route-B build must answer to.
*Release is cheap:* quote `d1-build-plan.md:732-737` (§11s.1's owner table) against `d1-route-b-plan.md:213-217` and record R1 candidate (i)/(ii) as refuted-by-measurement.

---

# PART B — THE ARTIFACT

## B1 — cleared on existence. **No slug.**
No `OpConnectFromWire`, `OpWireRef` or equivalent writer is on disk: the 105 `Op*.vi` in `C:\…\user.lib\claudeDev` contain `OpWireSource_v0…v5` (readers), `OpConnect_v0` / `OpConnect2_v0` / `OpConnectCtl_v0` / `OpConnectNested_v0` / `OpConnectNested_v1` (writers, all node-index or panel-index addressed), and no recipe in `tools/recipes/` builds one. The two index-addressed writers still need a source reachable from `Nodes[]` (`docs/toolkit-capabilities.md:55,:56`); `OpConnectCtl_v0` (`:25`) proves only that a **sink** may come from outside `Nodes[]` (a panel control's own terminal), as `OpStopFromNode_v0` (`:51`) does with `WhileLoop.Loop End Ref`. **No op takes a non-`Nodes[]` SOURCE.** Genuinely new.

## B2 `already-failed` — the front half has one recorded failure at exactly this operation, and the plan does not mention it
`tools/bench/build_opstopfromnode_v0_run3.log:56`:
> `**FAIL** T6 DISCRIMINATOR: the new wire's SOURCE resolves to the body node (direction proven, OpWireSource_v5)  sources [] (want exactly one, owner #44)`

That is the front half's contract — *given a wire, return the terminal with `Is Source?` TRUE* — returning **nothing** on a freshly created wire. The plan's Q3 asks about `copy_into` and second casts; it does not ask about this.
The cause is almost certainly already on record (A3-iii): the caller never set `UID 2` (`tools/recipes/build_opstopfromnode_v0.py:373-376`), and `docs/toolkit-capabilities.md:48` records the identical defect in the sibling caller. **So the release here is one sentence plus a correction to `toolkit-capabilities.md:51`** — but it must be written, because the new op will inherit the same `UID → cast(Wire) → Terms[]` chain, and `docs/d1-build-plan.md:820-825` already flagged that inheritance once (§11q.2 item 2) with CLAUDE.md's rule attached: *"the second time a class of failure is explained by inference rather than read from the machine, the next build is the READER for it."*

**Not found, and the plan asked:** no record of `copy_into`/`copy_by_index` failing for these node classes, and **no record of the DELETE-then-copy shape failing** — it is the shape that produced `OpConnectNested_v1` itself (`tools/recipes/build_opconnectnested_v1.py:45-60`, gates V3–V5d; run 2 31/1, cold `ExecState 1`). A "second cast in this op family" is likewise established twice (`build_opconstvalue_v1.py:165-199`; `docs/toolkit-capabilities.md:57`'s withdrawal). Copying **from an op VI donor** also has precedent (`tools/recipes/build_opaddshiftreg_v0.py:301`, `build_opwiresr_v0.py:297`, `tools/bench/build_keystone.log:355,374`) — with one recorded miss, `build_keystone.log:880`: *"`copy_into(FPTARGET_v0, error out 2)` EXC run blocked behind a modal dialog"*, and the standing rule at `docs/toolkit-capabilities.md:295-318` (copy an op to a scratch before pointing the fleet at it).

## B3 `helper-exists` — the "reverse" build the plan asks about is already on the record, and the front half is bigger than "four nodes"
1. **The reverse direction is recorded, with a disposition.** `archive/peer/2026-09-17-priorart-connectnested-v1.md:307-326` (B3-i) found that `OpExitLoop_v0`, `OpWire_v1` and **`OpWireSource_v5`** each already carry **two** independent `Traverse → IndexArray → To More Specific Class` ladders. `tools/recipes/build_opconnectnested_v1.py:70-78` records why it was not adopted *for v1*: *"building from `OpExitLoop_v0` means re-creating the sink AND source `Nodes[] → IA → Terms[] → IA` ladders and the `Connect Wire` invoke from scratch (7+ nodes, 10+ wires), while this build adds ONE node to an op that already works."* **That arithmetic does not transfer to this build** — here the copy route moves a whole front half, not one node, so the recorded rationale for preferring copy-into-v1 is not evidence for this plan. The reverse direction is therefore not unexplored; it is recorded as the **second attempt inside the budget** (`docs/d1-build-plan.md:805`).
2. **The front half is measured, and it is not four nodes.** `tools/bench/census_opwiresource_v5.log` has the whole VI: `UID to GObject Reference.vi` uid 990 (`:188-192`) → TMSC uid 1044 (`:193-198`) → `Terms[]` PN uid 145 (`:166-171`) → IndexArray uid 151 (`:172-175`), plus `IsSource` PN uid 1319 (`:223-228`). That is **five diagram objects**, and TMSC 1044's `target class` comes from **panel refnum control `reference 2` uid 299, wire 533** (`:84`, `:196`) — the typed seed, i.e. the step `OpConnectNested_v1` spent gates V3 and V5a–V5b on. The op also has 37 panel controls (`:65-102`), so the four-node estimate under-counts both the copy set and the panel work.

## B4 `already-measured` — the acceptance gate, and the "pick the Is Source? TRUE one" input mode
1. **The gate.** The plan's gate is *"the created wire SURVIVES `remove_bad_wires_scripted` and the scratch reads `ExecState 1`."* That instrument has been measured against reality and found to answer a different question: `archive/peer/2026-09-17-rbw-deleted-wires-run9.md:80-88` shows row 1 of run 9 ended with a **non-zero** wire on the terminal (`26189 → 26412`) and was still classified "deleted"; `:186-188` records the honest restatement — *"at most 2 of 8 became null, and 1 of 8 changed wire identity — not '3 deleted'."* The replacement instrument is already specified, `:206-209`: *"`Wire.Is Broken?` 6371004 + `Wire.Terminals[]` 6371003 + `Terminal.Diagram` 634A002, snapshotted from a **HELD** terminal reference rather than a re-indexed one"*, and `:191-192` notes this is the **second** time the cause was inferred rather than read. `Wire.Is Broken?` 6371004 is named as a missing reader in `CLAUDE.md:328`, `docs/NAMES.md:888-889`, and `archive/peer/2026-09-15-retrospective-cycle7.md:155,199`. **Building the writer with the retired gate reproduces run 9's ambiguity by construction** — a broken source wire and a good one will look identical again.
2. **The input mode.** *"or 'the one with `Is Source?` TRUE'"* is not part of either proven half. `docs/toolkit-capabilities.md:48` records how that selection is actually made today: *"Walk `term index` until error 1055; require exactly one terminal with `Is Source?` TRUE whose reciprocal wire is the wire asked about"* — a **Python-side** walk over repeated op runs (`tools/recipes/build_opstopfromnode_v0.py:368-388`). Doing it inside the op needs a loop/filter that neither half has, so "two proven halves" does not cover it. Keep the op single-terminal (`term index` only) and leave the filter in Python, or say plainly that an in-VI loop is new construction.

**Also checked and clear:** the flat-sequence objection in `archive/peer/2026-09-01…:71` (*"Flat Sequence… do not participate normally because they do not inherit from `Node`"*) is **already disposed of** at `archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md:64`, which distinguishes the structure object from a terminal obtained via `FlatSequenceInnerTunnel.Left/Right Terminal`. Not a finding. Note r3 is a **hypothesis** by its own disposition (`:76`, *"accepted as a HYPOTHESIS, not yet confirmed on the machine"*), and its ids 1C3A9000 / 1C3A9001 are explicitly not in `docs/NAMES.md` yet.

---

```
PRIOR-ART: refuted-already   (A2 — archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:21-25,:31-38,:77-89 + archive/peer/2026-09-17-rbw-deleted-wires-run9.md:109,:193-198 — covers the SINK-side (class, traverse index, terminal index) addressing this op keeps, twice argued to be too brittle to carry topology, and the un-dispositioned 2026-09-01 review of this exact artifact; does NOT touch the wire-terminal SOURCE, which that review never considered)
PRIOR-ART: contradicted      (A3 — docs/toolkit-capabilities.md:56 vs archive/peer/2026-09-17-rbw-deleted-wires-run9.md:141-151,:176-188,:203-205 (whose §11u / §6 R2 records DO NOT EXIST); docs/d1-build-plan.md:689-695,:14-18 vs STATUS.md:14-15,:98-112; docs/toolkit-capabilities.md:51 vs :48 + tools/recipes/build_opstopfromnode_v0.py:373-376 — covers the acceptance gate, which document is current on route A, and whether the front half has an open defect)
PRIOR-ART: unread-evidence   (A4 — docs/d1-route-b-plan.md:208-224,:234-240,:9,:15 — route B's own written treatment of these same 18 rows, offering two resolutions that need NO new op, uncited; does NOT assert those resolutions work — d1_tunnel_sources.json:3-40 suggests they do not for 14 of them, which is the disposition that must be written)
PRIOR-ART: already-failed    (B2 — tools/bench/build_opstopfromnode_v0_run3.log:56 + docs/d1-build-plan.md:820-825 — covers the FRONT HALF returning `sources []` for a wire it had just been asked about; the cause is probably already on record at docs/toolkit-capabilities.md:48, so the release is one sentence plus a correction to :51. Does NOT cover the delete-then-copy build shape, the second cast, or copying from an op donor — all three have working precedent: build_opconnectnested_v1.py:45-60, build_opconstvalue_v1.py:165-199, build_opaddshiftreg_v0.py:301)
PRIOR-ART: helper-exists     (B3 — archive/peer/2026-09-17-priorart-connectnested-v1.md:307-326 + tools/recipes/build_opconnectnested_v1.py:70-78 + tools/bench/census_opwiresource_v5.log:84,:166-175,:188-198,:217-228 — covers the plan's closing question (the reverse, additive-on-OpWireSource_v5 direction is already recorded, and the "copy adds ONE node" arithmetic that rejected it does not hold here) and the front half's real inventory: five diagram objects plus a typed-seed refnum control, not four nodes)
PRIOR-ART: already-measured  (B4 — archive/peer/2026-09-17-rbw-deleted-wires-run9.md:80-88,:141-151,:186-192,:206-209 + docs/toolkit-capabilities.md:48 + CLAUDE.md:328 + docs/NAMES.md:888-889 — covers the ACCEPTANCE GATE (RBW-survival by uid equality was measured to misreport, and its replacement reader is already specified) and the "pick the Is Source? TRUE terminal" input mode (done in Python today, not in either half); does NOT question the op's necessity, which A1 confirms)
```

**What I would fix before the build, in one line each:** gate on `Wire.Is Broken?` 6371004 + `Wire.Terminals[]` 6371003 from a **held** terminal reference (the reader `CLAUDE.md:328` has been asking for since cycle 7 — it is ~2 property nodes on the same front half you are already copying); write the missing §11u / §6 R2 records; state in the plan which of STATUS's (i)/(ii)/(iii) §11t settled; and dispose of `d1-route-b-plan.md` §6 R1 in writing.

## Sources

(extract from answer)

## What was done with it

Prior-art review of the ONE op `docs/d1-build-plan.md` §11t names as route B's first item. **6 findings, 0
`novel`. Every finding is dispositioned below, one line per slug, and FOUR of them changed something on disk
before any build ran.** Dispatched by `tools/prior_art_review.py` (claude/opus, `-Role priorart`), 464 s,
`tools/bench/priorart_connectfromwire.log`.

REFUTED: refuted-already - archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:31-38 - I OPENED the
cited review. Its verdict line 1 reads *"`OpWireRef_v0` is acceptable as a low-level wiring primitive **only after
both endpoints have already been resolved semantically**"*, and its score line prefers *"fused topology-specific
creators 8/10"* over *"generic `OpWireRef` 4/10"*. Both conditions are met here and neither was met by the 2026-09-01
plan: that plan proposed a GENERIC resolver that would itself discover endpoints from `(class, traverse index,
terminal index)` at call time, whereas `OpConnectFromWire_v0` is a FUSED creator for one topology (wire-terminal
source -> node-terminal sink) whose endpoints are resolved OFFLINE first, by `d1_rewire_sources.json` (109/109) and
`d1_tunnel_sources.json` (18/18) - both produced and archived before any wire is made. The review's objection is to
using indices as *the persistent topology description*; we do not - the persistent description is the source map,
and the indices are computed from it immediately before each call. Its failure-class list (`:77-89`) is ADOPTED as
the op's test matrix, and its own closing instruction - *"verify each endpoint's connected-wire state, verify both
endpoints' owning diagrams, and verify the target VI is not broken"* (`:89`) - is now this project's acceptance
gate (see `already-measured` below). The 2026-09-01 file's own disposition, blank since it was archived, is filled
in at the same time.

FIXED: contradicted - docs/d1-build-plan.md:1133 - the three conflicts are repaired at their sources, not argued.
(i) The missing records now EXIST: `docs/d1-build-plan.md` §11u.1 (line 1135) states the F1v gate is unsound and
why, and `docs/d1-route-b-plan.md:273` (§6 R2) is rewritten from "`OpConnectNested_v0` is not ExecState-verified"
(answered - v1 is cold-verified 7/0) to the instrument problem that replaced it. `docs/toolkit-capabilities.md`'s
`OpConnectNested_v1` row now carries the correction inline instead of *"the gate that uid equality cannot make"*.
(ii) Which document is current: `docs/d1-build-plan.md`'s `build_status` frontmatter is rewritten to say route A is
CLOSED by §11t and that work continues in the route-B plan, and `STATUS.md`'s NEXT block is rewritten to match
(the (i)/(ii)/(iii) choice is gone - §11t took (ii)). (iii) `docs/toolkit-capabilities.md:51`'s 🟡 T6 is closed in
place, with the caller line numbers, since :48 three rows earlier already held the cause.

FIXED: unread-evidence - docs/d1-route-b-plan.md:255 - `docs/d1-route-b-plan.md` §6 R1 now carries a written
disposition, and the finding is right that it needed one: R1's candidates (i) and (ii) are REFUTED for 14 of the 16
rows by our own `tools/bench/d1_tunnel_sources.json`. On each of those outer wires the terminal with `Is Source?`
TRUE is owned by `FlatSequenceInnerTunnel` (14) or `LeftShiftRegister` (2), so `#637`'s own outer terminal is the
wire's SINK, not its source, and a branch must come from a source. The single run-7 print R1 generalised from is an
OUTPUT tunnel. `docs/d1-route-b-plan.md`'s frontmatter now records this review instead of `NOT DISPATCHED`.

FIXED: already-failed - docs/toolkit-capabilities.md:51 - the recorded front-half failure
(`build_opstopfromnode_v0_run3.log:56`, `sources []`) is closed in writing with its cause: the caller
`tools/recipes/build_opstopfromnode_v0.py:373-376` sets `Class Name` + `index` and never `UID 2`, while
`OpWireSource_v5` is UID-addressed - the identical defect :48 already records for `diag_d1_full_route.py:265-273`
and the one that closed STATUS OPEN 28c. So the front half has no open defect to inherit. ⚠️ Carried into the op's
own test matrix as a REQUIRED gate, not as an assumption: the first thing the new op must prove is that its
`UID` input alone resolves a wire and returns its source terminal.

FIXED: helper-exists - docs/d1-route-b-plan.md:145 - both halves of this finding are taken. (1) The op's SPEC is
narrowed: it takes a `term index` on the source wire ONLY, and the "pick the one with `Is Source?` TRUE" filter
stays in Python, where `docs/toolkit-capabilities.md:48` records it already living ("walk `term index` until error
1055"). An in-VI loop would be new construction and is not built. (2) The front half's real inventory is taken
from `tools/bench/census_opwiresource_v5.log` rather than estimated: **five** diagram objects
(`UID to GObject Reference.vi` #990, TMSC #1044, `Terms[]` PN #145, `IndexArray` #151, `IsSource` PN #1319) plus
the typed-seed refnum control `reference 2` #299 on w533 - not "four nodes". Independently confirmed this session
by `tools/bench/diag_connectfromwire_facts.log` (A3/A4: `OpWireSource_v5` has TMSC `[1044, 1221]`, one
`References` source `[124]`, and its `Terms[]` node #145 is fed from TMSC #1044).

FIXED: already-measured - docs/d1-route-b-plan.md:273 - the acceptance gate is CHANGED before the build, not
after. RBW-survival-by-uid-equality is retired everywhere it was written down (§11u.1, §6 R2,
`toolkit-capabilities.md`'s v1 row) and replaced by the 2026-09-01 review's own list, which needs no new op:
**`ExecState 1` on a scratch built to be otherwise runnable** (the skill's "unforgeable signal"), plus each
endpoint's `Connected Wire` state and each endpoint's owning diagram, plus a COLD re-open in a restarted LabVIEW.
🔴 **Stated plainly, and flagged to judgement rather than decided here:** the instrument the finding actually
prescribes is `Wire.Is Broken?` **6371004** + `Wire.Terminals[]` 6371003 read from a HELD terminal reference, and
that is a SECOND op. A material session may not authorise a second op (CLAUDE.md §3), so it is **not built**, and
the `ExecState`-based gate above is used with that limitation written into the op's log. If judgement rules the
`ExecState` gate insufficient, the op's test must be re-run behind the reader - the build itself does not change.

**Nothing was rejected.** The one finding released (`refuted-already`) was released by opening its citation and
quoting the sentence that permits this use, as the rule requires, and the released review's own blank disposition
was filled in rather than left for the next reader to trip over.
