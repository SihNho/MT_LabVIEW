ATTACK the explanation below. It is a diagnosis formed under pressure after a FAILED PREDICTION,
and I need the strongest reason it is wrong, an alternative explanation, what would falsify it, and
the cheapest discriminating test. Files only — no LabVIEW, no COM, nothing to run on hardware.

## The artefacts

* Diagnostic: `tools/bench/replay_netmap_truncation.py` (pure file read, no COM).
* Its log: `tools/bench/replay_netmap_truncation.log` — the run that FAILED gate G12.
* Its readings: `tools/bench/replay_netmap_truncation.json`.
* Inputs: `tools/bench/main_vi_nodeterms.json` (complete census: 626 nodes, 3328 terminals, real
  terminal indices, `is_source`, per-field error columns) and `tools/bench/main_vi_netmap.json`
  (the truncated one, produced by `tools/gscript.py` `net_map` via `tools/bench/sweep_netmap_main.py`).
* The review this replays: `archive/peer/2026-09-20-c53-netmap-terms-truncation.md` §4 and §6.

## The prediction that FAILED

P5, taken verbatim from that review's §4: *"Diagram 19 is missing all of #637's i40–i58 wire ends —
9051, 9000, 9649, 11253, 16421, 29006, 29122, 28392, 29081, 29106, 32583, 32344."*

Gate G12 tested it as "all 12 wire uids are absent from `main_vi_netmap.json`'s `diagrams["19"]["wires"]`
table". MEASURED: only **5** of the 12 are absent (9649, 11253, 16421, 32583, 32344). The other **7**
(9051, 9000, 29006, 29122, 28392, 29081, 29106) ARE present as keys in that table.

Everything else in the replay passed: 626 nodes compared, 574 agree, 52 disagree, all 52 reproduced
with zero unexplained, `cap@40` holding exactly `WhileLoop #637` and `empties>=3` the other 51; #637
has 59 terminals and the netmap keeps 28, with 40 − 12 unnamed = 28 exactly.

## THE EXPLANATION I FORMED — attack this

"The review's sentence is right about the mechanism and loose about the object. `nets` in
`tools/gscript.py:2570-2572` is keyed by WIRE UID and accumulated across EVERY node of the diagram,
not per node. So a wire whose #637 end was dropped by the `max_terms=40` cap can still appear as a key
in the diagram's `wires` table, contributed by a DIFFERENT node on Diagram #686 that carries the same
wire and sits inside its own cap. The sound restatement is therefore not 'the wire is missing' but
'#637's OWN end is missing', and that is what I now measure as G12b: for all 12 of those wires, no end
in the netmap's table names node walk-index 4 (= `#637`). So P5 is false as literally written, true as
restated, and the practical consequence the review drew — that any fact about #637's border taken from
the netmap is suspect — is unaffected."

## Already ruled out (do not spend the review on these)

1. Not a stale file: `main_vi_netmap.json` has `complete: true` and both censuses name the same source VI.
2. Not the `if t` filter of `sweep_netmap_main.py:63-64`: the replay applies that filter to BOTH sides,
   and the 52 shortfalls all reproduce exactly with it applied.
3. Not a node the walk never reached: 626 of 626 nodeterms nodes are present in the netmap (0 missing),
   so `MISS_LIMIT` and the junk-Invoke break did not fire on this VI.

## What I need

1. The single strongest reason my restatement is wrong — including whether "no end names walk-index 4"
   is even a sound test of "#637's end is missing" (the netmap's `wires` entries are `[n, t, name]`
   where `n` is the WALK index, and I read `#637`'s `n` from `main_vi_nodeterms.json`; is that the same
   index space?).
2. An alternative explanation for the 7 present wires that is NOT "another node on the same diagram
   carries them" — e.g. a duplicate terminal of #637 inside i0..i39 carrying the same wire uid (i30
   and i29 both carry 5812; i31 and i3 both carry 2731; i21 and i38 both carry 1827 — so this shape
   demonstrably exists on this node).
3. What would falsify my account.
4. The cheapest discriminating test, files only.
5. Whether a NEGATIVE claim of the form "no node terminal on Diagram #686 other than #637 carries wire
   4185 / 7506" is now safe to make. I re-derived it from the COMPLETE census (each wire has exactly
   one carrier, `#637` i11 and i10 respectively) and used it to re-open the question Pre-decided 38(b)
   struck as unsound. Is the complete census's own completeness itself measured, or am I repeating the
   mistake one layer up?
