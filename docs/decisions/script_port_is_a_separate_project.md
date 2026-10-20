---
name: script_port_is_a_separate_project
description: "2026-10-20 - moving the tracking program from LabVIEW to a script language is wanted (maintenance, future Andor iXon) but planned as a SEPARATE project, not inside V6; language not chosen yet"
metadata:
  node_type: memory
  type: project
  originSessionId: 8cd8755f-522e-436e-9c93-ffe54f94d31b
  modified: 2026-10-20T08:36:08.085Z
---

User 2026-10-20 (chat): "나중의 관리를 위해서라도 스크립트로 바꾸는게 좋을 것 같은데", "추후에 Andor IXon도 연결해야 하니까", then "이거는 별도 프로젝트로 기획하는게 좋겠다".

Facts gathered in that chat: every device already has a script route - PI M-126 (PIPython), ASI TG-1000 (serial text; TigerASI), Autonics rotor (serial text, already driven by tools/motor_gate.py), JAI SP-5000M-USB (eBUS Python API or niimaqdx.dll ctypes), Andor iXon (SDK2: pyAndorSDK2, pylablib). Chat recommendation (NOT yet a user decision): Python orchestration + numpy/numba, only measured-too-slow kernels in C; camera behind one interchangeable interface (JAI now, iXon later).

**Why:** LabVIEW scripting itself caused most recent blocks (16-bit coordinate wrap, re-placement on save, GUI fallbacks); text code is easier for the lab to maintain; iXon would need a new camera path in LabVIEW anyway.

**How to apply:** do not start porting work inside V6 cycles; V6 work (P6L, GPU, rig ABBA) continues as is. The port gets its own project/folder and plan, started only on the user's word. Open for the user: language choice, numeric-identity tolerance vs the original (rule 1a), iXon model. Suggested first step: read-only inventory of what the original VI calls (no LabVIEW). Related: [[gpu_acceptance_by_reference_bead_experiment]].
