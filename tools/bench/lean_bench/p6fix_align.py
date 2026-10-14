r"""p6fix_align - lean task p6fix: p63_align (X/Y/Z bit alignment of a test leg against the S1 replay leg) PLUS column 0 included:
every B row's column 0 must be the buffer number of the row's OWN frame (the frame whose X/Y/Z are on the row).
  mode same : own number = A's column 0 at the matched A index (S1 stores the frame's own buffer number; frame k = number k)
  mode gap  : own number = 2k+1 for matched A index k (the P6-3 gap wrapper gives frame k the number 2k+1); cross-checked
              against the S1-gap leg's column 0 where that leg has the frame (--s1gap <run dir>)
Also: trans/rot (columns 1, 2) bits vs A at the matched index, split at A's init boundary (first row after A's last change in
columns 1-2): post-init rows must be identical; init rows are reported as facts. No LabVIEW.
    py tools/bench/lean_bench/p6fix_align.py <run_dir_A> <run_dir_B> --mode same|gap [--s1gap <dir>] [--out <json>]"""
import json, os, sys                                                                     # noqa: E401
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.dirname(HERE))
import p63_align as AL, m8b_replay_compare as M                                          # noqa: E401,E402


def bits(x):
    return np.ascontiguousarray(np.asarray(x, float)).view("u8")


def col0_own(ta, tb, mode, s1gap=None):
    ka = {k: i for i, k in enumerate(AL.keys(ta))}
    m = [(j, ka.get(k)) for j, k in enumerate(AL.keys(tb))]
    rows, own, bad = len(tb), 0, []
    xg = {"rows_checked": 0, "equal": 0}
    for j, i in m:
        if i is None:
            bad.append((j, float(tb[j, 0]), None, None))
            continue
        want = float(ta[i, 0]) if mode == "same" else float(2 * i + 1)
        if mode == "gap" and s1gap is not None and i < len(s1gap):
            xg["rows_checked"] += 1
            xg["equal"] += int(float(s1gap[i, 0]) == want)
        if float(tb[j, 0]) == want:
            own += 1
        else:
            bad.append((j, float(tb[j, 0]), i, want))
    lab = [float(tb[j, 0]) for j, i in m]
    steps = np.diff(lab) if len(lab) > 1 else np.array([])
    return {"rows": rows, "col0_own": own, "col0_not_own": len(bad), "first_not_own": bad[:12],
            "col0_strictly_increasing": bool(np.all(steps > 0)), "s1gap_crosscheck": xg if mode == "gap" else None,
            "lost_from_col0": int(sum((s / (2 if mode == "gap" else 1)) - 1 for s in steps if s > (2 if mode == "gap" else 1)))}


def trans_rot(ta, tb):
    ch = np.where(np.any(np.diff(ta[:, 1:3], axis=0) != 0, axis=1))[0]
    b = int(ch[-1]) + 2 if len(ch) else 0              # the row after A's last CHANGED row (P6-2's B3 definition: last change row 100 -> 101)
    ka = {k: i for i, k in enumerate(AL.keys(ta))}
    m = [(j, ka.get(k)) for j, k in enumerate(AL.keys(tb))]
    post = [(j, i) for j, i in m if i is not None and i >= b]
    pre = [(j, i) for j, i in m if i is not None and i < b]
    diff_post = [(j, i, tb[j, 1:3].tolist(), ta[i, 1:3].tolist()) for j, i in post if not np.array_equal(bits(tb[j, 1:3]), bits(ta[i, 1:3]))]
    eq_pre = sum(1 for j, i in pre if np.array_equal(bits(tb[j, 1:3]), bits(ta[i, 1:3])))
    return {"A_init_boundary_row": b, "post_init_rows": len(post), "post_init_differ": len(diff_post), "post_first_diff": diff_post[:5],
            "init_rows": len(pre), "init_rows_equal_A_same_frame": eq_pre,
            "init_first": [(j, i, tb[j, 1:3].tolist(), ta[i, 1:3].tolist()) for j, i in pre[:3]],
            "init_last": [(j, i, tb[j, 1:3].tolist(), ta[i, 1:3].tolist()) for j, i in pre[-2:]],
            "B_init_trans_range": [float(np.min(tb[[j for j, _i in pre], 1])), float(np.max(tb[[j for j, _i in pre], 1]))] if pre else None,
            "B_init_nonfinite": int(np.sum(~np.isfinite(tb[[j for j, _i in pre], 1:3]))) if pre else 0}


def main(a, b, mode, s1gap_dir=None, out=None):
    ia, ta = M.tra(a)
    ib, tb = M.tra(b)
    r = {"A": ia, "B": ib, "mode": mode}
    if ta is None or tb is None:
        r["error"] = "tra parse failed"
    else:
        r["align"] = AL.align(ta, tb)
        sg = M.tra(s1gap_dir)[1] if s1gap_dir else None
        r["col0"] = col0_own(ta, tb, mode, sg)
        r["transrot"] = trans_rot(ta, tb)
        h = r["align"]["gap_hist"]
        r["gap_classes"] = {"1-2": sum(v for k, v in h.items() if 1 <= k <= 2), "3-19": sum(v for k, v in h.items() if 3 <= k <= 19),
                            ">=20": sum(v for k, v in h.items() if k >= 20)}
    s = json.dumps(r, indent=1, default=str)
    print(s)
    if out:
        open(out, "w", encoding="utf-8").write(s)
    return r


# self-test: A rows k = [k, t, r, xyz_k]; B = frames 0,1,3 with own numbers (same) / one lagged row
_A = np.array([[k, 0, 0, k + 1, k + 2, k + 3] for k in range(5)], float)
_B = _A[[0, 1, 3]].copy()
assert col0_own(_A, _B, "same")["col0_own"] == 3
_B[2, 0] = 1
assert col0_own(_A, _B, "same")["col0_not_own"] == 1
_G = _A[[0, 2]].copy(); _G[:, 0] = [1, 5]
assert col0_own(_A, _G, "gap")["col0_own"] == 2 and col0_own(_A, _G, "gap")["lost_from_col0"] == 1

if __name__ == "__main__":
    av = sys.argv[1:]
    arg = lambda k, d=None: av[av.index(k) + 1] if k in av else d                    # noqa: E731
    main(av[0], av[1], arg("--mode", "same"), arg("--s1gap"), arg("--out"))
