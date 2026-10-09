---
card: 155-a2-1
status: current
date: 2026-10-09
---
# Brief 155-a2-1 - P5-1b PLAN on the REAL P5-1a graph, frame wires addressed `#30914` (PD378(b)); OFFLINE, LabVIEW 0, NOT launched

This is `tools/bench/cards/brief_154-a4-1.md` again (read it first; it names every maker, input and report line) with the
changes below. The tool gap that refused it is closed by card 155-a1-1 (`tools/bench/diag_c155_a1_1_facts.md`): stagexec
`53e17623`, stagesim `eb99c6ba` now address a BASE case's frames as `frame: "#<diagram uid>"`, measured order
(Case #30726 = [30914, 30922], False = `#30914`), and compile the SR-face -> case-tunnel link on a base case as
register_end_case_border (R1/R2) and the frame wires as `case_frame_wire`.

## Changes against brief_154-a4-1.md
1. **Pins.** stagexec 53e17623, stagesim eb99c6ba (NOT 1bab9cf9 / 78b8d5a1); stagekit aec03c6c, stage_prerun 9decb20f,
   vigraph a7eb58c7, addrcheck 207beb0d, gscript 1a80236e unchanged. No stage-tool or hook edit in this card.
2. **Makers.** Start from `prep_c154_a4_1_mk.py` e65b41d3 (its MAP PASS is the symbol -> real uid table, log
   `prep_c154_a4_1_mk.log:7-15`). Make `prep_c155_a2_1_*` with ONLY these differences: pins above, and **the compile must see the
   base**: the OPEN of 155-a1-1 is that a compile of `dict(TOP, actions=...)` with no base keeps the old plain-`tunnel` shape
   (`prep_c154_a4_1_mk.py:158`). Pass the base (`plan['base']` / `finalized.base`, or `owners=` read from graph bd67a511 by the
   stagexec helper `plan_base_owners`, `stagexec.py:593-652`) in every compile / replay / dry call. Call the existing functions;
   do not re-implement the owner read (`docs/script-writing.md` rules 1, 4). Any block you find copied across the
   `prep_c154_*` makers goes into the facts file as `OPEN:` with file:line; do not extract it in this card.
3. **Rows.** Actions 21 (`w_false_pass`) and 32 (`w_q_false`) carry `frame: "#30914"`, the False frame of Case #30726 (Enqueue
   sits on `#30922`). The frame uid comes from the graph / the 155-a1-1 measurement, not retyped; quote the check. Every other
   field is as in brief_154-a4-1 (field for field from `plan_ring_p5s01_in.json` fabc4b9c actions 21..32).
4. **Expected compile** (155-a1-1 A1): case_frame_wire, create, connect, add_sr, connect, connect_term_uid x2
   (register_end_case_border, case 30726), case_frame_wire = P5-1 ops 15..22, i.e. 8 ops for 12 actions. A different shape is a
   RETURN with the op list.
5. **Predicted Error List vs P5-1a base 47** (PD378(b)): `Tunnel: Missing assignment to tunnel` -1 and the Enqueue 'queue'
   unwired item -1, both closed by this step's wires; per class, BOTH elrule totals, non-gating (quote the P5-1a offsets:
   input +1, tunnel +1; `archive/peer/2026-10-09-c154-a3-3b-el47.md:55-59`).
6. **Everything else** as brief_154-a4-1: cut by X10 <= 680 from the adopted P5-1a start (`x10_start(2482fe7b)`), pass A and
   REALSIM replay 0 PROVISIONAL, pred (E1, D/TD/PB by position key), licence by script, sink gate, X11, the two recipes
   (`stage_d1_ring_p5s01b.py` + `_scratch.py`, copies of the P5-1a pair ONLY in: names, pins, plan path, base VI path / md5,
   output name; if the shared stagekit already offers a call that replaces a block of the pair, call it and say so), dry +
   prerun PASS on final bytes, X10 / X17 / X14 / `--scratch-required` rc / `--check-launch` quoted, prior-art review
   ANSWERED (base-case addressing is new: no PROVEN-PATTERN waiver unless the gate itself grants it - quote its line),
   invariants md5 before = after (adopt `prep_c154_a4_1_inv.py` 5430e942 as the base; add stagexec 53e17623, stagesim eb99c6ba,
   the 155-a1-1 files). NOT launched.
7. **Names** unchanged from brief_154-a4-1: plan `plan_ring_p5s01b.json`, `_pred.json`, `_licence.json`, recipes above, sim dir
   `tools/bench/sim/ring_p5s01b/**`, saved-file name `D1_ring_p5s01b_<ts>.vi` (the end of P5-1; adopted later as
   `D1_ring_p5s01_<ts>.vi` per the purpose).

## Return conditions
As brief_154-a4-1, plus: the compile op list differs from item 4; pass A / REALSIM shows a PROVISIONAL step or a refusal; the
prior-art verdict is not releasable; a protected md5 moved; a second failure at the same place.

## Report `tools/bench/diag_c155_a2_1_facts.md` (<= 45 lines)
As brief_154-a4-1 plus: op list vs item 4, frame uid check, pins, duplicate blocks seen (OPEN). Facts only.
