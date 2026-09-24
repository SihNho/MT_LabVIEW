## What was done with it
(for archive/peer/2026-09-25-76-6-makedefault-cold.md - card 76-6's write flags do not cover that file)

Material session 76-6, 2026-09-25 05:3x. ACCEPTED as the framing: (1) the after-save `_check` in `gscript.make_default`
reads CURRENT values and cannot catch a lost default - acknowledged, the S2 PASS in `tools/bench/selftest_make_default.log`
is therefore uninformative; only S3 (cold read) counts, and it FAILED 2/3 with Border Size 3 == IMAQ Create's own default,
so the informative count is 1 persisted of 2 (10,044-element String[] kept, I32[4] lost). (2) H1 (Make Current Default
did not copy the values; front panel closed) vs H2 (lost on save/load) is NOT yet discriminated. No further LabVIEW run
in card 76-6: the self-test's failure budget of 2 is spent (run 1 our-script-bug, IMAQ Create 'Image Name' required;
run 2 this finding). The prescribed test (Border Size 5, String[]/I32[] size sweep, sentinel + ReinitializeAllToDefault
before save, then save + reload, then with the panel open; probe ReinitializeAllToDefault on ActiveX first) is handed to
the judgement session as the next card; the stand-ins were NOT rebuilt.
