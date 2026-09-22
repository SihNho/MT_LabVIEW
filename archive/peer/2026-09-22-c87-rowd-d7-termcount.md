# c87-rowd-d7-termcount

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.8559  in 34 / out 48434 / cache-create 146596 / cache-read 2172918  (629s, 26 turn(s))
- **date:** 2026-09-22 15:50:40
- **outcome:** ANSWERED (632s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# FAILED PREDICTION — gate D7 failed on the M3a-3b Row-D landing run

`tools/bench/build_d1_m3a3b_rowD.log`, `BGRUN END rc=1 after 148s`, **20 gates pass / 1 fail**.
Recipe `tools/recipes/stage_d1_m3a3_rowD.py` (90 lines on `tools/stagekit.py`).

## What the run did

On a dated working COPY of the bed `claudeDev\D1_s3b_m3a3_20260922_081056.vi` (md5 `33ef524e…`, byte-unchanged
at both ends of the run): delete wire **7506** with **no Remove Bad Wires anywhere**, re-read
`FlatSequenceInnerTunnel #7468`, then connect the NEW loop's `Outgoing Handle` (owner `RightShiftRegister
#23868`) into the FSIT's now-bare `Left Terminal` `#7488` with `OpFsInnerTunnelConnect_v1.vi`, purge the junk
node, run the gates, save.

## The prediction that failed

Gate **D7**, written as *"`WhileLoop #637`'s terminal counts unchanged (total, wired)"*, with the stated intent
*"nothing downstream dropped"*:

    FAIL  D7 WhileLoop #637's terminal counts unchanged (total, wired)  before (60, 48) after (60, 47)
    (tools/bench/build_d1_m3a3b_rowD.log:200)

The TOTAL terminal count is unchanged at 60. The WIRED count fell by exactly one.

## What else the machine said (all PASS)

* `D1  FSIT #7468 still resolves and its LeftTerm #7488 is BARE after the delete  LeftTerm #7488 wire 0 err ''` (`:92`)
* `D0  the connect wrote a wire onto #7488  wire 25324 op err 'error 999999: POISON - not overwritten by the run' invoke err ''` (`:113`)
* `D2  exactly ONE source terminal on the net, owner RightShiftRegister #23868  [('RightShiftRegister', 23868)]` (`:120`)
* `D3  the OLD source #4334 is OFF that net  every owner [('FlatSequenceInnerTunnel', 7468), ('RightShiftRegister', 23868)]` (`:121`)
* `D4  PD85 violations 0 on the walk  []` (`:122`)
* `D5  wire_delta 0 on the ordered idempotent second pass` / `Is Broken? False ; UID 2 25324` (`:128-129`)
* `D5b the ordered second pass left ONE source on the net, still owner #23868` (`:136`)
* `D6  the diagram-wide broken-wire count <= the baseline 11  11 bad wire(s) vs baseline 11` (`:213`)
* Artefact SAVED through the approved broken-intermediate `gui_save` route:
  `D1_s3b_m3a3b_rowD_20260922_153612.vi` md5 `c9d38bb194013ac7b916d073466078c7`, 307,093 B, `ExecState` 0
  (broken BY DESIGN, never run) (`:205-210`).

## The two readings this session can see, and the evidence for each

**(1) D7 is over-strict and the fail is the row's own purpose.** `#637`'s terminal table shows
`t10 'Outgoing Handle' is_source=True wire=7506` BEFORE (`:35`) and `is_source=True wire=0` AFTER (`:149`).
Wire 7506 is exactly the wire this row deletes, and `#637` is the OLD loop whose shift register `#4334` is the
OLD source. So the one lost wired terminal is the OLD source going bare — the intended detachment — and D7's
"wired" half asserts the opposite of what Row D is for, while its "total" half (60 == 60) is what actually
tests "nothing downstream dropped".

**(2) Something else on `#637` lost a wire as a side effect.** Only t10's row was compared by eye; a second
terminal could in principle have changed in the same direction while t10 also changed, and the aggregate
(60, 47) cannot distinguish one change from two.

## Already ruled out on the machine (do not re-propose)

* Not Remove Bad Wires: there is **no** `remove_bad_wires` call site anywhere in the recipe (only a docstring
  mention at `stage_d1_m3a3_rowD.py:6`); D6's probe runs on a separate scratch copy deleted in the same run.
* Not a lost tunnel: `#7468` still resolves after the delete, and its `Right Terminal` `#7471` still carries
  its inner wire 7448 (`:91`, `:112`).
* Not a wire-count artefact: `Wire` census 1920 → 1920 across the whole run (`:86`, `:201`).

## One more observation, unexplained, reported rather than diagnosed

`CENSUS AFTER … {'Wire': 1920, 'Node': 636, 'LoopTunnel': 138}` (`:201`) against `Node 635` before (`:86`).
The FIRST connect minted one junk `Invoke` node and the recipe purged it (`:98`, `:108-109`), but the
**ordered second pass** (gate D5, which re-issues the same connect against the work file) minted another one
that was never purged — `#637`'s diagram went `nodes_on_diagram` 27 → 28 (`:23` vs `:137`) — and the artefact
was saved carrying it. The op's own `error out` also reads back as the POISON sentinel
(`'error 999999: POISON - not overwritten by the run'`) on every call while the raw Invoke `error out` is `''`.

## What I need from you

1. The strongest reason reading (1) is WRONG.
2. An alternative explanation for `(60, 48) -> (60, 47)` that neither reading covers.
3. What would falsify reading (1) — stated as something readable from the machine.
4. The CHEAPEST discriminating test between (1) and (2), read-only if possible, on the saved artefact or a
   scratch copy of it, naming the exact op/property and the exact comparison.
5. Whether the unpurged second-pass `Invoke` node in the SAVED artefact is a defect that must be repaired
   before this file is used as the next stage's bed, or a cosmetic leftover — and how to tell from the file.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled in this cell (correct for a read-only peer role), so the review is here in full.

---

# Failed-prediction review — D7, M3a-3b Row-D landing run

Read-only. No lock, no build, no edit, nothing run.

**Verdict:** reading (1)'s *fact* survives every check I could make. Its *conclusion* and its *remedy* do not — and the discriminating test the session asks for in question 4 was already bought twice: once in cycle 80, once inside this run's own log.

## 1. The single strongest reason reading (1) is WRONG

Not the identification of t10 — that holds. The sentence that fails is *"its 'total' half (60 == 60) is what actually tests 'nothing downstream dropped'."*

`OpWireSource_v5` walked net 7506 **before any mutation, on this same bed**, and reported exactly two real terminals — source `RightShiftRegister #4334`, sink `FlatSequenceInnerTunnel #7468`, *"2 real-owner row(s), 0 violate"* (`tools/bench/c80_rowd_routeA_r2.log:73-77`, repeated `:93-97`). There was nothing downstream to drop. And t10 is a shift-register **OUTER** terminal (`#4334 OUTER = 'Outgoing Handle' on wire 7506`, `c80_rowd_routeA_r2.log:26`, `:72`), which no wire deletion removes — unlike a loop tunnel, which LabVIEW does drop when its last wire goes ([NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080); I could not verify this on an NI doc page — the docs pages return navigation chrome to a fetch — so treat the tunnel half as forum-grade).

So on this row the *total* half was a constant that could not have moved, and the *wired* half carried the entire signal. Reading (1) proposes keeping the uninformative half and deleting the informative one, which makes D7 green by construction on every future row. Green is also what a total-only D7 would have been on this run's one real regression: `Node` 635 → 636 in the saved artefact (`build_d1_m3a3b_rowD.log:86` vs `:201`), which **no gate in the recipe reads**.

Second, smaller but immediate: the session understates its own record. **Both complete 60-row tables are printed** (`:25-84`, `:139-198`) and differ in exactly one row. Reading (2) is dead on evidence already in hand — no new machine time needed.

Framed correctly, D7 is not over-strict. It is **mis-specified**: `c80_rowd_routeA_r2.log:73-77` made the delta (−1, on t10, WIRED→BARE) predictable before the run, so "unchanged" was never a prediction anyone had grounds to write.

## 2. Alternative explanations neither reading covers

**(a) The −1 is not attributed — it is assumed.** `#637` was sampled once before everything (`:24-85`) and once after everything (`:138-199`). In between, four mutations: delete 7506 (`:89`), connect #1 (`:96`), the purge (`:108`), and connect #2 issued by gate D5 **against the artefact itself** (`:126`; `stagekit.py:588-591` re-issues against `self.work`). Nothing read `#637` in between. The competing story — the op clearing a still-attached endpoint rather than the delete baring it — yields an identical end state, and this op is measured to MERGE (`archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md:261-268`; three source terminals once, `tools/bench/build_d1_m3a3b_d3.log:318`). **The measurement does not distinguish these two causes.**

**(b) Identity is compared by numbers this run proves are recycled.** The junk Invoke node from connect #1 took **UID 7506 — the UID of the wire deleted seconds earlier** (`:89` vs `:98`), reproducibly the same UID at the same place in c80 (`c80_rowd_routeA_r2.log:127-128`). UIDs are unique within a VI, but *"if you delete an object, LabVIEW might assign the UID for that deleted object to a different object in the future"*, with Class Name / Label the documented cross-check ([GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property)). The D7 rows carry no terminal UID and no owner (`tools/recipes/build_d1_m3a1.py:507-510`), and **no census in this run counts shift registers** — the classes are Wire/Node/LoopTunnel (`stage_d1_m3a3_rowD.py:41`, `:77`) while `#637` carries 14 registers (`docs/cycle27-plan.md:3287-3292`). Unlikely; unmeasured; one census class away from being measured.

**(c) "Wired" is the weaker of two predicates this project already owns.** `has_wire = bool(wire_uid)` (`build_d1_m3a1.py:508`, `stagekit.py:360`) scores BARE and UNREAD alike, while the same module defines `term_state()` → WIRED / BARE / **UNREAD** and a `wired_count()` counting only WIRED (`build_d1_m3a1.py:524-538`). The gate used the weaker one. And the column `term_state` needs to detect UNREAD — `conn_err` — reads **0 on all 120 printed rows**, including every bare one, which `gscript.py:914` says should carry 1055; `gscript.py:947-949` silently substitutes zeros when a label is missing. One of the four error columns printed as evidence may not be a measurement.

## 3. What would falsify reading (1) — read from the machine

- **F1** `wired_terminals(#637)` sampled immediately after the delete, showing t10 still wired ⇒ the −1 belongs to a later step.
- **F2** any row classifying UNREAD under `term_state()` ⇒ read artefact, not connectivity.
- **F3** a `RightShiftRegister`+`LeftShiftRegister` census on the artefact differing from the bed's.
- **F4** a pre-delete walk of net 7506 with a third real owner. **Already taken; it shows two** (`c80_rowd_routeA_r2.log:73-77`).

## 4. Cheapest discriminating test

**Free, offline, no LabVIEW, no lock:** re-classify the two tables already dumped in `tools/bench/D1_s3b_m3a3b_rowD.json` (`:234`) with `build_d1_m3a1.term_state()`, and diff them as sets keyed on `(i, name, is_source, state)`. Reading (1) predicts exactly one differing element — t10, WIRED → BARE — and zero UNREAD anywhere. That settles (1) vs (2) outright.

The machine test (`stagekit.net_sources(7506)` on a scratch of the bed) needs no purchase: `c80_rowd_routeA_r2.log:73-77`. Worth naming the asymmetry — this run walked the NEW net twice (`:114-119`, `:130-135`) and the OLD net zero times.

## 5. The unpurged Invoke node — defect, not cosmetic

Repair before this file is used as a bed. It is predicted arithmetic, not an anomaly: the family mints *"1.00 stray `Invoke` per call"* (`stagekit.py:467-468`); two connects, one purge; 635 → 636 → 635 → 636 (`:86`, `:98`, `:110`, `:201`). Prior art named this hazard **before** the run — *"D5's second pass is a MUTATION of the stage target"* — and offered *"taking D5 on a scratch copy of the saved artefact"* as a release (`archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md:261-263`, `:278`); the cycle took the other release (`:303`), which checks the net, not the node census.

Why not cosmetic: it is a node on the target VI's own diagram, an unintended difference under rule 1a; an Invoke Node with an unwired required `reference` input is a broken node, so it pins `ExecState` 0 independently of the rows still to be wired — masked now by the by-design brokenness, still there when a later stage expects 1; and nothing in this recipe catches it (D6 counts wires, Remove Bad Wires does not delete nodes, the Node census is a FACT line, not a gate).

**How to tell from the file, read-only:** Node census on the artefact — the bed is 635, the artefact reads 636 (`:201`); then `node_labels(diagram 19)` → 28 rows vs the bed's 27, extra row labelled `Invoke Node`. Identify it by shape (6 terminals, 0 wired, `:100-107`), the same precondition `junk_purge` uses — **never by UID**, which demonstrably recycled.

## 6. Unasked, and open

The op's `error out` reads the POISON sentinel on all three calls (`:96`, `:113`, `:126`) — it never wrote its error channel. Every "the op succeeded" here is inferred from a side effect, for an op simultaneously observed to mint a stray node per call.

## Where I end up

Reading (1) holds on the fact and I could not break it: t10 is `#4334`'s outer terminal, the net had exactly two ends, exactly one row changed. Reading (2) is refuted by the run's own tables. What is wrong is the remedy — D7 should assert the **predicted set difference** (`{t10}`, WIRED→BARE, nothing else), not be relaxed to a half that cannot fail. **What would change my mind on the causal half: F1**, a sample of `#637` between the delete and the second connect. Nothing in this run took one.

Sources: [GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property) · [Loop class Shift Registers()](https://labviewwiki.org/wiki/Loop_class/Shift_Registers()_property) · [NI Idea Exchange — tunnels and wire deletion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080)

## Sources

(extract from answer)

## What was done with it

**NOTHING WAS ACTED ON — deliberately. This material dispatch's brief says: *"Do NOT act on it — disposition
is judgement's."*** The review is ANSWERED (claude / `hypothesis` / opus effort max, 632 s, $3.8559,
`tools/bench/peer_c87_d7.log` `BGRUN END rc=0 after 633s`) and is recorded here verbatim for the judgement
session. No gate, recipe, plan or artefact was changed because of it, and the saved artefact
`claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi` (md5 `c9d38bb194013ac7b916d073466078c7`) was left exactly as
the run wrote it.

The four things judgement has to decide, each stated as the review states it:

1. **D7's remedy.** The review does NOT accept reading (1)'s fix: it says the `total` half *"was a constant
   that could not have moved"* on this row and that relaxing D7 to it *"makes D7 green by construction on
   every future row"*. Its own remedy — assert the **predicted set difference** (`{t10}`, WIRED→BARE, nothing
   else) — is a gate redesign and was not made.
2. **Reading (2) is refuted on evidence already in hand** (both complete 60-row tables are printed,
   `build_d1_m3a3b_rowD.log:25-84` and `:139-198`, and differ in exactly one row) — but the review adds a
   cause that neither reading covered: **the −1 is not attributed**, because `#637` was sampled once before
   everything and once after everything, with four mutations in between and no read between the delete and
   the second connect. Its falsifier **F1** (a `wired_terminals(#637)` sample immediately after the delete)
   was NOT run.
3. **Its cheapest test costs no LabVIEW and no lock** and was NOT run: re-classify the two tables already in
   `tools/bench/D1_s3b_m3a3b_rowD.json` with `build_d1_m3a1.term_state()` and diff them as sets keyed on
   `(i, name, is_source, state)` — reading (1) predicts exactly one differing element and zero UNREAD.
4. **The unpurged second-pass `Invoke` node is called a DEFECT, not cosmetic** (§5): *"Repair before this file
   is used as a bed."* NOT repaired. Judgement decides whether
   `claudeDev\D1_s3b_m3a3b_rowD_20260922_153612.vi` may be the next stage's bed as saved.

Also recorded, unacted: §2(c) says the `conn_err` column reads 0 on all 120 printed rows including every bare
one, where `gscript.py:914` implies 1055 — i.e. one of the four error columns printed as evidence may not be a
measurement; and §6 notes the op's `error out` read the POISON sentinel on all three calls.
