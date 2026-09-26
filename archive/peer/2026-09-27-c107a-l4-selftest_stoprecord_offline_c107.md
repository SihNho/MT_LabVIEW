# c107a-l4-selftest_stoprecord_offline_c107

- **agent:** claude
- **role:** hypothesis
- **model:** claude-opus-5-5 (effort high; peer.ps1 default for role hypothesis)
- **kind:** review
- **cost:** $1.0522  in 18 / out 10908 / cache-create 84706 / cache-read 781397  (117s, 11 turn(s))
- **date:** 2026-09-27 07:57:24
- **outcome:** ANSWERED (121s)
- **verdict-card:** (no -ReviewCard)
- **why asked:** (Claude fills in)
- **verdict:** unverified

## Question

ATTACK this claim about a failed self-test gate (card 107-1).

Failing log: tools/bench/selftest_stoprecord_offline_c107.log, gate "L4 HEAD launched_plan_runs misses line 2 (negative)" FAIL.
Script: tools/bench/selftest_stoprecord_offline_c107.py.

What L4 did: it extracted `launched_plan_runs` from `git show HEAD:tools/stage_prerun.py` and called it on
c1 = "py -V\npy tools/stagexec.py run tools/bench/sim/disp/plan_disp.json", predicting [] (HEAD does not split on newlines).
HEAD returned one hit.

CLAIM (our explanation): the prediction was wrong, not the code. HEAD's launched_plan_runs (tools/stage_prerun.py, HEAD
version, the `for i, t in enumerate(toks)` loop) examines EVERY py-token in a segment independently, so in a plain two-line
command the second line's `py tools/stagexec.py run <plan>` is still found even though the newline is not a separator.
(launched_py differed: after the first py token it jumps `i = j + 1`, so `py -V<NL>py -u <stage>` skipped the second py.)
The shape HEAD really misses is the one in archive/peer/2026-09-27-c106e-oldcode-o1.md:24-30,52: a BACKSLASH-ESCAPED quote
spanning the newline (`wc -l \"x<NL>py tools/stagexec.py run p.json<NL>\"`), where shlex.split(posix=False) groups line 2
into one token while bash runs line 2. The fix: L4's negative uses that shape (c4), and a new L5 asserts the edited
launched_plan_runs (which now joins continuations and splits on \r?\n before shlex, like launched_py) finds c4.

Already ruled out: the edit is in place (L1/L2/L3 PASS on the new code); the HEAD extraction ran (it returned a list).

Questions: Is the explanation of why HEAD found c1 correct from the code? Does c4 actually defeat HEAD (read shlex non-posix
handling of `\"`)? Is there a shape where the NEW launched_plan_runs still misses a line-2 plan run, or where splitting on
newlines inside a genuinely quoted multi-line argument produces a false positive that would wrongly gate a command?


--- HOW TO ANSWER (mandatory, from the dispatcher) ---
Your job is to REFUTE the claim above, not to confirm it. Do not open with agreement.
1. Name the single strongest reason the claim is WRONG.
2. Name at least one ALTERNATIVE explanation of the same evidence.
3. Name the observation that would FALSIFY the claim.
4. End with the CHEAPEST discriminating test that separates the claim from your alternative.
If you still believe the claim holds after all four, say so explicitly and state what would change your mind.

## Answer

**The claim is right about c1 but wrong about its fix.** c4 does not defeat HEAD, so L4 will fail again on c4.

## 1. Strongest reason the claim is wrong: HEAD already finds c4, and this has been measured

- **Measured.** `tools/bench/diag_c106e_oldcode.log:12` shows HEAD's `launched_py` **finding** the stage on the same backslash-quote shape: `PASS O1a old launched_py FINDS the backslash-quote \`wc -l \"x<NL>py -u <stage><NL>\"\``. HEAD's `launched_plan_runs` uses the same tokenizer: `shlex.split(posix=False)` followed by `strip("\"'")`. It also scans every token (`for i, t in enumerate(toks)`), so it will find c4 too.
- **Your citation says the opposite.** `archive/peer/2026-09-27-c106e-oldcode-o1.md:24-30` is the *question* from the earlier round, i.e. the same wrong claim. Lines 52-54 are that review's *refutation* of it. The self-test comment at `selftest_stoprecord_offline_c107.py:69-71` repeats the misreading.
- **Why, from the shlex rules** (https://docs.python.org/3/library/shlex.html#parsing-rules). In non-POSIX mode, "Escape characters are not recognized" and "Quote characters are not recognized within words". So `\"x` is one ordinary word and the `"` inside it opens nothing. The newline is plain whitespace, and HEAD sees these tokens: `wc -l \"x py tools/stagexec.py run <plan> \"`. The `py` token at index 3 matches, then `stagexec`, `run`, `<plan>`.
- **Unmeasured.** The log on disk holds only run 1. The L4 label there ("misses line 2") is not the current label ("misses the escaped-quote line 2"), so c4 has never been run. Line 11 of the script ("L4 HEAD … finds 0") is a prediction.

On the part the claim gets right: tracing the code, HEAD on c1 gives `py -V py tools/stagexec.py run …`. At i=0 the loop skips `-V` and lands on `py`, which is not stagexec. At i=2 it finds the run. That is consistent with the one hit in the log (`selftest_stoprecord_offline_c107.log:44`). I read the edited function (`tools/stage_prerun.py:1511-1532`). I took HEAD's loop from the claim and the unchanged loop body, because I could not run `git show`.

## 2. Alternative explanation

HEAD's `launched_plan_runs` has **no line-2 miss driven by escape characters at all**. Scanning every token makes it immune to the `py -V` swallow that broke `launched_py`. The only line-2 miss is a **real quote at the start of a word that bash does not treat as a quote**. The clearest case is a quote inside a bash comment:

```
echo x # "a
py tools/stagexec.py run tools/bench/sim/disp/plan_disp.json
# "
```

- **Bash:** lines 1 and 3 are comments, and line 2 runs.
- **HEAD:** `shlex` has `commenters=''` under `split(comments=False)`, so `"a<NL>py …<NL># "` is one quoted token. HEAD misses the run.
- **New code:** it splits on newlines first, so line 2 is its own segment and is found.

This is the discriminating negative that c4 was meant to be. Without it, the edit to `launched_plan_runs` fixes a hole that no test demonstrates.

## 3. What would falsify my refutation

HEAD's `launched_plan_runs(c4)` returning `[]`.

## 4. Cheapest discriminating test

Run the existing L4 harness (lines 74-77) on two inputs:
- **c4:** I predict **1 hit**, so the claim fails.
- **The comment-quote command above:** I predict `[]` on HEAD and 1 hit on the new code, so it is the correct L4/L5 pair.

## Your extra questions

**Can the new code still miss a line-2 run?** Yes. These are separate from the newline handling, so they are not regressions, but they are real misses:
- `py -V<NL>(py tools/stagexec.py run p.json)`: the token `(py` fails `^py(thon)?…`.
- `x=$(py tools/stagexec.py run p.json)` and backtick substitution.
- `echo hi<NL>bash -c "py tools/stagexec.py run p.json"`: the command is one quoted token.
- `cd tools && py stagexec.py run ../p.json`: `STAGEXEC_RE` requires a `tools/` prefix.
- `py tools/stagexec.py <option> run p.json`: this only matters if stagexec accepts options before the subcommand, which I have not checked.

**Can the newline split cause a false positive?** Yes, and it is a regression.
- **Example:** `git commit -m "notes<NL>py tools/stagexec.py run tools/bench/sim/disp/plan_disp.json<NL>"`, or a `peer.ps1 -Task "…"` brief with the command on a line of its own.
- **HEAD:** one quoted token, not found. That is correct, because bash does not run it.
- **New code:** line 2 becomes a segment, so it is found. Then `check_launch` refuses it unless a dry-run or prerun record exists, and `guard_bash.py:260-268` returns 2, i.e. **BLOCKED**.
- **Heredoc bodies:** both versions already flag these, so that is not new.

The continuation-join side effect (`stage_prerun.py:1517`) can only add hits. It still can't hide a line-2 run, because every `py` token is scanned.

**Bottom line:** the diagnosis of c1 is right. The fix (c4 as the negative, `archive/…-o1.md:52` as the citation) is refuted by a measurement already on disk. The comment-quote command above should be the negative. Record the false positive on multi-line quoted arguments as a known cost of the newline split. What would change my mind: HEAD returning `[]` on c4.

## Sources

(extract from answer)

## What was done with it

ACCEPTED (card 107-1, material session). The c4 escaped-quote negative was dropped before it ran; L4/L5 now use the
review's comment-quote shape (`echo x # "a<NL>py tools/stagexec.py run <plan><NL># "`): HEAD predicted 0, new code 1
(`tools/bench/selftest_stoprecord_offline_c107.py`, L4/L5). The false positive on a quoted multi-line argument (`git commit
-m "..<NL>py tools/stagexec.py run ..<NL>"`) is recorded as an INFO line in the same self-test and reported to judgement as an
open cost of the newline split (launched_py carries the same cost since 106-5). The other misses listed (`(py`, `$( )`,
`bash -c`, `cd tools &&`) are not changed: outside card 107-1.
