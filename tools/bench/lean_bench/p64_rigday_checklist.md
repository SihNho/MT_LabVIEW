# P6-4 rig day - one-page checklist (90 Hz day, task p64run90; written by p64p3 2026-10-14, NOT run yet)

Nothing here starts before the user says the beads are ready (`user_notes.md:5`). Sample option R / M / J: the user's answer
to the HOLD in `questions_for_user.md` (p64p3); the steps below are for **R** (reference beads), with the M / J differences
in the last box. Every motor move stays inside the queue's session + v5 G0 (`user_notes.md:3`); rig-state stays **조립**.

## A. At the rig (user)
1. Put the sample in, focus on the bead plane (the z-stack calibration after Done Picking starts from here).
2. Close LabVIEW (the camera has one owner). Say "준비됨" in the chat.

## B. Snapshot -> bead map (session, LabVIEW closed; camera only, nothing moves)
3. `py tools/bench/lean_bench/p64_beadmap.py snap --out tools/bench/lean_bench/out_p64/snap_90_1.tif`, wait ~5 s, again `..._2.tif`.
4. `py tools/bench/lean_bench/p64_beadmap.py find --img ..._1.tif --img2 ..._2.tif --out out_p64/beadmap_90.json --png out_p64/beadmap_90.png`
   - prints **N** = single, round, isolated, non-drifting beads; picks = the N best (max 15) + fixed empty-field fill up to 15.
   - drifting beads (moved > 3 px between the two snapshots) are NOT picked.
5. **User checks the PNG** (green = picked bead, yellow = bead not picked / drifting, blue = rejected spot, red + = fill).
   Pick 1 is the brightest-contrast bead: the VI uses the FIRST click as the reference bead (`project-description.md:21`).
   If the picks look wrong: say so; the session re-runs step 3-4 (or uses the fixed 15 by leaving `--fracs-json` out).

## C. Before the first leg (session)
6. Byte-copy the A source `claudeDev\D1_s1_copy.vi` (3e3d23ce) and the product VI 15c664e3 into `claudeDev\bench\lean\`
   (plan section 1: A90 / B90); BOBS90 = `D1_ring_p64Bobs_20261014_114246.vi` 257fb852 (already there).
7. Move the stale pick log into its own leg's folder (refusal (c) fires until this is done; nothing is deleted):
   `py tools/bench/lean_bench/p64_abba.py --move-stale --to tools/bench/lean_bench/out_latest2/legs/W100OBS_a1`
   (note: `lean_report_latest.md` cites the old path `out_latest2/picklog_w100.txt`).
8. `p64_abba.py ... --order ABBAO` WITHOUT `--live` = dry: every slot must print "would start".

## D. Legs (session; bgrun --material; ~12 min per leg)
9. Smoke S0: `p64_abba.py --order B --run-s 60 --b-src <B90> --b-md5 <m> --fracs-json out_p64/beadmap_90.json --live`.
   Pass = p64_leg L0-L7 all PASS (15 picks registered == 15 panels closed, column 0 strictly increasing, TMX 39), fps within 15 %.
10. Then `--order ABBAO --run-s 120 ... --live` (A90, B90, B90, A90, BOBS90; the SAME bead map for every leg).

## E. A leg is REFUSED (no leg script launched, the loop ends) - what the user / session does
| refusal | meaning | what to do |
|---|---|---|
| (a) a LabVIEW process exists | the previous leg (or someone) left LabVIEW open; a fresh LabVIEW per leg is what makes the wrapper log exactly one line | close LabVIEW (`tasklist` shows none), rerun from the refused slot |
| (b) `claudeDev\bench\lean\obs\getbuff_first.txt` exists | a start value from an earlier load would be read as this leg's | move it into the leg folder that wrote it (`--move-stale --to <that leg folder>`), never delete |
| (c) `out_latest2\picklog_w100.txt` exists | an older pick log would be mixed with this leg's picks | step 7 (or move it into the leg folder that wrote it) |
| stop / session / rig / pin | STOP file, `motor_session.json` missing, rig-state not 조립, a VI md5 changed | stop; tell the user; nothing is retried automatically |
| VISA precheck | `Rotor` / `ASRL5` could not be opened | the ABBA ends (plan 5.3); user checks the ports |
After every leg: LabVIEW gone (waited, then taskkill) - gate T6. OBS leg: the wrapper file must hold exactly 1 line, otherwise
the number check is **NOT RUN** (never PASS); `p64_own.py` result in the leg folder.
Own-pick check (step 2, strict since p64p3 retry 1): saved row k is compared with pick k (the first `rows` picks, no skipping) with
the logged S; only `{0: rows}` passes, picks after the last row are counted. A FAIL reads **"OWN 대응 근거 부족"** = there is no
evidence that every row is its own pick's frame (a +1 offset, or a first / middle pick without a row); it is not called a product
computation error. The day's run then STOPS for the user, with no automatic retry of the leg.

## F. Option M / J differences (only if the user picks them)
- **M** (magnetic beads, magnet not moved): the VI's start-up move to 30 mm comes from the panel control
  `If no: current pos z?` = 30; keeping the magnet at 0 needs a panel-default change on ALL leg copies (A, B, OBS - a new build
  task, new md5 pins) or a driver write before Run (v5 writes no panel parameter today). Not built.
- **J** (Jev picks): step 4's candidate numbers go to Jev as text, Jev answers bead / not-bead per candidate; the user still
  checks the PNG. Not built (design only, report section 7).
