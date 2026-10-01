"""card 130-5 read-only: in each finalized plan's simulated END state, how many terminals sit in each Flat Sequence frame
(new:FS1.f0..f2)? stage_d1_ring_p3b1.py's FS/FU gates (UNVERIFIED in a dry) need every frame to hold created rows. No LabVIEW."""
import json, os, sys, collections
B = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(B))
import protocol as P
J = lambda p: json.load(open(p, encoding="utf-8"))
res = {}
for name in ("plan_ring_p3b1.json", "plan_ring_p3b2.json", "plan_ring_p3b.json"):
    pl = J(os.path.join(B, name))
    st = J(os.path.join(os.path.dirname(os.path.dirname(B)), pl["finalized"]["last_step"]["path"]))["state"]
    sym = st["sym"]
    fr = dict((k, sym[k]) for k in ("new:FS1.f0", "new:FS1.f1", "new:FS1.f2") if k in sym)
    if not fr and name == "plan_ring_p3b2.json":
        fr = {"new:FS1.f0": -2, "new:FS1.f1": -3, "new:FS1.f2": -4}
    cnt = collections.Counter(int(r["frame_diagram"] or 0) for r in st["terminals"])
    created = collections.Counter(int(r["frame_diagram"] or 0) for r in st["terminals"] if int(r["owner_uid"]) < 0)
    res[name] = dict((k, {"uid": u, "terminals": cnt.get(int(u), 0), "created_owner_terms": created.get(int(u), 0)}) for k, u in fr.items())
    print("FACT", name, json.dumps(res[name]))
ok = all(v["terminals"] > 0 for v in res["plan_ring_p3b1.json"].values())
print(("PASS" if ok else "FAIL") + "  F1 P3b-1 end state: every FS frame holds at least one terminal (FS/FU gates of the recipe)")
print(P.result_line(P.make_result(int(ok), int(not ok), None if ok else "F1 a P3b-1 FS frame holds no terminal")))
