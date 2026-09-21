# `ensure_loaded` reach audit — every `tools/gscript.py` wrapper that RUNS an op VI

**2026-09-21, cycle 67 material #4, Part B. STATIC READ ONLY — nothing was repaired here.**

**The measurement it came from:** cycle 67 material #3 (`tools/bench/diag_c67_opvi.log`) measured that
`g.add_shift_reg` on a target whose front panel had **not** been opened RUNS, returns a uid, writes an empty
error cluster and **creates nothing** (legs L1 and L4, two different targets); with `g.open_panel(target)`
first it mints the register and takes `ExecState` 1 → 0 (leg L3), and one prior `move_in` — whose own body
calls `g.ensure_loaded` (`tools/recipes/build_d1_v0.py:321`) — has the same effect (leg L2). This is the
silent-decline class `tools/gscript.py:1284-1338` already documents. `add_shift_reg` was the one wrapper in
its family that never reached `ensure_loaded`.

**Method.** AST over `tools/gscript.py`: every top-level function that calls both `op(...)` and `_run(...)`
(= runs an op VI), classified reader vs mutator from its own docstring/body, then checked for a load
(`ensure_loaded` / `open_panel`) of the file it edits, lexically before the op run that edits it.
53 wrappers run an op VI. **Line numbers are post-Part-A.**

> ⚠️ Any verb in DOES NOT REACH can silently decline exactly as `add_shift_reg` did: the op runs, the error
> cluster is clean, and nothing is created. **This is an inventory for judgement — repairing them is not
> authorised by this dispatch.**

## DOES NOT REACH — 9 mutating wrappers

| wrapper | line | what it mutates | note |
|---|---|---|---|
| `connect_ctl` | 999 | wires a node terminal to a front-panel object's terminal | no loader call anywhere in the body; its docstring already says "Verify by EFFECT" |
| `queue_node` | 1138 | places a queue primitive on `Diagram[diagram_index]` | verifies by a `Function` uid diff and raises on a reported error, but a silent decline returns `[]`, not an error |
| `loop_in` | 1171 | creates a For/While loop inside `Diagram[diagram_index]` | verifies by a `ForLoop`/`WhileLoop` uid diff; a silent decline returns `[]` |
| `loop_kernel` | 1820 | For loop + kernel subVI + tunnel wiring | verifies by three counts and raises on each — a silent decline would raise, not pass |
| `copy_into` | 1415 | edits `MOVE_DST` (substitution protocol), then copies back | no loader of `MOVE_DST` before the op run |
| `copy_by_index` | 1495 | edits `MOVE_DST` | its only `open_panel(MOVE_DST)` is at 1553, **after** the first op run |
| `move_by_label` | 1577 | edits `MOVE_DST` | reaches `open_panel` only through `save`→`gui_save`, i.e. after the edit |
| `delete_by_label` | 1681 | edits `MOVE_SRC` | same; guarded by `if not gone: raise`, so a silent decline raises |
| `make_default` | 2859 | panel DEFAULT VALUES of `target` (not diagram structure) | op run at 2868 with no prior load; returns `save(target)` |

## REACHES — 28 mutating wrappers

`add_shift_reg` :673 (**repaired in Part A, `ensure_loaded(target)` at :708**) · `wire_sr` :723 (**repaired in
Part A, :750**) · `exit_while` :1099 (:1118) · `while_loop` :1207 (:1213) · `for_loop` :1226 (:1227) ·
`drop_subvi` :1241 (:1243) · `wire` :1356 (:1379) · `exit_loop` :1737 (:1750) · `wire_indicators` :1772
(:1797) · `set_index_mode` :1871 (:1882) · `tunnel_indicator` :1898 (:1923) · `wire_control` :1944 (:1958) ·
`build_invoke` :2175 (:2186) · `build_property` :2210 (:2217) · `delete_object` :2291 (:2309) · `move_object`
:2350 (:2356) · `build_index_array` :2373 (:2381) · `create_control` :2411 (:2418) · `create_indicator` :2439
(:2442) · `connect_terminals` :2461 (:2472) · `remove_bad_wires_scripted` :2537 (:2540) ·
`set_auto_error_handling` :2671 (:2675) · `connect2` :2687 (:2691) · `set_node_label` :2710 (:2714) ·
`move_out` :2728 (:2732) · `build_clfn` :2750 (:2774 — before the op run that edits `target` at :2782; its
earlier `_run(pre)` at :2773 drives a preprocessor op that never touches `target`) · `conpane_assign` :2825
(`open_panel(target)` :2832 + `ensure_loaded(target)` :2836) · `build_case` :2875 (:2885) ·
`connect_nested_v2` :2908 (:2934).

## Readers — 16, correctly NOT loading (by design, `ensure_loaded`'s own docstring, "WHY READERS DO NOT CALL IT")

`report` :455 · `report_all` :488 · `subvis` :525 · `node_labels` :587 · `loop_cast` :626 · `shift_reg` :769 ·
`shift_reg_left` :802 · `panel_wiring` :842 · `node_terms` :886 · `tunnels` :957 · `count` :1021 ·
`fp_labels` :2491 · `node_info` :2513 · `net_map` :2556 · `conpane` :2798 · (`connect_nested_v1` is not in
`gscript.py`; it lives in `tools/recipes/build_opconnectnested_v1.py:421`, which does call `g.ensure_loaded`).

`subvis` and `net_map` do call `delete_object` (→ `ensure_loaded`) inside a junk-`Invoke` purge branch
(:567, :2642); that is a conditional cleanup after their own op run, not a pre-edit load, and they are
readers, so it is not a defect.
