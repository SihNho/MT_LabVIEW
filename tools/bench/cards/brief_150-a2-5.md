---
card: 150-a2-5
status: current
date: 2026-10-08
---
# Brief 150-a2-5 - retry of 150-a2-3: s07 prepared on the REAL s06 graph (rebase, X10, pred, recipes, licence, dry + prerun); offline, NOT launched

Same task as `tools/bench/cards/brief_150-a2-3.md` (md5 deb507f0) - read it and follow it unchanged, except:
- `tools/stage_prerun.py` is now **c739eb86** (150-a2-4 un-shadowed `b` at :4303-4306; it was 6208b7b7). Wherever the old brief says 6208b7b7, use c739eb86; do NOT edit the file.
- Card 150-a2-3 got through the binding (MAP-BOUND 4 nodes, FALLBACK-COUNT 0, RENAMED-OLD 5, FLIPPED-OLD 3: `tools/bench/prep_c150_a2_3_rebase.log:3-13`) and died only on the shadowed `b`.
  Its `tools/bench/prep_c150_a2_3_check.py` (invariant checker, pin 6208b7b7) may be copied to `prep_c150_a2_5_check.py` with the pin set to c739eb86; leave the a2-3 files untouched.
- Plan s07 is still 10a4f59a (the failed rebase wrote nothing); `sim/ring_p4_s07v18_base_real_fsmap.json` does not exist yet.
- If the rebase raises again, quote the traceback line (file:line) and RETURN; do not edit any stage tool.

Report: `tools/bench/diag_c150_a2_5_facts.md` (<= 35 lines), contents as in the old brief's last section. `OPEN:` line. Facts only.
