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
BASE_NOTE = ("경로 기준: 아래의 모든 상대 경로는 lean worktree `%s` (branch bench/lean-20261013) 기준입니다. GPT 작업 폴더 "
             "V6_debate(master)에는 lean_bench 의 보고서와 원본 출력이 없으니 이 절대 경로로 여세요." % ROOT)
REVIEW_FORMAT = ("결론 형식: STATE 의 agreed 첫 줄은 반드시 `VERDICT: PASS` 또는 `VERDICT: FAIL` 하나. PASS 는 (1) 원본에서 다시 "
                 "계산한 받아들임 숫자가 작업의 기준을 모두 만족하고 (2) 안전 기록(사이클 시작/끝 모터 리밋 읽기 값, LabVIEW 종료, "
                 "입력 md5 변화 없음, 원본 VI 미수정)이 모두 맞을 때만. 나머지 agreed 줄: 다음 단계의 방향 - FAIL 이면 원인과 같은 "
                 "작업을 어떻게 다시 할지, PASS 면 계획상 다음 단계가 무엇인지(큐에 이미 있는 작업이 맞는지). 플랜 세션이 이 줄들을 "
                 "읽고 다음 작업 파일을 씁니다. user_needed 에는 사용자만 답할 수 있는 질문(없으면 \"\"), 각 줄 앞에 둘 중 하나를 "
                 "붙일 것 (평가 토론 2026-10-14 합의): `HOLD:` = 안전 규칙·재시도 한도·받아들임 기준의 변경이나 예외 승인이 "
                 "필요함 → 답이 올 때까지 그 일에 기대는 작업만 보류; `ASSUME:` = 허용 범위 안에서 방법을 고르는 문제 → 택한 "
                 "가정을 같은 줄에 적고 진행.")


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


def keep_failed(tag, k, lb, kind="fail"):
    """Rename this run's report and session log to their _<kind><k> names (kind fail | hold). -> (report, log)."""
    out = []
    for base, ext in (("lean_report_%s" % tag, ".md"), ("session_%s" % tag, ".log")):
        src, dst = os.path.join(lb, base + ext), os.path.join(lb, "%s_%s%d%s" % (base, kind, k, ext))
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


def newest(lb, pattern):
    """The newest file matching pattern in lb, or the pattern's literal path when none exists."""
    hits = glob.glob(os.path.join(lb, pattern))
    return max(hits, key=os.path.getmtime) if hits else os.path.join(lb, pattern)


def cycle_id(lb):
    """`<run start yyyymmdd_HHMMSS>-c<n>`: n = 1 + the cycles already completed in this run (REVIEW lines), so every
    record of a cycle carries the same id and a retried tag never overwrites the earlier record (eval 2026-10-14)."""
    start, n = run_window(os.path.join(lb, "queue.log"))
    st = start.replace("-", "").replace(":", "").replace(" ", "_") if start else time.strftime("%Y%m%d_%H%M%S")
    return "%s-c%d" % (st, n + 1)


def review_topic(tag, task, rc, own, lb):
    """The review discussion's topic; first line = the Google doc title. Facts and paths only."""
    parts = [
        "lean 사이클 리뷰: %s (%s)" % (tag, time.strftime("%Y-%m-%d %H:%M")),
        "",
        BASE_NOTE,
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
        "- 사이클 시작/끝 모터 세션 (가장 최근 것): `%s`, `%s`" % (_rel(newest(lb, "motor_session_start_%s*.log" % tag)),
                                                    _rel(newest(lb, "motor_session_end_%s*.log" % tag))),
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
    if verdict == "HOLD":
        what = ("The cycle is ON HOLD: the review gave no verdict even after one retry (the reason is in "
                "questions_for_user.md). Do NOT retry or replace tag %s and do not queue anything that needs its result; "
                "write a task only for a plan step that does not depend on it and is not queued yet." % tag)
    elif verdict == "FAIL" and not given_up:
        what = ("The cycle FAILED (failure %d of %d allowed for this tag). Write a RETRY with the SAME tag: "
                "`tools/bench/lean_bench/queue/next/%s.md`. Keep the original task's start condition, acceptance and "
                "report format; change how to get there, from the review." % (k, MAX_FAILS, tag))
    elif verdict == "FAIL":
        what = ("The cycle FAILED for the %d. time - tag %s is given up (the reason is in questions_for_user.md). Do NOT "
                "retry it. Tasks in the queue that need its PASS will end NOT-STARTED on their own. Write a task only if "
                "the plan has a next step that does NOT depend on %s and is not queued yet." % (k, tag, tag))
    else:
        what = ("The cycle PASSED. If the queue already holds the plan's next step and the review asks no change to it, "
                "write nothing. If a step is missing before the next queued task, or the queue is empty, write the next "
                "step of the plan with a NEW short tag (lowercase letters/digits, not used before in queue/done).")
    what += (" To CHANGE a task that is already queued (e.g. the review says how it must be done), write the full revised "
             "task under the SAME file name into queue/next/ (e.g. queue/next/latest.md for queue/latest.md): it runs "
             "first and the old queued copy is retired automatically.")
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
        "Never queue: anything that needs beads or the user at the rig, a change to rules, hooks, "
        "`tools/motor_gate.py` or `tools/bench/motor_limits.json`, or a commit. Open user questions (evaluation "
        "2026-10-14): a `HOLD:` question (safety rule, retry limit, acceptance change or an exception approval) blocks "
        "ONLY the work that depends on its answer - queue other work; an `ASSUME:` question (a method choice inside the "
        "rules) does not block - take the stated assumption and write it into the task. If the next step needs the user, "
        "write no task and append ONE line starting `HOLD:` or `ASSUME:` to "
        "`tools/bench/lean_bench/questions_for_user.md` instead (that file is the one other file you may write).",
        "Task file format: like the files in `tools/bench/lean_bench/queue/done/` - title, one-session budget line "
        "(<= 180 min, <= $60), what to read, a start condition (which earlier report must say PASS), Do steps with "
        "predictions written BEFORE any LabVIEW run, the prohibitions, and the report "
        "`tools/bench/lean_bench/lean_report_<tag>.md` ending with `RESULT {\"<tag>\": \"PASS|FAIL|INCOMPLETE|NOT-STARTED\", ...}`. "
        "Every task keeps acceptance #1 of 2026-10-13: every saved row's buffer number is its own frame's.",
        "",
        "End your reply with ONE line: PLAN {\"wrote\": \"<path or none>\", \"why\": \"<one sentence>\"}",
    ])


def write_review(lb, tag, own, verdict, effective, res, cid):
    s = res.get("summary") or {}
    p = os.path.join(lb, "lean_review_%s_%s.md" % (tag, cid))
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Review of %s, cycle %s (%s)\n\n" % (tag, cid, time.strftime("%Y-%m-%d %H:%M")))
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
    cid = cycle_id(lb)
    out = {"lean_review": "", "tag": tag, "cycle_id": cid, "own": own, "verdict": "-", "cycle": "-", "plan": "-",
           "doc": "-"}
    if own == "NOT-STARTED":
        out.update(lean_review="SKIP", cycle="NOT-STARTED")
        log("REVIEW | %s | %s | %s | own NOT-STARTED | cycle NOT-STARTED - no review, no plan"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), cid, tag))
        return 0, out

    def verdict_of(r):
        for line in ((r.get("summary") or {}).get("agreed") or []):
            m = VERDICT_RE.match(str(line))
            if m:
                return m.group(1).upper()
        return None

    res = run_discussion(review_topic(tag, task, rc, own, lb))
    verdict = verdict_of(res)
    if verdict is None:
        # cycle 3 (2026-10-14 03:24): a Google Docs SSLEOFError ended the review after round 1. Evaluation 2026-10-14:
        # an error OR a missing verdict -> one retry; still no verdict -> HOLD (never PASS-UNREVIEWED)
        log("REVIEW-RETRY | %s | %s | %s | no verdict (%s) - one retry"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), cid, tag,
               (res.get("summary") or {}).get("error") or res.get("why") or "no VERDICT line"))
        res = run_discussion(review_topic(tag, task, rc, own, lb))
        verdict = verdict_of(res)
    s = res.get("summary") or {}
    out["doc"] = res.get("doc") or "-"
    passed = own == "PASS" and str(rc) == "0"
    if verdict is None:
        effective = "HOLD"
        question(lb, tag, "HOLD: cycle %s - the review gave no VERDICT twice (%s); the task is on hold, not passed - "
                          "check the review record" % (cid, res.get("why") or "no verdict line"))
    else:
        effective = "PASS" if (passed and verdict == "PASS") else "FAIL"
    for q in (s.get("user_needed") or []):
        if str(q).strip():
            qs = str(q).strip()
            question(lb, tag, qs if qs.upper().startswith(("HOLD:", "ASSUME:")) else "HOLD: (unmarked) %s" % qs)
    out.update(verdict=verdict or "none", cycle=effective)
    k, given_up = 0, False
    if effective == "FAIL":
        k = fail_index(tag, lb)
        given_up = k > MAX_FAILS
        if given_up:
            question(lb, tag, "HOLD: failed %d times (budget %d) - given up, not retried" % (k, MAX_FAILS))
    review_md = write_review(lb, tag, own, verdict or "none", effective, res, cid)
    if effective == "FAIL":
        keep_failed(tag, k, lb)
    elif effective == "HOLD":
        keep_failed(tag, fail_index(tag, lb), lb, kind="hold")
    nd = os.path.join(lb, "queue", "next")
    os.makedirs(nd, exist_ok=True)
    before = set(glob.glob(os.path.join(nd, "*.md")))
    prc = run_plan(plan_prompt(tag, task, effective if effective in ("FAIL", "HOLD") else "PASS", k, given_up,
                               review_md, lb))
    new = sorted(set(glob.glob(os.path.join(nd, "*.md"))) - before)
    if len(new) > 1:   # the plan may write at most one task: keep the first, park the rest for the user
        for p in new[1:]:
            os.replace(p, p + ".extra")
        question(lb, tag, "plan wrote %d task files; kept %s, parked the rest as .extra" % (len(new), _rel(new[0])))
    if new:   # a revision of a queued task: retire the old queued copy so the task does not run twice
        old = os.path.join(lb, "queue", os.path.basename(new[0]))
        if os.path.exists(old):
            os.makedirs(os.path.join(lb, "queue", "done"), exist_ok=True)
            os.replace(old, os.path.join(lb, "queue", "done", "%s_superseded_%s.md"
                                         % (os.path.splitext(os.path.basename(old))[0], time.strftime("%Y%m%d_%H%M%S"))))
            log("PLAN-REVISED | %s | %s replaces the queued copy (retired to queue/done)"
                % (time.strftime("%Y-%m-%d %H:%M:%S"), _rel(new[0])))
    out.update(lean_review="DONE", plan=_rel(new[0]) if new else "none (plan rc %s)" % prc)
    log("REVIEW | %s | %s | %s | own %s | verdict %s | cycle %s | plan %s | doc %s"
        % (time.strftime("%Y-%m-%d %H:%M:%S"), cid, tag, own, out["verdict"], effective, out["plan"], out["doc"]))
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
        os.makedirs(os.path.join(lb, "queue"), exist_ok=True)
        open(os.path.join(lb, "queue", "later.md"), "w").write("# old\n")
        mk("a2", "PASS")
        rc, out = cycle("a2", "t.md", 0, lb, disc(["VERDICT: PASS", "later: subVI only"]), plan(["later.md"]), print)
        check("1b revised queued task -> old copy retired, revision kept",
              not os.path.exists(os.path.join(lb, "queue", "later.md"))
              and os.path.exists(os.path.join(lb, "queue", "next", "later.md"))
              and glob.glob(os.path.join(lb, "queue", "done", "later_superseded_*.md")))
        os.remove(os.path.join(lb, "queue", "next", "later.md"))
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
        calls = []

        def flaky(t):
            calls.append(t)
            if len(calls) == 1:
                return {"ok": False, "why": "SSLEOFError", "summary": {"rounds": 1, "ended": "error", "error": "SSL"}}
            return disc(["VERDICT: PASS"])(t)
        mk("g", "PASS")
        rc, out = cycle("g", "t.md", 0, lb, flaky, plan(), print)
        check("4b discussion error -> one retry, verdict from the retry", len(calls) == 2 and out["cycle"] == "PASS")
        mk("d", "PASS")
        nd0 = len(seen)
        rc, out = cycle("d", "t.md", 0, lb, disc(["looks fine"]), plan(), print)
        check("4 no verdict twice -> HOLD (not PASS) + HOLD question + report kept as _hold1",
              out["cycle"] == "HOLD" and "HOLD: cycle" in open(q, encoding="utf-8").read()
              and os.path.exists(os.path.join(lb, "lean_report_d_hold1.md"))
              and not os.path.exists(os.path.join(lb, "lean_report_d.md")))
        check("4 plan told the task is on hold", len(seen) == nd0 + 1 and "ON HOLD" in seen[-1])
        mk("u", "PASS")
        rc, out = cycle("u", "t.md", 0, lb, disc(["VERDICT: PASS"], ["ASSUME: 90 Hz first", "beads when?"]), plan(), print)
        qt = open(q, encoding="utf-8").read()
        check("4c ASSUME kept, unmarked question recorded as HOLD", "ASSUME: 90 Hz first" in qt
              and "HOLD: (unmarked) beads when?" in qt and out["cycle"] == "PASS")
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
        ql = os.path.join(lb, "queue.log")
        with open(ql, "w", encoding="utf-8-sig") as f:
            f.write("2026-10-13 20:00:00 | RUN START (old)\nREVIEW | 2026-10-13 20:01:00 | x-c1 | a | own PASS\n"
                    "2026-10-13 22:22:10 | RUN START (worktree x, max 10 cycles)\n")
            for i in range(1, 5):   # queue lines are NOT counted; only this script's REVIEW lines (incl. NOT-STARTED)
                f.write("2026-10-13 23:0%d:00 | CYCLE %d/10 EXECUTE END t rc=0\n" % (i, i))
                f.write("REVIEW-RETRY | 2026-10-13 23:0%d:30 | x | t | no verdict - one retry\n" % i)
                f.write("REVIEW | 2026-10-13 23:0%d:59 | x-c%d | t | own %s\n" % (i, i, "NOT-STARTED" if i == 2 else "PASS"))
        open(os.path.join(lb, "run_limit.txt"), "w").write("5\n")
        evs = []
        fake_eval = lambda t: (evs.append(t), {"ok": True, "summary": {"rounds": 3, "agreed": ["keep"]}})[1]  # noqa: E731
        check("9 run window counts only the current run", run_window(ql) == ("2026-10-13 22:22:10", 4))
        check("9 4 of 5 cycles -> no evaluation, no STOP",
              maybe_evaluate(lb, ql, print, fake_eval) is None and not os.path.exists(os.path.join(lb, "STOP")))
        with open(ql, "a", encoding="utf-8") as f:
            f.write("REVIEW | 2026-10-13 23:09:00 | x-c5 | t | own PASS\n")
        ev = maybe_evaluate(lb, ql, print, fake_eval)
        check("10 5 of 5 -> STOP written + one evaluation discussion",
              ev is not None and os.path.exists(os.path.join(lb, "STOP")) and len(evs) == 1
              and "사이클 5개" in evs[0] and glob.glob(os.path.join(lb, "lean_eval_*.md")))
        check("10 STOP present -> no second evaluation", maybe_evaluate(lb, ql, print, fake_eval) is None and len(evs) == 1)
    print("RESULT " + json.dumps({"lean_review_selftest": "PASS" if ok == n else "FAIL", "pass": ok, "fail": n - ok}))
    return 0 if ok == n else 1


RUN_START_RE = re.compile(r"^\W*(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \| RUN START")


def run_window(qlog):
    """(start time 'YYYY-mm-dd HH:MM:SS' of the current run, cycles completed in it) from queue.log. A cycle is counted by
    its `REVIEW |` line, which this script writes itself for every outcome (PASS / FAIL / HOLD / NOT-STARTED) - not by
    the queue's own lines, which run 1 lost (evaluation 2026-10-14)."""
    try:
        lines = open(qlog, encoding="utf-8-sig", errors="replace").read().splitlines()
    except OSError:
        return None, 0
    start, n = None, 0
    for t in lines:
        m = RUN_START_RE.match(t)
        if m:
            start, n = m.group(1), 0
        elif t.startswith("REVIEW | "):
            n += 1
    return start, n


def run_limit(lb):
    """The cycle count after which a run stops for the evaluation discussion (run_limit.txt, written by the chat on the
    user's word; user 2026-10-13 "한 5 사이클정도 돌려보고 평가 토론 한번 해보도록 하자"). None = no limit file."""
    try:
        return int(open(os.path.join(lb, "run_limit.txt"), encoding="utf-8").read().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def eval_topic(lb, start, n):
    """The evaluation discussion's topic: the user's words and the run's files (paths only, no chat opinion -
    docs/debate.md: equal weight, round 1 independent)."""
    t0 = time.mktime(time.strptime(start, "%Y-%m-%d %H:%M:%S")) if start else 0
    files = []
    for pat in ("lean_review_*.md", "lean_report_*.md", "plan_*.log", "session_*.log", "motor_session_*.log",
                "questions_for_user.md", "user_notes.md", "queue/done/*.md", "queue/next/*.md", "queue/*.md"):
        files += [p for p in glob.glob(os.path.join(lb, pat)) if os.path.getmtime(p) >= t0 - 1]
    files += [p for p in glob.glob(os.path.join(BENCH, "debate", "c0-lean-*", "summary.json"))
              if os.path.getmtime(p) >= t0 - 1]
    parts = [
        "lean 러너 평가: 실행 → 리뷰(토론) → 플랜, 사이클 %d개 (%s 시작)" % (n, start),
        "",
        BASE_NOTE,
        "",
        "사용자 원문 (2026-10-13): \"한 5 사이클정도 돌려보고 평가 토론 한번 해보도록 하자\". 이 러너의 설계도 사용자 원문: "
        "\"실행 에이전트 --> 리뷰 에이전트 (토론) --> 플랜 방법으로 한 싸이클을 잡으면\", \"실패한 사이클은 멈춰버리지 말고 "
        "토론해서 방향 잡도록\", \"모터 움직임 제한을 위한 훅은 사이클 시작 시점에 걸고, 사이클 종료 시점에 풀리도록\". "
        "사용자는 앞서 '10 사이클마다 멈출 필요도 없겠는데?' 라고 물었습니다.",
        "",
        "## 평가할 것",
        "1. 각 단계가 제 일을 했는가: 실행(작업 결과), 리뷰(원본 출력에서 숫자를 다시 계산했는가, 판정이 맞았는가), "
        "플랜(쓴 작업이 계획 `../V6_ParallelLoop/docs/d1/ring-p6b.md` PD414 와 사용자 의견에 맞았는가).",
        "2. 반복된 실패 유형 (예: 큰 VI 편집 후 ExecState 0) 과 리뷰/플랜이 그것을 바로잡았는지.",
        "3. 사이클당 시간과 비용 (세션 로그의 JSON 결과, 토론 summary 의 claude_usd).",
        "4. 안전 기록: 사이클 시작/끝 모터 리밋 읽기 값, LabVIEW 종료(queue.log 의 LABVIEW-CLOSE / CYCLE-HOOK), 원본 VI 미수정.",
        "5. 권고: 계속 / 줄이거나 바꿈 / 판별 실험 - 그리고 사람의 확인 주기(5 또는 10 사이클마다 멈춤)를 없애도 되는가.",
        "",
        "## 원문 (요약 금지, 직접 열 것)",
        "- 큐 로그: `%s`" % _rel(os.path.join(lb, "queue.log")),
        "- 큐 스크립트와 단계 스크립트: `tools/bench/lean_bench/lean_queue.ps1`, `lean_review.py`, `lean_cycle_hooks.py`, "
        "`launch_lean.ps1`; lean 규칙 `CLAUDE.md`",
    ] + ["- `%s`" % _rel(p) for p in sorted(set(files))] + [
        "",
        REVIEW_RULE.replace("매 사이클 실행 뒤에 자동으로 연 리뷰", "정해진 사이클 수를 마친 뒤 자동으로 연 평가"),
        "",
        "결론 형식: 계속 / 줄이거나 바꿈 / 판별 실험. STATE 의 agreed 에는 러너 구성에 대한 구체적 변경이나 유지 결정을 한 "
        "줄씩, user_needed 에는 사용자가 정할 질문. 각 합의가 누구의 제안에서 나왔는지 적을 것. 이 결론은 채팅이 사용자에게 "
        "보고하고, 적용은 사용자가 정합니다.",
        "",
    ]
    return "\n".join(parts)


def maybe_evaluate(lb, qlog, log, run_discussion_fn):
    """After a cycle: when the run has reached run_limit.txt cycles, write STOP (the queue ends the run at its next loop
    check, BEFORE starting another cycle) and run ONE evaluation discussion. -> summary dict or None."""
    lim = run_limit(lb)
    start, n = run_window(qlog)
    if lim is None or n < lim or os.path.exists(os.path.join(lb, "STOP")):
        return None
    with open(os.path.join(lb, "STOP"), "w", encoding="ascii") as f:
        f.write("%s run limit %d reached (%d cycles since %s) - evaluation discussion, then the user's check\n"
                % (time.strftime("%Y-%m-%d %H:%M:%S"), lim, n, start))
    log("RUN-LIMIT | %s | %d cycles (limit %d) - STOP written; evaluation discussion starts"
        % (time.strftime("%Y-%m-%d %H:%M:%S"), n, lim))
    res = run_discussion_fn(eval_topic(lb, start, n))
    s = res.get("summary") or {}
    p = os.path.join(lb, "lean_eval_%s.md" % time.strftime("%Y%m%d_%H%M"))
    with open(p, "w", encoding="utf-8") as f:
        f.write("# Evaluation of the lean run started %s (%d cycles)\n\n- discussion: %s, rounds %s, ended %s, doc %s\n\n"
                % (start, n, "ok" if res.get("ok") else "FAILED (%s)" % res.get("why"), s.get("rounds"),
                   s.get("ended"), res.get("doc") or "-"))
        for name in ("agreed", "open", "experiment", "user_needed"):
            f.write("## %s\n" % name + "".join("- %s\n" % x for x in (s.get(name) or [])) + "\n")
    log("EVAL | %s | doc %s | record %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), res.get("doc") or "-", _rel(p)))
    return s


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
    ap.add_argument("--root", default=HERE, help="the lean_bench folder (queue, logs, STOP); the mock queue uses a temp one")
    ap.add_argument("--fake", default="", help="mock queue only: JSON scenario replacing the discussions and the plan")
    a = ap.parse_args(argv)
    lb = a.root
    qlog = os.path.join(lb, "queue.log")

    def log(line):
        with open(qlog, "a", encoding="utf-8") as f:
            f.write("%s\n" % line)
        print(line, flush=True)

    if a.fake:
        run_discussion, run_plan, run_eval = fake_steps(a.fake, a.tag, lb)
    else:
        def run_discussion(text):
            return debate_loop.run_discussion("lean-%s-review" % a.tag, 0, text, BENCH, log, max_min=a.max_min,
                                              max_rounds=a.max_rounds)

        def run_plan(p):
            return plan_session(a.tag, p, log)

        def run_eval(text):
            return debate_loop.run_discussion("lean-eval", 0, text, BENCH, log, max_min=60.0, max_rounds=a.max_rounds)
    try:
        code, out = cycle(a.tag, a.task, a.rc, lb, run_discussion, run_plan, log)
    except Exception as e:  # noqa: BLE001 - the review step crashed: the cycle is recorded as HOLD, never lost
        cid = cycle_id(lb)
        why = "%s: %s" % (type(e).__name__, str(e)[:200])
        question(lb, a.tag, "HOLD: cycle %s - the review step crashed (%s); the task is on hold" % (cid, why))
        log("REVIEW | %s | %s | %s | own %s | verdict none | cycle HOLD (review crashed: %s) | plan none | doc -"
            % (time.strftime("%Y-%m-%d %H:%M:%S"), cid, a.tag, report_result(a.tag, lb), why))
        code, out = 1, {"lean_review": "CRASH", "tag": a.tag, "cycle_id": cid, "cycle": "HOLD", "why": why}
    ev = maybe_evaluate(lb, qlog, log, run_eval)
    out["evaluation"] = "none" if ev is None else "done (%s rounds)" % ev.get("rounds")
    print(result_line(out))
    return code


def fake_steps(path, tag, lb):
    """Mock queue only: (run_discussion, run_plan, run_eval) from a JSON scenario
    {"<tag>": {"discussions": [<item>, ...], "plans": [[<file name>, ...], ...]}, "_eval": <item>}, where an item is
    "error" (the discussion ended in an error), "crash" (raises) or a summary dict. Each call consumes the next entry
    (state in <lb>/fake_state.json, since every cycle is a new process)."""
    sc = json.load(open(path, encoding="utf-8"))
    sp = os.path.join(lb, "fake_state.json")

    def take(key, kind, default):
        st = json.load(open(sp, encoding="utf-8")) if os.path.exists(sp) else {}
        i = st.get("%s/%s" % (key, kind), 0)
        st["%s/%s" % (key, kind)] = i + 1
        json.dump(st, open(sp, "w", encoding="utf-8"))
        seq = (sc.get(key) or {}).get(kind) if key != "_eval" else [sc.get("_eval")]
        return seq[i] if seq and i < len(seq) else default

    def item(x):
        if x == "crash":
            raise RuntimeError("fake review crash")
        if x == "die":   # the review process dies without recording anything (hard kill stand-in)
            os._exit(5)
        if x == "error" or x is None:
            return {"ok": False, "why": "fake error", "summary": {"rounds": 1, "ended": "error", "error": "fake"}}
        return {"ok": True, "doc": "fake-doc", "summary_path": "-", "summary": dict(x, rounds=x.get("rounds", 2),
                                                                                   ended=x.get("ended", "converged"))}

    def run_plan(_prompt):
        for name in take(tag, "plans", []):
            open(os.path.join(lb, "queue", "next", name), "w", encoding="utf-8").write("# fake task %s\n" % name)
        return 0

    return (lambda _t: item(take(tag, "discussions", None)), run_plan,
            lambda _t: item(take("_eval", "x", {"agreed": ["fake eval"]})))


if __name__ == "__main__":
    sys.exit(main())
