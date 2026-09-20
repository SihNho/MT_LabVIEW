---
type: peer-review
status: historical
date: 2026-08-28
tags: [peer-review]
---

# delete-unwire-undo-agy

- **agent:** gemini
- **date:** 2026-08-28
- **outcome:** ANSWERED (152s)
- **why asked:** codex hit quota; asked agy for the delete/unwire/undo scripting APIs.
- **verdict:** adopted

## Question

LabVIEW VI Scripting question - use web search and cite URLs. I need exact API names for three capabilities used from a scripting VI on a target VI's block diagram. (1) DELETE an object: the exact method to remove a GObject (node, constant, terminal) from a diagram - is it GObject 'Remove'? Any restrictions? (2) UNWIRE: how to delete just a wire or disconnect one terminal - is deleting the Wire object enough, or is there a Terminal 'Disconnect Wire' method? Is there a scripting equivalent of Edit>Remove Broken Wires? (3) UNDO: the scripting undo transaction API - NI's example uses methods named 'Begin Undo', 'End Undo' and 'Fail' with an undo name; what CLASS are those methods on (VI class? Application?), what are their exact long names, and does the transaction cover edits made by a scripting VI? Search labviewwiki.org class pages and NI forums.

## Answer

### 1. Delete an Object

* **Exact Method Name**: **`Generic:Delete`** (Short name: `Delete`, Class: `Generic`).
* **Is it `GObject:Remove`?**: **No.** There is no generic `Remove` method on `GObject`. (Specific containers have targeted remove methods like `MultiFrameStructure:Remove Frame` or `CaseStructure:Remove Case`, but general nodes, constants, controls, indicators, and wires use `Delete`).
* **Restrictions & Behavior**:
  1. **Automatic Reference Invalidation**: Calling `Generic:Delete` automatically deletes the object and **closes the object's reference**. Calling `Close Reference` on that reference afterwards will fail with error `1055` (*Object reference is invalid*).
  2. **Terminals**: You cannot call `Delete` directly on individual built-in terminals of primitive functions or subVIs; terminals belong to the node structure.
  3. **Target VI State**: The target VI must be in edit mode (not running or reserved for execution).
  4. **Containers**: Deleting a structure (e.g. While Loop, Case Structure) recursively deletes all objects contained within its subdiagrams.
  5. **Broken Wires**: Deleting a node leaves behind broken wires/dangling branches unless cleaned up.
* **References**:
  * [LabVIEW Wiki ??Generic class](https://labviewwiki.org/wiki/Generic_class)
  * [NI VI Server ??Generic:Delete Method](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/viserver/generic_delete.html)

---

### 2. Unwire / Disconnect / Remove Broken Wires

* **How to delete just a wire**:
  1. Read the **`Connected Wire`** property from the `Terminal` reference (Class: `Terminal`, Property: `Connected Wire`, Property ID `634A000`, Read-Only).
  2. If the reference is valid, call **`Generic:Delete`** (or `Wire:Delete`) on that `Wire` reference.
* **Is deleting the `Wire` object enough?**:
  * **Yes**, deleting the `Wire` reference removes the wire.
  * *Note*: If a wire branches to multiple sinks (a wire tree), calling `Delete` on the wire reference removes the entire wire tree from the source.
* **Is there a `Terminal:Disconnect Wire` method?**:
  * **No.** The `Terminal` class only provides `Connect Wire` and `Create Described Wire`; there is no programmatic `Disconnect Wire` method.
* **Scripting equivalent of `Edit 쨩 Remove Broken Wires` (`Ctrl+B`)**:
  * **Exact Method**: **`Block Diagram:Remove Bad Wires`** (Short name: `BD.Remove Bad Wires`).
  * **Owning Class**: **`VI` class** (invoked on the target VI reference, not on `Diagram` or `Application`).
  * **Behavior**: Programmatically removes all broken/unattached wire segments across the entire block diagram.
* **References**:
  * [LabVIEW Wiki ??Terminal class](https://labviewwiki.org/wiki/Terminal_class)
  * [LabVIEW Wiki ??Wire class](https://labviewwiki.org/wiki/Wire_class)
  * [NI VI Server ??VI:Block Diagram:Remove Bad Wires Method](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/viserver/vi_bd_remove_bad_wires.html)

---

### 3. Scripting Undo Transaction API

* **Owning Class**: All transaction methods reside on the **`VI` class** (invoked on the target VI reference).
* **Exact Method Names & Signatures**:
  1. **`Transaction:Begin Undo`** (Short name: `Transaction.Begin Undo`):
     * *Parameters*: `Name` (String, optional) ??defines the string shown in the UI menu under **Edit 쨩 Undo <Name>**.
     * *Behavior*: Starts an undo transaction on the target VI. Nested transactions are not supported; calling it while a transaction is active returns an error.
  2. **`Transaction:End Undo`** (Short name: `Transaction.End Undo`):
     * *Behavior*: Commits the transaction and pushes the grouped scripting operations as a single item onto the VI's undo stack.
  3. **`Transaction:Fail`** (Short name: `Transaction.Fail`):
     * *Behavior*: Discards/aborts the active transaction so no partial changes or empty undo entries are registered on error.
* **Does the transaction cover edits made by a scripting VI?**:
  * **Yes.** This API is specifically designed for VI Scripting tools to make programmatic modifications (creating nodes, wiring, moving, deleting objects) user-undoable in the LabVIEW editor.
  * *Boundary*: It only tracks changes to the target VI's block diagram and front panel. Changes outside the VI (e.g. disk file operations, Project Explorer items, or non-tracked internal tags) are not reversed by the undo stack.
* **Shipped Example**:
  * `labview\examples\Application Control\VI Scripting\Supporting Undo\Supporting Undo.lvproj`
* **References**:
  * [LabVIEW Wiki ??VI class: Transaction.Begin Undo method](https://labviewwiki.org/wiki/VI_class/Transaction.Begin_Undo_method)
  * [NI VI Scripting ??Supporting Undo](https://www.ni.com/docs/en-US/bundle/labview/page/lvhowto/supp_undo_scripting.html)



## Sources

(extract from answer)

## What was done with it

DECISIVE and machine-verified: Delete is Generic:Delete, NOT on GObject - which explained why a GObject-typed Invoke node offered only Move. Retargeting the class constant to Generic made Delete appear in the dropdown, and OpDeleteByLabel_v0 now works (0.05 s). Also gave Terminal Connected Wire + Wire delete for unwiring, VI method Block Diagram:Remove Bad Wires for Ctrl+B, and the VI-class Transaction Begin Undo / End Undo / Fail API. agys first substantive contribution.
