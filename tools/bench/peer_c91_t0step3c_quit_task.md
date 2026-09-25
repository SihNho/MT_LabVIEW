ATTACK this claim (card 91-1, log tools/bench/diag_c91_t0_step3c_r2.log, script tools/bench/diag_c91_t0_step3c.py):

CLAIM: The only failure in diag_c91_t0_step3c_r2.log is a HARNESS artefact in the script's own [Q] tail, not a build fault.
The build phase ended 73 gates pass / 0 fail (log :721-754): all 12 stamp sites at While-body level ExecState 1,
computation_diff(S1,new) 0 rows / removed 0 / added 24 = 2 x 12 (CallLibrary + DigitalNumericConstant only), the file
claudeDev\D1_s1_t0_20260926_055551.vi was saved BY SCRIPT at ExecState 1 (md5 25ea4f7d10d91c41c4b5de64f850c945, S3 re-read
ExecState 1), H2/H3 md5 pins hold, H6 files-left == [that file]. THEN the script's own quit step
(`subprocess.run([python, "-c", "Dispatch('LabVIEW.Application').Quit()"], timeout=90)`, script line 183) raised
TimeoutExpired, which was NOT caught, so the process died with rc=1 and LabVIEW (pid 24856, 746 MB) stayed alive.
Explanation: after stagekit.close() (which closes panels, restarts LabVIEW when scratches exist, and reads handles),
COM `Quit` on a LabVIEW that still holds the just-saved VI's front panel (or the panel of the byte-copied SCRATCH from run 1's
code path) blocks on a modal prompt or on the recompile of the reloaded VI; run 1 of the SAME script
(diag_c91_t0_step3c.log:1332, quit rc 1, forced=False, gone after the 60 s wait) shows the quit can also return late but fine.
The fix is in OUR script: wrap the quit in try/except TimeoutExpired and fall through to the existing taskkill branch.
Nothing about the saved artefact is in doubt.

ALREADY RULED OUT: (1) a broken build - every build gate passed and ExecState 1 was re-read after the save (:734-754);
(2) a modified input - K1/H2 md5 3e3d23ce... before and after, all pins hold (H3); (3) a leftover scratch - run 2 ran with
--reuse-probe, so no scratch copy was made (glob claudeDev\*c91* empty after the run).

Questions: (a) strongest reason the claim is wrong - could a LabVIEW that refuses COM Quit after a scripted save mean the
saved file is not what the md5 says (e.g. a deferred write)? (b) alternative explanation for the 90 s Quit block on run 2
but not run 1; (c) what would falsify "harness only"; (d) the cheapest discriminating test before the smoke run of that
file (tools/bench/diag_c90_t0_smoke.py, which restarts LabVIEW itself via bench_prep.restart_labview).
