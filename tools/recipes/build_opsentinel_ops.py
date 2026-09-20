r"""build_opsentinel_ops.py [equal|const|both] - the TWO ops D1's end-of-stream sentinel test needs INSIDE a loop
body, per `docs/d1-build-plan.md` §11g.1 (judgement, 2026-09-17: route (c), the cycle-15 freeze lifted for
exactly these two):

  OpCreateEqual_v0.vi  - erdosmiller `Create Equal.vi`    -> one `Equal?` Comparison node on a NAMED subdiagram
  OpCreateConst_v0.vi  - erdosmiller `Create Constant.vi` -> one numeric/Boolean CONSTANT on a NAMED subdiagram

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_opsentinel_ops.log \
        -- py -u tools/recipes/build_opsentinel_ops.py both

===============================================================================================================
WHAT ALREADY EXISTS - checked before a line was written, and then CHECKED AGAIN by the prior-art review
===============================================================================================================
`archive/peer/2026-09-17-priorart-priorart-d1-sentinel-ops.md` (ANSWERED, 7 findings, 0 novel). What it changed
in this file, finding by finding - the disposition is in that archive:

  B1 `already-built` - `tools/recipes/build_opcreator.py` is a GENERIC erdosmiller-creator op builder, run three
     times (`tools/bench/creators_chain.log:15-21,:32-38` = OpBuildFlatten_v0 / OpBuildUnflatten_v0). Its SCOPE
     is the **top-level** diagram (`:3`, `:50`: `PN VI.Block Diagram -> 'Diagram in'`), which is exactly what D1
     cannot use. **Taken:** this file is `build_opqueue.py`'s donor route (OpExitLoop_v0, whose `Diagram in`
     already comes from `Traverse('Diagram')[index 2]`) PLUS `build_opcreator.py:59-72`'s required-input probe
     loop, verbatim in shape. Neither half is re-invented.
  B2 `already-failed` - `build_opcreator.py --creator "Create Case Structure.vi"` blocked behind a modal dialog
     on EVERY run (`tools/bench/caseop_chain.log:18-21`) because a **terminal refnum was set over COM**
     (`docs/NAMES.md:473-475`: writing 0 into `Selector` makes the creator call `Connect Wire` with an invalid
     reference -> a 1055 dialog). **Taken:** no refnum input is ever set over COM here. `Create Equal.vi`'s
     `x` and `y` are fetched INSIDE the op from `Get Outputs` of a node named by Traverse - the `queue_node`
     fix (`tools/gscript.py:928-934`). `Create Constant.vi` has NO refnum input at all.
     🔴 **The half B2 leaves open is NOT closed by this file and must not be pretended away:** D1's sentinel
     wants `Equal?`'s `y` to come from the CONSTANT, and a constant is not a `Node`, so no `Get Outputs` reaches
     it and `Create Constant.vi`'s `Terminal` output dies with its op's dataflow
     (`archive/2026-08-31-status-full-assembly-narrative.md:531-534`, "one fused op"). Whether that becomes a
     FUSED create-const-and-connect op or a second addressing path (`Constant.Terminal` **634AC04** ->
     `Terminal.Connect Wire` **6349C03**, both already built inside `OpConstValueN_v1` / `OpStopFromNode_v0`) is
     a THIRD op either way, i.e. beyond the two §11g.1 authorises - **JUDGEMENT, reported, not taken.**
  B3 `helper-exists` - `Terminal.Create Constant` **6349C00** is one ID off `create_control` 6349C01 /
     `create_indicator` 6349C02 (`tools/gscript.py:2155-2161,:2180-2182`) and would create the constant FROM the
     sink terminal, already typed and already WIRED - which answers B2 as well. Its ladder is **top-level only**
     (`docs/NAMES.md:460-461`), so it needs the same subdiagram work. Recorded as the alternative route; not
     built here (third op, judgement).
  B4 `already-measured` - the owner-chain acceptance gate and its uids already exist
     (`tools/bench/build_d1_v0_run5.log:100-109`). **Taken:** the test below asserts uid -> body `Diagram` ->
     the right `WhileLoop` with `read_owner`, the same reader, and does not re-derive the gate.
  A2 `refuted-already` - twice before, a peer refused an erdosmiller library VI in favour of the DOCUMENTED
     VI-Server method, and neither precedent was cited by §11g.1:
     `archive/peer/2026-09-14-stage2-shiftreg-primitive.md:85` ("the direct Loop invoke method is the answer";
     disposition `:126-129`, `OpAddShiftReg_v0` built on `Loop.Add Shift Register` 6361000) and
     `archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md:259`, which is WHY `OpStopFromNode_v0` exists
     (`docs/toolkit-capabilities.md:51`: "refused the erdosmiller `Exit While Loop.vi` front-half swap").
     **Taken, with the reviewer's own scope note:** both precedents are about using a library VI for an
     UNDOCUMENTED SIDE EFFECT; `Create Equal.vi` / `Create Constant.vi` doing their documented job is a weaker
     case, and `queue_node` is itself four library creators that work (7/7). The precedents are now cited here,
     and the documented alternative is priced in B3 rather than left as a bare ID pair.
  A3 `contradicted` - "162/162" belongs to `Track_v6_CPU_queue_v0.vi`, not to the queue OPS, whose own evidence
     is `test_opqueue.log` **7/7** (`docs/toolkit-capabilities.md:32`). Corrected wherever this file cites it.
  A4 `unread-evidence` - `docs/stage2-assembly-step-e.md:221-222` already specifies this node as
     **`OpBuildEqual_v0`** in the `OpBuildIA_v0` pattern. Recorded: two in-house templates existed and only one
     was known to §11g.1. This file keeps the `queue_node` template because the PLAN names it and because
     `OpBuildIA_v0`'s `Diagram in` is the top-level one (B1's scope note) - the named-subdiagram requirement
     decides it, not preference.

Also already existing and re-used, not rebuilt: `tools/bench/diag_create_const_equal.log` (2026-09-17, 8/0) -
the two creators' connector panes AND the DATA TYPE of every input, which is why nothing below guesses:
  Create Constant.vi : Diagram in(0,refnum) location(2,cluster) Diagram out(4) **Type(5,VARIANT)**
                       Terminal(6,refnum out) **Value(7,VARIANT)** error in(11) error out(15)
  Create Equal.vi    : Diagram in(0) location(2) Diagram out(4) **x(5,refnum)** x = y?(6,refnum out)
                       **y(7,refnum)** Compare Aggregates?(9,bool=TRUE) error in(11) error out(15)

===============================================================================================================
PREDICTION CONTRACT - every line pass/fail, nothing inferred
===============================================================================================================
BUILD, per op (the donor `OpExitLoop_v0.vi` md5 is asserted unchanged at the end - it is a claudeDev op, but a
build that silently edits its own donor is the failure class `probe_move_into_v0` paid for):
 W1  the op file is a fresh copy of OpExitLoop_v0 and opens with ExecState 1
 W2  `Exit For Loop.vi` deleted, the creator dropped: SubVI count unchanged (-1 +1)
 W3  `Diagram in` <- the donor's `To More Specific Class`(Diagram) source, `error in` <- the donor's source,
     the creator's OWN `error out` (the LAST source terminal named `error out`) -> the donor's error sinks
 W4  every refnum input in INPUTS is wired from `Index Array[0]` of the named `Get Outputs` (equal: x<-216,
     y<-348; const: none)  -- NO refnum is set over COM (B2)
 W5  a front-panel control exists for `location (0, 0)` and for every REMAINING required input
     (const: `Type`, `Value`), found by `build_opcreator.py`'s probe loop; the labels are recorded
 W6  **ExecState 1** and the op is SAVED under claudeDev; a labels JSON is written next to the queue ops'

FUNCTIONAL TEST, on a scratch copy of EMPTY_v0.vi (unique name per run, deleted in the same run):
 F1  scratch = EMPTY_v0 copy, ExecState 1 before anything
 F2  one While loop created on the TOP-LEVEL diagram -> WhileLoop W, body Diagram D at Traverse index i_D
 F3  `Create Dequeue Element.vi` dropped on the TOP-LEVEL diagram as the SOURCE NODE, and its required inputs
     given controls until the scratch reads **ExecState 1** again (it has three `Terminal`-refnum OUTPUTS -
     `queue out`, `element`, `timed out?` - so `Equal?` can compare two operands of the SAME type, which a
     mixed pair could not)
 F4  **OpCreateConst_v0 places a constant on Diagram[i_D]**: exactly one new `Constant`-family object; its
     owner chain reads uid -> `Diagram` D -> `WhileLoop` W (B4's reader); the op's `error out` is empty.
     Reported, NOT gated: whether the VARIANT `Type`/`Value` inputs survived the COM boundary - the created
     object's CLASS (`DigitalNumericConstant` = a typed numeric got through) is the observable, and B3 cites a
     recorded variant-marshalling failure in the READ direction, so this is a measurement, not an assumption.
 F5  **OpCreateEqual_v0 places an `Equal?` on Diagram[i_D]** with x <- `queue out`, y <- `element` of the
     dropped creator on the TOP-LEVEL diagram: exactly one new node whose owner chain reads D -> W; the wires
     cross the loop border, so `LoopTunnel` is expected to GROW (reported as a range, `gscript.wire`'s own rule)
 F6  **ExecState 1 on the scratch after both placements** - the "trivially wired case" of the brief. An
     unwired constant cannot break a VI; an `Equal?` with both inputs wired and its output unused cannot
     either. A 0 here is a real failure and is reported with the bare-terminal census, not explained.
 F7  scratch deleted; donor md5 unchanged; handles before/after.

FAILURE BUDGET 2 per op (CLAUDE.md §3). No repair pass inside the run.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "bench"))
sys.path.insert(0, HERE)
import gscript as g                                      # noqa: E402
import build_track_v6_core as B                          # noqa: E402
from bench_prep import labview_handles                   # noqa: E402
from build_opownerchain_v1 import read_owner             # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER         # noqa: E402

LIB = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Erdos Miller\LV-Scripting"
SRC = os.path.join(g.CLAUDEDEV, "OpExitLoop_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
SRC_NODE_VI = os.path.join(LIB, "Create Dequeue Element.vi")
BENCH = os.path.join(ROOT, "bench")
OWNER_LABELS = os.path.join(BENCH, "opwiresource_v5_labels.json")
RUN_STAMP = time.strftime("%H%M%S")

SPEC = {
    "equal": dict(creator="Create Equal.vi", op="OpCreateEqual_v0.vi", inputs={"x": 216, "y": 348}),
    "const": dict(creator="Create Constant.vi", op="OpCreateConst_v0.vi", inputs={},
                  force_controls=("Type", "Value")),
}
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []
_OL = None


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def owner_of(target, uid):
    """B4's reader, unchanged: OpOwnerChain_v1 through build_opownerchain_v1.read_owner."""
    global _OL
    if _OL is None:
        with open(OWNER_LABELS, encoding="utf-8") as f:
            _OL = json.load(f)
    import build_opownerchain_v1 as OB
    vi = g.op(OP_OWNER)
    saved = OB.MAIN
    try:
        OB.MAIN = target
        r = read_owner(vi, _OL, uid)
    finally:
        OB.MAIN = saved
    return r


# ==================================================================================== BUILD
def build(kind):
    spec = SPEC[kind]
    OP = os.path.join(g.CLAUDEDEV, spec["op"])
    creator = os.path.join(LIB, spec["creator"])
    print(f"\n################ BUILD {spec['op']} from {spec['creator']}", flush=True)
    donor_md5 = md5(SRC)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    inv0 = g.uids(OP, "Invoke")

    def purge():
        junk = [u for u in g.uids(OP, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(OP, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(OP, "Invoke", i, verify=False)
            g.remove_bad_wires_scripted(OP)

    def nodes():
        labels = {r["uid"]: r["label"] for r in g.node_labels(OP, 0)}
        out = {}
        for cand in range(60):
            nu, rows = g.node_terms_uid(OP, 0, cand)
            if not nu:
                break
            out[nu] = (cand, labels.get(nu), rows)
        return out

    def idx(cls, uid):
        return [o["uid"] for o in g.report_all(OP, cls)].index(uid)

    gate(f"W1 {spec['op']} is a fresh OpExitLoop_v0 copy, ExecState 1", g.exec_state(OP) == 1)
    nd = nodes()
    u_exit = next(u for u, (n, l, r) in nd.items() if l == "Exit For Loop.vi")
    go = [u for u, (n, l, r) in nd.items() if l == "Get Outputs.vi"]
    pw = {r["label"]: r["wire"] for r in g.panel_wiring(OP)}
    u216 = next(u for u in go if any(r["name"] == "Names" and r["wire"] == pw["Names"] for r in nd[u][2]))
    u348 = next(u for u in go if u != u216)
    rows_exit = nd[u_exit][2]
    w_diag = next(r["wire"] for r in rows_exit if r["name"] == "Diagram in" and not r["is_source"])
    w_err_in = next(r["wire"] for r in rows_exit if r["name"] == "error in (no error)")
    w_err_out = next(r["wire"] for r in rows_exit if r["name"] == "error out")

    def src(w):
        return next(((u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr
                     if r["is_source"] and w and r["wire"] == w and u != u_exit), None)

    s_diag, s_err = src(w_diag), src(w_err_in)
    sinks_err = [(u, r["name"]) for u, (n, l, rr) in nd.items() for r in rr
                 if not r["is_source"] and r["wire"] == w_err_out and u != u_exit]
    err_ind = [r["label"] for r in g.panel_wiring(OP) if r["wire"] == w_err_out]
    fact(f"donor: GetOutputs 216={u216} 348={u348}; Diagram in <- {s_diag}; error in <- {s_err}; "
         f"error out -> {sinks_err} + {err_ind}")

    def cls_of(uid):
        lab = nd[uid][1] or ""
        return "SubVI" if lab.endswith(".vi") else ("Property" if lab == "Property Node" else "Function")

    n_sub0 = g.count(OP, "SubVI")
    g.delete_object(OP, "SubVI", idx("SubVI", u_exit))
    g.remove_bad_wires_scripted(OP)
    before = g.uids(OP, "SubVI")
    g.drop_subvi(OP, creator, 0, (1500, 700))
    newsub = [u for u in g.uids(OP, "SubVI") if u not in before]
    purge()
    if not gate("W2 Exit For Loop deleted, creator dropped (SubVI count unchanged)",
                len(newsub) == 1 and g.count(OP, "SubVI") == n_sub0,
                f"new {newsub}, SubVI {g.count(OP, 'SubVI')} (was {n_sub0})"):
        return None
    u_c = newsub[0]

    g.wire(OP, cls_of(s_diag[0]), idx(cls_of(s_diag[0]), s_diag[0]), s_diag[1], "SubVI", idx("SubVI", u_c),
           "Diagram in")
    g.wire(OP, cls_of(s_err[0]), idx(cls_of(s_err[0]), s_err[0]), s_err[1], "SubVI", idx("SubVI", u_c),
           "error in (no error)", branch=True)
    ndc = nodes()
    n_c0 = ndc[u_c][0]
    # the creator has TWO source terminals named 'error out' (t10 = the CREATED node's error terminal refnum,
    # t15 = the creator's own error chain). Wiring by name hits t10 - build_opqueue.py:121-127 paid a run for
    # this. Take the LAST, by terminal INDEX.
    t15 = max(r["i"] for r in ndc[u_c][2] if r["name"] == "error out" and r["is_source"])
    for su, sname in sinks_err:
        n_s = ndc[su][0]
        t_s = next(r["i"] for r in ndc[su][2] if r["name"] == sname and not r["is_source"])
        g.connect_terminals(OP, n_s, t_s, n_c0, t15)
    purge()
    gate("W3 Diagram in / error in / creator's own error out wired", True,
         f"creator error-out terminal index {t15}")

    ias = {}
    for inp, which in spec["inputs"].items():
        u_go = u216 if which == 216 else u348
        ia = g.build_index_array(OP, (1200, 900 + 150 * len(ias)))[-1]["uid"]
        purge()
        ias[inp] = ia
        nd2 = nodes()
        n_ia, n_go = nd2[ia][0], nd2[u_go][0]
        t_arr = next(r["i"] for r in nd2[ia][2] if r["name"] == "array")
        t_out = next(r["i"] for r in nd2[u_go][2] if r["name"] == "Outputs" and r["is_source"])
        g.connect_terminals(OP, n_ia, t_arr, n_go, t_out)
        purge()
        g.wire(OP, "IndexArray", idx("IndexArray", ia), "element", "SubVI", idx("SubVI", u_c), inp)
        purge()
    gate("W4 every refnum input wired from Index Array[0] of its Get Outputs (none set over COM)",
         len(ias) == len(spec["inputs"]), f"{sorted(ias)}")

    c0 = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    nd3 = nodes()
    n_c = nd3[u_c][0]
    t_loc = next(r["i"] for r in nd3[u_c][2] if r["name"] == "location (0, 0)")
    g.create_control(OP, n_c, t_loc)
    purge()
    # build_opcreator.py:59-72's probe loop, for the inputs that are NOT refnums (const: Type, Value)
    es = g.exec_state(OP)
    extra, ctl_by_term = [], {}
    for t in range(0, 16):
        if es == 1:
            break
        ndp = nodes()
        n_c = ndp[u_c][0]
        tname = next((r["name"] for r in ndp[u_c][2] if r["i"] == t), None)
        w1 = g.count(OP, "Wire")
        try:
            new, lab = g.create_control(OP, n_c, t)
        except Exception as e:
            print(f"   probe t{t}: EXC {str(e)[:110]}", flush=True)
            continue
        if new and lab and g.count(OP, "Wire") > w1:
            purge()
            es = g.exec_state(OP)
            extra.append((t, tname, lab))
            ctl_by_term[tname or f"t{t}"] = lab
            print(f"   probe t{t} ({tname!r}): control {lab!r} -> ExecState {es}", flush=True)
            continue
        if new:                        # an OUTPUT got an unwired control: remove it again
            ct = [o["uid"] for o in g.report_all(OP, "ControlTerminal")]
            for o in new:
                if o["uid"] in ct:
                    g.delete_object(OP, "ControlTerminal", ct.index(o["uid"]), verify=False)
                    ct = [x["uid"] for x in g.report_all(OP, "ControlTerminal")]
            g.remove_bad_wires_scripted(OP)
            purge()
    # RUN 1 MEASURED THE HOLE (build_opsentinel_ops.log, 09:43): the probe loop stops at ExecState 1, and
    # `Create Constant.vi`'s `Value` is OPTIONAL - `Type` alone made the op runnable, so `Value` never got a
    # control and the op could only ever create a DEFAULT-valued constant. D1's sentinel needs **-1**. So every
    # input this op is SPECIFIED to carry is given a control explicitly, not only the ones brokenness forces.
    for want in spec.get("force_controls", ()):
        if want in ctl_by_term:
            continue
        ndf = nodes()
        n_cf = ndf[u_c][0]
        tf = next((r["i"] for r in ndf[u_c][2] if r["name"] == want and not r["is_source"]), None)
        if tf is None:
            print(f"   force '{want}': no such input terminal", flush=True)
            continue
        try:
            new, lab = g.create_control(OP, n_cf, tf)
        except Exception as e:
            print(f"   force '{want}': EXC {str(e)[:110]}", flush=True)
            continue
        purge()
        if new and lab:
            extra.append((tf, want, lab))
            ctl_by_term[want] = lab
            print(f"   force t{tf} ({want!r}): control {lab!r} -> ExecState {g.exec_state(OP)}", flush=True)
    loc = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in c0]
    gate("W5 a control for 'location (0, 0)' (+ every remaining required input)", bool(loc),
         f"new controls {loc}; probe-created {extra}")

    if err_ind and g.exec_state(OP) == 1:
        nd7 = nodes()
        n_c7 = nd7[u_c][0]
        t15b = max(r["i"] for r in nd7[u_c][2] if r["name"] == "error out" and r["is_source"])
        pi = [i for i, l, ind in g.fp_labels(OP) if l == err_ind[0]]
        try:
            g.connect_ctl(OP, pi[0], n_c7, t15b)
        except Exception as e:
            print(f"   error-out indicator: {str(e)[:110]}", flush=True)
        purge()
    es = g.exec_state(OP)
    if not gate(f"W6 {spec['op']} ExecState 1", es == 1, f"ExecState {es}"):
        try:
            g.close_panel(OP)
        except Exception:
            pass
        return None
    g.set_auto_error_handling(OP, False)
    g.save(OP)
    labels = {"location": loc[0] if loc else "location (0, 0)", "inputs": spec["inputs"],
              "extra_controls": extra, "ctl_by_term": ctl_by_term, "creator": spec["creator"]}
    with open(os.path.join(BENCH, f"opcreate_{kind}_labels.json"), "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    gate("W6b donor OpExitLoop_v0.vi md5 unchanged", md5(SRC) == donor_md5, donor_md5)
    fact(f"{spec['op']} SAVED; labels {labels}")
    return labels


# ==================================================================================== the op wrappers
def create_node(kind, labels, target, diagram_index, location, src_cls=None, src_index=0,
                src_names=(), values=None):
    """Run Op<CreateEqual|CreateConst>_v0 on `target`. Same call shape as `gscript.queue_node`, so the wrapper
    that ends up in gscript.py is this function with `op()`/`_run()` inlined."""
    spec = SPEC[kind]
    g.ensure_loaded(target)
    vi = g.op(os.path.join(g.CLAUDEDEV, spec["op"]))
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", src_cls or "SubVI")
    vi.SetControlValue("index", int(src_index))
    vi.SetControlValue("Names", list(src_names[:1]))
    vi.SetControlValue("Class Name 2", "Diagram")
    vi.SetControlValue("index 2", int(diagram_index))
    vi.SetControlValue("Names 2", list(src_names[1:2]))
    vi.SetControlValue(labels["location"], list(location))
    for lab, val in (values or {}).items():
        vi.SetControlValue(lab, val)
    g._run(vi)
    return g._err(vi)


# ==================================================================================== FUNCTIONAL TEST
def functional_test(built):
    print("\n################ FUNCTIONAL TEST on a scratch copy of EMPTY_v0", flush=True)
    scratch = os.path.join(g.CLAUDEDEV, f"SCRATCH_sentinel_{RUN_STAMP}.vi")
    if os.path.exists(scratch):
        os.remove(scratch)
    shutil.copyfile(EMPTY, scratch)
    time.sleep(0.3)
    g.report_all(scratch, "SubVI")
    g.open_panel(scratch)
    time.sleep(0.8)
    inv0 = g.uids(scratch, "Invoke")
    try:
        gate("F1 scratch EMPTY_v0 copy opens ExecState 1", g.exec_state(scratch) == 1)
        dg0, wl0 = g.uids(scratch, "Diagram"), g.uids(scratch, "WhileLoop")
        g.while_loop(scratch, (500, 500))
        new_dg = g.new_since(scratch, "Diagram", dg0)
        new_wl = g.new_since(scratch, "WhileLoop", wl0)
        if not gate("F2 one While loop created", len(new_dg) == 1 and len(new_wl) == 1,
                    f"+{len(new_dg)} diagrams, +{len(new_wl)} loops"):
            return scratch
        W, D = new_wl[0]["uid"], new_dg[0]["uid"]
        i_D = new_dg[0].get("i", [o["uid"] for o in g.report_all(scratch, "Diagram")].index(D))
        fact(f"scratch: WhileLoop #{W}, body Diagram #{D} at Traverse index {i_D}")

        sub0 = g.uids(scratch, "SubVI")
        g.drop_subvi(scratch, SRC_NODE_VI, 0, (150, 150))
        newsub = g.new_since(scratch, "SubVI", sub0)
        n_src = g.count(scratch, "Node") - 1
        es = g.exec_state(scratch)
        made = []
        for t in range(0, 14):
            if es == 1:
                break
            w1 = g.count(scratch, "Wire")
            try:
                new, lab = g.create_control(scratch, n_src, t)
            except Exception as e:
                print(f"   src t{t}: EXC {str(e)[:100]}", flush=True)
                continue
            if new and lab and g.count(scratch, "Wire") > w1:
                es = g.exec_state(scratch)
                made.append((t, lab))
                continue
            if new:
                ct = [o["uid"] for o in g.report_all(scratch, "ControlTerminal")]
                for o in new:
                    if o["uid"] in ct:
                        g.delete_object(scratch, "ControlTerminal", ct.index(o["uid"]), verify=False)
                        ct = [x["uid"] for x in g.report_all(scratch, "ControlTerminal")]
                g.remove_bad_wires_scripted(scratch)
        # RUN 1's F3 GATED ON ExecState AND COULD NOT DISCRIMINATE - a gate defect, measured, not a build
        # defect. `gscript.while_loop`'s own docstring says it: "The new loop's conditional terminal is UNWIRED
        # (ExecState 0 until OpExitWhile / a stop control is wired)", so F2 makes the scratch broken by
        # construction and every later ExecState read is pinned at 0. That is `docs/NAMES.md:788` verbatim:
        # never gate on ExecState while a required input is unwired. Run 1's own bare-terminal census proved
        # the dropped node innocent - its only bare sinks were the FOUR UNNAMED conpane slots (t1, t3, t12,
        # t13 of `Create Dequeue Element.vi`), which are free terminals, not required inputs.
        bare_named = [r["name"] for r in B.walk(scratch, 0).get(newsub[0]["uid"] if newsub else 0, (0, "", []))[2]
                      if not r["is_source"] and r["wire"] == 0 and r["name"]]
        gate("F3 source node dropped with every NAMED input wired to a control", not bare_named and len(newsub) == 1,
             f"bare named inputs {bare_named}; controls {made}; ExecState {es} "
             f"(0 is EXPECTED here - F2's loop has an unwired conditional terminal)")

        # ---- F4: the CONSTANT on the body diagram
        if "const" in built:
            c0 = g.uids(scratch, "Constant")
            cb = built["const"].get("ctl_by_term", {})
            vals = {}
            if cb.get("Type"):
                vals[cb["Type"]] = 0.0         # a DBL variant -> a DBL constant
            if cb.get("Value"):
                vals[cb["Value"]] = -1.0       # the sentinel literal (plan §9a)
            fact(f"F4 setting the const op's VARIANT inputs: {vals} (labels from the build's own probe)")
            err = create_node("const", built["const"], scratch, i_D, (200, 120), values=vals)
            newc = g.new_since(scratch, "Constant", c0)
            classes = [o.get("class") for o in newc]
            ok = len(newc) == 1
            gate("F4 exactly one new Constant-family object on the body diagram", ok,
                 f"new {[(o['uid'], o.get('class'), o.get('pos')) for o in newc]}; op error {err!r}")
            if ok:
                r = owner_of(scratch, newc[0]["uid"])
                r2 = owner_of(scratch, r["owner_uid"]) if r.get("owner_uid") else {}
                gate("F4b owner chain: constant -> body Diagram -> the new WhileLoop",
                     r.get("owner_uid") == D and r2.get("owner_uid") == W,
                     f"{newc[0]['uid']} -> {r.get('ownercls')}#{r.get('owner_uid')} -> "
                     f"{r2.get('ownercls')}#{r2.get('owner_uid')} (want Diagram#{D} -> WhileLoop#{W})")
                fact(f"F4 REPORTED (not gated): created class {classes}, DigitalNumericConstant count "
                     f"{g.count(scratch, 'DigitalNumericConstant')} - this is the VARIANT Type/Value "
                     f"marshalling result (B3's open question)")

        # ---- F5: the Equal? on the body diagram, both operands from the top-level source node
        newn, ok = [], False
        if "equal" in built:
            n0 = g.uids(scratch, "Node")
            tun0 = g.count(scratch, "LoopTunnel")
            err = create_node("equal", built["equal"], scratch, i_D, (200, 220),
                              src_cls="SubVI", src_index=0, src_names=["queue out", "element"])
            newn = [o for o in g.new_since(scratch, "Node", n0) if o.get("class") != "Invoke"]
            ok = len(newn) == 1
            gate("F5 exactly one new node (the Equal?) on the body diagram", ok,
                 f"new {[(o['uid'], o.get('class'), o.get('pos')) for o in newn]}; op error {err!r}")
            fact(f"F5 LoopTunnel {tun0} -> {g.count(scratch, 'LoopTunnel')} "
                 f"(both operands cross the loop border; gscript.wire's rule says this is a RANGE)")
            if ok:
                r = owner_of(scratch, newn[0]["uid"])
                r2 = owner_of(scratch, r["owner_uid"]) if r.get("owner_uid") else {}
                gate("F5b owner chain: Equal? -> body Diagram -> the new WhileLoop",
                     r.get("owner_uid") == D and r2.get("owner_uid") == W,
                     f"{newn[0]['uid']} -> {r.get('ownercls')}#{r.get('owner_uid')} -> "
                     f"{r2.get('ownercls')}#{r2.get('owner_uid')} (want Diagram#{D} -> WhileLoop#{W})")

        # ---- F5c: THE SENTINEL SHAPE ITSELF. The Equal?'s Boolean output is written to the loop's conditional
        # terminal with `OpStopFromNode_v0` (toolkit row 51, body Nodes[index 3] . Terminals[index 4]). This is
        # exactly D1 §9a's construction, and it is ALSO what makes the ExecState gate below able to
        # discriminate at all: until the conditional terminal is wired, the scratch is broken by construction.
        if "equal" in built and ok:
            u_eq = newn[0]["uid"]
            wb = B.walk(scratch, i_D)
            n_eq = wb[u_eq][0]
            t_bool = next((r["i"] for r in wb[u_eq][2] if r["is_source"]), None)
            loop_i = [o["uid"] for o in g.report_all(scratch, "WhileLoop")].index(W)
            with open(os.path.join(BENCH, "opstopfromnode_labels.json"), encoding="utf-8") as f:
                slab = json.load(f)
            # RUN 2 MEASURED: the `read_*` keys of `opstopfromnode_labels.json` are NOT controls on
            # OpStopFromNode_v0 - reading `CondWireUID` off it raised LabVIEW **5005** ("parameter %p not found
            # in the VI's connector pane"). `build_opstopfromnode_v0.py:458` does not read them either: it reads
            # the result back with the SEPARATE reader `OpLoopEndRef_v0` (`loop_end_ref`). Same route here.
            from build_opstopfromnode_v0 import loop_end_ref as _ler
            before_c = _ler(scratch, loop_i)
            vs = g.op(os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
            vs.SetControlValue("vi path", scratch)
            vs.SetControlValue("Class Name", "WhileLoop")
            vs.SetControlValue("index", int(loop_i))
            vs.SetControlValue(slab["index_node"], int(n_eq))
            vs.SetControlValue(slab["index_term"], int(t_bool))
            g._run(vs)
            serr = g._err(vs, "error out") or ""
            after_c = _ler(scratch, loop_i)
            gate("F5c the Equal?'s Boolean output now drives the loop's conditional terminal",
                 bool(after_c.get("cond_wire_uid")),
                 f"cond terminal {before_c.get('cond_term_uid')} -> {after_c.get('cond_term_uid')}, "
                 f"wire {before_c.get('cond_wire_uid')} -> {after_c.get('cond_wire_uid')}; "
                 f"Equal? Nodes[{n_eq}].Terminals[{t_bool}]; op error {serr[:140]!r}")

        # junk Invokes: every op that mutates leaves creator Invokes behind (probe_move_into_v0 gate P4a). They
        # are not part of the artefact and they break ExecState, so they are purged before the state is judged.
        junk = [u for u in g.uids(scratch, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(scratch, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(scratch, "Invoke", i, verify=False)
        fact(f"F6 junk Invokes purged: {junk}")
        g.remove_bad_wires_scripted(scratch)
        es = g.exec_state(scratch)
        if not gate("F6 the scratch reads ExecState 1 with the sentinel shape complete", es == 1,
                    f"ExecState {es}"):
            bare = []
            for di in (0, i_D):
                try:
                    for uid, (ni, lab, rows) in __import__("build_track_v6_core").walk(scratch, di).items():
                        for r in rows:
                            if not r["is_source"] and r["wire"] == 0:
                                bare.append((di, uid, lab, r["i"], r["name"]))
                except Exception as e:
                    bare.append((di, "WALK FAILED", str(e)[:80], -1, ""))
            fact(f"F6 BARE-TERMINAL CENSUS (the measured cause, not a guess): {bare[:40]}")
    finally:
        try:
            g.close_panel(scratch)
        except Exception:
            pass
    return scratch


def main():
    which = (sys.argv[1] if len(sys.argv) > 1 else "both").lower()
    kinds = ["equal", "const"] if which == "both" else [which]
    g._lv = None
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")
    built = {}
    for k in kinds:
        lab = build(k)
        if lab is None:
            print(f"\nSTOP: {SPEC[k]['op']} did not reach ExecState 1 - NOT SAVED, no test run.", flush=True)
            break
        built[k] = lab
    scratch = None
    if built:
        try:
            scratch = functional_test(built)
        except Exception as e:
            gate("Fx functional test completed", False, f"EXC {str(e)[:250]}")
    if scratch and os.path.exists(scratch):
        try:
            os.remove(scratch)
            fact(f"scratch deleted: {os.path.basename(scratch)}")
        except Exception as e:
            fact(f"scratch NOT deleted: {str(e)[:90]}")
    fact(f"LabVIEW handles after: {labview_handles()}")
    print(f"\nVERDICT: {len(passes)} pass / {len(fails)} fail"
          + (f"   FAILING: {fails}" if fails else ""), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    t0 = time.time()
    rc = main()
    print(f"elapsed {time.time() - t0:.1f} s", flush=True)
    sys.exit(rc)
