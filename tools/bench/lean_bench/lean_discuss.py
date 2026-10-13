# ---
# labview: none
# hardware: none
# ---
"""A failed lean task opens ONE read-only Claude-GPT discussion, and the discussion's agreed actions become the NEXT task
(user 2026-10-13: "한 러너에 10 사이클은 돌려. 사이클 중간에 에러나 실패 등의 요인이 생기면 토론 세션으로 넘어가서 다음
액션을 취하도록 하고"). The queue (lean_queue.ps1) calls this after a task did not PASS.

  exit 0 = CONTINUE: the discussion ended with agreed actions and no question for the user; a retry task with the SAME
           tag was written to queue/next/ (the queue runs it before anything else; the failed report and session log are
           kept as lean_report_<tag>_fail<k>.md / session_<tag>_fail<k>.log, so later tasks that read
           lean_report_<tag>.md see the retry's result).
  exit 1 = SKIP: no agreed action, a question only the user can answer, the discussion failed, or this tag already
           failed MAX_FAILS times (failure budget 2, docs/rules/runner.md). The tag is given up for this run of the queue,
           the reason (and the question, if any) is appended to questions_for_user.md for the user's 10-cycle check, and
           the queue goes on with the next task (user 2026-10-13: "실패한 사이클은 멈춰버리지 말고 토론해서 방향 잡도록").
           Nobody answers the user's question in the meantime: tasks that need the skipped result end NOT-STARTED.

The discussion speakers only read (debate_relay's read-only Claude, GPT told read-only); the retry runs as a normal lean
session with the lean hooks (motor hook, originals, LabVIEW limits), bounded like every task (185 min, $60).

Shared code CALLED, not copied: tools/debate_loop.py run_discussion (topic file, gdoc under bgrun, deadline, STOP, summary,
the DEBATE log line).

Usage:  py tools/bench/lean_bench/lean_discuss.py --tag p6fix --task tools/bench/lean_bench/queue/done/p6fix_<ts>.md --rc 0
Self-test (no model call, no Google, no queue change): py tools/bench/lean_bench/lean_discuss.py selftest
"""
import argparse
import json
import os
import shutil
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
TOOLS = os.path.dirname(BENCH)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import debate_loop  # noqa: E402

MAX_FAILS = 2
RULE = ("요약을 믿지 말고 원문을 읽을 것: 아래 경로의 파일과 줄을 직접 열어 확인하고, 주장마다 file:line 을 붙이세요. "
        "이 토론은 lean 작업 큐가 실패한 작업 뒤에 자동으로 연 것입니다. 읽기만 하고 아무것도 실행하거나 고치지 마세요 "
        "(LabVIEW, 모터, 파일 수정 모두 금지). 사용자가 채팅으로 끼어들 수 있습니다.")
FORMAT = ("결론 형식: 원인 / 다음 작업. STATE 의 agreed 에는 다음 lean 세션이 그대로 할 행동만 한 줄씩 적으세요 - 큐가 이 "
          "줄들로 재시도 작업 파일을 써서 **사람의 확인 없이 바로** 돌립니다(같은 작업 태그, 같은 받아들임 기준, lean 규칙과 "
          "모터 훅은 그대로). 그러니 안전하지 않거나 사용자의 결정이 필요한 행동은 agreed 에 넣지 말고 user_needed 에 질문 "
          "하나로 쓰세요(그러면 큐가 멈추고 사용자를 기다립니다). 원래 작업을 포기해야 한다고 보면 agreed 를 비우세요.")


def _rel(p):
    return debate_loop._rel(p)


def _tail(path, n, pattern=None):
    """The last n lines of a file (only those containing `pattern`, when given), as `path:lineno text`. Never raises."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            lines = f.read().splitlines()
    except OSError:
        return ["`%s` (읽을 수 없음)" % _rel(path)]
    hit = [(i + 1, t) for i, t in enumerate(lines) if pattern is None or pattern in t]
    return ["`%s:%d` %s" % (_rel(path), i, t[:240]) for i, t in hit[-n:]] or ["(해당 줄 없음)"]


def fail_index(tag, lb=HERE):
    """1 + the number of failed runs of `tag` already kept (lean_report_<tag>_fail<k>.md)."""
    k = 1
    while os.path.exists(os.path.join(lb, "lean_report_%s_fail%d.md" % (tag, k))) or \
            os.path.exists(os.path.join(lb, "session_%s_fail%d.log" % (tag, k))):
        k += 1
    return k


def keep_failed(tag, k, lb=HERE):
    """Rename this run's report and session log to their _fail<k> names. -> (report, log) paths after the rename."""
    out = []
    for base, ext in (("lean_report_%s" % tag, ".md"), ("session_%s" % tag, ".log")):
        src, dst = os.path.join(lb, base + ext), os.path.join(lb, "%s_fail%d%s" % (base, k, ext))
        if os.path.exists(src):
            os.replace(src, dst)
        out.append(dst)
    return tuple(out)


def topic(tag, task, report, log, rc, k):
    """The topic text; first line = the Google doc title. Facts and paths only."""
    parts = [
        "lean 작업 %s 실패 %d회차 - 원인과 다음 행동 (%s)" % (tag, k, time.strftime("%Y-%m-%d %H:%M")),
        "",
        "lean 작업 큐가 작업 `%s` 를 돌렸고, 결과가 PASS 가 아닙니다 (launch_lean.ps1 rc=%s, 이 태그의 %d번째 실패, "
        "한도 %d). 큐는 이 토론이 끝날 때까지 다음 작업을 시작하지 않습니다." % (tag, rc, k, MAX_FAILS),
        "",
        "## 물어보는 것",
        "1. 이 작업이 PASS 하지 못한 **원인** (작업 지시 / 도구 / 대상 VI / 시간·비용 초과 중 무엇인지, 근거 file:line).",
        "2. **다음 lean 세션이 할 행동** - 한 세션(<= 180분, <= $60) 크기, 원래 작업의 받아들임 기준은 그대로.",
        "3. 같은 실패가 다시 나지 않게 하려면 무엇을 다르게 해야 하는가.",
        "",
        "## 읽을 원문 (요약 금지, 직접 열 것)",
        "- 작업 지시: `%s`" % _rel(task),
        "- 실패한 실행의 보고서: `%s`" % _rel(report),
        "- 실패한 실행의 세션 로그: `%s`" % _rel(log),
        "- lean 규칙: `%s`" % _rel(os.path.join(ROOT, "CLAUDE.md")),
        "- 지난 lean 보고서(성공 사례, 같은 도구와 경로): `tools/bench/lean_bench/lean_report.md` (P6-2), "
        "`tools/bench/lean_bench/lean_report_p63.md` (P6-3)",
        "- 계획과 결정: 주 체크아웃 `../V6_ParallelLoop/docs/d1/ring-p6b.md` PD414, "
        "`../V6_ParallelLoop/docs/lean-operation-proposal.md`",
        "",
        "## 보고서의 RESULT 줄",
    ]
    parts += _tail(report, 3, "RESULT")
    parts += ["", "## 세션 로그의 마지막 줄들"]
    parts += _tail(log, 12)
    parts += ["", RULE, "", FORMAT, ""]
    return "\n".join(parts)


def retry_task(tag, k, task, report, log, res):
    """The retry task text (same tag) from the discussion's agreed actions."""
    s = res.get("summary") or {}
    lines = [
        "# Lean task %s - retry %d after a failed run; next actions from the Claude-GPT discussion" % (tag, k),
        "One session, <= 180 min, <= $60. Written by `lean_discuss.py` (user 2026-10-13: on a failure the discussion "
        "decides the next action and the runner goes on).",
        "",
        "Read `CLAUDE.md` (the lean rules), then:",
        "- the original task `%s` - its start condition, acceptance, prohibitions and report format STILL HOLD unless an "
        "action below changes how you get there (never what counts as PASS);" % _rel(task),
        "- the failed run's report `%s` and session log `%s`;" % (_rel(report), _rel(log)),
        "- the discussion: summary `%s`, doc %s." % (_rel(res.get("summary_path") or "-"), res.get("doc") or "-"),
        "",
        "## Actions agreed by both sides (do these)",
    ]
    lines += ["%d. %s" % (i, x) for i, x in enumerate(s.get("agreed") or [], 1)]
    if s.get("experiment"):
        lines += ["", "## Experiments the discussion proposed (use when they help)"]
        lines += ["- %s" % x for x in s["experiment"]]
    if s.get("open"):
        lines += ["", "## Points the two sides did not settle (facts to check, not orders)"]
        lines += ["- %s" % x for x in s["open"]]
    lines += [
        "",
        "Do NOT edit `tools/hooks/**`, `tools/motor_gate.py`, `tools/bench/motor_limits.json` or `CLAUDE.md`. Do not commit.",
        "",
        "## Report `tools/bench/lean_bench/lean_report_%s.md`" % tag,
        "The original task's report contents, plus a first section \"Retry %d: what the discussion changed and what "
        "happened\", ending with the original task's RESULT line (key \"%s\")." % (k, tag),
        "",
    ]
    return "\n".join(lines)


def decide(res):
    """-> (continue?, why). Continue only on agreed actions and no question for the user."""
    s = res.get("summary") or {}
    if not res.get("ok"):
        return False, "discussion failed: %s" % res.get("why")
    if [q for q in (s.get("user_needed") or []) if str(q).strip()]:
        return False, "the discussion needs the user: %s" % "; ".join(str(q) for q in s["user_needed"])[:300]
    if not s.get("agreed"):
        return False, "no agreed action (ended %s)" % s.get("ended")
    return True, "%d agreed action(s), ended %s" % (len(s["agreed"]), s.get("ended"))


def handle(tag, task, rc, lb, run, log):
    """The whole failure path. run(topic_text) -> run_discussion-style result. -> (exit code, result dict)."""
    k = fail_index(tag, lb)
    report, slog = keep_failed(tag, k, lb)
    out = {"lean_discuss": "SKIP", "tag": tag, "fail": k, "rounds": 0, "agreed": 0, "doc": "-", "next_task": "-",
           "why": ""}

    def skip(why):
        out["why"] = why
        with open(os.path.join(lb, "questions_for_user.md"), "a", encoding="utf-8") as f:
            f.write("- %s | task `%s` given up after failure %d: %s | report `%s` | doc %s\n"
                    % (time.strftime("%Y-%m-%d %H:%M"), tag, k, why, _rel(report), out["doc"]))
        return 1, out

    if k > MAX_FAILS:
        return skip("failed %d times (budget %d) - no further discussion, for the user's check" % (k, MAX_FAILS))
    res = run(topic(tag, task, report, slog, rc, k))
    s = res.get("summary") or {}
    out.update(rounds=int(s.get("rounds") or 0), agreed=len(s.get("agreed") or []), doc=res.get("doc") or "-")
    go, why = decide(res)
    if not go:
        return skip(why)
    out["why"] = why
    if go:
        nd = os.path.join(lb, "queue", "next")
        os.makedirs(nd, exist_ok=True)
        p = os.path.join(nd, "%s.md" % tag)
        with open(p, "w", encoding="utf-8") as f:
            f.write(retry_task(tag, k, task, report, slog, res))
        out.update(lean_discuss="CONTINUE", next_task=_rel(p))
    return 0, out


def selftest():
    """No model call, no Google, in a temp folder: (1) agreed + no question -> CONTINUE, retry task written, failed
    report kept; (2) a user question -> STOP; (3) no agreed -> STOP; (4) third failure of a tag -> STOP w/o discussion;
    (5) RESULT line is JSON with Windows paths."""
    ok, n = 0, 0

    def check(name, cond):
        nonlocal ok, n
        n += 1
        ok += bool(cond)
        print("%s  %s" % ("PASS" if cond else "FAIL", name))

    def fake(summary, good=True):
        return lambda _t: {"ok": good, "why": "stub", "summary": summary, "doc": r"file://G:\x\doc.md",
                           "summary_path": r"G:\x\summary.json"}

    with tempfile.TemporaryDirectory() as lb:
        def mk(tag):
            open(os.path.join(lb, "lean_report_%s.md" % tag), "w", encoding="utf-8").write('RESULT {"%s": "FAIL"}\n' % tag)
            open(os.path.join(lb, "session_%s.log" % tag), "w", encoding="utf-8").write("x\n")
        mk("a")
        rc, out = handle("a", os.path.join(lb, "a.md"), 0, lb,
                         fake({"rounds": 3, "agreed": ["do X", "then Y"], "user_needed": [], "ended": "converged"}),
                         print)
        p = os.path.join(lb, "queue", "next", "a.md")
        check("1 agreed -> CONTINUE, exit 0", rc == 0 and out["lean_discuss"] == "CONTINUE")
        check("1 retry task written with the actions", os.path.exists(p) and "1. do X" in open(p, encoding="utf-8").read())
        check("1 failed report kept as _fail1", os.path.exists(os.path.join(lb, "lean_report_a_fail1.md"))
              and not os.path.exists(os.path.join(lb, "lean_report_a.md")))
        mk("a")
        rc, out = handle("a", "t", 0, lb, fake({"rounds": 2, "agreed": ["z"], "user_needed": ["beads?"]}), print)
        check("2 user question -> SKIP", rc == 1 and "needs the user" in out["why"] and out["fail"] == 2)
        qf = os.path.join(lb, "questions_for_user.md")
        check("2 question recorded for the user's check", os.path.exists(qf) and "beads?" in open(qf, encoding="utf-8").read())
        mk("a")
        rc, out = handle("a", "t", 0, lb, fake({"rounds": 2, "agreed": ["z"]}), print)
        check("4 third failure -> SKIP without a discussion", rc == 1 and out["fail"] == 3 and out["rounds"] == 0)
        mk("b")
        rc, out = handle("b", "t", 0, lb, fake({"rounds": 6, "agreed": [], "ended": "max-rounds"}), print)
        check("3 no agreed -> SKIP", rc == 1 and "no agreed" in out["why"])
        rc, out = handle("c", "t", 0, lb, fake({}, good=False), print)
        check("3b discussion failed -> SKIP", rc == 1 and "failed" in out["why"])
        line = result_line(out)
        try:
            json.loads(line[len("RESULT "):])
            check("5 RESULT line is JSON", True)
        except ValueError:
            check("5 RESULT line is JSON", False)
    print('RESULT %s' % json.dumps({"lean_discuss_selftest": "PASS" if ok == n else "FAIL", "pass": ok, "fail": n - ok}))
    return 0 if ok == n else 1


def result_line(out):
    return "RESULT " + json.dumps(out, ensure_ascii=False)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["selftest"]:
        return selftest()
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--task", required=True, help="the task file the queue ran (in queue/done)")
    ap.add_argument("--rc", default="?")
    ap.add_argument("--max-min", type=float, default=40.0)
    ap.add_argument("--max-rounds", type=int, default=6)
    ap.add_argument("--stub", action="store_true", help="stub speakers + local doc (no model call); a dry check only")
    a = ap.parse_args(argv)
    qlog = os.path.join(HERE, "queue.log")

    def log(line):
        with open(qlog, "a", encoding="utf-8") as f:
            f.write("%s\n" % line)
        print(line, flush=True)

    def run(text):
        return debate_loop.run_discussion("lean-%s" % a.tag, 0, text, BENCH, log, max_min=a.max_min,
                                          max_rounds=a.max_rounds, stub=a.stub, stub_secs=1.0,
                                          doc="local" if a.stub else "google")

    code, out = handle(a.tag, a.task, a.rc, HERE, run, log)
    log("LEAN-DISCUSS | %s | tag %s | %s | %s | next %s"
        % (time.strftime("%Y-%m-%d %H:%M:%S"), a.tag, out["lean_discuss"], out["why"], out["next_task"]))
    print(result_line(out))
    return code


if __name__ == "__main__":
    sys.exit(main())
