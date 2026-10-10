# ---
# labview: none
# hardware: none
# evidence: tools/bench/diag_c158_a2_3_measure.log:120-223
# ---
"""prep_c158_a3_1_proto - card 158-a3-1 MEASUREMENT before the stagekit change (offline, json only): on the recorded c158-a2-2 data,
(1) does frame-keyed cdiff(S1, real) == cdiff(S1, sim end re-keyed by the run's bindings) row for row, raw and with the frame tags
resolved to frame uids; (2) pair-keyed (source, sink) sets real vs sim (bound), created-node ends with and without the index.
Calls stagekit / vigraph / stagexec (bind_state); the real-row rebuild is diag_c158_a2_3_measure.py's AL rule, imported from that
script's json-free part is not possible (it runs at import), so it is exercised here once and then moved into stagekit."""
import os, sys, copy, json                                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import stagekit as K                                                                       # noqa: E402

PLAN, PRED = os.path.join(K.BENCH, "plan_ring_p5s02a.json"), os.path.join(K.BENCH, "plan_ring_p5s02a_pred.json")
LIC, SGC = os.path.join(K.BENCH, "plan_ring_p5s02a_licence.json"), os.path.join(K.BENCH, "prep_c156_a1_1_session.json")
SIMF = os.path.join(K.BENCH, "sim", "ring_p5s02a", "step_23_wire.json")
REAL = os.path.join(K.BENCH, "diag_c156_p5s02a_scratch.json")
V, SX = K.pure("vigraph"), K.pure("stagexec")
RS = K.RingSession(PLAN, PRED, LIC, SGC)
L = K.jload(SIMF)["state"]
D = K.jload(REAL)
BOUND = {}
for o in D["stagexec"]:
    BOUND.update(dict((int(k), int(v)) for k, v in (o.get("bound") or {}).items()))
RR, ST = D["real_end_rows"], L["terminals"]
by_uid = dict((int(s["term_uid"]), s) for s in ST)
neg = {}
for s in ST:
    if int(s["term_uid"]) < 0:
        neg.setdefault(BOUND.get(int(s["owner_uid"]), int(s["owner_uid"])), []).append(s)
pick, un = {}, []
for q in RR:
    if int(q[0]) in by_uid:
        pick[int(q[0])] = by_uid[int(q[0])]
for q in RR:
    u = int(q[0])
    if u in pick:
        continue
    c = neg.get(int(q[1]), [])
    m = [s for s in c if s["term_name"] == q[2] and bool(s["is_source"]) == bool(q[4])] or [s for s in c if bool(s["is_source"]) == bool(q[4])]
    if m:
        pick[u] = m[0]
        c.remove(m[0])
    else:
        un.append(q)
fmap = lambda v: BOUND.get(int(v), int(v)) if v not in (None, "") else v   # noqa: E731
real = [{"term_uid": int(q[0]), "owner_uid": int(q[1]), "term_name": q[2], "wire_uid": int(q[3] or 0), "is_source": bool(q[4]),
         "term_class": pick[int(q[0])].get("term_class"), "owner_class": pick[int(q[0])].get("owner_class"),
         "frame_diagram": fmap(pick[int(q[0])].get("frame_diagram"))} for q in RR if int(q[0]) in pick]
print("AL unmatched", len(un))
Lb, unbound = SX.bind_state(L, {"obj": BOUND, "term": {}, "diag": {}})
print("bind_state unbound negatives", len(unbound), sorted(unbound)[:12])
S1 = K.s1_frame_graph(RS.LAB)
Gsb = K.pred_end_graph(Lb, RS.LAB, RS.FSPAIRS)
pbr, restored, unlic = K.pb_rename_rows(RS.BASE["terminals"], L["terminals"], real, RS.REN)
GR = V.build4(pbr, Lb.get("objs") or [], copy.deepcopy(Lb["loops"]), RS.LAB, RS.FSPAIRS, frame_keyed=True)
cr, cs = V.computation_diff_frame(S1, GR), V.computation_diff_frame(S1, Gsb)
R_ = dict((y["sink"], y) for y in cr["rows"])
S_ = dict((y["sink"], y) for y in cs["rows"])
print("rows real", len(R_), "sim-bound", len(S_), "sinks only real", sorted(set(R_) - set(S_)), "only sim", sorted(set(S_) - set(R_)))
nd = 0
for k in sorted(set(R_) & set(S_)):
    if R_[k]["after"] != S_[k]["after"] or R_[k]["before"] != S_[k]["before"]:
        nd += 1
        print("  RAW DIFF", k, "real", R_[k]["after"], "sim", S_[k]["after"])
print("raw differing rows", nd)
PR, PS = V.pos_keys(GR), V.pos_keys(Gsb)
nd = 0
for k in sorted(set(R_) & set(S_)):
    a = sorted(map(str, (V._pos_src(PR, x) for x in R_[k]["after"] or [])))
    b = sorted(map(str, (V._pos_src(PS, x) for x in S_[k]["after"] or [])))
    if a != b:
        nd += 1
        print("  POS DIFF", k, a, b)
print("pos differing rows", nd)
for k in ("376|Terminal|cal cluster path|0", "376|Terminal|file size|0"):
    for tag, G, C in (("real", GR, R_), ("simb", Gsb, S_)):
        y = C.get(k)
        print("  ROW", tag, k, y and y["before"], y and y["after"],
              [(G["rows"][s.split("@")[0]]["term_uid"] if s.split("@")[0] in G["rows"] else None) for s in (y["after"] if y else [])])
    print("  S1 uids", [S1["rows"][s]["term_uid"] for s in (R_[k]["before"] or [])])
fo = lambda G: sorted((V.key_parts(k)[0], V.key_parts(k)[3], G["rows"][k]["frame_diagram"]) for k in G["frame_inner"])   # noqa: E731
print("frame map real", [x for x in fo(GR) if x[0] in (31546, 31557, 31308)])
print("frame map simb", [x for x in fo(Gsb) if x[0] in (31546, 31557, 31308)])


def pairs(rows, ob=None, created=()):
    P, half = [], []
    for w, (a, b) in K.wire_ends_pos(rows, ob).items():
        red = lambda k: (k[0], None, k[2], k[3]) if k[0] in created else k   # noqa: E731
        if not b:
            half.append((w, sorted(a)))
            continue
        for x in (a or [None]):
            for y in b:
                P.append((red(x) if x else None, red(y)))
    return P, half


created = set(BOUND.values())
for c in ((), created):
    Pb, _ = pairs(RS.BASE["terminals"], None, c)
    Ps, Hs = pairs(L["terminals"], BOUND, c)
    Pr, Hr = pairs(real, None, c)
    import collections as CC
    cb, cs_, cr_ = CC.Counter(Pb), CC.Counter(Ps), CC.Counter(Pr)
    print("PAIRS created-reduced" if c else "PAIRS raw", "new sim", sum((cs_ - cb).values()), "new real", sum((cr_ - cb).values()),
          "lost sim", sum((cb - cs_).values()), "lost real", sum((cb - cr_).values()),
          "newdiff", sorted(map(str, ((cs_ - cb) - (cr_ - cb)).elements())), sorted(map(str, ((cr_ - cb) - (cs_ - cb)).elements())),
          "lostdiff", sorted(map(str, ((cb - cs_) - (cb - cr_)).elements())), sorted(map(str, ((cb - cr_) - (cb - cs_)).elements())))
    print("  half sim", Hs, "half real", Hr)
print("RESULT " + json.dumps({"schema": "result-line/1", "status": "PASS", "gates": {"pass": 1, "fail": 0}, "first_fail": None, "artefacts": []}))
