# routeb-run10-error2-class

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $5.5451  in 44 / out 43345 / cache-create 276487 / cache-read 3064901  (639s, 40 turn(s))
- **date:** 2026-09-19 07:49:02
- **outcome:** ANSWERED (641s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Attack three claims a LabVIEW VI-scripting build is about to act on. All evidence is from our own logs; cite our files back at us where we are wrong, and search externally for the LabVIEW facts.

CLAIM 1 — why run 10's save failed.
`tools/gscript.py:2056-2071`: `save(target, allow_broken=True)` calls `exec_state(target)`, and if it reads 0 it diverts to `gui_save()` (a Ctrl+S keystroke save). Our own `docs/cycle27-plan.md:151-161` (Pre-decided 14a) states, from measurement, that an `ExecState` read taken WITHOUT the original VI preloaded returns 0 for BYTE-IDENTICAL known-good files — i.e. a cold 0 measures subVI linkage, not brokenness. Run 10's log reads cold ExecState 0 at `:37` and **preloaded ExecState 1 at `:496` for the same live working copy**. We therefore claim: the working copy was NOT broken, `save()` misread linkage as brokenness, and `SaveInstrument` was never attempted.

CLAIM 2 — what `error 2` actually is. We previously believed `error 2` on `Traverse for GObjects.vi` was a cumulative memory/reference-allocation failure that builds up within one LabVIEW instance, which is why run 10 was built to save, restart LabVIEW and re-measure in a fresh instance. A census of three runs (`build_d1_routeb_v5_run8.log`, `…v6_run9.log`, `…v7_run10.log`) says:
- `report_all(Diagram)` — 21 occurrences across the three runs, **0 successes**, every one `error 2`.
- `report_all(Wire)` 0/1, `report_all(WhileLoop)` 0/3, `count(Node)` 0/1, `count(LoopTunnel)` 0/3 — never succeeded.
- `report_all('SubVI')` — 3 successes per run, 9/9, **the only traverse ever observed to succeed**, always early (log line 60).
- The 54 SUCCESSFUL wiring rows never call `report_all` at all: they address diagrams by INDEX through a cached per-diagram walk (`tools/recipes/build_d1_v0.py:364-372`, `wmap` → `build_track_v6_core.walk`).
- Handles are refuted as the cause: healthy at 51,334, `error 2` at 35,541 (`…run10.log:38`, `:366`).
- Precedent in our files: `report_all('GlobalVariable')` fails on this same VI with error 1092 (`docs/cycle27-plan.md:326`).
We now claim: `error 2` is **class-specific**, not temporal — VI-wide traverse of certain classes simply does not work on this VI — so restarting LabVIEW and re-measuring in a fresh instance would not have fixed the census even if the save had worked.

CLAIM 3 — the fix. Because the build already addresses diagrams by index successfully, we intend to delete every `report_all(Diagram)` / `diag_index` / `count()` call from route B's path: the survival census walks the four build diagrams by index, and the 11 wiring rows that fail (they fail only inside `diag_index`, converting a node uid to a diagram index) get a measured uid→index table instead. No save, no restart, no phasing across instances.

What we want attacked, hardest first:
(a) CLAIM 2 confuses CLASS with TIME. Every observed success is early and every failure is late, so a purely temporal explanation fits the same data. Is there a reading of this evidence under which phasing across instances is still right? What single cheap measurement separates class from time? (We think: call `report_all(Diagram)` as the FIRST operation of a run, before any edit — but tell us if that is not decisive.)
(b) What IS LabVIEW `error 2` on `VI Scripting - Traverse.lvlib:Traverse for GObjects.vi`? Search externally. Is it "Memory is full", a generic, or something class-dependent? Are there documented limits on traversing Diagram class VI-wide on a large VI, or a known-good alternative property/method for enumerating diagrams?
(c) Is CLAIM 1 wrong? Note that our `docs/cycle27-plan.md:183-189` (Pre-decided 16b) FORBIDS preloading the original inside a step that saves, because the copy can cross-link to the in-memory original's subVIs and be written that way, and warns that a preloaded ExecState 1 is "necessary, never sufficient". Given that, is there ANY sound way for us to save a mid-restructure working copy? Is calling `SaveInstrument` directly (bounded by its 300 s hard timeout) sound, or is `gscript.py:2068`'s claim that it "blocks forever" on a broken VI the safer knowledge?
(d) Under CLAIM 3, is a diagram INDEX stable enough to be the census key? `archive/peer/2026-09-19-routeb-run7-index-shift.md` measured an index shift of +1 on Diagram[24]. If indices move when objects are created, what should the census key be, given that uid→index conversion is exactly the call that does not work?
(e) A process question with a concrete artefact: in `archive/peer/2026-09-19-priorart-d1-routeb-run10.md` we released a `REFUTED: already-failed` line asserting a fact about our OWN tool's save path, from a call-site summary, without reading the callee — and the machine disproved it 30 minutes later. Read the other six release lines in that file. Does any of them rest on the same kind of unverified claim about our own code?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

# Failed-prediction review — route-B run 10

## 1. The single strongest reason the claim is wrong

**CLAIM 2's census is a selection artifact. It counted only the call sites that printed the string `error 2`, because a traverse that succeeds never prints its own call name — and your own run-10 log contains dozens of successful traverses of exactly the classes it says "never succeeded."**

| record | what it actually shows |
|---|---|
| `tools/bench/build_d1_routeb_v7_run10.log:39` | `S1 BEFORE census: {'Diagram': 170, 'Node': 626, 'Wire': 1902, 'LoopTunnel': 132, …, 'WhileLoop': 3, 'SubVI': 98, …}` — **nine successful `count()` calls**, including `count(Node)`, `count(LoopTunnel)`, `count(Wire)`, `count(Diagram)`, `count(WhileLoop)`. `tools/gscript.py:1005-1014` shows `count()` is `OP_REPORT` → the same `Traverse for GObjects.vi`. The identical line is at `build_d1_routeb_v5_run8.log:39` and `build_d1_routeb_v6_run9.log:39`. |
| `…run10.log:44` and `:69` | `PASS S1t Diagram #639 is Traverse index 43` / `Diagram#686 … is Traverse index 19`. These are `diag_index`, and `tools/recipes/build_d1_v0.py:357-358` defines `diag_index` as `report_all(target,"Diagram")`. Both succeed — and `:44` is **earlier than the first `report_all('SubVI')` at `:60`**. |
| `…run10.log:352`, `:354` | Three more `diag_index` successes ("1.2-body Diagram index 24, frame-body Diagram index 56"), **ten log lines before `:364`**, where the same call raises `error 2`. |
| `build_d1_routeb_v7.py:955`, `:1034` | ~29 more `move_in(TARGET, uid, diag_index(TARGET, body_uid), …)` calls — all passing at `…run10.log:150-167`. |

So the true record is not "0/21 for Diagram, 9/9 for SubVI." It is: **`report_all(Diagram)` succeeds on the order of thirty times, then stops working.** Both of CLAIM 2's load-bearing sentences — *"`report_all('SubVI')` … the only traverse ever observed to succeed"* and *"`count(Node)` 0/1, `count(LoopTunnel)` 0/3 — never succeeded"* — are false against `:39` and `:44`. That is a temporal/state signature, precisely the opposite of what the claim concludes.

Two smaller corrections in passing. *"The 54 successful wiring rows never call `report_all` at all"* is also wrong: `build_d1_routeb_v7.py:1237-1238`, `:1270-1274`, `:1361-1363`, `:1615`, `:1660`, `:1730-1731` all call `diag_index` inside the row loop, and `:1367` calls `report_all(TARGET,"WhileLoop")` inside `sr_queue`. And the cited precedent cuts the other way: `report_all('GlobalVariable')` failing with **1092** (`docs/cycle27-plan.md:326`) — or **109**, which is what `docs/toolkit-capabilities.md:288-290` measured for the same class name; your two documents disagree — is evidence that a *class* problem has its own distinct error code, and therefore that error 2 is **not** the class-failure mode.

## 2. Alternative explanation of the same evidence

**Leaked GObject references inside our own op VIs.** This is not my invention — it is already written down here, and CLAIM 2 does not cite it:

> `.claude/skills/labview-automation/references/com-driving.md:305-312` — *"the failure follows the **reporter**, not the file: a VI that reported fine minutes earlier now fails identically. Cause: this is the leaked-references rule coming due. Op VIs that deliberately skip `Close Reference`, plus loading large VIs and their whole dependency trees repeatedly, accumulate until the process cannot allocate."*

And `docs/REFERENCES.md:126` records an op VI built by taking the guard out: *"`Close Reference` removed."* Externally this fits: LabVIEW error 2 is the generic **"Memory is full"**, and NI's own KB for it is titled [Error 2: Memory is Full when Opening a New Reference in LabVIEW](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU); NI's [Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) states that Property/Invoke-node references must be closed because LabVIEW gives you no way to know whether it allocated a new one.

Under this mechanism `report_all(cls)` leaks one refnum per **matched** object: `Wire` 1,902 per call, `Diagram` 170, `Node` 626, `SubVI` 98, `WhileLoop` 3. That predicts exactly what you see — monotonic onset, onset earlier in runs that traverse more, and small-class calls surviving *longer* rather than being immune (`report_all(WhileLoop)` dies late at `:482`, killed by everyone else's budget, not its own).

**A second rival the evidence does not separate from it: the VI's own state.** Every mutation the build makes is monotonic in time, so "the instance degrades" and "this VI stops being traversable once it carries three new While loops, 29 moved nodes, three deleted subVIs and ~50 new wires" fit the same log identically. They differ in exactly one prediction — whether save + restart + reopen helps. A leak: yes. A VI-state cause: no, the reopened copy carries it across.

I found no documented NI limit on traversing `Diagram` VI-wide on a large VI. The only documented class-specific Traverse failure is the [Error Ring class](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513). For enumerating diagrams without a VI-wide traverse: [`AbstractDiagram.All Objects[]`](https://labviewwiki.org/wiki/AbstractDiagram_class/All_Objects()_property) returns only that diagram's **top-level** objects, so a manual recursion from `VI.Block Diagram` down through each structure's own diagram reference gives a UID-keyed tree with no VI-wide traverse anywhere.

## 3. What would falsify it

- **Falsifies CLAIM 2 (class):** any `report_all(Diagram)` success after a `report_all(Diagram)` failure in the same instance — or, symmetrically, a `report_all('SubVI')` that fails at the moment `report_all(Diagram)` is failing. Either kills "the class simply does not work on this VI."
- **Falsifies my leak alternative:** `report_all(Diagram)` called in a tight loop on the *pristine, unedited* copy in a clean instance that never fails, however many iterations.
- **Falsifies the VI-state alternative:** the same call succeeding in a fresh instance on the *reopened, fully edited* copy.

## 4. Cheapest discriminating test

**Your proposed test is not decisive, and you have already run it eight times.** "Call `report_all(Diagram)` as the FIRST operation of a run" is what `:44` already is, in every route-B log from run 2 to run 10. It can only come back green, and green at t=0 is compatible with class, leak and VI-state alike.

**Cheapest, and it costs zero extra runs:** in `gscript.report_all`/`count`'s exception path, on the *first* `error 2` only, log four things before re-raising — (a) a retry of the same call, (b) `report_all('SubVI')`, (c) `count('WhileLoop')`, (d) handles **and LabVIEW private bytes** (`com-driving.md:310` measured the threshold at ~770 MB, so the handle count was never the right meter — that refutation in CLAIM 2 is a category error, not a refutation).

- same call succeeds on retry → transient; neither class nor monotonic
- same call fails, `SubVI` succeeds → genuinely class- or size-dependent, CLAIM 2 survives
- all three fail → instance-wide exhaustion; class is irrelevant and CLAIM 3 is right

**Second cheapest, minutes and read-only, no build, no rule-1a exposure:** `for i in range(200): report_all(TARGET,'Diagram')` on the pristine copy in a clean instance, logging `i` and private bytes. Dies at some `i` with no edits ⇒ leak confirmed, a restart is a palliative (the build just dies later) and the fix is to stop traversing. Survives 200 ⇒ the cause is the edited VI's state, and **run 10's save-restart-reopen would not have fixed the 11 wiring rows even if the save had worked** — which is the answer to your (a): under that branch, phasing across instances is not right, and R3 already conceded the wiring pass keeps failing.

One measurement gap to close either way: the S3w ledger prints WIRED and FAILED as separate blocks (`…run10.log:424+` vs `:478+`), so **the order of rows is not in the log**. "Every failure is late" is currently an assumption. A monotonic row counter and timestamp per row costs one f-string.

---

## (c) Is CLAIM 1 wrong?

**The mechanism is right; the conclusion is not yours to assert.** `…run10.log:367` is `gui_save(…)` raising, so `save()` did divert and `SaveInstrument` was never attempted — that part is confirmed, not inferred. But *"the working copy was NOT broken"* is barred by your own Pre-decided 16b: the preloaded 1 at `:496` is **necessary, never sufficient**, and a preload can mask a genuine break by supplying subVIs. The defensible statement is weaker and still sufficient for the fix: **the gate was UNREAD, so the branch was chosen on a value rule 14a forbids you to interpret.**

Also worth recording: this was not the documented failure mode. `com-driving.md:497-499` says a Ctrl+S in error-2 state writes a **stale** file — *mtime moves*. Here mtime did not move at all (`gscript.py:2040`). Run 10 hit a fourth mode, and the stale-write detector the prior-art round added (`v7:2280-2284`) was never exercised.

**Is `SaveInstrument` sound?** Your skill file contains both claims, about different conditions:

- `com-driving.md:314-317` — *"`SaveInstrument` **still works in this state** (it saved a 72 KB target fine **while every traverse was failing**)"*. That is a direct measurement in run 10's exact state.
- `com-driving.md:400-405` — *"`SaveInstrument` blocks forever on a BROKEN VI … measured at 20 minutes … Killing the blocked client is safe and **let the save complete** in one observed case."*

The evidence does not settle which condition run 10 was in — that is the unreadable question. So decide on the asymmetry instead: `gscript.py:2070` already bounds it at `hard_timeout_s=300`, so the worst case of trying is a **loud** 300 s timeout (and per `:405` possibly a completed save anyway), while the worst case of `gui_save` is a **silent stale write**. `gscript.py:2068`'s "blocks forever" is therefore not the safer knowledge — it is a true observation used to justify the more dangerous branch.

Sound sequence for saving a mid-restructure copy, no preload anywhere: check `lv_gui.ps1 -Action dialogs` → `SaveInstrument` bounded at 300 s → `md5 != ORIG_MD5` → cold reopen in a fresh instance → `count(Node)`/`count(Wire)` equal the pre-save values. That last step is the only real proof, and `v7:2314-2326` already implements it. **And the honest alternative: don't save at all.** The save exists only to serve the census, and the census needs a fresh instance only if the cause is cumulative. Run the two tests in §4 before spending another 30-minute run on the save.

## (d) Is a diagram index stable enough to key the census?

**No — and your own run 10 is worse than the archived +1.** `FRAME_BODY_UID = 639` (`build_d1_routeb_v7.py:422`, commented `# "diagram 43"`) reads Traverse index **43** at `…run10.log:44` and index **56** at `:352`/`:354` — **+13, inside one instance, with no restart involved.** The archived `archive/peer/2026-09-19-routeb-run7-index-shift.md:44`, `:51`, `:111` is about *node* indices on Diagram[24], a different and much smaller effect. `v7:2351`'s "run 8 read them as 20 / 21 / 24 / 56" is a snapshot, not an identity.

The key must be the diagram **UID**. Two things that follow:

- The resolution must not be a VI-wide traverse. Read the tree downward — `VI.Block Diagram`, then per-diagram `All Objects[]` (top-level only, per the wiki), then each structure's own diagram reference — keyed by UID throughout.
- Cheap validity check you can afford today: after resolving an index, **read that diagram's UID back by index and compare**. That is one indexed read, not a traverse. If it mismatches, scan neighbours rather than re-traversing.

## (e) Do the other six release lines rest on the same kind of claim?

Yes — one does, one overstates, three hold.

- **`:492 FIXED: already-measured — v7:2396`** *"the census now resolves the four build diagrams by parked UID instead of by pre-restart index."* The resolution is `report_all(Diagram)` at `v7:2265` (pre-restart) and `v7:2328` (post-reopen) — **the fix for a traverse-blocked census is built out of the traverse that is blocking it**, on both sides of the restart. It fails *safe* (UNREAD), which is why it is not the silent error the two REFUTED lines were, but it cannot deliver the reading the round claims it restored, and the machine said so within the hour: `:369`, `parked diagram uids [567, 2063, 4972, 639, 686] -> post-restart indices [None, None, None, None, None]`. Same habit: the callee was not opened.
- **`:494 FIXED: already-built — v7:2313`** *"reuses the existing checkpoint-reopen guards from `build_gpu_kernel.py:140-148` and `finish_gpu_kernel.py:24-27` rather than adding a new mechanism."* Reading `v7:2311-2320`, it **re-implements** the idea inline and cites those files in a comment; nothing is imported. Harmless, but again described from a comment rather than from the code.
- **`:493`** checks out — `…run10.log:1` is `BGRUN START … limit 60.0 min`. **`:491`** and **`:495`** check out as written (`v7:2280-2326`, `v7:2229`), with the caveat that `:491`'s gate was never exercised.

The pattern behind `:496`, `:497` and `:492` is one sentence long: **all three are claims about what our own code does, written from a call site or a comment instead of the callee.** The prior-art gate has no rule requiring a claim about our own tools to quote the function being claimed about. That rule is one line, costs nothing, and would have caught all three.

---

## If you still believe CLAIM 2

I do not, and `…run10.log:39` and `:44` are why. What would change my mind: the retry probe in §4 returning "same call fails, `report_all('SubVI')` succeeds, `count('WhileLoop')` succeeds" at the moment of the first error 2. That would make the class reading live again, and it costs one exception handler.

**Sources:** [Error 2: Memory is Full when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU) · [Error 2 may be crossed with an internal LabVIEW error](https://forums.ni.com/t5/LabVIEW/Error-2-Memory-is-full-occurring-at-FP-Open-invoke-node-in-built/td-p/3770243) · [Closing References in LabVIEW](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) · [Traverse for GObjects fails on the Error Ring class](https://forums.ni.com/t5/LabVIEW/VI-Scripting-Error-Ring/td-p/3957513) · [AbstractDiagram All Objects() returns top-level objects only](https://labviewwiki.org/wiki/AbstractDiagram_class/All_Objects()_property) · [Scripting — reference all objects (traverse)](https://forums.ni.com/t5/LabVIEW/Scripting-Reference-all-objects-traverse/td-p/3811133)

## Sources

(extract from answer)

## What was done with it

ACCEPTED by the cycle-42 judgement session, 2026-09-19. This review discharges run 10's failed predictions
(R1/R2/R5) under `guard_peer`, and it refuted the session's own diagnosis on the session's own log lines, which is
exactly what a failed-prediction review is for.

- **CLAIM 2 WITHDRAWN.** "`report_all(Diagram)` is 0-for-21 and has never once succeeded" was a selection artefact:
  the census counted only lines that PRINT `error 2`. Recorded as `docs/cycle27-plan.md` Pre-decided 21(e).
- **The leak diagnosis is adopted** — `report_all`/`count` leaking one GObject refnum per matched object — and the
  repair (restoring the `Close Reference` recorded as removed at `docs/REFERENCES.md:126`) is ordered as run 11's
  phase 2 in STATUS `## NEXT`. It is applied unconditionally because CLAUDE.md's reference-hygiene rule requires it
  regardless of its effect on `error 2`; Pre-decided 21(c).
- **`error 2` = "Memory is full", and the meter is LabVIEW private bytes, never the handle count.** Adopted as
  Pre-decided 21(a), which names every previous handle-based refutation in this project a category error.
- **The index key is refuted** (+13 on `FRAME_BODY_UID=639` inside one instance): Pre-decided 21(d).
- **CLAIM 1 accepted with the reviewer's narrowing** — the mechanism holds, but "the copy was NOT broken" overreaches
  what Pre-decided 16b permits us to say; the defensible form is "the gate was UNREAD". Run 11 sidesteps it by
  removing the save.
- **Answer (e) acted on:** the two wrong `REFUTED:` lines carry a written `CORRECTION` at
  `archive/peer/2026-09-19-priorart-d1-routeb-run10.md:499`, and the third release line the reviewer identified as
  resting on the same unread-callee error is named there. The reviewer's proposed rule is now
  `docs/cycle27-plan.md` Pre-decided 21(f).
- **Both discriminating tests are ordered**, as run 11's phases P1 and P2.

(Claude fills in)
