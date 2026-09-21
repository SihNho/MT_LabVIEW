# c76-m3a3-run2-failpred

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.1506  in 32 / out 43236 / cache-create 181066 / cache-read 2373901  (577s, 29 turn(s))
- **date:** 2026-09-22 08:37:35
- **outcome:** ANSWERED (581s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. You are the adversary; your job is to find the strongest reason it is WRONG, not to agree with it.

## The failure

`tools/bench/build_d1_m3a3_run2.log` (recipe `tools/recipes/build_d1_m3a3.py`, `BGRUN END rc=1 after 125s`,
26 gates pass / 2 fail) ends with two failing gates, both about the SAME row:

    FAIL  P0 ROW D's SINK RESOLVED - wire 7506 appears EXACTLY ONCE on FlatSequence #7468's terminal table
          (the PREDICTION, written before the read)   FAILED PREDICTION - FlatSequence #7468 did not resolve
          to a readable Nodes[] terminal table (nodes_index None, 0 terminal(s))
    FAIL  [94 D VISA] ROW ACCEPTANCE (Pre-decided 85/...) - the row was WRITTEN at all

Its own discriminator line reads:

    DISCRIMINATOR: 7468 present in the FlatSequence census True, its owner column 'TopLevelDiagram' ; and
    owner_of(Diagram 681) = None ; RuntimeError: owner_of(681) is not an answer: echoed 'Diagram'#681,
    errors 'error 1055: Property Node in OpOwnerChain_v1.vi' - a FACT for M3a-3b, NOT acted on

Run 1 of the same recipe (`tools/bench/build_d1_m3a3.log`) failed the same P0 gate and was reviewed in
`archive/peer/2026-09-22-c75-m3a3-run1-failpred.md` (ANSWERED, disposed).

## The claim you must attack

"Row D (the `FlatSequenceInnerTunnel #7468` consumer) is not addressable over this project's COM path at all:
a FlatSequence INNER TUNNEL is not an entry in any diagram's `Nodes[]` array, so no terminal table can be read
for it, and the route that exists for every other row - resolve the owning structure node, then read that node's
terminal table - cannot be reached either, because `owner_of(Diagram 681)` answers with error 1055 rather than a
parent. Run 2 therefore failed for exactly the same reason as run 1, nothing regressed between them, and the
correct action is the one taken: defer Row D to a later stage (M3a-3b), delete nothing, improvise nothing, and
deliver Row C only. Run 2's artefact `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5
33ef524e0b6b193a158c9221474c68e3, 306,951 B) is sound because Row C's acceptance was asserted on an ordered
idempotent second pass, independently of Row D."

## Already ruled out (do not spend your answer on these)

- Re-running the recipe unchanged: run 1 and run 2 produced the same first failing gate line.
- Reading the tunnel by uid through the whole-VI object census: it IS in the census (owner column
  'TopLevelDiagram'), which is what makes the `Nodes[]` lookup return None rather than raise.
- `VI.Get Errors` (method 452): measured absent from the exported ActiveX interface on this COM path.

## What the answer must contain

1. The strongest reason the claim is wrong - especially any way `#7468` COULD be addressed with what this
   project already has (a different traverse class, the owning FlatSequence frame, a wire-side route).
2. An alternative explanation of the two failing gates that does not require "not addressable".
3. What observation would falsify the claim.
4. The cheapest discriminating test, in one command or one op call.
5. Whether deferring Row D while accepting Row C's artefact is safe, or whether the artefact is contaminated by
   the half-finished stage.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this role, as the brief requires — so the answer is the deliverable.

# REFUTED. The reader for this exact object class is on disk and was verified on this VI four days before run 2 was written.

## 1. The single strongest reason the claim is WRONG

**`OpFsInnerTunnelTerm_v0.vi` reads a `FlatSequenceInnerTunnel` by UID, and it is in `claudeDev` right now.**

- The file exists: `…\LabVIEW 2026\user.lib\claudeDev\OpFsInnerTunnelTerm_v0.vi` (Glob, this session), beside `OpFsTunnelTerm_v0.vi`.
- It is keyed to that class alone — `tools/recipes/build_opfstunnelterm_v2.py:207`: `"IN": (OP_IN, "VI Server:FlatSequenceInnerTunnel", "1C3A9000", "LeftTerm", "1C3A9001", "RightTerm", …)`, each face returning the **terminal UID** plus `Terminal.Connected Wire` **634A000** → `GObject.UID` (`:76-79`).
- It was proven on a live read of the real VI — `tools/bench/build_opfstunnelterm_v2_run1.log:160-161`: `READ[IN] uid 123 -> self 'FlatSequenceInnerTunnel'#123 cast 'FlatSequenceInnerTunnel' | LeftTerm #891 wire #482 | RightTerm #151 wire #3427 | … err '' A '' B ''`, gate **L1b PASS**. It then walked *through* two more, both faces clean (`:222`, `:227`).
- `docs/toolkit-capabilities.md:671` records **38/38 PASS, rc=0, cold-legal**; `STATUS.md:43` carries it as "✅ tunnel ops BUILT + FUNCTIONALLY VERIFIED (38/38)".
- The class is abundant on the target: **518** `FlatSequenceInnerTunnel` objects (`build_opfstunnelterm_v2_run1.log:24`). `#7468` is one of 518.

None of that touches `Nodes[]`, an owning-structure terminal table, or an owner walk. "Not addressable over this project's COM path at all" is false as written.

**Why the premise cannot carry the conclusion.** A `Tunnel` is a child of **GObject**, not of `Node` — `Generic → GObject → Tunnel`. So `Diagram.Nodes[]` *can never* contain a tunnel, in any VI, on any transport. `diag_c75_m3a3_rows.log:177` ("in no diagram's `Nodes[]`, 174 scanned") is a definition, not a measurement, and the inference one line later — `:178` *"no terminal table exists for it over this COM path"* — does not follow. The same source publishes the two properties that do apply, `Inside Terminals[]` ("one reference for each frame") and `Outside Terminal`; this project holds both IDs (**6356000**/**6356001**, `docs/NAMES.md:1020`) and an op that uses them **addressed by tunnel UID** (`OpTunnelRead_v0.vi`, `toolkit-capabilities.md:72`).

**The gate that failed is not about the tunnel.** `phase0_resolve_tunnel` read `FlatSequence #681` (`build_d1_m3a3.py:523`; `build_d1_m3a3_run2.log:64-66`: *"FlatSequence #681 #681 lives at: None (173 diagram(s) scanned of 173)"*). A `FlatSequence` **is** a Node, and a Node belongs to exactly one diagram's `Nodes[]` — so `lives at: None` is *necessarily* a reader or scope defect. The claim fuses a definitional truth about a tunnel with a reader bug about a structure and reports the sum as a property of the machine.

Three details the log does not say:

| the claim | the log |
|---|---|
| "`owner_of(Diagram 681)` … error 1055" | `owner_of(#686)`, not 681 — `build_d1_m3a3_run2.log:62-63` |
| "`7468` present in the FlatSequence census, owner column `'TopLevelDiagram'`" | that row is **#681** — `:40`, `:63` |
| 1055 ⇒ "no parent" | 1055 is *"Object reference is invalid"*, and in this fleet it is the **class-refusal** signal — the FSIT op answers 1055 to a `FlatSequenceOuterTunnel` and a `LoopTunnel` (`…v2_run1.log:189,:196`). `owner_of(#686)`'s 1055 is the **documented** FlatSequenceFrame termination (`toolkit-capabilities.md:61`): positive evidence #686 is a frame diagram |

The owner column is the owner's **class** (`gscript.py:489,:499` — `Class Name 3`). `TopLevelDiagram` is a real class under `Diagram`, and here it is exactly what an object sitting on the VI's top diagram reports (`tools/bench/astra_wiring.log:2-9`). The census was **handing over #681's address**; it was read as noise.

## 2. Alternative explanation of the same two gates — no "not addressable" required

`Diagram #686` is a **frame diagram of `FlatSequence #681`**, and `#681` sits on the **top-level diagram**. `find_node` can only enumerate `report_all('Diagram')` rows and call `node_labels(i)` over them (`build_d1_m3a1.py:541-569`). If the root diagram is not a row of that census — or is a row whose `node_labels` omits FlatSequence members — **#681 is invisible to that reader by construction**, exactly as #7468 is invisible to `Nodes[]` by construction. Both gates then fail with nothing unaddressable: P0 cannot see a top-level node, and the Row-D gate is downstream of P0.

Supporting shape in the same log: **19 of 21** flat sequences report owner `'Diagram'`; the only two reporting `'TopLevelDiagram'` are **#681** and **#12938** (`:40`, `:49`).

Plainly: the evidence **does not distinguish** (a) root diagram absent from `Traverse('Diagram')`, (b) present but `node_labels` omits FlatSequence there, (c) hint index 0 is not the root despite `gscript.py:608`. Any explains it; none is the claim; all three are cheap to separate.

This branch is not new — run 1's review named it (*"a reader defect with a findable location"*, `archive/peer/2026-09-22-c75-m3a3-run1-failpred.md:119`, left **live** at `:115`). Run 2 ran that review's §4 measurement, then filed its answer as an un-actionable FACT. "Run 2 failed for exactly the same reason as run 1" is true — and it is the finding, not the defence.

## 3. What would falsify my position

`OpFsInnerTunnelTerm_v0.vi` on uid **7468** returning the refusal signature — `cast ''`, `LeftTerm #0 wire #0`, `RightTerm #0 wire #0`, 1055 on both faces, i.e. what it gives a SubVI (`:167`) or a `LoopTunnel` (`:189`). Also sufficient: faces non-zero but **neither** face's `Connected Wire` is **7506**, leaving the identity unconfirmed.

A **narrower** claim would survive, and nobody has made it: `#7468` is **readable but not yet writable**. `Terminal.Connect Wire` **6349C03** is invoked on the **sink** (`docs/NAMES.md:245,:847`), and Row D's sink is the tunnel face while its source is the bare register OUTER — the transpose of `OpConnectFromWire_v0` (`diag_c75_m3a3_rows.log:16-18`). The missing piece is one **additive** op: the FSIT front (`UID → TMSC(FSIT) → RightTerm`) feeding `Connect Wire`, source fetched *inside* the same op via `OpConnectNested_v1`'s existing `Traverse('Diagram')[19] → TMSC → Nodes[] → IA → Node.Terms[] → IA` ladder — the "no refnum crosses COM" pattern built four times already (`toolkit-capabilities.md:64,:66,:68,:70`). A missing **writer**, not an unaddressable object. That is M3a-3b's real brief.

## 4. The cheapest discriminating test

One read-only op run, ~1 s, no mutation, wire 7506 untouched, on `D1_s3b_m3a3_20260922_081056.vi`:

```
OpFsInnerTunnelTerm_v0.vi    UID = 7468
   (idiom: read_any(TARGET, 7468) — build_opfstunnelterm_v2.py:56-57 picks the op by owner class)
```

- faces non-zero, no error, one face's `Connected Wire` == **7506** → the claim is dead; Row D has an address **today**.
- faces `#0` with 1055 both → the claim survives for the read too, and I am wrong.

Then 1 s more for the #681 half: `report_all(target, "TopLevelDiagram")`. Present → the root diagram is in the census and the defect is inside `node_labels`; absent → `find_node` structurally cannot see top-level nodes, a one-line fix that also explains #12938.

## 5. Deferring Row D, and whether the artefact is contaminated

**The deferral is safe and Row C's acceptance is sound.** 7506 was not deleted, nothing improvised; the rows touch disjoint nets (4859/7506) and disjoint sinks, so Row D's absence cannot change Row C's source identity. Row C's acceptance is a property of net **25231** — one source terminal of any class, `RightShiftRegister #23895`, PD85 0, on an ordered idempotent second pass with `wire_delta` 0 — junk `Invoke` purged 634→635→634, four md5 pins and the M3a-2 input unchanged (`STATUS.md` lock `purpose:`).

**One contamination the claim omits: the artefact is a half-stage wearing a clean stage name.** `D1_s3b_m3a3_20260922_081056.vi` has `Global #7202` re-sourced while `#7468` is still fed by the OLD `#4334` OUTER, and the filename says nothing. This is the hazard run 1's review flagged (`…run1-failpred.md:148`) and which has **already** materialised once — the rejected run-1 file still sits under its clean name because the rename was refused. A later cycle adopting this as "M3a-3's output" inherits a consumer still reading the loop being replaced: the rule-1a failure Pre-decided 69 exists to catch. STATUS says Row D is deferred; the *file* does not. Stamp it, or record `#7468 → #4334` beside the md5 pin, before it becomes anyone's bed.

## What the claim gets right

Nothing regressed between the runs, and the first failing gate is identical for an identical reason. Not deleting 7506, improvising no address, refusing a GUI fallback — all correct. And the `Nodes[]` route for the tunnel genuinely does not exist; it just never could, and that constrains no other route.

**Sources:** [Tunnel class — LabVIEW Wiki](https://labviewwiki.org/wiki/Tunnel_class) · [GObject class — LabVIEW Wiki](https://labviewwiki.org/wiki/GObject_class) · [VI Server Class Hierarchy — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [Error 1055 from a Property or Invoke Node — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE) · [Anatomy of a VI and Common VI Objects — NI](https://www.ni.com/docs/en-AS/bundle/labview/page/anatomy-of-a-vi-and-common-vi-objects.html) · [How to change tunnel mode using VI scripting — NI Forums](https://forums.ni.com/t5/LabVIEW/How-to-change-tunnel-mode-using-vi-scripting/td-p/3969392)

## Sources

(extract from answer)

## What was done with it

Dispatched by the **Jev-integration MATERIAL session** of 2026-09-22 (docs/jev-integration-plan.md rows #2/#5),
because `guard_peer` refused every bgrun while `tools/bench/build_d1_m3a3_run2.log` had no review newer than it.
That session owns no part of M3a-3, so it records the findings and acts on none of them — per CLAUDE.md §3 the
design calls below belong to a judgement session.

1. **ACCEPTED, and it refutes the claim — `#7468` HAS an address today.** `OpFsInnerTunnelTerm_v0.vi` exists in
   `claudeDev`, is keyed to `VI Server:FlatSequenceInnerTunnel` (`tools/recipes/build_opfstunnelterm_v2.py:207`)
   and was proven on a live read (`tools/bench/build_opfstunnelterm_v2_run1.log:160-161`, 38/38,
   `docs/toolkit-capabilities.md:671`). A `Tunnel` descends from GObject, not Node, so "absent from every
   `Nodes[]`" is a class fact that constrains no other route. **NOT ACTED ON HERE:** the discriminating read
   (`OpFsInnerTunnelTerm_v0` on uid 7468, read-only, ~1 s) touches LabVIEW and belongs to the M3a-3b stage.
2. **ACCEPTED as a correction of the record:** the failing `phase0` gate read `FlatSequence #681`, not the
   tunnel; the `owner_of` 1055 was on `#686`, not `681`; and 1055 is this fleet's class-refusal signal, not
   "no parent" (`build_d1_m3a3_run2.log:62-66`, `…v2_run1.log:189,:196`).
3. **ACCEPTED, and it is the one line a judgement session should read first:** the evidence does not
   distinguish three reader defects in `find_node` (root diagram absent from `Traverse('Diagram')` · present but
   `node_labels` omits it · hint index 0 is not the root), and run 1's review had already named that branch and
   left it live (`archive/peer/2026-09-22-c75-m3a3-run1-failpred.md:115,:119`).
4. **ACCEPTED, no action taken:** Row D's deferral is safe and Row C's acceptance stands (disjoint nets
   4859/7506, disjoint sinks) — but `D1_s3b_m3a3_20260922_081056.vi` is a HALF stage under a clean stage name.
   Renaming a delivered artefact is a judgement call and was left alone; this note is the record.

Nothing in `tools/recipes/`, `STATUS.md`, `cycle_runner.py` or any `.vi` was touched by this session.
