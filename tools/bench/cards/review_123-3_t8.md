ATTACK this claim about the failing log tools/bench/selftest_sr_init_c123.log (script tools/bench/selftest_sr_init_c123.py, card 123-3, offline, no LabVIEW).

Observed: gate T8 failed with `SimError: address '901' is not '<uid>.<terminal>' / 'new:<kind><n>.<terminal>'` when the self-test called
`stagesim.op_wire(st, {"src": "901", "dst": "3111"}, ...)`. T1-T7 and T9 passed.

Claim: this is a bug in the SELF-TEST, not in the route under test. `stagesim.parse_addr` (tools/stagesim.py:326-332) requires an address of
the form '<owner uid>.<terminal name>' or a dict, and `resolve_addr` (tools/stagesim.py:335-368) selects by `term_uid` / `term` / side among
the rows of the OWNER uid. The self-test passed bare TERMINAL uids ("901", "3111") where owner-based addresses are required. The fix is to pass
{"uid": "900", "term_uid": 901} for the constant and {"uid": "311", "term": "outer"} for the left register's outer face; nothing in
stagesim.op_wire or in the new stagexec 'const_sr' route (tools/stagexec.py connect_route) changes.

Already ruled out: (1) the route itself - T1/T2/T6/T7 exercise connect_route/LVBackend.connect and pass; (2) a stagesim same-diagram rule -
the error is raised in parse_addr before op_wire reads any row.

Give the strongest reason this claim is wrong, an alternative explanation, what would falsify it, and the cheapest discriminating test.
