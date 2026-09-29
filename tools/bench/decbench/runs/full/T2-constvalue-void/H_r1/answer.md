The most likely cause is the reader, not the write. Gate A1b read an array constant through a generic `VI Server:Constant` value reader. On LabVIEW 2026 that reader returns an empty (void) variant for any constant that is not a `StringConstant`. So the 20 bytes say nothing about what constant #101 actually holds. I only read files for this; nothing was run.

**What the 20 bytes are.** The documented flattened-variant layout (`docs/NAMES.md:1153-1156`) decodes the returned hex exactly:
- `26008000` is the LV 2026 version.
- `00000001` means one type descriptor.
- `0004 0000` is that descriptor: length 4, type code 0x0000, which is void.
- `0001 0000` is the types-used count and index.
- There are no data bytes.
- `00000000` is the attribute count.

An empty `String[]` constant would still carry an array-of-string type descriptor. A void descriptor therefore means the property returned no value at all. It does not mean "empty list".

**Why the reader returns void.** `read_str` always casts to class `"Constant"` and runs `OpConstValue_v1.vi` (`tools/bench/diag_c118_p0.py:33-39`). `NAMES.md:1157-1165` records measurements of that route. It returns the value for a StringConstant but a void (TD 0x0000) variant, with no error, for numeric and Boolean constants. The fix recorded there is to read through a property node built for the object's most specific class. Gate A0 passed only because P0's #23583 is a string constant: its bytes end `…0343616d`, i.e. `Cam` (`diag_c118_p1.log:4`). The names constant on `Control Names` is a 1-D string array, most likely an `ArrayConstant`, so it hits the void case. The error field is empty, which matches that measured silent failure (`diag_c118_p1.log:8`).

**Most plausible alternative: the list never reached the constant.** `create_const_loop_term` writes `value` into the op's `Value` control (`tools/gscript.py:2823-2824`, label `"Value"` in `tools/bench/opcreateconst_loopterm_labels.json:5`). That control was made from the Create Constant invoke's Value input (`tools/bench/build_op_const_loopterm_77.py:48-49,57`). This route has only ever been checked with a scalar: a For-loop N of 1.0, read back as `'1'` (`build_op_const_loopterm_77.py:81,109`, `const_loopterm_77d.log:11`). A Python list passed over COM might arrive as an unusable variant and leave the constant empty. Even so, that would not produce a void descriptor. The constant takes its type from the sink, so an empty `String[]` would still read back with its array type.

**Cheapest test that separates the two:** read #101 again through a reader built for its own class, with no rebuild. Take its class from `report_all`, e.g. `ArrayConstant`, and add that class to `read_num`'s class loop, whose op is `OpConstValueN_v1` (`diag_c118_p0.py:46-54`). As a control, also run `read_str` on any existing, populated string-array constant.
- If the class-specific read shows the flattened Cam_pool00..19 and the control also comes back void, the reader was blind.
- If the class-specific read returns an array type with a count of 0, the COM value write is at fault.

ROOT CAUSE: Gate A1b read an array constant through the generic `VI Server:Constant` reader (`read_str`/`OpConstValue_v1`), which returns an error-free void variant for any non-string constant (`NAMES.md:1157-1165`), so the 20 bytes are an empty variant and say nothing about #101's contents.
TEST: Read #101 again through a reader built for its own class (`OpConstValueN_v1` with the class `report_all` gives, e.g. `ArrayConstant`), plus `read_str` on a known populated string-array constant as a control: Cam_pool00..19 bytes and a void control mean the reader was at fault, an empty typed array means the COM `Value` write was.