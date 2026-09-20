---
type: narrative
status: historical
date: 2026-08-31
tags: [archive, kernel, plan]
---

# Plan — parallelize the tracking kernel

Detailed working plan for **one thread** of this project. [STATUS.md](STATUS.md) says whether this
thread is the one currently being worked; this file says *how* to work it. History and the reasoning
behind past decisions live in [WORKLOG.md](archive/WORKLOG.md).

## The ask

Rebuild `Track N beads four-fold over-kernel-v3.vi` so it gains the whole camera image once, then
processes each bead's ROI in a genuinely parallel For Loop, with each bead's result landing at its own
index (no cross-talk between iterations).

## What was found by opening the actual VI

Read-only, on a scratch copy — the original was never touched.

- The existing kernel's outer For Loop (iterating over `# of bead 4 packs`) **already has an `N`/`P`
  terminal pair on its border**. `P` is the "number of generated parallel loop instances" terminal,
  which only appears once "Configure Iteration Parallelism" has been enabled. It was observed
  **unwired** (hollow/light terminal style vs. `N`'s solid wired style) — so parallel infrastructure
  exists on this loop but nothing drives it, matching the user's observation that it runs sequentially.
- The "four-fold" grouping calls two different reentrant sub-kernels per pack:
  - **`Track 1 of N bds xyz-kernel-reentrant.vi`** — confirmed via connector-pane strings to be a
    **true single-bead** unit: every input/output is suffixed "1" only (`Calibration cluster 1`,
    `starting x 1`/`y 1`, `X/Y/Z pos 1`, `Bead 1 is good?`). Takes the whole `Image` in and crops its
    own ROI internally (via `rect coord from center.vi`). No coupling to any other bead.
  - **`Track 2 of N bds xyz-kernel-reentrant-v2.vi`** — confirmed to bundle **two beads into one
    call** (`Calibration cluster 1` *and* `2`, `X/Y pos 1` *and* `2`, `starting x/y 1` *and* `2` all
    present together). The user visually confirmed it tracks its two beads sequentially/coupled
    internally — likely the shared complex-FFT bandpass trick (packing 2 real bead profiles into one
    complex transform) common in diffraction tracking, though the exact wiring wasn't traced.

## Decision (user, 2026-08-25)

**Abandon the four-fold / Track-2 pairing as the basis for parallelization.** It is not a safe atomic
unit — a single call already entangles two beads' data. Instead build the new VI around
**`Track 1 of N bds xyz-kernel-reentrant.vi` only**, calling it once per bead inside a genuinely
parallel For Loop (one bead = one independent iteration).

## Progress 2026-08-26 (autonomous session)

### Step 1 is DONE — connector pane confirmed, no drift

Byte-level extraction of `Track 1 of N bds xyz-kernel-reentrant.vi` recovers exactly these labels:

```
image in · cross size · Calibration cluster 1 · starting x 1 · starting y 1
X pos 1 · Y pos 1 · Z pos 1 · Bead 1 is good · bead 1 z position · bead z pos as a cal
```

**Every input and output is suffixed "1" and nothing else** — this is a genuinely single-bead unit,
exactly as the decision above assumed. It takes the whole `image in` and crops its own ROI internally.
Safe to call once per bead in a parallel For Loop. (File mtime 2025-08-21, same as the four-fold
over-kernel and `Track 2`, so all three are the current generation.)

### NEW LEAD — 2010-era prior art for a generalised fold count

`zz_LabView VI\background VIs\` contains a whole **legacy family, all dated 2010-09-07**, that nobody
has looked at in this project:

| file | note |
|---|---|
| `Track N beads N-fold over-kernel.vi` | **an N-fold over-kernel already exists** - generalised fold count, which is conceptually what we want |
| `Track N beads 24-fold over-kernel-v3.vi` | 649 KB - fold count pushed to 24 |
| `Track N beads twelve-fold over-kernel-v4.vi` | 226 KB |
| `Track N beads one-fold over-kernel-v3.vi` | 13 KB - the degenerate case, likely the clearest to read |
| `Track N beads exactly four-fold over-kernel.vi`, `Track N beads 2x4-fold master.vi`, `Track N beads over-kernel-v2.vi` | other variants |
| `Track 1 of N bds N FOLD / 12 FOLD / for N-fold xyz-kernel-reentrant.vi` | matching reentrant kernels |
| `Replace array elements- 1 of N N-fold.vi` | helper for scattering results back by index |

**Why this matters:** somebody already solved "make the fold count a parameter". Before building a
parallel loop from scratch, **open `Track N beads one-fold over-kernel-v3.vi` first** (smallest, so
clearest) and then `Track N beads N-fold over-kernel.vi`, to see how they index beads and scatter
results. Even if the 2010 code is not reusable directly, its indexing scheme is a free design review.

**PREP DONE 2026-08-26:** the whole `background VIs` folder (94 files, 3.6 MB) is copied to
`user.lib\claudeDevackground VIs_COPY\`, so these can be opened without any risk to originals and
without the cascade of "Find the VI Named X" dialogs. The family is larger than first listed - it also
includes `Track four-fold 1-2-3-4 over-kernel.vi`, `Track four-fold remainder over-kernel.vi` and
`remainder and splitting for 2x4fold.vi`, which suggests the 2010 author had already solved the
**remainder problem** (bead counts that are not an exact multiple of the fold size) - worth reading,
since the new one-bead-per-iteration design makes that problem vanish entirely.

**Caveats:** these are 15 years old and NOT in the current active chain (the live trio is dated
2025-08-21). Their dependencies may not resolve — **copy the whole `background VIs` folder before
opening anything**, per the file-location gotcha below. Byte extraction returned no readable strings
from them (older internal format), so they must be opened to learn anything.

### The interface the new parallel kernel must preserve

Extracted from `Track N beads four-fold over-kernel-v3.vi` (2026-08-26). The replacement must keep
this connector pane so it drops into the main VI unchanged:

| direction | terminal |
|---|---|
| in | `Image In` |
| in | `Array of cal clusters` |
| in | `Bead is good? array in` |
| in | `x,y,z array` |
| in | `cross size` |
| in | `# of bead 4 packs` |
| in | `pos in cal image in` |
| out | `Bead is good? array out` |
| out | `x,y,z array out` |
| out | `pos in cal image out` |

It calls **exactly two** sub-VIs — `Track 1 of N bds xyz-kernel-reentrant.vi` and
`Track 2 of N bds xyz-kernel-reentrant-v2.vi` — confirming the four-fold structure described above.
The `Calibration cluster 1/2`, `X/Y pos 1/2`, `starting x/y 1/2` labels seen inside are `Track 2`'s
own terminals, consistent with it bundling two beads per call.

### DESIGN INSIGHT — don't wire `N` at all; auto-index the bead arrays

`# of bead 4 packs` is a **pack** count, and the new design is one bead per iteration, so the counts
no longer correspond. Rather than multiplying by four (fragile, and wrong the moment the bead count
is not a multiple of 4), **auto-index the For Loop over `Array of cal clusters`**.

A LabVIEW For Loop with an auto-indexed input tunnel derives its iteration count from the array
length automatically — **`N` does not need to be wired at all**, and the loop then runs exactly once
per bead by construction. Auto-index `Bead is good? array in` and `x,y,z array` the same way, and
auto-index all three outputs, so each bead's result lands at its own index with no manual bookkeeping
and no cross-talk.

This also sidesteps the dataflow trap noted in the `labview-automation` skill (nothing computed inside the
loop may feed its own `N`), because nothing is wired to `N` in the first place.

`# of bead 4 packs` stays on the connector pane for drop-in compatibility, but can simply be left
unused inside — or wired to a sanity check that the array lengths agree.

## BREAKTHROUGH 2026-08-26 — the design already exists, and we now know exactly why it is slow

`Track N beads one-fold over-kernel-v3.vi` (2010, opened from the safe copy) **is already the
one-bead-per-iteration architecture this plan set out to build.** Verified by opening its block diagram:

- A **single For Loop**, with **`N` wired directly from `# of bead`** — not from a pack count.
- Inside it, **exactly one call to `TRACK 1 of N XYZ`**, the reentrant single-bead kernel.
- Results scattered per bead by index; an `i`-driven index calculation (with a `3` constant, i.e.
  `i*3`) walks the flat x/y/z array three elements at a time.

Its connector pane: `# of bead`, `pos in cal image in`, `cross size`, `x,y,z array`,
`Array of cal clusters`, `Bead is good? array in`, `Cosine bandpass for Hilbert`,
`Real-space cosine window`, `Image In` -> `pos in cal image out`, `x,y,z array out`,
`Bead is good? array out`.

### THE ROOT CAUSE OF THE SEQUENTIAL BEHAVIOUR

Magnifying the loop's left border (6x) shows what the wires actually terminate in:

| terminal | border marker | meaning |
|---|---|---|
| `pos in cal image in` | blue **▼** | **shift register** |
| `x,y,z array` | orange **▼** | **shift register** |
| `Bead is good? array in` | green **▼** | **shift register** |
| `cross size` | blue solid square | plain (non-indexed) tunnel |
| `Array of cal clusters` | magenta solid square | plain (non-indexed) tunnel |

**The three result arrays are carried in shift registers and updated in place with Replace Array
Subset.** That is a genuine loop-carried dependency: iteration *k+1* consumes the array produced by
iteration *k*. LabVIEW therefore cannot run the iterations in parallel — and would be right to refuse.

This explains the observation that started the whole project (the kernel runs sequentially) at a level
the byte-extraction analysis could never reach. It also explains why the existing four-fold kernel's
For Loop has a `P` terminal present but **unwired**: parallelism was contemplated and could not be
enabled, because the shift registers forbid it.

### What this changes about the build

**Do not build a new loop from scratch.** Start from this VI's structure and make one focused change:

1. **Replace all three shift registers with auto-indexed output tunnels.** Each iteration then writes
   its own index with no dependency on any other iteration - which is what makes parallelism legal.
   Auto-index the corresponding inputs too, instead of passing whole arrays in and using `Index Array`.
2. **Then** enable `Configure Iteration Parallelism` on the loop and wire `P`. Only step 1 makes step 2
   possible; doing step 2 first would either be rejected or silently produce wrong results.
3. `N` no longer needs wiring at all once inputs are auto-indexed - the loop count follows the array
   length by construction.

### The one real wrinkle: `x,y,z array` is 3 values per bead

The 2010 code indexes it flat with `i*3`. A naive auto-index over a flat array yields **one scalar per
iteration**, which is wrong. Two clean options:

- **Reshape to 2D `N x 3`** before the loop and auto-index rows (each iteration gets a 3-element array),
  then reshape the auto-indexed 2D output back to 1D after the loop. Preserves the external interface.
- Or carry x, y and z as three separate auto-indexed arrays inside the loop and interleave afterwards.

Prefer the reshape: it keeps the connector pane and the caller unchanged.

### Caveats before relying on this

- ~~Verify which subVI it calls~~ **RESOLVED 2026-08-26: it calls exactly
  `Track 1 of N bds xyz-kernel-reentrant.vi`** - the *same* single-bead kernel the current four-fold
  over-kernel uses, and precisely the unit chosen for parallelisation on 2025-08-25. It calls **no
  other** sub-VI: no `Track 2`, no remainder handler. So despite the 2010 date, it is directly
  compatible with today's kernel, and the design decision made independently in this project turns out
  to match what the original author already did.
- Its connector pane has two inputs the modern four-fold kernel does not (`Cosine bandpass for
  Hilbert`, `Real-space cosine window`) and uses `# of bead` where the modern one uses
  `# of bead 4 packs`. The replacement must match **today's** four-fold pane to drop in.
- Opening it in LabVIEW 2026 marked it `*` (recompiled from 2010 format). It is a copy in
  `claudeDev\background VIs_COPY\`; do not save it back over anything.

### THE BUILD IS NOW MOSTLY A LIBRARY CALL

`erdosmiller/lv-scripting`'s **`Create For Loop.vi`** (verified compiling on LabVIEW 2026) takes
**`Inputs Indexing?`** and **`Number of Static Parallel Instances`** as inputs, and returns the loop's
**inner terminal references**. That means the two hardest steps of this plan - turning the shift
registers into auto-indexed tunnels, and enabling iteration parallelism - become *parameters of a
single call* rather than GUI surgery on a structure border.

Sketch of the rebuild:

1. `Create Open VI Reference` / `New VI` -> target diagram reference.
2. **`Create For Loop.vi`** with `Inputs Indexing? = TRUE` for `Array of cal clusters`,
   `x,y,z array` (reshaped N x 3) and `Bead is good? array in`, and
   `Number of Static Parallel Instances` set to the desired P. Leave `Loop Count Terminal` unwired -
   auto-indexing determines the count.
3. **`Create SubVI.vi`** to drop `Track 1 of N bds xyz-kernel-reentrant.vi` inside the returned
   `Diagram out`.
4. **`Wire Inputs.vi`** from the returned inner tunnel terminals to the subVI's inputs.
5. Auto-indexed output tunnels for the three results; `Exit For Loop.vi` to leave scope.
6. Close every reference (see the `labview-automation` skill - leaks are severe).

### Build method — scripted, and steps 1–2 are already automated

The click-based steps below predate the scripting toolchain. **Read them as a specification of the
result, not as a procedure.** As of 2026-08-28 the loop creation and the kernel placement are a
single command:

```
py tools\gscript.py kernel <target.vi>
```

which creates the P=4 loop at a known `location`, finds its inner diagram deterministically (by
position, then confirmed by `owner=ForLoop`), drops `Track 1 of N bds xyz-kernel-reentrant.vi`
inside, and reports before/after object counts. See `STATUS.md` for what the fleet can and cannot do.

Two method corrections that matter here:

- **Do not create nodes with `New VI Object`** except for the structure styles that are in its ring
  (For Loop, While Loop, Case Structure). For anything else, **copy from a donor VI** — NI's own
  forums give this as the answer, and the generic-creator experiment failed. SubVIs are dropped with
  lv-scripting's `Create SubVI.vi`, wrapped as `OpSubVI_v1`.
- **Wiring is scripted** node-to-node by terminal name (`OpWire_v0`), and every wire is verified by
  the `Wire` count changing — never by looking at the diagram.

## Steps — partially done, see STATUS.md for live state

**Progress as of 2026-08-30 (corrected):** steps 1–2 are **scripted and reproducible** via
**`gscript.loop_kernel()`** — it creates the P=4 loop, places the tracking kernel in its inner
diagram, and wires named front-panel controls to named kernel inputs through tunnels LabVIEW
auto-creates on the border crossing. Containment is now **proven and encoded** (offset match +
margin check + owner assert). Three caveats:
**(1)** the older `gscript.py kernel` / `for_loop` path creates **no data tunnels at all** — that
claim was a silent no-op for days, see STATUS; **(2)** verification so far is **structural only**
(`ExecState == 1`), no data has ever flowed; **(3)** **no assembly run has ever saved its target.**
What remains is the glue in steps 3–7, the functional test, then the drop-in swap. Always check
[STATUS.md](STATUS.md) for live state before working from the list below.

Working file: `user.lib\claudeDev\Track N beads PARALLEL over-kernel v1.vi` — created as a copy of
the original four-fold kernel (so it keeps the correct connector pane). **Caution:** this copy is no
longer pristine — the user's Save All on 2026-08-27 persisted in-memory run artifacts into it
(62138 → 70933 bytes). For a clean build, re-copy from the true original in `background VIs\`, or use
`Track N beads PARALLEL over-kernel v2_KERNEL.vi`, which is still pristine.

1. Re-confirm `Track 1 of N bds xyz-kernel-reentrant.vi`'s connector pane hasn't drifted (already
   visually confirmed once).
2. In the working file's block diagram, find empty canvas and build there. **Do not** try to delete or
   otherwise touch the old four-fold/Track-2 structure's border — see "Do not re-attempt" in STATUS.md.
   - Drop a new For Loop.
   - Place a `Track 1 of N bds xyz-kernel-reentrant.vi` call inside it.
   - Wire the ~7 inputs (`Image In`, `Array of cal clusters`, `Bead is good? array in`, `x,y,z array`,
     `cross size`, plus whatever per-bead starting-x/y derivation the old loop did internally — check
     how it derived `starting x 1`/`starting y 1` from `x,y,z array`, likely just an unbundle/index)
     by branching new wires off the *existing* source wires. Fan-out from a source terminal never
     requires touching or deleting anything already there.
   - Auto-index the loop over bead count into `Track 1`'s single-bead inputs, and auto-index its
     outputs back out. Auto-indexed tunnels place each iteration's result at its own index
     automatically — no manual bookkeeping — *provided* auto-indexing is actually used rather than a
     shared non-indexed tunnel.
   - Enable "Configure Iteration Parallelism" on this **new** loop and wire a real value into `P`.
     It's a fresh isolated loop with nothing competing for its border pixels, so it should be far
     easier to hit than the old one — but verify rather than assume.
3. Delete the **3 output wires** currently running from the old structure to `Bead is good? array out`
   / `x,y,z array out` / `pos in cal image out`, and reconnect those terminals to the new loop's
   outputs. (Wires select and delete reliably; borders do not.)
4. Run **Clean Up Diagram** (right-click empty canvas) rather than hand-positioning anything.
5. Verify no shift registers or cross-iteration dependencies exist on the new loop — there shouldn't
   be any, each bead is independent, but confirm before calling it done.
6. Save. The file already lives in `user.lib\claudeDev`; no relocation needed.
7. Only then: wire it into the main V6 tracking VI in place of the current four-fold kernel call.

## File-location gotcha

The original kernel is at `zz_LabView VI\background VIs\Track N beads four-fold over-kernel-v3.vi`
(never modify). Its reentrant dependencies (`Track 1 of N bds xyz-kernel-reentrant.vi`,
`Track 2 of N bds xyz-kernel-reentrant-v2.vi`, plus ~5 deeper transitive helpers like
`Tracking-prep I of r.vi`) sit co-located in that same folder. **Copy the whole `background VIs`
folder**, not just the top VI, before opening anything — opening the top file alone cascades through
many "Find the VI Named X" dialogs. Confirmed the hard way.
