"""sim_k_probe_79 - card 79-4 read-only diagnostic: facts of run 2's end state (sim/k_split/step_27) for the PD178(b)
gate definitions (ownership tree, t3's wires, end-graph sources of the 10 end rows). Pure Python, no LabVIEW.
PREDICTION: t3 unwired at end; #23166's tree parent is #10170; no end row sources a KERN (e) terminal."""
import json, os, sys, glob
ROOT = r"G:/Codes/LabVIEW_Codes/MinLab/zz_LabView VI/AAA_UNIST/2. Tracking/V6_ParallelLoop"
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as S, vigraph as V, jev_candidates as JC
B = os.path.join(ROOT, "tools", "bench")
C = json.load(open(os.path.join(B, "k_contract_79_data.json"), encoding="utf-8"))
print("contract keys", list(C))
print("diagram_parent sample", list(C["diagram_parent"].items())[:5])
for k in C:
    if "owner" in k or "tree" in k:
        print(k, str(C[k])[:400])
st0 = json.load(open(os.path.join(B, "sim/k_split/step_00_base.json"), encoding="utf-8"))["state"]
stE = json.load(open(glob.glob(os.path.join(B, "sim/k_split/step_27_*.json"))[0], encoding="utf-8"))["state"]
print("obj sample", st0["objs"][:2])
o = [x for x in st0["objs"] if int(x["uid"]) in (23166, 10170, 5058)]
print("objs", o)
lab = JC.node_labels_default()
G0 = S.graph(st0, lab); GE = S.graph(stE, lab)
print("tree keys", list(G0["tree"].keys()))
par = G0["tree"]["parent"]
print("tree parent 23166", par.get(23166), "5058", par.get(5058), " end 5058", GE["tree"]["parent"].get(5058))
for k2 in G0["tree"]:
    if k2 != "parent":
        v = G0["tree"][k2]
        print("tree", k2, type(v), str(v)[:200] if not isinstance(v, dict) else [(a, v[a]) for a in list(v)[:3]], "23166:" , v.get(23166) if isinstance(v, dict) else None, v.get("23166") if isinstance(v, dict) else None)
KERN = 5058
kr = [r for r in stE["terminals"] if V.node_of(r) == KERN]
for r in sorted(kr, key=lambda r: r["term_name"]):
    w = r["wire_uid"]; oth = [(V.node_of(x), x["term_name"], x["is_source"]) for x in stE["terminals"] if w and x["wire_uid"] == w and x is not r]
    print("END", r["term_name"], "src" if r["is_source"] else "sink", "w", w, oth[:4])
# t3 base wire consumers
t3 = [r for r in st0["terminals"] if V.node_of(r) == KERN and r["term_name"] == "Bead is good? array out" and r["is_source"]]
print("t3 base", t3)
w3 = t3[0]["wire_uid"]
cons = [r for r in st0["terminals"] if r["wire_uid"] == w3 and not r["is_source"]]
print("t3 base consumers", [(V.node_of(r), r["term_uid"], r["term_class"], r["owner_class"]) for r in cons])
for r in cons:
    e = [x for x in stE["terminals"] if x["term_uid"] == r["term_uid"] and x["term_class"] == r["term_class"]]
    print(" end of", r["term_uid"], [(x["wire_uid"], S.has_source(stE, x["wire_uid"])) for x in e])
S1 = JC.load(JC.S1_KEY)
summ = json.load(open(os.path.join(B, "sim/k_split/summary.json"), encoding="utf-8"))
ekeys = [k for k in GE["rows"] if V.key_parts(k)[0] == KERN]
print("sample key", ekeys[:2])
for k in summ["end_cdiff_rows"]:
    es = V.effective_sources(GE, k); k1, _h = JC.map_key(S1, k, GE); s1 = V.effective_sources(S1, k1) if k1 else None
    print("ROW", V.key_parts(k), "END", sorted(V.key_parts(e)[0:3:2] for e in es)[:6], "S1", sorted(V.key_parts(e)[0:3:2] for e in s1)[:6] if s1 is not None else None)
print("ROWS on 23166", sorted(set((r["owner_uid"], r["owner_class"], r["term_class"], r["term_name"]) for r in st0["terminals"] if r["frame_diagram"] == 23166)))
print("ROWS owner 10170/WhileLoop", sorted(set((r["owner_uid"], r["owner_class"], r["term_class"], r["frame_diagram"]) for r in st0["terminals"] if r["owner_uid"] == 10170 or r["owner_class"] == "WhileLoop"))[:30])
print("END KERN frame_diagrams", sorted(set(r["frame_diagram"] for r in stE["terminals"] if V.node_of(r) == KERN)))
print("loops", [(L.get("loop_uid"), sorted(L.keys())) for L in st0["loops"]][:12])
print("objs WhileLoop+Diagram(owner WhileLoop)", [(o["uid"], o["class"], o["pos"]) for o in st0["objs"] if o["class"] == "WhileLoop" or (o["class"] == "Diagram" and o["owner"] == "WhileLoop")])
OB = st0["objs"]
for L in (10170, 23041, 23032, 637):
    i = next(k for k, o in enumerate(OB) if int(o["uid"]) == L)
    print("OBJS after", L, [(o["uid"], o["class"], o["owner"]) for o in OB[i:i + 8]])
print("n objs", len(OB), "Diagrams owner WhileLoop", sum(1 for o in OB if o["class"] == "Diagram" and o["owner"] == "WhileLoop"), "WhileLoops", sum(1 for o in OB if o["class"] == "WhileLoop"))
def owned_body(loop):
    i = next(k for k, o in enumerate(OB) if int(o["uid"]) == loop) + 1
    while i < len(OB) and OB[i]["class"] == "OuterTerminal":
        i += 1
    nx = OB[i] if i < len(OB) else {}
    return int(nx["uid"]) if nx.get("class") == "Diagram" and nx.get("owner") == "WhileLoop" else None
print("OWNED_BODY", [(o["uid"], owned_body(int(o["uid"]))) for o in OB if o["class"] == "WhileLoop"])
import protocol
print(protocol.result_line(protocol.make_result(1, 0, None, [])))
