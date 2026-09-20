# fstunnel-orphans-empty-at-ckpt00-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $5.1740  in 30 / out 53214 / cache-create 236150 / cache-read 2248309  (747s, 29 turn(s))
- **date:** 2026-09-18 12:50:10
- **outcome:** ANSWERED (749s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION — the "donor orphan wire" story may be inverted. Attack it.

## The prediction, and what the machine said

Recipe `tools/recipes/build_opfstunnelterm_v1.py` copies a donor VI `OpWireSource_v5.vi` and rebuilds its front
half. Its checkpoint CKPT[00] is `_v1.py:403` (`by = sweep(op)`), immediately after `shutil.copy2(DONOR, op)` +
`open_panel(op)` and BEFORE any construction.

PREDICTED (gate A0a of `tools/recipes/build_opfstunnelterm_v2.py`, and the brief this run executed): on the FRESH
donor copy at `_v1.py:403`, the set of Wire uids that NO owning-node terminal reads at either end ("the orphan
set") is EXACTLY {894, 1356}.

OBSERVED (`tools/bench/diag_fstunnel_preclean_twins.log`, gate P4 FAIL):
  "PRECLEAN @_v1.py:403: 42 wires, 111 node terminals, ExecState 1; orphan set (no owning-node terminal at either
   end) = []"
The orphan set at the fresh copy is EMPTY. Both 894 and 1356 exist as Wire objects at that point (they are in the
42-wire census, and they are in the DONOR FILE's own census), but every one of the 42 wires is carried by at least
one node terminal there.

At the LATER B4 point of the same recipe, the SAME function over the SAME kind of sweep finds them as orphans:
`tools/bench/diag_fstunnel_rbwvictims.log:79-88` ("END NONE" for both), and `remove_bad_wires_scripted` at B4
removes exactly [894, 1356], adds none, 43 -> 41 wires, ExecState 0 -> 1, with no node losing a connection
(133 -> 133 terminals) — reproduced again in this run's twin A:
  "RBW @TWIN A @B4: ExecState 0 -> 1; 43 -> 41 wires; REMOVED [894, 1356]; ADDED []; err ''"

So the same two wires are ATTACHED at `_v1.py:403` and DETACHED by the B4 point.

## The explanation formed under pressure — refute it

E-new: 894 and 1356 are wires of the donor's FRONT SECTION (the `Wire.Terms[]` property node #145 and/or the
`Index Array` #151, and/or the nodes the recipe deletes next). `_v1.py:426-441` deletes Node #145, Node #151 and
the three wires 578 / 639 / 533 by index. Deleting a NODE leaves wires that terminated on it with no node
endpoint, so the recipe's OWN deletes create the two orphans; the donor merely supplies the wire objects in an
attached state. If that is right, then "the donor ships two bad wires" (written into STATUS.md, into
`docs/toolkit-capabilities.md`, and into gate A0a of `_v2.py`) is a mis-statement of the measurement, there is
nothing to pre-clean before construction, and the end-of-build `remove_bad_wires_scripted` is removing debris the
build itself produced.

Attack this. In particular:
 1. Give the strongest reason E-new is WRONG. Is there a reading of LabVIEW's scripting model under which a wire
    can be "on a node terminal" at the fresh copy and legitimately orphaned later WITHOUT any delete causing it —
    e.g. a wire whose endpoints are STRUCTURE terminals (tunnels) rather than node terminals, so that a sweep over
    `OpNodeTerms` of diagram-0 NODES reports it differently depending on what else is on the diagram?
 2. Name an ALTERNATIVE explanation of "orphan set empty at :403, {894,1356} at B4" that does not involve the
    recipe's deletes. Candidates to consider and to attack: the sweep is bounded (`sweep(target, n=120,
    diagram=0)` stops at the first index returning no uid) and at :403 it saw 19 nodes / 111 terminals while at B4
    it saw more nodes / 133 terminals — could the :403 sweep have enumerated DIFFERENT objects (e.g. included a
    node later deleted whose terminals carried 894/1356)? Could `OpNodeTerms`' `wire` column mean something other
    than "the wire attached to this terminal" for an unwired or a broken terminal, such that a stale/garbage uid
    coincidentally matches 894 and 1356 at :403?
 3. What would FALSIFY E-new, and what is the CHEAPEST DISCRIMINATING TEST? Our candidate is: at `_v1.py:403`,
    print the (node uid, terminal name, terminal index, is_source) of every terminal whose `wire` column equals
    894 or 1356, then re-read the same after each of the recipe's deletes. Say whether that test actually
    discriminates, and what a null result (no terminal names them, yet the orphan set is still empty) would mean.
 4. If E-new stands, what ELSE in this project's written record is wrong as a consequence? We claim only that
    gate A0a of `_v2.py` becomes unsatisfiable. Say what else follows.

## Already ruled out — do not spend the answer on these

* Not a reproduction problem: twin A of this same run reproduced the recipe's construction object-for-object
  against run 1 (terms 145 / ia 151 / tmsc 1044 / consumers [157,1319,1326]; site wires 384,384,1694,1719,1719,1766)
  and its B4 `ExecState` is 0, exactly as run 1 measured.
* Not a `Wire.Is Broken?` perturbation: no such read was taken anywhere in this run.
* Not an RBW side effect before B4: the only `remove_bad_wires_scripted` calls in the diagnostic are gated by a
  flag that refuses before a B4 freeze, and the twin B that aborted never called it.
* Not a file-corruption question: all 95 originals are md5-identical before and after, nothing was saved, and both
  scratch VIs were created and deleted in the same run.
* The two wire uids ARE in the donor FILE's own census (`tools/bench/diag_fstunnel_rbwvictims.log:14`) — that part
  is not in dispute. What is in dispute is whether they are ORPHANED in the donor.

## Files worth opening

`tools/bench/diag_fstunnel_preclean_twins.log` and `.py` (this run) · `tools/bench/diag_fstunnel_rbwvictims.log`
(the earlier measurement, 18/18) · `tools/recipes/build_opfstunnelterm_v1.py:376-450` (build_one up to B2) ·
`tools/recipes/build_opfstunnelterm_v2.py` (gate A0a) · `docs/toolkit-capabilities.md` (the donor-orphan claim) ·
`STATUS.md`.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**E-new is wrong, and so is the claim it replaces. Both rest on a reader that is structurally blind to the endpoint class these two wires actually have.**

---

## 1. The single strongest reason E-new is WRONG

**"Orphan" is a category error.** The measurement both stories are built on — `orphan_wires()` (`build_opfstunnelterm_v2.py:462-467`, re-typed at `diag_fstunnel_preclean_twins.py:161-166`) and `ends_of()`/`term_map()` (`diag_fstunnel_rbwvictims.py:335-348`) — sweeps `Diagram.Nodes[]` via `sweep()` (`_v1.py:248-255`). It answers *"does any **node** terminal read this wire?"*, and the project has been reading its answer as *"does this wire have an endpoint at all?"*

Your own reader already told you those are different questions. `OpWireSource_v5` reports, for each wire, exactly one real terminal whose `Terminal.Owner` is **`TopLevelDiagram` #3** (`diag_fstunnel_rbwvictims.log:81,87`). Per NI's own answer on exactly this behaviour: node terminals report their `Owner` as the node, but *"for the ControlTerminal, you get the Diagram/TopLevelDiagram or whatever place you have put in that indicator"* — because *"Items that inherit from the 'Control' class are front panel objects. The 'ControlTerminal' class represents the terminals for those controls on the diagram."* And `ControlTerminal → Terminal → GObject`; it is **not** a Node, so `Diagram.Nodes[]` can never return it.

Confirmed locally, without LabVIEW: the seed **control** created at `_v1.py:455` never appears in the node census. `diag_fstunnel_orphans.log:21` = 19 node uids fresh; `:105` = 23 at B4; the delta is exactly `{148, 154, 168, 169}` — the four new property nodes. The control's terminal is absent from both.

So at B4 those wires are **not endpoint-less**. Each still terminates on a front-panel object. E-new's premise — *"deleting a NODE leaves wires that terminated on it with no node endpoint"* — is true and irrelevant; its conclusion, that the recipe *created two orphans*, is unproven because nothing measured has ever been capable of detecting an orphan.

**A second, purely local error in E-new's own sentence:** `_v1.py` contains **zero** calls to `remove_bad_wires_scripted` (grep over the file: no hit). There is no "end-of-build RBW". `_v1` reaches `B5a` at `ExecState 0` and refuses to save (`_v1.py:554-558`). The RBW calls that removed `[894, 1356]` were made by the *diagnostics* at the B4 freeze (`rbwvictims.py:520`, `preclean_twins.py:177`) and by `_v2.preclean()`, which runs **before** construction. The clause "the end-of-build `remove_bad_wires_scripted` is removing debris the build itself produced" describes code that does not exist.

On your Q1 as posed: the structure-tunnel idea is the right *shape* of objection but the wrong object — a tunnel's terminal would report the **structure** as owner, not the top-level diagram. The measured owner names the diagram, which is the ControlTerminal signature.

## 2. Alternative explanation of "`[]` at :403, `{894,1356}` at B4" — no orphan is created anywhere

Both wires keep a live **panel** end throughout and lose only their **node** end:

| wire | `Is Source?` on its ControlTerminal | what that makes it | the node end `_v1.py:426-434` deletes |
|---|---|---|---|
| **1356** | TRUE (`rbwvictims.log:87`) | a **CONTROL** feeding a node input | Index Array **#151** `index` — the donor's `term_index`, label `"index 2"` (`opwiresource_v5_labels.json:14`) |
| **894** | FALSE (`rbwvictims.log:81`) | an **INDICATOR** fed by a node output | Terms[] PN **#145** `error out` — the donor gives every PN its own error indicator; `errT` = `"error out 3"` (`…_labels.json:4`) |

That reproduces every number with nothing left over: at `:403` each wire has two terminals (one node, one panel) → `ExecState 1`, orphan set `[]`; after the deletes each has one (panel only, loose other end) → invisible to a node sweep, and genuinely bad, so RBW removes it.

**The consequence E-new misses is the one that matters:** on this reading `_v1.py` **silently disconnects one front-panel CONTROL and one front-panel INDICATOR from every op it builds from this donor**, and no measurement taken could see it. `A0d`'s *"the TERMINAL count is unchanged (no node lost a connection)"* and M4's *"NONE — no terminal that was wired before RBW reads 0 after it"* (`rbwvictims.log:162-164`) count **node** terminals only. They are literally true and they conceal exactly the loss that occurred.

A second, weaker alternative, ranked below: the `wire` column at `:403` could carry a spurious non-zero value — `node_terms` returns `conn_err`/`wire_err` per row (`gscript.py:860-867`) and **neither diagnostic printed them**. I rank it low (it would have to coincide with both uids), but it costs nothing to print in the same run.

## 3. What would falsify each claim

- **Falsifies my reading (and restores E-new):** `panel_wiring()` on a fresh donor copy shows **no** row with `wire == 894` and none with `wire == 1356`. Then the `TopLevelDiagram` owner is not a ControlTerminal here and the wires really are endpoint-less.
- **Falsifies E-new:** a panel row naming 894/1356 that is **still there at B4** — the wire never became endpoint-less at all, so nothing was orphaned.

On your Q3: the test you propose discriminates E-new's *proximate mechanism* but not its *conclusion*, and **its null branch is logically impossible**. The orphan set and the per-terminal dump are computed from the same `sweep()` rows; "no terminal names them, yet the orphan set is still empty" cannot both hold unless two back-to-back `sweep()` calls disagree. So that branch tests only sweep determinism — worth one extra call and a diff, not a run.

## 4. Cheapest discriminating test

One read-only script, one throwaway copy, ~4 op runs, no construction, no new op, no GUI. **`panel_wiring` already exists and is already functionally verified** (`gscript.py:772-809`; `toolkit-capabilities.md:22`, `test_oppanelwiring.log` 11/11, "constructed orphan = exactly +1"):

1. `g.panel_wiring(op)` at `_v1.py:403` → print every row with `wire in (894, 1356)`: `label`, `indicator`, `is_source`.
2. The same call at the B4 freeze, and once more after RBW.
3. `wire_source_owner(op, 894)` / `(op, 1356)` at `:403` — expect **2** terminals there against the 1 measured at B4.
4. Your test (which sweep rows name 894/1356 at `:403`) in the same script — it answers the other half, *which node end was lost*.
5. Free: the `conn_err`/`wire_err` columns for those rows.

Rows at `:403` **and** at B4 ⇒ never orphans; the build silently strands two panel objects. No rows at either point ⇒ E-new stands. Caveat: `panel_wiring` is **not recursive** — cluster elements and tab pages are not rows, so a missing row is the next thing to rule out, not proof.

Separately, and it is the attribution nobody has made: at B4, `delete_object` **only** those two wires and read `exec_state`. The 0→1 flip has never been separated from `#384`'s `Is Broken? True → False` across the same RBW call (`toolkit-capabilities.md:600-601`). Twin B attempted this at the wrong point — `:403`, where the VI is already legal and there is nothing to remove.

## 5. What else in the written record is wrong (your Q4 — it is more than gate A0a)

- **`_v2.py`'s whole `preclean()` is unsatisfiable, not just A0a.** `A0c` (RBW removes exactly `[894,1356]`) and `A0d` (42 → 40, terminals unchanged) fail for the same reason: on a fresh copy at `ExecState 1` both wires are fully connected and RBW should remove nothing. **Drop `_v2`, don't patch it.**
- **`_v2.py:109-116`**, the stated reason for deleting gate A0b — *"BY CONSTRUCTION an A0a orphan has no sink"* — is wrong for 894, which has a sink: an indicator's terminal. Whether `Wire.Is Broken?` is reachable through `connect_ctl` (the panel-object wiring op, `gscript.py:929-948`) was never asked.
- **`docs/toolkit-capabilities.md:584-610`**: the heading, "every copy starts with two bad wires", and especially `:597` *"Removing exactly those two costs no node its connection"* — the dangerous sentence, true as written and hiding the loss it was used to rule out. Also `:595` "reports 2 terminals for each" mis-reads its own reader: `wire_source_owner` appends the empty sentinel row **before** breaking (`rbwvictims.py:242-244`), so the count is 1 real + 1 empty.
- **`STATUS.md`** carries the same claim.
- **Gate L1 of `_v1.py`** ("an EMPTY `errs` column") would pass **vacuously** on an indicator that is no longer wired, since a bare indicator reads its default forever. `read_tunnel`'s poisoning (`_v1.py:574-588`) covers the value outputs but not this.
- **Process:** this is not `tool-not-built`. `panel_wiring` was built and verified on 2026-09-14 and is listed one screen above the section that got this wrong. Four diagnostics in one cycle asked "what are this wire's ends?" with a node-only reader and none reached for it.

**What would change my mind:** step 1 above returning no panel row for either uid. I hold the ControlTerminal reading with high confidence on the external documentation and on your own 19→23 node census, but I have *not* measured that these two specific wires land on `"index 2"` and `"error out 3"` — that pairing is a named, falsifiable prediction for the test to confirm or kill, not a measurement.

Sources: [NI Forums — VI Scripting: inconsistent behaviour of terms[] of a wire / owner](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055) · [LabVIEW Wiki — ControlTerminal class](https://labviewwiki.org/wiki/ControlTerminal_class) · [LabVIEW Wiki — Wire class](https://labviewwiki.org/wiki/Wire_class) · [LabVIEW Wiki — GObject class](https://labviewwiki.org/wiki/GObject_class) · [LabVIEW Wiki — AbstractDiagram class/Nodes() property](https://labviewwiki.org/wiki/AbstractDiagram_class/Nodes()_property) · [NI — VI class: Block Diagram:Remove Bad Wires](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/vi_block_diagram058remove_bad_wires.html)

*(Note: I could not write the plan file — `Write` is disabled in this session, consistent with the read-only peer brief. The review above is the whole answer.)*

## Sources

(extract from answer)

## What was done with it

disposition: RELAYED TO JUDGEMENT (cycle 23, dispatch 4, material session, 2026-09-18 12:5x). Arm 2 of a `-Dual`
failed-prediction review; arm 1 = `2026-09-18-fstunnel-orphans-empty-at-ckpt00-codex.md`.

- **Outcome classified:** `ANSWERED` in 749 s, opus / effort max (web search allowed for this role),
  `COST: $5.1740  in 30 / out 53214 / cache-create 236150 / cache-read 2248309  (747s, 29 turn(s))` —
  `tools/bench/peer_orphans_empty.log`. Its own note says `Write` was disabled, so the review text is the whole
  deliverable.
- **Its NAMED, FALSIFIABLE PREDICTION was that the two wires land on `#151 "index" T[2]` and `#145 "error out"
  T[3]`. IT IS CONFIRMED, exactly, by measurement** — `tools/bench/diag_fstunnel_orphan_timeline.log`: at
  `_v1.py:403` **#894 -> node #145 `error out` T[3] (source)** and **#1356 -> node #151 `index` T[2] (sink)**,
  orphan set EMPTY; both become orphans at the first checkpoint after the recipe deletes those two nodes
  (`_v1.py:442`), where `ExecState` goes **1 -> 0**.
- **Its stronger claim is NOT measured here and is the open one:** that each wire's OTHER end is a PANEL object's
  terminal (a `ControlTerminal` / indicator terminal), which the node-only `OpNodeTerms` sweep cannot see — so the
  wires were never "bad", and deleting them from a fresh copy would cost a panel object its connection. Our run
  shows exactly ONE node terminal per wire at `_v1.py:403`, which is CONSISTENT with that reading but does not
  establish it; the panel-side read (`gscript.connect_ctl` / `panel_wiring`) was not run in this dispatch.
- **Its recommendations are NOT acted on** — "Drop `_v2`, don't patch it", the `_v2.py:109-116` objection to A0b's
  stated reason, the corrections it wants in `docs/toolkit-capabilities.md:584-610` / `:595` / `:597` and in
  `STATUS.md`, and its `_v1.py` gate-L1 vacuity point. Every one of those is a judgement decision about what to
  believe and what to change; they are relayed with the measurement and left open.
- **Process claim recorded, not adjudicated:** it argues this is NOT `tool-not-built` because `panel_wiring` was
  built 2026-09-14 and four diagnostics in one cycle asked "what are this wire's ends?" with a node-only reader.
