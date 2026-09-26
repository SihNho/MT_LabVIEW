r"""f7911_facts_94_offline.py - card 94-3 parts (1)+(2) + offline terminal lookups, NO LabVIEW.
Reuses diag_c91_step4_stats.load/bucket (t0stamp format: int64 LE, [0]=QPC freq, then ticks).
(1) per B leg of 94-1: per iteration k of loop #637 (site 0 = `i`), last stamp of sites 2/3/4 in k; d43 = s4-s3,
    d42 = s4-s2 (us). Median in 10 equal TIME bins (by i_k time), least-squares slope vs k (us per 1000 iter).
(2) membership of uids in build_d1_v0.json moved/cut (+ any mention), with line numbers.
(x) offline terminal table (docs/wiki/subvi/D1_s1_copy.json 'terminals') for the tunnels of diagram 7911 and wires.
Prediction contract: 4 B legs found, stamps 1/iter (94-1 T14) so every iteration has sites 2,3,4 -> n_pairs == iterations-1.
Writes tools/bench/f7911_facts_94_offline.json; ends with a RESULT line.
"""
import json, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
from diag_c91_step4_stats import load, bucket, pct
import protocol

gates = []
def gate(name, ok, info=""):
    gates.append((name, bool(ok))); print("%s %s %s" % ("PASS" if ok else "FAIL", name, info), flush=True)

def fit(x, y):
    n = len(x); mx = sum(x) / n; my = sum(y) / n
    sxx = sum((a - mx) ** 2 for a in x); sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    return sxy / sxx if sxx else None

raw = json.load(open(os.path.join(HERE, "t0_step4v2_94_raw.json")))
out = {"part1": {}, "part2": {}, "terms": {}}
for r in raw["rows"]:
    if r["arm"] != "B" or not r.get("registered_ok"): continue
    d = os.path.join(ROOT, r["dir"]); S = load(d); f, I = S[0]; us = 1e6 / f
    last = {}
    for s in (2, 3, 4):
        m = {}
        for k, dt in bucket(I, S[s][1]): m[k] = max(m.get(k, 0), dt * us)
        last[s] = m
    ks = sorted(k for k in last[4] if k in last[3] and k in last[2] and k < len(I) - 1)
    t0, t1 = I[ks[0]], I[ks[-1]]
    rec = {"picks": r["picks"], "iterations": len(I), "n_pairs": len(ks)}
    for name, a in (("s4_minus_s3", 3), ("s4_minus_s2", 2)):
        y = [last[4][k] - last[a][k] for k in ks]
        bins = [[] for _ in range(10)]
        for k, v in zip(ks, y): bins[min(9, int(10 * (I[k] - t0) / (t1 - t0 + 1)))].append(v)
        rec[name] = {"bin_median_us": [round(pct(b, .5), 1) if b else None for b in bins], "bin_n": [len(b) for b in bins],
                     "slope_us_per_1000_iter": round(1000 * fit(ks, y), 2), "median_us": round(pct(y, .5), 1)}
    # iteration period too, same bins, for context
    per = [(I[k + 1] - I[k]) * us for k in ks]
    rec["period_slope_us_per_1000_iter"] = round(1000 * fit(ks, per), 2)
    out["part1"][r["leg"]] = rec
    gate("P1 %s pairs" % r["leg"], len(ks) >= len(I) - 2, "n_pairs=%d iters=%d" % (len(ks), len(I)))
    for nm in ("s4_minus_s3", "s4_minus_s2"):
        print("  %s %s bins=%s slope/1000it=%s" % (r["leg"], nm, rec[nm]["bin_median_us"], rec[nm]["slope_us_per_1000_iter"]), flush=True)
gate("P1 four B legs", len(out["part1"]) == 4, str(list(out["part1"])))

UIDS = [7911, 8634, 29009, 28233, 30306, 11310, 637, 639, 9087, 9227, 9025, 10177]
bj = os.path.join(HERE, "build_d1_v0.json"); B = json.load(open(bj)); lines = open(bj).read().splitlines()
sec = {}
for i, ln in enumerate(lines, 1):
    m = re.match(r'^ "(\w+)"', ln)
    if m: sec[m.group(1)] = i
moved = {e[1]: e[0] for e in B["moved"]}; cut = {e[0] for e in B["cut"]}
for u in UIDS:
    hits = [i for i, ln in enumerate(lines, 1) if re.search(r"(^|[^0-9])%d([^0-9]|$)" % u, ln)]
    out["part2"][u] = {"moved_to": moved.get(u), "cut": u in cut, "lines_mentioning": hits}
    print("  uid %d moved=%s cut=%s lines=%s" % (u, moved.get(u), u in cut, hits), flush=True)
out["part2"]["_sections"] = sec
gate("P2 membership computed", True, "moved lines %d-%d cut %d-%d" % (sec["moved"], sec["cut"] - 1, sec["cut"], sec["regs"] - 1))

T = json.load(open(os.path.join(ROOT, "docs", "wiki", "subvi", "D1_s1_copy.json")))["terminals"]
own = {}
for t in T: own.setdefault(t["owner_uid"], []).append(t)
wires = {}
for t in T: wires.setdefault(t["wire_uid"], []).append(t)
def brief(t): return "%s#%d t%d %s src=%s w%d d%s %s" % (t["owner_class"], t["owner_uid"], t["term_uid"], repr(t["term_name"]), t["is_source"], t["wire_uid"], t["frame_diagram"], t["term_class"])
on7911 = sorted({t["owner_uid"] for t in T if t["frame_diagram"] == 7911 and t["term_class"] in ("InnerTerminal",)})
out["terms"]["tunnels_with_inner_on_7911"] = on7911
for u in on7911 + [9025, 8634, 8741]:
    out["terms"][str(u)] = [brief(t) for t in own.get(u, [])]
for w in sorted({t["wire_uid"] for u in on7911 + [9025, 8634] for t in own.get(u, []) if t["wire_uid"]}):
    out["terms"]["w%d" % w] = [brief(t) for t in wires.get(w, [])]
for k, v in out["terms"].items(): print("  T %s: %s" % (k, v), flush=True)
json.dump(out, open(os.path.join(HERE, "f7911_facts_94_offline.json"), "w"), indent=1, default=str)
npass = sum(1 for _, ok in gates if ok); nfail = len(gates) - npass
print(protocol.result_line({"status": "PASS" if nfail == 0 else "FAIL", "gates": {"pass": npass, "fail": nfail},
      "first_fail": next((n for n, ok in gates if not ok), None), "artefacts": [{"path": "tools/bench/f7911_facts_94_offline.json", "md5": None}]}), flush=True)
