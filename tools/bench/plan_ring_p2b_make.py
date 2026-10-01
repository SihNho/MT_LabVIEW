r"""plan_ring_p2b_make - card 122-6 (offline, no LabVIEW): the RING P2b plan (PD240(a)-(e), PD241(b), PD244(a)/(c)) from the graph of the
SAVED P2a bed (diag_c122_graph_p2a.json md5 3f6f5d36, diag_c122_route.py on a never-saved byte copy of D1_ring_p2a_20260928_191739.vi).
FIVE valued constants (donor copies of claudeDev\DonorRingConst_v0.vi, PD241(b): array constant instead of Initialize Array) each wired to ONE
NEW indicator born on it, all on FS1 frame diagram #4866 (PD244(c): the frame immediately before #686), outside every loop.
PRIOR ART (checked): plan_ring_p2a_make.py (graph-derived plan + pred file), plan_qrt_pool_in.json (create rows with prim + donor),
stagesim.py G46b (create ArrayConstant prim const_donor -> ControlTerminal indicator born_on {"uid": "new:CK1"}), stagexec.py
const_born_on / CONST_IND_ROUTE (gscript.create_indicator_on_const -> OpConstInd_v0), gscript.const_indicator_on_diagram (the same two calls).
No new op.
PREDICTION -> plan_ring_p2b_pred.json: 10 create rows (<= 15, PD240(e)); 5 new wires (one per constant->indicator), no existing wire changed;
census ControlTerminal +5, Wire +5, ArrayConstant +4, DigitalNumericConstant +1; cdiff == the P2a bed's 16 rows; Error List 54 -> 54 (PD240(d):
every new terminal wired, constants only); types Num/FrameIdx Array1D<I32>, TransPos/RotPos Array1D<DBL> (F1/F2), Latest I32 (F3).
    py tools/bgrun.py --material --max-min 3 --log tools/bench/plan_ring_p2b_make.log -- py -u tools/bench/plan_ring_p2b_make.py"""
import hashlib, json, os, sys                                                      # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P  # noqa: E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731
GF = "diag_c122_graph_p2a.json"
G, DON, P2A, TY = J(GF), J("diag_c122_donor.json"), J("plan_ring_p2a.json"), J("facts_c120_types.json")["terms"]
QRTW = J("facts_c120_qrtw.json")["G2_fs_frame_pos"]["FS1"]
P2AEND = J("stage_d1_ring_p2a.json")["ring_p2a"]["cdiff_rows"]
EL = J("errorlist_expected_D1_ring_p2a_20260928_191739.json")
FRAME, NEXTF = 4866, 686
LABELS = ("Num", "TransPos", "RotPos", "FrameIdx", "Latest")
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:1200]), flush=True)


T = G["terminals"]
gmd5 = md5(os.path.join(B, GF))
gate("M0 graph md5 == card input 3f6f5d36; graph bed == D1_ring_p2a_20260928_191739.vi md5 c22a473f",
     gmd5 == "3f6f5d36808cc205771a8349b5a737ff" and os.path.basename(G["vi"]) == "D1_ring_p2a_20260928_191739.vi" and G["md5"] == "c22a473f26ebcc67296d1c2441f8a47a",
     (gmd5, G["vi"], G["md5"]))
order = [u for _x, u in sorted(QRTW)]
fsit = {}
for r in T:
    if r["owner_class"] == "FlatSequenceInnerTunnel":
        fsit.setdefault(int(r["owner_uid"]), set()).add(int(r["frame_diagram"] or 0))
adj = lambda a, b: sorted(u for u, fr in fsit.items() if {a, b} <= fr)  # noqa: E731
A1, A2 = adj(1817, FRAME), adj(3121, 1817)
gate("M1 #{0} is an FS1 frame (review c122-route-s0 (a)): LIVE tunnel adjacency 3121-1817 {1} and 1817-{0} {2} in this bed's graph; owners tuple "
     "FlatSequenceFrame; x-order puts it immediately before #{3} (PD244(c))".format(FRAME, A2[:3], A1[:3], NEXTF),
     A1 and A2 and G["owners"].get(str(FRAME)) == ["FlatSequenceFrame", 0] and G["owners"].get(str(NEXTF)) == ["FlatSequenceFrame", 0]
     and FRAME in order and order.index(NEXTF) == order.index(FRAME) + 1, {"order": order, "adj_1817_4866": A1, "adj_3121_1817": A2})
loopd = set(int(L.get("body_diagram") or L.get("body") or 0) for L in G["loops"]) | set(int(k) for k, v in G["owners"].items() if v[0] in ("WhileLoop", "ForLoop"))
gate("M2 #{0} is not a loop body (none of the five objects lands in a loop)".format(FRAME), FRAME not in loopd, sorted(loopd)[:30])
cts = [r for r in T if r.get("term_class") == "ControlTerminal" or r["owner_class"] == "ControlTerminal"]
used = sorted(set(r["term_name"] for r in cts) & set(LABELS))
gate("M3 none of the five labels is already on the panel ({0} panel terminals read; PD240(a): a clash is a plan FAIL)".format(len(cts)), not used and len(cts) > 0, used)
dpath = DON["path"]
gate("M4 donor DonorRingConst_v0.vi md5 == record == card input d8dc3013; classes dbl_20/i32_20 ArrayConstant, i32 DigitalNumericConstant",
     os.path.exists(dpath) and md5(dpath) == DON["md5"] == "d8dc30136c197bef836cd4622bbce61d"
     and DON["classes"] == {"dbl_20": "ArrayConstant", "i32_20": "ArrayConstant", "i32": "DigitalNumericConstant"}, DON)
canon = {"F1": TY["F1"]["types"]["canon"], "F2": TY["F2"]["types"]["canon"], "F3": TY["F3"]["types"]["canon"]}
gate("M5 F-types: F1 #30117 DBL, F2 #4580 DBL, F3 #637 i I32 (facts_c120_types.json)", canon == {"F1": "DBL", "F2": "DBL", "F3": "I32"}, canon)
ROWS = [  # label, donor key, const class, canon (from the F-types), value (PD240(b))
    ("Num", "i32_20", "ArrayConstant", "Array1D<" + canon["F3"] + ">", [-1] * 20, "I32[20] -1: nothing published in any slot (PD240(a)/(b))"),
    ("TransPos", "dbl_20", "ArrayConstant", "Array1D<" + canon["F1"] + ">", [0.0] * 20, "DBL[20] 0.0 = F1 #30117 Value type (PD240(a)/(b))"),
    ("RotPos", "dbl_20", "ArrayConstant", "Array1D<" + canon["F2"] + ">", [0.0] * 20, "DBL[20] 0.0 = F2 #4580 Value type (PD240(a)/(b))"),
    ("FrameIdx", "i32_20", "ArrayConstant", "Array1D<" + canon["F3"] + ">", [-1] * 20, "I32[20] -1 = F3 #637 i type (PD240(a)/(b))"),
    ("Latest", "i32", "DigitalNumericConstant", canon["F3"], -1, "I32 -1 'nothing published' (PD240(b))"),
]
acts = []
for k, (lab, key, cls, cn, val, why) in enumerate(ROWS):
    acts.append({"op": "create", "id": "p2b_c_" + lab, "class": cls, "diagram": FRAME, "as": "K{0}".format(k + 1), "pos": [1260, 60 + 70 * k],
                 "prim": "const_donor", "donor": {"donor": dpath, "uid": int(DON[key])}, "terminals": [{"name": "", "is_source": True}],
                 "why": "PD240(b)/PD241(b): valued constant for {0}: {1}; donor #{2} ({3})".format(lab, why, DON[key], key)})
    acts.append({"op": "create", "id": "p2b_i_" + lab, "class": "ControlTerminal", "diagram": FRAME, "as": "I{0}".format(k + 1), "label": lab, "indicator": True,
                 "born_on": {"uid": "new:K{0}".format(k + 1)},
                 "why": "PD240(a)/(c): indicator {0!r} ({1}) born on its constant on FS1 frame #{2}; one writer later (P3), readers by local (P4)".format(lab, cn, FRAME)})
gate("M6 rows {0} <= 15 (PD240(e)): 5 constants + 5 indicators, every create on #{1}".format(len(acts), FRAME),
     len(acts) == 10 and all(a["diagram"] == FRAME for a in acts), [a["id"] for a in acts])
pel = {"bed_total": EL["total"], "predicted_total": EL["total"], "new_items_predicted": 0, "alternative_total": EL["total"] + 1,
       "derivation": "PD240(d): every new terminal is wired (constant -> indicator), constants only, no existing net touched => 0 new items"}
pred = {"schema": "ring-p2b-pred/1", "graph": {"path": "tools/bench/" + GF, "md5": gmd5}, "bed": G["vi"], "bed_md5": G["md5"], "frame": FRAME,
        "rows": [{"label": r[0], "donor_key": r[1], "donor_uid": int(DON[r[1]]), "class": r[2], "canon": r[3], "value": r[4]} for r in ROWS],
        "census": {"ControlTerminal": 5, "Wire": 5, "ArrayConstant": 4, "DigitalNumericConstant": 1},
        "cdiff_rows": sorted(P2AEND), "errorlist": pel, "ops": ["create"] * len(acts), "donor": {"path": dpath, "md5": DON["md5"]}}
plan = {"schema": "stageplan/1", "stage": "ring_p2b",
        "goal": "RING P2b (PD240-244, card 122-6): on the SAVED P2a bed {0} add Num/TransPos/RotPos/FrameIdx/Latest indicators, each born on a valued "
                "donor constant (PD241(b)), all on FS1 frame #{1} (before #{2}); no existing net touched".format(os.path.basename(G["vi"]), FRAME, NEXTF),
        "base": {"path": "tools/bench/" + GF, "md5": gmd5}, "context": P2A["context"], "actions": acts, "open_rows": P2A["open_rows"]}
if all(c for _n, c in ok):
    json.dump(plan, open(os.path.join(B, "plan_ring_p2b_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump(pred, open(os.path.join(B, "plan_ring_p2b_pred.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p2b_in.json ({0} actions) + plan_ring_p2b_pred.json".format(len(acts)), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
