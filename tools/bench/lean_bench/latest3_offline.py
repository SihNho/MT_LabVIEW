r"""latest3_offline - offline, no LabVIEW (lean task latest retry 2). Reads only, except --move-cut (one rename inside out_latest2).
    py tools/bench/lean_bench/latest3_offline.py gates                 -> the 6 failing build gates re-checked with the stated U32 decode
    py tools/bench/lean_bench/latest3_offline.py move-cut              -> out_latest2\picklog_w100.txt -> picklog_w100_cut_20261014_0308.txt
    py tools/bench/lean_bench/latest3_offline.py run <log> <run dir> <align out json> <out json> [--no-align]
         -> p6fix_align (mode same) on the run + per-pick lag (latest_picklag) + the constant join + the last-pick facts
U32 decode (stated): the observer's Build Array came out U32 (I32 Num/last/picked/slot + the U32 tick); a logged v >= 2^31 is read
as v - 2^32. Lossless: I32 -> U32 keeps the bits, buffer numbers are < 2^31, the only negative value is the -1 marker."""
import json, os, sys                                                                     # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import latest_picklag as LP, p6fix_align as PA                                           # noqa: E401,E402
O2 = os.path.join(HERE, "out_latest2")
# fail1's functional-test vectors and Python reference (latest_build.py:35-43, copied; that module imports the LabVIEW driver)
R3, R5, I20 = [20, 21, 22] + list(range(3, 20)), [-1, 21, 22] + list(range(3, 20)), list(range(20))
VEC = [([-1] * 20, -1), (I20, 4), (R3, 5), (R3, 19), (R5, 20), (R5, 22), (I20, 19), (R3, 21), ([7] + [-1] * 19, -1),
       ([41, 42, 43, 44, -1] + list(range(25, 40)), 24)]


def ref(num, last):
    m = [n if n > last else last for n in num]
    v = max(m)
    return [v, m.index(v), last < v]


def dec(x):
    return x - 2 ** 32 if x >= 2 ** 31 else x


def gates():
    b = json.load(open(os.path.join(HERE, "latestobs_build.json"), encoding="utf-8"))
    out = {"recorded": {"pass": b["gates"]["pass"], "fail": b["gates"]["fail"], "failing": b["gates"]["failing"]}, "vectors": []}
    for phase in ("vectors_warm", "vectors_cold"):
        for v in b["obs"][phase]:
            num, last = VEC[v["k"] - 1]
            r = ref(num, last)
            want_line = list(num) + [last, r[0], r[1]] if r[2] else None
            raw = v["line"]
            e = {"phase": phase, "k": v["k"], "outputs_equal_ref": v["got"] == r, "lines_added": v["lines_added"],
                 "want_lines": 1 if r[2] else 0}
            if raw is not None:
                e["raw_equal"] = raw[:23] == want_line
                e["decoded_equal"] = [dec(x) for x in raw[:23]] == want_line
                e["has_u32_marker"] = any(x >= 2 ** 31 for x in raw[:23])
            out["vectors"].append(e)
    V = out["vectors"]
    failing = [e for e in V if e.get("raw_equal") is False]
    out["n_raw_fail"] = len(failing)
    out["n_raw_fail_equal_after_decode"] = sum(1 for e in failing if e["decoded_equal"])
    out["failing_keys"] = ["%s k%d" % (e["phase"], e["k"]) for e in failing]
    out["all_outputs_equal_ref"] = all(e["outputs_equal_ref"] for e in V)
    out["all_line_counts_right"] = all(e["lines_added"] == e["want_lines"] for e in V)
    out["all_lines_equal_after_decode"] = all(e.get("decoded_equal", True) for e in V)
    # the moved functest text file (14 lines = 7 found vectors x warm + cold), same decode
    ft = os.path.join(O2, "picklog_functest_20261014_025316.txt")
    L, bad = LP.parse(ft)
    want = [list(num) + [last] + ref(num, last)[:2] for num, last in VEC if ref(num, last)[2]] * 2
    out["functest_file"] = {"lines": len(L), "want": len(want), "bad_len": bad,
                            "equal_after_decode": len(L) == len(want) and all(v[:23] == w for v, w in zip(L, want))}
    return out


def move_cut():
    a, b = os.path.join(O2, "picklog_w100.txt"), os.path.join(O2, "picklog_w100_cut_20261014_0308.txt")
    if os.path.exists(b):
        return {"moved": False, "why": "target exists", "src_exists": os.path.exists(a)}
    if not os.path.exists(a):
        return {"moved": False, "why": "no source"}
    n = sum(1 for ln in open(a, encoding="utf-8", errors="replace") if ln.strip())
    st = os.stat(a)
    os.rename(a, b)
    return {"moved": True, "lines": n, "bytes": st.st_size, "mtime": st.st_mtime, "to": b, "src_gone": not os.path.exists(a)}


def run(log, rdir, align_out, out, do_align=True):
    R = {"log": log, "run": rdir}
    if do_align:
        a = PA.main(PA_S1, rdir, "same", None, align_out)
    else:
        a = json.load(open(align_out, encoding="utf-8"))
    R["align_col0"] = a.get("col0")
    R["align"] = {k: v for k, v in (a.get("align") or {}).items() if not isinstance(v, list) or len(v) < 30}
    R["transrot"] = a.get("transrot")
    L, bad = LP.parse(log)
    rows = LP.picklag(L)
    R["parse_bad"] = bad
    R["summary"] = LP.summary(rows)
    info, c0 = LP.run_col0(rdir)
    c0 = [int(x) for x in c0]
    R["rows"] = len(c0)
    pk = [r["picked"] for r in rows]
    const = pk[0] - c0[0]
    R["constant"] = {"first_picked": pk[0], "row0_col0": c0[0], "constant": const}
    sub = [p - const for p in pk]
    n = min(len(sub), len(c0))
    R["join"] = {"log_lines": len(pk), "rows": len(c0), "first_n_equal_in_order": sub[:len(c0)] == c0,
                 "mismatch_idx": [i for i in range(n) if sub[i] != c0[i]][:20],
                 "extra_picks_after_last_row": [{"i": i, "picked": pk[i], "minus_const": sub[i]} for i in range(len(c0), len(pk))]}
    st = np.diff(c0)
    R["col0_steps"] = LP.hist(st)
    R["lost_from_col0"] = int(sum(s - 1 for s in st))
    R["span"] = [c0[0], c0[-1]]
    # last-pick facts: ticks (ms) of the last lines, the spacing before, the lag-at-save of the last saved pick, file mtimes
    tk = [r["tick"] for r in rows]
    dt = list(np.diff(tk) % (2 ** 32))
    R["last_pick"] = {"last_lines": rows[-3:], "tick_steps_last5": [int(x) for x in dt[-5:]],
                      "tick_step_median": float(np.median(dt)) if dt else None,
                      "log_mtime": os.path.getmtime(log),
                      "tra_mtime": os.path.getmtime(os.path.join(rdir, "tra001-000")) if os.path.exists(os.path.join(rdir, "tra001-000")) else None}
    R["per_pick_lag_at_pick_all_zero"] = all(r["lag_pick"] == 0 for r in rows)
    json.dump({**R, "per_pick": rows}, open(out, "w", encoding="utf-8"), indent=1, default=str)
    return R


PA_S1 = LP.S1_REF

if __name__ == "__main__":
    av = sys.argv[1:]
    if av[0] == "gates":
        R = gates()
        json.dump(R, open(os.path.join(O2, "latest3_gates.json"), "w", encoding="utf-8"), indent=1)
        print(json.dumps({k: v for k, v in R.items() if k != "vectors"}, indent=1))
    elif av[0] == "move-cut":
        print(json.dumps(move_cut()))
    elif av[0] == "run":
        R = run(av[1], av[2], av[3], av[4], "--no-align" not in av)
        print(json.dumps(R, indent=1, default=str)[:9000])
