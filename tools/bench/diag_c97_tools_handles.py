r"""diag_c97_tools_handles.py - card 97-3: the discriminating test of archive/peer/2026-09-26-c97-t2handles.md §4 for the
one FAIL of tools/bench/selftest_c97_tools.log:120 (T2 +113 handles over ONE cold move_into_frame invocation). Claim under
test = the review's alternative: first-load cost of op VIs, not a per-call leak. Same never-saved scratch pattern as the
self-test (byte copy of D1_s1_copy.vi, deleted at the end; no stagekit import - judgement c97).
PREDICTIONS (gates; handles AND private bytes printed at every reading):
 S   setup: control L from a carrier IA; case A in 7911, case B in 639, Boolean #11639 into both selectors; True frames
 W0  warm-up, every op T2 uses called once, Delta per step RECORDED (no gate): T3 on case B's set; OpConstWire_v1,
     OpWireCtl_v0, OpConnectFromWire_v0 (+OpWireSource_v5) each once, idempotent, on existing 7911 edges
 W1  T2 on the PD206(b) set WARM: edge table equal AND |Delta handles| <= 100
 B1  20 warm idempotent OpConnectNested_v1 (#8741 -> #8764 'x' inside case A's frame): wire delta 0 each, |Delta| <= 100
 B2  20 warm idempotent OpConnectFromWire_v0 (the inner wire at #27716 'index'): wire delta 0 each, |Delta| <= 100
 B3  5 OpAllTerms_v0 reads: |Delta| <= 100
 H   LabVIEW gone, scratch deleted, S1 md5 unchanged
    py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_c97_tools_handles.log -- py -u tools/bench/diag_c97_tools_handles.py
"""
import hashlib, json, os, shutil, subprocess, sys, time                                     # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))  # noqa: E702
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import protocol as P                                                                      # noqa: E402
import gscript as g                                                                       # noqa: E402
import bench_prep as BP                                                                   # noqa: E402
import allterms as A                                                                      # noqa: E402
import build_d1_v0 as B                                                                   # noqa: E402
import build_opconnectnested_v1 as CN                                                     # noqa: E402
import build_opconnectfromwire_v0 as CF                                                   # noqa: E402
g._run.__defaults__ = (6.0, 120.0)
S1, S1_MD5 = os.path.join(g.CLAUDEDEV, "D1_s1_copy.vi"), "3e3d23cefd3a334001aa9d6156bf1aee"
FIX = os.path.join(g.CLAUDEDEV, "scratch_c97_h_%s.vi" % time.strftime("%Y%m%d_%H%M%S"))
SET_A, SET_B = [8741, 8775, 8795, 8476, 8764, 28180, 29009, 28233, 27716, 11310], [11261, 8323]
CNL, CFL = json.load(open(CN.MAP_OUT, encoding="utf-8")), json.load(open(CF.MAP_OUT, encoding="utf-8"))
G, R = {}, {"readings": []}


def md5(p): return hashlib.md5(open(p, "rb").read()).hexdigest()


def gate(k, ok, d=""):
    G[k] = bool(ok); print("  %s  %s  %s" % ("PASS" if ok else "FAIL", k, str(d)[:400]), flush=True); return bool(ok)  # noqa: E702


def pb():
    r = subprocess.run(["powershell", "-NoProfile", "-Command", "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                        "Select-Object -First 1).PrivateMemorySize64"], capture_output=True, text=True, timeout=60)
    return int((r.stdout or "0").strip() or 0)


def H(tag):
    h, m = BP.labview_handles(), pb()
    R["readings"].append((tag, h, m)); print("  READ  %-28s handles %s  private MB %.1f" % (tag, h, m / 1e6), flush=True)  # noqa: E702
    return h


def tix(di, uid, pred):
    _u, rows = g.node_terms_uid(FIX, di, g._node_index(FIX, di, uid))
    return [r for r in rows if pred(r)][0]


def src_i(w): return [x for x in CF.wire_source_owner(FIX, w, n=10) if x.get("is_source")][0]["i"]


def case(D, loc, pos, L, boolsrc):
    c = g.case_in(FIX, D, loc, L, position=pos)
    di = g._uid_index(FIX, "Diagram", D); ni = g._node_index(FIX, di, c["case"])          # noqa: E702
    s = [r for r in g.node_terms_uid(FIX, di, ni)[1] if not r["is_source"]][0]
    CN.connect_nested_v1(FIX, di, ni, s["i"], boolsrc[0], boolsrc[1], boolsrc[2], CNL)
    fr = g.case_frames(FIX, c["case"])
    return [f for n, f in zip(fr["names"], fr["frames"]) if n.strip() == "True"][0]


def body():
    gate("K S1 md5 before", md5(S1) == S1_MD5)
    BP.restart_labview(); g.reset(); time.sleep(3); shutil.copyfile(S1, FIX); time.sleep(0.4)  # noqa: E702
    gate("K scratch is a byte copy of S1", md5(FIX) == S1_MD5, os.path.basename(FIX))
    g.ensure_loaded(FIX); H("loaded")                                                     # noqa: E702
    ia0 = g.uids(FIX, "IndexArray"); g.build_index_array(FIX, (9000, 9000))              # noqa: E702
    ni = [t[0] for t in g.node_info(FIX) if t[1] == "Index Array"][-1]; _n, L = g.create_control(FIX, ni, 2)  # noqa: E702
    d639 = g._uid_index(FIX, "Diagram", 639); n = g._node_index(FIX, d639, 11639)        # noqa: E702
    boolsrc = (d639, n, [r["i"] for r in g.node_terms_uid(FIX, d639, n)[1] if r["is_source"]][0])
    FA = case(7911, (9000, 9300), (5250, 1600), L, boolsrc); FB = case(639, (9000, 9700), (5800, 1760), L, boolsrc)  # noqa: E702
    gate("S setup: control %r, True frames A #%s B #%s" % (L, FA, FB), bool(L and FA and FB))
    h = H("W0 start")
    r3 = g.move_into_frame(FIX, FB, SET_B, (5800, 1760)); h1 = H("W0 after T3 (case B)")  # noqa: E702
    d7911 = g._uid_index(FIX, "Diagram", 7911)
    ix = tix(d7911, 8741, lambda r: r["wire"] == 8804)
    print("  FACT  W0 OpConstWire_v1 idem %r" % (g.wire_const(FIX, "DigitalNumericConstant", g._uid_index(FIX, "DigitalNumericConstant", 8775),
                                                            "IndexArray", g._uid_index(FIX, "IndexArray", 8741), ix["i"]),), flush=True)
    h2 = H("W0 after OpConstWire_v1")
    print("  FACT  W0 OpWireCtl_v0 idem %r" % (g.wire_control(FIX, ["Exp Baseline"], "Function", g._uid_index(FIX, "Function", 8764), ["y"],
                                                             branch=True, src_diagram_index=d7911),), flush=True)
    h3 = H("W0 after OpWireCtl_v0")
    hw = tix(d7911, 28180, lambda r: r["name"] == "half-width" and not r["is_source"])
    print("  FACT  W0 OpConnectFromWire_v0 idem %r" % (CF.connect_from_wire(FIX, 31064, src_i(31064), d7911, g._node_index(FIX, d7911, 28180), hw["i"], CFL),), flush=True)
    h4 = H("W0 after OpConnectFromWire_v0")
    R["W0"] = {"T3": h1 - h, "OpConstWire_v1": h2 - h1, "OpWireCtl_v0": h3 - h2, "OpConnectFromWire_v0+OpWireSource_v5": h4 - h3}
    print("  FACT  W0 first-call deltas %r; T3 table missing %r extra %r" % (R["W0"], r3["missing"], r3["extra"]), flush=True)
    ha = H("W1 before T2 warm"); r = g.move_into_frame(FIX, FA, SET_A, (5250, 1600)); hb = H("W1 after T2 warm")  # noqa: E702
    gate("W1 T2 warm: edge table equal (%d edges), +%d tunnels" % (len(r["edges_before"]), len(r["new_tunnels"])), not r["missing"] and not r["extra"], (r["missing"], r["extra"]))
    gate("W1 T2 warm: handles flat +-100", abs(hb - ha) <= 100, (ha, hb, hb - ha))
    dF = g._uid_index(FIX, "Diagram", FA)
    x = tix(dF, 8764, lambda q: q["name"] == "x" and not q["is_source"])
    s = tix(dF, 8741, lambda q: q["is_source"] and q["wire"] == x["wire"])
    h5 = H("B1 before")
    b1 = [CN.connect_nested_v1(FIX, dF, g._node_index(FIX, dF, 8764), x["i"], dF, g._node_index(FIX, dF, 8741), s["i"], CNL) for _k in range(20)]
    h6 = H("B1 after 20 OpConnectNested_v1")
    gate("B1 20 idempotent OpConnectNested_v1: wire delta 0 each, no error", all(q[0] == 0 and not q[2] for q in b1), b1[:3])
    gate("B1 handles flat +-100 over 20 calls", abs(h6 - h5) <= 100, (h5, h6, h6 - h5))
    ki = tix(dF, 27716, lambda q: q["name"] == "index" and not q["is_source"])
    b2 = [CF.connect_from_wire(FIX, ki["wire"], src_i(ki["wire"]), dF, g._node_index(FIX, dF, 27716), ki["i"], CFL) for _k in range(20)]
    h7 = H("B2 after 20 OpConnectFromWire_v0")
    gate("B2 20 idempotent OpConnectFromWire_v0: wire delta 0 each, no error", all(q[0] == 0 and not q[2] for q in b2), b2[:2])
    gate("B2 handles flat +-100 over 20 calls (+20 OpWireSource_v5 walks)", abs(h7 - h6) <= 100, (h6, h7, h7 - h6))
    for _k in range(5):
        A.read_terms(FIX)
    h8 = H("B3 after 5 OpAllTerms_v0")
    gate("B3 handles flat +-100 over 5 whole-VI reads", abs(h8 - h7) <= 100, (h7, h8, h8 - h7))
    R["refs"] = g.ref_counts()


try:
    body()
except Exception as e:                                                                    # noqa: BLE001
    import traceback
    traceback.print_exc(); G["EXC %s" % str(e)[:120]] = False                            # noqa: E702
finally:
    print("  FACT  refs %r" % (g.ref_counts(),), flush=True)
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)  # noqa: E702
    for _k in range(5):
        try:
            if os.path.exists(FIX):
                os.remove(FIX)
            break
        except OSError:
            time.sleep(2)
    gate("H LabVIEW gone", "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower())
    gate("H scratch deleted", not os.path.exists(FIX)); gate("H S1 md5 unchanged", md5(S1) == S1_MD5)  # noqa: E702
    OUT = os.path.join(HERE, "diag_c97_tools_handles.json"); R["gates"] = G                 # noqa: E702
    json.dump(R, open(OUT, "w", encoding="utf-8"), indent=1, default=str)
    bad = [k for k, v in G.items() if not v]
    print("=== GATES: %d pass / %d fail; failing: %s" % (len(G) - len(bad), len(bad), bad), flush=True)
    print(P.result_line(P.make_result(len(G) - len(bad), len(bad), bad[0] if bad else None,
                                      [{"path": os.path.relpath(OUT, ROOT), "md5": md5(OUT)}])), flush=True)
    sys.exit(1 if bad else 0)
