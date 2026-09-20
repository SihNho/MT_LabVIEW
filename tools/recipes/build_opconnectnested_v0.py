r"""build_opconnectnested_v0.py - `OpConnectNested_v0.vi`: `Terminal.Connect Wire` **6349C03** with BOTH ends
addressed by INDEX on NESTED diagrams (`docs/d1-build-plan.md` §11m, the FOURTH and last op of the freeze lift).

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_opconnectnested_v0.log \
        -- py -u tools/recipes/build_opconnectnested_v0.py

WHY: `build_d1_v0_run7.log` - of 66 routable re-wire rows, 7 FAILED (5001 out of `Get Controls.vi` /
`Get Outputs.vi`) and 24 had NO ROUTE, every one of them because an end has **no name**. `gscript.wire` /
`wire_control` are name-addressed; `connect_terminals` (`gscript.py:2202`) takes BOTH ends from
`VI.Block Diagram -> Nodes[]` (top level on both sides) and `connect2` (`:2428`) takes a Traverse-"Diagram" sink
with a **top-level** source. Nothing addresses two ends by index on nested diagrams.

DONOR - CHANGED FROM THE ONE §11m NAMES, on measurement + the prior-art review
(`archive/peer/2026-09-17-priorart-connect-nested.md`, 6 findings, 0 novel):
  * **A3-i `contradicted`**: §11m says the body is *"`OpStopFromNode_v0`'s body-node ladder … duplicated"* with
    inputs *"(diagram index, node index, terminal index)"*. That ladder is **loop-anchored**, not diagram-indexed -
    `Traverse("WhileLoop")[index] -> To More Specific Class -> Loop.Diagram 6361401 -> …`
    (`build_opcreateconstonterm_v0.py:17-19`; `docs/toolkit-capabilities.md:51`), measured again in
    `tools/bench/diag_connectnested_donors.log` (this session's own census, 6 donors, 6/0). Duplicating it cannot
    express two different diagrams at all.
  * **B3-i `helper-exists`**: the right donor is **`OpConnect2_v0.vi`** (`build_opconnect2.py:3-6`) - it already
    carries the nested SINK ladder `Traverse("Diagram")[index] -> TMSC -> Nodes[][index 2] -> Terms[][index 3]`,
    the `Connect Wire` invoke, AND a complete SOURCE ladder `Nodes[][index 4] -> Terms[][index 5]` whose only
    wrong part is its head, a `VI Server:VI [Block Diagram 23C]` property node. And
    `diag_connectnested_donors.log` line for `OpConnect_v0` shows `Nodes[1]` and `Nodes[8]` **both taking
    `array` = w171** - one `Nodes[]` array feeding two independent Index Arrays, on a shipped VI.
  * **A3-ii `contradicted`**: §11m's *"It resolves all 31 rows"* is refuted by §11L:698 and by the run-7 log -
    16 of the 24 no-route rows print `outer_source (none)`, which is a SOURCE-RESOLUTION gap, not an addressing
    one. This op reaches ~8. Recorded, not argued with; the caller's row count is what the next run measures.

THE ONE THING THAT IS NOT KNOWN UNTIL THE MACHINE SAYS SO, so the build measures it instead of assuming:
`Traverse for GObjects.vi`'s `References` output is an array of **GObject** references, and the source ladder's
head property node is **Diagram**-class. Whether LabVIEW accepts that wire decides which of two ops ships:

  ROUTE A (two INDEPENDENT diagrams - what §11m wants): a SECOND `Index Array` on the same `References` array,
     its `element` into the source `Nodes[]` property node, with its own diagram-index control.
     -> `OpConnectNested_v0(vi, sink_diagram, sink_node, sink_term, src_diagram, src_node, src_term)`.
  ROUTE B (fallback, always type-correct): the sink ladder's `To More Specific Class` output
     (`specific class reference`, already Diagram-typed) BRANCHED into the source `Nodes[]` property node.
     -> `OpConnectNested_v0(vi, diagram, sink_node, sink_term, src_node, src_term)` - both ends on the SAME
        nested diagram. That still resolves every `same-loop … unnamed end` row of run 7.
The build tries A, reads `ExecState`, and falls back to B in the same run. Which one shipped is recorded in
`tools/bench/opconnectnested_labels.json` as `route` and stated in the log - never inferred by the caller.

PREDICTION CONTRACT (a machine checks every line; the build stops at the first miss and saves nothing on a miss)
 W0  donor `OpConnect2_v0.vi` present, ExecState 1; md5 recorded and re-asserted at the end.
 W1  the copy opens ExecState 1 and holds exactly ONE `Invoke` (Connect Wire) and >= 4 `IndexArray`s.
 W2  IDENTIFICATION BY WIRE TOPOLOGY, never by uid: from the invoke's `reference` / `Wire Source` wires back
     through IA(term) -> PN[Terms[]] -> IA(node) -> PN[Nodes[]] -> head. The two heads must differ (one is the
     TMSC chain, one is the `VI[Block Diagram]` property node) or the build stops.
 W3  the `VI[Block Diagram]` head is DELETED; Remove Bad Wires; the source `Nodes[]` PN's `reference` is BARE.
 W4  ROUTE A: one new `IndexArray`, `array` <- Traverse `References` (branch, SAME wire uid on both ends), a new
     front-panel control on its `index`; `element` -> source `Nodes[]` PN `reference`. ExecState read.
 W5  if ExecState != 1: Remove Bad Wires, then ROUTE B (TMSC `specific class reference` -> the same `reference`,
     branch). ExecState read again. One of the two must reach 1 or nothing is saved.
 W6  auto error handling OFF; ExecState 1 -> COM save; labels JSON written; donor md5 unchanged.

 FUNCTIONAL TEST on a scratch copy of `EMPTY_v0.vi` (unique name per run, DELETED in the same run):
 T1  one While loop on the top-level diagram -> body `Diagram` D at Traverse index i_D; two subVIs dropped in it.
 T2  (a) BODY NODE -> BODY NODE on the same nested diagram: the sink terminal goes wire 0 -> non-zero and the
     SAME wire uid appears on both ends (never a count). ExecState reported.
 T3  (b) BODY NODE -> an UNNAMED terminal of a NESTED STRUCTURE: a For loop is created on the top level and
     REPARENTED into the body with `OpMoveIn_v0` (12/0, §2b), so its unnamed count terminal lives on a nested
     diagram; each body-node output is tried until one leaves the VI runnable, and which one is reported.
     ⚠️ LEVEL OF VERIFICATION, stated: the gate is WIRE IDENTITY on an unnamed terminal (that is the new
     capability); a type-incompatible pairing makes a broken wire, which is a LabVIEW type fact, not a failure
     of the op, and is reported as such.
 T4  (c) SOURCE ON A DIFFERENT DIAGRAM from the sink - only expressible if ROUTE A shipped. If ROUTE B shipped
     this is reported as the MEASURED LIMIT of the op, not silently passed (§11m's test (c) is a report, not a
     gate, per the plan's own wording).
 T5  scratch deleted; donor md5 unchanged; handles before/after.

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
import gscript as g                       # noqa: E402
from bench_prep import labview_handles     # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpConnect2_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnectNested_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
BENCH = os.path.join(ROOT, "tools", "bench")
MAP_OUT = os.path.join(BENCH, "opconnectnested_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_connnested_{STAMP}.vi")
BOOLVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Is Path and Not Empty.vi"
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


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


def walk(target, diagram=0, limit=120):
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


def connect(src_uid, src_name, dst_uid, dst_name, branch=False, tag="", target=None):
    """Wire by name, verified by the SAME wire uid on BOTH ends (build_opstopfromnode_v0.connect verbatim)."""
    t = target or OP
    w = walk(t, 0)
    g.wire(t, cls_of(src_uid, w), idx(t, cls_of(src_uid, w), src_uid), src_name,
           cls_of(dst_uid, w), idx(t, cls_of(dst_uid, w), dst_uid), dst_name, branch=branch)
    w = walk(t, 0)
    a = (term(w[src_uid][2], src_name, True) or {}).get("wire")
    b = (term(w[dst_uid][2], dst_name, False) or {}).get("wire")
    ok = bool(a) and a == b
    print(f"      {tag}{src_name!r} -> {dst_name!r}: wire {a} / {b} {'OK' if ok else 'MISMATCH'}", flush=True)
    if not ok:
        raise RuntimeError(f"wire {src_name!r}->{dst_name!r} not on both ends ({a} vs {b})")
    return a


def data_out(rows):
    """The single DATA source terminal of a property node (not `reference out`, not `error out`)."""
    d = [r for r in rows if r["is_source"] and r["name"] not in ("reference out", "error out")]
    return d[0]["name"] if len(d) == 1 else None


def counts(target):
    return {c: g.count(target, c) for c in ("Node", "Property", "Wire", "ControlTerminal", "Invoke",
                                            "IndexArray", "SubVI", "Diagram", "LoopTunnel", "ForLoop")}


# ============================================================================== BUILD
def build():
    print("\n=== W0: the donor OpConnect2_v0.vi", flush=True)
    if not gate("W0a OpConnect2_v0.vi on disk", os.path.exists(SRC), SRC):
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
    w = walk(OP, 0)
    for uid, (n, lab, rows) in w.items():
        print(f"   Nodes[{n:2d}] #{uid:<6} {str(lab)[:38]:<38} "
              f"{[(r['i'], r['name'], 'OUT' if r['is_source'] else 'IN', r['wire']) for r in rows]}", flush=True)
    invokes = [u for u, (n, lab, rows) in w.items() if lab == "Invoke Node"]
    if not gate("W1 the copy is runnable and holds exactly one Invoke",
                len(invokes) == 1 and g.exec_state(OP) == 1 and c0["IndexArray"] >= 4,
                f"Invokes {invokes}, IndexArray {c0['IndexArray']}, ExecState {g.exec_state(OP)}"):
        return None
    inv = invokes[0]

    print("\n=== W2: identification BY WIRE TOPOLOGY (never by uid)", flush=True)

    def by_wire_out(wire, want_label=None):
        """the node whose SOURCE terminal carries `wire`"""
        for u, (n, lab, rows) in w.items():
            if want_label and lab != want_label:
                continue
            for r in rows:
                if r["is_source"] and r["wire"] == wire and wire:
                    return u, r["name"]
        return None, None

    def ladder_from(sink_wire, tag):
        """IA(term) -> PN[Terms[]] -> IA(node) -> PN[Nodes[]] -> head-wire, walking back from the invoke."""
        ia_t, _ = by_wire_out(sink_wire, "Index Array")
        if ia_t is None:
            raise RuntimeError(f"{tag}: no Index Array drives wire {sink_wire}")
        w_arr = term(w[ia_t][2], "array", False)["wire"]
        pn_t, _ = by_wire_out(w_arr, "Property Node")
        w_ref_t = term(w[pn_t][2], "reference", False)["wire"]
        ia_n, _ = by_wire_out(w_ref_t, "Index Array")
        w_arr_n = term(w[ia_n][2], "array", False)["wire"]
        pn_n, _ = by_wire_out(w_arr_n, "Property Node")
        w_head = term(w[pn_n][2], "reference", False)["wire"]
        head_uid, head_name = by_wire_out(w_head)
        print(f"   {tag}: IA(term) #{ia_t} <- PN[{data_out(w[pn_t][2])}] #{pn_t} <- IA(node) #{ia_n} "
              f"<- PN[{data_out(w[pn_n][2])}] #{pn_n} <- #{head_uid} {head_name!r} (w{w_head})", flush=True)
        return dict(ia_t=ia_t, pn_t=pn_t, ia_n=ia_n, pn_n=pn_n, head=head_uid, head_name=head_name)

    w_ref = term(w[inv][2], "reference", False)["wire"]
    w_src = term(w[inv][2], "Wire Source", False)["wire"]
    sink = ladder_from(w_ref, "SINK  ")
    src = ladder_from(w_src, "SOURCE")
    tmsc = next((u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)), None)
    trav = next((u for u, (n, lab, rows) in w.items() if term(rows, "References", True)), None)
    if not gate("W2 the two ladders are distinct and the TMSC + Traverse are present",
                sink["ia_t"] != src["ia_t"] and sink["head"] != src["head"] and tmsc and trav,
                f"sink head #{sink['head']} {sink['head_name']!r}; source head #{src['head']} "
                f"{src['head_name']!r}; TMSC #{tmsc}; Traverse #{trav}"):
        return None
    if not gate("W2b the SOURCE head is the VI[Block Diagram] property node (the one part to replace)",
                (w[src["head"]][1] == "Property Node") and src["head_name"] == "Diagram",
                f"#{src['head']} label {w[src['head']][1]!r} terminal {src['head_name']!r}"):
        return None

    print("\n=== W3: delete the VI[Block Diagram] head", flush=True)
    g.delete_object(OP, "Property", idx(OP, "Property", src["head"]))
    g.remove_bad_wires_scripted(OP)
    w = walk(OP, 0)
    bare = term(w[src["pn_n"]][2], "reference", False)
    es = g.exec_state(OP)
    if not gate("W3 the source Nodes[] property node's `reference` is now BARE",
                bool(bare) and bare["wire"] == 0, f"wire {bare and bare['wire']}, ExecState {es}"):
        return None

    # ---------------------------------------------------------------- W4: ROUTE A is MEASURED, and NOT repeated
    # RUN 1 (2026-09-17 11:2x, `tools/bench/build_opconnectnested_v0_run1.log`) executed ROUTE A against LabVIEW
    # and it FAILED, exactly as the type analysis said it would:
    #     "W4 source-diagram index control: 'index 6'"
    #     "W4 ROUTE A wired: ExecState 0 (GObject element -> Diagram-class property node)"
    # `Traverse for GObjects.vi`'s `References` is an array of **GObject** references; a `VI Server:AbstractDiagram`
    # property node's `reference` input is Diagram-class, and GObject -> Diagram is a DOWNCAST, which LabVIEW makes
    # a broken wire. The prior-art review's B3-i ("the swap needed here is one node: a second Index Array on the
    # Traverse References array") is therefore REFUTED BY MEASUREMENT on this one point - recorded in the archive.
    # It is NOT re-run here: a second attempt at a measured-impossible step is the grinding CLAUDE.md forbids.
    #
    # CONSEQUENCE, stated plainly because it is the session's main finding: two INDEPENDENT nested diagrams need a
    # SECOND `To More Specific Class`, and the fleet cannot make one - `New VI Object` creates no primitive
    # (`vi-scripting.md:308,:465`, the 0-399 style sweep created nothing), and the only primitive copier
    # `copy_by_index` would land it with an unwirable `target class` (a class-specifier **Constant** is a GObject,
    # not a Node, so no wire creator in this fleet reaches its output - the same wall §11i recorded).
    route, diag2_ctl = None, None
    fact("W4 ROUTE A: MEASURED IMPOSSIBLE in run 1 (GObject element -> Diagram-class property node = ExecState 0)"
         " - not repeated. The op ships as ROUTE B: both ends by index on the SAME nested diagram.")

    print("\n=== W5: ROUTE B - branch the sink ladder's already-cast Diagram reference", flush=True)
    # The run-1 defect this repairs: `remove_bad_wires_scripted` left the broken w1055 ON the source `reference`,
    # and the fallback then declined to wire "over" it, so ROUTE B was never actually attempted. The wire is now
    # DELETED explicitly by its Traverse index (`gscript.delete_object`, verify=True) and the bareness is GATED.
    w = walk(OP, 0)
    b = term(w[src["pn_n"]][2], "reference", False)
    if b and b["wire"]:
        order = [o["uid"] for o in g.report_all(OP, "Wire")]
        if b["wire"] in order:
            g.delete_object(OP, "Wire", order.index(b["wire"]))
            fact(f"W5a deleted the stale wire w{b['wire']} on the source `reference`")
        g.remove_bad_wires_scripted(OP)
        w = walk(OP, 0)
        b = term(w[src["pn_n"]][2], "reference", False)
    if not gate("W5a the source `reference` is BARE before ROUTE B wires it",
                bool(b) and b["wire"] == 0, f"wire {b and b['wire']}"):
        return None
    connect(tmsc, "specific class reference", src["pn_n"], "reference", branch=True, tag="W5 ")
    es = g.exec_state(OP)
    if es != 1:
        g.remove_bad_wires_scripted(OP)
        es = g.exec_state(OP)
    if es == 1:
        route = "B"
    fact(f"W5 ROUTE B (both ends on the SAME nested diagram): ExecState {es}")

    if not gate("W5 one of the two routes leaves the op RUNNABLE", route in ("A", "B"),
                f"route {route!r}, ExecState {g.exec_state(OP)}"):
        fact("NOT SAVED: a broken op is never written to disk")
        return None

    print("\n=== W6: save", flush=True)
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:
        fact(f"set_auto_error_handling failed ({str(e)[:60]})")
    es = g.exec_state(OP)
    if not gate("W6 ExecState 1 - the op is runnable", es == 1, f"ExecState {es}"):
        fact("NOT SAVED")
        return None
    g.save(OP)
    labels = {"route": route, "vi_path": "vi path", "class_name": "Class Name", "sink_diag": "index",
              "sink_node": "index 2", "sink_term": "index 3", "src_node": "index 4", "src_term": "index 5",
              "src_diag": diag2_ctl, "method": "6349C03",
              "panel": [(i, lbl, ind) for i, lbl, ind in g.fp_labels(OP)]}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact(f"saved {OP} ({os.path.getsize(OP)} bytes) as ROUTE {route}; labels -> {MAP_OUT}")
    gate("W6b donor OpConnect2_v0.vi md5 unchanged", md5(SRC) == donor_md5, donor_md5)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    return labels


# ============================================================================== the wrapper
def connect_nested(target, sink_diag, sink_node, sink_term, src_node, src_term, labels, src_diag=None):
    """Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (source) into
    Diagram[sink_diag].Nodes[sink_node].Terminals[sink_term] (sink). ROUTE B ignores `src_diag`
    (both ends share `sink_diag`). Returns (wire delta, exec_state, error string)."""
    g.ensure_loaded(target)
    w0 = g.count(target, "Wire")
    vi = g.op(OP)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(labels["class_name"], "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["src_node"], int(src_node))
    vi.SetControlValue(labels["src_term"], int(src_term))
    if labels.get("src_diag"):
        vi.SetControlValue(labels["src_diag"], int(sink_diag if src_diag is None else src_diag))
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        if "modal dialog" not in str(e):
            err = f"EXC {str(e)[:140]}"
        else:
            err = "modal dialog (dismissed)"
    return g.count(target, "Wire") - w0, g.exec_state(target), err


# ============================================================================== FUNCTIONAL TEST
def test(labels):
    print("\n=== T: FUNCTIONAL test on a scratch copy of EMPTY_v0", flush=True)
    for p, nm in ((EMPTY, "EMPTY_v0.vi"), (BOOLVI, "Is Path and Not Empty.vi"), (NUMVI, "Error Cluster ...vi")):
        if not gate(f"T0 {nm} present", os.path.exists(p), p):
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
        i_D = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(D)
        i_top = 0
        fact(f"scratch: WhileLoop #{W}, body Diagram #{D} at Traverse index {i_D}")

        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, i_D, (60, 60))
        g.drop_subvi(SCRATCH, BOOLVI, i_D, (60, 220))
        nsv = g.new_since(SCRATCH, "SubVI", sv0)
        if not gate("T1b two body nodes dropped inside the loop body", len(nsv) == 2, f"{nsv}"):
            return
        wb = walk(SCRATCH, i_D)
        pick = {}
        for o in nsv:
            u = o["uid"]
            n_i, lab, rows = wb[u]
            pick[u] = dict(n=n_i, lab=lab,
                           outs=[(r["i"], r["name"]) for r in rows if r["is_source"]],
                           bare=[(r["i"], r["name"]) for r in rows if not r["is_source"] and r["wire"] == 0])
            fact(f"body #{u} Nodes[{n_i}] {lab!r}: outs {pick[u]['outs']}; bare ins {pick[u]['bare']}")

        # ---------------- T2 (a) body node -> body node, SAME nested diagram
        a_uid, b_uid = nsv[0]["uid"], nsv[1]["uid"]
        t_out = next((i for i, nm in pick[a_uid]["outs"] if nm == "error out"), None)
        t_in = next((i for i, nm in pick[b_uid]["bare"] if nm and "error in" in nm), None)
        if t_out is None or t_in is None:
            gate("T2 (a) body->body: an error-out/error-in pair was found", False,
                 f"outs {pick[a_uid]['outs']} bare {pick[b_uid]['bare']}")
        else:
            dw, es, err = connect_nested(SCRATCH, i_D, pick[b_uid]["n"], t_in, pick[a_uid]["n"], t_out, labels)
            wb2 = walk(SCRATCH, i_D)
            w_sink = next((r["wire"] for r in wb2[b_uid][2] if r["i"] == t_in), 0)
            w_srcw = next((r["wire"] for r in wb2[a_uid][2] if r["i"] == t_out), 0)
            fact(f"T2 (a) op error {err[:120]!r}; wire delta {dw}; ExecState {es}")
            gate("T2 (a) BODY->BODY on a nested diagram: the sink is wired, SAME wire uid on both ends",
                 bool(w_sink) and w_sink == w_srcw, f"sink w{w_sink} / source w{w_srcw}")
            gate("T2b (a) the scratch is RUNNABLE after the wire (ExecState 1)", es == 1, f"ExecState {es}")

        # ---------------- T3 (b) body node -> an UNNAMED terminal of a NESTED structure
        fl0 = g.uids(SCRATCH, "ForLoop")
        g.for_loop(SCRATCH, (900, 900))
        nfl = g.new_since(SCRATCH, "ForLoop", fl0)
        if not gate("T3a a For loop was created on the top-level diagram", len(nfl) == 1, f"{nfl}"):
            nfl = []
        moved = False
        if nfl:
            F = nfl[0]["uid"]
            try:
                # `OpMoveIn_v0` via build_d1_v0.move_in - uid-addressed, 12/0 (plan §2b). NOT re-written here.
                from build_d1_v0 import move_in as _move_in
                _move_in(SCRATCH, F, i_D, (400, 400))
                wchk = walk(SCRATCH, i_D)
                moved = F in wchk
                fact(f"T3 For loop #{F} reparented into the body diagram: {moved}")
            except Exception as e:
                fact(f"T3 move_in failed ({str(e)[:140]}) - the For loop stays on the top level")
            wb3 = walk(SCRATCH, i_D if moved else i_top)
            if F in wb3:
                n_F2, _lab, rowsF = wb3[F]
                unnamed = [(r["i"], r["wire"]) for r in rowsF if not r["is_source"] and not r["name"]]
                fact(f"T3 For loop #{F} on diagram {'body ' + str(i_D) if moved else 'top-level 0'} "
                     f"Nodes[{n_F2}]: unnamed input terminals {unnamed}")
                if unnamed:
                    t_un = unnamed[0][0]
                    tried = []
                    for u in (a_uid, b_uid):
                        for t_i, t_nm in pick[u]["outs"]:
                            dw, es, err = connect_nested(SCRATCH, i_D if moved else i_top, n_F2, t_un,
                                                         pick[u]["n"] if moved else pick[u]["n"], t_i, labels,
                                                         src_diag=i_D)
                            wb4 = walk(SCRATCH, i_D if moved else i_top)
                            w_un = next((r["wire"] for r in wb4[F][2] if r["i"] == t_un), 0)
                            tried.append((u, t_i, t_nm, dw, es, w_un, err[:60]))
                            if w_un:
                                break
                        if tried and tried[-1][5]:
                            break
                    for r in tried:
                        print(f"      T3 try src #{r[0]} t{r[1]} {r[2]!r}: delta {r[3]}, ExecState {r[4]}, "
                              f"unnamed-terminal wire {r[5]}, err {r[6]!r}", flush=True)
                    ok = bool(tried) and bool(tried[-1][5])
                    gate("T3 (b) an UNNAMED terminal of a nested structure is REACHED by index "
                         "(wire 0 -> non-zero)", ok, f"{tried[-1] if tried else 'no attempt'}")
                    es_now = g.exec_state(SCRATCH)
                    fact(f"T3 ExecState after the unnamed-terminal wire: {es_now} "
                         f"(a type-incompatible pair makes a BROKEN wire - a LabVIEW type fact, not an op "
                         f"failure; the gate above is wire identity)")
                else:
                    gate("T3 (b) the For loop exposes an unnamed input terminal", False, f"rows {rowsF}")
            else:
                gate("T3 (b) the For loop is on the expected diagram", False,
                     f"#{F} not on diagram {i_D if moved else i_top}")

        # ---------------- T4 (c) source on a DIFFERENT diagram
        if labels.get("route") == "A" and labels.get("src_diag"):
            lt0 = g.count(SCRATCH, "LoopTunnel")
            sv1 = g.uids(SCRATCH, "SubVI")
            g.drop_subvi(SCRATCH, NUMVI, i_top, (1400, 200))
            ntop = g.new_since(SCRATCH, "SubVI", sv1)
            if len(ntop) == 1:
                U = ntop[0]["uid"]
                wt = walk(SCRATCH, i_top)
                n_U, _l, rowsU = wt[U]
                t_o = next((r["i"] for r in rowsU if r["is_source"] and r["name"] == "error out"), None)
                wb5 = walk(SCRATCH, i_D)
                t_i2 = next((r["i"] for r in wb5[a_uid][2]
                             if not r["is_source"] and r["wire"] == 0 and r["name"]), None)
                if t_o is not None and t_i2 is not None:
                    dw, es, err = connect_nested(SCRATCH, i_D, pick[a_uid]["n"], t_i2, n_U, t_o, labels,
                                                 src_diag=i_top)
                    wb6 = walk(SCRATCH, i_D)
                    w_s = next((r["wire"] for r in wb6[a_uid][2] if r["i"] == t_i2), 0)
                    fact(f"T4 (c) cross-diagram: err {err[:120]!r}, wire delta {dw}, "
                         f"LoopTunnel {lt0} -> {g.count(SCRATCH, 'LoopTunnel')}, ExecState {es}")
                    gate("T4 (c) a source on a DIFFERENT diagram reaches a nested sink "
                         "(LabVIEW creates the tunnel)", bool(w_s), f"sink wire {w_s}")
                else:
                    gate("T4 (c) a cross-diagram pair was addressable", False, f"t_o {t_o} t_i2 {t_i2}")
        else:
            fact("T4 (c) NOT EXPRESSIBLE - ROUTE B shipped: the op carries ONE diagram index, so a source on a "
                 "DIFFERENT nested diagram has no route. This is the MEASURED LIMIT, reported not gated "
                 "(d1-build-plan.md §11m's own wording for test (c)).")

        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        fact(f"T5 junk Invokes purged: {junk}")
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
    labels = None
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
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== build_opconnectnested_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
