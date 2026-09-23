r"""A5c - A5 and A5b RE-RUN under the judgement session's PAIR rule of 2026-09-23 16:xx (chat): PAIR acts only when
the best candidate of an intent has p >= ACT AND p - (runner-up p of the SAME intent) >= MARGIN; otherwise "llm".
ACT / MARGIN are READ from tools/bench/jev_menu_thresholds.json (pair.act, pair.margin) - not fitted here, so there is
no half-1 fitting step; half 1 is reported only for symmetry. OFFLINE: stored answers only, no Jev call, no LabVIEW.

PRIOR ART: a5_heldout.py (split(), SEED, the dangerous-direction definition) and a5b_seeds.py (the 1000-seed loop,
leave-one-intent-out, the set/result alignment check) - their logic is re-used; their JSON outputs are left as the
record of the OLD rule (threshold fitted on half 1, >= 2 over 0.70 -> llm).
The margin is computed over ALL candidates of the intent (at decision time every candidate has been scored); a
variant where the runner-up is taken only from the SAME half is also printed (it can only be less conservative).
PREDICTION CONTRACT (brief item 3): report acc, Brier, dangerous on half 2 of seed 20260923, and the 1000-split
count; PAIR may act only if dangerous == 0 everywhere. The bar is NOT lowered to pass.

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/bench_map_a5c.log -- py -u tools/bench/bench_map_20260923/a5c_margin.py
"""
import collections
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
SEED = 20260923
TH = json.load(open(os.path.join(BENCH, "jev_menu_thresholds.json"), encoding="utf-8"))["pair"]
ACT, MARGIN = float(TH["act"]), float(TH["margin"])
cand = json.load(open(os.path.join(BENCH, "jev_menu_pair_set.json"), encoding="utf-8"))
res = json.load(open(os.path.join(BENCH, "jev_menu_pair_result.json"), encoding="utf-8"))["items"]
assert len(cand) == len(res) and all(c["intent_id"] == r["intent_id"] and c["label"] == r["label"]
                                     for c, r in zip(cand, res)), "set/result misaligned"
ITEMS = [{"k": i, "id": r["intent_id"], "p": r["p"], "label": bool(r["label"])} for i, r in enumerate(res)
         if r.get("p") is not None]


def yes_set(pool):
    """Indices that ACT under the rule, the runner-up taken from `pool` (items of the same intent)."""
    by = collections.defaultdict(list)
    for it in pool:
        by[it["id"]].append(it)
    out = set()
    for _iid, xs in by.items():
        xs = sorted(xs, key=lambda x: -x["p"])
        second = xs[1]["p"] if len(xs) > 1 else 0.0
        if xs[0]["p"] >= ACT and xs[0]["p"] - second >= MARGIN:
            out.add(xs[0]["k"])
    return out


def score(h, yes):
    n = len(h)
    return {"n": n, "acc": round(sum(1 for i in h if (i["k"] in yes) == i["label"]) / n, 4) if n else None,
            "brier": round(sum((i["p"] - float(i["label"])) ** 2 for i in h) / n, 4) if n else None,
            "dangerous": [(i["id"], round(i["p"], 3)) for i in h if i["k"] in yes and not i["label"]],
            "acted": sum(1 for i in h if i["k"] in yes), "true_acted": sum(1 for i in h if i["k"] in yes and i["label"]),
            "positives": sum(1 for i in h if i["label"])}


def split(seed):
    idx = list(range(len(ITEMS)))
    random.Random(seed).shuffle(idx)
    h = len(idx) // 2
    return [ITEMS[i] for i in idx[:h]], [ITEMS[i] for i in idx[h:]]


def main():
    out = {"rule": {"act": ACT, "margin": MARGIN, "source": "tools/bench/jev_menu_thresholds.json pair"}}
    Y_all = yes_set(ITEMS)
    out["full_set"] = score(ITEMS, Y_all)
    h1, h2 = split(SEED)
    out["a5_seed_20260923"] = {"half1": score(h1, Y_all), "half2": score(h2, Y_all),
                               "half2_runnerup_same_half": score(h2, yes_set(h2))}
    bad_all, bad_same, by_id = 0, 0, collections.Counter()
    for seed in range(1000):
        _a, b = split(seed)
        d = score(b, Y_all)["dangerous"]
        bad_all += bool(d)
        by_id.update(x[0] for x in d)
        bad_same += bool(score(b, yes_set(b))["dangerous"])
    out["a5b_1000_splits"] = {"seeds_with_dangerous": bad_all, "seeds_with_dangerous_runnerup_same_half": bad_same,
                              "of": 1000, "dangerous_by_intent": dict(by_id)}
    lo = {}
    for iid in sorted(set(i["id"] for i in ITEMS)):
        held = [i for i in ITEMS if i["id"] == iid]
        s = score(held, Y_all)
        lo[iid] = {"acted": s["acted"], "true_acted": s["true_acted"], "dangerous": len(s["dangerous"]),
                   "best_p": round(max(i["p"] for i in held), 3)}
    out["leave_one_intent_out"] = lo
    out["lo_dangerous_total"] = sum(v["dangerous"] for v in lo.values())
    dang = len(out["full_set"]["dangerous"]) + bad_all + bad_same
    out["pair_keeps_acting"] = dang == 0
    for k in ("full_set",):
        print("  FACT  {0}: {1}".format(k, json.dumps(out[k])))
    for k, v in out["a5_seed_20260923"].items():
        print("  FACT  A5 seed {0} {1}: {2}".format(SEED, k, json.dumps(v)))
    print("  FACT  A5b: {0}".format(json.dumps(out["a5b_1000_splits"])))
    for iid, v in lo.items():
        print("  FACT  intent {0}: {1}".format(iid, json.dumps(v)))
    h2s = out["a5_seed_20260923"]["half2"]
    print("  {0}  A5c PAIR (act {1}, margin {2}) half-2 dangerous {3} == 0 and 1000-split dangerous {4} == 0 "
          "(acc h2 {5})".format("PASS" if out["pair_keeps_acting"] else "FAIL", ACT, MARGIN, len(h2s["dangerous"]),
                                bad_all, h2s["acc"]))
    json.dump(out, open(os.path.join(HERE, "a5c_margin.json"), "w", encoding="utf-8"), indent=1)
    print("=== A5c: PAIR keeps acting = {0}; JSON {1}".format(out["pair_keeps_acting"],
                                                            os.path.join(HERE, "a5c_margin.json")))
    return 0 if out["pair_keeps_acting"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
