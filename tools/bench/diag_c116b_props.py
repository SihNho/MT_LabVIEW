r"""diag_c116b_props - card 116-2 STEP 0b (P0) + P1 dump, READ-ONLY on byte copies: B3 vs R1 property compare, then the SAVED R1 graph.
Part A (one fresh LabVIEW, COM): work copy of R1 (claudeDev\scratch_c116b_prop_<ts>.vi, discarded) + scratch copy of B3; per file
  A1 every LoopTunnel via g.tunnels (OpTunnels_v0: uid, IndexMode, face names, wires), A2 every Constant via OpConstValue_v1 (base-Constant
  cast, lossless flattened bytes, uid echo - prior art diag_c105_const.py), A3 the R1 graph dump (wiki_build.read_live + k_contract_79.mloops
  + build_d1_v0.owner_of, prior art diag_c114c_b3graph.py) -> tools/bench/graph_l2r1_saved_20260928.json (fs_tunnel_pairs carried from the
  B3 dump, review c116b-keys.md:46: term_a/term_b only are used). Part B (a second fresh LabVIEW, NI's own LabVIEWCLI CreateComparisonReport
  = LVCompare, XML, -nobdcosm) on two fresh claudeDev byte copies -> tools/bench/diag_c116b_cmp.xml; the report is parsed offline afterwards.
Nothing is run, wired, deleted or saved; copies deleted; LabVIEW killed. PREDICTION: G1 tunnel count B3 == R1 == 151, every uid read with
identity; G2 IndexMode + face names equal for every tunnel uid kept in both (#637's included); G3 constant uid sets equal, every
uid echo == listing uid, flattened bytes equal per uid; G4 graph dump: 5827 terminal rows, 10138 objs, #637 in loops with no left_of entry for
the 6 retired pairs; G5 CLI rc 0 and the XML report exists; LabVIEW gone; inputs unchanged.
    py tools/bgrun.py --material --max-min 60 --log tools/bench/diag_c116b_props.log -- py -u tools/bench/diag_c116b_props.py"""
import json, os, re, shutil, subprocess, sys, time                                  # noqa: E401
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE))   # noqa: E702
sys.path.insert(0, os.path.join(ROOT, "tools"))
import stagekit as K, vigraph as V                                                 # noqa: E401,E402
g = K.g
R1, R1M = os.path.join(g.CLAUDEDEV, "D1_l2_r1_20260928_055441.vi"), "f465196bb5016638b146e771ba54c5af"
B3, B3M = os.path.join(g.CLAUDEDEV, "D1_l2_b3_20260928_032703.vi"), "1b5c12d71ca48f22e3f4b80316c67e51"
OUTG, OUTJ, XML = os.path.join(HERE, "graph_l2r1_saved_20260928.json"), os.path.join(HERE, "diag_c116b_props.json"), os.path.join(HERE, "diag_c116b_cmp.xml")
OP = os.path.join(g.CLAUDEDEV, "OpConstValue_v1.vi")
LAB = json.load(open(os.path.join(HERE, "opconstvalue_labels.json"), encoding="utf-8"))
GB3 = json.load(open(os.path.join(HERE, "graph_l2b3_20260928.json"), encoding="utf-8"))
SR = {9018, 9025, 29505, 29512, 1147, 1142, 5796, 5805, 119, 2972, 7311, 11001}
OWN = [637, 639, 686, 2294, 3644, 2580, 2396, 4432, 3656, 3920, 4031, 5129, 5328, 28343, 5752, 5569, 32572, 24364]
CLI = r"C:\Program Files (x86)\National Instruments\Shared\LabVIEW CLI\LabVIEWCLI.exe"
LVEXE = r"C:\Program Files\National Instruments\LabVIEW 2026\LabVIEW.exe"
DRY = bool(getattr(g.report_all, "_dry", False))                                   # stage_prerun --dry stubs COM (as stage_d1_l2r1.py)
s = K.Stage(R1, R1M, "scratch_c116b_prop", preload=False, deadline_min=45, reserve_s=180, out_json=OUTJ, task="card 116-2 STEP 0b")


def u8(v):
    try:
        return bytes(v) if v is not None and not isinstance(v, str) else b""
    except (TypeError, ValueError):
        return bytes(int(x) & 0xFF for x in v)


def read_const(t, i):
    vi = g.op(OP)
    vi.SetControlValue(LAB["hex"], "POISON"); vi.SetControlValue("UID", 0); vi.SetControlValue(LAB["size"], False)   # noqa: E702
    vi.SetControlValue("vi path", t); vi.SetControlValue("Class Name", "Constant"); vi.SetControlValue("index", i)   # noqa: E702
    g._run(vi)
    return {"uid": int(vi.GetControlValue("UID")), "hex": u8(vi.GetControlValue(LAB["u8"])).hex(), "err": str(g._err(vi, "error out") or "")[:120]}


def props(t, tag):
    n = g.count(t, "LoopTunnel")
    tun = [g.tunnels(t, i) for i in range(n)]
    lst = [int(o["uid"]) for o in g.report_all(t, "Constant")]
    con = [dict(read_const(t, i), want=u) for i, u in enumerate(lst)]
    s.fact("{0}: {1} LoopTunnels, {2} Constants read; handles {3}".format(tag, n, len(con), K.mod("bench_prep").labview_handles()))
    return {"tunnels": tun, "consts": con}


def body(_):
    # READ-ONLY: the work copy is registered as a scratch the way diag_c105_const.py:55 (read-only prior art) does; rev 1 called
    # discard_work, which stage_prerun.MODIFY_VERBS (:2011) lists, so the launch gate asked for a plan this read has none of.
    s.start(); s.scratches.append(s.work); b3c = s.scratch("b3", B3)                # noqa: E702
    P1, P3 = props(s.work, "R1"), props(b3c, "B3")
    s.R["props"] = {"r1": P1, "b3": P3}; s.dump()                                   # noqa: E702
    t1, t3 = dict((x["uid"], x) for x in P1["tunnels"]), dict((x["uid"], x) for x in P3["tunnels"])
    s.gate("G1 LoopTunnel count R1 == B3 == 151, every uid nonzero and distinct", len(t1) == len(t3) == 151 == len(P1["tunnels"]) and 0 not in t1 and 0 not in t3, (len(t1), len(t3)))
    key = lambda x: (x["index_mode"], x["out_name"], x["out_is_source"], tuple(x["in_names"]), tuple(x["in_is_source"]))   # noqa: E731
    dt = [(u, key(t3[u]), key(t1[u])) for u in sorted(set(t1) & set(t3)) if key(t1[u]) != key(t3[u])]
    wd = [(u, (t3[u]["out_wire"], t3[u]["in_wires"]), (t1[u]["out_wire"], t1[u]["in_wires"])) for u in sorted(set(t1) & set(t3))
          if (t1[u]["out_wire"], t1[u]["in_wires"]) != (t3[u]["out_wire"], t3[u]["in_wires"])]
    s.fact("TUNNEL index modes R1: {0}".format(sorted(set((u, t1[u]["index_mode"]) for u in OWN if u in t1))))
    s.fact("TUNNEL wire differences (reported, not gated; K4 of diag_c116b_keys already equal): {0}".format(wd[:20]))
    s.gate("G2 IndexMode + face names/directions equal for every tunnel kept in both ({0})".format(len(set(t1) & set(t3))), not dt and set(t1) == set(t3), dt[:20])
    c1, c3 = dict((c["want"], c) for c in P1["consts"]), dict((c["want"], c) for c in P3["consts"])
    echo = [c for c in P1["consts"] + P3["consts"] if c["uid"] != c["want"] or c["err"]]
    dc = [(u, c3[u]["hex"][:80], c1[u]["hex"][:80]) for u in sorted(set(c1) & set(c3)) if c1[u]["hex"] != c3[u]["hex"]]
    s.gate("G3 constants: uid sets equal ({0}/{1}), every echo == listing uid, no op error, bytes equal per uid".format(len(c1), len(c3)),
           set(c1) == set(c3) and not echo and not dc, {"echo_bad": echo[:10], "diff": dc[:20], "only_r1": sorted(set(c1) - set(c3)), "only_b3": sorted(set(c3) - set(c1))})
    lv = K.mod("wiki_build").read_live(s.work, fs_pairs=GB3["fs_tunnel_pairs"])
    loops, BD = K.mod("k_contract_79").mloops(s, s.work), K.mod("build_d1_v0")
    diags = [int(o["uid"]) for o in lv["objs"] if o["class"] == "Diagram"]
    O, todo = {}, diags + OWN
    while todo:
        u = todo.pop(0)
        if u in O:
            continue
        v = s.safe("owner_of #{0}".format(u), lambda: BD.owner_of(s.work, u, strict=False), ("?", 0))[0] or ("?", 0)
        O[u] = (str(v[0]), int(v[1] or 0))
        if O[u][1] and O[u][0] in V.STRUCT_OWNER:
            todo.append(O[u][1])
    gr = {"vi": R1, "md5": R1M, "source": "tools/bench/diag_c116b_props.py (read_live + mloops + owner_of on a byte copy of the SAVED R1)", "terminals": lv["terminals"],
          "objs": lv["objs"], "loops": loops, "fs_tunnel_pairs": GB3["fs_tunnel_pairs"], "owners": dict((str(k), list(v)) for k, v in sorted(O.items()))}
    if not DRY:
        json.dump(gr, open(OUTG, "w", encoding="utf-8")); s.fact("WROTE {0} md5 {1}".format(OUTG, K.md5(OUTG)))   # noqa: E702
    L637 = [L for L in loops if int(L.get("loop_uid", 0)) == 637]
    left = set(int(k) for L in L637 for k in (L.get("left_of") or {})) | set(int(x) for L in L637 for v in (L.get("left_of") or {}).values() for x in v)
    s.gate("G4 dump: 5827 rows, 10138 objs, every Diagram owner resolved, #637 in loops without the 12 SR uids", len(lv["terminals"]) == 5827 and len(lv["objs"]) == 10138
           and all(O[d][0] != "?" for d in diags) and len(L637) == 1 and not (left & SR), (len(lv["terminals"]), len(lv["objs"]), len(L637), sorted(left & SR)))


def cli_compare():
    ts = time.strftime("%Y%m%d_%H%M%S")
    a, b = os.path.join(g.CLAUDEDEV, "scratch_c116b_cmp_b3_%s.vi" % ts), os.path.join(g.CLAUDEDEV, "scratch_c116b_cmp_r1_%s.vi" % ts)
    shutil.copyfile(B3, a); shutil.copyfile(R1, b); os.path.exists(XML) and os.remove(XML)   # noqa: E702
    s.gate("C0 compare copies are byte copies", K.md5(a) == B3M and K.md5(b) == R1M, (os.path.basename(a), os.path.basename(b)))
    cmd = [CLI, "-OperationName", "CreateComparisonReport", "-vi1", a, "-vi2", b, "-reportType", "XML", "-reportPath", XML, "-nobdcosm",
           "-LabVIEWPath", LVEXE, "-PortNumber", "3364"]
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=1200); rc, out = p.returncode, (p.stdout or "") + (p.stderr or "")   # noqa: E702
    except subprocess.TimeoutExpired as e:
        rc, out = "TIMEOUT", str(e)[:400]
    s.fact("CLI rc {0} after {1:.0f} s: {2}".format(rc, time.time() - t0, re.sub(r"\s+", " ", out)[-1200:]))
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(5)   # noqa: E702
    for p_ in (a, b):
        for _i in range(5):
            try:
                os.path.exists(p_) and os.remove(p_); break                        # noqa: E702
            except OSError:
                time.sleep(3)
    s.gate("G5 CLI rc 0 and the XML report exists ({0} B)".format(os.path.getsize(XML) if os.path.exists(XML) else 0), rc == 0 and os.path.exists(XML), rc)
    s.gate("C9 compare copies deleted", not os.path.exists(a) and not os.path.exists(b))


if __name__ == "__main__":
    print(__doc__, flush=True)
    rc = K.run(body, s)
    if DRY:
        sys.exit(rc)                                                                # the dry path stops before the CLI part (no subprocess)
    g.reset(); subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
    try:
        cli_compare()
    except Exception as e:                                                          # noqa: BLE001
        s.gate("G5 CLI compare ran without an exception", False, str(e)[:200])
    subprocess.run(["taskkill", "/F", "/IM", "LabVIEW.exe"], capture_output=True, text=True, timeout=60); time.sleep(4)   # noqa: E702
    gone = "labview.exe" not in subprocess.run(["tasklist"], capture_output=True, text=True, timeout=60).stdout.lower()
    s.gate("Z LabVIEW gone; R1 and B3 md5 unchanged", gone and K.md5(R1) == R1M and K.md5(B3) == B3M, (gone, K.md5(R1), K.md5(B3)))
    s.dump(); sys.exit(s.summary())
