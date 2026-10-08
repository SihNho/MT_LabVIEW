# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_5_probe - card 150-a3-5 (OFFLINE, read-only): prints the s07 plan's finalized base / step files / rebase block, the s07 sim
end's sym table, the s07 creation maps present, any pre-existing s08 file, and the md5 of the card inputs. Writes nothing.
PREDICTION CONTRACT: prints only; RESULT PASS when every card input md5 matches.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c150_a3_5_probe.log -- py -u tools/bench/prep_c150_a3_5_probe.py"""
import glob, hashlib, json, os, sys                                                         # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                              # noqa: E731
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
card = J(os.path.join(B, "cards", "task_150-a3-5.json"))
bad = [(i["path"], md5(os.path.join(ROOT, i["path"])), i["md5"]) for i in card["inputs"] if md5(os.path.join(ROOT, i["path"])) != i["md5"]]
print("INPUTS bad", bad, flush=True)
P = J(os.path.join(B, "plan_ring_p4_s07v18.json"))
print("S07 plan md5", md5(os.path.join(B, "plan_ring_p4_s07v18.json")), "keys", sorted(P), flush=True)
f = P["finalized"]
print("S07 base", json.dumps(P.get("base"))[:600], flush=True)
print("S07 fin keys", sorted(f), flush=True)
print("S07 fin base", json.dumps(f.get("base"))[:600], flush=True)
print("S07 fin rebase", json.dumps(f.get("rebase"))[:1500], flush=True)
print("S07 step files first/last", f["step_files"][0], f["step_files"][-1], len(f["step_files"]), flush=True)
print("S07 open_rows", len(P.get("open_rows") or []), "end rows", len(f.get("end_cdiff_rows") or []), flush=True)
for p in (os.path.join(B, "sim", "ring_p4_s07v18", "step_30_create.json"), os.path.join(ROOT, f["step_files"][-1]["path"])):
    s = J(p)
    st = s["state"]
    print("STEP", os.path.relpath(p, ROOT), md5(p), "keys", sorted(s), "state keys", sorted(st), flush=True)
    print("  sym", json.dumps(st.get("sym"))[:1500], "neg", st.get("neg"), "vi", st.get("vi"), "md5", st.get("md5"), flush=True)
print("CMAPS s07", sorted(glob.glob(os.path.join(B, "creation_map", "*s07*"))), flush=True)
print("CMAPS s06", sorted(glob.glob(os.path.join(B, "creation_map", "*s06*"))), flush=True)
print("S08 existing", sorted(glob.glob(os.path.join(B, "*s08*")) + glob.glob(os.path.join(ROOT, "tools", "recipes", "*s08*")) + glob.glob(os.path.join(B, "sim", "*s08*"))), flush=True)
print("S07 files", sorted(os.path.basename(x) for x in glob.glob(os.path.join(B, "plan_ring_p4_s07v18*"))), flush=True)
print("S07 sim dir", sorted(os.listdir(os.path.join(B, "sim", "ring_p4_s07v18")))[:80], flush=True)
print("SIM s07*", sorted(glob.glob(os.path.join(B, "sim", "ring_p4_s07v18*"))), flush=True)
G = J(os.path.join(B, "graph_ring_p4s07_20261008_224835.json"))
print("GRAPH s07 keys", sorted(G), "vi", G.get("vi"), "md5", G.get("md5"), flush=True)
M = J(os.path.join(B, "memory_model.json"))
print("MM load_by_vi", json.dumps(M.get("load_by_vi"))[:1500], "op0", M.get("op0_read_mb"), flush=True)
print(protocol.result_line(protocol.make_result(0 if bad else 1, 1 if bad else 0, "inputs" if bad else None, [])), flush=True)
