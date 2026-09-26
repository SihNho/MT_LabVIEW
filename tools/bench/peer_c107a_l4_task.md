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
