# Cycle 137 brief — detail behind cards 137-1, 137-P1 (and 137-2) (judgement, 2026-10-02; PD302 in `docs/d1/ring-p4.md`)

## 137-1 (LabVIEW, scratch only) — pass items in full
1. New script `tools/bench/diag_c137_1_routes.py` (copy of `diag_c136_3_routes.py` 634a97b7, <=120 lines on stagekit). Its per-node
   lookup must find a node created inside a NEW While body: 136-3 raised `ValueError #29466 (ks const in WS body #29431) is not in
   Diagram[22].Nodes[]` (`diag_c136_3_routes.log:36-46`). Address the body diagram by its owner uid, or read the node by
   `read_terms` on the body. Show the fix with a `--dry` run that reaches every lookup before the real run.
2. List every whole-VI read call site of the new script with its count (PD299(b)); X10 prerun must PASS with R counted from that
   listing (report the gate's R and the source R). Do not change thresholds; X10 FAIL => return, no run.
3. ONE run, routes per `tools/bench/cards/brief_136.md` items 1-3 (U1 U2 U3 on a scratch VI, W1-Or in the same scratch VI, U5 U6
   on a scratch byte copy of the bed). Per route: PASS/FAIL, `Is Broken?`, census delta, whether a source wire was re-created;
   ExecState; Error List `--count-only --role scratch` ONCE at the end (PD258(a)). Record under `tools/bench/scratch_verify/`.
4. LabVIEW closed and verified gone; scratch VI and byte copy deleted after the records (md5 kept in the result); handles
   before/after; bed md5 395118775a52bc90073f4449b99f899d unchanged.

## 137-P1 (offline, read-only) — pass items in full
1. stagesim step 102 of `plan_ring_p4_v3.json` (d14c1bba, action `p4_x_fd`) stops with "#686 owns no terminal" while the real graph
   `graph_ring_p3b2b_20261002_133824.json` lists t8936 on 686 (`prep_c136_p2_sim.log:101-106`). Report: the code path that raises
   (file:line), what the plan addresses on 686 (terminal key/uid), the real graph's row for t8936 (owner, class), and which side
   differs (plan addressing, graph loader, simulator owner index). Facts only; NO edit of stagesim/stagekit/stagexec (PD301(e)).
2. v3 session table: per build step (<= 40 actions) the LabVIEW sessions needed. Each session's start = a MEASURED load (fresh 567.7,
   `diag_c136_4_mem.log:114`; bed copy 576.5, `:85`; bed 600.2, `diag_c136_1_graph.log:24`) + edit and read terms from
   `memory_model.json` (cite keys); planning stop 675, launch stop 690. Totals: sessions and broken files under each option of
   D-2026-10-02-04.
3. v3's distinct route classes on UNMEASURED routes: per class the action count, one example action id, and which of 137-1's routes
   (U1 U2 U3 U5 U6, W1-Or) measures it, or "none" plus the cheapest scratch measurement in one line.
4. Review c135e §4 (`archive/peer/2026-10-02-c136-3-c135e-elmismatch.md:76-83`): one-sided wires (source-only and sink-only, with uids)
   of `graph_ring_p3b1_20261002_073225.json` vs `graph_ring_p3b2b_20261002_133824.json` with the `prof()` logic of
   `errorlist_expect_p3b2.py:33-38`. Report the exact set difference and whether it equals {4878 + exactly one of 3268/30592/28437}
   and nothing new.
5. Write the facts to `tools/bench/prep_c137_p1_facts.md` (<= 80 lines), file:line on every claim.

## 137-2 (LabVIEW, after 137-1 returns) — read-only stop-mode op
Build a read-only op on the `OpLoopEndRef_v0` pattern (`tools/recipes/build_oploopendref_v0.py:250-266` — PD301(d) cited a wrong
`tools/bench/` path) that reads `While Loop.Stop If True?` (6362C01, community-sourced, PD299(d)) and a Boolean control's
`Mechanical Action`; run it on a bed byte copy for `#10170` and `stop (end)`; op hygiene per PD242(b) via `gscript.hygiene_run`.
