# priorart-opgeterrors-opus

- **agent:** claude
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** fact
- **cost:** $3.9164  in 36 / out 32006 / cache-create 194024 / cache-read 2213998  (448s, 33 turn(s))
- **date:** 2026-09-17 16:56:00
- **outcome:** ANSWERED (452s)
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

## Bottom line

**Not `novel` — eleven findings, and two of them are hard stops that codex's 16:48 review did not reach.** One correction to my opening line first: I said §10b.1's premise was contradicted by the code. It is not. `tools/gscript.py:2094-2123` confirms §10b.1 exactly — `build_invoke()` swallows the modal-dialog error and its docstring says *"the op's `error out` indicator is now unwired, so read creator errors from the dialog watchdog, not from `_err()`"* — while `build_property()` at `tools/gscript.py:2156-2158` raises on `error out 2`. **§10b.1 is the one pillar of §10b that survives this review intact.**

Also timely: `STATUS.md:31-34` now reads `status: acquired`, owner `material/cycle15-route-B-3-save-it`, purpose *"…OPEN 39 OpGetErrors_v0"*. This build is in flight as I write.

---

# PART A — the direction

## A1 · SETTLED-ALREADY — a judgement decision from *today* forbids exactly this class of work before F1/F2

`docs/d1-build-plan.md:859-860`, under the heading §11j *"DECIDED (judgement, 2026-09-17, after the sentinel-ops wall and the THIRD consecutive outcome violation)"*:

> **2. No diagnostic, framework, or review cycle before F1/F2** — the outcome reviewer's own ordering, adopted: third op → PHASE "full" → save → N1 → F1 (5 min) → F2.

`OpGetErrors_v0` is a diagnostic. The precondition still holds: `STATUS.md:87-88` says *"ExecState is 0 warm and **nothing was saved** — `Track_v6_D1_GPU.vi` does not exist."* F1/F2 have not run. §10 does not cite §11j.2 and does not argue it is superseded.

## A2 · REFUTED-ALREADY — the outcome review named this reader specifically, and the repeat escalates it

`archive/peer/2026-09-15-outcome-review-20260915.md:146,151`:

> "A competent engineer pursuing the stated outcome would have skipped or deferred: … **The currently planned `VI.Get Errors` reader** and `OpCaseFrames_v0` structural confirmation."

That objection is *stronger* now, not weaker. `STATUS.md:71-72`: *"**32 outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive time ⇒ the work stops for a re-plan with the USER.** Not answerable by a device."* And `CLAUDE.md:419`: an `OUTCOME-VIOLATION` *"is NOT answered by building a device."*

**Does it still apply — honestly?** There is exactly one precedent for overriding it, and it matters: `docs/cycle10-plan.md:28-29` records the same fork — build the reader, or honour *"further readers are tooling drift"* — and resolves it *"The user chose the reader."* So this is overridable. **By the user.** A material or judgement session authorising it internally is the move the rule exists to block.

## A3 · CONTRADICTED — five, one of them inside §10's own file

**(i) The same document refuses this build 17 lines above §10.** `docs/d1-route-b-plan.md:384-386`:

> **5. No fifth op is authorised by this plan.** B uses the four the freeze lift closed at … R1's resolution may need one; that is the judgement session's call, not this file's.

§10 (`docs/d1-route-b-plan.md:401`) authorises **two** new ops. The carve-out is for **one** op, scoped to **R1's resolution** — the cross-loop transport question, `STATUS.md:85-87` (OPEN 38). `OpGetErrors_v0` is OPEN 39 (`STATUS.md:89`), a different item. The carve-out does not cover it. This is precisely the failure mode the brief names: a section contradicting its own file.

**(ii) §10b.3 misdescribes the old recipe — and this voids the pillar.** §10b.3 asserts *"The old `build_opgeterrors.py` verifies exactly through that broken route [`net_map`]."* It does not. `tools/recipes/build_opgeterrors.py:49-59` probes terminals with `g.create_indicator()` + `g.fp_labels()`; `net_map` appears nowhere in the file. `tools/bench/build_opgeterrors.log:5-7` and `:14-16` show it printing terminal **names** directly:

```
   t1: indicator 'reference out'
   t3: indicator 'error out 2'
assembled: ExecState 0 outputs ['reference out', 'error out 2']
```

So "the walker was broken" does **not** explain the two prior failures. That negative result stands unexplained, and §10b.3 — one of four pillars — collapses.

**(iii) The two files disagree about why `net_map` failed, and the plan quotes the retracted one.** `docs/toolkit-capabilities.md:225-228` says `net_map` *"does not see nodes created by another op in the same session."* `tools/gscript.py:2451-2457` says the opposite and retracts it: *"(a) why fresh nodes were 'invisible': they sat in `Nodes[]` behind the walker's OWN junk … **The earlier 'stale reference' reading recorded in STATUS was wrong**"* — and that `net_map` was then fixed (*"snapshot Invoke uids first, purge what the walk added"*). The plan cites the doc. Two consequences: wrong cause, and the "broken route" is no longer broken.

**(iv) The archive carries a FALSE success record for this exact op.** `archive/peer/2026-09-09-clfn-scripted-node-broken-with-arguments.md:195`:

> "the private VI method Get Errors (0x452) enabled via LabVIEW.ini tokens … and **built as OpGetErrors_v0 to read the real error text. Results in `tools/bench/diag_chain.log` and `docs/gpu-backend.md`.**"

`tools/bench/diag_chain.log` exists and contains **no** match for `Get Errors`, `Errors`, `Details` or `error text`; `docs/gpu-backend.md` contains no match for `Get Errors`, `OpGetErrors` or `0x452`. Against it, `archive/STATUS-2026-09-14-full-before-condense.md:575`: *"OpGetErrors_v0 NOT achieved: VI method 0x452 yields no outputs through the erdosmiller creator even with the three private-scripting [tokens]."* Flagging this because a future session reading only line 195 will believe the op exists and works.

**(v)** `docs/violation-decisions.md:71-73` reports the cycle-9 retrospective as finding the missing tool was *"NOT a LabVIEW reader — building `VI.Get Errors` 'would have been more tooling drift'"*. The retrospective says the reverse: `archive/peer/2026-09-15-retrospective-cycle9.md:95` *"The primary one was **`VI.Get Errors`**"*, and `:101` *"its absence did not justify continuing to classify `ExecState 0` by inference."* (Codex found this one; I confirm it independently.)

## A4 · UNREAD-EVIDENCE — the file that gave you `452` offers two other routes on the same page

`archive/peer/2026-09-08-vi-error-list-by-script.md` is the origin of the ID §10 is built on. §10's ladder (452 → 6370003 → donor) never mentions either of these, both on that page:

- **`:115-141`** — `Application.Error Window:Open` **0x89D** + `VI.Refresh Error Window Entry` **0x473** (both private), with the sequence spelled out: refresh the VI's entry, open the Error Window, capture it. This answers "why is this VI `ExecState 0`" **without attaching any member to a node's output terminals** — the exact thing that failed twice — and this project already owns the capture tool (`tools/lv_gui.ps1`).
- **`:53-62`** — `Wire.Get Error List` **0x6370C0A** (private, required output `Error List`), also recorded as unbuilt at `docs/NAMES.md:898-899`. Route B's failure is about **63 wires**; per-wire errors fit the actual question better than a whole-VI list.

---

# PART B — the artifact

## B1 / B3 · HELPER-EXISTS — §10c.2's "next step" is already written and already run

§10c.2 presents `Invoke.Set Method (Allow Private)` **6370003** as new work, citing only the peer archive. It exists as runnable code: `tools/recipes/probe_allow_private3.py:112` calls `g.build_invoke(S, "VI Server:Invoke", "6370003", …)`, with a known-good control at `:105` and a three-branch verdict at `:120-134`. Its result, `tools/bench/probe_allow_private3.log:10-13`:

```
== Invoke.Set Method (Allow Private)
   class=VI Server:Invoke id=6370003
   objects created by ONE call: 1
   of those, 0 were readable; 0 carry method-specific terminals
```

Note the run's own docstring premise (a ~67-node spray) did **not** reproduce — one object. Verdict was `STILL INCONCLUSIVE` (`:25-26`), so this does not refute the branch — but it does mean the code is written, the discipline is in place, and re-running it under the fixed `net_map`/`node_terms()` is minutes, not a build.

Separately: `node_terms()` (`tools/gscript.py:816-824`) is the clean reader the plan correctly names — *"0 junk per call - the reason to prefer this over `net_map` for one node."* It has existed since 2026-09-14. That further undercuts §10b.3's "the reader was broken" story.

## B2 · ALREADY-FAILED — twice, with identical output, both unsaved

`tools/bench/build_opgeterrors.log:1-18` — 2026-09-09 12:45 (`rc=5`, 152 s) and 2026-09-14 01:34 (`rc=5`, 151 s), both ending `assembled: ExecState 0 outputs ['reference out', 'error out 2']` / `STOP: not saved`. The new plan addresses **one** named cause (the creator's swallowed error — legitimately, per §10b.1). Pillars 2, 3 and 4 do not survive A3 above.

## B4 · ALREADY-MEASURED — §10b.2's acceptance test has already been run twice and returned "refused"

§10b.2 proposes: *"after creating the 452 Invoke, enumerate the node's terminals and print their NAMES; `Errors`/`Details` present = attached, `reference out`/`error out` only = refused."* That is what `tools/bench/build_opgeterrors.log:5-7,14-16` already records, over terminal indices 0–7, twice: only `reference out` and `error out 2`.

The expected names are externally confirmed, so the census had a correct target: LabVIEW Wiki gives VI class `Get Errors`, **method ID 452, scope Private**, parameters **`Errors` (String Array, required)**, **`Details` (String Array, required)**, `Call Dangerously?` (Boolean, optional).

---

# One external fact that changes §10c.2's dead end

§10c.2's terminal branch: *"the recorded fallback is `Create from Reference` from a donor — **not attempted this session; it needs a donor VI that contains the node, and none is known to exist in this project.**"*

Contradicted in our own files — `docs/toolkit-capabilities.md:187-189` calls it *"a **real route, not a GUI one**"* — and contradicted externally. The NI thread on this exact method offers a **code snippet**: *"You can just drag the snippet onto a block diagram"*, as an alternative to the INI tokens. A LabVIEW snippet is a PNG carrying the diagram code, so **the donor is manufacturable, not merely findable**. And NI's own Idea Exchange entry confirms there is no public accessor at all, which raises the donor branch's value rather than lowering it. This is the "absence in what you happen to be looking at is not evidence of absence" error `CLAUDE.md` warns about.

# What this evidence does NOT settle

- **Whether 452 can attach through the ordinary setter is still unknown.** Both prior runs used a creator that swallows its own error (`tools/gscript.py:2102-2103`), so "silently refused" versus "1077" is genuinely undetermined. §10b.1 is right about this, and `OpBuildInvoke_v1` is the correct instrument to find out.
- **Whether `net_map`'s purge fix would have changed the 2026-09-14 result cannot be told from these logs** — and it does not matter, because that run never called `net_map` (A3-ii).
- **Nothing here says the reader is worthless.** The cycle-9 retrospective (`:95-101`) argues it is the primary missing tool. The dispute is about *ordering and authority*, not value — and `docs/cycle10-plan.md:28-29` shows who settles that.

---

```
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: helper-exists
PRIOR-ART: already-failed
PRIOR-ART: already-measured
```

**Sources:**
- [LabVIEW Wiki — VI class / Get Errors method](https://labviewwiki.org/wiki/VI_class/Get_Errors_method)
- [NI Community — how to programmatically check the error messages of a broken vi using labview scripting](https://forums.ni.com/t5/LabVIEW/how-to-programmatically-check-the-error-messages-of-a-broken-vi/td-p/3336258)
- [NI Community — Error list in VI scripting](https://forums.ni.com/t5/LabVIEW/Error-list-in-VI-scripting/td-p/2263216)
- [NI Idea Exchange — Programmatically access "Error List"](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Programmatically-access-Error-List/idi-p/2015364)

## Sources

(extract from answer)

## What was done with it

**THE BUILD WAS STOPPED. `OpGetErrors_v0` was NOT built this session, and no line of it was written.**

Both arms of the `-Dual` dispatch reached the same hard stop independently (codex: `refuted-already`,
`already-failed`; opus: `settled-already`, `refuted-already`, 5 × `contradicted`, `helper-exists`,
`already-measured`). The prior-art review's verdict power is the design (memory
`prior_art_review_is_the_fourth_peer`: *"it actually stops the work"*), and the only override is to open the
cited file and show in writing that it does not cover this case. I opened it. **It covers this case exactly:**

> `docs/d1-build-plan.md:859-860`, under *"DECIDED (judgement, 2026-09-17, after the sentinel-ops wall and the
> THIRD consecutive outcome violation)"*: **"2. No diagnostic, framework, or review cycle before F1/F2 — the
> outcome reviewer's own ordering, adopted: third op → PHASE "full" → save → N1 → F1 (5 min) → F2."**

`OpGetErrors_v0` is a diagnostic; `Track_v6_D1_GPU.vi` is not saved and F1/F2 have never run. The citation is
not refutable, so the override is not available to me. Reinforced by `archive/peer/2026-09-15-outcome-review-
20260915.md:146,151`, which names *"the currently planned `VI.Get Errors` reader"* among the work a competent
engineer would have skipped, and by `STATUS.md` OPEN 32 + `CLAUDE.md:419` (an `OUTCOME-VIOLATION` is never
answered by building a device).

What the review does NOT say, and what the judgement session should weigh when it re-decides:
* **§10b.1 survived intact** (opus's own correction to its opening line): `tools/gscript.py:2094-2123` confirms
  `build_invoke()` swallows the creator's error while `build_property()` raises at `:2156-2158`. So "the two
  failures are uninterpretable because the creator's error was never read" is TRUE, and `OpBuildInvoke_v1`
  remains the right instrument if this is ever authorised.
* **The donor fallback is stronger than §10c.2 said.** I wrote that `Create from Reference` "needs a donor VI
  that contains the node, and none is known to exist". Contradicted by `docs/toolkit-capabilities.md:187-189`
  and by the NI thread's snippet: a LabVIEW snippet is a PNG carrying diagram code, so the donor is
  **manufacturable, not merely findable**. That is a `contradicted` finding against my own plan text and it
  stands whether or not the op is ever built.
* **Value was never the dispute** — the cycle-9 retrospective still calls this the primary missing tool. The
  dispute is ordering and authority.

`docs/d1-route-b-plan.md` §10 is left in place, marked as NOT AUTHORISED, so the next judgement session inherits
the plan rather than re-deriving it.

FIXED: refuted-already - `docs/d1-route-b-plan.md`:401 - §10 is retained but the build was not started; the
section now records that the prior-art review stopped it on d1-build-plan.md:859-860, which I opened and could
not refute.
