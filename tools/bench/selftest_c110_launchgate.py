r"""selftest_c110_launchgate - card 110-1 G1 (docs/violation-decisions.md device-failed 15:49, :1552-1554). No LabVIEW.
L1  the literal material_marker.log:2422 command (`cd <root> && wc -l <recipe> && py -m pyflakes <recipe> 2>&1 | head;`)
    returns NO launch unit from stage_prerun.launched_py / launched_stage_scripts (py -m <module> launches the module)
L2  `py -u tools/recipes/stage_x.py` is still a launch
L3  `py tools/bgrun.py --material ... -- py -u tools/recipes/stage_x.py` is still a launch
H1  guard_bash.prerun_gate passes the literal command (rc 0); H2/H3 still refuse the L2/L3 launches (stage_x.py absent)
H4  guard_bash._lint_stripped drops the pyflakes segment of the literal command and leaves a launch command unchanged"""
import os, sys                                                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "hooks")):
    sys.path.insert(0, p)
os.chdir(ROOT)
import guard_bash as GB, stage_prerun as SP, protocol                              # noqa: E401,E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


GB.note = lambda *a, **k: None                                                     # no marker-log line from a test
GB._CUR_TOOL[0] = "Bash"
LIT = ('cd "{0}" && wc -l tools/recipes/stage_d1_l2a3.py && py -m pyflakes tools/recipes/stage_d1_l2a3.py 2>&1 | head;'
       .format(ROOT.replace("\\", "/")))
X = "tools/recipes/stage_x.py"
L2 = "py -u " + X
L3 = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u " + X
gate("L1 marker:2422 literal -> no launch unit", SP.launched_py(LIT) == [] and SP.launched_stage_scripts(LIT) == [],
     SP.launched_py(LIT))
gate("L1b compact -mpyflakes -> no launch unit", SP.launched_py("py -mpyflakes " + X) == [])
gate("L2 py -u stage_x.py is a launch", len(SP.launched_stage_scripts(L2)) == 1, SP.launched_stage_scripts(L2))
gate("L3 bgrun -- py -u stage_x.py is a launch", len(SP.launched_stage_scripts(L3)) == 1, SP.launched_stage_scripts(L3))
gate("L4 py -m pyflakes X && py -u X still a launch", len(SP.launched_stage_scripts("py -m pyflakes {0} && py -u {0}".format(X))) == 1)
gate("L5 py -X utf8 -u X still a launch (flag with argument)", len(SP.launched_stage_scripts("py -X utf8 -u " + X)) == 1)
gate("H1 prerun_gate(literal) == 0", GB.prerun_gate(LIT) == 0)
gate("H2 prerun_gate(L2) == 2", GB.prerun_gate(L2) == 2)
gate("H3 prerun_gate(L3) == 2", GB.prerun_gate(L3) == 2)
s = GB._lint_stripped(LIT)
gate("H4 _lint_stripped drops pyflakes, keeps launch cmds verbatim",
     "pyflakes" not in s and GB._lint_stripped(L3) == L3 and GB._lint_stripped(L2) == L2, s)
npass = sum(1 for _l, ok in G if ok)
nfail = len(G) - npass
ff = next((lab for lab, ok in G if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(npass, nfail))
print(protocol.result_line(protocol.make_result(npass, nfail, ff)), flush=True)
sys.exit(0 if nfail == 0 else 1)
