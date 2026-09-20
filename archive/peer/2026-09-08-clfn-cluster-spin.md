---
type: peer-review
status: historical
date: 2026-09-08
tags: [peer-review]
---

# clfn-cluster-spin

- **agent:** codex
- **date:** 2026-09-08
- **outcome:** ANSWERED (98s)
- **why asked:** failed prediction (patch_gpu_harness.py: predicted 'wire, purge, save, smoke in seconds'; observed 14-min 100 %-CPU spin) — mandatory devil's-advocate pass before acting on the diagnosis
- **verdict:** H1 REFUTED by the machine (09:0x): the saved HARNESS_gpu.vi carries the cluster wire (CLFN t32 <- loader 'Array of cal clusters', wire 4329) and loads/compiles/runs in 28 ms; the spin therefore came from a later step of the batch (junk purge / save / DLL smoke), not from type propagation. The bypass (file-loaded calibration) is kept as a fallback only; the cluster route is the live one.

## Question

Devil's-advocate review of a diagnosis (attack it, do not confirm). Context: LabVIEW 2026 (64-bit), VI Scripting over COM. A Call Library Function Node (copied from a donor, 17 parameters all 'Adapt to Type', handles by pointer) sits on a harness diagram. Scripted step: erdosmiller-style Connect Wire from a subVI output of type 1-D array of clusters {I32, SGL, 1-D DBL array, 2-D DBL array, 2-D CDB array, 2-D DBL array, I32} into the CLFN parameter 'Array Cal Cluster' (adapt to type). The wire was reported created (wire count 36->37, op returned normally). Immediately after, LabVIEW went to 100 percent CPU on one core for 14+ minutes, no modal dialog, Front Panel window responding (2 s ping), every subsequent VI Server call from the client hung; killed. Afterwards the VI file on disk had 36 wires, ExecState runnable, so LabVIEW's Remove Bad Wires may have removed that wire as BAD before a save. Earlier the same session, an identical sequence WITHOUT that wire completed in seconds. Hypothesis H1: LabVIEW's type propagation/compile for an Adapt-to-Type CLFN parameter receiving an array of clusters containing arrays enters a very long or infinite loop. Alternatives: H2 the next scripted call (a Traverse-for-GObjects report or GObject delete) hung, not the wire; H3 the wire was rejected as a bad wire and the spin was the DLL call itself (the smoke run) receiving an empty array; H4 COM apartment/root-loop stall unrelated to the wire. Questions: (1) Is there documented/forum evidence that Adapt-to-Type CLFN parameters with nested-handle cluster arrays cause compile hangs or extreme compile times in LabVIEW 2020+? (2) What is the cheapest discriminating test between H1/H2/H3 that needs no GUI (all scripted, COM)? (3) The bypass: the DLL reads the calibration file itself (path passed in the C-string parameter), and the cluster parameter stays unwired (empty placeholder control). Any correctness risk in passing a path through a LabVIEW 'C String Pointer' parameter buffer and overwriting it with a shorter status string (buffer = the input string's length + NUL)? Search NI forums/docs; cite URLs. Already ruled out: no modal dialog (window enumeration); LabVIEW restarted clean afterwards.

## Answer

The evidence does not currently support H1 as a known LabVIEW defect. The wire is suspicious, but the diagnosis overstates what the observations establish.

1. Evidence for H1

I found no NI documentation or post-2020 NI forum report describing a compile/type-propagation hang specifically caused by wiring an array of clusters containing arrays into an Adapt-to-Type CLFN parameter.

What the sources do establish is:

- Adapt to Type intentionally supports clusters containing LabVIEW handles. NI?셲 generated example represents an array inside a cluster as a LabVIEW array handle and explicitly says LabVIEW passes handles to the DLL. That makes your datatype complicated, but not documented as unsupported or pathological. [NI: How Do I Use ?쏛dapt To Type??for CLFNs?](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019L0sSAE&l=en-US)
- NI community guidance says clusters containing arrays are non-flat; Adapt to Type passes their native LabVIEW handle representation and is suitable only when the DLL understands those LabVIEW-native structures. [NI Community: malloc to receive a struct](https://forums.ni.com/t5/LabVIEW/call-library-function-node-malloc-to-recieve-a-struct/m-p/731522)
- Arrays of clusters have been used with Adapt to Type and pointer-to-handle formats. Reported problems concern ABI layout, padding, and handle interpretation?봭ot compiler hangs. [NI Community: Passing an Array of Clusters](https://forums.ni.com/t5/LabVIEW/Passing-an-Array-of-Clusters-from-LabVIEW-to-a-DLL/td-p/1623538)
- Recent discussion still treats fixed arrays, nested dynamic arrays, and struct layout as interoperability hazards, rather than identifying a known compiler-loop defect. [NI Community: CLFN with C structs](https://forums.ni.com/t5/LabVIEW/Call-library-function-node-C-DLL-with-structs/m-p/4451808)

Therefore I would classify H1 as plausible but uncorroborated. The strongest counterargument is that `Connect Wire` returned successfully. Unless the call returned before a deferred compilation pass finished, that shifts suspicion toward the first subsequent call or execution.

The restored file having 36 wires is weak evidence for ?쏳emove Bad Wires removed it.??It is equally compatible with the new wire never being saved, the process being killed before persistence, or a later delete/report operation never completing.

2. Cheapest discriminating test

Use fresh LabVIEW processes and disposable generated VIs for each case. Record a timestamp immediately before and after every COM invocation in the client. Never combine the wire, traversal, deletion, and run in one opaque sequence.

Run this three-way test:

| Case | Script after constructing the common 36-wire harness | Interpretation |
|---|---|---|
| A | Connect only the calibration wire; make no traversal, delete, save, or Run call. From a watchdog process, sample LabVIEW CPU and attempt one cheap VI Server property read after a fixed delay. | One-core spin before any further scripted operation strongly favors H1. |
| B | Do not connect that wire; invoke exactly the suspected Traverse/report or delete operation. Do not run the VI. | A hang here favors H2. |
| C | Leave the calibration input unwired and invoke Run, with DLL-side entry/exit logging if already available. Do no traversal/delete first. | Entry into the DLL followed by a hang favors H3. No DLL entry points back toward compilation/VI Server. |

The most valuable first run is A. It removes both H2 and H3 simultaneously. Allowing a quiet interval before the property read matters: immediately issuing traversal again would obscure whether deferred compilation or traversal consumed the CPU.

For a still cheaper preliminary check, inspect the existing client log or add manager-side timestamps around each COM call. If `Connect Wire` has a recorded return time and the next call has no return, the statement ?쐔he wire operation hung??is not justified; at most, the wire may have triggered deferred work that caused the next call to block.

For C, DLL entry logging is much more discriminating than LabVIEW execution state. A CLFN blocks its LabVIEW execution thread until the native function returns, so a DLL that loops can make later automation calls appear frozen. [NI Community: LabVIEW execution threads and CLFN blocking](https://forums.ni.com/t5/LabVIEW/How-does-labview-use-memory-in-call-library-function-node/td-p/3672647)

3. C-string bypass risk

The bypass is safe only under a strict buffer contract.

LabVIEW converts a C String Pointer parameter to a null-terminated `char *`; LabVIEW strings themselves are not C strings. [NI: Converting a LabVIEW String for a CLFN](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YILoCAO&l=en-US)

If LabVIEW supplies exactly `path byte length + 1` bytes, overwriting it with a status string is memory-safe only when:

```text
encoded status byte length + 1 <= encoded path byte length + 1
```

and the DLL always writes the terminating NUL. ?쏶horter??must mean shorter in encoded bytes, not characters.

The risks are:

- A longer status overruns LabVIEW?셲 buffer and can corrupt memory. C provides the callee no inherent way to discover the allocation size. [NI Community: proper DLL string buffers](https://forums.ni.com/t5/LabVIEW/Call-Library-Node-Questions-proper-way-to-provide-buffer-to-DLL/td-p/4288421)
- Missing NUL termination can make LabVIEW scan beyond the allocation when converting the result back. NI notes that non-constant C-string parameters are scanned after return to determine their resulting length. [NI: string-transfer best practices](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA0VU0000000Jlp0AE&l=en-US)
- A short path provides a correspondingly tiny output buffer. NI?셲 guidance is to configure an explicit minimum size or pass a deliberately initialized buffer when the DLL produces output. [NI Community: allocate the result-string buffer](https://forums.ni.com/t5/LabVIEW/Call-library-function-node-input-issue/m-p/4007212/highlight/true)
- Embedded NULs cannot be represented in this interface. If arbitrary bytes are needed, NI recommends a U8 array/data pointer instead. [NI: C string versus byte-array pointer](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YILoCAO&l=en-US)
- The DLL must not retain the pointer after returning; it is a LabVIEW-managed call buffer, not persistent DLL-owned storage. This last point is an ABI inference rather than a statement I found explicitly documented.

My recommendation: keep the bypass, but do not rely on path length as output capacity. Either make the parameter input-only and return status separately, or configure/provide a fixed explicit buffer at least as large as the DLL?셲 documented maximum status plus NUL. Also verify whether the DLL expects ANSI/code-page bytes or UTF-8; ?쏞 String Pointer??alone does not establish the DLL?셲 pathname encoding.

Bottom line: H1 remains a useful experimental hypothesis, not a supported diagnosis. A wire-only replay in a fresh process is the cheapest decisive test; the unwired calibration bypass is reasonable, while reusing the path buffer for output is safe only with a proven byte-capacity and termination contract.

## Sources

(extract from answer)

## What was done with it

Kept both DLL entries (GPUTracking_auto dispatches: cluster route if the array is non-empty, else file route). C-string contract adopted from the review: the DLL writes at most 59 bytes + NUL (snprintf/strncpy bounded), the caller must pass >= 60 bytes (the timing script passes 64 spaces; the file route needs the >= 83-byte path anyway); path bytes are the system code page (fopen). Documented in docs/gpu-backend.md.
