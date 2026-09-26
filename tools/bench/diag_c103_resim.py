r"""diag_c103_resim - card 103-1 P4. Pure Python, no LabVIEW. PRIOR ART: diag_c101c_resim.py (same shape: hold the OLD finalized
plan + step files in memory, re-simulate stageplan_disp_r4_open.json with stagesim, compare step by step by content).
The ONLY plan change: row r7_wait `donor_uid 44143` (stagekit.copy_in, MOVE_DST-only, r7 stop) -> `prim "Wait (ms)"`
(gscript.create_primitive_nested, donor claudeDev\OpWaitDonor_v0.vi registered by diag_c103_wait_donor2.log).
PREDICTION: R3 FINAL, no failed/undecided row; R4 end cdiff == the SAME 21 open_rows; R5 steps 0..(op 41's first act - 1) are
CONTENT-IDENTICAL to the old plan (Part A = r7's ops 1-40 unchanged); R6 op 41 compiles to route `primitive` for r7_wait and
the Wait donor is registered; R7 the new node after op 41 is class Function with exactly the plan's two terminals.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c103_resim.log -- py -u tools/bench/diag_c103_resim.py"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402
import stagexec as SX     # noqa: E402

R4O = os.path.join(HERE, "sim", "disp", "stageplan_disp_r4_open.json")
PO = os.path.join(HERE, "sim", "disp", "plan_disp.json")
LAB = os.path.join(HERE, "facts_c100_oplabels.json")
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
KEYS = ("only_sim_terms", "only_real_terms", "only_sim_edges", "only_real_edges", "dangling_sim_only", "dangling_real_only")
gates = []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def same(a, b):
    d = SX.compare(a, b, {"obj": {}, "term": {}, "diag": {}})
    return not any(d[k] for k in KEYS), dict((k, d[k][:6]) for k in KEYS if d[k])


OLD = J(PO)
old_md5 = SS.md5_file(PO)
old_st = [J(f["path"]) for f in OLD["finalized"]["step_files"]]
old_ops = SX.compile_plan(OLD)
r4o = J(R4O)
row = next(a for a in r4o["actions"] if a.get("id") == "r7_wait")
gate("R0 plan input: r7_wait carries prim 'Wait (ms)' and no donor_uid", row.get("prim") == "Wait (ms)" and "donor_uid" not in row, row)
S = SS.simulate(R4O, os.path.join(ROOT, r4o["base"]["path"]), out_root=os.path.join(HERE, "sim"),
                plan_out_dir=os.path.join(HERE, "sim", "disp"), log=lambda *_a: None)
gate("R3 re-simulation FINAL, 0 failed, 0 undecided", S["final"] and not S["failed"] and not S["undecided"],
     (S["failed"], S["undecided"], S["first_divergent"]))
NEW = J(PO)
want = sorted(set((int(r["node"]), r["term"]) for r in NEW["open_rows"]))
got = sorted(set((int(k.split("|")[0]), k.split("|")[2]) for k in S["end_cdiff_rows"] or []))
old_open = sorted(set((int(r["node"]), r["term"]) for r in OLD["open_rows"]))
gate("R4 end cdiff rows == the {0} declared open_rows, the SAME set as the old plan's".format(len(want)),
     got == want and want == old_open and len(want) == 21, {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got)),
                                                           "vs_old": sorted(set(want) ^ set(old_open))})
new_st = [J(f["path"]) for f in NEW["finalized"]["step_files"]]
ops = SX.compile_plan(NEW)
kw = next(k for k, o in enumerate(ops, 1) if NEW["actions"][o["acts"][0] - 1].get("id") == "r7_wait")
first = ops[kw - 1]["acts"][0]
diffs = [(k, same(old_st[k]["state"]["terminals"], new_st[k]["state"]["terminals"])[1]) for k in range(0, first)]
bad = [(k, d) for k, d in diffs if d]
gate("R5 steps 0..{0} (every act before op {1}, r7_wait) CONTENT-IDENTICAL to the old plan (Part A unchanged); ops 1..{2} same kinds".format(
    first - 1, kw, kw - 1), not bad and [o["kind"] for o in ops[:kw - 1]] == [o["kind"] for o in old_ops[:kw - 1]] and len(new_st) == len(old_st),
     bad[:3])
gate("R6 op {0} = r7_wait compiles to route `primitive`; Wait (ms) donor registered in facts_c100_oplabels.json".format(kw),
     ops[kw - 1].get("route") == "primitive" and "Wait (ms)" in J(LAB)["OpPrimCopyNested_v0"]["donors"], (kw, ops[kw - 1]))
st_w = new_st[first]["state"]
wu = st_w["sym"].get("WAIT1", st_w["sym"].get("new:WAIT1"))
trm = sorted((r["term_name"], bool(r["is_source"])) for r in st_w["terminals"] if r["owner_uid"] == wu)
gate("R7 WAIT1 (#{0}) after act {1}: class Function, terminals == plan".format(wu, first),
     SS.obj_class(st_w, wu) == "Function" and trm == sorted((t["name"], t["is_source"]) for t in row["terminals"]), (SS.obj_class(st_w, wu), trm))
print("  FACT r7_wait = op {0} of {1} (first act {2}); old plan md5 {3} -> new {4}".format(kw, len(ops), first, old_md5, SS.md5_file(PO)), flush=True)
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, PO)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
