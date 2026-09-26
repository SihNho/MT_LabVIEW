r"""diag_c92b_anythread.py - card 92-2 (PD199(a)): claudeDev\D1_s1_t0at_<ts>.vi = BYTE COPY of D1_s1_t0_20260926_055551.vi
(md5 25ea4f7d...) with `Any Thread?` (CallLibrary 636D403) set True on its 12 CLFN stamp nodes and NOTHING else.
FOUND FIRST: no WRITER for a CallLibrary property exists (grep 636D403 tools/: only the reader OpCLFNThread_v0.vi, card 92-1;
build_clfn's `reentrant` goes to NI's import-wizard `Reentrant` global and left 636D403 False - t0_clfn_thread_92.json).
Phase A builds the writer op claudeDev\OpCLFNThreadSet_v0.vi = byte copy of the reader OpCLFNThread_v0.vi (Traverse(Class
Name,index) -> Index Array -> TMSC(CallLibrary) -> read PN {Re-entrant, LibPath, CallConvention} + GObject.UID PN) plus a
WRITE property node [(636D403, True)] fed by a branch of the TMSC output, its value from a new boolean control
(Terminal.Create Control), and its `error out` wired into the read PN's `error in` so the read (same op run) happens
AFTER the write. Same route as diag_c92_clfn_thread.py (gscript only, no stagekit: not a stage script; ExecState is read
after every edit). Phase B self-tests the writer ON THE COPY (negative case, toggle False->True, 20 calls handle-flat);
phase C reads the copy back with the SEPARATE reader op; D counts + computation_diff(S1,copy) vs t0's own cdiff;
E saves by script; F cold re-open in a fresh LabVIEW.
PREDICTION CONTRACT (GATE lines):
 C0 t0 md5 == 25ea4f7d  C1 copy is a byte copy (md5 == t0's)
 A1 writer copy ES 1  A2 write PN built with ONE sink `Re-entrant` (build_property write-mode post-condition)
 A3 boolean control created on that sink  A4 TMSC out -> write PN reference (branch), write error out -> read PN error in: ES 1
 A5 COM save  A6 cold ES 1
 B1 negative: index 12 on the copy -> error text, no exception  B2 toggle uid[0]: write False reads False, write True reads True
 B3 20 write calls: handles flat (|delta| <= 100)  B4 write True on all 12: in-op readback True 12/12, uid echo 12/12
 C1 SEPARATE reader (OpCLFNThread_v0): Any Thread? True 12/12, uid echo 12/12, uids == t0's 12
 D1 per-class object counts copy == t0 (Node, Wire, CallLibrary, DigitalNumericConstant, WhileLoop, ForLoop, SubVI, Diagram, LoopTunnel)
 D2 computation_diff(S1, copy): 0 rows, 0 removed, 24 added == the same 24 nodes as t0's cdiff (t0_sites_s1_step3c_r2.json)
 E1 ES 1 warm  E2 saved by script, md5 != t0's  E3 t0 md5 unchanged
 F1 cold ES 1 in a fresh LabVIEW  F2 cold reader True 12/12  F3 t0 md5 unchanged  F4 LabVIEW gone
    py tools/bgrun.py --material --max-min 40 --log tools/bench/diag_c92b_anythread.log -- py -u tools/bench/diag_c92b_anythread.py [--rebuild]
"""
import hashlib, json, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
for p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes"), os.path.join(ROOT, "tools", "gpu")):
    sys.path.insert(0, p)
import protocol as P                                                            # noqa: E402
import gscript as g                                                             # noqa: E402
import vigraph as V                                                             # noqa: E402
import bench_prep                                                               # noqa: E402
CD = g.CLAUDEDEV
T0VI = os.path.join(CD, "D1_s1_t0_20260926_055551.vi"); T0_MD5 = "25ea4f7d10d91c41c4b5de64f850c945"
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"; S1VI = os.path.join(CD, "D1_s1_copy.vi")
READER = os.path.join(CD, "OpCLFNThread_v0.vi"); READER_MD5 = "a7308101be3a43eab60cbef3137ee376"
WRITER = os.path.join(CD, "OpCLFNThreadSet_v0.vi")
RLAB = json.load(open(os.path.join(HERE, "opclfnthread_labels.json"))); WLAB_P = os.path.join(HERE, "opclfnthreadset_labels.json")
STAMP = time.strftime("%Y%m%d_%H%M%S"); COPY = os.path.join(CD, "D1_s1_t0at_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c92b_anythread.json")
T0_CDIFF = json.load(open(os.path.join(HERE, "t0_sites_s1_step3c_r2.json")))["cdiff"]
T0_ADDED = sorted(a["node"] for a in T0_CDIFF["added"])
CLASSES = ("Node", "Wire", "CallLibrary", "DigitalNumericConstant", "WhileLoop", "ForLoop", "SubVI", "Diagram", "LoopTunnel")
REBUILD = "--rebuild" in sys.argv
g._run.__defaults__ = (6.0, 120.0)
G, F = {}, {"steps": []}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, detail=""):
    G[k] = bool(ok); print("GATE %-64s %s  %s" % (k, "PASS" if ok else "FAIL", str(detail)[:300]), flush=True); return bool(ok)


def fact(s): print("  " + s, flush=True); F["steps"].append(s)


def idx(op, cls, uid): return [o["uid"] for o in g.report_all(op, cls)].index(uid)


def node_terms_of(op, uid):
    for cand in range(60):
        nu, rows = g.node_terms_uid(op, 0, cand)
        if not nu: return None, None
        if nu == uid: return cand, rows
    return None, None


def build_writer():
    if os.path.exists(WRITER): os.remove(WRITER)
    shutil.copyfile(READER, WRITER); time.sleep(0.3); g.open_panel(WRITER); time.sleep(1.0); inv0 = g.uids(WRITER, "Invoke")

    def purge():
        junk = [u for u in g.uids(WRITER, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(WRITER, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True): g.delete_object(WRITER, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(WRITER)
    if not gate("A1 writer = copy of the reader, ExecState 1", g.exec_state(WRITER) == 1): return False
    props = g.report_all(WRITER, "Property"); nodes, _n = g.net_map(WRITER, 0, max_nodes=60, max_terms=24)
    pn_r = tmsc = None
    for _n_i, (u, _l, terms) in nodes.items():
        names = [t for _ti, t, _w in terms]
        if "Re-entrant" in names and u in {p["uid"] for p in props}: pn_r = u
        if "target class" in names and "specific class reference" in names: tmsc = u
    fact("read PN #%r  TMSC #%r" % (pn_r, tmsc))
    r = g.build_property(WRITER, "VI Server:CallLibrary", [("636D403", True)], (900, 450)); purge(); pw = int(r[-1]["uid"])
    n_w, rows = node_terms_of(WRITER, pw); fact("write PN #%d Nodes[%s] terminals %r" % (pw, n_w, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]))
    sink = [x for x in rows if not x["is_source"] and x["name"] not in ("reference", "error in (no error)")]
    if not gate("A2 write PN built with ONE write sink", pn_r and tmsc and n_w is not None and len(sink) == 1, [x["name"] for x in sink]): return False
    before = [l for _i, l, ind in g.fp_labels(WRITER) if not ind]
    _o, _lab = g.create_control(WRITER, n_w, sink[0]["i"]); purge()
    new = [l for _i, l, ind in g.fp_labels(WRITER) if not ind and l not in before]
    n_w, rows = node_terms_of(WRITER, pw); w_val = next(x["wire"] for x in rows if x["i"] == sink[0]["i"])
    if not gate("A3 boolean control created on the write sink", len(new) == 1 and w_val, (new, w_val)): return False
    g.wire(WRITER, "Function", idx(WRITER, "Function", tmsc), "specific class reference", "Property", idx(WRITER, "Property", pw), "reference", branch=True); purge()
    g.wire(WRITER, "Property", idx(WRITER, "Property", pw), "error out", "Property", idx(WRITER, "Property", pn_r), "error in (no error)"); purge()
    n_w, rows = node_terms_of(WRITER, pw); _nr, rrows = node_terms_of(WRITER, pn_r); es = g.exec_state(WRITER)
    w_ref = next(x["wire"] for x in rows if x["name"] == "reference"); w_ei = next(x["wire"] for x in rrows if x["name"] == "error in (no error)")
    w_eo = next(x["wire"] for x in rows if x["name"] == "error out")
    fact("after wiring: write PN ref wire %r, err out %r; read PN err in %r; ES %s" % (w_ref, w_eo, w_ei, es))
    if not gate("A4 TMSC -> write PN ref (branch), write err out -> read PN err in, ES 1", es == 1 and w_ref and w_ei and w_ei == w_eo): return False
    g.set_auto_error_handling(WRITER, False); purge(); es = g.exec_state(WRITER)
    if not gate("A5 ExecState 1 -> COM save", es == 1, es): return False
    g.save(WRITER); lab = dict(RLAB); lab["value_ctl"] = new[0]; lab["controls"] = [l for _i, l, ind in g.fp_labels(WRITER) if not ind]
    json.dump(lab, open(WLAB_P, "w"), indent=1); fact("writer labels %r" % lab)
    try: g.close_panel(WRITER)
    except Exception: pass
    return True


def run_op(op, lab, target, i, value=None):
    vi = g.op(op); vi.SetControlValue("vi path", target); vi.SetControlValue("vi path 2", target)
    vi.SetControlValue("Class Name", "CallLibrary"); vi.SetControlValue("index", int(i)); vi.SetControlValue("index 2", 0)
    if value is not None: vi.SetControlValue(lab["value_ctl"], bool(value))
    g._run(vi)
    row = {"index": i, "err": g._err(vi, lab["PNErr"]), "uid_echo": None, "AnyThread": None}
    try: row["uid_echo"] = int(vi.GetControlValue(lab["UID"]))
    except Exception as e: row["uid_echo"] = "ERR %r" % e                                       # noqa: BLE001
    try: v = vi.GetControlValue(lab["AnyThread"]); row["AnyThread"] = v if isinstance(v, bool) else str(v)
    except Exception as e: row["AnyThread"] = "ERR %r" % e                                     # noqa: BLE001
    print("ROW %s %s" % (os.path.basename(op), json.dumps(row, default=str)), flush=True); return row


def cdiff(target):
    import jev_candidates as JC, wiki_build as Wb
    G1 = JC.load(JC.S1_KEY); lv = Wb.read_live(target, fs_pairs=G1["wiki"]["fs_tunnel_pairs"])
    loops = json.load(open(JC._newest("graph_loops_s1_*.json"), encoding="utf-8"))["loops"]
    G2 = JC.from_parts({"terminals": lv["terminals"], "graph_summary": G1["wiki"]["graph_summary"]}, lv["objs"], loops, JC.node_labels_default(), lv["fs_tunnel_pairs"], "t0at")
    return V.computation_diff(G1, G2)


rows_b4 = rows_c = rows_f = []; counts = {}
try:
    gate("C0 t0 md5 == 25ea4f7d", md5(T0VI) == T0_MD5, md5(T0VI)); gate("C0b reader md5 == a7308101", md5(READER) == READER_MD5)
    shutil.copyfile(T0VI, COPY); time.sleep(0.3); gate("C1 %s is a byte copy of t0" % os.path.basename(COPY), md5(COPY) == T0_MD5)
    bench_prep.restart_labview(); g._lv = None
    ok = True
    if REBUILD or not (os.path.exists(WRITER) and os.path.exists(WLAB_P)):
        ok = build_writer()
        if ok: g.reset(); bench_prep.restart_labview(); g._lv = None; gate("A6 writer ExecState 1 COLD", g.exec_state(WRITER) == 1)
    if ok:
        WL = json.load(open(WLAB_P)); g.ensure_loaded(COPY); uids0 = [o["uid"] for o in g.report_all(COPY, "CallLibrary")]
        fact("copy CallLibrary uids %r" % uids0)
        r = run_op(WRITER, WL, COPY, 12, True); gate("B1 negative: index 12 -> error text, no exception", bool(r["err"]) and r["AnyThread"] is not True, r)
        r0 = run_op(WRITER, WL, COPY, 0, False); r1 = run_op(WRITER, WL, COPY, 0, True)
        gate("B2 toggle uid[0]: write False reads False, write True reads True", r0["AnyThread"] is False and r1["AnyThread"] is True and not r0["err"] and not r1["err"], (r0, r1))
        h0 = bench_prep.labview_handles()
        for k in range(20): run_op(WRITER, WL, COPY, k % 12, True)
        h1 = bench_prep.labview_handles(); gate("B3 20 write calls: handles flat |%d - %d| <= 100" % (h1, h0), abs(h1 - h0) <= 100)
        rows_b4 = [run_op(WRITER, WL, COPY, i, True) for i in range(12)]
        gate("B4 write True on all 12: in-op readback True 12/12, uid echo 12/12", len(rows_b4) == 12 and all(r["AnyThread"] is True and not r["err"] and r["uid_echo"] == uids0[r["index"]] for r in rows_b4))
        rows_c = [run_op(READER, RLAB, COPY, i) for i in range(12)]; uids_t0 = sorted(a["node"] for a in T0_CDIFF["added"] if a["class"] == "CallLibrary")
        gate("C1 SEPARATE reader: True 12/12, uid echo 12/12, uids == t0's 12", all(r["AnyThread"] is True and not r["err"] and r["uid_echo"] == uids0[r["index"]] for r in rows_c) and sorted(uids0) == uids_t0, (sorted(uids0), uids_t0))
        counts = {c: (len(g.report_all(T0VI, c)), len(g.report_all(COPY, c))) for c in CLASSES}; fact("counts t0 vs copy %r" % counts)
        gate("D1 per-class object counts copy == t0", all(a == b for a, b in counts.values()), counts)
        cd = cdiff(COPY); added = sorted(a["node"] for a in cd["computation_nodes_added"])
        for y in cd["rows"][:20]: fact("CDIFF ROW %r" % y)
        gate("D2 computation_diff(S1,copy): 0 rows, 0 removed, added == t0's 24", not cd["rows"] and not cd["computation_nodes_removed"] and added == T0_ADDED and len(added) == 24, (len(cd["rows"]), len(added)))
        es = g.exec_state(COPY); gate("E1 copy ExecState 1 warm", es == 1, es)
        if es == 1:
            g.save(COPY); m = md5(COPY); gate("E2 saved by script, md5 != t0's", m != T0_MD5, "%s %d B" % (m, os.path.getsize(COPY)))
        gate("E3 t0 md5 unchanged", md5(T0VI) == T0_MD5)
        g.reset(); bench_prep.restart_labview(); g._lv = None
        gate("F1 copy ExecState 1 COLD", g.exec_state(COPY) == 1)
        rows_f = [run_op(READER, RLAB, COPY, i) for i in range(12)]
        gate("F2 cold reader: True 12/12, uid echo 12/12", all(r["AnyThread"] is True and not r["err"] and r["uid_echo"] == uids0[r["index"]] for r in rows_f))
except Exception as e:                                                         # noqa: BLE001
    import traceback; traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])
gate("F3 t0 md5 unchanged / S1 unchanged", md5(T0VI) == T0_MD5 and md5(S1VI) == S1_MD5)
try: F["ref_counts"] = g.ref_counts()
except Exception: pass
try: g.reset()
except Exception: pass
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True); time.sleep(6)
gate("F4 LabVIEW gone at exit", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower())
arts = [{"path": os.path.relpath(OUT, ROOT), "md5": None}] + [{"path": p, "md5": md5(p)} for p in (COPY, WRITER) if os.path.exists(p)]
json.dump({"schema": "t0at-build/1", "card": "92-2 PD199(a)", "copy": COPY, "copy_md5": md5(COPY) if os.path.exists(COPY) else None, "t0": T0VI, "t0_md5": md5(T0VI),
           "writer": WRITER, "writer_md5": md5(WRITER) if os.path.exists(WRITER) else None, "counts": counts, "rows_write": rows_b4, "rows_read": rows_c, "rows_cold": rows_f,
           "gates": G, "facts": F}, open(OUT, "w"), indent=1, default=str)
arts[0]["md5"] = md5(OUT); bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
sys.exit(1 if bad else 0)
