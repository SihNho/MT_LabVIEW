---
type: peer-review
status: historical
date: 2026-09-09
tags: [peer-review, plan]
---

# clfn-build-op-plan

- **agent:** codex
- **date:** 2026-09-09
- **outcome:** ANSWERED (158s)
- **why asked:** devil's-advocate pass on the flatten/unflatten bridge for Parameter Info (COM cannot set cluster arrays).
- **verdict:** Approach endorsed; adopted the validation ladder: round-trip byte equality, read-back after Set, Prototype, Parameter Terminals count/types, save/reload check; enums flattened in their configured representation (U8/U16/U32) - read from the sample, never assumed.

## Question

Devil's-advocate review with citations. LabVIEW 2026 64-bit, VI Scripting, driven from Python over ActiveX by running op VIs. Plan to configure a Call Library Function Node fully by script: (a) NI's own import-wizard library resource\importtools\sharedlib\VI\Block Diagram\Call Library Node\ (Method\Create.vi: diagram + position -> typed CallLib refnum; Attribute\Library Path.vi, Function Name.vi, Calling Convention.vi, Reentrant.vi, Parameter Info.vi with an operation Get/Set ring; Parameter Terminals.vi) is used as the API; (b) because ActiveX SetControlValue cannot set an array-of-clusters control (verified: stays empty), the Parameter Info array is delivered as a FLATTENED STRING control and rebuilt inside the op with 'Unflatten From String' whose 'type' input is the array read back from the freshly created node; a 'Flatten To String' of that read-back gives the byte layout sample; (c) enum numeric values (Parameter Type: Numeric/Array/String/.../Void; Param Passing; Array Passing; String Passing; Numeric Type codes) are confirmed by reading the CallLibrary 'Prototype' method (636D000) after each Set. Questions: (1) Any known reason 'Unflatten From String' with a type taken from a VI-Scripting cluster array (contains enums) would fail, e.g. version/typedef issues, or the array's element type differing between Get and Set? (2) Is the CallLibrary 'Parameter Info' property known to require ALL fields consistent (e.g. Numeric Type must match Parameter Type) or does a bad combination silently break the node - how to detect (VI.ExecState, 'Prototype')? (3) LabVIEW flatten format for this cluster: are enums flattened as their representation size (U16 default for ring/enum constants?) and Booleans as one byte, strings as I32 length + bytes, big-endian - cite the NI 'flattened data' documentation. (4) Is there a simpler documented route: the wizard's higher-level 'VI\Block Diagram\Method\Create.vi' / 'VI Generator' that generates a whole wrapper VI from a header-parser function model - can it be driven without the UI (inputs are LabVIEW objects/refnums, likely not settable over ActiveX either)? (5) Risks of 'Run in any thread' (Reentrant.vi) for a DLL that spawns its own worker thread and uses CUDA. Cite sources; say what is verified vs inferred.

## Answer

Bottom line: the in-LabVIEW `Flatten ??string ??Unflatten` bridge is technically sound if both operations occur in the same LabVIEW 2026 installation and the `type` input is wired directly from the `Parameter Info` Get output. The larger risk is not enum flattening; it is relying on an undocumented, private import-wizard schema and treating `Prototype` or `ExecState` as complete validation.

1. Unflattening the `Parameter Info` array

I see no documented reason it should fail merely because the cluster contains enums. `Unflatten From String` returns exactly the static type and structure wired to its `type` terminal; nested arrays and strings retain their own size headers. [NI?셲 Unflatten documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/unflatten-from-string.html)

Important distinctions:

- The `type` input must be an ordinary LabVIEW value/wire, not the old flattened ?쐔ype string.??Your proposal satisfies this if the Get output is wired to `type`.
- Normal `Flatten To String` strips typedef wrappers. That generally helps: typedef identity should not prevent reconstruction when Get and Set expose the same underlying cluster layout. [NI?셲 Flatten documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/flatten-to-string.html)
- Enum labels are part of an enum?셲 LabVIEW type, but the flattened data contains its numeric value in the enum?셲 configured unsigned representation. Enum representations can be U8, U16, or U32; U16 is merely the default, not a guarantee for NI?셲 cluster. [NI enum documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MFtSAM&l=en-US)
- A ring is not an enum type. Its underlying representation may likewise be changed from the usual U16. [NI ring/enum representation note](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000001DeCbSAK)

The devil?셲-advocate failure modes are:

- `Parameter Info` Get and Set could use similar-looking but nonidentical private typedef revisions.
- NI could change the cluster field order, field types, enum representation, or semantic meaning in another LabVIEW release.
- The flattened string contains numerous NUL bytes. Confirm that the exact byte length survives Python ??ActiveX ??LabVIEW rather than trusting successful `SetControlValue`.
- A malformed array-length prefix could make unflattening consume too much or too little input.

Cheap acceptance test:

1. Get the fresh node?셲 array.
2. Flatten it.
3. Send that exact string through the Python/ActiveX route.
4. Record received byte length and preferably a digest inside the op.
5. Unflatten using the direct Get value as `type`.
6. Require no `error out`, empty `rest of binary string`, and equality between the original and reconstructed array.
7. Set it back, Get again, and require a second flattened-string byte comparison.

That validates transport, layout, enum representation, and Get/Set compatibility without manually decoding the cluster.

2. Consistency of `Parameter Info`

I found no public NI contract for the import-wizard `Attribute\Parameter Info.vi` cluster or its validity rules. Therefore, whether irrelevant fields are ignored, normalized, rejected, or leave a broken node is unverified.

NI?셲 public contract is only that a CLFN configuration must consistently describe the function?셲 parameter count, types, pointer/value semantics, return type, and calling convention. NI warns that a wrong calling convention can crash LabVIEW. [NI CLFN configuration guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGZjCAO&l=en-US)

Do not assume `Prototype` proves the whole cluster is valid:

- It probably proves that LabVIEW accepted enough of the configuration to render a prototype.
- It may omit inactive subfields. For example, `Numeric Type` might be ignored when `Parameter Type=String`.
- Two different internal combinations can plausibly render the same prototype.
- It cannot prove buffer sizes, ownership, pointer lifetime, or that the DLL ABI actually matches.

Likewise, `VI.ExecState != Bad` is necessary but insufficient. A syntactically valid CLFN can still crash or corrupt memory when called with a wrong ABI. NI documents error 1097 for an exception raised by external code, but native corruption need not become a recoverable LabVIEW error. [NI CLFN reference](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/call-library-function-node.html)

Recommended validation ladder:

- Require every attribute VI?셲 `error out` to be clean.
- Get `Parameter Info` back and compare every field with the requested canonical value.
- Check `Prototype`.
- Check the generated terminal count and terminal LabVIEW types using `Parameter Terminals.vi`.
- Require the wrapper VI not to be broken and obtain its broken-VI explanation, not only `ExecState`.
- Save, close, reload, and repeat Get/Prototype/terminal checks; this catches configurations that normalize on compilation or persistence.
- Finally call a deliberately harmless test export with known inputs, guarded by canaries around output buffers.

Use canonical defaults for inactive fields instead of arbitrary values. For example, even if `Numeric Type` is semantically irrelevant to a string parameter, populate it with the same default NI?셲 wizard produces.

Your enum-code method is good evidence, but `Prototype after Set` alone is slightly circular. Stronger evidence is:

- Start from wizard-created nodes representing every desired configuration.
- Read their complete `Parameter Info`.
- Diff one semantic change at a time.
- Set the inferred code into a fresh node.
- Require read-back equality, prototype equality, terminal-type equality, and save/reload stability.

3. Actual flattened representation

NI documents the following:

- Numeric data are flattened most-significant byte first?봟ig-endian by default. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)
- A Boolean is one byte in LabVIEW 5.0 and later; false is `00`, and the preferred true value is `01`. Boolean arrays also use one byte per element. [NI Unflatten documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/unflatten-from-string.html)
- A string is a big-endian 32-bit byte count followed immediately by those bytes. Thus `"ABC"` is `00 00 00 03 41 42 43`. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)
- An array begins with one big-endian 32-bit element count per dimension, followed by its elements.
- A cluster is simply the concatenation of its elements in cluster order; NI documents no general padding between ordinary cluster elements in flattened data. [NI Flattened Data](https://www.ni.com/docs/en-US/bundle/labview/page/flattened-data.html)

For enums: they flatten according to their actual U8/U16/U32 representation. U16 is the default for a normal enum constant, but you must measure the NI private cluster?셲 actual enum fields rather than assume U16. [NI enum representation documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019MFtSAM&l=en-US)

Because the outer object is an array, its first four bytes should be its element count. Strings nested inside each cluster always retain their own length prefix regardless of the top-level ?쐏repend array or string size???setting. [NI Flatten documentation](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/functions/flatten-to-string.html)

4. Higher-level wizard generator

The only route NI publicly documents is the interactive Import Shared Library wizard: provide a DLL and C/C++-compatible header, configure the wizard pages, and let it generate wrapper VIs and an `.lvlib`. NI documents no supported headless API for the internal `resource\importtools\sharedlib` VIs. [NI Import Shared Library Wizard documentation](https://www.ni.com/docs/en-US/bundle/labview/page/importing-functions-from-a-shared-library-file.html)

Therefore:

- `Method\Create.vi` and ?쏺I Generator??may be callable G code, but their installed presence does not make their connector pane or data model a supported API.
- Calling them directly from Python would likely reproduce the same COM marshalling problem for LabVIEW object references and private clusters.
- A LabVIEW op VI could hold all object/refnum wires internally and expose only paths, strings, scalars, and your flattened model to ActiveX. That is feasible in principle, but not simpler until the generator?셲 full input contract and side effects are understood.
- The high-level path also adds header-parser variability, generated-project behavior, naming rules, and overwrite behavior. NI explicitly says update mode can overwrite generated VIs and the project library. [NI wizard documentation](https://www.ni.com/docs/en-US/bundle/labview/page/importing-functions-from-a-shared-library-file.html)

For one known CUDA signature, the narrow node-attribute route is easier to characterize and verify. The high-level generator becomes attractive only if you need many header-derived wrappers and can freeze a tested LabVIEW-version-specific adapter around it.

5. ?쏳un in any thread??with a CUDA worker thread

?쏳un in any thread??is appropriate only when every exported DLL entry point that LabVIEW may call concurrently is thread-safe. NI says the UI-thread setting serializes calls for non-thread-safe libraries; enabling any-thread execution can otherwise produce instability or data corruption. [NI threading guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU000000A0bR0AS&l=en-US)

For your worker-thread architecture, the safest interpretation is:

- LabVIEW-facing entry points may run on arbitrary LabVIEW execution threads.
- Those entry points should only validate/copy arguments, enqueue a job under proper synchronization, wait for completion if the call is synchronous, and copy results back.
- All CUDA allocation, stream, cuFFT-plan use, kernel launch, synchronization, and shutdown should remain owned by the persistent worker unless explicitly designed for concurrent host access.
- Never retain pointers to LabVIEW-owned arrays or strings after the CLFN returns. Copy the required data or keep the call blocked until the worker has finished using it.
- Serialize initialization and destruction. Prevent shutdown/unload while jobs or CUDA callbacks remain active.
- Do not call `cudaDeviceReset()` casually. NVIDIA describes the primary context as process-shared and recommends resetting it only just before exit or for recovery from an unspecified launch failure. [CUDA Runtime API](https://docs.nvidia.com/cuda/cuda-runtime-api/group__CUDART__DRIVER.html)

One correction to the usual rationale: with the CUDA Runtime API, a dedicated worker is not required merely to keep a unique CUDA context alive. NVIDIA says the Runtime?셲 device primary context is shared among the application?셲 host threads. The worker is still valuable for serialization, resource ownership, predictable streams/plans, and avoiding races. [CUDA Programming Guide](https://docs.nvidia.com/cuda/cuda-programming-guide/02-basics/intro-to-cuda-cpp.html)

My verdict: proceed with the flattened-string bridge, but make byte-exact round-trip plus Get-after-Set/save-reload checks mandatory. Treat the importtools VIs, cluster layout, enum codes, and `Prototype` method as version-pinned internal behavior?봭ot a stable NI API.

## Sources

(extract from answer)

## What was done with it

Ladder written into the OpCLFNBuild recipe plan.
