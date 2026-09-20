---
type: archive
date: 2026-09-17
tags: [status, relocated, d1, route-a, run9]
---

# Relocated VERBATIM from STATUS.md, 2026-09-17 (material/cycle15-d1-route-A-run-9) — OPEN 33, 34, 35

Rule 4: STATUS.md passed ~110 lines, so the narrative moves down a layer unchanged. Nothing here is rewritten.
Live one-liners stay in STATUS; the current state of route A is `docs/d1-build-plan.md` §11s + STATUS OPEN 36.

34. ✅ **CLOSED BY MEASUREMENT** — it was the TYPE/gate choice, not the op. The discriminator ran inside
   `build_opconnectnested_v1` (two copies of ONE subVI, NAMED `error out` → NAMED `error in (no error)`): op
   error `''`, and **the wire SURVIVES `remove_bad_wires_scripted`**, which a broken wire does not. The old
   "same wire uid on both ends" gate was itself WRONG for this op — a cross-boundary wire is SEVERAL SEGMENTS
   with different uids (`NAMES.md:861-863`; `test_opconnectnested_v1_cold.log`, 7/0).
36. 🔴 **NEW, MEASURED 2026-09-17 (§11s) — route A's remaining 24 rows are TWO problems, neither an addressing
   one.** (a) **16 `from-tunnel`**: the one hop was READ (`diag_tunnelsource_onehop.log` 7/2,
   `d1_tunnel_sources.json`) — **14 sources are `FlatSequenceInnerTunnel`, 2 are `LeftShiftRegister` of `#637`**,
   1 is `SubVI #27605` (wired in run 9), 1 does not advance. A `FlatSequenceInnerTunnel` is on NO `Nodes[]`, so
   `OpConnectNested_v1` cannot name it; codex (r3, ANSWERED) says the API can — `Connect Wire` takes any Terminal
   ref, incl. `Wire.Terminals[]` + `Is Source?` — so what is missing is a **WRITER**, one fused op, **judgement**.
   (b) **6 `from-ctl` rows fail 5001 in `Get Controls.vi`** (panel-control source; 2 names carry newlines) and
   **no op addresses a panel source by index at all**. Run 9: **42 wired / 6 failed / 18 no-route of 66**; the v1
   op made 8 wires and **5 survived `remove_bad_wires_scripted`** (3 deleted — two branches of `#8885`'s net and
   the cross-diagram `D[19]→D[24]` one, unexplained and NOT chased). ExecState 0, nothing saved.
33. 🟡 **HALF CLOSED — the ADDRESSING gap is GONE; the SOURCE-RESOLUTION gap is now the only thing between D1
   and a saved VI.** ✅ `OpConnectNested_v1.vi` BUILT, SAVED (14,666 B), FUNCTIONAL **warm and cold**: two
   terminals by INDEX on two DIFFERENT nested diagrams, LabVIEW making the tunnels (`LoopTunnel 0 → 2`); an
   UNNAMED terminal on diagram P reached from a source on diagram Q (wire 0 → 414). ⚠️ `toolkit-capabilities.md:56`
   and §11n.2 said this "cannot be built by this fleet" — both WITHDRAWN in place. 🔴 What is left = **§11q.2**.
35. ✅ **FIXED + MEASURED** (`tools/bench/test_run_poison.log`, **11 pass / 0 fail**). `gscript` now carries a
   module POISON flag: `_deadline_call()` sets it on every expiry (`_run` AND `_invoke`), `_check_poison()` runs
