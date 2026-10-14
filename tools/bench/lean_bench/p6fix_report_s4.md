
## 4. The fixed VI and its test copies (all under `claudeDev\bench\lean\`, built by `p6fix_build.py` run 5, 85/0)
| file | md5 | what it is |
|---|---|---|
| **`D1_ring_p6fix_20261013_231910.vi`** | **3e847397eb120860adb2e868792345f7** | **the fixed P6** (byte copy of the bed c2d9c13c + the one edit below) |
| `D1_ring_p6fix_replay_20261013_231910.vi` | ae83d1aa088ba4546c65e039c6b4d16d | fixed P6 + plan 170's swaps: #6810 -> `replay_get_buff_image_paced60.vi` (new uid 31710), #22692 -> `replay_get_image_cal.vi` (new uid 6829) |
| `D1_ring_p6fix_replay_gap_20261013_231910.vi` | 2c499c7ba1a38c813d784efe7eacee76 | replay copy + #31710 -> P6-3's gap wrapper `gap_get_buff_image_paced60_20261013_161639.vi` (a885a8fb) |
| `D1_ring_p6fix_replay_w40_20261013_231910.vi` | db5e2e958201df1f1de928558aeff3ac | replay copy + RingSeqCheck #29724 -> P6-3's `RingSeqCheck_w40_20261013_161639.vi` (581e2953) |
| `D1_ring_p6fix_replay_w100_20261013_231910.vi` | ae8474bc8b33506c3659af407c2e7696 | replay copy + RingSeqCheck #29724 -> P6-3's `RingSeqCheck_w100_20261013_161639.vi` (429cdc5d) |

**The exact change in the fixed P6** (route: structure method + node MOVE + Remove Bad Wires + Terminal.Connect Wire; no node was copied
into the VI, so P6-3's copy breakage did not arise):
1. Flat Sequence #29721 `Add Frame` before its only frame: frames are now **[d31550 (new), d29869 (n2 read, unchanged)]** (warm F4, cold CF).
2. The 8 nodes Local BufDiff #30294, TransPos #30116, RotPos #30215, FrameIdx #30239 and IndexArray #30300, #30119, #30216,
   #30240 moved into d31550 (uids kept; F6 warm, CO cold). OpMoveIn leaves one unwired junk Invoke per call: the 8 were deleted (F6b).
3. Wires re-made (14 + 1, all `broken False`, no op error): Local -> IndexArray `array` x4 (inside d31550); `min slot` (pick loop
   tunnel #30179) -> new input tunnel #28684 of d31550 -> the 4 `index`; each `element` -> a new output tunnel of d31550 (#30270,
   #31529, #31634, #31692) -> its old sinks (BuildArray #2626 x3, Q&R #10068 / #29240 `x`, For Loop #1359 `Magnet position`).
4. One side effect, handled and gated: For Loop #1359's input tunnel #9503 (TransPos -> `Magnet position` #28083) lost both its
   wires in the move + Remove Bad Wires and LabVIEW deleted it; the TransPos element is wired to `Magnet position` again through a
   NEW For Loop tunnel #31600 (scalar, plain tunnel, as #9503 was).
- Gates: ExecState 1 warm (F12) and cold (C1); callee census unchanged (F13); **edge set with the new tunnels (and the gone #9503)
  collapsed as pass-throughs == the bed's, warm (F14, 2425 edges, +0/-0) and cold (CE vs the bed read cold in a fresh LabVIEW:
  +0/-0)**; no new object other than the 6 tunnels (F12b); md5 unchanged by the cold load (C2). So the data edges are exactly the
  bed's; only the owner (the new frame) of the 8 nodes changed, plus the tunnels the boundary needs.
- Test copies: each `replace_object` swap: callee diff == exactly the swap(s), wire-edge diff 0 after the uid remap (2431 edges),
  ExecState 1 warm and cold, cold edges == the source's cold edges, md5 unchanged by the cold load.
- Every pinned input unchanged during the build (Stage pins BEFORE/AFTER, H2/H3); LabVIEW gone at the end (H9).
