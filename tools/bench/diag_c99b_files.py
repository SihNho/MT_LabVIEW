"""diag_c99b_files - card 99-2, FILES ONLY (no LabVIEW): F1 ring identity, F2 inbound wires of the PD212(b) moved set,
F5 TurnOff #24444 (file part), F6 verb census.

FOUND FIRST: diag_c99_files2.py's graph class (par1359_95_graph.json = S1 md5 3e3d23ce, terminals table), f1359_gate_facts_97
(B_rows / B_cross: w8811 -> #8741 and #9227), docs/toolkit-capabilities.md, gscript/stagekit/stagexec defs.

PREDICTION CONTRACT
 P1 w8811 (#8634 'output array') has exactly 2 sinks: #8741 'array' and LoopTunnel #9227 (indexing, out of #1359)
 P2 #9227's outer wire ends on diagram 639 (the ring's right shift register or a node that feeds it)
 P3 every wire into the moved set from outside it comes from: w8811 (ring), #8476 Exp Baseline, #11608 (WLC) and the two
    half-width controls via tunnels 31051/31137 (the card's claim is 'w8811 + #8476 + #11608 only')
 P4 TurnOff #24444 terminal rows exist; no Local names TurnOff
 P5 graph md5 == 3e3d23cefd3a334001aa9d6156bf1aee
"""
import collections, glob, json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
P, F = [], []
OUT = {"facts": {}}


def gate(name, ok, got):
    (P if ok else F).append(name)
    print(("  PASS  " if ok else "  FAIL  ") + name, " got", got, flush=True)


class G:
    def __init__(self, path):
        self.d = json.load(open(path, encoding="utf-8"))
        self.objs = {o["uid"]: o for o in self.d.get("objs", [])}
        self.by_wire = collections.defaultdict(list)
        self.by_owner = collections.defaultdict(list)
        for t in self.d["terminals"]:
            if t["wire_uid"]:
                self.by_wire[t["wire_uid"]].append(t)
            self.by_owner[t["owner_uid"]].append(t)

    def ends(self, w, not_owner=None):
        if not w:
            return "UNWIRED"
        return [(t["owner_uid"], t["owner_class"], t["term_name"], "SRC" if t["is_source"] else "sink", "fd%s" % t["frame_diagram"])
                for t in self.by_wire.get(w, []) if t["owner_uid"] != not_owner]

    def node(self, uid, tag=""):
        o = self.objs.get(uid, {})
        print("  NODE #%s %s %s" % (uid, o.get("class", self.by_owner[uid][0]["owner_class"] if self.by_owner[uid] else "?"), tag))
        for t in self.by_owner[uid]:
            print("     t%s %r %s %s fd%s w%s -> %s" % (t["term_uid"], t["term_name"], "SRC" if t["is_source"] else "sink", t["term_class"],
                                                    t["frame_diagram"], t["wire_uid"], self.ends(t["wire_uid"], uid)))


s1 = G(os.path.join(B, "par1359_95_graph.json"))
print("keys:", list(s1.d.keys()), "objs:", len(s1.objs), "terminals:", len(s1.d["terminals"]))
gate("P5 graph md5 is S1", s1.d.get("md5") == "3e3d23cefd3a334001aa9d6156bf1aee", s1.d.get("md5"))
if s1.objs:
    print("  obj sample:", list(s1.objs.values())[0])

print("\n[F1] ring: #8634 output -> w8811 -> ?")
for u in (8634, 9227, 9087, 9025, 8953, 8984, 8741, 8775, 8795, 8566, 10177):
    s1.node(u)
e8811 = s1.ends(8811)
sinks = sorted((e[0], e[2]) for e in e8811 if e[3] == "sink")
gate("P1 w8811 sinks == {#8741 array, #9227}", sorted(x[0] for x in sinks) == [8741, 9227], sinks)
out9227 = [t for t in s1.by_owner[9227] if t["is_source"]]
print("  #9227 source terminals:", [(t["term_uid"], t["frame_diagram"], t["wire_uid"], s1.ends(t["wire_uid"], 9227)) for t in out9227])
o = [e for t in out9227 for e in (s1.ends(t["wire_uid"], 9227) if t["wire_uid"] else [])]
gate("P2 #9227 outer wire ends on diagram 639", any(e[4] == "fd639" for e in o), o)
# follow the right SR / whatever takes w9215 one hop further
for e in o:
    s1.node(e[0], "(sink of #9227's outer wire)")
OUT["facts"]["F1_w8811_ends"] = e8811
OUT["facts"]["F1_9227_outer"] = o

print("\n[F2] inbound wires into the moved set (PD212(b) set + #11261 + #8323)")
SET = {8741, 8764, 8476, 8775, 8795, 27716, 28180, 28233, 29009, 11310, 31051, 31137, 11363, 11261, 8323}
inbound = []
for u in sorted(SET):
    for t in s1.by_owner[u]:
        if t["is_source"] or not t["wire_uid"]:
            continue
        src = [x for x in s1.by_wire[t["wire_uid"]] if x["is_source"]]
        for x in src:
            if x["owner_uid"] not in SET:
                inbound.append({"sink": "%d:%s" % (u, t["term_name"]), "sink_fd": t["frame_diagram"], "wire": t["wire_uid"],
                                "src": "%d:%s" % (x["owner_uid"], x["term_name"]), "src_class": x["owner_class"], "src_fd": x["frame_diagram"]})
for r in inbound:
    print("   IN  w%(wire)s  %(src)s [%(src_class)s fd%(src_fd)s] -> %(sink)s fd%(sink_fd)s" % r)
srcs = sorted({int(r["src"].split(":")[0]) for r in inbound})
print("   source owners:", srcs)
OUT["facts"]["F2_inbound"] = inbound
# also: what is not in SET but a sink of set outputs (outbound), to see the set is closed
outbound = []
for u in sorted(SET):
    for t in s1.by_owner[u]:
        if not t["is_source"] or not t["wire_uid"]:
            continue
        for x in s1.by_wire[t["wire_uid"]]:
            if not x["is_source"] and x["owner_uid"] not in SET:
                outbound.append("%d:%s -w%d-> %d:%s [%s fd%s]" % (u, t["term_name"], t["wire_uid"], x["owner_uid"], x["term_name"], x["owner_class"], x["frame_diagram"]))
print("   OUTBOUND:", outbound)
OUT["facts"]["F2_outbound"] = outbound
for u in (31051, 31137, 8476):
    s1.node(u)

print("\n[F5] TurnOff #24444 in the S1 graph")
tt = [t for t in s1.d["terminals"] if t["term_name"].strip() == "TurnOff" or t["owner_uid"] == 24444]
for t in tt:
    print("   ", t, "->", s1.ends(t["wire_uid"], t["owner_uid"]))
loc = {u: [t["term_name"] for t in s1.by_owner[u]] for u, ob in s1.objs.items() if ob.get("class") == "Local"}
gate("P4 TurnOff terminal rows exist and no Local names it", bool(tt) and not any(n.strip() == "TurnOff" for v in loc.values() for n in v), (len(tt), loc))
OUT["facts"]["F5_terminals"] = tt
lab_path = os.path.join(B, "diag_c97_gatefacts.json")
if os.path.exists(lab_path):
    lab = json.load(open(lab_path, encoding="utf-8")).get("labels", {})
    hits = {u: r for u, r in lab.items() if "TurnOff" in str(r.get("label", ""))}
    print("   c97 label sweep objects labelled TurnOff:", hits)
    OUT["facts"]["F5_label_hits"] = hits
print("  [F5b] the TurnOff-labelled objects and their diagrams")
for u in (8603, 25116, 25261):
    s1.node(u, str(s1.objs.get(u)))
for dg in (4866, 25392, 639, 3628):
    print("   diagram #%d obj %s" % (dg, s1.objs.get(dg)))
    # the structure owning the diagram = the obj whose uid is closest below and whose class is a structure is NOT reliable;
    # report the terminals on that diagram whose owner is a structure (tunnels / selectors) instead
    own = sorted({(t["owner_uid"], t["owner_class"]) for t in s1.d["terminals"] if t["frame_diagram"] == dg
                  and t["owner_class"] in ("SelectorTunnel", "FlatSequenceInnerTunnel", "LoopTunnel", "CaseSelector", "Tunnel", "EventDataNode")})[:8]
    print("     structure-owned terminals on it:", own)
for u in (8603, 25116):
    for t in s1.by_owner.get(u, []):
        OUT["facts"].setdefault("F5_prop_terms", []).append([u, t["term_name"], t["is_source"], t["wire_uid"], t["frame_diagram"]])

print("\n[F6] verb census")
defs = {}
for f in ("tools/gscript.py", "tools/stagekit.py", "tools/stagexec.py"):
    for i, line in enumerate(open(os.path.join(ROOT, f), encoding="utf-8"), 1):
        m = re.match(r"\s*def (\w+)\(", line)
        if m:
            defs.setdefault(m.group(1), "%s:%d" % (f, i))
want = ["while_loop", "for_loop", "loop_in", "create_indicator", "create_control", "create_local_read", "build_property",
        "create_const_loop_term", "move_in", "move_out", "copy_in", "wire_indicators", "build_clfn", "drop_subvi", "set_index_mode"]
for w in want:
    print("   def %-24s %s" % (w, defs.get(w, "MISSING")))
OUT["facts"]["F6_defs"] = {w: defs.get(w, "MISSING") for w in want}
tc = open(os.path.join(ROOT, "docs", "toolkit-capabilities.md"), encoding="utf-8").read().splitlines()
for key in ("Wait", "Visible", "hidden", "Hidden", "Change To Write", "Create:Local", "OpCreateLocalRead", "move_in", "OpMoveIn",
            "loop_in", "Representation", "I32"):
    ls = [i + 1 for i, l in enumerate(tc) if key in l]
    print("   toolkit-capabilities '%s' lines: %s" % (key, ls[:12]))
    OUT["facts"].setdefault("F6_toolkit_lines", {})[key] = ls[:12]
ops = sorted(os.path.basename(p) for p in glob.glob(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\Op*.vi")
             + glob.glob(r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev\ops\Op*.vi"))
hit = [o for o in ops if re.search(r"Wait|Local|Visible|Hidden|Loop|Move|Prop|Indicator|Control", o)]
print("   op VIs matching Wait|Local|Visible|Hidden|Loop|Move|Prop|Indicator|Control:", hit)
OUT["facts"]["F6_ops"] = hit

json.dump(OUT, open(os.path.join(B, "diag_c99b_files.json"), "w", encoding="utf-8"), indent=1, default=str)
print("\n=== GATES: %d pass / %d fail%s" % (len(P), len(F), ("; failing: " + ", ".join(F)) if F else ""))
sys.path.insert(0, os.path.join(ROOT, "tools"))
try:
    import protocol
    print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None,
                                                    [{"path": "tools/bench/diag_c99b_files.json", "md5": None}])))
except Exception as e:                                                               # noqa: BLE001
    print('RESULT {"status":"%s","gates":{"pass":%d,"fail":%d},"note":"protocol.result_line unavailable: %s"}' % ("PASS" if not F else "FAIL", len(P), len(F), type(e).__name__))
