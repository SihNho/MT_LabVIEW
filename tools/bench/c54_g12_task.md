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
