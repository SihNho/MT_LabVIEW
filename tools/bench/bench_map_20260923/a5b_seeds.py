r"""A5b - the discriminating test the A5 hypothesis review named (archive/peer/2026-09-23-bench-map-a5-pair-heldout.md §4).
OFFLINE, stored answers only (no Jev call, no LabVIEW). It MEASURES; it does not change PAIR or any threshold.

  S  a5_heldout's rule (threshold = smallest grid t with yes-precision 1.0 on half 1; score half 2) over 1,000 seeds:
     how often half 2 carries >= 1 dangerous error (a labelled-FALSE item at/above t), and WHICH intents cause them
  L  leave-one-intent-out: threshold on the other intents, score the held-out intent's items
  F  both again with a PYTHON NAME FILTER in front of Jev (not adopted anywhere - a measurement of the reviewer's
     proposal): when the intent names the sink pin (dst_hint) and the candidate's sink terminal name differs, the answer
     is "no" whatever p says.
Items are aligned index-by-index between jev_menu_pair_set.json (the candidates) and jev_menu_pair_result.json (the p),
and the alignment is CHECKED (intent id + label per index).

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/bench_map_a5b.log -- py -u tools/bench/bench_map_20260923/a5b_seeds.py
"""
import collections
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
GRID = [round(0.05 * i, 2) for i in range(1, 20)]
cand = json.load(open(os.path.join(BENCH, "jev_menu_pair_set.json"), encoding="utf-8"))
res = json.load(open(os.path.join(BENCH, "jev_menu_pair_result.json"), encoding="utf-8"))["items"]
assert len(cand) == len(res) and all(c["intent_id"] == r["intent_id"] and c["label"] == r["label"]
                                     for c, r in zip(cand, res)), "set/result misaligned"
import re                                                                          # noqa: E402
# the intent names the sink pin only in the S1-row wording "... input '<name>'" (the 2 S3b rows name a tunnel index)
HINT = dict((c["intent_id"], m.group(1)) for c in cand for m in [re.search(r"input '(.*)'$", c["line"])] if m)
SINK = lambda c: re.search(r"-> SINK #\d+ \S+ terminal '(.*?)' \(", c["row"]).group(1)


def items(filt):
    out = []
    for c, r in zip(cand, res):
        p = r["p"]
        if filt and c["intent_id"] in HINT and SINK(c) != HINT[c["intent_id"]]:
            p = 0.0
        out.append({"id": c["intent_id"], "p": p, "label": c["label"], "dst": SINK(c)})
    return out


def thresh(h1):
    for t in GRID:
        ys = [i for i in h1 if i["p"] >= t]
        if ys and all(i["label"] for i in ys):
            return t
    return None


def danger(h2, t):
    return [i for i in h2 if t is not None and i["p"] >= t and not i["label"]]


def main():
    out = {}
    for filt in (False, True):
        its, tag = items(filt), "filter" if filt else "raw"
        n_bad, by_id, accs = 0, collections.Counter(), []
        for seed in range(1000):
            idx = list(range(len(its)))
            random.Random(seed).shuffle(idx)
            h1, h2 = [its[i] for i in idx[:24]], [its[i] for i in idx[24:]]
            t = thresh(h1)
            d = danger(h2, t)
            n_bad += bool(d)
            by_id.update(x["id"] for x in d)
            accs.append(sum(1 for i in h2 if (t is not None and i["p"] >= t) == i["label"]) / len(h2))
        lo = {}
        for iid in sorted(set(i["id"] for i in its)):
            t = thresh([i for i in its if i["id"] != iid])
            held = [i for i in its if i["id"] == iid]
            lo[iid] = {"t": t, "dangerous": len(danger(held, t)), "tp": sum(1 for i in held if t is not None and
                                                                            i["p"] >= t and i["label"])}
        accs.sort()
        out[tag] = {"seeds_with_dangerous": n_bad, "of": 1000, "dangerous_by_intent": dict(by_id),
                    "acc_half2_p5_p50_p95": [accs[50], accs[500], accs[950]], "leave_one_intent_out": lo,
                    "lo_dangerous_total": sum(v["dangerous"] for v in lo.values()),
                    "lo_true_yes_total": sum(v["tp"] for v in lo.values()),
                    "filtered_positive_items_lost": sum(1 for i in its if i["label"] and i["p"] == 0.0) if filt else 0}
        print("  FACT  {0}: {1}".format(tag, json.dumps({k: v for k, v in out[tag].items()
                                                          if k != "leave_one_intent_out"})))
    json.dump(out, open(os.path.join(HERE, "a5b_seeds.json"), "w", encoding="utf-8"), indent=1)
    print("=== A5b written {0}".format(os.path.join(HERE, "a5b_seeds.json")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
