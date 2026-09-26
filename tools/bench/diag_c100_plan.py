r"""diag_c100_plan - card 100-5 (PD213(c)(d)(b)): installed-schema check, PD213(d) classification of the display plan's
end computation_diff rows, and the finalized plan for stagexec dry / stage_prerun. Pure Python, no LabVIEW.

WHAT EXISTED FIRST: stagesim.simulate (unchanged), vigraph.key_parts/node_of, diag_c100_disp_sim.py (100-3's run of r2
under the in-process proposed schema). docs/protocol/stageplan.json was replaced by the proposed file BEFORE this run
(cp, card 100-5; old copy tools/bench/sim/disp/stageplan_schema_old_ab23c4c3.json). No classifier existed.

PREDICTION CONTRACT: P1 installed schema md5 == proposed b17f49dc. P2 every stageplan/1 JSON under tools/bench that
validated under the OLD schema validates under the installed one (widening only). P3 r3 validates and simulates with
failed None and the SAME 21 end rows as 100-3 (facts_c100_exec.json). P4 each row classified by PD213(d): 15 class 4
(open at base), 5 class 1 (#8764 y, #27716 index, #28180 half-width, #29009 left/right rank), 1 class 3 (#8323),
0 UNCLASSIFIED. P5 only if 0 UNCLASSIFIED: r3 + open_rows re-simulates FINAL (open_rows_match True).
"""
import glob, json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402
import vigraph as V       # noqa: E402

DISP = os.path.join(HERE, "sim", "disp")
OLD, PROP = os.path.join(DISP, "stageplan_schema_old_ab23c4c3.json"), os.path.join(DISP, "stageplan_schema_proposed.json")
INST = os.path.join(ROOT, "docs", "protocol", "stageplan.json")
R3, R3O = os.path.join(DISP, "stageplan_disp_r3.json"), os.path.join(DISP, "stageplan_disp_r3_open.json")
OUT = os.path.join(HERE, "facts_c100_plan.json")
SP = protocol.schema_path("stageplan/1")
gates, facts = [], {}


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)


def valid_under(schema_file, obj):
    protocol._SCHEMAS[SP] = json.load(open(schema_file, encoding="utf-8"))
    try:
        return protocol.validate_obj(obj)[0]
    finally:
        protocol._SCHEMAS.pop(SP, None)


gate("P1 installed schema == proposed", SS.md5_file(INST) == SS.md5_file(PROP), SS.md5_file(INST))
plans = {}
for p in glob.glob(os.path.join(HERE, "**", "*.json"), recursive=True):
    try:
        o = json.load(open(p, encoding="utf-8"))
    except Exception:            # noqa: BLE001 - not JSON / not ours
        continue
    if isinstance(o, dict) and o.get("schema") == "stageplan/1":
        plans[os.path.relpath(p, ROOT)] = (valid_under(OLD, o), valid_under(INST, o))
regress = [p for p, (a, b) in plans.items() if a and not b]
facts["earlier_plans"] = {"n": len(plans), "valid_old": sum(a for a, _b in plans.values()),
                          "valid_new": sum(b for _a, b in plans.values()), "regressed": regress,
                          "newly_valid": sorted(p for p, (a, b) in plans.items() if b and not a)}
gate("P2 every plan valid under the old schema still validates (widening only)", not regress and plans, facts["earlier_plans"])

plan = json.load(open(R3, encoding="utf-8"))
graph = os.path.join(ROOT, plan["base"]["path"])
gate("P3a r3 validates under the installed schema", protocol.validate_obj(plan)[0], protocol.validate_obj(plan)[1])
S = SS.simulate(R3, graph, out_root=os.path.join(HERE, "sim"), plan_out_dir=DISP, log=lambda *_a: None)
prev21 = json.load(open(os.path.join(HERE, "facts_c100_exec.json"), encoding="utf-8"))["end_cdiff_rows"]
gate("P3b r3 simulates (failed None), end rows == 100-3's 21", S["failed"] is None and S["end_cdiff_rows"] == prev21,
     (S["failed"], len(S["end_cdiff_rows"] or [])))
base_rows = set(S["steps"][0]["cdiff_rows"])
base_det = dict((d["sink"], d) for d in S["steps"][1]["cdiff_detail"])   # step 1 = the gate, no graph change
end_det = dict((d["sink"], d) for d in S["steps"][-1]["cdiff_detail"])
T = json.load(open(S["steps"][-1]["file"]["path"], encoding="utf-8"))["state"]["terminals"]
moved = set(n for a in plan["actions"] if a["op"] == "move_in" for n in a["nodes"])


def trace(r):
    """a sink row -> its ultimate source row, through plan-created tunnels (inner -> outer face)."""
    for _ in range(6):
        s = next((x for x in T if x["is_source"] and x["wire_uid"] and x["wire_uid"] == r["wire_uid"]), None)
        if s is None or not (s["owner_class"] == "LoopTunnel" and s["term_class"] == "InnerTerminal"):
            return s
        r = next((x for x in T if x["owner_uid"] == s["owner_uid"] and x["term_class"] == "OuterTerminal"), None)
        if r is None or not r["wire_uid"]:
            return None
    return None


table = []
for key in S["end_cdiff_rows"]:
    node, _c, term, _o = V.key_parts(key)
    d = end_det[key]
    row = {"key": key, "before": d["before"], "after": d["after"]}
    sinks = [x for x in T if V.node_of(x) == node and x["term_name"] == term and not x["is_source"]]
    src = trace(sinks[0]) if len(sinks) == 1 and sinks[0]["wire_uid"] else None
    row["src_now"] = src and {"owner_uid": src["owner_uid"], "owner_class": src["owner_class"], "term": src["term_name"]}
    b1 = V.key_parts(d["before"][0]) if len(d["before"]) == 1 else None
    if key in base_rows:
        row["cls"], row["same_as_base"] = 4, (base_det.get(key, {}).get("before"), base_det.get(key, {}).get("after")) == (d["before"], d["after"])
    elif node in moved and b1 and b1[1] == "ControlTerminal" and d["after"] == [] and src and src["owner_class"] == "Local" \
            and src["term_name"] == b1[2]:
        row["cls"] = 1
    elif (node, term) in ((8741, "array"), (11261, "element")) and src and src["owner_class"] == "Local" \
            and src["term_name"] in ("plot ring (display)", "plot WLC (display)"):
        row["cls"] = 2
    elif node == 8323 and d["before"] == ["11261|Terminal|appended array|0"] and d["after"] == [] and any(
            x["owner_class"] == "Local" and not x["is_source"] and x["term_name"] == term and x["wire_uid"] and
            any(y["is_source"] and y["wire_uid"] == x["wire_uid"] and y["owner_uid"] == 11261 for y in T) for x in T):
        row["cls"] = 3
    else:
        row["cls"] = "UNCLASSIFIED"
    table.append(row)
    print("  ROW {0:<48} class {1}  src_now {2}".format(repr(key), row["cls"], row["src_now"]), flush=True)
count = dict((c, sum(1 for r in table if r["cls"] == c)) for c in (1, 2, 3, 4, "UNCLASSIFIED"))
facts.update(classification=table, class_count=count, base_rows_changed=[r["key"] for r in table if r.get("same_as_base") is False])
gate("P4 every end row classified by PD213(d) (0 UNCLASSIFIED)", count["UNCLASSIFIED"] == 0, count)
if count["UNCLASSIFIED"] == 0:
    why = {1: "PD213(d)(1): source now a LOCAL READ of the same control", 3: "PD213(d)(3): #8323 written by the local WRITE",
           2: "PD213(d)(2): same data via L1/L2", 4: "PD213(d)(4): already open at the base"}
    op = dict(plan)
    op["open_rows"] = [{"node": V.key_parts(r["key"])[0], "term": V.key_parts(r["key"])[2], "why": why[r["cls"]]} for r in table]
    json.dump(op, open(R3O, "w", encoding="utf-8"), indent=1)
    S2 = SS.simulate(R3O, graph, out_root=os.path.join(HERE, "sim"), plan_out_dir=DISP, log=lambda *_a: None)
    facts["final_plan"] = {"plan_out": S2["plan_out"], "final": S2["final"], "end_rows": len(S2["end_cdiff_rows"] or [])}
    gate("P5 r3 + open_rows simulates FINAL", S2["final"], (S2["failed"], S2["undecided"], S2["first_divergent"]))
json.dump(facts, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
n_pass = sum(1 for _l, ok in gates if ok)
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(gates) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first,
                                                [{"path": os.path.relpath(OUT, ROOT), "md5": SS.md5_file(OUT)}])))
