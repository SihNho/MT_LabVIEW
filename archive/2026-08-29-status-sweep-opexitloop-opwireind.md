---
type: narrative
status: historical
date: 2026-08-29
tags: [archive]
---

# Archived from STATUS.md — 2026-08-29 sweep

Narrative blocks moved out of `STATUS.md` per rule 4 (dated entries accumulate → move to archive).
Every *conclusion* these blocks produced lives on in the active docs (STATUS fleet table, the
`labview-automation` skill, PLAN_kernel_parallel.md); what follows is the session-by-session story.

## Checkpoint — 2026-08-29, OpWireInd_v0 BUILT, SAVED, SMOKE-TESTED

**`OpWireInd_v0.vi` is on disk (10,188 B, 6 SubVIs, 26 wires, ExecState 1, cold-reload verified)**
— wires a node's output terminals to EXISTING front-panel indicators by label, via erdosmiller
`Wire Indicators.vi`. Controls: `vi path`, `Class Name`/`index` (source node), `Names` (source
output terminal names), `Class Name 2`='Diagram'/`index 2` (the diagram), `Names 2` (indicator
labels). Build was ~90% scripted: delete Wire Inputs → drop WI → 4 scripted wires; GUI was one
class-constant retarget (`Node`→`Diagram`, left-click dropdown at the (609,410) constant) and one
`-Action wire` gesture (Names 2 stub (872,496) → WI `Indicator Names` left-edge row 2 (886,496)).

**The contract, proven on a scratch copy of OpExitLoop (created+deleted same session):**
- WI **selects existing indicators by label and BRANCHES them onto the wire attached to the source
  terminal**. No new Wire object is created — **wire-count verification is useless for this op**;
  verify with `ExecState==1` instead.
- **The source terminal MUST already be wired.** An unwired source makes WI extend an unrelated
  wire → "This wire connects more than one data source", VI breaks (28 wires, ExecState 0).
  With source = a node's already-wired `error out`, the indicator receives the error value while
  the Clear Errors sink stays attached — exactly the error-visibility topology wanted, dialog-free.
- Success run: 0.07 s. A swallowed 5001 (bad name) is still a silent no-op — same as exit_loop.
- Context Help on WI (read 2026-08-29): "Outputs is an array of terminals to wire to the input
  terminals of the indicators selected with Indicator Names on Diagram in." Terminals left-edge
  top→bottom: `Diagram in`[0], `Indicator Names`[5], `Outputs`[7], `error in (no error)`[11].
- GUI lesson: two failed click-click wire gestures (one left a pending band that BLOCKED all COM
  until Esc — recovered per the skill); the bundled **`lv_gui.ps1 -Action wire`** primitive
  (approach + settle motions) landed it first try. Use it, not raw click pairs.

**ALL DONE (2026-08-29 evening). Error visibility is fleet-wide:**
- `gscript.wire_indicators(target, node_index, src_terms, indicator_names)` added; it raises on a
  broken target and refuses self-edit.
- **OpExitLoop_v0** (11,677 B), **OpWire_v1** (11,149 B), **OpWireInd_v0** (11,388 B): each now has
  an `error out` indicator (donor-copied from OpExitLoop via `copy_into`) branched onto its last
  chain node's `error out`. All three cold-verified ExecState 1, and all three **end-to-end
  tested**: a deliberate bad terminal name now returns `error 5001: Get Outputs.vi` through
  `gscript._err()` instead of being swallowed by the Clear Errors sinks.
- `gscript.wire()` / `exit_loop()` / `wire_indicators()` now read `_err` after every run and raise
  the REAL error; count checks stay as backup.
- **New rule learned: a running Op cannot edit its own .vi — silent no-op.** OpWireInd_v0's own
  indicator had to be wired by a file-copy of the op driving the original. Guard added in the
  wrapper; fact recorded in the skill.
- Cleanup done: `SCRATCH_wireind.vi` and `SCRATCH_opb.vi` created and deleted same session; Move
  example windows closed; skill updated with the Wire Indicators contract, the self-edit rule and
  the `-Action wire` gesture recommendation.

## (superseded mid-build checkpoint, same day)

**Design changed from the OpWireTerm recipe below, for the better.** Recon found erdosmiller
**`Wire Indicators.vi`** (controls: `Diagram in/out`, `Outputs` = array of source-terminal refnums,
element name "Wire Source"; `Indicator Names` = string array; full error pair) — it wires node
outputs to indicators in one call, so **no CCW, no Index Array**. Facts verified this session:
CCW is the internal wiring primitive of the proven VIs (Wire Inputs/Create For Loop/Exit Loop
byte-reference it); Wire Indicators' only subVI dep is `Error Cluster From Error Code.vi`;
**TopLevelDiagram inherits Diagram** (NI docs: generic/gobject/abstractdiagram/diagram/
topleveldiagram), so one `Diagram` cast constant covers top-level and structure diagrams.

**Recipe in flight:** `OpWireInd_v0.vi` = copy of OpWire_v1 (9,953 B) → delete `Wire Inputs.vi`
by label → drop `Wire Indicators.vi` → scripted wires (GO1.Outputs→WI.Outputs, TMSC2→WI.Diagram
in, error chain into ClearErr2) → ONE GUI step: retarget TMSC2 class constant `Node`→`Diagram` →
save. `Indicator Names` left unwired first (hypothesis: names default to source terminal names) —
**disproved**: it is a required input; the Error List named it in one look, and the `Names 2` →
`Indicator Names` wire was added with `-Action wire`.

## The superseded OpWireTerm_v0 plan (never built — Wire Indicators made it unnecessary)

Build `OpWireTerm_v0` — wire a node's output to a *front-panel terminal*, which the fleet could
not do. `OpWire_v1` uses `Wire Inputs.vi`, which only accepts a **Node**; a control or indicator's
diagram terminal is a **ControlTerminal**. The candidate primitive:
`Conditionally Connect Wire.vi` (erdosmiller) — inputs `Terminal in`, `Wire Source`,
`error in (no error)`; outputs `Terminal out`, `error out` (connector pane read off its own front
panel 2026-08-29). Recipe: copy `OpWire_v1` → delete `Wire Inputs.vi` by label → drop CCW →
retarget the second class constant `Node` → `Terminal` → wire `Get Outputs` element → `Wire
Source` and the cast → `Terminal in` → save; an `Index Array` may be needed for element 0.

## Resume-here block, morning 2026-08-29 (OpExitLoop_v0 done)

State on disk then: `OpExitLoop_v0.vi` works — creates auto-indexed output tunnels; 10,493 B
before the indicator copy; an unwired `error out` indicator (uid 613) added afterwards. Live test:
3 tunnels + 3 wires in 0.26 s. Fleet: OpWire_v1, OpMoveByLabel_v0, OpDeleteByLabel_v0, OpReport_v3,
OpForLoop_v0, OpSubVI_v1. `gscript.py`: every COM call through `_invoke()` (watchdog + hard cap);
helpers `exit_loop`, `copy_into`, `delete_by_label`, `move_by_label`, `remove_bad_wires`,
`loop_diagram`, `open_panel`/`close_panel`, `ensure_move_files_pristine`. `lv_stallcheck.ps1` +
settings hook = session-level stall detector. Move-example files pristine (Source 4,656 B, Target
4,300 B, `.ORIG.bak` beside each; Target had silently grown to 5,548 B because `move_by_label`
restored only the source — restored from NI's own examples copy, and `ensure_move_files_pristine()`
now guards BOTH files).

**2026-08-29 morning: `OpExitLoop_v0.vi` BUILT and SAVED (10,493 B; 28 wires, 7 subVIs,
ExecState 1, cold reload verified).** Structure: the OpWire_v1 skeleton (Wire Inputs deleted) +
`Exit For Loop.vi` at (875,451) + a second `Get Outputs.vi` (GO2) at (790,360) whose empty `Names`
(wired from the idle `Names 2` control) makes its `Outputs` an **empty array — the value EFL's
required `Shift Registers` input needs** (no shift registers = parallelism stays legal). Error
chain: TMSC_bot→ClearErr1 (pre-existing), GO1→GO2→EFL→ClearErr2.

**LIVE-TESTED and WRAPPED.** Against a scratch P=4 loop with the bead kernel inside: 3 tunnels +
3 wires in 0.26 s, and a 12× zoom of the loop border showed all three drawn with the
hollow-bracket glyph = AUTO-INDEXED — so `Loop Terminal Types` needs no wiring; the default is
already right. Use `gscript.exit_loop(target, node_index, output_names, diagram_index)`.

**The bead kernel exposes THREE outputs on its connector pane, not four:** `X pos 1`, `Y pos 1`,
`Z pos 1`. `cal image slice, bead 1` is a front-panel indicator only — probing proved it absent.
Including it made `Get Outputs` raise 5001, which OpExitLoop's Clear Errors sinks swallowed, so
the op returned cleanly having done nothing. That is the cost of the sinks: `exit_loop()` counts
the created tunnels and raises rather than trusting a clean return. The probe that settles such
questions: drive the OLD sink-less `OpWire_v0` with the candidate name and an EMPTY destination
array — a missing name raises a dialog the watchdog converts into an exception.

Debug lessons burned in on the way (all in the skill too): the Error List (View ▸ Error List)
names the exact required-input failure — read it instead of guessing; a wire gesture left pending
(rubber-band) blocks all COM until Esc; hovering a terminal draws diamond markers AND a tooltip
with the terminal's name — the reliable way to hit a 3-px hot zone on an icon-only subVI (GO2's
reported position (790,360) vs its visible icon at (800,391) differ, so trust the hover, not the
report, for GUI clicks).

## Pause context, 2026-08-28 late (mid-OpExitLoop build)

Where the work stopped: building `OpExitLoop_v0.vi`. Done and saved: the `Wire Inputs` node
deleted (SubVI 6→5), broken wires cleaned, ExecState 1 — a clean skeleton of 21 wires. Done in
memory but NOT saved: `Exit For Loop.vi` dropped at (875,451), second class constant retargeted
`Node` → `Diagram`. The open problem then: wiring `TMSC_bot → EFL['Diagram in']` and
`GO['Outputs'] → EFL['Outputs']` created wires but at least one came out broken (ExecState 0);
plan was to add the two wires one at a time from the clean skeleton. (Resolved next morning — see
above.) Untidy but harmless: LabVIEW showed editor windows for scratch VIs deleted from disk
(`KERNEL_regress`, `CONTAIN_scratch`, `CONTAIN_multi_scratch`); a restart clears them — ask the
user first.

## Peer-status corrections (2026-08-28) — quota false positive, and how to check codex quota

The earlier "codex hit its quota" note was WRONG — a false positive in `peer.ps1`. Its QUOTA regex
matched a bare `429` inside codex's *answer* (a LabVIEW method-ID table, `Transaction:Redo | 429`),
so a complete and correct reply was thrown away and codex was benched while healthy. Two fixes:
quota patterns now require their own context (`quota exceeded`, `HTTP 429`, …) and are matched
against the **envelope, not the answer body**; and a QUOTA verdict is confirmed by a ~6 s liveness
probe before any agent is benched.

How to check codex's remaining quota (searched 2026-08-28): interactive TUI `/status` shows rate
limits; `/statusline` toggles `five-hour-limit`/`weekly-limit` items into the status bar (settings
in `~/.codex/config.toml` under `tui.status_line`). **Headless there is none** — `codex doctor`
reports auth mode only, and `codex exec --json` emits per-turn token counts but no rate-limit
fields (verified). So the automated check stays the liveness probe, and `/status` is the human
one. Community caveat: `/status`, the warning banner and the error state sometimes disagree;
cross-check `chatgpt.com/codex/cloud/settings/analytics` if it matters.

## Superseded item-4 recipe notes (pre-OpExitLoop; kept for lineage)

Bead kernel terminals (extracted from the VI's own compressed strings): inputs `starting x 1`,
`starting y 1`, `Calibration cluster 1`, `Image`, `cross size`, `cross arm width`, `z step`,
`forget radius`; outputs `X pos 1`, `Y pos 1`, `Z pos 1` (+ `cal image slice, bead 1`, later
proven front-panel-only). `Exit For Loop.vi` real connector pane (read off its front panel
2026-08-28 — there is NO `Indexing` input, contrary to an earlier guess): inputs `Diagram in`,
`Outputs` (array of refnums), `Shift Registers` (array), `Stop Condition`, `Conditional
Terminals` (array), `Loop Terminal Types` (array of a ring including `Last`), `error in (no
error)`; outputs `Diagram out`, `Outputs` (array of OUTER terminals), `Shift Registers`,
`error out`. Tunnel kind is chosen through `Loop Terminal Types` per Example 8's comment; in
practice the default is already auto-indexed, so it needs no wiring.
