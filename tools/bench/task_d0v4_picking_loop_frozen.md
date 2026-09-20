PREDICTION (ours): on `claudeDev\Track_D0_copy_20260918.vi` (the "4.5" copy of the tracking VI), a GUI
click on `Done Picking \nBeads?` (uid 11819) at panel point (1114,915) would end the bead-picking while
loop and advance the VI to bead-profile calibration — because the identical click at the identical panel
rectangle did exactly that on the V6 copy (`tools/bench/drive_original_copy_v3.py`, 16/16, rc=0, 2026-09-17).

OBSERVATION (`tools/bench/drive_original_copy_v4.log`, 2026-09-18 17:25): it did not. Over 303 s the
picking loop never ended; no `choose bandpass` window and no save dialog ever appeared; the VI stayed
ExecState=2. Three further readings from the same run:
 (1) the panel-pick counter `Count` went 0 -> 1 on the first of three picks and then stayed 1;
 (2) the frame counter `current image number` read 0 for the entire run;
 (3) the stop Booleans written by VI Server (`stop (end)` uid 7 and `stop (end) 2` uid 19587) were set
     True and STAYED True — never consumed — through a 61 s single-write test and a further 60 s of 30
     re-arms. Only a COM Abort ended the VI (ExecState 1 after ~3 s).

OUR HYPOTHESIS (attack this): the bead-picking loop is not iterating at all because it is blocked waiting
for a camera frame that never arrives, so no front-panel control — the done button included — is ever
read. One cause explains all three readings together; "the click missed" explains only the first.

ALREADY RULED OUT (do not re-propose these):
 - Geometry/coordinates: the 4.5 panel rect is (-6,51,1930,1107), size (1936,1056), delta (0,0) against
   the V6 rect the v3 points were derived from (gate 7 PASS), so the derived click points are v3's exactly.
 - File mix-up / corruption: md5 of the original and of the copy are identical before and after the run;
   the copy was never saved and is still on disk.
 - A stale driver: v4 imports v2/v3's COM apartment, never-joined RunThread and hwnd token wholesale; the
   three `choose bandpass` clicks in the same run use the proven `clickprobe` path.

Give us the strongest reason our hypothesis is WRONG, one alternative explanation that also covers all
three readings, what observation would falsify ours, and the single cheapest discriminating test.
Relevant if it helps: rig state is ASSEMBLED with NO BEADS mounted; camera is 1280x1024 at 90 Hz and a
new session resets ROI and exposure; the VI is LabVIEW 2026 with IMAQdx.
