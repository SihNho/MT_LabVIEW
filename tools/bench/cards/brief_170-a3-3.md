---
card: 170-a3-3
status: current
date: 2026-10-13
---
# Brief 170-a3-3 (assignment 170-3) - offline: the S1-vs-P6 leg-chain driver (PD409(f), PD410(c)/(f), PD411), no LabVIEW, no hardware

Plan: `docs/d1/ring-p6.md` PD409(f), PD410(c)-(f), PD411(c)-(e); facts `tools/bench/p6_replay_facts.md` F5, F6 and X5-X9 (lines ~131-152). This card WRITES the driver the next card will RUN; it runs nothing that touches LabVIEW or a motor
(`flags.labview none`, `hardware none`; self-tests use stored data and stubs only). Read `docs/script-writing.md` first: shared functions are CALLED, never copied.

## The driver: `tools/bench/drive_m8_replay_p6.py`
`py -u tools/bench/drive_m8_replay_p6.py --p6 <replay copy path> [--s1-run-s 120] [--p6-run-s 150] [--picks 15]` runs, in this order:
1. P1 pins: S1 replay copy `claudeDev\replay\D1_s1_replay_20260925_075422.vi` md5 126f84975fca9f6124432a7e4decd0c8; the P6 replay copy's md5 read from `tools/bench/stage_replay_swap_170.json` `copies.p6.md5` (the file card 170-a3-2 writes) and equal to the file on disk;
   `docs/d1/ring-p6.md`-independent. Any mismatch = stop before any leg.
2. S1 leg: one motor_gate session (`py tools/motor_gate.py --session start`, then `--session end`, each verified by READBACK and its output kept in the log; read `tools/motor_gate.py` and `docs/rules/hardware.md` first: how the
   cycle's already-open session (`tools/bench/motor_session.json`) and the leg runner's own `--session start` inside `drive_m8` interact, and write down in the facts which of start/end the driver must call and which `drive_m8` already does;
   the driver must not leave limits set after the last leg and must never skip the PI reference move that start performs). The leg itself is the existing `diag_c104_leg.py --src <vi> --picks N --run-s S --out <dir>` via the leg runner shared with
   `drive_m8_replay_110.py` (`leg()` there, lines ~38-62: VISA precheck `drive_legguard.visa_precheck`, one rerun, LabVIEW-gone wait + taskkill, leg.json facts).
3. Then the P6 leg the same way, `--src` = the P6 replay copy, `--run-s` 150.
4. Per leg report (facts, not gates): tra rows, `Total Lost Frames` (leg.json `facts.lost`), frame-counter delta, files in the run dir with md5 and size, LabVIEW gone (T3), motor session start/end readback lines.
5. Compare ONLY IF S1 lost == 0 and the P6 leg wrote >= 1500 tra rows (else write the numbers and stop: PD409(c)/PD410(c), no compare): `m8b_replay_compare.compare_bc(da, db, 20, out)` / CLI `m8b_replay_compare.py <S1 run dir> <P6 run dir> --slots 20`.
   D = 20 is cited in the driver as `docs/d1/ring-p4b.md:21` (U13, PD411(c)); no graph read. The compare output (MATCH + first miss + drop signature, DISTINCT count, cal outside the F4 field, trans/rot post-init, init inside
   `tools/bench/motor_limits.json` PI/ASI ranges with the rotor "finite" only, every other leg file) is written as-is to `tools/bench/m8b_replay_p6.json`; each item PASS/FAIL stays a FACT: the driver never re-runs a leg or a compare after a FAIL.
   If `m8b_replay_compare` lacks the init-range check or the "every other leg file" listing that PD409(b)/PD411(d) require, add them in `m8b_replay_compare.py` as shared functions with `--selftest` coverage on the stored 110-7 legs (c2efe10d is the accepted base: quote its new md5) and NO change to the accepted checks.

## Shared code, not copies
`leg()` and the LabVIEW-gone wait exist inline in `drive_m8_replay_110.py` (rule 4): extract them into ONE small shared module under `tools/bench/` (e.g. `m8_legs.py`) with a docstring and a self-test, make the new driver call it, leave
`drive_m8_replay_110.py` byte-unchanged (it is the record of what ran) and report its copies in `facts` (file:line). Run `py tools/dupcheck.py` on the new files and quote the result.

## Self-tests (offline, ONE at a time; each under `py tools/bgrun.py --max-min 10 --log <file> -- <cmd>` if it takes more than a few seconds)
- Driver `--selftest`: stubs the leg runner and `motor_gate` calls with the stored 110-7 run dirs (`tools/bench/m8_out/replay_s1_20260927_184651` = leg A and leg B's dir from its leg.json) and asserts: the order start -> leg -> end per leg, the pin stop, the "S1 lost != 0 -> no compare" stop,
  the "< 1500 rows -> no compare" stop, and the compare on the stored dirs (4443 rows, 0 X/Y/Z rows differ, DISTINCT 4443/4443 with --slots 20).
- `m8b_replay_compare.py --selftest --slots 20` still gives its recorded result.
- The driver on `--help`/dry parse returns its usage without touching anything.

## Hygiene
No LabVIEW process started (`tasklist` before and after), no serial/VISA call, no `.vi` opened or written, no hook / stage_prerun / plan-of-record / STATUS / INDEX edit, `memory_model.json` untouched. Facts `tools/bench/diag_c170_a3_3_facts.md` (<= 40 lines, file:line).

## Not in this card
Running a leg, building the P6 replay copy (card 170-a3-2), fp-102. A new unexpected result = RETURN with the facts.
