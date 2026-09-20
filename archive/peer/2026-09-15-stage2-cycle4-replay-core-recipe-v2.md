---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review, stage2]
---

# stage2-cycle4-replay-core-recipe-v2

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (149s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

RE-REVIEW (attack, do not confirm). LabVIEW 2026 VI Scripting over COM, zero GUI. tools/recipes/build_track_v6_core.py was REWRITTEN after your review archive/peer/2026-09-15-stage2-cycle4-replay-core-recipe.md; read the new file whole, and docs/stage2-assembly-step-b.md "Cycle-4 assembly notes". Changes: must() aborts on the first failed gate; phase D = a SCRATCH discriminator of the wire-then-index tunnel route with your readback (inner tunnel wire uid == StrToPath.string wire uid, IndexMode 1, ExecState 1, a 2-element run) before the assembly reuses the same routine; H3 snapshots the five control UIDs and requires them unchanged+unwired and SubVI -1 after deleting the temporary kernel; register indices are resolved by the UID add_shift_reg returned via loop_cast's Shift Registers[]; exit_loop makes three auto-indexed output tunnels (XYZ/GOOD/POS) each gated by "inner wire == that kernel output's wire"; each RightIn gated by "the kernel output's wire uid unchanged" (a branch shares the Wire object); phase T compares XYZ, GOOD and POS with the reference ff/good/pos, exact, for frames before the first lost bead, hard_timeout_s=600, phases timed, --n=200 first pass.
Attack: (1) any remaining unguarded assumption that could produce a plausible-but-wrong VI; (2) LeftOutCtl still selects the control by Panel.Controls[] index taken from fp_labels order - the only readback after it is "the control's terminal is wired"; is there a cheap stronger gate with the fleet's readers (panel_wiring gives control uid/terminal wire; the register readers are WhileLoop-only) - e.g. check that the control's wire uid appears nowhere else, or run the VI with distinctive initial values and read the first output row back (frame 0 uses the initial state)? (3) exit_loop with THREE output names on one call: does erdosmiller Exit For Loop create one auto-indexed tunnel per name in the given order, and is 'inner wire == output wire' enough to pair them? (4) the first-row trick for (2): with Frame Paths = [one frame], XYZ row 0 must equal the reference frame's ff given initial state xyz0 - propose it as the cheapest functional gate before the 200/10,043 run; (5) anything in phase T that could hang past 600 s or mis-marshal (2-D Boolean/I32 arrays over ActiveX). Read-only; cite what you read.


## Answer

Verdict: still not safe to run as the final 10,043-frame gate. I found four substantive gaps and several smaller hardening issues.

1. H3 does not enforce ?쐍o other UID lost.??
The recipe computes `lost`, then only prints its size; it never calls `must()` on it ([build_track_v6_core.py:191](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:191)). Thus the stated rewrite requirement is not implemented.

The clean gate is:

- Snapshot `base_uids` before dropping the temporary kernel.
- After creating the five controls and deleting the kernel, require the final GObject UID set to equal `base_uids ??five_control_uids`.
- Also retain the existing control-UID, unwired-terminal, and SubVI-count gates.

That avoids having to guess which kernel-owned wires should appear in `lost`.

2. `LeftOutCtl` remains structurally under-verified.

`LeftOutCtl` receives an index derived from `fp_labels`, then the only gate is that the intended control has some wire ([build_track_v6_core.py:227](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:227)). `panel_wiring` confirms only the control-side terminal and wire UID; it cannot identify the far endpoint ([gscript.py:613](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:613)).

?쏻ire UID appears nowhere else??is the wrong invariant: a valid wire must also appear at the left shift-register sink, and branches can legitimately expose the same Wire UID at more terminals.

The cheapest reliable substitute is exactly the proposed one-frame functional gate:

- Supply only the first reference frame.
- Set the normal reference initial state `xyz0`, all-good, and zero positions.
- Require one XYZ/GOOD/POS row.
- Compare that row exactly with the first reference `ff/good/pos`.

NI confirms that an auto-indexed input supplies successive array elements and an indexed output collects one value per iteration, so a one-element input produces the needed single-iteration observation: [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG).

Distinctive artificial initial values are less useful here: they have no archived expected result and may exercise unrelated kernel behavior. The normal initial state plus exact frame-0 reference is the stronger oracle.

However, add a two-frame exact gate immediately after it. Frame 0 tests the left initializers; frame 1 is the first cheap test of `RightIn` feedback.

3. The `RightIn` gate does not prove `RightIn` was connected.

After `wire_sr("RightIn", ...)`, the recipe merely checks that the kernel output terminal retained its old Wire UID ([build_track_v6_core.py:242](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:242)). A silently declined branch would pass that check unchanged.

This is the largest remaining plausible-wrong-VI route. Because the For-loop register readers are not proven available, the two-frame reference run is the cheapest decisive gate. One frame alone cannot test the right-side feedback.

4. Three-output `exit_loop` is acceptable, but the recipe should not claim more than it checks.

`exit_loop` explicitly passes all three names as one ordered array and checks that three tunnels were created ([gscript.py:1403](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1403)). The project has previously measured a three-name call producing three tunnels and wires, but I found no upstream erdosmiller documentation promising name-to-tunnel traversal order; the upstream project only describes the library generally: [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting).

Fortunately, this recipe does not rely on traversal order. Matching each tunnel through the kernel output Wire UID is the correct pairing mechanism. With three distinct kernel output wires and three one-inside-terminal tunnels, it establishes the pairing.

Still add these gates:

- Each of the three matched tunnel UIDs is distinct.
- Each matched tunnel has `IndexMode == 1`.
- Each output Wire UID matches exactly one new tunnel, not merely `any(...)`.

NI states that indexed output tunnels accumulate one element per iteration and produce an array sized to the iteration count: [NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG).

5. Phase D does not actually verify ?쐔wo iterations.??
It sets `["a", "b"]`, runs, then unconditionally records success if Run returned ([build_track_v6_core.py:160](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:160)). There is no observable output or iteration-count readback.

The structural discriminator?봊ndexMode 1, inner tunnel Wire UID equal to `StrToPath.string`, ExecState 1?봧s useful. Rename the final gate to ?쐒uns and returns with a two-element input,??or add an indexed output/counter and require two rows. NI documents that the indexed input normally determines the For-loop count, but this recipe currently does not observe that result directly: [NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG).

6. The promised exact-type register gate is absent.

The Cycle-4 document says B3 gains an exact DBL[]/Boolean[]/I32[] type gate ([stage2-assembly-step-b.md:43](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-b.md:43)); the recipe performs no datatype readback. ExecState catches incompatible wiring, but it is not the documented exact-type gate. Either implement that readback or correct the notes and rely explicitly on the one-/two-frame functional tests.

7. The 600-second timeout is not an absolute recipe bound.

`_run` raises after 600 seconds but leaves its daemon COM worker alive ([gscript.py:214](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:214)). `main()` then enters `finally` and calls `close_panel`, which initiates another COM call with its own 180-second cap ([gscript.py:1039](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py:1039)). With both `OP` and `SCR`, termination can extend well past 600 seconds and risks a second COM call while the timed-out Run is still alive.

On a Run timeout, skip all further COM cleanup and terminate the process immediately; let the outer supervisor handle recovery. The existing 45-minute `bgrun` ceiling prevents an infinite process, but it does not make Phase T a 600-second bound.

8. ActiveX marshaling looks acceptable for the 200-frame pass, but add explicit shape gates.

NI requires control names and datatypes to match for Control Value Set/Get: [NI VI Server guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MoeSAE). The current nested conversion will fail loudly if COM returns flattened scalar elements, which is good. Still require:

- `len(XYZ[i]) == len(ff)`
- `len(GOOD[i]) == len(good)`
- `len(POS[i]) == len(pos)`
- outer row counts equal `len(frames)`
- nonempty reference session and nonempty frame list before running

The current row-count gate checks only outer dimensions ([build_track_v6_core.py:284](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:284)).

One final operational trap: `--n` defaults to `0`, meaning the full fixture, not 200 ([build_track_v6_core.py:308](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/recipes/build_track_v6_core.py:308)). If ??00 first??is mandatory, default to 200 and require an explicit `--full` for 10,043.

Recommended gate sequence: structural build ??1 frame exact ??2 frames exact ??200 frames exact ??explicit full run. The one-frame test is worth adding, but the two-frame test is essential because it is the first functional discriminator for a silently missed `RightIn` branch.

## Sources

(extract from answer)

## What was done with it

All eight points applied to `tools/recipes/build_track_v6_core.py` before the first run: H3 gates "no
pre-existing UID lost" (plus the five control UIDs unchanged/unwired, SubVI −1); output tunnels paired one-to-one
by the kernel output's wire uid, distinct, IndexMode 1; phase D's gate renamed to what it observes; `--n` defaults
to 200 with `--full` explicit, and the gate sequence is 1 frame (initialisers) → 2 frames (`RightIn` feedback —
the reviewer's decisive functional gate for a silently declined branch) → N → full; row-width gates on
XYZ/GOOD/POS; a Run timeout exits the process without further COM calls. The doc's "exact-type gate" claim was
corrected to the functional gate. Run: `tools/bench/build_track_v6_core.log`.
