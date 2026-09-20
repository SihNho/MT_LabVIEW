r"""build_track_v6_core.py - Track_v6_CPU_core_v0.vi: the stage-2 REPLAY CORE (docs/stage2-assembly-step-b.md,
REVISED route + "Cycle-4 assembly notes") - a For loop over the fixture frames with PARALLEL_kernel_v3clean and the
three feedback registers, built entirely by script, then RUN on the fixture and diffed against the 2026-09-07
reference. Zero GUI. Hardened per archive/peer/2026-09-15-stage2-cycle4-replay-core-recipe.md:
every structural gate is FATAL (must()), all THREE kernel outputs are captured and compared, register indices are
resolved from Loop.Shift Registers[] by the UID add_shift_reg returned, and the tunnel route (wire then index) is
proven on a scratch FIRST.

   [head]  HARNESS_loadcal (cal002 baked) -> Array of cal clusters, cross size ; windows(cross size) ; IMAQ Create
   [For]   Frame Paths[i] (String[], auto-indexed) -> StrToPath -> IMAQ ReadFile -> kernel
           3 shift registers (LeftOutCtl <- controls FIRST; LeftIn -> kernel in; kernel out -> RightIn)
           kernel outs -> auto-indexed OUT tunnels -> XYZ / GOOD / POS (2-D)

PHASES (each gate fatal):
  D  SCRATCH DISCRIMINATOR for the tunnel route: EMPTY copy + String[] control + For loop + StrToPath inside;
     wire_control(ctl -> StrToPath.string) then set_index_mode(tunnel, 1). GATE: tunnels()['in_wires'][0] ==
     StrToPath.string wire uid, IndexMode 1, ExecState 1, and the scratch RUNS with ['a','b'] (2 iterations).
  H1 copy EMPTY_v0; make_default(loader, cal002)      H2 head nodes + L.cross size -> W.cross length
  H3 kernel controls from a TEMPORARY top-level kernel: create_control x5; snapshot their UIDs; delete the instance
     + RBW; GATE: same 5 UIDs present, terminals unwired, SubVI count -1, no other UID lost
  H4 Frame Paths String[] control (Get Controls trick)
  L1 for_loop (no tunnels)   L2 drop StrToPath / ReadFile / kernel inside   L3 the proven tunnel route (same gate as D)
  L4 remaining wires (uid both ends)        R  registers: index by UID from loop_cast; LeftOutCtl -> LeftIn per reg;
     exit_loop for the 3 outputs (3 indexed tunnels); RightIn per reg (branch); GATE per wire: kernel terminal wire
     uid == far-end wire uid where readable
  O  3 tunnel_indicators (XYZ, GOOD, POS) ; ExecState 1 -> SAVE
  T  fixture run (hard_timeout_s=600, phases timed): XYZ/GOOD/POS rows vs reference ff/good/pos, EXACT for every
     frame before the first lost bead; post-loss deviation reported. --n=200 for a first pass; --build-only.
  py tools/bgrun.py --max-min 45 --log tools/bench/build_track_v6_core.log -- py -u tools/recipes/build_track_v6_core.py [--n=200] [--build-only]
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

VIS = r"C:\Program Files\NI\LVAddons\nivisioncommon\1\vi.lib\vision"
BG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\background VIs"
DATA = r"G:\Data\SiHyeong\20260906 Kimlab - 50bp 16X WT 90Hz 1p2 Ramp_Newbatch\test"
CAL = os.path.join(DATA, "cal002")
REF = os.path.join(os.path.dirname(HERE), "bench", "fixture_compare_results.jsonl")
REF_SESSION = "2026-09-07 16:00:38"
BASE = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "Track_v6_CPU_core_v0.vi")
SCR = os.path.join(g.CLAUDEDEV, f"SCRATCH_tunnel_{os.getpid()}.vi")
L_VI = os.path.join(g.CLAUDEDEV, "HARNESS_loadcal.vi")
C_VI = os.path.join(VIS, "Basics.llb", "IMAQ Create")
R_VI = os.path.join(VIS, "Files.llb", "IMAQ ReadFile")
W_VI = os.path.join(BG, "make both cosine bandpass.vi")
K_VI = os.path.join(g.CLAUDEDEV, "PARALLEL_kernel_v3clean.vi")
S_VI = os.path.join(g.CLAUDEDEV, "StrToPath.vi")
GC = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting\Get Controls.vi"
COS_HIL = "Cosine bandpass\nfor Hilbert "
COS_RS = "Real-space cosine window"
STATE = ["x,y,z array", "Bead is good? array in", "pos in cal image in"]
STATE_OUT = ["x,y,z array out", "Bead is good? array out", "pos in cal image out"]
OUT_KEYS = ["xyz", "good", "pos"]
PARAMS = ["4 pack remainder", "# of bead 4 packs"]
LABELS_OUT = os.path.join(os.path.dirname(HERE), "bench", "track_v6_core_labels.json")
g._run.__defaults__ = (6.0, 120.0)
PASS = []


class Stop(Exception):
    pass


def arg(name, default):
    v = next((a.split("=", 1)[1] for a in sys.argv if a.startswith(f"--{name}=")), None)
    return type(default)(v) if v is not None else default


def must(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)
    if not ok:
        raise Stop(name)


def walk(target, diagram=0):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(80):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source):
    return next((r for r in rows if r["name"] == name and r["is_source"] == source), None)


def sub_i(target, uid):
    return [o["uid"] for o in g.report_all(target, "SubVI")].index(uid)


def drop(target, path, diagram, pos):
    before = g.uids(target, "SubVI")
    g.drop_subvi(target, path, diagram, pos)
    new = [u for u in g.uids(target, "SubVI") if u not in before]
    must(f"drop {os.path.basename(path)}", len(new) == 1, str(new))
    return new[0]


def wire_sub(target, su, st, du, dt, dsrc, ddst, branch=False, tag=""):
    """Wire by name and gate by wire uid. Same diagram: one Wire object, same uid on both ends. ACROSS a loop border
    (run 1, 00:5x: 'New Image' -> 'Image' read 531/506 and my equal-uid gate stopped the build): the connection is
    TWO Wire objects joined by a NEW non-indexed tunnel (INDEX row 36 T3 measured outer 530->514, inner 514->497),
    so the gate is: both ends non-zero AND a new LoopTunnel with outer wire == source uid, inner wire == sink uid,
    IndexMode 0."""
    tun0 = {o["uid"] for o in g.report_all(target, "LoopTunnel")}
    g.wire(target, "SubVI", sub_i(target, su), st, "SubVI", sub_i(target, du), dt, branch=branch)
    a = term(walk(target, dsrc)[su][2], st, True)["wire"]; b = term(walk(target, ddst)[du][2], dt, False)["wire"]
    if dsrc == ddst:
        must(f"{tag}{st!r} -> {dt!r}", a and a == b, f"{a}/{b}")
        return
    new_idx = [o["i"] for o in g.report_all(target, "LoopTunnel") if o["uid"] not in tun0]
    new_t = [g.tunnels(target, i) for i in new_idx]
    # Run 2 (01:0x): an ARRAY wired into the For loop arrived AUTO-INDEXED (LabVIEW's editor default, applied by the
    # library) - one element per frame into a whole-array kernel input = the computation change rule 1a forbids; the
    # IndexMode-0 gate caught it. Fix (reviewed, …-core-fail2-array-tunnel-autoindexed): flip the new tunnel to
    # non-indexed and re-read - the mirror of the L3 route proven in phase D.
    if len(new_t) == 1 and new_t[0]["index_mode"] == 1:
        g.set_index_mode(target, new_idx[0], 0)
        new_t = [g.tunnels(target, new_idx[0])]
        b = term(walk(target, ddst)[du][2], dt, False)["wire"]
        print(f"   {tag}{st!r}: tunnel flipped to IndexMode 0 -> {(new_t[0]['out_wire'], list(new_t[0]['in_wires']), new_t[0]['index_mode'])}, sink wire now {b}", flush=True)
    # peer (…-core-fail1-border-wire-gate): exactly ONE new tunnel, continuous a -> tunnel -> b, input direction
    # (outer sink, inner source), clean error fields, IndexMode 0 (whole value every iteration)
    t = new_t[0] if len(new_t) == 1 else {}
    ok = (bool(a) and bool(b) and len(new_t) == 1 and t.get("out_wire") == a and list(t.get("in_wires", [])) == [b]
          and t.get("out_is_source") is False and list(t.get("in_is_source", [])) == [True]
          and not t.get("out_conn_err") and not t.get("out_wire_err") and t.get("index_mode") == 0)
    must(f"{tag}{st!r} -> {dt!r} across the border (one new non-indexed tunnel {a}->{b})", ok,
         f"a={a} b={b} new tunnels {[(x.get('out_wire'), list(x.get('in_wires', [])), x.get('index_mode'), x.get('out_is_source'), list(x.get('in_is_source', [])), x.get('out_conn_err'), x.get('out_wire_err')) for x in new_t]}")


def string_array_control(target, tag):
    u_gc = drop(target, GC, 0, (200, 700))
    wt = walk(target, 0); n = wt[u_gc][0]; t = term(wt[u_gc][2], "Control Names", False)["i"]
    before = {l for _i, l, ind in g.fp_labels(target) if not ind}
    g.create_control(target, n, t)
    label = [l for _i, l, ind in g.fp_labels(target) if not ind and l not in before][-1]
    pw = {r["label"]: r for r in g.panel_wiring(target)}
    ws = [o["uid"] for o in g.report_all(target, "Wire")]
    g.delete_object(target, "Wire", ws.index(pw[label]["wire"]), verify=False)
    g.delete_object(target, "SubVI", sub_i(target, u_gc), verify=False); g.remove_bad_wires_scripted(target)
    pw = {r["label"]: r for r in g.panel_wiring(target)}
    must(f"{tag} free String[] control", pw[label]["wire"] == 0, f"{label!r}")
    return label


def tunnel_route(target, fp_label, u_stp, body, tag):
    """wire_control(ctl -> StrToPath.string) creates a non-indexed tunnel; set_index_mode(1) must heal the wire.
    GATE (reviewer): the tunnel's inner wire uid == StrToPath.string's wire uid, IndexMode 1."""
    tun0 = {o["uid"] for o in g.report_all(target, "LoopTunnel")}
    g.wire_control(target, [fp_label], "SubVI", sub_i(target, u_stp), ["string"])
    new_t = [o for o in g.report_all(target, "LoopTunnel") if o["uid"] not in tun0]
    must(f"{tag} exactly one tunnel from wire_control", len(new_t) == 1, str(len(new_t)))
    g.set_index_mode(target, new_t[0]["i"], 1)
    t = g.tunnels(target, new_t[0]["i"])
    w_str = term(walk(target, body)[u_stp][2], "string", False)["wire"]
    print(f"   {tag} tunnel: mode {t['index_mode']} outer {t['out_wire']} inner {t['in_wires']}; StrToPath.string {w_str}", flush=True)
    must(f"{tag} IndexMode 1 and inner wire == StrToPath.string wire", t["index_mode"] == 1 and w_str and w_str in list(t["in_wires"]), "")
    return new_t[0]["i"]


def discriminator():
    print("\n== D scratch discriminator: tunnel wire-then-index route", flush=True)
    shutil.copyfile(BASE, SCR); time.sleep(0.3)
    try:
        g.open_panel(SCR); time.sleep(0.8)
        fp = string_array_control(SCR, "D")
        dia0 = {d["uid"] for d in g.report_all(SCR, "Diagram")}
        g.for_loop(SCR, (500, 200))
        body_uid = next(d["uid"] for d in g.report_all(SCR, "Diagram") if d["uid"] not in dia0)
        body = next(i for i, d in enumerate(g.report_all(SCR, "Diagram")) if d["uid"] == body_uid)
        u_stp = drop(SCR, S_VI, body, (60, 60))
        tunnel_route(SCR, fp, u_stp, body, "D")
        es = g.exec_state(SCR); must("D ExecState 1 after the route", es == 1, str(es))
        vi = g.op(SCR); vi.SetControlValue(fp, ["a", "b"]); t0 = time.time(); g._run(vi)
        must("D the scratch runs and returns with a two-element input", True, f"{time.time() - t0:.2f} s")
    finally:
        try:
            g.close_panel(SCR)
        except Exception:
            pass
        if os.path.exists(SCR):
            os.remove(SCR)


def build():
    print("\n== BUILD", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(BASE, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(0.8)
    print(f"H1 loader default -> {g.make_default(L_VI, {'file (use dialog)': CAL})} bytes", flush=True)
    uL = drop(OP, L_VI, 0, (100, 100)); uC = drop(OP, C_VI, 0, (100, 300)); uW = drop(OP, W_VI, 0, (300, 500))
    wire_sub(OP, uL, "cross size", uW, "cross length", 0, 0, tag="H2 ")
    labels = {}; ctl_uids = {}
    # Run 4 (01:2x) assembled 57/58 but ExecState 0: IMAQ Create's 'Image Name' is a REQUIRED input that was never
    # wired (HARNESS_compare had this control; review ...-core-fail4-assembled-but-broken ranked it first).
    wt = walk(OP, 0); nC = wt[uC][0]; tI = term(wt[uC][2], "Image Name", False)["i"]
    before = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    g.create_control(OP, nC, tI)
    new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before]
    must("H2 control 'Image Name' on IMAQ Create", bool(new) and new[-1] == "Image Name", str(new))
    labels["image_name"] = new[-1]
    # H3
    base_uids = g.uids(OP, "GObject")                 # v2 review: the exact object-set gate after the temp kernel goes
    uKt = drop(OP, K_VI, 0, (700, 900))
    wt = walk(OP, 0); nK = wt[uKt][0]
    for name in STATE + PARAMS:
        t = term(wt[uKt][2], name, False)["i"]
        before = {l for _i, l, ind in g.fp_labels(OP) if not ind}
        g.create_control(OP, nK, t)
        new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before]
        must(f"H3 control {name!r}", bool(new) and new[-1] == name, str(new))
        labels[name] = new[-1]
        ctl_uids[name] = {r["label"]: r["uid"] for r in g.panel_wiring(OP)}[name]
    sub0 = len(g.report_all(OP, "SubVI"))
    g.delete_object(OP, "SubVI", sub_i(OP, uKt), verify=False); g.remove_bad_wires_scripted(OP)
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    must("H3 the 5 controls survive by UID, terminals unwired", all(pw[n]["uid"] == ctl_uids[n] and pw[n]["wire"] == 0 for n in STATE + PARAMS))
    must("H3 SubVI count -1", len(g.report_all(OP, "SubVI")) == sub0 - 1)
    after = g.uids(OP, "GObject"); extra = after - base_uids; missing = base_uids - after
    # the five controls each bring their own owned objects (control, label, terminal...): require nothing of the
    # base set lost, and every extra object to be OWNED by one of the five controls (panel_wiring lists control uids
    # only, so the weaker but checkable form is: no base uid missing, and no SubVI/Wire left from the temp kernel)
    must("H3 no pre-existing object lost", not missing, str(missing))
    print(f"   H3 extra objects (the five controls and their parts): {len(extra)}", flush=True)
    fp_label = string_array_control(OP, "H4"); labels["frame_paths"] = fp_label
    # L1
    dia0 = {d["uid"] for d in g.report_all(OP, "Diagram")}
    g.for_loop(OP, (700, 100))
    body_uid = next(d["uid"] for d in g.report_all(OP, "Diagram") if d["uid"] not in dia0)
    body = lambda: next(i for i, d in enumerate(g.report_all(OP, "Diagram")) if d["uid"] == body_uid)
    must("L1 one For loop", len(g.report_all(OP, "ForLoop")) == 1)
    uS = drop(OP, S_VI, body(), (60, 60)); uR = drop(OP, R_VI, body(), (300, 60)); uK = drop(OP, K_VI, body(), (600, 60))
    tunnel_route(OP, fp_label, uS, body(), "L3")
    b = body()
    wire_sub(OP, uC, "New Image", uR, "Image", 0, b, tag="L4 ")
    wire_sub(OP, uS, "path", uR, "File Path", b, b, tag="L4 ")
    wire_sub(OP, uR, "Image Out", uK, "Image In", b, b, tag="L4 ")
    wire_sub(OP, uL, "Array of cal clusters", uK, "Array of cal clusters", 0, b, tag="L4 ")
    wire_sub(OP, uL, "cross size", uK, "cross size", 0, b, branch=True, tag="L4 ")
    wire_sub(OP, uW, "Cosine bandpass for Hilbert", uK, COS_HIL, 0, b, tag="L4 ")
    wire_sub(OP, uW, COS_RS, uK, COS_RS, 0, b, tag="L4 ")
    for name in PARAMS:
        g.wire_control(OP, [labels[name]], "SubVI", sub_i(OP, uK), [name])
        must(f"L4 control {name!r} -> kernel", bool(term(walk(OP, body())[uK][2], name, False)["wire"]))
    # R registers, index by UID
    reg_index = []
    for k in range(3):
        before_regs = set(g.loop_cast(OP, 0, "ForLoop")["shift_reg_uids"])
        uid = g.add_shift_reg(OP, 0, 150 + 60 * k, "ForLoop")
        regs = g.loop_cast(OP, 0, "ForLoop")["shift_reg_uids"]
        # …-core-fail3 review: the set must grow by exactly this uid (membership alone tolerates a stale uid)
        must(f"R register {k}: Shift Registers[] == before + {{uid}}", set(regs) == before_regs | {uid}, f"{sorted(before_regs)} -> {regs} (+{uid})")
        reg_index.append(regs.index(uid))
    print(f"   R register indices by UID: {reg_index}", flush=True)
    wb = walk(OP, body()); nKb = wb[uK][0]
    pl = {l: i for i, l, ind in g.fp_labels(OP) if not ind}
    for k, name in enumerate(STATE):
        g.wire_sr("LeftOutCtl", OP, 0, reg_index[k], ctl_index=pl[labels[name]], class_name="ForLoop")
        pw = {r["label"]: r for r in g.panel_wiring(OP)}
        must(f"R reg {k} LeftOutCtl <- {name!r} (control terminal wired)", pw[labels[name]]["wire"] != 0)
        g.wire_sr("LeftIn", OP, 0, reg_index[k], node_index=nKb, term_index=term(wb[uK][2], name, False)["i"], class_name="ForLoop")
        must(f"R reg {k} LeftIn -> kernel {name!r}", bool(term(walk(OP, body())[uK][2], name, False)["wire"]))
    tun0 = {o["uid"] for o in g.report_all(OP, "LoopTunnel")}
    g.exit_loop(OP, sub_i(OP, uK), STATE_OUT, body(), node_class="SubVI")
    out_t = [o for o in g.report_all(OP, "LoopTunnel") if o["uid"] not in tun0]
    must("R three output tunnels", len(out_t) == 3, str(len(out_t)))
    wb = walk(OP, body())
    tinfo = {o["uid"]: g.tunnels(OP, o["i"]) for o in out_t}
    paired = {}
    for k, name in enumerate(STATE_OUT):
        w_out = term(wb[uK][2], name, True)["wire"]
        hits = [u for u, t in tinfo.items() if w_out in list(t["in_wires"])]
        must(f"R output {name!r} pairs with exactly ONE new tunnel, IndexMode 1", len(hits) == 1 and tinfo[hits[0]]["index_mode"] == 1, f"{hits}")
        paired[name] = hits[0]
    must("R the three paired tunnels are distinct", len(set(paired.values())) == 3, str(paired))
    for k, name in enumerate(STATE_OUT):
        w_out = term(wb[uK][2], name, True)["wire"]
        g.wire_sr("RightIn", OP, 0, reg_index[k], node_index=nKb, term_index=term(wb[uK][2], name, True)["i"], class_name="ForLoop")
        must(f"R reg {k} RightIn <- kernel {name!r} (still one wire uid)", term(walk(OP, body())[uK][2], name, True)["wire"] == w_out)
    # O indicators
    for k, name in enumerate(STATE_OUT):
        w_out = term(walk(OP, body())[uK][2], name, True)["wire"]
        tun = next(o for o in out_t if w_out in list(g.tunnels(OP, o["i"])["in_wires"]))
        before = {l for _i, l, ind in g.fp_labels(OP) if ind}
        g.tunnel_indicator(OP, tun["i"])
        new = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in before]
        must(f"O indicator for {name!r}", bool(new), str(new)); labels[OUT_KEYS[k]] = new[-1]
    es = g.exec_state(OP)
    if es != 1:
        # Run 4 (01:2x): fully assembled, 57/58, ExecState 0 with no gate localising it. LOCALISER (diagnostic, not a
        # repair - nothing is saved): map every wire uid to the terminals holding it, then Remove Bad Wires and
        # report the wires that disappear: each is broken (or incomplete) - that names the culprit terminals.
        holders = {}
        dias = list(range(len(g.report_all(OP, "Diagram"))))
        for d in dias:
            for u, (n, lab, rows) in walk(OP, d).items():
                for r in rows:
                    if r["wire"]:
                        holders.setdefault(r["wire"], []).append((d, lab, r["name"], "S" if r["is_source"] else "s"))
        for r in g.panel_wiring(OP):
            if r["wire"]:
                holders.setdefault(r["wire"], []).append(("panel", r["label"], "terminal", "S" if r["is_source"] else "s"))
        for o in g.report_all(OP, "LoopTunnel"):
            t = g.tunnels(OP, o["i"])
            if t["out_wire"]:
                holders.setdefault(t["out_wire"], []).append(("tunnel", t["uid"], "outer", t["index_mode"]))
            for wi in t["in_wires"]:
                if wi:
                    holders.setdefault(wi, []).append(("tunnel", t["uid"], "inner", t["index_mode"]))
        before_w = g.uids(OP, "Wire")
        g.remove_bad_wires_scripted(OP)
        gone = sorted(before_w - g.uids(OP, "Wire"))
        print(f"   LOCALISER: Remove Bad Wires removed {len(gone)} wire(s); ExecState now {g.exec_state(OP)}", flush=True)
        for wi in gone:
            print(f"      broken wire {wi}: {holders.get(wi, '(no holder census)')}", flush=True)
    must("O ExecState 1", es == 1, str(es))
    g.set_auto_error_handling(OP, False); g.save(OP)
    with open(LABELS_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   SAVED; labels {labels}", flush=True)
    return labels


def load_reference():
    s = None; ref = {}
    for line in open(REF, encoding="utf-8"):
        d = json.loads(line)
        if "session" in d:
            s = d["session"]
        elif s == REF_SESSION:
            ref[d["frame"]] = d
    must("T reference session loaded", len(ref) > 0, REF_SESSION)
    return ref


def fixture_run(labels, ref, frames, tag):
    """ONE COM run over `frames`; XYZ/GOOD/POS rows compared EXACTLY with the reference (pre-loss frames)."""
    print(f"\n== T{tag} fixture run: {len(frames)} frames", flush=True)
    first_loss = next((f for f in sorted(ref) if any(v == -1.0 for v in ref[f]["ff"])), None)
    ld = g.op(L_VI); ld.SetControlValue("file (use dialog)", CAL); g._run(ld)
    nb = int(ld.GetControlValue("# of beads")); xyz0 = list(ld.GetControlValue("x,y,(blankz) array"))
    vi = g.op(OP)
    vi.SetControlValue(labels["image_name"], "track_v6_core")
    vi.SetControlValue(labels["x,y,z array"], xyz0)
    vi.SetControlValue(labels["Bead is good? array in"], [True] * nb)
    vi.SetControlValue(labels["pos in cal image in"], [0] * nb)
    vi.SetControlValue(labels["# of bead 4 packs"], nb // 4); vi.SetControlValue(labels["4 pack remainder"], nb % 4)
    t0 = time.time(); vi.SetControlValue(labels["frame_paths"], [os.path.join(DATA, f"img{f:05d}.tif") for f in frames])
    t_set = time.time() - t0
    t0 = time.time()
    try:
        g._run(vi, 6.0, 600.0)
    except RuntimeError as e:
        if "did not return" in str(e):
            # v2 review: after a Run timeout the COM worker is still alive - no further COM call, exit at once
            print(f"   T{tag} RUN TIMEOUT: {str(e)[:160]} - exiting without COM cleanup", flush=True)
            os._exit(3)
        raise
    t_run = time.time() - t0
    t0 = time.time()
    out = {k: [list(r) for r in vi.GetControlValue(labels[k])] for k in OUT_KEYS}
    print(f"   set {t_set:.2f} s; run {t_run:.1f} s ({t_run / max(1, len(frames)) * 1000:.1f} ms/frame); get {time.time() - t0:.2f} s; rows {[len(out[k]) for k in OUT_KEYS]}", flush=True)
    must(f"T{tag} one row per frame for XYZ/GOOD/POS", all(len(out[k]) == len(frames) for k in OUT_KEYS))
    r0 = ref[frames[0]]
    must(f"T{tag} row widths match the reference", len(out["xyz"][0]) == len(r0["ff"]) and len(out["good"][0]) == len(r0["good"]) and len(out["pos"][0]) == len(r0["pos"]),
         f"{len(out['xyz'][0])}/{len(r0['ff'])} {len(out['good'][0])}/{len(r0['good'])} {len(out['pos'][0])}/{len(r0['pos'])}")
    same = diff = 0; first_diff = None; worst = 0.0; worst_f = None
    for i, f in enumerate(frames):
        r = ref[f]
        exact = out["xyz"][i] == r["ff"] and [bool(x) for x in out["good"][i]] == [bool(x) for x in r["good"]] and [int(x) for x in out["pos"][i]] == [int(x) for x in r["pos"]]
        if first_loss is not None and f >= first_loss:
            d = max(abs(a - b) for a, b in zip(out["xyz"][i], r["ff"]))
            if d > worst:
                worst, worst_f = d, f
            continue
        if exact:
            same += 1
        else:
            diff += 1
            if first_diff is None:
                first_diff = (f, out["xyz"][i][:3], r["ff"][:3], out["good"][i], r["good"], out["pos"][i], r["pos"])
    print(f"   pre-loss frames: identical {same}, different {diff}; first difference {first_diff}; post-loss worst |dxyz| {worst} at {worst_f}", flush=True)
    must(f"T{tag} XYZ/GOOD/POS bit-identical to the reference before the first lost bead", diff == 0 and same > 0)


def main():
    g._lv = None
    N = arg("n", 200)
    timed_out = False
    try:
        discriminator()
        labels = build()
        if "--build-only" not in sys.argv:
            ref = load_reference(); order = sorted(ref)
            # v2 review gate sequence: 1 frame (initialisers) -> 2 frames (RightIn feedback) -> N -> --full
            fixture_run(labels, ref, order[:1], "1")
            fixture_run(labels, ref, order[:2], "2")
            fixture_run(labels, ref, order[:N], str(N))
            if "--full" in sys.argv:
                fixture_run(labels, ref, order, "full")
    except Stop as e:
        print(f"\nSTOP at gate: {e}", flush=True)
    except Exception as e:
        print(f"\nOBSERVED EXC {str(e)[:300]}", flush=True); PASS.append(("exception", False))
    finally:
        for p in (OP, SCR):
            try:
                g.close_panel(p)
            except Exception:
                pass
    n_ok = sum(1 for _n, p in PASS if p)
    print(f"\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for nme, p in PASS:
        print(f"   {'PASS' if p else 'FAIL'} {nme}", flush=True)
    return 0 if PASS and n_ok == len(PASS) else 1


if __name__ == "__main__":
    sys.exit(main())
