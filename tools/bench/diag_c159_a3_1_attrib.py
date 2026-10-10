# ---
# labview: none
# hardware: none
# ---
r"""Card 159-a3-1 (PD387(c)): OFFLINE attribution of the extra Error List items of the adopted P5-2a file 94ffff94
(EL 56) against P5-1 7f2582ae (EL 45). No LabVIEW, read-only on every input; writes diag_c159_a3_1_raw.json only
(attrib_c159_p5s02a.json / .md are written from it).

WHAT EXISTS (checked first, called not copied): allterms.join_wires / severed (wire table + half-wires from the
terminal rows, termless wires from the Wire objs), vigraph.dedupe_rows / build4 / wire_terminals / key_parts (full
endpoint keys per wire), errorlist_check.class_counts / norm_ocr (Error List per-class counts, OCR aliases folded).
The class->label fold (CLASS_KEYS) and the plan-action endpoint index are specific to this card.

PREDICTION CONTRACT (gates):
  K   every input md5 == the card's pin
  C   per Error List class counts: P5-1 45, P5-2a 56; new classes 'nosource' 5, 'undirected' 2, 'whilesubvi' 1;
      'notconnected' 22 -> 23, 'looseends' 21 -> 23 (brief); measured, not assumed
  S   join_wires/severed computed on both graphs (n_severed > 0 each)
  A   each new-class item gets a graph candidate set + action (or UNATTRIBUTED) - recorded, a FACT not a gate
  N   net-3 pairs listed or UNEXPLAINED - recorded
  O   attrib json written
"""
import collections
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOOLS = os.path.dirname(HERE)
ROOT = os.path.dirname(TOOLS)
sys.path.insert(0, TOOLS)
import allterms as AT          # noqa: E402  (join_wires / severed are pure; gscript is imported, never called)
import vigraph as V            # noqa: E402
import errorlist_check as EC   # noqa: E402
import protocol as P           # noqa: E402

B = "tools/bench/"
PINS = {
    B + "graph_ring_p5s02a_20261010_032547.json": "7ac24924f979afde964e63fb27957b45",
    B + "graph_ring_p5s01_20261009_125622.json": "6716c49948f097b8ac0e1780930bfab1",
    B + "plan_ring_p5s02r_in.json": "d84634bdbe0f4f94669d2443af116b8e",
    B + "errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json": "25d6084b2c2988338659758c1315a3fb",
    B + "errorlist_D1_ring_p5s01_20261009_124542_20261009_124554.json": "2e49ed9f0931ba03c3050e8c5c510edd",
}
GRAPH = {"p51": B + "graph_ring_p5s01_20261009_125622.json", "p52a": B + "graph_ring_p5s02a_20261010_032547.json"}
EL = {"p51": B + "errorlist_D1_ring_p5s01_20261009_124542_20261009_124554.json",
      "p52a": B + "errorlist_D1_ring_p5s02a_20261010_023239_20261010_024108.json"}
PLAN = B + "plan_ring_p5s02r_in.json"
OUT = os.path.join(HERE, "diag_c159_a3_1_raw.json")
STEP2, STEP3 = (24, 60), (61, 80)
# Error List class label <- substring of errorlist_check.norm_ocr(raw); first hit wins (order matters).
CLASS_KEYS = (("whilesubvi", "inputofwhileloop"), ("nosource", "hasnosource"), ("undirected", "undirectedtunnel"),
              ("looseends", "looseends"), ("notconnected", "notconnectedtoanything"),
              ("unwiredinput", "unwiredorbadterminal"), ("twotypes", "differenttypes"))
NEW_CLASS_ITEMS = {"nosource": [1, 2, 4, 6, 50], "undirected": [7, 8], "whilesubvi": [49]}   # brief, 0-based index

gates = []


def gate(label, ok, msg, extra=None):
    gates.append((label, bool(ok)))
    print("  %s  %s %s %s" % ("PASS" if ok else "FAIL", label, msg, json.dumps(extra, default=str)[:1500] if extra is not None else ""),
          flush=True)


def fact(msg, extra=None):
    print("  FACT  %s %s" % (msg, json.dumps(extra, default=str)[:2500] if extra is not None else ""), flush=True)


def jl(p):
    return json.load(open(os.path.join(ROOT, p), encoding="utf-8"))


def el_class(raw):
    n = EC.norm_ocr(raw)
    for lab, key in CLASS_KEYS:
        if EC.ocr_fold(key) in n:
            return lab
    return "other:" + n[:40]


# ------------------------------------------------------------------------------------------------ K
print("---------- [K] input pins", flush=True)
bad = {}
for p, m in PINS.items():
    got = hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()
    if got != m:
        bad[p] = got
gate("K", not bad, "every input md5 == card pin", bad)

# ------------------------------------------------------------------------------------------------ C
print("---------- [C] Error List classes", flush=True)
elitems = {k: jl(p)["items"] for k, p in EL.items()}
cc = {k: collections.Counter(el_class(it.get("raw")) for it in v) for k, v in elitems.items()}
classes = {}
for c in sorted(set(cc["p51"]) | set(cc["p52a"])):
    classes[c] = {"p51": cc["p51"].get(c, 0), "p52a": cc["p52a"].get(c, 0)}
fact("class_counts(ocr=True) p52a", EC.class_counts(elitems["p52a"], ocr=True))
fact("folded classes", classes)
fact("totals", {k: len(v) for k, v in elitems.items()})
idx_cls = {it["index"]: el_class(it.get("raw")) for it in elitems["p52a"]}
mism = {c: [i for i in ix if idx_cls.get(i) != c] for c, ix in NEW_CLASS_ITEMS.items()}
gate("C", all(not v for v in mism.values()) and len(elitems["p51"]) == 45 and len(elitems["p52a"]) == 56,
     "new-class items at the brief's indices; totals 45 / 56", mism)

# ------------------------------------------------------------------------------------------------ S
print("---------- [S] join_wires / severed on both graphs", flush=True)
GR, W, S, G4, OWN, OBJ = {}, {}, {}, {}, {}, {}
for k, p in GRAPH.items():
    d = jl(p)
    GR[k] = d
    terms, rec = V.dedupe_rows(d["terminals"])
    wire_objs = [o["uid"] for o in d["objs"] if o.get("class") == "Wire"]
    W[k] = AT.join_wires(terms, wire_objs)
    S[k] = AT.severed(W[k])
    G4[k] = V.build4(terms, d["objs"])
    OWN[k] = d.get("owners") or {}
    OBJ[k] = {int(o["uid"]): o for o in d["objs"]}
    shapes = collections.Counter(("termless" if w["termless"] else "src_only" if w["n_sink"] == 0 else "sink_only")
                                 for w in S[k])
    multi = [w["wire_uid"] for w in W[k] if w["n_src"] >= 2]
    fact("%s dedupe %s; wires %d (termless %d); severed %d %s; multi-source wires %s" % (
        k, rec["dropped"], len(W[k]), sum(1 for w in W[k] if w["termless"]), len(S[k]), dict(shapes), multi))
gate("S", all(S[k] for k in S), "severed() non-empty on both graphs", {k: len(v) for k, v in S.items()})


def ends(k, wire_uid):
    """[(is_source, owner_uid, owner_class, term_uid, term_name, term_class, frame_diagram)] of one wire."""
    out = []
    for key in V.wire_terminals(G4[k], wire_uid):
        r = G4[k]["rows"][key]
        out.append((bool(r["is_source"]), int(r["owner_uid"]), r["owner_class"], int(r["term_uid"]), r["term_name"],
                    r.get("term_class"), int(r.get("frame_diagram") or 0)))
    return sorted(out)


def sig(k, w):
    if w["termless"]:
        return ("termless", w["wire_uid"])
    e = ends(k, w["wire_uid"])
    return ("ends", tuple((x[0], x[3]) for x in e))


def shape(w):
    if w["n_src"] and w["n_sink"]:
        return "ok"
    return "termless" if w["termless"] else "src_only" if w["n_sink"] == 0 else "sink_only"


def frame_of(k, e):
    fr = sorted(set(x[6] for x in e if x[6]))
    return [{"diagram": f, "owner": OWN[k].get(str(f))} for f in fr]


sev = {k: {sig(k, w): w for w in S[k]} for k in S}
new_s = [sev["p52a"][s] for s in sev["p52a"] if s not in sev["p51"]]
res_s = [sev["p51"][s] for s in sev["p51"] if s not in sev["p52a"]]
fact("severed NEW in p52a (by endpoint term_uids; termless by wire uid)", collections.Counter(shape(w) for w in new_s))
fact("severed RESOLVED (in p51 only)", collections.Counter(shape(w) for w in res_s))

# tunnels with no source terminal (undirected candidates)
def sourceless_tunnels(k):
    out = {}
    for node, rs in G4[k]["by_node"].items():
        c = G4[k]["cls"].get(node)
        if c in ("LoopTunnel", "Tunnel", "SelectorTunnel") and rs and not any(r["is_source"] for r in rs):
            out[node] = [(r["term_uid"], r["term_class"], r["wire_uid"]) for r in rs]
    return out


ut = {k: sourceless_tunnels(k) for k in G4}
fact("tunnels with NO source terminal p51", ut["p51"])
fact("tunnels with NO source terminal p52a", ut["p52a"])

# ------------------------------------------------------------------------------------------------ plan index
plan = jl(PLAN)
acts = plan["actions"]
fact("plan actions", {"n": len(acts), "A24": acts[23]["id"], "A60": acts[59]["id"], "A61": acts[60]["id"], "A80": acts[79]["id"]})
AIDX = collections.defaultdict(list)       # ('term', term_uid) / ('uid', uid) / ('wire', uid) -> [(A#, id, field)]
for n, a in enumerate(acts, 1):
    for fld in ("src", "dst"):
        v = a.get(fld)
        if isinstance(v, dict) and isinstance(v.get("uid"), int):
            if v.get("term_uid"):
                AIDX[("term", int(v["term_uid"]))].append((n, a["id"], fld))
            AIDX[("uid", int(v["uid"]))].append((n, a["id"], fld + (":" + v["term"] if v.get("term") else "")))
    if a.get("op") == "delete_wire":
        AIDX[("wire", int(a["wire_uid"]))].append((n, a["id"], "wire_uid"))
    if a.get("op") == "delete_object":
        AIDX[("uid", int(a["uid"]))].append((n, a["id"], "delete"))
    for u in a.get("nodes") or []:
        AIDX[("uid", int(u))].append((n, a["id"], "move_in"))


def actions_for(e, wire_uid):
    hit = []
    for x in e:
        for h in AIDX.get(("term", x[3]), []):
            hit.append({"A": h[0], "id": h[1], "via": "term_uid %d (%s)" % (x[3], h[2])})
        for h in AIDX.get(("uid", x[1]), []):
            hit.append({"A": h[0], "id": h[1], "via": "owner uid %d (%s)" % (x[1], h[2])})
    for h in AIDX.get(("wire", wire_uid), []):
        hit.append({"A": h[0], "id": h[1], "via": "wire uid %d" % wire_uid})
    seen, out = set(), []
    for h in sorted(hit, key=lambda z: z["A"]):
        if (h["A"], h["via"]) not in seen:
            seen.add((h["A"], h["via"]))
            out.append(h)
    return out


def describe(k, w):
    e = [] if w["termless"] else ends(k, w["wire_uid"])
    return {"wire_uid": w["wire_uid"], "shape": shape(w), "n_src": w["n_src"], "n_sink": w["n_sink"],
            "src": [{"uid": x[1], "cls": x[2], "term_uid": x[3], "term": x[4], "tcls": x[5]} for x in e if x[0]],
            "sinks": [{"uid": x[1], "cls": x[2], "term_uid": x[3], "term": x[4], "tcls": x[5]} for x in e if not x[0]],
            "frame": frame_of(k, e), "actions": actions_for(e, w["wire_uid"]),
            "pos": (OBJ[k].get(w["wire_uid"]) or {}).get("pos")}


print("---------- [A] new severed wires in p52a", flush=True)
newd = [describe("p52a", w) for w in sorted(new_s, key=lambda w: w["wire_uid"])]
for d in newd:
    fact("NEW", d)
print("---------- [A] resolved severed wires (p51 only)", flush=True)
resd = [describe("p51", w) for w in sorted(res_s, key=lambda w: w["wire_uid"])]
for d in resd:
    fact("RESOLVED", d)
for k in ("p51", "p52a"):
    for node, rs in ut[k].items():
        e = []
        for r in G4[k]["by_node"][node]:
            e.append((False, node, G4[k]["cls"][node], r["term_uid"], r["term_name"], r["term_class"], r.get("frame_diagram") or 0))
        fact("SOURCELESS TUNNEL %s #%s actions" % (k, node), actions_for(e, 0))

print("---------- [H] the same wire uids in P5-1 (history; wire uids are only a join key within one read)", flush=True)
W51 = {w["wire_uid"]: w for w in W["p51"]}
hist = {}
for d in newd:
    u = d["wire_uid"]
    if u in W51:
        hist[u] = describe("p51", W51[u])
        fact("P5-1 wire %d" % u, {k: hist[u][k] for k in ("n_src", "n_sink", "src", "sinks", "frame")})
    else:
        fact("P5-1 wire %d absent" % u)
for w in S["p51"]:
    if not w["termless"]:
        fact("P5-1 severed non-termless (base)", describe("p51", w))
# is the #3052 'File # Saved' -> #376 'saved file refnum' pair (P5-1 w10394) carried by another wire in P5-2a?
pairs52 = [w for w in W["p52a"] if not w["termless"] and
           any(x[3] == 3060 for x in ends("p52a", w["wire_uid"])) and any(x[3] == 5772 for x in ends("p52a", w["wire_uid"]))]
fact("P5-2a wire(s) joining term 3060 -> 5772 (A13 w_ref)", [describe("p52a", w) for w in pairs52])
pairs52b = [w for w in W["p52a"] if not w["termless"] and any(x[3] == 5704 for x in ends("p52a", w["wire_uid"]))]
fact("P5-2a wire(s) on #376 'file progress' 5704 (A14 w_prog)", [describe("p52a", w) for w in pairs52b])
# PRECEDENT for 'does wiring a terminal that carries a stub clear the stub': step 1 wired the outside sources 24360
# (#24357, A19) and 24367 (#24361, A22) whose P5-1 wires went to #376 - same shape as A28/A35 on 24190/24288.
for tu in (24360, 24367, 25235, 24190, 24288, 24139, 24235, 8776, 24342):
    for k in ("p51", "p52a"):
        ws = [w for w in W[k] if not w["termless"] and any(x[3] == tu for x in ends(k, w["wire_uid"]))]
        fact("PRECEDENT %s term %d" % (k, tu), [{"wire": w["wire_uid"], "shape": shape(w),
                                                  "ends": [(x[0], x[1], x[2], x[3], x[4]) for x in ends(k, w["wire_uid"])]}
                                                 for w in ws] or "unwired")


# ------------------------------------------------------------------------------------------------ assemble
def map_class(d):
    if d["shape"] == "termless":
        return "notconnected"
    if d["shape"] == "src_only":
        return "looseends"
    sk = sorted((s["cls"], s["tcls"]) for s in d["sinks"])
    if len(sk) == 2 and ("LoopTunnel", "OuterTerminal") in sk and any(c == "SubVI" for c, _ in sk):
        return "whilesubvi"
    return "nosource"


def step_of(a):
    return 2 if STEP2[0] <= a <= STEP2[1] else 3 if STEP3[0] <= a <= STEP3[1] else None


cand = collections.defaultdict(list)
for d in newd:
    acts_ = sorted(set((h["A"], h["id"]) for h in d["actions"] if STEP2[0] <= h["A"] <= STEP3[1]))
    cand[map_class(d)].append({"kind": "wire", "uid": d["wire_uid"], "source": d["src"], "sinks": d["sinks"],
                               "frame": d["frame"], "actions": ["A%d %s" % a for a in acts_],
                               "steps": sorted(set(step_of(a) for a, _ in acts_)),
                               "evidence": "graph_ring_p5s02a wire %d (%s)" % (d["wire_uid"], d["shape"])})
for node, rs in ut["p52a"].items():
    e = [(False, node, G4["p52a"]["cls"][node], r["term_uid"], r["term_name"], r["term_class"], r.get("frame_diagram") or 0)
         for r in G4["p52a"]["by_node"][node]]
    acts_ = sorted(set((h["A"], h["id"]) for h in actions_for(e, 0)))
    cand["undirected"].append({"kind": "tunnel", "uid": node, "source": None,
                               "sinks": [{"term_uid": x[3], "tcls": x[5], "wire": r["wire_uid"]} for x, r in
                                         zip(e, G4["p52a"]["by_node"][node])],
                               "frame": frame_of("p52a", e), "actions": ["A%d %s" % a for a in acts_],
                               "steps": sorted(set(step_of(a) for a, _ in acts_)),
                               "evidence": "graph_ring_p5s02a tunnel #%d: no source terminal (P5-1: has one)" % node})
items = []
for c, ix in NEW_CLASS_ITEMS.items():
    cs = cand.get(c, [])
    for i in ix:
        if len(cs) == len(ix) and all(x["actions"] for x in cs):
            steps = sorted(set(s for x in cs for s in x["steps"]))
            one = cs[0] if len(cs) == 1 else None
            items.append({"no": i, "class": c, "pairing": "exact (1 item <-> 1 graph object)" if one else
                          "class set (%d items <-> %d graph objects; which item is which object is not readable: no uid "
                          "route, the after-double-click shots show no identifiable object)" % (len(ix), len(cs)),
                          "source": ({"uid": None, "term": None} if one["kind"] == "tunnel" or not one["source"] else
                                     {"uid": one["source"][0]["uid"], "term": one["source"][0]["term"]}) if one else
                                    "one of candidates[].source",
                          "sinks": [s.get("uid", one["uid"]) for s in one["sinks"]] if one else "one of candidates[].sinks",
                          "frame": one["frame"] if one else sorted(set(f["diagram"] for x in cs for f in x["frame"])),
                          "candidates": cs, "action": sorted(set(a for x in cs for a in x["actions"])),
                          "step": steps[0] if len(steps) == 1 else steps,
                          "evidence": one["evidence"] if one else "; ".join(x["evidence"] for x in cs)})
        else:
            items.append({"no": i, "class": c, "candidates": cs, "action": "UNATTRIBUTED", "step": None,
                          "why": "graph objects %d != items %d, or a candidate without an action" % (len(cs), len(ix))})
cls_out = {}
for c, v in classes.items():
    n_new = len(cand.get(c, []))
    cls_out[c] = dict(v, new=n_new, resolved=0, net=v["p52a"] - v["p51"],
                      graph_new_uids=[x["uid"] for x in cand.get(c, [])])
net3 = [x for c in ("notconnected", "looseends") for x in cand.get(c, [])]
unattr = [it["no"] for it in items if it["action"] == "UNATTRIBUTED"] + \
         ["net3 %s wire %d (no A24..A80 action)" % (x.get("kind"), x["uid"]) for x in net3 if not x["actions"]]
FINAL = {"card": "159-a3-1", "inputs": PINS, "items": items, "classes": cls_out, "net3": net3, "unattributed": unattr,
         "severed": {k: {"n": len(v), "shapes": dict(collections.Counter(shape(w) for w in v))} for k, v in S.items()},
         "resolved_severed": len(resd), "p51_history": hist,
         "rule": "class<-shape: termless=notconnected, source-only=looseends (count-level), sink-only with {LoopTunnel "
                 "outer, SubVI} sinks=whilesubvi, other sink-only=nosource, tunnel with no source terminal=undirected"}
FOUT = os.path.join(HERE, "attrib_c159_p5s02a.json")
json.dump(FINAL, open(FOUT, "w", encoding="utf-8"), indent=1, default=str)
fact("items", [(it["no"], it["class"], it["action"], it["step"]) for it in items])
fact("classes", {c: (v["p51"], v["p52a"], v["new"], v["resolved"]) for c, v in cls_out.items()})
fact("net3", [(x["uid"], x["actions"], x["steps"]) for x in net3])
fact("unattributed", unattr)
gate("A", len(items) == 8, "8 new-class items assembled (attributed %d)" % sum(1 for it in items if it["action"] != "UNATTRIBUTED"))
gate("N", len(net3) == 3, "net-3 graph objects listed: %d" % len(net3))

out = {"classes": classes, "severed": {k: len(v) for k, v in S.items()},
       "severed_shapes": {k: dict(collections.Counter(shape(w) for w in v)) for k, v in S.items()},
       "new": newd, "resolved": resd, "sourceless_tunnels": {k: {str(n): v for n, v in ut[k].items()} for k in ut},
       "el_new_class_items": {it["index"]: {"class": idx_cls[it["index"]], "raw": it.get("raw"),
                                            "shot": (it.get("show_error") or {}).get("bd_after")}
                              for it in elitems["p52a"] if idx_cls[it["index"]] in NEW_CLASS_ITEMS}}
json.dump(out, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
gate("O", os.path.exists(OUT) and os.path.exists(FOUT), "raw + attribution json written",
     [os.path.relpath(OUT, ROOT), os.path.relpath(FOUT, ROOT)])

npass = sum(1 for _, ok in gates if ok)
nfail = len(gates) - npass
ff = next((lab for lab, ok in gates if not ok), None)
print(P.result_line({"status": "PASS" if not nfail else "FAIL", "gates": {"pass": npass, "fail": nfail}, "first_fail": ff,
                     "artefacts": [{"path": os.path.relpath(f, ROOT).replace("\\", "/"),
                                    "md5": hashlib.md5(open(f, "rb").read()).hexdigest()} for f in (OUT, FOUT)]}),
      flush=True)
