# ---
# labview: none
# hardware: motor
# ---
# hardware = motor_gate.py is CALLED (one CLI subprocess that must be refused before any sender); no port is opened,
# no motion is sent - the lock is a temporary directory and the refusal comes before session_start.
"""Self-test of motor_gate.rig_lock_ok (shared rig lock, user 2026-10-21, debate riglock-v6 items 6 and 9) against a
TEMPORARY lock directory - never the real G:\\Codes\\rig\\rig_lock.json, no port, no motion. Also the CLI: --session and
--execute without a token are refused (rc 3) before any sender is reached.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/selftest_motor_gate_riglock.log -- py -u tools/bench/selftest_motor_gate_riglock.py
"""
import json
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
TMP = tempfile.mkdtemp(prefix="riglock_gate_")
os.environ["RIGLOCK_DIR"] = TMP            # set BEFORE riglock is imported (it reads the dir at import)
sys.path.insert(0, TOOLS)
import motor_gate as mg                                      # noqa: E402
sys.path.insert(0, mg.RIG_DIR)
import riglock as rl                                         # noqa: E402

ok = n = 0


def check(name, cond, detail=""):
    global ok, n
    n += 1
    ok += bool(cond)
    print("%s  %s %s" % ("PASS" if cond else "FAIL", name, detail))


def with_token(tok, kind):
    old = os.environ.get("RIGLOCK_TOKEN")
    if tok is None:
        os.environ.pop("RIGLOCK_TOKEN", None)
    else:
        os.environ["RIGLOCK_TOKEN"] = tok
    try:
        return mg.rig_lock_ok(kind)
    finally:
        if old is None:
            os.environ.pop("RIGLOCK_TOKEN", None)
        else:
            os.environ["RIGLOCK_TOKEN"] = old


STATUS_TMP = os.path.join(TMP, "STATUS_b2.md")
mg.STATUS_PATH = STATUS_TMP          # B2 (2026-10-21): rig_lock_ok compares STATUS.md with rig_lock.json - a temp copy
_set_state = rl.set_state


def both_states(state, by, note="", **k):
    """The chat records the user's word in BOTH places; this test follows it so B2 sees them agree."""
    r = _set_state(state, by, note, **k)
    with open(STATUS_TMP, "w", encoding="utf-8") as fh:
        fh.write("rig-state: %s\n" % state)
    return r


rl.set_state = both_states
check("lock dir is the temp dir", rl.DEFAULT_DIR == TMP, rl.DEFAULT_DIR)
check("no lock file -> start refused", not with_token("0" * 16, "start")[0])
rl.set_state("assembled", "selftest", "temp", init=True)
check("no token -> start refused", not with_token(None, "start")[0])
check("no token -> end refused", not with_token(None, "end")[0])
tok = rl.acquire("selftest", "gate test", pid=os.getpid())
check("holder, assembled -> start ok", with_token(tok, "start")[0])
check("holder, assembled -> execute ok", with_token(tok, "execute")[0])
check("holder, assembled -> reference ok", with_token(tok, "reference")[0])
check("wrong token -> execute refused", not with_token("f" * 16, "execute")[0])
rl.set_state("disassembled", "selftest", "temp")
check("holder, disassembled -> start ok", with_token(tok, "start")[0])
os.environ["RIGLOCK_TOKEN"] = tok
check("holder, disassembled, caller allows assembled only (lean hooks) -> refused",
      not mg.rig_lock_ok("start", ("assembled",))[0])
os.environ.pop("RIGLOCK_TOKEN", None)
rl.set_state("experiment", "selftest", "temp")
check("holder, experiment -> start refused", not with_token(tok, "start")[0])
check("holder, experiment -> execute refused", not with_token(tok, "execute")[0])
check("holder, experiment -> end (cleanup) ok", with_token(tok, "end")[0])
check("other token, experiment -> end refused", not with_token("f" * 16, "end")[0])
rl.set_state("assembled", "selftest", "temp")
with open(STATUS_TMP, "w", encoding="utf-8") as fh:
    fh.write("rig-state: 실험중\n")
check("B2 STATUS.md experiment vs lock assembled -> start refused, reason names the disagreement",
      not with_token(tok, "start")[0] and "DISAGREES" in with_token(tok, "start")[1])
check("B2 disagreement -> execute refused", not with_token(tok, "execute")[0])
check("B2 disagreement -> end (cleanup) still ok", with_token(tok, "end")[0])

# main(): an experiment declared mid-job (STATUS.md 실험중 AND rig_lock.json experiment) -> `--session end` still runs for
# the holder (item 9 + Q2: magnet home, limits released); `--session start` is refused. In-process, both session
# functions replaced by recorders - no sender can be reached.
ran = []
real_ss, real_se = mg.session_start, mg.session_end
mg.session_start = lambda *a, **k: (ran.append("start"), 0)[1]
mg.session_end = lambda *a, **k: (ran.append("end"), 0)[1]
rl.set_state("experiment", "selftest", "temp")
jr = os.path.join(TMP, "journal_main.log")


def gate_main(argv, token):
    del ran[:]
    os.environ.pop("RIGLOCK_TOKEN", None)
    if token:
        os.environ["RIGLOCK_TOKEN"] = token
    try:
        return mg.main(argv + ["--status", STATUS_TMP, "--journal", jr])
    finally:
        os.environ.pop("RIGLOCK_TOKEN", None)


rc_e = gate_main(["--session", "end"], tok)
check("experiment, holder -> --session end runs (cleanup: magnet home + release)", rc_e == 0 and ran == ["end"],
      "rc=%d ran=%s" % (rc_e, ran))
rc_s = gate_main(["--session", "start"], tok)
check("experiment, holder -> --session start refused, nothing run", rc_s == 3 and ran == [], "rc=%d ran=%s" % (rc_s, ran))
rc_n = gate_main(["--session", "end"], None)
check("experiment, no token -> --session end refused, nothing run", rc_n == 3 and ran == [], "rc=%d ran=%s" % (rc_n, ran))
with open(STATUS_TMP, "w", encoding="utf-8") as fh:
    fh.write("no machine key here\n")
rc_u = gate_main(["--session", "end"], tok)
check("unknown STATUS rig-state, holder -> --session end refused (default-deny)", rc_u == 3 and ran == [],
      "rc=%d ran=%s" % (rc_u, ran))
mg.session_start, mg.session_end = real_ss, real_se
rl.set_state("assembled", "selftest", "temp")
rl.release(tok)
check("released -> end refused", not with_token(tok, "end")[0])

# CLI: --session start with no token is refused (rc 3) - the refusal comes before session_start opens any port
status = os.path.join(TMP, "STATUS.md")
with open(status, "w", encoding="utf-8") as f:
    f.write("rig-state: assembled\n")
env = dict(os.environ, RIGLOCK_DIR=TMP)
env.pop("RIGLOCK_TOKEN", None)
p = subprocess.run([sys.executable, os.path.join(TOOLS, "motor_gate.py"), "--session", "start", "--status", status,
                    "--journal", os.path.join(TMP, "journal.log")], env=env, capture_output=True, text=True,
                   encoding="utf-8", errors="replace", timeout=60)
check("CLI --session start without token -> rc 3, lock named", p.returncode == 3 and "rig lock" in p.stderr,
      "rc=%d %s" % (p.returncode, p.stderr.strip()[:120]))

print("NO MOTION COMMAND WAS SENT AND NO PORT WAS OPENED BY THIS RUN.")
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                              "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
sys.exit(0 if ok == n else 1)
