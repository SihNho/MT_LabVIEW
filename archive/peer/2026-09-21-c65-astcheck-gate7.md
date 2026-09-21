# c65-astcheck-gate7

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $4.5524  in 38 / out 45593 / cache-create 211974 / cache-read 2467692  (562s, 34 turn(s))
- **date:** 2026-09-21 15:09:36
- **outcome:** ANSWERED (564s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# ATTACK this claim. Do not confirm it.

## The record

`tools/bench/c65_astcheck.log` is the static gate on a build script that has not been launched yet. It ran
`tools/bench/c60c_astcheck.py` over that script and came back **11 of 12 PASS, 1 FAIL**:

```
FAIL  7 move_in is neither imported nor called  called=True imported=True
=== ASTCHECK FAILED; failing: 7 move_in is neither imported nor called
```

`c60c_astcheck.py:99-101` is that check, verbatim:

```python
gate("7 move_in is neither imported nor called",
     "move_in" not in called and "move_in" not in imported, ...)
```

The build script under the gate mandates `move_in` at its step 3: an object created by one helper lands on
the top-level diagram and is then relocated onto a nested diagram before it can be joined to a terminal
that lives there.

**This is the THIRD consecutive cycle in which this exact line is the first failing gate line.** The same
normalised line appears at `tools/bench/c62f_astcheck.log:11`, `tools/bench/c64e_astcheck.log:11`, and now
`tools/bench/c65_astcheck.log:11`. `tools/cycle_runner.py:253` builds its repeated-failure signature from
precisely "the first failing GATE line of the run, normalised, uids dropped, lower-cased, 60 chars", and
`tools/bench/cycle_runner.log:97` already carries `gate:fail 7 move_in is neither imported nor called
called=true im` for an earlier cycle. Under this project's rules, the same first-failing gate line in two
consecutive cycles converts the next cycle to a different, cheaper model; a third conversion stops the
runner and asks the human.

**What changed since the last time this was reviewed.** The previous cycle ran the same route to completion
and it WORKED. Two files are on disk, both carrying the edits, and the final one re-opens cold, in a freshly
restarted LabVIEW, at execution state 1, with an ordered not-broken read on the new wire, 51 checks passed
and 1 failed (that one failure was a mis-written expectation, separately reviewed and settled). The
relocation step ran inside that success. So `move_in` is no longer a step whose safety is unknown; it is a
step that has shipped an artefact.

**What has NOT changed.** The previous review of this same gate failure
(`archive/peer/2026-09-21-c64-astcheck-gate7-movein.md`) argued something I am not disputing and do not want
re-argued: that "what scripting creates lands on the top-level diagram and must be moved in" is a property
of how the creating helper was WIRED, not a law of LabVIEW — `New VI Object` takes an `owner refnum`, and
this fleet's own `build_invoke` / `build_property` already expose a `diagram_index`. Its falsification test
(set the creating helper's second navigation pair to the destination diagram and see whether the object is
born there) is UNRUN. Its other discriminating test — running `c60c_astcheck.py` against a script that is
known to have built the WRONG thing, predicting 12/12 PASS — is also UNRUN, because the gate's own failure
now blocks every command that would run it.

## THE CLAIM YOU MUST TRY TO DESTROY

"Gate 7 fails BY CONSTRUCTION and reports nothing about this script's correctness. It encodes a prohibition
written for a different cycle, the route it forbids has since shipped a working artefact, and the right
handling is to report the failure verbatim, leave the gate file untouched, and run the build. Repeating the
same failing line for a third cycle is a cosmetic accounting artefact, not a signal that the work is going
wrong."

## Already ruled out (do not spend your answer on these)

- "Edit the gate, rename the argument, alias the call, or set the override env var": all four are forbidden
  here and none is under consideration. The question is only whether the failure MEANS anything.
- "The relocation is avoidable in principle": granted, and argued in the prior review. I am asking whether
  it should be avoided NOW, in this script, given the artefact that already shipped through it.
- "The other 11 gates passing is reassurance": the prior review already attacked that and I am not leaning
  on it.

## What I want back

1. The strongest reason the claim is WRONG — in particular, any reading in which a THIRD identical failing
   gate line is genuine evidence that this route is the wrong route, and not an accounting artefact.
2. A DIFFERENT explanation of why this line keeps recurring that I have not considered.
3. What observation would falsify the claim.
4. The cheapest discriminating test that separates your explanation from mine — runnable, not an argument.
   It must be READ-ONLY with respect to every pre-existing `.vi` file.

Answer one thing directly: when a static gate encodes a prohibition that a LATER, SUCCEEDING build
deliberately violates, is the correct repair to (a) retire the gate, (b) parameterise it so the brief
declares which route it is on, (c) leave it failing forever as a standing reminder, or (d) something else?
Say which, and say what it costs when the same line is also the machine's repeated-failure signal.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Two of the brief's load-bearing statements are false, and the files that refute them have been on disk for hours.** The claim's first half is now *measured* true — and that measurement destroys its second half.

---

## 0. The brief's premises, checked

The brief rests on *"Its falsification test … is UNRUN"* and *"running `c60c_astcheck.py` against a script known to have built the WRONG thing, predicting 12/12 PASS — is also UNRUN, because the gate's own failure now blocks every command that would run it."*

| the "unrun" test | where its answer already is | when |
|---|---|---|
| `c60c_astcheck.py` vs. the known-wrong script | `tools/bench/c62e_astcheck.log` — `BGRUN START … c60c_astcheck.py diag_c62_s3b_build.py`, `:11 PASS 7 …`, `:15 === ASTCHECK OK`, `:16 BGRUN END rc=0` | **2026-09-21 10:41:40** |
| does `OpCreateLocalRead_v0` carry a second navigation pair? | `tools/bench/diag_c64_s3b_row1.log:129` — `… (2, 'Class Name 2', False), … (6, 'index 2', False) …` | inside the run that "shipped the artefact" |

`c62e_astcheck.log` predates the previous review's dispatch (13:57:51) by **3 h 16 min**. That review predicted 12/12 PASS as its cheapest test; the machine had already returned 12/12 PASS. The c64 material session then wrote into the archive (`archive/peer/2026-09-21-c64-astcheck-gate7-movein.md:197-204`) *"THE REVIEW'S OWN DISCRIMINATING TEST WAS NOT RUN … it is unrun and outstanding."* And that same archive's disposition (`:209-213`) **told this cycle where the second answer was** — "the judgement session can see from `tools/bench/diag_c64_s3b_row1.log` whether a second `Class Name`/`index` pair exists without spending another COM read."

Precision: `:129` proves the pair **exists**. It does not prove it is an *owner*. Setting `Class Name 2 = "Diagram"` / `index 2 = <live #639>` and censusing where the Local lands is still genuinely unrun. Half that question is answered from disk; half is not.

---

## 1. The single strongest reason the claim is WRONG

`c62e_astcheck.log` does not support "report verbatim and run the build" — it destroys it.

That clean 12/12 was on `diag_c62_s3b_build.py`, the one script the plan itself records as having built the wrong artefact: `docs/cycle27-plan.md:2474-2480` — Local on `TopLevelDiagram #536`, a tunnelled cross-diagram path, `wire_delta` **3**, two different wire uids, `ExecState` **0**. The gate stamped it `=== ASTCHECK OK`.

The correct inference is *"a verdict from this file means nothing, in either direction."* The claim takes the same measurement and infers *"therefore proceed, reporting the FAIL verbatim"* — which quietly keeps the eleven PASSes in frame as the thing being reported *around*. `diag_c65_s3b_row2.py:46` says it outright: **"Every OTHER gate of c60c_astcheck must be OK."** That is a pass criterion, and `c62e` is the proof it is empty. You cannot cite the measurement to excuse the FAIL and then bank the PASSes it invalidates.

Concretely, the script's real prohibitions — no `g.open_panel`, no `g.ensure_loaded`, row 2 only, `move_in` at most once — live in a **docstring** (`:31-46`). Prose assertions are exactly what a static gate exists to replace. "Run it, the gate is noise" ships this build with *no static gate at all*, while the log reads as though eleven checks guarded it.

---

## 2. Is a THIRD identical line genuine evidence? Yes — mechanically

**2a. Gate 7 is not "always failing."** Across every astcheck log: `c60d`, `c60e`, `c61`, `c62b`, `c62c`, `c62e`, `c64d` all **PASS** (`called=False imported=False`); only `c62f`, `c64e`, `c65` **FAIL**. Seven passes and three failures *inside the same two runner cycles*. It is a working conditional that fires exactly when a script takes the `move_in` route — probes pass, deliverable builds fail. "A prohibition written for a different cycle" is hard to sustain when scripts in the *same* cycle were still honouring it.

**2b. The recurrence is the sole cause of a firefighter trigger.** `cycle_runner.py:417-420` — `common = fail_hist[-2] & fail_hist[-1]; ff_recipe = sorted(common)[0]`. Cycle 49 (`cycle_runner.log:97`) has six signatures; cycle 50 (`:100`) has three. **Their intersection is a singleton, and it is gate 7.** Strike that term and the intersection is **empty** — no firefighter is armed at all. That is the opposite of cosmetic: it is the one term that manufactures a trigger out of two cycles sharing no repeated failure. (`c60c_astcheck.py` is not on the bookkeeping exclusion list at `:244-246`, whose own comment says *"bookkeeping tools always carry a standing FAIL … never a firefighter signal."*)

**2c. It outranks real triggers, and no firefighter can clear it.** `sorted()` is by code point; the character after `gate:fail ` is `'7'` (0x37), below every lowercase letter — so against `gate:fail a_4 …`, `gate:fail k2 …`, `gate:fail vx …` (all real, all in those cycles) gate 7 wins selection and the genuine failure is not chosen. And `FF_PROMPT` (`:199-213`) sends a fable cycle to "clear THAT block", tested by `ff_recipe in fails` (`:464`) — while the brief mandates `move_in` the line reappears, so rung 1 fails, rung 2 fails, and `:470-475` returns `RUNNER STOP`. This runner has already been hand-aborted for false firefighter triggers **twice** (`cycle_runner.log:64`, `:89`).

**2d. And the brief's arithmetic is wrong in the *other* direction.** `cycle_runner.py:380` — `fail_hist = []`, in-process, never persisted. `cycle_runner.log:101`: the runner was **restarted at 14:43:11**; `c65_astcheck.log` is stamped **14:56:38**, inside the first cycle of the *new* runner. So the firefighter that 49 ∩ 50 had armed was silently discarded and never fired; the current occurrence is `fail_hist[0]`, not strike three; the escalation the brief fears **cannot happen now**, and a false firefighter nobody is watching for is being set up two cycles hence. Neither the claim nor the brief has the machine's state right.

**2e. Price.** Each recurrence buys a `guard_peer.py` block and an opus/max review — the last cost **$4.0461** (`…-c64-astcheck-gate7-movein.md:7`) to re-derive what sat in `c62e_astcheck.log`. This is the second. A "standing reminder" levying $4/cycle that never closes is a subscription.

---

## 3. A DIFFERENT explanation

Not staleness, not a wrong route, not accounting. **This project measures the answer and then loses it.**

`c62e_astcheck.log` (decisive, never read) → `diag_c64_s3b_row1.log:129` (printed on purpose, never read) → an archive that records both as "unrun and outstanding" and **invents a cause for it** ("the gate's own failure now blocks every command that would run it"). The recurrence is a **retrieval failure**: the question is re-asked each cycle because the archive says it's open, and the archive says it's open because nobody greps `tools/bench/` before dispatching. Under this project's own slugs that is `unreported-fact` + `inference-over-measurement` — and a causal story invented to explain a non-event is exactly what "absence in what you happen to be looking at is not evidence of absence" is written against.

*Secondary:* `c60c_astcheck.py:3-4` says it is "the predecessor's gate with its checks KEPT, **re-aimed**." Every re-aim carried gate 7 forward unexamined — and gate 9 too, whose `FORBIDDEN_ROUTES` (`:29`) still bans `build_invoke`, the one verb that creates on a chosen diagram (`gscript.py:2159`). Gate 7 forbids moving it in; gate 9 forbids creating it there. The cause is a copy-and-re-aim habit, not a judgement about `move_in`.

---

## 4. What would FALSIFY the claim

- **(a) — already paid for.** `c62e_astcheck.log`. Anything but a clean pass would have killed "reports nothing about correctness." It returned `=== ASTCHECK OK` — so that half stands as *measured*, and the operative half falls per §1.
- **(b)** — if removing gate 7 from 49 ∩ 50 leaves a non-empty intersection, "cosmetic" survives.
- **(c)** — a firefighter actually fires on `gate:fail 7 move_in …`. Impossible next cycle (`fail_hist` reset); live two cycles on.
- **(d)** — the owner-pair *semantics*. If the Local is born on `#639`, gate 7 was never stale, it was **correct**, and the framing inverts. The external record favours gate 7 here: NI documents `New VI Object`'s **owner refnum**, and that a substructure (loop, Case) **owns objects residing within it** — creation into a nested diagram is the documented mechanism, not an exotic one.

**What the evidence does not settle:** nothing here distinguishes "gate 7 is stale" from "gate 7 is correct and keeps being overridden." Both emit byte-identical log lines. Only (d) separates them, and (d) is the one test genuinely unrun. `c62e` says the gate cannot judge a script; it says nothing about LabVIEW.

---

## 5. Cheapest discriminating test — read-only, <1 s, no COM, no `.vi`

```
py -c "import re;S={};
[S.setdefault(m.group(1),set()).update(x.strip() for x in m.group(2).split(', ')) for m in (re.match(r'FAILED-RECIPES cycle (\d+): (.*)',l) for l in open('tools/bench/cycle_runner.log',encoding='utf-8',errors='replace')) if m];
c=S['49']&S['50'];d={x for x in c if 'move_in' not in x};
print('WITH    gate7:',sorted(c),'-> target',(sorted(c) or [None])[0]);
print('WITHOUT gate7:',sorted(d),'-> target',(sorted(d) or [None])[0])"
```

Replays `cycle_runner.py:417-420` from the runner's own written output, avoiding `failed_recipes()`'s one side effect (it writes `cycle_runner_retro_seen.json`, `:280-292`).

| | claim predicts | I predict |
|---|---|---|
| `WITH gate7` | one line among several | **singleton** = `gate:fail 7 move_in …` |
| `WITHOUT gate7` | still non-empty | **empty** — no trigger exists |

Non-empty ⇒ "cosmetic" is defensible and I am wrong. Empty ⇒ gate 7 is not an artefact beside the signal, it **is** the signal, and it is false.

**Second test, costing nothing:** open `c62e_astcheck.log` and `diag_c64_s3b_row1.log:129`.

---

## 6. (a) retire, (b) parameterise, (c) leave failing, or (d)?

**(b) — but not yet. And (c) is actively harmful.**

- **Not (a):** retiring gate 7 discards the only record that two mutually exclusive routes exist and were never chosen between — and fixes nothing, since gate 9 independently makes the file unsatisfiable.
- **Not (c):** this is the current de-facto policy and the worst option *precisely because the line is also the machine's signal*. It manufactures a trigger from an empty intersection, **outranks** genuine triggers, cannot be cleared by the mechanism it fires, walks the ladder to `RUNNER STOP`, and blocks each cycle's build at ~$4/recurrence.
- **(b):** the gate already takes its target as `sys.argv[1]` (`:26`). Add the *route* — `--route movein|owner` — so gate 7 becomes "on `owner`, `move_in` absent; on `movein`, `move_in` called **at most once**" (a shape already written: `c57d4_astcheck.log:13`), with gate 9's list flipping symmetrically. Not silencing: the check survives on the other branch, and a script claiming `--route owner` while calling `move_in` still fails.
- **Ordering matters:** parameterising *before* §5's replay, `c62e`, and the one owner-pair COM read encodes the disagreement instead of resolving it.
- **The (d) nobody named:** the firefighter trigger is separately broken — *a firefighter must not be selected by a signature no firefighter can clear*. But the fix is **not** adding `astcheck` to the exclusion list (§2a shows real astcheck failures are informative and would be suppressed). Route-parameterisation is the fix for both: once gate 7 stops emitting on the adopted route, the poisoned signature stops entering `fail_hist` and the runner coupling dissolves.

---

**Sources:** [NI — Adding an Object to a VI Using VI Scripting](https://www.ni.com/docs/en-US/bundle/labview/page/tutorial-adding-an-object-to-a-vi-using-vi-scripting.html) · [NI — Obtaining References to Objects in a Known Target VI](https://www.ni.com/docs/en-MY/bundle/labview/page/obtaining-references-to-objects-in-a-known-target-vi-using-vi-scripting.html) · [NI — GObject: Move](https://www.ni.com/docs/en-NR/bundle/labview-api-ref/page/properties-and-methods/vi-server/generic/gobject/move.html) · [LabVIEW Wiki — GObject Move method](https://labviewwiki.org/wiki/GObject_class/Move_method) ("LabVIEW makes a copy … instead of moving" — the `D3` gate at `diag_c65_s3b_row2.py:869` already checks for this, correctly) · [NI — Repositioning an Object Using VI Scripting](https://www.ni.com/docs/en-US/bundle/labview/page/tutorial-repositioning-an-object-in-a-vi-using-vi-scripting.html)

**Local:** `tools/bench/c62e_astcheck.log` · `c65_astcheck.log:11` · `c62f_astcheck.log:11` · `c64e_astcheck.log:11` · `diag_c64_s3b_row1.log:129` · `cycle_runner.log:64,89,97,100,101` · `tools/cycle_runner.py:243-259,380,417-420,464-475` · `tools/bench/c60c_astcheck.py:3-4,26,29,99-101` · `tools/hooks/guard_peer.py:51,161,219-244` · `docs/cycle27-plan.md:2473-2482` · `archive/peer/2026-09-21-c64-astcheck-gate7-movein.md:7,197-213` · `tools/bench/diag_c65_s3b_row2.py:31-46,46,869`

*(Note: the `Write` tool is disabled in this session, so this review exists only as this text — nothing was written to disk, no lock taken, no VI touched.)*

## Sources

(extract from answer)

## What was done with it

The SECOND and last review of cycle 65 material #1 part A (the brief caps this dispatch at two). It was
forced because clearing the first gate re-armed `guard_peer` on a DIFFERENT log: after
`tools/bench/c65_astcheck.log` was written, the hook's refusal read, verbatim,
`latest failing log : tools\bench\c65_astcheck.log` / `first failure line : FAIL  7 move_in is neither
imported nor called  called=True imported=True`. Outcome classified from the dispatcher's own line:
**ANSWERED (564 s)**, agent `claude`, role `hypothesis`, opus / effort max, `$4.5524`, log
`tools/bench/peer_c65_gate7.log` (`BGRUN END rc=0 after 564s`), task `tools/bench/peer_c65_gate7_task.md`.

**IT REFUTED MY BRIEF AT ITS PREMISES, AND I CONFIRMED BOTH REFUTATIONS OFF DISK BEFORE ACCEPTING THEM:**

1. My task file said the prior review's discriminating test was UNRUN. **It was run, hours earlier.**
   `tools/bench/c62e_astcheck.log:1` = `BGRUN START 2026-09-21 10:41:40 ... c60c_astcheck.py
   diag_c62_s3b_build.py`, `:11` `PASS  7 move_in is neither imported nor called  called=False
   imported=False`, `:15` `=== ASTCHECK OK`, `:16` `BGRUN END rc=0 after 0s`. The gate handed a clean
   **12/12** to the one script this plan records as having built the WRONG artefact.
2. My task file said the donor's second-navigation-pair question was UNRUN. **Half of it was answered inside
   the run that shipped row 1.** `tools/bench/diag_c64_s3b_row1.log:129` prints
   `OpCreateLocalRead_v0 front-panel labels READ OFF THE MACHINE: [(0,'vi path'), (1,'Class Name'),
   (2,'Class Name 2'), (3,'Names'), (4,'Names 2'), (5,'index'), (6,'index 2'), (7,'error out'), (8,'Text'),
   (9,'Indicator'), (10,'Write?')]`. The pair EXISTS. The review is precise that this does not prove it is
   an OWNER — that half is still genuinely unrun.
3. **I ran its §5 discriminating test** (read-only, no LabVIEW, no COM, no `.vi`; replayed from
   `tools/bench/cycle_runner.log:97` and `:100` rather than through `failed_recipes()`, whose side effect
   writes `cycle_runner_retro_seen.json`). **Its prediction is CONFIRMED:**
   - cycle 49 carries 6 signatures, cycle 50 carries 3;
   - `WITH gate7` the intersection is a **SINGLETON** — `gate:fail 7 move_in is neither imported nor called
     called=true im`;
   - `WITHOUT gate7` the intersection is **EMPTY**.
   So gate 7 is not an artefact sitting beside the firefighter signal: on those two cycles it **is** the
   signal, and it manufactures a trigger out of two cycles that share no real repeated failure.
4. Its §2d is also confirmed: `tools/bench/cycle_runner.log:101` reads `RUNNER NOTE | 2026-09-21 14:43:11 |
   runner swapped between cycles by the interactive chat`, and `cycle_runner.py:380` keeps `fail_hist` in
   process, so `c65_astcheck.log` (14:56:38) is `fail_hist[0]` of the NEW runner. The escalation my task
   file worried about cannot fire next cycle; a false one is being set up two cycles out instead.

**Implemented — the only change that is mechanical and touches neither the route nor the gate file:** the
docstring of `tools/bench/diag_c65_s3b_row2.py` carried "Every OTHER gate of c60c_astcheck must be OK". The
review's §1 shows that is an EMPTY pass criterion, and `c62e_astcheck.log` is the proof. That sentence is
now replaced by a dated correction stating exactly this, so the eleven PASSes are reported as facts and are
never cited as a warrant. Nothing else in the build script changed; `move_in` stays, at exactly one call
site, because the route is settled by `docs/cycle27-plan.md` Pre-decided 55(e)/(c)/(f)/(i) + 53(d').

**RECORDED, NOT ACTED ON — every one of these is a decision this dispatch is forbidden to take:**

- **Its §6 answer, (b) parameterise `c60c_astcheck.py` with `--route movein|owner`** so gate 7 becomes
  "on `owner`, absent; on `movein`, called at most once", with gate 9's `FORBIDDEN_ROUTES` flipping
  symmetrically. This brief says in terms: do NOT edit the gate file. It is quoted under `OPEN:`.
- Its §6 observation that **gate 9 independently makes the file unsatisfiable** — it bans `build_invoke`,
  the one verb that creates on a chosen diagram (`gscript.py:2159`) — so retiring gate 7 alone would fix
  nothing. Recorded.
- Its §6 warning that **(c), the current de-facto "leave it failing" policy, is the worst option**: it
  manufactures a trigger from an empty intersection, OUTRANKS genuine triggers (`sorted()` puts `'7'`
  = 0x37 below every lowercase letter, so `a_4` / `k2` / `vx` never get selected), cannot be cleared by the
  firefighter it fires (the brief mandates `move_in`, so the line reappears and `cycle_runner.py:470-475`
  walks to `RUNNER STOP`), and costs an opus/max review per recurrence — `$4.0461` last cycle, `$4.5524`
  this one, to re-derive what `c62e_astcheck.log` already held.
- Its §4(d), **the one genuinely unrun test**: set `Class Name 2 = "Diagram"` / `index 2 = <live index of
  #639>` on `OpCreateLocalRead_v0` and census where the Local lands. If it is born on `#639`, gate 7 was
  never stale but CORRECT, and `move_in` is avoidable. NI documents `New VI Object`'s `owner refnum` and
  that a substructure owns objects residing within it, so the external record favours gate 7 here. This is
  a route change and was NOT run.
- Its §3 diagnosis of the recurrence — **a retrieval failure, not a wrong route**: the answers were
  measured (`c62e_astcheck.log`, `diag_c64_s3b_row1.log:129`), never read, and then an archive recorded them
  as "unrun and outstanding" and invented a cause ("the gate's own failure now blocks every command that
  would run it" — my sentence, in this dispatch's own task file). Under this project's slugs that is
  `unreported-fact` + `inference-over-measurement`. Recorded for the retrospective; no device built
  (the user's standing order of 2026-09-18 08:53).
- Its incidental note that the `D3` gate in `diag_c65_s3b_row2.py` correctly guards LabVIEW's documented
  "Move makes a copy instead of moving" behaviour. No change needed.

Nothing was contested. The gate file was NOT touched, no argument renamed, no call hidden from the AST, and
`CYCLE_GUARD_OFF` was never set.
