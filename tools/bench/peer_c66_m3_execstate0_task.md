# REFUTE one claim about why a LabVIEW VI-Scripting build stage ended at `ExecState` 0

You are attacking ONE claim. Find the strongest reason it is WRONG, name an alternative explanation,
say what would falsify it, and end with the cheapest discriminating test — expressed only in verbs
we already own (list at the bottom). That test is the next cycle's opening measurement, so its
cheapness and its power to SEPARATE the two explanations matter more than its elegance.

## Background in one paragraph

We are restructuring a copy of a LabVIEW tracking VI by SCHEDULING only (standing rule: the
computation must not change). Stage "S3b-M3" takes a set of objects that sit on the top-level
sub-diagram `Diagram #639` (owner `WhileLoop #637`, 75 nodes) and moves them, ONE `move_in` call per
object, into the empty body `Diagram #23058` of a previously built `WhileLoop #23032`. `move_in`
SEVERS every wire attached to an object it moves, so each move is followed by re-wiring the rows
that move severed, with a node->node writer (`connect_nested_v1`) that addresses ONE nested diagram.
Verification is STRUCTURAL only — object censuses, `ExecState`, `Wire.Is Broken?`. We never run the
VI. The run under discussion is `tools/bench/diag_c66b_s3b_m3.log` (`BGRUN END rc=1`).

## THE CLAIM TO REFUTE

> S3b-M3 ended at `ExecState` 0 **because the diagram is incomplete, not because the moves or the
> rows are wrong**: 7/7 `move_in` calls landed (`Diagram #23058` `Nodes[]` =
> `[23035, 3529, 3560, 3447, 48, 10407, 23499, 23523]`), 7/7 attempted rows each shared one wire uid
> with the WIRED count rising at both ends, every minted junk `Invoke` was purged by uid (14/14,
> census 632 -> 633 -> 632 each time), `Wire` rose 1907 -> 1914 (+7), and
> `Node` / `ControlTerminal` / `Local` / `LoopTunnel` / `Tunnel` are all unchanged — but **four rows
> were never attempted** (three shift-register creations and the from-tunnel row), so the structure
> is simply unfinished, and a VI with unsatisfied required inputs is legitimately broken.

Attack it in particular on these seams, and on any seam we have not thought of:

1. **Is the inference valid at all?** "Four rows unattempted" would explain SOME broken state. Does
   it explain THIS one? Is there any way to tell, from counts alone, the difference between "broken
   because unfinished" and "broken because one of the fourteen edits is wrong"? If counts cannot
   distinguish them, say so plainly — that is the answer we most need.
2. **Do the gates that "passed" actually constrain anything?** Every gate above is a COUNT or a
   shared-uid check. A branch onto an existing net mints no object and moves no count. A wire that
   lands on a legal but WRONG terminal of the right node moves the same counts as the right one.
   A coerced connection (DBL->SGL, DBL->I32) is legal, leaves `ExecState` 1 and changes no count.
3. **`move_in` itself.** Is moving a `CaseStructure` (`#10407`, with its own tunnels and frames), a
   `SubVI`, three `ControlReferenceConstant`s and two `Local` variables into another loop's body by
   a scripting relocation semantically safe? Can a relocation leave an object attached to a diagram
   it no longer draws on, orphan a tunnel, or leave a structure's frame references dangling in a way
   that `report_all`-style censuses cannot see?
4. **The three shift-register rows and the from-tunnel row.** If those four rows are what is
   missing, is `ExecState` 0 the state LabVIEW would actually report — or would some of those show
   up as something else (a dangling wire, a required-input error, a specific error code)?
5. **Ordering.** Is there a defensible order for "move seven objects, then wire seven rows" that we
   are violating — e.g. does moving a structure before or after its wired neighbours change what the
   severing does?

## ALREADY RULED OUT — do not spend your answer on these three

1. Cycle 54 reached `ExecState` 0 at this SAME stage with 5/5 moves and 9/9 rows, so this is the
   second failure at the same place; the stage is being DECOMPOSED into smaller saved steps, not
   retried. Telling us to retry it, or to retry it with a different move set, is not useful.
2. `allow_broken` was never set and `gui_save` was never called, so nothing masked the reading.
3. The junk-`Invoke` mechanism that explained every earlier `ExecState` 0 in this project was purged
   after every single call and the whole-VI `Node` census returned to its prior value each time
   (632 -> 633 -> 632, 14/14), so it is not that.

## WHAT WE WANT OUT OF THIS

End with **THE CHEAPEST DISCRIMINATING TEST** that separates

  (H1) "the diagram is merely UNFINISHED — the 14 edits are all correct"   from
  (H2) "at least one of the seven moves or seven rows is itself WRONG",

expressed only in the verbs below. If the cheapest test needs a verb we do not have, say which ONE
verb, and what it must read, rather than describing a workflow we cannot execute. Rank by cost if
you can name more than one.

## THE VERBS WE OWN (everything below is built, wrapped and measured on this machine)

Read-only: `exec_state(vi)` · `count(vi, class)` · `uids(vi, class)` · `report(vi, class)` /
`report_all(vi, class)` (Traverse-for-GObjects census: uid, class, label, position, owner class) ·
`node_labels(vi, diagram_index)` · `node_terms(vi, diagram_index, node_index)` and
`node_terms_uid(...)` (per terminal: name, is_source, connected-wire uid, four error codes) ·
`tunnels(vi, index)` (a LoopTunnel's outer terminal + one inner terminal per frame) ·
`panel_wiring(vi)` / `fp_labels(vi)` (every front-panel control: label, indicator?, uid, its diagram
terminal's wire) · `node_info(vi)` · `net_map(vi, diagram_index)` (walks a diagram's nodes and
groups terminals into nets) · `wire_source_owner(vi, wire_uid)` (by-uid walk of a WIRE's own
`Terms[]`, giving each terminal's OWNER class and uid) · `conpane(vi)` · `subvis(vi, diagram_index)` ·
`diag_index(vi, uid)` · `owner_of(vi, uid)` (⚠️ measured to answer with the PREVIOUS query's object
sometimes — we do not gate on it) · `Wire.Is Broken?` 6371004, readable only through an ORDERED pass
that addresses its sink as `Diagram[d].Nodes[n].Terminals[t]` · `Terminal.Coercion Dot?` 634A006 and
`Terminal.Data Type` 634A008 (IDs known, NOT yet wrapped — reading one needs a new op VI).

Editing: `move_in(vi, uid, dest_diagram, position)` · `move_out` · `move_object` · `connect_nested_v1`
(node->node on ONE nested diagram) · `connect_terminals` / `connect2` · `wire_indicators` ·
`create_control` / `create_indicator` · `build_property` / `build_invoke` (create a scripted property
or invoke node from a property/method ID) · `delete_object(vi, class, index)` · `add_shift_reg` +
`wire_sr` · `for_loop` / `while_loop` / `build_case` · `save(vi)`.

Constraints on any test you propose: we never RUN the VI under test, we never click the GUI, and we
work on a stamped copy, never on an original.
