# ---
# labview: none
# hardware: none
# ---
r"""prep_c147_a1_3_check - card 147-a1-3 steps 0 + 7 (OFFLINE, no LabVIEW). md5 of every file the card says must stay byte-identical
(stagexec / stagekit / stagesim / stage_prerun / elrule / vigraph, v18, the s05 plan / pred / in + recipes + the whole sim/ring_p4_s05v18 tree,
the adopted s05 .vi 3f9ac26b, s04 95e408ff, s03 282301ca, bed 39511877, memory_model.json 88eeb037, the real s05 graph cbeeadf5, the s05 EL
expected file, the s147-a1-2 maker d57fdd4f) and the LabVIEW process list. 'before' writes tools/bench/prep_c147_a1_3_md5_before.json;
'after' compares against it.
COPIED from prep_c147_a1_2_check.py (f8eda8d2) with: the file list / pins of this card, snapshot name; LV is a gate here (the card runs ALONE:
no LabVIEW process before or after).
PREDICTION CONTRACT: B every file present; PIN pins hold; LV no LabVIEW process; A after == before for every file.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c147_a1_3_check_<mode>.log -- py -u tools/bench/prep_c147_a1_3_check.py <mode>"""
import hashlib, json, os, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S5D = "tools/bench/sim/ring_p4_s05v18"
VIS = {os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b", os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff",
       os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca", os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877"}
FILES = ["tools/bench/plan_ring_p4_s05v18.json", "tools/bench/plan_ring_p4_s05v18_pred.json", "tools/bench/plan_ring_p4_s05v18_in.json",
         "tools/recipes/stage_d1_ring_p4_s05v18.py", "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py",
         "tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s03v18.json",
         "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py", "tools/stagesim.py", "tools/stagexec.py", "tools/stagekit.py",
         "tools/vigraph.py", "tools/elrule.py", "tools/errorlist_check.py", "tools/bench/subvi_requiredness.json", "tools/bench/memory_model.json",
         "tools/bench/census_samples.json", "tools/bench/plan_l2b1_licence.json", "tools/bench/sim/ring_p4_s05v18_base_real_fsmap.json",
         "tools/bench/graph_ring_p4s05_20261008_013759.json", "tools/bench/errorlist_expected_D1_ring_p4s05_20261008_002621.json",
         "tools/bench/errorlist_D1_ring_p4s05_20261008_002621_20261008_012323.json", "tools/bench/diag_c147_a1_1_t2626.log",
         "tools/bench/sim/ring_p4_s04v18/step_23_wire.json", "tools/bench/sim/ring_p4_s03v18/step_20_create.json",
         "tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json",
         "tools/bench/creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl",
         "tools/bench/prep_c147_a1_2_mk.py", "tools/bench/prep_c146_a1_2_pred.py"] + sorted(VIS)
for dp, _dn, fn in os.walk(os.path.join(ROOT, S5D)):
    FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn)
PINS = dict(VIS, **{"tools/bench/plan_ring_p4_s05v18.json": "1fc9b486", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa", "tools/elrule.py": "a5ee7d5c",
                    "tools/bench/memory_model.json": "88eeb037", "tools/bench/prep_c147_a1_2_mk.py": "d57fdd4f", "tools/stage_prerun.py": "61d6f590",
                    "tools/stagexec.py": "1bab9cf9", "tools/stagekit.py": "9a3fceaf", "tools/stagesim.py": "748bbf30",
                    "tools/bench/graph_ring_p4s05_20261008_013759.json": "cbeeadf5", "tools/bench/diag_c147_a1_1_t2626.log": "be50e238",
                    "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py": "cd14eb47", "tools/bench/prep_c146_a1_2_pred.py": "19270d62"})
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c147_a1_3_md5_before.json")
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
gate("PIN card/brief pins hold", all(cur.get(f, "").startswith(w) for f, w in PINS.items()),
     dict((f, cur.get(f)) for f in PINS if not cur.get(f, "").startswith(PINS[f])))
tl = subprocess.run(["tasklist", "/v", "/fo", "csv"], capture_output=True, text=True, errors="replace").stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
gate("LV no LabVIEW process ({0})".format(len(lv)), not lv, lv)
if mode == "before":
    json.dump({"md5": cur, "lv": lv}, open(SNAP, "w", encoding="utf-8"), indent=1)
else:
    old = json.load(open(SNAP, encoding="utf-8"))
    gate("A after == before for {0} files".format(len(old["md5"])), old["md5"] == cur,
         dict((f, (old["md5"].get(f), cur.get(f))) for f in set(old["md5"]) | set(cur) if old["md5"].get(f) != cur.get(f)))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
