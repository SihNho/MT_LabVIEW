ATTACK this claim about the failed read-only fixture probe tools/bench/diag_c112c_fixture.py (log tools/bench/diag_c112c_fixture.log, card 112-3 W0).

What happened (log lines 3-40): the script restarted LabVIEW, byte-copied claudeDev\background VIs_COPY\exp-ref management.vi to
claudeDev\scratch_c112c_sr.vi and a dated read copy, read it (wiki_build.read_live, k_contract_79.mloops, build_d1_v0.owner_of:
66 terminal rows, 125 objs, ExecState 1, every Diagram owned), wrote tools/bench/graph_scratch_c112c_sr.json, then gate L failed
(the WhileLoop #74 has no shift register: LOOPS [('WhileLoop', 74, [], {}), ('ForLoop', 184, [205], {}), ('ForLoop', 45, [270], {})]),
and then `g.close_panel(scr)` raised LabVIEW error 1149 (0x47D) "Cannot close or set the state of a closed front panel". The
exception aborted the loop before the second fixture (fit WLC-plot KK.vi) was read; the finally block killed LabVIEW, deleted
the read copy, sources unchanged (gate H PASS).

CLAIM (mine): two separate causes, both in my script, none in the fleet tools:
 (1) gate L: a wrong FIXTURE CHOICE - the offline scan (tools/bench/diag_c112c_scan.log) picked exp-ref management.vi because it has
     LeftShiftRegisters and one WhileLoop, but the registers belong to its two FOR loops. stagexec.LVBackend.wire_sr addresses
     `uid_index("WhileLoop", loop)` only (tools/stagexec.py:1805), so a For-loop register cannot serve the T1 check (B2a's registers
     sit on WhileLoop #10170).
 (2) the crash: gscript.close_panel on a VI whose front panel was never opened (read_live/mloops/owner_of load the VI but open no
     panel); diag_c108b_graph.py, which I copied, never calls close_panel. Fix = drop the call (LabVIEW is killed at the end anyway).
Planned next act: rerun the probe (script already patched) reading fit WLC-plot KK.vi (T2) and WhileLoop-register candidates
choose bandpass v2.vi, check N bead pos v2.vi (they have local subVIs in background VIs_COPY; the fixture copies sit in claudeDev
root, so the subVIs must be found by LabVIEW's search path - measured by ExecState).

Already ruled out: the fleet readers (the read itself completed, 66 rows, ExecState 1); input modification (md5 unchanged).
Attack especially: whether loading a claudeDev-root byte copy of a VI whose subVIs are relative-linked into background VIs_COPY
can raise a modal "Find the VI named ..." dialog under COM (which would hang the rerun until the bgrun deadline), and whether
there is a cheaper fixture (a subVI-free VI with a WhileLoop shift register) under claudeDev that the scan missed.
