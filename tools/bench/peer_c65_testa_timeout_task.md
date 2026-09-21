# ATTACK this claim. Do not confirm it.

## The record

A READ-ONLY diagnostic, `tools/bench/diag_c64_row1_testa.py`, was launched under a background runner with a
22-minute process deadline. It edits nothing and saves nothing. It has two tests:

- **TEST A** — re-open one saved file cold and read some terminal tables. This finished normally and produced
  its reading (`tools/bench/diag_c64_row1_testa.log:38`).
- **TEST B** — on a second saved file, run a "whole-VI net census" for each of two wire objects: for EVERY
  diagram in the file, list its nodes, and for EVERY node read its full terminal table, collecting every
  terminal whose attached wire id equals the wire being traced. Then the same over all 116 front-panel rows.

TEST B's census was given its own internal soft budget of **600 s per wire** (`diag_c64_row1_testa.py:80`,
`:233-274`). Measured result, `tools/bench/diag_c64_row1_testa.log:46`:

```
TB wire 23502 ... : 2 member(s) over 103 diagram(s) / 450 node(s) in 601.6 s ;
                    budget 600 s reached after 103 of 173 diagrams
```

So ONE wire's census scanned 103 of 173 diagrams and 450 nodes in 601.6 s — about **5.8 s per diagram** and
**1.34 s per node** — and stopped on its own budget without finishing. The second wire (23526) was never
started. The process deadline then fired: `BGRUN TIMEOUT killed after 1321s` (`:53`). The two restarts the run
performs (`:17`, `:42`) account for part of the remaining wall clock.

The inner call being repeated is a COM round trip per node: `g.node_terms_uid(path, diagram_index,
node_index)` (`tools/gscript.py:1005`), which runs a LabVIEW VI Server operation that returns one node's
terminal table (uid, name, source/sink flag, attached wire id, four error columns). `g.node_labels(path,
diagram_index)` (`tools/gscript.py:587`) is called once per diagram. `g.report_all(path, 'Diagram')`
(`tools/gscript.py:488`) enumerated the 173 diagrams once, cheaply, at the start.

Elsewhere in the same file, a *targeted* lookup that stops at the first match, `find_node` (`:141`), located
three nodes by scanning **1 diagram of 173** each — because it was given a hint and hit immediately. Single
`node_terms_uid` reads in TEST A returned promptly. The file itself is a 476 KB VI with 1906 Wire objects,
631 Node objects, 116 ControlTerminal objects and 173 diagrams.

## THE CLAIM YOU MUST TRY TO DESTROY

"The prediction that failed is simply an under-estimate of cost: an exhaustive per-node COM census over a VI
of this size is inherently ~1.3 s per node, so a full two-wire census needs roughly 173/103 x 2 x 600 s ≈ 2000 s
of scanning alone and could never fit a 22-minute deadline. Nothing is wrong with the machine, the file, or
the tooling; the run was simply asked to do too much, and the fix is to scope the census (trace only the
diagrams that can carry the wire) rather than to raise the deadline."

## Already ruled out (do not spend your answer on these)

- "The VI was broken or the session was wedged": both files opened cold at execution state 1 (`:19`, `:44`),
  every census returned real data, and both pre-read restarts reported "clear (no modal dialog)" (`:17`,
  `:42`).
- "A modal dialog blocked it": the run's own dialog check was clean at both restarts, and the scan kept
  producing per-diagram progress until its own soft budget stopped it.
- "The census found the wrong answer": the 2 members it did find are the two intended terminals, and the
  source count is 1 (`:47-49`).

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which **1.34 s per node is
   abnormal** for a VI Server terminal-table read over an out-of-process COM connection, i.e. the cost is a
   defect (re-opening a VI reference per call, a per-call traverse from the root, an O(n^2) re-enumeration, a
   watchdog sleep, marshalling across apartments) rather than an inherent price.
2. A DIFFERENT explanation of the same timing that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.
   It must be READ-ONLY (this project may not modify or save the VI under test) and must not require the
   LabVIEW GUI.

Be concrete about the LabVIEW VI Server object model: is there a way to go from a **Wire** object to the
terminals attached to it directly (a property or method on the wire itself), instead of scanning every node
of every diagram and comparing wire ids? If yes, name the exact property/method and its class. If no, say so
plainly — that answer is as useful to me as the other one.
