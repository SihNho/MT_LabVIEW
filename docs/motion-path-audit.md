---
type: reference
status: current
date: 2026-09-12
tags: [docs]
---

# Audit of the motor / stage serial path — what is actually on it

Read-only inspection, 2026-09-12, at the user's request. No original was modified; lab VIs were inspected as copies in
claudeDev and deleted afterwards, vendor VIs were opened read-only in place, and no hardware was connected or touched.
Logs: `tools/bench/inspect_motion_vis2.log` (lab + ASI), `tools/bench/inspect_pi_vis2.log` (PI GCS command VIs).

## Why this audit happened

The user supplied the history that reframed the whole question: *the motor path was badly delayed, 115200 baud and a
partial loop split were adopted deliberately to fix it, and it still feels like one loop carries too much.* That is domain
knowledge no amount of reading could have produced, and it points the search at waiting rather than at work.

## The serial hardware is not the problem

| layer | measured / read | verdict |
|---|---|---|
| wire time at 115200 8N1 | 87 µs per byte, so a 10-byte command plus a 10-byte reply is under 2 ms | not the bottleneck; raising the baud rate could never have fixed much |
| Sunix card, COM3/COM4 (both instruments) | RX FIFO trigger 14 bytes, TX FIFO 16, no latency timer | a short reply returns via the 4-character timeout, about 0.35 ms |
| FTDI ports COM5/COM6 | LatencyTimer **16 ms**, the driver default | irrelevant here — the user confirmed both the ASI stage and the PI motor are RS-232 into the Sunix card |

So the remembered delay is in software or in the controller, not in the cable or the UART.

## What the diagrams contain

Counted across both passes. `node_info` sees only the top-level diagram, which is nearly empty in these VIs, so every
diagram index was walked with `net_map` and primitives identified by their terminal names.

| pattern | lab VIs | PI GCS command VIs |
|---|---|---|
| fixed `Wait (ms)` | **1** | **0** |
| front-panel property-node `Value` access | **19** | 0 (but POS?/TMN?/TMX?/GOH each carry 1–2 `Number of Rows` property nodes) |
| controller-error query after a command | — | **3** occurrences across MOV and VEL |

### 1. The only fixed delay is in the lab's own autofocus VI

`ASI_adjust focus-subvi.vi` carries a `Wait (ms)` primitive inside a case frame (diagram 8), together with five or more
property-node `Value` accesses and its own VISA traffic. The top-level node list of this VI literally begins with two
Property Nodes. If autofocus runs often, this single VI combines all three cost shapes at once. **The Wait's constant was
not read** — that needs either a constant-value reader op or a look at the diagram.

### 2. The lab's motor wrapper talks to the front panel, not just to the motor

`Motor control v5_No Recording.vi` (35 nodes, 18 diagrams) is built around **control references**: `tran display ref`,
`send to trans ref`, `change of trans value ref`, `Home ref`, and at least six property nodes reading or writing `Value`.

This matters more than it looks. A property-node `Value` access executes **in the UI thread**. Every one is a thread
switch, and they queue behind all other UI work — including the Intensity Graph redraw that `ARCHITECTURE.md` §10 already
names as the prime suspect for `t0`. **This is a concrete mechanism by which splitting the motor into its own loop would
not have helped:** the loops were separated, but they meet again in the UI thread.

### 3. PI's driver spends two round trips per command

`MOV.vi` and `VEL.vi` each call a subVI taking `Command substring` + `Controller error` + `System no.` after sending the
command — the GCS convention of querying controller error state after every command. So one motor command costs a send
plus an error query, i.e. two serial round trips, not one. `POS?`, `TMN?`, `TMX?` and `GOH` send and read once.

No PI command VI contains a fixed Wait. The command path itself is written sanely.

### 4. ASI's driver serializes its port with a semaphore, and reads by byte count

`Send Serial Command.vi` creates a named semaphore of size 1 around the VISA Write/Read pair, so **two callers of any ASI
command block each other**. This matters because `ARCHITECTURE.md` §5 recorded that no Queue, Notifier or Semaphore
appears in the main VI — true of the main VI, but the vendor driver underneath it has one.

The read is a VISA Read by **byte count** (diagram 3), not by termination character. If a reply is shorter than requested,
that read blocks until the VISA timeout. `Mercury_comm.vi`'s own help text puts the default timeout at 5000 ms, so a
single malformed or missed reply costs seconds, not milliseconds.

### 5. Cleared

`Mercury_comm.vi` is the connection-setup VI (port, baud, timeout, termination character, and a choice between RS-232 and
PI's DLL), used at initialisation, not per command. ASI's `Get Current Position` and `Move Axis to Position` are clean
send-and-parse VIs. `Max Trans Pos.vi` is effectively empty. `Global motor pos.vi` has **no block diagram at all** — the
traverse failed with error 1035, which confirms it is a pure VI Global rather than a shift-register functional global, so
it is not acting as a hidden mutex. It remains a race carrier, and no new global writers may be added.

## MEASURED: one serial round trip to the motor controller (2026-09-12)

Everything above was arithmetic. This is the real thing, measured with the user's permission through
`tools/bench/serial_roundtrip.ps1` on COM3 using **read-only GCS queries only** — no MOV, no GOH, no VEL, nothing that
actuates, and the ASI port untouched. The controller identified itself as **PI C-863.11 Mercury, firmware 1.3.0.7**.

| query | bytes exchanged | wire time at 115200 | measured median | difference |
|---|---|---|---|---|
| `ERR?` | 9 | 0.78 ms | 1.82 ms | 1.04 ms |
| `POS?` | 15 | 1.30 ms | **2.56 ms** | 1.26 ms |
| `TMX?` | 16 | 1.39 ms | 2.64 ms | 1.25 ms |
| `*IDN?` | 69 | 5.99 ms | 7.19 ms | 1.20 ms |

**round trip = 1.2 ms fixed + 86.8 µs per byte.** Four replies of very different lengths agree on the fixed term to
within 0.2 ms, so the model is solid rather than fitted. 30 samples each; `POS?` ran min 2.49, p95 2.63, max 2.64, i.e.
sd well under 0.1 ms. One 11.67 ms outlier appeared in 150 queries, so rare jitter exists.

The 1.2 ms fixed term is the controller's own turnaround plus the Sunix RX FIFO character timeout (about 0.35 ms) plus
driver and OS. `ERR?` returned a single latched 307 left by the `*IDN?` block and the first read cleared it; the
controller now answers `ERR? -> 0` three times running, so nothing was left in an error state. The exact meaning of
PI error 307 was not found in public sources.

### What this settles

**The serial read is not slow, and it cannot be made much faster.**

| change | `POS?` becomes | gain |
|---|---|---|
| RX FIFO trigger 14 → 1 | about 2.2 ms | 14 % |
| baud 115200 → 230400, if the C-863 supports it | about 1.9 ms | 26 % |
| both | about 1.55 ms | 39 % |

The floor is roughly 1.5 ms because the controller's own ~0.9 ms is not addressable from the host. So the user's
remembered "severe motor delay" is **very unlikely to be the round trip itself**. The surviving candidates are the ones
this audit already found: the motor loop free-running with no throttle (no `Wait` primitive anywhere in diagram 20),
the UI-thread property nodes, and the 5000 ms VISA timeout that a single missed reply would cost — that last one alone
matches "severe" far better than 2.56 ms does.

## What this changes

The leading explanation for "one loop carries too much" is now **UI-thread serialization**, not CPU work. It is testable
without hardware and without restructuring anything: count how many property-node `Value` accesses sit on the per-frame
path, and whether any of them are in the same loop as the display.

Ordering that follows, folded into [t0-instrumentation-plan.md](t0-instrumentation-plan.md):

1. **Step 0 first, unchanged** — determine which While loop holds what. Nothing above matters if these VIs are not on the
   per-frame path. In particular, find out whether autofocus and position queries run every frame or only per clamp step.
2. **Then the UI-thread question**, which this audit made concrete and cheap.
3. Only then the per-VI cost measurement.

## Two method notes worth keeping

- **`node_info` is top-level only.** `Mercury_comm.vi` reports 13 nodes of which 2 are top level; a first pass that used
  only `node_info` would have concluded these VIs were almost empty. Walk every diagram index with `net_map` instead.
- **Inspect one VI per subprocess behind its own fresh LabVIEW.** The first attempt died at the first VI and returned
  RPC errors for the remaining nine, voiding the batch. A 3-cell probe could not reproduce the crash with the same VI and
  the same call order, so it is logged as a transient (`tools/bench/nodeinfo_crash_probe.log`) and the answer is
  isolation, not a fix.
