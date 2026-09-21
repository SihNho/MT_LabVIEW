# c64-execstate-recompile

- **agent:** claude
- **role:** fact
- **model:** fable (effort low; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $3.4293  in 48 / out 11608 / cache-create 62004 / cache-read 1091556  (306s, 39 turn(s))
- **date:** 2026-09-21 12:32:21
- **outcome:** ANSWERED (307s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# API FACT QUESTION — LabVIEW ActiveX / VI Server: does a scripting read/edit leave `VI.ExecState` stale at 0, and can a recompile be forced over ActiveX?

This is a pure API-fact question about LabVIEW's own ActiveX / VI Server interface (LabVIEW 2026, Windows,
driven from Python via `win32com` `LabVIEW.Application`). Search NI's documentation, the LabVIEW VI Scripting
property/method reference, NI forums and any other external source. Answer with facts and citations (URLs),
not with an opinion about our project.

## The observation that motivates it

Driving LabVIEW over ActiveX, we call a scripting op VI that (a) reads the property `Wire.Is Broken?`
(property short-name id `6371004`) off a wire reference obtained from a terminal reference, and (b) invokes
`Terminal.Connect Wire` on a nested block diagram. After an IDEMPOTENT connect that creates no new wire at all
(wire count unchanged 1905 -> 1905, the op returning an empty error cluster and `Is Broken? = False`), the
owning VI's `VI.ExecState` flips from 1 (Good/runnable) to 0 (Bad/broken) and STAYS 0 for at least 14 seconds
across eight re-reads, across a released-and-reacquired VI reference, and across a dropped-and-recreated COM
Application proxy. A separate control showed that a scripting edit touching no wire at all also drives
`ExecState` 1 -> 0 on the same VI.

## The questions

1. Over LabVIEW's ActiveX / VI Server interface, is `VI.ExecState` known to report 0 / "Bad" after a VI
   Scripting operation (a property read such as `Wire.Is Broken?`, or an invoke such as
   `Terminal.Connect Wire`) purely because the VI has been MARKED as needing recompilation, rather than
   because it is genuinely broken? I.e. is `ExecState` documented (or widely reported) to be a CACHED /
   deferred value that only refreshes when LabVIEW recompiles or revalidates the VI?

2. If so, what makes it refresh? Specifically, is any of these reachable over ActiveX from an external client
   (not from inside a LabVIEW scripting VI):
   - a VI-class method that forces a compile or a recompile of one VI;
   - the `VI.Broken?` / `Is Broken` style property, and does it differ from `ExecState`;
   - `VI.Get Errors` / the error-list method (we have evidence this is ABSENT from the exported
     `VirtualInstrument` ActiveX interface — confirm or refute);
   - Mass Compile as a method/invoke node reachable over ActiveX;
   - a side effect of `VI.Save:Instrument` (saving the VI) that revalidates it;
   - opening/closing the front panel or block diagram window, `VI.FPWinOpen`, or a `Reinitialize`/`Revalidate`
     style call.
   For each, say whether it exists in the ActiveX type library, its exact name, and cite the source.

3. Is the documented meaning of `ExecState` values authoritative anywhere — what exactly do 0 and 1 mean, and
   is there an enumeration value that means "needs recompile" distinct from "broken"?

4. What is the CHEAPEST documented way, from an external ActiveX client, to obtain a TRUSTWORTHY answer to
   "is this VI actually broken?" after a scripting edit, without saving the VI and without running it?

## What I am NOT asking

Do not design our experiment, do not ask me to confirm anything, and do not comment on our project's process.
Facts plus citations only. "No documented mechanism exists" is a perfectly acceptable answer if that is what
the sources say — say so plainly and say what the sources DO establish.


## Answer

## Summary of findings

**Short answer:** No NI source documents `ExecState` as a cached value that goes stale after scripting edits — but the compilation model NI does document (compile is deferred until load/run/save) is consistent with what you observed, and an independent ActiveX-scripting project (Zuehlke labview-mcp) has hit persistent `eBad` after scripting operations too. The documented refresh mechanism is the VI-server **`Compile.VI` method** (LabVIEW 2011+, remote access allowed) — but it is a *VI Scripting–scope VI Server method*, not a member of the exported ActiveX `VirtualInstrument` dispatch interface, so from an external COM client you reach it the same way you reach `Terminal.Connect Wire`: via a scripting op VI that LabVIEW executes.

### 1. Is `ExecState = 0` documented to mean "needs recompile" rather than "genuinely broken"?

Not documented, either way. The property documentation ([LabVIEW Wiki, Execution.State property](https://labviewwiki.org/wiki/VI_class/Execution.State_property), mirroring NI's help) defines exactly four values with no "needs recompile" state and no caching note:

- **0 – Bad**: "VI has errors and cannot execute."
- **1 – Idle**: "VI is not running but is in memory."
- **2 – Run top level**
- **3 – Running**

What NI *does* document is that compilation is deferred: LabVIEW compiles a VI "during load, run or save (if necessary)" when a needs-recompile flag is set ([Loading VIs, LabVIEW Wiki](https://labviewwiki.org/wiki/Loading_VIs); [NI LabVIEW Compiler: Under the Hood](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html)). So between a scripting edit and the next compile trigger there is no fresh compile result for `ExecState` to report from; the sources simply never state which value it returns in that window. Forum threads about "Exec.State says BAD but the VI is good" exist but have other causes (e.g. a trailing space in the VI name in [this NI thread](https://forums.ni.com/t5/LabVIEW/Exec-State-shows-VI-is-quot-BAD-quot-but-VI-is-quot-GOOD-quot/td-p/544474); missing dependencies when opened via VI Server in [this LAVA thread](https://lavag.org/topic/14744-why-is-my-vi-bad/) — note that thread's point that VI Server opens do *not* auto-search for missing subVIs the way the IDE does). The [Zuehlke/labview-mcp project](https://github.com/Zuehlke/labview-mcp) (driving LabVIEW over ActiveX, as you are) repeatedly hit VIs stuck at `eBad` after scripting/generation, found "no working method to refresh or recompile VIs into valid execState" over the raw COM surface, and noted that patching then **saving through the IDE** left `execState = 1` ([PR #61](https://github.com/Zuehlke/labview-mcp/pull/61), [PR #60](https://github.com/Zuehlke/labview-mcp/pull/60)) — i.e. save-triggered compilation refreshed it. That is corroboration, not NI documentation.

### 2. Refresh mechanisms, item by item

- **Force-compile method — EXISTS, but in VI Server scripting scope, not the ActiveX interface.** `Compile.VI` method, VI class, method ID 466, added LabVIEW 2011: "Compiles the VI and optionally the entire VI hierarchy of that VI," parameters `Compile Entire Hierarchy (F)` and `Force Compile (T)`; "Remote access allowed: Yes"; classified as a VI Scripting method ([LabVIEW Wiki, Compile.VI method](https://labviewwiki.org/wiki/VI_class/Compile.VI_method)). NI staff advice for forcing project-wide compiles is exactly this: open a reference to each VI and call `Compile` with ForceCompile=TRUE ([NI Idea Exchange thread](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Force-Recompile-option-in-Mass-Compile/idi-p/2659839/page/2)). I could not verify it in the exported ActiveX `VirtualInstrument` type library — the ActiveX member reference pages ([NI VI Properties/Methods (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi.html), [documentation.help mirror](https://documentation.help/NI-ActiveX-LabView/VI_Class_Method.html)) were not fetchable in readable form, so I can neither confirm nor refute its presence there; no source I found shows anyone calling `Compile` directly on the COM `VirtualInstrument` object. Since you already execute scripting op VIs over ActiveX, an op VI containing a `Compile.VI` invoke node is the documented route.
- **`VI.Broken?` / Is Broken property** — no such property exists on the VI class; the class listing shows `Execution.State` only, with no separate Broken property ([LabVIEW Wiki, VI class](https://labviewwiki.org/wiki/VI_class)). (`Is Broken?` exists on the **Wire** class, which you already use.)
- **`Get Errors`** — exists on the VI class (method ID 452) but is **Private scope** (outputs `Errors[]`, `Details[]`, optional `Call Dangerously?`) ([LabVIEW Wiki, Get Errors method](https://labviewwiki.org/wiki/VI_class/Get_Errors_method)). Private methods are absent from the exported ActiveX interface, which is consistent with your evidence that `VirtualInstrument` lacks it; they require private-scope VI Server access even inside LabVIEW.
- **Mass Compile over ActiveX** — no documented Application- or VI-class ActiveX method exists; NI's own answer to "mass compile programmatically" is the per-VI `Compile` loop above ([same Idea Exchange thread](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Force-Recompile-option-in-Mass-Compile/idi-p/2659839/page/2)).
- **`SaveInstrument`** — is in the ActiveX interface ("saves a VI that is not currently running…", [NI VI Properties and Methods (ActiveX) search result](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi.html)), and since LabVIEW compiles on save when the recompile flag is set ([Loading VIs](https://labviewwiki.org/wiki/Loading_VIs)), saving is a documented compile trigger — the one route you excluded. The labview-mcp experience (save fixed `execState`) matches.
- **Front-panel open/close, `FPWinOpen`, Revalidate/Reinitialize** — `OpenFrontPanel`/`CloseFrontPanel` exist in the ActiveX interface, but no source documents them as compile triggers (the documented triggers are load, run, save). No `Revalidate`/`Reinitialize` method exists anywhere in the VI class listing ([LabVIEW Wiki, VI class](https://labviewwiki.org/wiki/VI_class)). There is a private `Fake Exec State` method, but it only *fakes* running/stopped appearance and is unrelated ([LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Fake_Exec_State_method)).

### 3. Authoritative meaning of the values

The four-value enumeration in §1 is the authoritative definition (NI help, mirrored at [labviewwiki Execution.State](https://labviewwiki.org/wiki/VI_class/Execution.State_property); the ActiveX `ExecStateEnum` uses names `eBad`, `eIdle`, `eRunTopLevel`, `eRunning`, seen in third-party COM clients, e.g. [ISIS SECI source](https://shadow.nd.rl.ac.uk/SECI/html/LabViewApp_8cs_source.html)). **There is no enumeration value distinguishing "needs recompile" from "broken"** — 0/Bad is the only non-runnable state, so a merely-uncompiled VI has no state of its own to report.

### 4. Cheapest trustworthy "is it actually broken?" without saving or running

Nothing cheaper is documented than forcing a compile and re-reading state: execute (over ActiveX, as a scripting op VI) an invoke of **`Compile.VI`** — with `Force Compile` left False it's a no-op when the VI is already compiled, and after it returns, `Execution.State` reflects a real compile verdict rather than the deferred flag ([Compile.VI method](https://labviewwiki.org/wiki/VI_class/Compile.VI_method)). It doesn't save, doesn't run, doesn't load the front panel or diagram, and NI staff endorse it as the programmatic compile mechanism. There is no documented pure-external-COM equivalent, and no documented read-only property that bypasses the deferred compile.

Sources: [Execution.State property](https://labviewwiki.org/wiki/VI_class/Execution.State_property) · [Compile.VI method](https://labviewwiki.org/wiki/VI_class/Compile.VI_method) · [Get Errors method](https://labviewwiki.org/wiki/VI_class/Get_Errors_method) · [VI class listing](https://labviewwiki.org/wiki/VI_class) · [Fake Exec State method](https://labviewwiki.org/wiki/VI_class/Fake_Exec_State_method) · [Loading VIs](https://labviewwiki.org/wiki/Loading_VIs) · [NI Compiler Under the Hood](https://www.ni.com/en/support/documentation/supplemental/10/ni-labview-compiler--under-the-hood.html) · [Force Recompile Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Force-Recompile-option-in-Mass-Compile/idi-p/2659839/page/2) · [Exec.State BAD thread](https://forums.ni.com/t5/LabVIEW/Exec-State-shows-VI-is-quot-BAD-quot-but-VI-is-quot-GOOD-quot/td-p/544474) · [LAVA "Why is my VI Bad?"](https://lavag.org/topic/14744-why-is-my-vi-bad/) · [labview-mcp PR #61](https://github.com/Zuehlke/labview-mcp/pull/61) · [labview-mcp PR #60](https://github.com/Zuehlke/labview-mcp/pull/60) · [NI ActiveX VI reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi.html) · [SECI ExecStateEnum usage](https://shadow.nd.rl.ac.uk/SECI/html/LabViewApp_8cs_source.html)

## Sources

(extract from answer)

## What was done with it

**Outcome: ANSWERED. REPORTED ONLY — by the dispatching brief's explicit instruction, NOTHING was built
against it in this dispatch.** It was dispatched FIRST precisely so its answer could not steer the build.

Its findings, recorded for the judgement session:

1. **No NI source documents `ExecState` as a cached value that goes stale after a scripting edit.** The
   property has exactly four values — 0 Bad ("VI has errors and cannot execute"), 1 Idle, 2 Run top level,
   3 Running — and **there is no enumeration value meaning "needs recompile"**, so a merely-uncompiled VI has
   no state of its own to report.
2. **What NI DOES document is that compilation is deferred to load, run or save.** Between a scripting edit
   and the next compile trigger there is no fresh compile result for `ExecState` to report from, and the
   sources never say what it returns in that window.
3. **`Compile.VI` (VI class, method ID 466, LabVIEW 2011+, "Remote access allowed: Yes", `Compile Entire
   Hierarchy` / `Force Compile`) is the documented force-recompile route**, but it is a VI-Scripting-scope
   VI Server method, not a member of the exported ActiveX `VirtualInstrument` interface — reachable from our
   external COM client only the way `Terminal.Connect Wire` is: inside a scripting op VI.
4. **`VI.Broken?` does not exist** (the VI class has `Execution.State` only; `Is Broken?` is a **Wire**-class
   property, the one this cycle is removing). **`VI.Get Errors` (452) exists but is PRIVATE scope**, which is
   consistent with our own evidence that it is absent from the ActiveX interface. **No Mass Compile method**
   is exposed. **No `Revalidate`/`Reinitialize`** exists.
5. **`SaveInstrument` IS in the ActiveX interface and saving is a documented compile trigger** — and an
   independent ActiveX-scripting project (Zuehlke `labview-mcp`, PRs #60/#61) repeatedly hit VIs stuck at
   `eBad` after scripting, found no COM-surface way to refresh, and had `execState` come back to 1 after
   **saving through the IDE**. Corroboration, not NI documentation.
6. Its answer to "cheapest trustworthy verdict without saving or running": nothing cheaper is documented than
   an op VI invoking `Compile.VI` and re-reading `Execution.State`.

**Not acted on here.** Whether to build a `Compile.VI` op, and what §2's "compilation is deferred to save"
implies for this cycle's save-bypass rejection, are judgement calls; they are returned as facts, not applied.
The hypothesis peer of the same day (`archive/peer/2026-09-21-c64-v2-run1.md` §3.4) then used point 2
against my own plan — that the COLD reopen, not the save-point read, is the first real compile verdict v2
ever gets — and that too is recorded rather than acted on.
