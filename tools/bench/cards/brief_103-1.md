# Brief 103-1 — display-stage SPLIT prep (PD215(b), `docs/d1-loop12-17-split-plan.md:1808-1822`)

Detail for the pass lines of `task_103-1.json`. No stage run in this card; the Part-A run is card 103-2.

**P1 — decomposition page `tools/bench/cards/split_plan_103.md` (≤ 1 page).**
- Part A = ops 1–40 exactly as run r7 executed them (`tools/bench/stage_d1_disp_r7.log`) from `claudeDev\D1_s1_copy.vi`
  → `claudeDev\D1_s1_dispA_<ts>.vi`, saved through `gui_save` with
  `-Exception Approved -Evidence "user 2026-09-22 broken-intermediate save"` (broken by design: rows 41–47 missing),
  md5 recorded, and Part A's binding after op 40 (`bind.obj/term/diag`) written to its result JSON.
  Pass: E1 through op 40 with WARN-class diffs only (`stagexec.classify_step_diff`), real step-40 read == simulated step 40.
- Part B = ops 41–47 from that file in a FRESH LabVIEW (memory baseline = one VI load), via a `stagexec --from-step 40`
  entry that binds Part A's recorded uids instead of re-executing → W1 RBW (pre-existing uids only) / E2 ExecState 1 /
  E3 cdiff == the 21 PD213(d) rows + added objects / #25261 False / PS saved by script → `claudeDev\D1_s1_disp_<ts>.vi`.
- For each sub-step: its saved file name and its pass criterion.

**P2 — prior art ONCE** (`prior_art_review.py` on the page). A non-`novel` verdict is released only by `REFUTED:` /
`FIXED:` in the review file (CLAUDE.md §5); otherwise stop and return FAIL with the verdict.

**P3 — Wait (ms) donor, MEASURED first.** Does `claudeDev\OpPrimDonor_v0.vi` (or another NI example already
byte-copied under claudeDev) contain a `Wait (ms)` node? Report node uid, class, owner diagram, terminal names. If
none: byte-copy an NI example VI that contains `Wait (ms)` into `claudeDev\OpWaitDonor_v0.vi` (never edit vi.lib or
examples — rule 1), measure the same, pin md5. Register it in `tools/bench/facts_c100_oplabels.json` `donors` exactly
as Max & Min is registered. Facts → `tools/bench/facts_c103_donor.json`.

**P4 — plan.** `r7_wait` row of `tools/bench/sim/disp/stageplan_disp_r4_open.json` → `"prim": "Wait (ms)"`, routed
through `create_primitive_nested` (`OpPrimCopyNested_v0`). Re-sim FINAL (same 21 open rows, 0 unclassified), re-dry
0 unroutable, `stage_prerun` all PASS, `py tools/protocol.py requires` green.

**P5 — recipe Part-A mode.** An explicit stop-after-step argument (40): after op 40 the recipe reads the real state,
compares it to simulated step 40 (WARN-class only), gui_saves `D1_s1_dispA_<ts>.vi`, writes md5 + binding JSON, and
dispatches NO op > 40. Prove it offline/dry (self-test). stagexec self-test stays green. The `--from-step` Part-B entry
may be built here too if it fits the budget; it is NOT a pass line of this card.

**Not in scope:** `stagekit.copy_in` (MOVE_DST-only, leave it); the S1 file as donor (REFUSED by PD215(b), +300 MB);
the owed tooling card (stop-record read-only refusal, pre-run precondition check, selftest_stagekit classing).
