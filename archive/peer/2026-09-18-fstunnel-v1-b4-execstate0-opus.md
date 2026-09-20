# fstunnel-v1-b4-execstate0-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9688  in 20 / out 44969 / cache-create 220139 / cache-read 973952  (655s, 18 turn(s))
- **date:** 2026-09-18 11:20:53
- **outcome:** ANSWERED (656s)
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

Write is disabled in this role (correct — AGENTS.md: the peer's output *is* its answer), so the review is below.

---

# REFUTED — and the session's own D1 diagnostic is what refutes it

The evidence does not favour the competing broken-wire explanation either. It does not *reach* either hypothesis, because **not one `Wire` object was read — in the failing run or in the diagnostic built to explain it.**

## 1. The single strongest reason the claim is WRONG

**A condition present in the LEGAL state cannot be the cause of the BROKEN state.** FACT 1: the fresh donor copy is `ExecState 1` with nodes 43, 124, 990 already present. FACT 4: their unwired sinks are present, wire-0, *in that same legal copy*. Same objects, same terminals, same zeros — one VI runs, one does not.

And the noun in the claim is false by definition. NI lists *"A required block diagram terminal is unwired"* as a cause of a broken VI, and required means *"the block diagram … **will be** broken if you do not wire the required inputs."* There is no state in which a VI is `ExecState 1` with a required input unwired — so FACT 1 **proves those inputs are not required**. Node 43 is `Open VI Reference`; `password`, `type specifier VI Refnum (for type only)`, `options`, `application reference (local)` are optional by design.

**Second leg, independent and just as fatal: the claim's only positive evidence comes from a detector this project already measured as blind to this failure class.**

`docs/NAMES.md:969-972` (measured 2026-09-15, peer-confirmed):

> **Deleting a node leaves its wire behind as a loose stub** … a later connection from that source then counts as a BRANCH, and **a search for "unwired sinks" will NOT find the orphaned consumer, because its `reference` still reports the stub's uid.** Identify and CACHE the consumer node and the wire uid BEFORE deleting, then delete node, **delete wire**, rewire.

The `DIAG unwired sinks` scan tests `r["wire"] == 0`; an orphan on a stub reports non-zero and is invisible. And `build_opfstunnelterm_v1.py:519` additionally filters out every terminal whose name starts with `error` — while the donor has a live error chain (FACT 2: node 43 `error out` w590 → node 124 `error in` w590). Blind twice over. That list is not evidence about what is unwired; it is the output of the wrong instrument.

Third, smaller: node 990's EMPTY sinks were measured and written down on 2026-09-15 at `docs/NAMES.md:855-859` — *"the remaining connector-pane slots report EMPTY names"*, on this exact subVI. The claim re-derived a documented non-event as a novel cause.

## 2. Alternative explanation — the loose stub wire #384

I rank this **above** the type-conflict story you asked me to attack hardest.

- Your own docstring says it: `:303-305` — *"the TMSC `specific class reference` output already owned a **residual source-only stub wire #384**"*.
- Provenance: the recipe *identifies* the TMSC by `twire(tmsc, T_CAST_OUT) == twire(pn_terms,'reference')` (`:411-412`), so 384's only known sink was node 145. `:426-434` deletes node 145. `:435-441` deletes wires 578, 639, 533 — **never 384.** That is exactly the sequence `NAMES.md:969-972` says leaves a stub and exactly the prescription that was skipped.
- NI: *"The block diagram contains a broken wire because of a mismatch of data types **or a loose, unconnected end**."* Branching two new sinks onto a wire does not heal a loose segment — so 384 can be broken at B4 while reading `src 384 → dst 384` perfectly.
- It explains every observation: identical failure in both classes, B4b passing, `ExecState 0` already at the first site, and why a node-terminal-only diagnostic could not see it.

Two more live alternatives: **(B)** the same mechanism with a hidden victim — any orphan on a stub, error chain included (`NAMES.md:311`: an unwired `reference` breaks the VI *"even when every wire is good"*); **(C)** your type conflict — and note section P never settled it: all three `FlatSequenceOuterTunnel` inheritance probes were 1077-refused (`run1.log:37-39`), so the back half's acceptance of an `OuterTerminal` reference went in unknown.

And the framing itself: `:307-310` records that the instrument used **cannot establish "not B"**. The honest report was *cause unknown; no wire was read.*

## 3. What would falsify the claim

It already is falsified — any VI that is `ExecState 1` with those terminals unwired kills it, and FACT 1 is that VI. Constructive version in one run: wire all 14 sinks at B4 and read `ExecState`; still 0 ⇒ dead. It cannot be rescued, because requiredness lives in the subVIs' connector panes and the recipe never edits them (donor md5 unchanged, `run1.log:135`).

## 4. Cheapest discriminating test

**T1 — Remove Bad Wires diff at B4.** One run, no new op, only calls this recipe already makes: read `uids(op,"Wire")` + `ExecState` → `remove_bad_wires_scripted` (VI method **410**, public, `docs/toolkit-capabilities.md:132`) → read both again, print the removed set.

| observation | reading |
|---|---|
| `ExecState → 1`, exactly `{384}` gone | **stub confirmed** — claim dead, type conflict dead |
| still 0, `{1694}`/`{1766}` gone | **type conflict** — sink `reference` now bare, 0 expected |
| still 0, nothing gone | no bad wire ⇒ node-level cause; claim still dead by §1 |

The *removed-uid set* is the measurement, not `ExecState`. `NAMES.md:962-967` forbids RBW inside a transient edit window; B4 is the end of the window on a scratch copy, which is the sanctioned place.

**T2 — non-destructive, and it NAMES the object: it is already built.** `Wire.Is Broken?` **6371004** ships inside `OpConnectNested_v0/v1` and `OpConnectFromWire_v0` (`docs/NAMES.md:888-897`, built and measured 2026-09-17, `False` on a good wire / `True` on a two-source wire). Read it on the sink terminals of 384 / 1694 / 1719 / 1766. ⚠️ Branch the Invoke's own `error out` into that node's `error in` (gate `W7b`) or it reports the *old* wire.

## 5. Q2 — "no reader that names the broken object?" **False.**

1. **`Wire.Is Broken?` 6371004 IS BUILT AND MEASURED** — `docs/NAMES.md:888-897`, dated 2026-09-17, *"it never needed a new op."* **`CLAUDE.md:346` is stale**, and the brief inherited the stale line. Two active docs contradict each other about the one capability this cycle spent its budget working around.
2. A second measured signature: two terminals on one wire both `Terminal.Is Source?` 634A003 TRUE (`NAMES.md:900-901`, measured on `w1231`). `OpWireSource_v5` — *the donor of this very recipe* — walks a wire's terminals from a bare UID (`:954-960`).
3. **`Wire.Get Error List` 6370C0A** (private, output `Error List`) sits at `NAMES.md:899` and is **absent from CLAUDE.md's list** — that is per-wire error *text*, closer to what was wanted than `VI.Get Errors`.
4. `VI.Get Errors` **452** is real — labviewwiki's VI class table lists it, RTE Yes, no published signature; NI publishes **no public API** returning Error List text. It is reachable over COM in principle (an ordinary Invoke node on `VI Server:VI`); the failure is *member selection*, not transport — two attempts gave *"only `reference out` / `error out` — no `Errors`, no `Details`"* (`toolkit-capabilities.md:169`). **The obvious external answer is already-tried prior art**: the forum's `SuperPrivateScriptingFeatureVisible` / `SuperSecretPrivateSpecialStuff` ini tokens were included in the 2026-09-09 attempt (`d1-route-b-plan.md:485`). Untried lever: `Invoke.Set Method (Allow Private)` **6370003**, `ID String = "Get Errors"`, `Allow Alternate Names? = TRUE`, class set first (`toolkit-capabilities.md:189-194`). And `OpGetErrors_v0` is **NOT AUTHORISED** — stopped by its own dual prior-art review (`d1-route-b-plan.md:463-473`). Unverified lead only: the same wiki table lists a `VI Linker Errors` property (257, RTE Yes); I could not confirm what it returns — don't plan on it. The GUI Error List does name the object (Items-with-errors / Errors-and-warnings / Details, double-click to highlight).

**None of it is needed here**: "which of four wires is broken" already has a built reader.

## 6. Q3 — empty-named terminals

A subVI node's terminals mirror its **connector pane**, a fixed pattern (12 slots for the common 4‑2‑2‑4). Unassigned slots exist as terminals with no name, cannot be wired, cannot be required. Nodes 124 and 990 show 12 terminals with 2 and 6 unnamed — that signature exactly. It **never breaks a VI**, and here it is not even an inference: measured 2026-09-15 (`NAMES.md:855-859`) and confirmed legal by FACT 1. FACT 3 is right that "which property item is selected" doesn't apply to 43/124/990 — but it *does* apply to the recipe's own nodes 145/148/168, no reader for it exists here, and it was not checked.

## 7. What would change my mind

T1 returning `ExecState 1` with **nothing removed**. Short of that, §1 rests on your own measurement and cannot be argued away: whatever breaks this VI, it is not a terminal that is equally unwired in the copy that runs.

**Sources:** [NI — Debugging Techniques in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/12/debugging-techniques-in-labview.html) · [Setting Required, Recommended, and Optional Inputs](https://rajsite.github.io/unofficial-lvdocs/lvhowto/Specifying_Required_Recomm.html) · [LabVIEW Wiki — VI class](https://labviewwiki.org/wiki/VI_class) · [NI Forums — programmatically check the error messages of a broken VI](https://forums.ni.com/t5/LabVIEW/how-to-programmatically-check-the-error-messages-of-a-broken-vi/td-p/3336258) · [NI Forums — Error list in VI scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/td-p/2263216) · [LAVA — SuperSecretPrivateSpecialStuff](https://lavag.org/topic/15869-what-exactly-is-supersecretprivatespecialstuff-for/) · [LabVIEW Wiki — Connector pane](https://labviewwiki.org/wiki/Connector_pane)

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
- opus's correction that Wire.Is Broken? 6371004 is already built is CONFIRMED against docs/NAMES.md:888-897 and has been applied to CLAUDE.md:346, which was stale and put a false "no reader exists" premise into the framing this review attacked.
