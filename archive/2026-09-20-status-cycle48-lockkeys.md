---
type: archive
status: archived
date: 2026-09-20
tags: [status-relocation, lock-keys, rule-4]
---

# STATUS lock keys relocated VERBATIM on 2026-09-20 (cycle 48, rule 4)

STATUS.md passed the ~110-line threshold when cycle 48's `owner_c48s1cd` key was added, so the five older lock
keys below were moved here **verbatim, unedited** and replaced in STATUS.md by one `lock_history:` pointer. Four
of them were already pointers into earlier relocation files; nothing is deleted, only moved.

## §1 — `owner_c47s1` (cycle 47, the refused S1 launch)

```yaml
  owner_c47s1: # 🔴 **NEVER ACQUIRED — the S1 CD launch was REFUSED by `guard_cycle.py`'s STALE-RETROSPECTIVE branch at 23:16; no LabVIEW, no process, no artefact.** Recipe integrity verified first and MATCHES the pin on all three (815 lines, md5 `2d69b0dc71ac…`, sha256 `c003d8547b50…`); `claudeDev\D1_s1_copy.vi` still does not exist. VERBATIM refusal + the full key → `archive/2026-09-19-status-cycle47-relocate.md` §1. ⚠️ Its closing claim "the ORIGINAL cannot be read" is **FALSE and corrected in §4** — one of four routes works.
```

⚠️ Superseded in fact by cycle 48: the same command ran on 2026-09-20 00:08:09 and produced
`claudeDev\D1_s1_copy.vi` (md5 `3e3d23cefd3a334001aa9d6156bf1aee`) — see STATUS's `owner_c48s1cd` key.

## §2 — `owner_c47t2` (cycle 47, the offline RSRC block diff)

```yaml
  owner_c47t2: # ✅ **T2 IS DONE — no lock needed, no LabVIEW, no COM, no motor, no camera.** OFFLINE RSRC block diff of `claudeDev\D1_s1arm_savetest.vi` against the ORIGINAL: **45 blocks each side, 43 byte-identical, 2 different, 0 one-sided** — only `LIvi` (+920 B) and `LIbd` (+920 B), the LinkObj reference tables. `VICD` / `BDHb` / `FPHb` / `VCTP` / `TM80` / `DFDS` / `LVSR` / `BDPW` all byte-identical. ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` **before and after**. Artefacts `tools/bench/t2_rsrc_blockdiff.json` md5 `0b8d68e9613e4384f5f07ec618ac29fc` + `…blockdiff.log` md5 `9131dc0a81a28396c5a3679d849c4cce`; 14 self-checks 0 fail; 8 sourced URLs + peer `archive/peer/2026-09-19-t2-rsrc-format.md`. Tables, the judgement, and the one OPEN item → `archive/2026-09-19-status-cycle47-relocate.md` §3.
```

## §3 — `owner_c46s1cd` (cycle 46 act 7)

```yaml
  owner_c46s1cd: # 🔵 **RELOCATED VERBATIM (rule 4) → `archive/2026-09-19-status-cycle47-relocate.md` §2** — cycle 46 act 7: the stop-record deadlock repair (30/0 + 29/0), the recipe RELEASED on 6 `FIXED:` lines, the static audit 6 PASS / 0 FAIL, and the `CYCLE_BUILD_BUDGET = 10` diagnosis that turned out to be the wrong branch.
```

## §4 — `owner_c46_closed` (the three released cycle-46 keys)

```yaml
  owner_c46_closed: # 🔵 **THE THREE RELEASED CYCLE-46 LOCK KEYS ARE RELOCATED VERBATIM (rule 4, act 7) → `archive/2026-09-19-status-cycle46-relocate.md` §3** — `owner_c46s1` (S1 phases A/B: `g.save()` under preload proven, arm md5 `e0112963cc1b9e3be29d2bb053ba9029`, gate B's cold-link FINDING), `owner_c46m4` (gate B's ANSWERED hypothesis review + the 7-PASS structural census, all nine classes delta 0) and `owner_c46m5` (T1, the 98-row subVI path census, 15 PASS / 0 FAIL, `tools/bench/s1_subvi_paths.json` md5 `d81e11f71578303b8684c9754d05bcee`). ORIGINAL md5 `2a78e17c449cacdaf5da389818526859` unchanged in all three.
```

## §5 — the previous `lock_history` (eight older keys)

```yaml
  lock_history: # 🔵 **EIGHT OLDER LOCK KEYS RELOCATED VERBATIM (rule 4, act 7) → `archive/2026-09-19-status-cycle46-relocate.md` §4** — `owner_c45m4_c45m3`, `owner_c45m2_s0v3`, the previous `lock_history`, `owner` / `since` / `purpose` (D1 route-B runs 8–10), `purpose_c37_38` and `purpose_now` (N1 acceptance). Every one of them was already a pointer into the cycle-36/39/44/45 relocation files; nothing new is recorded by moving them.
```
