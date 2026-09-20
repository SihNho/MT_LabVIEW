---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review, stage2]
---

# stage2-step-b-revised-forloop-route

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (132s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THIS REVISED PLAN (it replaces the one you refused). Read docs/stage2-assembly-step-b.md section "REVISED route" and your review archive/peer/2026-09-14-stage2-step-b-replay-core-plan.md. LabVIEW 2026 VI Scripting over COM, zero GUI.
The replay core is now a FOR loop: (1) an auto-indexed input tunnel from a 1-D DBL 'Frame IDs' control sets N and yields frame id i (the fixture's 10,043 frame ids are NOT contiguous - 124 gaps - so a lookup array is required); the control is obtained by Terminal.Create Control on an array-typed kernel input ('Real-space cosine window', DBL[]) and then DELETING that wire so the control is free (the kernel input is wired from the windows VI afterwards); (2) 'FramePath.vi' = a small sub-VI built at top level from three primitives harvested by copy_into (Move-by-label) from claudeDev/background VIs_COPY/save N xyz traces.vi: Path To String -> Format Into String (donor instance has FIVE inputs 'input 1..5' and 'initial string') -> String To Path; controls made by Terminal.Create Control on 'path', 'format string', 'input 1' (base string) / 'input 2' (index); planned format string "%s\img%05d.tif" with inputs 3-5 left UNWIRED; connector pane by script; (3) OpForLoop_v1 = OpForLoop_v0 + the missing Get Controls.'Control Terminals' -> Create For Loop.'Inputs' wire; (4) the shift-register ops rebuilt with the ForLoop-typed seed (OpLoopCast_v1 donor) because the WhileLoop seed errors 1055 on a ForLoop ref; (5) the loop's parallelism stays OFF.
Attack: (a) Format Into String with a format-string CONTROL, 2 specifiers, 5 input terminals of which 3 are unwired and untyped after the copy: does the VI compile (broken arrow?) and what does LabVIEW do at run time - error 85? ignore extras? Cite NI's documented rules for specifier/input count mismatch and for unwired inputs. If unsafe, what is the minimal safe form (e.g. 5 specifiers with '%s' and unwired string inputs defaulting to empty)? (b) the 'create a control then delete its wire' trick to obtain a typed array control: does deleting the wire leave a properly typed free control, and is the control's datatype exactly DBL 1-D (rule 1a: the frame id becomes an integer index via %05d - any rounding risk for ids up to 11824 in DBL? none, but say so)? (c) a For loop with an auto-indexed DBL[] input AND non-indexed inputs, and an auto-indexed output of 'x,y,z array out' (DBL[] per iteration -> 2-D DBL): confirm the output type and that exit_loop's auto-indexed tunnel is the right primitive; (d) the kernel's three feedback registers on a For loop: identical semantics to the While version? (e) the one thing most likely to break: name it, and the cheapest discriminating test. Read-only; do not open LabVIEW. Cite what you read.


## Answer

Verdict: the For-loop architecture is sound, but `FramePath.vi` is not safe as specified. The five-argument `Format Into String` donor is the most likely failure.

The prompt?셲 design supersedes the checked-in ?쏳EVISED route,??which still describes contiguous Loop Counter indexing and `Build Path`; [docs/stage2-assembly-step-b.md](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/docs/stage2-assembly-step-b.md) must be updated before execution.

### (a) Five-input `Format Into String`

Do not leave the donor at five argument terminals with only two intended values.

NI documents these `Format Into String` errors:

- 81: format specifier type mismatch
- 83: more arguments than specifiers
- 84: more specifiers than arguments

When `format string` is a control rather than a constant, its value cannot be validated at compile time, so the VI may have a good arrow and then return a formatting error at runtime. This is not error 85; error 85 belongs to scanning/parsing failures. [NI Function and VI Reference Manual, Format Into String](https://download.ni.com/support/manuals/321526a.pdf), [NI error-85 explanation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019N4XSAU).

Thus `%s\img%05d.tif` plus five argument terminals risks error 83 if the three unused terminals remain arguments. Their being unwired does not establish that they disappear from the node?셲 argument list?봳he node explicitly has default-valued argument terminals.

The suggested workaround of adding three `%s` conversions is also unsafe:

- Unwired donor arguments are not proven to be string-typed or empty-valued.
- A `%s` paired with a numeric/default numeric argument can produce error 81.
- Even if made safe, it conceals an unnecessary and structurally incorrect arity.

Minimal safe form:

1. Use a donor already resized to exactly two arguments, or script the copied node down to two.
2. Wire `Path To String` output to argument 1.
3. Wire the scalar DBL frame ID to argument 2.
4. Use `%s\img%05d.tif`.
5. Wire or report `error out` during the test.

`%d` is valid for DBL input: NI says the numeric conversion codes, including `d`, accept any numeric G datatype, and `%d` rounds the argument. [NI format syntax](https://download.ni.com/support/manuals/321526a.pdf), [NI Community example showing `%d` rounding DBL](https://forums.ni.com/t5/LabVIEW/Question-regarding-Format-Specifier-Syntax/m-p/3214603).

There is no rounding risk for integral frame IDs through 11,824. Such small integers are represented exactly by DBL; `%d` therefore returns the same integer. If malformed fixture data could contain fractional IDs, add an explicit integral-value assertion rather than silently accepting `%d` rounding. LabVIEW uses nearest-even rounding for floating-to-integer conversion. [NI rounding rules](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P82kSAC).

One wording defect also needs resolution: `input 1` cannot simultaneously be a front-panel ?쐀ase string??control and receive the `Path To String` output. The clean connector pane is `path`, `format string`, and `index`; argument 1 is internal wiring.

### (b) Create-control/delete-wire trick

Conceptually, yes. Creating a control from a terminal creates a separate front-panel control of the terminal?셲 correct datatype and wires its diagram terminal to the source. Deleting only that wire should leave the control and terminal in place. [NI LabVIEW manual](https://download.ni.com/support/manuals/320999b.pdf).

If the source terminal is genuinely `Real-space cosine window: DBL[]`, the resulting control should be rank-1 DBL?봭ot merely ?쐓ome numeric array.??But that exact VI Scripting sequence is not established by the documentation alone. Gate it with a reporter after deletion:

- control still exists by UID
- class is Array
- rank is 1
- element representation is DBL
- terminal has zero connected wires

Do not identify it solely by its copied label, because it originates from an unrelated kernel input.

### (c) For-loop indexing and output type

This part is correct.

An auto-indexed `DBL[]` input supplies one scalar DBL per iteration. Non-indexed inputs pass their complete value unchanged into every iteration. If no explicit `N` is wired, the array length sets the iteration count; if `N` or another indexed array is also present, LabVIEW uses the smallest limiting size. [NI auto-indexing rules](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG).

An auto-indexed output that receives `x,y,z array out: DBL[]` each iteration accumulates those 1-D rows into a 2-D DBL array. NI explicitly describes the inverse-rank behavior: scalars accumulate into 1-D arrays and 1-D arrays into 2-D arrays. [NI LabVIEW User Manual](https://download.ni.com/support/manuals/320999e.pdf).

Therefore `exit_loop` is the right primitive only if its reporter proves that it created an indexing output tunnel rather than a last-value tunnel. Also test the orientation as `[frame, xyz-element]`, because the fixture comparison will depend on dimension order.

### (d) Feedback registers

Yes: initialized shift registers have the same inter-iteration semantics on For and While loops. The external initializer supplies iteration zero; each right-terminal value becomes the left-terminal value on the following iteration; after completion the final right value exits. NI expressly supports shift registers on both loop types and requires every connected value to have the same datatype. [NI shift-register manual](https://download.ni.com/support/manuals/320999e.pdf), [NI For-loop shift-register walkthrough](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YKYuCAO).

The semantic hazards are elsewhere:

- A zero-length `Frame IDs` array means zero kernel executions.
- All three register paths still need exact rank/representation gates.
- Parallelism must remain disabled because each iteration consumes the previous iteration?셲 state.

The ForLoop-typed scripting seed is a construction requirement demonstrated by the local 1055 result; it does not change runtime shift-register semantics.

### (e) Most likely break and cheapest test

The likeliest break is `FramePath.vi`?셲 copied five-argument `Format Into String`, specifically dynamic format validation and ambiguous unused argument terminals?봭ot the For loop.

Cheapest discriminating test: build only `FramePath.vi`, with no image I/O or kernel, and call it over COM for:

- `base = C:\fixture`
- IDs `0`, `1`, `9999`, `10000`, `11824`
- expected strings ending in `img00000.tif`, `img00001.tif`, `img09999.tif`, `img10000.tif`, and `img11824.tif`

For every call, read:

- resulting path converted back to string
- `error out` code/source
- execution state

Before running it, report that `Format Into String` has exactly two argument terminals and that argument 1 is string while argument 2 is DBL. This single test discriminates donor arity, `%d` handling, zero-padding, backslash construction, Path/String conversion, connector-pane assignment, and COM invocation without touching TIFFs or the kernel.

Finally, [the archived review](G:/Codes/LabVIEW_Codes/MinLab/zz_LabView%20VI/AAA_UNIST/2.%20Tracking/V6_ParallelLoop/archive/peer/2026-09-14-stage2-step-b-replay-core-plan.md) correctly killed the earlier parameterized-style and While-loop tunnel-mutation routes, but its conclusion that Loop Counter indexing was sufficient is invalidated by the newly stated 124 gaps. The lookup array is mandatory.

## Sources

(extract from answer)

## What was done with it

Accepted in full. (a) The five-argument donor is rejected: a copied `Format Into String` keeps its arity and a node's
terminal count is not scriptable, so the recipe now requires a donor instance with exactly ONE argument and uses
`initial string` ← base, format `\img%05d.tif`, argument = index (`tools/bench/census_fis_donors.log` selects it);
the test reads `error out` for ids 0, 1, 9999, 10000, 11824. (b) The create-control/delete-wire trick gets the
reviewer's gate (UID persists, rank 1, DBL, terminal unwired). (c)/(d) confirmed; `exit_loop`'s tunnel is checked
to be indexing, and the `XYZ` orientation `[frame, element]` is asserted before the diff. The plan doc's stale
"Loop Counter / Build Path" text was corrected (docs/stage2-assembly-step-b.md, REVISED route).
