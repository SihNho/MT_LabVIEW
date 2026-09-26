# c103d-hooks-before

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.4757  in 20 / out 18733 / cache-create 107565 / cache-read 1030719  (205s, 19 turn(s))
- **date:** 2026-09-27 03:13:03
- **outcome:** ANSWERED (210s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim. Log: tools/bench/selftest_c103d_hooks_before.log (script tools/bench/selftest_c103d_hooks.py, card tools/bench/cards/task_103-4.json pass lines 2).

CLAIM: the three FAIL lines in selftest_c103d_hooks_before.log (S1, S2, L1) are the PRE-FIX state of the two defects card 103-4 names, run
deliberately BEFORE the edit ("hook edits: self-test before and after"), not a new problem:
 (1) tools/stop_record.py segment_class() classes `py -m <module>` as "build" unless the module is in PY_READONLY_MODULES
     {py_compile, ast, tokenize, tabnanny}; so `wc -l tools/recipes/stage_d1_disp.py && py -m pyflakes tools/recipes/stage_d1_disp.py 2>&1 | head`
     (tools/hooks/material_marker.log:2175, REFUSED STOPPED-RECIPE) was refused although pyflakes only parses the file.
     The fix is in tools/hooks/guard_bash.py stop_gate(): LINT_SEG_RE drops `py -m pyflakes|pycodestyle|flake8 <args> [2>&1]` segments
     before stop_record.check_command(), unless EXEC_PIPE_RE matches the whole command.
 (2) tools/stage_prerun.py vi_modifying_calls() classes tools/bench/selftest_stagekit.py (offline: "Nothing here opens COM, touches claudeDev
     or reads a .vi") as VI-modifying because it imports stagekit and calls save_route/create_local_read on a fake Stage
     (material_marker.log:2185 REFUSED PRERUN-GATE). Fix: VI_MOD_EXEMPT_PATHS = {"tools/bench/selftest_stagekit.py"} by project path.
The seven negatives (S3-S7, L2, L3) passed before the edit and must pass after.

Attack: is any of the three fails NOT explained by these defects? Does the guard_bash change open a way to EXECUTE a stopped recipe
(e.g. a crafted `py -m pyflakes` segment that runs code, a quoting trick through split_segments, `python -m flake8 --config` plugins,
a `-m pyflakes` segment whose arguments include `&&`-free exec)? Is dropping lint segments ever a loosening beyond the read-only case?
Is exempting selftest_stagekit.py by path unsafe? Name the cheapest discriminating test.


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**Verdict: the claim fails.** The three FAIL lines fit the two defects, but the `guard_bash` fix lets a command that actually runs a stopped recipe get through the gate. That breaks the card's own rule "never loosen a refusal beyond the read-only case" (`task_103-4.json:75`). The path exemption is also looser than it looks. And the "run before the edit" part is claimed, not measured.

## 1. Strongest reason the claim is wrong: the fix passes a command that runs the recipe

The lint pattern `LINT_SEG_RE` (`guard_bash.py:174-175`) separates arguments with `\s+`, and `\s` also matches a newline. Its argument pattern also accepts `"` and `\`. The splitter it relies on (`stop_record.split_segments`, `stop_record.py:183-211`) does not treat `\"` as an escaped quote. So this Bash command:

```
py -m pyflakes \"x
py -u tools/recipes/stage_d1_disp.py
\"
```

- **What the hook sees:** a quote opening at `\"x` and closing at the final `\"`. That is one balanced segment, and the lint pattern matches all of it, so the segment is dropped. The executor check (`EXEC_PIPE_RE`) does not fire either: there is no pipe, no `$(`, no backtick. `check_command("")` gets an empty string and allows.
- **What bash sees:** `\"` is a literal character, and the newline ends the first command. So line 2 runs the stopped recipe.
- **Before the fix:** this command was refused, because the whole segment was `py -m pyflakes` (build class) and it carried the recipe path.

This is a genuine loosening of a gate that used to refuse this command. It is not accidental-launch-realistic: nobody types this by mistake. It also has an older twin: `wc -l \"x<NL>py -u R<NL>\"` already gets through today, because `wc` counts as read-only. So the fix did not create this class of hole, but it adds another way in, and none of the new tests covers it.

I also expect the stage launch gate to miss this command. `stage_prerun.launched_py` (`stage_prerun.py:1290-1296`) does not split on newlines and tokenises with `shlex(posix=False)`. I have not run this.

## 2. Other ways dropping lint segments goes beyond "only parses the file"

These are all new relative to the pre-fix gate, since before it `py -m pyflakes|pycodestyle|flake8` on a recipe was build class and refused.

- **flake8 runs code from its config.** It loads `[flake8:local-plugins]` from `.flake8`, `setup.cfg` or `tox.ini`, with `paths` relative to that config file. `--config` and `--append-config` name any config file, and the argument pattern allows `--config=<path>`. `--output-file` writes to any path.
  - Sources: https://flake8.pycqa.org/en/latest/user/configuration.html and https://flake8.pycqa.org/en/latest/user/options.html
  - None of those config files exist at the project root today (glob found nothing). That is today's state, not a guarantee.
- **`-m` can load a different module than the real linter.** `python -m` puts the current directory first on the import path, and `PYTHONPATH` also affects the lookup (https://docs.python.org/3/using/cmdline.html). The lint pattern accepts an environment prefix, so `PYTHONPATH=tools/bench/sim/disp py -m pyflakes <recipe>` is dropped. That folder is writable by this card (`task_103-4.json:55`), so a `pyflakes/__main__.py` placed there would run with the recipe as its argument.
- **The program name is too broad.** `py(?:thon)?[\w.]*` matches `pytest`, `pylint` and the like, not just `py`/`python`. This copies `stop_record._PY_RE`, which already has the same breadth for `-m ast`.

All of these need a deliberately planted file or a crafted command. The gate's actual history is accidental launches (route-B run 3), so the real-world risk is low. The claim, though, was that nothing opened beyond the read-only case, and that is false as written.

## 3. The path exemption (`VI_MOD_EXEMPT_PATHS`)

- `tools/bench/selftest_stagekit.py` matches `tools/bench/selftest_*`, which is in the card's write flags. Any later material session can edit that file, and it stays exempt with no content or hash check.
- That runs against `stop_record.py`'s own principle: refuse by path, release only for specific file contents (hash).
- It also imports `gscript`, the COM runner (`selftest_stagekit.py:185`).
- To be fair, the older name-only exemption (`VI_MOD_EXEMPT`, `stage_prerun.py:1253`) is looser still, so this is not a regression.

## 4. Alternative explanation of the same log

There is no after-log; only `selftest_c103d_hooks_before.log` exists, and `guard_bash.py` and `stage_prerun.py` now contain the fix. The log therefore does not tell apart:

- **(a)** the code before the fix (the claim), and
- **(b)** the edit already in place but not taking effect.

Two further limits on what the log shows:

- S1–S7 test a stand-in `check_command` (`selftest_c103d_hooks.py:23`), not the real record logic. The real refusal is shown only by `material_marker.log:2175`. That was a build-class segment plus a hash mismatch: `stop_records.json:1149-1233` holds several records for `stage_d1_disp.py`.
- S2 was never observed in any log; it is predicted from the same code path.

## 5. What would falsify the claim

- The after-run still shows S1, S2 or L1 failing, which would support (b).
- The newline command in section 1 returns 0 from `GB.stop_gate` against the current code. From reading the code, I expect it does.

## 6. Cheapest discriminating test

Two parts, both offline with no LabVIEW:

1. Rerun `selftest_c103d_hooks.py` now. Ten of ten passing settles "before vs after", provided the file's modification time is later than 03:08:39.
2. Add four negative rows that must each return 2 (refused):
   - **N1:** `py -m pyflakes \"x\npy -u R\n\"`
   - **N2:** `PYTHONPATH=tools/bench py -m pyflakes R`
   - **N3:** `py -m flake8 --config=x.cfg R`
   - **N4:** `pytest -m pyflakes R`

I predict N1–N4 all return 0 against the current code. If they do, tighten `LINT_SEG_RE`:

- program exactly `py` or `python[\d.]*`, with no environment prefix;
- pyflakes and pycodestyle only (drop flake8);
- separators `[ \t]+`, not `\s+`;
- arguments restricted to `[\w./\\:-]+`, so no quotes, `=` or newlines.

Also pin the `selftest_stagekit.py` exemption to a file hash, or add an import check that refuses it once it imports anything that opens COM.

Sources:
- https://flake8.pycqa.org/en/latest/user/configuration.html
- https://flake8.pycqa.org/en/latest/user/options.html
- https://docs.python.org/3/using/cmdline.html

## Sources

(extract from answer)

## What was done with it

ACCEPTED (card 103-4 material session, 2026-09-27). The "claim fails" verdict was right on the loosening: s1 (newline inside a
quote-balanced segment), s2 (flake8 config plugins, `-m` import-path hijack through an env prefix, `py[\w.]*` too broad) and s3 (path-only
exemption) were all applied, as the review's s6 recipe proposed:
- `tools/hooks/guard_bash.py` LINT_SEG_RE: program exactly `py`/`python[N.N]`, no env prefix or flags, pyflakes/pycodestyle only (flake8
  dropped), `[ \t]` separators, arguments `[\w./\\:-]+` only; no drop when a segment `cd`s anywhere but the project root, or when a
  pyflakes/pycodestyle shadow sits at the root.
- `tools/stage_prerun.py` VI_MOD_EXEMPT_PATHS pins `tools/bench/selftest_stagekit.py` to its sha256 (82ab60d4...).
- The discriminating test was run: `tools/bench/selftest_c103d_hooks_after.log` 17/0, with N1-N4 from s6 and N5 (cd elsewhere) and L4
  (other bytes at the exempt path) all refused/classified; S1/S2/S8/L1 pass. The before-log's three FAILs are the pre-edit state.
Not done: S-rows still use a stand-in check_command (the live record for stage_d1_disp.py is released for the current bytes by
`2026-09-27-priorart-c103-partb-entry.md`, so a live refusal cannot be exercised without planting a record); the older `wc -l \"x<NL>...`
twin in stop_record.py is outside this card's write flags (stop_record.py not writable) - reported as open.
