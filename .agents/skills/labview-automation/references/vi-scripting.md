# VI Scripting reference (LabVIEW Automation skill)

Loaded from SKILL.md. Object creation, libraries, wiring protocol, dataflow rules, the op-fleet pattern.


## VI Scripting essentials

### Start from NI's shipped examples

`<LabVIEW>\examples\Application Control\VI Scripting\` ships runnable drivers for creating objects and
VIs, navigating and modifying diagrams, moving/selecting objects, structures, and connector panes.
**Copy them somewhere writable and adapt one.** Hand-building a driver by clicking reliably costs a
whole session and often still does not run.

### `New VI Object` — the terminal contract

| terminal | position | wire with |
|---|---|---|
| `vi object class` | **top** edge | VI Server Class constant (right-click > `Select VI Server Class`) |
| `owner refnum` | left, 1st | the VI reference |
| `style` | left, 2nd | ring constant naming the object, e.g. `For Loop`. **REQUIRED** |
| `position` | left, 3rd | cluster of two I32 |
| `error in` | left, bottom | error chain |
| `Path`, `bounds` | — | **leave unwired** |

`class` fixes the *datatype of the returned reference*; `style` fixes *what object gets created*. They
must agree.

Class paths worth remembering: For Loop = `Generic > GObject > Node > Structure > Loop > ForLoop`;
While Loop = `... > Loop > WhileLoop`; SubVI = `Generic > GObject > Node > SubVI`.

### Error codes

| error | meaning | real cause |
|---|---|---|
| **1059 (0x423)** "Unexpected file type" | `Path` got a non-typedef | a `.vi` was wired into `Path`. It is only for `.ctl`/`.lvclass`. Leave it unwired. |
| **1057 (0x421)** "cannot be cast to the specified type" | `class` and `style` disagree | e.g. class `ForLoop` with style `Subtract` |
| **1054 (0x41E)** "The specified object was not found" | the **`style` value does not name a real object** | Seen on every attempt across classes `Generic`, `GObject` and the concrete `Function` with `style` 0–39. |

**Read the error text before theorising — NI ships it.** `resource\errors\English\LabVIEW-errors.txt`
maps every code to its official description (`grep -n "1054"`), and 1054 turns out to be *"The
specified object was not found"* — nothing to do with classes. An earlier theory here, that 1054
meant "the class is abstract", was **disproved** by testing a concrete class, which failed
identically. Two classes failing the same way is evidence that something *common* to the attempts is
wrong, not evidence about the classes.

**`style` is not a small ordinal.** Wiring a plain U32 and feeding 0, 1, 2… does not select "For
Loop"; a sweep of 0–399 created nothing. The `style` input wants a **ring constant** whose items
carry LabVIEW's real style numbers, and `Create > Control` on that terminal gives a bare U32 that
loses them — so making `style` runtime-settable that way silently breaks the node.

### Do not build a generic node-creator — copy from a donor VI instead

This is the settled community answer, and it is worth taking before spending a session on
`New VI Object`. Asked how to drop a node whose style is missing from the ring, NI's forums give the
same advice twice over: **"create a VI with the function you want and copy it from that VI rather
than attempting to drop it."** The style ring does not expose every object, brute-forcing the numeric
codes is explicitly called out as risky ("iterate over all the values not in the list and log those
which don't return errors, though this method risks crashing LabVIEW"), and there is **no documented
way to read an existing node's style back** to learn its code.

So the maintainable pattern for machine-generated diagrams is a **donor VI** holding one clean
instance of every node the generator needs, plus a copy operation — either VI Server copy/paste or
`rcpacini/LabVIEW-VI-Snippet`, which moves whole diagram fragments. `New VI Object` stays useful for
the handful of styles that *are* in the ring (For Loop, While Loop, Case Structure and friends),
which is exactly what NI's own `Adding Objects.vi` example demonstrates.

Sources: [New VI Object - Variant Constant](https://forums.ni.com/t5/LabVIEW/New-VI-Object-Variant-Constant-VI-Scripting/td-p/2853348) ·
[Input for style in "New VI Object"](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Input-for-style-in-quot-New-VI-Object-quot-function/td-p/3267356) ·
[finding out "new VI object" parameters](https://forums.ni.com/t5/LabVIEW/LabVIEW-VI-scripting-finding-out-quot-new-VI-object-quot/td-p/3932054)

**And the process lesson:** read the vendor's shipped error text first, then search the forums, and
only then design an experiment. Five experiments were spent on error 1054 here; one search would have
redirected the whole approach.

**What *is* established:** `style` is runtime-settable — right-click it → `Create > Control` yields a
plain U32 — whereas **`vi object class` is not**. Converting that constant with `Change to Control`
produces an opaque refnum control that COM will happily set to `0`, `1` or even a string, and the
node still fails, because the class specifier is compile-time information.

**Errors hide.** LabVIEW's `Simple Error Handler` dialog is titled after the **VI's name**, not
"Error". A scripting run that appears to do nothing may have a modal dialog open under a bland title —
check the window list for an unexpected entry.

### Three rules that bite

- **CLOSE EVERY REFERENCE.** VI refs, diagram refs, and every node/wire/terminal ref must be closed
  with `Close Reference`, or the LabVIEW process **leaks memory severely**.
- **Dataflow can make a wire illegal.** A value produced *inside* a For Loop can never feed *that same
  loop's* `N` terminal, because `N` resolves before the loop runs. LabVIEW renders the rejection as a
  dashed wire with a red X. A broken wire is a semantic verdict, not necessarily a misclick.
- **Test whether an input is required** by deleting its constant and watching the run arrow: solid =
  optional, shattered = required. Faster and more reliable than reading documentation.

### Wiring a closed VI silently does nothing — open the panel first, save before closing

Two rules proven the hard way (2026-08-28, three silent failures then one lost build):

- **A target loaded only via `GetVIReference` declines edits silently** — no error, no dialog, the
  object count just stays put. First seen on wires; later confirmed for **object drops too**, so
  treat it as applying to every mutation, not only wiring. (A drop *can* succeed on a target whose
  file was just copied in and is still fully loaded — which is why it looked drop-safe at first.
  Do not rely on that.) Invoke
  `OpenFrontPanel` on the target first (forces the full load/edit state); then wires connect. An
  open *window* per se is not the documented requirement — a fully loaded, editable diagram is —
  but `OpenFrontPanel` is the reliable way to get there from COM.
- **Save BEFORE `CloseFrontPanel`.** Closing the panel of a modified VI that nothing else references
  unloads it and **silently discards every in-memory edit** — a completed 8-wire chain build
  evaporated this way, and the subsequent save wrote pristine bytes as if nothing had happened.
  Order is always: open panel → edit → verify → **save** → close panel.

Wire-connect semantics (erdosmiller `Wire Inputs.vi`, likely native `Connect Wire` too): a
**missing** destination terminal name raises error 5001; a **found** name whose connection is
illegal is **declined silently**; branching from an **already-wired source terminal** is declined
silently too. An unwired error *input* is harmless — only an unwired error *out* that receives an
error pops the automatic-error-handling dialog, so a chain without a sink just relocates the
dialog to its last node. `vi.lib\Utility\error.llb\Clear Errors.vi` is a drop-in sink: it consumes
the chain and never emits an error of its own.

Terminal-name conventions (all confirmed on LabVIEW 2026): NI/erdosmiller *subVIs* use
`error in (no error)` / `error out`; *primitives* vary — `To More Specific Class` uses plain
`error in`, while `New VI Object` uses `error in (no error)`. `Traverse for GObjects.vi` **does**
have error terminals (`error in (no error)` / `error out`).

### Auto-indexing vs shift registers — the key to loop parallelism

A For Loop whose results accumulate in a **shift register** has a loop-carried dependency and
**cannot be parallelised**: iteration *k+1* consumes what *k* produced. Replace shift registers with
**auto-indexed output tunnels** — each iteration writes its own index, no dependency, and iteration
parallelism becomes legal. Auto-indexed *input* tunnels also make `N` unnecessary, since the count
follows the array length by construction.

If a loop shows a `P` terminal that is present but unwired, suspect exactly this: someone wanted
parallelism and could not enable it because of a shift register.


## Libraries — evaluate before building

- **`erdosmiller/lv-scripting`** — **MIT**, 84 API VIs, declares `LabVIEW>=15.0`, and its spec sets
  `close labview before install=FALSE` so installing does not disturb a running session. Last release is 2017, but it was **installed and verified end-to-end on LabVIEW 2026**: its
  `Example 8 - For Loops.vi` ran and generated a complete For Loop (N wired, i terminal, shift
  registers, tunnels, conditional terminal) purely by code. `Create For Loop.vi` takes
  `Inputs Indexing?` and **`Number of Static Parallel Instances`** (the `P` terminal) as *parameters*
  and returns inner tunnel refs — so auto-indexing and parallelism become arguments rather than GUI
  surgery. Also `Create SubVI.vi`, `Wire Inputs.vi`, `Get Controls/Outputs.vi`, `Create Index Array.vi`,
  `Create Replace Array Subset.vi`, `Exit For Loop.vi`. **Recommended default — this is the one to use.**
  A `.vip` is a ZIP archive, so extract and inspect it before installing anything. Install **via VIPM**
  rather than copying into `vi.lib` by hand, so the install is tracked and can be uninstalled cleanly.
  Never keep a second copy of the same `.lvlib` around — duplicates cross-link and produce a benign but
  confusing "Dependency loaded from new path" load warning.
- **`rcpacini/LabVIEW-VI-Snippet`** — MIT, pure LabVIEW. Imports/exports block-diagram code as snippet
  PNGs (an embedded `niVI` chunk). Good for moving whole working fragments rather than scripting
  node-by-node.
- **LAVA `lava_lib_labview_api_scripting_tools`** (VIPM) — connector-pane refs, pattern selection, and
  wiring controls to the pane.
- **`Zuehlke/labview-mcp`** — MIT, LabVIEW 2026 Q3 only. **Read-only value:** converts a VI to text,
  which byte-level extraction can never do. Its *edit* RPC fails by the author's own account, it
  cannot handle project-local subVIs, and it rides an undocumented private gRPC with no version policy.
- **`CyantusLYX/labview_mcp`** — has the right primitives, but its licence reads "[To be specified]",
  which means all rights reserved. Read it for technique; do not vendor the code.


## THE WIRING PROTOCOL — follow this, do not improvise

Consolidated from a full session of GUI wiring on LabVIEW 2026. Improvised aiming produced **eight
consecutive silent failures**; this procedure then landed every remaining wire. The governing idea is
the same as Rule 0's: **never compute where a terminal is — make LabVIEW tell you.**

### Step 1 — locate the terminal, by node type

**Never trust coordinate arithmetic on a node.** A terminal row estimated from the node's bounding box
was off by 13 px in one measured case, which is fatal for a 2 px hot zone and fails *silently*.

| node type | how to reveal its terminals |
|---|---|
| **subVI** | right-click → **`Visible Items > Terminals`**. The icon redraws its connector pane as ~8×9 px coloured rectangles — big targets, colour-coded by datatype. |
| **primitive** (Index Array, To More Specific Class, …) | **no Terminals view exists.** Instead **hover the node and capture**: LabVIEW draws small **diamond markers** on every terminal, coloured by datatype. Measure the diamond. |

An **already-wired terminal shows no diamond**, which doubles as a wiring checklist: hover a node and
every terminal still needing a wire announces itself.

### Step 2 — confirm before committing

Open **Context Help** (`Help > Show Context Help`) and keep it open while hovering. It is a live
readout, not a static reference:

- Hovering a node shows its **full connector map with every terminal name**, so you learn the layout
  in one capture instead of one hover per terminal.
- Hovering **empty space** shows the generic *"move the cursor onto a node"* message — which is how
  you discover that the point you have been clicking is not on the node at all.
- Hovering a **broken wire** (no click) makes Context Help **name the error**, cheaper than opening
  the Error List.

A hover also raises the ordinary tip strip naming the exact terminal. Confirm the name before wiring.

**Caveat:** an open Context Help window **blocks all right-click context menus**. Close it before
menu work, reopen it for the next hover.

### Step 3 — wire, then verify

**Click source, then click destination — never a drag.** Start **2–3 px OUTSIDE** a *constant's*
right border (a click on the border resolves to the positioning tool); click *on* a node's terminal
rectangle or diamond. A constant's output stub sits at the vertical centre of its right border; a For
Loop's `N` box sits at exactly `(left_edge, top_edge)`.

Then **`probe` a 1-px column just outside the destination's left edge** and confirm the wire's colour
appears at the expected row. A 2-px-wide run means an array wire; 1 px means a scalar.

### Step 4 — read the failure mode before recovering

The wrong recovery makes things worse, so classify first:

| symptom | cause | recovery |
|---|---|---|
| probe white, **dashed line visible** | wire started, rubber band pending | one plain `click` on the destination commits it |
| probe white, **object selected** (marching ants) | the wire never started | **re-aim the source** — clicking the destination merely selects it |
| wire drawn but **red X** on it | type or class mismatch | fix the *types*, not the click — see the cast rule below |
| dashed segment that survives Escape and canvas clicks | a real broken wire is on the diagram | **`Edit > Remove Broken Wires`** |

**`Edit > Remove Broken Wires` is the cleanup tool of choice** — it deletes only broken segments and
leaves good branches intact. Do **not** reach for `Edit > Undo`: with a rubber-band step in the
history it undoes something other than the wire you meant, while the red X survives.

### Branching one output to two destinations

- Starting the second wire **on the existing wire** leaves a pending rubber band, and the usual
  "click empty canvas" gesture **cancels** it — the attempt vanishes silently.
- Starting again **at the source terminal** does create the branch, but often leaves a broken segment
  between the source and the new junction, killing the whole tree while looking connected.

So: branch from the source terminal, then run `Remove Broken Wires`, then probe both destinations.

### Class mismatches: `Traverse for GObjects` returns GObject

NI's `Traverse for GObjects.vi` (`vi.lib\Utility\traverseref.llb`) takes a **Class Name** filter,
which makes its `References` output look as though it is already that class. It is not — the
references are typed **GObject**. Feeding one to an API wanting a `Node` (lv-scripting's
`Get Outputs.vi`, `Wire Inputs.vi`) draws a wire that stays broken, and the Error List names it
exactly: **`Wire: Class conflict`**.

Insert a **`To More Specific Class`** node, with a VI Server Class constant on its `target class`
input. **A missing node cannot be fixed by re-clicking** — recognise this class of failure early.

### Setting a VI Server Class constant

Right-click → **`Select VI Server Class`** → a nested hierarchy (`Generic ▸ GObject ▸ Node ▸ …`).
**Clicking a category row only opens its submenu; it does not select that class.** To select `Node`,
hover `Node` to open its submenu and click the **first entry inside**, which repeats the category's
own name — the same pattern at every level.

A wrong class looks perfectly healthy until a downstream wire breaks, so **verify by reading the
constant's label afterwards**.

### Menu geometry

**Context-menu geometry is stable relative to the right-click point** — measured `Visible Items` =
click + (57, 9), and its `Terminals` sub-item = that + (204, 19).

**Menu-bar and deep-submenu rows are NOT stable** and shift between captures; two mis-selections came
from clicking a captured coordinate a moment later. For those, the only safe sequence is
**hover the target row → capture → confirm it is highlighted → click that same coordinate**.

### When a scripted edit "succeeds" but does nothing, read the Error List

`View ▸ Error List` (Ctrl+L) names the exact failure — *"SubVI 'X.vi': required input 'Shift
Registers' is not wired"* — in one step, where guessing costs many. Use it the moment
`ExecState == 0` and the cause is not obvious. Two companions:

- **A silent no-op usually means a swallowed error.** An Op whose error chain ends in
  `Clear Errors.vi` cannot report anything: a bad terminal name raises 5001 *inside* it and the
  sink eats it, so the call returns clean having done nothing. Verify by **counting what should
  have been created**, never by a clean return. To find out *which* name is wrong, drive a
  **sink-less** version of the op with an EMPTY destination array — the resulting dialog is the
  answer (and the watchdog turns it into an exception).
- **A required input can be satisfied without creating a constant.** Feeding an array input a
  genuinely empty array is often the "none of these" value, and a library VI whose name filter is
  left empty returns an empty array — so a second instance of a *getter* can be the empty-array
  source when the fleet has no constant-creation ability.

### Terminal hot-zones: hover to find them, don't compute them

An icon-only subVI's terminals are ~3 px. Hovering the right spot draws **diamond markers on the
node and pops a tooltip naming the terminal** — so probe a short vertical line of candidate
y-values, screenshot each, and click only where the tooltip confirms the name. Do **not** derive
the coordinate from the reporter's `Position`: a node reported at `(790, 360)` had its visible
icon at `(800, 391)`. The reporter is authoritative for scripting, the hover for clicking.

**A pending wire gesture blocks every COM call.** If a `wire` click leaves a rubber-band waiting
for its second endpoint, LabVIEW answers nothing until it is cancelled — press **Esc** (twice is
safe) before the next scripted step. This looks exactly like a hang with no dialog.

### Injected right-clicks may open nothing — use the left-click dropdown or the menu bar

On LabVIEW 2026, right-clicks injected with `mouse_event` (RIGHTDOWN/RIGHTUP) opened **no context
menu at all** — not on a diagram constant, not on bare canvas, at any delay; the dedicated
context-menu key (VK_APPS) after selecting the object also did nothing. (Older notes in this skill
assume right-click menus work; treat that as version- or input-method-dependent and verify with a
full-screen `shot` before clicking where you expect a menu item.) Two routes that do work:

- **A class-specifier constant opens its class picker on a plain LEFT click.** Hover a category to
  expand its submenu (allow 1–2 s), then click the leaf. `Generic ▶ GObject ▶ GObject` retargeted a
  constant first try, and the connected Invoke node's header updated to `GObj` immediately —
  confirmation without running anything.
- **The menu bar always works** (`Window ▶ Show Block Diagram`, etc.). Prefer it over shortcuts.

### Copying a node you cannot create: `GObject.Move` with `Duplicate?`

`New VI Object` cannot create most node types (error 1054), and NI's own advice is to copy from a
donor VI instead. The programmatic mechanism is **`GObject.Move(owner = <destination diagram>,
position, Duplicate? = TRUE)`** — cross-VI duplication, available since LabVIEW 2010. Supplying an
owner in another VI makes it a copy even with `Duplicate?` false. It returns **no reference to the
copy**, so identify the new object by uid-set difference on the destination.

NI ships a runnable driver: `examples\...\VI Scripting\Moving Objects\Simple Move.vi`. Two facts
make it reusable as a tool rather than a demo: its source and target are **static VI references**
to two adjacent `Test - Moving Objects Source/Target.vi` files (so both can be **byte-substituted**
by an ordinary file copy), and the object to copy is chosen by a **front-panel string control**
(`Add Label`) — COM-settable. Retarget its class-specifier constant from `Node` to `GObject` once
and it copies anything by label. Diagnostics: **1054** = label not found, **1057** = found but the
class constant disagrees. Revert both Test files before each run, or a stale in-memory copy
shadows the substituted bytes.

For a *wired fragment* rather than one object, the equivalents are
`TopLevelDiagram.Make Selection` → `Copy Selection` → destination `AbstractDiagram.Paste(position)`
(paste onto the actual subdiagram reference, not the top level), or `Move Selected Objects`.

### Place nodes with QUICK DROP, not the palette

`click canvas` -> `Ctrl+Space` -> type the node name -> `Enter` -> **click where you want it**.
That last click is required; `Enter` alone places nothing.

**Structures place with TWO clicks, not one.** Quick Drop works for structures (For Loop etc.), but
after `Enter` the first canvas click only **anchors one corner**; a second left-click sets the
opposite corner and actually creates the structure. Between the clicks the canvas looks completely
empty — the pending rubber-band does not render in `PrintWindow` captures — so do not misread the
mid-way screenshot as failure and start a recovery (a stray right-click there does *not* cancel the
placement; the next left-click still completes it, wherever it lands).

**Caveat, learned the hard way:** this worked first try for the **built-in primitive**
`Open VI Reference`, but **failed three times** for `Create SubVI.vi`, a member of an installed
*library* — Quick Drop listed it, but no node was ever placed. Quick Drop appears reliable for palette
primitives and **not** for library VIs. For library VIs, use the **library's own palette entry** — an installed VIPM library registers
one at the bottom of the Functions palette (e.g. `Erdos Miller > LV-Scripting`), and placing
`Create SubVI.vi` from there worked first try. Categories need two clicks, the leaf one click, then
click the canvas to drop.

### Windows open off-screen — move them deterministically

LabVIEW often opens diagram windows partly or wholly off-screen. Title-bar double-click to maximise is
unreliable; use a real `MoveWindow` call (`-Action movewin`) before doing any click work.

### Other hard-won facts

- **Controls palette = you are on a FRONT PANEL.** The Functions palette exists only on a block
  diagram. Every VI has two windows with near-identical titles that overlap on screen.
- Palette **category** needs two clicks; a **leaf item** needs one (a second click drops a stray copy).
- Palette geometry does **not** follow the click point — re-crop it each time.
- Menus beat sent shortcuts: `Ctrl+R` / `Ctrl+Z` / `Ctrl+S` frequently never arrive, and fail
  **silently**, so the next screenshot looks identical and you misdiagnose your logic.
- Popup and dropdown menus are separate top-level windows — invisible to `shotwin`; use full-screen
  `shot`.
- Submenus open on **hover**; wait ~2 s before capturing.
- Structure **borders do not hit-test** reliably on a dense diagram. Build in empty canvas, or script it.
- Freshly placed objects stay selected — click empty canvas to commit before probing.
- `Create > Constant` on a terminal generates a correctly-typed constant; you then only set its value.
- Long ring dropdowns: type-ahead is unreliable; scroll with `wheel` and click the item.
- **Clicking a small boolean constant TOGGLES it.** The operate tool is active over booleans, so a
  click meant to *select* silently flips True↔False and the diagram still looks right. Select
  booleans with a rubber-band drag started on empty canvas, never by clicking them.
- **A drag issued immediately after focusing a window is eaten by the activation click.** Click once
  on empty canvas first. Otherwise the rubber band never starts, which looks identical to a band
  that selected nothing.
- **Property-node header rows pack two outputs ~4 px apart** (`refnum out` and `error out` in one
  measured case). Hover for the tip strip before wiring; colour cannot separate them.
- **Error wires pass *through* node bodies**, so a mid-node click may select the wire rather than the
  node. Zoom and verify the selection before pressing Delete.
- **File dialogs eat the first keystroke.** Typing a path immediately after a "Select the VI to Open"
  dialog opens drops the leading character (`C:\...` → `:\...` → "invalid filename"). Click the
  filename field, `Ctrl+A`, then type, then verify the head of the field before OK.

### Strictly typed references, and reading a wire's appearance

`Create SubVI.vi`-style APIs want a **strictly typed** VI reference. A freshly dropped **Static VI
Reference** is weakly typed, so wiring it produces a **black dashed** wire — which is LabVIEW's
*type-mismatch* rendering, not a broken wire and not a misclick. Fix: right-click the Static VI
Reference → **Strictly Typed VI Reference** (greyed out until a path is assigned, so set the path
first via `Browse for Path…`).

| appearance | meaning |
|---|---|
| solid, coloured | connected, types agree |
| **black dashed** | **type mismatch** at one end |
| dashed with a red X | broken — dataflow illegal or dangling |


## Wires vs variables in parallel code

Local/global variables and `Value` property nodes are a legitimate way to avoid long wires — **but
never inside a parallelised loop.** Concurrent instances reading/writing the same variable is a
**race condition**, whereas wires enforce dataflow and are inherently parallel-safe. `Value` property
nodes additionally marshal through the **UI thread**, which is orders of magnitude slower than a wire
and unacceptable in a tight acquisition loop. For genuinely shared mutable state between separate
non-parallel loops, prefer a **DVR** or a **functional global / Action Engine**, which enforce mutual
exclusion, over a bare variable.

**Clean Up Block Diagram is scriptable** — the toolbar button's equivalent is the `Diagram > CleanUp`
invoke node, so generated code can tidy itself with no manual step. Ideal for machine-generated
diagrams; avoid running it over dense hand-built ones, whose layout carries authorial intent.
**On a large real diagram it is also a trap for automation:** CleanUp can run for MINUTES with no
progress indication — the calling script just sits in run mode (the only tell: a running VI's front
panel title drops the " Front Panel" suffix), which looks exactly like a hang or a silent no-op —
and when it finishes it has re-laid-out the ENTIRE diagram, so nothing (including the objects your
script just created at chosen positions) is where you expect. A scripting chain cloned from an
example ships with CleanUp at the end: REMOVE it before pointing the chain at any real VI, and wire
the Create-structure `location` input instead so results land at known coordinates.


## Build a fleet of frozen primitives, not one big generator

The tempting design is a single driver VI that generates the whole target in one run. It fails
badly: when something is wrong deep in a fixed chain, the diagnosis is pixel forensics on a diagram
you did not lay out, and every change means GUI surgery on the driver itself.

The alternative that works: **small, frozen Op VIs — each replacing exactly one screenshot-and-click
operation — composed by a command script.** The G side stays basic and never changes (open a VI,
create a node/subVI/structure at a position, find a terminal by name, wire A→B, create a constant or
control, save); all generality lives in the script, which is cheap to rewrite. The workflow becomes
*write script → run once → read the per-line log*, instead of *edit driver → run → screenshot-verify*.

Design rules for an Op VI:

- **Arguments are front-panel controls, not diagram constants**, so they can be set over COM.
- **Save defaults with `Edit > Make Current Values Default`**, or the configuration evaporates when
  the VI leaves memory.
- **One operation, no chaining logic.** Sequencing belongs to the script.
- **Errors return through an `error out` indicator**, never a dialog.
- A v0 Op VI may **leak references deliberately** — leaving the target in memory is wanted for
  chained operations, and `Close Reference`'s refnum input is awkward to wire by hand.
- A bare structure created by one Op VI legitimately leaves its target **broken** until later lines
  wire it. Check `ExecState` at the *end* of a script, not between every line.


## Connector pane by script (codex research 2026-08-31, sources in archive/peer/)

- VI property **`Connector Pane:Reference`** → ConnectorPane refnum; ConnectorPane property
  **`Pattern`** (U32, valid 4800–4835: 12-term 4-2-2-4 = **4815**, 16-term 5-3-3-5 = **4833**);
  invoke **`Assign Control To Terminal`**(Control refnum, Terminal Index). Set the pattern FIRST —
  treat a pattern change as clearing all assignments. Not settable while the VI runs/is reserved.
- **Terminal indices are not geometric** — read them from NI's `Connector Pane Pattern
  Reference.vi`, or mirror another VI's map read back via ConnectorPane **`Controls[]`** (one
  control refnum per terminal, terminal-index order, null = unassigned).
- **A byte-copied VI inherits its source's entire pane** (pattern + assignments) — check before
  building any pane scripting: the task may already be done. Verified 2026-08-31: a copy's pane
  widget was pixel-identical to its source's.
- Do NOT use VI property `Connector Pane:Set` (whole-pane copy with name/type matching demands).

## The bootstrap terminal (negative-search record, 2026-08-31)

Every fully-scripted route to a TYPED property node bottoms out in a cycle: `Create Property
Node.vi` needs a class-typed `reference` wire → a typed wire needs `To More Specific Class` with
the right class constant → retyping a `ClassSpecifierConstant` by script needs a property node
(`Class Name` IS writable — but writing it needs a property node of class ClassSpecifierConstant)
→ which needs a typed wire. Auxiliary exits checked and closed: `Create To More Specific Class.vi`
has a numeric `target class` input but no discoverable ID scheme (not a ring; no name strings in
the file); `New VI Object` numeric styles were swept 0–399 historically and create nothing;
`Get Outputs`→scalar needs an Index Array whose scripted creation (`Create Index Array.vi`) needs
the same driver being bootstrapped. **Conclusion: ONE manual property-node placement into ONE tool
op is a genuine, rule-compliant bootstrap** (evidence for the GUI gate). Once one op can write
`ClassSpecifierConstant.Class Name`, every later cast/property node is scriptable transitively.

## Unnamed-terminal wiring — peer-reviewed design constraints (2026-09-01, archive/peer/)

- **`Node.Terminals[]` exists but its array ORDER is not a contract.** Select terminals by the
  index shown in Context Help (enable "Display additional VI Scripting information"), or better by
  primitive-SPECIFIC properties — e.g. `IndexArray` exposes `Array Input Terminal`, `Index Count`,
  `Index Terminals[][]`, `Output Terminals`. Growable primitives (Decimate/Interleave) are exactly
  the category where generic Terminals[] indexing is discouraged. Verify any resolved terminal by
  direction (`Is Source?`) + datatype, and fail closed on signature mismatch.
- **Scripted terminal-to-terminal connection**: endpoint ORDER changes behaviour (documented
  case-tunnel bug reports); border crossings auto-create tunnels but not necessarily the intended
  one; loose/broken wires cannot be re-attached (delete + `Create Described Wire`). NEVER treat
  "no error" as success — verify endpoint wiring state, owning diagrams, and target ExecState.
- **Donor labels are discovery hints, not identity.** `Node.Label` is only reliable after the label
  has been DISPLAYED once (writing `Label.Text` does not force visibility), and no source
  guarantees label or grown-terminal-count survival across cross-VI duplicate+move. Donor
  acceptance test: reporter dump before/after copy comparing class, terminal count, per-terminal
  direction/datatype — in LabVIEW 2026, after save/reopen.
- **Peer verdict: generic `OpWireRef` 4/10; FUSED topology-specific creators 8/10** (e.g. Exit For
  Loop capturing outer terminals + Wire Indicators in one dataflow; Create Index Array-style
  creators that return terminal refnums). Build per-topology ops, not one universal wirer.


## Front-panel objects ARE scriptable (peer-verified 2026-09-04; machine confirmation pending)

"The fleet cannot create front-panel objects" was a statement about our op fleet, never about
LabVIEW. Three documented routes (archive/peer/2026-09-04-fp-object-creation-scripting.md):

1. **`Terminal.Create Indicator`** (method 6349C02; siblings `Create Control` 6349C01,
   `Create Constant` 6349C00) — the scripted equivalent of right-click > Create > Indicator on a
   node terminal. Derives the FULL datatype (element type, array rank) from the terminal and
   returns the new control's reference. Preferred: no style codes, no shell/element assembly.
2. `VI.Create from Reference` / `Create from Data Type` — new FP object from a typed template
   reference (what NI's example `Create Control From Reference.vi` demonstrates).
3. `New VI Object` with the VI's **Panel** refnum as owner and a control style from the ring
   (`Array (classic)`, then a nested New VI Object with the array ref as owner for the element).
   Objects are created as CONTROLS; flip with `Control.Indicator = TRUE` (writable in edit mode).

Geometry: `GObject.Position` is read/write for FP objects (upper-left incl. label);
`GObject.Bounds` is read-only — size only via `New VI Object`'s `bounds` input at creation or
class-specific properties. `Array.Number of Rows/Columns` set VISIBLE cells, not rank.

Op to build: OpCreateIndicator_v0 = Traverse node -> `Get Outputs.vi` (terminal ref by name) ->
Invoke Node `Create Indicator` (erdosmiller `Create Invoke Node.vi`). The terminal-typed wire from
Get Outputs should give the invoke node its class context without a GUI bootstrap.

## COM `Run` hangs with no dialog (2026-09-05) — what is and is not known

Two hangs of ~180 s (gscript's own watchdog, not a LabVIEW timeout) hit a reporter/revert Run
during unattended benchmark prep. **Refuted by test:** SendInput Alt/Esc focus before the call
(revert → focus → Run, with and without a click in between: all instant). **Unproven:** "a killed
or concurrent COM client blocks the next client" — correlated twice, but codex found no NI evidence
that VI Server serializes external clients for the duration of `Run` or holds an orphaned call
(archive/peer/2026-09-05-com-run-hang-after-killed-client.md). Live alternatives from NI sources:
a hidden/owned modal (the first hang tonight WAS a modal Find dialog), the previous client's VI
still running, root-loop busy (menus/mouse activity delay `Run`), or the delay sitting in
`GetVIReference`/another call misattributed to `Run`.

Practical rules: (1) never force-kill a python COM client that may be inside a call; let it finish
or use `VI.Abort()` on the running VI first; (2) an alive check must run a real VI, not just
`Application.Version` — `bench_prep.com_alive` runs `exec_state` in a child process with a 60 s
limit and restarts LabVIEW on timeout; (3) instrument per-call timing (GetVIReference / control
sets / Run entry / return) before theorising about which call blocked.

**Postscript (2026-09-05 11:30):** the "COM hang" pattern above was mostly *not* LabVIEW: the
benchmark cells' transcripts show two Haiku cells force-restarting LabVIEW mid-run and three cells
killing the benchmark driver, all after the project PostToolUse hook (`lv_stallcheck.ps1`) — which
runs inside spawned `claude -p` sessions too — told them an idle python was a "stalled LabVIEW
client". Lesson: an advisory hook is an instruction to whatever model reads it; gate it on an env
var when spawning subordinate sessions, and read the subordinate transcripts
(`~/.claude/projects/<project>/<session>.jsonl`) before theorising about the tool under test.

**Resolved (2026-09-05 12:5x, H5 — four predictions matched, reproducible):** the residual
no-dialog `Run` hangs are caused by **`OpenFrontPanel(activate=True)` followed by an lv_gui
`focus` (Alt tap / SetForegroundWindow / Esc)**: the next COM Run blocks until a mouse click
lands on the diagram (H5a hang 45 s → one canvas click → 0.02 s; repeatable; no hang without the
OpenFrontPanel step). Rules: (1) never call `open_panel` on a VI whose panel is already open —
check the window list first; (2) after any programmatic activation, click empty canvas before
the next COM call (lvclick.focus_bd does this); (3) prefer `OpenFrontPanel(activate=False)`
when the panel only needs to be loaded (see H6 in the same log). The 180 s / 45 s figures are
gscript's own watchdog. Earlier "cells killed the driver" explains the driver deaths, this
explains the hangs — two different failures that overlapped in time.


## Handles and responsiveness — measured 2026-09-06

A fresh LabVIEW 2026 holds ~31,500 kernel handles within a minute of starting; do not read that
number as a leak. `tools/bench/handle_audit.py` on a fresh instance: 20 reporter runs +29, a child
client with clean exit −4, 10 open/revert/close +7, 10 drop_subvi+revert +51, a client killed
mid-work −2, 20 GUI queries +1 — and the count fell back to baseline when the audit process exited.
Judge growth relative to baseline (bench_prep restarts above HANDLE_LIMIT). The metric behind
"(응답 없음)" is message latency: `lv_gui.ps1 -Action ping` (SendMessageTimeout WM_NULL per window;
0 ms when healthy, "HUNG" when the UI loop is stalled — e.g. the H5 state after a programmatic
activation + Alt tap, released by a click). Reference hygiene stays mandatory (CLAUDE.md §3), but its
verification is this measurement, repeated whenever a new op joins the fleet.

## Keystone ops (2026-09-06) — nodes without clicks

`gscript.build_invoke(target, "VI Server:<Class>", "<method Unique ID>", (x, y))`,
`gscript.build_property(target, "VI Server:<Class>", [(prop_id, is_write), ...], (x, y))`,
`gscript.delete_object(target, cls, index)`. IDs: `docs/vi-server-ids.json` (labviewwiki; the
erdosmiller creators call Set Method / Set Properties[] with AllowAlternateNames=FALSE). Rules learned
building them: the creator's `reference` must stay UNWIRED (a valid reference makes the library write
the bare class name and fail silently); a GObject wire into a Generic-class node is accepted and
re-types the node; deleting a node's dangling wires by Ctrl+B also removes a wire whose other sinks
are gone — after that the source is free and `wire()` can attach a fresh wire without a branch.

## A replaced op file is not reloaded while the old VI is in memory (2026-09-06)

Copying a new `.vi` over an op that LabVIEW still holds in memory (panel open, or referenced by a live
COM client) changes nothing observable: `GetVIReference` returns the loaded instance, so runs and reporter
reads describe the OLD diagram (a deleted node kept appearing in `report()`, and its error dialog kept
popping). Unload first — `CloseFrontPanel` and drop cached references (new Python process) — then use
the file. Symptom to recognise: a fresh copy of the file behaves differently from the 'same' VI by path.

## The typed-reference ladder — class-specific nodes with no class constant and no GUI (2026-09-06)

Every class-specific Property/Invoke node needs a wire of that class, and the only scripted downcast
(`To More Specific Class` + class constant) cannot be retyped by script. The way out is to never downcast:
start from the one typed reference every op already has (Open VI Reference → VI) and walk DOWN through
properties whose outputs are already typed:

    VI ──Block Diagram (23C, output 'Diagram')──▶ Diagram ──Nodes[] (6375809)──▶ Node[] ──Index Array──▶ Node
       ──Terminals[] (6359000, output 'Terms[]')──▶ Terminal[] ──Index Array──▶ Terminal
       ──▶ Terminal.Create Control (6349C01) / Create Indicator (6349C02) / Connect Wire (6349C03, `Wire Source`)
    Control (Create Control's output) ──Label (6332005)──▶ Text ──Text (632D800)──▶ the control's label string

Build it with erdosmiller `Create Property Node.vi` / `Create Invoke Node.vi` (class string
`VI Server:<Class>`, Unique-ID strings, `reference` UNWIRED) and `Create Index Array.vi` (its `Diagram in` is
required; `array` accepts a Generic ref but errors on most terminals — leave the node unwired and wire it by
name afterwards). Property-node OUTPUT terminals carry the property's SHORT name (`Diagram`, `Terms[]`).
Facts that bit: `Nodes[]` is CREATION order (uids are reused, so uid rank is wrong); a one-property PN's
Terminals[] = reference, reference out, error in, error out, output; an Index Array's = array, element,
index; Connect Wire on an already-wired sink re-routes and breaks the VI (branching a wired SOURCE is fine);
a replaced op file is not reloaded while the old VI is in memory. Deleting a node leaves its wires as
deletable Wire objects (no Ctrl+B needed) — but identify them by uid, not by bounding-box position.

## Operating rules learned the hard way (2026-09-07 night)

- **Never close LabVIEW's startup window from a script.** Right after launch, window enumeration reports a small
  untitled "modal" — it is LabVIEW's own startup child. Posting WM_CLOSE to it leaves the root loop in a state
  where every later `OpenFrontPanel` / `Run` blocks 60–180 s with no dialog. Wait ~45 s instead.
- **A COM client killed mid-`Run` leaves the (non-reentrant) op VI reserved**; every later Run of that op waits
  forever. After any deadline kill, restart LabVIEW before the next batch.
- **Node.Label / Node.Style reads crash LabVIEW 2026** on VIs that contain `To More Specific Class` + a VI Server
  class constant (RPC server vanishes in ~8 s). Read node identity as GObject.UID and take class/position from
  Traverse for GObjects instead.
- **Load a copied VI through the op (Open VI Reference inside LabVIEW) before `OpenFrontPanel` from COM**;
  open-first hung on OpBuildInvoke-lineage copies while report-then-open took 0.1 s.
- **Ops that keep an erdosmiller creator (Create Invoke Node.vi) drop one junk node on the TARGET per run** and the
  node refuses `Delete`; empty class/ID strings or an injected error do not stop it. Purge with
  `new_since(target,"Invoke")` + delete + Remove Bad Wires (VI method 410, scriptable) after every use.
- **Terminal.Connect Wire across a structure border creates the tunnel** (non-indexed); flip it with
  `LoopTunnel.IndexMode` afterwards. On an already-wired sink it re-routes and breaks the VI — only wire unwired sinks.
