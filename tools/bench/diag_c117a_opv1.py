r"""diag_c117a_opv1 - card 117-1 S0a: claudeDev\OpWireJoints_v1.vi = a BYTE COPY of OpWireJoints_v0 (v0 kept, md5 15cf4971...) plus
(W1) PN #118 `error in (no error)` <- the Traverse's `error out` (review c116d-sweep :41-44, :95: v0 discarded the Traverse error);
(W2) a SECOND `Close Reference` (KernelBuilder_v1 #157, copy_by_index - the proven route of diag_c116d_opbuild.py close_ref :148-168)
whose `reference` is a BRANCH of the Traverse `References` ARRAY wire; (W3) its `error in` <- PN #118 `error out` (branch), so the array
is closed only AFTER the read; (W4) the old Close Reference #615 `error in` <- the new close's `error out` (the element #615 closes is
then already closed by the array close: a harmless, unwired error; the ORDER is fixed instead of racing).
FOUND FIRST: docs/REFERENCES.md 4a/4a-bis (no fleet op closes its Traverse array; the S0 For-Loop route was never built); connect_terminals
BRANCHES an already-wired SOURCE (tools/gscript.py:2762-2764); `Close Reference` terminals error out/error in (no error)/reference
(REFERENCES.md:168). Whether Close Reference takes an ARRAY of refnums is not on file: W2's ExecState answers it (a type clash = broken wire).
PREDICTION: V0 copy ES 1; M graph has ONE node with a `References` source (Traverse), PN #118 error in unwired; W1..W4 each ES 1;
A copy_by_index saved the VI (ES 1); C COLD ES 1 in a fresh LabVIEW; K cold wiring as W1..W4; v0 md5 unchanged; LabVIEW gone.
    py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_c117a_opv1.log -- py -u tools/bench/diag_c117a_opv1.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                         # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, os.path.dirname(HERE)); sys.path.insert(0, HERE)  # noqa: E702
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
CD = g.CLAUDEDEV
V0, V1, KB = (os.path.join(CD, n) for n in ("OpWireJoints_v0.vi", "OpWireJoints_v1.vi", "KernelBuilder_v1.vi"))
V0_MD5, PN, CR0 = "15cf497190fcd972407f1be109197b01", 118, 615
LAB_IN, LAB_OUT = os.path.join(HERE, "diag_c116d_oplabels.json"), os.path.join(HERE, "diag_c117a_oplabels.json")
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {}
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True); return bool(ok)  # noqa: E702


def sweep(t):
    out = {}
    for n in range(80):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            break
        out[int(uid)] = (n, rows)
    return out


def term(by, uid, name, src):
    return next((r for r in by[uid][1] if r["name"] == name and bool(r["is_source"]) == src), None)


def trav(by):
    t = [u for u, (_n, rows) in by.items() if any(r["name"] == "References" and r["is_source"] for r in rows)]
    return t[0] if len(t) == 1 else None


def finish(dst, added):
    print("  FACT  ES at finish entry, before any wire (review c117a-opv1 section 3): %r" % g.exec_state(dst), flush=True)
    by = sweep(dst)
    for u, (n, rows) in sorted(by.items()):
        print("  FACT  node #%s [%d] %r" % (u, n, [(r["i"], r["name"], int(bool(r["is_source"])), r["wire"]) for r in rows]), flush=True)
    tv, new = trav(by), [u for u in by if u in set(int(o["uid"]) for o in added)]
    ok = gate("M graph: one Traverse (References source) #%s, PN #%s error in unwired, #%s error in unwired, ONE new node %r" % (tv, PN, CR0, new),
              tv and len(new) == 1 and PN in by and CR0 in by and not term(by, PN, "error in (no error)", False)["wire"]
              and not term(by, CR0, "error in (no error)", False)["wire"])
    if not ok:
        return
    cr = LAB["close_ref_array"] = new[0]
    # RUN 2 ORDER (run 1, diag_c117a_opv1.log: W1 wired w664 but ES 0 - the copied Close Reference #630 still had its REQUIRED
    # `reference` unwired, so the VI was broken BEFORE W1; our script's order, not W1): W2 first makes the VI runnable, then W1/W3/W4.
    steps = (("W2 NEW Close Reference `reference` <- Traverse References (branch)", cr, "reference", tv, "References"),
             ("W1 PN error in <- Traverse error out", PN, "error in (no error)", tv, "error out"),
             ("W3 NEW Close Reference error in <- PN error out (branch)", cr, "error in (no error)", PN, "error out"),
             ("W4 old #615 error in <- NEW Close Reference error out", CR0, "error in (no error)", cr, "error out"))
    for lab, su, sn, so, sname in steps:
        by = sweep(dst)
        dw, es = g.connect_terminals(dst, by[su][0], term(by, su, sn, False)["i"], by[so][0], term(by, so, sname, True)["i"])
        by = sweep(dst)
        if not gate("%s: sink wired, ES 1" % lab, term(by, su, sn, False)["wire"] and es == 1, (dw, es, term(by, su, sn, False)["wire"], term(by, so, sname, True)["wire"])):
            return
    g.set_auto_error_handling(dst, False)          # review c117a-opv1: #615 now always closes an already-closed element; no dialog
    gate("W5 auto error handling OFF, ES 1", g.exec_state(dst) == 1)
    LAB["traverse"] = tv


def cold():
    by, tv, cr = sweep(V1), LAB.get("traverse"), LAB.get("close_ref_array")
    w = lambda u, n, s: (term(by, u, n, s) or {}).get("wire")                               # noqa: E731
    gate("K cold: NEW CR #%s reference wire == Traverse References wire; PN error in == Traverse error out wire; #615 error in == NEW CR error out" % cr,
         tv in by and cr in by and w(cr, "reference", False) and w(cr, "reference", False) == w(tv, "References", True)
         and w(PN, "error in (no error)", False) == w(tv, "error out", True) and w(cr, "error in (no error)", False) == w(PN, "error out", True)
         and w(CR0, "error in (no error)", False) == w(cr, "error out", True) and w(CR0, "reference", False) == w(PN, "reference out", True),
         [(u, [(r["name"], r["wire"]) for r in by[u][1]]) for u in (tv, cr, PN, CR0) if u in by])


try:
    gate("V0 v0 md5 pinned", md5(V0) == V0_MD5, md5(V0))
    os.path.exists(V1) and os.remove(V1); shutil.copyfile(V0, V1)                             # noqa: E702
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    gate("V1 byte copy ES 1", g.exec_state(V1) == 1 and md5(V1) == V0_MD5)
    idx = next((i, c) for c in ("Node", "Function") for i, o in enumerate(g.report(KB, c)) if int(o["uid"]) == 157)
    print("  FACT  KB #157 = %s[%d]" % (idx[1], idx[0]), flush=True)
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                        # noqa: E702
    add, sel = g.copy_by_index(KB, idx[1], idx[0], V1, expect_uid=157, finish=finish)
    gate("A copy_by_index (uid guard 157) finished and saved v1 at ES 1", sel == 157 and all(G.values()) and md5(V1) != V0_MD5, (sel, len(add), md5(V1)))
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                        # noqa: E702
    gate("C COLD ExecState 1 (fresh LabVIEW)", g.exec_state(V1) == 1, md5(V1))
    cold()
    lab = dict(json.load(open(LAB_IN, encoding="utf-8"))["OpWireJoints_v0"], **LAB)
    lab.update(controls=[r["label"] for r in g.panel_wiring(V1) if not r["indicator"]], md5=md5(V1), donor="OpWireJoints_v0.vi " + V0_MD5)
    json.dump({"OpWireJoints_v1": lab}, open(LAB_OUT, "w", encoding="utf-8"), indent=1)
    print("  FACT  labels written %r" % lab, flush=True)
except Exception as e:                                                                       # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("H LabVIEW gone; v0 md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
         and md5(V0) == V0_MD5)
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": V1, "md5": md5(V1)}] if os.path.exists(V1) and not bad else []
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
