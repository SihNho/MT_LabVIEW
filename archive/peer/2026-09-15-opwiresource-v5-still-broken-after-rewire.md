---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, vi-scripting]
---

# opwiresource-v5-still-broken-after-rewire

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (62s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

BRIEF ATTACK (LabVIEW 2026 VI Scripting). tools/bench/build_opwiresource_v5.log: the rewire you approved was performed and its provenance gate PASSED - Owner candidates printed as 241 (reference wire 318, Owner out 523: OpReport_v3 identity node) and 157 (reference wire 639 = the Terms[] Index Array element wire, Owner out 751), the cast that feeds a UID node is 1221, it was fed by 523, I deleted wire 523, ran Remove Bad Wires, rewired cast 1221 reference from Owner out 751, and the gate confirms 751/751 on both ends. BUT ExecState went 1 -> 0 when wire 523 was deleted and stayed 0 after the rewire, so the build stopped. Candidates: (H1) wire 523 was a BRANCH feeding a second sink I did not enumerate, and that sink now has an unwired required reference input - the same one-wire-many-sinks trap I hit twice before; (H2) the rewired wire is BROKEN (type mismatch) even though both ends report the same uid - you already warned that a uid-equality gate cannot see a broken wire; (H3) the VI is actually fine but LabVIEW has not recompiled after a programmatic Remove Bad Wires (you cited a report of exactly that stale-compile behaviour), so ExecState lies until something forces a recompile; (H4) Remove Bad Wires deleted something else I needed when it ran on the transiently broken diagram. QUESTIONS: (1) rank; (2) the cheapest localisation with what I have: I can print every terminal of every node (my walker) and list which sinks have wire 0, which finds an unwired required input in one pass - is there anything cheaper or more direct; (3) for H3, what forces a recompile programmatically and is checking ExecState twice with a small delay meaningful, or must I open/close the front panel or call a specific method; (4) for H2, without a broken-wire reader, is Remove Bad Wires plus a re-read of ExecState a sufficient discriminator - if the wire were broken, Remove Bad Wires should delete it and leave the sink unwired, which my terminal dump would then show as wire 0. Read-only; cite what you read.

## Answer

**Ranking:** H1 > H2 > H4 > H3.

1. **H1 ??most likely.** `ExecState` changed exactly when wire 523 was deleted. A LabVIEW wire can be a tree with multiple branches; deleting its wire reference may therefore disconnect more than the enumerated 523??221 path. NI distinguishes selecting a branch from selecting an entire wire, confirming that branches belong to a larger wire topology. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. **H2 ??close second.** UID equality proves only that both terminals reference the same new wire object. It says nothing about datatype/class compatibility. NI explicitly identifies incompatible terminal types as a cause of broken wires. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

3. **H4 ??plausible, but mostly downstream of H1/H2.** ?쏳emove Bad Wires??operates globally and NI cautions that it can remove wires that are merely temporarily broken while editing. Thus the transient break could have caused additional deletion, but only where something had become broken. [NI documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

4. **H3 ??possible but weakest.** There is precedent for stale type/wire validity until LabVIEW re-evaluates a diagram, including cases corrected by unloading/reloading, rewiring, or force-compiling. That precedent is old and class-specific, so it should not outrank the direct topology/type explanations. [NI known issue](https://www.ni.com/en/support/documentation/bugs/08/archived--labview-8-6-x-known-issues-by-date.html)

**Cheapest localization**

First call **`Compile:VI` with `Force Compile = TRUE` and `Compile Entire Hierarchy = FALSE`**, then reread `ExecState`. The method exists specifically to compile a VI and exposes both flags. It does not require opening the front panel. [Compile:VI reference](https://labviewwiki.org/wiki/VI_class/Compile.VI_method)

If it remains `0`, run your terminal walker once. That is the cheapest reliable structural localization you already possess:

- Dump every sink terminal whose wire UID is `0`.
- Prioritize required inputs and terminals previously fed by Owner out 523.
- Also report every terminal currently claiming wire 751, which tests whether the intended branch set survived.

The only more direct diagnostic is LabVIEW?셲 Error List/Context Help, which names required unwired terminals and type conflicts, but obtaining that programmatically would require another reporter capability. NI confirms the Error List identifies both bad terminals and datatype mismatches. [NI debugging guide](https://lumen.ni.com/pdf/labview101/us/debugging_explanation.pdf)

**H3**

Two immediate `ExecState` reads separated by a delay are weak evidence. `ExecState` is simply a read-only state property??0` means bad and `1` means idle; its documentation promises no delayed recompilation or polling transition. [Execution.State reference](https://labviewwiki.org/wiki/VI_class/Execution.State_property)

Use this sequence:

1. `Compile:VI(Force Compile=TRUE, Compile Entire Hierarchy=FALSE)`.
2. Read `ExecState` once.
3. Only if the compile method is unavailable/fails, unload and reload the VI reference.

Opening/closing the front panel is not the documented compile mechanism. `Compile:VI` explicitly loads neither the panel nor diagram itself, so ensure the target is already in the editable/diagram-loaded state required by your operation. [Compile:VI reference](https://labviewwiki.org/wiki/VI_class/Compile.VI_method)

**H2 discriminator**

Yes?봶ith one qualification:

1. Force compile.
2. If still bad, call Remove Bad Wires.
3. Force compile again.
4. Dump terminals and reread `ExecState`.

If 751 was broken, Remove Bad Wires should remove it; NI defines that operation as deleting all broken wires. The destination should consequently report wire `0`. [Remove Bad Wires API](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/vi/removebadwires.html)

That distinguishes ??51 itself was broken??from ??51 is a valid wire but some other required terminal is unwired.??It is not sufficient without the terminal dump: removal can expose multiple disconnected sinks, and `ExecState == 0` alone cannot identify which one caused the break.

## Sources

(extract from answer)

## What was done with it

H1 first, as ranked: the recipe now dumps every unwired SINK terminal (and everything claiming the new Owner wire)
the moment ExecState is not 1, which is the reviewer's "cheapest reliable structural localisation" using the walker
that already exists — and then re-feeds any orphaned `reference` sink from the same Owner output, since a deleted
branch is the expected cause. `VI.Compile` with Force Compile (for H3) is NOT built yet; it is recorded as the next
op to add if a diagram ever reads broken with no unwired sink and no broken wire, and the recipe deliberately does
not treat two ExecState reads as evidence of recompilation. If the dump shows the new wire itself vanishing after a
Remove Bad Wires pass, that is the reviewer's H2 discriminator and the type mismatch is real.
