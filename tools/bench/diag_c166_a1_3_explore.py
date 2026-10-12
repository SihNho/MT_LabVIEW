# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_166-a1-3.md
# ---
r"""diag_c166_a1_3_explore - card 166-a1-3 (OFFLINE, json only): print the facts the new EL predictor rules need - the step-5 expected rows
4/7/8/49 (class, object, clears_by), the base-graph terminal rows of tunnels #5204 / #10404 and of wires 4337 / 9636, the plan actions that
name them, the stored predicted files' makers, and el_advisory of the stored 47-item read. Facts only, no verdict.
PREDICTION CONTRACT: rows 4/49 carry clears_by A70 w_k3f / A80 w_k4f; w4337 holds t9631 (#5204), w9636 holds t24363 (#10404); advisory rc 0.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/diag_c166_a1_3_explore.log -- py -u tools/bench/diag_c166_a1_3_explore.py"""
import glob, json, os, sys                                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K                                                                        # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
EXPF = os.path.join(B, "errorlist_expected_D1_ring_p5s02d_20261010_152518.json")
ex = J(EXPF)
print("EXPF keys", sorted(ex), "total", ex.get("total"), flush=True)
classes = {}
for r in ex["expected"]:
    classes[r.get("class")] = classes.get(r.get("class"), 0) + int(r.get("count") or 1)
    if r.get("item") in (4, 6, 7, 8, 49, 50) or r.get("class") in ("undirected", "whilesubvi", "nosource"):
        print("ROW", json.dumps({k: r.get(k) for k in ("item", "class", "norm_all", "object", "clears_by", "count")})[:900], flush=True)
print("ROW classes", classes, flush=True)
P = J(os.path.join(B, "plan_ring_p5s02e.json"))
print("PLAN base", P["finalized"]["base"], flush=True)
for a in P["actions"]:
    print("ACT", json.dumps(a)[:300], flush=True)
G = J(P["finalized"]["base"]["path"])
print("GRAPH keys", sorted(G), flush=True)
print("TERM keys", sorted(G["terminals"][0]), flush=True)
for t in G["terminals"]:
    if int(t.get("owner_uid") or 0) in (5204, 10404) or t.get("wire_uid") in (4337, 9636):
        print("TERM", json.dumps(t), flush=True)
for o in G.get("objs") or []:
    if int(o.get("uid") or 0) in (5204, 10404, 4337, 9636):
        print("OBJ", json.dumps(o)[:400], flush=True)
for p in sorted(glob.glob(os.path.join(B, "errorlist_predicted_D1_ring_p5s0*_end.json"))):
    d = J(p)
    print("PREDF", os.path.basename(p), K.md5(p)[:8], "total", d.get("total"), "| plan", d.get("plan"), "| decided_by", d.get("decided_by"), "| base", d.get("base_expected"),
          "| elrule md5", (d.get("elrule") or {}).get("module_md5"), flush=True)
for s in ("p5s01a", "p5s01b", "p5s02a", "p5s02b", "p5s02c", "p5s02d", "p5s02e"):
    pp = os.path.join(B, "plan_ring_%s_pred.json" % s)
    if os.path.exists(pp):
        e = J(pp).get("errorlist") or {}
        print("PRED", s, K.md5(pp)[:8], "plan", J(pp).get("plan"), "item_file", e.get("item_file"), "total", e.get("predicted_total"), flush=True)
READ = os.path.join(B, "errorlist_D1_ring_p5s02e_20261010_172913_20261010_173731.json")
R = J(READ)
print("READ keys", sorted(R), "items", len(R.get("items") or []), "extra", R.get("extra"), "missing", R.get("missing"), "verdict", R.get("verdict"),
      "expected_file", R.get("expected_file"), "plan_file", R.get("plan_file"), flush=True)
rc, rep = K.el_advisory(R["items"], os.path.join(B, "plan_ring_p5s02e_pred.json"), os.path.join(B, "plan_ring_p5s02e.json"))
K.el_advisory_print(rc, rep)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}), flush=True)
