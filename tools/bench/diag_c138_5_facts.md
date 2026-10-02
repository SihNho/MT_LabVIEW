---
type: facts
status: current
date: 2026-10-02
tags: [card-138-5, stop-mode, read-only-op]
---
# Card 138-5: reading a While loop's stop mode and a Boolean's mechanical action (read-only ops)

Run: `tools/bench/build_opstopmode_v0.py` -> `tools/bench/build_opstopmode_v0.log` (BGRUN END rc=0 after 356 s, 39 pass / 0 fail, `:141-143`).
Facts JSON: `tools/bench/diag_c138_5_facts.json`. Op labels: `tools/bench/diag_c138_5_oplabels.json`.
Id source: `archive/peer/2026-10-02-c138-5-mechaction.md` (claude/hypothesis fact question, ANSWERED, $1.34, labviewwiki).

## Property ids (measured on this machine: the data terminal was censused)
| class.property | id | data terminal short name | evidence |
|---|---|---|---|
| WhileLoop.Stop If True? | 6362C01 | `StopIfTrue` (Boolean) | build_opstopmode_v0.log:19 |
| Boolean.Mechanical Action | 6333808 | `MechAction` (integer 0..5) | build_opstopmode_v0.log:46 |
| Traverse for GObjects `Traverse Target` | ring input | 0 = front panel, 1 = block diagram | :77 (1 on an FP Boolean -> error 1055, uid 0) |

## Op VIs (claudeDev, saved by script, ExecState 1 cold)
- `OpStopMode_v0.vi` md5 87e43f4b2e514ea16aa30dcdc2244f6e (13,417 B): donor OpWhileCast_v0, WhileLoop TMSC #683 branched into new
  PN #657 `WhileLoop[Stop If True?]`. Inputs `vi path`, `Class Name`='WhileLoop', `index`; outputs `Stop If True?`, `error out 3`,
  loop uid echo `UID` (:19-23, :63).
- `OpStopModeB_v0.vi` md5 0ec05ebdad1a92255d7f861964d6af7c (12,302 B): donor OpSetIndexMode_v0, TMSC #683 retargeted by a Boolean seed
  into PN #118 `Boolean[Mechanical Action]` + GObject UID echo; `Traverse Target` is a control (set 0 for panel objects). Inputs
  `vi path`, `vi path 2`, `Class Name`='Boolean', `index`, `index 2`=0, `Traverse Target`=0; outputs `Mechanical Action`, `error out 2`,
  `UID`, `error out 3` (:46-47, :60-62, :64).

## Scratch check on known values (EMPTY_v0 copy: one While loop #43, one Boolean control #157)
- A fresh While loop reads Stop If True? = True (LabVIEW's default "Stop if True") (:72).
- A scratch-only writer copy (never saved, deleted) wrote False -> read False, True -> read True. So True = Stop if True,
  False = Continue if True (:73-74).
- Mechanical Action written 0,1,2,3,4,5 -> each read back equal (:78-83); the fresh control read 0 (:75).
- Past-the-end index -> error 1055 and echo 0 on both ops (:84).

## Bed byte copy (D1_ring_p3b2b_20261002_130007.vi, md5 395118775a52bc90073f4449b99f899d before and after, :4, :140)
- **#10170 Stop If True? = True (Stop if True)**, echo 10170, no error (:88). All six While loops of the bed read True:
  23041, 10170, 23032, 25380, 637, 15173 (:87).
- **`stop (end)` #7 Mechanical Action = 4**, no error (:93-94). `stop (end) 2` #19587 = 4; `Done Picking \nBeads?` #11819 = 4 (:92).
- 30 front-panel Booleans scanned (index 0..29, :91-92); values seen: 0 (switch-type, e.g. Auto-Focus, Auto-Reset, Z/dZ,
  continue tracking), 1 (e.g. Send, HOME, Stop Trans, Start Cycles), 4 (the three above).

## Name of the numeric value (CONFIDENCE: inference, not measured)
labviewwiki states 0..5 are the six actions "arranged from top left to bottom right" in the palette, which gives
0 Switch When Pressed, 1 Switch When Released, 2 Switch Until Released, 3 Latch When Pressed, **4 Latch When Released**,
5 Latch Until Released (`archive/peer/2026-10-02-c138-5-mechaction.md`). NI's own table did not render for the peer.
Consistent with: every stop-type button on the bed reads 4, LabVIEW's stock stop button is Latch When Released.
No reader of the enum's text exists in this fleet.

## Hygiene (PD242(b), gscript.hygiene_run, 20 rounds x 100 calls, copy closed without saving each round)
- OpStopMode_v0: 2,000 calls, 0 errors, h_closed max deviation 14, refs delta 0 -> PASS (:95-115).
- OpStopModeB_v0: 2,000 calls, 0 errors, max deviation 1, refs delta 0 -> PASS (:116-136).
- Records: `tools/bench/hygiene_OpStopMode_v0.json`, `tools/bench/hygiene_OpStopModeB_v0.json` (NOT in the default
  `tools/bench/op_hygiene/` folder the `op()` gate reads, which was outside the card's write list; until copied there the two ops
  run only inside `gscript.hygiene_probe`).

## End state
LabVIEW gone (:138); scratch target, two writers and the bed copy deleted (:139); handles 33,968 after restart -> 31,503 at end (:137).
