---
type: reference
status: current
date: 2026-09-14
tags: [docs]
---

# Keystone op spec — `OpBuildNode_v0.vi` (2026-09-04, awaiting start signal)

Purpose: the ONE op after which no diagram construction needs a GUI click. It creates a
Property Node or Invoke Node on a target VI's diagram, typed by CLASS NAME (string), with its
items (property/method names as strings, write flags), and optionally wires a reference terminal
into it. Everything Python passes is plain data.

## Front panel (all plain — settable from Python via SetControlValue)

| control | type | meaning |
|---|---|---|
| `vi path` | path | target VI (opened via Open VI Reference inside) |
| `Class Name` | string | Traverse class of the DIAGRAM to build in (`Diagram`) |
| `index` | I32 | which diagram (0 = top level; loop/case bodies by traversal index) |
| `kind` | string `property`\|`invoke` | which erdosmiller creator runs (Case structure) |
| `node class` | string | VI-Server class name for the new node, e.g. `Control`, `Terminal`, `LoopTunnel`, `ClassSpecifierConstant` |
| `items` | array of cluster {`ID String`, `Is Write?`} | properties (for `property`) — for `invoke` only element 0's `ID String` is used as the method |
| `ref class` / `ref index` / `ref terminal` | string / I32 / string | OPTIONAL source of the class-context wire: Traverse `ref class`[`ref index`] → `Get Outputs`[`ref terminal`] → the creator's `reference` |
| `location (0, 0)` | cluster {Horizontal, Vertical} | where to drop |
| `error out`, `UID` | indicators | result: new node's UID (from GObject `UID`-less: read back via OpReport after) |

`items` is an array-of-cluster control: `copy_into` it from the donor `Create Property Node.vi`'s
own `Properties` control (label `Properties`) — the one UNVERIFIED link; if copy_into cannot
carry an array-of-cluster, fall back to two parallel arrays (`ID Strings[]` strings, `Is Write?[]`
booleans) which are copyable from existing ops, and bundle inside the op with `Create Bundle.vi`.

## Diagram (built by script from a copy of OpSubVI_v1.vi, which already has path→Diagram navigation)

1. keep: `vi path` → Open VI Reference → Traverse(`Class Name`,`index`) → Index Array → Diagram ref
2. `drop_subvi` erdosmiller `Create Property Node.vi` and `Create Invoke Node.vi` (paths under
   `vi.lib\Erdos Miller\LV-Scripting\`), one in each frame of a Case structure keyed by `kind`
   (`Create Case Structure.vi` is scriptable; simplest v0: NO case — two ops, `OpBuildPN_v0` and
   `OpBuildInvoke_v0`, sharing the skeleton).
3. wire by name (names from ExportVIStrings, 2026-09-04): `Diagram in`, `Class Name`, `Properties`
   (PN) / `ID String` (Invoke), `location (0, 0)`, `error in (no error)`, `reference` (optional).
   Outputs: `Outputs`, `Inputs` (terminal ref arrays), `reference out`, `error out`.
4. `error out` → the op's `error out` indicator (existing).

## Acceptance (structural, then functional)

- Structural: ExecState 1 after assembly; every wire landed by +1 count or loud 5001 probe.
- Functional: run against `FPTARGET_v0.vi`: kind=property, node class=`Control`,
  items=[{`Position`,TRUE}], location (600,300) → OpReport shows +1 Property, +1 PropertyItem;
  then kind=invoke, node class=`Terminal`, items=[{`Create Indicator`,FALSE}] → +1 Invoke.
- Then rebuild `OpFP_v0`'s tail with these two calls + `wire` to prove zero-click parity with the
  seven GUI actions of 2026-09-04.

## Known unknowns (state them, do not bridge them with clicks)

- Whether `Class Name` on the erdosmiller VIs is on the connector pane (NAMES.md once said no for
  Create Property Node; ExportVIStrings lists it as a control). If unreachable by `Wire Inputs`,
  the class must come from the `reference` wire — then `ref *` inputs become mandatory.
- `copy_into` of an array-of-cluster control (see above).
- Whether `Create Invoke Node.vi` without `reference` yields a usable Application-classed node
  that `Class Name` re-types.

## Build plan v1 (2026-09-05, after the M3 clicker; for peer review before construction)

Skeleton = copy of `OpWire_v1.vi` (COM-verified structure 2026-09-05): chain A `vi path` →
Open VI Ref → Traverse(`Class Name`, `index`) → Index Array(308) → Get Outputs(216)[terminal
names] → **Wire Inputs(262)**.Inputs; chain B Traverse(`Class Name 2`, `index 2`) → Index
Array(327) → Wire Inputs.Node; `error out` → Clear Errors sinks (369/370). `OpFP_v0` is this
skeleton with a hand-clicked tail (Index Array 534 → Invoke 538 → Property 610); the keystone
must produce such tails by script.

Steps (one script, `tools/recipes/build_keystone.py`, on `OpBuildPN_v0.vi` = copy of OpWire_v1):
1. `drop_subvi(target, <Erdos Miller>\Create Property Node.vi, 0, (875, 600))`.
2. Chain B becomes the DIAGRAM source: `Class Name 2` = "Diagram", `index 2` = n → Index
   Array(327) output → creator `Diagram in`.
3. Chain A becomes the REFERENCE source: Traverse(`Class Name`,`index`) → Get Outputs[`terminal
   names`] → (new Index Array, element 0) → creator `reference` (class context; error 1077 if
   unwired). New Index Array via erdosmiller `Create Index Array.vi` if an op exists, else
   `copy_into` from `DONOR_arrayops.vi`.
4. `Properties` control: `copy_into(Create Property Node.vi, "Properties", target)` (array of
   {ID String, Is Write?}); fallback: two parallel array controls + `Create Bundle`.
5. `location (0, 0)`: copy_into from OpSubVI_v1 (control 732) → creator `location (0, 0)`.
6. Error chain: creator `error in (no error)` ← previous error wire (Get Outputs `error out`);
   creator `error out` → the existing sink (wire by name). Delete Wire Inputs(262) with
   `delete_by_label`, then `remove_bad_wires`.
7. `save` (allow_broken=False) → structural check (ExecState 1, +1 SubVI, wire counts).
Functional acceptance on `FPTARGET_v0.vi` as in §"Acceptance" above; then `OpBuildInvoke_v0`
by the same script with `Create Invoke Node.vi` (`ID String` instead of `Properties`).

Discovery batch first (scratch copy `SCRATCH_keystone.vi`, deleted afterwards): D1 drop of the
creator; D2 copy_into of the array-of-cluster control; D3 wire-by-name into `Diagram in` /
`reference` / `Properties` / `error in (no error)`; D4 delete_by_label on a SubVI node;
D5 an Index Array from script. Each step's prediction: +1 object of the expected class or a
loud 5001; nothing silent.

## Build plan v2 (2026-09-05, after codex review — archive/peer/2026-09-05-keystone-build-plan-attack.md)

What the review changed (accepted):
- **The created node's class follows the referenced OBJECT, not a string.** Machine evidence
  already on file: Terminal ref → node typed `Term`; only the `Create Indicator` Control refnum
  gives `Ctl` (NAMES.md, OpFP_v0). So the keystone's `node class` input is replaced by
  **`ref class` / `ref index`**: Traverse the TARGET for an existing object of the wanted class
  (Property, Invoke, Diagram, Control, Terminal, …) and pass THAT object ref as `reference`. Every
  class the toolkit needs already exists in some claudeDev VI (OpFP_v0 has a Property node and an
  Invoke node) — "donor by reference", zero clicks.
- **Delete last.** Record the Wire Inputs topology, install and wire the creator, verify every
  intended endpoint, then delete Wire Inputs and only then `remove_bad_wires`.
- **Pane names from the reporter, not ExportVIStrings.** Before wiring: run the connector-pane
  reporter (Get Controls / Get Outputs by name — a 5001 is the loud negative) on the installed
  `Create Property Node.vi` / `Create Invoke Node.vi`; the only confirmed inputs today are
  `Diagram in`, `Properties`, `reference`, `error in`; outputs unconfirmed.
- **`Properties` control check = wire it and read the datatype**, not a count.
- Longer-term architecture (peer §5, agreed): a reference-free generic creator = New VI Object
  (style `Property Node` / `Invoke Node`, ring value read on LV2026) + `Property Node Class Name`
  / `Invoke Node Class Name` (R/W) + `Set Properties[]` / `Add Property Item After` +
  `PropertyItem.Set Property` / `Set Method`. Write direction per row is NOT covered by
  `Set Properties[]` — the erdosmiller cluster handles it, so v2 keeps the erdosmiller creators
  and adds the class-name properties later for re-typing.

Steps (one script `tools/recipes/build_keystone.py`; discovery D1–D4 results feed the names):
1. Copy OpWire_v1 → OpBuildPN_v0. Confirm pane names of the creator with the reporter.
2. `drop_subvi` the creator at (875, 620) — no deletion yet.
3. Chain B (`Class Name 2`="Diagram", `index 2`) → Index Array(327).element → `Diagram in`.
4. Chain A (`Class Name`=<ref class>, `index`) → Index Array(308).element → `reference`
   (branch=True; Get Outputs stays wired but idle).
5. `Properties` control (copy_into from the creator) → `Properties`; wire-datatype check.
6. `location (0, 0)` (copy_into from OpSubVI_v1) → `location (0, 0)` if on the pane.
7. Error: Get Outputs `error out` → creator `error in`; creator `error out` → sink 369.
8. Verify all endpoints (wire counts +1 each, ExecState), THEN delete Wire Inputs(262),
   `remove_bad_wires`, save.
Acceptance: run against FPTARGET_v0 with `ref class`=Property, `ref index`=0 (a Property node
already present there? if not, against OpFP_v0 copy) → +1 Property whose items are the
requested ones (OpReport + a PropertyItem count); then `Invoke` likewise.

## 9. copy_into is unsafe with library VIs as donors (2026-09-06 04:3x)

Step-by-step replay (T2): substituting `Create Property Node.vi`'s bytes into the Move example's
source file and running OpMoveByLabel CRASHED LabVIEW (COM RPC failure -2147023170, process gone;
the earlier "hangs" of copy_into were the same failure seen through the 180 s watchdog). Byte
swap + revert alone is fine (T1: 0.1 s, no dialog). Rule: copy_into only from claudeDev donors we
built ourselves; never from vi.lib. The Properties control is obtained instead through the VI
method `Create from Data Type` (codex, NI API), reached by the Invoke keystone below.

## Build plan v3 — OpBuildInvoke_v0 first (tools/recipes/build_keystone_invoke.py)

Create Invoke Node.vi on a copy of OpWire_v1: `Diagram in` ← chain B (Class Name 2 = "Diagram");
`reference` ← Open VI Reference `vi reference` (VI-class node); `ID String` ← the existing string
control `Class Name` (method name from Python); error in ← Open VI Reference error out; error out →
Clear Errors sink. No new controls, no copy_into. First method: `Create from Data Type` — then the
Property-node keystone gets its `Properties` control from a data-type variant, not from a copy.

## 10. Plan v3 attempt (2026-09-06 04:3x) — branching by script BREAKS wires; decision needed

OpBuildInvoke_v0 assembly: drop OK; every "branch" wire (IA327.element → Diagram in, Open VI
Reference `vi reference` → reference, control `Class Name` → ID String, Open VI Reference error
out → error in) reported "accepted" (count 26 → 26) but the diagram capture shows red-X broken wires
at the branch points and along the old error chain: erdosmiller `Wire Inputs.vi` does not branch an
already-wired source — it attaches a second source ("more than one data source"), exactly the
failure recorded for Wire Indicators on 08-29. 3/3 today. The op was discarded unsaved.

Consequence: every keystone variant needs at least one BRANCH (the single Open VI Reference output
must feed both the Traverse and the creator), and the fleet has no native `Diagram.Connect Wire`
op — building one needs the branch. This is the verified-unreachable residue: **branch wiring by GUI
once per op build** (lvclick coordinates from COM + registered terminal offsets, reverse-direction
click on the existing wire, verified by ExecState 1 / wire count), after which the finished op makes
its own kind of node without clicks. Awaiting the user's approval of that exception.

## 11. Plan v4 (2026-09-06 05:1x) — the branch failures were TYPE failures

Five GUI branch attempts onto the Index Array 327 `element` wire all produced a dashed wire with a
red X, while the same click technique attached `reference` (VI ref → Generic) and `ID String`
(string) as solid wires. Pixel map: the click landed on the teal wire (x=673, y 493–508; the error
wire is at y=511, 3+ px away). Explanation that fits all five: `Index Array.element` carries a
GENERIC GObject refnum and `Create Invoke Node.vi`'s `Diagram in` is Diagram-typed — LabVIEW
refuses the coercion. OpSubVI_v1 already converts with `To More Specific Class` + a Diagram class
constant before `Create SubVI.vi`'s `Diagram in`, which is why plan v1 chose it. Plan v4 therefore
builds on OpSubVI_v1: branch `Diagram in` from the typed wire after To More Specific Class, branch
`reference` from Open VI Reference, and wire `ID String` by script from a string control copied
from a claudeDev donor (`copy_into(OpWire_v1, "Class Name 2")` — claudeDev donors are safe; the
vi.lib donor crashed LabVIEW). `Create SubVI.vi` stays in place; v0 tolerates its error.

## 12. MILESTONE 2026-09-06 05:53 — OpBuildInvoke_v0.vi exists and works (v0)

Built on OpSubVI_v1: `copy_into(OpWire_v1, "Class Name 2")` gave a string control (claudeDev donor,
no crash); `drop_subvi(Create Invoke Node.vi)` at (900,640); `wire_control(["Class Name 2"] →
"ID String")` by script (fresh wire); **one GUI branch wire** (approved exception) from the creator's
`Diagram in` (screen 910,679) to the To-More-Specific-Class Diagram wire (702,420) → ExecState 1 →
COM save (10,500 B). The reference branch from the VI refnum broke the VI (VI ref is not a GObject
ref) and was removed: v0 creates the node WITHOUT class context.
Functional test: run on a scratch copy of GUIBENCH_v0 with Class Name="Diagram", index=0,
Class Name 2="Create from Data Type" → **+1 Invoke node (uid 622) on the target** (COM). Known v0
limits: node lands at (0,0) (creator `location` unwired); node class/method not verified by the
reporter (no method field); the skeleton's second Open VI Reference raises an error-7 dialog when
`vi path 2` is empty (watchdog dismisses it) and Create SubVI.vi would drop a subVI if given a real
path. Bootstrap GUI acts: 7 wire attempts (1 successful branch + 5 type/snap failures + 1 removed),
all in tools/gui_actions.log with Evidence "keystone bootstrap (user: 예외 허용 2026-09-06)".
Next (v1): wire `location` from the existing location control wire (GUI branch), take `reference`
from a Traverse-found GObject (chain A) so the node class follows a real object, neutralise Create
SubVI / the second Open VI Reference, then the Property-node twin.

### v1 step 1 done (06:1x): `location` wired — node lands where asked
GUI branch from the creator's `location (0, 0)` (top-centre terminal, screen 927,676) onto the
location control's wire (vertical brown segment x=941, y 489-540 → click 941,515). ExecState stayed
1, COM save 10,652 B. Test: location (500,600) → new Invoke uid 622 at exactly (500,600).

## 13. v1 findings (2026-09-06 13:1x) and plan v5

Done in v1: `location` wired (node lands at the requested point), `reference` wired from the typed
Diagram wire, `Class Name` wired (it IS on the pane). Still untyped nodes because (a) the class
string must be `VI Server:<Class>` and the op currently feeds the creator's `Class Name` from the
SAME control as the Traverse class (`"Diagram"` vs `"VI Server:Diagram"` — conflict), and (b) the
method needs the Unique ID (`6349C0x`), not a display name (see NAMES.md).

Plan v5 (next session, scripted except the approved branch wires):
1. Skeleton = OpWire_v1 (two Traverse chains) + the typed-Diagram conversion copied from OpSubVI_v1
   is NOT available by script → instead keep OpSubVI_v1 as skeleton and add a THIRD string control
   (`copy_into(OpWire_v1, "Class Name 2")` again → LabVIEW renames to `Class Name 3`) for the
   creator's `Class Name`; delete the shared branch (click the pink wire → Delete; Ctrl+B) and re-wire
   Traverse ← `Class Name`, creator ← `Class Name 3` by script (fresh wires).
2. `reference` from the typed Diagram wire limits the op to Diagram-class nodes whose methods take
   the diagram as the object; for Terminal/Control-class nodes the op needs a second Traverse (OpWire
   skeleton) — build that variant once this one is verified.
3. Method IDs: extend OpReport with `All Supported Methods` (or a one-off op) so Python can map
   display name → ID; until then use the two known IDs.
4. Neutralise Create SubVI / Open VI Reference 2: scripted `delete_by_label` test result below.

Scripted delete test (13:2x): `delete_by_label(scratch, "Create SubVI.vi")` reached the Move-example
substitution protocol and died in its `gui_save` (Ctrl+S is a no-op for scripted edits — see §9/§11);
the runner killed it at the deadline; example files verified pristine afterwards. Conclusion: the
substitution protocol (copy_into / delete_by_label / move_by_label) is unusable until it stops relying
on the editor's Save; fix = save the substituted example via COM while it is NOT broken (copy a
control, not a primitive) or rebuild those ops on OpBuild* keystones. Deleting nodes stays GUI-only
(click + Delete + Ctrl+B) for now — one act per node, logged.

## 14. MILESTONE 2026-09-06 14:0x — OpBuildInvoke_v0 creates a TYPED Invoke node with its method

Test t8: `Class Name 3`="VI Server:Terminal", `Class Name 2`(ID String)="6349C03", `location`
(500,600), reference UNWIRED → a **Term / Connect Wire** node with its parameter rows (Wire Source,
Auto Wire?) at (487,600) on the scratch target. Root cause of every earlier "App / Method": with a
VALID `reference`, the erdosmiller creator takes the bare class name from the referenced object
("Diagram") and writes it to Method Class Name, which LabVIEW 2026 rejects silently (needs the
"VI Server:" prefix); only with `reference` unwired does it use the caller's Class Name string.
So: keep `reference` unwired; type by string; pass the method's Unique ID.

Op contract (front panel → Python): `vi path` (target), `Class Name`="Diagram" + `index` (which
diagram, via Traverse → To More Specific Class), `location (0, 0)`, `Class Name 3` = node class
("VI Server:<Class>"), `Class Name 2` = method Unique ID, `vi path 2` = "" (Create SubVI branch
errors 7 → one auto-error dialog per run, dismissed by gscript's watchdog; removing that branch
needs node deletion = GUI, not yet approved). Saved 10,752 B, ExecState 1.
GUI acts in the whole bootstrap: ~12 wire attempts/segment deletes, all logged with Evidence.

### Step 1a done (14:2x): Create SubVI + second Open VI Reference deleted (GUI, approved)
Two node deletes + Ctrl+B; ExecState 1; saved 9,952 B (backup `OpBuildInvoke_v0.vi.bak_before_delete`).
No error-7 dialog any more; the op's `error out` indicator is unwired (always clean) — creator errors
surface only as auto-error dialogs (watchdog) until an indicator is attached by a future op.

## 15. MILESTONE 2026-09-06 17:2x — OpBuildPN_v0.vi: typed Property Nodes from Python

Built from a copy of the cleaned OpBuildInvoke_v0: GUI delete of the Invoke creator (approved),
`drop_subvi(Create Property Node.vi)`, Diagram in ← To More Specific Class output and location ←
control BY SCRIPT (both sources were free after the delete — no branch needed), `Class Name 3` →
creator `Class Name` by script (on the pane), and the array-of-cluster `Properties` control created
with the terminal's context menu Create > Control (one GUI act; geometry registered). ExecState 1,
saved 10,764 B. Test: class "VI Server:GObject", Properties [("632A800", False)], location (500,600)
→ **GObj / Position** node at (497,600) in 0.05 s, no dialog. Wrapper `gscript.build_property`.
Step 1b (method/property inventory op) is deferred: reading `All Supported Methods` needs a
class-typed reference (To More Specific Class) that the fleet cannot place yet; the interim inventory
is docs/vi-server-ids.json fed by peer lookups of labviewwiki. Step 3 next: OpDelete_v0 =
build_invoke("VI Server:Generic", Generic.Delete 6327400) on a Traverse output (GObject → Generic
upcast is legal) to retire delete_by_label.

## 16. Step 3a done (17:4x) — OpDelete_v0: scripted node deletion, built WITH the keystone

Copy of OpBuildInvoke_v0 → GUI delete of the creator and of To More Specific Class (approved) →
`build_invoke(op, "VI Server:Generic", "6327400", (900,640))` put a Delete node on the op's own
diagram → `wire(IndexArray.element → reference)` by script (LabVIEW re-typed the node to GObj from
the wire — a GObject wire into a Generic-class node is a legal upcast) → ExecState 1, saved 9,299 B.
Test: `delete_object(scratch, "IndexArray", 0)` → IndexArray 3 → 2 (uid 534 gone), attached wires
left broken (target ExecState 0 until remove_bad_wires). One auto-error dialog appeared (dismissed by
the watchdog; the Delete node's error out is unwired) — same v0 limitation as the other ops.
`delete_by_label` and the substitution protocol are retired for deletion.

## 17. Step 3b plan — Move and Connect Wire ops need TWO references

`GObject.Move` (632A400: owner + position) and `Terminal.Connect Wire` (6349C03: source terminal)
each need a second reference on the op diagram: a second Traverse chain (OpWire_v1 has two) and,
for Connect Wire, terminal refs via `Node.Terminals[]` (6359000, a Property node the PN keystone can
now build) indexed by terminal position. Design: OpConnect_v0 = OpWire_v1 skeleton (chain A: node
A/index → PN Terminals[] → Index Array[term i] ; chain B: node B → Terminals[] → Index Array[term j])
→ build_invoke("VI Server:Terminal", "6349C03") with `reference` ← term i and `Wire Source` ← term j.
Blocking detail: the PN's reference input needs a Terminal/Node-typed wire; chain outputs are GObject
(Generic) → LabVIEW re-types a GObject-class PN, so build the PN as "VI Server:Node" and check the
wire is accepted (Node ⊂ GObject: a GObject wire into a Node PN is a downcast → probably refused;
then Traverse must be asked for the concrete class, e.g. "SubVI", whose refs are typed... they are
still delivered as GObject array elements). Test first on a scratch op before committing.

## 18. Step 3b probe (17:5x) — typed references are the next bootstrap

`build_property(scratch, "VI Server:Node", [("6359000", False)])` made a Node PN, but wiring the
Traverse/Index Array output (GObject-typed) into its reference re-typed the PN to **GObj** and the
`Terms[]` item became invalid (ExecState 0). So every op that needs a class-specific reference
(Node.Terminals[] for Connect Wire, GObject.Move's owner, ClassSpecifierConstant.Class Name...)
needs `To More Specific Class` with a class constant of that class on its diagram. The fleet cannot
place that pair by script (primitive + constant), but every op copy already carries one
(TMSC + "Diagram" constant from OpSubVI_v1). Bootstrap per class = change that constant's class
ONCE by GUI (the class constant's own menu), then copies of that op carry a typed source. Do this
for `Node` and `Terminal` first (Connect Wire), `GObject` for Move. After that, OpConnect_v0 /
OpMove_v0 are scripted builds (two Traverse chains = OpWire_v1 skeleton + the typed pair).

## 19. Step 1a closed (2026-09-06 18:2x) — the OpDelete dialog was a stale in-memory VI

The Function deleted on the copy (uid 683 at (653,279)) WAS the To More Specific Class node: a fresh
copy of the on-disk `OpDelete_v0.vi` has Functions [43] only and ExecState 1. The dialog kept appearing
because LabVIEW still held the previous OpDelete_v0 in memory (its panel was open) and both `op()` runs
and `report()` used that instance — `report(OP,'Function')` listed 683 while the file no longer had it.
After `close_panel(OP)` + a fresh process: `delete_object(scratch,'IndexArray',0)` → uid gone in 0.10 s,
no dialog. **Rule:** after replacing an op's file on disk, close its panel (unload) before using it; a
reporter read of a VI that is open in LabVIEW describes the in-memory version, not the file.

## 20. Step 3b — script-only typed references (2026-09-06 18:3x)

Probe on a scratch copy of OpBuildPN_v0: `build_property(S,'VI Server:Diagram',[('6375809',False)])` (AbstractDiagram.Nodes[])
then `wire(TMSC.'specific class reference' → PN.reference, branch)` → accepted (wire count unchanged = branch),
ExecState 1 — the PN keeps its Diagram class with a Diagram-typed wire. So typed references come from the
ladder Diagram → Nodes[] → Index Array → Node → Terminals[] → Index Array → Terminal, all built with
build_property + wire + an Index Array; the class-constant GUI bootstrap of §18 is NOT needed for Move /
Connect Wire. erdosmiller `Create To More Specific Class.vi` builds its nodes via New VI Object (its style
ring list is in the file; `target class` reads as int over COM) — codex asked to attack the claim
(archive/peer/…tmsc-class-bootstrap-attack). Open question: the Index Array on the op diagram — reuse
IA308 by rewiring (delete the Traverse→IA wire, wire Nodes[]→array) or `Create Index Array.vi`.

## 21. MILESTONE 2026-09-06 18:4x — OpMove_v0: the first op built with ZERO GUI acts

`tools/recipes/build_opmove.py` (one batch, 3 s): copy OpDelete_v0 → `delete_object(op,"Invoke",0)` (the
Delete node) → `delete_object(op,"Wire",i)` on the one wire right of IA308 (the dangling one; ExecState
0→1 — **broken wires are deletable as Wire objects, no Ctrl+B needed**) → `build_invoke("VI Server:GObject",
"632A400",(900,640))` → `wire(IA308.element → reference)` → `wire_control(["location (0, 0)"] → ["position"])`
→ ExecState 1 → COM save (9,337 B). Test: `move_object(scratch,"IndexArray",0,(1200,900))` → reporter
shows (1200,900), 0.04 s, target ExecState unchanged. Wrapper `gscript.move_object`. `owner` unwired.
Also learned: `remove_bad_wires` (menu recipe) silently did nothing — its lv_gui clicks left no entry in
tools/gui_actions.log (gate refusal swallowed by `_lv_gui`); superseded by wire deletion for this use.
Next (§20 ladder): OpBuildIA_v0 (`Create Index Array.vi`, `array` unwired) → OpCreateControl_v0
(Nodes[]→IA→Terminals[]→IA→Terminal.Create Control) → OpConnect_v0 (Terminal.Connect Wire by indices).

## 22. Peer review of the ladder (codex, 2026-09-06 18:5x — archive/peer/2026-09-06-connect-ladder-plan-attack.md)

- `AbstractDiagram.Nodes[]` order is UNDOCUMENTED and need not match Traverse order → never address a node by a
  Nodes[] index computed elsewhere; map UID ↔ index at call time (a Nodes[]-based reporter with GObject.UID), or
  address through Traverse (which our reporter already uses) wherever a Generic ref suffices.
- `Node.Terminals[]` index = the terminal index Context Help shows; Index Array has its own `Array Input Terminal`,
  `Index Terminals[][]`, `Output Terminals` properties (safer than raw indices on growable nodes).
- `Terminal.Connect Wire` (6349C03): invoke on the SINK terminal; params `Wire Source` (required; Terminal or Node),
  `Auto Wire? (T)`, `Wiring Specs`, `Auto Route? (F)`. Branching from an already-wired source: unverified → test.
- `Create Index Array.vi` `array`: resolved by test, not by docs — a GObject-typed wire is accepted (ExecState 1),
  `Diagram in` is REQUIRED (ExecState 0 when unwired). Library VIs that take Generic refs and downcast
  internally are typed gateways: they let a Traverse-addressed object reach a class-specific method.

## 23. Typed gateways in the library (2026-09-06 19:0x) — the ladder may not be needed at all

Probing erdosmiller VIs over COM (control names + types, read-only): `Conditionally Connect Wire.vi` has
`Terminal in` (refnum), `Wire Source` (refnum), error in/out — a two-reference Connect Wire whose inputs,
like `Create Index Array.vi`'s `array`, are expected to accept Generic/GObject wires (the library
downcasts inside). If so, OpConnect_v0 = OpWire_v1 skeleton (two Traverse chains, class "Terminal",
index a / index b → IA308.element / IA327.element) → `Terminal in` / `Wire Source`: no typed reference,
no Nodes[] ordering risk (codex §22), addressing by the reporter's Traverse order which Python already
uses. Gemini timed out (180 s) on the VI.Block Diagram ID; Claude fetched labviewwiki VI_class: Block
Diagram = 23C, Front Panel = 23D, Create from Data Type = 49D, Block Diagram:Remove Bad Wires = 410
(short IDs as printed for the VI class; registered in docs/vi-server-ids.json, verified only when a
PN built from them is legal).

## 24. OpBuildIA_v0 done (19:2x) and the gateway idea half-refuted (19:4x)

**OpBuildIA_v0** (`tools/recipes/build_opbuildia.py`, zero GUI): copy OpBuildPN_v0 → delete creator + 4 wires →
delete TMSC + class constant + wires → drop `Create Index Array.vi` → `build_property("VI Server:VI",[("23C",F)])`
wired from Open VI Reference `vi reference` (branch) → PN output **`Diagram`** (the property's SHORT name is the
terminal name; `Block Diagram` → error 5001) → `Diagram in`; IA308.element → `array`; location control →
location; `error out` → Clear Errors (added after the first test popped an 8 s dialog). Saved 11,136 B,
ExecState 1. Functional: +1 IndexArray at the requested spot every run; the library's `array` wiring failed
with error 1304 (`Index Count` out of bounds) for every terminal tried (IA inputs, Traverse inputs), so the
node arrives UNWIRED — wrapper `gscript.build_index_array(target, location)`; wire it afterwards.
**VI-class IDs are short** (23C/23D/49D/410 as printed on labviewwiki VI_class) and work as-is in
`Set Properties[]`.

**Conditionally Connect Wire.vi** (`Terminal in`, `Wire Source`, `Terminal out`): wiring IA.element (GObject)
into `Terminal in` / `Wire Source` leaves the op broken; deleting the three new wires one by one never
restores ExecState 1 (the inputs are required) → its inputs are Terminal-TYPED, unlike `Create Index
Array.vi`'s `array`. So the ladder IS needed for Connect Wire and Create Control — and it is now buildable:
VI → `Block Diagram` PN → `Nodes[]` PN → Index Array (OpBuildIA or the skeleton's IA308/IA327, rewired by
name) → `Terminals[]` PN (class Node, fed by a Node-typed IA element) → Index Array → Terminal-typed
element → `Terminal.Create Control` / `Terminal.Connect Wire` invokes. `tools/recipes/build_opcreatecontrol.py`
implements it on the OpWire_v1 skeleton (strip everything except wires 106/1066/1108, then 3 PNs + 1 Invoke).
Strip lesson: dangling wires are found by uid in a fixed skeleton; positional rules missed wires whose
bounding box starts far from the deleted node (error-out wire at (16,91); Traverse error wires 2 px from
the refs wires).

## 25. MILESTONE 2026-09-06 19:5x — OpCreateControl_v0: the typed-reference ladder works, zero GUI

`tools/recipes/build_opcreatecontrol.py` (35 s incl. test): OpWire_v1 → delete 4 SubVIs, 2 TMSCs, 2 class
constants and every wire except uids 106/1066/1108 → `build_property(VI, Block Diagram 23C)` ← Open VI Reference
`vi reference` → `build_property(Diagram, Nodes[] 6375809)` ← PN1 `Diagram` → IA308.array ← `Nodes[]`
→ `build_property(Node, Terminals[] 6359000)` ← IA308.element (Node-typed, accepted) → IA327.array ← `Terms[]`
→ `build_invoke(Terminal, Create Control 6349C01)` ← IA327.element (Terminal-typed, accepted) → error out →
Clear Errors. ExecState 1, saved 9,322 B. Test on a GUIBENCH_v0 copy, terminal 1 of node n for n = 0..15:
10 of 14 nodes got a new wired ControlTerminal (0.13–0.23 s each, no dialog); nodes whose terminal 1 was
already wired or absent gave none; n ≥ 14 → error dialog (out of range). Target ExecState stayed 1.
**Nodes[] order = CREATION order** (the uid-rank shortcut broke at 20:0x: LabVIEW reused uids 90/98 for
new nodes, which still went to the END of Nodes[]; `gscript.node_rank` kept only as a warning — pass explicit
indices; nodes just created are count(Node)-k). Wrapper
`gscript.create_control(target, node_uid, terminal_index)`. This retires copy_into for controls.
OpConnect_v0 follows the same ladder twice (`tools/recipes/build_opconnect.py`), its extra index controls
minted by OpCreateControl_v0 on the op itself.

## 26. OpConnect_v0 built (20:0x) and OpCreateIndicator_v0 (20:2x) — the label problem

`build_opconnect.py`: OpCreateControl_v0 copy -> strip invoke -> ladder B (build_index_array x2 + a Node.Terminals[]
PN, Nodes[] branched) -> OpCreateControl_v0 on the op itself for the two new IA index inputs ->
build_invoke(Terminal, Connect Wire 6349C03) <- IA327.element (sink) / IAb2.element (Wire Source) -> Clear
Errors. ExecState 1, saved 10,020 B, zero GUI. **Untested**: LabVIEW names a created control after its terminal
and COM SetControlValue needs that label; terminal 1 of an Index Array is `element` (an indicator got made),
and the labels for terminals 0/2/3 matched none of ~50 guesses; `Set Name.vi` is not the label (NAMES.md).
Fix: **OpCreateControl_v1 reports the label**: Create Control's `Create Control` output (Control ref) -> PN
Control.Label (6332005, Text refnum) -> PN Text.Text (632D800) -> indicator 'Text' on the op, placed by
**OpCreateIndicator_v0** (Terminal.Create Indicator 6349C02 on the same ladder; built 20:2x, 9,264 B; test:
indicators on 7 of 8 terminals of Traverse 124, 0.15 s each). Then every created control is addressable.

## 27. MILESTONE 2026-09-06 20:3x — OpCreateControl_v1 reports labels; OpCreateIndicator_v0

`build_opcreatecontrol_v1.py`: OpCreateControl_v0 + PN Control.Label (6332005) <- Invoke `Create Control` output
+ PN Text.Text (632D800) <- PN4 `Label` + an indicator on PN5's output made by OpCreateIndicator_v0 on the op
itself (discovery sweep: a one-property PN's Terminals[] = reference, reference out, error in, error out,
property output = index 4). Saved 9,774 B, ExecState 1. Test on GUIBENCH_v0 copy, node 11 (IA534): terminal 2
-> control labelled `index 3`, terminal 0 -> `array`, terminal 1 -> `element` (so an Index Array's Terminals[]
= array 0, element 1, index 2). Wrappers: `gscript.create_control(target, node_index, terminal_index)` ->
(new dicts, label); `gscript.create_indicator(...)`. The label problem of §26 is solved: every control the
toolkit creates comes back with the name COM must use.

## 28. MILESTONE 2026-09-06 21:0x — OpConnect_v0 verified; steps 1–3 complete with ZERO GUI acts in 3b

`gscript.connect_terminals(target, sink_node, sink_term, src_node, src_term)` (OpConnect_v0, 9,980 B, 0.04 s).
Verification (fresh scratch each try, `build_index_array` at (1300,700) as the unwired sink, ExecState 0):
source = Traverse 124 terminal 2 (`GObject Refs`) → **ExecState 0→1**, wire count unchanged (the already-wired
source was BRANCHED — same signature as erdosmiller branching); terminals 1/3/4/5/6 → a new broken wire (type
mismatch, ExecState stays 0); terminal 7 → a wire moved. Earlier "no wire, VI breaks" runs targeted IA534,
whose array input is already wired in GUIBENCH_v0: **Connect Wire on a wired sink re-routes and breaks** —
only wire unwired sinks. Index Array Terminals[]: array 0, element 1, index 2; Traverse for GObjects: 2 =
GObject Refs.

The step-3 replacement set (all built by script, none by clicking): delete_object (OpDelete_v0) · move_object
(OpMove_v0) · build_index_array (OpBuildIA_v0) · create_control (OpCreateControl_v1, returns the label) ·
create_indicator (OpCreateIndicator_v0) · connect_terminals (OpConnect_v0) — on top of build_invoke /
build_property (§14/§15). copy_into / move_by_label / delete_by_label are retired. Open: a Nodes[]-order reporter
(uid ↔ Nodes[] index) so callers need not track creation order; error visibility (creator errors sink into
Clear Errors — read Error List or add an error indicator via create_indicator); step 1b inventory op.

## 29. 2026-09-07 02:2x — OpFPLabels_v0 / OpNodeInfo_v0: names without GUI (built for the fixture acceptance)

Both from the OpWire_v1 skeleton, zero GUI, first build each (recipes build_opfplabels.py / build_opnodeinfo.py):
- **OpFPLabels_v0** (9,485 B): VI → Front Panel (23D, output `Panel`) → Panel.Controls[] (6348801, output
  `Controls[]`, tabbing order) → IA → Control [Label 6332005, Indicator 6332007] → Text.Text → indicators
  `Text` / `Indicator` (a 2-property PN: outputs are terminals 4 and 5). `gscript.fp_labels(vi)` →
  [(i, label, is_indicator)]. This answers "what are this VI's controls" for ANY VI headlessly.
- **OpNodeInfo_v0** (9,401 B): VI → Block Diagram → Nodes[] → IA → Node [Label 6359001, Style 6359009] →
  Text.Text → `Text` / `Style`. `gscript.node_info(vi)` → [(i, style, label)]. **Node.Style returns the node
  TYPE NAME** ('Read from Binary File', 'Index Array', 'File Dialog', 'For Loop', 'Unbundle By Name'…) — the
  same vocabulary as New VI Object's style ring. Two consequences: primitives on any diagram are nameable
  (the "which node is the TMSC" problem of §19 is gone), and the style strings are candidates for a scripted
  primitive dropper (Diagram.New VI Object with the style NAME) — to be tested; that would shrink the
  verified-impossible list to one entry.
First use: `Load and prep N cal images.vi` (lab loader) has an all-indicator front panel (cal-file refnum,
# slices in stack, # of beads, x,y,(blankz) array, exp/ref array, cross size, Array of cal clusters) and 18
top-level nodes, node 17 = File Dialog → node 1 = Read from Binary File; the harness copy replaces the dialog
with a path control (create_control on the file input).

## 30. RECOVERY packet 2026-09-07 03:5x — OpReport hangs on fresh OpBuildPN_v0 copies (6/6)

- **Prediction:** copy OpBuildPN_v0 → OpNetInfo_v0, open panel, `report(OP,'SubVI')` returns in < 1 s (it did for
  OpBuildIA_v0 at 19:1x from the same source).
- **Observation:** six attempts, six COM `Run` hangs (60–180 s, no modal dialog, LabVIEW UI responsive, ping 0 ms);
  twice the first report on the copy hung, once the report right after deleting the creator SubVI, once
  OpenFrontPanel itself (180 s). A LabVIEW restart (which after a forced kill shows a small UNTITLED modal that blocks
  COM until dismissed — now handled by tools/lv_restart.py) did not change it. Other ops (HARNESS builds,
  OpFPLabels/OpNodeInfo/OpRemoveBadWires from the OpWire_v1 skeleton, reports on v3/OpMove) work in the same instance.
- **Evidence:** tools/bench/fixture_probe.log 03:0x–03:5x; screenshots gscript_hang_1788718113/…877/…002/…149/…211/…358/…420/…1060.
- **Competing explanations:** (a) the copied VI (lvlib member call + array-of-cluster control) puts Traverse into a wait;
  (b) instance state after restart (first-load of LV-Scripting.lvlib > watchdog); (c) the OpReport op itself wedged.
- **Discriminating tests (T1/T2, running):** report on a fresh OpBuildPN copy with the panel closed, then opened;
  a report on OpMove_v0 already answered in 0.0 s (rules out (c) globally). Peer review: codex
  archive/peer/2026-09-07-com-run-hang-opbuildpn-copy.md.
- **Route around it:** OpNetInfo needs a Diagram-typed reference for sub-diagrams; the only scripted source is the
  TMSC(Diagram) chain that lives in the OpBuildPN/OpBuildInvoke lineage. Alternative under test: keep the creator
  (no deletion) and neutralise it with an error-in control set TRUE from Python.
- **T1 result (04:08):** `report()` on a fresh copy of OpBuildPN_v0 (SCRATCH_pnprobe.vi, panel NEVER opened) hung →
  the copied target triggers Traverse; the instance is otherwise fine. OpBuildPN_v0.vi itself is unchanged since
  17:15 (10,764 B), so the difference from the 19:1x success is instance state (OpBuildPN_v0 loaded as an op with
  its panel open while a same-content copy is traversed). Codex (archive/peer/2026-09-07-com-run-hang-opbuildpn-copy.md):
  Run(True) waits for UI-idle; candidates = non-reentrant reporter reserved by a killed client, Traverse waiting on the
  root loop, dependency resolution of the copy; recommended split tests (original vs copy vs Nodes[]-based op) and
  Run(False)+Abort() on the SAME reference as the recoverable pattern. Next: split tests T4–T7.
- **T0 after the killed batch (04:2x): even `report(OpMove_v0)` hangs** → a client killed mid-Run leaves the
  non-reentrant OpReport_v3 reserved/running and every later Run waits (codex's first candidate; CLAUDE.md §3
  "a killed client keeps its references alive"). So two distinct facts: (1) the fresh OpBuildPN copy trips the
  reporter; (2) once a client is killed during that hang, the instance is poisoned until LabVIEW restarts.
  Rule for the runner: after any BGRUN TIMEOUT that killed a COM client, restart LabVIEW before the next batch.
- **Split tests after a clean restart (04:3x):** T0 report(OpMove_v0) OK 0.3 s; T4 report(OpBuildPN_v0 ORIGINAL) OK
  0.5 s; **T5 node_info(fresh copy of OpBuildPN_v0) CRASHED LabVIEW after 8.5 s** (RPC -2147023170; every later call
  -2147023174 = server gone). So the copy is toxic to BOTH readers (Traverse hangs, Nodes[] crashes) while the
  original is fine — the earlier "startup modal after a forced kill" was crash-recovery residue of the same thing.
  Hypothesis: loading a same-content copy of a VI that is already in memory as an op (OpBuildPN_v0, panel open,
  FP values changed by SetControlValue) is the trigger; test next on the OpBuildInvoke_v0 lineage (its copies made
  OpDelete_v0 at 17:2x without incident).
- **04:4x verdict:** `node_info(OpBuildInvoke_v0 ORIGINAL)` crashes LabVIEW in 8.4 s while `report()` (Traverse) on
  a copy of the same VI returns in 0.6 s → the crash is in the Nodes[] reader (OpNodeInfo: Node.Label → Text.Text and
  Node.Style) on a node type present in OpBuildInvoke/OpBuildPN but not in v3's top level / Load and prep / OpMove
  (candidates: To More Specific Class, ClassSpecifierConstant). **Never run node_info on a VI containing a TMSC or
  class constant until the crashing property is isolated.** OpNetInfo is rebuilt WITHOUT Label/Style: node identity **2026-09-14: `Node.Label` alone (no Style) read all 626 nodes of the main VI headless with no crash — OpNodeLabels_v0; the suspect narrows to `Node.Style` or the TMSC/class-constant node types.**
  = GObject.UID (632A813), matched to the Traverse reporter's (class, uid, pos). Source lineage: OpBuildInvoke_v0
  (copies traverse fine).
- **04:5x ROOT CAUSE of the post-restart hangs: my own `lv_gui -Action dismiss` at startup.** restart_probe.py:
  restart, touch nothing, wait — `dialogs` keeps reporting the same small untitled window for 60 s (it is LabVIEW's
  startup/Getting-Started child, not a modal), and then report(copy) 1.0 s, **open_panel(copy) 0.1 s**, report 0.1 s
  all fine. Every instance where I had posted WM_CLOSE to that window hung on the next OpenFrontPanel/Run. Two
  real findings survive: (A) node_info (Node.Label/Style) CRASHES on OpBuildInvoke/OpBuildPN-type VIs; (B) a client
  killed mid-Run leaves OpReport reserved → restart. The 03:0x first hang remains unexplained (possibly (A) in
  progress). tools/lv_restart.py now waits 45 s and dismisses nothing.
- **05:2x:** clean restart (no dismiss) → copy of OpBuildInvoke_v0 loads via reporter (0.x s) and OpenFrontPanel
  returns; then **`delete_object` of the erdosmiller creator SubVI node (Create Invoke Node.vi) hangs 120 s** —
  the same op deleted six nodes of an FPTARGET copy, an Invoke on OpMove/OpCreateIndicator builds and the File
  Dialog express VI of the loader today without trouble. Deleting an lvlib-member subVI node is the specific
  trigger tonight (it worked once at 19:1x). Workaround for OpNetInfo: keep the creator and neutralise it with an
  `error in (no error)` control set TRUE from Python (erdosmiller VIs pass errors through).

## 31. 2026-09-07 06:0x–07:0x — OpNetInfo_v1 built, OpSetAutoErr_v0 built, still no loop map

- **OpNetInfo_v1.vi** (12,880 B, ExecState 1; recipe build_opnetinfo.py, OpBuildInvoke lineage): loaded via the
  reporter before OpenFrontPanel (the copy-then-open order matters tonight), creator KEPT and neutralised by a control
  on its `error in` (Nodes[4] terminal 9; the first sweep hit Open VI Reference's `error in (no error)` — Nodes[0]
  t4 — and poisoned the whole chain). Chain: Traverse(Diagram,index)→TMSC→Nodes[]→IA[index 2]→Node[UID] and
  Terminals[]→IA[index 3]→Terminal[Name, Connected Wire]→Wire[UID→'UID 2', Is Broken?]→Clear Errors.
  Open problem: with the creator's error injected, its unwired `error out` pops the auto-error dialog, and every
  attempt to wire that `error out` anywhere creates a BROKEN wire (type-refused; remove_bad_wires clears it) —
  Get Outputs apparently returns a different terminal for the creator's 'error out'.
- **OpSetAutoErr_v0.vi** (8,815 B, first build): VI.'Automatic Error Handling' (242) write from a boolean
  control — `gscript.set_auto_error_handling(vi, False)` silences auto-error dialogs of an op.
- Applying it to OpNetInfo_v1 and running the self-test HUNG inside OpNetInfo_v1's own run (window title lost
  "Front Panel" = running; no dialog; batch killed at 07:0x, LabVIEW restarted). Unresolved: whether the hang is
  the injected-error path inside the erdosmiller creator, or the open Block Diagram windows the create_* ops leave
  behind (H5-type UI-idle wait). Next: test OpNetInfo_v1 with the creator's error control FALSE (it will then
  create one stray Invoke per run on the TARGET — acceptable only on a scratch copy) to separate the two.
- The v3 loop map (tools/bench/v3_netmap.py) therefore has not run yet; the fix for v3 (two auto-indexed tunnels
  from Decimate outputs 1/2 into the kernel's starting x/y) waits on a sub-diagram-capable wire op
  (build_opconnect2.py is written, untested).

## 32. 2026-09-07 13:2x — OpNetInfo_v1 works on a clean instance; v3's defect read headlessly

Single-shot test on a fresh instance with no windows open: OpNetInfo_v1 (creator error injected, auto error
handling off) answers in 0.10 s — the 06:5x hang was instance state (open BD windows / poisoned run), not the op.
`net_map(PARALLEL_kernel_v3, diagram 1)` (tools/bench/v3_netmap.py, 3 s): the loop diagram lists the kernel
SubVI uid 3449: **t0 'starting x 1' UNWIRED, t1 'starting y 1' UNWIRED**, t2 'Calibration cluster 1' and
t3 'Bead 1 is good? in' wired to tunnels. (Terminal listing stopped at t3 — the out-of-range guard fired on an
unnamed/unwired read; refine later.) This is the wiring defect the harness sensitivity test predicted.
Fix = OpConnect2 (build_opconnect2.py): sink = diagram 1 node 0 terminals 0/1, source = top-level Decimate node
terminals 1/2 ('decimated array' outputs), then set_index_mode(1) on the two tunnels LabVIEW creates.

## 33. 2026-09-07 13:5x — the creator cannot be neutralised, only cleaned up after

OpNetInfo_v1 / OpConnect2_v0 keep the erdosmiller `Create Invoke Node.vi` (Delete on that node returns "0 gone";
its real `error in (no error)` is fed by the chain, so no control can be put on it; empty class/ID strings still
make it drop an untyped Invoke node — 1,403 junk nodes on a scratch in one net_map). Auto error handling is OFF on
both ops (OpSetAutoErr_v0), so the creator's failures are silent. **Protocol:** every use of these ops on a target
is followed by `new_since(target,"Invoke")` → delete each junk Invoke → Remove Bad Wires (fix_v3_starting_xy.py
`purge_junk`). A creator-free TMSC(Diagram) skeleton remains the proper fix (needs a working Delete on that node
or a fresh skeleton built from OpSubVI lineage on a clean instance).

## 34. MILESTONE 2026-09-07 14:1x — PARALLEL_kernel_v3 fixed by script and numerically accepted (20/20)

`tools/recipes/fix_v3_starting_xy.py --swap` on a fresh copy of v3: `connect2(FIX, 1, 0, 0, 3, 1)` and
`connect2(FIX, 1, 0, 1, 3, 2)` (Decimate outputs 1/2 → kernel `starting x 1`/`starting y 1` inside the P=4 loop;
LabVIEW made the two tunnels 3969/4010 itself), junk Invokes purged (2), `set_index_mode(…,1)` on both tunnels →
ExecState 1, saved 69,129 B; OpNetInfo read-back: t0 'starting x 1' wire 3958, t1 'starting y 1' wire 4004, not
broken. Swapped over PARALLEL_kernel_v3.vi (backup PARALLEL_kernel_v3.vi.bak_20260907_prefix). Clean restart, then
`run_fixture_compare.py --n=20`: **20/20 frames v3 == four-fold bit-for-bit, both == .tra (dev 0.00000), 44 ms/frame.**
Rule 1a acceptance of the parallel kernel: PASSED on 20 frames; full 10,043-frame run started 14:2x.
- **Full run 14:5x: 10,043/10,043 frames v3 == four-fold; == .tra on 10,017 frames; the last 26 frames (all beads
  lost at the end of the recording) differ from .tra by a one-frame phase of the −1 marking — driver feedback vs
  the main VI's reset state machine, not the kernel (archive/bench-2026-09-07-fixture/REPORT.md). ACCEPTED.**

## 35. 2026-09-07 15:0x–16:1x — the main VI's bead-loss reseed, read headlessly and reproduced

Read on a claudeDev COPY of the working copy (MAINCOPY_readonly.vi; loading it via the reporter takes ~160 s;
report(M,'Node') over 626 nodes took 17 min; the copy now carries junk Invoke nodes from OpNetInfo runs — scratch
only, never the working copy). Kernel call site = SubVI uid 5058 at (3811,1474) in **diagram 43 = the tracking
WhileLoop 637's diagram** (uid 639; also holds the fixture TIFF nodes 22700/22703/23020/23175, save trace 376,
current image number / LastBufferNumber logic, the autofocus Case 10407 driven by bead 2's cal-slice index).
- **Case 5540 (3771,1033)** sits between the loop's shift registers and the kernel: inputs t3 `Bead is good?
  array out` (wire 6041) and t6 `x,y,z array out` (5975) from the previous iteration, outputs t2 (5637 → kernel
  `Bead is good? array in`) and t5 (1681 → kernel `x,y,z array`). Its pass-through frame (diagram 81) has no
  nodes; its reset frame (diagram 82) has one Property Node reading `Value` (uid 4401 → wire 5888) — the
  calibration bead positions — so a reset re-seeds x,y from the cal positions and sets the flags TRUE.
- Selector = `x .or. y?` (10247): y ← Case 10445's output (10573; 10445 is selected by AND(frame counter
  `x = 0?` 3057/2136, NOT 3362) — a periodic auto-reset whose period never elapsed in this recording), x ← wire
  10312 from a loop-border terminal (the "a bead was lost last frame" flag by behaviour: the recording retries a
  lost bead every other frame).
- Driver rule (`run_fixture_compare.py --reseed=main`): if the previous frame's kernel output contains −1, feed
  x,y,z := cal positions and good := all TRUE (pos in cal image passed through); else plain feedback.
- Result on the bead-loss tail (frames 11794–11824): **harness == .tra to 0.0000 on every frame**, including the
  −1 / retry alternation of bead 5 (the other four beads never drop). Full 10,043-frame rerun with the rule: 16:1x.
- **Full rerun 16:3x with `--reseed=main`: 10,043/10,043 identical, worst dev vs .tra 0.00000, 19 ms/frame. No residual.**
