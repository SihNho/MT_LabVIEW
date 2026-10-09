---
card: 154-a2-3
status: current
date: 2026-10-09
---
# 154-a2-3 facts - P5-1 route census: 18 rows OK, 2 GAP (the refnum path); no tool edited (offline, LabVIEW 0)

## Rows (table: `tools/bench/p5_route_census.md`; evidence `diag_c154_a2_3_census.log:46-98`, RESULT 7/0)
- 20 census rows: 17 OK (creates, const wires, indicator on const, case_wired, case tunnel for the element, SR + const_sr, R1/R2,
  False pass-through, local write, SR exit -> local), 1 compile row OK (17 ops, log:92), 1 X17 read row, **2 GAP** (rows 9, 10).
- OK but no launched precedent: row 8 (#2626 -> case tunnel, scratch-measured only, diag_c123_casetun.log:38,45,69), row 17 on 686
  (local_write launched on #639 only), row 18 (no plan wires from a SR right OUTER face).

## GAP rows verbatim
- Row 9 (refnum #4866 -> loop 1.2): Va "FS exit to diagram #-19, the FS #681 sits on #536 - only ONE border (frame -> the FS's own
  diagram) is MEASURED (U6/U6')" (log:79); Vc same into a case tunnel on #23166 (log:81); Vb (tunnel on #10170, wire into its outer on
  686) = stagesim CRASH `TypeError` at stagesim.py:1783 (`st["diagrams"]` has no entry for base frame #4866), not a SimError (log:80).
  stagexec: frame-to-frame FS wires compile only for a PLAN-MADE FS (stagexec.py:656-711); fs_routes never carry fs_frame_to_frame
  (stagexec.py:304-305, stagesim.py:2513); a plain connect simulated as fs_frame_to_frame is refused (stagexec.py:2570-2573).
- Row 10 (loop tunnel -> case tunnel -> Enqueue 'queue'): a tunnel group needs its in- and out-wire in the next two actions
  (stagexec.py:766-775); the only tunnel-to-case-tunnel route starts at a plan-made SR inner face (stagexec.py:776-787); a plain
  cross-border wire is refused (stagesim.py:1506-1508). This row stays a GAP even if Obtain sat on 686.

## Registration (brief step 3) - not made
- Return condition "Any GAP row" met. Also measured: the `primitive` route consults no class/terminal table (stagexec.py:442-445,
  3068-3082, 472-484; stagesim.py:2298-2349); `QUEUE_TERM_TABLE` (stagesim.py:1605-1607) is read only for queue_kind 'dequeue'
  (stagesim.py:2296-2297). Obtain/Enqueue replayed with the donor-json names and ParameterTerminal without registration (log:77-78).
- termclass_table.json holds Obtain (n=2) and Enqueue (n=1) signatures; Dequeue and Release are absent (their class = plan-declared).
- X17 (stage_prerun.py:2827, read only): refuses c_obt (uid 108) and c_enq (uid 44) "external donor DonorQueue_v0.vi uid N: label
  UNMEASURED (not in PRIM_DONORS)" (log:94). Entries needed in PRIM_DONORS (stage_prerun.py:2802): (DonorQueue_v0.vi, 108/44/45/46)
  -> Obtain Queue / Enqueue Element / Dequeue Element / Release Queue, "Function", 81dba822efec5226123b3b88ee4383bc,
  tools/bench/donor_queue_v0.json. The DBL const (uid 52) is const_donor = exempt (stage_prerun.py:2840).

## Self-tests and md5
- Existing self-tests not run (no tool changed; the baseline is unchanged by definition).
- stagexec 1bab9cf9 -> 1bab9cf9, stagesim 78b8d5a1 -> 78b8d5a1, stage_prerun c739eb86 unchanged; stagekit 604529e8, addrcheck 207beb0d,
  gscript 1a80236e, vigraph a7eb58c7, memory_model 6f2b5687, graph 22f967b5, ring-p5.md 81df09ca, DonorQueue_v0.vi 81dba822: before = after
  (log:48 GATE P4a, log:96 GATE P4b). s09 VI and the donor never opened; tools/hooks untouched; LabVIEW processes at end: 0.
- Census run 1 (log:1-45) ended rc=1: my script caught SimError only and the Vb form raised TypeError; run 2 records it as CRASH.

OPEN: route for the refnum into the new True frame (rows 9-10): a tool card (base-FS frame-to-frame + loop-tunnel -> case-tunnel), Obtain on 686 (closes row 9 only), or a refnum indicator on #4866 + local read in the frame (existing routes; design change).
