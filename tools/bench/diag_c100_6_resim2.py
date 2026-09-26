r"""diag_c100_6_resim2 - card 100-6, after the PARITY stop (stage_d1_disp.log) and its review
(archive/peer/2026-09-26-c100-6-parity.md, disposition written). Pure Python, no LabVIEW. Adds to
stageplan_disp_r4_open.json's `context` the two fields stagesim.base_state reads (stagesim.py:196-207):
loops = tools/bench/graph_loops_s1_20260924.json (md5 3e3d23ce = S1) and owners = tools/bench/sim/l2a1/graph_k_80_owners.json
(D1_k's map, a STAND-IN; diag_c100_6_parity.log V2 = 0 one-side-only entries on 639/686/7911). Nothing else changes.
Re-simulates and gates: R1 validates; R2 only `context` changed; R3 FINAL; R4 end cdiff rows == the 21 declared open_rows.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c100_6_resim2.log -- py -u tools/bench/diag_c100_6_resim2.py"""
import copy, json, os, sys                                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402

R4O = os.path.join(HERE, "sim", "disp", "stageplan_disp_r4_open.json")
LOOPS, OWN = "tools/bench/graph_loops_s1_20260924.json", "tools/bench/sim/l2a1/graph_k_80_owners.json"
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:500]), flush=True)


old = json.load(open(R4O, encoding="utf-8"))
new = copy.deepcopy(old)
new["context"] = dict(old.get("context") or {}, loops={"path": LOOPS}, owners={"path": OWN})
gate("R2 only `context` changed", [k for k in set(old) | set(new) if old.get(k) != new.get(k)] == ["context"], new["context"])
ok, why = protocol.validate_obj(new)
gate("R1 validates under the installed schema", ok, why)
if ok:
    json.dump(new, open(R4O, "w", encoding="utf-8"), indent=1)
    S = SS.simulate(R4O, os.path.join(ROOT, new["base"]["path"]), out_root=os.path.join(HERE, "sim"),
                    plan_out_dir=os.path.join(HERE, "sim", "disp"), log=lambda *_a: None)
    gate("R3 simulates FINAL", S["final"], (S["failed"], S["undecided"], S["first_divergent"]))
    want = sorted(set((int(r["node"]), r["term"]) for r in new["open_rows"]))
    got = sorted(set((int(k.split("|")[0]), k.split("|")[2]) for k in S["end_cdiff_rows"] or []))
    gate("R4 end cdiff rows == the {0} declared open_rows".format(len(want)), got == want,
         {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))})
po = os.path.join(HERE, "sim", "disp", "plan_disp.json")
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, po)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
