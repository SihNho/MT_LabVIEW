r"""latest_picklag - offline, no LabVIEW (lean task latest retry): the per-pick lag of the W100 observer leg, from the data.
Pick log line (latestobs_build.py, one line per found=True call of the observer): Num[0..19], last, picked Num, picked slot, ms tick.
Per line: ring max = max(Num); lag at the pick = ring max - picked Num; unread = count(Num > last); in-write = count(Num == -1);
lag at save = the NEXT line's ring max - this picked Num (the newest frame when 1.2 comes back for the next pick, i.e. after this
row was written). Joined one-to-one, in order, with the leg's saved rows (column 0); fail1's W100 run is the comparison.
Also re-computes fail1's P62 / GAP / W40 / W100 own-number + X/Y/Z with p6fix_align (unchanged) from fail1's run dirs.
    py tools/bench/lean_bench/latest_picklag.py --log <picklog> --run <obs run dir> [--align <align json>] --out <json>
    py tools/bench/lean_bench/latest_picklag.py --recompute --out <json>"""
import collections, json, os, sys                                                         # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import p6fix_align as PA, m8b_replay_compare as M                                         # noqa: E401,E402
RUN1 = os.path.join(HERE, "out_latest", "run")
FAIL1 = {"P62": ("replay_s1_20261014_013257", "same"), "GAP": ("replay_s1_20261014_014456", "gap"),
         "W40": ("replay_s1_20261014_015700", "same"), "W100": ("replay_s1_20261014_020903", "same")}
S1_REF = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")
S1_GAP = os.path.join(HERE, "out_p63_s1gap", "run", "replay_s1_20261013_171345")


def hist(xs):
    return dict(sorted(collections.Counter(int(x) for x in xs).items()))


def dec(x):
    """the observer's Build Array came out U32 (I32 inputs + the U32 tick, latestobs_build run 2): an I32 value v < 0 is written
    as v + 2^32 (bit-exact). Buffer numbers are < 2^31, so x >= 2^31 -> x - 2^32 recovers the I32 exactly."""
    return x - 2 ** 32 if x >= 2 ** 31 else x


def parse(log):
    L = []
    for ln in open(log, encoding="utf-8", errors="replace"):
        if ln.strip():
            v = [int(round(float(x))) for x in ln.strip().split("\t")]
            L.append([dec(x) for x in v[:23]] + v[23:])
    bad = [i for i, v in enumerate(L) if len(v) != 24]
    return L, bad


def picklag(L):
    rows = []
    for i, v in enumerate(L):
        num, last, pk, sl, tk = v[:20], v[20], v[21], v[22], v[23]
        rmax = max(num)
        rows.append({"i": i, "tick": tk, "last": last, "picked": pk, "slot": sl, "ring_max": rmax, "lag_pick": rmax - pk,
                     "unread": sum(1 for n in num if n > last), "in_write": sum(1 for n in num if n == -1),
                     "slot_holds_picked": num[sl] == pk, "lag_save": (max(L[i + 1][:20]) - pk) if i + 1 < len(L) else None})
    return rows


def steps_of(col0):
    s = np.diff(np.asarray(col0, float)) if len(col0) > 1 else np.array([])
    return s


def summary(rows):
    lp = [r["lag_pick"] for r in rows]
    ls = [r["lag_save"] for r in rows if r["lag_save"] is not None]
    ti = np.diff([r["tick"] for r in rows]) % (2 ** 32) if len(rows) > 1 else np.array([])
    return {"lines": len(rows), "lag_pick_hist": hist(lp), "lag_pick_max": max(lp) if lp else None, "lag_pick_all_zero": all(x == 0 for x in lp),
            "unread_hist": hist(r["unread"] for r in rows), "in_write_hist": hist(r["in_write"] for r in rows),
            "slot_holds_picked_all": all(r["slot_holds_picked"] for r in rows),
            "lag_save_hist": hist(ls), "lag_save_mean": float(np.mean(ls)) if ls else None, "lag_save_max": max(ls) if ls else None,
            "dropped_at_pick_total": int(sum(r["unread"] - 1 for r in rows)),
            "tick_step_ms": {"mean": float(np.mean(ti)) if len(ti) else None, "min": int(np.min(ti)) if len(ti) else None,
                             "max": int(np.max(ti)) if len(ti) else None, "p99": float(np.percentile(ti, 99)) if len(ti) else None},
            "first": rows[:3], "last": rows[-3:]}


def join(rows, col0):
    pk = [r["picked"] for r in rows]
    c0 = [int(x) for x in col0]
    exact = pk == c0
    j, extra = 0, []                                   # col0 as an in-order subsequence of the picks; picks without a row listed
    for i, p in enumerate(pk):
        if j < len(c0) and p == c0[j]:
            j += 1
        else:
            extra.append((i, p))
    return {"log_lines": len(pk), "rows": len(c0), "one_to_one_in_order": exact, "rows_matched_in_order": j, "picks_without_row": extra[:20],
            "n_picks_without_row": len(extra)}


def run_col0(run_dir):
    info, t = M.tra(run_dir)
    return info, t[:, 0] if t is not None else None


def main(av):
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                        # noqa: E731
    out = arg("--out")
    R = {}
    if "--functest" in av:                             # the build's 14 test lines (7 found=True vectors, warm then cold), decoded
        import latest_build as LB                      # VEC + the Python reference only (module constants)
        L, bad = parse(arg("--functest"))
        want = [(num, last, LB.ref(num, last)) for num, last in LB.VEC if LB.ref(num, last)[2]] * 2
        chk = [{"k": i, "ok": len(v) == 24 and v[:20] == list(num) and v[20:23] == [last, r[0], r[1]], "line": v}
               for i, (v, (num, last, r)) in enumerate(zip(L, want))]
        R = {"lines": len(L), "want": len(want), "bad_len": bad, "all_equal": len(L) == len(want) and all(c["ok"] for c in chk),
             "n_ok": sum(c["ok"] for c in chk), "checks": chk}
    elif "--recompute" in av:
        os.makedirs(os.path.join(HERE, "out_latest2"), exist_ok=True)
        for leg, (d, mode) in FAIL1.items():
            a = PA.main(S1_REF, os.path.join(RUN1, d), mode, S1_GAP if mode == "gap" else None,
                        os.path.join(HERE, "out_latest2", "align_fail1_%s.json" % leg))
            st = steps_of(run_col0(os.path.join(RUN1, d))[1])
            R[leg] = {"run": d, "mode": mode, "rows": a["col0"]["rows"], "col0_own": a["col0"]["col0_own"],
                      "strictly_increasing": a["col0"]["col0_strictly_increasing"], "lost_from_col0": a["col0"]["lost_from_col0"],
                      "align": {k: a["align"].get(k) for k in ("matched", "unmatched", "lost", "damaged", "monotonic", "gap_hist") if k in a["align"]},
                      "align_keys": sorted(a["align"].keys()), "transrot_post_differ": a["transrot"]["post_init_differ"],
                      "step_hist": hist(st / (2 if mode == "gap" else 1))}
    else:
        L, bad = parse(arg("--log"))
        rows = picklag(L)
        R["parse_bad_lines"] = bad
        R["summary"] = summary(rows)
        info, c0 = run_col0(arg("--run"))
        R["run_info"] = info
        R["join"] = join(rows, c0)
        st = steps_of(c0)
        R["obs_step_hist"] = hist(st)
        f1 = run_col0(os.path.join(RUN1, FAIL1["W100"][0]))[1]
        R["fail1_w100_rows"] = len(f1)
        R["fail1_step_hist"] = hist(steps_of(f1))
        if arg("--align") and os.path.isfile(arg("--align")):
            a = json.load(open(arg("--align"), encoding="utf-8"))
            R["align"] = {"col0": a.get("col0"), "align": {k: v for k, v in (a.get("align") or {}).items() if not isinstance(v, list)}}
        R["per_pick"] = rows
    s = json.dumps(R, indent=1, default=str)
    print(s[:6000])
    if out:
        open(out, "w", encoding="utf-8").write(s)
    return R


# self-test: 3 picks of a 4-slot toy ring padded to 20 with -1
_T = [[5, 6, -1] + [-1] * 17 + [4, 6, 1, 100], [5, 6, 7, 8] + [-1] * 16 + [6, 8, 3, 202], [9, 6, 7, 8] + [-1] * 16 + [8, 9, 0, 305]]
_r = picklag(_T)
assert [x["lag_pick"] for x in _r] == [0, 0, 0] and [x["unread"] for x in _r] == [2, 2, 1] and [x["lag_save"] for x in _r] == [2, 1, None]
assert join(_r, [6, 8, 9])["one_to_one_in_order"] and join(_r, [6, 9])["n_picks_without_row"] == 1

if __name__ == "__main__":
    main(sys.argv[1:])
