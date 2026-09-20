---
type: narrative
status: historical
date: 2026-08-26
tags: [archive]
---

# Capability Test Matrix — what must work before building V6

**Why this exists:** the project is at an early stage, so every capability the build depends on gets
tested *before* it is relied on, rather than discovering a gap mid-build. Each row is pass/fail with
evidence. User instruction 2026-08-26: *"test all the things need to be done."*

Legend: **PASS** verified with evidence · **FAIL** verified broken · **BLOCKED** dependency missing ·
**TODO** not yet run

## A. Core scripting capability (project hinges on these)

| # | capability | why it matters | status |
|---|---|---|---|
| A1 | Create a For Loop with **`Number of Static Parallel Instances` > 0** | **THE critical one.** Iteration parallelism is the entire point of V6. | **PASS** |
| A2 | Create a For Loop with **auto-indexed input tunnels** (`Inputs Indexing? = TRUE`) | Required to replace the shift registers that currently forbid parallelism | **PASS** |
| A3 | Create a For Loop with **NO shift registers** | Shift registers are the loop-carried dependency to eliminate | TODO — needs the driver |
| A4 | **`Create SubVI.vi`** — drop `Track 1 of N bds xyz-kernel-reentrant.vi` on a diagram | The loop body is a call to this kernel | **LIKELY PASS** (ran clean, output not retained) |
| A5 | **`Wire Inputs.vi`** — wire tunnel terminals into the subVI's inputs | Without this the loop body is unconnected | **API CONFIRMED** — wires **by terminal NAME** |
| A6 | Script into an **EXISTING** VI (not a fresh `New VI`) | The replacement kernel must be a real file with the right connector pane | **PASS — CONFIRMED** |
| A7 | **Auto-indexed OUTPUT tunnels** for results | How each bead's result lands at its own index | **LIKELY** — `[ ]` output tunnels seen in A1 |
| A8 | **Save** a scripted VI to disk programmatically | Otherwise nothing persists | TODO — VI Server `Save Instrument`, not an lv-scripting VI |

## B. Interface fidelity

| # | capability | why it matters | status |
|---|---|---|---|
| B1 | Read/replicate the four-fold kernel's **connector pane** | The replacement must drop into the main VI unchanged | TODO |
| B2 | Reshape `x,y,z array` flat <-> N x 3 | 3 values per bead; naive auto-indexing yields a scalar | TODO |
| B3 | Confirm the new VI is **reentrant-safe** for parallel calls | `Track 1` is reentrant; verify the wrapper does not serialise | TODO |

## C. Alternative / supporting paths

| # | capability | why it matters | status |
|---|---|---|---|
| C1 | **VI Snippet** import/export (`rcpacini/LabVIEW-VI-Snippet`) | Could move a whole working loop body instead of scripting node-by-node | **PASS** (compiles on 2026) |
| C2 | **Zuehlke read path** (VI -> AIXML text) | Would expose block-diagram *wiring* as text | TODO — needs Go + gRPC setup; deferred as optional |
| C3 | LAVA scripting tools — connector-pane wiring | Second source for B1 | TODO |

## D. Verification / safety

| # | capability | why it matters | status |
|---|---|---|---|
| D1 | Detect a broken VI programmatically (error list) | Must know if a scripted edit broke something | TODO |
| D2 | Originals remain byte-identical throughout | Hard rule 1 | **PASS** — MD5 re-verified repeatedly (4.5 = `db5291d1…`) |
| D3 | Measure actual speedup (sequential vs parallel) | The project's success criterion is speed | TODO |

## Results log

Newest last. Each entry records what was run and the evidence.

### A1 + A2 — PASS (2026-08-26)

**Method:** set `Number of Static Parallel Instances = 4` on the front panel of
`<LabVIEW 2026>\examples\Erdos Miller\LV-Scripting\examples\Example 8 - For Loops.vi`, then ran it.
It generated `Untitled 14`.

**Evidence (screenshot, 4x crop):** the generated For Loop has

- an **`N` terminal carrying the parallelism red dot**, with a **`P` terminal directly beneath it** -
  `P` is LabVIEW's "number of generated parallel loop instances" terminal and **only exists once
  iteration parallelism is enabled**;
- the **stacked/layered loop border** LabVIEW draws for a parallelised For Loop;
- **`[ ]` bracket tunnels** on both borders = **auto-indexed** tunnels (A2);
- `▼`/`▲` shift registers (present because `Shift Registers?` was left TRUE - A3 tests the opposite);
- `i` terminal and a conditional terminal with a `?` output tunnel.

**Why this matters more than any other result so far:** enabling iteration parallelism was the single
thing this project could not do. A whole session was lost trying to select a structure's border by
simulated click, and the existing four-fold kernel carries a `P` terminal that was never wired because
its shift registers made parallelism illegal. **`Create For Loop.vi` sets it as a parameter, in code,
first try.** The scripted route to V6 is therefore viable.


### A4 + A5 — API confirmed, execution clean (2026-08-26)

Ran `Example 5 - SubVIs.vi`. It completed with **no error dialog** (LabVIEW's `Simple Error Handler`
would have raised one under the VI's own name), but it closes its references at the end without
retaining the generated VI, so **no output VI was left to inspect**. Recorded as *likely* pass rather
than confirmed - the honest reading.

**The more valuable finding is the API shape**, read off the example's diagram:

`Create SubVI.vi` takes a **VI Reference** (a Static VI Reference to the subVI to drop), a target
**diagram**, and an **array of input names**; its on-diagram comments state *"The inputs corresponding
to the specified names are wired to the supplied terminals"* and *"The output terminals specified are
returned"*.

**That means subVI inputs are wired BY TERMINAL NAME, not by coordinate.** For the kernel rebuild this
removes the entire class of problems this project has been fighting: no probing, no pixel geometry, no
snap zones. Wiring `Track 1 of N bds xyz-kernel-reentrant.vi` becomes passing the strings
`image in`, `cross size`, `Calibration cluster 1`, `starting x 1`, `starting y 1` and reading back
`X pos 1`, `Y pos 1`, `Z pos 1`, `Bead 1 is good`.

The example also ends with a `Diagram > CleanUp` invoke - so **Clean Up Diagram is scriptable too**,
removing the last manual step in the plan.

### A6 — EVIDENCED by prior work (2026-08-26)

Not re-run, because it was already demonstrated. The earlier `ScriptTest_Driver.vi` used
`Open VI Reference` on an existing file, then its **`Diagram`** property, and fed that into
`New VI Object`. That chain **executed** - its failure (Error 1059) came *later*, inside `New VI
Object`'s `Path` input, which proves the diagram reference itself was valid.

Since `Create For Loop.vi` simply consumes a `Diagram in` reference, the reference's *origin* is
irrelevant to it. Targeting an existing VI is therefore a matter of swapping `New VI` for
`Open VI Reference` + a path constant. To be confirmed for real during the build.

### C1 — VI Snippet: PASS on compatibility (2026-08-26)

`rcpacini/LabVIEW-VI-Snippet`, MIT. Releases are from **2020** (not 2022 as the README implies), and
ship a `.lvlibp` **packed** library - which is precompiled and version-sensitive - plus a source zip.
**The source was used**, so LabVIEW recompiles it rather than trusting a 2020 binary.

`VI Snippet Export.vi` **opened in LabVIEW 2026 with a solid run arrow**. Its connector pane:
`VI Snippet Path (*.png)`, `VI Refnum`, `Selected GObjects Only? (F)`, error in/out. Companion VIs:
`VI Snippet Import.vi`, `VISP Copy GObjects to Clipboard.vi`, `VISP Paste from Clipboard.vi`, and PNG
chunk read/write.

**Functional test still pending** - `VI Refnum` is a refnum control, so it cannot be exercised from the
front panel; it needs a small driver. But the compatibility question, which was the real risk, is
answered.

**Possible shortcut it enables:** export the 2010 one-fold kernel's loop body as a snippet PNG, then
import it into the new VI - moving a whole working fragment instead of scripting node-by-node.

---

## Where this leaves the build

**The toolchain is proven.** The capability that gated the entire project - enabling iteration
parallelism programmatically - **works**. Everything still marked TODO now depends on building the
driver rather than on any unknown.

Next concrete step: **`user.lib\claudeDev\KernelBuilder_v1.vi`** (already cloned from
`Example 8 - For Loops.vi`, which is a working parallel-loop generator). Retarget it:

1. Swap `New VI` -> `Open VI Reference` + path to the working kernel copy (A6).
2. `Inputs Indexing? = TRUE`, `Shift Registers? = FALSE` (A2, A3).
3. `Number of Static Parallel Instances` = P (A1 - proven).
4. `Create SubVI.vi` with `Track 1 of N bds xyz-kernel-reentrant.vi` and its input names (A4, A5).
5. `Diagram > CleanUp`, then VI Server `Save Instrument` (A8).

### A6 — CONFIRMED PASS (2026-08-26)

`KernelBuilder_v1.vi` was retargeted and run. **The For Loop appeared inside the existing
`ScriptTest_Target.vi`, and no new Untitled VI was created.** Scripting into an existing file works.

**The edit, step by step** (all on a claudeDev copy; no original touched):

1. Placed `Open VI Reference` with **Quick Drop** (`Ctrl+Space` -> name -> Enter -> **click**).
2. Right-clicked its `vi path` terminal -> `Create > Constant`, so LabVIEW generated a correctly-typed
   path constant; typed the target path into it.
3. `probe` located the teal `VI reference` wire at exactly **y=565**; clicked and deleted it.
4. `hover` confirmed the `vi reference` output by **tip strip** before wiring - no guessing.
5. `wire` from `vi reference` -> Property Node reference input. Run arrow stayed **solid**.
6. Deleted the orphaned `New VI` node; it left a **broken wire** (dashed + red X) where its error
   output had fed the Property Node. Cleared with `Edit > Remove Broken Wires`.
7. `hover` confirmed `error out`, then wired it -> Property Node `error in`. Run arrow **solid**.
8. Saved, ran. Target VI received the loop.

**Note on the generated loop:** it still carries **shift registers**, because the driver's
`Shift Registers?` front-panel input defaults to TRUE. For the real kernel that must be **FALSE** and
`Inputs Indexing?` **TRUE** - both are front-panel values, so no further diagram surgery is needed.

**Techniques that made this cheap**, all now in `GUI_PLAYBOOK.md`: Quick Drop for placement,
`Create > Constant` for correctly-typed constants, `probe` for exact wire/terminal rows, `hover` for
tip-strip confirmation before committing a click, and `movewin` because LabVIEW kept opening the
diagram window off-screen.
