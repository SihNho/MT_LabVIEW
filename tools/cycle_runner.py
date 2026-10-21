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
  3. REPLACED 2026-09-26 (card chat-M1b) by the JUDGEMENT LADDER: `tools/bench/next.json` (C7, next/1) absent,
     invalid or byte-identical after a cycle raises the ladder one level (x1 opus max, x2 fable low - user table
     2026-09-27, card chat-N4); the THIRD consecutive unchanged cycle is RUNNER STOP + a decisions_pending item. Exit 3. (Until
     2026-09-26 two unchanged cycles stopped the runner; until 2026-09-24 the comparison was STATUS.md's prose
     `## NEXT`.) `stop_requested: true` in next.json stops the runner with exit 0.
  4. `--cycles N` exhausted. Exit 0.
  (2026-09-24, card chat-D) also: LabVIEW not verified gone at cycle end (labview_close_hook), and a steer/1 card
  refused twice (protocol.steer_after_cycle -> a decisions_pending item). Exit 3.
  (2026-09-26, card chat-M1; rungs re-set 2026-09-27, card chat-N4) also: the JUDGEMENT LADDER (opus high ->
  opus max -> fable low, state in <bench>/judge_ladder.json) triggered again at fable/low -> a decisions_pending
  item. Exit 3.
  JUDGE A/B: OFF by default since 2026-09-27 (user table, card chat-N4: level 0 = Opus 5.5 high fixed); the flag
  --judge-ab on|auto keeps the parity experiment (odd medium, even high) available.
USAGE LIMIT (CLAUDE.md's protocol): a rate/usage-limit message in the session's output is NOT a failure - the
runner sleeps until the renewal time + 2 min and RERUNS THE SAME CYCLE from the beginning ("rerun, don't resume";
a cycle interrupted mid-run is void). The partial attempt is logged as a non-result.

PURPOSE FLOW (default since card chat-A1, user 2026-10-04; `--flow legacy` = the single-session cycle above): a cycle is
ONE PURPOSE - judgement session (CYCLE_ROLE=judgement, writes next.json = the purpose, dispatches no material card) ->
ASSIGNMENT session (claude-sonnet-5-5 high, CYCLE_ROLE=assign, tools/bench/assign/) -> PURPOSE_MET, or HANDBACK (decided by
tools/hooks/guard_assign.py: triggers a-d, 3 h / 60 USD caps, backstop) -> judgement on the hand-back -> next round or
close. Runner log lines ASSIGN | HANDBACK | HANDBACK-JUDGED | HANDBACK-LIMIT. Self-test tools/bench/selftest_assign_flow.py.

CLAUDE-GPT DISCUSSIONS (card chat-D2, user 2026-10-09 "둘 다 넣자"; tools/debate_loop.py): the due OUTCOME review is a
discussion (outcome_review.py = fallback when it errors; --outcome-by review = the old way), and a STUCK cycle
(HANDBACK-LIMIT, or the firefighter trigger) gets a discussion before the next cycle. Synchronous, deadline
--debate-max-min (40); result = a steer/1 card + decisions_pending items. Lines DEBATE-START | DEBATE | DEBATE-NO-DOC |
DEBATE-STEER | DEBATE-DECISION | DEBATE-DEADLINE | DEBATE-ERROR. Self-test tools/bench/selftest_runner_debate.py.

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


def spawn_env(extra=None):
    e = os.environ.copy()
    for k in ("CYCLE_ROLE", "ASSIGN_STATE", "ASSIGN_RESULT", "PURPOSE_PHASE", "HANDBACK_RECORD"):
        e.pop(k, None)              # card chat-A1: a role is set per spawned session, never inherited
    e.update(SPAWN_ENV_EXTRA)
    e.update(extra or {})
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
# `BGRUN TIMEOUT` in TWO CONSECUTIVE cycles, the NEXT cycle runs with the firefighter model instead of the base
# judgement model - a whole cycle, so it can execute, not only advise. Exactly ONE firefighter cycle per trigger; if
# the same recipe still fails in that cycle the runner STOPS and hands it to the user (never a second firefighter).
# USER TABLE 2026-09-27 (card chat-N4, "테이블대로 적용해서 차기 싸이클 부터는 변경된걸로 돌리자"): the firefighter is ONE
# Opus 5.5 MAX cycle, then STOP (was fable low -> fable medium -> STOP since 2026-09-18; weekly Fable at 75 %).
FF_MODEL, FF_EFFORT = "claude-opus-5-5", "max"
FF_LADDER = ("max",)              # one rung: an Opus max cycle, then ask the user
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
FF_PROMPT = ("\n\n## FIREFIGHTER CYCLE (runner-triggered, model Opus 5.5 max, one rung)\n"
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
# a session's own feeling. Level 0 = --model/--effort (opus 5.5 HIGH fixed since 2026-09-27; A/B below, default off);
# +1 after a cycle whose next.json came out UNCHANGED, or whose retrospective (archived in that cycle) names a
# judgement-quality VIOLATION slug; a cycle that DELIVERS (a PASS result card with artefacts, or a goalmap milestone
# newly `done`) resets to 0. A trigger at the TOP level is RUNNER STOP + a decisions_pending item.
# USER TABLE 2026-09-27 (card chat-N4): 0 opus high -> 1 opus MAX -> 2 fable low -> STOP (was opus medium -> opus high
# -> fable low -> fable medium). Data: judge A/B cycles 89-97 (high PASS 2.5 vs 2.0, $33 vs $39); cycle 87 fable/low
# judgement produced nothing in 6 min - so fable is the last rung, not the default.
# The recipe FIREFIGHTER (one Opus max cycle) maps onto rank 1 of the same scale and the higher rank wins, so the two
# never stack above rank 2 = fable/low.
JUDGE_RANKS = [None, ("claude-opus-5-5", "max"), ("fable", "low")]   # rank 0 = --model/--effort
JUDGE_TOP = len(JUDGE_RANKS) - 1
JUDGE_SLUGS = ("inference-over-measurement", "wrong-ordering", "judgement-in-material")
FF_RANK = {"max": 1}
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
    """(rank, model, effort): the higher of the judgement-ladder level and the firefighter rung, capped at JUDGE_TOP."""
    rank = max(0, min(int(level), JUDGE_TOP))
    if ff_recipe:
        rank = max(rank, FF_RANK.get(FF_LADDER[min(ff_rung, len(FF_LADDER) - 1)], 1))
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
        return level, "level %d (%s/%s) triggered again: %s" % (level, JUDGE_RANKS[JUDGE_TOP][0], JUDGE_RANKS[JUDGE_TOP][1],
                                                               "; ".join(trig)), True
    return level + 1, "+1: %s" % "; ".join(trig), False


def retro_files_in_window(peer_dir, t_start, t_end):
    """card chat-P1 2b: the retrospective archives CREATED inside the window (same stamp rule as retro_slugs_in_window)."""
    out = []
    try:
        names = os.listdir(peer_dir)
    except OSError:
        return out
    for fn in names:
        if "retrospective" in fn and fn.endswith(".md"):
            try:
                st = os.stat(os.path.join(peer_dir, fn))
            except OSError:
                continue
            if t_start <= min(st.st_ctime, st.st_mtime) <= t_end:
                out.append(fn)
    return sorted(out)


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
    """One open decisions-pending/1 item for a judgement ladder exhausted at its top rung. (id, None) | (None, why)."""
    q = ("Judgement ladder exhausted in cycle %d (opus high -> opus max -> fable low): %s. "
         "How should the work continue?" % (n, reason))
    return protocol.add_decision(q, ["re-plan the current item", "restart the ladder at level 0", "discuss"],
                                 "cycle %d" % n, blocks, path=path)       # card chat-D2: one writer of decision items


LAST_FAIL_LOGS = {}     # key -> log path of the run that produced it, for the most recent failed_recipes() call


def command_identity(cmd):
    """The SCRIPT identity of a bgrun command: every `.py` path in it, basename, `_vN` stripped, lower-cased, joined
    by `+` (so `py -u tools/stage_prerun.py --prerun tools/recipes/stage_d1_l2a1.py --graph x.json` and the same
    command without `--graph` are ONE recipe). Empty string when the command names no script."""
    parts = []
    for tok in re.findall(r"[\w.\\/\-]+\.py\b", cmd or "", re.I):
        base = re.sub(r"_v\d+(?=\.py$)", "", os.path.basename(tok.replace("\\", "/")).lower())
        parts.append(base)
    return "+".join(parts)


def newest_run_passed(bench, identity, since_mtime, skip_names=()):
    """True when the NEWEST bgrun run of `identity` (any log in bench with mtime >= since_mtime, by START time then
    mtime) ended rc=0 without a failed RESULT line. retrospective-cycle88 `device-failed` (threshold 1): cycle 87's
    firefighter fired on `gate:x1 dry run ...` although `prerun_l2a1_86-5b.log:213` had already PASSED 8/0 - the
    trigger read failures without asking whether a later run of the same recipe passed. In flight / no END = not
    passed (the failure stands until a finished run clears it)."""
    best = None      # ((start_ts, mtime), verdict)
    try:
        names = os.listdir(bench)
    except OSError:
        return False
    for fn in names:
        if not fn.endswith(".log") or fn.startswith(("cycle_", "peer_", "priorart_", "retro")) or fn in skip_names:
            continue
        p = os.path.join(bench, fn)
        try:
            mt = os.path.getmtime(p)
        except OSError:
            continue
        if mt < since_mtime:
            continue
        ts, cmd, seg = protocol.last_segment(read(p))
        if not cmd or command_identity(cmd) != identity:
            continue
        key = (ts or 0.0, mt)
        if best is None or key > best[0]:
            best = (key, protocol.run_verdict(seg))
    if best is None:
        return False
    v = best[1]
    return v["source"] != "none" and not v["failed"]


def failed_recipes(bench, t_start, t_end):
    """Recipe basenames whose bgrun log (mtime inside [t_start, t_end]) ended rc!=0 or TIMEOUT - unless the NEWEST
    run of the same recipe (command identity) passed, in which case the recipe is CLEARED (2026-09-26)."""
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
        # NEWEST RUN WINS (2026-09-26, retrospective-cycle88 device-failed): a later run of the same recipe that
        # PASSED clears this failure - no recipe key and no gate key are taken from a superseded failing run.
        ident = command_identity(m.group(1))
        if ident and newest_run_passed(bench, ident, mt):
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
        # chat 2026-10-09: a stale .git/index.lock (left by a killed git, seen 10-08 18:34 and 10-09 10:08) made the
        # cycle 149/150 commits fail silently (rc 128). Remove it only when it is older than 10 min and no git runs.
        # chat 2026-10-10: the "no git.exe" condition never held (the Claude app runs git every few seconds), so a lock
        # from 10-09 23:18 blocked the commits of cycles 160-164. A lock older than 30 min is removed regardless.
        lock = os.path.join(ROOT, ".git", "index.lock")
        if os.path.exists(lock) and time.time() - os.path.getmtime(lock) > 600:
            tl = subprocess.run(["tasklist", "/FI", "IMAGENAME eq git.exe"], capture_output=True, text=True, timeout=30)
            if "git.exe" not in (tl.stdout or "") or time.time() - os.path.getmtime(lock) > 1800:
                os.remove(lock)
                log_line(runner_log, "GIT | %s | cycle %d | removed stale .git/index.lock" % (time.strftime("%Y-%m-%d %H:%M:%S"), n))
        subprocess.run(["git", "add", "-A"], cwd=ROOT, timeout=120, capture_output=True)
        msg = "Cycle %d: session outputs (runner auto-commit)\n\nCo-Authored-By: Claude Fable 5.1 <noreply@anthropic.com>" % n
        r = subprocess.run(["git", "commit", "-q", "-m", msg], cwd=ROOT, timeout=120, capture_output=True, text=True)
        log_line(runner_log, "GIT | %s | cycle %d | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                          "committed" if r.returncode == 0 else "nothing to commit / rc=%d" % r.returncode))
    except Exception as e:  # noqa
        log_line(runner_log, "GIT | cycle %d | commit failed: %s" % (n, e))


CAP_SUMMARY_RE = re.compile(r"^CAPABILITIES-SUMMARY (\w+) \| (.+)$", re.M)


def capabilities_hook(n, runner_log, doc=None, timeout=300, gen=None):
    """Card chat-T7 item 6(c) (user 2026-10-09 "전부 적용"): at every cycle end, BEFORE the git commit, regenerate the function table +
    list of docs/toolkit-capabilities.md (`py tools/gen_capabilities.py --summary`) and its drift (`--check`), and log ONE line
    `CAPABILITIES | <time> | cycle N | regenerated <counts> | drift <line or none>`. A failure is logged and never stops the runner.
    `doc` / `gen` = another doc / generator (self-tests). Returns the logged line. Self-test: tools/bench/selftest_t7_capabilities.py."""
    gen = gen or os.path.join(HERE, "gen_capabilities.py")
    extra = ["--doc", doc] if doc else []
    try:
        p = subprocess.run([sys.executable, gen, "--summary"] + extra, cwd=ROOT, timeout=timeout, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        m = CAP_SUMMARY_RE.search(p.stdout or "")
        reg = ("%s %s" % (m.group(1), m.group(2))) if m and p.returncode == 0 else "FAILED rc=%d %s" % (
            p.returncode, ((p.stderr or p.stdout or "").strip().splitlines() or [""])[-1][:160])
        c = subprocess.run([sys.executable, gen, "--check"] + extra, cwd=ROOT, timeout=timeout, capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        dm = re.search(r"^DRIFT: (.*)$", c.stdout or "", re.M)
        drift = dm.group(1)[:200] if dm else "unread rc=%d" % c.returncode
    except Exception as e:  # noqa: BLE001 - logged, never raised
        reg, drift = "FAILED %s: %s" % (type(e).__name__, str(e)[:160]), "not checked"
    line = "CAPABILITIES | %s | cycle %s | regenerated %s | drift %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), n, reg, drift)
    log_line(runner_log, line)
    return line


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


def retro_fallback(n, t_start, a, bench, runner_log):
    """card chat-P1 item 2b (user 2026-09-28): the session runs its retrospective only when tools/retro_due.py says it
    is DUE. After the session the runner re-checks: DUE and no retrospective archived in [t_start, now] -> the runner
    runs it itself, synchronously (the session is gone; same shape as land_retrospective). A dry run only logs.
    Returns a one-line note or None. Never raises."""
    try:
        import retro_due as RD
        due, reasons, _f = RD.check(n, os.path.join(bench, "cards"), a.peer_dir)
    except Exception as e:  # noqa: BLE001 - bookkeeping must never kill the runner
        log_line(runner_log, "RETRO-DUE | cycle %d | check raised %s: %s" % (n, type(e).__name__, str(e)[:160]))
        return None
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if not due:
        log_line(runner_log, "RETRO-DUE | %s | cycle %d | not due" % (stamp, n))
        return None
    got = retro_files_in_window(a.peer_dir, t_start, time.time() + 60)
    if got:
        log_line(runner_log, "RETRO-DUE | %s | cycle %d | due and archived in the cycle (%s)" % (stamp, n, got[-1]))
        return None
    if a.dry_run or a.dry_cmd:
        note = "RETRO-DUE | %s | cycle %d | DUE, none archived, not run (dry run): %s" % (stamp, n, "; ".join(reasons)[:160])
        log_line(runner_log, note)
        return note
    retro_log = os.path.join(bench, "retro.log")
    cmd = [sys.executable, BGRUN, "--max-min", "20", "--log", retro_log, "--",
           sys.executable, os.path.join(HERE, "retrospective.py"), "--cycle", str(n)]
    t0 = time.time()
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace")
        rc = proc.returncode
    except Exception as e:  # noqa: BLE001
        rc = "exc %s" % e
    note = ("RETRO-DUE | %s | cycle %d | DUE (%s) and the session archived none - the runner ran it: rc=%s after %.0f s"
            % (stamp, n, "; ".join(reasons)[:160], rc, time.time() - t0))
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
    Rig state unknown, or 실험중 at START: the ports are the user's - nothing is sent, the skip is logged, ok=True.
    The END also runs in 실험중 (item 9 + Q2, 2026-10-21: magnet to 0 mm, limits released).
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
    # the END runs in the experiment state too (user 2026-10-21 item 9 + Q2: an experiment declared mid-cycle still gets
    # the magnet back to 0 mm and the limits released - the rig at its initial condition); the start never does
    if state not in ("assembled", "disassembled") and not (phase == "end" and state == "experiment"):
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


def labview_close_hook(n, a, bench, runner_log, status_text, t0=None, root_pid=None):
    """User 2026-09-24 ("사이클 종료하고서는 제대로 LabVIEW 끄는것 잊지 말것, 특히 카메라가 계속 Acquisition 하면 기계에
    좋지 않으니"; CLAUDE.md 1b MOTOR GRANT): every cycle ends with ITS LabVIEW CLOSED and VERIFIED GONE.
    B4 (user 2026-10-21 "승인"; follow-up "V6 후속작업 실시" 2026-10-22): only the LabVIEW this cycle OWNS is closed -
    rig_session.close_labview / own_labview: created after the cycle began (`t0`, Windows FILETIME) AND COM-launched
    (`/Automation`) or a live descendant of `root_pid` (the process holding the rig lock for the cycle). COM Quit only
    when every running LabVIEW is ours, else taskkill /F by pid (nothing is ever saved); then tasklist. Any other
    LabVIEW may be a user's: it is left running and the verdict is INCOMPLETE (ok False) - the caller keeps the rig
    lock. The same in the experiment state (B3: our LabVIEW is closed, the user's never), so `status_text` no longer
    decides anything (kept for the callers). t0 None = nothing is provably ours -> a running LabVIEW is INCOMPLETE.
    Returns (ok, reason); reason starts with OK: / FAIL: / INCOMPLETE: (or 'skipped' under --dry-run/--dry-cmd/
    --no-labview-close)."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    if a.dry_run or a.dry_cmd or getattr(a, "no_labview_close", False):
        log_line(runner_log, "LABVIEW-CLOSE | %s | cycle %d | skipped (dry run / --no-labview-close)" % (stamp, n))
        return True, "skipped"
    sys.path.insert(0, HERE)
    import rig_session
    if t0 is None:
        t0 = rig_session._filetime_now()          # nothing started after "now" -> nothing is provably this cycle's
    return rig_session.close_labview(runner_log, t0, None, root_pid, who="cycle %d" % n)


def bgrun_reap_hook(n, bench, runner_log):
    """Card 92-4 (retrospective-cycle90 `device-failed`, threshold 1): at every cycle end, close the record of any
    bgrun in `bench` that an OUTSIDE tree kill took down (START + `BGRUN PID`, no END/TIMEOUT, pid gone) by
    appending `BGRUN KILLED (external)` through tools/bgrun_reap.py. Touches no live pid and no LabVIEW. Never
    stops the runner: its outcome is one `BGRUN-REAP |` line. Returns the reap dict (or None on failure)."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    try:
        import bgrun_reap
        r = bgrun_reap.reap(bench=bench, who="cycle_runner cycle %d" % n,
                            exclude=[os.environ.get("BGRUN_LOG", "")] if os.environ.get("BGRUN_LOG") else ())
    except Exception as e:  # noqa: BLE001
        log_line(runner_log, "BGRUN-REAP | %s | cycle %d | FAILED: %s: %s" % (stamp, n, type(e).__name__, str(e)[:200]))
        return None
    log_line(runner_log, "BGRUN-REAP | %s | cycle %d | scanned %d, marked KILLED %s, live %d, undecidable %d, pids %s"
             % (stamp, n, r["scanned"],
                [("%s pid=%d" % (os.path.basename(p), pid)) for p, pid in r["marked"]] or "none",
                len(r["open_live"]), len(r["undecidable"]), r["pids"]))
    return r


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


# GATES DUE AT CYCLE START (card 108-5; docs/violation-decisions.md device-failed 2026-09-27 08:30, after
# archive/peer/2026-09-27-retrospective-cycle107.md:292 - the 2026-09-26 14:10 wrong-ordering device "check every due
# gate before the first dispatch" was decided and never built, so cycle 107 dispatched cards into gates they tripped).
# Every guard_cycle "due" check runs HERE, before the judgement session spawns, and the list rides in the cycle card
# (`gates_due`). A due OUTCOME review is RUN here (bgrun, like errorlist_hook), not left for a card to trip over.
# What is checked, and where the rule lives (read, not re-decided):
#   violations   `tools/violations.py --due` rc 1                             (guard_cycle.py:555-561)
#   outcome      outcome_review.is_due() on --peer-dir                         (guard_cycle.py:566-575, outcome_review.py:106)
#   retro-debt   guard_cycle's retrospective budget, recomputed from its own functions/constants (guard_cycle.py:638-670)
#   gate-fp      tools/gate_fp.py due(): >= 5 open false positives, the oldest >= 3 cycles, or one blocking a card (chat-P1)
#   recipe:<f>   for each tools/recipes/*.py named in next.json `act`: stop_record.check_command, guard_cycle.premature_build
#                (prior-art), stage_prerun.check_launch (recorded dry + prerun PASS for the current sha)
OUTCOME_MAX_MIN = 20                    # outcome_review.py waits up to 900 s on peer.ps1
ACT_RECIPE_RE = re.compile(r"(?:tools[\\/]recipes[\\/])?\b([A-Za-z][\w-]*\.py)\b")


def _hooks_dir_import(name):
    p = os.path.join(HERE, "hooks")
    if p not in sys.path:
        sys.path.append(p)
    return __import__(name)


def _outcome_due(peer_dir):
    """(due, why) - outcome_review.is_due() with its PEER pointed at `peer_dir` (the runner's --peer-dir)."""
    import outcome_review as OR
    old = OR.PEER
    OR.PEER = peer_dir
    try:
        return OR.is_due()
    finally:
        OR.PEER = old


def _retro_debt():
    """(due, detail) - guard_cycle.main's LAST block (guard_cycle.py:638-670), from guard_cycle's own functions."""
    GC = _hooks_dir_import("guard_cycle")
    log, retro = GC.newest_build_log(), GC.newest_retrospective()
    since = [p for p in GC.glob.glob(os.path.join(GC.BENCH, "*.log"))
             if GC.logclass.is_recipe_build_log(p) and (retro is None or os.path.getmtime(p) > retro[1])
             and time.time() - os.path.getmtime(p) <= GC.MAX_AGE_S]
    if retro is None:
        hours = 999.0
    elif len(since) >= 2:
        ts = [os.path.getmtime(p) for p in since]
        hours = (max(ts) - min(ts)) / 3600.0
    else:
        hours = 0.0
    overdue = len(since) >= GC.CYCLE_BUILD_BUDGET or hours >= GC.CYCLE_HOURS
    due = bool(log and (retro is None or (retro[1] < log[1] and overdue)))
    return due, "%d recipe build log(s) since %s, span %.1f h (budget %d / %.0f h)" % (
        len(since), os.path.basename(retro[0]) if retro else "no retrospective", hours, GC.CYCLE_BUILD_BUDGET,
        GC.CYCLE_HOURS)


def _recipe_state(name):
    """(due, detail) for tools/recipes/<name>: launch refusals that would meet a launch of it this cycle."""
    fp = os.path.join(ROOT, "tools", "recipes", name)
    cmd = "py tools/recipes/%s" % name
    why = []
    try:
        import stop_record
        ok, w = stop_record.check_command(cmd)
        if not ok:
            why.append("stop_record: " + " ".join(str(w).split())[:120])
    except Exception as e:  # noqa: BLE001
        why.append("stop_record error %s" % type(e).__name__)
    try:
        msg = _hooks_dir_import("guard_cycle").premature_build(cmd)
        if msg:
            why.append("prior-art: " + " ".join(str(msg).split())[:120])
    except Exception as e:  # noqa: BLE001
        why.append("prior-art error %s" % type(e).__name__)
    if os.path.basename(fp).startswith("stage_"):
        try:
            import stage_prerun
            ok, w = stage_prerun.check_launch(cmd)
            if not ok:
                why.append("launch gate: " + " ".join(str(w).split())[:120])
        except Exception as e:  # noqa: BLE001
            why.append("launch gate error %s" % type(e).__name__)
    return bool(why), ("; ".join(why) or "launch-ready (stop record, prior-art, dry+prerun records)")[:300]


def gates_due(bench, peer_dir, next_card):
    """[{gate, due, detail}] - every guard_cycle 'due' check, measured at cycle start. `due` None = the check errored.
    Never raises; each check is independent."""
    out = []

    def add(gate, fn):
        try:
            d, why = fn()
            out.append({"gate": gate[:80], "due": bool(d), "detail": str(why)[:300]})
        except Exception as e:  # noqa: BLE001 - one broken check must not hide the others
            out.append({"gate": gate[:80], "due": None, "detail": ("error %s: %s" % (type(e).__name__, e))[:300]})

    def viol():
        p = subprocess.run([sys.executable, os.path.join(HERE, "violations.py"), "--due"], cwd=ROOT, capture_output=True,
                           text=True, encoding="utf-8", errors="replace", timeout=120)
        lines = [ln.strip() for ln in (p.stdout or "").splitlines() if ln.startswith("DUE ")]
        return p.returncode == 1 and bool((p.stdout or "").strip()), (" | ".join(lines) or "rc %d, none due" % p.returncode)
    add("violations", viol)
    add("outcome", lambda: _outcome_due(peer_dir))
    add("retro-debt", _retro_debt)

    def gate_fp_due():
        # card chat-P1 item 3: the batched gate false positives - DUE at >= 5 open, oldest >= 3 cycles, or one blocking a
        # card; the prompt then asks for ONE tooling card that drains the queue (tools/gate_fp.py drain per entry)
        import gate_fp
        cd = os.path.join(bench, "cards")
        return gate_fp.due(cards_dir=cd, cycle=protocol.current_cycle(cd))
    add("gate-fp", gate_fp_due)
    act = (next_card or {}).get("act") or ""
    seen = []
    for m in ACT_RECIPE_RE.finditer(act):
        nm = m.group(1)
        if nm not in seen and os.path.isfile(os.path.join(ROOT, "tools", "recipes", nm)):
            seen.append(nm)
    for nm in seen[:6]:
        add("recipe:" + nm, lambda nm=nm: _recipe_state(nm))
    return out


# RETRO-UNDISPOSED (card 147-a1-5; docs/violation-decisions.md:1935-1947, decision 2026-10-08 01:16). guard_peer.py:1181-1195
# refuses a retrospective launch while the newest archived retrospective's disposition is the placeholder, but it is a
# PreToolUse hook and the runner's own child-process launch (retrospective_hook, :633-637) never meets it. The SAME test,
# COPIED (not imported: guard_peer pulls logclass/gateclass/protocol at import) from guard_peer.py:834-855: newest
# `*retrospective*.md` in the peer dir BY MTIME; undisposed = no '## What was done with it' heading, or < 80 characters left
# after the placeholder lines are removed. ADVISORY: it adds a gates_due entry and a log line, never refuses or stops.
RETRO_DISPOSITION_H = "## What was done with it"                                            # guard_peer.py:834
RETRO_PLACEHOLDER_RE = re.compile(r"^\s*\(?\s*claude fills in\s*\)?\s*$", re.I | re.M)      # guard_peer.py:835


def retro_undisposed(peer_dir):
    """Path of the newest archived retrospective whose disposition is missing, empty or still the placeholder, else None
    (guard_peer.undisposed('retrospective'), guard_peer.py:838-855, with PEER = `peer_dir`)."""
    try:
        files = [os.path.join(peer_dir, fn) for fn in os.listdir(peer_dir)
                 if "retrospective" in fn.lower() and fn.lower().endswith(".md")]   # = glob '*retrospective*.md' on Windows
    except OSError:
        return None
    if not files:
        return None
    newest = max(files, key=os.path.getmtime)
    try:
        with open(newest, encoding="utf-8", errors="replace") as f:
            body = f.read()
    except OSError:
        return None
    import dispo   # card 150-a3-3: the LAST column-0 RETRO_DISPOSITION_H line, same RETRO_PLACEHOLDER_RE (tools/dispo.py)
    left = dispo.disposition_len(body)
    # None = no heading line (an inline quote of the heading is not one); < 80 = empty or still the placeholder
    if left is None or left < 80:
        return newest
    return None


def retro_undisposed_item(n, peer_dir, runner_log):
    """The `retro-undisposed` gates_due item ({gate, due: True, detail}) when retro_undisposed() names a file, else None;
    logs `RETRO-UNDISPOSED <path>`. Never raises: an error becomes one log line and None."""
    try:
        p = retro_undisposed(peer_dir)
        if not p:
            return None
        rel = protocol._rel(p)
        log_line(runner_log, "RETRO-UNDISPOSED %s | %s | cycle %d | guard_peer.py:1181-1195 will refuse the next "
                 "retrospective launch until its '## What was done with it' is written" % (
                     rel, time.strftime("%Y-%m-%d %H:%M:%S"), n))
        return {"gate": "retro-undisposed", "due": True,
                "detail": ("%s: '## What was done with it' is missing or still the placeholder - write the disposition "
                           "before the cycle's retrospective is launched (guard_peer.py:1181-1195)" % rel)[:300]}
    except Exception as e:  # noqa: BLE001 - advisory only: never stop the runner
        log_line(runner_log, "RETRO-UNDISPOSED-CHECK error %s: %s" % (type(e).__name__, str(e)[:160]))
        return None


# CLAUDE-GPT DISCUSSIONS IN THE LOOP (card chat-D2, user 2026-10-09 "둘 다 넣자"): (1) the due OUTCOME review is a
# discussion (outcome_review.py is the fallback when it errors); (2) a STUCK cycle (HANDBACK-LIMIT, or the firefighter
# trigger) gets a discussion before the next cycle. Both write a steer/1 card from the agreed items and one
# decisions_pending item per user question (tools/debate_loop.py apply). Synchronous, deadline --debate-max-min.
def first_fail_line(path):
    """`<log name>: <first failing line>` of a failed bgrun log (GATE_FAIL_RE, else the BGRUN END/TIMEOUT line)."""
    txt = read(path)
    m = GATE_FAIL_RE.search(txt) or BGRUN_FAIL_RE.search(txt)
    line = (m.group(0) if m else "(no failing line found)").strip()
    return "%s: %s" % (os.path.basename(path), line[:200])


def debate_hook(kind, n, a, bench, runner_log, why="", fail_lines=()):
    """Run ONE discussion of `kind` ('outcome' | 'stuck') before cycle n and apply its result. Dry runs dispatch it
    only with --debate-stub (self-tests). -> the debate_loop result dict (+ 'applied'), or None when not dispatched.
    Never raises."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    stub = getattr(a, "debate_stub", False)        # getattr: self-tests build `a` by hand (selftest_cycle_runner_retro)
    if (getattr(a, "dry_run", False) or getattr(a, "dry_cmd", "")) and not stub:
        log_line(runner_log, "DEBATE | %s | cycle %d | %s | not dispatched (dry run) | %s" % (stamp, n, kind, why[:160]))
        return None
    try:
        import debate_loop as DL
        if kind == "outcome":
            topic = DL.outcome_topic(n, bench, runner_log, a.peer_dir, a.goalmap, a.status)
        else:
            topic = DL.stuck_topic(n, why, bench, runner_log, a.status, fail_lines)
        res = DL.run_discussion(kind, n, topic, bench, lambda s: log_line(runner_log, s),
                                max_min=getattr(a, "debate_max_min", DL.DEADLINE_MIN),
                                max_rounds=getattr(a, "debate_max_rounds", DL.MAX_ROUNDS), stub=stub,
                                stub_secs=getattr(a, "debate_stub_secs", 0.0), doc=getattr(a, "debate_doc", "google"))
        res["applied"] = DL.apply(res, kind, n, bench, a.goalmap, a.peer_dir, lambda s: log_line(runner_log, s))
        return res
    except Exception as e:  # noqa: BLE001 - a discussion must never stop the runner
        log_line(runner_log, "DEBATE-ERROR | %s | cycle %d | %s | %s: %s" % (stamp, n, kind, type(e).__name__,
                                                                           str(e)[:200]))
        return {"ok": False, "why": "%s: %s" % (type(e).__name__, e), "line": None}


def gates_due_hook(n, a, bench, runner_log, defer=None, out=None):
    """Cycle start: gates_due(), then a DUE outcome review is RUN before the session spawns - as a Claude-GPT
    discussion (card chat-D2; --outcome-by review = the old single-model review), falling back to outcome_review.py
    when the discussion errors (not in dry runs unless the self-test names a stand-in with --outcome-cmd), then the
    outcome check is re-read. `defer`: a reason the due review waits one cycle (a stuck discussion already ran in this
    gap). Returns the items for the card; `out` (a dict, optional) receives out['debate'] = the discussion result or
    None. Never stops the runner."""
    stamp = time.strftime("%Y-%m-%d %H:%M:%S")
    _m, card, _w = next_json_reading(bench)
    items = gates_due(bench, a.peer_dir, card)
    oc = next((x for x in items if x["gate"] == "outcome"), None)
    dres = None
    if oc and oc["due"] and defer:
        oc["detail"] = ("DUE, deferred one cycle (%s): %s" % (defer, oc["detail"]))[:300]
        log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | DUE, deferred one cycle: %s" % (stamp, n, defer))
    elif oc and oc["due"] and getattr(a, "outcome_by", "debate") == "debate":
        dres = debate_hook("outcome", n, a, bench, runner_log, oc["detail"])
        if dres and dres.get("ok"):
            try:
                still, why = _outcome_due(a.peer_dir)
            except Exception as e:  # noqa: BLE001
                still, why = None, "re-check error %s" % type(e).__name__
            oc["due"] = still
            oc["detail"] = ("DISCUSSED before the session (%s); now: %s" % (dres.get("slug"), why))[:300]
            log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | discussion %s | still due: %s | %s"
                     % (time.strftime("%Y-%m-%d %H:%M:%S"), n, dres.get("slug"), still, why[:160]))
        elif dres is not None:
            log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | the discussion did not complete (%s) - fallback "
                                 "outcome_review.py" % (time.strftime("%Y-%m-%d %H:%M:%S"), n, dres.get("why")))
    if oc and oc["due"] and not defer and not (dres and dres.get("ok")):
        stand_in = getattr(a, "outcome_cmd", "")
        if (a.dry_run or a.dry_cmd) and not stand_in:
            oc["detail"] = ("DUE, not dispatched (dry run): " + oc["detail"])[:300]
            log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | DUE, not dispatched (dry run) | %s"
                     % (stamp, n, oc["detail"][:160]))
        else:
            log = os.path.join(bench, "outcome_review_cycle%d.log" % n)
            inner = stand_in.split() if stand_in else [sys.executable, "-u", os.path.join(HERE, "outcome_review.py")]
            cmd = [sys.executable, BGRUN, "--max-min", str(OUTCOME_MAX_MIN), "--log", log, "--"] + inner
            log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | DUE (%s) - running before the session | %s"
                     % (stamp, n, oc["detail"][:120], protocol._rel(log)))
            try:
                proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, encoding="utf-8", errors="replace",
                                      env=dict(os.environ, MATERIAL="1"))
                rc = proc.returncode
            except Exception as e:  # noqa: BLE001
                rc = "raised %s" % type(e).__name__
            try:
                still, why = _outcome_due(a.peer_dir)
            except Exception as e:  # noqa: BLE001
                still, why = None, "re-check error %s" % type(e).__name__
            oc["due"] = still
            oc["detail"] = ("RAN before the session (rc %s, %s); now: %s" % (rc, protocol._rel(log), why))[:300]
            log_line(runner_log, "OUTCOME-REVIEW | %s | cycle %d | ran rc %s | still due: %s | %s"
                     % (time.strftime("%Y-%m-%d %H:%M:%S"), n, rc, still, why[:160]))
    ru = retro_undisposed_item(n, a.peer_dir, runner_log)          # card 147-a1-5, advisory
    if ru:
        items.append(ru)
    log_line(runner_log, "GATES-DUE | %s | cycle %d | %s" % (
        time.strftime("%Y-%m-%d %H:%M:%S"), n,
        "; ".join("%s=%s" % (x["gate"], {True: "DUE", False: "ok", None: "ERROR"}[x["due"]]) for x in items)))
    if out is not None:
        out["debate"] = dres
    return items


def write_cycle_card(bench, n, status_text, model, effort, ff_recipe, motor_verdict, a, errorlist=None, steer=None,
                     note=None, gates=None):
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
    if gates is not None:
        card["gates_due"] = list(gates)[:20]
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
        self.debate = None      # card chat-D2: the last DEBATE line of this run (doc link) - reaches the 30-min report

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
        if self.debate:         # card chat-D2: the discussion's doc link reaches the user through this report
            rows.append(("Claude-GPT 토론 (문서 링크)", self.debate))
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


# ------------------------------------------------------------------------------------------------ the session rerun loop
def run_session(a, cmd, log, env, n, status_path, runner_log, tag):
    """ONE session under bgrun, with the usage-limit / API-5xx rerun rule (CLAUDE.md usage-limit protocol: rerun, don't
    resume). Shared by every session of a cycle since card chat-A1; `tag` prefixes its log lines ("CYCLE 7" keeps the
    pre-chat-A1 text). -> (rc, fresh output, start stamp, end stamp, start epoch of the last attempt)."""
    rc, fresh, start, end, t0 = 0, "", "", "", time.time()
    for attempt in range(1, LIMIT_RETRIES + 1):
        start = time.strftime("%Y-%m-%d %H:%M:%S")
        t0 = time.time()
        before = len(read(log))
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True,
                              encoding="utf-8", errors="replace", env=env)
        end = time.strftime("%Y-%m-%d %H:%M:%S")
        rc = proc.returncode
        fresh = read(log)[before:] or (proc.stdout or "")
        wait = limit_wait_s(fresh)
        # TRANSIENT API 5xx (2026-09-22 09:58: two sessions in a row died on "API Error: 500 Internal server
        # error", the second after 5 s with 0 tokens, and the runner stopped on "non-zero twice"). A server-side
        # 5xx is not a judgement matter: wait 5 min and RERUN the cycle, like the usage-limit path.
        if wait is None and rc != 0 and re.search(r"API Error: 5\d\d", fresh):
            wait = 300.0
        if wait is None or attempt == LIMIT_RETRIES:
            break
        # A STOP MARKER BEATS THE RERUN (2026-10-02 23:50: cycle 141 slept to rerun although usage_stop_watch had
        # written the user's weekly-90 % STOP at 23:04 - and the chat could not kill the sleeping runner). Checked
        # before the sleep and again after it; the cycle then ends normally (end hooks below still run).
        if stop_marker(read(status_path)):
            log_line(runner_log, "%s | %s | %s | usage-limit attempt %d: rerun SKIPPED - STATUS carries a "
                                 "STOP marker" % (tag, start, end, attempt))
            break
        # RERUN, DON'T RESUME (CLAUDE.md's usage-limit protocol): the partial attempt is a non-result.
        log_line(runner_log, "%s | %s | %s | usage-limit attempt %d, non-result; sleeping %.0f min "
                             "(renewal + 2 min) then RERUNNING this cycle"
                 % (tag, start, end, attempt, wait / 60.0))
        if a.no_sleep:
            break
        time.sleep(wait)
        if stop_marker(read(status_path)):
            log_line(runner_log, "%s | %s | rerun SKIPPED after the wait - STATUS carries a STOP marker"
                     % (tag, time.strftime("%Y-%m-%d %H:%M:%S")))
            break
    return rc, fresh, start, end, t0


# ------------------------------------------------------------------------------------------------ PURPOSE FLOW
# Card chat-A1 (user 2026-10-04: "사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적
# 으로 쪼갤 것이 아니라 싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯" -> cloud bench
# tools/bench/assignbench/report_cloud.md -> "세션 규칙 설정은 그렇게 하고"). A cycle is ONE PURPOSE:
#   judgement (writes next.json = the purpose: act, pass, plan) -> ASSIGNMENT session (claude-sonnet-5-5 high, top-level
#   `claude -p`, CYCLE_ROLE=assign, dispatches task/1 cards) -> PURPOSE_MET, or HANDBACK -> judgement (HANDBACK <record>)
#   -> a revised next.json starts the next assignment round; an unchanged one closes the cycle -> retro_due /
#   retrospective, hooks, ladder, heartbeat as before.
# The hand-back is MECHANICAL (tools/hooks/guard_assign.py, called by the registered guard_session hook on every dispatch
# and by assignment_rounds() after the session): triggers a-d, cap 3 h / 60 USD (tools/bench/assign/assign_config.json,
# user-changeable), runaway backstop 30 cards. Hard last resorts: bgrun --max-min hard_minutes, claude --max-budget-usd
# hard_usd. Top-level, not a sub-agent of the judgement session: measured 2026-10-04 (Claude Code 2.1.281) that a
# sub-agent CAN dispatch sub-agents (docs: up to three layers), so the reason the brief gave is gone - it stays top-level
# for its own model/effort, its own process (cap, kill, cost envelope) and its own hook role.
ASSIGN_DIR = os.path.join(HERE, "bench", "assign")
ASSIGN_PROMPT_FILE = os.path.join(ASSIGN_DIR, "assign_prompt.md")
PURPOSE_ADDENDUM_FILE = os.path.join(ASSIGN_DIR, "purpose_addendum.md")
ASSIGN_AGENTS = ["material", "material-opus-max", "material-fable-low", "log-reader"]


def _guard_assign():
    p = os.path.join(HERE, "hooks")
    if p not in sys.path:
        sys.path.append(p)
    import guard_assign
    return guard_assign


def newest_assign_result(cards_dir):
    fs = [os.path.join(cards_dir, f) for f in _listdir(cards_dir) if f.startswith("assign_result_") and f.endswith(".json")]
    return max(fs, key=os.path.getmtime) if fs else None


def purpose_from_next(card):
    plan = card.get("plan") if isinstance(card.get("plan"), dict) else None
    return {"act": str(card.get("act") or "")[:200], "pass": [str(x)[:200] for x in card.get("pass") or []],
            "plan": ({"path": str(plan.get("path"))[:400], "md5": plan.get("md5")} if plan else None),
            "advances": [str(x) for x in card.get("advances") or []], "unblocks": card.get("unblocks"),
            "task_kind": card.get("task_kind"), "note": card.get("note")}


def write_assign_card(cards_dir, n, k, purpose, next_md5, cfg, state_path, result_path, handback_in):
    card = {"schema": "assign/1", "cycle": n, "round": k, "purpose": purpose, "next_md5": next_md5,
            "caps": {"minutes": float(cfg["cap_minutes"]), "usd": float(cfg["cap_usd"]),
                     "backstop_cards": int(cfg["backstop_cards"])},
            "state": protocol._rel(state_path).replace("\\", "/"), "result": protocol._rel(result_path).replace("\\", "/"),
            "handback_in": protocol._rel(handback_in).replace("\\", "/") if handback_in else None,
            "agents": ASSIGN_AGENTS}
    ok, why = protocol.validate_obj(card)
    if not ok:
        return None, why
    p = os.path.join(cards_dir, "assign_%d_%d.json" % (n, k))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False, indent=1)
    return p, None


def write_handback(cards_dir, n, k, trigger, detail, st_path, result_path, next_md5, usd, minutes):
    GA = _guard_assign()
    st = GA.state_load(st_path) or {}
    rec = {"schema": "handback/1", "cycle": n, "round": k, "trigger": trigger, "detail": str(detail)[:400] or "-",
           "cards": GA.card_rows(st)[:40],
           "assign_result": protocol._rel(result_path).replace("\\", "/") if os.path.exists(result_path) else None,
           "next_md5": next_md5, "cost_usd": usd, "minutes": round(minutes, 1)}
    ok, why = protocol.validate_obj(rec)
    if not ok:      # never lose a hand-back to a schema detail: record the reason in a minimal valid record
        rec = {"schema": "handback/1", "cycle": n, "round": k, "trigger": trigger,
               "detail": ("record did not validate (%s): %s" % (why, detail))[:400], "cards": []}
    p = os.path.join(cards_dir, "handback_%d_%d.json" % (n, k))
    with open(p, "w", encoding="utf-8") as f:
        json.dump(rec, f, ensure_ascii=False, indent=1)
    return p


def assign_cmd(a, cfg, prompt):
    """The assignment session's command (the bgrun-wrapped part), or None = skip (a dry run without a stand-in)."""
    if a.dry_run or a.dry_cmd:
        return a.assign_dry_cmd.split() if a.assign_dry_cmd else None
    return ["claude.exe", "-p", "--model", str(cfg["model"]), "--effort", str(cfg["effort"]),
            "--output-format", "json", "--permission-mode", a.permission_mode,
            "--max-budget-usd", "%.2f" % float(cfg["hard_usd"]), prompt]


def assignment_rounds(a, n, bench, runner_log, status_path, judge_prompt, model, effort, judge_rc, next_md5_cycle_start):
    """The purpose flow after the cycle's first judgement session. -> {'outcome', 'rounds', 'cost'}. Never raises into
    the loop: an internal error is logged as ASSIGN-ERROR and the cycle ends normally (end hooks still run)."""
    out = {"outcome": "none", "rounds": 0, "cost": 0.0}
    try:
        return _assignment_rounds(a, n, bench, runner_log, status_path, judge_prompt, model, effort, judge_rc,
                                  next_md5_cycle_start, out)
    except Exception as e:  # noqa: BLE001
        log_line(runner_log, "ASSIGN-ERROR | %s | cycle %d | %s: %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                                       type(e).__name__, str(e)[:300]))
        out["outcome"] = "error"
        return out


def _assignment_rounds(a, n, bench, runner_log, status_path, judge_prompt, model, effort, judge_rc, md5_start, out):
    GA = _guard_assign()
    cfg_path = os.path.abspath(a.assign_config) if a.assign_config else GA.DEFAULT_CONFIG
    cfg = GA.load_config(cfg_path)
    cards_dir = os.path.join(bench, "cards")
    os.makedirs(os.path.join(bench, "assign"), exist_ok=True)
    os.makedirs(cards_dir, exist_ok=True)

    def stamp():
        return time.strftime("%Y-%m-%d %H:%M:%S")

    if judge_rc != 0:
        log_line(runner_log, "ASSIGN | %s | cycle %d | not started: the judgement session exited %d" % (stamp(), n, judge_rc))
        out["outcome"] = "judge-failed"
        return out
    md5, card, why = next_json_reading(bench)
    if card is None or md5 == md5_start:
        log_line(runner_log, "ASSIGN | %s | cycle %d | not started: no NEW purpose (next.json %s)"
                 % (stamp(), n, "unchanged" if card is not None else "absent/invalid: %s" % why))
        out["outcome"] = "no-purpose"
        return out
    handback_in = None
    k = 0
    while True:
        if card.get("stop_requested"):
            log_line(runner_log, "ASSIGN | %s | cycle %d | not started: next.json sets stop_requested" % (stamp(), n))
            out["outcome"] = "stop-requested"
            return out
        k += 1
        out["rounds"] = k
        st_path = os.path.join(bench, "assign", "state_%d_%d.json" % (n, k))
        res_path = os.path.join(cards_dir, "assign_result_%d_%d.json" % (n, k))
        for stale in (res_path,):
            if os.path.exists(stale):
                os.remove(stale)
        purpose = purpose_from_next(card)
        ac_path, ac_why = write_assign_card(cards_dir, n, k, purpose, md5, cfg, st_path, res_path, handback_in)
        if not ac_path:
            log_line(runner_log, "ASSIGN | %s | cycle %d round %d | not started: the assign/1 card did not validate (%s)"
                     % (stamp(), n, k, ac_why))
            out["outcome"] = "card-invalid"
            return out
        inner = assign_cmd(a, cfg, "CARD %s\n\n%s" % (protocol._rel(ac_path).replace("\\", "/"), read(ASSIGN_PROMPT_FILE)))
        if inner is None:
            log_line(runner_log, "ASSIGN | %s | cycle %d round %d | skipped (dry run without --assign-dry-cmd)"
                     % (stamp(), n, k))
            out["outcome"] = "skipped"
            return out
        GA.new_state(st_path, n, k, purpose, md5, os.path.join(bench, "decisions_pending.json"))
        alog = os.path.join(bench, "cycle_%d_assign_%d.log" % (n, k))
        log_line(runner_log, "ASSIGN | %s | cycle %d round %d | start %s/%s, caps %s min / %s USD / %s cards (hard %s min / "
                             "%s USD) | %s" % (stamp(), n, k, cfg["model"], cfg["effort"], cfg["cap_minutes"],
                                               cfg["cap_usd"], cfg["backstop_cards"], cfg["hard_minutes"], cfg["hard_usd"],
                                               protocol._rel(ac_path)))
        cmd = [sys.executable, BGRUN, "--max-min", str(cfg["hard_minutes"]), "--log", alog, "--"] + inner
        env = spawn_env({"CYCLE_ROLE": "assign", "ASSIGN_STATE": st_path, "ASSIGN_RESULT": res_path,
                         "ASSIGN_CONFIG": cfg_path})
        rc, fresh, _s, _e, t_a = run_session(a, cmd, alog, env, n, status_path, runner_log, "CYCLE %d ASSIGN r%d" % (n, k))
        envj = result_json(fresh)
        usd = float(envj["total_cost_usd"]) if isinstance(envj, dict) and isinstance(
            envj.get("total_cost_usd"), (int, float)) else None
        out["cost"] += usd or 0.0
        minutes = (time.time() - t_a) / 60.0
        outcome, trig, detail, _res = GA.runner_verdict(st_path, res_path, usd, rc, cfg)
        st = GA.state_load(st_path) or {}
        log_line(runner_log, "ASSIGN | %s | cycle %d round %d | end exit %d | %s | %.0f min | %d card(s) | %s%s | %s"
                 % (stamp(), n, k, rc, ("$%.4f" % usd) if usd is not None else "$?", minutes, len(st.get("cards") or []),
                    outcome, (" (%s)" % trig) if trig else "", str(detail)[:200]))
        if outcome == "PURPOSE_MET":
            out["outcome"] = "purpose-met"
            return out
        hb_path = write_handback(cards_dir, n, k, trig, detail, st_path, res_path, md5, usd, minutes)
        log_line(runner_log, "HANDBACK | %s | cycle %d round %d | %s | %s | %s"
                 % (stamp(), n, k, trig, str(detail)[:200], protocol._rel(hb_path)))
        if k >= int(cfg["max_handbacks_per_cycle"]):
            log_line(runner_log, "HANDBACK-LIMIT | %s | cycle %d | %d hand-back(s) = max_handbacks_per_cycle; the cycle "
                                 "closes, the next cycle's judgement reads %s" % (stamp(), n, k, protocol._rel(hb_path)))
            out["outcome"] = "handback-limit"
            return out
        # the judgement session judges the hand-back: a revised next.json -> next round; unchanged -> the cycle closes
        jlog = os.path.join(bench, "cycle_%d_handback_%d.log" % (n, k))
        jprompt = judge_prompt + "\nHANDBACK %s\n" % protocol._rel(hb_path).replace("\\", "/")
        jcmd = ([sys.executable, BGRUN, "--max-min", str(a.max_min), "--log", jlog, "--"]
                + session_cmd(a, jprompt, model, effort))
        jenv = spawn_env({"CYCLE_ROLE": "judgement", "PURPOSE_PHASE": "handback", "HANDBACK_RECORD": hb_path})
        jrc, jfresh, _s, _e, _t = run_session(a, jcmd, jlog, jenv, n, status_path, runner_log, "CYCLE %d HANDBACK r%d" % (n, k))
        jj = result_json(jfresh)
        if isinstance(jj, dict) and isinstance(jj.get("total_cost_usd"), (int, float)):
            out["cost"] += float(jj["total_cost_usd"])
        md5b, card_b, why_b = next_json_reading(bench)
        moved = card_b is not None and md5b != md5
        log_line(runner_log, "HANDBACK-JUDGED | %s | cycle %d round %d | exit %d | next.json %s"
                 % (stamp(), n, k, jrc, ("CHANGED - assignment round %d" % (k + 1)) if moved and not
                    card_b.get("stop_requested") else ("stop_requested" if moved else
                                                       "unchanged - the cycle closes" if card_b is not None else
                                                       "absent/invalid (%s) - the cycle closes" % why_b)))
        if not moved or jrc != 0:
            out["outcome"] = "closed-after-handback"
            return out
        md5, card, handback_in = md5b, card_b, hb_path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-min", type=float, default=180.0, help="wall-clock cap for ONE cycle's session")
    ap.add_argument("--cycles", type=int, default=0, help="0 = until a stop condition fires")
    ap.add_argument("--budget-min", type=float, default=480.0,
                    help="GRACEFUL wall-clock budget for the whole run: once exceeded, no NEW cycle is started; the "
                         "cycle in progress always finishes (user, 2026-09-21: never cut a cycle mid-way). Pair it with "
                         "a bgrun cap >= budget + the longest cycle, so bgrun's kill is only the last resort.")
    ap.add_argument("--model", default="claude-opus-5-5")  # user 2026-09-23: Opus 5.5 pinned by id (alias 'opus' resolved to claude-opus-5)
    ap.add_argument("--effort", default="high")  # user table 2026-09-27 (card chat-N4): Opus 5.5 HIGH fixed (A/B 89-97: high PASS 2.5 vs 2.0, $33 vs $39). Before: user 2026-09-23 14:xx: medium on Opus 5.5 (its medium ~= Opus 5 max on the index); earlier today high (max = +4 pts at 3.3x cost, news.hada.io/topic?id=34142); was max since 2026-09-17
    ap.add_argument("--permission-mode", default="acceptEdits")
    ap.add_argument("--ff-model", default=FF_MODEL,
                    help="firefighter cycle model (user table 2026-09-27: claude-opus-5-5 at effort max)")
    ap.add_argument("--firefighter", default="", metavar="RECIPE",
                    help="USER-ORDERED: start the FIRST cycle as a firefighter on this recipe basename (one Opus max "
                         "cycle, then the user)")
    ap.add_argument("--judge-ab", default="off", choices=("auto", "on", "off"),
                    help="level-0 judgement effort A/B by cycle parity (odd medium, even high); default OFF since "
                         "2026-09-27 (user table, card chat-N4); auto = on until 2026-09-28 07:00 KST")
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
    ap.add_argument("--outcome-cmd", default="", help="self-test only (card 108-5): whitespace-split stand-in run under "
                                                        "bgrun instead of outcome_review.py when the outcome review is due")
    # card chat-D2 (user 2026-10-09 "둘 다 넣자"): Claude-GPT discussions in the loop (tools/debate_loop.py)
    ap.add_argument("--outcome-by", default="debate", choices=("debate", "review"),
                    help="the due outcome review: a Claude-GPT discussion (outcome_review.py = fallback), or review only")
    ap.add_argument("--debate-max-min", type=float, default=40.0, help="discussion deadline (STOP file, then a kill)")
    ap.add_argument("--debate-max-rounds", type=int, default=6)
    ap.add_argument("--debate-stub", action="store_true", help="self-test only: stub speakers (no model call)")
    ap.add_argument("--debate-stub-secs", type=float, default=0.0, help="self-test only: seconds per stub message")
    ap.add_argument("--debate-doc", default="google", choices=("google", "local", "authfail"),
                    help="google (real runs); local / authfail = self-test only")
    ap.add_argument("--flow", default="purpose", choices=("purpose", "legacy"),
                    help="purpose (card chat-A1, user 2026-10-04): judgement sets next.json as the cycle's purpose, an "
                         "assignment session (tools/bench/assign/assign_config.json) dispatches the cards, hand-back is "
                         "mechanical; legacy: one judgement session does everything (before 2026-10-04)")
    ap.add_argument("--assign-config", default="", help="assignment config (default tools/bench/assign/assign_config.json)")
    ap.add_argument("--assign-dry-cmd", default="", help="self-test only: whitespace-split stand-in for the assignment "
                                                           "session under --dry-run/--dry-cmd (without it a dry run "
                                                           "skips the assignment phase)")
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
    stuck_next = None       # card chat-D2: "HANDBACK-LIMIT in cycle N" -> a stuck discussion before the next cycle
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
        ff_triggered = False                    # card chat-D2: set when the RUNNER's trigger (not the user) fires
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
                ff_triggered = True
                break
        ff_pending = None
        # STUCK -> DISCUSSION BEFORE THIS CYCLE (card chat-D2): the previous cycle hit HANDBACK-LIMIT, or the firefighter
        # trigger just fired. The discussion writes a steer card for this cycle; the firefighter rung still runs after it.
        stuck_why = [w for w in (stuck_next, ("firefighter trigger: `%s` failed in cycles %d and %d" % (
            ff_recipe, n - 2, n - 1)) if ff_triggered else None) if w]
        stuck_next = None
        debate_res = None
        if stuck_why:
            fl = [first_fail_line(p) for p in (fail_logs_hist[-1].values() if fail_logs_hist else [])][:8]
            debate_res = debate_hook("stuck", n, a, bench, runner_log, "; ".join(stuck_why), fl)
            if debate_res and debate_res.get("line"):
                hb.debate = debate_res["line"]
            mark = stop_marker(read(status_path))
            if mark:                            # a STOP written while the discussion ran
                log_line(runner_log, "RUNNER STOP | %s | STATUS.md carries a STOP marker: %s"
                         % (time.strftime("%Y-%m-%d %H:%M:%S"), mark))
                return 0
        # JUDGEMENT LADDER + A/B (card chat-M1): level from <bench>/judge_ladder.json; rank = max(level, ff rung).
        j_level, j_reason = judge_state_load(bench)
        ab_eff, ab_why = judge_ab_effort(n, a.judge_ab)
        base_effort = ab_eff or a.effort
        j_rank, model, effort = judge_choice(j_level, ff_recipe, ff_rung, a.model, base_effort)
        if ff_recipe and j_rank == FF_RANK.get(FF_LADDER[min(ff_rung, len(FF_LADDER) - 1)], 1):
            model = a.ff_model          # --ff-model names the firefighter's model when its rung decided the rank
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
        # B4 (2026-10-22): a LabVIEW started from here on (the Error List check's included) counts as this cycle's own;
        # labview_close_hook closes only those at the cycle end
        sys.path.insert(0, HERE)
        import rig_session
        lv_t0 = rig_session._filetime_now()
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
        # GATES DUE (card 108-5): every guard_cycle due-check measured now; a due outcome review RUNS now, before the
        # session and before the STEER read below (so a steer card the review writes rides in this cycle's card).
        g_out = {}
        g_due = gates_due_hook(n, a, bench, runner_log,
                               defer=("stuck discussion %s ran before this cycle" % debate_res.get("slug"))
                               if debate_res and debate_res.get("ok") else None, out=g_out)
        out_res = g_out.get("debate")
        if out_res and out_res.get("line"):
            hb.debate = out_res["line"]
        for dr in (debate_res, out_res):        # card chat-D2: the session sees where the discussion is
            if dr and dr.get("slug"):
                ap_ = dr.get("applied") or {}
                this_prompt += ("\n\nDISCUSSION before this cycle (Claude-GPT, card chat-D2): %s - %s; summary %s; doc %s; "
                                "steer card %s; decisions %s. Read the summary, not only the steer line.\n"
                                % (dr["slug"], dr.get("why"), protocol._rel(dr.get("summary_path") or "-"),
                                   dr.get("doc") or "-", protocol._rel(ap_["steer"]) if ap_.get("steer") else "none",
                                   ", ".join(ap_.get("decisions") or []) or "none"))
        due_now = [x for x in g_due if x["due"] is not False]
        if due_now:
            this_prompt += ("\n\nGATES DUE at cycle start (card 108-5; cycle card `gates_due`): %s - answer these BEFORE "
                            "the first dispatch that would trip them.\n"
                            % "; ".join("%s: %s" % (x["gate"], x["detail"][:140]) for x in due_now))
        # STEER (user 2026-09-24, card chat-D): the newest open steer/1 from a repeated outcome verdict rides in the
        # cycle card; the session follows it or refuses it with evidence in next.json `steer` (read after the cycle).
        steer_path, steer_card = protocol.active_steer(os.path.join(bench, "cards"), os.path.join(bench, "steer_state.json"))
        if steer_card:
            log_line(runner_log, "STEER | %s | cycle %d carries %s (%s)" % (time.strftime("%Y-%m-%d %H:%M:%S"), n,
                                                                          protocol._rel(steer_path), steer_card["item"]))
            this_prompt += ("\n\nSTEER (steering card, user 2026-09-24; `debate:` items come from a Claude-GPT "
                            "discussion, card chat-D2): %s - item `%s`.\nREQUIRED ACT: %s\n"
                            "Goal ids: %s. Follow it (next.json `steer`: {\"item\": \"%s\", \"response\": \"follow\"}) or "
                            "refuse it with evidence ({\"item\": ..., \"response\": \"refuse\", \"evidence\": [\"file:line\", "
                            "...]}). No answer counts as a refusal; two refusals stop the runner and go to the user.\n"
                            % (protocol._rel(steer_path), steer_card["item"], steer_card["required_act"],
                               ", ".join(steer_card["goal_ids"]), steer_card["item"]))
        # C1: the cycle card. An invalid card is not dispatched (docs/session-protocol.md, common rule 5).
        card_path, card_why = write_cycle_card(bench, n, status_text, model, effort, ff_recipe, why, a, el_card,
                                               steer_path if steer_card else None, j_note, g_due)
        if not card_path:
            reason = "the cycle/1 card for cycle %d did not validate (%s) - no cycle is dispatched without one" \
                     % (n, card_why)
            log_line(runner_log, "RUNNER STOP | %s | %s" % (time.strftime("%Y-%m-%d %H:%M:%S"), reason))
            note_in_status(status_path, reason)
            return 3
        log_line(runner_log, "CYCLE-CARD | %s | cycle %d | wrote %s (cycle/1 valid; next.json before: %s)"
                 % (time.strftime("%Y-%m-%d %H:%M:%S"), n, protocol._rel(card_path), next_md5_before[:12]))
        this_prompt = "CARD %s\n\n" % protocol._rel(card_path).replace("\\", "/") + this_prompt
        purpose = a.flow == "purpose"
        if purpose:                       # card chat-A1: the judgement session sets the purpose, it dispatches nothing
            this_prompt += "\n\n" + read(PURPOSE_ADDENDUM_FILE)
            prev = newest_assign_result(os.path.join(bench, "cards"))
            if prev:
                this_prompt += "\nASSIGN-RESULT %s\n" % protocol._rel(prev).replace("\\", "/")
        cmd = ([sys.executable, BGRUN, "--max-min", str(a.max_min), "--log", cyc_log, "--"]
               + session_cmd(a, this_prompt, model, effort))
        cyc_t0 = time.time()
        rc, fresh, start, end, t0 = run_session(a, cmd, cyc_log, spawn_env({"CYCLE_ROLE": "judgement"} if purpose else None),
                                                n, status_path, runner_log, "CYCLE %d" % n)
        env = result_json(fresh)
        assign_cost = 0.0
        if purpose:
            ar = assignment_rounds(a, n, bench, runner_log, status_path, this_prompt, model, effort, rc, next_md5_before)
            assign_cost = ar["cost"]
            if ar["outcome"] == "handback-limit":   # card chat-D2: a stuck discussion before the next cycle
                stuck_next = "HANDBACK-LIMIT in cycle %d (%d assignment round(s))" % (n, ar["rounds"])
        land_retrospective(bench, runner_log)
        retro_fallback(n, cyc_t0, a, bench, runner_log)       # card chat-P1 2b: due + none archived -> run it here
        # A DRY RUN NEVER COMMITS (2026-09-24, card chat-B3): the self-tests run this runner with --dry-run/--dry-cmd on
        # a temp bench, and git_commit_cycle's `git add -A` on ROOT turned 16 self-test cycles into 16 "Cycle N runner
        # auto-commit" commits of the real working tree (b0f2ced..6d9f980).
        if a.dry_run or a.dry_cmd:
            log_line(runner_log, "GIT | cycle %d | skipped (dry run)" % n)
        else:
            capabilities_hook(n, runner_log)                  # card chat-T7: the function list, before the commit that carries it
            git_commit_cycle(n, runner_log)
        # LabVIEW CLOSED AND VERIFIED GONE at every cycle end (the camera must not keep acquiring - user 2026-09-24):
        # only the cycle's own (B4). FIRST since 2026-10-22, as in lean_cycle_hooks / rig_session: no VI of ours may
        # hold COM3 or drive the magnet while the motor end hook returns it to 0 mm (Q2) and releases the limits.
        ok_lv, why_lv = labview_close_hook(n, a, bench, runner_log, read(status_path), t0=lv_t0, root_pid=os.getpid())
        # MOTOR LIMITS OFF at cycle end, verified by readback (user 2026-09-23), after the magnet return to 0 mm (Q2,
        # inside motor_gate --session end). Runs whatever the session's exit was; a release that cannot be verified
        # stops the runner and is written into STATUS, because limits left ON silently are exactly what happened
        # between 2026-09-18 and 2026-09-23.
        ok_end, why_end = motor_limits_hook("end", n, a, bench, runner_log, read(status_path))
        # BGRUN REAPER at cycle end (card 92-4): close the record of any bgrun killed from outside during the cycle.
        bgrun_reap_hook(n, bench, runner_log)
        cost =("$%.4f" % (env["total_cost_usd"] + assign_cost)) if isinstance(env, dict) and isinstance(
            env.get("total_cost_usd"), (int, float)) else ("$%.4f" % assign_cost if assign_cost else "?")
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
        # stop condition 3 (next.json unchanged twice) was REPLACED 2026-09-26 (card chat-M1b) by the judgement
        # ladder above: unchanged x1 -> opus max, x2 -> fable low, x3 -> RUNNER STOP (user table 2026-09-27).
        if unchanged_streak >= 2:
            log_line(runner_log, "NEXT-UNCHANGED | %s | cycle %d | %d consecutive cycles without a new next.json - "
                                 "handled by the judgement ladder" % (time.strftime("%Y-%m-%d %H:%M:%S"), n, unchanged_streak))


if __name__ == "__main__":
    sys.exit(main())
# ---
# labview: read
# hardware: motor
# offline-args: --dry-run --dry-cmd --no-motor-hooks
# evidence: tools/protocol.py:1100
# ---
