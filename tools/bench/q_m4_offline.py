"""q_m4_offline - READ-ONLY, no LabVIEW (cycle 68 material, M4 brief J1). On the step-4 graph of the rowD bed (M3a-4
did not touch WhileLoop #637's counter path - it retired only VISA/position carriers):
  (1) wire 3268's terminals and the SOURCE of its net (J1: the frame counter's real source in loop 1.1 #637);
  (2) the primitive classes on the bed (donor candidates for Not Equal? / And / Select / Wait (ms));
  (3) the #10407 t0 feed today (the schedule Local) and #23032/#23058 contents."""
import collections, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import jev_candidates as JC   # noqa: E402
import vigraph as V           # noqa: E402

G = JC.load(JC.BED_KEY)
print("graph keys:", sorted(k for k in G if not k.startswith("_"))[:30])
wt = V.wire_terminals(G, 3268)
print("(1) wire 3268 terminals:", [V.show(k) for k in wt])
for k in wt:
    r = JC.term_row(G, k)
    print("   ", V.show(k), "is_source", r.get("is_source") if r else None, "frame", r.get("frame_diagram") if r else None)
srcs = [k for k in wt if (JC.term_row(G, k) or {}).get("is_source")]
print("   sources on the wire:", [V.show(k) for k in srcs])
for k in wt:
    if not (JC.term_row(G, k) or {}).get("is_source"):
        up = V.sources_of(G, k)
        print("   sources_of(", V.show(k), ") n=", len(up), [V.show(x) for x in list(up)[:12]])
        print("   effective_sources:", [V.show(x) for x in V.effective_sources(G, k)][:12])
        break
cc = collections.Counter(G["cls"].values())
print("(2) classes:", cc.most_common(70))
lab = JC.node_labels_default()
want = ("Not Equal", "And", "Select", "Wait", "Increment", "Add", "Equal", "Or", "Not")
hits = collections.defaultdict(list)
for u, c in G["cls"].items():
    lb = lab.get(int(u), "")
    for w in want:
        if lb.startswith(w) or w.lower() in lb.lower():
            hits[lb].append((int(u), c))
for lb in sorted(hits):
    print("   label", repr(lb), hits[lb][:6], "n=", len(hits[lb]))
print("(3) #10407 terminals:")
for k in V.terminals(G, node=10407):
    r = JC.term_row(G, k)
    print("   ", V.show(k), "src" if r.get("is_source") else "sink", "wire", r.get("wire_uid"),
          "eff", [V.show(x) for x in V.effective_sources(G, k)][:3] if not r.get("is_source") else "")
for n in (23032, 23058, 637, 639):
    print("   node", n, "class", G["cls"].get(n) or G["cls"].get(str(n)), "terms", len(V.terminals(G, node=n)))
