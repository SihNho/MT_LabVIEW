# priorart-fstunnel-v2-preclean

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $4.7805  in 36 / out 27004 / cache-create 281747 / cache-read 2575428  (422s, 28 turn(s))
- **date:** 2026-09-18 12:18:31
- **outcome:** ANSWERED (424s)
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
# Under review: `tools/recipes/build_opfstunnelterm_v2.py` ??one pre-clean insertion into the frozen `_v1` recipe

Cycle 23, dispatch 3. This is the plan for ONE recipe file, already written and NOT yet run.

## What the recipe is

`tools/recipes/build_opfstunnelterm_v2.py` is a **byte-for-byte copy** of the frozen
`tools/recipes/build_opfstunnelterm_v1.py` (md5 `577669d3bb83b25116cf33b5e6d07bb7`) plus **one functional
insertion** and two docstring lines. Verified mechanically: 187 inserted lines, 0 deleted, and the only two
replaced lines are both inside the docstring (the contract header and the launch line). Every code line of `_v1`
is unchanged. `_v1.py` itself was not edited (editing it bricks its launch path ??`stop_record._check:325`).

The insertion is `preclean()`, called once per op from `build_one`, immediately after `shutil.copy2(DONOR, op)` +
`open_panel(op)` (the `_v1.py:403` checkpoint) and **before any construction**:

1. compute the set of Wire uids on diagram 0 that **no owning-node terminal reads at either end**, from the
   recipe's own `sweep()` (OpNodeTerms) plus `gscript.uids(target, "Wire")`;
2. **gate A0a** ??that set must be EXACTLY `{894, 1356}`; any other set prints the actual set and ABORTS that op's
   build having removed nothing;
3. **gate A0b** ??`Wire.Is Broken?` 6371004 must read True on exactly those two, via
   `diag_fstunnel_wirebroken.read_broken()` (imported, not re-implemented); on anything else it ABORTS, again
   removing nothing;
4. **gate A0c** ??`remove_bad_wires_scripted` removes exactly `[894, 1356]` and adds none;
5. **gates A0d/A0e** ??wire count 42 ??40, node-terminal count unchanged, `ExecState == 1` before construction;
6. **gate A0f** ??a static self-check that this file calls the RBW helper from exactly ONE line, so B4 is reached
   with no RBW call.

## Why (the measurements this cycle produced)

* `tools/bench/diag_fstunnel_rbwvictims.log` (18/18 gates, rc=0): the DONOR `OpWireSource_v5.vi` holds 42 wires
  and **894 + 1356 are already in the donor** (`:14`); neither touches any node terminal (`:150-160`, "END NONE";
  894 has no source terminal, 1356 a source and no sink; both report owner `TopLevelDiagram` #3); the first
  checkpoint at `_v1.py:403` already has both (`:181-183`).
* At the B4 point `remove_bad_wires_scripted` removes exactly `[894, 1356]`, adds none, 43 ??41 wires,
  `ExecState 0 ??1`, **no node loses a connection** (133 ??133 terminals, "NONE ??no terminal that was wired
  before RBW reads 0 after it"), and 1694/1719/1766 survive (`:164-172`).
* `tools/bench/diag_fstunnel_wirebroken.log` (10/10, rc=0): `Wire.Is Broken?` 6371004 = True on the residual stub
  #384 with the orphans present; False after they are removed (`diag_fstunnel_rbwvictims.log:169-170`).

## The known weakness the reviewer should attack first

Gate A0b may be **unsatisfiable**: `Wire.Is Broken?`'s only Python-reachable carrier
(`OpConnectFromWire_v0`, `docs/NAMES.md:888-897`) reads the value off a SINK TERMINAL's `Connected Wire`, ordered
after a successful `Terminal.Connect Wire` ??and an A0a orphan has no sink terminal by construction. If that is
right, `_v2` aborts at A0b on every run and removes nothing. The recipe states this limit in its own contract and
records the independent non-perturbing indicator (?? sources = broken, `docs/NAMES.md:900-905`) beside the read.

## Questions for the prior-art review

* Has a donor-copy **pre-clean** (removing the template's own bad wires before construction) already been built,
  tried, or argued against anywhere in this project?
* Is there an existing helper that reads `Wire.Is Broken?` without a sink terminal, or an existing orphan-wire
  reader, that `preclean()` is hand-rolling?
* Has "the donor `OpWireSource_v5.vi` ships with bad wires" already been measured and written down before this
  cycle ??and did any earlier recipe built from that donor already work around it?
* Does any active document contradict the claim that removing 894/1356 costs no node its connection?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-18
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??`archive/2026-09-18-status-cycle22-close.md` (latest) + the `archive/2026-09-1[678]-status-*.md` set. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.
??**USER DECISION 2026-09-18 08:53 ??"?μ튂????誘쇰뱾吏 留먭퀬 怨꾩냽 吏꾪뻾".** **STANDING ORDER FOR EVERY CYCLE UNTIL THE
USER SAYS OTHERWISE: build NO further process device (gate, hook, record store, lock, launcher). A retrospective
naming one is a FINDING, not a task.** The 04:0x STOP is ANSWERED (`docs/violation-decisions.md` round-3
`DECISION: no-device`). Block verbatim ??`?쫈ycle21-wire-semantics.md` 짠6; STOP narrative ??`?쫈ycle20-close.md`.

STOP ??runner handover only (2026-09-18 12:2x): the OLD runner process exits after the current cycle so the
interactive session can restart `tools/cycle_runner.py` with the FIREFIGHTER ladder (fable low ??medium ??user;
self-test 2/2). Not a work stop; the line is removed at the restart. Sessions: ignore this line.
## START HERE
1. **Cycle plan = `docs/cycle21-plan.md`** (`docs/cycle20-plan.md` now `superseded`; P1 plan `docs/motor-limit-assurance-plan.md` **짠A.1**; master `docs/pre-rig-master-plan.md`; decisions `docs/decisions.md`; D1 `docs/d1-route-b-plan.md`, paused).
2. ?뵶 **NEVER patch a file with a `py - <<'EOF'` heredoc** ??one truncated **this file to 0 bytes** on 2026-09-17.
3. ?좑툘 `peer.ps1` only as `powershell -Command "& 'tools/peer.ps1' ??-TaskFile <f>"`, `-TimeoutSec >= 780`; **`-Dual` = FAILED-PREDICTION reviews ONLY** (CLAUDE.md:554), never `-Kind fact` / prose / ingest ??it doubles cost (opus arm ??1.86/call).
4. Six more operating hints (prior-art log naming 쨌 front panel open for edits 쨌 `guard_cycle`'s `FIXED:` release 쨌
   `py_compile` tripping BUILD_RE 쨌 짠11u unsound 쨌 짠10 not authorised): **`archive/2026-09-18-status-cycle1-census.md` 짠1**.

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:   # cycle-23 dispatch 2 (11:54-11:56, diag_fstunnel_rbwvictims, 18/18, rc=0) released it; two twin scratches deleted, handles 30,356??0,848, all 95 originals md5-identical, no original opened, nothing saved. Dispatch 1 (11:43-11:45, diag_fstunnel_wirebroken, 10/10, rc=0).
# CYCLE 22 lock lines RELOCATED VERBATIM ??archive/2026-09-18-status-cycle22-close.md 짠1 (build_opfstunnelterm_v1 RUN 1 gates 12/16 B4 ExecState 0 쨌 diag_fstunnel_orphans 8/8 쨌 the `-Dual` review, both arms now DISPOSED 쨌 handles 30,318??0,979 쨌 md5s identical BEFORE AND AFTER 쨌 no motor/serial/camera); cycle-21 ???쫈ycle21-wire-semantics.md 짠8/짠9/짠9a, cycle-20 ???쫈ycle20-close.md.
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
?넅 **SAFE MOTION ENVELOPE (user, 2026-09-17 ??says what is SAFE, not when motors are allowed; motors ARE allowed
while assembled INSIDE it, conditional on it being really enforced as refusing code):** ASI z free 쨌 ASI x/y
**never home/origin, ??.0 mm from `tools/bench/motor_anchor.json`** 쨌 PI magnet **0??9 mm only** (`Max Trans Pos`
= 40.94 is a **coerce** in the original and `TMX 52` ??**the controller protects nothing**; our scripts bypass the
coerce). ??`tools/motor_gate.py` = the ONE gateway, 70/70 self-test, default-deny; first live PI + ASI moves
passed; rotor transmit **NOT built** ??`archive/2026-09-17-status-motor-gate-live-moves.md`.
rig-state: 議곕┰   <!-- set 2026-09-17 23:0x on the user's words ("?ㅽ뿕 1李⑤줈 ?앸궗?붾뜲, 由ш렇???좎??섎뒗 以? + "議곕┰ ?곹깭?먯꽌????踰붿쐞 ?덉씠硫?紐⑦꽣 ?덉슜??) 쨌 the gate's ONE machine-readable key, parsed by motor_gate.rig_state(); ONLY the user's announcement may set it to 遺꾪빐 / 議곕┰ / ?ㅽ뿕以? Keep it at the start of the line, unquoted. -->

## Where things stand ??VERBATIM in `archive/2026-09-18-status-cycle22-close.md` 짠2 (cycle-20 짠1?벬? in `?쫈ycle20-close.md`; cycle-21 짠9/짠9a/짠10 in `?쫈ycle21-wire-semantics.md`; cycle 19 in `?쫈ycle19-flatseq.md`)
?뵶 **THE TUNNEL OP IS STILL UNBUILT ??verification level NONE.** B4 `ExecState 0` REPRODUCED and READ 2026-09-18 (`tools/bench/diag_fstunnel_wirebroken.log`, 10/10 gates, rc=0): `Wire.Is Broken?` 6371004 = **True on the residual stub #384** (the wire sites `_v1:476,483` share) and **False on 1694 / 1719 / 1766** (the other four sites); on a twin B4 scratch `remove_bad_wires_scripted` removed **894 + 1356 ONLY** ??neither a site wire ??and `ExecState 0 ??1` with #384 still in place. Dispatch 2 (`tools/bench/diag_fstunnel_rbwvictims.log`, 18/18, rc=0) then identified them: **894 and 1356 touch NO node terminal at all** (0 of 133 terminals; `OpWireSource_v5` gives 2 terminals each, owner `TopLevelDiagram` #3, 894 with **no source terminal**, 1356 source-only) and **both are already in the DONOR FILE `OpWireSource_v5.vi`** (42 wires) ??the template's own orphan wire objects, not created by `_v1.py`; RBW cost **no node its connection** (133??33 terminals, none unwired) and afterwards **`Is Broken?` on #384 = False**, ExecState 1, 1694/1719/1766 intact. What follows is judgement's call, not measured here.
**THE GAP stands: 174 ops, 123 recipes, 235+ peers ??zero runnable experimental VIs.**

## OPEN ??**items 1??0 VERBATIM in `archive/2026-09-17-status-runner-build.md` 짠2**; only the live ones below
32. ?뵶?뵶 **outcome review: six `OUTCOME-VIOLATION`s, SECOND consecutive ??the work stops for a re-plan with the USER.** Not answerable by a device. Stands above everything else here.
38/39/41. ?뵶 D1 route-B run 3 changed NOTHING (63 WIRED / 0 FAILED / 3 NO-ROUTE, ExecState 0), `SR_QUEUE_AUTHORISED`/`TEMP_SINK_AUTHORISED` = False ??**`docs/d1-route-b-plan.md` 짠11/짠11a**, archive 짠3 쨌 `VI.Get Errors` 452 NOT built (prior-art stopped it, `docs/d1-build-plan.md:859-860`; 짠10 NOT AUTHORISED) 쨌 **judgement only ??the stall watchdog's liveness test**, both arms ANSWERED and REFUSING "false positive", remedy not built (`archive/peer/2026-09-17-stall-preexperiment-sleep-{codex,opus}.md`).
42/43/46/47. **VERBATIM in `archive/2026-09-18-status-cycle20-open-items.md`** ??42 ?좑툘 39 undisposed reviews + `audit_cycle` A2/A3 SELF-REFERENTIAL, not fixed 쨌 43 ??`guard_cycle.fixed_claim()` FIXED (step 1, T1?밫6 + B1/B2) 쨌 46 ?좑툘 `SetCommand_signed.vi` is on NO disk 쨌 **47 ?뵶 JUDGEMENT: the audit A1/A2/A3 remedy is NOT a `logclass` entry; opus reads `device-failed`, threshold 1.**
48/48a/49/50. ??**ALL FOUR CLOSED** (48 recipe released+rewritten and gate-armed as `_v1` 쨌 49 `-Dual` review archived AND both arms disposed 쨌 50 fixed) ??the four items VERBATIM in `archive/2026-09-18-status-cycle22-close.md` 짠3, bodies in `archive/2026-09-18-status-cycle21-wire-semantics.md` 짠5 + `archive/2026-09-18-status-cycle20-open48.md`.

## NEXT
?뵶 **START HERE: run the reader, do not re-guess.** One action first, nothing to re-derive ??**read
`Wire.Is Broken?` 6371004 (BUILT and measured, `docs/NAMES.md:888-897`) on the six wire sites of
`tools/recipes/build_opfstunnelterm_v1.py` (`:431,438,441,444,449,452`) AND on the residual stub wire #384 on the
cast output**, on a scratch copy at the B4 point. Both arms of the `-Dual` review
(`archive/peer/2026-09-18-fstunnel-v1-b4-execstate0-{codex,opus}.md`, ANSWERED, disposed, ACCEPTED) name this as the
cheapest discriminating test, and it needs no new tool. It separates the two live explanations of B4 `ExecState 0`:
a broken wire among the six / #384 itself (opus ranks the un-deleted stub first) versus a cause elsewhere ??for
which the next reader is codex's "open the existing Error List at B4 on the scratch", NOT another inference.
**Do not re-run `build_opfstunnelterm_v1.py` before that read** ??the build is deterministic and run 1
(`tools/bench/build_opfstunnelterm_v1_run1.log`) already holds everything a repeat would produce.

?좑툘 **ANY edit to `_v1.py` BRICKS its path exactly as `_v0.py` is bricked.** `stop_record._check:325` refuses on the
FIRST matching record and `stop_record.py` has no supersede/clear verb, so a released recipe's bytes are the only
bytes that path can ever launch (it then refuses even `grep`/`cp`/`py_compile` naming it). The route that works, and
the one cycle 22 used ??**no gate edit, no `CYCLE_GUARD_OFF`** ??is: copy to the next `_vN` (the existing
`build_opconnectnested_v0/_v1` convention), then `py tools/stop_record.py write --recipe <new> --review <the review
that read those bytes> --verdict <its slugs>`, and the gate stamps the release itself on first check. Details +
two other harness frictions: `docs/toolkit-capabilities.md:569-582`.

**Then** `docs/cycle21-plan.md` (still `status: current`, its `## Pre-decided` unchanged ??no new plan file was
written on purpose, since its step 2 is what is unfinished): prove step 2's three done-whens ??the live
terminal+owner read; the fixture `LoopTunnel #28343 ??Max Trans Pos.vi 쨌 Magnet position output` **through the new
op**; the d10 uid-44036 walk crossing ?? FSIT with its hop count ??plus the two bad-input refusals (Pre-decided 3).
**None of the four has run yet: verification level of the tunnel op is NONE.** Step 3 (check A,
`docs/motor-limit-assurance-plan.md` 짠A.1, in 짠A.1's own order) only after step 2 closes; 짠A.1 is SETTLED ??do not
redesign it or re-open its release. P1 holds: no motor moves, no motor port opened for writing.

**Cycle 22 settled these, so do not re-litigate them:** the `:392` count failure WAS `gscript.wire`'s false negative
(all six sites now pass by effect ??`?쫣1_run1.log:57-68`) 쨌 the unwired-donor-sink explanation is DEAD (the FRESH
donor reads `ExecState 1` with those same sinks at wire 0, `tools/bench/diag_fstunnel_orphans.log:20-21,63-64`) 쨌
the per-site ExecState attributor added this cycle is **VACUOUS** in this recipe (`ExecState BEFORE = 0` at all six
sites) and is superseded by the `Wire.Is Broken?` read ??it is not defended 쨌 `VI.Get Errors` 452 is off the
critical path (probably unreachable over our COM path; `CLAUDE.md:345-346` corrected).

?뵶 **THE RUNNER'S ORDERS (user, 2026-09-17 23:4x): "紐⑦꽣 ?묐룞 泥댄겕 ?꾧퉴吏??紐⑤뱺 ?몄뀡 ?뚮젮蹂?寃? ?댄썑 ?닿? ?먮━??
?덈뒗 ?곹솴?먯꽌 紐⑦꽣 ?곹븳 ?섑븳 泥댄겕 寃利? ?댄썑 ?섎㉧吏???섎꽕??猷⑦봽 ?????덈룄濡?.** **P1's exit condition ??"P1 ENDS
when the only work left needs a real motor or the user" ??is MET.** P1 leaves 짠D's checker
`.claude/agents/motor-limit-checker.md` WRITTEN but its tools, the hash-record gate, the record-write hook and the
broken-VI proof **NOT BUILT**. **P2 (USER PRESENT): live limit verification. P3: the user restarts the runner.**
**No motor moved and no motor port was opened for writing in cycle 20.** `docs/cycle15-plan.md` stays `paused`;
D1/route-B: `archive/2026-09-18-status-cycle1-census.md` 짠4. ?좑툘 `prior_art_review` REFUSES without `--recipe`; a
non-`novel` verdict arms the launch gate; `CYCLE_GUARD_OFF` is never the answer.

## Where to look ??`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** 쨌 **`docs/motor-call-site-census.md`** (P1) 쨌 **`docs/d1-route-b-plan.md`** = the build order 쨌 `tools/recipes/build_d1_routeb_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Write is disabled this session, as in the 2026-09-17 and 2026-09-18 prior-art dispatches — so the review above is the deliverable in full, which is what `peer.ps1` archives.

**Summary for the judgement session:** 4 findings, 0 `novel`, so the launch gate arms against `tools/recipes/build_opfstunnelterm_v2.py`. The load-bearing one is A1 — gate A0b asks for a value `docs/NAMES.md:908-911` already records as having *no measured route* for an orphan wire, and the recipe's own `sink_terms_of`/`orphan_is_broken` reach the same dead end in code, so the build aborts before its RBW call on every run. A3 is the same gate seen from inside the file: A0g refuses the `Is Broken?` reader on the success path and A0b puts it there. B4 asks whether the clean belongs at the front at all, since the copy already reads `ExecState 1` with both orphans present and the only measured 0 → 1 is the end-of-build RBW that A0f forbids. B4b is the citation layer: the "END NONE" evidence is a two-wire read taken at the B4 state, and the line anchors used for it in the recipe, `docs/toolkit-capabilities.md:591,594` and `docs/NAMES.md:911` point at other lines.

## Sources

(extract from answer)

## What was done with it

disposition: RELAYED TO JUDGEMENT, NOT ACTED ON (cycle 23, dispatch 3, material session, 2026-09-18 12:2x).

- **Outcome classified:** `ANSWERED` in 424 s, opus / effort high, `COST: $4.7805  in 36 / out 27004 /
  cache-create 281747 / cache-read 2575428  (422s, 28 turn(s))` —
  `tools/bench/priorart_fstunnel-v2-preclean.log:3-4`.
- **The review's own summary says "4 findings, 0 `novel`", but the archived text carries NO machine-readable
  `PRIOR-ART: <slug>` line** (the only three in this file are the QUESTION's template, lines 41–43), and the cell
  itself notes "Write is disabled this session". So `prior_art_review.py` reported
  `STOP RECORD: none - 2026-09-18-priorart-fstunnel-v2-preclean.md carries no blocking verdict`
  (`…priorart_fstunnel-v2-preclean.log:10`) — **the launch gate was NOT armed**, which contradicts this review's
  own sentence "the launch gate arms against `tools/recipes/build_opfstunnelterm_v2.py`". Recorded as a fact; not
  repaired here, and NOT worked around.
- **No release line was written and `stop_record write` was NOT run** — both are the judgement session's call
  (cycle-23 brief, Pre-decided 4). `tools/recipes/build_opfstunnelterm_v2.py` remains WRITTEN AND NOT RUN.
### Dispositions decided by the cycle-23 judgement session and applied 2026-09-18 (dispatch 4, material)

**A1 — ACCEPTED.** Gate A0b is **deleted** from `tools/recipes/build_opfstunnelterm_v2.py`, and so is every line
that existed only to serve it: `orphan_is_broken()`, `sink_terms_of()`, the `CFW` / `CFW_LABELS` constants and the
`diag_fstunnel_wirebroken` import. The reviewer's point is the whole reason: `Wire.Is Broken?` 6371004 has its only
Python-reachable carrier in `OpConnectFromWire_v0`, which reads the value off a SINK TERMINAL's `Connected Wire`
after a successful `Terminal.Connect Wire`, and an A0a orphan has no sink terminal by construction — so the gate
could only ever abort the build. The identity check is now carried by A0a (the orphan set itself) plus A0c (RBW's
own removed-list); no replacement gate was added. See `tools/recipes/build_opfstunnelterm_v2.py:109` (the contract
entry recording the deletion), `:231` (the deleted constants), `:457` (the reuse note) and `:509` (where the gate
used to sit inside `preclean`).

**A3 — ACCEPTED, and resolved by the same deletion.** A3 was A1 seen from inside the file: A0g refuses the
`Is Broken?` reader on the success path while A0b put it there. With A0b gone the file no longer reads the property
anywhere, so the contradiction is gone. A0g itself is unchanged.

**B4b — ACCEPTED, and already corrected.** The stale line anchors the reviewer named
(`docs/toolkit-capabilities.md:591,594` and `docs/NAMES.md:911`) no longer occur anywhere in
`tools/recipes/build_opfstunnelterm_v2.py`; the "END NONE" evidence is now cited as
`tools/bench/diag_fstunnel_rbwvictims.log:80,86`, which `grep -n` confirms are the two
"END  NONE - no terminal of any diagram-0 node reads this wire uid" lines (`:80` for wire 894, `:86` for 1356).

**B4 — ANSWERED BY MEASUREMENT, not by argument.** B4 asked whether the clean belongs at the front at all, since
the fresh copy already reads `ExecState 1` with both orphans present. Cycle 23 dispatch 4 measured it on two twins
frozen at the recipe's B4 point: `tools/bench/diag_fstunnel_preclean_twins.log` (11/14 gates, `BGRUN END rc=1`)
and `tools/bench/diag_fstunnel_orphan_timeline.log`. The measurement went against the recipe's own A0a premise —
at the `_v1.py:403` checkpoint the orphan set is **EMPTY**, not `{894, 1356}` ("PRECLEAN @_v1.py:403: 42 wires, 111
node terminals, ExecState 1; orphan set (no owning-node terminal at either end) = []") — so the pre-clean aborted
having removed nothing, exactly as its own gate requires. The two wires are orphaned only later, at the B4 state,
where RBW still removes exactly `[894, 1356]` and `ExecState` goes 0 → 1. That failed prediction was dispatched
for refutation as a `-Dual` review (`archive/peer/2026-09-18-fstunnel-orphans-empty-at-ckpt00-{codex,opus}.md`).
What follows for A0a — and therefore for whether `_v2` can run at all — is the judgement session's call and is
**left open here**. A0e was demoted in the same edit from an assertion to a recorded observation
(`tools/recipes/build_opfstunnelterm_v2.py:121`, `:534`), since the fresh copy reads 1 with the orphans present and
the number cannot discriminate; the contract now states that the build's real separator is the B4 reading.

FIXED: settled-already - `tools/recipes/build_opfstunnelterm_v2.py`:109 - gate A0b, the finding's subject, is deleted from the recipe together with every line that existed only to serve it.

- **The four findings, relayed verbatim in the material session's return** (A1: gate A0b asks for a value
  `docs/NAMES.md:908-911` records as having no measured route for an orphan wire · A3: A0g refuses the `Is Broken?`
  reader on the success path while A0b puts it there · B4: whether the clean belongs at the front at all, since the
  copy already reads `ExecState 1` with both orphans present · B4b: the line anchors
  `docs/toolkit-capabilities.md:591,594` and `docs/NAMES.md:911` point at other lines). Whether each is accepted,
  refuted or changes the recipe is a judgement decision and is left open here.
