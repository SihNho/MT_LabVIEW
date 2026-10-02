# Brief for card 140-1 (judgement cycle 140, PD319(c)) — offline measurement, no LabVIEW, no tool edit

1. MODEL — write down the X10 formula and constants exactly as `tools/stage_prerun.py` computes them (start load,
   per-op cost by op kind if any, per whole-VI read cost, final-read term, PASS 675 / FAIL 690), with file:line.
   Reproduce step 1's 750.7 MB (`plan_ring_p4s1_pred.json:384-388`) from it, exact or within 0.5 MB.
2. BIND FACTS — for step 1 list the 29 reads: which are checkpoints {0, end} and which are BIND. For each BIND read:
   the action that creates the bound object, the first later action that uses its uid, and the binder's matching key
   (how stagekit/stagexec identifies the new uid from the read: before/after row diff, class, label, owner), file:line.
3. MERGE FACTS — (a) the minimal number of reads that still places every bind after its create and before its first
   use (interval point cover), for step 1 and for the whole v14 list; (b) for each merged group, whether the CURRENT
   binder would identify every created object unambiguously from ONE read (same class + same owner created twice in
   one group = ambiguous), cited to the binder code; (c) whether recipe/stagekit already supports a bind read placed
   later than its create (yes/no + file:line) — i.e. whether merging needs a tool edit.
4. SESSION TABLE A — current read model {0, len} | BIND per session, each session starting at the start load X10
   uses (606.1 = 600.2 bed load + op-0 read, or whatever X10 applies — say which), sessions = greedy
   dependency-closed prefixes of v14 action order, each predicted <= 675. Columns: session, first/last action id,
   action count, op kinds, R, predicted peak. Total sessions.
5. SESSION TABLE B — same, with reads merged per 3(a), only for groups 3(b) marks unambiguous (ambiguous binds keep
   their own read). Total sessions.
6. DEPENDENCY CHECK — every session is dependency-closed (no action uses a uid created in a later session); name any
   action that forces a cut. Also list where a session boundary would fall inside a group the plan treats as one
   unit (e.g. a create + its loose-end removal, PD261(d) "each RLE with its loose end").
7. Facts file `tools/bench/diag_c140_1_facts.md` (<= 45 lines), tables also as `tools/bench/diag_c140_1_sessions.json`.
   Measure, do not choose: no cut picked, no merge tool built. OPEN line = only what judgement must decide.
