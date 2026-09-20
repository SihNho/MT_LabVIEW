# c53-g2b-caseselector

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.2538  in 40 / out 37625 / cache-create 115603 / cache-read 2216671  (493s, 40 turn(s))
- **date:** 2026-09-20 06:24:08
- **outcome:** ANSWERED (497s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It is a diagnosis formed under pressure after a failed prediction in
`tools/bench/c53_row_class.log` (script `tools/bench/c53_row_class.py`). Do not confirm it. Find the
strongest reason it is WRONG, give an alternative explanation, say what would falsify it, and name the
cheapest discriminating test that separates the two — a test that reads FILES only (no LabVIEW, no COM;
this session is forbidden to open a VI for this question).

## What was predicted and what was measured

Gate `G2b` predicted: for the five nodes {10407, 48, 3529, 3560, 3447}, the number of WIRED terminals
counted from `tools/bench/main_vi_netmap.json`'s per-node `terms` array would equal the number of cut
rows those five nodes own in `tools/bench/d1_rewire_sources.json`.

    predicted 17 == 17
    MEASURED  16 != 17
    failing line: "  FAIL  G2b  netmap WIRED terminals on the 5 uids = 16 ; cut rows = 17"

Per-node totals measured from the netmap `terms` array (total/wired):
    10407 -> 6/6      48 -> 7/7      3529 -> 1/1      3560 -> 1/1      3447 -> 1/1     (sum 16)
Per-node cut rows in `d1_rewire_sources.json`:
    10407 -> 7 (indices 0..6)   48 -> 7 (0..6)   3529 -> 1   3560 -> 1   3447 -> 1     (sum 17)

Three other gates in the SAME script PASSED against the SAME netmap file:
  * `G2` — the netmap's `diagrams["43"]["wires"]` table yields exactly **17** terminal ends on those
    five uids, matching the 17 cut rows.
  * `G3` — for all 17 rows the wire uid in `d1_rewire_sources.json` equals the wire uid the netmap's
    `wires` table records at the same (node, terminal index).
  * `G4a/G4b` — `diagram_owners[43] == "WhileLoop"`, `diagram_owners[19] == "FlatSequenceFrame"`.

Raw netmap entry for the node in question (verbatim):

    "10407": {"label": "", "terms": [["# slices in stack", 9635],
                                     ["Index of closest\ncal image slice, bead 2", 10990],
                                     ["Outgoing Handle", 11232],
                                     ["VISA out", 7337],
                                     ["Out position", 7388],
                                     ["position [internal units]", 9113]]}

    "48":    {"label": "", "terms": [["-Inc reference", 4833], ["+Inc reference", 2819],
                                     ["Focus inc reference", 1893], ["VISA resource name", 1731],
                                     ["In position", 3947], ["Out position", 7388],
                                     ["Outgoing Handle", 11232]]}

`d1_rewire_sources.json` row for uid 10407 index 0 (verbatim, file line 1748):
    {"uid": 10407, "i": 0, "name": "", "is_source": false, "wire": 10799,
     "dest": "1.5", "other_ends": [{"kind":"node","diagram":"43","uid":10686,"i":0,
     "name":"x .and. y?","is_source":true}], ... "action": "cross-loop:1.2->1.5"}

`#10407` is a LabVIEW **Case Structure**. `#48` is a subVI call (`ASI_adjust focus-subvi.vi`).

## The explanation I formed (ATTACK THIS)

"The netmap's per-node `terms` array omits the Case Structure's SELECTOR terminal. The one terminal
present in `d1_rewire_sources.json` but absent from the netmap `terms` array is exactly
`#10407 i=0, name "", wire 10799` — the selector, fed by `#10686 'x .and. y?'`. Every other terminal
of #10407 lines up one-for-one and in the same ORDER once that first entry is dropped, i.e. the
netmap `terms` index k corresponds to `d1_rewire_sources` index k+1 for this node only. Therefore the
two files disagree only in the per-node `terms` ARRAY, the netmap's own `wires` table is complete, and
the 17-row cut set is correct."

## Already ruled out

* Not a missing wire: wire 10799 IS present in the netmap's `diagrams["43"]["wires"]` table, as
  `"10799": [[24, 0, ""], [25, 0, "x .and. y?"]]`, and node position 24 in that diagram resolves to uid 10407.
* Not an off-by-one in my own index map: `G3` compared all 17 (node, index) -> wire uid pairs against the
  netmap `wires` table and found zero mismatches.
* Not a stale file: both JSONs name the same source VI and the same 170-diagram census.

## What I need from you

1. The strongest reason the "selector is omitted" story is wrong.
2. At least one alternative explanation for a 6-vs-7 terminal count on a Case Structure in two censuses
   produced by the same toolkit (consider: a different `Terminal`/`Node.Terminals` property being read,
   subdiagram terminals, tunnels counted as node terminals, a filter on unnamed terminals, and the
   possibility that the netmap `terms` array is correct and `d1_rewire_sources.json` invented an index 0).
3. What observation would FALSIFY my story.
4. The cheapest file-only discriminating test, naming the file(s) to read. Candidate files that exist in
   `tools/bench/`: `main_vi_nodeterms.json`, `d1_step0_census.json`, `orig_3state_nodeterms.json`,
   `diagram19.json`, `frame_loop_state.json`, `main_vi_netmap.json`, `d1_rewire_sources.json`.
   Note whether any OTHER node in the netmap shows the same 1-terminal shortfall — if the shortfall is
   Case-Structure-specific that supports my story, if it is general it refutes it.

This matters because the number under test is the CUT-ROW COUNT for the next build stage (moving that
node set into a new loop). If the true count is 16, not 17, one terminal would be silently left unwired.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## Verdict: the claim is wrong about the mechanism, wrong about the scope, and it has already been falsified by files in `tools/bench/`. The number 17 survives — for a different reason.

---

## 1. Strongest reason the claim is WRONG

**The netmap's `terms` array does not omit "the selector". It omits *every terminal whose name is the empty string*, on every node of every class, by an explicit filter in the writer:**

`tools/bench/sweep_netmap_main.py:63-64`

```python
rec["nodes"][str(uid)] = {"label": lbl,
                          "terms": [[t, w] for _ti, t, w in terms if t]}
```

`t` is the terminal **name**. `if t` drops every unnamed terminal — and `_ti`, the real terminal index, is thrown away, so a `terms` index carries **no information at all** about a terminal index.

The project wrote this down six days before the failed prediction, in a comment, while building the very file used to corroborate the story — `tools/bench/sweep_nodeterms_main.py:74-76`:

```python
# the cache stored only NAMED terminals with their wire; compare on that subset, in order
mine_named = [(nm, w) for nm, w in mine if nm]
if mine_named[:len(theirs)] != theirs:
```

That comparison ran over **626 nodes** and reported **zero terminal-content mismatches** — all 11 logged mismatches are the same `"node index out of range (UID 0)"` artefact for uid 22963 (`tools/bench/sweep_nodeterms_main.log:189-200`). So the netmap `terms` array is already known to equal the *named subset, in order*, for the whole VI. G2b did not discover a Case Structure quirk; it rediscovered a documented write-time filter and attributed it to the nearest interesting object.

Two consequences the claim gets wrong in a way that matters:

- **"index k ↔ index k+1 for this node" is a coincidence, not a rule.** Unnamed terminals occur at i=1, 2, 6, 7 and 37, not only at i=0 (`main_vi_nodeterms.json:776-777`, `:498-499`, `:836-837`, `:848-849`, `:6869-6870`). For a node whose unnamed terminal sits in the middle, the offset starts mid-array; for a node with several, it is >1. Because `_ti` is discarded, the `terms` array can never be used as a per-terminal index map.
- **`d1_rewire_sources.json` did not invent index 0.** A *third* census, taken with a different op (`OpNodeTerms_v0` via `node_terms_uid`, not `OpNetInfo_v0` via `net_map`), records it independently: `main_vi_nodeterms.json:12806-12814` → `uid 10407, i 0, name "", wire 10799`.

## 2. Alternative explanation of the same evidence

**Two tables, two different filters, both correct — G2b compared a name-filtered set against a wire-filtered set. It is a category error, not a measurement.**

| table | built by | kept when |
|---|---|---|
| `diagrams[k].nodes[uid].terms` | `sweep_netmap_main.py:64` | **name ≠ ""** (wire may be 0) |
| `diagrams[k].wires` | `tools/gscript.py:2570-2572`, `if uid: nets.setdefault(uid, …)` | **wire ≠ 0** (name may be "") |

On the five uids there are **17 wired** terminals, of which **16 are named**. G2 counted the first set and got 17. G2b counted the second and got 16. Both numbers are right; the gate asserted they must be equal, and nothing in either file ever promised that. No Case Structure, no selector, no subdiagram terminal and no downcast is needed to explain it.

Scale of the filter, measured from files:

- `main_vi_netmap.json` contains **zero** `["", <wire>]` entries in any `terms` array across all 170 diagrams. The single `["", ` match in the entire file is `"diagram_owners": ["", "FlatSequenceFrame", …]`.
- `main_vi_nodeterms.json`: 3,328 terminals, **665 unnamed**, of which **156 are unnamed *and wired*** — every one of them invisible in the netmap `terms` array.
- Only **76** diagrams are case *frames* (`"owner": "CaseStructure"`), so there are at most 76 selectors and in reality far fewer (one per structure, not per frame). 156 ≫ that.

## 3. The observation that would FALSIFY the claim — and it is already on disk

Falsifier: *any node that is not a Case Structure whose netmap `terms` array is short by a wired terminal.*

**Found, and it is the worst possible node for this claim — WhileLoop #637, the loop being restructured:**

`main_vi_nodeterms.json:6421` (`"uid": 637`) … `:6868-6872`

```json
{ "i": 37, "name": "", "is_source": true, "wire": 2187, … }
```

unnamed, **wired**, index 37, on a While Loop. `tools/bench/diag_s2_scaffold.py:239` already names this exact feed: *"its outer feed at d1_rewire_sources.json:2358-2373 is an UNNAMED tunnel, out_name ''"*. The netmap `terms` array is short for #637 too, and #637 is in the 109-row move set.

For fairness, what would falsify **my** explanation: a `terms` array anywhere containing an empty-name entry (none exists); or a node where the named-subset comparison `A == B` fails; or a shortfall ≠ the node's unnamed-terminal count. None of the three is observed.

⚠️ **The rewritten gate can no longer tell the two apart.** The log's G2b (`c53_row_class.log:26`) came from an *earlier* revision of the script (the log's traceback at line 79 does not match the current line 80). The current `c53_row_class.py:144-146` asserts the conclusion as its own pass condition — `missing == [(10407, 0, "", 10799)]`, message *"(the CaseStructure SELECTOR…)"*. Both hypotheses predict exactly that, because this node happens to have exactly one unnamed terminal. Re-running it will go green and will look like confirmation of a story that was never tested.

## 4. Cheapest discriminating test — files only, no LabVIEW, ~20 lines

Read **`tools/bench/main_vi_nodeterms.json`** and **`tools/bench/main_vi_netmap.json`**. For each of the 626 nodes present in both, compute

```
A = [(t["name"], t["wire"]) for t in nodeterms_node["terms"] if t["name"]]   # named subset, index order
B = netmap_node["terms"]
shortfall = len(nodeterms_node["terms"]) - len(B)
unnamed   = sum(1 for t in nodeterms_node["terms"] if not t["name"])
```

| | prediction |
|---|---|
| **claim (selector)** | `shortfall == 1` on Case Structures only, `0` on every other class |
| **alternative (name filter)** | `A == B` for all 626 nodes **and** `shortfall == unnamed` for **every** node of **every** class |

Cheaper still, because it has already been run: `rg "mismatches" tools/bench/sweep_nodeterms_main.log` — 626/626 nodes checked on the named subset, 0 content mismatches (`:189`).

---

## What this means for the build stage

- **17 is the right cut-row count** — for *wired* terminals on those five uids, agreed by three sources (the netmap `wires` table via G2/G3, `d1_rewire_sources.json`, and `main_vi_nodeterms.json`). Nothing gets silently left unwired. But the conclusion rests on G2/G3, **not** on the selector story.
- **Delete or rewrite G2b.** As a check on cut rows it is unsound in both directions: it must fail for any node set containing an unnamed wired terminal (156 exist), and it would pass *spuriously* for a terminal that is unnamed **and** unwired.
- **Stop using `terms` as a terminal census anywhere.** Use the `wires` table or `main_vi_nodeterms.json`. State counts as **wired terminals**, never "terminals".
- **Residual blind spot, worth one sentence in the plan:** a terminal that is unnamed *and* unwired is invisible in *every* cached file — dropped by `if t` in `terms`, by `if uid:` in `wires`, and trimmed when trailing by `sweep_nodeterms_main.py:65-66`. Harmless for a move (nothing to re-wire), but no file in `tools/bench/` can support a claim of a *complete* terminal census.
- **Process:** `c53_row_class.py:5-13` says "PRIOR ART CHECKED BEFORE WRITING" and lists four inputs — `main_vi_nodeterms.json` and `sweep_netmap_main.py` are not among them, and both held the answer. The prior-art check searched the inputs it had chosen, not the tool that produced them.

## Limits of what I checked

- **I did not verify that #10407 is a Case Structure, or that i=0 is its selector.** `main_vi_nodeterms.json` carries no class field, and I did not open a VI. The label is plausible (index 0, unnamed, sink, fed by a boolean `x .and. y?`) but unmeasured — and nothing in the count depends on it either way.
- **External documentation does not settle it.** The LabVIEW Wiki's [Terminal class](https://labviewwiki.org/wiki/Terminal_class) says only that `Name` "returns the name of the terminal… the non-translatable string identifier", and says nothing about tunnels or selector terminals; the [Tunnel class](https://labviewwiki.org/wiki/Tunnel_class) page is a stub, and the NI threads found ([Scripting – Case Structure](https://forums.ni.com/t5/LabVIEW/Scripting-Case-Structure/td-p/3594382), [Scripting – Terminal Information](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)) do not address empty names. So the *reason* a given terminal is unnamed remains unmeasured — which is precisely why the story should not have been built on it. The local code settles the mechanism without it.

**What would change my mind:** a node in `main_vi_nodeterms.json` whose netmap `terms` array is short by *more or fewer* entries than its unnamed-terminal count, or any `terms` entry anywhere with an empty name. Either would mean something other than `sweep_netmap_main.py:64` is also removing entries.

Sources: [Terminal class – LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class) · [Tunnel class – LabVIEW Wiki](https://labviewwiki.org/wiki/Tunnel_class) · [Scripting – Case Structure (NI)](https://forums.ni.com/t5/LabVIEW/Scripting-Case-Structure/td-p/3594382) · [Scripting – Terminal Information (NI)](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

## Sources

(extract from answer)

## What was done with it

**ACCEPTED IN FULL — cycle 53 judgement session, 2026-09-20.** Dispatched correctly by the material
session under the failed-prediction rule when its own G2b explanation did not match the machine; the
review refuted that explanation and replaced it with a measured mechanism.

**The mechanism, adopted:** `tools/bench/sweep_netmap_main.py:63-64` writes
`"terms": [[t, w] for _ti, t, w in terms if t]` — an **unnamed-terminal filter applied to every node
of every class**, which also **discards the real terminal index**. 156 unnamed-and-wired terminals
exist in the VI, and `WhileLoop #637` t37 is one of them
(`tools/bench/main_vi_nodeterms.json:6868-6872`), so this is not a Case-Structure quirk. Confirmed
independently: `main_vi_nodeterms.json` carries `#10407 i=0, name ""`, wire 10799, errs `[0,0,0,0]`,
so `d1_rewire_sources.json` did not invent index 0.

🔴 **BINDING CONSEQUENCE, and it reaches past this cycle: the netmap `terms` array is NOT a terminal
census, and its positions are NOT terminal indices.** Any wired-terminal count, any terminal index
and any "this terminal has no name so it does not exist" inference taken from `main_vi_netmap.json`
is unsound. Count wired terminals from a terminal-census op (`node_terms`), never from the netmap.
Carried into Pre-decided 38 and into STATUS `## NEXT`.

This is the third member of one family found in as many cycles — 37(b)'s index-order read returning
the wrong object, 37(d)/(e)'s wire count that cannot see a cut, and now a census that silently drops
rows. All three are *readers that answer confidently with the wrong thing*, and all three would have
passed a green build. The lesson is not "be careful": it is that a reader's contract must be measured
before it is used as a gate.

⚠️ **AMENDED the same day, after the review's own discriminating test was run: the mechanism is
ACCEPTED BUT INCOMPLETE.** The 626-node test ran as gates G2b(rewritten)/G2c/G6 of
`tools/bench/c53_row_class.py` (`c53_row_class.log:80-81`, 19 pass / 2 fail). G6 **PASS** — all 17 cut
rows agree with `main_vi_nodeterms.json` on (name, wire, is_source). But G2b(rewritten) — "netmap
`terms` == the NAMED subset, in order, for every node" — measured **574/626**, and G2c — "each node's
shortfall equals its unnamed-terminal count" — measured **574/626** as well. So the `if t` filter
explains ~92 % of the defect and not the rest.

What the residue looks like, in both logged violations: the dropped terminal is a **NAMED** one and it
is the **LAST** one (uid 30804 `nodeterms_named` ends `('error out', 32594)` while `netmap_terms` ends
`('error in', 4360)`; uid 4620 the same shape), and the shortfall is **15 against 14 unnamed** — off by
exactly one, both times. A second effect is dropping the final named terminal on ~52 nodes and it is
unexplained.

This is a fresh failed prediction and it was dispatched as one — `-Agent claude -Role hypothesis`,
slug `c53-netmap-terms-shortfall`. 🔴 **The conclusion above is UNCHANGED and in fact strengthened**:
if the netmap can silently drop a *named* terminal as well as an unnamed one, then "count wired
terminals from `node_terms`, never from `main_vi_netmap.json`" holds a fortiori. What is now open is
narrower and is recorded as such — whether anything else in the fleet that reads the netmap is
affected. Pre-decided 38(h) carries the binding half; this file carries the unexplained half.
