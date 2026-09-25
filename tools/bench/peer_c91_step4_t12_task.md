ATTACK this claim (card 91-3, failing log tools/bench/diag_c91_step4.log, script tools/bench/diag_c91_step4.py, leg
wrapper tools/bench/diag_c91_step4_leg.py; Jev ladder `new-problem p=0.784`, review owed):

CLAIM: launch 1's ONLY failure class (T12 `registered picks == target` FAIL on every leg, first at leg1 ctl@15; T13 the
table missing the two 8-pick cells) is OUR SCRIPT'S float comparison, not a run fault. The leg wrapper derives the
registered bead count from the saved tra's row width, n = (bytes/rows - 24)/24 with rows = the header's "actual data
points", which gives 15.00004 / 14.00004 (the header undercounts the rows by ~1, `diag_c91_step4.log` REGISTERED lines);
the sequencer compared it with `abs(n - N) < 1e-9`, so a correctly registered 15 (cal001 = 96 + 57152 x 15 -> cal=15.0,
bandpass panels answered 15) was judged a mismatch, which (a) failed T12 on legs whose registration WAS correct
(leg1 rerun: tra 15.00004, cal 15.0, bp 15; leg2 a1: 15.00004 / 15.0 / 15), (b) bought a needless 12-min rerun of leg 2,
and (c) pushed legs 3/4 (8 picks) past HARD_MIN 55 so they were SKIPPED. Every leg's run gates passed: drive_m8 M1-M8
8/0 x4, PM1-PM4 (FPState 4 read back on both min legs, restored to 1), K2/K3, T1-T10 all PASS, TMX 39 after every leg,
S1/bed/kswap/t0 md5 unchanged (T8). The fix (already applied for launch 2): round(n) == N and |n - N| < 0.05, and the
merge re-judges launch 1's rows with the rounded rule. Launch 2 = the two 8-pick legs only, merged with launch 1's rows
(--legs 8min,8ctl --merge tools/bench/t0_step4_91.json).

A SECOND observation the reviewer may attack: the FIRST pick click was lost twice more (leg1 a1: 14 of 15, hwndCapture
22872738 on click 1; leg2 rerun: 14 of 15, hwndCapture 23463992 on click 1), each time with a NON-ZERO foreign mouse
capture recorded on click 1 and on no other pick click; the legs that registered all 15 had hwndCapture 0 on every pick.
That is 3 of 6 stamped legs (incl. the smoke) losing click 1 under a foreign capture, versus 0 of ~16 unstamped legs
(review archive/peer/2026-09-26-c91-smoke-k1.md §1). The site-10 (pick-loop `i`) cadence was clean at click 1 in the
smoke (max gap 122 ms, tools/bench/diag_c91_step4_click1.log). My reading: the capture-holding window is a harness /
Windows input-path state, and the card's "rerun once" rule covered it; the stamps' involvement is NOT excluded by this
data (the foreign capture only ever appeared in stamped runs).

Lost frames (120 s, ~10,680 frames): 15 ctl 2369 (14 beads) / 3024 (15 beads); 15 min 2899 (15) / 2757 (14).

ALREADY RULED OUT: (1) a run/VI fault - all M/PM/K/T1-T10 gates pass on all four legs; (2) a wrong tra layout - the
cal size rule (96 + 57152 n) and the bandpass count agree with round(n) on every leg; (3) a modified input - t0 md5
25ea4f7d re-read after every leg (M7) and T8.

Questions: (a) strongest reason the claim is wrong - is there a reading of tra/cal under which 15.00004 means the
registration was NOT clean (e.g. a truncated last row that also drops a frame)? (b) an alternative explanation for the
lost-first-click-under-foreign-capture pattern being 3/6 stamped vs 0/16 unstamped; (c) what would falsify "script
compare only"; (d) the cheapest discriminating test before launch 2 (the two 8-pick legs). Read-only; never open the VI.
