# ---
# labview: none
# hardware: none
# evidence: tools/stagekit.py:1790-1803
# ---
"""diag_c158_a2_3_measure - card 158-a2-3 (OFFLINE, no LabVIEW, no edits): the hypothesis review's section-4 PB-keying test and a
pair-keyed D/TD recount on the c158-a2-2 scratch data (archive/peer/2026-10-10-c158-a2-2-p5s02a-loopface.md:99-108).
Existing functions CALLED (none copied, docs/script-writing.md): stagekit.RingSession (plan/pred/licence/base/LAB/FSPAIRS),
stagekit.s1_frame_graph, stagekit.pred_end_graph, stagekit.pb_rename_rows, stagekit.pb_check, stagekit.term_identity_gates,
stagekit._pos_rows / wire_ends_pos, vigraph.build4 / effective_sources / computation_diff_frame / key_parts.
The real end is rebuilt from diag_c156_p5s02a_scratch.json `real_end_rows` (5 columns: term uid, owner, name, wire, is_source);
term_class / owner_class / frame_diagram come from the sim end row at the SAME index (alignment is measured and printed first,
ASSUMPTION AL) with sim uids mapped through the run's `bound` maps; objs / loops = the sim end's through the same map.
PREDICTION (review s4): sim frame -29 (CQ7.f0) ranks ordinal 1 (sorted -30 < -29), real 31506 ranks 0; the #376 'cal cluster path' /
'file size' tags flip /f1 -> /f0 once real uids are bound; reproduced real PB extra == the logged pair (376 cal cluster path, file size)."""
import os, sys, copy, json                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402
import protocol                                                                            # noqa: E402

# ---- INPUTS ------------------------------------------------------------------------------------------------------------------------
PLAN, PRED = os.path.join(K.BENCH, "plan_ring_p5s02a.json"), os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json")
LIC, SGC = os.path.join(K.BENCH, "plan_ring_p5s02a_licence.json"), os.path.join(K.BENCH, "prep_c156_a1_1_session.json")
SIMF = os.path.join(K.BENCH, "sim", "ring_p5s02a", "step_23_wire.json")
REAL = os.path.join(K.BENCH, "diag_c156_p5s02a_scratch.json")
M4 = {-44: 31546, -49: 31557, -29: 31506, -30: 31517}       # brief item 1(3); log :442 (-29/-30), :540 (-44), :548 (-49)
NODE, NAMES = 376, ("cal cluster path", "file size", "selected path", "current frame data array in")
FATE_SINKS = (5760, 5778, 5787, 5683, 5782, 5772, 5754)
FATE_SRCS = (24360, 24367, 25235, 24190, 24288, 3060)
OUT = os.path.join(K.BENCH, "diag_c158_a2_3_measure.json")

V = K.pure("vigraph")
RS = K.RingSession(PLAN, PRED, LIC, SGC)
L = K.jload(SIMF)["state"]
D = K.jload(REAL)
BOUND = {}
for o in D["stagexec"]:
    BOUND.update(dict((int(k), int(v)) for k, v in (o.get("bound") or {}).items()))
res, ok = {}, []


def remap(state, M):
    """A deep copy of a sim state with every uid field mapped through M (terminals, objs, loops)."""
    S = copy.deepcopy(state)
    f = lambda v: M.get(int(v), int(v)) if isinstance(v, int) or (isinstance(v, str) and v.lstrip("-").isdigit()) else v   # noqa: E731
    for r in S["terminals"]:
        for c in ("term_uid", "owner_uid", "wire_uid", "frame_diagram"):
            if r.get(c) not in (None, ""):
                r[c] = f(r[c])
    for o in S.get("objs") or []:
        o["uid"] = f(o["uid"])
    for lp in S["loops"]:
        lp["loop_uid"] = f(lp["loop_uid"])
        lp["right_uids"] = [f(u) for u in lp.get("right_uids") or []]
        lp["left_of"] = dict((str(f(k)), [f(u) for u in v]) for k, v in (lp.get("left_of") or {}).items())
    return S


def sink_keys(G):
    return dict((r["term_name"], k) for k, r in G["rows"].items() if r["node"] == NODE and not r.get("is_source") and r["term_name"] in NAMES)


def es_report(tag, G):
    sk, out = sink_keys(G), {}
    for n in NAMES:
        k = sk.get(n)
        out[n] = sorted(V.effective_sources(G, k)) if k else "NO KEY"
        print("  ES {0:10s} #376 {1!r:32s} key {2} -> {3}".format(tag, n, k, out[n]), flush=True)
    fo = sorted((k, V.key_parts(k)[3]) for k in G.get("frame_inner") or () if "/" not in k)
    return out


def cd376(tag, S1, G):
    rows = [y["sink"] for y in V.computation_diff_frame(S1, G)["rows"] if str(y["sink"]).startswith("376|")]
    print("  CD {0:10s} cdiff(S1, G) rows on #376: {1}".format(tag, rows), flush=True)
    return rows


print("== 0 inputs: sim end = plan step_files[-1]?", RS.P["finalized"]["step_files"][-1]["path"], "| BOUND", BOUND, flush=True)
# ---- ASSUMPTION AL: real_end_rows aligned with the sim end terminals by index -------------------------------------------------------
RR, ST = D["real_end_rows"], L["terminals"]
# AL: a real row takes the sim row with the SAME term uid; a real-only term uid takes an unused sim row (negative uid) of the same
# bound-mapped owner, first by (name, direction), then by (direction, read order). Counts printed; unmatched rows listed.
by_uid = dict((int(s["term_uid"]), s) for s in ST)
neg = {}
for s in ST:
    if int(s["term_uid"]) < 0:
        neg.setdefault(BOUND.get(int(s["owner_uid"]), int(s["owner_uid"])), []).append(s)
al = {"n_real": len(RR), "n_sim": len(ST), "same_uid": 0, "by_name": 0, "by_order": 0, "unmatched": [], "sim_neg_left": []}
pick = {}
for q in RR:
    if int(q[0]) in by_uid:
        al["same_uid"] += 1
        pick[int(q[0])] = by_uid[int(q[0])]
for q in RR:
    u = int(q[0])
    if u in pick:
        continue
    c = neg.get(int(q[1]), [])
    m = [s for s in c if s["term_name"] == q[2] and bool(s["is_source"]) == bool(q[4])]
    if m:
        al["by_name"] += 1
    else:
        m = [s for s in c if bool(s["is_source"]) == bool(q[4])]
        al["by_order"] += 1 if m else 0
    if m:
        pick[u] = m[0]
        c.remove(m[0])
    else:
        al["unmatched"].append(list(q))
al["sim_neg_left"] = [(s["term_uid"], s["owner_uid"], s["term_name"]) for c in neg.values() for s in c]
al["real_new_uids"] = sorted(u for u in pick if u not in by_uid)
print("== AL term matching", json.dumps(al), flush=True)
fmap = lambda v: BOUND.get(int(v), int(v)) if v not in (None, "") else v   # noqa: E731
real = [{"term_uid": int(q[0]), "owner_uid": int(q[1]), "term_name": q[2], "wire_uid": int(q[3] or 0), "is_source": bool(q[4]),
         "term_class": pick[int(q[0])].get("term_class"), "owner_class": pick[int(q[0])].get("owner_class"),
         "frame_diagram": fmap(pick[int(q[0])].get("frame_diagram"))} for q in RR if int(q[0]) in pick]
ok.append(not al["unmatched"])
Lb = remap(L, BOUND)                       # the sim end in real object space (objs / loops for the real build)

# ---- 1 the review's section-4 test ---------------------------------------------------------------------------------------------------
print("\n== 1 PB keying (section 4)", flush=True)
S1 = K.s1_frame_graph(RS.LAB)
Gs = K.pred_end_graph(L, RS.LAB, RS.FSPAIRS)
G4 = K.pred_end_graph(remap(L, M4), RS.LAB, RS.FSPAIRS)
GB = K.pred_end_graph(Lb, RS.LAB, RS.FSPAIRS)
pbr, restored, unlic = K.pb_rename_rows(RS.BASE["terminals"], L["terminals"], real, RS.REN)
GR = V.build4(pbr, Lb.get("objs") or [], copy.deepcopy(Lb["loops"]), RS.LAB, RS.FSPAIRS, frame_keyed=True)
fr = lambda G, u: sorted(set((V.key_parts(k)[0], V.key_parts(k)[3]) for k, r in G["rows"].items() if k in G["frame_inner"] and int(r["frame_diagram"] or 0) == u))   # noqa: E731
for tag, G, us in (("sim", Gs, (-29, -30)), ("sim+M4", G4, (31506, 31517)), ("sim+BOUND", GB, (31506, 31517)), ("real", GR, (31506, 31517))):
    print("  FO {0:10s} frame -> (tunnel node, ordinal) of its inner keys: {1}".format(tag, dict((u, fr(G, u)) for u in us)), flush=True)
for tag, G in (("S1", S1), ("sim", Gs), ("sim+M4", G4), ("sim+BOUND", GB), ("real", GR)):
    res["es_" + tag] = es_report(tag, G)
for tag, G in (("sim", Gs), ("sim+M4", G4), ("sim+BOUND", GB), ("real", GR)):
    res["cd_" + tag] = cd376(tag, S1, G)
for tag, G in (("real", GR), ("sim+M4", G4), ("sim+BOUND", GB), ("sim", Gs)):
    r = K.pb_check(S1, G, Gs, RS.PRED["cdiff_rows"], RS.P["open_rows"], unlic, V)
    res["pb_" + tag] = {"ok": r["ok"], "extra": r["extra_sinks"], "missing": r["missing_sinks"], "pairs_extra": [list(p) for p in r["pairs_extra"]],
                        "pairs_missing": [list(p) for p in r["pairs_missing"]]}
    print("  PB {0:10s} pb_check(S1, G, sim end) ok {1} extra {2} missing {3} pairs_extra {4} pairs_missing {5}".format(
        tag, r["ok"], r["extra_sinks"], r["missing_sinks"], r["pairs_extra"], r["pairs_missing"]), flush=True)
ok.append(res["pb_real"]["pairs_extra"] == [[376, "cal cluster path"], [376, "file size"]])
print("  REPRO real PB extra == log :559 pair:", ok[-1], flush=True)
# 1b the same cdiff in the MERGED (default, not frame-keyed) mode, the mode stagesim's end_cdiff_rows use (stagesim.py:2665-2667 ->
# jev_candidates.from_parts -> build4 without frame_keyed). S1 = stagesim.load_s1(plan) (stagesim.py:2438), the simulator's own S1.
SS = K.pure("stagesim")
S1m = SS.load_s1(RS.P)
cd_lab, cd_fs, _rec = SS.cdiff_inputs(RS.P, L, RS.LAB)
for tag, G in (("sim merged", SS.graph(L, cd_lab, cd_fs)), ("real merged", V.build4(pbr, Lb.get("objs") or [], copy.deepcopy(Lb["loops"]), RS.LAB, RS.FSPAIRS))):
    rows = sorted(SS.cdiff_keys(V.computation_diff(S1m, G)))
    res["merged_" + tag] = {"n": len(rows), "eq_pred": rows == sorted(RS.PRED["cdiff_rows"]), "only_rows": sorted(set(rows) - set(RS.PRED["cdiff_rows"])),
                            "only_pred": sorted(set(RS.PRED["cdiff_rows"]) - set(rows)), "on376": [x for x in rows if x.startswith("376|")]}
    print("  MERGED {0:11s} cdiff(S1, G) rows {1}".format(tag, res["merged_" + tag]), flush=True)

# ---- 2 pair-keyed D / TD recount -----------------------------------------------------------------------------------------------------
print("\n== 2 pair-keyed wires", flush=True)
ti = K.term_identity_gates(RS.BASE["terminals"], L["terminals"], real, renames=RS.REN, bind={"term": {}, "obj": BOUND})
print("  REPRO term_identity_gates: d_new {0} sim_new {1} d_lost {2} sim_lost {3} unwired {4} lost {5}".format(
    ti["d_new"], len(ti["sim_new"]), ti["d_lost"], len(ti["sim_lost_w"]), ti["unwired"], ti["lost"]), flush=True)
ok.append(ti["d_new"] == 21 and len(ti["sim_new"]) == 22 and ti["unwired"] == [(25223, 1, "InnerTerminal", True)])


def pairs(rows, ob=None):
    P, half = set(), set()
    for w, (a, b) in K.wire_ends_pos(rows, ob).items():
        if not a or not b:
            half.add((tuple(sorted(a)), tuple(sorted(b))))
        for x in a:
            for y in b:
                P.add((x, y))
    return P, half


Pb, Hb = pairs(RS.BASE["terminals"])
Ps, Hs = pairs(L["terminals"], BOUND)
Pr, Hr = pairs(real)
res["pairs"] = {"base": len(Pb), "sim": len(Ps), "real": len(Pr), "sim_new": len(Ps - Pb), "real_new": len(Pr - Pb),
                "sim_lost": len(Pb - Ps), "real_lost": len(Pb - Pr), "only_sim": sorted(map(str, Ps - Pr)), "only_real": sorted(map(str, Pr - Ps)),
                "half_sim": sorted(map(str, Hs)), "half_real": sorted(map(str, Hr)), "half_base": len(Hb),
                "half_only_sim": sorted(map(str, Hs - Hr)), "half_only_real": sorted(map(str, Hr - Hs))}
for k, v in res["pairs"].items():
    print("  PAIRS {0}: {1}".format(k, v), flush=True)
pos = lambda rows, u: [(k, r.get("term_name"), r.get("wire_uid")) for k, r in K._pos_rows(rows).items() if k[0] == u]   # noqa: E731
for tag, rows in (("base", RS.BASE["terminals"]), ("sim", L["terminals"]), ("real", real)):
    print("  TD node 25223 rows {0}: {1}".format(tag, pos(rows, 25223)), flush=True)

# ---- 4 FATE: the wires into #376 and out of the loop faces, real vs sim -------------------------------------------------------------
print("\n== 4 FATE", flush=True)
by = lambda rows: dict((int(r["term_uid"]), r) for r in rows)   # noqa: E731
wires = lambda rows: K.wire_ends_pos(rows)   # noqa: E731
res["fate"] = {}
for tag, rows in (("base", RS.BASE["terminals"]), ("sim", L["terminals"]), ("real", real)):
    T, W = by(rows), {}
    for r in rows:
        if r.get("wire_uid"):
            W.setdefault(int(r["wire_uid"]), []).append((int(r["term_uid"]), int(r["owner_uid"]), r["term_name"], bool(r["is_source"])))
    for u in FATE_SINKS + FATE_SRCS:
        r = T.get(u)
        w = int(r["wire_uid"] or 0) if r else None
        line = (u, r and r["term_name"], w, sorted(W.get(w, [])) if w else [])
        res["fate"].setdefault(str(u), {})[tag] = line
        print("  FATE {0:4s} t{1} {2!r} wire {3} ends {4}".format(tag, u, line[1], w, line[3]), flush=True)

json.dump(res, open(OUT, "w"), indent=1, default=str)
print(protocol.result_line({"status": "PASS" if all(ok) else "FAIL", "gates": {"pass": sum(ok), "fail": len(ok) - sum(ok)},
                            "first_fail": None if all(ok) else "reproduction of the logged PB / D / TD values", "artefacts": []}), flush=True)
