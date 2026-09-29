**The most likely cause is the reader, not the constant.** Gate A1b read the constant through a property node cast to the generic `Constant` class. For anything other than a string constant, that read returns an empty ("void") value without an error. So the bytes A1b got say nothing about whether the 20 names were written into constant #101.

**What held up when I checked the files**
- `read_str` reads through `OpConstValue_v1` with `Class Name = "Constant"` (`tools/bench/diag_c118_p0.py:32-41`).
- The project's own measurement already describes this: reading `Constant.Value` through a `VI Server:Constant` cast gives the value for a string constant, but a void value (type code 0x0000) for numeric and Boolean constants, with no error. What decides it is the class the property node was built for (`docs/NAMES.md:1157-1162`).
- The A1b bytes decode as a void value under the measured byte layout (`docs/NAMES.md:1153-1155`; `diag_c118_p1.log:8`). An empty string-array constant would still carry an array type descriptor. So void does not mean "the list is empty"; it means "the read returned nothing".
- The same 20 bytes, marked `"void": true`, came back earlier for VISA constants read through the base `Constant` class (`diag_c105_const.log:25-30`; `docs/d1-loop12-17-split-plan.md:1857`). The only real data this reader has returned is for a plain string constant (`diag_c118_p1.log:4`).
- Nothing in the create step shows an error (`diag_c118_p1.log:6-7`). The value reaches the constant only through one `SetControlValue` call (`tools/gscript.py:2823-2824`). No list has ever been sent this way, so a failed write is still possible, but it is not shown.

**What did not hold up**
- **Analyst 1 says ring #13245 was read "through the same reader". It wasn't.** That read used a different subVI, `OpConstValueN_v1` (`diag_c118_p0.py:44-60`). It also came back void, and on both routes (`diag_c118_p0.json:369`). That is consistent with the class-mismatch problem, but it is a different reader.
- **Analyst 1's test would tell us nothing new.** Reading #214 with `read_str` will give void; `NAMES.md:1157-1159` already records that for numeric constants. It says nothing about string-array constants.
- **Analyst 2's reads are sound but not the cheapest.** They need either a new subVI built for the `ArrayConstant` class, or an indicator plus a run of the scratch VI.
- **A side effect all three imply but only Analyst 1 states:** gate B2 compares two void results and passes without checking anything (`diag_c118_p1.py:91-95`), and gate B2b has the same A1b blind spot (`:96-99`).

**Cheapest test that separates the two explanations (Analyst 3's, and it survives):** make a second constant on the same `Control Names` input with `value=None`, then call `read_str` on it. This needs only calls that already exist.
- If that also returns the 20 void bytes, the reader cannot see string-array constants, and A1b tested nothing.
- If it returns a string-array type descriptor with zero elements, the reader works, and the list write is what failed.

I only read the files; nothing was run.

ROOT CAUSE: Gate A1b's reader (`read_str` → `OpConstValue_v1`, cast to the base `Constant` class) returns an empty void value without an error for any constant that is not a scalar string (`docs/NAMES.md:1157-1162`), so the 20 bytes are the reader's blind output and not proof that the Cam_pool00..19 list failed to reach constant #101.
TEST: In the same scratch donor VI, create a second constant on Get Controls.vi's `Control Names` input with `value=None` and read it with `read_str`: the same 20 void bytes mean the reader cannot see array constants, while a string-array type descriptor with zero elements means the reader works and the list write in `create_const_loop_term` failed.