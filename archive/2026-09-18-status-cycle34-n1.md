---
type: archive
status: archived
date: 2026-09-18
cycle: 34
tags: [status, narrative, n1, gpu, tmx, motor-limits]
---

# Cycle-34 STATUS narrative — relocated VERBATIM (CLAUDE.md rule 4)

STATUS.md had reached 114 lines. Nothing here is rewritten: the lock-block lines and OPEN item 55
below are the exact text STATUS.md carried at 2026-09-18 19:1x, moved down one layer by cycle-34
material dispatch C. STATUS.md keeps one line plus a pointer for each. §3 is the only NEW text and
records the judgement session's N1 decision, which is also summarised in STATUS.

## §1 — the lock block's `purpose*` lines, verbatim

```yaml
  purpose_now:   # ✅ **N1 VI-LEVEL IS MEASURED — cycle-34 material dispatch A, 19:04:47-19:08:05, `tools/bench/n1_gpuk_vi_fixture.py` -> `tools/bench/n1_gpuk_vi_fixture.log`, GATES 7/7, `BGRUN END rc=0 after 198s`.** (This dispatch re-owned the cycle-33 dispatch-2 line below, which was written at 18:5x and DIED without ever running — no log existed. Its text is kept verbatim as `purpose_prev_n1:`.) 10,043 frames x 5 beads swept through HARNESS_gpuk.vi in 126 s (12.5 ms/frame incl. COM). **GPU_kernel_v1.vi REPRODUCES THE DLL EXACTLY**: max |dx| 4.131e-06 / |dy| 3.135e-05 / |dz| 1.279e-05 and the single flip (k1679 f1937 bead 4, cpu_idx 26 -> gpu_idx 25, dz -4.667e-03) are the SAME NUMBERS the DLL-level run produced (`tools/bench/n1_gpu_vi_vs_cpu.log`), so the LabVIEW wrapper adds nothing. G4 reproduced gpuk_repeat.log's scalar worst |dev| 2.9253520220e-06 to 1e-12. Good-flag mismatches 0 of 50,215. **THE ACCEPTANCE PICTURE: every exceedance is bead 4 in the TAIL.** Overall vs tolerance: x 10 bead-frames > 1e-6, y 9 > 1e-6, z 0 > 1e-4. But in the window k<10018, i.e. BEFORE the first lost-bead frame, max |dx| 4.857e-07, |dy| 4.677e-07, |dz| 1.279e-05 and **0 exceedances on all three axes** — all 19 sit at k>=10023, bead 4 only, inside the 13 recorded lost-bead rows f11798..f11824. Excluded from the comparison: **13 bead-frames as SKIP** (`state[1][b]` false, or the reference row carries -1.0) **and 1 as FLIP** (GPU chose a different cal-image index), = 14 of 50,215; **50,201 bead-frames were actually compared**, over ALL 10,043 frames (no frame subset). ⚠️ **`gpu_n1_deltas.py` NEVER GATES ON THE TOLERANCE** — `TOL_XY/TOL_Z` (`tools/bench/gpu_n1_deltas.py:52`) only feed the REPORTED `n_exceed`/clustering (`:161-176`, `:207`); its G2 (`:156-158`) asserts reproduction of the earlier log's 4.13e-06 / 3.13e-05 / 1.28e-05 / 1 flip to 3 s.f. **That is why max |dy| 3.13e-05 sat inside a PASSING 8/8 run: the gate threshold, not the frame subset, explains it.** Exclusion rule identical in both scripts (`:152` / `n1_gpuk_vi_fixture.py:195`: VALID = ~SKIP & ~FLIP). HYGIENE: no LabVIEW at start (tasklist), the script's own `lv_restart` gave a fresh instance, **34,136 handles after** (~31,500 fresh baseline, i.e. +2.6k over ~10,043 Run + ~70,000 control calls — flat, not per-call); `g.reset()` ran in the script's `finally`; the instance was left up and was then CLOSED and proved gone (`tools/bench/n1_close_lv.log`, `before: ['23832'] ... after: [] PASS`). md5(ORIGINAL) c39f36e0675339673b707c59f0784fee before AND after; claudeDev only; NO motor, NO ASI, NO serial, NO camera. ⚠️ Getting here needed one peer dispatch: `guard_peer` blocked the measurement on ANOTHER dispatch's log (`tools/bench/tmx_selftest.log` 18:45, `FAIL | no TMX anywhere`); `archive/peer/2026-09-18-tmx-selftest-stale.md` (ANSWERED, claude/hypothesis, 406 s) is disposed and CONFIRMED the expectation is stale but REFUTED "so just re-run it" — see OPEN 55.
  purpose_prev_n1:   # N1 VI-LEVEL: tools/bench/n1_gpuk_vi_fixture.py drives HARNESS_gpuk.vi (hosts GPU_kernel_v1.vi) over all 10,043 fixture frames vs the CPU-kernel reference. claudeDev only; NO original opened, NO motor/ASI/serial/camera. Log tools/bench/n1_gpuk_vi_fixture.log. The DLL-level half (tools/bench/gpu_n1_deltas.py -> tools/bench/n1_gpu_vi_vs_cpu.log) uses NO LabVIEW.
  purpose:   # free since cycle-32 D0 v5 (18:08-18:13): **drive_original_copy_v5.py = 39 pass / 1 fail, BGRUN END rc=1 after 290s** (tools/bench/drive_original_copy_v5.log). **D0's done-when is MET on BOTH legs** - picks, done button, 3 bandpass panels, save dialog, experiment loop, own-control stop, trace file, then the whole cycle again. run1 tra001-000 285,369 B + cal001 171,552 B; run2 tra002-000 285,753 B + cal002 171,552 B, all under tools/bench/d0_out/v5_20260918_180813/. Frame counter ADVANCED (run1 8326->10856 lost=5; run2 8059->10589 lost=3 over 30 s) - it read 0 all through v4. STOP: the VI-Server single write to `stop (end)` + `stop (end) 2` idled it in **1.0 s on BOTH legs, no re-arm, no Abort** (v4's "never consumed" reading was taken in the picking stage and proved nothing). THE FIX: every click point LOCATED on this VI's own panel by `tools/bench/d0_locate.py` - done button box (1155,848)-(1200,876) centre **(1177,862)**, template score 0.00 vs next-best 28.35, evidence crops in tools/bench/d0_evidence_v5/; the inherited v4 point (1114,915) was 63 px left and 53 px below it. Picks verified by the 3 red markers the VI drew (0 -> 3 both legs). Both md5s c39f36e0675339673b707c59f0784fee IDENTICAL before and after; copy never saved, never deleted. 60/60 panel controls RECORDED, none set. Handles 0 -> 61,331 -> 60,548; LabVIEW exited on its own in 6 s. Motors: `--session start` verified TMN 0 / TMX 39 / FRF 1 / POS 0 before; after the run `TMX?=39.00000 TMN?=0 ERR?=0 FRF=1` and **POS?=30.00000 - the VI moved the PI magnet to 30 mm, inside the 0-39 envelope, and the limits held**. The single FAIL, gate 93, is a **PARSER FALSE RED**: `tmx_from` (drive_original_copy_v4.py:240-243) splits `TMX?=1=39.00000` on the first `=` and float("1=39.00000") raises, so it reports None while the very line it read says 39.00000. NOT patched (outside the dispatch's scope).
  prev_purpose_1:   # cycle-30 dispatch 3 (17:25-17:33): drive_original_copy_v4.py 13 pass / 3 fail (17:25-17:33): drive_original_copy_v4.py 13 pass / 3 fail, BGRUN END rc=1 after 471s (tools/bench/drive_original_copy_v4.log). FIRST FAIL = `13 run1.R4 picking loop ended | GUI | FAIL | Count 1 -> 1 after 303s; bandpass present=False; save present=False` — the done click did NOT end the bead-picking loop, so the experiment loop was never entered (frame counter 0 throughout) and R5-R10 + the whole restart leg never ran. Panel geometry IDENTICAL to v3's V6 rect (-6,51,1930,1107 / 1936x1056, delta 0,0), picks [(552,756),(430,640),(690,880)] `Count` 0->1->1->1 (only pick 1 registered). STOP: both stop Booleans written True stayed True with ExecState=2 for 61s single-write + 60s / 30 re-arms — never consumed (= the picking phase does not read them); COM Abort in cleanup returned ExecState 1. ORIGINAL md5 c39f36e0675339673b707c59f0784fee IDENTICAL before and after; COPY md5 c39f36e0675339673b707c59f0784fee IDENTICAL before and after (never saved, never deleted). 60/60 panel controls RECORDED, none set. Handles 0 -> 47,386; LabVIEW exited on its own at the end (tasklist empty). Motors: `--session start` verified TMN 0 / TMX 39 / FRF 1 before the run; the post-run read inside the driver FAILED (COM3/COM4 'access denied' — the VI still owned the ports) and the retry after LabVIEW exited PASSED: `TMX?=1=39.00000 POS?=0.00000 ERR?=0`, ASI SL/SU intact, X=-18473 Y=-27744 (tools/bench/d0v4_tmx_recheck.log).
  prev_purpose:   # cycle-30 dispatch 2 + cycle-24 lock lines RELOCATED VERBATIM -> archive/2026-09-18-status-cycle30-d0.md §1 (that file also holds dispatch 3's full gate table §2, the post-run motor readback §3, the stop measurement §4); cycle-24/23 dispatch lines (incl. the 894/1356 panel-object finding) -> archive/2026-09-18-status-motor-gate-rework.md §3
  motor:     # 2026-09-18 15:37 MOTOR PORTS (no LabVIEW): tools/bench/motor_gate2_live.log, 8/10 gates, five transmits, ASI +-0.2 mm moved and returned, PI did not move (FRF 0 / ERR 5). Controller limits LEFT ON (PI TMN 0 / TMX 39, ASI SL/SU +-2 mm). Ports closed.
# CYCLE 23 lock lines + "where things stand" VERBATIM → archive/2026-09-18-status-cycle23-close.md §1/§2 (§3 = dispatch 3's own facts). CYCLE 22 lock lines RELOCATED VERBATIM → archive/2026-09-18-status-cycle22-close.md §1 (build_opfstunnelterm_v1 RUN 1 gates 12/16 B4 ExecState 0 · diag_fstunnel_orphans 8/8 · the `-Dual` review, both arms now DISPOSED · handles 30,318→30,979 · md5s identical BEFORE AND AFTER · no motor/serial/camera); cycle-21 → …cycle21-wire-semantics.md §8/§9/§9a, cycle-20 → …cycle20-close.md.
```

## §2 — OPEN item 55, verbatim as STATUS.md carried it before this relocation

> 55. 🔴 **`tmx_from` can report a SILENT FALSE GREEN on a motor-limit check — assembled rig, so this outranks D1.** When a `before:` line carries no `TMX?=` token the parser falls through to the `LIMITS` line, which in `limits-set` mode is printed *after* the SPA write — so the gate reports back the value it just wrote and PASSES without ever reading what the controller held after the LabVIEW run. The two lines answer different questions (`before:` = "still 39 after the run"; `LIMITS` = "did we just set 39"). Peer's minimal remedy: return `(None, s)` when a `before:` line exists but has no `TMX?=` token. Preferred remedy is upstream: emit a normalised `PRELIMITS TMN=<n> TMX=<n>` from `tools/motor_send_pi.ps1:52` using its own `Num` parser and read it with an anchored regex. Review: `archive/peer/2026-09-18-tmx-lastfield-parse.md`. NOT built — it alters a motor-limit check on an assembled rig and was outside the dispatch's scope. 🆕 **19:04, SECOND REVIEW, disposed: `archive/peer/2026-09-18-tmx-selftest-stale.md`** (ANSWERED, claude/hypothesis, 406 s), dispatched by cycle-34 dispatch A only because `guard_peer` blocked an unrelated N1 measurement on `tools/bench/tmx_selftest.log`'s 18:45 `FAIL | no TMX anywhere` (14 pass / 1 fail; contract says 16/0). **CONFIRMED:** that expectation IS stale — the file changed after the run (15 cases then, 16 now; the case was relabelled `no TMX anywhere (reports the before: line it read)`), and the failing assertion is the line-TEXT one, not the value (`got=None` == `want=None`). **REFUTED — "so just re-run it":** the peer says the relabelled case now has zero discriminating power, and that the same patch makes `tmx_from` answer `None` for a **send-mode** transcript whose `LIMITS` line is legitimately PRE-write, contradicting `tmx_from`'s own docstring at `drive_original_copy_v4.py:295-299`. 🔴 **JUDGEMENT, unanswered: is `None` the intended answer for a send-mode transcript, or must step 4 keep answering from `LIMITS`?** Not patched and the self-test not re-run by dispatch A — it is another dispatch's parser and a motor-limit call on an assembled rig. 🆕 **2026-09-18 19:03 (cycle-34 dispatch B): the parser + self-test are now GREEN — `tools/bench/tmx_selftest2.log:18` `SELFTEST tmx_from: 16 pass / 0 fail`, `BGRUN END rc=0`.** The 18:45 red was a fixture/implementation edit out of step: cycle 33 patched the case at 18:46:07, 19 s after its only run, and died before re-running; this dispatch changed NO code, only re-ran it. 🔴 **JUDGEMENT STILL OPEN — the hypothesis peer REFUTES the contract** (`archive/peer/2026-09-18-tmx-selftest-contract.md`, ANSWERED, opus/max, $3.04): `motor_send_pi.ps1:111` (`--mode send`) prints a `before:` line with **no `TMX?=` token** (verified by grep — only `:58`, the limits-set path, emits `TMX?=`), so rule 3 fires on send-mode transcripts and suppresses the one genuinely PRE-transmit `LIMITS` line, while in limits-set mode `:58` always emits a literal `TMX?=` so rule 3 can never fire where the hazard lives. Peer also notes nothing parses the second tuple element (gate is value-only, `:1012`), so the reported-line change is cosmetic. NOT acted on — accepting or rejecting this is the judgement session's call.

## §3 — cycle-34 dispatch C: the peer's discriminating test, RUN

The judgement session accepted the `tmx-selftest-contract` refutation **as a hypothesis, not as grounds
to patch**, and dispatched its own cheapest discriminating test
(`archive/peer/2026-09-18-tmx-selftest-contract.md:102-113`). Throwaway script
`tools/bench/tmx_sendmode_probe.py`, created and deleted in the same operation; the logs are the record.

| run | log | outcome |
|---|---|---|
| 1 | `tools/bench/tmx_sendmode_probe.log` | 2 pass / 1 fail, `BGRUN END rc=1 after 0s` — **my own gate P2 was mis-specified**, not a parser fault: the control fixture carried a `PRELIMITS` line, which rule 1 (`drive_original_copy_v4.py:284`) outranks, so the value was 39.0 as predicted but it came off `PRELIMITS`, not off the `before:` line I had named |
| 2 | `tools/bench/tmx_sendmode_probe2.log` | 4 pass / 0 fail, `BGRUN END rc=0 after 0s`, with a fourth fixture (d) added as the real rule-2 control |

Returned `(value, line)`, verbatim from run 2:

```
RESULT a | value=None | line='before: POS?=1=30.00000  SVO?=1  FRF?=1  VEL?=1.0  ERR?=0'
RESULT b | value=39.0 | line='PRELIMITS TMN=0 TMX=39'
RESULT c | value=39.0 | line='PRELIMITS TMN=0 TMX=39'
RESULT d | value=39.0 | line='before: POS?=1=30.00000 TMN?=1=0.00000 TMX?=1=39.00000 ERR?=0'
```

(a) is the send-mode transcript the peer specified — `LIMITS` at `motor_send_pi.ps1:105` (genuinely
pre-transmit) followed by the `:111` `before:` line, which carries no `TMX?=` token. Per the peer's own
criterion at `:113`, **`None` CONFIRMS the refutation**: rule 3 pre-empts rule 4, so rule 4 is dead code
for the exact transcript class its docstring (`:295-299`) was written for. NOT patched — that is the
judgement session's call.

### Is the regression LIVE or THEORETICAL? — every call site, cycle-34 dispatch C

`grep` over the whole project for `tmx_from` / `parse_motor` / `prelimits_from` (`*.py`):

| call site | source of the text it parses | mode it can receive |
|---|---|---|
| `tools/bench/drive_original_copy_v4.py:1006` (`tmx_from`), `:848` + `:1007` (`parse_motor`) | `motor_gate()` at `drive_original_copy_v4.py:204-218` = `py tools/motor_gate.py --session start` | **limits-set ONLY** (`tools/motor_gate.py:375` `pi_call("limits-set", …)`) |
| `tools/bench/drive_original_copy_v5.py:656` (`tmx_from`), `:501` + `:657` (`parse_motor`) | `d4.motor_gate(...)`, the same wrapper | **limits-set ONLY** |
| `tools/bench/diag_d0_pickloop_liveness.py:433` (`tmx_from`), `:210` (`parse_motor`) | `v4.motor_gate(...)`, the same wrapper | **limits-set ONLY** |
| `tools/bench/drive_original_copy_v4.py:415` (`tmx_from`) | `selftest_tmx()` literals | test fixtures, no transcript |
| `tools/bench/tmx_fallthrough_probe.py:68` (`tmx_from`) | literals | test fixtures, no transcript |

The two PI send-mode (`--execute`) users in the fleet, `tools/bench/motor_gate2_live.py` and
`tools/bench/asi_xy_check.py:20-21`, **never call `tmx_from` or `parse_motor`**. So today the
regression is **theoretical, and latent**: no production path can hand `tmx_from` a send-mode
transcript, and if one ever does, the answer is `None` → the value-only gate `tmx == 39.0`
(`drive_original_copy_v4.py:1012`) fails — a false RED, the safe direction, never a false green.

## §5 — STATUS.md's "Where things stand" + D0 banner, verbatim before the cycle-34 trim

```
🎉 **D0 IS DELIVERED** (cycle 31, 18:08–18:13; `drive_original_copy_v5.py` **39 pass / 1 fail**, both legs, original
md5 unchanged, the VI moved the PI magnet to 30 mm inside 0–39 and the limits held) — banner text + the user's live
observation RELOCATED VERBATIM → `archive/2026-09-18-status-cycle31-d0-delivered.md` **§5** (facts §1–§4, and read
**§4** before the first D1 click); earlier banners → `…-cycle26-stop.md`.
🆕 **USER RULE 17:5x, now `docs/cycle27-plan.md` Pre-decided 9 — EVERY GUI action is capture → locate → act →
capture → confirm; derived or remembered coordinates are NEVER clicked blind.** It turned v4's 13/3 into v5's 39/1.

## Where things stand — VERBATIM in `archive/2026-09-18-status-cycle22-close.md` §2 (cycle-20 §1–§5 in `…cycle20-close.md`; cycle-21 §9/§9a/§10 in `…cycle21-wire-semantics.md`; cycle 19 in `…cycle19-flatseq.md`)
✅ **TUNNEL OPS BUILT + FUNCTIONALLY VERIFIED** (cycle-24 firefighter, 38/38, rc=0): `OpFsTunnelTerm_v0.vi` +
`OpFsInnerTunnelTerm_v0.vi` in claudeDev, cold-legal. **Do NOT re-run the recipe — run 1 is the record**
(`tools/bench/build_opfstunnelterm_v2_run1.log`; paragraph → `archive/2026-09-18-status-cycle26-stop.md` §1).
✅ **THE GAP IS BROKEN — "ZERO runnable experimental VIs" is no longer true.** The user can now run
`py tools/bgrun.py --material --max-min 30 --log tools/bench/<log> -- py -u tools/bench/drive_original_copy_v5.py`
and get a plain copy of the original driven, unattended, from panel parameters through picks, calibration, the
experiment loop and a clean own-control stop to a 285 kB trace file — twice. **Order is D0 → D1 → D2**
(`docs/cycle27-plan.md` Pre-decided 1), so D0 being met opens D1.
```

## §4 — N1 ACCEPTED (judgement session, cycle 34)

Decision text as the judgement session stated it, recorded here so STATUS can carry one line:

> **N1 IS ACCEPTED; D1 is unblocked.** On the window before the first bead loss (k<10018) the
> VI-level GPU kernel shows max |dx| 4.857e-07, |dy| 4.677e-07, |dz| 1.279e-05 against tolerances
> 1e-6 px (x,y) and ~1e-4 (z) — **zero exceedances on all three axes across 50,201 valid
> bead-frames**. All 19 whole-fixture exceedances are bead 4 at k≥10023, after that bead's own first
> loss at k=10018, where a per-bead position has no referent. The VI-level run reproduces the
> DLL-level numbers exactly, so the LabVIEW wrapper is numerically transparent.

TWO items are **flagged to the user, NOT closed**:

1. Acceptance is evaluated on the **pre-bead-loss window**, not on the whole fixture.
2. The single **z-LUT index flip** at k1679 / f1937 / bead 4 (cpu_idx 26 → 25, dz −4.667e-03, above
   the z tolerance), which `tools/bench/gpu_n1_deltas.py`'s FLIP mask excludes from the statistics.
