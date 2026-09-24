"""selftest_motor_fail_exit.py - a rejected / missed motor action must be VISIBLE to bgrun and audit_cycle.
Cycle 69 device-failed repair (retrospective-cycle68), RE-CUT 2026-09-24 for session protocol v1 C6: bgrun's body scan
(`RESULT: REJECTED`, `NOT at target`, `ERR?=N`, `FAIL:`) is REMOVED, so a motor failure is now caught by motor_gate.py's
own `RESULT {...}` line (one per call) and bgrun's any-RESULT-fails rule. NO HARDWARE: no port is opened - every
motor_gate call below is either refused by decide() before session_info()/transmit()/_run_ps, or an allowed DRY-RUN.

PRIOR ART CHECKED: the cycle-69 version of this file (A1 replayed the historic log's text through a nested bgrun and
relied on the scan), tools/bench/selftest_motor_gate2.py (in-process main() with refused commands), tools/protocol.py.

PREDICTION CONTRACT (all must hold; printed as PASS/FAIL rows, summary `N/N PASS, 0 FAIL`):
  A1 a CHAIN of real motor_gate CLI calls - refused `MOV` in 실험중 (exit 3), then an allowed dry-run (exit 0) - run by a
     wrapper that exits 0, through a nested bgrun -> END rc=1 with `(RESULT:` on the END line (the later PASS does not
     hide the refused move: any failing RESULT line fails the run)
  A2 the historic pi_testmove_20260923e.log (started before protocol.SWITCH_TS, no RESULT line) is still judged FAILED
     by protocol.log_verdict with audit_cycle's legacy FAILURE_RE - history is not rewritten
  A3 the same historic text replayed as a NEW run through a nested bgrun -> rc 0 (the scan is gone; stated, so nobody
     mistakes it for coverage: a modern motor chain is covered by A1, an old log by A2)
  B1-B3 motor_session_start_cycle68 / _start_cycle67 / _end_cycle67 logs -> nested bgrun rc=0 AND legacy verdict PASS
  C1 motor_gate CLI, rig-state 실험중, `MOV 1 5 --execute` -> exit 3, a `^FAIL:` line, and a LAST line `RESULT` FAIL
  C2 motor_gate CLI, assembled, `GOH` -> exit 3, RESULT FAIL;  C3 dry-run allowed `MOV 1 5` -> exit 0, RESULT PASS
  D  in-process mg.main() refusal prints neither a FAIL line nor a RESULT line (selftest_motor_gate2 stays green)
  E  both senders still carry their `FAIL:` Write-Output lines (static check; harmless, no longer load-bearing)
  F  every CLI call journals into TMP via `--journal`; tools/bench/motor_gate.log byte size unchanged by the run and the
     scratch journal holds exactly 6 rows (C1, C2, C3, A1 x2 via --journal; D via mg.LOG_PATH = the same TMP file)
Output never echoes a child's RESULT line; the only `RESULT {` line printed is this self-test's own verdict, last."""
import contextlib
import io
import os
import re
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import audit_cycle  # noqa: E402
import motor_gate as mg  # noqa: E402
import protocol  # noqa: E402

BGRUN = os.environ.get("BGRUN_UNDER_TEST") or os.path.join(ROOT, "tools", "bgrun.py")   # override: test a candidate copy
GATE = os.path.join(ROOT, "tools", "motor_gate.py")
TMP = tempfile.mkdtemp(prefix="selftest_motor_fail_exit_")
JOURNAL = os.path.join(TMP, "motor_gate.log")
rows = []


def row(ok, label, got, want):
    rows.append((bool(ok), label, got, want))


def raw(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return f.read()


def body(name):
    return "".join(l for l in raw(name).splitlines(True) if not l.startswith("BGRUN "))


def nested_bgrun(argv, tag):
    log = os.path.join(TMP, tag + ".log")
    subprocess.run([sys.executable, BGRUN, "--max-min", "1", "--log", log, "--"] + argv,
                   capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    txt = open(log, encoding="utf-8", errors="replace").read()
    ends = re.findall(r"(?m)^BGRUN END rc=(\d+)(.*)$", txt)
    return (int(ends[-1][0]), ends[-1][1]) if ends else (-1, "")


def replay_text(text, tag):
    src = os.path.join(TMP, tag + ".txt")
    with open(src, "w", encoding="utf-8") as f:
        f.write(text)
    return nested_bgrun([sys.executable, "-c", "import sys;sys.stdout.reconfigure(encoding='utf-8');"
                         "print(open(r'%s',encoding='utf-8').read())" % src], tag)[0]


def gate_cli(argv):
    argv = argv + ["--journal", JOURNAL]
    p = subprocess.run([sys.executable, GATE] + argv, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=ROOT)
    lines = [l for l in p.stdout.splitlines() if l.strip()]
    last = protocol.parse_result_line(lines[-1]) if lines else None
    return p.returncode, bool(re.search(r"(?m)^FAIL:", p.stdout)), last


def main():
    prod = mg.LOG_PATH
    prod_size = os.path.getsize(prod) if os.path.exists(prod) else -1
    st_exp = os.path.join(TMP, "status_exp.md")
    st_asm = os.path.join(TMP, "status_asm.md")
    open(st_exp, "w", encoding="utf-8").write("rig-state: 실험중\n")
    open(st_asm, "w", encoding="utf-8").write("rig-state: 조립\n")

    chain = os.path.join(TMP, "chain.py")
    with open(chain, "w", encoding="utf-8") as f:
        f.write("import subprocess,sys\n"
                "for a in (%r, %r):\n"
                "    p = subprocess.run([sys.executable, %r] + a, capture_output=True, text=True, encoding='utf-8')\n"
                "    sys.stdout.write(p.stdout)\n"
                "sys.exit(0)\n" % (
                    ["--status", st_exp, "--device", "pi", "--command", "MOV 1 5", "--execute", "--journal", JOURNAL],
                    ["--status", st_asm, "--device", "pi", "--command", "MOV 1 5", "--journal", JOURNAL], GATE))
    c, tail = nested_bgrun([sys.executable, "-u", chain], "chain")
    row(c == 1 and "(RESULT:" in tail, "A1 refused-then-allowed chain via bgrun", "code %d result-tail %s" % (
        c, "(RESULT:" in tail), "code 1 result-tail True")

    v = protocol.log_verdict(raw("pi_testmove_20260923e.log"), legacy_re=audit_cycle.FAILURE_RE,
                             mtime=os.path.getmtime(os.path.join(HERE, "pi_testmove_20260923e.log")))
    row(v["failed"] and v["source"] == "legacy", "A2 historic pi_testmove, legacy verdict",
        "failed %s src %s" % (v["failed"], v["source"]), "failed True src legacy")
    c = replay_text(body("pi_testmove_20260923e.log"), "pi_testmove")
    row(c == 0, "A3 historic text as a NEW run (no scan)", "code %d" % c, "code 0")
    for i, name in enumerate(["motor_session_start_cycle68.log", "motor_session_start_cycle67.log",
                              "motor_session_end_cycle67.log"], 1):
        c = replay_text(body(name), "green%d" % i)
        v = protocol.log_verdict(raw(name), legacy_re=audit_cycle.FAILURE_RE,
                                 mtime=os.path.getmtime(os.path.join(HERE, name)))
        row(c == 0 and not v["failed"], "B%d %s" % (i, name), "code %d failed %s" % (c, v["failed"]),
            "code 0 failed False")

    code, has, last = gate_cli(["--status", st_exp, "--device", "pi", "--command", "MOV 1 5", "--execute"])
    ok = code == 3 and has and last is not None and protocol.result_failed(last)
    row(ok, "C1 experiment-state execute refused", "code %d fail %s result %s" % (
        code, has, last and last.get("status")), "code 3 fail True result FAIL")
    code, has, last = gate_cli(["--status", st_asm, "--device", "pi", "--command", "GOH"])
    row(code == 3 and last is not None and protocol.result_failed(last), "C2 GOH refused (command class)",
        "code %d result %s" % (code, last and last.get("status")), "code 3 result FAIL")
    code, has, last = gate_cli(["--status", st_asm, "--device", "pi", "--command", "MOV 1 5"])
    row(code == 0 and not has and last is not None and not protocol.result_failed(last), "C3 allowed dry-run",
        "code %d fail %s result %s" % (code, has, last and last.get("status")), "code 0 fail False result PASS")

    buf_o, buf_e = io.StringIO(), io.StringIO()
    real_log = mg.LOG_PATH
    mg.LOG_PATH = JOURNAL
    try:
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            code = mg.main(["--status", st_asm, "--device", "pi", "--command", "GOH"])
    finally:
        mg.LOG_PATH = real_log
    both = buf_o.getvalue() + buf_e.getvalue()
    leak = bool(re.search(r"(?m)^FAIL:|^RESULT \{", both))
    row(code == 3 and not leak, "D in-process main() prints no FAIL/RESULT", "code %d leak %s" % (code, leak),
        "code 3 leak False")

    pi = open(os.path.join(ROOT, "tools", "motor_send_pi.ps1"), encoding="utf-8", errors="replace").read()
    asi = open(os.path.join(ROOT, "tools", "motor_asi_io.ps1"), encoding="utf-8", errors="replace").read()
    n = pi.count('Write-Output "FAIL: PI MOV') + asi.count('Write-Output "FAIL: ASI move')
    row(n == 3, "E sender FAIL lines present", "count %d" % n, "count 3")
    ns = sum(1 for _ in open(JOURNAL, encoding="utf-8")) if os.path.exists(JOURNAL) else 0
    now = os.path.getsize(prod) if os.path.exists(prod) else -1
    row(now == prod_size and ns == 6, "F production journal untouched", "bytes %d->%d scratch rows %d" % (
        prod_size, now, ns), "unchanged, scratch rows 6")

    for ok, label, got, want in rows:
        print("%-4s %-44s got %-30s want %s" % ("PASS" if ok else "FAIL", label, got, want), flush=True)
    nbad = sum(1 for r in rows if not r[0])
    print("\n%d/%d PASS, %d FAIL" % (len(rows) - nbad, len(rows), nbad), flush=True)
    print("NO PORT WAS OPENED AND NO MOTION COMMAND WAS SENT BY THIS RUN.", flush=True)
    first = next((r[1] for r in rows if not r[0]), None)
    print(protocol.result_line(protocol.make_result(len(rows) - nbad, nbad, first)), flush=True)
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
