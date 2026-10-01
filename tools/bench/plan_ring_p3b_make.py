r"""plan_ring_p3b_make - card 126-5 (OFFLINE, no LabVIEW, no COM): ring P3b plan INPUT on the REAL P3a graph.
Design of record: PD246(c) A1 (Flat Sequence of 3 frames in the new-frame case frame: [Num(i)=-1] -> [IMAQ Copy + TransPos/
RotPos/FrameIdx at i] -> [Num(i)=BufNum, Latest=BufNum]), A2 (local read -> Replace Array Subset -> local write), PD254(d)
(frame 3 takes Num by a SECOND local read), PD241(d) (Copy Src = #6810 Image Out t6865; pool refnums out of For #23093 by a
NEW output tunnel, route nested), PD247(b) (the For exit by route nested indexes). ring_p3_steps.md:26 lists the actions.
WHAT EXISTED FIRST: plan_ring_p3a_make_v3b.py (term_class from MEASURED rows), selftest_fs_c126.py (FS rows as stageplan/1),
stagesim FS model (card 126-3), census_samples.json. Nothing here edits stagesim/stagexec/gscript.
Every row's `why` starts 'ROUTE <route> | <MEASURED|PRECEDENT|UNMEASURED|HELD> | ...'.
CARD 126-8 RERUN (PD255(b), PD256(a)-(e)): rows are V.dedupe_rows'd at load (gate nonidentical == []; review
archive/peer/2026-10-01-c126-7-t644.md:87-96); the 13 crossings carry 126-6's census_samples.json connect_term_uid variant
(MEASURED where 126-4/126-6 ran that exact form, UNMEASURED for a 2nd+ sink into a frame the same source already entered);
the TransPos/RotPos source crossings are HELD (PD256(e)) - kept OUT of `actions`, bodies in plan_ring_p3b_rows.json `held_rows`;
a wire_remove_loose_ends row after every crossing + one for P3a's w27378 (PD255(b)/PD256(b)) - stageplan/1 has NO such op
(docs/protocol/stageplan.json:252-263) and stagexec/stagesim no executor, so they go to plan_ring_p3b_rows.json `post_rows`.
STEP 1 (diag_c126_8_orig.log): the ORIGINAL's #2626 takes element <- #30117 Value and element <- #4580 Value (PD238(c) holds).
PREDICTION: 45 action rows = 22 create + 12 same-frame wires + 11 crossings (7 MEASURED, 4 UNMEASURED), 2 HELD aside; 14 RLE
post rows; validates; compiles; replay A (34 non-crossing rows) no error, end cdiff == P3a's 16 rows; replay B (all 45) STOPS at
the first crossing p3b_x_i_f1 with stagesim's 'a border needs a tunnel' (no stagesim model for a border-crossing connect:
opmodels connect_from_wire same_diagram true); re-created nets (126-6 B1/B2) carry old terms + 1.
CARD 127-2 RERUN (PD257(a)-(d)): the 2 HELD rows are RELEASED into the actions (TransPos <- #30117 Value, RotPos <- #4580
Value, PD257(a)); the 14 wire_remove_loose_ends rows move INTO the plan (stageplan/1 op, card 127-2): w27378 first, then one
`of` each crossing right after it (PD255(b)/256(b)); the 4 2nd+-sink rows are tagged PROVISIONAL (PD257(d), pending card
127-1); stagexec compiles every crossing to connect_term_uid (fs_border / fs_border_inner_branch) and stagesim models them.
PREDICTION (127-2): 61 actions = 22 create + 12 same-frame wires + 13 crossings (9 MEASURED, 4 PROVISIONAL) + 14 RLE;
validates; compiles (13 connect_term_uid: 9 fs_border + 4 fs_border_inner_branch; 14 wire_remove_loose_ends); replay A
(34 non-crossing rows) end cdiff == P3a's 16 rows; replay B (all 61) END TO END, every fs_border census == its variant's
delta, end cdiff == P3a's 16 rows (P3b closes none of them: they are QRT's); every old sink of a re-created net still on the
source's (new) net.
CARD 127-3 RERUN (PD258(a)(c)): the 4 inner-face rows are MEASURED; + crossing p3b_x_err_in (IMAQ Copy error in <- #6810 error
out, w653 re-created, #649 kept) + its RLE; the Unbundle By Name / Select / const / 4 wires of PD258(c) are HELD (UNMEASURED).
PREDICTION (127-3): 63 actions = 22 create + 12 wires + 14 crossings (all MEASURED) + 15 RLE; compiles 10 fs_border + 4 inner;
replay B END TO END, end cdiff 16 == P3a's; M11 keeps w653's old sink #649.
CARD 128-5 RERUN (PD261(a), PD262(b)): the HELD guard rows become actions in f2 (Unbundler + Select from claudeDev vi.lib byte
copies, I32 -1 const; CP1 error out -> UB1 cluster (fs_frame_to_frame), UB1.element#0 -> SEL1.s, KM3 -> SEL1.t, SEL1 -> RAN3
new element; BufNum crossing retargeted to SEL1.f; Latest = BufNum unchanged); census_samples pin 205a7f23.
PREDICTION (128-5): 70 actions = 25 create + 16 wires + 14 crossings + 15 RLE; compiles (crossings as 127-3); replay A 41 rows
no error; replay B END TO END; end cdiff == P3a's 16 rows; M11 holds.
    py tools/bgrun.py --material --max-min 5 --log tools/bench/plan_ring_p3b_make_c127_3.log -- py -u tools/bench/plan_ring_p3b_make.py"""
import collections, copy, hashlib, json, os, shutil, sys, tempfile          # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX, vigraph as V          # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()               # noqa: E731
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:900]), flush=True)


GR, P3A = "tools/bench/graph_ring_p3a_20261001_190155.json", os.path.join(B, "plan_ring_p3a.json")
PINS = {GR: "2fa6ce0c3e8a3014fa916085cb852f68", "tools/bench/plan_ring_p3a.json": "234efaaa890c5d2ac255d746048ddb84",
        "tools/bench/ring_p3_steps.md": "6617a5e921b5671e6362da3848fb14cf",
        "tools/bench/census_samples.json": "205a7f23802f41342ed25d06dc212bc5",   # card 128-5: re-pinned after 128-4's vilib_donor section
        "tools/bench/diag_c126_7_facts2.py": "30587ab3652bda5923de50360d66c812",
        "archive/peer/2026-10-01-c126-7-t644.md": "2c2672260a0ca01c21e18f7d065d3edc"}
def md5_pre_sameline(p):
    """card 127-2: guard_peer appends 'SAME-ROW:' release lines to the cited review on every failed rerun of this script
    (archive/peer/2026-10-01-c126-7-t644.md:98-102), so the review is pinned on its text BEFORE the first such line."""
    b = open(p, "rb").read()
    k = b.find(b"\nSAME-ROW: ")
    return hashlib.md5(b if k < 0 else b[:k].rstrip(b"\r\n") + b"\n").hexdigest()


got = dict((p, (md5_pre_sameline if p.startswith("archive/peer/") else md5)(os.path.join(ROOT, p))) for p in PINS)
gate("M0 card inputs md5 == task_126-8.json (+ 126-5's P3a plan / steps pins)", got == PINS, got)
print("  FACT tool md5: stagesim {0} stagexec {1} vigraph {2}".format(*(md5(os.path.join(ROOT, "tools", f)) for f in
      ("stagesim.py", "stagexec.py", "vigraph.py"))), flush=True)
G = json.load(open(os.path.join(ROOT, GR), encoding="utf-8"))
T, DD = V.dedupe_rows(G["terminals"])                                      # card 126-8 / PD256(d): dedupe at load
own = G["owners"]
gate("M0b V.dedupe_rows at load: nonidentical == [] (OpAllTerms_v1's byte-identical duplicates only)", DD["nonidentical"] == [],
     dict(DD, raw=len(G["terminals"]), kept=len(T)))
cls_of = dict((int(o["uid"]), o["class"]) for o in G["objs"])
row = lambda u, n: [r for r in T if r["owner_uid"] == u and r["term_name"] == n]               # noqa: E731
tab = lambda u: [{"name": r["term_name"], "is_source": bool(r["is_source"]), "term_class": r["term_class"]} for r in T if r["owner_uid"] == u]  # noqa: E731
qr = row(27373, "x-y*floor(x/y)")
facts = {"case": (cls_of.get(22694), own.get("27219"), own.get("27232"), own.get("22694")),
         "i": [(r["term_uid"], r["wire_uid"], r["frame_diagram"]) for r in qr],
         "6810": [(r["term_uid"], r["term_name"], r["frame_diagram"]) for r in row(6810, "current image number") + row(6810, "Image Out")],
         # run 1 (plan_ring_p3b_make.log:4): t644 has TWO rows in the read (vigraph.dedupe_rows' case) - the gate keys on the
         # distinct (term_uid, frame) pair and records the duplicate count instead of assuming one row
         "vals": sorted(set((r["term_uid"], r["frame_diagram"]) for r in row(30117, "Value") + row(4580, "Value") + [x for x in T if x["term_uid"] == 644]),
                        key=lambda t: (t[0] != 30145, t[0] != 4728)),
         "t644_rows": len(set(json.dumps(x, sort_keys=True) for x in T if x["term_uid"] == 644)),
         "pool": [(r["term_uid"], r["wire_uid"], r["frame_diagram"]) for r in row(23099, "New Image")]}
gate("M1 bound uids on the P3a graph: case #22694 frames 27219 False/27232 on 639; i = #27373 remainder UNWIRED on 27219; "
     "#6810 t6897/t6865, #30117/#4580 Value, #637 i t644 on 639; #23099 New Image t23289 unwired on For body 23169",
     facts["case"] == ("CaseStructure", ["CaseStructure", 22694], ["CaseStructure", 22694], ["Diagram", 639])
     and facts["i"] == [(qr[0]["term_uid"], 0, 27219)] and facts["6810"] == [(6897, "current image number", 639), (6865, "Image Out", 639)]
     and facts["vals"] == [(30145, 639), (4728, 639), (644, 639)] and facts["t644_rows"] == 1 and facts["pool"] == [(23289, 0, 23169)], facts)
LAB = ("Num", "TransPos", "RotPos", "FrameIdx", "Latest")
ct = collections.Counter(r["term_name"] for r in T if r["term_class"] == "ControlTerminal" and r["term_name"] in LAB)
gate("M2 each local's label is ONE panel terminal (a local binds by label, PD240(a))", all(ct[x] == 1 for x in LAB), dict(ct))
RAS, IA = tab(29157), tab(3163)
gate("M3 $work donors MEASURED rows: Replace Array Subset #29157 (GrowableFunction, 1-D: array/index/new element/subarray -> "
     "output array) and Index Array #3163 (IndexArray, array/index -> element)",
     cls_of.get(29157) == "GrowableFunction" and sorted(t["name"] for t in RAS) == ["array", "index", "new element/subarray", "output array"]
     and cls_of.get(3163) == "IndexArray" and sorted(t["name"] for t in IA) == ["array", "element", "index"], (RAS, IA))
H = json.load(open(os.path.join(B, "graph_harness_copyloop_c95.json"), encoding="utf-8"))
CP = [{"name": r["term_name"], "is_source": bool(r["is_source"]), "term_class": r["term_class"]} for r in H["terminals"] if r["owner_uid"] == 11]
gate("M4 IMAQ Copy terminal table MEASURED (graph_harness_copyloop_c95.json SubVI #11, 8 rows)",
     len(CP) == 8 and set(t["name"] for t in CP) >= {"Image Src", "Image Dst", "Image Dst Out", "error in (no error)", "error out"}, CP)

CLAUDE = r"C:\Program Files\National Instruments\LabVIEW 2026\user.lib\claudeDev"
IMAQ_COPY = r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb\IMAQ Copy"
R_FS = "fs_create | MEASURED | PD246(c) A1 | diag_c125_5_fsscr.log:27 (FS on this same #27219 of a P3a copy)"
R_FR = "fs_frame | MEASURED | PD246(c) A1 | diag_c125_5_fsscr.log:32 (add(0,T) new at 1, add(1,T) new at 2)"
R_K = "primitive const_donor | MEASURED | PD238(c) Num(i)=-1 | const in a FS frame: diag_c125_5_fsscr.log:41-47 (C-3a); I32 -1 = DonorRingConst_v0 #249 (PD247(a))"
R_LR = "local_read (create_local_read + move_in) | PRECEDENT | PD246(c) A2 | run on loop body #639 (plan_l2a3_in.json:16); placement in a FS frame never run"
R_LW = "local_write (create_local_write -> dest diagram) | PRECEDENT | PD246(c) A2 | stagexec.py:206 route; placement in a FS frame never run"
R_RAS = "primitive $work donor #29157 | PRECEDENT | PD246(c) A2 Replace Array Subset | route measured in P3a (stage_d1_ring_p3a.log, Equal?/Increment/Q&R); class GrowableFunction never copied: census UNPREDICTED"
R_IA = "primitive $work donor #3163 | PRECEDENT | PD246(d) Index Array(pool, i) | route as P3a; class IndexArray never copied: census UNPREDICTED"
R_CP = "subvi (drop_subvi llb member) | PRECEDENT | PD241(d) IMAQ Copy | IMAQ Create llb member in For body (diag_c118_p1b_plan.json:8); path docs/NAMES.md:967"
R_W = "connect same-diagram (connect_nested_v1) | PRECEDENT | {0} | same-frame wire, as p3a_w_k20 in case frame 27219; inside a FS frame never run"
R_X = "connect_term_uid ACROSS {0} | {3} | {1} | {2}"                     # card 126-8: status is per row (126-6 variants)
CS = "census_samples.json connect_term_uid "
V_Q1 = CS + "case_frame_to_fs_frame (diag_c126_4_fs.log:53)"
V_Q3 = CS + "case_frame_to_fs_frame_branch: a NEW FS outer tunnel per frame (diag_c126_4_fs.log:57)"
V_B12 = CS + "loop_body_wired_src_to_fs_frame_in_case (diag_c126_6_cross.log:49,60): source net RE-CREATED (PD256(c))"
V_B3 = CS + "for_body_unwired_src_to_fs_frame_multi_border (diag_c126_6_cross.log:77-78): While tunnel IndexMode 0"
V_SAME = "PD257(d)/PD258(a) INNER-FACE branch of the entry FS tunnel (census {} n=3, diag_c127_1_fsinner.log:81-109)"
INNER = lambda a: "INNER-FACE" in a["why"]                                 # noqa: E731 - card 127-3: no longer PROVISIONAL
A = [{"op": "create", "id": "p3b_fs", "class": "FlatSequence", "as": "FS1", "diagram": 27219, "pos": [200, 40], "why": "ROUTE " + R_FS},
     {"op": "create", "id": "p3b_fr2", "class": "FlatSequenceFrame", "diagram": "new:FS1.f0", "why": "ROUTE " + R_FR},
     {"op": "create", "id": "p3b_fr3", "class": "FlatSequenceFrame", "diagram": "new:FS1.f1", "why": "ROUTE " + R_FR}]
loc = lambda i, nm, lab, f, mode, x: {"op": "create", "id": i, "class": "Local", "diagram": "new:FS1.f{0}".format(f), "as": nm,  # noqa: E731
                                      "label": lab, "mode": mode, "pos": [x, 40 + 60 * len(A) % 400],
                                      "terminals": [{"name": lab, "is_source": mode == "read", "term_class": "Terminal"}],
                                      "why": "ROUTE " + (R_LR if mode == "read" else R_LW)}
prim = lambda i, nm, f, donor, terms, why: {"op": "create", "id": i, "class": cls_of[donor], "diagram": "new:FS1.f{0}".format(f),  # noqa: E731
                                            "as": nm, "pos": [120, 40 + 60 * len(A) % 400],
                                            "prim": "Replace Array Subset" if donor == 29157 else "Index Array",
                                            "donor": {"donor": "$work", "uid": donor}, "terminals": copy.deepcopy(terms), "why": "ROUTE " + why}
w = lambda i, s, d, why: {"op": "wire", "id": i, "src": s, "dst": d, "why": "ROUTE " + why}                  # noqa: E731
# frame 1 (f0): Num(i) = -1
A += [loc("p3b_lr_num1", "LRN1", "Num", 0, "read", 20), prim("p3b_ras_num1", "RAN1", 0, 29157, RAS, R_RAS),
      {"op": "create", "id": "p3b_k_m1", "class": "DigitalNumericConstant", "diagram": "new:FS1.f0", "as": "KM1", "pos": [60, 160],
       "prim": "const_donor", "donor": {"donor": CLAUDE + r"\DonorRingConst_v0.vi", "uid": 249},
       "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}], "why": "ROUTE " + R_K},
      loc("p3b_lw_num1", "LWN1", "Num", 0, "write", 220)]
# frame 2 (f1): IMAQ Copy into Img(i) + TransPos / RotPos / FrameIdx at i
A += [prim("p3b_ia", "IA1", 1, 3163, IA, R_IA),
      {"op": "create", "id": "p3b_copy", "class": "SubVI", "diagram": "new:FS1.f1", "as": "CP1", "pos": [160, 40], "subvi_path": IMAQ_COPY,
       "terminals": copy.deepcopy(CP), "why": "ROUTE " + R_CP}]
for lab, nm in (("TransPos", "T"), ("RotPos", "R"), ("FrameIdx", "F")):
    A += [loc("p3b_lr_" + lab.lower(), "LR" + nm + "1", lab, 1, "read", 20), prim("p3b_ras_" + lab.lower(), "RA" + nm + "1", 1, 29157, RAS, R_RAS),
          loc("p3b_lw_" + lab.lower(), "LW" + nm + "1", lab, 1, "write", 220)]
# frame 3 (f2): Num(i) = BufNum (SECOND local read, PD254(d)), Latest = BufNum
A += [loc("p3b_lr_num3", "LRN3", "Num", 2, "read", 20), prim("p3b_ras_num3", "RAN3", 2, 29157, RAS, R_RAS),
      loc("p3b_lw_num3", "LWN3", "Num", 2, "write", 220), loc("p3b_lw_latest", "LWL1", "Latest", 2, "write", 220)]
# card 128-5, PD258(c) + PD261(a) + PD262(b): the error GUARD in frame f2 (where Num(i) is written): Unbundler (vi.lib byte copy
# DonorErrSel_ErrToWarning.vi #157) + Select (DonorErrSel_MergeErrors.vi #529) + I32 -1 (DonorRingConst_v0 #249). Terminal names
# in READ ORDER and term_class from 128-2's measured creates (diag_c128_2_donors.log:57 Unbundler census Terminal 4; :62 Select
# census ParameterTerminal 4). The Unbundler's 3 outputs read 'element' until wired: element#0 = status (:83, PD262(b)).
R_GD = "primitive vilib_donor {0} | MEASURED | PD261(a) guard {1} | create_primitive_nested on a claudeDev byte copy, diag_c128_2_donors.log:{2}"
UNB_T = [{"name": "cluster", "is_source": False, "term_class": "Terminal"}] + [{"name": "element", "is_source": True, "term_class": "Terminal"}] * 3
SEL_T = [{"name": "s? t:f", "is_source": True, "term_class": "ParameterTerminal"}] + \
        [{"name": n, "is_source": False, "term_class": "ParameterTerminal"} for n in ("f", "s", "t")]
A += [{"op": "create", "id": "p3b_ub_status", "class": "Unbundler", "diagram": "new:FS1.f2", "as": "UB1", "pos": [60, 120], "prim": "Unbundle",
       "donor": {"donor": CLAUDE + r"\DonorErrSel_ErrToWarning.vi", "uid": 157}, "terminals": copy.deepcopy(UNB_T),
       "why": "ROUTE " + R_GD.format("DonorErrSel_ErrToWarning #157", "Unbundle (status)", "56-58,83")},
      {"op": "create", "id": "p3b_sel", "class": "Function", "diagram": "new:FS1.f2", "as": "SEL1", "pos": [120, 120], "prim": "Select",
       "donor": {"donor": CLAUDE + r"\DonorErrSel_MergeErrors.vi", "uid": 529}, "terminals": copy.deepcopy(SEL_T),
       "why": "ROUTE " + R_GD.format("DonorErrSel_MergeErrors #529", "Select", "61-63")},
      {"op": "create", "id": "p3b_k_m3", "class": "DigitalNumericConstant", "diagram": "new:FS1.f2", "as": "KM3", "pos": [60, 200],
       "prim": "const_donor", "donor": {"donor": CLAUDE + r"\DonorRingConst_v0.vi", "uid": 249},
       "terminals": [{"name": "", "is_source": True, "term_class": "Terminal"}], "why": "ROUTE " + R_K + " (guard t = -1)"}]
NC = len(A)
A += [w("p3b_w_n1_arr", "new:LRN1.value", "new:RAN1.array", R_W.format("PD246(c) A2 frame 1")),
      w("p3b_w_m1_new", "new:KM1.value", "new:RAN1.new element/subarray", R_W.format("PD238(c) Num(i) = -1")),
      w("p3b_w_n1_out", "new:RAN1.output array", "new:LWN1.value", R_W.format("PD246(c) A2 frame 1")),
      w("p3b_w_ia_dst", "new:IA1.element", "new:CP1.Image Dst", R_W.format("PD238(c) IMAQ Copy Dst = Img(i)"))]
for nm in ("T", "R", "F"):
    A += [w("p3b_w_{0}_arr".format(nm.lower()), "new:LR{0}1.value".format(nm), "new:RA{0}1.array".format(nm), R_W.format("PD246(c) A2 frame 2")),
          w("p3b_w_{0}_out".format(nm.lower()), "new:RA{0}1.output array".format(nm), "new:LW{0}1.value".format(nm), R_W.format("PD246(c) A2 frame 2"))]
A += [w("p3b_w_n3_arr", "new:LRN3.value", "new:RAN3.array", R_W.format("PD254(d) frame 3 second Num read")),
      w("p3b_w_n3_out", "new:RAN3.output array", "new:LWN3.value", R_W.format("PD246(c) A2 frame 3"))]
# card 128-5 guard wires (PD261(a) form C1, measured as 5 wires all Is Broken? False, diag_c128_2_donors.log:80-99)
A += [w("p3b_w_err_ub", "new:CP1.error out", "new:UB1.cluster",
        "fs_frame_to_frame (f1 -> f2) | MEASURED | PD258(c) IMAQ Copy error out -> guard | stagesim FS_MEASURED; diag_c128_2_donors.log:80-83"),
      w("p3b_w_ub_sel", "new:UB1.element#0", "new:SEL1.s", R_W.format("PD262(b) s = status (element#0)")),
      w("p3b_w_m3_sel", "new:KM3.value", "new:SEL1.t", R_W.format("PD261(a) t = -1")),
      w("p3b_w_sel_n3", "new:SEL1.s? t:f", "new:RAN3.new element/subarray", R_W.format("PD258(c) element = status ? -1 : BufNum"))]
NW = len(A)
I = {"uid": 27373, "term": "x-y*floor(x/y)"}
A += [w("p3b_x_i_f1", I, "new:RAN1.index", R_X.format("FS border (case frame 27219 -> FS f0)", "PD246(c)(d) i = count mod 20", V_Q1, "MEASURED")),
      w("p3b_x_i_f3", I, "new:RAN3.index", R_X.format("FS border (27219 -> f2), source already wired", "PD246(c) i", V_Q3, "MEASURED"))]
for k, tgt in enumerate(("IA1", "RAT1", "RAR1", "RAF1")):
    A += [w("p3b_x_i_" + tgt.lower(), I, "new:{0}.index".format(tgt), R_X.format(
        "FS border (27219 -> f1)" + (", 1st sink of i into f1" if k == 0 else ", BRANCH into f1 already entered"), "PD246(c) i",
        V_Q3 if k == 0 else V_SAME, "MEASURED"))]
TWO = "case border (639 -> 27219) + FS border (-> {0})"
A += [w("p3b_x_bn_n3", {"uid": 6810, "term": "current image number"}, "new:SEL1.f",   # card 128-5: BufNum -> Select.f (PD258(c))
        R_X.format(TWO.format("f2"), "PD238(c)/PD258(c) Select f = BufNum; new sink on w3747 only (PD241(d))", V_B12 + " B1 exact", "MEASURED")),
      w("p3b_x_bn_latest", {"uid": 6810, "term": "current image number"}, "new:LWL1.value",
        R_X.format(TWO.format("f2"), "PD238(c) Latest = BufNum", V_SAME, "MEASURED")),
      w("p3b_x_img_src", {"uid": 6810, "term": "Image Out"}, "new:CP1.Image Src",
        R_X.format(TWO.format("f1"), "PD241(d) Src = #6810 Image Out t6865 (w3040, 0 sinks)", V_B12 + " (same form, other terminal)", "MEASURED")),
      # PD257(a): RELEASED (the original's #2626 takes #30117 / #4580 Value, diag_c126_8_orig.log:3-8,45-48)
      w("p3b_x_trans", {"uid": 30117, "term": "Value"}, "new:RAT1.new element/subarray",
        R_X.format(TWO.format("f1"), "PD238(c) TransPos(i) = #30117 Value t30145", V_B12 + " (form) | PD257(a) RELEASED", "MEASURED")),
      w("p3b_x_rot", {"uid": 4580, "term": "Value"}, "new:RAR1.new element/subarray",
        R_X.format(TWO.format("f1"), "PD238(c) RotPos(i) = #4580 Value t4728", V_B12 + " (form) | PD257(a) RELEASED", "MEASURED")),
      w("p3b_x_fidx", {"uid": 639, "term_uid": 644}, "new:RAF1.new element/subarray",
        R_X.format(TWO.format("f1"), "PD240(a) FrameIdx(i) = #637 i t644", V_B12 + " B2 exact", "MEASURED")),
      w("p3b_x_pool", {"uid": 23099, "term": "New Image"}, "new:IA1.array",
        R_X.format("For #23093 exit (indexing) + FS2/FS1 + #637 + case + FS", "PD241(d)/PD247(b) pool refnums, route nested",
                   V_B3 + " B3 exact", "MEASURED")),
      # card 127-3, PD258(c): IMAQ Copy error in <- #6810 error out t6924 (w653 -> LoopTunnel #649 on #639 today; old sink kept, M11)
      w("p3b_x_err_in", {"uid": 6810, "term": "error out"}, "new:CP1.error in (no error)",
        R_X.format(TWO.format("f1"), "PD258(c) Copy runs after #6810, upstream error skips it; #649 kept (PD256(c))",
                   V_B12 + " (same form, error net w653)", "MEASURED"))]
# card 127-3, PD258(c) HELD (UNMEASURED: no donor for NamedUnbundler / Select in the OpPrimCopyNested_v0 registry
# (facts_c100_oplabels.json donors = Max & Min, Wait (ms)); no recorded graph holds an error-cluster Unbundle By Name or a Select
# (diag_c127_3_facts.log); kept OUT of `actions` like 126-8's held rows, bodies in plan_ring_p3b_rows.json `held_rows`)
HELD = []        # card 128-5: the 127-3 HELD guard rows are now actions (above), from 128-2's measured form C1
NX = [a["id"] for a in A[NW:]]
# PD255(b)/PD256(b): wire_remove_loose_ends on P3a's w27378 first, then one `of` EVERY crossing right after it (stageplan/1
# op since card 127-2)
RLE_R = "wire_remove_loose_ends | MEASURED | gscript.py:4972 OpWireRemoveLooseEnds_v0; diag_c126_4_op.log:52-60; diag_c126_6_cross.log:61-65"
POST = [{"op": "wire_remove_loose_ends", "id": "p3b_rle_w27378", "wire_uid": 27378,
         "why": "ROUTE " + RLE_R + " | PD253(d)/PD255(b) P3a stub w27378 (Error List 55 -> 54)"}]
for xid in NX:
    POST.append({"op": "wire_remove_loose_ends", "id": "p3b_rle_" + xid[6:], "of": xid,
                 "why": "ROUTE " + RLE_R + " | PD256(b) every wire of crossing " + xid})
XA = A[NW:]
A = POST[:1] + A[:NW] + [r for x, p in zip(XA, POST[1:]) for r in (x, p)]           # RLE right after each crossing
NC, NW = NC + 1, NW + 1                                                              # (w27378's row is action 1)
p3a = json.load(open(P3A, encoding="utf-8"))
plan = {"schema": "stageplan/1", "stage": "ring_p3b",
        "goal": "RING P3b plan INPUT (cards 126-5/126-8/127-2; PD246(c) A1/A2, PD254(d), PD241(d), PD256, PD257): slot writes in a 3-frame Flat Sequence on case #22694 False frame 27219 of the P3a bed",
        "base": {"path": GR, "md5": PINS[GR]}, "context": dict(p3a["context"]), "open_rows": copy.deepcopy(p3a["open_rows"]), "actions": A}
v = P.validate_obj(plan)
opc = collections.Counter("x" if a["id"] in NX else a["op"] for a in A)
gate("M5 plan validates as stageplan/1; 70 rows = 25 create + 16 in-FS wires (12 + 4 guard) + 14 crossings + 15 wire_remove_loose_ends "
     "(w27378 first, one `of` right after each crossing); every why has a ROUTE tag",
     v[0] and dict(opc) == {"create": 25, "wire": 16, "x": 14, "wire_remove_loose_ends": 15} and A[0]["wire_uid"] == 27378
     and all(A[k + 1].get("of") == A[k]["id"] for k in range(len(A)) if A[k]["id"] in NX)
     and all(a["why"].startswith("ROUTE ") and len(a["why"]) <= 400 for a in A),
     (v, dict(opc), max(len(a["why"]) for a in A)))
st_of = lambda a: a["why"].split(" | ")[1]                                                                   # noqa: E731
CEN = {"fs_create": {"FlatSequence": 1, "Diagram": 1}, "fs_frame": {"Diagram": 1}}
CSJ = json.load(open(os.path.join(B, "census_samples.json"), encoding="utf-8"))
CTU = dict((x["name"], x) for x in CSJ["ops"]["connect_term_uid"]["variants"])
rows = []
for a in A:
    if a["op"] == "create":
        c = CEN.get("fs_create" if a["class"] == "FlatSequence" else "fs_frame" if a["class"] == "FlatSequenceFrame" else "", {a["class"]: 1})
    elif a["id"] in NX:
        vn = next((n for n in sorted(CTU, key=len, reverse=True) if (" " + n + " ") in a["why"] or (" " + n + ":") in a["why"]), None)
        c = {"variant": "fs_inner_branch (PD257(d))", "delta": {}} if INNER(a) else {"variant": vn, "delta": CTU[vn]["delta"] if vn else None}
    elif a["op"] == "wire_remove_loose_ends":
        c = {}
    else:
        c = {"Wire": 1}
    rows.append({"id": a["id"], "op": a["op"], "route": a["why"].split(" | ")[0][6:], "status": st_of(a), "created": c})
stc = collections.Counter(r["status"] for r in rows)
cc = collections.Counter()
for r in rows:
    if isinstance(r["created"], dict) and "variant" not in r["created"]:
        cc.update(r["created"])
xs = dict((r["id"], r["created"].get("variant")) for r in rows if r["id"] in NX)
gate("M6 statuses: crossings 14 MEASURED (126-4/126-6 variants, 4 inner-face branches PD258(a), PD258(c) error in); 34 non-crossing "
     "MEASURED/PRECEDENT + 15 RLE MEASURED; created (non-crossing) == FlatSequence 1, Diagram 3, "
     "Local 11, GrowableFunction 5, IndexArray 1, SubVI 1, DigitalNumericConstant 1, Wire 12",
     collections.Counter(r["status"] for r in rows if r["id"] in NX) == {"MEASURED": 14}
     and sum(1 for r in rows if r["id"] not in NX and r["op"] != "wire_remove_loose_ends" and r["status"] in ("MEASURED", "PRECEDENT")) == 41
     and sum(1 for r in rows if r["op"] == "wire_remove_loose_ends" and r["status"] == "MEASURED") == 15
     and all(xs[i] in CTU for i in NX if not str(xs[i]).startswith("fs_inner_branch"))
     and dict(cc) == {"FlatSequence": 1, "Diagram": 3, "Local": 11, "GrowableFunction": 5, "IndexArray": 1, "SubVI": 1, "DigitalNumericConstant": 2,
                      "Unbundler": 1, "Function": 1, "Wire": 16},
     (dict(stc), dict(cc), xs))
byw = collections.defaultdict(list)
for r in T:
    if r["wire_uid"]:
        byw[r["wire_uid"]].append(r)
gate("M10 w27378 is on the P3a graph (the first RLE row's target)", bool(byw.get(27378)),
     {"w27378_rows": [(r["owner_uid"], r["term_name"], r["is_source"]) for r in byw.get(27378, [])]})
# PD256(c): a re-created net must keep every old sink. 126-6 measured terms of the NEW net wire (diag_c126_6_cross_out.json
# B1 w27995 9 terms, B2 w28038 9 terms, loose 0); old net on P3a + the new SelectorTunnel outer face must equal that
RECRE = {3747: 6897, 3268: 644, 3040: 6865, 30592: 30145, 4878: 4728, 653: 6924}   # source net -> source terminal (+ PD258(c) w653)
old = dict((wu, sorted((r["owner_uid"], r["term_name"], bool(r["is_source"])) for r in byw.get(wu, []))) for wu in RECRE)
XO = json.load(open(os.path.join(B, "diag_c126_6_cross_out.json"), encoding="utf-8"))
nt = {3747: XO["B1"]["wires_after"]["27995"]["joints"]["terms"], 3268: XO["B2"]["wires_after"]["28038"]["joints"]["terms"]}
gate("M9 re-created nets keep old sinks (by count, 126-6 read): P3a w3747 / w3268 terms + 1 (case SelectorTunnel outer) == 9 each",
     all(len(old[wu]) + 1 == nt[wu] for wu in nt), {"old_terms": dict((k, len(x)) for k, x in old.items()), "new_terms": nt})
try:
    ops = SX.compile_plan(plan)
    comp = collections.Counter((o["kind"], o.get("route") or o.get("variant")) for o in ops)
    cerr = None
except SX.ExecStop as e:
    ops, comp, cerr = [], {}, str(e)
xcomp = dict((A[o["acts"][0] - 1]["id"], o["kind"] + ":" + str(o.get("route") or o.get("variant"))) for o in ops
             if A[o["acts"][0] - 1]["id"] in NX)
want_x = dict((i, "connect_term_uid:" + ("fs_border_inner_branch" if str(xs[i]).startswith("fs_inner") else "fs_border")) for i in NX)
gate("M7 stagexec.compile_plan: 14 crossings -> connect_term_uid (10 fs_border + 4 fs_border_inner_branch), 15 RLE -> "
     "wire_remove_loose_ends, no generic connect for a crossing",
     cerr is None and xcomp == want_x and comp.get(("wire_remove_loose_ends", None)) == 15,
     cerr or {"all": dict((str(k), n) for k, n in comp.items()), "crossings": xcomp})
SIM, ENDST = {}, None
tmp = tempfile.mkdtemp(prefix="c127_2_p3b_")
try:
    for tag, acts in (("A", [a for a in A if a["id"] not in NX and a["op"] != "wire_remove_loose_ends"]), ("B", list(A))):
        pm = os.path.join(tmp, "plan_ring_p3b_sim{0}.json".format(tag))
        json.dump(dict(plan, stage="ring_p3b_sim" + tag, actions=acts), open(pm, "w", encoding="utf-8"), indent=1)
        S = SS.simulate(pm, os.path.join(ROOT, GR), out_root=tmp, plan_out_dir=tmp, log=lambda *x: None, route_check=False)
        done = [s for s in S["steps"] if s["n"] and not s.get("error")]
        SIM[tag] = {"rows": len(acts), "ok_steps": len(done), "failed": S["failed"], "final": S.get("final"),
                    "end_cdiff": None if S["failed"] else sorted(S["steps"][-1].get("cdiff_rows") or [])}
        if tag == "B":
            SIM["B"]["crossings"] = dict((s["id"], dict((k, (s.get("effect_summary") or {}).get(k)) for k in ("how", "variant", "census", "borders")))
                                         for s in S["steps"] if s.get("id") in NX)
            if not S["failed"]:
                ENDST = json.load(open(S["steps"][-1]["file"]["path"], encoding="utf-8"))["state"]
        print("  FACT SIM {0}: {1}".format(tag, json.dumps(SIM[tag], default=str)[:1800]), flush=True)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
P3A_END = sorted(p3a["finalized"]["end_cdiff_rows"])
gate("M8 stagesim replay A (41 non-crossing rows) on graph_ring_p3a: no error; end cdiff == P3a's 16 rows",
     SIM["A"]["failed"] is None and SIM["A"]["ok_steps"] == 41 and SIM["A"]["end_cdiff"] == P3A_END,
     dict(SIM["A"], end_cdiff=len(SIM["A"]["end_cdiff"] or [])))
cx = SIM["B"].get("crossings") or {}
census_ok = all((cx.get(i) or {}).get("census") == (CTU[xs[i]]["delta"] if xs[i] in CTU else {}) for i in NX)
gate("M8b stagesim replay B (all 61) END TO END; every crossing's simulated census == its row's variant delta (PROVISIONAL rows {}); "
     "end cdiff == P3a's 16 rows",
     SIM["B"]["failed"] is None and SIM["B"]["ok_steps"] == len(A) and census_ok and SIM["B"]["end_cdiff"] == P3A_END,
     {"failed": SIM["B"]["failed"], "census_ok": census_ok, "end_cdiff_n": len(SIM["B"]["end_cdiff"] or []),
      "extra": sorted(set(SIM["B"]["end_cdiff"] or []) - set(P3A_END)), "missing": sorted(set(P3A_END) - set(SIM["B"]["end_cdiff"] or []))})
keep = {}
if ENDST:
    tw = dict((r["term_uid"], r["wire_uid"]) for r in ENDST["terminals"])
    for wu, src in RECRE.items():
        olds = [r["term_uid"] for r in byw.get(wu, [])]
        keep[wu] = {"old_terms": len(olds), "on_src_net": sum(1 for t in olds if tw.get(t) and tw.get(t) == tw.get(src)),
                    "end_wire": tw.get(src)}
gate("M11 PD256(c): every old terminal of each re-created source net (w3747 BufNum, w3268 i, w3040 Image Out, w30592 #30117, "
     "w4878 #4580) is on the source's END net (no lost sink)",
     bool(keep) and all(k["old_terms"] == k["on_src_net"] and k["old_terms"] > 0 for k in keep.values()), keep)
OPEN = ["PD258(c) HELD (UNMEASURED): Unbundle By Name `status` + Select + const -1 + 4 wires + BufNum retarget to Select.f - no donor "
        "in the OpPrimCopyNested_v0 registry and no recorded terminal table for Select / an error-cluster Unbundle By Name",
        "IMAQ Copy 'error out' left UNWIRED until the HELD rows land; 'error in' <- #6810 error out is IN (p3b_x_err_in)",
        "IMAQ Copy: 3 connector slots measured UNNAMED ('' x3, graph_harness_copyloop_c95.json #11 t132/t138/t144); stagexec binds them by order",
        "ROWS: 63 actions > 40 (D-2026-10-01-01 cap for P3b); PD255(c): ONE step with a full scratch run"]
if all(c for _n, c in ok):
    json.dump(plan, open(os.path.join(B, "plan_ring_p3b_in.json"), "w", encoding="utf-8"), indent=1)
    json.dump({"schema": "ring-p3b-rows/1", "card": "127-2", "plan_in": "tools/bench/plan_ring_p3b_in.json", "n_rows": len(rows),
               "n_actions": len(A), "status_counts": dict(stc), "created_non_crossing": dict(cc), "crossing_variants": xs,
               "compile": dict((str(k), n) for k, n in comp.items()), "compile_crossings": xcomp, "sim": SIM, "rows": rows,
               "recreated_nets": {"old_terms": dict((k, len(x)) for k, x in old.items()), "new_terms_126_6": nt, "end_keep": keep},
               "dedupe": DD, "open": OPEN, "held_rows": HELD, "card": "127-3"},
              open(os.path.join(B, "plan_ring_p3b_rows.json"), "w", encoding="utf-8"), indent=1)
    print("  FACT WROTE plan_ring_p3b_in.json md5 {0}, plan_ring_p3b_rows.json md5 {1}".format(
        md5(os.path.join(B, "plan_ring_p3b_in.json")), md5(os.path.join(B, "plan_ring_p3b_rows.json"))), flush=True)
np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None))), flush=True)
sys.exit(1 if nf else 0)
