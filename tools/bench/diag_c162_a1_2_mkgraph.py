# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c161_p5s02b_scratch.log:77
# ---
r"""diag_c162_a1_2_mkgraph - card 162-a1-2 (OFFLINE, no LabVIEW opened): writes diag_c162_a1_2_graph_plan.json, the decision-row plan of
diag_c162_a1_2_graph.py (the read-only graph read of P5-2 step 2's ADOPTED file claudeDev\D1_ring_p5s02b_<stamp>.vi). COPY of
diag_c158_a3_2b_mkgraph.py (card 158-a3-2b, ran) with: names p5s02a -> p5s02b (plan / scratch log = recipe LOG constant c161 / sum / json, base plan
diag_c158_a3_2b_graph_plan.json, out prefix graph_ring_p5s02b); the made objects are the 5 BOUND symbols of the STEPX lines (step 2 has no
`create` action: the tunnel ops bind -1/-7/-12/-19/-24) with their class read from the simulator's end step sim/ring_p5s02b/step_20_wire.json
(no class typed); counts 21 -> 12 new wires (term_identity.new) and deleted = lost_w - new.
PREDICTION: 5 bound symbols, one STEPX line each, all SelectorTunnel in the sim end (census SelectorTunnel 5); new wires 12 == D gate pairs 12;
deleted wires [24285, 24300, 24312]; last adopted record md5 == sum final_md5 == f9ae7751.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c162_a1_2_mkgraph.log -- py -u tools/bench/diag_c162_a1_2_mkgraph.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c161_p5s02b_scratch.log"
OUTP = "diag_c162_a1_2_graph_plan.json"
summ, scr, old = J("diag_c161_p5s02b_scratch_sum.json"), J("diag_c161_p5s02b_scratch.json"), J("diag_c158_a3_2b_graph_plan.json")
simend = J(os.path.join("sim", "ring_p5s02b", "step_20_wire.json"))


def objs(o, acc):
    if isinstance(o, dict):
        if isinstance(o.get("uid"), int) and o["uid"] < 0 and "class" in o:
            acc.setdefault(o["uid"], set()).add(o["class"])
        for v in o.values():
            objs(v, acc)
    elif isinstance(o, list):
        for v in o:
            objs(v, acc)
    return acc


SIMC = objs(simend, {})
alll = open(os.path.join(B, LOGN), encoding="utf-8", errors="replace").read().splitlines()
SEG0 = max(i for i, ln in enumerate(alll) if ln.startswith("BGRUN START"))
RX = re.compile(r"STEPX\s+(\d+)\s+\S+\s+acts \[[^\]]*\] ids \[[^\]]*\] bound (\{[^}]*\})")
made, hits = {}, {}
for i, ln in enumerate(alll, 1):
    if i - 1 < SEG0:
        continue
    m = RX.search(ln)
    if m:
        for sym, uid in ast.literal_eval(m.group(2)).items():
            hits.setdefault(sym, []).append(i)
            made[str(uid)] = "/".join(sorted(SIMC.get(sym, {"?"})))
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT last segment of {0} starts at line {1}; bound {2}; sim classes {3}".format(LOGN, SEG0 + 1, hits, dict((k, sorted(v)) for k, v in SIMC.items())), flush=True)
gate("C 5 bound symbols, one STEPX line each (last segment), each a SelectorTunnel in the sim end",
     len(hits) == 5 and all(len(v) == 1 for v in hits.values()) and len(made) == 5 and set(made.values()) == {"SelectorTunnel"}, (hits, made))
ti = scr.get("term_identity") or {}
nw = sorted(set(int(w) for w in ti.get("new") or []))
dwires = sorted(set(int(w) for w in ti.get("lost_w") or []) - set(nw))
dl = [ln for ln in alll[SEG0:] if "  PASS  D new (source, sink) pairs" in ln]
gate("W term_identity.new 12 wires; the log's D gate PASSED on 12 new pairs", len(nw) == 12 and bool(dl) and "pairs 12 ==" in dl[-1],
     (len(nw), nw, dl[-1][:160] if dl else None))
gate("DW deleted wires (lost_w - new) == [24285, 24300, 24312]", dwires == [24285, 24300, 24312], dwires)
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
ADV, ADM = (rec.get("artefact") or {}).get("path"), (rec.get("artefact") or {}).get("md5")
gate("A last adopted record = claudeDev\\D1_ring_p5s02b_*, md5 == file == sum final_md5", summ.get("final") and ADV
     and os.path.basename(ADV).startswith("D1_ring_p5s02b_") and SX.md5(ADV) == ADM == summ.get("final_md5") == SX.md5(summ["final"]),
     (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 162-a1-2 (PD354(a)): FINALIZED decision-row plan of tools/bench/diag_c162_a1_2_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P5-2 step 2's ADOPTED file (tools/bench/diag_c162_a1_2_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c158_a3_2b_graph.py -> tools/bench/graph_ring_p5s02b_<ts>.json. Written by tools/bench/diag_c162_a1_2_mkgraph.py.")
out["input"] = {"vi": ADV, "md5": ADM, "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": [], "deleted_wires": dwires, "new_wires": nw,
                "cite": "STEPX bound symbols in tools/bench/{0}:{1}, classes from tools/bench/sim/ring_p5s02b/step_20_wire.json; new wires = "
                        "term_identity.new of tools/bench/diag_c161_p5s02b_scratch.json; deleted wires = term_identity.lost_w minus new".format(
                            LOGN, ",".join(str(v[0]) for v in hits.values()))}
out["out_prefix"] = "graph_ring_p5s02b"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("P5-2a", "P5-2b").replace("p5s02a", "p5s02b")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}".format(json.dumps(made, sort_keys=True), nw, dwires), flush=True)
print("FACT plan json tools/bench/{0} md5 {1}".format(OUTP, SX.md5(os.path.join(B, OUTP))), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
