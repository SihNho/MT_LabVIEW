"""Self-test of cycle_runner's JUDGEMENT LADDER + JUDGE A/B (card chat-M1, user 2026-09-26; rungs re-set by the user's
model table 2026-09-27, card chat-N4: 0 opus high -> 1 opus MAX -> 2 fable low -> STOP; A/B default off; firefighter
= one Opus max cycle on rank 1). Dry: no session, no LabVIEW.
Existing checked first: selftest_cycle_runner_ff.py (the --dry-cmd stand-in pattern, reused here); protocol.validate_obj.
PREDICTION (12 gates):
  L1 unchanged next.json -> level 0 -> 1           L2 judgement slug twice (retro files) -> level 2
  L3 a PASS result card with artefacts, or a newly-done milestone -> reset to 0
  L4 level 2 (top) triggered again -> stop=True, and the decisions_pending item validates
  L5 ff + ladder never above fable/low (every level x ff rung); ff alone = rank 1 opus/max
  A1 A/B parity: odd cycle medium, even high     A2 A/B off after 2026-09-28 07:00 KST (auto) and when mode=off
  A3 a raised ladder level overrides the A/B effort
  D1 runner defaults: --effort high, --judge-ab off, FF claude-opus-5-5/max one rung
  I0 dry run with DEFAULT flags: cycle 1 card claude-opus-5-5/high, no JUDGE-AB line
  I1 dry run, A/B on: cycle 1 card effort medium, cycle 2 card effort high, JUDGE-AB lines logged
  I2 dry run: next.json moved in cycle 1 only -> cycle 3 claude-opus-5-5/max 'level 1', cycle 4 fable/low
  I3 ... and after cycle 4 (3rd unchanged) RUNNER STOP, no cycle 5
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
lv1, _, stop1 = CR.judge_ladder_step(1, False, set(), "")
lv, why, stop = CR.judge_ladder_step(2, False, set(), "")
dp = os.path.join(cards, "decisions_pending.json")
did, derr = CR.add_judge_decision(9, why, ["M3", "R1"], dp)
okd = did is not None and protocol.validate_obj(json.load(open(dp, encoding="utf-8")))[0]
gate("L4", stop and lv == 2 and lv1 == 2 and not stop1 and "fable/low" in why and okd,
     "stop=%s did=%s err=%s why=%s" % (stop, did, derr, why))

# L5
worst = set()
for level in range(0, 6):
    for rec, rung in ((None, 0), ("recipe:x", 0), ("recipe:x", 1)):
        r, m, e = CR.judge_choice(level, rec, rung, "claude-opus-5-5", "high")
        worst.add((r, m, e))
ranks = {r for r, _, _ in worst}
gate("L5", max(ranks) == 2 and (2, "fable", "low") in worst and CR.JUDGE_TOP == 2 and
     CR.judge_choice(0, None, 0, "claude-opus-5-5", "high") == (0, "claude-opus-5-5", "high") and
     CR.judge_choice(0, "recipe:x", 0, "claude-opus-5-5", "high") == (1, "claude-opus-5-5", "max") and
     CR.judge_choice(2, "recipe:x", 0, "claude-opus-5-5", "high") == (2, "fable", "low"), sorted(worst))

# A1-A3
before_until = CR.JUDGE_AB_UNTIL - 60
a1 = (CR.judge_ab_effort(1, "auto", before_until)[0], CR.judge_ab_effort(2, "auto", before_until)[0],
      CR.judge_ab_effort(87, "auto", before_until)[0])
gate("A1", a1 == ("medium", "high", "medium"), a1)
a2 = (CR.judge_ab_effort(2, "auto", CR.JUDGE_AB_UNTIL + 1)[0], CR.judge_ab_effort(2, "off", before_until)[0])
gate("A2", a2 == (None, None) and time.strftime("%Y-%m-%d %H:%M", time.localtime(CR.JUDGE_AB_UNTIL)) == "2026-09-28 07:00", a2)
eff = CR.judge_ab_effort(1, "on")[0]
gate("A3", CR.judge_choice(1, None, 0, "claude-opus-5-5", eff) == (1, "claude-opus-5-5", "max") and
     CR.judge_choice(2, None, 0, "claude-opus-5-5", eff) == (2, "fable", "low"), eff)

# D1 - parser defaults read from the source (the runner is not imported with argv)
src = open(os.path.join(ROOT, "tools", "cycle_runner.py"), encoding="utf-8").read()
gate("D1", 'ap.add_argument("--effort", default="high")' in src and 'ap.add_argument("--judge-ab", default="off"' in src
     and (CR.FF_MODEL, CR.FF_EFFORT, CR.FF_LADDER) == ("claude-opus-5-5", "max", ("max",)) and CR.FF_RANK == {"max": 1},
     "%s/%s %s %s" % (CR.FF_MODEL, CR.FF_EFFORT, CR.FF_LADDER, CR.FF_RANK))


def dry(cycles, ab, move):
    bench = tempfile.mkdtemp(prefix="ladbench_")
    status = os.path.join(bench, "STATUS.md")
    open(status, "w", encoding="utf-8").write("## NEXT\nx\n")
    emptypeer = tempfile.mkdtemp(prefix="ladpeer0_")
    env = dict(os.environ, LAD_BENCH=bench, LAD_MOVE=move)
    r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "cycle_runner.py"), "--cycles", str(cycles),
                        "--bench-dir", bench, "--status", status] + (["--judge-ab", ab] if ab else []) +
                       ["--peer-dir", emptypeer,
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


r, log, card = dry(1, None, "always")
gate("I0", (card(1).get("model"), card(1).get("effort")) == ("claude-opus-5-5", "high") and "JUDGE-AB" not in log,
     "%s/%s" % (card(1).get("model"), card(1).get("effort")))
if not gates[-1][1]:
    print(log)
r, log, card = dry(2, "on", "always")
gate("I1", card(1).get("effort") == "medium" and card(2).get("effort") == "high" and
     "JUDGE-AB | cycle 1 | medium" in log and "JUDGE-AB | cycle 2 | high" in log,
     "%s %s" % (card(1).get("effort"), card(2).get("effort")))
if not gates[-1][1]:
    print(log)
# I2/I3 (card chat-M1b, rungs chat-N4): next.json moves in cycle 1 only; cycles 2..4 unchanged
# -> cycle 3 opus/max, cycle 4 fable/low, after cycle 4 (3rd unchanged, at the top rung) RUNNER STOP.
r, log, card = dry(6, "off", "once")
c2, c3, c4 = card(2), card(3), card(4)
gate("I2", (c2.get("model"), c2.get("effort")) == ("claude-opus-5-5", "high")
     and (c3.get("model"), c3.get("effort")) == ("claude-opus-5-5", "max") and "level 1" in c3.get("note", "")
     and (c4.get("model"), c4.get("effort")) == ("fable", "low")
     and "level 0 -> 1" in log and "the loop is not moving" not in log,
     "%s/%s %s/%s %s/%s" % (c2.get("model"), c2.get("effort"), c3.get("model"), c3.get("effort"), c4.get("model"), c4.get("effort")))
gate("I3", not card(5) and "judgement ladder is exhausted" in log and r.returncode == 3,
     "runner-exit %d card5=%s" % (r.returncode, bool(card(5))))
if not (gates[-1][1] and gates[-2][1]):
    print(log)

n_pass = sum(ok for _, ok in gates)
first = next((l for l, ok in gates if not ok), None)
print("%d/%d PASS" % (n_pass, len(gates)))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first)))
sys.exit(0 if first is None else 1)
