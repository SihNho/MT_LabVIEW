r"""diag_c101c_resim - card 101-5 (rung 2 of 101-4). Pure Python, no LabVIEW. PRIOR ART: diag_c101b_resim.py (same
shape, one card earlier); nothing new is built, only the r5 record replaces the r4 record.
(A) hold the OLD finalized plan (plan_disp.json b535071e, the one run r5 executed) and its step files in memory;
(B) re-simulate the UNCHANGED plan input stageplan_disp_r4_open.json with the card-101-5 stagesim (only_source rule:
    a moved PRIMITIVE node - not a SubVI - that was a single-sink cut wire's only source takes the wire along);
(C) REPLAY vs r5: for every checkpoint k that r5 READ (tools/bench/stage_d1_disp.json "stagexec"[k].diff: 0 for
    k 2,3,4,5,24,25; {dangling_sim_only: [11365]} for k 12), stagexec.compare(OLD step k, NEW step k) must reproduce
    EXACTLY that diff. Equal component lists => the NEW step k has the real read's terminal, edge and dangling sets.
(D) the k12 shape: in OLD step 11 the wire on LoopTunnel inner 11365 has exactly one moved-side row (a source on
    Bundler #11310) and one outside row (11365, a sink) - the only_source shape.
PREDICTION: R3 FINAL, R4 end cdiff == 21 open rows, REPLAY equal on all 7 checkpoints, D1 shape holds.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/diag_c101c_resim.log -- py -u tools/bench/diag_c101c_resim.py"""
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


OLD_MD5 = SS.md5_file(PO)
fact("A0 (a FACT since cycle 102: every re-sim re-stamps finalized.at, so the md5 is never a fixed known value; R6b compares "
     "content) OLD plan on disk md5 {0}; r5 ran b535071e, run 1 wrote 8a96086f, run 2 7c432e1b, run 3 94800c90".format(OLD_MD5))
OLD = J(PO)
old_st = []
for f in OLD["finalized"]["step_files"]:
    ok = SS.md5_file(os.path.join(ROOT, f["path"])) == f["md5"]
    old_st.append(J(f["path"]) if ok else None)
gate("A1 all {0} OLD step files intact (md5 == finalized)".format(len(old_st)), all(old_st), sum(1 for x in old_st if x))
r5 = J(REC)
r5d = dict((int(r.get("k") or 0), r["diff"]) for r in r5["stagexec"] if r.get("k") is not None and r.get("diff") is not None)
# REAL reads only (review archive/peer/2026-09-27-c101-5-onlysource.md "Gate A2 is wrong"): the r5 log's `STEPX k ... diff N`
# lines; a `diff skipped (not a checkpoint)` step has NO real read and is never compared against the real machine.
import re                                                                          # noqa: E402
cps = sorted(int(m.group(1)) for m in re.finditer(r"^\s*STEPX\s+(\d+)\s.*\bdiff\s+\d+\s*$",
                                                  open(os.path.join(HERE, "stage_d1_disp_r5.log"), encoding="utf-8", errors="replace").read(), re.M)
             if int(m.group(1)) > 0)                                             # k0 = the base read, no op
gate("A2 the r5 record (task card 101-4) has REAL reads exactly at k [2, 3, 4, 5, 12, 24, 25] (facts_c101b_stage.json reads_compared)",
     r5.get("task") == "card 101-4" and cps == [2, 3, 4, 5, 12, 24, 25] and all(k in r5d for k in cps), (r5.get("task"), r5.get("stamp"), cps))
# (D) the k12 shape in the OLD step 11 state
t11 = old_st[11]["state"]["terminals"]
w11365 = next((r["wire_uid"] for r in t11 if r["term_uid"] == 11365), None)
rows_w = [r for r in t11 if r["wire_uid"] == w11365] if w11365 else []
ins = [r for r in rows_w if r["owner_uid"] == 11310]
outs = [r for r in rows_w if r["owner_uid"] != 11310]
fact("k12 shape: 11365 on wire {0}; rows {1}".format(w11365, [(r["term_uid"], r["owner_uid"], r["owner_class"], r["is_source"]) for r in rows_w]))
gate("D1 before op 12 the wire on 11365 has ONE moved-side source row (Bundler #11310) and ONE outside sink row (11365)",
     len(ins) == 1 and ins[0]["is_source"] and ins[0]["owner_class"] == "Bundler" and len(outs) == 1 and
     outs[0]["term_uid"] == 11365 and not outs[0]["is_source"], (len(ins), len(outs)))
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
# SECOND RUN (rule REVERTED after run 1, diag_c101c_resim.log 00:35 + review 2026-09-27-c101-5-onlysource.md): the card's
# source-class rule diverged from the REAL reads at k24/k25 (8323 kept) and cut edge 11369->11270 at k12. PREDICTION now:
# the re-simulation equals the r5 plan at every step (NEW == OLD), so the k12 gap [11365] is STILL OPEN and is reported as a
# fact, not hidden behind a rule fitted to one sample.
OLD_IS_R5 = OLD_MD5 == "b535071ef8e62fdf045ecb30499f89ce"
same_all = True                                                                    # cycle 102: content, not bytes (PD214(d)2)
for k in range(1, len(new_st)):
    got_k = comp(old_st[k]["state"]["terminals"], new_st[k]["state"]["terminals"])
    same_all = same_all and not any(got_k[x] for x in KEYS)
for k in cps:
    want_k = dict((x, [list(v) if isinstance(v, (list, tuple)) else v for v in r5d[k].get(x) or []]) for x in KEYS)
    got_k = comp(old_st[k]["state"]["terminals"], new_st[k]["state"]["terminals"])
    fact("REPLAY k{0}: r5 real-vs-OLD {1} | NEW-vs-OLD({2}) {3}".format(
        k, dict((x, y) for x, y in want_k.items() if y), "r5" if OLD_IS_R5 else "run1/run2",
        dict((x, y) for x, y in got_k.items() if y)))
gate("R6b (cycle 102, PD214(d)2) the re-simulated plan is CONTENT-IDENTICAL to the plan on disk at every step (terminals, edges, "
     "dangling sets; only finalized.at / md5 provenance may differ) - so 7c432e1b vs b535071e is provenance-only IF the plan on "
     "disk was itself content-identical to r5's (run 2's REPLAY facts: NEW-vs-OLD {} at k 2,3,4,5,12,24,25)", same_all, len(new_st))
w11365 = next(r["wire_uid"] for r in new_st[12]["state"]["terminals"] if r["term_uid"] == 11365)
fact("KNOWN GAP k12: sim keeps LoopTunnel inner 11365 on sourceless w{0}; real read wire 0 (r5.log:249). Source-class and "
     "sink-class rules are both refuted (review c101-5-onlysource); candidates A/B/C there are confounded on 4 real samples".format(w11365))
fact("R6 (retired cycle 102 - `finalized.at` is stamped on every re-sim, so bytes never repeat; R6b is the content gate) "
     "re-simulated plan_disp.json md5 {0} vs r5's b535071e".format(SS.md5_file(PO)))
n = sum(1 for _l, g in gates if g)
ff = next((l for l, g in gates if not g), None)
arts = [{"path": os.path.relpath(p, ROOT), "md5": SS.md5_file(p)} for p in (R4O, PO)]
print(protocol.result_line(protocol.make_result(n, len(gates) - n, ff, arts)), flush=True)
sys.exit(0 if ff is None else 1)
