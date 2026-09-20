# routeb-run4-error2-and-zdz

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.9657  in 28 / out 42336 / cache-create 196634 / cache-read 1749564  (564s, 29 turn(s))
- **date:** 2026-09-18 22:57:57
- **outcome:** ANSWERED (566s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed prediction — D1 route-B v1 run 4. Attack both claims below.

Context: a Python COM client (`tools/gscript.py`) drives LabVIEW 2026 VI Scripting over ActiveX to restructure a
copy of a large tracking VI. Run 4 (`tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`,
80 PASS / 1 FAIL) PREDICTED an "S3w ledger" stage and reached neither it nor the later S4/S5/S6 stages. The
prediction failed, so this review is mandatory. Your job is to REFUTE, not to agree.

---

## CLAIM 1 — "run 4's crash is a resource-budget failure of the READING LabVIEW instance, not a defect in what the recipe built"

Stated flatly so you can attack it:

> The crash `RuntimeError: count(LoopTunnel) on SCRATCH_routeb_221324.vi: error 2: Invoke Node in TRef
> Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReport_v3.vi` was raised inside
> `settle_index_modes()` with **51,284 handles** open in the LabVIEW process, against this install's measured
> fresh baseline of ~31,500 handles. LabVIEW error 2 is *memory full*. THEREFORE re-running the same recipe
> against a freshly restarted LabVIEW, with the whole-VI `count(LoopTunnel)` census narrowed in scope or dropped
> entirely, would get past this point — nothing the recipe BUILT is implicated.

Rivals you must weigh explicitly, and say which the evidence favours:

- (a) the recipe's own constructions (newly created shift registers, moved nodes, reparented terminals) left the
  VI in a state that makes `Traverse for GObjects` unbounded or cyclic, so the traverse never terminates and
  exhausts memory regardless of the starting handle count;
- (b) `OpReport_v3.vi` or the Traverse path leaks VI Server references per call, so cost is per-call and a
  restart only delays the same crash;
- (c) `count()` over a whole VI is simply the wrong instrument at this object count, and the fix is not a restart
  but a different query.

Also answer: is LabVIEW error 2 in a VI-Scripting Invoke Node reliably "memory full", or is it overloaded to
other conditions on this path? Cite a source.

---

## CLAIM 2 — "`Z/dZ` → `#2222` t0 has NO by-index route on this fleet"

Stated flatly:

> `docs/cycle15-plan.md` Pre-decided 3 says the `Z/dZ` wire is to be REORDERED. That cannot be executed as
> written. MEASURED in run 4 (`build_d1_routeb_v1_run4.log:163-164`): the `ControlTerminal` for `Z/dZ` is uid
> `#403`; on `Diagram[56]` it is `Nodes[None]` with terminals `[]`; the sink `#2222` is `Diagram[24].Nodes[20]`
> t0 = `('', False, 0)` — an UNNAMED sink terminal. `OpConnectNested_v1` addresses wires as
> `Diagram[].Nodes[].Terminals[]` (`tools/recipes/build_opconnectnested_v1.py:418-420`), so a `ControlTerminal`
> that does not appear in that diagram's `Nodes[]` array has no by-index address at all.

The question we actually need answered — be concrete and cheap:

**What is the CHEAPEST mechanism that wires a control terminal to an UNNAMED sink terminal on a DIFFERENT
diagram, using an op we already have?** Two facts constrain the answer:

1. `OpConnectFromWire_v0` IS built (`docs/toolkit-capabilities.md:70`) and branches from a WIRE's source
   terminal rather than from a node index.
2. But `'Z/dZ'` carries wire `w730` on a PRISTINE copy and carries **NO wire at all on the BUILT copy, because
   the node moves performed earlier in the recipe cut it** (`tools/bench/diag_sr_transport.log:20`, `:25-26`;
   `archive/peer/2026-09-18-priorart-d1-routeb-v1.md:871-873`). So a wire-source-based op has nothing to branch
   from at the moment we would call it.

Constraint on your answer: the user has a STANDING ORDER forbidding the construction of NEW process devices /
tooling. Prefer an answer that uses an EXISTING op, a different ORDERING of the existing steps (e.g. doing the
connection BEFORE the moves that cut `w730`), or a documented LabVIEW VI-Scripting address form we are not
using. If your answer requires new tooling, say so explicitly and say why nothing existing suffices.

---

## For BOTH claims, give me, per claim:

1. the STRONGEST reason the claim is WRONG;
2. an ALTERNATIVE explanation of the same evidence;
3. what observation would FALSIFY the claim;
4. the CHEAPEST DISCRIMINATING TEST that separates the claim from its best rival — a concrete command or query,
   not a comparison of options.

---

## ALREADY RULED OUT — do not spend the answer on these (all measured in run 4)

- The build is NOT broken in the way our old gate suggested: the BASELINE `ExecState` read **0 COLD (logged
  UNREAD)** while the LIVE working copy read **`ExecState` 1 PRELOADED**, and the original resident read-only
  also read 1. The cold read measures subVI linkage, not brokenness.
- Rule 1 (never modify an original) held: original md5 `2a78e17c449cacdaf5da389818526859` unchanged before,
  after, and across the preloaded read; the working copy was deleted.
- The build's OTHER two planned rows SUCCEEDED: shift registers `#26032` (on `#1359` t1/t2) and `#26082` (on
  `#29874` t3/t5) were created and moved together with their nodes. ONLY row 3 (`Z/dZ`) failed — it is the single
  FAIL line in the whole 80-pass run (`:164`).


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is the reply. Both claims are refuted.

# Failed-prediction review — D1 route-B v1 run 4

**Both claims are wrong, each refuted by this project's own files.** Claim 1 cites, as the cause of a failure, the handle count at which the identical call demonstrably *succeeded*. Claim 2 says a route does not exist; the route is implemented in the same recipe file that reports it missing, and is switched off by a boolean.

No lock taken, nothing built, nothing run.

---

## CLAIM 1 — "resource-budget failure of the reading instance, not a defect in what the recipe built"

### 1. Strongest reason it is WRONG — 51,284 is the control, not the cause

`build_d1_routeb_v1.py:385-386` are consecutive statements:

```python
fact(f"S1 LabVIEW handles with the copy open: {labview_handles()}")   # :385
got = {c: g.count(TARGET, c) for c in BEFORE}                          # :386
```

and `BEFORE` (`build_d1_routeb_v1.py:244`) contains **`LoopTunnel=132`**. The log records both, adjacent (`build_d1_routeb_v1_run4.log:26-27`):

```
FACT  S1 LabVIEW handles with the copy open: 51284
FACT  S1 BEFORE census: {... 'LoopTunnel': 132 ...}
```

So **`g.count(TARGET, "LoopTunnel")` ran and returned 132 at 51,284 handles** — same function (`gscript.py:951-960`), same op VI (`OpReport_v3`), same target, same process, same `Traverse for GObjects` path. The claim names that number as the reason the same call later failed. It is the number at which it worked.

Corroborated independently: the project already raised ~51.5 k as an open item and **closed it** — `archive/2026-09-17-status-cycle15-narrative.md:148-150` ("30,849 → 51,530 … **CLEARED 2026-09-17**"), with a 12/12 diagnostic recorded running at 51,220 handles (`:154`).

### 2. The handle count at the crash was never measured

- 51,284 is from S1, **~1,600 s before** the failure.
- 49,062 (`:341`) comes from the `finally:` block (`build_d1_routeb_v1.py:1780-1801`) — **after** the exception, **after** `lv_restart` dropped the process to 30,682 (`:335`), **after** two main-VI copies were re-opened, and **after** the working copy was deleted (`:339`, code `:1793-1795`).

Neither reading brackets the failing call. "Was raised inside `settle_index_modes()` with 51,284 handles open" attributes a start-of-run measurement to an end-of-run event. That is the claim's entire evidentiary basis.

### 3. "Nothing the recipe BUILT is implicated" is asserted over a window where nothing was recorded

`s3w`'s row loop accumulates into `done`/`failed`/`noroute` and prints at `build_d1_routeb_v1.py:1529` — **after** `settle_index_modes()` at `:1517`. The traceback killed that print.

Between the last log line (`:332`) and the crash, up to **66 rows** (`:323`) ran `wire_control`, `v1_connect`, `wire_sr`, `CONNECT_FROM_WIRE`, plus `create_equal`, `delete_object` and `remove_bad_wires_scripted` — and **every outcome was lost**. The claim clears the built state using the one window whose record was discarded.

### 4. Alternative explanation of the same evidence

The 66 writes changed the VI's structure, and `settle_index_modes()` is the **first whole-VI traverse after that burst**. Cross-diagram `Terminal.Connect Wire` **creates border tunnels by itself** — measured twice: `docs/toolkit-capabilities.md:68` (`LoopTunnel 0 → 2`) and `:70` (`LoopTunnel 0 → 1`). Dozens of cross-boundary writes plus a `remove_bad_wires_scripted` pass, against a VI that began with 132 tunnels.

This is **weaker and likelier than rival (a) as you framed it**: the traverse need not be unbounded or cyclic, only *different from the one that succeeded at S1*.

Rival (b) is weakly disfavoured, not excluded — the two "main VI resident" deltas are comparable (+19,784 at S1; +18,380 for *two* VIs at teardown). No in-run sampling exists, so this is suggestive only. Rival (c) is undercut by the same S1 fact: it was an adequate instrument on this target 1,600 s earlier.

### 5. Error 2 is NOT reliably "memory full" on this path

Error 2 is nominally *Memory is full*, but it is overloaded on exactly this call. NI's article covers Error 2 from **`Open VI Reference`**, `Obtain Notifier`, `Obtain Queue`, `.NET Constructor Node`, `Open/Create/Replace File` — and `TRef Traverse.vi` fails at an `Open VI Reference`. NI's FP.Open thread is a case where Error 2 is a **build-configuration** problem with no memory involvement; LAVA carries a thread titled *"Error 2: Memory is full — but it isn't."* So "error 2 ⇒ memory full ⇒ a restart gets past it" has a weak first link.

### 6. What would FALSIFY the claim

A handle reading taken **immediately before** the failing `count()` that is at or below ~51,284. That single number kills it, because S1 proves the call succeeds there.

### 7. Cheapest discriminating test — two lines, inside a run you were doing anyway

`labview_handles()` already exists and is already imported here (`tools/bench/bench_prep.py:61,64-71`; `probe_move_ctlterm_v0.py:115`).

1. Immediately before `build_d1_routeb_v1.py:1170`:
   ```python
   fact(f"S3w handles immediately before count(LoopTunnel): {labview_handles()} "
        f"(S1 read 51284 and the same call returned {BEFORE['LoopTunnel']} there)")
   ```
2. Make the ledger survive the exception: move the `done`/`failed`/`noroute` print (`:1529`) **above** `settle_index_modes()` (`:1517`), or wrap the call in `try/except`.

≈51 k ⇒ resource story dead, look at the 66 writes. ≫51 k ⇒ resource story survives **and** the ledger names which rows inflated it — the part the claim needs and lacks.

### 8. Process finding

`build_d1_routeb_v1.py:1793-1795` deletes the working copy in `finally:`. The state that crashed is **gone**; (a)/(b)/(c) can no longer be separated on existing evidence at any price. On an exception the copy should be *renamed aside*, not removed — the rule is "a broken VI is never **saved**", which a rename does not violate.

---

## CLAIM 2 — "`Z/dZ` → `#2222` t0 has NO by-index route on this fleet"

### 1. Strongest reason it is WRONG — the route is in this file, built ops only, off by a flag

`build_d1_routeb_v1.py:1198-1203` states the design in a comment; `:1257-1278` implements it:

| step | code | op | status |
|---|---|---|---|
| temporary sink with **NAMED** inputs `x`/`y` | `create_equal(...)` `:1261` | `OpCreateEqual_v0` | FUNCTIONAL 23/0, `toolkit-capabilities.md:64` |
| wire the control to `x` **by panel label** — never touches `Nodes[]` | `g.wire_control(TARGET,[label],tcls,tix,["x"],branch=True,…)` `:1272-1273` | `wire_control` | `toolkit-capabilities.md:138` |
| branch that wire's source terminal into the unnamed sink **by index** | `CONNECT_FROM_WIRE(TARGET, zw, srcs[0]["i"], d, n, t, …)` `:1286` | `OpConnectFromWire_v0` | built, T1 functional, `:70` |
| delete temporary, **re-read the sink after** | `:1291-1306` | `delete_object` + `remove_bad_wires_scripted` | Tier 1 |

It did not run because **`TEMP_SINK_AUTHORISED = False`** (`:285`), with the refusal printed at `:1251-1255`. That is an authorisation decision taken for a stated *risk* reason (the 1055 modal, `docs/NAMES.md:473-480`) — **not a missing capability**.

### 2. The claim's reason is the wrong generalisation

`OpConnectNested_v1` cannot address `#403` because **a ControlTerminal is a Terminal, not a Node** — the project measured this on 2026-09-14 and wrote it verbatim at `tools/recipes/build_opconnectctl_v0.py:4`, then built `OpConnectCtl_v0` (`Panel.Controls[] 6348801 → Control.Terminal 6332006`, `:9-14`) precisely to route around it. Three index spaces already in the fleet bypass `Nodes[]`:

- **panel index** — `Panel.Controls[i] → Control.Terminal` (`OpConnectCtl_v0`, `OpPanelWiring_v0`);
- **wire index** — `Wire.Terms[j]` (`OpConnectFromWire_v0`, `OpWireSource_v5`);
- **UID** — `UID to GObject Reference.vi`, and **run 4 resolved `#403` this way itself**: `run4.log:168` `OBSERVED uid 403 -> owner 'Diagram' uid 567 | self 'ControlTerminal'#403` (via `OpOwnerChain_v1`).

### 3. The second premise is wrong about WHICH move cut w730

`diag_sr_transport.log:20-26` shows w730 running `ControlTerminal (Diagram 639, is_source) → Tunnel #2276 → #2222 t0`. In `s3()`:

| lines | what |
|---|---|
| `:617-631` | **the 21 node moves** — `#2222` is in `MOVE_TABLE["1.2"]` (`:255`) and leaves Diagram 639 |
| `:640-680` | S3-zdz, the "reorder" |
| `:684-697` | the `#403` reparent |

**The node move cut w730, not the reparent.** Run 4 placed the reorder before the *reparent*, which was never the cutting step. Your suggestion — connect *before the moves that cut w730* — therefore means **before `:617`**, and that has **never been tried**; there w730 still exists and `OpConnectFromWire_v0` applies directly, no temporary.

⚠️ **The measurement does not settle this one:** a wire made before `:617` will itself be cut by the subsequent `move_in` of `#2222`, exactly as w730 was, unless the branch lands on something that moves with `#2222`. So the honest ranking is — the temporary-sink route is the cheapest thing *known* to work end to end; "before the node moves" is cheap to test but has an unmeasured survival problem.

### 4. `OpConnectCtl_v0` alone is NOT the fix — direction and scope

`build_opconnectctl_v0.py:11,14`: the invoke runs on the **control's** terminal with `'Wire Source' <- IA_t.element`, so the panel object is the **SINK** (built for an IMAQ Image *Display*, an indicator). `Z/dZ` is a **source** (`diag_sr_transport.log:20`, `is_source: true`), and its node half is `VI.Block Diagram 23C → Nodes[]` (`:12`) = **top-level only**, while `#2222` is on `Diagram[24]`. The mirror arrangement is **new tooling**, which the standing order forbids. Cited to disprove the generalisation, not as the route.

### 5. What would FALSIFY the claim

`:1286`'s `CONNECT_FROM_WIRE` returning a non-zero `after` at `:1287` with `Is Broken?` not `True`.

### 6. Cheapest discriminating test — flip one constant

Set `TEMP_SINK_AUTHORISED = True` (`build_d1_routeb_v1.py:285`) and run that path. The recipe already prints the discriminator at `:1288-1290` (`branched off w<zw> terminal <i> … -> wire <after>, Is Broken? …`) and the post-delete re-read at `:1306`.

- non-zero `after`, `Is Broken?` False ⇒ **Claim 2 refuted by measurement**;
- `noroute` from `:1263-1267` ⇒ `OpCreateEqual_v0` cannot place a source-less `Equal?` — the one genuinely unmeasured step, and the thing worth learning;
- the 1055 modal ⇒ the gate was right, and *that* is the finding — not "no route exists".

---

## Summary

| | claim | verdict | decisive citation |
|---|---|---|---|
| 1 | resource budget, build innocent | **refuted** | `run4.log:26-27` — the same `count(LoopTunnel)` succeeded at 51,284 handles |
| 2 | no by-index route | **refuted** | `build_d1_routeb_v1.py:1257-1278` — the route, built ops only, disabled at `:285` |

**What would change my mind on Claim 1:** a handle reading immediately before `:1170` far above 51,284. Even then "nothing the recipe built is implicated" stays unsupported — the 66 unlogged writes are a candidate *consumer* of those handles, so that reading relocates the question rather than closing it.

**What would change my mind on Claim 2:** a run with `TEMP_SINK_AUTHORISED = True` where `OpCreateEqual_v0` cannot place the temporary sink **and** no wire-, panel- or uid-addressed op reaches `#403`. Nothing on file shows that today.

Sources:
- [Error 2: Memory is Full when Opening a New Reference in LabVIEW — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU)
- [Error 2: Memory is full occurring at FP.Open invoke node in built application only — NI Community](https://forums.ni.com/t5/LabVIEW/Error-2-Memory-is-full-occurring-at-FP-Open-invoke-node-in-built/td-p/3770243)
- [Error 2: Memory is full — but it isn't — LAVA](https://lavag.org/topic/18730-error-2-memory-is-full-but-it-isnt/)
- [Memory Is Full Error in LabVIEW — NI](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000P9mtSAC)
- [GObject class](https://labviewwiki.org/wiki/GObject_class) · [Node class](https://labviewwiki.org/wiki/Node_class) · [Terminal class](https://labviewwiki.org/wiki/Terminal_class) — LabVIEW Wiki

## Sources

(extract from answer)

## What was done with it

Dispatched by the cycle-36 MATERIAL session as the mandatory failed-prediction review for run 4
(`tools/bench/build_d1_routeb_v1_run4.log`, `BGRUN END rc=1 after 1713s`, 80 pass / 1 fail; the predicted S3w
ledger and stages S4/S5/S6 were never reached). Single `-Agent claude -Role hypothesis` arm per
`docs/cycle27-plan.md` Pre-decided 7. Outcome ANSWERED (566 s, $3.9657); log `tools/bench/peer_routeb_run4.log`.

The peer REFUTED BOTH claims put to it:

- **Claim 1 (resource budget, build innocent) — refuted** on the log's own adjacent lines: `run4.log:26-27` shows
  the identical `g.count(TARGET,"LoopTunnel")` call returning 132 **at 51,284 handles**, i.e. the number the claim
  names as the cause is the number at which the call worked. The 51,284 reading is from S1, ~1,600 s before the
  crash; 49,062 is post-exception, post-restart. No reading brackets the failing call. Up to 66 `s3w` rows ran
  between the last log line and the crash and **their entire ledger was lost** because the print at
  `build_d1_routeb_v1.py:1529` sits *after* `settle_index_modes()` at `:1517`. Error 2 is also not reliably
  "memory full" on an `Open VI Reference` path (NI + LAVA sources cited).
- **Claim 2 (no by-index route for `Z/dZ`) — refuted**: the route is already coded in this very recipe at
  `build_d1_routeb_v1.py:1257-1278` out of built ops only (`OpCreateEqual_v0` temporary sink with NAMED `x`/`y`
  → `wire_control` by panel label → `OpConnectFromWire_v0` by wire index → delete + `remove_bad_wires_scripted`),
  and did not run solely because `TEMP_SINK_AUTHORISED = False` (`:285`). It also corrected our premise: the
  **node moves at `s3():617-631` cut w730, not the `#403` reparent**, so "connect before the cut" means before
  `:617` — untried, but with an unmeasured survival problem of its own. `ControlTerminal` is a Terminal, not a
  Node — already written at `tools/recipes/build_opconnectctl_v0.py:4` — and three non-`Nodes[]` index spaces
  (panel, wire, uid) exist in the fleet; run 4 itself resolved `#403` by uid at `run4.log:168`.

**No action taken on either finding in this session.** The material session's brief was dispatch-and-report only;
acceptance of a review, the `TEMP_SINK_AUTHORISED` flip (it is one of the two authorisation flags STATUS records
as "off permanently", Pre-decided 13), the two-line instrumentation at `:1170`/`:1529`, and the peer's process
finding that `finally:` deletes the crashed copy (`:1793-1795`) instead of renaming it aside are all judgement
calls. Carried to the cycle-36 judgement session as `OPEN:` — see the session summary and STATUS.
