---
name: diagram_layout_by_direct_coordinates
description: "2026-10-19 - block-diagram tidy of the product VI = direct coordinate placement (not Clean Up / Shrink Wrap); GUI resize allowed only for structure size on scratch + P6L byte copy; future builders keep code inside their loop's zone"
metadata:
  node_type: memory
  type: project
  originSessionId: 352cf43e-6115-43ef-a77e-e8ccfae2d90c
  modified: 2026-10-19T12:49:51.961Z
---

User decisions on the diagram layout (2026-10-19, after Claude-GPT discussion bd-layout, "둘 다 동의함"):
- Problem: "코드 위치가 너무 사방팔방임" - layout only; structures too big; others cannot read the code. The user's own Clean Up Diagram also failed ("나도 clean-up diagram 해봤거든? 그런데 안되더라고").
- Route: direct coordinates (sizes inner -> outer, positions outer -> inner, read back each move). Whole / selection Clean Up and Shrink Wrap are out; subVI split of loop bodies is a later, separate question.
- GUI resize allowed only when no scripting route exists: size of While / For / Case / Flat Sequence only, our scratch VIs and the P6L byte copy only, via tools/lv_gui.ps1 with recorded exception + evidence.
- Future builds: "이번에 정리해도 새로 만들때 또 온갖 이상한 곳에 만들 수 있잖아" -> one zone per top-level loop, no arbitrary absolute coordinates, layout gate after save + reopen (contents inside their structure, coordinates within +-30000).

**Why:** Clean Up cannot target one nested structure (measured) and froze LabVIEW on the whole P6L; P6L passes the 16-bit coordinate limit, which already made LabVIEW move objects on save.
**How to apply:** layout tasks follow docs/d1/layout.md PD421; every new VI build card carries the zone rule and the layout gate. Related: [[measure_before_more_structure_checks]].
