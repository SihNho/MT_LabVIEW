ATTACK this claim (card 91-3, failing log tools/bench/diag_c91_t0_smoke.log, script tools/bench/diag_c90_t0_smoke.py,
driver tools/bench/drive_m8.py on drive_original_copy_v5.py; Jev ladder verdict `already-reviewed-class p=0.426`, below
0.65, so this review is owed on the old path):

CLAIM: the smoke run's ONE failed gate (K1 = drive_m8 `M2 reached experiment loop` FAIL, because v5 step run1.L3 counted
2 of 3 pick MARKERS drawn by the VI - the click at (489,810) left no marker - and run1.L8 the `choose bandpass` panel
count did not match) is a HARNESS GUI artefact of the bead-pick automation (a click delivered before the live display
had redrawn, or on a frame the VI did not register), NOT an effect of the 12 stamp CLFN nodes added to
D1_s1_t0_20260926_055551.vi. Evidence: the VI DID reach the experiment loop - cal001 + tra001-000 were written
(tra header 2949 points, `diag_c91_t0_smoke.log` M5 PASS), it was stopped by its own control (M4 PASS), 12 stamp
files with 2950/940/917 stamps landed in the fresh T0STAMP_DIR (K2 PASS, K3 PASS), Total Lost Frames 25 in 30 s, and
the source md5 was unchanged after the run (M7 PASS). The identical L3/L8 class of failure was seen on the
UNMODIFIED S1 copy in earlier cycles (2 of 3 markers is a known v5 pick-registration flake); the smoke's purpose - a
file for every loop's `i` site (PD197(f)) - was met. Consequence I intend: proceed to step 4 (four 120 s legs at 15 and
8 picks) on this VI, with the card rule "a leg whose registered picks differ from its target is logged and rerun once".

ALREADY RULED OUT: (1) the stamp files being stale - T0STAMP_DIR was a fresh per-run directory and the default dir
gained no file (K3); (2) a modified input - M7 re-read the --src md5 25ea4f7d... after the run; (3) the loop never
running - 2949 tra points and 2950 site-0 stamps in 30 s (~98 /s including the pick phase frames).

Questions: (a) strongest reason the claim is wrong - could a stamp node on the DISPLAY loop (sites 11 U8 image, 12
image data, 13 picture, 16 circle/text case tunnel) delay or drop the marker draw so that a registered click shows no
marker, or could the stamp on the tracking loop's `i`/bool-array wires change when the pick loop accepts clicks?
(b) an alternative explanation of "2 of 3 markers + bandpass-panel mismatch"; (c) what observation would falsify
"harness only" (e.g. what in the .cal / .tra would show 2 picks were registered instead of 3, and how to count the
registered picks from the saved files rather than from the markers); (d) the cheapest discriminating test before the
four 120 s legs. Read-only: never open the VI; the files named above are all under tools/bench/.
