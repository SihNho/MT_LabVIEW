# ---
# labview: none
# hardware: none
# ---
r"""diag_c147_a1_4_mkgraph - card 147-a1-4 step 4 (OFFLINE): writes diag_c147_a1_4_graph_plan.json, the decision-row plan of diag_c147_a1_4_graph.py
(the read-only graph read of P4 session 6's ADOPTED file). COPIED from tools/bench/diag_c147_a1_1_mkgraph.py (md5 4c494fe3, card input) with the
s06 names; CHANGED: the create count is the plan's (not a typed 6) and deleted wires = the plan's delete_wire actions (s05 had none, s06 has 1).
Nothing typed: input vi/md5 from diag_c147_p4s06v18_scratch_sum.json (final/final_md5) == adopted_scratch.jsonl's last record; made uid -> class from
plan_ring_p4_s06v18.json create actions joined with the scratch log's STEPX create lines; new wires = the scratch json's term_identity.new (D gate).
PREDICTION: 2 creates, one STEPX line each, 2 bound uids; new wires == D gate count of the log; deleted wires [23807]; adopted record md5 == sum final_md5.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c147_a1_4_mkgraph.log -- py -u tools/bench/diag_c147_a1_4_mkgraph.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c147_p4s06v18_scratch.log"
OUTP = "diag_c147_a1_4_graph_plan.json"
plan, summ, scr, old = J("plan_ring_p4_s06v18.json"), J("diag_c147_p4s06v18_scratch_sum.json"), J("diag_c147_p4s06v18_scratch.json"), J("diag_c147_a1_1_graph_plan.json")
creates = dict((a["id"], a["class"]) for a in plan["actions"] if a.get("op") == "create")
dwires = sorted(int(a["wire_uid"]) for a in plan["actions"] if a.get("op") == "delete_wire")
lines = open(os.path.join(B, LOGN), encoding="utf-8", errors="replace").read().splitlines()
RX = re.compile(r"STEPX\s+\d+\s+create\s+acts \[\d+\] ids \['([^']+)'\] bound (\{[^}]*\})")
made, hits = {}, {}
for i, ln in enumerate(lines, 1):
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


gate("C {0} creates, one STEPX line each, {0} bound uids".format(len(creates)),
     len(creates) == 2 and all(len(hits.get(k, [])) == 1 for k in creates) and len(made) == len(creates), (hits, made))
ti = scr.get("term_identity") or {}
nw = sorted(int(w) for w in ti.get("new") or [])
dl = [ln for ln in lines if "  PASS  D new wires" in ln]
gate("W new wires from term_identity.new == the log's D gate count", dl and "D new wires {0} ==".format(len(nw)) in dl[-1], (nw, dl[-1:]))
gate("DW deleted wires from the plan's delete_wire actions == [23807]", dwires == [23807], dwires)
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
gate("A sum final under claudeDev, md5 == file == last adopted record", summ.get("final") and SX.md5(summ["final"]) == summ.get("final_md5")
     == (rec.get("artefact") or {}).get("md5"), (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 147-a1-4 (PD329(a), PD354(a)): FINALIZED decision-row plan of tools/bench/diag_c147_a1_4_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P4 session 6's ADOPTED file (tools/bench/diag_c147_a1_4_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c147_a1_1_graph.py -> tools/bench/graph_ring_p4s06_<ts>.json. Written by tools/bench/diag_c147_a1_4_mkgraph.py.")
out["input"] = {"vi": summ["final"], "md5": summ["final_md5"], "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": [], "deleted_wires": dwires, "new_wires": nw,
                "cite": "plan_ring_p4_s06v18.json create actions (class per id) bound in tools/bench/{0}:{1}; new wires = D gate (term_identity.new); "
                        "deleted wires = plan delete_wire actions".format(LOGN, ",".join(str(hits[k][0]) for k in creates if k in hits))}
out["out_prefix"] = "graph_ring_p4s06"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("session-5", "session-6").replace("p4s05", "p4s06")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}".format(json.dumps(made, sort_keys=True), nw, dwires), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
