# ---
# labview: none
# hardware: none
# ---
"""REVIEW and PLAN, the 2nd and 3rd step of every lean cycle (user 2026-10-13: "실행 에이전트 --> 리뷰 에이전트 (토론) -->
플랜 방법으로 한 싸이클을 잡으면"). The queue (lean_queue.ps1) calls this after the EXECUTE session and the cycle-end hook.

  REVIEW  one read-only Claude-GPT discussion (debate_loop.run_discussion, <= 40 min): re-computes the report's acceptance
          numbers from the raw output files, checks the safety records (motor readback lines, LabVIEW gone, input md5s),
          and gives VERDICT: PASS | FAIL plus the direction for the next step. The cycle counts as PASS only when the
          session's own RESULT is PASS AND the review says PASS (a review cannot turn a measured FAIL into a PASS).
          A failed cycle's report and session log are kept as lean_report_<tag>_fail<k>.md / session_<tag>_fail<k>.log,
          so later tasks that need lean_report_<tag>.md see no PASS.
  PLAN    one Opus session (read + Write only, <= 25 min, <= $10) reads the review and the plan of record and writes AT
          MOST ONE task file into queue/next/ (run before anything else): a same-tag retry after a FAIL (at most
          MAX_FAILS failures per tag), or the next step of the plan when the queue does not already hold it. Anything
          that needs beads, the user at the rig, a user decision or a rule change goes to questions_for_user.md instead.
  A task whose report says NOT-STARTED (its start condition was not met) gets neither step.
Nothing here stops the run: the user checks questions_for_user.md and the review records at the 10-cycle check.

Shared code CALLED, not copied: tools/debate_loop.py run_discussion; tools/bgrun.py for the plan session.
Usage:     py tools/bench/lean_bench/lean_review.py --tag p6fix --task tools/bench/lean_bench/queue/done/p6fix_<ts>.md --rc 0
Self-test: py tools/bench/lean_bench/lean_review.py selftest   (no model call, no Google, temp folder)
"""
import argparse
import glob
import json
import os
import re
import subprocess
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
PLAN_MAX_MIN = 25
PLAN_MAX_USD = 10
VERDICT_RE = re.compile(r"^\W*VERDICT\s*:\s*(PASS|FAIL)\b", re.I)
RESULT_RE = re.compile(r'^\s*`?RESULT\s*(\{.*\})')
REVIEW_RULE = ("요약을 믿지 말고 원문을 읽을 것: 보고서의 숫자를 그대로 옮기지 말고, 보고서가 가리키는 원본 출력 파일(tra, cal, "
               "로그)을 직접 열어 받아들임 숫자를 다시 계산하세요. 주장마다 file:line 을 붙이세요. 이 토론은 lean 작업 큐가 매 사이클 "
               "실행 뒤에 자동으로 연 리뷰입니다. 읽기만 하고 아무것도 실행하거나 고치지 마세요(LabVIEW, 모터, 파일 수정 모두 금지). "
               "사용자가 채팅으로 끼어들 수 있습니다.")
REVIEW_FORMAT = ("결론 형식: STATE 의 agreed 첫 줄은 반드시 `VERDICT: PASS` 또는 `VERDICT: FAIL` 하나. PASS 는 (1) 원본에서 다시 "
                 "계산한 받아들임 숫자가 작업의 기준을 모두 만족하고 (2) 안전 기록(사이클 시작/끝 모터 리밋 읽기 값, LabVIEW 종료, "
                 "입력 md5 변화 없음, 원본 VI 미수정)이 모두 맞을 때만. 나머지 agreed 줄: 다음 단계의 방향 - FAIL 이면 원인과 같은 "
                 "작업을 어떻게 다시 할지, PASS 면 계획상 다음 단계가 무엇인지(큐에 이미 있는 작업이 맞는지). 플랜 세션이 이 줄들을 "
                 "읽고 다음 작업 파일을 씁니다. user_needed 에는 사용자만 답할 수 있는 질문 하나(없으면 \"\") - 비드, 리그에서의 사용자 "
                 "작업, 규칙 변경, 사용자 결정이 필요한 일은 여기로.")


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


def report_result(tag, lb):
    """'PASS' | 'NOT-STARTED' | 'OTHER' from the last RESULT line of lean_report_<tag>.md (missing = OTHER)."""
    try:
        lines = open(os.path.join(lb, "lean_report_%s.md" % tag), encoding="utf-8", errors="replace").read().splitlines()
    except OSError:
        return "OTHER"
    hits = [m.group(1) for m in (RESULT_RE.match(t) for t in lines) if m]
    if not hits:
        return "OTHER"
    v = re.search(r'"%s"\s*:\s*"([A-Z-]+)"' % re.escape(tag), hits[-1])
    return v.group(1) if v and v.group(1) in ("PASS", "NOT-STARTED") else "OTHER"


def fail_index(tag, lb):
    """1 + the number of failed runs of `tag` already kept (lean_report_<tag>_fail<k>.md / session_<tag>_fail<k>.log)."""
    k = 1
    while os.path.exists(os.path.join(lb, "lean_report_%s_fail%d.md" % (tag, k))) or \
            os.path.exists(os.path.join(lb, "session_%s_fail%d.log" % (tag, k))):
        k += 1
    return k


def keep_failed(tag, k, lb):
    """Rename this run's report and session log to their _fail<k> names. -> (report, log) after the rename."""
    out = []
    for base, ext in (("lean_report_%s" % tag, ".md"), ("session_%s" % tag, ".log")):
        src, dst = os.path.join(lb, base + ext), os.path.join(lb, "%s_fail%d%s" % (base, k, ext))
        if os.path.exists(src):
            os.replace(src, dst)
        out.append(dst)
    return tuple(out)


def queue_listing(lb):
    """The task files waiting, in run order (queue/next first, then queue/ oldest first), with their first line."""
    out = []
    for d in (os.path.join(lb, "queue", "next"), os.path.join(lb, "queue")):
        for p in sorted(glob.glob(os.path.join(d, "*.md")), key=os.path.getmtime):
            try:
                first = open(p, encoding="utf-8", errors="replace").readline().strip()
            except OSError:
                first = "(unreadable)"
            out.append("`%s` - %s" % (_rel(p), first[:160]))
    return out or ["(empty)"]


def user_notes(lb):
    """The user's standing notes from the chat (user_notes.md, one per line, written by the chat on the user's word);
    they go into every review topic and plan prompt. -> list of lines."""
    try:
        return [t.strip() for t in open(os.path.join(lb, "user_notes.md"), encoding="utf-8").read().splitlines()
                if t.strip() and not t.startswith("#")]
    except OSError:
        return []


def question(lb, tag, text):
    with open(os.path.join(lb, "questions_for_user.md"), "a", encoding="utf-8") as f:
        f.write("- %s | `%s` | %s\n" % (time.strftime("%Y-%m-%d %H:%M"), tag, text))


def review_topic(tag, task, rc, own, lb):
    """The review discussion's topic; first line = the Google doc title. Facts and paths only."""
    parts = [
        "lean 사이클 리뷰: %s (%s)" % (tag, time.strftime("%Y-%m-%d %H:%M")),
        "",
        "lean 작업 큐가 작업 `%s` 를 실행했습니다 (launch_lean.ps1 rc=%s, 세션이 스스로 쓴 결과: %s). 이 리뷰가 사이클의 "
        "판정을 내리고, 그 다음에 플랜 세션이 다음 작업을 씁니다." % (tag, rc, own),
        "",
        "## 할 일",
        "1. 작업의 받아들임 기준을 원본 출력 파일에서 다시 계산해 PASS / FAIL 판정 (보고서의 숫자와 다르면 그 차이를 사실로).",
        "2. 안전 기록 확인: 사이클 시작/끝 모터 세션 로그의 읽기 값, LabVIEW 종료, 입력 md5, 원본 VI 미수정.",
        "3. 다음 단계의 방향 (FAIL: 원인과 다시 하는 방법 / PASS: 계획상 다음 단계, 큐에 있는 작업이 맞는지).",
        "",
        "## 읽을 원문 (요약 금지, 직접 열 것)",
        "- 작업 지시: `%s`" % _rel(task),
        "- 보고서: `%s`" % _rel(os.path.join(lb, "lean_report_%s.md" % tag)),
        "- 세션 로그: `%s`" % _rel(os.path.join(lb, "session_%s.log" % tag)),
        "- 사이클 시작/끝 모터 세션: `%s`, `%s`" % (_rel(os.path.join(lb, "motor_session_start_%s.log" % tag)),
                                          _rel(os.path.join(lb, "motor_session_end_%s.log" % tag))),
        "- 큐 로그: `%s` (LabVIEW 종료 줄 CYCLE-HOOK / LABVIEW-CLOSE)" % _rel(os.path.join(lb, "queue.log")),
        "- lean 규칙: `%s`" % _rel(os.path.join(ROOT, "CLAUDE.md")),
        "- 계획과 결정: 주 체크아웃 `../V6_ParallelLoop/docs/d1/ring-p6b.md` PD414, `../V6_ParallelLoop/docs/user-rules.md`, "
        "`../V6_ParallelLoop/docs/lean-operation-proposal.md`",
        "- 지난 lean 보고서(같은 도구와 경로): `tools/bench/lean_bench/lean_report.md` (P6-2), "
        "`tools/bench/lean_bench/lean_report_p63.md` (P6-3)",
        "",
        "## 보고서의 RESULT 줄",
    ]
    parts += _tail(os.path.join(lb, "lean_report_%s.md" % tag), 3, "RESULT")
    parts += ["", "## 세션 로그의 마지막 줄들"]
    parts += _tail(os.path.join(lb, "session_%s.log" % tag), 8)
    parts += ["", "## 지금 큐에 있는 작업 (실행 순서)"] + queue_listing(lb)
    notes = user_notes(lb)
    if notes:
        parts += ["", "## 사용자 의견 (채팅에서, 사용자 승인 - 방향을 정할 때 따를 것)"] + notes
    parts += ["", REVIEW_RULE, "", REVIEW_FORMAT, ""]
    return "\n".join(parts)


def plan_prompt(tag, task, verdict, k, given_up, review_md, lb):
    """The plan session's prompt (English; the session reads the Korean review itself)."""
    if verdict == "FAIL" and not given_up:
        what = ("The cycle FAILED (failure %d of %d allowed for this tag). Write a RETRY with the SAME tag: "
                "`tools/bench/lean_bench/queue/next/%s.md`. Keep the original task's start condition, acceptance and "
                "report format; change how to get there, from the review." % (k, MAX_FAILS, tag))
    elif verdict == "FAIL":
        what = ("The cycle FAILED for the %d. time - tag %s is given up (the reason is in questions_for_user.md). Do NOT "
                "retry it. Tasks in the queue that need its PASS will end NOT-STARTED on their own. Write a task only if "
                "the plan has a next step that does NOT depend on %s and is not queued yet." % (k, tag, tag))
    else:
        what = ("The cycle PASSED. If the queue already holds the plan's next step, write nothing. If a step is missing "
                "before the next queued task, or the queue is empty, write the next step of the plan with a NEW short tag "
                "(lowercase letters/digits, not used before in queue/done).")
    return "\n".join([
        "Lean PLAN step of the cycle `%s`. You ONLY plan: read files and write AT MOST ONE new file, a task file under "
        "`tools/bench/lean_bench/queue/next/`. Write nothing else, run nothing, never touch LabVIEW or a motor." % tag,
        "",
        "Read: `CLAUDE.md` (the lean rules); the task that just ran `%s`; the review record `%s` (verdict %s, the "
        "discussion's agreed / open lines and its doc); the plan of record in the main checkout "
        "`../V6_ParallelLoop/docs/d1/ring-p6b.md` (PD414) and `../V6_ParallelLoop/docs/user-rules.md`; "
        "`tools/bench/lean_bench/questions_for_user.md`." % (_rel(task), _rel(review_md), verdict),
        "Queue now, in run order:",
    ] + ["- " + x for x in queue_listing(lb)] + (
        ["", "The user's notes from the chat (follow them in the task you write):"] + ["- " + x for x in user_notes(lb)]
        if user_notes(lb) else []) + [
        "",
        what,
        "",
        "Never queue: anything that needs beads or the user at the rig, an open user decision, a change to rules, hooks, "
        "`tools/motor_gate.py` or `tools/bench/motor_limits.json`, or a commit. If the next step needs one of these, write "
        "no task and append ONE line to `tools/bench/lean_bench/questions_for_user.md` instead (that file is the one "
        "other file you may write).",
        "Task file format: like the files in `tools/bench/lean_bench/queue/done/` - title, one-session budget line "
        "(<= 180 min, <= $60), what to read, a start condition (which earlier report must say PASS), Do steps with "
        "predictions written BEFORE any LabVIEW run, the prohibitions, and the report "
        "`tools/bench/lean_bench/lean_report_<tag>.md` ending with `RESULT {\"<tag>\": \"PASS|FAIL|INCOMPLETE|NOT-STARTED\", ...}`. "
        "Every task keeps acceptance #1 of 2026-10-13: every saved row's buffer number is its own frame's.",
        "",
        "End your reply with ONE line: PLAN {\"wrote\": \"<path or none>\", \"why\": \"<one sentence>\"}",
    ])


def write_review(lb, tag, own, verdict, effective, res):
    s = res.get("summary") or {}
    p = os.path.join(lb, "lean_review_%s.md" % tag)
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Review of %s (%s)\n\n" % (tag, time.strftime("%Y-%m-%d %H:%M")))
        f.write("- session's own result: %s\n- review verdict: %s\n- cycle counts as: %s\n" % (own, verdict, effective))
        f.write("- discussion: %s, rounds %s, ended %s, doc %s\n- summary: `%s`\n\n"
                % ("ok" if res.get("ok") else "FAILED (%s)" % res.get("why"), s.get("rounds"), s.get("ended"),
                   res.get("doc") or "-", _rel(res.get("summary_path") or "-")))
        for name in ("agreed", "open", "experiment", "user_needed"):
            f.write("## %s\n" % name + "".join("- %s\n" % x for x in (s.get(name) or [])) + "\n")
    return p


def cycle(tag, task, rc, lb, run_discussion, run_plan, log):
    """REVIEW then PLAN for one finished cycle. -> (exit code, result dict). Never stops the run (exit 0)."""
    own = report_result(tag, lb)
    out = {"lean_review": "", "tag": tag, "own": own, "verdict": "-", "cycle": "-", "plan": "-", "doc": "-"}
    if own == "NOT-STARTED":
        out.update(lean_review="SKIP", cycle="NOT-STARTED")
        log("REVIEW | %s | %s | NOT-STARTED - no review, no plan" % (time.strftime("%Y-%m-%d %H:%M:%S"), tag))
        return 0, out
    res = run_discussion(review_topic(tag, task, rc, own, lb))
    s = res.get("summary") or {}
    out["doc"] = res.get("doc") or "-"
    verdict = None
    for line in (s.get("agreed") or []):
        m = VERDICT_RE.match(str(line))
        if m:
            verdict = m.group(1).upper()
            break
    passed = own == "PASS" and str(rc) == "0"
    if verdict is None:
        effective = "PASS-UNREVIEWED" if passed else "FAIL"
        question(lb, tag, "review gave no VERDICT (%s); the cycle counted as %s from the session's own result - check "
                          "the review record" % (res.get("why") or "no verdict line", effective))
    else:
        effective = "PASS" if (passed and verdict == "PASS") else "FAIL"
    for q in (s.get("user_needed") or []):
        if str(q).strip():
            question(lb, tag, "review asks: %s" % q)
    out.update(verdict=verdict or "none", cycle=effective)
    k, given_up = 0, False
    if effective == "FAIL":
        k = fail_index(tag, lb)
        given_up = k > MAX_FAILS
        if given_up:
            question(lb, tag, "failed %d times (budget %d) - given up, not retried" % (k, MAX_FAILS))
    review_md = write_review(lb, tag, own, verdict or "none", effective, res)
    if effective == "FAIL":
        keep_failed(tag, k, lb)
    nd = os.path.join(lb, "queue", "next")
    os.makedirs(nd, exist_ok=True)
    before = set(glob.glob(os.path.join(nd, "*.md")))
    prc = run_plan(plan_prompt(tag, task, "FAIL" if effective == "FAIL" else "PASS", k, given_up, review_md, lb))
    new = sorted(set(glob.glob(os.path.join(nd, "*.md"))) - before)
    if len(new) > 1:   # the plan may write at most one task: keep the first, park the rest for the user
        for p in new[1:]:
            os.replace(p, p + ".extra")
        question(lb, tag, "plan wrote %d task files; kept %s, parked the rest as .extra" % (len(new), _rel(new[0])))
    out.update(lean_review="DONE", plan=_rel(new[0]) if new else "none (plan rc %s)" % prc)
    log("REVIEW | %s | %s | own %s | verdict %s | cycle %s | plan %s | doc %s"
        % (time.strftime("%Y-%m-%d %H:%M:%S"), tag, own, out["verdict"], effective, out["plan"], out["doc"]))
    return 0, out


def plan_session(tag, prompt, log):
    """One Opus session, Read/Grep/Glob/Write only, under bgrun (PLAN_MAX_MIN, PLAN_MAX_USD). -> rc."""
    plog = os.path.join(HERE, "plan_%s_%s.log" % (tag, time.strftime("%Y%m%d_%H%M%S")))
    cmd = [sys.executable, os.path.join(TOOLS, "bgrun.py"), "--max-min", str(PLAN_MAX_MIN), "--log", plog, "--",
           "claude.exe", "-p", "--model", "claude-opus-5-5", "--effort", "high", "--permission-mode", "acceptEdits",
           "--allowedTools", "Read,Grep,Glob,Write", "--max-budget-usd", str(PLAN_MAX_USD), "--output-format", "json",
           prompt]
    log("PLAN-START | %s | %s | log %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), tag, _rel(plog)))
    rc = subprocess.call(cmd, cwd=ROOT)
    log("PLAN-END | %s | %s | rc %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), tag, rc))
    return rc


def result_line(out):
    return "RESULT " + json.dumps(out, ensure_ascii=False)


def selftest():
    """No model call, no Google, temp folder. Cases: own PASS + review PASS; own PASS + review FAIL (report kept as
    _fail1, retry asked); NOT-STARTED (no review, no plan); no verdict (PASS-UNREVIEWED + question); third failure
    (given up + question); user question recorded; plan wrote two files (one parked); RESULT is JSON."""
    ok, n = 0, 0

    def check(name, cond):
        nonlocal ok, n
        n += 1
        ok += bool(cond)
        print("%s  %s" % ("PASS" if cond else "FAIL", name))

    def disc(agreed, user_needed=(), good=True):
        return lambda _t: {"ok": good, "why": "stub", "doc": r"file://G:\x\doc.md", "summary_path": r"G:\x\s.json",
                           "summary": {"rounds": 2, "ended": "converged", "agreed": list(agreed),
                                       "user_needed": list(user_needed)}}

    with tempfile.TemporaryDirectory() as lb:
        seen = []

        def plan(write=()):
            def f(prompt):
                seen.append(prompt)
                for name in write:
                    open(os.path.join(lb, "queue", "next", name), "w").write("# t\n")
                return 0
            return f

        def mk(tag, res):
            open(os.path.join(lb, "lean_report_%s.md" % tag), "w", encoding="utf-8").write(
                'x\nRESULT {"%s": "%s", "minutes": 5}\n' % (tag, res))
            open(os.path.join(lb, "session_%s.log" % tag), "w", encoding="utf-8").write("x\n")

        q = os.path.join(lb, "questions_for_user.md")
        mk("a", "PASS")
        rc, out = cycle("a", "t.md", 0, lb, disc(["VERDICT: PASS", "next: latest as queued"]), plan(), print)
        check("1 own PASS + review PASS -> PASS, report kept",
              out["cycle"] == "PASS" and os.path.exists(os.path.join(lb, "lean_report_a.md")))
        check("1 plan ran with the PASS instruction", seen and "The cycle PASSED" in seen[-1])
        mk("b", "PASS")
        rc, out = cycle("b", "t.md", 0, lb, disc(["VERDICT: FAIL", "col 0 recomputed 2517/2518"]), plan(["b.md"]), print)
        check("2 own PASS + review FAIL -> FAIL, report kept as _fail1",
              out["cycle"] == "FAIL" and os.path.exists(os.path.join(lb, "lean_report_b_fail1.md"))
              and not os.path.exists(os.path.join(lb, "lean_report_b.md")))
        check("2 plan asked for a same-tag retry and wrote it", "SAME tag" in seen[-1] and out["plan"].endswith("b.md"))
        mk("c", "NOT-STARTED")
        k0 = len(seen)
        rc, out = cycle("c", "t.md", 0, lb, disc(["VERDICT: PASS"]), plan(), print)
        check("3 NOT-STARTED -> no review, no plan", out["lean_review"] == "SKIP" and len(seen) == k0)
        mk("d", "PASS")
        rc, out = cycle("d", "t.md", 0, lb, disc(["looks fine"]), plan(), print)
        check("4 no verdict -> PASS-UNREVIEWED + question",
              out["cycle"] == "PASS-UNREVIEWED" and "no VERDICT" in open(q, encoding="utf-8").read())
        for i in range(3):
            mk("e", "FAIL")
            rc, out = cycle("e", "t.md", 1, lb, disc(["VERDICT: FAIL"]), plan(), print)
        check("5 third failure -> given up + question, no retry asked",
              "given up" in open(q, encoding="utf-8").read() and "Do NOT retry" in seen[-1])
        mk("f", "PASS")
        rc, out = cycle("f", "t.md", 0, lb, disc(["VERDICT: PASS"], ["P6-4 needs beads - when?"]),
                        plan(["x1.md", "x2.md"]), print)
        check("6 user question recorded", "P6-4 needs beads" in open(q, encoding="utf-8").read())
        check("7 two plan files -> one kept, one parked",
              os.path.exists(os.path.join(lb, "queue", "next", "x1.md"))
              and os.path.exists(os.path.join(lb, "queue", "next", "x2.md.extra")))
        try:
            json.loads(result_line(out)[len("RESULT "):])
            check("8 RESULT line is JSON", True)
        except ValueError:
            check("8 RESULT line is JSON", False)
    print("RESULT " + json.dumps({"lean_review_selftest": "PASS" if ok == n else "FAIL", "pass": ok, "fail": n - ok}))
    return 0 if ok == n else 1


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
    a = ap.parse_args(argv)
    qlog = os.path.join(HERE, "queue.log")

    def log(line):
        with open(qlog, "a", encoding="utf-8") as f:
            f.write("%s\n" % line)
        print(line, flush=True)

    def run_discussion(text):
        return debate_loop.run_discussion("lean-%s-review" % a.tag, 0, text, BENCH, log, max_min=a.max_min,
                                          max_rounds=a.max_rounds)

    code, out = cycle(a.tag, a.task, a.rc, HERE, run_discussion, lambda p: plan_session(a.tag, p, log), log)
    print(result_line(out))
    return code


if __name__ == "__main__":
    sys.exit(main())
