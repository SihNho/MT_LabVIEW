# priorart-priorart-cycle11-delete

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.3327  in 48 / out 30943 / cache-create 196706 / cache-read 3183702  (423s, 37 turn(s))
- **date:** 2026-09-16
- **outcome:** ANSWERED (427s)
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
---
type: plan
status: current
date: 2026-09-16
cycle: 11
tags: [plan, delete, opdelete, phase-a]
supersedes: []
---

# Cycle 11 ??repair DELETE, then finish Phase A

One arc, run end to end without stopping (CLAUDE.md rule 2c). Three stages, each with a prediction contract.

## Why this cycle exists

`delete_object()` removes nothing and the op cannot say why. MEASURED
(`tools/bench/diag_delete_error_control.log`): `OpDelete_v0`'s front-panel `error out` reads `(False, 0, '')` even
for inputs that **cannot** succeed (index 999999; an unknown class name), while both attempts raised *"run blocked
behind a modal dialog (dismissed by watchdog after ~9 s)"*. So the indicator is DEAD and the **dialog is the only
error signal there is** ??and `gscript.delete_object` was swallowing exactly that exception until it was fixed
today.

Every op VI this fleet builds is built by **trimming a donor**, so delete is upstream of all of Phase A.

### The reading this cycle is built on, stated so it can be refuted

`gscript.wire`'s own docstring says: *"Unwired error INPUTS are harmless ??only an unwired error OUT that receives
an error raises a dialog."* That sentence explains every observation at once:

- the `Generic.Delete` Invoke Node's `error out` terminal is **unwired**;
- the method returns an error, Automatic Error Handling pops a modal dialog, the watchdog dismisses it;
- the front-panel `error out` indicator is wired to something else (or nothing), so it never moves;
- `delete_object` caught `"modal dialog"` and returned as if the delete had worked.

**Falsifier:** if `create_indicator` on that terminal declines (meaning the terminal is already wired), this reading
is wrong and the cause is elsewhere ??the recipe stops and says so rather than guessing.

### A second defect found while reading, which constrains the method

`net_map()` purges the junk Invoke nodes it drops (spec 짠33) with
`delete_object(target, "Invoke", idx, verify=False)` inside `except Exception: pass`. **With delete broken, net_map
cannot clean up after itself** and leaves the walked VI carrying junk Invokes and (per its own comment) broken.
Therefore: **no `net_map` call anywhere in this cycle until delete is proven.** Topology is read with `node_info`,
`fp_labels` and `report_all`, none of which run a creator.

## Stage 1 ??`OpDelete_v1`: wire the Invoke Node's error out to a live indicator

Recipe: `tools/recipes/build_opdelete_v1.py`. Copy `OpDelete_v0.vi` ??`OpDelete_v1.vi` in `claudeDev` (rule 1: the
v0 file is not an original, but it is not modified either ??the copy is edited). No GUI.

Route, using helpers that already exist ??no new capability is invented:

1. `node_info()` ??the Invoke node's `Nodes[]` index and style.
2. `create_indicator(target, invoke_index, 3)` ??terminal 3 is `error out` on a
   `reference / reference out / error in / error out` Invoke Node. This both **tests** and **fixes**: a wired
   terminal yields no control (documented), so a new indicator appearing is proof the terminal was unwired.
3. `fp_labels()` diff ??the label LabVIEW gave it (expected `error out 2`). The label is the confirmation that
   terminal 3 really is `error out`; a different name means the index was wrong and the recipe stops.
4. `save()` the copy.

**PREDICTION CONTRACT**
- P1 `OpDelete_v0` holds exactly ONE Invoke node and no junk Invokes left behind by a past `net_map`.
- P2 `create_indicator` adds exactly one `ControlTerminal`, labelled `error out` + a suffix.
- P3 `ExecState == 1` after the edit and the save persists (re-read from a fresh reference).

## Stage 2 ??prove the new op, on controls first and then for real

Same runner, no separate turn.

**PREDICTION CONTRACT**
- P4 Control A (`Property`, index 999999) and control B (class `NoSuchClassXYZ`) drive the NEW indicator to a
  NON-ZERO status, and the run **returns without a modal dialog**. The dialog was the unwired error out; wiring it
  should remove it.
- P5 A real delete of one `Property` object on a scratch copy either
  (a) removes exactly one object with a clean error ??delete works and the regression was only ever the reporting;
  or (b) reports a specific error code, which is the first time this project has had the reason in hand.
  **Both outcomes are results.** P5 is a measurement, not a gate.
- P6 A no-op sanity check: the scratch VI's object census is unchanged by the two control cases.

Then `tools/gscript.py` is patched to drive `OpDelete_v1` and read the live indicator by name, and the
`verify=False` warning is updated to say what the indicator now reports.

## Stage 3 ??Phase A1, then A7's three audits

- **A1** (`tools/recipes/build_opownerchain_v0.py`) re-run with the ordering the B2/B3 review settled:
  **deletes first, then connects, and only ever into UNWIRED sinks** (`gscript.py:2084`, `vi-scripting.md:603`
  already said so; the recipe had wired four already-wired sinks), plus `#1044` typed as class `Node`, not `SubVI`.
  A1 has **one** of its two failures left.
- **A7's three audits**, in this order:
  1. the **reentrancy audit** ??`t0-instrumentation-plan.md:65-70` calls it *"the highest-value check in the whole
     plan"*, and there is already a confirmed instance nobody had connected: `ASI_adjust focus-subvi.vi` is
     **non-reentrant** and called from both loop 43 and loop 99 (`main-vi-panel-map.md:558`), i.e. an accidental
     mutex between the frame loop and the display loop ??directly against CLAUDE.md rule 1c;
  2. the **VISA call-site census** ??every VISA/serial node and which diagram owns it, the evidence base for
     rule 1c's "no serial on the frame path";
  3. the **UI-thread census**.

`OpOwnerChain_v0` also answers OPEN #1 (is the periodic auto-reset gated by `Auto-Reset`?), whose decision is
assembled outside diagram 43.

## What is NOT in this cycle

No hardware. No original VI is opened. No GUI action. No `net_map`. No new op beyond `OpDelete_v1`, which is a
repair of an existing one rather than a new capability.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-16
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.

## ?좑툘 ONE SESSION AT A TIME

Two Claude sessions ran concurrently on 2026-09-16 and both edited the active documents; the second session's copy
of `CLAUDE.md` was stale for its whole run. Before starting: check for another live session, and **re-read
`CLAUDE.md` and this file from disk** rather than trusting a summary.

## START HERE

1. **`docs/pre-rig-master-plan.md` is THE plan** (`docs/cycle10-plan.md` is superseded ??it is that plan's Phase A).
   Settled decisions that must not be re-opened: **`docs/decisions.md`**.
2. ??**Gate: prior-art layer OPEN, rev6 NOT bought.** All 13 rev5 findings accepted (none argued) and the plan
   corrected ??new rows 1.9 stop/shutdown, Phase A9, A10, two 2A rows, banners in `restructure-plan-4.6.md:42` and
   `rotor-scheduler-design.md:74-75`. `REFUTED:` lines + per-finding table: end of
   `archive/peer/2026-09-16-priorart-master-plan-rev5.md`. ?좑툘 Gate hole recorded, not fixed: `guard_cycle.py`
   advises "change the plan instead" but accepts only `REFUTED:` ??a `FIXED:` form is the obvious repair.
2b. ??**Cycle-10 retrospective done, 7 VIOLATIONs, all answered.** Six slugs are at 4 occurrences across cycles
   7쨌8쨌9쨌10. Answers: `docs/violation-decisions.md` ??Round 2 (2 devices, 4 reasoned no-devices). Both devices are
   **built and tested**: the undisposed-review dispatch gate in `guard_peer.py`, and `audit_cycle.py` C4/C5 review
   cost. `violations.py` now compares decision **timestamps** (user: ??꾩뒪?ы봽 鍮꾧탳濡?怨좎튇??. Headline the
   retrospective found: **six reviews, 48 min 40 s, $28.55 ??and the declared reader never launched.**
3. ?뵶 **A1 RAN for the first time and FAILED 3/5 gates ??the root cause is the DELETE TOOL, not A1?셲 design.**
   `delete_object` removes nothing, and the op **cannot tell us why**: `OpDelete_v0`?셲 `error out` is a **dead
   indicator** ??it reads a clean, empty error cluster even for inputs that cannot possibly succeed (measured,
   `tools/bench/diag_delete_error_control.log`). LabVIEW?셲 real signal is a **modal dialog**, and the wrapper
   contained `if "modal dialog" not in str(e): raise` ??it caught exactly that signal and carried on; with
   `verify=False` a refused delete became a reported success.
   ??**Fixed in `tools/gscript.py`**: swallow removed, `error out` now read, docstring warns about `verify=False`.
   ?좑툘 **Assume every `verify=False` delete since the regression did nothing** ??`net_map`?셲 purge calls it that
   way inside `except Exception: pass`, so **no caller anywhere had positive evidence that delete works**.
   Three peer reviews (B2/B3 wiring, delete no-op, uid 9775) are archived **and annotated**. The A1 fix itself is
   settled: **deletes first, then connects, only into UNWIRED sinks** (`gscript.py:2084` and `vi-scripting.md:603`
   already said so ??the recipe wired four already-wired sinks), and `#1044` is class `Node`, not `SubVI`.
   A1 has **1 of its 2 failures left**. Evidence and full narrative:
   `archive/2026-09-16-status-gate-a1-delete-regression.md`.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since: 2026-09-16 15:3x
  purpose:
```

**Verified, not assumed:** no LabVIEW process at 15:4x ??the last diagnostic's instance (pid 14352) did **not**
exit with its client and was killed explicitly. So the old note *"a COM-launched LabVIEW with no panel exits with
its client"* is **not reliable**: always `tasklist | grep -i labview` and kill a stray rather than trusting it or
this file. Fresh instances sit at ~31,500 handles; use a unique scratch VI name per run, and delete the scratch in
the same run that creates it.

## HARDWARE ??permission follows the RIG STATE. Current state: **遺꾪빐 / DISASSEMBLED ??everything allowed**

| rig state | motors (PI 쨌 rotor 쨌 magnet) | **ASI piezo** | camera |
|---|---|---|---|
| **遺꾪빐 ??disassembled ??WE ARE HERE** | ??| ??| ??|
| 議곕┰ ??assembled | ??| ??| ??|
| ?ㅽ뿕以???experiment running | ??| ??| ??|

?좑툘 **The ASI carve-out is RETIRED** (user, 2026-09-16; quote and table in CLAUDE.md rule 1b). Do not re-introduce
"the piezo is the one exception", and do not reinstate the 2026-08-27 motor ban, from any older summary. **Only the
user announces a state change**; never infer one, and do not ask per incident inside a declared state.

Instruments: rotor counter **0** (not the old 100,000 baseline ??the original VI's first absolute move would be a
200-turn trip) 쨌 magnet motor full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`. **A camera session open RESETS ROI *and* exposure**, so the acquisition loop must apply the
contract itself (`tools/bench/camera_contract.py` reads and verifies; it cannot pre-set a later run).

**No beads while disassembled**, so bead-dependent acceptance waits. Fixture work is unaffected (10,043 frames,
`archive/bench-2026-09-07-fixture/`, 13 real lost-bead frames).

## Where things stand

**Stage 1 (analysis) CLOSED** ??`docs/` holds `instrument-libraries`, `main-vi-subvi-identity` (98 call sites, 0
mismatches), `main-vi-panel-map`, `main-vi-state`, `main-vi-startup`, `frame-loop-wire-graph`,
`rotor-sign-diagnosis`. Raw data: `archive/benchmarks/INDEX.md` rows 22??1.

**Stage 2 (assembly) IN PROGRESS**, cycles 1?? done (`docs/stage2-plan.md`, `stage2-assembly-step-{a,a3,b,c,e}.md`).
`Track_v6_CPU_core_v0.vi` 69/69 PASS (INDEX row 40) 쨌 `Track_v6_CPU_queue_v0.vi` 162/162 PASS (row 41).
**Say it exactly:** both are bit-identical to the reference for the **first 10,018 frames ??those before the first
bead loss**, not all 10,043, and both are **replay** artefacts: recorded TIFFs, `FOR` loops, no live acquisition,
no stop protocol.

**THE GAP (outcome review, 2026-09-15):** 168 op VIs, 116 recipes, 217 peer exchanges produced two replay VIs and
**zero runnable experimental VIs**. *"The next problem is not missing tooling; it is failure to cross the boundary
from replay proof to experiment product."*

## OPEN

1. ?윞 **Is the PERIODIC auto-reset gated by `Auto-Reset`?** It decides whether an hours-long dry run terminates
   itself on `Limit of Program`. Measured 2026-09-16 (`tools/bench/diag_reset_arm.log`): the period **enters** the
   frame loop through `LoopTunnel` #10114 and the remainder **leaves** through `LoopTunnel` #10177 ??the decision is
   assembled **outside diagram 43**, so it needs A1's owner chain. The lost-bead arm *is* gated, by `And` #9647.
2. ?윟 **Autofocus decision path ??closed.** `CaseStructure #10407` fires on `(frame counter mod 25) == 0 AND
   NOT(Fix to a Certain Pattern)` ??**every 25 frames ??3.6 Hz at 90 Hz** ??and transacts serial when it fires.
   But `Fix to a Certain Pattern` is **written by code every iteration** (Property Node #1469) from
   `NOT( Auto-Focus AND NOT(reseed-And 9921) AND (counter < Limit of Auto-Focus) )`, so **the switch that stops the
   piezo is `Auto-Focus` (uid 24266)**, exactly as the user said. Derivation: `docs/camera-acquisition-facts.md`.
2c. ?윟 **uid 9775 READS the camera geometry ??and the size the VI WRITES is the FRONT-PANEL display area, not the
   camera ROI.** MEASURED 2026-09-16, both halves (the second confirms the user from memory: read the camera frame
   size, then set the IMAQ display size). Chain, divisor and caveats: `docs/camera-acquisition-facts.md`,
   "MEASURED 2026-09-16 ??uid 9775 READS the geometry". **Consequence: the plan?셲 1280횞1024 budget basis is safe.**
   ?좑툘 Do NOT widen it to "the VI does not set frame size" ??the codex review refuses that (archived, annotated);
   the residual test is `Property Items[] ??Is Write` across the 106 Property nodes. The fresh-session 640횞512 ROI
   reading stays **unexplained** and is a different thing from the 첨2 display size.
3. **19 archived reviews lack frontmatter and annotation** (audit A4 ??the cycle-10 audit counts **23**). The bulk
   `frontmatter.py` pass is safe to run now; the annotations are judgement work, not a formatting pass, and they
   are now the subject of a device (`violation-decisions.md`, Round 2, `repeated-failure-class`).
4. `Global motor pos.vi` ??write-only here; **user: a readability container covering all motors, keep it**.
5. **Startup drives instruments**, which is *allowed* while the rig is apart and becomes a hard blocker at
   assembly: ASI `Initialize` + `Move Axis to Position` on diagrams 10 and 88, position read on 12, PI init/`MOV`/
   `GOH`/`VEL` on 1/3/4/5 (`main-vi-startup.md:22-33`). Record what each run touched; excise only when the state
   changes, and then node-by-node in the build log (rule 1a).

## NEXT

?뵶 **REBUILD `OpDelete_v0` WITH ITS ERROR WIRED OUT ??that is the next build, and nothing in Phase A moves first.**
Delete removes nothing and the op cannot tell us why, because its `error out` is dead (measured:
`diag_delete_error_control.log`). Every op VI this fleet builds by trimming a donor depends on delete, so this is
upstream of all of Phase A. Two things are already done and must not be redone: the wrapper no longer swallows the
modal-dialog exception and now reads `error out` (`tools/gscript.py`), and the *reason* to rebuild is measured
rather than assumed. **Then prove one delete on a scratch VI with `verify=True`** before touching A1.
Only after that, re-run A1 with the ordering the B2/B3 review established ??**deletes first, then connects, only
ever into unwired sinks** ??plus `#1044` as class `Node`. A1 has one failure left.

Then take **A7's three audits** with it ??the reentrancy
audit is the one `t0-instrumentation-plan.md:65-70` calls *"the highest-value check in the whole plan"*, and we
already have a confirmed instance nobody had connected: `ASI_adjust focus-subvi.vi` is **non-reentrant** and called
from both loop 43 and loop 99 (`main-vi-panel-map.md:558`), i.e. an accidental mutex between the frame loop and the
display loop.

## Where to look

`CLAUDE.md` rules 쨌 **`docs/decisions.md` settled decisions** 쨌 `docs/NAMES.md` verified strings 쨌
`docs/toolkit-capabilities.md` API 쨌 `docs/restructure-plan-4.6.md` target + stages 쨌
`docs/pre-rig-master-plan.md` the plan 쨌 `archive/2026-09-16-status-session-gate-and-autofocus.md` and
`archive/2026-09-16-status-cycles-8-10-narrative.md` the reasoning behind all of it 쨌
`archive/` history (rule 4: not read in normal work).


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

**Verdict: this cycle is blocked on eight prior-art findings.** The *direction* (give the delete op a live error indicator) is sound and was in fact prescribed in our own files on 2026-09-06 — but the **method Stage 1 chooses was measured and refuted here two days ago**, Stage 3's A7 is a verbatim restatement of a plan row whose dependencies it drops, and one of its two "new" facts contradicts a document written 2026-09-14.

---

# PART A — THE DIRECTION

## A1 · SETTLED ALREADY

**(1) The "reading this cycle is built on" (cycle11-plan.md:25-36) was recorded at build time, 2026-09-06.**

> `docs/keystone-op-spec.md:281` — *"One auto-error dialog appeared (dismissed by the watchdog; **the Delete node's error out is unwired**) — same v0 limitation as the other ops."*
> `docs/keystone-op-spec.md:255-256` — *"the op's `error out` indicator is unwired (always clean) — creator errors surface only as auto-error dialogs (watchdog) **until an indicator is attached by a future op**."*

Both halves of the plan's hypothesis — the Invoke node's `error out` is unwired, and the panel indicator is therefore dead — are stated as measured facts at the moment `OpDelete_v0` was built, together with the remedy. **Consequence for the build:** Stage 1 step 2's *test* half ("a new indicator appearing is proof the terminal was unwired", :55-56) is spending a mutating `create_indicator` call to re-establish something already in the record. The *fix* half is still needed; the test is not.

**(2) Stage 3's entire A7 is the master plan's A7 row, uncited.**

`docs/pre-rig-master-plan.md:74` already contains all three audits, the `t0-instrumentation-plan.md:65-70` quote, property **288**, and the ASI sentence verbatim — dated 2026-09-16, *"widened 2026-09-16, rev5 A6"*. The cycle plan reproduces it at :89-96 as if assembling it. Two things are lost in the copy: A7's scope (*"Three audits over **A4's membership***") and its `needs` column (**A4, A6**).

## A2 · REFUTED ALREADY

**(3) The fp_labels oracle in Stage 1 step 3 was measured wrong on 2026-09-14.**

The plan: *"`fp_labels()` diff → the label LabVIEW gave it (expected `error out 2`). **The label is the confirmation that terminal 3 really is `error out`**"* (cycle11-plan.md:57-58). Our own run:

> `tools/bench/build_opbuildpn_v1c.log:6-9` — create indicator on the terminal *named* `error out` (index 10) → **`new indicator label(s): ['error out 2']; ExecState 0`**
> `:17` — *"Remove Bad Wires … (not a bad-wire problem)"*
> `:19-24` — PHASE B on index **15**, the *other* terminal also named `error out` → `['error out 2']; ExecState 1`

**The label `error out 2` appeared for both the right and the wrong terminal.** It confirms the terminal's *name*, never that it is the error **out**. The recorded discriminator is name **plus `Is Source?`** — which is exactly how `tools/recipes/build_opaddshiftreg_v0.py:255` does it (`nm == "error out" and s`).

**(4) Label-set diffing as a creation oracle was refuted and formally replaced.**

> `archive/peer/2026-09-15-opwiresource-fail1-uid-indicator-not-created.md:53` — *"**label-set cardinality is not a valid creation-success oracle**"*; `:101-104` (our own annotation) — *"The recipe now diffs panel rows **by UID** (`panel_wiring`, a multiset keyed by object uid) … a duplicate label would make every later read ambiguous."*

The plan reverts to the method that was retired, and P2 (:63) re-states the prediction that failed.

**(5) The stated Falsifier does not falsify.**

Plan: *"if `create_indicator` on that terminal declines (meaning the terminal is already wired), this reading is wrong"* (:35-36). The same archived exchange records a **decline on an unwired terminal**, and its top-ranked cause was neither: `:26-27` — *"**Unlisted H6: the invoke failed or returned no valid object.**"*, decision table at `:81-87`. A decline is therefore not evidence about wiring, and the recipe would stop on a false conclusion.

## A3 · CONTRADICTED

**(6) "the dialog is the only error signal there is" (cycle11-plan.md:19) — not for the failure this cycle exists to fix.**

> `tools/bench/diag_delete_error.log:16-19` — the *real* delete (valid uid 1319, ExecState 1): **`Run: returned`** … `'error out' -> status FALSE (clean)` … `objects that disappeared: NONE`

No dialog. The dialogs in `diag_delete_error_control.log:9-11` came only from the two *impossible* control inputs. So P4's mechanism ("wiring it should remove the dialog", :72-73) is a claim about the control cases; **the regression case produced no dialog, no error and no deletion**, and wiring `error out` may leave it exactly as silent.

**(7) The cycle forbids `net_map`, then re-runs a recipe built on it.**

> plan `:43` — *"**no `net_map` call anywhere in this cycle until delete is proven**"*
> plan `:85` — *"**A1** (`tools/recipes/build_opownerchain_v0.py`) re-run…"*
> `tools/bench/build_opownerchain_v0.log:4-28, 31-59, 62-90, 92-120, 122-142, 145-164…` — that recipe's single run performs **~14 `net_map` walks** and reports *"purged 166 junk Invoke(s)"* (:59) with a delete that does not delete.

**(8) "A1 has one of its two failures left" (:88) — the log says three.**

> `tools/bench/build_opownerchain_v0.log:299` — *"OpOwnerChain_v0 build: **2 pass, 3 fail** -> B2 …, B3 …, B4 …"*

`STATUS.md` itself says *"FAILED 3/5 gates"*. The plan's fix list covers B2/B4's causes (`#1044` class, ordering); **B3 is not addressed** — see finding 10.

**(9) "a confirmed instance nobody had connected" (:91-93) — it was connected on 2026-09-14.**

> `docs/g9-core-budget.md:32-33` — *"any non-reentrant subVI shared by two loops **serialises them** (both focus subVIs are non-reentrant by design; **keep one caller each**)."*

That is the accidental-mutex consequence, drawn and turned into a design rule two days before this plan calls it unconnected. (Minor, same family: `:86` cites `gscript.py:2084`, which is blank — the "wire only unwired sinks" sentence is `gscript.py:2110-2111`.)

## A4 · UNREAD EVIDENCE

**(10) `archive/peer/2026-09-15-priorart-ownerchain.md:117` predicted A1's surviving failure and was never annotated.**

> *"The pending recipe rewires only nodes 163 and 1221 … and **neither deletes nor re-feeds node 482. It therefore repeats the recorded failure cause.**"*
> Outcome: `tools/bench/build_opownerchain_v0.log:143` — *"**FAIL** B3 … consumers {163: 751, 1221: 751, **482: 1444**}"*

The cycle-11 A1 fix (:85-87) names deletes-before-connects, unwired sinks and `#1044` — **node 482 appears nowhere**. That review's "What was done with it" is still `(Claude fills in)` (`:139`).

**(11) `docs/pre-rig-master-plan.md:66-77` — the Phase-A dependency table.** A7 `needs: A4, A6`; A4 `needs: A3`; A3 `needs: A2`; A2 `needs: A1`. The plan runs **A1 → A7**, skipping A2–A5. A7(a) and A7(c) are both defined *over A4's membership*, which will not exist.

**(12) `docs/keystone-op-spec.md:565-573` (§33) and `:527-531` (§30) — delete has returned "0 gone" before, on a specific object class.**

> `:567` — *"`Create Invoke Node.vi` (**Delete on that node returns "0 gone"**…)"* (2026-09-07)
> `:527-529` — *"`delete_object` of the erdosmiller creator SubVI node **hangs 120 s** — the same op deleted six nodes of an FPTARGET copy … without trouble. **Deleting an lvlib-member subVI node is the specific trigger**"*

This is the same symptom, scoped to an object class, recorded while other deletes in the same session succeeded — directly relevant to whether the cause is the tool (the plan's premise) or the object, and it is cited nowhere in the plan or in `STATUS.md`'s "assume every `verify=False` delete since the regression did nothing".

---

# PART B — THE ARTIFACT

## B1 · ALREADY BUILT (the technique, not the op)

There is no `OpDelete_v1` and no `build_opdelete*.py` among the 121 recipes — **the artifact is new**. The *operation* is not:

- `tools/recipes/build_opaddshiftreg_v0.py:255-259` — locates the Invoke node's terminal by `nm == "error out" and s`, then `create_indicator(OP, node, te)` and prints the new label.
- `tools/recipes/build_opbuildpn_v1.py:118-124` — the identical step with the identical contract: *"1 Create Indicator on creator.'error out'" / "predict: ControlTerminal +1, Wire +1, ExecState stays 1"*, plus an **address assertion before invoking** (`:103-111`) added after a peer review of the run that got it wrong.

Stage 1 should be a copy of `build_opbuildpn_v1.py`'s step, not a fresh route.

## B2 · ALREADY FAILED

- Finding (3) above: this exact step, with the plan's exact oracle, produced `error out 2` **and a broken VI** — `build_opbuildpn_v1c.log:6-19`.
- **`node_info()` on this VI family is a recorded crash.** `OpDelete_v0` is `OpBuildInvoke_v0` lineage (`docs/keystone-op-spec.md:275` — *"Copy of OpBuildInvoke_v0 → GUI delete of the creator…"*), and `docs/keystone-op-spec.md:523` records *"(A) **node_info (Node.Label/Style) CRASHES on OpBuildInvoke/OpBuildPN-type VIs**"* — echoed in `tools/gscript.py:2233` (*"no Style/Label: crash, spec §30"*). Stage 1 step 1 (`:53`) makes `node_info()` its only topology reader. **Scope caveat, stated so it can be refuted cheaply:** OpDelete_v0 has had its creator deleted, the crash was never isolated, and `docs/motion-path-audit.md:139-142` logs a separate non-reproduction on different VIs. Check before relying on it; do not assume it away.

## B3 · HELPER EXISTS

| the plan hand-rolls | the call that already exists |
|---|---|
| "terminal 3 is `error out`" (:54-55), an unmeasured index | **`node_terms(target, diagram, node)`** — *"every terminal of ONE node: **name, `Is Source?`**, wire UID"* (`docs/toolkit-capabilities.md:23`), and **creator-free** (`:54-55`: *"OpSubVIs_v1 / OpNodeTerms_v0 are creator-free"*), so it satisfies the plan's own no-`net_map` rule |
| `fp_labels()` set diff (:57) | **`panel_wiring(target)`** — label, indicator flag, UID, *"connected-wire UID (0 = bare)"* (`docs/toolkit-capabilities.md:22`); the UID-keyed oracle the 2026-09-15 review made mandatory |
| "the front-panel `error out` indicator is wired to something else (or nothing)" (:32) — asserted | same `panel_wiring` call reads that wire UID **with no edit at all** |
| P4's premise, that the dialog *is* the unwired error out (:72-73) | **`set_auto_error_handling(target, False)`** — *"silences the auto error dialog for **every unwired error out** in that VI"* (`tools/gscript.py:2314-2317`). One call on a copy discriminates P4's mechanism before anything is built |
| A7(a) "which diagram owns it" (:94) | **`subvis(target, diagram)`** + `tools/bench/main_vi_subvis.json` — *"98 sites, 0 mismatches"* (`docs/toolkit-capabilities.md:21`), tabulated in `docs/main-vi-subvi-identity.md` |

## B4 · ALREADY MEASURED

- **A7(a), the VISA census** — `docs/motion-path-audit.md` already is one: `:30-40` the per-VI node counts; `:43-46` `ASI_adjust focus-subvi.vi`'s `Wait (ms)` + VISA on **diagram 8**; `:66-70` the size-1 semaphore in `Send Serial Command.vi`; `:72-74` the byte-count read and 5000 ms timeout; `:84-99` the measured round trip (**2.56 ms**). Only the *membership* mapping is missing — and `:130` already says so: *"**Step 0 first, unchanged** — determine which While loop holds what. Nothing above matters if these VIs are not on the per-frame path."* That step is A3/A4.
- **A7(c), the UI-thread census** — `docs/g9-core-budget.md:32`: *"UI-thread `Value` property nodes (**106 today; 88 implicit**)"*, and `docs/toolkit-capabilities.md:26` records *"88/88 implicit `Value` nodes of the main VI labelled with a panel label"*. `motion-path-audit.md:122-126` already states the remaining question exactly as the plan restates it.
- **A7(b), reentrancy** — the instance (`g9-core-budget.md:33`, `main-vi-panel-map.md:558`) and the property to read (`docs/vi-server-ids.json:62`, `docs/subvi-call-cost-plan.md:72`) are both already on disk.
- One method note the plan should not lose: `docs/motion-path-audit.md:137-138` — *"**`node_info` is top-level only** … a first pass that used only `node_info` would have concluded these VIs were almost empty. Walk every diagram index with `net_map` instead."* With `net_map` banned (:43), A7's censuses need `node_terms`/`subvis` per diagram, not `node_info`.

---

**Cheapest release path, if you want one:** findings 1, 3, 4, 5, and B3 all dissolve into a single Stage-1 rewrite — `panel_wiring` to read the existing indicator's wire, `node_terms` to get the `error out` terminal's index **and** `Is Source?`, then `create_indicator` guarded by a UID diff, copied from `build_opbuildpn_v1.py:103-124`. Findings 7, 8, 10, 11 are about Stage 3 and are independent of that.

```
PRIOR-ART: settled-already
PRIOR-ART: settled-already
PRIOR-ART: refuted-already
PRIOR-ART: refuted-already
PRIOR-ART: refuted-already
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: contradicted
PRIOR-ART: unread-evidence
PRIOR-ART: unread-evidence
PRIOR-ART: unread-evidence
PRIOR-ART: already-built
PRIOR-ART: already-failed
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
```

## Sources

(extract from answer)

## What was done with it

**ACCEPTED, 15 of 16 verdicts, and the cycle was replanned around them.** This is the most valuable review of the
cycle: it arrived while `build_opdelete_v1.py` was already running, and the run then failed in exactly the way
finding (5) predicted. Disposition per finding:

| # | verdict | what was done |
|---|---|---|
| 1 | settled-already | ACCEPTED. `keystone-op-spec.md:255-256,281` recorded on **2026-09-06** both that the Delete node's `error out` is unwired and that the remedy is to attach an indicator. The *test* half of Stage 1 was spending a mutating call to re-derive a recorded fact; it is removed. The *fix* half stays. |
| 2 | settled-already | ACCEPTED. Stage 3's A7 is `pre-rig-master-plan.md:74` re-typed, and the copy dropped A7's scope ("over **A4's membership**") and its `needs: A4, A6`. The plan now cites the row instead of restating it. |
| 3 | refuted-already | ACCEPTED, and it is the finding that decided the rerun. `build_opbuildpn_v1c.log:6-24` shows `error out 2` appearing for BOTH the right and the wrong terminal. The label confirms a NAME, never a direction. Replaced by `node_terms` → name **plus `Is Source?`**, the discriminator `build_opaddshiftreg_v0.py:255` already uses. |
| 4 | refuted-already | ACCEPTED. `fp_labels` set-diffing was formally retired on 2026-09-15 in favour of a UID-keyed `panel_wiring` multiset. The rerun uses `panel_wiring`. |
| 5 | refuted-already | ACCEPTED — **and it correctly predicted this run's outcome.** `build_opdelete_v1.log` recorded `create_indicator` declining, and I read that as "therefore the terminal is already wired". The cited exchange records a decline on an **unwired** terminal, so a decline is not evidence about wiring at all. Worse, my recipe's fallback then called `wire_indicators`, which needs an already-wired SOURCE; with an unwired one it silently no-ops. That is the most likely reason `error out` is still dead on `OpDelete_v1`, i.e. **v1 is probably behaviourally identical to v0** and nothing was actually fixed. |
| 6 | contradicted | ACCEPTED. `diag_delete_error.log:16-19` already recorded the real delete returning with **no dialog**, so "the dialog is the only error signal" was never true of the regression case. Stage 2 re-measured exactly that. The plan's P4 mechanism is withdrawn. |
| 7 | contradicted | ACCEPTED, and it is worse than stated: the recipe's `nodes_by_uid()` helper calls `net_map` on **every** rewire and **every** delete — `build_opownerchain_v0.log:59` reports *"purged 166 junk Invoke(s)"* with a delete that does not delete. A1 cannot be re-run as written; it is rewritten creator-free on `node_terms` + `report_all`. |
| 8 | contradicted | ACCEPTED. 2 pass / 3 fail, not "one failure left". STATUS.md's line was wrong and is corrected. |
| 9 | contradicted | ACCEPTED. `g9-core-budget.md:32-33` had already drawn the accidental-mutex consequence and turned it into a design rule ("keep one caller each"). The `gscript.py:2084` citation was off by ~26 lines; the sentence is at `:2110-2111`. |
| 10 | unread-evidence | ACCEPTED, and this is the actionable half of A1. `archive/peer/2026-09-15-priorart-ownerchain.md:117` predicted the surviving B3 failure — **node 482** is neither deleted nor re-fed — and the log confirms it (`consumers {163: 751, 1221: 751, 482: 1444}`). That review is still unannotated; it is now on the OPEN list with the other undisposed ones. |
| 11 | unread-evidence | ACCEPTED. A7 `needs: A4, A6`; A4←A3←A2←A1. Running A1→A7 would define two of the three audits over a membership set that does not exist. Stage 3 is rescoped to A1 plus the A7 work that is genuinely independent of A4. |
| 12 | unread-evidence | ACCEPTED, and it reframes the whole cycle. `keystone-op-spec.md:527-529` records delete removing **six nodes of an FPTARGET copy** cleanly in the same session in which it hung on an lvlib-member subVI node, and `:567` records it returning "0 gone" on one specific node — while `§33` reports **1,403 junk nodes purged** by the same call. So delete has demonstrably worked, and "the tool is broken" is probably the wrong frame: the next measurement is a **class × target matrix**, not another repair. |
| B1 | already-built | ACCEPTED. Stage 1 is rewritten as a copy of `build_opbuildpn_v1.py:103-124` (address assertion before invoking, UID-diff oracle) rather than a fresh route. |
| B3 | helper-exists | ACCEPTED in full. `node_terms` (name, `Is Source?`, wire UID) and `panel_wiring` (label, indicator, UID, connected-wire UID) are both **creator-free**, so they also dissolve the plan's `net_map` ban into a non-issue. This killed a throwaway-copy workaround I had already written (`tools/bench/diag_opdelete_topology.py`, which walked disposable copies with `net_map` so the junk could go in the bin with them) — it is replaced by these two calls. `set_auto_error_handling(target, False)` is adopted as the discriminator for the dialog mechanism. |
| B4 | already-measured | ACCEPTED. `motion-path-audit.md:30-99` already **is** the VISA census, `g9-core-budget.md:32` already holds the UI-thread count (106 / 88 implicit), and the reentrancy property (288) and the instance are both on disk. What is missing in all three is only the **membership** mapping, which `motion-path-audit.md:130` itself names as the prerequisite. A7 is therefore not new work; it is A3/A4 work. |
| B2 | already-failed | **PARTIALLY REFUTED, by the reviewer's own invitation to check.** The claim that `node_info` crashes on OpBuildInvoke-lineage VIs did not hold here: `build_opdelete_v1.log` shows `node_info(OpDelete_v1, max_n=40)` returning four clean rows (`Open VI Reference`, `Traverse for GObjects.vi`, `Index Array`, `Invoke Node`) with no crash. The reviewer flagged the caveat as unisolated and pointed at a non-reproduction, and this is a third. **What survives, and is accepted:** `motion-path-audit.md:137-138` — `node_info` is *top-level only*, and this VI has no sub-diagrams, so it cannot be relied on for the A7 censuses. The other half of the finding — that `build_opbuildpn_v1c.log` shows this exact step producing a broken VI — is accepted under finding 3. |

**Cost:** this dispatch is the archive-reading reviewer whose token cost the user asked to track; the run is
`tools/bench/priorart_cycle11.log`.
