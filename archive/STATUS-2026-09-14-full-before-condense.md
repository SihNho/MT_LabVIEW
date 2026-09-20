---
type: narrative
status: historical
date: 2026-09-14
tags: [archive]
---

# STATUS — read this first (one screen; detail lives one layer down, never appended here)

## LabVIEW execution lock

```yaml
labview-lock:
  status: acquired
  owner: Claude (session 7b982769) - AUTONOMOUS ALL-DAY LOOP, user unreachable 2026-09-14
  since: 2026-09-14 (loop started ~09:xx)
  loop: >
    User: "하네스 구성해서 피어 리뷰를 통해서 오늘 쭉 루프를 돌려줘". Each cycle = peer-review the plan ->
    build with a control -> verify -> document -> STATUS. Targets, all cast-free ladders: (1) per-diagram
    Node.Label reader (no loop, one node per call) -> subVI identity; (2) Panel.Controls[] -> Control.Terminal
    -> Terminal.Connected Wire -> panel wiring column; (3) Nodes[]->Terminals[] on Global nodes -> read/write
    direction. Hard limits unchanged: zero GUI, zero edits to originals/vendor VIs, zero hardware. A blocked
    item is recorded as OPEN and the loop moves on; it never guesses to keep moving.
  scope: >
    System inventory only (docs/system-inventory-plan.md). READ-ONLY against the main VI and every vendor VI.
    WILL NOT: modify any original or instr.lib VI, implement the rotor sign fix (a behaviour change - diagnose
    and propose only), operate the motor or piezo (nothing planned needs hardware), or settle the rotor zero's
    meaning by inference. Scratch VIs under claudeDev are created and deleted as usual.
  previous: >
    released 2026-09-13 23:35 after task 1 (OpReportAll_v0, 646.50 s -> 1.70 s, rows IDENTICAL)
  purpose: >
    Task 1 (TOOLING) finished - OpReportAll_v0 built and functionally accepted (646.50 s -> 1.70 s on the main
    VI's 626 nodes, rows IDENTICAL). Every scratch VI was created and deleted in the same run; the main VI was
    read ONLY through headless COM traversal and was never opened, edited or saved.
```

## HARDWARE PERMISSION — FULL, RE-GRANTED 2026-09-13 for an unattended day

The user, twice and in detail, before a day away — the second time explicitly to unblock the frame-delay
measurement (*"프레임 지연 측정 해도 되도록 모터 다 분해해 뒀으니까 모터 사용하는 부분도 얼마든지 가동 가능.
현재 모터 가동범위에서는 하드웨어적으로 충돌 없음."*):

| instrument | physical state, in the user's words | permitted |
|---|---|---|
| **Piezo stage** | 분해해서 책상 위에 — detached, sitting on the desk | yes |
| **Rotor** | 아무리 돌아도 충돌 생길 리가 없음 | yes, any rotation |
| **Magnet motor** | 아무리 밑으로 내려가도 충돌 없음, 기계 가동범위 내 | yes, full travel |
| **Camera** | 셋팅 원복 시켜줄 수만 있으면 됨 | yes, **on condition of restore** |

So **the frame-delay measurement in the working copy is IN SCOPE**, unattended. It was the one item deferred as
"motor/piezo, user present"; that condition is lifted for this state.

**The camera condition is a real obligation, not a formality.** Measured 2026-09-12: `IMAQdxOpenCamera` RESETS the
ROI, so every run starts full-frame and a run that sets a smaller frame leaves it halved — the camera accepts the
write with rc=0 and no error, and a dirty exit does not preserve anything either. So any script touching the camera
must restore **Width, Height, OffsetX, OffsetY and the frame rate** (`AcquisitionFrameRateRaw`) in a `finally`, and
must never write `BinningHorizontal` — binning is what the calibration depends on. Baseline to restore to:
1280×1024, offsets 0, 90.0009 Hz. `tools/bench/imaqdx_limits.py --restore` puts the frame back.

**CLAUDE.md rule 1b is NOT revoked** — it exists because the piezo can destroy the rig, and that danger returns the
instant the rig is reassembled. This permission is tied to the disassembled state described above: **ask again in
any session that does not carry this line**, and stop at once if anything suggests the rig has been put back
together.

## HARDWARE PERMISSION — the earlier grant this replaces (2026-09-12)

The user has detached the motors from the rig, reconnected the camera, and stated: *"ASI stage, PI stage, rotor, camera
모두 작동해도 괜찮아"*. So for now **all four instruments may be operated, motion included**.

This does NOT revoke CLAUDE.md rule 1b. That rule exists because the ASI piezo can collide and break the rig, and that
danger returns the moment the rig is reassembled. Treat this permission as valid only while the hardware stays detached:
**ask again before operating anything in a new session, or as soon as the rig is put back together.**

Camera identified 2026-09-12 by calling `niimaqdx.dll` from Python (tools/bench/imaqdx_ctypes.py + imaqdx_limits.py —
no LabVIEW, so no modal dialog): IMAQdx name **`cam1`** (NOT `cam0` — that wrong guess is what blocked two earlier
harness runs), JAI **SP-5000M-USB**, 2560x2048 sensor, binning 2x2, frame 1280x1024, offsets 0, 8-bit mono, 90.0009 Hz,
exposure 1909 us with **ExposureAuto Continuous**. **CEILING = 247.95 Hz** (`AcquisitionFrameRateRaw` minimum 4033 us),
so the wanted 150 Hz is reachable with 65% headroom and the per-frame budget at 150 Hz is 6.67 ms. Details +
the "first run halves the image" finding: [docs/camera-acquisition-facts.md](docs/camera-acquisition-facts.md).
Report: `archive/bench-2026-09-12-camera-identity/REPORT.md` (INDEX row 19).
**PER-FRAME BUDGET, measured (C-API sweep, no LabVIEW): budget ~= frame period - 1 ms.
90 Hz -> 10 ms | 150 Hz -> 6 ms | 200 Hz -> 3 ms | 247 Hz -> 3 ms.** Failure is a CLIFF: processed drops to EXACTLY half
(150->75, 200->100, 90->45) while acquired never falls. Acquisition itself is only 0.12 ms (2%). **At 150 Hz the 6 ms
must cover the CPU kernel 2.43-2.87 ms, and ONE serial round trip is 2.56 ms = 43% of the budget by itself.** A VISA
subVI (uid 48) sits directly on the frame loop's body so it is CALLED every iteration; whether it TRANSACTS every call
is NOT yet established (it may gate internally) - do not state that cost as settled. The dedicated motor loop
(diagram 20, `Motor control v5`) is already correctly separate.
**METHOD, reusable for any "where is node X in the main VI" question:** do NOT walk diagrams (net_map costs ~8 s/node;
170 diagrams never finishes). Instead `tools/bench/find_property_nodes.py` runs ONE Traverse per class and cross-
references Step 0's `diagram_tree_main.json` (diagram -> node UIDs) to place every node - 106 Property nodes mapped in
107 s - then net_map only the diagrams that actually hold one, cheapest-first by node count (170 -> 38 diagrams).
`camera_config_scan.py` now accepts an explicit comma-separated diagram list for exactly this.
**NEW CAPABILITY, planned not built:** reading a diagram CONSTANT's value. Peer-sourced API (archive/peer/
2026-09-12-read-constant-value-scripting.md): `Constant.Value` = **634AC00**, returns an LV Variant, needs a
`To More Specific Class` downcast to `Constant`; registered in docs/vi-server-ids.json but NOT yet confirmed on this
machine. Recipe + prediction contract drafted at `tools/recipes/build_opconstvalue.py` (donor OpReport_v3; the variant
goes straight to a Variant indicator so ActiveX marshals it and no new primitive is needed for the OUTPUT side).
It unblocks three stuck questions at once: the fixed `Wait (ms)` inside `ASI_adjust focus-subvi.vi` (called every
frame-loop iteration), the main VI's `Number of Buffers` ring depth, and the camera geometry constants.
**BLOCKER on that recipe, be honest about it:** the `To More Specific Class` downcast needs a donor node, and there is
none confirmed. A byte scan found the STRING in four claudeDev VIs, but reading their diagrams found no such node -
the promising `['error out','error in (no error)','reference']` signature is `Close Reference`. A string in a .vi is a
hint, never proof of a structure (same error a peer caught in the camera work the same day). Settle one of: (a) find a
VI containing it by TERMINAL SIGNATURE; (b) test whether New VI Object's style ring carries it (never tried); (c) test
whether the downcast is needed at all by wiring a GObject ref into a `Constant` property node and looking at the wire.

### RESTRUCTURE 4.6 — where it stands at the end of 2026-09-13

Plan: [docs/restructure-plan-4.6.md](docs/restructure-plan-4.6.md) · rotor: [docs/rotor-scheduler-design.md](docs/rotor-scheduler-design.md)
· fleet limits: [docs/toolkit-capabilities.md](docs/toolkit-capabilities.md) · subVI cost: [docs/subvi-call-cost-plan.md](docs/subvi-call-cost-plan.md)
· **GPU portability when the PC changes: [docs/gpu-portability.md](docs/gpu-portability.md)**

### 2026-09-14 10:1x–10:3x — STALL RULE (user) + the purge was O(J²): fixed, peer-attacked, self-tested

User, mid-loop: *"이런 에러들도 반복되는 것 같으니 피어리뷰 반드시 필요하겠어. 규율에 적용하도록"* — a recurring "STALLED
LabVIEW client" alert is now a failed prediction with a MECHANICAL gate: `tools/lv_stallcheck.ps1` writes
`tools/bench/stall_pid<N>_<start>.log` (`STALL:` line, once per event) and `tools/hooks/guard_peer.py` blocks the next
build until `archive/peer/` holds a newer file that NAMES the failure (log or recipe name). CLAUDE.md updated.
Codex attack (`archive/peer/2026-09-14-stall-alert-wrappers-false-positive.md`) found and I fixed: (1) the alert that
triggered this was a false positive — idle WRAPPER pids (bgrun + py.exe launchers), now excluded (leaf-only); (2) lifetime
CPU can never flag a client that once worked → added a CPU-**delta** rule (`.stall_samples.txt`, +<0.5 s over ≥60 s);
(3) any newer archive file used to lift the gate, and exempt words (`dir`,`type`) in a build's args exempted it — both
closed. Self-tested on an idle sleeper: lifetime rule, once-per-event record, delta rule all fired; gate table-tested
(bound review → 0, unreviewed STALL → 2, `--out dir` → 2). Known limits kept: MAX_AGE 6 h, PEER_GUARD_OFF, BENCH_CELL.
**The probe that was running timed out at 12 min** (`probe_attach_reader2c.log`) — cause, confirmed in code: `delete_object`
took a per-object `report()` snapshot before AND after every delete, so purging J junk Invokes cost O(J²) op runs.
Fixed: `uids()` → `report_all`, `delete_object(verify=False)` for bulk, one snapshot per batch, and `net_map` now prints
walk/purge phase times. Next: `tools/recipes/probe_castfree_ladders5.py` (both ladders + control, phase-timed).

**10:3x–10:5x — both cast-free ladders COMPILE (probe_castfree5.log, 77 s):** `SubVIs[]`→IA→`SubVI[VI Name, VI Path]`
and `Control.Terminal`→`Terminal[Is Source?, Connected Wire]`, ExecState 1, names in docs/NAMES.md. Walk 1.5–2 s +
purge 5–8 s per net_map now. **OpSubVIs_v0 built** (build_opsubvis_v0.log, 89 s; three rows VIName/VIPath/UID on ONE
SubVI-class node; error out of the SubVIs[] node exposed as `error out 2`; donor md5 unchanged) — **functionally
WRONG on the main VI** (test_opsubvis.log): scratch exact (2 calls), but diagram 43 → 0 rows, no error, even index
9999 no error. Cause (code, not guess): donor `OpNodeInfo_v0`'s `index` is a NODE index on the TOP-LEVEL diagram — it
never selects a diagram, so the op only ever read diagram 0. Peer dispatched on that reading + plan v1 = same recipe
on donor **`OpNetInfo_v1`** (Traverse 'Diagram' by index → TMSC → Diagram, the op behind net_map), driven by the new
`gscript.subvis(target, diagram)` wrapper, which also purges the donor's one junk Invoke per run (spec §33). Handle
audit on v0: scratch +0.03/run; main VI **+0.95 handles/run with ZERO element refs returned** → not SubVIs[]; asked the
peer whether Open VI Reference on the 473 KB VI explains it (discriminator: 50 runs of OpReportAll_v0). Scripts ready:
`tools/bench/test_opsubvis.py` (T1–T6, purge check), `tools/bench/sweep_subvis_main.py` (170 diagrams → 
`main_vi_subvis.json`, cross-checked per diagram against the cache). `guard_peer` now also fires on `FAIL` rows.

**10:5x — `OpSubVIs_v1` BUILT + FUNCTIONALLY VERIFIED (14/14, `test_opsubvis_v1.log`).** Donor `OpNetInfo_v1`; peer
(codex, `archive/peer/2026-09-14-opsubvis-v1-donor-netinfo.md`) confirmed the wrong-donor diagnosis and asked for an
identity test on the junk-dropping creator — it was found by terminal signature (uid 243), **deleted cleanly from the
copy**, ExecState 1: spec §33's "creator cannot be deleted" was a wrong-reference result. **T0 = 0 junk Invokes per
call.** Diagram 43 == cache (6 calls; uid 5058 = `Track N beads four-fold over-kernel-v3.vi`), diagram 1 = `Simple
Error Handler.vi`, empty diagram → empty arrays, index 9999 → error 1055 on the node's own error out (release
criterion). API: `gscript.subvis(target, diagram)` → `[{uid, name, path}]`, 0.17 s small / ~1.2 s main VI.
OPEN: handle count +~0.9 per Open VI Reference on the main VI (same with zero element refs; peer's 4-block matrix is
the next discriminator). Trap hit and fixed: a rerun copied over a scratch still loaded → Traverse 1012 "Cannot load
block diagram"; scratch names are now unique per run.
**11:0x — SWEEP DONE: [docs/main-vi-subvi-identity.md](docs/main-vi-subvi-identity.md)** — all 170 diagrams, **98 call
sites, 56 distinct callees, 0 mismatches** against the Step-0 tree (168 s). The "node identity" documentation gap is
closed (`tools/bench/main_vi_subvis.json`; by-callee, by-diagram, paths). Stall hook: a second false positive on the
healthy sweep client (0.4 s CPU / 163 s — COM clients idle in LabVIEW's Run) → reviewed (`archive/peer/…stall-record-
sweep-false-positive.md`) and fixed: progress = the bgrun log's mtime (< 90 s → not stalled) gates BOTH CPU rules.
Next: `OpPanelWiring_v0` (panel wiring column) — plan peer-reviewed (`…oppanelwiring-v0-plan.md`), adopted: `Terminal`
row on its own node so an odd object cannot poison Indicator/UID; explicit error columns; constructed-orphan test.
**11:1x — `OpPanelWiring_v0` BUILT (run 2, 131 s, saved; run 1 stopped on my own step order — PN1b created with its
`reference` unwired before the ExecState check; peer-confirmed, `…panelwiring-step6-execstate0.md`).** 7 arrays: Text,
Indicator, ControlUID, IsSource, WireUID, TermErr, WireErr (`tools/bench/oppanelwiring_labels.json`). Functional test
running (`test_oppanelwiring.py`: scratch exact, constructed orphan, main VI 114 rows + orphan list, handles). Gate
fix: guard_peer now judges only the LAST bgrun run in a log (a successful rerun no longer re-arms on the reviewed
failure).
**11:2x — `OpPanelWiring_v0` FUNCTIONALLY VERIFIED (11/11, `test_oppanelwiring.log`) and the WIRING COLUMN is in
[docs/main-vi-panel-map.md](docs/main-vi-panel-map.md):** 114 rows (60/54 exact), every non-zero wire UID a real Wire,
`Is Source?` == CTL/IND on all rows, a constructed orphan detected as exactly +1, explicit error columns
(`term_err=0, wire_err=1055` on every bare row = terminal valid, no wire). **10 bare terminals** on the main VI —
recorded as "not used via its terminal", NOT "unused" (locals / `Value` property nodes are the next census). One
test-oracle error on the way (the donor op itself has six bare controls) — peer-confirmed, test rewritten as
baseline+delta. API: `gscript.panel_wiring(target)`. Handle growth on the main VI again ≈ +1.0/run (Open VI
Reference on the 473 KB VI; OPEN). Next: `OpNodeTerms_v0` (Node.Terminals[] → Name / Is Source? / wire UID per
terminal) for the globals' read/write direction — plan under peer review.
**12:0x — quota pause, resumed. `OpNodeTerms_v0` BUILT (run 2, 142 s, saved; run 1 stopped on a guessed short
name `IsBroken` vs the machine's `Broken?` — peer-checked, NAMES.md updated).** Peer-driven design: one property per
node (PN_N[Name] → PN_S[Is Source?] → PN_C[Connected Wire] → PN_W[UID]) with every node's `error out` tunnelled, so
a failing property never defaults the others. 7 arrays (`opnodeterms_labels.json`). API `gscript.node_terms(target,
diagram, node)`. Functional test running (`test_opnodeterms.py`: exact per-index tuples vs the walker on every
scratch node, Is Source? on Index Array / Open VI Reference / an unwired input, the three globals on main-VI diagram
19 — direction predicted Trans READ / Rot READ / Focus WRITE from docs/main-vi-state.md, a miss = doc finding).
**12:1x — `OpNodeTerms_v0` FUNCTIONALLY VERIFIED (all PASS, `test_opnodeterms.log`).** Exact per-index tuples vs the
walker on every scratch node; Is Source? semantics on primitives (Index Array inputs FALSE / `element` TRUE; Open VI
Reference `vi path` FALSE / `vi reference` TRUE; unwired inputs FALSE, wire 0, only conn/wire err 1055). **Diagram 19:
all three globals are WRITES** (Trans/Rot predicted READ — wrong; 19 is the init frame writing the globals). Cost
0.8 s/node on the main VI vs the walker's ~8 s/node (21 nodes: 167 s). ANOMALY, unexplained: the walker (`net_map`,
OpNetInfo_v1) has dropped **0 junk Invokes** on every walk since 12:1x (78–130 per walk before) — the disk file is
md5-unchanged; discriminator = restart LabVIEW and walk once (pending; peer favours in-memory aliasing of the loaded
OpNetInfo instance, `…walker-zero-junk-anomaly.md`).
**12:2x — GLOBALS DIRECTION MEASURED (`globals_direction_main.log`, 7/7 sites, tuples == walker): every access site
in the main VI is a WRITE** — Trans 5/19/83, Rot 8/19/83, Focus 19. So the main VI never READS its own globals via a
global node; the readers must sit inside subVIs (the motor loop `Motor control v5_No Recording.vi`) — inference,
to be measured. Positive control (a READ global must read TRUE: `global_read_control.py`) pending; without it the
"all WRITE" line stays an observation. Stall hook false positive #3 (silent 167-s walk; record `stall_pid6164_…`,
review dispatched): `net_map` now prints a progress line per node and per 20 purged junk.
**12:2x — ZERO-JUNK ANOMALY SOLVED (measured, `walk_junk_probe.log`): junk Invokes land only on an OPEN target.**
Same scratch/process/op: reference-only walk → 0 junk, after `open_panel` → 78. The 08-28 rule ("a reference-only
target declines edits silently") covers the creator's drop. Withdrawn: "the overnight sweep poured junk into the
main VI" (it was never opened). `drop_subvi` cannot place a global VI (error 1057) → the READ-global positive
control now runs on the motor subVI `Motor control v5_No Recording.vi` (original, by reference only, md5-checked).
**12:3x — DIRECTION SETTLED and documented in [docs/main-vi-state.md](docs/main-vi-state.md).** Positive control
PASSED on NI's Network Streams example (Traverse class `Global`; two WRITE + one READ `Host Stop` nodes told
apart). The motor subVI has NO global node (18 diagrams). So **`Global motor pos.vi` is write-only in this
hierarchy** (7 writes, 0 reads measured; a reader outside the hierarchy or a legacy carrier — ask the user).
Next (plan under peer review, `…nodeterms-full-sweep-plan.md`): `sweep_nodeterms_main.py` — the whole main VI
(635 nodes, ~10 min) through `node_terms` → junk-free net map WITH direction → local-variable census for the 10
bare-terminal panel objects. **12:34 sweep RUNNING** (`sweep_nodeterms_main.log`, ~12 min; node identity verified
per node — `node_terms` now returns the node's own UID). Class census first: `Global` 7 ✓, **`Local` 8**, `Property`
106, `Invoke` 1 (`LocalVariable` → error 1092). Step-0 tree artefact found: uid 22963 is listed on 11 diagrams,
always last — a phantom, harmless (the sweep stops at UID 0). Analyser ready: `analyse_nodeterms_main.py` →
locals/`Value` section of docs/main-vi-panel-map.md.
**12:4x — SWEEP DONE: `tools/bench/main_vi_nodeterms.json` = the junk-free net map WITH direction (626 nodes, 3328
terminals, identity verified per node, 0 real mismatches vs the Step-0 cache; 662 s).** Locals/`Value` section
written into docs/main-vi-panel-map.md: **8 local variables** (terminal name == control label on all 8: `Total Lost
Frames` ×2 W, `File # Saved` W, `Focus Pos (Track)` W, `Rot pos (deg)` R, `Trans Pos (mm)` R, `Picture` W, `Color
table` R); of the 10 bare-terminal objects only `File # Saved` is reached by a local. **106 `Value` property nodes,
88 implicit** (bound object not readable cast-free — the remaining attribution gap, with event-structure
registrations; the other 9 bare objects are unattributed, not "unused"). Globals cross-check: 7/7 same direction.
Sweep bug fixed (stats overwrite; class uids re-read by `patch_nodeterms_classes.py`).
**13:0x — STAGE 1 first pass, offline: [docs/frame-loop-wire-graph.md](docs/frame-loop-wire-graph.md)**
(`wiregraph_frame_loop.py`, peer-reviewed plan `…wiregraph-frame-loop-plan.md`). Checked: wire uid == logical net
(0 wires with >1 source; fan-out shares one uid, 19 wires, max 6 sinks). Kernel #5058: 8 of 10 inputs come from
the loop border (calibration/parameters), 2 from the previous-frame state case #5540; outputs → state case #2222,
`save trace.vi`, plots. The loop body is ONE data component (72/75 after cutting error/refnum/timer wires) — units
are not separable by wiring alone; **83 of 156 wires are unresolved half-edges** because the WhileLoop's own
tunnels/shift registers are not in `Nodes[]`. Next: an op reading `LoopTunnel` → `Outer Term`/inner terminals →
names + wires, to turn those half-edges into the loop's named inputs/outputs (stage-2 boundary list).
Startup doc closed two items (frame 10 = ASI Initialize = COM4; frames 5/8 write globals); inventory plan updated.
**13:3x — `OpTunnels_v0` BUILT (228 s, saved; plan peer-reviewed `…optunnels-v0-plan.md`: IDs Inside Terminals[]
6356000 / Outside Terminal 6356001 / IndexMode 6356C00; shift registers = sibling classes, NOT covered by v0).**
Per LoopTunnel (Traverse index → TMSC(LoopTunnel), donor OpSetIndexMode_v0): tunnel UID, IndexMode, outer terminal
name / Is Source? / wire UID (+ error cols), inner terminals as arrays (one per frame). `InsideTerms[]` auto-indexes
into a Terminal-class node cast-free. Functional test + main-VI census running (`test_optunnels.py` →
`main_vi_tunnels.json`; how many of the frame loop's 83 half-edges a tunnel wire explains is printed, not asserted).
**13:5x — `OpTunnels_v0` FUNCTIONALLY VERIFIED (all PASS; scratch: 5/5 tunnels, opposite directions, wires match the
node_terms oracle) and the main VI's 132 LoopTunnels censused (173 s).** Frame-loop border named in
[docs/frame-loop-wire-graph.md](docs/frame-loop-wire-graph.md): **31 tunnels = 25 inputs / 6 outputs** (camera
session + error chain, image, calibration clusters & cosine windows, bead-pack counts, cross size, file paths;
outputs: file number/progress, current image number, session/error out). 29/83 half-edges resolved; **54 remain =
shift registers (the per-frame STATE carriers) + loop terminals** — not LoopTunnels; reading them needs a cast to
LeftShiftRegister/RightShiftRegister (no donor) or `Loop.Shift Registers[]` (Loop-typed ref) → OPEN, next tool.
API: `gscript.tunnels(target, index)`. Handles +17/20 runs (main VI, same Open-VI-Reference growth).

### 2026-09-14 DAY LOOP — cycle 1 DONE: `OpBuildPN_v1` ends silent non-attach; both cast-free ladders OPEN

`OpBuildPN_v1` saved and verified (`build_opbuildpn_v1c.log`): control clean/1, bogus ID → **1077**, and
**`Control.Terminal` 6332006 and `AbstractDiagram.SubVIs[]` 6375802 both ATTACH**. `gscript.build_property`
now uses v1 and raises on creator error. Cycle 2 = compile the identity ladder (`SubVIs[]` → `SubVI.VI Name`)
and the panel ladder (`Control.Terminal` → `Is Source?`/`Connected Wire`) with v1, then sweep.
Earlier text below is kept as the record of how it was found.

Two facts, both from code/panel reads, not inference: (1) **`net_map` aborts** its node loop at the first node
whose per-node op run fails or reports UID 0 — every later node on that diagram is unvisited (tools/gscript.py
`net_map`: `except RuntimeError: break` / `if style == 0: break`). This is why three attach probes disagreed;
it also means the 170-diagram cache may be truncated on any diagram with such a node — treat per-diagram node
lists as *at least*, not *exactly*. (2) **`OpBuildPN_v0` discards the creator's `error out` and `Outputs`**
(creator uid 297, both unwired) — an unsupported property ID's error (1077) never reaches Python, leaving a
rows-less node identical to success. Fix in flight: `OpBuildPN_v1` (creator error + Outputs → panel), plan under
peer review, recipe `tools/recipes/build_opbuildpn_v1.py`, verified by a control AND a known-bad ID before use.
Cast-free ladders (SubVIs[] 6375802, Control.Terminal 6332006) are UNDECIDED until v1 can read the creator.

**Walker "limit" — CORRECTED 2026-09-14 ~12:xx; the stale-reference reading below was wrong.** Measured by class
census (`tools/bench/probe_builder_artifact.log`): **one `net_map` call adds 75 untyped junk Invoke nodes to the
target** (spec §33: OpNetInfo's neutralised creator drops one per run) and leaves it ExecState 0; deleting them +
Remove Bad Wires restores ExecState 1 with a census identical to pristine. `build_property` (v0 AND v1) is clean.
So: fresh nodes were "invisible" because they sat in `Nodes[]` behind the walker's own junk, on which its
end-of-nodes heuristic stopped; every ladder probe and all three `OpReportNodes_v0` builds broke because they had
called `net_map` on the target. Fix: `net_map` now purges its junk and runs Remove Bad Wires itself. The overnight 170-diagram sweep walked the main VI working copy and so poured junk Invokes into its in-memory
copy (never saved; disk md5 unchanged) — **already discarded by this morning's LabVIEW restart**, nothing to
revert. Per-diagram node lists in the cache are still *at least*. Path note (consistent with every working script, not separately tested): the revert probe passed a FORWARD-slash
path and Open VI Reference answered error 7; all working scripts use backslashes.

Plan peer-reviewed (`archive/peer/2026-09-14-autonomous-loop-plan.md`). Verdicts: **Node.Label rejected** as an
identity ("label must be displayed once"; it is a user label, not the callee). New cast-free routes to prove by
one compile each: `AbstractDiagram.SubVIs[]` 6375802 → `SubVI.VI Name` 635E401 (identity);
`Control.Terminal` 6332006 → `Terminal.Is Source?` 634A003 / `Connected Wire` 634A000 (panel wiring + direction;
read = source, write = sink — validate on one known pair). Global *field* identity still needs `Global.Control
Name` 6354802 (cast). Cycle 1 = `tools/recipes/probe_castfree_ladders.py`. LabVIEW restarted fresh (pid 14088,
34,310 handles); never-saved op copies deleted.

### 2026-09-14 OVERNIGHT — documentation first, by the user's direction. Read this before anything else.

The user's order (2026-09-13): understand and DOCUMENT before building — *"애초에 코드 다 뒤져봤으면 당연히 알거
아니야? … 시작하기 전에 내용 파악후 문서화가 가장 첫 스텝"*. Plan: [docs/system-inventory-plan.md](docs/system-inventory-plan.md).

| doc | state |
|---|---|
| [docs/instrument-libraries.md](docs/instrument-libraries.md) | **done** — ports from NI-VISA, drivers from `instr.lib` |
| [docs/main-vi-panel-map.md](docs/main-vi-panel-map.md) | 114 objects, CTL/IND — **wiring column missing** |
| [docs/main-vi-state.md](docs/main-vi-state.md) | **the 3 shared fields** — writer/reader map missing |
| [docs/rotor-sign-diagnosis.md](docs/rotor-sign-diagnosis.md) | **done** — diagnosis only, nothing changed |
| [docs/main-vi-startup.md](docs/main-vi-startup.md) | **first pass** — frames 1–13 by terminal signature; port on frame 10 unresolved |

**The full sweep exists**: `tools/bench/main_vi_netmap.json`, all 170 diagrams, 635 nodes, 91 min, complete.
Analyse it with `tools/bench/analyse_netmap_cache.py` — counts matches, never asserts identity. Validated: it
found the camera node at diagram 87 uid 9775, the same node the 2026-09-12 census found by a different route.
**Rotor zero settled**: `Baseline Startpoint` is not on `SetCommand.vi`'s connector pane (9 call sites, all 7 of
the same terminals, none of them Baseline), so the driver default **200.0** applies everywhere; unit still open.
**Every remaining gap** (panel wiring column, global read/write direction, node identity, the 115200 port on
startup frame 10) reduces to ONE blocked capability: a class-specific property read on a GObject-typed reference.

**Settled overnight.** Rotor = **Autonics** (COM5, alias `Rotor`), driver = the three VIs in
`instr.lib\Autonics Motor\`; PI M-126.PD1 = COM3; ASI = COM4. Shared state is exactly three DBLs:
`Trans position`, `Rot position`, `Focus position`. Main VI = **170 diagrams**, 133 of them case/sequence frames.
The rotor's negative-angle workaround is a **read-back parse**: the `Get Position` frame converts the reply with
an **unsigned** default (`0uL`), so a baseline keeps the coordinate positive — the user's own hypothesis, and the
PMC-1HS/2HS manual shows the controller accepts negative commands (`PAB 10, -1`).

**FIRST TASK WHEN AWAKE — and it is a DECISION, not a build.** Everything unfinished (the panel map's wiring
column, the state writer/reader map, the startup trace, `OpReportNodes_v0`) is blocked on one capability: reading
**why** a scripted VI is broken. `ExecState == 0` says only "broken".

The route to it — `VI:Get Errors` (452, private) — ran into a **circularity that is now measured, not guessed**:

- private members do not attach through our builder (`Control.Value` 09-12, `VI:Get Errors` 09-09 & 09-14:
  node created, member never attached);
- peer review proposed the dedicated `Allow Private` setters (`6370003` / `636F406`) as the cause;
- **three probes failed to confirm it** — each time the *reader* failed, not the question. Run 3, the only one
  whose control passed with an adequate read window: the node exists but `net_map` cannot read its terminals.

**So making the broken node readable needs the very capability being sought.** That is the finding, and it is
written up honestly in [docs/toolkit-capabilities.md](docs/toolkit-capabilities.md) — including the withdrawal of
two wrong intermediate claims (a "spray of ~67 nodes", and two premature "private is unreachable" verdicts).

The remaining option is a **donor node copied with `Create from Reference`**, which needs **one gated GUI action**
to create the donor — deliberately NOT taken unattended. That is the decision to make.

**A practice that earned its keep:** every probe of a suspected capability limit now runs a **control** — the
known-good case through the identical code path — and prints INVALID if the control fails. Run 1 would otherwise
have recorded "private members are GUI-only" as a permanent limitation. It was false.

**New mechanical rule.** `tools/hooks/guard_peer.py` blocks the next build after a failed prediction until a peer
review is archived — built because four rule violations happened in one stretch and the user said
*"규약을 셋팅해도 그럼 자꾸 회피한다는거잖아"*. It fired twice overnight and both times caught a real unreviewed
failure; the second produced the Allow-Private finding above. Known wart: its pattern treats any
`tools/bench/*.py` as a build, so it also blocks read-only inventory scripts — **not narrowed unilaterally**,
since adjusting a gate when it is inconvenient is how gates die.

**GPU on a different machine — settled 2026-09-13, measured.** Our kernel is portable (`-arch=sm_75` already embedded
`compute_75` PTX; the DLL is now rebuilt with native `sm_75/86/89` cubins + that PTX, numerically identical to the digit
on the 41-frame fixture). **cuFFT is the part that breaks**: under NVIDIA's own forced-PTX acceptance test
(`CUDA_FORCE_PTX_JIT=1`) our kernels load but `cufftPlan1d` returns `CUFFT_INTERNAL_ERROR`, isolated to that variable.
So RTX 30xx/40xx are fine with the current toolkit; **an RTX 50xx (Blackwell) box needs cuFFT from CUDA 12.8+**, and the
1e-6 px acceptance must be RE-RUN on any new GPU (`N=200 py tools/gpu/test_mt2.py`) because cuFFT guarantees
reproducibility only for a fixed GPU model.

**Decided by the user:** two separate top-level VIs (`4.6 cpu parallel` / `4.6 gpu parallel`), no runtime backend
switch; restructure FIRST and add the rotor inside it (experiments continue on the original VI); rotor = a 4th ROW of
`CycleSchedule`, absolute degrees, translation then rotation; `Value` property nodes become local variables by rule
rather than by measurement.

**The construction method changed on 2026-09-13 and this is the headline.** "Extract regions into subVIs" is dead:
(a) the user ran LabVIEW's **Clean Up Diagram** on an earlier version, so node positions carry NO functional meaning
and no box can be drawn around a feature; (b) measured — the cleanest candidate seam (diagrams 160-163) has **0
state-carrier hazards but 66 wires crossing its boundary**, against a 28-terminal connector pane limit. The replacement
is **rebuild the seven-loop top level fresh, reusing the 98 existing subVI calls unchanged**, deriving grouping from
the WIRE GRAPH (which Clean Up did not touch) rather than from layout.

**subVI call cost: ~100 ns** (86 ns measured in a community benchmark; Case dispatch ~6 ns; inlining unnecessary).
At a 6.00 ms budget, 100 calls = 0.01 ms, so the new code may be divided as finely as clarity wants. **NI's own help
text says "tens of microseconds" — unsourced and 600x off.** The real millisecond risks are array copies, UI-thread
work, allocation, GPU transfers and non-reentrant serialisation.

**Reentrancy, read 2026-09-13 (ActiveX exposes `IsReentrant` directly - no op needed):** every tracking kernel is
reentrant; **both focus VIs (`ASI_adjust focus-subvi`, `MCL_adjust focus-subvi`) are NOT**. That is a deliberate guard,
not a defect - two loops must never drive the stage at once. So keep it non-reentrant AND keep its callers to one.
(`ReentrancyType` reads 1 for every VI regardless of `IsReentrant`; it does not mean what the name suggests - ignore it.)

**Inter-loop state:** three fields of one VI global, `Global motor pos.vi` - `Trans position`, `Rot position`
(written at init, read by the motor loop) and `Focus position` (**written by the frame loop**). A whole-tree byte scan
found no other accessor in our hierarchy, so each field has exactly ONE writer today. Constraint for the split:
`Focus position`'s writer must MOVE to the ASI/focus loop, never be written from two.

**Gates:** G1 closed (design rule) · G2 closed (native extraction reachable via private `AbstractDiagram.SubVI From
Selection` = `6147ED`, tokens already set, but demoted - it converts locals into UI-thread property nodes) ·
G3 partially closed (cycle EXECUTION confirmed inside frame loop diagram 43 by node-position boxes; the table-editing
region is somewhere in the strip of diagrams 145-167, pinpointing deferred to stage 4) · G4/G7/G8/G9 open.

**Next:** stage 1 = derive each functional unit from the wire graph (anchor = the tracking kernel call, uid 5058).

### WORK ORDER — the restructuring is LAST, not first (corrected by the user 2026-09-13)

An earlier list here read as five parallel buckets. It is a dependency chain: **everything else is an INPUT to the
restructuring**, which is the final deliverable.

```
1. TOOLING        array-returning op (below) - unblocks everything that reads diagrams
        |
3. GATES          G4 image handoff · G7 slot-ownership state machine · G8 fault/shutdown · G9 core budget
4. MEASUREMENTS   array-crossing cost · display path cost · UI-thread Value cost
5. USER DECISION  where rotor zero is
        |
2. RESTRUCTURE    stages 0-6  <- starts only when the above are answered
```

Why they are prerequisites, not parallel work: G4/G7/G8 decide how the queues and image pool are BUILT in stage 2 —
deciding mid-build means rebuilding. G9 decides whether seven loops is viable at all. The array-crossing measurement
can impose "never split on images", which changes stage 2's design. And the rotor zero-point shapes the schedule data
structure that stage 4 writes into. Saying these could "proceed in parallel with construction" was wrong: the document
work can, but entering construction without their conclusions cannot.

### TOOLING BOTTLENECK FOUND 2026-09-13 — fix this BEFORE the restructuring

The fleet's traversal is **O(n²)**, and the cause is not what was assumed. Measured:

```
one bare op run, SMALL target VI     10.4 ms
one bare op run, the MAIN VI       960.8 ms      <- 92x, scales with TARGET SIZE
SetControlValue / GetControlValue    0.07 ms     <- COM is irrelevant
```

`report()` and friends call the op **once per object**, and **every run re-traverses the whole target VI**.
626 nodes x 0.96 s = 601 s, matching the 618 s actually measured. Same for every sweep done today.

**The fix is an op that loops INSIDE LabVIEW and returns ARRAYS** — one traverse, one run. That is
**hundreds of times faster** (626 nodes: 601 s -> ~1 s), and more fundamental than the UID-lookup trick invented the
same day (which cut the NUMBER of traversals, 170 diagrams -> 38, not the cost of one). The restructuring reads far
more diagram than today did, so it pays for itself immediately.

**UNBLOCKED 2026-09-13 22:5x — the array indicator is solved, and the stated blocker was wrong.** It read "no donor
exists ... front-panel object creation is the fleet's weak spot". No donor was ever needed: an indicator created
**from a tunnel** is typed by LabVIEW, so the array comes for free. Two ops now cover the whole output side, and
both are FUNCTIONALLY verified (a real call, value read back over COM — not just ExecState):

| step | call | verified |
|---|---|---|
| auto-indexed OUTPUT tunnel | `exit_loop(node_class="Property", ["Position"])` | LoopTunnel 1→2, Wire +1, ExecState 1 |
| force auto-indexing | `set_index_mode(target, tunnel, 1)` | op existed since 2026-08-31 |
| **the array indicator** | **`tunnel_indicator(target, tunnel)`** — NEW, `OpTunnelInd_v0` | new indicator `Array` reads `()` over COM = **an empty ARRAY**, not `(0,0)` |

`exit_loop`'s docstring was also too narrow: it says the names must be on the node's CONNECTOR PANE, but
erdosmiller's `Get Outputs.vi` enumerates a node's output terminals, so it works on a **Property node** too.

**Why `create_indicator` could never do this** (measured, not assumed): it addresses `Nodes[]→Terminals[]`, and a
sweep of a For Loop's `Terminals[0..13]` gave DANGLING indicators for 0–7 (front-panel object appears, **no wire**)
and nothing beyond. `ForLoop.Terminals[]` are the loop's own infrastructure terminals, and **a Tunnel is a GObject,
not a Terminal** — it inherits no Terminal methods. The route needs one extra hop, which is all `OpTunnelInd_v0` is:
`Tunnel.'Outer Term' (6356001) → Terminal.'Create Indicator' (6349C02)`, built on `OpSetIndexMode_v0`'s proven
`Traverse('LoopTunnel', index) → IndexArray → To More Specific Class` front half.
Peer review: `archive/peer/2026-09-13-tunnel-array-indicator.md`. Terminal names: `docs/NAMES.md`.

Also fixed today: **`gscript.wire()`'s guard was wrong for boundary crossings** — a wire into a loop creates a tunnel
AND splits into two wire objects (+2), so the flat `+1` check raised on three consecutive probe runs whose wires had
actually succeeded. It now expects `1 + tunnels created`, checked exactly.

### TASK 1 IS DONE — 646.50 s → 1.70 s, rows IDENTICAL (2026-09-13 23:3x)

`OpReportAll_v0` is built, saved and **functionally** accepted. `gscript.report_all(target, cls)` is a drop-in for
`report()`, same `[{i, class, uid, pos, owner}]` shape.

| target | class | n | `report_all` | `report` | speed-up | rows |
|---|---|---:|---:|---:|---:|---|
| main VI | Node | 626 | **1.70 s** | **646.50 s** | **379.8×** | IDENTICAL |
| main VI | Property | 106 | 1.15 s | 108.13 s | 93.8× | IDENTICAL |
| small | Node / Wire / CtlTerm / Diagram | 14/28/8/1 | 0.05–0.13 s | 0.09–0.31 s | 2–6× | IDENTICAL |

IDENTICAL = uid, class, pos and owner all match **in order** (order compared on purpose: a same-set/different-order
result would corrupt index-based lookups silently). `report_all` is nearly flat in n — the fixed cost is paid once.
646.50 s confirms the 618 s baseline. Report: `archive/bench-2026-09-13-array-reporter/REPORT.md` (INDEX row 21).

**Defect found by the test, fixed and re-verified:** on class `Diagram` the op popped a modal dialog — error 1055,
"object reference is invalid", from the top-level diagram's empty `Owner` — because both property nodes had an
unwired `error out`. `set_auto_error_handling(False)` applied; rows re-checked and still IDENTICAL. Classes that
never error (Node/Wire/Property) had hidden it completely.

**Three terminal names cost three build cycles**, all guessed from documentation instead of read off the machine:
`specific class reference`, `Outer Term`, `ClassName`. Standing fix in `docs/NAMES.md`: **after creating a node and
before wiring it, run `net_map`** — one call, prints every terminal, replaces a build cycle.

**NEXT (task 3/4/5, then 2):** G4/G7/G8 are designed; G9 and the CPU kernel's real parallel-instance count are
unread; the array-crossing / display-path / UI-thread `Value` costs are unmeasured; the rotor zero-point is the
user's call. Only then stage 0–6.

**Two rules learned the hard way while probing this — both cost real time today:**
1. **Never point an op at another op VI.** An op is a *running* VI; LabVIEW refuses (error 6500) and can leave the op
   wedged. To inspect an op, **copy it to a scratch file and inspect the copy**.
2. **ExecState can say healthy while the tool is unusable.** `OpFPLabels_v0` read ExecState 1 yet every call through
   it returned 6500, and `revert()` was itself refused with 6573 ("writable only when the VI is not running") — a run
   reservation ExecState does not report. **Restart LabVIEW.** Judge an op by whether a call succeeds, not by its
   reported state.

Also corrected: `net_map`'s docstring warning of "one 8 s dialog per node" is **stale** — `OpNetInfo_v1` already runs
with automatic error handling off and returns `UID 0` past the end. Details in `docs/toolkit-capabilities.md`.

### NEXT ACTIONS, in value order (2026-09-12 end of session)
1. ~~Frame-loop serial frequency~~ **DONE 2026-09-12** (`tools/bench/read_asi_focus.py`, asi_focus_anatomy.json).
   **Serial does NOT block 150 Hz.** `ASI_adjust focus-subvi.vi`'s top-level (unconditional) diagram holds only:
   2 x Property Node `Value` (uid 46, 108), a comparison (272), a reference pass-through (443), and **Case Structure
   uid 587** whose tunnels carry the VISA wire. The real serial VIs are INSIDE that case on diagram 4 (uid 663 =
   Move Axis to Position, uid 929 = Get Current Position), and the fixed `Wait (ms)` (uid 1179) is on diagram 8, also
   nested. 5 `Value` nodes total (46, 108 unconditional; 48, 1132, 1753 inside).
   **So the unconditional per-frame cost is TWO UI-THREAD property reads**, and a `Value` property node always runs in
   the UI thread - a direct mechanism for "turning the display on destabilises frames", since those reads queue behind
   the panel redraw. The motion audit's line about the motor loop ("separated, but they meet again in the UI thread")
   holds for the frame loop too. NOTE the script's own verdict line says "diagram 0: 1 VISA node" - that is uid 587,
   the Case Structure, flagged because its TUNNELS carry the VISA wire; a structure passing a refnum is not a
   transaction. Do not read that line literally.
2. ~~Measure the UI-thread cost of a `Value` property node~~ **CLOSED 2026-09-13 by decision (user chose this).**
   Converting `Value` property nodes to local variables cannot lose whatever the number is - a local variable never
   enters the UI thread, a property node always does - so the measurement would have set priority, not direction. It
   becomes an unconditional design rule for stage 1 and gets timed later, when stage 1's subVIs make it incidental.
   **Obstacle recorded because it will recur:** `build_property(..., 'VI Server:Control', [('633200D', False)], ...)`
   creates a node but the property does NOT attach (no `Value` terminal, wrong position, Node count 8 -> 224), with the
   same call shape as calls that work. Same symptom as `VI.Get Errors` 0x452. **An ID being listed in
   docs/vi-server-ids.json is not evidence it works.** If a `Value` property node is ever needed by script, copy it
   from a donor. Scratch deleted, donor OpFPLabels_v0 verified intact.
3. ~~Measure the ASI round trip~~ **DONE 2026-09-12** (`tools/bench/serial_roundtrip_asi.ps1`, COM4, 50/50 replies,
   0 timeouts, `/` STATUS only): **median 1.128 ms** for a 5-byte exchange. Do NOT copy that into the budget table -
   decompose it: 5 bytes x 86.8 us = 0.434 ms of wire time, so **fixed overhead = 0.69 ms**, and a realistic ~16-byte
   `WHERE` query costs **~2.1 ms = ~35 % of the 6.00 ms budget** when paid (PI is 2.56 ms; same order). Command safety
   was settled BEFORE transmitting: `archive/peer/2026-09-12-asi-tiger-readonly-commands.md` confirms `/` is query-only
   and its reply is fixed-length (the only shape that cannot trip the driver's read-by-byte-count); it also named
   `SAVEPOS`/`SP`, which halts axes, writes flash and leaves the controller dead until a power cycle. The script keeps
   an empty-by-default whitelist, that blacklist, and a `-IUnderstandTheRisk` gate.
3. **OpConstValue_v0** once its blocker above is settled - then read diagram 87's uid 13598/13540 (the two stacked
   numeric constants left of the camera property node) and the `Wait (ms)`.
4. Measure the display path (`ImageToArray` -> `Flatten Pixmap`) against the 6.00 ms budget.

**Display decoupling:** `Last` mode turns the cliff into a slope (8 ms delay -> 74.9 Hz on Next vs 123.0 Hz on Last,
acquired steady at 149.5), so a display loop on `Last` cannot block acquisition - the remaining risk is CPU/UI-thread
contention, not frame blocking. Ring depth 10/50/100 does NOT move the cliff.

**Main-VI structure mapped this session:** diagram 19 = the parent diagram holding the parallel While loops (where loop
multiplication would happen); diagram 20 = motor loop (already separate); diagram 43 = frame loop, already carrying
buffer-number frame-loss detection (`current image number` / `LastBufferNumber`, uids 3191 & 57) and the tracking call
(uid 5058) and the ASI VISA subVI (uid 48) directly on its body; diagram 99 = display/bead-selection loop using
IMAQdx Get Image -> IMAQ ImageToArray -> **Flatten Pixmap** (the slowest documented path); diagram 16 = autofocus subVI;
diagram 87 = **the camera configuration step**; diagrams 43, 99 and 157 each grab from the camera.

**The halving:** a **ROI, NOT a binning change** (binning stayed 2x2, offsets 0, PayloadSize 327680), so the calibration
is safe and no past measurement is wrong. `IMAQdxOpenCamera` resets the ROI (measured, imaqdx_reset_test.py) and even a
killed client does not leave it (imaqdx_dirty_exit.py), so every run starts full-frame. **Exactly one node in the whole
VI touches camera geometry: diagram 87 uid 9775**, an IMAQdx property node with terminals `Height` then `Width`, both
wired; the two nearest objects are stacked numeric constants uid 13598/13540 immediately to its left. Read-vs-write is
still open and is settled by reading those constants' values (next action 3). One observation stays unexplained and is
logged as such: the day's first probe read 640x512 on a fresh open, which no surviving hypothesis accounts for.

labview-lock:
  status: acquired
  owner: Codex Astra direct GUI benchmark (user authorized)
  since: 2026-09-13
  purpose: ASTRA scratch VI only; screenshot-guided clicks; no hardware execution
```

**GPU v2 (user 2026-09-09: "Saleh꺼 따라하지 마 … 최적으로"): our interface.** DLL side DONE offline: `mt2_open/set_image/track/close` +
one-node `mt2_track_simple(cal_path, pixel_ptr, line_width, w, h, nb, xyz_in, good_in, xyz_out, idx, good, status, len, flags)`
(tools/gpu/cuda/mt2.inc; strided IMAQ-style buffer via cudaMemcpy2D, pinned once; 31 chained frames == LabVIEW ref, 1.58 ms).
LabVIEW side IN PROGRESS: CLFN configured by script through NI's import-wizard library (docs/NAMES.md) — Parameter Info
delivered as a flattened string (COM cannot set cluster arrays) via Unflatten; DONE 02:0x: OpBuildFlatten_v0, OpBuildUnflatten_v0 (generic tools/recipes/build_opcreator.py) and **OpCLFNBuild_v0**
(tools/recipes/build_opclfn.py: NI Create → Library Path/Function Name/Calling Convention/Reentrant (Set) → Parameter Info Get →
Flatten→'data string' | Unflatten('binary string') → Parameter Info Set → Get2 → Flatten→'data string 2' | Prototype→'Prototype' |
Parameter Terminals→'Terms[]'; 41 wires, saved). Sample run 1 showed NI Create.vi needs the wizard's functional globals set first (error 1077 otherwise) → OpCLFNPre_v0
(tools/recipes/build_opclfnpre.py) sets them in the same session. **PC lost power 02:11:43 (Windows event 6008) during that build;
rebooted 11:07; nothing of value lost (unfinished OpCLFNPre copy + scratch deleted; clock-lock logon task re-applied P0).** RESUMED
11:1x: chain tools/bench/clfn_chain2.py (build OpCLFNPre → pre-op + builder sample run, log clfn_chain2.log) then compose the 14-parameter array in Python, set it, verify by Prototype +
Terms[] count + read-back equality; then HARNESS_gpu2 (IMAQ GetImagePixelPtr → one CLFN, DBL in/out, no image copies). Peer reviews: archive/peer/2026-09-09-clfn-*.md.
Rule added (docs/NAMES.md): ONE COM client at a time (two crashed LabVIEW). Lock: acquired while chains run.
**11:3x-12:0x: NI Create.vi KILLS LabVIEW (ACCESS_VIOLATION read at 0, LabVIEW.exe+0x578A41, minidumps d8556cd8/70426c46) the moment
the Function Name global is valid** - variants A (4 globals) / B (+Function Dec) / C (+empty Parameter Info) / E (kernel32+GetTickCount)
all crash in 0.3 s; D (Path only -> error 1077 first) survives; our DLL never loaded. Hypothesis: the EMPTY Parameter Info global is
applied -> node with zero parameters -> NULL deref on redraw. Peer review dispatched (codex, archive/peer/...clfn-create-crash-empty-paraminfo).
Constructive test = OpCLFNParams_v0 (tools/recipes/build_opclfnparams.py): Parameter Info FGV Get -> Flatten ('data string' + 'type string'
= layout sample) and Unflatten('binary string') -> FGV Set, so Python can fill the global BEFORE Create.vi. Chain log tools/bench/build_opclfnparams.log.
**12:0x CONFIRMED + SOLVED: with the global filled (15 records, layout decoded in docs/gpu-backend.md) Create.vi succeeds, no crash; the node
reads back all 15 parameters with our types; Set route + Parameter Terminals (30 refs) work.** `gscript.build_clfn(target, location, dll, fn,
flat_hex)` = one call (Params -> Pre -> Build). Composer tools/gpu/clfn_params.py. Now: tools/recipes/build_harness_gpu2.py (IMAQ Create ->
ReadFile -> GetImagePixelPtr -> CLFN mt2_track_simple, all inputs = controls) - first build reached every terminal (14 controls, all
indicators) but ExecState 0 -> probe (tools/bench/clfn_break_probe.py): kernel32 node fine, ANY function of the deployed DLL broken -> the deployed claudeDev\Debug\GPU Tracking.dll (01:22) predates mt2.inc (no mt2_* exports); redeployed tools/gpu/cuda/mt_track.dll (01:41, 22 exports) - STILL broken -> probes E-K: the SPACE in the file name `GPU Tracking.dll` breaks a scripted CLFN (same bytes as `mt_track.dll` in the same folder are fine) -> our interface now uses claudeDev\Debug\mt_track.dll; chain v4-v6 12:2x-12:5x: IMAQ GetImagePixelPtr's `Function` ring is REQUIRED (control added by a required-input probe, chain fine),
but the scripted CLFN itself breaks the VI whenever the Parameter Info holds ANY argument record (probes M01-M14, N1-N4: return-only
= runnable, return + one argument of any kind = broken, no error from any attribute VI). 12:5x: building OpGetErrors_v0
(tools/recipes/build_opgeterrors.py, VI method Get Errors 0x452) to read the real error text; codex dispatched in parallel
(archive/peer/...clfn-scripted-node-broken-with-arguments). 13:0x RESOLVED: a scripted CLFN's argument INPUTS are required until
wired (tools/bench/clfn_wire_probe.py: control on the argument input -> ExecState 1); the harness recipe's guard made relative.
OpGetErrors_v0 NOT achieved: VI method 0x452 yields no outputs through the erdosmiller creator even with the three private-scripting
ini tokens (LabVIEW.ini, backup archive/LabVIEW.ini.bak-2026-09-09-1300) - backlog.
**13:3x DONE — HARNESS_gpu2 built by script (ExecState 1, saved) and benchmarked: 200 chained frames, 5 beads: gpu2 5.70 − base 4.56 =
1.14 ms/frame (DLL 1.62 incl. 0.38 upload, abort-safe build); outputs == reference (x,y 4.9e-7 px, z 2.9e-6 µm, 0 flips). First run had 32 ms/frame +
stale-frame errors from pinning the IMAQ buffer → DLL-owned pinned staging buffer (mt2.inc). Report
archive/bench-2026-09-09-gpu2-in-labview/REPORT.md (INDEX row 15). Three-way FINAL: seq 8.15 · CPU-par 2.43 · GPU v2 1.14.**
**14:0x abort-safety (user: 실험 중단은 LabVIEW Abort 버튼) — DONE:** `mt2_open` closes any context the DLL still holds (single-context
policy) and the keep-alive thread parks after `mt_gpu_keepalive_idle` ms without a track call, waking on the next one
(`mt_gpu_keepalive_state`: 0/1/2). Verified tools/gpu/test_abort.py: 12 open-without-close cycles → 0 MB drift, results unchanged;
park/wake 1→2→1. Accuracy after the change: 61 frames 2.1e-7 px, 0 flips (tools/bench/test_mt2_abortsafe.log).
**14:xx-15:xx — DROP-IN GPU KERNEL (user: measure frame delay in the working copy's real loop, and finally one subVI whose
setting picks CPU-parallel or GPU).** `GPU_kernel_v1.vi` = a copy of PARALLEL_kernel_v3 (pane + 13 fp objects inherited), diagram
replaced by IMAQ GetImagePixelPtr + GetImageSize + ONE CLFN `mt2_track_simple_b`; recipe tools/recipes/build_gpu_kernel.py,
finisher tools/recipes/finish_gpu_kernel.py (from the checkpoint GPU_kernel_v1_partial.vi). Three findings on the way, all in
docs/: (1) two index spaces - wire_indicators wants the index WITHIN the traversed class, create_indicator wants Nodes[];
(2) a LabVIEW BOOLEAN array needs an "Adapt to Type" (`Any` + By Value) parameter - an Array/U8 parameter makes a bad wire that
Remove Bad Wires deletes, leaving the VI broken (isolated proof tools/bench/bool_wire_probe.py); (3) DLL: `mt2_track_simple_b`
takes the two good-flag arrays as LabVIEW handles, `nb <= 0` means "as many beads as the calibration", and an empty cal path
falls back to MT_GPU_CAL / mt_track_cal.txt beside the DLL. OpBuildCase_v0 (erdosmiller Create Case Structure) is built for the
backend switch. `SubVI.Replace` = 635E001 (docs/vi-server-ids.json) is the route for the single kernel call site (MAIN_VI_MAP
node 39 / uid 5058). **15:4x VERIFIED numerically as a drop-in** (HARNESS_gpuk, built by the same recipe family as the CPU rows, 200 frames):
base 2.92 · par 5.12 · gpuk 14.23 ms → kernel **par 2.20 / gpuk 11.31 ms**; outputs vs the LabVIEW reference: par 0.00, gpuk
2.93e-6 (z only). **The 11.31 did NOT reproduce**: two further runs gave gpuk 3.22 and 2.22 ms while the DLL's own per-frame log
(new: MT_GPU_LOG=<file>, written even when the caller passes status_len 0) said 1.65-1.77 ms every time — i.e. ~0.6 ms of
LabVIEW-side overhead, not 9.7. Machine load varied a lot between runs (base median 2.9 → 7.9 ms), so
**16:0x SETTLED (3 repeats, clocks P0/7000 MHz each time, archive/bench-2026-09-09-gpu-dropin-kernel/REPORT.md, INDEX row 16):
kernel ms/frame — CPU-parallel 2.55-2.72, GPU drop-in 2.65-3.19 (DLL 1.65 = 0.40 upload + 1.12 kernel); par bit-identical to the
reference, gpu z 2.9e-6 µm, 0 flips. At 5 beads the two backends are equivalent; the GPU's per-frame cost is nearly
bead-count independent. The 11.31 outlier never reproduced and is recorded as a non-result.**
**NOT YET RUN in the main VI: that VI initialises the motor and the piezo, so the frame-delay run waits for
the user.**
**16:5x-17:1x — backend-selector subVI (user: "1번만 하자"): PARTIAL.** Case-structure route probed
(tools/bench/case_probe.py, case_out_probe.py, recipes/patch_opbuildcase.py): a 2-frame Case Structure IS created
(diagrams 1 -> 3), subVIs CAN be dropped into a frame (`drop_subvi` diagram_index 1/2), and **wiring a top-level control to a
node inside a frame creates the tunnel automatically** (+2 wires). BLOCKED on two points: (a) erdosmiller
`Create Case Structure.vi` always tries to Connect Wire its `Selector` input and COM cannot supply a terminal refnum, so every
run raises an error-1055 modal dialog (an error-out indicator on the op did NOT silence it); (b) the OUTPUT side (a subVI output
inside a frame -> the pane indicator, i.e. an output tunnel) is still untested.
**Simpler alternative worth taking first:** both kernels already share the connector pane, so the backend can be selected at
EDIT time by `SubVI.Replace` (635E001) on the single kernel call site - a one-command switch (cpu|gpu) with no case structure and
no per-frame branch. Recommend building that before pushing further on the case structure.
**09-09 17:42 PC restarted by WINDOWS UPDATE (event 1074 "서비스 팩(계획됨)", KB5126256 installed 17:43; clean shutdown, no
Kernel-Power 41) — not a power loss.** The two REAL unexpected shutdowns are 09-02 08:41:59 and 09-09 02:11:43 (event 41,
BugcheckCode 0 = power cut / hard hang, both early-morning during unattended sessions; cause unknown, hardware/power side).
**2026-09-10 03:4x-04:0x — OpBuildCase_v1 DONE, functionally verified (`gscript.build_case`).** Stage 2 root cause: the Index
Array from OpBuildIA_v0 arrives UNWIRED (spec §24), so six "source terminal" attempts all broke the VI the same way; wiring
GC1.`Control Terminals` → IA.`array` by name (+1) then `element` → `Selector` (+1) gave wires 15, ExecState 1 → saved
(13,667 B). Peer attack archived (archive/peer/2026-09-10-opbuildcase-v1-ia-unwired.md; machine result preceded it). Functional
test (tools/bench/case_v1_test.py): case +1, diagrams +2, wires +3 (selector + 2 input tunnels), ExecState 1, no dialog —
**only when `Frames` is a 2-name STRING array** (`["0, Default","1"]`); ints/[] trip error 1302 `Frame Names` inside the
library (8 s dialog). Contract in docs/NAMES.md.
**04:2x-04:5x — TRACK_kernel_v1.vi BUILT (tools/recipes/build_track_kernel_v1.py, 106 s, zero GUI): case on control `index`
(0 = PARALLEL_kernel_v3, 1 = GPU_kernel_v1), 10 input + 3 output tunnels auto-created by wire_control / wire_indicators
(first frame +2 wires, second frame +1 = tunnel reused), 40 wires, ExecState 1. FUNCTIONAL backend 0: bit-identical to the
reference, DLL log +0 → frame '0, Default' IS the CPU kernel. Backend 1 first attempt did NOT switch (SetControlValue on a
loaded subVI never reaches its call; ActiveX has no MakeCurValsDefault) → OpMakeDefault_v0 built (VI method 3F3, test PASS).
Timing lesson: touching the kernel via VI Server before timing costs +9 ms/frame (panel loaded); untouched, track 1.62 vs
par 2.76 ms/frame. `index` is NOT on the connector pane (no conpane op): the backend is the control's saved default —
for the user: open TRACK_kernel_v1, set `index`, Edit > Make Current Values Default, save; for scripts: gscript.make_default.**
**19:0x-19:4x — `index` IS NOW ON TRACK_kernel_v1's CONNECTOR PANE (terminal 5), so the main VI can drive the backend with a
wire instead of a saved default.** Two new ops: `OpConPane_v0` (reads a pane: `gscript.conpane`) and `OpConPaneAssign_v0`
(`gscript.conpane_assign`), API in docs/NAMES.md. The pane PATTERN was never touched — it has 16 terminals, 13 were assigned
and 5/6/10 were free, so the assignment cost nothing to the 13 existing ones and no caller broke. Verified on a scratch copy
first, then applied: terminal 5 = `index`, other 13 kept, ExecState 1, 17,059 -> 17,087 B, outputs still bit-identical to the
reference (20-frame re-check). Shipped default is back to `index` = 0 (CPU). Two bugs this cost, both now in docs/NAMES.md:
deleting a node upstream of an Index Array silently deletes the wire DOWNSTREAM of it, and an edit on a VI loaded only through
GetVIReference is declined SILENTLY (the pane assignment reported success and changed nothing until `open_panel` was added).
**20:0x — THE GPU FRAME'S EXTRA ms IS LOCATED (not fixed): it is NOT the DLL and NOT a measurement artefact.** Probe
tools/bench/gpu_overhead_probe.py (3 cells x 200 frames, DLL log on): track is slower even as the ONLY GPU caller
(B: 4.47 vs A: 2.63), the gap reproduces inside one session (C: track 3.55 vs gpuk 2.20), and the DLL's self-timed total is
1.62-1.69 ms in every cell. So the cost is host-side, inside TRACK's GPU frame; the surviving explanation is a compiler copy
across the case tunnel / a non-const CLFN pointer parameter (peer review 2026-09-10-track-gpu-frame-1ms.md). Localizing it
needs edit-time "Show Buffer Allocations", which has no scripting API. **NOT worth fixing: the deployment route is to put
GPU_kernel_v1 at the main VI's single kernel call site (node 39 / uid 5058), which costs zero.** Also: absolute kernel times
are NOT comparable across runs (gpuk read 1.98 / 2.63 / 2.20 in three conditions) - only within-pass comparisons count.
**18:5x-19:0x — TIMING BENCHMARK DONE (INDEX row 18, archive/bench-2026-09-10-track-kernel-timing/): the Case Structure is
FREE (backend 0: track 2.84 vs par 2.87 ms/frame) and the GPU frame costs +1.06 ms (backend 1: track 3.04 vs gpuk 1.98),
cause open. One void attempt recorded (CPU contention made base slower than par).**
**05:1x — TRACK_kernel_v1 FUNCTIONALLY VERIFIED for BOTH backends (INDEX row 17, archive/bench-2026-09-10-track-kernel-v1/):
index 0 → bit-identical, no DLL log from track; index 1 → DLL log +50 from track, dev 2.69e-6 µm z = gpuk's, kernel ms =
gpuk's. Shipped default index = 0 (CPU). Timing rows stay 15–16 (this run was noisy).** NEXT (user decides): quiet-machine
timing repeat of base/par/gpuk/track; connector-pane op so `index` can be wired from the main VI; SubVI.Replace at the main
VI's single kernel call site (node 39 / uid 5058) + frame-delay run in the working copy — motor/piezo, user present.
(Earlier, 2026-09-09:) The restart killed the OpBuildCase_v1 node-inspection run (read-only, nothing lost). OpBuildCase_v1 stood at stage 1 saved
(Get Controls chain, ExecState 1); stage 2 (tools/recipes/build_opbuildcase_v1b.py) failed on three facts to fix: delete the
refnum controls' WIRES not the controls (delete_by_label needs the connector pane, error 5005), the "creator" is probably
uid 105 @ (900,640) not the rightmost SubVI (wire to `Inputs` gave 5001 on the wrong node), and Terminal.owner is not the node
uid (find the Index Array source another way) — diagnostic tools/bench/case_v1_inspect.py was interrupted by the reboot.
NEXT (user decides): deliverable GPU subVI in the 3-node form (mt2_open before the loop / mt2_track per frame / mt2_close after) with
the kernel VI's connector pane; OpGetErrors (error list by script) backlog; keep-alive/clock-lock notes for the rig;
then tools/bench/run_gpu2.py (reference compare + 200-frame timing).

**ROW 3 DONE 2026-09-08 11:2x / 2026-09-09 (final): three-way in LabVIEW, 200 frames, 5 beads — sequential 8.15 · CPU-parallel v3
**2.43** · GPU DLL 5.14 ms/frame (DLL 1.58 ms with SM clock lock + memory keep-alive; outputs == reference, z 2.9e-6 µm).
Root cause of the earlier 3.7× in-LabVIEW slowdown = GPU P-state at low duty cycle (not LabVIEW). Report:
archive/bench-2026-09-08-gpu-in-labview/REPORT.md (INDEX row 14); facts docs/gpu-backend.md.**

**Audit 2026-09-08 07:5x:** the user reported saving a VI by accident; the only original touched is the reference main VI
`..\Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi` (saved 07:50 by the user's own session, 471,229 B, already LabVIEW 2026
format — no format conversion; content changes, if any, are the user's; not re-baselined).

## Where we are (2026-09-01, summarized on the user's request)

1. **Kernel parallelization: structurally done.** `PARALLEL_kernel_v3.vi` (claudeDev, 68,138 B,
   ExecState 1): P=4 For loop, one reentrant `Track 1 of N` per bead, all 9 inputs / 3 outputs
   wired; connector pane inherited from the four-fold byte-copy. The old four-fold structure is
   still inside as dead code that EXECUTES; remove before any timing. Not yet run on data.
2. **Fixture recording: structurally done and saved** in the working copy
   `..\Min_Track N beads V6_ParallelLoop.vi` (473,317 B, 12:07:59, ExecState 1): per-frame
   `imgNNNNN.tif` next to `.cal`/`.tra`, filename from the same frame-index wire that feeds the
   .tra row. Full wiring table, decisions (error splice skipped: kernels are read-only on the
   image) and verification level in [docs/fixture-recording.md](docs/fixture-recording.md).
3. **Strategy settled:** what we built is loop-level parallelism; graph-level (frame pipelining)
   only if measurement shows A+B+W exceeding the camera period. See
   [docs/parallel-strategy.md](docs/parallel-strategy.md).
4. Originals untouched. Rig standardised on LabVIEW 2026.

## FIXTURE ACCEPTANCE 2026-09-07 (user: data in G:\Data\SiHyeong\20260906 ...\test; NEVER run motors/piezo)

Data: 10,044 imgNNNNN.tif (1280x1024 8-bit), cal002 (flattened cluster: 5x2 bead xy, 5x60x119 stack, 155-B params),
tra002-000 (385-B header + LE doubles: 1 lead, then 10,043 rows x 18 = frame, trans, rot, x1,y1,z1..x5,y5,z5). Frame
numbers = tif names (gaps = dropped frames). Parsed copy: %TEMP%\tra002_rows.json.
Built by script (zero GUI): OpFPLabels_v0 / OpNodeInfo_v0 (FP labels, BD node type names via Node.Style),
OpRemoveBadWires_v0 (VI method 410), HARNESS_loadcal.vi (lab loader `Load and prep N cal images.vi` with the File
Dialog replaced by control `file (use dialog)`: cal002 -> 5 beads, cross size 120, 60 slices, x,y,(blankz) array,
exp/ref (0,1,1,1,1), 5 clusters x 7 fields, 0.05 s), HARNESS_compare.vi (14,663 B: loader + IMAQ Create/ReadFile +
make both cosine bandpass -> PARALLEL_kernel_v3 AND READONLY_fourfold_COPY on identical inputs; controls/indicators
made by create_control/create_indicator). Working copy saved params: Cross length 120 px, pixel 84 nm, z step 0.1 um,
60 images, 20 avg. COM cannot push the cluster array into a control (silently empty) -> clusters flow inside LabVIEW.
IMAQ VIs: C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision (Basics.llb\IMAQ Create, Files.llb\IMAQ ReadFile).

**RESULT 14:1x — PASSED (20 frames): PARALLEL_kernel_v3 (fixed) == four-fold kernel bit-for-bit, and both == the
recorded .tra x/y/z (dev 0.00000), 44 ms/frame.** History: 03:0x the four-fold reproduced .tra exactly while v3 gave
(-16.6,-21.2,5.9) for every bead; 05:3x harness sensitivity test showed v3 == four-fold(starting x,y=0) → only the
Decimate→loop→kernel `starting x/y` path was missing (build_v3.py's GUI step); 13:2x read headlessly with OpNetInfo
(t0/t1 UNWIRED); 14:0x fixed by script (OpConnect2 ×2 + set_index_mode ×2 on a copy, swapped in; backup
PARALLEL_kernel_v3.vi.bak_20260907_prefix). **FINAL 16:3x: with the main VI's bead-loss reseed rule in the driver (spec §35), 10,043/10,043 frames v3 == four-fold
bit-for-bit AND == .tra to 0.00000 — no residual. ACCEPTED — archive/bench-2026-09-07-fixture/REPORT.md.**
Tools added today (all script-built): HARNESS_loadcal, HARNESS_compare, OpFPLabels, OpNodeInfo (crashes on
TMSC VIs — do not use there), OpRemoveBadWires, OpSetAutoErr, OpNetInfo_v1, OpConnect2_v0 (both drop one junk
Invoke per run on the target — purge with new_since, spec §33). Lock: released. MAINCOPY_readonly.vi (scratch copy of the working copy, junk-polluted) deleted.

## GPU/CUDA BACKEND 2026-09-07 (user: "시작. 허용 오차는 1e-6 px / 1e-6 um"; algorithm steps unchanged, rule 1a)

Plan + findings: [docs/gpu-backend.md](docs/gpu-backend.md). GPU: RTX 2060 6 GB, driver 457.51 (CUDA <= 11.1), no
CUDA toolkit, no CuPy. **Driver 616.64 downloaded + signature-verified (C:\Users\KimLab\Downloads\nvidia_616.64);
install needs the user's UAC click — two prompts timed out; run `tools\gpu\install_nvidia_driver.ps1` as admin.**
Found: the lab folder `zz_LabView VI\GPU Track Algo (Saleh Lab)` = the UCSB 2013 C/CUDA port of THESE subVIs (BSD) —
used as a reading aid only; the VI wiring is the spec. Reads in progress: `tools/bench/spec_wiring*.json` (net_map of
every diagram of the 12 analysis VIs + 7 calibration-loader VIs, claudeDev\SPEC copies), chain
`tools/bench/spec_chain.py` (self-healing: restart LabVIEW + resume). NumPy draft: `tools/gpu/ref_numpy.py`
**NumPy reference ACCEPTED on the full fixture 21:4x: 10,043 frames, worst |dx| 4.8e-7 px, |dy| 4.5e-7 px, z within 1e-4 um
except ONE frame (1937 bead 5: cal-slice SSD near-tie 0.353483 vs 0.353494 flips the index by one, dz 4.7e-3 um) —
inherent to any non-bit-identical port; user relaxed z to ~1e-4 ("1e-4 차이는 괜찮아").** Two VI facts found by
script-built subVI harnesses (`tools/bench/subvi_harness.py`): the quadratic fit is WEIGHTED [2,4,5,4,2] (numerically
identified, 1.5e-9); the radial profile is single precision. CuPy 13.6 runs on the old driver (pip nvidia-*-cu11 libs,
`tools/gpu/cuda_env.py`); CuPy port `tools/gpu/ref_cupy.py` == NumPy to 4e-12 px (report:
archive/bench-2026-09-07-gpu-reference/REPORT.md). **User's required comparison (2026-09-07 22:0x): (1) original
sequential VI, (2) CPU-parallel v3, (3) GPU DLL — measured IN LabVIEW, no motors.** **DONE 2026-09-08 00:5x (200 frames, 5 beads, in LabVIEW): sequential four-fold kernel 8.15 ms/frame, CPU-parallel
v3 (clean, P=4) 2.43 ms/frame = 3.35×, both == reference (dev 0.0). PARALLEL_kernel_v3.vi is now the CLEAN one (dead
four-fold loop 248 + case 107 removed; backup PARALLEL_kernel_v3_withdead.vi). Harness recipe:
tools/recipes/build_harness_variant.py --name=base|seq|par|gpu.** Was: `tools/bench/timing_chain.py`
(restart → delete the dead four-fold loop uid 248 from a v3 copy → swap into PARALLEL_kernel_v3.vi (backup
PARALLEL_kernel_v3_withdead.vi) → HARNESS_base/seq/par by script → `run_timing.py` 200 frames). **Toolchain INSTALLED 2026-09-08 05:2x (driver 616.64, VS Build Tools 2022, CUDA 12.6.3). DLL built + verified from Python:
`tools/gpu/cuda/mt_track.dll` == NumPy 4e-12 px, == LabVIEW 2e-7 px / 4e-6 um, 1.87 ms/frame (5 beads, incl. image upload);
the LabVIEW-handle entry (decorated export `?GPUTracking@@...` = the Saleh donor CLFN's function) verified with fake handles
(2.5e-6 um). Deployed as claudeDev\Debug\GPU Tracking.dll (+ cudart64_12, cufft64_11). PAUSED 06:1x (user needs LabVIEW): next = copy the donor CLFN (it has a 'path in' terminal -> DLL path is a runtime
input) into HARNESS_gpu by script — `tools/bench/copy_clfn2.py` after `lv_restart` (fixed: gscript OP_MOVE name collision;
copy_into(prepare=) hook + set_node_label). Stale windows DONOR_clfn.vi / GPU_kernel_probe.vi may be open: close without saving.** DLL source ready: `tools/gpu/cuda/mt_track.cu`.

## KEYSTONES 2026-09-06 17:2x: OpBuildInvoke_v0 (0.2 s/node) + OpBuildPN_v0 — typed Invoke AND Property nodes from Python

`gscript.build_invoke(target, "VI Server:Terminal", "6349C03", (x,y))`, `gscript.build_property(target,
"VI Server:GObject", [("632A800", False)], (x,y))` — both machine-verified (Term/Connect Wire;
GObj/Position). IDs: docs/vi-server-ids.json. Step 3a DONE + closed 2026-09-06 18:2x: `gscript.delete_object(target, cls, index)`
(OpDelete_v0, ExecState 1, 0.10 s, no dialog — the ~8 s dialog was a STALE IN-MEMORY copy of the op, spec §19).
Step 3b in progress (spec §17–§20): typed references by the script-only ladder Diagram→`Nodes[]`→Node→`Terminals[]`
(Diagram wire into a Diagram PN verified ExecState 1). **OpMove_v0 DONE 18:4x with ZERO GUI acts** (`gscript.move_object`,
0.04 s, spec §21). **OpBuildIA_v0 DONE 19:2x** (`gscript.build_index_array`, node arrives unwired, spec §24). **OpCreateControl_v0 DONE 19:5x** (`gscript.create_control(target, node_index, terminal_index)`, 0.15 s, ladder
VI→Block Diagram→Nodes[]→IA→Terminals[]→IA→Create Control, spec §25; Nodes[] = creation order). **OpCreateControl_v1 DONE 20:3x** (returns the created control's label; spec §27) + **OpCreateIndicator_v0**.
**OpConnect_v0 DONE 21:0x** (`gscript.connect_terminals(target, sink_node, sink_term, src_node, src_term)`, 0.06 s; a fresh
Index Array went ExecState 0→1 when wired from Traverse's GObject Refs; wired sinks must not be targeted — spec §28).
**Steps 1–3 complete; step 3b used ZERO GUI acts.** End-to-end check 21:0x: build_index_array 0.17 s → connect 0.06 s →
create_control 0.26 s ('index 3') → move 0.15 s on a scratch copy, then deleted. Open: Nodes[]-order reporter, error
visibility, step 1b inventory op (spec §28). LabVIEW clean (no scratch files, no dialogs).
Step 1b (inventory op) deferred; docs/vi-server-ids.json is the interim registry. Spec §14-§17.

## (superseded) KEYSTONE 2026-09-06 14:0x: OpBuildInvoke_v0.vi — TYPED Invoke nodes from Python (class string + method ID + position)

Verified t8: `VI Server:Terminal` + `6349C03` → a Term / Connect Wire node at the requested spot.
Contract + the reference-unwired rule in docs/keystone-op-spec.md §14 and docs/NAMES.md. Wrapper:
`gscript.build_invoke(target, cls, method_id, location)`. Open: error-7 dialog per run (Create SubVI
branch; deletion = GUI, not approved), method-ID inventory reporter, Property-node twin. Facts in
docs/NAMES.md. Substitution-protocol ops (copy_into/delete_by_label) confirmed unusable until they stop
depending on the editor's Save (§13). Every GUI act logged in tools/gui_actions.log.

Creates an Invoke node on a target diagram from Python (vi path, Class Name="Diagram", index,
Class Name 2 = method string, location (0, 0) = position — verified (500,600) exact, v1 06:1x). One approved GUI branch wire was needed (Diagram in); everything else
by script. v0 limits + next steps in docs/keystone-op-spec.md §12. Evidence of every click:
tools/gui_actions.log. LabVIEW clean (scratch target deleted).

Verified today: copy_into with a vi.lib donor CRASHES LabVIEW (T2); Terminal.Create Control /
VI.Create from Data Type exist (codex) — the control problem is solvable by script; but the Invoke
keystone build showed that erdosmiller Wire Inputs cannot BRANCH an existing wire (3/3 broke the
diagram). One GUI branch-wire per op build is the residue; user approval pending. Nothing saved;
LabVIEW clean (restarted 04:26, handles baseline ~34k this instance).

Discovery run 2 (under bgrun, 15 min cap): D1 drop OK; D3 wires accepted (verification pending on
ExecState after ALL inputs); save of a broken VI impossible (scripted edits do not dirty the VI ->
Ctrl+S no-op; COM SaveInstrument blocks on broken); D2 copy_into of the array-of-cluster control
HUNG (COM wedged through the substitution protocol) and was killed at the deadline — the Move example
files were left substituted and have been restored from the .ci_* backups. `tools/recipes/build_keystone.py`
(never-save-broken order) is written but untested. Decision needed: bootstrap the `Properties` control
with `Terminal.Create Control` on the creator's terminal (needs one Invoke method change = one GUI act
or an OpSetMethod op) vs. keep fighting copy_into. Scratch VIs deleted.

D1 (drop creator) passed; gui_save and delete_by_label hung 3 h 48 min unnoticed -> new mechanics:
`tools/bgrun.py` deadline runner (hook-enforced for backgrounded LabVIEW jobs), gui_save title-bar
click (H5), open_panel(activate=False). A per-call COM guard refactor of gscript was tried and rolled
back (`tools/gscript.py.guarded_attempt_20260905`). Plan v2 keeps Wire Inputs (empty Names) instead of
deleting it. Next: rerun tools/recipes/keystone_discovery.py via bgrun (15 min), then build_keystone.py.

## DONE 2026-09-05 13:xx: M3v1 clicker toolkit (tools/lvclick.py) — 12/12 verified, 0 screenshots

`calibrate / focus_bd / move_node / place_from_palette / node_menu / dialog_button`, geometry in
[docs/gui-geometry.json](docs/gui-geometry.json), spec+review in [docs/m3-clicker-spec.md](docs/m3-clicker-spec.md),
teaching note LEARNING.md §8, results report §9. Unknown geometry -> verb refuses -> vision once -> registry.
NEXT: keystone op ([docs/keystone-op-spec.md](docs/keystone-op-spec.md)) built with lvclick for the
verified-impossible residue only; then fixture/v3 functional acceptance.

## DONE 2026-09-05 11:57: GUI-executor model x effort matrix

22 valid cells (20 + sonnet-medium x3). Haiku 2-3/12 (drag only) at every effort; Sonnet/Opus/Fable
11-12/12 at every effort; effort raises only cost/time. Executor choice: **opus-low** ($3.53, 9.3 min,
66 turns), budget alternative sonnet-low ($3.16, 15.8 min); Fable stays the planner. Full table +
incidents: [docs/benchmark-report-2026-09-04.md](docs/benchmark-report-2026-09-04.md) §8; evidence
`archive/bench-2026-09-04/matrix/`. Rerun: `tools/bench/run_matrix.cmd` via Task Scheduler task
`LVBenchMatrix` (never as a child of this session — see CLAUDE.md hooks note).

## Next actions (in order)

0. **LabVIEW hygiene (user reports sluggish / '응답 없음', 2026-09-06):** CORRECTION — a fresh LabVIEW
   (restarted 04:15) shows 31,515 handles within a minute, so the 32,480 of the old instance was
   baseline, not a leak. Remaining explanations: the H5 UI-loop stall our automation leaves behind
   (released by a click) and pending calls of killed clients. Tools added: `lv_gui -Action ping`
   (per-window responsiveness), `tools/bench/handle_audit.py` (handle delta per operation type),
   bench_prep handle read + relative threshold. Rule: CLAUDE.md §3 "Reference hygiene". VERIFIED 04:18: handle deltas per
   phase A +29 (20 reports, same process) / B -4 (child, clean exit) / C +7 (10 open/revert/close) /
   D +51 (10 drop_subvi+revert) / E -2 (client killed mid-work) / F +1 (20 GUI queries); back to
   31,558 after the audit process exited; ping 0 ms on every window. Handles are NOT the cause of the
   sluggishness; the fleet's reference behaviour is flat at this scale. Evidence: archive/bench-2026-09-06-handles/.

1. **USER (hardware):** run the working copy a few frames at low frame rate with saving on;
   confirm `.cal` + `.tra` + `imgNNNNN.tif` land together and numbers match (gaps = lost frames).
2. **Functional acceptance (rule 1a gate):** same fixture frames through four-fold and v3 ->
   numerically identical X/Y/Z. Check first whether `.tra` holds raw kernel output or calibrated
   values. Then delete the dead four-fold structure in v3 and benchmark A/B/W per stage.
3. Fleet backlog (only as needed): fused topology-specific wiring ops (peer verdict 8/10),
   OpSetIndexMode error-out indicator, integrate `set_index_mode` into `tools/recipes/build_v3.py`
   replacing its GUI pauses; a ring-code primitive dropper (NI `Adding Objects.vi` pattern +
   `RingConstant.Strings And Values[]`) is the scripted replacement for palette placement.

## Hard-won this session (details in the skill / NAMES.md)

- `focus` taps Alt -> LabVIEW menu-bar keyboard mode -> next Ctrl-combo eaten, COM blocked.
  **Always focus -> Esc -> keys.** Esc is also the COM-unblock when calls time out with no dialog.
- Quick Drop is broken in this install; the right-click Functions palette works (click a category
  twice). Keep the LabVIEW instance alive with an open panel: a COM-autolaunched instance dies
  with its client, and a bash `&` launch dies with the shell.
- Everything valuable is saved; a hung LabVIEW may be killed freely (restart permission stands).

## The work cycle (user directive, 2026-08-31)

1) plan + peer-review the plan -> 2) ONE long script, names from [docs/NAMES.md](docs/NAMES.md)
-> 3) run as a batch -> 4) read results, revise -> 5) repeat. GUI only where scripting is verified
unreachable, gated by `tools/lv_gui.ps1`.

## Where everything else lives

- [docs/NAMES.md](docs/NAMES.md): verified terminal/label strings (newlines are real).
- [docs/fixture-recording.md](docs/fixture-recording.md) / [docs/parallel-strategy.md](docs/parallel-strategy.md)
- [docs/benchmark-report-2026-09-04.md](docs/benchmark-report-2026-09-04.md) — meeting-ready benchmark report; raw evidence in `archive/bench-2026-09-04/`
- [archive/benchmarks/INDEX.md](archive/benchmarks/INDEX.md) — catalog of EVERY benchmark (what it was, varied/fixed, result, evidence)
- [.claude/skills/labview-automation/SKILL.md](.claude/skills/labview-automation/SKILL.md): technique.
- [tools/gscript.py](tools/gscript.py): the op fleet (docstrings are contracts).
- [CLAUDE.md](CLAUDE.md) rules / [ARCHITECTURE.md](ARCHITECTURE.md) rig / [archive/](archive/) history
  (incl. `2026-09-01-status-before-summary.md`, the pre-summary STATUS); not read in normal work.
