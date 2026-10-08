ATTACK this claim about a failed prediction in tools/bench/diag_c153_a2_1_md5_before.log (script tools/bench/diag_c153_a2_1_md5.py).

Context: an offline md5 pin check (hashes files only, no LabVIEW) predicted that the ORIGINAL LabVIEW VI
`..\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (one directory above the project root) still hashes to the prefix
c39f36e0 - the md5 recorded by the on-disk node/terminal census `tools/bench/orig_3state_nodeterms.json` lines 2-6 (taken
2026-09-18) and by every earlier log (e.g. tools/bench/drive_original_copy_v5.log:22). Observed (log line 13):
  FAIL 2f048e3a18de3b5e3ca8368f6a24dae0 c39f36e0 <original path>
The second FAIL in the same log (docs/wiki/subvi/D1_s1_copy.json, true md5 5de014fe vs pin 3e3d23ce) was a mistyped pin by the
script author (the pin was never measured), not a file change.

CLAIM 1: the original file was changed on disk after 2026-09-18 by a save outside this project's sessions (the user owns the
original's state and runs real experiments with it; CLAUDE.md rule 1 forbids this project from saving it), so the 2026-09-18 census
can no longer be assumed to describe the current file.
CLAIM 2: this is not a fault of the md5 script; the right next step is ONE read-only read of a byte copy of the CURRENT original
(copy under user.lib\claudeDev, copy md5 == original md5, opened headless by COM, graph read only, no edit/save/Run, then
deleted) to measure which terminal feeds the 'frame index' input of its `save trace.vi` call (census node #376 t7, wire 3268),
and to compare with the census and with the S1 derived copy (w3268 <- While #637 iteration terminal i, docs/cycle27-plan.md:3748-3751).

Already ruled out: the census json itself is unchanged (b9e6849f, log line 14); every other pinned tool/VI matches (log lines 3-12);
no session of this project opened the original in this card.

Questions: (a) the strongest reason Claim 1 is wrong (e.g. a LabVIEW autosave/relink on open, a different file at the same path,
a copy-back from another drive, a project session that did save it - what in this repo would show that); (b) whether a byte copy
read can be misleading here (e.g. linked subVI resolution differing for a copy in claudeDev vs the original's folder, which could
change node uids or terminal sets); (c) the cheapest discriminating test before the LabVIEW read (e.g. mtime vs session logs,
saved-version bytes 19 00 80 00 vs 26 00 80 00 counts, size delta).
