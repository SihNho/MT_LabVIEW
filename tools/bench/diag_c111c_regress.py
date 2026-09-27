r"""diag_c111c_regress - card 111-3 D5: the existing OFFLINE self-tests of the edited files (stage_prerun.py, stagexec.py,
stop_record.py, hooks/guard_card.py -> protocol card flags) re-run after the edit, each compared with its LATEST archived log
(the pre-edit run) by gate NAME and COUNT. Nothing here opens LabVIEW; every child is an offline self-test that sandboxes its
records in %TEMP% (selftest_launch_gate.py:4, selftest_prerun_diag.py:23). NOT RUN here: selftest_stage_prerun_c110g.py
(it imports gscript, selftest_stage_prerun_c110g.py:33 - card 111-3 flags.labview 'none' refuses it; not routed around) and
`tools/stagexec.py selftest` (run on its own, the guard_card pure-selftest command form).
PREDICTION: R1 every test exits with the same gate NAMES as its baseline log and no gate that passed there fails now.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c111c_regress.log -- py -u tools/bench/diag_c111c_regress.py"""
import os, re, subprocess, sys                                                    # noqa: E401
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS); B = os.path.join(TOOLS, "bench")   # noqa: E702
sys.path.insert(0, TOOLS)
import protocol as P                                                              # noqa: E402
print(__doc__, flush=True)
TESTS = [("selftest_stage_prerun_c103.py", "selftest_stage_prerun_c103_c110g.log"),
         ("selftest_stage_prerun_c106c.py", "selftest_stage_prerun_c106c_c110g.log"),
         ("selftest_stage_prerun_c106e.py", "selftest_stage_prerun_c106e_c110g.log"),
         ("selftest_stage_prerun_graphload.py", "selftest_stage_prerun_graphload_c110g.log"),
         ("selftest_stage_prerun_headcmp_79-6.py", "selftest_stage_prerun_headcmp_c110g.log"),
         ("selftest_stage_prerun_stageplan.py", "selftest_stage_prerun_stageplan_c110g.log"),
         ("selftest_c110_launchgate.py", "selftest_c110_launchgate.log"),
         ("selftest_launch_gate.py", "selftest_launch_gate_c110.log"),
         ("selftest_prerun_diag.py", "selftest_prerun_diag_c110.log"),
         ("selftest_c106d_tools.py", "selftest_c106d_tools_c110.log"),
         ("selftest_c103d_hooks.py", "selftest_c103d_hooks_c110.log"),
         ("selftest_c108e_tools.py", "selftest_c108e_tools.log"),
         ("selftest_stoprecord_offline_c107.py", "selftest_stoprecord_offline_c107.log"),
         ("selftest_stoprecord_table.py", "selftest_stoprecord_table.log"),
         ("selftest_stoprecord_bgrun.py", "selftest_stoprecord_bgrun_c73.log"),
         ("selftest_stoprecord_eqform.py", "selftest_stoprecord_eqform_c73.log"),
         ("selftest_stoprecord_supersession.py", "selftest_stoprecord_supersession_c73.log"),
         ("selftest_protocol.py", "selftest_protocol.log"),
         ("selftest_protocol_wiring.py", "selftest_protocol_wiring.log"),
         ("selftest_requires.py", "selftest_requires.log"),
         ("selftest_retry_cap.py", "selftest_retry_cap.log"),
         ("selftest_stagexec_gate.py", "selftest_stagexec_gate.log")]
GATE_RE = re.compile(r"^\s*(?:\[\s*)?(PASS|FAIL|OK|ok|FAILED)\b\]?[\s:|-]+(.{0,70})", re.M)
GATE2_RE = re.compile(r"^GATE (.{1,72}?)\s+(PASS|FAIL)\b", re.M)                  # selftest_stoprecord_offline_c107.py:24


def _name(n):
    """The gate LABEL: the text before the first run of 2+ spaces (the detail), hex runs and digits masked."""
    n = re.split(r"\s{2,}", n.strip())[0]
    return re.sub(r"\d+", "#", re.sub(r"\b[0-9a-f]{6,}\b", "#", n))[:60]


def gates(text):
    """[(verdict, name)] - PASS/FAIL gate lines of either format."""
    a = [("PASS" if v.upper() in ("PASS", "OK") else "FAIL", _name(n)) for v, n in GATE_RE.findall(text)]
    return a + [(v, _name(n)) for n, v in GATE2_RE.findall(text)]


def last_run(text):
    i = text.rfind("BGRUN START")
    return text[i:] if i >= 0 else text


G = []
for t, base in TESTS:
    bp = os.path.join(B, base)
    b = gates(last_run(open(bp, encoding="utf-8", errors="replace").read())) if os.path.exists(bp) else None
    try:
        r = subprocess.run([sys.executable, "-u", os.path.join(B, t)], cwd=ROOT, capture_output=True, text=True, timeout=300,
                           encoding="utf-8", errors="replace")
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired:
        out, rc = "TIMEOUT", -9
    n = gates(out)
    open(os.path.join(B, "diag_c111c_regress_" + t.replace(".py", ".log")), "w", encoding="utf-8").write(out)
    nf = sorted(set(x for v, x in n if v == "FAIL")); bf = sorted(set(x for v, x in (b or []) if v == "FAIL"))
    newfail = [x for x in nf if x not in bf]
    missing = sorted(set(x for _v, x in (b or [])) - set(x for _v, x in n)); added = sorted(set(x for _v, x in n) - set(x for _v, x in (b or [])))
    ok = rc != -9 and not newfail and (b is None or not missing) and len(n) > 0
    store_dep = t == "selftest_stoprecord_offline_c107.py"          # reads the REAL store + git HEAD: judged by R2 below
    if not store_dep:
        G.append(ok)
    print("  {0}  R1 {1}: now {2}/{3} (rc {4}) | base {5} {6}/{7} | new fails {8} | missing {9} | added {10}".format(
        ("PASS" if ok else "FAIL") if not store_dep else "INFO", t, sum(1 for v, _ in n if v == "PASS"), sum(1 for v, _ in n if v == "FAIL"), rc, base,
        None if b is None else sum(1 for v, _ in b if v == "PASS"), None if b is None else sum(1 for v, _ in b if v == "FAIL"),
        newfail[:5], missing[:5], added[:5]), flush=True)
# R2 HEAD CONTROL for the store-dependent suite (selftest_stoprecord_offline_c107.py:46-53 reads the REAL stop-record store):
# the same launch commands through HEAD's stop_record (git show) and through the edited one must get the same verdict.
import importlib.util, tempfile                                                   # noqa: E401,E402
hp = os.path.join(tempfile.mkdtemp(prefix="c111c_rg_"), "stop_record_head.py")
open(hp, "wb").write(subprocess.run(["git", "show", "HEAD:tools/stop_record.py"], cwd=ROOT, capture_output=True, check=True).stdout)
sp = importlib.util.spec_from_file_location("stop_record_head", hp); HSR = importlib.util.module_from_spec(sp); sp.loader.exec_module(HSR)   # noqa: E702
HSR.ROOT, HSR.HERE = ROOT, TOOLS
import stop_record as SR                                                          # noqa: E402
# review archive/peer/2026-09-27-c111c-regress.md s49-57 (ACCEPTED): the live store holds no refusing record for this
# recipe, so HEAD == NEW on check_command would be vacuous. The store is replaced by selftest_c103d_hooks.py:23's fake
# (refuse iff a 'build' segment names tools/recipes/), evaluated with EACH module's own segment_class.
fake = lambda M, c: not any(M.segment_class(s, c) == "build" and M.RECIPE_DIR_RE.search(s) for s in M.split_segments(c))   # noqa: E731
R = "tools/recipes/stage_d1_disp.py"
CMDS = ["py tools/bgrun.py --material --max-min 40 --log x.log -- py -u %s" % R, "py -u %s" % R,
        "py tools/stage_prerun.py --dry %s && py -u %s" % (R, R), "py tools/stage_prerun.py --dry %s\npy -u %s" % (R, R),
        "py tools/stage_prerun.py --dry %s | py -" % R, "py tools/stage_prerun.py --dry $(py -u %s)" % R,
        "py tools/other_tool.py --dry %s" % R, "py tools/stage_prerun.py --graph x.json %s" % R, "py -m mymod %s" % R,
        "py -m mprof run %s" % R, "py -m streamlit run %s" % R, "py -m pyflakes %s && py -u %s" % (R, R),
        "PYTHONPATH=tools/bench py -m pyflakes %s" % R, "py -m pyflakes %s & cmd /c \"py %s\"" % (R, R)]
cmp_ = [(c[:44], fake(HSR, c), fake(SR, c)) for c in CMDS]
okc = all(h == n is False for _c, h, n in cmp_)
G.append(okc)
print("  {0}  R2 HEAD control (fake refusing store): every launch shape REFUSED by HEAD and by NEW {1}".format(
    "PASS" if okc else "FAIL", cmp_), flush=True)
LIT = 'cd "/g/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop" && py -m pyflakes %s; echo "pyflakes rc=$?"' % R
okl = fake(HSR, LIT) is False and fake(SR, LIT) is True
G.append(okl)
print("  {0}  R2b the ONE intended difference: material_marker.log:2434's lint refused by HEAD, allowed by NEW ({1}, {2})".format(
    "PASS" if okl else "FAIL", fake(HSR, LIT), fake(SR, LIT)), flush=True)
npass = sum(G); nfail = len(G) - npass
print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
print(P.result_line(P.make_result(npass, nfail, None if not nfail else "R1 regression", status="PASS" if not nfail else "FAIL")), flush=True)
sys.exit(0 if not nfail else 1)
