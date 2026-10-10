---
name: rotor-follows-signed-hardware-count
description: "The rotor motor is signed by nature; LabVIEW's serial path once lost the sign and the fix is now known — so the new VI must use SetCommand_signed.vi and follow the hardware number, sign included (user, 2026-09-16)"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 97b1695e-68c2-4985-8cac-1ca3097b3b15
  modified: 2026-09-16T12:52:49.402Z
type: decision
status: in-force
date: 2026-09-16
source: memory/rotor_follows_signed_hardware_count.md
---

# The rotor is signed. The new VI follows the hardware number, sign included.

On 2026-09-16 two project documents disagreed — `pre-rig-master-plan.md` said "unsigned `SetCommand.vi` only",
`questions-for-user-2026-09-14.md` said "use `SetCommand_signed.vi`". The user settled it:

> *"로터는 본래 부호 인식이 가능했으나 랩뷰 시리얼 통신에서 부호 인식이 안되는 문제가 있었음. 이제는 해결 방법을
> 찾은 것 같으니 부호를 포함하여 하드웨어 숫자 그대로 따라가야함."*

So: the controller itself always understood signed angles; the unsigned workaround existed only because the
LabVIEW serial path dropped the sign. That path is believed fixed now, so **the new VI uses
`SetCommand_signed.vi` and mirrors the hardware count exactly, negative values included** — no unsigned
wrapping, no offset baseline (the old 100,000 baseline is gone; the counter is at 0).

The user said "해결 방법을 찾은 것 같으니" — *seems* found. The sign round-trip on the real serial link is therefore
still a measurement to make while the rig is disassembled (CLAUDE.md 1b already lists "the rotor negative-angle
check on `SetCommand_signed.vi`" as expected work in that state), not a settled fact to build on blindly.
