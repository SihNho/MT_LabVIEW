# Lean task 9 - p64ready: one offline `p64_abba.py` dry at 150 Hz with the new A150 / B150 / BOBS150 pins (2026-10-15)

## 0. Start condition
- `lean_report_p64p2.md:239` RESULT: `"p64p2": "PASS"`, wrapper `1419d4c679bd2e68d4962e0ff3ad39d1`, a150 `65b409a8c44f9140b26f70135fb89b99`,
  b150 `d3953cd6e96cc225ac0ed3f8ec3eaca0`, bobs150 `35e7e973c93d1aa56bd6344fab1db8c1` - all four as the task names. **Met.**
- Review `lean_review_p64p2_20261015_014711-c1.md`: VERDICT PASS, `NEXT: p64ready` (:11), offline only (:12), acceptance from the
  DRY slot lines (:13); user_needed (:27) "Offline p64ready is not held."
- `tools/bench/motor_session.json` exists (Glob); `tools/bench/lean_bench/STOP` does not exist (Glob: no match).
- `tasklist | grep -ic labview` -> **0** at ~02:57 (before anything).
- `p64ready_md5.py start` (02:57:41) -> `PINS ALL MATCH` (section 5).

## 1. Predictions (written before the dry)
- Slots 1-4 (A A150, B B150, B B150, A A150): `md5 == pin` and `-> would start`.
- Slot 5 (O BOBS150): `md5 == pin` and `WOULD BE REFUSED: ['(c) the pick log ...\out_latest2\picklog_w100.txt exists (1475 lines) ...']`
  - the same refusal as the 90 Hz dry (`lean_report_p64p3.md:19`). No (b): `obs\getbuff_first.txt` absent (md5_start: exists false;
  `obs\configgrab_rate150.txt` exists false too). No stop / session / rig / pin / (a) reason in any slot.
- Gates `D slot1..5 ... pin read` PASS 5/0; `DRY nothing launched` printed; RESULT status PASS 5/0.
- LabVIEW count 0 before and after; every input md5 start = end.

## 2. Motor session start log (read only; no motor_gate call by this session)
Newest `tools/bench/lean_bench/motor_session_start_p64ready_20261015_025651.log`, last lines:
```
LIMITS SL X=-3.847494 Y=-4.774393 SU X=0.152497 Y=-0.774402
position after (must be unchanged): X=-52899 Y=-41518
RESULT: controller limits set (mode limits-set)
ASI : ASI controller limits match the file (SL {'X': -3.8475, 'Y': -4.7744} / SU {'X': 0.1525, 'Y': -0.7744} mm, tol 0.001) (sender code=0)
SESSION START OK -> G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_lean\tools\bench\motor_session.json
RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[]}
```
PI: `REFERENCED at 0; verify OK (attempt 1/3)`, limits TMN 0 / TMX 39. **ASI XY readback X=-52899 Y=-41518 == p64p2 retry 1's
-52899 / -41518** (unchanged).

## 3. The dry, run ONCE (log `tools/bench/lean_bench/out_p64/p64ready/dry150.log`, BGRUN START 02:58:05, `BGRUN END rc=0 after 2s`)
Command as run (Bash tool, `run_in_background`):
```
py tools/bgrun.py --max-min 3 --log tools/bench/lean_bench/out_p64/p64ready/dry150.log -- py -u tools/bench/lean_bench/p64_abba.py --a-src "C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\D1_s1_p64A150_20261015_015820.vi" --a-md5 65b409a8c44f9140b26f70135fb89b99 --b-src "C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\D1_ring_p64B150_20261015_015820.vi" --b-md5 d3953cd6e96cc225ac0ed3f8ec3eaca0 --o-src "C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\bench\lean\D1_ring_p64Bobs150_20261015_015820.vi" --o-md5 35e7e973c93d1aa56bd6344fab1db8c1 --hz 150 --run-s 120 --order ABBAO
```
No `--live`, no `--fracs-json`. (A first submission of the same command in the foreground with a 60 s timeout was BLOCKED by
the guard hook before it started - section 6; the dry itself ran exactly once.)

**The five DRY slot lines, verbatim:**
```
DRY slot 1 A D1_s1_p64A150_20261015_015820.vi md5=65b409a8c44f9140b26f70135fb89b99 pin=65b409a8c44f9140b26f70135fb89b99 -> would start
DRY slot 2 B D1_ring_p64B150_20261015_015820.vi md5=d3953cd6e96cc225ac0ed3f8ec3eaca0 pin=d3953cd6e96cc225ac0ed3f8ec3eaca0 -> would start
DRY slot 3 B D1_ring_p64B150_20261015_015820.vi md5=d3953cd6e96cc225ac0ed3f8ec3eaca0 pin=d3953cd6e96cc225ac0ed3f8ec3eaca0 -> would start
DRY slot 4 A D1_s1_p64A150_20261015_015820.vi md5=65b409a8c44f9140b26f70135fb89b99 pin=65b409a8c44f9140b26f70135fb89b99 -> would start
DRY slot 5 O D1_ring_p64Bobs150_20261015_015820.vi md5=35e7e973c93d1aa56bd6344fab1db8c1 pin=35e7e973c93d1aa56bd6344fab1db8c1 -> WOULD BE REFUSED: ["(c) the pick log G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_lean\\tools\\bench\\lean_bench\\out_latest2\\picklog_w100.txt exists (1475 lines) - not moved aside into its own leg's folder"]
```
| slot | arm | file | actual md5 | pin (task table) | equal | outcome |
|---|---|---|---|---|---|---|
| 1 | A | A150 | 65b409a8c44f9140b26f70135fb89b99 | 65b409a8c44f9140b26f70135fb89b99 | yes | would start |
| 2 | B | B150 | d3953cd6e96cc225ac0ed3f8ec3eaca0 | d3953cd6e96cc225ac0ed3f8ec3eaca0 | yes | would start |
| 3 | B | B150 | d3953cd6e96cc225ac0ed3f8ec3eaca0 | d3953cd6e96cc225ac0ed3f8ec3eaca0 | yes | would start |
| 4 | A | A150 | 65b409a8c44f9140b26f70135fb89b99 | 65b409a8c44f9140b26f70135fb89b99 | yes | would start |
| 5 | O | BOBS150 | 35e7e973c93d1aa56bd6344fab1db8c1 | 35e7e973c93d1aa56bd6344fab1db8c1 | yes | refused, ONLY reason (c) |

Slot 5's (c) file: `out_latest2\picklog_w100.txt`, 1475 lines, md5 **9a6cc2e3491afa481fcf5e0936f42945** (= p64p3 :104; read by
`p64ready_md5.py`, start and end). No (b) (`obs\getbuff_first.txt` absent), no stop / session / rig / pin / (a) reason in any slot.
The wrapper (1419d4c6) is not a slot file; it is called by A150 / B150 / BOBS150 and pinned separately (section 5, match).

```
DRY nothing launched; real paths: {"obs_dir": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\bench\\lean\\obs", "picklog": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_lean\\tools\\bench\\lean_bench\\out_latest2\\picklog_w100.txt", "stop": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_lean\\tools\\bench\\lean_bench\\STOP", "session": "G:\\Codes\\LabVIEW_Codes\\MinLab\\zz_LabView VI\\AAA_UNIST\\2. Tracking\\V6_lean\\tools\\bench\\motor_session.json"}
GATE D slot1 A pin read                                                               PASS
GATE D slot2 B pin read                                                               PASS
GATE D slot3 B pin read                                                               PASS
GATE D slot4 A pin read                                                               PASS
GATE D slot5 O pin read                                                               PASS
RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":5,"fail":0},"first_fail":null,"artefacts":[]}
```
The dry wrote no `out_p64/abba_150_*` folder (Glob: none; the dry branch `p64_abba.py:299-306` creates nothing).

## 4. Predictions vs results
| prediction (section 1) | result |
|---|---|
| slots 1-4 md5 == pin, would start | **as predicted** |
| slot 5 md5 == pin, refused by (c) only, pick log 1475 lines | **as predicted** (same refusal as the 90 Hz dry, p64p3 :19) |
| no (b); no stop / session / rig / pin / (a) | **as predicted** |
| gates D slot1..5 PASS 5/0; DRY nothing launched | **as predicted** |
| LabVIEW 0 before / after; md5 start = end | **as predicted** (section 5) |

## 5. LabVIEW and md5
- `tasklist | grep -ic labview` -> **0** before (~02:57) and **0** after (02:58:34).
- `p64ready_md5.py` (new, read-only; writes only `out_p64/p64ready/md5_start.json` 02:57:41 and `md5_end.json` 02:58:33):
  `PINS ALL MATCH` at start and end; **`DIFF start vs end: EQUAL 14 / 14`**. Pinned: wrapper 1419d4c6, A150 65b409a8,
  B150 d3953cd6, BOBS150 35e7e973, GetBuffFirst 4cd87cb4, picklog_w100 9a6cc2e3 (1475 lines), `.icd` 2ea8512c (all = the task's
  pins); `p64_abba.py` 90dba5ca, `p64_leg.py` 13c0be9e, `p64_own.py` 58abc8c3, `p64_sum.py` 4f8f115c, `drive_legguard.py` 741eeed0
  (start = end); `obs\getbuff_first.txt` and `obs\configgrab_rate150.txt` absent at start and end.

## 6. Approval prompts / hook refusals (first message verbatim)
- Permission prompt (first, during reading, not approved; I re-did the reads with the Glob / Read tools):
  `This Bash command contains multiple operations. The following parts require approval: ls ../../bench/lean_bench/*review*p64p2*, find .. -name "lean_review_p64p2_20261015_014711-c1.md"`
  (and a second compound read: `Contains shell syntax (string) that cannot be statically analyzed`).
- Hook refusal (first submission of the dry, nothing ran):
  `PreToolUse:Bash hook error: [py ".../tools/hooks/guard_lean.py"]: BLOCKED by guard_lean: a LabVIEW-touching command needs run_in_background (bgrun) or a timeout <= 30 s (got 60000)`
  -> re-submitted the identical command with `run_in_background`, which is the form the task itself names ("backgrounded");
  no guard variable set, nothing else changed.

## 7. What the rig day must do about slot 5
The O leg will be refused until `out_latest2\picklog_w100.txt` (1475 lines, md5 9a6cc2e3, from the W100OBS leg) is moved
aside. The existing explicit step `py tools/bench/lean_bench/p64_abba.py --move-stale --to <leg folder>` moves it (never
deletes) into its own leg's folder (e.g. the W100OBS leg folder); when to do that and into which folder is the user's / the rig
task's decision - **not done here**. `obs\getbuff_first.txt` is absent, so (b) needs nothing today; the rig task must re-run this
dry first (review :18) because a 90 Hz O leg run before the 150 Hz O leg writes a new pick log and wrapper file, which the O leg
moves into its own folder after it (`p64_abba.py:144-147`).

## 8. Notes, safety, files
- `user_notes.md` and the task do not conflict here (sample R, no minimum N, program first: nothing queued, no pull test, no
  Jev work).
- Acceptance #1 of 2026-10-13: no rows saved, no VI changed; the dry confirms the files the rig day will launch are exactly the
  p64p2 r1 copies whose edge diff left column 0's formation unchanged (`lean_report_p64p2.md:144-146`) - md5 == pin for all.
- Motors: no `motor_gate`, stage, PI or ASI command by this session; the start log was only read. No LabVIEW, camera or VI run.
- Not edited: `p64_abba.py` or any P-3 script, `lean_md5.py`, any .vi, `tools/hooks/**`, `motor_gate.py`, `motor_limits.json`,
  `CLAUDE.md`, the `.icd`. Nothing moved or deleted. Nothing committed. No rig / bead / pull / Jev task queued.
- New files: `tools/bench/lean_bench/p64ready_md5.py`, `out_p64/p64ready/{dry150.log, md5_start.json, md5_end.json}`, this report.

## 9. Verdict
**p64ready: PASS.** All five pins match; slots 1-4 would start; slot 5 refused only by (c), the pick log
`out_latest2\picklog_w100.txt` (1475 lines, md5 9a6cc2e3); LabVIEW 0 before and after; md5 start = end (14 / 14).
For the user (unchanged from the review): before any rig / bead run, say when the reference beads are ready and confirm the ASI
XY X=-52899 Y=-41518 (read again at this cycle's start) was your joystick.

RESULT {"p64ready": "PASS", "hz": 150, "slots_would_start": 4, "slot5": "refused (c)", "pins_match": true, "md5_equal": true, "minutes": 3}
