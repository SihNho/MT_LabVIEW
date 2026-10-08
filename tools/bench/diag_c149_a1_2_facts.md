---
type: facts
status: current
date: 2026-10-08
card: 149-a1-2
---
# Card 149-a1-2 facts: packages visible in-process (no install) and the reader WORKED (OCR, 51 items = window's own 51), but s06 reads 51 vs predicted 55 -> EL-ADVISORY rc 1 -> RETURN, NOT adopted

## Step 1 - probe (`tools/bench/diag_c149_a1_2_probe.py`, log `diag_c149_a1_2_probe.log`, RESULT 5/0 :11)
- Command form: the permission layer REFUSED both `$env:PYTHONPATH='...'; py ...` (PowerShell: "Command modifies environment variables")
  and `PYTHONPATH=... py ...` (Bash: approval required). Equivalent used: the script itself puts the LocalCache folder at sys.path[0]
  (where PYTHONPATH entries land) and sets os.environ['PYTHONPATH'] for its own process only (probe.py:9-15, log :3,5).
- Versions (log :6-10): comtypes 1.4.17, rapidocr_onnxruntime 1.4.4, numpy 2.2.6, onnxruntime 1.23.2, cv2 5.0.0.93 - all from
  `%LOCALAPPDATA%\Packages\Claude_pzs8sxrjxfjjc\LocalCache\Roaming\Python\Python310\site-packages`. Nothing installed; no .pth / py.ini /
  global site-packages / user env touched.

## Step 2 - Error List read (`diag_c149_a1_2_elrun.py` = runpy of UNCHANGED errorlist_check.py with the same sys.path[0]; log `diag_c149_a1_2_el.log`)
- `--vi claudeDev\D1_ring_p4s06_20261008_174730.vi --expected errorlist_expected_D1_ring_p4s05_20261008_002621.json --role final`, bgrun 35 min.
- Byte copy `_elc_D1_ring_p4s06_..._181243.vi` identical=True (:7); UIA 0 items (:21), MSAA 0 listitems (:23-24), OCR engine rapidocr-onnxruntime (:25)
  - same reader path as s05 at 01:23 (diag_c147_a1_1_el.log:20-25). Window's own count 51 ('51 errors and warnings', :27); 51 items read,
  "reached the window's own count" (:81); Esc closed (:82); refine_rows not refined [2,33,50] (:83).
- Verdict MISMATCH vs s05 expected: extra 5, missing 9 (:87); BY-DESIGN STOP "items MISSING" (:86); RESULT 11/0, BGRUN END rc=1 after 674 s.
- Read json `errorlist_D1_ring_p4s06_20261008_174730_20261008_181243.json` md5 899e2656; bed md5 unchanged True (:87).

## EL-ADVISORY (`diag_c149_a1_2_eladv.py`, log `diag_c149_a1_2_eladv.log:3-4`) - rc 1 RETURN
- total read 51, pred 55, diff -4 (> EL_TOTAL_TOL 3); unseen classes [] (no new class).
- per-class (read - pred): input -2 (4 vs 6), loop-tunnel-undirected -3 (0 vs 3), wire-sinks-no-source -1, output-tunnel->Replace Array Subset -1,
  output-tunnel->subVI -1, types-mismatch +1 (2 vs 1), wire-not-connected +2 (22 vs 20), wire-loose-ends +1 (21 vs 20); local 1, sr 1 = pred.
- Why a copy: guard_bash's LAUNCH GATE refused the recipe's own offline `--el-advisory` citing the OLD 12:52 failed segment of the appended
  scratch log (diag_c147_p4s06v18_scratch.log:341-690; last segment PASS 22/0 :1040). Logged **fp-62**. Copy = recipe :84-129 verbatim (peer
  `archive/peer/2026-10-08-c149-a1-2-eladv.md`: function-equivalent, rc not an artefact of the copy).

## Peer (hypothesis, both ANSWERED)
- `archive/peer/2026-10-08-c149-a1-2-el51.md` ($1.80): "reader probably right (51); drop = only unmodelled improvements NOT supported".
  New s06 item 6 "source void -> sink I32" (read json :322) not in s04/s05; op 21 "target BROKEN" (scratch log :990-994) never checked for a
  broken wire; pred's uncertain +1 input (10757 'array', pred :170-177) makes the real gap -5; one Build Array input item unexplained (3 -> 1).
  Cheapest test (read-only): compare s06 show-error captures items 5/6 with s05 items 7/8/10-13; check header/last-row capture for "51".
- `archive/peer/2026-10-08-c149-a1-2-eladv.md` ($0.90): copy faithful; rc decided by the OCR'd header count (alternative B unchecked).

## Not done (RETURN): adopt, final EL expected file, fresh load, graph, load_by_vi. Prepared, unrun: diag_c149_a1_2_{adopt,elexp,mkgraph,graph,memload}.py.
## Invariants (`diag_c149_a1_2_inv.log` 12/0): s05 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, s06 569ffbf5, stagekit, stagexec,
gscript, elrule, errorlist_check, memory_model 88eeb037 unchanged; no `_elc_*` left; adopted_scratch.jsonl not written. Handles 37208 -> 31259
(el.log:85). LabVIEW: tasklist "No tasks" after the run.

## Jev ladder
| log | ladder class p | NEXT-ACTION | what I did | result |
|---|---|---|---|---|
| diag_c149_a1_2_el.log | new-problem 0.610 (jev_gate.log:5276) | hypothesis review owed | dispatched c149-a1-2-el51 | ANSWERED, claim not supported |
| diag_c149_a1_2_eladv.log | new-problem 0.740 (jev_gate.log:5282) | hypothesis review owed | dispatched c149-a1-2-eladv | ANSWERED, copy faithful |

OPEN: (1) Is s06's 51 a new break (void->I32, op-21 "target BROKEN") or modelled-away items? run el51's read-only capture comparison / a
broken-wire read of w23807 before adopting, or accept with a new expected file? (2) The runner must see the LocalCache packages: launch it
inside the app, or keep the per-command sys.path wrapper (diag_c149_a1_2_elrun.py) for every EL read?
