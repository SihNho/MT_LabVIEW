# Failed prediction: the M3a-2 build run of 2026-09-22 01:58

A LabVIEW VI-scripting build recipe was run once under a background runner with a 45-minute deadline.
One of its prediction-contract gates failed. Below is the prediction as it was written BEFORE the run,
the measured result, and the log lines. No explanation is offered here.

## The prediction, written before the run

From `docs/cycle27-plan.md` item 92 (the stage's row table) and the recipe's own docstring
prediction contract, `tools/recipes/build_d1_m3a2.py:60-101`:

- ROW A — VISA session. SOURCE = the ONE source terminal of wire 4185 = `FlatSequenceInnerTunnel`
  #4194. SINK = LEFT shift register #23880 OUTER (named 'VISA out').
- ROW B — position. SOURCE = the ONE source terminal of wire 3968 = `FlatSequenceInnerTunnel` #3974.
  SINK = LEFT shift register #23909 OUTER ('position [internal units]').
- Both are same-diagram rows on `Diagram #686`.
- Gate H8: "no mutator call was REFUSED BY THE MACHINE (this file's refusals AND the imported
  helpers', since the imported helpers record theirs there)".
- Gates A-A / A-B: each row's acceptance — the wire carried by the new sink terminal has exactly ONE
  source terminal of any owner class, that terminal is #4194 / #3974, and the original sink
  (#4344 OUTER / #4274 OUTER) is still on that net.
- Gates S1 / S2 / S3 / S4: the stage always leaves a file whose bytes differ from the input, at the
  `claudeDev` target path, with the before- and after-save screen captures landing on disk.

Expected outcome: all gates pass, two rows written, one saved `.vi` on disk.

## The measured result

`tools/bench/build_d1_m3a2.log`, `BGRUN END rc=1 after 71s`.

```
=== GATES: 15 pass / 1 fail; failing: H8 no mutator call was REFUSED BY THE MACHINE (this file's refusals and the imported helpers')
```

Neither row ran. No file was left on disk:

```
  FACT  THE FILES THIS RUN LEFT ON DISK: []
```

## The log lines

`tools/bench/build_d1_m3a2.log`, the last three lines of phase 1 and the refusal:

```
  FACT  [1] the target is D1_s3b_m3a2_20260922_015842.vi - the STAGE'S OWN OUTPUT NAME; every edit below is made on THIS file and the input artefact is not touched again until H2 re-reads its md5
  FACT  [1] ensure_loaded(target) took 1.4 s (edits are SILENTLY DECLINED on a target that is not fully loaded - the measured cause of add_shift_reg's no-op, gscript.py:764)
  FACT  UNEXPECTED EXCEPTION: TypeError: not enough arguments for format string
  FACT  MACHINE REFUSAL at main: TypeError: not enough arguments for format string
```

`tools/bench/build_d1_m3a2.json`, key `unexpected_exception`, verbatim:

```
Traceback (most recent call last):
  File "...\tools\recipes\build_d1_m3a2.py", line 1033, in main
    hints = phase_1_copy()
  File "...\tools\recipes\build_d1_m3a2.py", line 515, in phase_1_copy
    read_es("[1] the target, COLD")
  File "...\tools\recipes\build_d1_m3a2.py", line 317, in read_es
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s) - NEVER a type discriminator (42(c)), "
TypeError: not enough arguments for format string
```

The source of `read_es`, `tools/recipes/build_d1_m3a2.py:307-320`, verbatim:

```python
def read_es(tag):
    t0 = time.time()
    try:
        es = g.exec_state(TARGET)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s) - NEVER a type discriminator (42(c)), "
         "NEVER substituted for the identity test (Pre-decided 70)"
         % (row["step"], tag, es, row["t_since_start_s"]))
    return es
```

## Other measured facts of the same run

- The recipe passed its pinned static gate immediately before the run: `py tools/bench/c60c_astcheck.py
  tools/recipes/build_d1_m3a2.py --route owner` → 11 PASS / 0 FAIL, `BGRUN END rc=0 after 0s`
  (`tools/bench/c74_astcheck_m3a2_r2.log`). Gate 1 of that checker is "the diagnostic parses —
  1106 lines, 16 gate sites".
- Hygiene gates that did pass: H2 (the input artefact's md5 unchanged), H3 ×4 (the four pinned
  md5s hold), H4 (the target copy byte-identical to the input), H5 ×2 (tool files unchanged),
  H6 (VI Server refs opened 3 == closed 3, 0 live), H7 (handles read at both ends: 33,956 before,
  30,689 after the recipe's own LabVIEW restart, 45,677 at exit).
- The recipe is 1106 lines and was edited earlier the same session at four sites (lines 527, 589,
  661 and 948 onward) to apply four accepted prior-art findings; `read_es` was not among the edited
  sites. The file had never been executed before this run.
- Project standing rules that bound the run: the failure budget is 2 per dispatch; a recipe that
  fails is not patched and re-run inside the same dispatch; `tools/hooks/guard_cycle.py` blocks the
  next recipe build until an archived review exists.

## What is asked

Attack the framing, not only the line. In particular:

1. What is the strongest reason the obvious reading of this failure is wrong or incomplete?
2. What classifies this failure — and is the class one this project has already met under another
   name? Cite files if you read them.
3. Is there a mechanical check this project could have run that would have caught it before the
   45-minute LabVIEW batch was launched, given that the pinned static checker's own gate 1 reports
   that the file parses? Name it concretely.
4. What is the cheapest discriminating test between your explanation and the next most likely one?
5. What would falsify your account?
