# ---
# labview: none
# hardware: none
# ---
r"""prep_c150_a3_5_check - card 150-a3-5 step 8 invariant step (OFFLINE, no LabVIEW). COPY of prep_c150_a3_1_check.py (1b935cd2) with the
card 150-a3-5 pin set: stagekit 06b8d844, stagexec 1bab9cf9, gscript 1a80236e, elrule a5ee7d5c, stage_prerun c739eb86, vigraph 13be0847,
stagesim 748bbf30, VIs s07 b3f86b32 / s06 569ffbf5 / s05 3f9ac26b / bed 39511877, memory_model b4a6eec6, adopted_scratch 450c894c, graphs s07
71935a84 / s06 a3ecb92b, dispo.py 4b456b18; PLUS every s07 plan/pred/in/licence/recipe file, the whole sim/ring_p4_s07v18 tree + its real-fsmap
base, and every tools/hooks/** file (md5 before == after). CHG = the s08 files this card writes (printed, not compared). LabVIEW process list.
'before' writes tools/bench/prep_c150_a3_5_md5_before.json; 'after' compares against it.
PREDICTION CONTRACT: B every file present; PIN pins hold; A after == before for every file; LV 0 LabVIEW processes.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c150_a3_5_check_<mode>.log -- py -u tools/bench/prep_c150_a3_5_check.py <mode>"""
import hashlib, json, os, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VIS = {os.path.join(CD, "D1_ring_p4s07_20261008_222709.vi"): "b3f86b32", os.path.join(CD, "D1_ring_p4s06_20261008_174730.vi"): "569ffbf5",
       os.path.join(CD, "D1_ring_p4s05_20261008_002621.vi"): "3f9ac26b", os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877"}
FILES = ["tools/bench/plan_ring_p4_s07v18.json", "tools/bench/plan_ring_p4_s07v18_pred.json", "tools/bench/plan_ring_p4_s07v18_in.json",
         "tools/bench/plan_ring_p4_s07v18_licence.json", "tools/recipes/stage_d1_ring_p4_s07v18.py", "tools/recipes/stage_d1_ring_p4_s07v18_scratch.py",
         "tools/bench/sim/ring_p4_s07v18_base_real_fsmap.json", "tools/bench/plan_ring_p4_s06v18.json", "tools/bench/plan_ring_p4_s05v18.json",
         "tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s03v18.json", "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py",
         "tools/stagesim.py", "tools/stagexec.py", "tools/stagekit.py", "tools/gscript.py", "tools/vigraph.py", "tools/elrule.py", "tools/dispo.py",
         "tools/errorlist_check.py", "tools/bench/subvi_requiredness.json", "tools/bench/memory_model.json", "tools/bench/census_samples.json",
         "tools/bench/adopted_scratch.jsonl", "tools/bench/graph_ring_p4s07_20261008_224835.json", "tools/bench/graph_ring_p4s06_20261008_192149.json",
         "tools/bench/errorlist_expected_D1_ring_p4s07_20261008_222709.json", "tools/bench/sim/ring_p4_s06v18/step_25_wire.json",
         "tools/bench/sim/ring_p4_s05v18/step_21_create.json", "tools/bench/sim/ring_p4_s04v18/step_23_wire.json",
         "tools/bench/sim/ring_p4_s03v18/step_20_create.json", "tools/bench/sim/ring_p4_v18/ring_p4_v3/summary.json",
         "tools/bench/creation_map/plan_ring_p4_s03v18_da66a030_20261007_203225.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s04v18_f349c39a_20261007_215246.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s05v18_1fc9b486_20261008_002835.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s06v18_cfbd9823_20261008_175325.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s07v18_08c2ad4d_20261008_222936.jsonl",
         "tools/bench/prep_c150_a1_1_mk.py", "tools/bench/prep_c150_a3_1_pred.py", "tools/bench/prep_c150_a3_1_check.py",
         "tools/bench/prep_c150_a3_1_licence.py", "tools/bench/prep_c150_a1_1_session.json", "tools/bench/prep_c150_a2_5_rebase.log"] + sorted(VIS)
for sub in ("tools/bench/sim/ring_p4_s07v18", "tools/hooks"):
    for dp, _dn, fn in os.walk(os.path.join(ROOT, sub)):
        FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn if "__pycache__" not in dp)
CHG = ["tools/bench/plan_ring_p4_s08v18.json", "tools/bench/plan_ring_p4_s08v18_in.json", "tools/bench/plan_ring_p4_s08v18_pred.json",
       "tools/bench/plan_ring_p4_s08v18_licence.json", "tools/recipes/stage_d1_ring_p4_s08v18.py", "tools/recipes/stage_d1_ring_p4_s08v18_scratch.py",
       "tools/bench/sim/ring_p4_s08v18_base_real_fsmap.json", "tools/bench/prep_c150_a3_5_session.json", "tools/bench/prerun_records.jsonl"]
PINS = dict(VIS, **{"tools/bench/plan_ring_p4_s07v18.json": "08c2ad4d", "tools/bench/plan_ring_p4_s07v18_pred.json": "6f46fc3c",
                    "tools/bench/plan_ring_p4_s07v18_licence.json": "aedbe1f1", "tools/recipes/stage_d1_ring_p4_s07v18.py": "e0f1152f",
                    "tools/recipes/stage_d1_ring_p4_s07v18_scratch.py": "80dbdb41", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa",
                    "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "b4a6eec6", "tools/stage_prerun.py": "c739eb86",
                    "tools/stagexec.py": "1bab9cf9", "tools/stagekit.py": "06b8d844", "tools/gscript.py": "1a80236e", "tools/dispo.py": "4b456b18",
                    "tools/bench/adopted_scratch.jsonl": "450c894c", "tools/bench/graph_ring_p4s07_20261008_224835.json": "71935a84",
                    "tools/bench/graph_ring_p4s06_20261008_192149.json": "a3ecb92b", "tools/stagesim.py": "748bbf30", "tools/vigraph.py": "13be0847",
                    "tools/bench/sim/ring_p4_s07v18/step_30_create.json": "c2b902b7", "tools/bench/prep_c150_a1_1_mk.py": "7a275061",
                    "tools/bench/prep_c150_a3_1_pred.py": "2644bdd4", "tools/bench/prep_c150_a3_1_check.py": "1b935cd2",
                    "tools/bench/prep_c150_a3_1_licence.py": "da47cb38"})
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c150_a3_5_md5_before.json")
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
