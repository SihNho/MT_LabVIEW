"""diag_s2_scaffold — THE DISCRIMINATING TEST of `docs/cycle27-plan.md` Pre-decided 34(j).

🔴 THIS IS A DIAGNOSTIC, NOT A STAGE AND NOT A RECIPE. It lives in `tools/bench/`, it produces READINGS
(`tools/bench/diag_s2_scaffold.json` + this log), and it must never be moved under `tools/recipes/`.
🔴 NOTHING HERE RUNS A VI (Pre-decided 34(f)): no Run, no `VI.Run` method, no front panel driven, no motor, no
ASI, no camera, no GUI action. The only VIs that execute are the BUILT op VIs (that is what scripting is).

WHAT ALREADY EXISTS AND IS REUSED (CLAUDE.md "check what exists before creating anything"):
  * `gscript.loop_in("while", ...)` `tools/gscript.py:1155` — the BUILT While-loop creator (there is no other
    `loop_in`; `gscript.while_loop` `:1191` is its tunnel-taking sibling and is not needed here).
  * `build_opsentinel_ops.create_node("equal", ...)` `tools/recipes/build_opsentinel_ops.py:387-405` — the BUILT
    caller of `OpCreateEqual_v0.vi` (labels `tools/bench/opcreate_equal_labels.json`).
  * `build_opstopfromnode_v0.loop_end_ref / walk / cls_of / idx` `:340`, `:129`, `:147`, `:158` — the BUILT
    conditional-terminal READER and diagram census (labels `tools/bench/opstopfromnode_labels.json`).
  * `build_d1_v0.move_in / diag_index / wmap / terms_of / owner_of` `:318`, `:357`, `:364`, `:375`, `:338`.
  * `stage_d1_s1.py`'s `Preload` / `fresh` / `file_facts` / `version_bytes` shapes (Pre-decided 14a/16/29(d)).
  * `diag_d1_execstate_preload.run_condition` `tools/bench/diag_d1_execstate_preload.py:192` — the BUILT
    child-process-per-condition ExecState reader, used here on SAVED files only (see the note at step 5).
Nothing new is built. No op is created (Pre-decided 2; user 2026-09-18 08:53).

PREDICTION CONTRACT (each line is a printed GATE; the first FATAL failure stops the chain and still dumps JSON)
  G1  the ORIGINAL exists and its md5 is 2a78e17c449cacdaf5da389818526859.                            FATAL
  G2  `claudeDev\\D1_s1_copy.vi` md5 is 3e3d23cefd3a334001aa9d6156bf1aee, 474202 B, BEFORE the copy.    FATAL
  G3  the scratch copy is byte-identical to it.                                                        FATAL
  G4  `Diagram #686` census yields >= 1 node with a named SOURCE terminal whose name is not
      array/cluster/error/path/refnum/image/string-shaped (Pre-decided 34(c): the operand must be SCALAR). FATAL
  G5  exactly one new WhileLoop and one new Diagram appear on `Diagram #686`.                          FATAL
  G6  some candidate produces exactly one new `Comparison` node with no op error.                      FATAL
  G7  after `OpStopFromNode_v0` the loop's conditional terminal is the SAME uid and carries a NON-ZERO
      wire, and that wire uid is one the driving Comparison sources (wire identity, not "wired").      FATAL
  G8  reading 1 — `exec_state(scratch)` with the ORIGINAL preloaded — is RECORDED (1 or 0, both legal
      outcomes of the test; this gate only asserts the reading was taken).                         non-fatal
  G9  save attempt 1 recorded: `g.save()` default `allow_broken=False`, never `gui_save`.          non-fatal
  G10 `move_in #48` lands in the new body (owner Diagram = new body, owner(owner) = the new loop).  non-fatal
  G11 reading 2 — `exec_state(scratch)` under the same preload — is RECORDED.                      non-fatal
  G12 save attempt 2 recorded under the same rules.                                                non-fatal
  G13 every reference this script opened is closed (`gscript.ref_counts()` live == 0).              non-fatal
  G14 the ORIGINAL's md5 is unchanged at the end.                                                       FATAL

CANDIDATE ORDER IS PRE-DECIDED BY THE BRIEF, not chosen here: (1) node #637 terminal `frame index` (I32,
`docs/NAMES.md:111-112`; outer wire 2187, `tools/bench/d1_rewire_sources.json:2309-2374`) if the census shows it
as a NAMED SOURCE terminal, then (2) the remaining candidates in the order the census itself yields, scalar-shaped
names only. Every attempt is logged with its verbatim error.

NOTE ON "IN ITS OWN CHILD PROCESS" (brief steps 5 and 7). `diag_d1_execstate_preload.child()` RESTARTS LabVIEW
before it reads (`:124-128`), so it can only ever read a file ON DISK — an unsaved in-memory edit does not
survive it. Readings 1 and 2 are therefore taken the way the DELIVERED S1 stage took its C8 reading
(`tools/recipes/stage_d1_s1.py:173`, Pre-decided 14a/16/29): `g.exec_state(scratch)` inside a `Preload` block
holding the ORIGINAL resident READ-ONLY in the same instance — the only route by which `gscript.save()` can reach
`SaveInstrument` at all (`tools/gscript.py:2065-2071`). The child-process form IS used, at the very end, on
whatever was actually SAVED (cold and preloaded), where it is meaningful.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

for _s in (sys.stdout, sys.stderr):          # the console is cp949 here; an em dash must never kill a run
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, os.path.join(ROOT, "tools", "recipes"))
import gscript as g                                                              # noqa: E402
from bench_prep import labview_handles                                           # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, wmap, terms_of            # noqa: E402
from build_opsentinel_ops import create_node as CREATE_NODE                      # noqa: E402
from build_opstopfromnode_v0 import loop_end_ref as LOOP_END_REF, walk as WALK   # noqa: E402
from build_opstopfromnode_v0 import cls_of, idx as cls_index                     # noqa: E402
import diag_d1_execstate_preload as D1ES                                         # noqa: E402

ORIGINAL = os.path.join(os.path.dirname(ROOT), "Min_Track N beads V6_ParallelLoop.vi")
ORIG_MD5 = "2a78e17c449cacdaf5da389818526859"          # stage_d1_s2.py:400
CLAUDEDEV = g.CLAUDEDEV
S1_ARTEFACT = os.path.join(CLAUDEDEV, "D1_s1_copy.vi")
S1_MD5 = "3e3d23cefd3a334001aa9d6156bf1aee"            # STATUS owner_c48s1cd
S1_SIZE = 474202
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(CLAUDEDEV, "DIAG_s2scaffold_%s.vi" % STAMP)   # unique per run (CLAUDE.md scratch rule)
OUT = os.path.join(HERE, "diag_s2_scaffold.json")

SIBLING_DIAG_UID = 686        # the FlatSequenceFrame diagram that HOLDS WhileLoop #637 (stage_d1_s2.py:414)
FRAME_LOOP_UID = 637
MOVE_UID = 48                 # ASI_adjust focus-subvi.vi — 34(e)'s smallest-first node (7 cut rows)
LOOP_AT = (2600, 2600)        # LOOP_LOCATIONS["1.2"], stage_d1_s2.py:432
EQ_AT = (120, 120)
NON_SCALAR_NAME_RE = (r"(?i)array|\[\s*\]|cluster|error|refnum|\bpath\b|image|string|list|buffer|table|"
                      r"\bLUT\b|profile|trace|matrix")          # stage_d1_s2.py:457-458, verbatim
PREFERRED = (FRAME_LOOP_UID, "frame index")                     # the brief's pre-selected first candidate
MAX_ATTEMPTS = 6
ADDRESSABLE = ("SubVI", "Function", "IndexArray", "Invoke", "Property")

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "no_vi_was_run": True,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5}, "scratch": {"path": SCRATCH},
     "census": {}, "attempts": [], "readings": {}, "saves": {}, "handles": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
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


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def version_bytes(path):
    with open(path, "rb") as f:
        head = f.read(64)
    return [{"offset": m.start(), "bytes": " ".join("%02x" % b for b in m.group(0))}
            for m in re.finditer(rb"(?s).\x00\x80\x00", head)]


def file_facts(tag, path):
    rec = {"path": path, "exists": os.path.exists(path)}
    if rec["exists"]:
        rec["md5"] = md5(path)
        rec["size"] = os.path.getsize(path)
        rec["version_candidates"] = version_bytes(path)
        fact("%s: %s md5 %s size %d B; version bytes %s"
             % (tag, os.path.basename(path), rec["md5"], rec["size"], rec["version_candidates"]))
    else:
        fact("%s: %s IS NOT ON DISK" % (tag, os.path.basename(path)))
    return rec


def fresh(tag):
    """A FRESH LabVIEW instance (standing restart authority) — stage_d1_s2.py:575-586."""
    g.reset()
    try:
        rc = subprocess.run([sys.executable, "-u", os.path.join(ROOT, "tools", "lv_restart.py")],
                            capture_output=True, text=True, timeout=600)
        fact("%s: lv_restart rc=%d %r" % (tag, rc.returncode, (rc.stdout or "").strip().splitlines()[-1:]))
    except Exception as e:                                                        # noqa: BLE001
        fact("%s: lv_restart FAILED (%s: %s)" % (tag, type(e).__name__, e))
    g.reset()


class Preload:
    """stage_d1_s2.py:589-613 verbatim: the ORIGINAL resident READ-ONLY for the duration of a phase. No panel on
    the original, nothing run, nothing saved."""

    def __init__(self, tag):
        self.tag, self.app, self.vi = tag, None, None

    def __enter__(self):
        import pythoncom
        from win32com.client import dynamic
        pythoncom.CoInitialize()
        self.app = dynamic.Dispatch("LabVIEW.Application")
        self.vi = self.app.GetVIReference(ORIGINAL, "", False, 0)
        fact("%s: ORIGINAL resident READ-ONLY (LabVIEW %s), its own ExecState %d; nothing opened, nothing saved"
             % (self.tag, self.app.Version, int(self.vi.ExecState)))
        return self

    def __exit__(self, *exc):
        self.vi = None
        self.app = None
        fact("%s: preload references released; refs %r" % (self.tag, g.ref_counts()))
        return False


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def census_686(target):
    """Every node of Diagram #686 with its OUTPUT terminal names — `walk` is the BUILT census."""
    d686 = diag_index(target, SIBLING_DIAG_UID)
    fact("Diagram #%d reads Traverse index %d — re-read here, never cached across a mutation (34(h))"
         % (SIBLING_DIAG_UID, d686))
    w = WALK(target, d686, limit=200)
    rows = []
    for uid, (node_i, label, terms) in w.items():
        outs = [(r["i"], r["name"]) for r in terms if r["is_source"] and (r["name"] or "").strip()]
        cls = cls_of(uid, w)
        rows.append({"uid": uid, "node_index": node_i, "label": label, "class_guess": cls,
                     "n_terms": len(terms), "named_source_terms": outs})
    for r in sorted(rows, key=lambda r: r["node_index"]):
        print(("      NODE Nodes[%3d] #%-6d %-14s %-44r named-source %s"
               % (r["node_index"], r["uid"], r["class_guess"], (r["label"] or "")[:44],
                  r["named_source_terms"][:6])).encode("ascii", "replace").decode("ascii"), flush=True)
    R["census"] = {"diagram_uid": SIBLING_DIAG_UID, "diagram_index": d686, "n_nodes": len(rows), "nodes": rows}
    return d686, w, rows


def candidates_from(rows, target):
    """Scalar-shaped named SOURCE terminals, PREFERRED first, then census order (the brief pre-decides this)."""
    ordered, seen = [], set()
    by_uid = {r["uid"]: r for r in rows}

    def add(r, ti, nm, why):
        key = (r["uid"], nm)
        if key in seen:
            return
        seen.add(key)
        ordered.append({"uid": r["uid"], "node_index": r["node_index"], "term_index": ti, "name": nm,
                        "class_guess": r["class_guess"], "label": r["label"], "why": why})

    pref = by_uid.get(PREFERRED[0])
    if pref:
        hit = [(ti, nm) for ti, nm in pref["named_source_terms"] if nm == PREFERRED[1]]
        if hit:
            add(pref, hit[0][0], hit[0][1], "brief's pre-selected first candidate (#%d %r)" % PREFERRED)
        else:
            fact("the brief's first candidate #%d %r is NOT a named source terminal on Diagram #%d: #%d's named "
                 "source terminals are %s (its outer feed at d1_rewire_sources.json:2358-2373 is an UNNAMED "
                 "tunnel, out_name '') — walking the census order instead, as the brief pre-decides"
                 % (PREFERRED[0], PREFERRED[1], SIBLING_DIAG_UID, PREFERRED[0],
                    pref["named_source_terms"][:12]))
    else:
        fact("the brief's first candidate node #%d is not on Diagram #%d's Nodes[] at all" % (PREFERRED[0],
                                                                                              SIBLING_DIAG_UID))
    for r in sorted(rows, key=lambda r: r["node_index"]):
        if r["class_guess"] not in ADDRESSABLE:
            continue
        try:
            cls_index(target, r["class_guess"], r["uid"])
        except ValueError:
            continue
        for ti, nm in r["named_source_terms"]:
            if re.search(NON_SCALAR_NAME_RE, nm):
                continue
            add(r, ti, nm, "census order, scalar-shaped name")
    R["candidates"] = ordered
    return ordered


def try_candidate(c, target, loop_uid, body_uid, d686):
    """ONE attempt: OpCreateEqual_v0 (both operands = this ONE terminal) then OpStopFromNode_v0."""
    att = {"candidate": c, "created_comparison": None, "create_error": None, "stop_error": None,
           "cond_before": None, "cond_after": None, "wire_identity": None, "ok": False}
    with open(os.path.join(HERE, "opcreate_equal_labels.json"), encoding="utf-8") as f:
        eq_labels = json.load(f)
    with open(os.path.join(HERE, "opstopfromnode_labels.json"), encoding="utf-8") as f:
        sfn_labels = json.load(f)
    loop_index = [o["uid"] for o in g.report_all(target, "WhileLoop")].index(loop_uid)
    body_index = diag_index(target, body_uid)
    before = LOOP_END_REF(target, loop_index)
    att["cond_before"] = {"cond_term_uid": before.get("cond_term_uid"), "cond_wire_uid": before.get("cond_wire_uid")}
    fact("ATTEMPT #%d %r (Nodes[%d], %s): conditional terminal BEFORE = #%s wire %s (0 is EXPECTED)"
         % (c["uid"], c["name"], c["node_index"], c["class_guess"],
            before.get("cond_term_uid"), before.get("cond_wire_uid")))
    src_i = cls_index(target, c["class_guess"], c["uid"])
    cmp0 = g.uids(target, "Comparison")
    try:
        err = CREATE_NODE("equal", eq_labels, target, body_index, EQ_AT, src_cls=c["class_guess"],
                          src_index=int(src_i), src_names=[c["name"], c["name"]])
    except Exception as e:                                                        # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)
    new_cmp = g.new_since(target, "Comparison", cmp0)
    att["create_error"] = ("%s" % err) if err else None
    att["created_comparison"] = [o["uid"] for o in new_cmp]
    fact("ATTEMPT #%d %r: OpCreateEqual_v0 on body Diagram#%d[%d] from %s[%d] — op error %r; new Comparison %s"
         % (c["uid"], c["name"], body_uid, body_index, c["class_guess"], src_i, err,
            att["created_comparison"]))
    if err or len(new_cmp) != 1:
        return att
    cmp_uid = new_cmp[0]["uid"]
    w = WALK(target, body_index, limit=60)
    if cmp_uid not in w:
        att["stop_error"] = "the new Comparison #%d is not addressable as a body Nodes[] index (uids %s)" % (
            cmp_uid, sorted(w))
        fact("ATTEMPT #%d %r: %s" % (c["uid"], c["name"], att["stop_error"]))
        return att
    node_i, _lab, rows = w[cmp_uid]
    bools = [r["i"] for r in rows if r["is_source"]]
    if not bools:
        att["stop_error"] = "the new Comparison #%d has no source terminal (rows %r)" % (cmp_uid, rows)
        fact("ATTEMPT #%d %r: %s" % (c["uid"], c["name"], att["stop_error"]))
        return att
    vi = g.op(os.path.join(CLAUDEDEV, "OpStopFromNode_v0.vi"))
    vi.SetControlValue(sfn_labels["vi_path"], target)
    vi.SetControlValue(sfn_labels["loop_class"], "WhileLoop")
    vi.SetControlValue(sfn_labels["loop_index"], int(loop_index))
    vi.SetControlValue(sfn_labels["index_node"], int(node_i))
    vi.SetControlValue(sfn_labels["index_term"], int(bools[0]))
    g._run(vi)
    sfn_err = g._err(vi, sfn_labels["connect_err"]) or ""
    att["stop_error"] = sfn_err or None
    after = LOOP_END_REF(target, loop_index)
    att["cond_after"] = {"cond_term_uid": after.get("cond_term_uid"), "cond_wire_uid": after.get("cond_wire_uid")}
    fact("ATTEMPT #%d %r: OpStopFromNode_v0(loop[%d], body Nodes[%d], Terminals[%d]) error out %r; conditional "
         "terminal AFTER = #%s wire %s" % (c["uid"], c["name"], loop_index, node_i, bools[0], sfn_err[:180],
                                           after.get("cond_term_uid"), after.get("cond_wire_uid")))
    try:
        cmp_terms = terms_of(target, body_index, cmp_uid, fresh=True)
        cmp_src_wires = sorted({wv for _i, (_nm, src_, wv) in cmp_terms.items() if src_ and wv})
    except Exception as e:                                                        # noqa: BLE001
        cmp_terms, cmp_src_wires = {"error": "%s: %s" % (type(e).__name__, e)}, []
    cond_wire = after.get("cond_wire_uid")
    same_term = after.get("cond_term_uid") == before.get("cond_term_uid")
    att["wire_identity"] = {"cond_wire_uid": cond_wire, "comparison_source_wires": cmp_src_wires,
                            "same_terminal": bool(same_term), "comparison_terminals": cmp_terms,
                            "comparison_uid": cmp_uid}
    att["ok"] = bool(cond_wire) and same_term and cond_wire in cmp_src_wires
    fact("ATTEMPT #%d %r: WIRE IDENTITY — conditional wire %r, Comparison #%d source wires %s, same terminal %s "
         "=> %s" % (c["uid"], c["name"], cond_wire, cmp_uid, cmp_src_wires, same_term,
                    "WIRED BOOLEAN" if att["ok"] else "NOT ACCEPTED"))
    if not att["ok"]:
        try:
            ci = [o["uid"] for o in g.report_all(target, "Comparison")].index(cmp_uid)
            g.delete_object(target, "Comparison", ci)
            att["cleanup"] = "deleted the rejected Comparison #%d" % cmp_uid
        except Exception as e:                                                    # noqa: BLE001
            att["cleanup"] = "could NOT delete the rejected Comparison #%d: %s: %s" % (cmp_uid,
                                                                                       type(e).__name__, e)
        fact("ATTEMPT #%d %r: %s" % (c["uid"], c["name"], att["cleanup"]))
    return att


def read_state(tag, target):
    es = g.exec_state(target)
    R["readings"][tag] = es
    fact("READING %s: exec_state(%s) with the ORIGINAL PRELOADED read-only = %r  (1 = runnable, 0 = broken)"
         % (tag, os.path.basename(target), es))
    return es


def try_save(tag, target):
    t0 = time.time()
    size, err = None, None
    try:
        size = g.save(target)          # DEFAULT allow_broken=False — never gui_save (29(d), 25 finding B1)
    except Exception as e:                                                        # noqa: BLE001
        err = "%s: %s" % (type(e).__name__, e)
    rec = {"seconds": round(time.time() - t0, 2), "returned_bytes": size, "exception": err}
    fact("SAVE %s: g.save() took %.2f s, returned %r; exception = %r (allow_broken stays False; gui_save is "
         "never called)" % (tag, rec["seconds"], size, err))
    rec["file"] = file_facts("SAVE %s artefact" % tag, target)
    R["saves"][tag] = rec
    return rec


def main():
    print("=== diag_s2_scaffold  %s   (DIAGNOSTIC — Pre-decided 34(j); NO VI IS RUN, 34(f))"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    h_before = labview_handles()
    R["handles"]["before"] = h_before
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % h_before)

    # ---- step 1: gates BEFORE the copy, then the copy
    R["original"]["file"] = file_facts("G1 the ORIGINAL, read-only", ORIGINAL)
    gate("G1 the ORIGINAL exists and its md5 equals the pin", R["original"]["file"].get("md5") == ORIG_MD5,
         str(R["original"]["file"].get("md5")))
    R["s1_artefact"]["file"] = file_facts("G2 the S1 artefact, read-only, BEFORE the copy", S1_ARTEFACT)
    gate("G2 the S1 artefact md5 == 3e3d23cefd3a334001aa9d6156bf1aee and size == 474202 B, BEFORE the copy",
         R["s1_artefact"]["file"].get("md5") == S1_MD5 and R["s1_artefact"]["file"].get("size") == S1_SIZE,
         "md5 %r size %r" % (R["s1_artefact"]["file"].get("md5"), R["s1_artefact"]["file"].get("size")))

    fresh("G2b")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S1_ARTEFACT, SCRATCH)
    R["scratch"]["after_copy"] = file_facts("G3 the scratch copy", SCRATCH)
    gate("G3 the scratch copy is byte-identical to the S1 artefact",
         R["scratch"]["after_copy"].get("md5") == S1_MD5, str(R["scratch"]["after_copy"].get("md5")))

    with Preload("P"):
        g.open_panel(SCRATCH)                 # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        R["before_census"] = {c: g.count(SCRATCH, c) for c in
                              ("Diagram", "WhileLoop", "SubVI", "Function", "Wire", "Node", "Comparison",
                               "LoopTunnel")}
        fact("class census of the scratch BEFORE any edit: %r" % R["before_census"])

        # ---- step 2: the census of Diagram #686
        print("\n--- step 2: census of Diagram #%d — nodes and their OUTPUT terminal names" % SIBLING_DIAG_UID,
              flush=True)
        d686, w686, rows = census_686(SCRATCH)
        cands = candidates_from(rows, SCRATCH)
        fact("%d candidate (node, named scalar-shaped source terminal) pairs, in the pre-decided order: %s"
             % (len(cands), [(c["uid"], c["name"]) for c in cands[:12]]))
        gate("G4 Diagram #%d offers at least one named scalar-shaped SOURCE terminal to compare (34(c))"
             % SIBLING_DIAG_UID, bool(cands), "0 candidates")

        # ---- step 3: ONE While loop on Diagram #686
        print("\n--- step 3: ONE While loop on Diagram #%d (gscript.loop_in, the BUILT creator)"
              % SIBLING_DIAG_UID, flush=True)
        dg0, wl0 = g.uids(SCRATCH, "Diagram"), g.uids(SCRATCH, "WhileLoop")
        g.loop_in("while", SCRATCH, d686, LOOP_AT)
        nd, nw = g.new_since(SCRATCH, "Diagram", dg0), g.new_since(SCRATCH, "WhileLoop", wl0)
        gate("G5 exactly one new Diagram and one new WhileLoop", len(nd) == 1 and len(nw) == 1,
             "+%d diagrams, +%d while loops" % (len(nd), len(nw)))
        loop_uid, body_uid = nw[0]["uid"], nd[0]["uid"]
        R["loop"] = {"loop_uid": loop_uid, "body_uid": body_uid, "location": list(LOOP_AT)}
        fact("new WhileLoop #%d, body Diagram #%d, at %r on Diagram #%d"
             % (loop_uid, body_uid, LOOP_AT, SIBLING_DIAG_UID))

        # ---- step 4: OpCreateEqual_v0 + OpStopFromNode_v0, candidate by candidate
        print("\n--- step 4: OpCreateEqual_v0 (both operands = ONE terminal) then OpStopFromNode_v0", flush=True)
        won = None
        for c in cands[:MAX_ATTEMPTS]:
            att = try_candidate(c, SCRATCH, loop_uid, body_uid, d686)
            R["attempts"].append(att)
            if att["ok"]:
                won = att
                break
        R["winner"] = won
        gate("G6 some candidate produced exactly one new Comparison with no op error",
             any(a["created_comparison"] and not a["create_error"] for a in R["attempts"]),
             "attempts %d; create errors %r" % (len(R["attempts"]),
                                                [a["create_error"] for a in R["attempts"]]))
        gate("G7 the loop's conditional terminal is WIRED on the SAME terminal, with the uid the driving "
             "Comparison sources", bool(won),
             "no candidate produced a wired Boolean; attempts %r"
             % [(a["candidate"]["uid"], a["candidate"]["name"], a["create_error"], a["stop_error"])
                for a in R["attempts"]])
        fact("OPERAND USED: node #%d Nodes[%d] (%s) terminal %r — %s"
             % (won["candidate"]["uid"], won["candidate"]["node_index"], won["candidate"]["class_guess"],
                won["candidate"]["name"], won["candidate"]["why"]))
        fact("CONDITIONAL TERMINAL: #%s carries wire %s (driving Comparison #%s)"
             % (won["cond_after"]["cond_term_uid"], won["cond_after"]["cond_wire_uid"],
                won["wire_identity"]["comparison_uid"]))

        # ---- step 5: reading 1, and step 6: save 1
        print("\n--- steps 5+6: ExecState with the ORIGINAL preloaded, then the save", flush=True)
        es1 = read_state("1_loop_scaffolded_no_move", SCRATCH)
        gate("G8 reading 1 taken (either value is a legitimate outcome of this test)", es1 is not None,
             "exec_state = %r" % es1, fatal=False)
        s1 = try_save("1_loop_scaffolded_no_move", SCRATCH)
        gate("G9 save attempt 1 completed without raising", s1["exception"] is None, str(s1["exception"]),
             fatal=False)

        # ---- step 7: move_in #48, reading 2, save 2
        print("\n--- step 7: move_in #%d into the new body, then the same two readings" % MOVE_UID, flush=True)
        try:
            d_body = diag_index(SCRATCH, body_uid)
            t_before = terms_of(SCRATCH, diag_index(SCRATCH, 639), MOVE_UID, fresh=True)
            wired = [(i, nm, bool(src), wv) for i, (nm, src, wv) in t_before.items() if wv]
            fact("#%d BEFORE the move: %d terminals, %d wired (a move SEVERS them — 33(a)); %r"
                 % (MOVE_UID, len(t_before), len(wired), wired[:10]))
            R["move"] = {"uid": MOVE_UID, "terminals_before": len(t_before), "wired_before": len(wired),
                         "wired_rows": wired}
            new_uid = move_in(SCRATCH, MOVE_UID, d_body, (60, 60))
            _c, ou = owner_of(SCRATCH, MOVE_UID)
            _c2, ou2 = owner_of(SCRATCH, ou) if ou else (None, None)
            R["move"].update({"returned_uid": new_uid, "owner_diagram": ou, "owner_owner_loop": ou2})
            ok = (ou == body_uid and ou2 == loop_uid)
        except Exception as e:                                                    # noqa: BLE001
            R["move"] = dict(R.get("move", {}), error="%s: %s" % (type(e).__name__, e))
            ok, ou, ou2 = False, None, None
            fact("move_in #%d RAISED %s: %s" % (MOVE_UID, type(e).__name__, e))
        gate("G10 move_in #%d lands in the new loop body (owner Diagram #%s, owner(owner) WhileLoop #%s)"
             % (MOVE_UID, body_uid, loop_uid), ok, "owner %r / %r" % (ou, ou2), fatal=False)
        R["after_move_census"] = {c: g.count(SCRATCH, c) for c in
                                  ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")}
        fact("class census AFTER the move: %r" % R["after_move_census"])
        es2 = read_state("2_after_move_in_48", SCRATCH)
        gate("G11 reading 2 taken", es2 is not None, "exec_state = %r" % es2, fatal=False)
        s2 = try_save("2_after_move_in_48", SCRATCH)
        gate("G12 save attempt 2 completed without raising", s2["exception"] is None, str(s2["exception"]),
             fatal=False)
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))

    # ---- the child-process readings, on what is actually ON DISK (see the module docstring's note)
    if R["saves"].get("2_after_move_in_48", {}).get("file", {}).get("exists"):
        print("\n--- child-process re-reads of the SAVED scratch (cold, then preloaded) — one instance each",
              flush=True)
        for tag, preload in (("S2DIAG-COLD", False), ("S2DIAG-PRELOAD", True)):
            try:
                res = D1ES.run_condition(tag, SCRATCH, preload)
                R["readings"][tag] = res.get("execstate")
                fact("CHILD %s (preload=%s): ExecState %r, rc %r" % (tag, preload, res.get("execstate"),
                                                                     res.get("child_rc", res.get("rc"))))
            except Exception as e:                                                # noqa: BLE001
                fact("CHILD %s raised %s: %s" % (tag, type(e).__name__, e))
    else:
        fact("no saved scratch on disk, so the child-process cold/preloaded re-reads are SKIPPED (they can only "
             "read a file, and a restart would destroy the in-memory state)")


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at the first FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
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
        h_end = None
        try:
            h_end = labview_handles()
        except Exception:                                                         # noqa: BLE001
            pass
        R["handles"]["after"] = h_end
        print("\n--- close-out", flush=True)
        fact("refs at end: %r (every reference this script opened is closed by its opener)" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (h_end, R["handles"].get("before")))
        gate("G13 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        m_end = md5(ORIGINAL) if os.path.exists(ORIGINAL) else None
        R["original"]["md5_after"] = m_end
        fact("ORIGINAL md5 AFTER: %s (pin %s)" % (m_end, ORIG_MD5))
        if m_end != ORIG_MD5:
            print("  FAIL  G14 the ORIGINAL's md5 is unchanged  %s" % m_end, flush=True)
            fails.append("G14 original md5 unchanged")
            rc = 1
        else:
            print("  PASS  G14 the ORIGINAL's md5 is unchanged  %s" % m_end, flush=True)
            passes.append("G14 original md5 unchanged")
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + "; ".join(fails)) if fails else ""),
              flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== NO VI WAS RUN (34(f)); no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
