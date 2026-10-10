# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c165_p5s02e_scratch.log:148
# ---
r"""diag_c165_a3_4_mkgraph - card 165-3-4 (OFFLINE, no LabVIEW opened): writes diag_c165_a3_4_graph_plan.json, the decision-row plan of
diag_c165_a3_4_graph.py (the read-only graph read of P5-2 step 5's ADOPTED file claudeDev\D1_ring_p5_<stamp>.vi). COPY of
diag_c164_a3_5_mkgraph.py (card 164-3-5, ran 4/0 on run 2); changed lines ONLY: names p5s02d -> p5s02e (scratch log = recipe LOG constant c165 / sum / json,
base plan diag_c164_a3_5_graph_plan.json, base graph graph_ring_p5s02d_20261010_154830.json, out prefix graph_ring_p5s02e, sim end
sim/ring_p5s02e/step_13_wire.json), adopted record prefix D1_ring_p5_ (PD400(c)), deleted_nodes = [] (the plan has no delete_object row),
and the gate predictions: step 5 binds 5 symbols (STEPX 03 -1/-2, 04 -7, 06 -10, 07 -16) whose sim classes must equal the CENSUS-ALL owner
classes of the scratch (log :148: LeftShiftRegister 1, RightShiftRegister 1, DigitalNumericConstant 1, SelectorTunnel 2); term_identity.new minus
base wires == 5 (CENSUS-ALL Wire 5), new ∩ base ⊆ lost_w; D gate pairs 10; deleted wires (lost_w - new) == {10362, 25232} (the two stubs).
    py tools/bgrun.py --material --max-min 2 --log tools/bench/diag_c165_a3_4_mkgraph.log -- py -u tools/bench/diag_c165_a3_4_mkgraph.py"""
import ast, collections, json, os, re, sys                                                  # noqa: E401
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "tools"))
from tools import protocol  # noqa: E402
import stagexec as SX                                                                       # noqa: E402
B = os.path.join(ROOT, "tools", "bench")
J = lambda p: json.load(open(os.path.join(B, p), encoding="utf-8"))                          # noqa: E731
LOGN = "diag_c165_p5s02e_scratch.log"
OUTP = "diag_c165_a3_4_graph_plan.json"
summ, scr, old = J("diag_c165_p5s02e_scratch_sum.json"), J("diag_c165_p5s02e_scratch.json"), J("diag_c164_a3_5_graph_plan.json")
simend = J(os.path.join("sim", "ring_p5s02e", "step_13_wire.json"))
WANT = {"RightShiftRegister": 1, "LeftShiftRegister": 1, "DigitalNumericConstant": 1, "SelectorTunnel": 2}
DELN = []


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


print("FACT last segment of {0} starts at line {1}; bound {2}; sim classes {3}".format(LOGN, SEG0 + 1, hits, dict((k, sorted(v)) for k, v in SIMC.items()
      if k in hits)), flush=True)
gate("C 5 bound symbols, one STEPX line each (last segment); sim classes == CENSUS-ALL owner classes {0}".format(WANT),
     len(hits) == 5 and all(len(v) == 1 for v in hits.values()) and len(made) == 5 and dict(collections.Counter(made.values())) == WANT, (hits, made))
ti = scr.get("term_identity") or {}
nw = sorted(set(int(w) for w in ti.get("new") or []))
dwires = sorted(set(int(w) for w in ti.get("lost_w") or []) - set(nw))
dl = [ln for ln in alll[SEG0:] if "  PASS  D new (source, sink) pairs" in ln]
BASEW = set(int(r["wire_uid"]) for r in J("graph_ring_p5s02d_20261010_154830.json")["terminals"] if r.get("wire_uid"))
NN, OO = sorted(set(nw) - BASEW), sorted(set(nw) & BASEW)
lw = set(int(w) for w in ti.get("lost_w") or [])
gate("W D gate PASSED on 10 new pairs; term_identity.new minus base wires == 5 (CENSUS-ALL Wire 5); new ∩ base wires ⊆ lost_w",
     len(NN) == 5 and set(OO) <= lw and bool(dl) and "pairs 10 ==" in dl[-1], {"new_not_in_base": NN, "re_ended_old": OO, "d": dl[-1][:120] if dl else None})
gate("DW deleted wires (lost_w - new) == [10362, 25232]", dwires == [10362, 25232], dwires)
rec = [json.loads(x) for x in open(SX.ADOPT_LOG, encoding="utf-8") if x.strip()][-1]
ADV, ADM = (rec.get("artefact") or {}).get("path"), (rec.get("artefact") or {}).get("md5")
gate("A last adopted record = claudeDev\\D1_ring_p5_*, md5 == file == sum final_md5", summ.get("final") and ADV
     and os.path.basename(ADV).startswith("D1_ring_p5_") and SX.md5(ADV) == ADM == summ.get("final_md5") == SX.md5(summ["final"]),
     (summ.get("final"), summ.get("final_md5"), rec.get("artefact")))
out = dict(old)
out["schema_note"] = ("card 165-3-4 (PD354(a), PD396(e), PD400(c)): FINALIZED decision-row plan of tools/bench/diag_c165_a3_4_graph.py. READ-ONLY: one "
                      "never-saved byte copy of P5-2 step 5's ADOPTED file (tools/bench/diag_c165_a3_4_adopt.log), fresh LabVIEW, graph read exactly as "
                      "diag_c164_a3_5_graph.py -> tools/bench/graph_ring_p5s02e_<ts>.json. Written by tools/bench/diag_c165_a3_4_mkgraph.py.")
out["input"] = {"vi": ADV, "md5": ADM, "same_rows_as": None}
out["edits"] = {"made": made, "deleted_nodes": DELN, "deleted_wires": dwires, "new_wires": nw,
                "cite": "STEPX bound symbols in tools/bench/{0}:{1}, classes from tools/bench/sim/ring_p5s02e/step_13_wire.json; deleted nodes = "
                        "none (no delete_object row in plan_ring_p5s02e.json); new wires = term_identity.new of tools/bench/diag_c165_p5s02e_scratch.json; "
                        "deleted wires = term_identity.lost_w minus new".format(LOGN, ",".join(sorted(set(str(v[0]) for v in hits.values()), key=int)))}
out["out_prefix"] = "graph_ring_p5s02e"
out["decisions"] = [dict(d, what=re.sub(r"\d+ new wires", "{0} new wires".format(len(nw)), re.sub(r"\d+ made", "{0} made".format(len(made)),
                         d["what"].replace("P5-2d", "P5-2e").replace("p5s02d", "p5s02e")))) for d in old["decisions"]]
json.dump(out, open(os.path.join(B, OUTP), "w", encoding="utf-8"), indent=1)
print("FACT made {0}; new wires {1}; deleted wires {2}; deleted nodes {3}".format(json.dumps(made, sort_keys=True), nw, dwires, DELN), flush=True)
print("FACT plan json tools/bench/{0} md5 {1}".format(OUTP, SX.md5(os.path.join(B, OUTP))), flush=True)
print(protocol.result_line(protocol.make_result(G["pass"], G["fail"], G["first"],
                                                [{"path": "tools/bench/" + OUTP, "md5": SX.md5(os.path.join(B, OUTP))}])), flush=True)
sys.exit(1 if G["fail"] else 0)
