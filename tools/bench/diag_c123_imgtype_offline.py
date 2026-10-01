r"""diag_c123_imgtype_offline - card 123-1 S6 prep, OFFLINE (no LabVIEW): from the P2a bed graph diag_c122_graph_p2a.json (P2b added
only 10 objects on #4866 and touched no existing net, stage_d1_ring_p2b.log TD/D gates), list the IMAQ Create nodes #20436, #13938 and
every IMAQ Create whose frame diagram lies inside For #23093, their 'Image Type' terminal, its wire and the wire's SOURCE (uid, class).
PREDICTION: #20436 and #13938 found; >= 1 IMAQ Create inside #23093; each Image Type terminal either wired to one source or unwired."""
import json, os, sys                                                               # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                     # noqa: E402
G = json.load(open(os.path.join(ROOT, "tools", "bench", "diag_c122_graph_p2a.json"), encoding="utf-8"))
T, O, L = G["terminals"], G.get("objs") or [], G.get("loops") or []
print("objs keys", sorted(O[0].keys()) if O else None, "| loops keys", sorted(L[0].keys()) if L else None)
byuid = dict((int(o.get("uid", -1)), o) for o in O)
for u in (20436, 13938, 23093):
    print("OBJ", u, json.dumps(byuid.get(u), ensure_ascii=False)[:600])
    print("LOOP", u, json.dumps([lp for lp in L if int(lp.get("uid", lp.get("loop_uid", -1))) == u], ensure_ascii=False)[:600])
names = sorted(set(r["term_name"] for r in T if int(r["owner_uid"]) in (20436, 13938)))
print("TERMS of 20436/13938:", names)
for r in T:
    if int(r["owner_uid"]) in (20436, 13938):
        print("  T", json.dumps(r, ensure_ascii=False))
src = dict((int(r["wire_uid"]), r) for r in T if r["is_source"] and r["wire_uid"])
it = [r for r in T if "Image Type" in r["term_name"] or "image type" in r["term_name"].lower()]
print("ALL 'Image Type' terminals:", len(it))
for r in it:
    s = src.get(int(r["wire_uid"] or 0))
    print("  IT owner #{0} {1} frame {2} wire {3} -> source {4}".format(r["owner_uid"], r["owner_class"], r["frame_diagram"], r["wire_uid"],
          (s["owner_uid"], s["owner_class"], s["term_name"], s["frame_diagram"]) if s else "UNWIRED/none"))
print(protocol.result_line(protocol.make_result(1, 0, None, [])), flush=True)
