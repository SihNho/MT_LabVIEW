# ---
# labview: none
# hardware: none
# ---
r"""diag_c152_b3_1_mkgraph - card 152-b3-1 (OFFLINE): writes diag_c152_b3_1_graph_plan.json, the decision-row plan of
diag_c152_b3_1_graph.py (the read-only graph read of P4 session 9's ADOPTED file). COPIED from tools/bench/diag_c151_a1_1_mkgraph.py (0e6517f3,
card 151-a3-1, ran 4/0) with names changed (s08 -> s09 plan / scratch log / sum / json, base plan diag_c151_a1_1_graph_plan.json) and the s08 constants
replaced by the s09 plan's own values: create count (3 -> 0; s09 creates no object) and plan delete_wire uids ([25415, 25645] -> [], read from
plan_ring_p4_s09v18.json 9d622c95: 3 wire + 3 wire_remove_loose_ends actions). Changed lines: 5-13, 22-25, 66-68, 72, 74-76.
The scratch log's STEPX / D-gate search is restricted to the LAST segment (from the last 'BGRUN START').
PREDICTION: 0 creates, 0 bound uids; new wires (term_identity.new + kept_by_key) == the D gate count;
plan delete_wire actions == [] == deleted_wires; adopted record md5 == sum final_md5.
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c152_b3_1_mkgraph.log -- py -u tools/bench/diag_c152_b3_1_mkgraph.py"""
import ast, json, os, re, sys                                                               # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c152_p4s09v18_scratch.log"
OUTP = "diag_c152_b3_1_graph_plan.json"
NCREATE, DWIRES = 0, []
plan, summ, scr, old = J("plan_ring_p4_s09v18.json"), J("diag_c152_p4s09v18_scratch_sum.json"), J("diag_c152_p4s09v18_scratch.json"), J("diag_c151_a1_1_graph_plan.json")
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
     len(creates) == NCREATE and all(len(hits.get(k, [])) == 1 for k in creates) and len(made) == len(creates), (hits, made))
ti = scr.get("term_identity") or {}
kept = sorted(int(n["wire"]) for n in ti.get("reuse_noted") or [] if n.get("kept_by_key"))   # the data fix: re-used uids
nw = sorted(set(int(w) for w in ti.get("new") or []) | set(kept))
dwires = [w for w in pdwires if w not in kept]
dl = [ln for ln in alll[SEG0:] if "  PASS  D new wires" in ln]
gate("W new wires (term_identity.new + kept_by_key re-used {0}) == the log's D gate count".format(kept),
     bool(dl) and "D new wires {0} ==".format(len(nw)) in dl[-1], (len(nw), nw, dl[-1][:160] if dl else None))
gate("DW plan delete_wire actions == {0} == deleted_wires (no kept_by_key uid)".format(DWIRES),
     pdwires == DWIRES and dwires == pdwires, (pdwires, dwires))
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
gate("A sum final under claudeDev, md5 == file == last adopted record", summ.get("final") and SX.md5(summ["final"]) == summ.get("final_md5")
     == (rec.get("artefact") or {}).get("md5"), (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 152-b3-1 (PD329(a), PD354(a), PD368(e)): FINALIZED decision-row plan of tools/bench/diag_c152_b3_1_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P4 session 9's ADOPTED file (tools/bench/diag_c152_b3_1_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c151_a1_1_graph.py -> tools/bench/graph_ring_p4s09_<ts>.json. Written by tools/bench/diag_c152_b3_1_mkgraph.py.")
out["input"] = {"vi": summ["final"], "md5": summ["final_md5"], "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": [], "deleted_wires": dwires, "new_wires": nw,
                "cite": "plan_ring_p4_s09v18.json create actions (class per id) bound in tools/bench/{0}:{1}; new wires = term_identity.new + "
                        "kept_by_key re-used uids {2}; deleted wires = plan delete_wire "
                        "actions {3} minus the re-used uids".format(LOGN, ",".join(str(hits[k][0]) for k in creates if k in hits), kept, pdwires)}
out["out_prefix"] = "graph_ring_p4s09"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("session-8", "session-9").replace("p4s08", "p4s09")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}; kept_by_key {3}".format(json.dumps(made, sort_keys=True), nw, dwires, kept), flush=True)
print("FACT plan json tools/bench/{0} md5 {1}".format(OUTP, SX.md5(os.path.join(B, OUTP))), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
