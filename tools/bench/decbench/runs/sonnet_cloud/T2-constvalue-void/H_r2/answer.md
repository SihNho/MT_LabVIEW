**Root cause:** the reader is what failed. `read_str` reads the value through a node cast to the base `VI Server:Constant` class, and that read comes back empty for any constant that isn't a plain string, which includes this array constant. There is no evidence the constant itself was created with the wrong value.

1. **The bytes we got are a flattened empty ("void") variant, not a value.** In the layout recorded at `docs/NAMES.md:1153-1156`, `26008000` is the LV2026 version, then one type descriptor of length 4 with type code `0000` (void), with no data after it. Nothing in it describes an array, not even an empty one.

2. **The reader is known to be blind here.** `read_str` sets `Class Name` = `"Constant"` on `OpConstValue_v1.vi` (`tools/bench/diag_c118_p0.py:36-38`). `docs/NAMES.md:1157-1163` records that `Constant.Value` read through a base `VI Server:Constant` cast "returns the value for a StringConstant but an EMPTY (void, TD 0x0000) variant for every DigitalNumericConstant, without error". It also says the class of the node used for the read decides the result. Constant #101 is a String[] array constant, not a StringConstant.

3. **This exact 20-byte value has shown up before as the reader's blind spot.** The same bytes came back for ring #13245, under both the RingConstant and Constant reads (`tools/bench/diag_c118_p0.json:457,465`). They also came back for 9 of 10 constants in `tools/bench/diag_c116b_props.json:3254-3320`, while the one string constant decoded (`:3290`). The P0 string constant decoded to `…0343616d` "Cam" (`diag_c118_p0.json:447`; gate A0 passed, `diag_c118_p1.log:4`).

4. **The write side shows no fault.** The `for_n` labels map `value_ctl` to `"Value"` (`tools/bench/opcreateconst_loopterm_labels.json`). So `create_const_loop_term` really passes the list through `SetControlValue` (`tools/gscript.py:2823-2824`), and both error outputs are empty (`diag_c118_p1.log:6-7`). The gate A1b at `diag_c118_p1.py:39` expects array bytes from a reader that can't produce them.

**Most plausible alternative:** COM delivered the Python list as a variant that `Create Constant` didn't accept, so #101 holds its default value. That default is an empty String[], not a filled one. If that were the case, a reader that can see arrays would return an array type descriptor with 0 elements. The void type can't tell the two cases apart, because the blind reader returns void either way.

**Cheapest discriminating test:** don't build anything new. Run `read_str` (unchanged) on a String[] constant that is known to be non-empty, in a graph that has already been measured.
- If it returns the same `2600…0004 0000 0001 …` void bytes, the reader is the cause and A1b is a false failure.
- If it decodes the strings, the reader can read arrays, and the fault is in the value write.

Either way, A1b needs a reader built for the constant's own class (the fix pattern in `NAMES.md:1159-1163`) before the gate can count.

ROOT CAUSE: A1b read String[] constant #101 through a node cast to the base `VI Server:Constant` class, which returns an empty (void) variant without error for any non-StringConstant (`docs/NAMES.md:1157-1163`), so the bytes say nothing about whether the names were written.
TEST: Run the unchanged `diag_c118_p0.read_str` on a String[] constant already known to hold strings: the same void hex convicts the reader, and decoded strings point instead at the `Value` write in `create_const_loop_term`.