# Prior-art round c107c - tools/recipes/stage_d1_disp.py (md5 1d1784ab0d9b714189e52f27d02ab2e4)

Card 107-3 (cycle 107). Plan of record: docs/d1-loop12-17-split-plan.md PD216(c)/(g), PD219(c).

## What is being released

The display-loop stage recipe `tools/recipes/stage_d1_disp.py` was last released by prior-art review
`archive/peer/2026-09-27-priorart-priorart-c104d-e3.md` (verdict novel) at recipe sha e22f2b50. Card 106-3 then
changed its bytes (git 4dbc3fc -> 93c2bfe): nine helpers were MOVED, unchanged, from the recipe into
`tools/stagexec.py` (DryPlanBE, w0_wires, report_stop, log_step_diffs, b1_gate, part_a_gates, w1_rbw, e3_gate,
kill_labview_at_exit); the recipe keeps only the gate order and the inputs (149 -> ~90 lines). The class `DryBE`,
`cdiff`, `part_a`, the inline W1 RBW block, the inline E3 gate and the taskkill-at-exit block are now calls to those
stagexec functions. `CUT` now comes from `SX.CUT`; imports of `stagesim`, `allterms`, `subprocess`, `time` dropped.

## What will run next (not in this card)

Part-B mode: `py tools/stage_prerun.py --dry tools/recipes/stage_d1_disp.py --from-step 33 --base
claudeDev\D1_s1_dispA_20260927_024535.vi` (recorded dry), then one Part-B LabVIEW run of ops 34-47 on the Part-A
file, end gates E1/W1/E2/E3/PS, saving claudeDev\D1_s1_disp_<ts>.vi at ExecState 1.

## Question for this review

Did the move duplicate a helper stagexec (or stagekit / gscript) ALREADY had under another name, or did it change
any gate's condition while claiming "moved unchanged"? Is there an earlier record that this refactor (recipe body
into stagexec helpers) was tried and reverted?
