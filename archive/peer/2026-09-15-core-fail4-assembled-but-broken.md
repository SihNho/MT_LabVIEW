---
type: peer-review
status: historical
date: 2026-09-15
tags: [peer-review]
---

# core-fail4-assembled-but-broken

- **agent:** codex
- **date:** 2026-09-15
- **outcome:** ANSWERED (104s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS (LabVIEW 2026 VI Scripting over COM; rule 1a). Log: tools/bench/build_track_v6_core.log run 4 (57/58), script tools/recipes/build_track_v6_core.py (reviewed ...-cycle4-replay-core-recipe-v2.md and three follow-ups). The replay core assembled completely: head (loadcal, IMAQ Create, windows), 5 kernel controls from a temp instance, String[] Frame Paths, For loop, StrToPath/ReadFile/kernel inside, Frame Paths tunnel indexed (inner wire == StrToPath.string), all border wires as single non-indexed tunnels (three arrays flipped from auto-index to 0 with inner wires preserved), the two param controls via wire_control, three shift registers (Shift Registers[] == before + {uid} each), LeftOutCtl from the three controls (control terminals wired), LeftIn into the kernel inputs, exit_loop -> three auto-indexed output tunnels each paired one-to-one by the kernel output wire, RightIn branches (output wire uid unchanged), three indicators - and then ExecState 0 (broken). The VI was not saved; the process closed it.
Candidates: (a) a REQUIRED input of some node still unwired (kernel inputs wired: Image In, Array of cal clusters, cross size, both windows, 4 pack remainder, # of bead 4 packs, the three state inputs; ReadFile: Image, File Path; StrToPath: string - what else could be required? does PARALLEL_kernel_v3clean or IMAQ ReadFile have another required input - e.g. ReadFile 'error in'? no, optional); (b) a TYPE conflict from register cross-pairing: LeftOutCtl selects the control by Panel.Controls[] index taken from fp_labels order (tabbing order) - if that order differs from Panel.Controls[], a DBL[] control could be wired to the Boolean register (each register's type is then fixed by that first wire, and the later LeftIn/RightIn to the kernel's typed terminals would be broken while the 'terminal wired' gates still pass); (c) the auto-index flip on the three array tunnels left an inner wire that reports connected but is broken; (d) a register created with the LeftOutCtl wire landing on the RIGHT register's outside terminal (the readers for For loops are unavailable); (e) the output tunnels: exit_loop's tunnel type vs indicator; (f) the loader's 'file (use dialog)' after make_default (no).
Questions: (1) Rank (a)-(f). (2) The cheapest localiser with the fleet's readers: on ExecState 0, snapshot every Wire uid with the terminals that hold it (node_terms across diagrams, panel_wiring, tunnels), run 'Remove Bad Wires' (VI method 410), and report the wires that disappear - each is a broken wire; is that reliable, and does it also delete wires that are merely incomplete? Alternative: the VI.'Get Errors' method (private?), or Node 'Broken?' - do the fleet's readers expose it? (3) For (b): a cheap structural check that the LeftOutCtl went to the intended register: after LeftOutCtl on the DBL[] control, does connecting LeftIn to the kernel's DBL[] input succeed while ExecState is measured before/after... i.e. measure ExecState after EACH register's three wires and after each output tunnel, so the first transition to 'broken-for-a-new-reason' is localised? (ExecState is 0 throughout construction because inputs are missing - so instead: build the loop with ONLY ReadFile+kernel and all non-register wires, then verify ExecState==0 solely due to the 3 unwired state inputs by wiring them TEMPORARILY from the controls through plain tunnels (wire_control) -> ExecState 1 expected; then delete those three wires and do the registers - each register's completion should return ExecState to 1 only when all three are done.) Propose the minimal version. Read-only; cite what you read.


## Answer

The leading fault is almost certainly an unwired required input on `IMAQ Create`?봲pecifically `Image Name`. The recipe wires only `New Image`; it never supplies `Image Name`. Earlier successful builders explicitly exposed both `Image Name` and `File Path` (`tools/bench/timing_chain5.log`, `tools/bench/track_check.log`). NI describes the image name as identifying the allocated image buffer and requiring uniqueness, consistent with it being essential to image creation. [NI: Image Display Shows Incorrect Image](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAovSAG&l=en-US)

### 1. Ranking

1. **(a), specifically `IMAQ Create.Image Name` ??very high**
   - This is the only obvious difference from the earlier runnable image-read harnesses.
   - `IMAQ ReadFile.Image`, `File Path`, and the listed kernel inputs are wired.
   - `error in` is not the likely omission.
   - NI says an unwired required terminal makes the VI broken. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)

2. **(b) wrong control/register association ??moderate, but lower than proposed**
   - The general risk is real: an untyped shift register adopts the first connected type.
   - However, `fp_labels()` and `wire_sr(LeftOutCtl)` both traverse `Panel.Controls[]`; [gscript.py](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/tools/gscript.py) explicitly documents that common index space. This is not a `fp_labels`-versus-`Panel.Controls[]` mismatch unless one implementation has diverged from its documented construction.
   - Still verify by UID, because the present gate only proves that each named control became wired.

3. **(d) wrong shift-register side ??low-to-moderate**
   - Possible indexing/reader defect, but the For-loop register fleet passed the 1024-iteration functional test.
   - It should be checked by endpoint identity rather than inferred from ?쐁ontrol terminal wired.??
4. **(c) damaged wire after the auto-index flip ??low**
   - The standalone discriminator proved the String[] flip route runnable.
   - For all three array borders, the post-flip reader found `IndexMode == 0`, preserved inner wire UIDs, clean tunnel errors, and the expected sink wire.
   - Tunnels can change array/scalar type across a loop boundary, so this was a reasonable concern, but current evidence is against it. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

5. **(e) output tunnel/indicator mismatch ??very low**
   - The indicators were created from the already typed tunnels, and each kernel output was paired one-to-one with a distinct auto-indexed tunnel.
   - Scripted `Connect Wire` can create a broken wire, so this is not impossible, but the construction path strongly constrains the type. [NI Community: Scripting Create Array Indicator](https://forums.ni.com/t5/LabVIEW/scripting-create-array-indicator/m-p/3282674/highlight/true)

6. **(f) loader default ??essentially excluded**
   - A default-value issue can cause wrong runtime behavior, but it does not normally explain a compile-time broken VI.
   - The loader itself is a runnable subVI; its `file (use dialog)` value is not a required terminal of the caller.

### 2. Cheapest localizer

Before building a more elaborate localizer, wire an `Image Name` string constant/control to `IMAQ Create.Image Name` and check the final `ExecState`. I expect that alone to change `0 ??1`.

The proposed `Remove Bad Wires` differential is useful, but its result must be interpreted narrowly:

- A disappeared wire was broken or incomplete at the time of removal.
- It does **not** prove a datatype conflict specifically.
- It can remove a wire that is merely unfinished; NI explicitly cautions that Remove Broken Wires can remove wires that appear broken because construction is incomplete. [NI: Using Wires to Link Block Diagram Objects](https://www.ni.com/docs/en-AS/bundle/labview/page/using-wires-to-link-block-diagram-objects.html)
- One `Wire` object may contain multiple branches. Its disappearance identifies the affected wire tree, not necessarily the exact bad segment.
- An empty disappeared set does **not** clear the VI: an unwired required terminal or broken node leaves `ExecState == 0` without any bad wire to remove. That is likely what you have.

So the snapshot ??method 410 ??UID difference is a good two-way classifier:

- `gone != ??: investigate those endpoint sets.
- `gone == ??&& ExecState == 0`: prioritize required unwired inputs or broken nodes.

A better nondestructive wire test is `Wire.Broken?`?봳he project registry records exact property name `Broken?`, ID `6371004` in `docs/NAMES.md`. The generic fleet knows the property identity, but I did not find a ready wrapper that enumerates it for every wire. `node_terms`, `panel_wiring`, and `tunnels` report connection/wire fields; they do not expose a node-level `Broken?` verdict.

`VI.Get Errors` is not the cheap route here. `docs/toolkit-capabilities.md` records two failed attempts with method `452`: only reference/error terminals appeared, not error details. The method is private/hidden rather than a standard selectable VI method, and the community workaround depends on copying a prepared Invoke Node or enabling private scripting tokens. [NI Community: Error List in VI Scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/td-p/2263216/highlight/true)

### 3. Minimal staged discriminator

I would not implement the proposed full temporary-tunnel sequence first. Use this smaller sequence:

1. Build exactly through L4, including all ordinary kernel inputs.
2. Add an `Image Name` string control/constant and wire it to `IMAQ Create.Image Name`.
3. Temporarily wire the three state controls straight through three non-indexed input tunnels to the kernel state inputs.
4. Check `ExecState` immediately.
   - Expected: `1`.
   - If still `0`, run the bad-wire differential. If it removes nothing, inspect required terminals on `IMAQ Create`, `IMAQ ReadFile`, and the kernel.
5. Delete the three temporary state wire trees/tunnels and run method 410.
6. Add all three registers.
7. For each register, verify structural identity:
   - initializer control?셲 panel wire UID reaches that register?셲 left outside terminal;
   - left inside terminal?셲 wire UID equals the intended typed kernel input wire UID;
   - right inside terminal is a sink on the intended kernel output?셲 existing wire UID.
8. Check `ExecState` after each register is fully completed. It will normally remain `0` after registers 1 and 2 because other required state inputs are still absent; the meaningful transition is after register 3, which should return it to `1`.
9. Add output tunnels and indicators only after that `ExecState == 1` checkpoint; verify it remains `1` after each output.

If you need register-by-register type localization rather than simply locating the phase, use three tiny independent scratch builds: one tested register plus two temporary direct state tunnels. That produces an unambiguous `ExecState == 1` expectation for every individual register, but it is unnecessary unless the `Image Name` fix does not solve run 5.

## Sources

(extract from answer)

## What was done with it

Adopted (1): `IMAQ Create.Image Name` — a required input the recipe had never wired (HARNESS_compare exposed it as
a control) — is now a control made at H2 and set to `track_v6_core` at run time. The `Remove Bad Wires`
differential stays in the recipe as the reviewer's two-way classifier (a wire that vanishes = broken/incomplete
tree; an empty set with ExecState 0 = a required unwired terminal or a broken node). `Wire.Broken?` 6371004 is
recorded as the better non-destructive reader to build when next needed; `VI.Get Errors` (452) is not attempted
again. The staged temporary-tunnel discriminator is held in reserve for the case the `Image Name` fix does not
take ExecState to 1. Rerun: `tools/bench/build_track_v6_core.log` (run 5).
