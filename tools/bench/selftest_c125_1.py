r"""Self-test for card 125-1: gate-fp fp-10..fp-13 drained, and stage_prerun X16 (PD251(b)).
Touches NO LabVIEW, no network: guard_peer runs in-process with BENCH / PEER / ACTIVE / gate-fp queue / launch ledger
pointed at a temp dir; protocol.check_command is called on synthetic card dicts. "BEFORE" = the new rule switched off
in-process (protocol.OFFLINE_SELFTESTS emptied, guard_peer.offline_cmd_lv_card stubbed to None).

PREDICTION CONTRACT (every gate must hold):
  A1-A4 fp-10 guard_peer RULE-OFFLINE-CMD: the entry's command (offline md5 script) under a labview:build card on ANOTHER
        card's failing log -> before rc 2, after rc 0 + ledger line; an LV recipe under the same card -> rc 2; the same
        offline command when the ledger says THIS card launched the failing log -> rc 2; corrupt ledger -> owned (gated)
  B1-B3 fp-11 guard_peer selftest_exempt for `selftest_case_frame_c124.py`: before False, after True; an unlisted LV
        self-test (selftest_c118_primnested.py) stays False; offline_command agrees
  C1-C3 fp-12 protocol.check_command, labview none, census hook-in self-test under bgrun: before refused, after allowed;
        an LV diagnostic of the same shape (diag_c123_struct.py, imports stagekit) still refused; an unlisted LV
        self-test still refused
  D1-D4 fp-13 `stagexec.py selftest` under labview none: before refused, after allowed; `stagexec.py run <plan>` refused;
        `selftest; run` chained refused; soft alert (card 60+ min old) does not refuse the listed self-test, still
        refuses the diagnostic
  E1-E3 X16: a plan with one created-primitive terminal lacking term_class -> FAIL naming it; the same with the class ->
        PASS; plan_ring_p3a.json -> PASS
  E4-E6 card 125-3 (PD252(a)): a const_donor create with term_class removed -> PASS; plan_ring_p2b.json -> PASS;
        the same constant create with `prim` removed (not const_donor) -> FAIL naming it
Ends with a RESULT line.
"""
import copy
import io
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
HOOKS = os.path.join(TOOLS, "hooks")
sys.path.insert(0, TOOLS)
sys.path.insert(0, HOOKS)
TMP = tempfile.mkdtemp(prefix="c125st_")
os.environ["GATE_FP_QUEUE"] = os.path.join(TMP, "gate_fp_queue.jsonl")
os.environ["PROTOCOL_LAUNCHES"] = os.path.join(TMP, "launches.jsonl")
os.environ.pop("TYPESAFE_API_KEY", None)
os.environ.pop("BENCH_CELL", None)
import protocol as P  # noqa: E402

RES = []
CARD_SRC = os.path.join(TOOLS, "bench", "cards", "task_chat-P1.json")
FP10_CMD = "py tools/bgrun.py --material --max-min 2 --log tools/bench/ring_p2a_md5.log -- py -u tools/bench/ring_p2a_md5.py"


def gate(label, ok, detail=""):
    RES.append((label, bool(ok)))
    print("  %-4s %-66s %s" % ("ok" if ok else "BAD", label, str(detail)[:150]), flush=True)


def card_file(cid, labview):
    d = json.load(open(CARD_SRC, encoding="utf-8"))
    d["id"], d["flags"] = cid, dict(d["flags"], labview=labview)
    d.pop("requires", None)
    p = os.path.join(TMP, "cards", "task_%s.json" % cid)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    json.dump(d, open(p, "w", encoding="utf-8"), indent=1)
    return p


def card_dict(labview):
    return {"id": "c125st", "flags": {"labview": labview, "gui": False, "hardware": "none", "run_vi": False,
                                      "write": [], "status_edit": False, "git_commit": False, "peers": []}}


class Off:
    """Switch the new rules off in-process (the BEFORE state)."""
    def __init__(self, gp=None):
        self.gp = gp

    def __enter__(self):
        self.saved = dict(P.OFFLINE_SELFTESTS)
        P.OFFLINE_SELFTESTS.clear()
        if self.gp:
            self.f = self.gp.offline_cmd_lv_card
            self.gp.offline_cmd_lv_card = lambda *a: None

    def __exit__(self, *a):
        P.OFFLINE_SELFTESTS.update(self.saved)
        if self.gp:
            self.gp.offline_cmd_lv_card = self.f


def fail_log(bench, name):
    p = os.path.join(bench, name)
    first = "  FAIL  L3 check_launch fixture"
    with open(p, "w", encoding="utf-8") as f:
        f.write("BGRUN START %s limit 5.0 min: py -u tools/bench/diag_c125fake.py\n%s\n" % (
            time.strftime("%Y-%m-%d %H:%M:%S"), first))
        f.write(P.result_line(P.make_result(0, 1, first.strip())) + "\nBGRUN END rc=1 after 2s\n")
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


def t_fp10():
    import guard_peer as gp
    import gate_fp as GF
    GF.QUEUE = os.environ["GATE_FP_QUEUE"]
    bench, peer = os.path.join(TMP, "bench"), os.path.join(TMP, "peer")
    os.makedirs(bench)
    os.makedirs(peer)
    old = gp.BENCH, gp.PEER, P.ACTIVE, P.LAUNCHES
    gp.BENCH, gp.PEER, P.ACTIVE, P.LAUNCHES = bench, peer, os.path.join(TMP, "active.json"), os.environ["PROTOCOL_LAUNCHES"]
    try:
        lg = fail_log(bench, "c125fake_other_card.log")
        P.bind("agt-lvb", "material", card_file("c125-lvb", "build"), goals=None)
        pay = {"agent_id": "agt-lvb", "agent_type": "material", "tool_name": "Bash", "tool_input": {"command": FP10_CMD}}
        with Off(gp):
            rc0, err0 = gp_main(gp, pay)
        rc1, err1 = gp_main(gp, pay)
        ledger = open(os.path.join(bench, "jev_gate.log"), encoding="utf-8").read() if os.path.isfile(
            os.path.join(bench, "jev_gate.log")) else ""
        gate("A1 fp-10 cmd, labview:build card, other card's log: before 2 / after 0", rc0 == 2 and rc1 == 0
             and "RULE-OFFLINE-CMD" in ledger, (rc0, rc1, err1[:90]))
        lv = dict(pay, tool_input={"command": "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- "
                                              "py -u tools/recipes/stage_d1_ring_p3a.py"})
        rc2, _e = gp_main(gp, lv)
        gate("A2 an LV recipe under the same card is still refused", rc2 == 2, rc2)
        P.record_launch("c125-lvb", "py tools/bgrun.py --material --max-min 5 --log tools/bench/%s -- py -u "
                                    "tools/bench/diag_c125fake.py" % os.path.basename(lg))
        rc3, _e = gp_main(gp, pay)
        gate("A3 the card's OWN failing log (ledger) still gates the offline cmd", rc3 == 2 and
             P.card_owns_log("c125-lvb", lg) and not P.card_owns_log("c125-other", lg), rc3)
        open(P.LAUNCHES, "a", encoding="utf-8").write("{not json\n")
        gate("A4 a corrupt ledger reads as owned (fail closed)", P.card_owns_log("c125-zzz", lg) is True)
    finally:
        gp.BENCH, gp.PEER, P.ACTIVE, P.LAUNCHES = old


def t_fp11():
    import guard_peer as gp
    st = "BGRUN START x limit 5.0 min: py -u tools/bench/selftest_case_frame_c124.py"
    with Off():
        b = gp.selftest_exempt(st)
    a = gp.selftest_exempt(st)
    gate("B1 fp-11 selftest_case_frame_c124 exempt: before False / after True", b is False and a is True, (b, a))
    gate("B2 an unlisted LV self-test (selftest_c118_primnested) is not exempt",
         gp.selftest_exempt("BGRUN START x limit 5.0 min: py -u tools/bench/selftest_c118_primnested.py") is False)
    gate("B3 offline_command: listed self-test True, stagexec run False",
         gp.offline_command("py -u tools/bench/selftest_case_frame_c124.py")
         and not gp.offline_command("py -u tools/stagexec.py run tools/bench/plan_ring_p3a.json"))


def chk(cmd, labview="none"):
    return P.check_command(card_dict(labview), cmd)


def t_fp12_13():
    bg = "py tools/bgrun.py --material --max-min 5 --log tools/bench/x.log -- "
    c12 = bg + "py -u tools/bench/selftest_census_hookin_c123.py"
    with Off():
        b = chk(c12)
    a = chk(c12)
    gate("C1 fp-12 census hook-in self-test, labview none: before refused / after allowed", b and a is None, (b, a))
    gate("C2 an LV diagnostic of the same shape (diag_c123_struct) is still refused",
         chk(bg + "py -u tools/bench/diag_c123_struct.py") is not None)
    gate("C3 an unlisted LV self-test (selftest_c118_primnested) is still refused",
         chk(bg + "py -u tools/bench/selftest_c118_primnested.py") is not None)
    c13 = bg + "py -u tools/stagexec.py selftest"
    with Off():
        b = chk(c13)
    a = chk(c13)
    gate("D1 fp-13 stagexec selftest, labview none: before refused / after allowed", b and a is None, (b, a))
    gate("D2 `stagexec.py run <plan>` is still refused",
         chk(bg + "py -u tools/stagexec.py run tools/bench/plan_ring_p3a.json") is not None)
    gate("D3 `stagexec.py selftest; stagexec.py run <plan>` is refused",
         chk("py -u tools/stagexec.py selftest; py -u tools/stagexec.py run tools/bench/plan_ring_p3a.json") is not None
         and chk('py -u "tools/stagexec.py" selftest') is None)
    old = dict(card_dict("build"), _bound=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() - 3 * 3600)))
    s1 = P.soft_alert_refusal(old, c12, P._launched_scripts(c12))
    s2 = P.soft_alert_refusal(old, bg + "py -u tools/bench/diag_c123_struct.py",
                              P._launched_scripts(bg + "py -u tools/bench/diag_c123_struct.py"))
    gate("D4 soft alert: listed self-test not refused, diagnostic still refused", s1 is None and s2 is not None, (s1, s2))


def t_x16():
    import stage_prerun as SP
    pl = json.load(open(os.path.join(TOOLS, "bench", "plan_ring_p3a.json"), encoding="utf-8"))
    bad = copy.deepcopy(pl)
    a = next(x for x in bad["actions"] if x.get("op") == "create" and x.get("terminals"))
    del a["terminals"][0]["term_class"]
    okb, detb = SP.x16_gate([bad])
    good = copy.deepcopy(bad)
    next(x for x in good["actions"] if x.get("id") == a["id"])["terminals"][0]["term_class"] = "ParameterTerminal"
    okg, detg = SP.x16_gate([good])
    gate("E1 X16 FAIL: a create terminal without term_class is named", okb is False and detb[0]["action"] == a["id"],
         detb)
    gate("E2 X16 PASS: the same plan with the class declared", okg is True, detg)
    okp, detp = SP.x16_gate([pl])
    gate("E3 X16 PASS on plan_ring_p3a.json as committed", okp is True, detp)
    # card 125-3 (PD252(a)): const_donor creates are out of X16's scope
    dn = copy.deepcopy(pl)
    k = next(x for x in dn["actions"] if x.get("prim") == "const_donor" and x.get("terminals"))
    for t in k["terminals"]:
        t.pop("term_class", None)
    okd, detd = SP.x16_gate([dn])
    gate("E4 X16 PASS: a const_donor create without term_class (card 125-3)", okd is True, detd)
    p2b = json.load(open(os.path.join(TOOLS, "bench", "plan_ring_p2b.json"), encoding="utf-8"))
    okq, detq = SP.x16_gate([p2b])
    gate("E5 X16 PASS on plan_ring_p2b.json (5 const_donor creates, no term_class)", okq is True, detq)
    nd = copy.deepcopy(dn)
    k2 = next(x for x in nd["actions"] if x.get("id") == k["id"])
    k2.pop("prim", None)
    okn, detn = SP.x16_gate([nd])
    gate("E6 X16 FAIL: the same constant create WITHOUT prim const_donor is still refused",
         okn is False and detn[0]["action"] == k["id"], detn)


def main():
    for t in (t_fp10, t_fp11, t_fp12_13, t_x16):
        try:
            t()
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            gate("%s raised" % t.__name__, False, "%s: %s" % (type(e).__name__, e))
            traceback.print_exc()
    shutil.rmtree(TMP, ignore_errors=True)
    npass = sum(1 for _l, ok in RES if ok)
    nfail = len(RES) - npass
    print("=== selftest_c125_1: %d pass / %d fail" % (npass, nfail), flush=True)
    print(P.result_line(P.make_result(npass, nfail, next((l for l, ok in RES if not ok), None))), flush=True)
    return 0 if nfail == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
