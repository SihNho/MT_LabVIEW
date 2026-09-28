r"""build_op_termtype - card 120-2 T1 (PD237(k)): the READ-ONLY terminal data-type reader claudeDev\OpTermDataType_v0.vi. FOUND FIRST: Terminal.Data
Type 634A008 resolves (a Variant, NAMES.md:470-484), no op reads it. REUSED: diag_c118_r1_opbuild.py's retype of hygiene-PASS OpWireJoints_v1 (24/0;
Traverse #124 -> IA #308 -> TMSC #683 -> PN #118 -> Close Ref #615/#630) with 'VI Server:Terminal' [632A813, 634A008], then the lossless OpConstValue_v1
byte route (v1b Flatten via OpBuildFlatten_v0; v1c Unflatten via OpBuildUnflatten_v0 typed U8[] from the hex VI's bytes -> U8[] + hex): the flattened
variant carries the TYPE DESCRIPTORS (NAMES.md:1153-1155). PREDICTION: every gate below PASS, ES 1 saved, COLD ES 1, LabVIEW gone.
    py tools/bgrun.py --material --max-min 20 --log tools/bench/build_op_termtype.log -- py -u tools/bench/build_op_termtype.py"""
import hashlib, json, os, shutil, subprocess, sys, time, traceback                        # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
sys.path[:0] = [os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")]
import protocol as P, gscript as g, bench_prep                                            # noqa: E401,E402
md5 = lambda p: hashlib.md5(open(p, "rb").read()).hexdigest()                             # noqa: E731
CD, KEY = g.CLAUDEDEV, "OpTermDataType_v0"
DONOR, DONOR_MD5, OP = os.path.join(CD, "OpWireJoints_v1.vi"), "29dcb59f58d4d959e965f9f545abd50b", os.path.join(CD, KEY + ".vi")
FLAT, UNFL = os.path.join(CD, "OpBuildFlatten_v0.vi"), os.path.join(CD, "OpBuildUnflatten_v0.vi")
HEXVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Bit Manipulation\Bytes to Lowercase Hex String.vi"
LAB_P, SIZE = os.path.join(HERE, "build_op_termtype_labels.json"), "data includes array or string size? (T)"
PN_OLD, TMSC, TRAV, CR_REF, CR_ARR, SEED_W = 118, 683, 124, 615, 630, 279
g._run.__defaults__ = (6.0, 120.0)
G, LAB = {}, {"class": "VI Server:Terminal", "props": ["632A813", "634A008"]}
def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:300]), flush=True); return bool(ok)  # noqa: E702
def sweep(t):
    out = {}
    for n in range(80):
        uid, rows = g.node_terms_uid(t, 0, n)
        if not uid:
            return out
        out[int(uid)] = (n, rows)
    return out
def ti(rows, name, src): return next(r for r in rows if r["name"].startswith(name) and bool(r["is_source"]) == src)
def panel(ind): return set(r["label"] for r in g.panel_wiring(OP) if bool(r["indicator"]) == ind)
def idx(cls, uid): return [int(o["uid"]) for o in g.report_all(OP, cls)].index(int(uid))
def delw(w): g.delete_object(OP, "Wire", [int(o["uid"]) for o in g.report_all(OP, "Wire")].index(int(w)), verify=False)
def wire(sc, su, sn, dc, du, dn, br=False): g.wire(OP, sc, idx(sc, su), sn, dc, idx(dc, du), dn, branch=br)
def make(fn, uid, name, src):   # create_indicator / create_control on #uid.name -> the ONE new panel label (None otherwise)
    ind = fn is g.create_indicator; b0 = panel(ind); by = sweep(OP); fn(OP, by[uid][0], ti(by[uid][1], name, src)["i"]); new = sorted(panel(ind) - b0)  # noqa: E702
    return new[0] if len(new) == 1 else None
def ind(uid, name, key):
    LAB[key] = make(g.create_indicator, uid, name, True)
    return gate("I indicator on #%s %r -> %r" % (uid, name, LAB[key]), LAB[key])
def creator(opv, cls, pos):
    inv0, n0 = g.uids(OP, "Invoke"), g.uids(OP, cls)
    vi = g.op(opv); vi.SetControlValue("vi path", OP); vi.SetControlValue("Class Name", "Terminal"); vi.SetControlValue("index", 0)  # noqa: E702
    vi.SetControlValue("location (0, 0)", list(pos)); g._run(vi)                        # noqa: E702  (the v1b/v1c call, verbatim)
    for u in sorted(g.uids(OP, "Invoke") - inv0):                                         # the creator's junk Invoke (v1b/v1c)
        g.delete_object(OP, "Invoke", idx("Invoke", u), verify=False)
    return sorted(g.uids(OP, cls) - n0)
def build():
    shutil.copyfile(DONOR, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)       # noqa: E702
    if not gate("D donor byte copy ES 1", g.exec_state(OP) == 1):
        return
    p0 = g.uids(OP, "Property"); g.build_property(OP, LAB["class"], [(p, False) for p in LAB["props"]], (900, 450))  # noqa: E702
    pn = sorted(g.uids(OP, "Property") - p0); by = sweep(OP)                              # noqa: E702
    srcs = [r["name"] for r in by[pn[0]][1] if r["is_source"]] if len(pn) == 1 else []
    if not gate("P one new Terminal PN with UID + Data Type sources", len(pn) == 1 and "UID" in srcs and "Data Type" in srcs, (pn, srcs)):
        return
    pn = LAB["pn"] = pn[0]; seed = make(g.create_control, pn, "reference", False)         # noqa: E702
    delw(ti(sweep(OP)[pn][1], "reference", False)["wire"]); delw(SEED_W)                  # noqa: E702
    g.wire_control(OP, [seed], "Function", idx("Function", TMSC), ["target class"])
    if not gate("S seed %r -> TMSC #%s target class" % (seed, TMSC), seed and ti(sweep(OP)[TMSC][1], "target class", False)["wire"], seed):
        return
    g.delete_object(OP, "Property", idx("Property", PN_OLD), verify=False); g.remove_bad_wires_scripted(OP)  # noqa: E702
    links = ((pn, "reference", TMSC, "specific class reference"), (pn, "error in (no error)", TRAV, "error out"),
             (CR_REF, "reference", pn, "reference out"), (CR_ARR, "error in (no error)", pn, "error out"))
    for su, sn, du, dn in links:
        by = sweep(OP); g.connect_terminals(OP, by[su][0], ti(by[su][1], sn, False)["i"], by[du][0], ti(by[du][1], dn, True)["i"])  # noqa: E702
    by = sweep(OP); got = [(ti(by[su][1], sn, False)["wire"], ti(by[du][1], dn, True)["wire"]) for su, sn, du, dn in links]  # noqa: E702
    if not gate("K old PN #%s gone, 4 links re-made on #%s, ES 1" % (PN_OLD, pn), PN_OLD not in by and all(a and a == b for a, b in got) and g.exec_state(OP) == 1, got):
        return
    if not all([ind(pn, "UID", "UID"), ind(pn, "Data Type", "DataType"), ind(pn, "error out", "Err")]):
        return
    fl = creator(FLAT, "FlattenString", (1300, 450))
    if not gate("F exactly one new FlattenString", len(fl) == 1, fl):
        return
    fl = fl[0]; w_dt = ti(sweep(OP)[pn][1], "Data Type", True)["wire"]                   # noqa: E702
    wire("Property", pn, "Data Type", "FlattenString", fl, "anything", True)
    if not gate("F Data Type -> Flatten.anything shares wire %s" % w_dt, w_dt and ti(sweep(OP)[fl][1], "anything", False)["wire"] == w_dt) or not ind(fl, "data string", "data"):
        return
    s0 = g.uids(OP, "SubVI"); g.drop_subvi(OP, HEXVI, 0, (1900, 450)); hv = sorted(g.uids(OP, "SubVI") - s0)  # noqa: E702
    u8c = make(g.create_control, hv[0], "bytes", False) if len(hv) == 1 else None
    u8c and delw(dict((r["label"], r) for r in g.panel_wiring(OP))[u8c]["wire"])
    uf = creator(UNFL, "FlattenUnflattenString", (1600, 650))
    if not gate("U one hex SubVI, one U8[] seed control, one Unflatten", len(hv) == 1 and u8c and len(uf) == 1, (hv, u8c, uf)):
        return
    hv, uf, LAB["u8type"] = hv[0], uf[0], u8c
    w_da = ti(sweep(OP)[fl][1], "data string", True)["wire"]
    wire("FlattenString", fl, "data string", "FlattenUnflattenString", uf, "binary string", True)
    g.wire_control(OP, [u8c], "FlattenUnflattenString", idx("FlattenUnflattenString", uf), ["type"])
    LAB["size"] = make(g.create_control, uf, SIZE, False)
    wire("FlattenUnflattenString", uf, "value", "SubVI", hv, "bytes")
    by = sweep(OP); pw = dict((r["label"], r) for r in g.panel_wiring(OP))                # noqa: E702
    ok = (ti(by[uf][1], "binary string", False)["wire"] == w_da and pw[u8c]["wire"] == ti(by[uf][1], "type", False)["wire"]
          and LAB["size"] and ti(by[uf][1], "value", True)["wire"] == ti(by[hv][1], "bytes", False)["wire"] != 0)
    if not gate("U data string -> binary string (branch), U8[] -> type, size? control, value -> bytes", ok, (w_da, LAB["size"])):
        return
    if not all([ind(hv, "hex string", "hex"), ind(uf, "value", "u8"), ind(uf, "rest of the binary string", "rest")]):
        return
    g.set_auto_error_handling(OP, False); es = g.exec_state(OP)                           # noqa: E702
    if gate("A assembled ES 1", es == 1, es):
        g.save(OP); LAB["controls"] = sorted(panel(False)); LAB["md5"] = md5(OP)          # noqa: E702
        gate("V saved by script", os.path.getsize(OP) > 0, LAB["md5"])


try:
    gate("M donor OpWireJoints_v1 md5 pinned", md5(DONOR) == DONOR_MD5, md5(DONOR))
    bench_prep.restart_labview(); g.reset(); time.sleep(3); build()                      # noqa: E702
    g.reset(); bench_prep.restart_labview(); g.reset(); time.sleep(3)                    # noqa: E702
    gate("C COLD ES 1 (fresh LabVIEW), md5 unchanged", "md5" in LAB and g.exec_state(OP) == 1 and md5(OP) == LAB["md5"], LAB.get("md5"))
    json.dump(LAB, open(LAB_P, "w", encoding="utf-8"), indent=1); print("  FACT  labels %r" % LAB, flush=True)  # noqa: E702
except Exception as e:                                                                    # noqa: BLE001
    traceback.print_exc(); gate("the run completed without an unhandled exception", False, repr(e)[:200])  # noqa: E702
finally:
    print("  FACT  refs %r" % (g.ref_counts(),), flush=True)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    gate("H LabVIEW gone; donor md5 unchanged", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower() and md5(DONOR) == DONOR_MD5)
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None, [{"path": OP, "md5": LAB["md5"]}] if LAB.get("md5") else [])), flush=True)
    sys.exit(1 if bad else 0)
