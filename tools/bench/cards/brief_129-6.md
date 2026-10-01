# Brief for card 129-6 (cycle 129 judgement) — WHERE does LabVIEW's private memory grow ~4 MB per stage op?

A MEASUREMENT card. It changes no tool, plan or recipe and decides nothing; the judgement session decides from its numbers.

## Facts it starts from (log-reader 129-5, `tools/bench/cards/result_129-5.json`)
- P3b-1 scratch pin2: private MB k0 570.0 → k5 588.8 → k10 606.1 → k15 638.0 → k20 650.5 → k25 672.3 → k30 689.0 → k33 697.3
  (`stage_d1_ring_p3b1_scratch_pin2.log:55,119,203,305,352,398,448,476`) ≈ +3.9 MB per op.
- P3a launch: 566.1 → 652.3 at k21 (`stage_d1_ring_p3a.log:39,252`) ≈ +4.1 MB per op.
- Limits: `stagexec.MEM_STOP_MB` 700 (`stage_prerun.py:59`), X10 fail point 690 MB, LabVIEW error 2 seen at 695 MB
  (`stage_prerun.py:1761-1764`). A 40-op step would end near 730 MB.

## 0. Time arithmetic (budget 35 min; bgrun `--max-min 30`)
fact question in the background ~5–10 min (overlaps) · ≤120-line diagnostic + dry/prerun ~6 min · fresh LabVIEW + open the
copy ~2 min · W1 15 reads (pin2 ran 33 ops in ~19 min, ≤ 30 s per checkpoint read) ~7 min · W2 15 edits ~2 min · W3 close +
reopen ~2 min · hygiene ~3 min (pin2's FAIL hygiene took ~16 min — report it if it repeats) · total ≈ 25–30 min.

## 1. Fact question first (background; `peer.ps1 -Kind fact`, no `-Agent` = gemini first arm, Opus fallback)
"In LabVIEW 2023–2026, does each VI Scripting edit made through VI Server (create node, wire, tunnel) add an entry to that
VI's undo history? Is memory per undo step proportional to the size of the edited diagram? How is the number of undo steps
per VI set (Tools » Options » Environment, its LabVIEW.ini token), and is there a VI Server property or method that limits
or clears a VI's undo history during a scripting session? Primary sources please." Report the answer + sources only.
**Change no LabVIEW setting or ini file** (the user's experiments use this LabVIEW).

## 2. Diagnostic `tools/bench/diag_c129_6_mem.py` (≤ 120 lines, stagekit), on a dated byte copy
`claudeDev\scratch_c129_mem_<ts>.vi` of the P3a bed (md5 `4dfa44aa…`; never the bed), fresh LabVIEW. Record private MB and
handles at every point:
- **M0** after open.
- **W1 reads only:** 15 repetitions of EXACTLY the per-op checkpoint read stagexec's Executor does after each op in the
  scratch run (the same functions the pin2 E1/STEPX/census checkpoints call — name them), no edit in between.
- **W2 edits only:** 15 cheap scripted edits with NO checkpoint read between them, on diagram 27219 (the case frame P3b-1
  edits): e.g. create an I32 constant with the plan's constant route; record MB after each.
- **W3:** close the copy without saving, then reopen it: MB after close and after reopen.
Report MB per step and the slope (MB/op) of W1 and W2, plus M0, W3. The copy is deleted at the end; LabVIEW verified gone.

## 3. Return
`result/1` (`tools/bench/cards/result_129-6.json`), validated, and `py tools/card_clock.py` on it (OK). Facts: the read
functions W1 called (file:line), every MB reading with its step, the two slopes, W3's two readings, the fact answer in two
lines with its source URLs, minutes per step. First unexpected result: finish the step, LabVIEW closed, copy deleted, return.
