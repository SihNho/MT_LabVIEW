ATTACK this claim about a failed gate in tools/bench/diag_c123_struct.log (script tools/bench/diag_c123_struct.py, card 123-5).

FAILED GATE (diag_c123_struct.log, "S1a Equal? #26802 on #639: x wire +1, y const wired"): the script predicted that
wiring the new Equal? node's `x` input from node #6810's output `current image number` (via
tools/recipes/build_opconnectnested_v1.py connect_nested_v1, same diagram #639) would add exactly ONE Wire object.
Observed: connect_nested_v1 returned (wire delta 0, ExecState 0, error '').

CLAIM (my explanation): the gate was wrong, not the wiring. `current image number` on #6810 was ALREADY wired
(wire w3747, docs/d1-loop12-17-split-plan.md PD246 brief: "BufNum (#6810 t6897, wire w3747)"), so Connect Wire made a
BRANCH of w3747, and a branch adds no Wire object (the skill's law "a successful BRANCH adds no Wire object";
docs/toolkit-capabilities.md:78 records an indicator "on w12256 (a BRANCH of an existing wire)" with no wire delta).
ExecState 0 is the bed's broken-by-design state (STATUS: P2b bed ExecState 0 by design), not this wire.
The op's own readback on that call printed {'UID': 26802, 'Name': 'x', 'UID 2': 0, 'Is Broken?': False}
(diag_c123_struct.log, line after "OBSERVED uid 26802"), which is reported, never gated (the readouts may pre-date the wire).

Already measured in the same run: the later case_wired call wired the case selector from Equal?'s `x = y?` output with
wire delta 1 and selector wire == source wire 27314 (gate S1c PASS), so the connect op itself works on this diagram.
NOT measured: the x terminal's wire uid after the call (the script did not read it back).

What I need: the strongest reason this explanation is wrong, an alternative (e.g. the connect silently declined and x
is still unwired), what would falsify the branch explanation, and the cheapest discriminating test (e.g. read Equal?'s
Terminals[] by uid echo: x's wire uid == w3747 => branch; 0 => declined).
