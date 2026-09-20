---
type: doc
status: current
date: 2026-09-19
tags: [s0, hygiene]
---

# S0-α — the DIFF: the build of this construction that WORKS vs the one that FAILS

`docs/cycle27-plan.md` Pre-decided 25, sub-step **S0-α** ("no LabVIEW at all"). One build of a For Loop +
`Close Reference`-style body node around the `References` array of this op family ends `ExecState` **1**; four runs of
the other end **0**. This file enumerates every ordered construction difference between them. It decides nothing.

- **WORKS, ends `ExecState` 1** (2026-09-13) — `tools/recipes/build_opreportall_v1.py`; record
  `docs/toolkit-capabilities.md:400-402`, `:409`, `:415-418`, `:432-438`.
- **FAILS, ends `ExecState` 0, replicated ×4** — `tools/recipes/build_s0_closeref_v3.py`; log
  `tools/bench/build_s0_closeref_v3.log` (ARM `:50`, OpReport_v4 `:99`, OpWireSource_v6 `:158`, OpReportAll_v1 `:202`).
  `…_v1.log` is the earlier run of the same failure.

Where the two sides use different helpers for the same step, the **callee** is quoted (Pre-decided 21(f)).
"W" = the working build, "F" = the failing build. Rows are in construction order, then cross-cutting.

| # | construction point | W — `build_opreportall_v1.py` (ends 1) | F — `build_s0_closeref_v3.py` (ends 0) |
|---|---|---|---|
| D1 | **which FILE the edits are applied to** | the target itself, at its `claudeDev` path: `shutil.copyfile(SRC, OP)` then `g.open_panel(OP)` — `build_opreportall_v1.py:121-123`; every op call takes `OP` (`:54-55`) | **the Move-example fixture**, not the target: `copy_by_index` substitutes the target's bytes into `MOVE_DST` and every edit in `FINISH` runs on that path — callee `tools/gscript.py:1518`, `:1536-1543`; `MOVE_DST` = `claudeDev\NIScriptingExamples\Moving Objects\Test - Moving Objects Target.vi`, `tools/gscript.py:78-80`. The result is file-copied back only after `ExecState==1` (`tools/gscript.py:1548-1557`) — so on a failure nothing is written at all (log `:101`, `:160`, `:204`) |
| D2 | **where the body node COMES FROM** | created natively in the target: `g.build_property(...)` — call `build_opreportall_v1.py:144-149`, callee `tools/gscript.py:2188` | **copied out of another VI**: `g.copy_by_index(DONOR, "Function", i_cr, dst, expect_uid=157, finish=FINISH)` — call `build_s0_closeref_v3.py:587`, donor `KernelBuilder_v1.vi` `:156`, uid `:157`, callee `tools/gscript.py:1479-1558` |
| D3 | **node CLASS put in the loop body** | a **Property** node, 4 items (`Position`/`UID`/`ClassName`/`Owner`) — `build_opreportall_v1.py:144-149`; a second Property node at `:162-165` | a **Function** `Close Reference`, terminals `[(0,'error out',True),(1,'error in (no error)',False),(2,'reference',False)]` — log `:68`, `:176`; recipe `:159-161` |
| D4 | **how the node reaches the body diagram** | built **directly on** the body diagram: `diagram_index=body` — `build_opreportall_v1.py:149`, callee `tools/gscript.py:2188`; body index from `report(OP,'Diagram')` `:137-142` | lands on **diagram 0** at `(0,75)` and is then **REPARENTED**: `move_in(dst, cr, body_i, (24,24))` — call `build_s0_closeref_v3.py:528` (new-loop) / `:453` (existing loop), callee `tools/recipes/build_d1_v0.py:318-335`; landing position log `:66`, `:174` |
| D5 | **satellite objects the copy brings** | none — `build_property` adds one Property node | the copy reports the Function **plus 3 `ParameterTerminal` objects** at `(24,99)`/`(0,99)`/`(0,75)` — log `:66`, `:174`; only the Function uid is reparented (`build_s0_closeref_v3.py:528`) |
| D6 | **the old consumers of `References`** | **DELETED FIRST, on purpose**: `delete_object(OP,'IndexArray',0)` then both old Property nodes — `build_opreportall_v1.py:129-133`, callees `tools/gscript.py:2234`; stated reason at `:127-128` (*"wiring it into a loop would need branch=True - or, far better, delete the consumer FIRST and the source is free"*); recorded as steps 1-3 in `docs/toolkit-capabilities.md:432-434` | **kept**: nothing is deleted anywhere in the recipe; diagram 0 still holds `Index Array #167`, `Property #241`, `Property #482` when the loop is built — log `:65` ("nodes on diagram 0 before = 5"), `:70` |
| D7 | **`remove_bad_wires_scripted`** | **CALLED, twice**, after each deletion — `build_opreportall_v1.py:130`, `:133`, callee `tools/gscript.py:2477`; recorded as its own step, `Wire 17->14`, `docs/toolkit-capabilities.md:433` | **NEVER CALLED.** The name appears once, in prose about a *past* result — `build_s0_closeref_v3.py:27`. No call site exists in the file |
| D8 | **VI state when the For Loop is created** | legal: `ExecState 1` after the deletions, before the loop — `docs/toolkit-capabilities.md:434` (step 3) | **unread**: the `Close Reference` is already on diagram 0 with `reference` and `error in` unwired (log `:69`, `:177` — both `wire: 0`) and no `ExecState` is taken between the copy and the loop (`build_s0_closeref_v3.py:507-528`) |
| D9 | **For Loop creation** | `g.for_loop(OP, (1400, 900))` — literal position, `build_opreportall_v1.py:136`, callee `tools/gscript.py:1210` | `g.for_loop(dst, loc)` with `loc` computed from the node bounding box `(max x + 220, min y + 40)`, then re-found by `g.find_at(dst,'ForLoop',loc,tol=80)` — `build_s0_closeref_v3.py:522-526`. **Stage 3 (`OpReportAll_v1`) creates NO loop at all** — it reuses the existing one (`:451`, log `:178`) and still ends 0 (log `:202`) |
| D10 | **the boundary-crossing WRITER** | `g.wire(OP,'SubVI',0,'References','Property',idx,'reference')` — node/terminal **by name**, tunnel auto-created — call `build_opreportall_v1.py:158-160`, callee `tools/gscript.py:1340-1390` (auto-create documented `tools/gscript.py:1379-1380`, `docs/toolkit-capabilities.md:408`) | `connect_from_wire(dst, wire_uid, src_term_index, body_i, node_i, term_i, CFW_LABELS)` — **wire-anchored branch**, sink addressed by `Diagram[d].Nodes[n].Terminals[t]` **index** — call `build_s0_closeref_v3.py:429`, `:540-542`, callee `tools/recipes/build_opconnectfromwire_v0.py:381-420` |
| D11 | **state of the source wire at crossing time** | the source terminal is **FREE** — its only consumer was deleted at D6 (`build_opreportall_v1.py:129-130`) | a **LIVE wire is branched**: `References` still drives `w188` into `Index Array #167` — `build_s0_closeref_v3.py:518-520`, log `:72-73`, `:79-81` (`branch of w188` → sink `w636` = SEGMENTED). Stage 3 branches `w421` (`dw=0`, EXACT) — log `:190-192` |
| D12 | **what the crossing produced** | `LoopTunnel 0->1, Wire 17->18`, **`ExecState 0->1`** — `docs/toolkit-capabilities.md:402`, `:409`, `:438` | `LoopTunnel` appears (`#642`, IndexMode **1 as read**), `Is Broken? False`, **`ExecState` after the write = 0** — log `:80-87`; recipe gates `:546-549` |
| D13 | **IndexMode handling** | not touched on the input tunnel (it came up auto-indexed); `set_index_mode` is used only on the **output** tunnels — `build_opreportall_v1.py:197`, callee `tools/gscript.py:1855` | read-then-write on every **input** tunnel: `settle_tunnel(..., want_mode=1)` for `References`, `want_mode=0` for the error chain — `build_s0_closeref_v3.py:303-316`, `:548`, `:573`; both already matched as read (log `:85-86`, `:95-96`) |
| D14 | **error-chain wiring into the loop body** | **none** — no error wire is made anywhere in the build (`build_opreportall_v1.py:129-183`) | a **second boundary crossing**: the panel `error out` net (`w425`, owner = the Traverse `#124`) is branched into `Close Reference.error in`, creating a second `LoopTunnel` at IndexMode 0 — `build_s0_closeref_v3.py:551-573`, log `:88-96`. In the existing-loop stage the same job is done by a **third writer**, `connect_nested_v1` — call `build_s0_closeref_v3.py:494-495`, callee `tools/recipes/build_opconnectnested_v1.py:418`, log `:197-199` |
| D15 | **loop OUTPUT side** | four auto-indexed **output tunnels** + typed indicators — `g.exit_loop(...)` `build_opreportall_v1.py:175-183` (callee `tools/gscript.py:1721`), `g.tunnel_indicator(...)` `:201`. (Note: `ExecState` was already 1 before any of this, `docs/toolkit-capabilities.md:438`) | **none** — no output tunnel and no indicator is ever created; the body node's `error out` is deliberately left unwired (`build_s0_closeref_v3.py:369-370`) |
| D16 | **auto error handling** | never touched | switched **OFF** on every stage, immediately before the final `ExecState` read — `g.set_auto_error_handling(dst, False)` `build_s0_closeref_v3.py:368`, callee `tools/gscript.py:2611`; log `:97`, `:200` |
| D17 | **what is SAVED, when, and by whom** | the recipe saves, **once, explicitly, after checking `ExecState`**: `if es != 1: … return 4` then `g.save(OP)` — `build_opreportall_v1.py:216-221`, callee `tools/gscript.py:2056`; policy stated `:41` | the recipe **contains no save call**. The save is inside the copier and is gated there: `if es != 1: raise … ; save(MOVE_DST)` — `tools/gscript.py:1548-1552`; the recipe's own post-hoc gates are `build_s0_closeref_v3.py:611-616`. An unrepaired byte copy left behind is deleted (`:630-638`, log `:101`) |
| D18 | **what is READ, and how often** | a full snapshot after **every** step — `snap()` prints `ForLoop/LoopTunnel/Property/CtlTerm/Wire/ExecState`, `build_opreportall_v1.py:87-90`, called at `:130`, `:133`, `:136`, `:160`, `:171`, `:183`, `:212` | `ExecState` is read only as a by-product of the writer's return (`tools/recipes/build_opconnectfromwire_v0.py:420`) and once at the end of `FINISH` (`build_s0_closeref_v3.py:374-376`). No count snapshot is taken at any point; **no reading exists between the node copy and the first wire** |
| D19 | **LabVIEW instance handling** | one instance for the whole build; the target's panel is opened once (`build_opreportall_v1.py:110-124`), no restart | LabVIEW is **killed and restarted before every stage** (`fresh()`, `build_s0_closeref_v3.py:236-249`, log `:56-58`, `:105-107`, `:164-166`); the panel is opened only by the copier, on `MOVE_DST` (`tools/gscript.py:1537`) |
| D20 | **target identity / name** | a fresh byte copy of `OpReport_v3.vi` written to a **new** name, `OpReportAll_v0.vi` — `build_opreportall_v1.py:54-55`, `:115-121` | fresh byte copies to `OpReport_v4.vi` / `OpWireSource_v6.vi` / `OpReportAll_v1.vi` — `build_s0_closeref_v3.py:147-152`, `:596-599`; the copies are byte-identical and read `ExecState` **1** cold (log `:59-60`, `:108-109`, `:167-168`) |
| D21 | **op-call timeout (shared `_run` default)** | `g._run.__defaults__ = (6.0, 90.0)` — `build_opreportall_v1.py:70` | `g._run.__defaults__ = (6.0, 120.0)` — `build_s0_closeref_v3.py:175` |
| D22 | **error-terminal neutraliser passed to the writer** | `g.wire()` sets no `error in` neutraliser — `tools/gscript.py:1366-1374` | the branch writer force-feeds `("error in", (True, 1, "neutralised creator"))` and zeroes the dead-source controls on every call — `tools/recipes/build_opconnectfromwire_v0.py:393-403`; `move_in` does the same — `tools/recipes/build_d1_v0.py:328-331` |
| D23 | **stop behaviour on a failed gate** | a missed prediction is recorded and the build continues; only `ExecState != 1` at the end blocks the save — `build_opreportall_v1.py:74-84`, `:216-219` | the first failing gate raises `B.Stop` and ends that stage, leaving nothing on disk — `build_s0_closeref_v3.py:621-638`, log `:100-101`, `:203-204` |

**Total: 23 ordered construction differences.**

The three most likely to be load-bearing, given that stage 3 (`OpReportAll_v1`) failed with **no loop creation, no new
tunnel and an EXACT branch** (log `:178`, `:190-192`, `:202`) — i.e. whatever breaks the VI is common to all four
failures and does not need a For Loop:

1. **D2 + D4 — the node is COPIED from another VI and then REPARENTED**, instead of being created inside the body.
   W: `build_opreportall_v1.py:144-149` → `tools/gscript.py:2188`. F: `build_s0_closeref_v3.py:587` →
   `tools/gscript.py:1479-1558`, then `:528`/`:453` → `tools/recipes/build_d1_v0.py:318-335`.
2. **D1 — the edits are applied to the Move fixture `MOVE_DST`, not to the target file.**
   W: `build_opreportall_v1.py:121-123`. F: `tools/gscript.py:1518`, `:1536-1543`, `:78-80`.
   ⚠️ counter-evidence, recorded here so it is not rediscovered: a different op *did* reach `ExecState` 1 inside the
   same hook — `tools/bench/build_opconnectfromwire_v0.log:58` ("W9 ExecState inside finish: 1").
3. **D7 — `remove_bad_wires_scripted` is never called on the failing side**, while the working build calls it twice
   and the record lists it as its own step. W: `build_opreportall_v1.py:130`, `:133` → `tools/gscript.py:2477`;
   `docs/toolkit-capabilities.md:433`. F: no call site (`build_s0_closeref_v3.py:27` is prose).

Next after these, on the same evidence: **D18** (no reading exists between the node copy and the first wire, so the
run cannot say which edit first broke the VI) and **D11** (a live wire is branched where the working build freed its
source first, `build_opreportall_v1.py:127-128`).
