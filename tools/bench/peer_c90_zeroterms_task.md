# FAILED PREDICTION — attack this reading of the machine

## The prediction that failed
`tools/bench/diag_c90_endpoints.py` gate **E1** predicted that all ELEVEN wires Remove Bad Wires removes from the
D1 Row-D bed — `[1731, 1893, 2819, 3947, 4833, 7337, 7388, 9635, 11232, 23502, 23540]` — would resolve through
`OpWireSource_v5` with at least one terminal carrying a real owner. Measured: **4 of 11 did, 7 of 11 returned no
owner at all** (`tools/bench/diag_c90_endpoints.log:91`, `=== GATES: 14 pass / 1 fail`, `BGRUN END rc=1 after 113s`).

## The claim I am about to build on — attack it
**The 7 wires `[1893, 2819, 4833, 7388, 11232, 23502, 23540]` have ZERO terminals: `Wire.Terms[]` (6371003)
returns an EMPTY array for each, so they are wire objects with no live endpoint at either end, while the other 4
have exactly ONE endpoint each.** If that is true, the next stage (M3a-4, re-wiring the severed rows) cannot
address those 7 by "read the surviving endpoint and re-attach the other" — there is no surviving endpoint to read.

## The measurement, verbatim
- `diag_c90_endpoints.log:25` — Traverse `Wire` census on the work copy: 1920 wires; **all 11 uids are PRESENT**,
  none absent.
- `:78`–`:88` — the table. The 4 that answered:
  `w1731 → LeftShiftRegister #4344 is_source=True recip=1731` · `w3947 → LeftShiftRegister #4274 is_source=True` ·
  `w9635 → LoopTunnel #9641 is_source=True` · `w7337 → RightShiftRegister #4334 is_source=False`.
  The 7 that did not: exactly ONE row, `is_source=None owner_class=None owner_uid=None recip=None`.
- `:34` — the error string on a null row, all six downstream columns:
  `errO=error 1055: Property Node in OpWireSource_v5.vi; errU=…; errG=…; errS=…; errWU=…; errCO=…`.
  **`errT` (`error out 3`, the `Wire.Terms[]` property node's OWN error column, `tools/bench/opwiresource_v5_labels.json:4`)
  is EMPTY on every one of those rows.**
- The 4 answering wires produce the IDENTICAL six-column 1055 signature at terminal index **1** — i.e. one index
  past the end of a one-element array (`:29`, `:44`, …).

## Already ruled out (do not spend the review on these)
1. **Dead / recycled uid.** `wire_source_owner` (`tools/recipes/build_opconnectfromwire_v0.py:464`) breaks with an
   explicit `unresolved` row when the op's uid echo (`UID 3`) differs from the queried uid. That branch NEVER fired
   on any of the 11 — every row printed came from the post-echo path, so the op matched the uid it was asked for.
2. **Reader history-echo.** The answer indicators are scrubbed to sentinels before every single run (`:443-449`),
   and the 4 real answers and the 7 nulls were interleaved in one loop on one open copy.
3. **Node-route blindness.** This is the WIRE route (`Wire.Terms[]` → `Is Source?` 634A003), not `wmap` /
   `Diagram.Nodes[]`; the known "a ControlTerminal is not a Node" limit (`docs/NAMES.md:966-991`) does not apply.
4. **PD85.** Every real-owner row satisfied `recip == queried uid`; 0 violations over all 11 (`:92`).

## What the answer must contain
- The strongest reason the ZERO-TERMINALS reading is wrong, stated as a competing mechanism, not a doubt.
- At least one alternative explanation for "index 0 errors 1055 on six downstream nodes while `Wire.Terms[]`'s own
  error column stays empty" — e.g. anything that makes an Index Array of a NON-empty array still yield an invalid
  reference, or anything in `OpWireSource_v5`'s own dataflow that could null the row without erroring at Terms[].
- What observation would falsify the zero-terminals claim.
- The CHEAPEST discriminating test on this fleet's existing tools, naming the op or property by id. Our fleet has
  `Wire.Terms[]` 6371003, `Is Source?` 634A003, `Generic.Owner` 6327806, `UID to GObject Reference.vi`,
  `OpOwnerChain_v1` (any uid → its owner), `gscript.report_all`/`uids`, and NO standalone `Wire.Is Broken?` 6371004
  reader (`docs/toolkit-capabilities.md:68`). A test requiring a NEW op VI is not cheap and should be named as such.

## Context you may need
These 11 wires were SEVERED (not deleted) by seven `move_in` calls in stage M3a-1 — LabVIEW severs every wire on a
moved object (`tools/bench/build_d1_m3a1.log:2754`, `ExecState` 1 → 0 at `:2778`, Wire census unchanged at 1907
across all seven moves). The artefact is broken BY DESIGN and is never run. The run was read-only: nothing saved,
no op built, the bed's md5 unchanged at both ends, `THE FILES THIS RUN LEFT ON DISK: []`.
