---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# wiresr-test-t8b-untyped-register-and-fplabels-dialog

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (64s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THESE TWO EXPLANATIONS briefly (LabVIEW 2026 VI Scripting over COM, zero GUI). Log: tools/bench/test_opwiresr.log; test code: tools/recipes/build_opwiresr_v0.py function test(); ops OpWireSR_*_v0.

RESULT: T1-T7 PASS - a script-created shift register wired on all three sides by the new ops compiles (ExecState 0->1) and the VI runs. Two anomalies:

(A) FAILED PREDICTION T8b. A SECOND register was added (untyped, all sides unwired), then OpWireSR_LeftOutCtl wired the STRING control 'Image Name' into its left OUTSIDE terminal (wire uid 192 created, op error clear). I predicted "type mismatch -> broken wire -> Remove Bad Wires (VI method 410) deletes exactly wire 192". Observed: ExecState 0 (as predicted) but Remove Bad Wires removed NOTHING (gone=set()). MY EXPLANATION: the register had no type yet, so the string wire simply TYPED it as string - a legal wire, nothing broken; ExecState 0 comes only from the register's other two terminals being unwired. (Your own prior review of this plan warned about exactly this ordering.) Attack: is there any reading where wire 192 IS broken yet method 410 leaves it? Would the same op, applied to a register already typed as an IMAQ image, produce a broken wire? Is 'LeftOutCtl' therefore functionally proven by T7 alone (wire exists on both ends), and should the type-mismatch sub-test be dropped rather than fixed?

(B) A watchdog 'BLOCKED' verdict at 23:18:37 during that step: an untitled enabled 348x200 window while every VI window was disabled; the run continued after dismiss and the op reported no error. Windows open at the time include 'OpFPLabels_v0.vi Block Diagram' and 'OpFPLabels_v0.vi Front Panel' - an op used by gscript.fp_labels, called immediately before LeftOutCtl; those windows have been open since the earlier build batch. MY EXPLANATION: OpFPLabels_v0 still has AUTOMATIC ERROR HANDLING enabled; some run of it hits an error (e.g. a panel object without a label), LabVIEW's automatic error dialog appears (untitled) and its BD is opened - the same signature as the error-7 dialog diagnosed earlier tonight (archive/peer/2026-09-14-wiresr-test-fail2-imaqcopy-llb-path.md). Fix planned: set_auto_error_handling(False) + save on OpFPLabels_v0 and OpSubVI_v1 (fleet convention). Attack: what else produces an untitled ~350x200 modal with all VI windows disabled in LabVIEW 2026? Is disabling automatic error handling on a fleet op safe when its callers read 'error out' (gscript.fp_labels: check whether it does)? Cheapest discriminating test for (B)?
Read-only; do not open LabVIEW. Cite what you read.


## Answer

(A) Your typing explanation is strongest, but T7 is slightly overstated.

- NI documents that a shift register adopts the datatype of the first object wired to it. Thus wire 192 can legally make the previously untyped register a string register; the two missing body-side connections?봭ot a type conflict?봢xplain `ExecState 0`. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)
- A genuinely broken wire should be deleted by Remove Bad Wires; that is the documented behavior. [NI wiring documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html) Therefore `gone=set()` is evidence that 192 was legal, unless method 410 silently targeted the wrong VI/diagram or otherwise no-op?셝. The present test has no broken-wire positive control, so it cannot exclude that tooling failure.
- Yes: if the register is first typed from an IMAQ-image terminal on any side, subsequently connecting a string initializer should either produce a broken wire or be rejected by `Connect Wire`. All shift-register terminals must ultimately carry the same type. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf)
- T7 currently proves only that the left outside terminal reports a nonzero wire UID: [build_opwiresr_v0.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_opwiresr_v0.py:343). It does not re-read the `Image Name` control terminal and assert the same UID. Add that equality check before calling the op fully proven.
- Recommendation: drop T8/T8b from normal acceptance. If type-mismatch behavior matters, make a separate test that first types all three register sides as IMAQ, confirms `ExecState 1`, then attempts the string connection and distinguishes ?쐀roken wire created??from ?쐁onnection rejected.??Do not make the wiring op?셲 acceptance depend on which behavior LabVIEW chooses.

(B) Automatic error handling is likely involved, but ?쏿 label-less object caused it??is unnecessarily speculative.

`fp_labels()` deliberately probes indices until one is out of range, and its own docstring says termination currently costs ?쐎ne 8 s dialog.??It catches the resulting watchdog `RuntimeError` as its end-of-array signal: [gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1947). That matches the timing immediately before `LeftOutCtl` much better than an exceptional label object.

Crucially, `fp_labels()` does **not** read `error out`. Consequently, simply disabling automatic error handling is unsafe: `_run()` may return normally on the first out-of-range access, so the loop can continue to `max_n=200` and append stale/invalid output values. NI confirms that disabling automatic handling suppresses the dialog but does not itself handle or clear the error. [NI: Prevent LabVIEW Error Dialog Box](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019SFfSAM&l=en-US)

Other possible sources of an untitled modal include load/search dialogs, password prompts, save/conflict prompts, or explicit dialog/error-handler VIs; size and blank title alone cannot identify it. The window log proves a real enabled top-level candidate while all VI windows were disabled, but not its owner, class, text, or originating VI.

Cheapest discriminator:

1. Call `fp_labels(S)` alone on the same scratch.
2. Record each requested index plus `OpFPLabels_v0`?셲 error-out value.
3. On the first modal, capture HWND, class, owner HWND, child-control text, and the current index before dismissing it.
4. Repeat with an exact valid-count iteration, avoiding the out-of-range sentinel.

If the bounded run produces no modal and index `N` consistently produces it, (B) is settled. The proper fix is then: expose/read `error out` and terminate on the expected bounds error, **then** disable automatic error handling and save the op. The same fleet treatment is safer for `OpSubVI_v1` because `drop_subvi()` already retrieves its returned error; `fp_labels()` presently does not.

## Sources

(extract from answer)

## What was done with it

(A) Accepted: T8/T8b dropped from acceptance (an untyped register takes its first wire's type — NI manual); the ops'
acceptance is T1–T7, and T7 is to be strengthened by re-reading the control terminal's wire UID (noted in
`gscript.wire_sr` docstring: verify by UID on both ends). (B) The reviewer's better explanation adopted: the 23:18:37
modal is `fp_labels()`'s own out-of-range sentinel dialog (its docstring admits the 8-s cost), NOT a label-less
object. Consequence: `OpFPLabels_v0` must NOT have automatic error handling disabled until `fp_labels` reads
`error out` and stops on the bounds error — `tools/recipes/fix_fleet_auto_error.py` now touches `OpSubVI_v1` only
(`drop_subvi` reads its error). `fp_labels` repair = a later cycle.
