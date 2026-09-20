ATTACK this claim. A build prediction failed in a new place, and the explanation below is the one this project
formed under pressure, minutes after the failure. It is about to drive the next expensive build, so if it is
wrong we need to know now.

Context you need: this project edits LabVIEW block diagrams programmatically over ActiveX/COM, using the
open-source **erdosmiller `lv-scripting`** library (`LV-Scripting.lvlib`) wrapped by our own op VIs. One op,
`wire_control`, is used to wire a named terminal of one object to a named terminal of another. The build is
rewiring a `Z/dZ` signal so that it terminates on a temporary sink node (a newly created `Equal?` primitive)
instead of its original destination.

## The claim under attack (quote it, then attack it)

"The `Z/dZ` -> `#2222 t0` wiring failed only because `wire_control` cannot address the created `Equal?` node's
`x` input by name; the temporary-sink ROUTE itself is sound, and the fix is to reach that terminal by INDEX with
an op we already have."

## The machine record, verbatim (all from `tools/bench/build_d1_routeb_v2_run5.log`)

* `:332` — the created node is WELL FORMED, our own census of its terminals:
  `created Equal? #10104 terminal census = {0: ('x = y?', True, 0), 1: ('y', False, 0), 2: ('x', False, 0)}`
  with `src_names=()`. (Tuple = (name, is_source, ...).)
* `:402` — one step later:
  `'Z/dZ': wire_control to the temporary sink failed: wire_control ['Z/dZ'] -> Function.['x']: error 5001:
  LV-Scripting.lvlib:Get Controls.vi<ERR>`
* So our own census says `x` EXISTS at index 2 with `is_source` False, while `Get Controls.vi` cannot find it.
  **That contradiction is the thing to explain.**
* Second, INDEPENDENT failure in the same run: LabVIEW `error 2` ("memory is full") recurred at
  `tools/recipes/build_d1_routeb_v2.py:1252` — a `count(LoopTunnel)` call routed through our `OpReport_v3.vi` —
  logged at `:406`, measured at **38,824 LabVIEW handles** (`:405`). The SAME call SUCCEEDED in run 4 at
  **51,284** handles. Six other rows failed the same way (`:396-401`).

## Already ruled out - do not spend your answer re-proposing these

1. REORDER route: `ControlTerminal #403` has no node index on `Diagram[56]`; our `OpConnectNested_v1` addresses
   `Diagram[].Nodes[].Terminals[]` only, so a control terminal is unreachable by that path
   (`tools/bench/build_d1_routeb_v1_run4.log:163-164`).
2. The RETRY guard returning early before the sink was reached: FIXED this cycle; it now logs and falls through
   (`tools/bench/build_d1_routeb_v2_run5.log:331`).
3. "A silent default/invalid refnum came out of the creation because `src_names=()`": REFUTED by measurement at
   `:332` - the node is well formed and its terminals are readable.
4. Handle exhaustion as the cause of `error 2`: REFUTED - it recurred at a LOWER handle count (38,824) than a
   count at which the identical call SUCCEEDED (51,284).

## What I want from you

(a) **What does `error 5001` mean specifically in erdosmiller `lv-scripting`'s `Get Controls.vi`?**
    EXTERNAL SEARCH REQUIRED - this is a third-party open-source library (github erdosmiller/lv-scripting) and a
    user-defined error range; do not answer from general LabVIEW error-code memory. Quote the library's own
    definition / source if you can find it, with the URL.
(b) Given the VI's NAME, does `wire_control` in that library address FRONT-PANEL CONTROLS only - i.e. is it
    simply the wrong op for an input terminal of a Function node on the block diagram? Say what evidence
    settles this either way.
(c) **The strongest reason the claim above is WRONG** - i.e. the case that the temporary-sink route is itself
    unsound and the `Z/dZ` row needs something else entirely, not an addressing fix.
(d) What else produces LabVIEW `error 2` at a property/report call when memory is plainly NOT exhausted?
    Name concrete mechanisms, not "memory pressure".
(e) The SINGLE cheapest discriminating test for (a)+(b), given this constraint: the created `Equal?` - unlike
    the `ControlTerminal #403` above - DOES have a node index on the diagram, so index-addressed ops we already
    own (`OpConnectFromWire_v0`, `OpConnectNested_v1`) are available without building anything new.
