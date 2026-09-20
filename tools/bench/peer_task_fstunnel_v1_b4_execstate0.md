CLAIM UNDER TEST (attack it): the `ExecState == 0` failure at gate B4 of `tools/recipes/build_opfstunnelterm_v1.py` is caused by REQUIRED INPUT TERMINALS THE RECIPE NEVER WIRES on nodes it creates — node 990 (six sinks with EMPTY names), node 124 (`Other Refnum`, `Traverse Generated Code (F)`) and node 43 (`type specifier VI Refnum`, `application reference (local)`) — and NOT by the six `wire_checked` connections.

WHY I BELIEVE IT: all six wire sites verified by effect this run — equal, non-zero wire uid at both ends (`src 384 -> dst 384`, `1694/1694`, `1719/1719`, `1766/1766`, log lines 57-68) — and gate B4b independently confirms the back half reads the face-A wire (`{157: 1694, 1319: 1694, 1326: 1694}`). The identical failure appears for both classes (`ExecState per step [('TMSC -> PN_A', 0), ('back half re-fed', 0)]`, log :75 and :115).

EVIDENCE FILES: `tools/bench/build_opfstunnelterm_v1_run1.log` (six site lines :57-68; `DIAG unwired sinks` :76; B4 :75 and :115); `tools/recipes/build_opfstunnelterm_v1.py` (helper at :284-320, its recorded limits at :297 and :308; six call sites :431,438,441,444,449,452).

ALREADY RULED OUT:
- The twice-fatal `:392` failure of the `_v0` bytes: a measured FALSE NEGATIVE of `gscript.wire`'s Wire-count test on a branch (`tools/gscript.py:1327-1329` says so in its own comment); all six sites now pass by effect, so it is not the cause of B4.
- "The per-site ExecState check would have caught a broken wire": measured VACUOUS — `ExecState BEFORE = 0` at all six sites, so it cannot discriminate anything in this recipe.
- Property ids `6356001` / `6356000` / `7CC75C00`: all 1077-refused on the OUTER class (recorded in `archive/2026-09-18-status-cycle21-wire-semantics.md` §7).

THE COMPETING EXPLANATION I WANT ATTACKED HARDEST, not mine: that one of the six wires IS BROKEN — a type-incompatible cast-output → property-node-`reference` downcast, which equal-uid verification passes, because LabVIEW joins type-incompatible terminals and draws a broken wire whose uid reads identically at both ends (`docs/NAMES.md:861-867`, measured 2026-09-15). That is the shape of sites `:441`, `:444`, `:452`. Nothing in this run distinguishes it from my claim.

QUESTIONS:
1. Which explanation does the evidence actually favour, and what is the CHEAPEST test that separates them?
2. Is it TRUE that this project has no reader that names the broken object? `CLAUDE.md` lists `VI.Get Errors` (method 452) and `Wire.Is Broken?` (6371004) as identified-but-unbuilt, and `docs/d1-build-plan.md:859-860` records prior art stopping the former. Attack that claim with an external search: name any LabVIEW VI Server / VI Scripting property or method that reports the CAUSE of a broken VI, including anything reachable WITHOUT building a new op VI — the actual signature of `VI.Get Errors`, whether it can be Invoked directly over a COM/ActiveX VI reference, and any equivalent in LabVIEW 2026. Cite vendor documentation with URLs.
3. In LabVIEW scripting, what is a node whose terminals have EMPTY names, and does that state by itself make a VI broken?
4. What would falsify my claim, concretely, in one run?

============================================================
MEASURED AFTER THE RUN (D1)
============================================================
Source: `tools/bench/diag_fstunnel_orphans.log` (read-only diagnostic, `BGRUN END rc=0 after 90s`, gates 8/8;
raw `tools/bench/diag_fstunnel_orphans.json`). Method: a pid-stamped SCRATCH copy of the donor
`OpWireSource_v5.vi`, read in two states — (fresh) the untouched copy, and (at_b4) after the same edit sequence
`build_opfstunnelterm_v1.build_one('OUT')` performs up to gate B4. Nothing was saved; the scratch was deleted in
the same run; all three files byte-identical before and after.

FACT 1 — the FRESH donor copy has ExecState 1 (LEGAL) with 19 nodes on diagram 0, uids
[43, 124, 145, 151, 157, 163, 167, 241, 307, 310, 482, 990, 1044, 1186, 1221, 1319, 1326, 1329, 1554]
(log :20-21). Nodes 43, 124 and 990 are ALL present in that fresh copy (log :64), so the recipe does not create
them; the objects the recipe creates are pn_a 145, pn_b 148, pn_a_uid 151, pn_b_uid 154, pn_b_cw 168,
pn_b_cwu 169 and the control 'reference 4' (log :101; recipe lines :451, :481, :484, :487, :492, :495, :455).

FACT 2 — identity and full terminal lists, IDENTICAL in the fresh (ExecState 1) and at_b4 (ExecState 0) states
(log :23-62 vs :107-146; only node 990's Nodes[] index changes, 9 -> 7, because two nodes were deleted):

  uid 43   ClassName Function, Nodes[0], style 'Open VI Reference', label 'Open VI Reference', pos (275,251)
    T0 'error out' out w590 | T1 'vi reference' out w467 | T2 'password ("")' in w0
    T3 'type specifier VI Refnum (for type only)' in w0 | T4 'error in (no error)' in w0 | T5 'options' in w0
    T6 'vi path' in w106 | T7 'application reference (local)' in w0

  uid 124  ClassName SubVI, Nodes[1], style 'Unknown', label 'Traverse for GObjects.vi', pos (495,281)
    T0 'error out' out w425 | T1 '# of Refs' out w303 | T2 'References' out w188 | T3 'dup VI Refnum' out w0
    T4 EMPTY in w0 | T5 'Other Refnum' in w0 | T6 'Traverse Generated Code (F)' in w0
    T7 'Traverse Target' in w415 | T8 'error in (no error)' in w590 | T9 EMPTY in w0
    T10 'Class Name' in w373 | T11 'VI Refnum' in w467

  uid 990  ClassName SubVI, Nodes[9] fresh / Nodes[7] at_b4, style 'Unknown',
           label 'UID to GObject Reference.vi', pos (900,1600)
    T0 'error out' out w1208 | T1 EMPTY in w0 | T2 'GObject' out w1081 | T3 'dup Owning VI' out w0
    T4 EMPTY in w0 | T5 EMPTY in w0 | T6 EMPTY in w0 | T7 EMPTY in w0 | T8 'error in (no error)' in w0
    T9 EMPTY in w0 | T10 'UID' in w1068 | T11 'Owning VI' in w467

FACT 3 — node 990 is NOT a Property Node and NOT an Invoke Node: `report_all` returns it only under the Traverse
classes SubVI and Node, with ClassName 'SubVI' (log :50, :134). The same holds for 124; 43 is a Function
primitive. So the "which property/method items are selected, is any item blank" part of the question does not
apply to any of the three. (Separately: no reader for a Property Node's selected ITEMS exists anywhere in this
project — `grep 'Property Item|Items\[\]|prop_items'` over `tools/gscript.py` and `docs/toolkit-capabilities.md`
returns only the id line `docs/toolkit-capabilities.md:185`. It was not needed here.)

FACT 4 — the six EMPTY-named sinks on 990, the two EMPTY-named sinks on 124 and every other unwired sink listed
in the failing run's `DIAG unwired sinks` line are present, with exactly the same wire-0 state, in the copy whose
ExecState is 1.

FACT 5 — the scratch reproduced the failure: ExecState 0 after the back half is re-fed (log :102), matching
`build_opfstunnelterm_v1_run1.log:75`.

HANDLES 30,318 after a fresh LabVIEW -> 30,979 at the end. md5 unchanged: 3StateClamping
c39f36e0675339673b707c59f0784fee, V6 2a78e17c449cacdaf5da389818526859, donor OpWireSource_v5
5dc45a04ea5d809f5ca57e9309ed59c5.
