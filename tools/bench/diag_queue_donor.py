r"""diag_queue_donor - Pre-decided 35(b): WHICH DONOR SHAPES CAN `queue_node('obtain')` ACCEPT as the
`element data type` source?

🔴 THIS IS A DIAGNOSTIC, NOT A STAGE AND NOT A RECIPE. It lives in `tools/bench/`, it produces READINGS
(`tools/bench/diag_queue_donor.json` + this log), and it must never be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND PICKS NOTHING. 35(b) reserves the choice of donor - and the writing of any queue stage -
for the judgement session. Nothing here is a recommendation.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is. No motor,
no ASI, no camera, no GUI action. The ORIGINAL is never opened or written (its md5 is probed at both ends);
`claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are NEVER opened or written by this file. Every edit
happens on a dated SCRATCH copy of `D1_s1_copy.vi`, exactly as cycle 50's diagnostic did
(`tools/bench/diag_s2_scaffold.py:88`), and that scratch's md5 is recorded.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53). Sub-step 1 below asks which BUILT ops can place a
diagram constant; if the answer were none, that would be the finding - not a reason to build one.

THE QUESTION. `gscript.queue_node` (`tools/gscript.py:1122-1149`) types the created `Obtain Queue` from a
`(node, NAMED output terminal)` pair: it sets `Class Name`/`index` to a TRAVERSE class and index, `Names` to ONE
exact terminal name, and the op's Get Outputs feeds `element data type` (`docs/NAMES.md:767-768`). Cycle 50
measured that a name read off a WIRE table is not automatically a `src_name`: `#637`'s outer feed carries
`out_name ''` (`docs/cycle27-plan.md:961-964`), and `tools/bench/diag_s2_scaffold.json` shows `#637 'frame index'`
failing the census's named-source test for that reason.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line: `grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `gscript.queue_node` `:1122` - the thing under test. `gscript.create_control` `:2360`, `gscript.count/uids/
    new_since/report_all/open_panel/close_panel/exec_state/save/node_labels` - built, unchanged.
  * `build_opsentinel_ops.create_node("const", ...)` `:387-405` - the BUILT caller of `OpCreateConst_v0.vi`
    (labels `tools/bench/opcreate_const_labels.json`), the only wrapper in the fleet that places a constant on a
    chosen diagram.
  * `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147` / `idx` `:158` - the BUILT diagram census.
  * `build_d1_v0.owner_of` `:338` / `diag_index` `:357` / `terms_of` `:375`.
  * `diag_s2_scaffold.fresh` `:155` / `file_facts` `:142` / `Preload` `:167` / `census_686` `:198`.
  * `hash_probe.probe` (34(k)); `bench_prep.labview_handles`.
Nothing new is built.

SUB-STEP 1 (zero LabVIEW): which BUILT ops can place a diagram constant AT ALL. Answered from the files, printed
as evidence, and gated - see `CONST_OPS` below.

SUB-STEP 2: for each donor shape reachable with BUILT ops only, on `Diagram #686` of the scratch:
  S-A  an EXISTING node's named output terminal - the known-good comparison, node #8486 `x+1` (Function,
       Nodes[0] of #686), the operand cycle 50's scaffold used on the first attempt.
  S-B  the FRAME LOOP's own outer named output terminal (`#637` `current image number`, `#686` terminal 36 -
       `docs/d1-build-plan.md:580`): does `queue_node` accept a `WhileLoop` as the source class at all? (Its
       USE is separately forbidden by 35(a) - R1 - and this measures only mechanical acceptance.)
  S-C  a DIAGRAM CONSTANT placed by `OpCreateConst_v0`: what class it is, whether it appears in
       `AbstractDiagram.Nodes[]` at all (MEASURED elsewhere as NO - `Constant` and `Node` are siblings under
       `GObject`, `tools/bench/peer_s2boundary.log:37`), whether any named output terminal is readable, and what
       `queue_node` does with it.
  S-D  a FRONT-PANEL CONTROL's terminal created by `create_control` on an UNWIRED NAMED INPUT of a `#686` node:
       a `ControlTerminal` whose output carries the control's LABEL as a name. ⚠️ This shape CHANGES the
       computation of the copy it is created on (an unwired input becomes driven), which is why it is measured
       on a throwaway scratch and never on an artefact.
Every attempt records the op's VERBATIM error, the new `Function` uids, and whether an `Obtain Queue` node
actually appeared.

SUB-STEP 3: `docs/d1-build-plan.md` §9 (`:576-585`)'s eight-queue table, read here and printed with, per queue,
which of the MEASURED shapes is type-available on `Diagram #686` before the loops start.

PREDICTION CONTRACT (each line is a printed GATE; only the file gates are FATAL - this is a measurement and
every later reading is wanted even when an earlier one fails)
  Q0  the ORIGINAL and `claudeDev\D1_s1_copy.vi` exist; ORIGINAL md5 2a78e17c449cacdaf5da389818526859.  FATAL
  Q1  the scratch copy is byte-identical to `D1_s1_copy.vi` (md5 3e3d23cefd3a334001aa9d6156bf1aee).     FATAL
  Q2  SUB-STEP 1: at least one BUILT op can place a diagram constant (both `OpCreateConst_v0.vi` and
      `OpCreateConstOnTerm_v0.vi` are on disk under `claudeDev`). If this FAILS, sub-step 2 is SKIPPED.
  Q3  `Diagram #686`'s census still offers node #8486 `x+1` as a named scalar source terminal (34(h)).
  Q4  S-A is ACCEPTED by `queue_node('obtain')` - the baseline. If this fails, no later rejection means
      anything, and the log says so.
  Q5a/b/c/d  each shape's outcome is RECORDED with its verbatim op error (a rejection is a legitimate
      outcome of this test; these gates assert only that the attempt was MADE and scored).
  Q6  the scratch's `ExecState` and the save attempt are recorded (either value is legitimate).
  Q7  no live VI Server reference is left open.
  Q8  the ORIGINAL's md5 is unchanged; `D1_s1_copy.vi` and `D1_s2_loops.vi` are unchanged.              FATAL
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
from build_d1_v0 import owner_of, diag_index, terms_of                            # noqa: E402
from build_opsentinel_ops import create_node as CREATE_NODE                       # noqa: E402
from build_opstopfromnode_v0 import walk as WALK, cls_of, idx as cls_index        # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1 = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2 = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_qdonor_%s.vi" % STAMP)     # unique per run (CLAUDE.md scratch rule)
OUT = os.path.join(HERE, "diag_queue_donor.json")

SIBLING_DIAG_UID = D.SIBLING_DIAG_UID            # 686
BASELINE_OPERAND = (8486, "x+1")                 # 34(l)'s measured winner, by NAME
FRAME_LOOP_UID = 637
FRAME_LOOP_TERM = "current image number"         # docs/d1-build-plan.md:580, `#686` terminal 36
Q_AT = {"S-A": (2600, 5200), "S-B": (2900, 5200), "S-C": (3200, 5200), "S-D": (3500, 5200)}
CONST_AT = (2600, 5600)

# ---- SUB-STEP 1, answered from the files (zero LabVIEW). Each row: op file, its BUILT caller, what it places,
# and the file:line that MEASURED it. Existence on disk is checked at run time.
CONST_OPS = [
    {"op": "OpCreateConst_v0.vi",
     "caller": "build_opsentinel_ops.create_node('const', ...)  tools/recipes/build_opsentinel_ops.py:387-405",
     "labels": "tools/bench/opcreate_const_labels.json",
     "places": "ONE constant on a CHOSEN diagram ('Class Name 2'='Diagram'/'index 2'), UNWIRED; 'Type' and "
               "'Value' are VARIANTs and the created object's Terminal is NOT returned to the caller",
     "evidence": "docs/toolkit-capabilities.md:65 - FUNCTIONAL 23/0, new Constant #354, owner chain "
                 "#354 -> Diagram#110 -> WhileLoop#43; the VARIANT route produced an EMPTY value"},
    {"op": "OpCreateConstOnTerm_v0.vi",
     "caller": "no gscript wrapper; recipe tools/recipes/build_opcreateconstonterm_v0.py",
     "labels": "(the recipe's own)",
     "places": "ONE constant ON A TERMINAL of a WhileLoop BODY node ('Class Name'='WhileLoop'/'index', "
               "'index 3'=body Nodes[] index, 'index 4'=Terminals[] index) - typed by the sink and ALREADY "
               "WIRED, so it cannot place a free constant on an arbitrary diagram",
     "evidence": "docs/toolkit-capabilities.md:66 - FUNCTIONAL 22/0, DigitalNumericConstant #159, value read "
                 "back -1 through OpConstValueN_v1, scratch ExecState 1"},
]

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "no_vi_was_run": True,
     "question": "Pre-decided 35(b): which donor shapes does queue_node('obtain') accept as element data type?",
     "picks_nothing": True, "files": {}, "const_ops": CONST_OPS, "census": {}, "shapes": {}, "handles": {},
     "hash_probe": [], "queue_table_s9": {}}


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


def labels_of(target, diagram_index):
    try:
        return {r["uid"]: r["label"] for r in g.node_labels(target, diagram_index)}
    except Exception as e:                                                        # noqa: BLE001
        fact("node_labels raised %s: %s" % (type(e).__name__, e))
        return {}


def attempt(shape, target, src_cls, src_index, src_name, d686, why, extra=None):
    """ONE `queue_node('obtain')` attempt. Records the verbatim op error, the new Function uids and the labels
    LabVIEW gave them, so 'accepted' means an Obtain Queue node EXISTS, never that a call returned."""
    rec = {"shape": shape, "src_cls": src_cls, "src_index": src_index, "src_name": src_name, "why": why,
           "accepted": False, "error": None, "new_function_uids": [], "new_labels": {}}
    if extra:
        rec.update(extra)
    before = set(g.uids(target, "Function"))
    try:
        new = g.queue_node("obtain", target, src_cls, int(src_index), src_name, d686, Q_AT[shape])
        rec["returned"] = new
    except Exception as e:                                                        # noqa: BLE001
        rec["error"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    after = set(g.uids(target, "Function"))
    rec["new_function_uids"] = sorted(after - before)
    if rec["new_function_uids"]:
        lab = labels_of(target, diag_index(target, SIBLING_DIAG_UID))
        rec["new_labels"] = {str(u): lab.get(u) for u in rec["new_function_uids"]}
    rec["accepted"] = bool(rec["new_function_uids"]) and not rec["error"]
    R["shapes"][shape] = rec
    fact("SHAPE %s (%s[%s] . %r - %s): accepted=%s; new Function uids %r %r; op error %r"
         % (shape, src_cls, src_index, src_name, why, rec["accepted"], rec["new_function_uids"],
            rec["new_labels"], rec["error"]))
    return rec


def main():
    print("=== diag_queue_donor  %s   (Pre-decided 35(b) MEASUREMENT; NO VI IS RUN, 34(f); PICKS NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])

    # ---------------------------------------------------------------- SUB-STEP 1: zero LabVIEW
    print("\n--- SUB-STEP 1: which BUILT ops can place a diagram constant at all (read from the files)",
          flush=True)
    for row in CONST_OPS:
        row["on_disk"] = os.path.exists(os.path.join(g.CLAUDEDEV, row["op"]))
        row["size"] = os.path.getsize(os.path.join(g.CLAUDEDEV, row["op"])) if row["on_disk"] else None
        fact("CONST-OP %s  on_disk=%s size=%s\n           caller   : %s\n           places   : %s\n"
             "           evidence : %s" % (row["op"], row["on_disk"], row["size"], row["caller"],
                                           row["places"], row["evidence"]))
    fact("gscript itself has NO constant wrapper: `grep -ni constant tools/gscript.py` returns only comments "
         "(:1312, :1329, :1410) - the only BUILT caller of a constant creator is "
         "build_opsentinel_ops.create_node('const', ...)")
    fact("MEASURED ELSEWHERE, and it is the reason this question exists: `AbstractDiagram.Nodes[]` EXCLUDES "
         "constants - `Constant` and `Node` are SIBLINGS under `GObject` "
         "(tools/bench/peer_s2boundary.log:37; archive/2026-09-18-status-cycle19-flatseq.md:87)")
    placeable = [r["op"] for r in CONST_OPS if r["on_disk"]]
    gate("Q2 at least one BUILT op can place a diagram constant", bool(placeable), "on disk: %r" % placeable)

    # ---------------------------------------------------------------- files
    print("\n--- the files (read-only probes, 34(k))", flush=True)
    o = probe("ORIGINAL", ORIGINAL)
    s1 = probe("S1 claudeDev\\D1_s1_copy.vi", S1)
    s2 = probe("S2 claudeDev\\D1_s2_loops.vi (never opened by this file)", S2)
    R["files"] = {"original": o, "s1": s1, "s2": s2}
    gate("Q0 the ORIGINAL and the S1 artefact exist and the ORIGINAL's md5 equals the pin",
         o.get("md5") == ORIG_MD5 and s1.get("exists") == "1",
         "orig md5 %s; s1 exists %s" % (o.get("md5"), s1.get("exists")), fatal=True)

    if not placeable:
        fact("SUB-STEP 2 IS SKIPPED: no BUILT op can place a diagram constant, which is itself the finding "
             "(and no op is built to fix it - Pre-decided 2)")
        return

    D.fresh("F1")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S1, SCRATCH)
    sc = probe("the scratch copy", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "after_copy": sc}
    gate("Q1 the scratch copy is byte-identical to D1_s1_copy.vi", sc.get("md5") == S1_MD5,
         sc.get("md5", "?"), fatal=True)

    with D.Preload("P"):
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        R["before_census"] = {c: g.count(SCRATCH, c) for c in
                              ("Diagram", "WhileLoop", "SubVI", "Function", "Constant", "ControlTerminal",
                               "Wire", "Comparison", "LoopTunnel")}
        fact("class census of the scratch BEFORE any edit: %r" % R["before_census"])

        # ------------------------------------------------------------ the census of Diagram #686
        print("\n--- the census of Diagram #%d (34(h): re-read, never cached across a mutation)"
              % SIBLING_DIAG_UID, flush=True)
        d686, w686, rows = D.census_686(SCRATCH)
        by_uid = {r["uid"]: r for r in rows}
        base = by_uid.get(BASELINE_OPERAND[0])
        base_ok = bool(base) and any(nm == BASELINE_OPERAND[1] for _i, nm in base["named_source_terms"])
        gate("Q3 node #%d still offers the named source terminal %r on Diagram #%d"
             % (BASELINE_OPERAND[0], BASELINE_OPERAND[1], SIBLING_DIAG_UID), base_ok,
             "named source terminals %r" % (base["named_source_terms"][:8] if base else None))

        # ------------------------------------------------------------ S-A: the known-good named scalar
        print("\n--- SHAPE S-A: an EXISTING node's named output terminal (#%d %r) - the baseline"
              % BASELINE_OPERAND, flush=True)
        if base_ok:
            attempt("S-A", SCRATCH, base["class_guess"], cls_index(SCRATCH, base["class_guess"],
                                                                   BASELINE_OPERAND[0]),
                    BASELINE_OPERAND[1], d686,
                    "node #%d Nodes[%d], the operand cycle 50's scaffold accepted on the first attempt"
                    % (BASELINE_OPERAND[0], base["node_index"]))
        else:
            R["shapes"]["S-A"] = {"shape": "S-A", "accepted": None, "error": "the baseline operand is not on "
                                                                             "the census - attempt NOT made"}
            fact("SHAPE S-A: NOT ATTEMPTED - the baseline operand is not on the census")
        gate("Q4 the BASELINE shape S-A is accepted (if it is not, no later rejection means anything)",
             bool(R["shapes"].get("S-A", {}).get("accepted")),
             repr(R["shapes"].get("S-A", {}).get("error")))
        gate("Q5a shape S-A was attempted and scored", "S-A" in R["shapes"])

        # ------------------------------------------------------------ S-B: the frame loop's outer terminal
        print("\n--- SHAPE S-B: the FRAME LOOP #%d's own outer named output terminal %r (mechanical "
              "acceptance only - 35(a) forbids its USE)" % (FRAME_LOOP_UID, FRAME_LOOP_TERM), flush=True)
        fl = by_uid.get(FRAME_LOOP_UID)
        fl_names = [nm for _i, nm in (fl or {}).get("named_source_terms", [])]
        fact("node #%d appears on the census as class_guess %r with %d named source terminals; %r is %s"
             % (FRAME_LOOP_UID, (fl or {}).get("class_guess"), len(fl_names), FRAME_LOOP_TERM,
                "PRESENT" if FRAME_LOOP_TERM in fl_names else "ABSENT"))
        try:
            fl_index = [o_["uid"] for o_ in g.report_all(SCRATCH, "WhileLoop")].index(FRAME_LOOP_UID)
        except ValueError:
            fl_index = None
        if fl_index is not None and FRAME_LOOP_TERM in fl_names:
            attempt("S-B", SCRATCH, "WhileLoop", fl_index, FRAME_LOOP_TERM, d686,
                    "the frame loop's outer boundary terminal 36 (docs/d1-build-plan.md:580), the shape the "
                    "five 'A' rows of the §9 table name")
        else:
            R["shapes"]["S-B"] = {"shape": "S-B", "accepted": None,
                                  "error": "not attempted: WhileLoop index %r, name present %s"
                                           % (fl_index, FRAME_LOOP_TERM in fl_names)}
            fact("SHAPE S-B: NOT ATTEMPTED (%s)" % R["shapes"]["S-B"]["error"])
        gate("Q5b shape S-B was attempted and scored", "S-B" in R["shapes"])

        # ------------------------------------------------------------ S-C: a diagram CONSTANT
        print("\n--- SHAPE S-C: a diagram CONSTANT placed by OpCreateConst_v0 on Diagram #%d"
              % SIBLING_DIAG_UID, flush=True)
        with open(os.path.join(HERE, "opcreate_const_labels.json"), encoding="utf-8") as f:
            const_labels = json.load(f)
        cb = const_labels.get("ctl_by_term", {}) or {}
        vals = {}
        if cb.get("Type"):
            vals[cb["Type"]] = 0.0            # a DBL variant -> a DBL constant (build_opsentinel_ops.py:477-480)
        if cb.get("Value"):
            vals[cb["Value"]] = 0.0
        c0 = g.uids(SCRATCH, "Constant")
        n0 = g.uids(SCRATCH, "Node")
        cerr = None
        try:
            cerr = CREATE_NODE("const", const_labels, SCRATCH, diag_index(SCRATCH, SIBLING_DIAG_UID),
                               CONST_AT, values=vals)
        except Exception as e:                                                    # noqa: BLE001
            cerr = "%s: %s" % (type(e).__name__, str(e)[:300])
        newc = g.new_since(SCRATCH, "Constant", c0)
        newn = g.new_since(SCRATCH, "Node", n0)
        const_rec = {"op_error": cerr, "variant_inputs": vals, "new_constants": newc, "new_nodes": newn}
        fact("OpCreateConst_v0 on Diagram #%d: op error %r; new Constant objects %r; new Node objects %r "
             "(a constant is NOT a Node - siblings under GObject)"
             % (SIBLING_DIAG_UID, cerr, [(o_["uid"], o_.get("class")) for o_ in newc],
                [(o_["uid"], o_.get("class")) for o_ in newn]))
        if newc:
            cu = newc[0]["uid"]
            ow = None
            try:
                ow = owner_of(SCRATCH, cu, strict=False)
            except Exception as e:                                                # noqa: BLE001
                ow = ("ERROR", "%s: %s" % (type(e).__name__, e))
            w_now = WALK(SCRATCH, diag_index(SCRATCH, SIBLING_DIAG_UID), limit=200)
            in_nodes = cu in w_now
            names = []
            if in_nodes:
                names = [(r["i"], r["name"]) for r in w_now[cu][2] if r["is_source"]]
            const_rec.update({"uid": cu, "class": newc[0].get("class"), "owner": ow,
                              "appears_in_diagram_Nodes": in_nodes, "source_terminal_names": names})
            fact("the new constant #%d (class %r) owner %r; appears in AbstractDiagram.Nodes[] of #%d: %s; "
                 "readable named SOURCE terminals: %r"
                 % (cu, newc[0].get("class"), ow, SIBLING_DIAG_UID, in_nodes, names))
            tried = []
            for cls_name in [c for c in (newc[0].get("class"), "Constant", "DigitalNumericConstant") if c]:
                if cls_name in tried:
                    continue
                tried.append(cls_name)
                try:
                    ci = cls_index(SCRATCH, cls_name, cu)
                except Exception as e:                                            # noqa: BLE001
                    fact("the constant is not addressable as Traverse %r[...]: %s: %s"
                         % (cls_name, type(e).__name__, e))
                    continue
                nm_candidates = [nm for _i, nm in names] or [""]
                for nm in nm_candidates[:2]:
                    key = "S-C" if "S-C" not in R["shapes"] else "S-C(%s,%r)" % (cls_name, nm)
                    Q_AT.setdefault(key, (3200 + 120 * len(R["shapes"]), 5200))
                    attempt(key, SCRATCH, cls_name, ci, nm, d686,
                            "a diagram constant placed by OpCreateConst_v0, addressed as Traverse %r, "
                            "src_name %r" % (cls_name, nm),
                            extra={"constant_uid": cu, "constant_class": newc[0].get("class")})
                break
        else:
            R["shapes"]["S-C"] = {"shape": "S-C", "accepted": None,
                                  "error": "no Constant object was created; op error %r" % cerr}
            fact("SHAPE S-C: NOT ATTEMPTED - OpCreateConst_v0 created no Constant object")
        R["const_creation"] = const_rec
        gate("Q5c shape S-C was attempted and scored", any(k.startswith("S-C") for k in R["shapes"]))

        # ------------------------------------------------------------ S-D: a control terminal
        print("\n--- SHAPE S-D: a ControlTerminal created by create_control on an UNWIRED NAMED INPUT of a "
              "Diagram #%d node (this CHANGES the scratch's computation - scratch only)" % SIBLING_DIAG_UID,
              flush=True)
        target_row = None
        for r in sorted(rows, key=lambda r: r["node_index"]):
            if r["class_guess"] not in ("SubVI", "Function", "IndexArray", "Invoke", "Property"):
                continue
            rec_w = w686.get(r["uid"])
            if not rec_w:
                continue
            bare = [(x["i"], x["name"]) for x in rec_w[2]
                    if (not x["is_source"]) and x["wire"] == 0 and (x["name"] or "").strip()]
            if bare:
                target_row = (r, bare[0])
                break
        if target_row:
            r, (ti, tn) = target_row
            fact("create_control source: node #%d Nodes[%d] (%s) unwired named INPUT terminal %d %r"
                 % (r["uid"], r["node_index"], r["class_guess"], ti, tn))
            made, label = None, None
            try:
                made, label = g.create_control(SCRATCH, r["node_index"], ti)
            except Exception as e:                                                # noqa: BLE001
                fact("create_control raised %s: %s" % (type(e).__name__, str(e)[:200]))
            R["control_creation"] = {"source_node": r["uid"], "terminal": [ti, tn],
                                     "new_control_terminals": made, "label": label}
            fact("create_control -> new ControlTerminal(s) %r, label %r" % (made, label))
            if made:
                cu = made[0]["uid"]
                try:
                    ci = cls_index(SCRATCH, "ControlTerminal", cu)
                    attempt("S-D", SCRATCH, "ControlTerminal", ci, label or "", d686,
                            "a front-panel control's terminal, named by its LABEL %r" % (label,),
                            extra={"control_terminal_uid": cu})
                except Exception as e:                                            # noqa: BLE001
                    R["shapes"]["S-D"] = {"shape": "S-D", "accepted": None,
                                          "error": "not addressable: %s: %s" % (type(e).__name__, e)}
                    fact("SHAPE S-D: %s" % R["shapes"]["S-D"]["error"])
            else:
                R["shapes"]["S-D"] = {"shape": "S-D", "accepted": None,
                                      "error": "create_control produced no ControlTerminal"}
        else:
            R["shapes"]["S-D"] = {"shape": "S-D", "accepted": None,
                                  "error": "no unwired named INPUT terminal on any addressable node of "
                                           "Diagram #%d - attempt NOT made" % SIBLING_DIAG_UID}
            fact("SHAPE S-D: NOT ATTEMPTED (%s)" % R["shapes"]["S-D"]["error"])
        gate("Q5d shape S-D was attempted and scored", "S-D" in R["shapes"])

        # ------------------------------------------------------------ the scratch's state, and the save
        print("\n--- the scratch's ExecState and the save attempt (both values legitimate; allow_broken stays "
              "False, gui_save is never called)", flush=True)
        R["after_census"] = {c: g.count(SCRATCH, c) for c in
                             ("Diagram", "WhileLoop", "SubVI", "Function", "Constant", "ControlTerminal",
                              "Wire", "Comparison", "LoopTunnel")}
        fact("class census of the scratch AFTER the attempts: %r" % R["after_census"])
        es, serr, size = None, None, None
        try:
            es = g.exec_state(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            serr = "exec_state raised %s: %s" % (type(e).__name__, e)
        fact("scratch ExecState with the ORIGINAL preloaded: %r %s" % (es, serr or ""))
        try:
            size = g.save(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:200])
        R["scratch"]["exec_state"] = es
        R["scratch"]["save"] = {"returned_bytes": size, "exception": serr}
        fact("g.save(scratch) returned %r; exception %r" % (size, serr))
        R["scratch"]["after_save"] = D.file_facts("the scratch after the save attempt", SCRATCH)
        gate("Q6 the scratch's ExecState and save attempt are recorded", True,
             "ExecState %r, save %r" % (es, size))
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    dump()

    # ---------------------------------------------------------------- SUB-STEP 3: the §9 table
    print("\n--- SUB-STEP 3: `docs/d1-build-plan.md` §9 (:576-585), read here, against the MEASURED shapes",
          flush=True)
    accepted = {k: v.get("accepted") for k, v in R["shapes"].items()}
    plan = os.path.join(ROOT, "docs", "d1-build-plan.md")
    rowsrc = []
    with open(plan, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            if re.match(r"^\|\s*`?Q_", line):
                rowsrc.append((i, line.rstrip()))
    for i, line in rowsrc:
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        q = cells[0].strip("` ")
        state = cells[5] if len(cells) > 5 else "?"
        R["queue_table_s9"][q] = {"line": i, "element_type": cells[1] if len(cells) > 1 else "",
                                  "src_uid": cells[2] if len(cells) > 2 else "",
                                  "terminal": cells[3] if len(cells) > 3 else "",
                                  "diagram": cells[4] if len(cells) > 4 else "", "state": state}
        print(("      §9 %-12s type %-28s src %-8s term %-28s state %s"
               % (q, (cells[1] if len(cells) > 1 else "")[:28], (cells[2] if len(cells) > 2 else "")[:8],
                  (cells[3] if len(cells) > 3 else "")[:28], state[:60])).encode("ascii", "replace")
              .decode("ascii"), flush=True)
    fact("§9 rows read from %s: %d (lines %r)" % (plan, len(rowsrc), [i for i, _ in rowsrc]))
    fact("MEASURED shape acceptance, for the judgement session to apply to those rows: %r" % accepted)
    fact("Per §9, the rows whose designated donor is a `#637` OUTER terminal (shape S-B) are Q_meta, Q_res, "
         "Q_good, Q_rmeta, Q_focusback (state A); Q_free and Q_work are state B (no source on #686 until the "
         "IMAQ Create stage); Q_focus is state C (no scalar slice index on #686 at all). 35(a) forbids USING "
         "an S-B pair; this diagnostic reports only whether the op ACCEPTS each shape.")
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
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
        gate("Q7 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        try:
            oe = probe("Q8 ORIGINAL after the run", ORIGINAL)
            s1e = probe("Q8 D1_s1_copy.vi after the run", S1)
            s2e = probe("Q8 D1_s2_loops.vi after the run", S2)
            ok8 = (oe.get("md5") == ORIG_MD5 and s1e.get("md5") == S1_MD5
                   and (s2e.get("exists") != "1" or s2e.get("md5") == S2_MD5))
            R["md5_after"] = {"original": oe.get("md5"), "s1": s1e.get("md5"), "s2": s2e.get("md5")}
            if not gate("Q8 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are all unchanged", ok8,
                        "orig %s s1 %s s2 %s" % (oe.get("md5"), s1e.get("md5"), s2e.get("md5"))):
                rc = 1
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  Q8 could not re-probe: %s: %s" % (type(e).__name__, e), flush=True)
            fails.append("Q8 re-probe raised")
            rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== FACTS ONLY - no donor is picked and no queue stage is written (35(b) reserves both for the "
              "judgement session). NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.",
              flush=True)
        sys.exit(rc)
