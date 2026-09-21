# c65-testa-timeout

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.5805  in 30 / out 33979 / cache-create 183668 / cache-read 1651738  (471s, 26 turn(s))
- **date:** 2026-09-21 14:57:28
- **outcome:** ANSWERED (472s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm it.

## The record

A READ-ONLY diagnostic, `tools/bench/diag_c64_row1_testa.py`, was launched under a background runner with a
22-minute process deadline. It edits nothing and saves nothing. It has two tests:

- **TEST A** — re-open one saved file cold and read some terminal tables. This finished normally and produced
  its reading (`tools/bench/diag_c64_row1_testa.log:38`).
- **TEST B** — on a second saved file, run a "whole-VI net census" for each of two wire objects: for EVERY
  diagram in the file, list its nodes, and for EVERY node read its full terminal table, collecting every
  terminal whose attached wire id equals the wire being traced. Then the same over all 116 front-panel rows.

TEST B's census was given its own internal soft budget of **600 s per wire** (`diag_c64_row1_testa.py:80`,
`:233-274`). Measured result, `tools/bench/diag_c64_row1_testa.log:46`:

```
TB wire 23502 ... : 2 member(s) over 103 diagram(s) / 450 node(s) in 601.6 s ;
                    budget 600 s reached after 103 of 173 diagrams
```

So ONE wire's census scanned 103 of 173 diagrams and 450 nodes in 601.6 s — about **5.8 s per diagram** and
**1.34 s per node** — and stopped on its own budget without finishing. The second wire (23526) was never
started. The process deadline then fired: `BGRUN TIMEOUT killed after 1321s` (`:53`). The two restarts the run
performs (`:17`, `:42`) account for part of the remaining wall clock.

The inner call being repeated is a COM round trip per node: `g.node_terms_uid(path, diagram_index,
node_index)` (`tools/gscript.py:1005`), which runs a LabVIEW VI Server operation that returns one node's
terminal table (uid, name, source/sink flag, attached wire id, four error columns). `g.node_labels(path,
diagram_index)` (`tools/gscript.py:587`) is called once per diagram. `g.report_all(path, 'Diagram')`
(`tools/gscript.py:488`) enumerated the 173 diagrams once, cheaply, at the start.

Elsewhere in the same file, a *targeted* lookup that stops at the first match, `find_node` (`:141`), located
three nodes by scanning **1 diagram of 173** each — because it was given a hint and hit immediately. Single
`node_terms_uid` reads in TEST A returned promptly. The file itself is a 476 KB VI with 1906 Wire objects,
631 Node objects, 116 ControlTerminal objects and 173 diagrams.

## THE CLAIM YOU MUST TRY TO DESTROY

"The prediction that failed is simply an under-estimate of cost: an exhaustive per-node COM census over a VI
of this size is inherently ~1.3 s per node, so a full two-wire census needs roughly 173/103 x 2 x 600 s ≈ 2000 s
of scanning alone and could never fit a 22-minute deadline. Nothing is wrong with the machine, the file, or
the tooling; the run was simply asked to do too much, and the fix is to scope the census (trace only the
diagrams that can carry the wire) rather than to raise the deadline."

## Already ruled out (do not spend your answer on these)

- "The VI was broken or the session was wedged": both files opened cold at execution state 1 (`:19`, `:44`),
  every census returned real data, and both pre-read restarts reported "clear (no modal dialog)" (`:17`,
  `:42`).
- "A modal dialog blocked it": the run's own dialog check was clean at both restarts, and the scan kept
  producing per-diagram progress until its own soft budget stopped it.
- "The census found the wrong answer": the 2 members it did find are the two intended terminals, and the
  source count is 1 (`:47-49`).

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which **1.34 s per node is
   abnormal** for a VI Server terminal-table read over an out-of-process COM connection, i.e. the cost is a
   defect (re-opening a VI reference per call, a per-call traverse from the root, an O(n^2) re-enumeration, a
   watchdog sleep, marshalling across apartments) rather than an inherent price.
2. A DIFFERENT explanation of the same timing that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.
   It must be READ-ONLY (this project may not modify or save the VI under test) and must not require the
   LabVIEW GUI.

Be concrete about the LabVIEW VI Server object model: is there a way to go from a **Wire** object to the
terminals attached to it directly (a property or method on the wire itself), instead of scanning every node
of every diagram and comparing wire ids? If yes, name the exact property/method and its class. If no, say so
plainly — that answer is as useful to me as the other one.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## VERDICT: the claim is wrong on its central assertion, and this project measured the refutation eight days ago.

The claim concedes the right *direction* (scope the work) but asserts three things that are false: that ~1.3 s per node is **inherent**, that **nothing is wrong with the tooling**, and that an exhaustive per-node census is **the way to trace a net**. All three fail.

---

## 1. The strongest reason the claim is WRONG

**The cost is not per node and it is not inherent. It is a fixed per-OP-RUN cost that scales with the TARGET FILE, and this project measured it, named it, and built a tool against it on 2026-09-13.**

`docs/toolkit-capabilities.md:335-372`, "THE bottleneck, measured 2026-09-13: every op run re-traverses the whole target":

```
one bare op run, SMALL target VI      10.4 ms
one bare op run, the MAIN VI         960.8 ms   <- 92x
SetControlValue                       0.069 ms
class Local    (8 objects)            991 ms
class Terminal (5763 objects)        1222 ms    <- 720x the objects, +23% time
```

> "**~990 ms of every call is FIXED** … The fixed part is opening the target: each op run does its own `Open VI Reference` on a 473 KB VI with 98 subVI call sites." (`:359-361`)

So: reading a terminal table costs ~10 ms of actual work. The other ~99 % is re-opening a 476 KB VI. **Touching 720× more objects adds 23 %** — the traversal is not the cost, so "an exhaustive census is inherently expensive because it is exhaustive" is refuted at the premise.

**Your denominator is wrong, and that is what makes the number look inherent.** `net_of` issues one `node_labels` run per diagram plus one `node_terms_uid` run per node (`diag_c64_row1_testa.py:245`, `:252`) — **103 + 450 + 1 = 554 op runs in 601.6 s = 1.086 s per run**, which lands on the measured 960.8 ms + ~13 % almost exactly. "1.34 s per node" is 601.6 ÷ 450: it silently charges 103 diagram runs to the nodes and hides the fact that the unit is the *run*, not the *node*.

**And this is a repeat of a failure this project has already paid for once.** `gscript.py:491-494`:

> "`report()` runs the op once per object … A 626-node sweep therefore paid that 626 times — **618 s measured**. This pays it once."

618 s for 626 runs and 601.6 s for 554 runs are the same event. `report_all` exists *because of it*. TEST B re-committed it with a different verb. That is `repeated-failure-class`, not physics.

**The mechanism is documented by the vendor**, so "nothing is wrong with the machine" is also too generous: a VI stays in memory only while a reference is open, its panel is open, or it is a subVI of something in memory — otherwise the next `Open VI Reference` must **load it from disk** ([NI, Building VI Server Applications](https://www.ni.com/docs/en-MY/bundle/labview/page/building-vi-server-applications.html); [NI forum: "Open VI reference is very slow if VI is not already loaded in memory"](https://forums.ni.com/t5/LabVIEW/Open-VI-reference-is-very-slow-if-VI-is-not-already-loaded-in/td-p/3337386) — 7 s cold vs 900 ms with the panel already open). Each op run opens, uses, and drops the last reference to a 476 KB VI with 98 subVI call sites; the load/unload churn is paid 554 times.

---

## Your direct question: **YES — Wire → terminals is one property read, and the op for it is already on disk**

| what | id | evidence |
|---|---|---|
| **`Wire >> Terminals[]`** — *"References the terminals connected by this wire"* | **6371003** | [LabVIEW Wiki, Wire class](https://labviewwiki.org/wiki/Wire_class) (6371004 `Is Broken?` — the one you already built — is the adjacent ID in the same table) |
| property-node output short name | **`Terms[]`** | `LEARNING.md:437`; `.claude/skills/labview-automation/references/vi-scripting.md:593-602` |
| `Terminal.Is Source?` | 634A003 | `docs/d1-build-plan.md:780` |
| `Generic.Owner` → owner class/uid | 6327806 | `docs/d1-build-plan.md:791` |

**It is not a design sketch — it is built, wrapped, and has been run read-only on this VI family:**

- `OpWireSource_v5.vi`, wrapper **`wire_source_owner(target, wire_uid, n=6)`** at `tools/recipes/build_opconnectfromwire_v0.py:423-447`. Docstring: *"`OpWireSource_v5` on `target`: the owner of the wire's single SOURCE terminal. **Read-only.**"* UID-addressed by wire; iterates terminal index with early exit.
- Run on 18 rows, **read-only on the working copy, md5 `2a78e17c449c…` before *and* after** (`docs/d1-build-plan.md:801-810`; `tools/bench/diag_tunnelsource_onehop.log`; raw rows `tools/bench/d1_tunnel_sources.json`).
- Cost: **2–3 op runs ≈ 3 s** for a 2-terminal wire. Against 601.6 s. For both wires: ~6 s against your extrapolated ~2000 s.

Caveat, stated honestly because it is real: `Terms[]` returns **ControlTerminals too, and a ControlTerminal's `Owner` is the Diagram, not a node** — NI's own thread on this ([Vi Scripting: inconsistent behaviour of terms[] of a wire / owner](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055)), and your own `docs/NAMES.md:899-901` measured the same on 2026-09-15. So `wire_source_owner` gives you owner **class + uid**, not `Diagram[46].Nodes[24]`; the diagram/node indices come offline from `main_vi_nodeterms.json` / `d1_step0_census.json`, which is exactly how run 9 did it (`d1-build-plan.md:809-810`). Panel-side members stay a `panel_wiring` call — **one op run, ~2 s** (`docs/NAMES.md:898`).

**Second, independent scoping error:** a wire is owned by exactly one diagram and its terminals are on that diagram. TEST A had already found both nodes on **diagram index 46, scanning 1 diagram of 173** (`diag_c64_row1_testa.log:21,:26,:35`). TEST B then searched 103 diagrams for terminals that could not have been anywhere else. "Trace only the diagrams that can carry the wire" is not a heuristic — it is **one** diagram, and the run already knew which.

---

## 2. Alternative explanations of the same timing

**(a) VI load/unload churn, not "per node".** The dominant term. Predicts cost ∝ (diagrams + nodes) × *target size*, independent of terminal counts — identical for a VI with one terminal per node. Fits 1.086 s/run against 960.8 ms measured.

**(b) Refnum/handle accumulation inside LabVIEW, making later runs progressively slower.** `gscript.py:539-540` records "handle count grows ~0.9 per Open VI Reference on the main VI"; the run opened at **34,168 handles** (`log:4`), already above the ~31,500 baseline CLAUDE.md names, and 554 opens add ~500 more. **Your measurement cannot distinguish (a) from (b)** — `net_of` records one total (`rec["scan_cost_s"]`, `:271`) and no per-diagram timestamps. Flat per-run cost ⇒ (a) alone; rising ⇒ (b) on top.

**(c) Cross-apartment marshalling in `_run`.** Every call builds a fresh daemon thread, `CoMarshalInterThreadInterfaceInStream` → `CoInitialize` → `CoGetInterfaceAndReleaseStream` → `Invoke` (`gscript.py:390-410`), and the "COM is 0.07 ms" figure covers `SetControlValue`/`GetControlValue` on the main thread, **not** this path. I checked it and it is disfavoured by the same table: the identical path costs 10.4 ms against a small target, so marshalling is ≤10 ms of the ~1000 ms. Named and killed.

**(d) The dialog watchdog. Ruled out by reading:** `_run(poll_s=6.0)` and runs finish in ~1.1 s, so `done.wait(6.0)` returns before the first `_lv_gui` PowerShell spawn (`gscript.py:370-373`). No per-run subprocess.

**(e) Not a timing explanation but a fault the record hides:** the run's own budget arithmetic guaranteed the kill before the first COM call — 2 wires × 600 s soft budget + 2 × ~45 s restarts + TEST A > the 1320 s process deadline. The soft budget is fixed per wire (`:80`) instead of derived from remaining wall clock.

---

## 3. What would falsify each side

**Falsifies the CLAIM** (any one of these):
- `node_terms_uid` on a **small** VI returning in ~10–30 ms. Same call, same code path, same terminal-table read — if the cost were inherent to the read it could not move 90×.
- `wire_source_owner(STEP9, 23502)` returning the same two members (owner uids 10407, 23499) in ≤ 5 s.
- Per-run times that are flat at ~1.09 s regardless of how many terminals the node has (450 nodes, wildly different terminal counts, one uniform cost).

**Falsifies MY account:**
- Per-run cost that stays ~1.1 s **on a small target too** → the cost is in the op run irrespective of target, my reload story dies, and "fewer runs" stops being the fix.
- Per-run cost climbing monotonically (≈0.5 s early → ≈2 s late) → the dominant term is accumulation (b), not the fixed open, and the fix is restart cadence, not array returns.

---

## 4. The cheapest discriminating test — read-only, no GUI, no save, ~45 s of LabVIEW time

One file under `bgrun --max-min 8`. No `g.save`, no `open_panel`, no `ensure_loaded`, no edit. Print **every individual elapsed time**, never an average — the shape is the measurement.

```python
import time, os, sys
import gscript as g
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
from build_opconnectfromwire_v0 import wire_source_owner   # :423, "Read-only"
from hash_probe import probe as HASH
from bench_prep import labview_handles

BIG   = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")   # 476 KB, TEST B's target
SMALL = os.path.join(g.CLAUDEDEV, "<scratch copy of any small VI>")   # copy first: a copy is not running

def timed(f, n=10):
    out = []
    for _ in range(n):
        t = time.time(); f(); out.append(round(time.time() - t, 3))
    return out

h0 = labween := labview_handles();  m0 = HASH(BIG)
A  = timed(lambda: g.node_terms_uid(BIG,   46, 24))      # same node, 10x, big target
B  = timed(lambda: g.node_terms_uid(SMALL,  0,  0))      # same call, small target
with g.vi_ref(BIG) as _keep:                             # hold the VI RESIDENT
    C = timed(lambda: g.node_terms_uid(BIG, 46, 24))
t = time.time(); W = wire_source_owner(BIG, 23502); dW = round(time.time() - t, 2)
m1 = HASH(BIG);  h1 = labview_handles()                  # md5 before == after; handle delta
```

| reading | decides |
|---|---|
| **B ≈ A** | the claim stands: the per-call cost is inherent to the terminal read |
| **B ≪ A** (prior: ~10–30 ms, `toolkit-capabilities.md:340`) | cost tracks **target size**, not node count — the claim is dead |
| **C ≪ A** | mechanism is load/unload churn → fix = hold a reference, or one run returning arrays |
| **C ≈ A** | the ~1 s is inside `Open VI Reference` even when resident → the *only* fix is fewer runs |
| **A flat vs. A rising**, plus `h1 − h0` | separates fixed per-run cost (a) from handle accumulation (b) |
| **W returns owner uids 10407 + 23499 in ~3 s** | the 601.6 s census was never necessary — the route existed and was already built |

Two guards, both from your own record: probe md5 before **and** after, exactly as the read-only run 9 did (`d1-build-plan.md:801`); and **do not read `Is Broken?`** in this script — that readback perturbs the target because it must be ordered after a `Connect Wire` (`docs/NAMES.md:920-929`). `Terms[]` / `Is Source?` / `Owner` do not.

---

## One fact the record does not report, and should

`tools/bench/diag_c64_row1_testa.json:211` reads **`"test_b": {}`**, with `"elapsed_s": 79.8` and `gates 7 pass / 0 fail` — the last `dump()` fired at the end of TEST A. The 601.6 s census survives as a single printed line and nothing else; the closing gates `Z_1` / `Z_1b` / `Z_1c` never ran, so **a run whose headline property is "READ-ONLY: nothing is edited" cannot prove from its own artefacts that it changed nothing**, and `test_b`'s per-member rows exist in no file. That is your own standing rule — *a step is not done until it has left a file* — broken by the same 22-minute overrun the claim treats as a mere under-estimate.

**What would change my mind:** arm **B** coming back at ~1.3 s. If the identical `node_terms_uid` call is as slow against a small VI as against the 476 KB one, the fixed-open account collapses and the claim's "inherent" is right. Everything else I have said follows from the cost being a function of the target, which is what `toolkit-capabilities.md:340-361` already measured and what `report_all` already exploits.

**Sources:** [Wire class — LabVIEW Wiki](https://labviewwiki.org/wiki/Wire_class) · [Vi Scripting: inconsistent behaviour of terms[] of a wire / owner — NI](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055) · [Building VI Server Applications — NI](https://www.ni.com/docs/en-MY/bundle/labview/page/building-vi-server-applications.html) · [Open VI reference is very slow if VI is not already loaded in memory — NI](https://forums.ni.com/t5/LabVIEW/Open-VI-reference-is-very-slow-if-VI-is-not-already-loaded-in/td-p/3337386) · [Closing References in LabVIEW — NI](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) · [Terminal class — LabVIEW Wiki](https://labviewwiki.org/wiki/Terminal_class)

## Sources

(extract from answer)

## What was done with it

Dispatched by cycle 65 material #1 part A to discharge the standing build gate: `guard_peer.py` refused
every build while `tools/bench/diag_c64_row1_testa.log` (`BGRUN TIMEOUT killed after 1321s`) was the newest
failing log. Outcome classified from the dispatcher's own line: **ANSWERED (472 s)**, agent `claude`, role
`hypothesis`, model opus / effort max, `$3.5805`, log `tools/bench/peer_c65_testa_timeout.log`
(`BGRUN END rc=0 after 473s`), task `tools/bench/peer_c65_testa_timeout_task.md`. Not a
TIMEOUT/QUOTA/ERROR, so it discharges; no re-dispatch was needed and only ONE review was run this dispatch.

**It REFUTED the claim at its centre.** My claim was "~1.3 s per node is inherent, nothing is wrong with the
tooling". The review shows the unit is the **op RUN**, not the node: `net_of` issued 103 `node_labels` +
450 `node_terms_uid` + 1 `report_all` = **554 runs in 601.6 s = 1.086 s per run**, which lands on this
project's OWN measurement of the fixed per-run cost against the main VI — `docs/toolkit-capabilities.md`
"one bare op run, the MAIN VI 960.8 ms" vs "SMALL target VI 10.4 ms", and "class Terminal (5763 objects)
1222 ms" against "class Local (8 objects) 991 ms", i.e. **720x the objects for +23 % time**. The traversal
is not the cost; re-opening a 476 KB VI 554 times is. My "1.34 s per node" divided 601.6 s by the nodes
alone and silently charged the 103 diagram runs to them. The review also names this a repeat of a cost
`report_all` was built to end (`tools/gscript.py:491-494`, "618 s measured ... this pays it once").

**Implemented in `tools/bench/diag_c65_s3b_row2.py` — mechanical only, no step of row 2's route changed:**

1. **Point (e), the fixed budget that guaranteed the kill.** `t3_budget_s()` derives every scan budget from
   the wall clock actually left (`RUN_DEADLINE_S - elapsed - RESERVE_S`, capped at `T3_MAX_BUDGET_S`),
   with 600 s reserved for the restart, the cold reopen and the ordered pass. TEST B's budget was a fixed
   600 s per wire, so 2 wires + 2 restarts + TEST A exceeded the 1320 s process deadline **before the first
   COM call**. A budget that runs out now stops the scan and says so in `scan_stopped`; it can no longer
   spend the whole process deadline.
2. **"One fact the record does not report."** `diag_c64_row1_testa.json:211` reads `"test_b": {}` because
   the last `dump()` fired at the end of TEST A, so the 601.6 s census survives as a printed line and in no
   file, and the closing md5 gates never ran. `t3_separator` now calls `dump()` on return, and `dump()` was
   added after the cold censuses and after the cold far-end gate, so every phase leaves a file before the
   next one can overrun. (CLAUDE.md, 2026-09-19: "a step is not done until it has left a file".)
3. **(a)-vs-(b), which the record could not separate.** `t3_separator` now records **every individual call's
   elapsed time** (`per_call_elapsed_s`, printed as first-5 / last-5, never an average — "the shape is the
   measurement") and the LabVIEW handle count either side of the scan. Flat ~1.09 s ⇒ the fixed open (a);
   monotonically climbing ⇒ handle accumulation (b) on top.
4. **The scoping error is already absent from this build and is now stated in the code.** The review's
   second point — a wire is owned by exactly one diagram, TEST A had already found both nodes on diagram
   index 46 after scanning 1 diagram of 173, and TEST B then searched 103 — does not apply to row 2's
   separator, which scans `Diagram #639` only (`T3_SCAN_LIMIT`, one diagram). The docstring now says so and
   the record carries `"scoped_to": "Diagram #639 only"`, `"diagrams_scanned": 1`.

**RECORDED, NOT ACTED ON — each would change row 2's verification instrument or add a new measurement, so
it is judgement's call, not this dispatch's:**

- The direct answer to my question — **`Wire >> Terminals[]` = property 6371003, short name `Terms[]`**, and
  the already-built read-only wrapper **`wire_source_owner(target, wire_uid, n=6)` at
  `tools/recipes/build_opconnectfromwire_v0.py:423-447`** (`OpWireSource_v5.vi`), measured at "2-3 op runs
  ~3 s" against 601.6 s, with the honest caveat that `Terms[]` returns ControlTerminals too and a
  ControlTerminal's `Owner` is the Diagram, so it yields owner class + uid, **not** `Diagram[46].Nodes[24]`.
  Substituting it for the terminal-side T3 census would change what the gates read.
- The review's **§4 discriminating test** (10 timed `node_terms_uid` calls on the big target, the same call
  on a small scratch target, the same again while a reference is held resident via `g.vi_ref`, then
  `wire_source_owner(STEP9, 23502)`), ~45 s of LabVIEW time under `bgrun --max-min 8`. It is a separate
  read-only diagnostic and was **not run here**; part B's per-call timings collect the (a)-vs-(b) half of it
  as a by-product.
- Its structural implications — holding a VI reference resident, or an op that returns arrays in one run —
  would mean editing `tools/gscript.py` or building a new op, both forbidden by this brief.
- Its explanation **(c)** (cross-apartment marshalling, named and killed by the reviewer itself: the same
  path costs 10.4 ms against a small target) and **(d)** (the dialog watchdog, ruled out by reading
  `gscript.py:370-373`) are recorded as closed, with nothing to do.
- Its warning not to read `Is Broken?` in a measurement script (`docs/NAMES.md:920-929`) is already this
  build's rule: the ordered pass is LAST, after the cold reopen, after every save (42(b), 52(f)).

Nothing in the review was contested. No route was changed, no plan document was edited,
`CYCLE_GUARD_OFF` was never set.
