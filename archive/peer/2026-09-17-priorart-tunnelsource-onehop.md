# priorart-tunnelsource-onehop

- **agent:** claude
- **model:** opus (effort high; pinned by -Model/-Effort (role priorart))
- **kind:** fact
- **cost:** $5.0663  in 50 / out 33735 / cache-create 232648 / cache-read 3792372  (453s, 42 turn(s))
- **date:** 2026-09-17
- **outcome:** ANSWERED (457s)
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
# PLAN under review: the ONE-HOP tunnel-source reader (`OpTunnelSource_v0`), docs/d1-build-plan.md 짠11r

## What is being built, exactly

For each of the 16-17 `from-tunnel` re-wire rows of `tools/bench/build_d1_v0_run7.log:280-325`, resolve the
**other end of the OLD tunnel's outside wire**, then wire from that terminal into the new loop body with
`OpConnectNested_v1.vi` (BUILT + SAVED this cycle, 14,666 B, ExecState 1 warm and cold; cross-diagram by INDEX;
LabVIEW creates the new tunnels itself - `tools/bench/test_opconnectnested_v1_cold.log`, 7/0).

The reader itself, one hop only:

    IN : vi path + the Traverse `LoopTunnel` index of the OLD tunnel (or its uid)
    OUT: for the tunnel's OUTSIDE terminal's connected wire, EVERY terminal on that wire, each with
         `Is Source?`, owner class, owner uid, and that terminal's INDEX within its owner
         (Nodes[]/Terminals[] index when the owner is a node; the tunnel index when the owner is a tunnel)

Route considered FIRST (the cheapest, and the reason this dispatch exists): **do not build a new VI at all** -
compose two ops that are already on disk:
  * `gscript.tunnels(target, index)` (`OpTunnels_v0.vi`, `tools/gscript.py:887-922`) already returns the tunnel's
    uid, `IndexMode`, and **`out_wire`** = the OUTSIDE terminal's connected wire uid.
  * `OpWireSource_v5.vi` (`tools/recipes/build_opwiresource_v5.py:155-174`) already takes (vi path, wire uid,
    terminal index) and returns `Is Source?`, owner class, owner uid and the terminal's reciprocal wire.
  * the terminal's index WITHIN its owner is then derived in Python from `gscript.node_terms()` /
    `gscript.tunnels()` by matching the wire uid - no LabVIEW capability is missing for it.
A new op VI is built ONLY if that composition is measured to fail.

## Iteration, and why it is not a walker

If a returned owner is itself a tunnel, the SAME one-hop read is repeated on that tunnel **from Python** until the
owner is a non-tunnel node, or a terminal on `Diagram 19` / the outer diagram (which `OpConnectNested_v1` can
address directly). No owner CHAIN is walked inside LabVIEW; only the wire's other end is read.

## The four objections of `archive/peer/2026-09-17-priorart-connectnested-v1.md` (recorded in d1-build-plan.md
## 짠11q.2) and how 짠11r answers each - attack these answers

1. **"The premise is contradicted: the 17 rows' sources are a CHAIN further out, and `d1-route-b-plan.md:316-318`
   says there is no named origin to find."** ANSWER: 짠11r no longer needs an ORIGIN. It needs the wire's other
   END, whatever it is - named or unnamed, node or tunnel - because `OpConnectNested_v1` addresses terminals by
   INDEX and creates its own tunnels. A chain is handled by iterating the one-hop read from Python with an explicit
   termination rule (non-tunnel owner, or a terminal on the outer diagram). "No NAMED source" was a limitation of
   the NAME-addressed writers, which no longer bounds the build.
2. **"The back half is `OpWireSource_v5`, which failed its own published control: 0 rows, error 1055"
   (`tools/bench/diag_d1_full_route.json:49-52`, STATUS OPEN 28c), so an additive build inherits the defect."**
   ANSWER: the 1055 is MEASURED FIRST, not inferred - the run's first gates read `exec_state` of
   `OpWireSource_v5.vi` and `OpTunnels_v0.vi` on disk, and re-run the op's own published control (wire 10850 on the
   working copy, which `docs/NAMES.md:946` records answering 12/12) with and without `open_panel`. The same JSON
   records `execstate_discriminator` = 0 for all three arms of that failed run, so "the op VI itself is broken on
   disk / the target was at ExecState 0" is a live and cheap explanation that has never been read from the machine.
   If the control does not reproduce 12/12, the reader is NOT built on that back half and the run stops with that
   fact.
3. **"Short names: `Tunnel.Outside Terminal` 6356001 is `Outer Term`, `Node.Terminals[]` is `Terms[]`,
   `Terminal.Connected Wire` is `Wire`, `Is Source?` is `IsSource`; and 6356001 / `ControlTerminal.Control`
   6353000 are UNVERIFIED in `docs/vi-server-ids.json`."** ANSWER: no new property node is created by the
   composition route - `OpTunnels_v0` already carries `Outside Terminal` (verified, `tools/bench/test_optunnels.log`)
   and `OpWireSource_v5` already carries `Terms[]` / `IsSource` / `Wire` / `Owner`. No unverified ID is used.
4. **"`Generic.Owner` returns a GENERIC reference, so that hop needs its own cast, and `OpOwnerChain_v1`
   terminates silently at a `FlatSequenceFrame`."** ANSWER: `OpWireSource_v5` already contains that cast (its
   `Owner -> To More Specific Class -> UID` branch, rewired and gated at `build_opwiresource_v5.py:98-124`), and no
   owner chain is walked at all - one hop, one owner, then Python.

## What the run will do (prediction contract)

* P0 original working copy md5 `2a78e17c449cacdaf5da389818526859` before AND after; handles recorded; no original
  opened for writing; all work on a COPY under `user.lib\claudeDev`, deleted in the same run.
* P1 `exec_state` of `OpWireSource_v5.vi` and `OpTunnels_v0.vi` read and reported (the 1055 question, measured).
* P2 the op's own published control re-run: wire 10850 -> exactly one source terminal.
* P3 three `from-tunnel` rows resolved one hop and checked against `tools/bench/d1_step0_census.json` and
  `tools/bench/diag_autofocus_border.log` (w3268's known source) - e.g. `#5058` t2 <- tunnel `#2580` outer wire
  w3853; `#376` t7 <- tunnel `#2213` outer wire w2187 (census: a source terminal of `#637`, diagram 19, i 37);
  `#5058` t12 <- tunnel `#3656` outer wire w3668.
* P4 all 16-17 rows resolved to `(diagram index, node index, terminal index)` triples, written to
  `tools/bench/d1_tunnel_sources.json`, with any unresolved row reported as unresolved, not guessed.

## The question for this review

Has this reader - or this composition - already been built, already been measured, or already FAILED here under
another name? And is any fact cited above contradicted by our own files?


=== STATUS.md IN FULL (the project's current decisions and state) ===
---
type: status
status: current
date: 2026-09-17
tags: [hand-off]
---

# STATUS ??read this first. One screen. Detail is one layer down, never appended here.
Narrative ??the `archive/2026-09-17-status-*.md` set (**`??d1-full-build-5.md` = the latest session**)
+ `archive/2026-09-16-??. ?좑툘 **ONE SESSION AT A TIME** ??re-read `CLAUDE.md` + this.

## START HERE
1. **`docs/pre-rig-master-plan.md` is THE plan**; decisions **`docs/decisions.md`**; cycle `docs/cycle15-plan.md`;
   **build plan `docs/d1-build-plan.md` (REV 4 + 짠11c?벬?1q)** ??짠5/짠5a-bis (moves), 짠10 (S/N1/F1/F2), **짠11p is
   the USER's route-A decision and 짠11q is what its prior-art review changed and BLOCKS; 짠11n.2's "unbuildable"
   is WITHDRAWN**. 2. ?좑툘 A prior-art dispatcher's log MUST be named `priorart_*` /
   `peer_*` (`tools/logclass.py`) or the guards read the reviewer's prose as a build failure. 3. ??Scripting EDITS
   need the target's FRONT PANEL open; a fixed op PATH is served from LabVIEW's MEMORY ??unique scratch name/run.
4. ??`guard_cycle` releases on a `FIXED: <slug> - <path>:<line> - ?? line under a prior-art archive's "What was
   done with it" (짠11g.3) ??ONE PER SLUG, or `REFUTED:` with the citation opened. 5. ?좑툘 `peer.ps1` only as
   `powershell -Command "& 'tools/peer.ps1' ??-Task (Get-Content -Raw <f>)"` ??`-File` loses a multi-line `-Task`;
   and `tools/prior_art_review.py` must be launched from **PowerShell**, not the Bash tool (rc 127 there today).

## LabVIEW execution lock

```yaml
labview-lock:
  status: released
  owner:
  since:
  purpose:
# 2026-09-17 13:1x-13:4x material/cycle15-d1-route-A-last: RELEASED. LabVIEW restarted TWICE (bench_prep, 31,3xx
# -> ~34,000 each). ??`OpConnectNested_v1.vi` BUILT + SAVED (14,666 B, ExecState 1 warm AND cold) ??the
# CROSS-DIAGRAM wire creator 짠11n called unbuildable. Runs: diag 10/0 쨌 build run 1 rc=1 (Python TypeError in the
# recipe's own hook, no LabVIEW fact) 쨌 build run 2 31/1 쨌 cold test 7/0. 3 scratches, ALL created and deleted in
# the same run, `claudeDev\SCRATCH*` verified empty. ORIGINAL never opened; md5 2a78e17c449cacdaf5da389818526859
# before AND after every run. Donor `OpConnectNested_v0` + NI example md5 unchanged. No GUI, no hardware.
# build_d1_v0 NOT run ??짠11p item 2 is blocked by its own prior-art review (see NEXT). Handles 31,270 -> 31,673.
# Earlier sessions, all RELEASED, originals md5 2a78e17c449... before AND after, no leftovers, no GUI, no hardware:
# open35-run-poison-fix (11/0) 쨌 d1-full-build-5 (OpConnectNested_v0 BUILT+SAVED, 14,234 B) 쨌 build-4
# (OpCreateConstOnTerm_v0 22/0, run 7 55/7) 쨌 build-3 (run 6 56/1) 쨌 phase-full-2 쨌 run 5 53/0. -> archive/
# 2026-09-17-status-d1-full-build-{4,5}.md (the two newest relocated VERBATIM at the END of -5).
```
**Never assume an instance exited**: `tasklist | grep -i labview`. Fresh ??1,500 handles; unique scratch name/run.
## HARDWARE ??permission follows the RIG STATE. Current: **遺꾪빐 / DISASSEMBLED ??everything allowed**
**遺꾪빐 ??WE ARE HERE** = motors ??ASI ??camera ??쨌 議곕┰ = ??????쨌 ?ㅽ뿕以?= ?????? ?좑툘 The ASI carve-out is
**RETIRED** (rule 1b); **only the user announces a state change**. Rotor counter **0** 쨌 magnet full travel 쨌 camera
1280횞1024, offsets 0, 90.0009 Hz, never write `BinningHorizontal`; **a session open RESETS ROI *and* exposure** ??
the acquisition loop applies `tools/bench/camera_contract.py`. **No beads while disassembled.**

## Where things stand
**Stage 1 CLOSED**. **Stage 2**: `?쪪PU_core_v0` 69/69 쨌 `??queue_v0` 162/162 ??**say it exactly:** bit-identical
for the **first 10,018 frames only**, both **replay** artefacts. **THE GAP:** 173 ops, 121 recipes, 231 peers ??**zero runnable experimental VIs**.

## OPEN ??one line each; long forms in `archive/2026-09-17-status-cycle15-narrative.md` (+ `??d1-phase-full-?? 짠0c)
1??, 5, 9??2 ??**archive 짠9**: PERIODIC auto-reset ungated 쨌 autofocus CLOSED (3.6 Hz) 쨌 27 undisposed peer
   archives 쨌 startup drives instruments 쨌 A2 54/54, A3 112/170 쨌 doc lint 2/4/3. **18 CLOSED by 짠11h ??no TIFF is
   written any more.** 13/14/15b/17b: ??stop measured (`#637` term **648 ??w3457 ??#11639**) 쨌 ?뵶 `bgrun --detach`
   misses an orphaned grandchild 쨌 ?뵶 v3's R11 scored the *restart*, so the stop is unproven.
16 쨌 19/25/26 쨌 20??3 쨌 27 쨌 28 쨌 28b 쨌 28c/d/e 쨌 29 쨌 30/30b/30c ????CLOSED, relocated VERBATIM to
   `archive/2026-09-17-status-d1-full-build-5.md`: GPU kernel accepted for now 쨌 PLAN = REV 4 + 짠11c?벬?1h,
   transport = queues only 쨌 relocation MEASURED (`WhileLoop 3??`, `Diagram 170??73`, 23 moves, 8 SRs, panel 114;
   **109 terminals / 24 uids**, source map **109/109**) 쨌 `OpCreateConstOnTerm_v0` 22/0 쨌 `diag_d1_full_route`
   retired (`OpWireSource_v5` = 1055 here, and that 1055 now BLOCKS 짠11p item 2 ??짠11q.2) 쨌 `OpStopFromNode_v0`
   T5 closed (0 ??387, ExecState 1) 쨌 짠11h: the TIFF writer is not original, F1 uncapped.
28f 쨌 31 쨌 32 쨌 34 ??**relocated VERBATIM to `archive/2026-09-17-status-open-28f-35.md`**, one line each:
28f. ?뵶 run 7, PHASE "full" stage 1: 66 routable rows ??**35 WIRED, 7 FAILED (5001), 24 NO-ROUTE** (17 `from-tunnel`),
   ExecState **0**, nothing saved ??**N1/F1/F2 still NOT RUN** (they need a saved ExecState 1).
31. ?뵶 retrospective still reviews the WRONG window (`retrospective.py:282-286`) ??reproduced a THIRD time today,
   and the cause is now named: `guard_cycle.stamp()` = `min(ctime, mtime)`, so RE-ARCHIVING an existing slug
   keeps the OLD ctime and the gate never sees the new review. No cycle-16 plan document yet.
32. ?뵶?뵶 outcome review 2026-09-17: **six `OUTCOME-VIOLATION`s, SECOND consecutive time** ??the work stops for a
   re-plan with the USER. Not answerable by a device. Zero new user-runnable deliverables.
34. ??**CLOSED BY MEASUREMENT** ??it was the TYPE/gate choice, not the op. The discriminator ran inside
   `build_opconnectnested_v1` (two copies of ONE subVI, NAMED `error out` ??NAMED `error in (no error)`): op
   error `''`, and **the wire SURVIVES `remove_bad_wires_scripted`**, which a broken wire does not. The old
   "same wire uid on both ends" gate was itself WRONG for this op ??a cross-boundary wire is SEVERAL SEGMENTS
   with different uids (`NAMES.md:861-863`; `test_opconnectnested_v1_cold.log`, 7/0).
33. ?윞 **HALF CLOSED ??the ADDRESSING gap is GONE; the SOURCE-RESOLUTION gap is now the only thing between D1
   and a saved VI.** ??`OpConnectNested_v1.vi` BUILT, SAVED (14,666 B), FUNCTIONAL **warm and cold**: two
   terminals by INDEX on two DIFFERENT nested diagrams, LabVIEW making the tunnels (`LoopTunnel 0 ??2`); an
   UNNAMED terminal on diagram P reached from a source on diagram Q (wire 0 ??414). ?좑툘 `toolkit-capabilities.md:56`
   and 짠11n.2 said this "cannot be built by this fleet" ??both WITHDRAWN in place. ?뵶 What is left = **짠11q.2**.
35. ??**FIXED + MEASURED** (`tools/bench/test_run_poison.log`, **11 pass / 0 fail**). `gscript` now carries a
   module POISON flag: `_deadline_call()` sets it on every expiry (`_run` AND `_invoke`), `_check_poison()` runs
   first in `lv` / `op` (cache hit included ??the unguarded path) / `_invoke` / `_run` / `_err`. With a REAL
   outstanding COM call the next `op()` raised **`COMPoisoned` in 0 ms** instead of blocking; it self-clears once
   the abandoned worker is measurably dead. `GSCRIPT_POISON_RECOVER=1` restarts LabVIEW instead (opt-in).

## NEXT
?뵶 **ONE JUDGEMENT QUESTION, and 짠11p's route-A verdict hangs on it.** 짠11p item 1 is **DONE** (see OPEN 33/34);
item 2, the tunnel-source reader, is **STOPPED BY ITS OWN PRIOR-ART REVIEW** ??`archive/peer/2026-09-17-priorart-
connectnested-v1.md`, disposed in full, consequences in **`docs/d1-build-plan.md` 짠11q.2**: (a) the machine's own
account (`build_d1_v0_run7.log:303-325`) says the 17 sources lie *"further out through more unnamed tunnels"* ??a
CHAIN, which the specified ONE-HOP reader cannot resolve, and `d1-route-b-plan.md:316-318` says outright *"there
is no named origin to find"*; (b) its back half is `OpWireSource_v5`, which **failed its own published control**
(0 rows, error 1055, cause unrecorded = OPEN 28c); (c) `Generic.Owner` returns a **Generic** ref, so that hop
needs its own cast, and `OpOwnerChain_v1` terminates silently at a `FlatSequenceFrame`. **Choose one:** (i) build
it anyway as specified, (ii) build the **1055 reader** first (CLAUDE.md's own "when a diagnosis is GUESSED twice,
build the reader"), (iii) accept that the 17 have no origin and let that decide route A vs **route B** per 짠11p.
?좑툘 A material session may not take this (CLAUDE.md 짠3) and did not. **Material, unblocked, NOT started:** a run 9
that wires only the ADDRESSING-gap rows (the 7 횞 5001 + the 8 unnamed-end) with the v1 op, to measure how far
route A now reaches ??35 + 15 of 66 expected, the 16 `from-tunnel` rows still unroutable, so it CANNOT produce a
saved VI and is a measurement, not a delivery; reparent the 6 `ControlTerminal`s per 짠5d; PHASE "full" stage 2
(8 queues, endpoints, sentinels, `#376`/`#6384` carriers, GPU kernel 13+6) is **still entirely unwritten**.
?좑툘 OPEN 32 stands: no diagnostic or framework cycle before F1/F2.

## Where to look
`CLAUDE.md` 쨌 **`docs/decisions.md`** 쨌 `docs/NAMES.md` 쨌 **`docs/toolkit-capabilities.md`** (new ops at the end
of the table) 쨌 **`docs/d1-build-plan.md`** = the build order 쨌 `tools/recipes/build_d1_v0.py`.


=== NO INDEX ===
Search the project directory yourself: `docs/`, `archive/` (peer exchanges and narratives both), `tools/bench/*.log`, `tools/recipes/`, `tools/gscript.py`, `archive/benchmarks/INDEX.md`. Nothing here is a complete listing, so do not treat any summary as the corpus - the answers that matter are often in old exchanges nobody annotated.


## Answer

Prior-art review complete — read-only: no lock taken, no build, no edit, no `.vi` opened, no hardware touched. (The plan file could not be written — `Write` is disabled this session — so the review is here in full.)

**5 findings, 0 `novel`.** The composition route is the right one to prefer, but it is already implemented twice in working code; the "chain" premise that shaped both this plan and the review before it is a hard-coded template string, not a measurement; and the 1055 that §11q.2 calls "cause unrecorded" has a cause readable from the files — the failing caller never sets the op's UID input.

---

# PART A — THE DIRECTION

## A1 — cleared, not settled elsewhere
`docs/d1-build-plan.md:689-700` (§11r, today) *is* the judgement decision, and `:719` (§11p) fixes the two-artifact budget. Nothing in `STATUS.md`, `docs/` or `archive/` decides against it. No slug.

## A2 — no surviving refutation
`docs/d1-route-b-plan.md:316-321` argues the opposite (*"there is no named origin to find … B never asks the question"*), but its force was the **named**-origin requirement, which `OpConnectNested_v1` removed (`docs/toolkit-capabilities.md:56`, FUNCTIONAL warm and cold). Not a refutation of §11r. No slug.

## A3 `contradicted` — "the machine's own account" is a literal in the recipe, and it fired on a row that HAD a resolved source

- `tools/recipes/build_d1_v0.py:1012-1018` prints *"the value comes from further out through more unnamed tunnels"* for **every** `from-tunnel` row whose `outer_source` is not a **NAMED node** — `if osrc.get("kind") != "node" or not osrc.get("name") …`.
- `tools/bench/build_d1_v0_run7.log:317` prints it for `#376 t7` while quoting a **resolved** source in the same line: `({'kind': 'node', 'diagram': '19', 'uid': 637, 'i': 37, 'name': '', 'is_source': True})`. That row's blocker was the empty `name` — addressing, which v1 removed.

**Scope:** the sentence's evidentiary status and the "16 rows are a CHAIN" premise built on it (`d1-build-plan.md:740-743`). It does **not** claim the other 16 rows do resolve — only that no run has measured that they do not.

## A4 `unread-evidence` — the read §11r specifies has already been run on the main VI, and returned an owner class the plan's OUT does not cover

`tools/bench/diag_autofocus_border.log:19-26` walked a wire's whole `Terms[]` with `OpWireSource_v5`, printing `source=`, owner class and owner uid per terminal — the plan's exact output, on the real VI, read-only:

```
:20  wire 3268 Terms[0] source=True owner 'Diagram' uid 639 …
:26  RESULT wire 3268 driven by ('Diagram', 639); sinks [… ('LoopTunnel', 2213) …]
```

Published at `docs/camera-acquisition-facts.md:225-230` — **two of the three** wires read that way are driven by `Diagram` 639 — with the consequence at `:235-237`: *"A source terminal owned by a `Diagram` is the control-terminal signature … the label comes from `panel_wiring`, not from the signature."*

The plan's OUT enumerates two owner cases (node → `Nodes[]/Terminals[]` index; tunnel → tunnel index). **Diagram-owned source terminals are a third**, they are the commonest one measured so far, and they carry no `Nodes[]/Terminals[]` index for `OpConnectNested_v1` to address. `#2213` — one of the 17 rows — is a sink on that very wire.

**Scope:** the OUT case enumeration and P3's oracle. It does not say the outer-terminal hop is wrong.

---

# PART B — THE ARTIFACT

## B1 — cleared on the name
`claudeDev` holds `OpTunnels_v0.vi`, `OpTunnelRead_v0.vi`, `OpTunnelInd_v0.vi`; no `OpTunnelSource*`.

## B2 `already-failed` — the 1055 has a cause in our files, and it is the CALLER, not `OpWireSource_v5`

The op is **UID-addressed**: `docs/toolkit-capabilities.md:48` — *"addressed by UID, so no traverse index is involved"*; the UID input is `"UID 2"` (`tools/bench/opwiresource_v5_labels.json:7`).

The wrapper that failed 38/38 never sets it:

- `tools/recipes/diag_d1_full_route.py:265-273` (docstring `:253` = *"build_opstopfromnode_v0.py:350-388 verbatim"*; same code at `tools/recipes/build_opstopfromnode_v0.py:368-376`) sets `"vi path"`, `"Class Name"="Wire"`, `"index"` = a **Traverse index** and `term_index` — and never `lab["uid_in"]`.
- The callers that WORK do: `tools/recipes/build_opwiresource_v5.py:161` — `vi.SetControlValue(labels["uid_in"], wire_uid)` — used by `tools/bench/diag_d1_step0.py:75-76` and `tools/bench/diag_autofocus_border.py:48`.
- And they got right answers **with the same 1055 present as the documented terminator**: `tools/bench/diag_d1_step0.log:21-22` — `wire 10850 Terms[2] … error 1055` then `wire 10850 -> {'owner_class': 'DigitalNumericConstant', 'owner_uid': 10739 …}`; ten wires resolved at `:21-58`. `docs/NAMES.md:944`: *"Walk `term index` 0,1,2… until error 1055 = past the end"*.

With `UID 2` at 0 the cast has no object, `Wire.Terms[]` is empty, and term index 0 is already past the end — which is exactly what the failure says: `"error column at t0"` for all 38 wires (`tools/bench/diag_d1_full_route.json:49-52`, `:54-202`).

Consequences for the plan as written:
1. **P1/P2 buy a measurement of a hypothesis the files already exclude** ("the op VI itself is broken on disk / the target was ExecState 0"). `diag_d1_step0.log:21-58` is the op working on the real VI.
2. **P2's control cannot be run as described.** `read_terminal` hard-codes the target: `build_opwiresource_v5.py:161` sets `"vi path"` to `MAIN` (`:35`, imported from `build_opconstvalue_v1`) — the ORIGINAL — so "wire 10850 on the working copy" reads the original instead; the other wrapper reproduces the defect above. `docs/NAMES.md:945` says the published 12/12 was *"Verified on the main VI"*, not on a copy.
3. Reusing either wrapper repeats the cause. The same defect is still live in `build_opstopfromnode_v0.py:350-388` — it is what `docs/toolkit-capabilities.md:51` records as the open *"T6 (`OpWireSource_v5` returned no terminals for w147)"*.

**Scope:** the back half's precondition and gates P1/P2. It does **not** claim the op is defect-free on a freshly copied target — only that the recorded failure is explained by the caller, and that no run has yet addressed the op by UID and failed.

## B3 `helper-exists` — the composition is already implemented twice, and the front half is inside built ops

- **The full composition, working and measured:** `tools/bench/diag_d1_step0.py:375-395` censuses every tunnel (gate `G3a` = 132 LoopTunnels) and `:432-455` resolves the remaining boundary wires with `OpWireSource_v5`, writing `resolved_boundary`/`tunnels`/`wiresource` to `d1_step0_census.json` — `tools/bench/diag_d1_full_route_run2.log:15` records **91/91**.
- **The one hop, with the plan's own rationale already in its comment:** `tools/bench/d1_rewire_map.py:205-214` — *"A LoopTunnel is a CARRIER, not a source: the value that reaches the moved node comes from whatever drives the tunnel's OUTER wire … LabVIEW makes the new loop's tunnel itself"* — takes `out_wire` and looks up the source terminal on it. It produced the 109/109 source map (STATUS OPEN 28b).
- **The LabVIEW-side chain, already shipped:** `tools/recipes/build_oploopcast_v0.py:21` carries `Tunnel[Outside Terminal 6356001] → Terminal[Connected Wire 634A000]`; `archive/bench-2026-09-13-array-reporter/build_optunnelind.py:16,:56,:109-110` builds 6356001 → Terminal (and records the short name `Outer Term`); `tools/gscript.py:889,:919` returns `out_wire`; `tools/gscript.py:816-824` (`node_terms`) already returns `{i, name, is_source, wire}`, the "index within its owner" the plan says it will derive.

**Scope:** the construction cost and the "compose two ops" framing — this is an **edit to `d1_rewire_map.py`**, not new construction. It does not claim the iteration exists (see B4).

## B4 `already-measured` — the data to follow the chain is already on disk, and one of the 17 rows is already resolved

- `d1_step0_census.json` holds **all 132** LoopTunnels with `out_wire` and `in_wires` (`diag_d1_step0.py:378-385`); `main_vi_nodeterms.json` holds every diagram's nodes and terminals with `i`/`name`/`is_source`/`wire` (`d1_rewire_map.py:119-125`).
- `d1_rewire_map.py:212-214` resolves the outer wire against **node terminals, constants and controls only** — it never consults `tun_by_wire`, built 50 lines earlier at `:152-158` from the same census. The tunnel→tunnel hop was never *tried*; its data was already in the same dict.
- `#376 t7` is already resolved offline (`build_d1_v0_run7.log:317`), so P3's three-row oracle has at most one row that needs the reader, and P4 is at most 16 rows.

**Scope:** the run's necessity and P3/P4's counts. It does not claim the offline join will resolve all 16 — it claims that has never been measured and costs no LabVIEW to measure.

---

```
PRIOR-ART: contradicted      (A3 — tools/recipes/build_d1_v0.py:1012-1018 + tools/bench/build_d1_v0_run7.log:317 vs docs/d1-build-plan.md:740-743 — covers the evidentiary status of "the value comes from further out through more unnamed tunnels": a literal printed whenever outer_source is not a NAMED node, fired on a row whose source WAS resolved; does NOT claim the other 16 rows resolve)
PRIOR-ART: unread-evidence   (A4 — tools/bench/diag_autofocus_border.log:19-26 + docs/camera-acquisition-facts.md:225-230,:235-237 vs the plan's OUT spec — the same read has been run on the main VI and returned source terminals whose Generic.Owner is a Diagram (639): a third owner case with no Nodes[]/Terminals[] index, identifiable only via panel_wiring; does NOT say the outer-terminal hop is wrong)
PRIOR-ART: already-failed    (B2 — tools/recipes/diag_d1_full_route.py:253,:265-273 + tools/recipes/build_opstopfromnode_v0.py:368-376 + tools/bench/opwiresource_v5_labels.json:7 + docs/toolkit-capabilities.md:48 + tools/recipes/build_opwiresource_v5.py:35,:161 + tools/bench/diag_d1_step0.log:21-58 + docs/NAMES.md:944-945 — covers the 1055 precondition and gates P1/P2: the failing wrapper never sets the op's UID input while the op is UID-addressed, the working callers do and answer correctly with the same 1055 as terminator, and read_terminal hard-codes the ORIGINAL so "the control on the working copy" cannot be run as written; does NOT claim the op is defect-free on a copied target)
PRIOR-ART: helper-exists     (B3 — tools/bench/diag_d1_step0.py:375-395,:432-455 + tools/bench/diag_d1_full_route_run2.log:15 + tools/bench/d1_rewire_map.py:205-214 + tools/recipes/build_oploopcast_v0.py:21 + archive/bench-2026-09-13-array-reporter/build_optunnelind.py:16,:109-110 + tools/gscript.py:816-824,:889,:919 — covers construction cost: tunnel census + OpWireSource_v5 + offline join is implemented and measured 91/91, the one-hop outer-wire lookup already exists with the plan's own rationale in its comment, and 6356001 → Connected Wire is inside two built ops; does NOT claim the iteration exists)
PRIOR-ART: already-measured  (B4 — tools/bench/d1_step0_census.json via tools/bench/diag_d1_step0.py:378-385 + tools/bench/d1_rewire_map.py:119-125,:152-158,:212-214 + tools/bench/build_d1_v0_run7.log:317 — covers the LabVIEW run's necessity and P3/P4's counts: all 132 tunnels with out_wire/in_wires and every diagram's terminals are already on disk, the outer-wire lookup never consults the tunnel map it had already built, and #376 t7 is already resolved; does NOT claim the offline join will resolve all 16)
```

**The two that change what happens next.** **B2** — the 1055 is a caller defect (`UID 2` never set); repair the wrapper before spending P1/P2 on "is the op broken on disk", and do not reuse `read_terminal` unpatched, since it reads the ORIGINAL. **B3 + B4** — the chain can be followed offline today from `d1_step0_census.json` + `main_vi_nodeterms.json` by having `d1_rewire_map.py:212-214` consult the `tun_by_wire` map it already builds; that is the cheapest discriminator for whether the 16 rows have a reachable source at all, and it costs no LabVIEW run.

**Checked and cleared:** no `OpTunnelSource*.vi` exists; `OpTunnels_v0` does carry `Outside Terminal` (`gscript.py:892`) and does return `out_wire` (`:919`), as the plan says; `OpWireSource_v5` does contain the `Owner → To More Specific Class → UID` cast (`toolkit-capabilities.md:48`), so the plan's answers to objections 3 and 4 stand on our own files; and §11p (`d1-build-plan.md:702-719`) authorises this artifact by name.

## Sources

(extract from answer)

## What was done with it

**ALL FIVE FINDINGS ACCEPTED WHOLE; NONE REFUTED. The review deleted the artifact it was reviewing** — no
`OpTunnelSource_v0.vi` was built, because B3/B4 showed the reader is a composition of ops already on disk plus an
OFFLINE join, and B2 showed the failure that motivated a fresh build was a caller defect. Zero of §11r's two-build
budget was spent. Dispositions, one per slug:

FIXED: already-measured - tools/bench/d1_tunnel_chain.py:1 - B4's offline route was written and run FIRST, and it
measured that the offline join alone resolves only 2 of the 18 rows.

- **B4's offline route was written and run FIRST** (`MATERIAL=1 py -u tools/bench/d1_tunnel_chain.py`): the chain is followed from
  `d1_step0_census.json` + `main_vi_nodeterms.json` with the `tun_by_wire` map `d1_rewire_map.py:152-158` already
  builds, costing no LabVIEW call. Result: **2 of 18** rows resolve offline (`#1359` t9 → `SubVI #27605`;
  `#376` t7 → a terminal of `#637`), **16 dead at the first hop** — the outer wire's source is a non-Node GObject
  that no census on disk covers by wire. So B4 is right that the data was there, and it also measured that the
  offline join alone does NOT resolve the 16 (the review said it did not claim it would).
FIXED: helper-exists - tools/bench/diag_tunnelsource_onehop.py:96 - the reader is a composition of ops already on
disk, so no VI was built: `gscript.tunnels()` + `OpWireSource_v5` + a Python join.

- **The reader is `gscript.tunnels()` + `OpWireSource_v5` + a Python join**, exactly B3's construction-cost point. Its owner
  lookup and its tunnel hop read `main_vi_nodeterms.json` / `d1_step0_census.json` instead of walking LabVIEW
  (`:152-175`). No VI was created, no property node was built, `Outer Term` / `Terms[]` / `IsSource` were never
  re-derived.
FIXED: already-failed - tools/bench/diag_tunnelsource_onehop.py:110 - the caller now sets the op's `UID 2` input
and takes the target as a parameter, so neither half of B2's cause is repeated.

- **`UID 2` (`lab["uid_in"]`) is set on every call and the target is a parameter**, so neither half of B2's cause is repeated: the op is
  UID-addressed and the ORIGINAL is no longer hard-coded. MEASURED consequence, `diag_tunnelsource_onehop.log`:
  the published control reproduced on the first try — *"G2 wire 10850: 2 terminals read, 1 report Is Source? TRUE;
  first error ''"*, owner `DigitalNumericConstant` **10739**, the constant scan's answer. **`OpWireSource_v5` is
  not broken; `diag_d1_full_route.py:265-273` is.** Gates P1/P2 were kept only because they now cost one call
  each, and P1 reported ExecState 1 for all three op VIs.
FIXED: unread-evidence - tools/recipes/build_d1_v0.py:1075 - the Diagram-owned / non-Node owner case gets its own
branch, reporting the measured owner class per row instead of assuming a Nodes[]/Terminals[] index exists.

- **The non-Node owner now has its own branch**, reporting the MEASURED owner class per row instead of assuming a `Nodes[]/Terminals[]` index
  exists. A4 predicted the third owner case and the measurement found a fourth and fifth:
  **14 rows `FlatSequenceInnerTunnel`, 2 rows `LeftShiftRegister`, 1 `SubVI`** (`d1_tunnel_sources.json`).
FIXED: contradicted - tools/recipes/build_d1_v0.py:1076 - run 7's printf "the value comes from further out through
more unnamed tunnels" is deleted; each row now prints the owner class and uid the machine returned.

- **The literal A3 named is gone.** Run 7's line
  *"the value comes from further out through more unnamed tunnels"* is gone; each row now prints the owner class
  and uid the machine returned. A3 was right that the sentence was a printf, not a finding: `#376` t7's source
  had in fact been resolved in the very line that printed it.

**What the review's own prescription produced, and it is the finding of the session:** following B4 and B3 cost
one 111-second read-only run instead of a build, and it turned §11r's premise over. The 16 rows are not an
addressing gap inside the loop hierarchy at all — their values enter the frame-loop's diagram from the enclosing
**flat sequence**, and a `FlatSequenceInnerTunnel` is not a node on any diagram, so
`OpConnectNested_v1`'s `Diagram[d].Nodes[n].Terminals[t]` cannot name them. See
`archive/peer/2026-09-17-flatseq-tunnel-source-addressing-r3.md`, which refutes the wider claim that they are
unreachable *by the API* — `Terminal.Connect Wire` accepts any Terminal reference, including one from
`Wire.Terminals[]` + `Is Source?`, which `OpWireSource_v5` already holds. That is a WRITER this fleet does not
have, and building it is beyond §11p's authorisation — carried to STATUS as the one judgement question.
