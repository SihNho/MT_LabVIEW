# ---
# labview: none
# hardware: none
# ---
"""Self-test of cycle_runner's RETRO-UNDISPOSED gates_due entry (card 147-a1-5). Offline: temp dirs only, no claude
session, no LabVIEW, no real archive file is read for the verdict or written.
Existing pieces reused: cycle_runner.retro_undisposed / retro_undisposed_item / gates_due_hook / write_cycle_card,
modelled on selftest_cycle_runner_ff.py (temp bench, log grep, protocol.result_line).
PREDICTION:
 (i)   newest retrospective has the placeholder disposition -> item {gate retro-undisposed, due True}, one
       'RETRO-UNDISPOSED <path>' log line, gates_due_hook's list carries it, the cycle/1 card with it validates
 (ii)  newest retrospective has a filled disposition -> no item, nothing logged
 (iii) no retrospective file at all (empty dir; and a missing dir) -> no item, no exception
 (iv)  an OLDER placeholder file and a NEWER filled one (by mtime, the hook's rule) -> no item
Usage: py tools/bench/selftest_cycle_runner_retro.py"""
import os
import sys
import tempfile
import time
import types

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import cycle_runner as CR  # noqa: E402
import protocol  # noqa: E402

PLACE = "# Retrospective\n\nbody\n\n## What was done with it\n\n(Claude fills in)\n"
FILLED = PLACE.replace("(Claude fills in)", "- finding 1 accepted: tools/cycle_runner.py:991 now checks the disposition; "
                       "finding 2 refuted against docs/violation-decisions.md:1935 because the slug was already decided.")
ok = fail = 0


def check(label, cond, extra=""):
    global ok, fail
    if cond:
        ok += 1
    else:
        fail += 1
    print("%s %s %s" % ("PASS" if cond else "FAIL", label, extra))


def case(files, logname):
    peer = tempfile.mkdtemp(prefix="retro_peer_")
    for i, (name, body) in enumerate(files):
        p = os.path.join(peer, name)
        with open(p, "w", encoding="utf-8") as f:
            f.write(body)
        t = time.time() - 100 + i * 10
        os.utime(p, (t, t))
    log = os.path.join(tempfile.mkdtemp(prefix="retro_log_"), logname)
    return peer, log


def logtext(p):
    return open(p, encoding="utf-8").read() if os.path.exists(p) else ""


# (i) placeholder
peer, log = case([("2026-10-08-retrospective-cycle999.md", PLACE)], "r1.log")
try:
    item = CR.retro_undisposed_item(999, peer, log)
    exc = None
except Exception as e:  # noqa: BLE001
    item, exc = None, e
check("(i) placeholder -> item", bool(item) and item.get("gate") == "retro-undisposed" and item.get("due") is True
      and exc is None, str(item)[:160])
check("(i) RETRO-UNDISPOSED logged", "RETRO-UNDISPOSED " in logtext(log) and "cycle999" in logtext(log))
# gates_due_hook integration: gates_due / next_json_reading stubbed so nothing real is read or run
saved = (CR.gates_due, CR.next_json_reading)
CR.gates_due = lambda bench, pd, card: [{"gate": "violations", "due": False, "detail": "stub"}]
CR.next_json_reading = lambda bench: (None, {}, None)
try:
    a = types.SimpleNamespace(peer_dir=peer, dry_run=True, dry_cmd="", outcome_cmd="", max_min=60)
    items = CR.gates_due_hook(999, a, os.path.dirname(log), log)
finally:
    CR.gates_due, CR.next_json_reading = saved
got = [x for x in items if x["gate"] == "retro-undisposed"]
check("(i) gates_due_hook list carries it", len(got) == 1 and got[0]["due"] is True)
check("(i) GATES-DUE line shows retro-undisposed=DUE", "retro-undisposed=DUE" in logtext(log))
card = {"schema": "cycle/1", "cycle": 999, "rig_state": "unknown", "model": "m", "effort": "high", "firefighter": None,
        "bed": None, "errorlist": None, "steer": None, "motor_session": None, "next": "tools/bench/next.json",
        "budget": {"minutes": 60.0, "dispatches": 8}, "rules": CR.CYCLE_RULES, "gates_due": items}
v_ok, v_why = protocol.validate_obj(card)
check("(i) cycle/1 card with the entry validates", v_ok, str(v_why)[:160])

# (ii) filled
peer, log = case([("2026-10-08-retrospective-cycle999.md", FILLED)], "r2.log")
item = CR.retro_undisposed_item(999, peer, log)
check("(ii) filled -> no item, nothing logged", item is None and "RETRO-UNDISPOSED" not in logtext(log))

# (iii) no retrospective at all; and a missing peer dir
peer, log = case([("2026-10-08-other-review.md", PLACE)], "r3.log")
try:
    item, exc = CR.retro_undisposed_item(999, peer, log), None
except Exception as e:  # noqa: BLE001
    item, exc = None, e
check("(iii) no retrospective -> no item, no exception", item is None and exc is None and logtext(log) == "")
try:
    item, exc = CR.retro_undisposed_item(999, os.path.join(peer, "missing_dir"), log), None
except Exception as e:  # noqa: BLE001
    item, exc = None, e
check("(iii) missing peer dir -> no item, no exception", item is None and exc is None)

# (iv) older placeholder, newer filled (newest by mtime decides, guard_peer.py:840-843)
peer, log = case([("2026-10-07-retrospective-cycle998.md", PLACE), ("2026-10-08-retrospective-cycle999.md", FILLED)],
                 "r4.log")
check("(iv) newer filled wins -> no item", CR.retro_undisposed_item(999, peer, log) is None)

print("%d/%d PASS" % (ok, ok + fail))
print(protocol.result_line(protocol.make_result(ok, fail, None if not fail else "%d failed" % fail)))
sys.exit(0 if not fail else 1)
