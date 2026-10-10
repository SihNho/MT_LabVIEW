---
name: pi-reference-at-every-cycle-start
description: "The user's 2026-09-23 rule after a near-accident — every cycle start MUST re-reference (home) the PI magnet stage and then compare commanded vs read-back coordinates before any move; a power-cycled controller reports 0 wherever the stage physically is, and trusting that number drove the magnet into the hard limit"
metadata:
  node_type: memory
  pinned: true
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-23T04:37:55.140Z
type: decision
status: in-force
date: 2026-09-23
source: memory/pi_reference_at_every_cycle_start.md
---

# Re-reference the PI stage at every cycle start, then compare real and reported coordinates

On 2026-09-23 the user asked me to test the PI magnet stage (0 → 30 → 0 mm) because it "did not respond" to the
main VI. Two things had happened: the controller had been power-cycled (which resets its position counter to 0
at whatever physical spot the stage is in, and leaves the servo off), and my gate's session-start step then
"restored the reference" by declaring that current counter as the true zero (`RON 1 0` + `POS 1 <current>`).
The stage was physically at about 30 mm while the controller said 0, so my "move to 30" drove it +30 mm into the
hard limit switch at the end of travel (stopped at 22 mm, controller error 216). Only a real reference move
(`FNL 1`, to the negative limit switch, 30.6 mm back) restored the true zero. The user's words:

> "와... 난리 날뻔했네. 반드시 싸이클 시작할 때는 PI 모터 원점 복귀 반드시 시킨 후에 실제 좌표와 아웃풋 좌표
> 비교하는거 반드시 만들어"

## How I apply it

- **A controller's reported position is not the physical position** until a reference move has been done in
  this power cycle. A reading that jumped (30 mm at 13:10, then 0 after a power-cycle) is a lost reference,
  never "the stage moved". Stop and re-reference; never define the current counter as zero.
- **Session start = reference first, then verify**: `motor_gate.py --session start` runs `FNL 1` (0 = negative
  limit switch, the convention the limits file's TMN 0 assumes), requires `FRF? 1`, then performs a small
  verification move inside the envelope (0 → 2 mm → 0) and compares commanded vs read-back positions within a
  tolerance; any mismatch, timeout or controller error refuses the session, and the cycle runner then does not
  start the cycle.
- The servo must be on before any move (`SVO 1 1`); after a power-cycle it is off and every `MOV` answers ERR 5.
- A reference move is a physical motion of the whole travel; it is only ever done through the gate, in rig state
  assembled or disassembled, never in 실험중, and the user should be told it will happen when they start a runner.
- The near-miss was my error in judgement: the evidence (position jump, ERR 5) was on the screen before the move.
