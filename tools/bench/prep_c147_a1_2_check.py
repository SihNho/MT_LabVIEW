# ---
# labview: none
# hardware: none
# ---
r"""prep_c147_a1_2_check - card 147-a1-2 steps 0 + 4 (OFFLINE, no LabVIEW). md5 of every file the card says must stay byte-identical
(stagexec / stagekit / stagesim / stage_prerun, v18, the s05 files incl. the whole sim/ring_p4_s05v18 tree, memory_model.json, plus the rest of
146-a1-5's list) and the LabVIEW process list. 'before' writes tools/bench/prep_c147_a1_2_md5_before.json; 'after' compares against it.
COPIED from prep_c146_a1_5_check.py (03ee9cc1) with: snapshot name, the LV line is a FACT with PIDs (a LabVIEW of the parallel LabVIEW card
147-a1-1 may legitimately run; this card starts none) and an LV-NEW gate: no LabVIEW PID in 'after' that was absent 'before' AND whose start
time falls inside this card is attributed here - reported, not inferred.
Existing tools checked: prep_c146_a1_5_check.py (copied).
PREDICTION CONTRACT: B every file present; A after == before for every file; PIN s05 plan 1fc9b486, v18 2ea6cafa, memory_model 559be4cf,
  elrule a5ee7d5c, s04 file 95e408ff; LV facts printed.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c147_a1_2_check_<mode>.log -- py -u tools/bench/prep_c147_a1_2_check.py <mode>"""
import hashlib, json, os, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S5D = "tools/bench/sim/ring_p4_s05v18"
FILES = ["tools/bench/plan_ring_p4_s05v18.json", "tools/bench/plan_ring_p4_s05v18_pred.json", "tools/bench/plan_ring_p4_s05v18_in.json",
         "tools/bench/plan_ring_p4_s05v18_prov2.json", "tools/bench/plan_ring_p4_s05v18_in_prov2.json", "tools/bench/plan_ring_p4_s05v18_pred_prov2.json",
         "tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s04v18_pred.json", "tools/bench/plan_ring_p4_s04v18_in.json",
         "tools/recipes/stage_d1_ring_p4_s04v18.py", "tools/recipes/stage_d1_ring_p4_s04v18_scratch.py",
         "tools/recipes/stage_d1_ring_p4_s05v18.py", "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py",
         "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py", "tools/stagesim.py", "tools/stagexec.py", "tools/stagekit.py",
         "tools/vigraph.py", "tools/elrule.py", "tools/bench/subvi_requiredness.json", "tools/bench/memory_model.json", "tools/bench/census_samples.json",
         "tools/bench/plan_l2b1_licence.json", "tools/bench/sim/ring_p4_s04v18_base_real_fsmap.json", "tools/bench/sim/ring_p4_s05v18_base_real_fsmap.json",
         "tools/bench/sim/ring_p4_s04v18/step_23_wire.json", "tools/bench/sim/ring_p4_s03v18/step_20_create.json",
         "tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json",
         "tools/bench/creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl",
         "tools/bench/prep_c146_a1_5_mk.py",
         os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi")]
for dp, _dn, fn in os.walk(os.path.join(ROOT, S5D)):
    FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn)
PINS = {"tools/bench/plan_ring_p4_s05v18.json": "1fc9b486", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa", "tools/elrule.py": "a5ee7d5c",
        "tools/bench/memory_model.json": "559be4cf", "tools/bench/prep_c146_a1_5_mk.py": "94275a2c",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff"}
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c147_a1_2_md5_before.json")
md5 = lambda p: hashlib.md5(open(p if os.path.isabs(p) else os.path.join(ROOT, p), "rb").read()).hexdigest()   # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:1500]), flush=True)


mode = sys.argv[1] if len(sys.argv) > 1 else "after"
have = [f for f in FILES if os.path.isfile(f if os.path.isabs(f) else os.path.join(ROOT, f))]
gate("B every file present ({0}/{1})".format(len(have), len(FILES)), len(have) == len(FILES), sorted(set(FILES) - set(have)))
cur = dict((f, md5(f)) for f in have)
for f in FILES:
    print("MD5 {0} {1}".format(cur.get(f), f), flush=True)
gate("PIN card/brief pins hold", all(cur.get(f, "").startswith(w) for f, w in PINS.items()), dict((f, cur.get(f)) for f in PINS))
tl = subprocess.run(["tasklist", "/v", "/fo", "csv"], capture_output=True, text=True, errors="replace").stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
print("FACT LV processes ({0}): {1}".format(len(lv), lv), flush=True)
if mode == "before":
    json.dump({"md5": cur, "lv": lv}, open(SNAP, "w", encoding="utf-8"), indent=1)
else:
    old = json.load(open(SNAP, encoding="utf-8"))
    gate("A after == before for {0} files".format(len(old["md5"])), old["md5"] == cur,
         dict((f, (old["md5"].get(f), cur.get(f))) for f in set(old["md5"]) | set(cur) if old["md5"].get(f) != cur.get(f)))
    print("FACT LV before {0} / after {1}".format(old["lv"], lv), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
