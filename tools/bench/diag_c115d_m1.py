"""card 115-4 M1/M4 (OFFLINE, no LabVIEW): loose-ends items of B3 vs R1 from the two Error List captures.

Existing tools checked: tools/lv_errorlist.py (capture), tools/errorlist_check.py (class/count licence compare; no uid:
UID_ROUTE errorlist_check.py:53). Items carry no uid, so identity = the Show-Error diagram screenshot (bd_after): Show
Error scrolls the diagram to the selected object, so the same wire in B3 and R1 should give a near-identical after-shot.

PREDICTION CONTRACT: B3 loose items 23, R1 loose items 24 (checker: 13+9+1 used + 1 extra). Pairing by downscaled
grey mean-abs-diff of bd_after: mutual best matches with diff < THR. Peer claim (1 new segment) predicts 23 paired,
1 R1 unpaired, 0 B3 unpaired; peer alternative (23-6+7) predicts 17 paired, 6 B3 unpaired, 7 R1 unpaired.
Writes tools/bench/diag_c115d_m1.json + contact sheets diag_c115d_sheet_*.png. Ends with a RESULT line.
"""
import json, os, sys
import numpy as np
from PIL import Image, ImageDraw
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import protocol

B = os.path.dirname(os.path.abspath(__file__))
CAP = {"B3": os.path.join(B, "errorlist_D1_l2_b3_20260928_032703_20260928_035208.json"),
       "R1": os.path.join(B, "errorlist_D1_l2_r1_20260928_055441_20260928_060555.json")}
THR = 6.0


def norm(s):
    return "".join(c for c in (s or "").lower() if c.isalnum())


def load(tag):
    d = json.load(open(CAP[tag], encoding="utf-8"))
    out, classes = [], {}
    for it in d["items"]:
        n = norm(it.get("raw")) + norm(it.get("reason"))
        k = ("loose" if "looseends" in n else "nosource" if "hasnosource" in n or "nosource" in norm(it.get("detail"))
             else "unconn" if "notconnectedtoanything" in norm(it.get("detail")) or "anything" in n else "other")
        if k == "loose" and "notconnectedtoanything" in norm(it.get("detail")) and "looseends" not in n:
            k = "unconn"
        classes[k] = classes.get(k, 0) + 1
        se = it.get("show_error") or {}
        out.append({"i": it["index"], "cls": k, "raw": it.get("raw"), "detail": (it.get("detail") or "")[:70],
                    "after": se.get("bd_after"), "before": se.get("bd_before"), "licensed_by": it.get("licensed_by")})
    return d, out, classes


def vec(p):
    im = Image.open(p).convert("L")
    w, h = im.size
    return np.asarray(im.resize((240, int(240 * h / w))), dtype=np.float32), (w, h)


def main():
    res, gates = {}, {}
    items = {}
    for tag in ("B3", "R1"):
        d, its, cls = load(tag)
        items[tag] = its
        res[tag] = {"n": len(its), "classes": cls, "loose_idx": [x["i"] for x in its if x["cls"] == "loose"]}
        print("FACT %s items %d classes %s" % (tag, len(its), cls))
        print("FACT %s loose idx %s" % (tag, res[tag]["loose_idx"]))
    L = {t: [x for x in items[t] if x["cls"] == "loose"] for t in items}
    for t in L:
        for x in L[t]:
            x["exists"] = bool(x["after"]) and os.path.exists(x["after"])
    gates["G1 B3 loose == 23"] = len(L["B3"]) == 23
    gates["G2 R1 loose == 24"] = len(L["R1"]) == 24
    gates["G3 every loose after-shot exists"] = all(x["exists"] for t in L for x in L[t])
    V = {t: [vec(x["after"])[0] if x["exists"] else None for x in L[t]] for t in L}
    shp = {t: sorted({v.shape for v in V[t] if v is not None}) for t in V}
    print("FACT shapes", shp)
    M = np.full((len(L["B3"]), len(L["R1"])), 999.0)
    for a, va in enumerate(V["B3"]):
        for b, vb in enumerate(V["R1"]):
            if va is not None and vb is not None and va.shape == vb.shape:
                M[a, b] = float(np.abs(va - vb).mean())
    pairs = []
    for a in range(M.shape[0]):
        b = int(M[a].argmin())
        if int(M[:, b].argmin()) == a and M[a, b] < THR:
            pairs.append((a, b, round(M[a, b], 2)))
    pa, pb = {p[0] for p in pairs}, {p[1] for p in pairs}
    ub = [a for a in range(M.shape[0]) if a not in pa]
    ur = [b for b in range(M.shape[1]) if b not in pb]
    for a, b, dv in pairs:
        print("PAIR B3#%d <-> R1#%d diff %.2f" % (L["B3"][a]["i"], L["R1"][b]["i"], dv))
    for a in ub:
        print("B3-ONLY #%d best R1#%d diff %.2f  %s" % (L["B3"][a]["i"], L["R1"][int(M[a].argmin())]["i"], M[a].min(),
                                                       os.path.basename(L["B3"][a]["after"])))
    for b in ur:
        print("R1-ONLY #%d best B3#%d diff %.2f  %s" % (L["R1"][b]["i"], L["B3"][int(M[:, b].argmin())]["i"],
                                                       M[:, b].min(), os.path.basename(L["R1"][b]["after"])))
    res["pairs"] = [(L["B3"][a]["i"], L["R1"][b]["i"], d) for a, b, d in pairs]
    res["b3_only"] = [L["B3"][a]["i"] for a in ub]
    res["r1_only"] = [L["R1"][b]["i"] for b in ur]
    res["diff_sorted_pairs"] = sorted(p[2] for p in pairs)
    res["shots"] = {t: {x["i"]: x["after"] for x in L[t]} for t in L}
    # contact sheets of the unpaired after-shots (for a visual read)
    for tag, idxs, lst in (("b3only", ub, L["B3"]), ("r1only", ur, L["R1"])):
        if not idxs:
            continue
        ims = [Image.open(lst[k]["after"]).convert("RGB") for k in idxs]
        w = 800
        ims = [im.resize((w, int(w * im.size[1] / im.size[0]))) for im in ims]
        H = sum(im.size[1] + 20 for im in ims)
        sheet = Image.new("RGB", (w, H), "white")
        y = 0
        dr = ImageDraw.Draw(sheet)
        for k, im in zip(idxs, ims):
            dr.text((4, y + 2), "%s item %d" % (tag, lst[k]["i"]), fill="red")
            sheet.paste(im, (0, y + 20))
            y += im.size[1] + 20
        p = os.path.join(B, "diag_c115d_sheet_%s.png" % tag)
        sheet.save(p)
        print("FACT sheet", p)
    gates["G4 loose counts reconcile: B3 - b3only + r1only == R1"] = \
        len(L["B3"]) - len(ub) + len(ur) == len(L["R1"])
    res["gates"] = gates
    json.dump(res, open(os.path.join(B, "diag_c115d_m1.json"), "w", encoding="utf-8"), indent=1)
    for g, v in gates.items():
        print("  GATE %s  %s" % ("PASS" if v else "FAIL", g))
    npass = sum(1 for v in gates.values() if v)
    import hashlib
    jp = os.path.join(B, "diag_c115d_m1.json")
    art = [{"path": jp, "md5": hashlib.md5(open(jp, "rb").read()).hexdigest()}]
    print(protocol.result_line(protocol.make_result(npass, len(gates) - npass,
                                                    next((g for g, v in gates.items() if not v), None), art)))


if __name__ == "__main__":
    main()
