r"""diag_c91_step4_stats.py - card 91-3: per-site time table from t0stamp files (PD197(b) bucketing), NO LabVIEW.
File format (t0stamp.c): int64 LE, [0] = QPC frequency, then stamps (ticks); one file per site per pid.
Sites (PD197(c) + t0_sites_s1_step3c_r2.json): loop #637 tracking: 0=`i`, 2 kernel, 3 Median#30306 For-tunnel,
4 Median#29009+FIR For-tunnel, 6 plot Z/dZ case-tunnel, 8 save trace; loop #15173 display: 10=`i`, 11 ImageToArray,
12 Flatten, 13 Draw, 16 circle/text case-tunnel; loop #25380: 20=`i`.
Bucketing: a stamp between the `i` stamps of iterations k and k+1 belongs to k; delta = stamp - i_k (us).
    py tools/bench/diag_c91_step4_stats.py <leg_dir> [...]   -> prints one table per dir
"""
import glob, json, os, struct, sys
LOOPS = {"637_tracking": (0, [2, 3, 4, 6, 8]), "15173_display": (10, [11, 12, 13, 16]), "25380": (20, [])}


def load(d):
    out = {}
    for p in glob.glob(os.path.join(d, "t0_site*.bin")):
        b = open(p, "rb").read(); v = struct.unpack("<%dq" % (len(b) // 8), b)
        site = int(os.path.basename(p)[7:9]); out.setdefault(site, (v[0], []))[1].extend(v[1:])
    return {s: (f, sorted(t)) for s, (f, t) in out.items()}


def pct(a, q):
    if not a: return None
    a = sorted(a); k = (len(a) - 1) * q; i = int(k)
    return a[i] if i == len(a) - 1 else a[i] + (a[i + 1] - a[i]) * (k - i)


def bucket(i_ticks, s_ticks):
    """for each stamp in s_ticks: (iteration k, delta ticks); stamps before the first i stamp are dropped."""
    import bisect
    res = []
    for t in s_ticks:
        k = bisect.bisect_right(i_ticks, t) - 1
        if k >= 0: res.append((k, t - i_ticks[k]))
    return res


def table(d):
    S = load(d); T = {"dir": d, "loops": {}}
    for name, (isite, members) in LOOPS.items():
        if isite not in S: T["loops"][name] = {"missing_i_site": isite}; continue
        f, I = S[isite]; us = 1e6 / f
        per = [(I[k + 1] - I[k]) * us for k in range(len(I) - 1)]
        L = {"i_site": isite, "iterations": len(I), "period_us": {"median": pct(per, .5), "p95": pct(per, .95), "max": max(per) if per else None},
             "span_s": (I[-1] - I[0]) / f if len(I) > 1 else 0, "sites": {}}
        for m in members:
            if m not in S: L["sites"][m] = {"missing": True}; continue
            B = bucket(I, S[m][1]); dl = [b[1] * us for b in B]; its = {}
            for k, _ in B: its[k] = its.get(k, 0) + 1
            L["sites"][m] = {"stamps": len(S[m][1]), "bucketed": len(B), "iterations_hit": len(its),
                             "stamps_per_iteration": {"median": pct(list(its.values()), .5), "max": max(its.values()) if its else None},
                             "delta_us": {"median": pct(dl, .5), "p95": pct(dl, .95), "max": max(dl) if dl else None, "min": min(dl) if dl else None}}
            # per-iteration LAST stamp of this site (For-body sites fire once per bead: the last one = the group's end)
            last = {}
            for k, dt in B: last[k] = max(last.get(k, 0), dt * us)
            L["sites"][m]["last_in_iter_us"] = {"median": pct(list(last.values()), .5), "p95": pct(list(last.values()), .95)}
        T["loops"][name] = L
    return T


if __name__ == "__main__":
    for d in sys.argv[1:]:
        print(json.dumps(table(d), indent=1))
