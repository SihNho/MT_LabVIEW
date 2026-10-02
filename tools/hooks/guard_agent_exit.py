"""guard_agent_exit.py - SubagentStop hook: a sub-agent may not end while a bgrun run IT launched is still alive.

Why (user decision D-2026-10-02-01, card chat-E1: "재료 에이전트는 중간에 갑자기 종료되지 않도록 장치 넣을 것"): three times
(card 129-2 on 2026-10-02, twice on 2026-09-17) a material agent started a LabVIEW run under tools/bgrun.py in the
background, wrote "waiting for the run to finish" and ended its turn; ending the agent killed the child mid-run. The
written rule ("wait in-turn") did not stop it, so it is now a refusal at the point of action.

Event semantics (official docs, https://code.claude.com/docs/en/hooks, read 2026-10-02): `SubagentStop` fires when a
SUB-AGENT finishes (the main session and `claude -p` sessions fire `Stop`, not this). Input = the common fields
(session_id, transcript_path, cwd, hook_event_name, ...) plus agent_id, agent_type, agent_transcript_path,
stop_hook_active, last_assistant_message. Exit code 2 + a reason on stderr "prevents the subagent from stopping"
(the reason is fed back to the agent, which continues). The matcher filters on agent type.

What is refused: THIS agent has a bgrun log whose LAST `BGRUN START` has no later `BGRUN END` / `BGRUN TIMEOUT` /
`BGRUN KILLED` line and whose `BGRUN PID <n>` process is alive. Attribution, both from data that exists today:
  (1) the agent's OWN transcript (agent_transcript_path, else <dir of transcript_path>/<session>/subagents/
      agent-<agent_id>.jsonl): every Bash/PowerShell tool_use whose command runs bgrun.py contributes its `--log`
      path(s) and the call's timestamp; the run counts only if its START is not older than that call (minus a
      slack), so an older run on a reused log name is never blamed on this agent;
  (2) the launch ledger tools/bench/cards/launches.jsonl (protocol.record_launch, written by guard_bash at the allowed
      launch): rows of the card this agent is bound to in tools/bench/cards/active.json, not older than the bind.
Runs of other agents, of the runner and of the chat appear in neither, so they never block this agent.

Never a trap: any exception => exit 0 (fail OPEN) and a logged line; a dead PID without END => allow (logged
"DEAD-NO-END"); after MAX_REFUSALS refusals for the same (agent, log) the stop is allowed and logged
("LOOP-BREAKER"). Self-test: tools/bench/selftest_guard_agent_exit.py. Prior art checked: no SubagentStop hook in
.claude/settings.json; tools/bgrun_reap.py closes logs of DEAD runners (complementary: this one guards LIVE runs).
Env overrides (self-test only): GUARD_AGENT_EXIT_LOG, GUARD_AGENT_EXIT_STATE, PROTOCOL_ACTIVE, PROTOCOL_LAUNCHES,
GUARD_AGENT_EXIT_PROJECT.
"""
import io
import json
import os
import re
import sys
import tempfile
import time
from datetime import datetime

PROJECT = os.environ.get("GUARD_AGENT_EXIT_PROJECT") or os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.abspath(__file__))))
CARDS = os.path.join(PROJECT, "tools", "bench", "cards")
ACTIVE = os.environ.get("PROTOCOL_ACTIVE") or os.path.join(CARDS, "active.json")
LAUNCHES = os.environ.get("PROTOCOL_LAUNCHES") or os.path.join(CARDS, "launches.jsonl")
LOG = os.environ.get("GUARD_AGENT_EXIT_LOG") or os.path.join(PROJECT, "tools", "bench", "guard_agent_exit.log")
STATE = os.environ.get("GUARD_AGENT_EXIT_STATE") or os.path.join(tempfile.gettempdir(), "guard_agent_exit_state.json")
MAX_REFUSALS = 3          # the 4th stop for the same (agent, log) is allowed
SLACK_S = 300             # a run's START may precede the transcript timestamp of its launch call by this much

BGRUN_RE = re.compile(r"bgrun\.py", re.I)
LOG_ARG_RE = re.compile(r"--log(?:\s+|=)(?:\"([^\"]+)\"|'([^']+)'|([^\s\"';&|]+))", re.I)
START_RE = re.compile(r"^BGRUN START (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)")
PID_RE = re.compile(r"^BGRUN PID (\d+)")
END_RE = re.compile(r"^BGRUN (END|TIMEOUT|KILLED)")


def note(msg):
    try:
        with io.open(LOG, "a", encoding="utf-8") as f:
            f.write(time.strftime("%Y-%m-%d %H:%M:%S") + " | " + msg + "\n")
    except Exception:
        pass


def local_epoch(s):
    return time.mktime(time.strptime(s, "%Y-%m-%d %H:%M:%S"))


def iso_epoch(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()


def resolve(path, cwd):
    p = path.replace("/", os.sep)
    if not os.path.isabs(p):
        p = os.path.join(cwd or PROJECT, p)
    return os.path.normcase(os.path.abspath(p))


def transcript_of(ev):
    p = ev.get("agent_transcript_path")
    if p and os.path.isfile(p):
        return p
    tp, aid, sid = ev.get("transcript_path"), ev.get("agent_id"), ev.get("session_id")
    if tp and aid:
        for c in (os.path.join(os.path.dirname(tp), sid or "", "subagents", "agent-%s.jsonl" % aid),
                  os.path.join(os.path.splitext(tp)[0], "subagents", "agent-%s.jsonl" % aid)):
            if os.path.isfile(c):
                return c
    return None


def logs_from_transcript(path, cwd):
    """{abs log path: earliest epoch of a bgrun call naming it} from this agent's own Bash/PowerShell calls."""
    out = {}
    with io.open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if "bgrun" not in line:
                continue
            try:
                row = json.loads(line)
            except ValueError:
                continue
            content = ((row.get("message") or {}).get("content")) or []
            if not isinstance(content, list):
                continue
            try:
                t = iso_epoch(row["timestamp"])
            except Exception:
                t = 0.0
            for item in content:
                if not isinstance(item, dict) or item.get("type") != "tool_use":
                    continue
                if item.get("name") not in ("Bash", "PowerShell"):
                    continue
                cmd = str((item.get("input") or {}).get("command") or "")
                if not BGRUN_RE.search(cmd):
                    continue
                for m in LOG_ARG_RE.finditer(cmd):
                    lp = resolve(next(g for g in m.groups() if g), cwd)
                    out[lp] = min(out.get(lp, t), t)
    return out


def logs_from_ledger(agent_id):
    """Ledger rows of the card this agent is bound to, launched at or after the bind."""
    out = {}
    try:
        with io.open(ACTIVE, encoding="utf-8") as f:
            ent = json.load(f).get(agent_id)
    except FileNotFoundError:
        return out
    if not ent:
        return out
    card, bound = ent.get("id"), local_epoch(ent["bound"])
    try:
        with io.open(LAUNCHES, encoding="utf-8") as f:
            rows = [json.loads(x) for x in f if x.strip()]
    except FileNotFoundError:
        return out
    for r in rows:
        if r.get("card") != card:
            continue
        t = local_epoch(r["t"])
        if t + 1 < bound:
            continue
        lp = resolve(os.path.join("tools", "bench", r["log"]), PROJECT)
        out[lp] = min(out.get(lp, t), t)
    return out


def pid_alive(pid):
    """True when `pid` is a live process (and, when its image name is readable, a python one)."""
    if os.name != "nt":
        try:
            os.kill(pid, 0)
            return True
        except OSError:
            return False
    import ctypes
    from ctypes import wintypes
    k32 = ctypes.windll.kernel32
    k32.OpenProcess.restype = wintypes.HANDLE
    h = k32.OpenProcess(0x1000, False, pid)            # PROCESS_QUERY_LIMITED_INFORMATION
    if not h:
        return ctypes.GetLastError() == 5               # ACCESS_DENIED = exists
    try:
        code = wintypes.DWORD()
        if not k32.GetExitCodeProcess(h, ctypes.byref(code)) or code.value != 259:   # STILL_ACTIVE
            return False
        buf, n = ctypes.create_unicode_buffer(1024), wintypes.DWORD(1024)
        if k32.QueryFullProcessImageNameW(h, 0, buf, ctypes.byref(n)):
            name = os.path.basename(buf.value).lower()
            return name.startswith("py")                 # py.exe / python.exe / pythonw.exe; else a reused pid
        return True
    finally:
        k32.CloseHandle(h)


def run_state(logp, since):
    """('live', pid) | ('ended', None) | ('dead', pid) | ('old', None) | ('none', None) for the log's LAST run."""
    if not os.path.isfile(logp):
        return "none", None
    with io.open(logp, encoding="utf-8", errors="replace") as f:
        lines = f.read().splitlines()
    idx = [i for i, x in enumerate(lines) if START_RE.match(x)]
    if not idx:
        return "none", None
    i = idx[-1]
    if local_epoch(START_RE.match(lines[i]).group(1)) + SLACK_S < since:
        return "old", None
    tail = lines[i + 1:]
    if any(END_RE.match(x) for x in tail):
        return "ended", None
    pid = next((int(PID_RE.match(x).group(1)) for x in tail if PID_RE.match(x)), None)
    if pid is None:
        return "live", None                              # START just written, PID line not yet: treat as live
    return ("live" if pid_alive(pid) else "dead"), pid


def load_state():
    try:
        with io.open(STATE, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_state(st):
    try:
        with io.open(STATE, "w", encoding="utf-8") as f:
            json.dump(st, f)
    except Exception:
        pass


def decide(ev):
    """Returns (exit_code, stderr_text)."""
    aid = ev.get("agent_id")
    if ev.get("hook_event_name", "SubagentStop") != "SubagentStop" or not aid:
        return 0, ""
    cwd = ev.get("cwd") or PROJECT
    logs = {}
    tp = transcript_of(ev)
    if tp:
        logs.update(logs_from_transcript(tp, cwd))
    for k, v in logs_from_ledger(aid).items():
        logs[k] = min(logs.get(k, v), v)
    if not logs:
        return 0, ""
    st, live = load_state(), []
    for lp, since in sorted(logs.items()):
        s, pid = run_state(lp, since)
        if s == "dead":
            note("DEAD-NO-END agent=%s log=%s pid=%s - allowed (runner gone, no END line)" % (aid, lp, pid))
        elif s == "live":
            key = aid + "|" + lp
            n = int(st.get(key, 0))
            if n >= MAX_REFUSALS:
                note("LOOP-BREAKER agent=%s log=%s pid=%s - allowed after %d refusals" % (aid, lp, pid, n))
                continue
            st[key] = n + 1
            live.append((lp, pid, n + 1))
    if not live:
        return 0, ""
    save_state(st)
    for lp, pid, n in live:
        note("REFUSED agent=%s type=%s log=%s pid=%s refusal=%d/%d" % (aid, ev.get("agent_type"), lp, pid, n,
                                                                         MAX_REFUSALS))
    rels = [os.path.relpath(lp, PROJECT).replace("\\", "/") if lp.startswith(os.path.normcase(PROJECT)) else lp
            for lp, _, _ in live]
    msg = ("BLOCKED by tools/hooks/guard_agent_exit.py (user D-2026-10-02-01): you launched a bgrun run that is still "
           "alive - ending now KILLS it mid-run. Wait in this turn for its final line, e.g. Bash timeout 600000: "
           "until grep -q \"BGRUN END\\|BGRUN TIMEOUT\\|BGRUN KILLED\" \"<log>\"; do sleep 10; done "
           "(repeat if the deadline passes), then report. Live: " +
           "; ".join("%s (pid %s, refusal %d/%d)" % (r, pid, n, MAX_REFUSALS) for r, (_, pid, n) in zip(rels, live)))
    return 2, msg


def main():
    try:
        raw = sys.stdin.buffer.read().decode("utf-8", errors="replace")
        ev = json.loads(raw)
        if not isinstance(ev, dict):
            raise ValueError("hook input is not an object")
        rc, msg = decide(ev)
    except Exception as e:                               # fail OPEN: a broken guard never traps an agent
        note("FAIL-OPEN %s: %s" % (type(e).__name__, str(e)[:300]))
        return 0
    if rc == 2:
        sys.stderr.write(msg + "\n")
    return rc


if __name__ == "__main__":
    sys.exit(main())
