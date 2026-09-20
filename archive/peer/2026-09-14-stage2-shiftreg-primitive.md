---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2]
---

# stage2-shiftreg-primitive

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (145s)
- **why asked:** stage-2 assembly needs shift registers (the kernel's x,y,z / good-flags / pos-in-cal feedback) and no
  op in the fleet wrote one; the plan proposed to use erdosmiller `Exit While Loop.vi`'s never-exercised
  `Shift Registers` input. Mandatory pre-construction review (CLAUDE.md rule 5).
- **verdict:** **ACCEPTED and acted on.** The reviewer refused the plan and named a documented creation API,
  `Loop.Add Shift Register` **6361000** — which this project had ALREADY catalogued at `docs/NAMES.md:234` ("not yet
  verified on this machine") and the plan had missed. Confirmed locally by grep before acting on it. Two secondary
  points adopted: `Terminal.Connect Wire` direction (invoke on the SINK, `Wire Source` = the source), and the
  demotion of the three-depth-1-queue fallback (no atomic tuple alignment; a blocked dequeue with timeout −1
  deadlocks with no recoverable previous state). **One caveat against the answer:** the reviewer could not read the
  erdosmiller VI at all (`AGENTS.md` forbids peers opening `.vi`), so everything it said about that library input is
  inference rather than measurement — which is precisely why the plan should not have rested on it either.

## Question

ATTACK THIS PLAN, do not confirm it. Context: LabVIEW 2026 VI Scripting driven from Python/COM, building a producer-consumer tracking VI by script only (zero GUI). Read docs/stage2-assembly-step-a.md and docs/stage2-plan.md in this project directory first.

Claims to attack:
(1) erdosmiller LV-Scripting "Exit While Loop.vi" has a "Shift Registers" input which, given terminal references of outputs of a node INSIDE the loop body, creates shift registers wired from those outputs. Open the library source under C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting and say what that input ACTUALLY does. Does it expect existing shift-register refs? booleans? Which side does it leave unwired?
(2) The plan then wires the LEFT shift register terminals with Terminal.Connect Wire (method 6349C03), reference = SINK terminal, Wire Source = source. Is Connect Wire direction-sensitive in that way? Can a LeftShiftRegister Inside/Outside Terminal legally be an endpoint? Is there a DIFFERENT documented scripting route to CREATE a shift register (a Loop method, a New VI Object style, a writable WhileLoop property)?
(3) Attack the declared fallback: three depth-1 queues standing in for three shift registers inside ONE While loop (dequeue at the top, enqueue of the kernel result at the bottom, seeded once before the loop). Name a concrete way that deadlocks, reorders, or differs numerically from a shift register in LabVIEW dataflow/clumping - or say plainly that it cannot.
(4) Name the single cheapest discriminating test separating "the Shift Registers input works as assumed" from "it does not".
Cite file paths and NI documentation URLs you actually read. Read-only: change nothing.


## Answer

The plan should not proceed as written. It overlooks LabVIEW?셲 direct `Loop.Add Shift Register` scripting method, and its claim about the Erdos Miller input is not yet established by admissible evidence.

I read [stage2-assembly-step-a.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-a.md), [stage2-plan.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-plan.md), [STATUS.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/STATUS.md), and the relevant non-archive reports/code. I changed nothing and did not run or open LabVIEW.

1. Erdos Miller `Exit While Loop.vi`

The installed connector/report evidence establishes:

- `Shift Registers` is an input/output pair at connector indices 7/8.
- The project feeds its input from `Get Outputs`, so its actual datatype is an array of terminal references?봭ot Boolean flags and not a Boolean ?쐁reate???array.
- It therefore does not appear to expect existing `LeftShiftRegister` or `RightShiftRegister` object references. The intended inputs are source terminal references associated with values leaving the loop.
- If it follows ordinary shift-register direction, those sources must be connected to the right register?셲 inside sink. The new left register?셲 outside initialization sink and inside body source necessarily remain unwired until separate wiring is performed. NI describes the same data direction: data enters the right terminal after an iteration and becomes available from the left terminal on the next iteration. [NI: Using Shift Registers](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO&l=en-US)

However, I cannot truthfully say I inspected the implementation of the installed VI. `AGENTS.md` explicitly forbids opening any `.vi`, including this vendor VI. The GitHub repository confirms that LV-Scripting is open-source, but its published web view does not expose this compiled VI?셲 block diagram text. [Erdos Miller LV-Scripting repository](https://github.com/erdosmiller/lv-scripting)

Consequently, the exact implementation and exact returned terminal side remain unproved. The manager must provide a plain-text reporter dump of:

`C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Exit Loop.vi`

That is the evidence needed to distinguish ?쐓ource terminal references used to create right-side connections??from any more complicated internal treatment. The current plan improperly promotes that inference to a construction contract.

2. `Terminal.Connect Wire` and the missed direct API

`Connect Wire` is direction-sensitive in precisely this sense:

- Invoke it on the destination terminal.
- Supply the original source terminal or source node through `Wire Source`.

The method documentation says it ?쐁onnects a wire to the terminal??and calls the argument ?쐔he original source of the wire.??[Terminal.Connect Wire, ID `6349C03`](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

Therefore:

- Left shift-register **outside** terminal: legal sink for initialization; invoke `Connect Wire` on it.
- Left shift-register **inside** terminal: legal source for the loop body; pass it as `Wire Source` while invoking on the kernel-input sink.
- Reversing either call is not justified.
- Both are legal terminal endpoints because `LeftShiftRegister` inherits `Tunnel`, which exposes the ordinary inside/outside terminal references. [LeftShiftRegister class](https://labviewwiki.org/wiki/LeftShiftRegister_class)

The bigger defect is that the plan calls shift-register creation a ?쐌issing primitive??while its own [NAMES.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/NAMES.md) already records the direct API:

- `Loop.Add Shift Register`
- Method ID `6361000`
- Input: `Y Position` (`U32`)
- Return: `RightShiftRegister` reference

It directly ?쏿dds a shift register at the specified location on the frame of the loop.??[Loop.Add Shift Register](https://labviewwiki.org/wiki/Loop_class/Add_Shift_Register_method)

That is the documented creation route the plan should try first. It is substantially cleaner than using `Exit While Loop.vi` as an undocumented side-effect generator. I found no writable WhileLoop property or `New VI Object` style that should be preferred. The direct Loop invoke method is the answer.

Once created, traverse from the returned right reference to its left register(s), or use the loop?셲 register collection. A left register?셲 `Right Shift Register` property is read-only, and `Add Element` creates stacked history elements; neither creates the initial pair. [LeftShiftRegister class](https://labviewwiki.org/wiki/LeftShiftRegister_class)

3. Three depth-1 queues are not unconditionally equivalent

Under very strict assumptions?봢ach queue is seeded exactly once, every iteration performs exactly one successful dequeue and one successful enqueue on each queue, operations have infinite timeouts, nobody else touches the queues, and all three operation chains are dataflow-ordered?봳he queues cannot reorder values. LabVIEW queues are FIFO, so each iteration receives the prior iteration?셲 value. [NI: What Is a Queue?](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P7OfSAK&l=en-US)

But the fallback is still operationally different and has a concrete deadlock:

- Suppose dequeue succeeds on `Q_x`.
- The `Q_good` dequeue then blocks forever because its seed was absent, consumed accidentally, or its queue reference/error path is invalid.
- The loop never reaches the three bottom enqueues.
- `Q_x` is now empty too, so there is no recoverable ?쐏revious iteration state.??
With default timeout `-1`, dequeue on an empty queue and enqueue on a full bounded queue can wait indefinitely. NI explicitly documents blocking when a bounded queue is full, and the same queue timeout semantics apply to removal from an empty queue. [NI queue blocking guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000002WyH0AU), [NI Community explanation](https://forums.ni.com/t5/LabVIEW/Queue-are-blocking-calls/td-p/3730372)

Three separate queues also lack atomic tuple alignment. If one operation times out, errors, is conditionally skipped, or a shutdown releases one queue before the others, `x/y/z`, bead-good, and calibration-position state can become iteration-skewed. A three-field cluster in one depth-1 queue would at least make alignment atomic.

Numerically, in the fault-free strict case, the queue mechanism should not change the array values merely because it is a queue. But it differs in scheduling, allocation/reference lifetime, error behavior, shutdown behavior, and persistence semantics. An uninitialized shift register retains its value between VI executions while the VI remains in memory; a seeded queue represents explicitly created runtime state and does not have that behavior. [NI: uninitialized shift-register persistence](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019OlISAU&l=en-US)

4. Cheapest discriminating test

One scratch loop, one typed source terminal, one call:

1. Record `Loop.Shift Registers[]` count.
2. Call `Exit While Loop.vi` with exactly that source terminal in `Shift Registers`.
3. Read the count again.
4. If it increased by one, inspect only that returned right register:
   - right inside terminal has the source?셲 wire;
   - left outside and left inside terminals are unwired.

This is cheaper and more discriminating than the proposed accumulator. It tests the disputed Erdos Miller behavior in one invocation without first building either left-side wiring op. If count stays unchanged?봮r the new right-inside wire does not match?봳he assumption is false.

My stronger recommendation is to skip that uncertainty and make the first test a single `Loop.Add Shift Register(6361000)` invocation. It is the documented creation API, returns the `RightShiftRegister` reference directly, and removes the largest unsupported premise from step A.

## Sources

(extract from answer)

## What was done with it

`docs/stage2-assembly-step-a.md` was rewritten around the direct method (section "REVISED 22:5x by the peer review");
the `Exit While Loop` side-effect route was not touched. Build + functional test:
`tools/recipes/build_opaddshiftreg_v0.py` (`OpAddShiftReg_v0` = `OpWhileCast_v0` + Invoke 6361000 on its typed
WhileLoop reference), log `tools/bench/build_opaddshiftreg_v0.log`.

**First run, 22:30 — the method is NOT private:** the Invoke node came back carrying `Add Shift Register` and
`Y Position` terminals, so `6361000` attaches through the ordinary builder. The batch then stopped on a failed
prediction of the recipe's own making (a gate on `ExecState == 1` placed before `Y Position` was wired); that failure
has its own review, `2026-09-14-addshiftreg-fail1-branch-or-decline.md`.
