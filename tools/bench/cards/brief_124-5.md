# Brief for card 124-5 — retry of 124-4: hygiene of the SAVED OpConnectTermUid_v0, then the P3a counter scratch (cycle 124 judgement)

`result_124-4.json` (FAIL 11/1): `claudeDev\OpConnectTermUid_v0.vi` is BUILT (assembled and cold `ExecState` 1, saved by script,
md5 `34120e6314dc44522dee07dcb04ea55a`, labels in `tools/bench/opconnecttermuid_v0_labels.json`); the owner-check fix is proven
on LabVIEW. The run stopped because `diag_c124_opconnecttermuid.py:92` called the op outside `g.hygiene_probe`
(`OpHygieneRefused`). Both failures of that script were our own script bugs.

## Decisions (judgement, cycle 124)
1. **Keep the saved op; do NOT rebuild it.** Verify its md5 == `34120e63…` first, then run ONLY the hygiene probe, inside
   `with g.hygiene_probe(OP):` (≥ 2,000 calls, 0 errors, handles flat ±100) → its record under `tools/bench/op_hygiene/`.
2. **`gscript.connect_term_uid` purges its own junk `Invoke`s** with `_purge_new_invokes`, as `case_wired` does, adding
   `"purged"` and `"invoke_left"` to its return dict (its existing keys unchanged; the fixed interface of `case_inner_face` /
   `case_frame_wire` is untouched).
3. Then the scratch exactly as `brief_124-4.md` § "Scratch proof" (R1–R4, per-frame read-back, census samples, scratch_verify
   record, Invoke +0, bed md5 unchanged, scratch deleted, LabVIEW gone) and the self-tests.

Return at the first unexpected result; R1–R4 are measurements — record what LabVIEW did, finish the run, return.
