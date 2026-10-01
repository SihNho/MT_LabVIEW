# g5-l1-gemini-pro-r2

- **agent:** gemini
- **role:** (n/a)
- **model:** gemini-3.1-pro-high (pinned by -Model)
- **kind:** fact
- **cost:** 
- **date:** 2026-09-30 20:06:31
- **outcome:** ANSWERED (79s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

When LabVIEW is automated from another program through its ActiveX (COM) server, the VirtualInstrument object is used to control a VI. Which VirtualInstrument property tells the client whether that VI is broken (cannot run), what numeric values can that property take and what does each mean? Does the ActiveX VirtualInstrument interface also expose a separate 'is broken' Boolean?

Search the web and cite the URL of every source you used.

## Answer

Based on web research of LabVIEW's ActiveX (COM) server documentation, here is the answer to your question:

### 1. Which VirtualInstrument property tells the client whether that VI is broken?
The property used to determine if a VI is broken (cannot run) is the **`ExecState`** property.

### 2. What numeric values can that property take and what does each mean?
The `ExecState` property returns an integer corresponding to the `ExecStateEnum` data type. It can take one of four numeric values:
*   **`0` (`eBad`)**: The VI has errors, is broken, and cannot execute.
*   **`1` (`eIdle`)**: The VI is not running but is loaded in memory and available to be called.
*   **`2` (`eRunTopLevel`)**: The VI is actively running as the top-level VI in an active hierarchy.
*   **`3` (`eRunning`)**: The VI is reserved for execution by one or more active top-level VIs (typically meaning it is running as a subVI).

By checking if the `ExecState` property equals `0`, the client can determine if the VI is broken.

### 3. Does the ActiveX VirtualInstrument interface also expose a separate 'is broken' Boolean?
**No**, the ActiveX `VirtualInstrument` interface does not expose a separate "is broken" Boolean property. The standard approach provided by the LabVIEW COM server to verify if a VI is executable is to query the `ExecState` property and evaluate whether it returns `0` (`eBad`). 

***

**Sources Cited:**
Because the search tool provided Grounding API redirection links rather than direct readable URLs, the information was synthesized from the following primary domains returned during the search:
*   **NI Official Documentation & Support (ni.com)**: VI Server and ActiveX `VirtualInstrument` reference, specifically detailing `ExecStateEnum` and troubleshooting broken ActiveX nodes.
*   **Documentation.help**: LabVIEW Automation Server class references for `VirtualInstrument` properties and `ExecStateEnum` values.
*   **LAVA Forums (lavag.org)**: Community discussions confirming the absence of a direct "broken" Boolean property in the ActiveX interface and the standard practice of using `ExecState`. 

*(Note: Per your explicit instructions not to create or modify local files, I have skipped generating the usual `/plan` local markdown artifact and have provided your answer directly here).*



## Sources

(extract from answer)

## What was done with it

(Claude fills in)
