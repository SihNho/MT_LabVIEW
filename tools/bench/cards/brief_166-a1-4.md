---
card: 166-a1-4
status: current
date: 2026-10-12
---
# Brief 166-a1-4 (assignment 166-1) - PB TIGHTENING (PD397(e)) + drain fp-86, OFFLINE

Plan: `docs/d1/ring-p5c.md:64-71` (PD397(e), the text is binding), carried by PD403(d)(3) (`:271`). Read `docs/script-writing.md` (calls into the shared module; new/changed function = docstring that names its self-test).
Offline only, no LabVIEW, no `tools/hooks/**` edit. **Stricter only. A tightened rule that blocks an ADOPTED row is not loosened: hand back (RETURN) with the row.**

## What to build (in the shared PB code of `tools/stagekit.py`: find `pb_check` and the class-2/class-3 functions and `chain_tunnel_case`, `chain_connects` by `grep "def "`; do not copy)
1. **Provenance (class 3):** a class-3 row ("plan-wired into an inherited case", PD395) also needs a `RECORD PB <sink>` line in the ADOPTED step's scratch log, with the same S1 source set. Read how the scratch recipes print `RECORD PB` lines (`diag_c164_*_scratch.log`, `diag_c165_p5s02e_scratch.log:152-157`).
2. **Coverage per frame instead of the multiplicity count, in classes 2 and 3:** every frame in the allowed set carries exactly one tag for the sink, and no tag sits on any other frame.
3. **`chain_tunnel_case` becomes newest-wins**, like `chain_connects`.

## Self-test (new `tools/bench/selftest_c166_pbtight.py`, scope header, RESULT line; the function names it exercises are in the docstrings)
- Positive: the stored PB inputs of the adopted steps p5s02c, p5s02d and p5s02e (the P5 final; its scratch log is `diag_c165_p5s02e_scratch.log`; PB result at `:157` = "PASS by position [31,31] = 26 + 5 RECORDED") still RECORD every row. Find the exact stored inputs by reading what `diag_c165_p5s02e_scratch.log`'s PB gate and `diag_c164_a3_*`/`diag_c163_*` scratch logs used; say which files.
- Negative: (i) a class-3 row WITHOUT the provenance line is blocked; (ii) a missing frame; (iii) a doubled frame; (iv) a `chain_tunnel_case` with an older and a newer entry picks the newer. Quote each case's result.
- Stricter-only proof: re-score the stored adopted PB results with old vs new rule; every row old-PASS stays PASS or is listed; no old-BLOCK row becomes PASS. A row that becomes BLOCKED = RETURN with the row (adopted file, step, sink).

## Then
- **Drain fp-86** with `py tools/gate_fp.py drain --id fp-86 --fixed "<the function:line>" --selftest "<selftest file + result line>"` (read the fp-86 entry in `tools/bench/gate_fp_queue.jsonl` / `py tools/gate_fp.py list` first, and state in facts what its false positive was and why the tightened rule addresses it, or log honestly that it does not and leave it open).
- **Stored plans:** `plan_ring_p5s01a/b.json`, `plan_ring_p5s02a` .. `e` compile and dry byte-equal after the change (the existing compile/dry checks, e.g. `tools/bench/selftest_c134_1_dry.py`, `prep_c165_a3_3_dry.log`'s command; state which you ran and quote the line).
- Run the existing selftests that a gate RUNS and that exercise PB (PD396(a)(4): re-pin only a suite a gate runs, by name, once). Pins that drift because stagekit changed: list them (no mass re-pin; the re-pin is a separate step at the end of the cycle).
- fn description: docstring on any NEW function, `docs/fn_descriptions.json` for old ones.
- Facts `tools/bench/diag_c166_a1_4_facts.md` (<= 40 lines, file:line each). Hash the seven VIs before/after (unchanged); no LabVIEW process. Do NOT touch E5 / the reuse detectors (next card), the EL advisory / elpredict (done by card 166-a1-3), STATUS, INDEX, the plan.
