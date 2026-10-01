r"""diag_c123_ring_p3_routes - card 123-2 STEP 2: every op / verb / file P3 needs, checked OFFLINE with
protocol.check_requires (the same function `py tools/protocol.py requires` runs), plus a donor census for the
primitives create_primitive_nested needs (registered donors: facts_c100_oplabels.json:257-274 = Max & Min, Wait (ms)
only) found in the P2b END graph by terminal-name signature (a '$work' donor candidate; not a measurement).
Existing: stagexec.CREATE_ROUTES / ROUTE_VERBS (stagexec.py:198-236), connect_route (stagexec.py:853-955).
PREDICTION: R0 the requires list runs; missing items are FACTS, not failures (they are the card's stop-rule input).
    py tools/bgrun.py --material --max-min 1 --log tools/bench/diag_c123_ring_p3_routes.log -- py -u tools/bench/diag_c123_ring_p3_routes.py"""
import hashlib, json, os, sys                                                       # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                    # noqa: E402
END = "tools/bench/sim/ring_p2b/step_10_create.json"
LLB = r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb"
REQ = [("verb", "gscript.add_shift_reg"), ("verb", "gscript.wire_sr"), ("file", "tools/bench/opmodels/add_shift_reg.json"),
       ("file", "tools/bench/opmodels/wire_sr.json"),
       ("verb", "gscript.case_in"), ("verb", "gscript.case_frames"), ("verb", "gscript.tunnel_use_default"),
       ("verb", "gscript.create_flat_sequence"), ("verb", "gscript.flat_sequence_in"), ("verb", "stagekit.flat_sequence_in"),
       ("verb", "stagekit.create_local_read"), ("verb", "stagekit.create_local_write"), ("op", "OpCreateLocalRead_v0"),
       ("verb", "gscript.create_primitive_nested"), ("op", "OpPrimCopyNested_v0"), ("file", "OpWaitDonor_v0.vi"),
       ("file", "DonorRingConst_v0.vi"), ("verb", "stagekit.const_row"), ("op", "OpCreateConstOnTerm_v0"),
       ("verb", "gscript.drop_subvi"), ("file", LLB), ("file", LLB + r"\IMAQ Copy"),
       ("verb", "gscript.wire_const"), ("verb", "gscript.set_index_mode"), ("op", "OpSetIndexMode_v0"),
       ("verb", "connect_nested_v1"), ("file", "tools/bench/opmodels/connect_across_fs.json"),
       ("file", "tools/bench/opmodels/tunnel.json"), ("file", "tools/bench/opmodels/const.json")]
SIG = {"Not Equal?": {"x", "y", "x != y?"}, "Equal?": {"x", "y", "x = y?"}, "Increment": {"x", "x+1"},
       "Quotient & Remainder": {"x", "y", "x-y*floor(x/y)", "floor(x/y)"}, "Add": {"x", "y", "x+y"},
       "Boolean To (0,1)": {"Boolean", "(0,1)"}, "Select": {"s", "t", "f", "s? t: f"},
       "Replace Array Subset": {"array", "index", "new element/subarray", "output array"},
       "Index Array (1-D)": {"array", "index", "element"}, "IMAQ Copy": {"Image Src", "Image Dst", "Image Dst Out"}}
r = protocol.check_requires({"requires": [{"kind": k, "name": n} for k, n in REQ]})
for x in r["found"]:
    print("FOUND   %s %s -> %s" % (x["kind"], x["name"], x["cite"]), flush=True)
for x in r["missing"]:
    print("MISSING %s %s" % (x["kind"], x["name"]), flush=True)
st = json.load(open(os.path.join(ROOT, END), encoding="utf-8"))["state"]
own, cls = {}, {}
for t in st["terminals"]:
    own.setdefault(int(t["owner_uid"]), set()).add(t["term_name"])
    cls[int(t["owner_uid"])] = (t["owner_class"], int(t["frame_diagram"] or 0))
don = {}
for nm, sig in SIG.items():
    hits = sorted(u for u, names in own.items() if names == sig and u > 0)
    don[nm] = [{"uid": u, "class": cls[u][0], "diagram": cls[u][1], "src": "%s:terminals[owner_uid=%d]" % (END, u)} for u in hits[:5]]
    print("DONOR-CANDIDATE %s: %d exact-signature owners in the P2b end graph %s" % (nm, len(hits), [(d["uid"], d["class"], d["diagram"]) for d in don[nm]]), flush=True)
OUT = "tools/bench/routes_c123_ring_p3.json"
json.dump({"schema": "facts/1", "card": "123-2", "requires": r, "donor_candidates": don, "graph": END,
           "registered_prim_donors": "tools/bench/facts_c100_oplabels.json:257-274 (Max & Min, Wait (ms))"},
          open(os.path.join(ROOT, OUT), "w", encoding="utf-8"), indent=1)
m5 = hashlib.md5(open(os.path.join(ROOT, OUT), "rb").read()).hexdigest()
print(protocol.result_line(protocol.make_result(1, 0, None, artefacts=[{"path": OUT, "md5": m5}])), flush=True)
