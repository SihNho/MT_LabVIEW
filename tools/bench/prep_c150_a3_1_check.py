# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_1_check - card 150-a3-1 (copy of prep_c150_a2_5_check.py 9a99d7a8: snapshot name, + stagesim 748bbf30 / vigraph 13be0847 /
s07 inputs pins) invariant step (OFFLINE, no LabVIEW). md5 of every file the card says must stay
byte-identical (stagekit 06b8d844 / stagexec 1bab9cf9 / gscript 1a80236e / elrule a5ee7d5c / stage_prerun c739eb86 / stagesim / vigraph, v18, the
s06 plan / pred / in / licence + recipes + the whole sim/ring_p4_s06v18 tree + its real-fsmap base, the s06 graph a3ecb92b, memory_model.json
8eec443c, adopted_scratch.jsonl 658fe5b9, the claudeDev s06 569ffbf5 / s05 3f9ac26b / s04 95e408ff / bed 39511877, s06 EL expected file, s06
creation maps) and the LabVIEW process list. 'before' writes tools/bench/prep_c150_a2_5_md5_before.json; 'after' compares against it.
COPIED from prep_c150_a2_3_check.py (d09e2aff) with: stage_prerun pin c739eb86 (150-a2-4); snapshot name. Nothing else.
PREDICTION CONTRACT: B every file present; PIN pins hold; A after == before for every file; LV 0 LabVIEW processes.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c150_a3_1_check_<mode>.log -- py -u tools/bench/prep_c150_a3_1_check.py <mode>"""
import hashlib, json, os, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
S6D = "tools/bench/sim/ring_p4_s06v18"
VIS = {os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5", os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b",
       os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff", os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877"}
FILES = ["tools/bench/plan_ring_p4_s06v18.json", "tools/bench/plan_ring_p4_s06v18_pred.json", "tools/bench/plan_ring_p4_s06v18_in.json",
         "tools/bench/plan_ring_p4_s06v18_licence.json", "tools/recipes/stage_d1_ring_p4_s06v18.py", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py",
         "tools/bench/sim/ring_p4_s06v18_base_real_fsmap.json", "tools/bench/plan_ring_p4_s05v18.json", "tools/bench/plan_ring_p4_s04v18.json",
         "tools/bench/plan_ring_p4_s03v18.json", "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py", "tools/stagesim.py", "tools/stagexec.py",
         "tools/stagekit.py", "tools/gscript.py", "tools/vigraph.py", "tools/elrule.py", "tools/errorlist_check.py", "tools/bench/subvi_requiredness.json",
         "tools/bench/memory_model.json", "tools/bench/census_samples.json", "tools/bench/adopted_scratch.jsonl",
         "tools/bench/graph_ring_p4s06_20261008_192149.json", "tools/bench/errorlist_expected_D1_ring_p4s06_20261008_174730.json",
         "tools/bench/sim/ring_p4_s05v18/step_21_create.json", "tools/bench/sim/ring_p4_s04v18/step_23_wire.json",
         "tools/bench/sim/ring_p4_s03v18/step_20_create.json", "tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json",
         "tools/bench/creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl",
         "tools/bench/prep_c148_a3_3_mk.py", "tools/bench/prep_c148_a3_3_pred.py", "tools/bench/prep_c147_a1_3_pred.py"] + sorted(VIS)
for dp, _dn, fn in os.walk(os.path.join(ROOT, S6D)):
    FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn)
CHG = ["tools/bench/plan_ring_p4_s07v18.json", "tools/bench/plan_ring_p4_s07v18_in.json", "tools/bench/plan_ring_p4_s07v18_pred.json",
       "tools/bench/plan_ring_p4_s07v18_licence.json", "tools/recipes/stage_d1_ring_p4_s07v18.py", "tools/recipes/stage_d1_ring_p4_s07v18_scratch.py",
       "tools/bench/sim/ring_p4_s07v18_base_real_fsmap.json"]
PINS = dict(VIS, **{"tools/bench/plan_ring_p4_s06v18.json": "cfbd9823", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa",
                    "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "8eec443c", "tools/stage_prerun.py": "c739eb86",
                    "tools/stagexec.py": "1bab9cf9", "tools/stagekit.py": "06b8d844", "tools/gscript.py": "1a80236e",
                    "tools/bench/adopted_scratch.jsonl": "658fe5b9", "tools/bench/graph_ring_p4s06_20261008_192149.json": "a3ecb92b",
                    "tools/bench/prep_c148_a3_3_mk.py": "5f00cd4f", "tools/bench/prep_c148_a3_3_pred.py": "8b2ec4f1",
                    "tools/stagesim.py": "748bbf30", "tools/vigraph.py": "13be0847",
                    "tools/bench/prep_c150_a1_1_session.json": "a164722f", "tools/bench/sim/ring_p4_s07v18_base_real_fsmap.json": "765c687c",
                    "tools/bench/prep_c150_a2_5_rebase.log": "28341ad1", "tools/bench/plan_ring_p4_s06v18_licence.json": "7f70bbf9",
                    "tools/recipes/stage_d1_ring_p4_s06v18.py": "d947df5d", "tools/recipes/stage_d1_ring_p4_s06v18_scratch.py": "31009bfc"})
FILES += ["tools/bench/prep_c150_a1_1_session.json", "tools/bench/prep_c150_a2_5_rebase.log", "tools/bench/sim/ring_p4_s07v18_base_real_fsmap.json"]
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c150_a3_1_md5_before.json")
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
for f in CHG:
    print("CHG {0} {1}".format(md5(f) if os.path.isfile(os.path.join(ROOT, f)) else "-", f), flush=True)
gate("PIN card/brief pins hold", all(cur.get(f, "").startswith(w) for f, w in PINS.items()),
     dict((f, cur.get(f)) for f in PINS if not cur.get(f, "").startswith(PINS[f])))
tl = subprocess.run(["tasklist", "/v", "/fo", "csv"], capture_output=True, text=True, errors="replace").stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
gate("LV no LabVIEW process (this card launches none)", not lv, lv)
if mode == "before":
    json.dump({"md5": cur, "lv": lv}, open(SNAP, "w", encoding="utf-8"), indent=1)
else:
    old = json.load(open(SNAP, encoding="utf-8"))
    gate("A after == before for {0} files".format(len(old["md5"])), old["md5"] == cur,
         dict((f, (old["md5"].get(f), cur.get(f))) for f in set(old["md5"]) | set(cur) if old["md5"].get(f) != cur.get(f)))
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
