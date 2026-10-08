# ---
# labview: none
# hardware: none
# ---
r"""guard_assign.py - the ASSIGNMENT session's MECHANICAL HAND-BACK (card chat-A1, user 2026-10-04).

USER, 2026-10-04: "사이클 기준은 작업지시로 훅을 걸지 말고 목적에 따라서 나누는게 맞는듯. 다만, 판단 사이클이 독자적으로 쪼갤
것이 아니라 싸이클 업무 배정 에이전트를 운용하여 유동성을 확보하는게 좋을듯" -> cloud bench -> "세션 규칙 설정은 그렇게 하고".
Bench (tools/bench/assignbench/report_cloud.md): every arm was weakest on HANDBACK (Opus 0.17, Sonnet high 0.42), so the
hand-back is decided HERE, by code, and the assignment session only obeys a refusal.

A cycle is one PURPOSE: the judgement session writes tools/bench/next.json (act, pass, plan), exits; tools/cycle_runner.py
spawns the assignment session (claude-sonnet-5-5 high, top-level `claude -p`, env CYCLE_SESSION=1 CYCLE_ROLE=assign
ASSIGN_STATE=<state file>), which dispatches task/1 cards to the material agents. tools/hooks/guard_session.py (the
registered PreToolUse Agent hook) calls check_dispatch() below on every counted dispatch of that session; the runner calls
evaluate() again after the session ends. NOT a registered hook itself (.claude/settings.json belongs to card chat-E3).

HAND-BACK TRIGGERS (each one refuses this dispatch AND every later one - `state.handback` is sticky):
  (a) a card FAILed with a first_fail the existing classifiers do not explain (gateclass.address_only's ADDR_FAIL_RE ->
      'address'; gateclass.classify_line -> 'log' = 'soft'; an errorlist JSON artefact whose by_design verdict is 'log' or
      that carries 'soft' -> 'by-design'), and that card was itself the ONE retry (task/1 `retry_of_card`).
  (b) the same failure class (classifier kind, else the normalised first_fail, else blocked_by.device) in two results.
  (c) a card would change the plan file (next.json plan.path), a protected path (config protected_globs: CLAUDE.md, user
      rules, settings, agents, hooks, memory_model.json, this config), a memory limit (memory_tokens next to a change
      word in goal/pass/why/note), or works outside the purpose (advances/unblocks disjoint from next.json's). A protected
      path or token that the purpose text itself names is inside the plan and passes.
  (d) a question only the user can answer: tools/bench/decisions_pending.json gained an open item since the session
      started, or a result is BLOCKED with blocked_by.device in config user_question_devices.
  LIMITS, checked between cards: cap-time (cap_minutes since the session started), cap-usd (estimate from the session's
  transcript + its subagents' transcripts x prices_per_mtok), backstop (backstop_cards dispatches). MAX_DISPATCHES (6)
  does not bind this role.
Plain refusals (fixable by the session, NOT a hand-back): a material dispatch without a `CARD <path>` prompt, an
unreadable card, a card with neither `advances` nor `unblocks`.

Config: tools/bench/assign/assign_config.json (env ASSIGN_CONFIG overrides). Self-test: tools/bench/selftest_assign_flow.py.
"""
import glob
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
TOOLS = os.path.join(ROOT, "tools")
DEFAULT_CONFIG = os.path.join(ROOT, "tools", "bench", "assign", "assign_config.json")
MATERIAL_TYPES = {"material", "material-opus-max", "material-fable-low", "material-fable-medium"}
DEFAULTS = {"model": "claude-sonnet-5-5", "effort": "high", "cap_minutes": 180, "cap_usd": 60, "hard_minutes": 300,
            "hard_usd": 90, "backstop_cards": 30, "max_handbacks_per_cycle": 3, "protected_globs": [],
            "memory_tokens": ["MEMSTOP", "X10", "memory_model"], "change_words": ["raise", "lower", "change", "set"],
            "user_question_devices": ["user", "decision"], "prices_per_mtok": {}}


def role():
    return (os.environ.get("CYCLE_ROLE") or "").strip().lower()


def load_config(path=None):
    p = path or os.environ.get("ASSIGN_CONFIG") or DEFAULT_CONFIG
    c = dict(DEFAULTS)
    try:
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        if isinstance(d, dict):
            c.update(d)
    except (OSError, ValueError):
        pass
    return c


def state_load(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else None
    except (OSError, ValueError):
        return None


def state_save(path, d):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)


def open_decisions_count(path):
    try:
        with open(path, encoding="utf-8") as f:
            d = json.load(f)
        return sum(1 for it in d.get("items") or [] if isinstance(it, dict) and it.get("status") == "open")
    except (OSError, ValueError, AttributeError):
        return 0


def new_state(path, cycle, rnd, purpose, next_md5, decisions_path, t0=None):
    """Written by the runner before it spawns the assignment session."""
    st = {"schema_note": "assignment state (card chat-A1); written by cycle_runner, read-modified by guard_assign",
          "cycle": cycle, "round": rnd, "t0": t0 or time.time(), "purpose": purpose, "next_md5": next_md5,
          "decisions_path": decisions_path, "decisions_open_start": open_decisions_count(decisions_path),
          "cards": [], "handback": None, "refusals": []}
    state_save(path, st)
    return st


# ------------------------------------------------------------------------------------------------ classification
def _norm_sig(s):
    s = re.sub(r"#-?\d+|\b\d{3,}\b|[0-9a-f]{12,}", "#", str(s or "")).lower()
    return re.sub(r"\s+", " ", s).strip()[:60]


def _artefact_by_design(res, card_path):
    for a in res.get("artefacts") or []:
        p = a.get("path") if isinstance(a, dict) else None
        if not p or not str(p).lower().endswith(".json"):
            continue
        p = p if os.path.isabs(p) else os.path.join(ROOT, p)
        try:
            with open(p, encoding="utf-8") as f:
                d = json.load(f)
        except (OSError, ValueError):
            continue
        if isinstance(d, dict) and (((d.get("by_design") or {}).get("verdict") == "log") or d.get("soft")):
            return True
    return False


def classify(res, card_path=None):
    """(explained_kind | None, class_key) for a FAIL/BLOCKED result/1 dict. Fails CLOSED: any classifier error -> unexplained."""
    ff = str(res.get("first_fail") or "")
    bb = res.get("blocked_by") if isinstance(res.get("blocked_by"), dict) else None
    try:
        import sys
        if TOOLS not in sys.path:
            sys.path.insert(0, TOOLS)
        import gateclass as GC
        if ff and GC.ADDR_FAIL_RE.search(ff):
            return "address", "address"
        if ff:
            line = ff if GC.FAIL_LINE_RE.match(ff) else "  FAIL  " + ff
            if GC.classify_line(line) == "log":
                return "soft", "soft:" + _norm_sig(ff.split("  ")[0])
    except Exception:       # noqa: BLE001
        pass
    try:
        if _artefact_by_design(res, card_path):
            return "by-design", "by-design"
    except Exception:       # noqa: BLE001
        pass
    if ff:
        return None, "ff:" + _norm_sig(ff)
    if bb:
        return None, "blocked:" + _norm_sig(re.sub(r"[-:]?\d+$", "", str(bb.get("device") or "")))
    return None, "status:" + str(res.get("status"))


def result_of(entry):
    """The result/1 dict beside the entry's card, written after the dispatch, or None."""
    cp = entry.get("card")
    if not cp or not entry.get("id"):
        return None
    p = os.path.join(os.path.dirname(cp), "result_%s.json" % entry["id"])
    try:
        if os.path.getmtime(p) < float(entry.get("t", 0)) - 5:
            return None
        with open(p, encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) and d.get("schema") == "result/1" else None
    except (OSError, ValueError):
        return None


def card_rows(st):
    rows = []
    for e in st.get("cards") or []:
        r = result_of(e)
        row = {"id": str(e.get("id"))[:80], "status": (r or {}).get("status", "no-result")[:20],
               "first_fail": (str((r or {}).get("first_fail"))[:200] if r and r.get("first_fail") else None),
               "class": None, "retry_of_card": e.get("retry_of_card")}
        if r and r.get("status") in ("FAIL", "BLOCKED"):
            kind, key = classify(r, e.get("card"))
            row["class"] = ("%s (explained)" % key if kind else key)[:120]
        rows.append(row)
    return rows


# ------------------------------------------------------------------------------------------------ USD estimate
def _price(prices, model):
    m = str(model or "")
    for k, v in (prices or {}).items():
        if isinstance(v, dict) and k not in ("default",) and k in m:
            return v
    if "fable" in m and isinstance((prices or {}).get("fable"), dict):
        return prices["fable"]
    return (prices or {}).get("default") or {"in": 10.0, "out": 50.0, "cache_read": 1.0, "cache_write": 20.0}


def usd_estimate(transcript_path, prices):
    """USD of the session so far: its transcript + <stem>/subagents/*.jsonl (nested agents land there too - measured
    2026-10-04 on Claude Code 2.1.281), assistant usage de-duplicated by message id. None when nothing is readable."""
    if not transcript_path:
        return None
    files = [transcript_path] + glob.glob(os.path.join(os.path.splitext(transcript_path)[0], "subagents", "*.jsonl"))
    seen, total, read_any = set(), 0.0, False
    for fp in files:
        try:
            with open(fp, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
            read_any = True
        except OSError:
            continue
        for line in lines:
            if '"usage"' not in line:
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            msg = d.get("message") if isinstance(d, dict) else None
            if not isinstance(msg, dict) or not isinstance(msg.get("usage"), dict):
                continue
            mid = msg.get("id") or d.get("uuid")
            if mid in seen:
                continue
            seen.add(mid)
            u, p = msg["usage"], _price(prices, msg.get("model"))
            total += (int(u.get("input_tokens") or 0) * p["in"] + int(u.get("output_tokens") or 0) * p["out"]
                      + int(u.get("cache_read_input_tokens") or 0) * p["cache_read"]
                      + int(u.get("cache_creation_input_tokens") or 0) * p["cache_write"]) / 1e6
    return round(total, 4) if read_any else None


# ------------------------------------------------------------------------------------------------ triggers
def evaluate(st, cfg, now=None, usd=None):
    """{'trigger', 'detail'} for the first hand-back condition that holds over the session's results, or None.
    Order: d, a, b, cap-time, cap-usd (a user question is reported before anything it may have caused)."""
    now = time.time() if now is None else now
    devs = [str(x).lower() for x in cfg.get("user_question_devices") or []]
    dp = st.get("decisions_path")
    if dp:
        n_open = open_decisions_count(dp)
        if n_open > int(st.get("decisions_open_start") or 0):
            return {"trigger": "d-user-question", "detail": "decisions_pending.json open items %d -> %d during the "
                    "session (%s)" % (int(st.get("decisions_open_start") or 0), n_open, os.path.basename(dp))}
    ids = {str(e.get("id")) for e in st.get("cards") or []}
    classes = {}
    for e in st.get("cards") or []:
        r = result_of(e)
        if not r or r.get("status") not in ("FAIL", "BLOCKED"):
            continue
        bb = r.get("blocked_by") if isinstance(r.get("blocked_by"), dict) else {}
        dev = str(bb.get("device") or "").lower()
        if r.get("status") == "BLOCKED" and any(dev == x or dev.startswith(x + ":") for x in devs):
            return {"trigger": "d-user-question", "detail": "card %s BLOCKED by %s: %s"
                    % (e.get("id"), bb.get("device"), str(bb.get("message") or "")[:200])}
        kind, key = classify(r, e.get("card"))
        if kind is None and r.get("status") == "FAIL" and e.get("retry_of_card") and str(e.get("retry_of_card")) in ids:
            return {"trigger": "a-unexplained-after-retry",
                    "detail": "card %s (the one retry of %s) FAILed again, first_fail not explained by gateclass / "
                              "addrcheck / by-design: %s" % (e.get("id"), e.get("retry_of_card"),
                                                             str(r.get("first_fail"))[:200])}
        classes.setdefault(key, []).append(str(e.get("id")))
    for key, who in classes.items():
        if len(who) >= 2:
            return {"trigger": "b-same-class-twice", "detail": "failure class `%s` in cards %s" % (key, ", ".join(who))}
    mins = (now - float(st.get("t0") or now)) / 60.0
    if mins >= float(cfg.get("cap_minutes") or 1e9):
        return {"trigger": "cap-time", "detail": "%.0f min since the assignment session started >= cap %s min"
                % (mins, cfg.get("cap_minutes"))}
    if usd is not None and usd >= float(cfg.get("cap_usd") or 1e9):
        return {"trigger": "cap-usd", "detail": "session spend %.2f USD >= cap %s USD" % (usd, cfg.get("cap_usd"))}
    return None


def _scope(ids):
    return [str(x) for x in ids if x]


def scope_match(card_ids, purpose_ids):
    for a in card_ids:
        for b in purpose_ids:
            if a == b or a.startswith(b + ".") or b.startswith(a + "."):
                return True
    return False


def _purpose_text(p):
    return " ".join([str(p.get("act") or ""), " ".join(str(x) for x in p.get("pass") or []), str(p.get("note") or "")])


def card_outside(card, purpose, cfg):
    """(c): '' or the reason this card leaves the purpose's plan."""
    import sys
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    import protocol
    ptxt = _purpose_text(purpose)
    pl = ptxt.lower()
    writes = (card.get("flags") or {}).get("write") or []
    writes = [str(g) for g in (writes if isinstance(writes, list) else [writes])]
    plan = (purpose.get("plan") or {}).get("path") if isinstance(purpose.get("plan"), dict) else None
    if plan and writes:
        pabs = plan if os.path.isabs(plan) else os.path.join(ROOT, plan)
        if protocol.path_in_globs(pabs, writes) and os.path.basename(plan).lower() not in \
                " ".join([str(purpose.get("act") or "")] + [str(x) for x in purpose.get("pass") or []]).lower():
            return "flags.write %s reaches the PLAN file %s (a plan change is judgement's)" % (writes, plan)
    def concrete(g):
        return os.path.join(ROOT, g.replace("\\", "/").replace("**", "x").replace("*", "x"))

    for g in cfg.get("protected_globs") or []:
        hits = [w for w in writes if protocol.path_in_globs(concrete(g), [w]) or protocol.path_in_globs(concrete(w), [g])]
        if not hits:
            continue
        named = g.replace("\\", "/").rstrip("*/").lower() in pl or any(
            "*" not in w and os.path.basename(w.replace("\\", "/")).lower() in pl for w in hits)
        if not named:
            return "flags.write %s reaches the protected path %s (user rule / memory limit / enforcement)" % (hits, g)
    body = " ".join(str(card.get(k) or "") for k in ("goal", "why", "note")) + " " + \
        " ".join(str(x) for x in card.get("pass") or [])
    for tok in cfg.get("memory_tokens") or []:
        for m in re.finditer(re.escape(tok), body, re.I):
            # card 148-a1-1 (fp-53): the +-60-char window stops at the token's own CLAUSE ('; ' / '. ' / newline), so a verb
            # of a neighbouring clause ("... file changed; md5 old -> new reported; ..., memory_model.json, ... unchanged",
            # task_146-a2-1.json:18) is not read as changing the limit ("unchanged" itself never matches: lookbehind)
            lo = max([body.rfind(s, 0, m.start()) + len(s) for s in ("; ", ". ", "\n") if body.rfind(s, 0, m.start()) >= 0]
                     + [max(0, m.start() - 60)])
            his = [body.find(s, m.end()) for s in ("; ", ". ", "\n") if body.find(s, m.end()) >= 0]
            win = body[lo: min(his + [m.end() + 60])].lower()
            verb = next((w for w in cfg.get("change_words") or [] if re.search(r"(?<![a-z])%s" % re.escape(w.lower()), win)),
                        None)
            if verb and tok.lower() not in pl:
                return "card text changes a memory limit: `%s` next to `%s` (%s...), and the purpose does not name it" \
                       % (tok, verb, " ".join(win.split())[:100])
    cids = _scope(list(card.get("advances") or []) + [card.get("unblocks")])
    pids = _scope(list(purpose.get("advances") or []) + [purpose.get("unblocks")])
    if pids and cids and not scope_match(cids, pids):
        return "card scope %s is disjoint from the purpose's %s" % (cids, pids)
    return ""


def _handback_msg(hb, st_path):
    return ("BLOCKED by tools/hooks/guard_session.py -> guard_assign: HANDBACK REQUIRED (%s).\n  %s\n\n"
            "User 2026-10-04 (card chat-A1): the hand-back is decided by code, not by the assignment session. Dispatch\n"
            "nothing more. Write your assign-result/1 (status HANDBACK, handback.reason = this trigger) to the `result`\n"
            "path of your assign/1 card, validate it with `py tools/protocol.py validate <path>`, and END your turn.\n"
            "The runner hands the record to a judgement session. State: %s\n"
            % (hb["trigger"], hb["detail"], _rel(st_path) if st_path else "?"))


def _rel(p):
    try:
        return os.path.relpath(p, ROOT)
    except ValueError:          # another drive (a temp dir): relpath cannot cross drives
        return p


def check_dispatch(st_path, sub, card, cpath, transcript_path=None, now=None, cfg=None):
    """(0, '') allow - the dispatch is recorded in the state; (2, text) refuse. Runs under guard_session's lock."""
    now = time.time() if now is None else now
    cfg = cfg or load_config()
    st = state_load(st_path) if st_path else None
    if st is None:
        return 2, ("BLOCKED by tools/hooks/guard_session.py -> guard_assign: no readable assignment state (ASSIGN_STATE=%r).\n"
                   "The assignment session is spawned by tools/cycle_runner.py with that file; nothing is dispatched "
                   "without it.\n" % st_path)
    if st.get("handback"):
        return 2, _handback_msg(st["handback"], st_path)

    def hand_back(trigger, detail):
        st["handback"] = {"trigger": trigger, "detail": str(detail)[:400], "t": now, "at_dispatch": sub}
        state_save(st_path, st)
        return 2, _handback_msg(st["handback"], st_path)

    def plain(text):
        st.setdefault("refusals", []).append({"t": now, "sub": sub, "why": text[:200]})
        state_save(st_path, st)
        return 2, "BLOCKED by tools/hooks/guard_session.py -> guard_assign: %s\n" % text

    if sub in MATERIAL_TYPES and card is None:
        return plain("a %s dispatch from the assignment session must be the one-line prompt `CARD <task/1 path>`." % sub)
    if card == {}:
        return plain("card %s is unreadable or not JSON - fix it and validate with `py tools/protocol.py validate`." % cpath)
    hb = evaluate(st, cfg, now, usd_estimate(transcript_path, cfg.get("prices_per_mtok")))
    if hb:
        return hand_back(hb["trigger"], hb["detail"])
    if len(st.get("cards") or []) >= int(cfg.get("backstop_cards") or 30):
        return hand_back("backstop", "%d dispatches already in this assignment session (runaway backstop %s)"
                         % (len(st.get("cards") or []), cfg.get("backstop_cards")))
    entry = {"id": "prose-%d" % (len(st.get("cards") or []) + 1), "sub": sub, "t": now, "card": None, "retry_of_card": None}
    if card:
        cids = _scope(list(card.get("advances") or []) + [card.get("unblocks")])
        if not cids:
            return plain("card %s names neither `advances` nor `unblocks` - copy the purpose's goal ids (%s) into it."
                         % (card.get("id"), _scope(list((st.get("purpose") or {}).get("advances") or [])
                                                    + [(st.get("purpose") or {}).get("unblocks")])))
        why = card_outside(card, st.get("purpose") or {}, cfg)
        if why:
            return hand_back("c-outside-purpose", "card %s: %s" % (card.get("id"), why))
        entry.update({"id": str(card.get("id")), "card": cpath, "retry_of_card": card.get("retry_of_card")})
    # every dispatch is one entry (a re-dispatch of the same card id is a second attempt: if both read a FAIL, that is
    # the same failure class twice - trigger b - which is what a second identical attempt means)
    st["cards"] = (st.get("cards") or []) + [entry]
    state_save(st_path, st)
    return 0, ""


def runner_verdict(st_path, result_path, envelope_usd=None, rc=0, cfg=None, now=None):
    """After the session: (outcome 'PURPOSE_MET'|'HANDBACK', trigger|None, detail, result dict|None). The hook's sticky
    trigger, then evaluate() with the envelope's exact cost, then what the session wrote."""
    import sys
    if TOOLS not in sys.path:
        sys.path.insert(0, TOOLS)
    import protocol
    cfg = cfg or load_config()
    st = state_load(st_path) or {}
    res, why = None, None
    try:
        with open(result_path, encoding="utf-8") as f:
            res = json.load(f)
        ok, why = protocol.validate_obj(res)
        if not ok:
            res = None
    except (OSError, ValueError) as e:
        why = "%s: %s" % (type(e).__name__, e)
    if st.get("handback"):
        return "HANDBACK", st["handback"]["trigger"], st["handback"]["detail"], res
    hb = evaluate(st, cfg, now, envelope_usd)
    if hb:
        return "HANDBACK", hb["trigger"], hb["detail"], res
    if res is None:
        if rc:
            return "HANDBACK", "session-exit", "the assignment session exited %s without a valid assign-result (%s)" \
                % (rc, why), None
        return "HANDBACK", "no-result", "no valid assign-result/1 at %s (%s)" % (result_path, why), None
    if res.get("status") == "HANDBACK":
        return "HANDBACK", "session", str((res.get("handback") or {}).get("reason") or "the session handed back"), res
    n_pass = len((st.get("purpose") or {}).get("pass") or [])
    met = {int(e.get("item")) for e in res.get("pass_evidence") or [] if e.get("met") and e.get("evidence")}
    missing = [i for i in range(n_pass) if i not in met]
    if missing:
        return "HANDBACK", "purpose-unproven", "PURPOSE_MET claimed but pass item(s) %s carry no met evidence" % missing, res
    return "PURPOSE_MET", None, "all %d pass item(s) met with evidence" % n_pass, res
