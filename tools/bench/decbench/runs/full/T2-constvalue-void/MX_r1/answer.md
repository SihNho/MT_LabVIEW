**Root cause:** the check's reader was at fault, not the code that created the constant. `read_str` cannot see array constants, so A1b could never pass. Paths below are under `tools/bench/` unless noted.

**What the bytes mean.** Decoded with the documented layout (docs/NAMES.md:1153-1155), the hex is:
- `26008000`: version
- `00000001`: one type descriptor
- `0004 0000`: that descriptor, type code 0x0000, which means **void**
- `0001 0000`: type count and index
- no data, and `00000000` attributes

So this is an empty variant, not an empty array. An empty value still keeps its type: the empty StringConstant #6086 still read back with its string descriptor `4030` (diag_c116b_props.json:3290).

**Why it came back void.** `read_str` runs OpConstValue_v1 with Class Name `Constant` (diag_c118_p0.py:36-38). Read through that base class, `Constant.Value` returns void, with no error, for every class measured except StringConstant (docs/NAMES.md:1157-1162; docs/toolkit-capabilities.md:63, "STRING constants only"). #101 was created on a String[] input (diag_c118_p1_plan.json:15). This project's graph dumps list such constants as `ArrayConstant`, e.g. #6059 (graph_l2r1_saved_20260928.json:1). #101's own class is inferred, because it was never read back.

The same 20 bytes came back for:
- ring #13245 in P0 (diag_c118_p0.json:457)
- numeric constants (build_opconstvalue_v1c.log:44), Boolean constants (diag_constvalue_siblings.log:4) and VISA constants (diag_c105_const.log:25-27)
- ArrayConstant #6059, read through the same base-class op (diag_c116b_props.py:3,42; diag_c116b_props.json:3283-3284)

A wrong-object read is ruled out: the uid echo was 101 (diag_c118_p1.log:8), and the reader checks the Constant traverse first (diag_c118_p0.py:33-35). P1's prediction assumed the string reader also covers String[] (diag_c118_p1.py:6,38-39). B2b (:99) would fail the same way, and B2 (:93-95) would pass without proving anything, because void equals void.

**Most plausible alternative: `create_const_loop_term` dropped the Python list.** The list reaches the op's `Value` control only as a COM value (tools/gscript.py:2823-2824). The For-N value route has never been read back: result_77-2.json:7 lists it as not measured, and diag_c99b_bench.log:29 logs only the uid. A related variant route did create an empty constant (docs/toolkit-capabilities.md:71). Both causes could be true at once.

**How to tell them apart.** Read an ArrayConstant that our creation code did not make, using the same `read_str`:
- If the reader is the cause, it returns the same void.
- If the creation code is the cause, it returns a non-void array descriptor.

That read is already in the files: #6059 came back void. So the reader cause is confirmed without running LabVIEW.

The creation code is still unverified, and P1-3 copies #101. To check it: put an indicator on #101's output (`create_indicator`, tools/gscript.py:2771), run the donor VI once, and read it with `GetControlValue`. It should return the 20 names.

ROOT CAUSE: A1b read #101 with `read_str` (OpConstValue_v1 on the base `Constant` class), which returns a void variant with no error for every non-string constant, and #101 is a String[] array constant, so the check could not see what `create_const_loop_term` wrote.
TEST: Read an ArrayConstant not made by our code (R1's #6059) with the same `read_str`: the identical 20-byte void, already on file (diag_c116b_props.json:3283-3284), confirms the reader is blind, while a non-void array descriptor would put the blame on the creation code.