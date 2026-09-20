---
type: measurement
status: current
date: 2026-09-16
cycle: 15
tags: [main-vi, stop, shutdown, file-writer, tracker-seam]
measured_in: [tools/bench/diag_stop_save_seam.log, tools/bench/stop_save_seam.json, tools/bench/main_vi_nodeterms.json]
---

# The original's STOP, FILE WRITER, SHUTDOWN and TRACKER SEAM — facts only

Cycle 15 step 1(b)+(c). **Read-only** on `Min_Track N beads V6_ParallelLoop.vi` (rule 1d): md5
`2a78e17c449cacdaf5da389818526859` **before and after** every run below. No judgement here — what D1 should be
built from is not decided in this file.

Two sources, both current for that md5:
* **offline** — `tools/bench/main_vi_nodeterms.json` (2026-09-14): every terminal of all 626 nodes on all 170
  diagrams, with name / direction / connected wire uid. Marked `census`.
* **measured this cycle** — `tools/bench/diag_stop_save_seam.log` (29/30 gates, 117 s, MEASURED 2026-09-16
  22:05): `OpWireSource_v5` for the 19 wires the census leaves with one end (control terminals and
  border-crossing segments are separate `Wire` objects), `OpOwnerChain_v1` for owner chains, `subvis()` for
  identity. Marked `measured`.

## 0. The three diagrams this file is about

| diagram (Traverse index) | uid | owner | what is on it |
|---|---|---|---|
| **43** | 639 | `WhileLoop` **#637** — the frame loop | the tracker seam, both stop Booleans, autofocus, WLC, `save trace.vi` |
| **19** | 686 | `FlatSequenceFrame` | the frame loop **#637 itself**, and `save N xyz traces.vi` **#6384** after it |
| **83** | 759 | `FlatSequenceFrame` | IMAQdx Stop/Close, `ASI TG-1000 Close.vi`, `IMAQ Dispose`, 2× Simple Error Handler |

`measured`: `5058 → Diagram#639 → WhileLoop#637`, `6384 → Diagram#686 → FlatSequenceFrame#0`,
`637 → Diagram#686 → FlatSequenceFrame#0`, `2078 / 29815 → Diagram#759 → FlatSequenceFrame#0`.
⚠️ **The owner chain terminates at a `FlatSequenceFrame` with uid 0** (the limit recorded in
`docs/toolkit-capabilities.md:49`), so *which* flat sequence and *which frame index* diagram 19 and diagram 83
are is **NOT measured** — the shutdown's trigger is "the flat sequence reaches that frame", with the frame's
position unread.

## 1. The stop control(s) — (b)(i) and (b)(iv)

| | `stop (end)` | `stop (end) 2` |
|---|---|---|
| panel control uid | **7** | **19587** |
| diagram terminal's wire | **6929** | **15230** |
| where that terminal SITS | owner `Diagram`**#639** = **inside the frame loop body** (`measured`) | owner `Diagram`**#639** — same (`measured`) |
| its only wire sink | `CompoundArithmetic`**#11639** term 2 `value` (`measured` + `census`) | `CompoundArithmetic`**#17883** term 1 `value` (`measured` + `census`) |
| that node's other inputs | wire 12070 ← node 12589 t2; wire 10249 ← `x = y?` #10019 (`census`) | wire 18092 ← `.not. x?` #17837; wire 18056 ← `x = y?` #22284 (`census`) |
| the node's `result` wire | **3457** → **two sinks, both owner `Diagram`#639** (`measured`) | **15229** → `Tunnel`**#22085** of `CaseStructure`**#22082** (`measured`) |
| owner chain of that node | `#11639 → Diagram#639 → WhileLoop#637` | `#17883 → Diagram#639 → WhileLoop#637` |

**(b)(iv) verdict, at the level it is actually measured.** Both stop Booleans are read **from terminals that sit
on the frame loop's own body diagram**, each OR-ed with two other conditions by a Compound Arithmetic node that
also sits on that diagram. So the original does hold an **in-loop Boolean stop path**, not a pre-loop tunnel.

### ✅ CLOSED 2026-09-17 — the conditional terminal is **uid 648**, driven by `CompoundArithmetic` **#11639**

`MEASURED` by `OpLoopEndRef_v0.vi` (`WhileLoop.Loop End Ref` **6362C00** → the terminal → `Is Source?` /
`Connected Wire`), built and functionally verified the same run — `tools/bench/build_oploopendref_v0.log` (16
pass / 0 fail, 56 s, MAIN md5 unchanged), raw `tools/bench/loopendref_637.json`:

| While loop (Traverse index) | conditional terminal uid | `Is Source?` | `Connected Wire` |
|---|---|---|---|
| **#637 — the frame loop** (index 1) | **648** | False (it is a SINK) | **3457** |
| #25380 (index 0) | 25410 | False | 1737 |
| #15173 (index 2) | 15276 | False | 19456 |

`OpWireSource_v5` on wire 3457: **exactly one source terminal, owner `CompoundArithmetic` uid 11639** (label
`Compound Arithmetic`); its two other terminals are the sinks already recorded here — the panel indicator
`TurnOff` (uid 24423) and **this conditional terminal, uid 648**. So the sentence below that could not be
established — *which* of wire 3457's two `Diagram#639` sinks is the loop's conditional terminal — is answered:
**the unnamed one is uid 648, the conditional terminal, and `stop (end)` uid 7 → `#11639` → wire 3457 → #637's
conditional terminal is the frame loop's stop path, entirely inside `Diagram#639`.** `stop (end) 2` #19587 →
`#17883` → wire 15229 → `Tunnel#22085` of `CaseStructure#22082` remains a **separate** path and does not reach
this terminal. Also measured, and new to `docs/NAMES.md`: the property's data-terminal short name is **`LpEndRef`**
and the id **6362C00 IS valid on class `WhileLoop`** on this machine (census, not "no error 1077").

**What was NOT measured until then, and was a failed prediction (P5).** The prediction was that the OR-ed `stop (end) 2` wire
would land on the loop's conditional terminal. It does not: uid 22082 reads class **`CaseStructure`**, and the
wire enters that case's input `Tunnel#22085`. The remaining claim — that one of wire 3457's two `Diagram#639`-owned
sinks IS `WhileLoop#637`'s conditional terminal — is an **inference**, because **no reader for the While loop's
conditional terminal exists in this toolkit**. Peer review:
`archive/peer/2026-09-16-stop-condterm-failed-prediction.md` (ANSWERED, 126 s) refused the inference — a terminal
whose `Generic.Owner` is the Diagram and which no node's `Terminals[]` claims is *also* the signature of a
front-panel `ControlTerminal`, so the signature does not identify anything — and named the cheapest test.

**That test was run** (`tools/bench/diag_stop_condterm_panel.log`, 30 s, `panel_wiring` over 114 panel objects,
md5 unchanged): of wire 3457's **two direct, non-source terminal references**, **one is the front-panel
INDICATOR `TurnOff` (uid 24423)**; wire 15229 and `Tunnel#22085` are carried by no panel object. Prediction Q2
("no panel object carries 3457") **failed** — second review
`archive/peer/2026-09-16-stop-condterm-panel-fail2.md` (ANSWERED, 107 s), which **rules the question open and
names the reason**: `panel_wiring` is documented as **NOT recursive** (`tools/gscript.py:632` — tab pages and
cluster elements are not rows), so the unmatched sink is equally well explained by a tab-page-nested
control/indicator terminal. **Nothing here says the loop has, or lacks, a wired conditional terminal.**
Cheapest remaining test, in order: (1) a **recursive** front-panel census — `Traverse for GObjects` over
`ControlTerminal`, each terminal's `Connected Wire` vs 3457; (2) only if that finds no second carrier, a new
reader for `WhileLoop.Loop End Ref` **0x06362C00** on uid 637. Both are new ops and are NOT built in this cycle.
`docs/frame-ownership-design.md:105` states the normal stop is LabVIEW's **Abort** (this file cited `:92-97`
until 2026-09-17; those lines are the superseded camera-overload paragraph — prior-art A3-iii,
`archive/peer/2026-09-17-priorart-priorart-loopendref.md`); that is a statement about
how the user *operates* the VI, and this file does not contradict or confirm it — it measures the wiring only.

## 2. `save N xyz traces.vi` — (b)(ii)

Call site **uid 6384**, on **diagram 19** (owner `FlatSequenceFrame`), i.e. **after the frame loop**, not inside
it. `subvis(MAIN, 19)` returns exactly two calls: `#27605 Max Trans Pos.vi` and `#6384 save N xyz traces.vi`
(`measured`). Path: `G:\...\background VIs\save N xyz traces.vi` (`docs/main-vi-subvi-identity.md:188`).

Every terminal, with the object that drives it (`census`, and `measured` for wire 1920):

| t | terminal | dir | wire | source / sink |
|---:|---|---|---:|---|
| 0 | *(unnamed)* | IN | 0 | bare |
| 1 | `error out` | OUT | 1920 | → `FlatSequenceInnerTunnel`**#4774** (`measured`) |
| 2,3,4 | *(unnamed)* | IN | 0 | bare |
| 5 | `desired # data points` | IN | 2362 | ← **WhileLoop#637** outer terminal 14 (also feeds `dimension size` of #781) |
| 6 | `cal cluster path` | IN | 21 | ← **WhileLoop#637** outer terminal 23 |
| 7 | `actual # data points` | IN | 4337 | ← **WhileLoop#637** t19 `file progress` (also → `length` of #2048) |
| 8 | `error in` | IN | 1899 | ← **WhileLoop#637** t15 `error out` |
| 9 | `data array` | IN | 4564 | ← `#2048 subarray` (Array Subset) |
| 10 | `file # to append` | IN | 5073 | ← **WhileLoop#637** t18 `file number to append out` |
| 11 | `base path/filename` | IN | 5104 | ← **WhileLoop#637** outer terminal 17 |

So **seven of its eight live inputs come straight off the frame loop's output tunnels**, and the eighth is an
`Array Subset` of the loop's `total data array out` (#637 t12 → #2048 `array`). The in-loop partner is
`save trace.vi` **#376** on diagram 43, whose `error out` (wire 541) reaches #6384 t8 via the loop border
(`docs/frame-loop-wire-graph.md:413`).

## 3. Camera close / ASI close / IMAQ dispose — (b)(iii)

All on **diagram 83**, confirmed by `subvis(MAIN, 83)` (`measured`), in this data order:

| uid | call | measured wiring |
|---|---|---|
| **1839** | `NI_Vision_Acquisition_Software.lvlib:IMAQdx Stop Acquisition.vi` | `Session Out` wire 2129 → **#2078**; `error out` wire 2134 → **#2078** |
| **2078** | `NI_Vision_Acquisition_Software.lvlib:IMAQdx Close Camera.vi` | `error out` wire 2138 → `Simple Error Handler.vi` **#560** |
| **29815** | `ASI TG-1000.lvlib:Close.vi` | every terminal **bare** (wire 0) — no error chain, no VISA wire on this diagram (`census`) |
| **2431** | `IMAQ Dispose` | `Image` in ← `FlatSequenceInnerTunnel`**#1813** (wire 1316) |
| **560**, **3587** | `Simple Error Handler.vi` ×2 | #560 fed by #2078's error; #3587's terminals bare |

Also on diagram 83: local `Total Lost Frames` **#2143** ← `FlatSequenceInnerTunnel`#2283 (wire 2271) → `x != 0?`
**#7223** → `Tunnel`#1185 (wire 7291).

**No VISA Close node is on diagram 83.** The ASI closes through its own library VI (#29815) with an unwired error
chain; whether any `VISA Close` exists elsewhere in the VI is **not established here** — the shutdown frame does
not contain one.

## 4. The per-frame tracker seam — (c)

`subvis(MAIN, 43)` (`measured`) returns exactly six calls:
`#22700 IMAQ Write TIFF File 2` · `#1114 WLC function sub.vi` · `#48 ASI_adjust focus-subvi.vi` ·
**`#5058 Track N beads four-fold over-kernel-v3.vi`** · `#376 save trace.vi` · `#6810 get buff image-lost frames.vi`.

**#5058 is the seam.** Its 16 terminals, in `Node.Terminals[]` order, each with the object on the other end
(`census` where both ends are nodes, `measured` where the wire had one end only):

| t | terminal name | dir | wire | other end |
|---:|---|---|---:|---:|
| 0 | `Bead is good? array in` | IN | 5637 | ← `#5540` (CaseStructure) t2 `Bead is good? array out` |
| 1 | `Image In` | IN | 3040 | ← **`#6810 get buff image-lost frames.vi` `Image Out`**; also → `#22700` t11 `Image` |
| 2 | `cross size` | IN | 373 | ← `LoopTunnel`**#2580** (`measured`) |
| 3 | `Bead is good? array out` | OUT | 5859 | → `RightShiftRegister`**#5796** (`measured`) |
| 4 | `x,y,z array out` | OUT | 505 | → `#2222` t2, `#2626` t4 `array` |
| 5 | *(unnamed)* | IN | 0 | bare |
| 6 | *(unnamed)* | IN | 0 | bare |
| 7 | `x,y,z array` | IN | 5975 | ← `#5540` t6 `x,y,z array out` |
| 8 | `pos in cal image out` | OUT | 121 | → `#10757` t0 `array`, `#10969` t0 `array` |
| 9 | `# of bead 4 packs` | IN | 42 | ← `LoopTunnel`**#2396** (`measured`) |
| 10 | *(unnamed)* | IN | 0 | bare |
| 11 | `4 pack remainder` | IN | 3512 | ← `LoopTunnel`**#4432** (`measured`) |
| 12 | `Array of cal clusters` | IN | 3646 | ← `LoopTunnel`**#3656** (`measured`) |
| 13 | `pos in cal image in` | IN | 7429 | ← `LeftShiftRegister`**#2972** (`measured`) |
| 14 | `Real-space cosine window` | IN | 3912 | ← `LoopTunnel`**#3920** (`measured`) |
| 15 | `Cosine bandpass\nfor Hilbert ` | IN | 4027 | ← `LoopTunnel`**#4031** (`measured`) |

Shape of the seam: **6 loop-invariant inputs arrive through LoopTunnels** (cross size, # of bead 4 packs, 4 pack
remainder, array of cal clusters, and the two windows), **2 inputs are per-frame state** (`pos in cal image in`
from `LeftShiftRegister#2972`; `Bead is good? array out` into `RightShiftRegister#5796`), **2 inputs come from
`CaseStructure#5540`** (the reseed case — its two frames are already measured in
`tools/bench/case5540_frame_sources.json`), and the **image comes from `#6810` directly**. Three outputs leave:
`x,y,z array out` (wire 505), `pos in cal image out` (wire 121), `Bead is good? array out` (wire 5859).

The same terminal set — minus the GPU-only extras — is `GPU_kernel_v1.vi`'s connector pane
(`tools/bench/gpu_kernel_v1_fp.json`), and `docs/gpu-backend.md:13` records the CPU and GPU kernels as sharing
one pane.

## What this file does NOT establish

1. ~~Which of wire 3457's two `Diagram#639` sinks is the loop's conditional terminal~~ — **CLOSED 2026-09-17,
   §1**: it is **uid 648**, and wire 3457's single source is `CompoundArithmetic` **#11639**
   (`tools/bench/build_oploopendref_v0.log`, `tools/bench/loopendref_637.json`).
2. Which flat sequence and which frame index diagrams 19 and 83 occupy (owner chain stops at
   `FlatSequenceFrame` uid 0).
3. Whether any `VISA Close` exists outside diagram 83.
4. Anything functional. Nothing was run; this is a **structural** reading (CLAUDE.md "name the level").
