r"""selftest_prerun_diag - card chat-N1 (2): a VI-MODIFYING script is launch-gated like tools/recipes/stage_*.py
whatever its name (stage_prerun.is_vi_modifying: ast - imports stagekit AND calls a MODIFY_VERBS name).
No LabVIEW: fixtures are tiny .py files in a %TEMP% sandbox, records / stage runs / logs go to sandbox files, and
guard_bash is fed synthetic PreToolUse JSON exactly as the harness would. Tests the tools/ tree it sits in.

PREDICTION CONTRACT (all PASS):
  D1 modifying fixture: is_vi_modifying True, launch REFUSED without records, refusal names the classifier + records
  D2 same fixture with dry + prerun PASS records: launch ALLOWED
  D3 read-only fixture (imports stagekit, calls s.es / s.census only): ALLOWED without records
  D4 script calling connect() WITHOUT importing stagekit: not modifying (both conditions required)
  D5 tools/recipes/stage_*.py path: refused without records, allowed with both (unchanged); grep/cat of it = no launch
  D6 tools/bench/diag_c90_t0_step3b.py -> True; tools/bench/drive_m8_panelmin89b.py -> False
  D7 guard_bash end-to-end (bgrun launch of the modifying fixture, no records): exit 2, stderr names is_vi_modifying
  D8 the gate's own tooling (stage_prerun.py / stagekit.py) is never classified modifying
    py tools/bgrun.py --max-min 3 --log tools/bench/selftest_prerun_diag.log -- py -u tools/bench/selftest_prerun_diag.py
"""
import json, os, shutil, subprocess, sys                                            # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
SAND = os.path.join(os.environ.get("TEMP", "."), "prerun_diag_selftest_%d" % os.getpid())
os.makedirs(os.path.join(SAND, "tools", "recipes"), exist_ok=True)
ENV = {"PRERUN_RECORDS": os.path.join(SAND, "records.jsonl"), "STAGE_RUNS": os.path.join(SAND, "stage_runs.jsonl"),
       "PRERUN_LOG_DIR": SAND}
os.environ.update(ENV)
sys.path.insert(0, TOOLS)
import stage_prerun as SP   # noqa: E402
import protocol as P        # noqa: E402
G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("ok " if ok else "BAD", label, str(detail)[:300]), flush=True)


def fixture(name, body, sub=""):
    p = os.path.join(SAND, sub, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def launch(p):
    return "py tools/bgrun.py --max-min 5 --log x.log -- py -u \"{0}\"".format(p)


def records(p):
    SP.write_record("dry", p, "PASS", None)
    SP.write_record("prerun", p, "PASS", None)


MOD = fixture("diag_fake_mod.py", "import sys\nimport stagekit as K\ns = K.Stage('x')\ns.move_in(1, 2, (3, 4))\n"
                                  "s.connect(0, 1, 't', 0, 2, 'u')\n")
RO = fixture("diag_fake_ro.py", "import stagekit as K\ns = K.Stage('x')\nprint(s.es('a'), s.census())\n")
NOIMP = fixture("diag_fake_noimp.py", "import gscript as g\ndef connect(*a):\n    pass\nconnect(1)\n")
STG = fixture("stage_fake_x.py", "import stagekit as K\n", sub=os.path.join("tools", "recipes"))

ok, why = SP.check_launch(launch(MOD))
gate("D1 modifying fixture refused without records, names classifier + records",
     SP.is_vi_modifying(MOD) and not ok and "is_vi_modifying" in why and "no dry + prerun PASS record" in why
     and "connect" in why and "move_in" in why, why)
records(MOD)
ok, why = SP.check_launch(launch(MOD))
gate("D2 modifying fixture allowed with dry + prerun records", ok, why)
ok, why = SP.check_launch(launch(RO))
gate("D3 read-only stagekit fixture allowed without records", ok and not SP.is_vi_modifying(RO), why)
gate("D4 connect() without importing stagekit is not modifying", not SP.is_vi_modifying(NOIMP), SP.vi_modifying_calls(NOIMP))
ok1, why1 = SP.check_launch(launch(STG))
records(STG)
ok2, why2 = SP.check_launch(launch(STG))
gate("D5 stage_* unchanged: refused w/o records, allowed with; grep is no launch",
     not ok1 and "is_vi_modifying" not in why1 and ok2 and SP.launched_stage_scripts("grep x " + STG) == []
     and SP.launched_stage_scripts(launch(STG)) == [os.path.normpath(STG)], [why1[:120], why2])
d90 = os.path.join(HERE, "diag_c90_t0_step3b.py")
m89 = os.path.join(HERE, "drive_m8_panelmin89b.py")
gate("D6 diag_c90_t0_step3b.py -> True, drive_m8_panelmin89b.py -> False",
     SP.is_vi_modifying(d90) is True and SP.is_vi_modifying(m89) is False,
     [SP.vi_modifying_calls(d90), SP.vi_modifying_calls(m89)])
MOD2 = fixture("diag_fake_mod2.py", "import stagekit as K\nK.Stage('y').delete_wire(5)\n")
env = dict(os.environ, **ENV)
for k in ("LV_GUARD_OFF", "BENCH_CELL", "CYCLE_SESSION"):
    env.pop(k, None)
pr = subprocess.run([sys.executable, os.path.join(TOOLS, "hooks", "guard_bash.py")], input=json.dumps(
    {"session_id": "selftest-prerun-diag", "tool_name": "Bash",
     "tool_input": {"command": "MATERIAL=1 " + launch(MOD2), "run_in_background": True}}),
    text=True, capture_output=True, encoding="utf-8", errors="replace", timeout=60, env=env, cwd=ROOT)
gate("D7 guard_bash refuses the modifying fixture launch (exit 2, classifier named)",
     pr.returncode == 2 and "is_vi_modifying" in (pr.stderr or ""), "exit %d %s" % (pr.returncode, (pr.stderr or "")[:200]))
gate("D8 the gate's own tooling is not classified",
     not SP.is_vi_modifying(os.path.join(TOOLS, "stage_prerun.py")) and not SP.is_vi_modifying(os.path.join(TOOLS, "stagekit.py")))
gate("D9 MODIFY_VERBS listed (%d verbs)" % len(SP.MODIFY_VERBS), len(SP.MODIFY_VERBS) >= 15, sorted(SP.MODIFY_VERBS))
shutil.rmtree(SAND, ignore_errors=True)
npass = sum(1 for _, o in G if o)
print("SUMMARY %d/%d gates pass" % (npass, len(G)), flush=True)
first = next((l for l, o in G if not o), None)
print(P.result_line(P.make_result(npass, len(G) - npass, first)), flush=True)
sys.exit(0 if first is None else 1)
