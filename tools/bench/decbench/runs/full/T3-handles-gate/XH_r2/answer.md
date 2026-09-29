**The saved VI is not defective. The failure comes from the card's gate: L4 applied the ±100 handle limit to an editing stage, and a project ruling already says that limit does not apply there.**

**Evidence**
- **The ruling.** Pre-decided 176(a) says the ±100 limit is "the reference-hygiene test for REPEATED OP CALLS … It does not apply to an editing stage: a stage that creates objects holds more handles while the VI is open. For editing stages the handle numbers are RECORDED, not gated" (`docs/d1-loop12-17-split-plan.md:458-461`). CLAUDE.md gives the same scope: 20 calls of one op must leave the count flat (`CLAUDE.md:224-225`, `:514`). Card 119-4 put the gate back anyway (`tools/bench/cards/task_119-4.json:32`). Earlier recipes only record the number (`tools/recipes/stage_d1_l7_r.py:112`).
- **Why R2 passed and this stage did not.** R2's operations barely changed the count; its largest step was +20 (`tools/bench/stage_d1_l2r2.log:48-267`), so its ±100 check passed (`:299`). This pool stage creates a For loop, an IMAQ Create subVI, three queue nodes, constants and 7 wires (`stage_d1_qrt_pool.log:45-151`, `:226`).
- **The growth pattern is one-time, not per call.** The first call of each op kind grows the count and repeat calls stay flat:
  - donor create: +79, then +0 (`:78`, `:87`)
  - Obtain Queue: +27, then +2 (`:115`, `:134`)
  - wire_const: +33, then +1, then +0 (`:160`, `:168`, `:197`)
  
  A per-call reference leak would add the same amount on every repeat.
- **The saved file cannot carry a leak.** A .vi on disk holds no open references. Every check on the file passed: the computation diff, the wires, and the Error List (`:226-231`; `result_119-4.json:24`). References opened and closed were 9/9 (`:245-246`).
- **Closing the VI released the handles.** The count went from 46,255 before save to 34,139 after the work (`:233`, `:247`). That means no leaked object reference kept the VI in memory. The +177 left over versus the count right after restart (33,962, `:29`) is within restart noise: in R2 the same comparison went down by 1,927 (`stage_d1_l2r2.log:27`, `:321`).

**The most plausible alternative** is a real per-call leak in an op that ran only once in this stage. The candidates are:
- `connect_from_wire`: +75 (`:217`)
- `connect_nested_v1`: +58 (`:189`)
- the For-loop create: +85 (`:50`)

Both connect ops created and then deleted a stray Invoke node (`:176-188`, `:204-216`). That create-and-delete path could hold a reference, and nothing in this run repeated those ops to rule it out.

**Cheapest discriminating test:** the 20-call test that 176(a) itself prescribes, run only on those ops. It runs on a scratch byte copy of R2, never the saved VI, which is broken by design and never cold-loaded (`:241`). Read the handle count after every call.
- **Leak:** the count climbs about 60–75 per call, well past +100.
- **One-time growth:** a step on the first call, then flat within ±100.

If it comes out flat, the judgement session should accept the artefact and remove L4's gate from future editing-stage cards, keeping the numbers as recorded facts.

ROOT CAUSE: The card's L4 applied the ±100 handle limit, which Pre-decided 176(a) reserves for repeated calls of one op, to an editing stage that creates objects, so the one-time growth from those objects failed a gate that should only have recorded it.
TEST: On a scratch byte copy of R2, call `connect_from_wire`, `connect_nested_v1` and the For-loop create 20 times each and read handles after every call; a leak climbs about 60–85 per call, one-time growth is a first-call step then flat within ±100.