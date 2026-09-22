r"""jev_gaterow.py - GATE-ROW triage: one verdict per failing row of a run (docs/jev-integration-plan.md 2차 #2).

    py tools/jev_gaterow.py tools/bench/<name>.log [--run -1] [--json <out>]

prints, and appends to tools/bench/jev_gate.log, one line per `FAIL` row of that run:

    JEV-GATEROW | <log> | <row label> | <class> p=<p>

<class> is `defect` (the VI/edit really is wrong), `prediction-error` (the gate's expectation was wrong, the
machine reading is fine), `reading-artefact` (a census/reader limitation), or `unknown` when the winning mean
probability is below the project's 0.70 band, when there is no key, or when the call errors. Every verdict is the
CONSENSUS of `jev.samples()` asks (5 by default; `JEV_SAMPLES` overrides).

ADVISORY, NEVER A GATE ON ITS OWN. Nothing refuses anything on the strength of these lines. They are read by
`tools/hooks/guard_peer.py`'s review ladder (2차 #1) as ONE input among others, and by a judgement session that
wants to know whether a 12-FAIL run is twelve defects or one blind reader.

NO LabVIEW: this reads .log files and calls api.typesafe.ai through tools/jev.py only.
Exit code 0 when at least one line was printed, 2 when the run has no FAIL rows or cannot be read.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
for _p in (HERE, os.path.join(HERE, "bench")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import jev                                      # noqa: E402
from jev_gaterow_q import GATEROW_Q, fail_rows  # noqa: E402

GATELOG = os.path.join(ROOT, "tools", "bench", "jev_gate.log")
THRESHOLD = jev.UNKNOWN_HI          # 0.70


def classify(state, purpose="gaterow", n=None, timeout=60, retries=3):
    """(class, mean probability, spread) for ONE row's state. Never raises."""
    mean, spread, err = jev.ask_n(state, {"why": GATEROW_Q}, n=n, purpose=purpose,
                                  timeout=timeout, retries=retries)
    if err or not isinstance(mean, dict) or not mean:
        return "unknown", None, None
    cls = max(mean, key=mean.get)
    p = mean[cls]
    sp = spread.get("spread") if isinstance(spread, dict) else None
    return (cls if p >= THRESHOLD else "unknown"), p, sp


def main(argv):
    args = [a for a in argv[1:] if not a.startswith("--")]
    run = -1
    out_json = None
    for i, a in enumerate(argv):
        if a == "--run" and i + 1 < len(argv):
            run = int(argv[i + 1])
        if a == "--json" and i + 1 < len(argv):
            out_json = argv[i + 1]
    if len(args) != 1:
        sys.stderr.write("usage: py tools/jev_gaterow.py <bgrun log> [--run -1] [--json <out>]\n")
        return 2
    logpath = args[0] if os.path.isabs(args[0]) else os.path.join(ROOT, args[0])
    rows = fail_rows(logpath, run_index=run)
    if not rows:
        sys.stderr.write("JEV-GATEROW | %s | no FAIL row in that run\n" % os.path.basename(logpath))
        return 2
    verdicts, lines = [], []
    for r in rows:
        cls, p, sp = classify(r["state"])
        line = "JEV-GATEROW | %s | %s | %s p=%s" % (
            os.path.basename(logpath), r["label"], cls, ("%.2f" % p) if p is not None else "-")
        print(line)
        sys.stdout.flush()
        lines.append(line)
        verdicts.append({"line": r["line"], "label": r["label"], "class": cls, "p": p, "spread": sp,
                         "row": r["row"]})
    try:
        with open(GATELOG, "a", encoding="utf-8") as f:
            f.write("\n".join(lines) + "\n")
    except OSError:
        pass
    if out_json:
        try:
            with open(out_json, "w", encoding="utf-8") as f:
                json.dump({"log": os.path.basename(logpath), "run": run, "verdicts": verdicts}, f,
                          ensure_ascii=False, indent=1)
        except OSError:
            pass
    return 0


def verdicts_for(logpath, run_index=-1, max_rows=5, n=2, timeout=25, retries=1):
    """The gate-row verdicts of one run as a compact text block, for the review ladder's state. Never raises.

    DELIBERATELY CHEAPER THAN THE CLI: 5 rows x 2 samples, 25 s per call, because this runs inside a PreToolUse
    hook that must not hold the session while it asks. The CLI (the measured path) uses the full consensus."""
    try:
        rows = fail_rows(logpath, run_index=run_index, max_rows=max_rows)
        if not rows:
            return ""
        out = []
        for r in rows:
            cls, p, _sp = classify(r["state"], purpose="gaterow-ladder", n=n, timeout=timeout, retries=retries)
            out.append("%s: %s (p=%s) | %s" % (
                r["label"], cls, ("%.2f" % p) if p is not None else "-", r["row"][:200]))
        return "\n".join(out)[:2400]
    except Exception:                       # noqa: BLE001 - an advisory input must never wedge a gate
        return ""


if __name__ == "__main__":
    sys.exit(main(sys.argv))
