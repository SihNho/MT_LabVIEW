# c93b-g5-wiretypes

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.1542  in 24 / out 8397 / cache-create 87848 / cache-read 1138933  (115s, 21 turn(s))
- **date:** 2026-09-26 10:26:45
- **outcome:** ANSWERED (119s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about the failing log tools/bench/diag_c93_wiretypes.log (script tools/bench/diag_c93_wiretypes.py).

CLAIM: gate G5 ("type reader verified on a known-type wire (loop i = I32)") failed because no scripted reader for the property Terminal.Data Type (634A008) exists in our op set (docs/NAMES.md:478-485), and card 93-1 forbade building one (labview=read, no claudeDev write). The failure is a missing TOOL, not a defect in the script's other readings; the per-wire type column of tools/bench/t0at_stamp_wiretypes_93.json is therefore INFERRED, not read.
PREDICTED by the script: a reader exists and returns I32 for the loop i terminal.
OBSERVED: G5 FAIL, "no reader: Terminal.Data Type 634A008 value needs a new op".
CONTEXT: judgement already ruled (docs/d1-loop12-17-split-plan.md Pre-decided 200(b)) that the type column is not needed while 200(a) stands (the stamp DLL flushes to disk inside stamp(), tools/t0stamp/t0stamp.c:61-62,74-78), and the reader is built only if the scalar-only build is revived.
ALREADY RULED OUT: the review archive/peer/2026-09-26-c93-h1-stamp-array-copy.md addressed the array-copy hypothesis, not this gate.

Questions: is "no reader exists" actually true (search docs/NAMES.md, docs/toolkit-capabilities.md, tools/gscript.py for any Data Type / type-descriptor read path, e.g. a flattened type string or Get Terminal type via another property)? Is anything else in that log's PASS rows unreliable because of the same gap?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

The claim is partly wrong. G5 was not a failed prediction: the script hard-codes it to FAIL. "No reader exists" is true only for the LabVIEW op set, and G3's PASS doesn't show anything about types either.

**1. Strongest reason the claim is wrong: nothing was predicted and nothing was measured.**
- `tools/bench/diag_c93_wiretypes.py:79-80` is `gate("G5 …", False, "no reader: …")`. That is a constant, not a reading.
- The script's own docstring says so: *"PREDICTION: … type-reader gate FAILS (no reader)"* (`diag_c93_wiretypes.py:12-14`).
- So the brief's "PREDICTED by the script: a reader exists and returns I32" is untrue. The observed result matches the written prediction exactly. The failed-prediction review was triggered by a gate built to fail, not by evidence about the system.
- It will fail the same way every time the script runs. The "missing tool" label is the author's opinion, written as a gate result.
- Fix: make it an explicit `UNREAD`/SKIP row that the result line does not count as FAIL. A permanent FAIL gate buys a review on every run and teaches the gates to cry wolf.

**2. Alternative explanation: a reader route does exist, just not over COM.**
- The claim equates "no op in our COM fleet" with "no reader". The COM part holds up locally:
  - `docs/NAMES.md:477-485`: `OpNodeTerms_v0` returns only Name, IsSource and WireUID.
  - `docs/cycle27-plan.md:1055,1803` and `tools/bench/device_value_diag_terminal_panel_wire.json`: the same absence was measured several times.
  - I found no `Op*Type*`/`Op*Coerc*` VI in `claudeDev` (Glob, empty).
- But the project already parses `.vi` files offline with pylabview (`tools/bench/diag_c89_profiler_lvsr.py:98-102`, `diag_c89_profiler_lvsr.log:16`). That needs no LabVIEW and no claudeDev write, so card 93-1's flags would allow it.
- pylabview's heap parser has an `OF__typeDesc` object-field tag, along with `OF__dataTypeDesc` and `OF__varTypeDesc` ([LVheap.py](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVheap.py)). In LabVIEW ≥7 the type descriptors themselves sit in the `VCTP` block ([LabVIEW Wiki: Type descriptor](https://labviewwiki.org/wiki/Type_descriptor)).
- If the block-diagram heap (BDHb) records a type-descriptor index on each terminal, the 12 types can be read offline from `D1_s1_t0at_20260926_090833.vi`.
- I have **not** checked that the BDHb actually carries `typeDesc` on terminals, or how LV 2026 encodes it. That is a hypothesis with one source, not a result.
- Separately, the COM route could also fail after an op is built. A type-only Variant may not marshal cleanly over ActiveX. The op would probably need `Data Type` → `Variant To Flattened String` → `type string` (I16[]), then decode against the flattened layout already measured in `docs/NAMES.md:1153`.

**3. Are the PASS rows reliable? Two of them overstate what they show.**
- **G3** ("not broken, sink terminal 'any'") says nothing about type. The stamp CLFN parameter is Adapt to Type (`any`), which accepts any wire, so "not broken" is guaranteed whatever the type is.
- G3 also reads the **t0 step-3c build record** (`tools/bench/t0_sites_s1_step3c_r2.json`), not t0at. The log shows `labview_launched: False`.
- **G2** takes sources from the offline S1 wiki graph (`docs/wiki/subvi/D1_s1_copy.json`). It likewise assumes the wire uids carried over unchanged into t0at through the thread-flag edits and re-save (`diag_c93_wiretypes.py:10`). That is inference; only the md5 in G4 is read from t0at itself.
- 3 of 12 rows (S03, S04, S06, all tunnel sources) have `expect None`. Even the inferred column is incomplete for the rows most likely to be arrays: Median and FIR outputs.
- G1 and G4 are sound for what they claim.

**4. What would falsify the claim.** Either of these would:
- An offline pylabview parse of t0at shows the loop-`i` source terminal (w3268, `Diagram#639`) → a type-descriptor entry that decodes as I32. Then a reader existed within the card's flags and "missing tool" was wrong.
- Or an existing op in `claudeDev` whose traversal includes `634A008`. I found none.

**5. Cheapest test that separates the two.** An offline, read-only Python pass with pylabview over the t0at `.vi` (as `diag_c89_profiler_lvsr.py` already does):
1. Dump the BDHb heap objects for the `Diagram#639` loop and its `i` terminal.
2. Check for an `OF__typeDesc` field and resolve it in the `VCTP` pool.
3. I32 comes back: the claim is falsified, and the tunnel rows S03, S04 and S06 get read the same way. No field is present: the claim stands, and building the op is the only route.

This takes about 10 minutes with no LabVIEW.

**What still holds:** judgement's ruling in `docs/d1-loop12-17-split-plan.md:1238-1240` (Pre-decided 200(b)) survives either outcome. The type column isn't needed while the file-flush explanation in 200(a) stands. So this is a record-keeping correction, not a blocker:
- relabel G5 as UNREAD instead of FAIL;
- G3 does not show types are consistent;
- "no reader" means "no COM op, offline route untested".

This is also at least the fifth time the Terminal.DataType gap has been recorded (`docs/cycle27-plan.md:1055,1803`, c53, s57, c66). It fits the `tool-not-built` class.

Sources:
- [pylabview LVheap.py (OF__typeDesc tags)](https://github.com/mefistotelis/pylabview/blob/master/pylabview/LVheap.py)
- [pylabview repository](https://github.com/mefistotelis/pylabview)
- [LabVIEW Wiki – Type descriptor](https://labviewwiki.org/wiki/Type_descriptor)
- [lvkit issue #104 (heap/typedesc pairing)](https://github.com/pragmatest-dev/lvkit/issues/104)

## Sources

(extract from answer)

## What was done with it

Card 93-2 (material, 2026-09-26): dispatched because `guard_peer` blocked every tools/bench run on
`tools/bench/diag_c93_wiretypes.log` G5. Nothing in the finding was acted on: card 93-2's scope is PD200(c) (flush
alignment, t0stamp v2, ABBA), and PD200(b) already rules the type column unneeded while 200(a) stands. The three
record-keeping points (G5 was a constant FAIL, `diag_c93_wiretypes.py:79-80`; G3 says nothing about types; the
offline pylabview typedesc route is untested) are passed to judgement in result_93-2.json `open`.
