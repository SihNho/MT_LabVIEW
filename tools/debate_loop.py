# ---
# labview: none
# hardware: none
# ---
"""Claude-GPT discussions INSIDE the cycle runner (card chat-D2, user 2026-10-09 "둘 다 넣자").

Two places, each REPLACING a single-model judgement (no new layer):
  outcome  every 5 cycles, where tools/outcome_review.py ran (that script stays the FALLBACK when the discussion errors)
  stuck    HANDBACK-LIMIT in a cycle, or the runner's firefighter trigger -> a discussion BEFORE the next cycle
           (the firefighter ladder runs after it unchanged: the discussion informs, it does not replace the safety rungs)
The result goes to the EXISTING channels: one steer/1 card from the items both speakers agreed
(protocol.steer_from_debate; the judgement session follows it or refuses it with evidence), and one decisions_pending
item per `user_needed` (protocol.add_decision). A Google sign-in failure never blocks the runner: the discussion is
written to a local doc, the runner logs DEBATE-NO-DOC, and one decisions_pending item asks the user to log in.

What already existed and is CALLED here, not re-written: tools/debate_gdoc.py (doc + rounds; --auto-end / --max-rounds /
--summary / --fallback-local added by this card), tools/debate_relay.py (speakers, STOP file, summary()),
tools/bgrun.py (hard deadline + END line), tools/protocol.py (steer/1, decisions-pending/1),
tools/outcome_review.py (cadence: is_due() counts `*outcome-review*.md` in the peer dir - archive_outcome() writes one).
The env the detached launcher sets (tools/debate_start.ps1) is set here for the runner's child; the PowerShell copy stays
as the chat's launch path (one env list in two languages - reported in card chat-D2's facts).

The runner calls, per discussion:  topic = outcome_topic(...) | stuck_topic(...)
                                   res = run_discussion(kind, n, topic, bench, log, ...)
                                   applied = apply(res, kind, n, bench, goalmap, peer_dir, log)
Self-test (no model call, no Google, stub speakers): py tools/debate_loop.py selftest
"""
import glob
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BGRUN = os.path.join(HERE, "bgrun.py")
GDOC = os.path.join(HERE, "debate_gdoc.py")
sys.path.insert(0, HERE)
import protocol  # noqa: E402

DEADLINE_MIN = 40.0      # brief chat-D2: a discussion never holds the runner longer than this (+ GRACE_S, then a kill)
GRACE_S = 90.0           # after the STOP file: time for the relay to kill its speakers and gdoc to write the summary
MAX_ROUNDS = 6
CYCLES_BACK = 5          # the outcome window (outcome_review.EVERY_N_CYCLES)
CLAUDEDEV = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"   # = outcome_review.CLAUDEDEV
RULE = ("요약을 믿지 말고 원문을 읽을 것: 아래 경로의 파일과 줄을 직접 열어 확인하고, 주장마다 file:line 을 붙이세요. "
        "이 토론은 러너가 사이클 사이에 자동으로 연 것입니다. 사용자가 채팅으로 끼어들 수 있습니다.")
FORMAT = ("결론 형식: 계속 / 줄이거나 바꿈 / 판별 실험. STATE 의 agreed 에는 다음 사이클이 그대로 따를 수 있는 행동만 한 줄씩 "
          "(러너가 이것을 조향 카드 steer/1 로 만들어 다음 판단 세션에 줍니다 - 판단 세션은 따르거나 근거를 들어 거절합니다), "
          "user_needed 에는 사용자만 답할 수 있는 질문 하나(없으면 \"\"; 러너가 decisions_pending 항목으로 올립니다).")


def _read(p, limit=None):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            t = f.read()
    except OSError:
        return ""
    return t if limit is None else t[:limit]


def _rel(p):
    return protocol._rel(p).replace("\\", "/")


def slug_for(n, kind, bench):
    """`c<n>-<kind>`, with -2, -3 ... when that discussion dir already holds a relay state (a cycle number re-used
    after a runner restart). -> (slug, dir)."""
    base = "c%d-%s" % (n, kind)
    slug, k = base, 1
    while os.path.exists(os.path.join(bench, "debate", slug, "relay", "state.json")):
        k += 1
        slug = "%s-%d" % (base, k)
    return slug, os.path.join(bench, "debate", slug)


def runner_env(base=None):
    """The child env a discussion needs outside the app (as tools/debate_start.ps1 sets it): the Claude MSIX
    site-packages on PYTHONPATH (Google libraries), GOOGLE_OAUTH_CLIENT_FILE (kept if set), UTF-8 stdio, BENCH_CELL
    unset is left to the relay (it sets it per speaker)."""
    import debate_relay
    env = dict(base if base is not None else os.environ)
    site = os.path.join(debate_relay.MSIX_ROAMING, "Python", "Python%d%d" % sys.version_info[:2], "site-packages")
    if os.path.isdir(site) and site not in env.get("PYTHONPATH", ""):
        env["PYTHONPATH"] = site + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.setdefault("GOOGLE_OAUTH_CLIENT_FILE",
                   os.path.join(os.path.expanduser("~"), ".config", "debate", "client_secret.json"))
    env["PYTHONIOENCODING"] = "utf-8"
    for k in ("CYCLE_SESSION", "CYCLE_ROLE", "ASSIGN_STATE"):     # the speakers are not runner sessions
        env.pop(k, None)
    return env


def refresh_gpt_worktree():
    """The GPT speaker reads the code from the sibling worktree V6_debate (debate_relay --codex-cwd default): bring it
    to master's latest commit, as tools/debate_start.ps1 does. -> (ok, detail); never raises."""
    wt = os.path.join(os.path.dirname(ROOT), "V6_debate")
    try:
        if not os.path.exists(wt):
            cmd = ["git", "-C", ROOT, "worktree", "add", "--detach", wt, "HEAD"]
        else:
            cmd = ["git", "-C", wt, "checkout", "--detach", "master"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        return p.returncode == 0, ("%s rc %d %s" % (" ".join(cmd[3:5]), p.returncode, (p.stderr or "").strip()[:160]))
    except Exception as e:  # noqa: BLE001
        return False, "%s: %s" % (type(e).__name__, e)


# ------------------------------------------------------------------------------------------------------------ topics
def cycle_lines(runner_log, cycles, limit=90):
    """The runner-log lines that belong to the given cycle numbers (CYCLE / NEXT / ASSIGN / HANDBACK* / STEER /
    FAILED-RECIPES / FIREFIGHTER / DEBATE / GATES-DUE ...), each cut to 300 chars, at most `limit` (newest kept)."""
    want = set(int(c) for c in cycles)
    rx = re.compile(r"(?:^CYCLE (\d+) \|)|(?:\bcycles? (\d+)\b)", re.I)
    out = []
    for ln in _read(runner_log).splitlines():
        if ln.startswith(("HEARTBEAT", "BGRUN", "JEV-")):
            continue
        m = rx.search(ln)
        if m and int(m.group(1) or m.group(2)) in want:
            out.append(ln[:300])
    return out[-limit:]


def _cost_of(lines):
    tot = 0.0
    for ln in lines:
        m = re.match(r"^CYCLE \d+ \|[^|]*\|[^|]*\| exit -?\d+ \| \$([0-9.]+)", ln)
        if m:
            tot += float(m.group(1))
    return tot


def _open_decisions(bench):
    return ["%s: %s" % (it.get("id"), str(it.get("question"))[:200])
            for it in protocol.open_decisions(os.path.join(bench, "decisions_pending.json"))]


def _steer_cards(cards_dir, k=4):
    out = []
    for p in sorted(glob.glob(os.path.join(cards_dir, "steer_*.json")), key=os.path.getmtime)[-k:]:
        try:
            c = json.load(open(p, encoding="utf-8"))
            out.append("%s - %s: %s" % (_rel(p), c.get("item"), str(c.get("required_act"))[:200]))
        except (OSError, ValueError):
            out.append("%s (unreadable)" % _rel(p))
    return out


def _next_section(status_path):
    m = re.search(r"^##\s+NEXT\s*$(.*?)(?=^##\s|\Z)", _read(status_path), re.M | re.S)
    return (m.group(1).strip() if m else "(no ## NEXT in STATUS.md)")[:2500]


def _goal_block(goalmap_path):
    try:
        gm = json.load(open(goalmap_path, encoding="utf-8"))
    except (OSError, ValueError):
        return "(goal map unreadable: %s)" % goalmap_path
    rows = ["- %s [%s] %s" % (m.get("id"), m.get("status"), str(m.get("title") or m.get("name") or "")[:120])
            for m in gm.get("milestones", []) if m.get("status") != "done"]
    return "\n".join(rows[:12]) or "(no open milestone)"


def _bullets(xs, empty="(없음)"):
    return "\n".join("- " + str(x) for x in xs) if xs else empty


def outcome_topic(n, bench, runner_log, peer_dir, goalmap_path, status_path, cycles_back=CYCLES_BACK):
    """The outcome discussion's topic (Korean; first line = doc title): goal, what the last `cycles_back` cycles
    delivered and cost (runner-log lines, cycle / result cards, claudeDev files changed in the window), STATUS NEXT,
    earlier steer cards and outcome reviews, open decisions - as paths and extracted lines, never as a summary."""
    cyc = list(range(max(1, n - cycles_back), n))
    lines = cycle_lines(runner_log, cyc)
    cards = os.path.join(bench, "cards")
    t0 = min([os.path.getmtime(p) for p in (os.path.join(cards, "cycle_%d.json" % c) for c in cyc) if os.path.exists(p)]
             or [time.time() - 7 * 86400])
    results = sorted((p for p in glob.glob(os.path.join(cards, "result_*.json")) if os.path.getmtime(p) >= t0),
                     key=os.path.getmtime)
    res_rows = []
    for p in results[-25:]:
        try:
            r = json.load(open(p, encoding="utf-8"))
            res_rows.append("%s %s (%d artefacts)" % (r.get("id"), r.get("status"), len(r.get("artefacts") or [])))
        except (OSError, ValueError):
            pass
    vis = sorted((os.path.basename(p) for p in glob.glob(os.path.join(CLAUDEDEV, "*.vi")) if os.path.getmtime(p) >= t0))
    outs = sorted(glob.glob(os.path.join(peer_dir, "*outcome-review*.md")), key=os.path.getmtime)[-2:]
    return "\n".join([
        "결과 점검 토론 - 사이클 %d 시작 전: 지난 %d사이클이 목표를 움직였나" % (n, len(cyc)),
        "", RULE, "",
        "## 질문",
        "1. 지난 사이클들(%s)의 작업이 산출물(사용자가 실험에 실제로 돌릴 VI, `docs/goalmap.json`)을 움직였나? 무엇이 새로 "
        "실행 가능해졌고, 그 증거는 무엇인가 ('VI가 있다'는 증거가 아님, '돌아서 이 숫자가 나왔다'가 증거)." % (
            ", ".join(str(c) for c in cyc) or "-"),
        "2. 계획이 목표에 비해 무거운가? 유능한 엔지니어라면 무엇을 건너뛰거나 줄였을까?",
        "3. 다음 %d사이클은 무엇을 바꿔야 하나 (계속 / 줄이거나 바꿈 / 판별 실험)?" % CYCLES_BACK,
        "", FORMAT, "",
        "## 출발 자료 (원문 경로 - 직접 열 것)",
        "- 목표: `docs/goalmap.json`, `project-requirements/` (사용자가 직접 쓴 목표)",
        "- 현재 계획과 다음 할 일: `STATUS.md`, `docs/d1/INDEX.md`, `tools/bench/next.json`",
        "- 러너 기록: `%s` (아래는 해당 사이클 줄을 그대로 뽑은 것)" % _rel(runner_log),
        "- 사이클 카드: %s" % (", ".join("`%s`" % _rel(os.path.join(cards, "cycle_%d.json" % c)) for c in cyc) or "-"),
        "- 이전 결과 점검: %s" % (", ".join("`%s`" % _rel(p) for p in outs) or "(없음)"),
        "", "### 열린 마일스톤 (docs/goalmap.json)", _goal_block(goalmap_path),
        "", "### STATUS.md ## NEXT (원문)", _next_section(status_path),
        "", "### 러너 로그 - 사이클 %s (원문 줄, 합계 비용 $%.2f)" % (
            ", ".join(str(c) for c in cyc) or "-", _cost_of(lines)), _bullets(lines),
        "", "### 이 기간의 결과 카드 (tools/bench/cards/result_*.json)", _bullets(res_rows),
        "", "### 이 기간에 바뀐 claudeDev VI", _bullets(vis),
        "", "### 이전 조향 카드", _bullets(_steer_cards(cards)),
        "", "### 사용자 결정 대기 (tools/bench/decisions_pending.json)", _bullets(_open_decisions(bench)),
    ]) + "\n"


def stuck_topic(n, why, bench, runner_log, status_path, fail_lines=(), cycles_back=2):
    """The stuck discussion's topic (Korean; first line = doc title): why the runner called it (HANDBACK-LIMIT / the
    firefighter trigger), the hand-back records of the previous cycle, the failing logs' first failing lines (passed in
    by the runner), the purpose (next.json), the last cycles' runner-log lines."""
    prev = n - 1
    cards = os.path.join(bench, "cards")
    hbs = []
    for p in sorted(glob.glob(os.path.join(cards, "handback_%d_*.json" % prev)), key=os.path.getmtime):
        try:
            h = json.load(open(p, encoding="utf-8"))
            hbs.append("`%s` - trigger %s: %s" % (_rel(p), h.get("trigger"), str(h.get("detail"))[:240]))
        except (OSError, ValueError):
            hbs.append("`%s` (unreadable)" % _rel(p))
    nxt = os.path.join(bench, "next.json")
    try:
        nj = json.load(open(nxt, encoding="utf-8"))
        purpose = "act: %s\npass: %s" % (str(nj.get("act"))[:400], "; ".join(str(x)[:160] for x in nj.get("pass") or []))
    except (OSError, ValueError):
        purpose = "(next.json absent or unreadable)"
    lines = cycle_lines(runner_log, range(max(1, n - cycles_back), n))
    return "\n".join([
        "막힘 토론 - 사이클 %d 시작 전: %s" % (n, why[:120]),
        "", RULE, "",
        "## 왜 열렸나", "러너가 감지: %s" % why,
        "", "## 질문",
        "1. 왜 막혔나? 핸드백 기록과 실패 로그의 첫 실패 줄에서 원인을 찾고, 같은 원인이 반복되는지 판단하세요.",
        "2. 무엇을 바꿔야 하나: 계획 / 순서 / 도구 / 중단 중 무엇이며, 가장 작은 다음 행동은?",
        "3. 그 행동이 맞는지 가르는 가장 싼 판별 실험은?",
        "", FORMAT, "",
        "## 출발 자료 (원문 경로 - 직접 열 것)",
        "- 목적(next.json): `%s`" % _rel(nxt), purpose,
        "- 계획: `STATUS.md`, `docs/d1/INDEX.md`",
        "", "### 핸드백 기록 (사이클 %d)" % prev, _bullets(hbs),
        "", "### 실패 로그의 첫 실패 줄", _bullets(list(fail_lines)),
        "", "### 러너 로그 - 최근 사이클 (원문 줄)", _bullets(lines),
        "", "### 사용자 결정 대기", _bullets(_open_decisions(bench)),
    ]) + "\n"


# ------------------------------------------------------------------------------------------------------------- run
def _kill_tree(pid):
    subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], capture_output=True)


def run_discussion(kind, n, topic_text, bench, log, max_min=DEADLINE_MIN, max_rounds=MAX_ROUNDS, stub=False,
                   stub_secs=0.0, doc="google", grace_s=GRACE_S, poll_s=2.0, _inner=None):
    """Run ONE discussion synchronously: topic -> <bench>/debate/<slug>/topic_in.md, then `debate_gdoc.py run --auto-end`
    under bgrun (hard cap max_min + grace + 5 min). At max_min the relay's STOP file is written (the speakers are killed
    within a second and gdoc writes its summary); a process still alive grace_s later is tree-killed. Logs ONE line
    `DEBATE | <time> | cycle n | kind | doc <url> | rounds r | converged y/n | $x | ended e | <relay dir>` and, when the
    Google doc could not be used, `DEBATE-NO-DOC | ...`. _inner: self-test only, replaces the gdoc command.
    -> {ok, slug, dir, relay, summary_path, summary, rc, deadline, killed, doc, line, why}. Never raises."""
    slug, d = slug_for(n, kind, bench)
    relay = os.path.join(d, "relay")
    os.makedirs(relay, exist_ok=True)
    topic = os.path.join(d, "topic_in.md")
    with open(topic, "w", encoding="utf-8") as f:
        f.write(topic_text)
    sp = os.path.join(d, "summary.json")
    runlog = os.path.join(d, "run.log")
    res = {"ok": False, "slug": slug, "dir": d, "relay": relay, "topic": topic, "summary_path": sp, "summary": None,
           "rc": None, "deadline": False, "killed": False, "doc": None, "line": None, "why": ""}
    stamp = lambda: time.strftime("%Y-%m-%d %H:%M:%S")  # noqa: E731
    try:
        if not stub and _inner is None:
            ok, det = refresh_gpt_worktree()
            log("DEBATE-WORKTREE | %s | cycle %d | %s | %s" % (stamp(), n, "ok" if ok else "NOT refreshed", det))
        inner = _inner or ([sys.executable, "-u", GDOC, "run", "--mode", "rounds", "--topic", topic, "--dir", relay,
                            "--auto-end", "--max-rounds", str(max_rounds), "--summary", sp, "--no-login",
                            "--fallback-local", "--doc", doc, "--poll", "10"]
                           + (["--stub", "--stub-secs", str(stub_secs)] if stub else []))
        cmd = [sys.executable, BGRUN, "--max-min", "%.2f" % (max_min + grace_s / 60.0 + 5), "--log", runlog, "--"] + inner
        log("DEBATE-START | %s | cycle %d | %s | %s | deadline %.1f min | relay %s (chat: py tools/debate_gdoc.py say "
            "--dir %s \"...\")" % (stamp(), n, kind, slug, max_min, _rel(relay), _rel(relay)))
        t0 = time.time()
        p = subprocess.Popen(cmd, cwd=ROOT, env=dict(runner_env(), MATERIAL="1"), stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
        stop_at, kill_at = t0 + max_min * 60.0, t0 + max_min * 60.0 + grace_s
        while p.poll() is None:
            now = time.time()
            if now >= stop_at and not res["deadline"]:
                res["deadline"] = True
                open(os.path.join(relay, "STOP"), "w").close()
                log("DEBATE-DEADLINE | %s | cycle %d | %s | %.1f min reached - STOP written, %.0f s grace"
                    % (stamp(), n, slug, max_min, grace_s))
            if now >= kill_at:
                res["killed"] = True
                _kill_tree(p.pid)
                log("DEBATE-DEADLINE | %s | cycle %d | %s | still running after the grace - process tree killed"
                    % (stamp(), n, slug))
                break
            time.sleep(poll_s)
        try:
            res["rc"] = p.wait(timeout=60)
        except subprocess.TimeoutExpired:
            _kill_tree(p.pid)
            res["rc"] = "killed"
        s = None
        if os.path.exists(sp) and os.path.getmtime(sp) >= t0 - 1:
            try:
                s = json.load(open(sp, encoding="utf-8"))
            except (OSError, ValueError):
                s = None
        res["summary"] = s
        if s is None:
            res["why"] = "no summary written (rc %s%s)" % (res["rc"], ", killed" if res["killed"] else "")
        elif s.get("ended") == "error":
            res["why"] = "the discussion ended in an error: %s" % (s.get("error") or "-")
        elif int(s.get("rounds") or 0) < 1:
            res["why"] = "no round completed (ended %s)" % s.get("ended")
        else:
            res["ok"] = True
            res["why"] = "ended %s" % s.get("ended")
        s = s or {}
        res["doc"] = s.get("doc_url") or (os.path.join(d, "doc.md") if os.path.exists(os.path.join(d, "doc.md")) else None)
        res["line"] = ("DEBATE | %s | cycle %d | %s | doc %s | rounds %d | converged %s | $%.2f | ended %s%s | %s"
                       % (stamp(), n, kind, res["doc"] or "-", int(s.get("rounds") or 0),
                          "y" if s.get("converged") else "n", float(s.get("claude_usd") or 0.0),
                          s.get("ended") or "-", " (deadline)" if res["deadline"] else "", _rel(d)))
        log(res["line"])
        if s.get("doc_error"):
            log("DEBATE-NO-DOC | %s | cycle %d | %s | %s | local doc %s"
                % (stamp(), n, slug, str(s["doc_error"])[:200], _rel(os.path.join(d, "doc.md"))))
    except Exception as e:  # noqa: BLE001 - a discussion must never break the runner
        res["why"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        log("DEBATE-ERROR | %s | cycle %d | %s | %s" % (stamp(), n, slug, res["why"]))
    return res


# ----------------------------------------------------------------------------------------------------------- apply
def archive_outcome(res, n, peer_dir):
    """Write `<peer_dir>/<date>-outcome-review-debate-c<n>.md` so outcome_review.is_due() (and guard_cycle's outcome
    gate, which calls it) counts the discussion as the outcome review. -> path."""
    s = res.get("summary") or {}
    os.makedirs(peer_dir, exist_ok=True)
    p = os.path.join(peer_dir, "%s-outcome-review-debate-c%d.md" % (time.strftime("%Y-%m-%d"), n))
    body = "\n".join([
        "# outcome-review-debate-c%d" % n, "",
        "- **agent:** claude + gpt (Claude-GPT discussion, tools/debate_loop.py, card chat-D2)",
        "- **role:** outcome", "- **kind:** discussion",
        "- **date:** %s" % time.strftime("%Y-%m-%d %H:%M:%S"),
        "- **outcome:** ANSWERED (%s)" % s.get("ended"),
        "- **doc:** %s" % (res.get("doc") or "-"),
        "- **why asked:** outcome review due (every %d cycles); from 2026-10-09 it is a discussion (user '둘 다 넣자')"
        % CYCLES_BACK, "",
        "## Question", "", "Topic file: `%s`" % _rel(res.get("topic") or ""), "",
        "## Answer", "",
        "Rounds %s, converged %s, ended %s, Claude cost $%.2f. Transcript: `%s` (and the doc above)." % (
            s.get("rounds"), s.get("converged"), s.get("ended"), float(s.get("claude_usd") or 0.0),
            _rel(res.get("relay") or "")), "",
        "### Agreed (both speakers' final STATE)", _bullets(s.get("agreed") or []), "",
        "### Open", _bullets(s.get("open") or []), "",
        "### Experiment", _bullets(s.get("experiment") or []), "",
        "### User needed", _bullets(s.get("user_needed") or []), "",
        "## What was done with it", "",
        "Written by the runner (card chat-D2): the agreed items became a steer/1 card and each user question a "
        "decisions_pending item - see the DEBATE-STEER / DEBATE-DECISION lines of tools/bench/cycle_runner.log for "
        "cycle %d. The judgement session follows the steer card or refuses it with evidence in next.json." % n, ""])
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
    return p


def apply(res, kind, n, bench, goalmap_path, peer_dir, log):
    """Turn a finished discussion into the existing channels: steer/1 (protocol.steer_from_debate -> write_steer in
    <bench>/cards), one decisions_pending item per user_needed, one 'log in' item when the Google doc was not reachable,
    and for kind 'outcome' the archive file that resets the outcome cadence. -> {steer, steer_why, decisions, archive}.
    Never raises."""
    out = {"steer": None, "steer_why": "", "decisions": [], "archive": None}
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    s = res.get("summary") or {}
    dec_path = os.path.join(bench, "decisions_pending.json")
    try:
        _a, _o, not_done, _k = protocol.goalmap_ids(goalmap_path)
        blocks = [g for g in (_a or not_done[:1])]
        if res.get("ok"):
            card, why = protocol.steer_from_debate(s, n, kind, res["slug"], [res["summary_path"], res["topic"]],
                                                   goalmap_path)
            out["steer_why"] = why
            if card:
                out["steer"] = protocol.write_steer(card, os.path.join(bench, "cards"))
            log("DEBATE-STEER | %s | cycle %d | %s | %s | %s" % (stamp, n, res["slug"], _rel(out["steer"]) if out["steer"]
                                                               else "no card", why))
            for q in s.get("user_needed") or []:
                did, err = protocol.add_decision(
                    "Discussion %s asks: %s" % (res["slug"], q), ["answer in the chat", "discuss again", "not needed"],
                    "cycle %d" % n, blocks, recommendation=None, path=dec_path, skip_if_open=True)
                out["decisions"].append(did or "NOT written: %s" % err)
                log("DEBATE-DECISION | %s | cycle %d | %s | %s | %s" % (stamp, n, res["slug"], did or "NOT written",
                                                                      (err or q)[:160]))
            if kind == "outcome":
                out["archive"] = archive_outcome(res, n, peer_dir)
        if s.get("doc_error"):
            did, err = protocol.add_decision(
                "The Google login for discussion docs failed (%s); discussion %s was written to a local file only. "
                "Run `py tools/debate_gdoc.py login` on the PC." % (str(s["doc_error"])[:90], res["slug"]),
                ["log in", "keep local-only"], "cycle %d" % n, (), path=dec_path, skip_if_open=False)
            out["decisions"].append(did or "NOT written: %s" % err)
            log("DEBATE-DECISION | %s | cycle %d | %s | %s | Google login needed" % (stamp, n, res["slug"],
                                                                                   did or "NOT written: %s" % err))
    except Exception as e:  # noqa: BLE001
        log("DEBATE-ERROR | %s | cycle %d | apply %s: %s" % (stamp, n, type(e).__name__, str(e)[:200]))
    return out


# -------------------------------------------------------------------------------------------------------- self-test
def selftest():
    """L1 topics carry the sources; L2 stub discussion -> summary, DEBATE line; L3 apply -> valid steer/1 + decisions +
    outcome archive that makes outcome_review.is_due() false; L4 Google auth failure -> local doc, DEBATE-NO-DOC, login
    item, still a steer; L5 deadline -> STOP written, summary ended stopped; L6 a child that ignores STOP is killed after
    the grace. No model call, no Google."""
    import shutil
    import tempfile
    import outcome_review
    tmp = tempfile.mkdtemp(prefix="debate_loop_")
    bench, peer = os.path.join(tmp, "bench"), os.path.join(tmp, "peer")
    os.makedirs(os.path.join(bench, "cards"))
    gm = os.path.join(ROOT, "docs", "goalmap.json")
    status = os.path.join(tmp, "STATUS.md")
    open(status, "w", encoding="utf-8").write("# S\n\n## NEXT\n가짜 다음 행동\n\n## OTHER\nx\n")
    rlog = os.path.join(bench, "cycle_runner.log")
    open(rlog, "w", encoding="utf-8").write(
        "CYCLE 3 | 2026-10-09 01:00 | 2026-10-09 02:00 | exit 0 | $12.5000 | next.json: act three\n"
        "HANDBACK-LIMIT | 2026-10-09 02:00:00 | cycle 4 | 2 hand-back(s) = max\n"
        "CYCLE 4 | 2026-10-09 02:00 | 2026-10-09 03:00 | exit 0 | $7.2500 | next.json: act four\n"
        "CYCLE 9 | x | y | exit 0 | $1.0 | other\n")
    json.dump({"schema": "handback/1", "cycle": 4, "round": 2, "trigger": "a-unexplained-after-retry",
               "detail": "GATE X17 twice", "cards": []}, open(os.path.join(bench, "cards", "handback_4_2.json"), "w"))
    logged = []
    log = logged.append
    ok = []
    try:
        t_out = outcome_topic(5, bench, rlog, peer, gm, status)
        t_st = stuck_topic(5, "HANDBACK-LIMIT in cycle 4", bench, rlog, status, ["build_x.py: **FAIL B4 at #77"])
        ok.append(("L1 topics: outcome has cycles 3-4 lines, cost 19.75, NEXT text, goal map; stuck has the hand-back "
                   "record and the failing line",
                   t_out.splitlines()[0].startswith("결과 점검 토론") and "act three" in t_out and "$19.75" in t_out
                   and "가짜 다음 행동" in t_out and "CYCLE 9" not in t_out and "docs/goalmap.json" in t_out
                   and "handback_4_2.json" in t_st and "GATE X17 twice" in t_st and "FAIL B4 at #77" in t_st))
        r = run_discussion("outcome", 5, t_out, bench, log, max_min=2, stub=True, doc="local")
        s = r["summary"] or {}
        ok.append(("L2 stub outcome discussion: ok, converged at round 3, DEBATE line with the doc link",
                   r["ok"] and s.get("converged") is True and s.get("rounds") == 3 and r["line"] is not None
                   and "| outcome | doc file://" in r["line"] and "converged y" in r["line"]))
        a = apply(r, "outcome", 5, bench, gm, peer, log)
        card = json.load(open(a["steer"], encoding="utf-8")) if a["steer"] else {}
        old = outcome_review.PEER
        outcome_review.PEER = peer
        try:
            due, why = outcome_review.is_due()
        finally:
            outcome_review.PEER = old
        decs = protocol.open_decisions(os.path.join(bench, "decisions_pending.json"))
        ok.append(("L3 apply: steer_5.json valid (debate:c5-outcome, debate-outcome, agreed act), 1 decision, the "
                   "archive makes the outcome review not due",
                   bool(card) and protocol.validate_obj(card, protocol.goalmap_ids(gm)[3])[0]
                   and card.get("item") == "debate:c5-outcome" and card.get("verdicts") == ["debate-outcome"]
                   and "가짜 합의" in card.get("required_act", "") and len(decs) == 1
                   and "가짜: 사용자 판단" in decs[0]["question"] and bool(a["archive"]) and not due))
        apply(r, "outcome", 5, bench, gm, peer, log)            # the same discussion applied twice: no duplicate item
        n_after_reapply = len(protocol.open_decisions(os.path.join(bench, "decisions_pending.json")))
        r4 = run_discussion("stuck", 6, t_st, bench, log, max_min=2, stub=True, doc="authfail")
        a4 = apply(r4, "stuck", 6, bench, gm, peer, log)
        decs = protocol.open_decisions(os.path.join(bench, "decisions_pending.json"))
        ok.append(("L4 auth failure: ok on a local doc, DEBATE-NO-DOC, a login item; a re-applied question is not "
                   "duplicated, a new discussion's question is its own item; steer_6 debate:c6-stuck",
                   n_after_reapply == 1 and
                   r4["ok"] and any(x.startswith("DEBATE-NO-DOC") for x in logged)
                   and any("debate_gdoc.py login" in d["question"] for d in decs)
                   and sum(1 for d in decs if "가짜: 사용자 판단" in d["question"]) == 2
                   and a4["steer"] and json.load(open(a4["steer"], encoding="utf-8"))["item"] == "debate:c6-stuck"))
        t = time.time()
        r5 = run_discussion("outcome", 7, t_out, bench, log, max_min=0.1, stub=True, stub_secs=30, doc="local",
                            grace_s=60, poll_s=0.5)
        s5 = r5["summary"] or {}
        ok.append(("L5 deadline 6 s: STOP written, the stub stops, summary ended stopped, no kill, < 60 s",
                   r5["deadline"] and not r5["killed"] and s5.get("ended") == "stopped" and not r5["ok"]
                   and "(deadline)" in (r5["line"] or "") and time.time() - t < 60))
        t = time.time()
        r6 = run_discussion("stuck", 8, t_st, bench, log, max_min=0.05, grace_s=3, poll_s=0.5,
                            _inner=[sys.executable, "-c", "import time; time.sleep(120)"])
        ok.append(("L6 a child that ignores STOP is tree-killed after the grace; no summary -> not ok",
                   r6["killed"] and not r6["ok"] and r6["summary"] is None and time.time() - t < 40))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    for name, good in ok:
        print("%s  %s" % ("PASS" if good else "FAIL", name))
    bad = [n_ for n_, g in ok if not g]
    print(protocol.result_line(protocol.make_result(len(ok) - len(bad), len(bad), bad[0] if bad else None)))
    return 0 if not bad else 1


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:  # noqa: BLE001
        pass
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest())
    print(__doc__)
    sys.exit(2)
