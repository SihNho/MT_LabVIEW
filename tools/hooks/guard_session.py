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
  (e) REPEATED TOOL FUNCTION (card chat-P2 item 4): an escalation-rung dispatch (material-opus-max / -fable-*) of a
      card whose failure repeats the SAME scripting function as the previous failing attempt is refused; the next card
      is the scratch-VI verification of that function at the same rung (stage_prerun.escalation_route).

  (f) SCOPE (user 2026-09-29 "수정안대로 진행하도록"): (a) and (b) bind RUNNER CYCLE SESSIONS only (CYCLE_SESSION=1,
      set by tools/cycle_runner.py). The interactive chat is not a cycle: it delegates offline work (benches,
      measurements) without a dispatch cap, and is bounded instead by its CONTEXT SIZE - a counted dispatch is refused
      once the chat's last turn used more than CHAT_CONTEXT_LIMIT tokens (write docs/chat-handoff.md, open a new chat).
      The Workflow tool (multi-agent orchestration) is a counted dispatch too: one in a cycle session, and subject to
      the same context rule in the chat. (c)-(e) are unchanged.

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
WORKFLOW_TOOLS = ("Workflow",)  # (f) multi-agent orchestration counts as one dispatch
# (f) DISABLED 2026-10-02 (user: "세션이 50% 넘으면 새 세션 열도록 강요하지 말고 그냥 문맥 압축하는 방향으로 가자" -
# the user is remote and cannot open a new chat): the chat runs on and relies on automatic context compaction. Was
# 500_000 (50 % of the 1M window). Set a number again to re-enable; None = no chat context bound.
CHAT_CONTEXT_LIMIT = None
TAIL_BYTES = 4_000_000          # read only the transcript's tail for the last assistant usage


def in_cycle():
    return bool(os.environ.get("CYCLE_SESSION"))


def last_context_tokens(transcript_path):
    """Tokens the chat's last assistant turn sent as input (input + cache creation + cache read), read from the
    tail of the transcript JSONL. None when unreadable - the caller fails OPEN (a broken reader never blocks)."""
    try:
        with open(transcript_path, "rb") as f:
            f.seek(0, 2)
            size = f.tell()
            f.seek(max(0, size - TAIL_BYTES))
            lines = f.read().decode("utf-8", "replace").splitlines()
    except (OSError, TypeError, ValueError):
        return None
    for line in reversed(lines):
        if '"usage"' not in line:
            continue
        try:
            d = json.loads(line)
        except ValueError:
            continue
        u = ((d.get("message") or {}).get("usage")) if isinstance(d, dict) else None
        if isinstance(u, dict) and d.get("type") == "assistant":
            return sum(int(u.get(k) or 0) for k in
                       ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    return None


def chat_context_refusal(data):
    """(f) The chat's bound: refuse a counted dispatch once its context passed CHAT_CONTEXT_LIMIT. '' = allow."""
    if CHAT_CONTEXT_LIMIT is None:
        return ""
    n = last_context_tokens((data or {}).get("transcript_path"))
    if n is None or n <= CHAT_CONTEXT_LIMIT:
        return ""
    return ("BLOCKED by tools/hooks/guard_session.py: CHAT CONTEXT %d tokens > %d (50 %% of the window).\n\n"
            "The interactive chat has no dispatch cap (user 2026-09-29); it is bounded by its context size instead,\n"
            "because a long context makes every turn expensive and fades the rules (CLAUDE.md section 3 item 2).\n"
            "Write the state into docs/chat-handoff.md and ask the user to open a new chat, which dispatches this.\n"
            % (n, CHAT_CONTEXT_LIMIT))
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
    elif data.get("tool_name") in WORKFLOW_TOOLS:
        sub = "workflow"
    else:
        return 0
    if not in_cycle():
        why = chat_context_refusal(data)
        if why:
            sys.stderr.write(why)
            return 2
    sid = session_id(data)
    try:
        with _lock(sid):
            return decide(sid, sub, ti)
    except TimeoutError as e:
        sys.stderr.write("BLOCKED by tools/hooks/guard_session.py: the session state lock is busy (%s) - retry the "
                         "dispatch in a moment.\n" % e)
        return 2


# (e) REPEATED TOOL FUNCTION -> SCRATCH VERIFY, NOT ESCALATION (card chat-P2 item 4, user 2026-09-28 "1~4번 적용";
# cycle 118 spent 84 min escalating one function). A dispatch to an escalation rung whose card re-issues a failed card
# (`retry_of_card`) is refused when stage_prerun.escalation_route() finds that the failure repeats the SAME scripting
# function as the previous failing attempt: the next card is the scratch-VI verification of that function, dispatched
# at the SAME rung as the failed card. Fails OPEN (a broken reader never blocks a dispatch) and is logged.
ESCALATION_TYPES = {"material-opus-max", "material-fable-low", "material-fable-medium"}


def escalation_refusal(sub, card, cpath):
    if sub not in ESCALATION_TYPES or not card or not card.get("retry_of_card"):
        return ""
    try:
        import stage_prerun
        route, fn, why = stage_prerun.escalation_route(card, cards_dir=os.path.dirname(cpath) if cpath else None)
    except Exception as e:  # noqa: BLE001
        sys.stderr.write("guard_session: escalation_route unreadable (%s: %s) - dispatch allowed\n"
                         % (type(e).__name__, str(e)[:160]))
        return ""
    if route != "scratch-verify":
        return ""
    return ("BLOCKED by tools/hooks/guard_session.py: REPEATED TOOL FUNCTION - SCRATCH VERIFY, NOT ESCALATION.\n"
            "  card %s re-issues %s to %s, but %s.\n\n"
            "Card chat-P2 item 4 (user 2026-09-28): the next card is the SCRATCH-VI VERIFICATION of `%s` at the SAME\n"
            "rung as %s (subagent_type of that card, normally `material`): a <=120-line stagekit script on a minimal\n"
            "scratch VI that runs `%s`, reads the graph back and writes tools/bench/scratch_verify/<function>_<ts>.json\n"
            "{\"function\": \"%s\", \"status\": \"PASS\", \"t\": <epoch>}. A model change does not fix a tool defect.\n"
            "Escalation stays for a failure that is NOT a repeated tool function (or after a newer scratch PASS).\n"
            % (card.get("id"), card.get("retry_of_card"), sub, why, fn, card.get("retry_of_card"), fn, fn))


def decide(sid, sub, ti):
    """The counted-dispatch decision, run under the session-state lock. 0 allow / 2 refuse."""
    st = load(sid)
    cycle = in_cycle()                   # (f) the cap and the retrospective close bind runner cycle sessions only
    if cycle and st.get("retro_done"):
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
    card, cpath = card_of_prompt(ti.get("prompt") if sub not in ("sendmessage-resume", "workflow") else "")
    why = escalation_refusal(sub, card, cpath)
    if why:
        sys.stderr.write(why)
        return 2
    entry = None
    live = prune_live(st.get("live"))
    if card is not None:
        cid = str(card.get("id") or os.path.basename(cpath or "?"))
        lv = str(((card.get("flags") or {}).get("labview")) or "none") if card else "read"   # unreadable: fail closed
        live = [e for e in live if e.get("id") != cid]          # a re-dispatch of the same card replaces its entry
        lv_live = [e for e in live if e.get("labview") != "none"]
        # RUN MODE (user 2026-09-28 15:4x): weekly usage above the fixed threshold = ECONOMY = no pipeline, one
        # live card at a time; missing/stale mode file fails safe to economy. Items 2-4 are untouched by the mode.
        try:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
            import run_mode
            mode, mode_why = run_mode.effective()
        except Exception as e:  # noqa: BLE001
            mode, mode_why = "economy", "run_mode unreadable: %s" % e
        if mode != "performance" and live:
            sys.stderr.write(
                "BLOCKED by tools/hooks/guard_session.py: ECONOMY MODE - one card at a time (%s).\n"
                "Live: %s. The pipeline (a prep card beside another card) runs only in PERFORMANCE mode\n"
                "(weekly usage <= tools/bench/run_mode_config.json threshold). Wait for its result_<id>.json, then\n"
                "dispatch %s.\n" % (mode_why, ", ".join("%s[%s]" % (e.get("id"), e.get("labview")) for e in live), cid))
            return 2
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
    if cycle and n > MAX_DISPATCHES:
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
