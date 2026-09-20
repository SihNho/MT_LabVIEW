Failed prediction recorded by the stall watchdog: tools/bench/stall_pid20500_143532.log says
"STALL: 2026-09-18 14:45:27 pid 20500 alive 595s, log stale, CPU +0.00s in the last 212s" for tools/bench/p2_open_copy.py.

My explanation: this is NOT a stall. p2_open_copy.py deliberately calls time.sleep(10000) after opening the D0 copy's
front panel, to hold two VI Server references (the ORIGINAL preloaded read-only + the copy) so the copy's subVI
hierarchy stays resident while the USER runs the VI by hand (P2 live motor-limit verification, user present).
Zero CPU and a quiet log are exactly what a sleeping reference holder looks like. This is the fifth occurrence of
the watchdog's known false-positive class (STATUS OPEN 41: "the watchdog could not tell a deliberate sleep from a
hang"; remedy - a heartbeat file - not built, and the user has ordered no new process devices).

Attack this: is there any way the process could be genuinely hung rather than sleeping (COM call blocked inside
LabVIEW while the user's VI runs; pythoncom apartment issues)? What observation would distinguish "sleeping in
time.sleep" from "blocked in a COM call" without killing it (e.g. a thread stack dump via py-spy, or the
process's wait reason)? Name the cheapest discriminating test. Is leaving the references held while the user runs
the VI risky in any way (LabVIEW behaviour when a running VI's caller reference is held by an external client)?
