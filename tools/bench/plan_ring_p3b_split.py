r"""plan_ring_p3b_split - card 129-1 (OFFLINE, no LabVIEW, no COM): split plan_ring_p3b_in.json (70 actions, md5 08fa2241) into
P3b-1 / P3b-2 (PD261(d), PD262(b), PD263(b)), finalize both with stagesim, write both predictions.
WHAT EXISTED FIRST: plan_ring_p3b_make.py (the 70-action input, not rebuilt), diag_c127_4_checks.py (finalize + pred shape),
stage_prerun.rebase / provisional_plans (pipeline base form, card chat-P1), census_predict.predict (census derivation).
Tool edit this card: stagesim.base_state keeps a simulated END STATE's simulator keys and continues its negative-uid counter
(a provisional base never existed for an FS stage before; without it P3b-2's new uids would reuse P3b-1's).
CUT: P3b-1 = w27378 RLE + FS/2 frames + frame f0 (Num(i) = -1) + IMAQ Copy (IA1, CP1) + frame f2 (Num(i) = BufNum) + the whole
guard (UB1, SEL1, KM3, 4 guard wires, BufNum -> SEL1.f) + the FIRST crossing of each source into the FS that P3b-1 needs
(i -> f0/f2/IA1, BufNum -> SEL1.f, Image Out, pool, error out) each with its RLE = 40. P3b-2 = TransPos/RotPos/FrameIdx in f1 and
Latest in f2 + their wires + the 3 INNER-FACE i branches, the BufNum -> Latest inner branch and the 3 value crossings + RLE = 30.
PREDICTION: S1 split 40 (15 create, 10 wire, 7 crossing, 8 RLE) + 30 (10 create, 6 wire, 7 crossing, 7 RLE), dependency-closed,
guard + IMAQ Copy in P3b-1, every RLE right after its crossing; S2 P3b-1 simulates END TO END, final, end cdiff == P3a's 16;
S3 P3b-2 references P3b-1 only by frame diagrams (rewritten to P3b-1's simulated uids); S4 P3b-2 on the provisional base END TO
END, final, end cdiff 16; S5 split end == unsplit 70-row end (cdiff rows, objects, terminals, wires, created-class census,
base terminals' wired state); S6 preds written (Error List 55 -> 54 -> 54, census derived or CENSUS-UNPREDICTED).
    py tools/bgrun.py --material --max-min 6 --log tools/bench/plan_ring_p3b_split.log -- py -u tools/bench/plan_ring_p3b_split.py"""
import collections, copy, hashlib, json, os, shutil, sys, tempfile                  # noqa: E401
B = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(B))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import protocol as P, stagesim as SS, stagexec as SX, census_predict as CPR       # noqa: E402,E401
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                    # noqa: E731
rel = lambda p: os.path.relpath(p, ROOT).replace("\\", "/")                       # noqa: E731
J = lambda p: json.load(open(p, encoding="utf-8"))                                # noqa: E731
ok = []


def gate(name, c, det=""):
    ok.append((name, bool(c)))
    print("{0}  {1}  {2}".format("PASS" if c else "FAIL", name, str(det)[:1500]), flush=True)


def finish(arts=()):
    np_, nf = sum(1 for _n, c in ok if c), sum(1 for _n, c in ok if not c)
    print(P.result_line(P.make_result(np_, nf, next((n for n, c in ok if not c), None), list(arts))), flush=True)
    sys.exit(1 if nf else 0)


PIN, GR = os.path.join(B, "plan_ring_p3b_in.json"), os.path.join(B, "graph_ring_p3a_20261001_190155.json")
PINS = {PIN: "08fa224112606aedd4a15ec378268d88", GR: "2fa6ce0c3e8a3014fa916085cb852f68",
        os.path.join(B, "census_samples.json"): "205a7f23802f41342ed25d06dc212bc5"}
got = dict((rel(p), md5(p)) for p in PINS)
gate("S0 inputs md5 == card (plan_ring_p3b_in 08fa2241, P3a graph 2fa6ce0c, census_samples 205a7f23)",
     all(md5(p) == m for p, m in PINS.items()), got)
IN = J(PIN)
A = IN["actions"]
X1 = ["p3b_x_i_f1", "p3b_x_i_f3", "p3b_x_i_ia1", "p3b_x_bn_n3", "p3b_x_img_src", "p3b_x_pool", "p3b_x_err_in"]
ONE = set(["p3b_rle_w27378", "p3b_fs", "p3b_fr2", "p3b_fr3", "p3b_lr_num1", "p3b_ras_num1", "p3b_k_m1", "p3b_lw_num1", "p3b_ia",
           "p3b_copy", "p3b_lr_num3", "p3b_ras_num3", "p3b_lw_num3", "p3b_ub_status", "p3b_sel", "p3b_k_m3", "p3b_w_n1_arr",
           "p3b_w_m1_new", "p3b_w_n1_out", "p3b_w_ia_dst", "p3b_w_n3_arr", "p3b_w_n3_out", "p3b_w_err_ub", "p3b_w_ub_sel",
           "p3b_w_m3_sel", "p3b_w_sel_n3"] + X1 + ["p3b_rle_" + x[6:] for x in X1])
GUARD = ["p3b_copy", "p3b_ub_status", "p3b_sel", "p3b_k_m3", "p3b_w_err_ub", "p3b_w_ub_sel", "p3b_w_m3_sel", "p3b_w_sel_n3",
         "p3b_x_bn_n3", "p3b_rle_bn_n3"]
A1, A2 = [a for a in A if a["id"] in ONE], [a for a in A if a["id"] not in ONE]
XS = set(a["of"] for a in A if a.get("of"))
kind = lambda a: "crossing" if a["id"] in XS else a["op"]                        # noqa: E731
kc = lambda L: dict(collections.Counter(kind(a) for a in L))                      # noqa: E731
rle_ok = lambda L: all(L[k + 1].get("of") == L[k]["id"] for k in range(len(L)) if L[k]["id"] in XS)   # noqa: E731
gate("S1 split: P3b-1 40 = 15 create + 10 wire + 7 crossing + 8 RLE; P3b-2 30 = 10 + 6 + 7 + 7; IMAQ Copy + every guard row in "
     "P3b-1; every RLE right after its crossing in the same half",
     len(ONE) == 40 and kc(A1) == {"wire_remove_loose_ends": 8, "create": 15, "wire": 10, "crossing": 7}
     and kc(A2) == {"create": 10, "wire": 6, "crossing": 7, "wire_remove_loose_ends": 7} and set(GUARD) <= ONE
     and rle_ok(A1) and rle_ok(A2), {"p3b1": kc(A1), "p3b2": kc(A2), "first_p3b2": A2[0]["id"]})


def sim(path, graph, out_root=SS.SIM_ROOT, plan_out=B):
    S = SS.simulate(path, graph, out_root=out_root, plan_out_dir=plan_out, log=lambda *x: None, route_check=False)
    end = J(S["steps"][-1]["file"]["path"])["state"] if not S["failed"] else None
    return S, end


# unsplit 70-row replay (temp dir: the stale tools/bench/sim/ring_p3b and plan_ring_p3b.json are not touched)
tmp = tempfile.mkdtemp(prefix="c129_1_")
try:
    SU, ENDU = sim(PIN, GR, out_root=os.path.join(tmp, "sim"), plan_out=tmp)
finally:
    shutil.rmtree(tmp, ignore_errors=True)
DEF = {}
for a in A:                                                                       # symbols a row defines (stagesim's own naming)
    if a["op"] == "create" and a.get("as"):
        DEF["new:" + a["as"]] = a["id"]
    if a["op"] == "create" and a["class"] == "FlatSequence":
        DEF["new:{0}.f0".format(a["as"])] = a["id"]
fs_rows = [a for a in A if a["op"] == "create" and a["class"] == "FlatSequenceFrame"]
for k, a in enumerate(fs_rows, 1):
    DEF["new:FS1.f{0}".format(k)] = a["id"]
gate("S1b every unsplit symbol is a defined one (stagesim's end sym keys == the rows' symbols)", set(SU["steps"] and ENDU["sym"]) == set(DEF),
     sorted(set(ENDU["sym"]) ^ set(DEF)))


def refs(a):
    out = []
    for f in ("diagram", "src", "dst", "parent"):
        v = a.get(f)
        if isinstance(v, str) and v.startswith("new:"):
            out.append(v if v in DEF else v.split(".")[0])
    return out


pos = dict((a["id"], k) for k, a in enumerate(A))
half = lambda i: 1 if i in ONE else 2                                             # noqa: E731
bad = [(a["id"], r) for a in A for r in refs(a) if r not in DEF or pos[DEF[r]] >= pos[a["id"]] or half(DEF[r]) > half(a["id"])]
bad += [(a["id"], a["of"]) for a in A if a.get("of") and half(a["of"]) != half(a["id"])]
cross = sorted(set(r for a in A2 for r in refs(a) if half(DEF[r]) == 1))
gate("S1c dependency-closed: no row needs a symbol made later or in a later half; P3b-2 needs P3b-1 only through frame diagrams",
     not bad and all(r.startswith("new:FS1.f") for r in cross), {"bad": bad, "p3b2_needs_p3b1": cross})
base_in = dict((k, copy.deepcopy(IN[k])) for k in ("schema", "context", "open_rows"))
P1IN = os.path.join(B, "plan_ring_p3b1_in.json")
json.dump(dict(base_in, stage="ring_p3b1", goal="RING P3b-1 (card 129-1 split of plan_ring_p3b_in.json 08fa2241; PD261(d)): FS + f0 "
               "Num(i)=-1 + IMAQ Copy + f2 Num(i)=BufNum with the status guard (PD261(a), PD262(b))",
               base={"path": rel(GR), "md5": md5(GR)}, actions=A1), open(P1IN, "w", encoding="utf-8"), indent=1)
S1, END1 = sim(P1IN, GR)
P1 = os.path.join(B, "plan_ring_p3b1.json")
P3A_END = sorted(J(os.path.join(B, "plan_ring_p3a.json"))["finalized"]["end_cdiff_rows"])
gate("S2 P3b-1 simulates END TO END on the P3a graph, FINAL, end cdiff == P3a's 16 rows",
     S1["failed"] is None and S1["final"] and sorted(S1["end_cdiff_rows"] or []) == P3A_END,
     {"failed": S1["failed"], "final": S1["final"], "end": len(S1["end_cdiff_rows"] or []), "plan": rel(P1), "md5": md5(P1)})
if not S1["final"]:
    finish()
PROV = os.path.join(B, "sim", "ring_p3b2_base_provisional.json")
json.dump(END1, open(PROV, "w", encoding="utf-8"), separators=(",", ":"), default=str)
A2r = copy.deepcopy(A2)
for a in A2r:
    if isinstance(a.get("diagram"), str) and a["diagram"] in cross:
        a["diagram"] = int(END1["sym"][a["diagram"]])
P2IN = os.path.join(B, "plan_ring_p3b2_in.json")
json.dump(dict(base_in, stage="ring_p3b2", goal="RING P3b-2 (card 129-1 split; PD261(d)): TransPos/RotPos/FrameIdx in f1 + Latest in f2 "
               "on P3b-1's END graph (provisional until P3b-1's artefact exists; stage_prerun --rebase)",
               base={"path": rel(PROV), "md5": md5(PROV), "provisional": True, "sim_of": {"plan": rel(P1), "md5": md5(P1)}},
               actions=A2r), open(P2IN, "w", encoding="utf-8"), indent=1)
v2 = P.validate_obj(J(P2IN))
gate("S3 P3b-2 input validates (stageplan/1, provisional baseref); frame symbols -> P3b-1 simulated uids",
     v2[0] and all(not (isinstance(a.get("diagram"), str) and a["diagram"] in cross) for a in A2r),
     {"valid": v2, "frames": dict((r, END1["sym"][r]) for r in cross), "neg_seed": END1["neg"]})
S2, END2 = sim(P2IN, PROV)
P2 = os.path.join(B, "plan_ring_p3b2.json")
gate("S4 P3b-2 simulates END TO END on the provisional base, FINAL, end cdiff == P3a's 16; no created uid reused",
     S2["failed"] is None and S2["final"] and sorted(S2["end_cdiff_rows"] or []) == P3A_END
     and not (set(END2["sym"].values()) & set(END1["sym"].values())),
     {"failed": S2["failed"], "final": S2["final"], "end": len(S2["end_cdiff_rows"] or []), "plan": rel(P2), "md5": md5(P2)})


def shape(st):
    objs = st["objs"]
    wires = set(r["wire_uid"] for r in st["terminals"] if r["wire_uid"])
    owners = set(r["owner_uid"] for r in st["terminals"])
    new_cls = collections.Counter(o["class"] for o in objs if int(o["uid"]) < 0)
    new_term = collections.Counter((r["owner_class"], r["term_name"], bool(r["is_source"]), r["term_class"], bool(r["wire_uid"]))
                                   for r in st["terminals"] if int(r["owner_uid"]) < 0)
    base_w = sorted((r["term_uid"], bool(r["wire_uid"])) for r in st["terminals"] if int(r["term_uid"]) > 0)
    return {"objects": len(objs), "owners": len(owners), "terminals": len(st["terminals"]), "wires": len(wires),
            "new_classes": dict(new_cls), "new_term_sig": new_term, "base_wired": base_w}


ok2 = bool(END2 and ENDU)
SHU, SH2 = (shape(ENDU), shape(END2)) if ok2 else ({}, {})
cnt = lambda s: dict((k, s.get(k)) for k in ("objects", "owners", "terminals", "wires"))   # noqa: E731
gate("S5 P3b-1 then P3b-2 == the unsplit 70-row replay: end cdiff rows, object/owner/terminal/wire counts, created-class census, "
     "created-terminal signatures, base terminals' wired state",
     ok2 and sorted(SU["end_cdiff_rows"]) == sorted(S2["end_cdiff_rows"]) and all(SHU[k] == SH2[k] for k in SHU),
     {"unsplit": cnt(SHU), "split": cnt(SH2), "cdiff": [len(SU["end_cdiff_rows"] or []), len(S2["end_cdiff_rows"] or [])],
      "diff": [k for k in SHU if SHU[k] != SH2[k]], "new_classes": SH2.get("new_classes")})
SAMP = J(os.path.join(B, "census_samples.json"))
ERRB = sorted(f for f in os.listdir(B) if f.startswith("errorlist_expected_D1_ring_p3a_"))


def pred(plan_path, S, end, base_graph, bed, bed_md5, el, card_note):
    pl = J(plan_path)
    rep = CPR.predict(pl, {}, SAMP)
    acts = pl["actions"]
    unp = [acts[k - 1]["id"] for k in rep["unpredicted"]]
    born = dict((int(u), DEF.get(s)) for s, u in end["sym"].items())
    base_owners = set(int(r["owner_uid"]) for r in J(base_graph)["terminals"])
    unw = sorted("{0} '{1}' ({2} #{3})".format(born.get(int(r["owner_uid"]), "?"), r["term_name"], r["owner_class"], r["owner_uid"])
                 for r in end["terminals"] if int(r["owner_uid"]) not in base_owners and not r["is_source"] and not r["wire_uid"])
    el = dict(el, unwired_created_sinks=unw, alternative="+{0} if LabVIEW flags an unwired created sink above as an item".format(len(unw)))
    d = {"schema": "ring-p3b-pred/1", "card": "129-1", "note": card_note, "plan": {"path": rel(plan_path), "md5": md5(plan_path)},
         "graph": {"path": rel(base_graph), "md5": md5(base_graph)}, "bed": bed, "bed_md5": bed_md5,
         "census": dict(rep["derived"]), "census_overall": rep["overall"], "census_unpredicted": unp,
         "census_rows": [dict((k, r[k]) for k in ("k", "id", "op", "variant", "delta", "verdict")) for r in rep["rows"]],
         "ops": [o["kind"] for o in SX.compile_plan(pl)], "cdiff_rows": sorted(S["end_cdiff_rows"]), "errorlist": el,
         "readback": {"row": "p3b_w_ub_sel", "terminal": "UB1 element#0", "expect_name": "status", "decided": "PD262(b)"}}
    po = plan_path[:-5] + "_pred.json"
    json.dump(d, open(po, "w", encoding="utf-8"), indent=1)
    return po, d


G = J(GR)
po1, d1 = pred(P1, S1, END1, GR, G["vi"], G["md5"],
               {"bed_total": 55, "removed": {"p3b_rle_w27378": 1}, "new_items_predicted": 0, "predicted_total": 54,
                "base_file": "tools/bench/" + ERRB[-1] if ERRB else None,
                "row_sources": {"p3b_rle_w27378": "-1: w27378 'Wire has loose ends' (diag_c126_4_op.log:52-60, 55 -> 54)",
                                "crossings + their RLE rows": "0: measured, loose ends cleared (diag_c126_6_cross.log:61-65; diag_c127_1_fsinner.log:81-109)",
                                "guard rows (UB1, SEL1, KM3, 4 wires, BufNum -> SEL1.f)": "0: every Select input wired (diag_c128_2_donors.log:80-99)"}},
               "P3b-1: base = the real P3a bed")
po2, d2 = pred(P2, S2, END2, PROV, G["vi"], G["md5"],
               {"bed_total": 54, "removed": {}, "new_items_predicted": 0, "predicted_total": 54, "base_file": "P3b-1's errorlist_expected (after its launch)",
                "row_sources": {"crossings + their RLE rows": "0 (as P3b-1)", "T/R/F + Latest creates and wires": "0: every created sink wired"}},
               "P3b-2: PROVISIONAL base (P3b-1's simulated end); bed/bed_md5 are the P3a bed's, inherited by the simulated state - "
               "replaced at stage_prerun --rebase onto P3b-1's saved artefact")
for tag, d, po in (("P3b-1", d1, po1), ("P3b-2", d2, po2)):
    print("  FACT {0} pred {1} md5 {2}: census {3} overall {4} unpredicted {5}; Error List {6} -> {7}; unwired created sinks {8}; ops {9}".format(
        tag, rel(po), md5(po), d["census"], d["census_overall"], d["census_unpredicted"], d["errorlist"]["bed_total"],
        d["errorlist"]["predicted_total"], d["errorlist"]["unwired_created_sinks"], dict(collections.Counter(d["ops"]))), flush=True)
gate("S6 preds written: P3b-1 Error List 55 -> 54, P3b-2 54 -> 54; ops == compile of each plan (40 / 30 actions)",
     d1["errorlist"]["predicted_total"] == 54 and d2["errorlist"]["predicted_total"] == 54
     and sorted(n for o in SX.compile_plan(J(P1)) for n in o["acts"]) == list(range(1, 41))
     and sorted(n for o in SX.compile_plan(J(P2)) for n in o["acts"]) == list(range(1, 31)), [len(d1["ops"]), len(d2["ops"])])
finish([{"path": rel(p), "md5": md5(p)} for p in (P1, P2, po1, po2, PROV)])
