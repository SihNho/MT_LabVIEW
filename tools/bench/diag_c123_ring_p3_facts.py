r"""diag_c123_ring_p3_facts - card 123-2 STEP 1: P3 facts from FILES ONLY (no LabVIEW, no COM import).
Reads the P2b stagesim END graph (tools/bench/sim/ring_p2b/step_10_create.json; summary.json says it is the last step) and
writes tools/bench/facts_c123_p3.json: (a) the Image Type sources of IMAQ Create #20436 and of the IMAQ Create inside For
#23093 (#23099), traced back through tunnels; (b) For #23093's tunnels, its body/parent diagrams; (c) loop 1.1 (#637, body
639) terminals P3 binds to and the five P2b indicators by label. Existing: diag_c122_p3.py (pool graph, same questions for
c122) - this re-reads the P2b END graph because wire uids are re-issued per read (P2a dump != pool dump).
PREDICTION: E0 summary's last step == step_10 (md5 830fbe67...); F1 #20436 and #23099 each have an 'Image Type' sink row;
F2 For #23093 body diagram resolves (owners[body] == ForLoop 23093); F3 #6810 has 'current image number', 'Image Out',
'error out' rows on 639; F4 #30117/#4580 'Value' sources on 639, #637 i (t644) on 639; F5 the five labels each ONE
ControlTerminal sink row on #4866.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c123_ring_p3_facts.log -- py -u tools/bench/diag_c123_ring_p3_facts.py"""
import hashlib, json, os, sys                                                       # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol                                                                    # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
END = "tools/bench/sim/ring_p2b/step_10_create.json"
md5 = lambda p: hashlib.md5(open(os.path.join(ROOT, p), "rb").read()).hexdigest()  # noqa: E731
J = lambda p: json.load(open(os.path.join(ROOT, p), encoding="utf-8"))              # noqa: E731
G = {"pass": 0, "fail": 0, "first": None}


def gate(lbl, ok, det=""):
    G["pass" if ok else "fail"] += 1
    if not ok and not G["first"]:
        G["first"] = lbl
    print("GATE %s | %s | %s" % ("PASS" if ok else "FAIL", lbl, json.dumps(det, default=str)[:600]), flush=True)


S = J("tools/bench/sim/ring_p2b/summary.json")
last = dict((S.get("steps") or [{}])[-1].get("file") or {}, n=(S.get("steps") or [{}])[-1].get("n"))
st = J(END)["state"]
T, OBJ, OWN = st["terminals"], {int(o["uid"]): o for o in st.get("objs") or []}, {int(k): v for k, v in (st.get("owners") or {}).items()}
PAIRS = J("tools/bench/diag_c122_graph_p2a.json").get("fs_tunnel_pairs") or []
cite = lambda t: "%s:terminals[term_uid=%s]" % (END, t)                             # noqa: E731
KEYS = ("term_uid", "term_name", "is_source", "wire_uid", "owner_uid", "owner_class", "frame_diagram", "term_class")
row = lambda r: dict([(k, r.get(k)) for k in KEYS], src=cite(r["term_uid"]))      # noqa: E731
of = lambda u: [r for r in T if int(r["owner_uid"]) == int(u)]                      # noqa: E731
on_wire = lambda w: [r for r in T if w and int(r["wire_uid"] or 0) == int(w)]       # noqa: E731
TUN = ("LoopTunnel", "FlatSequenceInnerTunnel", "FlatSequenceOuterTunnel", "SelectorTunnel", "Tunnel", "LeftShiftRegister", "RightShiftRegister")


def pair_of(term):
    for p in PAIRS:
        if int(p.get("term_a") or 0) == int(term):
            return int(p["term_b"])
        if int(p.get("term_b") or 0) == int(term):
            return int(p["term_a"])
    return None


def back(sink, hops=12):
    """the source chain of a sink row: same-wire source, then through a tunnel's other (sink) face."""
    path, r = [], sink
    for _ in range(hops):
        src = [x for x in on_wire(r["wire_uid"]) if x["is_source"]]
        if len(src) != 1:
            path.append({"stop": "%d sources on wire %s" % (len(src), r["wire_uid"])})
            return path
        s = src[0]
        path.append(row(s))
        if s["owner_class"] not in TUN:
            return path
        other = [x for x in of(s["owner_uid"]) if not x["is_source"]]
        pt = pair_of(s["term_uid"])
        other = [x for x in T if int(x["term_uid"]) == pt] or other
        if len(other) != 1:
            path.append({"stop": "tunnel #%s: %d sink faces" % (s["owner_uid"], len(other))})
            return path
        r = other[0]
        path.append(row(r))
    return path


F = {"schema": "facts/1", "card": "123-2", "graph": {"path": END, "md5": md5(END)}, "summary_md5": md5("tools/bench/sim/ring_p2b/summary.json")}
gate("E0 summary's last step is step_10 and its md5 == the file", last.get("path", "").endswith("step_10_create.json") and last.get("md5") == md5(END), last)
# (a) Image Type sources
F["a_image_type"] = {}
for u in (20436, 23099, 13245, 13938):
    rs = of(u)
    it = [r for r in rs if r["term_name"] == "Image Type" and not r["is_source"]]
    F["a_image_type"][str(u)] = {"obj": OBJ.get(u), "terms": [(r["term_uid"], r["term_name"], r["is_source"], r["wire_uid"]) for r in rs],
                                 "image_type_sink": [row(r) for r in it], "back": back(it[0]) if it else None,
                                 "name_sink": [row(r) for r in rs if r["term_name"] == "Image Name" and not r["is_source"]]}
    if u in (20436, 23099):
        gate("F1 #%d has ONE 'Image Type' sink row" % u, len(it) == 1, [x["term_uid"] for x in it])
ta, tb = [F["a_image_type"][k]["back"] for k in ("20436", "23099")]
F["a_same_source"] = bool(ta and tb and ta[0].get("term_uid") == tb[0].get("term_uid"))
# (b) For #23093
body = [d for d, v in OWN.items() if v == ["ForLoop", 23093]]
F["b_for"] = {"owners_23093": OWN.get(23093), "body": body, "obj": OBJ.get(23093)}
gate("F2 For #23093 body diagram resolves from owners", len(body) == 1, body)
par = (OWN.get(23093) or [None, None])[1]
tuns = sorted(set(int(r["owner_uid"]) for r in T if r["owner_class"] == "LoopTunnel" and int(r["frame_diagram"] or 0) in body))
F["b_for"]["tunnels"] = [{"uid": t, "faces": [row(r) for r in of(t)], "this_for": any(int(r["frame_diagram"] or 0) == par for r in of(t))} for t in tuns]
F["b_for"]["body_terms"] = [row(r) for r in T if int(r["frame_diagram"] or 0) in body and r["owner_class"] != "LoopTunnel"]
F["b_for"]["new_image"] = [row(r) for r in of(23099) if r["term_name"] == "New Image"]
F["b_for"]["sr"] = [lp for lp in st.get("loops") or [] if int(lp.get("loop_uid") or 0) == 23093]
# (c) loop 1.1
F["c_loop11"] = {"owners_639": OWN.get(639), "owners_637": OWN.get(637), "owners_686": OWN.get(686)}
want = {6810: ("current image number", "Image Out", "error out", "error in", "Image In", "Buffer to extract"), 30117: ("Value",), 4580: ("Value",)}
for u, names in want.items():
    for n in names:
        rs = [r for r in of(u) if r["term_name"] == n]
        F["c_loop11"]["%d|%s" % (u, n)] = [dict(row(r), sinks=[row(x) for x in on_wire(r["wire_uid"]) if not x["is_source"]] if r["is_source"] else None) for r in rs]
        gate("F3/F4 #%d '%s' ONE row on 639" % (u, n), len(rs) == 1 and int(rs[0]["frame_diagram"] or 0) == 639, [(r["term_uid"], r["frame_diagram"]) for r in rs])
i = [r for r in T if int(r["term_uid"]) == 644]
F["c_loop11"]["637|i"] = [dict(row(r), sinks=[row(x) for x in on_wire(r["wire_uid"]) if not x["is_source"]]) for r in i]
gate("F4 #637 i = t644 on 639", len(i) == 1 and int(i[0]["frame_diagram"] or 0) == 639, i)
F["c_loop11"]["sr_637"] = [lp for lp in st.get("loops") or [] if int(lp.get("loop_uid") or 0) == 637]
F["c_loop11"]["old_wire_uids_c122"] = {"w3747": [row(r) for r in on_wire(3747)], "w653": [row(r) for r in on_wire(653)], "w3040": [row(r) for r in on_wire(3040)]}
F["c_ind"] = {}
for lab in ("Num", "TransPos", "RotPos", "FrameIdx", "Latest"):
    rs = [r for r in T if r["term_name"] == lab and r.get("term_class") == "ControlTerminal"]   # sim rows: owner = the Diagram
    F["c_ind"][lab] = [dict(row(r), const=[row(x) for x in on_wire(r["wire_uid"]) if x["is_source"]]) for r in rs]
    gate("F5 '%s' ONE ControlTerminal sink row on #4866" % lab, len(rs) == 1 and not rs[0]["is_source"] and int(rs[0]["frame_diagram"] or 0) == 4866, [(r["term_uid"], r["frame_diagram"]) for r in rs])
F["c_ind_sym"] = {"sym": S.get("sym"), "new_classes": S.get("new_classes"), "src": "tools/bench/sim/ring_p2b/summary.json:2140-2163"}
F["c_ind_objs"] ={str(u): OBJ.get(u) for u in sorted(set(int(r["owner_uid"]) for v in F["c_ind"].values() for r in v))}
F["loop11_diagram_classes"] = sorted(set(r["owner_class"] for r in T if int(r["frame_diagram"] or 0) == 639))
OUT = "tools/bench/facts_c123_p3.json"
json.dump(F, open(os.path.join(ROOT, OUT), "w", encoding="utf-8"), indent=1, default=str)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"], artefacts=[{"path": OUT, "md5": md5(OUT)}])), flush=True)
