r"""run_selftests_chat_b2.py - card chat-B2: every self-test the protocol wiring can affect, in ONE bgrun, plus one
cycle_runner --dry-run cycle. No LabVIEW (selftest_stagekit is the pure-function half of stagekit: its own docstring
says "Nothing here opens COM"), no network (TYPESAFE_API_KEY removed), no motor (--no-motor-hooks).

WHAT EXISTED: each self-test below, unchanged in purpose; this file only runs them and tallies.

PREDICTION CONTRACT: every self-test exits 0; the dry-run runner writes cards/cycle_1.json that validates as cycle/1
and logs `NEXT | ... next.json read, CHANGED` for a stand-in that writes a valid next.json.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P  # noqa: E402

TESTS = ["selftest_protocol_wiring", "selftest_protocol", "selftest_cycle_runner", "selftest_cycle_runner_ff",
         "selftest_next_gate_jev", "selftest_guard_peer_budget", "selftest_guard_peer_failre", "selftest_guard_peer_jev",
         "selftest_guard_peer_ladder", "selftest_guard_peer_samerow", "selftest_jev_ladder_action",
         "selftest_bgrun_fail_scan", "selftest_bgrun_final_line", "selftest_bgrun_jev_exempt",
         "selftest_motor_fail_exit", "selftest_stagekit"]
ENV = {k: v for k, v in os.environ.items() if k != "TYPESAFE_API_KEY"}
PASS, FAIL = [], []


def gate(label, ok, detail=""):
    (PASS if ok else FAIL).append(label)
    print("  %s  %-44s %s" % ("PASS" if ok else "FAIL", label, str(detail)[:140]), flush=True)


HEAD0 = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()


def main():
    for t in TESTS:
        r = subprocess.run([sys.executable, "-u", os.path.join(HERE, t + ".py")], cwd=ROOT, env=ENV,
                           capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=900)
        out = (r.stdout or "") + (r.stderr or "")
        with open(os.path.join(HERE, "selftest_chatb2_%s.log" % t), "w", encoding="utf-8") as f:
            f.write(out)
        tail = [ln for ln in out.strip().splitlines() if ln.strip()][-1:] or [""]
        gate(t, r.returncode == 0, "exit %d | %s" % (r.returncode, tail[0]))

    # the runner, one dry cycle, isolated bench + STATUS; the stand-in writes a valid next.json
    tmp = tempfile.mkdtemp(prefix="b2run_")
    try:
        bench = os.path.join(tmp, "bench")
        os.makedirs(bench)
        st = os.path.join(tmp, "STATUS.md")
        open(st, "w", encoding="utf-8").write("# S\nrig-state: 조립\n\n## NEXT\nx\n")
        stand = os.path.join(tmp, "stand.py")
        open(stand, "w", encoding="utf-8").write(
            "import json,sys\njson.dump({'schema':'next/1','cycle':1,'act':'dry act','task_kind':'build',"
            "'stop_requested':False,'advances':['M3']},open(sys.argv[1],'w'))\n")
        if " " in tmp:
            gate("runner dry-run", False, "temp path has a space")
        else:
            r = subprocess.run([sys.executable, os.path.join(ROOT, "tools", "cycle_runner.py"), "--dry-run",
                                "--cycles", "1", "--no-motor-hooks", "--bench-dir", bench, "--status", st,
                                "--max-min", "2", "--dry-cmd", "%s %s %s" % (sys.executable, stand,
                                                                          os.path.join(bench, "next.json"))],
                               cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8", errors="replace",
                               timeout=300)
            log = open(os.path.join(bench, "cycle_runner.log"), encoding="utf-8").read()
            try:
                c = P.load_card(os.path.join(bench, "cards", "cycle_1.json"), None)
                cok = c["cycle"] == 1 and c["rig_state"] == "조립" and c["errorlist"] is None
            except (OSError, ValueError) as e:
                c, cok = str(e), False
            gate("runner --dry-run writes a valid cycle/1 card", cok and "CYCLE-CARD |" in log,
                 json.dumps(c, ensure_ascii=True)[:140] if isinstance(c, dict) else c)
            gate("runner reads next.json after the cycle", "next.json read, CHANGED" in log and r.returncode == 0,
                 [ln for ln in log.splitlines() if ln.startswith("NEXT |")][:1])
            print(log, flush=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, capture_output=True, text=True).stdout.strip()
    gate("no git commit was made by any dry-run runner in this bundle", head == HEAD0, "%s -> %s" % (HEAD0[:8], head[:8]))
    print("\n=== GATES: %d pass / %d fail%s" % (len(PASS), len(FAIL),
                                                ("; failing: " + ", ".join(FAIL)) if FAIL else ""), flush=True)
    print(P.result_line(P.make_result(len(PASS), len(FAIL), FAIL[0] if FAIL else None)), flush=True)
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
