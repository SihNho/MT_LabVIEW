"""diag_c64_connect_v2 - cycle 64 material #2. Build OpConnectNested_v2 ADDITIVELY on the donor
OpConnectNested_v1, with the embedded `Wire.Is Broken?` readback REMOVED, then run the PAIRED
v2-vs-v1 discriminating test in ONE LabVIEW session.

THE DECISION BEING EXECUTED (judgement, cycle 64; the route is NOT re-chosen here)
  docs/cycle27-plan.md Pre-decided 53(d7) named two branches. The save-bypass branch is REJECTED (it would
  need a `gui_save` GUI exception on every S3b row, for ever). The other branch is taken: v2 = the byte-copy
  of v1 with the property node(s) that read `Wire.Is Broken?` 6371004 DELETED - donor rule 51(h), the shipped
  precedent being OpCreateLocalRead_v0 on OpCreateLocal_v0. Dispatch #1 measured WHY: OpConnectNested_v1,
  OpConnect2_v0 and OpSetLabel_v0 all carry that reader by inheritance from OpNetInfo_v1
  (tools/recipes/build_opnetinfo.py:151), i.e. every op that can address a NESTED diagram, and
  docs/NAMES.md:912-929 records that such a read perturbs `ExecState`.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line - CLAUDE.md "before creating any new op,
tool or recipe": `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`, docs/toolkit-capabilities.md)
  tools/bench/diag_c64_perturb_t1t3.py        dispatch #1: the gate/fact/dump/read_es/_fresh_bed/_drop_scratch
                                              harness and the md5-pin block are carried over in shape.
  tools/bench/diag_s58_boolwire.py:456        `delete_by_uid` - the cycle-58 lesson (resolve the uid to its
                                              Traverse index over the SAME class list the census used).
  tools/bench/diag_c61_localdir_write.py:387  the `VI Server:VI` property `242` read-mode regression probe
                                              (`one_probe`/`delete_probe`), re-used in shape for gate C2.
  tools/recipes/build_opconnectnested_v1.py   `connect_nested_v1` - the DONOR's wrapper. NOT edited, NOT
                                              rebuilt, and the donor .vi is gated byte-unchanged either side.
  tools/gscript.py                            op :210 / vi_ref :244 / reset :262 / _run :341 / _err :435 /
                                              report_all :488 / node_labels :587 / panel_wiring :826 /
                                              node_terms :870 / node_terms_uid :925 / count :1005 /
                                              uids :1017 / open_panel :1241 / close_panel :1257 /
                                              ensure_loaded :1268 / exec_state :1977 / save :2062 /
                                              build_property :2194 / delete_object :2275 /
                                              connect_terminals :2445 / fp_labels :2475 - ALL ALREADY EXIST.
  THE ONE ADDITION, authorised by the brief: `connect_nested_v2` appended to tools/gscript.py, mirroring
  `connect_nested_v1` exactly but for the VI name and the removed readback outputs. NO EXISTING FUNCTION IN
  tools/gscript.py IS MODIFIED - proved mechanically by gate C1 (`git diff --numstat` deletions == 0).
  IS THERE ALREADY A GENERIC PATH that invokes an arbitrary op VI by path with named controls/indicators?
  Reported by gate C0 off the file itself: `g.op(path)` (:210) + `g._run(vi)` (:341) + `g._err(vi, name)`
  (:435) ARE that generic trio and every wrapper here is built from them, but there is NO single named
  wrapper taking (path, **named controls) - so the brief's additive `connect_nested_v2` is what is used.

STAGES - each stage leaves a FILE or a reading, in this order (user rule 2026-09-19, split + save):
  A  (files only, no LabVIEW)  md5 pins; C0/C1 gscript reports; static-gate evidence.
  B  (LabVIEW session 1, after a pre-batch restart 44(e))
     B1 FILE-COPY claudeDev\OpConnectNested_v1.vi -> claudeDev\OpConnectNested_v2.vi; donor gated byte-
        unchanged BEFORE and AFTER.
     B2 CENSUS v2's own TOP-LEVEL diagram: every node with class/label/uid and the full terminal+wire table
        of the property nodes that read `Wire` off the sink-terminal reference and then `UID` / `Is Broken?`.
     B3 DELETE those property nodes - WIRES FIRST, BY UID, THEN THE NODE BY UID (cycle 58's lesson), under a
        SAFETY RULE FIXED BEFORE THE RUN (see P_c3): a wire is deletable only if every terminal on it either
        belongs to a node being deleted, or is a SOURCE terminal on a node that stays, or is a SINK terminal
        on a ControlTerminal that stays (an unwired indicator is legal), or is an ERROR-IN sink on a node
        that stays (never a REQUIRED input - it carries a no-error default - and B4 re-wires it anyway).
        A node is deletable only if every wire touching it is deletable. A node that fails the rule is KEPT
        and REPORTED - it is not forced. Run 1's census (12:39) shows why this matters: the reader #242's
        `reference` comes from #241's `Wire` output, but #241's OWN `reference` (w572) is SHARED with the
        `Terminal.Connect Wire` Invoke #757, so #241 cannot be removed without touching a wire the op needs.
     B4 THE ERROR CHAIN MUST SURVIVE. The error-in source and error-out sinks of every deleted node are
        recorded BEFORE the delete; afterwards every ERROR-IN sink the deleted node used to feed is re-wired
        from that recorded upstream error SOURCE with `connect_terminals` (reader-free, top level) - for
        #242 that is #241's `error out` straight into `Clear Errors.vi` #399's `error in (no error)`. The
        `error out` INDICATOR's panel wiring is measured on the donor AND on v2 and gated for no regression.
     B5 ExecState, then SAVE claudeDev\OpConnectNested_v2.vi; md5 + size recorded.  <- THE ARTEFACT
  C  (LabVIEW session 2, after a SECOND restart) COLD-open v2: ExecState 1 is the artefact's pass criterion;
     md5 re-read. Then C2, the `VI Server:VI` 242 read-mode build_property regression on its own scratch.
  D  (the SAME session 2) THE PAIRED DISCRIMINATING TEST, two independent scratch duplicates of
     claudeDev\D1_s3a_focus_ind.vi (md5 eef91c1d..., FATAL pin, NEVER written), both deleted in the same run:
       ARM V2  cold ExecState -> ONE idempotent connect through v2 (46,24,0,46,25,0) -> wire_delta, Wire
               census either side, the op's error cluster, ExecState immediately after + three re-reads ~2 s
               apart.
       ARM V1  the IDENTICAL sequence through v1 on the second scratch, in the SAME session, so the
               comparison is PAIRED and not cross-session.
     NEITHER ARM SAVES ANYTHING. No value is asserted for either arm's ExecState: both outcomes are results.
  E  (the same session) the BAD-CALL gate: v2 called with a nonexistent node index on its own scratch; the
     `error out` cluster is read RAW off the op and must be NON-EMPTY. An op that has gone silent about
     errors is a FAIL, not a pass.
  Z  closing md5 pins, scratch existence, ref accounting, handles, the full ExecState timeline.

PREDICTION CONTRACT (a gate that asserts no value says so explicitly)
  P_a   the four md5 pins hold BEFORE: ORIGINAL 2a78e17c..., D1_s1_copy 3e3d23ce..., D1_s2_loops 6ff19497...,
        D1_s3a_focus_ind eef91c1d...; donor OpConnectNested_v1 b7a1bb56... and OpCreateLocalRead_v0
        f695d97a... byte-unchanged
  C_0   the generic-op-path question is ANSWERED off tools/gscript.py itself (NONE FOUND is acceptable)
  C_1   `git diff --numstat tools/gscript.py` shows ZERO deleted lines - the change is purely additive
  C_1b  the HEAD copy of gscript.py is actually READ (run 1's `git show HEAD:tools/gscript.py` came back
        EMPTY - the pathspec is resolved against the GIT ROOT, not this directory - so every def looked
        "added"; it is now `HEAD:./tools/gscript.py` and the def count at HEAD is itself gated), and
  C_1b2 every `def` name present at HEAD is still present now, plus exactly `connect_nested_v2`
  C_2   the shipped-path regression build_property('VI Server:VI', [('242', False)]) still creates a node
        whose i=4 row is a SOURCE, and the probe deletes again leaving the Property census where it was
  P_b   v2 is a byte-identical FILE COPY of v1 at creation (md5 equal), and the donor is unchanged after
  P_c   the census finds AT LEAST ONE property node carrying the `Wire.Is Broken?` ITEM terminal. Its short
        name on the node is `Broken?` - MEASURED off the machine in run 1 (12:39); `Is Broken?` is the PANEL
        INDICATOR's label, and run 1 matched on that and found 0 nodes. All spellings are accepted now. If
        the census still finds none, the run STOPS that leg and reports it - nothing is deleted on a guess
  P_c3  every delete obeys the safety rule above; a node that fails it is KEPT and named. NO VALUE ASSERTED
        about how many nodes end up deletable
  P_d   AFTER the deletes, NO node on v2's top-level diagram carries the `Wire.Is Broken?` item terminal -
        this is the acceptance criterion for "the readback is removed"
  P_e   every ERROR-IN sink a deleted node used to feed is WIRED again from the recorded upstream source
  P_e2  v2's `error out` panel terminal is WIRED, and P_e3 that it is UNCHANGED from the donor's reading -
        the donor's own value is measured in the same run, so an inherited 0 is not mistaken for a loss
  P_f   v2's ExecState is 1 at the save, and `g.save` (which REFUSES a broken VI, gscript.py:2071) returns a
        size - no `allow_broken`, no `gui_save`
  P_g   v2 REOPENS COLD at ExecState 1 in a freshly restarted LabVIEW  <- the artefact's pass criterion
  P_h   ARM V2: both nodes echo their own uid on Diagram #639; wire_delta == 0 and the Wire census is
        unchanged. The ExecState readings are RECORDED; NO VALUE IS ASSERTED
  P_i   ARM V1: the identical sequence, same session. RECORDED; NO VALUE IS ASSERTED
  P_j   THE BAD CALL through v2 returns a NON-EMPTY error cluster read RAW off the op's `error out`
  Z_*   four md5 pins hold AFTER; donor + OpCreateLocalRead_v0 byte-unchanged; EVERY scratch exists=False;
        refs opened == closed == 0 live; handles either side

WHAT THIS IS NOT
  No `allow_broken`, no `gui_save`, no GUI action of any kind, no edit to any file under claudeDev other than
  CREATING OpConnectNested_v2.vi, no change to any existing tools/gscript.py function, no cast, no splice
  (51(h)), no recipe, nothing written under tools/recipes/, no VI run of any D1 artefact or of the main VI
  (34(f) - op VIs are run, the fleet's normal mechanism), no motor / ASI / camera (rig ASSEMBLED), no new
  process device. remove_bad_wires_scripted / remove_bad_wires / move_in are neither imported nor called.
  retrospective.py / audit_cycle.py / violations.py / doc_ingest.py / prior_art_review.py are NOT run (54(a)).
  docs/cycle27-plan.md and STATUS.md `## NEXT` are NOT edited. No route is chosen and none is recommended.
"""
import json
import os
import shutil
import subprocess
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
GSCRIPT_PY = os.path.join(ROOT, "tools", "gscript.py")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
LOCALREAD = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
LOCALREAD_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
DONOR = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
DONOR_MD5 = "b7a1bb56cefe2b4632125e6bda0d7221"
OP2 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v2.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c64_connect_v2.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
V2_LABELS_PATH = os.path.join(BENCH, "opconnectnested_v2_labels.json")
V2_LABELS = dict(V1_LABELS)
V2_LABELS["route"] = "A-cross-diagram (v2: the Wire.Is Broken? readback deleted)"

ARMV2_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64V2_%s.vi" % STAMP)
ARMV1_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64V1_%s.vi" % STAMP)
REG_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64REG_%s.vi" % STAMP)
BAD_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64BAD_%s.vi" % STAMP)
SCRATCHES = (ARMV2_SCRATCH, ARMV1_SCRATCH, REG_SCRATCH, BAD_SCRATCH)

CASE_UID, SRC_UID, D639 = 10407, 10686, 639
BRIEF_SINK_NODE, BRIEF_SRC_NODE = 24, 25
STANDARD_TERMS = ("reference", "reference out", "error in (no error)", "error out")
ERR_IN_NAME, ERR_OUT_NAME = "error in (no error)", "error out"
ERR_IN_ALIASES = ("error in (no error)", "error in")
# MEASURED 2026-09-21 12:39 off the machine (tools/bench/diag_c64_connect_v2.log, run 1's B2 census): the
# PROPERTY ITEM's short name on the node is `Broken?`; `Is Broken?` is the PANEL INDICATOR's label. Run 1
# selected on the panel label and found 0 nodes. All three spellings are accepted here.
BROKEN_NAMES = ("Broken?", "Is Broken?", "IsBroken")
SCAN_LIMIT = 140
REG_POS = (7200, 5600)
VI_CLASS, PROP_VI_242 = "VI Server:VI", "242"

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": ("cycle 64 material #2: build OpConnectNested_v2 (v1 minus the embedded Wire.Is Broken? "
              "readback) and run the PAIRED v2-vs-v1 test in ONE LabVIEW session"),
     "route_is_judgements": "Pre-decided 53(d7), donor rule 51(h); this file executes it, it does not re-choose it",
     "no_allow_broken": True, "no_gui_save": True, "no_gui_action": True, "no_recipe": True,
     "no_new_device": True, "no_cast": True, "no_splice": True,
     "gscript_change": "ADDITIVE ONLY: one new function connect_nested_v2; gate C_1 proves 0 deleted lines",
     "claudedev_writes": "OpConnectNested_v2.vi is CREATED; no other file under claudeDev is written",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "move_in": "not imported, not called",
     "handles": {}, "hash_probe": [], "exec_state_timeline": [],
     "stage_a": {}, "stage_b": {}, "stage_c": {}, "stage_d": {}, "stage_e": {},
     "peer_a": ("tools/bench/peer_c64_execstate_recompile.log - ANSWERED, REPORTED ONLY; "
                "NOTHING IN THIS FILE IS BUILT AGAINST IT")}


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


def read_es(tag, target, leg):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:140])
    row = {"step": len(R["exec_state_timeline"]) + 1, "leg": leg, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s | %s] = %r   (+%.1f s)" % (row["step"], leg, tag, es, row["t_since_start_s"]))
    return es


# ===================================================================================== census helpers
def term_rows(rows):
    return [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]} for t in rows]


def class_map(target):
    """uid -> Traverse class, for the classes that matter on an op's top-level diagram."""
    out = {}
    for cls in ("Property", "Invoke", "ControlTerminal", "SubVI"):
        try:
            for o in g.report_all(target, cls):
                out[o["uid"]] = cls
        except Exception as e:                                                     # noqa: BLE001
            fact("class_map(%s) raised %s: %s" % (cls, type(e).__name__, str(e)[:120]))
    return out


def census0(target, tag):
    """Every node on the TOP-LEVEL diagram (Traverse Diagram index 0) with class, label, uid echo and its
    full terminal+wire table. Junk-free: node_labels and node_terms both come from creator-deleted ops."""
    try:
        labels = g.node_labels(target, 0)
    except Exception as e:                                                         # noqa: BLE001
        fact("%s: node_labels(0) raised %s: %s" % (tag, type(e).__name__, str(e)[:200]))
        labels = []
    cm = class_map(target)
    nodes = []
    for n, r in enumerate(labels[:SCAN_LIMIT]):
        rec = {"n": n, "uid": r["uid"], "label": r["label"], "class": cm.get(r["uid"], "?")}
        try:
            echo, rows = g.node_terms_uid(target, 0, n)
            rec["uid_echo"] = echo
            rec["terms"] = term_rows(rows) if echo == r["uid"] else []
            rec["echo_ok"] = (echo == r["uid"])
        except Exception as e:                                                     # noqa: BLE001
            rec["uid_echo"], rec["terms"], rec["echo_ok"] = None, [], False
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
        nodes.append(rec)
    nets = {}
    for rec in nodes:
        for t in rec["terms"]:
            if t["wire"]:
                nets.setdefault(t["wire"], []).append(
                    {"n": rec["n"], "uid": rec["uid"], "class": rec["class"], "t": t["i"],
                     "name": t["name"], "is_source": t["is_source"]})
    # CONTROL TERMINALS ARE NOT IN Diagram.Nodes[] - measured in run 1: node_labels returned 21 rows while
    # count('ControlTerminal') was 20 and none of the 21 was one (diag_c64_connect_v2.log:51-72). The
    # hypothesis peer's 3 (archive/peer/2026-09-21-c64-v2-run1.md) named the consequence: without them the
    # safety rule cannot see the FAR END of a wire that branches onto a panel indicator, so clause (c) was
    # dead code and a lost `error out` branch would be invisible. panel_wiring (gscript.py:826) reads every
    # top-level panel object's diagram terminal in ONE op run; its rows are folded into the net map here.
    panel_rows = []
    try:
        panel_rows = g.panel_wiring(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("%s: panel_wiring raised %s: %s" % (tag, type(e).__name__, str(e)[:200]))
    for p in panel_rows:
        if p.get("wire"):
            nets.setdefault(p["wire"], []).append(
                {"n": None, "uid": p["uid"], "class": "ControlTerminal", "t": 0,
                 "name": p["label"], "is_source": p["is_source"], "panel": True,
                 "indicator": p["indicator"]})
    echo_bad = [(r["n"], r["uid"], r.get("uid_echo")) for r in nodes if not r.get("echo_ok")]
    fact("%s: %d node(s) on the top-level diagram + %d wired panel terminal(s), %d distinct wire(s); "
         "uid-echo failures %r" % (tag, len(nodes), sum(1 for p in panel_rows if p.get("wire")), len(nets),
                                   echo_bad))
    return nodes, nets, echo_bad


def node_by_uid(nodes, uid):
    return next((x for x in nodes if x["uid"] == uid), None)


def delete_by_uid(tag, target, cls, uid):
    """delete_object(target, cls, index, verify=True) - gscript.py:2275 - addresses by (class, Traverse
    index), so the uid is resolved over the SAME class list the census used (diag_s58_boolwire.py:456)."""
    rd = {"tag": tag, "class": cls, "uid": uid}
    try:
        cur = [o["uid"] for o in g.report_all(target, cls)]
        rd["members"], rd["index"] = len(cur), cur.index(uid)
    except Exception as e:                                                         # noqa: BLE001
        rd["index"], rd["error_verbatim"] = None, "index resolution failed %s: %s" % (type(e).__name__,
                                                                                      str(e)[:250])
        R["stage_b"].setdefault("deletes", []).append(rd)
        fact("%s: could NOT resolve #%r to a %s index - %s" % (tag, uid, cls, rd["error_verbatim"]))
        return rd
    try:
        gone = g.delete_object(target, cls, rd["index"])
        rd["gone"], rd["error_verbatim"] = (sorted(gone) if gone else gone), ""
    except Exception as e:                                                         # noqa: BLE001
        rd["gone"], rd["error_verbatim"] = None, "%s: %s" % (type(e).__name__, str(e)[:400])
    R["stage_b"].setdefault("deletes", []).append(rd)
    fact("%s: delete_object(%r, %r) uid #%r of %r -> gone %r ; error VERBATIM %r"
         % (tag, cls, rd["index"], uid, rd.get("members"), rd.get("gone"), rd["error_verbatim"]))
    return rd


def wire_is_deletable(net_terms, doomed_uids):
    """THE SAFETY RULE, fixed before the run. A wire may be deleted only if every terminal on it either
    (a) belongs to a node being deleted, or (b) is a SOURCE terminal on a node that stays (its output simply
    goes unwired - legal), or (c) is a SINK terminal on a ControlTerminal that stays (an unwired indicator is
    legal), or (d) is an ERROR-IN sink on a node that stays - an error-in terminal is never a REQUIRED input,
    it carries a no-error default, so leaving it bare cannot break the VI; and B4 re-wires the deleted node's
    recorded UPSTREAM error source into it anyway, so the chain survives rather than merely being legal.
    Anything else - e.g. the Invoke's `reference` SINK - means the wire feeds something that still needs it.

    Returns (ok, why, repairs) where `repairs` names the (d) sinks the error chain must be re-wired into.
    """
    why, repairs = [], []
    for t in net_terms:
        if t["uid"] in doomed_uids:
            why.append("t%d %r on #%d (DOOMED)" % (t["t"], t["name"], t["uid"]))
        elif t["is_source"]:
            why.append("t%d %r on #%d (SOURCE that stays - output goes unwired)" % (t["t"], t["name"], t["uid"]))
        elif t["class"] == "ControlTerminal":
            why.append("t%d %r on #%d (ControlTerminal SINK that stays - unwired indicator is legal)"
                       % (t["t"], t["name"], t["uid"]))
        elif t["name"] in ERR_IN_ALIASES:
            why.append("t%d %r on #%d (ERROR-IN sink that stays - defaults to no-error; B4 re-wires it)"
                       % (t["t"], t["name"], t["uid"]))
            repairs.append(t)
        else:
            return (False, "REFUSED: t%d %r is a SINK on #%d (%s) which STAYS and still needs this wire" % (
                t["t"], t["name"], t["uid"], t["class"]), [])
    return True, " ; ".join(why), repairs


# ===================================================================================== STAGE A
def stage_a():
    print("\n=== STAGE A  files only - md5 pins, the gscript reports (no LabVIEW, no COM)", flush=True)
    K = R["stage_a"]
    o = probe("A0 ORIGINAL (read-only probe)", ORIGINAL)
    gate("P_a ORIGINAL md5 == %s" % ORIG_MD5, o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("A0b D1_s1_copy.vi", S1_ARTEFACT)
    gate("P_a2 D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("A0c D1_s2_loops.vi", S2_ARTEFACT)
    gate("P_a3 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("A0d D1_s3a_focus_ind.vi (the bed, NEVER written)", S3A_ARTEFACT)
    gate("P_a4 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    lr = probe("A0e OpCreateLocalRead_v0.vi", LOCALREAD)
    gate("P_a5 OpCreateLocalRead_v0.vi md5 == %s" % LOCALREAD_MD5, lr.get("md5") == LOCALREAD_MD5,
         lr.get("md5", "?"))
    dn = probe("A0f THE DONOR OpConnectNested_v1.vi", DONOR)
    gate("P_a6 the donor OpConnectNested_v1.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5,
         dn.get("md5", "?"), fatal=True)
    K["donor_md5_before"] = dn.get("md5")
    K["donor_size"] = dn.get("size")

    # ---- C0: is there ALREADY a generic op-invoker in tools/gscript.py?
    src = open(GSCRIPT_PY, encoding="utf-8").read()
    lines = src.splitlines()
    generic = [(i + 1, ln.strip()) for i, ln in enumerate(lines)
               if ln.startswith("def op(") or ln.startswith("def _run(") or ln.startswith("def _err(")]
    kwargs_wrappers = [(i + 1, ln.strip()) for i, ln in enumerate(lines)
                       if ln.startswith("def ") and "**controls" in ln]
    K["generic_op_path"] = {"primitives": generic, "kwargs_wrappers": kwargs_wrappers}
    fact("C0 the generic trio in tools/gscript.py: %r" % (generic,))
    fact("C0 wrappers taking **controls (a partial generic path, each bound to ONE op VI): %r"
         % (kwargs_wrappers,))
    fact("C0 VERDICT: there is NO single named function taking (arbitrary op VI path, **named controls). "
         "`g.op(path)` + `g._run(vi)` + `g._err(vi, name)` ARE the generic trio and every wrapper is built "
         "from them, but each wrapper hard-codes its own op path - so the brief's ONE ADDITIVE function "
         "`connect_nested_v2` is what this run uses.")
    gate("C_0 the generic-op-path question is answered off tools/gscript.py itself", bool(generic),
         "op/_run/_err at %r" % ([n for n, _l in generic],))

    # ---- C1: the gscript change is purely ADDITIVE
    try:
        # encoding="utf-8" IS LOad-BEARING - see the C1b comment below. Every text=True subprocess call in
        # this fleet decodes with the Windows locale codec (cp949 here) and returns stdout=None at the first
        # unmappable byte, silently.
        ns = subprocess.run(["git", "diff", "--numstat", "--", "tools/gscript.py"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        K["git_numstat"] = (ns.stdout or "").strip()
        st = subprocess.run(["git", "status", "--porcelain", "--", "tools/gscript.py"], cwd=ROOT,
                            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
        K["git_status_porcelain"] = (st.stdout or "").strip()
        fact("C1 git status --porcelain tools/gscript.py -> %r (a leading ' M' means the change is UNSTAGED, "
             "so `git diff --numstat` with no ref does compare against HEAD)" % (K["git_status_porcelain"],))
        parts = (K["git_numstat"].split("\t") if K["git_numstat"] else [])
        added = int(parts[0]) if len(parts) > 2 and parts[0].isdigit() else None
        deleted = int(parts[1]) if len(parts) > 2 and parts[1].isdigit() else None
    except Exception as e:                                                         # noqa: BLE001
        K["git_numstat"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        added = deleted = None
    K["gscript_added"], K["gscript_deleted"] = added, deleted
    fact("C1 git diff --numstat tools/gscript.py -> %r (added %r, deleted %r)"
         % (K["git_numstat"], added, deleted))
    gate("C_1 the tools/gscript.py change deletes ZERO lines (purely additive)", deleted == 0,
         "added %r / deleted %r" % (added, deleted))

    try:
        # THE ACTUAL CAUSE OF RUN 1's C_1b FAILURE, found by the hypothesis peer
        # (archive/peer/2026-09-21-c64-v2-run1.md, its 1) and NOT by me: `git show` DID resolve and emit the
        # file - the log carries `UnicodeDecodeError: 'cp949' codec can't decode byte 0xe2 in position
        # 12250` from subprocess's reader THREAD (diag_c64_connect_v2.log:25-33). CPython on Windows
        # (subprocess.py:1506-1548) appends nothing when that thread raises and then returns stdout=None -
        # no exception reaches the caller. `text=True` with no `encoding=` decodes with the locale codec
        # (cp949 here) while tools/gscript.py is UTF-8. My own diagnosis ("the pathspec is resolved against
        # the git root") was WRONG; the pathspec change is kept because it is harmless and correct, but
        # `encoding="utf-8", errors="replace"` is the fix. rc/stderr/bytes are recorded either way.
        head = subprocess.run(["git", "show", "HEAD:./tools/gscript.py"], cwd=ROOT,
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              timeout=120)
        K["git_show_rc"] = head.returncode
        K["git_show_stderr"] = (head.stderr or "").strip()[:300]
        K["git_show_bytes"] = len(head.stdout or "")
        import re as _re
        old_defs = set(_re.findall(r"^\s*def\s+(\w+)", head.stdout or "", _re.M))
        new_defs = set(_re.findall(r"^\s*def\s+(\w+)", src, _re.M))
        K["defs_at_head"] = len(old_defs)
        K["defs_lost"] = sorted(old_defs - new_defs)
        K["defs_added"] = sorted(new_defs - old_defs)
        fact("C1b git show HEAD:./tools/gscript.py -> rc %r, %r bytes, %d defs at HEAD ; stderr %r"
             % (K["git_show_rc"], K["git_show_bytes"], K["defs_at_head"], K["git_show_stderr"]))
    except Exception as e:                                                         # noqa: BLE001
        K["defs_lost"], K["defs_added"] = ["ERROR %s" % type(e).__name__], []
    fact("C1b defs lost %r ; defs added %r" % (K["defs_lost"], K["defs_added"]))
    gate("C_1b the HEAD copy of tools/gscript.py was actually READ (an empty read would make every def look "
         "'added' - run 1's failure)", K.get("defs_at_head", 0) > 50,
         "%r defs at HEAD, rc %r, %r bytes" % (K.get("defs_at_head"), K.get("git_show_rc"),
                                               K.get("git_show_bytes")))
    gate("C_1b2 no existing def was removed, and exactly `connect_nested_v2` was added",
         K["defs_lost"] == [] and K["defs_added"] == ["connect_nested_v2"],
         "lost %r added %r" % (K["defs_lost"], K["defs_added"]))
    gate("C_1c tools/gscript.py has the new verb importable", hasattr(g, "connect_nested_v2"),
         "hasattr(g,'connect_nested_v2')=%r" % hasattr(g, "connect_nested_v2"))

    with open(V2_LABELS_PATH, "w", encoding="utf-8") as f:
        json.dump(V2_LABELS, f, indent=1)
    fact("C1d v2 control-label map written -> %s (v2 is a FILE COPY of v1, so the panel is unchanged)"
         % os.path.relpath(V2_LABELS_PATH, ROOT).replace("\\", "/"))
    dump()


# ===================================================================================== STAGE B
def stage_b():
    print("\n=== STAGE B  build OpConnectNested_v2 on the donor - copy, census, delete, error chain, SAVE",
          flush=True)
    K = R["stage_b"]

    # ---- B1 file copy
    if os.path.exists(OP2):
        fact("B1 a previous OpConnectNested_v2.vi exists (%r) - it is REMOVED so the copy is from the donor"
             % HASH(OP2))
        try:
            g.close_panel(OP2)
        except Exception:                                                          # noqa: BLE001
            pass
        os.remove(OP2)
    shutil.copyfile(DONOR, OP2)
    time.sleep(0.4)
    c = probe("B1 OpConnectNested_v2.vi immediately after the FILE COPY", OP2)
    K["v2_md5_at_copy"] = c.get("md5")
    gate("P_b v2 is a byte-identical FILE COPY of the donor at creation", c.get("md5") == DONOR_MD5,
         "%r vs donor %r" % (c.get("md5"), DONOR_MD5), fatal=True)
    d2 = probe("B1b the donor, right after the copy", DONOR)
    gate("P_b2 the donor is byte-unchanged by the copy", d2.get("md5") == DONOR_MD5, d2.get("md5", "?"))

    g.open_panel(OP2)          # the skill's rule: open the panel before editing
    time.sleep(1.0)
    es = read_es("[B2] v2 as copied, before any edit", OP2, "B")
    K["exec_state_as_copied"] = es
    gate("P_b3 v2 opens at ExecState 1 before any edit", es == 1, "%r" % (es,), fatal=True)

    # ---- B2 census
    nodes, nets, echo_bad = census0(OP2, "B2 v2 top-level census (BEFORE)")
    K["census_before"] = nodes
    K["echo_failures_before"] = echo_bad
    gate("P_c0 EVERY node in the BEFORE census echoed its own uid (a node whose echo fails contributes zero "
         "terminals and is indistinguishable from one that has none - the peer's 5)", not echo_bad,
         "%r" % (echo_bad,), fatal=True)
    K["nets_before"] = {str(k): v for k, v in nets.items()}
    K["counts_before"] = {c2: g.count(OP2, c2) for c2 in ("Node", "Wire", "Property", "Invoke",
                                                          "ControlTerminal")}
    fact("B2 counts BEFORE: %r" % (K["counts_before"],))
    for rec in nodes:
        print(("    [%02d] #%-6d %-16s %-22r %r"
               % (rec["n"], rec["uid"], rec["class"], rec["label"],
                  [(t["i"], t["name"], "SRC" if t["is_source"] else "snk", t["wire"])
                   for t in rec["terms"]])).encode("ascii", "replace").decode("ascii"), flush=True)

    pn_broken = [r for r in nodes if any(t["name"] in BROKEN_NAMES for t in r["terms"])]
    K["is_broken_nodes"] = [{"n": r["n"], "uid": r["uid"], "class": r["class"], "label": r["label"],
                             "terms": r["terms"]} for r in pn_broken]
    fact("B2 node(s) carrying a Wire.Is Broken? item terminal %r: %r"
         % (list(BROKEN_NAMES), [(r["n"], r["uid"], r["class"]) for r in pn_broken],))
    gate("P_c the census finds at least one node carrying the Wire.Is Broken? item terminal",
         bool(pn_broken), "%d found" % len(pn_broken), fatal=True)

    # the PN that reads `Wire` off the sink-terminal reference, feeding the Is Broken? reader's `reference`
    feeders = []
    for b in pn_broken:
        ref_w = next((t["wire"] for t in b["terms"] if t["name"] == "reference"), 0)
        if not ref_w:
            continue
        for t in nets.get(ref_w, []):
            if t["is_source"] and t["uid"] != b["uid"]:
                src_node = node_by_uid(nodes, t["uid"])
                feeders.append({"feeder_uid": t["uid"], "feeder_n": t["n"], "feeder_class": t["class"],
                                "feeder_term": t["name"], "wire": ref_w, "feeds_uid": b["uid"],
                                "feeder_terms": (src_node or {}).get("terms", [])})
    K["reference_feeders"] = feeders
    fact("B2 the `reference` feeders of the Is Broken? reader(s): %r"
         % ([(f["feeder_uid"], f["feeder_class"], f["feeder_term"], "w%d" % f["wire"]) for f in feeders],))

    # ---- record the error chain BEFORE anything is deleted
    doomed = [r["uid"] for r in pn_broken] + [f["feeder_uid"] for f in feeders
                                              if f["feeder_class"] == "Property"]
    doomed = sorted(set(doomed))
    K["doomed_candidates"] = doomed
    chain = []
    for uid in doomed:
        rec = node_by_uid(nodes, uid)
        ein = next((t for t in rec["terms"] if t["name"] == ERR_IN_NAME), None)
        eout = next((t for t in rec["terms"] if t["name"] == ERR_OUT_NAME), None)
        up = None
        if ein and ein["wire"]:
            up = next((t for t in nets.get(ein["wire"], []) if t["is_source"] and t["uid"] != uid), None)
        downs = []
        if eout and eout["wire"]:
            downs = [t for t in nets.get(eout["wire"], []) if not t["is_source"] and t["uid"] != uid]
        chain.append({"uid": uid, "error_in_wire": (ein or {}).get("wire", 0),
                      "error_out_wire": (eout or {}).get("wire", 0),
                      "upstream_source": up, "downstream_sinks": downs})
    K["error_chain_before"] = chain
    fact("B2 error chain of the doomed nodes BEFORE the delete: %r" % (chain,))

    pw_before = g.panel_wiring(OP2)
    eo_before = next((r for r in pw_before if r["label"] == ERR_OUT_NAME and r["indicator"]), None)
    K["error_out_panel_before"] = eo_before
    fact("B2 the `error out` INDICATOR before the delete: %r" % (eo_before,))
    # its diagram node: the node whose terminal table is a single SINK named `error out`
    eo_node_before = next((r for r in nodes if eo_before and r["class"] == "ControlTerminal"
                           and len(r["terms"]) == 1 and r["terms"][0]["name"] == ERR_OUT_NAME
                           and r["terms"][0]["wire"] == eo_before["wire"]), None)
    K["error_out_diagram_node_before"] = eo_node_before
    fact("B2 the `error out` indicator's DIAGRAM node: %r"
         % ({"n": eo_node_before["n"], "uid": eo_node_before["uid"]} if eo_node_before else None))

    # ---- B3 delete, wires first, BY UID, under the safety rule
    deleted_nodes, kept_nodes, repairs_due = [], [], []
    for uid in sorted(doomed, key=lambda u: 0 if any(t["name"] in BROKEN_NAMES
                                                     for t in node_by_uid(nodes, u)["terms"]) else 1):
        live_nodes, live_nets, live_echo = census0(OP2, "B3 census before deleting #%d" % uid)
        if live_echo:
            kept_nodes.append({"uid": uid, "why": "uid-echo failures in the live census %r" % (live_echo,)})
            gate("P_c3z node #%d is NOT deleted: the live census had uid-echo failures, so its wire table "
                 "cannot be trusted" % uid, False, "%r" % (live_echo,))
            continue
        rec = node_by_uid(live_nodes, uid)
        if rec is None:
            kept_nodes.append({"uid": uid, "why": "no longer on the diagram"})
            continue
        doomed_now = {uid}
        plan, refusal, reps = [], None, []
        for t in rec["terms"]:
            if not t["wire"]:
                continue
            ok, why, rep = wire_is_deletable(live_nets.get(t["wire"], []), doomed_now)
            plan.append({"wire": t["wire"], "via_term": t["name"], "deletable": ok, "why": why})
            if not ok:
                refusal = why
            reps.extend(rep)
        K.setdefault("delete_plans", []).append({"uid": uid, "plan": plan, "refused": refusal,
                                                 "error_in_sinks_to_repair": reps})
        fact("B3 delete plan for #%d: %r" % (uid, plan))
        if refusal:
            kept_nodes.append({"uid": uid, "why": refusal})
            gate("P_c3 node #%d is KEPT because the safety rule refuses one of its wires (a result, not a "
                 "failure)" % uid, True, refusal)
            continue
        up = next((c["upstream_source"] for c in chain if c["uid"] == uid), None)
        # THE WIRE DELETES ARE GATED BEFORE THE NODE GOES (the peer's 3.2): delete_by_uid records a failure
        # in `error_verbatim` and returns; run 1's code then deleted the NODE regardless, which would leave
        # dangling broken wires -> ExecState 0 -> g.save refuses -> no artefact, diagnosed two stages later.
        wire_results = [delete_by_uid("B3 wire w%d of #%d" % (w, uid), OP2, "Wire", w)
                        for w in sorted({p["wire"] for p in plan})]
        bad = [r for r in wire_results if r.get("error_verbatim")]
        if bad:
            kept_nodes.append({"uid": uid, "why": "a wire delete FAILED: %r" % ([b["error_verbatim"]
                                                                                 for b in bad],)})
            gate("P_c3y node #%d is NOT deleted because %d of its wire deletes FAILED (deleting the node "
                 "anyway would leave dangling broken wires)" % (uid, len(bad)),
                 False, "%r" % ([(b["uid"], b["error_verbatim"]) for b in bad],))
            read_es("[B3] after the FAILED wire deletes of #%d" % uid, OP2, "B")
            continue
        delete_by_uid("B3 THE NODE #%d" % uid, OP2, "Property", uid)
        after_uids = g.uids(OP2, "Property")
        gone = uid not in after_uids
        deleted_nodes.append({"uid": uid, "gone": gone})
        if gone and reps:
            repairs_due.append({"deleted_uid": uid, "upstream_source": up, "error_in_sinks": reps})
        gate("P_c3b node #%d is gone from the Property census" % uid, gone, "gone=%r" % gone)
        read_es("[B3] after deleting #%d" % uid, OP2, "B")
    K["repairs_due"] = repairs_due
    K["deleted_nodes"], K["kept_nodes"] = deleted_nodes, kept_nodes
    fact("B3 deleted %r ; kept %r" % (deleted_nodes, kept_nodes))

    # ---- B3b acceptance: no `Is Broken?` terminal left
    nodes2, nets2, echo_bad2 = census0(OP2, "B3b v2 top-level census (AFTER the deletes)")
    K["census_after"] = nodes2
    K["echo_failures_after"] = echo_bad2
    gate("P_d0 EVERY node in the AFTER census echoed its own uid - without this P_d below is falsely "
         "passable (a systematic echo failure reads exactly like 'the readback is gone')", not echo_bad2,
         "%r" % (echo_bad2,))
    K["counts_after"] = {c2: g.count(OP2, c2) for c2 in ("Node", "Wire", "Property", "Invoke",
                                                         "ControlTerminal")}
    fact("B3b counts AFTER: %r (before %r)" % (K["counts_after"], K["counts_before"]))
    left = [(r["n"], r["uid"]) for r in nodes2 if any(t["name"] in BROKEN_NAMES for t in r["terms"])]
    K["is_broken_terminals_left"] = left
    gate("P_d NO node on v2's top-level diagram carries the Wire.Is Broken? item terminal any more",
         not left, "%r" % (left,))

    # ---- B4 THE ERROR CHAIN MUST SURVIVE: re-wire each deleted node's UPSTREAM error SOURCE straight into
    #      the ERROR-IN sink(s) its `error out` used to feed (the brief's "the Invoke's error out straight to
    #      the error out indicator", generalised to whatever the census actually found downstream).
    done = []
    for rep in repairs_due:
        up = rep.get("upstream_source")
        for sink in rep["error_in_sinks"]:
            entry = {"deleted_uid": rep["deleted_uid"], "from": up,
                     "to": {"uid": sink["uid"], "t": sink["t"], "name": sink["name"]}}
            src_live = node_by_uid(nodes2, up["uid"]) if up else None
            sink_live = node_by_uid(nodes2, sink["uid"])
            if not up or src_live is None or sink_live is None:
                entry["error_verbatim"] = ("no live upstream error SOURCE (%r) or sink (%r) to re-wire"
                                           % (up, sink))
            else:
                try:
                    dw, es_r = g.connect_terminals(OP2, sink_live["n"], sink["t"], src_live["n"], up["t"])
                    entry.update({"wire_delta": dw, "exec_state_after": es_r, "error_verbatim": ""})
                except Exception as e:                                             # noqa: BLE001
                    entry["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            done.append(entry)
            fact("B4 error-chain re-wire: %r" % (entry,))
    K["error_chain_repairs"] = done
    # THE FREE READING the peer's 6 asked for: `connect_terminals` -> OpConnect_v0 is a READER-FREE edit op
    # (no `Wire.Is Broken?` anywhere in it), and B4 has just made such an edit on this VI. Its ExecState
    # either side is reported. NO VALUE IS ASSERTED and nothing is decided from it.
    if done:
        fact("B4 READER-FREE EDIT READING (reported, nothing asserted): connect_terminals -> OpConnect_v0 "
             "returned ExecState %r after the repair wire(s) %r"
             % ([d.get("exec_state_after") for d in done], [d.get("wire_delta") for d in done]))
        gate("P_e0 the reader-free edit's own ExecState reading is recorded (NO VALUE IS ASSERTED)", True,
             "%r" % ([d.get("exec_state_after") for d in done],))
    nodes3, _n3, _e3 = census0(OP2, "B4 v2 top-level census (AFTER the error-chain repair)")
    K["census_after_repair"] = nodes3
    still_bare = []
    for rep in repairs_due:
        for sink in rep["error_in_sinks"]:
            live = node_by_uid(nodes3, sink["uid"])
            w = next((t["wire"] for t in (live or {}).get("terms", []) if t["i"] == sink["t"]), 0)
            if not w:
                still_bare.append({"uid": sink["uid"], "t": sink["t"], "name": sink["name"]})
    K["error_in_sinks_still_bare"] = still_bare
    gate("P_e the error chain SURVIVES: every error-in sink the deleted node used to feed is wired again",
         not still_bare, "still bare: %r ; repairs %r" % (still_bare, done))

    pw_after = g.panel_wiring(OP2)
    eo_after = next((r for r in pw_after if r["label"] == ERR_OUT_NAME and r["indicator"]), None)
    K["error_out_panel_final"] = eo_after
    fact("B4 the `error out` INDICATOR: donor %r -> v2 %r" % (eo_before, eo_after))
    gate("P_e2 v2's `error out` panel terminal is WIRED", bool(eo_after and eo_after["wire"]),
         "v2 %r (the DONOR's own reading was %r - if the donor's is 0 too, this is a property inherited "
         "from OpConnectNested_v1, not something this build lost)" % (eo_after, eo_before))
    gate("P_e3 v2's `error out` panel wiring is UNCHANGED from the donor's",
         bool(eo_before) and bool(eo_after) and eo_before["wire"] == eo_after["wire"],
         "donor %r -> v2 %r" % ((eo_before or {}).get("wire"), (eo_after or {}).get("wire")))

    # ---- B5 ExecState then SAVE
    es = read_es("[B5] v2 immediately before the save", OP2, "B")
    K["exec_state_before_save"] = es
    gate("P_f v2's ExecState is 1 at the save point", es == 1, "%r" % (es,))
    try:
        size = g.save(OP2)
        K["save_returned_size"], K["save_error_verbatim"] = size, ""
    except Exception as e:                                                         # noqa: BLE001
        K["save_returned_size"], K["save_error_verbatim"] = None, "%s: %s" % (type(e).__name__, str(e)[:400])
    fact("B5 g.save(OP2) -> %r ; error VERBATIM %r" % (K["save_returned_size"], K["save_error_verbatim"]))
    gate("P_f2 v2 SAVED with no allow_broken and no gui_save", K["save_returned_size"] is not None,
         "%r / %r" % (K["save_returned_size"], K["save_error_verbatim"]))
    sv = probe("B5 OpConnectNested_v2.vi AFTER the save", OP2)
    K["v2_md5_after_save"], K["v2_size_after_save"] = sv.get("md5"), sv.get("size")
    fact("B5 THE ARTEFACT: claudeDev\\OpConnectNested_v2.vi md5 %r size %r"
         % (K["v2_md5_after_save"], K["v2_size_after_save"]))
    d3 = probe("B5b the donor after the whole build", DONOR)
    gate("P_b4 the donor OpConnectNested_v1.vi is byte-unchanged by the build", d3.get("md5") == DONOR_MD5,
         d3.get("md5", "?"))
    try:
        g.close_panel(OP2)
    except Exception:                                                              # noqa: BLE001
        pass
    dump()


# ===================================================================================== STAGE C
def stage_c():
    print("\n=== STAGE C  COLD reopen of v2 in a freshly restarted LabVIEW + the 242 regression", flush=True)
    K = R["stage_c"]
    es = read_es("[C] v2 COLD in a freshly restarted LabVIEW", OP2, "C")
    K["cold_exec_state"] = es
    gate("P_g v2 REOPENS COLD at ExecState 1 (the artefact's pass criterion)", es == 1, "%r" % (es,))
    cv = probe("C the artefact re-read after the cold open", OP2)
    K["v2_md5_cold"] = cv.get("md5")
    gate("P_g2 the artefact's md5 is unchanged by the cold open",
         cv.get("md5") == R["stage_b"].get("v2_md5_after_save"),
         "%r -> %r" % (R["stage_b"].get("v2_md5_after_save"), cv.get("md5")))

    # ---- C2 the shipped-path build_property regression
    print("\n--- C2  the `VI Server:VI` 242 read-mode build_property regression (cycle 61's gate)", flush=True)
    try:
        shutil.copy2(S3A_ARTEFACT, REG_SCRATCH)
        g.open_panel(REG_SCRATCH)
        time.sleep(0.8)
        before = g.count(REG_SCRATCH, "Property")
        uids_before = set(g.uids(REG_SCRATCH, "Property"))
        K["property_census_before"] = before
        new = g.build_property(REG_SCRATCH, VI_CLASS, [(PROP_VI_242, False)], REG_POS)
        K["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        K["error_verbatim"] = ""
        added = sorted(set(g.uids(REG_SCRATCH, "Property")) - uids_before)
        K["property_uid_delta"] = added
        row_i4 = None
        for n in range(SCAN_LIMIT):
            try:
                nu, rows = g.node_terms_uid(REG_SCRATCH, 0, n)
            except Exception:                                                      # noqa: BLE001
                continue
            if added and nu == added[0]:
                row_i4 = next((r for r in term_rows(rows) if r["i"] == 4), None)
                K["full_terminal_table"] = term_rows(rows)
                break
        K["row_i4"] = row_i4
        fact("C2 build_property('VI Server:VI', [('242', False)]) -> new %r ; i=4 row VERBATIM %r"
             % (K["new"], row_i4))
        gate("C_2 the shipped-path 242 regression creates a node whose i=4 row is a SOURCE",
             bool(row_i4) and row_i4.get("is_source") is True, "%r" % (row_i4,))
        for uid in added:
            delete_by_uid("C2 regression probe #%d" % uid, REG_SCRATCH, "Property", uid)
        K["property_census_after_delete"] = g.count(REG_SCRATCH, "Property")
        gate("C_2b the regression probe deleted again and the Property census returned",
             K["property_census_after_delete"] == before,
             "%r -> %r" % (before, K["property_census_after_delete"]))
    except Exception as e:                                                         # noqa: BLE001
        K["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
        fact("C2 raised %s" % K["error_verbatim"])
        gate("C_2 the shipped-path 242 regression ran without an unhandled exception", False,
             K["error_verbatim"])
    finally:
        K["scratch_exists"] = drop_scratch(REG_SCRATCH, "C2")
        gate("Z_c the C2 regression scratch is deleted in the same run", not K["scratch_exists"],
             REG_SCRATCH)
    dump()


# ===================================================================================== STAGE D
def fresh_bed(path, tag, leg):
    shutil.copy2(S3A_ARTEFACT, path)
    g.open_panel(path)
    time.sleep(1.0)
    rec = {"path": path, "cold_exec_state": read_es("[cold] %s" % tag, path, leg)}
    try:
        rec["d639"] = diag_index(path, D639)
    except Exception as e:                                                         # noqa: BLE001
        rec["d639"] = None
        rec["d639_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    rec["sink"], rec["source"] = {}, {}
    if isinstance(rec["d639"], int):
        for key, uid, what in (("sink", CASE_UID, "SINK"), ("source", SRC_UID, "SOURCE")):
            r = {"uid": uid}
            try:
                rows = g.node_labels(path, int(rec["d639"]))
                n = next((i for i, x in enumerate(rows) if x["uid"] == uid), None)
                r["nodes_index"] = n
                r["label"] = next((x["label"] for x in rows if x["uid"] == uid), None)
                if n is not None:
                    echo, trows = g.node_terms_uid(path, int(rec["d639"]), n)
                    r["uid_echo"] = echo
                    r["terms"] = term_rows(trows) if echo == uid else []
            except Exception as e:                                                 # noqa: BLE001
                r["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            rec[key] = r
            fact("%s %s #%d: Nodes[%r] echo %r label %r t0 %r"
                 % (tag, what, uid, r.get("nodes_index"), r.get("uid_echo"), r.get("label"),
                    next((t for t in r.get("terms", []) if t["i"] == 0), None)))
    rec["t0_wire_before"] = next((t["wire"] for t in rec["sink"].get("terms", []) if t["i"] == 0), None)
    rec["wire_census_before"] = g.count(path, "Wire")
    return rec


def drop_scratch(path, leg):
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


def one_arm(which, path, caller, labels):
    """ONE idempotent connect on ONE fresh scratch of the bed. NOTHING IS SAVED. NO VALUE IS ASSERTED."""
    print("\n--- ARM %s  the idempotent connect (46,24,0,46,25,0) through %s" % (which, caller.__name__),
          flush=True)
    a = {"arm": which, "caller": caller.__name__, "scratch": path}
    try:
        rec = fresh_bed(path, "ARM %s scratch" % which, which)
        a.update(rec)
        sink_i, src_i = rec["sink"].get("nodes_index"), rec["source"].get("nodes_index")
        a["brief_indices"] = [BRIEF_SINK_NODE, BRIEF_SRC_NODE]
        a["live_indices"] = [sink_i, src_i]
        a["indices_match_brief"] = (sink_i == BRIEF_SINK_NODE and src_i == BRIEF_SRC_NODE)
        a["echoes_ok"] = (rec["sink"].get("uid_echo") == CASE_UID
                          and rec["source"].get("uid_echo") == SRC_UID)
        fact("ARM %s: live Nodes[] indices %r vs the brief's %r ; uid echoes ok = %r"
             % (which, a["live_indices"], a["brief_indices"], a["echoes_ok"]))
        gate("P_%s0 ARM %s both nodes echo their own uid on Diagram #639" % (which, which), a["echoes_ok"],
             "sink echo %r, source echo %r" % (rec["sink"].get("uid_echo"), rec["source"].get("uid_echo")))
        if sink_i is None or src_i is None or not a["echoes_ok"]:
            a["non_result"] = "the nodes did not resolve - this arm is a NON-RESULT, not a reading"
            fact("ARM %s %s" % (which, a["non_result"]))
            return a
        es_pre = read_es("[ARM %s] immediately BEFORE the connect" % which, path, which)
        a["exec_state_before"] = es_pre
        t0 = time.time()
        try:
            dw, es_post, err = caller(path, int(rec["d639"]), sink_i, 0, int(rec["d639"]), src_i, 0, labels)
            a["wire_delta"], a["exec_state_from_wrapper"], a["op_error_verbatim"] = dw, es_post, err
            a["call_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            a["wire_delta"] = a["exec_state_from_wrapper"] = None
            a["op_error_verbatim"] = ""
            a["call_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        a["call_cost_s"] = round(time.time() - t0, 2)
        a["wire_census_after"] = g.count(path, "Wire")
        try:
            echo, trows = g.node_terms_uid(path, int(rec["d639"]), sink_i)
            a["t0_wire_after"] = next((t["wire"] for t in term_rows(trows) if t["i"] == 0), None)
            a["sink_echo_after"] = echo
        except Exception as e:                                                     # noqa: BLE001
            a["t0_wire_after"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
        fact("ARM %s: wire_delta %r ; Wire %r -> %r ; sink t0 wire %r -> %r ; op error VERBATIM %r ; "
             "call error %r" % (which, a.get("wire_delta"), rec["wire_census_before"],
                                a.get("wire_census_after"), rec["t0_wire_before"], a.get("t0_wire_after"),
                                a.get("op_error_verbatim"), a.get("call_error_verbatim")))
        gate("P_%s1 ARM %s the connect is IDEMPOTENT (wire_delta 0, Wire census unchanged)" % (which, which),
             a.get("wire_delta") == 0 and a.get("wire_census_after") == rec["wire_census_before"],
             "delta %r ; %r -> %r" % (a.get("wire_delta"), rec["wire_census_before"],
                                      a.get("wire_census_after")))
        a["exec_state_immediately_after"] = read_es("[ARM %s] immediately AFTER the connect" % which, path,
                                                    which)
        reread = []
        for k in range(3):
            time.sleep(2.0)
            reread.append(read_es("[ARM %s] re-read %d of 3 (~2 s apart)" % (which, k + 1), path, which))
        a["re_reads"] = reread
        gate("P_%s2 ARM %s's ExecState timeline is recorded (NO VALUE IS ASSERTED)" % (which, which), True,
             "before %r -> wrapper %r -> after %r -> re-reads %r"
             % (a.get("exec_state_before"), a.get("exec_state_from_wrapper"),
                a.get("exec_state_immediately_after"), reread))
    finally:
        a["scratch_exists"] = drop_scratch(path, "ARM %s" % which)
        gate("Z_%s the ARM %s scratch is deleted in the same run" % (which, which), not a["scratch_exists"],
             path)
    return a


def stage_d():
    print("\n=== STAGE D  THE PAIRED DISCRIMINATING TEST - both arms in ONE LabVIEW session, nothing saved",
          flush=True)
    K = R["stage_d"]
    K["v2"] = one_arm("V2", ARMV2_SCRATCH, g.connect_nested_v2, V2_LABELS)
    dump()
    K["v1"] = one_arm("V1", ARMV1_SCRATCH, CONNECT_V1, V1_LABELS)
    dump()
    print("\n--- THE PAIRED COMPARISON (same LabVIEW session, two independent scratches of the same bed)",
          flush=True)
    print("  %-6s %-10s %-12s %-14s %-12s %-22s" % ("arm", "cold ES", "wire_delta", "ES after", "re-reads",
                                                    "op error"), flush=True)
    for key in ("v2", "v1"):
        a = K.get(key) or {}
        print(("  %-6s %-10r %-12r %-14r %-12r %-22r"
               % (key.upper(), a.get("cold_exec_state"), a.get("wire_delta"),
                  a.get("exec_state_immediately_after"), a.get("re_reads"),
                  (a.get("op_error_verbatim") or a.get("call_error_verbatim") or "")[:22]))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    dump()


# ===================================================================================== STAGE E
def stage_e():
    print("\n=== STAGE E  THE BAD-CALL GATE: v2 with a nonexistent node index must report an ERROR",
          flush=True)
    K = R["stage_e"]
    try:
        shutil.copy2(S3A_ARTEFACT, BAD_SCRATCH)
        g.open_panel(BAD_SCRATCH)
        time.sleep(0.8)
        di = diag_index(BAD_SCRATCH, D639)
        K["d639"] = di
        w_before = g.count(BAD_SCRATCH, "Wire")
        bad_sink, bad_src = 9999, 9998
        K["call"] = "connect_nested_v2(target, %r, %r, 0, %r, %r, 0) - NONEXISTENT node indices" % (
            di, bad_sink, di, bad_src)
        fact("E %s" % K["call"])
        try:
            dw, es, err = g.connect_nested_v2(BAD_SCRATCH, di, bad_sink, 0, di, bad_src, 0, V2_LABELS)
            K["wire_delta"], K["exec_state"], K["wrapper_error_verbatim"] = dw, es, err
            K["call_error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            K["wire_delta"] = K["exec_state"] = None
            K["wrapper_error_verbatim"] = ""
            K["call_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        # read the op's OWN error cluster RAW, off the indicator
        try:
            raw = g.op(OP2).GetControlValue("error out")
            K["error_out_raw"] = list(raw) if isinstance(raw, (list, tuple)) else raw
        except Exception as e:                                                     # noqa: BLE001
            K["error_out_raw"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        K["wire_census"] = [w_before, g.count(BAD_SCRATCH, "Wire")]
        fact("E bad call -> wrapper error VERBATIM %r ; call error %r ; RAW `error out` %r ; Wire %r"
             % (K.get("wrapper_error_verbatim"), K.get("call_error_verbatim"), K.get("error_out_raw"),
                K["wire_census"]))
        raw = K.get("error_out_raw")
        non_empty = bool(isinstance(raw, list) and len(raw) >= 2 and (raw[0] or int(raw[1] or 0) != 0))
        K["error_cluster_non_empty"] = non_empty
        gate("P_j v2's `error out` cluster is NON-EMPTY on a deliberately bad call (an op that has gone "
             "silent about errors is a FAIL)", non_empty, "RAW %r ; wrapper said %r"
             % (raw, K.get("wrapper_error_verbatim") or K.get("call_error_verbatim")))
    except Exception as e:                                                         # noqa: BLE001
        K["stage_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:500])
        gate("P_j the bad-call gate ran without an unhandled exception", False, K["stage_error_verbatim"])
    finally:
        K["scratch_exists"] = drop_scratch(BAD_SCRATCH, "E")
        gate("Z_e the bad-call scratch is deleted in the same run", not K["scratch_exists"], BAD_SCRATCH)
    dump()


# ===================================================================================== main
def main():
    print("=== diag_c64_connect_v2  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 64 material #2: build OpConnectNested_v2 (v1 MINUS the embedded Wire.Is Broken? "
          "readback) and run the PAIRED v2-vs-v1 test in ONE LabVIEW session.", flush=True)
    print("=== No allow_broken, no gui_save, no GUI action, no recipe, no cast, no splice, no VI run, "
          "no motor/ASI/camera. The only file created under claudeDev is OpConnectNested_v2.vi.", flush=True)

    stage_a()                        # files only

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    R["ref_counts_before"] = g.ref_counts()
    fact("tracked VI Server refs BEFORE: %r" % (R["ref_counts_before"],))

    D.fresh("Z_R1 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart_1"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart_1"])
    dump()

    try:
        stage_b()
    except SystemExit:
        raise
    except Exception as e:                                                         # noqa: BLE001
        gate("Vx stage_b completed without an unhandled exception", False,
             "EXC %s: %s" % (type(e).__name__, str(e)[:400]))
    finally:
        dump()

    D.fresh("Z_R2 RESTART before the COLD reopen of v2")
    R["handles"]["after_restart_2"] = labview_handles()
    fact("LabVIEW handles AFTER the second restart: %r" % R["handles"]["after_restart_2"])
    dump()

    saved = R["stage_b"].get("save_returned_size") is not None
    later = (stage_c, stage_d, stage_e) if saved else (stage_c,)
    if not saved:
        gate("Vy STAGE B produced a SAVED artefact (without it ARM V2 would be measuring the donor under a "
             "different file name, so D and E are SKIPPED)", False,
             "save error VERBATIM %r" % (R["stage_b"].get("save_error_verbatim"),))
    for stage in later:
        try:
            stage()
        except SystemExit:
            raise
        except Exception as e:                                                     # noqa: BLE001
            gate("Vx %s completed without an unhandled exception" % stage.__name__, False,
                 "EXC %s: %s" % (type(e).__name__, str(e)[:300]))
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
    z4 = probe("Z1e OpCreateLocalRead_v0.vi after everything", LOCALREAD)
    z5 = probe("Z1f THE DONOR OpConnectNested_v1.vi after everything", DONOR)
    z6 = probe("Z1g THE ARTEFACT OpConnectNested_v2.vi after everything", OP2)
    R["v2_md5_final"] = z6.get("md5")
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == LOCALREAD_MD5,
         "%s" % (z4.get("md5"),))
    gate("Z_1c THE DONOR OpConnectNested_v1.vi is byte-unchanged across the whole run",
         z5.get("md5") == DONOR_MD5, "%s" % (z5.get("md5"),))
    rc = R["ref_counts"] or {}
    gate("Z_1d refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    left = [p for p in SCRATCHES if os.path.exists(p)]
    gate("Z_1e EVERY scratch is gone (the artefact OpConnectNested_v2.vi is the ONLY file this run leaves)",
         not left, "still on disk: %r" % ([os.path.basename(p) for p in left],))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-5s %-58s %-12s %-10s" % ("step", "leg", "call / tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-5s %-58s %-12r %-10s" % (row["step"], row["leg"], row["tag"][:58],
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
