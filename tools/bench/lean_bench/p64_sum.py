# ---
# labview: none
# hardware: none
# ---
r"""p64_sum - offline, read-only (P6-4 preparation P-3): lost frames of a leg from its saved tra file, the SAME formula for both arms
(plan section 3 item 3, ASSUME-2): lost = (last col0 - first col0 + 1) - rows. The VI indicator `Total Lost Frames` is only recorded
beside it (in P6 it counts camera-loop gaps only: W100 indicator "0" vs 1068). Also the per-arm ABBA summary and the PD217(f) gain
form of plan 9.1 as a computed FACT (the judgement stays the report's).
    py tools/bench/lean_bench/p64_sum.py --run <run dir> [--run ...]        -> one line per run
    py tools/bench/lean_bench/p64_sum.py --abba <p64_abba json>            -> per-arm lost + the criterion fact
    py tools/bench/lean_bench/p64_sum.py --dry                             -> the recorded W100 / W100OBS / P62 runs + a toy ABBA
tra read by m8b_replay_compare.tra (unchanged); step histogram by latest_picklag.hist."""
import json, os, sys                                                                      # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); BENCH = os.path.dirname(HERE); ROOT = os.path.dirname(os.path.dirname(BENCH))
sys.path.insert(0, HERE); sys.path.insert(0, BENCH); sys.path.insert(0, os.path.join(ROOT, "tools"))
import m8b_replay_compare as M, latest_picklag as LP, protocol as P                       # noqa: E401,E402


def lost_col0(c0):
    """Column-0 lost frames of one leg: (last - first + 1) - rows; with the step histogram and the strictly-increasing flag.
    Returns {rows, first, last, lost, strictly_increasing, steps}. Self-check: the assert below."""
    c = [int(x) for x in c0]
    if not c:
        return {"rows": 0, "first": None, "last": None, "lost": None, "strictly_increasing": None, "steps": {}}
    st = np.diff(np.asarray(c, dtype=np.int64))
    return {"rows": len(c), "first": c[0], "last": c[-1], "lost": (c[-1] - c[0] + 1) - len(c),
            "strictly_increasing": bool((st > 0).all()), "steps": LP.hist(st)}


assert lost_col0([0, 1, 3, 5, 6]) == {"rows": 5, "first": 0, "last": 6, "lost": 2, "strictly_increasing": True, "steps": {1: 2, 2: 2}}


def run_sum(run_dir, npick=None, hz=None, run_s=None):
    """lost_col0 of a run dir's tra file + tra parse facts (dims, cols == 3 + 3N when npick is given) + the measured row rate
    (rows / run_s) when run_s is given. Returns a dict; {"error": ...} when the tra cannot be read."""
    try:
        info, t = M.tra(run_dir)
    except Exception as e:                                                                # noqa: BLE001
        return {"run_dir": run_dir, "error": repr(e)[:300]}
    if t is None:
        return {"run_dir": run_dir, "error": "tra not parsed", "tra": info}
    r = dict(lost_col0(t[:, 0]), run_dir=run_dir, dims=info["dims"], parsed=info["parsed"])
    if npick:
        r["cols_eq_3_3N"] = info["dims"][1] == 3 + 3 * int(npick)
    if hz and run_s:
        r["rows_per_s"] = round(r["rows"] / float(run_s), 2)
    return r


def abba_summary(rows):
    """Per-arm lost (col0) of the counted legs (registered_ok, not refused) and the plan-9.1 frames criterion as a FACT:
    met when there are 2 A and 2 B legs and every B < min(A) - 0.25 * mean(A). rows: dicts with arm, lost_col0, registered_ok."""
    arm = {}
    for r in rows:
        if r.get("registered_ok") and not r.get("refused") and r.get("arm") in ("A", "B") and isinstance(r.get("lost_col0"), int):
            arm.setdefault(r["arm"], []).append(r["lost_col0"])
    A, B = arm.get("A", []), arm.get("B", [])
    out = {"lost_by_arm": arm, "criterion": "every B < min(A) - 0.25 * mean(A) (PD217(f) gain form, plan 9.1)"}
    if len(A) == 2 and len(B) == 2:
        lim = min(A) - 0.25 * float(np.mean(A))
        out.update({"limit": lim, "met": all(b < lim for b in B)})
    else:
        out.update({"limit": None, "met": None, "why": "needs 2 A and 2 B counted legs, have %d / %d" % (len(A), len(B))})
    return out


_toy = [{"arm": a, "lost_col0": v, "registered_ok": True} for a, v in (("A", 3000), ("B", 200), ("B", 300), ("A", 3400))]
assert abba_summary(_toy)["met"] is True and abba_summary([dict(_toy[1], lost_col0=2600)] + _toy[:1] + _toy[2:])["met"] is False

DRY_RUNS = {"W100 p6close": ("out_p6close/run/replay_s1_20261014_043654", {"rows": 1472, "first": 0, "last": 2539, "lost": 1068, "steps": {1: 403, 2: 1068}}),
            "W100OBS latest": ("out_latest2/run/replay_s1_20261014_033411", {"rows": 1474, "first": 0, "last": 2541, "lost": 1068, "steps": {1: 405, 2: 1068}}),
            "P62 p6close": ("out_p6close/run/replay_s1_20261014_040041", {"rows": 2540, "first": 0, "last": 2539, "lost": 0, "steps": {1: 2539}})}


def dry():
    G = {}
    for tag, (rel, want) in DRY_RUNS.items():
        r = run_sum(os.path.join(HERE, *rel.split("/")), npick=15)
        print("RUN %s %s" % (tag, json.dumps({k: v for k, v in r.items() if k != "run_dir"}, default=str)), flush=True)
        G["D %s == %s" % (tag, want)] = all(r.get(k) == v for k, v in want.items()) and r.get("strictly_increasing") is True and r.get("cols_eq_3_3N") is True
    s1 = abba_summary(_toy)
    s2 = abba_summary([dict(_toy[1], lost_col0=2600)] + _toy[:1] + _toy[2:])
    print("ABBA toy %s | %s" % (json.dumps(s1), json.dumps(s2)), flush=True)
    G["D toy ABBA: met True, then False with B 2600"] = s1["met"] is True and s2["met"] is False
    return G


if __name__ == "__main__":
    av = sys.argv[1:]
    if "--dry" in av:
        G = dry()
    elif "--abba" in av:
        d = json.load(open(av[av.index("--abba") + 1], encoding="utf-8"))
        s = abba_summary(d.get("rows") or [])
        print(json.dumps(s, indent=1)); G = {"S summary computed": True}                # noqa: E702
    else:
        G = {}
        for i, a in enumerate(av):
            if a == "--run":
                r = run_sum(av[i + 1]); print(json.dumps(r, default=str)); G["S %s read" % os.path.basename(av[i + 1])] = "error" not in r   # noqa: E702
    for k, v in G.items():
        print("GATE %-90s %s" % (k, "PASS" if v else "FAIL"), flush=True)
    bad = [k for k, v in G.items() if not v]
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None)), flush=True)
    sys.exit(1 if bad or not G else 0)
