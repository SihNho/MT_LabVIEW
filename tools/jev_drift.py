r"""jev_drift.py - insertion #4 of the SECOND WAVE table in docs/jev-integration-plan.md: PER-COMMAND DRIFT.

The question asked, once per command that RUNS something: "is this command a step toward STATUS.md's `## NEXT`
FIRST ACT?" - the 🔴 bullet a fresh session is supposed to start from. A low probability prints ONE advisory
line and logs it. IT NEVER BLOCKS ANYTHING, by construction: tools/hooks/guard_bash.py calls advisory() and
discards its return value.

WHY IT IS ONLY A WARNING: the state carries the FIRST act alone, so a command pursuing a later act that the
same NEXT names ("THEN D-2 ...") reads as off-task. That is a property of the question, measured and reported
in tools/bench/jev_wave2b_trials.py, not a defect to be patched by widening the gate's powers.

PRIOR ART CHECKED before writing (CLAUDE.md, "check what already exists"):
  - tools/jev.py            - transport, key handling, ledger, unknown band. NOT re-implemented here.
  - tools/bench/jev_next_q.py - the NEXT-quality questions (#5). A different question: that one judges the
                            hand-off text, this one judges a command against it.
  - tools/hooks/guard_bash.py:next_gate() - the advisory shape this file copies (print + jev_gate.log, silent
                            on any failure).
  - tools/jev_triage.py, tools/bench/jev_gate.py - failure-class work, unrelated.
No LabVIEW, no COM, no network except through jev.ask().
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import jev  # noqa: E402

STATUS = os.path.join(ROOT, "STATUS.md")
MARKER_LOG = os.path.join(HERE, "hooks", "material_marker.log")
GATE_LOG = os.path.join(BENCH, "jev_gate.log")
RATE_STATE = os.path.join(BENCH, "jev_drift_state.json")
RATE_SECONDS = 60.0            # at most one Jev call per 60 s per session
FIRST_ACT_MAX = 1500
DRIFT_LO = 0.30                # p <= this prints the advisory; the project's "no" band

NEXT_SECTION_RE = re.compile(r"^##\s+NEXT\s*$(.*?)(?=^##\s|\Z)", re.M | re.S)

# A command that RUNS something: the deadline runner, a recipe or bench script in command position, or a peer
# dispatch. Command position, never a substring - the reason is guard_bash.MATERIAL_RE's own comment (a
# read-only one-liner that merely CONTAINS such a path is not a run).
RUNS_RE = re.compile(
    r"\bbgrun\.py\b|"
    r"\bpy(?:thon)?[\w.]*\s+(?:-\S+\s+)*[^\s|;&]*tools[\\/](?:recipes|bench)[\\/][^\s|;&]*\.py|"
    r"peer\.ps1\b", re.I)
# Read-only shells: a command whose FIRST word only reads. Skipped without spending a call.
READONLY_RE = re.compile(
    r"^\s*(?:cd\s+\S+\s*(?:&&|;)\s*)?"
    r"(?:cat|head|tail|sed|grep|rg|less|type|wc|ls|dir|git|echo|find|"
    r"Get-Content|Select-String|Get-ChildItem)\b", re.I)
# Reading ABOUT a script is not running it, even past a `cd`.
READ_OF_SCRIPT_RE = re.compile(r"(?:^|&&|;|\|)\s*(?:cat|head|tail|sed|grep|rg|less|type|wc)\b", re.I)


DRIFT_Q = {
    "type": "noul",
    "instructions": (
        "A long-running LabVIEW VI-scripting project hands each work cycle a written first act: "
        "`next_first_act` is the one bullet of STATUS.md's `## NEXT` that says what the session does FIRST - "
        "the act, the file to start from, and how it will know it succeeded. `command` is a shell command the "
        "session is about to run; `recent_commands` are the last few commands it ran, oldest first, for "
        "context only. Decide whether `command` is a step toward carrying out that first act. Count as steps "
        "toward it: running the named script or diagnostic, a syntax/AST check of it, re-running it after a "
        "repair, and measuring something the first act's pass criterion needs. Do NOT count: work on the "
        "project's own machinery (self-tests of tools, audit or bookkeeping scripts, gate repairs), a "
        "different deliverable, or a later act that the hand-off defers until after this one."),
    "criteria": {
        "true": ("The command advances the first act as written - it runs, checks, or repairs the named script "
                 "or diagnostic, or it measures exactly what the first act's criterion requires."),
        "false": ("The command does something else: a tool self-test, an audit or documentation script, a "
                  "different build, or an act the hand-off explicitly puts after the first one. The first act "
                  "is not advanced by running it."),
    },
}

WHAT_Q = {
    "type": "choice",
    "instructions": (
        "The command was judged not to advance the cycle's first act. Say what it is doing instead."),
    "criteria": {
        "review": "A peer review, prior-art review, retrospective or other review dispatch.",
        "diagnostic": "A measurement or diagnostic run that is not what the first act asked for.",
        "repair": "Work on the project's own machinery: a tool self-test, a gate or audit repair, bookkeeping.",
        "other": "None of those - a different build, a different deliverable, or something unclassifiable.",
    },
}


def first_act(status_path=STATUS, maxchars=FIRST_ACT_MAX, text=None):
    """The cycle's first act from STATUS.md's `## NEXT`, truncated. '' when there is no NEXT section.

    ORDER, measured on the three hand-offs of 2026-09-22 (tools/bench/jev_drift_set.json): a 🔴 bullet that
    says FIRST ACT wins, because two of the three hand-offs open with a 🔴 STATE bullet and only name the act
    in the SECOND one - taking 'the first 🔴' would have fed the gate a status report. Then any 🔴 bullet,
    then the first line: a hand-off without the marker still has one, and an empty state would silence the
    reading entirely."""
    if text is None:
        try:
            with open(status_path, encoding="utf-8", errors="replace") as fh:
                text = fh.read()
        except OSError:
            return ""
    m = NEXT_SECTION_RE.search(text)
    if not m:
        return ""
    lines = [ln.strip() for ln in m.group(1).splitlines() if ln.strip()]
    red = [ln for ln in lines if ln.startswith("\U0001F534")]          # 🔴
    for ln in red:
        if re.search(r"FIRST ACT", ln[:120], re.I):
            return ln[:maxchars]
    if red:
        return red[0][:maxchars]
    return (lines[0][:maxchars] if lines else "")


def recent_commands(n=5, marker_log=MARKER_LOG):
    """The last n commands this project's material-marker recorded, oldest first. [] on any failure."""
    try:
        with open(marker_log, encoding="utf-8", errors="replace") as fh:
            rows = [ln.rstrip("\n") for ln in fh if ln.strip() and not ln.startswith("#")]
    except OSError:
        return []
    out = []
    for ln in rows[-n:]:
        parts = ln.split("\t")
        out.append(parts[2][:200] if len(parts) >= 3 else ln[:200])
    return out


def is_run_command(cmd):
    """True when the command RUNS something (bgrun / a recipe or bench script / a peer dispatch)."""
    if not cmd or READONLY_RE.search(cmd) or READ_OF_SCRIPT_RE.search(cmd):
        return False
    return bool(RUNS_RE.search(cmd))


def _rate_ok(sid, now=None, path=None, seconds=None, commit=True):
    """True when this session has not asked within `seconds`. Records the new time when commit is set.

    A missing or corrupt state file means 'allowed' - the rate limit protects the budget, it is not a gate,
    so it fails open and never wedges the hook.

    `path`/`seconds` default to the MODULE GLOBALS at call time, not at definition time: a default argument
    is bound once, so `jev_drift.RATE_STATE = <temp>` in the self-test silently had no effect and two cases
    rate-limited each other through the project's real state file."""
    now = time.time() if now is None else now
    path = RATE_STATE if path is None else path
    seconds = RATE_SECONDS if seconds is None else seconds
    state = {}
    try:
        with open(path, encoding="utf-8") as fh:
            state = json.load(fh)
        if not isinstance(state, dict):
            state = {}
    except (OSError, ValueError):
        state = {}
    last = state.get(str(sid))
    if isinstance(last, (int, float)) and now - last < seconds:
        return False
    if commit:
        state[str(sid)] = now
        if len(state) > 64:                      # keep the file small; drop the oldest sessions
            state = dict(sorted(state.items(), key=lambda kv: kv[1])[-32:])
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(state, fh)
        except OSError:
            pass
    return True


def judge(cmd, act=None, recent=None, timeout=20, retries=0, purpose="drift"):
    """(p, what, err). p is the probability the command advances the first act; `what` is the second-choice
    answer, asked ONLY when p <= DRIFT_LO. Never raises."""
    act = first_act() if act is None else act
    if not act:
        return None, None, "no first act"
    recent = recent_commands() if recent is None else recent
    state = {"next_first_act": act[:FIRST_ACT_MAX],
             "command": (cmd or "")[:400],
             "recent_commands": "\n".join(recent)[:1200]}
    resp, err = jev.ask(state, {"on_task": DRIFT_Q}, purpose=purpose, timeout=timeout, retries=retries)
    if err:
        return None, None, err
    p = jev.noul(resp, "on_task")
    if p is None:
        return None, None, "no noul in response"
    what = None
    if p <= DRIFT_LO:
        wresp, werr = jev.ask(state, {"what": WHAT_Q}, purpose=purpose + "-what",
                              timeout=timeout, retries=retries)
        if not werr:
            what = jev.choice(wresp, "what")[0]
    return p, what, None


def advisory(cmd, sid="0", write_log=True):
    """The hook entry point. Returns the advisory line (also written to stderr and jev_gate.log) or None.

    ALWAYS returns None-or-a-string and NEVER raises: the caller discards it, and nothing this function does
    can change whether the command runs."""
    try:
        if not is_run_command(cmd):
            return None
        if not _rate_ok(sid):
            return None
        p, what, err = judge(cmd)
        if err or p is None or p > DRIFT_LO:
            return None
        line = "JEV-DRIFT p=%.2f: %s" % (p, what or "?")
        sys.stderr.write(line + "  (advisory, nothing is blocked; docs/jev-integration-plan.md 2nd wave #4)\n")
        if write_log:
            try:
                with open(GATE_LOG, "a", encoding="utf-8") as fh:
                    fh.write("%s | %s | drift_gate | %s\n" % (
                        time.strftime("%Y-%m-%d %H:%M:%S"), line, (cmd or "").replace("\n", " ")[:160]))
            except OSError:
                pass
        return line
    except Exception:      # noqa: BLE001 - an advisory reading may never break the hook
        return None


if __name__ == "__main__":
    c = " ".join(sys.argv[1:])
    print("run-command: %s" % is_run_command(c))
    print("first act  : %s" % first_act()[:160])
    if is_run_command(c):
        pp, ww, ee = judge(c)
        print("p=%s what=%s err=%s" % (pp, ww, ee))
