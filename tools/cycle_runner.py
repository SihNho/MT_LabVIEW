r"""cycle_runner.py - cycles are started by a RUNNER, not by a person, and never continued in a chat.

CLAUDE.md section 3 item 2 ("Session = one cycle - ENFORCED BY A RUNNER"), user decision 2026-09-17
("2번으로 가자. Opus max") after a 15-hour session: each cycle is a FRESH `claude -p` judgement session
(**opus, effort max**) that reads STATUS.md + the current plan, runs one cycle (delegate -> decide ->
retrospective -> STATUS NEXT) and exits. This script spawns it, checks how it ended, and spawns the next -
so no chat session ever grows long again, and the overnight loop needs nobody present.

    py tools/cycle_runner.py                      # loop until a stop condition fires
    py tools/cycle_runner.py --cycles 3           # at most three cycles
    py tools/cycle_runner.py --dry-run --cycles 3 # self-test: the session is replaced by `py -c "print('dry')"`

WHAT ALREADY EXISTED, checked before writing a line of this:
  * `tools/bgrun.py` - the process-tree deadline and the final BGRUN END/TIMEOUT line. EVERY cycle is launched
    THROUGH it rather than with a second copy of that logic (`guard_bash.py` already trusts that shape).
  * `tools/peer.ps1:389-399` - the flags THIS install accepts for a headless claude cell
    (`-p --model --effort --output-format json --permission-mode`), verified against `claude --help`. Not guessed.
  * `tools/hooks/guard_session.py` - the per-session dispatch cap and the after-the-retrospective refusal. This
    runner does not duplicate them; it only starts and ends sessions.
  * `tools/logclass.py` - `cycle_` is registered there as machinery, so a judgement session's transcript is never
    read as a build log by guard_cycle / guard_peer / audit_cycle / bgrun's inner-failure scan.

STOP CONDITIONS (all four, each written to the runner log, the last three also appended to STATUS.md):
  1. `STOP` at the start of a line in STATUS.md's first 60 lines, or a `## STOP` heading - the USER'S handle on
     the loop. Checked BEFORE every cycle. Exit 0.
  2. the session exited non-zero twice in a row. Exit 3.
  3. STATUS.md's `## NEXT` section came out byte-identical two cycles running - a cycle that changed nothing is
     a loop, and a loop is cheaper to stop than to watch. Exit 3.
  4. `--cycles N` exhausted. Exit 0.
USAGE LIMIT (CLAUDE.md's protocol): a rate/usage-limit message in the session's output is NOT a failure - the
runner sleeps until the renewal time + 2 min and RERUNS THE SAME CYCLE from the beginning ("rerun, don't resume";
a cycle interrupted mid-run is void). The partial attempt is logged as a non-result.

SAFETY: this script starts no LabVIEW and touches no instrument. What the spawned session may touch is decided
by STATUS.md's rig-state banner, which `tools/cycle_prompt.md` forbids it to infer.
"""
import argparse
import json
import os
import re
import subprocess
import sys
import time

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BGRUN = os.path.join(HERE, "bgrun.py")

STOP_LINE_RE = re.compile(r"^STOP\b", re.M)
STOP_HEAD_RE = re.compile(r"^#{1,6}\s*STOP\b", re.M)
STATUS_HEAD_LINES = 60
NEXT_RE = re.compile(r"^##\s+NEXT\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)

# A usage/rate-limit refusal, and the renewal instant if the message carries one. Deliberately broad on the
# DETECTION and narrow on the TIME: mistaking a limit for a failure costs a wrongly-stopped loop, while an
# unparsed time only costs the fallback wait.
LIMIT_RE = re.compile(r"usage limit|rate limit|limit reached|too many requests|\b429\b", re.I)
RESET_EPOCH_RE = re.compile(r"reset[sA-Za-z_]*[\"']?\s*[:=]\s*[\"']?(\d{10,13})\b", re.I)
RESET_CLOCK_RE = re.compile(r"reset[s]?\s*(?:at|:)?\s*(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", re.I)
LIMIT_FALLBACK_MIN = 40.0
LIMIT_MAX_SLEEP_S = 8 * 3600
LIMIT_RETRIES = 3

# Cycle-48 retrospective (disposed): `claude -p` kills a backgrounded child when the turn ends; the ceiling
# of 0 removes that wait/kill. Closes the background-kill class standing at 17 cumulative occurrences.
SPAWN_ENV_EXTRA = {"CLAUDE_CODE_PRINT_BG_WAIT_CEILING_MS": "0",
                   "CYCLE_SESSION": "1"}  # tools/hooks/report_gate.py exempts runner cells (they are not the chat)


def spawn_env():
    e = os.environ.copy()
    e.update(SPAWN_ENV_EXTRA)
    return e


def read(p):
    try:
        with open(p, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def stop_marker(status_text):
    """The user's handle on the loop. `STOP` at the start of a line in the head of the file, or a STOP heading."""
    head = "\n".join(status_text.splitlines()[:STATUS_HEAD_LINES])
    m = STOP_LINE_RE.search(head) or STOP_HEAD_RE.search(status_text)
    if not m:
        return None
    line = status_text[m.start():].splitlines()[0].strip()
    return line[:200]


def next_section(status_text):
    m = NEXT_RE.search(status_text)
    return (m.group(1).strip() if m else "")


def next_last_line(status_text):
    lines = [ln.strip() for ln in next_section(status_text).splitlines() if ln.strip()]
    return lines[-1][:160] if lines else "(no NEXT section)"


def session_cmd(a, prompt, model=None, effort=None):
    """The command bgrun will run: one headless judgement session, or the dry-run stand-in."""
    if a.dry_cmd:
        return a.dry_cmd.split() if isinstance(a.dry_cmd, str) else list(a.dry_cmd)
    if a.dry_run:
        return [sys.executable, "-c", "print('dry')"]
    # Flags verified against `claude --help` on this install (and used by tools/peer.ps1 the same way).
    # `claude.exe`, not `claude`: CreateProcess does not apply PATHEXT, so the bare name is not found.
    return ["claude.exe", "-p", "--model", model or a.model, "--effort", effort or a.effort,
            "--output-format", "json", "--permission-mode", a.permission_mode, prompt]


def result_json(log_text):
    """The `--output-format json` envelope out of a bgrun log, or None.

    bgrun brackets the child's output with its own BGRUN lines, so those are dropped and what remains is tried
    as JSON - first whole, then the last line that looks like an object."""
    body = "\n".join(ln for ln in log_text.splitlines() if not ln.startswith("BGRUN ")).strip()
    for cand in (body, *[ln for ln in reversed(body.splitlines()) if ln.startswith("{")][:3]):
        try:
            d = json.loads(cand)
            if isinstance(d, dict):
                return d
        except ValueError:
            continue
    return None


def limit_wait_s(log_text, now=None):
    """Seconds to sleep for a usage limit (renewal + 2 min), or None when this is not a limit message."""
    if not LIMIT_RE.search(log_text):
        return None
    now = now if now is not None else time.time()
    m = RESET_EPOCH_RE.search(log_text)
    if m:
        v = int(m.group(1))
        target = v / 1000.0 if v > 1e11 else float(v)
        return max(0.0, min(target - now + 120.0, LIMIT_MAX_SLEEP_S))
    m = RESET_CLOCK_RE.search(log_text)
    if m:
        hh, mm = int(m.group(1)), int(m.group(2) or 0)
        ap = (m.group(3) or "").lower()
        if ap == "pm" and hh < 12:
            hh += 12
        elif ap == "am" and hh == 12:
            hh = 0
        lt = time.localtime(now)
        target = time.mktime((lt.tm_year, lt.tm_mon, lt.tm_mday, hh, mm, 0, 0, 0, -1))
        if target <= now:
            target += 24 * 3600
        return max(0.0, min(target - now + 120.0, LIMIT_MAX_SLEEP_S))
    return LIMIT_FALLBACK_MIN * 60.0


def log_line(path, text):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except OSError:
        pass
    print(text, flush=True)


def last_cycle_number(runner_log):
    n = 0
    for line in read(runner_log).splitlines():
        m = re.match(r"CYCLE\s+(\d+)\s*\|", line)
        if m:
            n = max(n, int(m.group(1)))
    return n


# FIREFIGHTER (user, 2026-09-18: "기존 구조로 처리가 잘 안되는 부분은 Fable, low로 소방수 파견" ... "단순히 판단만으로는
# 부족한게 아닌가" ... "트리거링 걸리면 발동하도록"). The trigger is MECHANICAL and read from bgrun logs, never from a
# session's feeling of being stuck: when the SAME recipe (tools/recipes/<name>.py) ended `BGRUN END rc!=0` or
# `BGRUN TIMEOUT` in TWO CONSECUTIVE cycles, the NEXT cycle runs with the firefighter model (fable, low) instead of
# opus/max - a whole cycle, so it can execute, not only advise. Exactly ONE firefighter cycle per trigger; if the
# same recipe still fails in that cycle the runner STOPS and hands it to the user (never a second firefighter).
FF_MODEL, FF_EFFORT = "fable", "low"
FF_LADDER = ("low", "medium")     # user 2026-09-18: low first, then medium, then ask the user
# the command follows "limit N min:" - a lazy `.*?:` stopped at the first colon of the TIMESTAMP (self-test, 11:38)
BGRUN_START_RE = re.compile(r"^BGRUN START .*? min:\s*(.*)$", re.M)
BGRUN_FAIL_RE = re.compile(r"^BGRUN (?:END rc=([1-9]\d*)|TIMEOUT)", re.M)
# The recipe must be the SCRIPT bgrun ran (command position after py/python and its flags, optionally behind a
# MATERIAL=1 marker) - not a path mentioned as an argument to a diagnostic (peer finding, 2026-09-18:
# `py tools/diag_x.py tools/recipes/build_y.py` must not fire the trigger).
RECIPE_RE = re.compile(r"^\s*(?:MATERIAL=1\s+)?(?:\S*[\\/])?py(?:thon)?(?:\.exe)?\s+(?:-\S+\s+)*"
                       r"(?:\S*[\\/])?tools[\\/]recipes[\\/]([\w.\-]+\.py)", re.I)
# the first failing gate line of a run: `**FAIL B4 [...] ...`, `FAIL P4 ...`, or bgrun's own `first: ...`
GATE_FAIL_RE = re.compile(r"^\**\s*(FAIL\b[^\n]{0,120})|^BGRUN INNER FAILURE:.*?first:\s*([^\n]{0,120})", re.M)
FF_PROMPT = ("\n\n## FIREFIGHTER CYCLE (runner-triggered, model fable/low)\n"
             "The recipe `%s` is the block (it failed in previous cycles, or the user ordered a firefighter on it "
             "- see STATUS.md). This cycle exists to clear THAT block "
             "and nothing else. You MAY read the failing logs and the recipe yourself and patch the recipe or "
             "the tool it calls directly (the material hand-off is suspended for this one cycle), you MAY run "
             "the recipe under bgrun with the --material flag (`py tools/bgrun.py --material --max-min N --log "
             "tools/bench/<name>.log -- py -u <script>`; the env-prefix MATERIAL=1 form is auto-denied by the "
             "permission layer under `claude -p`), and you must end with a measured result: "
             "either the recipe's gates pass, or a diagnosis with a discriminating test that was RUN. "
             "DO NOT EXIT before that result exists (2026-09-18 12:59: the first firefighter patched the recipe, "
             "backgrounded a retrospective and exited in 6 min without ever running it - that is not a result). "
             "Wait for your own background jobs (bgrun deadlines bound them); if a gate blocks the launch, clear "
             "it inside this cycle. "
             "Every other rule stands: no new process device, no motor move, no original touched, STATUS NEXT "
             "written, retrospective run. If you cannot clear it, say so in NEXT in one paragraph for the user.\n")


LAST_FAIL_LOGS = {}     # key -> log path of the run that produced it, for the most recent failed_recipes() call


def failed_recipes(bench, t_start, t_end):
    """Recipe basenames whose bgrun log (mtime inside [t_start, t_end]) ended rc!=0 or TIMEOUT."""
    out = set()
    LAST_FAIL_LOGS.clear()
    try:
        names = os.listdir(bench)
    except OSError:
        return out
    for fn in names:
        if not fn.endswith(".log") or fn.startswith(("cycle_", "peer_", "priorart_", "retro")):
            continue
        p = os.path.join(bench, fn)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if not (t_start <= mt <= t_end):
            continue
        # bgrun APPENDS: judge the LAST run in the file, not the first START / first failure anywhere (peer
        # finding 2026-09-18: a log that opens with an old rc=1 but whose current run passed must not count)
        txt = read(p)
        starts = list(BGRUN_START_RE.finditer(txt))
        if not starts:
            continue
        m = starts[-1]
        if not BGRUN_FAIL_RE.search(txt[m.end():]):
            continue
        seg = txt[m.end():]
        # bookkeeping tools always carry a standing FAIL (doc_lint L6, audit lines) - never a firefighter signal
        if re.search(r"doc_lint|audit_cycle|violations\.py|retrospective|doc_ingest|outcome_review|"
                     r"prior_art_review|selftest|peer\.ps1", m.group(1), re.I):
            continue
        r = RECIPE_RE.search(m.group(1))
        if r:
            # user 2026-09-18: "동일 실수 반복" - a recipe saved as _v3, _v4 ... each cycle is the SAME recipe (5 cycles slipped
            # past this trigger overnight 2026-09-19 as v3..v7). Strip the version suffix before comparing.
            out.add("recipe:" + re.sub(r"_v\d+(?=\.py$)", "", r.group(1).lower()))
            LAST_FAIL_LOGS["recipe:" + re.sub(r"_v\d+(?=\.py$)", "", r.group(1).lower())] = p
        # SAME MISTAKE, different file name (user, 2026-09-18: "동일 실수 반복하는 것도 판단 조건에 들어가야"): the
        # first failing GATE line of the run, normalised (uids/#numbers dropped, lower-cased, 60 chars) - a recipe
        # renamed v1 -> v2 that dies at the same gate keeps the same signature.
        g = GATE_FAIL_RE.search(seg)
        if g:
            sig = re.sub(r"#\d+|\b\d{3,}\b", "#", g.group(1) or g.group(2) or "").lower()
            sig = re.sub(r"\s+", " ", sig).strip()[:60]
            out.add("gate:" + sig)
            LAST_FAIL_LOGS["gate:" + sig] = p
    # SAME MISTAKE named by the retrospective: a `VIOLATION: repeated-failure-class` line in a retrospective
    # archived during this cycle is the peer's own statement that the cycle repeated a known failure.
    for fn in os.listdir(os.path.join(ROOT, "archive", "peer")) if os.path.isdir(os.path.join(ROOT, "archive", "peer")) else []:
        if "retrospective" not in fn or not fn.endswith(".md"):
            continue
        p = os.path.join(ROOT, "archive", "peer", fn)
        try:
            # CREATION time, not mtime (2026-09-20 02:3x): the next session ANNOTATES the previous retrospective
            # ("why asked" / "verdict"), which moved cycle 48's file into cycle 36's window and fired a false
            # firefighter on a slug that had already been counted once. On Windows st_ctime is the creation time.
            st = os.stat(p)
            if not (t_start <= min(st.st_ctime, st.st_mtime) <= t_end):
                continue
        except OSError:
            continue
        if re.search(r"^VIOLATION:\s*repeated-failure-class\b", read(p), re.M):
            # ONCE PER FILE, EVER (2026-09-21 01:5x): the creation-time fix was beaten when the next session
            # RE-CREATED retrospective-cycle57.md (relocation/annotation by rewrite gives a new creation time),
            # so the same slug was counted in two consecutive cycles and fired a second false firefighter. A
            # retrospective's verdict is counted exactly once, by filename, persisted across runner restarts.
            seen_path = os.path.join(bench, "cycle_runner_retro_seen.json")
            try:
                seen = json.loads(read(seen_path) or "[]")
            except ValueError:
                seen = []
            if fn in seen:
                continue
            seen.append(fn)
            try:
                with open(seen_path, "w", encoding="utf-8") as f:
                    json.dump(seen, f, indent=0)
            except OSError:
                pass
            out.add("retro:repeated-failure-class")
    return out


RETRO_START_RE = re.compile(r"^BGRUN START .*?retrospective\.py --cycle (\S+)", re.M)


def land_retrospective(bench, runner_log):
    """A retrospective the session started but did not finish is RE-RUN by the runner, synchronously.

    Added 2026-09-19 23:5x after five retrospectives (cycles 37, 38, 44, 45, 46, 47 in the sessions' numbering)
    died at session exit: `claude -p` ends its turn, bgrun's child dies with it, `retro.log` has a START and no END,
    and `guard_cycle` then refuses the next cycle's build - three cycles (~$120) produced no deliverable for that
    reason alone. The runner outlives the session, so it is the one process that can let the peer call finish.
    A repair of an existing device (the runner), not a new one. Returns a one-line note or None.
    """
    retro_log = os.path.join(bench, "retro.log")
    text = read(retro_log)
    starts = list(RETRO_START_RE.finditer(text))
    if not starts:
        return None
    last = starts[-1]
    tail = text[last.end():]
    if re.search(r"^BGRUN (END|TIMEOUT)", tail, re.M):
        return None
    cyc = last.group(1)
    cmd = [sys.executable, BGRUN, "--max-min", "20", "--log", retro_log, "--",
           sys.executable, os.path.join(HERE, "retrospective.py"), "--cycle", cyc]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        rc = proc.returncode
    except Exception as e:  # noqa: BLE001 - the runner must never die on bookkeeping
        rc = "exc %s" % e
    note = ("RETRO-LANDED | %s | retrospective --cycle %s had a START without END (killed by session exit); "
            "the runner re-ran it: rc=%s after %.0f s" % (time.strftime("%Y-%m-%d %H:%M:%S"), cyc, rc, time.time() - t0))
    log_line(runner_log, note)
    return note


def note_in_status(status_path, reason):
    """APPEND a stop notice; never rewrite STATUS.md - it is the user's file and the next session's cold start."""
    try:
        with open(status_path, "a", encoding="utf-8") as f:
            f.write("\n## RUNNER STOPPED %s — %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
    except OSError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-min", type=float, default=180.0, help="wall-clock cap for ONE cycle's session")
    ap.add_argument("--cycles", type=int, default=0, help="0 = until a stop condition fires")
    ap.add_argument("--budget-min", type=float, default=480.0,
                    help="GRACEFUL wall-clock budget for the whole run: once exceeded, no NEW cycle is started; the "
                         "cycle in progress always finishes (user, 2026-09-21: never cut a cycle mid-way). Pair it with "
                         "a bgrun cap >= budget + the longest cycle, so bgrun's kill is only the last resort.")
    ap.add_argument("--model", default="opus")
    ap.add_argument("--effort", default="max")
    ap.add_argument("--permission-mode", default="acceptEdits")
    ap.add_argument("--ff-model", default=FF_MODEL, help="firefighter cycle model (user 2026-09-18: fable)")
    ap.add_argument("--firefighter", default="", metavar="RECIPE",
                    help="USER-ORDERED: start the FIRST cycle as a firefighter on this recipe basename (the ladder "
                         "low -> medium -> user then applies as usual)")
    ap.add_argument("--status", default=os.path.join(ROOT, "STATUS.md"))
    ap.add_argument("--bench-dir", default=os.path.join(ROOT, "tools", "bench"))
    ap.add_argument("--prompt-file", default=os.path.join(HERE, "cycle_prompt.md"))
    ap.add_argument("--dry-run", action="store_true", help="replace the session with `py -c \"print('dry')\"`")
    # Whitespace-split, so it carries no path with a space in it. Self-test only; nothing in the real loop uses it.
    ap.add_argument("--dry-cmd", default="", help="self-test only: the exact command to run instead of a session")
    ap.add_argument("--no-sleep", action="store_true", help="self-test only: report a usage-limit wait, do not take it")
    a = ap.parse_args()

    status_path = os.path.abspath(a.status)
    bench = os.path.abspath(a.bench_dir)
    runner_log = os.path.join(bench, "cycle_runner.log")
    os.makedirs(bench, exist_ok=True)
    prompt = read(os.path.abspath(a.prompt_file))
    if not prompt.strip() and not (a.dry_run or a.dry_cmd):
        print("no prompt: %s is empty or missing" % a.prompt_file, flush=True)
        return 4

    n = last_cycle_number(runner_log)
    run_t0 = time.time()
    done = 0
    bad_streak = 0
    unchanged_streak = 0
    fail_hist = []          # per cycle: the set of recipe basenames whose bgrun log failed inside that cycle
    fail_logs_hist = []     # per cycle: key -> log path (for the Jev same-failure check)
    ff_active, ff_pending, ff_rung = False, None, 0
    while True:
        status_text = read(status_path)
        mark = stop_marker(status_text)
        if mark:
            log_line(runner_log, "RUNNER STOP | %s | STATUS.md carries a STOP marker: %s"
                     % (time.strftime("%Y-%m-%d %H:%M:%S"), mark))
            return 0
        if a.cycles and done >= a.cycles:
            log_line(runner_log, "RUNNER STOP | %s | --cycles %d exhausted"
                     % (time.strftime("%Y-%m-%d %H:%M:%S"), a.cycles))
            return 0
        # GRACEFUL BUDGET (user, 2026-09-21 "강제 종료에 대한 규칙은 바꿔야겠는데? 그냥 셧다운 하지 말고 진행 작업들
        # 마무리하고 종료하는 방향으로"): checked ONLY between cycles, so a cycle that has started always runs to its
        # own end (retrospective landed, NEXT written) before the runner exits. bgrun's hard cap stays as the last
        # resort and must be set well above this budget.
        elapsed_min = (time.time() - run_t0) / 60.0
        if a.budget_min and elapsed_min >= a.budget_min:
            log_line(runner_log, "RUNNER STOP | %s | graceful: --budget-min %.0f exceeded (%.0f min elapsed); the last "
                                 "cycle finished normally, no new cycle started - relaunch to continue"
                     % (time.strftime("%Y-%m-%d %H:%M:%S"), a.budget_min, elapsed_min))
            return 0

        n += 1
        next_before = next_section(status_text)
        cyc_log = os.path.join(bench, "cycle_%d.log" % n)
        # firefighter trigger: the same recipe failed in the two previous cycles (fail_hist[-2] & fail_hist[-1])
        # user 2026-09-18: "Low로 첫번, 그 다음 middle로. 그래도 안되면 나한테 판단 요청" - a ladder of at most two
        # firefighter cycles (low, then medium) on the same recipe; the third failure goes to the user.
        ff_recipe = None
        if a.firefighter and done == 0:         # user-ordered firefighter for the first cycle
            ff_recipe, ff_rung = (a.firefighter if ":" in a.firefighter else "recipe:" + a.firefighter).lower(), 0
            log_line(runner_log, "FIREFIGHTER | %s | USER-ORDERED on `%s`" % (time.strftime("%Y-%m-%d %H:%M:%S"),
                                                                             ff_recipe))
        elif ff_active and ff_pending:          # the previous firefighter did not clear it -> next rung
            ff_recipe, ff_rung = ff_pending, ff_rung + 1
        elif len(fail_hist) >= 2 and not ff_active:
            common = fail_hist[-2] & fail_hist[-1]
            # JEV VETO (user 2026-09-22, docs/jev-integration-plan.md #3; measured 92.5 % / Brier 0.059 on 40
            # labelled pairs): the regex says "same recipe / same gate" - ask Jev whether the two failing runs are
            # really the same failure class. A confident NO (p <= 0.30) vetoes the firefighter for that key and
            # is logged; anything else (yes, unknown band, no key, network error) leaves the old rule in force.
            for key in sorted(common):
                la = fail_logs_hist[-2].get(key) if len(fail_logs_hist) >= 2 else None
                lb = fail_logs_hist[-1].get(key) if fail_logs_hist else None
                p_same, jev_err = None, None
                if la and lb and not key.startswith("retro:"):
                    try:
                        import jev
                        p_same, jev_err = jev.same_failure_class(jev.summarise_failure(la), jev.summarise_failure(lb),
                                                                 purpose="firefighter-trigger")
                    except Exception as e:  # noqa: BLE001 - Jev must never break the runner
                        jev_err = "%s: %s" % (type(e).__name__, str(e)[:120])
                if p_same is not None and p_same <= 0.30:
                    log_line(runner_log, "JEV-VETO | %s | `%s` failed in two consecutive cycles but Jev says the two "
                                         "runs are DIFFERENT failures (p_same=%.2f; %s vs %s) - no firefighter for it"
                             % (time.strftime("%Y-%m-%d %H:%M:%S"), key, p_same, os.path.basename(la),
                                os.path.basename(lb)))
                    continue
                if p_same is not None:
                    log_line(runner_log, "JEV-SAME | %s | `%s`: p_same=%.2f (%s vs %s)"
                             % (time.strftime("%Y-%m-%d %H:%M:%S"), key, p_same, os.path.basename(la),
                                os.path.basename(lb)))
                elif la and lb and not key.startswith("retro:"):
                    log_line(runner_log, "JEV-SKIP | %s | `%s`: no reading (%s) - old rule applies"
                             % (time.strftime("%Y-%m-%d %H:%M:%S"), key, jev_err))
                ff_recipe, ff_rung = key, 0
                break
        ff_pending = None
        model, effort = (a.ff_model, FF_LADDER[ff_rung]) if ff_recipe else (a.model, a.effort)
        this_prompt = prompt + (FF_PROMPT % ff_recipe if ff_recipe else "")
        if ff_recipe:
            log_line(runner_log, "FIREFIGHTER | %s | cycle %d runs as %s/%s (rung %d of %d): `%s` failed in the "
                                 "two previous cycles" % (time.strftime("%Y-%m-%d %H:%M:%S"), n, model, effort,
                                                          ff_rung + 1, len(FF_LADDER), ff_recipe))
        ff_active = bool(ff_recipe)
        # NEXT snapshot for guard_bash.next_gate (user, 2026-09-21): the session may not launch its retrospective
        # until `## NEXT` differs from this. Written right before the spawn, from the same status_text the
        # session will read.
        try:
            import hashlib
            with open(os.path.join(bench, "next_snapshot.md5"), "w", encoding="utf-8") as f:
                f.write(hashlib.md5(next_section(status_text).encode("utf-8")).hexdigest())
        except OSError:
            pass
        cmd = ([sys.executable, BGRUN, "--max-min", str(a.max_min), "--log", cyc_log, "--"]
               + session_cmd(a, this_prompt, model, effort))
        for attempt in range(1, LIMIT_RETRIES + 1):
            start = time.strftime("%Y-%m-%d %H:%M:%S")
            t0 = time.time()
            before = len(read(cyc_log))
            proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", env=spawn_env())
            end = time.strftime("%Y-%m-%d %H:%M:%S")
            rc = proc.returncode
            fresh = read(cyc_log)[before:] or (proc.stdout or "")
            wait = limit_wait_s(fresh)
            # TRANSIENT API 5xx (2026-09-22 09:58: two sessions in a row died on "API Error: 500 Internal server
            # error", the second after 5 s with 0 tokens, and the runner stopped on "non-zero twice"). A server-side
            # 5xx is not a judgement matter: wait 5 min and RERUN the cycle, like the usage-limit path.
            if wait is None and rc != 0 and re.search(r"API Error: 5\d\d", fresh):
                wait = 300.0
            if wait is None or attempt == LIMIT_RETRIES:
                break
            # RERUN, DON'T RESUME (CLAUDE.md's usage-limit protocol): the partial attempt is a non-result.
            log_line(runner_log, "CYCLE %d | %s | %s | usage-limit attempt %d, non-result; sleeping %.0f min "
                                 "(renewal + 2 min) then RERUNNING this cycle"
                     % (n, start, end, attempt, wait / 60.0))
            if a.no_sleep:
                break
            time.sleep(wait)

        env = result_json(fresh)
        land_retrospective(bench, runner_log)
        cost =("$%.4f" % env["total_cost_usd"]) if isinstance(env, dict) and isinstance(
            env.get("total_cost_usd"), (int, float)) else "?"
        status_after = read(status_path)
        next_after = next_section(status_after)
        log_line(runner_log, "CYCLE %d | %s | %s | exit %d | %s | %s"
                 % (n, start, end, rc, cost, next_last_line(status_after)))
        done += 1
        fails = failed_recipes(bench, t0, time.time())
        fail_hist.append(fails)
        fail_logs_hist.append(dict(LAST_FAIL_LOGS))
        if fails:
            log_line(runner_log, "FAILED-RECIPES cycle %d: %s" % (n, ", ".join(sorted(fails))))
        if ff_active and ff_recipe in fails:
            if ff_rung + 1 < len(FF_LADDER):
                ff_pending = ff_recipe          # next cycle: the next rung (low -> medium)
                log_line(runner_log, "FIREFIGHTER | %s | %s/%s did not clear `%s`; next cycle escalates to %s"
                         % (time.strftime("%Y-%m-%d %H:%M:%S"), model, effort, ff_recipe, FF_LADDER[ff_rung + 1]))
            else:
                reason = ("the firefighter ladder (%s: %s) did not clear `%s` - it failed again in cycle %d; "
                          "the user's judgement is requested, no third firefighter"
                          % (a.ff_model, " -> ".join(FF_LADDER), ff_recipe, n))
                log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
                note_in_status(status_path, reason)
                return 3

        bad_streak = bad_streak + 1 if rc != 0 else 0
        unchanged_streak = unchanged_streak + 1 if next_after == next_before else 0
        if bad_streak >= 2:
            reason = ("the judgement session exited non-zero twice in a row (last exit %d, log %s) - a repeat "
                      "failure is a judgement matter, not something to retry" % (rc, os.path.basename(cyc_log)))
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        if unchanged_streak >= 2:
            reason = ("STATUS.md's NEXT section was byte-identical after two consecutive cycles (%d and %d) - "
                      "the loop is not moving" % (n - 1, n))
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3


if __name__ == "__main__":
    sys.exit(main())
