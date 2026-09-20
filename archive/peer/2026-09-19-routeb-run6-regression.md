# routeb-run6-regression

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.6636  in 28 / out 44997 / cache-create 171918 / cache-read 1500108  (678s, 24 turn(s))
- **date:** 2026-09-19 02:24:28
- **outcome:** ANSWERED (680s)
- **why asked:** MANDATORY failed-prediction review (CLAUDE.md rule 5). Run 6's prediction — "routing the
  temporary-sink source lookup through the same two-index retry the five sibling from-ctl rows use would close
  the `Z/dZ` row WITHOUT disturbing any other row" — half held (`Z/dZ` WIRED, `tools/bench/build_d1_routeb_v3_run6.log:408`)
  and half broke (`#2222 t5 'Correction Factor'`, WIRED in run 5 at `…v2_run5.log:387`, FAILED on both indices at
  `…v3_run6.log:418`). Single arm per `docs/cycle27-plan.md` Pre-decided 7.
- **verdict:** REFUTES the prediction's premise — every row whose outcome changed between run 5 and run 6 is a
  terminal of the SAME node `#2222`, so the change set did disturb the `Correction Factor` row. Unconfirmed
  against the machine; its own discriminating test (§Q-B3, over the preserved crash copy) is UNRUN.

## Question

# FAILED-PREDICTION REVIEW — D1 route-B v3, run 6: one row closed, a previously-wired row regressed

Attack the prediction below. Both halves. I am not asking whether the run "went well".

## Context in three sentences

`tools/recipes/build_d1_routeb_v3.py` restructures a copy of a LabVIEW VI by VI Scripting over a COM
client (`tools/gscript.py`). Stage S3w re-wires 66 terminal rows of a moved subVI/case-structure set
inside diagram index 24 (the "1.2 body"); a parallel copy of the same body exists at diagram index 56
(the "frame body"). Rows sourced from a front-panel control are wired by a helper `wire_control`,
which addresses its sink as `Diagram[<idx>].Nodes[<n>].Terminals[<t>]` and is retried over two
diagram indices in the order `[24, 56]`.

## THE PREDICTION THAT FAILED

> "Routing the temporary-sink source lookup through the same two-index retry that the five sibling
> from-ctl rows use would close the `Z/dZ` row WITHOUT disturbing any other row."

It half held and half broke. Attack BOTH halves.

### Half A — HELD (allegedly): the `Z/dZ` row is now wired

Evidence, `tools/bench/build_d1_routeb_v3_run6.log`:

```
:351  FACT  S3w 'Z/dZ' P1 TWO-INDEX RETRY into the temporary sink: reparented=True, 1.2-body Diagram
      index 24, frame-body Diagram index 56, order [24, 56], temp `x` terminal index 2; attempts
      (index, outcome, sink wire) = [(24, 'no error', 29238)]; temp `x` wire 29238; control panel
      wire 29238; refs {'opened': 26, 'closed': 26, 'live': 0, 'cached_op_vis': 25}
:353  FACT  S3w 'Z/dZ' P2 ControlTerminal CENSUS before wire_source_owner(w29238):
      {'ct_uid': 403, 'owner_class': 'Diagram', 'owner_uid': 567, 'owner_diagram_index': 24,
       'wire_on_control': 29238}
:354  FACT  S3w 'Z/dZ' P2 wire_source_owner(w29238) returned 3 terminal(s), 1 of them sources:
      [{'i':0,'is_source':True,'owner_class':'Diagram','owner_uid':567},
       {'i':1,'is_source':False,'owner_class':'Comparison','owner_uid':10105},
       {'i':2,'is_source':False,'owner_class':'','owner_uid':0}]
:355  FACT  S3w 'Z/dZ' -> #2222 t0: temporary Equal? #10105 created as a named sink; branched off
      w29238 terminal 0 (owner Diagram#567) -> wire 29238, Is Broken? False, delta 0, ExecState 0, err ''
:356  FACT  S3w 'Z/dZ': after deleting the temporary sink, #2222 t0 carries wire 29238
:408  WIRED  #2222 t0 '' <- from-ctl 47  OpConnectFromWire_v0 w29238 -> D[24].N[20].T[0] wire 29238
      (temporary Equal? #10105 created as a named sink, temporary deleted=True)
```

The whole verification of half A is: the temporary `Equal?`'s own `x` terminal carried wire 29238,
which equals the wire read on the control's own panel row; `wire_source_owner` found exactly one
source terminal on that wire, owned by `Diagram#567`; `Is Broken? False`, delta 0; and after the
temporary `Equal? #10105` was deleted, `#2222 t0` still reads wire 29238.

**Q-A: Does that verification actually establish that `#2222 t0` now sits on the ORIGINAL control's
net — the same electrical net the original VI's computation used — rather than on a look-alike wire
that merely carries the same numeric wire id, or on a net the temporary node's deletion silently
re-formed?** Name the strongest concrete reason this verification is insufficient, and say what a
sufficient one would read instead.

### Half B — BROKE: a row that was wired in run 5 failed on BOTH indices in run 6

Run 5 (`tools/bench/build_d1_routeb_v2_run5.log:387`), SUCCEEDED:

```
WIRED  #2222 t5 'Correction Factor' <- from-ctl 9289  wire_control 'Correction Factor' ->
'Correction Factor'; sink D[24].N[19].T[5] wire 0 -> 29386; reparented=True;
attempts [(24, 'no error', 29386)]
```

Run 6 (`tools/bench/build_d1_routeb_v3_run6.log:418`), FAILED:

```
FAILED  #2222 t5 'Correction Factor' <- from-ctl 9289  wire_control 'Correction Factor' ->
'Correction Factor'; sink D[24].N[20].T[5] wire 0 -> 0; reparented=True;
attempts [(24, "wire_control ['Correction Factor'] -> CaseStructure.['Correction Facto", 0),
          (56, "wire_control ['Correction Factor'] -> CaseStructure.['Correction Facto", 0)]
```

(The attempt message is truncated at 70 chars by the ledger formatter, not by the error source.)

The `Z/dZ` row in the same run wired to `D[24].N[20].T[0]` (`:408`) — the same node `#2222`, reached
at node index 20 in run 6 and at node index 19 in run 5.

Ledger totals moved: run 5 `attempted 66, WIRED 57, FAILED 6, NO-ROUTE 3` → run 6 `attempted 66,
WIRED 55, FAILED 7, NO-ROUTE 4` (`run6.log:362`). Two further `#2222` rows became NO-ROUTE in run 6
under the sink rule (`:425-426`, `t3` and `t4` each reading `'<no such terminal>' is_source=None
wire=None`).

**The change set between run 5 and run 6 was FOUR items, none aimed at the `Correction Factor` row:**

1. the two-index retry applied to the **temporary-sink branch only** (the `Z/dZ` path);
2. a ControlTerminal census logged before `wire_source_owner`, plus a fall-through so a raise becomes
   a FAILED ledger row instead of ending the run;
3. `_err()` in `tools/gscript.py:435` now keeps the FULL `error out` source string (previously
   `src.splitlines()[0]`);
4. six per-call `GetVIReference` sites in `tools/gscript.py` converted to a cached `vi_ref()` closure
   (`tools/gscript.py:217-255`; sites at `:1241, :1249, :1383, :1966, :2057, :2793`).

**Q-B1: What could make a previously-wired from-ctl row fail on BOTH diagram indices when the change
set did not touch it? Name the MECHANISM, not a list of candidates.** State it as a causal chain
ending at `sink wire 0 -> 0` on both index 24 and index 56.

**Q-B2: Is `Class Operator:Traverse (Traverse Failed)` (the crash below) ONE fault with this row
regression, or TWO independent faults?** Take a side and give the reason it is not the other.

**Q-B3: What is the SINGLE cheapest discriminating test that separates your answer to Q-B1 from the
next-most-likely alternative?** Give it as a concrete procedure over this project's existing tools
(`tools/gscript.py` ops, a recipe stage, a log read) — not as "instrument more".

### The crash, for Q-B2

```
:429  FACT  S3w handles IMMEDIATELY BEFORE g.count(TARGET, 'LoopTunnel') in settle_index_modes: 35558
:430  FACT  CRASH RuntimeError: count(LoopTunnel) on SCRATCH_routeb_013612.vi: error 2: Invoke Node
      in TRef Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReport_v3.vi
:452  RuntimeError: count(LoopTunnel) on SCRATCH_routeb_013612.vi: error 2: Invoke Node in TRef
      Traverse.vi->VI Scripting - Traverse.lvlib:Traverse for GObjects.vi->OpReport_v3.vi
      | <APPEND> | Method Name: <b>Class Operator:Traverse</b> (Traverse Failed)
```

Six ledger rows immediately before it (`:419-424`) failed with the same `error 2` out of
`report_all(Diagram)`. The crash is at the same call site as in runs 4 and 5.

## ALREADY RULED OUT — do not spend the answer on these three

1. Python-side VI Server refnum leakage: `REFS` reads `{'opened':26,'closed':26,'live':0}` at `:351`
   / `:353` and `{'opened':32,'closed':32,'live':0,'cached_op_vis':25}` at `:440` — `live: 0` on both
   sides of the failure. (Noted: no traverse refnum array ever crosses COM, so this can never
   *exclude* refnum exhaustion INSIDE the op VIs — that remains open.)
2. Kernel handle count as a cause: 35,558 handles at `:429`, LOWER than run 4's at the same call site;
   and `tools/bench/bench_prep.py:64-71` reads the KERNEL count, which cannot see VI Server refnums.
   The handle comparison is withdrawn as unmeasured.
3. Damage to the original VI: md5 `2a78e17c449cacdaf5da389818526859` identical before (`:13`) and
   after (`:438`); nothing was saved into the original, and the crash copy was renamed aside, not
   deleted (`:437`).

## Output I need

For each of Q-A, Q-B1, Q-B2, Q-B3: one clearly separated answer. Q-B3 must be a procedure I can
execute as written.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is wrong in its premise: run 6's change set *did* touch the `Correction Factor` row — it wired into that row's own node, `#2222`, minutes earlier in the same pass.** Every row whose outcome changed between run 5 and run 6 is a terminal of `#2222`, and the ledger totals close on that and nothing else:

| | run 5 | run 6 | delta |
|---|---|---|---|
| WIRED | 57 | 55 | −1 (`#2222 t5`) −2 (`#2222 t3`,`t4`) +1 (`#2222 t0` = Z/dZ) |
| FAILED | 6 | 7 | +1 (`#2222 t5`) |
| NO-ROUTE | 3 | 4 | −1 (Z/dZ) +2 (`#2222 t3`,`t4`) |

`run5.log:338,385-387,402` vs `run6.log:362,408,418,425-426`. In run 5, `#2222 t3` and `t4` were **WIRED** (`run5.log:385-386`); in run 6 they read `'<no such terminal>'`. The six `report_all … error 2` rows are byte-identical in both runs (`run5.log:396-401` ≡ `run6.log:419-424`). So run 6 changed exactly one node's state and exactly that node's rows broke. "Without disturbing any other row" is refuted arithmetically.

---

## Q-A — the verification does not establish that `#2222 t0` is on the control's net

**Strongest reason: the identity check bottoms out at the *diagram*, which every candidate shares.** `wire_source_owner(w29238)` reports the one source terminal's owner as `Diagram#567` (`run6.log:354`) — the same value the ControlTerminal census reports as *its* owner (`:353`). Terminals are owned by nodes; a source terminal reported as owned by a Diagram means either the helper hops one level too far, or the source is some top-level node on diagram 24. Either way the predicate satisfied is "the source is *something* in diagram 24", true of ~30 objects including the node the wire should *not* be on.

Three supports, all from the machine:

1. **A wire id is an allocation slot, not an identity.** NI's own documentation: *"if you delete an object, LabVIEW might assign the UID for that deleted object to a different object in the future"*, and it advises checking Class Name or Label **alongside** the UID "to detect this situation" ([LabVIEW Wiki, GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property)). This VI demonstrably recycles: run 6's new objects got uids 1581, 2043, 3176, 5950, 10413 (`run6.log:404,412-416`) while its other new objects sit at 26 000–29 000. And wire **29238** was, one run earlier, the from-tunnel wire on `#2222 t3` (`run5.log:385`).
2. **Everything probative was read while the temporary still existed.** Source, `Is Broken? False`, delta 0 are all at `:354-355`, before the delete. The only post-delete read is the id itself (`:356`) — the one quantity the doc above says is insufficient on its own.
3. **The cited proof line contains an unread anomaly**: the wire's third terminal reads `owner_class '', owner_uid 0` (`:354`). Either the census cannot read that terminal — making its `i=0` reading equally suspect — or the wire carries a terminal attached to nothing. It was passed over as "1 of them sources".

**A sufficient verification reads, after the delete:** the sink terminal's wire `W`; `wire_source_owner(W)` returning exactly one source whose **own uid is 403** (not its owner's), with that terminal's class printed; `ControlTerminal#403`'s own wire equal to `W`; the Wire-object count delta across create+delete equal to 0; and — per CLAUDE.md's "structural is not functional" — `ExecState` 1 at the end plus numbers through the path. The fleet already prints `uid → self 'ControlTerminal'#403` (`run6.log:352`), so the discriminating read exists and was not used here.

## Q-B1 — mechanism: a destination-side fault, invariant under a source-side retry

1. **Diagram 24's entire node index space is +1 in run 6.** Run 5 addressed N[1],3,5,7,13,15,17,19,21,25,27; run 6 addresses N[2],4,6,8,14,16,18,20,22,26,28,30 (`run5.log:362-392` vs `run6.log:386-417`). Not a local shift at `#2222` — a global one from slot 1 up, i.e. one extra object in the walk. `wmap` is cached per (target, diagram) and invalidated **only** by an explicit `fresh=True` (`build_d1_v0.py:364-372`), and the Z/dZ path changes diagram 24's node population twice: create `Equal? #10105` (`:350`), delete it (`:356`).
2. `from-ctl` rows address the sink by **class index** but verify it by **node index** (`build_d1_routeb_v3.py:1748-1749`), so the recipe and the machine can disagree about which object `D[24].N[n]` names — which is what `'<no such terminal>'` on `t3`/`t4` looks like.
3. `wire_control` **raised**, and the message prefix proves the branch: `branch=True` (`:1748`) disables the Wire-count guard at `gscript.py:1964`, and `count()` failures carry their own `count(Wire) on …` prefix — so the raise is `gscript.py:1957`, LabVIEW's own `error out` from `OpWireCtl_v0`.
4. Therefore `after` never left its initialiser (`:1741`), and `tried.append((sd, str(e)[:70], 0))` (`:1753`) recorded a literal 0. **`sink wire 0 -> 0` is not a measurement** — `#2222 t5` was never read after the attempts. The wire may exist.
5. The retry varies only `src_diagram_index` — the diagram `Get Controls` searches for the *control* (`gscript.py:1947-1949`). It never varies the destination. **A destination-side fault is invariant under this retry**, which is precisely why both attempts fail identically. "Failed on both indices" is the fingerprint of the fault being on the end the retry does not move, not evidence of a new cause.

**Alternative explanation of the same evidence** (the measurement does not yet separate it from the above): the op *did* create the wire on attempt 1 and errored afterwards; the index-addressed readback at `:1749` then looked at the wrong node, returned 0, `if after: break` didn't fire, and attempt 2 re-entered on an already-wired control. Same `0 -> 0`, same two attempts, wire present on the diagram. Q-B3 separates them.

**What would falsify my answer:** `#2222` sitting at live index 20 with its run-5 terminal census intact (7 terminals, `t3`/`t4`/`t5` present and named) on the preserved copy. Then the index space was not stale and the fault is inside `OpWireCtl_v0` for a CaseStructure destination.

## Q-B2 — TWO faults

`Class Operator:Traverse (Traverse Failed)` is a **separate, pre-existing** fault. It is at the same call site in runs 4, 5 and 6 (your own brief), and its six victim rows are identical strings in runs 5 and 6 (`run5.log:396-401` ≡ `run6.log:419-424`) — a run in which `Correction Factor` wired successfully. **A constant cannot explain a change.** Error 2 is LabVIEW's "Memory is full", and NI documents it specifically for *opening a new reference* ([NI KB: Error 2: Memory is Full when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU)) — consistent with refnum pressure inside the op VIs, which `gscript.py:236-238` already states its counters cannot see.

Two caveats on your "ruled out" list, because both bear on this: (a) `_REF_CLOSED` is incremented unconditionally in `vi_ref`'s `finally` (`gscript.py:251-259`), so `live: 0` is a tautology, not a measurement — and a `with vi_ref(t) as r:` binding outlives the block in the caller's frame, so `ref = None` is not "the only name that ever held it"; (b) the thing that makes Q-B2 answerable is not that reading but the run-to-run invariance above.

**What would flip me to ONE fault:** `#10105` still present on the preserved copy (i.e. `temporary deleted=True` is false), or the recovered full `Correction Factor` error string turning out to be `error 2 … Traverse`.

## Q-B3 — cheapest discriminating test (procedure, as written)

Run 6 renamed its working copy aside instead of deleting it (`run6.log:437`). The failing state is **on disk**. Reuse the pattern already in `build_d1_routeb_v3.py:415-455` (`crash_copy_measure`): restart LabVIEW, read, save nothing, run nothing. No build, no rig, no gate.

1. Print `md5`, size and **mtime** of `SCRATCH_routeb_013612_crash_020648.vi`, and compare mtime with the run's last `g.save(TARGET)` (`build_d1_routeb_v3.py:1899`). If the file predates S3w, **stop — the test is void**; go to step 6 instead.
2. `g.count(CRASH,'LoopTunnel')` and `g.report_all(CRASH,'Diagram')` on the fresh instance. **Succeeds ⇒ error 2 is session state** (refnum/memory inside the op VIs), confirming Q-B2's "two faults". Fails identically ⇒ it is VI content, and the temp-node surgery becomes a suspect for both.
3. Fresh walk of diagram 24 (`wmap(CRASH, 24, fresh=True)`): does `#10105` still exist, and is `#2222` at index **19 or 20**?
4. `g.node_terms(CRASH, 24, idx(#2222))` — full census t0…t6: name, `is_source`, `wire`.
5. For `t0`'s wire and `t5`'s wire, print **each terminal's own uid and class**, not its owner.

Readings decide: `#2222` at 19 with 7 terminals ⇒ the recipe's index space was +1 stale (Q-B1 as stated). `t5` carrying a **non-zero** wire ⇒ the row was wired and `FAILED` is bookkeeping (the alternative). `t0`'s source uid **403** ⇒ half A holds; anything else ⇒ it is on another net.

6. One-line fix regardless: `str(e)[:70]` truncates at exactly the colon before LabVIEW's error code — at eight sites (`build_d1_routeb_v3.py:1075, 1237, 1360, 1412, 1421, 1452, 1498, 1753`). Change #3 was added to stop throwing that remainder away (`gscript.py:438-441`); the callers still throw it away. That is the same `unread-evidence` finding recurring inside the run that was supposed to close it.

Sources: [LabVIEW Wiki — GObject UID property](https://labviewwiki.org/wiki/GObject_class/UID_property) · [NI — Error 2: Memory is Full when Opening a New Reference](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z0000019KhWSAU) · [NI — Block Diagram:Remove Bad Wires](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/vi_block_diagram058remove_bad_wires.html)

*(I could not write the plan file — Write is disabled in this session, correctly for a read-only peer role — so the review above is the whole output.)*

## Sources

(extract from answer)

## What was done with it

**DISPOSED 2026-09-19 by the cycle-39 judgement session; applied by a MATERIAL session the same day into a NEW
recipe `tools/recipes/build_d1_routeb_v4.py`** (cut from v3's bytes — patching v3 in place would invalidate its
released stop record, `tools/stop_record.py:318-331`). Four dispositions, J1–J4. None changes any per-bead
computation (rule 1a): J1 and J3 are addressing and gating, J2 and J4 are read-only instrumentation.

FIXED: contradicted - tools/recipes/build_d1_routeb_v4.py:450 - J1, from Q-B1: `wmap_invalidate()` drops the CACHED walk of ONE diagram, and it is called immediately after the temporary `Equal?` is CREATED (inside `create_equal`, the common creation helper, `:1160`) and immediately after it is DELETED (`:1676`), so no row addressed after that bracket uses a node index taken before it — the mechanism the review named for `#2222` sitting at N[19] in run 5 and N[20] in run 6. TARGETED to the affected diagram, not a global `fresh=True`, because extra traverses are the wrong direction while `error 2` is open.

FIXED: unread-evidence - tools/recipes/build_d1_routeb_v4.py:1728 - J2, from Q-A: the `Z/dZ` row's verification is now a MEASUREMENT taken AFTER the temporary sink is deleted, and any wrong reading FAILS the row (`:1737`): (a) the source identity is closed from the reciprocal end the fleet can actually read — the control's OWN wire must equal the wire the sink carries, with exactly one reciprocal source terminal on that wire and the ControlTerminal's own class/uid self-echo printed; (b) the Wire-count delta across the whole bracket must be 0, opened at `:1519`; (c) `Is Broken?` must be False; (d) the sink terminal's wire id is read back from the machine, and the raise paths that used to record the initialiser `0` now re-read the sink instead (`:1589` for the temp sink, `:1921` for the from-ctl rows — the line the review named as "not a measurement").

FIXED: refuted-already - tools/recipes/build_d1_routeb_v4.py:906 - J3: the `S3-zdz 'Z/dZ' -> #2222 t0 is wired BEFORE the #403 reparent` gate is RETIRED and its exact former text is quoted in the comment above the replacement. It failed in runs 4, 5 and 6 while in run 6 the row it guards SUCCEEDED, because it asserts the ordering of the REORDER route that `docs/cycle27-plan.md` Pre-decided 13a retired in favour of the temp-sink path, which wires `Z/dZ` AFTER the reparent by design. The pre-reparent reading is still RECORDED as a fact; the J2 gate is the replacement.

FIXED: unread-evidence - tools/recipes/build_d1_routeb_v4.py:248 - J4: all nine `str(e)[:70]` / `str(err)[:70]` sites of the recipe now log the FULL message (`:775`, `:1144`, `:1311`, `:1434`, `:1487`, `:1496`, `:1537`, and the two rewritten retry loops at `:1589`/`:1921`). Run 6's only NEW failure message — `#2222 t5 'Correction Factor'`, `…v3_run6.log:418` — was cut at exactly the colon before LabVIEW's error code, throwing away the remainder that `gscript._err()` had just been fixed to keep. `tools/gscript.py` is NOT touched by v4; the `_REF_CLOSED` side claim below is deliberately held for a later dispatch.

Not acted on in this dispatch, deliberately: Q-B3's five-step read over the preserved crash copy (`v4` still
names run 5's copy `SCRATCH_routeb_235020_crash_001808.vi` in `crash_copy_measure`, unchanged), and the
`_REF_CLOSED`-is-a-tautology claim about `tools/gscript.py:251-259`.

The original note, kept verbatim:

UNDISPOSED, deliberately. This was cycle 38's LAST dispatch and its brief was measurement-only: dispatch the
review, report the facts, change no recipe, patch no tool, launch no build, prepare no v4 (editing v3's bytes
re-triggers the stop-record deadlock this cycle worked through). Nothing in this answer was acted on. The four
items it leaves on the table for the next cycle's judgement session, all unrun:

- Q-B3's five-step read over the preserved crash copy `…\claudeDev\SCRATCH_routeb_013612_crash_020648.vi`
  (restart, read, save nothing, run nothing — the `crash_copy_measure` pattern at
  `tools/recipes/build_d1_routeb_v3.py:415-455`), which separates the stale-index-space mechanism from the
  "wired but mis-read" alternative.
- Its step-1 void condition: if the crash copy's mtime predates S3w, the test is void.
- Its claim that `str(e)[:70]` still truncates at eight recipe call sites, so change #3's full-string fix is
  discarded by the callers.
- Its claim that `_REF_CLOSED` is incremented unconditionally in `vi_ref`'s `finally` (`tools/gscript.py:251-259`),
  which if true makes `live: 0` a tautology rather than a measurement.
