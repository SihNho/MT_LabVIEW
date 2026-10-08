# ---
# labview: none
# hardware: none
# ---
r"""prep_c152_a2_2_check - card 152-a2-2 invariant step (OFFLINE). COPY of prep_c151_a3_2_check.py (itself the copy of prep_c150_a3_6_check.py 4455f2cc)
with ONLY the card 152-a2-2 pin set (brief_152-a2-2.md step 7): stagesim c24bd39a (new pin, was 748bbf30), + derived graph e26b4d90, + selftest_c152_fsowner.py
64918ff7; FILES += the derived graph, the selftest, every prep_c151_a3_2_* file, diag_c152_a1_1/a2_1 facts; CHG = the s09 files this card writes (printed,
not compared); SNAP name prep_c152_a2_2_md5_before.json. Everything else unchanged.
PREDICTION CONTRACT: B every file present; PIN pins hold; A after == before for every file; LV 0 LabVIEW processes.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c152_a2_2_check_<mode>.log -- py -u tools/bench/prep_c152_a2_2_check.py <mode>"""
import glob, hashlib, json, os, subprocess, sys                                            # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
VIS = {os.path.join(CD, "D1_ring_p4s08_20261009_031503.vi"): "f99e8414", os.path.join(CD, "D1_ring_p4s07_20261008_222709.vi"): "b3f86b32"}
FILES = ["tools/bench/plan_ring_p4_s08v18.json", "tools/bench/plan_ring_p4_s08v18_pred.json", "tools/bench/plan_ring_p4_s08v18_in.json",
         "tools/bench/plan_ring_p4_s08v18_licence.json", "tools/recipes/stage_d1_ring_p4_s08v18.py", "tools/recipes/stage_d1_ring_p4_s08v18_scratch.py",
         "tools/bench/sim/ring_p4_s08v18_base_real_fsmap.json", "tools/bench/plan_ring_p4_s07v18.json", "tools/bench/plan_ring_p4_s07v18_pred.json",
         "tools/bench/plan_ring_p4_s07v18_licence.json", "tools/recipes/stage_d1_ring_p4_s07v18.py", "tools/recipes/stage_d1_ring_p4_s07v18_scratch.py",
         "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py", "tools/stagesim.py", "tools/stagexec.py", "tools/stagekit.py", "tools/gscript.py",
         "tools/vigraph.py", "tools/elrule.py", "tools/errorlist_check.py", "tools/addrcheck.py", "tools/bench/memory_model.json",
         "tools/bench/graph_ring_p4s08_20261009_033522.json", "tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json",
         "tools/bench/graph_ring_p4s07_20261008_224835.json", "tools/bench/selftest_c152_fsowner.py",
         "tools/bench/errorlist_expected_D1_ring_p4s08_20261009_031503.json", "tools/bench/creation_map/plan_ring_p4_s08v18_c328fdaf_20261009_031742.jsonl",
         "tools/bench/creation_map/plan_ring_p4_s07v18_08c2ad4d_20261008_222936.jsonl", "tools/bench/diag_c150_a3_6_facts.md",
         "tools/bench/diag_c151_a1_1_facts.md", "tools/bench/diag_c152_a1_1_facts.md", "tools/bench/diag_c152_a2_1_facts.md"] + sorted(VIS)
FILES += sorted(os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "tools", "bench", "prep_c150_a3_6_*")))
FILES += sorted(os.path.relpath(p, ROOT).replace("\\", "/") for p in glob.glob(os.path.join(ROOT, "tools", "bench", "prep_c151_a3_2_*")))
for sub in ("tools/bench/sim/ring_p4_s08v18", "tools/bench/sim/ring_p4_s07v18", "tools/hooks"):
    for dp, _dn, fn in os.walk(os.path.join(ROOT, sub)):
        FILES += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn if "__pycache__" not in dp)
FILES.remove("tools/hooks/material_marker.log")          # appended by the guard hook on every --material command (diag_c150_a3_6_facts.md:44); listed in CHG
CHG = ["tools/bench/plan_ring_p4_s09v18.json", "tools/bench/plan_ring_p4_s09v18_in.json", "tools/bench/plan_ring_p4_s09v18_pred.json",
       "tools/bench/plan_ring_p4_s09v18_licence.json", "tools/recipes/stage_d1_ring_p4_s09v18.py", "tools/recipes/stage_d1_ring_p4_s09v18_scratch.py",
       "tools/bench/sim/ring_p4_s09v18_base_real_fsmap.json", "tools/bench/prep_c152_a2_2_session.json", "tools/bench/prerun_records.jsonl",
       "tools/bench/gate_fp_queue.jsonl", "tools/hooks/material_marker.log"]
for dp, _dn, fn in os.walk(os.path.join(ROOT, "tools/bench/sim/ring_p4_s09v18")):
    CHG += sorted(os.path.relpath(os.path.join(dp, n), ROOT).replace("\\", "/") for n in fn)
PINS = dict(VIS, **{"tools/bench/plan_ring_p4_s08v18.json": "c328fdaf", "tools/bench/plan_ring_p4_s08v18_pred.json": "cf2eccbf",
                    "tools/bench/plan_ring_p4_s08v18_licence.json": "6b978d9e", "tools/recipes/stage_d1_ring_p4_s08v18.py": "ca5a5478",
                    "tools/recipes/stage_d1_ring_p4_s08v18_scratch.py": "7cab5049", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa",
                    "tools/elrule.py": "a5ee7d5c", "tools/bench/memory_model.json": "a28b6dd7", "tools/stage_prerun.py": "c739eb86",
                    "tools/stagexec.py": "1bab9cf9", "tools/stagekit.py": "604529e8", "tools/gscript.py": "1a80236e", "tools/addrcheck.py": "207beb0d",
                    "tools/errorlist_check.py": "2b466a89", "tools/bench/graph_ring_p4s08_20261009_033522.json": "44858dbf",
                    "tools/bench/graph_ring_p4s08_20261009_033522_fsowner.json": "e26b4d90", "tools/bench/selftest_c152_fsowner.py": "64918ff7",
                    "tools/bench/graph_ring_p4s07_20261008_224835.json": "71935a84", "tools/stagesim.py": "c24bd39a", "tools/vigraph.py": "13be0847",
                    "tools/bench/sim/ring_p4_s08v18/step_19_wire.json": "ccfaa07c", "tools/bench/prep_c150_a3_6_mk.py": "f3e6d12c",
                    "tools/bench/prep_c150_a3_6_pred.py": "7996f5b1", "tools/bench/prep_c150_a3_6_licence.py": "efe26399",
                    "tools/bench/prep_c150_a3_6_check.py": "4455f2cc", "tools/bench/prep_c151_a3_2_mk.py": "04a5cab3",
                    "tools/bench/prep_c151_a3_2_probe.py": "6cc4085f", "tools/bench/prep_c151_a3_2_check.py": "ef418179",
                    "tools/bench/errorlist_expected_D1_ring_p4s08_20261009_031503.json": "c19cde96"})
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c152_a2_2_md5_before.json")
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
