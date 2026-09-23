# c68-h6-fixture-listing

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $0.8606  in 16 / out 6640 / cache-create 74317 / cache-read 641059  (77s, 14 turn(s))
- **date:** 2026-09-24 00:25:58
- **outcome:** ANSWERED (81s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed gate H6 in tools/bench/q_m4_copy_probe.log (cycle 68) - attack the explanation

The diagnostic worked on the NI Moving-Objects fixture file `claudeDev\NIScriptingExamples\Moving Objects\Test - Moving
Objects Target.vi` (Stage work_dir = that folder), saved nothing, and its gate H6 compares the `*.vi` listing of the
claudeDev TOP folder before/after against an expected list. Observed: `added [] removed []`; expected list
`['Test - Moving Objects Target.vi']` (`q_m4_copy_probe.log:76`). `tools/stagekit.py` Stage.close(): when
`expect_files` is None it expects `[basename(self.work)]` if the work file exists - but the work file lives in a
SUBFOLDER that the listing (`glob(CLAUDEDEV/*.vi)`) never sees.

Our explanation: an expectation bug in our own script (the default expectation assumes the work copy is in the claudeDev
top folder); the machine did exactly what was intended (nothing left in claudeDev, nothing removed). All other gates
passed: bed md5 unchanged, pins hold, refs 5/5. The fix: pass `expect_files=[]` for a fixture-folder work copy.

Already ruled out: a stray file in claudeDev (the listing diff is empty both ways).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The diagnosis is right, but "the machine did exactly what was intended" was never measured, and the proposed fix makes H6 pass without checking the folder the run actually wrote to.**

The bug diagnosis stands. The listing only reads the claudeDev top folder: `glob(os.path.join(CLAUDEDEV, "*.vi"))` at `tools/stagekit.py:1067` and `:277`, and Python's glob does not look into subfolders unless you pass `recursive=True` with `**` (https://docs.python.org/3/library/glob.html). The work file sits in `claudeDev\NIScriptingExamples\Moving Objects\` (`tools/gscript.py:88-90`). The default expectation at `stagekit.py:1075-1076` adds `basename(self.work)` whenever that file exists, so it assumed the work copy was in the top folder. The probe's own plan also expected `[]`: "files left in claudeDev == []" (`q_m4_copy_probe.py:10`). The empty diff is real, not an empty listing: the BEFORE listing held 245 files (`q_m4_copy_probe.log:4`).

**1. Strongest reason the claim is wrong.** Nobody measured that the run left nothing behind in the folder it actually wrote to. The run overwrote both files in the Moving-Objects folder with the bed's bytes:
- the Target file, when `Stage.start` copied the input over it (`stagekit.py:296`);
- the Source file, at `q_m4_copy_probe.py:29` (confirmed by gate K4, `log:23`).

H6 cannot see that folder, and no gate checks it. The only evidence that the fixtures were restored is an unconditional print (`q_m4_copy_probe.py:54`, `log:82`) that runs after the gates, with no md5 comparison.

Changing the expectation to `[]`, which `q_m4_copy_probe.py:49` already does, turns a false FAIL into a PASS that says nothing about that folder. H6 would still pass if the fixtures were left with the bed's bytes in them. That exact failure happened on 2026-08-28 (`gscript.py:91-93`).

There is a second gap in the restore. `restore_move_fixtures` first copies live → `.ORIG.bak` whenever the `.bak` file is missing (`gscript.py:1514-1515`). If a `.bak` was ever missing, "restore" would save the bed's bytes as the new "pristine" copy, and the log still says "restored".

**2. Alternative explanation for the same evidence.** `added [] removed []` fits both "nothing was left anywhere" and "the fixture folder was left in a bad state". The top-folder diff cannot tell the two apart. The claim treats the first as proven.

**3. What would falsify the claim.** Either of these, measured after the final `restore_move_fixtures()`:
- `md5(MOVE_DST) != md5(MOVE_DST_ORIG)` or `md5(MOVE_SRC) != md5(MOVE_SRC_ORIG)`;
- a `*.vi` in `MOVE_DIR` that was not there before.

**Also missing from "all other gates passed":** LabVIEW's handle count went from 33,987 to 63,471 during a 70-second run (`log:16`, `log:66`). That is +29.5k, although refs opened and closed matched 5/5. Loading a bed with 173 diagrams may explain it, but it was not reported. Rule 3's reference-hygiene section treats handle growth as the leak measure.

**4. Cheapest test that separates the two (read-only, about 1 second, no LabVIEW):**
- md5 `Test - Moving Objects Target.vi` against its `.ORIG.bak`, and the Source file against its `.ORIG.bak`;
- confirm neither `.bak` has the bed's md5 `fdd6d74ac8a5ba0c1a545ad89ff2996f`;
- list `MOVE_DIR\*.vi`.

If all match and neither `.bak` is the bed, the claim holds in full.

**Recommended fix:** keep `expect_files=[]` for the top folder. Then add a gate after the restore, not a print: both fixtures match their `.ORIG.bak`, neither `.bak` has the bed's md5, and the `MOVE_DIR` listing is unchanged. Also make `restore_move_fixtures` fail instead of silently creating a missing `.ORIG.bak` from the live file.

**What would change my mind:** evidence that some other step already checks the fixtures' md5 after every run that swaps them in. I found none in `stagekit.close()` or the probe.

## Sources

(extract from answer)

## What was done with it

Cycle 68 material, 2026-09-24 00:2x. Owed because guard_peer armed on `tools/bench/q_m4_copy_probe.log:76` (Jev ladder
no verdict).
- §4 ACCEPTED AND RUN: `tools/bench/q_fixture_check.py` -> `tools/bench/q_fixture_check.log`: both fixtures == their
  `.ORIG.bak` (Source 13397129..., Target 055b62fa...), neither is the bed's md5, listing = the 6 shipped example VIs.
  So the claim holds in full for this run.
- §1 / Recommended fix ACCEPTED: `tools/stagekit.py` `fixtures_check()` + `fixture_listing()` (gate rows FX, md5 vs
  `.bak`, bad-md5 list, listing unchanged); called after the restore in `tools/recipes/stage_d1_m4a.py` and
  `stage_d1_m4b.py`, and it sets the process rc. `q_m4_copy_probe.py` now passes `expect_files=[]`.
- "make restore_move_fixtures fail on a missing .bak": NOT done (gscript change outside this task; the FX gate's
  bad-md5 check catches the case it describes). Left to judgement.
- Handle growth 33,987 -> 63,471 in the probe: RECORDED as a fact (bed load, 173 diagrams; refs 5/5). Not diagnosed.
(Claude fills in)

JEV-DISCHARGE: q_m4_copy_probe.log (2026-09-24 00:26:01, p=0.834)
  This failing run was released without a NEW peer review: Jev judged, at the probability shown, that the failure above is the one this review already attacks (tools/bench/jev_gate.py, docs/jev-integration-plan.md row #1). The review itself is the evidence; this line only records which failure was charged to it.
