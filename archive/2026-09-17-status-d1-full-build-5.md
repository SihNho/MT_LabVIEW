---
type: archive
status: historical
date: 2026-09-17
tags: [status-narrative, cycle15, d1]
relocated_from: STATUS.md
---

# STATUS narrative relocated 2026-09-17 (session `material/cycle15-d1-full-build-5`, run 8)

Rule 4: STATUS.md reached 135 lines. The OPEN items below were **all ✅ CLOSED** and are moved **verbatim**; one
line plus this pointer is left in STATUS. Nothing is rewritten and nothing is deleted.

## The closed OPEN items, verbatim as they stood

```
16. ✅ **GPU kernel ACCEPTED FOR NOW** — user 2026-09-17 "현재로서는 통과", revisit later (`decisions.md:38`);
   N1's whole-fixture range is REPORTED, not gated. D1 stays on `GPU_kernel_v1.vi`, no CPU-fallback branch.
19/25/26. ✅ PLAN = REV 4 + §11c–§11h; TRANSPORT = **queues only**; sentinels stop 1.2/1.5/1.7; `#12589`/`#642`
   stay on 1.1. 20–23 ✅ CLOSED. 27. ✅ **RELOCATION MEASURED** — run 5 53/0, re-confirmed run 6 (56/1, the 1 a
   stale gate now fixed): `WhileLoop 3→6`, `Diagram 170→173`, all 23 moves, 8 SRs, ControlTerminal 114 intact,
   collateral 0, d19 clean. Re-wire list = `tools/bench/build_d1_v0.json`, **109 terminals / 24 uids**.
28. ✅ **§11i's WALL IS GONE.** **`OpCreateConstOnTerm_v0` BUILT, SAVED, FUNCTIONAL 22/0**
   (`build_opcreateconstonterm_v0.log`, toolkit row 54): `Terminal.Create Constant` **6349C00** on a BODY node's
   terminal → a `DigitalNumericConstant` **typed by the sink and already WIRED**, value **−1** read back through
   `OpConstValueN_v1`, `ControlTerminal` unchanged, scratch ExecState 1. Its census settles A3: 6349C00 **does**
   take a `Value` input (t6/t7), so no value-write chain was needed. It placed **5 literals in the real D1 copy**.
   🟡 **`OpCreateConst_v0` is NOT the literal placer** — measured in the same run: its VARIANT route yields class
   `Constant` with an **EMPTY** value. (That is the old NEXT line's "material, needs no decision" — CLOSED.)
28b. ✅ **SOURCE MAP COMPLETE — 109/109** (`tools/bench/d1_rewire_map.py` → `d1_rewire_sources.json`). The old
   45/82 join could not see constants, control terminals, loop tunnels or the 8 moving shift registers.
28c/28d/28e. ✅ `diag_d1_full_route` is RETIRED (§11j.2). Its findings stand: `copy_by_index` of the −1 donor
   `#4609` copied nothing (route (a) dead); `OpWireSource_v5` returns 1055 for every wire in this configuration.
29. ✅ **`OpStopFromNode_v0` T5 CLOSED BY MEASUREMENT** (wire 0 → **387**, VI at **ExecState 1**). 🟡 T6 open.
   ✅ `audit_cycle.py`'s `FAILURE_RE` repaired — it matched neither `**FAIL**` nor `BGRUN END rc≠0`, so it
   reported ZERO failures for a window with five; verified on 4 real logs (device for `device-failed`, round 5).
30/30b/30c. ✅ §7.1's TSV → D2 (§11f.1; §7.3 measured `#376` saves periodically). ✅ **§11h — the per-frame TIFF
   writer is NOT original behaviour and D1 DELETES it**: true original (md5 `1eb666c1df8a…`) **97/179/622** vs the
   copy's **98/181/626**, gate **S1t** 4/4 again in run 7 (`Wire 1902→1899`, bare named sinks 28→26, ExecState
   0→0; `#23175`/`#22703` left standing). **F1 needs no TIFF cap ⇒ the 5-min run is affordable.**
```

## What this session (run 8) added, in full — the short forms are STATUS OPEN 33/34/35

### The donor census that decided the build (`tools/bench/diag_connectnested_donors.log`, 6/0, read-only)

Six ops censused node-by-node, every md5 unchanged: `OpNetInfo_v1`, `OpNodeTerms_v0`, `OpConnect_v0`,
`OpStopFromNode_v0`, `OpCreateConstOnTerm_v0`, `OpWhileCast_v0` (raw → `tools/bench/connectnested_donors.json`).
Three facts came out of it:

1. **`OpStopFromNode_v0`'s ladder is LOOP-anchored**, `Traverse("WhileLoop")[index] → To More Specific Class →
   `Loop.Diagram` 6361401 → …`, so "duplicate it for the source side" (§11m) puts BOTH ends on the same loop.
2. **`OpNetInfo_v1`/`OpConnect2_v0` hold the DIAGRAM-indexed ladder**: `Open VI Reference` → `Traverse for
   GObjects.vi`(`Class Name`, `References[]`) → `Index Array`(`index`) → `To More Specific Class`(`target class`
   ← a class constant) → `Nodes[]` → IA(`index 2`) → `Terms[]` → IA(`index 3`) = a Terminal reference addressed
   by (diagram, node, terminal).
3. **`OpConnect_v0` proves two ladders can share one array**: its `Nodes[1]` and `Nodes[8]` both take
   `array` = w171.

### The op, and the wall (`build_opconnectnested_v0_run1.log`, `…v0.log`)

Run 1 built the prior-art review's own prescription — a second `Index Array` on the Traverse `References` array
feeding the source `Nodes[]` node — and measured `W4 ROUTE A wired: ExecState 0`. `References` is an array of
**GObject** references; the property node is **Diagram**-class; GObject → Diagram is a downcast. Run 1 also had a
defect of mine: `remove_bad_wires_scripted` left the broken wire on the source `reference`, so the ROUTE-B
fallback declined to wire and never ran. Repaired by deleting the wire by Traverse index and gating bareness.

Run 2 shipped **ROUTE B**: the source `Nodes[]` node is fed by **branching the sink ladder's already-cast
`specific class reference`**, so both ends sit on the diagram named by `index`. ExecState 1, saved, 14,234 B,
donor md5 unchanged.

### Why a second cast cannot be made (the finding that blocks §11m as written)

* `New VI Object` creates no primitive — `.claude/skills/labview-automation/references/vi-scripting.md:308`,
  and `:465` records the 0–399 style sweep creating nothing.
* `gscript.copy_by_index` is the fleet's primitive copier, but a copied `To More Specific Class` arrives with its
  **`target class`** input bare, and that input is fed by a **class-specifier `Constant`** — a GObject, not a
  Node, so no wire creator in this fleet reaches its output. Identical to §11i's recorded wall.

### The three peer exchanges of this session

| slug | agent | outcome | what it changed |
|---|---|---|---|
| `priorart-connect-nested` | claude/opus | ANSWERED, 6 findings 0 novel | donor changed to `OpConnect2_v0`; "resolves all 31 rows" refuted (reaches ~7–8); its own one-node-swap advice then refuted by measurement |
| `connectnested-stall` | codex | ANSWERED | my "GObject.Move wedged LabVIEW" withdrawn; the real defect is `_run` abandoning a live COM call (STATUS OPEN 35) |
| `connectnested-t2b` | codex | ANSWERED | "functionally verified" withdrawn; named a third cause of ExecState 0 (a REQUIRED unwired input) and prescribed the three-postcondition test that became `test_opconnectnested_v1.py` |

### The three test runs, in order

| log | result |
|---|---|
| `test_opconnectnested_v0.log` | 7/1. Body→body on a nested diagram **w0 → 206, same uid both ends**; an **UNNAMED** terminal reached by index (branch, `wire delta 0`). ExecState gate invalid — the pair was `error out` → `path`, and a fresh While loop is broken anyway |
| `test_opconnectnested_v1.log` | **10/1, the decisive one.** Scratch built to **ExecState 1 first** (5 literals via `OpCreateConstOnTerm_v0`, stop wired via `OpStopFromNode_v0`), sink asserted **unwired**, op error **empty**, wire created **w285 on both ends** — and **ExecState 1 → 0** |
| `build_opconnectnested_v0.log` run 2 | the build itself, 10/1 (the 1 = ROUTE A, expected) |

**Level of verification, stated: STRUCTURAL + ENDPOINT/WIRE-IDENTITY. NOT functional.** Undecided between
(a) the unnamed sink terminal's type being incompatible again and (b) the op's wire being broken by construction.

---

## Relocated VERBATIM from `STATUS.md`'s lock block, 2026-09-17 ~13:5x (rule 4, STATUS was at 120 lines)

Two session entries, moved whole, nothing rewritten. STATUS keeps one line pointing here.

```
# 2026-09-17 12:2x material/open35-run-poison-fix: RELEASED. Two 3-second runs of tools/bench/test_run_poison.py
# (11 pass / 0 fail). LabVIEW NOT restarted. Scratch `SCRATCHPOISON_1220*/1221*.vi` created and DELETED in the
# same run, verified gone. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859 read before AND after.
# OpReport_v3 / OpWire_v1 md5 unchanged. Nothing saved, no GUI, no hardware. Handles 31,276 -> 31,381.
# 2026-09-17 11:0x-12:1x material/cycle15-d1-full-build-5: RELEASED. LabVIEW restarted twice (31,561 / 31,669 ->
# ~34,000). `OpConnectNested_v0` BUILT + SAVED (ExecState 1, 14,234 B). 4 scratches: 3 self-deleted, 1 orphaned by
# the bgrun kill and deleted by hand -> `claudeDev\SCRATCH*` is EMPTY, verified. ORIGINAL never opened; md5
# 2a78e17c449cacdaf5da389818526859 verified after. No GUI, no hardware. build_d1_v0 NOT run (see NEXT). Handles
# 31,285 -> 31,632. -> facts in OPEN 33/34/35.
```
