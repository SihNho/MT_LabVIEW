# priorart-routeb-run3-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17 17:33:26
- **outcome:** ANSWERED (332s)
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

## Part A — The direction

### A1 — Not settled exactly

No file decides the exact transport of `#1359` t1 and `#29874` t3. The general queue-only direction and paired-queue pattern are older, but applying them to these two shift-register reads is new.

### A2 — Refuted already, fallback only

The proposed bare-`Equal?` fallback is contrary to the recorded contract of `OpCreateEqual_v0`:

- The op is specified to receive both `x` and `y` as terminal references obtained from named outputs; its only functional test supplied both operands. [docs/toolkit-capabilities.md:52](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/toolkit-capabilities.md:52>) [tools/recipes/build_opsentinel_ops.py:78](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opsentinel_ops.py:78>) [tools/recipes/build_opsentinel_ops.py:96](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opsentinel_ops.py:96>)
- The earlier creator failure record says invalid terminal-refnum inputs caused error 1055 and a modal; the review explicitly required real internal terminal references. [docs/NAMES.md:468](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/NAMES.md:468>) [docs/NAMES.md:473](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/NAMES.md:473>) [archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md:277](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md:277>)
- Run 3 instead passes an empty name list, producing empty `Names` and `Names 2`. [tools/recipes/build_d1_routeb_v0.py:739](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:739>) [tools/recipes/build_d1_routeb_v0.py:746](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:746>) [tools/recipes/build_opsentinel_ops.py:397](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opsentinel_ops.py:397>)

Scope: this refutes only the no-source bare-`Equal?` fallback, not branching an already-existing `Z/dZ` wire.

### A3 — Contradicted

The diagnostic’s required named type sources are already recorded as unnamed:

- Right register 8 is written by `#1359` t2, whose terminal name is blank; right register 12 is written by `#29874` t5, also blank. [docs/frame-loop-wire-graph.md:417](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:417>) [docs/frame-loop-wire-graph.md:421](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:421>)
- `diag_sr_transport.py` accepts that writer only when `term_name` is truthy. [tools/bench/diag_sr_transport.py:145](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/diag_sr_transport.py:145>) [tools/bench/diag_sr_transport.py:160](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/diag_sr_transport.py:160>)
- `sr_queue` then refuses the row when that name is absent. [tools/recipes/build_d1_routeb_v0.py:793](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:793>)

The claimed same-type measurement is also not implemented: P3 checks only that a named source exists; it reads no datatype. [tools/bench/diag_sr_transport.py:134](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/diag_sr_transport.py:134>) [tools/bench/diag_sr_transport.py:160](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/diag_sr_transport.py:160>)

Finally, the plan says every address is reread live, but `sr_queue` directly reuses the cached `(class, Traverse index)` from `sr_transport.json`. [tools/bench/plan_routeb_run3.md:41](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/plan_routeb_run3.md:41>) [tools/recipes/build_d1_routeb_v0.py:791](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:791>) [tools/recipes/build_d1_routeb_v0.py:803](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_d1_routeb_v0.py:803>)

### A4 — Unread evidence

Two obvious precedents were missed:

- The measured shift-register table already supplies both register indices, writers, left-side wires, readers, and the fact that the writer outputs are unnamed. [docs/frame-loop-wire-graph.md:403](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:403>) [docs/frame-loop-wire-graph.md:426](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:426>)
- The GPU-kernel builder already documents the temporary-sink → branch → delete-temporary topology. [archive/bench-2026-09-09-gpu-dropin-kernel/REPORT.md:68](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/bench-2026-09-09-gpu-dropin-kernel/REPORT.md:68>) [tools/recipes/build_gpu_kernel.py:151](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:151>)

## Part B — The artifacts

### B1 — Already built

Two component shapes already exist:

1. The paired producer/consumer queue topology exists with six lock-stepped queues, error-chained paired publication, FIFO alignment gates, and the 162/162 replay result. [docs/stage2-assembly-step-c.md:21](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-c.md:21>) [docs/stage2-assembly-step-c.md:39](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/stage2-assembly-step-c.md:39>) [docs/d1-build-plan.md:160](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-build-plan.md:160>)

   Scope: this does not mean `Q_sr1/Q_sr2` themselves exist; only their claimed queue topology does.

2. Temporary sink → branch permanent sink → delete temporary → Remove Bad Wires was already implemented for the GPU-kernel outputs. The recipe explicitly says the permanent branch survives deletion and gates `ExecState == 1` before saving. [tools/recipes/build_gpu_kernel.py:151](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:151>) [tools/recipes/build_gpu_kernel.py:172](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:172>) [tools/recipes/build_gpu_kernel.py:177](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/bench-2026-09-09-gpu-dropin-kernel/build_gpu_kernel.py:177>)

### B2 — No exact prior failure found

I found no record of an attempted `Q_sr1/Q_sr2` build or this exact `Z/dZ → #2222 t0` build. The bare-`Equal?` issue above is a prior rejected mechanism, not an exact run of this artifact.

### B3 — No missing helper finding

The implementation already uses the relevant existing calls: `queue_node`, `shift_reg_left`, `OpConnectFromWire_v0`, indexed nested wiring, `delete_object`, and `remove_bad_wires_scripted`. The recorded alternative for removing only one sink is `Wire.Disconnect Terminal 6370C0D`, but deletion of a disposable sink node followed by Remove Bad Wires is also expressly recorded as valid. [docs/NAMES.md:896](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/NAMES.md:896>) [archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:28](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-opwiresource-fail3-branch-wire-is-one-object.md:28>)

### B4 — Already measured

Most of `diag_sr_transport.py` duplicates existing measurements:

- Left registers `#9025` and `#29512`, indices 8 and 12, and inside wires `9097` and `28039` were already measured on 2026-09-14. [tools/bench/test_opshiftregs_v1.log:10](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/test_opshiftregs_v1.log:10>) [tools/bench/test_opshiftregs_v1.log:14](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/test_opshiftregs_v1.log:14>)
- Their exact writers and readers are already tabulated. [docs/frame-loop-wire-graph.md:417](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:417>) [docs/frame-loop-wire-graph.md:440](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:440>) [docs/frame-loop-wire-graph.md:444](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/frame-loop-wire-graph.md:444>)
- `Z/dZ` is already recorded as control UID 47, source of wire 730. [tools/bench/main_vi_panel_wiring.json:185](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/main_vi_panel_wiring.json:185>)
- `#2222` t0 is already recorded as an unnamed sink on that same wire, with the route classified `from-ctl`. [tools/bench/d1_rewire_sources.json:913](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/d1_rewire_sources.json:913>) [tools/bench/main_vi_nodeterms.json:11998](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/main_vi_nodeterms.json:11998>)

The genuinely unmeasured item is datatype identity/coercion—but the new diagnostic does not measure it.

PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: already-measured

## Sources

(extract from answer)

## What was done with it

**THE BUILD WAS STOPPED BEFORE IT RAN — full disposition in the opus arm of the same `-Dual` dispatch,
`archive/peer/2026-09-17-priorart-routeb-run3-opus.md`.** `SR_QUEUE_AUTHORISED` and `TEMP_SINK_AUTHORISED` are
both `False` in `tools/recipes/build_d1_routeb_v0.py`; the recipe was not executed.

Kept here because they are this arm's own contributions and the two arms differ:

1. **A1 is DIFFERENT from opus's A1, and I record the disagreement rather than picking a winner.** This arm says
   "not settled exactly — no file decides the exact transport of these two rows"; opus says the shape is
   `#376`'s and was decided as "the register goes with the node" (`docs/d1-build-plan.md:446`,
   `docs/frame-loop-wire-graph.md:397`). Both are cited and neither is wrong about its own citation: nothing
   names *these two rows*, and a general rule for this *shape* does exist. That is a judgement question and it
   is in the hand-back.
2. **A2's scope line is the one that saved decision (2) from being thrown away with decision (1):** *"this
   refutes only the no-source bare-`Equal?` fallback, not branching an already-existing `Z/dZ` wire."* So the
   measured half of decision (2) stays armed and only the unmeasured half is disarmed.
3. **A3's second half is a defect in my diagnostic that opus did not name:** P3 *"checks only that a named
   source exists; it reads no datatype"*, while the plan claimed it would establish the queue carries the
   register's type. It cannot — `docs/stage2-assembly-step-b.md:53` says the fleet cannot read type descriptors
   and the gate must be FUNCTIONAL. P3's expectation was therefore INVERTED before the run (it now asserts the
   writers are UNNAMED, which is what the documents state) and the type claim was removed from the plan.

FIXED: contradicted - `tools/bench/diag_sr_transport.py`:160 - P3 no longer claims a type measurement it cannot
make; it predicts, and then confirms on the machine, that the partner-right writers are unnamed.
