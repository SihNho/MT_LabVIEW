"""card 115-4 M3/M4 (OFFLINE, no LabVIEW): locate the Show-Error SELECTION in each loose-ends after-shot and pair B3 <-> R1 items.

Why: diag_c115d_m1.log:8-50 - whole-image pairing fails (Show Error scrolls to different viewports). Method: the diagram
pane (crop) of every after-shot is registered by phase correlation to other shots of the SAME run (identical diagram) -> the
pixels that change between two aligned views of one run are the two selections; the selection of item k = the changed
pixels common to >= 2 comparisons (a partner's own selection differs per partner). Then B3 item b and R1 item r are
registered to each other and b's selection mask is mapped into r's frame: same wire <=> high overlap.
PREDICTION: every loose item gets a non-empty selection mask; peer claim -> 23 pairs + 1 R1-only; alternative -> 17 + 6 + 7.
Outputs diag_c115d_sel.json, diag_c115d_sel_<run>_<i>.png (after-shot with the mask boxed). RESULT line at the end.
"""
import hashlib, json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol

B = os.path.dirname(os.path.abspath(__file__))
M1 = json.load(open(os.path.join(B, "diag_c115d_m1.json"), encoding="utf-8"))
CAP = {"B3": "errorlist_D1_l2_b3_20260928_032703_20260928_035208.json", "R1": "errorlist_D1_l2_r1_20260928_055441_20260928_060555.json"}
Y0, Y1, X0, X1 = 82, 1026, 12, 1908          # diagram pane inside the Block Diagram window capture (1936x1056)


def pane(p):
    return np.asarray(Image.open(p).convert("L"), dtype=np.float32)[Y0:Y1, X0:X1]


def shift(a, b):
    """(dy, dx, peak): b[y, x] ~ a[y + dy, x + dx]."""
    F = np.fft.fft2(a - a.mean()) * np.conj(np.fft.fft2(b - b.mean()))
    r = np.fft.ifft2(F / (np.abs(F) + 1e-6)).real
    dy, dx = np.unravel_index(int(r.argmax()), r.shape)
    h, w = a.shape
    dy, dx = (dy - h if dy > h // 2 else dy), (dx - w if dx > w // 2 else dx)
    return int(dy), int(dx), float(r.max())


def overlap(a, b, dy, dx):
    """views of a and b on their common area, both in b's frame: returns (a_part, b_part, (y0, y1, x0, x1) in b)."""
    h, w = b.shape
    y0, y1, x0, x1 = max(0, -dy), min(h, h - dy), max(0, -dx), min(w, w - dx)
    if y1 - y0 < 50 or x1 - x0 < 50:
        return None
    return a[y0 + dy:y1 + dy, x0 + dx:x1 + dx], b[y0:y1, x0:x1], (y0, y1, x0, x1)


def changed(a, b, dy, dx):
    o = overlap(a, b, dy, dx)
    if o is None:
        return None, None
    ap, bp, (y0, y1, x0, x1) = o
    m = np.zeros(b.shape, bool)
    m[y0:y1, x0:x1] = np.abs(ap - bp) > 40
    cov = np.zeros(b.shape, bool)
    cov[y0:y1, x0:x1] = True
    return m, cov


def main():
    runs, sel, gates = {}, {}, {}
    for t, f in CAP.items():
        d = json.load(open(os.path.join(B, f), encoding="utf-8"))
        runs[t] = {it["index"]: pane(it["show_error"]["bd_after"]) for it in d["items"] if (it.get("show_error") or {}).get("bd_after")}
    for t in runs:
        idx = sorted(runs[t])
        for k in [int(i) for i in M1[t]["loose_idx"]]:
            a = runs[t][k]
            masks = []
            for j in idx:
                if j == k:
                    continue
                dy, dx, pk = shift(runs[t][j], a)
                if pk < 0.15:
                    continue
                m, cov = changed(runs[t][j], a, dy, dx)
                if m is None or cov.mean() < 0.5:
                    continue
                masks.append((m, cov))
                if len(masks) >= 4:
                    break
            if len(masks) < 2:
                sel[(t, k)] = None
                print("SEL %s#%d: only %d usable partners" % (t, k, len(masks)))
                continue
            common = np.logical_and.reduce([m | ~c for m, c in masks]) & np.logical_or.reduce([c for _, c in masks])
            ys, xs = np.nonzero(common)
            sel[(t, k)] = common
            print("SEL %s#%d: partners %d, sel px %d, bbox y %s-%s x %s-%s" % (t, k, len(masks), common.sum(),
                  ys.min() if len(ys) else None, ys.max() if len(ys) else None, xs.min() if len(xs) else None, xs.max() if len(xs) else None))
            im = Image.open(M1["shots"][t][str(k)]).convert("RGB")
            if len(ys):
                ImageDraw.Draw(im).rectangle([xs.min() + X0 - 6, ys.min() + Y0 - 6, xs.max() + X0 + 6, ys.max() + Y0 + 6], outline="red", width=3)
            im.save(os.path.join(B, "diag_c115d_sel_%s_%d.png" % (t, k)))
    gates["S1 every loose item has a selection mask with >= 20 px"] = all(v is not None and v.sum() >= 20 for v in sel.values())
    # pair B3 <-> R1 by mapped selection overlap
    score = {}
    for (tb, b), mb in sel.items():
        if tb != "B3" or mb is None:
            continue
        for (tr, r), mr in sel.items():
            if tr != "R1" or mr is None:
                continue
            dy, dx, pk = shift(runs["B3"][b], runs["R1"][r])
            o = overlap(mb.astype(np.float32), mr.astype(np.float32), dy, dx)
            if o is None or pk < 0.1:
                continue
            ap, bp, _ = o
            inter = float((ap > 0.5).__and__(bp > 0.5).sum())
            score[(b, r)] = (round(inter / max(1.0, min(mb.sum(), mr.sum())), 3), round(pk, 3), dy, dx)
    res = {"score": {"%d-%d" % k: v for k, v in score.items()}, "pairs": [], "b3_only": [], "r1_only": []}
    used_r = set()
    for b in [int(i) for i in M1["B3"]["loose_idx"]]:
        c = sorted(((v[0], r) for (bb, r), v in score.items() if bb == b and r not in used_r), reverse=True)
        if c and c[0][0] >= 0.5:
            res["pairs"].append((b, c[0][1], c[0][0])); used_r.add(c[0][1])
            print("PAIR B3#%d <-> R1#%d overlap %.2f" % (b, c[0][1], c[0][0]))
        else:
            res["b3_only"].append(b); print("B3-ONLY #%d best %s" % (b, c[:2]))
    res["r1_only"] = [r for r in [int(i) for i in M1["R1"]["loose_idx"]] if r not in used_r]
    print("R1-ONLY", res["r1_only"])
    gates["S2 counts reconcile 23 - b3only + r1only == 24"] = 23 - len(res["b3_only"]) + len(res["r1_only"]) == 24
    res["gates"] = gates
    jp = os.path.join(B, "diag_c115d_sel.json")
    json.dump(res, open(jp, "w", encoding="utf-8"), indent=1)
    for g_, v in gates.items():
        print("  GATE %s  %s" % ("PASS" if v else "FAIL", g_))
    n = sum(gates.values())
    print(protocol.result_line(protocol.make_result(n, len(gates) - n, next((k for k, v in gates.items() if not v), None),
                                                    [{"path": jp, "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}])))


if __name__ == "__main__":
    main()
