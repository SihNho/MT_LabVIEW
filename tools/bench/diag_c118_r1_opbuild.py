r"""diag_c118_r1_opbuild - card 118-4 R1 (PD234(j)(1)): build two READ-ONLY typed constant-VALUE readers,
claudeDev\OpConstValueRing_v0.vi (VI Server:RingConstant) and OpConstValueArr_v0.vi (VI Server:ArrayConstant).
FOUND FIRST: OpConstValue_v1 (base Constant cast: value for StringConstant only, VOID for every other class, NAMES.md:1157-1162),
OpConstValueN_v1 (DigitalNumericConstant cast; RingConstant is not in that traverse, diag_c118_p0.json:452), OpConstValueB_v0 (Boolean).
The fix recorded in NAMES.md = build the Value node for the object's MOST-SPECIFIC class. Donor = the hygiene-PASS OpWireJoints_v1
(op_hygiene/OpWireJoints_v1.json: Traverse #124 -> IA #308 -> TMSC #683 -> PN #118 -> Close Reference #615 (typed ref) and #630
(References array); diag_c117a_opv1b.log:7-23). Retype = the proven build_opconstvaluen_v0.py:74-118 steps on that donor: new PN
[GObject.UID 632A813, Constant.Value 634AC00 (+ Representation 5DCFC00 for the ring, dropped if the class lacks it)], a typed seed
control from its `reference` -> TMSC 'target class', old PN #118 deleted, its four links re-made on the new PN, indicators on UID / Value /
(Representation) / error out. No target VI is touched.
PREDICTION per op: D copy ES 1; P new PN has UID + Value sources; S seed -> TMSC; K old PN deleted, 4 links re-made, ES 1; I indicators;
A saved by script ES 1; C COLD ES 1 in a fresh LabVIEW. Labels -> tools/bench/diag_c118_oplabels.json. LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/diag_c118_r1_opbuild.log -- py -u tools/bench/diag_c118_r1_opbuild.py"""
import json, os, shutil, subprocess, sys, time, traceback                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import hashlib                                                                            # noqa: E402
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402  (the proven op-build form, diag_c117a_opv1.py:15)


class K(object):
    md5 = staticmethod(lambda p: hashlib.md5(open(p, "rb").read()).hexdigest())
CD, DONOR = g.CLAUDEDEV, os.path.join(g.CLAUDEDEV, "OpWireJoints_v1.vi")
DONOR_MD5, LAB_P = "29dcb59f58d4d959e965f9f545abd50b", os.path.join(HERE, "diag_c118_oplabels.json")
OPS = (("OpConstValueRing_v0", "VI Server:RingConstant", [("632A813", False), ("634AC00", False), ("5DCFC00", False)]),
       ("OpConstValueArr_v0", "VI Server:ArrayConstant", [("632A813", False), ("634AC00", False)]))
PN_OLD, TMSC, TRAV, CR_REF, CR_ARR, SEED_W = 118, 683, 124, 615, 630, 279
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {}


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


def build(key, cls, props):
    op = os.path.join(CD, key + ".vi")
    if os.path.exists(op):
        os.remove(op)
    shutil.copyfile(DONOR, op); time.sleep(0.3); g.open_panel(op); time.sleep(1.0)       # noqa: E702
    if not gate("%s D donor byte copy ES 1" % key, g.exec_state(op) == 1):
        return None
    p0 = g.uids(op, "Property")
    try:
        g.build_property(op, cls, props, (900, 450))
    except Exception as e:                                                                # noqa: BLE001
        print("  FACT  %s build_property %r raised %s" % (key, props, str(e)[:160]), flush=True)
    pn = sorted(g.uids(op, "Property") - p0)
    by = sweep(op); srcs = [r["name"] for r in by[pn[0]][1] if r["is_source"]] if len(pn) == 1 else []
    if len(props) == 3 and not pn:
        props = props[:2]; g.build_property(op, cls, props, (900, 450)); pn = sorted(g.uids(op, "Property") - p0)  # noqa: E702
        by = sweep(op); srcs = [r["name"] for r in by[pn[0]][1] if r["is_source"]] if len(pn) == 1 else []  # noqa: E702
    if len(props) == 3 and "Representation" not in srcs and len(pn) == 1:                  # class lacks it: rebuild with 2 props
        print("  FACT  %s PN #%s sources %r lack Representation - rebuilt with UID + Value" % (key, pn[0], srcs), flush=True)
        g.delete_object(op, "Property", idx(op, "Property", pn[0]), verify=False); props = props[:2]  # noqa: E702
        p0 = g.uids(op, "Property"); g.build_property(op, cls, props, (900, 450)); pn = sorted(g.uids(op, "Property") - p0)  # noqa: E702
        by = sweep(op); srcs = [r["name"] for r in by[pn[0]][1] if r["is_source"]] if len(pn) == 1 else []  # noqa: E702
    if not gate("%s P one new %s PN with UID + Value sources" % (key, cls), len(pn) == 1 and "UID" in srcs and "Value" in srcs, (pn, srcs)):
        return None
    pn = pn[0]; c0 = panel(op, False)                                                     # noqa: E702
    g.create_control(op, by[pn][0], ti(by[pn][1], "reference", False)["i"]); seed = sorted(panel(op, False) - c0)  # noqa: E702
    by = sweep(op); w_seed = ti(by[pn][1], "reference", False)["wire"]                     # noqa: E702
    ws = [int(o["uid"]) for o in g.report_all(op, "Wire")]; g.delete_object(op, "Wire", ws.index(int(w_seed)), verify=False)  # noqa: E702
    ws = [int(o["uid"]) for o in g.report_all(op, "Wire")]; g.delete_object(op, "Wire", ws.index(SEED_W), verify=False)  # noqa: E702
    g.wire_control(op, seed, "Function", idx(op, "Function", TMSC), ["target class"])
    by = sweep(op)
    if not gate("%s S seed %r -> TMSC #%s target class" % (key, seed, TMSC), len(seed) == 1 and ti(by[TMSC][1], "target class", False)["wire"], seed):
        return None
    g.delete_object(op, "Property", idx(op, "Property", PN_OLD), verify=False); g.remove_bad_wires_scripted(op)  # noqa: E702
    links = ((pn, "reference", TMSC, "specific class reference"), (pn, "error in (no error)", TRAV, "error out"),
             (CR_REF, "reference", pn, "reference out"), (CR_ARR, "error in (no error)", pn, "error out"))
    for su, sn, du, dn in links:
        by = sweep(op); g.connect_terminals(op, by[su][0], ti(by[su][1], sn, False)["i"], by[du][0], ti(by[du][1], dn, True)["i"])  # noqa: E702
    by = sweep(op)
    got = [(ti(by[su][1], sn, False)["wire"], ti(by[du][1], dn, True)["wire"]) for su, sn, du, dn in links]
    if not gate("%s K old PN #%s gone, 4 links re-made on #%s (sink wire == source wire), ES 1" % (key, PN_OLD, pn),
                PN_OLD not in by and all(a and a == b for a, b in got) and g.exec_state(op) == 1, got):
        return None
    lab = {"pn": pn, "class": cls, "props": [p for p, _w in props], "seed": seed[0]}
    for name, k in (("UID", "UID"), ("Value", "Value"), ("Representation", "Repr"), ("error out", "Err")):
        if name == "Representation" and len(props) < 3:
            continue
        i0 = panel(op, True); by = sweep(op); g.create_indicator(op, by[pn][0], ti(by[pn][1], name, True)["i"]); new = sorted(panel(op, True) - i0)  # noqa: E702
        if not gate("%s I indicator on %r -> %r" % (key, name, new), len(new) == 1):
            return None
        lab[k] = new[0]
    g.set_auto_error_handling(op, False); es = g.exec_state(op)                           # noqa: E702
    if gate("%s A assembled ES 1" % key, es == 1, es):
        g.save(op); lab["controls"] = sorted(panel(op, False)); lab["md5"] = K.md5(op); LAB[key] = lab  # noqa: E702
        gate("%s V saved by script" % key, os.path.getsize(op) > 0, lab["md5"])
    try:
        g.close_panel(op)
    except Exception:                                                                     # noqa: BLE001
        pass


h0 = None
try:
    gate("M donor OpWireJoints_v1 md5 pinned", K.md5(DONOR) == DONOR_MD5, K.md5(DONOR))
    bench_prep.restart_labview(); g.reset(); time.sleep(3); h0 = bench_prep.labview_handles()  # noqa: E702
    for key, cls, props in OPS:
        build(key, cls, list(props))
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                    # noqa: E702
    for key in list(LAB):
        op = os.path.join(CD, key + ".vi")
        gate("%s C COLD ES 1 (fresh LabVIEW), md5 unchanged" % key, g.exec_state(op) == 1 and K.md5(op) == LAB[key]["md5"], K.md5(op))
    json.dump(LAB, open(LAB_P, "w", encoding="utf-8"), indent=1); print("  FACT  labels %r" % LAB, flush=True)  # noqa: E702
    gate("L both ops built", sorted(LAB) == sorted(k for k, _c, _p in OPS), sorted(LAB))
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
finally:
    try:
        print("  FACT  handles at end %r (start %r); refs %r" % (bench_prep.labview_handles(), h0, g.ref_counts()), flush=True)
    except Exception:                                                                     # noqa: BLE001
        pass
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("H LabVIEW gone; donor md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower() and K.md5(DONOR) == DONOR_MD5)
    bad = [k for k, v in G.items() if not v]
    arts = [{"path": os.path.join(CD, k + ".vi"), "md5": v["md5"]} for k, v in LAB.items()]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, arts)), flush=True)
    sys.exit(1 if bad else 0)
