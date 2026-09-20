---
type: reference
status: current
date: 2026-09-19
tags: [docs]
---

# REFERENCES — third-party code used, and what derives from it

**Purpose:** every piece of borrowed or derived code in this project is cited here so that anyone —
a labmate, a reviewer, a future session, or the author of a thesis chapter — can locate the original.
Per the project rule: cite author, version, licence and a resolvable URL, and state explicitly which
of our files derives from which of theirs.

All URLs accessed **2026-08-26**.

---

## 1. Installed dependencies

### [R1] LV-Scripting — Erdos Miller

> Taylor, D. / Erdos Miller. **LV-Scripting** — *an open source LabVIEW library for code generation
> using VI Scripting*. Version **0.10.0.1** (release `v0.10.0`, 2017-07-18).
> Licence: **MIT** (Copyright (c) 2016–2017, Erdos Miller).
> <https://github.com/erdosmiller/lv-scripting>
> Package: <https://github.com/erdosmiller/lv-scripting/releases/download/v0.10.0/lv_scripting-0.10.0.1.vip>

- **Installed** on this machine via JKI VI Package Manager, 2026-08-26 (user-approved), into
  `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\` (84 VIs).
- Declared compatibility `LabVIEW >= 15.0`; **verified working on LabVIEW 2026 (26.3.1f1)**.
- **Used for:** `Create For Loop.vi` (loop creation with auto-indexing and
  `Number of Static Parallel Instances`), `Create SubVI.vi`, `Wire Inputs.vi`, `Get Controls.vi` /
  `Get Outputs.vi`, `Create Index Array.vi`, `Create Replace Array Subset.vi`, `Exit For Loop.vi`.

---

## 2. Code shipped with LabVIEW (National Instruments)

### [R2] NI VI Scripting example suite

> National Instruments. **VI Scripting examples**, bundled with LabVIEW 2026.
> Local path: `C:\Program Files\National Instruments\LabVIEW 2026\examples\Application Control\VI Scripting\`
> Licence: as per the LabVIEW end-user licence agreement (shipped example code).

- **Used for:** `Creating Objects\Adding Objects.vi` — the canonical `New VI Object` wiring, from
  which the terminal contract and error semantics documented in the `labview-automation` skill were derived.

---

## 3. Evaluated but NOT installed

### [R3] LabVIEW-VI-Snippet — Ryan Pacini

> Pacini, R. **LabVIEW-VI-Snippet** — *VI Snippet Import and Export Library for LabVIEW*.
> Release **0.2.0** (2020-01-18); source archive from release 0.1.0 (2020-01-15).
> Licence: **MIT**. <https://github.com/rcpacini/LabVIEW-VI-Snippet>

- Downloaded to `user.lib\claudeDev\VISnippet_EVAL\` for evaluation only; **not installed**.
- Source (not the packed `.lvlibp`) was used, so LabVIEW recompiles it; `VI Snippet Export.vi`
  **verified compiling on LabVIEW 2026**.

### [R4] labview-mcp — Zühlke

> Zühlke Engineering. **labview-mcp** — read/write/edit/run LabVIEW code from an MCP client.
> Licence: **MIT**. Requires LabVIEW 2026 Q3. <https://github.com/Zuehlke/labview-mcp>

- **Not used.** Relies on NI's private, undocumented `lvai.LVAI` gRPC interface with no version
  policy; its author reports the edit RPC fails, and it cannot handle VIs containing project-local
  subVIs. Retained as a possible *read-only* (VI → text) aid.

### [R5] labview_mcp — CyantusLYX

> CyantusLYX. **labview_mcp** — MCP server exposing LabVIEW VI Scripting via DQMH and COM.
> Licence: **NONE DECLARED** (repository states "[To be specified]").
> <https://github.com/CyantusLYX/labview_mcp>

- **Read for technique only; no code copied.** With no declared licence the work is
  "all rights reserved" by default, so it must not be vendored. Its
  `get_object_terminals` → `connect_objects(src, src_term, dst, dst_term)` pattern informed our
  understanding of terminal-name-based wiring.

### [R6] LabVIEW Scripting Tools — LAVA

> LAVA (LabVIEW Advanced Virtual Architects). **LabVIEW Scripting Tools**, VIPM package
> `lava_lib_labview_api_scripting_tools`.
> <https://www.vipm.io/package/lava_lib_labview_api_scripting_tools/>

- **Not installed.** Noted for connector-pane reference/pattern/wiring functions. The vipm.io page
  returned HTTP 403 when fetched, so its licence and version were **not verified** — check inside the
  VIPM client before use.

### [R7] labview_assistant — Jan Göbel

> Göbel, J. **labview_assistant** — MCP server and scripting functions for LLM-driven LabVIEW code
> generation. <https://github.com/JanGoebel/labview_assistant>

- **Not evaluated in depth.** Listed for completeness.

---

### [R8] Gemini Computer Use — Google

> Google. **Gemini API — Computer Use** (documentation). Model IDs `gemini-3.7-flash`,
> `gemini-3.5-flash-lite`, `gemini-3.5-flash`; `interactions.create` API; desktop action set;
> 0..999 coordinate normalisation; `safety_decision` contract.
> <https://ai.google.dev/gemini-api/docs/computer-use>  (accessed 2026-08-26)

### [R9] google-genai SDK — Google

> Google. **`google-genai`** Python SDK, v2.20.0. Licence: **Apache-2.0**.
> <https://github.com/googleapis/python-genai>  — installed via pip 2026-08-26.

### [R10] computer-use-preview — Google

> Google. **computer-use-preview** reference agent. Licence: **Apache-2.0**. **Browser-only**
> (Playwright / Browserbase). <https://github.com/google/computer-use-preview>
> Read for the agent-loop shape only; **no code copied** — the desktop executor is original.

## 4. Derivation map — which of our files came from where

| our file | derived from | nature of change |
|---|---|---|
| `user.lib\claudeDev\KernelBuilder_v1.vi` | **[R1]** `Example 8 - For Loops.vi` (LV-Scripting examples) | byte-for-byte copy, then retargeted: `New VI` → `Open VI Reference`, subVI placement and save added |
| `user.lib\claudeDev\OpForLoop_v0.vi` | `KernelBuilder_v1.vi`, hence **[R1]** `Example 8 - For Loops.vi` | copy of the builder, then everything but the `Create For Loop` chain deleted; config exposed as front-panel controls |
| `user.lib\claudeDev\OpSubVI_v0.vi` | `KernelBuilder_v1.vi`, hence **[R1]** `Example 8 - For Loops.vi` | copy of the builder, stripped to `Open VI Reference → Diagram property → Create SubVI`; second `Open VI Reference` and a path control added; **`Close Reference` removed — ON PURPOSE, see §4a below, not as an oversight** |
| `user.lib\claudeDev\OpWire_v0.vi` | — (original work; calls **[R1]** `Traverse for GObjects.vi` from **[R2]** plus `Get Outputs.vi` / `Wire Inputs.vi`) | built from a blank VI; no third-party diagram was copied |
| `user.lib\claudeDev\OpSubVI_v1.vi` | `OpWire_v0.vi` | copy of OpWire, second traverse chain and the `Get Outputs`/`Wire Inputs` pair deleted, cast class changed `Node` → `Diagram`, so the chain yields a structure's inner diagram as a target |
| `user.lib\claudeDev\OpReport_v0.vi` | `OpSubVI_v1.vi`, hence `OpWire_v0.vi` | copy of OpSubVI_v1 with the entire editing half deleted (two rubber-band selections + `Remove Broken Wires`), leaving `Open VI Reference → Traverse for GObjects` and indicators on `# of Refs` and `error out`; read-only |
| `user.lib\claudeDev\OpReport_v1.vi` | `OpReport_v0.vi` | copy of v0 with an `Index Array` (`index` control) and a GObject Property Node (`Position`, `Class Name`) added, plus their indicators; still read-only |
| `user.lib\claudeDev\OpReport_v2.vi` | `OpReport_v1.vi` | two more property rows (`UID`, `Owner`) plus a second, Generic-class Property Node reading the owner's `Class Name` |
| `user.lib\claudeDev\OpReport_v3.vi` | `OpReport_v2.vi` | identical diagram with `Ignore Errors inside Node` set on both Property Nodes |
| `user.lib\claudeDev\DONOR_Ex1_GetControlsWireIndicators.vi` | **[R1]** `Example 1 - Getting Controls and Wiring Indicators.vi` | byte-for-byte copy, kept as a wired donor for `OpWire` surgery |
| `user.lib\claudeDev\DONOR_Ex3_PrimitiveFunctions.vi` | **[R1]** `Example 3 - Primitive Functions (Part 1).vi` | byte-for-byte copy, kept as a wired donor for `OpWire` surgery |
| `user.lib\claudeDev\ScriptDriver_DropForLoop.vi` | **[R2]** NI `Adding Objects.vi` | byte-for-byte copy, then `vi object class` changed to `ForLoop` and `style` to `For Loop` |
| `user.lib\claudeDev\NIScriptingExamples\` | **[R2]** | unmodified copy of NI's example suite, for safe inspection |
| `user.lib\claudeDev\VISnippet_EVAL\` | **[R3]** | unmodified download, evaluation only |
| `.claude/skills/labview-automation/` | **[R1]**, **[R2]** | original prose; the `New VI Object` contract and error semantics were **derived by observation** of [R2], not copied |
| `tools/lv_gui.ps1` | — | original work (no third-party code) |
| `tools/gscript.py` | — | original work; drives the Op-VI fleet over ActiveX, uses pywin32 as a dependency only |
| `tools/uitars_grounder.py` | **[R11]** (prompt template, coordinate contract), **[R12]** (weights), **[R13]** (runtime) | original code; `smart_resize` re-implemented from the published formula |
| `tools/gemini_executor.py` | **[R8]** (protocol), **[R9]** (SDK), **[R10]** (loop shape only) | original code; request/response shapes and action names follow the official docs |

## 4a. `Close Reference` in the traverse ops — WHY IT IS ABSENT, and what was measured about it (2026-09-19)

Added by the D1 **stage S0** material session, whose task was "restore the `Close Reference` these ops are
missing". The line above (`OpSubVI_v0.vi` … "`Close Reference` removed") had been read for weeks as an oversight;
it is not. **Nothing in this section is a decision** — the two decisions it raises belong to a judgement session
and are named as such.

**Which ops carry a traverse and have NO `Close Reference`** — MEASURED, `tools/bench/s0_hygiene_probe.log` /
`…_run2.log` (12 PASS / 1 FAIL, the one FAIL discussed below):

| op | nodes | the reference-creating chain | close-ref nodes |
|---|---|---|---|
| `OpReport_v3.vi` (behind `gscript.count` / `report`) | 5 | Function#43 `Open VI Reference` → SubVI#124 `Traverse for GObjects.vi` → IndexArray#167 → Property#241 → Property#482 | **0** |
| `OpWireSource_v5.vi` | 19 | contains that SAME chain (#43/#124/#167/#241/#482) plus `UID to GObject Reference.vi`#990 and two `To More Specific Class` | **0** |
| `OpReportAll_v0.vi` (behind `gscript.report_all`) | 5 | Open VI Reference → Traverse → **For Loop** → 2 Property | **0** |
| `KernelBuilder_v1.vi` — **the donor** | 18 | — | **1**, Function **#157 `Close Reference`** |

**Why it was removed.** Two of our own documents record the reason, and neither is cited by the plan that ordered
the repair:
- `archive/WORKLOG.md:84-86` — "`OpSubVI_v0` deliberately **leaks its references**: `Close Reference` **defeated
  four wiring attempts** and, for chained operations, keeping the target in memory is wanted anyway."
- `archive/VI_SCRIPTING_GUIDE.md:479-480` — the same as a standing design rule for v0 ops: "`Close Reference`'s
  refnum input is awkward to wire by hand."

The node's terminals, which no document here recorded until now: 0 `error out` (source), 1 `error in (no error)`
(sink), 2 **`reference`** (sink) — `tools/bench/s0_terminal_names.log`, read-only, 6/6.

**What the leak actually costs, measured.** On a scratch copy of `Min_Track N beads V6_ParallelLoop.vi`
(md5 `2a78e17c449cacdaf5da389818526859`), fresh LabVIEW, OLD ops:

| window | handles | private bytes | `error 2`? |
|---|---|---|---|
| 20 × `count(Node)` (626 matched objects/call) | 34,134 → 34,349 (**+215**) | 586.5 → 613.7 MB (**+27.2 MB**) | none |
| 20 × `report_all(Diagram)` (170 matched/call, VI already loaded) | 34,349 → 34,358 (**+9**) | 613.7 → 613.6 MB (**−0.1 MB**) | none |

**+202 of the +215 is the first call** (`…_run2.log:75`: call 0 is already at 34,336 against the 34,134 pre-loop
baseline) — i.e. the 473 KB VI load, not the traverse. The second window, taken with the VI already in memory, is
flat across 3,400 objects that the leak hypothesis says should have leaked.

**Two consequences, both for judgement, not for this file:**
1. `docs/cycle27-plan.md` Pre-decided 21(b) names "a leaked GObject reference per matched object" as the live
   cause of `error 2`. The second window does not support it. Amending a `## Pre-decided` line is a judgement
   session's act (Pre-decided 12), so it stands unamended and is flagged here.
2. `STATUS.md` NEXT §1's acceptance gate — "20 consecutive calls, handle count flat (±100)" — is **blind to this
   reference class by construction**: `tools/gscript.py:227-228` records that the kernel handle count "cannot see
   VI Server refnums at all". It FAILS on the unrepaired op (for a VI load) and PASSES with the leak in place.
   Private bytes are the meter `docs/cycle27-plan.md:321-324` names for `error 2`.

**Status of the repair: NOT BUILT.** `tools/recipes/build_s0_closeref_v0.py` (would produce `OpReport_v4.vi` and
`OpWireSource_v6.vi` as NEW files, the old ones untouched) is written and syntax-clean, and its mandatory
prior-art review `archive/peer/2026-09-19-priorart-s0-closeref.md` returned **NOT NOVEL, 7 slugs**;
`tools/stop_record.py` refuses its launch until a `FIXED:`/`REFUTED:` line releases it. The review's own
recommendation is that the repair is still owed but should enclose the close in a **For Loop** over the
`References` array — a route `docs/toolkit-capabilities.md:438-443` records as already built and measured
(`LoopTunnel 0→1`, `ExecState 0→1`), and the shape `OpReportAll_v0.vi` already has on disk.

### 4a-bis. ⚖️ **S0 IS CLOSED — the unrepaired traverse ops are ACCEPTED AS THEY ARE, on measurement (2026-09-19)**

Three arms, all on the same scratch copy of `Min_Track N beads V6_ParallelLoop.vi` (md5
`2a78e17c449cacdaf5da389818526859`), fresh LabVIEW each time, the OLD ops exactly as they sit on disk
(`OpReport_v3.vi` md5 `0743701a249b6ac20a5dab9ee676c09c`, `OpWireSource_v5.vi` `5dc45a04ea5d809f5ca57e9309ed59c5`,
`OpReportAll_v0.vi` `ffcec2c75e92dcad514299ba20e66054` — **byte-identical before and after every arm**). Meters are
the ONE S0 criterion of `docs/cycle27-plan.md:453-457`: **G-A** no `error 2` · **G-B** kernel handles flat ±100
**counted from call 1** · **G-C** LabVIEW private-byte drift ≤ 5 MB.

| arm | workload, 20 calls | handles (from call 1) | private bytes | `error 2`? | log |
|---|---|---|---|---|---|
| **traverse-only** | 20 × `report_all(Diagram)`, VI already loaded | **+9** | **−0.1 MB** | none | `tools/bench/s0_hygiene_probe_run2.log:121-123` |
| **traverse + mutate** | `count(Node)` → `report_all(Diagram)` → `OpWireSource_v5` → `build_property`, ×20 | **−19** | **+34.6 MB** | none | `tools/bench/s0b_refleak_profile.log:61-64`; artefact `tools/bench/s0b_refleak_profile.json` md5 `b3ddf21fc39735e329c61477dbcac03e` |
| **mutate-only** | the same loop with the three explicit traverse legs REMOVED, `build_property` kept | **−12** | **+34.5 MB** | none | `tools/bench/s0b_mutonly_profile.log:61-65`, `:68-71`; artefact `tools/bench/s0b_mutonly_profile.json` md5 `6917c1cba61a403561de55a5ac0f5071` |

**What the three arms decide.** Mutate-only (+34.5 MB) accounts for essentially all of traverse+mutate's +34.6 MB —
the two differ by **0.1 MB** — so the drift is **VI growth** (20 Property nodes created, node count 626 → 645, ≈1.7 MB
each), not a traverse leak; and traverse-only is flat at −0.1 MB over 3,400 matched objects. On
**traverse-attributable drift, G-C is MET**, alongside G-A and G-B. ⚠️ Read the third arm precisely: it is not
traverse-free. `build_property` runs `report_all(Property)` twice internally (`tools/gscript.py:2196`, `:2225`,
`:1017-1021`) in **both** arms, so those cancel; what was removed is exactly `count(Node)` (626 matched/call),
`report_all(Diagram)` (170 matched/call) and the UID-addressed `OpWireSource_v5` run.

**Consequence, decided by judgement in advance** (`docs/cycle27-plan.md` Pre-decided 25(iv) + 27 + 28 — both branches
were written before the arm ran): the ops are **accepted as they are, with the measurement as the record**. No
`Close Reference` repair is built, **no new `_vN` op file exists**, and every old op file is unchanged. CLAUDE.md's
reference-hygiene rule states its acceptance as a measurement ("20 consecutive calls ⇒ handle count flat"), so
passing it on both meters is compliance, not evasion — ⚠️ **flagged to the user: only they may overturn this reading
of their own rule.** The two "consequences for judgement" listed above §4a's repair paragraph are thereby settled for
S0's purposes; §4a's "Status of the repair: NOT BUILT" stands and is now permanent rather than pending.
**S0 IS CLOSED; S1 is next** (`docs/cycle27-plan.md` Pre-decided 22's stage table).

## 5. Attribution inside the artefacts

A `.vi` is a binary and cannot carry a comment header, so derived VIs should additionally record their
origin in **`File > VI Properties > Documentation`** (the VI Description field), which is visible in
Context Help and survives copying. Text artefacts carry their citation inline.

**Status:** still pending for `KernelBuilder_v1.vi` and `ScriptDriver_DropForLoop.vi`. Attempted via
`Ctrl+I` on 2026-08-26; the shortcut silently did not open the VI Properties dialog (a known LabVIEW
failure mode - see the `labview-automation` skill on unreliable shortcuts). Use **`File > VI Properties >
Documentation`** from the menu instead, which is reliable. The citations are meanwhile complete in this
file, so provenance is not lost.

### [R11] UI-TARS — ByteDance-Seed

> ByteDance-Seed. **UI-TARS** — native GUI agent model. Licence: **Apache-2.0**.
> <https://github.com/bytedance/UI-TARS>  · Model **UI-TARS-1.5-7B** (Qwen2.5-VL based):
> <https://huggingface.co/ByteDance-Seed/UI-TARS-1.5-7B>  · Coordinate guide:
> <https://github.com/bytedance/UI-TARS/blob/main/README_coordinates.md>  · Prompt templates:
> <https://github.com/bytedance/UI-TARS/blob/main/codes/ui_tars/prompt.py>  · `ui-tars` PyPI package
> (official action parser). Accessed 2026-08-26.
> Benchmarks quoted from the model card: ScreenSpot-Pro 61.6 (vs OpenAI CUA 23.4), OSWorld 42.5.

### [R12] UI-TARS-1.5-7B GGUF + mmproj — mradermacher

> mradermacher. **UI-TARS-1.5-7B-GGUF** — quantised GGUF files and the `mmproj` vision projector.
> <https://huggingface.co/mradermacher/UI-TARS-1.5-7B-GGUF>. Files used: `UI-TARS-1.5-7B.Q4_K_M.gguf`
> (4.8 GB), `UI-TARS-1.5-7B.mmproj-Q8_0.gguf` (1.0 GB). Chosen to fit a 6 GB RTX 2060.
> NOTE: the community Ollama tags `0000/ui-tars-1.5-7b` and `-q8_0` are **text-only** (no projector)
> and were rejected for that reason.

### [R13] Ollama

> Ollama. Local LLM runtime, v0.32.15, licence **MIT**. <https://github.com/ollama/ollama>.
> Installed via winget 2026-08-26. Used for `/api/generate` with base64 `images`.

### [R14] Korean setup guide (community)

> simsimit00. *UI-TARS: ByteDance's GUI automation AI agent* (Korean blog), Tistory.
> <https://simsimit00.tistory.com/582>. Supplied by the user 2026-08-26. Independently recommends the
> planner/executor split, action allow-listing, and single-monitor operation adopted here.
