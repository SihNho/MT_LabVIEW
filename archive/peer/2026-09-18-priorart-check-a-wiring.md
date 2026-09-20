# priorart-check-a-wiring

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.8531  in 46 / out 25995 / cache-create 250401 / cache-read 3397879  (367s, 39 turn(s))
- **date:** 2026-09-18 01:12:34
- **outcome:** ANSWERED (371s)
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
# About to build: `tools/motor_wiring_check.py` ??check A of `docs/motor-limit-assurance-plan.md` 짠A

Cycle 19, P1 step 2. This is the WIRING CHECK: for every in-scope motion call site, trace the position/target
input BACKWARDS and compare the built VI's trace against the original's. It is a READER ??no VI is run, nothing
is saved, no serial port is opened, no motor moves (cycle19-plan Pre-decided 1). It will live in `tools/`, not
`tools/recipes/`, exactly like `tools/motor_census.py` (step 1, closed).

## What I found already exists, checked before writing a line

- `tools/motor_census.py` + `tools/bench/motor_census_3state-ORIGINAL.json` / `??v6-workingcopy.json`:
  the 43 in-scope sites per VI with diagram index, node uid, callee, path, `kind`, owner structure.
  Check A does NOT re-census; it consumes this JSON.
- `docs/motor-call-site-census.md` ??the two cycle-1 decisions (kinds; `ASSUMED_MOTION` in scope).
- `tools/gscript.py` readers: `count(vi,'Diagram')`, `report_all(vi,cls)`, `node_labels(vi,d)` (uid+label for
  every node of one diagram, in `Nodes[]` order ??so it doubles as the uid ??node-index map),
  `node_terms(vi,d,n)` (per-terminal name / `Is Source?` / wire uid, 0 junk per call),
  `subvis(vi,d)`, `tunnels(vi,i)`, `shift_reg`/`shift_reg_left`.
- `OpWireSource_v5.vi` + `build_opwiresource_v5.read_terminal()` ??WIRE uid ??each `Wire.Terms[]` entry's
  `Is Source?`, reciprocal wire, owner class + owner uid. Prior art for the backward hop:
  `tools/bench/diag_autofocus_border.py` resolves three wires of the main VI this way (12/12 verified).
  KNOWN DEFECT I will not repeat: `read_terminal` hard-codes `MAIN` as `vi path`
  (`tools/recipes/build_opwiresource_v5.py:161`) and the op is UID-addressed, so the caller must set `UID 2`
  (`toolkit-capabilities.md:60`, the caller defect that produced "0 rows, error 1055"). My caller passes the
  target explicitly and sets the uid input.
- `OpTunnelRead_v0.vi` (`toolkit-capabilities.md:71`) ??tunnel uid ??inner wire per frame, frame diagram uid.
- `tools/bench/build_diagram_hierarchy.py` nearest-structure rule (already reused by motor_census).
- `docs/motion-path-audit.md`, `docs/main-vi-startup.md:33` (the startup ASI move, the plan's known
  no-limit candidate), `docs/instrument-libraries.md`.
- `net_map()` is deliberately NOT used: it drops junk Invoke nodes into the target and purges them afterwards.
  On an ORIGINAL that is an in-memory modification I do not want (rule 1), and `node_labels` + `node_terms`
  give the same information junk-free.

## The design

1. Read the two census JSONs; take the 43 in-scope sites per VI verbatim (no demotion pass, cycle19-plan).
2. Per VI: `node_labels(vi, d)` for every diagram that carries an in-scope site ??`uid ??(diagram, Nodes[] index,
   label)`. One op run per diagram.
3. Per site: `node_terms(vi, d, idx)` ??every terminal name, direction, wire uid. Pick the position/target input
   by name pattern; if none matches, walk every wired non-error non-refnum input (capped), so nothing is silently
   skipped. Record ALL input terminal names in the row.
4. Backward walk, offline in Python plus one UID-addressed op run per wire: wire uid ??`OpWireSource_v5` ??the
   single terminal with `Is Source? TRUE` ??owner class + owner uid ??if that uid is a node in the map, read its
   terminals and continue; bounded depth and a wall-clock budget.
5. Per hop record: node class, uid, terminal name; whether the node is a coerce / `In Range and Coerce`; for a
   coerce, where its upper- and lower-limit inputs come from and whether either is unwired; whether any
   ALTERNATIVE path reaches the call site without passing the coerce (every other source terminal on the same
   net, and every other wired input of the same call site).
6. Compare the V6 working copy's row against the 3StateClamping original's row, field by field. Difference = FAIL.
   Original with no limit on the path = a reported FACT for judgement, not a FAIL.
7. Outputs: `tools/bench/wiring_check_A_3state-ORIGINAL.json`, `??v6-workingcopy.json`, `docs/motor-wiring-check-A.md`.

## Default-deny and the negative proof

- A site whose trace cannot be completed (missing reader, error, budget) is `UNTRACED` ??in scope, never dropped,
  never counted as PASS, with the missing primitive named. Same principle as census DECISION 2.
- The comparator must be proven to REFUSE, not only to pass (cycle19-plan Pre-decided 4): three MUTATION
  NEGATIVES on its own input (the trace JSON) ??coerce node deleted from a path, coerce upper-limit wire cut,
  a second un-coerced path added to a call site ??each must produce FAIL. Building deliberately broken VIs is
  짠D.4's later step (it tests the EXTRACTOR, not the comparator) and is NOT done this cycle.

## Prediction contract (printed before execution, machine-checked after)

G1 both originals' md5 unchanged before AND after. G2 exactly 43 in-scope rows per VI, zero dropped.
G3 every row carries a verdict in {PASS, FAIL, UNTRACED}. G4 the three mutation negatives each produce FAIL.
G5 no VI run, nothing saved, no serial port opened; LabVIEW handle count printed before and after.
Measurement, not a gate: the ORIGINAL-vs-V6 differing-row count and which rows differ.


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??`archive/2026-09-18-status-cycle1-census.md` (latest) + the `archive/2026-09-1[67]-status-*.md` set.
?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.
## START HERE
1. **Cycle plan = `docs/cycle19-plan.md`** (P1 plan `docs/motor-limit-assurance-plan.md`; master
   `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, **`-Dual -TimeoutSec >= 780`**.
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌
   `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md`
   짠1** ??read once per fresh session, then work from here.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# Cycle-17 census runs held it 23:29-23:41 / 23:49-23:53, released it. MEASURED before AND after: NO LabVIEW.exe;
# nothing run/saved, no port opened, both originals' md5 unchanged. ("pid 13480 holds COM3+COM4" was STALE.)
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.

## HARDWARE ??permission follows the RIG STATE. Current: **議곕┰ / ASSEMBLED** (machine key `rig-state:` below)
遺꾪빐 = motors ??ASI ??camera ??쨌 **議곕┰ ??WE ARE HERE** = camera ?? motors/ASI ONLY through `tools/motor_gate.py`
inside the envelope 쨌 ?ㅽ뿕以?= ?????? ?좑툘 ASI carve-out **RETIRED** (rule 1b); **only the user announces a state
change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera 1280횞1024, offsets 0, 90.0009 Hz, never write
`BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??the acquisition loop applies
`tools/bench/camera_contract.py`. **No beads on the rig.**
?뵶 **P1 IS STRICTER THAN THE RIG STATE AND P1 WINS:** in P1 (see `## NEXT`) **no motor moves and no motor port is
opened for writing** ??`motor_gate.py --execute` is not to be called at all.
?넅 **SAFE MOTION ENVELOPE (user, 2026-09-17 ??says what is safe, NOT when motors are allowed):** ASI up/down no
limit 쨌 ASI x/y **never home/origin, ??~1 mm from the current position** 쨌 PI magnet **0??9 mm only** (`Max Trans
Pos` = 40.94, a **coerce** in the original; `TMX 52` ??**the controller protects nothing**; our scripts bypass the
coerce ??every motor-commanding tool must carry the clamp as refusing code).
**Motors ARE allowed while assembled INSIDE the envelope ??conditional on the envelope being really enforced**
(user, 2026-09-17 evening). ??`tools/motor_gate.py` = the ONE gateway (70/70 self-test; default-deny; PI 0??9,
ASI x/y ??.0 mm from `tools/bench/motor_anchor.json`, ASI z free); its first live PI + ASI moves all passed;
rotor transmit **NOT built**. Numbers ??`archive/2026-09-17-status-motor-gate-live-moves.md`.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand
?넅 **CYCLE 18: the STOP RECORD + LAUNCH GATE is BUILT and PROVEN ??`device-failed` DISCHARGED** (`violations.py`
= "0 slug(s) awaiting a response"). `tools/stop_record.py` + `guard_bash.py:156` / `guard_cycle.py:462`; **refusal
by PATH, release qualified by HASH**; fail-closed; **`prior_art_review.py` now REFUSES without `--recipe`**;
29/29 self-test gates. Full text ??`archive/2026-09-18-status-cycle18-stopgate.md` 짠1; decision ??
`docs/violation-decisions.md` round 6.
?넅 **`doc_ingest` contradiction RESOLVED (judgement): CLAUDE.md:49's 議곕┰ row was stale, STATUS was right.** Both
sources are the user's; the 2026-09-17 evening envelope decision is LATER and NARROWS (one gateway + enforced
envelope), so it amends the 2026-09-16 table. CLAUDE.md rule 1b now carries the amended row + the why.
**P1 step 1 (CENSUS) IS CLOSED** ??`tools/motor_census.py` ??`docs/motor-call-site-census.md`: 97 sites, **IN
SCOPE 43, undecided 0**, originals' md5 unchanged. ?뵶 **Rule 1c fact: `ASI_adjust focus-subvi.vi` (COMMAND) is
called on diagram 43 = the FRAME LOOP** ??the ORIGINAL already puts serial traffic on the frame acquisition path.
Recorded, nothing changed. Numbers ??`archive/2026-09-18-status-cycle18-stopgate.md` 짠2.
**Stage 1 CLOSED**; **Stage 2** `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??bit-identical for the **first
10,018 frames only**, both **replay**. **THE GAP:** 174 ops, 123 recipes, 235 peers ??**zero runnable
experimental VIs** (`archive/2026-09-18-status-cycle1-census.md` 짠2).

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
32. ?뵶?뵶 **outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive ??the work stops for a re-plan with the
   USER.** Not answerable by a device. Stands above everything else here.
38. ?뵶 D1 route-B run 3 changed NOTHING (63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0); `SR_QUEUE_AUTHORISED` / `TEMP_SINK_AUTHORISED` = False. **`docs/d1-route-b-plan.md` 짠11/짠11a**; archive 짠3.
39. ?뵶 `VI.Get Errors` 452 NOT built ??prior-art stopped it on `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED.
41. ?뵶 **judgement only ??the stall watchdog's liveness test.** Both arms (ANSWERED) REFUSE "false positive"; remedy
   not built. `archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`.
42. ?좑툘 39 archived reviews undisposed (`doc_lint` L6 FAIL ??the ONLY fail; L3 110/110, L4, L8 all PASS).
43. ?뵶 **`guard_cycle.premature_build` ALLOWS where `selftest_guard_cycle_fixed.py` T6 expects REFUSED.**
   **MEASURED AND DIAGNOSED, cycle 19** (annotation: `archive/peer/2026-09-18-cycle18-t6-regression-codex.md`
   짠"Cycle 19"): **T6 has NEVER passed** ??no `selftest_guard_cycle_fixed.log` exists and no log names it PASS;
   the "6/6" at `archive/2026-09-17-status-d1-phase-full-narrative.md:254-256` states each test's *expected*
   verdict in prose, so codex's refutation rested on intent, not output; no older `guard_cycle.py` exists, so
   "drift" is unevidenced. `guard_cycle.py:379`'s `if not newer:` **inverts** CLAUDE.md:449 condition (b) ??a
   review newer than the recipe suppresses the very check it should trigger. **So route-B run 3 evaded nothing;
   the branch never enforced.** ?뵩 **CYCLE 20 FIXES `:379`** ??first enforcement, not a repair; every recipe
   launched down that branch to date went unchecked. Until then the cycle-18 launch gate is the ONLY thing
   binding a launch to a verdict. Detail ??`archive/2026-09-18-status-cycle18-stopgate.md` 짠3.

## NEXT
**CYCLE 19 STARTS HERE ??read `docs/cycle19-plan.md` (`status: current`) and its `## Pre-decided`. Do its BOUNDED
T6 pre-step (ONE dispatch, measurement only ??OPEN 43), then run P1 step 2: `docs/motor-limit-assurance-plan.md`
짠A, check A, carrying all 43 in-scope sites, no demotion pass.** One step, then close. If a fix for T6 is needed,
it is cycle 20's ??do not let it eat check A.

Cycle 18 is CLOSED and its gate is DISCHARGED: `py tools/violations.py` now reports **"0 slug(s) awaiting a
response"** (`device-failed` answered 2026-09-18 00:53, `docs/violation-decisions.md` round 6), so `guard_cycle`
will not refuse cycle 19's build on a slug at threshold. The device itself is in "Where things stand" above; its
rationale stays in `docs/cycle18-plan.md` (`status: done`). **The date-granularity bug at
`docs/violation-decisions.md:197-207` did NOT bite ??same-day answers parse; that note is now stale, and only the
user should decide whether to delete it.**
?좑툘 **Practical change every session must know: `tools/prior_art_review.py` now REFUSES (rc 2) without
`--recipe <path>`**, unless `--no-recipe "<reason>"` with a real reason. A non-`novel` verdict plants a stop
record and the launch gate refuses that recipe until a valid `FIXED:`/`REFUTED:` line stands. Do not route around
it; `CYCLE_GUARD_OFF` is never the answer.

?뵶 **THE RUNNER'S ORDERS (user, 2026-09-17 23:4x): "紐⑦꽣 ?묐룞 泥댄겕 ?꾧퉴吏??紐⑤뱺 ?몄뀡 ?뚮젮蹂?寃? ?댄썑 ?닿? ?먮━??
?덈뒗 ?곹솴?먯꽌 紐⑦꽣 ?곹븳 ?섑븳 泥댄겕 寃利? ?댄썑 ?섎㉧吏???섎꽕??猷⑦봽 ?????덈룄濡?.**
**P1 (runner, unattended, NOW):** `docs/motor-limit-assurance-plan.md` 짠D order ??census ????A ??B ??broken-VI
proof ??C + record hook ??one step per cycle, material sub-sessions do the work. **NO MOTOR MAY MOVE AND NO MOTOR
PORT MAY BE OPENED FOR WRITING in P1** (`motor_gate.py --execute` is not to be called; stubs only); LabVIEW +
camera allowed (rig 議곕┰). Takes precedence over OPEN 41 and the D1 build.
**P1 ENDS ??and the cycle that finds it so writes a line starting `STOP` in this file's first 60 lines ??when the
only work left needs a real motor or the user** (or the failure budget is spent). Say in that line what is ready.
**P2 (USER PRESENT):** live verification of the limits on the real motors. **P3:** the user restarts the runner
for the rest (OPEN 41, D1 ??. 짠D's independent checker `.claude/agents/motor-limit-checker.md` is WRITTEN; its
tools, the hash-record gate, the record-write hook and the broken-VI proof are **NOT BUILT**.
?뱥 **Every runner cycle writes `docs/cycle<N>-plan.md` with a `## Pre-decided` section; the closing session writes
the NEXT cycle's file** and flips its own off `status: current` (cycle 18 ??`done`, cycle 19 ??`current`).
`docs/cycle15-plan.md` stays `status: paused`, its `## Pre-decided` still authoritative for the D1 queue
questions. D1/route-B state: `archive/2026-09-18-status-cycle1-census.md` 짠4. **OPEN 32 still stands above all.**

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

## PRIOR-ART REVIEW — `tools/motor_wiring_check.py` (check A)

The direction is sound and not previously refuted. But four measured artefacts covering this build's steps 2–4 were not consulted, and one of them already measured what this design's central rule does at a structure border. Verdict is not `novel`.

---

### PART A — THE DIRECTION

**A1 SETTLED ALREADY — no.** Check A is the current authorised step (`docs/cycle19-plan.md:16`) and the census explicitly reserved this work: *"It does **not** trace the position input backwards; that is check A"* (`docs/motor-call-site-census.md:161-167`). Nothing here is decided against it.

**A2 REFUTED ALREADY — no.** No archived review, retrospective or superseded section argues against a static backward wiring check. The nearest neighbour (`d1-build-plan.md` §11q–11s) abandoned a *premise about tunnel chains*, not the trace method.

**A3 CONTRADICTED — yes, one, and it is narrow.**
The plan states: *"`net_map()` is deliberately NOT used: it drops junk Invoke nodes into the target and purges them afterwards. On an ORIGINAL that is an in-memory modification I do not want (rule 1)."*

That rationale is contradicted by measurement in our own files:
- `docs/NAMES.md:332-339` — *"Same scratch, same process, same OpNetInfo_v1: walked **by reference only → 0 junk**; after `open_panel` → **78 junk** … So: reads of the main VI (never opened) never received junk — the STATUS line saying the overnight sweep 'poured junk' into it **was an inference and is withdrawn**."*
- `docs/toolkit-capabilities.md:76-77` — *"junk Invokes land only on an open target (a reference-only read never receives them — `walk_junk_probe.log`)"*.

The **choice** survives; only the reason is wrong. The reason that does survive is a different one the plan does not cite: `archive/2026-09-16-status-gate-a1-delete-regression.md:143-144` — *"`net_map`'s purge calls it `verify=False` inside `except Exception: pass`, so **no caller anywhere had positive evidence that delete works**"*. And the cost argument is independently decisive (`docs/toolkit-capabilities.md:23` 0.8 s/node vs `:493` net_map ≈ 8 s/node). Fix the sentence, keep the decision.

**A4 UNREAD EVIDENCE — yes, four documents, and they are the ones this build is about to re-derive.**

| what exists | citation | what it covers |
|---|---|---|
| Every terminal of **all 626 nodes on all 170 diagrams** of `Min_Track N beads V6_ParallelLoop.vi` — name, `is_source`, wire uid | `tools/bench/main_vi_nodeterms.json:2` (the `vi` field names that path); described at `docs/main-vi-stop-and-save.md:17` | **the plan's steps 2 AND 3, for one of its two targets, already measured 2026-09-14, read-only** |
| Per-diagram `Nodes[]` uid lists, same VI, 170 diagrams / 635 nodes | `tools/bench/diagram_tree_main.json:2`; generator contract at `tools/bench/sweep_nodeterms_main.py:3-7` | the uid → `Nodes[]`-index map the plan spends **one `node_labels` op run per diagram** to rebuild |
| `InRangeAndCoerce` is a valid Traverse class and the whole VI holds exactly **3** | `docs/NAMES.md:319`; the three labelled at `tools/bench/main_vi_node_labels.json:292,1490,1715` | the candidate limit-node set is **bounded at 3 and enumerable in one op run**, forward — no backward walk needed to *find* a coerce |
| Diagram 13 already recorded as a **range clamp** (`In Range?` `coerced(x)` `lower limit`) | `docs/main-vi-startup.md:36` | sits **three frames after** the startup ASI move at `docs/main-vi-startup.md:33` — the line the plan cites as its "known no-limit candidate". The plan cites `:33` and not `:36` |

Concretely, the data the plan's steps 3 and 5 want is already in the file, per terminal, including the "is a limit input unwired?" column: `tools/bench/main_vi_nodeterms.json:4519-4554` — diagram 13, node 0, uid **790**, `In Range?` **wire 0 (unwired)**, `coerced(x)` wire 2254, `lower limit` (sink). One md5 comparison against the current VI validates or invalidates the whole cache; that is the cheap check, not a re-sweep. The 3StateClamping original genuinely has no such cache and does need the live pass.

---

### PART B — THE ARTIFACT

**B1 ALREADY BUILT — no.** No tool performs the original-vs-copy limit comparison. `tools/motor_census.py` stops at call sites (`census()` at `:347-378` uses `g.subvis`, which returns `SubVIs[]` order, not the `Nodes[]` index this needs), and `gscript.py` has `subvis`/`node_labels`/`node_terms`/`node_terms_uid`/`tunnels` but no wire-source wrapper. Building `tools/motor_wiring_check.py` is warranted.

**B2 ALREADY FAILED — no**, with one correction in the plan's favour: the `OpWireSource_v5` caller defect it names is real. `tools/recipes/build_opwiresource_v5.py:161` does `vi.SetControlValue("vi path", MAIN)` — the target is hard-coded and the `vi` argument is the *op*, not the target. Confirmed independently at `docs/d1-build-plan.md:744-746`.

**B3 HELPER EXISTS — yes, two.**

1. **The cross-border backward hop is already built as a composition and already run.** `docs/d1-build-plan.md:727-731`: *"`gscript.tunnels()` gives the old tunnel's OUTER wire; `OpWireSource_v5` walks that wire's `Terms[]` and returns `Is Source?` + owner class/uid; the owner is located and the terminal index derived **offline** from `main_vi_nodeterms.json` + `d1_step0_census.json`. Raw rows: `tools/bench/d1_tunnel_sources.json`."* Driver: `tools/bench/diag_tunnelsource_onehop.py`. Its own prior-art review concluded it was a composition of ops already on disk *before* it was built (`archive/peer/2026-09-17-priorart-tunnelsource-onehop.md`).
2. **The wire-uid join and backward slice are already written and offline.** `tools/bench/wiregraph_frame_loop.py` builds 92 directed edges and a named *backward slice* from `main_vi_nodeterms.json` with no LabVIEW run at all (`docs/frame-loop-wire-graph.md:15` and the slice at `:43`). The plan's step 4 hand-rolls the same join one wire at a time, at one op run per wire.

**B4 ALREADY MEASURED — yes, twice, and the first is the decision-relevant one.**

1. **The plan's step-4 continuation rule has already been measured at a structure border, and it terminates.** The plan says: *"if that uid is a node in the map, read its terminals and continue."* That is exactly the rule run on 18 comparable hops, with this result — `docs/d1-build-plan.md:733-739`: **`FlatSequenceInnerTunnel` 14 rows, `LeftShiftRegister` 2 rows, both "❌ not a node on any diagram"**; 1 resolved, 1 did not advance. Raw: `tools/bench/diag_tunnelsource_onehop.log:22-45`, e.g. `:28` *"UNRESOLVED owner uid 5818 (FlatSequenceInnerTunnel) is neither a node on diagrams (19, 43, 0) nor a LoopTunnel"*.
 Two more measurements compound it, neither cited by the plan:
 - `OpWireSource_v5` returns owner class **`Diagram`** (uid 639) for a border-fed wire, not the border object — `tools/bench/diag_autofocus_border.log:8` and `:20`.
 - `OpOwnerChain_v1` **terminates silently on a `FlatSequenceFrame` owner** (`owner_uid 0`, `error 1055`, empty cast echo) — `docs/toolkit-capabilities.md:61`. And `FlatSequenceFrame` is the owner class of this plan's headline site: *"d10 FlatSequenceFrame uid 44036 ASI `Move Axis to Position.vi`"* (`docs/motor-call-site-census.md:105`).
 Under the plan's own default-deny, the startup ASI move — the one site §A singles out — lands in `UNTRACED`. The missing primitive is already researched with ids in the archive: `FlatSequenceInnerTunnel.Left Terminal` **1C3A9000** / `Right Terminal` **1C3A9001** (`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md:57-62`) — a peer answer, so a hypothesis under rule 5, not a fact.

2. **One hop of the exact trace check A exists to make is already on disk.** `tools/bench/diag_tunnelsource_onehop.log:38-42` — ForLoop `#1359` t9 `Magnet position output` ← LoopTunnel `#28343` ← **RESOLVED `{'diagram': 19, 'node': 16, 'term': 0, 'owner_class': 'SubVI', 'owner_uid': 27605}`** — and `docs/frame-loop-wire-graph.md:264` names that source *"subVI `Max Trans Pos.vi` · `Magnet position output`"*, i.e. the original's limit source. Measured on the same V6 working copy with md5 `2a78e17c449cacdaf5da389818526859` verified before the run (`tools/bench/diag_tunnelsource_onehop.log:2`) — the same md5 the census re-verified on 2026-09-18 (`docs/motor-call-site-census.md:19-21`).

The three mutation negatives on the comparator (G4) are, as far as these files go, genuinely new. That part is not blocked by anything here.

---

```
PRIOR-ART: unread-evidence
PRIOR-ART: contradicted
PRIOR-ART: helper-exists
PRIOR-ART: already-measured
PRIOR-ART: already-measured
```

## Sources

(extract from answer)

## What was done with it

**HELD FOR JUDGEMENT — no release line is written here, deliberately.** The cycle-19 material session that
picked up check A found this review already on disk and the launch gate already armed
(`tools/bench/stop_records.json`: `tools/motor_wiring_check.py`, verdict
`unread-evidence, contradicted, helper-exists, already-measured`, `released: null`; `guard_bash.py` refuses any
command naming that path). Its brief says a verdict other than `novel` is a STOP and that the `FIXED:` /
`REFUTED:` release is the judgement session's call, so it wrote none. `tools/motor_wiring_check.py` does not
exist; nothing was built, nothing was run in LabVIEW.

Every load-bearing citation in the review was OPENED and verified verbatim by that session (2026-09-18,
offline, no LabVIEW process): `docs/NAMES.md:319` · `docs/NAMES.md:332-339` · `docs/toolkit-capabilities.md:61`
· `docs/d1-build-plan.md:733-739` · `docs/motor-call-site-census.md:105` · `docs/main-vi-startup.md:33-36` ·
`tools/bench/diag_tunnelsource_onehop.log:28`. All exist and say what the review says they say.

Three measurements added on top, for whoever writes the release:

1. **A4's cache is still valid.** `tools/bench/main_vi_nodeterms.json`'s `vi` field names
   `Min_Track N beads V6_ParallelLoop.vi`, whose md5 on disk is `2a78e17c449cacdaf5da389818526859` — the same
   md5 `docs/motor-call-site-census.md:19-21` recorded. 170 diagrams / 626 nodes / 3,328 terminals, swept in
   662 s. The 3StateClamping ORIGINAL still has no such cache.
2. **B4.1's terminator covers most of check A's scope, not a corner of it.** Of the 43 in-scope census sites,
   **32 are owned by `FlatSequenceFrame`** (6 CaseStructure, 3 WhileLoop, 1 Sequence, 1 ForLoop), including
   the headline startup ASI move (d10 uid 44036) — computed from
   `tools/bench/motor_census_3state-ORIGINAL.json`'s `owner_structure` column.
3. **A4's "the coerce set is bounded at 3" is confirmed and is a fact about the whole VI.** A label scan of all
   170 diagrams of `tools/bench/main_vi_node_labels.json` returns exactly four limit-shaped nodes:
   `In Range and Coerce` d13 uid 790, d73 uid 25455, d88 uid 41725, and `Array Max & Min` d43 uid 10969 (the
   frame loop's bead-position min, not a limit). So at most 3 of the 43 sites can be `COERCE_ON_PATH` through
   a coerce node on a main-VI diagram.

Consequence, stated as a fact and not as a decision: check A as briefed would classify ~40 of 43 sites
`ORIGINAL_UNBOUNDED` or `UNRESOLVED`, which is `docs/motor-limit-assurance-plan.md`'s own
"Open for judgement" item *"What to do with a call site where the original itself is unbounded."*

### RELEASE — cycle-19 judgement session, 2026-09-18

**This review is RIGHT on all four slugs.** Nothing here is refuted. The design it stopped has been replaced by
`docs/motor-limit-assurance-plan.md` **§A.1**, written after this review; §A's requirements are unchanged, the
METHOD is what changed. The most damaging finding — that the backward-walk continuation rule terminates on 32 of
the 43 sites — was additionally taken to the machine this cycle rather than argued with, and the measurement
(`tools/bench/probe_flatseq_walk_run2.log`, `tools/bench/probe_flatseq_outer.log`) shows the barrier is
`Diagram[d].Nodes[]` addressing rather than LabVIEW: the tunnels are Traverse-visible and UID-addressable, and
the missing primitive is a UID-addressed tunnel reader, now cycle 20's build and a prerequisite to check A.

```
FIXED: unread-evidence - docs/motor-limit-assurance-plan.md:69 - Check A now consumes main_vi_nodeterms.json and diagram_tree_main.json under md5 validation instead of re-running node_labels per diagram, and enumerates the three InRangeAndCoerce uids forward (:50) instead of walking backwards to discover a coerce.
FIXED: contradicted - docs/motor-limit-assurance-plan.md:77 - The withdrawn "net_map pours junk into an original" claim is deleted and the decision now rests on the two reasons that survive, no positive delete evidence and 0.8 s/node vs 8 s/node.
FIXED: helper-exists - docs/motor-limit-assurance-plan.md:72 - The trace is now an offline join reusing wiregraph_frame_loop.py and diag_tunnelsource_onehop.py, touching LabVIEW once per border instead of once per wire, with the already-resolved Max Trans Pos hop as the walker's fixture.
FIXED: already-measured - docs/motor-limit-assurance-plan.md:60 - Check A no longer inherits the terminating continuation rule: the flat-sequence border was measured this cycle to be crossable by UID-addressed tunnel properties, so a UID-addressed tunnel reader is built and proven before check A runs.
```

Two consequences recorded here so they are not lost: the callee scan found **zero** limiting constructs in every
motion subVI and no nodes at all in `Max Trans Pos.vi` (§A.1 item 2), and a limit can also live in a control's
**Data Entry range**, which is not a node — so no site may be classified `ORIGINAL_UNBOUNDED` until that is read
(§A.1 item 7). Check A itself is NOT run by this release; it is cycle 21's, after the reader.
