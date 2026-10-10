---
name: verify-wiring-by-scripting-not-screenshots
description: "Verification of generated LabVIEW code (wiring, broken state, instance counts) must be done programmatically, not by screenshot inspection — the user's standing correction"
metadata: 
  node_type: memory
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T02:31:12.617Z
type: decision
status: in-force
date: 2026-08-27
source: memory/verify_wiring_by_scripting_not_screenshots.md
---

# Verify generated LabVIEW code by scripting, never by screenshots

The user corrected this twice in the same project (2026-08-27). First: *"위에 인스트럭션 보면 계속
코드 스크린샷 찍고 마우스 클릭하고 하는 것 같은데, 지금 스크립트 vi 쓰는거 아니야?"* — stop doing
edits by screenshot-and-click when a scripting driver exists. Then, when screenshots were still being
used to *check* the results: *"G cli로 연결상태 확인도 가능하잖아? 그런데 왜 캡처해서 와이어링 상태
보려는거야?"* — connection/wiring state can be checked through G/scripting too, so capturing the
screen to look at wires is the wrong tool.

The standing rule this establishes: **the whole cycle — edit, run, and verify — should be
programmatic.** Screenshots are only for genuinely one-time GUI surgery that scripting cannot reach.
Programmatic verification means things like:

- **VI Scripting "Get Error List"** (VI class invoke node): returns whether the VI is broken and
  every breakage reason — a solid/broken run arrow as data instead of pixels.
- **Diagram traversal** (e.g. lv-scripting's object-enumeration VIs): count SubVI instances, tunnels,
  and wires on the generated diagram and expose the counts on front-panel indicators.
- **COM readback** (`GetControlValue` on the driver's error/status indicators) to pull those results
  into the terminal without touching the GUI.

One subtlety that matters on this project: scripted edits live **in memory** until the driver saves
the target, so out-of-process checkers (LabVIEWCLI on the disk file, byte-level inspection) see the
pristine file, not the edits. A verifier must therefore run inside the same LabVIEW instance (a
checker driver VI read via COM) — or the builder must save the target first.
