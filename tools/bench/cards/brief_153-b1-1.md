---
card: 153-b1-1
status: current
date: 2026-10-09
---
# Brief 153-b1-1 - stagesim COLLECT-ALL replay device + self-test (docs/d1/ring-p4d.md PD370(c), violation-decisions 2026-10-09 07:0x); offline, one tool edit

Read `docs/d1/ring-p4d.md` PD370 (c) and (e). Context: in cycle 152 `stagesim` stopped at the FIRST unmeasured thing twice (op 185's owner, then op 187's tunnel naming),
costing two rounds. The device lists ALL of them in one replay. It is a stage-tool edit made on purpose; nothing else is.

## What to build (`tools/stagesim.py` only; new file md5 to be quoted)
1. A `collect_all` mode of the replay (flag, default OFF; default path byte-for-byte the same behaviour, the same refusals at the same lines).
2. In that mode, on an UNMEASURED refusal (the family that today raises at `stagesim.py:1805-1807` for an FS with no measured owner, and at `stagesim.py:1892` for an FS border tunnel naming with no table row; find the others by grepping the raises that carry an "UNMEASURED"/unmeasured text) the replay:
   (a) takes the PLAN's own predicted value for that step,
   (b) marks the step PROVISIONAL with the refusal text and the op index,
   (c) continues, and (d) returns every refusal as a list.
3. A collect-all result is never a PASS: its verdict/status field must be a distinct value (e.g. `PROVISIONAL`) that `stage_prerun`, `stagexec` and the launch gate do not accept as dry/prerun/launch PASS. Show by grep that no existing consumer maps it to PASS; if one would, STOP and return it as `OPEN:` (do not edit that consumer).

## Self-test (new file `tools/bench/selftest_c153_collect_all.py` <= 120 lines on `tools/stagekit.py` where it fits; log `tools/bench/selftest_c153_collect_all.log`)
Replay the s09 plan `tools/bench/plan_ring_p4_s09v18.json` on the s08 END graph `tools/bench/graph_ring_p4s08_20261009_033522.json` (44858dbf), with
(i) #29721's owner read NOT used (the derived graph `..._fsowner.json` e26b4d90 NOT given) and
(ii) a TEMP COPY of `tools/bench/fs_tunnel_naming_table.json` WITHOUT row `152-b1-2` (the real table 769ae8d0 is never edited; check its md5 after).
Expected: the collect-all list contains BOTH refusals - op 185 owner and op 187 naming - and the same replay in default mode still refuses at op 185 with the same text as today.
Then run the existing stagesim self-tests, all must stay as today: `py tools/stagesim.py selftest`, and `tools/bench/selftest_stagesim_{k79,pin,l2a1_80,unflip_81,fsexit_c138_1,tunnel_naming}.py`, `tools/bench/selftest_c152_fsowner.py`. Quote pass/fail counts before and after (run them BEFORE the edit too).
NOTE `selftest_stagesim_pin.py` may pin stagesim's md5: if it fails only on the md5 of stagesim.py, report it as `OPEN:` with the line; do not edit the pin file.

## Invariants (quote md5 before/after; unchanged)
stagekit 604529e8, addrcheck 207beb0d, stagexec 1bab9cf9, gscript 1a80236e, stage_prerun c739eb86, vigraph 13be0847, card_clock (as found), `fs_tunnel_naming_table.json` 769ae8d0, s09 VI eb1d0f31, graph 22f967b5. Only `stagesim.py` changes (128bacfb -> new).
No recipe gate-criterion change (PD370(e)); no hook edit; no LabVIEW use at all (labview none); no motor or camera.

## Return (<= 30 lines)
New stagesim md5; the two listed refusals quoted (op, text, file:line of the log); self-test counts old/new; whether any consumer could read the PROVISIONAL status as PASS. `OPEN:` for anything needing judgement. Failure budget 2.
