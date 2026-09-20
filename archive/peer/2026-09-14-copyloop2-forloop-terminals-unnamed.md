---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# copyloop2-forloop-terminals-unnamed

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (79s)
- **why asked:** failed prediction in build_harness_copyloop2 run 1: the For loop node's Terminals[] held one unnamed sink instead of a terminal named N
- **verdict:** unverified

## Question

FAILED PREDICTION, please ATTACK my explanation. Context: LabVIEW 2026 VI Scripting over COM (Python tools/gscript.py driving op VIs). Recipe tools/recipes/build_harness_copyloop2.py, log tools/bench/build_harness_copyloop2.log. I created an EMPTY For Loop with erdosmiller Create For Loop.vi on the top diagram (ExecState 0 = broken, expected since N is unwired). Then I read the loop node via Node.Terminals[] (our OpNodeTerms_v0: Terminal.Name, Is Source?, Connected Wire) and PREDICTED a sink terminal named 'N'. OBSERVED: Terminals[] on the ForLoop node has exactly ONE entry: name '' (empty), Is Source? False, wire 0. My hypothesis: that single unnamed sink IS the loop count terminal (N), and Terminal.Name is empty for structure terminals because the 'N' glyph is not a label. Alternatives to weigh: (a) it is NOT N and N is only reachable via the ForLoop class property 'Count Terminal'; (b) Node.Terminals[] on structures lists tunnels' outer terminals only (none here). Questions: 1) In LabVIEW VI Scripting, what does Node.Terminals[] return for a ForLoop with no tunnels? Is the N (count) terminal in it, and what is its Terminal.Name? 2) What is the documented way to get the count terminal refnum (property name/class)? 3) Is it safe to wire an I32 source (IMAQ GetImageSize 'Y Resolution') into that terminal 0 with Terminal.Connect Wire and judge success by ExecState==1 (an empty loop with N wired is runnable)? Cite NI docs/forums. Already ruled out: the loop is real (Traverse class ForLoop count 1); the node is the loop (its UID matches the Traverse ForLoop UID).

## Answer

Your prediction was directionally right, but the object model behind it is slightly different: terminal 0 is almost certainly the external terminal of the For Loop?셲 **Loop Count tunnel**. Do not rely on its empty `Terminal.Name` or its array index as the durable identification mechanism.

1. `Node.Terminals[]`

NI?셲 For Loop anatomy identifies the N object as a `GObject ??Tunnel`, not merely a generic terminal. Its external wiring endpoint is the tunnel?셲 `Outside Terminal`. The iteration terminal `i`, by contrast, is a separate terminal accessed through `Loop:Loop Counter`. [NI-derived VI Scripting anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html#for-loop-anatomy)

That explains your observation:

- No user-created tunnels exist.
- `Node.Terminals[]` returns one externally wireable sink.
- The internal iteration terminal is not an external sink.
- Therefore, by elimination and object-model consistency, the single unnamed sink is the external endpoint of N.

I found no NI documentation guaranteeing that its `Terminal.Name` equals `""`. Thus, ?쐃mpty because N is a glyph rather than a label??is plausible but unproven. An NI forum discussion explicitly warns that terminal names are not always sufficient identifiers and recommends subclass-specific properties where available. [NI Community: Scripting?봗erminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

Verdict on the alternatives:

- **(a) Partly correct and the safer API model.** N is explicitly reachable through the ForLoop-specific property, and that is how it should be identified. Nevertheless, `Node.Terminals[0]` apparently exposes its external endpoint too.
- **(b) Incorrect as stated.** Structure tunnels are separate objects available through `Structure:Tunnels[]`; the N count object is its own special tunnel obtained through `ForLoop:Loop Count`. [For Loop anatomy](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html#for-loop-anatomy)

2. Documented reference path

The precise property is:

```text
ForLoop:Loop Count
```

It returns a `GObject:Tunnel` reference. Then obtain:

```text
Tunnel:Outside Terminal
```

So the robust route is:

```text
ForLoop ref
  ??Loop Count
  ??Outside Terminal
  ??Connect Wire
```

It is **`Loop Count`**, not `Count Terminal`. The same documentation separately lists `Loop:Loop Counter` for `i` and `ForLoop:Loop End Ref` for the optional conditional terminal. [NI-derived VI Scripting anatomy, lines 92??04](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/anatomy.html#for-loop-anatomy)

3. Wiring and verification

Yes, wiring an actual I32 source to N is type-correct: NI documents both N and `i` as signed 32-bit integers. [NI LabVIEW Fundamentals](https://web.physics.ucsb.edu/~phys13BH/w2014/LV_Fundamentals.pdf)

Calling `Terminal.Connect Wire` on the count tunnel?셲 outside terminal with the I32 source is the correct scripting operation. The method accepts a terminal or node as its wire source. [Terminal `Connect Wire` reference](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

However, **do not use `ExecState == 1` as the only proof that the intended connection was made**. An NI employee notes that `Connect Wire` behaves like the wiring tool and can create a wire that is present but broken. [NI Community: scripting create array indicator](https://forums.ni.com/t5/LabVIEW/scripting-create-array-indicator/m-p/3282674/highlight/true)

Use all of these checks:

1. Obtain N through `ForLoop:Loop Count ??Outside Terminal`, rather than assuming `Terminals[0]`.
2. After connection, verify that N?셲 `Connected Wire` is non-null.
3. Verify the same wire reaches the intended Y Resolution source.
4. Verify the wire is not broken, if your reporter exposes wire status.
5. Finally verify the target VI is runnable/`ExecState == 1`.

For an otherwise empty ordinary For Loop, wiring N should remove the broken state: NI says required block-diagram terminals must be wired, while N supplies the loop count. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) NI separately confirms that the count terminal determines the number of executions. [NI: Build and Configure a For Loop](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YJYFCA4&l=en-US)

Bottom line: terminal 0 is almost certainly N?셲 outside terminal, but your recipe should identify it through **`ForLoop:Loop Count ??Tunnel:Outside Terminal`**, not through its blank name or position in `Node.Terminals[]`.

## Sources

(extract from answer)

## What was done with it

Confirmed on the machine (build_harness_copyloop2.log 14:33): Terminal.Connect Wire on the loop node's single
unnamed sink put wire 346 on BOTH that terminal and GetImageSize 'Y Resolution', ExecState 0 -> 1; HARNESS_copyloop
and HARNESS_copyloop0 saved. The robust route (ForLoop:Loop Count -> Tunnel:Outside Terminal) needs a ForLoop-typed
reference, the same seed-cast gap as the shift-register reader; recorded in docs/NAMES.md. The recipe uses the
single-unwired-sink rule plus the peer's wire-identity check. Verdict: correct.
