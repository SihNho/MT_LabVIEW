"""Self-test for tools/card_clock.py (card 129-3, brief_129-3.md s2). Temp fixtures, mtimes set with os.utime.
Prediction: 4/4 - (a) 128-5 copy MISMATCH with both reasons (i)+(ii); (b) 129-1 copy OK; (c) no-bind UNMEASURED;
(d) honest-short (measured < 0.8*budget, first_fail not about budget) OK.
"""
import datetime as dt, json, os, shutil, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import card_clock  # noqa: E402
from protocol import make_result, result_line  # noqa: E402

CARDS = os.path.join(ROOT, "tools", "bench", "cards")
LOG = os.path.join(CARDS, "guard_card.log")


def real_bind(cid):
    t, n = card_clock.find_bind(LOG, cid)
    with open(LOG, encoding="utf-8", errors="replace") as f:
        return f.readlines()[n - 1]


def ts(s):
    return dt.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").timestamp()


tmp = tempfile.mkdtemp(prefix="card_clock_")
ok = fail = 0
try:
    log = os.path.join(tmp, "guard_card.log")
    with open(log, "w", encoding="utf-8") as f:
        f.write("2026-10-02 00:00:00 | ALLOW material x | unrelated line\n")
        f.write(real_bind("128-5"))
        f.write(real_bind("129-1"))
        f.write("2026-10-02 02:00:00 | ALLOW material z | BOUND agent z (material) -> tools\\bench\\cards\\task_t-d.json (id t-d)\n")
    for cid in ("128-5", "129-1"):
        shutil.copy(os.path.join(CARDS, "task_%s.json" % cid), tmp)
        shutil.copy(os.path.join(CARDS, "result_%s.json" % cid), tmp)
    os.utime(os.path.join(tmp, "result_128-5.json"), (ts("2026-10-02 00:49:02"),) * 2)
    m = os.path.getmtime(os.path.join(CARDS, "result_129-1.json"))
    os.utime(os.path.join(tmp, "result_129-1.json"), (m, m))
    base = {"schema": "result/1", "status": "FAIL", "gates": {"pass": 1, "fail": 1}, "blocked_by": None,
            "artefacts": [], "facts": [], "open": [], "note": ""}
    json.dump(dict(base, id="t-c", first_fail="x", cost={"usd": None, "minutes": 3, "labview_runs": 0}),
              open(os.path.join(tmp, "result_t-c.json"), "w"))
    json.dump({"schema": "task/1", "id": "t-c", "budget": {"minutes": 20}}, open(os.path.join(tmp, "task_t-c.json"), "w"))
    json.dump(dict(base, id="t-d", first_fail="gate G3 wires mismatch 4 != 5",
                   cost={"usd": None, "minutes": 6, "labview_runs": 0}), open(os.path.join(tmp, "result_t-d.json"), "w"))
    json.dump({"schema": "task/1", "id": "t-d", "budget": {"minutes": 50}}, open(os.path.join(tmp, "task_t-d.json"), "w"))
    os.utime(os.path.join(tmp, "result_t-d.json"), (ts("2026-10-02 02:06:00"),) * 2)
    cases = [("a 128-5 copy", "result_128-5.json", "CLOCK-MISMATCH", ["(i)", "(ii)"]),
             ("b 129-1 copy", "result_129-1.json", "OK", []),
             ("c no bind", "result_t-c.json", "CLOCK-UNMEASURED", ["no bind line"]),
             ("d honest short", "result_t-d.json", "OK", [])]
    for label, fn, want, subs in cases:
        line, verdict, rc = card_clock.clock(os.path.join(tmp, fn), log, tmp)
        good = verdict == want and rc == {"OK": 0, "CLOCK-MISMATCH": 1, "CLOCK-UNMEASURED": 2}[want] \
            and all(s in line for s in subs)
        ok += good
        fail += not good
        print("%s %s | %s" % ("PASS" if good else "FAIL", label, line))
    # (e) card 129-8: main() on a result without cost.minutes (result_129-5.json copy) -> exit 2 + a parseable SKIP RESULT line
    import contextlib, io
    from protocol import RESULT_PREFIX, validate_obj  # noqa: E402
    r5 = json.load(open(os.path.join(CARDS, "result_129-5.json"), encoding="utf-8"))
    (r5.get("cost") or {}).pop("minutes", None)
    json.dump(r5, open(os.path.join(tmp, "result_129-5.json"), "w", encoding="utf-8"))
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            rc = card_clock.main([os.path.join(tmp, "result_129-5.json"), "--log", log, "--cards", tmp])
        rl = [x for x in buf.getvalue().splitlines() if x.startswith(RESULT_PREFIX)]
        d = json.loads(rl[-1][len(RESULT_PREFIX):]) if rl else None
        good = rc == 2 and d is not None and validate_obj(d)[0] and d["status"] == "SKIP" \
            and str(d.get("first_fail", "")).startswith("CLOCK-UNMEASURED: ") and "no cost.minutes" in d["first_fail"]
        why = d
    except Exception as e:  # noqa: BLE001 - the pre-fix main() raised here
        good, why = False, "raised %r" % e
    ok += good
    fail += not good
    print("%s e main() no cost.minutes -> exit 2 + SKIP RESULT | %s" % ("PASS" if good else "FAIL", why))
finally:
    shutil.rmtree(tmp, ignore_errors=True)
print("SELFTEST card_clock %d/%d" % (ok, fail))
print(result_line(make_result(ok, fail, None if fail == 0 else "selftest_card_clock: %d failed" % fail)))
sys.exit(0 if fail == 0 else 1)
