# fstunnel-v1-b4-execstate0-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 11:09:56
- **outcome:** ANSWERED (196s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

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



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The required-input-terminal claim is wrong. Its proposed cause already exists unchanged in the legal control state.

1. Strongest refutation

The fresh donor has `ExecState == 1` while nodes 43, 124, and 990—and every cited unwired/empty terminal—are already present with the same wire-zero state. After the recipe, those terminals remain identical while only recipe-created objects and connections differ. That is a direct same-VI counterexample to “those unwired terminals cause `ExecState == 0`”:

- Fresh legal state and target nodes: [diag_fstunnel_orphans.log](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/diag_fstunnel_orphans.log:20>)
- Fresh terminal inventories: same file at lines 23–62.
- B4 broken state: same file at line 102.
- Unchanged B4 terminal inventories: same file at lines 107–146.

Requiredness is not inferred from “input + wire 0.” LabVIEW separately classifies connector-pane inputs as required, recommended, or optional; only an unwired required input breaks the caller. Recommended and optional inputs may remain unwired without even generating a warning. [NI: Setting Required, Recommended, and Optional Inputs and Outputs](https://www.ni.com/docs/ar-IQ/csh?context=lvcore_lvhowto_specifying_required_recomm)

Node 43 is especially weak evidence: NI documents `vi path` as the required Open VI Reference input, while the type specifier is used only when a typed reference is wanted and an unwired local application reference has defined local behavior. [NI: Calling a LabVIEW VI by Reference](https://www.ni.com/en/support/documentation/supplemental/06/calling-a-labview-vi-by-reference.html), [NI Open VI Reference reference manual](https://download.ni.com/support/manuals/321526b.pdf)

2. Alternative explanation

Between the two proposed explanations, the evidence favors a broken newly-created connection, not the inherited unwired terminals.

Equal nonzero wire UIDs prove attachment, not compilability. NI explicitly says wiring can create a broken wire and that incompatible terminal data types are a standard cause. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-US/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

The strongest candidate is therefore the cast-output → property-node `reference` connection at one or both of:

- TMSC → PN_A, recipe line 476
- TMSC → PN_B, recipe line 483

A plausible mechanism is that scripting attached the wire before type propagation/adaptation produced a compatible property-node reference type. The common downstream GObject/property chain is another possibility. The identical OUT/IN result supports a shared construction error; it does not implicate unchanged donor nodes.

This does not prove which wire is broken. It establishes that the current UID evidence cannot clear those wires.

3. What “EMPTY” terminals mean

Nodes 124 and 990 are ordinary SubVI call nodes. Their terminal arrays reflect connector-pane slots. An empty reported name can mean an unassigned/spare connector-pane terminal—or, less commonly, a connected terminal whose associated control label is empty. It is not a special “broken node” state.

NI explicitly recommends connector-pane patterns containing unused terminals for later expansion, so unused/unnamed slots are valid. [NI: Icon and Connector Panes](https://www.ni.com/en/support/downloads/instrument-drivers/tools-resources/instrument-driver-guidelines/icon-and-connector-panes.html), [NI: Assigning Terminals to Controls and Indicators](https://www.ni.com/docs/en-AS/bundle/labview/page/assigning-terminals-to-controls-and-indicators.html)

Thus an empty name says nothing about requiredness. D1 proves that point empirically for these exact instances.

4. Readers for the cause

The project’s stronger claim—“no reader exists”—is also too broad.

- `VI.Get Errors`, method `452`, exists as a private VI Server/VI Scripting method. Its observed signature is:

  - `Errors`: 1-D string array output
  - `Details`: 1-D string array output
  - `Call Dangerously?`: optional Boolean input

  An NI-hosted discussion reports that the result is accessible through “the 2 string arrays” and that it returns usable error information, though not exactly the Error List presentation. [NI Community: Error list in VI scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/m-p/2269168) The community VI Server catalog confirms private method `452` and those three parameter names, although its type table is incomplete. [LabVIEW Wiki: VI.Get Errors](https://labviewwiki.org/wiki/VI_class/Get_Errors_method)

- `Wire.Get Error List`, private method `6370C0A`, returns an I32 error-list array for a particular Wire reference. Iterating wires and calling it would identify the offending wire by identity even if the returned reason needs decoding. [LabVIEW Wiki: Wire.Get Error List](https://labviewwiki.org/wiki/Wire_class/Get_Error_List_method)

- `Wire.Is Broken?` answers only whether a wire is broken, not why.

- Without building any op VI, LabVIEW’s Error List UI already reports the cause and can highlight the offending diagram location through “Show Error.” A specific broken wire also has a `List Errors` shortcut and displays its reason when hovered. [NI: Debugging Tools in LabVIEW](https://www.ni.com/getting-started/labview-basics/debug.htm), [NI: Correcting Broken Wires](https://www.ni.com/docs/en-US/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

I find no defensible basis for saying `VI.Get Errors` can be invoked directly as `VirtualInstrument.GetErrors` over the existing COM reference. This is a private VI Server method, while external ActiveX clients are limited to members exported by LabVIEW’s ActiveX type library. NI says that type library defines the exported `Application` and `VirtualInstrument` interfaces; the documented `VirtualInstrument` ActiveX method list does not include `GetErrors`. [NI: ActiveX and LabVIEW](https://www.ni.com/en/shop/labview/activex-and-labview.html), [VirtualInstrument ActiveX method catalog](https://documentation.help/NI-ActiveX-LabView/VI_Class_Method.html)

Therefore, absent a LabVIEW-side Invoke Node/helper, direct COM invocation is unlikely. That is an inference from the exported interface, not a vendor-documented prohibition. NI does not appear to publish an official API-reference page or supported signature for private method `452`; the exact signature above comes from the NI-hosted discussion and community catalog, not supported vendor documentation.

5. Concrete falsification

The original claim is already falsified by D1: its alleged cause is present unchanged in an executable state.

A one-run falsifier would be even more explicit: at B4, obtain the Error List and observe either:

- “connected terminals have different types,” highlighting one of the six new wires; or
- another error associated with a recipe-created property node.

Either result rules out nodes 43/124/990 as the cause. Conversely, the competing broken-wire explanation would be falsified if every new wire reports unbroken and Error List specifically identifies an unwired required input on one of those three inherited nodes.

The cheapest discriminating test is: pause at B4 on the disposable scratch, open LabVIEW’s existing Error List by clicking the broken Run arrow or selecting View → Error List, record the first error’s text, then use Show Error. It requires no new op VI, no save, and directly separates “required terminal on 43/124/990” from “broken/type-incompatible new wire.”

## Sources

(extract from answer)

## What was done with it

ACCEPTED in full by the cycle-22 judgement session, 2026-09-18. The claim is refuted by a measurement that did not
exist when it was written: the FRESH donor copy reads ExecState 1 with those same sinks at wire 0
(tools/bench/diag_fstunnel_orphans.log:20-21,63-64), so unwired-but-legal input terminals cannot be the cause of
B4. Accepted consequences:
- The leading hypothesis is now the UN-DELETED RESIDUAL STUB WIRE #384 on the cast output, which wire_checked
  branched from: it explains every observation at once - all six sites pass by effect, B4b reads the face-A wire,
  and the VI stays broken.
- The discriminating test needs no new reader: Wire.Is Broken? 6371004 is ALREADY BUILT and measured
  (docs/NAMES.md:888-897). It is run at each of the six sites and on #384 itself, next cycle.
- wire_checked's equal-uid test is insufficient exactly as the 2026-09-18 10:21 prior-art review said, and the
  per-site ExecState attributor added this cycle is VACUOUS in this recipe (measured: ExecState BEFORE = 0 at all
  six sites). It is superseded by a Wire.Is Broken? check per site; the attributor is not defended.
- The `DIAG unwired sinks` scan is blind by construction (a stub wire reads non-zero; build_opfstunnelterm_v1.py:519
  filters error*), so it is never again cited as evidence that nothing is unwired.
- codex's finding that VI.Get Errors 452 is probably NOT reachable over our COM path (absent from the exported VirtualInstrument ActiveX interface) is recorded; with Wire.Is Broken? built, 452 leaves the critical path and STATUS OPEN 38/39/41's "452 NOT built" no longer blocks anything.
