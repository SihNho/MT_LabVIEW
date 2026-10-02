The Python list never reached the constant. I read the code and logs only and ran nothing, so this is inferred, not measured.

**What the evidence shows**
- `create_const_loop_term` passes `value` to the op VI's `"Value"` control with a bare `vi.SetControlValue(lab["value_ctl"], value)` (`tools/gscript.py:2823-2824`). It never checks the value afterwards.
- That control is the Variant "Value" terminal of `Terminal.Create Constant` (`tools/bench/build_op_const_loopterm_77.py:48-49,57`).
- The only value the verb was ever validated with is a scalar: an I32 N constant that read back `1` (`docs/NAMES.md:326-327`). A 20-element string array had never gone through this path before card 118-2.
- The create call itself returned `err ''`, `inv_err ''` and uid 101 (`diag_c118_p1.log:6-7`). So an invoke that succeeds with the value ignored is what you'd expect here.
- The read-back bytes are only 20 bytes long (`diag_c118_p1.log:8`). They are a flattened-variant header (`26008000`, the LV2026 stamp) followed by a near-empty body.
- 20 strings `Cam_pool00..19` would have to appear in the bytes, but none do. This looks like the default, empty value of the sink-typed `Control Names` constant.
- The reader works. The same `read_str` returned real content for P0's `Cam` constant at gate A0 (`diag_c118_p1.log:4`).

**Most plausible alternative**
The value was written but `read_str` read the wrong constant. It picks the constant by position in the `Constant` traverse via `order.index(uid)` (`diag_c118_p0.py:33-38`). That order may not match creation order, or the donor has other constants.

**Cheapest discriminating test**
On the scratch donor, create two names constants on the same input. Create one with `value=None` and one with `value=NAMES`, then read both back with `P0M.read_str`.
- If the two hex strings are identical to `2600800000000001000400000001000000000000`, the value is dropped on the write path. The reader is then not at fault.
- If they differ, or the `value=NAMES` one carries the strings, the problem is in reading or in which constant was selected.

As a free cross-check, `read_num` on the I32 constant 214 (created with `value=20`) should show whether the value path works for scalars.

ROOT CAUSE: The 20-string Python list passed as `value` never reached the Create Constant "Value" variant, so a default empty sink-typed names constant was created; the invoke reported no error and the verb had only ever been validated with scalars.
TEST: On the same scratch donor, create one names constant with `value=None` and one with `value=NAMES`, read both with `read_str`, and see whether their hex is identical (value dropped on write) or different (reader or constant-selection problem).