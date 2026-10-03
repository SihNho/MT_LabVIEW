# Brief 142-P1 — offline facts for the P4 subVI re-plan

User 2026-10-03 (`docs/d1/ring-p4b.md:94-103`): P4 from here on is built WITH SUBVIs — the bed's loop 1.2 keeps the local
reads/writes in seqlock order (n1 = Num(i) read → track → n2 = Num(i) read; Latest/`last`; StopAll); pure computation goes
into small subVIs in their own files. The slot-write repair (Insert Into Array → Replace Array Subset) and the saved
session-1 file `D1_ring_p4s01_20261002_232547.vi` are kept as they are.

## (1) Decomposition table — tools/bench/prep_c142_p1_subvi_table.md + .json
Every action of `tools/bench/plan_ring_p4_v17.json` whose id does not start `p4_rp` (the repair), grouped by connected
computation (follow the plan's wires). Per group:
- action ids, `prim`/class of each created node;
- external inputs: source (action id + terminal, or bed uid + terminal) and LabVIEW type where the plan or graph states it;
- external outputs: sink(s) and type;
- contains any of: Local (read/write), shift register (`add_shift_reg`), Flat Sequence frame/border/FS exit, a border of
  While `#10170` / its body `#23166` or of a plan-made While (W1), refnum/IMAQ, Wait (ms), stop/conditional terminal.
  PURE = none of these.
Also list the bed-only glue actions (locals, registers, FS, waits, stops, tunnels, RLE, delete_*). Counts: actions in pure
groups vs bed actions. The group already being built as a subVI in card 142-1 is `p4_gt_last` / `p4_f_min` /
`p4_sel_mask` / `p4_k_max` / `p4_k_max_found` / `p4_amm` / `p4_lt_found` — confirm or correct its boundary (any wire into
or out of it the brief 142-1 did not name).
A proposal is optional and must be labelled "proposal"; judgement decides the subVI list.

## (2) Remaining repair as one bed session — tools/bench/plan_ring_p4_rasrest.json
The v17 `p4_rp*` actions NOT applied by session 1 (`plan_ring_p4_s01.json` = v17 ops 1..24), plus only the v17 actions
they depend on. `py tools/stage_prerun.py --rebase` onto `tools/bench/graph_ring_p4s01_20261002_234419.json` (the
session-1 file's real graph; first-read stand-in rule PD326(b)), then `--dry` and `--prerun`; report X10 at start
596.5 MB against the limit in `memory_model.json`, the predicted Error List count (one item per created node with an
unwired input, PD322(e)), and the recipe pair `tools/recipes/stage_d1_ring_p4_rasrest.py` / `_scratch.py` made from the
s02 recipes. Report the action count and any action that does not fit.

Facts only; return at the first unexpected result.
