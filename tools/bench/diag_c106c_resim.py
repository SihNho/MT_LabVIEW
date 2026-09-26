r"""diag_c106c_resim - card 106-3 T1: re-simulate the EXECUTED display plan tools/bench/sim/disp/plan_disp.json with the
card-106-3 stagesim (finalize cdiff graph = the E3 inputs: node_labels_default + the S1 wiki fs pairs, stagesim.cdiff_inputs;
classed open-row rule, stagesim.open_rows_classed). OFFLINE, no LabVIEW, nothing in tools/bench/sim/disp is written: the
step files go to %TEMP%\c106c_resim, a compact summary to tools/bench/sim/c106c_resim_summary.json.
PRIOR ART: diag_c103_resim.py / diag_c104c_e3rows.py (same simulate call; the 104-3 E3 row census). No new op.
PREDICTION CONTRACT:
  R1 the simulation reaches the last action with no failed step
  R2 end cdiff rows (node, term) == the plan's PD213(d) class 1-3 open rows (6 rows, read from each row's `why`)
  R3 final True through the classed rule; the legacy all-21-rows rule is False; class-4 sources == S1 for all 15 rows
  R4 every re-simulated step STATE == the pinned step file's state (the ops are untouched; only the finalize graph changed)
  R5 plan_disp.json and its pinned step files are byte-unchanged (md5 before == after == the pins)
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c106c_resim.log -- py -u tools/bench/diag_c106c_resim.py"""
import json
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS          # noqa: E402
import stagexec as SX          # noqa: E402
import protocol                # noqa: E402

PLAN = os.path.join(ROOT, "tools", "bench", "sim", "disp", "plan_disp.json")
OUT = os.path.join(ROOT, "tools", "bench", "sim", "c106c_resim_summary.json")
J = lambda p: json.load(open(p, encoding="utf-8"))   # noqa: E731
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:600]), flush=True)


print(__doc__, flush=True)
P = J(PLAN)
pins = [(f["path"], f["md5"]) for f in P["finalized"]["step_files"]]
md5_plan0 = SS.md5_file(PLAN)
pin_ok0 = all(SS.md5_file(SS._abs(p)) == m for p, m in pins)
tmp = os.path.join(tempfile.gettempdir(), "c106c_resim")
os.makedirs(tmp, exist_ok=True)
S = SS.simulate(PLAN, SS._abs(P["finalized"]["base"]["path"]), out_root=tmp, plan_out_dir=tmp, log=lambda *_a: None)
end = sorted(set((SS.V.key_parts(k)[0], SS.V.key_parts(k)[2]) for k in (S["end_cdiff_rows"] or [])))
cls = [(int(r["node"]), r["term"], SS.open_row_class(r)) for r in P["open_rows"]]
want = sorted(set((n, t) for n, t, c in cls if c in (1, 2, 3)))
print("  FACT  cdiff_inputs {0}".format(S["cdiff_inputs"]), flush=True)
print("  FACT  step-0 (unedited S1 base) cdiff rows: {0} (the 104-3 finalize read 15 class-4 rows at step 0)".format(
    len(S["steps"][0]["cdiff_rows"] or [])), flush=True)
print("  FACT  end rows {0}".format(end), flush=True)
gate("R1 simulation reached the last action ({0}) with no failed step".format(len(P["actions"])),
     S["failed"] is None and S["steps"][-1]["n"] == len(P["actions"]), S["failed"])
gate("R2 end cdiff rows == the plan's class 1-3 open rows ({0} of {1})".format(len(want), len(cls)), end == want,
     {"extra": sorted(set(end) - set(want)), "missing": sorted(set(want) - set(end))})
oc = S["open_rows_classed"]
gate("R3 final via the classed rule (legacy all-rows rule False; class-4 sources == S1 {0}/{1} rows, {2} keys)".format(
    oc["c4_n"] - len(set(b["row"] for b in oc["c4_bad"])), oc["c4_n"], oc["c4_keys"]),
     S["final"] and oc["ok"] and not S["open_rows_match_legacy"] and not oc["c4_bad"], oc)
diff_steps = []
for s, (p, _m) in zip(S["steps"], pins):
    a, b = J(s["file"]["path"])["state"], J(SS._abs(p))["state"]
    if a != b:
        diff_steps.append((s["n"], sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))))
gate("R4 every re-simulated step state == its pinned step file state ({0} steps)".format(len(pins)), not diff_steps and
     len(S["steps"]) == len(pins), diff_steps[:6])
gate("R5 plan_disp.json + its {0} pinned step files byte-unchanged".format(len(pins)),
     SS.md5_file(PLAN) == md5_plan0 == "c7d80fc93279f4ea5efd21c068e7efa6" and pin_ok0 and
     all(SS.md5_file(SS._abs(p)) == m for p, m in pins), md5_plan0)
old = P["finalized"]
rec = {"card": "106-3", "plan": {"path": "tools/bench/sim/disp/plan_disp.json", "md5": md5_plan0},
       "cdiff_inputs": S["cdiff_inputs"], "end_rows": end, "want_class_1_3": want,
       "old_finalize_rows_n": len(old.get("end_cdiff_rows") or []), "new_finalize_rows_n": len(end),
       "step0_rows_n": len(S["steps"][0]["cdiff_rows"] or []), "final": S["final"],
       "open_rows_match_legacy": S["open_rows_match_legacy"], "open_rows_classed": oc,
       "rows_per_step": [(s["n"], len(s.get("cdiff_rows") or [])) for s in S["steps"]],
       "step_state_diffs": diff_steps, "resim_plan_out_tmp": S["plan_out"],
       "note": "step files in %TEMP%\\c106c_resim, not kept in the project"}
with open(OUT, "w", encoding="utf-8") as f:
    json.dump(rec, f, indent=1, default=str)
_ = SX  # imported to prove stagexec's open_row_class delegation loads (SX.open_row_class is SS.open_row_class)
print("  FACT  stagexec.open_row_class is stagesim.open_row_class: {0}".format(SX.open_row_class is SS.open_row_class))
n_pass = sum(1 for _l, ok in gates if ok)
first = next((l for l, ok in gates if not ok), None)
print("=== GATES: {0} pass / {1} fail{2}".format(n_pass, len(gates) - n_pass, "; failing: " + first if first else ""))
print(protocol.result_line(protocol.make_result(n_pass, len(gates) - n_pass, first,
                                                artefacts=[{"path": "tools/bench/sim/c106c_resim_summary.json",
                                                            "md5": SS.md5_file(OUT)}])))
sys.exit(0 if first is None else 1)
