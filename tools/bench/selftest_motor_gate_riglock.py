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
