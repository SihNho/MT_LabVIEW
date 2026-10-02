# Brief chat-S4 - adopt the scratch result, read only new nodes, resume within a cycle (user 2026-10-03)

User approved (after the chat's process analysis): "A, B는 도입하는게 좋겠고 4번의 경우 한 싸이클 내에서는 계속 이어서
작업하는게 좋겠음." Measured basis: whole-VI read ~21.5 s and ~1.95 MB that only a fresh LabVIEW frees, error 2 at
704.8 MB (diag_chat_m1_mem.log); every step today is run twice (scratch byte copy, then the real bed); a mismatch at
step k restarts the whole stage from step 0 (P3b-1 needed 4 scratch attempts: stops at ops 1, 33, 26, then pass).

## A - adopt the scratch result
When a scratch run on a BYTE COPY of the bed passes every STOP gate (gateclass) including the step-end checks
(computation diff, Error List exactness rules, prim gate, input md5), that scratch file IS the stage's result: save it
under claudeDev with the normal stage name (GUI Ctrl+S rule for broken intermediates, as today), record md5, and do
NOT re-run the same ops on the real bed. The launch gate / recipes must accept "adopted scratch" as the launch.

## B - read only the new node
Replace the per-BIND whole-VI read (wiki_build.read_live / report_all) with a per-node read of the node just created
(read_terms / OpAllTerms_v1 by owner uid - measured working in 137-3, diag_c137_3_lookup.log:39,44,67,72), also for
constants inside new bodies. Keep ONE whole-VI read at session start and ONE at session end (and wherever a gate needs
the whole graph). Update stage_prerun X10 so R counts only whole-VI reads (per-node reads ~0 MB - measure it).

## Resume within a cycle
On a STOP-gate failure at step k: save the scratch as-is (GUI save rule), record its md5 and the last good step, and
write a resume record. A later card IN THE SAME CYCLE may resume from that file: one whole-VI read, verify it equals the
simulator state after step k-1 (computation diff 0 vs sim), then continue from step k with the fixed plan/model. A new
cycle always restarts from the last accepted stage file. Never resume onto the real bed.

## Do
Implement A, B and resume in stagexec/stagekit/stage_prerun/recipes (one shared mechanism), self-tests for each
(adopt path, per-node bind equals whole-read bind on recorded graphs, resume verify passes/fails correctly), and a
measured LabVIEW check on a scratch copy: one small known plan (e.g. the P3a or P4 s01 plan) run with B, reporting
seconds and MB per BIND vs today. Record the decision in docs/d1/tooling.md + INDEX. Runner stopped; no other live
card editing tools. Edit tool only. git commit allowed. Return one result/1 JSON object.
