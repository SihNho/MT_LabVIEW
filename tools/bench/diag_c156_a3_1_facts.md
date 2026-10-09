---
type: facts
status: current
date: 2026-10-09
card: 156-a3-1
---
# Card 156-a3-1 facts: wire present -> `cfw`, wire 0 -> the exact op-16 stop (ops 16 AND 17); `diag_c156_a3_1_route.py` (stagexec 25a1494c called unchanged) -> `.log` rc=0 13/0 (:60-61)
## M1 connect_route, op 16 (#24360 -> 5760 'cal cluster path') and op 17 (#24367 -> 5778 'file size')
- op16 (step_15 and step_17 = executor prev): #24360 LoopTunnel #24357 InnerTerminal wire 24330 (route.log:9,15). AS STORED -> `cfw`,
  dst (1,1,6) (:11,17). WIRE 0 -> STOP "ADDRESS: #24360 is an INNER face of LoopTunnel #24357: only the outer face's owner route is measured (l2a1_faces_81.log)" (:12,18) == scratch :254 verbatim.
- op17 (step_15 and step_20): #24367 LoopTunnel #24361 InnerTerminal, wire 24153 (:23,29). AS STORED -> `cfw` (1,1,9) (:25,31); WIRE 0 ->
  STOP "ADDRESS: #24367 is an INNER face of LoopTunnel #24361: ..." (:26,32). Peer s4 predictions P1-P4 all held (:13-34).
## M2 live state of #24360 / wire 24330 / #24357 after op 12 and at the op-16 read: NOT LOGGED
- Scratch log: 24360 only in the stop text (:254-255); 24330 never. Resume record: only "stop" (:5); its "reads" are op numbers.
- Loggers: the read `real_new = be.read()` (stagexec.py:2478) is written nowhere; STEPX prints diff counts only (:2540-2542); resume_record
  (:2178-2193) stores bind/loop_of/reads-as-k. Op 15 was a checkpoint (scratch :243 diff 0): op 16 ran on that fresh read (stale=False, :2485).
- compare() drops a dangling term that is in allow_either and unwired on the other side (stagexec.py:970-972): op-15 diff 0 holds either way.
## M3 the ambiguous fate and the ops that use it
- step_09: wire 24330 = {5760 on #376 sink, 24360 on #24357 source}; step_10 (mv_376): only 24360 left on it (route.log:36-37).
- Rule: _apply_only_sink keeps the source row unless fate == "delete" (stagesim.py:1065-1080, clear at :1076-1077); fate from
  opmodels/move_in.json:4 `"only_sink": "ambiguous"`; ambiguous sources -> `allow_either` (stagesim.py:1238-1239).
- step_10 only_sink, all "ambiguous": w10394 (src 3060 ControlReferenceConstant), w24091 (25235 LoopTunnel), w24153 (24367 LoopTunnel), w24285
  (24190 LSR), w24312 (24288 LSR), w24330 (24360 LoopTunnel) (route.log:38-39); steps 11/12 add none (:40-43). Executor: self.allow (stagexec.py:2466,2533).
  | op | src | dst | sim src wire | route wired | route wire 0 |   (route.log:46-55; 24190/24288/25235 source no later op)
  | 13 connect w_ref | #3060 (#3052) | 5772 | 0 (#3052 moved in at op 11) | nested (plan_ring_p5s02a.json:1292) | nested |
  | 16 tunnel t_in1 | #24360 (#24357) | 5760 | 24330 | cfw (plan :1326) | STOP INNER face #24360 |
  | 17 tunnel t_in2 | #24367 (#24361) | 5778 | 24153 | cfw (plan :1338) | STOP INNER face #24367 |
## M4 why ops 10-12 are not E1 checkpoints
- Rule: `BIND = {k | ops[k].kind in SX.BIND_KINDS}`, `CHECKPOINTS = {0, len(ops)} | BIND` (stagekit.py:1927-1929); BIND_KINDS = ("add_sr",
  "tunnel","create","connect_term_uid") (stagexec.py:1978), no move_in -> [1,3,6,8,9,15,16,17] (route.log:57).
- Executor accepts any SUPERSET (refuses only a set lacking a binding/last op, stagexec.py:2409-2419). Plan field: none - action key
  `checkpoint` is a log label only (stagexec.py:2536,2542), 0 actions carry it (route.log:58).
- Recipe: RingSession(plan, pred, licence, census) has no checkpoint argument (stagekit.py:1915); executor() passes self.CHECKPOINTS (:1982);
  the recipe builds RS at module level, calls RS.executor(s) (stage_d1_ring_p5s02a.py:32,43). No recipe assigns `.CHECKPOINTS` (grep
  `\.CHECKPOINTS\s*=` tools/recipes: 0 hits). Older precedent of extra checkpoints: stage_d1_disp.py:9 "binding ops + 4, 5, 12, last";
  stage_prerun X10 models reads from the captured list (stage_prerun.py:1982-2001). P5-1: 154 [1,2,4,5,6,7,8,9,10,12,13,14] of 14
  (diag_c154_p5s01a_scratch.log:73), 155 [2,4,6,7,8] of 8 (diag_c155_p5s01b_scratch.log:60); `move_in` 0 hits in both: no move ops.
## M5 precedent: LabVIEW fate of a wire whose only sink moved into a structure
- grep `only[-_ ]sink.{0,120}(kept|keep|delet|drop|dangl|measured)` and `move_?in.{0,160}(kept_half|half-wire|wire 0|dropped)`: tools/bench/*facts*.md
  none; archive/peer only delete_object cases (2026-09-28-priorart-c115b-l2r1.md:564) and only-source moves, no only-sink move sample.
- opmodels_onlysink.log:192-196: move src=constant {kept_half 1, deleted 1}; move src=node {kept_half 1}; delete src=tunnel {kept_half 2}
  (D3 LoopTunnel w5090 :140). NO move sample with a LoopTunnel source: no precedent for #24360 / #24367.
OPEN: M1 says the stop needs #24360 unwired in the live read, but that read is not logged (M2) - accept the wire-0 explanation on the code path alone?
OPEN: op 17 (#24367) stops the same way with its wire gone; op 13 routes `nested` either way - which ops the retry must cover.
OPEN: M4 - extra move_in checkpoints are reachable only by a recipe attribute or a stagekit change; which, if any, PD379(e) intends.
