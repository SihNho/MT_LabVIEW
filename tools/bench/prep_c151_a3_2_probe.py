# ---
# labview: none
# hardware: none
# ---
r"""prep_c151_a3_2_probe - card 151-a3-2 (OFFLINE, read-only; copy of the prep_c150_a3_5_probe.py pattern): prints the card input md5s, the s08 plan's
finalized base / step files / rebase block, the s08 sim end's sym table and FS keys, the s08 creation map, any pre-existing s09 file, v18 ops 185..202
(kinds, action ids, new: refs), and the FS #29721 question on BOTH the s08 sim end (END8) and the REAL s08 graph 44858dbf loaded by stagesim.base_state:
fs_unmeasured, owners of #29869 / #29721, diagrams entry, and stagesim._diag_chain(st, 29869, {}) (the call that raised at stagesim.py:1805-1807). Writes nothing.
PREDICTION CONTRACT: prints only; RESULT PASS when every card input md5 matches.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c151_a3_2_probe.log -- py -u tools/bench/prep_c151_a3_2_probe.py"""
import glob, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagesim as SS, stagexec as SX                                                       # noqa: E401,E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
card = J(os.path.join(B, "cards", "task_151-a3-2.json"))
bad = [(i["path"], md5(os.path.join(ROOT, i["path"])), i["md5"]) for i in card["inputs"] if md5(os.path.join(ROOT, i["path"])) != i["md5"]]
print("INPUTS bad", bad, flush=True)
P = J(os.path.join(B, "plan_ring_p4_s08v18.json"))
f = P["finalized"]
print("S08 plan md5", md5(os.path.join(B, "plan_ring_p4_s08v18.json")), "keys", sorted(P), flush=True)
print("S08 base", json.dumps(P.get("base"))[:600], flush=True)
print("S08 fin keys", sorted(f), flush=True)
print("S08 fin rebase", json.dumps(f.get("rebase"))[:1500], flush=True)
print("S08 step files first/last", f["step_files"][0], f["step_files"][-1], len(f["step_files"]), flush=True)
print("S08 open_rows", len(P.get("open_rows") or []), "end rows", len(f.get("end_cdiff_rows") or []), flush=True)
END8F = os.path.join(ROOT, f["step_files"][-1]["path"])
E = J(END8F)
st8 = E["state"]
print("END8", os.path.relpath(END8F, ROOT), md5(END8F), "state keys", sorted(st8), flush=True)
print("  sym", json.dumps(st8.get("sym"))[:1500], "neg", st8.get("neg"), "vi", st8.get("vi"), "md5", st8.get("md5"), flush=True)
print("CMAPS s08", sorted(glob.glob(os.path.join(B, "creation_map", "*s08*"))), flush=True)
for cm in sorted(glob.glob(os.path.join(B, "creation_map", "*s08*"))):
    print("  head", open(cm, encoding="utf-8").read()[:900], flush=True)
print("S09 existing", sorted(glob.glob(os.path.join(B, "*s09*")) + glob.glob(os.path.join(ROOT, "tools", "recipes", "*s09*")) + glob.glob(os.path.join(B, "sim", "*s09*"))), flush=True)
v18 = J(os.path.join(B, "plan_ring_p4_v18.json"))
A, OPS = v18["actions"], SX.compile_plan(v18)
print("V18 ops", len(OPS), "actions", len(A), flush=True)
for k in range(185, len(OPS) + 1):
    o = OPS[k - 1]
    for n in o["acts"]:
        a = A[n - 1]
        refs = dict((x, a.get(x)) for x in ("dest_diagram", "loop", "body", "parent", "uid", "diagram", "at", "src", "dst", "born_on", "on", "of", "as") if a.get(x) is not None)
        print("V18OP {0} kind {1} act #{2} {3} op {4} refs {5}".format(k, o["kind"], n, a["id"], a.get("op"), json.dumps(refs)[:500]), flush=True)
GRF = os.path.join(B, "graph_ring_p4s08_20261009_033522.json")
GR = J(GRF)
print("GRAPH s08 md5", md5(GRF), "keys", sorted(GR), "fs_measured keys", sorted((GR.get("fs_measured") or {})), flush=True)
print("GRAPH s08 fs_measured 29721", ((GR.get("fs_measured") or {}).get("fs_frames") or {}).get("29721"), flush=True)
for name, st in (("END8", None), ("REAL-s08", None)):
    try:
        s = SS.base_state(E["state"] if name == "END8" else GR, (P.get("context") or {}) if name == "END8" else (P.get("context") or {}))
    except Exception as ex:                                                                   # noqa: BLE001
        print("BASE {0} base_state raised {1!r}".format(name, ex), flush=True)
        continue
    print("BASE {0} fs_unmeasured {1}; owners 29869 {2} 29721 {3}; diagrams 29869 {4}; fs_frames 29721 {5}".format(
          name, s.get("fs_unmeasured"), (s.get("owners") or {}).get("29869"), (s.get("owners") or {}).get("29721"),
          (s.get("diagrams") or {}).get("29869"), (s.get("fs_frames") or {}).get("29721")), flush=True)
    try:
        print("BASE {0} _diag_chain(29869) -> {1}".format(name, SS._diag_chain(s, 29869, {})), flush=True)
    except Exception as ex:                                                                   # noqa: BLE001
        print("BASE {0} _diag_chain(29869) RAISED {1}: {2}".format(name, type(ex).__name__, ex), flush=True)
print(protocol.result_line(protocol.make_result(0 if bad else 1, 1 if bad else 0, "inputs" if bad else None, [])), flush=True)
