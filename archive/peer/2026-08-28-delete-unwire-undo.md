---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# delete-unwire-undo

- **agent:** codex
- **date:** 2026-08-28
- **outcome:** QUOTA (84s)
- **why asked:** Exact scripting APIs for delete, unwire and undo, before building the ops.
- **verdict:** adopted

## Question

LabVIEW VI Scripting. I need three capabilities on a target VI's block diagram, driven from G code (a scripting VI), and I need exact class/method/property names plus availability. (1) DELETE an object: what is the exact method to remove a GObject (node, constant, terminal) from a diagram? Is it GObject 'Remove' or 'Delete'? Any restriction (e.g. cannot remove while VI running/reserved)? (2) UNWIRE: how do I delete just a wire, or disconnect one terminal? Is deleting the Wire object enough, or is there a Terminal 'Disconnect Wire' / 'Remove Wire' method? Also: is there a scripting equivalent of Edit>Remove Broken Wires? (3) UNDO: NI ships an example called 'Supporting Undo.vi' in the VI Scripting examples. What is the scripting undo API - e.g. VI methods 'Begin Undo Transaction' / 'End Undo Transaction' / 'Undo', or an App-level equivalent? Exact names, how transactions are named/nested, and whether undo works for edits made by scripting from an external COM client. Cite URLs (labviewwiki.org class pages, NI forums, NI docs) for every claim.

## Answer

The relevant APIs are `Generic.Delete`, `Wire.Disconnect Terminal`, `VI.Block Diagram:Remove Bad Wires`, and the VI-level `Transaction:*` methods. There is no GObject method named `Remove`.

### 1. Delete a diagram object

Use an Invoke Node on the object reference:

- Owning class: `Generic`
- Method: `Delete`
- Data/short/long name: `Delete`
- Method ID: `6327400`
- Scope: `VI Scripting`
- Parameters: none
- Effect: deletes the object and invalidates every reference to it
- Run-Time Engine: listed as available
- While target VI is running: **No**

This method is inherited by `GObject`, so it applies to ordinary nodes, constants, and wires. It is not named `GObject.Remove`. [LabVIEW Wiki: Generic.Delete](https://labviewwiki.org/wiki/Generic_class/Delete_method)

Important terminal caveat: although `Terminal` inherits `GObject`, most node terminals are owned structural components of their node. I would not treat `Delete` as a general way to remove one fixed terminal from a primitive or subVI. For growable nodes and structures, use the owning node?셲 specific resize/remove-terminal API. For disconnecting an ordinary terminal, use the wire API below. The public `Terminal` method list contains creation and connection methods but no `Delete Terminal`, `Disconnect Wire`, or `Remove Wire` method. [LabVIEW Wiki: Terminal class](https://labviewwiki.org/wiki/Terminal_class)

The documented availability says `Settable when the VI is running: No`. It does not explicitly document ?쐒eserved for running??on that page. In practice, treat any non-editable target?봱unning, reserved, locked, password-protected, or lacking its diagram?봞s unavailable for diagram mutation, but I do not have a sufficiently specific public NI citation establishing the exact error for every reservation state.

### 2. Unwire

There are two distinct operations.

#### Delete the complete wire

Call inherited:

```text
Wire reference ??Generic.Delete
```

That deletes the entire wire object, and its reference becomes invalid. An NI forum answer to this exact question also says to obtain the wire reference and call `Delete`. [NI Community: Disconnect wire through VI scripting](https://forums.ni.com/t5/LabVIEW/Disconnect-wire-through-VI-scripting/m-p/3046977)

#### Disconnect only one terminal

Call an Invoke Node on the **Wire reference**:

- Owning class: `Wire`
- Method: `Disconnect Terminal`
- Data/short name: `DisconnectTerminal`
- Long name: `Disconnect Terminal`
- Method ID: `6370C0D`
- Required input: `Terminal`
- Scope: `VI Scripting`
- Run-Time Engine: **No**

Thus, it is `Wire.Disconnect Terminal(terminal ref)`, not a Terminal-class `Disconnect Wire` or `Remove Wire` method. [LabVIEW Wiki: Wire.Disconnect Terminal](https://labviewwiki.org/wiki/Wire_class/Disconnect_Terminal_method)

You can obtain the connected terminals through:

- `Wire.Terminals[]` ??property ID `6371003`; first entry is the source when one exists
- `Terminal.Connected Wire` ??property ID `634A000`, read-only

See [Wire.Terminals[]](https://labviewwiki.org/wiki/Wire_class/Terminals%28%29_property) and [Terminal class](https://labviewwiki.org/wiki/Terminal_class).

Disconnecting a terminal may leave a shortened, loose-ended, or broken wire. If you want no residual wire, deleting the complete `Wire` object is simpler.

#### Equivalent of Edit ??Remove Broken Wires

Yes:

- Owning class: `VI`
- Method: `Block Diagram:Remove Bad Wires`
- Data name: `BD.Remove Bad Wires`
- Method ID: `410`
- Scope: `VI Scripting`
- Parameters: none
- Effect: removes all broken wires on that VI?셲 block diagram
- Loads block diagram: yes
- Run-Time Engine: no
- While VI is running: the metadata says **Yes**

[LabVIEW Wiki: VI.Block Diagram:Remove Bad Wires](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)

That is the scripting counterpart of Ctrl+B/Edit ??Remove Broken Wires; NI documents Ctrl+B as deleting all broken wires. [NI: Keyboard Shortcuts](https://www.ni.com/docs/en-AS/bundle/labview/page/keyboard-shortcuts.html)

Caution: older NI forum evidence reports that `Block Diagram:Remove Bad Wires` did not participate correctly in an undo transaction. The same discussion reports that diagram cleanup became undoable when invoked through `Diagram.TopLvlDiag`, but that observation concerns cleanup and should not be generalized as proof that `Remove Bad Wires` is undo-safe. [NI Community: Undo for Programmatic BD cleanup](https://forums.ni.com/t5/LabVIEW/Undo-for-Programmatic-BD-cleanup/m-p/1020002)

### 3. Undo/redo API

These are methods on the **target VI reference**, not Application-level methods:

| Exact long name | ID | Purpose |
|---|---:|---|
| `Transaction:Begin Undo` | `402` | Starts a transaction |
| `Transaction:End Undo` | `403` | Commits it as one undoable action |
| `Transaction:Fail` | `42A` | Cancels the transaction and deletes its undo information |
| `Transaction:Undo` | `428` | Equivalent to Edit ??Undo |
| `Transaction:Redo` | `429` | Equivalent to Edit ??Redo |
| `Transaction:Get Undo State` | `489` | Returns availability and menu text |
| `Transaction:Get Redo State` | `490` | Returns availability and menu text |

The complete method list and IDs are on the [LabVIEW Wiki VI class page](https://labviewwiki.org/wiki/VI_class).

Typical G sequence:

```text
target VI.Transaction:Begin Undo(Name = "Delete generated tracking code")

perform all scripting edits

success and something changed?
    target VI.Transaction:End Undo
else
    target VI.Transaction:Fail
```

`Transaction:Begin Undo` has one optional string input, `Name`. That text becomes the action name shown beside Edit ??Undo/Redo. It is a VI Scripting method, not available in the Run-Time Engine, allows remote access, and cannot be invoked while the target VI is running. [LabVIEW Wiki: Transaction.Begin Undo](https://labviewwiki.org/wiki/VI_class/Transaction.Begin_Undo_method)

`Transaction:End Undo` has no parameters, is VI Scripting-only, permits remote access, is unavailable in the Run-Time Engine, and cannot be invoked while the target VI is running. [LabVIEW Wiki: Transaction.End Undo](https://labviewwiki.org/wiki/VI_class/Transaction.End_Undo_method)

Darren Nattinger?셲 example explanation confirms:

- begin before making scripting changes;
- the `Name` appears in the Undo/Redo menu;
- call `End Undo` only after a successful, real edit;
- call `Transaction:Fail` after failure or when nothing changed;
- unwrapped scripting edits can clear the existing undo stack.

[LabVIEW Artisan: Supporting Undo](https://labviewartisan.blogspot.com/2009/06/labview-scripting-tip-2-supporting-undo.html)

I found no authoritative public documentation defining nested transaction semantics. Therefore, do **not** assume nesting is supported or that inner names create separate undo records. Use one non-nested transaction per user-visible operation, with exactly one matching `End Undo` or `Fail`.

Undo does work for ordinary scripting edits performed by another VI against the target VI, provided the edits are enclosed properly. NI forum evidence explicitly reports that scripted diagram changes can subsequently be undone from the affected target VI. [NI Community: Undo for Programmatic BD cleanup](https://forums.ni.com/t5/LabVIEW/Undo-for-Programmatic-BD-cleanup/m-p/1020002)

For your COM arrangement: if COM runs a G scripting VI, and that G code opens the target reference and calls the transaction methods on it, COM does not inherently prevent undo. The transaction belongs to the target VI. The methods themselves are marked `Remote access allowed: Yes`, but the evidence does not guarantee that every particular scripting mutation records undo state correctly. Tags are a documented counterexample from user testing: tag changes were not restored by undo in LabVIEW 2015/2017. [NI Community: GObject tags not captured in Undo/Redo](https://forums.ni.com/t5/LabVIEW/Setting-a-Tag-of-an-object-is-not-captured-in-Undo-Redo/td-p/3746931)

Practical recommendation: wrap node deletion, wire deletion/disconnection, and creation in one named target-VI transaction; call `Fail` on any error; avoid nesting; and separately verify `Remove Bad Wires`, because historical evidence says that particular method may disrupt undo behavior.

## Sources

(extract from answer)

## What was done with it

MISCLASSIFIED AS QUOTA AND NEARLY LOST - the wrapper matched a bare 429 in the answer body (method-ID table) and benched codex; the answer itself is excellent and is now adopted. Confirms Generic:Delete (verified on the machine via the Invoke dropdown, and OpDeleteByLabel_v0 built from it), and adds what was still missing: Wire:Disconnect Terminal(terminal ref) for UNWIRING a single terminal without deleting the whole wire, Wire Terminals[] / Terminal Connected Wire to find it, VI:Block Diagram:Remove Bad Wires (ID 410) for Ctrl+B, and the full VI-class Transaction table (Begin Undo 402 / End Undo 403 / Fail 42A / Undo 428 / Redo 429 / Get Undo State 489). Caveats recorded: do not nest transactions, and Remove Bad Wires may not participate correctly in undo.
