"""Self-test of cycle_runner's runner-side HEARTBEAT + report_gate (card chat-H1, 2026-09-25). Dry: no claude session,
no LabVIEW, no real toast (HEARTBEAT_TOAST_STUB records the calls).
EXISTING, checked first: selftest_cycle_runner_ff.py (the stand-in-session pattern reused here); report_gate.py had no
bench override, so REPORT_GATE_BENCH was added for this test only.
PREDICTION: a 2-cycle dry run emits EXACTLY 3 HEARTBEAT lines (2 `cycle-end` + 1 `FINAL`), 3 stubbed toasts, a Korean
heartbeat_latest.md with a table; the FINAL line names the last result card `hb-2 PASS` and next act; report_gate as a
Stop hook exits 2 naming a HEARTBEAT line, exits 0 under CYCLE_SESSION=1, exits 0 after --ack;
selftest_cycle_runner_ff stays 3/3.
Usage: MATERIAL=1 py tools/bgrun.py --max-min 10 --log tools/bench/selftest_heartbeat.log -- py -u tools/bench/selftest_heartbeat.py"""
import json
import os
import subprocess
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
RUNNER = os.path.join(ROOT, "tools", "cycle_runner.py")
GATE = os.path.join(ROOT, "tools", "hooks", "report_gate.py")

if len(sys.argv) > 1 and sys.argv[1] == "session":          # the stand-in judgement session
    bench = os.environ["HB_BENCH"]
    cnt = os.path.join(bench, "count.txt")
    c = int(open(cnt).read()) + 1 if os.path.exists(cnt) else 1
    open(cnt, "w").write(str(c))
    os.makedirs(os.path.join(bench, "cards"), exist_ok=True)
    with open(os.path.join(bench, "cards", "result_hb-%d.json" % c), "w", encoding="utf-8") as f:
        json.dump({"schema": "result/1", "id": "hb-%d" % c, "status": "PASS", "artefacts": [{"path": "x", "md5": "y"}]}, f)
    with open(os.path.join(bench, "next.json"), "w", encoding="utf-8") as f:
        json.dump({"schema": "next/1", "cycle": c, "act": "heartbeat self-test act %d" % c, "task_kind": "build",
                   "stop_requested": False, "advances": ["M3"]}, f)
    time.sleep(1.1)
    sys.exit(0)

gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("%s %s %s" % ("PASS" if ok else "FAIL", label, detail), flush=True)


bench = tempfile.mkdtemp(prefix="hbbench_")
status = os.path.join(bench, "STATUS.md")
open(status, "w", encoding="utf-8").write("## NEXT\nx\n")
stub = os.path.join(bench, "toast_stub.txt")
env = dict(os.environ, HB_BENCH=bench, HEARTBEAT_TOAST_STUB=stub)
env.pop("CYCLE_SESSION", None)
r = subprocess.run([sys.executable, RUNNER, "--cycles", "2", "--bench-dir", bench, "--status", status,
                    "--dry-cmd", "py tools/bench/selftest_heartbeat.py session"],
                   capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, cwd=ROOT)
# what the chat's report_gate reads in reality: the bgrun log around the runner = its stdout
main_log = os.path.join(bench, "cycle_runner_main_selftest.log")
open(main_log, "w", encoding="utf-8").write(r.stdout + "BGRUN END rc=0 after 1s\n")
log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
hb = [ln for ln in log.splitlines() if ln.startswith("HEARTBEAT |")]
for ln in hb:
    print("  " + ln[:260])
gate("H1 exactly 3 heartbeats", len(hb) == 3, "(got %d)" % len(hb))
gate("H2 2 cycle-end + 1 FINAL", sum("| cycle-end |" in x for x in hb) == 2 and sum("| FINAL |" in x for x in hb) == 1)
gate("H3 FINAL last", bool(hb) and "| FINAL |" in hb[-1] and log.rfind("RUNNER STOP") < log.rfind("| FINAL |"))
gate("H4 FINAL content", bool(hb) and "last result hb-2 PASS" in hb[-1] and "heartbeat self-test act 2" in hb[-1]
     and "cycles 2" in hb[-1] and "hb-1(1 artefacts)" in hb[-1] and "open decisions" in hb[-1])
gate("H5 hooks field", bool(hb) and all("hooks errorlist=" in x and "motor=" in x and "close=" in x for x in hb))
toasts = open(stub, encoding="utf-8").read().splitlines() if os.path.exists(stub) else []
gate("H6 3 stubbed toasts", len(toasts) == 3, "(got %d)" % len(toasts))
md = open(os.path.join(bench, "heartbeat_latest.md"), encoding="utf-8").read() \
    if os.path.exists(os.path.join(bench, "heartbeat_latest.md")) else ""
gate("H7 heartbeat_latest.md Korean + table", "러너 종료 최종 보고" in md and "| 항목 | 값 |" in md)
gate("H8 no heartbeat error", "HEARTBEAT-ERROR" not in log)

genv = dict(os.environ, REPORT_GATE_BENCH=bench)
for k in ("CYCLE_SESSION", "BENCH_CELL"):
    genv.pop(k, None)
stop = json.dumps({"hook_event_name": "Stop"})
g1 = subprocess.run([sys.executable, GATE], input=stop, capture_output=True, text=True, encoding="utf-8",
                    errors="replace", env=genv)
gate("G1 Stop blocked on HEARTBEAT", g1.returncode == 2 and "HEARTBEAT |" in g1.stderr, "(exit %d)" % g1.returncode)
g2 = subprocess.run([sys.executable, GATE], input=stop, capture_output=True, text=True, env=dict(genv, CYCLE_SESSION="1"))
gate("G2 runner cell exempt", g2.returncode == 0, "(exit %d)" % g2.returncode)
subprocess.run([sys.executable, GATE, "--ack"], capture_output=True, text=True, env=genv)
g3 = subprocess.run([sys.executable, GATE], input=stop, capture_output=True, text=True, env=genv)
gate("G3 released after --ack", g3.returncode == 0, "(exit %d)" % g3.returncode)

ff = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "bench", "selftest_cycle_runner_ff.py")],
                    capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
gate("F1 selftest_cycle_runner_ff 3/3", "3/3 PASS" in ff.stdout,
     "(%s)" % ([ln for ln in ff.stdout.splitlines() if "/3 PASS" in ln] or ["?"])[0])

n_fail = sum(not ok for _, ok in gates)
print("%d/%d PASS" % (len(gates) - n_fail, len(gates)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol  # noqa: E402
first = next((lbl for lbl, ok in gates if not ok), None)
print(protocol.result_line(protocol.make_result(len(gates) - n_fail, n_fail, first)))
sys.exit(0 if n_fail == 0 else 1)
