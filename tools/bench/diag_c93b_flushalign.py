r"""diag_c93b_flushalign.py - card 93-2 part (1), PD200(c)(1): OFFLINE, no LabVIEW. For the 92-3 B legs (leg2/leg3), the
top-15 tracking-loop periods (site 00 = loop #637 `i`, period k = I[k+1]-I[k]) with iteration index k, distance to the
nearest m*1024-1 (v1 flushes site s inside the call whose per-site index is 1023 mod 1024, t0stamp.c:74-78), and which
sites' flush calls (any site, any loop) fall inside that period's [I[k], I[k+1]) window.
FOUND FIRST: diag_c91_step4_stats.load (file reader, imported); nothing else existed for flush alignment.
PREDICTION CONTRACT: F1 both legs' site-00 files load (>= 10000 stamps)  F2 15 rows per leg  F3 json written.
Alignment is REPORTED, not judged (card rule).
    py -u tools/bench/diag_c93b_flushalign.py
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P                                                            # noqa: E402
import diag_c91_step4_stats as ST                                               # noqa: E402
LD = os.path.join(HERE, "t0_legs", "c92c_abba8_20260926_091948"); LEGS = ["leg2_B_p8_a1", "leg3_B_p8_a1"]
G, OUT = {}, {"schema": "t0-flushalign/1", "card": "93-2 (1)", "src": os.path.relpath(LD, ROOT), "legs": {}}
for leg in LEGS:
    S = ST.load(os.path.join(LD, leg)); f, I = S.get(0, (None, []))
    G["F1 %s site00 >= 10000 stamps" % leg] = len(I) >= 10000
    if not I: continue
    us = 1e6 / f; per = [(I[k + 1] - I[k]) * us for k in range(len(I) - 1)]
    flushes = []                                                                # (tick, site, per-site index)
    for s, (_, T) in S.items():
        flushes += [(T[j], s, j) for j in range(1023, len(T), 1024)]
    flushes.sort(); srt = sorted(per); med = srt[len(srt) // 2]
    rows = []
    for k in sorted(range(len(per)), key=lambda k: -per[k])[:15]:
        m = round((k + 1) / 1024); d = k - (m * 1024 - 1)
        inwin = [(s, j) for t, s, j in flushes if I[k] <= t < I[k + 1]]
        rows.append({"iter": k, "period_ms": round(per[k] / 1e3, 3), "nearest_k1024m1": m * 1024 - 1, "dist": d,
                     "flush_calls_in_period": ["s%02d#%d" % x for x in inwin]})
    # all periods that contain ANY flush call vs those that do not (reported, not judged)
    fl_k = set()
    import bisect
    for t, s, j in flushes:
        k = bisect.bisect_right(I, t) - 1
        if 0 <= k < len(per): fl_k.add(k)
    wf = sorted(per[k] for k in fl_k); nf = sorted(per[k] for k in range(len(per)) if k not in fl_k)
    q = lambda a, p: round(a[min(len(a) - 1, int(p * (len(a) - 1)))] / 1e3, 3) if a else None   # noqa: E731
    OUT["legs"][leg] = {"iterations": len(I), "period_median_ms": round(med / 1e3, 3), "top15": rows,
                        "flush_calls_total": len(flushes), "periods_with_flush": {"n": len(wf), "median_ms": q(wf, .5), "p95_ms": q(wf, .95), "max_ms": q(wf, 1)},
                        "periods_without_flush": {"n": len(nf), "median_ms": q(nf, .5), "p95_ms": q(nf, .95), "max_ms": q(nf, 1)},
                        "top15_with_flush": sum(1 for r in rows if r["flush_calls_in_period"])}
    G["F2 %s 15 rows" % leg] = len(rows) == 15
    for r in rows: print("%s iter %6d  %8.3f ms  dist %+5d  flush %s" % (leg, r["iter"], r["period_ms"], r["dist"], ",".join(r["flush_calls_in_period"])[:120]), flush=True)
    print("%s SUMMARY %s" % (leg, json.dumps({k: v for k, v in OUT["legs"][leg].items() if k != "top15"})), flush=True)
jp = os.path.join(HERE, "t0_flushalign_93.json"); OUT["gates"] = G; json.dump(OUT, open(jp, "w"), indent=1)
G["F3 json written"] = os.path.isfile(jp)
for k, v in G.items(): print("GATE %-40s %s" % (k, "PASS" if v else "FAIL"), flush=True)
bad = [k for k, v in G.items() if not v]
import hashlib
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(jp, ROOT), "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}])), flush=True)
sys.exit(1 if bad else 0)
