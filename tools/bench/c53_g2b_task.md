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
