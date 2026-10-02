r"""gate_fp.py - GATE FALSE POSITIVES, BATCHED (card chat-P1 item 3; user 2026-09-28 "1~4번은 적용하도록").

Cycles 110-115 lost much of their time to a gate that refused something it should not have, and each such refusal
was repaired on the spot, inside the card that met it. This file makes the false positive a QUEUE ITEM instead: the
material session logs it with evidence, routes around it only by a form the gates already accept, and a tooling card
drains the queue in one batch when the runner says it is due (cycle_runner.gates_due item `gate-fp`).

  log   --gate <hook|checker:label> --cmd "<cmd>" --why "<file:line evidence>" --card <id> [--line "<refusal line>"]
        [--log <failing log>]
        Appends {id,t,iso,cycle,gate,cmd,first_refusal_line,why,card,log,status:"open"} to the queue. DEDUPE: an OPEN
        entry with the same gate and the same refusal line (the command when no line is given) is re-used - the card
        is added to its `cards` and no new id is made. `--why` must cite at least one file:line (evidence, not a
        feeling); exit 2 otherwise.
  drain --id <fp-n> --fixed <path:line> --selftest <name>
        Closes one entry: the fix must exist (path under the project) and the self-test must exist
        (tools/bench/<name>.py). status -> "drained".
  close --id <fp-n> --reason "<why, citing an existing path:line>"
        card 133-1: closes an entry that is NOT a false positive (a correct refusal, or superseded) - no fix exists, so
        drain does not fit. status -> "closed". Self-test: tools/bench/selftest_c133_1_gatefp_close.py.
  list  [--open]            print the queue
  due                       exit 1 when a batch drain is due (>= DUE_OPEN open, oldest >= DUE_CYCLES cycles, or one
                            entry BLOCKING a card: a result_<id>.json with blocked_by.device == "gate-fp:<fp id>")

RULE-GATE-FP (tools/hooks/guard_peer.py): a FAILING LOG named by an OPEN entry whose gate is a CHECKER (a guard_*
hook or `checker:<stage_prerun|stagekit|stagesim|stop_record|protocol|launchunit|doc_lint>[:label]`) and whose
first failure line is not a LabVIEW observation does not owe a hypothesis review - at most ONE such entry per gate
per cycle (`discharge_for_log`). A LabVIEW observation (ExecState, a STALL, a TIMEOUT, an Error List item, a COM
error) is never a checker false positive. No env bypass exists or is added; motor gate, originals protection and
bgrun deadlines are out of scope by construction (they are not checkers).

WHAT EXISTED: nothing queued false positives (grep "false positive" tools/*.py: only comments); the release forms
FIXED:/REFUTED: (guard_cycle), --retry-card (stage_prerun RETRY CAP) and the Jev ladder's our-script-bug rung stay
the ways a single refusal is answered; this queue does not replace them.
Self-test: tools/bench/selftest_chat_p1.py (log / dedupe / drain / due, RULE-GATE-FP only for checker gates).
"""
import argparse
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BENCH = os.path.join(HERE, "bench")
sys.path.insert(0, HERE)
import protocol as P  # noqa: E402

QUEUE = os.environ.get("GATE_FP_QUEUE") or os.path.join(BENCH, "gate_fp_queue.jsonl")   # env: self-tests only
DUE_OPEN = 5
DUE_CYCLES = 3
CHECKER_TOOLS = ("stage_prerun", "stagekit", "stagesim", "stop_record", "protocol", "launchunit", "doc_lint")
CHECKER_RE = re.compile(r"^(?:guard_[a-z_]+|checker:(?:%s)(?::.+)?)$" % "|".join(CHECKER_TOOLS), re.I)
# A LabVIEW OBSERVATION is never a checker's false positive: it is the machine answering.
LV_OBS_RE = re.compile(r"ExecState|OBSERVED:|^STALL:|STALL:|BGRUN TIMEOUT|Error List|errorlist|LabVIEW (?:error|returned)|"
                       r"com_error|0x8[0-9A-Fa-f]{7}|Is Broken", re.I)
CITE_RE = re.compile(r"[\w./\\-]+\.\w+:\d+")


def is_checker_gate(gate):
    return bool(CHECKER_RE.match((gate or "").strip()))


def read_queue(path=None):
    out = []
    try:
        with open(path or QUEUE, encoding="utf-8") as f:
            for ln in f:
                ln = ln.strip()
                if ln:
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def _write_queue(rows, path=None):
    path = path or QUEUE
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=True) + "\n")
    os.replace(tmp, path)


def _cycle():
    try:
        return int(P.current_cycle())
    except Exception:                    # noqa: BLE001
        return 0


def log_fp(gate, cmd, why, card, line="", log=None, path=None, cycle=None):
    """(entry, created: bool) or raises ValueError on missing evidence."""
    if not (gate or "").strip():
        raise ValueError("--gate is empty")
    if not CITE_RE.search(why or ""):
        raise ValueError("--why must cite the evidence as file:line (got %r)" % (why or "")[:120])
    key_line = (line or "").strip() or (cmd or "").strip()
    with P.file_lock((path or QUEUE) + ".lock"):
        rows = read_queue(path)
        for r in rows:
            if r.get("status") == "open" and r.get("gate") == gate and (r.get("first_refusal_line") or r.get("cmd")) == key_line:
                cards = r.setdefault("cards", [r.get("card")])
                if card and card not in cards:
                    cards.append(card)
                if log and not r.get("log"):
                    r["log"] = log
                _write_queue(rows, path)
                return r, False
        n = 1 + max([int(str(r.get("id", "fp-0")).split("-")[-1]) for r in rows if str(r.get("id", "")).startswith("fp-")]
                    or [0])
        e = {"id": "fp-%d" % n, "t": time.time(), "iso": time.strftime("%Y-%m-%d %H:%M:%S"),
             "cycle": _cycle() if cycle is None else int(cycle), "gate": gate.strip(), "cmd": (cmd or "")[:1000],
             "first_refusal_line": key_line[:400], "why": (why or "")[:600], "card": card, "cards": [card],
             "log": log, "checker": is_checker_gate(gate), "status": "open", "discharges": []}
        rows.append(e)
        _write_queue(rows, path)
        return e, True


def drain(fp_id, fixed, selftest, path=None):
    """(entry, None) or (None, why)."""
    m = re.match(r"^(.+?):(\d+)$", (fixed or "").strip())
    if not m:
        return None, "--fixed must be <path>:<line>"
    fp = m.group(1) if os.path.isabs(m.group(1)) else os.path.join(ROOT, m.group(1))
    if not os.path.isfile(fp):
        return None, "--fixed path does not exist: %s" % m.group(1)
    st = selftest if selftest.endswith(".py") else selftest + ".py"
    if not (os.path.isfile(os.path.join(BENCH, st)) or os.path.isfile(os.path.join(ROOT, st))):
        return None, "--selftest %s not found under tools/bench" % selftest
    with P.file_lock((path or QUEUE) + ".lock"):
        rows = read_queue(path)
        for r in rows:
            if r.get("id") == fp_id:
                if r.get("status") != "open":
                    return None, "%s is already %s" % (fp_id, r.get("status"))
                r.update({"status": "drained", "fixed": fixed, "selftest": selftest, "drained_t": time.time(),
                          "drained_iso": time.strftime("%Y-%m-%d %H:%M:%S")})
                _write_queue(rows, path)
                return r, None
    return None, "no entry %s" % fp_id


def close(fp_id, reason, path=None):
    """card 133-1 (PD276(d), PD282(b)): close an OPEN entry that is NOT a false positive (the refusal was CORRECT, or the
    entry is superseded) - no fix, no self-test. `reason` must cite at least one EXISTING <path>:<line> (the review / log
    that decided it). status -> "closed". (entry, None) or (None, why)."""
    cites = CITE_RE.findall(reason or "")
    real = [c for c in cites if os.path.isfile(c.rsplit(":", 1)[0] if os.path.isabs(c.rsplit(":", 1)[0])
                                               else os.path.join(ROOT, c.rsplit(":", 1)[0]))]
    if not real:
        return None, "--reason must cite an existing <path>:<line> (got %s)" % (cites or "none")
    with P.file_lock((path or QUEUE) + ".lock"):
        rows = read_queue(path)
        for r in rows:
            if r.get("id") == fp_id:
                if r.get("status") != "open":
                    return None, "%s is already %s" % (fp_id, r.get("status"))
                r.update({"status": "closed", "close_reason": reason.strip()[:600], "closed_t": time.time(),
                          "closed_iso": time.strftime("%Y-%m-%d %H:%M:%S")})
                _write_queue(rows, path)
                return r, None
    return None, "no entry %s" % fp_id


def note(fp_id, text, path=None):
    """card 131-2: attach a NOTE to an entry (why it stays open, who owns it). (entry, None) or (None, why). Status is
    not changed; a later note replaces the earlier one."""
    if not (text or "").strip():
        return None, "--text is empty"
    with P.file_lock((path or QUEUE) + ".lock"):
        rows = read_queue(path)
        for r in rows:
            if r.get("id") == fp_id:
                r.update({"note": text.strip()[:600], "note_iso": time.strftime("%Y-%m-%d %H:%M:%S")})
                _write_queue(rows, path)
                return r, None
    return None, "no entry %s" % fp_id


def blocking_ids(cards_dir=None):
    """fp ids named by a result/1 card's blocked_by.device == 'gate-fp:<id>'."""
    d = cards_dir or P.CARDS_DIR
    out = set()
    try:
        names = os.listdir(d)
    except OSError:
        return out
    for fn in names:
        if not (fn.startswith("result_") and fn.endswith(".json")):
            continue
        try:
            with open(os.path.join(d, fn), encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        dev = str(((r or {}).get("blocked_by") or {}).get("device") or "") if isinstance(r, dict) else ""
        if dev.startswith("gate-fp:"):
            out.add(dev.split(":", 1)[1].strip())
    return out


def due(path=None, cards_dir=None, cycle=None):
    """(due: bool, detail) - the runner's gates_due item `gate-fp`."""
    rows = [r for r in read_queue(path) if r.get("status") == "open"]
    if not rows:
        return False, "gate-fp queue: 0 open"
    cur = _cycle() if cycle is None else int(cycle)
    oldest = min(int(r.get("cycle") or cur) for r in rows)
    blk = sorted(blocking_ids(cards_dir) & set(r.get("id") for r in rows))
    why = []
    if len(rows) >= DUE_OPEN:
        why.append("%d open (>= %d)" % (len(rows), DUE_OPEN))
    if cur - oldest >= DUE_CYCLES:
        why.append("oldest from cycle %d, now %d (>= %d cycles)" % (oldest, cur, DUE_CYCLES))
    if blk:
        why.append("blocking a card: %s" % ", ".join(blk))
    detail = "gate-fp queue: %d open (%s)%s" % (len(rows), ", ".join(r["id"] for r in rows[:8]),
                                                 ("; DUE: " + "; ".join(why) + " - spend ONE tooling card to drain it")
                                                 if why else "")
    return bool(why), detail


def _names_log(entry, log_path):
    b = os.path.basename(log_path or "")
    if not b:
        return False
    for k in ("log", "cmd", "first_refusal_line", "why"):
        v = str(entry.get(k) or "")
        if v and (os.path.basename(v) == b or b in v):
            return True
    return False


def discharge_for_log(log_path, first_line, path=None, cycle=None, record=True):
    """(entry, None) when an OPEN checker entry names this failing log and may discharge it this cycle, else
    (None, why). At most ONE entry per gate per cycle discharges (re-discharging the same entry is the same one)."""
    cur = _cycle() if cycle is None else int(cycle)
    with P.file_lock((path or QUEUE) + ".lock"):
        rows = read_queue(path)
        hits = [r for r in rows if r.get("status") == "open" and _names_log(r, log_path)]
        if not hits:
            return None, "no open gate-fp entry names %s" % os.path.basename(log_path or "")
        if LV_OBS_RE.search(first_line or ""):
            return None, "the failure line is a LabVIEW observation, not a checker's false positive"
        for r in hits:
            if not is_checker_gate(r.get("gate")):
                continue
            used = [x for x in rows if x is not r and x.get("gate") == r.get("gate")
                    and any(int(d.get("cycle") or -1) == cur for d in x.get("discharges") or [])]
            if used:
                return None, "gate %s already discharged %s in cycle %d (one per gate per cycle)" % (
                    r.get("gate"), used[0].get("id"), cur)
            if record:
                ds = r.setdefault("discharges", [])
                if not any(d.get("log") == os.path.basename(log_path) and int(d.get("cycle") or -1) == cur for d in ds):
                    ds.append({"cycle": cur, "log": os.path.basename(log_path), "t": time.time()})
                    _write_queue(rows, path)
            return r, None
        return None, "entry %s names the log but its gate %r is not a checker" % (hits[0].get("id"), hits[0].get("gate"))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd")
    lg = sub.add_parser("log")
    lg.add_argument("--gate", required=True)
    lg.add_argument("--cmd", dest="command", required=True)
    lg.add_argument("--why", required=True)
    lg.add_argument("--card", required=True)
    lg.add_argument("--line", default="")
    lg.add_argument("--log", default=None)
    dr = sub.add_parser("drain")
    dr.add_argument("--id", required=True)
    dr.add_argument("--fixed", required=True)
    dr.add_argument("--selftest", required=True)
    nt = sub.add_parser("note")
    nt.add_argument("--id", required=True)
    nt.add_argument("--text", required=True)
    cl = sub.add_parser("close")
    cl.add_argument("--id", required=True)
    cl.add_argument("--reason", required=True)
    ls = sub.add_parser("list")
    ls.add_argument("--open", action="store_true")
    sub.add_parser("due")
    a = ap.parse_args(argv)
    if a.cmd == "close":
        e, why = close(a.id, a.reason)
        print(("CLOSED %s" % e["id"]) if e else "REFUSED: %s" % why)
        return 0 if e else 2
    if a.cmd == "note":
        e, why = note(a.id, a.text)
        print(("NOTED %s" % e["id"]) if e else "REFUSED: %s" % why)
        return 0 if e else 2
    if a.cmd == "log":
        try:
            e, new = log_fp(a.gate, a.command, a.why, a.card, a.line, a.log)
        except ValueError as ex:
            print("REFUSED: %s" % ex)
            return 2
        print("%s %s gate=%s checker=%s (queue %s)" % ("LOGGED" if new else "DEDUPED", e["id"], e["gate"], e["checker"],
                                                       P._rel(QUEUE)))
        return 0
    if a.cmd == "drain":
        e, why = drain(a.id, a.fixed, a.selftest)
        print(("DRAINED %s (%s, %s)" % (e["id"], a.fixed, a.selftest)) if e else "REFUSED: %s" % why)
        return 0 if e else 2
    if a.cmd == "list":
        for r in read_queue():
            if a.open and r.get("status") != "open":
                continue
            print("%s %-7s cycle %s gate %s card %s | %s" % (r.get("id"), r.get("status"), r.get("cycle"), r.get("gate"),
                                                             r.get("card"), str(r.get("first_refusal_line"))[:100]))
            if r.get("note"):
                print("    note: %s" % r["note"])
        return 0
    if a.cmd == "due":
        d, why = due()
        print(("DUE " if d else "ok ") + why)
        return 1 if d else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
