"""latest_lag - offline (lean task latest): per leg of a legs json, the matched S1 frame index of every row (X/Y/Z bits, as
p63_align), the step histogram (frames advanced per row; step 1 = nothing lost), and the END LAG = frames written by the end
minus the last row's frame. Frames written by the end = v5's frame-counter delta + C, C calibrated on 0-lost legs (default 77:
p6fix P62 2536 - 2459, W40 2539 - 2461 = 78; also printed per leg as last_A - delta for 0-lost legs).
    py tools/bench/lean_bench/latest_lag.py <legs json> [...] [--c 77] [--out <json>]"""
import json, os, sys                                                                     # noqa: E401
from collections import Counter
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import p63_align as AL, m8b_replay_compare as M                                          # noqa: E401,E402
S1_REF = os.path.join(HERE, "out_20261013d", "run", "replay_s1_20261013_142928")


def seq_of(run_dir, ka):
    _i, tb = M.tra(run_dir)
    return [ka.get(k) for k in AL.keys(tb)]


def main(av):
    c = float(av[av.index("--c") + 1]) if "--c" in av else 77.0
    out = av[av.index("--out") + 1] if "--out" in av else None
    files = [a for i, a in enumerate(av) if a.endswith(".json") and (i == 0 or av[i - 1] not in ("--out",))]
    _i, ta = M.tra(S1_REF)
    ka = {k: i for i, k in enumerate(AL.keys(ta))}
    res = {}
    for f in files:
        d = json.load(open(f, encoding="utf-8"))
        for tag, r in d["legs"].items():
            rd = r.get("run_dir")
            if not rd or not os.path.isdir(rd):
                rd = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(HERE))), rd or "")
            if not os.path.isdir(rd):
                continue
            seq = seq_of(rd, ka)
            ok = [x for x in seq if x is not None]
            st = [b - a for a, b in zip(ok, ok[1:])]
            fd = r.get("frames_delta")
            k = "%s:%s" % (os.path.basename(os.path.dirname(f)), tag)
            res[k] = {"rows": len(seq), "unmatched": len(seq) - len(ok), "first": ok[0] if ok else None, "last": ok[-1] if ok else None,
                      "frames_delta": fd, "last_minus_delta": (ok[-1] - fd) if ok and fd is not None else None,
                      "end_lag": round(fd + c - ok[-1], 1) if ok and fd is not None else None,
                      "step_hist": dict(sorted(Counter(st).items())), "mean_step": round(sum(st) / len(st), 3) if st else None,
                      "max_step": max(st) if st else None, "lost": sum(s - 1 for s in st)}
            print(k, json.dumps(res[k]))
    if out:
        json.dump(res, open(out, "w", encoding="utf-8"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1:])
