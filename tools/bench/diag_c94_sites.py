r"""diag_c94_sites.py - card 94-1: per-site summary from t0_step4v2_94_raw[_dry].json (no LabVIEW). Reuses the
diag_c91_step4_stats.table output already stored per B leg (stats_full). Counted legs = registered_ok only.
Per B leg per site: stamps, overflow (t0_meta: "site calls stored overflow"), delta median/p95 us; per loop period
median/p95/max. Per site: slope us/bead = (mean over B15 legs - mean over B11 legs)/4 (for delta median, delta p95,
last-in-iteration median, and loop period median/p95); repeat spread |B15a-B15b|, |B11a-B11b|; lost by arm and
stamped/unstamped lost ratio (mean B / mean A) at 11 and 15. Reports numbers only; no lever named.
    py tools/bench/diag_c94_sites.py [raw.json]  -> writes t0_step4v2_94[_dry].json next to it, prints a table
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))


def meta_overflow(sm):
    ov = {}
    for _, lines in (sm or {}).items():
        for ln in lines:
            p = ln.split()
            if len(p) == 4 and all(x.lstrip("-").isdigit() for x in p): ov[int(p[0])] = {"calls": int(p[1]), "stored": int(p[2]), "overflow": int(p[3])}
    return ov


def mean(a):
    a = [x for x in a if isinstance(x, (int, float))]
    return sum(a) / len(a) if a else None


def summarize(raw):
    R = json.load(open(raw)); legs = {}
    for r in R["rows"]:
        if not r.get("registered_ok"): continue
        L = {"arm": r["arm"], "picks": r["picks"], "lost": r["lost_frames"], "frames_delta": r["frames_delta"]}
        T = (R.get("stats_full") or {}).get(r["leg"])
        if r["arm"] == "B" and isinstance(T, dict) and "loops" in T:
            ov = meta_overflow(r.get("stamp_meta")); L["loops"] = {}
            for ln, Lp in T["loops"].items():
                if "period_us" not in Lp: L["loops"][ln] = {"missing": True}; continue
                pu = Lp["period_us"]; isite = Lp["i_site"]
                sites = {str(isite): {"stamps": Lp["iterations"], "overflow": (ov.get(isite) or {}).get("overflow")}}
                for s, S in Lp["sites"].items():
                    if "delta_us" not in S: sites[str(s)] = {"missing": True}; continue
                    sites[str(s)] = {"stamps": S["stamps"], "overflow": (ov.get(int(s)) or {}).get("overflow"), "per_iter_med": S["stamps_per_iteration"]["median"],
                                     "delta_med_us": S["delta_us"]["median"], "delta_p95_us": S["delta_us"]["p95"], "last_in_iter_med_us": S["last_in_iter_us"]["median"]}
                L["loops"][ln] = {"iterations": Lp["iterations"], "period_med_us": pu["median"], "period_p95_us": pu["p95"], "period_max_us": pu["max"], "sites": sites}
            L["overflow_sites"] = ov
        legs[r["leg"]] = L
    B = {n: [v for v in legs.values() if v["arm"] == "B" and v["picks"] == n and "loops" in v] for n in (11, 15)}
    slope = {}
    for ln in ("637_tracking", "15173_display", "25380"):
        per = {}
        for key in ("period_med_us", "period_p95_us"):
            a = [[l["loops"].get(ln, {}).get(key) for l in B[n]] for n in (11, 15)]
            per[key] = {"B11": a[0], "B15": a[1], "slope_us_per_bead": (mean(a[1]) - mean(a[0])) / 4 if mean(a[0]) is not None and mean(a[1]) is not None else None,
                        "spread_B11": abs(a[0][0] - a[0][1]) if len(a[0]) == 2 and None not in a[0] else None, "spread_B15": abs(a[1][0] - a[1][1]) if len(a[1]) == 2 and None not in a[1] else None}
        sites = set().union(*[set(l["loops"].get(ln, {}).get("sites", {})) for n in (11, 15) for l in B[n]]) if B[11] or B[15] else set()
        for s in sorted(sites, key=int):
            for key in ("delta_med_us", "delta_p95_us", "last_in_iter_med_us"):
                a = [[(l["loops"].get(ln, {}).get("sites", {}).get(s) or {}).get(key) for l in B[n]] for n in (11, 15)]
                if not any(x is not None for x in a[0] + a[1]): continue
                m11, m15 = mean(a[0]), mean(a[1])
                per["site%s %s" % (s, key)] = {"B11": a[0], "B15": a[1], "slope_us_per_bead": (m15 - m11) / 4 if m11 is not None and m15 is not None else None,
                                                "spread_B11": abs(a[0][0] - a[0][1]) if len(a[0]) == 2 and None not in a[0] else None,
                                                "spread_B15": abs(a[1][0] - a[1][1]) if len(a[1]) == 2 and None not in a[1] else None}
        slope[ln] = per
    lost = {}
    for v in legs.values(): lost.setdefault("%s%d" % (v["arm"], v["picks"]), []).append(v["lost"])
    ratio = {n: (mean(lost.get("B%d" % n, [])) / mean(lost.get("A%d" % n, []))) if mean(lost.get("A%d" % n, [])) else None for n in (11, 15)}
    ovt = sum(o["overflow"] for v in legs.values() for o in (v.get("overflow_sites") or {}).values())
    out = {"schema": "t0-step4v2/1", "card": "94-1 PD201", "raw": os.path.basename(raw), "legs": legs, "slope_15_vs_11": slope,
           "lost_by_arm": lost, "lost_ratio_B_over_A": ratio, "overflow_total": ovt,
           "missing_B_legs": {n: 2 - len(B[n]) for n in (11, 15)}, "note": "numbers only; no lever named, no equivalence judged"}
    sp = os.path.join(os.path.dirname(raw), "t0_step4v2_94%s.json" % ("_dry" if raw.endswith("_dry.json") else ""))
    json.dump(out, open(sp, "w"), indent=1, default=str)
    print("LOST %s ratio B/A %s overflow_total %s missing_B %s" % (json.dumps(lost), json.dumps(ratio), ovt, out["missing_B_legs"]), flush=True)
    for ln, per in slope.items():
        for k, v in per.items():
            print("SLOPE %-14s %-34s B11=%s B15=%s slope=%s spr11=%s spr15=%s" % (ln, k, v["B11"], v["B15"], v["slope_us_per_bead"], v["spread_B11"], v["spread_B15"]), flush=True)
    return sp, out


if __name__ == "__main__":
    summarize(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "t0_step4v2_94_raw.json"))
