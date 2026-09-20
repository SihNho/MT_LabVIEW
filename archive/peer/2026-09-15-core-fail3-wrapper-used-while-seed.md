---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# core-fail3-wrapper-used-while-seed

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (56s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS DIAGNOSIS briefly (LabVIEW 2026 VI Scripting over COM). Log: tools/bench/build_track_v6_core.log run 3 (37/38): all wiring gates passed (three array tunnels flipped to IndexMode 0 with their inner wires preserved and re-read); then gscript.add_shift_reg(target, 0, y, class_name='ForLoop') raised "error 1055: Invoke Node in OpAddShiftReg_v0.vi".
MY DIAGNOSIS: a wrapper defect, not a LabVIEW finding. tools/gscript.py add_shift_reg() always runs OpAddShiftReg_v0 (the WhileLoop-seeded op, OP_ADD_SHIFT_REG) and only passes class_name into the op's 'Class Name' Traverse control - it never selects the ForLoop-seeded twin OpAddShiftRegF_v0 (built in cycle 3 with SR_SEED=For, labels tools/bench/opaddshiftregF_labels.json). The WhileLoop-typed seed feeding To More Specific Class rejects a ForLoop reference downstream with 1055 - the exact signature this project measured on 2026-09-14 (INDEX row 28, test_oploopcast.log T3). The same defect exists in wire_sr(): OpWireSR_* is used regardless of class_name; the F-family (OpWireSRF_*, tools/bench/opwiresrF_labels.json) is never selected. The cycle-3 functional test of the F-ops (row 39) used the recipe's own helpers (add_sr_for / run_op with OPFAM), which is why the wrappers' defect was not exercised.
FIX: add_shift_reg and wire_sr choose op file + labels json by class_name ('ForLoop' -> the F twins). Attack: (1) any alternative reading of 1055 here (e.g. the Invoke itself being the failing node rather than the TMSC seed - the message names 'Invoke Node')? (2) is the recipe's use of loop_cast(OP, 0, 'ForLoop') for the register index compatible with the F-op (loop_cast's ForLoop path uses OpLoopCast_v1 - same seed lineage)? (3) after the fix, what single readback proves the right op ran (the returned uid appears in loop_cast's shift_reg_uids)? Read-only; cite tools/gscript.py lines you read.


## Answer

The diagnosis is strong, but ?쐃xact signature??overstates the evidence.

1. Error 1055 means only that the Invoke Node received an invalid object reference; naming `Invoke Node` identifies where the invalid reference was consumed, not where it became invalid. Theoretically, traversal could return no object, the target reference could be invalidated, or TMSC could emit an invalid reference. [NI?셲 description](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L75SAE&l=en-US) supports that narrower interpretation. Also, the earlier T3 logged 1055 at downstream **Property Nodes**, whereas this failure names an **Invoke Node**, so it is the same invalid-ref mechanism, not literally the same signature. Still, the 37 preceding gates plus the deterministic class/op mismatch make the wrapper defect overwhelmingly likelier.

2. `loop_cast(OP, 0, "ForLoop")` is compatible. It selects `OpLoopCast_v1` for `ForLoop` when available and otherwise `OpLoopCast_v0`; it does not use the WhileLoop op ([gscript.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:422>), especially lines 444??52). Thus its TMSC seed has the correct ForLoop lineage. The recipe uses it correctly after creation ([build_track_v6_core.py](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:253>)).

3. Yes: the minimal readback is:
   ```python
   uid = add_shift_reg(...)
   regs = loop_cast(..., "ForLoop")["shift_reg_uids"]
   assert uid in regs
   ```
   That is exactly the existing gate at recipe lines 253??56. For protection against a stale retained UID or non-clean rerun, the stronger proof is `after_set == before_set | {uid}`, not membership alone.

The current file already implements the proposed fix:

- `add_shift_reg`: selects the F labels and `OpAddShiftRegF_v0` at [gscript.py lines 484??03](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:484>).
- `wire_sr`: selects the F label map and `OpWireSRF_*` family at [gscript.py lines 520??42](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:520>).

Verdict: accept the wrapper diagnosis, but describe 1055 as corroborating invalid-reference evidence?봭ot proof by itself that TMSC was the originating node.

## Sources

(extract from answer)

## What was done with it

Wrapper diagnosis accepted (`add_shift_reg` / `wire_sr` now select the F-ops and their label maps by
`class_name`); the wording is corrected here: 1055 is corroborating invalid-reference evidence at the Invoke, not
proof that the TMSC seed was the originating node. The register gate is strengthened as recommended to
`set(after) == set(before) | {uid}`. Rerun: `tools/bench/build_track_v6_core.log` (run 4).
