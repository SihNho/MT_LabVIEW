# ---
# labview: none
# hardware: none
# ---
r"""diag_c158_a3_2b_mkgraph - card 158-a3-2b (OFFLINE, no LabVIEW opened): writes diag_c158_a3_2b_graph_plan.json, the decision-row plan of
diag_c158_a3_2b_graph.py (the read-only graph read of P5-2 step 1's ADOPTED file claudeDev\D1_ring_p5s02a_<stamp>.vi). COPIED from
tools/bench/diag_c155_a3_2_mkgraph.py (b9e4a567, card 155-a3-2, ran 4/0) with names changed (P5-1b -> P5-2a plan / scratch log / sum / json, base
plan diag_c155_a3_2_graph_plan.json, out prefix graph_ring_p5s02a), create count 1 -> 4 (c_deq, c_rel, c_tmo, c_case7), and the W gate read from
the scratch json (term_identity.new == the D gate's 'new (source, sink) pairs' are pair counts since PD386(b), so the old 'D new wires N' log text
no longer exists): deleted wires = term_identity.lost_w minus term_identity.new (the uids LabVIEW did not re-use).
PREDICTION: 4 creates, one STEPX line each in the last segment, 4 bound uids; new wires 21 (term_identity.new); deleted wires [24091, 24153];
adopted record md5 == sum final_md5 == 94ffff94.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c158_a3_2b_mkgraph.log -- py -u tools/bench/diag_c158_a3_2b_mkgraph.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c158_p5s02a_scratch.log"
OUTP = "diag_c158_a3_2b_graph_plan.json"
NCREATE = 4
plan, summ, scr, old = J("plan_ring_p5s02a.json"), J("diag_c158_p5s02a_scratch_sum.json"), J("diag_c158_p5s02a_scratch.json"), J("diag_c155_a3_2_graph_plan.json")
creates = dict((a["id"], a["class"]) for a in plan["actions"] if a.get("op") == "create")
alll = open(os.path.join(B, LOGN), encoding="utf-8", errors="replace").read().splitlines()
SEG0 = max(i for i, ln in enumerate(alll) if ln.startswith("BGRUN START"))
RX = re.compile(r"STEPX\s+\d+\s+create\s+acts \[\d+\] ids \['([^']+)'\] bound (\{[^}]*\})")
made, hits = {}, {}
for i, ln in enumerate(alll, 1):
    if i - 1 < SEG0:
        continue
    m = RX.search(ln)
    if m and m.group(1) in creates:
        b = ast.literal_eval(m.group(2))
        hits.setdefault(m.group(1), []).append(i)
        if b:
            made[str(b[max(b)])] = creates[m.group(1)]
G = {"pass": 0, "fail": 0, "first": None}


def gate(label, ok, d=""):
    G["pass" if ok else "fail"] += 1
    G["first"] = G["first"] or (None if ok else label)
    print("GATE {0} | {1} | {2}".format("PASS" if ok else "FAIL", label, str(d)[:900]), flush=True)


print("FACT last segment of {0} starts at line {1}; creates {2}".format(LOGN, SEG0 + 1, creates), flush=True)
gate("C {0} creates, one STEPX line each (last segment), {0} bound uids".format(len(creates)),
     len(creates) == NCREATE and all(len(hits.get(k, [])) == 1 for k in creates) and len(made) == len(creates), (hits, made))
ti = scr.get("term_identity") or {}
nw = sorted(set(int(w) for w in ti.get("new") or []))
dwires = sorted(set(int(w) for w in ti.get("lost_w") or []) - set(nw))
dl = [ln for ln in alll[SEG0:] if "  PASS  D new (source, sink) pairs" in ln]
gate("W term_identity.new 21 wires; the log's D gate PASSED on 21 new pairs", len(nw) == 21 and bool(dl) and "pairs 21 ==" in dl[-1],
     (len(nw), nw, dl[-1][:160] if dl else None))
gate("DW deleted wires (lost_w - new) == [24091, 24153]", dwires == [24091, 24153], dwires)
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
ADV, ADM = (rec.get("artefact") or {}).get("path"), (rec.get("artefact") or {}).get("md5")
gate("A last adopted record = claudeDev\\D1_ring_p5s02a_*, md5 == file == sum final_md5", summ.get("final") and ADV
     and os.path.basename(ADV).startswith("D1_ring_p5s02a_") and SX.md5(ADV) == ADM == summ.get("final_md5") == SX.md5(summ["final"]),
     (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 158-a3-2b (PD354(a), PD386(e)): FINALIZED decision-row plan of tools/bench/diag_c158_a3_2b_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P5-2 step 1's ADOPTED file (tools/bench/diag_c158_a3_2b_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c155_a3_2_graph.py -> tools/bench/graph_ring_p5s02a_<ts>.json. Written by tools/bench/diag_c158_a3_2b_mkgraph.py.")
out["input"] = {"vi": ADV, "md5": ADM, "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": [], "deleted_wires": dwires, "new_wires": nw,
                "cite": "plan_ring_p5s02a.json create actions (class per id) bound in tools/bench/{0}:{1}; new wires = term_identity.new of "
                        "tools/bench/diag_c158_p5s02a_scratch.json; deleted wires = term_identity.lost_w minus new".format(
                            LOGN, ",".join(str(hits[k][0]) for k in creates if k in hits))}
out["out_prefix"] = "graph_ring_p5s02a"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("P5-1", "P5-2a").replace("p5s01", "p5s02a")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}".format(json.dumps(made, sort_keys=True), nw, dwires), flush=True)
print("FACT plan json tools/bench/{0} md5 {1}".format(OUTP, SX.md5(os.path.join(B, OUTP))), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
