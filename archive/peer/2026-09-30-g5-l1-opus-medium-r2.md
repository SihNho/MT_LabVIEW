# g5-l1-opus-medium-r2

- **agent:** claude
- **role:** fact
- **model:** claude-opus-5-5 (effort medium; peer.ps1 default for role fact)
- **kind:** fact
- **cost:** $0.9504  in 32 / out 6859 / cache-create 29120 / cache-read 598217  (159s, 32 turn(s))
- **date:** 2026-09-30 20:01:03
- **outcome:** ANSWERED (161s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

When LabVIEW is automated from another program through its ActiveX (COM) server, the VirtualInstrument object is used to control a VI. Which VirtualInstrument property tells the client whether that VI is broken (cannot run), what numeric values can that property take and what does each mean? Does the ActiveX VirtualInstrument interface also expose a separate 'is broken' Boolean?

Search the web and cite the URL of every source you used.

## Answer

I couldn't open NI's own ActiveX pages, so the answer below rests on secondary sources for the numbers. It's also not settled whether a separate "is broken" Boolean exists.

**Property: `ExecState`.** On the ActiveX `VirtualInstrument` object, `ExecState` reports the VI's execution state, and its type is `ExecStateEnum`. NI's ActiveX reference has a page for it ([ExecState – NI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi/execstate.html), listed under [VI Properties (ActiveX)](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html)), and `ExecStateEnum` is listed among NI's [ActiveX Enumerations](https://zone.ni.com/reference/en-XX/help/371361R-01/axprop/activex_enumerations/). Those NI pages load their content with JavaScript, the old zone.ni.com links now redirect to a general page, and the documentation.help mirror returned 403 errors. So I could not read NI's own table of the enum values.

**Values and meanings.** This table is my reconstruction from three sources, not a quote from NI:

| Value | ActiveX name | Meaning |
|---|---|---|
| 0 | `eBad` | The VI has errors and cannot run (it is broken) |
| 1 | `eIdle` | The VI is in memory but not running |
| 2 | `eRunTopLevel` | The VI is the top-level VI of a running hierarchy |
| 3 | `eRunning` | The VI is reserved for execution by one or more running top-level VIs |

- **Numbers and meanings** come from the LabVIEW Wiki's copy of the equivalent VI Server property, Execution.State. It gives "0 Bad—VI has errors and cannot execute", 1 Idle, 2 Run top level, 3 Running, as an Enum U32 ([LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Execution.State_property)).
- **The ActiveX names `eIdle`, `eRunning` and `eRunTopLevel`** appear as `ExecStateEnum` members in real C# code that uses LabVIEW's COM server ([SECI LabViewApp.cs](https://shadow.nd.rl.ac.uk/SECI/html/LabViewApp_8cs_source.html)).
- **`eBad` = 0 and `eIdle` = 1** are shown in practice in an ActiveX automation project, which reports a broken `.vim` as "execState 0" / `eBad` and the working `.vi` as `eIdle` ([Zuehlke/labview-mcp PR #60](https://github.com/Zuehlke/labview-mcp/pull/60)).

That the ActiveX enum uses the same numbers as the VI Server enum is an inference. It fits both sources, but I couldn't check it against NI's ActiveX table.

**What "Bad" can also mean.** "Bad" doesn't always mean the VI's code is wrong. Forum threads show `ExecState`/Exec.State returning Bad in other situations:
- a wrong VI path, in one case caused by a trailing space ([NI forum](https://forums.ni.com/t5/LabVIEW/Exec-State-shows-VI-is-quot-BAD-quot-but-VI-is-quot-GOOD-quot/td-p/544474));
- a VI locked by another project context ([NI forum](https://forums.ni.com/t5/LabVIEW/Running-top-level-VI-indicated-as-bad-by-exec-state/td-p/4183251));
- dependencies that can't be found because the run-time engine searches different paths ([NI forum](https://forums.ni.com/t5/LabVIEW/Does-the-definition-of-quot-Execution-State-quot-equals-quot-Bad/td-p/1544378)).

**Is there a separate "is broken" Boolean?** Not settled. None of the sources I found mention one on the ActiveX `VirtualInstrument` interface. Everything I found checks for a broken VI by comparing `ExecState` to `eBad`, including the NI threads above and the [LAVA thread](https://lavag.org/topic/14744-why-is-my-vi-bad/). Because I couldn't read NI's full ActiveX property list, I can't say for certain that no such property exists. To settle it, check the LabVIEW type library (`labview.tlb`) in an object browser, or read NI's VI Properties (ActiveX) page in a browser.

Sources:
- https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi/execstate.html
- https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/activex/vi-p.html
- https://zone.ni.com/reference/en-XX/help/371361R-01/axprop/activex_enumerations/
- https://labviewwiki.org/wiki/VI_class/Execution.State_property
- https://shadow.nd.rl.ac.uk/SECI/html/LabViewApp_8cs_source.html
- https://github.com/Zuehlke/labview-mcp/pull/60
- https://forums.ni.com/t5/LabVIEW/Exec-State-shows-VI-is-quot-BAD-quot-but-VI-is-quot-GOOD-quot/td-p/544474
- https://forums.ni.com/t5/LabVIEW/Running-top-level-VI-indicated-as-bad-by-exec-state/td-p/4183251
- https://forums.ni.com/t5/LabVIEW/Does-the-definition-of-quot-Execution-State-quot-equals-quot-Bad/td-p/1544378
- https://lavag.org/topic/14744-why-is-my-vi-bad/

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
