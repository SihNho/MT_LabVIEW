r"""diag_c100_disp_sim - card 100-3: simulate the REVISED display-loop plan (tools/bench/sim/disp/stageplan_disp_r2.json)
under the PROPOSED stageplan schema amendment (tools/bench/sim/disp/stageplan_schema_proposed.json), in-process only.

WHAT EXISTED FIRST: tools/stagesim.simulate (used unchanged); the installed docs/protocol/stageplan.json refuses symbolic
diagram fields, and card 100-3 may not write docs/protocol, so the swap is IN THIS PROCESS ONLY - stagexec prerun/run in
any other process read the installed schema and stay closed. Pure Python; imports no stagexec/stagekit/gscript.

PREDICTION CONTRACT: P1 the plan validates under the installed schema: False (symbolic diagram fields). P2 under the
proposed schema: True. P3 the simulation applies every action (failed None). P4 final False (the display rows change
where #8741/#8764/#27716/#28180/#29009/#11261 get their inputs: locals instead of wires, so computation_diff rows > 0).
Output: plan_disp.json + step files under tools/bench/sim/disp, facts in tools/bench/facts_c100_exec.json.
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol          # noqa: E402
import stagesim as SS    # noqa: E402

PLAN = os.path.join(ROOT, "tools", "bench", "sim", "disp", "stageplan_disp_r2.json")
PROP = os.path.join(ROOT, "tools", "bench", "sim", "disp", "stageplan_schema_proposed.json")
OUT = os.path.join(ROOT, "tools", "bench", "facts_c100_exec.json")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:400]), flush=True)


plan = json.load(open(PLAN, encoding="utf-8"))
v1 = protocol.validate_obj(plan)
gate("P1 installed schema refuses the revised plan (symbolic diagram fields)", not v1[0], v1[1])
protocol._SCHEMAS[protocol.schema_path("stageplan/1")] = json.load(open(PROP, encoding="utf-8"))
v2 = protocol.validate_obj(plan)
gate("P2 the PROPOSED schema accepts it", v2[0], v2[1])
graph = os.path.join(ROOT, plan["base"]["path"])
S = SS.simulate(PLAN, graph, out_root=os.path.join(ROOT, "tools", "bench", "sim"),
                plan_out_dir=os.path.join(ROOT, "tools", "bench", "sim", "disp"), log=print)
gate("P3 every action applied (failed None)", S["failed"] is None, S["failed"])
gate("P4 not final: end computation_diff rows > 0 (display inputs now come from locals)", not S["final"],
     (S["final"], len(S["end_cdiff_rows"] or [])))
rows = S["end_cdiff_rows"] or []
facts = {"schema_installed": v1, "schema_proposed": v2, "failed": S["failed"], "final": S["final"],
         "end_cdiff_rows": rows, "first_divergent": S["first_divergent"], "n_candidates": S["n_candidates"],
         "plan_out": S["plan_out"], "sym": S["sym"], "steps": len(S["steps"])}
json.dump(facts, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
print("END_CDIFF_ROWS", len(rows), rows[:40])
print("FIRST_DIVERGENT", S["first_divergent"])
n_pass = sum(1 for _l, ok in gates if ok)
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail".format(n_pass, len(gates) - n_pass))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first,
                                                [{"path": os.path.relpath(OUT, ROOT), "md5": SS.md5_file(OUT)}])))
