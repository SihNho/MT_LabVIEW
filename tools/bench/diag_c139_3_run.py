r"""diag_c139_3_run.py - card 139-3: scratch only (bed never opened; a byte copy serves as the Greater?/AMM donor as in 139-1 B).
FOUND FIRST: 139-1 B stopped at loop_in (error 1055, OpForLoopIn_v0) because loop_in's default src_cls 'SubVI' index 0
(gscript.py:1524) needs a SubVI the EMPTY_v0 scratch lacks (diag_c139_1_facts.md:27-32). Placing a SubVI = gscript.drop_subvi
(gscript.py:1577, OpSubVI_v1). Boolean constant creator = create_const_loop_term('while_cond', value=False) (gscript.py:2975,
measured 138-6 step 4); value read back = read_const_value -> read_bool_const (gscript.py:4428). Donor recipe = 138-6 step1.
Group = 139-1 stepB verbatim (diag_c139_1_run.py:47-100) + ONE unwired DonorI32Max_v0 SubVI on the top level before the While,
loop_in called exactly as stagexec.py:2653 (g.loop_in(route, W, di, pos), all defaults).
PREDICTION: 1 DonorBoolF_v0: exactly one new constant, BooleanConstant, value False, ExecState 1, saved by script.
2 one new SubVI on the top level; loop_in returns ONE ForLoop uid and ONE new Diagram (FACT: LoopTunnels added by loop_in).
3 every wire err '' and Is Broken? False; 3 FMN tunnels, IndexMode 1 each; ExecState 1.
4 runs Num=[-1,5,3,9,0,1,2,-7,4,8,6,7,10..17]: last 2 -> 3; last 17 -> 2147483647; scratch_verify record written.
5 LabVIEW gone; scratch files deleted; bed md5 unchanged.
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c139_3_run.log -- py -u tools/bench/diag_c139_3_run.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)                    # noqa: E702
import diag_c138_6_run as D                                                                    # noqa: E402 (main() guarded)
S5, g, TB, P = D.S5, D.g, D.TB, D.P                                                             # noqa: E702
gate, fact, md5, Stop, rows, one, cp = D.gate, D.fact, D.md5, D.Stop, D.rows, D.one, D.cp       # noqa: E702
CD, BED, BEDM, TS, MAXV = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S"), D.MAXV     # noqa: E702
DONB, EMPTY = os.path.join(CD, "DonorBoolF_v0.vi"), os.path.join(CD, "EMPTY_v0.vi")            # noqa: E702
BEDD = os.path.join(CD, "scratch_c139_3_bdon_%s.vi" % TS)
TGT = D.TGT2 = os.path.join(CD, "scratch_c139_3_for_%s.vi" % TS)
NUM = [-1, 5, 3, 9, 0, 1, 2, -7, 4, 8, 6, 7] + list(range(10, 18)); OUT, SCR = {}, S5.SCR       # noqa: E702
def ldump(): json.dump(OUT, open(os.path.join(HERE, "diag_c139_3_out.json"), "w", encoding="utf-8"), indent=1, default=str)   # noqa: E704
def step1():
    os.path.exists(DONB) and os.remove(DONB); shutil.copyfile(EMPTY, DONB); g.open_panel(DONB)   # noqa: E702
    w0 = g.uids(DONB, "WhileLoop"); g.while_loop(DONB, (200, 200)); uw = sorted(g.uids(DONB, "WhileLoop") - w0)[0]   # noqa: E702
    wi = [int(o["uid"]) for o in g.report_all(DONB, "WhileLoop")].index(uw); c0 = g.uids(DONB, "Constant")   # noqa: E702
    r = g.create_const_loop_term(DONB, "while_cond", wi, value=False); new = sorted(g.uids(DONB, "Constant") - c0)   # noqa: E702
    u = int(r.get("created_uid") or 0); rv = g.read_const_value(DONB, u); OUT["donor"] = {"uid": u, "read": rv, "new": new, "create": r, "while": uw}   # noqa: E702
    fact("1 DonorBoolF create/read", OUT["donor"])
    gate("1 exactly one new constant #%s == created uid" % u, u and new == [u] and not r.get("err"), (new, r))
    gate("1 BooleanConstant, value False read back", rv.get("cls") == "BooleanConstant" and rv.get("value") is not None and not rv.get("value") and not rv.get("err"), rv)
    gate("1 DonorBoolF_v0 ExecState 1", g.exec_state(DONB) == 1); g.save(DONB); g.close_panel(DONB)   # noqa: E702
    OUT["donor"]["md5"] = md5(DONB); gate("1 saved by script", os.path.getsize(DONB) > 0, OUT["donor"]["md5"])   # noqa: E702
def stepB():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); shutil.copyfile(EMPTY, TGT); SCR.append(TGT); g.open_panel(TGT)   # noqa: E702
    top = int(g.report_all(TGT, "Diagram")[0]["uid"]); s0 = g.uids(TGT, "SubVI")                  # noqa: E702
    g.drop_subvi(TGT, D.DON, 0, (900, 520)); SV = sorted(g.uids(TGT, "SubVI") - s0); fact("2 SubVI dropped (DonorI32Max_v0)", SV)   # noqa: E702
    gate("2 one SubVI on the top level", len(SV) == 1, SV)
    d0, f0 = g.uids(TGT, "Diagram"), g.uids(TGT, "ForLoop")                                     # noqa: E702
    g.for_loop(TGT, (60, 400)); FG = sorted(g.uids(TGT, "ForLoop") - f0)[0]; fgb = sorted(g.uids(TGT, "Diagram") - d0)[0]   # noqa: E702
    g.create_const_loop_term(TGT, "for_n", TB.walk(TGT, 0)[FG][0], value=20); d1 = g.uids(TGT, "Diagram")   # noqa: E702
    g.while_loop(TGT, (500, 100)); W = sorted(g.uids(TGT, "WhileLoop"))[0]; wb = sorted(g.uids(TGT, "Diagram") - d1)[0]   # noqa: E702
    wc = g.create_const_loop_term(TGT, "while_cond", 0, value=True); d2, lt0 = g.uids(TGT, "Diagram"), g.uids(TGT, "LoopTunnel")   # noqa: E702
    di = g._uid_index(TGT, "Diagram", wb); FMN = g.loop_in("for", TGT, di, (250, 150))         # noqa: E702 - stagexec.py:2653 form
    nb = sorted(g.uids(TGT, "Diagram") - d2); lt1 = sorted(g.uids(TGT, "LoopTunnel") - lt0)      # noqa: E702
    OUT["loop_in"] = {"ret": FMN, "new_diagrams": nb, "new_looptunnels": lt1, "is_for": FMN in g.uids(TGT, "ForLoop") if isinstance(FMN, int) else False}
    fact("2 loop_in result (ret, new Diagram, new LoopTunnels)", OUT["loop_in"])
    gate("2 loop_in: one ForLoop uid, one new Diagram", OUT["loop_in"]["is_for"] and len(nb) == 1, OUT["loop_in"]); fmb = nb[0]   # noqa: E702
    k0, GH = cp(fgb, "const_donor", (40, 40), {"donor": D.I0_D, "uid": 248}), cp(top, "Greater?", (300, 420), {"donor": BEDD, "uid": 11721})
    GT, AMM = cp(wb, "Greater?", (60, 60), {"donor": BEDD, "uid": 11721}), cp(wb, "Array Max & Min", (700, 150), {"donor": BEDD, "uid": 10969})
    SW, KMX = cp(fmb, "Select", (120, 80), {"donor": D.SEL_D, "uid": 529}), cp(fmb, "const_donor", (20, 140), {"donor": D.DON, "uid": 127})
    B = OUT["B"] = {"top": top, "SV": SV, "FG": FG, "fgb": fgb, "W": W, "wb": wb, "wc": wc, "FMN": FMN, "fmb": fmb, "k0": k0, "GH": GH, "GT": GT,
                    "AMM": AMM, "SW": SW, "KMX": KMX, "wires": {}}; fact("3 created", B)           # noqa: E702
    def Wr(tag, snk, src):
        r = g.connect_term_uid(TGT, snk, src); B["wires"][tag] = r; fact("3 WIRE %s" % tag, r)   # noqa: E702
        gate("3 wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r); return rows(TGT)   # noqa: E702
    R = Wr("GH.y <- k0 (FG out)", one(rows(TGT), owner_uid=GH, term_name="y")["term_uid"], one(rows(TGT), owner_uid=k0, is_source=True)["term_uid"])
    nx = TB.walk(TGT, 0)[GH][0]; tx = next(r["i"] for r in g.node_terms_uid(TGT, 0, nx)[1] if r["name"] == "x" and not r["is_source"])   # noqa: E702
    new, lab = g.create_control(TGT, nx, tx)
    R = rows(TGT); w = one(R, owner_uid=GH, term_name="x")["wire_uid"]; num = one(R, wire_uid=w, is_source=True); B["num"] = (new, lab, num)   # noqa: E702
    fact("3 Num control on GH.x", B["num"]); gate("3 Num control created and wired to GH.x", new and w, B["num"])   # noqa: E702
    R = Wr("GT.x <- Num (W in)", one(R, owner_uid=GT, term_name="x")["term_uid"], num["term_uid"])
    wi = [x for x in R if x["owner_class"] == "LoopTunnel" and x["is_source"] and x.get("frame_diagram") == wb]; gate("3 W in-tunnel inner face", len(wi) == 1, wi)   # noqa: E702
    dw = g._uid_index(TGT, "Diagram", wb)
    def ti(u, name, src): return next(r["i"] for r in g.node_terms_uid(TGT, dw, g._node_index(TGT, dw, u))[1] if r["name"] == name and bool(r["is_source"]) == src)   # noqa: E704
    c = g.create_control_nested(TGT, GT, ti(GT, "y", False)); R = rows(TGT)                      # noqa: E702
    R = Wr("SW.t <- Num (FMN in)", one(R, owner_uid=SW, term_name="t")["term_uid"], wi[0]["term_uid"])
    R = Wr("SW.s <- GT out (FMN in)", one(R, owner_uid=SW, term_name="s")["term_uid"], one(R, owner_uid=GT, is_source=True)["term_uid"])
    R = Wr("SW.f <- KMX", one(R, owner_uid=SW, term_name="f")["term_uid"], one(R, owner_uid=KMX, is_source=True)["term_uid"])
    R = Wr("AMM.array <- SW out (FMN out)", one(R, owner_uid=AMM, term_name="array")["term_uid"], one(R, owner_uid=SW, is_source=True)["term_uid"])
    i = g.create_indicator_nested(TGT, AMM, ti(AMM, "min value", True))
    pw = dict((int(r["uid"]), r["label"]) for r in g.panel_wiring(TGT)); B.update(ctl=c, ind=i, panel=pw); fact("3 last / min / panel", (c, i, pw))   # noqa: E702
    gate("3 last control + min indicator, err ''", c.get("created_uid") and i.get("created_uid") and not c.get("err") and not i.get("err"), (c, i))
    R = rows(TGT); lt = [g.tunnels(TGT, k) for k in range(len(g.report_all(TGT, "LoopTunnel")))]
    on = dict((t["uid"], sorted(set(x.get("frame_diagram") for x in R if x["owner_uid"] == t["uid"]))) for t in lt)
    B["tunnels"] = [(t["uid"], t["index_mode"], t["out_is_source"], on[t["uid"]]) for t in lt]; fact("3 LoopTunnels (uid, IndexMode, out_is_source, diagrams)", B["tunnels"])   # noqa: E702
    fm = [t for t in B["tunnels"] if fmb in t[3]]; B["sv_rows"] = [x for x in R if x["owner_uid"] == SV[0]]; fact("3 SubVI terminal rows", B["sv_rows"])   # noqa: E702
    ws = sorted(set(x["wire_uid"] for x in R if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT, "Wire")))
    B["rle"] = dict((w, g.wire_remove_loose_ends(TGT, w, index=WI.get(w))) for w in ws); fact("4 Is Broken? per wire", [(w, r.get("broken_before")) for w, r in B["rle"].items()])   # noqa: E702
    es = B["es"] = g.exec_state(TGT)
    gate("3 3 FMN tunnels, every IndexMode 1", len(fm) == 3 and all(t[1] == 1 for t in fm), fm, need=False)
    gate("4 every wire Is Broken? False", all(not r.get("broken_before") for r in B["rle"].values()), need=False)
    gate("4 ExecState 1", es == 1, es)
    vi = g.lv().GetVIReference(TGT, "", False, 0); L, M, N = pw[int(c["created_uid"])], pw[int(i["created_uid"])], lab   # noqa: E702
    vi.SetControlValue(N, NUM); back = list(vi.GetControlValue(N)); arr = isinstance(vi.GetControlValue(L), (list, tuple)); B["runs"] = []   # noqa: E702
    gate("4 Num reads back the 20-element list", back == NUM, back)
    for last, want in ((2, 3), (17, MAXV)):
        vi.SetControlValue(L, [last] * 20 if arr else last); t0 = time.time(); g._run(vi); got = int(vi.GetControlValue(M))   # noqa: E702
        B["runs"].append((last, want, got, round(time.time() - t0, 2)))
        gate("4 RUN last=%s -> min %s (got %s; last is array? %s)" % (last, want, got, arr), got == want, need=False)
    json.dump({"function": "loop_in('for') in a While body with a SubVI present + 3 auto-index tunnels by connect_term_uid", "card": "139-3", "t": time.time(),
               "log": "tools/bench/diag_c139_3_run.log", "status": "PASS" if es == 1 and all(r[1] == r[2] for r in B["runs"]) else "FAIL", "out": B},
              open(os.path.join(HERE, "scratch_verify", "for_group_c139_3_%s.json" % TS), "w", encoding="utf-8"), default=str, indent=1)
    gate("4 scratch_verify record written", True)
def main():
    D.bench_prep.restart_labview(); g.reset(); time.sleep(3); gate("bed md5 before", md5(BED) == BEDM)   # noqa: E702
    step1(); ldump(); stepB()                                                                    # noqa: E702
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
        gate("5 LabVIEW gone", "labview.exe" not in S5.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower(), need=False)
        for p in SCR:
            for _ in range(5):
                try:
                    os.path.exists(p) and os.remove(p); break                                    # noqa: E702
                except OSError:
                    time.sleep(2)
        gate("5 scratch files deleted", not any(os.path.exists(p) for p in SCR), SCR, need=False)
        gate("5 bed md5 unchanged", md5(BED) == BEDM, need=False)
        bad = [k for k, v in S5.G.items() if not v]; arts = [{"path": p, "md5": md5(p)} for p in (DONB,) if os.path.exists(p)]   # noqa: E702
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)
