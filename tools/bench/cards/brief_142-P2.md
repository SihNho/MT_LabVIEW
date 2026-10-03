# Brief 142-P2 — offline: P4 plan v18 with the two subVIs (PD330, `docs/d1/ring-p4b.md:109`)

v18 = `tools/bench/plan_ring_p4_v17.json` with:
- S1: actions `p4_gt_last`, `p4_f_min`, `p4_sel_mask`, `p4_k_max`, `p4_k_max_found`, `p4_amm`, `p4_lt_found` and every wire/
  For-tunnel action INSIDE that group (`prep_c142_p1_subvi_table.md:33-42`, minus `p4_or_w1`) replaced by ONE `create` of
  class `SubVI` (stagexec route `subvi`, `tools/stagexec.py:255,3047-3054`; `subvi_path` =
  `claudeDev\RingPickSlot_v0.vi`, md5 6fcf153f7b8fecda727f5dcf944faab9) on `new:W1.body`; its boundary wires re-pointed to
  the subVI's terminals by NAME as MEASURED (`tools/bench/build_ringpickslot_v2.log:20,55,129`: `Num`, `last`, `min Num`,
  `min slot`, `found`). `found` → `p4_or_w1`.x stays.
- S2: actions `p4_eq_seq`, `p4_gt_n1`, `p4_and`, `p4_dec`, `p4_sel_last`, `p4_sel_disc`, `p4_inc_disc` and their inner wires
  replaced by ONE SubVI create of `claudeDev\RingSeqCheck_v0.vi` on diagram 23166, terminals `n1`, `n2`, `last`, `Latest`,
  `discards` / `next last`, `next discards`, `valid` — PROVISIONAL (card 142-4 builds it now): mark these names
  `provisional: true`; the seven rollback Selects' `s` and every other consumer of `p4_and`'s output re-pointed to `valid`.
- Everything else (repair `p4_rp*`, rollback Selects, Index Arrays, locals, registers, FS, W1, stop) unchanged.

Then: replay END in stagesim + `compile_plan` on v18 (prerequisite: does stagesim model a `SubVI` create from a file
path, with its terminals? Report YES with the line, or the exact gap — do NOT edit stagesim/stagexec/stage_prerun);
report action count v17 → v18, end cdiff v17 vs v18 (only the replaced nodes should differ), and the X10 session table
of v18's non-repair part at start 596.5. Write `tools/bench/plan_ring_p4_v18.json` + `tools/bench/prep_c142_p2_facts.md`.
Facts only; return at the first unexpected result.
