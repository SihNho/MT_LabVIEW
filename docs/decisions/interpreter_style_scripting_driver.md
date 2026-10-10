---
name: interpreter-style-scripting-driver
description: "Build the scripting driver as a command interpreter (script lines → primitive ops), not as a one-shot monolithic builder VI — the user's architectural directive"
metadata: 
  node_type: memory
  originSessionId: 1ffa4eb9-19ac-4240-b7d7-6ef33fffb8c1
  modified: 2026-08-27T06:08:32.813Z
type: decision
status: in-force
date: 2026-08-27
source: memory/interpreter_style_scripting_driver.md
---

# The scripting driver must be an interpreter, not a one-shot builder

After watching the monolithic `KernelBuilder_v1.vi` fail opaquely (2026-08-27 — an unwired input
deep in its fixed chain cost hours of pixel-forensics), the user stopped the work and dictated the
architecture: *"화면 캡처, 마우스 클릭 대체할 수 있는 모듈만 만들어. 스크립트로 타겟 vi, 타겟
노드, 타겟 subvi 등을 다 지정할 수 있게 하고 혹은 control/terminal 생성 가능하도록. 그리고
스크립트로 function call을 계속 하는거야. 한 번 실행에 script 수백줄 넣으면 수백번 코드가
돌도록."*

The shape this dictates:

- **One generic driver VI (an interpreter)** whose front panel takes a LIST of commands (set via
  COM as a string array, e.g. JSON lines). One Run executes hundreds of primitive operations in
  sequence. Editing the build = editing the script text, never the driver's diagram.
- **Primitive command set**, each mapping to an lv-scripting/VI-Scripting call: open target VI,
  get diagram, create node/subVI/structure at position, get terminal by name, wire A→B, create
  constant/control/indicator on a terminal, set property, save instrument, close refs.
- **A handle registry** inside the interpreter (name → refnum map) so later lines can reference
  objects created by earlier lines.
- **Per-line status log** exposed as an indicator array, read back via COM after the run — errors
  localize to a script line instead of "somewhere in the chain".
- The workflow becomes *write script → run once → read log/check once*, not
  *edit driver VI → run → screenshot-verify*, and the driver VI itself almost never needs GUI
  surgery again.

The user's summary of why: a single fixed-chain builder run is worth only "one script line" anyway
(*"코드 한 번 실행이 script 한 줄이나 마찬가지잖아"*), so generality must live in the script, not
in the diagram. This complements (does not replace) the standing rules: reuse erdosmiller
lv-scripting for the primitives, inputs as FP controls, and verify by scripting rather than
screenshots.

The user later sharpened the division of labour (2026-08-27): *"기본적이고 바꿀 필요 없는 기능을
Scripting vi로 구현하고, 나중에 너가 function call script를 짜서 기본 기능들을 구현"* — the
G-side implements only basic, never-changing functions (the frozen primitive set), and Claude
composes them from script files per task. Rationale: future code shape is unknown and **more VIs of
other kinds will keep being built on this same setup**, so the interpreter must stay small, general,
and project-agnostic (ties into the portability rule: this tool travels to the user's other LabVIEW
projects).
