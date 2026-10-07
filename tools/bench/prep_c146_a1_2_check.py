# ---
# labview: none
# hardware: none
# ---
r"""prep_c146_a1_2_check - card 146-a1-2 steps 1 + 8 (OFFLINE, no LabVIEW). md5 of every file the card says must stay byte-identical (s04
plan/pred/_in/recipes, s05 recipes, v18, stage tools, licence, s04 adopted file, s03 file, bed, s04 real base, s04 graph, elrule) and the
LabVIEW process list; memory_model.json is compared against git HEAD as PARSED json: exactly one added load_by_vi key 95e408ff.. = 605.4,
every other key/parameter equal. 'before' writes tools/bench/prep_c146_a1_2_md5_before.json; 'after' compares against it.
COPIED from prep_c145_a2_6_check.py (names, + the memory_model diff gate MM, + the hygiene copy gate HY in 'after'; memory_model.json moved
from the byte list to MM because this card edits it).
PREDICTION CONTRACT: B every file present; A after == before for every file; PIN s04 plan f349c39a, v18 2ea6cafa, s04 file 95e408ff, bed
  39511877, s03 282301ca, elrule a5ee7d5c; MM one added key; HY op_hygiene copy md5 == original (after only); LV no LabVIEW.exe process.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/prep_c146_a1_2_check_<mode>.log -- py -u tools/bench/prep_c146_a1_2_check.py <mode>"""
import hashlib, json, os, subprocess, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
from tools import protocol  # noqa: E402
CD = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
FILES = ["tools/bench/plan_ring_p4_s04v18.json", "tools/bench/plan_ring_p4_s04v18_pred.json", "tools/bench/plan_ring_p4_s04v18_in.json",
         "tools/recipes/stage_d1_ring_p4_s04v18.py", "tools/recipes/stage_d1_ring_p4_s04v18_scratch.py",
         "tools/recipes/stage_d1_ring_p4_s05v18.py", "tools/recipes/stage_d1_ring_p4_s05v18_scratch.py",
         "tools/bench/plan_ring_p4_v18.json", "tools/stage_prerun.py", "tools/stagesim.py", "tools/stagexec.py", "tools/stagekit.py",
         "tools/vigraph.py", "tools/elrule.py", "tools/bench/subvi_requiredness.json",
         "tools/bench/plan_l2b1_licence.json", "tools/bench/sim/ring_p4_s04v18_base_real_fsmap.json",
         "tools/bench/sim/ring_p4_s04v18/step_23_wire.json", "tools/bench/graph_ring_p4s04_20261007_223245.json",
         "tools/bench/errorlist_expected_D1_ring_p4s04_20261007_215031.json", "tools/bench/build_opwiringrules_v0_hygiene.json",
         os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"), os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"),
         os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi")]
PINS = {"tools/bench/plan_ring_p4_s04v18.json": "f349c39a", "tools/bench/plan_ring_p4_v18.json": "2ea6cafa", "tools/elrule.py": "a5ee7d5c",
        "tools/stage_prerun.py": "61d6f590", "tools/bench/graph_ring_p4s04_20261007_223245.json": "094ba298",
        "tools/bench/build_opwiringrules_v0_hygiene.json": "57e3bf4d",
        os.path.join(CD, "D1_ring_p4s04_20261007_215031.vi"): "95e408ff", os.path.join(CD, "D1_ring_p4s03_20261007_202957.vi"): "282301ca",
        os.path.join(CD, "D1_ring_p3b2b_20261002_130007.vi"): "39511877"}
SNAP = os.path.join(ROOT, "tools", "bench", "prep_c146_a1_2_md5_before.json")
MM = "tools/bench/memory_model.json"
KEY = "95e408ff14a406edd3f16b32ba7324f1"
HY = ("tools/bench/build_opwiringrules_v0_hygiene.json", "tools/bench/op_hygiene/build_opwiringrules_v0_hygiene.json")
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
head = json.loads(subprocess.run(["git", "show", "HEAD:" + MM], cwd=ROOT, capture_output=True, text=True, encoding="utf-8").stdout)
now = json.load(open(os.path.join(ROOT, MM), encoding="utf-8"))
added = sorted(set(now.get("load_by_vi") or {}) - set(head.get("load_by_vi") or {}))
rest_now = dict(now, load_by_vi=dict((k, x) for k, x in now["load_by_vi"].items() if k != KEY))
print("MD5 {0} {1} (HEAD parsed keys {2})".format(md5(MM), MM, sorted(head)), flush=True)
gate("MM memory_model.json vs git HEAD: added load_by_vi keys {0} == [{1}] value {2}; every other key equal (fail_above {3}, memstop {4})".format(
     added, KEY[:8], (now["load_by_vi"].get(KEY) or {}).get("value"), now["fail_above_mb"]["value"], now["memstop_mb"]["value"]),
     added == [KEY] and now["load_by_vi"][KEY]["value"] == 605.4 and rest_now == head
     and now["fail_above_mb"]["value"] == 680.0 and now["memstop_mb"]["value"] == 695.0,
     [k for k in set(head) | set(now) if head.get(k) != rest_now.get(k)])
if mode == "before":
    json.dump(cur, open(SNAP, "w", encoding="utf-8"), indent=1)
else:
    old = json.load(open(SNAP, encoding="utf-8"))
    gate("A after == before for {0} files".format(len(old)), old == cur, dict((f, (old.get(f), cur.get(f))) for f in set(old) | set(cur) if old.get(f) != cur.get(f)))
    hy = [md5(x) if os.path.isfile(os.path.join(ROOT, x)) else None for x in HY]
    lst = sorted(os.listdir(os.path.join(ROOT, "tools", "bench", "op_hygiene"))) if os.path.isdir(os.path.join(ROOT, "tools", "bench", "op_hygiene")) else None
    gate("HY op_hygiene copy md5 == original {0}; directory lists {1}".format(hy, lst), hy[0] is not None and hy[0] == hy[1], hy)
tl = subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout
lv = [ln for ln in tl.splitlines() if "labview" in ln.lower()]
gate("LV no LabVIEW process", not lv, lv)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], [])), flush=True)
sys.exit(1 if G["fail"] else 0)
