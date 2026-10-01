"""diag_c127_3_checks - card 127-3 STEP 3 OFFLINE (no LabVIEW, no COM): (1) stagesim simulate plan_ring_p3b_in.json on the P3a
graph -> FINAL tools/bench/plan_ring_p3b.json; (2) stagexec dry + prerun in-process (the command line naming the executor is
refused under flags.labview none - gate-fp fp-15, as diag_c127_2_checks.py); (3) census + Error List prediction from the
simulated steps, written to tools/bench/plan_ring_p3b_pred.json (the recipe's only source of expected values).
PREDICTION: (1) final, 63 steps, end cdiff 16 == P3a's; (2) dry PASS (stagexec binds IMAQ Copy's 3 unnamed sinks by order,
card 127-3), prerun PASS; (3) Error List = 54 (P3a's 55 - w27378) + 0 own items (end cdiff adds no row; every created input is
wired; the HELD PD258(c) rows add none)."""
import collections, io, json, os, sys, contextlib, hashlib    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX     # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()   # noqa: E731
ok = []


def gate(n, c, d=""):
    ok.append((n, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", n, str(d)[:1500]), flush=True)


def run(fn, *a):
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        try:
            rc = fn(*a)
        except SystemExit as e:
            rc = e.code
    return rc, buf.getvalue()


PIN = os.path.join(B, "plan_ring_p3b_in.json")
GR = os.path.join(B, "graph_ring_p3a_20261001_190155.json")
P3A = json.load(open(os.path.join(B, "plan_ring_p3a.json"), encoding="utf-8"))
S = SS.simulate(PIN, GR, log=lambda *x: None, route_check=False)
last = S["steps"][-1]
po = os.path.join(B, "plan_ring_p3b.json")
end = sorted(last.get("cdiff_rows") or [])
gate("C1 simulate plan_ring_p3b_in: no failed step, final, 63 steps, end cdiff == P3a's 16 rows",
     S["failed"] is None and S.get("final") and len(S["steps"]) == 64 and end == sorted(P3A["finalized"]["end_cdiff_rows"]),
     {"failed": S["failed"], "final": S.get("final"), "steps": len(S["steps"]) - 1, "end_cdiff": len(end)})
res = {}
for mode in ("dry", "prerun"):
    rc, out = run(SX.main, ["stagexec.py", mode, po])
    res[mode] = [ln for ln in out.splitlines() if ln.startswith("RESULT")]
    for f in [ln[:400] for ln in out.splitlines() if ln.startswith("FAIL") or " FAIL " in ln[:12]][:12]:
        print("  FACT {0} {1}".format(mode, f), flush=True)
    gate("C2 stagexec {0} on plan_ring_p3b.json PASS".format(mode), rc in (0, None), res[mode])
# census prediction: per step's simulated census (stagesim effect_summary) summed, with its row source
cen, src = collections.Counter(), []
for s in S["steps"][1:]:
    es = s.get("effect_summary") or {}
    c = es.get("census") if isinstance(es.get("census"), dict) else None
    if c is None:
        c = s.get("census") if isinstance(s.get("census"), dict) else {}
    cen.update(c)
    src.append("{0} {1} {2}".format(s.get("id"), es.get("how") or es.get("route") or s.get("op"), json.dumps(c, sort_keys=True)))
print("  FACT census per step:\n    " + "\n    ".join(src), flush=True)
pl = json.load(open(po, encoding="utf-8"))
ops = [o["kind"] for o in SX.compile_plan(pl)]
el = {"base_file": None, "bed_total": 55, "removed": {"p3b_rle_w27378": 1}, "new_items_predicted": 0, "predicted_total": 54,
      "sources": ["P3a bed Error List 55 (stage_d1_ring_p3a errorlist_expected), w27378 'Wire has loose ends' removed by p3b_rle_w27378 "
                  "(diag_c126_4_op.log:52-60, 55 -> 54)",
                  "P3b own: 0 - end cdiff adds no open row (16 == P3a's); every created sink terminal is wired by a plan row; RLE after every crossing",
                  "UNPREDICTED: type/break items of new classes (FS / GrowableFunction / IndexArray) - the scratch run pins them (PD235(f))"]}
ebase = sorted(f for f in os.listdir(B) if f.startswith("errorlist_expected_D1_ring_p3a_"))
el["base_file"] = "tools/bench/" + ebase[-1] if ebase else None
pred = {"schema": "ring-p3b-pred/1", "card": "127-3", "plan": {"path": "tools/bench/plan_ring_p3b.json", "md5": md5(po)},
        "graph": {"path": "tools/bench/graph_ring_p3a_20261001_190155.json", "md5": md5(GR)},
        "bed": json.load(open(GR, encoding="utf-8"))["vi"], "bed_md5": json.load(open(GR, encoding="utf-8"))["md5"],
        "census": dict(cen), "census_sources": src, "ops": ops, "cdiff_rows": end, "errorlist": el}
json.dump(pred, open(os.path.join(B, "plan_ring_p3b_pred.json"), "w", encoding="utf-8"), indent=1)
gate("C3 prediction written: census + Error List 54 (P3a 55 - w27378) + 0 own", el["base_file"] is not None,
     {"census": dict(cen), "ops": dict(collections.Counter(ops)), "el_base": el["base_file"], "pred_md5": md5(os.path.join(B, "plan_ring_p3b_pred.json"))})
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
