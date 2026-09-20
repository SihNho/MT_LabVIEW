---
type: peer-review
status: historical
date: 2026-09-09
tags: [peer-review]
---

# clfn-create-crash-empty-paraminfo

- **agent:** codex
- **date:** 2026-09-09
- **outcome:** ANSWERED (141s)
- **why asked:** failed prediction: NI Create.vi with the wizard globals set was expected to create a configured CLFN; instead LabVIEW died (ACCESS_VIOLATION at 0) in every variant where Function Name was valid (A/B/C/E), survived only D (Path only).
- **verdict:** unverified

## Question

CONTEXT: LabVIEW 2026 (26.3.1f1 64-bit), VI Scripting. We call NI's import-wizard library VI resource\importtools\sharedlib\VI\Block Diagram\Call Library Node\Method\Create.vi from our own op VI (Diagram ref + position in -> CallLib Refnum out) to create a Call Library Function Node on a target VI whose front panel is open. Create.vi internally reads the wizard's functional globals VI\Block Diagram\Attribute\{Function Name, Path, Calling Convention, Reentrant, Parameter Info}.vi and Call Library Node\Attribute\Function Dec.vi and applies them to the new node.
OBSERVED: (1) with all globals EMPTY, Create.vi returns error 1077 (Function Name invalid) and LabVIEW survives. (1b) With ONLY Path set to our DLL: error dialog, a CallLibrary node exists afterwards, LabVIEW survives. (2) With Function Name='mt2_track_simple', Path=<our DLL>, Calling Convention=0 (C), Reentrant=TRUE set (Parameter Info global untouched = empty array; Function Dec untouched OR 'int32_t mt2_track_simple(void);'), LabVIEW dies within 0.3 s: the minidump shows ACCESS_VIOLATION read at address 0 in LabVIEW.exe+0x578A41 with GDI32 frames on the stack (a drawing routine); our DLL is NOT in the crashed process's module list. Three variants (basic 4 globals / +Function Dec / +Parameter Info explicitly set to empty) all crash identically.
OUR HYPOTHESIS: Create.vi applies the EMPTY Parameter Info array, leaving a CLFN with zero parameters (not even the 'return value' entry), and LabVIEW's node-drawing code dereferences NULL on redraw.
ALREADY RULED OUT: the Function Dec string (crash without it); two COM clients (single client); the DLL being loaded (absent from module list); Library Path alone (survives).
TASK: ATTACK this hypothesis. (a) Search NI forums / LAVA / labviewwiki for the import-wizard scripting VIs (sharedlib importtools 'Parameter Info', 'Create.vi', 'CallLib Refnum') and for CLFN VI-Scripting crashes when Parameter Info / parameters are set to an empty array; (b) what is the minimal valid Parameter Info array - is a 'return value' entry mandatory as the first element (Parameter Type Void)? (c) in the import wizard's own flow, which globals are set BEFORE Create.vi is called, and is Create.vi ever called with an empty Parameter Info? You may read docs/gpu-backend.md (section 'Plan: scripted CLFN configuration') and archive/peer/2026-09-09-clfn-*.md. Give alternative causes and, for each, the cheapest discriminating test. Cite URLs.

## Answer

The hypothesis is plausible and now has strong circumstantial support, but the evidence does not isolate ?쐚ero array elements??from a closely related known defect: writing `Parameter Info` can corrupt the return-parameter name/display state and node width. I found no published report specifically reproducing an empty-array `ParamInfo` crash.

### What the sources establish

- `CallLib:Parameter Info` is an array in which element 0 represents the function return value?봭ot the first ordinary argument. [LabVIEW Wiki: Parameter Info property](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)
- A newly configured CLFN has no ordinary parameters but still has a return type of `Void`. Thus ?쐍o C arguments??is represented by one return-value record, not by an empty parameter list. [Configuring the Call Library Function Node](https://documentation.help/Call-Library-Function-Node/Configuring_the_CLF_Node.html)
- LabVIEW?셲 error definitions distinguish an invalid return record from ordinary invalid parameters: error 1174 is ?쏧nvalid return parameter,??while 1177 says `Void` is valid only as the return type. [LabVIEW error-code list](https://labviewwiki.org/wiki/LabVIEW_Error_Code_Family)
- The exact NI import-wizard implementation has been discussed publicly. The reported sequence is to set `Path.vi`, `Parameter Info.vi`, `Reentrant.vi`, `Calling Convention.vi`, and `Function Name.vi`, then run `Call Library Node\Method\Create.vi`. [NI forum: CLFN scripting problems](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512)
- That same thread documents a real `Parameter Info` scripting bug: merely reading and rewriting the existing array blanks the return-value name, and the CLFN is drawn at the wrong width until its configuration dialog repairs it. The import wizard reportedly creates nodes showing the same missing-return-name behavior. [NI forum: CLFN scripting problems](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512)
- NI has acknowledged that these wizard implementation VIs reside under `resource\importtools\sharedlib`, but community discussion describes them as password-protected and undocumented internals rather than a supported API. [NI forum: Programmatic access to Import DLL Wizard](https://forums.ni.com/t5/LabVIEW/Programmatic-access-to-Import-DLL-Wizard/td-p/2997415)

That known return-name/width defect is unusually consistent with your GDI/drawing stack. It supports the general conclusion that malformed `Parameter Info` can poison CLFN display state, but it weakens the narrower claim that the null dereference must specifically be caused by ?쐍o return-value element.??
### Minimal valid `Parameter Info`

Structurally, the minimum is one element:

- Index 0: return value.
- For a genuine `void f(void)`: type `Void`; no ordinary parameter elements.
- For `int32_t mt2_track_simple(void)`: type `Numeric`, signed 32-bit, passed by value; no ordinary parameter elements.

A one-element `Void` array is useful as a structural crash test, but it is not the correct final declaration for `mt2_track_simple`. LabVIEW permits intentionally treating a non-void return as `Void` and discarding the result, so it should nevertheless form a valid CLFN. [Configuring the Call Library Function Node](https://documentation.help/Call-Library-Function-Node/Configuring_the_CLF_Node.html)

I would not hand-construct that cluster initially. `Parameter Info` returns only fields relevant to each parameter type, making incomplete/default-filled clusters a second source of ambiguity. [LabVIEW Wiki: Parameter Info property](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)

### Does the wizard call `Create.vi` with an empty array?

Probably not in its normal flow.

The public account says all five functional globals, including `Parameter Info`, are populated before `Create.vi`. Separately, the normal CLFN model always begins with a `Void` return record even when it has no arguments. Together, those facts strongly imply that the wizard supplies at least one `Parameter Info` element. [NI forum](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512), [CLFN configuration documentation](https://documentation.help/Call-Library-Function-Node/Configuring_the_CLF_Node.html)

That is still an inference, not proof of the LabVIEW 2026 implementation. The cheapest definitive evidence would be reporter output from the wizard?셲 caller showing the array immediately before `Create.vi`, or a trace of the FGV?셲 array length and element 0. I found no indexed source showing that internal diagram or any legitimate empty-array call path.

### Cheapest discriminating tests

Run these only through the manager?셲 existing single LabVIEW execution path.

1. **Empty array versus valid return record**

   Seed `Parameter Info` from a manually configured, harmless `void dummy(void)` CLFN by reading its `ParamInfo` and passing that exact one-element array to the FGV. Keep every other input identical.

   - Survives: strongly confirms the empty-array hypothesis.
   - Still crashes: the problem is broader than a missing return entry.

2. **Return-name corruption versus array length**

   Starting from the known-good one-element array, test the return record unchanged, then with only its parameter-name string emptied.

   - Only the empty-name case crashes: this is likely the known return-name/display bug becoming fatal in 26.3.1, not an array-length defect.
   - Both survive while zero elements crashes: specifically implicates missing element 0.

   The name-focused test is important because read/write of `ParamInfo` is already known to erase the return name and produce the wrong displayed width. [NI forum](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512)

3. **Hand-built cluster versus native cluster schema**

   Compare:

   - exact `ParamInfo` read from a valid manually configured node;
   - a hand-built supposedly equivalent cluster.

   If only the native copy survives, the cause is an invalid enum value, missing type-dependent field, or 2026 schema/default mismatch?봭ot array length.

4. **Does `Create.vi` write `ParamInfo` before dying?**

   Immediately after creation, but before any deliberate redraw operation, report the new node?셲 `Parameter Info`, `Input Terminals[]`, `Output Terminals[]`, and bounds.

   - Zero-length `ParamInfo` plus crash on first bounds/image/UI access supports the proposed drawing-null path.
   - A valid one-element array with a blank name or implausible bounds points to the known return-name/layout defect.
   - If the process dies before the property read, use a target whose diagram is not visible or defer panel updates, if your existing tooling exposes that safely.

5. **Separate `Reentrant` from `Parameter Info`**

   Repeat the empty-array case with `Reentrant=FALSE`, then repeat a valid one-element case with `TRUE`.

   - Crash follows empty array: parameter state.
   - Crash follows `TRUE`: `Create.vi` may be combining invalid node state with its `Any Thread?` write. The scripting property exists independently as `Any Thread?`. [CallLibrary class property list](https://labviewwiki.org/wiki/CallLibrary_class)

6. **Separate symbol configuration from DLL resolution**

   Use a deliberately nonexistent library path with the same function name and parameter arrays.

   - Empty array still crashes while one-element survives: neither export lookup nor DLL loading is required.
   - Both survive: the real DLL path may trigger path/export validation even if the module is not yet visible in the dump.

7. **Test repaint as trigger, not root cause**

   Create the same malformed node with its diagram hidden or with UI updates deferred, then query nonvisual properties before permitting redraw.

   - Creation succeeds until redraw: supports malformed internal state consumed by drawing.
   - It crashes without any visible diagram: GDI frames may be secondary cleanup/error-dialog rendering rather than the originating defect.

### Alternative explanations, ranked

1. **Known blank return-name/layout bug, now fatal in 26.3.1** ??High plausibility. Cheapest test: valid one-element array with nonempty versus empty return name. [NI forum](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512)

2. **Malformed hand-built parameter cluster** ??High plausibility if you are constructing the cluster rather than cloning one produced by LabVIEW. Cheapest test: copy `ParamInfo` verbatim from a valid CLFN. The property?셲 fields are type-dependent. [Parameter Info documentation](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)

3. **Unsupported use of private wizard internals** ??Moderate plausibility. The wizard VIs are undocumented implementation code, and their FGVs may require initialization performed by higher-level wizard pages. Cheapest test: capture all FGV values from one genuine wizard-generated zero-argument function immediately before creation and replay them exactly. [NI forum](https://forums.ni.com/t5/LabVIEW/Programmatic-access-to-Import-DLL-Wizard/td-p/2997415)

4. **`Reentrant`/calling-convention write applied while the node is structurally incomplete** ??Moderate-to-low. Cheapest test: factorial isolation of `Reentrant` with a known-good one-element return array.

5. **Error-dialog or redraw reentrancy rather than the CLFN renderer itself** ??Moderate-to-low. GDI frames identify where it died, not necessarily what corrupted the object. Cheapest test: hidden diagram/deferred UI and immediate property reporting.

Bottom line: treat an empty `Parameter Info` array as invalid and never send it. But the first decisive experiment should use an exact one-element array cloned from a healthy CLFN, followed by a return-name-only mutation. That distinguishes your proposed missing-return-entry bug from the already documented `ParamInfo` return-name/drawing defect with only two controlled runs.

## Sources

(extract from answer)

## What was done with it

Adopted: element 0 = return-value record, an empty Parameter Info array is never sent. Constructive test built as OpCLFNParams_v0 (tools/recipes/build_opclfnparams.py): the FGV is filled from flattened bytes BEFORE Create.vi (one-element Void return record first, then the fresh node's own Parameter Info is read back through OpCLFNBuild_v0's Get->Flatten as the LabVIEW-produced sample for the 14-entry array). The return-name/width bug (NI forum 4147512) is checked by reading Prototype after every Set.
