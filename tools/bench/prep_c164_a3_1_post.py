# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_164-3-1.md
# ---
r"""prep_c164_a3_1_post - card 164-3-1 (OFFLINE, read-only): after prep_c164_a3_1_mk.py stopped at END1 (fatal), the md5 UNCHANGED list (tools, memory
model, graph, EL, the five VIs) and, read from the sim end step file, the Wire objects / terminal rows of w23460, w23489 (the other delete_wire of the
plan) and w23519. No file is written.
PREDICTION CONTRACT: every pinned md5 equal; w23460 and w23489 both 0 rows and both still in `objs` (stagesim.py:1446-1464 drops the Wire object only for a
  sourceless wire); w23519 rows t8494 src + t23450 / t23241 / t7606.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/prep_c164_a3_1_post.log -- py -u tools/bench/prep_c164_a3_1_post.py"""
import os, sys                                                                               # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, B)
import prep_plan_flow_lib as FL                                                              # noqa: E402
L, J, md5, ROOT, CD = FL.L, FL.J, FL.md5, FL.ROOT, FL.CD
gate = L.Gate(fatal_default=False)
PIN = {"tools/stagekit.py": "dd57c1ca", "tools/stage_shared.py": "b688edd4", "tools/stagexec.py": "a4df7e15", "tools/stagesim.py": "95a162ba",
       "tools/stage_prerun.py": "7605116f", "tools/bench/prep_plan_flow_lib.py": "34264f5e", "tools/bench/memory_model.json": "8fb432e4",
       "tools/bench/graph_ring_p5s02c_20261010_131658.json": "3d5196ab", "tools/bench/errorlist_expected_D1_ring_p5s02c_20261010_125755.json": "26d45c71",
       "tools/bench/plan_ring_p5s02r_in_pre164r3.json": "4d93c82d", "tools/bench/plan_ring_p5s02d_prev872822f3.json": "872822f3",
       os.path.join(CD, "D1_ring_p5s02c_20261010_125755.vi"): "564d8cbe", os.path.join(CD, "D1_ring_p5s02b_20261010_105511.vi"): "f9ae7751",
       os.path.join(CD, "D1_ring_p5s02a_20261010_023239.vi"): "94ffff94", os.path.join(CD, "D1_ring_p5s01b_20261009_123319.vi"): "7f2582ae",
       os.path.join(CD, "D1_ring_p4s09_20261009_060515.vi"): "eb1d0f31"}
for p, w in PIN.items():
    h = md5(os.path.join(ROOT, p))
    gate("U {0} == {1}".format(os.path.basename(p), w), h.startswith(w), h)
for p in ("tools/bench/plan_ring_p5s02d.json", "tools/bench/plan_ring_p5s02r_in.json"):
    print("FACT MD5 {0} {1}".format(md5(os.path.join(ROOT, p)), p), flush=True)
PL = J(os.path.join(ROOT, "tools/bench/plan_ring_p5s02d.json"))
last = max(PL["finalized"]["step_files"], key=lambda x: int(x["n"]))
END = J(os.path.join(ROOT, last["path"]))["state"]
base = J(os.path.join(ROOT, "tools/bench/graph_ring_p5s02c_20261010_131658.json"))
for w in (23460, 23489, 23519):
    rows = sorted((r["term_uid"], r["is_source"]) for r in END["terminals"] if r["wire_uid"] == w)
    obj = [o for o in END["objs"] if int(o["uid"]) == w]
    bobj = [o for o in base.get("objs") or [] if int(o["uid"]) == w]
    print("FACT ENDOBJ {0} w{1}: rows {2}; objs {3}; in base objs {4}".format(last["path"], w, rows, obj, bobj), flush=True)
sys.exit(gate.result())
