---
type: facts
status: current
date: 2026-10-02
tags: [card-139-1, error-list, case-selector, for-loop, loop_in]
---
# Card 139-1 facts (LabVIEW, scratch only; order A = bed copy, B = For group; stopped in B)
Run `tools/bench/diag_c139_1_run.py` -> `tools/bench/diag_c139_1_run.log` (BGRUN END rc=1 after 826 s, 8 pass / 2 fail, :27-29).
Out JSON `tools/bench/diag_c139_1_out.json`. Bed md5 395118775a52bc90073f4449b99f899d before and after (:3, :26); LabVIEW gone (:24);
3 scratch files deleted (:25).
## A. Bed byte copy, delete_wire w25415, ONE full Error List read (every item double-clicked)
- w25415 before: t9668 `x .and. y?` (#9647, source) -> t10469 (#10465 outer face, owner_class Tunnel) + t25557
  `autofocus reseed flag (1.2 to 1.1)`; after the delete all three wire 0, ExecState 0 (log :5-8).
- Full read: 52 items, 52 double-clicked (:10). Compared with the expected file (`errorlist_expected_D1_ring_p3b2b_20261002_130007.json`,
  `EC.compare`, normalised text): **exactly ONE extra, none missing** (out JSON :319-322):
  **item index 9, `Case Structure 'Case Structure': Unwired selector`** - "The Case structure must have a Boolean, numeric or
  enumerated input wired to its selector terminal" (out JSON :46-52). Screenshot after its double-click:
  `tools/bench/errorlist_shots/bd_184749_after9.png` (a True/False Case with an empty selector; the `x .and. y?` output beside it).
- Owner uid: NOT readable from the list (uid_route "Selection List[] op unbuilt", `errorlist_check.py` UID_ROUTE). From the graph:
  #10465 has one outer face (t10469, on #23166) and one inner face per frame (t10467 on #10453, t10468 on #10459;
  `diag_c138_6_q1.log:30-32`) = the selector of the Case whose frames are #10453/#10459. So the 52nd item is that Case's selector
  losing its only source; v7's step 159 re-wires it.
- GATE FAIL `A exactly one item new vs the 51 baseline` (:11) is OUR gate's bug: it diffed raw OCR strings against the 13:08 read
  without normalising, so spacing noise ("You haveconnectedan ..." vs "You have connected an ...") counted 5 new / 4 gone. The
  normalised compare above is the valid one.
## B. For-loop group inside a While body (STOPPED before any group node)
- Created: top-level generator For FG (N = 20 const), While W (cond const True). Then
  `gscript.loop_in("for", TGT, <W body index>, (250,150))` raised `error 1055: To More Specific Class in OpForLoopIn_v0.vi (new [])`
  (log :19-22). loop_in's defaults are `src_cls=None -> "SubVI", src_index 0` (`gscript.py:1524`): the scratch (EMPTY_v0 copy)
  has NO SubVI, so Traverse SubVI[0] gives no reference and the cast fails. In the bed (stagexec route `stagexec.py:2653`) a SubVI
  exists, so this is a scratch-only condition - UNMEASURED whether the op then adds input tunnels from that SubVI's outputs
  (Names = [] here and in stagexec).
- Not reached: GT/AMM/SW/KMX creation, Num control, the 3 auto-index tunnels, IndexMode read-back, Is Broken?, ExecState, runs.
  No scratch_verify record written.
OPEN: rerun B with a SubVI present on the scratch (or loop_in given src_cls of a node that exists, e.g. the generator's
Greater? helper) - which form does judgement accept as faithful to v8's p4_f_min route?
