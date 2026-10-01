r"""plan_ring_p3a_make_v3 - card 124-6 STEP 2 (offline, no LabVIEW; PD250(c)(d)): plan_ring_p3a_in_v3.json from v2 with ONE change -
`p3a_w_qr_x` (Q&R.x <- the count) takes its source by `frame: "False"` from TI1's inner face (was 'new:TI1.inner', which compiled to
the loop-tunnel `branch` and failed on two inner faces: result_124-3.json, stagexec route 19). With the 124-6 routes, rows 15/16 (the
register-inner-face groups) compile to connect_term_uid (R1/R2) and row 23 to case_frame_wire variant branch (R4, census {}).
Also writes the prediction file plan_ring_p3a_pred.json (beside the FINAL plan tools/bench/plan_ring_p3a.json, read by
stage_prerun X15 / census_predict and by the recipe): census per class (sampled rows from census_samples.json, the rest from the
model, each marked), the compiled op kinds, the end cdiff rows (== the P2b bed's 16), and the Error List prediction against the P2b
bed's errorlist_expected (54 items). PRIOR ART: plan_ring_p3a_make.py (v1 rows), plan_ring_p2b_make.py (pred layout).
PREDICTION: v3 == v2 except action 23's src; 25 actions; compiles to 21 ops incl. connect_term_uid x2, case_frame_wire x2.
    py tools/bgrun.py --material --max-min 3 --log tools/bench/plan_ring_p3a_make_v3.log -- py -u tools/bench/plan_ring_p3a_make_v3.py"""
import copy, hashlib, json, os, sys                                                # noqa: E401
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import protocol as P, stagexec as SX  # noqa: E401,E402
B = os.path.dirname(os.path.abspath(__file__))
J = lambda fn: json.load(open(os.path.join(B, fn), encoding="utf-8"))  # noqa: E731
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()  # noqa: E731
ok = []


def gate(name, c, det):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, json.dumps(det, default=str)[:700]), flush=True)


V2F, ELF = "plan_ring_p3a_in_v2.json", "errorlist_expected_D1_ring_p2b_20261001_140658.json"
gate("M0 inputs: v2 md5 5308f515, P2b errorlist_expected 54 items", md5(os.path.join(B, V2F)) == "5308f51512fe3b9cc19e33a6935e05c5"
     and J(ELF)["total"] == 54, (md5(os.path.join(B, V2F)), J(ELF)["total"]))
v2 = J(V2F)
v3 = copy.deepcopy(v2)
k = next(i for i, a in enumerate(v3["actions"]) if a["id"] == "p3a_w_qr_x")
v3["actions"][k]["src"] = {"uid": "new:TI1", "side": "inner", "frame": "False"}
v3["actions"][k]["why"] = ("x = the count (left value through the case); v3 (card 124-6, PD250(c)): addressed by frame 'False' on TI1's inner "
                           "face, already wired by its group -> case_frame_wire variant branch (R4, census {}, diag_c124_p3a_scratch.log:77,80)")
v3["goal"] = v2["goal"] + "; v3 (card 124-6): routes connect_term_uid (R1/R2) and case_frame_wire branch (R4)"
diff = [i for i, (a, b) in enumerate(zip(v2["actions"], v3["actions"])) if a != b]
gate("M1 v3 == v2 except action {0} (p3a_w_qr_x); 25 actions".format(k + 1), diff == [k] and len(v3["actions"]) == 25, diff)
ops = SX.compile_plan(v3)
kinds = [o["kind"] for o in ops]
cfw = [(o["frame"], o["variant"]) for o in ops if o["kind"] == "case_frame_wire"]
gate("M2 compile: 21 ops, connect_term_uid x2 (acts 15-17, 18-20), case_frame_wire [(True, new_wire), (False, branch)]",
     len(ops) == 21 and [o["acts"] for o in ops if o["kind"] == "connect_term_uid"] == [[15, 16, 17], [18, 19, 20]]
     and cfw == [("True", "new_wire"), ("False", "branch")], list(zip(kinds, [o["acts"] for o in ops])))
CS = J("census_samples.json")["ops"]
smp = lambda op_, v: CS[op_] and next(x["delta"] for x in CS[op_]["variants"] if x["name"] == v)  # noqa: E731
CW, CTU = smp("case_wired", "new_wire"), smp("connect_term_uid", "register_end_case_border")
CFN, CFB = smp("case_frame_wire", "new_wire"), smp("case_frame_wire", "branch")
SCAL = smp("create_primitive_nested:const_donor", "scalar")
census, src = {}, []


def add(d, why):
    src.append(why)
    for c, n in d.items():
        census[c] = census.get(c, 0) + n


add(CW, "case_wired new_wire (SAMPLED diag_c123_wired.log:88)")
add({c: 2 * n for c, n in CTU.items()}, "connect_term_uid x2 (SAMPLED diag_c124_p3a_scratch.log:53,61)")
add(CFN, "case_frame_wire new_wire p3a_w_true_pass (SAMPLED :71)")
add(CFB, "case_frame_wire branch p3a_w_qr_x (SAMPLED :77,80)")
add({c: 3 * n for c, n in SCAL.items()}, "const_donor scalar x3 KP1/KC1/K20 (SAMPLED stage_d1_ring_p2b.log:121)")
add({"DigitalNumericConstant": 1, "Wire": 1}, "MODEL const_on_term WK1: one wired constant (unsampled)")
add({"Wire": 3}, "MODEL const_sr x2 + const K20->Q&R.y: Wire +1 each (PD247(a) 'Measured per call ... Wire +1'; not a census sample)")
add({"Wire": 1}, "MODEL wire_sr LeftIn SP1L.inner -> Equal?.y: new wire (source unwired); wire_sr RightIn + cfw Equal?.x branch w3747: +0")
add({"OuterTerminal": 4, "InnerTerminal": 4}, "MODEL add_shift_reg x2: each register pair = 2 outer + 2 inner faces (UNMEASURED: 124-5 A1 logged Nodes only)")
SRC = ("LoopTunnel", "Wire", "WhileLoop", "Diagram", "SubVI", "Local", "ControlTerminal", "ArrayConstant", "DigitalNumericConstant",
       "CaseStructure", "Tunnel", "OuterTerminal", "InnerTerminal", "SelectorTunnel")
census = dict((c, census.get(c, 0)) for c in SRC)
gate("M3 census: Wire 11, DNC 4, CaseStructure 1, Diagram 2, Tunnel 1, SelectorTunnel 2, OuterTerminal 7, InnerTerminal 10, rest 0",
     census == {"LoopTunnel": 0, "Wire": 11, "WhileLoop": 0, "Diagram": 2, "SubVI": 0, "Local": 0, "ControlTerminal": 0,
                "ArrayConstant": 0, "DigitalNumericConstant": 4, "CaseStructure": 1, "Tunnel": 1, "OuterTerminal": 7,
                "InnerTerminal": 10, "SelectorTunnel": 2}, census)
EL, P2B = J(ELF), J("plan_ring_p2b_pred.json")
pel = {"bed_total": EL["total"], "predicted_total": EL["total"], "new_items_predicted": 0, "alternative_total": EL["total"] + 1,
       "base_file": "tools/bench/" + ELF,
       "derivation": "every sink P3a makes is wired: Wait (ms) input (1), Equal? x/y, the case selector, both register LEFT outer faces "
                     "initialised (const_sr), both RIGHT inner faces, TI1/TO1 in BOTH frames (False via Increment, True pass-through), "
                     "Increment x, Q&R x/y; unwired OUTPUTS (Wait's timer value, both Q&R outputs, the registers' right outer faces) "
                     "make no Error List item; no existing net is cut (branches only) => 0 new; alternative 55 if LabVIEW flags an "
                     "item the model does not see (pinned on the scratch, PD235(f))"}
rows = [{"id": a["id"], "donor_uid": a["donor"]["uid"], "canon": "I32", "class": a["class"]} for a in v3["actions"] if a.get("prim") == "const_donor"]
pred = {"schema": "ring-p3a-pred/1", "graph": v3["base"], "bed": "C:\\Program Files\\National Instruments\\LabVIEW 2026\\user.lib\\claudeDev\\D1_ring_p2b_20261001_140658.vi",
        "bed_md5": "652b1447ebbda761a7d5ba36455a0fa1", "bufnum_canon": "I32", "rows": rows, "census": census, "census_sources": src,
        "census_note": "UNPREDICTED overall by census_predict (rows without a sample rule); the scratch run measures it before the ONE launch (PD247(e))",
        "ops": kinds, "cdiff_rows": sorted(P2B["cdiff_rows"]), "errorlist": pel}
gate("M4 pred rows: 3 const_donor rows I32 (KP1 #249, KC1 #248, K20 #214); P2b cdiff rows 16", [r["donor_uid"] for r in rows] == [249, 248, 214]
     and len(pred["cdiff_rows"]) == 16, rows)
if all(c for _n, c in ok):
    json.dump(v3, open(os.path.join(B, "plan_ring_p3a_in_v3.json"), "w", encoding="utf-8"), indent=1)
    json.dump(pred, open(os.path.join(B, "plan_ring_p3a_pred.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p3a_in_v3.json + plan_ring_p3a_pred.json", flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
