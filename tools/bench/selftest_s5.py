r"""selftest_s5 - card chat-S5 (the user's "S1", PD337): unit self-test of the four parts. OFFLINE, no LabVIEW, no Jev call
(ADDR_JEV=0). Existed first (checked): selftest_rebase_uidreuse_c143_4.py (UID-REUSE), selftest_elpred.py (EL rule),
selftest_gateclass_s2/s3.py (soft path) - none covers a name that does not bind, prose fields, releases or the by-design EL.
PREDICTION CONTRACT: 21 gates PASS, 0 FAIL.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_s5.log -- py -u tools/bench/selftest_s5.py"""
import json, os, sys, tempfile, time                                                   # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "hooks"))
os.environ["ADDR_JEV"] = "0"
os.environ["GATE_SOFT_LOG"] = os.path.join(tempfile.gettempdir(), "s5_soft.jsonl")
import addrcheck as AC, protocol as PR, gateclass as GC, elrule as ELR, stage_prerun as SPR   # noqa: E401,E402
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:400]), flush=True)


def row(t, o, name, src, cls="Terminal", oc="Local", w=0):
    return {"term_uid": t, "owner_uid": o, "term_name": name, "is_source": src, "term_class": cls, "owner_class": oc, "wire_uid": w}


# ---- 1. address by (owner, index, class) - the 143-4 case: plan 'value', LabVIEW 'StopAll'
sim = [row(-21, -20, "StopAll", True)]
real = [row(23310, 6902, "StopAll", True), row(23276, 6899, "StopAll", False)]
r, how, _c = AC.resolve(sim, -20, "value", want_source=True)
gate("A1 143-4: plan 'value' on Local -20 resolves to -21 by stagesim's alias", r and r["term_uid"] == -21 and how == "value-alias", how)
ok, how = AC.real_match(sim, -21, real, 23310, 6902)
gate("A2 143-4: bound real #23310 'StopAll' sits at the same position (unique class+direction)", ok and how == "unique-dir", how)
r, how, c = AC.resolve(sim, -20, "NoSuch", want_source=True)
gate("A3 an unknown name on that Local stays UNRESOLVED (never guessed), candidates listed", r is None and c and c[0]["term_uid"] == -21, c)
two = [row(1, 9, "x", False, oc="Add"), row(2, 9, "y", False, oc="Add"), row(3, 9, "x+y", True, oc="Add")]
r, how, _c = AC.resolve(two, 9, "lbl", want_source=False, pos={"index": 1, "class": "Terminal", "source": False})
gate("A4 recorded triple (index 1, Terminal, sink) picks #2 'y' when the name does not bind", r and r["term_uid"] == 2 and how == "triple", how)
r, how, _c = AC.resolve(two, 9, "lbl", want_source=False, pos={"index": 1, "class": "InnerTerminal"})
gate("A5 a triple whose class disagrees resolves nothing", r is None, how)
r, how, _c = AC.resolve(two, 9, "value", want_source=False)
gate("A6 'value' alias refuses on a node with TWO sinks (not unique)", r is None, how)
realtwo = [row(11, 90, "a", False, oc="Add"), row(12, 90, "b", False, oc="Add"), row(13, 90, "o", True, oc="Add")]
gate("A7 real_match: same index on a two-sink node -> 'index'; other index -> refused",
     AC.real_match(two, 2, realtwo, 12, 90) == (True, "index") and AC.real_match(two, 2, realtwo, 11, 90) == (False, None))

# ---- 2. tier (a) over a plan + address-only failures owe no review
plan = {"schema": "stageplan/1", "stage": "t", "actions": [{"op": "wire", "id": "w1", "src": {"uid": 6902, "term": "value"},
        "dst": {"uid": 9, "term": "x"}}, {"op": "wire", "id": "w2", "src": "6902.Nope", "dst": "new:X1.in"}]}
rep = AC.check_plan(plan, real + two)
gate("B1 check_plan: 2 resolved (alias, name), 1 unresolved with candidates, 1 symbolic skipped",
     len(rep["resolved"]) == 2 and len(rep["unresolved"]) == 1 and rep["unresolved"][0]["candidates"] and len(rep["skipped"]) == 1, rep)
seg = ('REBASE REFUSED: x\nRESULT {"schema":"result-line/1","status":"FAIL","gates":{"pass":0,"fail":1},"first_fail":'
       '"REBASE REFUSED: plan-referenced terminal #-20.\'value\' does not bind uniquely (0 sim row(s))","artefacts":[]}\n')
gate("B2 address_only: a rebase refused only on an address -> True (no hypothesis review owed)",
     GC.address_only(seg, PR.all_result_lines(seg)))
seg2 = seg + "Traceback (most recent call last):\n"
seg3 = seg + "GATE FAIL | X10 peak 700 > 680 | {}\n"
gate("B3 address_only: + a Traceback, or + another failing gate -> False (STOP gates kept)",
     not GC.address_only(seg2, PR.all_result_lines(seg2)) and not GC.address_only(seg3, PR.all_result_lines(seg3)))
import guard_peer as GP                                                                 # noqa: E402
log = "BGRUN START 2026-10-03 12:00:00 limit 3.0 min: py -u tools/stage_prerun.py --rebase p.json --graph g.json\n" + seg + "BGRUN END rc=2 after 2s\n"
gate("B4 guard_peer.log_failure: that rebase log is not a failed prediction", GP.log_failure(log, time.time()) == (False, None),
     GP.log_failure(log, time.time()))

# ---- 3. by-design EL difference on a good result
P = {"new_items": [["cond", 23166], ["local", -20]], "closed_items": [], "predicted_total": 53}
ex = ["Local Variable 'StopAll': not connected to anything", "While Loop: Conditional terminal is not wired"]
v, why, _d = ELR.by_design_verdict(ex, [], 53, 51, prediction=P)
gate("C1 143-1: 2 extra session-boundary items, re-derived 53 == measured 53 -> log", v == "log", why)
v2, why2, _d = ELR.by_design_verdict(ex + ["Insert Into Array: Contains unwired or bad terminal"], [], 54, 51, prediction=P)
v3, why3, _d = ELR.by_design_verdict(ex, ["x"], 53, 51, prediction=P)
v4, why4, _d = ELR.by_design_verdict(ex, [], 52, 51, prediction=P)
gate("C2 unexplained: another class / a missing item / a total the rule does not reproduce -> stop",
     (v2, v3, v4) == ("stop", "stop", "stop"), [why2, why3, why4])

# ---- 4. prose vs machine fields, releases, bind-time md5
sp = {"schema": "stageplan/1", "stage": "t", "actions": [{"op": "wire", "id": "w1", "src": "1.a", "dst": "2.b", "why": "I32[20] -1 " + "z" * 540}]}
gate("D1 stageplan: a 551-char `why` validates (prose, no length gate)", PR.validate_obj(sp)[0], PR.validate_obj(sp))
res = {"schema": "result/1", "id": "x", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "blocked_by": None,
       "artefacts": [], "facts": [], "open": [], "cost": {"usd": None, "minutes": 1, "labview_runs": 0}, "note": "n" * 400}
gate("D2 result/1: a 400-char note still FAILS (x-limit: the communication budget the schema states)", not PR.validate_obj(res)[0],
     PR.validate_obj(res))
gate("D3 machine_view drops `why`; negative_uids_left ignores '-1' in prose and finds -5 in an address",
     "why" not in PR.machine_view(sp)["actions"][0] and SPR.negative_uids_left(sp) == []
     and SPR.negative_uids_left({"schema": "stageplan/1", "stage": "t", "actions": [{"op": "wire", "src": {"uid": -5, "term": "a"}}]}) == [-5])
gate("D4 prose_fields(stageplan) lists goal, open_rows[].why, action.why", set(PR.prose_fields("stageplan")) >= {"$.goal", "#action.why"},
     PR.prose_fields("stageplan"))
tmp = tempfile.mkdtemp(prefix="s5_")
rv = os.path.join(tmp, "review.md")
with open(rv, "w", encoding="utf-8") as f:
    f.write("# review\n- **date:** 2026-10-02\n\nPRIOR-ART: helper-exists\n\n## What was done with it\n")
ok1, m1 = PR.write_release(rv, "FIXED", "contradicted", "tools/addrcheck.py", 1, "x")
body1 = open(rv, encoding="utf-8").read()
ok2, m2 = PR.write_release(rv, "FIXED", "helper-exists", "tools/addrcheck.py", 1, "tier (a) resolver added")
body2 = open(rv, encoding="utf-8").read()
gate("D5 release: a slug the review did not issue is refused and NOTHING written", not ok1 and "RELEASE" not in body1, m1)
gate("D6 release: a valid FIXED writes a release/1 record + the legacy line, and guard_cycle releases it",
     ok2 and len(PR.read_releases(body2)) == 1 and "\nFIXED: helper-exists - tools/addrcheck.py:1 - " in body2, m2)
card = json.load(open(os.path.join(ROOT, "tools", "bench", "cards", "task_chat-S5.json"), encoding="utf-8"))
card["id"] = "s5-selftest-md5"
card["inputs"] = [{"path": "tools/bench/cards/brief_chat-S5.md", "md5": "0" * 32}]
cp = os.path.join(tmp, "task_s5.json")
json.dump(card, open(cp, "w", encoding="utf-8"))
okb, mb = PR.bind("s5-selftest-agent", "material", cp)
gate("D7 bind refuses a card whose input md5 changed (nothing bound)", not okb and "input md5 changed" in mb
     and PR.binding("s5-selftest-agent") is None, mb)
card["inputs"][0]["md5"] = PR._md5(os.path.join(ROOT, "tools", "bench", "cards", "brief_chat-S5.md"))
gate("D8 input_md5_changes: the current md5 -> no change", PR.input_md5_changes(card) == [], PR.input_md5_changes(card))
print(PR.result_line(PR.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
