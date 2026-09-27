ATTACK this claim about two FAILED offline self-test runs in card 112-4 (tools/bench/cards/task_112-4.json), both BEFORE any
LabVIEW stage launch:

(A) tools/bench/selftest_stagekit_c112d.log (script tools/bench/selftest_stagekit.py, 47 pass / 2 fail, BGRUN END rc=1, NO RESULT LINE):
    J1 FAIL with `com_error ... LabVIEW: (Hex 0x7) File not found`, 's': 14.0, then case_j IndexError (list index out of range).
(B) tools/bench/selftest_d4_l2b2a.log (script tools/bench/selftest_d4_l2b2a.py): T0a..T1b PASS, then `TypeError: keywords must be strings`
    at line 84 (`dict(info, **{25829: ...})`, int keys), rc=1.

CLAIM (mine):
(A) is an INVOCATION error, not a regression of the edit under test. I ran `py -u tools/bench/selftest_stagekit.py` DIRECTLY. Case J
    (create_local_read) is written to run under the dry harness `py tools/stage_prerun.py --dry tools/bench/selftest_stagekit.py`, which
    installs a fake gscript (tools/stage_prerun.py:562-608); run directly, gscript is REAL, so create_local_read made a real COM call into
    LabVIEW (14 s: COM activation) for a panel that does not exist -> error 7 -> [] -> IndexError. The previous record of this self-test
    is exactly that dry form: tools/bench/selftest_stagekit_c101-5_dry2.log:73 J1 PASS ('s': 0.0), :79 `51 pass / 0 fail`.
    The edit under test (tools/stagekit.py, card 112-4) ADDS five pure functions (d4_load/d4_ok/d4_e1/d4_pb/d4_form + _d4_terms,
    D4_FAIL_KEYS) between uid_edges and fixture_listing and changes no existing function; cases A..I passed 47/47 in the direct run.
    No LabVIEW process is running now (tasklist: no LabVIEW.exe), so the COM-activated instance exited with the Python process.
(B) is a bug in my own new test script (Python forbids non-string ** keys); fixed to `i2 = dict(info); i2[25829] = ...`.

Already ruled out: a change to any existing stagekit function (the edit only inserts new functions); an open LabVIEW left behind (tasklist).
Attack: (a) could the J1 failure come from the new module-level code in stagekit (import-time side effect, a name shadowing something
case J uses, e.g. `_d4_terms`/`D4_FAIL_KEYS`), rather than from the invocation; (b) is a direct run of selftest_stagekit.py supposed to
be offline (its docstring says "Nothing here opens COM") - i.e. is case J itself a latent defect that the dry harness hides; (c) did the
COM activation leave anything behind (a LabVIEW instance, a stale lock, a created file) that would matter for the next stage launch;
(d) the cheapest discriminating test (my proposal: rerun it under `py tools/stage_prerun.py --dry tools/bench/selftest_stagekit.py`
and expect 51/0; plus rerun selftest_d4_l2b2a.py and expect all gates PASS).
