r"""build_op_const_loopterm_77 - task 77-2 (m8 plan PD20(a)+(c)): a constant on a LOOP-OWNED terminal.
    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/const_loopterm_77.log -- py -u tools/bench/build_op_const_loopterm_77.py
FOUND FIRST: OpCreateConstOnTerm_v0 (6349C00 on WhileLoop[i].Diagram.Nodes[n].Terminals[t], 22/0) cannot reach a
top-level For N or a conditional terminal; OpCreateIndicator_v0 has the top-level Nodes[]->Terminals[] ladder;
OpCreateConstOnTerm_v0 already holds WhileLoop `Loop End Ref` 6362C00 (from OpStopFromNode_v0). NAMES.md:313: an
empty For loop's Terminals[0] = N. build_d1_v0.loop_end_ref reads a cond terminal. So two ops, no new route:
 A OpCreateConstTop_v0     = OpCreateIndicator_v0, invoke 6349C02 -> 6349C00 (+Value ctl, UID + error indicators)
 B OpCreateConstLoopEnd_v0 = OpCreateConstOnTerm_v0, invoke `reference` re-fed from LpEndRef
PREDICTION: A1/B1 ops ExecState 1 and saved; T1 For N constant = DigitalNumericConstant, N wired; T2 cond constant
wired (cond wire != 0); T3 body-node control constant -7; T4 scratch ExecState 1 warm; H 20 calls handles +-100 and
refs live 0; C (after save + LabVIEW restart) ExecState 1, N text '1', body text '-7', wires unchanged, cond wired.
"""
import json, os, shutil, subprocess, sys, time
sys.path[:0] = [os.path.join(os.path.dirname(os.path.abspath(__file__)), p) for p in ("..", ".", "../recipes")]
import gscript as g, protocol                                                      # noqa: E401,E402
import build_opcreateconstonterm_v0 as C                                           # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                      # noqa: E402
from build_d1_v0 import loop_end_ref                                               # noqa: E402
from bench_prep import labview_handles, restart_labview                            # noqa: E402
D = g.CLAUDEDEV
OPA, OPB = g.OP_CONST_TOP, g.OP_CONST_LOOPEND
DON_A, DON_B = os.path.join(D, "OpCreateIndicator_v0.vi"), os.path.join(D, "OpCreateConstOnTerm_v0.vi")
ST = time.strftime("%H%M%S")
MD5_A, MD5_B = "a25cfa393eb33f0bf68485476bb09269", "c1c9d89f5dd6cc72d60bc28b91486642"  # task_77-3 inputs
S, S2 = os.path.join(D, "SCRATCH_cl77_%s.vi" % ST), os.path.join(D, "SCRATCH_cl77h_%s.vi" % ST)
R, P, F = {}, [], []
def gate(n, ok, d=""):
    (P if ok else F).append(n); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", n, d), flush=True); return ok
def src_of_ref(opx):
    wk = C.walk(opx); inv = [u for u, (n, l, r) in wk.items() if l == "Invoke Node"]
    w = C.term(wk[inv[0]][2], "reference", False)["wire"] if len(inv) == 1 else None
    s = [(u, r["name"]) for u, (n, l, rr) in wk.items() for r in rr if u not in inv and r["wire"] == w and r["is_source"]]
    return inv, w, s
def fresh_copy(donor, opx):
    C.OP = opx
    if os.path.exists(opx): os.remove(opx)
    shutil.copyfile(donor, opx); time.sleep(0.3); g.open_panel(opx); time.sleep(0.5)
def finish(opx, tag):
    g.set_auto_error_handling(opx, False); es = g.exec_state(opx)
    if gate(tag + " op ExecState 1 -> saved", es == 1, "ExecState %s" % es): g.save(opx)
    g.close_panel(opx); return es == 1
def build_a():
    fresh_copy(DON_A, OPA); inv, w, s = src_of_ref(OPA)
    if not gate("A0 donor has 1 Invoke fed by one source", len(inv) == 1 and len(s) == 1, "%s w%s %s" % (inv, w, s)): return None
    g.delete_object(OPA, "Invoke", C.idx(OPA, "Invoke", inv[0]), verify=False); g.remove_bad_wires_scripted(OPA)
    new = g.build_invoke(OPA, "VI Server:Terminal", "6349C00", (1500, 1600))[-1]["uid"]
    C.connect(s[0][0], s[0][1], new, "reference", tag="A ")
    wk = C.walk(OPA); vrow = C.term(wk[new][2], "Value", False)
    g.create_control(OPA, wk[new][0], vrow["i"])
    pu = g.build_property(OPA, "VI Server:GObject", [("632A813", False)], (1950, 1600))[-1]["uid"]
    C.connect(new, "Create Constant", pu, "reference", tag="A ")
    lab = {}
    for u, nm in ((pu, None), (new, "error out")):
        wk = C.walk(OPA); t = next(r["i"] for r in wk[u][2] if r["is_source"] and (r["name"] == nm if nm else r["name"] not in ("reference out", "error out")))
        b = {r["uid"] for r in g.panel_wiring(OPA)}; g.create_indicator(OPA, wk[u][0], t)
        lab["err_ind" if nm else "uid_ind"] = [r["label"] for r in g.panel_wiring(OPA) if r["uid"] not in b][0]
    lab["value_ctl"] = "Value"; R["census_A"] = [(r["i"], r["name"], r["is_source"]) for r in C.walk(OPA)[new][2]]
    return lab if finish(OPA, "A1") else None
def build_b():
    fresh_copy(DON_B, OPB); inv, w, s = src_of_ref(OPB)
    wk = C.walk(OPB); pn = [u for u, (n, l, rr) in wk.items() if any(r["name"] == "LpEndRef" and r["is_source"] for r in rr)]
    if not gate("B0 donor: 1 Invoke, 1 LpEndRef property node", len(inv) == 1 and len(pn) == 1, "%s %s w%s" % (inv, pn, w)): return None
    C82.del_wire(OPB, w, "B"); C.connect(pn[0], "LpEndRef", inv[0], "reference", branch=True, tag="B ")  # LpEndRef already feeds the donor's readers (run 1)
    lab = json.load(open(C.MAP_OUT, encoding="utf-8"))
    return {k: lab[k] for k in ("uid_ind", "err_ind", "value_ctl")} if finish(OPB, "B1") else None
def main():
    h0 = labview_handles(); R["handles_start"] = h0
    if all(os.path.exists(p) and C.md5(p) == m for p, m in ((OPA, MD5_A), (OPB, MD5_B))) and os.path.exists(g.CONST_LOOPTERM_LABELS):
        gate("A1/B1 ops reused unchanged (md5 == card 77-3)", True)  # 77-3: no rebuild, no re-save
    else:
        labs = {"for_n": build_a(), "while_cond": build_b()}
        if not all(labs.values()): return
        json.dump(labs, open(g.CONST_LOOPTERM_LABELS, "w"), indent=1)
    shutil.copyfile(C.EMPTY, S); time.sleep(0.3); g.open_panel(S)
    d0 = g.uids(S, "Diagram"); g.while_loop(S, (600, 200)); nd = g.new_since(S, "Diagram", d0); Du = nd[0]["uid"]
    iD = [o["uid"] for o in g.report_all(S, "Diagram")].index(Du); s0 = g.uids(S, "SubVI")
    g.drop_subvi(S, C.NUMVI, iD, (80, 80)); SVu = g.new_since(S, "SubVI", s0)[0]["uid"]
    f0 = g.uids(S, "ForLoop"); g.for_loop(S, (200, 200)); Fu = g.new_since(S, "ForLoop", f0)[0]["uid"]
    iD = [o["uid"] for o in g.report_all(S, "Diagram")].index(Du); R["body_diag"] = [Du, iD, SVu]  # 77-3: re-read by uid (NAMES.md:299)
    wt = C.walk(S); nF, rowsF = wt[Fu][0], wt[Fu][2]; R["for_terms"] = rowsF
    c0 = g.uids(S, "Constant"); ra = g.create_const_loop_term(S, "for_n", nF, 1.0, term_index=rowsF[0]["i"])
    nA = g.new_since(S, "Constant", c0); wN = C.walk(S)[Fu][2][0]["wire"]; R["A"] = [ra, nA, wN]
    gate("T1 For N: inv_err '' + 1 DigitalNumericConstant + N wired", not ra["inv_err"] and len(nA) == 1 and nA[0].get("class") == "DigitalNumericConstant" and wN != 0, repr(R["A"])[:300])
    li = 0; c0 = g.uids(S, "Constant"); rb = g.create_const_loop_term(S, "while_cond", li, True)
    nB = g.new_since(S, "Constant", c0); le = loop_end_ref(S, li); R["B"] = [rb, nB, le]
    gate("T2 While cond: inv_err '' + 1 constant + cond wired", not rb["inv_err"] and len(nB) == 1 and le["cond_wire_uid"] != 0, repr(R["B"])[:300])
    wb = C.B.walk(S, iD)
    if not gate("T3a body diagram (re-read by uid) holds the NUMVI node", SVu in wb, "Du %s iD %s SV %s keys %s" % (Du, iD, SVu, list(wb))): return
    ni, rr = wb[SVu][0], wb[SVu][2]
    tc = next(r["i"] for r in rr if "code" in r["name"].lower() and not r["is_source"])
    C.OP = DON_B  # control = the unmodified OpCreateConstOnTerm_v0 (fresh_copy re-points C.OP at OPB)
    c0 = g.uids(S, "Constant"); rc = C.create_const_on_term(S, li, ni, tc, json.load(open(C.MAP_OUT)), value=-7.0)
    nC = g.new_since(S, "Constant", c0); R["Cctl"] = [rc, nC]
    gate("T3 control: body-node constant via OpCreateConstOnTerm_v0", not rc["inv_err"] and len(nC) == 1, repr(R["Cctl"])[:300])
    es = g.exec_state(S); gate("T4 scratch ExecState 1 warm", es == 1, "ExecState %s" % es)
    uids = {"N": nA[0]["uid"] if nA else 0, "cond": nB[0]["uid"] if nB else 0, "body": nC[0]["uid"] if nC else 0}
    R["warm_read"] = {k: C.read_const(S, v) for k, v in uids.items() if v}
    if es == 1: g.save(S)
    g.close_panel(S)
    shutil.copyfile(C.EMPTY, S2); time.sleep(0.3); g.open_panel(S2); g.while_loop(S2, (600, 200))
    h1 = labview_handles(); hr = [g.create_const_loop_term(S2, "while_cond", 0, True)["inv_err"][:60] for _ in range(20)]
    h2 = labview_handles(); rc2 = g.ref_counts(); g.close_panel(S2); R["H"] = [h1, h2, hr, rc2]
    gate("H1 20 verb calls: handles flat +-100", h1 and h2 and abs(h2 - h1) <= 100, "%s -> %s errs %s" % (h1, h2, sorted(set(hr))))
    gate("H2 refs opened == closed", rc2.get("live") == 0, repr(rc2))
    restart_labview(); g.reset(); time.sleep(3)
    es = g.exec_state(S); gate("C0 COLD ExecState 1", es == 1, "ExecState %s" % es)
    cr = {k: C.read_const(S, v) for k, v in uids.items() if v}; R["cold_read"] = cr
    wN2 = C.walk(S)[Fu][2][0]["wire"]; le2 = loop_end_ref(S, li); R["cold_cond"] = le2
    gate("C1 COLD For N constant text '1', drives N's wire", str(cr.get("N", {}).get("text", "")).strip() == "1" and cr["N"].get("wire") == wN2 != 0, "%r wN %s" % (cr.get("N"), wN2))
    gate("C2 COLD body constant text '-7'", str(cr.get("body", {}).get("text", "")).strip() == "-7", repr(cr.get("body")))
    gate("C3 COLD cond terminal wired", le2["cond_wire_uid"] != 0, repr(le2))
    R["cond_class"] = [o for o in g.report_all(S, "Constant") if o["uid"] == uids["cond"]]
    gate("C4 COLD cond constant class BooleanConstant", [o.get("class") for o in R["cond_class"]] == ["BooleanConstant"], repr(R["cond_class"]))
    try: g.close_panel(S)  # cold instance never opened S's panel -> LabVIEW 1149 (run 77c :15); teardown only
    except Exception as e:  # narrowed per archive/peer/2026-09-25-const-loopterm-77c.md: only 1149 (0x47D) is expected
        R["cold_close_panel"] = str(e)[:300]
        if "0x47D" not in str(e): raise
    gate("C5 cold teardown close_panel: none or 1149 only", "0x47D" in R.get("cold_close_panel", "0x47D"), R.get("cold_close_panel", "no exception"))
if __name__ == "__main__":
    t0 = time.time()
    try: main()
    except Exception as e: gate("X no unhandled exception", False, "%s: %s" % (type(e).__name__, str(e)[:250]))
    finally:
        R["ref_counts_end"] = g.ref_counts(); g.reset()
        subprocess.call(["taskkill", "/IM", "LabVIEW.exe", "/F"]); time.sleep(4)
        for p in (S, S2):
            if os.path.exists(p): os.remove(p)
        gate("Z scratches deleted", not os.path.exists(S) and not os.path.exists(S2))
        gone = b"LabVIEW.exe" not in subprocess.run(["tasklist"], capture_output=True).stdout
        gate("Z LabVIEW closed and verified gone", gone)
        R.update(passes=P, fails=F, elapsed_s=round(time.time() - t0))
        json.dump(R, open(os.path.join(os.path.dirname(__file__), "const_loopterm_77.json"), "w"), indent=1, default=str)
        arts = [{"path": p, "md5": C.md5(p)} for p in (OPA, OPB) if os.path.exists(p)]
        print(protocol.result_line(protocol.make_result(len(P), len(F), F[0] if F else None, arts)), flush=True)
    sys.exit(1 if F else 0)
