---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# wire-silent-fail

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** ANSWERED (75s)
- **why asked:** Programmatic wires on OpWire_v1 completed with no error but created nothing (Wire count unchanged) - why?
- **verdict:** adopted

## Question

LabVIEW VI Scripting question. Using scripting (Connect Wire / a library like erdosmiller lv-scripting whose 'Wire Inputs.vi' internally uses a 'Conditionally Connect Wire' helper), a programmatic wire between two valid terminals (a subVI's 'error out' output and another subVI's 'error in (no error)' input, same diagram) completes without any error but NO wire object is created - the diagram's Wire count is unchanged. The same tooling created wires successfully on another VI earlier. Questions: (1) Under what conditions does LabVIEW's scripting Connect Wire silently fail / decline to create a wire? (e.g. target VI not open in editor? terminals belonging to node instances whose underlying subVI is currently running/reserved? type mismatch? already-wired terminal?) (2) Does the target VI need its front panel or block diagram open for wire creation to work? (3) Is there a known issue wiring ERROR cluster terminals specifically via scripting? Search NI forums and LAVA; cite URLs.

## Answer

Short answer: an open front panel/block-diagram window is not required, and I found no documented error-cluster-specific scripting defect. The strongest suspects are that the destination VI is not editable/reserved, the helper deliberately skipped the operation, or the terminal references do not identify the instances/terminals you think they do.

1. Conditions that prevent or decline wiring

- **Target VI running or reserved for execution:** `Terminal.Connect Wire` is explicitly marked ?쏶ettable when the VI is running: No.??LabVIEW also prevents source-code changes when a VI is running or reserved because those changes require recompilation. [Connect Wire method metadata](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method), [NI forum discussion](https://forums.ni.com/t5/LabVIEW/Creating-control-on-front-panel-using-VI-scripting/td-p/3907493)

  Check the edit state of the **VI whose diagram owns the two subVI-node instances**, not merely whether either called subVI?셲 panel happens to be running. A called subVI being separately busy is not, by itself, documented as preventing edits to an otherwise idle caller. However, if the target VI is part of a reserved running hierarchy, it is not editable.

- **A conditional wrapper skipped the primitive call:** this is particularly plausible with `Wire Inputs.vi` and a helper named `Conditionally Connect Wire`. The library is an abstraction over native VI Scripting, so ?쐍o error??can mean its condition evaluated false rather than that LabVIEW attempted and rejected `Connect Wire`. [erdosmiller/lv-scripting repository](https://github.com/erdosmiller/lv-scripting)

  Inspect or report the helper?셲 predicates and expose a result such as `attempted?`, `already wired?`, and `compatible?`. This is the first thing I would test.

- **Wrong object level or wrong terminal reference:** `Connect Wire` must be invoked on a terminal, with another terminal or node supplied as `Wire Source`. NI/LAVA examples show failures and unintended connections caused by passing the node instead of its terminal or selecting the wrong `Terminals[]` entry. [NI terminal-vs-node example](https://forums.ni.com/t5/LabVIEW/Connecting-wires-to-build-array-through-VI-Scripting/m-p/3092652/highlight/true), [NI wrong-terminal example](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/Wrong-connections-by-connect-wires-method-in-vi-scripting/td-p/3372667), [LAVA example](https://lavag.org/topic/17674-add-a-new-invoke-node-to-the-block-diagram/)

- **Already-wired sink:** an input terminal accepts one source. A conditional helper may intentionally treat ?쏿lready connected??as a no-op. Native interactive wiring normally replaces/reconnects or produces a wiring operation, but I found no authoritative statement that native `Terminal.Connect Wire` must replace an existing input wire. Therefore verify `Terminal.Wire`/connected status before calling rather than assuming replacement.

- **Source/sink orientation:** invoke `Connect Wire` on the intended `error in` terminal and pass the `error out` terminal as `Wire Source`. The method?셲 documented model is ?쐁onnects a wire to the terminal??from the supplied source. [Connect Wire method](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method)

- **Type or direction mismatch:** type mismatch normally produces a **broken wire**, not no wire. An NI employee specifically describes `Connect Wire` as behaving like the wiring tool and notes that the resulting wire can be broken. Thus a pure type mismatch is a weak explanation for an unchanged wire count. [NI scripting example](https://forums.ni.com/t5/LabVIEW/scripting-create-array-indicator/td-p/3282674), [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

- **Stale references:** if nodes were replaced, deleted/recreated, connector panes changed, or references were cached across scripting operations, the refs may no longer represent the displayed instances. I found no source documenting this exact silent symptom, so treat it as a hypothesis. Reacquire both node references from the target diagram immediately before wiring and identify terminals by connector-pane identity/name?봭ot a historically assumed `Terminals[]` index.

2. Must the panel or diagram window be open?

**No.** The method metadata says it loads neither the front panel nor block diagram into memory, and NI?셲 scripting tutorial explicitly performs wiring programmatically and only later says to run the scripting VI, which creates and opens the generated VI?셲 windows. A visible editor window is therefore not a prerequisite. [Connect Wire metadata](https://labviewwiki.org/wiki/Terminal_class/Connect_Wire_method), [NI VI Scripting wiring tutorial mirror](https://rajsite.github.io/unofficial-lvdocs/lvhowto/wiring_scripting_objects.html)

The distinction is:

- Window visibly open: not required.
- Diagram present and target VI editable: required in practice.
- Diagram removed from the VI: editing is impossible. [NI forum discussion](https://forums.ni.com/t5/LabVIEW/Can-not-edit-my-program-I-know-about-edit-mode/td-p/90890)

Opening the diagram is still a useful diagnostic because it confirms edit mode and lets the manager inspect broken or hidden wiring, but it should not be the fix.

3. Error-cluster-specific issue?

I found **no NI-forum or LAVA report establishing a special `Connect Wire` failure for error-cluster terminals**. LAVA examples traverse and inspect error-cluster-related wiring normally, and ordinary LabVIEW documentation treats error clusters as normal cluster dataflow terminals. [LAVA error-terminal scripting example](https://lavag.org/topic/19370-need-some-scripting-ninja-help-finding-constants/), [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

Recommended cheap check:

1. Confirm the target/caller VI is `Idle` and not reserved.
2. Bypass `Wire Inputs.vi` and call native `Terminal.Connect Wire` once: invoke on `error in`; supply `error out`.
3. Immediately reacquire the target diagram?셲 `Wires[]` and both terminals??connected-wire properties.
4. If native wiring succeeds, instrument `Conditionally Connect Wire`; its predicate is the cause.
5. If native wiring still does nothing, reacquire the two subVI-node instances and report terminal index, terminal name, direction, type descriptor, owner chain, and existing-wire status.

Given the unchanged count and absence of an error, my ranking is: **conditional helper skipped > stale/wrong terminal reference > target VI reserved > existing sink wire > type mismatch > error-cluster defect**.

## Sources

(extract from answer)

## What was done with it

Codex's 'target must be fully loaded/editable' framing pointed the right way; its claim that an open panel is not required was contradicted empirically - OpenFrontPanel on the target made the identical wire succeed immediately (GetVIReference alone does not load the diagram for editing). Rule codified in gscript.open_panel/close_panel and the skill.
