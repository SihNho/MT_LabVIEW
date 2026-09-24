# Card 78-3 plan: M8(b) replay SWAP stage + two replay runs (m8 plan PD13(d), PD14(c), PD15, PD17(b'), PD22(d); docs/m8-real-run-plan.md:98-315)

Recipe: `tools/recipes/stage_replay_swap.py` (84 lines, stagekit Stage, dry PASS, pre-run 7/0). Rows/uids/paths from
`tools/bench/plans/plan_replay_swap_78.json`. Offline graph: `tools/bench/graph_s3_loop15_20260924.json` (the only graph
in the dry-run shape, so S3 is the Stage input; S1 is copied beside it and treated identically).

What the stage does (no VI is run):
1. Dated byte copies `claudeDev\replay\D1_s3_replay_<ts>.vi` (from `D1_s3_loop15.vi` 1a11d92a) and
   `claudeDev\replay\D1_s1_replay_<ts>.vi` (from `D1_s1_copy.vi` 3e3d23ce). Their subVIs are absolute G: paths
   (`docs/wiki/subvi/D1_s1_copy.json:89813`), the replay VIs sit in the same folder.
2. Per copy: census BEFORE (#6810 -> `get buff image-lost frames.vi`, #22692 -> `IMAQdx Get Image.vi`), ExecState 1,
   whole-VI wire-edge set (`wiki_build.read_live`), then `gscript.replace_object` (PD15, accepted on
   `tools/bench/swap_verb_75.json` 21/0) #6810 -> `replay\replay_get_buff_image.vi` (842ecad9) and #22692 ->
   `replay\replay_get_image_cal.vi` (afce0d04) - both accepted as built in PD22(b).
3. Gates per copy: callee diff == exactly the two swaps (new uid read from the verb, remapped new->old per PD15); wire-edge
   diff 0 after the remap; ExecState 1; scripted save. Cold (fresh LabVIEW): ExecState 1, census == warm, md5 stable.
   Pins: S1, S3, the three replay VIs, the original - unchanged.

Then (not part of the recipe): each saved copy runs in its OWN LabVIEW launch through `tools/bench/drive_m8.py --leg rs1|rs3
--src <copy>` (new leg: the run copy is made beside the replay VIs; v5 driver unchanged; same picks, RUN_S 35 s). Motors
under the 2026-09-24 grant with the runner's session checks. Then `tools/bench/m8b_replay_compare.py` joins the two
tra files on iteration index (rows = LE I32 dims + LE f64, time,trans,rot + 3x(x,y,z)) and gates X/Y/Z bit-identity over
the common prefix (>= 1000 rows), reporting row counts, identical prefix, first differing row; the cal files are compared
byte-wise as a FACT. Result `tools/bench/m8b_replay_78.json` + an INDEX row.

Known risks: #22692 swap is a vi.lib subVI -> an unowned claudeDev VI (PD15 measured only the #6810 kind); per-frame IMAQ
ReadFile from G: may slow the frame loop (fewer rows; the join is on iteration so it only lowers the common count).
