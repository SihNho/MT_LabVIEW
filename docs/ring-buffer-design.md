---
type: design
status: current
date: 2026-09-28
tags: [frame-handoff, loop-1.1, loop-1.2, user-decision]
supersedes: docs/d1-build-plan.md §9 (Q_free/Q_work pool queues only)
---
# Frame handoff 1.1 → 1.2: RING BUFFER, no queues (user design, 2026-09-28 16:3x)

Decided in the chat with the user after the pool/queue design (PD233–237) and a proposed rollback ("option C") were
both reconsidered. The user's own sketch, then four points agreed:

> IMAQbuff = array(20,1) … `[BufNum,IMAQcurrent] = Acquisition(IMAQcurrent); Idx=rem(BufNum/20); IMAQbuff(Idx)=Current`
> … tracking loop: `if i~=rem(BufNum/20); Track = TrackingAnalysis(IMAQbuff(i)); Save = saveAnalysis(BufNum, Track)`
> "1번 지적은 훌륭한 부분 / 2번 … 특정 프레임은 놓쳐버릴 수도 있으니까 / 3번 … 버퍼로 20 프레임이 있어도 문제가
> 생긴다면 최신 칸으로 움직이는게 맞음 / 4번 … 칸 번호는 카메라 루프를 쓸 수밖에 없지 않나?"

Tracking stays in its own loop 1.2 (the K / L2 chain and the 20 pool images of cycle 119 are KEPT). Only the two pool
QUEUES (`Q_free`, `Q_work`) are dropped. Rollback to D1_s4 is CANCELLED.

## Design
1. **Slots:** the 20 IMAQ images already created by the POOL stage (`Cam_pool00..19`, bed
   `claudeDev\D1_qrt_pool_20260928_141055.vi`). Slot index = the CAMERA LOOP's own counter k mod 20 (not BufNum mod
   20), so the camera acquires DIRECTLY into `Img(k mod 20)` — no extra copy.
2. **No corruption (seqlock):** per-slot number array `Num(20)`, init -1. Camera loop, per frame: `Num(i) = -1` (writing),
   acquire into `Img(i)`, store the frame-paired values (`#30117` Trans Pos, `#4580` Rot pos, frame index) in per-slot
   arrays, then `Num(i) = BufNum`, publish `Latest = BufNum`. Tracking loop: `n1 = Num(i)`, track `Img(i)`, `n2 = Num(i)`;
   the result is valid only if `n1 == n2 and n1 >= 0`; otherwise it is DISCARDED and counted as lost.
3. **Read order:** the tracking loop keeps `last` (last processed BufNum) and takes the slot holding the SMALLEST
   `Num > last`. Camera-side skips (BufNum jumps) are gaps, never re-reads.
4. **Overload:** in order while the 20 slots hold the backlog; when an overwrite is detected (seqlock mismatch, or the
   next wanted number is gone), JUMP TO THE NEWEST slot (`Latest`) — the user's rule "최신 칸으로 움직이는게 맞음".
5. **Transport:** `Num`, the per-slot value arrays and `Latest` cross loops as LOCAL variables (single writer = the
   camera loop; CLAUDE.md 1c''). The results 1.2 → 1.7 (file writer) stay a lossless FIFO queue.
6. The camera loop never waits on 1.2 (camera free-runs, 2026-09-15). Buffer Number Mode = Last is unchanged.

Rule 1a: the per-bead maths and its inputs are unchanged; each result carries its own frame's BufNum and values
(PD233(f)(1)(2) still hold, now through the per-slot arrays instead of Q_work).
