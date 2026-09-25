ATTACK this claim (failed prediction, log tools/bench/diag_c89_donor_census.log, script tools/bench/diag_c89_donor_census.py, card tools/bench/cards/task_89-2.json, result tools/bench/cards/result_89-2.json).

CLAIM (card 89-2's diagnosis, formed after the census): "A per-bead tick-count stamp helper VI (t0_stamp.vi: ring buffer of tick counts, written to a file once at the end, called at 5 points inside the frame loop of D1_s1_copy.vi) cannot be assembled from the existing scripting verbs in tools/gscript.py within a 75-minute card, because its body needs >= 10 primitives (Replace Array Subset, Quotient & Remainder, Write to Binary File, Initialize Array, Equal To 0?, Increment, Build Path, ...) that only `copy_by_index` (gscript.py:1549-1628, one LabVIEW restart per copied primitive) can create, plus a reentrancy setter (VI property 288) that no verb writes; so the in-VI instrumentation route is closed for this cycle."

PREDICTED (card 89-2): the donor census finds every needed primitive in a donor VI and the helper is buildable in one staged run.
OBSERVED: diag_c89_donor_census.log run 2 ended FAIL with first failing line "no donor for Open/Create/Replace File, Close File, Select" (the census encoded its verdict as a gate); run 1 was a TypeError on result_line (patched).

Already ruled out:
- `New VI Object` style-ring primitives: only the ring's own styles are creatable (skill rule 0.2); the primitives above are outside it (docs/toolkit-capabilities.md).
- vi.lib named-terminal VIs as substitutes: `High Resolution Relative Seconds.vi` is droppable (drop_subvi), but buffering/writing still needs array and file primitives.
- Editing D1_s1_copy.vi itself: forbidden by the card (headless read only).

Questions for the adversary: (1) the strongest reason the claim is wrong — e.g. a way to get the helper WITHOUT copying primitives (a vi.lib/express VI that already implements "append timestamps to a file" or "tick count to array", a `.vim`, `Write Delimited Spreadsheet.vi`, `Format Into File`, a Queue/DVR-based buffer built from creatable objects, a VI snippet/clipboard import, the `Merge VI` mechanism, or LabVIEW's own Profile Performance and Memory tool which needs no edit at all); (2) an alternative explanation of the FAIL (the census looked in the wrong donor set; the gate was a census verdict and not a build failure); (3) what would falsify the claim; (4) the cheapest discriminating test.
