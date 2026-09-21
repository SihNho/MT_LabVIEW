# REFUTE THIS CLAIM — `OpAddShiftReg_v0.vi` never executes at all

## Context, all of it MEASURED on this machine (LabVIEW 2026, Windows, COM/ActiveX VI Server)

We drive LabVIEW from Python over COM. A thin wrapper module (`tools/gscript.py`) calls small
single-purpose "op" VIs by `Application.GetVIReference(path)` + `SetControlValue(...)` + `Run` +
`GetControlValue(...)`. One of them, `OpAddShiftReg_v0.vi`, is supposed to invoke
`Loop.Add Shift Register` (method 6361000) on a While loop inside a target VI and return the new
`RightShiftRegister`'s uid.

**`add_shift_reg` is a measured NO-OP on EVERY loop tried**, in the log
`tools/bench/diag_c67_addsr.log` (`BGRUN END rc=1 after 1702s`, 38 pass / 13 fail):

* Leg 1 — While loop uid `#23032`, default `y_position`.
* Leg 2 — the same `#23032`, with a `y` MEASURED to lie inside that loop's own vertical span
  (existing registers on this VI sit at y offsets −229 … +748 from their loop's Position top, so
  the y used was inside the span by measurement).
* Leg 4 — While loop uid `#637`, a completely different loop that ALREADY CARRIES 14 shift
  registers (8 readable left/right pairs read back by the same fleet's `shift_reg_left` op).

Three separate loops, three separate scratch copies of the VI, three separate runs. In every one:

* the wrapper returned the **SAME uid 23561** with error string **`''`** (empty);
* **uid 23561 does not exist** among the VI's **10,028** `GObject` rows;
* `GObject` 10028 → 10028, `minted []`, `vanished []`;
* `LeftShiftRegister` 36 → 36 and `RightShiftRegister` 36 → 36, both `minted []`;
* `Tunnel` 471 → 471 (both shift-register classes derive from `Tunnel`, so this count is itself a
  creation detector);
* `Node` 632, `Wire` 1907, `ControlTerminal` 116, `Local` 10, `LoopTunnel` 135 — all unchanged;
* `ExecState` **1 → 1**, where the wrapper's own docstring (`tools/gscript.py:683-687`) states that
  a newly created, unwired register breaks the VI, i.e. predicts `ExecState` 0;
* `#23032` reads class `'WhileLoop'`, is index 2 of 6 in `report_all('WhileLoop')`, and its uid was
  echoed off the machine immediately before every call, so the addressing was right.

## Already ruled out (do not re-argue these)

1. **Geometry** — `y_position` was varied and measured inside the loop's own span; no change.
2. **Loop identity / addressing** — uid echoed at the index before each call; class confirmed
   `'WhileLoop'`; 23 loops (6 While + 17 For) all unchanged in the register census.
3. **The top-level-diagram hypothesis** (`#23032` sits on a nested `Diagram #686`, traverse index 19,
   not on the top-level diagram) — REFUTED by leg 4, because `#637` is a different loop entirely and
   behaves identically.

## The claim to refute

> **`OpAddShiftReg_v0.vi` never executes at all. The wrapper reads its `uid` indicator's SAVED
> DEFAULT, which is why one constant 23561 appears for three different loops in three different
> files and why the error string is empty — `_run()` reports nothing because the op's own error
> indicator is never written. The register is never attempted, so the loop, its geometry and the
> diagram's nesting are all irrelevant.**

## The relevant wrapper code, verbatim

`tools/gscript.py:699-707`:

```python
vi = op(os.path.join(CLAUDEDEV, "OpAddShiftRegF_v0.vi") if class_name == "ForLoop" else OP_ADD_SHIFT_REG)
vi.SetControlValue("vi path", target)
vi.SetControlValue("Class Name", class_name); vi.SetControlValue("index", loop_index)
vi.SetControlValue(lab["y_position"], int(y_position))
_run(vi)
err = _err(vi, lab["error"]) if "error" in lab else ""
if err:
    raise RuntimeError(f"add_shift_reg: {err}")
return int(vi.GetControlValue(lab["uid"]))
```

`tools/bench/opaddshiftreg_labels.json` = `{"y_position": "Y Position", "uid": "UID 2",
"error": "error out 3"}`.

`op(path)` (`:210-215`) is a CACHED `Application.GetVIReference(path, "", False, 0)` — one
long-lived reference per op VI, reused across calls for the life of the Python process.

`_run(vi)` (`:341-432`) marshals the `IDispatch` to a daemon thread and calls
`disp.Invoke(disp.GetIDsOfNames(0, "Run"), 0, pythoncom.DISPATCH_METHOD, 1)` under a watchdog
(polls for modal dialogs) and a hard 180 s cap. It raises on: a COM exception from `Run`, a watchdog
dialog hit, or the cap expiring. Otherwise it returns elapsed seconds. It does **not** read any
status back from the VI.

`_err(vi, name)` (`:435-450`) does `status, code, src = tuple(vi.GetControlValue(name))` inside a
bare `try/except` that **returns `None` on any exception**, and returns `None` when `status` is
False.

## What we need from you

1. **Attack the claim.** Give the single strongest reason it is WRONG, and an alternative
   explanation of the same three observations (constant uid, empty error, zero object creation,
   `ExecState` unchanged) that does NOT require the op VI to be un-run.

2. **Name the READS that distinguish "the op never ran" from "the op ran and
   `Loop.Add Shift Register` declined silently."** Be concrete about what is readable over the
   ActiveX `VirtualInstrument` surface (`GetControlValue`, `SetControlValue`, `Run`,
   `OpenFrontPanel`, `ExecState`, `Call Chain`, etc.) and over VI Scripting from a *separate* op
   VI. **Say which of your proposed reads is CHEAPEST**, and rank them.

   In particular, address: is there any read that proves a VI's block diagram actually executed, as
   opposed to inferring it from an output value? (Consider: a sentinel/counter indicator whose
   default differs from what any execution would write; `VI.Execution >> Call Chain`; run-count
   properties; the FP indicator's value before vs after an explicit `Make Current Values Default`
   comparison; reverting the op VI and re-reading.)

3. **What, in a fleet like this one, can make `Run` return silently on a VI that is itself BROKEN,
   or on a VI that has never been reserved for running?** Specifically:
   * Does LabVIEW's ActiveX `VirtualInstrument.Run` raise, or silently no-op, when the target VI's
     `ExecState` is 0 (broken)? Cite behaviour, not intuition.
   * Does it raise or no-op when the VI is in an edit-mode / not-reserved state, or when its front
     panel has never been opened?
   * Can `Run` succeed while the diagram short-circuits — e.g. an error cluster arriving from a
     prior step, a Case structure's default frame, a disabled diagram structure, an unwired
     Invoke Node — leaving every indicator at its saved default?
   * Is there any way `SetControlValue` on a control name that does not exist on the panel fails
     silently rather than raising, so the op runs on stale/default inputs? (We call
     `SetControlValue("vi path"/"Class Name"/"index"/"Y Position", …)` without checking those names
     exist.)

4. **What would falsify the claim, and what is the cheapest discriminating test?** We can run
   read-only inspections of the op VI (its `ExecState`, its full panel control/indicator list with
   loaded values, md5) and single write legs on throwaway copies of the target. We may NOT edit the
   op VI, may NOT edit `tools/gscript.py`, and may NOT save anything.

## Constraints on your answer

* We are a behaviour-preserving refactor of a production LabVIEW VI; the original is never modified.
* Answer with **reads and tests**, not with a redesign. Any route change, new verb, new op VI or
  repair you propose will be quoted verbatim and handed to a separate judgement session — it will
  NOT be acted on by the session that receives your answer. So make the *diagnostic* half of your
  answer as self-sufficient as possible.
* Where you assert LabVIEW behaviour, say whether it is documented, measured elsewhere, or inferred.
