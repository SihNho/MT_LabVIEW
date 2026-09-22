# M3a-3b ROW D on `tools/stagekit.py` — delete 7506, then connect #23868 → FSIT #7468's LeftTerm #7488

RECIPE: `tools/recipes/stage_d1_m3a3_rowD.py` — **80 lines**, the first stage written on the accepted
stage-script library `tools/stagekit.py` (725 lines, self-test 32/0, `tools/bench/selftest_stagekit.log`;
a 595-line probe re-cut on the kit matched the recorded run 13/13, `tools/bench/diag_c83_connect2x2_kit.log`).
It is astcheck-clean and has NEVER RUN. This is STATUS NEXT's FIRST ACT.

## What this dispatch does

INPUT is the ROW-C BED `claudeDev\D1_s3b_m3a3_20260922_081056.vi`, md5
`33ef524e0b6b193a158c9221474c68e3`, 306,951 B — imported as `build_opfsinnertunnelconnect_v0.BED`, so
no address is retyped. (The fork "bed vs `D1_s3b_m3a2_20260922_023029.vi`" is RATIFIED BY JUDGEMENT:
STATUS NEXT names the bed and every uid below was measured ON IT in cycles c81–c84; starting from M3a-2
would discard Row C.) The bed is md5-pinned at entry and exit and is **never opened for EXECUTION**.

THE ROW: `FlatSequenceInnerTunnel #7468`'s `Left Terminal` `#7488` is fed by the OLD
`RightShiftRegister #4334` through wire **7506**; it must be fed by the NEW `RightShiftRegister #23868`
(the new loop's `Outgoing Handle`, Diagram `#686` / `Nodes[21]` / `Terminals[1]`, owner by Pre-decided 120).

Sequence, on a dated working COPY: (1) read `WhileLoop #637`'s wired terminals and a Wire/Node/LoopTunnel
census; (2) `delete_wire(7506)` — **NO Remove Bad Wires anywhere in the file**; (3) re-read the FSIT and
require it to STILL RESOLVE with `#7488` BARE (gate D1); (4) `OpFsInnerTunnelConnect_v1.vi`
(md5 `5b4e5f0fb3baae96361c33ce81bcd7b1`) from the new loop's terminal into `#7488`, with the address
triple RE-RESOLVED inside the call, never carried (34(h)); (5) junk purge; (6) the gates; (7) ONE save.

## ⚠️ AMENDED AFTER THE PRIOR-ART REVIEW (2026-09-22 15:32) — D1–D4 ARE ALREADY MEASURED

`archive/peer/2026-09-22-priorart-c87-rowd-stagekit.md` A1/A4 cite a run this plan had missed:
`tools/bench/diag_c86_norbw.py` ran **this exact sequence** at 14:46 — on a byte-identical scratch of this
same bed (`diag_c86_norbw.log:7-8`, `:36`), with `remove_bad_wires_scripted` and its GUI form rebound to a
raising guard and the rebind proved before the work (`:27-28`), with the same op `OpFsInnerTunnelConnect_v1.vi`
md5 `5b4e5f0f…` (`:22`) — and every gate this plan calls its open question came back **PASS**:

| gate | c86's answer | citation |
|---|---|---|
| **D1** `#7468` still resolves, `#7488` BARE after `del_wire(7506)` with no RBW | PASS — `uid_back=7468`, `error out=''`, `term_a_uid=7488`, `wire_a=0`, inner wire 7448 survives | `diag_c86_norbw.log:74-77` |
| **D0** the connect writes a wire onto `#7488` | PASS — new wire **25324** on `#7488` *and* on `#23906`, same uid, `wire_delta 1`, invoke `error out=''` | `:87`, `:96-97` |
| **D2** ONE source terminal, owner `RightShiftRegister #23868` | PASS — `[('RightShiftRegister', 23868)]` | `:105`, `:107` |
| **D3** OLD `#4334` off the net | PASS — every owner `[('FlatSequenceInnerTunnel', 7468), ('RightShiftRegister', 23868)]` | `:108` |
| **D4** PD85 violations 0 | PASS — `0: []` | `:109` |
| `Wire.Is Broken?` on the new wire | False, and the op's `UID 2` IS that wire | `:106`, `:110` |

**So D1–D4 are RE-ASSERTED PRECONDITIONS on the landing run, not the open question.** c86 **saved nothing**
and deleted its scratch (`:113`), and its log carries `BGRUN START` with **no `BGRUN END`** — truncated
mid-cell-B — so the ordered second pass, D5, D6 and D7 were never reached. **WHAT IS ACTUALLY NEW HERE:
the SAVE of a Row-D artefact, D5, D5b, D6 and D7.**

**B4, accepted and answered by measurement:** `expect_is_broken_false` re-issues the connect against the
work file, and `OpFsInnerTunnelConnect_v1` is on record MERGING (`build_d1_m3a3b_d3.log:58-60`, `:318`,
`:321`), so `wire_delta 0` alone is NOT evidence the second pass was inert. A gate **D5b** is added: a FRESH
`net_sources` walk AFTER the second pass, required to still show exactly one source owner `#23868` and PD85 0.
Nothing is asserted about a re-merge being inert — it is now READ.

## The measurement this exists for — plan entry 111a (ANSWERED by c86; see the amendment above)

c83 read `error 1055` from the connect after a delete and c84's failed-prediction review
(`archive/peer/2026-09-22-c84-replace-vs-branch.md` §3) named the live alternative: every c83 deleting
cell called `remove_bad_wires_scripted` ONE LINE after `del_wire`
(`tools/bench/diag_c83_connect2x2_r2.py:449-450`), and that verb is on record DELETING A TUNNEL
(`archive/2026-09-17-status-d1-route-b-2.md:44-46`), which is why it is refused as a rule-1a hazard at
`docs/cycle27-plan.md:1860-1862`. **"Gone" ≠ "unresolvable".** So gate D1 is the whole point: after a
delete with no Remove Bad Wires anywhere, does `#7468` still resolve and is `#7488` BARE? The raw
`term_a_uid` / `wire_a` / `err` columns are reported whichever way it goes.

## GATES — each prints the value it compared

* **D1** (fatal) FSIT `#7468` still resolves AND `#7488` is BARE after the delete — the 111a measurement.
* **D0** (fatal) the connect wrote a wire onto `#7488`; prints the wire uid, the op `err` and `invoke_err`.
* **D2** exactly ONE source terminal on that net, owner `RightShiftRegister #23868` (owner identity
  decides, never a count — Pre-decided 117 as corrected by 120).
* **D3** the OLD source `#4334` is OFF that net.  **D4** PD85 violations 0 on the walk.
* **D5** `Wire.Is Broken?` False on the ORDERED idempotent second pass (42(b)), `wire_delta` 0.
* **D7** `WhileLoop #637`'s terminal counts (total, wired) unchanged — nothing downstream dropped.
* **D6** diagram-wide broken-wire count ≤ the bed's own baseline **11**, measured on a SCRATCH copy of
  the artefact because the only reader on disk mutates (Remove Bad Wires delta,
  `tools/bench/broken_probe2.py:12`); the artefact itself is never perturbed.

## What already exists and is imported rather than rebuilt

`tools/stagekit.py` (every verb, the pin check, the census, the junk purge, the save route, the close
report) and `build_opfsinnertunnelconnect_v0` (`BED`, `BED_MD5`, `PINS`, `resolve_triple`, `FSIT_UID`,
`LEFT_TERM_EXPECT`, `ROWD_WIRE`, `OLD_SOURCE`, `RSR_EXPECT`, `LOOP_NODES_IDX`, `LOOP_TERM_IDX`), plus the
already-built `claudeDev\OpFsInnerTunnelConnect_v1.vi`.
**Nothing new is built: no op, no verb, no device, no third configuration.**

## What is settled and is NOT re-tested

* `Terminal.Connect Wire` 6349C03 **MERGES** onto an already-wired sink — c84, 4/4 cells. Hence
  delete-BEFORE-connect here, not connect-then-delete.
* Two BARE terminals **CREATE** a wire — c83's trivial-VI cells 4/4, and
  `tools/bench/build_harness_copyloop2.log:31-40` (census 9 → 10).
* `UID to GObject Reference.vi` resolves a TERMINAL uid, and the uid ECHO is the only column that catches
  a ghost — c81, `tools/bench/diag_c81_uidref.log:85`.
* `OpFsInnerTunnelConnect_v1` is legal and its two uid echoes hold on 20/20 calls — c84.

## Not done, deliberately

No Remove Bad Wires; no tunnel re-creation; no `Wire.Disconnect Terminal` 6370C0D (Pre-decided 123); no
new op; the artefact is BROKEN BY DESIGN (uninitialised SRs belong to other stages), is NEVER RUN and
never cold-loaded (34(f)). Rig is 조립: no motor, no ASI, no camera. Originals untouched (rule 1).

## Pre-decided

* The artefact is broken BY DESIGN — `ExecState` is RECORDED, never a criterion (Pre-decided 89/97).
* The save route is scripted at `ExecState` 1, otherwise the user-approved broken-intermediate `gui_save`
  (CLAUDE.md §3.6, user 2026-09-22 "저장 허용함."); the run says WHICH route it used.
* Owner identity decides every source question, never a wire count or delta.
* A negative D1 is a FIRST-CLASS RESULT: save nothing, report the raw columns, stop.
