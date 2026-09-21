"""diag_c64_perturb_t1t3 - cycle 64 material #1. PURE MEASUREMENT, nothing is built, nothing is saved.

THE QUESTION (docs/cycle27-plan.md Pre-decided 53(d7))
  `OpConnectNested_v1` drives `ExecState` 1 -> 0 on an UNCHANGED VI after a zero-change idempotent connect
  (tools/bench/diag_c62_negctrl.log:24-31). TWO explanations are open: the op perturbs only the READING, or it
  genuinely breaks the VI. THIS FILE MEASURES; IT DOES NOT CHOOSE BETWEEN THEM. No route is chosen or
  recommended, and docs/cycle27-plan.md / STATUS `## NEXT` are NOT edited by this run.

THE SAVE LEG IS DROPPED - judgement's decision of cycle 64
  The predecessor tools/bench/diag_c63_connect_perturb.py (826 lines, 30 gate sites) carried a T2 leg built on
  `save(path, allow_broken=True)` -> `gui_save`. It NEVER RAN: its static gate failed
  (tools/bench/c63_astcheck.log:15 `ASTCHECK FAILED; failing: 3 allow_broken=True is never passed`) and the
  runner's bgrun deadline killed the process tree at 11:56. THIS file is that file with **T2 DELETED ENTIRELY**:
  no save of any VI, no `allow_broken`, no `gui_save`, no write of any VI file, no GUI action of any kind.
  Consequently `py tools/bench/c60c_astcheck.py diag_c64_perturb_t1t3.py` must come back ASTCHECK OK on EVERY
  gate - gates 2 and 3 now pass because neither `gui_save` nor `allow_broken` appears as a call or an import.
  A failing static gate is reported VERBATIM and STOPS the run; the gate file is NOT edited, no argument is
  renamed, no call is hidden from the AST, and CYCLE_GUARD_OFF is NEVER set.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line of this file - CLAUDE.md "before creating any
new op, tool or recipe")
  tools/bench/diag_c63_connect_perturb.py    the direct parent; T1 + T3 are carried over, T2 is deleted.
  tools/bench/diag_c62_negctrl.py            the `node_on_639` uid-echo resolver and the md5-pin block.
  tools/recipes/build_opconnectnested_v1.py  `connect_nested_v1` - the op under test (NOT rebuilt, NOT edited)
  tools/bench/c60c_astcheck.py               the static gate (NOT edited)
  grep "^def " tools/gscript.py              exec_state :1977 / vi_ref :244 / reset :262 / open_panel :1241 /
                                             close_panel :1257 / count / node_labels / node_terms /
                                             node_terms_uid / panel_wiring / report_all / create_control /
                                             delete_object / ref_counts - ALL ALREADY EXIST; none is added.
  docs/toolkit-capabilities.md               consulted for the op roster; nothing there needed extending.
  NOTHING NEW IS BUILT: no op, no gscript verb, no recipe, no device, NO EDIT to tools/gscript.py.

ORDER (stated because it differs from the brief's listing order, for one mechanical reason and no other)
  T0 (leftover check, files only) -> T3 (files only) -> md5 pins -> pre-batch restart -> T1 -> closing pins.
  T3 touches no LabVIEW at all, so no later COM hang can destroy its census.

T0 - THE c63 LEFTOVER (files only)
  Does `claudeDev\DIAG_c63_t2_*.vi` exist? The run that would have created it never started. Any match is
  reported (name / size / md5) and DELETED. Nothing else is deleted.

T3 - WHICH SHIPPED OPS CARRY THEIR OWN INTERNAL `Is Broken?` READBACK? (pure file reading, no LabVIEW)
  Census of tools/recipes/build_op*.py + tools/bench/*op*build*.py + every wrapper in tools/gscript.py for
  `Wire.Is Broken?` / property id 6371004 being BUILT INTO an op or READ BY a wrapper. Table: op VI name /
  builder file:line / reads `Is Broken?` internally YES-NO-UNKNOWN / the evidence line. UNKNOWN where no
  builder file exists is an expected and acceptable answer.

T1 - IS THE 0 TRANSIENT? (ONE untouched scratch of D1_s3a_focus_ind.vi; NOTHING is saved anywhere in T1)
  cold ExecState (expect 1) -> resolve #10407 / #10686 on Diagram #639 by uid ECHO (never owner_of: it is
  measured to answer silently with the previous query's object, Pre-decided 53(d8)) -> find an UNWIRED SINK
  terminal for step (iii) BEFORE the connect, so the scan does not pollute the timeline -> ONE idempotent
  `connect_nested_v1(46, 24, 0, 46, 25, 0)` -> a TIMESTAMPED ExecState TIMELINE:
    (i)   EIGHT bare ExecState re-reads ~2 s apart - does it return to 1 by itself?
    (ii)  an ExecState read after EACH read-only call, in this order: count('Node') / node_terms(#10407) /
          count('Wire') / panel_wiring (all 116 rows) / count('Local') / count('ControlTerminal')
    (iii) ONE benign EDIT - `create_control` on an UNWIRED SINK terminal of a node on Diagram #639 - then the
          new control is DELETED BY UID; ExecState read after each.
    (iv)  NEW, THE FRESH-REFERENCE LEG. LabVIEW is NOT restarted. Three readings in one place:
          (a) through the reference the run has been using, held open across the read;
          (b) that reference is RELEASED and a NEW VI Server reference to the SAME in-memory VI is acquired,
              and ExecState is read through THAT;
          (c) the Application proxy itself is dropped (`gscript.reset()`, which forgets `_lv` and every cached
              op-VI reference) and a completely new COM Dispatch + GetVIReference reads it again.
          MEASURED FACT recorded before the run, because it changes how (a)/(b) must be read: `gscript.exec_state`
          (tools/gscript.py:1977-1979) ALREADY opens a short-lived `vi_ref` per call and releases it, so EVERY
          ExecState reading in this whole file is already taken through a fresh VI reference. (iv) makes that
          explicit and adds the one thing the per-call path does NOT do - dropping the Application proxy.
    (v)   NEW, THE SECOND-BED LEG. With the perturbed scratch STILL OPEN in the same LabVIEW session, a SECOND
          independent scratch duplicate of the SAME bed is opened and its COLD ExecState read. Then it is
          deleted. The perturbed scratch is read once more afterwards. Upgraded per the review's 3: the BED
          FILE itself and the OP UNDER TEST are also read (ExecState only, never opened for edit, never
          written) BEFORE and AFTER the connect, so session-level damage would come with a LOCATION.

ARMS B and C - THE DISCRIMINATING TEST THE REVIEW NAMED (archive/peer/2026-09-21-c64-astgate3.md, its 5)
  The review's central attack is that T1 measures ONE WELDED EVENT: `OpConnectNested_v1` performs a connect
  AND an ordered `Wire.Is Broken?` property read inside the same op (docs/NAMES.md:902-908), so no number of
  readings downstream can say which half produced the 0. Both arms are PURE MEASUREMENT on their own throwaway
  scratch of the same bed, deleted in the same run; they build nothing, save nothing, add no op and do not
  touch tools/gscript.py. THEY ARE RUN UNCONDITIONALLY - neither is conditioned on the other's result, so no
  result-dependent decision is taken inside this material session.
  ARM B  `gscript.connect2` :2671 -> `OpConnect2_v0.vi`, the SAME idempotent pair, through a connect op that
         T3 measures for an internal `Is Broken?` readback (the arm records T3's verdict beside its own
         reading rather than relying on a doc). Verified the same way as T1: uid echo on both nodes,
         wire_delta, and the sink terminal still carrying wire 10799 afterwards - if the echo or the wire
         does not match, the arm is a NON-RESULT and is reported as one, never as a 0.
  ARM C  `gscript.set_node_label` :2694 -> `OpSetLabel_v0.vi` writes a node's label back to the SAME TEXT it
         already has: a scripting edit that touches NO WIRE AT ALL. Recorded because it leaves the op's junk
         Invoke on the target (gscript.py:2697); the Node census is taken either side. NOTHING IS SAVED, so
         the junk dies with the scratch.
  NO VALUE IS ASSERTED BY EITHER ARM and no route is chosen from them.

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
  P_i  (iv) the OLD-reference and NEW-reference ExecState readings are both taken and reported. NO VALUE IS
       ASSERTED - equal and different are both results.
  P_j  (v) the SECOND bed's COLD ExecState is read in the SAME LabVIEW session while the perturbed scratch is
       still open. NO VALUE IS ASSERTED.
  P_k  (v) the BED FILE and the OP UNDER TEST are read (ExecState) before AND after the connect, never opened
       for edit and never written. NO VALUE IS ASSERTED; their md5 pins are re-checked at the end anyway.
  P_l  ARM B: the same idempotent pair through `connect2` / OpConnect2_v0 on its own fresh scratch. The arm
       COUNTS only if both nodes echo their own uid AND wire_delta == 0 AND the sink terminal still carries
       wire 10799 afterwards; otherwise it is reported as a NON-RESULT. NO ExecState VALUE IS ASSERTED.
  P_m  ARM C: `set_node_label` writes a node's label back to the text it already has, on its own fresh
       scratch - a scripting edit touching no wire. Node census either side. NO VALUE IS ASSERTED.
  R_a  the T3 table is produced with one row per op VI and an evidence line on every YES
  R_c  T3's verdict for OpConnect2_v0.vi is recorded and printed beside ARM B (YES/NO/UNKNOWN), so the arm is
       read against a measurement of our own files rather than against a sentence in a doc
  Z_*  four md5 pins hold before AND after; OpCreateLocalRead_v0.vi and OpConnectNested_v1.vi byte-unchanged;
       EVERY scratch exists=False at the end; refs opened == closed == 0 live; handles both sides

WHAT THIS IS NOT
  No save of any VI, no `allow_broken`, no `gui_save`, no GUI action of any kind, no new op, no new gscript
  verb, NO EDIT to tools/gscript.py, no splice (51(h)), no cast, no second construction, no recipe, nothing
  written under tools/recipes/, no VI run (34(f) - op VIs are run, the fleet's normal mechanism), no motor /
  ASI / camera (rig ASSEMBLED), no new process device. remove_bad_wires_scripted / remove_bad_wires are
  neither imported nor called. retrospective.py / audit_cycle.py / violations.py / doc_ingest.py /
  prior_art_review.py are NOT run (54(a)). No route is chosen and none is recommended.
"""
import contextlib
import glob as globmod
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
OUT = os.path.join(BENCH, "diag_c64_perturb_t1t3.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
T1_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64T1_%s.vi" % STAMP)
T1B_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64T1B_%s.vi" % STAMP)
ARMB_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64ARMB_%s.vi" % STAMP)
ARMC_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64ARMC_%s.vi" % STAMP)
SCRATCHES = (T1_SCRATCH, T1B_SCRATCH, ARMB_SCRATCH, ARMC_SCRATCH)
C63_LEFTOVER_GLOB = os.path.join(g.CLAUDEDEV, "DIAG_c63_t2_*.vi")

CASE_UID, SRC_UID, D639, WIRE_PIN = 10407, 10686, 639, 10799
BRIEF_SINK_NODE, BRIEF_SRC_NODE = 24, 25

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 64 material #1: does OpConnectNested_v1 perturb the READING or really break the VI?",
     "save_leg_dropped": ("judgement's decision this cycle: no save(), no allow_broken, no gui_save, no write "
                          "of any VI file - so c60c_astcheck must be OK on EVERY gate"),
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "move_in": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "no_save": "g.save is neither imported nor called anywhere in this file",
     "no_gui_action": True,
     "chooses_no_route": True, "recommends_no_route": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "t0": {}, "t1": {}, "t3": {},
     "arm_b": {}, "arm_c": {},
     "peer_review_that_named_the_arms": "archive/peer/2026-09-21-c64-astgate3.md (claude/hypothesis, ANSWERED)"}


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


def read_es_through(tag, ref, leg="T1"):
    """ExecState through a reference the CALLER holds open (the (iv) leg), recorded on the same timeline."""
    t0 = time.time()
    try:
        es = int(ref.ExecState)
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


def read_neighbours(when):
    """ExecState of the BED FILE and of the OP UNDER TEST - read only, never opened for edit, never written.

    The review's 3 (archive/peer/2026-09-21-c64-astgate3.md): if the session takes damage, these give it a
    LOCATION; if they stay 1 while the scratch reads 0, the damage is confined to the scratch. Their md5 pins
    are re-checked at the end of the run either way.
    """
    rec = {"when": when,
           "bed_file": read_es("[%s] the BED FILE itself (read-only, never written)" % when, S3A_ARTEFACT,
                               "NEIGH"),
           "op_under_test": read_es("[%s] the OP UNDER TEST OpConnectNested_v1.vi" % when, OP_UNDER_TEST,
                                    "NEIGH")}
    R["t1"].setdefault("neighbours", []).append(rec)
    return rec


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


# ===================================================================================== T0 (files only)
def t0_leftover():
    print("\n=== T0  THE c63 LEFTOVER: does claudeDev\\DIAG_c63_t2_*.vi exist? (files only, no LabVIEW)",
          flush=True)
    hits = sorted(globmod.glob(C63_LEFTOVER_GLOB))
    R["t0"]["pattern"] = C63_LEFTOVER_GLOB
    R["t0"]["matches_found"] = len(hits)
    rows = []
    for p in hits:
        rec = {"name": os.path.basename(p), "size": os.path.getsize(p)}
        try:
            rec["md5"] = probe("T0 c63 leftover %s" % rec["name"], p).get("md5")
        except Exception as e:                                                     # noqa: BLE001
            rec["md5"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        try:
            os.remove(p)
            rec["deleted"] = not os.path.exists(p)
        except Exception as e:                                                     # noqa: BLE001
            rec["deleted"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
        rows.append(rec)
        fact("T0 c63 leftover: %r" % (rec,))
    R["t0"]["rows"] = rows
    if not hits:
        fact("T0: NO file matches DIAG_c63_t2_*.vi - the c63 run that would have created it never started, "
             "so there is nothing to delete. Nothing else was deleted.")
    gate("T0_a the c63 leftover pattern is checked and any match deleted (0 matches is the expected answer)",
         not globmod.glob(C63_LEFTOVER_GLOB),
         "%d match(es) found ; %d remain" % (len(hits), len(globmod.glob(C63_LEFTOVER_GLOB))))


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
        except Exception:                                                          # noqa: BLE001
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
                for vi_name in re.findall(
                        r"OP\w*\s*=\s*os\.path\.join\([^,]+,\s*[\"'](Op[\w]*\.vi)[\"']\)", src):
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
    # T3 is ARM B's instrument, not a docs artefact: the arm is read against THIS measurement.
    c2 = next((r for r in rows if r["op_vi"].startswith("OpConnect2_v0.vi")), None)
    R["t3"]["OpConnect2_v0_verdict"] = (c2 or {}).get("is_broken_internal", "NOT ON THE TABLE")
    R["t3"]["OpConnect2_v0_row"] = c2
    gate("R_c T3's verdict for OpConnect2_v0.vi (ARM B's op) is recorded and reported beside the arm",
         c2 is not None, "internal `Is Broken?` readback = %r ; row %r"
         % (R["t3"]["OpConnect2_v0_verdict"], c2))
    fact("ARM B's op OpConnect2_v0.vi carries an internal `Is Broken?` readback: %r (measured from our own "
         "builder files, not from a doc)" % (R["t3"]["OpConnect2_v0_verdict"],))


# ===================================================================================== T1
def t1():
    print("\n=== T1  IS THE 0 TRANSIENT?  (one untouched scratch; NOTHING is saved anywhere)", flush=True)
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
        read_neighbours("BEFORE the connect")

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
        fact("the op's OWN `op readback` line(s) VERBATIM (this is where `Is Broken?` / `UID 2` are printed): "
             "%r" % (t["op_readback_lines"],))

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

        # ---------------------------------------------------------------- (iv) THE FRESH-REFERENCE LEG
        print("\n--- T1 (iv)  FRESH-REFERENCE LEG: release the VI reference, acquire a NEW one to the SAME "
              "in-memory VI. LabVIEW is NOT restarted.", flush=True)
        ref = {"measured_before_the_run": ("gscript.exec_state (tools/gscript.py:1977-1979) already opens a "
                                           "SHORT-LIVED vi_ref per call and releases it in a finally - so "
                                           "every ExecState reading above was ALREADY taken through a fresh "
                                           "VI Server reference. (iv) makes that explicit and adds the one "
                                           "thing the per-call path does not do: dropping the Application "
                                           "proxy itself.")}
        ref["ref_counts_before"] = g.ref_counts()
        try:
            with g.vi_ref(T1_SCRATCH) as r_old:
                ref["old_reference_reading"] = read_es_through(
                    "(iv a) through the OLD reference, held open", r_old)
                ref["old_reference_reading_2"] = read_es_through(
                    "(iv a2) same OLD reference, second read", r_old)
            # the `with` has now RELEASED that reference (gscript.vi_ref drops the only name in its finally)
            fact("(iv) the OLD reference is RELEASED; ref_counts now %r" % (g.ref_counts(),))
            with g.vi_ref(T1_SCRATCH) as r_new:
                ref["new_reference_reading"] = read_es_through(
                    "(iv b) through a BRAND-NEW reference to the SAME in-memory VI", r_new)
        except Exception as e:                                                     # noqa: BLE001
            ref["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        ref["ref_counts_after_ab"] = g.ref_counts()
        # (iv c) drop the Application proxy and every cached op-VI proxy, then read again. LabVIEW itself is
        # NOT restarted and the VI stays loaded - only this process's COM proxies are discarded.
        try:
            g.reset()
            ref["reset_called"] = "gscript.reset() - _lv and the op-VI cache dropped; LabVIEW NOT restarted"
        except Exception as e:                                                     # noqa: BLE001
            ref["reset_called"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        ref["after_fresh_dispatch_reading"] = read_es(
            "(iv c) after gscript.reset(): a NEW COM Dispatch + a NEW VI reference", T1_SCRATCH)
        # IDENTITY CHECK, per the review's 3: a changed reading after reset() would be ambiguous between "the
        # proxy was stale" and "the VI was silently UNLOADED and reloaded from the untouched disk file"
        # (nothing is saved, so a reload yields a pristine VI). These two readbacks separate them: the same
        # node uid echo and the same t0 wire uid say it is still the same in-memory object.
        try:
            d639b = diag_index(T1_SCRATCH, D639)
            ref["d639_after_reset"] = d639b
            rows_after = g.node_labels(T1_SCRATCH, int(d639b))
            n_after = next((i for i, r in enumerate(rows_after) if r["uid"] == CASE_UID), None)
            ref["case_nodes_index_after_reset"] = n_after
            if n_after is not None:
                echo_a, trows_a = g.node_terms_uid(T1_SCRATCH, int(d639b), n_after)
                ref["case_uid_echo_after_reset"] = echo_a
                t0a = next((tr for tr in trows_a if tr["i"] == 0), None)
                ref["case_t0_after_reset"] = t0a
                ref["case_t0_wire_uid_after_reset"] = (t0a or {}).get("wire")
        except Exception as e:                                                     # noqa: BLE001
            ref["identity_check_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("(iv) IDENTITY CHECK after reset(): #10407 echo %r, its t0 wire uid %r (the pre-connect pin is "
             "%d) - same object, or a silent reload?"
             % (ref.get("case_uid_echo_after_reset"), ref.get("case_t0_wire_uid_after_reset"), WIRE_PIN))
        t["fresh_reference_leg"] = ref
        gate("P_i (iv) the OLD-reference and NEW-reference readings are both taken (no value asserted)",
             ("old_reference_reading" in ref and "new_reference_reading" in ref),
             "OLD %r / OLD again %r -> released -> NEW %r ; after reset() + fresh Dispatch %r"
             % (ref.get("old_reference_reading"), ref.get("old_reference_reading_2"),
                ref.get("new_reference_reading"), ref.get("after_fresh_dispatch_reading")))
        fact("(iv) VERDICT: OLD ref %r ; NEW ref %r ; after a fresh Application Dispatch %r - a NEW reference "
             "%s the reading"
             % (ref.get("old_reference_reading"), ref.get("new_reference_reading"),
                ref.get("after_fresh_dispatch_reading"),
                "CHANGES" if ref.get("new_reference_reading") != ref.get("old_reference_reading")
                else "does NOT change"))

        # ---------------------------------------------------------------- (v) THE SECOND-BED LEG
        print("\n--- T1 (v)  SECOND-BED LEG: a SECOND independent scratch of the SAME bed, opened in the SAME "
              "LabVIEW session while the perturbed scratch is STILL OPEN.", flush=True)
        second = {"path": T1B_SCRATCH}
        try:
            shutil.copy2(S3A_ARTEFACT, T1B_SCRATCH)
            second["md5_at_birth"] = probe("(v) the SECOND bed at birth", T1B_SCRATCH).get("md5")
            second["md5_equals_the_bed_pin"] = (second["md5_at_birth"] == S3A_MD5)
            g.open_panel(T1B_SCRATCH)
            time.sleep(1.0)
            second["cold_exec_state"] = read_es(
                "(v) [COLD] the SECOND, untouched bed - same LabVIEW session, perturbed scratch still open",
                T1B_SCRATCH, "T1b")
            for cls in ("Wire", "Node"):
                try:
                    second["count_%s" % cls] = g.count(T1B_SCRATCH, cls)
                except Exception as e:                                             # noqa: BLE001
                    second["count_%s" % cls] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
        except Exception as e:                                                     # noqa: BLE001
            second["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        gate("P_j (v) the SECOND bed's COLD ExecState is read in the SAME session (no value asserted)",
             "cold_exec_state" in second,
             "SECOND bed cold ExecState %r ; Wire %r ; Node %r ; md5 == the bed pin -> %r"
             % (second.get("cold_exec_state"), second.get("count_Wire"), second.get("count_Node"),
                second.get("md5_equals_the_bed_pin")))
        try:
            g.close_panel(T1B_SCRATCH)
        except Exception as e:                                                     # noqa: BLE001
            fact("(v) close_panel on the second bed raised %s: %s" % (type(e).__name__, str(e)[:160]))
        if os.path.exists(T1B_SCRATCH):
            try:
                os.remove(T1B_SCRATCH)
            except Exception as e:                                                 # noqa: BLE001
                fact("(v) could not remove the second scratch: %s" % (e,))
        second["scratch_exists"] = os.path.exists(T1B_SCRATCH)
        t["second_bed_leg"] = second
        gate("Z_3b the SECOND scratch is deleted in the same run", not second["scratch_exists"], T1B_SCRATCH)

        # the perturbed scratch, read once more after the second bed came and went
        t["exec_state_after_the_second_bed"] = read_es(
            "[the PERTURBED scratch, read again after the second bed was opened and closed]", T1_SCRATCH)
        nb = read_neighbours("AFTER the connect")
        gate("P_k (v) the BED FILE and the OP UNDER TEST were read either side of the connect (no value "
             "asserted; their md5 pins are re-checked at the end)",
             len(R["t1"].get("neighbours", [])) == 2,
             "BEFORE %r -> AFTER %r"
             % (R["t1"]["neighbours"][0] if R["t1"].get("neighbours") else None, nb))

        t["census_after"] = censuses(T1_SCRATCH, "T1 AFTER everything")
        t["final_exec_state"] = read_es("[T1 final]", T1_SCRATCH)
    finally:
        for p in (T1_SCRATCH, T1B_SCRATCH):
            try:
                if os.path.exists(p):
                    g.close_panel(p)
            except Exception as e:                                                 # noqa: BLE001
                fact("close_panel(%s) raised %s: %s" % (os.path.basename(p), type(e).__name__, str(e)[:160]))
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:                                             # noqa: BLE001
                    fact("could not remove %s: %s" % (os.path.basename(p), e))
        R["t1"]["scratch_exists"] = os.path.exists(T1_SCRATCH)
        R["t1"]["second_scratch_exists"] = os.path.exists(T1B_SCRATCH)
        gate("Z_3 both T1 scratches are deleted in the same run",
             not (R["t1"]["scratch_exists"] or R["t1"]["second_scratch_exists"]),
             "T1 exists=%r ; T1b exists=%r" % (R["t1"]["scratch_exists"], R["t1"]["second_scratch_exists"]))


# ===================================================================================== ARM B / ARM C
def _fresh_bed(path, tag, leg):
    """Copy the bed to `path`, open it, read its cold ExecState, resolve #10407 / #10686 by uid echo."""
    shutil.copy2(S3A_ARTEFACT, path)
    g.open_panel(path)
    time.sleep(1.0)
    rec = {"path": path, "cold_exec_state": read_es("[cold] %s" % tag, path, leg)}
    try:
        rec["d639"] = diag_index(path, D639)
    except Exception as e:                                                         # noqa: BLE001
        rec["d639"] = None
        rec["d639_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    if isinstance(rec["d639"], int):
        rec["sink"] = node_on_639(path, rec["d639"], CASE_UID, "%s SINK" % tag)
        rec["source"] = node_on_639(path, rec["d639"], SRC_UID, "%s SOURCE" % tag)
    else:
        rec["sink"], rec["source"] = {}, {}
    rec["t0_wire_before"] = next((t["wire"] for t in rec["sink"].get("terminal_rows", []) if t["i"] == 0),
                                 None)
    rec["wire_census_before"] = g.count(path, "Wire")
    return rec


def _drop_scratch(path, leg):
    try:
        g.close_panel(path)
    except Exception as e:                                                         # noqa: BLE001
        fact("%s close_panel raised %s: %s" % (leg, type(e).__name__, str(e)[:160]))
    if os.path.exists(path):
        try:
            os.remove(path)
        except Exception as e:                                                     # noqa: BLE001
            fact("%s could not remove %s: %s" % (leg, os.path.basename(path), e))
    return os.path.exists(path)


def arm_b():
    """THE DISCRIMINATING TEST the review named: the SAME idempotent pair through a connect op that does NOT
    carry the embedded `Is Broken?` reader. Pure measurement, own scratch, nothing saved, no new op."""
    print("\n=== ARM B  the SAME idempotent connect through `connect2` / OpConnect2_v0 (T3 verdict for its "
          "internal `Is Broken?` readback: %r)" % (R["t3"].get("OpConnect2_v0_verdict"),), flush=True)
    a = R["arm_b"]
    a["op"] = "gscript.connect2 (tools/gscript.py:2671) -> OpConnect2_v0.vi"
    a["t3_verdict_for_this_op"] = R["t3"].get("OpConnect2_v0_verdict")
    try:
        rec = _fresh_bed(ARMB_SCRATCH, "ARM B scratch", "ARMB")
        a.update(rec)
        sink_i = rec["sink"].get("nodes_index")
        src_i = rec["source"].get("nodes_index")
        a["echoes_ok"] = (rec["sink"].get("uid_echo") == CASE_UID
                          and rec["source"].get("uid_echo") == SRC_UID)
        es_pre = read_es("[ARM B] immediately BEFORE connect2", ARMB_SCRATCH, "ARMB")
        a["exec_state_before"] = es_pre
        a["call"] = "connect2(target, %r, %r, 0, %r, 0)" % (rec["d639"], sink_i, src_i)
        fact("ARM B THE ONE CALL: %s   (the SAME pair T1 connects, through the OTHER op)" % a["call"])
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_ret = g.connect2(ARMB_SCRATCH, rec["d639"], sink_i, 0, src_i, 0)
            a["wire_delta"] = dw
            a["exec_state_returned_by_the_wrapper"] = es_ret
            a["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            a["wire_delta"], a["exec_state_returned_by_the_wrapper"] = None, None
            a["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        a["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
        for ln in a["op_stdout_verbatim"]:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        a["wire_census_after"] = g.count(ARMB_SCRATCH, "Wire")
        a["exec_state_after"] = read_es("[ARM B] immediately AFTER connect2", ARMB_SCRATCH, "ARMB")
        # is it the SAME experiment as T1's? the sink must still carry wire 10799
        try:
            d = diag_index(ARMB_SCRATCH, D639)
            rows = g.node_labels(ARMB_SCRATCH, int(d))
            n = next((i for i, r in enumerate(rows) if r["uid"] == CASE_UID), None)
            echo, trows = g.node_terms_uid(ARMB_SCRATCH, int(d), n)
            a["uid_echo_after"] = echo
            a["t0_after"] = next((tr for tr in trows if tr["i"] == 0), None)
            a["t0_wire_after"] = (a["t0_after"] or {}).get("wire")
        except Exception as e:                                                     # noqa: BLE001
            a["readback_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        a["counts_as_the_same_experiment"] = bool(
            a.get("echoes_ok") and a.get("wire_delta") == 0
            and a.get("t0_wire_before") == WIRE_PIN and a.get("t0_wire_after") == WIRE_PIN)
        fact("ARM B: ExecState %r -> %r ; wire_delta %r ; Wire %r -> %r ; #10407 t0 wire %r -> %r ; error %r"
             % (a.get("exec_state_before"), a.get("exec_state_after"), a.get("wire_delta"),
                a.get("wire_census_before"), a.get("wire_census_after"), a.get("t0_wire_before"),
                a.get("t0_wire_after"), a.get("error_verbatim")))
        gate("P_l ARM B ran and its comparability is recorded (a NON-RESULT is an acceptable answer; NO "
             "ExecState value is asserted)", True,
             "counts_as_the_same_experiment=%r ; echoes_ok=%r ; wire_delta=%r ; t0 wire %r -> %r ; "
             "ExecState %r -> %r"
             % (a.get("counts_as_the_same_experiment"), a.get("echoes_ok"), a.get("wire_delta"),
                a.get("t0_wire_before"), a.get("t0_wire_after"), a.get("exec_state_before"),
                a.get("exec_state_after")))
    finally:
        a["scratch_exists"] = _drop_scratch(ARMB_SCRATCH, "ARM B")
        gate("Z_3c the ARM B scratch is deleted in the same run", not a["scratch_exists"], ARMB_SCRATCH)


def arm_c():
    """A scripting edit that touches NO WIRE: write a node's label back to the text it already has."""
    print("\n=== ARM C  `set_node_label` writes a node's EXISTING label back - a scripting edit with no wire",
          flush=True)
    a = R["arm_c"]
    a["op"] = "gscript.set_node_label (tools/gscript.py:2694) -> OpSetLabel_v0.vi"
    a["note"] = "leaves the op's junk Invoke on the target (gscript.py:2697); nothing is saved"
    try:
        rec = _fresh_bed(ARMC_SCRATCH, "ARM C scratch", "ARMC")
        a.update(rec)
        node_i = rec["source"].get("nodes_index")
        a["node_index"] = node_i
        a["label_before"] = rec["source"].get("label")
        a["node_census_before"] = g.count(ARMC_SCRATCH, "Node")
        es_pre = read_es("[ARM C] immediately BEFORE set_node_label", ARMC_SCRATCH, "ARMC")
        a["exec_state_before"] = es_pre
        fact("ARM C THE ONE CALL: set_node_label(target, %r, %r, %r) - the SAME text it already carries"
             % (rec["d639"], node_i, a["label_before"]))
        if a["label_before"] is None or node_i is None:
            # writing "" where the machine returned no label would CHANGE the label, not rewrite it.
            a["returned_uid"] = None
            a["error_verbatim"] = ""
            a["skipped"] = ("NOT ATTEMPTED: node_labels returned label %r for Nodes[%r], and writing an "
                            "empty string would be a CHANGE, not a rewrite"
                            % (a["label_before"], node_i))
            fact("ARM C %s" % a["skipped"])
        else:
            try:
                a["returned_uid"] = g.set_node_label(ARMC_SCRATCH, rec["d639"], node_i, a["label_before"])
                a["error_verbatim"] = ""
            except Exception as e:                                                 # noqa: BLE001
                a["returned_uid"] = None
                a["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        a["node_census_after"] = g.count(ARMC_SCRATCH, "Node")
        a["wire_census_after"] = g.count(ARMC_SCRATCH, "Wire")
        a["exec_state_after"] = read_es("[ARM C] immediately AFTER set_node_label", ARMC_SCRATCH, "ARMC")
        try:
            rows = g.node_labels(ARMC_SCRATCH, int(rec["d639"]))
            a["label_after"] = next((r["label"] for r in rows if r["uid"] == SRC_UID), None)
        except Exception as e:                                                     # noqa: BLE001
            a["label_after"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        fact("ARM C: ExecState %r -> %r ; Node %r -> %r ; Wire %r -> %r ; label %r -> %r ; error %r"
             % (a.get("exec_state_before"), a.get("exec_state_after"), a.get("node_census_before"),
                a.get("node_census_after"), a.get("wire_census_before"), a.get("wire_census_after"),
                a.get("label_before"), a.get("label_after"), a.get("error_verbatim")))
        gate("P_m ARM C ran and its censuses are recorded (NO ExecState value is asserted)", True,
             "ExecState %r -> %r ; Node %r -> %r (the op's junk Invoke is expected) ; Wire %r -> %r"
             % (a.get("exec_state_before"), a.get("exec_state_after"), a.get("node_census_before"),
                a.get("node_census_after"), a.get("wire_census_before"), a.get("wire_census_after")))
    finally:
        a["scratch_exists"] = _drop_scratch(ARMC_SCRATCH, "ARM C")
        gate("Z_3d the ARM C scratch is deleted in the same run", not a["scratch_exists"], ARMC_SCRATCH)


# ===================================================================================== main
def main():
    print("=== diag_c64_perturb_t1t3  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 64 material #1: does OpConnectNested_v1 PERTURB THE READING or REALLY BREAK THE VI?",
          flush=True)
    print("=== THE SAVE LEG IS DROPPED (judgement, cycle 64): no save(), no allow_broken, no gui_save, no "
          "write of any VI file, no GUI action. Nothing is built and no route is chosen.", flush=True)
    print("=== ARMS B and C are the discriminating test named by archive/peer/2026-09-21-c64-astgate3.md "
          "(claude/hypothesis, ANSWERED): both run UNCONDITIONALLY, on their own throwaway scratches, "
          "through verbs that already exist - no new op, no save, no edit to tools/gscript.py.", flush=True)

    t0_leftover()                    # files only
    t3_census()                      # files only - runs before any COM call
    dump()

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    R["ref_counts_before"] = g.ref_counts()
    fact("tracked VI Server refs BEFORE: %r" % (R["ref_counts_before"],))

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
        arm_b()
    finally:
        dump()
    try:
        arm_c()
    finally:
        dump()

    R["ref_counts"] = g.ref_counts()
    fact("tracked VI Server refs AFTER: %r" % (R["ref_counts"],))
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
    left = [p for p in SCRATCHES if os.path.exists(p)]
    gate("Z_1e EVERY scratch is gone (nothing is left on disk by this run)",
         not left and not globmod.glob(C63_LEFTOVER_GLOB),
         "still on disk: %r ; c63 leftovers: %r"
         % ([os.path.basename(p) for p in left], globmod.glob(C63_LEFTOVER_GLOB)))

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
