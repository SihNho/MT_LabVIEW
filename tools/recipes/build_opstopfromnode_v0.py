r"""build_opstopfromnode_v0.py - `OpStopFromNode_v0.vi`: wire a While loop's CONDITIONAL TERMINAL from a
terminal of a NODE INSIDE ITS OWN BODY, by the DIRECT typed-reference route.

    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/build_opstopfromnode_v0.log \
        -- py -u tools/recipes/build_opstopfromnode_v0.py

WHY: `docs/d1-build-plan.md` §11c/§9a stops D1's three new loops on END-OF-STREAM SENTINELS - each loop's stop is
a Boolean produced INSIDE its own body, never a panel read (§4's read-once rule). §11e.2 lifted the cycle-15 op
freeze narrowly for this one op.

THE DESIGN CHANGED AFTER ITS PRIOR-ART REVIEW, and this header records both.
  DISPATCHED: `archive/peer/2026-09-17-priorart-d1-op-exitwhile-node.md` (slug `d1-op-exitwhile-node`, trigger
  new-op). 5 findings, 0 novel. The proposal was a FRONT-HALF SWAP on `OpExitWhile_v0` (delete
  `Get Controls.vi`, feed the stop `Index Array` from a third `Get Outputs.vi`). Two verdicts changed it:
    * **B1 `helper-exists`** - the erdosmiller `Exit While Loop.vi` `Stop Condition` is NOT the only route, and
      the direct one is already priced: `WhileLoop.Loop End Ref` **6362C00** hands back a **`Terminal`**
      (`docs/NAMES.md:246-249`, VERIFIED on the machine by `OpLoopEndRef_v0`, 16/0), and `Terminal.Connect Wire`
      **6349C03** on a sink is built FOUR times over (`tools/recipes/build_opwiresr_v0.py:4`). The review's own
      line: the last time this project chose between a library-VI side effect and a direct typed-reference
      method, the review refused the library VI and the direct method shipped.
    * **A3 `contradicted`** - the build was authorised as *additive* (§11e.2) while the proposal deleted a
      subVI and a wire. **This route is additive in the literal sense: NOTHING is deleted from the donor.**
  So the donor is `OpLoopEndRef_v0.vi`, not `OpExitWhile_v0.vi`, and `tools/recipes/build_opexitwhilenode_v0.py`
  (written before the review returned) is SUPERSEDED and not run.

  THE REVISED DESIGN WAS THEN DISPATCHED AGAIN: `archive/peer/2026-09-17-priorart-d1-op-stopfromnode.md`
  (slug `d1-op-stopfromnode`). 5 findings, 0 novel, all accepted; A1/A2/B1 cleared the route ("the op is
  genuinely unbuilt; no archived exchange refutes the direct route or the `LpEndRef` branch"). Four repairs
  landed in THIS file before it was run:
    * **A3-ii** two counts corrected - the body-node CHAIN is built **twice**, not four times
      (`build_opwiresr_v0.py:227-245`); and `Loop.Diagram` **6361401** is *"listed from the Wiki, UNVERIFIED"* in
      `docs/NAMES.md:241-242` but **MEASURED PASS** in `tools/bench/build_opwiresr_v0.log:25-29,:69-73` - it is
      verified by LOG, not by the names file.
    * **B2** the loop-end-ref driver is now IMPORTED from `build_d1_v0` (it poisons every output, `IsSource`
      included, and reads the four per-property error columns; the hand-rolled copy dropped both, and T3/T3b/T4
      are scored on exactly that read).
    * **B3** `pn()` now CENSUSES the node it creates and `data_name()` asserts exactly one data SOURCE terminal
      instead of taking index 4; the indicator block asserts one new, uniquely-labelled INDICATOR.
    * **B4** T6 no longer wires an `error out` CLUSTER as a "mismatch" - **LabVIEW accepts an error cluster on a
      conditional terminal** (Stop if Error), so that gate would have read 1 -> 1 and failed a working op.
      It is now the POSITIVE `OpWireSource_v5` check, which also proves DIRECTION.
  ⚠️ **A3-i, escalated, NOT patched here:** the sentence that authorises this build (§11e.2) names
  *"the stop front-half swap on `OpExitWhile_v0`"*, and this op is not that. The substance is the same duty and
  the same narrow scope, but only judgement re-words an authorisation - flagged in STATUS.

WHAT ALREADY EXISTS - checked before a line was written:
  * `OpLoopEndRef_v0.vi` - BUILT, 16/0, ExecState 1. Censused 2026-09-17 (`tools/bench/diag_loopendref_front.log`):
      `To More Specific Class` **#683** `specific class reference` (w366) = the WhileLoop-typed reference
      -> Property **#657** data terminal **`LpEndRef`** (w775) = THE CONDITIONAL TERMINAL
      -> #738 `UID`, #743 `IsSource`, #745 `Wire` (the read path, untouched).
  * `build_opwiresr_v0.py` - the body-node chain and the Connect Wire invoke, verbatim:
      TMSC --branch--> PN Loop[`Diagram` 6361401] -> PN AbstractDiagram[`Nodes[]` 6375809] -> IndexArray(node)
      -> PN Node[`Terms[]` 6359000] -> IndexArray(term); Invoke Terminal[`Connect Wire` 6349C03] with
      `reference` = the SINK and `Wire Source` = the source terminal.
  * `g.build_property`, `g.build_index_array`, `g.build_invoke`, `g.create_control`, `g.create_indicator`,
    `g.wire`, `g.set_auto_error_handling`, `g.exec_state`, `g.save` - all built.
  * `OpExitWhile_v0` stays as it is: it remains the right op for a PANEL-control stop. No op is replaced.

PREDICTION CONTRACT (counts a machine checks; stop at the first miss, nothing saved on a miss):
  W0  `OpLoopEndRef_v0.vi` present, ExecState 1, and the three censused uids (#683, #657, #124) are on its
      diagram; its `LpEndRef` data terminal is at index 4 of #657.
  W1  copy -> `OpStopFromNode_v0.vi`: Node 14, Property 8, Wire 25, ControlTerminal 20, ExecState 1.
  W2  PN Loop[Diagram] created and fed from #683 `specific class reference` (branch) - Property 8 -> 9.
  W3  PN AbstractDiagram[Nodes[]] - Property 10; W4 IndexArray(node) + its `index` control;
      W5  PN Node[Terms[]] - Property 11; W6 IndexArray(term) + its `index` control.
  W7  Invoke Terminal[Connect Wire]: `reference` <- #657 `LpEndRef` (BRANCH - the read path keeps its wire),
      `Wire Source` <- IndexArray(term) `element`. Every wire verified by the SAME wire uid on both ends.
  W8  ExecState 1 -> COM save; labels json written. NOTHING is deleted at any step: Node/Property/Wire counts
      only ever INCREASE, and that is gated (W8b).
  T1..T6 on a SCRATCH created and DELETED in the same run: EMPTY_v0 copy + a While loop + a body node with a
      Boolean output (`Is Path and Not Empty.vi`, a subVI, so `drop_subvi` places it - no new op).
      T3/T3b the conditional terminal's wire goes 0 -> NON-ZERO on the SAME terminal uid; T4 that wire uid is
      the SAME on both ends (the body node's Boolean output and the conditional terminal); T5 ExecState 1.
      T6 is the DISCRIMINATING TEST: the same node's `error out` CLUSTER wired onto a SECOND loop's conditional
      terminal must DROP ExecState to 0 - a no-op would leave it at 1.
      **LEVEL OF VERIFICATION, stated (CLAUDE.md): STRUCTURAL + WIRE-IDENTITY + a TYPE discriminator - NOT a
      run.** `Is Path and Not Empty.vi` with an unwired `path` returns FALSE, so running the scratch would spin
      forever, and `create_control` reaches TOP-LEVEL nodes only (`gscript.py:2155`), so no control can be
      attached to a terminal inside the body. Execution behaviour is proven by D1's F2 gate, not here.
No original is touched; nothing outside `user.lib\claudeDev` is written.
"""
import json
import os
import shutil
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
# B2 (prior-art `d1-op-stopfromnode`): the loop-end-ref driver EXISTS and carries safeguards a copy drops -
# it POISONS every output before the run (including `IsSource`) and reads the FOUR per-property error columns,
# because "no error out" is not a verdict that a property resolved (toolkit-capabilities.md:234-238). Imported,
# not re-written. It reads `LOOPENDREF_LABELS` itself.
from build_d1_v0 import loop_end_ref as _loop_end_ref   # noqa: E402

SRC = os.path.join(g.CLAUDEDEV, "OpLoopEndRef_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpStopFromNode_v0.vi")
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
LOOPENDREF_LABELS = os.path.join(ROOT, "tools", "bench", "oploopendref_labels.json")
MAP_OUT = os.path.join(ROOT, "tools", "bench", "opstopfromnode_labels.json")
BOOLVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Is Path and Not Empty.vi"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_stopfromnode_{STAMP}.vi")

# MEASURED in OpLoopEndRef_v0 (tools/bench/diag_loopendref_front.log, 2026-09-17)
U_TMSC = 683          # `specific class reference` = the WhileLoop-typed reference
U_PN_ENDREF = 657     # data terminal `LpEndRef` = the conditional terminal
U_TRAVERSE = 124
P_DIAGRAM, P_NODES, P_TERMS, M_CONNECT = "6361401", "6375809", "6359000", "6349C03"
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


def gate(name, ok, detail=""):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(f"  FACT  {line}", flush=True)


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


def data_name(uid, w=None):
    """The property node's DATA terminal, CENSUSED - not the index-4 convention.

    B3 (prior-art `d1-op-stopfromnode`): `build_opcaseframes_v0.prop_node()`/`add_indicator()` carry assertions a
    hand-rolled helper drops, and `toolkit-capabilities.md:234-238` measured why it matters - **a valid id on the
    WRONG CLASS creates a property node with no data terminal and NO ERROR AT ALL**. That is live here: W2 puts
    `Diagram` 6361401 on class `VI Server:Loop` while the reference arrives from a `WhileLoop`. Those helpers bind
    their target through a module-global `OP`, so they are not importable into this file; their ASSERTION is taken
    verbatim instead - exactly one data SOURCE terminal, or the build stops."""
    w = w or walk(OP, 0)
    data = [r for r in w[uid][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
    if len(data) != 1:
        raise RuntimeError(f"property #{uid} has {len(data)} data SOURCE terminals, not 1: "
                           f"{[(r['name'], r['is_source']) for r in w[uid][2]]} - a valid id on the WRONG CLASS "
                           f"creates a node with no data terminal and no error (toolkit-capabilities.md:234-238)")
    return data[0]["name"]


def connect(src_uid, src_name, dst_uid, dst_name, branch=False, tag=""):
    """Wire by name, verified by the SAME wire uid on BOTH ends - never by a count, never by ExecState
    (docs/toolkit-capabilities.md row 37)."""
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


def pn(cls, pid, pos):
    """Create ONE property node and census it (B3): exactly one new `Property` object, and `data_name` then
    asserts it has exactly one data SOURCE terminal. 'No error' is explicitly NOT the verdict."""
    before = g.uids(OP, "Property")
    g.build_property(OP, cls, [(pid, False)], pos)
    new = [u for u in g.uids(OP, "Property") if u not in before]
    if len(new) != 1:
        raise RuntimeError(f"build_property({cls}, {pid}) made {len(new)} Property nodes: {new}")
    nm = data_name(new[0])
    print(f"      CENSUS {cls} {pid} -> uid {new[0]}, data terminal {nm!r}", flush=True)
    return new[0]


def ia(pos):
    r = g.build_index_array(OP, pos)
    return r[-1]["uid"] if r else None


def make_ctl(uid, name):
    w = walk(OP, 0)
    n, rows = w[uid][0], w[uid][2]
    t = term(rows, name, False)["i"]
    before = {lbl for _i, lbl, ind in g.fp_labels(OP) if not ind}
    g.create_control(OP, n, t)
    new = [lbl for _i, lbl, ind in g.fp_labels(OP) if not ind and lbl not in before]
    if len(new) != 1:
        raise RuntimeError(f"create_control on {name!r} made {new}")
    return new[0]


def counts(target):
    return {c: g.count(target, c) for c in ("Node", "Property", "Wire", "ControlTerminal", "Invoke", "IndexArray")}


def build():
    print("\n=== W0: the donor", flush=True)
    if not gate("W0a OpLoopEndRef_v0.vi on disk", os.path.exists(SRC), SRC):
        return False
    g.open_panel(SRC)
    es = g.exec_state(SRC)
    gate("W0 donor ExecState 1", es == 1, f"ExecState {es}")
    g.close_panel(SRC)

    print("\n=== W1: the copy (additive build - nothing is ever deleted)", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    c0 = counts(OP)
    fact(f"copy census: {c0}, ExecState {g.exec_state(OP)}")
    if not gate("W1 the copy matches the censused donor",
                c0["Node"] == 14 and c0["Property"] == 8 and c0["Wire"] == 25 and c0["ControlTerminal"] == 20,
                f"{c0}"):
        return False
    w = walk(OP, 0)
    for uid in (U_TMSC, U_PN_ENDREF, U_TRAVERSE):
        gate(f"W1b #{uid} present on the op's diagram", uid in w, "")
    endref_name = data_name(U_PN_ENDREF, w)
    if not gate("W1c #657's data terminal is the conditional-terminal reference", endref_name == "LpEndRef",
                f"{endref_name!r} (want 'LpEndRef')"):
        return False

    print("\n=== W2..W6: the body-node chain, branched off the SAME typed reference", flush=True)
    y = 1400
    d = pn("VI Server:Loop", P_DIAGRAM, (300, y))
    gate("W2 PN Loop[Diagram] created", bool(d), f"uid {d}")
    connect(U_TMSC, "specific class reference", d, "reference", branch=True, tag="W2 ")
    nn = pn("VI Server:AbstractDiagram", P_NODES, (520, y))
    connect(d, data_name(d), nn, "reference", tag="W3 ")
    ia_n = ia((760, y))
    connect(nn, data_name(nn), ia_n, "array", tag="W4 ")
    lbl_node = make_ctl(ia_n, "index")
    fact(f"node-index control is labelled {lbl_node!r}")
    tt = pn("VI Server:Node", P_TERMS, (980, y))
    connect(ia_n, "element", tt, "reference", tag="W5 ")
    ia_t = ia((1220, y))
    connect(tt, data_name(tt), ia_t, "array", tag="W6 ")
    lbl_term = make_ctl(ia_t, "index")
    fact(f"term-index control is labelled {lbl_term!r}")
    es = g.exec_state(OP)
    if not gate("W6b the body-node chain leaves the op runnable", es == 1, f"ExecState {es}"):
        return False

    print("\n=== W7: Terminal.Connect Wire on the conditional terminal", flush=True)
    r = g.build_invoke(OP, "VI Server:Terminal", M_CONNECT, (1500, y + 180))
    inv = r[-1]["uid"] if r else None
    if not gate("W7 Invoke Terminal[Connect Wire] created", bool(inv), f"uid {inv}"):
        return False
    # BRANCH on the sink: #657's `LpEndRef` already feeds the three READ property nodes (#738/#743/#745) and that
    # read path must survive - this op reads the terminal back as its own verification output.
    connect(U_PN_ENDREF, "LpEndRef", inv, "reference", branch=True, tag="W7 sink ")
    connect(ia_t, "element", inv, "Wire Source", tag="W7 src ")
    try:
        # B3: `add_indicator`'s assertions taken verbatim - exactly one new panel object, it IS an indicator,
        # and its label is UNIQUE (a duplicate label is this fleet's recorded way to write the wrong control).
        lbl_err = None
        w = walk(OP, 0)
        n = w[inv][0]
        t = term(w[inv][2], "error out", True)
        if t:
            rows0 = {r["uid"]: r for r in g.panel_wiring(OP)}
            g.create_indicator(OP, n, t["i"])
            rows1 = {r["uid"]: r for r in g.panel_wiring(OP)}
            new = [r for u, r in rows1.items() if u not in rows0]
            if len(new) != 1:
                raise RuntimeError(f"create_indicator made {len(new)} panel objects: {new}")
            if not new[0].get("indicator") or sum(1 for r in rows1.values()
                                                  if r["label"] == new[0]["label"]) != 1:
                raise RuntimeError(f"the new panel object is not a uniquely-labelled indicator: {new[0]}")
            lbl_err = new[0]["label"]
        fact(f"connect-wire error indicator: {lbl_err!r}")
    except Exception as e:
        fact(f"error indicator not created ({str(e)[:80]}) - the op's own `error out` chain still reports")
        lbl_err = None
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:
        fact(f"set_auto_error_handling failed ({str(e)[:60]})")

    print("\n=== W8: ExecState and save", flush=True)
    c1 = counts(OP)
    fact(f"after build: {c1} (was {c0})")
    gate("W8b the build was ADDITIVE - no class lost a member",
         all(c1[k] >= c0[k] for k in c0), f"{ {k: (c0[k], c1[k]) for k in c0} }")
    es = g.exec_state(OP)
    if not gate("W8 ExecState 1 - the op is runnable", es == 1, f"ExecState {es}"):
        fact("NOT SAVED: a broken op is never written to disk")
        return False
    g.save(OP)
    with open(LOOPENDREF_LABELS, encoding="utf-8") as f:
        ler = json.load(f)
    labels = {"vi_path": "vi path", "loop_class": "Class Name", "loop_index": "index",
              "index_node": lbl_node, "index_term": lbl_term, "connect_err": lbl_err}
    labels.update({f"read_{k}": v for k, v in ler.items()})
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact(f"saved {OP} ({os.path.getsize(OP)} bytes); labels -> {MAP_OUT}")
    return labels


# ------------------------------------------------------------------ the functional test
def loop_end_ref(target, loop_index):
    """B2: `build_d1_v0.loop_end_ref` verbatim - it poisons EVERY output (IsSource included) and returns the four
    per-property error columns in `errs`, which this file's earlier hand-rolled copy dropped. T3/T3b/T4 are scored
    on `errs` being empty, so a silently unresolved property can no longer read as 'not wired yet'."""
    return _loop_end_ref(target, loop_index)


_WSRC_LABELS = None


def wire_source(target, wire_uid, max_terms=8):
    """B4(b), the POSITIVE check: `OpWireSource_v5` (12/12, toolkit-capabilities.md:48) resolves which object
    DRIVES a wire. Walk `term index` until the read errors; return every terminal with its `Is Source?`, its
    reciprocal wire and its OWNER uid. This proves DIRECTION, which a wire-uid equality cannot."""
    global _WSRC_LABELS
    if _WSRC_LABELS is None:
        with open(os.path.join(ROOT, "tools", "bench", "opwiresource_v5_labels.json"), encoding="utf-8") as f:
            _WSRC_LABELS = json.load(f)
    lab = _WSRC_LABELS
    # MEASURED, run 2: `g.uids()` returns a SET, and a Traverse index must come from the ORDERED listing -
    # `report_all` is that order everywhere else in this fleet (`build_opwiresource_v0.read_wire` indexes into
    # `g.uids(...)` only because it happens to receive a list from `uids()` in that file's call site).
    wires = [o["uid"] for o in g.report_all(target, "Wire")]
    if wire_uid not in wires:
        return []
    wi = wires.index(wire_uid)
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi"))
    out = []
    for t in range(max_terms):
        vi.SetControlValue(lab["owner_uid"], 0)
        vi.SetControlValue(lab["is_source"], False)
        vi.SetControlValue(lab["recip_wire"], 0)
        vi.SetControlValue(lab["cls_back"], "POISON")
        vi.SetControlValue("vi path", target)
        vi.SetControlValue("Class Name", "Wire")
        vi.SetControlValue("index", int(wi))
        vi.SetControlValue(lab["term_index"], int(t))
        try:
            g._run(vi)
        except Exception:
            break
        errs = " ".join(x for x in (g._err(vi, lab[k]) or "" for k in ("errS", "errWU", "errG")) if x)
        if errs:
            break
        out.append(dict(term=t, is_source=bool(vi.GetControlValue(lab["is_source"])),
                        recip=int(vi.GetControlValue(lab["recip_wire"])),
                        owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                        owner_cls=vi.GetControlValue(lab["cls_back"])))
    return out


def test(labels):
    print("\n=== T: FUNCTIONAL test on a scratch VI", flush=True)
    if not gate("T0a EMPTY_v0.vi present", os.path.exists(EMPTY), EMPTY):
        return
    if not gate("T0b the Boolean-output donor subVI exists", os.path.exists(BOOLVI), BOOLVI):
        return
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copyfile(EMPTY, SCRATCH)
    time.sleep(0.3)
    g.report_all(SCRATCH, "SubVI")
    g.open_panel(SCRATCH)
    inv0 = g.uids(SCRATCH, "Invoke")
    try:
        wl0, dg0 = g.uids(SCRATCH, "WhileLoop"), g.uids(SCRATCH, "Diagram")
        # MEASURED, run 1 (`build_opstopfromnode_v0.log` 08:04): `loop_in("while", SCRATCH, 0, ...)` raised
        # `error 1055: To More Specific Class in OpWhileLoopIn_v0.vi`. `loop_in` takes its input tunnels from
        # Traverse `src_cls`[`src_index`] and DEFAULTS `src_cls` to **"SubVI"** (`gscript.py:978`) - EMPTY_v0 has
        # no SubVI at all, so the cast had nothing to cast. `while_loop()` is the right creator here: it places a
        # While loop on the TOP-LEVEL diagram and takes its tunnels from named front-panel CONTROLS (none), so it
        # needs no existing node. The body node is dropped into it afterwards, which is what the test needs.
        g.while_loop(SCRATCH, (200, 200))
        nwl, ndg = g.new_since(SCRATCH, "WhileLoop", wl0), g.new_since(SCRATCH, "Diagram", dg0)
        if not gate("T1 one While loop created", len(nwl) == 1 and len(ndg) == 1, f"{nwl} {ndg}"):
            return
        loop_uid, body_uid = nwl[0]["uid"], ndg[0]["uid"]
        body_i = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")].index(body_uid)
        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, BOOLVI, body_i, (80, 80))
        nsv = g.new_since(SCRATCH, "SubVI", sv0)
        if not gate("T2 the Boolean-output node is inside the loop body", len(nsv) == 1, f"{nsv}"):
            return
        u_node = nsv[0]["uid"]
        wb = walk(SCRATCH, body_i)
        node_i, rows = wb[u_node][0], wb[u_node][2]
        outs = [(r["i"], r["name"]) for r in rows if r["is_source"] and r["name"]]
        ins = [(r["i"], r["name"]) for r in rows if not r["is_source"] and r["name"]]
        fact(f"body node #{u_node} (body Nodes[{node_i}]) outputs {outs}; inputs {ins}")
        bool_t = next((i for i, n in outs if "?" in n), None)
        err_t = next((i for i, n in outs if n == "error out"), None)
        if not gate("T2b a Boolean output was found", bool_t is not None, f"outputs {outs}"):
            return
        loop_i = [o["uid"] for o in g.report_all(SCRATCH, "WhileLoop")].index(loop_uid)
        before = loop_end_ref(SCRATCH, loop_i)
        # MEASURED, run 2: T5 read ExecState 0 AFTER the op and the run stopped there with no way to tell whether
        # the op broke the VI or the VI was already broken. A fresh While loop's conditional terminal is UNWIRED,
        # which by itself is a broken VI (`gscript.while_loop` says so: "ExecState 0 until OpExitWhile / a stop
        # control is wired"). So the BEFORE number is now recorded, and T5 is judged as a TRANSITION.
        es_before = g.exec_state(SCRATCH)
        fact(f"BEFORE: cond term {before['cond_term_uid']}, wire {before['cond_wire_uid']}, "
             f"ExecState {es_before} (0 is EXPECTED - an unwired conditional terminal IS a broken VI)")

        vi = g.op(OP)
        vi.SetControlValue("vi path", SCRATCH)
        vi.SetControlValue("Class Name", "WhileLoop")
        vi.SetControlValue("index", int(loop_i))
        vi.SetControlValue(labels["index_node"], int(node_i))
        vi.SetControlValue(labels["index_term"], int(bool_t))
        g._run(vi)
        err = g._err(vi, "error out") or ""
        fact(f"OpStopFromNode_v0 error out: {err[:180]!r}")
        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)

        after = loop_end_ref(SCRATCH, loop_i)
        fact(f"AFTER : cond term {after['cond_term_uid']}, wire {after['cond_wire_uid']}")
        gate("T3 the conditional terminal is now WIRED", after["cond_wire_uid"] != 0,
             f"wire {after['cond_wire_uid']} (was {before['cond_wire_uid']})")
        gate("T3b the SAME terminal, not a new one",
             after["cond_term_uid"] == before["cond_term_uid"] and after["cond_term_uid"] != 0,
             f"{before['cond_term_uid']} -> {after['cond_term_uid']}")
        wb2 = walk(SCRATCH, body_i)
        src_w = next((r["wire"] for r in wb2[u_node][2] if r["i"] == bool_t), 0)
        gate("T4 the SAME wire uid on both ends (never a count)", src_w == after["cond_wire_uid"] and src_w,
             f"body node output w{src_w} vs conditional terminal w{after['cond_wire_uid']}")
        es = g.exec_state(SCRATCH)
        es_rbw = None
        if es != 1:
            g.remove_bad_wires_scripted(SCRATCH)
            es_rbw = g.exec_state(SCRATCH)
        fact(f"ExecState {es_before} (before the op) -> {es} (after) "
             + (f"-> {es_rbw} (after Remove Bad Wires)" if es_rbw is not None else ""))
        gate("T5 wiring the Boolean stop makes the loop COMPILE (ExecState 0 -> 1)",
             es_before == 0 and (es == 1 or es_rbw == 1),
             f"ExecState {es_before} -> {es}"
             + (f" -> {es_rbw} after RBW" if es_rbw is not None else "")
             + " (want 0 -> 1; a fresh While loop with an unwired conditional terminal is a broken VI, so the "
               "BEFORE number is expected to be 0 and the transition is what the op is judged on)")

        # ---- T6: the DISCRIMINATING TEST (CLAUDE.md devil's-advocate: name what would falsify it and run the
        # cheapest separator). The alternative explanation for T3/T4 is "the op did nothing, and the wire uid I
        # read was already there".
        #
        # REWRITTEN after prior-art `d1-op-stopfromnode` B4 `already-measured`. The first version wired the same
        # node's `error out` CLUSTER onto a second loop's conditional terminal and required ExecState 1 -> 0.
        # **That is not a mismatch**: LabVIEW ACCEPTS an error cluster on a conditional terminal (only `status`
        # passes; the shortcut items become Stop if Error / Continue While Error - LabVIEW Wiki, While loop, the
        # same page 6362C00 came from, docs/NAMES.md:241). Predicted 1 -> 1, i.e. a working op blocked by its own
        # gate - the exact class this cycle already paid for (STATUS 27b, "the five fails are MY GATES").
        # B4(b)'s repair is used instead, and it is STRONGER: `OpWireSource_v5` (12/12) resolves the wire's own
        # source terminal, so the assertion is POSITIVE and proves DIRECTION, which T4's uid equality does not.
        #
        # The VI is deliberately NOT RUN. Level of verification, stated: STRUCTURAL + WIRE-IDENTITY + SOURCE
        # RESOLUTION. `Is Path and Not Empty.vi` with an unwired `path` returns FALSE, so a run would spin
        # forever, and there is no control creator for a terminal INSIDE a loop body (`create_control` walks
        # VI -> Block Diagram -> Nodes[], the TOP LEVEL only - gscript.py:2155). Execution behaviour is proven by
        # D1's F2 gate (all loops exit), not by this scratch.
        if after["cond_wire_uid"]:
            terms_on_wire = wire_source(SCRATCH, after["cond_wire_uid"])
            for r in terms_on_wire:
                print(f"      wire {after['cond_wire_uid']} t{r['term']}: is_source={r['is_source']} "
                      f"owner {r['owner_cls']}#{r['owner_uid']} recip w{r['recip']}", flush=True)
            srcs = [r for r in terms_on_wire if r["is_source"]]
            gate("T6 DISCRIMINATOR: the new wire's SOURCE resolves to the body node (direction proven, "
                 "OpWireSource_v5)",
                 len(srcs) == 1 and srcs[0]["owner_uid"] == u_node,
                 f"sources {[(r['term'], r['owner_cls'], r['owner_uid']) for r in srcs]} "
                 f"(want exactly one, owner #{u_node})")
        else:
            gate("T6 DISCRIMINATOR: the new wire's SOURCE resolves to the body node", False,
                 "no wire on the conditional terminal to resolve")
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            os.remove(SCRATCH)
            fact(f"scratch deleted: {SCRATCH}")
        except Exception as e:
            fact(f"scratch NOT deleted ({str(e)[:60]})")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    try:
        labels = build()
        if labels:
            test(labels)
    finally:
        try:
            g.close_panel(OP)
        except Exception:
            pass
        g._lv = None
    print("\n--- FACTS ---", flush=True)
    for f_ in facts:
        print("  " + f_, flush=True)
    print(f"\n=== build_opstopfromnode_v0: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
