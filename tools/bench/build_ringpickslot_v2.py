r"""build_ringpickslot_v2.py - card 142-3 (escalation 1 of 142-1/142-2): claudeDev\RingPickSlot_v0.vi = plan_ring_p4_v17.json's slot group (GT1 FMN1 SW1 KMX1 KMX2
AMM1 LT1, :945-1126,1578-1689); external wires p4_w_num_gt/p4_t_fnum_in, p4_t_last_out, p4_t_n1_in, p4_t_slot_in, p4_w_lt_or = the brief's Num, last / min Num, min slot,
found. = v1 (same calls/order, measured v1.log:3-38) + desk-check fixes (diag_c142_3_facts.md; review archive/peer/2026-10-03-c142-3-hyp-rps1.md): F1 every terminal by
ITS OWN uid (reg after creation, mk from create_*, tr re-checks owner/name/direction, never after the relabel; v1.py:46 took a control terminal's OWNER = diagram #3);
F2 for_loop leaves 3 unwired constants (5 traverse entries) on the top level (OpForLoop_v0's 3 Create Constant.vi, probe_opforloop.log:8-16 = v1.log:15-21): the FMN's
are gated unwired, then deleted; F3 a For's label is 'For Loop' (stage_d1_qrt_pool_scratch.log:52); F4 Num/last types read on GT.x/GT.y before use (review 2a).
PREDICTION: wires err ''/unbroken; GT.x Array1D<I32>, GT.y I32; scaffold end ForLoop {} Constant {KMX2} Comparison {GT}, GT.y/KMX2/last unwired; FMN +1 For +1 Diagram
+5 Constant (3 TopLevelDiagram, 2 ArrayConstant) unwired -> deleted (array elements go with their array); labels {Array Max & Min, For Loop, Greater?, Less?, Select};
Constant {KMX1, KMX2} I32 2147483647; 3 LoopTunnels IndexMode 1; ExecState 1; pane 11 Num 10 last 3 min Num 2 min slot 1 found; 7 runs == ref (Num I32 read back);
fresh: md5 same, ExecState 1, vectors 2+5 equal; handles +-100 over the runs; bed + s01 md5 same; LabVIEW gone.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/build_ringpickslot_v2.log -- py -u tools/bench/build_ringpickslot_v2.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import diag_c138_6_run as D                                                                    # noqa: E402 (main() guarded)
S5, g, P, BP, gate, fact, md5, Stop, rows, cp = D.S5, D.g, D.P, D.bench_prep, D.gate, D.fact, D.md5, D.Stop, D.rows, D.cp   # noqa: E702
CD, BED, BEDM, TS, MAXV, TOP = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S"), 2147483647, [3]   # noqa: E702
S01, S01M = os.path.join(CD, "D1_ring_p4s01_20261002_232547.vi"), "dc61e193e0376ce760f88fdfcda7087b"   # noqa: E702
TGT = D.TGT2 = os.path.join(CD, "RingPickSlot_v0.vi"); BEDD = os.path.join(CD, "scratch_c142_3_bdon_%s.vi" % TS)   # noqa: E702
SEL, DMAX, KO = {"donor": D.SEL_D, "uid": 529}, {"donor": D.DON, "uid": 127}, {"": True}; OUT, SCR, TU = {"runs": [], "fresh": []}, S5.SCR, {}   # noqa: E702
R3, R5, I20 = [20, 21, 22] + list(range(3, 20)), [-1, 21, 22] + list(range(3, 20)), list(range(20)); VEC = [([-1] * 20, -1), (I20, 4), (R3, 5), (R3, 19), (R5, 20), (R5, 22), (I20, 19)]   # noqa: E702
def CMP(o): return {o: True, "x": False, "y": False}                                           # noqa: E704
def ref(num, last): m = [n if n > last else MAXV for n in num]; return [min(m), m.index(min(m)), min(m) < MAXV]   # noqa: E702,E704
def peak(): return S5.subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process LabVIEW | Select-Object -First 1).PeakWorkingSet64/1MB"], capture_output=True, text=True).stdout.strip()   # noqa: E704
def kill(tag): g.reset(); S5.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5); gate("%s LabVIEW gone" % tag, "labview.exe" not in S5.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)   # noqa: E702,E704
def canon(k): t = g.read_term_type(TGT, TU[k][0]); return (t.get("types") or {}).get("canon"), t.get("err")   # noqa: E702,E704 - a node PIN's type (route measured diag_c140_5_run2.log:31)
def reg(u, tag, want):   # F1: the node's terminal rows read ONCE after it is made; each terminal used later is registered by ITS OWN uid
    rs = [r for r in rows(TGT) if r["owner_uid"] == u]; fact("TERMS %s #%s" % (tag, u), [(r["term_uid"], r["term_name"], r["is_source"]) for r in rs])   # noqa: E702
    for n, s in want.items(): m = [r for r in rs if r["term_name"] == n and r["is_source"] == s]; gate("T %s.%s unique on #%s" % (tag, n, u), len(m) == 1, m); TU["%s.%s" % (tag, n)] = (m[0]["term_uid"], u, n, s)   # noqa: E701,E702
def tr(R, k):            # F1: the terminal by its own uid; owner / name / direction re-checked in THIS read (a reused uid fails here)
    u, o, n, s = TU[k]; m = [r for r in R if r["term_uid"] == u]; gate("T %s = #%s" % (k, u), len(m) == 1 and (m[0]["owner_uid"], m[0]["term_name"], m[0]["is_source"]) == (o, n, s), [(r["term_uid"], r["owner_uid"], r["term_name"], r["wire_uid"]) for r in m]); return m[0]   # noqa: E702
def Wr(tag, snk, src):
    R = rows(TGT); r = g.connect_term_uid(TGT, tr(R, snk)["term_uid"], tr(R, src)["term_uid"]); OUT.setdefault("wires", {})[tag] = r; fact("WIRE %s" % tag, r); gate("wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r)   # noqa: E702
def mk(fn, u, name, src, tag):   # top-level create_control / create_indicator by node index (diag_c140_5_run.py:49-53), node identity by uid echo
    ni = g._node_index(TGT, 0, u); nu, rs = g.node_terms_uid(TGT, 0, ni); p0 = set(int(r["uid"]) for r in g.panel_wiring(TGT))   # noqa: E702
    r = fn(TGT, ni, next(x["i"] for x in rs if x["name"] == name and bool(x["is_source"]) == src)); ct = r[0] if isinstance(r, tuple) else r   # noqa: E702
    np_ = [x for x in g.panel_wiring(TGT) if int(x["uid"]) not in p0]; OUT[tag] = {"ret": r, "panel": np_, "echo": nu}; fact("PANEL %s" % tag, OUT[tag])   # noqa: E702
    gate("panel object %s: node echo #%s, one new panel object wired, one new ControlTerminal" % (tag, u), nu == u and len(np_) == 1 and bool(np_[0]["wire"]) and len(ct) == 1, (nu, np_, ct))
    TU[tag] = (int(ct[0]["uid"]), TOP[0], np_[0]["label"], bool(np_[0]["is_source"])); return int(np_[0]["uid"])   # noqa: E702
def dele(u, cls):        # v1.py:29-32 (measured v1.log:14-21,34): re-read the traverse, skip a uid already gone with its owner
    order = [int(o["uid"]) for o in g.report_all(TGT, cls)]
    if int(u) not in order: return fact("DELETE #%s %s skipped: not in the traverse any more" % (u, cls), order)   # noqa: E701
    g.delete_object(TGT, cls, order.index(int(u)), verify=False); fact("DELETE #%s %s sent (index %d)" % (u, cls, order.index(int(u))), order)   # noqa: E702
def build():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); gate("bed byte copy md5 == bed", md5(BEDD) == BEDM)   # noqa: E702
    gate("target does not exist yet", not os.path.exists(TGT), TGT); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT); SCR.append(TGT); g.open_panel(TGT)   # noqa: E702
    TOP[0] = top = int(g.report_all(TGT, "Diagram")[0]["uid"]); d0, f0 = g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop")   # noqa: E702
    g.for_loop(TGT, (60, 520)); FG = sorted(g.uids(TGT, "ForLoop") - f0)[0]; fgb = sorted(g.uids(TGT, "Diagram") - d0)[0]   # noqa: E702
    OUT["n_const"] = g.create_const_loop_term(TGT, "for_n", g._node_index(TGT, 0, FG), value=20); k0 = cp(fgb, "const_donor", (40, 40), {"donor": D.I0_D, "uid": 248})   # noqa: E702
    GT = cp(top, "Greater?", (300, 150), {"donor": BEDD, "uid": 11721}); reg(k0, "k0", KO); reg(GT, "GT", CMP("x > y?"))   # noqa: E702
    Wr("scaffold GT.y <- k0 (generator For out)", "GT.y", "k0."); pn = mk(g.create_control, GT, "x", False, "Num")   # noqa: E702
    OUT["type_num"] = canon("GT.x"); gate("F4 Num (on GT.x) is Array1D<I32>", OUT["type_num"][0] == "Array1D<I32>", OUT["type_num"])   # noqa: E702
    C0 = g.report_all(TGT, "Constant"); fact("scaffold Constant traverse (uid, class, owner, pos)", [(o["uid"], o["class"], o["owner"], o["pos"]) for o in C0])   # noqa: E702
    dele(FG, "ForLoop"); [dele(u, "Constant") for u in sorted(int(o["uid"]) for o in C0 if o["owner"] != "ArrayConstant")]; fact("RBW 1", g.remove_bad_wires_scripted(TGT))   # noqa: E702
    KMX2, H = cp(top, "const_donor", (900, 330), DMAX), cp(top, "Less?", (300, 650), {"donor": BEDD, "uid": 10950}); reg(KMX2, "KMX2", KO); reg(H, "H", CMP("x < y?"))   # noqa: E702
    Wr("scaffold H.y <- KMX2", "H.y", "KMX2."); pl = mk(g.create_control, H, "x", False, "last"); dele(H, "Comparison"); fact("RBW 2", g.remove_bad_wires_scripted(TGT))   # noqa: E702
    R = rows(TGT); w = dict((k, tr(R, k)["wire_uid"]) for k in ("GT.y", "GT.x", "KMX2.", "last", "Num"))
    SC = OUT["scaffold_end"] = {"for": sorted(g.uids(TGT, "ForLoop")), "const": sorted(g.uids(TGT, "Constant")), "cmp": sorted(g.uids(TGT, "Comparison")), "wires": w}
    gate("ONE re-read after the scaffold deletes == predicted end state", SC["for"] == [] and SC["const"] == [KMX2] and SC["cmp"] == [GT] and not w["GT.y"] and not w["KMX2."] and not w["last"] and bool(w["GT.x"]) and w["GT.x"] == w["Num"], SC)
    Wr("GT.y <- last", "GT.y", "last"); OUT["type_last"] = canon("GT.y"); gate("F4 last (on GT.y) is I32", OUT["type_last"][0] == "I32", OUT["type_last"])   # noqa: E702
    c1, d1, f1 = g.uids(TGT, "Constant"), g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop"); g.for_loop(TGT, (480, 300))   # noqa: E702
    nf, nd = sorted(g.uids(TGT, "ForLoop") - f1), sorted(g.uids(TGT, "Diagram") - d1); gate("FMN for_loop: +1 ForLoop, +1 Diagram", len(nf) == 1 and len(nd) == 1, (nf, nd))   # noqa: E702
    FMN, fmb = nf[0], nd[0]; J = [o for o in g.report_all(TGT, "Constant") if int(o["uid"]) not in c1]; ju = set(int(o["uid"]) for o in J)   # noqa: E702
    jw = [r for r in rows(TGT) if r["owner_uid"] in ju and r["wire_uid"]]; OUT["junk"] = [(o["uid"], o["class"], o["owner"], o["pos"]) for o in J]; fact("F2 FMN junk (uid, class, owner, pos)", OUT["junk"])   # noqa: E702
    gate("F2: +5 Constant entries (3 TopLevelDiagram, 2 ArrayConstant), none wired", sorted(o["owner"] for o in J) == ["ArrayConstant"] * 2 + ["TopLevelDiagram"] * 3 and not jw, jw)
    [dele(int(o["uid"]), "Constant") for o in J if o["owner"] == "TopLevelDiagram"]; c2 = sorted(g.uids(TGT, "Constant")); gate("F2 junk deleted: Constant == {KMX2}", c2 == [KMX2], c2)   # noqa: E702
    SW, KMX1 = cp(fmb, "Select", (120, 80), SEL), cp(fmb, "const_donor", (20, 140), DMAX)       # noqa: E702
    AMM, LT = cp(top, "Array Max & Min", (800, 150), {"donor": BEDD, "uid": 10969}), cp(top, "Less?", (1050, 150), {"donor": BEDD, "uid": 10950})   # noqa: E702
    reg(SW, "SW", {"s? t:f": True, "t": False, "s": False, "f": False}); reg(KMX1, "KMX1", KO); reg(LT, "LT", CMP("x < y?")); reg(AMM, "AMM", {"array": False, "min value": True, "min index (indices)": True})   # noqa: E702
    B = OUT["B"] = {"top": top, "GT": GT, "KMX2": KMX2, "FMN": FMN, "fmb": fmb, "SW": SW, "KMX1": KMX1, "AMM": AMM, "LT": LT}; fact("created", B)   # noqa: E702
    Wr("SW.t <- Num (FMN in)", "SW.t", "Num"); Wr("SW.s <- GT out (FMN in)", "SW.s", "GT.x > y?"); Wr("SW.f <- KMX1", "SW.f", "KMX1."); Wr("AMM.array <- SW out (FMN out)", "AMM.array", "SW.s? t:f")   # noqa: E702
    pm, ps = mk(g.create_indicator, AMM, "min value", True, "min Num"), mk(g.create_indicator, AMM, "min index (indices)", True, "min slot")   # noqa: E702
    Wr("LT.y <- KMX2", "LT.y", "KMX2."); Wr("LT.x <- AMM.min value", "LT.x", "AMM.min value")    # noqa: E702
    pf = mk(g.create_indicator, LT, "x < y?", True, "found"); want = {pn: "Num", pl: "last", pm: "min Num", ps: "min slot", pf: "found"}   # noqa: E702 - no tr() after this line
    OUT["labels"] = [(r["uid"], g.set_control_label(TGT, i, want[int(r["uid"])])) for i, r in enumerate(g.panel_wiring(TGT)) if int(r["uid"]) in want]
    pw = OUT["panel"] = [(r["uid"], r["label"], r["indicator"], r["wire"]) for r in g.panel_wiring(TGT)]; fact("panel", pw)   # noqa: E702
    gate("panel == {Num, last} controls + {min Num, min slot, found} indicators, all wired", sorted((p[1], bool(p[2])) for p in pw) == sorted([("Num", False), ("last", False), ("min Num", True), ("min slot", True), ("found", True)]) and all(p[3] for p in pw), pw)
    ws = sorted(set(x["wire_uid"] for x in rows(TGT) if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT, "Wire")))
    rle = dict((w, g.wire_remove_loose_ends(TGT, w, index=WI.get(w))) for w in ws); OUT["broken"] = [w for w, r in rle.items() if r.get("broken_before") or r.get("err")]   # noqa: E702
    gate("every wire Is Broken? False (%d wires)" % len(ws), not OUT["broken"], OUT["broken"], need=False)
    lab = dict((int(x["uid"]), x["label"]) for di in (0, g._uid_index(TGT, "Diagram", fmb)) for x in g.node_labels(TGT, di)); fact("node labels (top + FMN body)", lab)   # noqa: E702
    OUT["prim"] = dict((k, lab.get(B[k])) for k in ("GT", "SW", "AMM", "LT")); gate("PRIM gate: GT Greater? / SW Select / AMM Array Max & Min / LT Less?", OUT["prim"] == {"GT": "Greater?", "SW": "Select", "AMM": "Array Max & Min", "LT": "Less?"}, OUT["prim"])   # noqa: E702
    gate("F3 census: node labels == Array Max & Min, For Loop, Greater?, Less?, Select", sorted(v for v in lab.values() if v and v not in want.values()) == ["Array Max & Min", "For Loop", "Greater?", "Less?", "Select"], sorted(lab.values()), need=False)
    cs = OUT["consts"] = dict((u, g.read_const_value(TGT, u)) for u in sorted(g.uids(TGT, "Constant"))); fact("constants", cs)   # noqa: E702
    gate("census: Constant == {KMX1, KMX2}, I32 2147483647 each", sorted(cs) == sorted([KMX1, KMX2]) and all(v.get("value") == MAXV and (v.get("type") or {}).get("repr_name") == "I32" for v in cs.values()), cs, need=False)
    lt = OUT["tunnels"] = [(t["uid"], t["index_mode"]) for t in (g.tunnels(TGT, k) for k in range(len(g.report_all(TGT, "LoopTunnel"))))]   # noqa: E702
    gate("census: For 1, 3 LoopTunnels IndexMode 1", len(g.uids(TGT, "ForLoop")) == 1 and len(lt) == 3 and all(t[1] == 1 for t in lt), lt, need=False)
    es = OUT["es"] = g.exec_state(TGT); gate("ExecState 1", es == 1, es)                      # noqa: E702
    vi = g.op(g.OP_CONPANE_ASSIGN); L = [x for _i, x, _d in g.fp_labels(TGT)]                # noqa: E702 - diag_replay_skeleton.py:38-49
    for slot, l in ((11, "Num"), (10, "last"), (3, "min Num"), (2, "min slot"), (1, "found")):
        for k, v in (("vi path", TGT), ("index", L.index(l)), ("Terminal Index", slot), ("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")): vi.SetControlValue(k, v)   # noqa: E701
        g._run(vi); gate("pane assign %s -> %s err ''" % (l, slot), not g._err(vi), g._err(vi))   # noqa: E702
    g.save(TGT); SCR.remove(TGT); OUT["pane"] = g.conpane(TGT); OUT["md5"] = md5(TGT); fact("pane read back / saved md5", (OUT["pane"], OUT["md5"]))   # noqa: E702
    gate("pane read back: 11 Num, 10 last, 3 min Num, 2 min slot, 1 found, others free", OUT["pane"] == {**{k: None for k in range(12)}, 11: "Num", 10: "last", 3: "min Num", 2: "min slot", 1: "found"}, OUT["pane"])
def runs(tag, idx):
    vi = g.lv().GetVIReference(TGT, "", False, 0); h = OUT["h_" + tag] = [BP.labview_handles()]   # noqa: E702
    for k in idx:
        num, last = VEC[k]; vi.SetControlValue("Num", num); vi.SetControlValue("last", last); g._run(vi); nb = list(vi.GetControlValue("Num"))   # noqa: E702
        got = [vi.GetControlValue("min Num"), vi.GetControlValue("min slot"), vi.GetControlValue("found")]; want = ref(num, last); OUT[tag].append((k + 1, last, want, got))   # noqa: E702
        ok = got == want and all(type(x) is int for x in got[:2] + nb) and nb == num and vi.GetControlValue("last") == last   # Num I32[] and last read back exactly
        gate("%s vector %d last=%s -> %s (got %s)" % (tag, k + 1, last, want, got), ok, need=False)
    h.append(BP.labview_handles()); gate("%s handles flat over the runs (+-100)" % tag, abs(h[1] - h[0]) <= 100, h, need=False)   # noqa: E702
def main():
    BP.restart_labview(); g.reset(); time.sleep(3); OUT["h0"] = BP.labview_handles()           # noqa: E702
    gate("bed + s01 md5 before", md5(BED) == BEDM and md5(S01) == S01M); build(); runs("runs", range(7))   # noqa: E702
    OUT["h1"], OUT["peak_mb"] = BP.labview_handles(), peak(); fact("handles h0/h1, peak MB", (OUT["h0"], OUT["h1"], OUT["peak_mb"]))   # noqa: E702
    kill("A"); BP.restart_labview(); g.reset(); time.sleep(3)                                  # noqa: E702
    gate("fresh: saved md5 unchanged, ExecState 1", md5(TGT) == OUT["md5"] and g.exec_state(TGT) == 1); runs("fresh", (1, 4))   # noqa: E702
if __name__ == "__main__":
    try: main()                                                                                 # noqa: E701
    except Stop as e: print("STOP at the first unexpected result: %s" % e, flush=True)         # noqa: E701
    except Exception as e: traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)   # noqa: E701,E702,BLE001
    finally:
        kill("Z"); [os.path.exists(p) and os.remove(p) for p in SCR]; bad = [k for k, v in S5.G.items() if not v]; FL = TGT[:-3] + "_c142_3_FAIL_%s.vi" % TS   # noqa: E702
        if bad and OUT.get("md5") and os.path.exists(TGT): os.replace(TGT, FL); fact("OUR saved file moved aside (a gate failed)", FL)   # noqa: E701,E702
        gate("scratch files deleted; bed + s01 md5 unchanged", not any(os.path.exists(p) for p in SCR) and md5(BED) == BEDM and md5(S01) == S01M, SCR, need=False)
        json.dump(OUT, open(os.path.join(HERE, "diag_c142_3_out.json"), "w", encoding="utf-8"), indent=1, default=str); bad = [k for k, v in S5.G.items() if not v]   # noqa: E702
        json.dump({"function": "RingPickSlot_v0 subVI build + run", "card": "142-3", "t": time.time(), "log": "tools/bench/build_ringpickslot_v2.log", "status": "FAIL" if bad else "PASS", "out": OUT}, open(os.path.join(HERE, "scratch_verify", "ringpickslot_c142_3_%s.json" % TS), "w", encoding="utf-8"), indent=1, default=str)
        arts = [{"path": TGT, "md5": md5(TGT)}] if os.path.exists(TGT) else []; print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)   # noqa: E702
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True); sys.exit(1 if bad else 0)   # noqa: E702
