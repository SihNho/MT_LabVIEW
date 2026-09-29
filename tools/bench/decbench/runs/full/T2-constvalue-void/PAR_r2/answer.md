**Answer:** gate A1b checked the reader, not the constant. `read_str` returns a void (empty, no-type) result for any constant that is not a plain string. So this run does not show whether the 20 names reached constant #101.

**What held up under checking**
- **The reader is class-blind.** It looks the node up in the generic `Constant` list and runs `OpConstValue_v1` with `Class Name "Constant"` (`tools/bench/diag_c118_p0.py:33-38`). `docs/NAMES.md:1157-1162` records that reading `Value` through a node built for the base `VI Server:Constant` class returns data only for a StringConstant. Numeric and Boolean constants come back void, with no error, and the fix is a property node built for the constant's most specific class.
- **These exact bytes are the reader's known "blind" answer.** The same 20 bytes, `2600800000000001000400000001000000000000`, come back from:
  - ring #13245 in P0 (`diag_c118_p0.json:369,457,465`)
  - four Booleans and a numeric (`diag_constvalue_siblings.log:4-7,12`)
  - #101 here (`diag_c118_p1.log:8`)

  The only read that has ever returned data is StringConstant #23583 (`diag_c118_p1.log:4`).
- **The void bytes cannot come from the write** (my own point, beyond the analysts'). The bytes decode to a type code of 0x0000 (`NAMES.md:1153-1155`). Constant #101 was created on a String[] input (`diag_c118_p1.py:33`), so it is a string array whatever it holds. Even an empty or default array would carry an array type in the read-back. Void therefore comes from the reader, not from a missing value.
- **The other explanation is still open, but it is not what this gate measured.** `create_const_loop_term` passes the Python list unchecked into the op's variant `Value` control (`gscript.py:2823-2824`). It treats "success" as a created uid plus no invoke error (`gscript.py:2807,2826-2834`). So a list that failed to convert into a String[] value would still report no error (`diag_c118_p1.log:6-7`).

**What I dropped**
- **Analyst 3's "void on a known array ⇒ write not implicated".** That overclaims. It shows the reader is blind, not that the write worked.
- **Analyst 1's citation of `allterms_bed_20260923.json:1609`.** I did not verify it.
- **Analyst 2's direct test as the "cheapest" one.** Re-reading #101 through a node built for its array class is the decisive test. But it needs a reader that does not exist yet, so it costs more.

**Cheapest test that separates the two causes:** run `read_str`, read-only, on a String[] constant that already exists and is known to be non-empty.
- **Void result:** the reader is blind to arrays, and A1b is a false gate. A later gate (B2b, `diag_c118_p1.py:7`) uses the same reader and should be expected to fail the same way. Whether the value landed then needs the array-typed reader (the `NAMES.md:1159-1162` pattern).
- **Real bytes:** the reader works on arrays, and the fault is the Python-list write in `create_const_loop_term`.

ROOT CAUSE: Gate A1b read the String[] constant #101 through `read_str`, whose `Value` node is built for the base `VI Server:Constant` class and returns this exact void (type 0x0000) result, without error, for every non-string constant (NAMES.md:1157-1162; same bytes as ring #13245 and the Booleans/numerics), so the gate failed on the reader's blind spot and never measured whether the 20 names were written.
TEST: Run `diag_c118_p0.read_str` read-only on an existing non-empty String[] constant: the same void bytes prove the reader is blind (A1b is a false gate; check #101 with an array-typed reader), while real bytes clear the reader and put the fault on `create_const_loop_term`'s Python-list `Value` write.