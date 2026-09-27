"""card 115-4 M3 follow-up (OFFLINE): overlay the selection masks of the UNPAIRED items (diag_c115d_sel.log:54-73) and measure
where each R1-only selection lands in the B3 frame relative to the B3-only selections (the retired left-inner stubs).
Reuses diag_c115d_sel.py's functions; coverage threshold relaxed to 0.3 for R1#13/#19 (sel.log:27,30 had 1 partner).
PREDICTION (alternative 23-6+7): each R1-only selection centroid lies within ~150 px (B3 frame) of some B3-only centroid
(both at loop #637's left shift registers). Outputs diag_c115d_sel2_<run>_<i>.png, diag_c115d_sel2.json, RESULT line."""
import hashlib, json, os, sys
import numpy as np
from PIL import Image
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import diag_c115d_sel as S                                                          # noqa: E402
import protocol                                                                     # noqa: E402

B = S.B
SEL = json.load(open(os.path.join(B, "diag_c115d_sel.json"), encoding="utf-8"))
UN = {"B3": SEL["b3_only"], "R1": SEL["r1_only"]}


def mask(t, k, runs):
    a, ms = runs[t][k], []
    for j in sorted(runs[t]):
        if j == k:
            continue
        dy, dx, pk = S.shift(runs[t][j], a)
        if pk < 0.12:
            continue
        m, cov = S.changed(runs[t][j], a, dy, dx)
        if m is None or cov.mean() < 0.3:
            continue
        ms.append((m, cov))
        if len(ms) >= 5:
            break
    if len(ms) < 2:
        return None, len(ms)
    return np.logical_and.reduce([m | ~c for m, c in ms]) & np.logical_or.reduce([c for _, c in ms]), len(ms)


def main():
    runs = {}
    for t, f in S.CAP.items():
        d = json.load(open(os.path.join(B, f), encoding="utf-8"))
        runs[t] = {it["index"]: S.pane(it["show_error"]["bd_after"]) for it in d["items"] if (it.get("show_error") or {}).get("bd_after")}
    M, out = {}, {"items": {}, "r1_to_b3": {}}
    for t in UN:
        for k in UN[t]:
            m, n = mask(t, k, runs)
            M[(t, k)] = m
            im = Image.open(S.M1["shots"][t][str(k)]).convert("RGB")
            if m is not None:
                arr = np.asarray(im).copy()
                ys, xs = np.nonzero(m)
                for dy in range(-2, 3):
                    arr[np.clip(ys + S.Y0 + dy, 0, arr.shape[0] - 1), np.clip(xs + S.X0, 0, arr.shape[1] - 1)] = (255, 0, 0)
                im = Image.fromarray(arr)
                c = (float(ys.mean()), float(xs.mean()))
            else:
                c = None
            im.save(os.path.join(B, "diag_c115d_sel2_%s_%d.png" % (t, k)))
            out["items"]["%s#%d" % (t, k)] = {"partners": n, "px": int(m.sum()) if m is not None else 0, "centroid_pane": c}
            print("MASK %s#%d partners %d px %s centroid %s" % (t, k, n, out["items"]["%s#%d" % (t, k)]["px"], c))
    # R1-only centroid mapped into each B3-only frame (b[y,x] ~ a[y+dy,x+dx] with a=R1 shot, b=B3 shot)
    for r in UN["R1"]:
        cr = out["items"]["R1#%d" % r]["centroid_pane"]
        row = {}
        for b in UN["B3"]:
            cb = out["items"]["B3#%d" % b]["centroid_pane"]
            dy, dx, pk = S.shift(runs["R1"][r], runs["B3"][b])
            if cr is None or cb is None or pk < 0.1:
                row[b] = None
                continue
            y, x = cr[0] - dy, cr[1] - dx
            row[b] = {"dist": round(float(np.hypot(y - cb[0], x - cb[1])), 1), "peak": round(pk, 3), "shift": [dy, dx]}
        out["r1_to_b3"][r] = row
        best = sorted((v["dist"], b) for b, v in row.items() if v)
        print("R1#%d -> nearest B3-only selections %s" % (r, best[:3]))
    gates = {"T1 every unpaired item has a mask": all(v is not None for v in M.values()),
             "T2 every R1-only centroid within 150 px of a B3-only centroid": all(
                 any(v and v["dist"] <= 150 for v in out["r1_to_b3"][r].values()) for r in UN["R1"])}
    out["gates"] = gates
    jp = os.path.join(B, "diag_c115d_sel2.json")
    json.dump(out, open(jp, "w", encoding="utf-8"), indent=1, default=str)
    for g_, v in gates.items():
        print("  GATE %s  %s" % ("PASS" if v else "FAIL", g_))
    n = sum(gates.values())
    print(protocol.result_line(protocol.make_result(n, len(gates) - n, next((k for k, v in gates.items() if not v), None),
                                                    [{"path": jp, "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}])))


if __name__ == "__main__":
    main()
