# Brief chat-PI1 — block-diagram crops for the PI (user 2026-10-16)

User (chat): PI asked to see the real code; "다이어그램 패널의 1) 원본 메인 vi 2) 수정 (하네스 교체 전) vi 3) 현재 구조 vi
핵심 부분을 찍어서 (전체를 보여주지 마. 어차피 너무 작은 건 보지도 못함)"; then "지금 랩뷰 프리함 사용하도록".
The lean runner is STOPPED (STOP file present) - do NOT restart it. No hardware: no camera, motors, ASI; never Run a VI.

## Goal
Readable PNG images of the KEY PART of the block diagram of three VIs, not the whole diagram. Native pixel scale (no
downscaling); each final crop ideally <= ~1800 x 1100 px; split a large region into two crops rather than shrinking.

## Sources (open BYTE COPIES only, in claudeDev\shots_20261016\; md5 of the sources before and after must match)
1. ORIGINAL `G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` md5 2f048e3a18de3b5e3ca8368f6a24dae0
2. P6-1 (before the harness swap) `claudeDev\D1_ring_p6_20261012_212645.vi` md5 c2d9c13cb40c0a5cab7433896d1df157
3. CURRENT `claudeDev\bench\lean\D1_ring_p6latest_20261014_010104.vi` md5 15c664e3eed1c580e05b13e42c86566f
If a copy opens with missing subVIs, still capture (the diagram draws) and note it.

## How
No Op VI captures images yet. Build ONE new Op VI `claudeDev\OpGetImage_v0.vi` (same conventions as the other Op*.vi,
driven from Python through tools/gscript.py / tools/kb_com.py): VI path + object UID + PNG path in; GObject reference ->
VI Scripting method **Get Image** -> `Write PNG File.vi`. FIRST verify from LabVIEW itself that the method exists and
its inputs (image depth etc.); if it is not on GObject, find the right class and report it. Record each object's Bounds
and crop with PIL to the listed nodes + ~40 px padding. GUI screenshots only if scripting is VERIFIED unreachable
(lv_gui.ps1 exception path) - that is a RETURN, not a workaround, under this card (gui: false).

## What (confirm each UID by reading the diagram first)
- A. ORIGINAL frame loop = While "B" (diagram 43, docs/frame-loop-anatomy.md): camera buffer -> image copy -> tracking
  kernel -> plots / saving, all in ONE loop one after another. Include uid 6810, 22700, 5058 and nearby save / plot
  calls. One or two crops (`A1_original_frame_loop.png`, `A2_...`).
- B. P6-1: loop 1.2 = While #10170, body d23166, ring READER: seqlock reads n1 / n2 and the Local reads BufDiff #30294,
  TransPos #30116, RotPos #30215, FrameIdx #30239 + IndexArrays (#30300 ...), OUTSIDE the seqlock here
  (`..\V6_lean\tools\bench\lean_bench\lean_report_p6fix.md` sections 1-2). `B_p6-1_reader_before_fix.png`.
- C. CURRENT: the same region after the fix (Locals between n1 and n2). Same crop size as B if the layout allows.
  `C_current_reader_after_fix.png`.
- D. CURRENT: loop 1.1 ring WRITER, Flat Sequence #27509 (frames d27641 | d32464 | d27722). `D_current_writer_loop11.png`.
- E (optional, only if readable): CURRENT, loops 1.1 / 1.2 / 1.7 side by side. `E_...png`.

## Output
`tools/bench/pi_shots_20261016/`: the crops above, `raw_*.png` (uncropped Get Image per structure), `shots.json`
(file, source VI + md5, uid, bounds, crop box, pixel size, one-line description). Close copies WITHOUT saving, close
LabVIEW and verify it is gone, set/clear `labview-lock`, one history line in STATUS.md. Commit nothing.
Result card `tools/bench/cards/result_chat-PI1.json` (result/1).
