r"""build_opconnectnested_v1.py - `OpConnectNested_v1.vi`: `Terminal.Connect Wire` 6349C03 with the SINK and the
SOURCE on **TWO DIFFERENT nested diagrams**, both addressed purely by INDEX. `docs/d1-build-plan.md` §11p item 1
(the user's LAST attempt at route A).

    MATERIAL=1 py tools/bgrun.py --max-min 30 --log tools/bench/build_opconnectnested_v1.log \
        -- py -u tools/recipes/build_opconnectnested_v1.py

WHAT ALREADY EXISTS (checked before writing a line, per the standing rule):
  * `OpConnectNested_v0.vi` + `tools/recipes/build_opconnectnested_v0.py` - the same op with ONE diagram index.
    This build is ADDITIVE on it: its ladders, its Invoke, its panel controls are all kept.
  * `tools/recipes/build_opconstvalue_v1.py:165-199` - the PROVEN route for a second `To More Specific Class`
    inside an op VI: `copy_by_index(<NI example>, "Function", i_tmsc, OP, expect_uid=..., finish=...)` plus a
    TYPED refnum seed control on `target class`. `OpConstValue_v1.vi` (13,499 B) is on disk, so it worked.
  * `gscript.build_index_array`, `create_control`, `wire`, `wire_control`, `delete_object`,
    `remove_bad_wires_scripted`, `set_auto_error_handling` - nothing here is hand-rolled.
  * measured this session: `tools/bench/diag_connectnested_v1_facts.log`, 10/0.

THE CLAIM THIS BUILD REFUTES OR CONFIRMS, stated before the run. `docs/toolkit-capabilities.md:56` and
`d1-build-plan.md` §11n item 2 both say the cross-diagram op "**cannot be built by this fleet**" because "a second
TMSC has no creator ... `copy_by_index` would land it with an unwirable `target class` (a class-specifier
`Constant` is a GObject, not a Node)". Two things on our own record contradict the reason:
  (a) `toolkit-capabilities.md:72` - "`To More Specific Class`'s `target class` accepts **any wire of the target
      type**", so it never has to be a class-specifier Constant; and
  (b) `build_opconstvalue_v1.py` did exactly this copy and fed `target class` from a `create_control` seed.
MEASURED HERE (`diag_connectnested_v1_facts.log`): `OpConnectNested_v0`'s TMSC #683 takes `target class` from
w772, whose source is on NO node of diagram 0 and on NO panel control - i.e. it IS a class-specifier Constant, so
the claim's premise is right and its conclusion is still wrong: we make our OWN seed instead of branching w772.

THE FIVE CODE-GENERATION CAUSES codex named for run 1's ExecState 0
(`archive/peer/2026-09-17-nested-diagram-terminals.md` §2), and how each is ruled out BY MEASUREMENT here:
  1. "the second class-specifier constant is not configured as AbstractDiagram/Diagram" -> there IS no second
     class-specifier constant. The second TMSC's `target class` is a refnum CONTROL created by
     `Terminal.Create Control` FROM the very property node the cast must satisfy (gate V3), so its type is that
     node's own reference type by construction, not by a string we typed.
  2. "the second TMSC's terminals wired by the wrong index" -> every connection is made BY TERMINAL NAME and
     verified by reading the SAME wire uid back on BOTH ends (`connect()`), never by a count (gates V5a-V5d).
  3. "the property node was configured for another class" -> the source `Nodes[]` property node is NOT rebuilt;
     it is the donor's own node #744, identified by WIRE TOPOLOGY back from the Invoke's `Wire Source` (gate V2),
     and its data-terminal name is asserted to be `Nodes[]`.
  4. "Set Properties[] picked an alternate/localised name" -> no property node is created by this build at all.
  5. "the Index Array output was wired past the downcast" -> gate V6 re-reads the finished ladder from the Invoke
     backwards and asserts the SOURCE ladder's head is the NEW TMSC and the SINK ladder's head is the OLD one,
     with DIFFERENT `reference` wires and DIFFERENT index controls.

BUILD (each gate fatal; nothing is saved on a miss; the donor is never written)
 V0  donor `OpConnectNested_v0.vi` present at ExecState 1; md5 recorded and re-asserted at the end.
 V1  copy -> `OpConnectNested_v1.vi`; opens ExecState 1; exactly ONE TMSC; 19 nodes.
 V2  IDENTIFY BY WIRE TOPOLOGY: from the Invoke's `reference` -> the SINK ladder, from `Wire Source` -> the
     SOURCE ladder. Both heads must be the SAME property-node `reference` wire today (that is v0's branch).
 V3  delete that wire NET (it has three sinks: `Create Invoke Node.vi` `Diagram in`, the sink `Nodes[]` PN, the
     source `Nodes[]` PN); Remove Bad Wires; `create_control` on the SOURCE `Nodes[]` PN's now-bare `reference`
     -> ONE new control = the TYPED SEED, arriving already wired to it.
 V4  re-wire the OLD TMSC to its two remaining sinks; `build_index_array` + `References` (branch) + a new `index`
     control -> the SOURCE-DIAGRAM index. ExecState 1; save (copy_by_index copies the FILE).
 V5  `copy_by_index(NI example, "Function", 6, expect_uid=99)`; in `finish`, on the loaded Target:
     V5a delete the seed's own wire (one sink) so `target class` and the PN `reference` are both free;
     V5b seed -> new TMSC `target class`;  V5c new IA `element` -> new TMSC `reference`;
     V5d new TMSC `specific class reference` -> the SOURCE `Nodes[]` PN `reference`; ExecState 1 inside finish.
 V6  re-read the finished VI: two TMSCs, two distinct diagram-index controls, the two ladders' heads differ.
 V7  auto error handling OFF; ExecState 1; labels JSON; donor md5 unchanged; file size recorded.

THE PRIOR-ART REVIEW (`archive/peer/2026-09-17-priorart-connectnested-v1.md`, 8 findings) CHANGED TWO THINGS:
  * **B4 `already-measured`, ADOPTED.** "same wire uid on both ends" is NOT a proof that the wire is good:
    `docs/NAMES.md:861-863` - *"LabVIEW joins type-incompatible terminals and draws a broken wire, whose uid still
    reads identically at both ends"*, and `test_opconnectnested_v1.log:24-27` measured exactly that pair on v0
    (w285 on both ends, ExecState 1 -> 0). So T2 now (a) puts the SAME subVI in both bodies so the pair is
    `error out` -> `error in (no error)` (§11n.4's own discriminator), (b) records ExecState BEFORE and AFTER, and
    (c) adds the decisive gate: **`remove_bad_wires_scripted` and the wire SURVIVES** - RBW deletes a broken wire
    and leaves a good one, which uid-equality cannot distinguish.
  * **B3-i `helper-exists`, RECORDED, NOT ADOPTED - and this is the one judgement-shaped call in the build, so it
    is written down.** `OpExitLoop_v0.vi` (and `OpWire_v1`, `OpWireSource_v5`) already carry TWO independent
    `Traverse -> IndexArray -> To More Specific Class` ladders with their own `Class Name`/`index` pairs
    (`tools/bench/probe_opexitloop.log:12-18`; #788 is Diagram-typed). That IS the cheaper source of a second
    cast, and the 6-donor census that concluded "no second TMSC exists" never censused those three. It is not
    adopted here because building from `OpExitLoop_v0` means re-creating the sink AND source
    `Nodes[] -> IA -> Terms[] -> IA` ladders and the `Connect Wire` invoke from scratch (7+ nodes, 10+ wires),
    while this build adds ONE node to an op that already works. If V5 fails, `OpExitLoop_v0` is the second
    attempt, not a third route. The review states B3-i "does not claim the copied-TMSC route fails".
  * A3-ii / B2 concern **artifact 2** (the tunnel-source reader), not this build, and are carried forward.

FUNCTIONAL TEST on a scratch copy of `EMPTY_v0.vi` (unique name per run, DELETED in the same run):
 T1  TWO While loops on the top-level diagram, the SAME subVI dropped in each body -> two DIFFERENT nested
     diagrams and a TYPE-COMPATIBLE pair (B4).
 T2  THE GATE: body(A) `error out` -> body(B) `error in (no error)`, addressed by (diagram, node, terminal) on
     both sides. Sink wire 0 -> non-zero, the SAME wire uid on both ends, ExecState before/after recorded, and
     the wire SURVIVES `remove_bad_wires_scripted`.
 T3  body(B) output -> an UNNAMED input terminal of a For loop REPARENTED into body(A) (`OpMoveIn_v0`, 12/0).
     Gate = wire identity on an unnamed terminal ACROSS diagrams; ExecState is REPORTED (a type-incompatible
     pair makes a broken wire - a LabVIEW type fact, not an op failure).
 T4  scratch deleted; donor md5 unchanged; original working-copy md5 2a78e17c449c... before and after; handles.

FAILURE BUDGET 2 (CLAUDE.md §3). No repair pass inside the run.
Nothing outside `user.lib\claudeDev` is written; no original is opened.
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

SRC = os.path.join(g.CLAUDEDEV, "OpConnectNested_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
EX = os.path.join(g.CLAUDEDEV, "NIScriptingExamples", "Finding and Modifying Objects", "Navigating Nodes and Wires.vi")
EX_TMSC_UID, EX_TMSC_FN_INDEX = 99, 6      # measured: diag_connectnested_v1_facts.log D5
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
BENCH = os.path.join(ROOT, "tools", "bench")
MAP_OUT = os.path.join(BENCH, "opconnectnested_v1_labels.json")
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_cnv1_{STAMP}.vi")
BOOLVI = r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\file.llb\Is Path and Not Empty.vi"
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")
ORIG = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking\Min_Track N beads V6_ParallelLoop.vi"
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"
g._run.__defaults__ = (6.0, 120.0)

passes, fails, facts = [], [], []


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(f"  {'PASS' if ok else '**FAIL**'}  {name}{('  ' + detail) if detail else ''}", flush=True)
    if not ok and fatal:
        raise Stop(name)
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


def src_of(w, wire):
    """the node whose SOURCE terminal carries `wire`"""
    for u, (n, lab, rows) in w.items():
        for r in rows:
            if r["is_source"] and r["wire"] == wire and wire:
                return u
    return None


def connect(target, src_uid, src_name, dst_uid, dst_name, branch=False, tag=""):
    """Wire by NAME, verified by the SAME wire uid on BOTH ends (build_opconnectnested_v0.connect verbatim)."""
    w = walk(target, 0)
    g.wire(target, cls_of(src_uid, w), idx(target, cls_of(src_uid, w), src_uid), src_name,
           cls_of(dst_uid, w), idx(target, cls_of(dst_uid, w), dst_uid), dst_name, branch=branch)
    w = walk(target, 0)
    a = (term(w[src_uid][2], src_name, True) or {}).get("wire")
    b = (term(w[dst_uid][2], dst_name, False) or {}).get("wire")
    ok = bool(a) and a == b
    print(f"      {tag}#{src_uid}.{src_name!r} -> #{dst_uid}.{dst_name!r}: wire {a} / {b} "
          f"{'OK' if ok else 'MISMATCH'}", flush=True)
    if not ok:
        raise Stop(f"wire #{src_uid}.{src_name!r} -> #{dst_uid}.{dst_name!r} not on both ends ({a} vs {b})")
    return a


def del_net(target, wire_uid, tag=""):
    order = [o["uid"] for o in g.report_all(target, "Wire")]
    if wire_uid not in order:
        raise Stop(f"{tag}: wire {wire_uid} not in the Wire traverse order")
    g.delete_object(target, "Wire", order.index(wire_uid))
    g.remove_bad_wires_scripted(target)
    print(f"      {tag}deleted wire net w{wire_uid}", flush=True)


def ladder_from(w, sink_wire, tag):
    """IA(term) <- PN[Terms[]] <- IA(node) <- PN[Nodes[]] <- head-wire, walking back from the Invoke."""
    ia_t = src_of(w, sink_wire)
    w_arr = term(w[ia_t][2], "array", False)["wire"]
    pn_t = src_of(w, w_arr)
    w_ref_t = term(w[pn_t][2], "reference", False)["wire"]
    ia_n = src_of(w, w_ref_t)
    w_arr_n = term(w[ia_n][2], "array", False)["wire"]
    pn_n = src_of(w, w_arr_n)
    w_head = term(w[pn_n][2], "reference", False)["wire"]
    head = src_of(w, w_head)
    i_ctl = term(w[ia_n][2], "index", False)["wire"]
    print(f"   {tag}: IA(term) #{ia_t} <- PN #{pn_t} <- IA(node) #{ia_n}(index w{i_ctl}) <- PN #{pn_n} "
          f"<- head #{head} (w{w_head})", flush=True)
    return dict(ia_t=ia_t, pn_t=pn_t, ia_n=ia_n, pn_n=pn_n, head=head, head_wire=w_head, idx_wire=i_ctl)


# ============================================================================== BUILD
def build():
    print("\n=== V0: the donor", flush=True)
    gate("V0a OpConnectNested_v0.vi on disk", os.path.exists(SRC), SRC, fatal=True)
    gate("V0b the NI example donor on disk", os.path.exists(EX), EX, fatal=True)
    donor_md5, ex_md5 = md5(SRC), md5(EX)
    g.open_panel(SRC)
    es = g.exec_state(SRC)
    gate("V0 donor ExecState 1", es == 1, f"ExecState {es}", fatal=True)
    g.close_panel(SRC)

    print("\n=== V1: the copy", flush=True)
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(SRC, OP)
    time.sleep(0.3)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    w = walk(OP, 0)
    tmscs = [u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)]
    es = g.exec_state(OP)
    gate("V1 the copy is runnable with exactly ONE To More Specific Class",
         es == 1 and len(tmscs) == 1 and len(w) == 19, f"ExecState {es}, TMSC {tmscs}, {len(w)} nodes", fatal=True)
    tm_old = tmscs[0]

    print("\n=== V2: identification BY WIRE TOPOLOGY (never by uid)", flush=True)
    inv = next(u for u, (n, lab, rows) in w.items() if lab == "Invoke Node")
    sink = ladder_from(w, term(w[inv][2], "reference", False)["wire"], "SINK  ")
    src = ladder_from(w, term(w[inv][2], "Wire Source", False)["wire"], "SOURCE")
    trav = next(u for u, (n, lab, rows) in w.items() if term(rows, "References", True))
    gate("V2 both ladders currently share ONE head wire off the single TMSC (v0's branch)",
         sink["head"] == tm_old and src["head"] == tm_old and sink["head_wire"] == src["head_wire"]
         and sink["pn_n"] != src["pn_n"],
         f"heads #{sink['head']}/#{src['head']} w{sink['head_wire']}/w{src['head_wire']}; "
         f"Nodes[] PNs #{sink['pn_n']}/#{src['pn_n']}", fatal=True)
    for k, d in (("sink", sink), ("source", src)):
        names = [r["name"] for r in w[d["pn_n"]][2] if r["is_source"] and r["name"] not in ("reference out", "error out")]
        gate(f"V2b the {k} head property node's data output is 'Nodes[]'", names == ["Nodes[]"], f"{names}",
             fatal=True)
    pn_src = src["pn_n"]
    head_wire = sink["head_wire"]
    other = []
    for u, (n, lab, rows) in w.items():
        for r in rows:
            if (not r["is_source"]) and r["wire"] == head_wire and u != pn_src:
                other.append((u, r["name"]))
    fact(f"V2 the TMSC-output net w{head_wire} also feeds {other} (these are re-wired in V4)")

    print("\n=== V3: bare the SOURCE Nodes[] reference, then create the TYPED SEED on it", flush=True)
    del_net(OP, head_wire, "V3 ")
    w = walk(OP, 0)
    b = term(w[pn_src][2], "reference", False)
    gate("V3a the source Nodes[] `reference` is BARE after the net delete", b and b["wire"] == 0,
         f"wire {b and b['wire']}", fatal=True)
    before_ctl = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    _new, seed_label = g.create_control(OP, w[pn_src][0], term(w[pn_src][2], "reference", False)["i"])
    now_ctl = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before_ctl]
    gate("V3 exactly ONE new control created = the typed seed", len(now_ctl) == 1,
         f"new controls {now_ctl}, op-reported label {seed_label!r}", fatal=True)
    seed = now_ctl[0]
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    gate("V3b the seed arrived WIRED to the source Nodes[] `reference`",
         bool(pw.get(seed, {}).get("wire")), f"seed {seed!r} wire {pw.get(seed, {}).get('wire')}", fatal=True)
    fact(f"V3 seed control {seed!r} (uid {pw[seed]['uid']}) on w{pw[seed]['wire']}")

    print("\n=== V4: restore the old TMSC's other sinks; build the SOURCE-DIAGRAM Index Array", flush=True)
    first = True
    for u, nm in other:
        connect(OP, tm_old, "specific class reference", u, nm, branch=not first, tag="V4 ")
        first = False
    ia0 = g.uids(OP, "IndexArray")
    g.build_index_array(OP, (2500, 1500))
    new_ia = g.new_since(OP, "IndexArray", ia0)
    gate("V4a exactly one new Index Array", len(new_ia) == 1, f"{new_ia}", fatal=True)
    ia_new = new_ia[0]["uid"]
    connect(OP, trav, "References", ia_new, "array", branch=True, tag="V4 ")
    w = walk(OP, 0)
    before_ctl = {l for _i, l, ind in g.fp_labels(OP) if not ind}
    _n2, lab2 = g.create_control(OP, w[ia_new][0], term(w[ia_new][2], "index", False)["i"])
    now_ctl = [l for _i, l, ind in g.fp_labels(OP) if not ind and l not in before_ctl]
    gate("V4b exactly ONE new control = the source-diagram index", len(now_ctl) == 1,
         f"{now_ctl} (op-reported {lab2!r})", fatal=True)
    src_diag_ctl = now_ctl[0]
    es = g.exec_state(OP)
    gate("V4 the op is RUNNABLE before the copy (copy_by_index copies the FILE)", es == 1, f"ExecState {es}",
         fatal=True)
    g.save(OP)
    fact(f"V4 saved intermediate ({os.path.getsize(OP)} B); seed {seed!r}, src-diagram control {src_diag_ctl!r}")

    # ---------------------------------------------------------------- V5  the SECOND To More Specific Class
    print("\n=== V5: copy a second To More Specific Class (copy_by_index, the proven route)", flush=True)
    state = {}

    def finish(dst, added):
        # `copy_by_index` hands back `new_since(...)`, i.e. a list of OBJECT DICTS, not uids (run 1 of this build
        # died here with `unhashable type: 'dict'`). Normalise once, and keep accepting a bare uid set.
        add_uids = sorted({o["uid"] if isinstance(o, dict) else o for o in added})
        wd = walk(dst, 0)
        new_tm = [u for u in add_uids if u in wd and term(wd[u][2], "specific class reference", True)]
        if len(new_tm) != 1:
            raise Stop(f"V5 expected exactly ONE new To More Specific Class among {add_uids}, got {new_tm}")
        tm_new = new_tm[0]
        state["tm_new"] = tm_new
        print(f"      V5 new TMSC #{tm_new} Nodes[{wd[tm_new][0]}] terminals "
              f"{[(r['i'], r['name'], r['is_source'], r['wire']) for r in wd[tm_new][2]]}", flush=True)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        del_net(dst, pwd[seed]["wire"], "V5a ")
        wd = walk(dst, 0)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        if pwd[seed]["wire"] or term(wd[state["pn_src"]][2], "reference", False)["wire"]:
            raise Stop("V5a the seed / the source Nodes[] reference are not both free after the net delete")
        i_tm = idx(dst, "Function", tm_new)
        g.wire_control(dst, [seed], "Function", i_tm, ["target class"])
        wd = walk(dst, 0)
        pwd = {r["label"]: r for r in g.panel_wiring(dst)}
        a, b = pwd[seed]["wire"], term(wd[tm_new][2], "target class", False)["wire"]
        print(f"      V5b seed {seed!r} -> new TMSC 'target class': wire {a} / {b} "
              f"{'OK' if a and a == b else 'MISMATCH'}", flush=True)
        if not (a and a == b):
            raise Stop("V5b seed -> new TMSC 'target class' not on both ends")
        connect(dst, state["ia_new"], "element", tm_new, "reference", tag="V5c ")
        connect(dst, tm_new, "specific class reference", state["pn_src"], "reference", tag="V5d ")
        g.set_auto_error_handling(dst, False)
        print(f"      V5 ExecState inside finish: {g.exec_state(dst)}", flush=True)

    state["pn_src"], state["ia_new"] = pn_src, ia_new
    g.close_panel(OP)
    added, sel = g.copy_by_index(EX, "Function", EX_TMSC_FN_INDEX, OP, expect_uid=EX_TMSC_UID, finish=finish)
    fact(f"V5 copy_by_index added "
         f"{sorted({o['uid'] if isinstance(o, dict) else o for o in added})}, selected uid {sel}")

    print("\n=== V6: re-read the finished op", flush=True)
    g.open_panel(OP)
    time.sleep(0.6)
    w = walk(OP, 0)
    tmscs = [u for u, (n, lab, rows) in w.items() if term(rows, "specific class reference", True)]
    gate("V6a the op now holds TWO To More Specific Class nodes", len(tmscs) == 2, f"{tmscs}")
    inv = next(u for u, (n, lab, rows) in w.items() if lab == "Invoke Node")
    sink2 = ladder_from(w, term(w[inv][2], "reference", False)["wire"], "SINK  ")
    src2 = ladder_from(w, term(w[inv][2], "Wire Source", False)["wire"], "SOURCE")
    gate("V6 the two ladders now have DIFFERENT heads and DIFFERENT diagram-index wires",
         sink2["head"] != src2["head"] and sink2["head_wire"] != src2["head_wire"]
         and sink2["ia_n"] != src2["ia_n"],
         f"heads #{sink2['head']}/#{src2['head']}, head wires w{sink2['head_wire']}/w{src2['head_wire']}")
    # the source head's own `reference` must come from the NEW Index Array on the Traverse array
    w_ref_new = term(w[src2["head"]][2], "reference", False)["wire"]
    gate("V6b the SOURCE TMSC's `reference` is fed by the NEW Index Array",
         src_of(w, w_ref_new) == ia_new, f"fed by #{src_of(w, w_ref_new)}, expected #{ia_new}")
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    gate("V6c the SOURCE-diagram index control drives the new Index Array's `index`",
         pw[src_diag_ctl]["wire"] and pw[src_diag_ctl]["wire"] == term(w[ia_new][2], "index", False)["wire"],
         f"{src_diag_ctl!r} wire {pw[src_diag_ctl]['wire']}")

    print("\n=== V7: save", flush=True)
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:
        fact(f"set_auto_error_handling failed ({str(e)[:60]})")
    es = g.exec_state(OP)
    gate("V7 ExecState 1 - the op is runnable", es == 1, f"ExecState {es}", fatal=True)
    g.save(OP)
    labels = {"route": "A-cross-diagram", "vi_path": "vi path", "class_name": "Class Name",
              "sink_diag": "index", "sink_node": "index 2", "sink_term": "index 3",
              "src_node": "index 4", "src_term": "index 5", "src_diag": src_diag_ctl,
              "seed": seed, "method": "6349C03",
              "panel": [(i, lbl, ind) for i, lbl, ind in g.fp_labels(OP)]}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact(f"saved {OP} ({os.path.getsize(OP)} bytes); labels -> {MAP_OUT}")
    gate("V7b donor OpConnectNested_v0.vi md5 unchanged", md5(SRC) == donor_md5, donor_md5)
    gate("V7c NI example md5 unchanged", md5(EX) == ex_md5, ex_md5)
    try:
        g.close_panel(OP)
    except Exception:
        pass
    return labels


# ============================================================================== the wrapper
def connect_nested_v1(target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, labels):
    """Wire Diagram[src_diag].Nodes[src_node].Terminals[src_term] (SOURCE) into
    Diagram[sink_diag].Nodes[sink_node].Terminals[sink_term] (SINK). Returns (wire delta, ExecState, error)."""
    g.ensure_loaded(target)
    w0 = g.count(target, "Wire")
    vi = g.op(OP)
    vi.SetControlValue(labels["vi_path"], target)
    vi.SetControlValue(labels["class_name"], "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["src_diag"], int(src_diag))
    vi.SetControlValue(labels["src_node"], int(src_node))
    vi.SetControlValue(labels["src_term"], int(src_term))
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
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else f"EXC {str(e)[:140]}"
    # the op's own readouts on the SINK terminal's wire; REPORTED, never gated - their dataflow order relative to
    # the Connect Wire invoke is not fixed (both take the same terminal reference), so they may pre-date the wire.
    rd = {}
    for k in ("UID", "Name", "UID 2", "Is Broken?"):
        try:
            rd[k] = vi.GetControlValue(k)
        except Exception:
            pass
    print(f"      op readback {rd}", flush=True)
    return g.count(target, "Wire") - w0, g.exec_state(target), err


# ============================================================================== FUNCTIONAL TEST
def test(labels):
    print("\n=== T: FUNCTIONAL test - TWO nested diagrams on a scratch copy of EMPTY_v0", flush=True)
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
        nA = g.new_since(SCRATCH, "Diagram", dg0)
        dg1 = g.uids(SCRATCH, "Diagram")
        g.while_loop(SCRATCH, (1600, 300))
        nB = g.new_since(SCRATCH, "Diagram", dg1)
        nwl = g.new_since(SCRATCH, "WhileLoop", wl0)
        gate("T1 two While loops, two new body diagrams", len(nwl) == 2 and len(nA) == 1 and len(nB) == 1,
             f"loops {[o['uid'] for o in nwl]}, bodies A {[o['uid'] for o in nA]} B {[o['uid'] for o in nB]}",
             fatal=True)
        DA, DB = nA[0]["uid"], nB[0]["uid"]
        order = [o["uid"] for o in g.report_all(SCRATCH, "Diagram")]
        iA, iB = order.index(DA), order.index(DB)
        fact(f"scratch: body A Diagram #{DA} at Traverse index {iA}; body B Diagram #{DB} at index {iB}")

        # B4 (prior-art, ADOPTED): the SAME subVI in both bodies, so the pair under test is
        # NAMED `error out` -> NAMED `error in (no error)` - type-compatible by construction.
        sv0 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, iA, (60, 60))
        aA = g.new_since(SCRATCH, "SubVI", sv0)
        sv1 = g.uids(SCRATCH, "SubVI")
        g.drop_subvi(SCRATCH, NUMVI, iB, (60, 60))
        aB = g.new_since(SCRATCH, "SubVI", sv1)
        gate("T1b one subVI in each body", len(aA) == 1 and len(aB) == 1,
             f"A {[o['uid'] for o in aA]} B {[o['uid'] for o in aB]}", fatal=True)
        UA, UB = aA[0]["uid"], aB[0]["uid"]
        wA, wB = walk(SCRATCH, iA), walk(SCRATCH, iB)
        nA_i, _l, rowsA = wA[UA]
        nB_i, _l2, rowsB = wB[UB]
        fact(f"T1 body A #{UA} Nodes[{nA_i}] outs "
             f"{[(r['i'], r['name']) for r in rowsA if r['is_source']]}")
        fact(f"T1 body B #{UB} Nodes[{nB_i}] bare ins "
             f"{[(r['i'], r['name']) for r in rowsB if not r['is_source'] and r['wire'] == 0]}")

        # ---------------- T2 THE GATE: cross-diagram body(A) -> body(B)
        t_out = next((r["i"] for r in rowsA if r["is_source"] and r["name"] == "error out"), None)
        t_in = next((r["i"] for r in rowsB if not r["is_source"] and r["name"]
                     and "error in" in r["name"] and r["wire"] == 0), None)
        if t_out is None or t_in is None:
            gate("T2 an error-out/error-in pair was found across the two bodies", False,
                 f"t_out {t_out} t_in {t_in}")
        else:
            es_before = g.exec_state(SCRATCH)
            lt_before = g.count(SCRATCH, "LoopTunnel")
            dw, es, err = connect_nested_v1(SCRATCH, iB, nB_i, t_in, iA, nA_i, t_out, labels)
            wA2, wB2 = walk(SCRATCH, iA), walk(SCRATCH, iB)
            w_sink = next((r["wire"] for r in wB2[UB][2] if r["i"] == t_in), 0)
            w_src = next((r["wire"] for r in wA2[UA][2] if r["i"] == t_out), 0)
            lt = g.count(SCRATCH, "LoopTunnel")
            fact(f"T2 op error {err[:140]!r}; wire delta {dw}; LoopTunnel {lt_before} -> {lt}; "
                 f"ExecState {es_before} -> {es}")
            gate("T2 CROSS-DIAGRAM: the sink on body B is WIRED (0 -> non-zero)", bool(w_sink),
                 f"sink w{w_sink}, source w{w_src}")
            fact(f"T2 wire uids: sink w{w_sink} / source w{w_src} "
                 f"({'same uid' if w_sink == w_src else 'DIFFERENT - LabVIEW made tunnels + segments'})")
            # B4 (prior-art, ADOPTED): uid equality does NOT prove the wire is good. RBW deletes a BROKEN wire
            # and leaves a GOOD one - that is the discriminator uid equality cannot make (NAMES.md:861-863).
            g.remove_bad_wires_scripted(SCRATCH)
            wB4 = walk(SCRATCH, iB)
            w_after = next((r["wire"] for r in wB4[UB][2] if r["i"] == t_in), 0)
            es_rbw = g.exec_state(SCRATCH)
            gate("T2c THE REAL GATE: the cross-diagram wire SURVIVES Remove Bad Wires (i.e. it is not broken)",
                 bool(w_after) and w_after == w_sink, f"sink wire after RBW: {w_after} (was {w_sink})")
            gate("T2b the scratch is no MORE broken than before the wire "
                 "(a fresh While loop's unwired conditional terminal is itself a break - NAMES.md:788)",
                 es == es_before or es == 1, f"ExecState {es_before} -> {es} -> {es_rbw} after RBW")

        # ---------------- T3 cross-diagram into an UNNAMED terminal of a nested structure
        fl0 = g.uids(SCRATCH, "ForLoop")
        g.for_loop(SCRATCH, (900, 1400))
        nfl = g.new_since(SCRATCH, "ForLoop", fl0)
        if gate("T3a a For loop was created on the top-level diagram", len(nfl) == 1, f"{nfl}"):
            F = nfl[0]["uid"]
            moved = False
            try:
                from build_d1_v0 import move_in as _move_in
                _move_in(SCRATCH, F, iA, (400, 400))
                moved = F in walk(SCRATCH, iA)
                fact(f"T3 For loop #{F} reparented into body A: {moved}")
            except Exception as e:
                fact(f"T3 move_in failed ({str(e)[:160]}) - the For loop stays on the top level")
            d_tgt = iA if moved else 0
            wt = walk(SCRATCH, d_tgt)
            if F in wt:
                nF, _lf, rowsF = wt[F]
                unnamed = [(r["i"], r["wire"]) for r in rowsF if not r["is_source"] and not r["name"]]
                fact(f"T3 For loop #{F} on diagram {d_tgt} Nodes[{nF}]: unnamed input terminals {unnamed}")
                if unnamed:
                    t_un = unnamed[0][0]
                    wB3 = walk(SCRATCH, iB)
                    tried = []
                    for r in wB3[UB][2]:
                        if not r["is_source"]:
                            continue
                        dw, es, err = connect_nested_v1(SCRATCH, d_tgt, nF, t_un, iB, wB3[UB][0], r["i"], labels)
                        w_un = next((x["wire"] for x in walk(SCRATCH, d_tgt)[F][2] if x["i"] == t_un), 0)
                        tried.append((r["i"], r["name"], dw, es, w_un, err[:60]))
                        if w_un:
                            break
                    for x in tried:
                        print(f"      T3 try src t{x[0]} {x[1]!r}: delta {x[2]}, ExecState {x[3]}, "
                              f"unnamed-terminal wire {x[4]}, err {x[5]!r}", flush=True)
                    gate("T3 an UNNAMED terminal on diagram P is reached from a source on diagram Q "
                         "(wire 0 -> non-zero)", bool(tried) and bool(tried[-1][4]),
                         f"{tried[-1] if tried else 'no attempt'}")
                    fact(f"T3 ExecState after the unnamed-terminal wire: {g.exec_state(SCRATCH)} "
                         f"(a type-incompatible pair makes a BROKEN wire - a LabVIEW type fact, not an op "
                         f"failure; the gate above is wire identity)")
                else:
                    gate("T3 the For loop exposes an unnamed input terminal", False, f"{rowsF}")
            else:
                gate("T3 the For loop is on the expected diagram", False, f"#{F} not on diagram {d_tgt}")

        junk = [u for u in g.uids(SCRATCH, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(SCRATCH, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(SCRATCH, "Invoke", i, verify=False)
        fact(f"T4 junk Invokes purged: {junk}")
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        try:
            os.remove(SCRATCH)
            fact(f"scratch deleted: {os.path.basename(SCRATCH)}")
        except Exception as e:
            fact(f"scratch NOT deleted ({str(e)[:80]})")


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    g._lv = None
    t0 = time.time()
    h0 = labview_handles()
    fact(f"LabVIEW handles before: {h0} (fresh-instance baseline ~31,500)")
    gate("V0z original working-copy md5 before", md5(ORIG) == ORIG_MD5, md5(ORIG))
    labels = None
    try:
        labels = build()
        if labels:
            test(labels)
    except Stop as e:
        fact(f"STOPPED at a fatal gate: {e}")
    except Exception as e:
        gate("Vx build/test completed without an unhandled exception", False, f"EXC {str(e)[:300]}")
    finally:
        for p in (OP, SCRATCH):
            try:
                g.close_panel(p)
            except Exception:
                pass
        g._lv = None
    gate("Vz original working-copy md5 after", md5(ORIG) == ORIG_MD5, md5(ORIG))
    fact(f"LabVIEW handles after: {labview_handles()} (before {h0})")
    print("\n--- FACTS ---", flush=True)
    for x in facts:
        print("  " + x, flush=True)
    print(f"\n=== build_opconnectnested_v1: {len(passes)} pass, {len(fails)} fail"
          + (f" -> {', '.join(fails)}" if fails else "") + f"  ({time.time() - t0:.0f} s) ===", flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
