---
type: archive
status: historical
date: 2026-09-17
tags: [status-narrative, d1, route-b, cycle15]
---

# STATUS narrative relocated VERBATIM — cycle 15, route-B session 2 (material)

Rule 4: nothing here is rewritten, only moved out of `STATUS.md`. One line plus a pointer is left behind.

## §1 — the lock block of this session

```yaml
labview-lock:
  status: released
  owner: material/cycle15-d1-route-B-2
  since: 2026-09-17 15:3x-16:3x
```

RELEASED. Runs, all under `bgrun`, all terminated, all `BGRUN END`:

| log | result |
|---|---|
| `tools/bench/peer_dual_selftest.log` | `rc=0 after 100s` — `peer.ps1 -Dual` self-test, both arms ANSWERED |
| `tools/bench/priorart_routeb_census.log` | `rc=0 after 502s` — 6 findings, 0 novel |
| `tools/bench/diag_moved_structure_terminals.log` | **39 pass / 0 fail, 113 s** |
| `tools/bench/priorart_routeb_build.log` | `rc=0 after 506s` — 7 findings, 0 novel |
| `tools/bench/build_d1_routeb_v0.log` | **84 pass / 2 fail, 415 s** (run 1) |
| `tools/bench/peer_routeb_noroute.log` | `rc=0 after 512s` — codex ANSWERED 87 s, opus TIMEOUT 420 s |
| `tools/bench/retro_cycle15_routeb.log` | `rc=0 after 365s` — 2 violations |
| `tools/bench/build_d1_routeb_v0_run2.log` | **84 pass / 2 fail, 548 s** (run 2) |

ORIGINAL `Min_Track N beads V6_ParallelLoop.vi` md5 **2a78e17c449cacdaf5da389818526859** read BEFORE and AFTER
every run and unchanged at the end. Every scratch (`SCRATCH_term_pre_*`, `SCRATCH_term_post_*`,
`SCRATCH_ctprobe_*`, `SCRATCH_routeb_*`) created and deleted in the same run; `claudeDev` holds no leftover.
No GUI action, no hardware. Handles 30,680 → 38,803 across the session (fresh-instance baseline ~31,500).

## §2 — OPEN 37, in full, as it was resolved

37. ✅ **CLOSED 2026-09-17 by `tools/bench/diag_moved_structure_terminals.log` (39 pass / 0 fail, 113 s).** The
   cause was **NOT** a tunnel side and **NOT** the restructuring. (a) On the pristine original `#5540` **t1 is an
   UNNAMED SINK** (`is_source` FALSE, w5979); the named output is **t2** (w5637) — `main_vi_nodeterms.json`
   :11292-11315, reproduced live by 5 identity reads. (b) The shift was made by the failing run's own `bare()`:
   deleting t1's wire + `remove_bad_wires_scripted` DELETES THE TUNNEL, so every higher index drops by one and
   the map goes 7 → 6 terminals. Measured sequence **`[5979, 5637, 0]`**, identical to
   `build_opconnectfromwire_v0_run2.log:96`. (c) **A `GObject.Move` costs nothing**: five structures moved into
   three fresh While loops left `Wire 1902 → 1902`, `LoopTunnel 132 → 132`, terminal counts 7/7/10/7/7 unchanged
   and every name at its own index. (d) **The SINK RULE holds on the pristine original for all 8 moved-structure
   `from-tunnel` rows** — every sink reads `is_source` FALSE. (e) `#5540`'s index → side → tunnel, joined offline
   from `stage2-assembly-step-e.md:137-147` CENSUS B: **t0 = case SELECTOR · t1 = IN tunnel 5967 · t2 = OUT
   SelectorTunnel 5680 · t3 = IN 5702 · t4 = IN 5725 · t5 = IN 5825 · t6 = OUT SelectorTunnel 6016**.
   ⚠️ **CAVEAT, measured:** after the move every `#5540` terminal reads `is_source` FALSE **including the two
   OUTPUT tunnels** (they are unwired), so `is_source == FALSE` alone does NOT separate input from output on a
   freshly moved structure — address those rows by INDEX (which survives) or by the CENSUS-B side map.

37b. (superseded text) 🔴 **the 2026-09-17 reading that a `from-tunnel` sink needs a SIDE, not just an index.**
   `build_opconnectfromwire_v0_run2.log` T2: the op wired w5812 (source owned by `FlatSequenceInnerTunnel`
   **#5818**) into `#5540` t1 with **no error**, sink wire **0 → 1231** — and that wire reads
   **`Wire.Is Broken? TRUE`**, with TWO `Is Source? TRUE` terminals (`SelectorTunnel` #5680, `LoopTunnel` #2497).
   The terminal the op resolved is named **`Bead is good? array out`** — an OUTPUT tunnel. codex (ANSWERED,
   `archive/peer/2026-09-17-cfw-t2c2-broken-wire.md`) confirms two sources = broken and supplies the mechanism: a
   tunnel has an OUTSIDE and one INSIDE terminal per frame, and a source onto an OUTPUT tunnel's outside terminal
   is a source-to-source conflict. My "the index drifted when the copy was restructured" cause is **withdrawn as
   unmeasured**. The cheapest settling test — a read-only `Node.Terminals[]` census of `#5540` on an
   unrestructured AND a restructured copy, comparing `Terminal.Name` 634A004 and `Is Source?` 634A003 — was NOT
   run (third build attempt; the budget is two).

## §3 — OPEN 36, in full, as it stood before route B's build closed (a)

36. ✅ **LARGELY CLOSED 2026-09-17 (§11u + `OpConnectFromWire_v0`).** (a) the 16 `from-tunnel` rows now have a
   WRITER — built, saved, ExecState 1, and it ACCEPTED a `FlatSequenceInnerTunnel` source on the real VI.
   (b) the 6 `from-ctl` rows split: **3 were a caller bug** (`wire_control` without `src_diagram_index`;
   `'Auto-Reset'` wires cleanly with index 43) and **3 are UNDIAGNOSED `ForLoop` tunnels**, re-assigned to
   `OpConnectNested_v1`. **The newline is NOT the cause.** (c) run 9's "3 of 8 wires deleted by RBW" is
   **WITHDRAWN** — that gate compared uids; at most 2 went null and 1 changed identity.

## §4 — the NEXT block this session replaced

✅ **Route A is closed (§11t) and B's FIRST ITEM IS BUILT.** `OpConnectFromWire_v0.vi` (16,524 B, ExecState 1,
`tools/recipes/build_opconnectfromwire_v0.py`, run 2 **42 pass / 1 fail**) is the writer §11t asked for, and it
carries the project's first ORDERED `Wire.Is Broken?` **6371004** readout — which was never a missing op, only a
missing error-chain branch (prior-art A1). T1 is fully functional on a scratch (outer wire → into a new While
loop body, `Is Broken? FALSE`, `LoopTunnel 0 → 1`).
🔴 **THE ONE JUDGEMENT QUESTION (OPEN 37): how does a route-B recipe address a `from-tunnel` SINK?** The op takes
`(diagram, node, terminal index)`; a structure tunnel has an outside terminal and one inside terminal per frame,
and T2 put a source onto an OUTPUT tunnel's outside terminal and got a broken wire. Either (i) the recipe derives
the correct SIDE first (`Tunnel.Outside Terminal` 6356001 / `Inside Terminals[]` 6356000 — `OpTunnelRead_v0`
already reads both), or (ii) the sink addressing changes shape. **That is a design decision, not a build.** The
read-only two-copy census above is the measurement that should precede it.
⚠️ `docs/d1-route-b-plan.md` is REVISED but still `authorises: nothing` — B is not started. Its ledger is now
**63 of 82 routed / 19 not** (18 R1 + 1 R3), and R1's own in-plan candidates (i)/(ii) are **refuted by
measurement** for 14 of 16 rows. Stage 2 (8 queues, sentinels, carriers, GPU kernel 13+6) is still unwritten, and
OPEN 32 (two consecutive outcome reviews demanding a re-plan with the USER) stands above all of this.

## §5 — the two structural runs of route B, side by side

| | run 1 | run 2 | what changed |
|---|---:|---:|---|
| S3w attempted | 66 | 66 | — |
| **WIRED** | 51 | **63** | `dest` fallback for `#5058`'s sink rows + tunnel-identity source resolution |
| **FAILED** | 0 | **0** | — |
| **NO-ROUTE** | 15 | **3** | 10 were `dest=None`, 2 were an over-strict wire-match refusal |
| SINK RULE | 8 OK / 0 REFUSED / 0 BAD | **16 OK / 0 REFUSED / 0 BAD** | the 6 `#5058` rows joined once `dest` resolved |
| RE-TARGET name check | (not implemented) | **23 rows verified** | codex's falsification test, run as a gate |
| ExecState warm | 0 | 0 | 3 required inputs still unwired by construction |
| gates | 84 pass / 2 fail | 84 pass / 2 fail | the same two: `S3w 0 rows NO-ROUTE`, `S5 ExecState 1 WARM` |

Both runs: `S1` census exact (Diagram 170 · Node 626 · Wire 1902 · LoopTunnel 132 · ControlTerminal 114 ·
WhileLoop 3 · Local 8 · SubVI 98 · Function 181) · `S1t` SubVI 98→97, Function 181→180, Node 626→624,
Wire 1902→1899 · `S1d` SubVI 97→94, 32 re-wire rows captured from the deleted subVIs · `S2` WhileLoop 3→6,
Diagram 170→173 · `S2d` SubVI 94→97, 0 of 3 uid reuse · `S3` 21 nodes + 6 ControlTerminals reparented,
ControlTerminal 114→114, Local 8 · `S3b` 109 terminals to re-connect (32 deleted + 77 moved), all 13 §8 crossings
in the cut set, 0 collateral, 0 nodes on diagram 19 other than `#637` lost a wire · `S3c` 8 shift registers ·
`F0` **109/109 resolved** (`cross-loop 5 · from-stay 11 · from-tunnel 18 · to-sr 12 · from-sr 8 · same-loop 16 ·
source-side 27 · from-ctl 7 · from-const 5`).
