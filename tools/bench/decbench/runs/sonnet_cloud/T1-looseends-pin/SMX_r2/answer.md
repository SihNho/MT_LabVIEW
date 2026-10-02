**Diagnosis: the pin is wrong, the stage is not.** All structural gates passed on the scratch. The end equals the simulation, exactly the 11 stubs and 13 tunnels are lost, and ENDS/TD are clean (`diag_c116b_scratch.log:279-285`, 43/0 at `:340`). In the Error List `extra == []` and three of four classes equal the pin. Only "loose" is off: 22 = 24 − 11 + **9**, not + 11 (`diag_c116b_scratch_el.log:114-116`). Paths below are under `tools/bench/` unless given.

**Why the pin was a guess.** It assumes (1) every tunnel delete leaves one new loose-end item on its shared net, and (2) only w25438/w25461 were already loose (`plan_l2r2_make.log:44`).
- (2) rests on R1's PD230 list, whose location is "INFERRED, not measured" (`errorlist_expected_D1_l2_r1_20260928_055441.json:75`; `docs/d1-loop12-17-split-plan.md:2072`).
  - Free segments are invisible to `Wire.Terms[]` (`cards/result_115-4.json:22`).
  - The per-net Remove-Loose-Ends separator never ran (`STATUS.md:92`).
  - Per-wire vs per-segment counting is unknown (`archive/peer/2026-09-28-c115e-sel.md:134`).
- (1) extrapolates from R1's shift-register branches to tunnel faces. The project's own delete model records a node-delete remnant as sometimes removed, sometimes kept (`opmodels/delete_object.json:217-218`; `opmodels_onlysink.log:192-194`).
- The −2 term was added between the 26/57 and 24/55 plan runs (`plan_l2r2_make.log:20,42`). Review c115e proposed only an upper bound ("no more than" the nets that lost a sink, `c115e-sel.md:118`). PD230(f) pinned an equality (`docs/d1-loop12-17-split-plan.md:2080`), and 22 satisfies the bound.

**Candidates for the missing 2.**
- Cause: two tunnel deletes left no remnant.
- Alternative: two of the 11 "new" nets were already loose in R1. That is possible only if R1's inferred items were mislocated (seven nets, only w25438/w25461 inside the 13, `diag_c115d_graph.log:17-27`), so it is less likely.
- A reader fault is least likely: all 53 items were double-clicked and the classes reconcile. One OCR'd header count (`diag_c116b_scratch_el.log:27`) is the only unchecked link.

ROOT CAUSE: The P4 pin is an unmeasured per-net model (one new loose end per deleted tunnel unless the net is one of the two inferred-loose nets) extrapolated from R1's inferred accounting, and it overcounts by two nets, most plausibly because two tunnel deletes leave no wire remnant, while the stage itself ran exactly as planned.
TEST: On a scratch byte copy of R1 (md5 f465196b, no rebuild needed) call Wire.Remove Loose Ends on only the 11 shared nets the pin treats as clean (the 13 uids at `plan_l2r2_make.log:26-38` minus w25438/w25461) and read just the Error List header count: unchanged at 55 refutes the already-loose alternative and supports the no-remnant cause, while any drop means those nets were already loose.