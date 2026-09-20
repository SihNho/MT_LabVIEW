---
type: narrative
status: historical
date: 2026-08-27
tags: [archive, gui]
---

# VI Scripting Guide — editing LabVIEW block diagrams with code

**This is the LabVIEW *coding* guideline.** Its sibling `GUI_PLAYBOOK.md` covers driving the LabVIEW
*mouse*; use this one first, because anything scriptable should never be clicked.
`LEARNING.md` explains the same material as prose for the user.

**Status: PROVEN WORKING on this machine (2026-08-26).** A driver VI has programmatically created
both a Subtract function and a **For Loop** on another VI's block diagram.

---

## 1. Setup

Enabled at `Tools ▸ Options ▸ VI Server ▸ "Show VI Scripting functions, properties and methods"`
(persisted as `server.viscripting.showScriptingOperationsInEditor=True` in `LabVIEW.ini`). The palette
then appears at `Functions ▸ Programming ▸ Application Control ▸ VI Scripting`.

## 2. Start from NI's examples — never hand-build a driver

NI ships a full, runnable example suite that nobody had noticed:
`C:\Program Files\National Instruments\LabVIEW 2026\examples\Application Control\VI Scripting\`
copied (so it can be modified freely) to `user.lib\claudeDev\NIScriptingExamples\`.

| example | what it gives you |
|---|---|
| `Creating Objects\Adding Objects.vi` | the canonical `New VI Object` wiring. **Verified running.** |
| `Creating Objects\Drop Add Function Inside While Loop.vi` | dropping a node **inside** a structure |
| `Creating Objects\New VI Object Location Argument.vi` | placement semantics |
| `Structures\VI Scripting with Structures - For Loop.vi` | ForLoop properties: `Loop Count`/N, `Loop Counter`/i, `Diagram`, `Has Conditional Terminal?` (doc-only) |
| `Selecting Objects\Enclose Selection.vi`, `Moving Objects\` | selection and placement |
| `Connector Pane\Add Terminals to Connector Pane.vi` | building a connector pane programmatically |

Hand-building a driver by clicking cost a full session and never ran. Cloning `Adding Objects.vi` and
changing one constant took minutes. **Always adapt an example.**

Working driver in this project: `user.lib\claudeDev\ScriptDriver_DropForLoop.vi`
(its title still reads "Adding Objects.vi" because the VI's internal name was never changed — harmless).

## 3. `New VI Object` — the verified recipe

Wire **exactly** these. `Path` and `bounds` stay **unwired**.

| terminal | position on node | wire with |
|---|---|---|
| `vi object class` | **top** edge | a VI Server Class constant — set via right-click ▸ `Select VI Server Class` |
| `owner refnum` | left, 1st | the VI reference (the example passes it through a VI Property Node) |
| `style` | left, 2nd | a ring constant naming the object, e.g. `Subtract`, `For Loop`. **REQUIRED** |
| `position` | left, 3rd | cluster of two I32, e.g. `{100, 200}` |
| `error in` | left, bottom | the error chain |
| `Path` | — | **leave unwired** |
| `bounds` | — | **leave unwired** |

The example's own on-diagram text agrees: *"Determine the owner, class, style, and location of the new
object."* Four things, no path.

### `class` and `style` are two halves of ONE decision

`class` fixes the **datatype of the reference you get back**; `style` fixes **what object is actually
created**. They must agree, or you get Error 1057.

### Which inputs are really required

`style` is required — deleting its constant **breaks the run arrow** immediately. `Path` and `bounds`
are not: NI's working example leaves both unwired forever. (An earlier note in this project claiming
all three were mandatory was simply wrong.) To check any node this way: delete a constant and look at
the run arrow — solid = optional, shattered = required.

## 4. Error codes, decoded

| error | meaning | actual cause here |
|---|---|---|
| **1059 (0x423)** "Unexpected file type" | `Path` got something that isn't a type def | a **`.vi`** path was wired into `Path`. That input is only for a `.ctl` type definition or `.lvclass`. **Leave it unwired.** |
| **1057 (0x421)** "Object cannot be cast to the specified type" | `class` vs `style` disagree | `class = ForLoop` while `style` was still `Subtract`: LabVIEW built a Subtract and could not hand it back as a For Loop refnum. |

**Errors are easy to miss.** LabVIEW's `Simple Error Handler` dialog is titled after the **VI's name**,
not "Error". A scripting run that appears to do nothing may have a modal dialog open under an
innocuous window title — check the window list for an unexpected entry.

## 5. `Select VI Server Class` — recorded paths

Right-click the class constant ▸ `Select VI Server Class ▸` …

| object | path |
|---|---|
| **For Loop** | `Generic ▸ GObject ▸ Node ▸ Structure ▸ Loop ▸ ForLoop` |
| While Loop | `Generic ▸ GObject ▸ Node ▸ Structure ▸ Loop ▸ WhileLoop` |
| **SubVI** | `Generic ▸ GObject ▸ Node ▸ SubVI` — needed to drop the tracking kernel |
| Function | `Generic ▸ GObject ▸ Node ▸ Function` |
| Constant | `Generic ▸ GObject ▸ Constant ▸ …` |
| Case Structure | `Generic ▸ GObject ▸ Node ▸ Structure ▸ MultiFrameStructure ▸ …` |

Submenus open on **hover** — move onto the parent, wait ~2 s, then take a **full-screen** capture
(window captures cannot see menus).

## 6. Practical technique

- **Make constants with `Create ▸ Constant` on the terminal.** LabVIEW generates one already matching
  that terminal's type, so only the *value* needs setting. This avoids a whole class of type errors.
- **Setting a long ring constant:** type-ahead is unreliable; scroll with
  `& .\tools\lv_gui.ps1 -Action wheel -Notches -8` and click the item.
- **Run a driver by clicking the run arrow** (window origin `+70,+66`), not `Ctrl+R` — sent shortcuts
  frequently never arrive.
- **Every run creates a new untitled VI** if the driver starts from `New VI`. Harmless, but the window
  list fills up quickly.

## 6a. CLOSE EVERY REFERENCE — scripting leaks memory badly if you don't

Every object reference a scripting run obtains — VI refs, diagram refs, and **every node, wire and
terminal ref** — must be explicitly closed with **Close Reference** when finished. Failing to do so
causes **severe memory leaks** in the LabVIEW process, and this process is the same LabVIEW instance
the user runs real experiments in, so a leaky driver degrades their rig rather than just a scratch
session.

NI's `Adding Objects.vi` models this: its step 5 is *"Use the Close Reference function to close each
open object reference when you are finished using it"*, and the example ends with two Close Reference
nodes before the error handler. Any driver adapted from it must keep that tail intact — it is not
decoration.

## 7. LabVIEW dataflow rules that bite when scripting

- A value produced **inside** a For Loop can never feed **that same loop's `N`** terminal — `N` must be
  resolved before the loop begins. LabVIEW shows the rejection as a dashed wire with a red X. A broken
  wire is a *semantic* verdict, not necessarily a misclick.
- Auto-indexed tunnels place each iteration's result at its own index automatically — which is exactly
  what the per-bead parallel loop needs, provided auto-indexing is genuinely on rather than a shared
  non-indexed tunnel.

## 8. Next step for this project

Build **one parameterised driver** — front-panel controls for target VI path, object class, style and
position — and drive it from PowerShell via **VI Server / LabVIEW CLI**. Then every future diagram
edit is one command with zero screenshots, and the GUI is touched only once. Replace the driver's
`New VI` node with `Open VI Reference` + a path constant so it targets an **existing** VI.

---

## 9. Existing public libraries — evaluate these BEFORE hand-building anything

Raised by the user 2026-08-26: the VI Scripting primitive layer this project was about to build by
hand already exists as open source. **Analyse and reuse first; hand-build only what is genuinely
missing.** Findings below are verified from the repositories themselves, not taken on trust.

### This machine

| fact | value |
|---|---|
| LabVIEW | **26.3.1f1 = 2026 Q3** |
| VIPM (JKI VI Package Manager) | **installed** — `C:\Program Files\JKI\VI Package Manager` |
| DQMH / Erdos Miller / OpenG in `vi.lib` | **none installed** |
| LabVIEW listening ports | `0.0.0.0:3364` (classic VI Server), `127.0.0.1:63376` + `[::1]:63376`, `127.0.0.1:63356` |

### Assessment

| library | license | needs | verdict |
|---|---|---|---|
| **erdosmiller/lv-scripting** | **MIT** | LabVIEW 2015+, VIPM `.vip` | **RECOMMENDED foundation.** Pure G, no undocumented APIs, no external runtime, 13 progressive examples. VIPM is already installed, so it drops straight in. |
| **Zuehlke/labview-mcp** | MIT | LabVIEW **2026 Q3** + AI feature | **Use for READING ONLY.** Converts a VI to text (AIXML) — which would finally give us block-diagram *wiring* as text, something byte extraction can never do. **Do not build on its editing.** |
| **CyantusLYX/labview_mcp** | **NONE ("[To be specified]")** | LabVIEW 2020+, **DQMH**, Go + Python + `win32com` | **Read for technique, do not vendor.** No license = all rights reserved by default. Also drags in DQMH (not installed) and a three-language stack. |
| **JanGoebel/labview_assistant** | not yet checked | MCP server + scripting functions | Not yet evaluated. Lower priority. |

### VERDICT on `erdosmiller/lv-scripting` — VERIFIED WORKING on LabVIEW 2026, and it solves the hard part

Evaluated 2026-08-26 **without installing anything**: a `.vip` is a ZIP archive, so it was downloaded,
extracted, and copied to `user.lib\claudeDev\LVScripting_EVAL\` for inspection.

| fact | value |
|---|---|
| latest release | **v0.10.0.1, 2017-07-18** — unmaintained for 8 years |
| licence | **MIT** |
| declared LabVIEW requirement | `LabVIEW>=15.0` — so 2026 (26.x) qualifies |
| `close labview before install` | **FALSE** — installing does not disturb a running session |
| API size | **84 VIs**, installed to `vi.lib\Erdos Miller\LV-Scripting` |
| **compiles on LabVIEW 2026?** | **YES — verified.** `Create For Loop.vi` opened with a **solid run arrow**, no "Find the VI" dialogs, no errors. The 2017 age is not a blocker. |

### INSTALLED AND VERIFIED END-TO-END (2026-08-26)

`erdosmiller/lv-scripting` **v0.10.0.1 is installed** (user approved) and proven working:

- VIPM reported `installed / No Errors`, targeting **LabVIEW 2026 (64-bit)**.
- On disk: **84 API VIs** at `<LabVIEW 2026>\vi.lib\Erdos Miller\LV-Scripting\`.
- Examples at `<LabVIEW 2026>\examples\Erdos Miller\LV-Scripting\examples\`.
- **`Example 8 - For Loops.vi` loaded with a solid run arrow and RAN**, generating `Untitled 13`
  containing a complete For Loop built purely by code: `N` wired from a constant, `i` terminal,
  **shift registers on both borders**, input tunnels, and a conditional terminal. **No clicking.**

That is the whole toolchain validated: a 2017 MIT library, driving LabVIEW 2026, generating configured
loop structures programmatically.

**One benign warning to expect:** "Load Warning Summary - Dependency loaded from new path". It appears
if a VI had previously been loaded from a *copy* of the library. Harmless; click Ignore. To avoid it,
do not keep a second copy of `LV-Scripting.lvlib` anywhere (the evaluation copy in `claudeDev` was
deleted for exactly this reason - two copies of the same `.lvlib` cross-link and confuse LabVIEW).

**Install/uninstall is tracked by VIPM**, so it can be removed cleanly - which is why VIPM was used
rather than copying files into `vi.lib` by hand.

#### `Create For Loop.vi` alone covers the hardest part of the kernel rebuild

Its connector pane, read directly off the front panel:

| direction | terminal |
|---|---|
| in | `Diagram in`, `Loop Count Terminal`, `Inputs`, **`Inputs Indexing?`**, `location (0,0)`, `Shift Register Inputs`, **`Number of Static Parallel Instances`**, `error in` |
| out | `Diagram out`, `Inputs` (inner terminals), `Shift Registers` (inner terminals), `Loop Counter`, `error out` |

Two of those matter enormously here:

- **`Number of Static Parallel Instances`** is the loop's **`P`** setting — iteration parallelism,
  configured *programmatically at creation time*. This is the exact thing an entire session was lost
  trying to enable by clicking a structure border, and the reason the existing four-fold kernel has a
  `P` terminal sitting unwired.
- **`Inputs Indexing?`** sets **auto-indexing per input tunnel** — precisely the change needed to
  replace the 2010 kernel's shift registers, which are what make the loop non-parallelisable.

It also returns the **inner terminal references** for the tunnels it creates, so the loop body can be
wired without hunting for terminals on screen at all.

#### Other directly relevant API VIs (84 total)

`Create SubVI.vi` · `Wire Inputs.vi` · `Wire Indicators.vi` · `Get Controls.vi` · `Get Outputs.vi` ·
`Get Term Type.vi` · `Conditionally Connect Wire.vi` · `Create Index Array.vi` ·
`Create Replace Array Subset.vi` · `Create Constant.vi` · `Exit For Loop.vi` · `Set Name.vi` ·
`Create Case Structure.vi` · `Create Property Node.vi` · `Create Open VI Reference.vi`

Examples 1-13 ship with it; **Example 8 - For Loops** and **Example 5 - SubVIs** are the two to read.

#### Install status: INSTALLED 2026-08-26 (user approved)

VIPM reported `installed / No Errors` for LabVIEW 2026 64-bit; the 84 API VIs live at
`vi.lib\Erdos Miller\LV-Scripting`, and `Example 8 - For Loops.vi` ran and generated a complete For
Loop purely by code. Installing via VIPM (rather than copying into `vi.lib` by hand) keeps the
install tracked and cleanly uninstallable.

*Historical note:* the first attempt to launch the `.vip` was blocked because installing software is
a system change, so the library was initially only extracted to `claudeDev\LVScripting_EVAL\` for
evaluation. **Delete that evaluation copy if it still exists** — two copies of the same `.lvlib`
cross-link and produce a confusing "Dependency loaded from new path" warning on load.

### Wider search, round 2 (2026-08-26) — two more candidates, one potentially important

The user noted the first search was not exhaustive. Two further options surfaced:

| library | license | needs | why it matters |
|---|---|---|---|
| **`rcpacini/LabVIEW-VI-Snippet`** | **MIT** | LabVIEW 2022, ships as a Packed Library (`.lvlibp`), **no external dependencies** | Programmatically **imports a VI Snippet PNG onto a block diagram** and **exports diagram code to PNG**. Also copies front-panel objects to their original positions, **wires the connector-pane terminals**, updates the VI icon and clones VI properties. |
| **LAVA "LabVIEW Scripting Tools"** (VIPM: `lava_lib_labview_api_scripting_tools`) | LAVA/OpenG-style (verify in VIPM) | VIPM install | Provides block-diagram refs, control-terminal refs, **connector-pane reference plus pattern selection and wiring controls to it**, creating primitives by enclosure, creating labels. The vipm.io page returned HTTP 403 from here — **verify inside the VIPM client**. |

**Why the snippet library could be a big deal for this project.** A VI Snippet is a PNG carrying an
embedded `niVI` chunk that contains the actual binary block-diagram code. So snippet import/export is
a way to move *whole working diagram fragments* between VIs programmatically — and the author states
it deliberately works around "limitations in the LabVIEW IDE's native object placement methods",
which is precisely the wall this project hit when trying to place and wire objects by hand.

Concretely, that suggests a much cheaper build path than wiring node-by-node: **build the parallel
loop body once (by hand or by scripting), export it as a snippet, then import it** into the target
VI — instead of scripting every node and wire individually. Worth testing on a copy before committing
to the node-by-node approach.

**Connector-pane wiring appears in both**, which matters because the replacement kernel must match the
existing four-fold connector pane exactly to drop into the main VI.

**Still the working decision:** `erdosmiller/lv-scripting` as the foundation (user's call). These two
are complements, not replacements — snippets for moving code fragments, LAVA tools for connector-pane
work.

### Why the editing route via Zuehlke is rejected for this project

Its own README is blunt, and the limitations land exactly on our use case:

- `ApplyAIXMLToVI` — the **edit** RPC — *"consistently fails with generic errors across multiple
  configurations."* Editing is precisely what we need.
- It **cannot regenerate VIs containing project-local subVIs or Express VIs.** Our tracking VIs are
  built almost entirely from project-local subVIs, so the write path is a non-starter here too.
- It rides NI's **private, undocumented `lvai.LVAI` gRPC**: *"no `.proto` in the install, no
  documentation, no version policy, and no promise that any of these RPCs will still be there next
  quarter."* On a shared rig running real experiments, a silent break after a LabVIEW update is an
  expensive failure mode.
- Author's own advice: *"Work on copies, keep your code in version control, commit before you let an
  assistant loose on it."* This project has no version control on the `.vi` files.

**But its read path is genuinely attractive** and low-risk: reading cannot corrupt anything, and
"VI → text" would let us see the four-fold kernel's actual wiring, plus the 2010 N-fold prior art,
without opening and squinting at diagrams. Worth a bounded experiment on a **copy**.

### DECISION (user, 2026-08-26)

**`erdosmiller/lv-scripting` is the chosen foundation** — *"erdosmiller seems to best fit our need."*
The search is explicitly **not** considered exhaustive, so keep watching for better options.
Installing it modifies the production LabVIEW install, so it requires the user's go-ahead.

### Recommended order

1. **Install `lv-scripting` via VIPM** and work through its examples — it is the stable, MIT-licensed
   base for *creating and wiring* code.
2. **Try Zuehlke's read path on a copy** to dump a VI to text. If it works, VI comprehension in this
   project stops being guesswork.
3. **Read `labview_mcp`'s scripting SubVIs for technique only** (`get_object_terminals` →
   `connect_objects(src, src_term, dst, dst_term)` is the pattern worth learning), without copying
   code that carries no licence.
4. Hand-build only the primitives that none of the above supply.

## 10. Clean Up Diagram, and wires vs variables

Both raised by the user 2026-08-26.

### Clean Up Block Diagram — yes, and it is scriptable

The toolbar's **Clean Up Block Diagram** button auto-arranges wires and node placement. Importantly it
is **not just a GUI button**: the same operation is the **`Diagram > CleanUp`** invoke node, and NI's
`Adding Objects.vi` and the lv-scripting examples already call it as the last step before closing
references. `KernelBuilder_v1.vi` inherits that call.

So generated code can be tidied **as part of the script**, with no manual step. That removes the last
hand-operation from `PLAN_kernel_parallel.md`.

*Caveat:* Clean Up is excellent for **machine-generated** diagrams, which have no layout intent to
destroy. On a dense hand-built diagram it can rearrange things in ways the author will dislike, and it
is not undo-friendly at scale — so do not run it over the existing tracking VIs casually.

### Wires vs local/global variables — for THIS project, use wires

There is a real alternative to wiring a repeatedly-used value everywhere: declare it as a
local/global **variable** and read/write it, or use a **Value property node**. It removes long wires
and can make a diagram much tidier.

**But for the parallel kernel specifically, wires are the correct choice, and variables would be a
bug.** Three reasons, in order of severity:

1. **Variables are not parallel-safe.** A local or global variable read/written from inside a
   **parallelised** For Loop is a genuine **race condition** — several loop instances execute
   simultaneously, and the order of their reads and writes is undefined. Since the entire purpose of
   V6 is to run bead iterations concurrently, introducing variables would reintroduce exactly the
   class of non-determinism we are trying to engineer away. Wires enforce dataflow, and dataflow is
   what makes the parallelism safe.
2. **`Value` property nodes are slow.** A Value property node marshals through the **user-interface
   thread**, which costs orders of magnitude more than a wire. Inside a per-bead tracking loop running
   at camera rate, that is a performance problem, not a style preference — and speed is this project's
   whole success criterion.
3. **They hide the dependency.** A wire states visually that A feeds B; a variable does not, so the
   execution order becomes implicit and the diagram becomes harder to reason about — and harder for
   LabVIEW to schedule.

**When variables *are* the right tool:** genuinely shared mutable state that several independent,
*non-parallel* loops must exchange — for example a stop flag between the motor loop and the camera
loop in the main VI. Even then, the robust idioms are a **DVR** or a **functional global / Action
Engine**, which enforce mutual exclusion, rather than a bare local variable.

**Why it does not bite us here:** each bead is fully independent — `Track 1 of N bds
xyz-kernel-reentrant.vi` takes the whole image and crops its own ROI, sharing nothing with other
beads. So there is no shared mutable state to model, and auto-indexed tunnels carry everything needed.

## 11. Static VI Reference must be STRICTLY TYPED for `Create SubVI.vi`

Found 2026-08-26 while building `KernelBuilder_v1.vi`. A freshly dropped **Static VI Reference**
(`Programming > Application Control`) outputs a plain, weakly-typed VI refnum. `Create SubVI.vi`'s
`VI Reference` input wants a **strictly typed** reference, so wiring the two produces a **black dashed
wire** — LabVIEW's type-mismatch rendering, not a broken/red-X wire and not a misclick.

Fix: right-click the Static VI Reference -> **`Strictly Typed VI Reference`** (it is greyed out until
the reference actually points at a VI, so assign the path first via `Browse for Path...`). The node's
output then carries the target VI's connector-pane type, and the wire goes solid.

**Reading wires by colour/style:**

| appearance | meaning |
|---|---|
| solid, coloured | connected, types agree |
| **black dashed** | **type mismatch** at one end |
| dashed with red X | broken — dataflow illegal or dangling |

**Also from this session — file dialogs eat the first keystroke.** Typing a full path into a Windows
"Select the VI to Open" dialog immediately after it opens dropped the leading `C`, yielding an
`:\Program Files\...` path and an "invalid filename" error. Click into the filename field, `Ctrl+A`,
*then* type; and press `Home` and capture to verify the head of the field before clicking OK.

## 12. Driving LabVIEW from Python over ActiveX/COM — the run/verify pipeline

This is the single biggest efficiency win found in this project: **configuring a driver VI, running
it, and verifying the result are all script calls, with no GUI interaction at all.** Wrapper:
[tools/kb_com.py](../tools/kb_com.py).

"COM" here is Microsoft's **Component Object Model** — the same mechanism as ActiveX, nothing to do
with serial COM ports. LabVIEW registers itself as an automation server, so any process can obtain a
reference to the *already-running* instance and call its VI Server API.

### The connection

```python
from win32com.client import dynamic
lv = dynamic.Dispatch("LabVIEW.Application")
vi = lv.GetVIReference(vi_path, "", False, 0)
```

Prerequisites on this rig, both already enabled: VI Server **ActiveX** protocol, and TCP on **port
3364**. `LabVIEWCLI.exe` also exists and connects on 3364, but its `RunVI` operation fails with
**error 1031** (connector-pane constraint), so the COM route is the one to use.

### Methods must be invoked by DISPID

`dynamic.Dispatch` cannot see LabVIEW's methods by name through normal attribute access. Invoke them
explicitly:

```python
import pythoncom
def invoke_method(com_obj, name, *args):
    ole = getattr(com_obj, "_oleobj_", com_obj)
    dispid = ole.GetIDsOfNames(0, name)
    return ole.Invoke(dispid, 0, pythoncom.DISPATCH_METHOD, 1, *args)
```

### What is available, and what is not

| member | dispid | use |
|---|---|---|
| `ExecState` | 557 | **0 = BROKEN** (shattered run arrow), 1 = idle/runnable, 2/3 = running |
| `SaveInstrument` | 1002 | persist in-memory scripted edits to disk |
| `Abort` | — | stop a run; see the base-VI caveat below |
| `FPWinOpen` | 534 | settable — **closes a zombie error dialog** that ignores clicks |
| `CloseFrontPanel` / `OpenFrontPanel` / `FPState` | 1061 / 1080 / 608 | window control |
| `ExportVIStrings` | 1000 | dump documentation and connector names to text |
| `GetPanelImage`, `Revert`, `GetLockState`, `SaveForPrevious` | 1016, 1018, 1021, 1024 | occasionally useful |

**Not available:** `IsBroken`, `GetSubVIs`, `CallsList`, `MethodNames`. `AllVIsInMemory` fails with
0x408 "VI Server access denied".

`ExecState` is the important one — it answers *"is the wiring I just generated legal?"* as data.
**Verify generated code this way, never by screenshot.**

### Three traps that cost real time

- **`SetControlValue` is runtime-only.** Values set over COM vanish when the VI unloads from memory.
  To persist a driver's configuration, set the values and then use **`Edit > Make Current Values
  Default`** in the GUI, followed by a save. This bit twice before it was understood.
- **ActiveX cannot dispatch parallel clones.** `GetVIReference(path, "", False, 0x40)` asks for a
  reentrant-run reference, but every ActiveX caller receives **the same base VI** regardless. Proven:
  a second job overwrote the first job's front-panel path control, and its `Run` failed 0x3E8 "not in
  a state compatible". Real parallel dispatch needs a G-native `Start Asynchronous Call` launcher.
- **`Abort` on a clone reference does nothing across threads**, but `Abort` on the **base VI**
  reference from a fresh process releases hung clones instantly (it also aborts sibling jobs).

### Make errors return as data, never as a dialog

A `Simple Error Handler` in a scripting driver is actively harmful for unattended runs: its modal
dialog holds `Run` hostage indefinitely, and its window is titled after the *VI* —
`[Details Display Dialog.vi] Front Panel` — so it is easy to miss in a window list. Delete it and
wire an **`error out` cluster indicator** instead. In this project that change turned apparently
random 20–74 minute hangs into a 1.0 s run returning `error 1055` as a value.

**Hang triage rule:** on any suspected hang, enumerate windows *first* and look for a `[*.vi]`-titled
dialog. Also give every scripted run a watchdog that aborts on timeout — the edits made before the
hang usually survive.

## 13. The Op-VI fleet and GScript — the current architecture

Directed by the user after the monolithic builder failed opaquely: **do not build one VI that
generates the whole target in a single run.** Instead build small, frozen **Op VIs** — each replacing
one screenshot-and-click operation — and compose them from a command script.

The division of labour is deliberate. The **G side stays basic and never changes**: open a VI, create
a node/subVI/structure at a position, find a terminal by name, wire A→B, create a constant or
control, save. All generality lives in the **script**, because future code shape is unknown and more
VIs of other kinds will be built on this same setup. The workflow becomes *write script → run once →
read the per-line log*, rather than *edit driver VI → run → screenshot-verify*.

Design rules for an Op VI:

- **Arguments are front-panel controls, not diagram constants** — so they can be set over COM.
- **Defaults are saved with `Edit > Make Current Values Default`**, or the configuration evaporates
  when the VI leaves memory.
- **One operation, no chaining logic.** Sequencing is the script's job.
- **Errors come back through an `error out` indicator**, never a dialog (see §12).
- v0 Op VIs may **leak references deliberately** — leaving the target VI in memory is wanted for
  chained operations, and `Close Reference`'s refnum input is awkward to wire by hand.

A bare structure created by an Op VI legitimately leaves its target **broken** until later script
lines wire it. That is correct behaviour, not a defect — check `ExecState` at the *end* of a script,
not between every line.

Current fleet status is tracked in [STATUS.md](../STATUS.md).
