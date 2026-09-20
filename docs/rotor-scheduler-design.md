---
type: reference
status: current
date: 2026-09-14
tags: [docs, rotor]
---

# Adding the rotor to the experiment scheduler

> **DESIGN, agreed with the user 2026-09-12. Nothing is built yet.** Every decision below is the user's; the
> measurements and the code reading behind them are cited so a later session does not re-derive them.

## What the user asked for

> "스케줄러에 row 하나 추가하여 로터 정보도 넣고싶어. 프레임에 영향이 없다면 모터 우선, 그 다음 로터값만큼 변경.
> 만약 순서를 두기 위해서 문제가 생긴다면 동시 명령도 괜찮음. 그리고 로터는 절대값으로" — and, on units, "degree로 하자".

So: **a fourth ROW in `CycleSchedule` holding an ABSOLUTE rotor target in DEGREES**, with the translation stage moved
first and the rotor second.

## What already exists — this is mostly wiring, not new hardware

Read from the working copy on 2026-09-12. The rotor is **already fully plumbed**; it is simply not connected to the
scheduler, only to manual controls.

| where | what is already there |
|---|---|
| `Motor control v5` (diagram 20, the motor loop) | `Send to rot`, `send to rot ref`, `change of rot value ref`, `rot display ref`, `last rot pos`, `Rot VISA in`, `Rot VISA out` |
| front panel | `Rot step (turns)`, `Rot Step (deg) `, `Rot \nSpeed` (=100.0), `Send to Rot`, `1 L-Turn`, `1 R-Turn`, `Current pos rot?`, and the indicators `Rot pos (deg)`, `RotationVISA` |

Degrees was chosen partly because `Rot pos (deg)` is already the readback unit, so the schedule value and the
instrument's own feedback share a unit and no conversion sits in between.

## The table's shape, from the user (2026-09-12)

> "스케줄러의 경우 이벤트 구조 통해서 열 개수가 자동으로 변경되게 했어. 행 개수는 4개로 고정되어야 겠고 열은 내가
> 입력하는 경우에 따라 계속 가변적이어야해. 그리고 해당 루프를 버튼 눌러 돌리기 전에는 스케줄 예약일 뿐이야."

| axis | meaning | size |
|---|---|---|
| **row** | the item — speed, force, wait, **rotor** | **fixed at 4** (3 today) |
| **column** | the cycle | **variable**, resized automatically by the Event Structure as the user types |

This matches what was read from the VI and settles two things. `CycleSchedule` read back as `((0.0,), (0.0,), (0.0,))`
— **3 rows × 1 column**, i.e. three items for one cycle, not three cycles. And the `disabled index (col)` operations on
diagram 47 are **whole-row** access, which is exactly "one item across all cycles". So the rotor is a **4th row**, the
variable-column behaviour is untouched, and the edit path still needs no change.

Third point, and it helps the architecture: **the schedule is only a reservation until the Start button is pressed.**
The scheduler loop therefore sits blocked until then and consumes no core while idle — one less pressure on the core
budget the peer review raised (gate G9 in the restructure plan).

## Where the work actually lands — three sites, two already cleared

| site | verdict | evidence |
|---|---|---|
| the schedule table's edit path (Event case) | **no change needed** | diagram 47 uses Index Array and Replace Array Subset with **`disabled index (col)`**, i.e. whole-row access that does not care how many rows/columns exist |
| sending the command to the controller | **no change needed** | `Send to rot` / `Rot VISA` already exist in `Motor control v5` |
| **splitting a schedule entry into speed / force / wait** | **this is the work** | not yet located; it is the only place that indexes the schedule by item |

## The loop it lives in

Under the 7-loop design (`STATUS.md`), the scheduler is its **own loop**, separate from tracking and from acquisition:

```
[3 scheduler]  next schedule entry -> publish targets (speed, force, wait, ROTOR deg) as local variables
                                          |
[4 motor]      read targets -> A: send translation -> B: poll until arrived
                                -> C: send rotor absolute -> D: confirm -> start the wait
```

**Nothing here touches the frame budget.** The motor loop has been parallel to acquisition since
`4.4_MotorParallelLoop`, so however long a serial exchange takes, the camera is unaffected — the user made this point
explicitly and it is correct. Local variables carry the targets, which neither serialise the loops (a data wire between
loops would) nor enter the UI thread.

⚠️ **Boundary of what the user decided, added 2026-09-16.** The sentence above that is the user's is the *first* one —
the motor loop is parallel to acquisition, so serial cost never reaches the frame budget. **"Local variables carry the
targets" is this document's own reasoning, not a user decision**, and it was once cited in `pre-rig-master-plan.md` as
if it were one, which released a peer correction that should not have been released. That correction stands:
`restructure-plan-4.6.md:59-63` (2026-09-12) shows four non-atomic writes let the motor loop read **a new speed with an
old force**. **The requirement is that the motor never acts on a half-updated target set; the transport is an open
decision** recorded in `pre-rig-master-plan.md` row 1.3 — locals are still a candidate, but only published and consumed
as a set, because a single cluster needs a donor typedef the present op fleet cannot create (`toolkit-capabilities.md`
has no Bundle writer). The block diagram above is the *topology*, not the settled transport.

The earlier caution in this project's notes — that serial cost is "43 % of the 150 Hz budget" — applies to the **ASI**
subVI that sits inside the *frame* loop, not to the PI motor loop. Do not conflate them.

## Sequencing: translation first, then rotor

The user allowed simultaneous commands if ordering proved awkward, but ordering costs nothing here (it is paid in the
motor loop, off the frame path), so **sequence it properly**. A magnet that rotates while it is still travelling gives
the bead a torque history that differs from cycle to cycle; sequencing removes that variable.

State machine in the motor loop, one pass per schedule step: `send translation` → `poll position until arrived` →
`send rotor absolute` → `confirm` → `begin the wait`.

One cost to keep in view: a PI round trip is 2.56 ms and MOV-class commands do **two** round trips, so a step that
moves both axes is roughly 10 ms of serial. That does not touch frames, but it does slow the motor loop's own position
polling — and the user requires position to be read as fast as possible during force ramping. Keep the command bursts
out of the ramping window.

## RESOLVED: multi-turn works, and absolute positioning already exists

Two questions were open — whether the controller accepts a multi-turn angle, and whether absolute positioning exists at
all. Both are now answered, and the answer removes a step from the design.

**Multi-turn is fine.** The user's own usage: *"−7200 입력 후 send to rot 누르면 20바퀴 돌아감. 양수 음수가 나눠지지."*
7200 / 360 = 20, so the controller takes a cumulative angle and the sign selects direction. No 360° wrap.

**Absolute positioning is already implemented.** Reading `Motor control v5_No Recording.vi` (copied to claudeDev, read,
deleted) and an offline byte scan of the same file:

- it calls **`MOV.vi` (absolute) *and* `MVR.vi` (relative)**, alongside `POS?.vi`, `GOH.vi`, `VEL.vi`, `SetCommand.vi`;
- the rotor command node carries a `Ring` input whose items are **`MovePos` / `MovePosRel`** — the absolute/relative
  selector;
- the node shapes are symmetric, two of each (diagrams 6 and 16 for the rotor command, 8 and 13 for the PI position
  command), which is what a case-selected absolute/relative pair looks like;
- **`Pos_degree` is the unit used throughout the rotor path**, so the user's choice of degrees needs no conversion;
- `last rot pos` sits on diagram 0.

A comment inside the VI reads *"This VI is specifically used for 'Min_Track N beads 4.0_Add Rotation Info.vi'"* — this
motor wrapper was written to handle rotation in the first place. Only the scheduler link is missing.

### Consequence: one less step than planned

| earlier plan | final |
|---|---|
| schedule holds absolute → motor computes `step = target − current` → send relative | **schedule holds absolute degrees → pass straight to `Pos_degree` with the Ring set to `MovePos`** |

No software accumulator is needed. Because the controller holds the absolute position itself, the manual
`1 L-Turn` / `1 R-Turn` buttons (relative, `Rot increment (F3)`) can be used mid-experiment without the scheduler's
absolute targets drifting out of step — a failure mode the relative design would have had.

> **LOCATED 2026-09-14 — the zero is `Baseline Startpoint`, an INPUT of `Autonics Motor\SetCommand.vi`.**
> The rotor is an **Autonics** pulse motor (not ASI, not PI — the user said so, and `instr.lib` confirms it: the
> `Autonics Motor` folder holds exactly `Configure.vi`, `SetCommand.vi`, `Close.vi`, which are the three subVIs the
> main VI calls). `SetCommand.vi` carries the comment *"Converting degree into pulse"* and takes:
>
> | terminal | direction |
> |---|---|
> | `VISA resource name`, `Ring` (`MovePos`/`MovePosRel`/`Get Position`/`SetSpeed`), `Numeric`, **`Baseline Startpoint`** | **in** |
> | **`Pos_degree`**, `read buffer`, `read buffer 2`, `VISA resource name Out` | **out** |
>
> **Correction to the rest of this document: `Pos_degree` is an OUTPUT, not the input the schedule writes.**
> The commanded value goes in through `Numeric`.
>
> **What `Baseline Startpoint` MEANS is open.** I claimed it was the zero, reasoning that pulse counts cannot go
> negative — an external search found Autonics documents a signed 32-bit position range, so that premise is not
> safe and the claim is withdrawn. Its saved default is 200.0, unit unknown. See `docs/instrument-libraries.md`.
>
> **This does not block the rotor row** (user: *"configuration은 그대로 쓰면 되는데 왜 자꾸 바꾸려고 하는거야?"*).
> The schedule's rotor row must call `SetCommand.vi` **exactly as the existing `Send to Rot` path does** — same
> `Baseline Startpoint` source, same `Ring`, same everything — with only the commanded value coming from the
> schedule instead of the panel control. Copying the working call makes the new path correct by construction and
> leaves the unknown constant unchanged, which rule 1a requires regardless. The remaining trace is therefore
> "what feeds the existing call", not "what does 200 mean".

**Where zero is: NOT a decision to make — a value already in the code (user, 2026-09-13).** Asked to choose between
"experiment start" and "after manual alignment", the user answered that neither is the question:

> "내 기억이 정확하다면 컨트롤러 절대좌표가 아마 음수를 지원 안해줬을거임. 그래서 임의로 중간지점을 내가 0으로
> 잡은 것 같은데, 이게 정확하다면 main vi 코드 상에 분명 잡혀있을 수 밖에 없음."

That reasoning is decisive. If the controller's absolute coordinate cannot go negative, yet the user types `−7200`
and the rotor turns, then **something in the main VI adds an offset before the command goes out** — and that offset
*is* the zero. So this is a search, not a choice.

**Candidate names, from an offline byte scan of the main VI** (`tools/bench/vi_strings_rotor.py`, read-only, no
LabVIEW). A single extracted string is only a hint — compiled code in the same streams produces convincing ASCII —
but these arrived as a coherent GROUP, which is much stronger:

```
start angle(0)      Auto-reset zero  x4      last rot pos      Current pos rot?  x3
Rot pos (deg)  x6   Rot position             Rot Step (deg)    Rot step (turns)
Pos_degree          MovePos / MovePosRel     MOV.vi            Rot, COM3 9600 / COM2 115200
```

`start angle(0)` and `Auto-reset zero` are the likely mechanism; `last rot pos` / `Current pos rot?` say the software
keeps an absolute position of its own.

**Ruled out, after a wrong guess of mine:** `Cal Zero` / `+ Cal Zero` / `- Cal Zero` are **magnet-motor** presets, not
anything rotor or calibration related — see ARCHITECTURE.md §3. Do not follow them.

**The question the trace has to answer**, reduced to one sentence: *what is the difference between the number the
user types and the number that reaches the controller?* That difference is the zero. Trace backwards from the rotor
VISA write / `MOV.vi` call site through wire topology — never by position, since the diagram was Cleaned Up.

## Backward compatibility, which is a rule-1a matter

Adding a row is *adding* behaviour, not changing existing computation — but an existing 3-row schedule must still
produce **identical** motion. Acceptance: run an old schedule through the new code with the rotor row absent or 0 and
require the translation commands and timings to match the old path exactly.

## Both codebases

The user's 2026-09-12 decision is that the CPU-parallel and GPU builds are **two separate top-level VIs**, not one with
a runtime switch. The scheduler and motor logic are identical in both, so they must live in **shared subVIs** — the two
files should differ only in the loop that calls the tracking kernel. The rotor row is the first feature that will
prove whether that discipline is being kept.
