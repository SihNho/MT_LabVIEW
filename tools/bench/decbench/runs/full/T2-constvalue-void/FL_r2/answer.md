**Finding (confidence: moderate — read from files, not measured on LabVIEW).**

**What the bytes say.** The read-back `2600800000000001000400000001000000000000` (diag_c118_p1.log:8) contains no string data at all. Compare gate A0 in the same run, where the same reader returned bytes ending in a length-prefixed `Cam` (diag_c118_p1.log:4). So the reader works for a scalar string constant, and for #101 it returned an empty, untyped value — not even twenty empty strings.

**How the value was written.** `create_const_loop_term` puts the Python object straight into the op VI's `Value` control with `SetControlValue` and runs it (tools/gscript.py:2823-2825). That control was made by `create_control` on the `Value` input of the `Terminal.Create Constant` invoke (tools/bench/build_op_const_loopterm_77.py:48-49, 57), so it is a variant. The function's only success evidence is the created uid and the invoke error (tools/gscript.py:2807, 2826-2834); neither says anything about the value. Gate A1 passing (diag_c118_p1.log:7) therefore proves creation only.

**What is new in this call.** The diagnostic passed a Python list of 20 strings (tools/bench/diag_c118_p1.py:33). The other callers I found pass scalars: `int(value)` (tools/bench/diag_c90_t0_step3.py:68) and `bool(value)` (tools/gscript.py:3554). I found no earlier array value through this route, so the array case is unproven.

**Most plausible root cause.** The list did not survive the COM → variant control → `Create Constant` path as a String array. The constant was created and typed by the sink, but its value was never set, with no error raised.

**Most plausible alternative.** The reader is at fault. `read_str` finds #101 in the `Constant` traverse and reads it through `OpConstValue_v1.vi` (tools/bench/diag_c118_p0.py:33-41). That op may return an empty variant for any array constant, even one holding the right value. It was only shown on a scalar string here (diag_c118_p1.log:4).

**Discriminating test.** One scratch VI from `EMPTY_v0.vi`, about 15 s (the failed run took 15.4 s, diag_c118_p1.log:28):
1. Drop `Get Controls.vi` and create the names constant exactly as in diag_c118_p1.py:32-33.
2. Create an indicator on the constant's output terminal, run the scratch VI, and read the indicator with `GetControlValue`. This bypasses `OpConstValue_v1.vi`.
3. Read the same constant with `read_str`.

Outcomes:
- Indicator shows `Cam_pool00..19`, `read_str` shows the void bytes → reader defect; the write is fine and gate A1b needs a different reader.
- Indicator shows an empty array → the write path dropped the value; the fix belongs in how the array is handed to `Value`.

**Not checked.** I did not open the op VIs themselves, and tools/bench/diag_c118_p0.json was not searched for an earlier array-constant read that might already settle the reader question.

ROOT CAUSE: `create_const_loop_term` handed a Python list to the op's variant `Value` control, a route only proven for scalars, so constant #101 was created without the 20 strings while the uid/error oracle reported success.
TEST: In one scratch VI, create the same constant, wire it to an indicator, run, and compare the indicator's value with `read_str` on the same uid — a filled indicator blames the reader, an empty one blames the write.