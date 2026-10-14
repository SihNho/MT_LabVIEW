# ---
# labview: none
# hardware: none
# ---
"""Mock queue test (evaluation discussion 2026-10-14, user "동의"): runs the REAL lean_queue.ps1 and lean_review.py on a
temp lean_bench folder, with only the hooks, the execute session and the discussions/plan replaced by stubs (no model,
no LabVIEW, no motor, no Google). A `tail -F` holds queue.log the whole time (the run-1 log-write failure).

  run A (run_limit 4; t1..t5): t1 PASS; t2 discussion error then no verdict -> HOLD; t3 review crashes -> HOLD recorded;
        t4 FAIL with a HOLD: and an ASSUME: question, plan writes a retry -> 4 cycles -> STOP + evaluation; t5 not run.
  run B: start hook fails -> STOP, task put back, end hook still called, no review.
  run C: the review process dies unrecorded -> the queue writes STOP.
Usage: py tools/bench/lean_bench/mock/mock_run.py     (about a minute)
"""
import glob
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
LB = os.path.dirname(HERE)
QUEUE = os.path.join(LB, "lean_queue.ps1")
TAIL = r"C:\Program Files\Git\usr\bin\tail.exe"
ASSEMBLED = "\uc870\ub9bd"   # the rig-state word for assembled


def setup(name, tasks, limit=None, fail_hooks=()):
    root = os.path.join(HERE, "runs", "%s_%s" % (time.strftime("%Y%m%d_%H%M%S"), name))
    os.makedirs(os.path.join(root, "queue"))
    for i, t in enumerate(tasks):
        p = os.path.join(root, "queue", "%s.md" % t)
        open(p, "w", encoding="utf-8").write("# mock task %s\n" % t)
        os.utime(p, (time.time() - 100 + i, time.time() - 100 + i))   # run order = list order
    if limit:
        open(os.path.join(root, "run_limit.txt"), "w").write("%d\n" % limit)
    for h in fail_hooks:
        open(os.path.join(root, h), "w").close()
    st = os.path.join(root, "STATUS_fake.md")
    open(st, "w", encoding="utf-8").write("rig-state: %s   <!-- mock -->\n" % ASSEMBLED)
    open(os.path.join(root, "queue.log"), "w").close()
    return root, st


def run(root, st, timeout=240):
    holder = subprocess.Popen([TAIL, "-n", "0", "-F", os.path.join(root, "queue.log")], stdout=subprocess.DEVNULL,
                              stderr=subprocess.DEVNULL)
    try:
        t0 = time.time()
        p = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", QUEUE, "-Root", root,
                            "-Stub", HERE, "-Status", st, "-MaxTasks", "10"], capture_output=True, text=True,
                           encoding="utf-8", errors="replace", timeout=timeout)
        return p.returncode, time.time() - t0, (p.stdout or "") + (p.stderr or "")
    finally:
        holder.kill()


def text(p):
    try:
        return open(p, encoding="utf-8-sig", errors="replace").read()
    except OSError:
        return ""


def main():
    ok, n, rows = 0, 0, []

    def check(name, cond):
        nonlocal ok, n
        n += 1
        ok += bool(cond)
        rows.append("%s  %s" % ("PASS" if cond else "FAIL", name))
        print(rows[-1], flush=True)

    # ---- run A
    root, st = setup("A", ["t1", "t2", "t3", "t4", "t5"], limit=4)
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    reviews = [ln for ln in ql.splitlines() if ln.startswith("REVIEW | ")]
    qs = text(os.path.join(root, "questions_for_user.md"))
    check("A queue ended by itself (rc 0, %.0f s)" % secs, rc == 0)
    check("A queue's own lines written while tail -F held the log (CYCLE 1..4 START)",
          all("CYCLE %d/10 START t%d" % (i, i) in ql for i in range(1, 5)))
    check("A 4 cycles recorded by REVIEW lines", len(reviews) == 4)
    check("A t1 PASS", any("| t1 |" in r and "cycle PASS" in r for r in reviews))
    check("A t2 error then no verdict -> retry + HOLD, report kept as _hold1",
          "REVIEW-RETRY" in ql and any("| t2 |" in r and "cycle HOLD" in r for r in reviews)
          and os.path.exists(os.path.join(root, "lean_report_t2_hold1.md")))
    check("A t3 review crash -> HOLD recorded, queue went on",
          any("| t3 |" in r and "review crashed" in r for r in reviews) and "review step crashed" in qs)
    check("A t4 FAIL -> report _fail1, retry queue/next/t4.md written",
          any("| t4 |" in r and "cycle FAIL" in r for r in reviews)
          and os.path.exists(os.path.join(root, "lean_report_t4_fail1.md"))
          and os.path.exists(os.path.join(root, "queue", "next", "t4.md")))
    check("A HOLD: and ASSUME: questions recorded", "HOLD: need an exception" in qs and "ASSUME: 90 Hz leg first" in qs)
    check("A run limit -> STOP + one evaluation record",
          "run limit 4" in text(os.path.join(root, "STOP")) and len(glob.glob(os.path.join(root, "lean_eval_*.md"))) == 1)
    check("A t5 not started (still queued)", os.path.exists(os.path.join(root, "queue", "t5.md")) and "START t5" not in ql)
    check("A review records carry the cycle id (no overwrite)", len(glob.glob(os.path.join(root, "lean_review_*-c*.md"))) == 3)

    # ---- run B
    root, st = setup("B", ["b1", "b2"], fail_hooks=["fail_hook_start_b1"])
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    check("B start hook fails -> STOP, task put back, end hook called, no review",
          "motor session start FAILED before b1" in text(os.path.join(root, "STOP"))
          and os.path.exists(os.path.join(root, "queue", "b1.md")) and "| b1 | end | STUB ok" in ql
          and "REVIEW | " not in ql and "START b2" not in ql)

    # ---- run C
    root, st = setup("C", ["c1", "c2"])
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    check("C review dies unrecorded -> STOP by the queue, c2 not started",
          "died without recording" in text(os.path.join(root, "STOP")) and "START c2" not in ql)

    # ---- run D
    root, st = setup("D", ["t1"])
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    check("D queue empty after a PASS cycle -> RUN END, no STOP file",
          rc == 0 and "RUN END: queue empty after 1 cycles" in ql and not os.path.exists(os.path.join(root, "STOP")))

    # ---- run E (evaluation 2026-10-14 changes 2-4)
    root, st = setup("E", ["e1", "e2", "e3", "e4", "e5"])
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    reviews = [ln for ln in ql.splitlines() if ln.startswith("REVIEW | ")]
    order = [r.split(" | ")[3] for r in reviews]
    check("E e1 session INCOMPLETE + PASS-BY-REVIEW with source -> PASS, closed by the review",
          any("| e1 |" in r and "cycle PASS" in r for r in reviews) and "REVIEW-CLOSE" in ql)
    check("E e2 review PASS, session INCOMPLETE, no source -> HOLD (no retry)",
          any("| e2 |" in r and "cycle HOLD" in r for r in reviews) and "START e2" in ql and ql.count("START e2") == 1)
    check("E e3's plan revises queued e5 -> it keeps its place (e4 before e5)", order == ["e1", "e2", "e3", "e4", "e5"]
          and "keeps the original's place" in ql)
    check("E NEXT lines matched the queue (no mismatch)", "PLAN-ORDER-MISMATCH" not in ql)
    check("E run ended on the empty queue after 5 cycles", "RUN END: queue empty after 5 cycles" in ql)

    # ---- run F (change 1: the end hook's position check fails -> STOP, no review)
    root, st = setup("F", ["f1", "f2"], fail_hooks=["fail_hook_end_f1"])
    rc, secs, out = run(root, st)
    ql = text(os.path.join(root, "queue.log"))
    check("F end hook fails (position change) -> STOP, no review, f2 not started",
          "cycle end hook FAILED after f1" in text(os.path.join(root, "STOP")) and "REVIEW | " not in ql
          and "START f2" not in ql)

    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok == n else "FAIL",
                                  "gates": {"pass": ok, "fail": n - ok}, "first_fail": None, "artefacts": []}))
    return 0 if ok == n else 1


if __name__ == "__main__":
    sys.exit(main())
