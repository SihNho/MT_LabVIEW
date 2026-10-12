---
card: 166-a1-5
status: current
date: 2026-10-12
---
# Brief 166-a1-5 (assignment 166-1) - P6 FACT CENSUS F1-F5, OFFLINE, FACTS ONLY

Plan: `docs/d1/ring-p5c.md:273-282` (PD403(e), binding). Cycle 167's judgement writes `docs/d1/ring-p6.md` from your output, so every row must carry its source (`file:line` or `json path`) and nothing may be a design, a verdict, or an inference stated as a measurement.
**Rule (violation-decisions 2026-10-12 inference-over-measurement):** a value you did not read in this card is written "unread assumption", not as a fact. Precedent: the P5 census `tools/bench/p5_facts.md` + `.json` (cycle 153, PD370(f); same layout) - read its head for the form.
Offline, no LabVIEW, no motor/camera, no VI is opened or saved. Reads only: stored graph reads, Error List reads, scratch logs, the plan docs, the code. Scripts: `docs/script-writing.md` (scope header, `RESULT` line, call shared functions such as `tools/vigraph.py`/`stagekit` readers rather than re-parsing graph json by hand; if no reader exists write one small one in a shared module with a self-test).

## Inputs you read
- The P5 final: `tools/bench/graph_ring_p5s02e_20261012_173009.json` (7815af09, read from 75773b0d by card 166-a1-1), its Error List read `tools/bench/errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json` (0c0664d8, 47 items) and the expected file `tools/bench/errorlist_expected_D1_ring_p5_20261010_172913.json` (c94be128, card 166-a1-2).
- S1 lineage: `tools/bench/graph_ring_p5s01_20261009_125622.json` and earlier graphs back to the original copy (`docs/d1/INDEX.md` lists them; the original VI is never opened).
- Plan texts named below: PD374(g), PD363, PD366(d), PD224(d) (grep `docs/d1/*.md` and `docs/d1-*.md`); user rules U8/U9/U11 (`docs/user-rules.md`); STATUS.md's 2026-09-28 overload note (the "USER RULE, re-confirmed 2026-09-28" line, STATUS.md ~line 131).

## The rows
- **F1 - the 47 items:** for each: class (loose end / not connected / Build Array / two types ...), object uid, owner and loop, the P-step/action that produced it (A-number and step) OR "present since <earlier bed>" (name the first graph/read where it appears), and for a "not connected" input what FED it in S1 (lineage back to the original copy). Use the per-step expected files (`errorlist_expected_D1_ring_p*`) and plans (`plan_ring_p5*.json`, ring-p4*) to date each item; where dating needs a read that does not exist, write "not dated: no read of <bed>".
- **F2 - PD374(g)'s carry:** every consumer of `#644` `i` and of `FrameIdx` in the P5 final graph: each row = consumer uid/class, what it computes, which loop, used as a counter or not (read the wire's sink node and its owner; quote the terminal/wire uids).
- **F3 - open P6 obligations measured on the P5-final graph:** (a) the item-6 void -> I32 mismatch (PD363): which item it is in the 47, what produces the void and what expects I32; (b) `#2626` input names versus S1 (PD366(d)): list each input name in the final graph and in S1, mark equal/different.
- **F4 - the overload path as built:** list the nodes in the P5 final that do jump-to-Latest, discard (queue flush / lossless FIFO read) and the counters (uid, class, owner, loop, what wires into/out of it), then LIST them against U8/U9/U11 and STATUS's 2026-09-28 overload note, one row per clause: "built as ..." with the evidence. Facts, **no verdict** (no "complies"/"violates").
- **F5 - replay / ABBA tools that exist:** path, input, what each compares: the PD224(d) recorded-frame replay, `tools/bench/drive_original_copy_v5.py`, the ABBA/diag tools (`grep -l "ABBA" tools tools/bench`), and the two steer_158 tests (frame-number gap; execution order with a test delay in loop 1.2: `tools/bench/cards/steer_158.json`, `docs/d1/runner.md`) - what exists, what is MISSING (a missing tool is a row "missing", not a plan).

## Outputs and end
`tools/bench/p6_facts.md` (human table per F, <= 400 lines is fine, each row cited) + `tools/bench/p6_facts.json` (same rows, machine-readable, with `source` per row) + the script(s) that produced them and their log. Quote in your result: item counts per F, rows marked "unread assumption" or "not dated", and the md5 of both outputs.
Hash the seven VIs before/after (unchanged; 75773b0d, 7f2582ae, eb1d0f31, 94ffff94, f9ae7751, 564d8cbe, 6dcd5c3d); no LabVIEW process. Do NOT edit STATUS, INDEX, the plan, any tools/*.py except a new small shared reader if truly needed (then self-test it). Concurrent card 166-a1-4 edits `tools/stagekit.py`: do not import-pin stagekit's md5 and do not edit it.
