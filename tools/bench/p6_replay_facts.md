---
type: facts
status: current
date: 2026-10-12
card: 170-a1-1
---
# P6-2 replay facts F1-F6 (PD409(d), docs/d1/ring-p6.md:260-269) - facts only, no decision
Written by `tools/bench/diag_c170_a1_1_facts.py` (offline, LabVIEW reads 0). Re-hash by `diag_c170_a1_1_hash.py` -> `tools/bench/diag_c170_a1_1.log`. Machine-readable: `tools/bench/p6_replay_facts.json`. P6 graph cites are graph uids (single-line json).

## 1 - re-hash (drift first): NO DRIFT

| row | expected | measured | status |
|---|---|---|---|
| card input tools/bench/cards/brief_170-a1-1.md | f26bb5f03b829a3e5cef592e64bf83aa | f26bb5f03b829a3e5cef592e64bf83aa | EQUAL |
| card input docs/d1/ring-p6.md | bd2339fd3028aa761bb0fd93599cdc0c | bd2339fd3028aa761bb0fd93599cdc0c | EQUAL |
| card input tools/bench/graph_ring_p6_20261012_212645.json | fbc7b7eef540b87f8b935a10df2a02bd | fbc7b7eef540b87f8b935a10df2a02bd | EQUAL |
| card input tools/recipes/stage_replay_swap.py | 2bb111e296bf0f38967627483c517d68 | 2bb111e296bf0f38967627483c517d68 | EQUAL |
| card input tools/bench/plans/plan_replay_swap_110.json | 6b5ef7e5bba88eb79445132e06c91188 | 6b5ef7e5bba88eb79445132e06c91188 | EQUAL |
| card input tools/bench/m8b_replay_compare.py | ab7c1a68141862b91cf195670ae300d3 | ab7c1a68141862b91cf195670ae300d3 | EQUAL |
| card input tools/bench/diag_replay_standins.py | 8e6250b1ca8689c951bc667dca63b943 | 8e6250b1ca8689c951bc667dca63b943 | EQUAL |
| card input tools/bench/p6_replay_ready.md | ee2c7cb5bb54815f378b071d9331bd38 | ee2c7cb5bb54815f378b071d9331bd38 | EQUAL |
| card input tools/bench/drive_original_copy_v5.py | 3ea486d55f1dea6636ece97d31c8e9e4 | 3ea486d55f1dea6636ece97d31c8e9e4 | EQUAL |
| card input tools/stagekit.py | 22967183e5aee50fa9a43e8b4a7657e7 | 22967183e5aee50fa9a43e8b4a7657e7 | EQUAL |
| card input docs/script-writing.md | f5fd847a8621a26d58c0b40a85fad5a2 | f5fd847a8621a26d58c0b40a85fad5a2 | EQUAL |
| VI D1_ring_p6_20261012_212645.vi | c2d9c13c | c2d9c13cb40c0a5cab7433896d1df157 | EQUAL |
| VI D1_ring_p5_20261010_172913.vi | 75773b0d | 75773b0ded2a08586bb1a542ddda5af6 | EQUAL |
| VI D1_ring_p5s01_20261009_124542.vi | 7f2582ae | 7f2582ae54dc5bc42c3df0bdf3c72d2e | EQUAL |
| VI D1_s1_copy.vi | 3e3d23ce | 3e3d23cefd3a334001aa9d6156bf1aee | EQUAL |
| VI replay\D1_s1_replay_20260925_075422.vi | 126f8497 | 126f84975fca9f6124432a7e4decd0c8 | EQUAL |
| VI replay\replay_get_buff_image.vi | 842ecad9 | 842ecad9a6674a5060ebb3d5522751a9 | EQUAL |
| VI replay\replay_get_image_cal.vi | afce0d04 | afce0d04346fc58234d28bcc0fc42e55 | EQUAL |
| VI replay\replay_imaqdx_get_image_buf.vi | a89dafc1 | a89dafc1db03feef7b528f0dd4fcc692 | EQUAL |
| frames dir file count | 10045 | 10045 | EQUAL |
| frames_manifest.json (in dir) | f9032ae5510e96126d9f53fc92f69cfe | f9032ae5510e96126d9f53fc92f69cfe | EQUAL |
| frames md5 vs frames_manifest.json per-frame md5 | 0 differ | 0 differ | EQUAL |
| manifest md5 (p6_replay_frames_manifest.txt) | none pinned (new file) | 9055d98a15a4c9c2fd4e03de7ac41bb3 | EQUAL |

## F1 - FACT

#6810 (S1 callee 'get buff image-lost frames.vi', docs/wiki/subvi/D1_s1_copy.json:89810) and #22692 (S1 callee 'IMAQdx Get Image.vi') are SubVI nodes in P6 by uid with the same terminal names as S1; the P6 graph stores no SubVI names, so the P6 callee is NOT-DETERMINED by name. #6810 sits directly on d639 of While #637 (loop 1.1, no Case): one call per 1.1 iteration in P6 and in S1. S1: tracker #5058 is on the same d639 and its 'Image In' is #6810's 'Image Out' wire -> 1 call per tracked frame. P6: #5058 is on d23166 of While #10170 (loop 1.2), 'Image In' from #29843 IndexArray (ring slot read): #6810 runs every 1.1 iteration whether or not 1.2 reads that frame, so calls per tracked frame = 1.1 iterations / 1.2 tracked reads (>= 1), a run-time number the graph cannot give. #22692 is under For #22433 / Sequence #21590 / For #21305 in the calibration flat-sequence frames (session path to d26117 'CamSessionOut'), no While: 0 calls per tracked frame in P6 and S1 (identical terminals and partners); calls per calibration = the two For counts, unread.

- part present_by_uid: FACT
- part callee_name_in_P6: NOT-DETERMINED (the P6 graph has no graph_summary.subvi_calls; same uid + same terminal names as S1 only)
- part calls_per_tracked_frame_P6: NOT-DETERMINED (run-time ratio of 1.1 to 1.2 iterations)
- cite: docs/wiki/subvi/D1_s1_copy.json:89810
- cite: docs/wiki/subvi/D1_s1_copy.json:90152
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=6876]
- cite: docs/wiki/subvi/D1_s1_copy.json:35985
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=5089]
- cite: docs/wiki/subvi/D1_s1_copy.json:35645
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=22722]
- cite: docs/wiki/subvi/D1_s1_copy.json:57535

## F2 - EVERY

New frame in P6 = Case #22694 frame 'False' (d27219), selector #26879 'x = y?' with x = #6810 'current image number' and y = the previous iteration's value (LSR #27056 <- RSR #27039 on the same wire); d27219 holds the P3a counter #27311 'x+1' (ring write). replay_get_buff_image.vi (842ecad9) = get-buff copy with #529 swapped to the buf stand-in, wire edges unchanged; in it 'Buffer Number In' = the 'Buffer to extract' input and 'Buffer Number Out' = the 'current image number' output, and the stand-in wires BN Out = BN In. In P6 1.1, 'Buffer to extract' = LSR #5351 <- RSR #1117 <- #1978 'x+1', #1978 'x' = #1034 (one frame carries #6810 'current image number', the other 'Buffer to extract'). Under the stand-in both frames give current(i+1) = current(i) + 1, so x != y on every 1.1 iteration and EVERY stand-in frame is classed new and counted (first iteration: constant #27095 vs the start value, both unread). Whether 1.2 then tracks every ring frame is a run-time count (F3), not shown by the graph.

- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=27161]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=27154]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=6897]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=6876]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=2037]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=27315]
- cite: docs/wiki/subvi/get buff image-lost frames.json:212
- cite: docs/wiki/subvi/get buff image-lost frames.json:132
- cite: tools/bench/stage_d1_ring_p3a.json:119
- cite: tools/bench/stage_d1_ring_p3a.json:136
- cite: tools/bench/stage_d1_ring_p3a.json:140
- cite: tools/bench/diag_replay_standins.py:9
- cite: tools/bench/stage_replay_78.log:81
- cite: tools/bench/stage_replay_78.log:93

## F3 - {"discards": "NOT READABLE", "lost": "READABLE"}

Ring discards: #29724 'next discards' -> RSR #29648 only; its outer face (loop exit) is unwired; LSR #29655 (start constant #29662) -> #29724 'discards' only; no indicator, local, or file carries it (no other terminal named 'discard'). A leg cannot read it: NOT READABLE. Per RingSeqCheck's accepted arithmetic the count rises only on an invalid read (valid = n1==n2 AND n1>last), so a frame overwritten before 1.2 reads it (n1 > last+1, still valid) is not counted. S1 lost frames: indicator 'Total Lost Frames' on d3292 (Case #3191 in loop 1.1, fed by #3162 'x-y'), present in P6 too; the v5 leg reads it by label once at the end of RUN_S, before the stop, into the L11 detail -> drive_m8 'total_lost_frames' -> leg.json 'lost' (110-7: '0' both legs): READABLE. No saved file carrying it was found (save trace.vi #376 has no lost-frames input).

- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=29903]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=29952]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=29663]
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=29671]
- cite: docs/d1/ring-p4b.md:140
- cite: docs/d1/ring-p4b.md:141
- cite: tools/bench/graph_ring_p6_20261012_212645.json terminals[term_uid=4195]
- cite: docs/wiki/subvi/D1_s1_copy.json:35325
- cite: tools/bench/drive_original_copy_v2.py:132
- cite: tools/bench/drive_original_copy_v5.py:497
- cite: tools/bench/drive_original_copy_v5.py:506
- cite: tools/bench/drive_m8.py:113
- cite: tools/bench/drive_m8.py:128
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:437
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json:469

## F4 - FACT (layout + offset/length rule); NOT-DETERMINED (values of #26136, #26145)

Card 170-a2-2 (from the F4 read of card 170-a2-1 and the offline decoder run `tools/bench/diag_c170_a2_2_cal.log`, 6 pass / 0 fail, :65).

- **Layout - FACT.** ClusterConstant #26159 'input cluster' = 9 elements, in order (0-based): 0 'x,y pos array' Array2D<DBL>; 1 'cal image array' Array3D<DBL>; 2 '# slices in stack' I32; 3 'bandpass/forget array' Array2D<I32>; 4 'obj step between slices' DBL; 5 '# avg per slice' I32; **6 'Date and time' String**; 7 'exp/ref array' Array1D<I32>; 8 'Pixel distance' DBL (`diag_c170_a2_1_f4.log:13`; decoder `diag_c170_a2_2_cal.log:4-25`, D2 PASS :25). Bundled by NamedBundler #26446, whose 'output cluster' type equals #26159's (canon + label-exact signature, `diag_c170_a2_1_f4.log:17`); its 'Date and time' input t26470 is a String (:11,18).
- **Write call - FACT.** #26615 ReadWriteFile 'data' <- #26446; 'prepend array or string size? (T)' and 'byte order' unwired = defaults (big-endian, size-prefixed) (graph cites below).
- **Position RULE - FACT.** Walk the flattened cluster from byte 0: an array = one I32 per dimension, then the elements; I32 = 4 B; DBL = 8 B; String = I32 length N + N bytes. The 'Date and time' field starts right after elements 0-5 and is I32 N + N text bytes (field length 4 + N). Offset and length are therefore READ FROM THE FILE by this walk, not constant (elements 0, 1, 3 are run-sized arrays). Code: `walk()` in `tools/bench/diag_c170_a2_1_cal.py:79-113` (self-test :116-119), driven at :173 with the TD list from `gscript.parse_type_descriptors`.
- **Text source - FACT (graph).** #26428 'concatenated string' has FOUR inputs: #26411 'date string' (t26433), #26136 (t26436), #26411 'time string' (t26439), #26136 again (t26442; wire 26707 has 2 sinks) (`docs/wiki/subvi/D1_s1_copy.json:66445-66492`, `:83531-83588`). So text = date + C + time + C, C = value of FixedConstant #26136 (a String, `diag_c170_a2_1_f4.log:15`). (Earlier text named three inputs; the fourth is the second #26136 sink.)
- **Formats.** #26126 'want seconds?' = TRUE, read (`diag_c170_a2_1_f4.log:19-20`) - FACT. #26136 (FixedConstant, String) and #26145 (EnumConstant 'date format (0)', items short/long/abbreviated) values: **NOT READ by an existing op** - OpConstValue_v1 gave a void variant, OpConstValueRing_v0 error 1055 (`diag_c170_a2_1_f4.log:14,21-24`) - NOT-DETERMINED.
- **OBSERVED text** (both stored cal001 of 110-7, cp949): `2026년 9월 27일 일요일` + 0x0D + `오후 6:51:02` (A) / `오후 7:02:38` (B) + 0x0D, 36 text bytes. Split as observed: date (year 년, month 월, day 일, weekday) | 0x0D | time (오후 = PM marker, h:mm:ss, 12-hour) | 0x0D. Consistent with C = "\r" for #26136, but that value is OBSERVED, not read. Which enum item produced the date form is not determined.
- **Per-file, 110-7 - FACT.** Leg A `tools/bench/m8_out/replay_s1_20260927_184651/cal001` (md5 e5570a96): walk consumes 857376 of 857376 B; field offset 857264, length 40 (4 + 36); text offset 857268 (`diag_c170_a2_2_cal.log:35,42,45`). Leg B `tools/bench/m8_out/replay_s1_20260927_185846/cal001` (md5 ea1ed8a3): same size, same offset 857264, same length 40 (:50,57,60). Bytes before and after the field identical A vs B; the whole files differ in 5 bytes, all inside the time text (6:51:02 vs 7:02:38) (:64). Run-sized arrays this run: x,y pos [15,2], cal image [15,60,119], bandpass/forget [15,3], exp/ref [15] (:36-44).
- **Gate H of card 170-a2-1 - FACT.** Handles 57984 -> 51489 (a FALL of 6495, not growth), gscript refs opened 2 closed 2 live 0 (`diag_c170_a2_1_f4.log:25-26`); the FAIL came from the gate's abs(delta) <= 100 criterion (`diag_c170_a2_1_f4.py:140`). Growth is the leak signal; no leak is shown.

- cite: tools/bench/diag_c170_a2_1_f4.log:13
- cite: tools/bench/diag_c170_a2_1_f4.log:17
- cite: tools/bench/diag_c170_a2_1_f4.log:19
- cite: tools/bench/diag_c170_a2_1_f4.log:21
- cite: tools/bench/diag_c170_a2_1_f4.log:24
- cite: tools/bench/diag_c170_a2_1_f4.log:25
- cite: tools/bench/diag_c170_a2_2_cal.log:45
- cite: tools/bench/diag_c170_a2_2_cal.log:60
- cite: tools/bench/diag_c170_a2_2_cal.log:64
- cite: tools/bench/diag_c170_a2_1_cal.py:79
- cite: docs/wiki/subvi/D1_s1_copy.json:66485
- cite: docs/wiki/subvi/D1_s1_copy.json:83531
- cite: docs/wiki/subvi/D1_s1_copy.json:66315
- cite: docs/wiki/subvi/D1_s1_copy.json:66415
- cite: docs/wiki/subvi/D1_s1_copy.json:66445
- cite: docs/wiki/subvi/D1_s1_copy.json:66505
- cite: docs/wiki/subvi/D1_s1_copy.json:66495
- cite: docs/wiki/subvi/D1_s1_copy.json:66535
- cite: docs/wiki/subvi/D1_s1_copy.json:66515
- cite: docs/wiki/subvi/D1_s1_copy.json:66345
- cite: docs/wiki/subvi/D1_s1_copy.json:66275
- cite: docs/wiki/subvi/D1_s1_copy.json:66305

## F5 - FACT

VI-written, in run_dir tools/bench/m8_out/replay_s1_<ts>/: the cal file (save dialog of #26615, path typed under run_dir) and tra*; in the 110-7 replay legs exactly cal001 (857376 B) + tra001-000 (A 1706560 B, B 3282880 B), TIFFs 0. Driver-written: the run copy <src>_run_<ts>.vi beside the replay VIs (deleted by drive_m8 at end), m8_v5_replay_s1_p<N>_r<S>.json, its _clicks.json, m8_replay_s1_p<N>_r<S>.json, screenshots in tools/bench/m8_shots, leg.json in the leg's --out dir. v5 cleanup deletes only *.tif/*.tiff in run_dir (none in 110-7); cal and tra are kept. What the P6 copy writes is NOT measured until a P6 leg runs.

- cite: tools/bench/drive_m8.py:75
- cite: tools/bench/drive_original_copy_v5.py:78
- cite: tools/bench/drive_m8.py:72
- cite: tools/bench/drive_m8.py:123
- cite: tools/bench/drive_m8.py:82
- cite: tools/bench/drive_m8.py:83
- cite: tools/bench/drive_m8.py:78
- cite: tools/bench/drive_m8.py:136
- cite: tools/bench/diag_c104_leg.py:176
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:673
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:674
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:678
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json:703
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/B_dispreplay_a1/leg.json:704
- cite: tools/bench/drive_original_copy_v5.py:688
- cite: tools/bench/drive_original_copy_v2.py:418

## F6 - FACT

X5 plan literal: stage_replay_swap.py loads only PLANS {78, 95, 110}, picked by --plan <tag>; a P6 plan needs a new entry there (a recipe edit). X6/X7 driver pins: drive_m8_replay_110.py hard-codes leg A (S1 replay copy 126f8497) and takes leg B's md5 only from stage_replay_swap_110.json copies.disp; --disp <path> takes leg B's path; it writes card '110-7' and an INDEX row naming the display-loop VI. X8 leg kind: diag_c104_leg.py takes --src <any vi> --picks N --run-s S --out <dir> and always runs drive_m8 --leg replay_s1, so both legs write m8_replay_s1_p<N>_r<S>.json (leg.json in --out keeps each); drive_m8 accepts replay_s1/replay_s3 and reads the md5 from --src itself. X9: drive_m8 M7 needs BED/S3/ORIG/S1 + src md5 unchanged. Run length: --run-s seconds only (diag_c104_leg -> drive_m8 -> v5.RUN_S); NO frame-count parameter exists; the stand-in serves paths[k mod 10044] (110-7 leg A: frames_delta 4081 in 120 s). Compare: m8b_replay_compare.main(dir_a, dir_b, out). v5 runs motor_gate --session start itself and never --session end. The shared pieces that take a P6 copy as a parameter today: diag_c104_leg --src, drive_m8 --src, m8b_replay_compare.main; the 110 wrapper's pins and the PLANS literal do not.

- cite: tools/recipes/stage_replay_swap.py:22
- cite: tools/recipes/stage_replay_swap.py:24
- cite: tools/bench/drive_m8_replay_110.py:19
- cite: tools/bench/drive_m8_replay_110.py:20
- cite: tools/bench/drive_m8_replay_110.py:21
- cite: tools/bench/drive_m8_replay_110.py:22
- cite: tools/bench/drive_m8_replay_110.py:41
- cite: tools/bench/drive_m8_replay_110.py:80
- cite: tools/bench/drive_m8_replay_110.py:86
- cite: tools/bench/diag_c104_leg.py:22
- cite: tools/bench/diag_c104_leg.py:23
- cite: tools/bench/diag_c104_leg.py:33
- cite: tools/bench/diag_c104_leg.py:176
- cite: tools/bench/drive_m8.py:68
- cite: tools/bench/drive_m8.py:69
- cite: tools/bench/drive_m8.py:36
- cite: tools/bench/drive_m8.py:85
- cite: tools/bench/drive_m8.py:121
- cite: tools/bench/drive_original_copy_v5.py:52
- cite: tools/bench/m8b_replay_compare.py:31
- cite: tools/bench/diag_replay_standins.py:9
- cite: tools/bench/t0_legs/c110f_replay_20260927_184600/A_S1replay_a1/leg.json:438

HANDBACK-GATE: F2=EVERY F3=discard NOT READABLE; lost READABLE -> HANDBACK
