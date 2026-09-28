r"""run_mode.py - PERFORMANCE vs ECONOMY runner mode from the WEEKLY usage (user, 2026-09-28 15:4x):
"50% 초과시, 적용 전 모델 (미리 처리하지 않는 기존 방침 = 절약모드) … 보고 후 절약모드로 러너. 50% 미만: 적용 후 모델
(퍼포먼스 모드)" · "주간 사용량 기준. 2~4는 절약모드에서도 키고. 고정 수치로 할 것 … 나중에 기준은 얼마든지 변경 가능".

  performance : weekly all-models usage <= threshold -> the pipeline (acceleration item 1) is allowed: 2 live cards.
  economy     : weekly usage  > threshold, OR the mode file is missing/unreadable/older than stale_min
                -> ONE live card at a time (no prep card beside a LabVIEW card). Items 2-4 stay on in BOTH modes.

The runner cannot read plan usage itself (only the desktop app's session tools can), so the MAIN CHAT writes the
file at every 30-min tick:  py tools/run_mode.py write --weekly <percentUsed of "Weekly · all models">
Readers (guard_session, cycle_runner):  run_mode.effective() -> ("performance"|"economy", reason)
Threshold and staleness live in tools/bench/run_mode_config.json so the user can change them without code.
    py tools/run_mode.py get        # prints the effective mode
"""
import json, os, sys, time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BENCH = os.path.join(ROOT, "tools", "bench")
MODE_FILE = os.path.join(BENCH, "run_mode.json")
CONFIG_FILE = os.path.join(BENCH, "run_mode_config.json")
DEFAULT_CONFIG = {"threshold_pct": 50, "stale_min": 90, "basis": "Weekly · all models"}


def config():
    try:
        c = json.load(open(CONFIG_FILE, encoding="utf-8"))
        return dict(DEFAULT_CONFIG, **c)
    except Exception:
        return dict(DEFAULT_CONFIG)


def effective(now=None):
    c = config()
    try:
        m = json.load(open(MODE_FILE, encoding="utf-8"))
    except Exception:
        return "economy", "no readable %s (fail-safe)" % os.path.basename(MODE_FILE)
    age = ((now or time.time()) - float(m.get("t", 0))) / 60.0
    if age > float(c["stale_min"]):
        return "economy", "mode file %.0f min old > %s (fail-safe)" % (age, c["stale_min"])
    pct = float(m.get("weekly_pct", 101))
    mode = "performance" if pct <= float(c["threshold_pct"]) else "economy"
    return mode, "weekly %.0f%% vs threshold %s%% (written %.0f min ago)" % (pct, c["threshold_pct"], age)


def write(weekly_pct):
    prev = None
    try:
        prev = json.load(open(MODE_FILE, encoding="utf-8")).get("mode")
    except Exception:
        pass
    c = config()
    mode = "performance" if float(weekly_pct) <= float(c["threshold_pct"]) else "economy"
    rec = {"schema": "run_mode/1", "t": time.time(), "iso": time.strftime("%Y-%m-%d %H:%M:%S"),
           "weekly_pct": float(weekly_pct), "threshold_pct": c["threshold_pct"], "mode": mode}
    tmp = MODE_FILE + ".tmp"
    json.dump(rec, open(tmp, "w", encoding="utf-8"), indent=1)
    os.replace(tmp, MODE_FILE)
    with open(os.path.join(BENCH, "run_mode.log"), "a", encoding="utf-8") as f:
        f.write("RUN-MODE | %s | weekly %s%% | %s%s\n" % (rec["iso"], weekly_pct, mode,
                                                      " | CHANGED from %s" % prev if prev and prev != mode else ""))
    return mode, prev


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "write" and sys.argv[2] == "--weekly":
        mode, prev = write(sys.argv[3])
        print("RUN-MODE %s%s" % (mode, " (CHANGED from %s)" % prev if prev and prev != mode else ""))
    elif len(sys.argv) >= 2 and sys.argv[1] == "--selftest":
        import tempfile
        ok = 0
        d = tempfile.mkdtemp()
        MODE_FILE = os.path.join(d, "m.json"); CONFIG_FILE = os.path.join(d, "c.json"); BENCH = d
        cases = []
        cases.append(("missing -> economy", effective()[0] == "economy"))
        write(10); cases.append(("10% -> performance", effective()[0] == "performance"))
        write(50); cases.append(("50% -> performance (<= threshold)", effective()[0] == "performance"))
        write(51); cases.append(("51% -> economy", effective()[0] == "economy"))
        write(10); cases.append(("stale -> economy", effective(now=time.time() + 91 * 60)[0] == "economy"))
        json.dump({"threshold_pct": 5}, open(CONFIG_FILE, "w")); write(10)
        cases.append(("config threshold 5, 10% -> economy", effective()[0] == "economy"))
        for name, good in cases:
            ok += good
            print("%s %s" % ("PASS" if good else "FAIL", name))
        print("SELFTEST %d/%d" % (ok, len(cases)))
        sys.exit(0 if ok == len(cases) else 1)
    else:
        print("%s | %s" % effective())
