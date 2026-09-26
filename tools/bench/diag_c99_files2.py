"""diag_c99_files2 - card 99-1, FILES ONLY (no LabVIEW). Second pass after diag_c99_files.log.

diag_c99_files.log P5 FAILED on OUR filter (the 'Force' substring also hits the SubVI name 'Magnet2Force v3_for M270.vi',
#28490/#28083); review archive/peer/*c99-files-p5*. P5 is re-stated here as an EXACT label match.

Existing inputs only: par1359_95_graph.json (S1, md5 3e3d23ce), graph_s3_loop15_20260924.json (bed, md5 1a11d92a),
diag_c97_gatefacts.json labels, diagram_tree_main.json.

PREDICTION CONTRACT
 P5b exact label 'Force (pN) vs Extension (nm) ' (with or without trailing blank) on exactly {#10313} among the c97 labels
 P6  #11261 'array' comes from LoopTunnel #11363 (out of ForLoop #1359); 'element' from Bundler #11608
 P7  #6085 and #5696 sit in two frames (2235, 2265) of ONE case structure (shared selector tunnels 7091/2451)
 P8  graph_s3_loop15 md5 == 1a11d92aacabf7ec844d65b8af19f39f
"""
import json, collections

B = "tools/bench/"
out = {"gates": {"pass": [], "fail": []}, "facts": {}}

def gate(name, ok, got):
    (out["gates"]["pass"] if ok else out["gates"]["fail"]).append(name)
    print(("  PASS  " if ok else "  FAIL  ") + name, " got", got)

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
        return [(t["term_uid"], t["term_name"], "SRC" if t["is_source"] else "sink", t["owner_uid"], t["owner_class"], t["frame_diagram"])
                for t in self.by_wire.get(w, []) if t["owner_uid"] != not_owner] if w else "UNWIRED"

    def node(self, uid, tag=""):
        o = self.objs.get(uid)
        print(f"  NODE #{uid} {o['class'] if o else '?'} {tag}")
        for t in self.by_owner[uid]:
            print(f"     t{t['term_uid']} {t['term_name']!r} {'SRC' if t['is_source'] else 'sink'} {t['term_class']} fd{t['frame_diagram']} w{t['wire_uid']} -> {self.ends(t['wire_uid'], uid)}")

s1 = G(B + "par1359_95_graph.json")
lab = json.load(open(B + "diag_c97_gatefacts.json", encoding="utf-8"))["labels"]

print("[P5b/P5c] review c99-files-p5 point 4")
FN = "Force (pN) vs Extension (nm)"
loc_terms = {u: [t["term_name"] for t in s1.by_owner[u]] for u, o in s1.objs.items() if o["class"] == "Local"}
print("   Local terminal names:", loc_terms)
gate("P5b no Local's terminal is the Force graph", not any(n.strip() == FN for v in loc_terms.values() for n in v), loc_terms)
recs = sorted({t["term_uid"] for t in s1.d["terminals"] if t["term_name"].strip() == FN})
gate("P5c terminal records named the Force graph == {8323}", recs == [8323], recs)
exact = sorted(u for u, r in lab.items() if r.get("label", "").strip() == FN)
print("   c97 exact-label objects:", exact)
for u in ("10313", "22542", "22560"):
    print("   label", u, lab.get(u))
ext = sorted((u, r.get("diag_uid")) for u, r in lab.items() if "Extension (nm) vs Time" in r.get("label", ""))
print("   labels 'Extension (nm) vs Time (Frame #)':", ext, [(u, s1.objs.get(int(u), {}).get("class")) for u, _ in ext])

print("\n[F1a/F1b] the #8323 feed chain")
for u in (11261, 11363, 11608, 11576, 11310):
    s1.node(u)
src = {t["term_name"]: s1.ends(t["wire_uid"], 11261) for t in s1.by_owner[11261] if not t["is_source"]}
gate("P6 #11261 array<-#11363, element<-#11608", any(e[3] == 11363 for e in src.get("array", [])) and any(e[3] == 11608 for e in src.get("element", [])), src)

print("\n[F2] indicators near the plots: ControlTerminals whose name mentions Z / Extension / Force / graph / chart")
for t in s1.d["terminals"]:
    if t["owner_class"] in ("Diagram",) and t["term_class"] == "ControlTerminal":
        n = t["term_name"]
        if any(k in n for k in ("Z", "Extension", "Force", "raph", "hart", "Plot", "plot")):
            print(f"   CT t{t['term_uid']} {n!r} {'SRC(control)' if t['is_source'] else 'sink(indicator)'} fd{t['frame_diagram']} w{t['wire_uid']} -> {s1.ends(t['wire_uid'], t['owner_uid'])}")

print("\n[F2] the Z/dZ case: selector tunnels shared by frames 2235/2265")
for u in (7091, 2451, 2765, 3176, 2992, 6132):
    s1.node(u)
frames = {t["frame_diagram"] for u in (7091, 2451) for t in s1.by_owner[u]}
gate("P7 7091/2451 have terminals in both 2235 and 2265", {2235, 2265} <= frames, sorted(frames))
sel = [t for t in s1.d["terminals"] if t["owner_class"] in ("CaseSelector",) and t["frame_diagram"] in (2235, 2265)]
print("   CaseSelector terminals in 2235/2265:", [(t["owner_uid"], t["term_name"], t["wire_uid"], s1.ends(t["wire_uid"], t["owner_uid"])) for t in sel])
cs = [t for t in s1.d["terminals"] if t["owner_class"] == "CaseSelector" and t["owner_uid"] in {x["owner_uid"] for x in sel}]
for t in cs:
    print("   selector rec:", t["owner_uid"], t["term_name"], "SRC" if t["is_source"] else "sink", "fd", t["frame_diagram"], "w", t["wire_uid"], s1.ends(t["wire_uid"], t["owner_uid"]))

print("\n[F3] S1: loop #637 conditional terminal (known #648/w3457) as a naming probe")
for t in s1.d["terminals"]:
    if t["term_uid"] == 648 or t["wire_uid"] == 3457:
        print("   ", t)

b = G(B + "graph_s3_loop15_20260924.json")
gate("P8 bed graph md5", b.d["md5"].startswith("1a11d92a"), b.d["md5"])
print("\n[F3] bed: every terminal record on the same class as #648, owned by a loop, per loop body")
cond_cls = {t["owner_class"] for t in s1.d["terminals"] if t["term_uid"] == 648}
print("   #648 owner_class set:", cond_cls)
for t in b.d["terminals"]:
    if t["owner_class"] in cond_cls or "ondition" in t["term_name"] or t["owner_uid"] in (23032, 10170, 23041, 637, 15173, 25380):
        print("   ", t["owner_uid"], t["owner_class"], t["term_uid"], repr(t["term_name"]), "SRC" if t["is_source"] else "sink", "fd", t["frame_diagram"], "w", t["wire_uid"], "->", b.ends(t["wire_uid"], t["owner_uid"]))
print("   bed locals:", [(u, o["class"]) for u, o in b.objs.items() if o["class"] == "Local"] if b.objs else "no objs in bed graph")

json.dump(out, open(B + "diag_c99_files2.json", "w"), indent=1)
ng = out["gates"]
print(f"RESULT {json.dumps({'schema':'result-line/1','status':'PASS' if not ng['fail'] else 'FAIL','gates':{'pass':len(ng['pass']),'fail':len(ng['fail'])},'first_fail':ng['fail'][0] if ng['fail'] else None,'artefacts':[]})}")
