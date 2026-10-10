---
name: motor-limits-set-and-released-every-cycle
description: "The user's 2026-09-23 rule — the cycle runner must SET the controller motor limits at every cycle start and RELEASE them at every cycle end, each verified by readback, so limits never stay on the rig unnoticed when the user starts an experiment"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: 1e5293f3-09a7-4b72-9393-fcba8dd55703
  modified: 2026-09-23T04:13:07.120Z
type: decision
status: in-force
date: 2026-09-23
source: memory/motor_limits_set_and_released_every_cycle.md
---

# Controller motor limits: set at cycle start, released at cycle end, verified both times

On 2026-09-23, as the user was about to start an experiment, they asked whether the motor limits were released.
They were not: `motor_gate.py --session start` had written the safe-motion limits into the PI and ASI controllers on
2026-09-18 and `--session end` had never been run, so the ASI stage was still confined to a ±2 mm window and the
magnet to 0–39 mm five days later. The user believed a hook already did this each cycle; it did not — only the
gateway command existed. Their instruction:

> "게이트로 해줘. 그리고 훅으로 묶어서 매 사이클마다 시작할때는 묶고, 종료시에는 풀고. 그 다음 각 싸이클 시작 및
> 종료 시점마다 제대로 리밋 셋팅 되어있는지 확인하도록 훅에 추가하고"

The release was done through the gate (rig state temporarily 조립, one `--session end`, readback PI 0–52 mm and
ASI ±500 mm, position unchanged, then back to 실험중), and `tools/cycle_runner.py` gained `motor_limits_hook`
(commit bcb0bb6).

## How I apply it

- The runner, not a session and not a person, sets the limits before every cycle and releases them after every
  cycle, and each is verified by the gate's readback lines; a start that fails verification stops the runner
  before the cycle, an end that fails stops it after and writes the failure into STATUS.
- In rig state 실험중 or unknown the hook sends nothing and logs the skip: the serial ports belong to the user.
- When the user announces an experiment, check the controller limits first and say their current state in one
  line; never assume a previous session released them.
- A safety setting whose "undo" is a command nobody is obliged to run is not a safety setting. Anything set on
  the hardware for a session must have its release in the same mechanical loop.
