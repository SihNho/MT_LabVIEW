# Under review: `tools/recipes/build_opfstunnelterm_v2.py` — one pre-clean insertion into the frozen `_v1` recipe

Cycle 23, dispatch 3. This is the plan for ONE recipe file, already written and NOT yet run.

## What the recipe is

`tools/recipes/build_opfstunnelterm_v2.py` is a **byte-for-byte copy** of the frozen
`tools/recipes/build_opfstunnelterm_v1.py` (md5 `577669d3bb83b25116cf33b5e6d07bb7`) plus **one functional
insertion** and two docstring lines. Verified mechanically: 187 inserted lines, 0 deleted, and the only two
replaced lines are both inside the docstring (the contract header and the launch line). Every code line of `_v1`
is unchanged. `_v1.py` itself was not edited (editing it bricks its launch path — `stop_record._check:325`).

The insertion is `preclean()`, called once per op from `build_one`, immediately after `shutil.copy2(DONOR, op)` +
`open_panel(op)` (the `_v1.py:403` checkpoint) and **before any construction**:

1. compute the set of Wire uids on diagram 0 that **no owning-node terminal reads at either end**, from the
   recipe's own `sweep()` (OpNodeTerms) plus `gscript.uids(target, "Wire")`;
2. **gate A0a** — that set must be EXACTLY `{894, 1356}`; any other set prints the actual set and ABORTS that op's
   build having removed nothing;
3. **gate A0b** — `Wire.Is Broken?` 6371004 must read True on exactly those two, via
   `diag_fstunnel_wirebroken.read_broken()` (imported, not re-implemented); on anything else it ABORTS, again
   removing nothing;
4. **gate A0c** — `remove_bad_wires_scripted` removes exactly `[894, 1356]` and adds none;
5. **gates A0d/A0e** — wire count 42 → 40, node-terminal count unchanged, `ExecState == 1` before construction;
6. **gate A0f** — a static self-check that this file calls the RBW helper from exactly ONE line, so B4 is reached
   with no RBW call.

## Why (the measurements this cycle produced)

* `tools/bench/diag_fstunnel_rbwvictims.log` (18/18 gates, rc=0): the DONOR `OpWireSource_v5.vi` holds 42 wires
  and **894 + 1356 are already in the donor** (`:14`); neither touches any node terminal (`:80,86`, "END NONE";
  894 has no source terminal, 1356 a source and no sink; both report owner `TopLevelDiagram` #3 — `:81-82,87-88`);
  the first checkpoint at `_v1.py:403` already has both (`:20`, timeline `:94-97`).
* At the B4 point `remove_bad_wires_scripted` removes exactly `[894, 1356]`, adds none, 43 → 41 wires,
  `ExecState 0 → 1` (`:159`), **no node loses a connection** (133 → 133 terminals, "NONE — no terminal that was
  wired before RBW reads 0 after it", `:162-164`), and 1694/1719/1766 survive (`:167-168`).
  ⚠️ CORRECTED 2026-09-18 12:3x — the anchors in this block were WRONG when the review was dispatched (its finding
  B4b caught exactly that); the measured values were right throughout.
* `tools/bench/diag_fstunnel_wirebroken.log` (10/10, rc=0): `Wire.Is Broken?` 6371004 = True on the residual stub
  #384 with the orphans present; False after they are removed (`diag_fstunnel_rbwvictims.log:169-170`).

## The known weakness the reviewer should attack first

Gate A0b may be **unsatisfiable**: `Wire.Is Broken?`'s only Python-reachable carrier
(`OpConnectFromWire_v0`, `docs/NAMES.md:888-897`) reads the value off a SINK TERMINAL's `Connected Wire`, ordered
after a successful `Terminal.Connect Wire` — and an A0a orphan has no sink terminal by construction. If that is
right, `_v2` aborts at A0b on every run and removes nothing. The recipe states this limit in its own contract and
records the independent non-perturbing indicator (≥2 sources = broken, `docs/NAMES.md:900-905`) beside the read.

## Questions for the prior-art review

* Has a donor-copy **pre-clean** (removing the template's own bad wires before construction) already been built,
  tried, or argued against anywhere in this project?
* Is there an existing helper that reads `Wire.Is Broken?` without a sink terminal, or an existing orphan-wire
  reader, that `preclean()` is hand-rolling?
* Has "the donor `OpWireSource_v5.vi` ships with bad wires" already been measured and written down before this
  cycle — and did any earlier recipe built from that donor already work around it?
* Does any active document contradict the claim that removing 894/1356 costs no node its connection?
