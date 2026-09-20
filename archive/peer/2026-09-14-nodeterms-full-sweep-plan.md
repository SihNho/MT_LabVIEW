---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, plan]
---

# nodeterms-full-sweep-plan

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (55s)
- **why asked:** plan change (a full 635-node re-sweep of the main VI through the new node_terms op, for a direction-aware net map and a local-variable census) - plans are peer-reviewed before they run.
- **verdict:** ACTED ON: (a)/(c) node_terms now returns the node's own UID (the donor's node-UID reader survives in the op); the sweep verifies uid == Step-0 tree per node and treats UID 0 as out-of-range (aborts the diagram, records it); (b) same IA_n/index-2 lineage - tuple equality already shown; (d) Traverse class 'Local' counted first (with 'Global', 'Property', 'Invoke'); the terminal-name rule for locals is recorded as OBSERVED; 'Local.Control Name' noted as the identity route if a cast ever becomes available; (e) census limits (implicit invokes, control refs, Value(Signaling), event registrations) written into the doc as not covered.

## Question

PLAN REVIEW (attack it; be brief). CONTEXT: OpNodeTerms_v0 (gscript.node_terms(target, diagram, node)) is functionally verified today: per-index tuples identical to the old per-terminal walker on every node tested, Is Source? semantics verified on primitives AND on global nodes (NI example: two WRITE + one READ 'Host Stop' nodes distinguished, tools/bench/global_read_control3.log); 0.8 s per node on the main VI vs the old walker's ~8 s per node, and it drops no junk. Traverse class name for global nodes = 'Global' (report_all works). PLAN: tools/bench/sweep_nodeterms_main.py - for every diagram k of the main VI (170 diagrams, node counts per diagram known from tools/bench/diagram_tree_main.json, 635 nodes total) run node_terms(MAIN, k, n) for n in 0..N_k-1 -> tools/bench/main_vi_nodeterms.json {diagram: {n: {uid?: no - node_terms does not return the node uid; take it from the tree's per-diagram uid list IF Nodes[] order == tree order, else from the old cache main_vi_netmap.json which stores (n->uid) per diagram}, terms: [(name, is_source, wire, errs)]}}; ~10 min; cross-check per diagram against main_vi_netmap.json (names+wires per index must match where the old cache has the node; the old cache is 'at least', it truncated on some diagrams). USES: (1) a complete, junk-free net map WITH terminal direction (the old cache has no direction); (2) LOCAL VARIABLE census: a local-variable node's single terminal is named after its control (as a global's is named after its field) -> which of the 10 panel objects with a bare terminal (docs/main-vi-panel-map.md) are used through locals, and read or write; (3) 'Value' property nodes: terminal 'Value' + an unwired 'reference' = implicit PN, but the LINKED CONTROL is not in any terminal name - still a gap; ask: is there a cast-free property giving an implicit property node's / local variable's linked object (PropertyNode.'Linked Object'? LocalVariable class?) or a Traverse class ('LocalVariable', 'Property') whose owner/position we can cross-reference? ATTACK: (a) is Nodes[] order stable between the Step-0 tree (built from Nodes[] via net_map) and now - any risk the main VI's in-memory copy changed order (it was never edited; LabVIEW restarted at 10:52)? (b) node index space: node_terms uses the same 'index 2' = Nodes[] index as OpNetInfo - agreed? (c) a diagram with 0 nodes or a node index past the end: what does node_terms return (error 1055 on the Node.Terminals[] read -> empty arrays; is that distinguishable from a node with zero terminals?) (d) the local-variable terminal-name claim: cite LabVIEW docs/wiki - does a local variable node's terminal Name equal the control label, and does Is Source? TRUE mean read? (e) the 10 bare-terminal objects: which are likely locals/Value-PN accessed (e.g. 'Image' indicator via Value PN, 'Stop Trans' via local) - any other access mechanism we would miss (event structure registrations, control references, Value(signaling))? Concrete failure scenarios + cheapest checks.

## Answer

Verdict: proceed, but do not trust cached `n ??UID` across the LabVIEW restart. Make identity and error status first-class outputs.

- **(a) `Nodes[]` order:** No documentation I found promises persistence of array order across reloads. A restart creates a fresh object graph, even if the VI was never edited. Failure scenario: the sweep is internally correct, but cached UIDs are silently attached to different nodes. Cheapest check: before the full sweep, obtain current `(index, UID, class, bounds)` for every diagram and compare it with the Step-0 tree. Better: have the same operation return the selected node?셲 UID alongside its terminals.

- **(b) Index space:** Agreed only if both `OpNodeTerms` and `OpNetInfo` literally perform `Index Array(diagram.Nodes[], n)`. ?쏷erminal index??is separately defined as an index into `Node.Terminals[]`; it proves nothing about node indexing ([NI Community](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)). Cheapest check: for 5??0 heterogeneous nodes, report UID/class/bounds through both paths at the same `k,n`.

- **(c) Bounds/errors:** Your current behavior is unsafe. An out-of-range `n` that becomes error 1055 and then empty arrays is indistinguishable from a valid zero-terminal node. Skip known zero-node diagrams; reject `n < 0 || n ??N`; and store `{ok, error_code, uid, terminal_count, terms}`. Abort a diagram on any invalid-node error rather than writing `{terms:[]}`.

- **(d) Locals:** NI documents that locals are associated with front-panel objects by their **owned labels**, but does not document that `Terminal.Name` must equal that label ([NI Local Variables](https://www.ni.com/docs/en-GB/bundle/labview/page/local-variables.html)). Treat the terminal-name rule as observed, not contractual. `Is Source? = TRUE` means the terminal produces data ([LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class/Is_Source%3F_property)); therefore for a local, TRUE corresponds to reading the front-panel value, while FALSE corresponds to writing it. Cheap verification: one known local read and one known local write.

- **Direct identity exists:** Traverse should expose the scripting class **`Local`**, not `LocalVariable`; it is listed in the VI Server hierarchy ([class hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)). Test that class for `Control Name`; an NI employee specifically identifies that property as the way to bind a created local ([NI Community](https://forums.ni.com/t5/LabVIEW/create-local-variable-using-labview-scripting/td-p/2616645)). For implicit property nodes, the cast-free **Property ??Linked Control** property returns the actual control reference, or NULL plus error when no control link exists ([Linked Control](https://labviewwiki.org/wiki/Property_class/Linked_Control_property)). That closes the stated implicit-PN gap; read the returned control?셲 label/UID.

- **(e) Census completeness:** Bare-terminal + local + implicit `Value` is not exhaustive. Also count implicit **invoke nodes**, explicit property/invoke nodes reached through control-reference wires, control-reference nodes, `Value (Signaling)`, and event-structure static/dynamic registrations. NI distinguishes implicit links from explicitly wired reference links ([NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000wwBXCAY&l=en-US)); controls also expose `Control Reference Nodes[]` and `Local Variables[]`, which is the cheapest authoritative reverse census ([Control class](https://labviewwiki.org/wiki/Control_class)). Use those panel-side arrays as the completeness oracle, then reconcile them with the diagram sweep.

Likely guesses such as `Image ??Value PN` and `Stop Trans ??local` should remain hypotheses until `Linked Control`/`Local.Control Name` identifies them. Position matching should be only a last-resort sanity check, never identity.

## Sources

(extract from answer)

## What was done with it

See the **verdict** line at the top of this file (filled 2026-09-14 14:2x; the day's outcomes are in STATUS.md and docs/).
