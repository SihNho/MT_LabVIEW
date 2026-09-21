# REFUTE two claims about a LabVIEW VI-Scripting move stage, then answer one factual API question

You are attacking two claims. Find the strongest reason each is WRONG, name an alternative
explanation, say what would falsify it, and name the cheapest discriminating test we could run over
our COM/VI-Server property path. Then answer the separate FACTUAL question at the end, using the web.

## Background in one paragraph

We are restructuring a copy of a LabVIEW tracking VI by SCHEDULING only (rule: the computation must
not change). The working bed is `claudeDev\D1_s3b_row2_20260921_160311.vi`. On the top-level
sub-diagram `Diagram #639` (owner `WhileLoop #637`) sit 75 nodes. A previously built empty
`WhileLoop #23032` has an empty body `Diagram #23058`. Stage "S3b-M3" moves a set of objects from
`#639` into `#23058` with one `move_in` call per object, then re-wires the rows that the move
severed. Everything is verified STRUCTURALLY only (`ExecState`, object censuses, `Wire.Is Broken?`)
— we never run the VI.

## CLAIM 1 — the move set is SEVEN objects, not five

> S3b-M3's move set is not the five loop-1.5 nodes but **seven objects**: those five plus the two
> Local variables `#23499` and `#23523`, all moved into `#23032`'s body `Diagram #23058`.
> Reason: `#10407` (a CaseStructure) moves to `#23058` while both Locals currently sit on
> `Diagram #639`, so leaving them behind makes rows 1 and 2 cross-diagram, and our `connect_nested_v1`
> verb addresses one nested diagram only. A Local variable binds to its front-panel control **by
> label**, not by wire, so relocating one changes no data path — which is precisely what the
> indicator+Local substitution was built to buy. This is therefore a pure SCHEDULING change,
> permitted by our behaviour-preserving-refactor rule, and it keeps every row intra-diagram with no
> new tunnel and no border object.

Attack in particular: is "a Local variable can be moved between diagrams with no semantic effect"
actually true in LabVIEW? Name any way a Local's diagram membership changes behaviour, legality,
race semantics, dataflow scheduling or the compiler's verdict — e.g. inside a Case/Event/Disabled
structure, a Timed Loop, a subVI boundary, reentrancy, or the race conditions LabVIEW's own docs
warn about for Locals. Also: is there any way `Diagram.MoveObject`-style relocation of a Local can
silently rebind, orphan or duplicate it?

## CLAIM 2 — the abort clause that fired was mis-scoped, and the re-scoping is correct

> Abort clause A2 was written to catch "a watched wire branching onto an existing structure's
> tunnel" and was scoped as "on ANY tunnel terminal". It fired on wires **23540** and **23502**,
> whose sinks are `#10407`'s **own** t2 / t0 case tunnels — the very connection the two rows were
> built to make, and the same sink the original undivided wire **10990** used. The new net **23556**
> was measured tunnel-free (`IndexArray #10757` -> owner `Diagram 639`). Each of the three wires
> walked by uid showed exactly **one source and one sink**; a branch would show a third endpoint.
> The clause is therefore re-scoped to: abort only if a watched wire has **more than one sink**, or
> a sink other than the terminal its row was built to feed.

The machine's own lines, verbatim, from `tools/bench/diag_c66_s3b_m3.log`:

```
  FAIL  P1b-A2 NO watched wire sits on a terminal of a STRUCTURE node on #639  [{'node_uid': 10407, 'node_class': 'CaseStructure', 'terminal': 0, 'is_source': False, 'wire': 23502, 'node_is_structure': True}, {'node_uid': 10407, 'node_class': 'CaseStructure', 'terminal': 2, 'name': 'index', 'is_source': False, 'wire': 23540, 'node_is_structure': True}]
  PASS  P1c-A2 wire 23556 has NO terminal whose OWNER is in the Tunnel family  owner classes ['IndexArray', 'Diagram', '']
  FAIL  P1c-A2 wire 23540 has NO terminal whose OWNER is in the Tunnel family  owner classes ['Local', 'SelectorTunnel', '']
  FAIL  P1c-A2 wire 23502 has NO terminal whose OWNER is in the Tunnel family  owner classes ['Local', 'Tunnel', '']
```

Attack in particular: (a) is "exactly one source and one sink when walked by uid" a SOUND test for
"this wire is not branched" over LabVIEW's VI Server object model — i.e. can a branched net present
as one Wire object whose `Terminals[]` enumeration returns only two entries, or can a branch live on
a *different* Wire object of the same net that a uid walk never visits? (b) Does the re-scoped clause
still catch the failure it was written for? (c) Note the third owner class in each list is the empty
string `''` — say what an empty owner class most plausibly is on this path and whether it can hide a
third endpoint.

## Already ruled out (do not re-propose these)

1. "The tunnel class is a blind spot in our census" — `report_all('Tunnel')` now resolves and returns
   **471** rows (LoopTunnel 135 · ConditionalTunnel 146 · SelectorTunnel 146 · shift registers 36/36),
   so that class is counted.
2. "Our reader cannot see structure tunnel terminals" — `node_terms` run on all 15 structure nodes of
   `#639` returned their tunnel terminals.
3. "`#639` might not be the diagram we think" — `owner_of(639)` = `('WhileLoop', 637)`, so `#639` is a
   sub-diagram, consistent with every other census.

## SEPARATE FACTUAL QUESTION — please use web search for this one

We measured `TYPE READ UNREACHABLE`: no property our fleet wraps carries a wire's or a terminal's
**data type**. Tried and named, each with the field its wrapper returns:

- `Terminal.Name` 634A004
- `Terminal.Is Source?` 634A003
- `Terminal.Connected Wire` 634A000
- `Terminal.Diagram` 634A002
- `Tunnel.Outside Terminal` 6356001
- `Tunnel.Inside Terminals[]` 6356000
- `Wire.Is Broken?` 6371004
- `NumericConstant.Representation` 5DCFC00

Question: over LabVIEW's VI Server / ActiveX property-and-method surface, **is there a reachable
route to the data type of a wire or of a node terminal** — a property short name, a method, or a
documented indirection — that we have not tried? We need it because `Is Broken?` catches a
type-INCOMPATIBLE connection but **not a LEGAL COERCION** (DBL->SGL, DBL->I32), which leaves
`ExecState` 1 and every count correct while silently changing the numbers. Name the exact identifier
and cite its source (NI documentation page, property node reference, forum post with the short name
visible). If there is genuinely no such route, say so and name the closest indirect proxy
(e.g. a coercion-dot indicator, a saved-file inspection route, a `Get Type Descriptor`-style path).
