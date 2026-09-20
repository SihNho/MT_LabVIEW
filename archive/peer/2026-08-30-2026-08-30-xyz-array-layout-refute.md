---
type: peer-review
status: historical
date: 2026-08-30
tags: [peer-review]
disposition: legacy
---

# 2026-08-30-xyz-array-layout-refute

- **agent:** codex
- **date:** 2026-08-30
- **outcome:** ANSWERED (96s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Attack an ASSUMPTION I am about to build on. Do NOT confirm it - try to break it.

ASSUMPTION UNDER ATTACK: 'In this project's bead-tracking code, the flat 1-D array called x,y,z array is INTERLEAVED PER BEAD - element order is x0,y0,z0, x1,y1,z1, x2,y2,z2, ... so bead i occupies elements 3i, 3i+1, 3i+2.'

WHY IT MATTERS: I plan to split that array OUTSIDE a parallel For Loop using Decimate 1D Array with 3 outputs, which distributes elements round-robin (out0 = elements 0,3,6..., out1 = 1,4,7..., out2 = 2,5,8...). If the array is instead BLOCKED ([all x][all y][all z]) or ordered any other way, Decimate silently produces wrong values with no error, and the refactor changes the computation - which is forbidden here.

WHAT TO DO: read the project directory (read-only) and find evidence for or against. Relevant places: MAIN_VI_MAP.md, ARCHITECTURE.md, STATUS.md, and any extracted VI strings, reports or notes under the project tree. Look for how x,y,z array is BUILT (the producer side) and how it is CONSUMED, and for the inverse operation on the output side (Interleave 1D Arrays vs Build Array vs Reshape). The producer's structure is the decisive evidence: an Interleave-style build or a per-bead Build Array of 3 elements inside a loop implies interleaved; an append of three whole arrays implies blocked.

NOTE: you cannot read .vi files - they are binary. Use only the markdown/text artefacts in the tree.

ALREADY RULED OUT: the array is not per-bead clusters (it is a flat numeric array); the four-fold kernel is called exactly once in the main VI; the kernel's per-bead inputs are separate scalars named 'starting x 1' / 'starting y 1'.

ANSWER WITH: (1) your verdict - interleaved, blocked, or UNDETERMINED from the available text; (2) the exact file and line evidence for it; (3) if UNDETERMINED, name the single cheapest check that would settle it; (4) any OTHER way this Decimate plan could silently produce wrong numbers - e.g. array length not a multiple of 3, unequal output lengths feeding auto-indexed tunnels (which take the MINIMUM length and would silently truncate the bead count), or a remainder/padding convention. Be adversarial about (4).

## Answer

Verdict: **UNDETERMINED from the available text.** Do not wire the Decimate plan yet.

The text contains a strong interleaving hint, but no decisive producer-side evidence.

Evidence:

- [PLAN_kernel_parallel.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/PLAN_kernel_parallel.md:132>) says the old one-fold kernel was visually inspected.
- [PLAN_kernel_parallel.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/PLAN_kernel_parallel.md:137>) reports an iteration-index calculation using a constant `3`, described as `i*3`, that ?쐗alks the flat x/y/z array three elements at a time.??- [PLAN_kernel_parallel.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/PLAN_kernel_parallel.md:157>) says the same array is updated in place with Replace Array Subset.

That supports a three-slot record per bead, but it does **not** establish:

- that offsets are specifically `3i=x`, `3i+1=y`, `3i+2=z`;
- whether `i*3` indexes the input, output, or only one coordinate;
- whether some offset, header, sentinel, or padding is involved;
- how the main VI originally constructs the array.

The contrary problem is that later files promote the inference into an unsupported fact:

- [STATUS.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:375>) simply declares ?쐘,y,z per bead interleaved.??- [STATUS.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:381>) calls Interleave the inverse operation, but this describes the planned replacement, not an observed existing producer.
- [PLAN_kernel_parallel.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/PLAN_kernel_parallel.md:273>) explicitly says the starting-X/Y derivation still needed checking and calls the presumed unbundle/index operation ?쐋ikely.??That undercuts treating the later assertion as proven.
- [MAIN_VI_MAP.md](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/MAIN_VI_MAP.md:135>) establishes only one kernel call site, not the input array?셲 construction.
- `ARCHITECTURE.md` and `strings_out.txt` contain no producer/layout evidence.

The single cheapest settling check is: **ask for one plain-text reporter/wiring trace starting at the main kernel call?셲 `x,y,z array` input and walking upstream to the node that constructs it**, including node type, input order, and upstream terminal labels. `Interleave 1D Arrays(x,y,z)` or per-bead `Build Array(x,y,z)` followed by concatenation would prove interleaving; concatenating three complete coordinate arrays would prove blocked layout.

Other silent-failure risks:

- **Length not divisible by three is data loss, not merely unequal output lengths.** Decimate returns equal-length outputs and drops excess trailing elements. With 3 outputs, lengths `3N+1` or `3N+2` can therefore discard valid-looking values without an error. For an input shorter than three elements, every output can be empty. [NI?셲 documented explanation](https://digital.ni.com/public.nsf/allkb/F9700E328CEB1DD986256DA70026C458)
- **The For Loop silently uses the shortest auto-indexed input.** Any mismatch among decimated X/Y, calibration clusters, and `Bead is good?` shortens the bead count with no explicit length error. [NI auto-indexing documentation](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000PAghSAG)
- A wired `N` or pack count can impose another smaller iteration limit; NI documents the effective count as the smallest applicable value. [NI arrays and loops documentation](https://www.ni.com/en/support/documentation/supplemental/08/labview-arrays-and-clusters-explained.html)
- Even if records are triplets, their order could be `x,z,y`, `z,x,y`, or another historical convention. The reported `i*3` alone cannot distinguish these.
- The array might reserve triplets for rejected beads while the calibration/good-bead arrays filter them differently. Equal lengths would not detect this semantic misalignment.
- The old remainder handler may maintain padded slots or pack-oriented ordering. Removing it could change which triplets correspond to real beads even when the total length is divisible by three.
- Rebuilding the output with Interleave is correct only if its inputs and terminal order match the old contract; NI defines it as interleaving corresponding elements in input-terminal order. [NI function reference](https://download.ni.com/support/manuals/321526a.pdf)
- Because input Z is currently unused by the proposed single-bead kernel, an incorrect third stream can remain invisible during tracking yet corrupt `x,y,z array out` or downstream state when the array is reconstructed.

Minimum guards before accepting the refactor: assert `length(xyz) mod 3 == 0`, assert `length(xyz)/3` equals every bead-indexed companion array and the intended bead count, and numerically compare the reconstructed flat output against the existing kernel.

## Sources

(extract from answer)

## What was done with it

(Claude fills in)
