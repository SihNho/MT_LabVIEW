---
name: context-help-shows-which-terminal-is-targeted
description: "Keep LabVIEW's Context Help open while hovering: it identifies the exact terminal the cursor snapped to and explains a broken wire, without clicking anything"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T10:45:33.443Z
type: decision
status: in-force
date: 2026-08-27
source: memory/context_help_shows_which_terminal_is_targeted.md
---

# Use Context Help as a live targeting and diagnosis readout

The user taught this (2026-08-27) while GUI wiring was failing repeatedly on 1–2 px terminals:
*"LabVIEW 도움말 띄워놓고 subvi 위에 올려놓으면 도움말 항목이 바뀜. 그리고 target node 근처로
움직이면 node에서 깜빡깜빡 거리지. 그 때 도움말도 어떤 node에 도착했는지 같이 깜빡거리면서
표시해줘"* — with Context Help open, hovering a node switches the help topic, and approaching a
terminal makes the node blink while the help shows which terminal has been reached. They added:
*"노드 연결선에 에러가 났을 때 해당 선 위에 마우스 올리면 (클릭은 하지 말고) 도움말창에서 어떤
에러인지도 보여줘"* — hovering a **broken wire**, without clicking, makes Context Help name the
error.

So Context Help is not a static reference; it is a **live readout for both targeting and diagnosis**,
and both uses are pure hover — nothing is clicked, so nothing can be damaged or mis-selected.

**Targeting.** Hover the node and capture: LabVIEW draws small **diamond markers** on every terminal,
coloured by datatype, and an already-wired terminal shows none. Measuring a diamond's position gives
the terminal's true coordinate. This is decisive for **primitives** (Index Array, To More Specific
Class, …), which have no `Visible Items > Terminals` view to enlarge them; hunting their terminals by
coordinate arithmetic fails silently, and in one session eight consecutive attempts missed because
the assumed row was ~13 px off the real one. SubVI nodes have the terminal-pattern trick instead.

**Diagnosis.** When a wire draws but stays broken, hover the wire and read the reason from Context
Help rather than opening the Error List. It is one hover instead of a window, and it points at the
specific wire rather than listing every problem in the VI.

Two practical notes: the Context Help window relocates itself away from the cursor, so capture the
full screen and find it rather than assuming a fixed rectangle; and an open Context Help window
blocks right-click context menus entirely, so close it before menu work and reopen it for the next
hover.
