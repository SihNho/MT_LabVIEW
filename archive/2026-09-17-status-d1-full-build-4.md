---
type: archive
status: historical
date: 2026-09-17
tags: [d1, cycle15, material, rewire, ops]
session: material/cycle15-d1-full-build-4
---

# Session narrative — `material/cycle15-d1-full-build-4` (2026-09-17, ~10:30–11:2x)

Brief: build the third op (`Terminal.Create Constant` 6349C00 on a body node's terminal, §11j.1), then PHASE
"full", then N1 / F1 / F2. LabVIEW restarted first (handles were 78,224 → after restart **33,999**).

## 1. `OpCreateConstOnTerm_v0` — BUILT, SAVED, FUNCTIONAL **22 pass / 0 fail, 17 s**

`tools/recipes/build_opcreateconstonterm_v0.py` → `tools/bench/build_opcreateconstonterm_v0.log`.
Donor `OpStopFromNode_v0.vi` copied; its one `Invoke Terminal[Connect Wire 6349C03]` deleted (ExecState stayed 1);
`Invoke Terminal[Create Constant 6349C00]` created in its place on the SAME body-node ladder.

**The measurement the op existed to make — 6349C00's terminal census, never taken before:**
`reference`(0 IN) · `reference out`(1 OUT) · `error in`(2) · `error out`(3) · `Create Constant`(4 IN / 5 OUT) ·
**`Value`(6 IN / 7 OUT)**. So the NI-documented *optional `Value` input* is real, and the op sets the literal at
creation — no separate value-write chain is needed and none was built.

Functional test on a scratch copy of `EMPTY_v0.vi` (deleted in the same run): a `While` loop, a body node with a
bare numeric input (`Error Cluster From Error Code.vi`, `error code` I32), then the op:

| gate | result |
|---|---|
| T3o | the invoke's OWN error cluster is empty (prior-art B4's oracle, brought out on `error out 8`) |
| T3 | exactly one new object, **`DigitalNumericConstant` #159**, created UID returned on `UID 4` |
| T3b | the target terminal went **wire 0 → 176** |
| T3c | **`ControlTerminal` unchanged (0 → 0)** — no panel object, which is D1's S4s requirement |
| T4 | owner chain **#159 → Diagram#110 → WhileLoop#43** |
| T5a | class echo `DigitalNumericConstant` (prior-art B4′: asserted BEFORE any value read) |
| T5 | value read back through `OpConstValueN_v1`: **text `-1`, Representation 3** |
| T6 | `OpStopFromNode_v0` then drove the loop's conditional terminal; scratch **ExecState 1** |

**T5b, the A4 question closed in the same run:** `OpCreateConst_v0(Type=DBL, Value=-1)` produced class
**`Constant`** with an **EMPTY** value (`text ''`, `repr 0`) — its VARIANT route does **not** carry −1. STATUS's
"material, needs no decision" item is answered, and the answer is that the older op cannot place the literal.

## 2. The prior-art review — 5 findings, all accepted, and two of them changed the build before it ran

`archive/peer/2026-09-17-priorart-priorart-createconst-term.md` (claude/opus, ANSWERED, 460 s).
**A3** `contradicted` — two NI-sourced records in our own files already said 6349C00 takes an optional `Value`;
the recipe's probe loop (which stops at `ExecState 1`) could never have seen an *optional* input, the exact hole
`build_opsentinel_ops` run 1 paid for. Replaced by a forced control on every parameter input — and that is why
`Value` exists on the op at all. **B2** `already-failed` — the planned test invoked on `Equal?`'s `y`, which
`OpCreateEqual_v0` wires by construction, and the sibling method is measured to create **nothing** on a wired
terminal; the test was changed to a bare terminal, and §11k was written for D1's real ordering. **B4 / B4′** added
the created-object UID + error oracle and the class echo. Disposition and `FIXED:` lines are in the archive.

## 3. The re-wire source map — **109 / 109**, closing STATUS OPEN 28b's "45 / 82"

`tools/bench/d1_rewire_map.py` → `tools/bench/d1_rewire_sources.json`. Offline, no LabVIEW: it joins S3b's own cut
list with `main_vi_nodeterms.json` (1376 node wires), `opconstvaluen_scan.json` (155 constant wires),
`d1_step0_census.json`'s panel (103 control wires) and tunnels (253 tunnel wires), plus plan §5c's own
wire-by-wire shift-register table — a shift register is neither a node on a diagram nor a `LoopTunnel`, which is
exactly why every earlier join stalled at 45.

`source-side 27 · from-tunnel 18 · same-loop 16 · to-sr 12 · from-stay 11 · from-sr 8 · from-ctl 7 ·
from-const 5 · cross-loop 5`.

## 4. PHASE "full", stage 1 (the re-wire) — **55 pass / 7 fail**, 118 s, `build_d1_v0_run7.log`

Relocation reproduced exactly (S1 census exact, S1t 4/4, S2 `WhileLoop 3→6` / `Diagram 170→173`, all 23 moves,
`#5058` deleted and `GPU_kernel_v1.vi` dropped, 8 registers created, panel 114 intact, `#637`'s conditional
terminal still **648 ← w3457**, original md5 unchanged before and after). Then, of **66 routable rows attempted**:

| outcome | n | what it proves |
|---|---:|---|
| **WIRED** | **35** | body-to-body named wiring WORKS on a nested diagram (`g.wire` via Traverse class+index — 10 rows, into `CaseStructure` / `ForLoop` named tunnels and from `ControlReferenceConstant`s); `wire_sr` LeftIn/RightIn WORKS on the new loops (20 rows); **`OpCreateConstOnTerm_v0` placed 5 literals in the real VI** with the originals' values (0, 0, 0, 1000.0, 0 → uids 25591 / 25633 / 10412 / 25697 / 25843) |
| **FAILED** | **7** | 6 × `wire_control` → **error 5001 from `Get Controls.vi`** (`Auto-Reset`, `Reset Tracking`, `Correction Factor`, the two newline-labelled For-loop controls); 1 × `g.wire` `'subarray' → 'x'` → 5001 from `Get Outputs.vi` |
| **NO-ROUTE** | **24** | 8 rows whose sink or source terminal has **NO NAME** (a structure's selector / an unnamed tunnel) and 16 `from-tunnel` rows whose outer wire has no NAMED node source — the value arrives from further out through more unnamed tunnels |

End state: `S3d` unresolved (the six seam tunnels are in the NO-ROUTE set), the three new loops' conditional
terminals read **4767 / 8908 / 13038 with wire 0** (stage 2 not run), 23 junk Invokes purged, **ExecState 0**, so
nothing was saved and the working copy was deleted. Handles 31,283 → 34,415.

## 5. What this measured, and what it did not

It is a **measurement, not an inference**: every row was attempted against LabVIEW and the log says per row what
happened. The capability that is missing is now stated exactly — **a wire creator that addresses BOTH ends by
INDEX on nested diagrams.** `gscript.wire` / `wire_control` are name-addressed (`gscript.py:1144-1147`);
`connect_terminals` (`:2202`) and `connect2` (`:2428`) both take a **top-level** source. `OpStopFromNode_v0`
already proves the sink half — its ladder reaches `WhileLoop[i].Diagram.Nodes[n].Terminals[t]` and invokes
`Terminal.Connect Wire` **6349C03** with a body terminal as `Wire Source` — so the fourth op is that ladder
duplicated for the source side. That is a NEW op beyond the three §11j authorises, and only judgement lifts it.

N1 / F1 / F2 were not run: they need a saved D1 VI at ExecState 1, and there is none.
