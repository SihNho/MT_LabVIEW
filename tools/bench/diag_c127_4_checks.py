"""diag_c127_4_checks - card 127-4 (PD259(b)) OFFLINE (no LabVIEW, no COM): the rest of 127-3's checks after the dry renumber fix
(stagexec._fs_entries_remap, SimBackend RLE-DRY check, dry_run SIM-INTERNAL). Same steps as diag_c127_3_checks.py (prior art,
re-used, not rebuilt) + the recipe-level pre-run and the scratch decision:
  C1 stagesim simulate plan_ring_p3b_in.json on the P3a graph -> FINAL plan_ring_p3b.json (63 actions, end cdiff 16 == P3a's)
  C2 stage_prerun --dry / --prerun on the PLAN (stagexec dry + prerun_plan + X8/X11/X13/X16/X15, recorded) - in-process, as 127-3
  C3 plan_ring_p3b_pred.json: census per row (row sources), ops, cdiff rows, Error List 54 (= P3a 55 - w27378) + own items 0, with
     the rows that move it and every created node's still-unwired sink listed as a source
  C4 stage_prerun --dry / --prerun on the RECIPE tools/recipes/stage_d1_ring_p3b.py (COM stubbed, recorded; NOT launched)
  C5 stage_prerun.scratch_requirement(recipe) -> SCRATCH-REQUIRED / SCRATCH-SKIP-PROVEN, recorded
PREDICTION: C1 PASS; C2 dry PASS + prerun PASS (inner-face branches find their entry face; RLE rows non-vacuous); C3 written;
C4 dry PASS + prerun PASS; C5 SCRATCH-REQUIRED (new classes FS / IMAQ Copy subVI / IndexArray, D-2026-10-01-01 => full scratch)."""
import collections, contextlib, hashlib, io, json, os, sys    # noqa: E401
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
B = os.path.join(ROOT, "tools", "bench")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX, stage_prerun as SP     # noqa: E402,E401
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
    out = buf.getvalue()
    for ln in [x for x in out.splitlines() if x.startswith(("RESULT", "===", "  FAIL", "FAIL", "SCRATCH", "  WARN", "ADVISORY"))][:40]:
        print("    | " + ln[:600], flush=True)
    return rc, out


PIN = os.path.join(B, "plan_ring_p3b_in.json")
GR = os.path.join(B, "graph_ring_p3a_20261001_190155.json")
po = os.path.join(B, "plan_ring_p3b.json")
REC = os.path.join(ROOT, "tools", "recipes", "stage_d1_ring_p3b.py")
P3A = json.load(open(os.path.join(B, "plan_ring_p3a.json"), encoding="utf-8"))
m0 = md5(po)
S = SS.simulate(PIN, GR, log=lambda *x: None, route_check=False)
last = S["steps"][-1]
end = sorted(last.get("cdiff_rows") or [])
gate("C1 simulate plan_ring_p3b_in: no failed step, final, 63 steps, end cdiff == P3a's 16 rows",
     S["failed"] is None and S.get("final") and len(S["steps"]) == 64 and end == sorted(P3A["finalized"]["end_cdiff_rows"]),
     {"failed": S["failed"], "final": S.get("final"), "steps": len(S["steps"]) - 1, "end_cdiff": len(end),
      "plan_md5_before": m0, "plan_md5_after": md5(po)})
for mode in ("--dry", "--prerun"):
    rc, out = run(SP.main, [mode, po])
    gate("C2 stage_prerun {0} on plan_ring_p3b.json PASS".format(mode), rc == 0,
         [ln for ln in out.splitlines() if ln.startswith("RESULT")])
    if rc != 0:
        break
c2_ok = all(c for n, c in ok if n.startswith("C2"))
# C3 census per row + Error List sources
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
fin_st = json.load(open(os.path.join(ROOT, pl["finalized"]["step_files"][-1]["path"]), encoding="utf-8"))
fin_st = fin_st.get("state", fin_st)
base_owners = set(int(r["owner_uid"]) for r in json.load(open(GR, encoding="utf-8"))["terminals"])
unw = sorted("{0}#{1} {2!r} (owner {3} #{4})".format("sink", r["term_uid"], r["term_name"], r["owner_class"], r["owner_uid"])
             for r in fin_st.get("terminals") or [] if int(r["owner_uid"]) not in base_owners and not r["is_source"] and not r["wire_uid"])
print("  FACT created-node sinks still unwired at the plan's end ({0}): {1}".format(len(unw), unw), flush=True)
rle = [a["id"] for a in pl["actions"] if a["op"] == "wire_remove_loose_ends"]
el = {"bed_total": 55, "removed": {"p3b_rle_w27378": 1}, "new_items_predicted": 0, "predicted_total": 54,
      "row_sources": {"p3b_rle_w27378": "-1: w27378 'Wire has loose ends' removed (diag_c126_4_op.log:52-60, 55 -> 54)",
                      "crossings (fs_border / fs_inner_branch)": "0: measured census, Error List count unchanged (diag_c127_1_fsinner.log:81-109)",
                      "RLE rows " + ",".join(x for x in rle if x != "p3b_rle_w27378"): "0: loose ends left by crossings cleared (diag_c126_6_cross.log:61-65)",
                      "created nodes": "0 if no required input is unwired; created sinks still unwired at end: {0}".format(unw or "none")},
      "unpredicted": "type/break items of new classes (FS / IMAQ Copy subVI / IndexArray) - the full scratch run pins them (PD235(f))"}
ebase = sorted(f for f in os.listdir(B) if f.startswith("errorlist_expected_D1_ring_p3a_"))
el["base_file"] = "tools/bench/" + ebase[-1] if ebase else None
G = json.load(open(GR, encoding="utf-8"))
pred = {"schema": "ring-p3b-pred/1", "card": "127-4", "plan": {"path": "tools/bench/plan_ring_p3b.json", "md5": md5(po)},
        "graph": {"path": "tools/bench/graph_ring_p3a_20261001_190155.json", "md5": md5(GR)}, "bed": G["vi"], "bed_md5": G["md5"],
        "census": dict(cen), "census_sources": src, "ops": ops, "cdiff_rows": end, "errorlist": el,
        "held": "PD258(c)/PD259(c) Unbundle By Name + Select + const -1 rows (UNMEASURED, not in this plan)"}
PO = os.path.join(B, "plan_ring_p3b_pred.json")
json.dump(pred, open(PO, "w", encoding="utf-8"), indent=1)
gate("C3 prediction written: census + Error List 54 (P3a 55 - w27378) + 0 own, row sources", el["base_file"] is not None,
     {"census": dict(cen), "ops": dict(collections.Counter(ops)), "el_base": el["base_file"], "pred_md5": md5(PO)})
if c2_ok:
    for mode in ("--dry", "--prerun"):
        rc, out = run(SP.main, [mode, REC])
        gate("C4 stage_prerun {0} on the recipe (COM stubbed, NOT launched) PASS".format(mode), rc == 0,
             [ln for ln in out.splitlines() if ln.startswith(("RESULT", "=== "))])
        if rc != 0:
            break
    req, why, st_ = SP.scratch_requirement(REC)
    line = ("SCRATCH-REQUIRED | {0} | {1}".format(SP.stage_key(REC), why) if req else
            "SCRATCH-SKIP-PROVEN | {0} | proven: {1}".format(SP.stage_key(REC), ", ".join(st_)))
    print("  FACT " + line, flush=True)
    gate("C5 --scratch-required decision recorded (predicted SCRATCH-REQUIRED)", req, line)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None),
                                  [{"path": "tools/bench/plan_ring_p3b_pred.json", "md5": md5(PO)}])), flush=True)
sys.exit(1 if nf else 0)
