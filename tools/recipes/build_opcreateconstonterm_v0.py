r"""build_opcreateconstonterm_v0.py - `OpCreateConstOnTerm_v0.vi`: invoke **`Terminal.Create Constant` 6349C00**
on `WhileLoop[i].Diagram.Nodes[n].Terminals[t]`, i.e. on a terminal of a node that lives on a loop's BODY
(nested) diagram, so the constant arrives already TYPED and already WIRED to that sink.

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_opcreateconstonterm_v0.log \
        -- py -u tools/recipes/build_opcreateconstonterm_v0.py

WHY: `docs/d1-build-plan.md` §11j (judgement, 2026-09-17) named this as the THIRD and last op of the narrow
cycle-15 freeze lift, over option (i) (a fused `Create Constant.vi` + `Terminal.Connect Wire` op). §11i states the
wall it answers: `OpCreateConst_v0` (BUILT, 23/0) places a constant on a named subdiagram but **cannot connect it**
to `Equal?`'s `y` - the creator's `Terminal` output refnum dies with its op's dataflow and a `Constant` is a
GObject, not a `Node`, so `Get Outputs` cannot reach it.

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md), and what is taken from each:
  * `OpStopFromNode_v0.vi` - BUILT and FUNCTIONAL (`tools/bench/build_opstopfromnode_v0_run3.log`,
    `build_opsentinel_ops_run3.log` F5c). It ALREADY CONTAINS the entire front half this op needs:
        Traverse(`WhileLoop`)[index] -> `To More Specific Class`#683 -> PN `VI Server:Loop`[`Diagram` 6361401]
        -> PN `VI Server:AbstractDiagram`[`Nodes[]` 6375809] -> IndexArray(`index 3`)
        -> PN `VI Server:Node`[`Terms[]` 6359000] -> IndexArray(`index 4`)
    So this op is that file COPIED, with its one `Invoke Terminal[Connect Wire 6349C03]` replaced by
    `Invoke Terminal[Create Constant 6349C00]`. Nothing is re-derived.
  * `gscript.create_control` / `create_indicator` (6349C01 / 6349C02) - the SIBLING methods, exercised. Their
    ladder is TOP-LEVEL only (`docs/NAMES.md:460-461`), which is exactly why the body-node ladder above is needed
    and why `create_control` is not simply reused.
  * `gscript.build_invoke` / `build_property` / `create_control` / `wire` / `save` / `set_auto_error_handling`.
  * `OpConstValueN_v1.vi` (`docs/toolkit-capabilities.md:47`) - the READER for a numeric constant's value,
    `Representation` and the wire it drives. Used by the functional test; NOT rebuilt.
  * `OpCreateEqual_v0` / `OpCreateConst_v0` - the two ops of §11g.1. Not used by this op; `OpCreateConst_v0`
    remains the way to place an UNWIRED constant with a chosen value.
  * `docs/vi-server-ids.json:69` registers `Terminal.Create Constant` = **6349C00**. NOTHING in this project has
    ever invoked it, so its PARAMETER LIST IS UNMEASURED - W4 censuses the created Invoke node's own terminals and
    prints every one before anything is wired. No parameter is assumed.

PREDICTION CONTRACT (a machine checks every line; the build stops at the first miss and saves nothing on a miss)
 W0  donor `OpStopFromNode_v0.vi` present and ExecState 1.
 W1  the copy opens ExecState 1 and holds EXACTLY ONE `Invoke` (the Connect Wire) and the two IndexArrays that
     `index 3` / `index 4` drive.
 W2  that one Invoke is DELETED; ExecState is still 1 afterwards (its `error out` indicator simply goes unwired,
     and a source that loses a sink cannot break a VI).
 W3  `Invoke VI Server:Terminal [6349C00]` created - exactly one new `Invoke`.
 W4  ITS TERMINALS ARE CENSUSED AND PRINTED (the measurement this op exists to make), then `reference` is wired
     from the term IndexArray's `element`, verified by the SAME wire uid on both ends.
 W5  every REMAINING required input of the invoke gets a front-panel control (the `build_opcreator.py` probe
     loop). Reported, not assumed: which ones there were.
 W6  IF the census showed a created-object OUTPUT, a `VI Server:Constant`[`Value` 634AC00 **write**] property node
     is added and fed from a VARIANT control, so the op can also SET the value. This is ATTEMPTED, measured and
     REVERTED if it breaks the op - `Constant.Value`'s writability through this fleet's property-node route is
     unmeasured (`docs/NAMES.md:911` measures only the READ direction, and only for StringConstant).
 W7  ExecState 1 -> saved under claudeDev; labels JSON written.

 FUNCTIONAL TEST on a scratch copy of EMPTY_v0.vi (unique name per run, DELETED in the same run):
 T1  one While loop on the top-level diagram -> WhileLoop W, body Diagram D at Traverse index i_D.
 T2  a node with a BARE NUMERIC input is dropped INSIDE the body (`Error Cluster From Error Code.vi`, whose
     `error code` is I32; `drop_subvi` into a body diagram is proven - `build_opstopfromnode_v0.py` T2).
 T3  the op runs on that terminal: exactly ONE new `Constant`-family object; the node's terminal goes from
     wire 0 to a NON-ZERO wire; `ControlTerminal` count UNCHANGED (no panel object is created - D1's S4s gate).
 T4  owner chain of the new constant: uid -> `Diagram` D -> `WhileLoop` W (`OpOwnerChain_v1`, the same reader
     the sentinel ops are gated with).
 T5  the created object's CLASS and its VALUE read back with `OpConstValueN_v1`. **The value gate is -1 only if
     W6 succeeded**; otherwise the value is REPORTED and the gate is the wiring, not the literal - stating which
     is which instead of pretending.
 T6  `OpStopFromNode_v0` then drives the loop's conditional terminal from that node's `error out` (LabVIEW
     accepts an error cluster there - Stop if Error), and the scratch reads **ExecState 1**: the whole D1 §9a
     shape, end to end, with a wired literal.
 T7  scratch deleted; donor md5 unchanged; handles before/after.

FAILURE BUDGET 2 (CLAUDE.md §3). No repair pass inside the run.
No original is touched; nothing outside `user.lib\claudeDev` is written.
"""
import hashlib
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g                                      # noqa: E402
import build_track_v6_core as B                          # noqa: E402
from bench_prep import labview_handles                   # noqa: E402
from build_opownerchain_v1 import read_owner             # noqa: E402
from build_opownerchain_v1 import OP as OP_OWNER         # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpCreateConstOnTerm_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
BENCH = os.path.join(ROOT, "tools", "bench")
STOP_LABELS = os.path.join(BENCH, "opstopfromnode_labels.json")
OWNER_LABELS = os.path.join(BENCH, "opwiresource_v5_labels.json")
CONSTN_LABELS = os.path.join(BENCH, "opconstvaluen_v1_labels.json")
MAP_OUT = os.path.join(BENCH, "opcreateconstonterm_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_constonterm_{STAMP}.vi")
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
M_CREATE_CONST = "6349C00"
P_CONST_VALUE = "634AC00"
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


def cls_of(uid, w):
    lab = (w[uid][1] or "")
    if lab == "Property Node":
        return "Property"
    if lab == "Index Array":
        return "IndexArray"
    if lab == "Invoke Node":
        return "Invoke"
    return "SubVI" if lab.endswith(".vi") else "Function"


def idx(target, cls, uid):
    return [o["uid"] for o in g.report_all(target, cls)].index(uid)


def connect(src_uid, src_name, dst_uid, dst_name, branch=False, tag=""):
    """Wire by name, verified by the SAME wire uid on BOTH ends (build_opstopfromnode_v0.connect verbatim)."""
    w = walk(OP, 0)
    g.wire(OP, cls_of(src_uid, w), idx(OP, cls_of(src_uid, w), src_uid), src_name,
           cls_of(dst_uid, w), idx(OP, cls_of(dst_uid, w), dst_uid), dst_name, branch=branch)
    w = walk(OP, 0)
    a = (term(w[src_uid][2], src_name, True) or {}).get("wire")
    b = (term(w[dst_uid][2], dst_name, False) or {}).get("wire")
    ok = bool(a) and a == b
    print(f"      {tag}{src_name!r} -> {dst_name!r}: wire {a} / {b} {'OK' if ok else 'MISMATCH'}", flush=True)
    if not ok:
        raise RuntimeError(f"wire {src_name!r}->{dst_name!r} not on both ends ({a} vs {b})")
    return a


def owner_of(target, uid):
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


def counts(target):
    return {c: g.count(target, c) for c in ("Node", "Property", "Wire", "ControlTerminal", "Invoke",
                                            "IndexArray", "Constant")}


# ============================================================================== BUILD
def build():
    print("\n=== W0: the donor", flush=True)
    if not gate("W0a OpStopFromNode_v0.vi on disk", os.path.exists(SRC), SRC):
        return None
    donor_md5 = md5(SRC)
    g.open_panel(SRC)
    es = g.exec_state(SRC)
    gate("W0 donor ExecState 1", es == 1, f"ExecState {es}")
    g.close_panel(SRC)

    print("\n=== W1: the copy", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    c0 = counts(OP)
    fact(f"copy census: {c0}, ExecState {g.exec_state(OP)}")
    with open(STOP_LABELS, encoding="utf-8") as f:
        slab = json.load(f)
    pw = {r["label"]: r["wire"] for r in g.panel_wiring(OP)}
    w_node_i, w_term_i = pw.get(slab["index_node"]), pw.get(slab["index_term"])
    wk = walk(OP, 0)
    ia_node = next((u for u, (n, l, rows) in wk.items()
                    if l == "Index Array" and any(r["wire"] == w_node_i for r in rows)), None)
    ia_term = next((u for u, (n, l, rows) in wk.items()
                    if l == "Index Array" and any(r["wire"] == w_term_i for r in rows)), None)
    invokes = [u for u, (n, l, rows) in wk.items() if l == "Invoke Node"]
    if not gate("W1 the copy holds exactly one Invoke and both body-ladder Index Arrays",
                len(invokes) == 1 and ia_node and ia_term and g.exec_state(OP) == 1,
                f"Invokes {invokes}; IA(node) #{ia_node} via w{w_node_i}; IA(term) #{ia_term} via w{w_term_i}; "
                f"ExecState {g.exec_state(OP)}"):
        return None
    u_old_inv = invokes[0]

    print("\n=== W2: delete the Connect Wire invoke", flush=True)
    g.delete_object(OP, "Invoke", idx(OP, "Invoke", u_old_inv), verify=False)
    g.remove_bad_wires_scripted(OP)
    es = g.exec_state(OP)
    if not gate("W2 the Connect Wire invoke is gone and the op still compiles",
                g.count(OP, "Invoke") == 0 and es == 1, f"Invoke {g.count(OP, 'Invoke')}, ExecState {es}"):
        return None

    print("\n=== W3/W4: Invoke Terminal[Create Constant 6349C00]", flush=True)
    r = g.build_invoke(OP, "VI Server:Terminal", M_CREATE_CONST, (1500, 1600))
    inv = r[-1]["uid"] if r else None
    if not gate("W3 Invoke Terminal[6349C00] created", bool(inv) and g.count(OP, "Invoke") == 1, f"uid {inv}"):
        return None
    wk = walk(OP, 0)
    rows = wk[inv][2]
    census = [(x["i"], x["name"], "OUT" if x["is_source"] else "IN") for x in rows]
    fact(f"W4 6349C00 TERMINAL CENSUS (never measured before): {census}")
    connect(ia_term, "element", inv, "reference", tag="W4 ")

    # --- W5: EVERY parameter input of the invoke gets a control - FORCED, not probe-gated.
    # PRIOR-ART A3 (`contradicted`, archive/peer/2026-09-17-priorart-priorart-createconst-term.md): two NI-sourced
    # records in our own files say 6349C00 takes an **optional `Value` input**
    # (`archive/peer/2026-09-06-fp-control-creation-scripting-routes.md:36`, quoted again at
    # `…priorart-d1-sentinel-ops.md:294`). An OPTIONAL input is invisible to a probe loop that stops at
    # ExecState 1 - which is exactly the hole run 1 of `build_opsentinel_ops.py` fell into (`:327-330`: `Value`
    # never got a control, so the op could only create DEFAULT-valued constants). So every parameter input is
    # given a control unconditionally, and the census above is what says which ones those are.
    print("\n=== W5: a control for EVERY parameter input of the invoke (A3: expect an optional `Value`)",
          flush=True)
    made, ctl_by_term = [], {}
    wk = walk(OP, 0)
    params = [x for x in wk[inv][2]
              if not x["is_source"] and x["name"] not in ("reference", "error in (no error)") and x["wire"] == 0]
    fact(f"W5 parameter inputs to satisfy: {[(x['i'], x['name']) for x in params]}")
    for x in params:
        wk = walk(OP, 0)
        n_inv = wk[inv][0]
        try:
            new, lab = g.create_control(OP, n_inv, x["i"])
        except Exception as e:
            print(f"   t{x['i']} ({x['name']!r}): EXC {str(e)[:110]}", flush=True)
            continue
        if new and lab:
            made.append((x["i"], x["name"], lab))
            ctl_by_term[x["name"] or f"t{x['i']}"] = lab
            print(f"   t{x['i']} ({x['name']!r}): control {lab!r} -> ExecState {g.exec_state(OP)}", flush=True)
        else:
            print(f"   t{x['i']} ({x['name']!r}): no control created (optional-and-declined or already wired)",
                  flush=True)
    es = g.exec_state(OP)
    if es != 1:
        g.remove_bad_wires_scripted(OP)
        es = g.exec_state(OP)
    value_ctl = next((lab for nm, lab in ctl_by_term.items() if nm.strip().lower() == "value"), None)
    gate("W5 the invoke's parameter inputs all carry controls", es == 1,
         f"controls {made}; value control {value_ctl!r}; ExecState {es}")

    # --- W6: BRING THE ORACLE OUT. Prior-art B4 (`already-measured`): a set difference over the target's objects
    # is not the authoritative creation oracle - `archive/peer/2026-09-15-opwiresource-fail1-uid-indicator-not-
    # created.md:26-27,:53,:55` ("label-set cardinality is not a valid creation-success oracle … the returned
    # reference and error cluster are the authoritative experiment"). So the invoke's created-object reference is
    # turned into a UID through `GObject.UID` 632A813 and reported on an indicator, and its `error out` gets one
    # too. A zero-object run then says WHY instead of needing a diagnosis by inference.
    print("\n=== W6: the created-object reference and the error, brought out (prior-art B4)", flush=True)
    uid_ind = err_ind = None
    wk = walk(OP, 0)
    outs = [x for x in wk[inv][2] if x["is_source"] and x["name"] not in ("reference out", "error out")]
    fact(f"W6 created-object outputs on the invoke: {[(x['i'], x['name']) for x in outs]}")
    snapshot = counts(OP)
    try:
        if outs:
            pu = g.build_property(OP, "VI Server:GObject", [("632A813", False)], (1950, 1600))
            u_pu = pu[-1]["uid"]
            connect(inv, outs[0]["name"], u_pu, "reference", tag="W6 ")
            wk = walk(OP, 0)
            t_uid = next((x["i"] for x in wk[u_pu][2] if x["is_source"] and x["name"] not in
                          ("reference out", "error out")), None)
            rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
            g.create_indicator(OP, wk[u_pu][0], t_uid)
            rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
            new = [r for u, r in rows1.items() if u not in rows0]
            uid_ind = new[0]["label"] if len(new) == 1 else None
        wk = walk(OP, 0)
        t_err = next((x["i"] for x in wk[inv][2] if x["is_source"] and x["name"] == "error out"), None)
        if t_err is not None:
            rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
            g.create_indicator(OP, wk[inv][0], t_err)
            rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
            new = [r for u, r in rows1.items() if u not in rows0]
            err_ind = new[0]["label"] if len(new) == 1 else None
        es = g.exec_state(OP)
        if es != 1:
            g.remove_bad_wires_scripted(OP)
            es = g.exec_state(OP)
        if es != 1:
            raise RuntimeError(f"the oracle chain broke the op (ExecState {es})")
        gate("W6 the op returns the created object's UID and the invoke's own error", bool(err_ind),
             f"uid indicator {uid_ind!r}, error indicator {err_ind!r}")
    except Exception as e:
        fact(f"W6 oracle chain REJECTED: {str(e)[:220]} (census before {snapshot})")
        g.remove_bad_wires_scripted(OP)
        gate("W6 the op returns the created object's UID and the invoke's own error", False,
             f"ExecState {g.exec_state(OP)} - the caller falls back to a uid set difference")

    print("\n=== W7: ExecState and save", flush=True)
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:
        fact(f"set_auto_error_handling failed ({str(e)[:60]})")
    es = g.exec_state(OP)
    if not gate("W7 ExecState 1 - the op is runnable", es == 1, f"ExecState {es}"):
        fact("NOT SAVED: a broken op is never written to disk")
        return None
    g.save(OP)
    labels = {"vi_path": "vi path", "loop_class": slab["loop_class"], "loop_index": slab["loop_index"],
              "index_node": slab["index_node"], "index_term": slab["index_term"], "value_ctl": value_ctl,
              "method": M_CREATE_CONST, "census": census, "param_controls": made, "ctl_by_term": ctl_by_term,
              "uid_ind": uid_ind, "err_ind": err_ind}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact(f"saved {OP} ({os.path.getsize(OP)} bytes); labels -> {MAP_OUT}")
    gate("W7b donor OpStopFromNode_v0.vi md5 unchanged", md5(SRC) == donor_md5, donor_md5)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    return labels


# ============================================================================== the wrapper
def create_const_on_term(target, loop_index, node_index, term_index, labels, value=None):
    """Run OpCreateConstOnTerm_v0 on `target`. Returns {err, inv_err, created_uid} - prior-art B4's oracle
    (the invoke's own error cluster and the created object's UID), not a set difference."""
    g.ensure_loaded(target)
    vi = g.op(OP)
    if labels.get("uid_ind"):
        vi.SetControlValue(labels["uid_ind"], 0)
    if labels.get("err_ind"):
        vi.SetControlValue(labels["err_ind"], (False, 0, ""))
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(labels["loop_class"], "WhileLoop")
    vi.SetControlValue(labels["loop_index"], int(loop_index))
    vi.SetControlValue(labels["index_node"], int(node_index))
    vi.SetControlValue(labels["index_term"], int(term_index))
    if labels.get("value_ctl") and value is not None:
        vi.SetControlValue(labels["value_ctl"], value)
    g._run(vi)
    out = dict(err=g._err(vi, "error out") or "", inv_err="", created_uid=None)
    if labels.get("err_ind"):
        out["inv_err"] = g._err(vi, labels["err_ind"]) or ""
    if labels.get("uid_ind"):
        try:
            out["created_uid"] = int(vi.GetControlValue(labels["uid_ind"]))
        except Exception:
            pass
    return out


def read_const(target, uid):
    """The created constant's value/Representation/text through OpConstValueN_v1 (toolkit row 47), addressed by
    its Traverse index among `DigitalNumericConstant` (or `Constant` if it is not numeric)."""
    with open(CONSTN_LABELS, encoding="utf-8") as f:
        lab = json.load(f)
    for cls in ("DigitalNumericConstant", "Constant"):
        order = [o["uid"] for o in g.report_all(target, cls)]
        if uid not in order:
            continue
        vi = g.op(os.path.join(g.CLAUDEDEV, "OpConstValueN_v1.vi"))
        for k in ("text", "hex"):
            vi.SetControlValue(lab[k], "POISON")
        vi.SetControlValue(lab["u8"], [])
        vi.SetControlValue(lab["wire"], -1)
        vi.SetControlValue("UID", 0)
        vi.SetControlValue(lab["size"], False)
        vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", cls)
        vi.SetControlValue("index", order.index(uid))
        err = ""
        try:
            g._run(vi)
            err = g._err(vi, "error out") or ""
        except Exception as e:
            err = f"EXC {str(e)[:90]}"
        return dict(cls=cls, uid_back=int(vi.GetControlValue("UID")), text=vi.GetControlValue(lab["text"]),
                    repr=vi.GetControlValue(lab["repr"]), wire=int(vi.GetControlValue(lab["wire"])), err=err)
    return dict(cls=None, err="uid not found among DigitalNumericConstant / Constant")


# ============================================================================== FUNCTIONAL TEST
def test(labels):
    print("\n=== T: FUNCTIONAL test on a scratch copy of EMPTY_v0", flush=True)
    if not gate("T0a EMPTY_v0.vi present", os.path.exists(EMPTY), EMPTY):
        return
    if not gate("T0b the numeric-input donor subVI exists", os.path.exists(NUMVI), NUMVI):
        return
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copyfile(EMPTY, SCRATCH)
    time.sleep(0.3)
    g.report_all(SCRATCH, "SubVI")
    g.open_panel(SCRATCH)
    time.sleep(0.6)
    inv0 = g.uids(SCRATCH, "Invoke")
    try:
        wl0, dg0 = g.uids(SCRATCH, "WhileLoop"), g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (300, 300))
        nwl, ndg = g.new_since(SCRATCH, "WhileLoop", wl0), g.new_since(SCRATCH, "Diagram", dg0)
        if not gate("T1 one While loop created", len(nwl) == 1 and len(ndg) == 1, f"{nwl} {ndg}"):
            return
        W, D = nwl[0]["uid"], ndg[0]["uid"]
        i_D = ndg[0].get("i", [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(D))
        fact(f"scratch: WhileLoop #{W}, body Diagram #{D} at Traverse index {i_D}")

        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, i_D, (80, 80))
        nsv = g.new_since(SCRATCH, "SubVI", sv0)
        if not gate("T2 the numeric-input node is inside the loop body", len(nsv) == 1, f"{nsv}"):
            return
        u_node = nsv[0]["uid"]
        wb = B.walk(SCRATCH, i_D)
        n_i, rows = wb[u_node][0], wb[u_node][2]
        bare_in = [(r["i"], r["name"]) for r in rows if not r["is_source"] and r["wire"] == 0 and r["name"]]
        outs = [(r["i"], r["name"]) for r in rows if r["is_source"] and r["name"]]
        fact(f"body node #{u_node} (body Nodes[{n_i}]): bare inputs {bare_in}; outputs {outs}")
        t_num = next((i for i, n in bare_in if "code" in n.lower()), bare_in[0][0] if bare_in else None)
        if not gate("T2b a bare input terminal was found to build the constant on", t_num is not None,
                    f"bare inputs {bare_in}"):
            return

        ct0, c0 = g.count(SCRATCH, "ControlTerminal"), g.uids(SCRATCH, "Constant")
        loop_i = [o["uid"] for o in g.report_all(SCRATCH, "WhileLoop")].index(W)
        res = create_const_on_term(SCRATCH, loop_i, n_i, t_num, labels,
                                   value=-1.0 if labels.get("value_ctl") else None)
        newc = g.new_since(SCRATCH, "Constant", c0)
        fact(f"op oracle (prior-art B4): error out {res['err'][:120]!r}; invoke error {res['inv_err'][:120]!r}; "
             f"created UID {res['created_uid']}")
        gate("T3o the invoke reported no error of its own", not res["inv_err"], res["inv_err"][:160])
        ok = gate("T3 exactly one new Constant-family object", len(newc) == 1,
                  f"new {[(o['uid'], o.get('class'), o.get('pos')) for o in newc]}")
        wb2 = B.walk(SCRATCH, i_D)
        w_after = next((r["wire"] for r in wb2[u_node][2] if r["i"] == t_num), 0)
        gate("T3b the target terminal is now WIRED (wire 0 -> non-zero)", bool(w_after),
             f"terminal t{t_num} wire 0 -> {w_after}")
        gate("T3c no panel object was created (D1 S4s: ControlTerminal unchanged)",
             g.count(SCRATCH, "ControlTerminal") == ct0, f"{ct0} -> {g.count(SCRATCH, 'ControlTerminal')}")
        if ok:
            r1 = owner_of(SCRATCH, newc[0]["uid"])
            r2 = owner_of(SCRATCH, r1["owner_uid"]) if r1.get("owner_uid") else {}
            gate("T4 owner chain: constant -> body Diagram -> the new WhileLoop",
                 r1.get("owner_uid") == D and r2.get("owner_uid") == W,
                 f"{newc[0]['uid']} -> {r1.get('ownercls')}#{r1.get('owner_uid')} -> "
                 f"{r2.get('ownercls')}#{r2.get('owner_uid')} (want Diagram#{D} -> WhileLoop#{W})")
            # B4' (prior-art): the created object's CLASS is the measured discriminator between "the value is
            # wrong" and "the reader is pointed at the wrong class" (docs/NAMES.md:911-919). It is asserted
            # BEFORE the value gate, and it is already free - read_owner echoes the object's own class.
            cls_echo = r1.get("cls_back") or newc[0].get("class")
            gate("T5a the created object is a TYPED numeric constant (class echo, before any value read)",
                 str(cls_echo) == "DigitalNumericConstant",
                 f"class echo {cls_echo!r} (the VARIANT route of OpCreateConst_v0 produced the base "
                 f"'Constant' - build_opsentinel_ops_run3.log:38)")
            rc = read_const(SCRATCH, newc[0]["uid"])
            fact(f"T5 created constant #{newc[0]['uid']}: class {cls_echo}, OpConstValueN_v1 -> {rc}")
            if labels.get("value_ctl"):
                gate("T5 the constant carries -1", str(rc.get("text", "")).strip() in ("-1", "-1.00", "-1.0"),
                     f"text {rc.get('text')!r}, Representation {rc.get('repr')!r}, err {rc.get('err', '')[:80]!r}")
            else:
                fact("T5 VALUE NOT GATED: 6349C00 exposed no `Value` parameter, so the op creates the SINK'S "
                     "DEFAULT value. The literal -1 is therefore still open - reported, not pretended.")

        # --- T5b: prior-art A4 - the one-run readback STATUS/§11i:750-753 already scheduled as material work:
        # does `OpCreateConst_v0`'s VARIANT-written constant actually carry -1? Same scratch, same reader, no
        # extra run. Reported, not gated: it judges a DIFFERENT op.
        try:
            with open(os.path.join(BENCH, "opcreate_const_labels.json"), encoding="utf-8") as f:
                clab = json.load(f)
            import build_opsentinel_ops as S
            c1 = g.uids(SCRATCH, "Constant")
            cb = clab.get("ctl_by_term", {})
            vals = {}
            if cb.get("Type"):
                vals[cb["Type"]] = 0.0
            if cb.get("Value"):
                vals[cb["Value"]] = -1.0
            e2 = S.create_node("const", clab, SCRATCH, i_D, (400, 300), values=vals)
            nc2 = g.new_since(SCRATCH, "Constant", c1)
            rc2 = read_const(SCRATCH, nc2[0]["uid"]) if len(nc2) == 1 else {}
            fact(f"T5b A4/§11i:750-753 ANSWERED - OpCreateConst_v0(Type=DBL, Value=-1) -> "
                 f"{[(o['uid'], o.get('class')) for o in nc2]}, OpConstValueN_v1 {rc2}, op error {e2!r}")
        except Exception as e:
            fact(f"T5b A4 readback not completed ({str(e)[:140]})")

        # T6: the whole D1 §9a shape - the body node's output drives the loop's conditional terminal
        t_out = next((i for i, n in outs if n == "error out"), outs[0][0] if outs else None)
        if t_out is not None:
            with open(STOP_LABELS, encoding="utf-8") as f:
                slab = json.load(f)
            vs = g.op(os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi"))
            vs.SetControlValue("vi path", SCRATCH)
            vs.SetControlValue("Class Name", "WhileLoop")
            vs.SetControlValue("index", int(loop_i))
            vs.SetControlValue(slab["index_node"], int(n_i))
            vs.SetControlValue(slab["index_term"], int(t_out))
            g._run(vs)
            fact(f"T6 OpStopFromNode_v0 error out: {(g._err(vs, 'error out') or '')[:140]!r}")
        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        g.remove_bad_wires_scripted(SCRATCH)
        es = g.exec_state(SCRATCH)
        if not gate("T6 the scratch reads ExecState 1 with the wired literal in place", es == 1,
                    f"ExecState {es}; junk Invokes purged {junk}"):
            bare = []
            for di in (0, i_D):
                try:
                    for uid, (ni, lab, rr) in B.walk(SCRATCH, di).items():
                        for r in rr:
                            if not r["is_source"] and r["wire"] == 0:
                                bare.append((di, uid, lab, r["i"], r["name"]))
                except Exception as e:
                    bare.append((di, "WALK FAILED", str(e)[:70], -1, ""))
            fact(f"T6 BARE-TERMINAL CENSUS (the measured cause, not a guess): {bare[:40]}")
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            os.remove(SCRATCH)
            fact(f"scratch deleted: {os.path.basename(SCRATCH)}")
        except Exception as e:
            fact(f"scratch NOT deleted ({str(e)[:60]})")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")
    try:
        labels = build()
        if labels:
            test(labels)
    except Exception as e:
        gate("Wx build/test completed without an unhandled exception", False, f"EXC {str(e)[:250]}")
    finally:
        try:
            g.close_panel(OP)
        except Exception:
            pass
        g._lv = None
    fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== build_opcreateconstonterm_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
