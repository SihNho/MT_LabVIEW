---
type: peer-review
status: historical
date: 2026-09-08
tags: [peer-review]
---

# clfn-scripting-config

- **agent:** codex
- **date:** 2026-09-08
- **outcome:** ANSWERED (133s)
- **why asked:** the harness CLFN's parameter types are fixed to the donor's single-precision signature; before declaring 'not scriptable' (rule: external search is mandatory) - is the CLFN configuration reachable by VI Scripting?
- **verdict:** HYPOTHESIS, not yet verified on the machine (LabVIEW Wiki class dump): VI Server class CallLibrary (Generic>GObject>Node>GrowableFunction>CallLibrary), Parameter Info 636D409 R/W array of clusters, Library Path 636D400, Function Name 636D401, Dynamic Library? 636D40A. To verify: OpBuildPN with class 'VI Server:CallLibrary' + ID 636D409 read on HARNESS_gpu's node, dump the cluster typedef.

## Question

Factual API question, search NI docs and forums, cite URLs. LabVIEW 2026 (64-bit), VI Scripting enabled. Question 1: Can a Call Library Function Node's configuration (library path, function name, calling convention, and especially each PARAMETER's type: numeric type SGL/DBL, array dimensions, 'Adapt to Type', 'Array Data Pointer' vs 'Handle', string format) be read or changed PROGRAMMATICALLY through VI Server / VI Scripting - property nodes, invoke nodes, or any private/scripting class such as 'CallLibraryFunctionNode', 'CLFN', 'ExternalCall'? List every property/method you can find with evidence (NI docs, LabVIEW Wiki, LAVA/NI forum posts, VI Scripting class hierarchy dumps). Question 2: If not scriptable, is there any documented way to create a CLFN with a given parameter configuration by code, e.g. via 'New VI Object' + a .lvlib/.h import wizard (Import Shared Library wizard API), 'Create from Data Type', or the LabVIEW 'Call Library Function' JSON/XML in VI Snippets (rcpacini VI-Snippet)? Question 3: When a CLFN parameter is a 1-D or 2-D array of SGL passed as 'Array Handle', is it correct that LabVIEW passes the SGL data (4-byte floats) with no conversion, and that wiring a DBL array into that terminal inserts a coercion to SGL (precision loss) rather than breaking the wire? Already known: the node in question was copied from a 2013 lab DLL demo whose C header declares all arrays as float; VI Scripting has no obvious CLFN class in the public class hierarchy we dumped (Generic > GObject > Node > ... Function?).

## Answer

The premise is overturned: a CLFN is scriptable. The relevant VI Server class is named `CallLibrary`, not `CallLibraryFunctionNode`, `CLFN`, or `ExternalCall`.

The public class hierarchy is:

`Generic ??GObject ??Node ??GrowableFunction ??CallLibrary`

Its class ID is `16417`, and its scope is VI Scripting. [LabVIEW Wiki class dump](https://labviewwiki.org/wiki/CallLibrary_class)

## 1. Programmatic CLFN configuration

The `CallLibrary` class exposes these class-specific properties:

| ID | Property | Access | Purpose |
|---|---|---:|---|
| `636D400` | Library Path | R/W | DLL/shared-library path |
| `636D401` | Function Name | R/W | Exported function name |
| `636D402` | Calling Convention | R/W | `0` = C, `1` = stdcall/WINAPI |
| `636D403` | Any Thread? | R/W | Thread-safe/reentrant execution setting |
| `636D404` | Old Parameter Info | R/W, deprecated | Older parameter descriptor |
| `636D405` | Allow Preallocation | R/W | Preallocation setting |
| `636D406` | NI Validated | R/W | NI validation flag |
| `636D407` | Output Terminals[] | Read-only | Output parameter terminal references |
| `636D408` | Input Terminals[] | Read-only | Input parameter terminal references |
| `636D409` | Parameter Info | R/W | Complete parameter-description array |
| `636D40A` | Dynamic Library? | R/W | Dynamic-path-terminal mode |
| `636D40B` | Reserve Callback | R/W | Reserve callback name |
| `636D40C` | Unreserve Callback | R/W | Unreserve callback name |
| `636D40D` | Abort Callback | R/W | Abort callback name |
| `636D40E` | Error Checking Level | R/W | CLFN error-checking setting |

The class-specific methods are:

| ID | Method | Purpose |
|---|---|---|
| `636D000` | Prototype | Returns the current C prototype string |
| `636D001` | Create C File | Generates a C skeleton representing the configuration |
| `636D002` | Type Only Param | Undocumented in the available class dump |

This inventory and the IDs come from the published VI Server hierarchy dump. [CallLibrary class](https://labviewwiki.org/wiki/CallLibrary_class)

Most importantly, `Parameter Info` is explicitly:

- VI Scripting scope
- read/write
- an array of clusters
- one cluster per parameter, with element zero representing the return value
- capable of returning only fields relevant to each parameter kind

The documentation specifically names fields such as `Param Passing` and `Array Passing`. [Parameter Info property](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)

Therefore numeric representation, array dimensions and passing format, string format, and the distinction between numeric/array/string/Adapt-to-Type are represented by this property?셲 parameter descriptor?봭ot merely by the terminal types.

Caveats:

- It is not settable while the owning VI is running. [Parameter Info property](https://labviewwiki.org/wiki/CallLibrary_class/Parameter_Info_property)
- `Library Path`, `Function Name`, and `Calling Convention` are editor-time properties rather than run-time-engine properties. [CallLibrary class](https://labviewwiki.org/wiki/CallLibrary_class)
- Calling convention values documented by the class dump are `0` for C and `1` for stdcall/WINAPI. [Calling Convention property](https://labviewwiki.org/wiki/CallLibrary_class/Calling_Convention_property)
- `Old Parameter Info` is deprecated and should not be the basis of new automation. [Old Parameter Info property](https://labviewwiki.org/wiki/CallLibrary_class/Old_Parameter_Info_property)

I did not find a trustworthy text source enumerating the exact cluster element names, enum values, and nested types for every `Parameter Info` field. The cheapest conclusive check is for the manager to create a property node from a known `CallLibrary` reference, select `Parameter Info`, and inspect or report the resulting cluster typedef in LabVIEW 2026. Reading a known SGL-array CLFN and a known string CLFN would reveal the 2026 enum values safely.

The missing `CallLibrary` entry in your earlier hierarchy dump probably means the dump/filter was incomplete or did not include scripting classes. That is an inference; the externally published hierarchy explicitly contains the class.

## 2. Creating configured CLFNs

There are three realistic routes.

1. **Create/place a `CallLibrary` object, then write its properties.**  
   Once `New VI Object` returns the object reference, cast it to `CallLibrary` and write `Library Path`, `Function Name`, `Calling Convention`, and `Parameter Info`. NI previously published an example titled ?쏶cripting a Call Library Function Node Using LabVIEW,??corroborating that this workflow exists. [NI Community example](https://forums.ni.com/t5/Example-Code/Scripting-a-Call-Library-Function-Node-Using-LabVIEW/ta-p/3514624)

2. **Copy a configured template CLFN and overwrite the configuration.**  
   This is likely the most robust approach if creating the object by style is awkward. It avoids needing an undocumented style ID; `Parameter Info` can then be read or replaced.

3. **Use the Import Shared Library wizard interactively.**  
   NI documents the wizard as parsing a DLL/header and generating wrapper VIs inside an `.lvlib`. [NI wizard example](https://www.ni.com/docs/en-AS/bundle/labview/page/example-importing-functions-from-a-shared-library-file.html) NI?셲 current guidance says it converts supported C types into LabVIEW types and generates wrapper VIs. [NI DLL guidance](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019Ls1SAE)

I found no documented, supported programmatic API for driving that wizard. A forum investigation found internal, password-protected VIs under `resource\importtools\sharedlib`, but explicitly described them as undocumented. That is unsuitable as a stable LabVIEW 2026 API. [NI forum: programmatic wizard access](https://forums.ni.com/t5/LabVIEW/Programmatic-access-to-Import-DLL-Wizard/td-p/2997415)

VI Snippets are another template-copy mechanism, not a JSON/XML CLFN configuration API. The rcpacini project states that the PNG?셲 `niVI` chunk embeds a binary VI resource (`RSRC...`); it then uses VI Scripting and the clipboard to copy GObjects. [rcpacini/LabVIEW-VI-Snippet](https://github.com/rcpacini/LabVIEW-VI-Snippet) Thus a snippet can preserve an already-configured CLFN, but there is no exposed CLFN JSON/XML to edit.

I found no evidence that `Create from Data Type` can synthesize a CLFN prototype. Terminal creation/coercion is not equivalent to setting the CLFN?셲 ABI descriptor.

## 3. SGL arrays and Array Handle

Two separate statements are involved:

- **Element representation:** yes. If the CLFN parameter is configured as an array of `4-byte Single`, its payload elements are SGL/32-bit floats. NI?셲 external-code guide gives exactly that configuration and the resulting C prototype uses `float *`. [NI external-code manual copy](https://www.labviewforum.de/attachment.php?aid=2370)
- **Pointer shape:** an `Array Handle` does **not** pass a raw `float *`. It passes a pointer to a pointer whose target begins with one four-byte dimension value per dimension, followed by the data. `Array Data Pointer` is the setting that passes a pointer directly to the first array element. [CLFN configuration documentation](https://documentation.help/Call-Library-Function-Node/Configuring_the_CLF_Node.html)

Consequently:

- 1-D SGL Array Handle layout: handle ??dimension size ??SGL data.
- 2-D SGL Array Handle layout: handle ??two dimension sizes ??SGL data.
- The elements remain four-byte SGL; the handle/dimension header changes the ABI.
- A normal C declaration such as `float *a` expects **Array Data Pointer**, not Array Handle.
- A DLL designed for LabVIEW handles must declare/use the corresponding LabVIEW handle structure and memory-manager conventions.

For DBL wired to an SGL-array CLFN terminal: yes, ordinary LabVIEW numeric compatibility means the wire should remain valid and LabVIEW converts the array to the terminal?셲 SGL representation, usually showing a coercion dot. NI states that when terminals have different numeric types LabVIEW converts one representation to the other, and that coercing large arrays creates a converted copy. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999b.pdf), [NI Development Guidelines](https://download.ni.com/support/manuals/321393d.pdf)

That conversion loses precision when going from DBL to SGL. The DLL then receives SGL payload data?봭ot DBL bytes reinterpreted as SGL. For a large tracking array, it also implies a potentially significant temporary allocation and conversion cost.

Bottom line: inspect `Parameter Info` before assuming the inherited node?셲 ABI. If the C header says `float *`, the expected CLFN configuration is normally `Array ??4-byte Single ??correct dimensions ??Array Data Pointer`; `Array Handle` would be correct only if the DLL was specifically written for LabVIEW array handles.

## Sources

(extract from answer)

## What was done with it

Benchmark row 3 finished with the fixed-type DLL contract (integer x,y in via X Array, x,y,z out as 3 exact SGL integers). CallLibrary scripting queued as the route to a clean DBL-typed deliverable wrapper (docs/gpu-backend.md, docs/vi-server-ids.json).
