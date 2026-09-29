The value was probably written, and the gate failed because of its reader. Gate A1b read constant #101 with `read_str`, which runs `OpConstValue_v1`. That reader only works on String constants, and a string-array constant is a different class. So the gate could not have seen the array.

**Evidence**
- `read_str` reads `Constant.Value` through the generic `Constant` class (`diag_c118_p0.py:32-41`). `docs/toolkit-capabilities.md:63` says this reader handles "STRING constants only." `docs/NAMES.md:1157-1162` records that the same read returns an empty (void) value with no error for numeric and Boolean constants, and that it works only when the read is built for the constant's exact class.
- The bytes A1b got, `26008000 00000001 0004 0000 0001 00000000`, decode as one type of code 0, which is void, and no data (layout in `docs/NAMES.md:1153-1155`). The same 20 bytes are logged as `VOID_HEX` (`diag_c105_const.py:4-5,24`), for Boolean and numeric constants (`diag_constvalue_siblings.log:4-7,12`), and for wired, non-empty ring #13245 in this same card's P0 (`diag_c118_p0.json:457,465`). The one String constant read correctly (`diag_c118_p0.json:447`).
- #101 is a 1D array of strings. LabVIEW gives that the class `ArrayConstant`, not `StringConstant` (e.g. `docs/wiki/subvi/D1_s1_copy.json:11339-11340`). So it falls in the reader's void case.
- A value that failed to write would still leave a constant typed by its input, which is an empty string array. Its flattened bytes would carry an array type (length 0), not type code 0. Void bytes therefore come from the reader, not from a missing value.
- B2b (`diag_c118_p1.py:96-99`) uses the same reader on the copied constant and would fail the same way.

**Most plausible alternative:** the list never reached the constant. `create_const_loop_term` passes the Python list over COM into the op's variant `Value` control (`gscript.py:2823-2824`, `opcreateconst_loopterm_labels.json:5`). That write path has never been read back (`docs/d1-build-plan.md:1084-1087`). Because the reader is blind to arrays, A1b says nothing either way about the value, so this alternative is still open.

**Cheapest test that separates them:** one read-only call of the existing op, with nothing built. Run `read_str` on an array constant that is already saved and known to be non-empty, e.g. `ArrayConstant` #6059 ("Axes to move") in `D1_s1_copy.vi` (`D1_s1_copy.json:11339-11340`).
- If it also returns the void bytes, the reader is blind to arrays and A1b is a false failure.
- If it returns flattened elements, the reader works on arrays, so #101 really lacks its value and the variant write is at fault.

Only in the first case would the value check still need a reader built for the `ArrayConstant` class, the same fix `docs/NAMES.md:1159-1162` describes for numeric constants.

ROOT CAUSE: Gate A1b read the string-array constant #101 with `OpConstValue_v1`, which reads through the generic `Constant` class and returns an empty void value for anything that is not a `StringConstant` (NAMES.md:1157-1162), so the 20-byte void result reflects the reader, not the constant's contents.
TEST: Run the same `read_str` on an existing, non-empty `ArrayConstant` (#6059 in `D1_s1_copy.vi`): void bytes confirm the reader is blind to arrays, while real elements would point to the Python-list-to-variant write in `create_const_loop_term` instead.