r"""Self-test for card chat-P2 (user 2026-09-28 "그렇게 1~4번 적용하여 수정하면 되겠음"): speed items 1-4.
Touches NO LabVIEW, spawns NO agents, calls NO network. The Error List reader and gscript are replaced by in-process
fakes; guard_session is fed synthetic payloads (throwaway session ids, deleted at the end); cards live in a temp dir.

PREDICTION CONTRACT (every gate below must hold):
  U1-U5  item 1: docs/user-rules.md has rows U1..U13, each with a quote, a date and a source; prior_art_review.build_task
         carries the file in full and the fixed contradiction question; an absent file is SAID in the task;
         `user-rule-contradicted` is a blocking prior-art slug and the question's own menu line is not an answer
  N1-N2  item 1: a recipe with a create class no clean stage ran -> new_structure_classes names it and it is NOT proven;
         once two clean stages carry it -> no new class
  L1-L2  item 1: doc_lint L9 warns on Pre-decided items >= 238 without `USER-RULES:` (a deeper sub-heading stays inside
         the section) and passes items < 238 and items carrying the line
  A1-A6  item 2: bound 61 min ago, a NEW bgrun launch of a recipe is refused (SOFT ALERT); a read, a self-test under
         bgrun and a 30-min-old card are not; a re-bind keeps first_bound; the real hook path refuses through bind()
  E1-E4  item 3: errorlist_check --count-only --role scratch with matching class counts = ONE read without the
         double-click; with an extra item the FULL read follows at once; --role final refuses count-only (full read);
         the default is a full read
  S1-S6  item 4: an escalation card whose failure repeats the previous attempt's function -> scratch-verify; a different
         function -> escalate; a newer scratch PASS -> escalate; the stage-run route; guard_session refuses the
         escalation rung (exit 2) and lets the same card go to `material`
Output avoids a line starting with FAIL; ends with a RESULT line.
"""
import contextlib
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
HOOKS = os.path.join(TOOLS, "hooks")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HOOKS)
TMP = tempfile.mkdtemp(prefix="p2st_")
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("BENCH_CELL", None)
import protocol as P  # noqa: E402

RES, SIDS = [], []
GS = os.path.join(HOOKS, "guard_session.py")
CARD_P2 = os.path.join(TOOLS, "bench", "cards", "task_chat-P2.json")


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-62s %s" % ("ok" if ok else "BAD", label, str(detail)[:150]), flush=True)


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    return path


# ------------------------------------------------------------------------------------------------ U user rules
def t_user_rules():
    import re
    body = open(os.path.join(ROOT, "docs", "user-rules.md"), encoding="utf-8").read()
    rows = re.findall(r"^\| (U\d+) \|([^|]*)\|([^|]*)\|([^|]*)\|([^|]*)\|$", body, re.M)
    ids = [r[0] for r in rows]
    gate("U1 user-rules.md rows U1..U13, each quote + date + source", ids == ["U%d" % i for i in range(1, 14)] and all(
        '"' in r[2] and re.search(r"2026-\d\d-\d\d", r[3]) and r[4].strip() for r in rows), ids)
    import prior_art_review as PA
    task = PA.build_task("PLAN: put a queue between loop 1.1 and 1.2", "new-op", False)
    gate("U2 build_task carries user-rules.md in full + the fixed question", "docs/user-rules.md IN FULL" in task and
         "| U13 |" in task and "Does this plan contradict any rule in user-rules.md? Name the rule and the plan line."
         in task, len(task))
    t2 = PA.build_task("x", rules_path=os.path.join(TMP, "absent.md"))
    gate("U3 an absent user-rules.md is SAID in the task", "ABSENT" in t2, t2[t2.find("user-rules"):][:60])
    import guard_cycle as GC
    ans = "## Answer\nC1: plan line 4 puts a queue on a control signal, rule U4.\nPRIOR-ART: user-rule-contradicted\n"
    found = [s for s in GC.PRIOR_ART_RE.findall(ans) if s in GC.PRIOR_ART_SLUGS and s != "novel"]
    gate("U4 `user-rule-contradicted` is a blocking prior-art slug", found == ["user-rule-contradicted"], found)
    menu = [s for s in GC.PRIOR_ART_RE.findall(PA.QUESTIONS)]
    gate("U5 the question's own menu lines are not answers (indented)", menu == [], menu)


# ------------------------------------------------------------------------------------------------ N new structure
def clean_log(path, ok=True):
    with open(path, "w", encoding="utf-8") as f:
        f.write("BGRUN START 2026-09-28 09:00:00 limit 30.0 min: py -u tools/recipes/stage_x.py\n")
        f.write(P.result_line(P.make_result(5 if ok else 4, 0 if ok else 1, None if ok else "G3")) + "\n")
        f.write("BGRUN END rc=%d after 60s\n" % (0 if ok else 1))
    return path


def t_new_structure():
    import stage_prerun as SP
    rdir = os.path.join(TMP, "ns", "tools", "recipes")
    os.makedirs(rdir)
    rec = os.path.join(rdir, "stage_p2new.py")
    open(rec, "w").write("import stagekit as K, stagexec as SX\nPLAN = 'plan_p2ns.json'\nx = SX.Executor(PLAN)\n"
                         "K.run(x, None)\n")
    wj(os.path.join(rdir, "plan_p2ns.json"), {"schema": "stageplan/1", "stage": "p2ns", "actions": [
        {"op": "wire", "src": "1.a", "dst": "2.b"}, {"op": "create", "class": "Queue", "diagram": 3}]})
    sig = SP.pattern_signature(rec)
    old = [x for x in sig if x != "create:Queue"] + ["op:tunnel"]
    a, b = clean_log(os.path.join(TMP, "ns", "a.log")), clean_log(os.path.join(TMP, "ns", "b.log"))
    runs = [{"by": "bgrun", "stage": "stage_a.py", "pattern": old, "log": a},
            {"by": "bgrun", "stage": "stage_b.py", "pattern": old, "log": b}]
    new = SP.new_structure_classes(rec, runs=runs, recs=[])
    pp = SP.proven_pattern(rec, runs=runs, recs=[])
    gate("N1 a create class no clean stage ran is named NEW and not proven", new == ["create:Queue"] and not pp[0],
         (new, pp[0]))
    runs2 = [dict(r, pattern=sig + ["op:tunnel"]) for r in runs]
    gate("N2 once two clean stages carry it: no new class, proven", SP.new_structure_classes(rec, runs=runs2, recs=[])
         == [] and SP.proven_pattern(rec, runs=runs2, recs=[])[0], SP.new_structure_classes(rec, runs=runs2, recs=[]))


# ------------------------------------------------------------------------------------------------ L doc_lint L9
def t_lint():
    import doc_lint as DL
    p = os.path.join(TMP, "plan_l9.md")
    open(p, "w", encoding="utf-8").write(
        "---\ntype: plan\nstatus: current\ndate: 2026-09-28\n---\n# x\n## Pre-decided\n"
        "237. **old item** no line\n   more text\n"
        "238. **new design** without the line\n"
        "239. **new design** with it\n   USER-RULES: U4, U13\n"
        "### sub-heading inside\n"
        "240. **after the sub-heading** no line\n"
        "241. **none** \n   USER-RULES: none apply\n"
        "## Other section\n"
        "242. not a Pre-decided item\n")
    miss = DL.check_user_rules_lines([p])
    nums = [m.split("(item ")[1].rstrip(")") for m in miss]
    gate("L1 L9 names items 238 and 240 only (>= 238, no line; sub-heading kept inside)", nums == ["238", "240"], miss)
    lvl = [r[0] for r in DL.RESULT if r[1].startswith("L9")]
    gate("L2 L9 is WARN-only", lvl and lvl[-1] == "WARN", lvl)


# ------------------------------------------------------------------------------------------------ A soft alert
def t_soft_alert():
    recipe = "tools/recipes/stage_d1_s2.py"
    c = json.load(open(CARD_P2, encoding="utf-8"))
    c["flags"] = dict(c["flags"], labview="build", gui=True, run_vi=True)
    c.pop("requires", None)
    old = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 61 * 60))
    young = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 30 * 60))
    launch = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u %s" % recipe
    why = P.check_command(dict(c, _bound=old), launch)
    gate("A1 61 min: a NEW bgrun recipe launch is refused (SOFT ALERT)", why and "SOFT ALERT" in why and
         "finish the running step" in why.lower(), (why or "")[:90])
    why = P.check_command(dict(c, _bound=old), "grep -n def %s" % recipe)
    gate("A2 61 min: a read of the same file is not refused", why is None, why)
    why = P.check_command(dict(c, _bound=old), "py tools/bgrun.py --material --max-min 5 --log tools/bench/y.log -- "
                                               "py -u tools/bench/selftest_chat_p2.py")
    gate("A3 61 min: a self-test under bgrun is not refused", why is None, why)
    why = P.check_command(dict(c, _bound=young), launch)
    gate("A4 30 min: the same launch passes the soft alert", not (why and "SOFT ALERT" in why), why)
    act = os.path.join(TMP, "active_a.json")
    saved = P.ACTIVE
    P.ACTIVE = act
    try:
        ok1, _m = P.bind("agt-p2-a", "material", CARD_P2)
        d = json.load(open(act, encoding="utf-8"))
        d["agt-p2-a"]["first_bound"] = old
        json.dump(d, open(act, "w", encoding="utf-8"))
        ok2, _m = P.bind("agt-p2-a", "material", CARD_P2)
        b = P.binding("agt-p2-a")
        gate("A5 a re-bind to the same card keeps first_bound", ok1 and ok2 and b.get("first_bound") == old
             and b.get("bound") != old, b)
        ok, msg = P.hook_decision({"agent_id": "agt-p2-a", "agent_type": "material", "tool_name": "Bash",
                                   "tool_input": {"command": launch}})
        gate("A6 the real hook path refuses through bind()'s clock", not ok and "SOFT ALERT" in (msg or ""),
             (msg or "")[:90])
    finally:
        P.ACTIVE = saved


# ------------------------------------------------------------------------------------------------ E Error List count-only
class _FakeG(object):
    CLAUDEDEV = None

    def open_panel(self, *a):
        pass

    def close_panel(self, *a):
        pass

    def exec_state(self, *a):
        return 0

    def ref_counts(self):
        return {"live": 0}

    def _lv_gui(self, *a):
        pass


class _FakeE(object):
    SHOTS = None

    def __init__(self, raws):
        self.raws, self.calls = raws, []

    def read(self, vi, out_json=None, log=print, on_item=None, max_steps=None, **k):
        self.calls.append({"out": out_json, "on_item": on_item is not None})
        items = []
        for i, r in enumerate(self.raws):
            it = {"index": i, "raw": r, "detail": ""}
            if on_item is not None:
                it["show_error"] = {"diagram_fronted": True}
            items.append(it)
        return {"method": "fake", "n_reported": len(items), "items": items, "closed_with_esc": True,
                "window": {"title": "Error list"}, "errors": []}


def run_ec(raws, argv_extra):
    import errorlist_check as EC
    d = os.path.join(TMP, "ec_%d" % len(RES))
    os.makedirs(d)
    bed = os.path.join(d, "bedp2.vi")
    open(bed, "wb").write(b"not a vi")
    exp = wj(os.path.join(d, "exp.json"), {"expected": [{"match": "wire has loose ends", "count": 2},
                                                        {"match": "is not wired", "count": 1}]})
    g, e = _FakeG(), _FakeE(raws)
    g.CLAUDEDEV, e.SHOTS = d, d
    saved = (EC.g, EC.E, EC.labview_handles, EC.labview_up, EC.vi_ready, EC.open_diagram, EC.BENCH, sys.argv)
    EC.g, EC.E, EC.labview_handles = g, e, (lambda: 100)
    EC.labview_up, EC.vi_ready, EC.open_diagram = (lambda R: 100), (lambda s, R: None), (lambda s, R: True)
    EC.BENCH, sys.argv = d, ["errorlist_check.py", "--vi", bed, "--expected", exp] + argv_extra
    out = io.StringIO()
    try:
        with contextlib.redirect_stdout(out):
            rc = EC.main()
    finally:
        EC.g, EC.E, EC.labview_handles, EC.labview_up, EC.vi_ready, EC.open_diagram, EC.BENCH, sys.argv = saved
    js = [p for p in os.listdir(d) if p.startswith("errorlist_bedp2_") and p.endswith(".json") and "_raw" not in p]
    R = json.load(open(os.path.join(d, js[0]), encoding="utf-8")) if len(js) == 1 else {}
    return rc, e.calls, R, out.getvalue()


def t_errorlist():
    good = ["Wire: wire has loose ends", "Wire: wire has loose ends", "Image In: 'Image In' is not wired"]
    rc, calls, R, _o = run_ec(good, ["--count-only", "--role", "scratch"])
    gate("E1 scratch count-only, counts match: ONE read, no double-click, OK",
         rc == 0 and [c["on_item"] for c in calls] == [False] and R.get("read_mode") == "count"
         and R.get("verdict") == "OK" and R.get("gates", {}).get("every_item_dclicked") is True,
         (rc, calls, R.get("read_mode"), R.get("verdict")))
    rc, calls, R, _o = run_ec(good + ["Add: Contains unwired or bad terminal"], ["--count-only", "--role", "scratch"])
    gate("E2 scratch count-only, an extra item: FULL read follows at once",
         [c["on_item"] for c in calls] == [False, True] and R.get("read_mode") == "count->full"
         and "1 extra" in (R.get("count_only_first") or {}).get("why", "") and R.get("dclicked") == 4,
         (calls, R.get("read_mode"), R.get("count_only_first")))
    rc, calls, R, o = run_ec(good, ["--count-only", "--role", "final"])
    gate("E3 --role final refuses count-only: full read", [c["on_item"] for c in calls] == [True] and
         R.get("read_mode") == "full" and R.get("count_only_refused") is True and "COUNT-ONLY REFUSED" in o,
         (calls, R.get("read_mode")))
    rc, calls, R, _o = run_ec(good, [])
    gate("E4 the default (no flags) is a full read", [c["on_item"] for c in calls] == [True] and
         R.get("read_mode") == "full" and R.get("verdict") == "OK", (calls, R.get("verdict")))


# ------------------------------------------------------------------------------------------------ S repeated function
def t_escalation():
    import stage_prerun as SP
    cd = os.path.join(TMP, "cards_e")
    sv = os.path.join(TMP, "scratch_verify")
    os.makedirs(sv)
    saved_sv, saved_seg = SP.SCRATCH_DIR, SP.stage_run_segments
    SP.SCRATCH_DIR = sv
    FN = "stagekit.p2_selftest_fn"
    try:
        wj(os.path.join(cd, "task_e-1.json"), {"id": "e-1"})
        wj(os.path.join(cd, "result_e-1.json"), {"status": "FAIL", "first_fail": "G4 %s raised KeyError 'x'" % FN})
        wj(os.path.join(cd, "task_e-2.json"), {"id": "e-2", "retry_of_card": "e-1"})
        wj(os.path.join(cd, "result_e-2.json"), {"status": "FAIL", "first_fail": "G4 %s raised KeyError 'y'" % FN})
        esc = wj(os.path.join(cd, "task_e-3.json"), {"id": "e-3", "retry_of_card": "e-2", "escalation": 1})
        r = SP.escalation_route(json.load(open(esc)), cards_dir=cd)
        gate("S1 same function as the previous attempt -> scratch-verify", r[0] == "scratch-verify" and r[1] == FN, r)
        wj(os.path.join(cd, "result_e-1.json"), {"status": "FAIL", "first_fail": "G2 gscript.wire raised"})
        r = SP.escalation_route(json.load(open(esc)), cards_dir=cd)
        gate("S2 a different function -> escalate", r[0] == "escalate", r)
        wj(os.path.join(cd, "result_e-1.json"), {"status": "FAIL", "first_fail": "G4 %s raised" % FN})
        time.sleep(0.05)
        wj(os.path.join(sv, "p2.json"), {"function": FN, "status": "PASS", "t": time.time() + 1})
        r = SP.escalation_route(json.load(open(esc)), cards_dir=cd)
        gate("S3 a scratch PASS newer than the failure -> escalate", r[0] == "escalate", r)
        os.remove(os.path.join(sv, "p2.json"))
        wj(os.path.join(cd, "task_e-4.json"), {"id": "e-4", "retry_of": "stage_d1_p2x.py"})
        wj(os.path.join(cd, "result_e-4.json"), {"status": "FAIL", "first_fail": "G4 %s raised" % FN})
        SP.stage_run_segments = lambda key, now=None: ([(1.0, True, FN), (2.0, True, FN)]
                                                       if key == "stage_d1_p2x.py" else [])
        r = SP.escalation_route({"id": "e-5", "retry_of_card": "e-4"}, cards_dir=cd)
        gate("S4 stage-run route: last two runs of the stage failed in it -> scratch-verify",
             r[0] == "scratch-verify" and "stage_d1_p2x.py" in r[2], r)
    finally:
        SP.SCRATCH_DIR, SP.stage_run_segments = saved_sv, saved_seg
    # S5/S6 through the real hook (a subprocess; its SCRATCH_DIR is the project's, which holds no record for FN)
    sid = "selftest-p2-esc-%d" % os.getpid()
    SIDS.append(sid)

    def gs(sub):
        p = subprocess.run([sys.executable, GS], text=True, capture_output=True, timeout=60, cwd=ROOT,
                           input=json.dumps({"session_id": sid, "tool_name": "Agent",
                                             "tool_input": {"subagent_type": sub, "prompt": "CARD %s" % esc}}))
        return p.returncode, p.stderr or ""
    rc, err = gs("material-opus-max")
    gate("S5 guard_session refuses the escalation rung (REPEATED TOOL FUNCTION)", rc == 2 and
         "REPEATED TOOL FUNCTION" in err and FN in err, err[:100])
    rc, err = gs("material")
    gate("S6 the same card to `material` (same rung) is allowed", rc == 0, (rc, err[:100]))


def main():
    try:
        for fn in (t_user_rules, t_new_structure, t_lint, t_soft_alert, t_errorlist, t_escalation):
            try:
                fn()
            except Exception as e:                                                 # noqa: BLE001
                import traceback
                traceback.print_exc()
                gate("%s raised" % fn.__name__, False, "%s: %s" % (type(e).__name__, e))
    finally:
        import guard_session as G
        for sid in SIDS:
            for p in (G.state_path(G.SAFE_RE.sub("_", sid)), G.state_path(G.SAFE_RE.sub("_", sid)) + ".lock"):
                if os.path.isfile(p):
                    os.remove(p)
        shutil.rmtree(TMP, ignore_errors=True)
    npass = sum(1 for _l, ok in RES if ok)
    bad = [l for l, ok in RES if not ok]
    print("\nSUMMARY %d/%d gates pass%s" % (npass, len(RES), ("; not passing: " + ", ".join(bad)) if bad else ""))
    print(P.result_line(P.make_result(npass, len(bad), bad[0] if bad else None)), flush=True)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
