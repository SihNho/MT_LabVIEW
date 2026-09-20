FAILED PREDICTION in tools/bench/selftest_cycle_runner_ff.py (log tools/bench/selftest_cycle_runner_ff.log, 11:28):
predicted the dry runner would log FAILED-RECIPES for cycles 1-2 and a FIREFIGHTER line for cycle 3; observed both
modes ended "exit 2" on cycle 1 and 2 immediately (0 s) and RUNNER STOP "exited non-zero twice".

My explanation: `tools/cycle_runner.py` splits `--dry-cmd` on whitespace (docstring line: "Whitespace-split, so it
carries no path with a space in it"), and the self-test passed `sys.executable` + an ABSOLUTE path under
`G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\...` - which contains spaces -
so the stand-in command was mangled and py exited 2 ("can't open file"). Fix applied: pass
`py tools/bench/selftest_cycle_runner_ff.py <mode>` (relative, cwd=ROOT).

Already ruled out: the firefighter code path itself was never reached (no FAILED-RECIPES line, cycles took 0 s);
the fake-log writer needs env FF_BENCH, which the test sets.

Attack this: what else would produce exit 2 in 0 s for both modes? Would the relative-path fix still fail on
this Windows/Git-Bash setup (py launcher, cwd handling in subprocess.run with cwd=ROOT)? Name the cheapest
discriminating test. Also: is "trigger = same recipe basename with BGRUN END rc!=0 / TIMEOUT in two consecutive
cycle windows, by log mtime" a sound trigger, or can a log written by a DIAGNOSTIC (not a build) or a re-run of
an old log fire it falsely?
