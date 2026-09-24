Failed prediction, card 76-6 (LabVIEW 2026, VI Server over ActiveX from Python).

Claim under test: `tools/gscript.py` `make_default` (lines ~2985-3030) sets front-panel control values with
VirtualInstrument.SetControlValue, runs our op `OpMakeDefault_v0.vi` (VI method `Default Values:Make Current Default`,
3F3, on a VI reference opened by path), checks the op's error out (empty), then saves the VI (VirtualInstrument
SaveInstrument path), and reads every value back in memory after the save: all equal.

Prediction: after a LabVIEW restart (cold load of the saved file) every value equals what was set.
Observed (`tools/bench/selftest_make_default.log` lines 75-82, run 2): scratch VI = EMPTY_v0 copy + IMAQ Create +
IMAQ ImageToArray; controls created by `Terminal.Create Control` on 'Image Name', 'Border Size' (I32 scalar),
'Optional Rectangle' (I32 1-D array) and a free String[] 'Control Names' (made from Get Controls.vi's terminal,
then that subVI deleted). Values set: Border Size 3, Optional Rectangle [1,2,3,4], Control Names = 10044 path strings.
Cold read: Border Size 3 OK, Control Names 10044 OK, Optional Rectangle EMPTY (len 0).
Earlier (card 76-5, `tools/bench/replay_vis_76d_defaults.log`): the same function lost a String[] ['1'] and a DBL scalar
10044 but kept a 10044-element String[] - so the lost set is not simply "by type".

Already ruled out: op error out non-empty (checked, empty); in-memory values wrong after save (read back, equal);
the negative case (unknown label raises, it does).

Question: what makes one control's default not persist while others in the same VI, same call, do? Name the most likely
mechanism, one competing one, and the cheapest discriminating measurement we can run by VI Server scripting
(no GUI). Our own-tools claim involved: that SaveInstrument saves defaults set by Make Current Default on a
separately-opened reference in the same LabVIEW instance.
