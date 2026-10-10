---
name: hardware-never-operate-asi-piezo-superseded
description: SUPERSEDED 2026-09-16 — the ASI piezo no longer has its own permission rule; hardware access is decided by rig state alone (see hardware_operation_permission.md)
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 6564f349-1de2-4ed3-9a30-327eb21b9046
  modified: 2026-09-16T04:54:21.660Z
type: decision
status: superseded
date: 2026-09-16
source: memory/hardware_never_operate_asi_piezo_stage.md
superseded_by: hardware_operation_permission
---

# Superseded: the ASI piezo is no longer a special case

This memory used to say that the ASI piezo stage must never be actuated on this magnetic-tweezers rig, because it
can collide and physically break parts, and that every other instrument the original VI controls is safe to
operate. It was treated as an exception that survived every later permission change.

**The user retired that carve-out on 2026-09-16**, in the same message that introduced the rig-state permission
table:

> *"이는 Piezo stage인 ASI 컨트롤러를 포함하는 내용 (ASI와 다른 모터를 구분하여 권한 두지 말것)."*

So the ASI is now governed exactly like the PI translation motor, the rotor and the magnet motor: allowed while
the rig is **disassembled**, forbidden once it is **assembled**, forbidden **during an experiment**. The live rule
is in `hardware_operation_permission.md`.

Keep this file only so that an old summary quoting "never operate the ASI piezo" can be recognised as out of date.
