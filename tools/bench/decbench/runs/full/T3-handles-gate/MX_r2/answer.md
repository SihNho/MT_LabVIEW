**No: nothing shows the saved VI is defective. The L4 pass criterion is what's wrong.**

1. **The ±100 test was used outside its scope.** L4 applies "handles +-100" to the whole stage (`tools/bench/cards/task_119-4.json:32`). That number is the reference-hygiene test for 20 repeated calls of one operation (`CLAUDE.md:224-225`, `CLAUDE.md:514`). Pre-decided 176(a) already ruled that it "does not apply to an editing stage": handles there are "RECORDED, not gated", and "a leak is judged only by the 20-call test" (`docs/d1-loop12-17-split-plan.md:458-462`). The recipe followed that ruling. It recorded the handle numbers (`tools/bench/stage_d1_qrt_pool.log:233`) and passed the leak gate, references opened = closed at 9/9 (`:245-246`), the same approach as `tools/recipes/stage_d1_l7_r.py:112`.

2. **R2 is not a fair comparison.** R2's measurement window starts after its first operation (`tools/recipes/stage_d1_l2r2.py:96-98`). R2 ran only delete operations (`tools/bench/stage_d1_l2r2.log:34`), so its only first-call cost (+20, `:48`) fell before the window.

3. **The growth comes from each operation's first call, not from every call.** These first calls fall inside the window:
   - `drop_subvi` +35 (`stage_d1_qrt_pool.log:68`)
   - `create_primitive_nested` +79 (`:78`)
   - queue obtain +27 (`:115`)
   - queue enqueue +29 (`:152`)
   - `wire_const` +33 (`:160`)
   - `connect_nested_v1` +58 (`:189`)
   - `connect_from_wire` +75 (`:217`)

   They add up to +336. Five repeat calls, each still creating a new constant, node or wire, cost +0, +0, +2, +1 and +0 (`:87, :96, :134, :168, :197`).

4. **The same first-call costs show up in other LabVIEW sessions.**
   - In dispA_r2, a create stage that passed (`tools/bench/stage_d1_dispA_r2.log:685`), `wire_const` cost +33 and then +1 (`:251, :258`), the same as here.
   - `loop_in` cost +87 there (`:56`) and +85 here (`:50`).
   - In c97, `connect_from_wire` cost +74 on its first call (`tools/bench/diag_c97_tools_handles.log:35`), against +75 here.
   - c97 also ran both connect operations 20 times with no handle growth (`:125, :128`).

5. **Handle counts during the build say nothing about the file.** The saved VI is never run (`stage_d1_qrt_pool.log:237`) and never reopened after saving (`:241`).

**Most plausible alternative:** a real per-call leak in one of the operations called only once here: `loop_in`, `drop_subvi` or queue enqueue. A leak would add handles on every call. The repeat calls in point 3 rule this out for the other operations, but not for these three.

ROOT CAUSE: Card 119-4's L4 applied the ±100 handle test, which is meant for 20 repeated calls of one operation, to a whole editing stage against Pre-decided 176(a), and the +322 it caught is the one-time first-call cost of seven operations (+336, with the five repeat calls adding only +3), not a reference leak in the saved VI.
TEST: In one LabVIEW run on a scratch byte copy of R2, without saving, call each of `loop_in`, `drop_subvi` and queue enqueue 20 times (176(a)'s test): handles flat within ±100 after the first call confirm a one-time cost, while a rise close to the first-call cost on every call (about +500 or more over the 19 repeats) would confirm a leak.