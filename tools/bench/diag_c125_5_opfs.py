r"""diag_c125_5_opfs - card 125-5 STEP 1 (brief_125-5.md, PD252(e) route (a)): TWO new op VIs + their hygiene records + a 1-frame FS donor.
  OpFsDiagrams_v0 (frame-ORDER reader): Traverse('FlatSequence')[index] -> TMSC(FlatSequence seed) -> PN [UID 632A813, Diagrams[] 3578BC00]
    -> Index Array[k] -> GObject.UID -> indicator; Close Reference on the Diagrams[] ARRAY (as OpWireJoints_v1 closes its References array).
  OpFsAddFrame_v0: same head -> PN [UID] (echo) -> Invoke FlatSequence.Add Frame 3578B800 (`Reference Frame Index`, `After(T)`) -> its
    return ref (the new FlatSequenceFrame) -> Close Reference.
  ADDRESSING: the FS is addressed by Traverse('FlatSequence') index + UID echo (the wrapper resolves uid -> index and refuses a wrong echo),
  the proven head of every OpSetIndexMode_v0-donor op (diag_c124_opconnecttermuid.py:33-39 retarget), not UID to GObject Reference.
EXISTING FIRST: no FS creator / frame-add op / Diagrams[] reader (diag_c123_struct.log:47, result_125-4.json); Add Frame id measured
(diag_c125_4fsm.log:23, gscript.FS_METHODS); a SMALL VI with ONE 1-frame FS found read-only: NI example `VI Scripting with Structures -
For Loop.vi` (claudeDev copy) FS #1309, 54 GObjects (diag_c125_5_fsfind.log:5). Build pattern + hygiene = diag_c124_opconnecttermuid.py /
diag_c124_opctu_hyg.py (calls only inside gscript.hygiene_probe). Close Reference donor KernelBuilder_v1 #157.
PREDICTION: both ops ES 1, saved, COLD ES 1 / R1 reader on a scratch copy: echo 1309, k0 = the FS frame Diagram uid, err '' /
RH 2,000 reader calls 0 errors, handles +-100 / A1 first Add Frame (0, After T): echo 1309, err '', FS frames 1 -> 2, reader k0 unchanged,
k1 = the new frame Diagram / AH 20 rounds x 100 Add Frame on fresh scratch copies: 0 errors, every round 101 frames, handles +-100 /
D DonorFs_v0.vi = a byte copy of the example with every object of the FS frame deleted: frame terminals 0, ES 1, saved / LabVIEW gone.
    py tools/bgrun.py --material --max-min 45 --log tools/bench/diag_c125_5_opfs.log -- py -u tools/bench/diag_c125_5_opfs.py"""
import json, os, shutil, sys, time, traceback                                              # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import diag_c100_verbs_build as V                                                          # noqa: E402
import allterms                                                                            # noqa: E402
g, P, bench_prep, gate, fact, md5 = V.g, V.P, V.bench_prep, V.gate, V.fact, V.md5             # noqa: E702
CD, KR, KA = g.CLAUDEDEV, "OpFsDiagrams_v0", "OpFsAddFrame_v0"
OPR, OPA, KB = os.path.join(CD, KR + ".vi"), os.path.join(CD, KA + ".vi"), os.path.join(CD, "KernelBuilder_v1.vi")
EX, FS = os.path.join(CD, "NIScriptingExamples", "Structures", "VI Scripting with Structures - For Loop.vi"), 1309
DON, LAB_P = os.path.join(CD, "DonorFs_v0.vi"), os.path.join(HERE, "opfs_v0_labels.json")
TS, SCRS = time.strftime("%Y%m%d_%H%M%S"), []
g._run.__defaults__ = (6.0, 120.0)


def scr(tag):
    p = os.path.join(CD, "scratch_c125_5_%s_%s.vi" % (tag, TS)); shutil.copyfile(EX, p); SCRS.append(p); time.sleep(0.2); return p  # noqa: E702


def head(key, props):
    b = V.B("OpSetIndexMode_v0.vi", key + ".vi")
    if not gate("%s D donor OpSetIndexMode_v0 copy ES 1" % key, g.exec_state(b.op) == 1):
        return None, None, None
    tm, p = V.retarget(b, key, "VI Server:FlatSequence", props, (900, 450))
    if tm:
        b.w(tm, "error out", p, "error in (no error)", sc="Function", branch=b.wired(tm, "error out", True))
    return b, tm, p


def cr_copy(b, pos):
    return g.create_primitive_nested(b.op, int(g.report_all(b.op, "Diagram")[0]["uid"]), "Close Reference", pos, donor={"donor": KB, "uid": 157})


def build_reader():
    b, tm, p = head(KR, [("632A813", False), ("3578BC00", False)])
    if not tm:
        return None
    outs = b.data(p, True); fact("%s PN outputs" % KR, outs)                                 # noqa: E702
    ia = int(g.build_index_array(b.op, (1100, 450))[-1]["uid"]); b.purge()                 # noqa: E702
    b.w(p, outs[1], ia, "array", dc="IndexArray")
    pu = b.pn("VI Server:GObject", [("632A813", False)], (1300, 450))
    b.w(ia, "element", pu, "reference", sc="IndexArray")
    b.w(p, "error out", pu, "error in (no error)")
    cr = cr_copy(b, (1500, 450))
    b.w(p, outs[1], cr, "reference", dc="Node", branch=True)
    b.w(pu, "error out", cr, "error in (no error)", dc="Node")
    lab = {"k": b.ctl(ia, "index"), "fs_echo": b.ind(p, outs[0]), "diag_uid": b.ind(pu, "UID"), "Err": b.ind(cr, "error out"),
           "uids": {"tmsc": tm, "pn": p, "ia": ia, "pu": pu, "cr": cr}}
    b.finish(KR, lab)
    return KR in V.LAB


def build_adder():
    b, tm, p = head(KA, [("632A813", False)])
    if not tm:
        return None
    inv = int(g.build_invoke(b.op, "VI Server:FlatSequence", g.FS_METHODS["Add Frame"], (1100, 450))[-1]["uid"]); b.inv0.add(inv); b.purge()  # noqa: E702
    ni, rows = b.terms(inv); fact("%s Invoke census" % KA, [(r["i"], r["name"], r["is_source"]) for r in rows])  # noqa: E702
    b.w(tm, "specific class reference", inv, "reference", sc="Function", dc="Invoke", branch=True)
    b.w(p, "error out", inv, "error in (no error)", dc="Invoke")
    lab = {"rfi": b.ctl(inv, "Reference Frame Index"), "after": b.ctl(inv, "After(T)")}
    cr = cr_copy(b, (1400, 450))
    nc, crow = b.terms(cr); ni, rows = b.terms(inv)                                        # noqa: E702
    t_ref = next(r["i"] for r in crow if r["name"] == "reference" and not r["is_source"])
    t_out = next(r["i"] for r in rows if r["name"] == "Add Frame" and r["is_source"])
    fact("%s Add Frame return -> Close Reference" % KA, g.connect_terminals(b.op, nc, t_ref, ni, t_out)); b.purge()  # noqa: E702
    b.w(inv, "error out", cr, "error in (no error)", sc="Invoke", dc="Node")
    lab.update(fs_echo=b.ind(p, "UID"), Err=b.ind(cr, "error out"), uids={"tmsc": tm, "pn": p, "inv": inv, "cr": cr})
    b.finish(KA, lab)
    return KA in V.LAB


def rd(t, ti, k):
    vi = g.op(OPR); g._set_common(vi, t, V.LAB[KR], "FlatSequence", ti); vi.SetControlValue(V.LAB[KR]["k"], int(k)); g._run(vi)  # noqa: E702
    return int(vi.GetControlValue(V.LAB[KR]["fs_echo"]) or 0), int(vi.GetControlValue(V.LAB[KR]["diag_uid"]) or 0), g._err(vi, V.LAB[KR]["Err"]) or ""


def add(t, ti, rfi, after):
    vi = g.op(OPA); L = V.LAB[KA]; g._set_common(vi, t, L, "FlatSequence", ti)            # noqa: E702
    vi.SetControlValue(L["rfi"], int(rfi)); vi.SetControlValue(L["after"], bool(after)); g._run(vi)  # noqa: E702
    return int(vi.GetControlValue(L["fs_echo"]) or 0), g._err(vi, L["Err"]) or ""


def frames(t):
    return [o["uid"] for o in g.report_all(t, "Diagram") if o["owner"] == "FlatSequenceFrame"]


def record(key, op_path, ok, calls, errs, h0, h1, hs, work):
    json.dump({"schema": "op-hygiene/1", "op": key, "path": op_path, "md5": md5(op_path), "status": "PASS" if ok else "FAIL", "calls": calls,
               "errors": errs, "handles_before": h0, "handles_after": h1, "handles_per_round": hs, "workload": work, "card": "125-5",
               "criterion": "docs/violation-decisions.md 2026-09-28 10:37 (1) + PD242(b): >= 2,000 consecutive calls, 0 errors, handles flat +-100",
               "log": "tools/bench/diag_c125_5_opfs.log"}, open(os.path.join(HERE, "op_hygiene", key + ".json"), "w", encoding="utf-8"), indent=1)


def hyg_reader():
    t = scr("r"); g.ensure_loaded(t); ti = g._uid_index(t, "FlatSequence", FS); fr = frames(t)  # noqa: E702
    r0, r1 = rd(t, ti, 0), rd(t, ti, 1)
    fact("R1 reader k0 / k1 on #%s (frames by report_all %s)" % (FS, fr), (r0, r1))
    if not gate("R1 echo %s, k0 == the frame Diagram %s, err ''" % (FS, fr), r0 == (FS, fr[0], "") and len(fr) == 1, (r0, fr)):
        return False
    h0, hs, errs = bench_prep.labview_handles(), [], 0
    for k in range(2000):
        errs += int(rd(t, ti, 0) != r0)
        if k % 100 == 99:
            hs.append(bench_prep.labview_handles())
    h1 = bench_prep.labview_handles(); ok = errs == 0 and abs(h1 - h0) <= 100              # noqa: E702
    gate("RH 2000 reader calls: 0 errors/mismatches, handles flat +-100", ok, (errs, h0, h1, hs))
    record(KR, OPR, ok, 2001, errs, h0, h1, hs, "1 warm + 2000 reads (k=0) of FS #%s on a never-saved byte copy of %s" % (FS, os.path.basename(EX)))
    return ok


def hyg_adder():
    t = scr("a0"); g.ensure_loaded(t); ti = g._uid_index(t, "FlatSequence", FS); f0 = frames(t)  # noqa: E702
    a = add(t, ti, 0, True); f1 = frames(t); k0, k1 = rd(t, ti, 0), rd(t, ti, 1)           # noqa: E702
    fact("A1 first Add Frame(0, T)", (a, f0, f1, k0, k1))
    if not gate("A1 echo %s, err '', frames 1 -> 2, k0 == old frame, k1 == the new frame" % FS, a == (FS, "") and len(f0) == 1 and len(f1) == 2
                and k0[1] == f0[0] and k1[1] in f1 and k1[1] != f0[0] and not k1[2], (a, f0, f1, k0, k1)):
        return False
    h0, hs, errs, bad = bench_prep.labview_handles(), [], 0, []
    for rnd in range(20):
        t = scr("a%02d" % (rnd + 1)); g.ensure_loaded(t); ti = g._uid_index(t, "FlatSequence", FS)  # noqa: E702
        for _k in range(100):
            errs += int(add(t, ti, 0, True) != (FS, ""))
        n = len(frames(t)); hs.append(bench_prep.labview_handles())                          # noqa: E702
        if n != 101:
            bad.append((rnd, n))
    h1 = bench_prep.labview_handles(); ok = errs == 0 and not bad and abs(h1 - h0) <= 100  # noqa: E702
    gate("AH 20 rounds x 100 Add Frame: 0 errors, 101 frames every round, handles flat +-100", ok, (errs, bad, h0, h1, hs))
    record(KA, OPA, ok, 2001, errs, h0, h1, hs, "1 first call + 20 rounds x 100 Add Frame(0, After T) on FS #%s of fresh never-saved byte copies of %s" % (FS, os.path.basename(EX)))
    return ok


def donor():
    os.path.exists(DON) and os.remove(DON); shutil.copyfile(EX, DON); g.open_panel(DON); time.sleep(1)  # noqa: E702
    fd = frames(DON)[0]; di = g._uid_index(DON, "Diagram", fd)                              # noqa: E702
    inner = [int(r["uid"]) for r in g.node_labels(DON, di)]
    fact("D frame #%s nodes before" % fd, inner)
    for _pass in range(2):           # pass 2: owners of terminals still on the frame (control terminals, tunnels), by GObject index
        for u in inner:
            for c in ("Node", "GObject"):
                order = [o["uid"] for o in g.report_all(DON, c)]
                if u in order:
                    g.delete_object(DON, c, order.index(u), verify=False)
                    break
        g.remove_bad_wires_scripted(DON)
        rows, _dt = allterms.read_terms(DON, allterms.OP_ALLTERMS_V1)
        left = [r for r in rows if int(r.get("frame_diagram") or 0) == fd]
        inner = sorted(set(int(r["owner_uid"]) for r in left if int(r["owner_uid"]) != FS))
        fact("D pass %d: %d frame terminals left, owners %s" % (_pass + 1, len(left), inner), [(r["term_name"], r["owner_class"]) for r in left][:12])
        if not left:
            break
    es = g.exec_state(DON)
    fact("D after strip: frame terminals %d, nodes %s, ES %s, GObjects %d" % (len(left), [r["uid"] for r in g.node_labels(DON, di)], es,
         len(g.report_all(DON, "GObject"))), left[:6])
    if gate("D DonorFs_v0: FS #%s frame #%s empty (0 terminals), ES 1" % (FS, fd), not left and es == 1, (len(left), es)):
        g.save(DON); V.LAB["DonorFs_v0"] = {"donor": DON, "uid": FS, "frame": fd, "md5": md5(DON)}            # noqa: E702
        gate("D saved", os.path.getsize(DON) > 0, md5(DON))


try:
    for p in (OPR, OPA):
        os.path.exists(p) and os.remove(p)
    bench_prep.restart_labview(); g.reset(); time.sleep(3)                                   # noqa: E702
    if build_reader() and build_adder():
        json.dump(V.LAB, open(LAB_P, "w", encoding="utf-8"), indent=1)
        g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                   # noqa: E702
        if gate("C COLD ExecState 1 both ops", g.exec_state(OPR) == 1 and g.exec_state(OPA) == 1, (md5(OPR), md5(OPA))):
            with g.hygiene_probe(OPR):
                okr = hyg_reader()
            if okr:
                with g.hygiene_probe(OPA):
                    hyg_adder()
                donor()
                json.dump(V.LAB, open(LAB_P, "w", encoding="utf-8"), indent=1)
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:300])  # noqa: E702
finally:
    V.subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("X LabVIEW gone", "labview.exe" not in V.subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    for p in SCRS:
        os.path.exists(p) and os.remove(p)
    gate("X scratch copies deleted", not any(os.path.exists(p) for p in SCRS), len(SCRS))
    bad = [k for k, v in V.G.items() if not v]
    arts = [{"path": p, "md5": md5(p)} for p in (OPR, OPA, DON, LAB_P) if os.path.exists(p)]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(V.G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(V.G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
