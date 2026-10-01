# Brief for card 123-3 — the routes ring P3a needs (cycle 123 judgement, 2026-10-01)

Decision: `docs/d1-loop12-17-split-plan.md` Pre-decided **246(c)(e)**. Route facts: card 123-2's
`tools/bench/routes_c123_ring_p3.json`, `tools/bench/facts_c123_p3.json`, `tools/bench/ring_p3_steps.md`.
Work only on BYTE COPIES of the bed `claudeDev\D1_ring_p2b_20261001_140658.vi` (md5 `652b1447ebbda761a7d5ba36455a0fa1`).
The bed is never saved over and its md5 must be unchanged at the end. Scratch copies are deleted, or kept as
`claudeDev\scratch_c123_*.vi` with their md5 recorded. Every script is a ≤ 120-line stagekit file.

## STEP 1 — measurements on one scratch copy (one LabVIEW run, read back, no save over the bed)
Record each in a `tools/bench/scratch_verify/` record (classes created, terminal names, uids, wires), with the log line.
- (a) `case_in` into a While body: a Case structure on While `#637`'s body `639`, its boolean selector wired from an
  `Equal?` whose inputs are BufNum (`#6810` t6897, wire w3747) and a placeholder. What LabVIEW creates (case frames, their
  names, the selector terminal, tunnels).
- (b) The `$work` node donor for `Equal?`, `Increment` and `Quotient & Remainder` (a node of that function duplicated from
  the work VI into `639` or a case frame): created classes and terminal names for each.
- (c) The For-loop output tunnel: route `nested` from `IMAQ Create #23099` New Image (`t23289`, unwired today) inside For
  `#23093` (body `23169`) to a sink inside While `#637` (e.g. an `Index Array` placed for this measurement). Read back the
  For tunnel's indexing mode, the array type that reaches the sink, and every flat-sequence tunnel created on the way.

## STEP 2 — build the SR-initialisation route
A numeric constant of a given representation and value on the loop's OWNER diagram (here FS1 frame `686`), wired to the
LEFT shift register's outer face of a While loop (here `#637`). Today `connect_route` refuses a constant source into a
shift-register face (`stagexec.py:932-937`) and `const_on_term` refuses a sink whose diagram is not a While body
(`stagexec.py:2219-2223`). The mechanism is yours to measure (`OpConstInd_v0` already puts valued constants on a
flat-sequence frame, PD242(a)/243(a)). Deliver:
- the gscript verb and the stagexec plan route, a stagesim model, and an opmodel record whose samples include the classes
  each call CREATES (e.g. a constant plus anything LabVIEW adds);
- a scratch verification on a bed copy: add a shift register to `#637`, initialise it with an I32 −1 and with a U32
  4294967295 from constants on `686`, and read back value, representation, wire and the register's left outer terminal;
- a self-test; and a hygiene record (≥ 2,000 consecutive calls, 0 errors, handles flat ±100) for any NEW op VI —
  `gscript.op()` refuses a new op without it.

## Rules
- Do not run a stage recipe; this card builds and measures routes only.
- GUI only if a step truly needs it, through `lv_gui.ps1 -Exception Approved`, capture → locate → act → capture → confirm.
- LabVIEW closed and verified gone after each LabVIEW run.
- Return at the first unexpected result in STEP 2 (a measurement in STEP 1 that comes out "unexpected" IS the fact to
  record, not a failure).
