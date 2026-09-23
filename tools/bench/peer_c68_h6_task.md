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
