# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_5_check - card 146-a1-5 steps 0 + 6 (OFFLINE, no LabVIEW). md5 of every file the card says must stay byte-identical
(s05 plan/_in/_pred, every file under sim/ring_p4_s05v18/ incl. _passA/_prov/_prov2/s04end, s05 + s04 recipes, s04 plan/_in/_pred, v18,
memory_model.json PINNED 559be4cf, stage tools, elrule, requiredness, licence, census samples, creation maps, s04/s05 real bases, s04 adopted
file) and the LabVIEW process list. 'before' writes tools/bench/prep_c146_a1_5_md5_before.json; 'after' compares against it.
COPIED from prep_c146_a1_3_check.py (adeb0ea6) with: the file list (s05 files + the whole sim/ring_p4_s05v18 tree added, *_prov2 list kept
as part of that tree), pins (s05 plan 1fc9b486 / pred 961f30c4), snapshot name.
Existing tools checked: prep_c146_a1_3_check.py (copied).
PREDICTION CONTRACT: B every file present; A after == before for every file; PIN s05 plan 1fc9b486, s05 pred 961f30c4, v18 2ea6cafa, elrule
  a5ee7d5c, memory_model 559be4cf, s04 file 95e408ff; LV no LabVIEW.exe (a LabVIEW of the parallel card 146-a1-4 would show here and is reported).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c146_a1_5_check_<mode>.log -- py -u tools/bench/prep_c146_a1_5_check.py <mode>"""
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
         "tools/bench/graph_ring_p4s04_20261007_223245.json",
         "tools/bench/creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl",
         os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi")]
for dp, _dn, fn in os.walk(os.path.join(ROOT, S5D)):
    FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn)
PINS = {"tools/bench/plan_ring_p4_s05v18.json": "1fc9b486", "tools/bench/plan_ring_p4_s05v18_pred.json": "961f30c4",
        "tools/bench/plan_ring_p4_v18.json": "2ea6cafa", "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "559be4cf",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff"}
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c146_a1_5_md5_before.json")
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
if mode == "before":
    json.dump(cur, open(SNAP, "w", encoding="utf-8"), indent=1)
else:
    old = json.load(open(SNAP, encoding="utf-8"))
    gate("A after == before for {0} files".format(len(old)), old == cur, dict((f, (old.get(f), cur.get(f))) for f in set(old) | set(cur) if old.get(f) != cur.get(f)))
tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
gate("LV no LabVIEW process", not lv, lv)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
