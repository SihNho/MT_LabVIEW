r"""PreToolUse hook (Agent): ONE SESSION = ONE CYCLE, mechanically.

CLAUDE.md section 3 item 2 ("Session = one cycle - ENFORCED BY A RUNNER", user decision 2026-09-17,
"2번으로 가자. Opus max", after a 15-hour session): a judgement session reads STATUS.md + the current plan,
runs ONE cycle (delegate -> decide -> retrospective -> STATUS NEXT) and EXITS; `tools/cycle_runner.py` spawns
the next one fresh. The failure mode this hook removes is the one the user actually saw: a session that keeps
going after its cycle is finished, so the context grows all night and the expensive model re-reads it every turn.

Prose cannot enforce "now stop" on the session that is enjoying itself. So two refusals, both counted in a file:

  (a) DISPATCH CAP. The 7th material-type dispatch (material + its Fable rungs + log-reader + SendMessage resumes)
      in one session is refused (card chat-N1 (4b), user 2026-09-26; was 8). peer.ps1 is never counted.
  (b) AFTER THE RETROSPECTIVE, THE CYCLE IS CLOSED. Once `tools/retrospective.py` has run in this session
      (recorded by `tools/hooks/guard_bash.py`, which sees the command), any further material dispatch is
      refused. A retrospective reviews a cycle; work done after it belongs to a cycle nobody reviewed.
  (c) NO SendMessage RESUME in a cycle session (CYCLE_SESSION=1), 2026-09-24 - see send_message_refusal().
  (d) PIPELINE (card chat-P1 item 1, user 2026-09-28 "1~4번은 적용하도록"): a dispatch whose prompt is `CARD <path>`
      is tracked as LIVE in st["live"] = [{id, labview, t, minutes, card}] until its result_<id>.json exists (newer
      than the dispatch) or budget.minutes x 1.5 have passed. At most MAX_LIVE (2) cards are live, at most ONE of
      them with flags.labview != "none" (one COM client). A labview:none card dispatched while a LabVIEW card is live
      is a PREP card: it counts in st["prep"] (budget PREP_BUDGET = 3), not in MAX_DISPATCHES. The state file is
      read-modified-written under a lock file (two Agent calls in one message run this hook concurrently).

STATE: `tools/bench/session_<session_id>.json` = {"dispatches": n, "retro_done": bool, ...}. A file, not a
memory - CLAUDE.md: "a rule whose counter is my memory is not a rule at all". `.json`, so no log gate globs it.

BENCH_CELL set => exit 0 immediately (same exemption lv_stallcheck.ps1 uses): benchmark cells spawned by the
harness dispatch agents by construction and are not cycles.

Exit code 2 = block (stderr goes back to Claude); 0 = allow.
Self-test: `py tools/bench/selftest_guard_session.py` (synthetic stdin JSON, no LabVIEW, no agents spawned).
"""
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
BENCH = os.path.join(ROOT, "tools", "bench")

MAX_DISPATCHES = 6          # card chat-N1 (4b), user-approved 2026-09-26 (was 8)
# The agents a cycle's material work goes through (.claude/agents/), incl. the Fable escalation rungs. Every other
# subagent_type - the peer roles, Explore, a one-off general-purpose search - is never counted or refused; peer.ps1
# runs through Bash and is never counted.
COUNTED = {"material", "material-opus-max", "material-fable-low", "material-fable-medium", "log-reader"}
# This harness names the sub-agent tool `Agent`; older Claude Code builds name it `Task`. Matching both costs
# nothing and stops the hook from becoming silently inert after an upgrade (the defect guard_cycle's PRIOR_ART_RE
# had for a day: a gate that never fires looks exactly like a gate that passes).
AGENT_TOOLS = ("Agent", "Task")
SAFE_RE = re.compile(r"[^A-Za-z0-9._-]")
MAX_LIVE = 2                # card chat-P1 (1): one LabVIEW card + one offline prep card
PREP_BUDGET = 3             # offline cards dispatched while a LabVIEW card is live
LIVE_FACTOR = 1.5           # a card with no result is dead after budget.minutes x this
CARD_RE = re.compile(r"^\s*CARD\s+(\S+)", re.M)
sys.path.insert(0, os.path.dirname(HERE))       # tools/ - protocol.file_lock (one lock definition)


def session_id(data=None):
    sid = ""
    if isinstance(data, dict):
        sid = str(data.get("session_id") or "")
    sid = sid or os.environ.get("CLAUDE_SESSION_ID") or "unknown"
    return SAFE_RE.sub("_", sid)[:80]


def state_path(sid):
    return os.path.join(BENCH, "session_%s.json" % sid)


def load(sid):
    try:
        with open(state_path(sid), encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            d.setdefault("dispatches", 0)
            d.setdefault("retro_done", False)
            return d
    except (OSError, ValueError):
        pass
    return {"dispatches": 0, "retro_done": False}


def save(sid, d):
    try:
        os.makedirs(BENCH, exist_ok=True)
        with open(state_path(sid), "w", encoding="utf-8") as f:
            json.dump(d, f)
    except OSError:
        pass


def mark_retro_done(sid):
    """Called by tools/hooks/guard_bash.py when it sees the retrospective being run in this session.

    It lives here, not there, so there is ONE definition of the session state file (logclass.py's lesson:
    a classifier that three files each maintain separately is three classifiers)."""
    try:
        with _lock(sid):
            d = load(sid)
            if not d.get("retro_done"):
                d["retro_done"] = True
                save(sid, d)
            return d
    except TimeoutError:                 # observe-only: never wedge guard_bash; fall back to the unlocked write
        d = load(sid)
        d["retro_done"] = True
        save(sid, d)
        return d


def _lock(sid):
    import protocol
    return protocol.file_lock(state_path(sid) + ".lock")


def card_of_prompt(prompt):
    """(card dict | None, card abs path | None) for a `CARD <path>` prompt. An unreadable card -> ({}, path)."""
    m = CARD_RE.search(prompt or "")
    if not m:
        return None, None
    p = m.group(1).strip("\"'")
    p = p if os.path.isabs(p) else os.path.join(ROOT, p)
    try:
        with open(p, encoding="utf-8") as f:
            c = json.load(f)
        return (c if isinstance(c, dict) else {}), p
    except (OSError, ValueError):
        return {}, p


def prune_live(live, now=None):
    """The entries still live: no result_<id>.json newer than the dispatch beside the card, and younger than
    budget.minutes x LIVE_FACTOR."""
    now = now or time.time()
    out = []
    for e in live or []:
        res = os.path.join(os.path.dirname(e.get("card") or os.path.join(BENCH, "cards", "x")),
                           "result_%s.json" % e.get("id"))
        try:
            if os.path.getmtime(res) >= float(e.get("t", 0)) - 5:
                continue
        except OSError:
            pass
        if now - float(e.get("t", 0)) > float(e.get("minutes") or 60) * 60 * LIVE_FACTOR:
            continue
        out.append(e)
    return out


def send_message_refusal(data):
    """(c) NO RESUME BY SendMessage IN A CYCLE SESSION (docs/violation-decisions.md "repeated-failure-class -
    2026-09-24 05:54"; cycle 71 lost 57 min: a judgement session resumed a material agent with SendMessage, which
    runs it in the BACKGROUND, then polled build logs after that agent had already stopped on a gate refusal).

    Scope: CYCLE_SESSION=1 only (the interactive chat is untouched). The target's subagent_type is NOT visible to a
    PreToolUse hook - the Agent tool returns the agent id only after the spawn, and a cycle session's in-process
    agents are the material/log-reader ones by construction - so every SendMessage in a cycle session is refused
    except to "main" (a background agent reporting to its parent). Returns the refusal text or ''."""
    if data.get("tool_name") != "SendMessage" or not os.environ.get("CYCLE_SESSION"):
        return ""
    to = str((data.get("tool_input") or {}).get("to") or "").strip()
    if to.lower() == "main":
        return ""
    return ("BLOCKED by tools/hooks/guard_session.py: NO SendMessage RESUME IN A CYCLE SESSION (to=%r).\n\n"
            "SendMessage resumes a material/log-reader agent in the BACKGROUND; cycle 71 then polled logs for 57 min\n"
            "after that agent had stopped (docs/violation-decisions.md, repeated-failure-class 2026-09-24 05:54).\n"
            "Dispatch a NEW foreground Agent (subagent_type material or log-reader) with the full brief instead;\n"
            "it blocks until it returns.\n" % to)


def main():
    if os.environ.get("BENCH_CELL"):
        return 0
    try:
        data = json.load(sys.stdin)
    except Exception:
        return 0
    why = send_message_refusal(data)
    if why:
        sys.stderr.write(why)
        return 2
    ti = data.get("tool_input") or {}
    if data.get("tool_name") == "SendMessage":
        # card chat-L2: a SendMessage RESUME is a dispatch - it restarts a material/log-reader agent's work, so it
        # counts against MAX_DISPATCHES and is refused after the retrospective like a new Agent call. The target's
        # subagent_type is not visible here (see send_message_refusal), so every resume counts except to "main".
        if str(ti.get("to") or "").strip().lower() in ("", "main"):
            return 0
        sub = "sendmessage-resume"
    elif data.get("tool_name") in AGENT_TOOLS:
        sub = str(ti.get("subagent_type") or "").strip().lower()
        if sub not in COUNTED:
            return 0
    else:
        return 0
    sid = session_id(data)
    try:
        with _lock(sid):
            return decide(sid, sub, ti)
    except TimeoutError as e:
        sys.stderr.write("BLOCKED by tools/hooks/guard_session.py: the session state lock is busy (%s) - retry the "
                         "dispatch in a moment.\n" % e)
        return 2


def decide(sid, sub, ti):
    """The counted-dispatch decision, run under the session-state lock. 0 allow / 2 refuse."""
    st = load(sid)
    if st.get("retro_done"):
        sys.stderr.write(
            "BLOCKED by tools/hooks/guard_session.py: THIS SESSION'S CYCLE IS CLOSED BY ITS RETROSPECTIVE.\n"
            "  session state : %s (dispatches=%s, retro_done=true)\n\n"
            "CLAUDE.md section 3 item 2: a session runs ONE cycle - delegate, decide, run the retrospective,\n"
            "write STATUS.md's NEXT line, stop. Work started after the retrospective belongs to a cycle that\n"
            "nobody reviewed, and it is what makes a session grow all night.\n"
            "Write the NEXT line and end the session; `tools/cycle_runner.py` spawns the next cycle fresh.\n"
            % (os.path.relpath(state_path(sid), ROOT), st.get("dispatches")))
        return 2
    # (d) PIPELINE - only a `CARD <path>` dispatch is tracked; a prose prompt counts exactly as before.
    card, cpath = card_of_prompt(ti.get("prompt") if sub != "sendmessage-resume" else "")
    entry = None
    live = prune_live(st.get("live"))
    if card is not None:
        cid = str(card.get("id") or os.path.basename(cpath or "?"))
        lv = str(((card.get("flags") or {}).get("labview")) or "none") if card else "read"   # unreadable: fail closed
        live = [e for e in live if e.get("id") != cid]          # a re-dispatch of the same card replaces its entry
        lv_live = [e for e in live if e.get("labview") != "none"]
        if len(live) >= MAX_LIVE:
            sys.stderr.write(
                "BLOCKED by tools/hooks/guard_session.py: PIPELINE FULL - %d cards are live (%s).\n"
                "Card chat-P1 (user 2026-09-28): at most %d cards run at once - one LabVIEW card and one offline prep\n"
                "card. Wait for one to return (its result_<id>.json) before dispatching %s.\n"
                % (len(live), ", ".join("%s[%s]" % (e.get("id"), e.get("labview")) for e in live), MAX_LIVE, cid))
            return 2
        if lv != "none" and lv_live:
            sys.stderr.write(
                "BLOCKED by tools/hooks/guard_session.py: a second LabVIEW card while %s (labview %s) is live.\n"
                "One COM client at a time: card %s has flags.labview=%r. Only a labview:none card may run beside a\n"
                "LabVIEW card (card chat-P1 pipeline).\n" % (lv_live[0].get("id"), lv_live[0].get("labview"), cid, lv))
            return 2
        entry = {"id": cid, "labview": lv, "t": time.time(), "card": cpath,
                 "minutes": (card.get("budget") or {}).get("minutes") if card else None}
        if lv == "none" and lv_live:
            p = int(st.get("prep", 0)) + 1
            if p > PREP_BUDGET:
                sys.stderr.write(
                    "BLOCKED by tools/hooks/guard_session.py: PREP BUDGET SPENT (%d offline cards beside a LabVIEW card).\n"
                    "Card chat-P1: an offline prep card dispatched while a LabVIEW card is live counts in its own budget\n"
                    "of %d, not in the %d-dispatch cap. Wait for %s to return.\n"
                    % (PREP_BUDGET, PREP_BUDGET, MAX_DISPATCHES, lv_live[0].get("id")))
                return 2
            st["prep"] = p
            st["live"] = live + [entry]
            st["last_subagent"] = sub
            save(sid, st)
            return 0
    n = int(st.get("dispatches", 0)) + 1
    if n > MAX_DISPATCHES:
        sys.stderr.write(
            "BLOCKED by tools/hooks/guard_session.py: CYCLE DISPATCH CAP REACHED (%d material/log-reader "
            "dispatches).\n"
            "  session state : %s\n\n"
            "Six dispatches is a cycle's worth of material work (card chat-N1, 2026-09-26); past that this\n"
            "session is carrying a second cycle, which CLAUDE.md section 3 item 2 forbids. WRITE NEXT AND EXIT:\n"
            "run the retrospective if it is owed, write STATUS.md's NEXT line, and let the runner start a fresh\n"
            "session.\n"
            % (MAX_DISPATCHES, os.path.relpath(state_path(sid), ROOT)))
        return 2
    st["dispatches"] = n
    st["last_subagent"] = sub
    if entry is not None:
        st["live"] = live + [entry]
    save(sid, st)
    return 0


if __name__ == "__main__":
    sys.exit(main())
