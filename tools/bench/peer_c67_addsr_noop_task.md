# ATTACK this claim. Cycle 67 material #2, LabVIEW 2026 (26.3.1f1) VI Scripting over ActiveX/COM.

## 0. THE FAILING LOG UNDER REVIEW

`tools/bench/diag_c67_m3a.log` — `BGRUN END rc=1 after 663s`, GATES 75 pass / 8 fail.

The failed prediction is explicit in our own source. `tools/gscript.py:683-687` says of
`add_shift_reg`: *"BOTH SIDES COME BACK UNWIRED, and an unwired register breaks the VI (ExecState 0)
until they are wired — that is correct, not a failure."* We predicted a created register and
`ExecState` 0. We observed **no register at all and `ExecState` 1**.

## 1. THE MEASURED FACTS — all verbatim from `tools/bench/diag_c67_m3a.log`

- Both `add_shift_reg` calls on While Loop `#23032` returned the **SAME uid 23561** with error `''`
  (empty string) — `:61` and `:72`.
- Whole-VI class censuses **UNCHANGED across both calls**: `Node` 632 / `Wire` 1907 / `LoopTunnel` 135 /
  `Tunnel` 471 (`:105`).
- `ExecState` stayed **1** after both calls (`:63`, `:74`) — not the 0 our docstring predicts.
- `shift_reg(#23032, reg_index 0..7)` returns **error 1055 at EVERY slot** (`:83-100`) — i.e.
  `Loop.Shift Registers[]` on `#23032` is EMPTY.
- The SAME reader is not broken: `shift_reg_left` read **three real pairs on While Loop `#637`** in the
  same run (`:44-46`), with names and wire uids.
- `#23032` does **not** sit on the VI's top-level diagram: it is on `Diagram #686`, traverse index 19
  (`:53-55`). Traverse index 0 is `TopLevelDiagram` uid **536 with 0 nodes**.

## 2. ALREADY RULED OUT — do not spend your answer on these

- **The op is not simply broken.** The identical `shift_reg_left` reader returned three real register
  pairs on `#637` in the same run and the same process.
- **The loop reference is not stale by construction**: the `loop_index` used for the call echoed uid
  `23032` immediately before the call.
- **Nothing was saved and nothing else was edited** in the segment under review.

## 3. THE CLAIM TO REFUTE

> **`Loop.Add Shift Register` (method 6361000) silently does nothing when the target loop is not on the
> VI's top-level diagram, and `OpAddShiftReg_v0`'s returned uid 23561 is therefore stale — a value read
> back from a reference that no longer names a created object.**

Attack it. Give the strongest reason it is wrong, an alternative explanation of the measurement, what
would falsify it, and the cheapest discriminating test.

## 4. SPECIFICALLY: NAME AT LEAST TWO RIVAL CAUSES YOU RATE HIGHER

Rate each, and for each give the cheapest discriminating test in terms of readings we can take over
this COM path. Candidates we have already thought of, which you should judge rather than merely repeat:

- **(i) `y_position`** — the op takes a y coordinate. If the y we passed falls outside `#23032`'s own
  vertical span, does LabVIEW decline the insertion silently rather than clamping?
- **(ii) TRAVERSE ORDER MISMATCH** — the op VI does its own `Traverse for GObjects` internally. If its
  enumeration order differs from the `report_all` ordering the Python side used to pick `loop_index`,
  the op targeted a DIFFERENT While Loop, one that legitimately has no new register visible to our
  later `shift_reg(#23032, …)` read. What would we see in that case, and how do we separate it from a
  true no-op?
- **(iii) THE CAST** — we pass `class_name='WhileLoop'` and the op downcasts the generic reference. Does
  LabVIEW accept a reference of the wrong or of an over-general class for this method and ignore the
  call, or does it error 1055/1057?

Also answer directly: **what does `Loop.Add Shift Register` actually return**, and is an empty error
string from our wrapper proof that the method itself ran?

## 5. WHAT I WILL DO WITH YOUR ANSWER

The next diagnostic is a pure READER: five legs on five fresh scratch duplicates of one read-only bed,
nothing saved, nothing built. Each leg takes the SAME census — for every `WhileLoop` and `ForLoop` uid
in the VI, probe `shift_reg`/`shift_reg_left` at reg_index 0..7 and count the slots that answer WITHOUT
error 1055 — plus `ExecState`, the four class counts, and a full `GObject` uid-SET diff (`minted` /
`vanished`). So optimise your answer for **"what will that census show, and what is he going to conclude
wrongly from it"**, not for whether to run it.

🔴 Route changes, new verbs and re-orderings are recorded verbatim and NOT acted on by me — the reader
runs as specified regardless. Tell me anyway; the judgement session reads them.
