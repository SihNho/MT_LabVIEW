"""compare_h - the H arm (claude-opus-5-5 / high) of a run vs v1's H (results_full.json): per-case blind/mech scores,
usd and minutes. Facts only; markdown section on stdout.

    python3 tools/bench/decbench/compare_h.py --tag sonnet_cloud
"""
import argparse
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dec_score as DS  # noqa: E402


def load(tag, cases):
    res = json.load(open(os.path.join(HERE, "results_%s.json" % tag), encoding="utf-8"))
    out = {}
    for r in res["records"]:
        if r.get("invalid") or r["arm"] != "H":
            continue
        rub = cases[r["case"]]["rubric"]
        b = DS.combine(r.get("blind") or {}, rub) if r.get("blind") else None
        out.setdefault(r["case"], []).append({"rep": r["rep"], "b": b["score"] if b else None,
                                              "m": DS.combine(r.get("mech") or {}, rub)["score"],
                                              "usd": r["usd"], "min": r["minutes"]})
    return out


def m(xs, n=2):
    xs = [x for x in xs if x is not None]
    return ("%.*f" % (n, st.mean(xs))) if xs else "-"


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", required=True)
    ap.add_argument("--v1", default="full")
    a = ap.parse_args(argv)
    cases = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]}
    v1, now = load(a.v1, cases), load(a.tag, cases)
    L = ["| case | v1 H blind r1 ; r2 | cloud H blind r1 ; r2 | v1 H mech mean | cloud H mech mean | v1 usd / run | "
         "cloud usd / run | v1 min / run | cloud min / run |", "|---|---|---|---|---|---|---|---|---|"]
    allv, alln = [], []
    for cid in cases:
        x, y = sorted(v1.get(cid, []), key=lambda r: r["rep"]), sorted(now.get(cid, []), key=lambda r: r["rep"])
        allv += x
        alln += y
        L.append("| %s | %s | %s | %s | %s | %s | %s | %s | %s |" % (
            cid, " ; ".join("-" if r["b"] is None else "%.2f" % r["b"] for r in x) or "-",
            " ; ".join("-" if r["b"] is None else "%.2f" % r["b"] for r in y) or "-",
            m([r["m"] for r in x]), m([r["m"] for r in y]), m([r["usd"] for r in x]), m([r["usd"] for r in y]),
            m([r["min"] for r in x], 1), m([r["min"] for r in y], 1)))
    L.append("| **all** (n %d / %d) | %s | %s | %s | %s | %s | %s | %s | %s |" % (
        len(allv), len(alln), m([r["b"] for r in allv], 3), m([r["b"] for r in alln], 3), m([r["m"] for r in allv], 3),
        m([r["m"] for r in alln], 3), m([r["usd"] for r in allv]), m([r["usd"] for r in alln]),
        m([r["min"] for r in allv], 1), m([r["min"] for r in alln], 1)))
    print("\n".join(L))


if __name__ == "__main__":
    main()
