r"""retro_due.py - is a RETROSPECTIVE due at the end of this cycle? (card chat-P1 item 2b; user 2026-09-28 "1~4번은
적용하도록"). Cycles 110-115 paid a retrospective every cycle (~9 peer reviews per cycle in all); the retrospective now
runs every THIRD cycle, or earlier when there is a reason:

  DUE when any of
    (a) >= EVERY_N (3) cycle cards `tools/bench/cards/cycle_<n>.json` were written after the newest ANSWERED
        retrospective (guard_cycle.newest_retrospective - one definition, never re-derived here);
    (b) THIS cycle has no PASS result/1 card with a claudeDev `.vi` artefact (a cycle that delivered no saved build
        step is exactly the cycle whose structure needs reviewing);
    (c) tools/violations.py shows a slug ONE occurrence below its threshold (threshold >= 2), counting only the
        occurrences newer than that slug's newest decision block in docs/violation-decisions.md (a decided slug with
        no fresh occurrence is not "near"; see near_threshold()).

  py tools/retro_due.py --cycle N            exit 1 = DUE (reasons printed), 0 = not due
  py tools/retro_due.py --cycle N --close    closes the session WITHOUT a retrospective when not due: exit 0 and one
                                             `CLOSED` record in tools/bench/retro_due.jsonl. When DUE it closes
                                             nothing, exit 1 - run the retrospective. `tools/hooks/guard_bash.py`
                                             RETRO_RE matches this command, so next_gate (next.json written first) and
                                             the session close (guard_session.mark_retro_done) hold exactly as for
                                             `retrospective.py`.
The runner re-checks it after the session (cycle_runner.retro_fallback): DUE and no retrospective archived in the
cycle's window -> it runs the retrospective itself, synchronously, like land_retrospective.

WHAT EXISTED: guard_cycle.newest_retrospective / CYCLE_BUILD_BUDGET (the backstop, raised 10 -> 30 builds and 8 -> 24 h
by this card), violations.scan/decisions/threshold, cycle_runner.retro_slugs_in_window. Nothing decided "due".
Self-test: tools/bench/selftest_chat_p1.py (due / not-due / --close).
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
sys.path.insert(0, os.path.join(HERE, "hooks"))
import protocol as P  # noqa: E402

EVERY_N = 3
RECORD = os.environ.get("RETRO_DUE_RECORD") or os.path.join(BENCH, "retro_due.jsonl")     # env: self-tests only
CLAUDEDEV_RE = re.compile(r"claudeDev", re.I)


def newest_answered_retro(peer_dir=None):
    """(path, stamp) | None - guard_cycle.newest_retrospective with its PEER pointed at peer_dir."""
    import guard_cycle as GC
    old = GC.PEER
    if peer_dir:
        GC.PEER = peer_dir
    try:
        return GC.newest_retrospective()
    finally:
        GC.PEER = old


def cycle_cards(cards_dir):
    out = []
    try:
        for fn in os.listdir(cards_dir):
            m = re.match(r"^cycle_(\d+)\.json$", fn)
            if m:
                p = os.path.join(cards_dir, fn)
                out.append((int(m.group(1)), os.path.getmtime(p), p))
    except OSError:
        pass
    return sorted(out)


def delivered(cycle, cards_dir):
    """[result ids] of PASS result/1 cards written since cycle_<cycle>.json with a claudeDev .vi artefact."""
    cc = [c for c in cycle_cards(cards_dir) if c[0] == cycle]
    t0 = cc[0][1] if cc else 0.0
    out = []
    try:
        names = os.listdir(cards_dir)
    except OSError:
        return out
    for fn in names:
        if not (fn.startswith("result_") and fn.endswith(".json")):
            continue
        p = os.path.join(cards_dir, fn)
        try:
            if os.path.getmtime(p) < t0:
                continue
            with open(p, encoding="utf-8") as f:
                r = json.load(f)
        except (OSError, ValueError):
            continue
        if not isinstance(r, dict) or r.get("status") != "PASS":
            continue
        if any(CLAUDEDEV_RE.search(str(a.get("path") or "")) and str(a.get("path") or "").lower().endswith(".vi")
               for a in r.get("artefacts") or [] if isinstance(a, dict)):
            out.append(r.get("id") or fn)
    return sorted(out)


def near_threshold():
    """[(slug, fresh occurrences, threshold)] - slugs one occurrence below their threshold (threshold >= 2), counting
    only retrospectives newer than the slug's newest decision block. The mechanical reading of the brief's
    "violations.py shows a slug at threshold-1": an ANSWERED slug is re-opened by one fresh occurrence (violations.py
    main), so counting all-time hits would make every answered slug permanently "near" and the retrospective due every
    cycle; the fresh count is the one that walks toward a new DUE."""
    import violations as VI
    hits, _loss = VI.scan()
    dec = VI.decisions()
    out = []
    for slug, files in hits.items():
        th = VI.threshold(slug)
        if th < 2:
            continue
        fresh = [f for f in files if VI._retro_stamp(f) > dec.get(slug, "")]
        if len(fresh) == th - 1:
            out.append((slug, len(fresh), th))
    return sorted(out)


def check(cycle, cards_dir=None, peer_dir=None, violations=True):
    """(due: bool, reasons: [str], facts: dict)."""
    cards_dir = cards_dir or P.CARDS_DIR
    retro = newest_answered_retro(peer_dir)
    since = [c for c in cycle_cards(cards_dir) if retro is None or c[1] > retro[1]]
    reasons = []
    if len(since) >= EVERY_N:
        reasons.append("(a) %d cycle card(s) since the newest answered retrospective %s (every %d)" % (
            len(since), os.path.basename(retro[0]) if retro else "(none)", EVERY_N))
    dl = delivered(cycle, cards_dir)
    if not dl:
        reasons.append("(b) cycle %d has no PASS result/1 with a claudeDev .vi artefact" % cycle)
    near = []
    if violations:
        try:
            near = near_threshold()
        except Exception as e:           # noqa: BLE001 - fail toward DUE: an unreadable tally is not "fine"
            reasons.append("(c) violations tally unreadable: %s" % e)
        if near:
            reasons.append("(c) slug(s) one below threshold: %s" % ", ".join("%s %d/%d" % x for x in near))
    facts = {"cycle": cycle, "since_retro": [c[0] for c in since], "retro": P._rel(retro[0]) if retro else None,
             "delivered": dl, "near": [list(x) for x in near]}
    return bool(reasons), reasons, facts


def _record(d):
    try:
        with open(RECORD, "a", encoding="utf-8") as f:
            f.write(json.dumps(d, ensure_ascii=True) + "\n")
    except OSError:
        pass


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cycle", type=int, required=True)
    ap.add_argument("--close", action="store_true")
    ap.add_argument("--cards-dir", default="")
    ap.add_argument("--peer-dir", default="")
    a = ap.parse_args(argv)
    due, reasons, facts = check(a.cycle, a.cards_dir or None, a.peer_dir or None)
    for r in reasons:
        print("DUE  %s" % r)
    if not due:
        print("NOT DUE: %d cycle card(s) since the newest retrospective (%s), delivered %s, no slug near threshold" % (
            len(facts["since_retro"]), facts["retro"], facts["delivered"]))
    if a.close:
        if due:
            print("NOT CLOSED: the retrospective is due - run `py tools/bgrun.py --max-min 10 --log tools/bench/retro.log "
                  "-- py tools/retrospective.py --cycle %d`" % a.cycle)
            _record(dict(facts, t=time.time(), iso=time.strftime("%Y-%m-%d %H:%M:%S"), due=True, closed=False,
                         reasons=reasons))
            return 1
        _record(dict(facts, t=time.time(), iso=time.strftime("%Y-%m-%d %H:%M:%S"), due=False, closed=True))
        print("CLOSED cycle %d without a retrospective (not due) - record %s" % (a.cycle, P._rel(RECORD)))
        return 0
    return 1 if due else 0


if __name__ == "__main__":
    sys.exit(main())
