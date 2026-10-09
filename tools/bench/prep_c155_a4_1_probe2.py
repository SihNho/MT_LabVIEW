# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_155-a4-1.md
# ---
"""prep_c155_a4_1_probe2 - card 155-a4-1, OFFLINE (json only): prior-art rows for the P5-2 links. Prints (1) every move_in /
delete_object / delete_wire / base-cond stop / local_read / case_wired-with-symbolic-src / numeric-constant-with-value action in
the stored plans tools/bench/plan_*.json (non-pred, non-prov), (2) $work donor candidates for Equal? / Greater Or Equal To 0? /
And / Increment from main_vi_node_labels.json that are present in the P5-1 graph 6716c499, (3) the LEFT shift registers #24133 /
#24187 rows. Read-only. PREDICTION CONTRACT: prints the lists; RESULT line."""
import glob, json, os, sys                                                                     # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stage_prerun as SPR  # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
G = json.load(open(os.path.join(B, "graph_ring_p5s01_20261009_125622.json"), encoding="utf-8"))
T = G["terminals"]
OBJ = dict((int(o["uid"]), o) for o in G["objs"])
seen = {}
for p in sorted(glob.glob(os.path.join(B, "plan_*.json"))):
    n = os.path.basename(p)
    if any(x in n for x in ("_pred", "_prov", "_licence", "poskey_conv", "_draft")):
        continue
    try:
        d = json.load(open(p, encoding="utf-8"))
    except Exception:                                                                          # noqa: BLE001
        continue
    for i, a in enumerate((d or {}).get("actions") or [], 1) if isinstance(d, dict) else []:
        op = a.get("op")
        k = None
        if op == "move_in":
            k = "move_in dest={0} nodes={1}".format(a.get("dest_diagram"), a.get("nodes"))
        elif op in ("delete_object", "delete_wire"):
            k = "{0} {1}".format(op, {x: a.get(x) for x in ("uid", "wire_uid", "at") if a.get(x) is not None})
        elif op == "wire" and isinstance(a.get("dst"), dict) and a["dst"].get("term") == "cond":
            k = "wire->cond dst={0} src={1}".format(a["dst"], a.get("src"))
        elif op == "create" and a.get("class") == "Local" and a.get("mode") == "read":
            k = "local_read diagram={0}".format(a.get("diagram"))
        elif op == "create" and a.get("class") == "CaseStructure" and isinstance(a.get("src"), str):
            k = "case_wired symbolic src={0} diagram={1}".format(a.get("src"), a.get("diagram"))
        elif op == "create" and a.get("value") is not None:
            k = "create value={0} class={1} prim={2} route-on={3}".format(a.get("value"), a.get("class"), a.get("prim"), a.get("on"))
        elif op == "create" and a.get("prim") and (a.get("donor") or {}).get("donor") == "$work":
            k = "work-prim {0} #{1}".format(a.get("prim"), a["donor"].get("uid"))
        if k:
            seen.setdefault(k, []).append("{0}:{1}".format(n, i))
for k in sorted(seen):
    print("PLAN {0} | {1} | {2}".format(k, len(seen[k]), seen[k][:4]))
LAB = SPR.prim_donor_labels()
want = ("Equal?", "Greater Or Equal To 0?", "Greater Or Equal?", "And", "Increment", "Not Equal?", "Greater Than 0?")
for w in want:
    c = sorted(u for u, l in LAB.items() if l == w)
    inb = [u for u in c if u in OBJ]
    print("DONOR {0!r}: main_vi uids {1}; in P5-1 graph {2}".format(w, c[:20], [(u, OBJ[u]["class"]) for u in inb[:10]]))
for u in (24133, 24187, 23041):
    print("ROWS #{0}: {1}".format(u, [(r["term_uid"], r["term_name"], r["term_class"], r["frame_diagram"], r["wire_uid"]) for r in T if int(r["owner_uid"]) == u]))
for wu in (23519, 9610):
    print("WIRE w{0}: {1}".format(wu, [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"]) for r in T if int(r["wire_uid"] or 0) == wu]))
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
