**Root cause: gate A1b measures with the wrong reader. The readback is the documented "void variant" signature, so the gate says nothing about whether the 20 names were written.**

**Evidence**

- The bytes `26008000 | 00000001 | 0004 0000 | 0001 | 0000…` parse, by the measured layout, as version, one type descriptor, a 4-byte descriptor with code `0x0000` (void), and no data (`docs/NAMES.md:1153-1155`, `diag_c118_p1.log:8`).
- An empty or wrongly filled string array would still carry an array/string descriptor; this carries none.
- `read_str` runs `OpConstValue_v1.vi` with `Class Name` = `"Constant"`, i.e. the generic-class read (`tools/bench/diag_c118_p0.py:36-39`).
- That read is recorded as returning the value for a StringConstant but an empty void variant, without error, for DigitalNumericConstant and BooleanConstant; the static class of the property node decides (`docs/NAMES.md:1157-1162`).
- The constant was created on a String-array input (`diag_c118_p1.py:33`), so it is not a plain StringConstant. That it is an array-class constant is my inference, not something the log records.
- `read_str` was only ever proven on the string constant #23583 (`diag_c118_p1.log:4`, `diag_c118_p0.py:109-110`).
- The read returned `err ''` (`diag_c118_p1.log:8`), matching the "void without error" behaviour.

**Most plausible alternative: the value was never written**

- `create_const_loop_term` passes `value` only through `SetControlValue(lab["value_ctl"], value)` (`tools/gscript.py:2823-2824`).
- That control is the one made on the Create Constant invoke's `Value` input (`tools/bench/build_op_const_loopterm_77.py:48-49,57`).
- Its success oracle is only the created uid and the invoke error (`tools/gscript.py:2807`), so `created_uid 101, err ''` (`diag_c118_p1.log:6-7`) does not prove content.
- A Python list of 20 strings could have been dropped on the way in, leaving a default constant.

Both can be true at once. But the A1b failure itself is explained by the reader alone: a void descriptor is what this reader returns for non-string classes whatever the content.

**Cheapest discriminating test**

A scratch-VI check, no rebuild of the op VIs:

1. In the same donor, call `read_str` on a string-array constant whose content is known independently of the writer (for example, one already saved in a VI).
2. Read #101 through a Value property node built for its most specific class, the `OpConstValueN_v0` practice (`docs/NAMES.md:1159-1165`).

Outcomes:

- Known-content constant also reads `…0004 0000…` and the typed read of #101 shows Cam_pool00..19: reader defect only.
- Typed read shows an array descriptor with zero elements: the writer dropped the value as well.

ROOT CAUSE: Gate A1b read an array-class constant through `read_str`'s generic `Constant`-class Value node, which returns an empty void variant without error for non-StringConstant classes, so the failing bytes reflect the reader and not the written value.
TEST: Read a known-content string-array constant with `read_str` and read #101 through a most-specific-class Value node; void on the known constant plus Cam_pool00..19 on the typed read confirms the reader, while an empty typed array indicates the writer dropped the value.