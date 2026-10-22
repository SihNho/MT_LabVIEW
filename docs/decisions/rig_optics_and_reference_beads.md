---
name: rig_optics_and_reference_beads
description: "2026-10-22 owner facts - 50x oil objective (100x before), SP-5000M 5 um pixels binning 2 (~200 nm/px nominal; the 84 nm in .cal is stale from the 100x objective, owner 2026-10-22), polystyrene reference beads in every run, fixture bead 1 = reference, '16X' = DNA name, LUT 100 nm x ~6 um"
metadata:
  node_type: memory
  type: project
  originSessionId: 8cd8755f-522e-436e-9c93-ffe54f94d31b
  modified: 2026-10-22T06:54:09.181Z
---

User 2026-10-22 (chat): "현재 SP5000M-USB 사용중", "레퍼런스 비드가 있음. 측정을 위해서는 항상 non-paramagnetic streptavidin polystyrene bead를 같이 사용", "지금 bead는 100 nm씩 하고 있고 대략 6 um정도 볼거임", "이전에는 100X oil immersive 쓰다가 지금은 화면 확장을 위해서 50X oil immersive 사용", "DNA 이름임. 50배율로 찍었어" (about the "16X" in the fixture folder name).

Full table with sources: `G:\Codes\LabVIEW2Scr\docs\rig-facts.md` (commit 7c37a6a). Fixture (20260906 ... test) bead 1 = reference bead (z range 0.21 um, frame-to-frame x 0.0085 px, z 4.1 nm); beads 2-5 tethered.

**Why:** pixel size and the reference bead decide every tracking-precision comparison; the .cal file's `pixel distance` 84 nm disagrees with the 50x nominal ~200 nm/px - owner 2026-10-22: "예전 렌즈 사용할 때 기록인듯. (100X)". If 84 was measured at 100x (nominal 100), 50x may be ~168 nm/px; measure it. LabVIEW never uses this number; analysis runs in MATLAB with its own parameters (owner 2026-10-22: "Matlab 분석할때 거기 있는 파라미터 사용함. 그러니 사실 랩뷰에서는 사용 안하는 숫자").

**How to apply:** use bead 1 as the noise floor on the fixture; quote nm figures as nominal until the 50x pixel size is measured; never assume 16X is a magnification. Related: [[script_port_is_a_separate_project]].
