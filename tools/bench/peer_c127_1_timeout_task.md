ATTACK this claim about tools/bench/diag_c127_1_fsinner.log (script tools/bench/diag_c127_1_fsinner.py, plan tools/bench/diag_c127_1_fsinner_plan.json).

FAILURE: `BGRUN TIMEOUT killed after 2402s (limit 40.0 min)` (diag_c127_1_fsinner.log:116). The last line before the kill is
`PASS S_latest connect_term_uid op err ''` (log:112), i.e. the 6th and last wire returned in 6.7 s; the kill came during the
post-connect reads (census snapshot, OpAllTerms_v1 read, wire_joints, wire_remove_loose_ends, then an Error List GUI read).

CLAIM: the timeout is a BUDGET error in the script, not a LabVIEW hang or a defect of the measured route:
 - the script does an Error List GUI read (errorlist_check E.read, ~125 KB raw each) after the first crossings and after EACH
   second sink; raw-file mtimes 22:35:51, 22:44:34, 22:53:00, 23:01:30 => one wire + its reads + one Error List read takes
   ~8.5 min; 4 such reads + setup (start 22:22:33) cannot fit in 40 min, and S_latest's would have ended ~23:10;
 - bgrun --max-min 40 was BELOW the Stage's own deadline_min=42 (diag_c127_1_fsinner.py:22), so the Stage's orderly close
   (scratch delete, md5 checks, LabVIEW kill) never ran; LabVIEW (PID 17792) and the scratch were left behind.
 - every measured prediction up to the kill held: A_i/A_bn census == 126-6's; 3 second sinks (S_rat1/rar1/raf1) census {},
   FS outer tunnels 60 -> 60, Is Broken? False, wire 32859 joints 3/4->4->6->7, terms 2->3->4->5, loose 0, Error List 61 / loose 24
   unchanged (log:79-109). S_latest's op returned wire 27589 (the existing inner-face wire), err '' (log:112) but its census was
   never read.

Questions: what is the strongest reason this claim is wrong (e.g. a slow-down per read that signals a growing leak / handle
growth, or a GUI read that hung rather than ran slow)? An alternative explanation? What would falsify it? The cheapest
discriminating test before re-running (e.g. Error List read once at the end only, deadline ordering bgrun > Stage deadline)?
