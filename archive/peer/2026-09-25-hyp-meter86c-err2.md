# hyp-meter86c-err2

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.2032  in 20 / out 9542 / cache-create 99419 / cache-read 975020  (135s, 14 turn(s))
- **date:** 2026-09-25 23:15:44
- **outcome:** ANSWERED (138s)
- **verdict-card:** VERDICT-CARD hyp-meter86c-err2 verdict=unverified -> tools\bench\cards\verdict_hyp-meter86c-err2.json
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

--- REVIEW CARD (review/1, id hyp-meter86c-err2, role hypothesis) ---
CLAIM: LabVIEW error 2 after op 41 (act 45) in the full replay is caused by memory accumulated by ~41 whole-VI GObject traverse reads (OpReportAll_v0), not by act 45's wire itself.
PREDICTED: after op 41 the uid read-back shows the wire on #6007 with sole source #6007 (owner #5680) and sole sink #5082 on #5058
OBSERVED: meter_l2a1_86c.log:682-686: op 41 wire_tunouter err '' at 695.0 MB; the next whole-VI read raised error 2 (Traverse for GObjects, OpReportAll_v0); read-back empty (log:734); ops 1-40 diff 0; reads summed +140.4 MB vs edits +1.7 MB (log:730)
ALREADY RULED OUT: plan/sim divergence: 41 per-op diffs all 0 (log:733)
ALREADY RULED OUT: op 41 edit error: returned err '' and node census 635->635 (log:682-684)
ATTACHMENT: tools/bench/meter_l2a1_86c.log (md5 None)
ATTACHMENT: tools/bench/meter_l2a1_86c.py (md5 None)
ATTACHMENT: tools/stagexec.py (md5 None)
ATTACHMENT: archive/peer/2026-09-25-hyp-unroutable-err2-85.md (md5 None)
--- END REVIEW CARD ---

FAILED PREDICTION, card 86-2: tools/bench/meter_l2a1_86c.py, log tools/bench/meter_l2a1_86c.log (one run, 1236 s).

Test: fresh LabVIEW (process absent before launch), D1_k scratch, the full plan_l2a1 executor replay (42 ops / 46 acts)
with the stagexec.Meter in warn-only mode, plus a READ-ONLY uid read-back of the new wire hooked onto the executor's own
whole-VI read right after op 41 (act 45, rw_6007_5082) and op 42 (act 46, rw_6026_5164).

Prediction (gates R41/R42): after op 41 the wire on #6007 has sole source #6007 (owner SelectorTunnel #5680) and sole
sink #5082 on SubVI #5058; same for #6026 -> #5164 after op 42.
Observed: ops 1-40 each diff 0 vs their step file (log:40-679). Op 41's edit itself returned OK: "OP wire_tunouter
SelectorTunnel[11] #5680 -> SubVI[17].t0 -> err ''" (log:682), node census 635 -> 635 (log:684), meter op k41 695.0 MB,
handles 46171 (log:685). The whole-VI read right after it (OpReportAll_v0, Traverse for GObjects) raised LabVIEW error 2
(log:686). So the read-back had no data: R41/R42 = {} (log:734-735). Op 42 never ran.
Memory (private bytes): 570.7 MB after load -> 694.9 MB after op 40's read; sum of d_mb at the edit calls +1.7 MB, sum at
the whole-VI reads +140.4 MB (log:689-730, METER SUMMARY log:730). Handles 45,889 -> 46,171, flat-ish.
Prior: run 85 (unroutable_l2a1_85.py) died at act 45 with error 2 too (unroutable_l2a1_85.log:562); com-driving.md:310-312
records error 2 near ~770 MB private bytes. Here it came at 695 MB.

My explanation: error 2 ("memory full") is triggered by the whole-VI GObject traverse report (OpReportAll_v0) once
LabVIEW's private bytes have grown ~125 MB through ~41 such reads on this 635-node VI - i.e. the per-op READ, not the
edit, accumulates memory, and the failure point is a read-count/memory threshold, not something specific to act 45.
Competing explanation: act 45's wire itself (tunnel outer face -> SubVI t0) leaves the diagram in a state that makes the
next GObject traverse fail (e.g. a wire LabVIEW cannot report), and memory is incidental - 85 also died at exactly act 45.

Questions: (1) which explanation do the numbers support; what single run separates them cheapest (e.g. act 45 after
ops[:22] only, where memory is ~635 MB, or ops 1-40 with the reads thinned)? (2) is 695 MB vs 770 MB consistent with a
memory ceiling at all? (3) anything in stagexec LVBackend.read / OpReportAll_v0 usage that leaks per call?
Files: tools/bench/meter_l2a1_86c.log, tools/bench/meter_l2a1_86c.py, tools/stagexec.py (Executor.run ~811-922,
LVBackend.read ~1063), archive/peer/2026-09-25-hyp-unroutable-err2-85.md, archive/peer/2026-09-25-hyp-meter86b-prefix.md.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

--- VERDICT CONTRACT (session protocol v1, C5; mandatory) ---
Write your answer as usual. Then make the LAST line of your answer exactly one line of the form
VERDICT {"schema":"verdict/1","id":"hyp-meter86c-err2","verdict":"<one of: refuted | supported | unverified>","alternative":"...","discriminating_test":"...","violations":[],"sources":["url or file:line"],"note":""}
Single-line JSON, no code fence. alternative/discriminating_test/note <= 300 chars each; violations <= 2 items {"slug","loss_min","loss_usd","evidence"} using the retrospective slug list. Gates read ONLY this line; the prose above it is archived for people.


## Answer

**Verdict: unverified, and I lean against the claim.** The meter shows memory growing during the reads. It does not show that memory caused error 2. The timing points at act 45's wire at least as strongly.

## 1. Strongest reason the claim is wrong: the ceiling it needs is a knife edge
- **The previous read passed at almost the same memory.** The read after op 40 started at 690.9 MB, ran to completion and finished at 694.9 MB (`meter_l2a1_86c.log:677-678`). Op 41 added only +0.1 MB (`:685`). The read that failed started at 695.0 MB (`:686-687`). For the memory claim to hold, the limit has to sit inside that last read's ~4 MB of growth.
- **Nothing shows the process nearing a limit.** Memory grows in a steady line, about 3.4 MB per read. Reads do not slow down: GObject reads take 8.83 s at the start and 8.95 s at the end (`:730`). 695 MB is small for a 64-bit process. The only earlier error-2 figure is about 770 MB (`com-driving.md:310-311`), which is 75 MB higher, so there is no fixed ceiling here.
- **The failure lands on the one new step, twice.** In both 85 and 86c, error 2 came on the first read after `wire_tunouter`, the only step type never run in sequence before. Every other step type had already passed dozens of reads (`log:40-679`, `unroutable_l2a1_85.log:558-562`).
- **Caveat: "85 also died at act 45" cannot decide this on its own.** The replay is deterministic, so a memory threshold would also land on the same act every time. One detail weakly favours act 45: 85 started from a different process state, with 33,997 handles against 45,652 here, and still failed at the same act. But 85 had no private-bytes meter.
- **Reads have not been shown to leak.** `OpReportAll_v0` has no Close Reference (`docs/REFERENCES.md:158`). However, the traverse-only arm was measured flat, −0.1 MB over 20 calls (`REFERENCES.md:211`).
  - The steps of 4.0–4.1 MB, alternating with 0.1 MB (`log:689-728`), look like the memory allocator growing in chunks. They do not look like a per-object leak.
  - The +140.4 MB figure says only when memory grew, not that it is retained (`:730`).
  - Each read also includes a terminals pass of about 11.7 s. So the growth cannot be pinned on the GObject traverse.
  - **Answer to your question (3):** the leak exists by construction, but it has not been measured as the cause of this growth.

## 2. Alternative explanation
The act-45 wire, from the SelectorTunnel #5680 outer face to SubVI #5082 on the same diagram 23166, leaves an object or state that `Traverse for GObjects` cannot walk. LabVIEW then reports that failure as error 2, which also covers failures other than RAM running out ([NI KB](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU), [LAVA: "Error 2: memory is full – but it isn't"](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/)).

The node census stays at 635 (`:684`), but the wire's sink was never read back, so "err ''" only means the op returned without error.

## 3. What would falsify each side
- **Falsifies the claim:** act 45 on the full step_44 graph at low memory (about 580 MB), followed by one read, gives error 2.
- **Falsifies the alternative:** the same act-45 read comes back clean with sink #5082, and error 2 appears in a no-edit read loop at about 42 reads / 695 MB.

**Answer to your question (2):** 695 MB against 770 MB fits a threshold that depends on the process's state, or it fits no memory ceiling at all. It does not fit a fixed ceiling.

## 4. Cheapest discriminating test (about 5 minutes instead of 20)
1. Start a fresh LabVIEW. Replay ops 1–40 **with the per-op whole-VI reads skipped**, then do one read at the end and check it against step_44 (diff 0). Memory should be about 580 MB.
2. Run op 41 (act 45).
3. Do one read plus the R41 uid read-back.

How to read the result:
- **Error 2 at about 580 MB:** act 45 is the cause.
- **Clean, sink #5082:** the cause is reads or accumulated memory. Only then run the second leg: a no-edit loop of `report_all(GObject)` plus the terminals pass on that graph, logging private bytes on every call.

`Executor.run` diffs after every op (`stagexec.py:902`), so skipping the reads needs a thin driver over `ex.ops[:40]`. That is also why this test answers the gap the 86b review left: it runs act 45 on the full 44-act graph, not on the 22-op prefix (`archive/peer/2026-09-25-hyp-meter86b-prefix.md:100-106`).

Sources: [NI KB, error 2 on opening references](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU) · [LAVA, error 2 not from memory](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/) · [NI, Traverse for GObjects VI](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/vi-lib/utility/traverseref-llb/traverse-for-gobjects-vi.html)

VERDICT {"schema":"verdict/1","id":"hyp-meter86c-err2","verdict":"unverified","alternative":"Act 45's tunnel-outer-face->SubVI wire leaves a state Traverse for GObjects cannot walk, reported as error 2 (not only memory-full); prior read k40 ran fine 690.9->694.9 MB, op41 added +0.1 MB, and 85/86c both failed on the first read after the only novel op","discriminating_test":"Fresh LV: replay ops 1-40 with per-op reads skipped (one step_44 check at ~580 MB), then op 41 + one read + R41 uid read-back. Error 2 => act 45; clean with sink #5082 => then no-edit report_all(GObject)+terminals loop to find the read/memory threshold","violations":[],"sources":["tools/bench/meter_l2a1_86c.log:677-687","tools/bench/meter_l2a1_86c.log:730","docs/REFERENCES.md:158","docs/REFERENCES.md:211",".claude/skills/labview-automation/references/com-driving.md:310-311","tools/bench/unroutable_l2a1_85.log:558-562","https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/","https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU"],"note":"Deterministic replay means 'same act twice' alone cannot discriminate; per-read MB growth is timing attribution, not a proven retained leak (traverse-only arm was flat)."}

## Sources

(extract from answer)

## What was done with it

Card 86-2 (material session, 2026-09-25 23:2x): verdict `unverified` recorded; per card rule "review owed -> hypothesis
review then stop" NO further LabVIEW run was made. The review's discriminating test (ops 1-40 with per-op reads skipped,
one step_44 check, then op 41 + one read + R41 read-back, fresh LabVIEW, ~5 min) is handed to the judgement session as an
OPEN item in `tools/bench/cards/result_86-2.json`; nothing was built for it. No change to stagexec.py or OpReportAll_v0.
