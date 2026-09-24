r"""selftest_item34 - card chat-D (user decisions 2026-09-24, items 3/4): steer/1 card, per-stage retry cap, cycle-end
LabVIEW close, and the regression self-tests they touch. NO LabVIEW, NO agents, NO serial: the LabVIEW close hook is
exercised with its three process primitives (_lv_pids / _lv_quit_graceful / _lv_kill) REPLACED by fakes; the runner
is driven with --dry-cmd on a temp bench; the retry cap by tools/bench/selftest_launch_gate.py (sandboxed records).

WHAT EXISTED FIRST: selftest_protocol.py, selftest_cycle_runner.py, selftest_cycle_runner_ff.py,
selftest_launch_gate.py (re-run here as subprocesses, unchanged except the launch gate's new C/M4-M6 cases).

PREDICTION CONTRACT (all PASS):
  S1 docs/protocol/steer.json: a well-formed steer/1 validates; one with an unknown slug / 1 evidence item does not
  S2 outcome_slugs reads the ANSWER only (the question's template lines do not count); on the two newest archived
     reviews (2026-09-24 vs 2026-09-22) the repeated set is non-empty and steer_for returns a VALID card
  S3 outcome_review.steer_after_review(write=False) reports WOULD WRITE and writes nothing (no peer dispatch)
  S4 next/1 `steer`: follow validates; refuse without evidence does not; refuse with evidence does
  S5 steer_after_cycle: follow -> followed (active_steer then None); no answer -> refused 1/2; refuse -> stop 2/2;
     add_steer_decision appends ONE valid open item to a COPY of decisions_pending.json
  S6 runner (--dry-cmd, temp bench with a steer card): cycle card carries `steer`; a session that never answers is
     STOPPED after 2 cycles, exit 3, reason names the steer, decisions_pending gets the item
  S7 labview_close_hook: dry run skipped; rig 실험중 skipped (nothing killed); none running OK; graceful OK;
     force OK; still running after force -> FAIL; tasklist unreadable -> FAIL
  S8 regression: selftest_protocol, selftest_cycle_runner, selftest_cycle_runner_ff, selftest_launch_gate all rc 0
    py tools/bgrun.py --material --max-min 15 --log tools/bench/selftest_item34.log -- py -u tools/bench/selftest_item34.py
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import protocol as P      # noqa: E402
import cycle_runner as CR  # noqa: E402

RES = []


def gate(label, ok, detail=""):
    RES.append(bool(ok))
    print("  %s  %s  %s" % ("PASS" if ok else "FAIL", label, str(detail)[:260]), flush=True)


TMP = tempfile.mkdtemp(prefix="item34_")
GOALS = P.goal_ids()
REV = sorted([os.path.join(ROOT, "archive", "peer", f) for f in os.listdir(os.path.join(ROOT, "archive", "peer"))
              if "outcome-review" in f and f.endswith(".md")], key=os.path.getmtime)
LATEST, PREV = REV[-1], REV[-2]

print("---------- S1 steer/1 schema")
steer, why = P.steer_for(LATEST, PREV, 901)
gate("S2a steer_for on the two newest archived reviews returns a card", steer is not None, why)
ok, why1 = P.validate_obj(steer, GOALS) if steer else (False, "no card")
gate("S1a a well-formed steer/1 validates (goal ids checked against docs/goalmap.json)", ok, why1)
bad = dict(steer or {}, verdicts=["not-a-slug"])
gate("S1b unknown verdict slug -> invalid", not P.validate_obj(bad)[0], P.validate_obj(bad)[1])
bad = dict(steer or {}, evidence=(steer or {}).get("evidence", [])[:1])
gate("S1c one evidence item -> invalid (needs both reviews)", not P.validate_obj(bad)[0], P.validate_obj(bad)[1])
bad = dict(steer or {}, goal_ids=["M99"])
gate("S1d a goal id not in the goal map -> invalid", not P.validate_obj(bad, GOALS)[0], P.validate_obj(bad, GOALS)[1])

print("---------- S2 outcome slugs")
q_only = "## Question\n  OUTCOME-VIOLATION: <slug>\nOUTCOME-VIOLATION: tooling-over-delivery\n"
gate("S2b the question part does not count (no '## Answer' after it)",
     P.outcome_slugs(q_only + "## Answer\nnothing\n## What was done with it\nOUTCOME-VIOLATION: ordering-stale\n") == [])
la, lb = P.outcome_slugs(open(LATEST, encoding="utf-8").read()), P.outcome_slugs(open(PREV, encoding="utf-8").read())
gate("S2c latest/previous slugs read, repeated set == card verdicts", steer and sorted(set(la) & set(lb)) == steer["verdicts"],
     "%s | %s | %s" % (os.path.basename(LATEST), la, lb))
print("  FACT  steer item %s goal_ids %s act: %s" % (steer["item"], steer["goal_ids"], steer["required_act"]) if steer else "")

print("---------- S3 outcome_review.steer_after_review(write=False)")
import outcome_review as OR  # noqa: E402  (imported for its function; nothing is dispatched)
cards_tmp = os.path.join(TMP, "cards_s3")
os.makedirs(cards_tmp)
p3, w3 = OR.steer_after_review(write=False, cards_dir=cards_tmp)
gate("S3 write=False -> WOULD WRITE, no file", p3 is None and w3.startswith("WOULD WRITE") and not os.listdir(cards_tmp), w3[:200])
p3b, w3b = OR.steer_after_review(write=True, cards_dir=cards_tmp)
gate("S3b write=True -> steer_<cycle>.json in the given cards dir, valid", bool(p3b) and P.load_card(p3b, GOALS)["schema"] == "steer/1",
     p3b)

print("---------- S4 next/1 steer answer")
NXT = {"schema": "next/1", "cycle": 901, "act": "x", "task_kind": "build", "stop_requested": False, "advances": ["M8"]}
item = steer["item"] if steer else "outcome:ordering-stale"
gate("S4a follow validates", P.validate_obj(dict(NXT, steer={"item": item, "response": "follow"}))[0])
gate("S4b refuse WITHOUT evidence is invalid", not P.validate_obj(dict(NXT, steer={"item": item, "response": "refuse"}))[0])
gate("S4c refuse with evidence validates",
     P.validate_obj(dict(NXT, steer={"item": item, "response": "refuse", "evidence": ["STATUS.md:12"]}))[0])

print("---------- S5 steer_after_cycle / active_steer / add_steer_decision")
cards5 = os.path.join(TMP, "cards5")
state5 = os.path.join(TMP, "state5.json")
sp5 = P.write_steer(dict(steer, cycle=5), cards5)
a_p, a_c = P.active_steer(cards5, state5)
gate("S5a a fresh steer card is active", a_p == sp5, a_p)
act, det = P.steer_after_cycle(sp5, steer, dict(NXT, steer={"item": item, "response": "follow"}), 6, state5)
gate("S5b follow -> followed, then no active steer", act == "followed" and P.active_steer(cards5, state5) == (None, None), det)
sp5b = P.write_steer(dict(steer, cycle=7), cards5)
gate("S5c a NEWER card for the same item is active again", P.active_steer(cards5, state5)[0] == sp5b)
act1, d1 = P.steer_after_cycle(sp5b, steer, dict(NXT), 8, state5)
act2, d2 = P.steer_after_cycle(sp5b, steer, dict(NXT, steer={"item": item, "response": "refuse", "evidence": ["x.md:1"]}), 9, state5)
gate("S5d no answer -> refused 1/2; refuse -> stop 2/2", act1 == "refused" and act2 == "stop", "%s | %s" % (d1, d2))
dp = os.path.join(TMP, "decisions_pending.json")
shutil.copyfile(os.path.join(TOOLS, "bench", "decisions_pending.json"), dp)
n0 = len(json.load(open(dp, encoding="utf-8"))["items"])
did, derr = P.add_steer_decision(steer, 9, P._json_load(state5, {})["items"][item]["refusals"], dp)
d = json.load(open(dp, encoding="utf-8"))
gate("S5e add_steer_decision appends ONE open item, file validates", did and len(d["items"]) == n0 + 1
     and d["items"][-1]["status"] == "open" and P.validate_obj(d, GOALS)[0], did or derr)

print("---------- S6 runner with a steer card (--dry-cmd, temp bench)")
case = os.path.join(TMP, "run6")
bench6 = os.path.join(case, "bench")
os.makedirs(os.path.join(bench6, "cards"))
sp6 = os.path.join(case, "STATUS.md")
open(sp6, "w", encoding="utf-8").write("# STATUS (self-test)\n\n## NEXT\nfirst.\n")
P.write_steer(dict(steer, cycle=1), os.path.join(bench6, "cards"))
shutil.copyfile(os.path.join(TOOLS, "bench", "decisions_pending.json"), os.path.join(bench6, "decisions_pending.json"))
sess = os.path.join(TMP, "sess.py")
open(sess, "w", encoding="utf-8").write(
    "import sys, json, os, time\n"
    "json.dump({'schema': 'next/1', 'cycle': 1, 'act': 'self-test act', 'task_kind': 'build', 'stop_requested': False,\n"
    "           'advances': ['M8'], 'note': 'turn %s' % time.time()}, open(os.path.join(sys.argv[1], 'next.json'), 'w'))\n"
    "print('session done')\n")
if " " in TMP or " " in sys.executable:
    gate("S6 space-free temp and interpreter paths (--dry-cmd is whitespace-split)", False, TMP)
else:
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "cycle_runner.py"), "--dry-cmd", "%s %s %s" % (sys.executable, sess, bench6),
                        "--cycles", "4", "--status", sp6, "--bench-dir", bench6, "--max-min", "2"],
                       cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    log = open(os.path.join(bench6, "cycle_runner.log"), encoding="utf-8").read()
    c1 = json.load(open(os.path.join(bench6, "cards", "cycle_1.json"), encoding="utf-8"))
    gate("S6a cycle_1.json carries the steer path + md5", (c1.get("steer") or {}).get("path", "").endswith("steer_1.json")
         and len((c1.get("steer") or {}).get("md5") or "") == 32, c1.get("steer"))
    gate("S6b two unanswered cycles -> RUNNER STOP exit 3 naming the steer", r.returncode == 3
         and "steering card" in log and log.count("CYCLE-CARD |") == 2, "rc %s | %s" % (r.returncode, log.strip().splitlines()[-1][:200]))
    items = json.load(open(os.path.join(bench6, "decisions_pending.json"), encoding="utf-8"))["items"]
    gate("S6c decisions_pending (temp bench) got the open steer item", items[-1]["status"] == "open" and "Steering card" in items[-1]["question"],
         items[-1]["id"])
    gate("S6d LABVIEW-CLOSE skipped under --dry-cmd (logged)", "LABVIEW-CLOSE |" in log and "skipped (dry run" in log)

print("---------- S7 labview_close_hook with fake process primitives")
A = argparse.Namespace(dry_run=False, dry_cmd="", no_labview_close=False)
ASM = "rig-state: assembled\n"
rl = os.path.join(TMP, "runner7.log")
CR.LV_GRACE_S, CR.LV_FORCE_WAIT_S = 0.2, 0.2
calls = []


def fake(pid_seq, quit_msg="quit rc=0"):
    seq = list(pid_seq)
    CR._lv_pids = lambda: (seq.pop(0) if len(seq) > 1 else seq[0])
    CR._lv_quit_graceful = lambda t: calls.append("quit") or quit_msg
    CR._lv_kill = lambda: calls.append("kill") or "taskkill rc=0"


ok, why = CR.labview_close_hook(1, argparse.Namespace(dry_run=True, dry_cmd="", no_labview_close=False), TMP, rl, ASM)
gate("S7a dry run -> skipped", ok and why == "skipped", why)
calls.clear()
fake([[123]])
ok, why = CR.labview_close_hook(1, A, TMP, rl, "rig-state: 실험중\n")
gate("S7b rig 실험중 -> skipped, nothing quit or killed", ok and "skipped" in why and calls == [], (why, calls))
fake([[]])
ok, why = CR.labview_close_hook(1, A, TMP, rl, ASM)
gate("S7c none running -> OK", ok and "no LabVIEW" in why, why)
calls.clear()
fake([[123], []])
ok, why = CR.labview_close_hook(1, A, TMP, rl, ASM)
gate("S7d graceful quit closes it -> OK, no kill", ok and "gracefully" in why and calls == ["quit"], (why, calls))
calls.clear()
fake([[123], [123], [123], [], []])
ok, why = CR.labview_close_hook(1, A, TMP, rl, ASM)
gate("S7e quit fails, force works -> OK forced", ok and "forced" in why and calls == ["quit", "kill"], (why, calls))
calls.clear()
fake([[123]])
ok, why = CR.labview_close_hook(1, A, TMP, rl, ASM)
gate("S7f still running after quit + force -> FAIL", not ok and "still running" in why, why)
fake([None])
ok, why = CR.labview_close_hook(1, A, TMP, rl, ASM)
gate("S7g tasklist unreadable -> FAIL", not ok and "tasklist" in why, why)

print("---------- S8 regression self-tests")
for name in ("selftest_protocol.py", "selftest_cycle_runner.py", "selftest_cycle_runner_ff.py", "selftest_launch_gate.py"):
    r = subprocess.run([sys.executable, "-u", os.path.join(HERE, name)], cwd=ROOT, capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=900)
    tail = [ln for ln in (r.stdout or "").splitlines() if ln.strip()][-3:]
    bads = [ln.strip()[:150] for ln in (r.stdout or "").splitlines() if ln.strip().startswith(("FAIL", "BAD"))]
    gate("S8 %s rc 0" % name, r.returncode == 0, " | ".join(bads[:3] or tail))

shutil.rmtree(TMP, ignore_errors=True)
npass, nfail = sum(RES), len(RES) - sum(RES)
print("=== GATES: %d pass / %d fail" % (npass, nfail))
print(P.result_line(P.make_result(npass, nfail, None if nfail == 0 else "selftest_item34 case failed")))
sys.exit(0 if nfail == 0 else 1)
