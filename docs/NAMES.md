---
type: reference
status: current
date: 2026-09-15
tags: [docs, vi-scripting]
---

# Verified name registry — the exact strings the scripting APIs accept

Every name below was **verified on this machine** (probe, wire success, or byte-level extraction).
The APIs are string-keyed and fail silently or with 5001 on any mismatch; newlines and trailing
spaces are REAL and must be reproduced exactly. `\n` marks a real linefeed. Add new names the
moment they are verified; never guess from this file's absences.

## Track 1 of N bds xyz-kernel-reentrant.vi (the per-bead kernel)

| terminal | direction | type |
|---|---|---|
| `Image` | in | IMAQ image refnum |
| `Calibration cluster 1` | in | cluster |
| `cross size` | in | I32 |
| `starting x 1` | in | DBL |
| `starting y 1` | in | DBL |
| `Bead 1 is good? in` | in | bool |
| `cosine window\nfor hilbert` | in | DBL array (whole-array ⇒ NON-indexed tunnel) |
| `real-space\ncosine window` | in | DBL array (whole-array ⇒ NON-indexed tunnel) |
| `X pos 1` / `Y pos 1` / `Z pos 1` | out | DBL |
| `Bead 1 is good? out` | out | bool |
| `bead 1 z position\nas a cal image index` | out | DBL |
| `Index of closest\ncal image slice, bead 1` | out | I32 (→ `pos in cal image out` element) |

## Four-fold pane / PARALLEL_kernel_v3.vi front panel

| control/indicator | notes |
|---|---|
| `Image In` | capital I in "In" |
| `x,y,z array`, `x,y,z array out` | flat DBL array, bead k = 3k,3k+1,3k+2 |
| `Array of cal clusters` | |
| `cross size` | |
| `Bead is good? array in`, `Bead is good? array out` | |
| `pos in cal image in`, `pos in cal image out` | I32 array |
| `Cosine bandpass\nfor Hilbert ` | **newline AND trailing space** |
| `Real-space cosine window` | single line |
| `4 pack remainder`, `# of bead 4 packs` | legacy pack inputs (dead in v3's new path) |

## Library VIs (Erdos Miller LV-Scripting)

| VI | terminals confirmed |
|---|---|
| `Set Name.vi` | `Type in`(refnum, in), `Type out`, `Name`, error pair. Writes a property literally called `Name` — NOT the owned label; useless for move/delete-by-label. |
| `Get Controls.vi` | `Diagram in/out`, `Control Names`, `Control Terminals` |
| `Wire Inputs.vi` | `Names`, `Inputs`(refnum array), `Node in`, error pair. Missing dest name → 5001; already-wired source → silent BRANCH (Wire count unchanged) |
| `Wire Indicators.vi` | `Outputs`(refnum array), `Indicator Names`; source must already be wired |
| `Exit For Loop.vi` | in: `Diagram in`, `Outputs`, `Shift Registers`, `Stop Condition`, `Conditional Terminals`, `Loop Terminal Types`; **out: `Outputs` = OUTER TERMINAL refnums of created tunnels** (the fleet's tunnel-access primitive) |
| `Create Property Node.vi` | `Diagram in`, `Properties`(array of {`ID String`,`Is Write?`} — COM needs `gscript.cluster_array`), `reference` (MUST be wired for class context, else 1077), `error in`[11]; `Class Name` NOT on pane |

## Primitives (named-terminal wiring works on primitives — one verified name each)

| node | class | terminals |
|---|---|---|
| Decimate 1D Array | `Unbundler` | in `array`; outputs unnamed (wire by GUI/tunnel) |
| Interleave 1D Arrays | (GrowableFunction family) | inputs/outputs unnamed — wired by GUI |
| To More Specific Class | `Function` | `reference`, `specific class reference`, `error in`/`error out` |

## VI Server class names that surprise

`Decimate 1D Array` traverses as **`Unbundler`**; a For Loop's `N` terminal reports as **`Tunnel`**;
data tunnels are **`LoopTunnel`**; `Diagram` class path in the picker is
`Generic ▸ GObject ▸ AbstractDiagram ▸ Diagram ▸ Diagram`. `Interleaver` is NOT a valid class name
(error 1092).

## OpSetIndexMode_v0.vi (fleet, built 2026-08-31)

Controls: `vi path`, `vi path 2` (set = vi path; silences inherited orphan), `Class Name`
(= `LoopTunnel`), `index` (tunnel traverse index), `index 2` (**IndexMode value: 0 = regular /
non-indexed, 1 = auto-indexed; U32, only 0|1 documented**). Property-node write terminal name for
Wire Inputs: **`IndexMode`** (no space). LoopTunnel property-menu also confirms scripting
properties: `Condition Terminal`, `Index Mode`, `Is Conditional?`, `Inside Terminals[]`,
`Outside Terminal`.

## Fixture-recording recon (Min_Track N beads V6_ParallelLoop.vi working copy, 2026-09-01)

### get buff image-lost frames.vi — the acquisition node (found via Ctrl+F Objects → VIs by Name)
Pane (Context Help with scripting indices): IN `Session In`[0], `Image In`[5],
`Buffer to extract`[7], `error in`[11]; OUT `Session Out`[4], **`Image Out`[6]**,
`Missed frames?`[8], **`current image number`[10]** (авторитет frame index — camera buffer number),
`error out`[15]. Reentrant preallocated clone, **Time Critical priority**.

### IMAQ Write TIFF File 2 (LVAddons)
Load path (NOTE: **no `.vi` extension inside the LLB**):
`C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision\Files.llb\IMAQ Write TIFF File 2`
Pane per Context Help with scripting indices (2026-09-03, CORRECTS the earlier recon): IN
`Color Palette`[7], `Image`[11], `File Path`[10], **`TIFF Options`[9]** (compression etc. — exists
after all), `error in (no error)`[8]; OUT **`Image Out (duplicate)`[3]** (a passthrough DOES exist),
`error out`[0]. Reentrant, shared clone. In the fixture both `TIFF Options` (default = no
compression) and `Image Out` are left unwired.

### Navigation that works on a huge diagram
Ctrl+F → Objects → Select Object ▸ **VIs by Name...** → type-ahead → OK → Find: LabVIEW scrolls to
and SELECTS the instance. Beats scrollbar hunting by an order of magnitude.

### Frame-number semantics (user, 2026-09-01)
The `.tra` frame number is **`current image number` − the FIRST image number** (captured at run
start). Camera buffer numbers increment even when acquisition drops a frame, so lost frames appear
as GAPS in the frame numbering — this is deliberate and diagnostic. **The fixture image filename
must branch the EXISTING subtraction output wire** (the exact value written to `.tra`), never
recompute from `current image number` or loop `i`; that makes image↔tra alignment definitional,
gaps included. Recon target: the subtract node downstream of `current image number`[10], upstream
of the trace assembly.

### save trace.vi pane (verified by probe)
IN: **`frame index`** (I32 — arrives ALREADY COMPUTED: the current−first subtraction lives in the
MAIN while loop, not in this subVI; per the user it also feeds array-indexing/append nodes in the
trace assembly), `current frame data array in`, `total data array in`, `cal cluster path`,
`saved file refnum`(?), two-line labels not yet byte-verified: `base path/filename`,
`file # to append`. OUT: `total data array out`, `selected path` (the actual .tra path — but only
valid AFTER the node runs; do NOT use it to path the TIFF, that would order the write after
analysis), `file number to append out`, `file progress`, `file size`, `error out`.

### Main VI front panel path controls (verified)
**`Track File Path`**, **`Cal File Path`** — path controls; the fixture directory =
Strip Path(`Track File Path`), branchable by `wire_control`.


## Fixture wiring — names VERIFIED by successful wire() calls (2026-09-01)

| node (uid) | verified terminals |
|---|---|
| Subtract uid 5119 (Function; sits at (4641,1692), beside 'Save trace') | out `x-y` — THE frame-index source (current−first) |
| Format Into String uid 22703 (class `FormatScanString`) | in `input 1`, out `resulting string`; `format string` still needs its constant |
| Build Path uid 23020 (Function) | in `base path`, `name or relative path`; out `appended path` |
| Strip Path uid 23175 (Function) | in `path` (unwired yet); out `stripped path` |
| IMAQ Write TIFF File 2 uid 22700 (SubVI i26) | `Image`, `File Path`, `error in (no error)` all wired |
| get buff image-lost frames uid 6810 (SubVI i42) | `Image Out` and `error out` BRANCH-wired to TIFF |

`Track File Path` (top-level Path control, ID=91 in VI strings): Get Controls reports
"Control Track File Path not found" for src diagrams 0–59 — the control's TERMINAL lives in some
deeper subdiagram (VI has 170 Diagrams); sweep of 60–169 was running at write time.
wire_control gained `src_diagram_index` for this.

Main working copy saved 2026-09-01 11:35 as 299,205 B (2026-format resave shrink — expected).


## Fixture build completion notes (2026-09-01 12:08)

- Format-string constant created via node right-click **Edit Format String...** dialog (its
  "Corresponding format string" box is editable free text; OK creates+wires the constant). This
  beats terminal-targeted Create>Constant on a growable node - terminal rows are ~6 px apart.
- Strip Path `path` fed by a **GUI wire branch**: start the drag ON the Strip Path `path` terminal
  (CH-verified snap), END the click on the existing path wire - reverse direction connected on the
  first try after wire->terminal failed twice.
- `Track File Path` control is NOT reachable by Get Controls from ANY of the VI's 170 diagrams
  (likely: Get Controls only lists connector-pane/pane-root controls). wire_control has a
  `src_diagram_index` parameter now; for non-pane controls use the GUI branch of their wire.
- Kernel image access audit: both sub-kernels touch the image ONLY via `Omars IMAQ
  ImageToArray.vi` (read-only) - basis for skipping the error series splice.


## FP object creation by script — MACHINE-CONFIRMED 2026-09-04

`OpFP_v0.vi` (claudeDev; copy of OpWireInd_v0 + Index Array + Invoke Node + Property Node):
`Get Outputs`.`Outputs` -> Index Array `element` -> Invoke Node (auto-typed **Term** from the wire)
method **`Create Indicator`**, return terminal name **`Create Indicator`** (Control Refnum) ->
Property Node (auto-typed **Ctl**) item `Position`. Run against `FPTARGET_v0.vi` with
Class Name=SubVI, index=0, Names=['error out']: target ControlTerminal 9 -> 10 and a new FP
indicator "error out 2" of the correct error-cluster type appeared. Wiring names verified by
successful `gscript.wire` calls: IndexArray out `element`, Invoke in `reference`, Invoke out
`Create Indicator`, Property in `reference`.

Control-class property picker (seen on the PN): Position >(All Elements/Left/Top), Indicator,
Label >, Caption >, Bounds >(read-only), Visible, Disabled, Value, Description, Tip Strip,
Key Focus, Blinking, Locked, Selected, Owning Pane, Terminal >, Typedef >, Style ID, UID ...

GUI notes: LabVIEW popup SUBMENUS open only on real cursor motion (hover sweep of several
`move` steps); arrow keys close them. Clicking the node's Method/Property FIELD opens the
chooser directly, more reliable than the right-click menu's Select Method submenu.

## Input terminals are invisible to `Get Outputs` (2026-09-06)

`OpFP_v0` with `Names=['Properties']` on erdosmiller `Create Property Node.vi` (an INPUT) raised
**error 1055 "Object reference is invalid" at the Invoke Node**: `Get Outputs.vi` resolves OUTPUT
terminal names only, so the Invoke received an invalid ref — the test never reached `Create
Indicator`. Input-terminal refs need `Get Inputs`-style lookup (erdosmiller `Wire Inputs.vi` resolves
them internally) before any Terminal method (Create Control / Create Constant) can be scripted.

## erdosmiller creators — facts settled 2026-09-06 (Create Invoke Node.vi read + codex)

- `Class Name` IS on the connector pane of `Create Invoke Node.vi` (bottom-centre string terminal;
  wire-by-name accepted). It is written verbatim to the new node's **Method Class Name**, so the
  string must be `VI Server:<Class>` — `VI Server:Diagram`, `VI Server:Terminal`, `VI Server:VI`,
  `VI Server:Control` (no inheritance path). A bare `Diagram` fails SILENTLY: the library VI has
  automatic error handling off and its `error out` was unwired → node stays `App`, no method.
- `ID String` goes to `Invoke.Set Method` with **Allow Alternate Names = FALSE** → it must be the
  method's Unique ID, e.g. Terminal.Create Indicator `6349C02`, Terminal.Connect Wire `6349C03`.
  Display names ("Connect Wire") are rejected. Class/method inventories: ClassSpecifierConstant
  `All Types[]`, Invoke `All Supported Methods` (both readable — reporter extension to do).
- The created node's class comes from that string, NOT from the `reference` wire type; the
  reference is only wired into the node afterwards (erdosmiller wires "reference" by name), so a
  reference of a different class than `Class Name` makes a broken wire on the target.
- Pane order on the icon (LabVIEW 2026): left edge top→bottom `Diagram in`, `reference`,
  `Inputs`, `error in (no error)`; top `ID String` (left), `location (0, 0)` (centre); bottom-centre
  `Class Name`; right edge `Diagram out`(?), `reference out`, `Outputs`, `error out` (bottom).
- **`reference` must be UNWIRED** for the string-typed path: a valid reference makes the creator
  write the referenced object's bare class name → silent failure → `App`. Verified 2026-09-06
  (t6/t7 with reference wired: App; t8 without: Term / Connect Wire).
- OpBuildInvoke_v0 controls: `vi path`, `Class Name`(="Diagram", for the diagram lookup),
  `index`, `location (0, 0)`, `Class Name 3` (node class, "VI Server:…"), `Class Name 2` (method
  Unique ID), `vi path 2` (leave ""). Known IDs: Terminal.Create Indicator 6349C02,
  Terminal.Connect Wire 6349C03.

## VI Server Unique IDs -> docs/vi-server-ids.json (2026-09-06)

Property/method Unique ID strings used by the keystone ops (Set Method / Set Properties[] with AllowAlternateNames=FALSE). Notable: Terminal.Create Control 6349C01, Create Constant 6349C00, Generic.Delete 6327400, GObject.Move 632A400, Property.All Supported Properties 636F80E, Invoke.All Supported Methods 637040D, GObject.Position 632A800.

## Property-node OUTPUT terminal names = the property's SHORT name (verified 2026-09-06)

`wire()`/Get Outputs finds a Property Node's output by the short name shown on the node, not the long
name: VI `Block Diagram` (23C) → **`Diagram`**; Node `Terminals[]` (6359000) → **`Terms[]`**; Terminal `Connected
Wire` (634A000) → **`Wire`**; Constant `Terminal` (634AC04) → `Terminal`; DigitalNumericConstant `Numeric Text`
(634D007) → **`NumText`**; AbstractDiagram
`Nodes[]` (6375809) → `Nodes[]`. The long name raises error 5001. Short names are on each labviewwiki
property page ("Short Name"). PN input is `reference`; Invoke input is `reference`; Invoke error terminals
`error in (no error)` / `error out`.

## Node.Terminals[] order (verified by creating indicators, 2026-09-06)

- Property Node with ONE property: 0 `reference`, 1 `reference out`, 2 `error in (no error)`, 3 `error out`,
  4 the property output (its short name, e.g. `Text`).
- Index Array (1 index): 0 `array`, 1 `element`, 2 `index` (labels reported by OpCreateControl_v1).
- Traverse for GObjects.vi: terminal 2 = **`References`** output (the only source that made a fresh Index Array
  legal). ⚠️ This line read "`GObject Refs`" until 2026-09-19 and **contradicted `:741` of this same file**, which
  lists `References` for the same node and index — raised as `contradicted` by
  `archive/peer/2026-09-19-priorart-s0-closeref.md` A3(ii) ("one of these is wrong and a by-name wire against the
  wrong one fails"). SETTLED BY READING THE MACHINE, not by choosing a document:
  `tools/bench/s0_terminal_names.log` (read-only, 6/6, rc=0) prints node #124's twelve terminals on BOTH
  `OpReport_v3.vi` and `OpWireSource_v5.vi`, byte-identical lists, sources
  `['error out', '# of Refs', 'References', 'dup VI Refnum']`. `:741` was right. There is no terminal named
  `GObject Refs` on this node.
- **`Close Reference`** (the Application Control primitive; donor copy = Function **#157** in
  `KernelBuilder_v1.vi`) has exactly THREE terminals — 0 `error out` (source), 1 `error in (no error)` (sink),
  2 **`reference`** (sink, the refnum input). Measured 2026-09-19, `tools/bench/s0_terminal_names.log`; no
  document in this project recorded them before. ⚠️ `archive/WORKLOG.md:84-86` records that wiring THIS input
  "defeated four wiring attempts" by hand, which is why `OpSubVI_v0.vi` ships without the node
  (`docs/REFERENCES.md:126`).
- `Terminal.Connect Wire`: invoke on the SINK terminal; `Wire Source` = source Terminal (GObject refnum). A wired
  source is branched; a wired sink is re-routed (breaks the VI) — wire unwired sinks only.
- `Terminal.Create Control` / `Create Indicator` name the new front-panel object after the TERMINAL NAME
  (duplicates get " 2", " 3"); OpCreateControl_v1 reports that label on its own `Text` indicator.
- **`Node.Label` 6359001 → `Text.Text` 632D800 reads HEADLESS, panel closed, for every node class of the main VI**
  (2026-09-14, `OpNodeLabels_v0` / `gscript.node_labels`, 626 nodes over 170 diagrams, no crash, handles flat): an
  IMPLICIT property node's label = its bound panel object's label (88/88 matched the panel), a subVI node's label =
  its VI file name, a primitive's = its type name (`Index Array`, `Stacked Sequence Structure`, `Property Node`).
  The LabVIEW-Wiki "must have been displayed once" caveat did not bite on a VI saved by a human. The 2026-09-07
  crash (spec §30) therefore points at `Node.Style` or at TMSC/class-constant VIs, not at `Label` itself.
- Loop / ForLoop property IDs (LabVIEW Wiki, 2026-09-14; **not yet verified on this machine** — no Loop-typed ref
  yet): `Loop` class 16405: `Loop Counter` 6361400, `Diagram` 6361401, `Shift Registers[]` 6361402, method
  `Add Shift Register` 6361000. `ForLoop` 16434: `Loop Count` 6362000 (→ Tunnel), `Has Conditional Terminal?` 6362001,
  `Loop End Ref` 6362002, `Is Parallelism Enabled?` 6362004, `Number of Static Parallel Instances` 6362005,
  `Dynamic Parallel Instances Tunnel` 6362006, `Chunk Size Tunnel` 6362008, `Parallel Schedule` 6362009. `Property`
  class: `Linked Control` 636F806; `Local`: `Control` 6355403, `Control Name` 6355400. `WhileLoop`: `Loop End Ref`
  **6362C00 — ✅ VERIFIED ON THE MACHINE 2026-09-17**, data-terminal short name **`LpEndRef`**, returns a
  `Terminal` reference that `Terminal.Is Source?` 634A003 and `Terminal.Connected Wire` 634A000 accept without a
  cast (`OpLoopEndRef_v0`, `tools/bench/build_oploopendref_v0.log`, census not "no 1077"). Shift registers: `LeftShiftRegister` class 16442, `RightShiftRegister` 16399 — both derive from `Tunnel`
  (so `Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 apply); `LeftShiftRegister.Right Shift Register`
  6374C00 pairs left → right; stacked left elements via method 6374800. **Verified on the machine 15:1x** (`OpLoopCast_v0`,
  `test_oploopcast.log`): `ForLoop.Loop Count` short name `LpCount`; `Loop.Shift Registers[]` returns the loop's
  registers (counts 0–4 over the main VI's 17 For loops); NI's example short names `LpCounter`, `HasConditionalTerm`,
  `LpEndRef`, `Diagram`.
- **Overwriting a VI that is still loaded blocks the next `OpenFrontPanel` behind an UNTITLED modal** ("The VI … has
  changed on disk since last saved or loaded by LabVIEW … Revert / Cancel", 2026-09-14 19:39,
  `tools/bench/dialog_1939_crop.png`): bgrun's dialog scan reported "no dialog" while `lv_gui.ps1 -Action dialogs`
  saw it (`ENABLED|…|808,436,1091,625|` with an empty title). **The trap that reproduced it on a FRESH instance
  (19:46): `close_panel(path)` / any `GetVIReference(path)` LOADS the file — a recipe that "closes the old copy" and
  then overwrites the file has just created the memory-vs-disk conflict itself.** Rules: never reference an output
  file over COM before writing it (only `os.remove` + copy, on an instance where nothing of that name is loaded);
  close every panel on every exit path (`finally`); after a deadline kill run `lv_gui -Action dialogs` before
  anything else. Recovery = LabVIEW restart (standing permission).
- **Tool scope: `connect_terminals`, `connect_ctl`, `create_control`, `create_indicator` address the TOP-LEVEL diagram's
  `Nodes[]` only** (an index measured inside a case frame or loop body draws the 8-s out-of-range dialog and does
  nothing; `build_setcommand_signed.log` runs 1–2). Inside a structure use `wire(target, 'Function', traverse_i, name, …)`,
  `wire_indicators(… node_class='Function', diagram_index=frame)`, `wire_control(…)` — Traverse-class indices span all
  diagrams. Terminal names of the driver's primitives (read by `node_terms`): String Subset `substring`/`string`,
  Hexadecimal String To Number `number`/`string`/`default (0uL)`, Type Cast `x`/`type`/`*(type *) &x`, Multiply `x`/`y`/`x*y`.
- **erdosmiller `Create For Loop.vi` with `Number of Static Parallel Instances` = 4 sets BOTH `Is Parallelism
  Enabled?` 6362004 = TRUE and `Number of Static Parallel Instances` 6362005 = 4** (measured 18:1x on
  PARALLEL_kernel_v3.vi, `test_oploopcast_v1.log`); NI documents the two properties separately, so any other builder
  must write 6362004 explicitly. The original main VI: 0 of 17 For loops parallel; uid 22786 stores P=12 disabled.
- `Loop.Shift Registers[]` short terminal name on this machine: **`ShiftRegs[]`**; `Tunnel.Outside Terminal` → `Outer Term`,
  `Tunnel.Inside Terminals[]` → `InsideTerms[]`, `ForLoop.Loop Count` → `LpCount`. An op that carries two Index Arrays
  with wired `index` inputs (the donor's Traverse selector and a later one) must be told apart by the `array` wire
  (`build_opshiftregs_v1.log` run 1 wired the wrong one).
- **`Loop.Shift Registers[]` 6361402 enumerates the RIGHT registers** (measured 15:3x, `test_opshiftregs.log`: all
  14 elements of the frame loop read `GObject.Class Name` = `RightShiftRegister`; each has ONE inside terminal
  (sink, the body-side feed) and an outside terminal (source, the final value; wired on 4 of 14). A Tunnel-class
  property node compiles on the Index-Array element (`Outside Terminal` short name `Outer Term`, `Inside Terminals[]`
  → `InsideTerms[]`). The inside terminal's `Name` = the register's label (`x,y,z array out`, `error out`, …).
  `RightShiftRegister` 16399 (parent Tunnel): `Left Registers[]` 6357800 (array: stacked lefts),
  `Is An Error Register` 6357801 (LabVIEW Wiki, not yet verified on the machine).
- **Traverse `Diagram` indices are NOT stable across a structure creation** (2026-09-14 15:2x,
  `build_opshiftregs_v0.log`): a second For loop's body appeared at index 1, shifting every later diagram, so "the
  index not in the before-set" pointed at the OLD loop's body. Identify a new diagram by its UID (`report_all` rows)
  and confirm membership (`node_labels(op, body)` lists the node) before wiring into it.
- **THE CAST SEED, GUI-free (2026-09-14 15:0x, `build_oploopcast_v0.log`):** `To More Specific Class`'s `target class`
  accepts ANY wire of the target type (NI doc; codex). A typed refnum CONTROL is obtained by `Terminal.Create Control`
  on the `reference` INPUT of a property node already configured to that class — NI's shipped examples
  `examples\Application Control\VI Scripting\Structures\VI Scripting with Structures - <X>.vi` hold one class constant
  wired to such nodes (For Loop: uid 183 → five ForLoop nodes over one wire). Recipe: scratch copy → delete that wire →
  `create_control(scratch, node, 0)` (label `reference`) → delete the other nodes so the scratch stays runnable (a
  broken VI cannot be COM-saved) → `copy_into(scratch, 'reference', op)` → delete the op's constant wire →
  `wire_control(['reference'] → TMSC 'target class')`. A seed casts only its own class: a ForLoop seed on a WhileLoop
  ref → error 1055 downstream (`test_oploopcast.log` T3). `Create For Loop.vi` has NO loop-typed output (its terminals:
  Diagram in/out, Inputs, Shift Registers, Loop Counter, Loop Count Terminal, …).
- **An EMPTY For Loop's `Node.Terminals[]` = ONE entry, `Name` = '' (empty), sink, unwired = the count tunnel's
  outside terminal (N)** (2026-09-14, `build_harness_copyloop2.log`; peer: the typed route is `ForLoop:Loop Count` →
  `Tunnel:Outside Terminal`, which needs a ForLoop-class reference — same cast gap as shift registers). Wiring N by
  script: `connect_terminals(target, loop_node, 0, src_node, src_term)` with an I32 source, then verify the SAME wire
  uid on both terminals (`node_terms`) and ExecState 1. `i` is not listed (inner terminal). **`Create For Loop`'s
  `Control Names` does NOT wire an existing front-panel control into the new loop** (measured: loop created, 0 tunnels,
  control still unwired — `build_harness_copyloop.log`).

## Junk Invoke nodes break the target VI (2026-09-08 10:3x)

Every op that reaches into a target through the Traverse ladder (OpNetInfo / net_map, OpCreateControl / create_control,
OpConnect, OpSetLabel, OpMoveOut) leaves one unwired Invoke node on the target's diagram per run; an Invoke node with an
unwired `reference` makes the VI **non-executable even when every wire is good** (Remove Bad Wires reports nothing).
Three OpBuildBA recipe runs failed this way. Rule for every recipe: `inv0 = g.uids(target, "Invoke")` right after opening
the target, and purge `g.new_since(target, "Invoke", inv0)` (delete_object) before every ExecState check and before saving.

## Node class census of the main VI (`report_all(main, "Node")` → `class` column, 2026-09-14)

Function 161 · Property 106 · SubVI 93 · IndexArray 47 · GrowableFunction 40 · CaseStructure 37 · **ControlReferenceConstant 21**
· BuildArray 19 · ForLoop 17 · Bundler 12 · NamedUnbundler 12 · Comparison 11 · Local 8 · Global 7 · PolymorphicSubVI 5 ·
Sequence 4 · CompoundArithmetic 4 · Unbundler 3 · WhileLoop 3 · FlattenString 3 · InRangeAndCoerce 3 · EventStructure 2 ·
FormatScanString 2 · NamedBundler 2 · ArrayToCluster 2 · Invoke 1 · ReadWriteFile 1 (= 626). A **`ControlReferenceConstant`**
is a single-terminal SOURCE node named after its panel object (like a global's field / a local's control) — it is how
the "bare-terminal" panel objects are reached (through explicit property nodes / event registrations). Class names
that Traverse rejects: `ControlRef`, `ControlReference`, `ControlRefConstant`, `PropertyNode`, `LocalVariable`.

## Traverse class for global-variable nodes = `Global` (measured 2026-09-14, `global_read_control3.log`)

`report_all(vi, "Global")` lists global-variable nodes (`GlobalVariable` → error 1). Direction of a global node =
`Terminal.Is Source?` of its single data terminal (via `gscript.node_terms`): TRUE = READ, FALSE = WRITE — verified on
NI's Network Streams example (two WRITE + one READ `Host Stop` nodes told apart). The terminal's `Name` is the
global's FIELD name (e.g. `Trans position`). `drop_subvi` cannot place a global VI (New VI Object error 1057).

## Junk Invokes land ONLY on an open (editable) target — measured 2026-09-14 12:25 (`walk_junk_probe.log`)

Same scratch, same process, same OpNetInfo_v1: walked **by reference only → 0 junk**; after `open_panel` → **78
junk**. The creator's drop is an edit, and "a target loaded only via GetVIReference declines edits silently"
(08-28 rule) applies to it. So: reads of the main VI (never opened) never received junk — the STATUS line saying the
overnight sweep "poured junk" into it was an inference and is withdrawn; purge is only needed on build targets,
which are always `open_panel`ed. A reader op that must stay junk-free on an open target still needs its creator
deleted (OpSubVIs_v1 / OpNodeTerms_v0 pattern).

## `net_map` purges its own junk now — and the cast-free ladders' terminal names (2026-09-14)

The 09-08 rule above was never applied to `net_map` itself: ONE walk of an 8-node diagram drops ~75-100 junk Invokes
(one per op run: per node AND per terminal), enough on its own to hold the target at ExecState 0 — which is what every
"ladder broke the VI" reading of 09-13/14 actually measured. `net_map` now snapshots Invoke uids before the walk,
deletes what it added and runs Remove Bad Wires, printing `net_map: N nodes walked in X s; J junk Invoke(s) purged in Y s`
(measured 8-11 nodes: walk 1.5-2.0 s, purge 78-101 junk in 5-8 s). Cost trap fixed the same day: `delete_object`'s
before/after `uids()` snapshots used per-object `report()` → an O(J²) purge that hit a 12-min deadline; `uids()` now
uses `report_all` and bulk deletes pass `verify=False` with one snapshot per batch.

Terminal short names read off the machine (probe_castfree5.log), all compile WITHOUT a cast:
- `AbstractDiagram.SubVIs[]` 6375802 → **`SubVIs[]`** (fed from the Nodes[]-node's `reference out`); its elements feed a
  **`VI Server:SubVI`** property node directly: `VI Name` 635E401 → **`VIName`**, `VI Path` 635E403 → **`VIPath`**.
- `Control.Terminal` 6332006 → **`Terminal`** (fed from a Control-class node's `reference out`); it feeds a
  **`VI Server:Terminal`** node directly: `Is Source?` 634A003 → **`IsSource`**, `Connected Wire` 634A000 → **`Wire`**.
- `GObject.UID` 632A813 → `UID` (on any GObject-descendant class node).
- `Wire.Is Broken?` 6371004 → **`Broken?`**; `Terminal.Name` 634A004 → `Name`; `Node.Terminals[]` → `Terms[]`;
  `Panel.Controls[]` → `Controls[]`; `VI.Front Panel` → `Panel`; `Control.Label` → `Label`, `.Indicator` →
  `Indicator`, `.Terminal` → `Terminal`; `Text.Text` → `Text` (all read from walks on 2026-09-14). Rule restated:
  when a walk has already printed a node's terminal names, the recipe must match THOSE strings — a guessed
  variant (`IsBroken`) cost one build run today.

## One COM client at a time (2026-09-09)

Two Python clients running OpFPLabels concurrently (one on NI Vision LLB VIs, one on the import-wizard library) crashed
LabVIEW 2026 with "Fatal Internal Error 0x6AD83CCC objmsg.cpp line 178". Op VIs are non-reentrant and VI Server serialises
badly under two callers: run reads sequentially (chain scripts), never in parallel background jobs.

## OpBuildCase_v1 — Case Structure from control NAMES (built + functionally verified 2026-09-10)

`gscript.build_case(target, location, selector_name, input_names, frame_names)` — supersedes v0 (below, keep for the
history of the 1055 dialog). Controls: `vi path` (+ `vi path 2` = same), `Class Name`="Terminal"/`index`=0 (Traverse
anchor), `location (0, 0)`, **`Control Names`** = [selector control label], **`Control Names 2`** = input control labels
(become input tunnels), **`Frames`** = STRING ARRAY of frame names.

- Diagram: PN `VI.Block Diagram` → `Get Controls.vi` ×2 (`Control Names` / `Control Names 2`); GC1.`Control Terminals` →
  Index Array (`array`; element 0) → creator `Selector`; GC2.`Control Terminals` → creator `Inputs`. Built by
  `tools/recipes/build_opbuildcase_v1.py` (stage 1) + `build_opbuildcase_v1c.py` (stage 2, scratch-then-copy).
- **`Frames` is an array of frame NAMES, one per frame the selector type creates.** A numeric selector yields 2 frames, so
  pass `["0, Default", "1"]` or `["0", "1, Default"]` (both verified). An integer (COM coerces it to a 1-element array),
  `[]`, or any other length raises **error 1302 `Frame Names` inside the library VI** — an 8 s modal dialog no sink of ours
  reaches. (Measured: ints 1/2/3 and [] all → dialog; the two 2-name arrays → 0.1 s, no dialog.)
- Contract (tools/bench/case_v1_test.py on a stripped PARALLEL_kernel_v3 copy, selector `# of bead 4 packs`, inputs
  `x,y,z array` + `Image In`): +1 CaseStructure, Diagrams 1→3, Wires +3 (selector + one per input tunnel), ExecState 1,
  both op error outs empty. Never list the selector control in the inputs too.
- Lessons from stage 2: `OpBuildIA_v0`'s Index Array arrives UNWIRED (spec §24) — wire `array` by name afterwards
  (`g.wire(T,"SubVI",gc,"Control Terminals","IndexArray",ia,"array")` accepted, +1 wire); six "which source terminal"
  attempts were chasing that. `delete_by_label` needs the connector pane (5005) → delete the refnum controls as
  ControlTerminal objects by position and verify with `fp_labels`. Peer review: archive/peer/2026-09-10-opbuildcase-v1-ia-unwired.md.

## Connector pane by script — OpConPane_v0 reads it (built + verified 2026-09-10)

`OpConPane_v0.vi` (tools/recipes/build_opconpane.py, from OpFPLabels_v0): controls `vi path` + `index` (TERMINAL index);
indicators `Text` (the label of the control on that terminal, an error means the terminal is FREE), `Indicator`,
`Number of Connection Terminals`. Chain: `VI.Connector Pane:Reference` **23E** → `ConnectorPane.Controls[]` **239A8403**
(+ `Number of Connection Terminals` **239A8401**) → Index Array → `Control.Label` → `Text.Text`.

- **Property-node output SHORT names, verified by successful wires:** VI.Connector Pane:Reference → **`ConPane`**;
  ConnectorPane.Controls[] → **`Ctrls[]`** (`Controls[]` raises 5001, unlike the Panel class's own `Controls[]`).
- **TRACK_kernel_v1's pane, read 2026-09-10:** 16 terminals (a 5-3-3-5 pattern), 13 assigned, **5, 6 and 10 FREE**.
  0 `Bead is good? array in` · 1 `Image In` · 2 `cross size` · 3 `Bead is good? array out` · 4 `x,y,z array out` ·
  7 `x,y,z array` · 8 `pos in cal image out` · 9 `# of bead 4 packs` · 11 `4 pack remainder` · 12 `Array of cal clusters` ·
  13 `pos in cal image in` · 14 `Real-space cosine window` · 15 `Cosine bandpass\nfor Hilbert `.
- **Never change `Pattern` (239A8400) on a VI that already has callers** — a pattern change clears every assignment and
  breaks the call sites. Assign into a FREE terminal instead.

`OpConPaneAssign_v0.vi` (tools/recipes/build_opconpaneassign.py, also from OpFPLabels_v0, whose
`Front Panel -> Panel.Controls[] -> Index Array[index]` already yields the Control refnum the method wants): controls
`vi path`, `index` (front-panel TABBING position of the control) and `Terminal Index`; method
`ConnectorPane.Assign Control To Terminal` **239A8000**, whose input parameter names wire by name as **`Control`** and
**`Terminal Index`**. Wrappers `gscript.conpane(target)` and `gscript.conpane_assign(target, label, terminal)`.

- **The target's front panel MUST be open before the assignment.** Without `open_panel`, the assign returns a CLEAN error
  cluster, the op stays runnable, and the file comes back byte-identical — the silent-decline rule for VI-Server-only loads,
  costing one full test run to rediscover (2026-09-10). `conpane_assign` opens the panel itself and re-reads the pane to
  prove the assignment landed.
- Applied to TRACK_kernel_v1 on 2026-09-10: `index` → terminal 5, other 13 assignments unchanged, 17,059 → 17,087 B,
  ExecState 1, outputs still bit-identical to the reference.

## Deleting a node upstream of an Index Array silently deletes the wire DOWNSTREAM of it (measured 2026-09-10)

Removing the node that fed `Index Array.array` leaves `element` with an undefined type, so the existing
`element -> next node` wire becomes broken and `Remove Bad Wires` deletes it. The wire count gives no hint (the same three
wires disappear either way) and the VI simply stays at `ExecState 0` with every replacement wire apparently correct — two
build attempts were lost to it. **After replacing a node upstream of an Index Array, re-wire its `element` output too.**
Diagnosis method that found it: `print_net_map(*net_map(...))` on the broken build and on the intact source, then diff the
UNWIRED lists (net_map lists only unwired terminals here, which is exactly what makes the diff readable).

## Never load a VI you are about to overwrite (measured 2026-09-10)

A recipe that starts `close_panel(OP)` (or any `GetVIReference`) and then `shutil.copyfile(SRC, OP)` **loads** the old file
into LabVIEW and then changes it on disk. The next `OpenFrontPanel` raises a modal:

> The VI OpConPane_v0.vi has changed on disk since last saved or loaded by LabVIEW. If you load its block diagram, it will
> probably be inconsistent with the parts of the VI already in memory, resulting in a corrupt VI.  [Revert] [Cancel]

It blocks every COM call until the process is killed — the symptom is `COM OpenFrontPanel did not return within 180s
(no dialog)`, because the watchdog's own dialog probe ran before the modal appeared. Correct pattern: **`os.remove(OP)` then
copy**, never a VI-Server touch of the target first (`build_opconpane.py`, `build_opbuildcase_v1c.py`).

## Timing protocol: never touch a kernel through VI Server before timing it (measured 2026-09-10)

`GetVIReference` + `SetControlValue` on TRACK_kernel_v1 before run_timing made its harness row cost **+9 ms/frame**
(kernel 11-22 ms vs par 1.8-2.3; track_check.log) — the touch loads the subVI's front-panel data space and every call
then refreshes it (the IMAQ image display among the controls). Fresh LabVIEW, kernel untouched: track 1.62 vs par 2.76 ms
(track_time.log). Rule: configure (set values → OpMakeDefault_v0 → save) in one session, **restart**, then time.
`MakeCurValsDefault` is NOT in the ActiveX VirtualInstrument interface (DISP_E_UNKNOWNNAME); a SetControlValue on a
loaded subVI does NOT reach its calls (backend 1 ran the CPU frame). VI method `Default Values:Make Current Default` = ID
**3F3** (labviewwiki VI class; no scripting licence) → OpMakeDefault_v0 (tools/recipes/build_opmakedefault.py).

## Case-structure assembly pattern (TRACK_kernel_v1, measured 2026-09-10, tools/recipes/build_track_kernel_v1.py)

- **Input tunnels:** `wire_control(T, [ctl], "SubVI", i, [term], branch=True)` from a top-level control to a node inside
  frame 1 = **+2 wires** (tunnel + inner wire); the same control to the node in frame 2 = **+1 wire** (LabVIEW REUSES the
  tunnel and wires only its inner terminal). Pass `branch=True` to skip the +1 count check; verify by counts yourself.
- **Output tunnels:** `wire_indicators(T, i, [out], [pane_indicator], node_class="SubVI")` from the node inside a frame to
  the pane indicator = **+2** in the first frame (tunnel + inner wire; ExecState 0 until the other frame is wired — an output
  tunnel unwired in one case breaks the VI, so its ExecState raise is expected there) and **+1** in the second frame
  (tunnel reused), ExecState back to 1. Do the two frames back-to-back per output.
- **`create_indicator`/`create_control` reach the TOP-LEVEL `Nodes[]` ONLY, and on the main VI that list is EMPTY** (cycle 56, 2026-09-20: `node_info(max_n=40)` = `[]`; all 114 pre-existing `ControlTerminal`s read owner class `Diagram`, not `TopLevelDiagram`) — an index inside a frame or loop body draws the 8-s dialog and does nothing. ✅ **Not a dead end: put a node there first** — `build_index_array` → `owner_of` `('TopLevelDiagram', 536)`, `node_info` 0→1 → `create_indicator(Nodes[0].Terminals[2])` → ControlTerminal 114→115 → `delete_object(IA)` → `ExecState` 1, saved `claudeDev\DIAG_s56_t3_p2_20260920_221901.vi` md5 `cbe9ddd5…`, log `tools/bench/diag_s56_transport3.log`.
  ✅ **Wiring that new terminal to a source on a NESTED diagram IS MEASURED AND IT WORKS** (cycles 57–58, 2026-09-20/21) — `move_in` it onto the nested diagram first, then give `wire_indicators` `diagram_index` = **the LIVE Traverse index of the diagram the INDICATOR's terminal lives on**, never the source's: `tools/gscript.py:1787-1789` feeds `Diagram in` from that argument and it scopes the INDICATOR lookup only. **The ARGUMENT, not the verb, caused all three `error 5001 … Control <label> not found`** (they passed the source's diagram, or `diagram_index=0`); every attempt since, given the indicator's own diagram, returns an EMPTY error column: numeric → `Is Broken?` **False** (`tools/bench/diag_s57_typepair.log:195`, wire 10990, whole-VI `Wire` delta 0), Boolean → `Is Broken?` **False** (`tools/bench/diag_s58_boolwire.log:151-154`, wire 0 → 10799, delta 0). ⚠️ The one raise left is NOT a wiring failure: `tools/bench/diag_s57_ctmove_wire.log:83` wired a NUMERIC indicator to the BOOLEAN `'x .and. y?'` and `wire_indicators` raised on its own post-wiring `ExecState` check (`gscript.py:1794-1797`) — the ordered second pass read `Is Broken?` **True**, i.e. a TYPE mismatch (`Terminal.Create Indicator` 6349C02 takes no type argument, so the indicator inherits its carrier terminal's type). Since the 2026-09-20 repair of the two create wrappers these calls RAISE the dialog text instead of returning `[]` with `exception None`.
- **A new selector control without a node to hang it on:** `build_index_array` (unwired IA) → `create_control` on its
  `index` terminal (label `index`, I32) → delete the IA → the control stays on the pane, unwired, VI runnable.
  It is NOT on the connector pane (no conpane op yet); the backend is chosen through its saved DEFAULT value.
- **Case selector reports as class `Tunnel`** (like a For Loop's N): 10 inputs + 3 outputs + selector = 14 Tunnels.
- Result: 3 Nodes (case + 2 kernels), 40 Wires, 3 Diagrams, ExecState 1, 17,061 B.

## OpBuildCase_v0 (erdosmiller `Create Case Structure.vi`, built 2026-09-09) — SUPERSEDED by v1

Controls: `vi path`, `Class Name`/`index` (the Traverse anchor, as in the other creators), `location (0, 0)`, **`Frames`**
(number of frames — 2 gives the diagram count 1 → 3), **`Selector`** and **`Inputs`** (REFNUM controls).

- **Never SetControlValue on `Selector`.** It is a terminal refnum; writing 0 into it makes the creator call `Connect Wire`
  with an invalid reference → **error 1055 dialog** ("Object reference is invalid", Method Name: Connect Wire) that blocks the
  run. Leave it untouched and wire the selector afterwards. `Inputs` accepts an empty array.
- **Case frames are Diagrams:** after a 2-frame case, `drop_subvi(target, path, diagram_index=1 or 2, ...)` places a node
  INSIDE that frame (index 0 stays the top-level diagram; an out-of-range index raises a dialog).
- **The Selector error is NOT silenced by an error-out indicator** (tried 2026-09-09: an indicator on the op's error out,
  saved, still a modal dialog on every run). The error is raised inside `Create Case Structure.vi` itself. Until the op can
  be given a real Selector terminal refnum, every case-structure creation blocks an unattended run.
- **Wiring INTO a frame creates the tunnel for you:** `wire_control` from a top-level control to a node inside the frame
  succeeds and adds **2** wires (outside→tunnel, tunnel→node), so the usual "+1 wire" check must be relaxed.

## Two index spaces: Nodes[] vs "index within the traversed class" (2026-09-09)

Ops do not agree on what `index` means, and passing the wrong one gives **error 1055 at a To More Specific Class** (an
out-of-range Index Array yields an invalid refnum, which the cast then rejects):

| op / helper | what `index` means |
|---|---|
| `create_control` / `create_indicator` (OpCreateControl/Indicator) | **Nodes[] index** (creation order) |
| `wire_indicators` (OpWireInd), `wire` (OpWire_v1), `wire_control` (OpWireCtl), `report`/`delete_object` | **index within the traversed `Class Name`** (e.g. the 1st CallLibrary = 0) |

Seen 2026-09-09 building GPU_kernel_v1: `wire_indicators(..., Nodes[] index 2, node_class="CallLibrary")` on a diagram with a
single CallLibrary node → 1055; `cls_i("CallLibrary", uid)` = 0 is correct.

## Nodes[] index = CREATION order — never a Traverse("Node") position (2026-09-09)

`OpCreateControl/Indicator` address `Diagram.Nodes[k]`; `k` is the node's creation rank (junk Invokes purged before every
drop keep it stable). The reporter's `report(vi, "Node")` (Traverse for GObjects) lists nodes in a DIFFERENT order — using
its position put a control on the wrong node (`t2` of IMAQ Create came back as `error in (no error)`). Keep a `RANK` dict
(`uid -> count("Node") - 1` at drop / after `build_clfn`), as `tools/recipes/build_harness_gpu2.py` does.

## `gscript.uids()` RETURNS A SET — it has no order, and a traverse index cannot be read out of it (2026-09-15)

```python
def uids(target, cls):
    return {o["uid"] for o in report_all(target, cls)}     # a SET COMPREHENSION
```

Step 0a burned three runs on this. Each run needed the Traverse **index** of a newly created loop body so that
`drop_subvi(target, path, diagram_index, loc)` would place the subVI inside it, and each attempt derived that index
the wrong way:

| attempt | how the index was derived | what happened |
|---|---|---|
| 1, 2 | `count("Diagram") - 1`, i.e. "the newest is last" | the subVI landed on a pre-existing diagram, silently, and a whole-VI SubVI count called it a pass |
| 3 | `list(uids(...)).index(new_uid)` | **set iteration order**, not traverse order. It reported "index 0" and the subVI landed on the harness's existing loop body — which `subvis()` then exposed, because that listing also contained `IMAQ Copy` and `IMAQ GetImageSize` |

An earlier version of this section recorded attempt 3's "the new body's Traverse index is 0" as a measured fact.
**That was wrong** — it was the hash order of a set, and the next run falsified it: attempt 4 measured the same
body (uid 472) at **Traverse index 1**, and `new_since` reported `i=1` independently. The entry is corrected here
rather than deleted, because the mistake is the useful part: there is no rule about where a new diagram lands, and
looking for one is the error.

**Use what already exists instead of deriving an index:**

- **`gscript.new_since(target, cls, before_uid_set)`** — returns the objects created since `before`, from `report()`,
  so each carries its real Traverse index `i` **and** its uid. Its own docstring says it: *"Use this, NOT position
  matching, to identify what a mutating Op just created."*
- **`gscript.loop_diagram(target, loop_pos)`** with `LOOP_DIAGRAM_OFFSET = (10, 22)` — a loop's body reports its
  position at exactly `loop_pos + offset`, measured 2026-08-28 on three loops with a 21x margin to the next
  nearest diagram, so selecting a loop's subdiagram by position is unambiguous here rather than a heuristic.
- And verify arrival by **listing that diagram's contents** (`subvis(target, index)`), never by a whole-VI count.

Two more names resolved the same day, both previously guessed wrong:

Two more names resolved in the same run, both previously guessed wrong:

| fact | value |
|---|---|
| `StrToPath.vi` connector terminals | **`string`** (input) and **`path`** (output) — lowercase. Step 0a run 1 guessed `"String"` and got error 1057 |
| `gscript.while_loop()` return value | a **float — elapsed run time, not a UID**. Run 1's log printed `uid 0.1486…`; that number is seconds |

## IMAQ pixel pointer + NI's CLFN scripting library (read 2026-09-09, tools/bench/labels_chain.log)

- `vision\Basics.llb\IMAQ GetImagePixelPtr`: in `Image`, `Pixel Pointer in`, `X Coordinate`, `Y Coordinate`, `Function`,
  `error in (no error)`; out `Pixel Pointer out`, `LineWidth(Pixels)`, `Pixel Size (Bytes)`, `Transfer Max Size`,
  `Image Border Size`, `error out`. Byte stride = LineWidth × Pixel Size. `IMAQ GetImageSize`: `X Resolution`, `Y Resolution`.
  **`Function` (ring, terminal 7) is REQUIRED** — the VI stays broken until it is wired (a control on it, default value, fixes it;
  found by the required-input probe in tools/recipes/build_harness_gpu2.py, 2026-09-09). `Pixel Pointer in` (t6) is optional.
- NI import-wizard CLFN library `resource\importtools\sharedlib\VI\Block Diagram\Call Library Node\` (all take
  `CallLib Refnum` in / `CallLib Refnum out`, `error in (no error)` / `error out`, and an `operation` ring for read/write):
  `Method\Create.vi` (`diagram`, `position/next to` → `CallLib Refnum out`, `diagram out`), `Attribute\Library Path.vi`
  (`path`/`path out`), `Function Name.vi`, `Calling Convention.vi`, `Reentrant.vi`, `Parameter Info.vi` (`parameter info` /
  `parameter info out`), `Parameter Terminals.vi` (`Terms[]`), `Method\Connect Terminals.vi` (`Terms[]`, `diagram`, `Array`),
  `Method\Create String.vi` (`Position`, `Term Refnum`, `Owner`, `CLN node`). Create.vi returns a TYPED refnum → no TMSC needed.
- Import-wizard FUNCTIONAL GLOBALS `VI\Block Diagram\Attribute\{Function Name, Path, Calling Convention, Reentrant, Parameter Info}.vi`
  + `Call Library Node\Attribute\Function Dec.vi`: inputs `operation` (0 Get / 1 Set) + value (`function name`, `path`, `calling convention`,
  `reentrant`, `parameters info`, `String`); output of Parameter Info.vi = **`parameters info out`**. `Create.vi` applies ALL of them —
  an EMPTY `Parameter Info` crashes LabVIEW, and a library FILE NAME containing a space (`GPU Tracking.dll`) leaves the scripted node
  broken — deploy DLLs for scripted CLFNs under space-free names; and a scripted CLFN's argument INPUT terminals are REQUIRED
  until wired (the VI stays ExecState 0 until every argument input has a control/wire) (docs/gpu-backend.md). Flatten To String primitive: inputs `anything`, outputs `data string`,
  `type string (7.x only)` (populated anyway); Unflatten From String: `binary string`, `type`, `error in` → `value`, `error out`.

## Traversable VI Server class names — confirmed and refuted (2026-09-12)

`g.report(target, cls)` / `g.count()` take a class-name string, and a wrong one fails with **error 109** rather than
anything self-explanatory. Confirmed working on the main VI: `SubVI`, `Property`, `Invoke`, `Node`, `Wire`, `Diagram`,
`Terminal` (5763 of them), `Constant` (301), `DigitalNumericConstant` (180), `NumericConstant` (207),
`StringConstant` (22), `GObject` (10030), `IndexArray`, `CaseStructure`, `WhileLoop`, `ForLoop`, `Sequence`,
`EventStructure`.

**Added 2026-09-16 (cycle 13, `tools/bench/diag_hierarchy_a3.log` part B — all four measured on the main VI):**
`Tunnel` (**468**; a For loop's `N` terminal is one of these, and so is every structure tunnel EXCEPT a flat
sequence's — the owner histogram is `CaseStructure 173 · ForLoop 130 · WhileLoop 91 · Sequence 58 ·
EventStructure 16`, **zero FlatSequence**) · `Structure` (**63**, which is the 84-structure census **minus the 21
FlatSequence**) · `MultiFrameStructure` (**43** = 37 Case + 4 stacked Sequence + 2 Event — **`FlatSequence` is NOT
a `MultiFrameStructure`**). **Refuted, both error 1092:** `SequenceTunnel`, `FlatSequenceTunnel`.
Consistent with these: `build_property('VI Server:FlatSequence', Frames[] 6363801)` is refused with **1077**,
while the same id attaches on `VI Server:MultiFrameStructure`.

### 🟢 FlatSequence has its OWN frame accessors — MEASURED 2026-09-16, ids confirmed on the machine

`FlatSequence` (class id **16459**) does not borrow `MultiFrameStructure`'s properties; it has a parallel pair,
and **both attach** (`tools/bench/diag_flatseq_diagrams_attach.log`, 5 gates pass / 0 fail, 33 s — the census is
the verdict, not the absence of 1077):

| class | property id | data terminal | verdict |
|---|---|---|---|
| `VI Server:FlatSequence` | **`3578BC00`** | **`Diagrams[]`** | **ATTACHED** — the frame **Diagram** references directly |
| `VI Server:FlatSequence` | **`3578BC07`** | **`Frames[]`** | **ATTACHED** |
| `VI Server:FlatSequence` | `6363801` | — | refused, **1077** (the id belongs to `MultiFrameStructure`) |
| `VI Server:MultiFrameStructure` | `6363801` | `Frames[]` | attached (control) |

Found by the peer review of a failed prediction (`archive/peer/2026-09-16-flatseq-frame-unreachable.md`, codex,
ANSWERED 125 s) and then **confirmed against the machine rather than taken on its word**. So "1077 on
`VI Server:FlatSequence`" meant *wrong class for that id*, never *unreachable*. The remaining step — walking
`Diagrams[]` to resolve the 57 `FlatSequenceFrame` diagrams — needs a new op VI and is a judgement call.

⚠️ **CORRECTED 2026-09-16: `FlatSequenceFrame` was in that list and does NOT belong there.** The machine refuses
it as a traverse class with **error 1092** — `tools/bench/build_diagram_hierarchy_run3.log:8`
(*"probe class 'FlatSequenceFrame': … error 1092 … Traverse for GObjects.vi->OpReportAll_v0.vi"*) — and `:9` shows
the working name is **`FlatSequence`** (21 of them). By this file's own rule two sections down, 1092 means the
string is **not in the VI Server GObject hierarchy at all**, which is the same evidence codex's
`FlatSequenceFrame`-is-a-sibling-of-`GObject` hypothesis predicts
(`archive/peer/2026-09-16-ownerchain-flatseqframe-1055-r2.md`). `FlatSequenceFrame` is still the string a diagram
inside a flat sequence REPORTS as its owner class — it is a real runtime class, just not a traversable one.
Found by the cycle-12 prior-art review (`contradicted`, A3-iii).

**Refuted:** `ArraySubset` and `ReplaceArraySubset` are NOT class names — both return error 109 — even though
`IndexArray` is one. Do not guess a primitive's class name from its palette label.

Note for planning: a `report()` pass costs roughly a second per object, so `Terminal` (5763) is about 90 minutes and
`GObject` (10030) longer still. Traverse a narrow class, or reach objects another way.

### The two failure codes are different, and `PropertyNode` / `InvokeNode` are the trap (measured 2026-09-16)

`ArraySubset`-style unknown names give **error 109**. The *plausible-looking* names `PropertyNode` and `InvokeNode`
give **error 1092** instead — *"Invalid Class Operator VI"* — and 1092 is easy to misread as damage to the target
VI rather than a bad string. Measured as a 2×2 grid (`tools/bench/diag_autofocus_panel.log`): `PropertyNode` fails
on **both** a 626-node main VI and a 12-node op VI, while `Property` returns 106 and 12 on the same two. The
failure follows the **name**, never the VI.

The VI Server hierarchy is why, and codex sourced it (`archive/peer/2026-09-16-traverse-1092-failed-prediction.md`,
ANSWERED): the class is `Property` (class ID 16419), reached as
`GObject → Node → Function → GrowableFunction → ObjectFunction → Property`. **`PropertyNode` does not exist in the
hierarchy at all** — it is the palette's descriptive name, and the traverse wants the unlocalized VI Server class
name. Any ancestor in that chain also selects property nodes, as part of a wider result.

### Case-structure frame identity, and a DIAGRAM-SCOPED traverse (peer-sourced 2026-09-16, not yet machine-verified)

From `archive/peer/2026-09-16-case-frame-identity-retry.md` (codex, ANSWERED), asked because
`stage2-assembly-step-e.md:150` has carried *"which diagram is the TRUE frame"* as open since 2026-09-15:

| what | how |
|---|---|
| frame labels | `CaseStructure.Frame Names` **6365002** → string array; a Boolean selector gives `"False"` / `"True"` |
| **label → index** | `CaseStructure.Get Frame Index("True")`, then index `MultiFrameStructure.Frames[]`. ⚠️ **Do not assume `Frame Names` order matches `Frames[]`** — that correspondence is undocumented, and assuming it is how a polarity gets inverted |
| default frame | `CaseStructure.Default Case` **6365001** (I32). It is the *fallback*, never "the True frame" |
| visible frame | `MultiFrameStructure.Visible Frame` **6363800** (U32, 0-based) — the frame shown in the EDITOR, writable while running. Not the executing frame |
| executing frame | **does not exist** as a public scripting property in LabVIEW 2026 |
| subVIs inside one frame | `Traverse for GObjects.vi` with **`Traverse Target = Other`** and **`Other Refnum` = that frame's Diagram reference**, class `SubVI` — it descends recursively into nested containers. Our `OpReportAll_v0` passes Target = 1 (whole BD), so a diagram-scoped variant is a real capability we do not have yet |

**And the warning that matters more than the IDs:** a subVI found inside the selected frame still may not run — it
can sit inside a nested unselected Case or a Disable Structure, it can stall waiting for a required input, or a
subroutine-priority call can carry `Skip Subroutine Call If Busy`. "The frame is selected" never proves "the call
executed", so an instrument claim needs the inner dataflow, not just the selector.

### Two properties an earlier exchange surfaced, both worth having (peer-sourced 2026-09-16, NOT yet machine-verified)

- **`Linked Control` on the `Property` class** returns the front-panel object an *implicit* property node is linked
  to (the node whose `reference` terminal is unwired). Siblings: `Link To Control`, `Disconnect From Control`.
  This is the route to name a property node's control — `panel_wiring` cannot, by construction, because it reports
  *terminals* and a property-node read never touches one.
- **`ClassSpecifierConstant.AllTypes[]`** enumerates LabVIEW's VI Server classes programmatically — class IDs,
  parents, localized and unlocalized names. That is the way to stop guessing class strings entirely: read the list
  from the machine rather than from a palette label or a wiki.

`Property` has **no children** in the hierarchy (ID 16419, under `ObjectFunction`, beside `Invoke`), so a traverse
on `Property` cannot silently over-select other node kinds — the one way the fix above could have been wrong.

⚠️ **This was already written down, twice, and still cost a cycle.** The list above has said `Property` since
2026-09-12, and `tools/bench/census_opwiresource_v5.log:11` recorded `== PropertyNode: raised ... error 1092` —
in the very census file whose uids `tools/recipes/build_opownerchain_v0.py` was built from. The recipe still went
out with `PropertyNode` in three places and would have died at its first `count()`. Before passing a class string
anywhere, read this section; do not re-derive it from what the node is called on the palette.

## `ExecState 0` on an op is not damage — revert first, and check the on-disk checksum (2026-09-12)

`OpFPLabels_v0.vi` read `ExecState 0` and every call through `g.fp_labels()` failed with LabVIEW error **6503**
*"The VI is not executable… either broken or contains a subVI that LabVIEW cannot locate"*. It had worked twenty
minutes earlier. Nothing was damaged:

```
on-disk md5 5f2da97f2d016abf9ad211706d4ab3f6, size 9485
ExecState before revert: 0
revert (reload from disk)
ExecState after  revert: 1
on-disk md5 unchanged  : True
```

**The break was purely in-memory.** What preceded it was pointing scripting ops at *another op VI* —
`g.report(OpFPLabels_v0, "Property")` and `g.net_map(OpFPLabels_v0, 0)` — which appears to leave the target's loaded
copy in an edit state LabVIEW marks broken until it is reloaded. This is the same family as the already-recorded rule
that a `*` in the title bar does not mean the disk file changed: **the loaded state and the file are different things.**

Diagnostic order that worked, and the one to repeat:
1. check every other op (41/41 were ExecState 1) → the cause is specific to this VI, not systemic;
2. check the other VIs that got the same treatment today — the **main VI working copy and three donor VIs were all
   ExecState 1**, which falsified "net_map breaks its target" and confirmed the main VI was never at risk;
3. only then ask disk-vs-memory: `revert()` + an md5 comparison answers it in one call.

Two wrong guesses were made before this evidence was in: that the failure came from pointing `fp_labels` at *itself*,
and earlier that a string in a `.vi` proved a donor node existed. Gather the discriminating observations first.

## Cross-shell paths: never hand a Bash `/tmp` path to PowerShell (2026-09-12)

This project drives both Git Bash and PowerShell, and **`/tmp` is not the same directory in the two**. Git Bash maps it
into its MSYS root; PowerShell reads a leading `/` as the current DRIVE root, so a file written from Bash to
`/tmp/task.txt` is looked for by PowerShell at `G:\tmp\task.txt` and is simply not there.

The failure is quiet and points at the wrong thing. A peer dispatch built as
`powershell -Command "& .\tools\peer.ps1 -Agent codex -Task (Get-Content -Raw /tmp/task.txt)"`
did not report a missing file as its headline: `Get-Content` failed, `-Task` therefore arrived **empty**, and peer.ps1
rejected the call with *"Both -Agent and -Task are required"* — which reads like a bad argument list, not a bad path.

**Rule:** any file handed between the two shells lives under the project (e.g. `tools/bench/scratch/`) or under the
session scratchpad named in the environment — never `/tmp`. Write it and read it with the same relative path so both
shells resolve it identically.

(Related, and from the same session: the heredoc ban in CLAUDE.md is real. Appending this very section with
`py - <<'EOF'` died on `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes … truncated \xXX escape`
because the prose contains Windows paths. Use Edit/Write for file patches.)

## Property and method terminals use LabVIEW's SHORT name, not the documented one (2026-09-13)

Building `OpTunnelInd_v0` cost one whole build cycle to two wrong terminal names — **both wrong in the same
direction**, and both guessed from documentation instead of read off the machine:

| what the docs / the property list call it | what the terminal is actually called |
|---|---|
| `Tunnel.Outside Terminal` (property 6356001) | **`Outer Term`** |
| `To More Specific Class` → "specific class reference out" | **`specific class reference`** |

The symptom is `error 5001: LV-Scripting.lvlib:Get Outputs.vi` from `wire()` — a MISSING name, not an illegal
connection (an illegal but existing name is declined *silently* instead). So 5001 always means "look up the real
name", never "this wire is not allowed".

**How to get the real names in one call, without guessing:** `g.net_map(target, 0, max_nodes=40, max_terms=20)`
prints every node's full terminal list with indices and which wire is attached. Run it on the assembled-but-broken
VI *before* the next attempt; it is far cheaper than a build cycle, and it is what finally supplied both names above.

Verified terminals of the nodes this project builds most:

| node | terminals (in `Terminals[]` order) |
|---|---|
| Property node (any class) | `reference`, `reference out`, `error in (no error)`, `error out`, then one per property |
| Invoke node (any class) | `reference`, `reference out`, `error in (no error)`, `error out`, then the method's |
| `To More Specific Class` | `specific class reference`, `error out`, `target class`, `reference`, `error in` |
| `Traverse for GObjects.vi` | `error out`, `# of Refs`, `References`, `dup VI Refnum`, `Other Refnum`, `Traverse Generated Code (F)`, `Traverse Target`, `error in (no error)`, `Class Name`, `VI Refnum` |
| `Index Array` | `array`, `element`, `index` |

Note that a Property/Invoke node's `error in` is spelled `error in (no error)` while `To More Specific Class` uses
the bare `error in` — the primitive-vs-subVI split already recorded in the skill, confirmed again here.

- **`Create For Loop.vi` / `Create While Loop.vi` `Control Names` DO work — when `Get Controls.'Control Terminals'` is wired
  into the creator's `Inputs`** (2026-09-14 20:4x, `test_opwhileloop.log`: one tunnel per named control, outer wire on
  the control's terminal). OpForLoop_v0 never had that wire (probe_opforloop.log), hence the morning's "Control Names
  route not available" — a defect of OUR op, not of the library. An empty While loop's `Node.Terminals[]` is empty
  (a For loop's holds the N terminal). `Exit While Loop.vi` connector: 0 `Diagram in`, 1 `Conditional Terminals`,
  2 `Loop Terminal Types`, 5/6 `Outputs` in/out, 7/8 `Shift Registers` in/out, 9 `Stop Condition`, 11/15 error.
- **Queue creators (erdosmiller, `probe_queue_vis.log`):** `Create Obtain Queue.vi` 5 `element data type` (a terminal
  ref whose TYPE the queue takes; the created `Obtain Queue` node's own `element data type` input is wired from it),
  6 `queue out`; `Create Enqueue Element.vi` 5 `queue`, 7 `element`; `Create Dequeue Element.vi` 5 `queue`,
  7 `timeout in ms (-1)`, 8 `element`, 14 `timed out?`; `Create Release Queue.vi` 5 `queue`; ALL: 0 `Diagram in`,
  2 `location (0, 0)`, 4 `Diagram out`, **9 `error in` / 10 `error out` = terminal REFNUMS of the created node's error
  terminals, 11 `error in (no error)` / 15 `error out` = the creator's own chain** — wire 15 by INDEX (a by-name
  `error out` hits 10 and feeds a refnum into an error cluster). Created nodes' terminal names: Obtain `name (unnamed)`,
  `element data type`, `create if not found? (T)`, `max queue size (-1, unlimited)`, `queue out`, `created new?`;
  Enqueue `queue`, `element`, `timeout in ms (-1)`, `queue out`, `timed out?`; Dequeue `queue`, `timeout in ms (-1)`,
  `queue out`, `element`, `timed out?`; Release `queue`. Wiring a refnum output from the top level into a node inside a
  loop auto-creates the tunnel (census 2026-09-14 22:03). **Never run a scripted VI with a `Dequeue(-1)`: a producer
  that silently produces nothing (N = 0 from an errored ReadFile) turns it into a COM hang** (test_opqueue.log run 1).

## Shift registers are CREATABLE by script — `Loop.Add Shift Register` 6361000 (VERIFIED 2026-09-14, INDEX row 37)

The entry above ("not yet verified on this machine") is now verified, and two things the fleet had assumed were
wrong are settled by measurement (`tools/bench/build_opaddshiftreg_v0_run3.log`):

- **The method is PUBLIC.** It attaches through the ordinary `build_invoke` — no "Allow Private" setter is needed.
  The node's terminals: `reference`, `reference out`, `error in (no error)`, `error out`, and **`Add Shift Register`
  and `Y Position` TWICE EACH** — index 6 = `Y Position` sink, 7 = source; 4 = return sink, 5 = **return source**.
  Address them by **index + direction, never by name** (the third duplicate-name incident of the day).
- **A `Loop`-class Invoke accepts a `WhileLoop` reference** (VI Server inheritance): no retarget to a WhileLoop-class
  invoke, and `6361000` is owned by `Loop` 16405, not by `WhileLoop`.
- **Both sides of the new register come back UNWIRED**, and an unwired register legitimately breaks the VI
  (ExecState 0) until wired. Wiring rule (labviewwiki, adopted): `Terminal.Connect Wire` **6349C03 is invoked on the
  SINK**, `Wire Source` = the source. `LeftShiftRegister` 16442 derives from `Tunnel`, so `Outside Terminal` 6356001
  (the initial-value sink) and `Inside Terminals[]` 6356000 (the body-side source) apply to it.
- API: `gscript.add_shift_reg(target, loop_index, y_position, class_name='WhileLoop')` → the new register's UID.

**Two COM/recipe traps recorded the same evening, both of which cost a batch:**

- **`gscript.wire(..., branch=True)` only SKIPS the wire-count check** — it does not verify anything, and an unchanged
  wire count is equally consistent with a successful branch and a silent decline. Verify a branch by reading the
  **wire UID on both terminal ends** (`node_terms`): a real branch shares the existing Wire object, so the two UIDs
  are equal. Never gate on `ExecState` while a required input is still unwired — it cannot discriminate.
- **`g._lv = None` must run before ANY op-VI proxy is cached** (top of `main()`, once). Executing it after an earlier
  phase has cached reporter VIs re-Dispatches the Application underneath those proxies, and the next call against a
  cached one raises `0x800706BA` `RPC_S_SERVER_UNAVAILABLE` mid-batch — which is **not** proof the process died
  (a busy STA gives `RPC_E_SERVERCALL_RETRYLATER` 0x8001010A, a disconnected object `RPC_E_DISCONNECTED` 0x80010108).

## Vision LLB member locations (re-learned 2026-09-14 23:13 — write the path from HERE, never from memory)

| VI | path (no `.vi` inside the LLB) |
|---|---|
| `IMAQ Create` | `…\nivisioncommon\1\vi.lib\vision\Basics.llb\IMAQ Create` |
| `IMAQ GetImageSize` | `…\Basics.llb\IMAQ GetImageSize` |
| `IMAQ ReadFile` | `…\Files.llb\IMAQ ReadFile` |
| `IMAQ Write TIFF File 2` | `…\Files.llb\IMAQ Write TIFF File 2` |
| **`IMAQ Copy`** | **`C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb\IMAQ Copy`** — NOT Basics.llb, and NOT under `nivisioncommon\1` (there is no Management.llb there); error 7 either way; cost two batches on 2026-09-14 |

**How a wrong LLB path shows up:** `OpSubVI_v1`'s `Open VI Reference` errors 7 and the op's AUTOMATIC ERROR
HANDLING raises an **untitled** ~350×305 modal and opens the op's own Block Diagram (`OpSubVI_v1.vi Block Diagram`
appears among the windows). gscript's watchdog reports it correctly as a modal (`tools/bench/test_opwiresr.log`).

## Three facts from overnight cycle 3 (2026-09-14/15, INDEX row 39)

- **`set_node_label` is an EDIT: the target's panel must be OPEN or it is declined silently** — like `wire` and
  `drop_subvi`. Inside `copy_into(prepare=…)` the hook must `open_panel(src)` first and read the label back
  (`node_labels`) on the intended UID before the Move op runs; otherwise `OpMoveByLabel` fails with **error 1054
  "object not found"** at its `Open VI Object Reference` (`cycle3_toolkit.log` run 2, item 3).
- **A SCALAR control cannot auto-index:** `for_loop(tunnels=[scalar], indexing=[True])` creates the tunnel but
  IndexMode stays 0 (no error). With an ARRAY control the same call gives IndexMode 1, and an indexed array input
  alone makes the For loop legal (N = array length; an empty array = zero iterations, initialised registers return
  their initialisers). `set_index_mode(…, 1)` is safe BEFORE the inner terminal is wired (array-typed outer).
- **A free String[] control from nothing:** drop `Get Controls.vi`, `create_control` on its `Control Names` input
  (String[]), delete that wire, delete the helper node, `remove_bad_wires`. The control keeps its type (verified:
  it drove an auto-indexed For loop with 3 elements and with an empty array). The same trick yields any array
  type that some droppable VI exposes on an input terminal.
- **A border-crossing wire is TWO Wire objects through a tunnel** (uids differ at the two ends — never gate a
  cross-border wire on uid equality; gate on: exactly one new LoopTunnel, `out_wire` == source, `in_wires` ==
  [sink], outer sink / inner source, clean error fields). **And an ARRAY wired INTO a For loop by name arrives
  AUTO-INDEXED** (LabVIEW's editor default, applied by `Wire Inputs.vi`): `Array of cal clusters` came in with
  IndexMode 1 — one cluster per frame into a whole-array kernel input, a rule-1a computation change caught only by
  the IndexMode-0 gate (`build_track_v6_core.log` run 2). Whole-value array inputs must be flipped with
  `set_index_mode(tunnel, 0)` and re-read.
- **A loop NODE's `Terminals[]` lists ALL its tunnels' outer terminals, named by their source labels** (measured
  2026-09-15 03:3x on `Track_v6_CPU_core_v0.vi`, `census_loop_node_terms.log`): index 0 = N (unnamed sink),
  then each input tunnel (sink, name = the control/source label), each shift register's outside pair
  (source = final value / sink = initial value, name = the initialising control), and each auto-indexed output
  tunnel (source, name = the inner source's terminal name). So a loop's output can be wired onward BY NAME with
  `wire(target, 'ForLoop', i, '<output name>', …)` / `connect_terminals(...)` like any node — no tunnel-outer op needed.
- **Queue primitive terminal names (exact, `test_opqueue.log`):** Enqueue Element: `queue`, `element`,
  `timeout in ms (-1)`, `error in (no error)` → `queue out`, `timed out?`, `error out`. Dequeue Element: `queue`,
  `timeout in ms (-1)`, `error in (no error)` → `queue out`, `element`, `timed out?`, `error out`. Release Queue:
  `queue`, `force destroy? (F)`, `error in (no error)` → `queue name`, `remaining elements`, `error out`. A guessed
  `'timeout'` cost a 9-minute batch on 2026-09-15 (5001 from Wire Inputs).
- **A forward slash inside `vi path` makes an op's `Open VI Reference` fail → error 1055 at the first property
  node, in 0 s** (2026-09-15 03:54, `census_constant_seed.log` run 1: `os.path.join(dir, "sub/file.vi")`). Always
  pass backslash paths to the ops; the same VI loaded fine with a backslash path.
- **After ANY LabVIEW kill/restart inside a script, call `gscript.reset()`** (clears the Application AND the
  op-proxy cache `_cache`); `_lv = None` alone leaves cached op VIs bound to the dead instance and the next
  cache-hit call dies with 0x800706BA (2026-09-14 22:35, 2026-09-15 04:00). Never retain an op proxy across a
  restart boundary; no per-call liveness check (peer `…-opconstvalue-fail1-stale-op-cache.md`).
- **COM-launched LabVIEW lifetime (measured 2026-09-15 04:19–04:22, `tools/bench/diag_rpc_restart.py`):**
  `Dispatch("LabVIEW.Application")` blocks ~14 s and returns an instance that answers `Version` immediately;
  loading the 4-MB main VI via the reporter takes ~17 s on a fresh instance and ~12 s warm; and an instance
  that the script launched, with **no front panel open, exits within seconds of the client process ending** —
  so "no LabVIEW process afterwards" is the normal outcome of a script that died, not evidence of a crash. The
  run-4 `0x800706BA` right after a kill+relaunch was NOT reproduced in two controlled attempts (cold and warm);
  its trigger is unknown — a preflight (`com_preflight`: two spaced round-trips, unchanged pid) is the gate
  (peer `…-opconstvalue-run4-rpc-after-restart-no-labview.md`).
- **UID → object without traversing:** `C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\VIServer\UID to
  GObject Reference.vi` — terminals MEASURED 2026-09-15 11:52: inputs **`Owning VI`**, **`UID`**,
  `error in (no error)`; outputs **`GObject`**, `dup Owning VI`, `error out`; the remaining connector-pane slots
  report EMPTY names. Development environment only, not the runtime engine; never submit a UID that may not exist
  (reported crash hazard). Not yet wrapped as an op — the route to take when a UID lookup is needed on a big VI, since
  `gscript.report()` costs ONE OP RUN PER OBJECT (use `uids()`/`report_all` for lists: one run).
- **A wire-uid-equality gate does NOT prove a wire is GOOD** (measured 2026-09-15 06:20,
  `tools/bench/build_opwiresource_v0.log`): LabVIEW joins type-incompatible terminals and draws a broken wire, whose
  uid still reads identically at both ends. Gate `exec_state == 1` after any wire whose types are not obviously
  compatible. Measured case: `Generic.Owner` (6327806) returns a **Generic** reference, and wiring it into a
  **GObject**-class property node (for `UID` 632A813) is a downcast — ExecState 1 → 0, and `Terminal.Create
  Indicator` on that node then returns NOTHING (no object, no error). A downcast needs a To More Specific Class;
  `Wire` → `GObject` (e.g. `Terminal.Connected Wire` → `UID`) is an upcast and is legal. `Generic` exposes no UID.
- **Case-structure reading (IDs sourced 2026-09-15, peer `…-case-frame-reader-property-ids`; short names marked
  UNKNOWN are to be censused, never guessed):** class `CaseStructure` (id 16408), parent `MultiFrameStructure`.
  `MultiFrameStructure.Frames[]` **6363801** (frame Diagram refs; **short name MEASURED — the data terminal is
  named `Frames[]`**, censused five times on `VI Server:MultiFrameStructure` at
  `tools/bench/build_opcaseframes_v0.log:9-11,36-38,61-63,90-92,120-122`; the "UNKNOWN" here was stale, found by
  the cycle-13 prior-art review. Whether it attaches to `VI Server:FlatSequence` is a different question and is
  measured in cycle 13) · `CaseStructure.Frame Names`
  **6365002** → `FrameNames` · `MultiFrameStructure.Visible Frame` **6363800** → `VisFrame` ·
  `CaseStructure.Selector` **6365000** (short name UNKNOWN) · method `CaseStructure.Get Frame Index` **6364C04** →
  `GetFrameIndex`. A case DATA tunnel is class **`ConditionalTunnel`** (inherits `Tunnel`), and its
  `Use Default if Unwired` is **5D251C00** → `UseDefault`. `Tunnel.Inside Terminals[]` 6356000 gives one inner
  terminal per frame but **its order is NOT documented as frame order** — map each inner terminal to its frame with
  `Terminal.Diagram` **634A002** → `Diagram` and match that diagram's `UID` against `Frames[]`.
- **Before building a reader for the main VI, read `docs/main-vi-panel-map.md`** — it already lists every top-level
  panel object with the wire uid its terminal carries. The three reseed selector feeders (wires 10312 / 9806 / 10142
  → controls `Reset Tracking` / `Auto-Reset` / `Limit of Program`) were in that table before the UID-walk op was
  built (2026-09-15). `gscript.panel_wiring(target)` regenerates it in ONE op run (~2 s on the main VI).
- **A wire whose SOURCE terminal reports owner class `Diagram` is a front-panel CONTROL TERMINAL** (a control
  terminal's `Owner` is the diagram, not the control) — measured 2026-09-15 12:06 and cross-checked against
  `panel_wiring`. Name it from the panel census, not from `Generic.Owner`.
- ✅ **`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED, 2026-09-17** — and it never needed a new op. Short name
  **`Is Broken?`**. `OpConnectNested_v0/v1` and `OpConnectFromWire_v0` all carry the reader already: a property
  node reads `Wire` off the SINK terminal reference, and a second reads that wire's `UID` + `Broken?`, surfaced on
  the panel as `UID 2` / `Is Broken?`. ⚠️ **The whole trick is ORDER**: that node's `error in (no error)` ships
  UNWIRED, so it may run BEFORE the `Connect Wire` and report the OLD wire — which is why every readback in
  `build_d1_v0_run9.log:260-267` printed `'UID 2': 0`. Branch the Invoke's own `error out` into it
  (`build_opconnectfromwire_v0.py` gate **W7b**) and it answers: measured `False` on a good wire
  (`build_opconnectfromwire_v0_run2.log` T1f2) and **`True`** on a two-source wire (T2c2). **Use this, not
  "the wire survives `remove_bad_wires_scripted`"** — that check is uid equality and misreports
  (`docs/d1-build-plan.md` §11u.1).
- ⚠️ **READING `Is Broken?` PERTURBS THE TARGET — an ExecState read taken AFTER a wire read is not evidence of
  brokenness** (measured 2026-09-18, cycle 23). Because the readout is ordered after the Invoke, the only way to
  make it run is to perform `Terminal.Connect Wire` — and the cheapest form of that is to re-connect the SAME
  source→sink pair the wire already has, i.e. an **idempotent** connect (0 new Wire objects). Measured on a B4
  scratch whose `ExecState` was **1** immediately before: the read returned `UID 2 = 384`, `Is Broken? = False`,
  wire delta 0 — and `ExecState` afterwards read **0**
  (`tools/bench/diag_fstunnel_rbwvictims.log:169-170`). So: read the value, then treat any ExecState taken after
  it as SUSPECT, and re-establish legality from a VI the reader has not touched.
  🔴 **THE OPERATIONAL CONSEQUENCE, RE-LEARNED THE EXPENSIVE WAY IN CYCLE 61 (2026-09-21): NEVER READ
  `Is Broken?` ABOVE A SAVE POINT.** The ordered pass belongs AFTER the save, and preferably after a COLD
  reopen — the order `tools/recipes/stage_d1_s3a_focus_ind.py` passed 64/0 with, and what Pre-decided 42(b)
  already said. `tools/bench/diag_c61_localdir_write.log` built a correct op, read `Is Broken?` (False) before
  finishing it, then read its save gate as `ExecState` **0** and threw the build away; the identical
  construction with the read moved below the save saved at **1** and reopened cold at **1**
  (`tools/bench/diag_c61_localdir_write2.log`, `docs/cycle27-plan.md` Pre-decided 52(f)). **OPEN — the mechanism is not
  settled**: an idempotent connect that leaves a legal VI illegal could be the connect itself, the property node's
  own execution, or a stale/uncommitted compile state; nothing here distinguishes them, and one measurement on one
  wire is not a rule. Two consequences that hold regardless: a reader of `Is Broken?` must not be placed on a
  recipe's success path, and a wire **no node terminal carries** (an orphan) has no sink terminal at all, so this
  route cannot read its `Is Broken?` value — there is no measured route to that value today
  (`…rbwvictims.log:80,86` — "END NONE" for 894 and 1356).
- **Still not built (IDs recorded 2026-09-15):** VI-class method **`Get Errors` 452** (private; the compiler's
  error list) and `Wire.Get Error List` **6370C0A** (private, output `Error List`).
- **Two terminals on one wire both reporting `Terminal.Is Source?` 634A003 TRUE = the wire is BROKEN** (two
  drivers). MEASURED 2026-09-17 on `w1231` (`SelectorTunnel` #5680 + `LoopTunnel` #2497, `Is Broken? True`).
  ⚠️ A structure TUNNEL has an OUTSIDE terminal and one INSIDE terminal per frame (`Tunnel.Outside Terminal`
  **6356001**, `Tunnel.Inside Terminals[]` **6356000**), and on a loop BODY diagram the inside terminal of an
  INPUT tunnel is itself a SOURCE — so wiring a source onto an OUTPUT tunnel's outside terminal makes exactly this
  conflict. A `(node, terminal index)` pair does not name the SIDE.
- **A BRANCH is one Wire object shared by every sink** (same run): deleting "the branch" deletes the whole wire and
  breaks the other sinks; to drop one branch, delete the SINK NODE and run Remove Bad Wires (which removes only
  BROKEN wires — it never restores a healthy one you deleted). The per-sink primitive, if ever needed on a wire
  that must survive, is **`Wire.Disconnect Terminal` 6370C0D** (no `Terminal.Disconnect Wire` exists; the
  counterpart is `Terminal.Connect Wire` 6349C03).
- **Lossless bytes out of an op (measured 2026-09-15 05:06–05:11, `OpConstValue_v1.vi`):** a LabVIEW string
  indicator reaches Python through `GetControlValue` **code-page DECODED (cp949)** — binary strings are corrupted
  (chars > U+00FF); a string route can never be proven lossless. Route that works: `Flatten To String` →
  `Unflatten From String` (creator `OpBuildUnflatten_v0`, class `FlattenUnflattenString`; terminals `binary string`,
  `type`, `data includes array or string size? (T)`, `byte order (0:big-endian, network order)`, `error in (no
  error)` → `value`, `rest of the binary string`, `error out`) with `type` ← a U8[] control and the size? Boolean
  control set FALSE per run = String To Byte Array (no creator exists for it) → U8[] indicator arrives as
  SAFEARRAY(VT_UI1) (`bytes(v)`); `vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi` (`bytes` U8[] sink →
  `hex string`, 2 lowercase digits/byte) gives the same bytes as ASCII. **U8[] typed control from nothing:**
  `create_control` on that VI's `bytes` input, then cut the wire (same trick as the String[] control).
- **Flattened-variant layout (measured, LV 2026):** U32 version `26008000` · I32 nTDs · TDs (I16 length, I16 code —
  low byte = type, high byte 0x40 = labelled; string TD `4030 ffffffff` + Pascal label) · I16 nTypesUsed · I16
  indices · data (string: I32 length + bytes; scalars: raw big-endian, DBL 0x0A = 8 B) · I32 attribute count.
  Parser: `tools/recipes/build_opconstvalue_v1b.py::decode_flat`.
- **`Constant.Value` 634AC00 read through a `VI Server:Constant` cast returns the value for a StringConstant but an
  EMPTY (void, TD 0x0000) variant for every DigitalNumericConstant, without error** (measured on 6 uids of the main
  VI, 2026-09-15 05:11); BooleanConstant is void too (4/4). **RESOLVED 05:41 (`OpConstValueN_v0.vi`): the STATIC
  CLASS of the scripted property node decides — the same 634AC00 read through a node built for
  `VI Server:DigitalNumericConstant` (typed control from ITS `reference` → TMSC target) returns the value for every
  numeric constant (labelled TDs 400a DBL / 4007 U32 / 4003 I32).** This is UNDOCUMENTED LabVIEW 2026 behaviour
  (probably a defect — NI documents Value on the base class with no subtype restriction; peer
  `…-opconstvaluen-run2-typed-node-carries-data`); the working practice is: build the Value node for the object's
  most-specific class. A wrong-class object through the typed cast surfaces as error 1055 on the typed property
  nodes (separate error indicators), not on the op chain. In THIS `Flatten To String(variant)` encoding labelled
  scalar TDs have ODD lengths (7, 11, 17, 21, 23) with no pad byte (the even-rounding applies to the
  `Variant To Flattened String` form, not here). `NumericConstant.Representation` enum (NI doc): 1 DBL, 3 I32,
  6 U32 — cross-checks the TD low byte 0x0A/0x03/0x07.
- **`VI Server:DigitalNumericConstant` property IDs (measured by attaching each, 2026-09-15 05:34 — the labviewwiki
  class table is shifted):** `634D001` Fmt&Prec · `634D002` Format · `634D003` Precision · `634D004` RadixVis ·
  `634D005` refused (error 107, private) · `634D006` FormatString · `634D007` **NumText** (the `Numeric Text`
  reference → `Text.Text` 632D800) · `634D008` Unit Label. `5DCFC00` = NumericConstant.Representation.
- **The register ops exist for BOTH loop classes:** WhileLoop seed (`OpAddShiftReg_v0`, `OpWireSR_*`) and ForLoop
  seed (`OpAddShiftRegF_v0`, `OpWireSRF_*`, `SR_SEED=For`); the register READERS (`shift_reg*`) remain WhileLoop-only.

- **Two nodes can expose the same property name — select a property node by DATAFLOW, never by first match**
  (measured 2026-09-15 12:5x, `tools/bench/build_opwiresource_v4.log`). `OpReport_v3`'s identity node carries
  `Position`/`ClassName`/`UID`/`Owner` on ONE property node describing the TRAVERSED object; a second `Owner` node
  built later describes an indexed terminal. A recipe that picked "the node with an `Owner` output" got the first
  one and silently reported the traversed object's owner (a `Diagram`, uid constant across every index) while a
  neighbouring chain reported the right classes. The gate that catches it: after wiring, print and assert that each
  property node's `reference` sink wire equals the wire you intended, and read `Generic.Class Name` of the object
  whose UID you print.

- **`OpWireSource_v5.vi` (built 2026-09-15, 12/12): wire UID -> the object that DRIVES it.** Address any object by
  UID through `vi.lib\VIServer\UID to GObject Reference.vi` (`Owning VI` + `UID` -> `GObject`), cast to `Wire`, then
  `Wire.Terms[]` -> Index Array[`term index`] -> per terminal: `Is Source?` 634A003, the reciprocal
  `Connected Wire` 634A000 -> `UID`, and `Generic.Owner` -> `ClassName` + cast(GObject) -> `UID`. Labels in
  `tools/bench/opwiresource_v5_labels.json`. Walk `term index` 0,1,2... until error 1055 = past the end; require
  exactly ONE terminal with `Is Source?` TRUE whose reciprocal wire is the wire asked about. Verified on the main VI:
  wire 10850 -> source `DigitalNumericConstant` 10739 / sink `Comparison` 10950.

- **Never call Remove Bad Wires inside a transient edit window** (measured 2026-09-15 13:3x,
  `tools/bench/build_optunnelread_v0.log`): while an Index Array's `array` input is momentarily unwired its
  `element` output has no type, so EVERY wire downstream counts as broken and Remove Bad Wires deletes the whole
  reader chain — leaving provenance gates that still pass on the wires you did check. Order: delete → rewire →
  (optionally) clean up once at the end, and re-feed orphaned terminal readers from the Index Array ELEMENT, never
  from the cast that produces the array.

- **Deleting a node leaves its wire behind as a loose stub** (measured 2026-09-15, confirmed by peer
  `…-opcaseframes-identify-before-delete`): a later connection from that source then counts as a BRANCH, and a search
  for "unwired sinks" will NOT find the orphaned consumer, because its `reference` still reports the stub's uid.
  Identify and CACHE the consumer node and the wire uid BEFORE deleting, then delete node, delete wire, rewire.
- **Owner chain inside a case frame:** a node's `Generic.Owner` is its frame **Diagram**; that Diagram's `Owner` is
  the **CaseStructure**. So on a Frames[] element, `Owner` → `UID` should equal the case's own uid — a free
  provenance check for frame readers.

## `Count` — MEASURED 2026-09-18 (cycle 35), `tools/bench/diag_count_indicator_run4.log`, 16/0, rc=0

Read off the claudeDev D0 copy `Track_D0_copy_20260918.vi` (read-only; original md5 `2a78e17c449c…` unchanged).
Full readings in `tools/bench/count_indicator.json`.

| fact | value |
|---|---|
| label, exact bytes | `'Count'` — no newline, no trailing space; the ONLY panel object matching `count` |
| uid / role | **28051, a front-panel CONTROL — `indicator` False** (not an indicator, which is what its name suggests and what two harness versions assumed) |
| its terminal | `is_source` **True** — it DRIVES wire **30530**; nothing writes it through the terminal |
| who READS it (wire 30530 sinks) | `Comparison` **#29111** label `Equal?`, terminal `x` (its `y` = w29234, output `x = y?` = w29334) · `SelectorTunnel` **#31929** of `CaseStructure` **#28709** |
| where those live | Diagram **#15795** (Traverse index 142) → `Sequence` #15649 → Diagram #15622 → **`EventStructure` #15544** → Diagram #15266 |
| who WRITES it | **two implicit `Property` nodes labelled `Count`**, each with a `Value` terminal that is a SINK carrying a wire: **#32191** (`Value` ← w32760) on Diagram #12960 (index 86), and **#30688** (`Value` ← w31525) on Diagram #28741 (index 144) inside `CaseStructure` #28709 |
| the 8 `Local` objects | uids 2991, 4277, 11574, 3160, 3097, 2143, 16942, 25805 — none is labelled `Count` (whole-VI sweep, 170/170 diagrams) |

So `Count` is a **control used as a counter variable**: written by `Value` property nodes inside an
`EventStructure`'s case, read back by an `Equal?` test and a case selector on the same diagram. `panel_wiring`
alone could never have said this — it sees terminals only (`docs/toolkit-capabilities.md:22`, the op's own row: label, indicator flag, control UID, terminal `Is Source?`, connected-wire UID), and the
writers are property nodes. The reader that found them is `node_labels`, because an implicit property node's
label IS its bound panel object's name (`docs/toolkit-capabilities.md:26`).

⚠️ Two limits of this reading, both measured rather than assumed: the owner chain of #32191 terminates at
`FlatSequenceFrame` with **owner_uid 0** (the known silent termination, `docs/toolkit-capabilities.md:61`), so
that writer's enclosing structure above the frame is NOT established; and `report_all('GlobalVariable')` fails on
this VI with `error 1092`, so a global-variable writer would not have been seen.
⚠️ Also measured, and NOT diagnosed: the claudeDev D0 copy reads **ExecState 0 (broken)** as it sits on disk.
