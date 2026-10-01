ATTACK this claim (failed prediction in tools/bench/diag_c123_casetun.py -> tools/bench/diag_c123_casetun.log:69-70).

Setting: LabVIEW 2026 VI Scripting driven over COM from Python. A Case structure with a Boolean selector (frames False / True)
was dropped on a loop body; an INPUT tunnel and an OUTPUT tunnel were created by wiring across the case border with
`Terminal.Connect Wire` (op OpConnectNested_v1: sink terminal and source terminal each addressed as
diagram index / Diagram.Nodes[] index / Node.Terminals[] index). In the False frame the input feeds Increment, Increment feeds
the output tunnel. The prediction was: the case node's `Terminals[]` would then list one UNWIRED source (input tunnel's inner face
in True) and one UNWIRED sink (output tunnel's inner face in True), so the same op could wire True-frame inner -> inner.
Observed: case `Terminals[]` = 3 rows only: selector + the two OUTER faces (log:69). No inner face listed.

The explanation formed:
 (1) A structure node's `Terminals[]` lists only outer faces; a tunnel's per-frame inner terminals are reachable only through the
     tunnel object (`Tunnel.Inside Terminals[]` 6356000, one per frame, order not documented as frame order -> map by
     `Terminal.Diagram` 634A002), or through a whole-VI `Traverse('Terminal')` read whose rows carry owner uid = the tunnel and
     frame_diagram = the frame's Diagram uid (our OpAllTerms_v1).
 (2) The True-frame pass-through therefore needs a writer that takes the two terminals by TERMINAL REFERENCE (resolved from the
     terminal's UID via vi.lib `UID to GObject Reference.vi` -> To More Specific Class(Terminal)) and calls
     `Terminal.Connect Wire` on the output tunnel's True inner terminal with `Wire Source` = the input tunnel's True inner terminal.
 (3) The three junk `Invoke` nodes counted after the run (log:71) come from the cross-border connect ops, not from the case.

Strongest reason this is wrong? Alternatives to test: e.g. the frame diagram's `Nodes[]` already contains the tunnel objects
(so the existing index-triple op reaches the inner face with no new op); `Connect Wire` refuses an inner->inner wire whose two
ends belong to tunnels of the same structure; `UID to GObject Reference.vi` does not resolve a Terminal uid; the inner
terminal order of `Inside Terminals[]` is frame order after all. Name the cheapest discriminating test for each.
