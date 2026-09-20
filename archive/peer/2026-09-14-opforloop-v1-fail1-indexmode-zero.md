---
type: peer-review
status: historical
date: 2026-09-14
tags: [peer-review]
---

# opforloop-v1-fail1-indexmode-zero

- **agent:** codex
- **date:** 2026-09-14
- **outcome:** ANSWERED (61s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK THESE TWO EXPLANATIONS (LabVIEW 2026 VI Scripting over COM, zero GUI; erdosmiller LV-Scripting 'Create For Loop.vi').
Log: tools/bench/cycle3_toolkit.log (item 1) / tools/recipes/build_opforloop_v1.py. OpForLoop_v1 = OpForLoop_v0 + the wire Get Controls.'Control Terminals' -> Create For Loop.'Inputs' (verified on both ends, ExecState 1, saved). Test on a scratch: a scalar BOOLEAN control brought in by copy_into; for_loop(tunnels=[that control], indexing=[True]) -> exactly ONE new LoopTunnel whose outer terminal carries the control terminal's wire (PASS) but the tunnel's IndexMode reads 0, predicted 1 (FAIL T3).
H1 - the test was ill-posed: a scalar Boolean cannot auto-index (auto-indexing needs an array), so Create For Loop.vi (or LabVIEW) silently created a plain tunnel; the flag is honoured only for array inputs. H2 - the op's 'Inputs Indexing?' front-panel control is not actually wired into the creator's 'Inputs Indexing?' terminal (the same class of defect as the missing 'Inputs' wire found in row 32), so the flag never reaches the library. A read-only census of the op's wiring is running (tools/bench/diag_opforloop_v1.log) and will show whether that terminal is wired.
Questions: (1) Does the erdosmiller creator (or the underlying LoopTunnel.IndexMode write) refuse/ignore indexing on a scalar-typed input, and is that documented (library doc, NI IndexMode property doc)? (2) If H2, what is the minimal repair? (3) Given the project also has a working set_index_mode(tunnel, 1) op (OpSetIndexMode_v0): is setting IndexMode=1 on a tunnel BEFORE its inner terminal is wired to anything safe (the earlier objection concerned retyping an already-wired inner terminal)? (4) The cheapest discriminating test between H1 and H2 (e.g. repeat with a 1-D string array control, which the fleet can create from Get Controls.'Control Names'). Read-only; do not open LabVIEW; cite what you read.


## Answer

H2 is ruled out by the census. H1 is the leading explanation, but the present test does not prove that the creator ?쐓ilently refuses??scalar indexing.

1. Scalar input and `IndexMode`

NI defines input auto-indexing specifically in terms of an **array** entering a loop: each iteration receives one array element, and an indexed array can determine the For Loop count. [NI: Auto-Indexing Tunnels](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)

The older NI manual is even more explicit: indexing maps 1-D array ??scalar, 2-D array ??1-D array, and so forth. It does not define indexing for an already-scalar input. [NI LabVIEW User Manual, ?쏛uto-Indexing Loops??(https://download.ni.com/support/manuals/320999e.pdf)

However, NI?셲 `LoopTunnel.IndexMode` documentation only says:

- `0` = Regular
- `1` = Auto Index
- read/write, not writable while running

It does **not** document a datatype error, refusal, coercion, or silent fallback when `1` is written on a scalar tunnel. [NI `LoopTunnel.IndexMode`](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/tunnel/looptunnel/indexmode.html)

Therefore:

- The Boolean test is ill-posed as a positive auto-indexing test.
- The observed `IndexMode=0` is consistent with H1.
- But the documentation does not establish whether erdosmiller explicitly filters it, LabVIEW normalizes the write, or the creator applies the mode before/after typing in a way that leaves it regular.
- The erdosmiller repository describes the package as a VI-Scripting code-generation library, but publishes no textual behavioral contract for this creator. [erdosmiller/lv-scripting](https://github.com/erdosmiller/lv-scripting)

Also, `ExecState=0` is not independent evidence that ?쐓calar indexing is illegal.??Once the tunnel remained regular, the For Loop still had neither a wired `N` nor an indexed array supplying its count. That alone explains the broken scratch VI.

2. H2 and minimal repair

The diagnostic shows:

- panel `Inputs Indexing?`: wire UID `1981`
- `Create For Loop.vi`.`Inputs Indexing?`: wire UID `1981`

So H2 is false for `OpForLoop_v1`: the flag reaches the creator.

If another copy actually had H2, the minimal repair would be exactly one wire:

```text
Inputs Indexing? FP terminal
    ??Create For Loop.vi / Inputs Indexing?
```

Then verify the identical nonzero wire UID at both terminals, `ExecState=1`, save the op, and test both `True` and `False` using an array input. No additional property node or wrapper change would be justified.

3. Setting `IndexMode=1` before wiring the inner terminal

This is the safer ordering, provided the **outer terminal is already typed as an array** and the inner terminal is still unwired.

Changing the mode then establishes the intended array?뭙lement boundary before anything inside depends on the tunnel?셲 type. It avoids the earlier hazard: changing an already-wired inner terminal from ?쐗hole array??to ?쐃lement??and thereby invalidating or retyping an existing downstream wire.

I would not call this unconditionally guaranteed by NI: the `IndexMode` page documents mutability but says nothing about ordering or automatic retyping. [NI `LoopTunnel.IndexMode`](https://www.ni.com/docs/ko-KR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/tunnel/looptunnel/indexmode.html)

Practical rule:

```text
wire array to outer terminal
??set IndexMode = 1
??verify readback = 1
??wire the now-element-typed inner terminal
```

Do not extrapolate safety to an untyped tunnel or to one whose inner terminal is already wired.

4. Cheapest discriminating test

Repeat the existing creator test with a genuine 1-D string-array control??Control Names` is an appropriate readily available specimen:

1. Create the For Loop with that control in `Inputs`.
2. Supply `Inputs Indexing? = True`.
3. Before wiring anything inside, verify:

   - exactly one new tunnel;
   - outer wire UID equals the array control-terminal wire UID;
   - `IndexMode == 1`;
   - the loop is executable without an `N` wire, assuming no other broken structure.

Then repeat with the same array and `Inputs Indexing? = False`; expect `IndexMode == 0` and an unwired `N` to leave the loop broken.

Interpretation:

- Array `True ??1`, `False ??0`: H1 confirmed operationally; creator flag works.
- Both yield `0`: not H2?봳he wire census already excludes it. Investigate the creator?셲 internal indexing-array construction/order.
- Direct `OpSetIndexMode_v0` changes the same array tunnel to `1`, while the creator leaves it `0`: defect is inside `Create For Loop.vi` or in how its indexing Boolean array aligns with its `Inputs` array.
- Direct setter also refuses/readbacks `0`: likely LabVIEW-side tunnel typing/state constraint.

The paired `True`/`False` run is stronger than a single array-positive test because it also detects input-array alignment or Boolean-array construction errors.

## Sources

(extract from answer)

## What was done with it

H2 was dead before the review arrived (census `tools/bench/diag_opforloop_v1.log`: `Inputs Indexing?` wire 1981 on
both ends). H1 accepted as the leading explanation with the reviewer's caveat that the scalar test proves nothing
positive. The op's test (`tools/recipes/build_opforloop_v1.py`) was rewritten around an ARRAY input — the String[]
control made by the assembly's own trick (Get Controls `Control Names` → control → cut) — with T4 ExecState 1 (an
indexed array alone gives N), T5 a 3-element run, T6 an empty-array run (zero iterations). Point 3 recorded in
NAMES.md: `set_index_mode(1)` is safe BEFORE the inner terminal is wired, on an array-typed outer terminal. Rerun:
`tools/bench/cycle3_toolkit.log` (run 2).
