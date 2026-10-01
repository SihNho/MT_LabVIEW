r"""diag_c122_opbuild - card 122-3 (PD241(a)): claudeDev\OpConstInd_v0.vi = an INDICATOR born on a diagram CONSTANT, any nesting depth:
Traverse(`Class Name`)[`index`] -> TMSC (VI Server:Constant seed) -> PN [GObject.UID 632A813, Constant.Terminal 634AC04] -> Invoke
Terminal.Create Indicator 6349C02; refs closed: Traverse array (#630), typed constant ref (#615), the Terminal ref (CR1 <- invoke `reference
out`), the created object's ref (CR2 <- invoke `Create Indicator`).
FOUND FIRST: create_indicator_nested reaches Node / LoopTunnel / SelectorTunnel only (gscript.py:4005-4011; a Constant is not a Node,
result_122-1.json); OpTunnelInd_v0 = the same tail on Tunnel.Outside Terminal (tools/recipes/build_optunnelind.py) but no Close Reference;
OpConstValueN_v1's PN(Constant).'Terminal' source name (tools/recipes/build_opconstvaluen_v1.py:5). Donor + retype steps = the hygiene-PASS
OpWireJoints_v1 route of diag_c118_r1_opbuild.py:57-111 (#124 Traverse, #683 TMSC, #118 PN, #615/#630 closes, seed wire 279); the two new
Close References = KernelBuilder_v1 #157 through copy_by_index (diag_c117a_opv1.py:92-95).
PREDICTION: M donor md5; P new PN has UID + Terminal sources; S seed -> TMSC; K old PN gone + 4 links; I invoke wired (reference <- Terminal,
error in <- PN error out); C1 copy 1 finished ES 1 saved; C2 copy 2 finished ES 1 saved; COLD ES 1; labels file; LabVIEW gone.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c122_opbuild.log -- py -u tools/bench/diag_c122_opbuild.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
CD = g.CLAUDEDEV
DONOR, OP, KB = (os.path.join(CD, n) for n in ("OpWireJoints_v1.vi", "OpConstInd_v0.vi", "KernelBuilder_v1.vi"))
DONOR_MD5, LAB_P = "29dcb59f58d4d959e965f9f545abd50b", os.path.join(HERE, "diag_c122_oplabels.json")
PN_OLD, TMSC, TRAV, CR_REF, CR_ARR, SEED_W = 118, 683, 124, 615, 630, 279
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:300]), flush=True); return bool(ok)  # noqa: E702


def sweep(t):
    out = {}
    for n in range(80):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def ti(rows, name, src):
    return next(r for r in rows if r["name"] == name and bool(r["is_source"]) == src)


def panel(t, ind): return set(r["label"] for r in g.panel_wiring(t) if bool(r["indicator"]) == ind)


def idx(t, cls, uid): return [int(o["uid"]) for o in g.report_all(t, cls)].index(int(uid))


def link(t, su, sn, du, dn):
    by = sweep(t); g.connect_terminals(t, by[su][0], ti(by[su][1], sn, False)["i"], by[du][0], ti(by[du][1], dn, True)["i"])  # noqa: E702
    by = sweep(t); a, b = ti(by[su][1], sn, False)["wire"], ti(by[du][1], dn, True)["wire"]       # noqa: E702
    return gate("W %s.%s <- %s.%s" % (su, sn, du, dn), a and a == b, (a, b))


def finish1(op, added):
    p0 = g.uids(op, "Property"); g.build_property(op, "VI Server:Constant", [("632A813", False), ("634AC04", False)], (900, 450))  # noqa: E702
    pn = sorted(g.uids(op, "Property") - p0); by = sweep(op)                                 # noqa: E702
    srcs = [r["name"] for r in by[pn[0]][1] if r["is_source"]] if len(pn) == 1 else []
    if not gate("P one new Constant PN with UID + Terminal sources", len(pn) == 1 and "UID" in srcs and "Terminal" in srcs, (pn, srcs)):
        raise RuntimeError("P")
    pn = pn[0]; c0 = panel(op, False)                                                     # noqa: E702
    g.create_control(op, by[pn][0], ti(by[pn][1], "reference", False)["i"]); seed = sorted(panel(op, False) - c0)  # noqa: E702
    by = sweep(op); w_seed = ti(by[pn][1], "reference", False)["wire"]                     # noqa: E702
    ws = [int(o["uid"]) for o in g.report_all(op, "Wire")]; g.delete_object(op, "Wire", ws.index(int(w_seed)), verify=False)  # noqa: E702
    ws = [int(o["uid"]) for o in g.report_all(op, "Wire")]; g.delete_object(op, "Wire", ws.index(SEED_W), verify=False)  # noqa: E702
    g.wire_control(op, seed, "Function", idx(op, "Function", TMSC), ["target class"])
    by = sweep(op)
    if not gate("S seed %r -> TMSC #%s target class" % (seed, TMSC), len(seed) == 1 and ti(by[TMSC][1], "target class", False)["wire"], seed):
        raise RuntimeError("S")
    g.delete_object(op, "Property", idx(op, "Property", PN_OLD), verify=False); g.remove_bad_wires_scripted(op)  # noqa: E702
    ok = all([link(op, pn, "reference", TMSC, "specific class reference"), link(op, pn, "error in (no error)", TRAV, "error out"),
              link(op, CR_REF, "reference", pn, "reference out"), link(op, CR_ARR, "error in (no error)", pn, "error out")])
    inv = int(g.build_invoke(op, "VI Server:Terminal", "6349C02", (1150, 450))[-1]["uid"])
    cr1 = [int(o["uid"]) for o in added if int(o["uid"]) in sweep(op)]
    ok = ok and gate("C1 one copied Close Reference node %r" % cr1, len(cr1) == 1)
    ok = ok and all([link(op, inv, "reference", pn, "Terminal"), link(op, inv, "error in (no error)", pn, "error out"),
                     link(op, cr1[0], "reference", inv, "reference out"), link(op, cr1[0], "error in (no error)", inv, "error out")])
    g.set_auto_error_handling(op, False)
    LAB.update(pn=pn, inv=inv, cr1=cr1[0], seed=seed[0], class_="VI Server:Constant", props=["632A813", "634AC04"])
    gate("K old PN #%s gone, links made, ES 1" % PN_OLD, ok and PN_OLD not in sweep(op) and g.exec_state(op) == 1, g.exec_state(op))


def finish2(op, added):
    by = sweep(op); cr2 = [int(o["uid"]) for o in added if int(o["uid"]) in by]             # noqa: E702
    ok = gate("C2 one copied Close Reference node %r" % cr2, len(cr2) == 1)
    ok = ok and all([link(op, cr2[0], "reference", LAB["inv"], "Create Indicator"),
                     link(op, cr2[0], "error in (no error)", LAB["cr1"], "error out")])
    LAB["cr2"] = cr2[0]
    for name, k, u in (("UID", "UID", LAB["pn"]), ("error out", "Err", cr2[0])):
        i0 = panel(op, True); by = sweep(op); g.create_indicator(op, by[u][0], ti(by[u][1], name, True)["i"]); new = sorted(panel(op, True) - i0)  # noqa: E702
        ok = gate("I indicator on #%s %r -> %r" % (u, name, new), ok and len(new) == 1) and ok
        LAB[k] = new[0] if new else None
    LAB["controls"] = sorted(panel(op, False))
    gate("A assembled ES 1", ok and g.exec_state(op) == 1)


def kb157():
    return next((c, i) for c in ("Node", "Function") for i, o in enumerate(g.report(KB, c)) if int(o["uid"]) == 157)


def fresh():
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                     # noqa: E702


try:
    gate("M donor OpWireJoints_v1 md5 pinned", md5(DONOR) == DONOR_MD5, md5(DONOR))
    os.path.exists(OP) and os.remove(OP); shutil.copyfile(DONOR, OP)                        # noqa: E702
    fresh(); h0 = bench_prep.labview_handles(); c, i = kb157(); print("  FACT  KB #157 = %s[%d]" % (c, i), flush=True)  # noqa: E702
    fresh(); add, sel = g.copy_by_index(KB, c, i, OP, expect_uid=157, finish=finish1)       # noqa: E702
    gate("C1 copy 1 (uid guard 157) finished, saved, gates clean", sel == 157 and all(G.values()) and md5(OP) != DONOR_MD5, md5(OP))
    fresh(); add, sel = g.copy_by_index(KB, c, i, OP, expect_uid=157, finish=finish2)       # noqa: E702
    gate("C2 copy 2 finished, saved, gates clean", sel == 157 and all(G.values()), md5(OP))
    fresh(); gate("COLD ExecState 1 (fresh LabVIEW)", g.exec_state(OP) == 1, md5(OP))   # noqa: E702
    LAB.update(md5=md5(OP), donor="OpWireJoints_v1.vi " + DONOR_MD5)
    json.dump({"OpConstInd_v0": LAB}, open(LAB_P, "w", encoding="utf-8"), indent=1); print("  FACT  labels %r" % LAB, flush=True)  # noqa: E702
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("H LabVIEW gone; donor md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
         and md5(DONOR) == DONOR_MD5)
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": OP, "md5": md5(OP)}] if os.path.exists(OP) and not bad else []
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
