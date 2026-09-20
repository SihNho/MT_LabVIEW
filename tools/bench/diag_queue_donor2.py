r"""diag_queue_donor2 - Pre-decided 35(b) ROUND 2. The two donor shapes round 1 did NOT measure.

🔴 THIS IS A DIAGNOSTIC, NOT A STAGE AND NOT A RECIPE. It lives in `tools/bench/`, it produces READINGS
(`tools/bench/diag_queue_donor2.json` + this log), and it must never be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND PICKS NOTHING. 35(b) reserves the choice of donor - and the writing of any queue stage -
for the judgement session. Nothing here is a recommendation.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is. No motor,
no ASI, no camera, no GUI action. The ORIGINAL is never opened or written (its md5 is probed at both ends);
`claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are NEVER opened or written. Every edit happens on a
dated SCRATCH copy of `D1_s1_copy.vi`, and that scratch is left SAVED with its md5 recorded.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53). Where this file sets a control value that an
existing wrapper hard-codes (`OpCreateConstOnTerm_v0`'s `Class Name`), it is calling a BUILT op with a different
input, not building anything.

WHAT ROUND 1 ALREADY SETTLED (`tools/bench/diag_queue_donor.py` / `.log` / `.json`, 12/0) AND IS NOT REDONE:
  * `queue_node('obtain')` ACCEPTS a node's named output (#8486 `x+1`) and a `WhileLoop`'s OUTER named terminal
    (#637 `current image number`), and REFUSES a diagram constant placed by `OpCreateConst_v0`
    (`error 1057: To More Specific Class in OpQueueObtain_v0.vi`; the constant is not in `AbstractDiagram.Nodes[]`
    and exposes no named source terminal).
  * Round 1's `create_control` attempt started from a Diagram-#686 `Nodes[]` index. `docs/NAMES.md:278` and
    `:474-475` MEASURED that `create_control`'s ladder walks the **TOP-LEVEL** `Nodes[]` - so that index was in the
    wrong address space and the attempt measured the attempt, not the shape. This file re-measures it properly.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line: `grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `gscript.create_control` `:2360` (OpCreateControl_v1, top-level ladder), `gscript.build_index_array` `:2322`,
    `gscript.drop_subvi` `:1225`, `gscript.queue_node` `:1122`, `gscript.delete_object` `:2240`,
    `count/uids/new_since/report_all/open_panel/close_panel/exec_state/save/node_labels/node_terms_uid`.
  * `build_d1_v0.move_in` `:318` / `owner_of` `:338` / `diag_index` `:357` / `terms_of` `:375`.
  * `build_opcreateconstonterm_v0.create_const_on_term` `:364` and `read_const` `:392` - the BUILT caller/reader
    of `OpCreateConstOnTerm_v0.vi` (labels `tools/bench/opcreateconstonterm_labels.json`).
  * `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147` / `idx` `:158` - the BUILT diagram census.
  * `build_opwiresource_v5.read_terminal` `:155` - the BUILT "which object drives this wire" reader (its `MAIN`
    module global is monkeypatched to the scratch, the way `build_d1_v0.owner_of` does it; the toolkit row warns
    the function otherwise hard-codes the ORIGINAL as `vi path`).
  * `diag_s2_scaffold.fresh` `:155` / `file_facts` `:142` / `Preload` `:167` / `census_686` `:198` /
    `NON_SCALAR_NAME_RE` `:96`; `hash_probe.probe` (34(k)); `bench_prep.labview_handles`.
Nothing new is built.

THE TWO SHAPES

SHAPE 1 - A FRONT-PANEL CONTROL AS THE DONOR. Two documented BUILT routes to a control of a CHOSEN type make the
  type deliberate rather than whatever terminal happened to be bare:
    scalar     `build_index_array` (an unwired Index Array on the TOP-LEVEL diagram) -> `create_control` on its
               `index` terminal (I32) - `docs/NAMES.md:476-478`.
    non-scalar `drop_subvi(Error Cluster From Error Code.vi)` on the TOP-LEVEL diagram -> `create_control` on a
               CLUSTER/ARRAY-shaped input terminal of it (`error in (no error)`) - the same trick as the String[]
               control at `docs/NAMES.md:832-835`.
  For each: where does the ControlTerminal LAND (owner Diagram uid)? `create_control`'s ladder is top-level, so
  the terminal cannot be born on `Diagram #686`; `move_in` (uid-addressed, BUILT) is then asked to relocate it
  there, and the owner is RE-READ. Then: does it appear in `#686`'s `AbstractDiagram.Nodes[]`, what named SOURCE
  terminal (`out_name`) does it expose, and does `queue_node('obtain')` accept it - verbatim error on refusal.

SHAPE 2 - TYPE THE QUEUE FROM ITS OWN `element data type` INPUT. An `Obtain Queue` is first created on `#686`
  with the round-1 baseline donor (#8486 `x+1`), because `queue_node` is the only creator of that node and it
  always needs a (node, named output) pair. `OpCreateConstOnTerm_v0` is then asked to put a constant straight onto
  that node's `element data type` INPUT terminal. Its ladder is
  `Traverse(Class Name)[index] -> To More Specific Class -> Loop.Diagram 6361401 -> AbstractDiagram.Nodes[] ->
  Node.Terms[] -> Invoke Terminal[Create Constant 6349C00]` (`build_opcreateconstonterm_v0.py:17-24`), i.e. the
  container is downcast to a LOOP. Whether that is INTRINSIC is measured, not asserted:
    (a) `Class Name`='Diagram', `index`= Traverse index of `#686`            -> verbatim error
    (b) `Class Name`= the measured CLASS of `#686`'s owner, its Traverse index -> verbatim error
    (c) POSITIVE CONTROL on a real loop body: `Class Name`='WhileLoop', `index`= the frame loop #637, a node on
        its body diagram with a BARE named input - proves the op is functional in THIS scratch, so a refusal in
        (a)/(b) is about the diagram class and not about the call.
  If any attempt places a constant, the `Obtain Queue`'s terminal wire is re-read and the constant's class/value
  are read back with `OpConstValueN_v1` (`read_const`).

SHAPE 3 - DEPENDENCY, for every shape that is ACCEPTED: does the donor's source depend on `#637`? For a node
  donor, every INPUT wire is traced to its driving object with `OpWireSource_v5` and the driver's owner is
  reported; for a ControlTerminal donor there are no inputs; for `#637`'s own outer terminal the dependency is
  total by construction. This is the property 35(a) actually cares about.

PREDICTION CONTRACT (each line is a printed GATE; only the file gates are FATAL - this is a measurement and every
later reading is wanted even when an earlier one fails)
  R0  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859; `claudeDev\D1_s1_copy.vi` exists.       FATAL
  R1  the scratch copy is byte-identical to `D1_s1_copy.vi` (md5 3e3d23cefd3a334001aa9d6156bf1aee).       FATAL
  R2  the TOP-LEVEL block diagram is identified and its uid is NOT 686 (the address space `create_control`
      walks is named, not assumed).
  R3  node #8486 still offers the named source terminal `x+1` on Diagram #686 (34(h)).
  R4a a SCALAR control is created and its ControlTerminal's owner Diagram is RECORDED (either value legitimate).
  R4b a NON-SCALAR control is created and its ControlTerminal's owner Diagram is RECORDED.
  R4c for every created ControlTerminal, `move_in` to Diagram #686 is attempted and the owner RE-READ.
  R4d every ControlTerminal that reached #686 is scored against `queue_node('obtain')` with its verbatim error.
  R5  the baseline `Obtain Queue` is created on #686 and its `element data type` terminal index is READ.
  R6a/b/c the three `OpCreateConstOnTerm_v0` attempts are MADE and scored with their verbatim errors.
  R7  a dependency reading is recorded for every ACCEPTED shape.
  R8  the scratch's ExecState and the save attempt are recorded (either value legitimate); md5 recorded.
  R9  no live VI Server reference is left open.
  R10 the ORIGINAL's md5 is unchanged; `D1_s1_copy.vi` and `D1_s2_loops.vi` are unchanged.                FATAL
"""
import json
import os
import re
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, terms_of                   # noqa: E402
from build_opstopfromnode_v0 import walk as WALK, cls_of, idx as cls_index        # noqa: E402
import build_opcreateconstonterm_v0 as COT                                        # noqa: E402
import build_opwiresource_v5 as WS                                                # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1 = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2 = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_qdonor2_%s.vi" % STAMP)    # unique per run (CLAUDE.md scratch rule)
OUT = os.path.join(HERE, "diag_queue_donor2.json")

SIBLING_DIAG_UID = D.SIBLING_DIAG_UID            # 686
FRAME_LOOP_UID = 637
FRAME_BODY_UID = 639                             # diag_s2_scaffold.py:461 - VERIFIED here by owner_of, not assumed
BASELINE_OPERAND = (8486, "x+1")                 # round 1's ACCEPTED donor, by NAME
EDT_NAME = "element data type"                   # docs/NAMES.md:773-774, the Obtain Queue node's own input
NUMVI = (r"C:\Program Files\National Instruments\LabVIEW 2026\vi.lib\Utility\error.llb"
         r"\Error Cluster From Error Code.vi")   # build_opcreateconstonterm_v0.py:98-99
NON_SCALAR = D.NON_SCALAR_NAME_RE
IA_AT = (2600, 6000)
SUBVI_AT = (3200, 6000)
MOVE_AT = {"C1": (2600, 6400), "C2": (3000, 6400)}
QN_AT = {"C1": (2600, 6800), "C2": (3100, 6800), "BASE": (3600, 6800)}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "no_vi_was_run": True, "picks_nothing": True,
     "question": "Pre-decided 35(b) round 2: shape 1 = a front-panel control donor; shape 2 = a constant on the "
                 "Obtain Queue's own element-data-type input; shape 3 = each accepted shape's dependency on #637",
     "files": {}, "geometry": {}, "shape1": {}, "shape2": {}, "shape3": {}, "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def safe(fn, *a, **kw):
    """Run a measurement call and return (value, error-string) - a refusal is a reading, never a crash."""
    try:
        return fn(*a, **kw), None
    except Exception as e:                                                        # noqa: BLE001
        return None, "%s: %s" % (type(e).__name__, str(e)[:400])


def owner(target, uid):
    (o, err) = safe(owner_of, target, uid, strict=False)
    return (o if o else (None, None)), err


def walk_rows(target, diagram_index, limit=200):
    """[{uid, node_index, label, class_guess, in_bare, out_named}] for one diagram - the BUILT census."""
    w = WALK(target, diagram_index, limit=limit)
    rows = []
    for uid, (ni, label, terms) in w.items():
        rows.append({"uid": uid, "node_index": ni, "label": label, "class_guess": cls_of(uid, w),
                     "out_named": [(r["i"], r["name"]) for r in terms
                                   if r["is_source"] and (r["name"] or "").strip()],
                     "in_bare": [(r["i"], r["name"]) for r in terms
                                 if (not r["is_source"]) and r["wire"] == 0 and (r["name"] or "").strip()],
                     "n_terms": len(terms)})
    rows.sort(key=lambda r: r["node_index"])
    return w, rows


# ---------------------------------------------------------------- OpCreateConstOnTerm_v0 with a chosen container
def const_on_term(target, cls_name, cls_idx, node_i, term_i, labels, value=None):
    """`build_opcreateconstonterm_v0.create_const_on_term` VERBATIM except that the container CLASS is an argument
    instead of the hard-coded 'WhileLoop' (the op's own `Class Name` control - a different INPUT to a BUILT op,
    not a new op). Returns {err, inv_err, created_uid}."""
    g.ensure_loaded(target)
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpCreateConstOnTerm_v0.vi"))
    if labels.get("uid_ind"):
        vi.SetControlValue(labels["uid_ind"], 0)
    if labels.get("err_ind"):
        vi.SetControlValue(labels["err_ind"], (False, 0, ""))
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(labels["loop_class"], cls_name)
    vi.SetControlValue(labels["loop_index"], int(cls_idx))
    vi.SetControlValue(labels["index_node"], int(node_i))
    vi.SetControlValue(labels["index_term"], int(term_i))
    if labels.get("value_ctl") and value is not None:
        vi.SetControlValue(labels["value_ctl"], value)
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:                                                        # noqa: BLE001
        err = "EXC %s: %s" % (type(e).__name__, str(e)[:300])
    out = {"container_class": cls_name, "container_index": int(cls_idx), "node_index": int(node_i),
           "term_index": int(term_i), "err": err, "inv_err": "", "created_uid": None}
    if labels.get("err_ind"):
        out["inv_err"] = g._err(vi, labels["err_ind"]) or ""
    if labels.get("uid_ind"):
        try:
            out["created_uid"] = int(vi.GetControlValue(labels["uid_ind"]))
        except Exception:                                                         # noqa: BLE001
            pass
    return out


# ---------------------------------------------------------------- one queue_node('obtain') attempt
def q_attempt(shape, target, src_cls, src_index, src_name, d686, why, extra=None):
    rec = {"shape": shape, "src_cls": src_cls, "src_index": src_index, "src_name": src_name, "why": why,
           "accepted": False, "error": None, "new_function_uids": []}
    if extra:
        rec.update(extra)
    before = set(g.uids(target, "Function"))
    new, err = safe(g.queue_node, "obtain", target, src_cls, int(src_index), src_name, d686, QN_AT[shape])
    rec["returned"] = new
    rec["error"] = err
    after = set(g.uids(target, "Function"))
    rec["new_function_uids"] = sorted(after - before)
    rec["accepted"] = bool(rec["new_function_uids"]) and not err
    fact("QUEUE-ATTEMPT %s (%s[%s] . %r - %s): accepted=%s; new Function uids %r; op error %r"
         % (shape, src_cls, src_index, src_name, why, rec["accepted"], rec["new_function_uids"], err))
    return rec


# ---------------------------------------------------------------- shape 3: who drives this wire
def wire_driver(target, wire_uid, max_terms=6):
    """Every terminal of one wire through OpWireSource_v5 (UID-addressed), returning the SOURCE rows."""
    lab = json.load(open(os.path.join(HERE, "opwiresource_v5_labels.json"), encoding="utf-8"))
    vi = g.op(os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi"))
    saved = WS.MAIN
    rows = []
    try:
        WS.MAIN = target
        for i in range(max_terms):
            r, err = safe(WS.read_terminal, vi, lab, int(wire_uid), i)
            if r is None:
                rows.append({"index": i, "call_error": err})
                break
            rows.append(r)
            if r.get("errs") and r.get("owner_uid") == 0 and not r.get("is_source"):
                break
    finally:
        WS.MAIN = saved
    return [r for r in rows if r.get("is_source")], rows


def dependency_of_node(target, diagram_index, uid, label):
    """Every INPUT wire of one node, traced to its driving object's owner - 35(a)'s actual property."""
    rec = {"uid": uid, "label": label, "diagram_index": diagram_index, "inputs": [], "driver_owner_uids": [],
           "depends_on_frame_loop": None}
    t, err = safe(terms_of, target, diagram_index, uid, fresh=True)
    if t is None:
        rec["error"] = err
        fact("DEPENDENCY #%s: terms_of raised %s" % (uid, err))
        return rec
    fed = [(i, nm, wv) for i, (nm, src, wv) in t.items() if (not src) and wv]
    rec["n_terminals"] = len(t)
    rec["fed_inputs"] = fed
    fact("DEPENDENCY #%s %r: %d terminals, %d INPUT terminals carry a wire: %r"
         % (uid, label, len(t), len(fed), fed[:10]))
    for i, nm, wv in fed:
        srcs, allrows = wire_driver(target, wv)
        row = {"term_index": i, "term_name": nm, "wire": wv,
               "sources": [{"owner_class": s.get("owner_class"), "owner_uid": s.get("owner_uid"),
                            "cast_class": s.get("cast_class"), "err": s.get("err"), "errs": s.get("errs")}
                           for s in srcs],
               "terminals_read": len(allrows)}
        rec["inputs"].append(row)
        for s in srcs:
            if s.get("owner_uid"):
                rec["driver_owner_uids"].append(int(s["owner_uid"]))
        fact("DEPENDENCY #%s t%d %r wire %s <- sources %r" % (uid, i, nm, wv, row["sources"]))
    owners = set(rec["driver_owner_uids"])
    rec["depends_on_frame_loop"] = (FRAME_LOOP_UID in owners) if fed else False
    for u in list(owners):
        if u == FRAME_LOOP_UID:
            continue
        (ocls, ouid), _e = owner(target, u)
        rec.setdefault("driver_owner_chain", []).append({"driver_uid": u, "owner_class": ocls, "owner_uid": ouid})
        if ouid == FRAME_LOOP_UID or ouid == SIBLING_DIAG_UID:
            pass
    fact("DEPENDENCY #%s: driving-object owner uids %r; owner chain %r; a DIRECT feed from WhileLoop #%d: %s"
         % (uid, sorted(owners), rec.get("driver_owner_chain"), FRAME_LOOP_UID, rec["depends_on_frame_loop"]))
    return rec


# ================================================================================================= main
def main():
    print("=== diag_queue_donor2  %s   (Pre-decided 35(b) ROUND 2; NO VI IS RUN, 34(f); PICKS NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])

    print("\n--- the files (read-only probes, 34(k))", flush=True)
    o = probe("ORIGINAL", ORIGINAL)
    s1 = probe("S1 claudeDev\\D1_s1_copy.vi", S1)
    s2 = probe("S2 claudeDev\\D1_s2_loops.vi (never opened by this file)", S2)
    R["files"] = {"original": o, "s1": s1, "s2": s2}
    gate("R0 the ORIGINAL and the S1 artefact exist and the ORIGINAL's md5 equals the pin",
         o.get("md5") == ORIG_MD5 and s1.get("exists") == "1",
         "orig md5 %s; s1 exists %s" % (o.get("md5"), s1.get("exists")), fatal=True)

    D.fresh("F1")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S1, SCRATCH)
    sc = probe("the scratch copy", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "after_copy": sc}
    gate("R1 the scratch copy is byte-identical to D1_s1_copy.vi", sc.get("md5") == S1_MD5,
         sc.get("md5", "?"), fatal=True)

    cot_labels = json.load(open(os.path.join(HERE, "opcreateconstonterm_labels.json"), encoding="utf-8"))

    with D.Preload("P"):
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        R["before_census"] = {c: g.count(SCRATCH, c) for c in
                              ("Diagram", "WhileLoop", "SubVI", "Function", "Constant", "ControlTerminal",
                               "Wire", "Comparison", "LoopTunnel", "IndexArray")}
        fact("class census of the scratch BEFORE any edit: %r" % R["before_census"])

        # ----------------------------------------------------------------- geometry
        print("\n--- geometry: Diagram #%d, the TOP-LEVEL diagram, and the frame loop's body"
              % SIBLING_DIAG_UID, flush=True)
        d686 = diag_index(SCRATCH, SIBLING_DIAG_UID)
        (o686cls, o686uid), e686 = owner(SCRATCH, SIBLING_DIAG_UID)
        fact("Diagram #%d reads Traverse index %d; its OWNER is %r #%s (err %r)"
             % (SIBLING_DIAG_UID, d686, o686cls, o686uid, e686))
        o686_index, o686_ie = safe(cls_index, SCRATCH, o686cls, o686uid) if o686cls else (None, "no owner class")
        fact("the owner of Diagram #%d addresses as Traverse %r[%r] (err %r)"
             % (SIBLING_DIAG_UID, o686cls, o686_index, o686_ie))

        diag_uids = [x["uid"] for x in g.report_all(SCRATCH, "Diagram")]
        top_uid, top_i, top_owner = None, None, None
        for i in range(min(3, len(diag_uids))):
            (ocls, ouid), _e = owner(SCRATCH, diag_uids[i])
            fact("Diagram Traverse[%d] = #%d, owner %r #%s" % (i, diag_uids[i], ocls, ouid))
            if top_uid is None and (ocls or "").lower().startswith(("virtual", "vi")):
                top_uid, top_i, top_owner = diag_uids[i], i, ocls
        if top_uid is None:
            top_uid, top_i, top_owner = diag_uids[0], 0, "(owner class did not name the VI - index 0 assumed)"
        R["geometry"] = {"d686_index": d686, "d686_owner_class": o686cls, "d686_owner_uid": o686uid,
                         "d686_owner_traverse_index": o686_index, "top_diagram_uid": top_uid,
                         "top_diagram_index": top_i, "top_diagram_owner": top_owner, "n_diagrams": len(diag_uids)}
        gate("R2 the TOP-LEVEL block diagram is identified and is NOT Diagram #%d" % SIBLING_DIAG_UID,
             top_uid is not None and top_uid != SIBLING_DIAG_UID,
             "top-level = Diagram #%s (Traverse[%s], owner %r)" % (top_uid, top_i, top_owner))

        _w686, rows686 = walk_rows(SCRATCH, d686)
        by686 = {r["uid"]: r for r in rows686}
        base = by686.get(BASELINE_OPERAND[0])
        base_ok = bool(base) and any(nm == BASELINE_OPERAND[1] for _i, nm in base["out_named"])
        fact("Diagram #%d holds %d nodes; #%d named source terminals %r"
             % (SIBLING_DIAG_UID, len(rows686), BASELINE_OPERAND[0],
                (base or {}).get("out_named", [])[:8]))
        gate("R3 node #%d still offers the named source terminal %r on Diagram #%d (34(h))"
             % (BASELINE_OPERAND[0], BASELINE_OPERAND[1], SIBLING_DIAG_UID), base_ok)

        _wtop, rowstop = walk_rows(SCRATCH, top_i)
        R["geometry"]["top_nodes"] = rowstop
        fact("the TOP-LEVEL diagram (#%s, Traverse[%s]) holds %d nodes: %r"
             % (top_uid, top_i, len(rowstop),
                [(r["node_index"], r["uid"], r["class_guess"], (r["label"] or "")[:24]) for r in rowstop[:14]]))
        for r in rowstop:
            if r["in_bare"]:
                fact("   TOP node Nodes[%d] #%d %s bare named INPUTS %r"
                     % (r["node_index"], r["uid"], r["class_guess"], r["in_bare"][:8]))

        (fb_cls, fb_owner), _e = owner(SCRATCH, FRAME_BODY_UID)
        fact("Diagram #%d's owner is %r #%s (expected WhileLoop #%d - VERIFIED, not assumed)"
             % (FRAME_BODY_UID, fb_cls, fb_owner, FRAME_LOOP_UID))
        R["geometry"]["frame_body_owner"] = {"class": fb_cls, "uid": fb_owner}

        # ================================================================= SHAPE 1
        print("\n--- SHAPE 1: a front-panel CONTROL as the donor (scalar and non-scalar)", flush=True)
        made = {}

        # ---- C1 SCALAR: build_index_array -> create_control on its `index` terminal (NAMES.md:476-478)
        ia0 = g.uids(SCRATCH, "IndexArray")
        ia, ia_err = safe(g.build_index_array, SCRATCH, IA_AT)
        new_ia = g.new_since(SCRATCH, "IndexArray", ia0)
        fact("C1 build_index_array on the TOP-LEVEL diagram at %r: error %r; new IndexArray %r"
             % (IA_AT, ia_err, [(x["uid"], x.get("class")) for x in new_ia]))
        c1 = {"route": "build_index_array -> create_control on its `index` terminal (docs/NAMES.md:476-478)",
              "type_intended": "SCALAR I32", "helper_error": ia_err,
              "helper_uid": new_ia[0]["uid"] if new_ia else None}
        if new_ia:
            _wt, rt = walk_rows(SCRATCH, top_i)
            hit = [r for r in rt if r["uid"] == c1["helper_uid"]]
            if hit:
                h = hit[0]
                c1["helper_node_index"] = h["node_index"]
                cand = [(i, nm) for i, nm in h["in_bare"] if not re.search(NON_SCALAR, nm)] or h["in_bare"]
                c1["helper_bare_inputs"] = h["in_bare"]
                fact("C1 helper IndexArray #%s is TOP-LEVEL Nodes[%d]; bare named inputs %r; trying %r"
                     % (c1["helper_uid"], h["node_index"], h["in_bare"], cand[:1]))
                if cand:
                    ct0 = g.uids(SCRATCH, "ControlTerminal")
                    res, cerr = safe(g.create_control, SCRATCH, h["node_index"], int(cand[0][0]))
                    newct = g.new_since(SCRATCH, "ControlTerminal", ct0)
                    c1.update({"terminal_tried": cand[0], "create_error": cerr,
                               "label": (res[1] if res else None),
                               "new_control_terminals": [(x["uid"], x.get("class")) for x in newct]})
                    fact("C1 create_control(Nodes[%d], t%d) -> error %r, label %r, new ControlTerminal %r"
                         % (h["node_index"], cand[0][0], cerr, c1.get("label"), c1["new_control_terminals"]))
                    if newct:
                        made["C1"] = {"uid": newct[0]["uid"], "label": c1.get("label"), "rec": c1}
            else:
                fact("C1 the new IndexArray is NOT on the top-level Nodes[] walk - no create_control attempt")
        R["shape1"]["C1"] = c1
        gate("R4a a SCALAR control was created and scored", "C1" in made or bool(c1.get("create_error"))
             or bool(c1.get("helper_error")), repr(c1.get("create_error") or c1.get("helper_error")))

        # ---- C2 NON-SCALAR: drop a subVI on the TOP-LEVEL diagram -> create_control on a cluster input
        c2 = {"route": "drop_subvi(Error Cluster From Error Code.vi) on the TOP-LEVEL diagram -> create_control "
                       "on a CLUSTER-shaped input (the docs/NAMES.md:832-835 trick)",
              "type_intended": "NON-SCALAR (error cluster)", "subvi": NUMVI,
              "subvi_on_disk": os.path.exists(NUMVI)}
        sv0 = g.uids(SCRATCH, "SubVI")
        if c2["subvi_on_disk"]:
            _dt, sv_err = safe(g.drop_subvi, SCRATCH, NUMVI, top_i, SUBVI_AT)
            newsv = g.new_since(SCRATCH, "SubVI", sv0)
            c2["helper_error"] = sv_err
            c2["helper_uid"] = newsv[0]["uid"] if newsv else None
            fact("C2 drop_subvi on the TOP-LEVEL diagram at %r: error %r; new SubVI %r"
                 % (SUBVI_AT, sv_err, [(x["uid"], x.get("class")) for x in newsv]))
            if newsv:
                _wt, rt = walk_rows(SCRATCH, top_i)
                hit = [r for r in rt if r["uid"] == c2["helper_uid"]]
                if hit:
                    h = hit[0]
                    c2["helper_node_index"] = h["node_index"]
                    c2["helper_bare_inputs"] = h["in_bare"]
                    cand = [(i, nm) for i, nm in h["in_bare"] if re.search(NON_SCALAR, nm)]
                    fact("C2 helper SubVI #%s is TOP-LEVEL Nodes[%d]; bare named inputs %r; NON-SCALAR-shaped %r"
                         % (c2["helper_uid"], h["node_index"], h["in_bare"], cand[:3]))
                    if cand:
                        ct0 = g.uids(SCRATCH, "ControlTerminal")
                        res, cerr = safe(g.create_control, SCRATCH, h["node_index"], int(cand[0][0]))
                        newct = g.new_since(SCRATCH, "ControlTerminal", ct0)
                        c2.update({"terminal_tried": cand[0], "create_error": cerr,
                                   "label": (res[1] if res else None),
                                   "new_control_terminals": [(x["uid"], x.get("class")) for x in newct]})
                        fact("C2 create_control(Nodes[%d], t%d %r) -> error %r, label %r, new ControlTerminal %r"
                             % (h["node_index"], cand[0][0], cand[0][1], cerr, c2.get("label"),
                                c2["new_control_terminals"]))
                        if newct:
                            made["C2"] = {"uid": newct[0]["uid"], "label": c2.get("label"), "rec": c2}
                    else:
                        c2["create_error"] = "no NON-SCALAR-shaped bare named input on the dropped subVI"
        else:
            c2["helper_error"] = "the donor subVI is not on disk"
        R["shape1"]["C2"] = c2
        gate("R4b a NON-SCALAR control was created and scored", "C2" in made or bool(c2.get("create_error"))
             or bool(c2.get("helper_error")), repr(c2.get("create_error") or c2.get("helper_error")))

        # ---- where the ControlTerminals LANDED, then move_in to Diagram #686, then queue_node
        for key in ("C1", "C2"):
            m = made.get(key)
            if not m:
                continue
            u = m["uid"]
            (ocls, ouid), oerr = owner(SCRATCH, u)
            m["born_owner"] = {"class": ocls, "uid": ouid, "error": oerr}
            fact("%s ControlTerminal #%d (label %r) is BORN owned by %r #%s - Diagram #%d? %s"
                 % (key, u, m["label"], ocls, ouid, SIBLING_DIAG_UID, ouid == SIBLING_DIAG_UID))
            if ouid != SIBLING_DIAG_UID:
                d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)       # 34(h): re-read before use
                nu, merr = safe(move_in, SCRATCH, u, d686_now, MOVE_AT[key])
                (ocls2, ouid2), oerr2 = owner(SCRATCH, u)
                m["move_in"] = {"returned_uid": nu, "error": merr, "owner_class_after": ocls2,
                                "owner_uid_after": ouid2, "owner_error": oerr2}
                fact("%s move_in(ControlTerminal #%d -> Diagram #%d): returned %r, error %r; owner AFTER %r #%s "
                     "=> on Diagram #%d: %s"
                     % (key, u, SIBLING_DIAG_UID, nu, merr, ocls2, ouid2, SIBLING_DIAG_UID,
                        ouid2 == SIBLING_DIAG_UID))
            gate("R4c %s move_in to Diagram #%d attempted and the owner re-read" % (key, SIBLING_DIAG_UID),
                 "move_in" in m or m["born_owner"]["uid"] == SIBLING_DIAG_UID,
                 repr(m.get("move_in", {}).get("error")))

            d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
            _w, rows_now = walk_rows(SCRATCH, d686_now)
            hit = [r for r in rows_now if r["uid"] == u]
            m["in_686_nodes"] = bool(hit)
            m["out_named"] = hit[0]["out_named"] if hit else []
            fact("%s ControlTerminal #%d appears in Diagram #%d's AbstractDiagram.Nodes[]: %s; named SOURCE "
                 "terminals (out_name) %r" % (key, u, SIBLING_DIAG_UID, m["in_686_nodes"], m["out_named"]))
            ci, cierr = safe(cls_index, SCRATCH, "ControlTerminal", u)
            m["controlterminal_traverse_index"] = ci
            if ci is None:
                m["queue"] = {"accepted": None, "error": "not addressable as Traverse 'ControlTerminal': %s"
                                                         % cierr}
                fact("%s: %s" % (key, m["queue"]["error"]))
            else:
                names = [nm for _i, nm in m["out_named"]] or [m["label"] or ""]
                m["queue"] = q_attempt(key, SCRATCH, "ControlTerminal", ci, names[0], d686_now,
                                       "a front-panel control's terminal, %s, label %r"
                                       % (m["rec"]["type_intended"], m["label"]),
                                       extra={"control_terminal_uid": u, "out_name_used": names[0]})
            R["shape1"][key]["donor"] = {k: v for k, v in m.items() if k != "rec"}
        gate("R4d every created ControlTerminal was scored against queue_node('obtain')",
             all("queue" in m for m in made.values()) if made else False,
             "created %r" % sorted(made))

        # ================================================================= SHAPE 2
        print("\n--- SHAPE 2: a constant placed straight onto the Obtain Queue's own `%s` INPUT" % EDT_NAME,
              flush=True)
        d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
        bidx, bierr = safe(cls_index, SCRATCH, base["class_guess"], BASELINE_OPERAND[0]) if base_ok else (None, "")
        base_q = None
        if bidx is not None:
            base_q = q_attempt("BASE", SCRATCH, base["class_guess"], bidx, BASELINE_OPERAND[1], d686_now,
                               "round 1's ACCEPTED baseline donor #%d %r - the only way an Obtain Queue node "
                               "can be made to exist at all" % BASELINE_OPERAND)
        R["shape2"]["baseline_obtain"] = base_q
        q_uid = (base_q or {}).get("new_function_uids", [None])[0] if base_q else None
        gate("R5 the baseline Obtain Queue was created on Diagram #%d" % SIBLING_DIAG_UID, bool(q_uid),
             "new Function uids %r; error %r" % ((base_q or {}).get("new_function_uids"),
                                                 (base_q or {}).get("error")))

        edt = None
        if q_uid:
            d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
            _w, rows_now = walk_rows(SCRATCH, d686_now)
            qrow = [r for r in rows_now if r["uid"] == q_uid]
            if qrow:
                qr = qrow[0]
                t, terr = safe(terms_of, SCRATCH, d686_now, q_uid, fresh=True)
                R["shape2"]["obtain_node"] = {"uid": q_uid, "node_index": qr["node_index"],
                                              "class_guess": qr["class_guess"], "terms_error": terr,
                                              "terminals": {str(k): v for k, v in (t or {}).items()}}
                fact("the new Obtain Queue #%s is Diagram #%d Nodes[%d] (%s); its terminals %r"
                     % (q_uid, SIBLING_DIAG_UID, qr["node_index"], qr["class_guess"],
                        [(i, nm, src, wv) for i, (nm, src, wv) in sorted((t or {}).items())]))
                for i, (nm, src, wv) in sorted((t or {}).items()):
                    if nm == EDT_NAME and not src:
                        edt = {"term_index": i, "name": nm, "wire_before": wv,
                               "node_index": qr["node_index"]}
                fact("the `%s` INPUT terminal of #%s: %r" % (EDT_NAME, q_uid, edt))
        R["shape2"]["element_data_type_terminal"] = edt

        cot = []
        if edt:
            d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
            c0 = g.count(SCRATCH, "Constant")
            a = const_on_term(SCRATCH, "Diagram", d686_now, edt["node_index"], edt["term_index"],
                              cot_labels, value=0.0)
            a.update({"attempt": "(a) container class 'Diagram', the Traverse index of Diagram #%d"
                                 % SIBLING_DIAG_UID,
                      "constants_delta": g.count(SCRATCH, "Constant") - c0})
            cot.append(a)
            fact("SHAPE2 (a) Class Name='Diagram'[%d] Nodes[%d].Terminals[%d]: err %r | invoke err %r | created "
                 "uid %r | Constant count delta %d"
                 % (d686_now, edt["node_index"], edt["term_index"], a["err"], a["inv_err"], a["created_uid"],
                    a["constants_delta"]))

            if o686cls and o686_index is not None:
                c0 = g.count(SCRATCH, "Constant")
                b = const_on_term(SCRATCH, o686cls, o686_index, edt["node_index"], edt["term_index"],
                                  cot_labels, value=0.0)
                b.update({"attempt": "(b) container class %r (the MEASURED class of Diagram #%d's owner) [%s]"
                                     % (o686cls, SIBLING_DIAG_UID, o686_index),
                          "constants_delta": g.count(SCRATCH, "Constant") - c0})
                cot.append(b)
                fact("SHAPE2 (b) Class Name=%r[%s] Nodes[%d].Terminals[%d]: err %r | invoke err %r | created uid "
                     "%r | Constant count delta %d"
                     % (o686cls, o686_index, edt["node_index"], edt["term_index"], b["err"], b["inv_err"],
                        b["created_uid"], b["constants_delta"]))
        R["shape2"]["const_on_term_attempts"] = cot
        gate("R6a/b the two Diagram-#%d attempts were made and scored" % SIBLING_DIAG_UID, len(cot) >= 1,
             "%d attempts" % len(cot))

        # ---- (c) POSITIVE CONTROL: the same op on a real WhileLoop BODY node of this same scratch
        pc = {"attempt": "(c) POSITIVE CONTROL - WhileLoop #%d's body Diagram #%d, a node with a bare named input"
                         % (FRAME_LOOP_UID, FRAME_BODY_UID)}
        fb_i, fb_e = safe(diag_index, SCRATCH, FRAME_BODY_UID)
        wl_i, wl_e = safe(cls_index, SCRATCH, "WhileLoop", FRAME_LOOP_UID)
        pc.update({"body_diagram_index": fb_i, "whileloop_index": wl_i, "index_errors": [fb_e, wl_e]})
        if fb_i is not None and wl_i is not None:
            _wb, rowsb = walk_rows(SCRATCH, fb_i, limit=200)
            cand = [(r, r["in_bare"][0]) for r in rowsb if r["in_bare"]]
            pc["n_body_nodes"] = len(rowsb)
            if cand:
                r, (ti, tn) = cand[0]
                pc.update({"node_uid": r["uid"], "node_index": r["node_index"], "term": [ti, tn]})
                c0 = g.count(SCRATCH, "Constant")
                res = const_on_term(SCRATCH, "WhileLoop", wl_i, r["node_index"], ti, cot_labels, value=-1.0)
                res["constants_delta"] = g.count(SCRATCH, "Constant") - c0
                pc["result"] = res
                t_after, _te = safe(terms_of, SCRATCH, fb_i, r["uid"], fresh=True)
                pc["terminal_after"] = (t_after or {}).get(ti)
                fact("SHAPE2 (c) POSITIVE CONTROL on WhileLoop #%d[%s] body Nodes[%d] #%d Terminals[%d] %r: "
                     "err %r | invoke err %r | created uid %r | Constant delta %d | terminal after %r"
                     % (FRAME_LOOP_UID, wl_i, r["node_index"], r["uid"], ti, tn, res["err"], res["inv_err"],
                        res["created_uid"], res["constants_delta"], pc["terminal_after"]))
            else:
                pc["result"] = {"err": "no body node with a bare named input was found"}
                fact("SHAPE2 (c): %s" % pc["result"]["err"])
        R["shape2"]["positive_control"] = pc
        gate("R6c the positive control was made and scored", "result" in pc,
             repr(pc.get("result", {}).get("err")))

        # ---- did anything land on the Obtain Queue's element data type?
        placed = [a for a in cot if a.get("created_uid")]
        if placed and edt and q_uid:
            d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
            t_after, _e = safe(terms_of, SCRATCH, d686_now, q_uid, fresh=True)
            R["shape2"]["obtain_terminal_after"] = (t_after or {}).get(edt["term_index"])
            rc, rerr = safe(COT.read_const, SCRATCH, placed[0]["created_uid"])
            R["shape2"]["created_constant"] = {"read": rc, "error": rerr}
            fact("SHAPE2: a constant WAS placed (uid %r); the Obtain Queue's `%s` terminal now reads %r; the "
                 "constant reads back %r (err %r)"
                 % (placed[0]["created_uid"], EDT_NAME, R["shape2"]["obtain_terminal_after"], rc, rerr))
        else:
            fact("SHAPE2: NO constant was placed on the Obtain Queue's `%s` terminal by any attempt" % EDT_NAME)

        # ================================================================= SHAPE 3
        print("\n--- SHAPE 3: does each ACCEPTED donor's source depend on WhileLoop #%d?" % FRAME_LOOP_UID,
              flush=True)
        accepted = []
        if base_q and base_q.get("accepted"):
            accepted.append(("S-A #%d %r (round 1's ACCEPTED node donor)" % BASELINE_OPERAND, "node",
                             BASELINE_OPERAND[0]))
        for key in ("C1", "C2"):
            m = made.get(key)
            if m and m.get("queue", {}).get("accepted"):
                accepted.append(("%s ControlTerminal #%d %r" % (key, m["uid"], m["label"]), "control", m["uid"]))
        R["shape3"]["accepted_shapes"] = [a[0] for a in accepted]
        fact("ACCEPTED shapes to report a dependency for: %r" % R["shape3"]["accepted_shapes"])
        d686_now = diag_index(SCRATCH, SIBLING_DIAG_UID)
        for tag, kind, uid in accepted:
            if kind == "node":
                R["shape3"][tag] = dependency_of_node(SCRATCH, d686_now, uid, BASELINE_OPERAND[1])
            else:
                _w, rows_now = walk_rows(SCRATCH, d686_now)
                hit = [r for r in rows_now if r["uid"] == uid]
                rec = {"uid": uid, "kind": "ControlTerminal", "in_686_nodes": bool(hit),
                       "fed_inputs": (hit[0]["in_bare"] if hit else None),
                       "depends_on_frame_loop": False,
                       "note": "a front-panel control's terminal has no INPUT terminal - its value comes from the "
                               "panel, so it cannot depend on WhileLoop #%d by dataflow" % FRAME_LOOP_UID}
                R["shape3"][tag] = rec
                fact("DEPENDENCY %s: %r" % (tag, rec))
        R["shape3"]["S-B note"] = ("the #%d OUTER terminal shape (round 1's second ACCEPTED shape) depends on "
                                   "WhileLoop #%d TOTALLY by construction - it IS that loop's output boundary "
                                   "terminal, so its value exists only after the loop stops" % (FRAME_LOOP_UID,
                                                                                                FRAME_LOOP_UID))
        fact(R["shape3"]["S-B note"])
        gate("R7 a dependency reading is recorded for every ACCEPTED shape",
             all(t in R["shape3"] for t, _k, _u in accepted), "accepted %d" % len(accepted))

        # ================================================================= close the scratch out
        print("\n--- the scratch's census, ExecState and the save (allow_broken stays False; gui_save is never "
              "called)", flush=True)
        R["after_census"] = {c: g.count(SCRATCH, c) for c in
                             ("Diagram", "WhileLoop", "SubVI", "Function", "Constant", "ControlTerminal",
                              "Wire", "Comparison", "LoopTunnel", "IndexArray")}
        fact("class census of the scratch AFTER the attempts: %r" % R["after_census"])
        es, eerr = safe(g.exec_state, SCRATCH)
        fact("scratch ExecState with the ORIGINAL preloaded: %r (err %r)" % (es, eerr))
        size, serr = safe(g.save, SCRATCH)
        R["scratch"]["exec_state"] = es
        R["scratch"]["save"] = {"returned_bytes": size, "exception": serr}
        fact("g.save(scratch) returned %r; exception %r" % (size, serr))
        R["scratch"]["after_save"] = D.file_facts("the scratch after the save attempt", SCRATCH)
        gate("R8 the scratch's ExecState and save attempt are recorded", True,
             "ExecState %r, save %r, md5 %r" % (es, size, R["scratch"]["after_save"].get("md5")))
        _r, cperr = safe(g.close_panel, SCRATCH)
        if cperr:
            fact("close_panel raised %s" % cperr)
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception:                                                             # noqa: BLE001
        import traceback
        traceback.print_exc()
        rc = 1
    finally:
        try:
            g.reset()
        except Exception:                                                         # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                         # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                         # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("R9 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        try:
            oe = probe("R10 ORIGINAL after the run", ORIGINAL)
            s1e = probe("R10 D1_s1_copy.vi after the run", S1)
            s2e = probe("R10 D1_s2_loops.vi after the run", S2)
            ok10 = (oe.get("md5") == ORIG_MD5 and s1e.get("md5") == S1_MD5
                    and (s2e.get("exists") != "1" or s2e.get("md5") == S2_MD5))
            R["md5_after"] = {"original": oe.get("md5"), "s1": s1e.get("md5"), "s2": s2e.get("md5")}
            if not gate("R10 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are all unchanged", ok10,
                        "orig %s s1 %s s2 %s" % (oe.get("md5"), s1e.get("md5"), s2e.get("md5"))):
                rc = 1
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  R10 could not re-probe: %s: %s" % (type(e).__name__, e), flush=True)
            fails.append("R10 re-probe raised")
            rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== FACTS ONLY - no donor is picked and no queue stage is written (35(b) reserves both for the "
              "judgement session). NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
