"""selftest_retry_cap - the retry-cap RECORDER repair (card 78-2; docs/violation-decisions.md
"device-failed - 2026-09-25 07:05").

What existed: tools/stage_prerun.py check_cap/record_stage_run/retry_card (cap logic, unchanged), the hook
tools/hooks/guard_bash.py (used to RECORD in main(); now only checks), tools/bgrun.py (now records at child start).
No earlier self-test of the cap existed (grep selftest_*cap*: none).

Prediction contract (all against a TEMP stage_runs file via STAGE_RUNS, cycle forced by STAGE_RUNS_CYCLE):
  C1 guard_bash hook on a real stage launch (hook allows or refuses - either) -> count unchanged
  C2 guard_cycle hook on the same launch -> count unchanged
  C3 a bgrun whose child never starts (missing interpreter = the permission-layer stand-in: no child) -> unchanged
  C4 bgrun of a dummy tools/recipes/stage_*.py -> +1, line has by=bgrun, cycle, card=None, log line printed
  C5 second run -> 2; check_cap now REFUSES a 3rd
  C6 --retry-card <task/1 retry_of=stage> -> check_cap allows; that bgrun records card id; same card again refused
  C7 the real stage_runs.jsonl lines (hook-written, no `by`) seeded into the temp file do not count
  C8 the real tools/bench/stage_runs.jsonl is byte-unchanged by this self-test
Ends with a C6 RESULT line.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TOOLS = os.path.join(ROOT, "tools")
REAL_RUNS = os.path.join(TOOLS, "bench", "stage_runs.jsonl")
TMP = tempfile.mkdtemp(prefix="rcst_")
RUNS = os.path.join(TMP, "stage_runs.jsonl")
CK = "selftest 78-2"
os.environ["STAGE_RUNS"] = RUNS
os.environ["STAGE_RUNS_CYCLE"] = CK
sys.path.insert(0, TOOLS)
import stage_prerun as SP  # noqa: E402
import protocol as P  # noqa: E402

G = []


def gate(label, ok, detail=""):
    G.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:300]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def counted(stage):
    return [r for r in SP.read_stage_runs() if r.get("stage") == stage and r.get("cycle") == CK and r.get("by") == "bgrun"]


def nlines():
    try:
        return sum(1 for _ in open(RUNS, encoding="utf-8"))
    except OSError:
        return 0


real_md5 = md5(REAL_RUNS)
# C7 seed: the real hook-written lines, re-keyed to this cycle so they WOULD count under the old rule
seed = []
for ln in open(REAL_RUNS, encoding="utf-8"):
    d = json.loads(ln)
    d["cycle"] = CK
    seed.append(json.dumps(d))
open(RUNS, "w", encoding="utf-8").write("\n".join(seed) + "\n")
real_stage = "tools/recipes/stage_replay_standins.py"
ok, why, _c = SP.check_cap("py -u " + real_stage, os.path.join(ROOT, real_stage), SP.read_stage_runs(), CK)
old_rule = len([r for r in SP.read_stage_runs() if r.get("stage") == "stage_replay_standins.py"])
gate("C7 {0} seeded hook-written lines ({1} of that stage) no longer count: cap allows".format(len(seed), old_rule),
     ok and old_rule >= 2, why)

# dummy stage script: path must match tools/recipes/stage_*.py
dd = os.path.join(TMP, "tools", "recipes")
os.makedirs(dd)
dummy = os.path.join(dd, "stage_selftest_dummy.py")
open(dummy, "w").write("import sys\nsys.path.insert(0, %r)\nimport protocol as P\n"
                       "print(P.result_line(P.make_result(1, 0)))\n" % TOOLS)
key = SP.stage_key(dummy)
launch = 'py tools/bgrun.py --material --max-min 1 --log tools/bench/x.log -- py -u "{0}"'.format(dummy)
real_launch = "py tools/bgrun.py --material --max-min 40 --log tools/bench/stage_replay_78.log -- py -u " + real_stage


def hook(name, cmd):
    data = json.dumps({"tool_name": "Bash", "tool_input": {"command": cmd}, "session_id": "selftest-78-2"})
    r = subprocess.run([sys.executable, os.path.join(TOOLS, "hooks", name)], input=data, capture_output=True,
                       text=True, encoding="utf-8", errors="replace", cwd=ROOT, timeout=60)
    return r.returncode, [l for l in (r.stderr or r.stdout or "").splitlines() if "BLOCKED" in l][:1]


n0 = nlines()
rc, msg = hook("guard_bash.py", real_launch)
gate("C1 guard_bash hook on a stage launch records nothing (hook rc={0})".format(rc), nlines() == n0, msg)
rc, msg = hook("guard_cycle.py", real_launch)
gate("C2 guard_cycle hook on a stage launch records nothing (hook rc={0})".format(rc), nlines() == n0, msg)


def bgrun(extra=(), child=None, log="run.log"):
    argv = [sys.executable, os.path.join(TOOLS, "bgrun.py"), "--max-min", "1", "--log", os.path.join(TMP, log)]
    argv += list(extra) + ["--"] + (child or [sys.executable, "-u", dummy])
    r = subprocess.run(argv, capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT, timeout=120)
    return r.returncode, r.stdout or ""


rc, outp = bgrun(child=[os.path.join(TMP, "no_such_python.exe"), "-u", dummy], log="nostart.log")
gate("C3 child that never starts (rc={0}) records nothing".format(rc), nlines() == n0 and rc != 0,
     [l for l in outp.splitlines() if "BGRUN END" in l][:1])

rc, outp = bgrun()
c = counted(key)
gate("C4 started run +1 (rc={0}, counted {1}, by/cycle/card on the line)".format(rc, len(c)),
     rc == 0 and len(c) == 1 and c[0]["card"] is None and "BGRUN STAGE-RUN recorded" in outp,
     [l for l in outp.splitlines() if "STAGE-RUN" in l][:1])
rc, outp = bgrun()
c = counted(key)
ok3, why3, _ = SP.check_cap(launch, dummy, SP.read_stage_runs(), CK)
gate("C5 second run -> {0}; cap 2 REFUSES a third".format(len(c)), len(c) == 2 and not ok3, why3[:120])

card = json.load(open(os.path.join(TOOLS, "bench", "cards", "task_78-2.json"), encoding="utf-8"))
card.update(id="st-78-2", retry_of=key)
cardp = os.path.join(TMP, "task_st.json")
json.dump(card, open(cardp, "w", encoding="utf-8"))
okc, whyc, cid = SP.check_cap(launch.replace("--material", "--material --retry-card " + cardp), dummy,
                              SP.read_stage_runs(), CK)
rc, outp = bgrun(extra=["--retry-card", cardp])
c = counted(key)
ok4, why4, _ = SP.check_cap(launch + " --retry-card " + cardp, dummy, SP.read_stage_runs(), CK)
gate("C6 RETRY card allows ONE (check {0}/{1}; run 3 recorded card {2!r}; reuse refused)".format(okc, cid, c[-1]["card"]),
     okc and cid == "st-78-2" and len(c) == 3 and c[-1]["card"] == "st-78-2" and not ok4, (whyc or why4)[:160])

gate("C8 real tools/bench/stage_runs.jsonl byte-unchanged", md5(REAL_RUNS) == real_md5, real_md5)
shutil.rmtree(TMP, ignore_errors=True)
npass = sum(1 for _l, o in G if o)
first = next((l for l, o in G if not o), None)
print("=== GATES: {0} pass / {1} fail".format(npass, len(G) - npass), flush=True)
print(P.result_line(P.make_result(npass, len(G) - npass, first)), flush=True)
sys.exit(0 if first is None else 1)
