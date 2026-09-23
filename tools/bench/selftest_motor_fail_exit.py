"""selftest_motor_fail_exit.py - cycle 69 device-failed repair (retrospective-cycle68): a rejected / missed motor
action must be VISIBLE to bgrun and audit_cycle. NO HARDWARE: no port is opened - every motor_gate call below is
refused by decide() (motor_gate.py main(): `if not d.allowed: ... return 3`) before session_info()/transmit()/_run_ps.

PRIOR ART CHECKED: tools/bench/selftest_bgrun_fail_scan.py (replays a literal line through a nested bgrun - same
method used here), tools/bench/selftest_motor_gate2.py (in-process main() with refused commands - case D below proves
the new FAIL line does not leak into it).

PREDICTION CONTRACT (all must hold; printed as PASS/FAIL rows, summary `N/N PASS, 0 FAIL`):
  A1 pi_testmove_20260923e.log (BGRUN lines stripped) replayed through a nested bgrun -> nested END rc=1 (inner failure)
  A2 same log through audit_cycle.FAILURE_RE -> matches
  B1-B3 motor_session_start_cycle68 / _start_cycle67 / _end_cycle67 logs -> nested bgrun END rc=0 AND no FAILURE_RE match
  C1 motor_gate CLI, STATUS override rig-state 실험중, `MOV 1 5 --execute` -> exit 3 and a stdout line `^FAIL:`
  C2 motor_gate CLI, assembled, `GOH` -> exit 3 and `^FAIL:`;  C3 dry-run allowed `MOV 1 5` -> exit 0, no FAIL line
  D  in-process mg.main() refusal prints no FAIL line (selftest_motor_gate2 stays green under bgrun)
  E  both senders carry the new `FAIL:` Write-Output lines (static check)
  F  (cycle 70 F6a) C1-C3 journal into TMP via `--journal`; tools/bench/motor_gate.log byte size unchanged by the run
     and the scratch journal holds exactly 4 rows (C1, C2, C3 via --journal; D via mg.LOG_PATH = the same TMP file)
Output never echoes a matched line (it would itself trip bgrun's scan)."""
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

BGRUN = os.path.join(ROOT, "tools", "bgrun.py")
GATE = os.path.join(ROOT, "tools", "motor_gate.py")
TMP = tempfile.mkdtemp(prefix="selftest_motor_fail_exit_")
rows = []


def row(ok, label, got, want):
    rows.append((bool(ok), label, got, want))


def body(name):
    with open(os.path.join(HERE, name), encoding="utf-8", errors="replace") as f:
        return "".join(l for l in f if not l.startswith("BGRUN "))


def nested_bgrun_code(text, tag):
    src = os.path.join(TMP, tag + ".txt")
    with open(src, "w", encoding="utf-8") as f:
        f.write(text)
    log = os.path.join(TMP, tag + ".log")
    subprocess.run([sys.executable, BGRUN, "--max-min", "1", "--log", log, "--", sys.executable, "-c",
                    "import sys;sys.stdout.reconfigure(encoding='utf-8');print(open(r'%s',encoding='utf-8').read())"
                    % src], capture_output=True, text=True, encoding="utf-8", errors="replace", cwd=ROOT)
    ends = re.findall(r"(?m)^BGRUN END rc=(\d+)", open(log, encoding="utf-8", errors="replace").read())
    return int(ends[-1]) if ends else -1


def gate_cli(argv):
    # cycle 70 F6a: every CLI case journals into TMP, never into the production tools/bench/motor_gate.log
    argv = argv + ["--journal", os.path.join(TMP, "motor_gate.log")]
    p = subprocess.run([sys.executable, GATE] + argv, capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=ROOT)
    return p.returncode, bool(re.search(r"(?m)^FAIL:", p.stdout))


def main():
    prod = mg.LOG_PATH
    prod_size = os.path.getsize(prod) if os.path.exists(prod) else -1
    bad = body("pi_testmove_20260923e.log")
    c = nested_bgrun_code(bad, "pi_testmove")
    row(c == 1, "A1 pi_testmove replay via bgrun", "code %d" % c, "code 1")
    row(bool(audit_cycle.FAILURE_RE.search(bad)), "A2 pi_testmove via audit FAILURE_RE",
        "match" if audit_cycle.FAILURE_RE.search(bad) else "none", "match")
    for i, name in enumerate(["motor_session_start_cycle68.log", "motor_session_start_cycle67.log",
                              "motor_session_end_cycle67.log"], 1):
        t = body(name)
        c = nested_bgrun_code(t, "green%d" % i)
        m = audit_cycle.FAILURE_RE.search(t)
        row(c == 0 and not m, "B%d %s" % (i, name), "code %d audit %s" % (c, "match" if m else "none"),
            "code 0 audit none")

    st_exp = os.path.join(TMP, "status_exp.md")
    st_asm = os.path.join(TMP, "status_asm.md")
    open(st_exp, "w", encoding="utf-8").write("rig-state: 실험중\n")
    open(st_asm, "w", encoding="utf-8").write("rig-state: 조립\n")
    code, has = gate_cli(["--status", st_exp, "--device", "pi", "--command", "MOV 1 5", "--execute"])
    row(code == 3 and has, "C1 experiment-state execute refused", "code %d fail-line %s" % (code, has),
        "code 3 fail-line True")
    code, has = gate_cli(["--status", st_asm, "--device", "pi", "--command", "GOH"])
    row(code == 3 and has, "C2 GOH refused (command class)", "code %d fail-line %s" % (code, has),
        "code 3 fail-line True")
    code, has = gate_cli(["--status", st_asm, "--device", "pi", "--command", "MOV 1 5"])
    row(code == 0 and not has, "C3 allowed dry-run", "code %d fail-line %s" % (code, has), "code 0 fail-line False")

    buf_o, buf_e = io.StringIO(), io.StringIO()
    real_log = mg.LOG_PATH
    mg.LOG_PATH = os.path.join(TMP, "motor_gate.log")
    try:
        with contextlib.redirect_stdout(buf_o), contextlib.redirect_stderr(buf_e):
            code = mg.main(["--status", st_asm, "--device", "pi", "--command", "GOH"])
    finally:
        mg.LOG_PATH = real_log
    leak = bool(re.search(r"(?m)^FAIL:", buf_o.getvalue() + buf_e.getvalue()))
    row(code == 3 and not leak, "D in-process main() prints no FAIL", "code %d leak %s" % (code, leak),
        "code 3 leak False")

    pi = open(os.path.join(ROOT, "tools", "motor_send_pi.ps1"), encoding="utf-8", errors="replace").read()
    asi = open(os.path.join(ROOT, "tools", "motor_asi_io.ps1"), encoding="utf-8", errors="replace").read()
    n = pi.count('Write-Output "FAIL: PI MOV') + asi.count('Write-Output "FAIL: ASI move')
    row(n == 3, "E sender FAIL lines present", "count %d" % n, "count 3")
    scratch = os.path.join(TMP, "motor_gate.log")
    ns = sum(1 for _ in open(scratch, encoding="utf-8")) if os.path.exists(scratch) else 0
    now = os.path.getsize(prod) if os.path.exists(prod) else -1
    row(now == prod_size and ns == 4, "F production journal untouched", "bytes %d->%d scratch rows %d" % (
        prod_size, now, ns), "unchanged, scratch rows 4")

    for ok, label, got, want in rows:
        print("%-4s %-44s got %-26s want %s" % ("PASS" if ok else "FAIL", label, got, want), flush=True)
    nbad = sum(1 for r in rows if not r[0])
    print("\n%d/%d PASS, %d FAIL" % (len(rows) - nbad, len(rows), nbad), flush=True)
    print("NO PORT WAS OPENED AND NO MOTION COMMAND WAS SENT BY THIS RUN.", flush=True)
    return 1 if nbad else 0


if __name__ == "__main__":
    sys.exit(main())
