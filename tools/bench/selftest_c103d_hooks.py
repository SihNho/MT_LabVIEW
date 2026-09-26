r"""selftest_c103d_hooks - card 103-4 pass lines 2 (no LabVIEW, no model).
S  guard_bash.stop_gate: the material_marker.log:2175 command (`wc -l <stopped recipe> && py -m pyflakes <it> 2>&1 | head`) is
   READ-ONLY and passes; a command that EXECUTES the stopped recipe (direct, under bgrun, after a lint segment, lint piped into
   `py -`) is still refused. The stop store is replaced by a fake whose rule is stop_record's own (segment_class 'build' on a
   tools/recipes/ path = refuse), so the test does not depend on the live records.
L  stage_prerun launch gate: tools/bench/selftest_stagekit.py (offline, imports stagekit) is not a VI-modifying launch; the SAME
   bytes under another path still are (the exemption is by path, not by content)."""
import os, shutil, sys, tempfile                                                   # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
os.chdir(ROOT)
import stop_record as SR, guard_bash as GB, stage_prerun as SP, protocol          # noqa: E401,E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


GB.note = lambda *a, **k: None                                                     # no marker-log line from a test
SR.check_command = lambda c: (not any(SR.segment_class(s, c) == "build" and SR.RECIPE_DIR_RE.search(s)
                                      for s in SR.split_segments(c)), "fake-refusal\n")
R = "tools/recipes/stage_d1_disp.py"
for lab, cmd, want in (
        ("S1 marker:2175 wc + pyflakes piped to head passes", "wc -l {0} && py -m pyflakes {0} 2>&1 | head -20".format(R), 0),
        ("S2 py -m pycodestyle alone passes", "py -m pycodestyle {0}".format(R), 0),
        ("S3 NEGATIVE direct launch refused", "py -u {0}".format(R), 2),
        ("S4 NEGATIVE bgrun launch refused", "py tools/bgrun.py --material --max-min 5 --log x.log -- py -u {0}".format(R), 2),
        ("S5 NEGATIVE lint then launch refused", "py -m pyflakes {0} && py {0}".format(R), 2),
        ("S6 NEGATIVE lint piped into py - refused", "py -m pyflakes {0} | py -".format(R), 2),
        ("S7 NEGATIVE unknown module refused", "py -m mymod {0}".format(R), 2),
        # archive/peer/2026-09-27-c103d-hooks-before.md s6 (accepted): N1-N4 + the cd rule
        ("S8 marker:2175 verbatim shape (cd to the project root first) passes",
         'cd "{0}" && wc -l {1} && py -m pyflakes {1} 2>&1 | head -20'.format(ROOT.replace("\\", "/"), R), 0),
        ("N1 NEGATIVE escaped-quote newline smuggles a launch", 'py -m pyflakes \\"x\npy -u {0}\n\\"'.format(R), 2),
        ("N2 NEGATIVE env prefix (PYTHONPATH hijack) refused", "PYTHONPATH=tools/bench py -m pyflakes {0}".format(R), 2),
        ("N3 NEGATIVE flake8 (config plugins) refused", "py -m flake8 --config=x.cfg {0}".format(R), 2),
        ("N4 NEGATIVE pytest -m pyflakes refused", "pytest -m pyflakes {0}".format(R), 2),
        ("N5 NEGATIVE cd elsewhere then lint refused", "cd tools/bench/sim/disp && py -m pyflakes ../../../../{0}".format(R), 2)):
    got = GB.stop_gate(cmd)
    gate(lab, got == want, "rc {0}".format(got))
st = os.path.join(ROOT, "tools", "bench", "selftest_stagekit.py")
gate("L1 selftest_stagekit.py is not a VI-modifying launch", not SP.launched_vi_modifying(
    "py tools/bgrun.py --material --max-min 3 --log x.log -- py -u tools/bench/selftest_stagekit.py"), SP.vi_modifying_calls(st))
tmp = os.path.join(tempfile.gettempdir(), "c103d_copy_of_selftest_stagekit.py")
shutil.copyfile(st, tmp)
gate("L2 NEGATIVE the same bytes under another path are still VI-modifying", SP.is_vi_modifying(tmp), SP.vi_modifying_calls(tmp))
os.remove(tmp)
pin0 = dict(SP.VI_MOD_EXEMPT_PATHS)
SP.VI_MOD_EXEMPT_PATHS = dict((k, "0" * 64) for k in pin0)                         # other bytes at the exempt path
gate("L4 NEGATIVE other bytes at the exempt path are VI-modifying again (sha256 pin)", SP.is_vi_modifying(st), SP.vi_modifying_calls(st))
SP.VI_MOD_EXEMPT_PATHS = pin0
gate("L3 NEGATIVE a real stage recipe is still a stage launch", SP.launched_stage_scripts("py -u " + R), R)
n = sum(1 for _l, ok in G if ok)
print("=== GATES: {0} pass / {1} fail".format(n, len(G) - n))
print(protocol.result_line(protocol.make_result(n, len(G) - n, next((l for l, ok in G if not ok), None))))
sys.exit(0 if n == len(G) else 1)
