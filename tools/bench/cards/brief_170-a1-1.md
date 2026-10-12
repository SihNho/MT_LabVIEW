# Brief 170-a1-1 - P6-2 replay facts F1-F6 (offline, no LabVIEW, no hardware)

Plan: `docs/d1/ring-p6.md:231` PD409(a)(d). Read that item first. This card MEASURES facts; it makes no decision.

## 1. Re-hash (first, report drift before anything else)
Hash as BYTES only (never open a .vi): the card inputs, and the VIs in
`C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev`:
bed `D1_ring_p6_20261012_212645.vi` c2d9c13c, `D1_ring_p5_20261010_172913.vi` 75773b0d, P5-1 7f2582ae, S1 3e3d23ce
(find its file via `tools/bench/plans/plan_replay_swap_110.json`), `replay\D1_s1_replay_20260925_075422.vi` 126f8497,
stand-ins `replay\replay_get_buff_image.vi` 842ecad9, `replay\replay_get_image_cal.vi` afce0d04, and the third stand-in
a89dafc1 (find which file from `tools/bench/diag_replay_standins.py` / the 110 plan). Also a manifest of
`G:\m8_replay_frames` (10045 files): sorted name + size + md5 per file written to
`tools/bench/p6_replay_frames_manifest.txt`; the md5 of that file is the "manifest md5". Report expected vs measured
per row. The md5 prefixes above are the purpose's expected values; quote the full md5 you measure.
Use a shared hashing helper if one exists (grep `def .*md5` in tools/stagekit.py, tools/bench/prep_c168_hashlib.py);
do not write a new one beside it.

## 2. Facts F1-F6 (PD409(d)) - write `tools/bench/p6_replay_facts.md` and `.json`
Each fact: FACT (with file:line or graph uid you read in this card) or NOT-DETERMINED (what is missing).
- F1: #6810 and #22692 present by uid in `tools/bench/graph_ring_p6_20261012_212645.json` with their old callees; which
  loop calls each, and how many times per tracked frame in P6 vs in S1.
- F2: what P6 uses to decide "new frame" (P3a counter, PD246(c); nodes #26879 / #27039 per the plan) and what the buf
  stand-in's BN Out = BN In feeds it. Verdict word: EVERY / SOME / NONE of the stand-in frames get tracked.
- F3: where S1's lost-frames count and the ring's discard count (#29724 'discards' / 'next discards') end up
  (indicator, local, saved file) and how a leg reads each. Verdict word per count: READABLE / NOT READABLE.
- F4: the cal date/time field: offset and length in the .cal file, from the ORIGINAL's cal write path (cite the node or
  format string in the stored graph / source), NOT from where two files differ.
- F5: every file a leg writes, and which ones the v5 cleanup deletes (`tools/bench/drive_original_copy_v5.py:688`).
- F6: what the leg chain needs to run a ring replay copy (X5-X9 of `tools/bench/p6_replay_ready.md`): plan literal,
  driver md5 pins, leg kind, run-length / frame-count parameter - and the existing shared function that takes each.
  No copied driver (`docs/script-writing.md`).

## 3. Output shape
`p6_replay_facts.json`: keys `f1`..`f6`, each `{"verdict": ..., "cites": [...], "text": ...}`, plus `rehash` rows and
`handback_gate`. `p6_replay_facts.md` ends with ONE line:
`HANDBACK-GATE: F2=<EVERY|SOME|NONE> F3=<discard READABLE|NOT READABLE; lost READABLE|NOT READABLE> -> <PROCEED|HANDBACK>`
where HANDBACK = F2 is NONE or the discard count is NOT READABLE.

## 4. Do not
Open LabVIEW or any .vi; touch hardware; edit plan, STATUS, hooks or stage tools; start a second hashing script when a
shared one exists. A hook refusal = BLOCKED with its text.
