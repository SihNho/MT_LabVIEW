# ---
# labview: none
# hardware: none
# ---
r"""diag_c150_a3_2_mkgraph - card 150-a3-2 (OFFLINE): writes diag_c150_a3_2_graph_plan.json, the decision-row plan of diag_c150_a3_2_graph.py
(the read-only graph read of P4 session 7's ADOPTED file). COPIED from tools/bench/diag_c149_a3_2_mkgraph.py (card 149-a3-2, ran 4/0) with names
changed (s06 -> s07 plan / scratch log / sum / json, base plan diag_c149_a3_2_graph_plan.json) and the s06 constants replaced by the s07 plan's own
values: create count (2 -> len(plan create actions) = 5) and plan delete_wire uids ([23807] -> the plan's delete_wire uids). The kept_by_key
data fix is kept unchanged (s07's term_identity.reuse_noted is [] in diag_c150_p4s07v18_scratch.json, so it moves nothing).
The scratch log's STEPX / D-gate search is restricted to the LAST segment (from the last 'BGRUN START').
PREDICTION: 5 creates, one STEPX line each, 5 bound uids; new wires (8 term_identity.new + 0 kept_by_key) == 8 == D gate count;
plan delete_wire actions == [25283, 25348, 25386, 25638] == deleted_wires; adopted record md5 == sum final_md5.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c150_a3_2_mkgraph.log -- py -u tools/bench/diag_c150_a3_2_mkgraph.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c150_p4s07v18_scratch.log"
OUTP = "diag_c150_a3_2_graph_plan.json"
plan, summ, scr, old = J("plan_ring_p4_s07v18.json"), J("diag_c150_p4s07v18_scratch_sum.json"), J("diag_c150_p4s07v18_scratch.json"), J("diag_c149_a3_2_graph_plan.json")
creates = dict((a["id"], a["class"]) for a in plan["actions"] if a.get("op") == "create")
pdwires = sorted(int(a["wire_uid"]) for a in plan["actions"] if a.get("op") == "delete_wire")
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


print("FACT last segment of {0} starts at line {1}".format(LOGN, SEG0 + 1), flush=True)
gate("C {0} creates, one STEPX line each (last segment), {0} bound uids".format(len(creates)),
     len(creates) == 5 and all(len(hits.get(k, [])) == 1 for k in creates) and len(made) == len(creates), (hits, made))
ti = scr.get("term_identity") or {}
kept = sorted(int(n["wire"]) for n in ti.get("reuse_noted") or [] if n.get("kept_by_key"))   # the data fix: re-used uids
nw = sorted(set(int(w) for w in ti.get("new") or []) | set(kept))
dwires = [w for w in pdwires if w not in kept]
dl = [ln for ln in alll[SEG0:] if "  PASS  D new wires" in ln]
gate("W new wires (term_identity.new + kept_by_key re-used {0}) == the log's D gate count".format(kept),
     bool(dl) and "D new wires {0} ==".format(len(nw)) in dl[-1], (len(nw), nw, dl[-1][:160] if dl else None))
gate("DW plan delete_wire actions == [25283, 25348, 25386, 25638] == deleted_wires (no kept_by_key uid)",
     pdwires == [25283, 25348, 25386, 25638] and dwires == pdwires, (pdwires, dwires))
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
gate("A sum final under claudeDev, md5 == file == last adopted record", summ.get("final") and SX.md5(summ["final"]) == summ.get("final_md5")
     == (rec.get("artefact") or {}).get("md5"), (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 150-a3-2 (PD329(a), PD354(a), PD366): FINALIZED decision-row plan of tools/bench/diag_c150_a3_2_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P4 session 7's ADOPTED file (tools/bench/diag_c150_a3_2_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c149_a3_2_graph.py -> tools/bench/graph_ring_p4s07_<ts>.json. Written by tools/bench/diag_c150_a3_2_mkgraph.py.")
out["input"] = {"vi": summ["final"], "md5": summ["final_md5"], "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": [], "deleted_wires": dwires, "new_wires": nw,
                "cite": "plan_ring_p4_s07v18.json create actions (class per id) bound in tools/bench/{0}:{1}; new wires = term_identity.new + "
                        "kept_by_key re-used uids {2} (stagekit.py:1513 d_new); deleted wires = plan delete_wire "
                        "actions {3} minus the re-used uids".format(LOGN, ",".join(str(hits[k][0]) for k in creates if k in hits), kept, pdwires)}
out["out_prefix"] = "graph_ring_p4s07"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("session-6", "session-7").replace("p4s06", "p4s07")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}; kept_by_key {3}".format(json.dumps(made, sort_keys=True), nw, dwires, kept), flush=True)
print("FACT plan json tools/bench/{0} md5 {1}".format(OUTP, SX.md5(os.path.join(B, OUTP))), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
