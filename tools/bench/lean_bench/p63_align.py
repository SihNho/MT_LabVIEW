r"""p63_align - lean task P6-3: align every tracked row of a test leg with the S1 replay leg of the same recorded frames.
No LabVIEW. Reference A = S1 replay run dir (P6-2: out_20261013d/run/replay_s1_20261013_142928, 6321 rows, every frame,
lost 0). Test B = a P6-3 leg run dir. Row key = the 45 X/Y/Z cells (columns 3..), compared as f64 BITS (NaN bits too).
For each B row: the A row indices with the same key (S1 rows are DISTINCT over 20; a key seen twice in A is reported).
Outputs: matched / damaged (no A row has its key) / order (strictly increasing A index) / gaps between consecutive matched
rows (lost frames = sum of (gap - 1)) / gap-size histogram / column 0 and 1-2 facts.
    py tools/bench/lean_bench/p63_align.py <run_dir_A> <run_dir_B> [--out <json>]"""
import json, os, sys                                                                     # noqa: E401
from collections import Counter
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import m8b_replay_compare as M                                                           # noqa: E402


def keys(t):
    x = np.ascontiguousarray(t[:, 3:])
    return [bytes(r) for r in x.view("u1").reshape(len(t), -1)]


def align(ta, tb):
    ka, kb = keys(ta), keys(tb)
    idx = {}
    for i, k in enumerate(ka):
        idx.setdefault(k, []).append(i)
    dup_a = sum(1 for v in idx.values() if len(v) > 1)
    hit = [idx.get(k) for k in kb]
    m = [h[0] if h else None for h in hit]
    multi = sum(1 for h in hit if h and len(h) > 1)
    damaged = [j for j, v in enumerate(m) if v is None]
    seq = [v for v in m if v is not None]
    inc = all(b > a for a, b in zip(seq, seq[1:]))
    steps = [b - a for a, b in zip(seq, seq[1:])]
    gaps = [(j, s) for j, s in enumerate(steps) if s != 1]
    lost = sum(s - 1 for s in steps if s > 1)
    span = (seq[-1] - seq[0] + 1) if seq else 0
    return {"rows_A": len(ta), "rows_B": len(tb), "A_keys_seen_twice": dup_a, "B_rows_with_several_A": multi,
            "matched": len(seq), "damaged": len(damaged), "damaged_rows_first": damaged[:10],
            "first_A": seq[0] if seq else None, "last_A": seq[-1] if seq else None, "span_A": span,
            "strictly_increasing": inc, "non_increasing_steps": sum(1 for s in steps if s <= 0),
            "lost_in_span": lost, "span_minus_rows": span - len(seq),
            "gap_count": sum(1 for s in steps if s > 1), "gap_hist": dict(sorted(Counter(s - 1 for s in steps if s > 1).items())),
            "gaps_first": [(j, s - 1) for j, s in gaps[:25]], "seq_head": seq[:12], "seq_tail": seq[-5:]}


def col_facts(t):
    c0 = t[:, 0]
    d = np.diff(c0)
    return {"col0_head": c0[:6].tolist(), "col0_tail": c0[-3:].tolist(), "col0_diff_uniq_head": sorted(set(np.round(d, 9).tolist()))[:8],
            "col1_head": t[:3, 1].tolist(), "col2_head": t[:3, 2].tolist()}


def main(a, b, out=None):
    ia, ta = M.tra(a)
    ib, tb = M.tra(b)
    r = {"A": ia, "B": ib}
    if ta is None or tb is None:
        r["error"] = "tra parse failed"
    else:
        r["align"] = align(ta, tb)
        r["colA"], r["colB"] = col_facts(ta), col_facts(tb)
        ka = {k: i for i, k in enumerate(keys(ta))}
        pairs = [(float(tb[j, 0]), ka.get(k)) for j, k in enumerate(keys(tb))]
        off = Counter(round(c0 - i, 6) for c0, i in pairs if i is not None and c0 >= 0)
        r["colB0"] = {"rows_col0_eq_-1": int(np.sum(tb[:, 0] == -1)), "first_row_col0_ge0": int(np.argmax(tb[:, 0] >= 0)),
                      "col0_minus_A_index_hist": dict(sorted(off.items())[:12])}
        # P6-3 (written before the W legs were read): column 0 as an independent frame label. With BN Out == BN In (the W legs)
        # P6-2 showed col0 = (aligned S1 index) - 20 for index >= 20 and -1 below; lost frames counted from col0 alone.
        m = [(float(c0), i) for c0, i in pairs if i is not None]
        ge = [(c0, i) for c0, i in m if i >= 20]
        lab = [int(c0) + 20 for c0, i in ge]
        st = [b - a for a, b in zip(lab, lab[1:])]
        r["col0_label"] = {"rows_index_ge20": len(ge), "col0_eq_index_minus_20": sum(1 for c0, i in ge if c0 == i - 20),
                           "rows_index_lt20": len(m) - len(ge), "of_them_col0_eq_-1": sum(1 for c0, i in m if i < 20 and c0 == -1),
                           "lost_from_col0_labels": sum(s - 1 for s in st if s > 1), "col0_label_steps_le0": sum(1 for s in st if s <= 0)}
        h = r["align"]["gap_hist"]
        r["gap_classes"] = {"1-2": sum(v for k, v in h.items() if 1 <= k <= 2), "3-19": sum(v for k, v in h.items() if 3 <= k <= 19),
                            ">=20": sum(v for k, v in h.items() if k >= 20)}
    s = json.dumps(r, indent=1, default=str)
    print(s)
    if out:
        open(out, "w", encoding="utf-8").write(s)
    return r


_A = np.array([[0, 0, 0, 1, 1, 1], [0, 0, 0, 2, 2, 2], [0, 0, 0, 3, 3, 3], [0, 0, 0, 4, 4, 4]], float)
_B = np.array([[0, 0, 0, 1, 1, 1], [0, 0, 0, 3, 3, 3], [0, 0, 0, 9, 9, 9], [0, 0, 0, 4, 4, 4]], float)
_r = align(_A, _B)
assert _r["matched"] == 3 and _r["damaged"] == 1 and _r["lost_in_span"] == 1 and _r["strictly_increasing"] and _r["gap_hist"] == {1: 1}

if __name__ == "__main__":
    av = sys.argv[1:]
    o = av[av.index("--out") + 1] if "--out" in av else None
    main(av[0], av[1], o)
