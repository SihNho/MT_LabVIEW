r"""uc_report_v1 - facts-only report of a ucbench full run (card chat-B4): results_<tag>.json -> report_v1.md.

    py -u tools/bench/ucbench/uc_report_v1.py [--tag full] [--out report_v1.md]

Offline, no model, no LabVIEW. Per task x arm: recall (blind, mech), precision, false claims, claims, usd, minutes,
sub-agents, Workflow calls, tokens, r1/r2 values; L3 count accuracy; UC vs SXH and UC vs SMX per task; which tasks
discriminate (between-arm range of arm means > the largest within-arm |r1 - r2|); key items found only by UC runs and
only by single-session runs. No recommendation.
PREDICTION CONTRACT: every record of the results file lands in exactly one table row; ends with a RESULT line.
"""
import argparse
import glob
import json
import os
import statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
ARM_ORDER = ["SH", "SXH", "SMX", "UC"]
SINGLE = ("SH", "SXH", "SMX")


def m(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 3) if xs else None


def fmt(x):
    return "-" if x is None else ("%.3f" % x if isinstance(x, float) else str(x))


def pair(xs):
    return " / ".join(fmt(x) for x in xs) if xs else "-"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="full")
    ap.add_argument("--out", default="report_v1.md")
    a = ap.parse_args()
    res = json.load(open(os.path.join(HERE, "results_%s.json" % a.tag), encoding="utf-8"))
    tasks = {t["id"]: t for t in json.load(open(os.path.join(HERE, "tasks.json"), encoding="utf-8"))["tasks"]}
    recs = res["records"]
    rows_written = 0
    L = ["# ucbench report v1 (card chat-B4) - facts only", "",
         "Run tag `%s`, par %s, total spend $%.2f (scorer cells $%.2f). Arms: SH = claude-opus-5-5 high, SXH = xhigh, "
         "SMX = max (single sessions); UC = `--effort ultracode` (xhigh main loop + Workflow). Same prompt, tools and "
         "60-min cap for every arm. usd / tokens are the cell's own result envelope (`total_cost_usd`, `modelUsage`). "
         "Sub-agents = distinct agent_id values in the cell's hook log (sub-agents that made at least one tool call)."
         % (res["tag"], res["par"], res["spent_usd"], res["score_usd"]), ""]
    inv = sorted(glob.glob(os.path.join(HERE, "runs", a.tag, "*", "*_invalid_a*.json")))
    L += ["Invalid attempts re-run from the start: %d %s" % (len(inv), [os.path.basename(p) for p in inv][:12]),
          "Records: %d, invalid after retries: %d" % (len(recs), sum(1 for r in recs if r.get("invalid"))), ""]
    by = {}
    for r in recs:
        by.setdefault((r["task"], r["arm"]), []).append(r)
    means = {}
    for tid in res["tasks"]:
        t = tasks[tid]
        L += ["## %s (key %d items)" % (tid, len(t["key"])), "",
              "| arm | runs | recall blind (mean; r1 / r2) | recall mech | precision | false claims | claims | "
              "extra real | usd | min | sub-agents | Workflow calls | out tokens | in+cache tokens |" +
              (" count acc |" if t.get("counts") else ""),
              "|---" * (14 + (1 if t.get("counts") else 0)) + "|"]
        for arm in ARM_ORDER:
            rs = sorted([r for r in by.get((tid, arm), []) if not r.get("invalid")], key=lambda x: x["rep"])
            if not by.get((tid, arm)):
                continue
            sc = [r.get("score") or {} for r in rs]
            g = lambda k: [s.get(k) for s in sc]  # noqa: E731
            tok = [r.get("tokens") or {} for r in rs]
            row = {"recall": g("recall"), "precision": g("precision"), "false": g("false_claims"),
                   "usd": [round(r.get("usd") or 0, 2) for r in rs], "min": [r.get("minutes") for r in rs]}
            means[(tid, arm)] = {k: m(v) for k, v in row.items()}
            means[(tid, arm)]["spread_recall"] = (abs(row["recall"][0] - row["recall"][1])
                                                  if len(row["recall"]) == 2 and None not in row["recall"] else None)
            cnt = [((r.get("counts") or {}).get("count_acc")) for r in rs]
            L.append("| %s | %d | %s; %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s | %s |%s" % (
                arm, len(rs), fmt(m(row["recall"])), pair(row["recall"]), pair(g("recall_mech")),
                pair(row["precision"]), pair(row["false"]), pair(g("claims_n")), pair(g("extra_real")),
                pair(row["usd"]), pair(row["min"]), pair([(r.get("calls") or {}).get("sub_agents") for r in rs]),
                pair([(r.get("top_tool_uses") or {}).get("Workflow", 0) for r in rs]),
                pair([x.get("outputTokens") for x in tok]),
                pair([(x.get("inputTokens") or 0) + (x.get("cacheReadInputTokens") or 0) +
                      (x.get("cacheCreationInputTokens") or 0) for x in tok]),
                (" %s |" % pair(cnt)) if t.get("counts") else ""))
            rows_written += len(by[(tid, arm)])
        L.append("")
        for other in ("SXH", "SMX"):
            u, o = means.get((tid, "UC")), means.get((tid, other))
            if u and o:
                d = {k: (None if u[k] is None or o[k] is None else round(u[k] - o[k], 3))
                     for k in ("recall", "precision", "false", "usd", "min")}
                L.append("- UC minus %s (%s): recall %s, precision %s, false claims %s, usd %s, minutes %s" % (
                    other, "orchestration effect, same main-loop effort" if other == "SXH" else "cost-matched alternative",
                    fmt(d["recall"]), fmt(d["precision"]), fmt(d["false"]), fmt(d["usd"]), fmt(d["min"])))
        am = [means[(tid, x)]["recall"] for x in ARM_ORDER if (tid, x) in means and means[(tid, x)]["recall"] is not None]
        sp = [means[(tid, x)]["spread_recall"] for x in ARM_ORDER if (tid, x) in means
              and means[(tid, x)]["spread_recall"] is not None]
        if am and sp:
            L.append("- discrimination (recall): between-arm range of means %.3f vs largest within-arm |r1-r2| %.3f "
                     "-> %s" % (max(am) - min(am), max(sp), "DISCRIMINATES" if max(am) - min(am) > max(sp)
                                else "does not discriminate"))
        found = {}
        for r in by_valid(recs, tid):
            for k, v in ((r.get("blind") or {}).get("key") or {}).items():
                if v:
                    found.setdefault(k, set()).add(r["arm"])
        kids = [k["id"] for k in t["key"]]
        uc_only = [k for k in kids if found.get(k) == {"UC"}]
        single_only = [k for k in kids if k in found and "UC" not in found[k]]
        none = [k for k in kids if k not in found]
        txt = {k["id"]: k["text"] for k in t["key"]}
        L.append("- key items found by UC runs only: %d %s" % (len(uc_only), uc_only))
        L.append("- key items found by single-session runs only (never by UC): %d %s" % (len(single_only), single_only))
        L.append("- key items found by no run: %d %s" % (len(none), none))
        for k in (uc_only + single_only)[:15]:
            L.append("  - %s (%s): %s" % (k, ",".join(sorted(found[k])), txt[k][:160]))
        L.append("")
    with open(os.path.join(HERE, a.out), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    ok = rows_written == len(recs)
    print("REPORT %s rows %d of %d records" % (a.out, rows_written, len(recs)))
    print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS" if ok else "FAIL",
                                  "gates": {"pass": int(ok), "fail": int(not ok)},
                                  "first_fail": None if ok else "rows %d != records %d" % (rows_written, len(recs)),
                                  "artefacts": [{"path": "tools/bench/ucbench/" + a.out}]}), flush=True)
    return 0 if ok else 1


def by_valid(recs, tid):
    return [r for r in recs if r["task"] == tid and not r.get("invalid")]


if __name__ == "__main__":
    raise SystemExit(main())
