---
type: peer-review
status: historical
date: 2026-09-09
tags: [peer-review]
---

# clfn-scripted-node-broken-with-arguments

- **agent:** codex
- **date:** 2026-09-09
- **outcome:** ANSWERED (144s)
- **why asked:** failed prediction: a scripted CLFN (NI Create.vi + Parameter Info) with any ARGUMENT record leaves the VI broken; return-only node fine; no attribute VI reports an error; no error-list readback available.
- **verdict:** unverified

## Question

CONTEXT: LabVIEW 2026 (26.3.1f1 64-bit), VI Scripting, driven from Python over ActiveX. We create a Call Library Function Node by script with NI's import-wizard library: fill the functional globals VI\Block Diagram\Attribute\{Parameter Info, Path, Function Name, Calling Convention, Reentrant}.vi, then Call Library Node\Method\Create.vi (diagram, position -> CallLib Refnum), then the Attribute VIs Library Path/Function Name/Calling Convention/Reentrant (Set), Parameter Info (Set, same array again), Parameter Terminals. The DLL is x64, exports plain C names (e.g. mt2_track_simple), lives at a path WITHOUT spaces in the file name.
OBSERVED (each on a fresh VI containing only the node, fresh LabVIEW): Parameter Info = [return value: Numeric I32 by value] -> VI ExecState 1 (runnable), 2 terminals. Parameter Info = [return value] + ANY ONE argument record (Numeric I32 by value / U64 by value / String C String Pointer / 1-D DBL array Array Data Pointer / U8 array ...) -> ExecState 0 (VI broken), 4 terminals, every attribute VI returns no error, and reading Parameter Info back returns our records (LabVIEW normalises Num Dimensions to 1 and the numeric type of strings to I32, and blanks the return value's name). Parameter Info cluster layout we send (decoded from the type descriptor): Parameter Name (string), Num Dimensions (I32), Parameter Type (U16: Numeric 0 Array 1 String 2 ... Void 9), Numeric Type (U16: I8 0 I16 1 I32 2 I64 3 U8 4 U16 5 U32 6 U64 7 SGL 8 DBL 9 PTR INT 10 PTR UINT 11), Param Passing (U16: By Value 0, Pointer To Value 1), Array Passing (U16: Array Data Pointer 0, Array Handle 1, Array Handle Pointer 2), String Passing (U16: C String Pointer 0 ...), Adapt Format (U16), ActiveX Types (U16), Const (unused) (bool), Minimum Size (string, "" = none). We cannot read the VI's error list yet (building an op for the private VI method Get Errors 0x452 in parallel).
QUESTION: why does a scripted CLFN with one or more ARGUMENTS leave the VI broken while the argument-less node is fine? Attack these candidates and rank them, with the cheapest discriminating test each: (1) argument terminals created by Parameter Info Set have no data type until something else runs (what? the CallLibrary method 'Type Only Param' 636D002? 'Prototype' 636D000? re-setting Function Name/Library Path AFTER Parameter Info? the 'Function Dec' string? the configuration dialog OK?) (2) a field value that LabVIEW rejects for arguments but not for the return value (e.g. Minimum Size "" for arrays/strings, Adapt Format, Num Dimensions 0 for scalars, Const) (3) an unwired scalar/array INPUT terminal of a CLFN being illegal when created by script (normally CLFN inputs are optional) (4) Error Checking Level 636D40E / Dynamic Library? 636D40A defaults left unset by the wizard path (5) anything in NI's own import wizard flow (resource\importtools\sharedlib) that runs AFTER Create.vi for nodes with parameters ??e.g. Method\Connect Terminals.vi, Create String / Create Array Element (are wired constants REQUIRED for scripted CLFN inputs?). Search NI forums, LAVA, labviewwiki (CallLibrary class pages, 'Parameter Info property', 'Type Only Param'), the import-wizard discussions. Cite URLs. You may read docs/gpu-backend.md (section 'Plan: scripted CLFN configuration' and the results below it) and archive/peer/2026-09-0*-clfn-*.md.

## Answer

The strongest explanation is that `Parameter Info (Set)` updates the CLFN?셲 stored metadata and grows the terminal pairs, but does not fully commit concrete terminal datatypes in this scripted/private-wizard path. The resulting terminals exist?봦ence 4 terminals?봟ut at least one is internally untyped, so the compiler breaks the VI. The fact that every argument category fails, while the identical zero-argument path is runnable, argues strongly for a generic terminal-finalization problem rather than an ABI-specific field error.

NI explicitly says that clicking **OK** in the normal configuration dialog both resizes the CLFN and ?쐓ets the terminals to the correct data types.??That is a distinct operation beyond merely storing parameter records. [NI Call Library Function Node reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/call-library-function-node.html)

## Ranked candidates

### 1. Argument terminal datatype/finalization never completes ??high probability

Evidence:

- The node grows from 2 to 4 terminals, proving `Parameter Info` affects topology.
- Every argument type fails, including the simplest I32-by-value case.
- Readback only proves the `ParamInfo` metadata was stored. It does not prove that the compiler-facing terminal datatype was installed.
- NI documents the normal dialog?셲 **OK** action as both resizing and assigning terminal datatypes. [NI reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/call-library-function-node.html)
- A documented scripting bug already shows that writing `Parameter Info` does not perform all the normalization/layout work performed by the dialog: it blanks the return parameter name, and opening the dialog and clicking OK repairs the state. [NI scripting-bug thread](https://forums.ni.com/t5/LabVIEW-2021-Public-Beta/BUG-s-Call-Library-Function-Node-Scripting-Problems/td-p/4147512)

Cheapest discriminating test:

1. Create the return+I32 node.
2. Obtain the argument?셲 left terminal.
3. Read its terminal type descriptor/type string and compare it with:
   - the return terminal;
   - an I32 terminal from a manually configured CLFN;
   - an ordinary I32 control terminal.

If the scripted argument terminal has an empty, invalid, or different type descriptor, this is essentially confirmed.

Even cheaper behavioral version: wire an I32 control/constant to the left argument terminal.

- If the wire is broken or rejected: terminal datatype was never committed.
- If the wire coerces/repairs the terminal and `ExecState` becomes 1: wiring supplied the missing datatype.
- If the wire is valid but `ExecState` remains 0: the cause lies elsewhere.

Best repair experiments, in order:

1. Open Configure and click OK without changing anything. If this alone repairs the VI, a missing internal ?쐁ommit configuration??operation is proven.
2. Repeat `Parameter Info (Set)` after all other attributes are final.
3. Re-set Function Name after `Parameter Info`.
4. Re-set Library Path last.
5. Re-set both Function Name and Library Path last.

I would test the normal dialog OK before invoking private method `636D002`.

`Prototype` (`636D000`) is documented as returning the prototype of the currently configured node, not applying or parsing one. [LabVIEW Wiki CallLibrary methods](https://labviewwiki.org/wiki/CallLibrary_class) Therefore reading it is an excellent diagnostic but unlikely to finalize the node.

`Type Only Param` (`636D002`) is listed as a private method with no published description or contract. [LabVIEW Wiki CallLibrary class](https://labviewwiki.org/wiki/CallLibrary_class) Its name is suggestive, but there is no public basis for assuming that it commits all parameter terminal types. Do not call it blindly on anything valuable. First report its connector names/types from a harmless reference node.

### 2. Hand-built records differ from a native LabVIEW record in a hidden or type-dependent way ??medium-high probability

The public property description says that only fields relevant to a parameter type are returned. That implies the apparent common cluster contains type-dependent semantics; byte-for-byte round-trip readback does not necessarily prove that every combination is compiler-valid. [LabVIEW Wiki Parameter Info](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)

However, a simple I32-by-value argument should require very few special fields. Since that also fails, candidates such as array `Minimum Size` cannot explain the full observation.

Cheapest decisive test:

- Manually configure a harmless `int32_t f(int32_t x)` CLFN.
- Read its entire native `Parameter Info`.
- Apply those exact flattened bytes to a fresh scripted node, changing nothing.
- Use the same DLL and function if possible.

Interpretation:

- Native record works, synthetic equivalent fails: hidden/default/schema mismatch.
- Native record also fails: generic scripting/finalization problem.
- Copying the entire configured donor node works while replaying its native `ParamInfo` fails: `ParamInfo` alone does not reproduce required internal state.

Within this candidate, test fields in this order:

1. `Num Dimensions`: use the exact native scalar value.
2. `Parameter Name`: use a nonempty `arg1`.
3. `Const`: clone the native value.
4. All irrelevant enum fields: clone native defaults rather than zeroing them.
5. `Minimum Size`: relevant primarily to arrays and strings, so it cannot explain the I32 case by itself.
6. `Adapt Format`: likewise unlikely to explain ordinary explicitly typed numeric arguments.

NI?셲 documented workflow for a basic I32 argument is simply to insert an argument and leave its I32-by-value defaults. [NI simple-DLL tutorial](https://forums.ni.com/t5/Developer-Center-Resources/Tutorial-Configuring-the-Call-Library-Function-Node-to-call-a/ta-p/3522246) That makes an exotic scalar-field requirement unlikely.

### 3. Unwired argument input is considered unusable because its datatype is unresolved ??medium probability as a symptom, low as the root cause

Unwired CLFN inputs are not categorically illegal in modern LabVIEW. Community reports state that LabVIEW can allocate default storage for an unwired argument when it can determine the parameter datatype from explicit CLFN configuration. [NI discussion](https://forums.ni.com/t5/LabVIEW/Do-I-need-to-give-all-the-controller-in-Call-library-Function/m-p/3862516)

Similarly, simple scalar output parameters can operate without wiring the corresponding left terminal because LabVIEW can allocate storage itself. [NI discussion](https://forums.ni.com/t5/LabVIEW/Make-sure-that-you-wire-all-inputs-and-outputs-of-your-Call/m-p/3273915)

Therefore candidate 3 in its strong form?붴쏿ll unwired CLFN inputs are illegal?앪봧s contradicted.

But it becomes plausible when combined with candidate 1:

> An unwired argument is legal only after the node has a concrete parameter datatype; your scripted terminal may lack one.

Cheapest test:

- Wire a correctly typed constant/control to the sole argument.
- Separately wire or leave unwired the right-side terminal.

If a left-side wire repairs the VI, compare terminal type descriptors before and after wiring. That distinguishes ?쐎rdinary required input??from ?쐗ire forced type propagation.??
### 4. Missing wizard post-creation `Connect Terminals` / Create String / Create Array Element ??medium-low probability

The public description of the import wizard says it generates wrapper VIs containing configured CLFNs. [NI Import Shared Library documentation](https://www.ni.com/docs/en-AS/bundle/labview/page/importing-functions-from-a-shared-library-file.html)

The likely role of VIs named `Connect Terminals`, `Create String`, and `Create Array Element` is to construct and wire the generated wrapper?셲 controls, indicators, and allocation scaffolding. That is an inference from their names and the wizard?셲 output; I found no public documentation of their connector contracts.

NI?셲 normal tutorial explicitly configures the CLFN first and then creates front-panel controls and indicators for its inputs and outputs. [NI simple-DLL tutorial](https://forums.ni.com/t5/Developer-Center-Resources/Tutorial-Configuring-the-Call-Library-Function-Node-to-call-a/ta-p/3522246) This suggests those creation/wiring steps are wrapper generation, not an intrinsic prerequisite for a valid CLFN.

Cheap test:

- For the I32 case, create and connect only an ordinary I32 control; do not run any wizard helper.
- If runnable, the helper is unnecessary.
- If only the wizard?셲 `Connect Terminals.vi` repairs it, inspect what else that VI changes besides wiring.
- Test string/array helpers only after scalar I32 works. They may be needed for buffer allocation in a runnable wrapper, but cannot explain why the scalar case is broken.

### 5. `Function Dec` is missing or stale ??low-medium probability

A stored C declaration might be part of the private wizard?셲 internal state, but public evidence says the actual CLFN prototype is determined from library/function/parameter configuration. NI describes function name plus number/types of arguments as the prototype. [NI DLL-access article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGZjCAO)

Also, `Prototype` is a read method, not a prototype setter. [LabVIEW Wiki](https://labviewwiki.org/wiki/CallLibrary_class)

Cheap test:

- Compare `Prototype` immediately after setting:
  - return-only;
  - return+I32;
  - native/manual return+I32.
- If the scripted node reports the correct C prototype but is broken, `Function Dec` text is probably not the missing piece.
- If it reports an incomplete or nonsensical prototype, replay the exact `Function Dec` produced by the genuine wizard flow before creation and again after `Parameter Info`.

### 6. `Dynamic Library?` or `Error Checking Level` defaults ??low probability

Both are genuine CLFN properties. `Dynamic Library?` is property `636D40A`; `Error Checking Level` is `636D40E`. [LabVIEW Wiki CallLibrary class](https://labviewwiki.org/wiki/CallLibrary_class)

They are poor fits because:

- The same defaults produce a runnable return-only node.
- Neither property is intrinsically dependent on argument count.
- A missing DLL or missing export can break the run arrow, but you have already shown the same library/function combination is accepted for the zero-argument declaration. NI documents missing library/function as a broken-arrow cause. [NI DLL-access article](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGZjCAO&l=en-US)

Cheap test:

- Read both properties from:
  - the runnable return-only scripted node;
  - the broken one-argument node;
  - a manually configured good node.
- If values match, eliminate this candidate.
- If they differ, clone the manual node?셲 values. Do not guess enum values.

## Recommended test order

1. Get the actual error-list text. This may immediately say ?쐀ad/unwired terminal??or ?쐇nvalid parameter.??2. On return+I32, inspect the argument terminal?셲 datatype.
3. Wire an I32 constant/control and recheck `ExecState`.
4. Open configuration and click OK without changes.
5. Replay exact native `ParamInfo` from a manually configured one-argument CLFN.
6. Copy the entire native CLFN node as a control.
7. Only then test attribute reordering, `Function Dec`, and private `Type Only Param`.
8. Compare `Dynamic Library?` and `Error Checking Level` last.

My current ranking is:

1. Terminal datatype not committed by scripted `Parameter Info (Set)`.
2. Synthetic `Parameter Info` differs from a native record in hidden/type-dependent state.
3. Unwired input exposes the missing datatype; unwiredness itself is not generally illegal.
4. A wizard post-create helper performs an undocumented finalization as a side effect.
5. Missing/stale `Function Dec` or attribute-order revalidation.
6. `Dynamic Library?` / error-checking defaults.

The single most informative cheap experiment is the I32 case with: terminal type report ??wire I32 constant ??type report again ??`ExecState`. The normal configuration-dialog OK test is the next strongest because NI explicitly identifies that action as the point where terminal datatypes are set.

## Sources

(extract from answer)

## What was done with it

Test #1 (wire a typed control to the argument's input terminal) run as tools/bench/clfn_wire_probe.py; the private VI method Get Errors (0x452) enabled via LabVIEW.ini tokens (backup archive/LabVIEW.ini.bak-2026-09-09-1300) and built as OpGetErrors_v0 to read the real error text. Results in tools/bench/diag_chain.log and docs/gpu-backend.md.
