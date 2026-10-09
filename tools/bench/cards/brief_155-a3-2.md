---
card: 155-a3-2
status: current
date: 2026-10-09
---
# Brief 155-a3-2 - CONTINUATION of 155-a3-1: adopt the PASSED P5-1b scratch file, final Error List, graph read, load_by_vi (NO new scratch run)

Read `tools/bench/diag_c155_a3_1_facts.md` and `tools/bench/cards/brief_155-a3-1.md` items 3-8 first. Card 155-a3-1 ran the ONE scratch: PASS 20/0, saved `claudeDev\D1_ring_p5s01b_20261009_123319.vi` md5 7f2582ae54dc5bc42c3df0bdf3c72d2e (ExecState 0 by design). It returned only because `adopt_scratch` does not rename.

Decision (assignment session, an assumption - flag it in the report): make `claudeDev\D1_ring_p5s01_<stamp>.vi` by a plain BYTE COPY of that file (no tool edit; verify the md5 is equal), then call `stagexec.adopt_scratch` by import with the copy as the artefact (input 2482fe7b, the scratch log `diag_c155_p5s01b_scratch.log`, the required gate list the scratch recipe declares; copy `diag_c154_a3_3_adopt.py` -> `diag_c155_a3_2_adopt.py`, names/ids/paths only). Keep the `...p5s01b_...` file untouched. Quote both paths and md5s and the adopt/1 record. A refusal => RETURN with it (file:line).

Then, on the ADOPTED copy and as in brief_155-a3-1 items 4-8: final Error List (expected file `errorlist_expected_D1_ring_p5s01_<stamp>.json`; total + per class vs P5-1a 47 and vs the hand prediction 45; both elrule totals 47; non-gating), fresh-instance load + graph json `graph_ring_p5s01_<stamp>.json` with the quoted rows (Case #30726 frames / selector / tunnels, the two new SelectorTunnels #31257 / #31293, the sr_q shift register on #10170 and its terminals, `#30914` frame wires, Enqueue `queue` source, remaining open terminals), ONLY the `load_by_vi` entry in memory_model.json (before 386a4cf4; diff quoted), invariants md5 before = after, handles, LabVIEW closed and verified gone.

NO new scratch, NO second launch of any recipe. No recipe / plan / tool / hook edit. A gate refusing your OWN command text is a false positive: `py tools/gate_fp.py log`.

## Report `tools/bench/diag_c155_a3_2_facts.md` (<= 45 lines)
Adopt record; EL total + per-class; graph path + md5 + quoted rows; `load_by_vi` diff; invariants; handles; LabVIEW gone. `OPEN:` line. Facts only.
