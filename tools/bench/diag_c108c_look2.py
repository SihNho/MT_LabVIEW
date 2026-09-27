"""c108c look2: file layout, plan_disp actions, pre-order around group-B structures (offline)."""
import json, hashlib
B = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\V6_ParallelLoop\tools\bench"
for f in ("graph_l2a1_bed_20260927.json", "par1359_95_graph.json", "sim/disp/plan_disp.json"):
    raw = open(B + "\\" + f, "rb").read()
    print(f, "md5", hashlib.md5(raw).hexdigest(), "lines", raw.count(b"\n"))
p = json.load(open(B + r"\sim\disp\plan_disp.json", encoding="utf-8"))
for a in p["actions"]:
    print("ACT", json.dumps({k: v for k, v in a.items() if k != "why"})[:260])
print("OPEN", json.dumps(p["open_rows"])[:1500])
print("FINALIZED keys", list(p["finalized"].keys()))
for f in ("graph_l2a1_bed_20260927.json", "par1359_95_graph.json"):
    g = json.load(open(B + "\\" + f, encoding="utf-8"))
    print("==", f, g.get("md5"), "loops", [(L["loop_uid"], L["class"]) for L in g.get("loops", [])])
    objs = g["objs"]
    idx = {o["uid"]: i for i, o in enumerate(objs)}
    for s in (1359, 2222, 29874, 637, 10170, 23041, 23032):
        i = idx.get(s)
        if i is None:
            print(" no", s); continue
        seq = [(o["uid"], o["class"]) for o in objs[i:i + 14] if o["class"] not in ("Terminal", "InnerTerminal", "OuterTerminal")]
        print(" PRE", s, seq[:10])
    ow = g.get("owners", {})
    print(" owners for tunnels", {k: ow.get(k) for k in ("9087", "9227", "11363", "31051", "2276", "29172", "7911", "2235", "29894")})
