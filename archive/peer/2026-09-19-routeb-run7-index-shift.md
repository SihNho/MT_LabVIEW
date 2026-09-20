# routeb-run7-index-shift

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $5.1027  in 38 / out 52092 / cache-create 241098 / cache-read 2676018  (758s, 37 turn(s))
- **date:** 2026-09-19 03:29:00
- **outcome:** ANSWERED (760s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

# Failed-prediction review — D1 route-B run 7 (slug `routeb-run7-index-shift`)

You are the adversarial reviewer for a failed prediction in a LabVIEW VI-Scripting build fleet. Your job is to
attack the framing below, not to agree with it. Every claim in it is mine; treat none of it as established.

## The prediction that failed

Judgement decided J1 from the run-6 review (`archive/peer/2026-09-19-routeb-run6-regression.md` Q-B1): that
`#2222` t3/t4/t5 regressed in run 6 because the wire map is cached per (target, diagram) and invalidated only by
`fresh=True`, while the `Z/dZ` temp-sink path creates and deletes `Equal? #10105` on Diagram[24] in the same pass.

**Prediction:** invalidating that cache at the create and at the delete restores t3/t4/t5 to run 5's outcomes.

**Observed in run 7** (`tools/bench/build_d1_routeb_v4_run7.log`): both invalidation sites fired
(`cache hit dropped: True`, `:350`, `:357`) and NOTHING recovered — t3/t4 stayed NO-ROUTE
`'<no such terminal>' is_source=None wire=None` (`:429-430`), t5 stayed FAILED (`:421`), and the ledger went
66/55/7/4 (run 6) to 66/54/9/3 (run 7).

## What run 7 newly measured

- t5's message, untruncated for the first time: idx 24 `error 5001: LV-Scripting.lvlib:Wire Inputs.vi | Input
  Correction Factor not found | Complete call chain: Wire Inputs.vi | OpWireCtl_v0.vi`; idx 56 `… Get Controls.vi |
  Control Correction Factor not found | … | OpWireCtl_v0.vi`. Both read the sink back as `D[24].N[20].T[5] wire 0`.
- The `Z/dZ` row (t0) itself is sound on every identity reading: the source control's own wire 29238 equals the sink
  wire 29238; exactly ONE reciprocal source terminal on w29238 (`is_source=True owner Diagram#567`, `#403`
  self-echo `('Diagram',567)`); `Is Broken? False`; sink read back 29238.
- t0 nevertheless FAILED its new gate on ONE reading: the **VI-WIDE** Wire count across the temp-sink bracket went
  1937 -> 1841, **delta -96**. The only destructive call inside that bracket is `remove_bad_wires_scripted`, run
  after `delete_object(Comparison)`. This fleet has no per-diagram wire count.
- Run 5 -> run 6 moved every node index on Diagram[24] by +1 (run 5 addressed N[1,3,..,19]; run 6 N[2,4,..,20]).
- Unchanged: the run dies at `g.count(TARGET,'LoopTunnel')` in `settle_index_modes` (`:433`) with LabVIEW `error 2`
  and `OpReport_v3.vi | Method Name: Class Operator:Traverse (Traverse Failed)`, after 6 `report_all(Diagram)`
  victim rows (`:423-428`), at 35,551 handles.

## Judgement's current hypothesis, H4, which you are asked to destroy

The temp `Equal?` node is still ALIVE on Diagram[24] while the sibling `#2222` rows are wired — the bracket
straddles those rows instead of enclosing only its own — so during them every node index on that diagram is +1.
t3/t4 then address past the end (`<no such terminal>`) and t5 addresses the WRONG node, which has no input named
`Correction Factor`. This explains why a cache fix changed nothing: the cache was never the fault; the node's real
index differed.

## Already ruled out — do not propose these

1. The wmap cache: measured, invalidation fired at both sites and changed no outcome.
2. Kernel handle counts as evidence about refnums: withdrawn as unmeasured — `tools/bench/bench_prep.py:64-71`
   reads the kernel count, which cannot see VI Server refnums.
3. `live: 0` in the REFS lines: `_REF_CLOSED` increments unconditionally in `vi_ref`'s `finally`
   (`tools/gscript.py:251-259`), so it is a tautology and excludes nothing.

## Answer four questions

- **Q1.** Give the strongest reason H4 is WRONG, and name the alternative that better explains all four
  observations together (t3/t4 `<no such terminal>`, t5's two different name-lookup messages on two different
  indices, the +1 shift, and the cache fix changing nothing).
- **Q2.** Is the -96 VI-wide wire delta collateral CAUSED by `remove_bad_wires_scripted`, or pre-existing mid-build
  breakage merely reaped by it? Name the cheapest measurement that discriminates, using only readers this fleet
  already has (`Wire.Is Broken?` 6371004 is built and measured, `docs/NAMES.md:888-897`; there is no per-diagram
  wire count).
- **Q3.** Is a VI-WIDE remove-bad-wires ever safe in the middle of a multi-row build? If not, what removes only the
  wires orphaned by one `delete_object`?
- **Q4.** Does the ledger's WIRED count measure SURVIVING wires, or only attempts that returned without raising?
  If the latter, what is the cheapest end-of-run verification that the 54 claimed wires still exist?

You may read the project's files read-only to check any of this. Cite `file:line` for every claim you make about
our code or logs. Where you REFUTE something, say so in those words.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

Write is disabled for this role (correct — I'm read-only), so the review is the answer itself.

---

# Failed-prediction review — `routeb-run7-index-shift`

**H4 is REFUTED.** Not "weakened" — the run's own log and run 5 contain three independent readings that each kill it, one of them a natural control experiment that nobody seems to have noticed was run.

## 1. The single strongest reason H4 is wrong

**The +1 shift exists before the temporary node does, and run 5 is a control in which the temporary node stayed ALIVE across the `#2222` rows and every one of them wired.**

**R1 — the shift predates its own alleged cause by ~170 log lines.** `tools/bench/build_d1_routeb_v4_run7.log:179` reads `sink #2222 is Diagram[24].Nodes[20]`. That line is emitted by `S3-zdz`, inside `s3()`, and `Equal? #10105` is not created until `:350`, inside `s3w()`. The matching line in run 5 reads `Nodes[19]` (`tools/bench/build_d1_routeb_v2_run5.log:163`). So the run-5→run-6 index difference is already present at a point in the build where **neither run has created a temporary node**. H4's mechanism cannot produce a difference that precedes it.

**R2 — run 5 already ran the experiment, and it came out against H4.** In run 5 the temp-sink bracket *aborted*: `Equal? #10104` was created (`run5.log:332`), `wire_control` into it raised `5001 … Get Controls.vi`, and the row returned NO-ROUTE at `tools/recipes/build_d1_routeb_v4.py:1606-1609` — which is **before** the `delete_object(Comparison)` + `remove_bad_wires_scripted` at `:1665-1669`. The temporary `Equal?` was therefore **never deleted and stayed on Diagram[24] for the rest of run 5** — precisely the state H4 says shifts every index by one — and `#2222` t2/t3/t4/t5 all wired, at `N[19]`, with readbacks and `Is Broken? FALSE` (`run5.log:384-387`). A live temp node neither moved `#2222`'s index nor broke a single row.

**R3 — this fleet does not address nodes by an index it assumed, so "addressing past the end" is not a failure mode it has.** `tools/recipes/build_track_v6_core.py:84-92` builds the walk **keyed by node UID** (`out[u] = (n, labels.get(u), rows)`); `node_index_on` and `terms_of` look the UID up in it (`tools/recipes/build_d1_v0.py:364-380`, `build_d1_routeb_v4.py:445-447`). `node_terms` even returns the node's own `UID` alongside its rows for exactly this reason (`tools/gscript.py:896-902`). A stale cache yields a stale *index*; the next walk yields the truthful one — and J1 forced two walks. More decisively, **`wire_control` never touches `Diagram[].Nodes[]` at all**: its destination is `(class name, class index, terminal NAME)` (`tools/gscript.py:1928-1953`), and the `24` / `56` in t5's `attempts` are `src_diagram_index` — *where to look for the control* — not a node index (`build_d1_routeb_v4.py:1899-1907`). A `Diagram[24].Nodes[]` shift cannot generate `Input Correction Factor not found`.

And the shift is not even uniform, so "every node index moved by +1" is itself an overreading: `#8885` sits at `D[24].N[25]` in run 5 (`run5.log:380`) **and** at `D[24].N[25]` in run 7 (`run7.log:407`), while indices 1–20 move by one. One inserted node shifts every later index uniformly. This does not.

## 2. The alternative that explains all four observations

**A VI-WIDE `Remove Bad Wires`, fired in the middle of the S3w row loop, reaped the debris left by S1d and S3 and took `#2222`'s bare tunnels with it.**

`build_d1_routeb_v4.py:1665-1669` runs `delete_object(Comparison)` then `g.remove_bad_wires_scripted(TARGET)` — LabVIEW's `VI.Block Diagram:Remove Bad Wires`, which "removes all the broken wires on the block diagram of the VI", i.e. the whole VI including every subdiagram ([NI docs](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/vi_block_diagram058remove_bad_wires.html), [LabVIEW Wiki](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method)). On this recipe's own path it is the **first** RBW since S1t (`:623`); between them the build deleted three subVIs (S1d) and moved 21 nodes plus 6 control terminals (S3), cutting ~109 crossings. That is where -96 comes from.

`#2222` is a CaseStructure (`run7.log:141`) and every one of its input tunnels was cut by the move — `t0 w730, t2 w505, t3 w628, t4 w1773, t5 'Correction Factor' w6096` (`run7.log:274-280`). They sat bare and broken from S3 until this bracket. In LabVIEW, when the last wire on a tunnel goes, the tunnel goes with it ([NI Idea Exchange](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080)) — and this project has already measured it in its own words: *"a wire delete plus Remove Bad Wires — deleted the tunnel and dropped every higher index by one"* (`build_d1_routeb_v4.py:54-55`). Ordering fits: the Z/dZ row **is** `#2222 t0`, the first of the `#2222` group, and its FACT lines (`:349-360`) sit between `#1359`'s (`:347`) and `#8885`'s (`:361`), so the RBW runs **before** t2/t3/t4/t5.

- **t3/t4 `<no such terminal>`** — the tunnels are gone; `is_source=None, wire=None` is `.get()`'s default, i.e. **absent**, which is what a destroyed tunnel looks like and *not* what a wrong-but-valid node looks like (that would return a real name and possibly a real wire).
- **t5** — `Wire Inputs.vi | Input Correction Factor not found` is the machine's own name lookup reporting that no input on that node carries the name. Destruction explains it; so does the weaker variant that the tunnel survives but loses its inherited name when its wire is cut. Both live on the cut-then-reap axis; neither is an index.
- **t5's second message** at index 56, `Get Controls.vi | Control Correction Factor not found`, is a different and expected failure: `reparented=True`, so the control terminal is no longer on Diagram[56].
- **The cache fix changed nothing** because the objects were destroyed, not mis-addressed.

**Where the evidence stops.** It does not separate "the tunnel was deleted" from "the tunnel survives unnamed and the walk under-reported it". This run's read path was demonstrably degrading — `node_labels` 1055 at `:422`, `report_all(Diagram)` error 2 at `:423-428`, fatal error 2 at `:433`, handles 31,128 → 51,328 at `:442`. What the evidence does settle is that the cause is wire/tunnel destruction, not node indexing.

## 3. What would falsify each claim

- **Falsifies H4:** a run in which the temp node is alive across the `#2222` rows and they all wire — **already observed (run 5)**; or `#2222` reading `N[20]` before any temp node exists — **already observed (`run7.log:179`)**.
- **Falsifies my alternative:** a `node_terms(TARGET, 24, 20)` census immediately before and immediately after `:1669` showing `#2222`'s terminal count unchanged (7 → 7) while t3/t4 still read absent afterwards. Then the loss is in the reader, not the machine.

## 4. Cheapest discriminating test

**Rerun v4 with exactly one line deleted — `remove_bad_wires_scripted` at `:1669`.** Delete the temp node, do not reap. Everything else byte-identical.
- t3/t4/t5 come back WIRED → the mid-build VI-wide RBW is the cause; the fix is scope, not cache.
- They still fail → the cause is upstream of the bracket, and the next call is a `node_terms(TARGET, 24, 20)` census at three points (end of S3 / before the bracket / after it) — three op runs, and it shows exactly when the terminal list changed.

Bracket that run with a per-diagram wire count (see Q2), and **log the index that comes back from each J1 invalidation**. Run 7 had that number for free on both sides of the bracket and printed only `cache hit dropped: True`. One integer would have closed this question a cycle ago.

---

## Q2 — is -96 caused by the delete, or pre-existing breakage reaped?

**Almost certainly pre-existing, reaped — but the run does not prove it, and one stated premise is wrong.**

The temp `Equal?` had three terminals and one wire, w29238, and **that wire survived** (`run7.log:356, 358, 360`: sink reads back 29238, `Is Broken? False`, source identity ok). A node with one surviving wire cannot orphan 96. Meanwhile ~109 crossings had been cut since the last RBW.

**REFUTED premise:** "there is no per-diagram wire count" and "building one is out of scope". `gscript.net_map(target, diagram_index)` already returns `nets = {wire_uid: [(node, term, name), …]}` for **one** diagram (`tools/gscript.py:2496-2501`); `len(nets)` is a per-diagram wire count, built, and in the fleet. Caveat, stated plainly: it sees only wires touching a node terminal on that diagram, so a fully orphaned wire is invisible to it — which for this question is a feature, since it counts exactly the wires still attached to something.

**Cheapest discriminator with existing readers, two extra calls:** `g.count(TARGET,'Wire')` at the end of `s3()` and again immediately before `delete_object` at `:1666`. Already ~1937 at end of S3 and unchanged by the delete ⇒ debris predates the bracket. Drops at the delete ⇒ the delete caused it. Stronger and still cheap: call `remove_bad_wires_scripted` a second time straight after the first — a reap is idempotent, so 1841 → 1841 confirms standing debris, while a second large drop means something in the bracket is still manufacturing broken wires.

## Q3 — is a VI-wide RBW ever safe mid-build?

**No.** It is whole-VI by definition, irreversible under script, and in a build whose intermediate state is deliberately full of cut wires it destroys exactly the objects the remaining rows intend to wire. Route A already treated it as hostile: `build_d1_v0.py:1112-1128` runs it once and then checks which of its own wires **died** (`F1v … {len(died)} deleted by it`). Route B v4 calls it inside the row loop with no such check.

In order of preference:
1. **Do not create the debris.** Capture the temp node's wire UIDs before `delete_object`, then delete exactly those Wire objects — the fleet already deletes by class+index (`g.delete_object(target,'Wire',i)`) — and nothing else.
2. **Use the diagram-scoped method, which exists.** `AbstractDiagram.Remove Wire Loose Ends`, short name `RemWireLooseEnds`, **method ID 6375409**, class `AbstractDiagram` (16503): "traverses the referenced diagram and removes all wire ends that are not connected to anything", scoped to the referenced diagram, not the VI ([LabVIEW Wiki](https://labviewwiki.org/wiki/AbstractDiagram_class/Remove_Wire_Loose_Ends_method)). This contradicts the plan's premise that only a VI-wide reaper is available. It is still diagram-wide rather than delete-scoped, so prefer (1).
3. If a VI-wide RBW must run, run it **once at S5, after every row** — never inside the loop — and gate it the way route A does.

## Q4 — does WIRED mean surviving?

**No. It is a mixture, and its weakest members mean only "the call returned without raising."**

| row kind | what the ledger records | verified? |
|---|---|---|
| from-tunnel | `wire 26309, Is Broken? FALSE` (`run7.log:366`) | yes — machine readback |
| `OpConnectNested_v1` | wire uid + count delta (`:389`) | partly |
| `wire_sr` | `wire_sr RightIn reg[1] -> D[24].N[0].T[3]` (`:367`) | **no uid, no readback** |
| plain `wire` | `wire Function[38].'x < y?' -> Function[41].'x'` (`:395`) | **no uid, no readback** |
| `wire_control` | `after` via `next(…, 0)` (`build_d1_routeb_v4.py:1908, 1919`) | **sentinel collision** |

That last one matters for this very diagnosis: `next(…, 0)` returns `0` both for "unwired" and for "no such terminal", so t5's `sink D[24].N[20].T[5] wire 0 -> 0` is **not** evidence that terminal 5 exists. Contrast the from-tunnel path, which uses `.get(t, ("<no such terminal>", None, None))` (`:1798`) and can tell the two apart. The two `#2222` failure modes may well be one failure mode reported by two readers of different quality.

And **nothing re-checks any row at the end.** The bracket removed 96 wires around row 40 of 66; every row wired before it still counts WIRED.

**Cheapest end-of-run verification:** one `set(o["uid"] for o in g.report_all(TARGET,"Wire"))` after S5's RBW, tested against the wire uids the ledger already holds — one traverse, no new op. To cover the rows that record no uid, give `wire_sr`/`wire` the single readback the other paths already do — `next((x["wire"] for x in g.node_terms(TARGET,d,n) if x["i"]==t), None)`, with `None` rather than `0` so absent ≠ bare — and store it. The survival gate itself is not a new device: the pattern is at `build_d1_v0.py:1115-1128`, and route B dropped it.

---

**What would change my mind:** a reading of `#2222`'s index taken from two walks in the *same* run, one with the temp node alive and one after its deletion, showing them differ. That would resurrect H4's mechanism. Run 7 could have produced it for nothing and did not.

**Sources:** [NI — Block Diagram:Remove Bad Wires](https://www.ni.com/docs/en-US/bundle/labview/page/lvscript/vi_block_diagram058remove_bad_wires.html) · [LabVIEW Wiki — Block Diagram.Remove Bad Wires](https://labviewwiki.org/wiki/VI_class/Block_Diagram.Remove_Bad_Wires_method) · [LabVIEW Wiki — AbstractDiagram.Remove Wire Loose Ends](https://labviewwiki.org/wiki/AbstractDiagram_class/Remove_Wire_Loose_Ends_method) · [NI Idea Exchange — tunnel/passthrough wire deletion](https://forums.ni.com/t5/LabVIEW-Idea-Exchange/Automatically-Delete-Passthrough-Wires-when-a-Linked-Tunnel-is/idi-p/2421080)

## Sources

(extract from answer)

## What was done with it

Disposed 2026-09-19 by the cycle-39 judgement session; applied the same day by a MATERIAL session in
`tools/recipes/build_d1_routeb_v5.py` (cut from v4's bytes; v2/v3/v4 untouched, each frozen by its own released
stop record). **H4 — judgement's own hypothesis — is REFUTED BY MEASUREMENT and withdrawn**: `OpCreateEqual_v0`
(v4 `:1521`) and `delete_object` (v4 `:1668`) are both inside the single t0 handler `from_ctl_unnamed`
(v4 `:1444-:1747`), while the sibling `#2222` rows dispatch from the row loop at v4 `:1820` only after it has
returned, so the bracket is tight and cannot shift indices under them. **The reviewer's alternative — a VI-wide
`Remove Bad Wires` fired mid-loop reaping the build's own deliberately-cut wires — is ACCEPTED IN FULL**, and
its three consequences are the three changes below. None touches per-bead computation (rule 1a): K1 removes a
destructive call, K2 and K3 are read-only instrumentation.

FIXED: contradicted - tools/recipes/build_d1_routeb_v5.py:1760 - Q3 accepted: the mid-loop VI-wide `g.remove_bad_wires_scripted(TARGET)` is DELETED and nothing replaces it, because the restructure leaves wires cut between S1d/S3 and this rewiring pass (`build_d1_routeb_v4_run7.log:274-280` lists `#2222`'s five cut input tunnels) and a whole-VI reaper inside the row loop destroys that scaffolding - run 7's -96; R2's natural control stands (run 5 returned NO-ROUTE at v4 `:1606-1609`, never reached the reaper, and wired `#2222` t2/t3/t4/t5), and the temp node's only wire w29238 survived the delete unaided, so no targeted cleanup is owed in its place.
FIXED: helper-exists - tools/recipes/build_d1_routeb_v5.py:520 - Q2's refutation accepted: "this fleet has no per-diagram wire count" was false, so the J2(b) gate now reads Diagram[tdi] alone and logs the VI-wide pair beside it; the count is taken from `build_d1_v0.wmap` -> `build_track_v6_core.walk`, which this recipe already calls for every address, and NOT from `gscript.net_map`, because `net_map` drops an untyped `Invoke` per op run on the target and then calls `remove_bad_wires_scripted(target)` itself (`tools/gscript.py:2507-2516`, `:2568-2588`) - i.e. it would have re-fired, twice, the exact VI-wide reaper K1 removes.
FIXED: unread-evidence - tools/recipes/build_d1_routeb_v5.py:2120 - Q4 accepted in full: every WIRED row now registers the wire uid it claims (`claim_wire`, `:1130`), `wire_sr` and plain `wire` rows take the one-call readback they never took, the `next(..., 0)` sentinel becomes `None` at both `wire_control` sites (`:2036`) so `sink wire 0 -> 0` can no longer pass for evidence that a terminal exists, and a SURVIVAL CENSUS (`set(o["uid"] for o in g.report_all(TARGET,"Wire"))`) runs immediately after the S3w PRE-SETTLE ledger line - placed there, not after S5, because no run has ever reached S5.

Not acted on, recorded: the reviewer's `AbstractDiagram.Remove Wire Loose Ends` (6375409) is NOT built and is
not built here - K1 needs no replacement reaper at all, and building an op would be a new device. The reviewer's
own request to "log the index that comes back from each J1 invalidation" is superseded: H4 being refuted, the
index is no longer the question.
