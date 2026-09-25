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
  3. `tools/bench/next.json` (C7, next/1) came out absent, invalid or byte-identical two cycles running - a cycle
     that changed nothing is a loop, and a loop is cheaper to stop than to watch. Exit 3. (Until 2026-09-24 this
     compared STATUS.md's prose `## NEXT`.) `stop_requested: true` in next.json stops the runner with exit 0.
  4. `--cycles N` exhausted. Exit 0.
  (2026-09-24, card chat-D) also: LabVIEW not verified gone at cycle end (labview_close_hook), and a steer/1 card
  refused twice (protocol.steer_after_cycle -> a decisions_pending item). Exit 3.
  (2026-09-26, card chat-M1) also: the JUDGEMENT LADDER (opus medium -> opus high -> fable low -> fable medium,
  state in <bench>/judge_ladder.json) triggered again at fable/medium -> a decisions_pending item. Exit 3.
  JUDGE A/B: until 2026-09-28 07:00 KST the level-0 effort is medium on odd cycles, high on even (--judge-ab).
USAGE LIMIT (CLAUDE.md's protocol): a rate/usage-limit message in the session's output is NOT a failure - the
runner sleeps until the renewal time + 2 min and RERUNS THE SAME CYCLE from the beginning ("rerun, don't resume";
a cycle interrupted mid-run is void). The partial attempt is logged as a non-result.

SAFETY: this script starts no LabVIEW and touches no instrument. What the spawned session may touch is decided
by STATUS.md's rig-state banner, which `tools/cycle_prompt.md` forbids it to infer.
"""
import argparse
import hashlib
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
ERRORLIST_RETRY_S = 20      # card chat-E1: one retry of a COM-not-ready Error List FAIL
ERRORLIST_REUSE_OUT = None  # card 81-1: where an offline re-verdict JSON is written (None = bench; self-tests set a tmp)
sys.path.insert(0, HERE)
import protocol  # noqa: E402  - session protocol v1: C1 cycle card, C6 first_fail_signature, C7 next.json

# SESSION PROTOCOL v1 (docs/session-protocol.md, user-approved 2026-09-24), wired 2026-09-24 (task card chat-B):
#   C1  before every spawn the runner writes `<bench>/cards/cycle_<n>.json` (cycle/1, validated) and the session's
#       prompt starts with the one line `CARD <that path>`.
#   C7  the session writes `<bench>/next.json` (next/1). It REPLACES the md5 of STATUS.md's prose `## NEXT` in both
#       places that used it: the snapshot guard_bash.next_gate compares against (now the md5 of next.json's bytes,
#       or `absent`), and stop condition 3 (a next.json that is absent, invalid or byte-identical after the cycle
#       counts as "unchanged"; twice running stops the loop). `stop_requested: true` in next.json stops the runner.
#   C6  the FAILED-RECIPES same-mistake signature is protocol.first_fail_signature (RESULT.first_fail; the old
#       GATE_FAIL_RE only for runs that started before protocol.SWITCH_TS).
RIG_STATE_CARD = {"disassembled": "분해", "assembled": "조립", "experiment": "실험중"}
CYCLE_RULES = ["§3 judgement vs material", "§2c run the cycle to the end", "Stages are SIMULATED"]

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


# JUDGEMENT LADDER (user 2026-09-26, card chat-M1): the judgement model is raised BY RULE, from files only, never by
# a session's own feeling. Level 0 = --model/--effort (opus 5.5 medium; A/B below); +1 after a cycle whose next.json
# came out UNCHANGED, or whose retrospective (archived in that cycle) names a judgement-quality VIOLATION slug; a
# cycle that DELIVERS (a PASS result card with artefacts, or a goalmap milestone newly `done`) resets to 0. A trigger
# at level 3 is RUNNER STOP + a decisions_pending item. Data: fable/low delivered L7-1b (cycles 71/72) after Opus failed
# twice; cycle 87 fable/low judgement produced nothing in 6 min - so fable is a rung, not the default.
# The recipe FIREFIGHTER ladder is unchanged; both map onto the same RANK scale and the higher rank wins, so the two
# never stack above rank 3 = fable/medium.
JUDGE_RANKS = [None, ("claude-opus-5-5", "high"), ("fable", "low"), ("fable", "medium")]   # rank 0 = --model/--effort
JUDGE_TOP = len(JUDGE_RANKS) - 1
JUDGE_SLUGS = ("inference-over-measurement", "wrong-ordering", "judgement-in-material")
FF_RANK = {"low": 2, "medium": 3}
VIOLATION_SLUG_RE = re.compile(r"^VIOLATION:\s*([a-z][\w-]*)", re.M)
# JUDGE A/B (user 2026-09-26, "Opus 5.5도 기본을 medium이 좋을지 high가 좋을지도 판단 필요"): until 2026-09-28 07:00 KST
# the LEVEL-0 effort alternates by cycle parity (odd = medium, even = high); a raised ladder level overrides it.
JUDGE_AB_UNTIL = 1790546400    # 2026-09-28 07:00:00 KST = 2026-09-27 22:00:00 UTC (calendar.timegm)


def judge_ab_effort(n, mode, now=None):
    """(effort | None, why). mode on|off|auto; auto = on before JUDGE_AB_UNTIL."""
    now = time.time() if now is None else now
    on = mode == "on" or (mode == "auto" and now < JUDGE_AB_UNTIL)
    if not on:
        return None, "A/B off (%s)" % ("after 2026-09-28 07:00 KST" if mode == "auto" else mode)
    return ("medium" if n % 2 else "high"), "A/B cycle parity %s" % ("odd" if n % 2 else "even")


def judge_choice(level, ff_recipe, ff_rung, base_model, base_effort):
    """(rank, model, effort): the higher of the judgement-ladder level and the firefighter rung, capped at fable/medium."""
    rank = max(0, min(int(level), JUDGE_TOP))
    if ff_recipe:
        rank = max(rank, FF_RANK.get(FF_LADDER[min(ff_rung, len(FF_LADDER) - 1)], 2))
    rank = min(rank, JUDGE_TOP)
    if rank == 0:
        return 0, base_model, base_effort
    m, e = JUDGE_RANKS[rank]
    return rank, m, e


def judge_ladder_step(level, next_moved, slugs, delivered):
    """-> (new_level, reason, stop). Pure; the caller persists and logs."""
    if delivered:
        return 0, "delivered (%s) - reset to level 0" % delivered, False
    trig = []
    if not next_moved:
        trig.append("next.json UNCHANGED")
    hit = sorted(set(slugs) & set(JUDGE_SLUGS))
    if hit:
        trig.append("retrospective VIOLATION " + ",".join(hit))
    if not trig:
        return level, "no trigger - level %d kept" % level, False
    if level >= JUDGE_TOP:
        return level, "level %d (fable/medium) triggered again: %s" % (level, "; ".join(trig)), True
    return level + 1, "+1: %s" % "; ".join(trig), False


def retro_slugs_in_window(peer_dir, t_start, t_end):
    """VIOLATION slugs from retrospective files CREATED inside the cycle window (creation time, as failed_recipes)."""
    out = set()
    try:
        names = os.listdir(peer_dir)
    except OSError:
        return out
    for fn in names:
        if "retrospective" not in fn or not fn.endswith(".md"):
            continue
        p = os.path.join(peer_dir, fn)
        try:
            st = os.stat(p)
        except OSError:
            continue
        if t_start <= min(st.st_ctime, st.st_mtime) <= t_end:
            out.update(VIOLATION_SLUG_RE.findall(read(p)))
    return out


def goalmap_done(path):
    try:
        with open(path, encoding="utf-8") as f:
            return {m.get("id") for m in json.load(f).get("milestones", []) if m.get("status") == "done"}
    except (OSError, ValueError, AttributeError):
        return set()


def delivered_in_window(cards_dir, t_start, t_end, done_before, goalmap_path):
    """'' or a short description: a PASS result/1 card with artefacts written in the window, or a milestone newly done."""
    newly = sorted(goalmap_done(goalmap_path) - set(done_before))
    if newly:
        return "goalmap milestone done: " + ",".join(newly)
    try:
        names = sorted(os.listdir(cards_dir))
    except OSError:
        return ""
    for fn in names:
        if not (fn.startswith("result_") and fn.endswith(".json")):
            continue
        p = os.path.join(cards_dir, fn)
        try:
            if not (t_start <= os.path.getmtime(p) <= t_end):
                continue
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and d.get("schema") == "result/1" and d.get("status") == "PASS" and d.get("artefacts"):
            return "PASS card " + fn
    return ""


def judge_state_load(bench):
    d = protocol._json_load(os.path.join(bench, "judge_ladder.json"), {})
    try:
        return max(0, min(int(d.get("level", 0)), JUDGE_TOP)), str(d.get("reason", "start"))
    except (TypeError, ValueError):
        return 0, "start"


def judge_state_save(bench, level, reason, n):
    try:
        protocol._json_save(os.path.join(bench, "judge_ladder.json"),
                            {"level": level, "reason": reason[:300], "after_cycle": n,
                             "at": time.strftime("%Y-%m-%d %H:%M:%S")})
    except Exception:   # noqa: BLE001 - a lost state file only restarts the ladder at 0
        pass


def add_judge_decision(n, reason, blocks, path):
    """One open decisions-pending/1 item for a judgement ladder exhausted at fable/medium. (id, None) | (None, why)."""
    d = protocol._json_load(path, {"schema": "decisions-pending/1", "items": []})
    items = d.setdefault("items", [])
    day = time.strftime("%Y-%m-%d")
    did = "D-%s-%02d" % (day, 1 + sum(1 for it in items if str(it.get("id", "")).startswith("D-%s-" % day)))
    q = ("Judgement ladder exhausted in cycle %d (opus medium -> opus high -> fable low -> fable medium): %s. "
         "How should the work continue?" % (n, reason))
    items.append({"id": did, "asked": time.strftime("%Y-%m-%dT%H:%M"), "by": "cycle %d" % n, "question": q[:300],
                  "options": ["re-plan the current item", "restart the ladder at level 0", "discuss"],
                  "recommendation": None, "blocks": [b for b in blocks if re.match(r"^M[0-9]+[a-z]?$", b)],
                  "status": "open", "answer": None, "answered_at": None})
    ok, why = protocol.validate_obj(d)
    if not ok:
        return None, why
    protocol._json_save(path, d)
    return did, None


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
        # C6: the signature is the run's own RESULT.first_fail; GATE_FAIL_RE only for a pre-switch run without one.
        st_ts, _st_cmd, st_seg = protocol.last_segment(txt)
        raw = protocol.first_fail_signature(st_seg, GATE_FAIL_RE, st_ts)
        if raw:
            sig = re.sub(r"#\d+|\b\d{3,}\b", "#", raw).lower()
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


def git_commit_cycle(n, runner_log):
    """Commit everything the cycle left in the tree (2026-09-24: cycles 68/69 ended with 129 uncommitted files;
    neither the runner nor the session prompt ever committed, so the chat had to). Never fails the cycle."""
    try:
        subprocess.run(["git", "add", "-A"], cwd=ROOT, timeout=120, capture_output=True)
        msg = "Cycle %d: session outputs (runner auto-commit)\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" % n
        r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT, timeout=120, capture_output=True, text=True)
        log_line(runner_log, "GIT | %s | cycle %d | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                          "committed" if r.returncode == 0 else "nothing to commit / rc=%d" % r.returncode))
    except Exception as e:  # noqa
        log_line(runner_log, "GIT | cycle %d | commit failed: %s" % (n, e))


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


MOTOR_OK = {"start": "SESSION START OK", "end": "SESSION END OK"}
MOTOR_VERIFY = ("PI controller limits match the file", "ASI controller limits match the file")


def motor_limits_hook(phase, n, a, bench, runner_log, status_text):
    """User, 2026-09-23 ("훅으로 묶어서 매 사이클마다 시작할때는 묶고, 종료시에는 풀고. 그 다음 각 싸이클 시작 및 종료
    시점마다 제대로 리밋 셋팅 되어있는지 확인하도록 훅에 추가"): every cycle opens with `motor_gate.py --session start`
    (controller limits WRITTEN and READ BACK) and closes with `--session end` (limits RELEASED and READ BACK).
    Until this hook existed the limits set on 2026-09-18 stayed on for five days because `--session end` was a
    command nobody called.

    Returns (ok, reason). 'ok' means the gate ran, exited 0, printed its OK line AND both readback-verify lines.
    Rig state 실험중 / unknown: the ports are the user's - nothing is sent, the skip is logged, ok=True.
    Dry runs and --no-motor-hooks skip too (self-tests must not open serial ports)."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if a.dry_run or a.dry_cmd or getattr(a, "no_motor_hooks", False):
        log_line(runner_log, "MOTOR-LIMITS | %s | cycle %d %s | skipped (dry run / --no-motor-hooks)" % (stamp, n, phase))
        return True, "skipped"
    try:
        sys.path.insert(0, HERE)
        import motor_gate
        state = motor_gate.rig_state(status_text)
    except Exception as e:  # noqa: BLE001
        state = "unknown (%s)" % e
    if state not in ("assembled", "disassembled"):
        log_line(runner_log, "MOTOR-LIMITS | %s | cycle %d %s | skipped: rig state %s (ports are the user's)"
                 % (stamp, n, phase, state))
        return True, "skipped: rig state %s" % state
    log = os.path.join(bench, "motor_session_%s_cycle%d.log" % (phase, n))
    cmd = [sys.executable, BGRUN, "--max-min", "5", "--log", log, "--",
           sys.executable, os.path.join(HERE, "motor_gate.py"), "--session", phase]
    proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
    text = read(log) + (proc.stdout or "") + (proc.stderr or "")
    ok = (proc.returncode == 0 and MOTOR_OK[phase] in text and all(v in text for v in MOTOR_VERIFY))
    sess = os.path.join(bench, "motor_session.json")
    if ok and phase == "start" and not os.path.exists(sess):
        ok = False
    if ok and phase == "end" and os.path.exists(sess):
        ok = False
    verdict = "OK (limits %s and read back on PI and ASI)" % ("SET" if phase == "start" else "RELEASED") if ok else \
              "FAIL rc=%d - see %s" % (proc.returncode, os.path.basename(log))
    log_line(runner_log, "MOTOR-LIMITS | %s | cycle %d %s | %s" % (stamp, n, phase, verdict))
    return ok, verdict


LV_IMAGE = "LabVIEW.exe"
LV_GRACE_S = 60.0       # COM Quit, then wait this long for the process to go before forcing it
LV_FORCE_WAIT_S = 30.0
LV_QUIT_SRC = ("import win32com.client as w\n"
               "w.Dispatch('LabVIEW.Application').Quit()\n")


def _lv_pids():
    """PIDs of running LabVIEW.exe (tasklist, CSV). [] when none; None when tasklist itself failed."""
    try:
        r = subprocess.run(["tasklist", "/FI", "IMAGENAME eq %s" % LV_IMAGE, "/FO", "CSV", "/NH"],
                           capture_output=True, text=True, timeout=30)
    except Exception:  # noqa: BLE001
        return None
    if r.returncode != 0:
        return None
    return [int(x) for x in re.findall(r'^"%s","(\d+)"' % re.escape(LV_IMAGE), r.stdout or "", re.M | re.I)]


def _lv_quit_graceful(timeout_s):
    """Ask LabVIEW to quit over COM from a CHILD process (a hung COM call is killed with the child, never the
    runner). A save prompt left open by the quit is not answered - the force step follows (rule 1: never Save)."""
    try:
        r = subprocess.run([sys.executable, "-c", LV_QUIT_SRC], capture_output=True, text=True, timeout=timeout_s)
        return "quit rc=%d" % r.returncode
    except subprocess.TimeoutExpired:
        return "quit call timed out after %.0f s (child killed)" % timeout_s
    except Exception as e:  # noqa: BLE001
        return "quit call failed: %s" % e


def _lv_kill():
    try:
        r = subprocess.run(["taskkill", "/F", "/T", "/IM", LV_IMAGE], capture_output=True, text=True, timeout=30)
        return "taskkill rc=%d" % r.returncode
    except Exception as e:  # noqa: BLE001
        return "taskkill failed: %s" % e


def _wait_gone(limit_s, poll_s=2.0):
    t0 = time.time()
    while True:
        p = _lv_pids()
        if p == []:
            return True
        if time.time() - t0 >= limit_s:
            return False
        time.sleep(poll_s)


def labview_close_hook(n, a, bench, runner_log, status_text):
    """User 2026-09-24 ("사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것, 특히 카메라가 계속 Acquisition 하면 기계에
    좋지 않으니"; CLAUDE.md 1b MOTOR GRANT): after the motor end hook, every cycle ends with LabVIEW CLOSED and VERIFIED
    GONE - COM Quit first (graceful), then taskkill /F (force; nothing is ever saved), then tasklist must show no
    LabVIEW.exe. Returns (ok, reason). Skipped (logged, ok=True) under --dry-run/--dry-cmd/--no-labview-close and in
    rig state 실험중/unknown (then LabVIEW is the user's experiment - it is never killed by the runner)."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if a.dry_run or a.dry_cmd or getattr(a, "no_labview_close", False):
        log_line(runner_log, "LABVIEW-CLOSE | %s | cycle %d | skipped (dry run / --no-labview-close)" % (stamp, n))
        return True, "skipped"
    try:
        import motor_gate
        state = motor_gate.rig_state(status_text)
    except Exception as e:  # noqa: BLE001
        state = "unknown (%s)" % e
    if state not in ("assembled", "disassembled"):
        log_line(runner_log, "LABVIEW-CLOSE | %s | cycle %d | skipped: rig state %s (LabVIEW is the user's)"
                 % (stamp, n, state))
        return True, "skipped: rig state %s" % state
    pids = _lv_pids()
    if pids is None:
        verdict, ok = "FAIL: tasklist could not be read", False
    elif not pids:
        verdict, ok = "OK: no LabVIEW.exe was running", True
    else:
        steps = [_lv_quit_graceful(LV_GRACE_S)]
        if _wait_gone(LV_GRACE_S):
            verdict, ok = "OK: closed gracefully (pids %s; %s)" % (pids, steps[0]), True
        else:
            steps.append(_lv_kill())
            gone = _wait_gone(LV_FORCE_WAIT_S)
            left = _lv_pids()
            ok = bool(gone and left == [])
            verdict = ("OK: forced (pids %s; %s)" % (pids, "; ".join(steps)) if ok else
                       "FAIL: LabVIEW.exe still running after quit + force (pids %s; %s)" % (left, "; ".join(steps)))
    log_line(runner_log, "LABVIEW-CLOSE | %s | cycle %d | %s" % (stamp, n, verdict))
    return ok, verdict


def errorlist_hook(n, a, bench, runner_log, status_text):
    """User decision 5, 2026-09-24 ("사이클 시작하기 전에 LabVIEW 컴파일 에러 창은 반드시 확인해야할듯"): before every
    cycle - and BEFORE the motor start hook (card chat-C2) - `tools/errorlist_check.py` reads the current bed's Error
    List on a byte-identical scratch copy (GUI, capture-confirmed), double-clicks each item, and compares against the
    bed's expected-errors file.

    Returns (verdict, json_path, reason); verdict OK | MISMATCH | FAIL | SKIP. FAIL stops the runner before the cycle;
    MISMATCH starts the cycle and the cycle/1 card carries the result. Skipped (logged) in rig state 실험중 (no
    LabVIEW use at all), under --dry-run/--dry-cmd and --no-errorlist-hook (self-tests)."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if a.dry_run or a.dry_cmd or getattr(a, "no_errorlist_hook", False):
        log_line(runner_log, "ERRORLIST | %s | cycle %d | SKIP | dry run / --no-errorlist-hook" % (stamp, n))
        return "SKIP", None, "skipped"
    try:
        import motor_gate
        state = motor_gate.rig_state(status_text)
    except Exception as e:  # noqa: BLE001
        state = "unknown (%s)" % e
    if state == "experiment":
        log_line(runner_log, "ERRORLIST | %s | cycle %d | SKIP | rig state 실험중 (no LabVIEW use)" % (stamp, n))
        return "SKIP", None, "rig state experiment"
    # REUSE (card 81-1, retrospective-cycle80 device-failed): bed md5 == the md5 of the newest complete saved read of
    # that bed -> re-verdict its raw items OFFLINE with the current checker, no LabVIEW, log 'REUSE'. Any other case
    # (no bed, changed md5, incomplete read, an error in the offline path) -> the GUI read below, unchanged.
    try:
        import errorlist_check as EC
        bed = EC.current_bed_text(status_text)
        if bed:
            bmd5 = hashlib.md5(open(bed, "rb").read()).hexdigest()
            src, raw, why = EC.find_reusable(bed, bmd5, bench)
            if src:
                verdict, js = EC.reverdict(bed, src, raw, bench, out_dir=ERRORLIST_REUSE_OUT)
                log_line(runner_log, "ERRORLIST | %s | cycle %d | REUSE | %s | %s (bed md5 %s unchanged since %s; "
                         "no LabVIEW)" % (stamp, n, verdict, js, bmd5, os.path.basename(src)))
                return verdict, js, "offline re-verdict of %s" % os.path.basename(raw)
            log_line(runner_log, "ERRORLIST | %s | cycle %d | GUI-READ | %s" % (stamp, n, why))
    except Exception as e:  # noqa: BLE001 - the offline path must never block the GUI read
        log_line(runner_log, "ERRORLIST | %s | cycle %d | GUI-READ | reuse path error %s: %s"
                 % (stamp, n, type(e).__name__, str(e)[:160]))

    def run_once(log):
        cmd = [sys.executable, BGRUN, "--max-min", "15", "--log", log, "--",
               sys.executable, "-u", os.path.join(HERE, "errorlist_check.py")]
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                              env=dict(os.environ, MATERIAL="1"))
        text = read(log) + (proc.stdout or "")
        m = re.findall(r"ERRORLIST-VERDICT: (OK|MISMATCH|FAIL) (\S.*\.json)", text)
        verdict, js = (m[-1][0], m[-1][1].strip()) if m else ("FAIL", None)
        if "BGRUN END" not in text:
            verdict = "FAIL"
        return verdict, js, text

    log = os.path.join(bench, "errorlist_check_cycle%d.log" % n)
    verdict, js, text = run_once(log)
    # COM NOT READY (card chat-E1, 2026-09-25): the 01:02 restart stopped on com_error -2147221231 (ClassFactory)
    # right after LabVIEW was launched. Such a FAIL is retried ONCE after ERRORLIST_RETRY_S; a second FAIL stops the
    # runner exactly as before. Any other FAIL is not retried.
    if verdict == "FAIL" and ("-2147221231" in text or "ClassFactory" in text):
        log_line(runner_log, "ERRORLIST | %s | cycle %d | FAIL (COM not ready) - retry once in %d s | %s"
                 % (stamp, n, ERRORLIST_RETRY_S, js or os.path.basename(log)))
        time.sleep(ERRORLIST_RETRY_S)
        log = os.path.join(bench, "errorlist_check_cycle%d_retry.log" % n)
        verdict, js, text = run_once(log)
    log_line(runner_log, "ERRORLIST | %s | cycle %d | %s | %s" % (stamp, n, verdict, js or os.path.basename(log)))
    return verdict, js, "see %s" % os.path.basename(log)


def write_cycle_card(bench, n, status_text, model, effort, ff_recipe, motor_verdict, a, errorlist=None, steer=None,
                     note=None):
    """C1: `<bench>/cards/cycle_<n>.json`, validated against docs/protocol/cycle.json. Returns (path, None) or
    (None, reason). `errorlist` is {path, verdict OK|MISMATCH} from errorlist_hook, null when skipped (card chat-C2); `bed` is read
    from the optional `<bench>/bed.json` ({path, md5}) and is null when there is none."""
    try:
        import motor_gate
        rig = RIG_STATE_CARD.get(motor_gate.rig_state(status_text), "unknown")
    except Exception:       # noqa: BLE001
        rig = "unknown"
    bed = None
    try:
        with open(os.path.join(bench, "bed.json"), encoding="utf-8") as f:
            b = json.load(f)
        bed = {"path": str(b["path"]), "md5": b.get("md5")}
    except (OSError, ValueError, KeyError, TypeError):
        pass
    # card 81-1 E1: NOTHING ever writes <bench>/bed.json (grep over tools/: only this reader), so `bed` was null on
    # every card (cycle_81.json). Fall back to the bed the Error List check itself reads (STATUS -> newest named
    # claudeDev D1_*.vi, errorlist_check.current_bed_text) with its md5 - the value errorlist_hook's REUSE compares.
    if bed is None:
        try:
            import errorlist_check as EC
            bp = EC.current_bed_text(status_text)
            if bp:
                bed = {"path": bp, "md5": hashlib.md5(open(bp, "rb").read()).hexdigest()}
        except Exception:   # noqa: BLE001 - a missing bed stays null, as before
            bed = None
    next_path = os.path.join(bench, "next.json")
    card = {"schema": "cycle/1", "cycle": n, "rig_state": rig, "model": model, "effort": effort,
            "firefighter": ff_recipe or None, "bed": bed, "errorlist": errorlist,
            "steer": ({"path": protocol._rel(steer)[:400], "md5": protocol._md5(steer)} if steer else None),
            "motor_session": (motor_verdict or None) and str(motor_verdict)[:120],
            "next": protocol._rel(next_path), "budget": {"minutes": float(a.max_min), "dispatches": 8},
            "rules": CYCLE_RULES}
    if note:
        card["note"] = str(note)[:300]
    ok, why = protocol.validate_obj(card)
    if not ok:
        return None, why
    d = os.path.join(bench, "cards")
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, "cycle_%d.json" % n)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    return p, None


def next_json_reading(bench):
    """(md5 | 'absent', card | None, why | None) of `<bench>/next.json` - the ONE reading the runner uses."""
    return protocol.next_state(os.path.join(bench, "next.json"))


def note_in_status(status_path, reason):
    """APPEND a stop notice; never rewrite STATUS.md - it is the user's file and the next session's cold start."""
    try:
        with open(status_path, "a", encoding="utf-8") as f:
            f.write("\n## RUNNER STOPPED %s — %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
    except OSError:
        pass


# HEARTBEAT (card chat-H1, user 2026-09-25: the session cron never fired all afternoon; "세션 예약이면 세션 바뀔 때마다
# 새로 셋팅 필요 -> 훅으로"). Reporting comes from the RUNNER PROCESS, not from any session timer and no LLM: a
# `HEARTBEAT | ...` line at EVERY CYCLE END (after the motor end hook and the LabVIEW close) and one FINAL at RUNNER
# STOP. No periodic timer (judgement change to the card, user: "싸이클 종료 시점 기준이 좋을 것 같기는 함. 30분을 할 필요는
# 없지"). Each goes to the runner log (so tools/hooks/report_gate.py sees it in cycle_runner_main_*.log and refuses to
# let the chat stay silent), to <bench>/heartbeat_latest.md, and to a Windows toast (tools/heartbeat_toast.ps1,
# detached, never waited on). Dry runs do not toast unless HEARTBEAT_TOAST_STUB=<file> is set, which records the call.
TOAST_PS1 = os.path.join(HERE, "heartbeat_toast.ps1")
_HOOK_PREFIX = {"errorlist": "ERRORLIST |", "motor": "MOTOR-LIMITS |", "close": "LABVIEW-CLOSE |"}


class Heartbeat:
    def __init__(self, a, bench, runner_log, status_path, t0):
        self.a, self.bench, self.runner_log, self.status_path, self.t0 = a, bench, runner_log, status_path, t0
        self.cycle, self.cycle_t0, self.phase = None, None, "starting"
        self.cycles_done, self.cost = 0, 0.0
        self.final_done = False

    # -- state the main loop updates
    def begin(self, n):
        self.cycle, self.cycle_t0, self.phase = n, time.time(), "running"

    def cycle_end(self, n, rc, cost):
        self.cycles_done += 1
        try:
            self.cost += float(str(cost).lstrip("$"))
        except ValueError:
            pass
        self.phase = "ended %s (exit %d, %s)" % (time.strftime("%H:%M"), rc, cost)
        self.emit("cycle-end")

    # -- facts
    def _last_result(self):
        cards = [os.path.join(self.bench, "cards", f) for f in _listdir(os.path.join(self.bench, "cards"))
                 if f.startswith("result_") and f.endswith(".json")]
        if not cards:
            return "none"
        p = max(cards, key=os.path.getmtime)
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
            return "%s %s" % (d.get("id", os.path.basename(p)), d.get("status", "?"))
        except (OSError, ValueError):
            return "%s unreadable" % os.path.basename(p)

    def _hooks(self):
        lines = read(self.runner_log).splitlines()
        out = {}
        for k, pre in _HOOK_PREFIX.items():
            last = next((ln for ln in reversed(lines) if ln.startswith(pre)), None)
            if not last:
                out[k] = "-"
                continue
            parts = [p.strip() for p in last.split("|")]
            v = parts[3] if len(parts) > 3 else "?"
            out[k] = ("%s %s" % (parts[2], v.split()[0] if v else "?"))[:60]
        return out

    def _decisions(self):
        try:
            return len(protocol.open_decisions(os.path.join(self.bench, "decisions_pending.json")))
        except Exception:   # noqa: BLE001
            return -1

    def _next_act(self):
        try:
            _m, card, _w = next_json_reading(self.bench)
            return card["act"][:150] if card else "(no valid next.json)"
        except Exception:   # noqa: BLE001
            return "(unreadable)"

    def _deliverables(self):
        d = os.path.join(self.bench, "cards")
        ids = []
        for f in _listdir(d):
            p = os.path.join(d, f)
            if f.startswith("result_") and f.endswith(".json") and os.path.getmtime(p) >= self.t0:
                try:
                    with open(p, encoding="utf-8") as fh:
                        r = json.load(fh)
                    if r.get("status") == "PASS":
                        ids.append("%s(%d artefacts)" % (r.get("id", f), len(r.get("artefacts") or [])))
                except (OSError, ValueError):
                    pass
        return ", ".join(ids) or "none"

    # -- output
    def emit(self, kind):
        try:
            now = time.time()
            stamp = time.strftime("%Y-%m-%d %H:%M:%S")
            hooks, dec, last = self._hooks(), self._decisions(), self._last_result()
            if self.cycle is None:
                cyc = "no cycle yet (runner up %.0f min)" % ((now - self.t0) / 60.0)
            else:
                cyc = "cycle %d %s since %s (%.0f min)" % (
                    self.cycle, self.phase, time.strftime("%H:%M", time.localtime(self.cycle_t0)),
                    (now - self.cycle_t0) / 60.0)
            hk = "hooks errorlist=%s motor=%s close=%s" % (hooks["errorlist"], hooks["motor"], hooks["close"])
            tag = "FINAL" if kind == "final" else "cycle-end"
            extra = "%s | cycles %d, cost $%.2f, deliverables %s, next act: %s" % (
                tag, self.cycles_done, self.cost, self._deliverables(), self._next_act())
            line = "HEARTBEAT | %s | %s | %s | last result %s | %s | open decisions %d" % (
                stamp, extra, cyc, last, hk, dec)
            log_line(self.runner_log, line)
            self._write_md(kind, stamp, cyc, last, hooks, dec)
            self._toast(kind, cyc, last, dec)
        except Exception as e:  # noqa: BLE001 - a heartbeat must never break the runner
            try:
                log_line(self.runner_log, "HEARTBEAT-ERROR | %s | %s: %s"
                         % (time.strftime("%Y-%m-%d %H:%M:%S"), type(e).__name__, str(e)[:160]))
            except Exception:   # noqa: BLE001
                pass

    def _write_md(self, kind, stamp, cyc, last, hooks, dec):
        kind_ko = {"cycle-end": "사이클 종료 보고", "final": "러너 종료 최종 보고"}.get(kind, kind)
        para = ("%s — %s 기준. 현재 %s. 마지막 결과 카드는 %s, 사용자 결정 대기 %d건. 누적 %d사이클, 비용 $%.2f."
                % (kind_ko, stamp, cyc, last, dec, self.cycles_done, self.cost))
        para += " 이번 실행 산출물: %s. 다음 할 일: %s." % (self._deliverables(), self._next_act())
        rows = [("종류", kind), ("시각", stamp), ("사이클", cyc), ("마지막 결과", last),
                ("Error List 훅", hooks["errorlist"]), ("모터 리밋 훅", hooks["motor"]),
                ("LabVIEW 종료 훅", hooks["close"]), ("결정 대기", str(dec)),
                ("누적 사이클 / 비용", "%d / $%.2f" % (self.cycles_done, self.cost))]
        body = "# 러너 하트비트\n\n%s\n\n| 항목 | 값 |\n|---|---|\n%s\n" % (
            para, "\n".join("| %s | %s |" % (k, str(v).replace("|", "/")) for k, v in rows))
        tmp = os.path.join(self.bench, "heartbeat_latest.md.tmp")
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(body)
        os.replace(tmp, os.path.join(self.bench, "heartbeat_latest.md"))

    def _toast(self, kind, cyc, last, dec):
        title = "cycle runner: %s" % kind
        body = "%s | last %s | decisions %d" % (cyc, last, dec)
        stub = os.environ.get("HEARTBEAT_TOAST_STUB")
        if stub:
            with open(stub, "a", encoding="utf-8") as f:
                f.write("TOAST | %s | %s\n" % (title, body))
            return
        if self.a.dry_run or self.a.dry_cmd:
            return
        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0) | getattr(subprocess, "DETACHED_PROCESS", 0)
        subprocess.Popen(["powershell.exe", "-NoProfile", "-NonInteractive", "-ExecutionPolicy", "Bypass",
                          "-WindowStyle", "Hidden", "-File", TOAST_PS1],
                         env=dict(os.environ, HB_TITLE=title, HB_BODY=body[:240]), creationflags=flags,
                         stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         close_fds=True)

    def final(self):
        if not self.final_done:
            self.final_done = True
            self.emit("final")


def _listdir(d):
    try:
        return os.listdir(d)
    except OSError:
        return []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-min", type=float, default=180.0, help="wall-clock cap for ONE cycle's session")
    ap.add_argument("--cycles", type=int, default=0, help="0 = until a stop condition fires")
    ap.add_argument("--budget-min", type=float, default=480.0,
                    help="GRACEFUL wall-clock budget for the whole run: once exceeded, no NEW cycle is started; the "
                         "cycle in progress always finishes (user, 2026-09-21: never cut a cycle mid-way). Pair it with "
                         "a bgrun cap >= budget + the longest cycle, so bgrun's kill is only the last resort.")
    ap.add_argument("--model", default="claude-opus-5-5")  # user 2026-09-23: Opus 5.5 pinned by id (alias 'opus' resolved to claude-opus-5)
    ap.add_argument("--effort", default="medium")  # user 2026-09-23 14:xx: medium on Opus 5.5 (its medium ~= Opus 5 max on the index); earlier today high (max = +4 pts at 3.3x cost, news.hada.io/topic?id=34142); was max since 2026-09-17
    ap.add_argument("--permission-mode", default="acceptEdits")
    ap.add_argument("--ff-model", default=FF_MODEL, help="firefighter cycle model (user 2026-09-18: fable)")
    ap.add_argument("--firefighter", default="", metavar="RECIPE",
                    help="USER-ORDERED: start the FIRST cycle as a firefighter on this recipe basename (the ladder "
                         "low -> medium -> user then applies as usual)")
    ap.add_argument("--judge-ab", default="auto", choices=("auto", "on", "off"),
                    help="level-0 judgement effort A/B by cycle parity (odd medium, even high); auto = on until "
                         "2026-09-28 07:00 KST (user 2026-09-26)")
    ap.add_argument("--peer-dir", default=os.path.join(ROOT, "archive", "peer"),
                    help="self-test only: where retrospectives are read for the judgement ladder")
    ap.add_argument("--goalmap", default=os.path.join(ROOT, "docs", "goalmap.json"),
                    help="self-test only: the goal map whose milestones count as delivery")
    ap.add_argument("--status", default=os.path.join(ROOT, "STATUS.md"))
    ap.add_argument("--bench-dir", default=os.path.join(ROOT, "tools", "bench"))
    ap.add_argument("--prompt-file", default=os.path.join(HERE, "cycle_prompt.md"))
    ap.add_argument("--dry-run", action="store_true", help="replace the session with `py -c \"print('dry')\"`")
    # Whitespace-split, so it carries no path with a space in it. Self-test only; nothing in the real loop uses it.
    ap.add_argument("--dry-cmd", default="", help="self-test only: the exact command to run instead of a session")
    ap.add_argument("--no-sleep", action="store_true", help="self-test only: report a usage-limit wait, do not take it")
    ap.add_argument("--no-motor-hooks", action="store_true", help="self-test only: skip motor_gate --session start/end (never for a real run)")
    ap.add_argument("--no-errorlist-hook", action="store_true", help="self-test only: skip the cycle-start Error List check (never for a real run)")
    ap.add_argument("--no-labview-close", action="store_true", help="self-test only: skip the cycle-end LabVIEW close (never for a real run)")
    a = ap.parse_args()

    status_path = os.path.abspath(a.status)
    bench = os.path.abspath(a.bench_dir)
    runner_log = os.path.join(bench, "cycle_runner.log")
    os.makedirs(bench, exist_ok=True)
    prompt = read(os.path.abspath(a.prompt_file))
    if not prompt.strip() and not (a.dry_run or a.dry_cmd):
        print("no prompt: %s is empty or missing" % a.prompt_file, flush=True)
        return 4

    run_t0 = time.time()
    hb = Heartbeat(a, bench, runner_log, status_path, run_t0)
    try:
        return _loop(a, status_path, bench, runner_log, prompt, run_t0, hb)
    finally:
        hb.final()      # every exit of the loop follows a RUNNER STOP line: the final summary heartbeat


def _loop(a, status_path, bench, runner_log, prompt, run_t0, hb):
    n = last_cycle_number(runner_log)
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
        hb.begin(n)
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
        # JUDGEMENT LADDER + A/B (card chat-M1): level from <bench>/judge_ladder.json; rank = max(level, ff rung).
        j_level, j_reason = judge_state_load(bench)
        ab_eff, ab_why = judge_ab_effort(n, a.judge_ab)
        base_effort = ab_eff or a.effort
        j_rank, model, effort = judge_choice(j_level, ff_recipe, ff_rung, a.model, base_effort)
        if ff_recipe and model == "fable":
            model = a.ff_model          # --ff-model still names the firefighter's fable build
        if ab_eff:
            log_line(runner_log, "JUDGE-AB | cycle %d | %s | %s" % (n, ab_eff, ab_why if j_rank == 0 else
                                                                   "%s, OVERRIDDEN by rank %d (%s/%s)"
                                                                   % (ab_why, j_rank, model, effort)))
        log_line(runner_log, "JUDGE-LADDER | %s | cycle %d | level %d rank %d -> %s/%s | %s%s"
                 % (time.strftime("%Y-%m-%d %H:%M:%S"), n, j_level, j_rank, model, effort, j_reason[:160],
                    (" | firefighter rung %d" % (ff_rung + 1)) if ff_recipe else ""))
        j_note = "judge-ladder level %d rank %d: %s%s" % (j_level, j_rank, j_reason[:150],
                                                          ("; judge-ab %s" % ab_eff) if ab_eff else "")
        goal_done_before = goalmap_done(a.goalmap)
        this_prompt = prompt + (FF_PROMPT % ff_recipe if ff_recipe else "")
        if ff_recipe:
            log_line(runner_log, "FIREFIGHTER | %s | cycle %d runs as %s/%s (rung %d of %d): `%s` failed in the "
                                 "two previous cycles" % (time.strftime("%Y-%m-%d %H:%M:%S"), n, model, effort,
                                                          ff_rung + 1, len(FF_LADDER), ff_recipe))
        ff_active = bool(ff_recipe)
        # NEXT snapshot for guard_bash.next_gate (user, 2026-09-21; C7 since 2026-09-24): the session may not launch
        # its retrospective until `next.json` differs from this. md5 of next.json's BYTES, or `absent`.
        next_md5_before, _nc, _nw = next_json_reading(bench)
        try:
            with open(os.path.join(bench, "next_snapshot.md5"), "w", encoding="utf-8") as f:
                f.write(next_md5_before)
        except OSError:
            pass
        # ERROR LIST at cycle start, BEFORE the motor start hook (user decision 5, 2026-09-24; card chat-C2). FAIL to
        # read = RUNNER STOP before the cycle (no motor limits were set yet); MISMATCH = the cycle runs, its cycle/1
        # card carries the result and the prompt says to deal with those errors first.
        el_verdict, el_json, el_why = errorlist_hook(n, a, bench, runner_log, status_text)
        if el_verdict == "FAIL":
            reason = "the cycle-start Error List check could not be completed for cycle %d (%s, %s) - no cycle runs " \
                     "on an unread bed" % (n, el_why, el_json)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        el_card = None
        if el_json and el_verdict in ("OK", "MISMATCH"):
            el_card = {"path": protocol._rel(el_json)[:400], "verdict": el_verdict}
            os.environ["ERRORLIST_JSON"] = el_json
            this_prompt += ("\n\nERRORLIST (cycle-start Error List check, user decision 5 2026-09-24): %s - %s\n"
                            % (el_verdict, el_card["path"]))
            if el_verdict == "MISMATCH":
                this_prompt += ("The bed's Error List does NOT match its expected-errors file: deal with the "
                                "unexpected/missing errors listed in that JSON FIRST, before any other work.\n")
        # MOTOR LIMITS ON at cycle start, verified by readback (user 2026-09-23). A start that cannot be verified
        # stops the runner: a cycle must never run with unknown controller limits.
        ok, why = motor_limits_hook("start", n, a, bench, runner_log, status_text)
        if not ok:
            reason = "motor limits could not be SET and verified at the start of cycle %d (%s) - no cycle runs " \
                     "with unverified controller limits" % (n, why)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        # STEER (user 2026-09-24, card chat-D): the newest open steer/1 from a repeated outcome verdict rides in the
        # cycle card; the session follows it or refuses it with evidence in next.json `steer` (read after the cycle).
        steer_path, steer_card = protocol.active_steer(os.path.join(bench, "cards"), os.path.join(bench, "steer_state.json"))
        if steer_card:
            log_line(runner_log, "STEER | %s | cycle %d carries %s (%s)" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                                          protocol._rel(steer_path), steer_card["item"]))
            this_prompt += ("\n\nSTEER (outcome-review steering card, user 2026-09-24): %s - item `%s`.\nREQUIRED ACT: %s\n"
                            "Goal ids: %s. Follow it (next.json `steer`: {\"item\": \"%s\", \"response\": \"follow\"}) or "
                            "refuse it with evidence ({\"item\": ..., \"response\": \"refuse\", \"evidence\": [\"file:line\", "
                            "...]}). No answer counts as a refusal; two refusals stop the runner and go to the user.\n"
                            % (protocol._rel(steer_path), steer_card["item"], steer_card["required_act"],
                               ", ".join(steer_card["goal_ids"]), steer_card["item"]))
        # C1: the cycle card. An invalid card is not dispatched (docs/session-protocol.md, common rule 5).
        card_path, card_why = write_cycle_card(bench, n, status_text, model, effort, ff_recipe, why, a, el_card,
                                               steer_path if steer_card else None, j_note)
        if not card_path:
            reason = "the cycle/1 card for cycle %d did not validate (%s) - no cycle is dispatched without one" \
                     % (n, card_why)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        log_line(runner_log, "CYCLE-CARD | %s | cycle %d | wrote %s (cycle/1 valid; next.json before: %s)"
                 % (time.strftime("%Y-%m-%d %H:%M:%S"), n, protocol._rel(card_path), next_md5_before[:12]))
        this_prompt = "CARD %s\n\n" % protocol._rel(card_path).replace("\\", "/") + this_prompt
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
        # A DRY RUN NEVER COMMITS (2026-09-24, card chat-B3): the self-tests run this runner with --dry-run/--dry-cmd on
        # a temp bench, and git_commit_cycle's `git add -A` on ROOT turned 16 self-test cycles into 16 "Cycle N runner
        # auto-commit" commits of the real working tree (b0f2ced..6d9f980).
        if a.dry_run or a.dry_cmd:
            log_line(runner_log, "GIT | cycle %d | skipped (dry run)" % n)
        else:
            git_commit_cycle(n, runner_log)
        # MOTOR LIMITS OFF at cycle end, verified by readback (user 2026-09-23). Runs whatever the session's exit
        # was; a release that cannot be verified stops the runner and is written into STATUS, because limits left
        # ON silently are exactly what happened between 2026-09-18 and 2026-09-23.
        ok_end, why_end = motor_limits_hook("end", n, a, bench, runner_log, read(status_path))
        # LabVIEW CLOSED AND VERIFIED GONE at every cycle end, after the motor end hook and whatever it returned (the
        # camera must not keep acquiring - user 2026-09-24). Its failure stops the runner below.
        ok_lv, why_lv = labview_close_hook(n, a, bench, runner_log, read(status_path))
        cost =("$%.4f" % env["total_cost_usd"]) if isinstance(env, dict) and isinstance(
            env.get("total_cost_usd"), (int, float)) else "?"
        # HEARTBEAT at cycle end (card chat-H1): after motor end + LabVIEW close, before any stop decision below
        hb.cycle_end(n, rc, cost)
        if not ok_end:
            reason = "motor limits could not be RELEASED and verified at the end of cycle %d (%s) - the " \
                     "controllers may still carry the session limits; check them before any experiment" % (n, why_end)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        if not ok_lv:
            reason = "LabVIEW could not be closed and verified gone at the end of cycle %d (%s) - the camera may " \
                     "still be acquiring; close LabVIEW by hand" % (n, why_lv)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        status_after = read(status_path)
        # C7: the machine NEXT. Absent / invalid / byte-identical all count as "unchanged" for stop condition 3.
        next_md5_after, next_card, next_why = next_json_reading(bench)
        next_moved = next_card is not None and next_md5_after != next_md5_before
        log_line(runner_log, "NEXT | %s | cycle %d | next.json %s | %s"
                 % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                    ("absent" if next_md5_after == "absent" else
                     "INVALID (%s)" % next_why if next_card is None else
                     ("read, CHANGED" if next_moved else "read, UNCHANGED") + " md5 " + next_md5_after[:12]),
                    ("act: %s | %s: %s" % (next_card["act"][:120],
                                           "advances" if next_card.get("advances") else "unblocks",
                                           next_card.get("advances") or next_card.get("unblocks"))
                     if next_card else "-")))
        log_line(runner_log, "CYCLE %d | %s | %s | exit %d | %s | %s"
                 % (n, start, end, rc, cost,
                    ("next.json: " + next_card["act"][:150]) if next_card else next_last_line(status_after)))
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

        # JUDGEMENT LADDER step (card chat-M1), from files only: next.json moved?, retrospective slugs, delivery.
        t_now = time.time()
        delivered = delivered_in_window(os.path.join(bench, "cards"), t0, t_now, goal_done_before, a.goalmap)
        slugs = retro_slugs_in_window(a.peer_dir, t0, t_now)
        new_level, j_why, j_stop = judge_ladder_step(j_level, next_moved, slugs, delivered)
        log_line(runner_log, "JUDGE-LADDER | %s | cycle %d end | level %d -> %d | %s"
                 % (time.strftime("%Y-%m-%d %H:%M:%S"), n, j_level, new_level, j_why[:200]))
        if j_stop:
            blocks = list((next_card or {}).get("advances") or []) if next_card else []
            did, derr = add_judge_decision(n, j_why, blocks, os.path.join(bench, "decisions_pending.json"))
            judge_state_save(bench, 0, "reset after RUNNER STOP in cycle %d (%s)" % (n, j_why), n)
            reason = ("the judgement ladder is exhausted: %s - the user's decision is requested (%s)"
                      % (j_why, ("decisions_pending " + did) if did else ("decisions_pending NOT written: %s" % derr)))
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        judge_state_save(bench, new_level, j_why, n)

        if steer_card:
            s_act, s_detail = protocol.steer_after_cycle(steer_path, steer_card, next_card, n,
                                                         os.path.join(bench, "steer_state.json"))
            log_line(runner_log, "STEER | %s | cycle %d | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                                      s_act.upper(), s_detail))
            if s_act == "stop":
                st = protocol._json_load(os.path.join(bench, "steer_state.json"), {}).get("items", {})
                refusals = (st.get(steer_card["item"]) or {}).get("refusals", [])
                did, derr = protocol.add_steer_decision(steer_card, n, refusals,
                                                        os.path.join(bench, "decisions_pending.json"))
                reason = ("the steering card %s (%s) was refused twice - the user's decision is requested (%s)"
                          % (protocol._rel(steer_path), steer_card["item"],
                             ("decisions_pending " + did) if did else ("decisions_pending NOT written: %s" % derr)))
                log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
                note_in_status(status_path, reason)
                return 3
        if next_card is not None and next_card.get("stop_requested"):
            reason = "next.json (cycle %d) sets stop_requested: %s" % (n, next_card.get("note") or next_card["act"][:150])
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 0
        bad_streak = bad_streak + 1 if rc != 0 else 0
        unchanged_streak = 0 if next_moved else unchanged_streak + 1
        if bad_streak >= 2:
            reason = ("the judgement session exited non-zero twice in a row (last exit %d, log %s) - a repeat "
                      "failure is a judgement matter, not something to retry" % (rc, os.path.basename(cyc_log)))
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        if unchanged_streak >= 2:
            reason = ("tools/bench/next.json was absent, invalid or byte-identical after two consecutive cycles "
                      "(%d and %d) - the loop is not moving" % (n - 1, n))
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3


if __name__ == "__main__":
    sys.exit(main())
