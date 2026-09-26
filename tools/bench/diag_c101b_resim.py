r"""diag_c101b_resim - card 101-4 (rung 1 of 101-3). Pure Python, no LabVIEW.
(A) hold the OLD finalized plan (plan_disp.json 9e1e98c9, the one run r4 executed) and its step files in memory;
(B) re-simulate the UNCHANGED plan input stageplan_disp_r4_open.json with the card-101-4 stagesim (only_source rule:
    a moved constant that was a single-sink cut wire's only source takes the wire along) -> plan_disp.json + step files;
(C) REPLAY vs r4: for steps 1-4, stagexec.compare(OLD step k, NEW step k) must reproduce EXACTLY the diff run r4
    recorded between the OLD step k and the REAL read (tools/bench/stage_d1_disp.json "stagexec"[k].diff): 0 for k 1-3,
    {dangling_sim_only: [8753]} for k 4. Equal component lists => the NEW step k has the real read's terminal, edge and
    dangling sets (X_real = X_old - sim_only + real_only, likewise X_new). 'unbound'/'who' are sim-internal: not compared.
(D) where else the plan moved: every step k whose OLD vs NEW compare is non-zero (expected: 4, 5 only - #8795 is the
    second DigitalNumericConstant; step 6 moves #8741 and R-BARE removed the half-wires in the OLD model).
PRIOR ART: diag_c101_resim.py (A/B shape), diag_c101_op4.py (the op-4 read). PREDICTION: R3 FINAL, R4 end cdiff == 21
open rows, REPLAY k1-k4 equal, D changed steps == [4, 5].
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c101b_resim.log -- py -u tools/bench/diag_c101b_resim.py"""
import json, os, sys                                                                # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol           # noqa: E402
import stagesim as SS     # noqa: E402
import stagexec as SX     # noqa: E402

R4O = os.path.join(HERE, "sim", "disp", "stageplan_disp_r4_open.json")
PO = os.path.join(HERE, "sim", "disp", "plan_disp.json")
REC = os.path.join(HERE, "stage_d1_disp.json")
J = lambda p: json.load(open(p if os.path.isabs(p) else os.path.join(ROOT, p), encoding="utf-8"))   # noqa: E731
KEYS = ("only_sim_terms", "only_real_terms", "only_sim_edges", "only_real_edges", "dangling_sim_only", "dangling_real_only")
gates, facts = [], []


def gate(label, ok, detail=""):
    gates.append((label, bool(ok)))
    print("  {0}  {1}  {2}".format("PASS" if ok else "FAIL", label, str(detail)[:900]), flush=True)


def fact(s):
    facts.append(s)
    print("  FACT " + s, flush=True)


def comp(a, b):
    d = SX.compare(a, b, {"obj": {}, "term": {}, "diag": {}})
    return dict((k, [list(x) if isinstance(x, (list, tuple)) else x for x in d[k]]) for k in KEYS)


gate("A0 OLD plan is the one r4 ran (md5 9e1e98c9...)", SS.md5_file(PO) == "9e1e98c97d4e6980530b12b2b4d39fa4", SS.md5_file(PO))
OLD = J(PO)
old_st = []
for f in OLD["finalized"]["step_files"]:
    ok = SS.md5_file(os.path.join(ROOT, f["path"])) == f["md5"]
    old_st.append(J(f["path"]) if ok else None)
gate("A1 all {0} OLD step files intact (md5 == finalized)".format(len(old_st)), all(old_st), sum(1 for x in old_st if x))
r4 = J(REC)
r4d = dict((int(r.get("k", 0)), r["diff"]) for r in r4["stagexec"])
gate("A2 the r4 record is the r4 run (stamp 20260926_234019) with diffs for k 0-4", r4["stamp"] == "20260926_234019" and
     sorted(r4d) == [0, 1, 2, 3, 4], (r4["stamp"], sorted(r4d)))
S = SS.simulate(R4O, os.path.join(ROOT, J(R4O)["base"]["path"]), out_root=os.path.join(HERE, "sim"),
                plan_out_dir=os.path.join(HERE, "sim", "disp"), log=lambda *_a: None)
gate("R3 re-simulation FINAL", S["final"], (S["failed"], S["undecided"], S["first_divergent"]))
NEW = J(PO)
want = sorted(set((int(r["node"]), r["term"]) for r in NEW["open_rows"]))
got = sorted(set((int(k.split("|")[0]), k.split("|")[2]) for k in S["end_cdiff_rows"] or []))
gate("R4 end cdiff rows == the {0} declared open_rows".format(len(want)), got == want,
     {"extra": sorted(set(got) - set(want)), "missing": sorted(set(want) - set(got))})
new_st = [J(f["path"]) for f in NEW["finalized"]["step_files"]]
fact("NEW plan_disp.json md5 {0}; {1} step files".format(SS.md5_file(PO), len(new_st)))
for k in (1, 2, 3, 4):
    want_k = dict((x, [list(v) if isinstance(v, (list, tuple)) else v for v in r4d[k].get(x) or []]) for x in KEYS)
    got_k = comp(old_st[k]["state"]["terminals"], new_st[k]["state"]["terminals"])
    fact("REPLAY k{0}: r4 real-vs-OLD {1} | NEW-vs-OLD {2}".format(
        k, dict((x, y) for x, y in want_k.items() if y), dict((x, y) for x, y in got_k.items() if y)))
    gate("REPLAY k{0}: NEW step == r4 REAL read on terminals, edges and dangling sets".format(k), got_k == want_k,
         {"r4": want_k, "new": got_k})
e4 = new_st[4].get("effect") or {}
row = dict((r["term_uid"], r["wire_uid"]) for r in new_st[4]["state"]["terminals"] if r["term_uid"] in (8753, 8774))
gate("R5 NEW step 4 effect: only_source w8804 #8775 DigitalNumericConstant -> 8753 fate delete; 8753/8774 wire 0",
     [(x["wire"], x["src_uid"], x["sink_term_uid"], x["fate"]) for x in e4.get("only_source") or []] == [(8804, 8775, 8753, "delete")]
     and row == {8753: 0, 8774: 0}, (e4.get("only_source"), row))
e5 = new_st[5].get("effect") or {}
fact("PREDICTION op 5 (mv_8795): only_source {0}".format(e5.get("only_source")))
changed = []
for k in range(len(new_st)):
    d = comp(old_st[k]["state"]["terminals"], new_st[k]["state"]["terminals"])
    if any(d.values()):
        changed.append(k)
        fact("OLD vs NEW step {0:02d}: {1}".format(k, dict((x, y) for x, y in d.items() if y)))
gate("D1 the model change moves ONLY steps 4-5 (converged by step 6: #8741's move deletes the half-wires in both)",
     changed == [4, 5], changed)
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, PO)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
