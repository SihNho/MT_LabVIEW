r"""build_opconnecttermuid_v0 - card 124-1 STEP 1 (PD249(f)): claudeDev\OpConnectTermUid_v0.vi = `Terminal.Connect Wire` 6349C03
between TWO terminals each addressed WITHOUT a node: SINK = Traverse(`Class Name`='Terminal')[`index`] -> TMSC (VI Server:Terminal
seed) [+ GObject.UID echo]; SOURCE = `UID to GObject Reference.vi` (Owning VI = the target's Open VI Reference, `UID`) -> a second
TMSC (same seed) [+ UID echo] -> `Wire Source`. Readback ordered after the Invoke: Terminal[Connected Wire] -> Wire[UID, Broken?];
Close Reference on the Wire ref and on the UID-resolved GObject.
FOUND FIRST: case Terminals[] lists OUTER faces only (diag_c123_casetun.log:69); tunnels are not in Nodes[] (peer
archive/peer/2026-10-01-c124-1-casetun-innerface-hyp.md §3; fact -gemini §2); inner faces per frame are read by OpAllTerms_v1's
frame_diagram (docs/toolkit-capabilities.md:339-347); every existing writer needs a NODE index triple on at least one end
(OpConnectNested_v1, OpConnectFromWire_v0, OpFsInnerTunnelConnect_v0/v1; toolkit-capabilities.md:73-76). The build pattern is
diag_c100_verbs_build.py (B / retarget / uid_echo / drop_subvi U2G, OpPrimCopyNested_v0 run 4 PASS) on an OpSetIndexMode_v0 copy;
Close Reference donor KernelBuilder_v1 #157 (diag_c122_opbuild.py); the hygiene criterion of op_hygiene/OpConstInd_v0.json.
PREDICTION: D donor ES1 / S Terminal seed ES1 / U U2G dropped / T2 second TMSC copied (1 node) / A assembled ES 1 + saved /
C COLD ES 1 / F1 first call on a scratch copy of OpPrimDonor_v0.vi: an already-connected (sink, source) pair -> echoes == uids,
UID 2 == that wire, Broken? False, wire count +0 / H 2,000 calls 0 errors, handles flat +-100 / LabVIEW gone.
An op build lives in tools/bench like its precedents (diag_c100_verbs_build.py, diag_c122_opbuild.py, diag_c118_r1_opbuild.py).
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c124_opconnecttermuid.log -- py -u tools/bench/diag_c124_opconnecttermuid.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import diag_c100_verbs_build as V                                                          # noqa: E402
g, P, bench_prep, gate, fact, md5 = V.g, V.P, V.bench_prep, V.gate, V.fact, V.md5             # noqa: E702
CD, KEY = g.CLAUDEDEV, "OpConnectTermUid_v0"
OP, KB = os.path.join(CD, KEY + ".vi"), os.path.join(CD, "KernelBuilder_v1.vi")
LAB_P = os.path.join(ROOT, "tools", "bench", "opconnecttermuid_v0_labels.json")
HYG_P = os.path.join(ROOT, "tools", "bench", "op_hygiene", KEY + ".json")
SCR = os.path.join(CD, "scratch_c124_hyg_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
N_CALLS = 2000
g._run.__defaults__ = (6.0, 120.0)


def build():
    b = V.B("OpSetIndexMode_v0.vi", KEY + ".vi")
    if not gate("D donor OpSetIndexMode_v0 copy ES 1", g.exec_state(b.op) == 1):
        return None
    tm, pe1 = V.retarget(b, KEY, "VI Server:Terminal", [("632A813", False)], (900, 450))   # sink TMSC + its UID echo
    if not tm:
        return None
    top = int(g.report_all(b.op, "Diagram")[0]["uid"])
    seed = next(r for r in b.terms(tm)[1] if r["name"] == "target class")
    lab = {"tmsc1": tm, "echo1": pe1, "top": top}
    ovr = next(f for f in sorted(g.uids(b.op, "Function")) if any(r["name"] == "vi path" and not r["is_source"] and r["wire"]
               and r["wire"] == next(x["wire"] for x in g.panel_wiring(b.op) if x["label"] == "vi path") for r in b.terms(f)[1]))
    s0 = set(g.uids(b.op, "SubVI")); g.drop_subvi(b.op, V.U2G, 0, (900, 800)); b.purge()      # noqa: E702
    new = sorted(set(g.uids(b.op, "SubVI")) - s0)
    if not gate("U `UID to GObject Reference.vi` dropped", len(new) == 1, new):
        return None
    u2g = new[0]
    fact("U2G terminals", [(r["i"], r["name"], r["is_source"]) for r in b.terms(u2g)[1]])
    tm2 = g.create_primitive_nested(b.op, top, "TMSC", (1100, 800), donor={"donor": b.op, "uid": tm})
    gate("T2 second TMSC copied from #%s -> #%s" % (tm, tm2), bool(tm2))
    b.w(ovr, "vi reference", u2g, "Owning VI", sc="Function", dc="SubVI", branch=True)
    lab["src_uid"] = b.ctl(u2g, "UID")
    b.w(u2g, "GObject", tm2, "reference", sc="SubVI", dc="Function")
    seed_ctl = [r["label"] for r in g.panel_wiring(b.op) if not r["indicator"] and r["wire"] == seed["wire"]]
    g.wire_control(b.op, seed_ctl[:1], "Function", b.idx("Function", tm2), ["target class"], branch=True); b.purge()  # noqa: E702
    pe2 = V.uid_echo(b, tm2, (1300, 800))
    inv = int(g.build_invoke(b.op, "VI Server:Terminal", "6349C03", (1500, 450))[-1]["uid"]); b.inv0.add(inv); b.purge()  # noqa: E702
    fact("Invoke terminals", [(r["i"], r["name"], r["is_source"], r["wire"]) for r in b.terms(inv)[1]])
    b.w(tm, "specific class reference", inv, "reference", sc="Function", dc="Invoke", branch=True)
    b.w(tm2, "specific class reference", inv, "Wire Source", sc="Function", dc="Invoke", branch=True)
    # error chain = execution order: TMSC1 -> echo1 -> U2G -> TMSC2 -> echo2 -> Invoke -> CW -> Wire PN -> CR wire -> CR gobj
    b.w(tm, "error out", pe1, "error in (no error)", sc="Function", branch=b.wired(tm, "error out", True))
    u2g_ein = next((r["name"] for r in b.terms(u2g)[1] if not r["is_source"] and r["name"].startswith("error in")), None)
    if u2g_ein:
        b.w(pe1, "error out", u2g, u2g_ein, dc="SubVI")
    b.w(u2g, "error out", tm2, "error in", sc="SubVI", dc="Function")
    b.w(tm2, "error out", pe2, "error in (no error)", sc="Function")
    b.w(pe2, "error out", inv, "error in (no error)", dc="Invoke")
    cw = b.pn("VI Server:Terminal", [("634A000", False)], (1700, 450))
    b.w(inv, "reference out", cw, "reference", sc="Invoke"); b.w(inv, "error out", cw, "error in (no error)", sc="Invoke")  # noqa: E702
    pw = b.pn("VI Server:Wire", [("632A813", False), ("6371004", False)], (1900, 450))
    b.w(cw, b.data(cw, True)[0], pw, "reference"); b.w(cw, "error out", pw, "error in (no error)")  # noqa: E702
    crs = []
    for k in range(2):
        crs.append(g.create_primitive_nested(b.op, top, "Close Reference", (2100, 450 + 250 * k), donor={"donor": KB, "uid": 157}))
    gate("C two Close Reference copies %r" % crs, len(crs) == 2 and all(crs))
    b.w(pw, "reference out", crs[0], "reference", dc="Node"); b.w(pw, "error out", crs[0], "error in (no error)", dc="Node")  # noqa: E702
    b.w(u2g, "GObject", crs[1], "reference", sc="SubVI", dc="Node", branch=True)
    b.w(crs[0], "error out", crs[1], "error in (no error)", sc="Node", dc="Node")
    outs = b.data(pw, True)
    lab.update(u2g=u2g, tmsc2=tm2, echo2=pe2, inv=inv, cw=cw, pw=pw, crs=crs, data_out=outs)
    lab["sink_echo"], lab["src_echo"] = b.ind(pe1, "UID"), b.ind(pe2, "UID")
    lab["wire_uid"], lab["broken"] = b.ind(pw, outs[0]), b.ind(pw, outs[1])
    lab["Err"] = b.ind(crs[1], "error out")
    lab.update(vi_path="vi path", class_name="Class Name", index="index", method="6349C03", donor="OpSetIndexMode_v0.vi")
    b.finish(KEY, lab)
    return lab if KEY in V.LAB else None


def call(lab, target, ti, src_uid):
    vi = g.op(OP)
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "Terminal")   # noqa: E702
    vi.SetControlValue("index", int(ti)); vi.SetControlValue(lab["src_uid"], int(src_uid))  # noqa: E702
    g._run(vi)
    return dict((k, vi.GetControlValue(lab[k])) for k in ("sink_echo", "src_echo", "wire_uid", "broken")), g._err(vi, lab["Err"]) or ""


def hygiene(lab):
    shutil.copyfile(os.path.join(CD, "OpPrimDonor_v0.vi"), SCR); time.sleep(0.3)           # noqa: E702
    import allterms
    rows, _dt = allterms.read_terms(SCR, allterms.OP_ALLTERMS_V1)
    by = {}
    for r in rows:
        by.setdefault(r["wire_uid"], []).append(r) if r["wire_uid"] else None
    w, pair = next((w, p) for w, p in sorted(by.items()) if len(p) == 2 and sum(x["is_source"] for x in p) == 1)
    snk, src = next(x for x in pair if not x["is_source"]), next(x for x in pair if x["is_source"])
    ti = g._uid_index(SCR, "Terminal", snk["term_uid"])
    wc0 = len(g.uids(SCR, "Wire"))
    r1, e1 = call(lab, SCR, ti, src["term_uid"])
    fact("F1 pair w%s sink #%s (Traverse %s) <- source #%s" % (w, snk["term_uid"], ti, src["term_uid"]), (r1, e1))
    if not gate("F1 first call: echoes, UID 2 == w%s, Broken? False, wires +0" % w, not e1 and int(r1["sink_echo"]) == snk["term_uid"]
                and int(r1["src_echo"]) == src["term_uid"] and int(r1["wire_uid"]) == w and r1["broken"] is False
                and len(g.uids(SCR, "Wire")) == wc0, (r1, e1, len(g.uids(SCR, "Wire")), wc0)):
        return
    h0, hs, errs, codes = bench_prep.labview_handles(), [], 0, []
    for k in range(N_CALLS):
        _r, e = call(lab, SCR, ti, src["term_uid"])
        if e:
            errs += 1; codes.append(str(e)[:80])                                             # noqa: E702
        if k % 100 == 99:
            hs.append(bench_prep.labview_handles())
    h1 = bench_prep.labview_handles()
    ok = errs == 0 and abs(h1 - h0) <= 100 and len(g.uids(SCR, "Wire")) == wc0
    gate("H %d calls, 0 errors, handles flat +-100, wires +0" % N_CALLS, ok, (errs, h0, h1, len(g.uids(SCR, "Wire")), wc0))
    json.dump({"schema": "op-hygiene/1", "op": KEY, "path": OP, "md5": md5(OP), "status": "PASS" if ok else "FAIL", "calls": N_CALLS,
               "errors": errs, "error_codes": sorted(set(codes)), "handles_before": h0, "handles_after": h1, "handles_per_round": hs,
               "workload": "1 first call + %d idempotent re-connects of w%s (sink #%s <- source #%s) on a never-saved byte copy of "
                           "OpPrimDonor_v0.vi" % (N_CALLS, w, snk["term_uid"], src["term_uid"]),
               "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1) + PD242(b): >= 2,000 consecutive calls, 0 errors, handles flat +-100",
               "log": "tools/bench/diag_c124_opconnecttermuid.log", "build_log": "tools/bench/diag_c124_opconnecttermuid.log"},
              open(HYG_P, "w", encoding="utf-8"), indent=1)


try:
    os.path.exists(OP) and os.remove(OP)
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                  # noqa: E702
    lab = build()
    if lab:
        json.dump({KEY: lab}, open(LAB_P, "w", encoding="utf-8"), indent=1); fact("labels", lab)  # noqa: E702
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                   # noqa: E702
        if gate("C COLD ExecState 1 (fresh LabVIEW)", g.exec_state(OP) == 1, md5(OP)):
            hygiene(lab)
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    V.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in V.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    os.path.exists(SCR) and os.remove(SCR)
    gate("X scratch deleted", not os.path.exists(SCR), SCR)
    bad = [k for k, v in V.G.items() if not v]
    if bad and os.path.exists(OP) and KEY not in V.LAB:
        os.remove(OP)
    arts = [{"path": p, "md5": md5(p)} for p in (OP, LAB_P, HYG_P) if os.path.exists(p) and not bad]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(V.G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(V.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
