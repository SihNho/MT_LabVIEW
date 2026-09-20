# d1-s2-boundary-recut

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.3597  in 16 / out 38411 / cache-create 173246 / cache-read 825035  (489s, 22 turn(s))
- **date:** 2026-09-20 02:52:37
- **outcome:** ANSWERED (492s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

Two claims about a LabVIEW VI-restructuring project. Attack both. Files cited are readable in the project directory.

BACKGROUND. We are splitting one large While-loop body of a LabVIEW VI ("the frame body", node `#637`) into additional parallel While loops connected by LabVIEW Queues. Three subVI nodes relocate into three new loops: `#5058` (CPU tracking kernel, 13 cut wires), `#376` (`save trace.vi`, 12), `#48` (`ASI_adjust focus-subvi.vi`, 7). The build is driven by our own VI-Scripting op library over COM. Ten full-length attempts (v3→v7, five cycles, ~$166) died at the re-wiring stage; the user then ordered the work split into stages that each SAVE an intermediate artefact. Stage S1 (a copy with two fixture nodes deleted) succeeded and is on disk. Stage S2 has now consumed a whole cycle without launching.

CLAIM A — a diagnosis we have just overturned, and we may have overturned it wrongly.
Our own hand-off notes and an in-code comment (`tools/recipes/build_d1_routeb_v7.py:131-135`) say the inter-loop queue ELEMENT TYPES "were never designed", and that this undesigned row is what blocks the three loops from ever getting real stop conditions. A file search contradicts that: the eight-queue element-type table (name, element, type source, bound, overload policy) is at `docs/d1-build-plan.md:544-558` §9; the stop-sentinel convention at `:565-581` §9a; it is adopted verbatim as a binding decision at `docs/cycle15-plan.md:118-123`; and a producer-consumer core using those queues was actually BUILT and logged 162/162 at `docs/stage2-assembly-step-c.md:18-30`. We now believe the "design gap" is a STALE COMMENT, not a gap, and that no new design work is owed.

CLAIM B — the replacement diagnosis, and the stage boundary we propose to adopt on it.
The real reason stage S2 cannot end with a saved VI is legality: `tools/gscript.py:2065-2071` reaches `SaveInstrument` only when `ExecState != 0`, `allow_broken=True` is banned here, and the GUI-save fallback has failed at eight logged sites. A newly created While loop whose conditional terminal is unwired is a compile-time break. Our census over all 14 already-built ops that write a diagram finds none that places a Boolean constant TRUE on a new loop's conditional terminal, and we are forbidden to build a new op. Separately, `move_in` SEVERS a node's wires — the relocated node lands unwired — so a moved node can also leave a bare Required input.
We conclude: every state between "a new While loop exists" and "its conditional terminal is wired to its real stop condition" is an unsaveable VI, so that span is ATOMIC and cannot be subdivided into saveable VI artefacts. Therefore the correct stage boundary is ONE COMPLETE LOOP PER STAGE — create the loop, move its node in, obtain its queues, wire its dequeue, build its sentinel comparison, drive the conditional terminal from it, re-wire that node's cut wires, then save — smallest loop first: `#48` (7 cut rows, 2 queues), then `#376` (12 rows), then `#5058` (13 rows).

ALREADY RULED OUT (do not propose these):
- Building a new scripting op for the conditional terminal, or any new tool/device — forbidden by a standing user order.
- Sourcing a scaffold Boolean from an existing front-panel control (measured: it delivers FALSE at load, i.e. a loop that never stops).
- `allow_broken=True`, saving a broken VI, or the GUI-save fallback.

ANSWER THESE:
1. The strongest reason CLAIM A is wrong — i.e. a reading on which the element types really are undesigned despite those four files, or on which "designed on paper" is not the thing the blocked build needed.
2. The strongest reason CLAIM B's atomicity argument is wrong. In particular: is there a route we have missed by which a newly created While loop can be made saveable — a constant TRUE, an always-true comparison such as `Equal?` fed both operands from one source, an existing Boolean net, a loop created in an already-terminated state, or a LabVIEW scripting property on the loop itself? Say what the LabVIEW/VI-Scripting facts actually are, with sources.
3. An alternative explanation for ten failed full-length attempts that neither claim captures.
4. What observation would falsify CLAIM B's "one complete loop per stage" boundary — including whether the three loops are mutually dependent in a way that forbids building one alone (note: our notes say loop `#48`'s stop sentinel arrives on a queue WRITTEN BY the loop that holds `#5058`, which under this boundary would not exist yet).
5. The single cheapest discriminating test we could run next, stated as a command-shaped step with its prediction.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this session, so the review is my output, as the peer brief specifies.

---

# Failed-prediction review — CLAIM A and CLAIM B

**CLAIM A is wrong.** **CLAIM B is half wrong** — its severing premise holds, its conclusion is refuted by a measurement already in your own logs.

---

## 1. The strongest reason CLAIM A is wrong

**The four cited files do not agree with each other.** What exists is not one design; it is two, and the build cannot tell which binds. CLAIM A was reached by confirming that *a table exists* — nobody cross-read the tables.

| queue | `docs/d1-build-plan.md` §9 | `docs/cycle15-plan.md` Pre-decided 1 |
|---|---|---|
| `Q_focusback` | `:555` — "**1 DBL**, `#10407` t6's value" | `:122` — "`#10407` t6 (**Bool**)" |
| `Q_focus` | `:554` — source `#10757 .element` | `:121` — source `pos in cal image out` |
| `Q_rmeta` | `:553` — "the kernel's own outputs" | `:120` — `#6810 current image number` (DBL) |

Same queue, same terminal, two different element types. `docs/frame-loop-wire-graph.md:410` settles it: `#10407` t6 is `position [internal units]` (wire 9113), feeding SR `#4256` and `Global motor pos.vi`'s `Focus position`. Numeric. So the document that is wrong is `cycle15-plan.md` — **the binding one**, the one a material session "applies without asking" (`cycle15-plan.md:113`).

**Second, and this is the reading on which "designed on paper" is not what the blocked build needed.** `queue_node` consumes a `src_name` = *a named OUTPUT terminal of a node that already exists on the diagram* (`docs/toolkit-capabilities.md:32`). "The kernel's own outputs" (`:553`) is not a `src_name`. `#10757 .element` (`:554`) names a Dequeue **the build itself creates** — a type source with an ordering constraint the table does not express. Run 3 died on precisely this class: `sr_queue` *"refuses a nameless type source, so both rows would have returned NO-ROUTE"* (`build_d1_routeb_v7.py:113-116`). §9 supplies a resolvable `(node, named output terminal)` pair for at most three of the eight.

**Third:** `cycle15-plan.md:120-121` sources `Q_res`/`Q_good` from the **GPU** kernel's `x,y,z array out` / `Bead is good? array out`. Cycle 49 established that `#5058` is the **CPU** kernel (`STATUS.md:76`, Pre-decided 31(a), fatal gate C2k). Those type sources name a node S2 does not place.

**Alternative explanation of the same evidence.** The v7 comment is neither stale nor a design gap — it is accurate about a different predicate. Read it literally: *"the element types of **the other six** queues are an undesigned row"* — the six beyond the two SR queues the paragraph above had just refused — and "undesigned" plausibly means *not resolved to a `src_name` on this copy*. Under that reading the comment is **current**, and design work is owed.

---

## 2. The strongest reason CLAIM B is wrong

First, what survives. **The severing premise is right** — `STATUS.md:64` (`a5_lands_unwired=True`), `cycle27-plan.md:838` Pre-decided 33(a) correcting 32(f). **And your census conclusion about a constant is right**, which refutes my own opening hypothesis: `Constant` and `Node` are **siblings** under `GObject`, not parent and child ([VI Server Class Hierarchy](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy)), so `AbstractDiagram.Nodes[]` excludes constants and `OpStopFromNode_v0`'s `Loop.Diagram → Nodes[] → Terms[]` ladder can never source one. The conditional terminal is reachable only through `WhileLoop.Loop End Ref` 6362C00 (`toolkit-capabilities.md:62`), and an unwired one is a broken VI ([NI: *Conditional terminal is not wired*](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/conditional-terminal-is-not-wired.html)).

**Now the refutation. The route exists, it is built, and it reached `ExecState 1` on a loop the build created.** `docs/toolkit-capabilities.md:63-64`:

> `OpCreateEqual_v0` places an `Equal?` **with both operands wired from output terminals of one existing node** … its Boolean output then drives the loop's conditional terminal through `OpStopFromNode_v0` (term 119, wire 0 → **387**) and the scratch reads **ExecState 1**.
> T5 CLOSED BY MEASUREMENT (`tools/bench/build_opsentinel_ops_run3.log`, gates F5c/F6) — *"the op produces a RUNNABLE VI"*. `OpCreateEqual_v0` 23/0.

That is literally question 2's "always-true comparison such as `Equal?` fed both operands from one source", on `WhileLoop#43` of an `EMPTY_v0` copy — **a loop the build created** — and `ExecState 1` is exactly `gscript.save()`'s predicate at `tools/gscript.py:2071`.

`cycle27-plan.md:816-820` already wrote the selection rule: **(1)** a constant-TRUE op wins; **(2)** failing that, `OpCreateEqual_v0` → `OpStopFromNode_v0`. `STATUS.md:22` reports only that *"32(d) rule (1) still has no winner"* — and `STATUS.md:59-64` converts that into "S2 CANNOT END LEGAL". **Rule (2) is never evaluated.** That is the whole gap.

**And the operand need not be inside the body.** `toolkit-capabilities.md:64`: *"Operands may sit on an outer diagram: LabVIEW makes the tunnels (measured `LoopTunnel 0 → 2`)."* That falsifies 32(b)'s premise that the body-node routes "were unreachable only because an empty body has no node to address" — so **create loop → scaffold → save** is legal on an *empty* body, before any `move_in`.

**The smuggled premise.** CLAIM B ends the span at *"its **real** stop condition"*. Your own decided order ends it at a **scaffold** (`cycle27-plan.md:803`). Swapping "legal" for "real" inflates the atomic unit by the entire queue/sentinel design — and CLAIM B then pulls the 13/12/7 re-wiring rows inside it as well. The premise licenses ~3 operations; the conclusion bundles ~20, and the 20 include **the exact stage that killed v3→v7 ten times** (`cycle27-plan.md:830`). That is the user's 2026-09-19 rule run backwards.

Two caveats I will not hide: the scaffold operand must be a **scalar** — `STATUS.md:22` already caught that `#5058` t3 is `Bead is good? array out`, an ARRAY, and `Equal?` on arrays yields an array that will not drive a conditional terminal. And `x == x` is TRUE for every non-NaN value, which satisfies legality unconditionally and satisfies 30(f)'s "must not hang" for any frame counter or position.

---

## 3. An alternative explanation for the ten failures — address invalidation by self-mutation

Neither claim touches this. Every re-wire row is addressed by **terminal INDEX**, and the indices drift because the build's own earlier edits create tunnels and sever wires:

- `toolkit-capabilities.md:70` — T2c2's wire reads `Is Broken? TRUE` because *"terminal index 1 came from a census of the RESTRUCTURED copy and was applied to an UNRESTRUCTURED one."*
- `archive/peer/2026-09-17-priorart-priorart-routeb-build.md:301` — *"A stale `ti` selects a different, live tunnel's wire, `w_now` is non-zero, and the SINK RULE checks only the sink — so a wrong-but-valid source is wired silently and no gate sees it."*
- `toolkit-capabilities.md:68` — the RBW-survival gate *"IS uid equality … **Do not cite RBW-survival as evidence a wire is good**"*, and *"terminal-INDEX drift across tunnel creation is a live, unmeasured alternative."*

This predicts the observed pattern exactly: failures concentrated in the one stage that applies a large batch of pre-computed indices *after* many mutations; a different local symptom each time; each explained locally and patched; none fixed. It also predicts that **CLAIM B's boundary will not help** — 32 rows become 13/12/7, but address-then-mutate is unchanged inside each batch.

It sits in tension with CLAUDE.md's own work-cycle rule ("every name resolved at planning time; no mid-run name discovery"). That rule is sound for **names**, which are stable, and unsound for **indices**, which are not stable under mutation. The rule that made your batches replayable is the same rule that makes index-addressed re-wiring unsound.

---

## 4. What falsifies "one complete loop per stage" — and the dependency question

**Falsifier:** `ExecState 1` read on a copy holding one new loop + one moved node + a scaffolded conditional terminal, with the node's cut wires **not** re-wired. One integer separates the loop from its re-wiring and kills the boundary. Conversely, a connector-pane census showing zero Required inputs among the cut rows of `#48`/`#376`/`#5058` falsifies the bare-Required half *a priori*.

**On the dependency you flagged — it does not exist at build time.** All eight Obtains sit at top level on `Diagram #686` (`d1-build-plan.md:593` S1q; `build_d1_routeb_v7.py:100`). So 1.5's Dequeue takes its refnum from an Obtain that exists whether or not 1.2 does, and the `−1` `Equal?` is built from 1.5's own Dequeue output. **Loop `#48` is fully buildable with `#5058`'s loop absent.** The dependency is **runtime only**: with no producer, 1.5 blocks forever.

Two consequences. Intermediate artefacts must never be RUN — state that in the plan rather than leaving it implicit. And **"smallest loop first" orders by the wrong quantity**: cut-wire count is a convenience, and if any intermediate will ever be run, the order is producer-before-consumer (`#5058`'s loop first), not 7 → 12 → 13.

---

## 5. The cheapest discriminating test

On a **scratch copy of the already-saved `claudeDev\D1_s1_copy.vi`** (md5 `3e3d23ce…`) — built ops only, no new op, original never opened:

1. `loop_in('while', …)` → one new While loop on `Diagram #686`
2. `OpCreateEqual_v0` → `Equal?` on the new body, **both operands from one SCALAR output terminal** of a node on the parent diagram
3. `OpStopFromNode_v0` → conditional terminal from that `Equal?`
4. **read `ExecState`** → then `move_in` `#48` → **read `ExecState` again**

**Predictions.** Step 3 → **`ExecState 1`**, reproducing `build_opsentinel_ops_run3.log` F5c/F6 on the real copy; that alone falsifies "S2 cannot end legal". Step 4 → if still **1**, the loop and its re-wiring are separable and the stage cuts far finer than one loop; if **0**, CLAIM B's bare-Required premise is confirmed empirically for `#48`, and phase A's census question is answered by measurement rather than by inventory. Either branch leaves a file.

Four op calls, against a paper census that has now consumed a cycle and two paid prior-art rounds without touching LabVIEW.

---

**What would change my mind on CLAIM B:** a log line showing `OpStopFromNode_v0` failing on a loop whose body holds only an `Equal?`, or a measurement that `OpCreateEqual_v0` cannot place onto a body whose only content is itself. Neither is in `tools/bench/`. Until one is, "no built op can make a new While loop legal" is an inventory conclusion contradicted by your own 23/0 functional record.

**Sources:** [VI Server Class Hierarchy — LabVIEW Wiki](https://labviewwiki.org/wiki/VI_Server_Class_Hierarchy) · [NI — Conditional terminal is not wired](https://www.ni.com/docs/en-US/bundle/labview-api-ref/page/errors/conditional-terminal-is-not-wired.html) · [NI — Specifying Conditions for While Loops](https://www.ni.com/docs/en-AS/bundle/labview/page/specifying-conditions-for-while-loops.html) · [NI Forums — Wiring the conditional terminal of a while loop created by LabVIEW Scripting](https://forums.ni.com/t5/LabVIEW/Wiring-the-conditional-terminal-of-a-while-loop-created-by/td-p/2115512) · [While loop — LabVIEW Wiki](https://labviewwiki.org/wiki/While_loop)

## Sources

(extract from answer)

## What was done with it

DISPOSED by the cycle-50 judgement session, 2026-09-20 — the session that asked it. Both of the claims put to this
review were REFUTED and both refutations are ACCEPTED; the answers are written into `docs/cycle27-plan.md`
Pre-decided 34:
- Answer 1 ⇒ 34(g). CLAIM A is wrong. The element types are on file but SIX OF EIGHT do not resolve to a
  `(node, named output terminal)` `src_name` that exists on this copy, so the v7 comment was current in substance.
  The `Q_focusback` type contradiction is resolved to 1 DBL on the measured evidence the review cited.
- Answer 2 ⇒ 34(a)/(b)/(c). CLAIM B's atomicity is refuted by our own measurement: 32(d) rule (2) was never
  evaluated and it qualifies, and the operands may sit on the OUTER diagram, so an EMPTY new loop can be scaffolded
  and saved. This is the single most valuable thing in the exchange.
- Answer 3 ⇒ 34(h). Address invalidation by self-mutation is adopted as the strongest rival explanation for the ten
  v3→v7 deaths and as a binding constraint on every re-wiring stage.
- Answer 4 ⇒ 34(e)/(f). The `#48`/`#5058` dependency is runtime-only, so smallest-first ordering stands — but only
  because 34(f) now forbids RUNNING any intermediate artefact, which is the condition the review itself attached to
  its producer-first alternative. Producer-first is NOT adopted, and the reason is recorded.
- Answer 5 ⇒ 34(j). Adopted verbatim as the next build, run as a DIAGNOSTIC on a scratch copy rather than as a
  stage.
- My own claim B is withdrawn in 34(d). Nothing in this exchange is left unaccepted.
