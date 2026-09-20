r"""motor_census.py - every MOTION CALL SITE reachable from a given VI, by REACHABILITY TO A SERIAL WRITE.

Step 1 of docs/motor-limit-assurance-plan.md SS-D's build order (census -> A -> B -> broken-VI proof ->
C + record hook).  A READER: it opens VIs by reference, traverses them, and changes nothing - so it
lives in tools/, not tools/recipes/.  No VI is run, nothing is saved, no serial port is opened.

WHAT ALREADY EXISTED, checked before writing a line (CLAUDE.md "before creating any new op/tool/recipe")
  * docs/main-vi-subvi-identity.md - 98 call sites / 56 distinct callees of the WORKING COPY
    `Min_Track N beads V6_ParallelLoop.vi`, measured 2026-09-14 by tools/bench/sweep_subvis_main.py
    (OpSubVIs_v1 per diagram).  THE SOURCE OF THE PLAN'S PROVISIONAL COUNTS: its "by callee" table has
    `MOV.vi` 7, `VEL.vi` 4, `SetCommand.vi` 9, ASI `Move Axis to Position.vi` 4, `GOH.vi` 2
    (main-vi-subvi-identity.md:18-29).  It is a subVI IDENTITY listing; it classifies nothing and it
    was never run on the 3StateClamping original.
  * docs/instrument-libraries.md:167-169 - the whole-tree library counts (MOV x12, VEL x9, GOH x7 ...),
    which count FILES ON DISK, not call sites in one VI.
  * docs/motion-path-audit.md - PI MOV/VEL = send + error query; every ASI write funnels through
    `Send Serial Command.vi` (VISA Write/Read inside a semaphore).
  * tools/callgraph.py - OFFLINE byte-scan of subVI NAME references.  Cannot see call sites, cannot
    see VISA.  Reused here only as prior art, not as the mechanism.
  * tools/bench/build_diagram_hierarchy.py - the nearest-structure match that turns a Traverse
    'Diagram' index into "which loop/case owns it".  Its rule (a structure's body Diagram sits at
    struct_pos + (10,22); accept only if the runner-up is MARGIN times farther) is reused below.
  None of them answers "does this call site reach a serial write", which is the census's PRIMARY rule.

CLASSIFICATION (the judgement session's decision, implemented exactly)
  PRIMARY  = REACHABILITY.  A call site is MOTION if the called subVI's own hierarchy contains a
             serial WRITE node.  Measured, not named.
  CROSS-CHECK = the name list below.  A call site that matches reachability but is NOT on the name
             list is reported as UNCLASSIFIED; a name-list call site that does NOT match reachability
             is reported as NAME_ONLY.  Neither is ever dropped.

CYCLE-1 JUDGEMENT DECISIONS (2026-09-17) - applied on top of the above; they LABEL what the
reachability test found, they do not replace it.
  DECISION 1 - the partition is not query-vs-command, it is "CAN THIS CALL CHANGE MOTOR STATE?".
    Every MOTION site carries a `kind`:
      COMMAND    can change position / velocity / motor state.  IN scope for checks A, B, C and for
                 the approved fixed clamp (plan `## Pre-decided` 2).
      QUERY      transmits but cannot change motor state (POS?, TMN?, TMX?, ASI Get Current
                 Position).  OUT of scope for A/B/C - kept in the census because it is serial
                 traffic and CLAUDE.md rule 1c cares where serial sits.
      CONFIGURE  Autonics Configure / ASI Initialize / Mercury_GCS_Configuration_Setup.  IN scope,
                 default-deny: a configure call can home an axis or set a soft limit.  Whether it
                 actually does is NOT measured here; only a recorded measurement may demote it.
    Callee not on any list  =>  COMMAND (in scope).  A site is NEVER defaulted out of scope.
  DECISION 2 - the UNKNOWN bucket is ABOLISHED.  A site whose callee's hierarchy cannot be
    traversed (the error-1040 vi.lib VIs) is emitted as `ASSUMED_MOTION`, counted IN SCOPE, with
    the reason recorded (which VI, which error).  Same default-deny principle as motor_gate.py.
    A site leaves ASSUMED_MOTION only by a recorded measurement, never by assumption.  The census
    can therefore state MECHANICALLY that ZERO sites are undecided - which is what plan SS-D.4
    ("a checker that misses one is not used") requires.

HOW "contains a serial write" IS MEASURED, and why it is a COM read
  Two offline probes (scratchpad, no LabVIEW) REFUTED the cheap route: a .vi's raw bytes and every
  zlib blob inside it do NOT carry the string "VISA Write", not even in SetCommand.vi, which is
  measured to contain five of them.  Only VISA *terminal* names survive.  And the node's scripting
  CLASS is the generic 'Function' (tools/bench/visa_class_probe.log:14), so Traverse-by-class cannot
  single it out either.  What identifies it is its LABEL: OpNodeLabels_v0 read |VISA Write| on uids
  795/865/2246/2711/435 of SetCommand.vi (visa_class_probe.log:23-40).  So: per VI, walk its Traverse
  'Diagram' indices and read node labels.  Cost is paid once per VI path and memoised.

PREDICTION CONTRACT (printed before the run, machine-checked after).  Run 3 adds P5-P8: the two
decisions above are a RELABELLING, so every count the reachability test produced must be UNCHANGED
from run 2 (tools/bench/motor_census_run2.log).  A change in a BUCKET LABEL is the intended effect;
a change in the MOTION TOTAL or a per-callee count is a FAILED PREDICTION and owes a peer review.
 P1  >= 1 PI motion call site in the 3StateClamping original
 P2  >= 1 ASI motion call site in the 3StateClamping original
 P3  md5 of both originals unchanged, before and after
 P4  the tool exits 0
 P5  every call site of every target carries a `kind` in {COMMAND, QUERY, CONFIGURE,
     ASSUMED_MOTION, NONE}
 P6  undecided == 0 on every target
 P7  the 3StateClamping original still shows exactly 41 motion call sites (run 2's number)
 P8  per-callee counts unchanged from run 2: MOV 7 / VEL 4 / SetCommand 9 /
     ASI Move Axis to Position 4 / GOH 2

    py tools/bgrun.py --max-min 45 --log tools/bench/motor_census.log -- env MATERIAL=1 py -u tools/motor_census.py
"""
import hashlib
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PROJECT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import gscript as g                                                            # noqa: E402

BENCH = os.path.join(HERE, "bench")
TRACK = r"G:\Codes\LabVIEW_Codes\MinLab\zz_LabView VI\AAA_UNIST\2. Tracking"
ORIG_3STATE = os.path.join(TRACK, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
ORIG_V6 = os.path.join(TRACK, "Min_Track N beads V6_ParallelLoop.vi")
CLAUDEDEV = g.CLAUDEDEV

# Target 2 of the brief: "whatever VI under user.lib\claudeDev that drive_original_copy.py names as
# its target".  tools/bench/drive_original_copy.py:89 names `claudeDev\D0_MAINCOPY_<STAMP>.vi`, a
# per-run scratch copy created and deleted inside the run - so it normally does not exist.  Resolved
# at run time rather than asserted.
def d0_targets():
    out = []
    try:
        for f in sorted(os.listdir(CLAUDEDEV)):
            if f.upper().startswith("D0_MAINCOPY") and f.lower().endswith(".vi"):
                out.append(os.path.join(CLAUDEDEV, f))
    except OSError:
        pass
    return out


# --- the two rules ------------------------------------------------------------------------------
# A serial TRANSMIT node, by node label.  "VISA Write" is the measured one; the others are the
# labels LabVIEW gives the same act on the older serial palette, kept so the reader is not blind to
# a VI that predates VISA.  Everything VISA-ish that is NOT a transmit is recorded separately.
WRITE_LABELS = ("VISA Write", "Serial Port Write", "Bytes Written")
VISA_ANY = "VISA"

# CROSS-CHECK ONLY - never used to decide.  The names docs/motor-limit-assurance-plan.md:34-35 and
# docs/instrument-libraries.md:167-169 call motion.
NAME_LIST = {
    "mov.vi", "vel.vi", "goh.vi",
    "move axis to position.vi", "move axis relative.vi",
    "setcommand.vi", "setcommand_signed.vi",
}

# --- DECISION 1's three kinds.  Basenames, lower case.  These lists LABEL; they never decide
# whether a site is motion (reachability does that), and a callee on none of them falls through to
# COMMAND, never out of scope.
COMMAND_NAMES = {
    "mov.vi", "vel.vi", "goh.vi",
    "move axis to position.vi", "move axis relative.vi",
    "setcommand.vi", "setcommand_signed.vi",
    # the three LAB wrappers the reachability test caught and a name-based checker would have missed
    "motor control v5_no recording.vi", "asi_adjust focus-subvi.vi",
    "check n bead pos v3-kimlab.vi",
}
QUERY_NAMES = {"pos?.vi", "tmn?.vi", "tmx?.vi", "get current position.vi"}
CONFIGURE_NAMES = {"configure.vi", "initialize.vi", "mercury_gcs_configuration_setup.vi"}
KINDS = ("COMMAND", "QUERY", "CONFIGURE", "ASSUMED_MOTION", "NONE")
IN_SCOPE_KINDS = ("COMMAND", "CONFIGURE", "ASSUMED_MOTION")

STRUCT_CLASSES = ["WhileLoop", "ForLoop", "CaseStructure", "Sequence", "EventStructure",
                  "FlatSequenceFrame", "CaseSelector"]
MARGIN = 3.0            # build_diagram_hierarchy.py's acceptance margin, reused unchanged
REACH_BUDGET_S = 1800.0  # wall-clock ceiling for the reachability DFS; anything untested -> UNKNOWN


def md5(p):
    if not os.path.exists(p):
        return "MISSING"
    h = hashlib.md5()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def device_of(path):
    """PI / ASI / rotor / unknown, from the driver library the callee lives in.  A LABEL on the row,
    not the classification rule - docs/instrument-libraries.md:37-40 is the source."""
    low = (path or "").lower()
    if "\\mercury\\" in low or "gcs_labview" in low:
        return "PI"
    if "asi tg-1000" in low:
        return "ASI"
    if "autonics" in low:
        return "rotor"
    if "claudedev" in low and "setcommand" in os.path.basename(low):
        return "rotor"
    return "unknown"


# --- per-VI measurements, memoised -----------------------------------------------------------------
_direct = {}        # vipath.lower() -> {"write": n, "visa": n, "diagrams": n, "labels": [...], "err": str}
_callees = {}       # vipath.lower() -> [paths]
_reach = {}         # vipath.lower() -> True | False | None(unknown)
_paths = {}         # vipath.lower() -> real path
_t_start = 0.0


def budget_left():
    return REACH_BUDGET_S - (time.time() - _t_start)


def direct_write(path):
    """Does THIS VI's own diagrams carry a serial transmit node?  One count() + one node_labels()
    per Traverse 'Diagram' index."""
    k = path.lower()
    if k in _direct:
        return _direct[k]
    rec = {"write": 0, "visa": 0, "diagrams": 0, "labels": [], "err": ""}
    try:
        nd = int(g.count(path, "Diagram"))
        rec["diagrams"] = nd
        for d in range(nd):
            rows, err = g.node_labels(path, d, strict=False)
            if err:
                rec["err"] = (rec["err"] + " | " + str(err))[:200]
            for r in rows:
                lab = r.get("label") or ""
                if any(lab.startswith(w) for w in WRITE_LABELS):
                    rec["write"] += 1
                    if lab not in rec["labels"]:
                        rec["labels"].append(lab)
                elif VISA_ANY in lab:
                    rec["visa"] += 1
    except Exception as e:
        rec["err"] = "%s: %s" % (type(e).__name__, str(e)[:160])
    _direct[k] = rec
    return rec


def callees_of(path):
    """Immediate subVI PATHS of `path`, by the per-diagram OpSubVIs_v1 sweep.

    RUN 1 (tools/bench/motor_census.log, 2026-09-17 23:33) USED `VI.Callees` HERE AND IT BROKE THE
    PRIMARY RULE: that property returns NAMES ("MOV.vi", "ASI TG-1000.lvlib:Send Serial Command.vi",
    and .ctl typedefs), GetVIReference on a bare name did not resolve, so the name went on as if it
    were a path and `count(Diagram)` died with error 1445 / error 7 - 72 of 126 VIs errored and 109
    came back UNKNOWN, including every VI below MOV/VEL/GOH/Move Axis to Position.  So those four
    were classified `name` only, contradicting docs/motion-path-audit.md:58-74, which records PI's
    MOV/VEL sending over serial and every ASI write funnelling through `Send Serial Command.vi`.
    OpSubVIs_v1 returns the REAL `VI Path` for every call site (that is the whole point of
    docs/main-vi-subvi-identity.md), so it is the only route used now."""
    k = path.lower()
    if k in _callees:
        return _callees[k]
    out, seen = [], set()
    try:
        nd = int(g.count(path, "Diagram"))
        for d in range(nd):
            rows, _err = g.subvis(path, d, purge=False, strict=False)
            for r in rows:
                p2 = r.get("path") or ""
                if not p2 or not os.path.isabs(p2):
                    continue                       # a name, not a path: unusable, and never silent
                if p2.lower() in seen:
                    continue
                seen.add(p2.lower())
                out.append(p2)
    except Exception as e:
        _direct.setdefault(k, {}).setdefault("callee_err", "%s: %s" % (type(e).__name__, str(e)[:140]))
    _callees[k] = out
    return out


def reaches_write(path, depth=0, stack=()):
    """True / False / None(unknown, budget or error).  Demand-driven DFS, memoised per VI path."""
    k = path.lower()
    if k in _reach:
        return _reach[k]
    if k in stack:
        return False                                   # recursion guard: a cycle adds no write
    if budget_left() <= 0:
        return None
    _reach[k] = None                                   # provisional, so a cycle sees UNKNOWN not True
    rec = direct_write(path)
    if rec["write"] > 0:
        _reach[k] = True
        return True
    if rec["err"] and rec["diagrams"] == 0:
        _reach[k] = None
        return None
    val = False
    for c in callees_of(path):
        if budget_left() <= 0:
            val = None
            break
        r = reaches_write(c, depth + 1, stack + (k,))
        if r is True:
            val = True
            break
        if r is None:
            val = None                                 # keep looking; a later True still wins
    _reach[k] = val
    return val


def unknown_reason(path, limit=3):
    """DECISION 2: why this callee's reachability could not be decided - WHICH VI, WHICH ERROR.
    Reads only the memoised caches (no new COM call), walking the callee's own hierarchy for the
    VIs that came back unknown WITH an error string; those are the error-1040 roots."""
    seen, queue, hits = set(), [path.lower()], []
    while queue and len(hits) < limit:
        k = queue.pop(0)
        if k in seen:
            continue
        seen.add(k)
        rec = _direct.get(k) or {}
        err = (rec.get("err") or "").strip()
        if _reach.get(k) is None and err:
            hits.append("%s: %s" % (os.path.basename(k), err[:110]))
        for c in _callees.get(k, []):
            if c.lower() not in seen:
                queue.append(c.lower())
    if hits:
        return "untraversable below %s -> " % os.path.basename(path) + " ; ".join(hits)
    return ("untraversable below %s -> no errored descendant in cache (budget exhausted or a "
            "provisional cycle marker)" % os.path.basename(path))


def kind_of(base, rule):
    """DECISION 1 + DECISION 2.  Returns (kind, in_scope)."""
    if rule == "unknown":                       # DECISION 2: never "UNKNOWN", always ASSUMED_MOTION
        return "ASSUMED_MOTION", True
    if rule == "none":                          # measured: reaches no serial write anywhere
        return "NONE", False
    if base in QUERY_NAMES:
        return "QUERY", False
    if base in CONFIGURE_NAMES:
        return "CONFIGURE", True
    return "COMMAND", True                      # incl. every callee on no list: default-deny


# --- structure path -------------------------------------------------------------------------------
def structure_map(target):
    """diagram index -> {"owner": class, "struct_uid": uid|None, "struct_pos": (x,y)|None}.
    Nearest-structure match, exactly the rule tools/bench/build_diagram_hierarchy.py:14-20 measured
    and verifies (body diagram at struct_pos + (10,22); accept only if the runner-up is MARGIN times
    farther).  Ambiguous -> struct_uid None, never guessed."""
    dias = g.report_all(target, "Diagram")
    structs = {}
    for cls in STRUCT_CLASSES:
        try:
            structs[cls] = g.report_all(target, cls)
        except Exception:
            structs[cls] = []
    out = {}
    for i, d in enumerate(dias):
        owner = d.get("owner") or ""
        rec = {"owner": owner, "struct_uid": None, "struct_pos": None}
        cands = structs.get(owner) or []
        if cands:
            dx, dy = d["pos"][0] - 10.0, d["pos"][1] - 22.0
            scored = sorted(((math.hypot(c["pos"][0] - dx, c["pos"][1] - dy), c) for c in cands),
                            key=lambda t: t[0])
            best = scored[0]
            second = scored[1][0] if len(scored) > 1 else float("inf")
            if best[0] == 0 or second >= MARGIN * max(best[0], 1e-6):
                rec["struct_uid"] = best[1]["uid"]
                rec["struct_pos"] = list(best[1]["pos"])
        out[i] = rec
    return out, len(dias)


# --- one target -------------------------------------------------------------------------------------
def census(target, tag):
    print("=" * 78, flush=True)
    print("TARGET %s  %s" % (tag, target), flush=True)
    res = {"tag": tag, "vi": target, "exists": os.path.exists(target), "ran": False,
           "call_sites": [], "by_callee": {}, "errors": []}
    if not res["exists"]:
        print("  DOES NOT EXIST - skipped", flush=True)
        return res
    smap, ndia = structure_map(target)
    res["n_diagrams"] = ndia
    print("  diagrams=%d" % ndia, flush=True)
    for d in range(ndia):
        try:
            rows, err = g.subvis(target, d, purge=False, strict=False)
        except Exception as e:
            res["errors"].append("diagram %d: %s" % (d, str(e)[:140]))
            continue
        if err:
            res["errors"].append("diagram %d: %s" % (d, str(err)[:140]))
        for r in rows:
            name, path, uid = r["name"], r["path"], r["uid"]
            res["by_callee"].setdefault(name, []).append({"diagram": d, "uid": uid})
            res["call_sites"].append({
                "owner_vi": target, "diagram": d,
                "owner_structure": smap.get(d, {}).get("owner", ""),
                "structure_uid": smap.get(d, {}).get("struct_uid"),
                "callee": name, "callee_path": path, "uid": uid,
            })
    print("  call sites=%d  distinct callees=%d" % (len(res["call_sites"]), len(res["by_callee"])),
          flush=True)
    res["ran"] = True
    return res


def classify(res):
    """Fill rule / device / reach for every call site of one target.  Reachability is memoised
    across targets, so the second target is nearly free."""
    for cs in res["call_sites"]:
        p = cs["callee_path"] or cs["callee"]
        base = os.path.basename(p).lower()
        by_name = base in NAME_LIST or base.replace("asi tg-1000.lvlib:", "") in NAME_LIST
        r = reaches_write(p)
        cs["reaches_serial_write"] = r
        cs["by_name"] = bool(by_name)
        cs["device"] = device_of(p)
        # `name` and `name_unknown` are kept APART on purpose: run 1 collapsed them and so reported
        # 18 call sites as "on the name list, no serial write found" when the truth was "the
        # reachability test never completed on them".
        if r is True and by_name:
            cs["rule"] = "both"
        elif r is True:
            cs["rule"] = "reachability"          # -> UNCLASSIFIED, reported never dropped
        elif by_name and r is False:
            cs["rule"] = "name"                  # -> NAME_ONLY: measured, no serial write anywhere
        elif by_name:
            cs["rule"] = "name_unknown"          # on the name list, reachability INCONCLUSIVE
        elif r is None:
            cs["rule"] = "unknown"
        else:
            cs["rule"] = "none"
        cs["motion"] = cs["rule"] in ("both", "reachability", "name", "name_unknown")
        # DECISION 1 + 2.  `motion` keeps its run-2 meaning (reaches a serial write) so the 41 is
        # comparable; `kind` / `in_scope` are the new, additional labels.
        cs["kind"], cs["in_scope"] = kind_of(base, cs["rule"])
        cs["assumed_reason"] = unknown_reason(p) if cs["kind"] == "ASSUMED_MOTION" else ""
    return res


def main():
    global _t_start
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    out = {"when": time.strftime("%Y-%m-%d %H:%M:%S"), "md5_before": {}, "md5_after": {},
           "targets": [], "gates": {}}
    for tag, p in (("3state", ORIG_3STATE), ("v6", ORIG_V6)):
        out["md5_before"][tag] = md5(p)
        print("MD5 BEFORE %-8s %s" % (tag, out["md5_before"][tag]), flush=True)
    print("PREDICTION P1 >=1 PI motion call site in the 3StateClamping original", flush=True)
    print("PREDICTION P2 >=1 ASI motion call site in the 3StateClamping original", flush=True)
    print("PREDICTION P3 both originals' md5 unchanged", flush=True)
    print("PREDICTION P4 exit 0", flush=True)
    print("PREDICTION P5 every call site carries a kind in %s" % (KINDS,), flush=True)
    print("PREDICTION P6 undecided == 0 on every target", flush=True)
    print("PREDICTION P7 the 3StateClamping original still shows exactly 41 MOTION call sites "
          "(run 2's number; a change here is a FAILED prediction)", flush=True)
    print("PREDICTION P8 per-callee counts unchanged from run 2: MOV 7 / VEL 4 / SetCommand 9 / "
          "ASI Move Axis to Position 4 / GOH 2", flush=True)
    print("NOTE a change in BUCKET LABELS (UNKNOWN -> ASSUMED_MOTION, motion -> "
          "COMMAND/QUERY/CONFIGURE) is the INTENDED effect of the cycle-1 decisions, not a failure",
          flush=True)
    d0 = d0_targets()
    print("D0 claudeDev targets (drive_original_copy.py:89 D0_MAINCOPY_<STAMP>.vi): %s"
          % (d0 if d0 else "NONE EXIST"), flush=True)

    g._lv = None
    _t_start = time.time()
    targets = [("3state-ORIGINAL", ORIG_3STATE), ("v6-workingcopy", ORIG_V6)]
    targets += [("d0-claudedev", p) for p in d0]
    try:
        for tag, p in targets:
            try:
                r = census(p, tag)
            except Exception as e:
                r = {"tag": tag, "vi": p, "exists": os.path.exists(p), "ran": False,
                     "call_sites": [], "by_callee": {}, "errors": ["CENSUS EXC %s" % str(e)[:200]]}
                print("  CENSUS EXC %s" % str(e)[:200], flush=True)
            out["targets"].append(r)
            _dump(out)
        for r in out["targets"]:
            if r["ran"]:
                classify(r)
                _dump(out)
    finally:
        try:
            g.reset()
        except Exception:
            pass

    out["reach_cache"] = {_p: {"reach": _reach.get(_p), "write": _direct.get(_p, {}).get("write"),
                               "diagrams": _direct.get(_p, {}).get("diagrams"),
                               "err": _direct.get(_p, {}).get("err")}
                          for _p in sorted(set(list(_reach) + list(_direct)))}
    out["reach_tested"] = len(_direct)
    out["reach_unknown"] = sum(1 for v in _reach.values() if v is None)

    for tag, p in (("3state", ORIG_3STATE), ("v6", ORIG_V6)):
        out["md5_after"][tag] = md5(p)
    same = all(out["md5_after"][t] == out["md5_before"][t] for t in out["md5_before"])
    out["gates"]["P3_md5_unchanged"] = same

    orig = next((r for r in out["targets"] if r["tag"] == "3state-ORIGINAL"), None)
    def motion(r, dev=None):
        return [c for c in r["call_sites"] if c.get("motion") and (dev is None or c["device"] == dev)]
    out["gates"]["P1_PI"] = bool(orig and orig["ran"] and motion(orig, "PI"))
    out["gates"]["P2_ASI"] = bool(orig and orig["ran"] and motion(orig, "ASI"))

    # --- P5-P8: decisions 1/2 applied everywhere, and the run-2 numbers unmoved -----------------
    ran = [r for r in out["targets"] if r["ran"]]
    out["gates"]["P5_every_site_has_kind"] = bool(ran) and all(
        c.get("kind") in KINDS for r in ran for c in r["call_sites"])
    out["gates"]["P6_undecided_zero"] = bool(ran) and all(
        sum(1 for c in r["call_sites"] if c.get("kind") not in KINDS) == 0 for r in ran)
    out["gates"]["P7_motion_total_41"] = bool(orig and orig["ran"] and len(motion(orig)) == 41)
    RUN2 = {"MOV.vi": 7, "VEL.vi": 4, "SetCommand.vi": 9,
            "Move Axis to Position.vi": 4, "GOH.vi": 2}
    per2 = {}
    for c in (motion(orig) if orig and orig["ran"] else []):
        per2[os.path.basename(c["callee_path"] or c["callee"])] = \
            per2.get(os.path.basename(c["callee_path"] or c["callee"]), 0) + 1
    out["per_callee_3state"] = per2
    out["gates"]["P8_per_callee_unchanged"] = all(per2.get(k) == v for k, v in RUN2.items())
    if not out["gates"]["P8_per_callee_unchanged"]:
        print("P8 DETAIL expected %s got %s" % (RUN2, {k: per2.get(k) for k in RUN2}), flush=True)

    _report(out)
    _dump(out)
    npass = sum(1 for v in out["gates"].values() if v)
    print("SUMMARY %d/%d gates pass: %s" % (npass, len(out["gates"]), out["gates"]), flush=True)
    for k, v in out["gates"].items():
        if not v:
            print("  -> FAIL  %s" % k, flush=True)
    print("CENSUS DONE -> %s" % os.path.join(BENCH, "motor_census_<target>.json"), flush=True)
    return 0 if all(out["gates"].values()) else 2


def _dump(out):
    for r in out["targets"]:
        fn = os.path.join(BENCH, "motor_census_%s.json" % r["tag"])
        with open(fn, "w", encoding="utf-8") as f:
            json.dump({"when": out["when"], "md5_before": out["md5_before"],
                       "md5_after": out["md5_after"], "gates": out["gates"],
                       "reach": out.get("reach_cache", {}), "target": r}, f, indent=1)
    with open(os.path.join(BENCH, "motor_census_all.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=1)


def _report(out):
    for r in out["targets"]:
        print("-" * 78, flush=True)
        print("TARGET %s  exists=%s ran=%s" % (r["tag"], r["exists"], r["ran"]), flush=True)
        if not r["ran"]:
            continue
        mo = [c for c in r["call_sites"] if c.get("motion")]
        dec = [c for c in mo if c["rule"] in ("both", "reachability", "name")]
        print("  call sites %d, motion %d, REACH-COVERAGE %d/%d decided by a completed reachability test"
              % (len(r["call_sites"]), len(mo), len(dec), len(mo)), flush=True)
        per = {}
        for c in mo:
            per.setdefault(os.path.basename(c["callee_path"] or c["callee"]), []).append(c)
        for name in sorted(per):
            rows = per[name]
            print("  %-42s n=%-3d dev=%-7s rules=%s diagrams=%s"
                  % (name, len(rows), rows[0]["device"],
                     sorted({x["rule"] for x in rows}),
                     [x["diagram"] for x in rows]), flush=True)
        for c in mo:
            print("    SITE d%-4d %-18s uid=%-7d %-8s %-13s %s"
                  % (c["diagram"], c["owner_structure"], c["uid"], c["device"], c["rule"],
                     c["callee"]), flush=True)
        unc = [c for c in mo if c["rule"] == "reachability"]
        nmo = [c for c in r["call_sites"] if c["rule"] == "name"]
        nuk = [c for c in r["call_sites"] if c["rule"] == "name_unknown"]
        unk = [c for c in r["call_sites"] if c["rule"] == "unknown"]
        print("  NAME_UNKNOWN (name list, reachability inconclusive): %d" % len(nuk), flush=True)
        for c in nuk:
            print("    NAME_UNKNOWN d%-4d uid=%-7d %s" % (c["diagram"], c["uid"], c["callee"]), flush=True)
        print("  UNCLASSIFIED (reaches a serial write, NOT on the name list): %d" % len(unc), flush=True)
        for c in unc:
            print("    UNCLASSIFIED d%-4d uid=%-7d %s  <- %s"
                  % (c["diagram"], c["uid"], c["callee"], c["callee_path"]), flush=True)
        print("  NAME_ONLY (on the name list, no serial write found): %d" % len(nmo), flush=True)
        for c in nmo:
            print("    NAME_ONLY d%-4d uid=%-7d %s" % (c["diagram"], c["uid"], c["callee"]), flush=True)
        # --- DECISION 1 + 2: the kind table.  Replaces the UNKNOWN bucket entirely. -------------
        kc = {k: [c for c in r["call_sites"] if c.get("kind") == k] for k in KINDS}
        print("  KIND TABLE (decision 1: can this call CHANGE motor state?; decision 2: "
              "untraversable => ASSUMED_MOTION, in scope)", flush=True)
        for k in KINDS:
            print("    %-15s %-3d  in_scope=%s" % (k, len(kc[k]), k in IN_SCOPE_KINDS), flush=True)
        insc = [c for c in r["call_sites"] if c.get("in_scope")]
        undecided = [c for c in r["call_sites"] if c.get("kind") not in KINDS]
        r["kind_counts"] = {k: len(kc[k]) for k in KINDS}
        r["in_scope_total"] = len(insc)
        r["undecided"] = len(undecided)
        print("    IN-SCOPE TOTAL (A/B/C + the approved fixed clamp): %d" % len(insc), flush=True)
        print("    undecided: %d" % len(undecided), flush=True)
        for c in kc["ASSUMED_MOTION"]:
            print("    ASSUMED_MOTION d%-4d uid=%-7d %-38s %s"
                  % (c["diagram"], c["uid"], c["callee"], c.get("assumed_reason", "")[:150]),
                  flush=True)
        if unk and len(unk) != len(kc["ASSUMED_MOTION"]):
            print("    *** rule=='unknown' %d but ASSUMED_MOTION %d - decision 2 not fully applied"
                  % (len(unk), len(kc["ASSUMED_MOTION"])), flush=True)
        # The plan's known candidate for an unlimited position input: the startup ASI move.
        # DIAGRAM-LEVEL CO-OCCURRENCE ONLY - a real backward trace is check A, not this census.
        lim = {c["diagram"] for c in r["call_sites"]
               if os.path.basename(c["callee_path"] or c["callee"]).lower().startswith("max trans pos")}
        print("  diagrams holding `Max Trans Pos.vi` (the original's limit source): %s"
              % sorted(lim), flush=True)
        for c in mo:
            if c["diagram"] not in lim:
                print("    NO-LIMIT-ON-SAME-DIAGRAM d%-4d %-8s uid=%-7d %s"
                      % (c["diagram"], c["device"], c["uid"], c["callee"]), flush=True)
    print("-" * 78, flush=True)
    print("REACH tested=%d unknown=%d budget_left=%.0fs"
          % (out["reach_tested"], out["reach_unknown"], budget_left()), flush=True)
    for tag in out["md5_before"]:
        print("MD5 AFTER %-8s %s  %s" % (tag, out["md5_after"][tag],
              "SAME" if out["md5_after"][tag] == out["md5_before"][tag] else "*** CHANGED ***"),
              flush=True)


if __name__ == "__main__":
    sys.exit(main())
