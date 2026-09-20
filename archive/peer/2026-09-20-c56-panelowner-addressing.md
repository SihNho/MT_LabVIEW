# c56-panelowner-addressing

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.4378  in 20 / out 40441 / cache-create 186008 / cache-read 1078610  (519s, 22 turn(s))
- **date:** 2026-09-20 22:37:15
- **outcome:** ANSWERED (520s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the following claim. It is the explanation formed, under time pressure, for a FAILED PREDICTION in
`tools/bench/diag_s56_transport3.log` (run by `tools/bench/diag_s56_transport3.py`, LabVIEW 2026, VI Scripting
over COM, read-only peer: do not run anything, do not edit anything).

THE FAILING GATES (verbatim from tools/bench/diag_s56_transport3.log):
  FAIL  A1 owner_of(#6) answered and diag_index resolved it  ('Panel', 3) -> index None
  FAIL  A2 wire_indicators returned an EMPTY error column on at least one attempt
        ['NOT ATTEMPTED: function index 102 / diagram_index None unresolved']
  FAIL  A3 a target indicator's wire uid changed from 0   attempt None -> wire None
Context lines from the same log:
  :21  A0 ControlTerminal uid 6 label VERBATIM 'File # Saved' (utf-8 hex 46696c652023205361766564),
       indicator=True, wire=0, is_source=False
  :25  A1 the target indicator's owner: owner_of(#6) = ('Panel', 3) [strict=True] error VERBATIM ''
  :26  diag_index(#3) raised ValueError: 3 is not in list
  :35  A1d the ALT indicator's owner: owner_of(#31543) = ('Panel', 3) [strict=True] error VERBATIM ''
  :68  B1 build_index_array(top-level, (6200, 5200)) -> new [{'i': 0, 'class': 'IndexArray', 'uid': 23486,
       'pos': (6200, 5200), 'owner': 'TopLevelDiagram'}] ; error VERBATIM ''
  :71  B1b the new IndexArray's owner diagram: owner_of(#23486) = ('TopLevelDiagram', 536) error VERBATIM ''
  :72  B2 node_info(max_n=40) AFTER the IndexArray: 1 entries -> [(0, 'Index Array', 'Index Array')]
  :75  B3 create_indicator(Nodes[0].Terminals[2]) -> new [{'i': 114, 'class': 'ControlTerminal', 'uid': 23541,
       'pos': (6224, 5203), 'owner': 'TopLevelDiagram'}] ; error VERBATIM ''
  :77  B3b the new indicator reads label None, indicator=None, wire=None   (looked up by uid 23541 in panel_wiring)
Earlier, on the SAME VI and the same source node (tools/bench/diag_s56_transport2.log:56), the call
  wire_indicators(node_class='Function', index=102, Names=['x .and. y?'], Names 2=['File # Saved'],
                  diagram_index=46)      # 46 = Traverse Diagram index of Diagram #639, the frame owning the source
returned  error 5001: LV-Scripting.lvlib:Wire Indicators.vi<ERR> | Control File # Saved not found.

THE CLAIM UNDER ATTACK, in four parts:
 (1) `tools/gscript.py:849,:859` show that `panel_wiring`'s `uid` column is `ControlUID`, i.e. the FRONT-PANEL
     CONTROL's uid - NOT its block-diagram terminal's uid. Therefore uid 6 is a Panel object, `owner_of` rightly
     answers ('Panel', 3), and the instruction "resolve diagram_index from the target indicator's own owner
     diagram" has NO resolvable value as written: a panel control has no owner Diagram.
 (2) The diagram that wire_indicators must be handed is therefore the diagram that owns the front-panel
     TERMINALS, and the log shows that is the TopLevelDiagram #536 (every ControlTerminal created in phase 2
     reads owner class 'TopLevelDiagram'; owner_of(#23486) = ('TopLevelDiagram', 536)). Traverse `Diagram`
     index 0 is #536, so the corrected call passes diagram_index=0.
 (3) Dispatch 3's 5001 "Control File # Saved not found" is explained by exactly this: erdosmiller's
     `Wire Indicators.vi` looks its `Indicator Names` up on `Diagram in` (fed from `diagram_index`,
     tools/gscript.py:1787-1788), it was handed frame #639, and no front-panel control terminal is owned by
     #639 - so the lookup could not find the control even though the control exists.
 (4) Phase 2 proves the top-level head is HEALTHY, not dead: `node_info` went from 0 entries to 1 the moment an
     Index Array existed there, and `create_indicator` then produced ControlTerminal #23541 (count 114 -> 115).
     So the earlier "create_indicator cannot reach this VI" reading was about an EMPTY Nodes[], not a broken
     `VI -> Block Diagram` reference; and B3b's label None does NOT mean the indicator is absent - it means
     panel_wiring is keyed by CONTROL uid, so a TERMINAL uid finds no row.

WHAT IS ALREADY RULED OUT (do not spend the answer on these):
  * The control does exist and is unwired: panel_wiring read it on the same scratch in the same phase
    (uid 6, label 'File # Saved', indicator=True, wire=0).
  * A label-bytes mismatch was checked with a SECOND reader: `fp_labels` index 7 returned the identical bytes
    ('File # Saved', hex 46696c652023205361766564), so no hidden newline or trailing space is involved.
  * The source terminal is wired: #10686 t0 'x .and. y?' is_source True, wire 10799, 3 of 3 terminals wired
    before and after.
  * Traverse-index staleness: #10686's Traverse `Function` index was re-resolved LIVE (102 of 183) and the
    Diagram indices were re-resolved live (#639 = 46, #686 = 19).

WHAT TO DO, as an adversary:
  a) Give the STRONGEST reason each of (1)-(4) is wrong, with the specific mechanism, not a doubt.
  b) Give an ALTERNATIVE explanation of the 5001 that survives the four "already ruled out" facts - in
     particular, say whether `Wire Indicators.vi` looks indicator names up through `Get Controls.vi` on a
     Diagram reference at all, or through the VI's Panel (in which case diagram_index would be irrelevant to
     the lookup and part (2) is a fantasy), and what the LV-Scripting library actually does with `Diagram in`.
  c) Say what OBSERVATION would falsify the claim that diagram_index=0 (the TopLevelDiagram) fixes the 5001 -
     and what a SUCCESS with diagram_index=0 would still leave unproven about the branch it creates.
  d) Name the CHEAPEST discriminating test, given these hard constraints: no VI may be RUN, no new op VI may be
     built, at most 3 calls of the verb, and every reading must come from existing ops
     (`report`/`report_all`, `panel_wiring`, `fp_labels`, `node_info`, `node_terms_uid`, `owner_of`, the
     `Wire.Is Broken?` carrier `connect_nested_v1`).
  e) Say plainly whether the corrected call is even the right question, or whether the evidence in phase 2
     (create_indicator WORKS on the top-level diagram) makes wire_indicators unnecessary for the transport
     indicators this work needs.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is wrong where it is actionable.** Parts (1) and (4) are factually right and inert; part (3)'s mechanism is probably right; part (2) — the only part that changes what gets run next — is circular, and this project has already *measured* the opposite on this same VI. The vendor record settles nothing: the public repo ships no per-VI documentation at all, only VIPM examples ([erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)), so "the lookup is scoped to `Diagram in`" rests entirely on a Context-Help sentence paraphrased in our own file (`com-driving.md:162-163`).

## 1. The single strongest reason the claim is wrong

**Part (2) proves "front-panel terminals live on the TopLevelDiagram" from a terminal that phase 2 had just placed on the TopLevelDiagram.** "Every ControlTerminal created in phase 2" is exactly one — #23541 (`log:75`) — created by a call that was *told* to work on Traverse Diagram 0 (`log:74`). The sample was manufactured by the hypothesis.

The premise is also false in general and false here:

- LabVIEW does not require FP terminals on the top-level diagram. The stock Stop-button-inside-a-While-loop is a control terminal owned by a structure diagram.
- **On a working copy of this very VI, six ControlTerminals were measured on frame `Diagram #639`** (`docs/d1-build-plan.md:1227`), and `Get Controls.vi` — the same library, the same name-lookup pattern — **raised 5001 at `src_diagram_index=0` and succeeded at 43 = #639** (`:1230-1231`).
- This VI's top-level diagram holds **zero nodes** (`log:67`, `transport2.log:42-44`). The author never used it.

So the claim prescribes the one value already measured to produce 5001 on this VI, and rejects the family already measured to work.

Part (3) then **refutes part (2) rather than supporting it.** `Wire Indicators.vi` *branches the indicator onto the wire already attached to the source* (`gscript.py:1765-1770`). Source wire 10799 lives inside #639 (`diag_s3a_ind_transport.log:28-32`). An indicator found on the top-level diagram cannot join a wire inside a case frame without a border object — and the failing run created none (#637 stayed 59/48, `log:47`). Under its own premise the corrected call is self-contradictory. Confirming this: the fleet's **only** measured WI success with an explicit index is `build_setcommand_signed.py:122` with `READ_DIAGRAM = 1` (`:32`) — a **case-frame diagram, not the top level** — wiring `'read buffer 2'`, whose terminal sat on the net deleted inside that frame (`:111-112`). Every WI success here passed the diagram owning *both* the source wire and the indicator terminal.

Two smaller faults: part (1)'s "NO resolvable value as written" is one hop short, not impossible — `Control[Terminal] → GObject.Owner` is a ladder `OpPanelWiring_v0` already half-walks (`gscript.py:831-834`); turning "our op doesn't return it" into "it has no meaning" is what licensed the guess. And part (3) cites `gscript.py:1787-1788` for a data path those lines don't show (they set `Class Name 2`/`index 2` on the op); the actual evidence is `archive/2026-08-29-status-sweep-opexitloop-opwireind.md:69-70`.

Part (4) is right about the empty `Nodes[]` (`gscript.py:2399-2402` records 1055 on all 20 s3a calls) and irrelevant in the direction it implies: **`create_indicator` addresses top-level `Nodes[]` only** — this project's own recipe says so (`build_setcommand_signed.py:113-115`) — and every source this work needs is inside a structure. Phase 2 confirmed a scope limit; it did not open a route.

## 2. Alternative explanation of the same 5001

**`'File # Saved'`s terminal is on neither #639 nor the top-level diagram — it is inside one of the six While loops or another frame.** Dispatch 3's 5001 then carries exactly one bit, "not on #639", and `diagram_index=0` reproduces it verbatim. Nothing in the ruled-out list touches this: the control exists, the bytes match, the source is wired, the indices are live — and none of that locates the *terminal*.

Weaker but live, and the one that would make part (2) a fantasy: 5001 may be a **connection** failure, not a lookup failure. This project corrected itself on precisely that point once (`docs/d1-build-plan.md:1241-1243`: "the library may raise it for a *connection* failure as readily as a *lookup* failure"). The message text argues against it here, but with no vendor documentation the measurement does not distinguish the two cleanly.

## 3. What would falsify the claim

- A `ControlTerminal` census showing terminals owned by class `Diagram` rather than `TopLevelDiagram` — that kills premise (2) before any verb call.
- The same `5001 Control File # Saved not found` at `diagram_index=0`.

**What a success at `diagram_index=0` would still leave unproven:** that the branch joined the intended net (a branch creates no Wire object — `gscript.py:1771-1772`); that the border was crossed legally (no tunnel was created in the failing run, and a cross-diagram branch must create one); that the VI survives — both recorded cross-border WI attempts in this fleet ended ExecState 0 (`case_out_probe.log:32,39`; `build_track_kernel_v1.log:59-63`, "wires 31->33 ExecState 0"); that the state is durable (ExecState went 1 → 0 after the `Is Broken?` read in *both* dispatches, `log:58`, `transport2.log:69`); and anything functional — no VI may be run, so the indicator is never shown to carry a value.

## 4. Cheapest discriminating test

**Step 1 costs zero verb calls and may end the question:** `report_all(scratch, 'ControlTerminal')` — 114 rows, each carrying the owner-class column that already printed `TopLevelDiagram` at `log:68,75`. Group by owner. Claim predicts 114/114 `TopLevelDiagram`; the alternative predicts a large share owned by `Diagram`.

**Step 2, only if step 1 leaves it open — one verb call:** dispatch 3's exact call with `diagram_index=0` and the name **`'File # Saved'`**, reading ExecState and #637's terminal count in the same pass, plus `connect_nested_v1`'s `Wire.Is Broken?` on 10799 on any success.

⚠️ **Never probe with `'Image'`.** A2's plan (`log:37,40`) targeted uid 31543 = `PlugInControl` = the IMAQ Image Display, which two local records say this library cannot address at all (`build_opconnectctl_v0.py:3` "5001 twice"; `build_harness_dispI.py:162`). Had `diagram_index` resolved, that attempt returns 5001 under *every* hypothesis — and would most likely have been read as refuting the diagram theory.

## Is the corrected call even the right question? No.

Under the claim's own mechanism the only diagram that can carry a legal branch is the source's own #639 — so the question is not "which index" but **"can the indicator's terminal be moved into #639"**, which is exactly `diag_s3a_ind_transport`'s route B (`move_in`), never executed because route A produced no terminal. And the single unknown the whole dispatch turned on — the owner diagram of uid 6's *terminal* — is one property read off a reference an existing op already holds. The cycle's "no new op" pre-decision is what forced a guess in its place; two dispatches of guessing against one op VI is a trade worth putting to the user rather than absorbing silently.

I hold parts (1), (3)-mechanism and (4); I reject the prescription. What would change my mind: a ControlTerminal census showing all 114 owned by the TopLevelDiagram.

Sources: [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting) (examples only — no per-VI API docs), [LabVIEW Scripting Tools (VIPM)](https://www.vipm.io/package/lava_lib_labview_api_scripting_tools/), [Programmatically Scripting VIs in LabVIEW](https://rajsite.github.io/unofficial-lvdocs/lvconcepts/scripting_property_method.html).

## Sources

(extract from answer)

## What was done with it

**RECORDED, NEITHER ACCEPTED NOR REJECTED (`docs/cycle27-plan.md` Pre-decided 41(b)). NOTHING IN IT WAS ACTED
ON.** This was a FORCED review: `guard_peer.py` blocked the next build over `tools/bench/diag_s56_transport3.log`
(first failing gate `A1 owner_of(#6) answered and diag_index resolved it  ('Panel', 3) -> index None`), and a
material session may not accept or reject a review's substance. Concretely, after it landed: no script was
edited, no gate redesigned, nothing re-run on its advice, no op VI built (Pre-decided 2), `gscript.py` untouched,
the attempt plan not altered, and its §4 step 2 not adopted as a decision. `docs/cycle27-plan.md`, `CLAUDE.md`
and `docs/NAMES.md` were not changed on it.

**Why the next run is not "acting on it":** `tools/bench/diag_s56_transport3b.py` was WRITTEN AND AST-CHECKED
BEFORE this exchange was dispatched (`tools/bench/c56m5b_astcheck.log`, then `guard_peer` refused the launch and
this review was dispatched in response). Its gate `E0 every ControlTerminal reads owner class 'TopLevelDiagram'`
— the census this review names in §3 and §4 as the falsifier — was already in that file, arrived at independently
from `log:75`. It was therefore left exactly as written, including the attempt-2 probe on the next unwired
indicator row, which this review argues is worthless (uid 31543 = `PlugInControl`, the IMAQ Image Display).
Changing that would have been accepting the review.

**What it says, for judgement, in one line each — every point is the REVIEWER's, none is endorsed here:**
- It calls the claim "wrong where it is actionable": parts (1) and (4) right but inert, (3)'s mechanism probably
  right, and **(2) — the `diagram_index = 0` prescription — circular**, because "every ControlTerminal created in
  phase 2" is exactly ONE terminal (#23541) which phase 2 had just placed on Traverse Diagram 0.
- It cites `docs/d1-build-plan.md:1227` and `:1230-1231` as this project's own OPPOSITE measurement on this VI:
  six ControlTerminals measured on frame `Diagram #639`, and `Get Controls.vi` raising **5001 at
  `src_diagram_index=0`** while succeeding at 43 = #639.
- It argues (3) refutes (2): WI BRANCHES onto the source's existing wire, wire 10799 lives inside #639, and a
  top-level indicator cannot join it without a border object — none was created (#637 stayed 59/48).
- Its alternative 5001: `'File # Saved'`s TERMINAL is on neither #639 nor the top level, so the 5001 carries one
  bit ("not on #639") and `diagram_index=0` would reproduce it verbatim; weaker but live, 5001 may be a
  CONNECTION failure, not a lookup failure (`docs/d1-build-plan.md:1241-1243`).
- Its falsifiers: a ControlTerminal census with owners of class `Diagram` rather than `TopLevelDiagram`; or the
  same 5001 at `diagram_index=0`.
- Its list of what a SUCCESS at 0 would still leave unproven: which net the branch joined, whether the border was
  crossed legally, whether the VI survives (both recorded cross-border WI attempts ended ExecState 0), durability,
  and anything functional (no VI may be run).
- Two corrections of OUR citations: part (1) is "one hop short, not impossible" — `Control[Terminal] →
  GObject.Owner` is a ladder `OpPanelWiring_v0` already half-walks (`gscript.py:831-834`); and `gscript.py:1787-1788`
  does not show the `Diagram in` data path (it sets the op's controls) — the evidence it names is
  `archive/2026-08-29-status-sweep-opexitloop-opwireind.md:69-70`.
- Its answer to "is the corrected call the right question": **No** — the question is whether the indicator's
  TERMINAL can be moved into #639 (`move_in`, route B of `diag_s3a_ind_transport`, never executed), and the one
  unknown the dispatch turned on is a single property read off a reference an existing op already holds.
- Its closing claim is a PROCESS one, addressed to the user and left to judgement verbatim: *"The cycle's 'no new
  op' pre-decision is what forced a guess in its place; two dispatches of guessing against one op VI is a trade
  worth putting to the user rather than absorbing silently."*

Cost, for the comparison record: **$3.4378**, in 20 / out 40,441 / cache-create 186,008 / cache-read 1,078,610,
520 s, 22 turns; `BGRUN END rc=0 after 521s`, log `tools/bench/peer_c56_panelowner_addressing.log`.
