# s0run1-closeorder

- **agent:** claude
- **role:** hypothesis
- **model:** opus (effort max; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $3.6393  in 26 / out 40579 / cache-create 167398 / cache-read 1612876  (534s, 23 turn(s))
- **date:** 2026-09-19 18:32:27
- **outcome:** ANSWERED (538s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. It is the explanation a material session formed, under time pressure, for the two failures of
`tools/bench/build_s0_closeref_v1.log` (recipe `tools/recipes/build_s0_closeref_v1.py`, D1 stage S0). Do not
confirm it. Name the strongest reason it is wrong, an alternative explanation, what would falsify it, and the
cheapest discriminating test. You may read the project directory read-only.

=== WHAT THE BUILD IS ===
S0 restores `Close Reference` to three of our own VI-Scripting "op" VIs, as NEW files, so each op closes the
array of GObject references its `Traverse for GObjects.vi` returns (CLAUDE.md reference hygiene). The design,
prescribed by an earlier prior-art review and adopted by a judgement session, is:
a For Loop AUTO-INDEXING the Traverse `References` array, with `Close Reference` inside the body, so the scalar
refnum input is fed ONE refnum per iteration. Targets: OpReport_v3 -> OpReport_v4, OpWireSource_v5 -> _v6
(neither has a loop: one is created), OpReportAll_v0 -> OpReportAll_v1 (it ALREADY has that loop, with two
Property nodes in the body).

=== THE PREDICTION THAT FAILED ===
The recipe predicted, in gates, that each of the three stages would end with a SAVED, runnable (ExecState 1)
repaired op. RESULT: 41 PASS / 2 FAIL, `BGRUN END rc=1 after 566s`, NO VI SAVED at all.
  * `build_s0_closeref_v1.log:47-49` - stages 1 and 2 (the no-loop ops) raised
    `AttributeError: 'set' object has no attribute 'index'` inside the recipe's `tun_index`, which called
    `gscript.uids(target, "LoopTunnel").index(uid)`; `gscript.uids()` returns a SET.
  * `:114-118` - stage 3 (OpReportAll_v1) failed its own gate G3c "exactly ONE last Property node in the body's
    reference chain", because BOTH body Property nodes qualified: PN #114 reads its reference on wire 421 and
    PN #115 on wire 548, and BOTH have `reference out` = 0 (neither passes the reference through).

=== THE CLAIM YOU MUST ATTACK ===
(1) Both failures are the material session's own coding defects, NOT evidence against the For-Loop design.
(2) The design is sound and was measured working as far as it got: at `:32-33` the `References` array wire (w188)
    was branched INTO the new For Loop body by the built writer `OpConnectFromWire_v0` on the FIRST attempt -
    sink terminal reads back wire 636, the op's own `Wire.Is Broken?` reads False, and a new LoopTunnel #642
    appeared. So the archived warning that `Close Reference`'s refnum input "defeated four wiring attempts"
    (`archive/WORKLOG.md:84-86`) does not apply to this route, because the array is never wired into that input.
(3) The repair for stage 3 is: since the two body Property nodes are PARALLEL rather than error/reference
    chained, feed `Close Reference`'s `reference` from ONE Property node's `reference out` pass-through and its
    `error in (no error)` from the OTHER Property node's `error out`. The claim is that this makes the close
    execute AFTER BOTH property reads, so no reference is closed while it is still being read.
(4) Nothing else in the run needs to change: with `tun_index` reading `report_all` order instead of a set, the
    remaining steps (set the References tunnel IndexMode to 1 so the array supplies N; branch the panel
    `error out` net into the loop as a NON-indexed tunnel to order the close after the property reads on the top
    diagram) will reach ExecState 1.

=== ALREADY RULED OUT (do not spend the answer on these) ===
* NOT the handle count: the kernel handle count cannot see VI Server refnums at all (`tools/gscript.py:227-228`),
  which is why the acceptance gates are "no `error 2` in 20 calls", "handles flat +-100 FROM CALL 1" and
  "private bytes drift <= 5 MB".
* NOT a claim that this repair fixes LabVIEW `error 2`: a judgement session withdrew that premise on measurement
  (`docs/cycle27-plan.md:329`; 20 x report_all(Diagram) = 3,400 matched objects moved handles +9 with no
  `error 2`). S0 is rule compliance only.
* NOT the `Open VI Reference` refnum: deliberately NOT closed, because chained ops want the target in memory
  (`tools/gscript.py:1293-1295`).

=== WHAT WOULD BE MOST USEFUL ===
Attack (3) hardest: is "refnum from node A's pass-through + error in from node B's error out" really sufficient
to order a `Close Reference` after BOTH parallel property reads inside a For Loop body, in LabVIEW dataflow? If
it is not sufficient, say exactly what execution can still interleave and what the cheapest correct ordering is
using only nodes that already exist. Second, attack (2): is there any reading of `build_s0_closeref_v1.log:32-33`
under which the branch did NOT actually succeed?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**REFUTED.** The claim's central factual premise — that `OpReportAll_v0`'s two body Property nodes are PARALLEL — is false, and this project's own build record of that VI says so. Write is disabled for this role, so the review is below.

---

## 1. Strongest reason the claim is wrong: the body is a CHAIN, and it mints a second reference

`tools/recipes/build_opreportall_v1.py` is the build record of the very VI being repaired:

| step | what it built |
|---|---|
| `:144-149` | **PN1** = Property on `VI Server:GObject`, items Position · UID · ClassName · **Owner**, inside the body |
| `:158-160` | `g.wire(... "References", "Property", pidx(pn1_uid), "reference")` — PN1 fed by the auto-indexed `References` tunnel |
| `:162-165` | **PN2** = Property on `VI Server:Generic`, item ClassName |
| `:168-171` | `g.wire(OP, "Property", pidx(pn1_uid), **T_OWNER**, "Property", pidx(pn2_uid), "reference")` |

**PN2's `reference` is PN1's `Owner` output.** They are chained — through a property *output* that returns a NEW reference, not through the `reference` pass-through the gate inspected. "Both `reference out` = 0" (`log:116-117`) is true and irrelevant. The wire uids corroborate the build order: w421 (PN1.reference, step 6) < w548 (PN1.Owner → PN2.reference, step 8).

Three consequences:

- **(a) The stated reason for the two-wire repair is false.** "One dependency cannot order a close after both" (`build_s0_closeref_v1.py:99-104`, repeated verbatim in `build_s0_closeref_v2.py:118-120,:360`) — PN2 is *already* downstream of PN1, so a single dependency on PN2 orders the close after both.
- **(b) The repair leaves one reference per iteration unclosed.** Each iteration PN1 mints an `Owner` reference that PN2 consumes and nothing closes. NI: "If you open a reference … LabVIEW creates a new reference every time"; the analogous `Owning VI` property's help says "Close this reference when you are finished using it." So S0 would close N traversed refs and leak N owner refs — and the gates cannot see it, by the session's own citation (`tools/gscript.py:227-228`). The scope claim at `build_s0_closeref_v1.py:62-63` is not this op's whole hygiene obligation.
- **(c) Node selection is provenance-blind.** `p_ref = next((u for u in body_pns if tab[u]["ref_out"] is not None))` over `body_pns = sorted(...)` (v1 `:348`, v2 `:366`): *every* Property node has a `reference out` terminal, so gate G3c is vacuous and the choice is "lowest UID". It picks PN1 by accident of numbering. If that order ever differs, the repair wires the close to **PN2**'s pass-through — closing the `Owner` ref, leaving the traversed element open, inverting the stage's purpose, at ExecState 1, passing every gate.

**On your direct question — is "refnum from A + `error in` from B" sufficient to order the close after both?** Yes, as ordering. A LabVIEW node fires only when every wired input has data, so `Close Reference` waits for both. That is not the defect. The defect is that it is the wrong repair for a chain that mints a second reference, and that the error wire carries a *known* fault: PN2 is precisely the node documented to raise **error 1055 "Object reference is invalid"** on class `Diagram` — `fix_opreportall_errors.py:1-15`, "most likely the `Owner` of the top-level diagram, which is the one object in the traversal with nothing above it" — which is why auto error handling was disabled. Claim (3) routes that error into `Close Reference.error in`, on the class this recipe's own equivalence gate exercises (`log:129`). **The evidence does not settle whether the close then still happens:** NI documents `Close File` as closing "regardless of whether an error occurred in a preceding operation", and cleanup nodes generally follow that pattern, but the LabVIEW Wiki page for `Close Reference` is a stub and I found no NI statement for it. Buying that uncertainty for ordering PN2 already provides is a bad trade.

## 2. Alternative explanation of `log:32-33` — a reading where the branch did NOT succeed

The line reads `connect_from_wire(References) dw=1 **ExecState=0** err='' sub={'UID 2': 636, 'Is Broken?': False}`.

The prior art the recipe says it follows records the opposite for the same step — `docs/toolkit-capabilities.md:438`: "wire References across the boundary → LoopTunnel 0->1, **ExecState 0->1** ← the array supplies N". That flip to 1 *is* the evidence of auto-indexing. S0 got 0. S0 also did not use that route: the measured one is `g.wire()` after deleting the Index Array to free the source (`build_opreportall_v1.py:127-130`); S0 must preserve it, so it substituted a branch. And `gscript.wire`'s own docstring says the definitive check on a crossing is "the EFFECT (**ExecState**, or the tunnel appearing)" (`tools/gscript.py:1361-1362`) — the gate took the tunnel half and ignored the ExecState half pointing the other way.

**Alternative:** the tunnel was not auto-indexing, so wire 636 carried the whole array into a scalar refnum input — the configuration the four archived failures are about — and `Is Broken? False` is the anomaly to explain (type propagation not yet run), not the reassurance. This project has already measured that shape twice: `tools/gscript.py:1293-1295` — "the **branch into a … Property Node's `reference` lands as a BAD wire (uid 467, ExecState 0, remove_bad_wires does not clear it)**" (`tools/bench/diag_bdloaded_reader.log`). The session cited that same paragraph for a different point (`:64-67`) and did not notice it records this failure mode.

Decisively: the run crashed in `settle_tunnel` at `i = tun_index(dst, u)`, and the `note()` printing `index_mode` is the **next** statement (v1 `:239,:263-265`). **The index mode was never read.** Claim (2) converts "we never measured it" into "it was measured working" — about a VI that no longer exists (`log:136` G-A0 FAIL; stubs deleted at `:51,:95,:120`), which under the user's 2026-09-19 rule means nobody can open it to check.

In fairness: ExecState 0 there is *also* consistent with an innocent mid-build state. The log cannot distinguish the two — that is the point.

## 3. What would falsify this review

Falsifies **me**: a body census showing PN #115's `reference` sourced from a **LoopTunnel** inner terminal (two independent auto-indexed tunnels off one array), not from #114's `Owner`; plus the input tunnel reading `IndexMode == 1` immediately after `connect_from_wire`.

Falsifies the **claim**: `wire_source_owner(RA_V0, 548)` returning owner uid **114** with source terminal `Owner`; and/or `IndexMode == 0` on the tunnel `connect_from_wire` created.

## 4. Cheapest discriminating test

One read-only script, no edits, no saves, no new op, ~2 minutes — every call already exists:

```python
g.net_map(RA_V0, 1)                        # body: node → terminal → wire (used at build_opreportall_v1.py:102)
[g.tunnels(RA_V0, i) for i in range(g.count(RA_V0, "LoopTunnel"))]   # IndexMode + inner/outer wires
wire_source_owner(RA_V0, 421); wire_source_owner(RA_V0, 548)         # who drives each PN's `reference`
```

In one run this settles: chain vs parallel; which PN carries the auto-indexed traversed reference (the provenance the selection code lacks); whether an `Owner` reference is minted and left unclosed; how many tunnels the loop has. **Stage 3 needs no build to be decided.**

Second arm, scratch copy, saves nothing: run `connect_from_wire` and `g.wire` into a fresh For Loop and print `index_mode` and `exec_state` *immediately after each* — separates "branch is fine, IndexMode just needed setting" from `gscript.py:1293-1295`'s bad-wire result.

## Not disputed

`gscript.uids()` returning a set (`tools/gscript.py:1021`) is plainly a coding defect. What does not follow is claim (1)'s second half and claim (4)'s "nothing else needs to change": in stages 1–2 the design was never exercised past the crash point, so the log is silent on it rather than supportive.

**Sources:** [Closing References in LabVIEW — NI](https://www.ni.com/en/support/documentation/supplemental/13/closing-references-in-labview.html) · [Generic class/Owning VI property — LabVIEW Wiki](https://labviewwiki.org/wiki/Generic_class/Owning_VI_property) · [Generic class/Owner property — LabVIEW Wiki](https://labviewwiki.org/wiki/Generic_class/Owner_property) · [Close File (G Dataflow) — NI](http://www.ni.com/documentation/en/labview/latest/node-ref/close-file/) · [Close Reference function — LabVIEW Wiki (stub)](https://labviewwiki.org/wiki/Close_Reference_function)

## Sources

(extract from answer)

## What was done with it

**The material session TESTED the review instead of arguing with it, and the machine sided with the review.**
`tools/bench/s0_body_census.py` (NEW, read-only, no edit/save/new op — `BGRUN END rc=0 after 1s`, **7 PASS / 0
FAIL**, `tools/bench/s0_body_census.log`) ran §4's discriminating test with ONE substitution, stated in its own
docstring: `g.net_map` was NOT used, because `docs/cycle27-plan.md` Pre-decided 17 bans it as an instrument —
it calls `remove_bad_wires_scripted(target)` internally and would have WRITTEN to one of our op VIs. `walk` +
`wire_source_owner` + `gscript.tunnels` answer the same three questions read-only.

MEASURED, and it settles §1 against this session's reading:

- **The body is a CHAIN.** `s0_body_census.log:47,:49` — `#114 'Owner'` is a SOURCE carrying **w548**, and
  **w548 is `#115`'s `reference` input**; `:60` confirms it from the wire's own terminals (source owner
  `Property#114`, sink `Property#115`). `:58`/`:68` — w421's source is **LoopTunnel #511**, the `References`
  input tunnel, **IndexMode 1**. So run 1's "the two Property nodes are PARALLEL" (`build_s0_closeref_v1.log:
  114-117`) was an inference from "both `reference out` = 0", and the review is right that this is true and
  irrelevant: they are chained through a property OUTPUT, not through the pass-through.
- **Consequence (b) therefore has a live premise**: `#114.Owner` mints a NEW reference every iteration
  (`:47`), and neither v1 nor v2 closes it. Whether S0's scope must grow to cover it is NOT decided here.
- **Consequence (c) is confirmed as a real hazard**: `_finish_loop_exists` picks its refnum source by lowest
  uid, which on these bytes happens to be #114 — correct by accident, not by provenance.
- **§2 (did run 1's `References` branch really succeed?) is NOT settled.** This census measured the ORIGINAL
  op, where the tunnel is IndexMode 1; it says nothing about the tunnel `connect_from_wire` created in run 1,
  which was never read (the crash was the next statement) and whose VI no longer exists. The review's second
  arm — a scratch-copy run printing `index_mode` and `exec_state` immediately after each write — remains the
  open test.

**ACTIONS TAKEN:** none to the repair. `tools/recipes/build_s0_closeref_v2.py` (the retry, with run 1's two bug
fixes) is **NOT LAUNCHED**; a 🔴 block at the top of its docstring records this refutation and points here.
Accepting a review and changing a design are judgement acts (CLAUDE.md §3), so the two questions above go to the
judgement session as OPEN, with the measurements already taken. `OpReportAll_v0.vi` md5
`ffcec2c75e92dcad514299ba20e66054` identical before and after the census (`:74`); the route-B original's md5 was
verified unchanged after run 1 (`build_s0_closeref_v1.log:139`). No VI was saved by any run in this cycle.
