r"""diag_c111c_realstore - card 111-3 D5, review archive/peer/2026-09-27-c111c-stageplan.md s60-64 (ACCEPTED): is
selftest_stoprecord_offline_c107.py's 15/10 (diag_c111c_regress2.log:23, archived 25/0) store drift or the edit?
OFFLINE: offline_c107's own command list (selftest_stoprecord_offline_c107.py:39-53) through HEAD's stop_record (git show
HEAD:tools/stop_record.py) and the edited one, both on the REAL store tools/bench/stop_records.json, save_records disabled
(nothing is stamped). Also the HEAD vs working launched_plan_runs for its L4 (the function was not edited by card 111-3).
PREDICTION: S1 every command gets the SAME allow/refuse verdict from HEAD and NEW (=> the 10 fails are store drift);
S2 the store holds no undisposed record for tools/recipes/stage_d1_disp.py (why N1-N8 are allowed by both); S3 launched_plan_runs
source is byte-identical in HEAD and the working copy.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c111c_realstore.log -- py -u tools/bench/diag_c111c_realstore.py"""
import importlib.util, json, os, subprocess, sys, tempfile                      # noqa: E401
TOOLS = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); ROOT = os.path.dirname(TOOLS)   # noqa: E702
sys.path.insert(0, TOOLS)
import stop_record as SR, protocol as P                                           # noqa: E401,E402
print(__doc__, flush=True)
G = []


def gate(lab, ok, det=""):
    G.append(bool(ok)); print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(det)[:1500]), flush=True)   # noqa: E702


def head_src(rel):
    return subprocess.run(["git", "show", "HEAD:" + rel], cwd=ROOT, capture_output=True, check=True).stdout


hp = os.path.join(tempfile.mkdtemp(prefix="c111c_rs_"), "stop_record_head.py"); open(hp, "wb").write(head_src("tools/stop_record.py"))   # noqa: E702
sp = importlib.util.spec_from_file_location("stop_record_head", hp); HSR = importlib.util.module_from_spec(sp); sp.loader.exec_module(HSR)   # noqa: E702
HSR.ROOT, HSR.HERE, HSR.STORE = ROOT, TOOLS, SR.STORE
SR.save_records = HSR.save_records = lambda recs: None
R = "tools/recipes/stage_d1_disp.py"; rq = '"%s"' % ROOT.replace("\\", "/")        # noqa: E702
CMDS = {"P1": "py tools/stage_prerun.py --dry %s --from-step 33" % R,
        "P2": "py tools/bgrun.py --material --max-min 8 --log tools/bench/x.log -- py -u tools/stage_prerun.py --dry %s --from-step 33" % R,
        "P3": "py -u tools/stage_prerun.py --prerun %s --stop-after 40" % R,
        "P4": "cd %s && py tools\\stage_prerun.py --dry tools\\recipes\\stage_d1_disp.py" % rq,
        "P5": "MATERIAL=1 py tools/bgrun.py --max-min 8 --log x.log -- py -u tools/stage_prerun.py --dry %s" % R,
        "N1": "py tools/bgrun.py --material --max-min 40 --log x.log -- py -u %s" % R, "N2": "py -u %s" % R,
        "N3": "py tools/stage_prerun.py --dry %s && py -u %s" % (R, R), "N4": "py tools/stage_prerun.py --dry %s\npy -u %s" % (R, R),
        "N5": "py tools/stage_prerun.py --dry %s | py -" % R, "N6": "py tools/stage_prerun.py --dry $(py -u %s)" % R,
        "N7": "py tools/other_tool.py --dry %s" % R, "N8": "py tools/stage_prerun.py --graph x.json %s" % R}
rows = dict((k, (HSR.check_command(c)[0], SR.check_command(c)[0])) for k, c in CMDS.items())
for k, c in CMDS.items():                                                         # a differing verdict: both messages + classes
    if rows[k][0] != rows[k][1]:
        print("  FACT {0} HEAD: {1!r}\n  FACT {0} NEW : {2!r}\n  FACT {0} classes HEAD {3} NEW {4}".format(
            k, HSR.check_command(c)[1][:600], SR.check_command(c)[1][:600], HSR.command_keys(c), SR.command_keys(c)), flush=True)
rows2 = dict((k, (HSR.check_command(c)[0], SR.check_command(c)[0])) for k, c in CMDS.items())
print("  FACT second pass (order effects?) {0}".format(rows2), flush=True)
gate("S1 real store: every offline_c107 command gets the same verdict from HEAD and NEW (allow?)", all(h == n for h, n in rows.values()), rows)
recs = [r for r in json.load(open(SR.STORE, encoding="utf-8")) if "stage_d1_disp" in str(r.get("recipe_path"))]
states = [SR.record_state(SR.load_records(), i)[1] for i, r in enumerate(SR.load_records()) if "stage_d1_disp" in str(r.get("recipe_path"))]
gate("S2 the real store holds no refusing record for {0} ({1} record(s), states {2})".format(R, len(recs), sorted(set(states))),
     rows["N2"] == (True, True), {"released": [bool(r.get("released")) for r in recs]})


def fn_src(text, name):
    s = text.split("def %s(" % name, 1)[1]
    return s.split("\ndef ", 1)[0]


cur = open(os.path.join(TOOLS, "stage_prerun.py"), encoding="utf-8").read()
hd = head_src("tools/stage_prerun.py").decode("utf-8")
gate("S3 launched_plan_runs is unchanged by card 111-3 (HEAD == working copy); offline_c107 L4 reads HEAD's copy",
     fn_src(cur, "launched_plan_runs") == fn_src(hd, "launched_plan_runs"))
npass = sum(G); nfail = len(G) - npass
print("=== GATES: {0} pass / {1} fail".format(npass, nfail), flush=True)
print(P.result_line(P.make_result(npass, nfail, None if not nfail else "S realstore", status="PASS" if not nfail else "FAIL")), flush=True)
sys.exit(0 if not nfail else 1)
