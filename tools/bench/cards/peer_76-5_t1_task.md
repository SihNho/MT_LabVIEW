ATTACK this claim about failed gates T1/T2/T3 in tools/bench/replay_vis_76d_test.log (script tools/bench/diag_replay_gbtest.py;
the stand-ins were built by tools/bench/diag_replay_standins.py, log tools/bench/replay_vis_76d.log run 2 = 35/0; card 76-5).

OBSERVED (test run 2): harness = IMAQ Create -> VUT -> IMAQ ImageToArray, all error outs on indicators. Get-buff copy
(replay_get_buff_image.vi, only #529 -> replay_imaqdx_get_image_buf.vi) with b = 8217, 8218, and b = 5 after a restart:
'Image Pixels (U8)' EMPTY (shape (0,)), every error cluster (False, 0, ''), 'current image number' == b, 'Missed frames?'
TRUE. Cal stand-in (replay_get_image_cal.vi), 3 calls: pixels EMPTY, errors clean, 'Buffer Number Out' 0, 0, 0 (predicted 0,1,2).
The fixture frames are 8-bit 1280x1024 (tools/gpu/fixture.py:5), so a U16 image type is ruled out.

STAND-IN DESIGN (diag_replay_standins.py): For loop whose N comes from an auto-indexed String[] control 'Control Names'
(default meant to be ['1']); uninitialised shift register with Increment in the body; Increment.x+1 leaves by a border wire
(tunnel IndexMode 0) into a top-level Decrement -> k; Q&R(k, y) with control 'y' (default meant 10044); Index Array over
String[] control 'Control Names 2' (default meant = 10044 paths G:\m8_replay_frames\f%05d.tif) -> StrToPath.vi -> IMAQ
ReadFile (Image <- Image In, Image Out -> Image Out indicator). ReadFile's own error out is UNWIRED (the plan says error in
passes straight to error out). Defaults were set by gscript.make_default (SetControlValue on a vi_ref, then OpMakeDefault
'Make Current Default', then save), which returned 38,896 B; then the file was copied.

CLAIM (E1): the defaults did not persist in the saved stand-ins, so N = 0 (loop never runs; the mode-0 output tunnel yields
0; Decrement -> -1; coerced into U32 Buffer Number Out -> 0) and the path array is empty (empty path -> ReadFile errors,
silently, because its error out is unwired) -> the image stays empty. ALTERNATIVE I considered (E2): defaults persisted but
the counter/ReadFile body is at fault. Planned discriminator: a READ-ONLY cold load of both stand-ins reading the three
controls' values ('Control Names', 'Control Names 2', 'y') with nothing run (tools/bench/diag_replay_defaults.py).

Give the strongest reason E1 is wrong, a better alternative, what would falsify E1, and whether the planned read-only
discriminator actually separates E1 from the alternatives (e.g. does a cold vi_ref GetControlValue show saved defaults?).
