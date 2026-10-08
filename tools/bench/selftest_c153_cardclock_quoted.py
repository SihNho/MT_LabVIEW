# ---
# labview: none
# hardware: none
# ---
r"""selftest_c153_cardclock_quoted - card 153-b2-1 (gate-fp fp-72, docs/d1/ring-p4d.md PD370(d)): card_clock's CITE ignores QUOTED
text. PRIOR ART: tools/bench/selftest_card_clock.py (5 cases, NOT edited; same temp-fixture shape: a bind line in a temp log, result mtime
set with os.utime). Offline, stdlib + card_clock; writes only a temp dir.
PREDICTION:
  Q1 'min slot' quoted in blocked_by.message (fp-72's text), measured 10 < 0.8*90 -> OK (the old json.dumps + CITE text matched it);
  Q2 an UNQUOTED 'budget spent' in blocked_by.message, measured 10 -> CLOCK-MISMATCH (i) (unchanged);
  Q3 an apostrophe "card's budget wasn't" in first_fail -> MISMATCH (i) (an apostrophe quotes nothing);
  Q4 "minutes" in double quotes / `timeout` in backticks only -> OK;
  Q5 every result_*.json in tools/bench/cards: old match == new match, except files whose ONLY CITE hits sit inside a quoted span.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/selftest_c153_cardclock_quoted.log -- py -u tools/bench/selftest_c153_cardclock_quoted.py"""
import datetime as dt, glob, json, os, re, shutil, sys, tempfile                   # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import card_clock as C                                                              # noqa: E402
from protocol import make_result, result_line                                      # noqa: E402
N = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, detail=""):
    N["pass" if ok else "fail"] += 1
    if not ok and N["first"] is None:
        N["first"] = label
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


def old_cite(res):                                                                  # card_clock.py before card 153-b2-1 (md5 85b9ae7a, line 55)
    return " ".join(str(x) for x in (res.get("first_fail"), json.dumps(res.get("blocked_by"))) if x)


tmp = tempfile.mkdtemp(prefix="cc_quoted_")
try:
    log = os.path.join(tmp, "guard_card.log")
    T0 = dt.datetime(2026, 10, 9, 4, 54, 41)
    cases = {
        "q1": ("SA pass A replays to its end: op 187 refused (tunnel naming UNMEASURED)",
               {"device": "stagesim", "message": "tools/stagesim.py:1892 wire {'uid': 30179, 'term': 'outer'} -> {'uid': 29879, 'term': "
                "'index'}: source 'min slot' on a LoopTunnel - UNMEASURED tunnel naming for that owner class (card 131-1)"}, "OK", []),
        "q2": ("x", {"device": "stagesim", "message": "budget spent on op 187"}, "CLOCK-MISMATCH", ["(i)"]),
        "q3": ("the card's budget wasn't enough", None, "CLOCK-MISMATCH", ["(i)"]),
        "q4": ('gate G3 named "minutes" and `timeout` wrong', {"device": "x", "message": "term 'min' unwired"}, "OK", []),
    }
    with open(log, "w", encoding="utf-8") as f:
        for cid in cases:
            f.write("%s | ALLOW material a | BOUND agent a (material) -> tools\\bench\\cards\\task_%s.json (id %s)\n" % (T0.strftime("%Y-%m-%d %H:%M:%S"), cid, cid))
    base = {"schema": "result/1", "status": "BLOCKED", "gates": {"pass": 1, "fail": 1}, "artefacts": [], "facts": [], "open": [], "note": "",
            "cost": {"usd": None, "minutes": 10, "labview_runs": 0}}
    for cid, (ff, bb, want, subs) in cases.items():
        p = os.path.join(tmp, "result_%s.json" % cid)
        json.dump(dict(base, id=cid, first_fail=ff, blocked_by=bb), open(p, "w", encoding="utf-8"))
        json.dump({"schema": "task/1", "id": cid, "budget": {"minutes": 90}}, open(os.path.join(tmp, "task_%s.json" % cid), "w"))
        t = (T0 + dt.timedelta(minutes=10)).timestamp()
        os.utime(p, (t, t))
        line, verdict, rc = C.clock(p, log, tmp)
        was = bool(C.CITE.search(old_cite(dict(first_fail=ff, blocked_by=bb))))
        gate("Q{0} {1} -> {2} (old CITE text matched: {3})".format(cid[1], cid, want, was),
             verdict == want and rc == {"OK": 0, "CLOCK-MISMATCH": 1}[want] and all(s in line for s in subs), line)
    gate("Q1b fp-72's text DID match the old CITE text (the false positive is reproduced)",
         bool(C.CITE.search(old_cite({"first_fail": cases["q1"][0], "blocked_by": cases["q1"][1]}))))
    diff, bad = [], []
    files = sorted(glob.glob(os.path.join(ROOT, "tools", "bench", "cards", "result_*.json")))
    for p in files:
        try:
            res = json.load(open(p, encoding="utf-8"))
        except Exception:                                                           # noqa: BLE001
            continue
        if not isinstance(res, dict):
            continue
        o, n = bool(C.CITE.search(old_cite(res))), bool(C.CITE.search(C.cite_text(res)))
        if o != n:
            raw = " ".join([str(res.get("first_fail") or "")] + list(C._strings(res.get("blocked_by"))))
            quoted_hit = any(C.CITE.search(m.group(0)) for m in C.QUOTED.finditer(raw))
            diff.append((os.path.basename(p), o, n))
            if n or not quoted_hit:
                bad.append(os.path.basename(p))
    gate("Q5 {0} stored result files: old == new CITE match except quoted-only hits ({1} differ: {2}); bad {3}".format(
        len(files), len(diff), diff[:8], bad), not bad, diff)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("=== selftest_c153_cardclock_quoted: {0} pass / {1} fail".format(N["pass"], N["fail"]), flush=True)
print(result_line(make_result(N["pass"], N["fail"], N["first"])), flush=True)
sys.exit(1 if N["fail"] else 0)
