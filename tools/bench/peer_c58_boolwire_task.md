ATTACK this claim. It is the explanation this project formed for a FAILED PREDICTION, and the next build
depends on it. Find the strongest reason it is WRONG.

# The failed prediction

`tools/bench/diag_s58_boolcarrier_run2.log` (cycle 58 material #1, run 2, `BGRUN END rc=1 after 248s`,
54 pass / 9 fail) predicted, in its own docstring, gate `B3b`: *"ExecState after the delete == 1"*.
It measured **0**, on all three candidates (gate lines `C1 B3b` / `C2 B3b` / `C3 B3b`).

# THE CLAIM UNDER ATTACK (written into docs/cycle27-plan.md as Pre-decided 48(b)+48(d))

> A Boolean type needs a **SOURCE** terminal, and `create_indicator` on a SOURCE terminal makes a REAL wire.
> The whole-VI `Wire` count reads 1905 -> 1905 (after `build_property` places the carrier) -> **1906** (after
> `create_indicator`), the added wire's uid is **23586** on candidate C1 and **23576** on C2/C3, and that wire
> is **STILL ALIVE after `delete_object(carrier)`** with **0** pre-existing wire uids removed. `ExecState`
> reads 1 (baseline) -> 1 (after `build_property`) -> 1 (after `create_indicator`) -> **0 (after the carrier
> delete)**. THEREFORE: the indicator is left sourced by a wire whose node is gone, and **that dangling wire
> is what takes the VI to ExecState 0** — so deleting that wire BY ITS UID, before deleting the carrier, will
> leave both ends unwired and return the VI to ExecState 1, i.e. to the state cycle 57 saved from.

That last sentence is the load-bearing one: the next build (three saved sub-steps, `delete_object(target,
"Wire", <index of uid 23576>)` before `delete_object(carrier)`) does nothing else differently.

# What has already been ruled out (do not spend the review re-deriving these)

* `remove_bad_wires_scripted` is REFUSED as the repair: it has a measured over-removal on THIS VI
  (`archive/2026-09-17-status-d1-route-b-2.md:45`, "DELETES THE TUNNEL"), a rule-1a hazard. Not a candidate.
* The reverse route — never deleting the carrier at all — is a different route (47(i) route 2) and is not
  what this review is about.
* An earlier review of the same failure, `archive/peer/2026-09-21-c58-delete-execstate0.md`, returned
  `REFUTED — the "dangling wire" is not established by this log`, and stated its own falsifier: *"if uid 23586
  is alive after the delete, I am wrong about the mechanism and the claim's cause stands"*. Run 2's `B3d` step
  read it **ALIVE** on all three candidates. Read that archive file; say plainly whether that falsifier firing
  actually rescues the claim, or whether the claim can still be wrong for a reason that review did not name.

# Specifically

1. The strongest reason `ExecState` would STILL be 0 after deleting that wire by uid — name the mechanism.
2. An alternative explanation of the `1 -> 1 -> 1 -> 0` timeline that does not involve the created wire at all.
   (Note `create_indicator` itself left `ExecState` 1 WITH the wire present — what does that imply?)
3. What would falsify the claim, and the cheapest discriminating test. The next run reads: `ExecState` and the
   whole-VI `Wire` uid SET after each of `build_property`, `create_indicator`, the WIRE delete, and the CARRIER
   delete; the uid SET that disappeared on each delete; and the ControlTerminal census across the wire delete.
   Say what ELSE should be read in the same run to separate your alternative from the claim — it must be a
   reading, not a mutation.
4. A specific risk in `delete_object(target, "Wire", index)` itself: `tools/gscript.py:2240` addresses by
   (Traverse CLASS, Traverse INDEX), the index being resolved as
   `[o["uid"] for o in g.report_all(target,"Wire")].index(uid)` immediately before the call, with `verify=True`
   so the call returns the uid set that disappeared and raises unless exactly one object went. Is there a way
   this deletes something other than the intended wire, or leaves a stub, on a 1906-wire VI?

Files worth reading: `tools/bench/diag_s58_boolcarrier.py` (the script, its docstring carries the full
prediction contract and the predicted risks), `tools/bench/diag_s58_boolcarrier_run2.log`,
`tools/gscript.py` (`delete_object` :2240, `create_indicator` :2388, `build_property` :2194),
`docs/cycle27-plan.md` Pre-decided 46-48, `archive/peer/2026-09-21-c58-delete-execstate0.md`.

Do not tell me the plan is sound. Tell me where it breaks.
