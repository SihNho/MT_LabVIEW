r"""diag_c127_3_facts - card 127-3 (OFFLINE, no LabVIEW, no COM): read recorded files only.
Facts for PD258(c): IMAQ Copy terminal table (graph_harness_copyloop_c95.json SubVI #11), NamedUnbundler / Select objects and
their terminals in the P3a bed graph (donor candidates for create_primitive_nested), registered donors of OpPrimCopyNested_v0,
#6810 error out / error in rows on the P3a graph, frame 3 rows of the p3b plan.
PREDICTION: prints facts only; RESULT PASS when every file loads."""
import json, os, sys, collections                                           # noqa: E401
B = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(B))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, gscript as g, vigraph as V                          # noqa: E401,E402
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))     # noqa: E731
H = J("tools/bench/graph_harness_copyloop_c95.json")
print("HARNESS keys", list(H.keys()))
for r in H["terminals"]:
    if r["owner_uid"] == 11:
        print("  CP", json.dumps(r, sort_keys=True))
hobj = [o for o in H.get("objs", H.get("objects", [])) if int(o.get("uid", 0)) == 11]
print("  CP obj", hobj)
G = J("tools/bench/graph_ring_p3a_20261001_190155.json")
T, DD = V.dedupe_rows(G["terminals"])
cls = collections.Counter(o["class"] for o in G["objs"])
print("P3A classes", dict(cls))
for o in G["objs"]:
    if o["class"] in ("NamedUnbundler", "Select", "Unbundler", "Bundler", "NamedBundler") or "Select" in o["class"]:
        print("  OBJ", json.dumps(o, sort_keys=True)[:400])
        for r in T:
            if r["owner_uid"] == int(o["uid"]):
                print("     T", r["term_uid"], repr(r["term_name"]), r["is_source"], r["term_class"], r["wire_uid"], r["frame_diagram"])
for r in T:
    if r["owner_uid"] == 6810:
        print("  6810", r["term_uid"], repr(r["term_name"]), r["is_source"], r["term_class"], r["wire_uid"], r["frame_diagram"])
for wu in sorted(set(r["wire_uid"] for r in T if r["owner_uid"] == 6810 and "error" in r["term_name"] and r["wire_uid"])):
    print("  NET w%s" % wu, [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"], r["frame_diagram"]) for r in T if r["wire_uid"] == wu])
lab = g._c100("OpPrimCopyNested_v0")
print("DONORS", json.dumps(lab.get("donors"), sort_keys=True)[:3000])
print("C100 labels", g.C100_LABELS)
pl = J("tools/bench/plan_ring_p3b_in.json")
for a in pl["actions"]:
    if a.get("id") in ("p3b_copy", "p3b_ras_num3", "p3b_lw_num3", "p3b_lw_latest", "p3b_lr_num3", "p3b_x_bn_n3", "p3b_x_bn_latest", "p3b_x_img_src"):
        print("  ROW", json.dumps(a)[:700])
print("context", json.dumps(pl["context"])[:800])
print(P.result_line(P.make_result(1, 0, None)))
