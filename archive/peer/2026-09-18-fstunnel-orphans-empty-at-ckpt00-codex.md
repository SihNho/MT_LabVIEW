# fstunnel-orphans-empty-at-ckpt00-codex

- **agent:** codex
- **model:** gpt-5.6-sol (effort medium; peer.ps1 default (user, 2026-09-15))
- **kind:** review
- **cost:** 
- **date:** 2026-09-18 12:37:41
- **outcome:** ANSWERED (107s)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

FAILED PREDICTION — the "donor orphan wire" story may be inverted. Attack it.

## The prediction, and what the machine said

Recipe `tools/recipes/build_opfstunnelterm_v1.py` copies a donor VI `OpWireSource_v5.vi` and rebuilds its front
half. Its checkpoint CKPT[00] is `_v1.py:403` (`by = sweep(op)`), immediately after `shutil.copy2(DONOR, op)` +
`open_panel(op)` and BEFORE any construction.

PREDICTED (gate A0a of `tools/recipes/build_opfstunnelterm_v2.py`, and the brief this run executed): on the FRESH
donor copy at `_v1.py:403`, the set of Wire uids that NO owning-node terminal reads at either end ("the orphan
set") is EXACTLY {894, 1356}.

OBSERVED (`tools/bench/diag_fstunnel_preclean_twins.log`, gate P4 FAIL):
  "PRECLEAN @_v1.py:403: 42 wires, 111 node terminals, ExecState 1; orphan set (no owning-node terminal at either
   end) = []"
The orphan set at the fresh copy is EMPTY. Both 894 and 1356 exist as Wire objects at that point (they are in the
42-wire census, and they are in the DONOR FILE's own census), but every one of the 42 wires is carried by at least
one node terminal there.

At the LATER B4 point of the same recipe, the SAME function over the SAME kind of sweep finds them as orphans:
`tools/bench/diag_fstunnel_rbwvictims.log:79-88` ("END NONE" for both), and `remove_bad_wires_scripted` at B4
removes exactly [894, 1356], adds none, 43 -> 41 wires, ExecState 0 -> 1, with no node losing a connection
(133 -> 133 terminals) — reproduced again in this run's twin A:
  "RBW @TWIN A @B4: ExecState 0 -> 1; 43 -> 41 wires; REMOVED [894, 1356]; ADDED []; err ''"

So the same two wires are ATTACHED at `_v1.py:403` and DETACHED by the B4 point.

## The explanation formed under pressure — refute it

E-new: 894 and 1356 are wires of the donor's FRONT SECTION (the `Wire.Terms[]` property node #145 and/or the
`Index Array` #151, and/or the nodes the recipe deletes next). `_v1.py:426-441` deletes Node #145, Node #151 and
the three wires 578 / 639 / 533 by index. Deleting a NODE leaves wires that terminated on it with no node
endpoint, so the recipe's OWN deletes create the two orphans; the donor merely supplies the wire objects in an
attached state. If that is right, then "the donor ships two bad wires" (written into STATUS.md, into
`docs/toolkit-capabilities.md`, and into gate A0a of `_v2.py`) is a mis-statement of the measurement, there is
nothing to pre-clean before construction, and the end-of-build `remove_bad_wires_scripted` is removing debris the
build itself produced.

Attack this. In particular:
 1. Give the strongest reason E-new is WRONG. Is there a reading of LabVIEW's scripting model under which a wire
    can be "on a node terminal" at the fresh copy and legitimately orphaned later WITHOUT any delete causing it —
    e.g. a wire whose endpoints are STRUCTURE terminals (tunnels) rather than node terminals, so that a sweep over
    `OpNodeTerms` of diagram-0 NODES reports it differently depending on what else is on the diagram?
 2. Name an ALTERNATIVE explanation of "orphan set empty at :403, {894,1356} at B4" that does not involve the
    recipe's deletes. Candidates to consider and to attack: the sweep is bounded (`sweep(target, n=120,
    diagram=0)` stops at the first index returning no uid) and at :403 it saw 19 nodes / 111 terminals while at B4
    it saw more nodes / 133 terminals — could the :403 sweep have enumerated DIFFERENT objects (e.g. included a
    node later deleted whose terminals carried 894/1356)? Could `OpNodeTerms`' `wire` column mean something other
    than "the wire attached to this terminal" for an unwired or a broken terminal, such that a stale/garbage uid
    coincidentally matches 894 and 1356 at :403?
 3. What would FALSIFY E-new, and what is the CHEAPEST DISCRIMINATING TEST? Our candidate is: at `_v1.py:403`,
    print the (node uid, terminal name, terminal index, is_source) of every terminal whose `wire` column equals
    894 or 1356, then re-read the same after each of the recipe's deletes. Say whether that test actually
    discriminates, and what a null result (no terminal names them, yet the orphan set is still empty) would mean.
 4. If E-new stands, what ELSE in this project's written record is wrong as a consequence? We claim only that
    gate A0a of `_v2.py` becomes unsatisfiable. Say what else follows.

## Already ruled out — do not spend the answer on these

* Not a reproduction problem: twin A of this same run reproduced the recipe's construction object-for-object
  against run 1 (terms 145 / ia 151 / tmsc 1044 / consumers [157,1319,1326]; site wires 384,384,1694,1719,1719,1766)
  and its B4 `ExecState` is 0, exactly as run 1 measured.
* Not a `Wire.Is Broken?` perturbation: no such read was taken anywhere in this run.
* Not an RBW side effect before B4: the only `remove_bad_wires_scripted` calls in the diagnostic are gated by a
  flag that refuses before a B4 freeze, and the twin B that aborted never called it.
* Not a file-corruption question: all 95 originals are md5-identical before and after, nothing was saved, and both
  scratch VIs were created and deleted in the same run.
* The two wire uids ARE in the donor FILE's own census (`tools/bench/diag_fstunnel_rbwvictims.log:14`) — that part
  is not in dispute. What is in dispute is whether they are ORPHANED in the donor.

## Files worth opening

`tools/bench/diag_fstunnel_preclean_twins.log` and `.py` (this run) · `tools/bench/diag_fstunnel_rbwvictims.log`
(the earlier measurement, 18/18) · `tools/recipes/build_opfstunnelterm_v1.py:376-450` (build_one up to B2) ·
`tools/recipes/build_opfstunnelterm_v2.py` (gate A0a) · `docs/toolkit-capabilities.md` (the donor-orphan claim) ·
`STATUS.md`.



--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

## 1. Strongest reason E-new is wrong

E-new assigns causation without identifying the endpoints. The observation proves only:

- At `:403`, some `OpNodeTerms` rows report `wire = 894` and `wire = 1356`.
- At B4, no such rows remain.

It does **not** prove those rows belong to nodes `#145` or `#151`. Until those carrier rows are identified, “deleting #145/#151 created the orphans” is an unsupported attribution.

LabVIEW’s terminal ownership model makes that omission important. Ordinary node terminals are owned by their nodes, but control terminals can be owned by the diagram rather than the corresponding front-panel object. Structure tunnels also have distinct outer and per-subdiagram inner terminals. Thus, a generic diagram-0 “node terminals” census is not necessarily a complete or uniform model of every endpoint class. [NI Community: terminal ownership](https://forums.ni.com/t5/LabVIEW/Vi-Scripting-inconsistent-behaviour-of-terms-of-a-wire-owner/td-p/3309055), [NI Community: inner and outer tunnel terminals](https://forums.ni.com/t5/LabVIEW/LabvVIEW-Scripting-wiring-a-pass-through-tunnel-inside-a-case/td-p/3945608)

That supplies a plausible way for the reporter’s classification to change after structural editing or diagram fix-up without the explicit deletions being the causal event. It does **not**, by itself, show that structure terminals spontaneously disconnect merely because more nodes exist.

There is also contrary pressure against this attack: LabVIEW practitioners deliberately wire through temporary generic nodes and then delete those nodes, leaving the intended wire geometry behind. NI material likewise treats deleting diagram objects and subsequently running “Remove Bad Wires” as normal behavior. Those observations make E-new mechanically plausible, even though they do not identify these two wires. [NI Community: temporary bundle nodes deleted while wire remains](https://forums.ni.com/t5/LabVIEW-APIs-Discussions/What-is-up-with-the-DeleteJoint-method/m-p/3384955), [NI user manual example](https://download.ni.com/support/manuals/320999b.pdf)

## 2. Alternative explanation

The strongest alternative is a **reporter-semantic or diagram-fix-up transition**, not bounded enumeration by itself:

1. At `:403`, `OpNodeTerms` returns two terminal records whose `wire` field is 894/1356.
2. Those records are not true current endpoints of the Wire objects—for example, they are structure-related proxy terminals, stale associations exposed before diagram recompilation, or reporter output whose `wire` column has broader semantics than “this terminal occurs in `Wire.Terms[]`.”
3. A later construction operation forces LabVIEW to normalize the diagram, removing those associations.
4. The wires then appear orphaned at B4 even if neither carrier was one of the explicitly deleted nodes.

This is plausible enough to test because LabVIEW’s scripting object graph is not ownership-uniform, and tunnel terminals have inner/outer representations. It is not yet supported by direct evidence.

The bounded `sweep(..., n=120)` theory is weaker:

- Missing later nodes or terminals can make the algorithm report **too many** orphans.
- It cannot normally explain an empty orphan set: to suppress 894 and 1356, the sampled rows must positively contain those exact values.
- The fact that `:403` enumerates a node later deleted is not an alternative to E-new. If that node’s real terminals carry the two wires and its deletion removes those connections, that is precisely E-new.
- More terminals at B4 should provide more opportunities to find carriers, not fewer. The reversal therefore suggests actual carrier loss or changed semantics, not merely a larger census.

An accidental or stale UID match remains possible, but it requires showing that `OpNodeTerms.wire` is not a direct live attached-wire reference. NI’s conventional scripting approach is to obtain a node’s `Terminals[]` and navigate from the terminal to its connected wire, so a persistent nonzero wire reference should ordinarily be treated as meaningful until contradicted by `Wire.Terms[]`. [NI Community: navigating node terminals and using terminal properties](https://forums.ni.com/t5/LabVIEW/Scripting-Terminal-Information/td-p/4303374)

## 3. What would falsify E-new

Any of these observations would falsify its causal claim:

- At `:403`, every carrier of 894/1356 belongs to objects that survive through B4.
- The carriers remain present immediately after deleting `#145`, `#151`, 578, 639, and 533, but disappear after a later non-delete construction operation.
- Direct `Wire.Terms[]` inspection at `:403` shows that neither wire actually contains the supposed `OpNodeTerms` carrier terminals.
- Skipping the suspect deletes while executing the remaining construction still produces `{894,1356}` as B4 orphans.
- Performing only the suspect deletes fails to produce those orphans.

Conversely, E-new receives strong causal support if the named carrier terminal belongs to `#145` or `#151`, disappears immediately when that node is deleted, and the same Wire UID remains in the diagram with no other endpoint.

## 4. Does the proposed test discriminate?

Yes—with one addition.

Printing `(node uid, terminal name, terminal index, is_source)` for every row naming 894/1356 before and after each delete is the correct first test. It identifies the presently missing causal fact: who carries the wires and exactly when that carrier disappears.

However, also print each wire’s own `Wire.Terms[]` terminal identities. Otherwise both the orphan calculation and the proposed test depend on the same `OpNodeTerms.wire` column and cannot detect a shared reporter-semantics bug.

A null result—no terminal rows name the wires even though the computed orphan set is empty—would mean the diagnostic is internally inconsistent. Likely causes would be cached data, a different sweep instance feeding the reducer, UID coercion/collision, or hidden carrier classes not included in the printed subset. It would invalidate both the fresh-copy conclusion and E-new until the orphan reducer’s actual inputs were dumped.

## 5. Consequences if E-new survives

More than gate A0a changes:

- A0a is unsatisfiable if it demands `{894,1356}` on every untouched fresh donor copy.
- The statements that the donor “ships two orphan/bad wires” in `STATUS.md` and `docs/toolkit-capabilities.md` are false. The donor ships two attached wires that later become debris.
- Any pre-clean step that deletes 894/1356 from the untouched donor is not merely unnecessary; it risks deleting valid attached wiring.
- The B4 `remove_bad_wires_scripted` result remains valid, but its interpretation changes from donor sanitation to cleanup of build-produced damage.
- The 18/18 reproducibility establishes deterministic B4 victims, not donor-origin orphanhood.
- Any donor-quality conclusion, recipe invariant, or test fixture derived from the claimed fresh-copy orphan set must be revised.
- The cleanup may be masking a construction defect. The better repair could be to prevent the orphan-producing edit or explicitly disconnect/delete the affected wires when removing their owners, rather than relying on a global cleanup afterward.
- Claims such as “RBW removes no live connections” remain supported at B4 by the unchanged terminal count, but they do not show that earlier valid donor connectivity was preserved.

After attacking it, I still think E-new is the leading explanation: the count arithmetic is compatible with it, deletion is known to leave bad-wire remnants, and the bounded-sweep theory has the wrong error direction. What would change my mind is seeing the two fresh carrier terminals belong to surviving objects, or seeing the transition occur at a non-delete operation.

The cheapest discriminating test is: at `:403`, dump the two wires’ `Wire.Terms[]` plus all matching `OpNodeTerms` rows; then repeat immediately after each individual deletion. If the carrier is `#145/#151` and vanishes on that deletion, E-new wins. If it survives all deletes and disappears later, the fix-up/reporter alternative wins.

## Sources

(extract from answer)

## What was done with it

disposition: RELAYED TO JUDGEMENT (cycle 23, dispatch 4, material session, 2026-09-18 12:5x). Arm 1 of a `-Dual`
failed-prediction review; arm 2 = `2026-09-18-fstunnel-orphans-empty-at-ckpt00-opus.md`.

- **Outcome classified:** `ANSWERED` in 107 s, gpt-5.6-sol / effort medium; the CLI reports no cost line
  (`tools/bench/peer_orphans_empty.log`). Both arms rc=0 ("DUAL DONE: codex rc=0, opus rc=0").
- **Its central verdict:** E-new is the leading explanation, and the cheapest discriminating test is to dump each
  wire's carrier rows at `_v1.py:403` and again after each individual delete (`:175`).
- **THAT TEST WAS RUN, and it CONFIRMS E-new** — `tools/bench/diag_fstunnel_orphan_timeline.log` (8/9 gates; the
  one FAIL is the checker's own docstring, not a measurement): at `_v1.py:403` the orphan set is EMPTY and
  **#894 is carried by node #145 `error out` T[3] (source) and #1356 by node #151 `index` T[2] (sink)** — the two
  nodes the recipe deletes next — and the orphan set becomes exactly `[894, 1356]` at the FIRST checkpoint after
  those deletes (`_v1.py:442`), where `ExecState` also goes **1 -> 0**. It stays 0 through all six wire sites
  (every site reads `ExecState BEFORE = 0`) to the B4 freeze.
- **The one caveat NOT addressed, recorded rather than waved away** (`:156`): the orphan reducer and the carrier
  test both read the same `OpNodeTerms.wire` column, so a shared reporter-semantics bug would be invisible to
  both. The reviewer's addition — dumping each wire's own `Wire.Terms[]` identities — was NOT run in this
  dispatch.
- **Its consequences list (`:160-172`) is NOT acted on here**: whether gate A0a, the donor-orphan sentences in
  `STATUS.md` / `docs/toolkit-capabilities.md`, and `_v2.py` itself are now wrong, and what replaces them, are
  judgement decisions. Left open, with the measurement above beside them.
