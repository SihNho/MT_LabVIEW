"""diag_c120_s0_base - card 120-4, OFFLINE (no LabVIEW): the scratch plan's base graph = the MEASURED read of
claudeDev\\HARNESS_copyloop.vi (tools/bench/graph_harness_copyloop_c95.json, md5 pinned == the file) plus the three keys
stagesim/stagexec read and that read lacks: owners (the For body -> its ForLoop, from the graph's own objs), loops [] (no
shift registers), fs_tunnel_pairs [] (no flat sequence). Writes tools/bench/scratch_c120_base_graph.json. Nothing invented:
every row is copied from the c95 read."""
import hashlib, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import protocol as P  # noqa: E402
G = json.load(open(os.path.join(HERE, "graph_harness_copyloop_c95.json"), encoding="utf-8"))
gates = []


def gate(lab, ok, d=""):
    gates.append((lab, bool(ok)))
    print("  GATE {0}  {1}  {2}".format("PASS" if ok else "FAIL", lab, str(d)[:300]), flush=True)


fm = hashlib.md5(open(G["vi"], "rb").read()).hexdigest()
gate("B1 c95 graph md5 == HARNESS_copyloop.vi on disk", fm == G["md5"], (fm, G["md5"]))
loops = [o for o in G["objs"] if o["class"] in ("ForLoop", "WhileLoop")]
bodies = [o for o in G["objs"] if o["class"] == "Diagram" and o.get("owner") in ("ForLoop", "WhileLoop")]
gate("B2 exactly one loop and one loop body in the read", len(loops) == 1 and len(bodies) == 1, (loops, bodies))
own = {str(bodies[0]["uid"]): [loops[0]["class"], int(loops[0]["uid"])]}
out = dict(G, owners=own, loops=[], fs_tunnel_pairs=[], source="tools/bench/diag_c120_s0_base.py <- graph_harness_copyloop_c95.json")
p = os.path.join(HERE, "scratch_c120_base_graph.json")
json.dump(out, open(p, "w", encoding="utf-8"), indent=1)
m = hashlib.md5(open(p, "rb").read()).hexdigest()
print("  FACT wrote {0} md5 {1} owners {2}".format(p, m, own), flush=True)
n = sum(1 for _l, ok in gates if ok)
print(P.result_line(P.make_result(n, len(gates) - n, next((l for l, ok in gates if not ok), None),
                                  artefacts=[{"path": "tools/bench/scratch_c120_base_graph.json", "md5": m}])), flush=True)
sys.exit(0 if n == len(gates) else 1)
