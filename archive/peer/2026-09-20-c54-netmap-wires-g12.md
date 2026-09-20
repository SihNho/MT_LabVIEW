# c54-netmap-wires-g12

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $2.8299  in 18 / out 39564 / cache-create 129775 / cache-read 992531  (576s, 14 turn(s))
- **date:** 2026-09-20 07:28:32
- **outcome:** ANSWERED (580s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK the explanation below. It was formed under pressure, immediately after a prediction failed, and it is
about to be written into this project's binding plan. Your job is to break it, not to agree with it.

## The failed prediction

`tools/bench/replay_netmap_truncation.py` is an OFFLINE replay (files only, no LabVIEW) that re-derives
`WhileLoop #637`'s border wires from the complete terminal census `tools/bench/main_vi_nodeterms.json` and
compares them with `tools/bench/main_vi_netmap.json`. Its prediction P5 was:

    P5  netmap Diagram 19 (= Diagram #686) is missing ALL of #637's i40..i58 wire ends
        (the 12 wires named on the record: 9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392,
         29081, 29106, 32583, 32344)

MEASURED, `tools/bench/replay_netmap_truncation.log`:

    FAIL  G12 P5 all 12 absent from the netmap wires table  absent=5 present=[9051, 9000, 29006, 29122, 28392, 29081, 29106]

i.e. **7 of the 12 ARE in the netmap `wires` table**, only 5 are absent.

## The claim you must attack

> The netmap `wires` table is built INSIDE the same truncated terminal loop (`tools/gscript.py:2570-2572`, the
> loop whose bounds are `:2549` `for t in range(max_terms)` with `max_terms = 40`, plus the `:2557-2560` break
> after three consecutive unnamed-and-unwired terminals), but it is **keyed by wire uid and filled from every
> node of the diagram**. So a wire whose only `#637` end sits at terminal index i40..i58 loses THAT end, yet it
> still appears in the table whenever a DIFFERENT node on Diagram #686 carries the same wire at a terminal index
> the scan did reach. Therefore the record's sentence — "Diagram 19 is missing all of `#637`'s i40..i58 wire
> ends" — is TRUE at the level of `#637`'s own ends and FALSE at the level of the wires table, and the
> project's operative rule (never take a fact about `#637`'s border from the netmap) is unchanged by the
> failure.

Attack all of it, including the last clause — the claim that the failure changes nothing operationally is the
part most likely to be self-serving.

## Already ruled out (do not spend the answer on these)

* The 40-terminal cap and the `empties >= 3` early stop are MEASURED, not inferred: gates G5/G6 reproduced all
  52 shortfalls across 626 nodes (cap@40 explains exactly `#637`; `empties >= 3` explains the other 51).
* `#637` has 59 terminals and the netmap keeps exactly 28 = 40 - 12 unnamed within i0..i39 (G8/G9/G10 PASS).
* All 12 named wires really do sit on i40..i58 (G11 PASS), so this is not a mis-identified terminal range.

## Two further facts you should weigh

1. The `.py` on disk NO LONGER MATCHES the `.log`. The current bytes contain a "REFINEMENT" print block and a
   follow-up gate `G12b P5 restated: #637's OWN end is missing for all 12`, and NEITHER string occurs anywhere
   in `tools/bench/replay_netmap_truncation.log`. So the refinement above was written AFTER the run and has
   never itself been executed. Treat "G12b would pass" as an untested assertion, and say what that does to the
   claim's standing.
2. The same run's G16 also failed — `every #637 wire the complete census reports appears in the doc
   missing=28` — against `docs/frame-loop-wire-graph.md`. State whether G12 and G16 are one fault or two.

## What I need back

1. The strongest reason the claim above is WRONG.
2. An alternative explanation for `present=[9051, 9000, 29006, 29122, 28392, 29081, 29106]` that does not use
   "another node on the same diagram carried it" — including any mechanism by which a wire could enter the
   `wires` table without any scanned terminal carrying it at all.
3. What observation would FALSIFY the claim.
4. The CHEAPEST discriminating test, runnable offline against
   `tools/bench/main_vi_netmap.json` + `tools/bench/main_vi_nodeterms.json` only (no LabVIEW, no COM).

Files you may read: `tools/bench/replay_netmap_truncation.py`, `tools/bench/replay_netmap_truncation.log`,
`tools/gscript.py` (the `net_map` region around `:2540-2580`), `tools/bench/main_vi_netmap.json`,
`tools/bench/main_vi_nodeterms.json`, `docs/frame-loop-wire-graph.md`.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

No — the mechanism in that claim is almost certainly right, and its last clause is wrong for a reason the run itself measured and the claim walks past.

---

## 1. The strongest reason the claim is wrong

**The claim mis-states what the netmap knows about `#637`, in the direction that flatters it: the `wires` table holds *forty* of `#637`'s ends, not twenty-eight — and twelve of those forty appear in no node's `terms` array at all.**

The two tables in `main_vi_netmap.json` are two *differently filtered* views of one walk:

- `nodes[uid].terms` — `sweep_netmap_main.py:63-64`, `[[t, w] for _ti, t, w in terms if t]` → named terminals only, **terminal index discarded**.
- `wires` — `gscript.py:2570-2572`, `for t, name, uid in terms: if uid: nets.setdefault(uid, []).append((n, t, name))` → **every wired terminal the walk scanned, named or not**, with the index kept.

`#637`'s twelve unnamed terminals inside `i0..i39` are all wired (`replay_netmap_truncation.log:109-132`: i14→2362, i17→5104, i22→3668, i23→21, i26→5174, i27→5336, i30→5812, i31→2731, i32→2641, i33→5265, i34→3853, i37→2187). Every one of them is in the `wires` table and in none of the `terms` arrays. So:

- The settled arithmetic "netmap keeps exactly 28 = 40 − 12" (G8/G9/G10) is true **only of the `nodes` view**. The `wires` view kept 40.
- Wire 2731 and wire 5812 each have **two** `#637` ends in that table (i3+i31, i29+i30). `#637`'s fan-out as the `wires` table reports it is not what the `nodes` table implies.
- Census-wide the same asymmetry has up to **156 instances** (`log:74`, "terminals the `if t` filter drops that ARE WIRED (whole census): 156") — the exact count needs the scan mask, but the direction is fixed.

That is why "the operative rule is unchanged" fails. The rule as written — *never take a fact about `#637`'s border from the netmap* — names the wrong object. What the failure actually established is a property of the **file**:

> The netmap's per-diagram `wires` table records, for each wire, only the ends at terminal indices `0..39` of the nodes the walk reached before its own stop conditions. It is a **lower bound on every wire's end set, on every diagram**, and it is **not self-diagnosing**: truncation silently converts a two-ended net into a one-ended net, which looks exactly like a genuinely one-ended net. The `nodes` view at least gets shorter; the `wires` view just gets quieter.

Diagram 19 alone has two truncated nodes — `#637` (cap@40) and `#6384` (`empties3@i4`, `log:25`) — so this is not a `#637` anomaly even on `#637`'s own diagram. And the project has already been burned by precisely the negative-existence claim this licenses: Pre-decided 38(b)'s struck "sources on #686 = 0", and G15 (`log:234`) having to re-measure "no OTHER node on #686 carries 4185/7506" against the complete census. Leaving the rule scoped to `#637` leaves every other consumer of `wires` unwarned about the same defect.

Two smaller errors in the same paragraph:

- "filled from **every** node of the diagram" — false. Filled from the scanned prefix of the nodes the walk *reached*: `max_nodes=200` (`sweep_netmap_main.py:55`), `MISS_LIMIT=4` (`gscript.py:2525`), the junk-Invoke signature break (`:2564-2565`), `empties>=3` (`:2557-2560`), `max_terms=40` (`:2549`). "Every node" is the word doing the work that makes the table sound trustworthy.
- The record's sentence ("Diagram 19 is missing all of `#637`'s i40..i58 **wire ends**") was never the false reading. **G12's implementation** was — `absent = [w for w in EXPECTED_MISSING if str(w) not in d19w]` (`replay_netmap_truncation.py:287`) tests wire-*presence*, not end-presence. So the underlying model error is precise and worth naming as such: *presence in `wires` was treated as equivalent to appearing in some node's `terms`*. Those two tables cannot be cross-validated by presence, by construction.

## 2. What survives — and the corroboration the claim did not cite

The mechanism is right, and the project's own doc already proved it six days before the run. `docs/frame-loop-wire-graph.md` (MEASURED, `OpShiftRegs_v1`/`OpTunnels_v0`, nodeterms-sourced) gives a diagram-19 source node for the present wires and **none** for the absent ones:

| wire | netmap `wires` | other diagram-19 end, per the doc |
|---|---|---|
| 9051 | present | `#8953 Initialize Array · initialized array` (`:440`) |
| 29122 | present | `#28124 Initialize Array · initialized array` (`:444`) |
| 28392 | present | tunnel 28343 ← `subVI Max Trans Pos.vi · Magnet position output` (`:264`) |
| 29081, 29106 | present | tunnels 29077/29102 ← `#28670` (`:265-266`) |
| 9649 | **absent** | tunnel 9641 — "(no source node on 19)" (`:262`) |
| 32583 | **absent** | tunnel 32572 — "(no source node on 19)" (`:267`) |
| 11253, 16421, 32344 | **absent** | left-register initial value "— (wire X)", no source node (`:442-443`, `:445`) |

Twelve for twelve, the present/absent split tracks "does another diagram-19 node carry this wire". So the story is correct — and that is the sharpest process criticism available, not a concession: **the evidence was one grep from a document in `docs/`, and two lines of unexecuted print from the file already open.** A plausible reconstruction was written where a reading was on disk.

## 3. What the untested G12b does to the claim's standing

Worse than the brief states. The on-disk `replay_netmap_truncation.json` contains `part4_doc` but **none** of `review_named_wires_with_no_637_end_in_netmap`, `differences_vs_frame_loop_state_json`, `outer_map_rederived`, `wires_not_printed_in_doc_text` — so the artefact is the *old* run's and the current file has never executed. Three consequences:

1. **G12b cannot fail.** No end in any `wires` table can have `t ≥ 40` (`gscript.py:2549` bounds `t` at 39), and none of the twelve appears among `#637`'s `i0..i39` wires. G12b is therefore *entailed* by facts already accepted (G8–G11), not measured by anything. A gate that cannot fail is not a test, and "the sound restatement" replaces a falsified empirical prediction with a tautology while keeping the word "MEASURED" (`replay_netmap_truncation.py:296-298`).
2. **Its key is an unvalidated cross-census index join.** `any(e[0] == n637["n"])` (`:303`) takes `n` from *nodeterms* (`sweep_nodeterms_main.py:44-50`, `enumerate(diagram_tree_main.json uids)`) and uses it as a key into *netmap* `wires` ends, whose `n` is `net_map`'s own walk index. The netmap file **does not store that index→uid map at all** (`sweep_netmap_main.py:62-63` re-keys by uid and discards `_k`), so nothing in the file corroborates the join. Meanwhile the project's own record says this index space can move: `sweep_nodeterms_main.py:60-62` carries a mismatch class "Nodes[] order differs from the Step-0 tree", and `net_map` **mutates `Nodes[]` while walking it** — ~75 junk Invoke nodes per walk, purged afterwards (`gscript.py:2513-2523`, `:2582-2600`). A uid-keyed check was available and was not used.
3. **G16 was rewritten after it failed.** The log's gate — "every #637 wire the complete census reports appears in the doc", `missing=28` (`log:244`) — no longer exists. On disk it is "the doc's #637 outer rows == the complete-census re-derivation" (`replay_netmap_truncation.py:453-455`), with a new PART 4 pulling in two new inputs. Changing a failed gate's pass criterion after seeing the failure is the move `retrospective.py`'s `rule-evaded` slug exists for, and it destroys comparability: if the next cycle runs the current file and reports "15 pass / 1 fail", no record will remain that a prediction about the doc ever failed. And the replacement gate is *weaker than useless* — `frame_loop_state.json` backs the section the doc itself marks **superseded** and **HEURISTIC** (`docs/frame-loop-wire-graph.md:349`, `:428`), while the authoritative MEASURED sections (`:403-447`), which is where `#637`'s border facts now live, go unchecked.

## 4. Alternative explanations for `present=[9051, 9000, 29006, 29122, 28392, 29081, 29106]` that do not use "another node carried it"

Including the mechanism the brief asked for — a wire entering `wires` with no scanned terminal behind it:

**(a) Cross-census wire-uid identity failure.** UIDs are unique within a VI *at a time*, but NI's own documentation says: "If you delete an object, LabVIEW might assign the UID for that deleted object to a different object in the future," and recommends checking Class Name or Label **in addition to** the UID ([LabVIEW Wiki, GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property); [NI GObject properties](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject-p.html)). The netmap sweep created and deleted tens of Invokes per diagram across 170 diagrams and then ran Remove Bad Wires (`gscript.py:2582-2596`) — i.e. it freed UIDs while measuring. The nodeterms census ran later. So a uid in netmap `wires` need not denote the same wire in nodeterms. The 574/626 node agreement makes wholesale drift implausible for wires reachable in *both* views — but it says nothing about a uid that appears **only** in the `wires` table, which is exactly the set under discussion, and the replay never offers that agreement as the join's warrant.

**(b) Stale-indicator misattribution — a wire in the table with no terminal carrying it, needing no other node.** `gscript.py:2551-2556` re-runs the op only `if t`, then reads `Name`/`UID 2` unconditionally. Any run that fails *without raising* (swallowed timeout, op error-out set, COM returning prior values) leaves the previous terminal's — or at `t == 0`, the previous **node's** last terminal's — name and wire in those indicators, and `:2570-2572` files that uid under the current `(n, t)`. Signature: an end whose `(name, wire)` duplicates the immediately preceding end, disagreeing with nodeterms at that `(n, t)`.

**(c) An unrecognised junk Invoke walked as a real node.** The only guard is an exact six-name signature test at `t == 5` (`:2564`). A junk node whose first six terminal names differ is recorded as real, and its wired terminals enter `nets` — wires that exist in no census (Remove Bad Wires was needed afterwards, so wires did exist). High-numbered uids are what fresh objects get.

**(d) The "different node" may be invisible to the check that would look for it.** `diagram_tree_main.json` lists 635 nodes; nodeterms holds 626 (`log:5`), because `sweep_nodeterms_main.py:56-59` **breaks a whole diagram** at the first out-of-range node. The replay reports "nodes in nodeterms but NOT in the netmap: 0" (`log:13`) and **never computes the reverse**. So a carrier could sit on netmap diagram 19 and be absent from `WIDX` entirely — in which case the natural check comes back empty and gets misread as refuting a mechanism that is in fact true.

## 5. What would falsify the claim

- Any of the seven present wires has an end in `NM["diagrams"]["19"]["wires"]` that resolves to node `#637` → G12b is false and the restatement collapses.
- For some present wire, **every** end resolves to a node/terminal that nodeterms says carries a *different* wire uid, or to an `n` absent from nodeterms diagram 19 → presence is a measurement artefact ((a)–(d)), not another carrier.
- The netmap's own key order for diagram 19 puts something other than `637` at position 4 → the index join under G12b is wrong, whatever else is true.
- For the *operational* clause specifically: any active document or decision that took a count, a fan-out, or an "only carrier" from netmap `wires` for a wire on any diagram holding one of the 52 truncated nodes. 38(b) is one such instance; G15's forced re-measurement is a second. Two instances falsify "unchanged".

## 6. G12 and G16: two faults, plus a third

**Two, with one common cause.** G12 is a wrong model of the netmap *file* (wire-keyed net table vs node-keyed terms array, differently filtered). G16 is a wrong claim about a *document* the same run shows is nodeterms-sourced (`log:241-243`) and whose generators only ever printed selected rows — border tunnels, state carriers, half-edge accounting — so "all 45 of `#637`'s wires appear in the text" was never the doc's contract. The two gaps are demonstrably independent: of the seven netmap-present wires the doc contains only `{9051, 29122}`; of the five netmap-absent it contains `{11253, 16421, 32344}` (`log:240`). Different mechanisms, different remedies. What they share is one process fault: **both predictions were asserted about artefacts on disk that had not been read.** That is the fault worth counting. The third is §3.3 — the post-hoc gate rewrite, which is the one that will cost the next cycle.

## 7. Cheapest discriminating test — offline, two files already in memory

One pass, no LabVIEW, no COM, no new op:

```
D  = "19"
nmN = NM["diagrams"][D]["nodes"]          # uid -> {...}, insertion order == walk order
ntN = {nd["n"]: nd for nd in NT["diagrams"][D]["nodes"]}

# (0) FREE, one line: the join's key, checked inside the netmap alone
list(nmN.keys())[4] == "637"              # if not, G12b's key is wrong, full stop

# (1) the reverse-direction node check the replay never did
set(nmN) - {str(nd["uid"]) for nd in NT["diagrams"][D]["nodes"]}

# (2) resolve EVERY end of the 12 tail wires
for w in EXPECTED_MISSING:
    for n, t, name in (NM["diagrams"][D]["wires"].get(str(w)) or []):
        nd = ntN.get(n)                                   # nodeterms node at walk index n
        tm = next((x for x in nd["terms"] if x["i"] == t), None) if nd else None
        bucket = ("self_end"            if nd and nd["uid"] == 637
             else "other_node_confirmed" if tm and tm["wire"] == w and tm["name"] == name
             else "unresolved_or_disagree")
```

Three counters decide it: `other_node_confirmed` → the mechanism is real and measured (predicted: 9051→#8953, 29122→#28124, 28392→Max Trans Pos.vi, 29081/29106→#28670); `self_end` → G12b false; `unresolved_or_disagree` → alternatives (a)–(d).

Then run the identical resolution over **every end of every wire on all 170 diagrams** — same three lines, same loaded data — and report the global agreement rate. That single number validates or destroys the cross-census `n` join that G12b rests on, which no measurement currently supports. Add one more line while the data is open: count ends whose `(n, t)` is an unnamed terminal in nodeterms — that is the exact size of the `wires`/`terms` asymmetry (the "up to 156"), and it is the number the corrected operative rule should be written around.

**Net verdict.** The mechanism holds; I would change my mind on it only if test (2) returns `self_end` or `unresolved_or_disagree` for one of the seven. The claim's final clause does not hold: the rule needs rewriting from "don't trust the netmap about `#637`'s border" to "netmap `wires` is a lower bound on any wire's end set and `nodes[*].terms` is a *different* lower bound — never join them by presence, never count from either" — and the un-run G12b/G16 rewrite must be executed, or reverted, before any of this is written into a binding plan.

**Sources:** [LabVIEW Wiki — GObject class/UID property](https://labviewwiki.org/wiki/GObject_class/UID_property) · [NI — GObject Properties](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject-p.html)

## Sources

(extract from answer)

## What was done with it

**Dispatched by the cycle-54 MATERIAL session** because `tools/hooks/guard_peer.py` blocked every build on
`tools/bench/replay_netmap_truncation.log:162`
(`FAIL  G12 P5 all 12 absent from the netmap wires table  absent=5 present=[9051, 9000, 29006, 29122, 28392,
29081, 29106]`). Outcome **ANSWERED**, `-Agent claude -Role hypothesis` (opus / effort max / web),
**$2.8299, 580 s**, log `tools/bench/peer_c54_g12.log`. The gate lifted and
`tools/bench/diag_s3_focus_trial.py` (Pre-decided 38(d)) then launched.

**RECORDED, NOT ACCEPTED OR REJECTED.** The netmap replay is not this session's work — it belongs to the
cycle-54 judgement session's "SECOND ACT" (STATUS NEXT) — and CLAUDE.md §3 reserves "what to accept from a
review" to judgement. The material facts a judgement session needs, none of them re-framed:

1. The review **does not defend** the claim it was asked to attack in the direction expected: it says the
   `wires` table holds **40** of `#637`'s ends, not 28, and that **12 of those 40 appear in no node's `terms`
   array at all** — i.e. the claim under-states what the netmap knows, "in the direction that flatters it".
2. It names **four** alternative mechanisms for the 7 present wires that do not use "another node on the same
   diagram carried it": cross-census **uid reuse** (NI's own documentation: a deleted object's UID may be
   reassigned, and the sweep created/deleted Invokes and ran Remove Bad Wires while measuring); **stale
   indicator misattribution** at `gscript.py:2551-2556` (the op is re-run only `if t`, then `Name`/`UID 2` are
   read unconditionally); an **unrecognised junk Invoke** walked as a real node (the only guard is a six-name
   signature test at `t == 5`, `:2564`); and a **carrier invisible to the check** — `sweep_nodeterms_main.py:56-59`
   breaks a whole diagram at the first out-of-range node (635 nodes in `diagram_tree_main.json` vs 626 in
   nodeterms), and the replay computed the node-set difference in one direction only.
3. On G12 vs G16 it says **two faults, one common cause** — "both predictions were asserted about artefacts on
   disk that had not been read" — and names a **third**: the post-hoc gate rewrite.
4. It confirms independently the fact this session measured while framing the question: the current
   `replay_netmap_truncation.py` bytes contain a REFINEMENT block and a gate `G12b` that occur **nowhere** in
   the log, so that restatement **has never been executed**. Its instruction is that the rewrite be **run or
   reverted before anything from it is written into a binding plan**.
5. Its §7 gives a discriminating test that is **offline, files only** (`main_vi_netmap.json` +
   `main_vi_nodeterms.json`, no LabVIEW, no COM): check the join key inside the netmap alone, do the reverse
   node-set check the replay never did, and resolve every end of the 12 tail wires.

**Not run here.** That test is the judgement session's to schedule: this session's brief is Pre-decided 38(d)
and explicitly forbids taking result-dependent actions outside it.
