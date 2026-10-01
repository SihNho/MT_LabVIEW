# Brief for card 128-4 (cycle 128 judgement) — decisions are in `docs/d1-loop12-17-split-plan.md` Pre-decided 261

## 1. X5 gate false positive (PD261(b)) — log, fix, drain
`py tools/gate_fp.py log --gate X5 --cmd "stage_prerun --prerun tools/recipes/stage_d1_ring_p3b.py" --why "tools/bench/diag_c128_3_x5.log M1" --card 128-4`.
Fix in `tools/stage_prerun.py`: X5 compares wiring ops (excluding `wire_remove_loose_ends`) with plan wiring rows, and
RLE ops with plan RLE rows, each 1:1 (consistent with `SP_WIRING` `:901`). Reset `D` and unwrap/re-wrap `Stage._op`
once per `main()` so an in-process `--dry` then `--prerun` counts once. Self-test cases: P3b recipe X5 PASS
(26/26 + 15/15); a recipe with one extra wire FAILS; two in-process `main()` calls count the same as one. Existing
stage_prerun self-tests stay green. Then `gate_fp.py drain --id <fp-n> --fixed <path:line> --selftest <name>`.

## 2. Donors (PD261(a))
Byte-copy (file copy only, no LabVIEW) vi.lib `Error to Warning.vi` and `Merge Errors.vi` into claudeDev as
`DonorErrSel_ErrToWarning.vi` / `DonorErrSel_MergeErrors.vi`. Uids come from `diag_c128_2_donors.log` / `_out.json`
(Unbundler #157; a Select uid among #529/#542/#479/#386 — use the one 128-2 copied for C1). Record path, md5, uid in
the plan input. An I32 −1 constant: use the existing `const_donor` route the plan already uses for I32 constants.
Merge 128-2's new census samples (`diag_c128_2_donors_out.json`) into `tools/bench/census_samples.json` in its existing
record format; `selftest_case_frame_c124` and `c125_1_offline_measure` stay green.

## 3. Guard rows (PD258(c) + PD261(a))
Add to the P3b plan input (`plan_ring_p3b_make.py`), in the frame where `Num(i)` is written: create Unbundler (donor),
create Select (donor), create I32 −1 constant; `IMAQ Copy` error out → that frame (`fs_frame_to_frame`, measured kind)
→ Unbundler cluster in; Unbundler `status` → Select s; constant → t; BufNum (the frame's inner value already used for
`Num(i)`) → f; Select output → the `Num(i)` element (replacing BufNum's direct wire there). `Latest = BufNum` stays
unconditional. Terminal names + `term_class` from 128-2's measured rows only.

## 4. Split (PD261(d))
Cut the full plan into `plan_ring_p3b1.json` and `plan_ring_p3b2.json`: each ≤ 40 actions counting every create,
wire, crossing and RLE row; RLE rows in the step that makes their loose end; dependency-closed cut (step 1 needs nothing
from step 2); IMAQ Copy + guard in the same step. P3b-2's base is stagesim's END graph of P3b-1, marked provisional
(`base.provisional: true`, `sim_of` P3b-1's plan + md5). Recipes `tools/recipes/stage_d1_ring_p3b1.py` /
`_p3b2.py` (≤120 lines each, inputs only). Error List and census predictions per half (Error List: 54 after w27378's
removal, plus each half's own predicted items, named).

## 5. Checks
Out-of-process: plan dry + prerun and recipe dry + prerun for BOTH halves; `--scratch-required` for P3b-1 recorded
(a scratch run happens regardless, PD261(c)); prior-art review for P3b-1 (new classes Unbundler, Select from vi.lib
copies; FS / GrowableFunction / IndexArray if they are in it) dispatched, verdict annotated. Recipes NEVER launched.
