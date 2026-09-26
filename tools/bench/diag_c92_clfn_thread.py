r"""diag_c92_clfn_thread.py - card 92-1 M1 (PD198(c)(1)): READ the thread setting of the 12 CLFN stamps in
claudeDev\D1_s1_t0_20260926_055551.vi (md5 25ea4f7d...) from LabVIEW - CallLibrary property `Any Thread?` 636D403 (raw
boolean), plus `Library Path` 636D400 and `Calling Convention` 636D402 (docs/vi-server-ids.json:83-94) - by uid, read-only.
FOUND FIRST: no reader for a CallLibrary property exists (grep 636D403 in tools/gscript.py: none; OpCLFNBuild/Pre/Params
only SET through NI's import-wizard globals, tools/recipes/build_opclfn.py:67-72 - the `Reentrant` set is 636D403's
writer, so the VALUE is what build_clfn's `reentrant=True` default wrote, but the card asks for the read). So phase A builds
the reader op OpCLFNThread_v0.vi by the proven typed-control-seed route of tools/recipes/build_oploopcast_v0.py
(docs/toolkit-capabilities.md 'SOLVED 2026-09-14 ... the typed-control seed'): donor OpSetIndexMode_v0.vi
(Traverse(Class Name, index) -> Index Array -> TMSC -> IndexMode WRITE PN), the write PN deleted, a CallLibrary-class
property node built (build_property), `Terminal.Create Control` on its `reference` input = the CallLibrary-typed SEED,
that seed wired to the TMSC 'target class', TMSC out -> the property node, indicators + a GObject.UID echo. Phase B runs it
on the t0 copy for index 0..11 (Traverse order == report_all order) and writes tools/bench/t0_clfn_thread_92.json.
Rules: the t0 copy is never saved, never edited (only Open VI Reference + property READS); no scratch of it is made.
PREDICTION CONTRACT (GATE lines): B1 donor copy ES 1  B2 write PN deleted, ES 1  B3 TMSC found with a wired target class
 B4 CallLibrary property node built (3 read items)  B5 seed control created on its `reference`  B6 seed -> target class
 and TMSC out -> reference: ES 1  B7 indicators: 3 data + error out + UID  B8 ES 1 -> COM save  B9 cold ES 1
 R1 report_all(t0,'CallLibrary') == 12 uids == the step-3c table  R2 uid echo == report_all uid for all 12
 R3 12 rows with a boolean `Any Thread?` and no error text  R4 t0 md5 unchanged  R5 LabVIEW gone at exit
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c92_clfn_thread.log -- py -u tools/bench/diag_c92_clfn_thread.py [--rebuild]
"""
import hashlib, json, os, shutil, subprocess, sys, time
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools")); sys.path.insert(0, HERE)
import protocol as P                                                            # noqa: E402
import gscript as g                                                             # noqa: E402
CD = g.CLAUDEDEV
T0VI = os.path.join(CD, "D1_s1_t0_20260926_055551.vi"); T0_MD5 = "25ea4f7d10d91c41c4b5de64f850c945"
DONOR = os.path.join(CD, "OpSetIndexMode_v0.vi"); OP = os.path.join(CD, "OpCLFNThread_v0.vi")
LAB = os.path.join(HERE, "opclfnthread_labels.json"); OUT = os.path.join(HERE, "t0_clfn_thread_92.json")
SITES = json.load(open(os.path.join(HERE, "t0_sites_s1_step3c_r2.json")))
EXPECT_UIDS = sorted(int(p["reported_not_deleted"][0]["uid"]) for p in SITES["purges"] if p["tag"].endswith("after build") and p["reported_not_deleted"])
PROPS = [("636D403", "AnyThread"), ("636D400", "LibraryPath"), ("636D402", "CallingConvention")]
REBUILD = "--rebuild" in sys.argv
g._run.__defaults__ = (6.0, 120.0)
G, F = {}, {"steps": []}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, detail=""):
    G[k] = bool(ok); print("GATE %-60s %s  %s" % (k, "PASS" if ok else "FAIL", str(detail)[:300]), flush=True); return bool(ok)


def fact(s): print("  " + s, flush=True); F["steps"].append(s)


def idx(cls, uid): return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def inds(): return [lab for _i, lab, is_ind in g.fp_labels(OP) if is_ind and lab]


def node_terms_of(uid, diagram=0):
    for cand in range(60):
        nu, rows = g.node_terms_uid(OP, diagram, cand)
        if not nu: return None, None
        if nu == uid: return cand, rows
    return None, None


def make_indicator(uid, term_name):
    n, rows = node_terms_of(uid); t = next(r["i"] for r in rows if r["name"] == term_name)
    before = set(inds()); g.create_indicator(OP, n, t); new = [l for l in inds() if l not in before]
    assert len(new) == 1, "indicator on %r: %r" % (term_name, new); return new[0]


def build():
    inv0 = [0]

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0[0]]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True): g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)
    if os.path.exists(OP): os.remove(OP)
    shutil.copyfile(DONOR, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0); inv0[0] = g.uids(OP, "Invoke")
    fact("donor controls %r" % [l for _i, l, ind in g.fp_labels(OP) if not ind])
    if not gate("B1 donor copy ExecState 1", g.exec_state(OP) == 1): return False
    props = g.report_all(OP, "Property"); fact("donor Property nodes %r" % [p["uid"] for p in props])
    nodes, _nets = g.net_map(OP, 0, max_nodes=60, max_terms=24)
    pn_w = next((u for _n, (u, _l, terms) in nodes.items() if any(t == "IndexMode" for _ti, t, _w in terms) and u in {p["uid"] for p in props}), None)
    if pn_w is None: return gate("B2 IndexMode write PN found + deleted, ES 1", False, "not found")
    g.delete_object(OP, "Property", idx("Property", pn_w)); g.remove_bad_wires_scripted(OP); purge()
    if not gate("B2 IndexMode write PN found + deleted, ES 1", g.exec_state(OP) == 1, pn_w): return False
    nodes, _nets = g.net_map(OP, 0, max_nodes=60, max_terms=24)
    tmsc = next(((u, terms) for _n, (u, _l, terms) in nodes.items() if any(t == "target class" for _ti, t, _w in terms)
                 and any(t == "specific class reference" for _ti, t, _w in terms)), None)
    if not tmsc: return gate("B3 TMSC found with a wired target class", False, "no TMSC")
    tmsc_uid, W = tmsc[0], next(w for _ti, t, w in tmsc[1] if t == "target class")
    if not gate("B3 TMSC found with a wired target class", bool(W), (tmsc_uid, W)): return False
    r = g.build_property(OP, "VI Server:CallLibrary", [(pid, False) for pid, _n in PROPS], (900, 650)); purge()
    pu = int(r[-1]["uid"]); n_p, rows = node_terms_of(pu)
    fact("CallLibrary PN #%d Nodes[%s] terminals %r" % (pu, n_p, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]))
    if not gate("B4 CallLibrary property node built (3 read items)", n_p is not None and len(rows) >= 5): return False
    t_ref = next(x for x in rows if x["name"] == "reference" and not x["is_source"])
    _objs, seed = g.create_control(OP, n_p, t_ref["i"]); purge()
    n_p, rows = node_terms_of(pu); w_seed = next(x["wire"] for x in rows if x["i"] == t_ref["i"])
    if not gate("B5 seed control created on `reference` (CallLibrary-typed)", bool(seed) and bool(w_seed), (seed, w_seed)): return False
    wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", wires.index(w_seed)); wires = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", wires.index(W))
    g.wire_control(OP, [seed], "Function", idx("Function", tmsc_uid), ["target class"]); purge()
    g.wire(OP, "Function", idx("Function", tmsc_uid), "specific class reference", "Property", idx("Property", pu), "reference"); purge()
    n_p, rows = node_terms_of(pu); es = g.exec_state(OP)
    fact("after wiring: PN terminals %r ES %s" % ([(x["i"], x["name"], x["wire"]) for x in rows], es))
    if not gate("B6 seed -> target class, TMSC out -> reference: ES 1", es == 1 and next(x["wire"] for x in rows if x["i"] == t_ref["i"]), es): return False
    r = g.build_property(OP, "VI Server:GObject", [("632A813", False)], (900, 850)); purge(); uu = int(r[-1]["uid"])
    g.wire(OP, "Function", idx("Function", tmsc_uid), "specific class reference", "Property", idx("Property", uu), "reference", branch=True); purge()
    lab = {"seed": seed}
    data = [x["name"] for x in rows if x["is_source"] and x["name"] not in ("reference out", "error out")]
    fact("PN data outputs %r" % data)
    for name, key in zip(data, [k for _p, k in PROPS]): lab[key] = make_indicator(pu, name)
    lab["PNErr"] = make_indicator(pu, "error out"); lab["UID"] = make_indicator(uu, "UID"); lab["UIDErr"] = make_indicator(uu, "error out")
    if not gate("B7 indicators: 3 data + error out + UID + UID err", len(data) == 3 and all(lab.values()), lab): return False
    g.set_auto_error_handling(OP, False); purge(); es = g.exec_state(OP)
    if not gate("B8 ExecState 1 -> COM save", es == 1, es): return False
    g.save(OP); lab["controls"] = [l for _i, l, ind in g.fp_labels(OP) if not ind]
    json.dump(lab, open(LAB, "w"), indent=1); fact("labels %r" % lab)
    try: g.close_panel(OP)
    except Exception: pass
    return True


def read():
    lab = json.load(open(LAB)); ctl = set(lab.get("controls") or [])
    objs = g.report_all(T0VI, "CallLibrary"); uids = [o["uid"] for o in objs]
    gate("R1 report_all(t0, CallLibrary) == 12 == step-3c uids", len(uids) == 12 and sorted(uids) == EXPECT_UIDS, (uids, EXPECT_UIDS))
    rows = []
    for i, u in enumerate(uids):
        vi = g.op(OP); vi.SetControlValue("vi path", T0VI)
        if "vi path 2" in ctl: vi.SetControlValue("vi path 2", T0VI)
        vi.SetControlValue("Class Name", "CallLibrary"); vi.SetControlValue("index", i)
        if "index 2" in ctl: vi.SetControlValue("index 2", 0)
        g._run(vi)
        row = {"index": i, "uid_report_all": u, "uid_echo": None, "err": g._err(vi, lab["PNErr"]), "uid_err": g._err(vi, lab["UIDErr"])}
        try: row["uid_echo"] = int(vi.GetControlValue(lab["UID"]))
        except Exception as e: row["uid_echo"] = "ERR %r" % e                                   # noqa: BLE001
        for _p, k in PROPS:
            try: v = vi.GetControlValue(lab[k]); row[k] = (v if isinstance(v, (bool, int, float, str)) else str(v))
            except Exception as e: row[k] = "ERR %r" % e                                       # noqa: BLE001
        row["property_ids"] = {k: p for p, k in PROPS}; rows.append(row); print("ROW " + json.dumps(row, default=str), flush=True)
    gate("R2 uid echo == report_all uid for all 12", all(r["uid_echo"] == r["uid_report_all"] for r in rows) and len(rows) == 12)
    gate("R3 12 rows with a boolean AnyThread and no error text", len(rows) == 12 and all(isinstance(r["AnyThread"], bool) and not r["err"] for r in rows),
         [(r["uid_report_all"], r["AnyThread"], (r["err"] or "")[:60]) for r in rows])   # run 1: _err returned None -> TypeError in this detail string
    return rows


ok_build = True
try:
    import bench_prep; bench_prep.restart_labview(); g._lv = None
    if REBUILD or not (os.path.exists(OP) and os.path.exists(LAB)):
        ok_build = build()
        if ok_build:
            g.reset(); bench_prep.restart_labview(); g._lv = None
            gate("B9 ExecState 1 COLD in a fresh LabVIEW", g.exec_state(OP) == 1)
    rows = read() if ok_build else []
except Exception as e:                                                         # noqa: BLE001
    import traceback; traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200]); rows = []
gate("R4 t0 md5 unchanged", md5(T0VI) == T0_MD5, md5(T0VI))
try: F["ref_counts"] = g.ref_counts()
except Exception: pass
try: g.reset()
except Exception: pass
subprocess.run(["powershell", "-NoProfile", "-Command", "Stop-Process -Name LabVIEW -Force -ErrorAction SilentlyContinue"], capture_output=True); time.sleep(6)
gate("R5 LabVIEW gone at exit", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, errors="replace").stdout.lower())
json.dump({"schema": "t0-clfn-thread/1", "card": "92-1 PD198(c)(1)", "vi": T0VI, "vi_md5": T0_MD5, "reader_op": OP, "reader_md5": md5(OP) if os.path.exists(OP) else None,
           "property_ids": {k: p for p, k in PROPS}, "rows": rows, "gates": G, "facts": F, "build_clfn_default": "reentrant=True (tools/gscript.py:2968)"},
          open(OUT, "w"), indent=1, default=str)
bad = [k for k, v in G.items() if not v]
print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
sys.exit(1 if bad else 0)
