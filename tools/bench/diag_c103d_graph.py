"""card 103-4 (no LabVIEW): the OFFLINE graph JSON for the Part-A file's md5, so stage_prerun's dry/pre-run of the PART-B mode
finds a terminal-list graph (find_graph by input md5). It is SIMULATED step 39 (after op 33) with every created uid replaced by its
Part-A real uid (stagexec.from_step_state) - the state Part A's A2 gate measured equal to the real read at op 33
(stage_d1_dispA_r2.log:652,658). Not a LabVIEW read; the note says so."""
import json, os, sys
T = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, T); os.chdir(T)
import stagexec as SX, protocol
PLAN, PARTA = os.path.join(T, "bench/sim/disp/plan_disp.json"), os.path.join(T, "bench/stage_d1_dispA.json")
pa = json.load(open(PARTA, encoding="utf-8"))["partA"]
st = SX.from_step_state(PLAN, pa["stop_after"], pa)
base = json.load(open("bench/par1359_95_graph.json", encoding="utf-8"))
out = {"vi": pa["file"], "md5": pa["md5"],
       "note": "SIMULATED (card 103-4): plan_disp.json step after op {0} bound through stage_d1_dispA.json partA.bind; "
               "Part A A2 measured real read == this step (stage_d1_dispA_r2.log:658). Offline stand-in for the dry/pre-run only.".format(pa["stop_after"]),
       "terminals": st["terminals"], "objs": st.get("objs") or [], "graph_summary": st.get("graph_summary") or base.get("graph_summary")}
p = "bench/sim/disp/graph_dispA_step{0}.json".format(pa["stop_after"])
json.dump(out, open(p, "w", encoding="utf-8"), indent=0)
neg = [r for r in st["terminals"] if min(r["owner_uid"], r["term_uid"]) < 0]
print("wrote", p, "terminals", len(st["terminals"]), "objs", len(out["objs"]), "negative owner/term rows", len(neg), "md5", SX.md5(p))
print(protocol.result_line(protocol.make_result(int(not neg), int(bool(neg)), None if not neg else "negative uids left")))
