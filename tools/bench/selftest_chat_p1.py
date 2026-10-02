r"""Self-test for card chat-P1 (user 2026-09-28 "1~4번은 적용하도록"): the acceleration items 1-4.
Touches NO LabVIEW, spawns NO agents, calls NO network: hooks are fed synthetic payloads (in-process with their BENCH /
PEER / ACTIVE / queue pointed at a temp dir, or as subprocesses with throwaway session ids that are deleted at the end).

PREDICTION CONTRACT (every gate below must hold):
  B1   12 concurrent `protocol.bind` processes on one active.json -> all 12 bindings survive (item 1(a))
  S1-S7 guard_session pipeline: LabVIEW card A allowed; a 2nd LabVIEW card refused; an offline card allowed as PREP
       (dispatch count unchanged); a 3rd live card refused (PIPELINE FULL); A's result file frees its slot; the 4th
       prep card beside a LabVIEW card refused (PREP BUDGET); two concurrent prose dispatches both counted (lock)
  O1-O4 guard_peer RULE-OFFLINE-CARD: an offline card bound labview:none is not blocked by another card's failing log
       (exit 0 + ledger line); a labview:build card / an LV-touching command / an unbound caller are not exempted
  F1-F9 gate_fp: log needs file:line; log + dedupe; RULE-GATE-FP discharges a checker entry naming the failing log
       (guard_peer exit 0); a 2nd entry of the same gate in the same cycle does not; a non-checker gate and a LabVIEW
       observation never; drain needs an existing fix + self-test; due at >= 5 open
  C1-C4 guard_cycle premature_build (a): a running prior-art review naming ANOTHER recipe does not block; naming THIS
       recipe, or with no START line, blocks; a --no-recipe review does not; constants 30 / 24
  P1-P4 proven_pattern: two other clean stages covering the signature -> proven; one clean + one failed -> not; an old
       record whose script sha moved -> not counted; the signature holds ops + create classes + K./SX. calls
  R1-R6 provisional base: refused at launch; plans validate with baseref; --rebase binds sim uids to real ones and drops
       provisional; the launch refusal is gone; a changed N plan refuses the rebase
  X1-X3 X14 advisory: WARN over 15 unproven, INFO under, budget 25 when proven; never a gate
  D1-D6 retro_due: not due (2 cards, delivered); due at 3 cards; due with no delivery; --close records CLOSED / refuses
       when due; guard_bash RETRO_RE matches `retro_due.py --close` only and a real hook call closes the session
  U1-U2 cycle_runner: gates_due carries a `gate-fp` item; retro_fallback logs DUE-not-run in a dry run
Output avoids a line starting with FAIL; ends with a RESULT line.
"""
import argparse
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
TMP = tempfile.mkdtemp(prefix="p1st_")
os.environ["GATE_FP_QUEUE"] = os.path.join(TMP, "gate_fp_queue.jsonl")
os.environ["RETRO_DUE_RECORD"] = os.path.join(TMP, "retro_due.jsonl")
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("BENCH_CELL", None)
import protocol as P  # noqa: E402

RES = []
CARD_P1 = os.path.join(TOOLS, "bench", "cards", "task_chat-P1.json")


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-58s %s" % ("ok" if ok else "BAD", label, str(detail)[:150]), flush=True)


def wj(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)
    return path


def card(path, cid, labview, minutes=60):
    d = json.load(open(CARD_P1, encoding="utf-8"))
    d["id"] = cid
    d["flags"] = dict(d["flags"], labview=labview)
    if labview == "none":
        # PD284(d): a realistic offline PREP card writes bench/recipe files only; the source card's `tools/**` can match a
        # stage tool, which guard_session's pairing check (PD281(a), guard_session.py:75,238) rightly refuses beside a
        # LabVIEW card.
        d["flags"]["write"] = ["tools/bench/**", "tools/recipes/**"]
    d["budget"] = {"failures": 2, "minutes": minutes}
    return wj(path, d)


# ------------------------------------------------------------------------------------------------ B1 concurrent binds
def t_binds():
    act = os.path.join(TMP, "active_b1.json")
    env = dict(os.environ, PROTOCOL_ACTIVE=act)
    code = ("import sys; sys.path.insert(0, %r); import protocol as P; ok, m = P.bind(sys.argv[1], 'material', %r); "
            "print(ok, m)" % (TOOLS, CARD_P1))
    procs = [subprocess.Popen([sys.executable, "-c", code, "agt-b1-%02d" % i], env=env, cwd=ROOT,
                              stdout=subprocess.PIPE, stderr=subprocess.STDOUT) for i in range(12)]
    outs = [p.communicate(timeout=120)[0].decode("utf-8", "replace") for p in procs]
    d = json.load(open(act, encoding="utf-8"))
    got = sorted(k for k in d if k.startswith("agt-b1-"))
    gate("B1 12 concurrent binds all survive (lock)", len(got) == 12 and all(o.startswith("True") for o in outs),
         "%d/12 %s" % (len(got), [o[:60] for o in outs if not o.startswith("True")][:2]))


# ------------------------------------------------------------------------------------------------ S guard_session
GS = os.path.join(HOOKS, "guard_session.py")
SIDS = []


def gs_call(sid, prompt, sub="material"):
    p = subprocess.run([sys.executable, GS], input=json.dumps({"session_id": sid, "tool_name": "Agent",
                                                              "tool_input": {"subagent_type": sub, "prompt": prompt}}),
                       text=True, capture_output=True, timeout=60, cwd=ROOT)
    return p.returncode, p.stderr or ""


def gs_state(sid):
    import guard_session as G
    return G.load(G.SAFE_RE.sub("_", sid))


def t_session():
    cd = os.path.join(TMP, "cards_s")
    A = card(os.path.join(cd, "task_p1s-A.json"), "p1s-A", "build")
    Bl = card(os.path.join(cd, "task_p1s-B.json"), "p1s-B", "read")
    C = card(os.path.join(cd, "task_p1s-C.json"), "p1s-C", "none")
    D = card(os.path.join(cd, "task_p1s-D.json"), "p1s-D", "none")
    sid = "selftest-p1-pipe-%d" % os.getpid()
    SIDS.append(sid)
    rc, _ = gs_call(sid, "CARD %s" % A)
    gate("S1 LabVIEW card A dispatched", rc == 0, rc)
    rc, err = gs_call(sid, "CARD %s" % Bl)
    gate("S2 a 2nd LabVIEW card (labview read) is REFUSED", rc == 2 and "second LabVIEW card" in err, err[:90])
    rc, _ = gs_call(sid, "CARD %s" % C)
    st = gs_state(sid)
    gate("S3 offline card allowed as PREP, dispatches unchanged", rc == 0 and st.get("prep") == 1
         and st.get("dispatches") == 1, (rc, st.get("prep"), st.get("dispatches")))
    rc, err = gs_call(sid, "CARD %s" % D)
    gate("S4 a 3rd live card is REFUSED (PIPELINE FULL)", rc == 2 and "PIPELINE FULL" in err, err[:90])
    time.sleep(0.05)
    wj(os.path.join(cd, "result_p1s-A.json"), {"schema": "result/1", "id": "p1s-A", "status": "PASS"})
    rc, _ = gs_call(sid, "CARD %s" % Bl)
    st = gs_state(sid)
    gate("S5 A's result frees its slot: LabVIEW card B allowed", rc == 0 and st.get("dispatches") == 2
         and sorted(e["id"] for e in st.get("live", [])) == ["p1s-B", "p1s-C"], (rc, st.get("live")))
    # S6 prep budget: C live beside B; prep cards E, F (after C/E return), then G refused
    n_ok = []
    prev = "p1s-C"
    for x in ("E", "F", "G"):
        time.sleep(0.05)
        wj(os.path.join(cd, "result_%s.json" % prev), {"schema": "result/1", "id": prev, "status": "PASS"})
        cx = card(os.path.join(cd, "task_p1s-%s.json" % x), "p1s-%s" % x, "none")
        rc, err = gs_call(sid, "CARD %s" % cx)
        n_ok.append((x, rc, "PREP BUDGET" in err))
        prev = "p1s-%s" % x
    gate("S6 the 4th prep card beside a LabVIEW card is REFUSED (PREP BUDGET 3)",
         [r[1] for r in n_ok] == [0, 0, 2] and n_ok[-1][2], n_ok)
    sid2 = "selftest-p1-conc-%d" % os.getpid()
    SIDS.append(sid2)
    payload = json.dumps({"session_id": sid2, "tool_name": "Agent", "tool_input": {"subagent_type": "material",
                                                                                   "prompt": "x"}})
    ps = [subprocess.Popen([sys.executable, GS], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           cwd=ROOT) for _ in range(4)]
    for p in ps:
        p.stdin.write(payload.encode())
        p.stdin.close()
    rcs = [p.wait(timeout=60) for p in ps]
    gate("S7 4 concurrent prose dispatches are all counted (state lock)", rcs == [0] * 4 and
         gs_state(sid2).get("dispatches") == 4, (rcs, gs_state(sid2).get("dispatches")))


# ------------------------------------------------------------------------------------------------ O / F guard_peer
def fail_log(bench, name, first="  FAIL  X5 wiring ops 3 vs plan rows 4"):
    p = os.path.join(bench, name)
    with open(p, "w", encoding="utf-8") as f:
        f.write("BGRUN START %s limit 5.0 min: py -u tools/bench/diag_p1fake.py\n%s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), first))
        f.write(P.result_line(P.make_result(0, 1, first.strip()[:100])) + "\nBGRUN END rc=1 after 2s\n")
    return p


def gp_main(gp, payload):
    old = sys.stdin, sys.stderr
    sys.stdin, err = io.StringIO(json.dumps(payload)), io.StringIO()
    sys.stderr = err
    try:
        rc = gp.main()
    finally:
        sys.stdin, sys.stderr = old
    return rc, err.getvalue()


def t_peer():
    import guard_peer as gp
    import gate_fp as GF
    GF.QUEUE = os.environ["GATE_FP_QUEUE"]
    bench, peer = os.path.join(TMP, "gp_bench"), os.path.join(TMP, "gp_peer")
    os.makedirs(bench)
    os.makedirs(peer)
    old = gp.BENCH, gp.PEER, P.ACTIVE
    gp.BENCH, gp.PEER, P.ACTIVE = bench, peer, os.path.join(TMP, "active_gp.json")
    try:
        lg = fail_log(bench, "diag_p1fake_x5.log")
        off = card(os.path.join(TMP, "cards_gp", "task_p1g-off.json"), "p1g-off", "none")
        lvc = card(os.path.join(TMP, "cards_gp", "task_p1g-lv.json"), "p1g-lv", "build")
        P.bind("agt-off", "material", off, goals=None)
        P.bind("agt-lv", "material", lvc, goals=None)
        cmd_off = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/bench/run_selftests_chat_p1.py t"
        rc, err = gp_main(gp, {"agent_id": "agt-off", "agent_type": "material", "tool_name": "Bash",
                               "tool_input": {"command": cmd_off}})
        ledger = open(os.path.join(bench, "jev_gate.log"), encoding="utf-8").read() if os.path.isfile(
            os.path.join(bench, "jev_gate.log")) else ""
        gate("O1 offline card NOT blocked by another card's failing log", rc == 0 and "RULE-OFFLINE-CARD" in ledger,
             (rc, err[:80]))
        gate("O2 a labview:build card is not exempted", gp.offline_card({"agent_id": "agt-lv"}, cmd_off) is None)
        cmd_lv = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- py -u tools/recipes/stage_d1_l2r1.py"
        gate("O3 an LV-touching command is not exempted (offline card)", gp.offline_card({"agent_id": "agt-off"}, cmd_lv)
             is None and gp.offline_command("py tools/stage_prerun.py --prerun tools/recipes/stage_d1_l2r1.py"))
        gate("O4 an unbound caller is not exempted", gp.offline_card({"agent_id": "agt-none"}, cmd_off) is None
             and gp.offline_card({}, cmd_off) is None)
        # ---- gate_fp
        r = subprocess.run([sys.executable, os.path.join(TOOLS, "gate_fp.py"), "log", "--gate", "guard_cycle", "--cmd",
                            "x", "--why", "no citation here", "--card", "c1"], capture_output=True, text=True, cwd=ROOT)
        gate("F1 gate_fp log without file:line evidence is REFUSED", r.returncode == 2 and "REFUSED" in r.stdout,
             r.stdout[:80])
        e1, new1 = GF.log_fp("checker:stage_prerun:X5", "py tools/stage_prerun.py --prerun x", "tools/stage_prerun.py:1800 "
                             "counts stop ops", "c1", line="X5 wiring ops 3 vs plan rows 4", log=lg)
        e1b, new1b = GF.log_fp("checker:stage_prerun:X5", "other form", "tools/stage_prerun.py:1800", "c2",
                               line="X5 wiring ops 3 vs plan rows 4")
        gate("F2 log + dedupe on gate+line (card merged)", new1 and not new1b and e1b["id"] == e1["id"]
             and e1b["cards"] == ["c1", "c2"], (e1["id"], e1b.get("cards")))
        rc, err = gp_main(gp, {"tool_name": "Bash", "tool_input": {"command": cmd_lv}})
        ledger = open(os.path.join(bench, "jev_gate.log"), encoding="utf-8").read()
        gate("F3 RULE-GATE-FP discharges a checker entry naming the failing log", rc == 0 and "RULE-GATE-FP" in ledger
             and e1["id"] in ledger, (rc, err[:100]))
        lg2 = fail_log(bench, "diag_p1fake_x5b.log")
        GF.log_fp("checker:stage_prerun:X5", "c", "tools/stage_prerun.py:1801", "c3", line="another line", log=lg2)
        e2, why2 = GF.discharge_for_log(lg2, "  FAIL  X5 another")
        gate("F4 a 2nd entry of the same gate in the same cycle does NOT discharge", e2 is None and "one per gate" in why2,
             why2)
        lg3 = fail_log(bench, "diag_p1fake_lv.log")
        GF.log_fp("labview:census", "c", "tools/stagekit.py:1", "c4", line="census 3", log=lg3)
        e3, why3 = GF.discharge_for_log(lg3, "  FAIL  census 3")
        GF.log_fp("checker:stagekit:D7", "c", "tools/stagekit.py:2", "c5", line="ExecState 0", log=os.path.join(bench, "q.log"))
        e4, why4 = GF.discharge_for_log(os.path.join(bench, "q.log"), "  FAIL  D7 ExecState 0 expected 1")
        gate("F5 a non-checker gate never discharges", e3 is None and "not a checker" in why3, why3)
        gate("F6 a LabVIEW observation never discharges", e4 is None and "LabVIEW observation" in why4, why4)
        bad, why_d = GF.drain(e1["id"], "tools/no_such_file.py:3", "selftest_chat_p1")
        good, _w = GF.drain(e1["id"], "tools/gate_fp.py:1", "selftest_chat_p1")
        gate("F7 drain needs an existing fix; then closes the entry", bad is None and good and good["status"] == "drained",
             why_d)
        d0, _ = GF.due(cycle=P.current_cycle())
        for i in range(5):
            GF.log_fp("guard_bash", "cmd%d" % i, "tools/hooks/guard_bash.py:%d" % (i + 1), "c9", line="line %d" % i)
        d1, det = GF.due(cycle=P.current_cycle())
        gate("F8 due at >= 5 open (not before)", not d0 and d1 and "open" in det, det[:100])
        gate("F9 is_checker_gate: guard_* and checker:<tool> only", GF.is_checker_gate("guard_cycle")
             and GF.is_checker_gate("checker:stagekit:D7") and not GF.is_checker_gate("checker:myscript:x")
             and not GF.is_checker_gate("labview:x"))
    finally:
        gp.BENCH, gp.PEER, P.ACTIVE = old


# ------------------------------------------------------------------------------------------------ C guard_cycle
def t_cycle():
    import guard_cycle as GC
    bench, peer = os.path.join(TMP, "gc_bench"), os.path.join(TMP, "gc_peer")
    os.makedirs(bench)
    os.makedirs(peer)
    rdir = os.path.join(TMP, "gcr", "tools", "recipes")
    os.makedirs(rdir)
    mine = os.path.join(rdir, "stage_p1mine.py").replace("\\", "/")
    open(mine, "w").write("print('x')\n")
    old = GC.BENCH, GC.PEER
    GC.BENCH, GC.PEER = bench, peer
    try:
        def review(start):
            with open(os.path.join(bench, "priorart_p1.log"), "w", encoding="utf-8") as f:
                f.write(start + "\nrunning...\n")
            return GC.premature_build("py %s" % mine) or ""
        m1 = review("BGRUN START 2026-09-28 10:00:00 limit 12.0 min: py -u tools/prior_art_review.py --plan-file a.md "
                    "--slug s --recipe tools/recipes/stage_other.py")
        gate("C1 a running review of ANOTHER recipe does not block (timing)", "STILL RUNNING" not in m1, m1[:70])
        m2 = review("BGRUN START 2026-09-28 10:00:00 limit 12.0 min: py -u tools/prior_art_review.py --plan-file a.md "
                    "--slug s --recipe %s" % mine)
        m3 = review("no start line")
        gate("C2 naming THIS recipe, or no START line, blocks", "STILL RUNNING" in m2 and "STILL RUNNING" in m3)
        m4 = review("BGRUN START 2026-09-28 10:00:00 limit 12.0 min: py -u tools/prior_art_review.py --plan-file a.md "
                    "--slug s --no-recipe \"plan only\"")
        gate("C3 a --no-recipe review blocks no recipe", "STILL RUNNING" not in m4, m4[:70])
        gate("C4 backstop constants 30 builds / 24 h", GC.CYCLE_BUILD_BUDGET == 30 and GC.CYCLE_HOURS == 24.0)
    finally:
        GC.BENCH, GC.PEER = old


# ------------------------------------------------------------------------------------------------ P proven pattern
def clean_log(path, ok=True):
    with open(path, "w", encoding="utf-8") as f:
        f.write("BGRUN START 2026-09-28 09:00:00 limit 30.0 min: py -u tools/recipes/stage_x.py\n")
        f.write(P.result_line(P.make_result(5 if ok else 4, 0 if ok else 1, None if ok else "G3")) + "\n")
        f.write("BGRUN END rc=%d after 60s\n" % (0 if ok else 1))
    return path


def t_proven():
    import stage_prerun as SP
    rdir = os.path.join(TMP, "pp", "tools", "recipes")
    os.makedirs(rdir)
    rec = os.path.join(rdir, "stage_p1new.py")
    open(rec, "w").write("import stagekit as K, stagexec as SX\nPLAN = 'plan_p1pp.json'\n"
                         "x = SX.Executor(PLAN)\nK.run(x, None)\n")
    wj(os.path.join(rdir, "plan_p1pp.json"), {"schema": "stageplan/1", "stage": "p1pp", "actions": [
        {"op": "wire", "src": "1.a", "dst": "2.b"}, {"op": "create", "class": "Local", "diagram": 3}]})
    sig = SP.pattern_signature(rec)
    gate("P4 signature = ops + create classes + K./SX. calls", sig == sorted(
        ["op:wire", "op:create", "create:Local", "K.run", "SX.Executor"]), sig)
    big = sig + ["op:tunnel", "K.save"]
    ok1, ok2, bad = (clean_log(os.path.join(TMP, "pp", n), okk) for n, okk in
                     (("a.log", True), ("b.log", True), ("c.log", False)))
    runs = [{"by": "bgrun", "stage": "stage_a.py", "pattern": big, "log": ok1},
            {"by": "bgrun", "stage": "stage_b.py", "pattern": big, "log": ok2},
            {"by": "bgrun", "stage": "stage_c.py", "pattern": big, "log": bad}]
    p1 = SP.proven_pattern(rec, runs=runs, recs=[])
    gate("P1 two other clean stages covering the signature -> proven", p1[0] and p1[1] == ["stage_a.py", "stage_b.py"],
         p1[:2])
    p2 = SP.proven_pattern(rec, runs=[runs[0], runs[2]], recs=[])
    gate("P2 one clean + one failed -> NOT proven", not p2[0], p2[:2])
    old = [{"by": "bgrun", "stage": "stage_d.py", "script": "tools/recipes/stage_d1_l2r1.py", "sha256": "0" * 64,
            "log": ok1}]
    p3 = SP.proven_pattern(rec, runs=[runs[0]] + old, recs=[])
    gate("P3 an old record whose script sha moved is not counted (fail closed)", not p3[0] and p3[1] == ["stage_a.py"],
         p3[:2])


# ------------------------------------------------------------------------------------------------ R provisional + rebase
def graph(rows):
    return {"vi": "x.vi", "md5": "0" * 32, "terminals": rows, "objs": []}


def row(t, name, src, wire, owner, cls, tcls="Terminal"):
    return {"term_uid": t, "term_name": name, "is_source": src, "wire_uid": wire, "owner_uid": owner,
            "owner_class": cls, "frame_diagram": 3, "term_class": tcls}


def t_rebase():
    import stage_prerun as SP
    d = os.path.join(TMP, "rb", "tools", "recipes")
    os.makedirs(d)
    add = [row(11, "x", False, 0, 10, "Add"), row(12, "x+y", True, 0, 10, "Add")]
    gN = wj(os.path.join(d, "g_base_n.json"), graph(add))
    planN = wj(os.path.join(d, "plan_p1n.json"), {"schema": "stageplan/1", "stage": "p1n",
                                                  "base": {"path": gN, "md5": P._md5(gN)},
                                                  "actions": [{"op": "create", "class": "Constant", "diagram": 3}]})
    prov = wj(os.path.join(d, "g_prov.json"), graph([row(11, "x", False, -3, 10, "Add"), add[1],
                                                     row(-2, "", True, -3, -1, "Constant")]))
    real = wj(os.path.join(d, "g_real.json"), graph([row(11, "x", False, 60, 10, "Add"), add[1],
                                                     row(51, "", True, 60, 50, "Constant")]))
    plan = {"schema": "stageplan/1", "stage": "p1m",
            "base": {"path": prov, "md5": P._md5(prov), "provisional": True,
                     "sim_of": {"plan": planN, "md5": P._md5(planN)}},
            "actions": [{"op": "wire", "src": {"uid": -1, "term_uid": -2}, "dst": {"uid": 10, "term": "x"}},
                        {"op": "delete_wire", "wire_uid": -3}], "final": True, "finalized": {"x": 1}}
    pp = wj(os.path.join(d, "plan_p1m.json"), plan)
    rec = os.path.join(d, "stage_p1m.py")
    open(rec, "w").write("PLAN = 'plan_p1m.json'\n")
    ok_v, why_v = P.validate_obj(json.load(open(pp, encoding="utf-8")))
    gate("R2 a provisional plan validates against stageplan/1 (baseref)", ok_v, why_v)
    ok, why = SP.check_launch("py %s" % rec.replace("\\", "/"))
    gate("R1 a provisional base is REFUSED at launch", not ok and "PROVISIONAL" in why, why[:90])
    ok, det = SP.rebase(pp, real, simulate=False)
    new = json.load(open(pp, encoding="utf-8"))
    a0, a1 = new["actions"]
    gate("R3 --rebase binds sim uids to the real ones", ok and a0["src"] == {"uid": 50, "term_uid": 51}
         and a1["wire_uid"] == 60 and a0["dst"] == {"uid": 10, "term": "x"}, (det, a0, a1))
    gate("R4 base -> real graph, provisional/final/finalized dropped, still valid",
         new["base"].get("md5") == P._md5(real) and "provisional" not in new["base"] and "finalized" not in new
         and "final" not in new and P.validate_obj(new)[0], new["base"])
    ok, why = SP.check_launch("py %s" % rec.replace("\\", "/"))
    gate("R5 after --rebase the provisional refusal is gone", "PROVISIONAL" not in why, why[:90])
    wj(pp, plan)
    with open(planN, "a", encoding="utf-8") as f:
        f.write("\n")
    ok, det = SP.rebase(pp, real, simulate=False)
    gate("R6 a changed N plan REFUSES the rebase (re-simulate)", not ok and "changed since" in det, det[:90])


# ------------------------------------------------------------------------------------------------ X14
def t_x14():
    import stage_prerun as SP
    rec = os.path.join(TMP, "pp", "tools", "recipes", "stage_p1new.py")
    lines = []
    w = SP.x14_advisory(rec, 30, log=lines.append)
    i = SP.x14_advisory(rec, 10, log=lines.append)
    gate("X1 unproven: budget 15, WARN over, INFO under", w["budget"] == 15 and w["warn"] and lines[0].startswith("  WARN")
         and not i["warn"] and lines[1].startswith("  INFO"), lines)
    orig = SP.proven_pattern
    SP.proven_pattern = lambda r: (True, ["stage_a.py", "stage_b.py"], ["op:wire"])
    try:
        p = SP.x14_advisory(rec, 20, log=lines.append)
    finally:
        SP.proven_pattern = orig
    gate("X2 proven: budget 25, 20 rows no WARN", p["budget"] == 25 and not p["warn"] and "stage_a.py" in lines[-1],
         lines[-1])
    src = open(os.path.join(TOOLS, "stage_prerun.py"), encoding="utf-8").read()
    gate("X3 X14 is never a gate", 'gate("X14' not in src and "x14_advisory(" in src)


# ------------------------------------------------------------------------------------------------ D retro_due
def t_retro():
    import retro_due as RD
    cd, peer = os.path.join(TMP, "rd_cards"), os.path.join(TMP, "rd_peer")
    os.makedirs(cd)
    os.makedirs(peer)
    now = time.time()
    rp = os.path.join(peer, "2026-09-28-retrospective-cycle200.md")
    open(rp, "w").write("# retro\n- **outcome:** ANSWERED\n")
    os.utime(rp, (now - 1000, now - 1000))
    for n, t in ((201, now - 500), (202, now - 400)):
        wj(os.path.join(cd, "cycle_%d.json" % n), {"schema": "cycle/1", "cycle": n})
        os.utime(os.path.join(cd, "cycle_%d.json" % n), (t, t))
    wj(os.path.join(cd, "result_202-1.json"), {"schema": "result/1", "id": "202-1", "status": "PASS",
                                               "artefacts": [{"path": "C:/x/user.lib/claudeDev/D1_a.vi", "md5": None}]})
    due, why, f = RD.check(202, cd, peer, violations=False)
    gate("D1 not due: 2 cards since the retro, delivered", not due and f["delivered"] == ["202-1"], (why, f))
    wj(os.path.join(cd, "cycle_203.json"), {"schema": "cycle/1", "cycle": 203})
    wj(os.path.join(cd, "result_203-1.json"), {"schema": "result/1", "id": "203-1", "status": "PASS",
                                               "artefacts": [{"path": "C:/x/user.lib/claudeDev/D1_b.vi", "md5": None}]})
    due3, why3, _ = RD.check(203, cd, peer, violations=False)
    gate("D2 due at 3 cycle cards since the newest retrospective", due3 and why3[0].startswith("(a)"), why3)
    os.remove(os.path.join(cd, "result_203-1.json"))
    wj(os.path.join(cd, "result_203-2.json"), {"schema": "result/1", "id": "203-2", "status": "PASS", "artefacts": []})
    os.remove(os.path.join(cd, "cycle_203.json"))
    wj(os.path.join(cd, "cycle_204.json"), {"schema": "cycle/1", "cycle": 204})
    os.remove(os.path.join(cd, "cycle_201.json"))
    dueb, whyb, _ = RD.check(204, cd, peer, violations=False)
    gate("D3 due when the cycle delivered no claudeDev .vi", dueb and any(w.startswith("(b)") for w in whyb), whyb)
    orig = RD.near_threshold
    RD.near_threshold = lambda: []
    try:
        wj(os.path.join(cd, "result_204-1.json"), {"schema": "result/1", "id": "204-1", "status": "PASS",
                                                   "artefacts": [{"path": "C:/x/claudeDev/D1_c.vi", "md5": None}]})
        rc0 = RD.main(["--cycle", "204", "--close", "--cards-dir", cd, "--peer-dir", peer])
        wj(os.path.join(cd, "cycle_205.json"), {"schema": "cycle/1", "cycle": 205})
        rc1 = RD.main(["--cycle", "205", "--close", "--cards-dir", cd, "--peer-dir", peer])
    finally:
        RD.near_threshold = orig
    recs = [json.loads(ln) for ln in open(os.environ["RETRO_DUE_RECORD"], encoding="utf-8")]
    gate("D4 --close records CLOSED when not due, refuses (rc 1) when due", rc0 == 0 and rc1 == 1
         and recs[0]["closed"] and not recs[1]["closed"], (rc0, rc1, [r.get("closed") for r in recs]))
    import guard_bash as GB
    m = [bool(GB.RETRO_RE.search(c)) for c in ("py tools/retro_due.py --cycle 5 --close",
                                               "py tools/retro_due.py --cycle 5", "grep retro_due.py --close x",
                                               "py tools/bgrun.py --max-min 10 --log r.log -- py tools/retrospective.py "
                                               "--cycle 5")]
    gate("D5 RETRO_RE: `retro_due.py --close` and retrospective.py only", m == [True, False, False, True], m)
    sid = "selftest-p1-close-%d" % os.getpid()
    SIDS.append(sid)
    env = dict(os.environ, NEXT_SNAPSHOT=os.path.join(TMP, "no_snapshot.md5"), NEXT_JSON=os.path.join(TMP, "no_next.json"))
    p = subprocess.run([sys.executable, os.path.join(HOOKS, "guard_bash.py")], text=True, capture_output=True,
                       input=json.dumps({"session_id": sid, "tool_name": "Bash", "tool_input": {
                           "command": "py tools/retro_due.py --cycle 9 --close", "timeout": 20000}}), env=env, cwd=ROOT)
    gate("D6 guard_bash: `retro_due.py --close` closes the session (retro_done)", p.returncode == 0 and
         gs_state(sid).get("retro_done") is True, (p.returncode, p.stderr[:80]))


# ------------------------------------------------------------------------------------------------ U cycle_runner
def t_runner():
    import cycle_runner as CR
    bench, peer = os.path.join(TMP, "cr_bench"), os.path.join(TMP, "cr_peer")
    os.makedirs(os.path.join(bench, "cards"))
    os.makedirs(peer)
    items = CR.gates_due(bench, peer, None)
    g = [x for x in items if x["gate"] == "gate-fp"]
    gate("U1 gates_due carries a gate-fp item", len(g) == 1 and g[0]["due"] is not None, g)
    a = argparse.Namespace(peer_dir=peer, dry_run=True, dry_cmd=None)
    lg = os.path.join(bench, "runner.log")
    note = CR.retro_fallback(7, time.time() - 60, a, bench, lg)
    gate("U2 retro_fallback: DUE, none archived, not run in a dry run", note and "not run (dry run)" in note,
         (note or "")[:100])


def main():
    try:
        for fn in (t_binds, t_session, t_peer, t_cycle, t_proven, t_rebase, t_x14, t_retro, t_runner):
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
