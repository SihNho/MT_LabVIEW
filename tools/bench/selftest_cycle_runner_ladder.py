"""Self-test of cycle_runner's JUDGEMENT LADDER + JUDGE A/B (card chat-M1, user 2026-09-26). Dry: no session, no LabVIEW.
Existing checked first: selftest_cycle_runner_ff.py (the --dry-cmd stand-in pattern, reused here); protocol.validate_obj.
PREDICTION (10 gates):
  L1 unchanged next.json -> level 0 -> 1           L2 judgement slug twice (retro files) -> level 2
  L3 a PASS result card with artefacts, or a newly-done milestone -> reset to 0
  L4 level 3 triggered again -> stop=True, and the decisions_pending item validates
  L5 ff + ladder never above fable/medium (every level x ff rung)
  A1 A/B parity: odd cycle medium, even high     A2 A/B off after 2026-09-28 07:00 KST (auto) and when mode=off
  A3 a raised ladder level overrides the A/B effort
  I1 dry run, A/B on: cycle 1 card effort medium, cycle 2 card effort high, JUDGE-AB lines logged
  I2 dry run: next.json moved in cycle 1 only -> cycle 3 runs claude-opus-5-5/high, card note 'level 1'
Usage: py tools/bench/selftest_cycle_runner_ladder.py"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))

if len(sys.argv) > 1 and sys.argv[1] == "stand-in":
    bench = os.environ["LAD_BENCH"]
    cnt = os.path.join(bench, "count.txt")
    c = int(open(cnt).read() or 0) + 1 if os.path.exists(cnt) else 1
    open(cnt, "w").write(str(c))
    if c == 1 or os.environ.get("LAD_MOVE") == "always":
        with open(os.path.join(bench, "next.json"), "w", encoding="utf-8") as f:
            json.dump({"schema": "next/1", "cycle": c, "act": "ladder self-test %d" % c, "task_kind": "build",
                       "stop_requested": False, "advances": ["M3"]}, f)
    time.sleep(1.1)
    sys.exit(0)

import cycle_runner as CR  # noqa: E402
import protocol  # noqa: E402

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("%s %s %s" % ("PASS" if ok else "**FAIL", label, detail))


# L1
lv, why, stop = CR.judge_ladder_step(0, False, set(), "")
gate("L1", lv == 1 and not stop and "UNCHANGED" in why, why)

# L2 - slugs read from retrospective FILES created in the window
peer = tempfile.mkdtemp(prefix="ladpeer_")
t0 = time.time() - 1
open(os.path.join(peer, "2026-09-26-retrospective-cycle1.md"), "w").write("x\nVIOLATION: wrong-ordering | loss_min=5\n")
s1 = CR.retro_slugs_in_window(peer, t0, time.time() + 1)
lv, _, _ = CR.judge_ladder_step(0, True, s1, "")
open(os.path.join(peer, "2026-09-26-retrospective-cycle2.md"), "w").write("VIOLATION: judgement-in-material | x\n")
s2 = CR.retro_slugs_in_window(peer, time.time() - 0.5, time.time() + 1)
lv2, why2, _ = CR.judge_ladder_step(lv, True, s2, "")
other, _, _ = CR.judge_ladder_step(0, True, {"scope-creep"}, "")
gate("L2", lv == 1 and lv2 == 2 and other == 0 and "judgement-in-material" in why2, "%s %s -> %d" % (s1, s2, lv2))

# L3
cards = tempfile.mkdtemp(prefix="ladcards_")
gm = os.path.join(cards, "goalmap.json")
json.dump({"milestones": [{"id": "M3", "status": "active"}]}, open(gm, "w"))
before = CR.goalmap_done(gm)
ta = time.time() - 1
d0 = CR.delivered_in_window(cards, ta, time.time() + 1, before, gm)
json.dump({"schema": "result/1", "id": "x", "status": "PASS", "artefacts": [{"path": "a", "md5": None}]},
          open(os.path.join(cards, "result_x.json"), "w"))
d1 = CR.delivered_in_window(cards, ta, time.time() + 1, before, gm)
os.remove(os.path.join(cards, "result_x.json"))
json.dump({"schema": "result/1", "id": "y", "status": "PASS", "artefacts": []}, open(os.path.join(cards, "result_y.json"), "w"))
d_empty = CR.delivered_in_window(cards, ta, time.time() + 1, before, gm)
json.dump({"milestones": [{"id": "M3", "status": "done"}]}, open(gm, "w"))
d2 = CR.delivered_in_window(cards, ta, time.time() + 1, before, gm)
lv, why, _ = CR.judge_ladder_step(2, False, {"wrong-ordering"}, d1)
gate("L3", d0 == "" and d_empty == "" and "PASS card" in d1 and "M3" in d2 and lv == 0, "%r %r %r -> %d" % (d0, d1, d2, lv))

# L4
lv, why, stop = CR.judge_ladder_step(3, False, set(), "")
dp = os.path.join(cards, "decisions_pending.json")
did, derr = CR.add_judge_decision(9, why, ["M3", "R1"], dp)
okd = did is not None and protocol.validate_obj(json.load(open(dp, encoding="utf-8")))[0]
gate("L4", stop and lv == 3 and okd, "stop=%s did=%s err=%s" % (stop, did, derr))

# L5
worst = set()
for level in range(0, 6):
    for rec, rung in ((None, 0), ("recipe:x", 0), ("recipe:x", 1)):
        r, m, e = CR.judge_choice(level, rec, rung, "claude-opus-5-5", "medium")
        worst.add((r, m, e))
ranks = {r for r, _, _ in worst}
gate("L5", max(ranks) == 3 and (3, "fable", "medium") in worst and
     CR.judge_choice(0, "recipe:x", 0, "claude-opus-5-5", "medium") == (2, "fable", "low") and
     CR.judge_choice(1, "recipe:x", 1, "claude-opus-5-5", "medium") == (3, "fable", "medium"), sorted(worst))

# A1-A3
before_until = CR.JUDGE_AB_UNTIL - 60
a1 = (CR.judge_ab_effort(1, "auto", before_until)[0], CR.judge_ab_effort(2, "auto", before_until)[0],
      CR.judge_ab_effort(87, "auto", before_until)[0])
gate("A1", a1 == ("medium", "high", "medium"), a1)
a2 = (CR.judge_ab_effort(2, "auto", CR.JUDGE_AB_UNTIL + 1)[0], CR.judge_ab_effort(2, "off", before_until)[0])
gate("A2", a2 == (None, None) and time.strftime("%Y-%m-%d %H:%M", time.localtime(CR.JUDGE_AB_UNTIL)) == "2026-09-28 07:00", a2)
eff = CR.judge_ab_effort(1, "on")[0]
gate("A3", CR.judge_choice(1, None, 0, "claude-opus-5-5", eff) == (1, "claude-opus-5-5", "high") and
     CR.judge_choice(2, None, 0, "claude-opus-5-5", eff) == (2, "fable", "low"), eff)


def dry(cycles, ab, move):
    bench = tempfile.mkdtemp(prefix="ladbench_")
    status = os.path.join(bench, "STATUS.md")
    open(status, "w", encoding="utf-8").write("## NEXT\nx\n")
    emptypeer = tempfile.mkdtemp(prefix="ladpeer0_")
    env = dict(os.environ, LAD_BENCH=bench, LAD_MOVE=move)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "cycle_runner.py"), "--cycles", str(cycles),
                        "--bench-dir", bench, "--status", status, "--judge-ab", ab, "--peer-dir", emptypeer,
                        "--goalmap", os.path.join(bench, "nogoalmap.json"), "--no-motor-hooks",
                        "--no-errorlist-hook", "--no-labview-close",
                        "--dry-cmd", "py tools/bench/selftest_cycle_runner_ladder.py stand-in"],
                       capture_output=True, text=True, env=env, cwd=ROOT)
    log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()

    def card(n):
        try:
            return json.load(open(os.path.join(bench, "cards", "cycle_%d.json" % n), encoding="utf-8"))
        except (OSError, ValueError):
            return {}
    return r, log, card


r, log, card = dry(2, "on", "always")
gate("I1", card(1).get("effort") == "medium" and card(2).get("effort") == "high" and
     "JUDGE-AB | cycle 1 | medium" in log and "JUDGE-AB | cycle 2 | high" in log,
     "%s %s" % (card(1).get("effort"), card(2).get("effort")))
if not gates[-1][1]:
    print(log)
r, log, card = dry(3, "off", "once")
c3 = card(3)
gate("I2", c3.get("model") == "claude-opus-5-5" and c3.get("effort") == "high" and "level 1" in c3.get("note", "")
     and "level 0 -> 1" in log and "JUDGE-LADDER |" in log, "%s/%s note=%r" % (c3.get("model"), c3.get("effort"),
                                                                            c3.get("note", "")[:80]))
if not gates[-1][1]:
    print(log)

n_pass = sum(ok for _, ok in gates)
first = next((l for l, ok in gates if not ok), None)
print("%d/%d PASS" % (n_pass, len(gates)))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
sys.exit(0 if first is None else 1)
