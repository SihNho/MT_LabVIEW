# ---
# labview: none
# hardware: none
# ---
"""Card 153-a1-1 census (F1, F3, F5, F6, part of F2): reads the s09 graph 22f967b5 and the S1 wiki 3e3d23ce; no LabVIEW.
Found before writing: c73_l7r_facts.py (S1-side #376 rows, log :92-150), diag_c153_a1_1_probe.log (owners = diagram -> [class,
struct], loops 23041 / 10170 / 637). Prediction: #376 sits on 23405 (loop 1.7); its t5/t7 are unwired; 22 termless wires;
#23041 has 2 SR pairs. Output: tools/bench/diag_c153_a1_1_census.json + log lines."""
import json, os, collections
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.chdir(ROOT)
G = json.load(open("tools/bench/graph_ring_p4s09_20261009_062044.json", encoding="utf-8"))
W = json.load(open("docs/wiki/subvi/D1_s1_copy.json", encoding="utf-8"))
OWN, OBJ = G["owners"], {o["uid"]: o for o in G["objs"]}
TAG = {639: "1.1 #637", 23166: "1.2 #10170", 23405: "1.7 #23041", 536: "top"}

def rows_index(terms):
    by_owner, by_wire = collections.defaultdict(list), collections.defaultdict(list)
    for t in terms:
        by_owner[t["owner_uid"]].append(t)
        if t["wire_uid"]:
            by_wire[t["wire_uid"]].append(t)
    return by_owner, by_wire
BO, BW = rows_index(G["terminals"])
SO, SW = rows_index(W["terminals"])

def chain(d):
    """diagram uid -> list of diagram uids up to the top, using owners (diagram -> [cls, struct]; struct -> ['Diagram', d])."""
    out, seen = [], set()
    while d and d not in seen:
        seen.add(d); out.append(d)
        o = OWN.get(str(d))
        if not o:
            break
        s = o[1]
        p = OWN.get(str(s))
        d = p[1] if p else 0
    return out

def where(d):
    c = chain(d)
    for x in c:
        if x in TAG:
            return TAG[x] + (" (nested %s)" % c[:c.index(x)] if c.index(x) else "")
    return "other %s" % c

def node_loc(uid, BOx=None):
    rs = (BOx or BO).get(uid, [])
    ds = sorted({r["frame_diagram"] for r in rs})
    return ds

def other_ends(w, BWx, me):
    return [(r["owner_uid"], r["owner_class"], r["term_name"], r["is_source"], r["term_uid"]) for r in BWx.get(w, []) if r["term_uid"] != me]

out = {"F1": [], "F3": {}, "F5": {}, "F6": {}, "F2": {}}
print("== F1 #376 S1 vs s09")
s09_376 = {r["term_name"]: r for r in BO[376]}
for r in sorted(SO[376], key=lambda r: r["term_uid"]):
    src = [e for e in other_ends(r["wire_uid"], SW, r["term_uid"]) if e[3]] if not r["is_source"] else []
    s = s09_376.get(r["term_name"])
    rec = {"term": r["term_name"], "dir": "OUT" if r["is_source"] else "IN", "s1_wire": r["wire_uid"], "s1_src": src,
           "s09_term_uid": s and s["term_uid"], "s09_wire": s and s["wire_uid"], "s09_diag": s and s["frame_diagram"],
           "s09_where": s and where(s["frame_diagram"]),
           "s09_other_ends": s and other_ends(s["wire_uid"], BW, s["term_uid"]) if s and s["wire_uid"] else []}
    rec["s1_src_in_s09"] = [{"uid": e[0], "diags": node_loc(e[0]), "where": [where(d) for d in node_loc(e[0])],
                             "exists": e[0] in OBJ} for e in src]
    out["F1"].append(rec)
    print(" ", json.dumps(rec)[:900])
print("== F3 loop 1.7 #23041 body 23405")
inside = [t for t in G["terminals"] if 23405 in chain(t["frame_diagram"])]
nodes = collections.defaultdict(list)
for t in inside:
    nodes[(t["owner_uid"], t["owner_class"])].append((t["term_name"], t["is_source"], t["wire_uid"], t["term_uid"], t["frame_diagram"]))
for (u, c), ts in sorted(nodes.items()):
    ends = {x[2]: other_ends(x[2], BW, x[3]) for x in ts if x[2]}
    out["F3"][str(u)] = {"class": c, "terms": ts, "ends": {str(k): v for k, v in ends.items()}}
    print("  #%s %s %s ends %s" % (u, c, ts, ends))
loop_rows = [t for t in G["terminals"] if t["owner_uid"] in (23041,) ]
print("  rows owned by loop 23041:", loop_rows)
print("  loops entry:", [L for L in G["loops"] if L["loop_uid"] == 23041])
for lp in (23041, 10170, 637):
    print("  structure objs owned:", lp, OWN.get(str(lp)))
print("== F5 loop 1.2 #10170 body 23166: SubVIs and Selects")
for t in G["terminals"]:
    if t["frame_diagram"] == 23166 and t["owner_class"] in ("SubVI",) or (t["frame_diagram"] == 23166 and t["term_name"] in ("s", "s? t:f")):
        pass
sel = collections.defaultdict(list)
for t in G["terminals"]:
    if 23166 in chain(t["frame_diagram"]) and (t["owner_class"] in ("SubVI", "Select", "Local") or "t:f" in t["term_name"]):
        sel[(t["owner_uid"], t["owner_class"], t["frame_diagram"])].append((t["term_name"], t["is_source"], t["wire_uid"], t["term_uid"]))
for (u, c, d), ts in sorted(sel.items()):
    ends = {x[2]: other_ends(x[2], BW, x[3]) for x in ts if x[2]}
    out["F5"][str(u)] = {"class": c, "diag": d, "where": where(d), "terms": ts, "ends": {str(k): v for k, v in ends.items()}}
    print("  #%s %s d%s %s ends %s" % (u, c, d, ts, ends))
print("== F6 stop: rows of loop diagrams' own terminals (i / cond) and StopAll / stop (end) locals")
for d in (23405, 23166, 639):
    for t in BO.get(d, []):
        print("  diag-owned", d, t["term_name"] or "''", t["term_uid"], "src" if t["is_source"] else "sink", "w%s" % t["wire_uid"],
              other_ends(t["wire_uid"], BW, t["term_uid"]) if t["wire_uid"] else [])
for t in G["terminals"]:
    if t["owner_class"] in ("Local", "ControlTerminal") and ("stop" in t["term_name"].lower() or "StopAll" in t["term_name"]):
        e = other_ends(t["wire_uid"], BW, t["term_uid"]) if t["wire_uid"] else []
        out["F6"].setdefault("stop_objs", []).append([t["owner_uid"], t["owner_class"], t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"], where(t["frame_diagram"]), e])
        print("  ", t["owner_uid"], t["owner_class"], repr(t["term_name"]), "src" if t["is_source"] else "sink", "w%s" % t["wire_uid"], "d%s" % t["frame_diagram"], where(t["frame_diagram"]), e)
print("== F2 wire classes in s09 (termless / one-sided)")
wires = [o["uid"] for o in G["objs"] if o["class"] == "Wire"]
termless = [w for w in wires if w not in BW]
onesided = []
for w in wires:
    rs = BW.get(w, [])
    if rs and (all(r["is_source"] for r in rs) or not any(r["is_source"] for r in rs)):
        onesided.append((w, ["%s|%s|%s|%s" % (r["owner_uid"], r["owner_class"], r["term_name"], "src" if r["is_source"] else "sink") for r in rs]))
out["F2"] = {"n_wire_objs": len(wires), "termless": termless, "onesided": onesided,
             "termless_where": {str(w): OBJ[w]["owner"] for w in termless}}
print("  wire objs %d termless %d onesided %d" % (len(wires), len(termless), len(onesided)))
print("  termless", termless)
for x in onesided:
    print("  onesided", x)
print("== #2626 rows (Build Array open item)")
for t in BO[2626]:
    print("  ", t["term_name"], t["term_uid"], "src" if t["is_source"] else "sink", "w%s" % t["wire_uid"], where(t["frame_diagram"]))
json.dump(out, open("tools/bench/diag_c153_a1_1_census.json", "w", encoding="utf-8"), indent=0, default=str)
print('RESULT {"schema":"result-line/1","status":"PASS","gates":{"pass":1,"fail":0},"first_fail":null,"artefacts":[{"path":"tools/bench/diag_c153_a1_1_census.json","md5":null}]}')
