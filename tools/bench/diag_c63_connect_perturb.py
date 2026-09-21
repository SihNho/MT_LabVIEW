"""diag_c63_connect_perturb - cycle 63 material #1. PURE MEASUREMENT, nothing is built, no route is chosen.

THE QUESTION (STATUS `## NEXT` line 87 = docs/cycle27-plan.md Pre-decided 53(d7))
  `OpConnectNested_v1` drives `ExecState` 1 -> 0 on an UNCHANGED VI after a zero-change idempotent connect
  (tools/bench/diag_c62_negctrl.log:24-31). TWO explanations are open: the op perturbs only the READING, or it
  genuinely breaks the VI. THIS FILE MEASURES; IT DOES NOT CHOOSE BETWEEN THEM. No route is chosen or
  recommended, and docs/cycle27-plan.md / STATUS `## NEXT` are NOT edited by this run.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line of this file - CLAUDE.md "before creating any
new op, tool or recipe")
  tools/bench/diag_c62_negctrl.py            the immediate predecessor; its scaffold, its `node_on_639` uid-echo
                                             resolver and its md5-pin block are reused verbatim in shape.
  tools/recipes/build_opconnectnested_v1.py  `connect_nested_v1` - the op under test (NOT rebuilt, NOT edited)
  tools/bench/c60c_astcheck.py               the static gate (NOT edited - see THE AUTHORISED EXCEPTION below)
  grep "^def " tools/gscript.py              exec_state / open_panel / close_panel / count / node_labels /
                                             node_terms / node_terms_uid / panel_wiring / report_all /
                                             create_control / delete_object / save / ref_counts / reset
  docs/toolkit-capabilities.md               consulted for the op roster; nothing there needed extending.
  NOTHING NEW IS BUILT: no op, no gscript verb, no recipe, no device, NO EDIT to tools/gscript.py.

THE AUTHORISED STATIC-GATE EXCEPTION (decided by the judgement session of cycle 63, cited here as instructed)
  `py tools/bench/c60c_astcheck.py diag_c63_connect_perturb.py` gate 3 (`allow_broken=True` is never passed)
  WILL FAIL, and gate 2 (`gui_save` neither imported nor called) may fail, BECAUSE T2's whole question is what
  `save(path, allow_broken=True)` does. That failure IS AUTHORISED and is reported verbatim. The gate file is
  NOT edited, the argument is NOT renamed, the call is NOT wrapped to hide it from the AST, and
  CYCLE_GUARD_OFF is NEVER set. EVERY OTHER static gate must pass.

ORDER (stated because it differs from the brief's listing order, for one mechanical reason and no other)
  T3 runs FIRST. It touches no LabVIEW at all - it reads files - and T2 is allowed to hang on a save, in which
  case bgrun's deadline is the answer. Running T3 first means a T2 hang cannot also destroy T3's census.
  T3 -> md5 pins -> pre-batch restart -> T1 -> T2 -> restart -> T2 cold reopen -> closing pins.

T1 - IS THE 0 TRANSIENT? (ONE untouched scratch of D1_s3a_focus_ind.vi; NOTHING is saved in T1)
  cold ExecState (expect 1) -> resolve #10407 / #10686 on Diagram #639 by uid ECHO (never owner_of: it is
  measured to answer silently with the previous query's object, Pre-decided 53(d8)) -> find an UNWIRED SINK
  terminal for step (iii) BEFORE the connect, so the scan does not pollute the timeline -> ONE idempotent
  `connect_nested_v1(46, 24, 0, 46, 25, 0)` -> a TIMESTAMPED ExecState TIMELINE:
    (i)   EIGHT bare ExecState re-reads ~2 s apart - does it return to 1 by itself?
    (ii)  an ExecState read after EACH read-only call, in this order: count('Node') / node_terms(#10407) /
          count('Wire') / panel_wiring (all 116 rows) / count('Local') / count('ControlTerminal')
    (iii) ONE benign EDIT - `create_control` on an UNWIRED SINK terminal of a node on Diagram #639 - then the
          new control is DELETED BY UID; ExecState read after each.

T2 - DOES THE IN-MEMORY STATE SURVIVE A SAVE AND A COLD REOPEN? (a SECOND, independent scratch, KEPT on disk)
  copy the bed to claudeDev\DIAG_c63_t2_<stamp>.vi and record THAT FILE's md5/size as the BED md5 -> cold
  ExecState -> the SAME ONE idempotent connect -> `save(path, allow_broken=True)`, which routes to `gui_save`
  (tools/gscript.py:2072-2074 -> :1982), the Ctrl+S path `move_in` already calls internally at :1443; it is
  guarded to claudeDev, title-matched and mtime-confirmed, so NO new GUI exception is needed and none is
  invented. Report: whether the call raised (verbatim), the mtime delta, size before/after, md5 before vs after.
  A saved file whose md5 EQUALS the BED md5 means the in-memory edits did NOT land - reported as THE READING,
  never as a pass (that is cycle 62's C_1 false pass, 53(d7)). Then LabVIEW is RESTARTED and the written file is
  COLD-opened in the fresh instance: ExecState, count('Wire'), count('Node'), the wire uid on #10407 t0, the
  node count of Diagram #639. The file is LEFT on disk and its final path / md5 / size reported.

T3 - WHICH SHIPPED OPS CARRY THEIR OWN INTERNAL `Is Broken?` READBACK? (pure file reading, no LabVIEW)
  Census of tools/recipes/build_op*.py + tools/bench/*op*build*.py + every wrapper in tools/gscript.py for
  `Wire.Is Broken?` / property id 6371004 being BUILT INTO an op or READ BY a wrapper. Table: op VI name /
  builder file:line / reads `Is Broken?` internally YES-NO-UNKNOWN / the evidence line. UNKNOWN where no
  builder file exists is an expected and acceptable answer.

PREDICTION CONTRACT (a gate that asserts no value says so explicitly; both outcomes are results)
  P_a  the T1 scratch opens COLD at ExecState 1
  P_b  #10407 and #10686 resolve on Diagram #639 with their OWN uid echoed back; their Nodes[] indices are
       RECORDED against the brief's 24 / 25 (a mismatch is a reading, and the LIVE indices are used)
  P_c  *** wire_delta == 0 and the Wire census is unchanged (1905 -> 1905) *** - the connect is idempotent
  P_d  THE READING: ExecState immediately after the idempotent connect. NO VALUE IS ASSERTED.
  P_e  (i) eight bare re-reads: NO VALUE IS ASSERTED; the gate records whether any of them returns to 1
  P_f  (ii) each of the six read-only calls returns without raising; the ExecState after each is RECORDED and
       NO VALUE IS ASSERTED
  P_g  (iii) `create_control` on a node of a NESTED diagram: A REFUSAL IS AN EXPECTED AND ACCEPTABLE ANSWER -
       `create_control` addresses the TOP-LEVEL Nodes[] (tools/gscript.py:2395-2401) and THIS VI's top-level
       diagram is measured EMPTY (Pre-decided 53, `create_indicator` A2: 0 rows by two readers). The gate
       RECORDS what happened and asserts no value; the ExecState after it is recorded either way.
  P_h  if a control WAS created, deleting it by uid removes exactly that uid; ExecState after is recorded
  Q_a  the T2 copy's own md5 equals the bed's md5 at the moment it is taken (this is the BED md5)
  Q_b  the T2 file opens COLD at ExecState 1
  Q_c  the T2 idempotent connect also reports wire_delta == 0
  Q_d  `save(allow_broken=True)`: raise-or-not verbatim, mtime delta, size before/after, md5 before vs after.
       NO VALUE IS ASSERTED. md5 UNCHANGED == the in-memory edits did NOT land, and is reported as such.
  Q_e  after a LabVIEW RESTART, the written file's COLD ExecState / Wire / Node / #10407 t0 wire uid /
       Diagram #639 node count. NO VALUE IS ASSERTED - a cold 1 and a cold 0 are both results.
  R_a  the T3 table is produced with one row per op VI and an evidence line on every YES
  Z_*  four md5 pins hold before AND after; OpCreateLocalRead_v0.vi and OpConnectNested_v1.vi byte-unchanged;
       every scratch exists=False EXCEPT T2's deliberate file; refs opened == closed == 0 live; handles both
       sides

WHAT THIS IS NOT
  No new op, no new gscript verb, NO EDIT to tools/gscript.py, no splice (51(h)), no cast, no second
  construction, no recipe, nothing written under tools/recipes/, no VI run (34(f) - op VIs are run, the fleet's
  normal mechanism), no GUI action beyond the authorised gui_save inside `save(allow_broken=True)`, no motor /
  ASI / camera (rig ASSEMBLED), no new process device. remove_bad_wires_scripted / remove_bad_wires are neither
  imported nor called. retrospective.py / audit_cycle.py / violations.py / doc_ingest.py / prior_art_review.py
  are NOT run (54(a)).
"""
import contextlib
import io
import json
import os
import re
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                              # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index                                                 # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
RECIPES = os.path.join(ROOT, "tools", "recipes")
GSCRIPT_PY = os.path.join(ROOT, "tools", "gscript.py")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
OP_UNDER_TEST = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c63_connect_perturb.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
T1_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C63T1_%s.vi" % STAMP)
T2_FILE = os.path.join(g.CLAUDEDEV, "DIAG_c63_t2_%s.vi" % STAMP)

CASE_UID, SRC_UID, D639, WIRE_PIN = 10407, 10686, 639, 10799
BRIEF_SINK_NODE, BRIEF_SRC_NODE = 24, 25

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 63 material #1: does OpConnectNested_v1 perturb the READING or really break the VI?",
     "authorised_static_gate_exception": ("c60c_astcheck gates 2 (gui_save) and 3 (allow_broken=True) are "
                                          "EXPECTED TO FAIL in T2; authorised by the cycle-63 judgement "
                                          "session; the gate file is NOT edited and CYCLE_GUARD_OFF is NEVER "
                                          "set"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "move_in": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "chooses_no_route": True, "recommends_no_route": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "reached ONLY through save(allow_broken=True) in T2 - the authorised exception",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "t1": {}, "t2": {}, "t3": {}}


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
        raise SystemExit(1)
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
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def read_es(tag, target, leg="T1"):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "leg": leg, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s | %s] = %r   (+%.1f s)"
         % (row["step"], leg, tag, es, row["t_since_start_s"]))
    return es


def node_on_639(target, d639, uid, tag):
    """Nodes[] position of `uid` on Diagram #639, VERIFIED by the node's own uid echo.

    Deliberately NOT via owner_of: Pre-decided 53(d8) records owner_of answering silently with the PREVIOUS
    query's object. diag_c62_negctrl.py:142-179 is the same resolver; it is reused unchanged in shape.
    """
    rec = {"uid": uid}
    try:
        rows = g.node_labels(target, int(d639))
        rec["nodes_on_639"] = len(rows)
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        rec["node_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    n = next((i for i, r in enumerate(rows) if r["uid"] == uid), None)
    rec["nodes_index"] = n
    rec["label"] = next((r["label"] for r in rows if r["uid"] == uid), None)
    terms = []
    if n is not None:
        try:
            echo, trows = g.node_terms_uid(target, int(d639), n)
            rec["uid_echo"] = echo
            if echo == uid:
                terms = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                          "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                         for t in trows]
                rec["how"] = "node_labels position (verified by the node's own UID)"
            else:
                rec["how"] = "REJECTED: Nodes[%d] echoed %r, not %r" % (n, echo, uid)
        except Exception as e:                                                     # noqa: BLE001
            rec["how"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:250])
    else:
        rec["how"] = "NOT IN Diagram.Nodes[] (%d nodes listed)" % len(rows)
    rec["terminal_rows"] = terms
    fact("%s #%d on Diagram #639: Nodes[%r] label %r [%s] ; t0 %r"
         % (tag, uid, n, rec.get("label"), rec.get("how"),
            next((t for t in terms if t["i"] == 0), None)))
    R.setdefault("nodes", {})[str(uid)] = rec
    return rec


def censuses(target, tag):
    out = {}
    for cls in ("Node", "Wire", "ControlTerminal", "Local"):
        try:
            out[cls] = g.count(target, cls)
        except Exception as e:                                                     # noqa: BLE001
            out[cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:100])
    fact("CENSUS %s: %r" % (tag, out))
    return out


def call_and_read(label, fn, target, leg="T1"):
    """Run ONE read-only call, record its own return/error VERBATIM, then read ExecState after it."""
    rec = {"call": label}
    t0 = time.time()
    try:
        val = fn()
        rec["returned"] = (("%d rows" % len(val)) if isinstance(val, (list, tuple)) else val)
        rec["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["returned"] = None
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("READ-ONLY CALL %s -> returned %r, error %r" % (label, rec["returned"], rec["error_verbatim"]))
    rec["exec_state_after"] = read_es("after %s" % label, target, leg)
    return rec


# ===================================================================================== T3 (files only)
IS_BROKEN_RE = re.compile(r"6371004|Is Broken\?|IsBroken")


def t3_census():
    print("\n=== T3  WHICH SHIPPED OPS CARRY THEIR OWN INTERNAL `Is Broken?` READBACK? (files only, no LabVIEW)",
          flush=True)
    builders = []
    for d, pat in ((RECIPES, re.compile(r"^build_op.*\.py$")),
                   (BENCH, re.compile(r"^.*op.*build.*\.py$", re.I))):
        for fn in sorted(os.listdir(d)):
            if pat.match(fn):
                builders.append(os.path.join(d, fn))
    R["t3"]["builder_files_scanned"] = len(builders)

    # every op VI that actually exists on disk
    op_vis = sorted(f for f in os.listdir(g.CLAUDEDEV)
                    if f.lower().startswith("op") and f.lower().endswith(".vi"))
    R["t3"]["op_vis_on_disk"] = len(op_vis)

    built_by, evidence = {}, {}
    for path in builders:
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except Exception as e:                                                     # noqa: BLE001
            continue
        lines = src.splitlines()
        # which op VI does this builder WRITE?  `OP = os.path.join(g.CLAUDEDEV, "OpXxx_vN.vi")`
        produced = []
        for i, ln in enumerate(lines, 1):
            m = re.match(r"\s*(OP\w*)\s*=\s*os\.path\.join\([^,]+,\s*[\"'](Op[\w]*\.vi)[\"']\)", ln)
            if m and not m.group(1).startswith("OP_SRC"):
                produced.append((m.group(2), i, m.group(1)))
        # is `Wire.Is Broken?` BUILT INTO the op (a build_property / property-list site) or merely discussed?
        hits = [(i, ln.strip()) for i, ln in enumerate(lines, 1) if IS_BROKEN_RE.search(ln)]
        build_hits = [(i, ln) for i, ln in hits
                      if ("6371004" in ln and ("build_property" in ln or "(\"6371004" in ln
                                               or "'6371004'" in ln or '"6371004"' in ln))]
        read_hits = [(i, ln) for i, ln in hits if "GetControlValue" in ln or "Is Broken?\"" in ln
                     or "'Is Broken?'" in ln]
        for vi_name, decl_line, _var in produced:
            key = vi_name
            rec = built_by.setdefault(key, {"op_vi": vi_name, "builder": "%s:%d"
                                            % (os.path.relpath(path, ROOT).replace("\\", "/"), decl_line),
                                            "is_broken_internal": "NO", "evidence": ""})
            if build_hits:
                rec["is_broken_internal"] = "YES"
                rec["evidence"] = "%s:%d  %s" % (os.path.relpath(path, ROOT).replace("\\", "/"),
                                                 build_hits[0][0], build_hits[0][1][:150])
            elif read_hits:
                rec["is_broken_internal"] = "YES"
                rec["evidence"] = "%s:%d  %s" % (os.path.relpath(path, ROOT).replace("\\", "/"),
                                                 read_hits[0][0], read_hits[0][1][:150])
            elif hits:
                rec["evidence"] = "mentions only (no build/read site): %s:%d" % (
                    os.path.relpath(path, ROOT).replace("\\", "/"), hits[0][0])
        evidence[os.path.basename(path)] = len(hits)

    # DONOR LINEAGE: a v1 built additively ON a donor inherits the donor's property nodes. Record the donor
    # declarations so a YES can propagate as INHERITED rather than being read as a NO.
    lineage = {}
    for path in builders:
        try:
            src = open(path, encoding="utf-8", errors="replace").read()
        except Exception:                                                          # noqa: BLE001
            continue
        for i, ln in enumerate(src.splitlines(), 1):
            m = re.match(r"\s*SRC\w*\s*=\s*os\.path\.join\([^,]+,\s*[\"'](Op[\w]*\.vi)[\"']\)", ln)
            if m:
                for vi_name, _dl, _v in [(x, 0, 0) for x in re.findall(
                        r"OP\w*\s*=\s*os\.path\.join\([^,]+,\s*[\"'](Op[\w]*\.vi)[\"']\)", src)]:
                    lineage.setdefault(vi_name, []).append(m.group(1))
    for vi_name, donors in lineage.items():
        rec = built_by.get(vi_name)
        if not rec or rec["is_broken_internal"] == "YES":
            continue
        for dn in donors:
            drec = built_by.get(dn)
            if drec and drec["is_broken_internal"] == "YES":
                rec["is_broken_internal"] = "YES"
                rec["evidence"] = "INHERITED from donor %s -> %s" % (dn, drec["evidence"])

    rows = []
    for vi in op_vis:
        rec = built_by.get(vi)
        if rec:
            rows.append(rec)
        else:
            rows.append({"op_vi": vi, "builder": "(no builder file found)",
                         "is_broken_internal": "UNKNOWN", "evidence": ""})
    for vi_name, rec in sorted(built_by.items()):
        if vi_name not in op_vis:
            rec2 = dict(rec)
            rec2["op_vi"] = vi_name + "  (builder exists; VI not on disk)"
            rows.append(rec2)

    # tools/gscript.py wrappers that READ `Is Broken?` off an op's panel
    wrap = []
    gsrc = open(GSCRIPT_PY, encoding="utf-8", errors="replace").read().splitlines()
    cur = "(module level)"
    for i, ln in enumerate(gsrc, 1):
        m = re.match(r"def (\w+)\(", ln)
        if m:
            cur = m.group(1)
        if IS_BROKEN_RE.search(ln) and ("GetControlValue" in ln or "6371004" in ln):
            wrap.append({"wrapper": cur, "line": "tools/gscript.py:%d" % i, "evidence": ln.strip()[:150]})
    R["t3"]["gscript_wrappers_reading_is_broken"] = wrap
    R["t3"]["table"] = rows

    yes = [r for r in rows if r["is_broken_internal"] == "YES"]
    unk = [r for r in rows if r["is_broken_internal"] == "UNKNOWN"]
    print("\n  %-34s %-56s %-8s %s" % ("OP VI", "BUILDER file:line", "IsBroken", "EVIDENCE"), flush=True)
    for r in rows:
        print(("  %-34s %-56s %-8s %s" % (r["op_vi"][:34], r["builder"][:56], r["is_broken_internal"],
                                          r["evidence"][:90])).encode("ascii", "replace").decode("ascii"),
              flush=True)
    print("", flush=True)
    for w in wrap:
        print(("  WRAPPER %s at %s  ::  %s" % (w["wrapper"], w["line"], w["evidence"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    gate("R_a T3 table produced (one row per op VI; UNKNOWN where no builder file exists is acceptable)",
         len(rows) > 0, "%d rows ; YES %d ; UNKNOWN %d ; %d builder files scanned ; %d gscript wrappers read "
         "`Is Broken?`" % (len(rows), len(yes), len(unk), len(builders), len(wrap)))
    gate("R_b OpConnectNested_v1.vi is on the table and its row is YES (the measured case, "
         "diag_c62_s3b_build.log:51)",
         any(r["op_vi"].startswith("OpConnectNested_v1.vi") and r["is_broken_internal"] == "YES"
             for r in rows),
         repr(next((r for r in rows if r["op_vi"].startswith("OpConnectNested_v1.vi")), None)))
    fact("T3: %d op VIs on disk, %d rows, YES %d, UNKNOWN %d, gscript wrappers reading `Is Broken?`: %d"
         % (len(op_vis), len(rows), len(yes), len(unk), len(wrap)))
    R["t3"]["yes_rows"] = [r["op_vi"] for r in yes]


# ===================================================================================== T1
def t1():
    print("\n=== T1  IS THE 0 TRANSIENT?  (one untouched scratch; NOTHING is saved)", flush=True)
    t = R["t1"]
    shutil.copy2(S3A_ARTEFACT, T1_SCRATCH)
    try:
        g.open_panel(T1_SCRATCH)
        time.sleep(1.0)
        es0 = read_es("[cold] the untouched T1 scratch", T1_SCRATCH)
        gate("P_a the T1 scratch opens COLD at ExecState 1", es0 == 1, "%r" % (es0,))

        try:
            d639 = diag_index(T1_SCRATCH, D639)
        except Exception as e:                                                     # noqa: BLE001
            d639 = None
            t["d639_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        t["d639"] = d639
        fact("diag_index(#639) RE-READ off the machine = %r" % (d639,))

        sink = node_on_639(T1_SCRATCH, d639, CASE_UID, "SINK") if isinstance(d639, int) else {}
        src = node_on_639(T1_SCRATCH, d639, SRC_UID, "SOURCE") if isinstance(d639, int) else {}
        gate("P_b #10407 and #10686 resolve on Diagram #639 with their OWN uid echoed back",
             sink.get("uid_echo") == CASE_UID and src.get("uid_echo") == SRC_UID,
             "sink Nodes[%r] echo %r ; source Nodes[%r] echo %r"
             % (sink.get("nodes_index"), sink.get("uid_echo"), src.get("nodes_index"), src.get("uid_echo")),
             fatal=True)
        gate("P_b2 the LIVE Nodes[] indices equal the brief's %d / %d (a mismatch is a reading; the LIVE "
             "indices are used either way)" % (BRIEF_SINK_NODE, BRIEF_SRC_NODE),
             sink.get("nodes_index") == BRIEF_SINK_NODE and src.get("nodes_index") == BRIEF_SRC_NODE,
             "live sink %r ; live source %r" % (sink.get("nodes_index"), src.get("nodes_index")))

        t["census_before"] = censuses(T1_SCRATCH, "T1 BEFORE everything")

        # (iii)'s target is chosen BEFORE the connect so the scan cannot pollute the timeline.
        print("\n--- T1 setup: find an UNWIRED SINK terminal on a node of Diagram #639 (for step iii)",
              flush=True)
        bench_target = None
        try:
            rows = g.node_labels(T1_SCRATCH, int(d639))
        except Exception as e:                                                     # noqa: BLE001
            rows = []
            t["node_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        t["nodes_on_639"] = len(rows)
        for i in range(min(len(rows), 40)):
            try:
                echo, trows = g.node_terms_uid(T1_SCRATCH, int(d639), i)
            except Exception:                                                      # noqa: BLE001
                continue
            cand = next((tr for tr in trows if tr["is_source"] is False and tr["wire"] in (0, None)), None)
            if cand is not None:
                bench_target = {"nodes_index": i, "node_uid": echo,
                                "label": rows[i]["label"], "terminal_index": cand["i"],
                                "terminal_name": cand["name"]}
                break
        t["benign_edit_target"] = bench_target
        fact("the UNWIRED SINK terminal chosen for step (iii): %r" % (bench_target,))
        read_es("[after the (iii) target scan, before the connect]", T1_SCRATCH)

        # ---------------------------------------------------------------- THE ONE CONNECT
        wires_before = g.count(T1_SCRATCH, "Wire")
        es_pre = read_es("[immediately BEFORE the idempotent connect]", T1_SCRATCH)
        call = ("connect_nested_v1(target, %r, %r, 0, %r, %r, 0)"
                % (d639, sink.get("nodes_index"), d639, src.get("nodes_index")))
        t["call"] = call
        fact("THE ONE CALL: %s   (IDEMPOTENT - this pair is already joined by wire %d)" % (call, WIRE_PIN))
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_c, err_c = CONNECT_V1(T1_SCRATCH, d639, sink.get("nodes_index"), 0,
                                             d639, src.get("nodes_index"), 0, V1_LABELS)
            t["connect_result"] = {"wire_delta": dw, "exec_state_returned_by_the_op": es_c,
                                   "error_column_verbatim": err_c}
        except Exception as e:                                                     # noqa: BLE001
            t["connect_result"] = {"wire_delta": None, "exec_state_returned_by_the_op": None,
                                   "error_column_verbatim": "EXCEPTION %s: %s"
                                                            % (type(e).__name__, str(e)[:400])}
        op_out = buf.getvalue().rstrip().splitlines()
        for ln in op_out:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        t["op_stdout_verbatim"] = [ln.strip() for ln in op_out]
        t["op_readback_lines"] = [ln.strip() for ln in op_out if "readback" in ln or "Is Broken?" in ln]
        fact("connect result: %r" % (t["connect_result"],))
        fact("the op's OWN `op readback` line(s) VERBATIM: %r" % (t["op_readback_lines"],))

        wires_after = g.count(T1_SCRATCH, "Wire")
        t["wire_census_across_connect"] = {"before": wires_before, "after": wires_after}
        gate("P_c *** wire_delta == 0 and the Wire census is unchanged ***",
             t["connect_result"].get("wire_delta") == 0 and wires_before == wires_after,
             "wire_delta %r ; Wire %r -> %r" % (t["connect_result"].get("wire_delta"), wires_before,
                                                wires_after))
        es_post = read_es("[immediately AFTER the idempotent connect]", T1_SCRATCH)
        t["exec_state_across_connect"] = {"before": es_pre, "after": es_post}
        gate("P_d *** THE READING: ExecState %r -> %r across the idempotent connect (no value asserted) ***"
             % (es_pre, es_post), True, "")

        # ---------------------------------------------------------------- (i) eight bare re-reads
        print("\n--- T1 (i)  EIGHT consecutive BARE ExecState re-reads, ~2 s apart", flush=True)
        bare = []
        for k in range(8):
            if k:
                time.sleep(2.0)
            bare.append(read_es("(i) bare re-read %d/8" % (k + 1), T1_SCRATCH))
        t["bare_rereads"] = bare
        gate("P_e (i) eight bare re-reads recorded; does ExecState return to 1 BY ITSELF? (no value asserted)",
             True, "values %r ; any 1 -> %s" % (bare, any(b == 1 for b in bare)))
        fact("(i) VERDICT: ExecState %s return to 1 by itself across 8 bare re-reads over ~14 s"
             % ("DOES" if any(b == 1 for b in bare) else "does NOT"))

        # ---------------------------------------------------------------- (ii) read-only calls
        print("\n--- T1 (ii)  an ExecState read after EACH read-only call, in the brief's order", flush=True)
        sink_i = sink.get("nodes_index")
        seq = [("count('Node')", lambda: g.count(T1_SCRATCH, "Node")),
               ("node_terms(#10407 = Nodes[%r] of Diagram #639)" % sink_i,
                lambda: g.node_terms(T1_SCRATCH, int(d639), int(sink_i))),
               ("count('Wire')", lambda: g.count(T1_SCRATCH, "Wire")),
               ("panel_wiring (all 116 rows)", lambda: g.panel_wiring(T1_SCRATCH)),
               ("count('Local')", lambda: g.count(T1_SCRATCH, "Local")),
               ("count('ControlTerminal')", lambda: g.count(T1_SCRATCH, "ControlTerminal"))]
        t["read_only_sequence"] = [call_and_read(lbl, fn, T1_SCRATCH) for lbl, fn in seq]
        raised = [r["call"] for r in t["read_only_sequence"] if r["error_verbatim"]]
        gate("P_f (ii) each of the six read-only calls returned without raising", not raised, "%r" % (raised,))
        after_reads = [r["exec_state_after"] for r in t["read_only_sequence"]]
        fact("(ii) VERDICT: ExecState after the six read-only calls = %r ; any 1 -> %s"
             % (after_reads, any(x == 1 for x in after_reads)))

        # ---------------------------------------------------------------- (iii) the benign edit
        print("\n--- T1 (iii)  ONE benign EDIT: create_control on an UNWIRED SINK terminal, then delete it",
              flush=True)
        made = []
        if bench_target is None:
            t["benign_edit"] = {"skipped": "no unwired SINK terminal found on Diagram #639 in the first 40 "
                                           "nodes"}
            gate("P_g (iii) create_control attempted (a refusal is an expected, acceptable answer)", True,
                 "NOT ATTEMPTED: no unwired SINK terminal found")
        else:
            ct_before = g.count(T1_SCRATCH, "ControlTerminal")
            rec = {"target": bench_target, "ControlTerminal_before": ct_before}
            try:
                made, label = g.create_control(T1_SCRATCH, bench_target["nodes_index"],
                                               bench_target["terminal_index"])
                rec["returned"] = {"new": made, "label": label}
                rec["error_verbatim"] = ""
            except Exception as e:                                                 # noqa: BLE001
                made, rec["returned"] = [], None
                rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            rec["ControlTerminal_after"] = g.count(T1_SCRATCH, "ControlTerminal")
            fact("(iii) create_control(Nodes[%r], t%r) -> returned %r, error %r ; ControlTerminal %r -> %r"
                 % (bench_target["nodes_index"], bench_target["terminal_index"], rec.get("returned"),
                    rec["error_verbatim"], ct_before, rec["ControlTerminal_after"]))
            rec["exec_state_after_create"] = read_es("(iii) after create_control", T1_SCRATCH)
            t["benign_edit"] = rec
            gate("P_g (iii) create_control ATTEMPTED and its return/error recorded - a REFUSAL is an EXPECTED "
                 "and ACCEPTABLE answer (it addresses the TOP-LEVEL Nodes[], gscript.py:2395-2401, and this "
                 "VI's top-level diagram is measured EMPTY)", True,
                 "created %d control(s) ; error %r" % (len(made or []), rec["error_verbatim"]))

            if made:
                new_uid = made[0]["uid"]
                rec2 = {"deleted_uid": new_uid}
                try:
                    rows_ct = g.report_all(T1_SCRATCH, "ControlTerminal")
                    idx = next((i for i, o in enumerate(rows_ct) if o["uid"] == new_uid), None)
                    rec2["traverse_index"] = idx
                    gone = g.delete_object(T1_SCRATCH, "ControlTerminal", idx)
                    rec2["gone"] = sorted(gone) if gone else gone
                    rec2["error_verbatim"] = ""
                except Exception as e:                                             # noqa: BLE001
                    rec2["gone"] = None
                    rec2["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
                rec2["ControlTerminal_after_delete"] = g.count(T1_SCRATCH, "ControlTerminal")
                rec2["exec_state_after_delete"] = read_es("(iii) after deleting the new control BY UID",
                                                          T1_SCRATCH)
                t["benign_edit_delete"] = rec2
                gate("P_h (iii) the new control was deleted BY UID (exactly that uid gone)",
                     rec2.get("gone") == [new_uid], "%r" % (rec2,))
            else:
                t["benign_edit_delete"] = {"skipped": "nothing was created, so nothing is deleted"}
                gate("P_h (iii) delete-by-uid NOT REACHED (nothing was created)", True, "")

        t["census_after"] = censuses(T1_SCRATCH, "T1 AFTER everything")
        t["final_exec_state"] = read_es("[T1 final]", T1_SCRATCH)
    finally:
        try:
            g.close_panel(T1_SCRATCH)
        except Exception as e:                                                     # noqa: BLE001
            fact("T1 close_panel raised %s: %s" % (type(e).__name__, str(e)[:160]))
        if os.path.exists(T1_SCRATCH):
            try:
                os.remove(T1_SCRATCH)
            except Exception as e:                                                 # noqa: BLE001
                fact("could not remove the T1 scratch: %s" % (e,))
        R["t1"]["scratch_exists"] = os.path.exists(T1_SCRATCH)
        gate("Z_3 the T1 scratch is deleted in the same run", not R["t1"]["scratch_exists"], T1_SCRATCH)


# ===================================================================================== T2
def t2():
    print("\n=== T2  DOES THE IN-MEMORY STATE SURVIVE A SAVE AND A COLD REOPEN?  (a SECOND scratch, KEPT)",
          flush=True)
    t = R["t2"]
    shutil.copy2(S3A_ARTEFACT, T2_FILE)
    bed = probe("T2 the written file AT BIRTH (this md5 is THE BED md5)", T2_FILE)
    t["bed_md5"] = bed.get("md5")
    t["bed_size"] = bed.get("bytes", bed.get("size"))
    t["path"] = T2_FILE
    gate("Q_a the T2 copy's own md5 equals the bed's pin at birth", bed.get("md5") == S3A_MD5,
         "%r vs pin %s" % (bed.get("md5"), S3A_MD5))

    g.open_panel(T2_FILE)
    time.sleep(1.0)
    es0 = read_es("[cold] the T2 file, before any call", T2_FILE, "T2")
    gate("Q_b the T2 file opens COLD at ExecState 1", es0 == 1, "%r" % (es0,))

    try:
        d639 = diag_index(T2_FILE, D639)
    except Exception as e:                                                         # noqa: BLE001
        d639 = None
        t["d639_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    t["d639"] = d639
    sink = node_on_639(T2_FILE, d639, CASE_UID, "T2 SINK") if isinstance(d639, int) else {}
    src = node_on_639(T2_FILE, d639, SRC_UID, "T2 SOURCE") if isinstance(d639, int) else {}

    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            dw, es_c, err_c = CONNECT_V1(T2_FILE, d639, sink.get("nodes_index"), 0,
                                         d639, src.get("nodes_index"), 0, V1_LABELS)
        t["connect_result"] = {"wire_delta": dw, "exec_state_returned_by_the_op": es_c,
                               "error_column_verbatim": err_c}
    except Exception as e:                                                         # noqa: BLE001
        t["connect_result"] = {"wire_delta": None, "exec_state_returned_by_the_op": None,
                               "error_column_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
    for ln in buf.getvalue().rstrip().splitlines():
        print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    t["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
    fact("T2 connect result: %r" % (t["connect_result"],))
    gate("Q_c the T2 idempotent connect also reports wire_delta == 0",
         t["connect_result"].get("wire_delta") == 0, "%r" % (t["connect_result"].get("wire_delta"),))
    es_pre_save = read_es("[T2 after the idempotent connect, before the save]", T2_FILE, "T2")
    t["exec_state_before_save"] = es_pre_save

    # ---------------------------------------------------------------- THE SAVE (authorised exception)
    print("\n--- T2 THE SAVE: save(path, allow_broken=True) -> routes to gui_save (gscript.py:2072-2074 -> "
          ":1982). Guarded to claudeDev, title-matched, mtime-confirmed. If it HANGS, bgrun's deadline IS the "
          "answer.", flush=True)
    mt_before = os.path.getmtime(T2_FILE)
    sz_before = os.path.getsize(T2_FILE)
    md5_before = probe("T2 immediately BEFORE the save", T2_FILE).get("md5")
    sv = {"mtime_before": mt_before, "size_before": sz_before, "md5_before": md5_before}
    t0 = time.time()
    try:
        sv["save_returned"] = g.save(T2_FILE, allow_broken=True)
        sv["raised_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        sv["save_returned"] = None
        sv["raised_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    sv["save_cost_s"] = round(time.time() - t0, 1)
    sv["mtime_after"] = os.path.getmtime(T2_FILE)
    sv["mtime_delta_s"] = round(sv["mtime_after"] - mt_before, 3)
    sv["size_after"] = os.path.getsize(T2_FILE)
    md5_after = probe("T2 immediately AFTER the save", T2_FILE).get("md5")
    sv["md5_after"] = md5_after
    sv["md5_changed"] = (md5_after != md5_before)
    t["save"] = sv
    fact("T2 SAVE: returned %r, raised %r, cost %.1f s, mtime delta %r s, size %r -> %r, md5 %r -> %r"
         % (sv["save_returned"], sv["raised_verbatim"], sv["save_cost_s"], sv["mtime_delta_s"],
            sz_before, sv["size_after"], md5_before, md5_after))
    gate("Q_d *** THE SAVE READING: md5 %s across save(allow_broken=True) *** (no value asserted; an "
         "UNCHANGED md5 means THE IN-MEMORY EDITS DID NOT LAND - cycle 62's C_1 false pass)"
         % ("CHANGED" if sv["md5_changed"] else "UNCHANGED"), True,
         "mtime delta %r s ; size %r -> %r ; raised %r"
         % (sv["mtime_delta_s"], sz_before, sv["size_after"], sv["raised_verbatim"]))
    fact("READING (not a decision): the written file %s carry any in-memory change - md5 %s the BED md5 %s"
         % ("DOES" if sv["md5_changed"] else "does NOT",
            "differs from" if sv["md5_changed"] else "EQUALS", t["bed_md5"]))

    try:
        g.close_panel(T2_FILE)
    except Exception as e:                                                         # noqa: BLE001
        fact("T2 close_panel raised %s: %s" % (type(e).__name__, str(e)[:160]))

    # ---------------------------------------------------------------- THE COLD REOPEN
    print("\n--- T2 RESTART LabVIEW, then COLD-open the written file in the fresh instance", flush=True)
    R["handles"]["before_t2_restart"] = labview_handles()
    D.fresh("T2 RESTART (a FRESH LabVIEW instance for the cold reopen)")
    R["handles"]["after_t2_restart"] = labview_handles()
    cold = {}
    try:
        g.open_panel(T2_FILE)
        time.sleep(1.0)
        cold["exec_state"] = read_es("[COLD] the written file in a freshly restarted LabVIEW", T2_FILE, "T2")
        for cls in ("Wire", "Node"):
            try:
                cold["count_%s" % cls] = g.count(T2_FILE, cls)
            except Exception as e:                                                 # noqa: BLE001
                cold["count_%s" % cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        try:
            d639c = diag_index(T2_FILE, D639)
            cold["d639"] = d639c
            rows = g.node_labels(T2_FILE, int(d639c))
            cold["nodes_on_639"] = len(rows)
            n = next((i for i, r in enumerate(rows) if r["uid"] == CASE_UID), None)
            cold["case_nodes_index"] = n
            if n is not None:
                echo, trows = g.node_terms_uid(T2_FILE, int(d639c), n)
                cold["case_uid_echo"] = echo
                t0row = next((tr for tr in trows if tr["i"] == 0), None)
                cold["case_t0"] = t0row
                cold["case_t0_wire_uid"] = (t0row or {}).get("wire")
        except Exception as e:                                                     # noqa: BLE001
            cold["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    finally:
        try:
            g.close_panel(T2_FILE)
        except Exception:                                                          # noqa: BLE001
            pass
    t["cold_reopen"] = cold
    fact("T2 COLD REOPEN: %r" % (cold,))
    gate("Q_e *** THE COLD READING: the written file reopens at ExecState %r in a freshly restarted LabVIEW "
         "*** (no value asserted; #10407 t0 wire %r, Wire %r, Node %r, Diagram #639 nodes %r)"
         % (cold.get("exec_state"), cold.get("case_t0_wire_uid"), cold.get("count_Wire"),
            cold.get("count_Node"), cold.get("nodes_on_639")), True, "")
    fin = probe("T2 the written file, FINAL", T2_FILE)
    t["final"] = {"path": T2_FILE, "md5": fin.get("md5"), "size": fin.get("bytes", fin.get("size"))}
    gate("Z_4 T2's deliberate file is the ONE scratch left on disk", os.path.exists(T2_FILE), T2_FILE)


# ===================================================================================== main
def main():
    print("=== diag_c63_connect_perturb  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 63 material #1: does OpConnectNested_v1 PERTURB THE READING or REALLY BREAK THE VI?",
          flush=True)
    print("=== AUTHORISED: c60c_astcheck gates 2/3 fail in T2 (gui_save / allow_broken=True) - judgement's "
          "decision this cycle; the gate file is NOT edited, CYCLE_GUARD_OFF is NEVER set.", flush=True)

    t3_census()                      # files only - runs first so a T2 save hang cannot lose it
    dump()

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("Z0 ORIGINAL (read-only probe)", ORIGINAL)
    gate("Z_0 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("Z0b D1_s1_copy.vi", S1_ARTEFACT)
    gate("Z_0b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("Z0c D1_s2_loops.vi", S2_ARTEFACT)
    gate("Z_0c D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("Z0d D1_s3a_focus_ind.vi (the bed, NEVER written)", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("Z0e the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("Z_0e OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))
    ut = probe("Z0f the OP UNDER TEST OpConnectNested_v1.vi", OP_UNDER_TEST)
    R["op_under_test_md5_before"] = ut.get("md5")
    fact("OpConnectNested_v1.vi md5 BEFORE (measured now, the closing gate compares against it): %r"
         % (ut.get("md5"),))

    D.fresh("Z_R RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    try:
        t1()
    finally:
        dump()
    try:
        t2()
    finally:
        dump()

    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                         # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    z4 = probe("Z1e the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    z5 = probe("Z1f the OP UNDER TEST OpConnectNested_v1.vi after everything", OP_UNDER_TEST)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5,
         "%s" % (z4.get("md5"),))
    gate("Z_1c the OP UNDER TEST OpConnectNested_v1.vi is byte-unchanged across the run",
         z5.get("md5") == R.get("op_under_test_md5_before"),
         "%r -> %r" % (R.get("op_under_test_md5_before"), z5.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1d refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1e every scratch is gone EXCEPT T2's deliberate file",
         (not os.path.exists(T1_SCRATCH)) and os.path.exists(T2_FILE),
         "T1 exists=%r ; T2 exists=%r" % (os.path.exists(T1_SCRATCH), os.path.exists(T2_FILE)))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-4s %-58s %-12s %-10s" % ("step", "leg", "call / tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-4s %-58s %-12r %-10s" % (row["step"], row["leg"], row["tag"][:58],
                                                  row["exec_state"], row["wall_clock"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
