# Brief for card 123-8 — P3a plan and recipe on the REAL P2b graph, no build (cycle 123 judgement, 2026-10-01)

Design: `docs/d1-loop12-17-split-plan.md` Pre-decided **246(c)(d)**, **247(a)(b)(d)**, **248(a)(d)**. Step list:
`tools/bench/ring_p3_steps.md` (row P3a). Facts: `tools/bench/facts_c123_p3.json`. Routes now present: `const_sr`
(shift-register initial value from a constant, 123-3), `case_wired` (case with a wired selector, 123-7), `$work` donors for
`Equal?`/`Increment`/`Quotient & Remainder` (`diag_c123_routes.log:55`), `Wait (ms)` donor (`facts_c100_oplabels.json:266-273`).

## Steps
1. Read the graph of the saved bed `claudeDev\D1_ring_p2b_20261001_140658.vi` (md5 `652b1447…`), read-only, no save →
   `tools/bench/graph_ring_p2b_<ts>.json`. Also read BufNum's representation (`read_term_type` on `#6810` `t6897`).
2. `tools/bench/plan_ring_p3a.json` on that graph (base = the real graph, not provisional), ≤ 25 rows, stagesim FINAL:
   in While `#637` (body `639`):
   - `Wait (ms)` with a constant 1, no data dependency on the frame path;
   - a previous-BufNum shift register on `#637`, initial value from a constant on FS1 frame `686` = −1 in BufNum's own
     representation (I32 → `DonorRingConst_v0` `#249`; U32 → `DonorSRInit_v0` `#134` = 4294967295); its right terminal
     takes BufNum (a branch of w3747);
   - `Equal?`: x = BufNum (branch of w3747), y = the previous-BufNum register's left terminal;
   - `case_wired` on `639`, selector = `Equal?`'s `x = y?`: True = duplicate (empty, counter passed through), False = new
     frame;
   - a new-frame counter register on `#637`, I32 initial 0 (`DonorSRInit_v0` `#248`) from a constant on `686`; in the False
     frame `Increment` → the output tunnel → the register's right terminal; the True frame wires the count straight through;
   - `Quotient & Remainder` in the False frame: x = the count (the register's left value through the case), y = I32
     constant 20; its remainder (`i`) stays unconnected until P3b.
   The census prediction file comes from `tools/census_predict.py` samples where measured; unmeasured classes are marked
   unmeasured (the prerun's X15 line reports them as CENSUS-UNPREDICTED, which then requires the scratch run).
   The Error List prediction (new items) is written with its reasoning.
3. `tools/recipes/stage_d1_ring_p3a.py` ≤ 120 lines on stagekit, using stagekit's census gate helper.
4. dry + prerun PASS; prior-art review (`prior_art_review.py --recipe`) answered, verdict and any release recorded;
   `py tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p3a.py` exit code recorded.

## Rules
- NO scratch run and NO launch in this card. LabVIEW only for the read in step 1; LabVIEW closed and verified gone after it.
- If the budget or the 60-minute backstop stops the card, return with the state recorded (which step, which files).
- A fact that contradicts PD246/247/248 is returned as OPEN, not decided. Return at the first unexpected result.
