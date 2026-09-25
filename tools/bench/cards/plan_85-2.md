---
type: plan
status: draft
date: 2026-09-25
---
# Card 85-2 plan: two routes for the last two unroutable L2-A1 rows (Pre-decided 191, docs/d1-loop12-17-split-plan.md:893-915)

Context: L2-A1 staged move on bed `claudeDev\D1_k_20260925_100155.vi`. The stagexec dry run (tools/bench/dry_l2a1_85b.log:47-48)
lists two unroutable rows after op 36:
- R41 `rw_10988_17272`: bare `min value` output #10988 of Function #10969 -> front-panel ControlTerminal #17272 (sink).
  `wire_indicators` needs a WIRED source (measured limit, tools/gscript.py:1835-1838), so it cannot be used.
- R45 `rw_6007_5082` (+ R46 `rw_6026_5164`): bare OUTER faces of SelectorTunnels #5680 / #6016 (on CaseStructure #5540)
  -> SubVI #5058 inputs `Bead is good? array in` #5082 / `x,y,z array` #5164. Addressing through #5540's Terminals[] is
  ambiguous (two bare '' sources).

Builds (both copy `claudeDev\ops\OpConstWire_v1.vi`, md5 c978863c, built and measured in card 85-1):
1. `tools/recipes/build_opctlsinkwire_v1.py` -> `ops\OpCtlSinkWire_v1.vi`: delete the Constant.Terminal PN; wire the
   Node.Terminals[] IA element into Connect Wire's `Wire Source`; re-type the source TMSC #683 with a Terminal-typed seed
   (create_control on Invoke.reference) and wire it into Connect Wire's `reference`. Call: ladder 1 = Traverse('ControlTerminal')[i]
   (the sink), ladder 2 = Traverse(<source node class>)[j].Terminals[t] (the source).
2. `tools/recipes/build_optunouter_v1.py` -> `ops\OpTunOuterWire_v1.vi`: replace the Constant.Terminal PN by a
   `VI Server:Tunnel` PN reading `Outside Terminal` 6356001, re-type TMSC #683 with a Tunnel-typed seed. Call: ladder 1 =
   Traverse('SelectorTunnel')[i] (the tunnel), ladder 2 = the sink node's Terminals[t] (unchanged from OpConstWire_v1).
Each build negative-tests 20 calls on a D1_k scratch (wrong class -> 1057, no wire, handles flat).
Routing (tools/stagexec.py, both backends): `ctlsink` for a bare node-terminal source into a ControlTerminal sink;
`tunouter` for a bare owner-routed tunnel outer face. Gate on a scratch run of the plan: sole source owner = planned uid,
sole sink = plan sink, ordered second pass Is Broken? False. Rule 1a: same edges as S1.
Round 2 edits (after `unroutable_l2a1_85_build_tun.log` run 1 and review `archive/peer/2026-09-25-hyp-optunouter-uidreuse-85.md`):
`build_optunouter_v1.py` gates the deletion before building, identifies the new PN by its output name `Outer Term` (LabVIEW
may reuse uid 136), and re-reads the old seed wire right before deleting it. `tools/recipes/stage_d1_l2a1.py` (PD191(c)): after
an E1 stop the dry path logs every UNROUTABLE row and returns, instead of dying on UnboundLocalError `real`.
Rejected (PD191): re-cutting {#10969,#17272} into one joint move; carrying the owner's Terminals[] order across the move.
