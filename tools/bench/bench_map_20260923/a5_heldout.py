r"""A5 - Jev menus on a HELD-OUT half (connectivity-map plan step 5b, layer A). OFFLINE: no LabVIEW, no Jev call.

WHAT: each labelled set's MEASURED answers (tools/bench/jev_menu_<m>_result.json `items`, p from step 5's run
2026-09-23 16:43, 785 calls) are split 50/50 by a FIXED seed; the threshold is set on half 1 by the SAME rule the
step-5 script used (jev_menu_thresholds.json `rules`), and half 2 is scored at that threshold. No answer is
re-asked, so this measures threshold over-fitting, not Jev's sampling noise (stated, not hidden).

DANGEROUS DIRECTION (jev_pairs.py docstring): PAIR/CHAIN = a false "yes" at/above the threshold (a wrong wire);
RISK = a true risk scored <= the proceed threshold; OP = an acted (p >= t) wrong op.
PREDICTION CONTRACT: PAIR half-2 accuracy >= 0.85 AND 0 dangerous errors -> "PAIR keeps acting" (plan 5b A5).
Brier is threshold-free. Items are split per ITEM, not per intent (a known leak for PAIR: one intent's candidates
can fall in both halves) - reported as a caveat.

    MATERIAL=1 py tools/bgrun.py --max-min 5 --log tools/bench/bench_map_a5.log -- py -u tools/bench/bench_map_20260923/a5_heldout.py
"""
import json
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.dirname(HERE)
SEED = 20260923
GRID = [round(0.05 * i, 2) for i in range(1, 20)]
OUT = {"seed": SEED, "grid": GRID, "menus": {}}


def split(items):
    idx = list(range(len(items)))
    random.Random(SEED).shuffle(idx)
    h = len(idx) // 2
    return [items[i] for i in idx[:h]], [items[i] for i in idx[h:]]


def brier(rows):
    return round(sum((r["p"] - (1.0 if r["label"] else 0.0)) ** 2 for r in rows) / len(rows), 4) if rows else None


def binary(name, items, risk=False):
    items = [i for i in items if i.get("p") is not None]
    h1, h2 = split(items)
    if risk:     # proceed when p_risk <= t: largest grid t strictly below every positive's p on half 1
        pos = [i["p"] for i in h1 if i["label"]]
        ok = [t for t in GRID if not pos or t < min(pos)]
        t = max(ok) if ok else None
        yes = lambda i: t is None or i["p"] > t          # "risk" -> goes to the LLM
        danger = [i for i in h2 if i["label"] and not yes(i)]
    else:        # smallest grid t whose yes-precision on half 1 is 1.0 with >= 1 yes
        t = None
        for c in GRID:
            ys = [i for i in h1 if i["p"] >= c]
            if ys and all(i["label"] for i in ys):
                t = c
                break
        yes = lambda i: t is not None and i["p"] >= t
        danger = [i for i in h2 if yes(i) and not i["label"]]
    acc = sum(1 for i in h2 if yes(i) == bool(i["label"])) / len(h2)
    res = {"n": len(items), "n_half1": len(h1), "n_half2": len(h2), "pos_half1": sum(1 for i in h1 if i["label"]),
           "pos_half2": sum(1 for i in h2 if i["label"]), "threshold_half1": t, "acc_half2": round(acc, 4),
           "brier_half2": brier(h2), "brier_half1": brier(h1), "dangerous_half2": len(danger),
           "dangerous_items": [{k: v for k, v in d.items() if k in ("intent_id", "line", "change", "y", "z", "p")}
                               for d in danger],
           "recall_yes_half2": (round(sum(1 for i in h2 if yes(i) and i["label"]) /
                                      max(1, sum(1 for i in h2 if i["label"])), 4))}
    OUT["menus"][name] = res
    return res


def op(items):
    items = [i for i in items if i.get("probs")]
    h1, h2 = split(items)
    t = None
    for c in GRID:
        acted = [i for i in h1 if max(i["probs"].values()) >= c]
        if acted and all(i["pred"] == i["label"] for i in acted):
            t = c
            break
    acted2 = [i for i in h2 if t is not None and max(i["probs"].values()) >= t]
    wrong2 = [i for i in acted2 if i["pred"] != i["label"]]
    b = sum(sum((i["probs"].get(k, 0) - (1.0 if k == i["label"] else 0.0)) ** 2 for k in i["probs"])
            for i in h2) / len(h2)
    res = {"n": len(items), "n_half1": len(h1), "n_half2": len(h2), "threshold_half1": t,
           "acc_half2_argmax": round(sum(1 for i in h2 if i["pred"] == i["label"]) / len(h2), 4),
           "acted_half2": len(acted2), "acc_acted_half2": (round(1 - len(wrong2) / len(acted2), 4) if acted2 else None),
           "brier_multiclass_half2": round(b, 4), "dangerous_half2": len(wrong2),
           "dangerous_items": [{"label": w["label"], "pred": w["pred"], "source": w.get("source")} for w in wrong2]}
    OUT["menus"]["op"] = res
    return res


def main():
    load = lambda m: json.load(open(os.path.join(BENCH, "jev_menu_{0}_result.json".format(m)), encoding="utf-8"))
    for m in ("pair", "chain"):
        r = binary(m, load(m)["items"])
        print("  FACT  {0}: {1}".format(m, json.dumps({k: v for k, v in r.items() if k != "dangerous_items"})))
    r = binary("risk", load("risk")["items"], risk=True)
    print("  FACT  risk: {0}".format(json.dumps({k: v for k, v in r.items() if k != "dangerous_items"})))
    r = op(load("op")["items"])
    print("  FACT  op: {0}".format(json.dumps({k: v for k, v in r.items() if k != "dangerous_items"})))
    p = OUT["menus"]["pair"]
    keep = p["threshold_half1"] is not None and p["acc_half2"] >= 0.85 and p["dangerous_half2"] == 0
    OUT["pair_keeps_acting"] = keep
    OUT["pair_act_threshold_for_B"] = p["threshold_half1"] if keep else None
    for d in p["dangerous_items"]:
        print("  FACT  PAIR dangerous on half 2: {0}".format(d))
    print("  {0}  A5 PAIR half-2 acc {1} >= 0.85 and dangerous {2} == 0 (threshold from half 1 = {3})".format(
        "PASS" if keep else "FAIL", p["acc_half2"], p["dangerous_half2"], p["threshold_half1"]))
    with open(os.path.join(HERE, "a5_heldout.json"), "w", encoding="utf-8") as f:
        json.dump(OUT, f, indent=1)
    print("=== A5: PAIR keeps acting = {0}; JSON {1}".format(keep, os.path.join(HERE, "a5_heldout.json")))
    return 0 if keep else 1


if __name__ == "__main__":
    raise SystemExit(main())
