r"""jev_drift.py - insertion #4 of the SECOND WAVE table in docs/jev-integration-plan.md: PER-COMMAND DRIFT.

The question asked, once per command that RUNS something: "is this command a step toward ANY act STATUS.md's
`## NEXT` orders or permits?" A low probability prints ONE advisory line and logs it. IT NEVER BLOCKS
ANYTHING, by construction: tools/hooks/guard_bash.py calls advisory() and discards its return value.

⚠️ CHANGED 2026-09-22 (user: "전부 적용해보자"): THE STATE IS THE WHOLE `## NEXT` SECTION, NOT THE FIRST ACT.
The first measurement of this reading (31 labelled commands x the NEXT in force, 77.4 %, Brier 0.181,
tools/bench/jev_wave2b_trials.py) showed the cost of the narrow state in the numbers: 5 of 18 on-task commands
were false alarms and the `sequel` subset - a later act that the SAME hand-off defers to the same cycle - read
as off-task by construction, because the state simply did not contain those acts. That was a property of the
QUESTION, so the question is what changed: `next_section` now carries the whole hand-off (🔴/🟢/⚠️ bullets in
order, <= NEXT_MAX chars) and the criterion is "any act this NEXT orders or permits - the first act, a later
act it defers to this cycle, or a repair it names". Everything else is unchanged: advisory only, one reading
per session per RATE_SECONDS, read-only commands skipped without spending a call.

`first_act()` IS KEPT, unused by the live path, because tools/bench/jev_wave2b_trials.py is the archived
measurement of the OLD question and must keep running against the old state to stay comparable.

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
NEXT_MAX = 4000                # the WHOLE `## NEXT` section (2026-09-22); the longest of 2026-09-22's three
                               # hand-offs is ~1.7 k chars, so this truncates nothing seen so far
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
        "A long-running LabVIEW VI-scripting project hands each work cycle a written hand-off. "
        "`next_section` is that hand-off verbatim: the whole `## NEXT` section of STATUS.md, bullet by bullet "
        "in order - the state the work is in, the act the session must do FIRST, any later acts the same "
        "hand-off defers to this cycle ('THEN ...'), and any repairs, checks or bookkeeping it names. "
        "`command` is a shell command the session is about to run; `recent_commands` are the last few commands "
        "it ran, oldest first, for context only. Decide whether `command` is a step toward ANY act this "
        "hand-off orders or permits. Count as steps toward it: running a script or diagnostic the hand-off "
        "names, a syntax/AST check of one, re-running it after a repair, measuring something one of its pass "
        "criteria needs, and carrying out a later act or a named repair the same hand-off lists. Do NOT count: "
        "work the hand-off does not mention at all - a different deliverable, a tool self-test or gate repair "
        "it never asked for, or bookkeeping outside it."),
    "criteria": {
        "true": ("The command advances something this NEXT orders or permits - the first act, a later act the "
                 "same hand-off defers to this cycle, or a repair, check or measurement it names."),
        "false": ("The command does something this NEXT does not ask for at all: a different build or "
                  "deliverable, a self-test or machinery repair the hand-off never names, or unrelated "
                  "bookkeeping."),
    },
}

WHAT_Q = {
    "type": "choice",
    "instructions": (
        "The command was judged not to advance anything the cycle's hand-off (`next_section`) orders or "
        "permits. Say what it is doing instead."),
    "criteria": {
        "review": "A peer review, prior-art review, retrospective or other review dispatch.",
        "diagnostic": "A measurement or diagnostic run that is not what the first act asked for.",
        "repair": "Work on the project's own machinery: a tool self-test, a gate or audit repair, bookkeeping.",
        "other": "None of those - a different build, a different deliverable, or something unclassifiable.",
    },
}


def next_block(status_path=STATUS, maxchars=NEXT_MAX, text=None):
    """THE WHOLE `## NEXT` section of STATUS.md, blank lines dropped, bullets kept IN ORDER, truncated to
    `maxchars`. '' when there is no NEXT section (the reading then stays silent, as it always did).

    This replaces first_act() in the live path on 2026-09-22. Nothing is selected, ranked or summarised here:
    the point of the change is that the model sees the later acts and the named repairs too, so a command
    pursuing one of them is not off-task by construction. Truncation is at the END (the tail of a hand-off is
    housekeeping; the acts are at the top) and NEXT_MAX is above every hand-off written so far."""
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
    return "\n".join(lines)[:maxchars]


def first_act(status_path=STATUS, maxchars=FIRST_ACT_MAX, text=None):
    """SUPERSEDED IN THE LIVE PATH 2026-09-22 by next_block(); KEPT because tools/bench/jev_wave2b_trials.py is
    the archived measurement of the narrow question and has to keep asking it to stay comparable.

    The cycle's first act from STATUS.md's `## NEXT`, truncated. '' when there is no NEXT section.

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


def judge(cmd, act=None, recent=None, timeout=20, retries=0, purpose="drift", n=None):
    """(p, what, err). p is the CONSENSUS mean probability that the command advances something the cycle's
    `## NEXT` orders or permits; `what` is the second-choice answer, asked ONLY when p <= DRIFT_LO.
    Never raises on a Jev error (it returns it); the caller's try/except covers the rest.

    `act` is the STATE, and from 2026-09-22 that state is the whole NEXT section, not one bullet - the keyword
    is kept so the trial scripts that pass a state in keep working. `n` is the consensus width; None means
    jev.samples() (5 since 2026-09-22 17:3x, the project-wide answer to single-call flapping)."""
    # LIVE STATE = the FIRST ACT again (interactive chat, 2026-09-22 18:xx): the whole-NEXT state was measured on
    # the same 31 commands and read WORSE at every threshold (77.4 % -> 54.8 %, off-task detection 11/13 -> 4/13,
    # tools/bench/jev_wave3a.log:34-56). The wider question is kept behind JEV_DRIFT_STATE=next for re-trials.
    if act is None:
        act = next_block() if os.environ.get("JEV_DRIFT_STATE", "").lower() == "next" else first_act()
    if not act:
        return None, None, "no next section"
    recent = recent_commands() if recent is None else recent
    state = {"next_section": act[:NEXT_MAX],
             "command": (cmd or "")[:400],
             "recent_commands": "\n".join(recent)[:1200]}
    p, _spread, err = jev.ask_n(state, {"on_task": DRIFT_Q}, n=n, purpose=purpose,
                                timeout=timeout, retries=retries)
    if err:
        return None, None, err
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
    print("next block : %s" % next_block()[:240].replace("\n", " | "))
    if is_run_command(c):
        pp, ww, ee = judge(c)
        print("p=%s what=%s err=%s" % (pp, ww, ee))
