ATTACK this claim about the failed run tools/bench/diag_c131_5_s4_el.log (script tools/bench/diag_c131_5_s4_el.py, offline, no LabVIEW).

Observed: gate E1 FAIL "stubs log retires exactly ONE wire, w3040", detail = TWO hits, tools/bench/diag_c131_5_stubs.log lines 14 and 21, both the identical text "RETIRED w3040 src/snk 1/0 ...".

Claim: this is a parsing bug in diag_c131_5_s4_el.py, not a fact about the graph. diag_c131_5_stubs.log is written by bgrun in APPEND mode and holds three runs of diag_c131_5_stubs.py (BGRUN START lines; run 1 crashed, runs 2 and 3 each printed the same single RETIRED line; run 2 ended rc=1 only for a malformed RESULT line, run 3 rc=0). The script counted RETIRED lines across all runs. Fix applied: count only lines after the LAST 'BGRUN START' and require that run to end 'BGRUN END rc=0'. Every run of the stubs script retired exactly one wire, the same one.

What would falsify it: any run section of diag_c131_5_stubs.log that retires a wire other than w3040, or more than one wire, or a difference between the two RETIRED lines.
