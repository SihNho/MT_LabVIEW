# ---
# labview: none
# hardware: none
# ---
"""card chat-E3: REPLAY the failure records of cycles 142-143 through the new write-time / launch-time checks.
OFFLINE, read-only on the real records (result cards, logs, launch ledger, gate_fp queue); fixtures in %TEMP%.
For each record: which check now catches it (write | launch | WAITING | earlier card chat-S5 | not catchable here) and the
card minutes involved (result_<id>.json cost.minutes - an UPPER bound for what an early catch saves; '?' when the record
does not give the share).
PREDICTION: 143-1 release slug, 143-P1 stale pin + WAITING, fp-36..39 -> caught here; 143-5 f1/f2 and 143-3/4 -> chat-S5;
142-1, 142-2, 142-P1, 143-1 Error List -> not catchable offline; 142-4 run 1 (runtime data shape) -> not caught.
"""
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
os.chdir(ROOT)
XT = tempfile.mkdtemp(prefix="e3replay_")
CARDS = os.path.join(XT, "cards")
os.makedirs(CARDS)
os.environ["GUARD_WRITE_CARDS"] = CARDS
sys.path.insert(0, TOOLS)
sys.path.insert(0, os.path.join(TOOLS, "hooks"))
import protocol as P      # noqa: E402
import stop_record as SR  # noqa: E402
import guard_cycle as GC  # noqa: E402
import guard_write as GW  # noqa: E402
import stage_prerun as SP  # noqa: E402

BC = os.path.join(HERE, "cards")


def mins(cid):
    try:
        return json.load(open(os.path.join(BC, "result_%s.json" % cid), encoding="utf-8"))["cost"]["minutes"]
    except Exception:          # noqa: BLE001
        return "?"


ROWS = []
OK = []


def row(rec, where, minutes, evidence, ok=True):
    ROWS.append((rec, where, minutes, evidence))
    OK.append(ok)
    print("  %-38s | %-34s | %5s min | %s" % (rec, where, minutes, str(evidence)[:170]), flush=True)


try:
    # 143-1: release line written with a review slug instead of the verdict slug (refused at first launch try)
    rv = os.path.join(XT, "2026-10-03-priorart-c143-1-replay.md")
    src = os.path.join(ROOT, "archive", "peer", "2026-10-03-priorart-c143-1-p4s02v18.md")
    body = open(src, encoding="utf-8", errors="replace").read() if os.path.exists(src) else "PRIOR-ART: contradicted\n"
    body = body.split(GC.DISPOSITION_MARK)[0] + "\n%s\nFIXED: stale-limit - tools/recipes/stage_d1_ring_p4_s02v18.py:47 - x\n" \
        % GC.DISPOSITION_MARK
    open(rv, "w", encoding="utf-8").write(body)
    pr = GW.check_review(rv)
    row("143-1 release line, review slug", "WRITE (guard_write.check_review)", "?",
        pr[0] if pr else "NOT CAUGHT", bool(pr))
    # 143-P1: worked on the s02v18 pair pinned at 758b1673/fdf58b0a while 143-1 changed it
    card = json.load(open(os.path.join(BC, "task_143-P1.json"), encoding="utf-8"))
    json.dump(card, open(os.path.join(CARDS, "task_143-P1.json"), "w", encoding="utf-8"))
    pins = GW.open_card_pins(os.path.join(TOOLS, "recipes", "stage_d1_ring_p4_s02v18.py"))
    row("143-P1 stale copy of the s02v18 pair", "WRITE (open-card pin, in 143-1's turn)", mins("143-P1"),
        pins[0] if pins else "NOT CAUGHT", bool(pins))
    # 143-P1 / 141-P1 / 140-P1: dry FAIL 'E1 BASE unbound' on a provisional base -> WAITING
    real = SP.provisional_dry_graph
    SP.provisional_dry_graph = lambda r: ("base_provisional.json", None)     # the logs' graph IS base_provisional.json
    for cid, lg in (("143-P1", "prep_c143_p1_dry.log"), ("141-P1", "prep_c141_p1_dry.log"), ("140-P1", "prep_c140_p1_dry.log")):
        p = os.path.join(HERE, lg)
        if not os.path.exists(p):
            continue
        text = open(p, encoding="utf-8", errors="replace").read()
        fails = [ln.split("first_fail=", 1)[1] for ln in text.splitlines() if ln.startswith("=== DRY FAIL")]
        prov = "base_provisional" in text
        w = SP.waiting_reason("r.py", {"status": "FAIL", "fails": fails}) if prov else None
        row("%s dry on a provisional base" % cid, "WAITING (no FAIL, no review)" if w else "still FAIL", mins(cid),
            w or (fails[:1] or ["no DRY FAIL line"])[0], bool(w))
    SP.provisional_dry_graph = real
    # fp-36: 142-4 (labview build) held by 142-P2's offline failing log
    lg = os.path.join(HERE, "prep_c142_p2_q1.log")
    owner = P.log_owner(lg)
    row("fp-36 142-4 held by 142-P2's log", "LAUNCH (guard_peer RULE-OTHER-CARD)", "?",
        "log owner %s != 142-4" % owner, owner == "142-P2")
    c37 = ("py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c142_5_scrreq.log -- py -u "
           "tools/stage_prerun.py --scratch-required tools/recipes/stage_d1_ring_p4_s02v18.py")
    row("fp-37 stage_prerun --scratch-required", "LAUNCH (header: offline checker)", "?",
        "stop_record.offline_checker %s, guard_cycle.offline_only %s" % (SR.offline_checker(c37), GC.offline_only(c37)),
        SR.offline_checker(c37) and GC.offline_only(c37))
    cls = SR.segment_class("git add tools/recipes/stage_d1_ring_p4_s03v18.py tools/recipes/stage_d1_ring_p4_s03v18_scratch.py")
    row("fp-38 git add of recipe paths", "LAUNCH (not a launch: read-only)", "?", "segment_class %s" % cls, cls == "readonly")
    t143_3 = json.load(open(os.path.join(BC, "task_143-3.json"), encoding="utf-8"))
    c39 = ("py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c143_3_adopt.log -- py -u tools/stagexec.py "
           "adopt --script tools/recipes/stage_d1_ring_p4_s02v18_scratch.py --log tools/bench/diag_c143_1_scratch.log")
    t143_3 = dict(t143_3, requires=None)
    r = P.check_command(t143_3, c39)
    row("fp-39 stagexec adopt under labview %s" % t143_3["flags"].get("labview"), "LAUNCH (header offline-args)", "?",
        r or "allowed", r is None)
    # earlier card chat-S5 (PD337): prose length no longer gated; gate tokeniser reads the machine view; addrcheck
    plan = json.load(open(os.path.join(HERE, "plan_ring_p4_s03v18.json"), encoding="utf-8"))
    plan["actions"][0]["why"] = "x" * 545
    row("143-5 f1 why 545 > 400", "ELIMINATED by chat-S5 (PD337(d))", mins("143-5"), P.validate_obj(plan)[1])
    row("143-5 f2 gate tokenised a why", "ELIMINATED by chat-S5 (machine_view)", "(same)",
        "why stripped: %s" % ("why" not in json.dumps(P.machine_view(plan)["actions"][0])))
    row("143-3 / 143-4 plan address vs graph", "chat-S5 addrcheck (prerun)", "%s+%s" % (mins("143-3"), mins("143-4")),
        "tools/addrcheck.py tier (a), not this card")
    for cid, what in (("142-1", "delete_object count"), ("142-2", "scaffold terminal"), ("142-P1", "rebase shape"),
                      ("143-1", "Error List 53 vs 51/52")):
        row("%s %s" % (cid, what), "NOT CATCHABLE offline (LabVIEW)", mins(cid), "scripting-function / real-graph fact")
    row("142-4 run 1 import crash (dict wire src)", "NOT CAUGHT (runtime data shape)", "?",
        "compiles; fails only on the plan data at run time (build_ringseqcheck_v0.py:26)")
finally:
    shutil.rmtree(XT, ignore_errors=True)

caught = [r for r in ROWS if r[1].startswith(("WRITE", "LAUNCH", "WAITING"))]
m = sum(x for x in (r[2] for r in caught) if isinstance(x, (int, float)))
print("CAUGHT BY THIS CARD: %d records; card minutes on them (upper bound, '?' excluded): %d" % (len(caught), m))
n_fail = sum(1 for o in OK if not o)
print(P.result_line(P.make_result(len(OK) - n_fail, n_fail, None if not n_fail else "a predicted catch did not happen")))
