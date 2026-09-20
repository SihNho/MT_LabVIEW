# priorart-priorart-cfw-recipe

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.5999  in 26 / out 40255 / cache-create 262589 / cache-read 1935060  (561s, 24 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (565s)
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
r"""build_opconnectfromwire_v0.py - `OpConnectFromWire_v0.vi`: `Terminal.Connect Wire` 6349C03 whose **SOURCE is a
terminal taken from an EXISTING WIRE** (`Wire.Terms[]` 6371003, picked by index), and whose SINK is a node terminal
addressed purely by INDEX on a nested diagram. `docs/d1-build-plan.md` 짠11t, route B's first item.

    MATERIAL=1 py tools/bgrun.py --max-min 40 --log tools/bench/build_opconnectfromwire_v0.log \
        -- py -u tools/recipes/build_opconnectfromwire_v0.py

WHY IT EXISTS. 18 of the D1 re-wire rows have a source that is owned by `FlatSequenceInnerTunnel` (14),
`LeftShiftRegister` (2) or a `LoopTunnel` - classes that are on NO `Diagram.Nodes[]`, so no index-addressed writer
can name them (`tools/bench/d1_tunnel_sources.json`, `build_d1_v0_run9.log:321-338`). codex
(`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md`, ANSWERED) says `Connect Wire`'s `Wire Source`
takes ANY Terminal reference, including one from `Wire.Terminals[]`. This op is that writer.

WHAT ALREADY EXISTS - checked before a line was written, and the prior-art review
(`archive/peer/2026-09-17-priorart-priorart-connectfromwire.md`, 6 findings, 0 novel, all dispositioned) checked it
again: no `OpConnectFromWire` / `OpWireRef` is on disk; `OpConnect*` are all node-index or panel-index addressed.
Nothing here is hand-rolled - `gscript` supplies `drop_subvi`, `build_property`, `build_index_array`,
`create_control`, `create_indicator`, `copy_by_index`, `wire`, `wire_control`, `delete_object`,
`remove_bad_wires_scripted`, `set_auto_error_handling`; `build_opconnectnested_v1` supplies `walk`, `term`,
`src_of`, `cls_of`, `idx`, `connect`, `del_net`, `ladder_from`.

THE CONSTRUCTION - ADDITIVE on `OpConnectNested_v1.vi`, nothing deleted except ONE wire.
MEASURED topology of both halves, `tools/bench/diag_connectfromwire_facts.log` (A1-A4, this session):
  v1 (21 nodes): `Open VI Reference` #43 (`vi reference` w467) -> `Traverse` #124 -> IA #308(`index`) -> TMSC #683
     -> SINK ladder #235/#236/#237/#239 -> Invoke #757 `reference`;  IA #645(`index 6`) -> TMSC #1045 -> SOURCE
     ladder #744/#750/#751/#753 -> Invoke #757 `Wire Source` (wire w969).
  v5 front half: `UID to GObject Reference.vi` #990 (`Owning VI` <- w467, `UID` <- a control, `GObject` out)
     -> TMSC #1044 (`target class` <- a Wire-typed refnum SEED) -> `Wire.Terms[]` PN #145 -> IA #151 -> a
     TERMINAL reference.
So: build the v5 front half fresh inside a copy of v1 and re-point the Invoke's `Wire Source` at it.

?좑툘 THE OLD SOURCE LADDER IS **NOT DELETED**, on purpose. Deleting five nodes means re-stitching an error chain for
no gain: `#744`/`#751`'s `error out` terminals are MEASURED unwired (`diag_connectfromwire_facts.log` N[13],
N[15]), so the dead ladder cannot propagate an error into the Invoke, and `index 4/5/6` may be left at 0. Keeping
it also keeps `Wire Source` fed while `copy_by_index` needs the op at ExecState 1 (`copy_by_index` copies the
FILE - the same constraint `build_opconnectnested_v1.py` gate V4 records).

THE ACCEPTANCE GATE, CHANGED BEFORE THE BUILD by the prior-art review's B4 `already-measured` and by
`archive/peer/2026-09-17-rbw-deleted-wires-run9.md` (codex, ANSWERED, accepted in full):
  * ??NOT "the wire survives `remove_bad_wires_scripted`" **as implemented** - that check compares two
    `Terminal.Connected Wire` reads, i.e. object identity. `Terminal.Connect Wire` returns nothing, and run 9's
    `#1359` t4 was counted "deleted" while ending with a NON-ZERO wire (`26189 -> 26412`).
  * ??INSTEAD, the list `archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md:89` asked for, which
    needs no new op: (a) each endpoint's `Connected Wire` state - the sink goes 0 -> NON-ZERO and is still
    NON-ZERO after RBW (that is sound; only uid EQUALITY was not); (b) each endpoint's owning diagram; (c) the
    target VI is not broken - `ExecState`, reported for the scratch and GATED where the scratch is runnable;
    (d) the new wire's SOURCE terminal is read back with `OpWireSource_v5` and must be the object we asked for.
  ?뵶 The instrument that finding really prescribes is `Wire.Is Broken?` **6371004** + `Wire.Terminals[]` 6371003
    from a HELD terminal reference. That is a SECOND op; a material session may not authorise one (CLAUDE.md 짠3),
    so it is NOT built and this limitation is printed in the log.

BUILD GATES (each fatal unless marked; nothing saved on a miss; donors never written)
 W0  `OpConnectNested_v1.vi` at ExecState 1; `UID to GObject Reference.vi` and the NI example on disk; md5s taken.
 W1  copy -> `OpConnectFromWire_v0.vi`; 21 nodes, exactly TWO TMSC, one Invoke, `Wire Source` fed by an
     Index Array; the SOURCE ladder identified BY WIRE TOPOLOGY (`ladder_from`), never by uid.
 W2  `drop_subvi(UID to GObject Reference.vi)` -> exactly ONE new SubVI carrying `GObject`/`Owning VI`/`UID`.
 W3  `Open VI Reference`'s `vi reference` -> the new subVI's `Owning VI` (BRANCH; same wire uid on both ends).
 W4  `create_control` on its `UID` -> exactly ONE new control = the source WIRE's uid input.
 W5  `build_property("VI Server:Wire", 6371003)` -> ONE Property node whose data output is `Terms[]`.
 W6  `create_control` on that node's `reference` -> exactly ONE new control = the WIRE-TYPED SEED, arriving wired.
 W7  two indicators on the two new `error out` terminals (the op must be able to say why it failed).
 W8  ExecState 1 and SAVE - required before `copy_by_index`.
 W9  `copy_by_index(NI example, "Function", 6, expect_uid=99)` -> a THIRD TMSC; in `finish`: delete the seed's
     wire, seed -> new TMSC `target class`, subVI `GObject` -> new TMSC `reference`, new TMSC
     `specific class reference` -> the `Terms[]` node's `reference`; ExecState inside finish reported.
 W10 `build_index_array` + `Terms[]` -> `array` + a new `index` control.
 W11 delete the wire on the Invoke's `Wire Source`; wire the new Index Array's `element` there instead.
 W12 auto error handling OFF; ExecState 1; save; labels JSON; donor md5s unchanged.

FUNCTIONAL TEST
 T1  scratch copy of `EMPTY_v0.vi` (unique name, deleted in the same run): an outer wire `A.error out ->
     B.error in` on diagram 0, a While loop, a third copy of the same subVI in its BODY. Branch from the outer
     wire's SOURCE terminal into the body node's `error in` - the exact shape route B's 18 rows need. Gates:
     op error empty; sink wire 0 -> non-zero; still non-zero after RBW; the new wire's source terminal read back
     through `OpWireSource_v5` is owned by subVI A.
 T2  a fresh working COPY of the original (never the original): source = wire **w5812**, whose only source
     terminal is owned by `FlatSequenceInnerTunnel` **#5818** (MEASURED, `d1_tunnel_sources.json` row 1) - the
     class the whole op exists for. Sink = `#5540` t1 on `Diagram #639` (Traverse index 43), BARED first. Gates:
     op error empty; sink wire 0 -> non-zero; the new wire's source terminal still owned by #5818.
     ?좑툘 ExecState is REPORTED, not gated: a fresh copy of the original already reads 0
     (`diag_connectfromwire_facts.log` B0).
 T3  every scratch deleted in this run; donors' md5 unchanged; the ORIGINAL's md5 read before AND after.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                                              # noqa: E402
from build_opconnectnested_v1 import (walk, term, src_of, cls_of, idx, connect,   # noqa: E402
                                      del_net, ladder_from, Stop)
from bench_prep import labview_handles                                           # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnectFromWire_v0.vi")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects", "Navigating Nodes and Wires.vi")
EX_TMSC_UID, EX_TMSC_FN_INDEX = 99, 6
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
UIDVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to GObject Reference.vi"
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
BENCH = os.path.join(ROOT, "tools", "bench")
MAP_OUT = os.path.join(BENCH, "opconnectfromwire_v0_labels.json")
V5_MAP = os.path.join(BENCH, "opwiresource_v5_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cfw1_{STAMP}.vi")
WORK = os.path.join(g.CLAUDEDEV, f"SCRATCH_cfw2_{STAMP}.vi")
T2_WIRE, T2_OWNER, T2_SINK_
=== END OF THE RECIPE'S DOCSTRING. This IS the plan: the file is `tools/recipes/build_opconnectfromwire_v0.py`,
written but NEVER RUN. ===

ROUND 2. The DIRECTION was reviewed 30 minutes ago:
`archive/peer/2026-09-17-priorart-priorart-connectfromwire.md` (6 findings, 0 novel). **All six are already
dispositioned in that file's "What was done with it"**, and four of them changed files on disk BEFORE this recipe
was written: `docs/d1-build-plan.md` 짠11u (new), `docs/d1-route-b-plan.md` 짠6 R1 disposition + 짠6 R2 rewrite + 짠1
counts + 짠4 table + 짠7 S3w, `docs/toolkit-capabilities.md` (the RBW-gate sentence and the T6 open item both
corrected), and `archive/peer/2026-09-01-2026-09-01-opwireref-donor-plan-attack.md`'s blank disposition filled in.
**Do not re-raise those six unless my disposition is wrong** ??if it is, say which one and quote the line.

What I want from THIS round is the CODE, not the direction. Read
`tools/recipes/build_opconnectfromwire_v0.py` itself and answer:
1. Is any step of W0?밯12 or T1?밫3 already done by an existing helper in `tools/gscript.py` or by an existing
   recipe, so the code is redundant?
2. Has any step here been TRIED AND FAILED before, in a log or an archived exchange ??in particular
   `drop_subvi` of a `vi.lib` VI into an op, `build_property` with class `"VI Server:Wire"` and id `6371003`,
   `create_control` on a property node's `reference` to make a typed seed, a THIRD `To More Specific Class` in
   one op, or `create_indicator` on a subVI's `error out`?
3. Is the ASSUMPTION at the heart of the build recorded as refuted anywhere: that the old SOURCE ladder can be
   LEFT IN PLACE (dead) because `#744`/`#751`'s `error out` terminals are unwired, so it cannot poison the
   Invoke's error chain, and `index 4/5/6` may be left at 0?
4. Are the gate VALUES wrong anywhere ??counts, uids, terminal names ??against what our own files record?
5. Which of the facts cited in the docstring are contradicted elsewhere in our own files?


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
  status: acquired
  owner: material/cycle15-d1-route-B-1
  since: 2026-09-17 14:3x
  purpose: diag_connectfromwire_facts (topology of v1+v5; the from-ctl 5001 cause), then OpConnectFromWire_v0
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

## PRIOR-ART REVIEW — round 2 (the CODE)

**5 findings, 0 `novel`.** Four of the five are about steps this project has already built or already measured; the fifth is a method fix written into `docs/d1-build-plan.md` **earlier in this same session** that the recipe's T2 does not implement. I did not re-raise round 1's six.

I checked every gate value you asked about; most are right, and I say which below so they are not re-derived.

---

# PART A — THE DIRECTION

## A1 `already-built` — the "SECOND op" the docstring declines to build is **already inside the VI this build copies**

`build_opconnectfromwire_v0.py:48-50` and its log line `:546-548` say:

> *"The instrument that finding really prescribes is `Wire.Is Broken?` **6371004** + `Wire.Terminals[]` 6371003 from a HELD terminal reference. That is a SECOND op; a material session may not authorise one (CLAUDE.md §3), so it is NOT built."*

That is wrong about `OpConnectNested_v1`, measured this session by your own diagnostic:

- `tools/bench/diag_connectfromwire_facts.log:16` — `N[10] #241 Property IN [(0,'reference',**572**)] OUT [(4,'Name',609),(5,'**Wire**',620)]`. w572 is the **same wire** that feeds the Invoke's `reference` (`:23`, `#757 IN (0,'reference',572)`) — i.e. the **held sink-terminal reference**, not a re-indexed one.
- `tools/bench/diag_connectfromwire_facts.log:17` — `N[11] #242 Property IN [(0,'reference',620)] OUT [(4,'UID',660),(5,'**Broken?**',676)]`, published as panel `UID 2` (13) and `Is Broken?` (14) (`:27`, and `tools/bench/opconnectnested_v1_labels.json:80-88`).
- The chain's provenance: `docs/keystone-op-spec.md:539` — *"Terminals[]→IA[index 3]→Terminal[Name, Connected Wire]→Wire[UID→'UID 2', Is Broken?]→Clear Errors"* (OpNetInfo_v1), and the short name is verified, not guessed: `docs/NAMES.md:357` — *"`Wire.Is Broken?` 6371004 → **`Broken?`**"*.

So `Wire.Is Broken?` from a held terminal reference is **built, saved and copied forward**. What is actually missing is **dataflow ordering**, and that is stated in one place only — the donor recipe's wrapper comment, `tools/recipes/build_opconnectnested_v1.py:444-446`: *"their dataflow order relative to the Connect Wire invoke is not fixed (both take the same terminal reference), so they may pre-date the wire."* Run 9 shows exactly that: `tools/bench/build_d1_v0_run9.log:260-267`, **eight** readbacks, every one `'UID 2': 0` — including rows that ended WIRED (`:273`, `:277`, `:286`).

Ordering the read after the Invoke is **one `connect(..., branch=True)`** from `#757`'s `error out` (w1027, `diag_connectfromwire_facts.log:23`) into `#241`'s `error in (no error)`, which the same line measures **unwired** (`:16`, `IN (2,'error in (no error)',0)`). That is one call inside the additive build already being written — not a second op, and not a CLAUDE.md §3 authorisation.

`docs/d1-build-plan.md:1158-1160` and `docs/d1-route-b-plan.md:286-288` carry the same "not built / second op / judgement call" sentence and are wrong the same way; they are where the docstring got it.

*Release is cheap if I am wrong:* open `diag_connectfromwire_facts.log:16-17` and show `#241`/`#242` are fed from something other than the Invoke's own `reference` wire, or show that branching an error chain into `#241` cannot order it.

## A2 `contradicted` — the dead-ladder safety argument reads our own recorded rule **backwards**

`build_opconnectfromwire_v0.py:32-34`:

> *"`#744`/`#751`'s `error out` terminals are MEASURED unwired (`diag_connectfromwire_facts.log` N[13], N[15]), so the dead ladder cannot propagate an error into the Invoke."*

The measurement is correct — `diag_connectfromwire_facts.log:19` (`#744 … OUT [(3,'error out',0)]`) and `:21` (`#751`, same). The inference is the wrong half of the rule. `tools/gscript.py:1292-1293`:

> *"Unwired error INPUTS are harmless — only an **unwired error OUT that receives an error raises a dialog**."*

So "unwired" is the hazardous state, not the safe one, and the hazard is not propagation into the Invoke — it is a **modal dialog inside a COM run**, which this project has already lost a run to: `tools/bench/build_keystone.log:880` (*"`copy_into(FPTARGET_v0, error out 2)` EXC run blocked behind a modal dialog"*), and which the recipe itself expects at `:364` (`"modal dialog (dismissed)" if "modal dialog" in str(e)`).

The one defence against it is `set_auto_error_handling(OP, False)` — and in this recipe it is **non-fatal**, `:312-315` (`except Exception … fact("set_auto_error_handling failed")`), after which W12 saves anyway. The donor recipe called it **twice**, once inside `finish` and once at the end (`build_opconnectnested_v1.py:361`, `:394`). This build calls it once, in the branch that is allowed to fail silently.

I am **not** claiming the dead ladder will error at `index 4/5/6 = 0`; with `Class Name = "Diagram"` (`:342`) `References[0]` is a Diagram and the cast plausibly succeeds. The finding is that the safety argument as written does not establish what it claims, and the cheap fix is to make W12's AEH-off gate fatal (or wire the two dead `error out`s to the indicators W7 already knows how to make).

## A3 `contradicted` — the headline count "18" disagrees with the three files it rests on

`build_opconnectfromwire_v0.py:8-10`: *"**18** of the D1 re-wire rows have a source that is owned by `FlatSequenceInnerTunnel` (14), `LeftShiftRegister` (2) or a `LoopTunnel`"*, citing `build_d1_v0_run9.log:321-338`. Those are the 18 NO-ROUTE lines, and they are not 18 of that kind:

- 14 `FlatSequenceInnerTunnel` + 2 `LeftShiftRegister` + 1 `LoopTunnel` = **17** (`run9.log:321-323, :325-338`).
- The 18th is **`from-ctl`**, not a tunnel at all: `run9.log:324` — *"NO-ROUTE `#2222` t0 '' ← from-ctl 47 control 'Z/dZ' / sink name '' — wire_control is name-addressed on BOTH ends"*. Nothing in the JSON or the plan says this op addresses a panel-control source; `docs/d1-route-b-plan.md:290-291` (R3) keeps it as its own unsolved row.
- The `LoopTunnel` row is the one that **does not need this op**: `tools/bench/d1_tunnel_sources.json:188-211` — `"why": "tunnel 2213 outer wire 2187 does not advance the hop"`, and its `census_outer_source` is `{'kind':'node','diagram':'19','uid':637,'i':37,'is_source':True}`, i.e. an index-addressable node terminal that `OpConnectNested_v1` can already name.
- Our other two files say **16**: `docs/d1-route-b-plan.md:255-262` (*"candidates (i) and (ii) are REFUTED for 14 of the 16 rows … `FlatSequenceInnerTunnel` (14 rows) or `LeftShiftRegister` … (2 rows)"*) and `STATUS.md` OPEN 36 (*"16 `from-tunnel` … 14 … 2 … 1 is `SubVI #27605` (wired in run 9), 1 does not advance"*).

The op's real target set is **16**. T1's docstring (`:73`) inherits the error (*"the exact shape route B's 18 rows need"*). This changes no code, but the build log and the next plan revision will report reach as `n/18` against a denominator our own measurement says is 16.

---

# PART B — THE ARTIFACT

## B1 `already-failed` — W1 drops the node-count assertion its donor had, on a **fixed** op path, and that is the recorded stale-in-memory failure

`build_opconnectfromwire_v0.py:176-177`:

```python
gate("W1 the copy is runnable with exactly TWO To More Specific Class nodes",
     es == 1 and len(tmscs) == 2, f"ExecState {es}, TMSC {tmscs}, {len(w)} nodes", fatal=True)
```

`len(w)` is **printed, not asserted**, although the docstring's W1 (`:54`) promises "21 nodes". The donor recipe asserted it: `tools/recipes/build_opconnectnested_v1.py:261` — `es == 1 and len(tmscs) == 1 and **len(w) == 19**`.

That assertion is not decoration; it is the remedy this project adopted after the failure it is the guard for. `archive/peer/2026-09-17-priorart-d1-build-rev3.md:131`:

> *"The 'fresh donor copy' was **the previous run's artefact**: the same LabVIEW process still held `OpMoveIn_v0.vi` in memory with run 2's unsaved edits, so `GetVIReference(path)` served the cached object and the disk overwrite was invisible. Remedy: a **uniquely named working copy per run** plus gate **P1z**, which proves the copy is the donor (ExecState 1, 15 nodes, **no `UID to GObject Reference.vi`**) before anything is edited."*

Same gate spelled out at `archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md:132`; `STATUS.md` START HERE item 3 states the mechanism (*"a fixed op PATH is served from LabVIEW's MEMORY — unique scratch name/run"*). This recipe uses a **fixed** path (`:102`, `OP = …/OpConnectFromWire_v0.vi`, `shutil.copyfile` at `:168`) and both discriminators P1z names are exactly the ones it drops: the node count, and the absence of `UID to GObject Reference.vi`.

Concretely: a re-run after a failure at or past W5 meets a cached OP with 22+ nodes, still two TMSCs, still ExecState 1 → **W1 passes**, W2's "exactly one new SubVI" passes (`new_since` sees only the newly dropped one), and the op ends with **two** `UID to GObject Reference.vi` nodes. Adding `len(w) == 21` and "no `UID to GObject Reference.vi` on the fresh copy" to W1 costs one line each.

## B2 `unread-evidence` — T2's bare-the-sink step ignores the method fix written into the plan **this session**, and the log it cites measured that step failing

`docs/d1-build-plan.md:1187-1188` (§11u.2, written from `archive/peer/2026-09-17-wireinputs-forloop-tunnel-name.md`, codex, ANSWERED):

> *"**Method fix carried forward: a 'bare the sink' step must assert the terminal reads wire 0 and stop if it does not.**"*

and the measurement behind it, in the very log this recipe cites for its own facts — `tools/bench/diag_connectfromwire_facts.log:70`: *"`#1359` t7 … wire **31059 → 31166** after baring"*, i.e. the bare step did not bare.

`build_opconnectfromwire_v0.py:485-500` prints the outcome and continues:

```python
bare = next((r["wire"] for r in rows if r["i"] == T2_SINK_T), 0)
fact(f"T2 sink … wire {cur} -> {bare} after baring")      # :493  printed, never gated
dw, es, err, sub = connect_from_wire(...)                  # :494
gate("T2c the sink terminal carries a wire that it did not before", bool(after) and after != bare, …)
```

`T2c` is satisfied by *"some other wire is here now"*, which is true both for a clean create on a bare terminal and for a replacement on an occupied one. T1 does gate this (`:442-443`, `t_c["wire"] == 0`, fatal); T2, the row that actually matters, does not.

Second half of the same finding: T2 reads the source **before** the destructive step and re-uses the pre-delete uid afterwards. `:474` `wire_source_owner(WORK, T2_WIRE)` → `:489` `delete_object(WORK,"Wire",…)` + `:490` `remove_bad_wires_scripted` → `:494` `connect_from_wire(WORK, **T2_WIRE**, src_i, …)`. w5812 is the **outer** wire feeding LoopTunnel `#5569` (`run9.log:321`), and deleting the tunnel's inner segment then running RBW is precisely the class of edit `docs/d1-build-plan.md:1147-1149` records as unmeasured: *"LabVIEW creates/removes border tunnels as wires cross structures … so `T[4]` after the edits need not denote `T[4]` before them."* Re-reading w5812's source terminal after the bare step (one more `wire_source_owner` call — the function is already there) makes T2's premise checked rather than assumed.

## B3 — gate VALUES: checked, and these are **right**. No slug.

So they are not re-derived next session:

| gate | value | verified against |
|---|---|---|
| `EX_TMSC_UID, EX_TMSC_FN_INDEX = 99, 6` | ✅ | `build_opconnectnested_v1.py:113` (same donor, same pair, run 2 31/1) |
| `T2_WIRE/T2_OWNER/T2_SINK_UID/T2_SINK_T = 5812/5818/5540/1` | ✅ | `tools/bench/d1_tunnel_sources.json:8-15` (row 1) and `build_d1_v0_run9.log:321` |
| `T2_DIAG_UID = 639`, used as a **uid** then converted (`:481`) | ✅ | `diag_connectfromwire_facts.log:64` (*"Diagram #639 is Traverse('Diagram') index 43"*); `#5540` is a frame-loop body node (`docs/frame-loop-wire-graph.md:71,:253-254`) |
| `"dead_src_node":"index 4"`, `"dead_src_term":"index 5"`, `"dead_src_diag":"index 6"` (`:320-321`) | ✅ | `tools/bench/opconnectnested_v1_labels.json:8-10` — the donor recipe already wrote this map (`build_opconnectnested_v1.py:400-406`); consider loading it instead of retyping it |
| W1 "exactly TWO TMSC" / W5b `outs == ["Terms[]"]` | ✅ | `diag_connectfromwire_facts.log:28-29` (`TMSC [683, 1045]`) and `:42,:59` (`#145` data output `Terms[]`) |
| `#744`/`#751` `error out` unwired | ✅ | `diag_connectfromwire_facts.log:19,:21` — the fact is right; see A2 for what it does and does not license |

## B4 — your Q2, answered item by item. **No slug** — none of these has a recorded failure.

- **`drop_subvi` of a `vi.lib` VI into an op** — precedented with the *same* VI and the same resulting uid: `tools/bench/build_opwiresource_v1.log:9,23,49,82` (*"PASS A exactly one new SubVI (UID to GObject Reference.vi) [990]"*).
- **`build_property` with `"VI Server:Wire"`** — precedented: `tools/recipes/build_opnetinfo.py:151` builds a Wire-class node with `632A813` + `6371004` (OpNetInfo_v1, `docs/keystone-op-spec.md:535`). `6371003`'s short name `Terms[]` is measured on the machine (`diag_connectfromwire_facts.log:42`), not guessed.
- **`create_control` on a property node's `reference` to make a typed seed** — this is the *documented* seed recipe, `docs/toolkit-capabilities.md:71-79`, and the donor build used it (`build_opconnectnested_v1.py:294`, gate V3).
- **A THIRD `To More Specific Class` in one op** — a second is established twice (`build_opconstvalue_v1.py:165-199`; `build_opconnectnested_v1.py` V5, cold-verified 7/0). I found **no record of a third**, and none against it. Genuinely untried, not refuted.
- **`create_indicator` on a subVI's `error out`** — routine: `build_opbuildpn_v1.py:121`, `build_opconnectctl_v0.py:155`, `build_opaddshiftreg_v0.py:249`, ~20 more.

**Two prose notes, no slug, because neither is a defect today:**

1. **W2/W3/W4/W9 repeat `tools/recipes/build_opwiresource_v1.py:112-174` step for step** — drop the lookup VI, census its terminals, branch `Open VI Reference` → `Owning VI`, `create_control` on `UID`, copy a TMSC from the NI example in a `finish` hook, seed `target class`, wire `GObject` → `reference`. Nothing there is importable (it is a builder body, not helpers), so this is not redundancy you can remove — but it is where the lessons live. One of them is not carried: `:124-130` requires the census to match **name AND direction** and to see **exactly one** of each, because the VI also exposes unnamed connector-pane slots and a `dup Owning VI` flow-through source. W2b (`:194-197`) keys a plain dict by name and checks direction only for `GObject`. Measured, it does not bite — `diag_connectfromwire_facts.log:46` shows `#990` with exactly one `UID` sink, one `Owning VI` sink, one `GObject` source and five `''` slots — so this is a weaker gate, not a broken one.
2. **`connect_from_wire` drops two things its donor's wrapper had**: `g.ensure_loaded(target)` (`build_opconnectnested_v1.py:421`; the panels are opened explicitly at `:411`/`:470`, so the mechanism `gscript.py:1276-1281` cares about is satisfied — but the call is idempotent and free), and the `UID`/`Name`/`UID 2`/`Is Broken?` readback loop (`build_opconnectnested_v1.py:446-452`). The second is the same instrument as A1: the new op inherits those indicators and never reads them.

---

```
PRIOR-ART: already-built     (A1 — tools/bench/diag_connectfromwire_facts.log:16-17,:23,:27 + tools/bench/opconnectnested_v1_labels.json:80-88 + docs/keystone-op-spec.md:539 + docs/NAMES.md:357 + tools/recipes/build_opconnectnested_v1.py:444-452 + tools/bench/build_d1_v0_run9.log:260-267 — covers the claim at build_opconnectfromwire_v0.py:48-50 and :546-548 that `Wire.Is Broken?` 6371004 from a HELD terminal reference is "a SECOND op … NOT BUILT": it is node #242 of the VI this build copies, fed from the Invoke's own `reference` wire w572, already on the panel as `Is Broken?`/`UID 2`. Does NOT claim the readout is usable as-is — it is UNORDERED (every run-9 readback reads `UID 2: 0`); the missing piece is one branch of #757's `error out` into #241's unwired `error in (no error)`, not an op)
PRIOR-ART: contradicted      (A2 — tools/gscript.py:1292-1293 vs build_opconnectfromwire_v0.py:32-34; plus tools/bench/build_keystone.log:880 and build_opconnectfromwire_v0.py:312-315 vs build_opconnectnested_v1.py:361,:394 — covers the dead-ladder safety argument: "error out unwired ⇒ cannot propagate" is the safe reading of a rule whose recorded point is that an unwired error OUT receiving an error is what raises a modal dialog, and the only defence in this recipe is a non-fatal set_auto_error_handling. Does NOT assert the dead ladder WILL error at index 4/5/6 = 0)
PRIOR-ART: contradicted      (A3 — build_opconnectfromwire_v0.py:8-10,:73 vs tools/bench/build_d1_v0_run9.log:321-338 (esp. :324, a from-ctl row) + tools/bench/d1_tunnel_sources.json:188-211 + docs/d1-route-b-plan.md:255-262 + STATUS.md OPEN 36 — covers the "18 rows" denominator: the classes named total 17, one of the 18 NO-ROUTE rows is a panel-control source this op does not address, and the LoopTunnel row's own census names an index-addressable node terminal on #637. The measured target set is 16. Does NOT touch the op's necessity for those 16)
PRIOR-ART: already-failed    (B1 — build_opconnectfromwire_v0.py:102,:168,:176-177 vs tools/recipes/build_opconnectnested_v1.py:261 + archive/peer/2026-09-17-priorart-d1-build-rev3.md:131 + archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md:132 + STATUS.md START HERE item 3 — covers W1 asserting only ExecState and the TMSC count on a FIXED op path, while the recorded stale-in-memory failure's remedy (gate P1z) is precisely the node count plus the absence of `UID to GObject Reference.vi`. Does NOT claim the first run will fail — it is the re-run after a mid-build failure that passes W1 on a dirty cached VI)
PRIOR-ART: unread-evidence   (B2 — docs/d1-build-plan.md:1183-1188 and :1147-1149 vs build_opconnectfromwire_v0.py:485-500 + tools/bench/diag_connectfromwire_facts.log:70 + tools/bench/build_d1_v0_run9.log:321 — covers T2's bare-the-sink step, which prints rather than asserts wire 0 (the method fix written into the plan this session, from a measurement in the log this recipe cites) and re-uses the pre-delete uid w5812 after a delete + Remove Bad Wires without re-reading it. T1 already gates this correctly at :442-443; does NOT apply to T1)
```

**What I would change before the run, one line each:** branch `#757 error out` → `#241 error in (no error)` and read `UID 2`/`Is Broken?` back in `connect_from_wire`, then delete the "SECOND op / NOT BUILT" paragraph and its log print; make W12's `set_auto_error_handling` gate **fatal**; add `len(w) == 21` and "no `UID to GObject Reference.vi`" to W1; make T2's bare step assert `bare == 0` and stop, and re-read w5812's source terminal after it; and write the denominator as **16**, citing `d1_tunnel_sources.json`.

## Sources

(extract from answer)

## What was done with it

Round 2 of the prior-art review for `OpConnectFromWire_v0` - the CODE this time, not the direction. **5 findings,
0 `novel`, all five ACCEPTED and all five fixed in `tools/recipes/build_opconnectfromwire_v0.py` before it ran.**
Round 1 (`archive/peer/2026-09-17-priorart-priorart-connectfromwire.md`) was dispositioned first, and this round
was asked not to re-raise it; it did not.

FIXED: already-built - tools/recipes/build_opconnectfromwire_v0.py:196 - **this is the most valuable finding of
the day and it reverses my own conclusion.** I had written that the sound gate, `Wire.Is Broken?` 6371004 from a
held terminal reference, "is a SECOND op, NOT BUILT" and flagged it to judgement. It is node **#242 of the VI this
build copies**: #241 reads `Wire` off the SINK terminal reference w572, #242 reads that wire's `UID` and
`Broken?`, and both already surface on the panel as `UID 2` and `Is Broken?`. What was missing was ORDER, not a
reader - #241's `error in (no error)` is unwired, so the read may run BEFORE the `Connect Wire`, which is exactly
why every run-9 readback printed `'UID 2': 0` (`build_d1_v0_run9.log:260-267`). New gate **W7b** branches the
Invoke's own `error out` into #241's `error in (no error)` (both asserted first: exactly one such reader, its
`error in` currently unwired), `connect_from_wire` returns `Is Broken?`/`UID 2`/`Name`, and the tests gate on them
(**T1f2**, **T2c2**). The "SECOND op" paragraph and its closing log print are deleted. **This also closes round
1's B4 without judgement**: the acceptance instrument that finding demanded is now in the op, so nothing here is
waiting on a decision.

FIXED: contradicted - tools/recipes/build_opconnectfromwire_v0.py:288 - the dead-ladder safety argument read
`gscript.py:1292-1293` backwards. The recorded point is that an unwired error OUT which RECEIVES an error is what
raises a MODAL DIALOG, and a modal dialog hangs every later COM call (`build_keystone.log:880` is the recorded
instance). The only defence this op has is auto error handling being OFF, and W12 treated a failure to turn it off
as a printed note. It is now gate **W12a, FATAL**. The design itself is unchanged and the finding does not claim
the dead ladder WILL error at `index 4/5/6 = 0`.

FIXED: contradicted - tools/recipes/build_opconnectfromwire_v0.py:14 - the denominator. The docstring said "18 of
the D1 re-wire rows"; the classes it then names total 17, and `tools/bench/d1_tunnel_sources.json` makes the real
target set **16** (14 `FlatSequenceInnerTunnel` + 2 `LeftShiftRegister`). Of run 9's 18 NO-ROUTE rows, `#2222` t0
is a PANEL-CONTROL source this op does not address (`build_d1_v0_run9.log:324`) and `#376` t7's hop does not
advance. The docstring now says 16 and names the two exclusions. `docs/d1-route-b-plan.md`'s ledger is unaffected:
its 18 R1 rows are the plan's own row count, and its "19 -> 1" sentence already excludes the control-source row as
R3.

FIXED: already-failed - tools/recipes/build_opconnectfromwire_v0.py:176 - W1 asserted only ExecState and the TMSC
count on a FIXED op path, which `STATUS.md` START HERE item 3 and
`archive/peer/2026-09-17-moveinto-stale-in-memory-vi.md` both record as the shape that lets a half-built CACHED VI
pass a re-run's first gate. W1 now also asserts `len(w) == 21` and that NO `UID to GObject Reference.vi` is
already on the diagram - i.e. that the copy really is a clean donor and not this build's own leftovers.

FIXED: unread-evidence - tools/recipes/build_opconnectfromwire_v0.py:500 - T2's bare-the-sink step now ASSERTS
`bare == 0` and STOPS if it does not (new gate **T2a2**, fatal), and the source wire w5812's terminal is re-read
AFTER the delete + Remove Bad Wires instead of before. This is the same method fix the session had just written
into `docs/d1-build-plan.md` §11u.2 from
`archive/peer/2026-09-17-wireinputs-forloop-tunnel-name.md` - and the finding is right that I wrote the rule into
the plan and then left the recipe doing the thing the rule forbids. T1 already gated this correctly.

**Nothing was refused.** B3 (gate values) and B4 (my Q2, item by item) came back clear with no slug, and are
recorded here only so a later reader does not re-ask: no recorded failure exists for `drop_subvi` of a `vi.lib` VI
into an op, for `build_property` with `"VI Server:Wire"` + `6371003`, for `create_control` on a property node's
`reference` as a typed seed, for a third `To More Specific Class` in one op, or for `create_indicator` on a
subVI's `error out`.
