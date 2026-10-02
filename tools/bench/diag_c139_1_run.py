r"""diag_c139_1_run.py - card 139-1 (PD313(b)(e), docs/d1/ring-p4.md:278-292): scratch only, based on diag_c138_6_run.py (its
helpers imported, nothing re-typed). Order: A = bed byte copy (known route, 138-6 :61-68) then a fresh LabVIEW, B = the For group.
FOUND FIRST: 138-6 step 2 stopped because GT sat on the TOP-LEVEL diagram (create_control_nested refuses, gscript.py:4149);
for_n constants exist only for a top-level For (gscript.py:2978); no I32-array control creator (diag_c138_6_run.py:8) -> Num =
top-level create_control (gscript.py:2922) on helper Greater? GH.x after GH.y is wired from a top-level generator For (N=20, I32 0
const #248 inside; the 138-6 measured wire, facts :33-34) - LabVIEW types the new control like the wired y (UNMEASURED, gated).
Group as v8 (plan_ring_p4_v8.json): While W (cond = const True, one iteration) body holds GT (p4_gt_last, Comparison), FMN For
(p4_f_min), SW Select #529 (p4_sel_mask) + KMX DonorI32Max_v0 #127 (p4_k_max) in FMN body, AMM #10969 (p4_amm); tunnels made by
connect_term_uid across ONE border each: TFN1 (p4_t_fnum), TFB1 (p4_t_fgt), TFS1 (p4_t_fsel).
PREDICTION: A: bed copy md5 == bed; w25415 deleted; FULL Error List read (every item double-clicked) = 52 items, exactly ONE raw
not in the 51-item baseline (errorlist_..._130834.json); bed md5 unchanged. B: every wire err '' and Is Broken? False; Num control
reads back a 20-element list; 3 LoopTunnels with an inner face on FMN's body, every IndexMode 1; ExecState 1; runs
Num=[-1,5,3,9,0,1,2,-7,4,8,6,7,10..17]: last 2 -> 3; last 17 -> 2147483647. LabVIEW gone; scratch files deleted.
    py tools/bgrun.py --material --max-min 50 --log tools/bench/diag_c139_1_run.log -- py -u tools/bench/diag_c139_1_run.py"""
import collections, json, os, shutil, sys, time, traceback                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import diag_c138_6_run as D                                                                    # noqa: E402 (main() guarded)
S5, g, AT, TB, C82, EC, P = D.S5, D.g, D.AT, D.TB, D.C82, D.EC, D.P                              # noqa: E702
gate, fact, md5, Stop, rows, one, cp = D.gate, D.fact, D.md5, D.Stop, D.rows, D.one, D.cp       # noqa: E702
CD, BED, BEDM, TS, MAXV = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S"), D.MAXV     # noqa: E702
BEDC, BEDD = os.path.join(CD, "scratch_c139_1_bed_%s.vi" % TS), os.path.join(CD, "scratch_c139_1_bdon_%s.vi" % TS)
TGT = D.TGT2 = os.path.join(CD, "scratch_c139_1_for_%s.vi" % TS)
BASE = os.path.join(HERE, "errorlist_D1_ring_p3b2b_20261002_130007_20261002_130834.json")
EXP = os.path.join(HERE, "errorlist_expected_D1_ring_p3b2b_20261002_130007.json")
NUM = [-1, 5, 3, 9, 0, 1, 2, -7, 4, 8, 6, 7] + list(range(10, 18)); OUT, SCR = {}, S5.SCR       # noqa: E702
def ldump(): json.dump(OUT, open(os.path.join(HERE, "diag_c139_1_out.json"), "w", encoding="utf-8"), indent=1, default=str)   # noqa: E704
def stepA():
    shutil.copyfile(BED, BEDC); SCR.append(BEDC); gate("A bed byte copy md5 == bed", md5(BEDC) == BEDM)   # noqa: E702
    g.open_panel(BEDC); r0 = [x for x in rows(BEDC) if x["wire_uid"] == 25415]; fact("A w25415 terminals before", r0)   # noqa: E702
    ok = C82.del_wire(BEDC, 25415, "A "); gate("A delete_wire w25415", ok and 25415 not in g.uids(BEDC, "Wire"))   # noqa: E702
    r1 = [x for x in rows(BEDC) if x["term_uid"] in set(t["term_uid"] for t in r0)]; OUT["A_after"] = {"rows": r1, "es": g.exec_state(BEDC)}
    fact("A same terminals after", OUT["A_after"])
    EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(BEDC, RR)   # noqa: E702
    r = EC.E.read(BEDC, os.path.join(HERE, "errorlist_c139_1_bed_raw.json"), log=lambda m: None, on_item=EC.make_on_item(BEDC, RR))
    it = r.get("items") or []; base = [x.get("raw") for x in json.load(open(BASE, encoding="utf-8"))["items"]]   # noqa: E702
    new = list((collections.Counter(x.get("raw") for x in it) - collections.Counter(base)).elements())
    gone = list((collections.Counter(base) - collections.Counter(x.get("raw") for x in it)).elements())
    exp = json.load(open(EXP, encoding="utf-8")).get("expected", []); extra, missing, _u = EC.compare(it, exp)   # noqa: E702
    nr = [dict((k, x.get(k)) for k in ("index", "object", "reason", "raw", "detail")) for x in it if x.get("raw") in new]
    OUT["A_el"] = {"items": len(it), "n": r.get("n_reported"), "dclicked": sum(1 for x in it if x.get("show_error")),
                   "new_vs_base": nr, "gone_vs_base": gone, "extra_vs_expected": extra, "missing_vs_expected": missing,
                   "shots": [(x.get("show_error") or {}).get("screenshot") for x in it if x.get("raw") in new], "errors": (r.get("errors") or [])[:3]}
    fact("A Error List FULL read", OUT["A_el"]); ldump()                                        # noqa: E702
    gate("A full read: 52 items, all double-clicked", len(it) == 52 and OUT["A_el"]["dclicked"] == 52, (len(it), OUT["A_el"]["dclicked"]), need=False)
    gate("A exactly one item new vs the 51 baseline", len(new) == 1, (new, gone), need=False)
    g.close_panel(BEDC); gate("A bed md5 unchanged", md5(BED) == BEDM)                          # noqa: E702
def stepB():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT); SCR.append(TGT); g.open_panel(TGT)   # noqa: E702
    top = int(g.report_all(TGT, "Diagram")[0]["uid"]); d0, f0 = g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop")   # noqa: E702
    g.for_loop(TGT, (60, 400)); FG = sorted(g.uids(TGT, "ForLoop") - f0)[0]; fgb = sorted(g.uids(TGT, "Diagram") - d0)[0]   # noqa: E702
    g.create_const_loop_term(TGT, "for_n", TB.walk(TGT, 0)[FG][0], value=20); d1 = g.uids(TGT, "Diagram")   # noqa: E702
    g.while_loop(TGT, (500, 100)); W = sorted(g.uids(TGT, "WhileLoop"))[0]; wb = sorted(g.uids(TGT, "Diagram") - d1)[0]   # noqa: E702
    wc = g.create_const_loop_term(TGT, "while_cond", 0, value=True); d2 = g.uids(TGT, "Diagram")   # noqa: E702
    FMN = g.loop_in("for", TGT, g._uid_index(TGT, "Diagram", wb), (250, 150)); fmb = sorted(g.uids(TGT, "Diagram") - d2)[0]   # noqa: E702
    k0, GH = cp(fgb, "const_donor", (40, 40), {"donor": D.I0_D, "uid": 248}), cp(top, "Greater?", (300, 420), {"donor": BEDD, "uid": 11721})
    GT, AMM = cp(wb, "Greater?", (60, 60), {"donor": BEDD, "uid": 11721}), cp(wb, "Array Max & Min", (700, 150), {"donor": BEDD, "uid": 10969})
    SW, KMX = cp(fmb, "Select", (120, 80), {"donor": D.SEL_D, "uid": 529}), cp(fmb, "const_donor", (20, 140), {"donor": D.DON, "uid": 127})
    B = OUT["B"] = {"top": top, "FG": FG, "fgb": fgb, "W": W, "wb": wb, "wc": wc, "FMN": FMN, "fmb": fmb, "k0": k0, "GH": GH, "GT": GT,
                    "AMM": AMM, "SW": SW, "KMX": KMX, "wires": {}}; fact("B created", B)          # noqa: E702
    def Wr(tag, snk, src):
        r = g.connect_term_uid(TGT, snk, src); B["wires"][tag] = r; fact("B WIRE %s" % tag, r)   # noqa: E702
        gate("B wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r); return rows(TGT)   # noqa: E702
    R = Wr("GH.y <- k0 (FG out)", one(rows(TGT), owner_uid=GH, term_name="y")["term_uid"], one(rows(TGT), owner_uid=k0, is_source=True)["term_uid"])
    nx = TB.walk(TGT, 0)[GH][0]; tx = next(r["i"] for r in g.node_terms_uid(TGT, 0, nx)[1] if r["name"] == "x" and not r["is_source"])   # noqa: E702
    new, lab = g.create_control(TGT, nx, tx)
    R = rows(TGT); w = one(R, owner_uid=GH, term_name="x")["wire_uid"]; num = one(R, wire_uid=w, is_source=True); B["num"] = (new, lab, num)   # noqa: E702
    fact("B Num control on GH.x", B["num"]); gate("B Num control created and wired to GH.x", new and w, B["num"])   # noqa: E702
    R = Wr("GT.x <- Num (W in)", one(R, owner_uid=GT, term_name="x")["term_uid"], num["term_uid"])
    wi = [x for x in R if x["owner_class"] == "LoopTunnel" and x["is_source"] and x.get("frame_diagram") == wb]; gate("B W in-tunnel inner face", len(wi) == 1, wi)   # noqa: E702
    di = g._uid_index(TGT, "Diagram", wb)
    def ti(u, name, src): return next(r["i"] for r in g.node_terms_uid(TGT, di, g._node_index(TGT, di, u))[1] if r["name"] == name and bool(r["is_source"]) == src)   # noqa: E704
    c = g.create_control_nested(TGT, GT, ti(GT, "y", False)); R = rows(TGT)                      # noqa: E702
    R = Wr("SW.t <- Num (FMN in)", one(R, owner_uid=SW, term_name="t")["term_uid"], wi[0]["term_uid"])
    R = Wr("SW.s <- GT out (FMN in)", one(R, owner_uid=SW, term_name="s")["term_uid"], one(R, owner_uid=GT, is_source=True)["term_uid"])
    R = Wr("SW.f <- KMX", one(R, owner_uid=SW, term_name="f")["term_uid"], one(R, owner_uid=KMX, is_source=True)["term_uid"])
    R = Wr("AMM.array <- SW out (FMN out)", one(R, owner_uid=AMM, term_name="array")["term_uid"], one(R, owner_uid=SW, is_source=True)["term_uid"])
    i = g.create_indicator_nested(TGT, AMM, ti(AMM, "min value", True))
    pw = dict((int(r["uid"]), r["label"]) for r in g.panel_wiring(TGT)); B.update(ctl=c, ind=i, panel=pw); fact("B last / min / panel", (c, i, pw))   # noqa: E702
    gate("B last control + min indicator, err ''", c.get("created_uid") and i.get("created_uid") and not c.get("err") and not i.get("err"), (c, i))
    R = rows(TGT); B["classes"] = dict((k, sorted(set(x["owner_class"] for x in R if x["owner_uid"] == B[k]))) for k in ("GT", "SW", "KMX", "AMM"))
    B["classes"]["FMN"] = ["ForLoop"] if FMN in g.uids(TGT, "ForLoop") else []; fact("B node classes vs v8 (p4_gt_last Comparison, p4_sel_mask/p4_amm Function, p4_k_max DigitalNumericConstant, p4_f_min ForLoop)", B["classes"])   # noqa: E702
    lt = [g.tunnels(TGT, k) for k in range(len(g.report_all(TGT, "LoopTunnel")))]
    on = dict((t["uid"], sorted(set(x.get("frame_diagram") for x in R if x["owner_uid"] == t["uid"]))) for t in lt)
    B["tunnels"] = [(t["uid"], t["index_mode"], t["out_is_source"], on[t["uid"]]) for t in lt]; fact("B LoopTunnels (uid, IndexMode, out_is_source, diagrams)", B["tunnels"])   # noqa: E702
    fm = [t for t in B["tunnels"] if fmb in t[3]]
    ws = sorted(set(x["wire_uid"] for x in R if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT, "Wire")))
    B["rle"] = dict((w, g.wire_remove_loose_ends(TGT, w, index=WI.get(w))) for w in ws); fact("B Is Broken? per wire", [(w, r.get("broken_before")) for w, r in B["rle"].items()])   # noqa: E702
    es = B["es"] = g.exec_state(TGT)
    gate("B 3 FMN tunnels, every IndexMode 1", len(fm) == 3 and all(t[1] == 1 for t in fm), fm, need=False)
    gate("B every wire Is Broken? False", all(not r.get("broken_before") for r in B["rle"].values()), need=False)
    gate("B ExecState 1", es == 1, es)
    vi = g.lv().GetVIReference(TGT, "", False, 0); L, M, N = pw[int(c["created_uid"])], pw[int(i["created_uid"])], lab   # noqa: E702
    vi.SetControlValue(N, NUM); back = list(vi.GetControlValue(N)); arr = isinstance(vi.GetControlValue(L), (list, tuple)); B["runs"] = []   # noqa: E702
    gate("B Num reads back the 20-element list", back == NUM, back)
    for last, want in ((2, 3), (17, MAXV)):
        vi.SetControlValue(L, [last] * 20 if arr else last); g._run(vi); got = int(vi.GetControlValue(M)); B["runs"].append((last, want, got, list(vi.GetControlValue(N))))   # noqa: E702
        gate("B RUN last=%s -> min %s (got %s; last is array? %s)" % (last, want, got, arr), got == want, need=False)
    json.dump({"function": "For group inside a While body: 3 auto-index tunnels by connect_term_uid", "card": "139-1", "t": time.time(), "log": "tools/bench/diag_c139_1_run.log",
               "status": "PASS" if es == 1 and all(r[1] == r[2] for r in B["runs"]) else "FAIL", "out": B},
              open(os.path.join(HERE, "scratch_verify", "for_group_c139_1_%s.json" % TS), "w", encoding="utf-8"), default=str, indent=1)
def main():
    D.bench_prep.restart_labview(); g.reset(); time.sleep(3); gate("bed md5 before", md5(BED) == BEDM)   # noqa: E702
    stepA(); ldump(); g.reset(); D.bench_prep.restart_labview(); g.reset(); time.sleep(3); stepB()   # noqa: E702
if __name__ == "__main__":
    try:
        main()
    except Stop as e:
        print("STOP at the first unexpected result: %s" % e, flush=True)
    except Exception as e:                                                                      # noqa: BLE001
        traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300], need=False)   # noqa: E702
    finally:
        ldump(); g.reset()                                                                       # noqa: E702
        S5.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
        gate("C LabVIEW gone", "labview.exe" not in S5.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
        for p in SCR:
            for _ in range(5):
                try:
                    os.path.exists(p) and os.remove(p); break                                    # noqa: E702
                except OSError:
                    time.sleep(2)
        gate("C scratch files deleted", not any(os.path.exists(p) for p in SCR), SCR, need=False)
        gate("C bed md5 unchanged", md5(BED) == BEDM, need=False)
        bad = [k for k, v in S5.G.items() if not v]
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, [])), flush=True)
        sys.exit(1 if bad else 0)
