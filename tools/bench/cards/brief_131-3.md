# Brief 131-3 — P3b-1 scratch run `pin4` on a P3a byte copy (LabVIEW), PD271(c)

Same procedure as `tools/bench/cards/brief_130-6.md` Step B (pin3), now on the re-finalized plan
(`plan_ring_p3b1.json` edbdba99, pred e4bba5b3; `docs/d1/tooling.md` PD271). The real recipe is NOT launched; the bed is
never opened for edit (byte copy only).

## Predictions (stated before the run — a miss is a return, not a retry)
- every recipe gate PASSes through op 31 of 31, including each crossing's tunnel NAME (op 26 now predicts `Image Out`)
  and the per-frame FS counts f0 0 / f1 16 / f2 18 (PD269(b)(c));
- peak LabVIEW memory ≤ 663.4 MB (X10; pin3 measured 650.4 MB at op 26);
- scratch Error List `--count-only --role scratch` per-class counts == the pred file's (or its named alternative).

## Steps
1. `py tools/stage_prerun.py --dry` + `--prerun` on recipe + helper (current bytes) — must still PASS (31/31, 15/0).
2. Scratch `pin4` under bgrun, WAITED IN-TURN to its `BGRUN END` (`.claude/agents/material.md:92-98`; never end the turn
   while it runs; `tools/wait_logs.py` ticks).
3. Error List count-only on the scratch copy; scratch copy deleted; LabVIEW verified gone; bed md5 4dfa44aa unchanged.
4. Only if 1–3 all match their predictions and ≤ 50 min used: write the MEASURED census into `plan_ring_p3b1_pred.json`
   by a script citing the log line (PD264(c)), then `--dry` + `--prerun` again; report `--scratch-required` exit.

Return at the first unexpected result (step finished, LabVIEW closed, scratch cleaned). result/1 in
`tools/bench/cards/result_131-3.json`, with the measured peak, per-gate counts and Error List counts.
