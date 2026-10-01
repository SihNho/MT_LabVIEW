"""card_clock.py - measure a card's minutes from the machine's record and flag false budget/minutes claims.

Card 129-3 (brief_129-3.md s1; docs/violation-decisions.md 2026-10-02 01:01, retrospective cycle 128
inference-over-measurement: card 128-5 claimed 45 min and 'budget spent' after ~8 min).
Prior art checked: no existing clock/minutes checker in tools/ (protocol.py validates schema only).

measured = result-file mtime - FIRST 'BOUND agent ... (id <id>)' line of guard_card.log, minutes.
Verdicts: CLOCK-MISMATCH (exit 1) when (i) first_fail/blocked_by cites budget/minutes while measured < 0.8*budget,
or (ii) claimed > measured + max(5, 0.25*measured); CLOCK-UNMEASURED (exit 2) when no bind line, no task card or no
cost.minutes; else OK (exit 0). Prints one CLOCK line and one RESULT line. Stdlib only (+ protocol.result_line).
Usage: py tools/card_clock.py <result_X.json> [--log <guard_card.log>] [--cards <dir>]
"""
import argparse, datetime as dt, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
from protocol import make_result, result_line  # noqa: E402

CITE = re.compile(r"budget|minute|\bmin\b|time.?out|deadline", re.I)


def find_bind(log, cid):
    pat = re.compile(r"^(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d) \|.*BOUND agent .*\(id " + re.escape(cid) + r"\)\s*$")
    if not os.path.isfile(log):
        return None, None
    with open(log, encoding="utf-8", errors="replace") as f:
        for n, line in enumerate(f, 1):
            m = pat.match(line.rstrip("\r\n"))
            if m:
                return dt.datetime.strptime(m.group(1), "%Y-%m-%d %H:%M:%S"), n
    return None, None


def clock(result_path, log, cards):
    res = json.load(open(result_path, encoding="utf-8"))
    cid = str(res.get("id"))
    bound, n = find_bind(log, cid)
    written = dt.datetime.fromtimestamp(os.path.getmtime(result_path))
    claimed = (res.get("cost") or {}).get("minutes")
    budget = None
    tp = os.path.join(cards, "task_%s.json" % cid)
    if os.path.isfile(tp):
        budget = (json.load(open(tp, encoding="utf-8")).get("budget") or {}).get("minutes")
    measured = None if bound is None else round((written - bound).total_seconds() / 60.0, 1)
    reasons = []
    if bound is None:
        reasons.append("no bind line for id %s in %s" % (cid, os.path.basename(log)))
    if budget is None:
        reasons.append("no task card / budget.minutes (%s)" % os.path.basename(tp))
    if claimed is None:
        reasons.append("no cost.minutes")
    if reasons:
        verdict, rc = "CLOCK-UNMEASURED", 2
    else:
        cite = " ".join(str(x) for x in (res.get("first_fail"), json.dumps(res.get("blocked_by"))) if x)
        if CITE.search(cite) and measured < 0.8 * budget:
            reasons.append("(i) failure text cites budget/minutes but measured %.1f < 0.8*budget %.1f" % (measured, 0.8 * budget))
        if claimed > measured + max(5.0, 0.25 * measured):
            reasons.append("(ii) claimed %s > measured %.1f + %.1f" % (claimed, measured, max(5.0, 0.25 * measured)))
        verdict, rc = ("CLOCK-MISMATCH", 1) if reasons else ("OK", 0)
    line = "CLOCK id=%s bound=%s (%s:%s) written=%s measured=%s claimed=%s budget=%s verdict=%s reason=%s" % (
        cid, bound.strftime("%H:%M:%S") if bound else "-", os.path.basename(log), n if n else "-",
        written.strftime("%H:%M:%S"), measured if measured is not None else "-", claimed, budget, verdict,
        "; ".join(reasons) if reasons else "-")
    return line, verdict, rc


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("result")
    ap.add_argument("--log", default=os.path.join(ROOT, "tools", "bench", "cards", "guard_card.log"))
    ap.add_argument("--cards", default=os.path.join(ROOT, "tools", "bench", "cards"))
    a = ap.parse_args(argv)
    line, verdict, rc = clock(a.result, a.log, a.cards)
    print(line)
    if verdict == "CLOCK-UNMEASURED":       # card 129-8: was status BLOCKED, which result-line/1 does not allow -> raised
        print(result_line(make_result(0, 0, "CLOCK-UNMEASURED: " + line.split(" reason=", 1)[-1], status="SKIP")))
        return rc
    status = {"OK": "PASS", "CLOCK-MISMATCH": "FAIL"}[verdict]
    print(result_line(make_result(1 if rc == 0 else 0, 0 if rc == 0 else 1,
                                  None if rc == 0 else verdict, status=status)))
    return rc


if __name__ == "__main__":
    sys.exit(main())
