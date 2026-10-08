# ---
# labview: none
# hardware: none
# evidence: tools/bench/cards/brief_153-b1-1.md
# ---
r"""selftest_c153_collect_all - card 153-b1-1 (docs/d1/ring-p4d.md PD370(c)): stagesim's COLLECT-ALL replay. OFFLINE (no COM);
every simulate() writes into a temp dir only (out_root + plan_out_dir), never under tools/bench.
FIXTURES: plan_ring_p4_s09v18.json (9d622c95, 6 actions = v18 ops 185..190, finalized step files md5-pinned in the plan) on the s08
END graph graph_ring_p4s08_20261009_033522.json (44858dbf, NO fs_owner_read: FS #29721 UNMEASURED) and a TEMP COPY of
fs_tunnel_naming_table.json (769ae8d0) WITHOUT row '152-b1-2 X' (the only src_looptunnel row). The real table is never written.
EXISTING checked first: selftest_c152_fsowner.py (R10 = the owner refusal text), diag_c153_b1_1_default_before.json (today's default
refusal, recorded with the unedited stagesim 128bacfb).
PREDICTION: C1 default mode (real table) fails at step 1 (op 185 p4_x_n2_order) with the text recorded before the edit; C2 default
mode + temp table: same; C3 collect-all + temp table: verdict PROVISIONAL, final False, failed set, refusals listed at steps 1 AND 3 -
step 1 the FS #29721 owner text, step 3 (op 187 p4_x_slot_fs) 'UNMEASURED tunnel naming' on a LoopTunnel 'min slot'; each refusal
carries the plan's prediction (md5 == plan.finalized.step_files); C4 collect-all + real table: only step 1 (op 187's LoopTunnel rule is
measured); C5 collect-all on the fsowner-derived graph (e26b4d90): 0 refusals and STILL verdict PROVISIONAL / final False; C6 no
plan_<stage>.json written anywhere by a collect-all run, the plan / real table / recorded sim step files unchanged; C7 the module
override CROSS_LT_FROM_TABLE is back to None after every run."""
import copy, glob, hashlib, json, os, sys, tempfile                                          # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagesim as SS, protocol as P                                                         # noqa: E401,E402
res = []


def gate(label, ok, detail=""):
    res.append(bool(ok))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:700]), flush=True)


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


PLAN = os.path.join(HERE, "plan_ring_p4_s09v18.json")
G08 = os.path.join(HERE, "graph_ring_p4s08_20261009_033522.json")
GFO = os.path.join(HERE, "graph_ring_p4s08_20261009_033522_fsowner.json")
TAB = os.path.join(HERE, "fs_tunnel_naming_table.json")
SIMD = os.path.join(HERE, "sim", "ring_p4_s09v18")
watch = [PLAN, G08, GFO, TAB] + sorted(p for p in glob.glob(os.path.join(SIMD, "*")) if os.path.isfile(p))
before = dict((p, md5(p)) for p in watch)
print("  FACT  stagesim {0}; table {1}; plan {2}".format(md5(os.path.join(ROOT, "tools", "stagesim.py"))[:8], before[TAB][:8],
                                                         before[PLAN][:8]), flush=True)
tmp = tempfile.mkdtemp(prefix="c153b1_")
T = json.load(open(TAB, encoding="utf-8"))
T2 = copy.deepcopy(T)
T2["rows"] = [r for r in T["rows"] if not str(r.get("run", "")).startswith("152-b1-2")]
TMPTAB = os.path.join(tmp, "naming_table_without_152-b1-2.json")
json.dump(T2, open(TMPTAB, "w", encoding="utf-8"), indent=1)
print("  FACT  temp table rows {0} -> {1}; LoopTunnel pairs real {2} / temp {3}".format(
    len(T["rows"]), len(T2["rows"]), SS.naming_table_lt_pairs(TAB), SS.naming_table_lt_pairs(TMPTAB)), flush=True)
today = json.load(open(os.path.join(HERE, "diag_c153_b1_1_default_before.json"), encoding="utf-8"))
k = [0]


def run(graph, **kw):
    k[0] += 1
    d = os.path.join(tmp, "r{0}".format(k[0]))
    S = SS.simulate(PLAN, graph, out_root=os.path.join(d, "sim"), plan_out_dir=d, log=print, **kw)
    return S, d


S1, _ = run(G08)
gate("C1 default (real table): fails at step 1 with today's text (recorded by stagesim {0})".format(today["stagesim_md5"][:8]),
     S1["failed"] == today["failed"] and not S1["final"] and "verdict" not in S1, S1["failed"])
S2, _ = run(G08, naming_table=TMPTAB)
gate("C2 default + temp table: same refusal at step 1", S2["failed"] == today["failed"] and not S2["final"], S2["failed"])
S3, d3 = run(G08, collect_all=True, naming_table=TMPTAB)
rf = S3["collect_all"]["refusals"]
by = dict((r["n"], r) for r in rf)
print("  FACT  C3 refusals: {0}".format(json.dumps([(r["n"], r["id"], r["refusal"]) for r in rf])), flush=True)
gate("C3a collect-all: verdict PROVISIONAL, final False, failed set, never PASS",
     S3["verdict"] == "PROVISIONAL" and S3["final"] is False and S3["failed"] and S3["collect_all"]["stopped_by"] is None,
     (S3["verdict"], S3["final"], S3["failed"]))
gate("C3b op 185 (step 1 p4_x_n2_order) owner refusal listed: FS #29721 UNMEASURED",
     1 in by and by[1]["id"] == "p4_x_n2_order" and "29721" in by[1]["refusal"] and "UNMEASURED" in by[1]["refusal"], by.get(1))
gate("C3c op 187 (step 3 p4_x_slot_fs) naming refusal listed: LoopTunnel 'min slot' UNMEASURED tunnel naming",
     3 in by and by[3]["id"] == "p4_x_slot_fs" and "UNMEASURED tunnel naming" in by[3]["refusal"] and "LoopTunnel" in by[3]["refusal"]
     and "min slot" in by[3]["refusal"], by.get(3))
pin = dict((s["n"], s["md5"]) for s in json.load(open(PLAN, encoding="utf-8"))["finalized"]["step_files"])
gate("C3d every refusal carries the plan's own prediction (md5 == plan.finalized.step_files[n])",
     rf and all(r["prediction"] and r["prediction"]["md5"] == pin.get(r["n"]) for r in rf), [r["prediction"] for r in rf])
steps = [s for s in S3["steps"] if s.get("provisional")]
gate("C3e the PROVISIONAL steps are exactly the refused ones and carry no error", sorted(s["n"] for s in steps) == sorted(by)
     and all(s["error"] is None for s in steps), [(s["n"], s["error"]) for s in steps])
S4, d4 = run(G08, collect_all=True)
gate("C4 collect-all + real table: only step 1 (op 187's LoopTunnel naming is measured by row 152-b1-2)",
     [r["n"] for r in S4["collect_all"]["refusals"]] == [1] and S4["verdict"] == "PROVISIONAL", S4["collect_all"]["refusals"])
S5, d5 = run(GFO, collect_all=True)
gate("C5 collect-all on the fsowner graph: 0 refusals and still verdict PROVISIONAL, final False, failed set",
     S5["collect_all"]["n_refusals"] == 0 and S5["verdict"] == "PROVISIONAL" and S5["final"] is False and S5["failed"],
     (S5["collect_all"]["n_refusals"], S5["failed"]))
plans = [p for d in (d3, d4, d5) for p in glob.glob(os.path.join(d, "**", "plan_*.json"), recursive=True)]
after = dict((p, md5(p)) for p in watch)
gate("C6 no plan_<stage>.json from a collect-all run; plan, graphs, real table, recorded sim files unchanged",
     not plans and after == before and sorted(p for p in glob.glob(os.path.join(SIMD, "*")) if os.path.isfile(p)) == watch[4:],
     (plans, [os.path.basename(p) for p in watch if after[p] != before[p]]))
gate("C7 CROSS_LT_FROM_TABLE is None after the runs", SS.CROSS_LT_FROM_TABLE is None, SS.CROSS_LT_FROM_TABLE)
nf = res.count(False)
print(P.result_line(P.make_result(res.count(True), nf, None if not nf else "selftest_c153_collect_all")), flush=True)
sys.exit(1 if nf else 0)
