# priorart-opgeterrors-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** fact
- **cost:** 
- **date:** 2026-09-17 16:48:28
- **outcome:** ANSWERED (216s)
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
## 10. `OpGetErrors_v0` — the third attempt at `VI.Get Errors` 452, and WHAT IS DIFFERENT NOW

Authorised by the judgement session (brief, 2026-09-17, decision 3) as the reader for "why is this VI
`ExecState 0`", which OPEN 39 names as the missing instrument. **Budget: 2 attempts.** This section exists to be
attacked by the prior-art review before a line is built — the two previous attempts are recorded FAILURES and
CLAUDE.md's "when a diagnosis is GUESSED twice, build the reader" is not a licence to rebuild the same thing the
same way.

### 10a. What FAILED, twice, and exactly how — read from our own files, not remembered

| attempt | record | symptom |
|---|---|---|
| 2026-09-09 | `docs/toolkit-capabilities.md:259` | "Invoke node created with only reference/error terminals, with and without the private ini tokens" |
| 2026-09-14 | `docs/toolkit-capabilities.md:157` | same signature: "node created with only `reference out` / `error out` — **no `Errors`, no `Details`**" |

The recipe from those attempts is still on disk: `tools/recipes/build_opgeterrors.py` (107 lines). It calls
`g.build_invoke(OP, "VI Server:VI", "452", …)` at line 34 and then *probes for output terminals by creating
indicators on terminal indices 0–7* (lines 49–59), i.e. it infers attachment from what a later walker can see.

### 10b. The four things that are different, each with its citation

1. **THE CREATOR'S ERROR IS NOW A RAISE — but only on the PROPERTY path.** `OpBuildPN_v1` exposes the creator's
   real `error out` (pane index 15; index 10 with the same name is a sink) and `build_property()` **raises** on it
   (`tools/gscript.py:2150-2163`). `build_invoke()` does NOT: it drives `OpBuildInvoke_v0.vi`, whose "`error out`
   indicator is now unwired, so read creator errors from the dialog watchdog" (`tools/gscript.py:2094-2123`).
   ⇒ **The first build is `OpBuildInvoke_v1`, not `OpGetErrors_v0`.** `docs/toolkit-capabilities.md:247-249` says
   this in as many words: *"an `OpBuildInvoke_v1` with the same exposure is needed for the Invoke case"*. Without
   it a third attempt would produce the same uninterpretable result as the first two, which is the definition of
   `repeated-failure-class`.
2. **"No error" is NOT a verdict that a member attached** (`docs/toolkit-capabilities.md`, prior-art A3-iv,
   2026-09-16): `Control.Value` 633200D — a *valid* ID on the wrong class — created a node with no `Value`
   terminal and **no error at all**. The robust check is the **data-terminal-name census** on the created node
   (`tools/recipes/build_opcaseframes_v0.py:49-58`: exactly one data SOURCE terminal, its name printed, never
   guessed). So the acceptance here is: after creating the 452 Invoke, enumerate the node's terminals and print
   their NAMES; `Errors` / `Details` present = attached, `reference out` / `error out` only = refused.
3. **The three probes that "proved" private members unreachable were VOID, and the reason is known**:
   `net_map` / `OpNetInfo_v1` "does not see nodes created by another op in the same session"
   (`docs/toolkit-capabilities.md`, RESOLVED 2026-09-14, `tools/bench/probe_stale_nodes.log`). The old
   `build_opgeterrors.py` verifies exactly through that broken route. ⇒ read terminals with `node_terms()` on a
   re-read report, not with the walker, and carry a **CONTROL** (a known-good public method, `Terminal.Create
   Indicator` 6349C02) through the identical code path in the same run — the discipline
   `docs/toolkit-capabilities.md` imposed after probe run 1 concluded a limitation from a broken reader.
4. **The COM poison guard is in** (STATUS OPEN 34, `…-d1-route-b-1.md` §2, 11/0), so a refused creator call no
   longer leaves the client in a state where every later read lies.

### 10c. The order, and the two stopping rules

1. `OpBuildInvoke_v1` = `OpBuildInvoke_v0` + the creator's real `error out` and `Outputs` surfaced, built by the
   same additive-on-a-proven-front-half pattern as `tools/recipes/build_oploopendref_v0.py`. Gate: the control
   (`Terminal.Create Indicator` 6349C02) attaches and its terminal names print; a deliberately bogus ID `FFFFFFF`
   raises 1077.
2. `OpGetErrors_v0`: create the 452 Invoke on `VI Server:VI` through v1. **If the creator raises, the answer is
   "the ordinary setter refuses a private member" and the next step is `Invoke.Set Method (Allow Private)`
   6370003 with `ID String = "Get Errors"` and `Allow Alternate Names? = TRUE`** (`toolkit-capabilities.md`, the
   three points from `archive/peer/2026-09-14-private-method-attach.md`: set the CLASS first, the setter takes an
   ID *String*, no special VI-reference option is needed). If THAT refuses, the recorded fallback is
   `Create from Reference` from a donor — **not attempted this session; it needs a donor VI that contains the
   node, and none is known to exist in this project.**
3. **Functional test before any use**: a scratch VI deliberately broken in two independent ways — one unwired
   REQUIRED input on a subVI call, and one type-mismatched wire — and the op must NAME the broken object's uid
   and print the error text. A `Get Errors` that returns an empty list on a VI whose `ExecState` is 0 is a FAILED
   op, not a clean VI.
4. **Budget 2.** Two failed builds ⇒ stop, write both logs' failure lines, hand back. Nothing in route B's
   build order depends on this op existing.

### 10d. What this op does NOT decide

It reports; it repairs nothing. The route-B run may use its output to name what is broken, and only rows the op
NAMES may be fixed — the budget-2 rule in the brief exists so that "ExecState 0" never again becomes a licence to
guess at 63 wires.


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
  status: released
  owner:
  since:
  purpose:
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

### A1 — Not settled

The technical question remains open: “`VI.Get Errors` 452 is still the missing instrument,” and the existing bare-input counts “discriminated nothing.” The judgement session authorized an experiment; it did not answer whether method 452 can be attached successfully. [STATUS.md:89](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:89>) [docs/d1-route-b-plan.md:403](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-route-b-plan.md:403>)

### A2 — Refuted already, but conditionally

On 2026-09-15 the outcome review explicitly put the reader among work to skip and said to abandon “`VI.Get Errors` … unless the delivery actually fails without them”; it classified the project as `tooling-over-delivery`. [archive/peer/2026-09-15-outcome-review-20260915.md:151](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-outcome-review-20260915.md:151>) [archive/peer/2026-09-15-outcome-review-20260915.md:218](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-outcome-review-20260915.md:218>)

That refutation does not plainly cover the current case: its stated exception may now apply because route B remains unsaved at `ExecState 0` after its two-run budget. [STATUS.md:83](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:83>) [STATUS.md:87](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:87>)

### A3 — Contradicted

1. The plan says `net_map` cannot see nodes created by another op and that the old recipe verified “exactly through that broken route.” [docs/d1-route-b-plan.md:438](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-route-b-plan.md:438>)

   The implementation record says the opposite: fresh nodes were hidden by the walker’s own junk, and “the earlier ‘stale reference’ reading … was wrong.” [tools/gscript.py:2452](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:2452>) [tools/gscript.py:2457](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:2457>) Toolkit documentation also labels that reasoning “SUPERSEDED” and attributes it to walker junk. [docs/toolkit-capabilities.md:144](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/toolkit-capabilities.md:144>)

   Moreover, the old recipe did not use `net_map` for its terminal verdict; it created indicators on terminal indices and inspected their labels/wires. [tools/recipes/build_opgeterrors.py:49](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opgeterrors.py:49>)

2. `docs/violation-decisions.md` says the cycle-9 retrospective found that the missing tool was “NOT a LabVIEW reader” and that `VI.Get Errors` would have been tooling drift. [docs/violation-decisions.md:71](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/violation-decisions.md:71>)

   The cited retrospective actually says, “The primary one was `VI.Get Errors`,” lists the failed states it would have explained, and says its prior build failures did not justify continued inference. [archive/peer/2026-09-15-retrospective-cycle9.md:91](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-retrospective-cycle9.md:91>) [archive/peer/2026-09-15-retrospective-cycle9.md:95](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-retrospective-cycle9.md:95>) [archive/peer/2026-09-15-retrospective-cycle9.md:101](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/archive/peer/2026-09-15-retrospective-cycle9.md:101>)

### A4 — Unread evidence

The obvious missed evidence is the correction embedded in `tools/gscript.py`: it withdraws the stale-node explanation that §10b.3 treats as established. [tools/gscript.py:2452](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:2452>) [tools/gscript.py:2457](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/gscript.py:2457>)

## Part B — The artifact

### B1 — Not already built successfully

A matching recipe exists, but it never produced a saved working `OpGetErrors_v0`: both runs ended `STOP: not saved`. [tools/recipes/build_opgeterrors.py:1](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/recipes/build_opgeterrors.py:1>) [tools/bench/build_opgeterrors.log:7](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opgeterrors.log:7>) [tools/bench/build_opgeterrors.log:16](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opgeterrors.log:16>)

### B2 — Already failed

The exact old build failed on 2026-09-09 and 2026-09-14. Both runs produced only `reference out` and `error out 2`, remained `ExecState 0`, and exited `rc=5` without saving. [tools/bench/build_opgeterrors.log:1](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opgeterrors.log:1>) [tools/bench/build_opgeterrors.log:10](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/tools/bench/build_opgeterrors.log:10>)

The new plan does address the repeated implementation: it first proposes `OpBuildInvoke_v1` with the creator’s real error and outputs exposed, then requires named-terminal census rather than accepting node creation. [docs/d1-route-b-plan.md:426](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-route-b-plan.md:426>) [docs/d1-route-b-plan.md:448](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-route-b-plan.md:448>) The historical failure still applies as prior art, but it does not establish that this revised path will fail.

### B3 — No helper-exists finding

`node_terms()` already supplies the required terminal-name census, and the plan explicitly uses it rather than reimplementing it. [docs/toolkit-capabilities.md:23](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/toolkit-capabilities.md:23>) [docs/d1-route-b-plan.md:439](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/docs/d1-route-b-plan.md:439>)

### B4 — Not already measured

The current broken-VI cause remains unmeasured; the two existing input censuses explicitly produced no verdict. [STATUS.md:89](<G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop/STATUS.md:89>)

PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: already-failed

## Sources

(extract from answer)

## What was done with it

**THE BUILD WAS STOPPED — see the full disposition in the opus arm of the same `-Dual` dispatch,
`archive/peer/2026-09-17-priorart-opgeterrors-opus.md`.** Both arms independently reached the same stop, and the
citation each rests on (`docs/d1-build-plan.md:859-860`, "No diagnostic, framework, or review cycle before
F1/F2") was opened and found to cover this case exactly, so the override was not available.

Recorded here because it is this arm's own finding and is worth keeping separately: B2/B3/B4 are NOT stops —
codex agrees the revised path addresses the repeated implementation (`OpBuildInvoke_v1` first, then a
named-terminal census rather than "the node was created"), that `node_terms()` is already the right helper and
is used rather than reimplemented, and that the current broken-VI cause **remains unmeasured**. So the
historical failure is prior art, not a prediction. The stop is about ORDERING, not about the design.

FIXED: already-failed - `docs/d1-route-b-plan.md`:401 - §10 retained and marked NOT AUTHORISED rather than
built; the two recorded 2026-09-09/14 failures are cited in it with what each actually showed.
