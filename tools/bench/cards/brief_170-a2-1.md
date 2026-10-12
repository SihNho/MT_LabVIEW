---
card: 170-a2-1
status: current
date: 2026-10-12
---
# Brief 170-a2-1 (assignment 170-2) - re-hash, then ONE read-only LabVIEW read for F4 (the .cal date/time field)

Plan: `docs/d1/ring-p6.md` PD410(e) (line 321-323) and PD409(b) (the .cal rule). Facts so far: `tools/bench/p6_replay_facts.md` F4 (line 93-106).
This card MEASURES; it decides nothing. Nothing is built, nothing is saved, no VI is run, no hardware.

## Steps, in this order (stop at the first unexpected result and return with the facts)
1. **Re-hash first (drift = RETURN).** Hash as BYTES: the card inputs, and in `C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`:
   bed `D1_ring_p6_20261012_212645.vi` c2d9c13c, `D1_ring_p5_20261010_172913.vi` 75773b0d, `D1_ring_p5s01_20261009_124542.vi` 7f2582ae,
   `D1_s1_copy.vi` 3e3d23ce, `replay\D1_s1_replay_20260925_075422.vi` 126f8497, `replay\replay_get_buff_image.vi` 842ecad9,
   `replay\replay_get_image_cal.vi` afce0d04, `replay\replay_imaqdx_get_image_buf.vi` a89dafc1; graph `graph_ring_p6_20261012_212645.json` fbc7b7ee;
   the frames manifest: regenerate `G:\m8_replay_frames` (10045 files) the way `tools/bench/diag_c170_a1_1_hash.py` did, into a NEW path
   `tools/bench/diag_c170_a2_1_manifest.txt`, and compare its md5 with `p6_replay_frames_manifest.txt` 9055d98a. CALL the hashing/manifest
   functions of `diag_c170_a1_1_hash.py` (import) or stagekit; do not write a second copy (docs/script-writing.md). Quote full md5s, expected vs measured.
2. **F4 read, ONE LabVIEW session, read-only, on `claudeDev\D1_s1_copy.vi` 3e3d23ce** (a byte copy of the original; never the original itself;
   use the existing read path other read cards use, a never-saved byte copy or the gscript read verbs that do not save). Read:
   (a) the TYPE of ClusterConstant #26159 'input cluster': element order, each element's type (numeric representation, string, array dims, nested cluster);
   (b) the VALUES of #26136 (string constant in the 'Date and time' concatenation #26428), #26126 (BooleanConstant, 'want seconds?') and #26145 (EnumConstant, 'date format');
   (c) which element of the cluster the NamedBundler #26446 'Date and time' input fills (its name / index in the cluster type).
   Look for an existing verb first: `gscript.read_const_value` (tools/gscript.py:4417), `read_bool_const` (:4391), and a cluster-type reader in
   `docs/toolkit-capabilities.md`; check with `py tools/protocol.py requires <card>`. If NO existing verb reads a cluster constant's element types, say so and write
   a NEW scoped, read-only diagnostic (no save, `labview: read` scope header) that uses VI Server property reads only; do NOT use GUI actions.
3. **After LabVIEW:** `tasklist` shows no LabVIEW; every VI Server reference you opened is closed (handle count before/after); `D1_s1_copy.vi` md5 3e3d23ce unchanged.
4. **Write the cal date/time field rule into `tools/bench/p6_replay_facts.md` F4** (replace the NOT-DETERMINED text in that section only, keep every other line;
   edit with the Edit tool): the cluster layout as read (order, types), the field's position as a RULE ("flattened cluster of N elements; elements before it: ...;
   the field is a length-prefixed (I32, big-endian, because 'prepend array or string size? (T)' and 'byte order' are default) string of text '<date format ...><F136 value><time>'"),
   a recipe for locating the field's offset and length in a given .cal file from the preceding fixed-size/array-size-prefixed elements, and the exact formats of the
   date and time strings as read from the constants (so the compare can verify it by parsing the stored .cal 110-7 files: `tools/bench/m8_out/replay_s1_20260927_184651/cal001`).
   Update `p6_replay_facts.json` key `f4` the same way (verdict FACT or NOT-DETERMINED naming what is still missing). Cite every statement (file:line or the read log line).
   Then, as a CHECK of the rule (offline, no LabVIEW): apply it to the stored 110-7 .cal files of leg A and leg B (cal001 in each run dir; leg B's dir from its `leg.json` run_dir)
   and report the field's offset, length and text in each; report whether the bytes of the two files outside the field are identical. Facts only.

## Not in this card
No recipe, plan, licence, STATUS, INDEX or hook edit; no VI built or saved; no motor, no camera; no peer. A gate FAIL or an unreadable value = RETURN with the facts, no second attempt.
Script rules: `docs/script-writing.md` (calls into shared functions; scope header; ends with `RESULT {...}`; run under `py tools/bgrun.py --material --max-min 15 --log <new log> -- <cmd>`).
