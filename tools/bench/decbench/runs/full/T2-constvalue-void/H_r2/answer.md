The bytes that came back are an empty (void) variant. The most likely cause is the reader, not the constant. `read_str` reads every constant through the base `Constant` class, and that route returns nothing for any constant that is not a plain string. Constant #101 is a string array.

**What the bytes mean.** The project's measured layout for a flattened variant is: version `26008000`, then the number of type descriptors, the descriptors, the types-used list, the data, and an attribute count (docs/NAMES.md:1153-1155). Split that way, `26008000 | 00000001 | 0004 0000 | 0001 | 0000 | 00000000` (diag_c118_p1.log:8) is one type descriptor with type code 0x0000 (void), no data and no attributes. The value is not wrong or truncated; it is missing. An empty string array would still carry an array type descriptor, so this is not simply "the write set zero names".

**Why the reader is the likely cause.**
- `read_str` sends the uid to `OpConstValue_v1.vi` with `Class Name` = "Constant" (tools/bench/diag_c118_p0.py:32-41).
- toolkit-capabilities.md:63 limits that reader to **STRING constants only**.
- NAMES.md:1157-1162 records the same failure: reading `Constant.Value` through the base `Constant` class returns a void variant, with no error, for every numeric and Boolean constant. The fix there was a property node built for the constant's own class.
- The one reading that worked here, A0 (log:4), was on StringConstant #23583. The failing one is on an array constant: `Get Controls.vi`'s `Control Names` input is a string array, and the verb makes a constant of the sink's type (gscript.py:2797).
- The gate still ran and reported `err ''`, as the "without error" in NAMES.md:1158 predicts.

**The main alternative: the value was never written.** `create_const_loop_term` pushes a Python list into the op's `Value` control and returns only the new uid and the invoke error (gscript.py:2823-2835). It never reads the value back. Its earlier tests covered only a For loop's count terminal and a While loop's stop terminal (toolkit-capabilities.md:72). They show the constant being created and wired, not the value being stored. So `err ''` and uid 101 (log:6-7) are consistent with a constant that never received its value.

**Cheapest test that separates the two.** Build a ≤120-line scratch reader: a copy of the `OpConstValueN_v1` pattern whose `Value` property node is typed `VI Server:ArrayConstant`. The existing numeric reader can't be reused, because its typed node would reject an array constant with error 1055 (NAMES.md:1165). Run it once on donor #101 before anything is deleted.
- If it returns a string array holding the 20 names Cam_pool00..Cam_pool19, the constant is correct and only gate A1b's reader was wrong.
- If it returns an empty array or the wrong strings, the value write in `OpCreateConstTop_v0` failed.
- If it also returns a void variant, the read question is still open. The next check is to write one scalar string, "Cam_pool00", with the same function onto a string input and read it back with `read_str`.

ROOT CAUSE: Gate A1b read the string-array constant #101 through `OpConstValue_v1`'s base-`Constant` property node, which returns an empty (void) variant with no error for any constant that is not a scalar string (NAMES.md:1157-1162, toolkit-capabilities.md:63), so the 20-byte void it got says nothing about whether the names were written.
TEST: Read #101 once with a scratch reader whose `Value` property node is typed `VI Server:ArrayConstant` (the `OpConstValueN_v1` pattern); getting the 20 Cam_pool names back clears the writer and blames the reader, while an empty array or wrong strings means `create_const_loop_term`'s list-to-`Value` write never took effect.