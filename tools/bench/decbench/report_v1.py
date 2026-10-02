"""report_v1 - card chat-B2: decbench full-run report from results_<tag>.json + cases.json. Facts only, no recommendation.

    py tools/bench/decbench/report_v1.py --tag full   ->  tools/bench/decbench/report_v1.md

Sections: per category x arm (blind / mech score means, usd and minutes per arm-run, repeat spread = mean |r1 - r2| of
the blind score over the category's cases); per case x arm; peer review (defect hit rate on the defect cases, false
alarms on the clean case); discriminating cases (between-arm range of per-arm mean blind score > within-repeat range =
max |r1 - r2| over arms, as matbench v1); mechanical vs blind disagreements; cost and validity lines.
Score per arm-run = mean(must_hit) - 0.5 * max(forbidden), floored at 0 (dec_score.combine); bonus reported beside it.
PREDICTION: every expected arm-run present and valid; RESULT line.
"""
import argparse
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dec_score as DS  # noqa: E402

CAT = {"steering": "steering", "troubleshooting": "troubleshooting", "review": "peer review"}


def f(x, n=2):
    return "-" if x is None else ("%.*f" % (n, x))


def mean(xs):
    xs = [x for x in xs if x is not None]
    return st.mean(xs) if xs else None


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="full")
    ap.add_argument("--out", default=os.path.join(HERE, "report_v1.md"))
    ap.add_argument("--arms", default="H,XH,MX,FL,PAR")
    ap.add_argument("--title", default="# decbench v1 - decision bench, full run (card chat-B2)")
    ap.add_argument("--embedded", action="store_true", help="called from decbench.py: print REPORT_V1, not RESULT")
    a = ap.parse_args(argv)
    res = json.load(open(os.path.join(HERE, "results_%s.json" % a.tag), encoding="utf-8"))
    cases = {c["id"]: c for c in json.load(open(os.path.join(HERE, "cases.json"), encoding="utf-8"))["cases"]}
    arms = a.arms.split(",")
    arm_name = {"H": "Opus 5.5 high", "XH": "Opus 5.5 xhigh", "MX": "Opus 5.5 max", "FL": "Fable 5.1 low",
                "PAR": "PAR (3 Opus high lenses + 1 synthesiser)", "SH": "Sonnet 5.5 high", "SMX": "Sonnet 5.5 max"}
    arm_name = {k: v for k, v in arm_name.items() if k in arms}
    recs = [r for r in res["records"] if not r.get("invalid")]
    invalid = [r for r in res["records"] if r.get("invalid")]
    for r in recs:
        rub = cases[r["case"]]["rubric"]
        r["_m"] = DS.combine(r.get("mech") or {}, rub)
        r["_b"] = DS.combine(r.get("blind") or {}, rub) if r.get("blind") else None
    by = {}
    for r in recs:
        by.setdefault((r["case"], r["arm"]), {})[r["rep"]] = r
    L = [a.title, "",
         "Facts only. 10 known-answer cases x %d arms x %d repeats, --par %s. Arms: %s." % (
             len(arms), max((r["rep"] for r in recs), default=0), res.get("par"),
             "; ".join("%s = %s" % (k, v) for k, v in arm_name.items())),
         "Score per arm-run = mean(must_hit) - 0.5 x max(forbidden), floored at 0; bonus mean beside it, never added. "
         "blind = one Opus 5.5 high scorer cell per case (answer key + rubric texts, labels shuffled, arm/model hidden); "
         "mech = rubric regexes. usd / min = per arm-run (PAR = sum of its 4 cells; min = wall clock of the arm-run).",
         "Spent $%.2f (arm-runs $%.2f + blind scorers $%.2f). Valid arm-runs %d, invalid %d." % (
             res["spent_usd"], res["spent_usd"] - res["blind_usd"], res["blind_usd"], len(recs), len(invalid)), ""]
    # --- per category x arm
    L += ["## Per category x arm", "",
          "| category | arm | n | blind mean | mech mean | bonus (blind) | usd / run | min / run | repeat spread (blind) |",
          "|---|---|---|---|---|---|---|---|---|"]
    for cat, cname in CAT.items():
        cids = [c for c in cases if cases[c]["category"] == cat]
        for arm in arms:
            rs = [r for r in recs if r["arm"] == arm and r["case"] in cids]
            spread = []
            for cid in cids:
                d = by.get((cid, arm), {})
                if 1 in d and 2 in d and d[1]["_b"] and d[2]["_b"]:
                    spread.append(abs(d[1]["_b"]["score"] - d[2]["_b"]["score"]))
            L.append("| %s | %s | %d | %s | %s | %s | %s | %s | %s |" % (
                cname, arm, len(rs), f(mean([r["_b"]["score"] for r in rs if r["_b"]])),
                f(mean([r["_m"]["score"] for r in rs])),
                f(mean([r["_b"]["bonus"] for r in rs if r["_b"] and r["_b"]["bonus"] is not None])),
                f(mean([r["usd"] for r in rs])), f(mean([r["minutes"] for r in rs]), 1), f(mean(spread))))
    L += ["", "## All cases x arm (blind r1 ; r2 | mech r1 ; r2 | usd mean | min mean)", "",
          "| case | " + " | ".join(arms) + " |", "|---|" + "---|" * len(arms)]
    for cid in cases:
        row = []
        for arm in arms:
            d = by.get((cid, arm), {})
            b = " ; ".join(f(d[k]["_b"]["score"]) if k in d and d[k]["_b"] else "-" for k in (1, 2))
            m = " ; ".join(f(d[k]["_m"]["score"]) if k in d else "-" for k in (1, 2))
            row.append("%s &#124; %s &#124; $%s &#124; %s" % (b, m, f(mean([x["usd"] for x in d.values()])),
                                                             f(mean([x["minutes"] for x in d.values()]), 1)))
        L.append("| %s | %s |" % (cid, " | ".join(row)))
    L += ["", "## Per arm totals", "", "| arm | n | blind mean | mech mean | usd total | usd / run | min / run | turns / run "
          "| tool calls / run | timeouts |", "|---|---|---|---|---|---|---|---|---|---|"]
    for arm in arms:
        rs = [r for r in recs if r["arm"] == arm]
        L.append("| %s | %d | %s | %s | %s | %s | %s | %s | %s | %d |" % (
            arm, len(rs), f(mean([r["_b"]["score"] for r in rs if r["_b"]]), 3), f(mean([r["_m"]["score"] for r in rs]), 3),
            f(sum(r["usd"] for r in rs)), f(mean([r["usd"] for r in rs])), f(mean([r["minutes"] for r in rs]), 1),
            f(mean([r["turns"] for r in rs]), 1), f(mean([r["tools"] for r in rs]), 1), sum(1 for r in rs if r["timeout"])))
    # --- peer review
    rev = [c for c in cases if cases[c]["category"] == "review"]
    dfc = [c for c in rev if not cases[c].get("clean")]
    cln = [c for c in rev if cases[c].get("clean")]
    L += ["", "## Peer review: defect hits (%s) and clean-case false alarms (%s)" % (", ".join(dfc), ", ".join(cln)), "",
          "Defect hit = blind must-hit mean of the arm-run (0..1); full hit = every must_hit item scored 1 by the blind "
          "scorer; accepted = forbidden item (DEFECT none/minor) committed (blind >= 0.5). False alarm on the clean case = "
          "its forbidden item (DEFECT: blocker) committed (blind >= 0.5; mech in brackets).", "",
          "| arm | defect must-hit mean (blind) | full hits / runs | accepted-as-fine / runs | clean-case false alarms / runs "
          "(mech) |", "|---|---|---|---|---|"]
    for arm in arms:
        dr = [r for r in recs if r["arm"] == arm and r["case"] in dfc and r["_b"]]
        cr = [r for r in recs if r["arm"] == arm and r["case"] in cln]
        mh = lambda r: [r["blind"].get(i["id"], 0) for i in cases[r["case"]]["rubric"]["must_hit"]]  # noqa: E731
        fa = sum(1 for r in cr if r["_b"] and r["_b"]["forbidden"] >= 0.5)
        fam = sum(1 for r in cr if r["_m"]["forbidden"] >= 0.5)
        L.append("| %s | %s | %d / %d | %d / %d | %d / %d (%d) |" % (
            arm, f(mean([r["_b"]["must"] for r in dr])), sum(1 for r in dr if all(x >= 1 for x in mh(r))), len(dr),
            sum(1 for r in dr if r["_b"]["forbidden"] >= 0.5), len(dr), fa, len(cr), fam))
    L += ["", "Per defect case, blind must-hit mean per arm:", "", "| case | " + " | ".join(arms) + " |",
          "|---|" + "---|" * len(arms)]
    for cid in dfc:
        L.append("| %s | %s |" % (cid, " | ".join(f(mean([r["_b"]["must"] for r in recs if r["case"] == cid and
                                                            r["arm"] == arm and r["_b"]])) for arm in arms)))
    # --- discriminating cases
    L += ["", "## Discriminating cases (blind score)", "",
          "within = the largest |r1 - r2| over arms; between = range of the per-arm mean scores. A case whose between "
          "is not larger than its within is not distinguishable from repeat noise.", "",
          "| case | within | between | discriminates | per-arm mean |", "|---|---|---|---|---|"]
    disc = []
    for cid in cases:
        pm, within = {}, 0.0
        for arm in arms:
            d = by.get((cid, arm), {})
            sc = [d[k]["_b"]["score"] for k in (1, 2) if k in d and d[k]["_b"]]
            if sc:
                pm[arm] = st.mean(sc)
                if len(sc) == 2:
                    within = max(within, abs(sc[0] - sc[1]))
        between = (max(pm.values()) - min(pm.values())) if pm else 0.0
        yes = between > within
        if yes:
            disc.append(cid)
        L.append("| %s | %s | %s | %s | %s |" % (cid, f(within), f(between), "yes" if yes else "no",
                                                 ", ".join("%s %s" % (k, f(v)) for k, v in pm.items())))
    L += ["", "Discriminating: %s" % (", ".join(disc) or "none")]
    # --- disagreements
    dis = DS.disagreements(recs)
    L += ["", "## Mechanical vs blind disagreements (|mech - blind| >= 0.5 on one item): %d" % len(dis), ""]
    cnt = {}
    for x in dis:
        p = x.split()
        cnt[(p[0], p[3])] = cnt.get((p[0], p[3]), 0) + 1
    L += ["| case | item | count |", "|---|---|---|"] + ["| %s | %s | %d |" % (k[0], k[1], v) for k, v in sorted(cnt.items())]
    L += ["", "<details><summary>all %d</summary>" % len(dis), ""] + ["- " + x for x in dis] + ["", "</details>"]
    # --- validity
    L += ["", "## Validity", ""]
    atts = [r for r in recs if r.get("attempt", 1) > 1]
    L.append("- Arm-runs re-run from the start after a rate-limit/overload cell: %d (%s)." % (
        len(atts), ", ".join("%s %s r%d a%d" % (r["case"], r["arm"], r["rep"], r["attempt"]) for r in atts) or "none"))
    L.append("- Invalid arm-runs in the table: %d (%s)." % (len(invalid), ", ".join("%s %s r%s" % (r["case"], r["arm"],
                                                                                              r["rep"]) for r in invalid)
                                                          or "none"))
    L.append("- Timeouts (cell cap): %d." % sum(1 for r in recs if r["timeout"]))
    nob = [r for r in recs if not r["_b"]]
    L.append("- Arm-runs without a blind score: %d (%s)." % (len(nob), ", ".join("%s %s r%d" % (r["case"], r["arm"], r["rep"])
                                                                               for r in nob) or "none"))
    models = sorted({m for r in recs for c in r["cells"] for m in c.get("models_used", [])})
    L.append("- Models seen in cell envelopes (modelUsage): %s." % ", ".join(models))
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    exp = len(cases) * len(arms) * 2
    fails = (["invalid %d" % len(invalid)] if invalid else []) + (["runs %d != %d" % (len(recs), exp)] if len(recs) != exp
                                                                  else []) + (["no blind %d" % len(nob)] if nob else [])
    print(("REPORT_V1 " if a.embedded else "RESULT ") + json.dumps({"schema": "result-line/1", "status": "FAIL" if fails else "PASS",
                                  "gates": {"pass": 3 - len(fails), "fail": len(fails)},
                                  "first_fail": fails[0] if fails else None,
                                  "artefacts": [{"path": "tools/bench/decbench/report_v1.md"}]}))
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
