r"""diag_c138_6_run.py - card 138-6 (PD312(c)(d)(e), docs/d1/ring-p4.md): scratch-only measurements, ONE LabVIEW run, order 0,1,3,4,2
(riskiest last; the run STOPS at the first failed gate). Bed never edited, never run; only the step-2 scratch VI is run.
FOUND FIRST: donor recipe = diag_c123_routes.py:20-36 (EMPTY_v0 + For + gscript.create_const_loop_term for_n, value read back by
read_const_value -> {representation, repr_name}); Mechanical Action writer + target = build_opstopmode_v0.py:55-231 (imported, its
build_writer/call/B reused, labels diag_c138_5_oplabels.json); bed delete = build_opfsinnertunnelconnect_v0.del_wire:336; Error List =
errorlist_check (diag_c137_7_types.py:66-70 form); wiring by terminal uid = gscript.connect_term_uid over allterms.read_terms rows
(diag_c137_7_types.py form; across a For border UNMEASURED - v8's tunnel ops compile to connect_nested_v1/cfw instead).
No I32-array control creator exists: Num = auto-indexed OUTPUT of a generator For (N = 20) fed by its `i` terminal when read_terms
lists one (owner = the For, source, on its body), else by an I32 0 constant (DonorSRInit_v0 #248); `last` = Create Control on Greater?.y
after x is wired (type read back from the control's value).
PREDICTION: 0 records copied, op_hygiene_check None for both, OpStopModeB_v0 opened by gscript.op() outside hygiene_probe.
1 DonorI32Max_v0: one new constant, value 2147483647, repr_name I32, ExecState 1, saved. 3 bed copy md5 == bed; w25415 deleted;
#10465 rows before = 3 (t10469 outer w25415, t10467/t10468 inner unwired); after: FACT (exists? rows) + Error List count (FACT).
4 scratch Boolean: Mechanical Action written 4 -> read 4; local read created; ExecState 0 (latch => broken) and EL items > 0.
2 every op err ''; LoopTunnels on FMN: 3 (2 in, 1 out) + 1 on FG; every IndexMode 1; every wire Is Broken? False; ExecState 1;
runs: Num=i: last 2 -> 3, last 19 -> 2147483647, last -1 -> 0 (Num=0: last -1 -> 0, last 0 -> 2147483647).
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c138_6_run.log -- py -u tools/bench/diag_c138_6_run.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import build_opstopmode_v0 as S5                                                              # noqa: E402 (main() guarded)
import allterms as AT                                                                         # noqa: E402
import build_track_v6_core as TB                                                              # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                                 # noqa: E402
import errorlist_check as EC                                                                  # noqa: E402
g, P, bench_prep, md5, gate, fact, Stop = S5.g, S5.P, S5.bench_prep, S5.md5, S5.gate, S5.fact, S5.Stop
CD, BED, BEDM, TS = g.CLAUDEDEV, S5.BED, S5.BED_MD5, time.strftime("%H%M%S")
DON = os.path.join(CD, "DonorI32Max_v0.vi"); MAXV = 2147483647                                 # noqa: E702
BEDC, BEDD = os.path.join(CD, "scratch_c138_6_bed_%s.vi" % TS), os.path.join(CD, "scratch_c138_6_bdon_%s.vi" % TS)
TGT4, TGT2 = os.path.join(CD, "scratch_c138_6_latch_%s.vi" % TS), os.path.join(CD, "scratch_c138_6_for_%s.vi" % TS)
SEL_D, I0_D = os.path.join(CD, "DonorErrSel_MergeErrors.vi"), os.path.join(CD, "DonorSRInit_v0.vi")
OUT, SCR = {}, S5.SCR
def ldump(): json.dump(OUT, open(os.path.join(HERE, "diag_c138_6_out.json"), "w", encoding="utf-8"), indent=1, default=str)   # noqa: E704
def rows(t): return AT.read_terms(t, op=AT.OP_ALLTERMS_V1)[0]                                  # noqa: E704
def one(rs, **kw):
    r = [x for x in rs if all(x.get(k) == v for k, v in kw.items())]
    gate("T one terminal %s" % kw, len(r) == 1, [(x["term_uid"], x["term_name"], x["wire_uid"]) for x in r][:5]); return r[0]   # noqa: E702
def el_count(W, tag):
    EC._lv_imports(); RR = {"gui_acts_outer": [], "errors": []}; EC.open_diagram(W, RR)        # noqa: E702
    r = EC.E.read(W, os.path.join(HERE, "errorlist_c138_6_%s_raw.json" % tag), log=lambda m: None, on_item=None)
    o = {"items": len(r.get("items") or []), "n": r.get("n_reported"), "classes": EC.class_counts(r.get("items")), "errors": (r.get("errors") or [])[:2],
         "first": [str(i)[:160] for i in (r.get("items") or [])[:4]]}
    fact("EL %s" % tag, o); return o                                                              # noqa: E702
def step0():
    for k in ("OpStopMode_v0", "OpStopModeB_v0"):
        shutil.copyfile(os.path.join(HERE, "hygiene_%s.json" % k), g.op_hygiene_record_path(os.path.join(CD, k + ".vi")))
        gate("0 %s record in op_hygiene/, op_hygiene_check None" % k, g.op_hygiene_check(os.path.join(CD, k + ".vi")) is None, g.op_hygiene_check(os.path.join(CD, k + ".vi")))
    S5.LAB.update(json.load(open(S5.LAB_P, encoding="utf-8"))); vi = g.op(S5.OPB)               # noqa: E702 - outside hygiene_probe
    gate("0 OpStopModeB_v0 opened by gscript.op() outside hygiene_probe", vi is not None)
def step1():
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), DON); g.open_panel(DON)   # noqa: E702
    f0 = g.uids(DON, "ForLoop"); g.for_loop(DON, (200, 200)); uf = sorted(g.uids(DON, "ForLoop") - f0)[0]   # noqa: E702
    c0 = g.uids(DON, "Constant"); r = g.create_const_loop_term(DON, "for_n", TB.walk(DON, 0)[uf][0], value=MAXV); new = sorted(g.uids(DON, "Constant") - c0)   # noqa: E702
    u = int(r.get("created_uid") or 0); rv = g.read_const_value(DON, u); OUT["donor"] = {"uid": u, "read": rv, "new": new, "create": r}   # noqa: E702
    fact("1 donor create/read", OUT["donor"])
    gate("1 exactly one new constant #%s == created uid" % u, u and new == [u] and not r.get("err"), (new, r))
    gate("1 value 2147483647, representation I32", rv.get("value") == MAXV and (rv.get("type") or {}).get("repr_name") == "I32" and not rv.get("err"), rv)
    gate("1 DonorI32Max_v0 ExecState 1", g.exec_state(DON) == 1); g.save(DON); g.close_panel(DON)   # noqa: E702
    OUT["donor"]["md5"] = md5(DON); gate("1 saved by script", os.path.getsize(DON) > 0, OUT["donor"]["md5"])   # noqa: E702
def step3():
    shutil.copyfile(BED, BEDC); SCR.append(BEDC); gate("3 bed byte copy md5 == bed", md5(BEDC) == BEDM)   # noqa: E702
    g.open_panel(BEDC); r0 = [x for x in rows(BEDC) if x["owner_uid"] == 10465]; OUT["t10465_before"] = r0; fact("3 #10465 rows before", r0)   # noqa: E702
    gate("3 #10465 has 3 rows, t10469 on w25415", len(r0) == 3 and any(x["term_uid"] == 10469 and x["wire_uid"] == 25415 for x in r0), r0)
    ok = C82.del_wire(BEDC, 25415, "3 "); gate("3 delete_wire w25415", ok and 25415 not in g.uids(BEDC, "Wire"))   # noqa: E702
    tun = g.uids(BEDC, "Tunnel"); r1 = [x for x in rows(BEDC) if x["owner_uid"] == 10465]
    OUT["t10465_after"] = {"exists_in_Traverse_Tunnel": 10465 in tun, "rows": r1, "es": g.exec_state(BEDC)}; fact("3 #10465 after delete", OUT["t10465_after"])   # noqa: E702
    OUT["el_bed"] = el_count(BEDC, "bed"); gate("3 bed md5 unchanged", md5(BED) == BEDM)   # noqa: E702
def step4():
    shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT4); SCR.append(TGT4); g.open_panel(TGT4)   # noqa: E702
    g.while_loop(TGT4, (300, 200)); g.create_const_loop_term(TGT4, "while_cond", 0, value=False)   # noqa: E702
    cu = int(g.build_property(TGT4, "VI Server:Control", [("6332000", True)], (700, 80))[-1]["uid"])
    for c in range(40):
        nu, rs = g.node_terms_uid(TGT4, 0, c)
        if nu == cu:
            g.create_control(TGT4, c, next(r["i"] for r in rs if not r["is_source"] and r["name"] not in S5.STD)); break   # noqa: E702
    g.delete_object(TGT4, "Property", [o["uid"] for o in g.report_all(TGT4, "Property")].index(cu)); g.remove_bad_wires_scripted(TGT4)   # noqa: E702
    gate("4 target (While + Boolean control) ExecState 1", g.exec_state(TGT4) == 1)
    wb, _l = S5.build_writer("OpStopModeB_v0", "scratch_c138_6_wB.vi", "VI Server:Boolean", S5.P_MECH, "pn")
    w = S5.wr(wb, "scratch_c138_6_wB", "OpStopModeB_v0", TGT4, 0, 4); r = S5.call(S5.OPB, S5.LAB["OpStopModeB_v0"], TGT4, 0)
    OUT["latch"] = {"write": w, "read": r}; gate("4 Mechanical Action written 4 -> read 4 (reader outside hygiene_probe)", r.get("v") == 4 and not w["err"] and not r["err"], (w, r))   # noqa: E702
    pi = [i for i, x in enumerate(g.panel_wiring(TGT4)) if not x["indicator"]]
    try:
        lr = g.create_local_read(TGT4, pi[0])
    except Exception as e:                                                                      # noqa: BLE001 - a refusal is itself the latch evidence
        lr = {"exception": repr(e)[:300]}
    OUT["latch"].update(local=lr, es=g.exec_state(TGT4), panel=g.panel_wiring(TGT4)); fact("4 local of a latched Boolean", OUT["latch"])   # noqa: E702
    OUT["latch"]["el"] = el_count(TGT4, "latch")
    gate("4 latch + local => refused, or ExecState 0 with Error List items > 0", "exception" in lr or lr.get("err") or (OUT["latch"]["es"] == 0 and OUT["latch"]["el"]["items"] > 0),
         (lr, OUT["latch"]["es"], OUT["latch"]["el"]))
def cp(dg, prim, pos, donor):
    return int(g.create_primitive_nested(TGT2, dg, prim, pos, donor=donor))
def step2():
    shutil.copyfile(BED, BEDD); SCR.append(BEDD); shutil.copyfile(os.path.join(CD, "EMPTY_v0.vi"), TGT2); SCR.append(TGT2); g.open_panel(TGT2)   # noqa: E702
    top = int(g.report_all(TGT2, "Diagram")[0]["uid"]); d0, f0 = g.uids(TGT2, "Diagram"), g.uids(TGT2, "ForLoop")   # noqa: E702
    g.for_loop(TGT2, (100, 300)); FG = sorted(g.uids(TGT2, "ForLoop") - f0)[0]; fgb = sorted(g.uids(TGT2, "Diagram") - d0)[0]   # noqa: E702
    g.create_const_loop_term(TGT2, "for_n", TB.walk(TGT2, 0)[FG][0], value=20); d1, f1 = g.uids(TGT2, "Diagram"), g.uids(TGT2, "ForLoop")   # noqa: E702
    g.for_loop(TGT2, (700, 300)); FMN = sorted(g.uids(TGT2, "ForLoop") - f1)[0]; fmb = sorted(g.uids(TGT2, "Diagram") - d1)[0]   # noqa: E702
    GT, AMM = cp(top, "Greater?", (500, 150), {"donor": BEDD, "uid": 11721}), cp(top, "Array Max & Min", (1200, 300), {"donor": BEDD, "uid": 10969})
    SW, KMX = cp(fmb, "Select", (120, 80), {"donor": SEL_D, "uid": 529}), cp(fmb, "const_donor", (20, 140), {"donor": DON, "uid": OUT["donor"]["uid"]})
    OUT["s2"] = {"top": top, "FG": FG, "fgb": fgb, "FMN": FMN, "fmb": fmb, "GT": GT, "AMM": AMM, "SW": SW, "KMX": KMX, "wires": {}}; fact("2 created", OUT["s2"])   # noqa: E702
    R = rows(TGT2); loopt = [x for x in R if x["owner_uid"] == FG]; fact("2 terminals owned by FG", loopt)   # noqa: E702
    iv = [x for x in loopt if x["is_source"] and x.get("frame_diagram") == fgb]
    if len(iv) == 1:
        num, OUT["s2"]["num"] = iv[0]["term_uid"], "i"
    else:
        k0 = cp(fgb, "const_donor", (40, 40), {"donor": I0_D, "uid": 248}); R = rows(TGT2); num, OUT["s2"]["num"] = one(R, owner_uid=k0, is_source=True)["term_uid"], "const0"   # noqa: E702
    def W(tag, snk, src):
        r = g.connect_term_uid(TGT2, snk, src); OUT["s2"]["wires"][tag] = r; fact("2 WIRE %s" % tag, r)   # noqa: E702
        gate("2 wire %s err '' and Is Broken? False" % tag, not r.get("err") and r.get("broken") is False, r); return rows(TGT2)   # noqa: E702
    R = W("GT.x <- Num (FG out)", one(R, owner_uid=GT, term_name="x")["term_uid"], num)
    tg = [x for x in R if x["owner_class"] == "LoopTunnel" and x["is_source"] and x.get("frame_diagram") == top]; gate("2 FG out tunnel outer face", len(tg) == 1, tg)   # noqa: E702
    di = g._uid_index(TGT2, "Diagram", top)
    def ti(u, name, src): return next(r["i"] for r in g.node_terms_uid(TGT2, di, g._node_index(TGT2, di, u))[1] if r["name"] == name and bool(r["is_source"]) == src)   # noqa: E704
    c = g.create_control_nested(TGT2, GT, ti(GT, "y", False)); R = rows(TGT2)                   # noqa: E702 - after x is wired, so y has adapted
    R = W("SW.t <- Num (FMN in)", one(R, owner_uid=SW, term_name="t")["term_uid"], tg[0]["term_uid"])
    R = W("SW.s <- GT out (FMN in)", one(R, owner_uid=SW, term_name="s")["term_uid"], one(R, owner_uid=GT, is_source=True)["term_uid"])
    R = W("SW.f <- KMX", one(R, owner_uid=SW, term_name="f")["term_uid"], one(R, owner_uid=KMX, is_source=True)["term_uid"])
    R = W("AMM.array <- SW out (FMN out)", one(R, owner_uid=AMM, term_name="array")["term_uid"], one(R, owner_uid=SW, is_source=True)["term_uid"])
    i = g.create_indicator_nested(TGT2, AMM, ti(AMM, "min value", True))
    pw = dict((int(r["uid"]), r["label"]) for r in g.panel_wiring(TGT2)); OUT["s2"].update(ctl=c, ind=i, panel=pw); fact("2 last control / min indicator", (c, i, pw))   # noqa: E702
    gate("2 control + indicator created, err ''", c.get("created_uid") and i.get("created_uid") and not c.get("err") and not i.get("err"), (c, i))
    lt = [g.tunnels(TGT2, k) for k in range(len(g.report_all(TGT2, "LoopTunnel")))]; OUT["s2"]["tunnels"] = lt
    fact("2 LoopTunnels (uid, IndexMode, out_is_source)", [(t["uid"], t["index_mode"], t["out_is_source"]) for t in lt])
    ws = sorted(set(x["wire_uid"] for x in rows(TGT2) if x["wire_uid"])); WI = dict((int(r["uid"]), k) for k, r in enumerate(g.report_all(TGT2, "Wire")))
    OUT["s2"]["rle"] = dict((w, g.wire_remove_loose_ends(TGT2, w, index=WI.get(w))) for w in ws); fact("2 Is Broken? per wire (RLE)", [(w, r.get("broken_before"), r.get("broken_after")) for w, r in OUT["s2"]["rle"].items()])   # noqa: E702
    es = g.exec_state(TGT2); OUT["s2"]["es"] = es
    gate("2 4 LoopTunnels, every IndexMode 1", len(lt) == 4 and all(t["index_mode"] == 1 for t in lt), [(t["uid"], t["index_mode"]) for t in lt], need=False)
    gate("2 every wire Is Broken? False", all(not r.get("broken_before") for r in OUT["s2"]["rle"].values()), need=False)
    gate("2 ExecState 1", es == 1, es)
    vi = g.lv().GetVIReference(TGT2, "", False, 0); L, M = pw[int(c["created_uid"])], pw[int(i["created_uid"])]   # noqa: E702
    arr = isinstance(vi.GetControlValue(L), (list, tuple)); cases = ((2, 3), (19, MAXV), (-1, 0)) if OUT["s2"]["num"] == "i" else ((-1, 0), (0, MAXV))
    OUT["s2"]["runs"] = []
    for last, want in cases:
        vi.SetControlValue(L, [last] * 20 if arr else last); g._run(vi); got = int(vi.GetControlValue(M)); OUT["s2"]["runs"].append((last, want, got))   # noqa: E702
        gate("2 RUN last=%s -> min %s (got %s; last control array? %s)" % (last, want, got, arr), got == want, need=False)
    json.dump({"function": "connect_term_uid across a For border + auto-index", "status": "PASS" if all(r[1] == r[2] for r in OUT["s2"]["runs"]) and es == 1 else "FAIL",
               "t": time.time(), "card": "138-6", "log": "tools/bench/diag_c138_6_run.log", "out": OUT["s2"]}, open(os.path.join(HERE, "scratch_verify", "for_group_c138_6_%s.json" % TS), "w", encoding="utf-8"), default=str, indent=1)
def main():
    bench_prep.restart_labview(); g.reset(); time.sleep(3); fact("handles after restart", bench_prep.labview_handles())   # noqa: E702
    gate("bed md5 before", md5(BED) == BEDM); step0(); step1(); step3(); ldump()                  # noqa: E702
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                          # noqa: E702 - fresh instance after the bed copy
    step4(); ldump(); step2()                                                                    # noqa: E702
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
        bad = [k for k, v in S5.G.items() if not v]; arts = [{"path": p, "md5": md5(p)} for p in (DON,) if os.path.exists(p)]   # noqa: E702
        print("=== GATES: %d pass / %d fail; failing: %s" % (len(S5.G) - len(bad), len(bad), bad), flush=True)
        print(P.result_line(P.make_result(len(S5.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
        sys.exit(1 if bad else 0)
