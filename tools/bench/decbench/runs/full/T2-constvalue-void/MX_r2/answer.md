The gate failed because its reader cannot read an array constant's value. The log does not show that the 20 names were lost.

**Why this is the cause**
- `read_str` runs `OpConstValue_v1`, which reads `Constant.Value` through the base `Constant` class (`tools/bench/diag_c118_p0.py:5,32-41`). The docs say it works on "STRING constants only" (`docs/toolkit-capabilities.md:63`). For any other kind of constant, that read returns an empty (void) value and no error (`docs/NAMES.md:1157-1162`).
- The constant sits on `Control Names`, which is a String[] input (`docs/NAMES.md:976-977`, `tools/bench/diag_c118_p1_plan.json:15`). So it is an array constant, not a string constant.
- The returned hex has a type code of `0000` (void), no data and 0 attributes (layout in `docs/NAMES.md:1153-1155`). If the reader had really read a String[] constant, the bytes would describe a string array even when the array was empty.
  - The reader returned exactly these 20 bytes for Boolean and numeric constants (`tools/bench/diag_constvalue_siblings.log:4-7,12`).
  - It returned them again for ring #13245 (`tools/bench/diag_c118_p0.json:457,465`).
  - The reader echoed uid 101 (`diag_c118_p1.log:8`), so it did read the right object.
  - The gate's check, `endswith(FLAT)` (`diag_c118_p1.py:21,39`), could never pass with this reader.

**Most plausible alternative: the list was never written**
- `create_const_loop_term` passes the raw Python list into the op VI's `Value` input (a variant) (`tools/gscript.py:2823-2824`). It returns only the new uid and the errors (`:2826-2834`), so success there does not prove the value landed.
- Only scalar values have been tested through this function (`docs/toolkit-capabilities.md:72`). An earlier build kept its String[] as a panel default instead (`tools/recipes/stage_replay_standins.py:4-6`).
- The same doc records another route that took its value as a variant and produced a constant with an empty value (`docs/toolkit-capabilities.md:71`). A String[] panel default set over COM also failed to persist once (`docs/m8-real-run-plan.md:239-243`).
- Because the reader returns the same void bytes whether or not the value is there, this log cannot rule the alternative out.

**Cheapest test that tells them apart**
1. Rerun only the donor step. The whole failing run took 15.4 s (`diag_c118_p1.log:28`).
2. After step A2 deletes Get Controls (`diag_c118_p1.py:40`), wire an indicator to the constant with the existing `create_indicator_nested` (`tools/gscript.py:3979-3982`).
3. Run the scratch donor VI. It contains only the constants, an empty For loop and the indicator, so it touches no instrument.
4. Read the indicator with `GetControlValue`, and call `read_str` on the same uid again.

This builds nothing new. The other option, a reader typed for array constants (`docs/NAMES.md:1164-1165`), would mean building a new op VI.

ROOT CAUSE: Gate A1b read a String[] constant with `read_str`/`OpConstValue_v1`, whose base-class `Constant.Value` read returns an empty (void) value for every non-string constant, so the 20 bytes are just that reader's standard empty result, not evidence that the names were lost.
TEST: Recreate the donor constant, wire an indicator to it, run the scratch donor VI and read the indicator: Cam_pool00..19 there (with `read_str` still empty) confirms the reader is the cause, while an empty array means the Python list never reached the constant.