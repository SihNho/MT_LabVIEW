ATTACK this claim (cycle 83 failed prediction, log tools/bench/m8_load_83.log, script tools/bench/drive_m8_load83.py).

CONTEXT. drive_m8_load83.py runs the S1 copy (D1_s1_copy.vi) and the loop-1.5 split (D1_s3_loop15.vi) for real on the
assembled rig, 8 legs: 8 and 15 bead picks x 90 and 150 Hz x 120 s. Between legs, with LabVIEW closed, it opens the
camera through the IMAQdx C API (niimaqdx.dll, IMAQdxOpenCamera mode 0), writes AcquisitionFrameRate = 150 and reads
it back (150.0, period 6666 us, full 1280x1024, offsets 0). Then the VI runs. After the VI exits, a fresh C-API session
reads 90.0009 Hz (period 11111) and the VI's own frame counter advanced 10,679-10,682 frames in 120 s = 89 frames/s in
ALL eight legs, including the four "150 Hz" ones.

PREDICTION THAT FAILED (T5): the VI inherits the camera's current AcquisitionFrameRate, so the 150 Hz legs would count
~150 frames/s. Basis: docs/camera-acquisition-facts.md:25 (rate is a camera attribute) and the wiki's lack of any
AcquisitionFrameRate write in the main VI (only IMAQ Set Camera Attribute in a shutter subVI).

MY EXPLANATION: the main VI's IMAQdx Open Camera (Controller mode) loads the saved camera file (.icd / camera
attribute file, saved at 90 Hz with the 90 Hz exposure contract), which overwrites the volatile 150 Hz I wrote; the
C-API open with mode 0 does NOT reload that file (it kept 150 within the sequencer's own reads). Discriminating test I
plan: set 150 via C API, close, reopen twice via C API only, read; if it still reads 150 the reset belongs to the VI's
open path (camera file load or an attribute write I have not found), if it reads 90 any session open reloads the file.

WHAT THE RESULT MEANS EITHER WAY: the 150 Hz cells in m8_load_83.json are REPEATS of the 90 Hz cells and must be
reported as such (lost frames 12/14 at 8 picks, 3161/3269 at 15 picks - all at ~89 Hz). Real 150 Hz runs need the
rate set INSIDE the VI's session (a panel control or the camera file), which is a VI change, not a driver change.

Please give: the strongest reason my explanation is wrong; an alternative explanation (e.g. IMAQdx Configure Grab or
the ExposureTime contract capping the rate to 90, the VI writing AcquisitionFrameRateRaw, the driver's `--run-s`
patch measuring wrongly); what would falsify mine; the cheapest discriminating test. Also say whether the
frames-per-second figure (frame counter delta / RUN_S) is a valid measure of the camera rate here.
