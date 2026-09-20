---
type: archive
status: archived
date: 2026-09-18
tags: [status, cycle22, close, fstunnel, dual-review, stub-wire]
---

# CYCLE 22 — the close, relocated from STATUS (rule 4; STATUS had reached 109 lines)

Relocated VERBATIM 2026-09-18 by the cycle-22 material session on the judgement session's instruction. Nothing is
rewritten; STATUS keeps the lock yaml, the HARDWARE banner, the live OPEN items and NEXT, and points here.

## §1 — the cycle-21/22 lock-block comment lines, verbatim as they stood in STATUS

(Note added on relocation, not part of the verbatim block: the "NO DISPOSITION WRITTEN" state below is SUPERSEDED —
both dispositions were written 2026-09-18 by the cycle-22 judgement session under `## What was done with it` in
`archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-codex.md` and `…-opus.md`.)

```
# 11:06-11:21 peer_fstunnel_v1_b4_dual rc=0/860s = the owed FAILED-PREDICTION `-Dual` review, BOTH ARMS ANSWERED
# (codex 196s, no cost line; opus/max 656s $3.9688) → archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-{codex,
# opus}.md. BOTH REFUTE the required-input claim (a condition present in the ExecState-1 copy cannot break the
# broken one); both name a cheaper separator. ⚠️ opus says `Wire.Is Broken?` 6371004 is ALREADY BUILT
# (docs/NAMES.md:888-897) ⇒ CLAUDE.md:346's "identified-but-unbuilt" line is STALE. **NO DISPOSITION WRITTEN -
# judgement's call** (dispositions for both arms still owed).
# CYCLE 22: 10:50 build_opfstunnelterm_v1 RUN 1 rc=1/162s gates 12/16 - six wire sites PASS, B4 ExecState 0,
# nothing saved. 11:1x diag_fstunnel_orphans rc=0/90s gates 8/8 READ-ONLY: the B4 "unwired sinks" 43 / 124 / 990
# are DONOR nodes (Open VI Reference · Traverse for GObjects.vi · UID to GObject Reference.vi), all present with
# the SAME wire-0 sinks in a copy whose ExecState is **1**, none a Property/Invoke node. Handles 30,318→30,979;
# scratch created+deleted in-run; md5 BEFORE AND AFTER identical - 3state c39f36e0…, V6 2a78e17c…, donor
# 5dc45a04…; no motor/serial/camera, `motor_gate --execute` never called. Cycle-21/22 lock lines + the D1 tables
# RELOCATED VERBATIM → archive/2026-09-18-status-cycle21-wire-semantics.md §8/§9/§9a; cycle-20 close →
# archive/2026-09-18-status-cycle20-close.md.
```

## §2 — STATUS's "Where things stand" section, verbatim as it stood

```
## Where things stand — cycle-20 detail in `archive/2026-09-18-status-cycle20-close.md` (§1–§5)
🔴 **THE TUNNEL OP IS STILL UNBUILT — verification level NONE.** `build_opfstunnelterm_v1.py` RUN 1 (10:50) reached
gate **B4 with ExecState 0** in BOTH classes; the six `wire_checked` sites all pass by effect. D1 (11:1x) then
measured the B4 "unwired sinks": 43/124/990 are **donor** nodes, unwired the same way in a copy whose ExecState is
**1** ⇒ that suspicion is dead by measurement. Cycle-21 narrative + the D1 tables + the two peer refutations →
`archive/2026-09-18-status-cycle21-wire-semantics.md` §9/§9a/§10 (§1/§3/§4/§7 = the earlier detail); cycle 19 →
`archive/2026-09-18-status-cycle19-flatseq.md`.
**THE GAP stands: 174 ops, 123 recipes, 235+ peers → zero runnable experimental VIs.**
```

## §3 — OPEN items 48 / 48a / 49 / 50, verbatim; all four CLOSED, which is why STATUS no longer lists them

```
48/48a/49/50. **ALL FOUR VERBATIM in `archive/2026-09-18-status-cycle21-wire-semantics.md` §5** — 48 ✅ recipe RELEASED + REWRITTEN, RUN twice, failing only at `:392`, now PATCHED and gate-armed again (see above; body `archive/2026-09-18-status-cycle20-open48.md`; 44+45 RETIRED) · 49 ✅ `-Dual` review archived, both arms ANSWERED, judgement SETTLED (no `--cycle 20` retrospective; `violations.py`'s 8 not re-derived) · 50 ✅ FIXED.
```

## §4 — the cycle-22 dispositions, for the record

The `-Dual` review of the B4 `ExecState 0` failed prediction was ACCEPTED IN FULL in both arms. The accepted
consequences (verbatim in each peer file's `## What was done with it`): the donor-node/required-input hypothesis is
dead by measurement (`tools/bench/diag_fstunnel_orphans.log:20-21,63-64`); the live hypothesis is the un-deleted
residual STUB WIRE #384 on the cast output; the discriminating test is `Wire.Is Broken?` 6371004, which is ALREADY
BUILT (`docs/NAMES.md:888-897`); the per-site `ExecState` attributor added this cycle is VACUOUS and is not
defended; the `DIAG unwired sinks` scan is blind by construction and is never cited as evidence again; and
`VI.Get Errors` 452 is off the critical path (probably unreachable over our COM path). `CLAUDE.md:345-346` was
corrected the same day — `Wire.Is Broken?` is no longer listed as missing.

Cycle-22 harness frictions (`stop_record.py` having no supersede verb, the missing `MATERIAL=1` allowlist entry, and
`build_opfstunnelterm_v1.py` still writing `opfstunnelterm_v0.json`) are recorded in
`docs/toolkit-capabilities.md`, section "Harness frictions measured in cycle 22".
