"""build_opwiresr_v0.py - the four OpWireSR_*_v0 ops (docs/stage2-assembly-step-a3.md) + their functional test.

A register from add_shift_reg (row 37) has three UNWIRED terminals. Each op wires ONE of them with
Terminal.Connect Wire 6349C03 (invoked on the SINK, 'Wire Source' = the source), reaching every terminal through a
TYPED chain and no cast. Donor for all four: OpWhileCast_v0 (holds the WhileLoop-typed reference at the TMSC's
'specific class reference', a Loop[Shift Registers[]] node, and an Open VI Reference).

Register chain (added to every op)           TMSC -> (existing) Loop[ShiftRegs[]] --branch--> IA_r(index reg)
   -> PN_LR RightShiftRegister[Left Registers[]] -> IA_l(0) -> PN_LO Tunnel[Outer Term] -> PN_LI Tunnel[InsideTerms[]]
   -> IA_li(0)   (left INSIDE);  IA_r.element --branch--> PN_RI Tunnel[InsideTerms[]] -> IA_ri(0)  (right INSIDE)
Body-node chain (LeftIn, RightIn)            TMSC --branch--> PN_D Loop[Diagram] -> PN_N AbstractDiagram[Nodes[]]
   -> IA_n(index node) -> PN_T Node[Terms[]] -> IA_t(index term)
Top-level-node chain (LeftOutNode)           Open VI Reference.'vi reference' --branch--> PN_BD VI[Block Diagram]
   -> Nodes[] -> IA_n -> Terms[] -> IA_t
Control chain (LeftOutCtl)                   'vi reference' --branch--> PN_FP VI[Front Panel] -> Panel[Controls[]]
   -> IA_c(index ctl) -> Control[Terminal]

  op                    reference (sink)        Wire Source
  OpWireSR_LeftIn_v0    IA_t (body node term)   IA_li (left inside)
  OpWireSR_RightIn_v0   IA_ri (right inside)    IA_t (body node term)
  OpWireSR_LeftOutNode  PN_LO (left outside)    IA_t (top-level node term)
  OpWireSR_LeftOutCtl   PN_LO (left outside)    PN_CT (control terminal)

PREDICTION CONTRACT (stop at the first miss, nothing saved on a miss):
  B0  the very first op gates Loop.Diagram 6361401 (listed from the Wiki, UNVERIFIED): PN created, its data
      terminal named 'Diagram', ExecState 1 after wiring the seed into it.
  Bn  every op: ExecState 1 with all chains wired and the invoke's reference + Wire Source wired; saved; labels json.
  T   FUNCTIONAL on a scratch (HARNESS_copyloop + stop control + While loop + IMAQ Copy in the body + one register):
      LeftOutNode: top-level IMAQ Create.'New Image' -> left OUTSIDE; LeftIn: left INSIDE -> body IMAQ Copy.'Image Dst';
      RightIn: 'Image Dst Out' -> right INSIDE. Predict: each register terminal's wire uid == the far end's;
      ExecState 0 -> 1; the VI RUNS and returns with stop TRUE. Then LeftOutCtl on a SECOND register from the
      string control 'Image Name': predict the wire EXISTS and ExecState drops to 0 (type mismatch = broken wire);
      Remove Bad Wires restores 1.
Scratch deleted on every exit path; donor md5 checked.
  py tools/bgrun.py --max-min 30 --log tools/bench/build_opwiresr_v0.log -- py -u tools/recipes/build_opwiresr_v0.py
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import gscript as g  # noqa: E402

# SR_SEED=For (step B revised route, 2026-09-14 23:5x): the same four ops on the ForLoop-typed seed (OpLoopCast_v1
# donor) -> OpWireSRF_*_v0, tested on HARNESS_copyloop's EXISTING For loop (the WhileLoop seed errors 1055 on a
# ForLoop reference; the register READERS are WhileLoop-seeded too, so the For test verifies from the node side).
SEED = os.environ.get("SR_SEED", "While")
FOR = SEED == "For"
CLS = "ForLoop" if FOR else "WhileLoop"
OPFAM = "OpWireSRF" if FOR else "OpWireSR"
SRC = os.path.join(g.CLAUDEDEV, "OpLoopCast_v1.vi" if FOR else "OpWhileCast_v0.vi")
MAP_OUT = os.path.join(os.path.dirname(HERE), "bench", "opwiresrF_labels.json" if FOR else "opwiresr_labels.json")
ADDSR_MAP = os.path.join(os.path.dirname(HERE), "bench", "opaddshiftregF_labels.json" if FOR else "opaddshiftreg_labels.json")
SCRATCH_SRC = os.path.join(g.CLAUDEDEV, "HARNESS_copyloop.vi")
S = os.path.join(g.CLAUDEDEV, f"SCRATCH_wiresr_{os.getpid()}.vi")
# NOT Basics.llb: 'IMAQ Copy' lives in Management.llb (error 7 otherwise - recorded in an earlier recipe header and
# re-learned 23:13 as an untitled modal from OpSubVI_v1's auto error handling, tools/bench/test_opwiresr.log)
# ...and Management.llb is under the nivision\1 package, not nivisioncommon\1 (peer scan of the installed files,
# archive/peer/2026-09-14-wiresr-test-fail2-imaqcopy-llb-path.md)
COPY_VI = r"C:\Program Files\NI\LVAddons\nivision\1\vi.lib\vision\Management.llb\IMAQ Copy"
STOP = "Shift Registers?"
P_SR, P_LEFTREGS, P_OUTER, P_INSIDE = "6361402", "6357800", "6356001", "6356000"
P_DIAGRAM, P_NODES, P_TERMS = "6361401", "6375809", "6359000"
P_BD, P_FP, P_CTLS, P_CTLTERM, M_CONNECT = "23C", "23D", "6348801", "6332006", "6349C03"
GENERIC = {"reference", "reference out", "error in (no error)", "error in", "error out"}
VARIANTS = ["LeftIn", "RightIn", "LeftOutNode", "LeftOutCtl"]
g._run.__defaults__ = (6.0, 120.0)
STEPS, PASS = [], []
OP = None


def step(name, predict, fn):
    print(f"\n== {name}\n   predict: {predict}", flush=True)
    t0 = time.time()
    try:
        r = fn()
        print(f"   result : {r}  ({time.time() - t0:.1f} s)", flush=True)
        STEPS.append((name, "ok"))
        return r
    except Exception as e:
        print(f"   OBSERVED: EXC {str(e)[:300]}", flush=True)
        STEPS.append((name, "exc"))
        return None


def check(name, ok, detail=""):
    PASS.append((name, bool(ok)))
    print(f"   {'PASS' if ok else 'FAIL'} {name} {detail}", flush=True)


def walk(target, diagram=0, limit=100):
    labels = {r["uid"]: r["label"] for r in g.node_labels(target, diagram)}
    out = {}
    for n in range(limit):
        u, rows = g.node_terms_uid(target, diagram, n)
        if not u:
            break
        out[u] = (n, labels.get(u), rows)
    return out


def term(rows, name, source=None):
    for r in rows:
        if r["name"] == name and (source is None or r["is_source"] == source):
            return r
    return None


def snap(tag=""):
    return (f"{tag} Property={len(g.report_all(OP, 'Property'))} IndexArray={len(g.report_all(OP, 'IndexArray'))} "
            f"Invoke={len(g.report_all(OP, 'Invoke'))} Wire={len(g.report_all(OP, 'Wire'))} ExecState={g.exec_state(OP)}")


def idx(cls, uid):
    return [o["uid"] for o in g.report_all(OP, cls)].index(uid)


def cls_of(uid, w):
    lab = w[uid][1] or ""
    if lab == "Property Node":
        return "Property"
    if lab == "Index Array":
        return "IndexArray"
    if lab == "Invoke Node":
        return "Invoke"
    return "SubVI" if lab.endswith(".vi") else "Function"


def pn(cls, pid, pos):
    r = g.build_property(OP, cls, [(pid, False)], pos)
    return r[-1]["uid"] if r else None


def ia(pos):
    r = g.build_index_array(OP, pos)
    return r[-1]["uid"] if r else None


def wire_uid(uid, name, source, w=None):
    w = w or walk(OP, 0)
    r = term(w[uid][2], name, source)
    return r["wire"] if r else None


def data_name(uid, w=None):
    """A property node's data terminal = index 4 (v1 recipe)."""
    w = w or walk(OP, 0)
    return next(r["name"] for r in w[uid][2] if r["i"] == 4)


def connect(src_uid, src_name, dst_uid, dst_name, branch=False, tag=""):
    """wire by name, verified by the SAME wire uid on both ends (row 37: never by count, never by ExecState)."""
    w = walk(OP, 0)
    g.wire(OP, cls_of(src_uid, w), idx(cls_of(src_uid, w), src_uid), src_name,
           cls_of(dst_uid, w), idx(cls_of(dst_uid, w), dst_uid), dst_name, branch=branch)
    w = walk(OP, 0)
    a = wire_uid(src_uid, src_name, True, w); b = wire_uid(dst_uid, dst_name, False, w)
    ok = bool(a) and a == b
    print(f"   {tag}{src_name!r} -> {dst_name!r}: wire {a} / {b} {'OK' if ok else 'MISMATCH'}", flush=True)
    if not ok:
        raise RuntimeError(f"wire {src_name!r}->{dst_name!r} not on both ends ({a} vs {b})")
    return a


def make_ctl(uid, name, label_key, labels):
    w = walk(OP, 0)
    n, rows = w[uid][0], w[uid][2]
    t = term(rows, name, False)["i"]
    before = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    g.create_control(OP, n, t)
    new = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before]
    print(f"   control on {name!r} -> {new}", flush=True)
    labels[label_key] = new[-1]


def make_ind(uid, name, label_key, labels):
    w = walk(OP, 0)
    n, rows = w[uid][0], w[uid][2]
    t = term(rows, name, True)["i"]
    before = {l for _i, l, ind in g.fp_labels(OP) if ind}
    g.create_indicator(OP, n, t)
    new = [l for _i, l, ind in g.fp_labels(OP) if ind and l not in before]
    print(f"   indicator on {name!r} -> {new}", flush=True)
    labels[label_key] = new[-1]


def build(variant):
    global OP
    OP = os.path.join(g.CLAUDEDEV, f"{OPFAM}_{variant}_v0.vi")
    print(f"\n######## BUILD {os.path.basename(OP)}  (seed {CLS})", flush=True)
    if os.path.exists(OP):
        os.remove(OP)                    # never reference the output over COM before writing it (NAMES.md trap)
    shutil.copyfile(SRC, OP); time.sleep(0.3); g.open_panel(OP); time.sleep(1.0)
    print(snap("start:"), flush=True)
    if g.exec_state(OP) != 1:
        print("STOP: donor copy not runnable.", flush=True); return None
    w = walk(OP, 0)
    tmsc = next(u for u, v in w.items() if term(v[2], "specific class reference"))
    ovr = next(u for u, v in w.items() if term(v[2], "vi reference", True))
    sr_pn = next((u for u, v in w.items() if v[1] == "Property Node" and "ShiftRegs" in data_name(u, w)), None)
    print(f"   TMSC {tmsc}, Open VI Reference {ovr}, Loop[ShiftRegs[]] PN {sr_pn}", flush=True)
    if sr_pn is None:
        print("STOP: Loop[Shift Registers[]] node not found in donor.", flush=True); return None
    labels = {}
    y = 1500
    # ---- register chain
    ia_r = step("R1 IA_r on ShiftRegs[] (branch)", "same wire both ends", lambda: (ia((300, y)), None)[0])
    connect(sr_pn, data_name(sr_pn), ia_r, "array", branch=True, tag="R1 ")
    make_ctl(ia_r, "index", "index_reg", labels)
    lr = step("R2 PN_LR RightShiftRegister[Left Registers[]]", "Property +1", lambda: pn("VI Server:RightShiftRegister", P_LEFTREGS, (500, y)))
    connect(ia_r, "element", lr, "reference", tag="R2 ")
    ia_l = ia((700, y)); connect(lr, data_name(lr), ia_l, "array", tag="R3 ")
    lo = pn("VI Server:Tunnel", P_OUTER, (900, y)); connect(ia_l, "element", lo, "reference", tag="R4 ")
    li = pn("VI Server:Tunnel", P_INSIDE, (1100, y)); connect(lo, "reference out", li, "reference", tag="R5 ")
    ia_li = ia((1300, y)); connect(li, data_name(li), ia_li, "array", tag="R6 ")
    ri = pn("VI Server:Tunnel", P_INSIDE, (500, y + 200)); connect(ia_r, "element", ri, "reference", branch=True, tag="R7 ")
    ia_ri = ia((700, y + 200)); connect(ri, data_name(ri), ia_ri, "array", tag="R8 ")
    es = g.exec_state(OP); print(f"   register chain: ExecState {es}", flush=True)
    if es != 1:
        print("STOP: register chain broken.", flush=True); return None
    # ---- node / control chain
    src_term = None
    if variant in ("LeftIn", "RightIn"):
        d = step("B0 PN_D Loop[Diagram] 6361401 (UNVERIFIED property - the gate)", "Property +1, data terminal 'Diagram'",
                 lambda: pn("VI Server:Loop", P_DIAGRAM, (300, y + 400)))
        if not d:
            return None
        print(f"   PN_D data terminal: {data_name(d)!r}", flush=True)
        connect(tmsc, "specific class reference", d, "reference", branch=True, tag="B0 ")
        if g.exec_state(OP) != 1:
            print("STOP: Loop[Diagram] on the WhileLoop seed breaks the VI - Wiki property not usable this way.", flush=True); return None
        nn = pn("VI Server:AbstractDiagram", P_NODES, (500, y + 400)); connect(d, data_name(d), nn, "reference", tag="B1 ")
    elif variant == "LeftOutNode":
        bd = pn("VI Server:VI", P_BD, (300, y + 400)); connect(ovr, "vi reference", bd, "reference", branch=True, tag="B0 ")
        nn = pn("VI Server:AbstractDiagram", P_NODES, (500, y + 400)); connect(bd, data_name(bd), nn, "reference", tag="B1 ")
    else:
        fp = pn("VI Server:VI", P_FP, (300, y + 400)); connect(ovr, "vi reference", fp, "reference", branch=True, tag="B0 ")
        pc = pn("VI Server:Panel", P_CTLS, (500, y + 400)); connect(fp, data_name(fp), pc, "reference", tag="B1 ")
        ia_c = ia((700, y + 400)); connect(pc, data_name(pc), ia_c, "array", tag="B2 "); make_ctl(ia_c, "index", "index_ctl", labels)
        ct = pn("VI Server:Control", P_CTLTERM, (900, y + 400)); connect(ia_c, "element", ct, "reference", tag="B3 ")
        src_term = (ct, data_name(ct))
    if variant != "LeftOutCtl":
        ia_n = ia((700, y + 400)); connect(nn, data_name(nn), ia_n, "array", tag="B2 "); make_ctl(ia_n, "index", "index_node", labels)
        tt = pn("VI Server:Node", P_TERMS, (900, y + 400)); connect(ia_n, "element", tt, "reference", tag="B3 ")
        ia_t = ia((1100, y + 400)); connect(tt, data_name(tt), ia_t, "array", tag="B4 "); make_ctl(ia_t, "index", "index_term", labels)
        src_term = (ia_t, "element")
    es = g.exec_state(OP); print(f"   node chain: ExecState {es}", flush=True)
    if es != 1:
        print("STOP: node chain broken.", flush=True); return None
    # ---- the invoke
    inv = step("C1 Invoke Terminal.Connect Wire", "Invoke +1", lambda: g.build_invoke(OP, "VI Server:Terminal", M_CONNECT, (1500, y + 300))[-1]["uid"])
    if not inv:
        return None
    sink, src = {"LeftIn": (src_term, (ia_li, "element")),
                 "RightIn": ((ia_ri, "element"), src_term),
                 "LeftOutNode": ((lo, data_name(lo)), src_term),
                 "LeftOutCtl": ((lo, data_name(lo)), src_term)}[variant]
    connect(sink[0], sink[1], inv, "reference", branch=(variant.startswith("LeftOut")), tag="C2 sink ")
    connect(src[0], src[1], inv, "Wire Source", branch=(variant == "LeftIn" or variant == "RightIn"), tag="C3 src ")
    make_ind(inv, "error out", "error", labels)
    g.set_auto_error_handling(OP, False)
    es = g.exec_state(OP)
    print("\n" + snap(f"assembled {variant}:") + f" labels {labels}", flush=True)
    if es != 1 or any(k == "exc" for _n, k in STEPS):
        print("VERDICT: BROKEN - NOT SAVING.", flush=True)
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return None
    g.save(OP)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    return labels


def run_op(variant, labels, target, loop_index, reg_index, **kw):
    vi = g.op(os.path.join(g.CLAUDEDEV, f"{OPFAM}_{variant}_v0.vi"))
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", CLS); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(labels["index_reg"], reg_index)
    for k, v in kw.items():
        vi.SetControlValue(labels[k], v)
    g._run(vi)
    return g._err(vi, labels["error"])


def test(all_labels):
    print("\n######## FUNCTIONAL TEST", flush=True)
    shutil.copyfile(SCRATCH_SRC, S); time.sleep(0.3)
    try:
        g.copy_into(g.OP_FORLOOP, STOP, S)
        g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
        inv0 = g.uids(S, "Invoke")
        dia0 = {d["uid"] for d in g.report_all(S, "Diagram")}
        g.while_loop(S, (200, 1400))
        body_uid = next(d["uid"] for d in g.report_all(S, "Diagram") if d["uid"] not in dia0)
        body = lambda: next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid)
        sub0 = g.uids(S, "SubVI"); g.drop_subvi(S, COPY_VI, body(), (300, 300))
        u_copy = [u for u in g.uids(S, "SubVI") if u not in sub0][0]
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(S, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(S, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(S)
        g.exit_while(S, STOP, body())
        top = walk(S, 0)
        creates = [u for u, v in top.items() if v[1] == "IMAQ Create"]
        sub_i = lambda u: [o["uid"] for o in g.report_all(S, "SubVI")].index(u)
        # Image Src of the body copy from the 2nd IMAQ Create (crosses the border: auto tunnel)
        g.wire(S, "SubVI", sub_i(creates[1]), "New Image", "SubVI", sub_i(u_copy), "Image Src", branch=True)
        bw = walk(S, body())
        n_copy = bw[u_copy][0]
        print(f"   body IMAQ Copy node {n_copy}: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in bw[u_copy][2]]}", flush=True)
        t_dst = term(bw[u_copy][2], "Image Dst", False)["i"]; t_out = term(bw[u_copy][2], "Image Dst Out", True)["i"]
        n_cr = top[creates[0]][0]; t_new = term(top[creates[0]][2], "New Image", True)["i"]
        print(f"   ExecState before the register: {g.exec_state(S)}", flush=True)
        uid = g.add_shift_reg(S, 0, 150)
        print(f"   register uid {uid}; ExecState {g.exec_state(S)} (0 expected)", flush=True)
        e1 = run_op("LeftOutNode", all_labels["LeftOutNode"], S, 0, 0, index_node=n_cr, index_term=t_new)
        e2 = run_op("LeftIn", all_labels["LeftIn"], S, 0, 0, index_node=n_copy, index_term=t_dst)
        e3 = run_op("RightIn", all_labels["RightIn"], S, 0, 0, index_node=n_copy, index_term=t_out)
        print(f"   op errors: {e1!r} {e2!r} {e3!r}", flush=True)
        check("T1 no op errors", not (e1 or e2 or e3))
        lft = g.shift_reg_left(S, 0, 0, 0, "WhileLoop"); print(f"   register: {lft}", flush=True)
        bw = walk(S, body()); top = walk(S, 0)
        w_dst = term(bw[u_copy][2], "Image Dst", False)["wire"]; w_out = term(bw[u_copy][2], "Image Dst Out", True)["wire"]
        w_new = term(top[creates[0]][2], "New Image", True)["wire"]
        check("T2 left OUTSIDE wire == IMAQ Create.New Image wire", lft["left"]["out"]["wire"] and lft["left"]["out"]["wire"] == w_new, f"{lft['left']['out']['wire']} vs {w_new}")
        check("T3 left INSIDE wire == IMAQ Copy.Image Dst wire", lft["left"]["inside"] and lft["left"]["inside"][0]["wire"] == w_dst and w_dst, f"{lft['left']['inside']} vs {w_dst}")
        check("T4 right INSIDE wire == IMAQ Copy.Image Dst Out wire", lft["inside"] and lft["inside"][0]["wire"] == w_out and w_out, f"{lft['inside']} vs {w_out}")
        es = g.exec_state(S); check("T5 ExecState 1 with all three wired", es == 1, str(es))
        if es == 1:
            vi = g.op(S); vi.SetControlValue(STOP, True); vi.SetControlValue("Image Name", "srA"); vi.SetControlValue("Image Name 2", "srB")
            t0 = time.time()
            try:
                g._run(vi); ok = True
            except RuntimeError as e:
                ok = False; print(f"   run: {str(e)[:160]}", flush=True)
            check("T6 the VI runs and returns with stop TRUE", ok, f"{time.time() - t0:.2f} s")
        # LeftOutCtl on a second register, from the STRING control 'Image Name' -> predicted broken wire
        uid2 = g.add_shift_reg(S, 0, 250)
        p_name = next(i for i, (l, ind) in enumerate([(l, ind) for _i, l, ind in g.fp_labels(S)]) if l == "Image Name" and not ind)
        e4 = run_op("LeftOutCtl", all_labels["LeftOutCtl"], S, 0, 1, index_ctl=p_name)
        lft2 = g.shift_reg_left(S, 0, 1, 0, "WhileLoop")
        es2 = g.exec_state(S)
        print(f"   LeftOutCtl: err {e4!r}, left outside wire {lft2['left']['out']['wire']}, ExecState {es2}", flush=True)
        check("T7 LeftOutCtl made a wire from the control terminal", not e4 and lft2["left"]["out"]["wire"] != 0)
        check("T8 type mismatch -> ExecState 0 (predicted)", es2 == 0)
        # peer (a3 review): Remove Bad Wires can cascade - prove that ONLY the string wire disappeared
        w_before = g.uids(S, "Wire"); w_str = lft2["left"]["out"]["wire"]
        g.remove_bad_wires_scripted(S)
        gone = w_before - g.uids(S, "Wire")
        check("T8b Remove Bad Wires removed exactly the string wire", gone == {w_str}, f"gone={gone} expected={{{w_str}}}")
        lft_again = g.shift_reg_left(S, 0, 0, 0, "WhileLoop")
        check("T8c register 1's three wires survived", lft_again["left"]["out"]["wire"] == w_new and lft_again["left"]["inside"][0]["wire"] == w_dst and lft_again["inside"][0]["wire"] == w_out)
        print(f"   after Remove Bad Wires: ExecState {g.exec_state(S)} (register 2 still unwired -> 0 is fine)", flush=True)
        check("T9 no junk Invoke", not [u for u in g.uids(S, "Invoke") if u not in inv0])
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        if os.path.exists(S):
            os.remove(S)


def add_sr_for(target, loop_index, y):
    """OpAddShiftRegF_v0 (built by build_opaddshiftreg_v0.py with SR_SEED=For) -> new register uid."""
    with open(ADDSR_MAP, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpAddShiftRegF_v0.vi"))
    vi.SetControlValue("vi path", target); vi.SetControlValue("Class Name", "ForLoop"); vi.SetControlValue("index", loop_index)
    vi.SetControlValue(lab["y_position"], int(y)); g._run(vi)
    err = g._err(vi, lab["error"])
    if err:
        raise RuntimeError(f"add_sr_for: {err}")
    return int(vi.GetControlValue(lab["uid"]))


def test_for(all_labels):
    """FUNCTIONAL, For seed: HARNESS_copyloop's existing For loop (N = 1024); a NEW IMAQ Copy dropped in its body;
    one register: LeftOutNode <- top IMAQ Create.'New Image'; LeftIn -> body copy.'Image Dst'; RightIn <- 'Image Dst
    Out'. The WhileLoop-seeded readers cannot census a For loop's register, so the proof is from the node side:
    the three node terminals carry non-zero wires, ExecState 0 -> 1, the VI RUNS (1024 iterations) and returns."""
    print("\n######## FUNCTIONAL TEST (For seed)", flush=True)
    shutil.copyfile(SCRATCH_SRC, S); time.sleep(0.3)
    try:
        g.report_all(S, "SubVI"); g.open_panel(S); time.sleep(0.8)
        inv0 = g.uids(S, "Invoke")
        dias = g.report_all(S, "Diagram")
        body_uid = next(d["uid"] for d in dias if "For" in str(d.get("owner")))
        body = lambda: next(i for i, d in enumerate(g.report_all(S, "Diagram")) if d["uid"] == body_uid)
        sub0 = g.uids(S, "SubVI"); g.drop_subvi(S, COPY_VI, body(), (500, 500))
        u_copy = [u for u in g.uids(S, "SubVI") if u not in sub0][0]
        junk = [u for u in g.uids(S, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(S, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(S, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(S)
        top = walk(S, 0)
        creates = [u for u, v in top.items() if v[1] == "IMAQ Create"]
        sub_i = lambda u: [o["uid"] for o in g.report_all(S, "SubVI")].index(u)
        g.wire(S, "SubVI", sub_i(creates[1]), "New Image", "SubVI", sub_i(u_copy), "Image Src", branch=True)
        bw = walk(S, body()); n_copy = bw[u_copy][0]
        t_dst = term(bw[u_copy][2], "Image Dst", False)["i"]; t_out = term(bw[u_copy][2], "Image Dst Out", True)["i"]
        n_cr = top[creates[0]][0]; t_new = term(top[creates[0]][2], "New Image", True)["i"]
        es0 = g.exec_state(S); print(f"   ExecState before the register: {es0}", flush=True)
        uid = add_sr_for(S, 0, 150)
        print(f"   register uid {uid}; ExecState {g.exec_state(S)} (0 expected)", flush=True)
        e1 = run_op("LeftOutNode", all_labels["LeftOutNode"], S, 0, 0, index_node=n_cr, index_term=t_new)
        e2 = run_op("LeftIn", all_labels["LeftIn"], S, 0, 0, index_node=n_copy, index_term=t_dst)
        e3 = run_op("RightIn", all_labels["RightIn"], S, 0, 0, index_node=n_copy, index_term=t_out)
        check("F1 no op errors", not (e1 or e2 or e3), f"{e1!r} {e2!r} {e3!r}")
        bw = walk(S, body()); top = walk(S, 0)
        w_dst = term(bw[u_copy][2], "Image Dst", False)["wire"]; w_out = term(bw[u_copy][2], "Image Dst Out", True)["wire"]
        w_new = term(top[creates[0]][2], "New Image", True)["wire"]
        check("F2 body copy 'Image Dst' wired (left inside)", bool(w_dst), str(w_dst))
        check("F3 body copy 'Image Dst Out' wired (right inside)", bool(w_out), str(w_out))
        check("F4 top IMAQ Create 'New Image' wired (left outside)", bool(w_new), str(w_new))
        es = g.exec_state(S); check("F5 ExecState 1 with all three wired", es == 1, str(es))
        if es == 1:
            vi = g.op(S); vi.SetControlValue("Image Name", "srFA"); vi.SetControlValue("Image Name 2", "srFB")
            t0 = time.time()
            try:
                g._run(vi); ok = True
            except RuntimeError as e:
                ok = False; print(f"   run: {str(e)[:160]}", flush=True)
            check("F6 the VI runs 1024 iterations and returns", ok, f"{time.time() - t0:.2f} s")
        check("F7 no junk Invoke", not [u for u in g.uids(S, "Invoke") if u not in inv0])
    finally:
        try:
            g.close_panel(S)
        except Exception:
            pass
        if os.path.exists(S):
            os.remove(S)


def main():
    g._lv = None
    donor_md5 = hashlib.md5(open(SRC, "rb").read()).hexdigest()
    all_labels = {}
    for v in VARIANTS:          # all four on both seeds: the assembly seeds its registers from CONTROLS (LeftOutCtl)
        STEPS.clear()
        lab = build(v)
        if not lab:
            print(f"\nSTOP at {v}: nothing further built.", flush=True)
            return 2
        all_labels[v] = lab
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(all_labels, f, indent=2)
    if FOR:
        test_for(all_labels)
    else:
        test(all_labels)
    same = hashlib.md5(open(SRC, "rb").read()).hexdigest() == donor_md5
    n_ok = sum(1 for _n, ok in PASS if ok)
    print(f"\ndonor md5 unchanged: {same}\nSUMMARY {n_ok}/{len(PASS)} PASS", flush=True)
    for n, ok in PASS:
        print(f"   {'PASS' if ok else 'FAIL'} {n}", flush=True)
    return 0 if (PASS and n_ok == len(PASS) and same) else 1


if __name__ == "__main__":
    sys.exit(main())
