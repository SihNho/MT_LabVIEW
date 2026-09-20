r"""build_track_v6_queue.py - Track_v6_CPU_queue_v0.vi: step C v2.1 (docs/stage2-assembly-step-c.md) - the kernel path
of the step-B replay core moved into the pool-queue producer/consumer structure, REPLAY mode: three FOR loops over the
same N running in parallel through queues with blocking calls; the pool is a queue of IMAGE REFNUMS.

   [head]  HARNESS_loadcal, windows; SAMPLE: IMAQ Create('sample') -> IMAQ ReadFile(frame 0, 'Sample Path')
           -> KT = a top-level kernel instance (type source for the result queues AND a one-shot self-check)
           PathToStr.vi (String type source)  ;  5 kernel state/param controls made on KT
   [Q]     Obtain x7: Q_free/Q_img <- 'New Image' (image refnum) ; Q_meta/Q_rmeta <- PathToStr.string ;
           Q_res/Q_good/Q_pos <- KT outputs                                   (all unbounded, timeouts -1)
   [pool]  For i over Pool Names[8] (indexed): IMAQ Create(name_i) -> Enqueue(Q_free, image)
   [ACQ]   For i over Frame Paths (indexed): Dequeue(Q_free) -> ReadFile(StrToPath(path_i), image) ->
           Enqueue(Q_img, image) ; Enqueue(Q_meta, path_i)          (error-chained: Q_meta after Q_img)
   [TRK]   For n (N from an indexed Frame Paths tunnel whose inner wire is deleted): Dequeue(Q_img) ->
           kernel(image; 3 registers) ; Dequeue(Q_meta) ; Enqueue Q_res/Q_good/Q_pos/Q_rmeta (chained) ;
           Enqueue(Q_free, image) LAST in the chain (the image is returned only after the kernel used it)
   [sink]  For n (same N trick): Dequeue Q_res/Q_good/Q_pos/Q_rmeta (chained) -> 4 auto-indexed outputs ->
           XYZ/GOOD/POS/META ; Release x7 chained from the sink's last error out (so they run after the sink)
GATES (fatal, must()): every wire by uid / tunnel topology (step-B helpers); all three arrays flipped to
IndexMode 0 where whole values cross; registers by UID-set; ExecState 1 -> save; then the numeric sequence
1 -> 2 -> 200 -> --full with META[n] == Frame Paths[n], KT output == row 0, and XYZ/GOOD/POS EXACT vs the reference
before the first lost bead. Residual (recorded): image-refnum identity of the returned pool is not readable over COM.
  py tools/bgrun.py --max-min 50 --log tools/bench/build_track_v6_queue.log -- py -u tools/recipes/build_track_v6_queue.py [--n=200] [--full] [--build-only]
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402
import build_track_v6_core as B  # noqa: E402  (must, walk, term, drop, wire_sub, string_array_control, load_reference)

VIS = B.VIS
OP = os.path.join(g.CLAUDEDEV, "Track_v6_CPU_queue_v0.vi")
P2S = os.path.join(g.CLAUDEDEV, "PathToStr.vi")
DONOR = os.path.join(g.CLAUDEDEV, "background VIs_COPY", "save N xyz traces.vi")
STATE, STATE_OUT, PARAMS, OUT_KEYS = B.STATE, B.STATE_OUT, B.PARAMS, B.OUT_KEYS
LABELS_OUT = os.path.join(os.path.dirname(HERE), "bench", "track_v6_queue_labels.json")
must, walk, term = B.must, B.walk, B.term
g._run.__defaults__ = (6.0, 120.0)


def fidx(uid, cls="Function"):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def sub_i(uid):
    return fidx(uid, "SubVI")


def qnode(kind, src_cls, src_uid, src_name, diagram, loc):
    new = g.queue_node(kind, OP, src_cls, fidx(src_uid, src_cls), src_name, diagram, loc)
    must(f"queue {kind} from {src_name!r}", len(new) == 1, str(new))
    return new[0]


def wire_any(su, scls, st, du, dcls, dt, dsrc, ddst, branch=False, tag=""):
    """generic by-name wire with the step-B gates (same diagram: uid equality; across a border: tunnel topology
    with the array auto-index flip)."""
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    g.wire(OP, scls, fidx(su, scls), st, dcls, fidx(du, dcls), dt, branch=branch)
    a = term(walk(OP, dsrc)[su][2], st, True)["wire"]; b = term(walk(OP, ddst)[du][2], dt, False)["wire"]
    if dsrc == ddst:
        must(f"{tag}{st!r} -> {dt!r}", a and a == b, f"{a}/{b}")
        return
    new_idx = [o["i"] for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    new_t = [g.tunnels(OP, i) for i in new_idx]
    if len(new_t) == 1 and new_t[0]["index_mode"] == 1:
        g.set_index_mode(OP, new_idx[0], 0)
        new_t = [g.tunnels(OP, new_idx[0])]
        b = term(walk(OP, ddst)[du][2], dt, False)["wire"]
    t = new_t[0] if len(new_t) == 1 else {}
    ok = (bool(a) and bool(b) and len(new_t) == 1 and t.get("out_wire") == a and list(t.get("in_wires", [])) == [b]
          and t.get("out_is_source") is False and list(t.get("in_is_source", [])) == [True]
          and not t.get("out_conn_err") and not t.get("out_wire_err") and t.get("index_mode") == 0)
    must(f"{tag}{st!r} -> {dt!r} across the border", ok, f"a={a} b={b} {[(x.get('out_wire'), list(x.get('in_wires', [])), x.get('index_mode')) for x in new_t]}")


def indexed_in(label, du, dcls, dt, body, tag):
    """control -> node inside a loop through an AUTO-INDEXED tunnel (wire then flip; the row-40 D route)."""
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    g.wire_control(OP, [label], dcls, fidx(du, dcls), [dt])
    new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    must(f"{tag} one tunnel from {label!r}", len(new_t) == 1, str(len(new_t)))
    g.set_index_mode(OP, new_t[0]["i"], 1)
    t = g.tunnels(OP, new_t[0]["i"]); w = term(walk(OP, body)[du][2], dt, False)["wire"]
    must(f"{tag} IndexMode 1 and inner wire == {dt!r}", t["index_mode"] == 1 and w and w in list(t["in_wires"]), f"{t['in_wires']} vs {w}")
    return new_t[0]["i"]


def count_tunnel(label, du, dcls, dt, body, tag):
    """an auto-indexed input tunnel whose only job is to set N: made via indexed_in, then its inner wire deleted."""
    ti = indexed_in(label, du, dcls, dt, body, tag)
    w = term(walk(OP, body)[du][2], dt, False)["wire"]
    ws = [o["uid"] for o in g.report_all(OP, "Wire")]
    g.delete_object(OP, "Wire", ws.index(w), verify=False)
    t = g.tunnels(OP, ti)
    w_after = term(walk(OP, body)[du][2], dt, False)["wire"]        # …-guessed-timeout-name review: the named sink itself
    must(f"{tag} count tunnel: inner unwired, {dt!r} back to wire 0, still IndexMode 1",
         t["index_mode"] == 1 and not any(t["in_wires"]) and w_after == 0, f"{t['in_wires']} sink {w_after}")


def fresh_labview():
    """Run 1 (03:16): copy_by_index died with Errno 22 on the Move-example Target while LabVIEW still had that VI
    LOADED from the 00:3x StrToPath copy - the substitution protocol must never overwrite a loaded VI's file
    (peer ...-strtopath-fail4 / ...-queue-fail1-errno22). A copy_by_index session therefore starts on a FRESH
    instance (standing restart permission; nothing of value is unsaved at this point of the recipe)."""
    import subprocess
    subprocess.run(["powershell", "-NoProfile", "-Command",
                    "$p = Get-Process LabVIEW -ErrorAction SilentlyContinue; if ($p) { Stop-Process -Id $p.Id -Force; Start-Sleep -Seconds 8 }"],
                   capture_output=True, text=True, timeout=60)
    g.reset()          # the Application AND the op-proxy cache (stale proxies -> 0x800706BA)
    print("   fresh LabVIEW instance for the copy_by_index session", flush=True)


def build_pathtostr():
    if os.path.exists(P2S):
        print("P PathToStr.vi exists - reused", flush=True); return
    fresh_labview()
    shutil.copyfile(B.BASE, P2S); time.sleep(0.3)
    lab = {}

    def finish(dst):
        w = walk(dst, 0)
        u = next(u for u, v in w.items() if term(v[2], "path", False) and term(v[2], "string", True))
        n = w[u][0]
        b0 = {l for _i, l, ind in g.fp_labels(dst) if not ind}; g.create_control(dst, n, term(w[u][2], "path", False)["i"])
        lab["path"] = [l for _i, l, ind in g.fp_labels(dst) if not ind and l not in b0][-1]
        w = walk(dst, 0)
        b0 = {l for _i, l, ind in g.fp_labels(dst) if ind}; g.create_indicator(dst, n, term(w[u][2], "string", True)["i"])
        lab["string"] = [l for _i, l, ind in g.fp_labels(dst) if ind and l not in b0][-1]
    funcs = [o["uid"] for o in g.report(DONOR, "Function")]
    try:
        g.copy_by_index(DONOR, "Function", funcs.index(160), P2S, expect_uid=160, finish=finish)
    except Exception:
        if os.path.exists(P2S):
            os.remove(P2S)              # never leave a half-built sub-VI that a rerun would "reuse"
        raise
    g.open_panel(P2S); time.sleep(0.5)
    g.conpane_assign(P2S, lab["path"], 0); g.conpane_assign(P2S, lab["string"], 1)
    must("P PathToStr.vi runnable with pane", g.exec_state(P2S) == 1 and lab["path"] in str(g.conpane(P2S)))
    g.set_auto_error_handling(P2S, False); g.save(P2S); g.close_panel(P2S)


def build():
    print("\n== BUILD queue core", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(B.BASE, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(0.8)
    labels = {}
    print(f"H1 loader default -> {g.make_default(B.L_VI, {'file (use dialog)': B.CAL})} bytes", flush=True)
    uL = B.drop(OP, B.L_VI, 0, (100, 100)); uW = B.drop(OP, B.W_VI, 0, (300, 500))
    B.wire_sub(OP, uL, "cross size", uW, "cross length", 0, 0, tag="H2 ")
    # sample image + frame-0 reader + KT (type source and one-shot self-check)
    uCs = B.drop(OP, B.C_VI, 0, (100, 300)); uRs = B.drop(OP, B.R_VI, 0, (300, 300)); uKT = B.drop(OP, B.K_VI, 0, (700, 900))
    uP2S = B.drop(OP, P2S, 0, (100, 1300)); uS_dummy = None
    for (u, name, key) in ((uCs, "Image Name", "sample_name"), (uRs, "File Path", "sample_path")):
        wt = walk(OP, 0); n = wt[u][0]; t = term(wt[u][2], name, False)["i"]
        b0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}; g.create_control(OP, n, t)
        new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in b0]
        must(f"H2 control {name!r} on sample node", bool(new), str(new)); labels[key] = new[-1]
    B.wire_sub(OP, uCs, "New Image", uRs, "Image", 0, 0, tag="H2 ")
    B.wire_sub(OP, uRs, "Image Out", uKT, "Image In", 0, 0, tag="H2 ")
    B.wire_sub(OP, uL, "Array of cal clusters", uKT, "Array of cal clusters", 0, 0, tag="H2 ")
    B.wire_sub(OP, uL, "cross size", uKT, "cross size", 0, 0, branch=True, tag="H2 ")
    B.wire_sub(OP, uW, "Cosine bandpass for Hilbert", uKT, B.COS_HIL, 0, 0, tag="H2 ")
    B.wire_sub(OP, uW, B.COS_RS, uKT, B.COS_RS, 0, 0, tag="H2 ")
    wt = walk(OP, 0); nK = wt[uKT][0]
    for name in STATE + PARAMS:
        t = term(wt[uKT][2], name, False)["i"]
        b0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}; g.create_control(OP, nK, t)
        new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in b0]
        must(f"H3 control {name!r}", bool(new) and new[-1] == name, str(new)); labels[name] = new[-1]
    for k, name in enumerate(STATE_OUT):          # KT outputs -> indicators (self-check row 0)
        wt = walk(OP, 0); t = term(wt[uKT][2], name, True)["i"]
        b0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, wt[uKT][0], t)
        new = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in b0]
        must(f"H3 KT indicator {name!r}", bool(new), str(new)); labels["kt_" + OUT_KEYS[k]] = new[-1]
    fp = B.string_array_control(OP, "H4 frame paths"); labels["frame_paths"] = fp
    pn = B.string_array_control(OP, "H4 pool names"); labels["pool_names"] = pn
    must("H4 two distinct String[] controls", fp != pn, f"{fp!r} {pn!r}")
    es = g.exec_state(OP); must("H ExecState 1 with the head + KT wired (kernel inputs satisfied)", es == 1, str(es))
    # Q: seven Obtains
    Q = {}
    Q["free"] = qnode("obtain", "SubVI", uCs, "New Image", 0, (1300, 100)); Q["img"] = qnode("obtain", "SubVI", uCs, "New Image", 0, (1300, 200))
    Q["meta"] = qnode("obtain", "SubVI", uP2S, "string", 0, (1300, 300)); Q["rmeta"] = qnode("obtain", "SubVI", uP2S, "string", 0, (1300, 400))
    Q["res"] = qnode("obtain", "SubVI", uKT, "x,y,z array out", 0, (1300, 500)); Q["good"] = qnode("obtain", "SubVI", uKT, "Bead is good? array out", 0, (1300, 600))
    Q["pos"] = qnode("obtain", "SubVI", uKT, "pos in cal image out", 0, (1300, 700))
    # pool loop: create + enqueue into Q_free
    def new_loop(loc, tag):
        dia0 = {d["uid"] for d in g.report_all(OP, "Diagram")}; fl0 = {o["uid"] for o in g.report_all(OP, "ForLoop")}
        g.for_loop(OP, loc)
        bu = next(d["uid"] for d in g.report_all(OP, "Diagram") if d["uid"] not in dia0)
        lu = next(o["uid"] for o in g.report_all(OP, "ForLoop") if o["uid"] not in fl0)
        must(f"{tag} loop created", True, str(lu))
        return lu, (lambda: next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if d["uid"] == bu))
    _lp, bP = new_loop((100, 1600), "L pool")
    uCp = B.drop(OP, B.C_VI, bP(), (60, 60))
    indexed_in(pn, uCp, "SubVI", "Image Name", bP(), "L")
    eF = qnode("enqueue", "Function", Q["free"], "queue out", bP(), (400, 60))
    wire_any(uCp, "SubVI", "New Image", eF, "Function", "element", bP(), bP(), tag="L ")
    # ACQ loop
    _la, bA = new_loop((700, 100), "A ACQ")
    uS = B.drop(OP, B.S_VI, bA(), (60, 60)); uR = B.drop(OP, B.R_VI, bA(), (300, 60))
    indexed_in(fp, uS, "SubVI", "string", bA(), "A")
    dF = qnode("dequeue", "Function", Q["free"], "queue out", bA(), (60, 260))
    wire_any(dF, "Function", "element", uR, "SubVI", "Image", bA(), bA(), tag="A ")
    wire_any(dF, "Function", "error out", uR, "SubVI", "error in (no error)", bA(), bA(), tag="A ")
    B.wire_sub(OP, uS, "path", uR, "File Path", bA(), bA(), tag="A ")
    eI = qnode("enqueue", "Function", Q["img"], "queue out", bA(), (600, 60))
    wire_any(uR, "SubVI", "Image Out", eI, "Function", "element", bA(), bA(), tag="A ")
    wire_any(uR, "SubVI", "error out", eI, "Function", "error in (no error)", bA(), bA(), tag="A ")
    eM = qnode("enqueue", "Function", Q["meta"], "queue out", bA(), (600, 260))
    indexed_in(fp, eM, "Function", "element", bA(), "A meta")
    wire_any(eI, "Function", "error out", eM, "Function", "error in (no error)", bA(), bA(), tag="A chain ")
    # TRK loop
    _lt, bT = new_loop((700, 700), "T TRK")
    uK = B.drop(OP, B.K_VI, bT(), (400, 60))
    count_tunnel(fp, uK, "SubVI", "cross size", bT(), "T count")      # a throw-away sink; cross size is wired next
    dI = qnode("dequeue", "Function", Q["img"], "queue out", bT(), (60, 60))
    dM = qnode("dequeue", "Function", Q["meta"], "queue out", bT(), (60, 260))
    wire_any(dI, "Function", "element", uK, "SubVI", "Image In", bT(), bT(), tag="T ")
    wire_any(dI, "Function", "error out", dM, "Function", "error in (no error)", bT(), bT(), tag="T ")
    b = bT()
    B.wire_sub(OP, uL, "Array of cal clusters", uK, "Array of cal clusters", 0, b, branch=True, tag="T ")
    B.wire_sub(OP, uL, "cross size", uK, "cross size", 0, b, branch=True, tag="T ")
    B.wire_sub(OP, uW, "Cosine bandpass for Hilbert", uK, B.COS_HIL, 0, b, branch=True, tag="T ")
    B.wire_sub(OP, uW, B.COS_RS, uK, B.COS_RS, 0, b, branch=True, tag="T ")
    for name in PARAMS:
        g.wire_control(OP, [labels[name]], "SubVI", sub_i(uK), [name], branch=True)
        must(f"T control {name!r} -> kernel", bool(term(walk(OP, bT())[uK][2], name, False)["wire"]))
    lt_i = fidx(_lt, "ForLoop")
    reg_index = []
    for k in range(3):
        before_regs = set(g.loop_cast(OP, lt_i, "ForLoop")["shift_reg_uids"])
        uid = g.add_shift_reg(OP, lt_i, 150 + 60 * k, "ForLoop")
        regs = g.loop_cast(OP, lt_i, "ForLoop")["shift_reg_uids"]
        must(f"T register {k}: Shift Registers[] == before + {{uid}}", set(regs) == before_regs | {uid}, f"{regs}")
        reg_index.append(regs.index(uid))
    wb = walk(OP, bT()); nKb = wb[uK][0]
    pl = {l: i for i, l, ind in g.fp_labels(OP) if not ind}
    for k, name in enumerate(STATE):
        g.wire_sr("LeftOutCtl", OP, lt_i, reg_index[k], ctl_index=pl[labels[name]], class_name="ForLoop")
        g.wire_sr("LeftIn", OP, lt_i, reg_index[k], node_index=nKb, term_index=term(wb[uK][2], name, False)["i"], class_name="ForLoop")
        must(f"T reg {k} LeftIn -> kernel {name!r}", bool(term(walk(OP, bT())[uK][2], name, False)["wire"]))
    eR = qnode("enqueue", "Function", Q["res"], "queue out", bT(), (800, 60))
    eG = qnode("enqueue", "Function", Q["good"], "queue out", bT(), (800, 200))
    eP = qnode("enqueue", "Function", Q["pos"], "queue out", bT(), (800, 340))
    eRM = qnode("enqueue", "Function", Q["rmeta"], "queue out", bT(), (800, 480))
    eFr = qnode("enqueue", "Function", Q["free"], "queue out", bT(), (800, 620))
    wire_any(uK, "SubVI", "x,y,z array out", eR, "Function", "element", bT(), bT(), tag="T ")
    wire_any(uK, "SubVI", "Bead is good? array out", eG, "Function", "element", bT(), bT(), tag="T ")
    wire_any(uK, "SubVI", "pos in cal image out", eP, "Function", "element", bT(), bT(), tag="T ")
    wire_any(dM, "Function", "element", eRM, "Function", "element", bT(), bT(), tag="T ")
    wire_any(dI, "Function", "element", eFr, "Function", "element", bT(), bT(), branch=True, tag="T ")
    wire_any(dM, "Function", "error out", eR, "Function", "error in (no error)", bT(), bT(), tag="T chain ")
    wire_any(eR, "Function", "error out", eG, "Function", "error in (no error)", bT(), bT(), tag="T chain ")
    wire_any(eG, "Function", "error out", eP, "Function", "error in (no error)", bT(), bT(), tag="T chain ")
    wire_any(eP, "Function", "error out", eRM, "Function", "error in (no error)", bT(), bT(), tag="T chain ")
    wire_any(eRM, "Function", "error out", eFr, "Function", "error in (no error)", bT(), bT(), tag="T chain ")
    wb = walk(OP, bT())
    for k, name in enumerate(STATE_OUT):
        w_out = term(wb[uK][2], name, True)["wire"]
        g.wire_sr("RightIn", OP, lt_i, reg_index[k], node_index=nKb, term_index=term(wb[uK][2], name, True)["i"], class_name="ForLoop")
        must(f"T reg {k} RightIn <- kernel {name!r}", term(walk(OP, bT())[uK][2], name, True)["wire"] == w_out)
    # sink loop
    _ls, bS = new_loop((1300, 900), "S sink")
    sR = qnode("dequeue", "Function", Q["res"], "queue out", bS(), (60, 60))
    count_tunnel(fp, sR, "Function", "timeout in ms (-1)", bS(), "S count")   # exact name (test_opqueue.log); run 3 guessed 'timeout' -> 5001
    sG = qnode("dequeue", "Function", Q["good"], "queue out", bS(), (60, 200))
    sP = qnode("dequeue", "Function", Q["pos"], "queue out", bS(), (60, 340))
    sM = qnode("dequeue", "Function", Q["rmeta"], "queue out", bS(), (60, 480))
    wire_any(sR, "Function", "error out", sG, "Function", "error in (no error)", bS(), bS(), tag="S chain ")
    wire_any(sG, "Function", "error out", sP, "Function", "error in (no error)", bS(), bS(), tag="S chain ")
    wire_any(sP, "Function", "error out", sM, "Function", "error in (no error)", bS(), bS(), tag="S chain ")
    outs = {}
    for key, u in (("xyz", sR), ("good", sG), ("pos", sP), ("meta", sM)):
        tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
        g.exit_loop(OP, fidx(u), ["element"], bS(), node_class="Function")
        new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
        must(f"S output tunnel for {key}", len(new_t) == 1 and g.tunnels(OP, new_t[0]["i"])["index_mode"] == 1)
        b0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.tunnel_indicator(OP, new_t[0]["i"])
        new = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in b0]
        must(f"S indicator {key}", bool(new)); labels[key] = new[-1]
    # TEARDOWN (recipe review ...-stage2-queue-core-recipe.md §4/§6): a join of TRK completion AND sink completion
    # with no Merge Errors: a DRAIN loop (8 dequeues of Q_free) takes its queue refnum from TRK's last
    # Enqueue(Q_free).'queue out' exported through a last-value tunnel (=> after TRK) and its error in from the
    # sink's exported 'error out' (=> after the sink); Release(Q_free) takes ITS refnum from the drain's dequeue
    # 'queue out' (=> after the drain); the other six releases chain by error from that one.
    def export_last(loop_uid, node_uid, name, body_fn, tag):
        tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
        g.exit_loop(OP, fidx(node_uid), [name], body_fn(), node_class="Function")
        new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
        must(f"{tag} exported {name!r} through one tunnel", len(new_t) == 1)
        g.set_index_mode(OP, new_t[0]["i"], 0)
        must(f"{tag} last-value mode", g.tunnels(OP, new_t[0]["i"])["index_mode"] == 0)
    export_last(_lt, eFr, "queue out", bT, "T export")        # TRK's only 'queue out' export
    export_last(_ls, sM, "error out", bS, "S export")          # the sink's only 'error out' export
    _ld, bD = new_loop((1300, 1600), "D drain")
    dD = qnode("dequeue", "ForLoop", _lt, "queue out", bD(), (60, 60))      # refnum via TRK (after TRK)
    count_tunnel(pn, dD, "Function", "timeout in ms (-1)", bD(), "D count")          # N = 8 (Pool Names)
    g.wire(OP, "ForLoop", fidx(_ls, "ForLoop"), "error out", "Function", fidx(dD), "error in (no error)")
    must("D drain error in <- sink error out (after the sink)", bool(term(walk(OP, bD())[dD][2], "error in (no error)", False)["wire"]))
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    g.exit_loop(OP, fidx(dD), ["timed out?"], bD(), node_class="Function")
    new_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    must("D 'timed out?' indexed output", len(new_t) == 1 and g.tunnels(OP, new_t[0]["i"])["index_mode"] == 1)
    b0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.tunnel_indicator(OP, new_t[0]["i"])
    labels["drain"] = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in b0][-1]
    export_last(_ld, dD, "queue out", bD, "D export")
    prev = None
    for k, key in enumerate(["free", "img", "meta", "rmeta", "res", "good", "pos"]):
        if key == "free":
            rel = qnode("release", "ForLoop", _ld, "queue out", 0, (1900, 100))          # after the drain
        else:
            rel = qnode("release", "Function", Q[key], "queue out", 0, (1900, 100 + 120 * k))
            wire_any(prev, "Function", "error out", rel, "Function", "error in (no error)", 0, 0, tag="S rel ")
        prev = rel
    wt = walk(OP, 0); t = term(wt[prev][2], "error out", True)["i"]
    b0 = {l for _i, l, ind in g.fp_labels(OP) if ind}; g.create_indicator(OP, wt[prev][0], t)
    labels["release_error"] = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in b0][-1]
    es = g.exec_state(OP)
    must("O ExecState 1", es == 1, str(es))
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(LABELS_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   SAVED; labels {labels}", flush=True)
    return labels


def fixture_run(labels, ref, frames, tag):
    print(f"\n== T{tag} queue-core run: {len(frames)} frames", flush=True)
    first_loss = next((f for f in sorted(ref) if any(v == -1.0 for v in ref[f]["ff"])), None)
    ld = g.op(B.L_VI); ld.SetControlValue("file (use dialog)", B.CAL); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    vi = g.op(OP)
    paths = [os.path.join(B.DATA, f"img{f:05d}.tif") for f in frames]
    vi.SetControlValue(labels["sample_name"], "sample"); vi.SetControlValue(labels["sample_path"], paths[0])
    vi.SetControlValue(labels["pool_names"], [f"pool{k}" for k in range(8)])
    vi.SetControlValue(labels["x,y,z array"], xyz0); vi.SetControlValue(labels["Bead is good? array in"], [True] * nb)
    vi.SetControlValue(labels["pos in cal image in"], [0] * nb)
    vi.SetControlValue(labels["# of bead 4 packs"], nb // 4); vi.SetControlValue(labels["4 pack remainder"], nb % 4)
    vi.SetControlValue(labels["frame_paths"], paths)
    t0 = time.time()
    try:
        g._run(vi, 6.0, 600.0)
    except RuntimeError as e:
        if "did not return" in str(e):
            print(f"   T{tag} RUN TIMEOUT (a blocked queue = an intentional hang): {str(e)[:120]}", flush=True); os._exit(3)
        raise
    t_run = time.time() - t0
    out = {k: [list(r) for r in vi.GetControlValue(labels[k])] for k in ("xyz", "good", "pos")}
    meta = list(vi.GetControlValue(labels["meta"]))
    kt = {k: list(vi.GetControlValue(labels["kt_" + k])) for k in OUT_KEYS}
    print(f"   run {t_run:.1f} s ({t_run / max(1, len(frames)) * 1000:.1f} ms/frame); rows {[len(out[k]) for k in out]} meta {len(meta)}", flush=True)
    must(f"T{tag} one row per frame", all(len(out[k]) == len(frames) for k in out) and len(meta) == len(frames))
    must(f"T{tag} META[n] == Frame Paths[n] for every n", [str(m) for m in meta] == paths)
    r0 = ref[frames[0]]
    must(f"T{tag} KT one-shot (frame 0 on the sample image) == reference row 0 (xyz, good, pos)",
         kt["xyz"] == r0["ff"] and [bool(x) for x in kt["good"]] == [bool(x) for x in r0["good"]] and [int(x) for x in kt["pos"]] == [int(x) for x in r0["pos"]],
         f"{kt['xyz'][:3]} vs {r0['ff'][:3]}")
    drain = [bool(x) for x in vi.GetControlValue(labels["drain"])]
    must(f"T{tag} Q_free drained: 8 dequeues, none timed out (the pool came back whole)", len(drain) == 8 and not any(drain), str(drain))
    rel_err = vi.GetControlValue(labels["release_error"])
    must(f"T{tag} releases clean", not rel_err[0], str(rel_err))
    same = diff = 0; first_diff = None
    for i, f in enumerate(frames):
        r = ref[f]
        if first_loss is not None and f >= first_loss:
            continue
        exact = out["xyz"][i] == r["ff"] and [bool(x) for x in out["good"][i]] == [bool(x) for x in r["good"]] and [int(x) for x in out["pos"][i]] == [int(x) for x in r["pos"]]
        same += exact; diff += (not exact)
        if not exact and first_diff is None:
            first_diff = (f, out["xyz"][i][:3], r["ff"][:3])
    print(f"   pre-loss: identical {same}, different {diff}; first diff {first_diff}", flush=True)
    must(f"T{tag} XYZ/GOOD/POS bit-identical before the first lost bead", diff == 0 and same > 0)


def main():
    g._lv = None
    N = B.arg("n", 200)
    try:
        build_pathtostr()
        labels = build()
        if "--build-only" not in sys.argv:
            ref = B.load_reference(); order = sorted(ref)
            fixture_run(labels, ref, order[:1], "1"); fixture_run(labels, ref, order[:2], "2")
            fixture_run(labels, ref, order[:N], str(N))
            if "--full" in sys.argv:
                fixture_run(labels, ref, order, "full")
    except B.Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True)
    except Exception as e:
        print(f"\nOBSERVED EXC {str(e)[:300]}", flush=True); B.PASS.append(("exception", False))
    finally:
        for p in (OP, P2S):
            try:
                g.close_panel(p)
            except Exception:
                pass
    n_ok = sum(1 for _n, p in B.PASS if p)
    print(f"\nSUMMARY {n_ok}/{len(B.PASS)} PASS", flush=True)
    for nme, p in B.PASS:
        print(f"   {'PASS' if p else 'FAIL'} {nme}", flush=True)
    return 0 if B.PASS and n_ok == len(B.PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
