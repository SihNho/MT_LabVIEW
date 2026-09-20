# priorart-routeb-run3-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** fact
- **cost:** $6.3419  in 68 / out 43146 / cache-create 251807 / cache-read 5395835  (617s, 57 turn(s))
- **date:** 2026-09-17 17:43:45
- **outcome:** ANSWERED (619s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

PRIOR-ART REVIEW (trigger: new-op).

You are checking ONE thing: has this already been done here? Do not review the plan's merits -
other reviews do that. Answer in two parts, naming a FILE and LINE for every finding. A finding without a citation
cannot be acted on, because the only way this review is released is by someone opening your citation and showing in
writing that it does not cover their case.

PART A - THE DIRECTION (this is the part that matters most)
 A1 SETTLED ALREADY. Has this direction, or its central question, already been decided or answered in STATUS.md,
    docs/ or archive/? Quote the decision and its date.
 A2 REFUTED ALREADY. Has this direction already been tried, abandoned, or argued against - in an archived peer
    review, a retrospective, or a superseded plan section? Say what killed it and whether that still applies.
 A3 CONTRADICTED. Does any fact the plan cites conflict with something else in these files? Quote BOTH sides. A
    summary line that contradicts its own section 40 lines earlier counts, and has happened here.
 A4 UNREAD EVIDENCE. Which existing document should obviously have been consulted for this direction and clearly
    was not? Name it.

PART B - THE ARTIFACT, if the plan builds or changes one
 B1 ALREADY BUILT. Does an op, recipe, helper or VI already do this, possibly under another name? Check
    tools/gscript.py's functions, tools/recipes/, docs/toolkit-capabilities.md and the claudeDev VI names.
 B2 ALREADY FAILED. Has this exact build been attempted and failed? What did the record say was the cause, and
    does the new plan address that cause or repeat it?
 B3 HELPER EXISTS. Is the plan hand-rolling something the toolkit already provides - indexing, identification,
    wiring, saving, censusing? Name the call.
 B4 ALREADY MEASURED. Has the question this artifact would answer already been measured and written down?

End with machine-readable lines, one per finding:
  PRIOR-ART: settled-already | refuted-already | contradicted | unread-evidence
  PRIOR-ART: already-built | already-failed | helper-exists | already-measured
  PRIOR-ART: novel
`novel` only if none apply. Do not invent slugs.

THESE VERDICTS STOP THE WORK. Any slug other than `novel` blocks the next build until someone opens your citation
and refutes it in writing. So be precise about what your citation actually covers: an over-broad match costs real
work, and a missed one costs a whole build cycle.

=== WHAT IS UNDER REVIEW ===
# Route B run 3 — implementing the two judgement decisions, and nothing else

Changed file: `tools/recipes/build_d1_routeb_v0.py` (edited 2026-09-17 17:06, not yet run).
New diagnostic: `tools/bench/diag_sr_transport.py` (read-only, not yet run).
Prior state: run 2 = 84 pass / 2 fail, ledger **63 WIRED / 0 FAILED / 3 NO-ROUTE**
(`tools/bench/build_d1_routeb_v0_run2.log:408`), `ExecState 0`, nothing saved.

## What the judgement session decided (session brief, 2026-09-17), and what I am building

**(1) `#1359` t1 and `#29874` t3 get two lock-stepped queues `Q_sr1` / `Q_sr2`** — enqueued in loop 1.1 each
iteration with the frame, dequeued in 1.2 in the same iteration as `Q_work` (`docs/stage2-assembly-step-c.md`'s
paired producer/consumer shape, 162/162 in replay). Their source is a `LeftShiftRegister` of `#637` that STAYS
on 1.1 while both sinks move into 1.2, so a direct wire between two sibling loops is illegal.
MEASURED basis: `tools/bench/d1_tunnel_sources.json` — the source terminal of `w9097` / `w28039` is owned by
`LeftShiftRegister` **#9025** / **#29512**, "neither a node on diagrams (19, 43, 0) nor a LoopTunnel".

Implementation, per row (`build_d1_routeb_v0.py`, function `sr_queue` inside `s3w`):
* `Obtain` on `Diagram #686` (outside both loops), element TYPE from a NAMED node output;
* `Enqueue` inside 1.1's body (`Diagram #639`), tunnel auto-created (`docs/NAMES.md:762`);
* the enqueue's `element` **branched off the LEFT register's own inside wire** with `OpConnectFromWire_v0`;
* `Dequeue` inside 1.2's body; its `element` → the sink by INDEX with `OpConnectNested_v1`;
* `Release` outside both loops.

**RULE 1a, the part I think is the crux:** what `#1359` t1 consumed is the LEFT register's OUTPUT — the PREVIOUS
iteration's value. Enqueueing from the node that WRITES the partner RIGHT register would advance the value by one
iteration while every structural gate stayed green. So that node is used ONLY as the queue's TYPE source (a type
carries no value) and the VALUE is branched off the left register's own wire.

**(2) `#2222` t0 ← control `Z/dZ` (uid 47), UNNAMED sink** (`from_ctl_unnamed`): `wire_control` is name-addressed
on both ends. Use the control's OWN wire if it has one on this copy (measured per run); otherwise create a
TEMPORARY named sink (a bare `Equal?` via `OpCreateEqual_v0`, 23/0), `wire_control` into its `x`, branch off that
wire by index with `OpConnectFromWire_v0`, delete the temporary, and RE-READ the sink.

## The facts the build does not have, and how it gets them

`queue_node('obtain', …)` takes the element TYPE from a NAMED OUTPUT TERMINAL of an existing node
(`tools/gscript.py:1068-1074`), and `STATUS.md`'s NEXT says route B §2b "never says which terminal each of the 8
queues takes". `tools/bench/diag_sr_transport.py` measures it read-only on a pristine copy in the same runner
(P1–P6: the two registers and their partners, the single source terminal of each partner's inside wire, its
NAME and Traverse class/index, `Z/dZ`'s net, `#2222` t0's state) and writes `tools/bench/sr_transport.json`,
which `sr_queue` reads. Nothing is cached across the two: every address is re-read live at wiring time and the
run REFUSES the row if the register index drifted.

## Stated in advance: this CANNOT reach `ExecState 1`

`s1q` (the 8 queues) and `s4b` (the three sentinel `Equal?`s) are both still SKIPPED — the element types of the
other six queues are an undesigned row and the sentinels depend on them — so 1.2 / 1.5 / 1.7 keep UNWIRED
conditional terminals, which is a broken VI by construction. Run 3's target is the LEDGER gate (**0 FAILED,
0 NO-ROUTE**) plus the new gate "both SR queues built", not the save.

## Also in this run (bug found while editing, not a new feature)

`s3w`'s RETARGET name check appended `(tag, …)` before `tag` was assigned — a latent `NameError` run 2 never
reached because no row mismatched. `tag` moved above the block.

## The questions I want attacked

1. Has this cross-loop transport already been built, measured or REFUTED in our own files under another name?
2. Is branching the enqueue's `element` off the LEFT register's inside wire actually value-preserving, or is
   there an ordering hazard (the enqueue and the register's writer race within the same iteration)?
3. Does a `queue_node('obtain', …)` typed from the partner-writer's output give the SAME type the register
   carries, or could a coercion make it merely compatible?
4. Is a bare `Equal?` with no source wiring something `OpCreateEqual_v0` can create at all, and is deleting a
   temporary sink safe when the branch and the temporary's segment belong to ONE net?
5. What existing helper already does any of this, so the new code is redundant?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS — read this first. One screen. Detail is one layer down, never appended here.
Narrative → the `archive/2026-09-17-status-*.md` set (**`…-d1-route-b-2.md` = the latest session**)
+ `archive/2026-09-16-…`. ⚠️ **ONE SESSION AT A TIME** — re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + §11c–§11u)** — §5/§5a-bis (moves), §10 (S/N1/F1/F2).
   ⚠️ **§11t CLOSED ROUTE A; B is now BUILT — `tools/recipes/build_d1_routeb_v0.py`, plan `docs/d1-route-b-plan.md`.**
   §11u says the run-9 "Remove Bad Wires deleted 3 of 8" gate was UNSOUND — never cite it. 2. ⚠️ A prior-art
   dispatcher's log MUST be named `priorart_*` / `peer_*` (`tools/logclass.py`) or the guards read the reviewer's
   prose as a build failure. 3. ✅ Scripting EDITS need the target's FRONT PANEL open; a fixed op PATH is served
   from LabVIEW's MEMORY — unique scratch name/run.
4. ✅ `guard_cycle` releases on a `FIXED: <slug> - <path>:<line> - …` line under a prior-art archive's "What was
   done with it" (§11g.3) — ONE PER SLUG, or `REFUTED:` with the citation opened. 5. ⚠️ `peer.ps1` only as
   `powershell -Command "& 'tools/peer.ps1' … -TaskFile <f>"` — `-File` loses a multi-line `-Task`;
   and `tools/prior_art_review.py` must be launched from **PowerShell**, not the Bash tool (rc 127 there today).
6. 🔴 **NEVER patch a file with a `py - <<'EOF'` heredoc** — on 2026-09-17 one truncated **this file to 0 bytes**
   mid-write on a lone-surrogate `UnicodeEncodeError`. Use Edit/Write (CLAUDE.md already says so).

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: material/cycle15-route-B-3-save-it
  since: 2026-09-17 16:5x
  purpose: OPEN 38 (Q_sr1/Q_sr2 + Z/dZ) -> route B run 3 -> save Track_v6_D1_GPU.vi; OPEN 39 OpGetErrors_v0
# 2026-09-17 15:3x-16:3x material/cycle15-d1-route-B-2: RELEASED. ✅ **ROUTE B BUILT — 63 WIRED / 0 FAILED /
# 3 NO-ROUTE** (`build_d1_routeb_v0_run2.log`, 84 pass / 2 fail, 548 s). Runs, all bgrun, all BGRUN END:
# `peer_dual_selftest.log` rc=0 100 s · `priorart_routeb_census.log` rc=0 502 s (6 findings) ·
# `diag_moved_structure_terminals.log` **39/0, 113 s** · `priorart_routeb_build.log` rc=0 506 s (7 findings) ·
# `build_d1_routeb_v0.log` 84/2 415 s · `peer_routeb_noroute.log` rc=0 512 s (codex ANSWERED 87 s, opus
# TIMEOUT 420 s) · `retro_cycle15_routeb.log` rc=0 365 s · `build_d1_routeb_v0_run2.log` 84/2 548 s.
# ORIGINAL md5 2a78e17c449cacdaf5da389818526859 before AND after EVERY run. 4 scratch classes, ALL created and
# deleted in the same run; claudeDev holds no leftover and NOTHING was saved. No GUI, no hardware.
# Handles 30,680 → 38,803. Relocated VERBATIM -> archive/2026-09-17-status-d1-route-b-2.md §1; all EARLIER
# sessions (route-B-1 back to run 5) likewise RELEASED, md5 unchanged -> …-d1-route-b-1.md §1.
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ≈31,500 handles; unique scratch name/run.
## HARDWARE — permission follows the RIG STATE. Current: **분해 / DISASSEMBLED ⇒ everything allowed**
**분해 ← WE ARE HERE** = motors ✅ ASI ✅ camera ✅ · 조립 = ❌ ❌ ✅ · 실험중 = ❌ ❌ ❌. ⚠️ The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** · magnet full travel · camera
1280×1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** →
the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `…CPU_core_v0` 69/69 · `…_queue_v0` 162/162 — **say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay**. **THE GAP:** 174 ops, 123 recipes, 235 peers → **zero
runnable experimental VIs**.

## OPEN — one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `…-d1-phase-full-…` §0c)
1–3, 5, 9–12 — **archive §9**: PERIODIC auto-reset ungated · autofocus CLOSED (3.6 Hz) · 27 undisposed peer
   archives · startup drives instruments · A2 54/54, A3 112/170 · doc lint 2/4/3. **18 CLOSED by §11h — no TIFF is
   written any more.** 13/14/15b/17b: ✅ stop measured (`#637` term **648 ← w3457 ← #11639**) · 🔴 `bgrun --detach`
   misses an orphaned grandchild · 🔴 v3's R11 scored the *restart*, so the stop is unproven.
16 · 19/25/26 · 20–23 · 27 · 28 · 28b · 28c/d/e · 29 · 30/30b/30c — ✅ ALL CLOSED; text in
   `archive/2026-09-17-status-d1-full-build-5.md` and `…-d1-route-b-1.md` §5. Headlines: relocation MEASURED
   (`WhileLoop 3→6`, `Diagram 170→173`, source map **109/109**) · `OpCreateConstOnTerm_v0` 22/0 · 28c was the
   CALLER never setting `UID 2` · §11h: the TIFF writer is not original, F1 uncapped.
28f · 31 · 32 — one line each, full text in `archive/2026-09-17-status-d1-route-b-1.md` §4 and
   `…-status-open-28f-35.md`: 28f run 7's 35/7/24 is SUPERSEDED by run 9's 42/6/18 · 🔴 31 the retrospective
   still reviews the WRONG window (`retrospective.py:282-286`; cause = `guard_cycle.stamp()` = min(ctime,
   mtime)) — **reproduced again today**: the cycle-15-routeb retrospective reviewed the morning's
   `OpConnectNested` work and never mentioned route B · 🔴🔴 **32 outcome review: six `OUTCOME-VIOLATION`s,
   SECOND consecutive time ⇒ the work stops for a re-plan with the USER.** Not answerable by a device.
33 · 34 · 35 — ✅ CLOSED; VERBATIM in `archive/2026-09-17-status-d1-route-b-1.md` §2: `OpConnectNested_v1`
   built+saved and measured in the real VI · gscript's COM poison fixed (11/0). ⚠️ its "survives RBW" gate is
   RETIRED by §11u.
36 · 37 — ✅ **BOTH CLOSED 2026-09-17**; full text relocated VERBATIM to
   `archive/2026-09-17-status-d1-route-b-2.md` §2/§3. Headlines: the 16 `from-tunnel` rows are WIRED, every one
   `Wire.Is Broken? FALSE` · OPEN 37's cause was never a tunnel SIDE — `#5540` t1 is an unnamed SINK on the
   pristine original, and the index shifted because the failing run's own `bare()` (wire delete + Remove Bad
   Wires) DELETED THE TUNNEL. ⚠️ **A `GObject.Move` costs nothing** (`Wire 1902→1902`, `LoopTunnel 132→132`),
   but after a move EVERY terminal of a moved structure reads `is_source` FALSE **including its OUTPUT tunnels**
   — so address those rows by INDEX, which survives, never by `is_source` alone.
38. 🔴 **NEW — route B is BUILT and its ledger is 63 WIRED / 0 FAILED / 3 NO-ROUTE** (run 2,
   `tools/bench/build_d1_routeb_v0_run2.log`, 84 pass / 2 fail, 548 s; run 1 was 51/0/15). The plan's own S3w
   gate is "0 NO-ROUTE" and the **3 that remain are the ones the plan already calls judgement**: `#1359` t1 and
   `#29874` t3, whose source is a `LeftShiftRegister` of `#637` that STAYS on loop 1.1 (a cross-loop TRANSPORT
   choice, §6 R1's residue), and `#2222` t0 ← control `Z/dZ` with an unnamed sink (§6 R3). ExecState is 0 warm
   and **nothing was saved** — `Track_v6_D1_GPU.vi` does not exist. **Failure budget SPENT (2 runs).**
39. 🔴 `VI.Get Errors` **452 is still the missing instrument.** Run 1's whole-VI count of 420 bare named inputs
   discriminated nothing (an unwired `error in (no error)` is legal); run 2's narrowed 56 is not a verdict either.
40. ✅ `peer.ps1` role **`hypothesis`** (opus/**max**, the only claude role with WebSearch/WebFetch) + **`-Dual`**
   (one `-TaskFile` → codex AND that role, archived `<slug>-codex`/`-opus`). First real use: **codex ANSWERED
   87 s, opus TIMED OUT at 420 s.** One data point, against the opus arm; `-TimeoutSec` may be too low.

## NEXT
✅ **ROUTE B WORKS.** One recipe, `tools/recipes/build_d1_routeb_v0.py`, takes a fresh copy of the original to
**63 of 66 attempted connections WIRED, 0 FAILED**, using the four writers already on disk and **no new op**. The
16 `from-tunnel` rows R1 called "the one that decides B" are all wired, each with `OpConnectFromWire_v0`'s own
ordered `Wire.Is Broken?` **6371004** reading **FALSE** — 13 of them from a `FlatSequenceInnerTunnel` source.
🔴 **THE THREE JUDGEMENT QUESTIONS, and they are the only things between here and a saved VI** (OPEN 38):
(1) how the two `LeftShiftRegister`-fed values (`#1359` t1, `#29874` t3) cross from loop 1.1 — a queue, a tunnel,
or moving the register; (2) `#2222` t0 ← control `Z/dZ` with an unnamed sink (R3); (3) whether to build
`VI.Get Errors` 452 so ExecState 0 stops being explained by inference (OPEN 39).
⚠️ **Stage 2 was NOT attempted**: `s1q` reports that `queue_node('obtain', …)` takes its element TYPE from a
named output terminal and route B §2b never says which terminal each of the 8 queues takes; sentinels, carriers
and the GPU kernel's 13+6 pane likewise. OPEN 32 (two consecutive outcome reviews demanding a re-plan with the
USER) still stands above all of this.

## Where to look
`CLAUDE.md` · **`docs/decisions.md`** · `docs/NAMES.md` · **`docs/toolkit-capabilities.md`** · **`docs/d1-route-b-plan.md`** = the build order · `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.



## Answer

Write is disabled in this session (correct for a read-only reviewer), so the review is below in full.

---

# PRIOR-ART REVIEW — Route B run 3 (`Q_sr1`/`Q_sr2` + `Z/dZ`)

Read-only. No LabVIEW opened, no lock taken, nothing run. Every claim carries a file:line or a URL.

**Verdict: NOT novel.** Two findings would change the build; five more are cheaper corrections.

---

## PART A — THE DIRECTION

### A1 · SETTLED ALREADY — this shape already has a decided mechanism, and it is not a queue

The direction is stated as "two sibling loops cannot be wired directly, so the value crosses through a queue". But the thing crossing is not a value in flight — it is a **loop-carried register**, and this project decided how those are handled, twice:

> `docs/frame-loop-wire-graph.md:397` (2026-09-14) — *"every row of kind shift register is state that crosses frame boundaries inside the frame loop today; in the rebuilt seven-loop design **each must live in exactly one loop (rule: one writer)**."*

> `docs/d1-build-plan.md:446` (REV 4 §7.2) — *"**`#376 save trace.vi` moves into 1.7 with its two shift registers** (`#15/#51` total data array, `#24/#1108` error chain) and keeps producing exactly what it produces today."*

`#376` is the identical shape: a node that both reads the left side and writes the right side of a `#637` register, moving into a new loop. The decided answer was *the register goes with the node*, and `docs/d1-route-b-plan.md:119` already budgets that mechanism — "8 shift registers (4 on 1.2, 2 on 1.5, 2 on 1.7)", built with `add_shift_reg` + `wire_sr`. `#1359`'s and `#29874`'s registers are not among them.

**Scope of this finding:** it does not say a queue is forbidden. It says the plan proposes a *different* mechanism for a shape that already has a decided one, one section away in the same build plan, without saying why.

### A2 · REFUTED ALREADY — "a queue standing in for a shift register" was dispatched, attacked, and abandoned

> `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:32` (the question asked) — *"Attack the declared fallback: three depth-1 queues standing in for three shift registers … Name a concrete way that deadlocks, reorders, or differs numerically from a shift register in LabVIEW dataflow/clumping — or say plainly that it cannot."*

> `:91` — *"Under very strict assumptions — each queue is seeded exactly once, every iteration performs exactly one successful dequeue and one successful enqueue on each queue, operations have infinite timeouts, nobody else touches the queues, and all three operation chains are dataflow-ordered — the queues cannot reorder values."*
> `:101` — *"Three separate queues also lack atomic tuple alignment … can become iteration-skewed."*
> `:103` — *"in the fault-free strict case, the queue mechanism should not change the array values … But it differs in scheduling, allocation/reference lifetime, error behavior, shutdown behavior, and persistence semantics."*

Disposition (`:126-129`): the queue fallback was dropped and replaced by the direct `Loop.Add Shift Register` **6361000**, built as `OpAddShiftReg_v0`.

**Does it still apply?** Yes, and more strongly: that case was three queues inside **one** loop; run 3 is two queues **across two** loops, which weakens every assumption the peer listed. One item does *not* apply and I will not let it be used against the plan: the "uninitialised register persists between runs" difference is irrelevant here, because both registers **are** initialised — `#8953 Initialize Array` and `#28124 Initialize Array` (`docs/frame-loop-wire-graph.md:440,:444`).

Second refutation, more recent and specifically about these two rows:

> `archive/peer/2026-09-17-routeb-run1-noroute-codex.md:146` — *"'owned by a shift register' is insufficient evidence that a queue is required. You need the producer/consumer timing requirement."*
> Its own disposition, `:186-189` — *"Point 3 accepted as a correction to my wording … the reason line now says 'a cross-loop TRANSPORT question', **with the timing claim removed**."*

`tools/recipes/build_d1_routeb_v0.py:756-759` restores exactly that removed claim — *"enqueued in 1.1 each iteration with the frame and dequeued in 1.2 in the same iteration as `Q_work`"* — with no measurement added since the retraction.

### A3 · CONTRADICTED — two, and the first one stops the run

**(i) The run cannot pass its own new gate, and the file that says so is from 2026-09-14.**

The queue's element TYPE is taken from "the node that WRITES the partner RIGHT register". Those nodes' terminals are `#1359` t2 and `#29874` t5, and **both are unnamed**:

> `docs/frame-loop-wire-graph.md:417` — `| 8 | (unnamed) | 9018 | #1359 For Loop t2 `` (wire 9215) |`
> `:421` — `| 12 | (unnamed) | 29505 | #29874 For Loop t5 `` (wire 29591) |`
> `tools/bench/d1_rewire_sources.json:702` — `"name": ""` · `:1614` — `"name": ""`

Against the new code:

> `tools/bench/diag_sr_transport.py:160-162` gates on `bool(named and named.get("term_name"))` — `""` is falsy, so **P3 fails**.
> `tools/recipes/build_d1_routeb_v0.py:794-799` turns a missing `term_name` into `noroute` — so **both rows return NO-ROUTE**.

Run 3's stated target is "0 FAILED, 0 NO-ROUTE plus both SR queues built". On the evidence already on disk it reaches neither, and the ~550 s build is spent to learn something two lines of an existing document already state.

**(ii) The source of the value is described two ways in our own files, and the difference is `index_mode`.**

> `tools/bench/d1_rewire_sources.json:689-694` — `#1359` t1's source is `{"kind": "tunnel", "uid": 9087, "index_mode": 1}`
> `:1566-1571` — `#29874` t3's source is `{"kind": "tunnel", "uid": 29911, "index_mode": 1}`

versus the brief's *"the source terminal of `w9097`/`w28039` is owned by `LeftShiftRegister` #9025/#29512"*. Both are true of different hops — the register drives the wire, the wire lands on the For loop's own **auto-indexing** input tunnel — but the plan never mentions `index_mode 1`. The plan already treats index mode as a thing to re-assert after restructuring (`docs/d1-route-b-plan.md:333`, gate S3d, `IndexMode 0` on six *whole-array* tunnels); these two auto-indexed tunnels have no gate at all. If either comes back index-mode 0, the For loop's N changes and the per-bead maths changes with every structural gate green.

### A4 · UNREAD EVIDENCE — `docs/frame-loop-wire-graph.md`'s state-carrier sections, and the consequence nobody has written down

**The write-back has no route, and the build will not notice.** Chain of already-measured facts:

| fact | citation |
|---|---|
| right register **9018** is fed **each frame** by `#1359` t2 (w9215); right **29505** by `#29874` t5 (w29591) | `docs/frame-loop-wire-graph.md:417`, `:421` |
| both registers are in the **"stay 1.1"** column | `docs/d1-build-plan.md:365` |
| both writers **move into 1.2** | `docs/d1-route-b-plan.md:126-127` |
| both writes are classified `"action": "source-side"` with **`"sinks": []`** | `tools/bench/d1_rewire_sources.json:699-710`, `:1612-1622` |
| the ledger **excludes** every `source-side` row | `tools/recipes/build_d1_routeb_v0.py:636-639`; rationale at `docs/d1-route-b-plan.md:169-170` (*"re-connected from its sink's side … need no call of their own"* — which is false when the sink is a shift-register terminal, not a node) |
| no fresh register is created for either | `tools/recipes/build_d1_v0.py:282-287` (`SHIFT_REGS`: 1147/1142, 5796/5805, 119/2972, 7311/11001, 4256/4274, 4334/4344, 15/51, 24/1108 — neither pair present) |

**Consequence:** after run 3, registers 9018 and 29505 have **no writer**. Their left side yields the `Initialize Array` seed on every frame forever, where the original re-writes it each frame. The queue transports the read faithfully and the accumulator it reads from is dead. Nothing in the ledger, the S-gates, or `ExecState` can see this — `ExecState` is explicitly not read until S5, and an unwritten register is not a broken wire.

This is the one finding I would not release without a measurement. The `#376` precedent (A1) is the recorded remedy.

---

## PART B — THE ARTIFACT

### B1 · ALREADY BUILT — three components, with their scope stated

1. **Paired producer/consumer queues** — `docs/stage2-assembly-step-c.md:39-42`: *"The paired queues are FIFO and produced/consumed once per iteration by a single producer/consumer; their enqueues are **error-chained** (second `error in` ← first `error out`) so a failed first enqueue cannot publish a partial pair"*, plus the `META[n] == Frame Paths[n]` alignment gate. **Scope:** the topology exists; `Q_sr1`/`Q_sr2` do not. What the run-3 plan omits is the two things that make the pattern lock-stepped — the error chain and an alignment gate — while adding two more streams to the set.
2. **Temporary sink → branch → delete the temporary** (decision 2's fallback) — `archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:14-15`: *"temporary indicator to create the wire, then `wire_indicators` branches the pane indicator onto it, then the temporary one is deleted"*; the same trick twice more in `docs/stage2-assembly-step-b.md:48-50` and `:63-67`.
3. **The register alternative to decision 1** — `gscript.add_shift_reg` + `wire_sr` (`docs/toolkit-capabilities.md:41-42`), already called by this very recipe at `tools/recipes/build_d1_routeb_v0.py:615-619`. ⚠️ **Honest limit, so this is not read as a free fix:** `wire_sr`'s `LeftOutNode` variant reaches a *top-level* node via `VI.Block Diagram` (`toolkit-capabilities.md:42`), and the initialisers `#8953`/`#28124` sit on `Diagram#686`, which `docs/diagram-hierarchy.md:95-97` measures as a **FlatSequenceFrame** diagram, not the top level. The evidence does not settle which route is cheaper. It does settle that the write-back must exist either way.

### B2 · ALREADY FAILED — no exact prior failure; **I am not firing this slug**

There is no record of a `Q_sr1`/`Q_sr2` build or of this `Z/dZ → #2222` t0 build. The nearest record is the 1055-modal class (`docs/NAMES.md:473-475`: an invalid terminal refnum makes the creator call `Connect Wire` with an invalid reference → *"error 1055 dialog … that blocks the run"*; `:478-480`: an error-out indicator does **not** silence it) — which is a live hazard for the bare-`Equal?`, not a repeat of it. The contract mismatch itself is covered by A3: `OpCreateEqual_v0` fetches both operands inside the op from `Get Outputs` (`docs/toolkit-capabilities.md:52`), `tools/recipes/build_opsentinel_ops.py:397,400` passes `Names`/`Names 2` straight through, and `tools/recipes/build_d1_routeb_v0.py:747` calls it with `src_names=()`. The recipe's own docstring (`:742-744`) already admits this is unmeasured. A modal dialog is disqualifying under the unattended-run requirement, so this path should not be first-choice in a run nobody is watching.

### B3 · HELPER EXISTS — two, both answering questions the plan asks

- **`gscript.set_index_mode(target, tunnel_index, mode)`** — `tools/gscript.py:1798`, for A3(ii).
- **`Wire.Disconnect Terminal` `6370C0D`** — `docs/NAMES.md:896`, established in `archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:28-35`. That file **answers question 4 outright**: `:24` — *"A branched net is represented by one `Wire` object … deleting the Wire GObject removes the complete net"*; `:32-35` and the disposition `:49-52` — deleting the disposable **sink node** and running Remove Bad Wires keeps the branch. So decision 2's delete step is safe **provided the temporary NODE is deleted, never the wire**. No new measurement needed. The recorded hazard for this trick is in `gscript.wire_indicators`' own docstring, `tools/gscript.py:1708-1713`: *"Each source terminal MUST ALREADY BE WIRED … An UNWIRED source makes it extend an unrelated wire instead → 'This wire connects more than one data source' and the target breaks."*

### B4 · ALREADY MEASURED — the diagnostic re-measures what is on disk, and skips what is not

- Register geometry: `docs/frame-loop-wire-graph.md:403-424` (right side: uid, per-frame writer, wire) and `:426-447` (left side: initialiser, per-frame reader, wire). Rows 8 and 12 at `:417`, `:421`, `:440`, `:444` carry every fact P1–P3 goes to LabVIEW for.
- **Question 3 has a recorded answer, and it is "not structurally":** `docs/stage2-assembly-step-b.md:53` — *"the fleet cannot read type descriptors, so the gate is FUNCTIONAL instead."* So no `diag_*` can establish that the queue carries the register's type; only a run against the fixture can. This matters because LabVIEW queues are strictly typed and a near-miss surfaces as a **coercion dot**, not a break — i.e. silently, which is the rule-1a failure mode ([NI forum: keeping types straight](https://forums.ni.com/t5/LabVIEW/How-to-keep-types-straight-in-PPLS/td-p/3298363), [element data type of a queue](https://forums.ni.com/t5/LabVIEW/Is-it-possible-to-get-the-element-data-type-of-a-Queue-from/td-p/3055592)).

---

## On question 2, since the evidence separates its two halves

**The VALUE is safe; the ORDERING is not measured.** A left shift-register terminal holds one fixed datum for the whole iteration — the right terminal's value transfers to the left at the end of an iteration and is what the body reads for all of the next one ([LabVIEW Wiki: Shift register](https://labviewwiki.org/wiki/Shift_register)) — so a branch off that wire is value-identical to what `#1359` t1 read, and there is no write/read race within the iteration. The reasoning in `build_d1_routeb_v0.py:760-764` is right on that point.

What is *not* established is that the enqueue stays paired with `Q_work`: the enqueue has no dataflow dependency on the rest of 1.1's body, and `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:101` names iteration skew as the failure mode. The project's own answer is the error chain at `docs/stage2-assembly-step-c.md:39-42`, which this plan does not adopt. Separately, `docs/NAMES.md:763-764` — *"**Never run a scripted VI with a `Dequeue(-1)`**: a producer that silently produces nothing … turns it into a COM hang"* — applies to two new queues that get no sentinel (only three are planned, `docs/d1-route-b-plan.md:337`).

---

```
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
```

**Sources:** [LabVIEW Wiki — Shift register](https://labviewwiki.org/wiki/Shift_register) · [NI forum — keeping types straight in PPLs](https://forums.ni.com/t5/LabVIEW/How-to-keep-types-straight-in-PPLS/td-p/3298363) · [NI forum — element data type of a queue](https://forums.ni.com/t5/LabVIEW/Is-it-possible-to-get-the-element-data-type-of-a-Queue-from/td-p/3055592)

## Sources

(extract from answer)

## What was done with it

**THE BUILD WAS STOPPED BEFORE IT RAN. Decision (1) — `Q_sr1`/`Q_sr2` — is refuted and is handed back to
judgement; decision (2)'s temporary-sink half is disarmed.** `tools/recipes/build_d1_routeb_v0.py` now carries
`SR_QUEUE_AUTHORISED = False` and `TEMP_SINK_AUTHORISED = False`, and the RUN 3 block of its docstring records
why. The recipe was NOT executed, so no LabVIEW time and no ~550 s build were spent on a run that could not pass
its own new gate. Both `-Dual` arms ANSWERED (codex 332 s, opus 619 s) and reached the same conclusion; 12
findings, 0 `novel`.

**I confirmed each stopping finding from the files, without opening LabVIEW**, because a review is a hypothesis
until it is checked (CLAUDE.md rule 5):

| finding | what I read | verdict |
|---|---|---|
| A3(i) the type source does not exist | `docs/frame-loop-wire-graph.md:417` `\| 8 \| (unnamed) \| 9018 \| #1359 For Loop t2 …`, `:421` the same for `#29874` t5 → `#29505`; `d1_rewire_sources.json` `"name": ""` | **CONFIRMED.** `sr_queue` refuses a nameless type source, so both rows return NO-ROUTE and the run fails its own gate |
| A3(ii) the sink auto-indexes | `d1_rewire_sources.json`: both rows `{"kind":"tunnel","index_mode":1}` | **CONFIRMED.** `#1359` t1 auto-indexes an ARRAY and sets the For loop's N. A queue delivering one element per frame iteration is a different computation, and gate S3d covers six OTHER tunnels |
| A4 the write-back has no route | the same two rows: the registers are READ (t1/t3) **and** WRITTEN (t2/t5) by the moving node | **CONFIRMED.** The queue carried only the read side, so loop-carried state would silently stop updating |
| A1/A2 the mechanism was already decided, and the queue form abandoned | `frame-loop-wire-graph.md:397` "each must live in exactly one loop"; `d1-build-plan.md:446` `#376` moves WITH its two registers; `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:126-129` replaced queues-for-registers with `Loop.Add Shift Register` 6361000 | **CONFIRMED**, and a NAMED source exists after all: the initialisers `#8953` / `#28124` `Initialize Array`.`initialized array` (`:440,:444`) |

Also accepted, and acted on:
* **B2 — the bare `Equal?` risks a 1055 MODAL** (`docs/NAMES.md:473-480`: an invalid terminal refnum makes the
  creator call `Connect Wire` with an invalid reference and an error-out indicator does not silence the dialog).
  Disqualifying in an unattended run, so `TEMP_SINK_AUTHORISED = False`; the control's OWN wire is still read and
  used, which is the measured half of decision (2).
* **B3 — question 4 was already answered and I did not look.**
  `archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:24,:32-35,:49-52`: a branched net is
  ONE `Wire` object, so deleting the WIRE removes the whole net, while deleting the disposable SINK NODE and
  running Remove Bad Wires keeps the branch. My code already deletes the node, not the wire — right by accident,
  and now right on the record.
* **Question 2, split correctly by the reviewer:** the VALUE is safe (a left register terminal holds one datum
  for the whole iteration, so a branch off it is value-identical), but the PAIRING with `Q_work` is not
  measured, and `docs/stage2-assembly-step-c.md:39-42`'s error chain — the thing that makes the pattern
  lock-stepped — was not in the plan at all. If judgement ever revives a queue here, that is the missing half.
* **`docs/NAMES.md:763-764`**: never run a scripted VI with a `Dequeue(-1)`; the two new queues had no sentinel
  planned (only three are budgeted, `docs/d1-route-b-plan.md:337`), so an unattended run could have COM-hung.

Not mine to decide: whether `#1359`/`#29874`'s registers move into 1.2 with their nodes (the decided mechanism,
and the one `add_shift_reg` + `wire_sr` already serves), and whether `wire_sr`'s `LeftOutNode` can reach the
initialisers on `Diagram#686`, which `docs/diagram-hierarchy.md:95-97` measures as a FlatSequenceFrame diagram
rather than the top level (B1.3's honest limit).

FIXED: refuted-already - `tools/recipes/build_d1_routeb_v0.py`:196 - SR_QUEUE_AUTHORISED and
TEMP_SINK_AUTHORISED are both False and the docstring's RUN 3 block records the four confirmed refutations, so
the queue path cannot fire until judgement re-decides it.

FIXED: settled-already - `docs/d1-route-b-plan.md`:429 - a new section 11 records the mechanism this project
already decided for a loop-carried register (frame-loop-wire-graph.md:397 and d1-build-plan.md:446, where #376
moves WITH its two registers) and states the open question as the register's destination, not a transport.

FIXED: contradicted - `docs/d1-route-b-plan.md`:418 - section 11 records, with the machine measurement behind
it, that the only candidate type source is unnamed and that its wire's source is a LoopTunnel rather than a
node, so queue_node('obtain', ...) could never have been typed for these rows.

FIXED: unread-evidence - `docs/d1-route-b-plan.md`:422 - the index_mode 1 fact that d1_rewire_sources.json
carried and no plan had read is now stated, with the consequence that gate S3d covers six other tunnels and
these two have no index-mode gate at all.

FIXED: already-built - `docs/d1-route-b-plan.md`:431 - section 11 names OpAddShiftReg_v0 (Loop.Add Shift
Register 6361000) as the existing mechanism and records the honest limit that wire_sr's LeftOutNode variant
reaches a top-level node while the two initialisers sit on a FlatSequenceFrame diagram.

FIXED: helper-exists - `docs/d1-route-b-plan.md`:451 - section 11a records that a branched net is ONE Wire
object, so deleting the disposable SINK NODE plus Remove Bad Wires keeps the branch; the delete step needed no
new measurement and the recipe already deletes the node, not the wire.

FIXED: already-measured - `docs/d1-route-b-plan.md`:407 - the register geometry table in section 11 carries the
values from frame-loop-wire-graph.md and d1_rewire_sources.json, confirmed once on the machine, so no future
session re-measures them.
