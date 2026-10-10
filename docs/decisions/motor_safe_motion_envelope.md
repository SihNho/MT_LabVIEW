---
name: motor-safe-motion-envelope
description: "The user's 2026-09-17 limits within which Claude-driven motor moves cannot damage the assembled rig — ASI never homed and x/y within about 1 mm of the current position, PI magnet translation kept to 0–39 mm"
metadata: 
  node_type: memory
  pinned: false
  originSessionId: b5d0cc76-fda8-4724-8899-5a019fc98595
  modified: 2026-09-27T09:22:12.665Z
type: decision
status: in-force
date: 2026-09-27
source: memory/motor_safe_motion_envelope.md
---

# The motion envelope inside which a scripted move cannot break the rig

On 2026-09-17, with the rig still assembled after an experiment, the user was asked whether a motor command sent
by Claude could drive a stage past its safe range. Their answer defines the envelope. It matters because a
scripted `MOV` bypasses the original VI, and the original VI is where the protection lives.

| axis | what the user said | the limit to enforce |
|---|---|---|
| **ASI stage, up/down (focus)** | "ASI 상하 움직임은 문제가 없음" | no extra limit |
| **ASI stage, x / y (sideways)** | "좌우로 너무 크게 움직이면 문제 가능성 있음" | **(1) never call home / origin; (2) move only within about 1 mm of the position the stage is at now** |
| **PI motor (magnet translation)** | `Max Trans Pos` is set to **40.94**; "만일을 위해 0~39 까지만 움직인다면 문제 없음" | **target always inside 0–39 mm** |

**PI direction (user at the rig, 2026-09-27): 0 mm is the CEILING — the magnet farthest from the sample, where the
reference move's negative limit switch is — and larger mm values move the magnet DOWN toward the sample.** So a
reference move retreats (safe), 39 mm is the closest allowed approach, and when the user says the magnet "looks low"
the question to answer is how LARGE the mm value is. The user is anxious about the magnet sitting low because of the
2026-09-23 incident (a false zero after a controller power-cycle drove the magnet into the hard limit): answer such a
report with the reference-move evidence and the current mm reading, and offer an immediate stop.

The user also explained the mechanism: **in LabVIEW the upper bound is applied by a coerce operation** (the value
is clamped to `Max Trans Pos` before it is sent). So the controller is not what protects the rig; the clamp in the
VI is. Any tool, recipe or new VI of ours that commands these axes must carry the same clamp itself — clamp the
PI target to 0–39, refuse ASI home commands, and refuse an ASI x/y target more than about 1 mm from the position
read at the start — as code that refuses, not as a note to be careful. In the restructured VI the original coerce
must be preserved exactly (it is part of the original's computation); the narrower 0–39 margin is for our own
scripted test moves.

## Controller-side limits (user present, 2026-09-18)

Live verification found that the original VI's magnet bound is only the panel control's Data-Entry range (0…40.84
on `Trans Step (mm)`), which programmatic writes bypass — so the user asked whether the controllers themselves can
hold limits. They can, and the user chose to use them:
- **PI C-863**: `SPA 1 0x15 39.0` / `SPA 1 0x30 0.0` (RAM, lost at controller power-cycle) — measured: `MOV 1 40`
  refused with ERR 7, no motion. The user's design: *set the limits by a hook when a motor session starts and force
  their release when it ends*, with a check at every session start.
- **ASI**: `SL`/`SU` are ABSOLUTE coordinates (same frame as `W X`), persist across power cycles. The user ordered
  **±2 mm around the current position** written into the controller now (*"지금 값을 기준으로 +- 2mm 넣어줘"*):
  `SL X=-3.8475 Y=-4.7744`, `SU X=0.1525 Y=-0.7744`; undo is `SL X=-500 Y=-500`, `SU X=500 Y=500`. The scripted
  envelope (our gate) stays ±1 mm; the controller limit is the outer fence.
- Because SL/SU are absolute, any coordinate-zero change (`HERE`/`ZERO`, or the original VI re-zeroing at start)
  would silently move the fence; that is why those commands stay forbidden and `W X` is re-read after each run.

The first unattended D0 run left the magnet at 30 mm (the original's own startup move). The user did not want it
returned: *"0으로 되돌릴 필요는 현재 없음. 가동 범위 안에서만 움직이면됨"* — the harness never parks the motor on
its own; where the magnet rests is irrelevant as long as every move stays inside the limits. "Return the PI motor
to 0 at startup" is a topic for the final LabVIEW code, to be discussed with the user when that VI is finalised.

## Inside our own VIs: an extra fixed clamp is approved (same day)

After the external gate was shown to work on the real motors, the user asked for the same certainty about mistakes
in our LabVIEW code (*"LabVIEW 코딩에서 상한 하한 관련 실수가 없는지도 확신이 필요함"*). They approved a wiring check
against the original, a run with fake motor subVIs fed out-of-range inputs, and a run gate — and also **an extra
fixed clamp directly in front of the motor subVIs in the VIs we build** (*"추가 고정제한도 있으면 좋음"*). That clamp
is a user-granted, narrow exception to "never change the original's computation": results must stay identical
inside the envelope and may differ only for values outside it; the original's own coerce at 40.94 stays untouched.
The user wants this work done in **its own session**; the plan is `docs/motor-limit-assurance-plan.md`.

The user then added that a **dedicated checking sub-session is a must** whenever a main VI or any motor-driving VI
is built (*"모터 리밋이 정상적으로 걸리는지를 체크하는 하위 세션이 꼭 필요하지 않나 싶음"*): the session that
builds a motor-capable VI must not be the one that certifies its limits. It was raised as a question, so the design
is to be discussed with the user before it is built.

## The permission that goes with it (same day)

Asked whether this changes the rule "assembled rig ⇒ no motors", the user answered: **"조립 상태에서도 이 범위
안이면 모터 허용함. 다만, 정말로 이 범위 안에서만 이동할 수 있는지"** — motors ARE allowed while the rig is
assembled, inside this envelope, and the condition attached is that staying inside it must be *really guaranteed*,
not intended. So the permission is only as good as the enforcement: before any move on an assembled rig, the
refusing clamp must exist in the command path and must have been tested without motion (out-of-range target, ASI
home, ASI x/y step over 1 mm — each refused). A move sent through any path that lacks the clamp is not covered by
this permission. "Experiment running" still means no motors and no camera at all.
