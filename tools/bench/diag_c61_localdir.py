"""diag_c61_localdir - cycle 61 material #1. A READ (Part A), a PROBE (Part B) and a FILE CENSUS (Part C).

WHAT THIS IS
  `## NEXT` line 79 = docs/cycle27-plan.md Pre-decided 51(h3): a newly created Local Variable is born in
  WRITE mode (`is_source` False) and S3b needs READ. 51(h3) requires TWO things established BEFORE anything
  is built, and the brief adds a THIRD (the prior-art census), because cycle 60's whole waste was a reader
  that `gscript.node_terms` already provided (the standing lesson at 51(h)).

WHAT THIS IS NOT - stated so a later reader never has to infer it
  NOTHING IS BUILT. NO op VI is created, no property chain is spliced into an existing op (51(h): splicing
  is 6 failures / 0 successes in this project's own logs), no `To More Specific Class` cast is made, no VI
  is SAVED (`g.save` is never called), no VI is RUN (34(f)), no GUI action is taken, no new `gscript` verb
  is added, nothing is written under `tools/recipes/`, no new process device (Pre-decided 2). Every probe
  node this run creates on the scratch is DELETED again in the same run, and the scratch itself is deleted.
  NO ROUTE IS CHOSEN OR RECOMMENDED; `docs/cycle27-plan.md` and STATUS's `## NEXT` are not edited.
  Rig state 조립 / ASSEMBLED: no motor, no ASI, no camera (`tools/motor_gate.py` is not called).

WHAT ALREADY EXISTS AND IS REUSED INSTEAD OF REBUILT (checked before writing a line of this file)
  - gscript.node_terms :870 / node_terms_uid :925   the Local-binding + is_source reader (cycle 60's N1/N2)
  - gscript.build_property :2194                    creator; its per-ID tuple is (property_id, is_write)
  - gscript.delete_object :2240, report_all :488, uids :1017, count :1005, exec_state :1977, fp_labels :2440
  - build_d1_v0.diag_index / owner_of               uid -> diagram index / owner, never a remembered number
  - diag_s2_scaffold.fresh                          the pre-batch LabVIEW restart (44(e))
  - hash_probe.probe                                the md5 gates
  - the harness shape (gate/fact/probe/dump/locate/terms_of_uid) is COPIED from
    tools/bench/diag_c60_n4_localbinding.py, which ran 27 pass / 0 fail on 2026-09-21.
  No new tool, no new op, no new verb is needed for any of the three parts.

PREDICTION CONTRACT (machine-checkable; a failed prediction is the peer-review trigger)
  A_1  the three machine-produced JSONs are on disk and parse
  A_2  c53_row_class.json carries EXACTLY the two rows `#10407` t0 and t2 with action `cross-loop:1.2->1.5`
  A_3  for each of those two rows, d1_rewire_sources.json and main_vi_nodeterms.json agree with c53 on the
       terminal's `is_source` and on the far end's uid / terminal name / `is_source`
  A_4  the plan's prose at :1182-1188 and :1283-1290 is QUOTED, not paraphrased; any disagreement with the
       JSONs is REPORTED as "file X says .., file Y says .." and NOT resolved here
  B_0  the scratch opens at ExecState 1 and is byte-identical to D1_s3a_focus_ind.vi at creation
  B_1  node_terms returns exactly ONE named terminal for each of the 8 pre-existing Locals, and the
       is_source split reads 3 True / 5 False (51(h3)'s ground truth, re-confirmed live)
  B_2  build_property('VI Server:Local', [('6355401', True)])  -> error column and terminal table RECORDED
  B_3  the same with is_write False                            -> error column and terminal table RECORDED
  B_4  the same two for the KNOWN-GOOD 6355400 (control: it resolved here as short name `CtrlName`,
       terminal i=4 SOURCE, diag_s3b_l0_localname_run2.log:50-56)
  B_5  every probe node created is DELETED again; the Property census returns to its pre-probe value
  B_6  the ExecState is read before and after every probe and after every delete
  C_1  the direction/read-write-mode census over our own files is reported with file:line hits VERBATIM
  C_2  the property-WRITING ops in this fleet are named with donor and shape, generic vs hard-wired stated
  C_3  archive/peer/ is listed BY FILENAME ONLY for a Local-direction slug (bodies are not read)
  H_1  20 consecutive node_terms calls; handles flat +-100; refs opened == closed, 0 live
  Z_1  four md5 gates PASS before AND after (ORIGINAL FATAL, s1, s2 FATAL, s3a FATAL)
  Z_2  the scratch is deleted in the same run (exists=False) and ARTEFACTS ON DISK is []

NOTHING HERE INTERPRETS A RESULT. The brief is result-independent by construction: it names the
measurements, not the action. Anything that looks like a decision goes into the OPEN line instead.
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
from build_d1_v0 import diag_index, owner_of                                       # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C61DIR_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c61_localdir.json")

LOCAL_CLASS = "VI Server:Local"
PROP_DIRECTION = "6355401"      # 51(h3)'s candidate. docs/cycle27-plan.md:2314-2316. Named `Local.Write?`
                                # by a PEER and flagged UNVERIFIED at tools/bench/diag_s56_transport2.py:91.
PROP_CTRLNAME = "6355400"       # the CONTROL: measured to resolve here as short name `CtrlName`, i=4 SOURCE
                                # (tools/bench/diag_s3b_l0_localname_run2.log:50-56; docs/NAMES.md:260)
PROBE_POS = [(6600, 5600), (6600, 5750), (6900, 5600), (6900, 5750)]

# docs/main-vi-panel-map.md:405 + :409-416, measured 2026-09-14. `Is Source? TRUE = the local is READ,
# FALSE = WRITTEN.` Quoted here ONLY to be compared with what this run reads off the machine.
PANEL_MAP_TABLE = [
    {"uid": 2991,  "control": "Total Lost Frames", "read": False},
    {"uid": 4277,  "control": "File # Saved",      "read": False},
    {"uid": 11574, "control": "Focus Pos (Track)", "read": False},
    {"uid": 3160,  "control": "Rot pos (deg)",     "read": True},
    {"uid": 3097,  "control": "Trans Pos (mm)",    "read": True},
    {"uid": 2143,  "control": "Total Lost Frames", "read": False},
    {"uid": 16942, "control": "Picture",           "read": False},
    {"uid": 25805, "control": "Color table",       "read": True},
]

N_CONSECUTIVE = 20
SCAN_LIMIT = 80

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 61 material #1: (A) the REQUIRED DIRECTION read off the machine-produced row tables, "
             "(B) whether a Local's direction can be WRITTEN at all - PROBE ONLY, (C) a prior-art census "
             "over our own files. docs/cycle27-plan.md Pre-decided 51(h3).",
     "builds_nothing": True, "saves_no_vi": True, "creates_no_op": True, "no_cast": True, "no_splice": True,
     "no_new_verb": True, "no_recipe": True, "no_new_device": True, "no_vi_was_run": True,
     "no_gui_action": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True, "interprets_nothing": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s1_artefact": {"path": S1_ARTEFACT, "md5_pin": S1_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "s3a_artefact": {"path": S3A_ARTEFACT, "md5_pin": S3A_MD5},
     "handles": {}, "hash_probe": [],
     "A_direction": {}, "B_probes": {}, "C_priorart": {}, "H_hygiene": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
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
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def count_of(target, cls):
    try:
        return g.count(target, cls)
    except Exception as e:                                                         # noqa: BLE001
        return "ERROR %s: %s" % (type(e).__name__, str(e)[:80])


def uid_set(target, cls):
    try:
        return set(g.uids(target, cls)), ""
    except Exception as e:                                                         # noqa: BLE001
        return set(), "%s: %s" % (type(e).__name__, str(e)[:200])


def close_quietly(target):
    try:
        g.close_panel(target)
    except Exception as e:                                                         # noqa: BLE001
        fact("close_panel(%s) raised %s: %s" % (os.path.basename(target), type(e).__name__, e))


_LABEL_CACHE = {}


def node_label_rows(target, di, fresh=False):
    """node_labels for ONE diagram. A uid's position here is a CANDIDATE node index - candidate, because
    node_terms_uid echoes the node's own UID and THAT is what verifies it. `fresh` re-reads after an edit."""
    key = (target, int(di))
    if fresh:
        _LABEL_CACHE.pop(key, None)
    if key not in _LABEL_CACHE:
        try:
            _LABEL_CACHE[key] = (g.node_labels(target, int(di)), "")
        except Exception as e:                                                     # noqa: BLE001
            _LABEL_CACHE[key] = ([], "%s: %s" % (type(e).__name__, str(e)[:250]))
    return _LABEL_CACHE[key]


def locate(target, uid, fresh=False):
    """uid -> owner / diagram index / candidate node index, ALL read off the machine. Owner comparisons
    accept BOTH 'Diagram' and 'TopLevelDiagram'."""
    loc = {"uid": uid}
    for strict in (True, False):
        try:
            cls, ouid = owner_of(target, uid, strict=strict)
            loc.update({"owner_strict": strict, "owner_class": cls, "owner_uid": ouid,
                        "owner_error_verbatim": ""})
            break
        except Exception as e:                                                     # noqa: BLE001
            loc.update({"owner_strict": strict, "owner_class": None, "owner_uid": None,
                        "owner_error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:250])})
    if loc.get("owner_class") not in ("Diagram", "TopLevelDiagram"):
        loc["diagram_index"] = None
        loc["why_no_diagram_index"] = ("owner_of answered %r, which is neither 'Diagram' nor "
                                       "'TopLevelDiagram'" % (loc.get("owner_class"),))
        return loc
    try:
        loc["diagram_index"] = diag_index(target, loc["owner_uid"])
    except Exception as e:                                                         # noqa: BLE001
        loc["diagram_index"] = None
        loc["diag_index_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        return loc
    rows, err = node_label_rows(target, loc["diagram_index"], fresh=fresh)
    loc["node_labels_error_verbatim"] = err
    loc["nodes_on_that_diagram"] = len(rows)
    loc["candidate_node_index"] = next((i for i, r in enumerate(rows) if r["uid"] == uid), None)
    loc["node_own_label"] = next((r["label"] for r in rows if r["uid"] == uid), None)
    return loc


def terms_of_uid(target, loc):
    """node_terms on the located node, VERIFIED by the node's own UID; bounded scan fallback."""
    rec = {"diagram_index": loc.get("diagram_index"), "candidate_node_index": loc.get("candidate_node_index")}
    di, uid = loc.get("diagram_index"), loc.get("uid")
    if di is None:
        rec["how"] = "not located"
        return rec
    tries = []
    if loc.get("candidate_node_index") is not None:
        tries.append(int(loc["candidate_node_index"]))
    for n in tries:
        try:
            node_uid, rows = g.node_terms_uid(target, di, n)
        except Exception as e:                                                     # noqa: BLE001
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            continue
        if node_uid == uid:
            rec.update({"how": "node_labels position (verified by the node's own UID)", "node_index": n,
                        "node_uid": node_uid, "terms": rows})
            return rec
        rec.setdefault("rejected", []).append({"n": n, "node_uid_echoed": node_uid})
    scanned = 0
    for n in range(SCAN_LIMIT):
        if n in tries:
            continue
        scanned += 1
        try:
            node_uid, rows = g.node_terms_uid(target, di, n)
        except Exception as e:                                                     # noqa: BLE001
            rec.setdefault("scan_errors", []).append({"n": n, "error_verbatim": str(e)[:160]})
            continue
        if not node_uid:
            break
        if node_uid == uid:
            rec.update({"how": "bounded scan (%d calls)" % scanned, "node_index": n, "node_uid": node_uid,
                        "terms": rows})
            return rec
    rec["how"] = "NOT FOUND (candidate rejected, bounded scan of %d nodes did not echo the uid)" % scanned
    return rec


def term_rows_verbatim(terms):
    return [{"i": t["i"], "name": t["name"], "name_hex": (t["name"] or "").encode("utf-8").hex(),
             "is_source": t["is_source"], "wire": t["wire"],
             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]} for t in terms]


# ============================================================ PART A - files only, no LabVIEW
def part_a(K):
    print("\n========== PART A  the REQUIRED DIRECTION, off the machine-produced tables only", flush=True)
    paths = {"c53_row_class": os.path.join(HERE, "c53_row_class.json"),
             "d1_rewire_sources": os.path.join(HERE, "d1_rewire_sources.json"),
             "main_vi_nodeterms": os.path.join(HERE, "main_vi_nodeterms.json")}
    K["sources"] = paths
    data = {}
    for k, p in paths.items():
        try:
            with open(p, encoding="utf-8") as f:
                data[k] = json.load(f)
            K.setdefault("loaded", {})[k] = True
        except Exception as e:                                                     # noqa: BLE001
            data[k] = None
            K.setdefault("loaded", {})[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    gate("A_1 the three machine-produced JSONs are on disk and parse",
         all(v is True for v in K["loaded"].values()), repr(K["loaded"]), fatal=True)

    def dicts_matching(obj, pred):
        """Every dict ANYWHERE in the JSON for which pred() is true - so the row list is found by its
        CONTENT, never by a remembered key name or index."""
        out = []

        def walk(o):
            if isinstance(o, dict):
                try:
                    if pred(o):
                        out.append(o)
                except Exception:                                                  # noqa: BLE001
                    pass
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(obj)
        return out

    c53 = dicts_matching(data["c53_row_class"],
                         lambda r: r.get("owner_uid") == 10407 and r.get("terminal_index") in (0, 2))
    K["c53_rows_verbatim"] = c53
    gate("A_2 c53_row_class.json carries exactly the two rows #10407 t0 and t2", len(c53) == 2,
         "found %d; indices %r" % (len(c53), [r.get("terminal_index") for r in c53]), fatal=True)
    for r in c53:
        fact("A_2 c53_row_class.json  #10407 t%s name=%r is_source=%r (%s) wire=%r action=%r dest_row=%r "
             "far_end=%r construction_verb=%r"
             % (r.get("terminal_index"), r.get("terminal_name"), r.get("is_source"),
                r.get("source_or_sink"), r.get("wire"), r.get("action_verbatim"), r.get("dest_row"),
                r.get("other_end"), r.get("construction_verb")))

    rw = dicts_matching(data["d1_rewire_sources"],
                        lambda r: r.get("uid") == 10407 and r.get("i") in (0, 2) and "action" in r)
    K["rewire_rows_verbatim"] = rw
    gate("A_2b d1_rewire_sources.json carries exactly the two rows #10407 t0 and t2", len(rw) == 2,
         "found %d; indices %r" % (len(rw), [r.get("i") for r in rw]), fatal=True)
    for r in rw:
        fact("A_3 d1_rewire_sources.json  #10407 t%s name=%r is_source=%r wire=%r action=%r source=%r"
             % (r.get("i"), r.get("name"), r.get("is_source"), r.get("wire"), r.get("action"),
                r.get("source")))

    # main_vi_nodeterms.json - the third, independent census. Find #10407 / #10686 / #10757 by uid.
    def node_by_uid(obj, uid):
        found = []

        def walk(o):
            if isinstance(o, dict):
                if o.get("uid") == uid and isinstance(o.get("terms"), list):
                    found.append(o)
                for v in o.values():
                    walk(v)
            elif isinstance(o, list):
                for v in o:
                    walk(v)
        walk(obj)
        return found[0] if found else None

    nt = {}
    for uid in (10407, 10686, 10757):
        n = node_by_uid(data["main_vi_nodeterms"], uid)
        nt[uid] = ({"uid": uid, "terms": [{"i": t.get("i"), "name": t.get("name"),
                                           "is_source": t.get("is_source"), "wire": t.get("wire")}
                                          for t in n["terms"]]} if n else None)
    K["nodeterms_verbatim"] = nt
    gate("A_3a main_vi_nodeterms.json carries #10407, #10686 and #10757",
         all(nt[u] for u in (10407, 10686, 10757)),
         repr({u: (len(nt[u]["terms"]) if nt[u] else None) for u in nt}))

    pairs = []
    for ti, far_uid, far_i in ((0, 10686, 0), (2, 10757, 1)):
        sink = next((t for t in (nt[10407]["terms"] if nt[10407] else []) if t["i"] == ti), None)
        src = next((t for t in (nt[far_uid]["terms"] if nt[far_uid] else []) if t["i"] == far_i), None)
        pairs.append({"sink_node": 10407, "sink_i": ti, "sink_row": sink,
                      "far_node": far_uid, "far_i": far_i, "far_row": src})
        fact("A_3b nodeterms  SINK #10407 t%s = %r   <-   FAR END #%s t%s = %r"
             % (ti, sink, far_uid, far_i, src))
    K["the_two_rows"] = pairs

    # cross-census agreement, stated as an agreement/disagreement REPORT, never resolved here
    agree = []
    for p, c, w in zip(pairs, sorted(c53, key=lambda r: r["terminal_index"]),
                       sorted(rw, key=lambda r: r["i"])):
        a = {"terminal_index": p["sink_i"],
             "c53_is_source": c.get("is_source"), "rewire_is_source": w.get("is_source"),
             "nodeterms_is_source": (p["sink_row"] or {}).get("is_source"),
             "c53_far": (c.get("other_end") or [{}])[0], "rewire_far": w.get("source"),
             "nodeterms_far_is_source": (p["far_row"] or {}).get("is_source"),
             "wire_c53": c.get("wire"), "wire_rewire": w.get("wire"),
             "wire_nodeterms": (p["sink_row"] or {}).get("wire")}
        a["all_three_agree_on_sink_is_source"] = (a["c53_is_source"] == a["rewire_is_source"]
                                                  == a["nodeterms_is_source"])
        a["all_three_agree_on_wire"] = (a["wire_c53"] == a["wire_rewire"] == a["wire_nodeterms"])
        agree.append(a)
        fact("A_3c AGREEMENT t%s: is_source c53=%r rewire=%r nodeterms=%r (agree=%r) ; wire %r/%r/%r "
             "(agree=%r) ; far end is_source per nodeterms=%r"
             % (a["terminal_index"], a["c53_is_source"], a["rewire_is_source"], a["nodeterms_is_source"],
                a["all_three_agree_on_sink_is_source"], a["wire_c53"], a["wire_rewire"],
                a["wire_nodeterms"], a["all_three_agree_on_wire"], a["nodeterms_far_is_source"]))
    K["cross_census_agreement"] = agree
    gate("A_3 the three censuses agree on both rows' is_source and wire",
         all(a["all_three_agree_on_sink_is_source"] and a["all_three_agree_on_wire"] for a in agree),
         repr([(a["terminal_index"], a["all_three_agree_on_sink_is_source"], a["all_three_agree_on_wire"])
               for a in agree]))

    # the plan's prose, QUOTED not paraphrased
    plan = os.path.join(ROOT, "docs", "cycle27-plan.md")
    quoted = {}
    try:
        lines = open(plan, encoding="utf-8").read().splitlines()
        quoted["1182-1188"] = lines[1181:1188]
        quoted["1283-1290"] = lines[1282:1290]
    except Exception as e:                                                         # noqa: BLE001
        quoted["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
    K["plan_prose_quoted_verbatim"] = quoted
    gate("A_4 the plan's prose at :1182-1188 and :1283-1290 was QUOTED into the JSON, not paraphrased",
         "error_verbatim" not in quoted, "%d + %d lines"
         % (len(quoted.get("1182-1188", [])), len(quoted.get("1283-1290", []))))

    # the ONE derived statement Part A is allowed to make: it restates the flags, it does not argue.
    K["statement_from_the_flags_alone"] = [
        {"row": "#10407 t%s" % p["sink_i"],
         "terminal_index_on_10407": p["sink_i"],
         "is_source_as_the_census_records_it": (p["sink_row"] or {}).get("is_source"),
         "therefore_that_terminal_is": ("SOURCE" if (p["sink_row"] or {}).get("is_source") else "SINK"),
         "far_end_node": p["far_node"], "far_end_terminal_name": (p["far_row"] or {}).get("name"),
         "far_end_is_source": (p["far_row"] or {}).get("is_source"),
         "therefore_the_far_end_is": ("SOURCE" if (p["far_row"] or {}).get("is_source") else "SINK"),
         "so_a_local_taking_over_this_feed_sits_at_the_far_end_and_must_be":
             ("SOURCE (= READ, per docs/main-vi-panel-map.md:405 'Is Source? TRUE = the local is READ')"
              if (p["far_row"] or {}).get("is_source")
              else "SINK (= WRITE, per docs/main-vi-panel-map.md:405)"),
         "quoted_flag_values_only": True}
        for p in pairs]
    for s in K["statement_from_the_flags_alone"]:
        fact("A_4b FROM THE FLAGS ALONE  %s: is_source=%r -> %s ; far end #%s %r is_source=%r -> %s ; "
             "the Local replacing that feed must be %s"
             % (s["row"], s["is_source_as_the_census_records_it"], s["therefore_that_terminal_is"],
                s["far_end_node"], s["far_end_terminal_name"], s["far_end_is_source"],
                s["therefore_the_far_end_is"],
                s["so_a_local_taking_over_this_feed_sits_at_the_far_end_and_must_be"]))
    dump()


# ============================================================ PART C - files only, no LabVIEW
def part_c(K):
    print("\n========== PART C  prior-art census over our OWN files (no LabVIEW)", flush=True)

    def grep(path, pattern, flags=re.I):
        hits = []
        try:
            for i, ln in enumerate(open(path, encoding="utf-8", errors="replace").read().splitlines(), 1):
                if re.search(pattern, ln, flags):
                    hits.append({"file": os.path.relpath(path, ROOT).replace("\\", "/"),
                                 "line": i, "text": ln.strip()[:300]})
        except Exception as e:                                                     # noqa: BLE001
            hits.append({"file": path, "line": None, "text": "ERROR %s: %s" % (type(e).__name__, e)})
        return hits

    # --- C1: does anything already READ or WRITE a Local's direction / read-write mode?
    pat = r"6355401|Local\.Write|Write\?|local.{0,20}(direction|read/write|read-write)|" \
          r"(direction|read/write|read-write).{0,20}local"
    c1_files = [os.path.join(ROOT, "tools", "gscript.py"),
                os.path.join(ROOT, "docs", "toolkit-capabilities.md"),
                os.path.join(ROOT, "docs", "NAMES.md"),
                os.path.join(ROOT, "docs", "main-vi-panel-map.md")]
    c1 = []
    for p in c1_files:
        c1 += grep(p, pat)
    rec_dir = os.path.join(ROOT, "tools", "recipes")
    for fn in sorted(os.listdir(rec_dir)):
        if fn.endswith(".py"):
            c1 += grep(os.path.join(rec_dir, fn), pat)
    K["C1_local_direction_hits"] = c1
    for h in c1:
        fact("C1 %s:%s  %s" % (h["file"], h["line"], h["text"]))
    if not c1:
        fact("C1 NONE FOUND - no file among tools/gscript.py, docs/toolkit-capabilities.md, docs/NAMES.md, "
             "docs/main-vi-panel-map.md, tools/recipes/*.py mentions a Local's direction / read-write mode")
    gate("C1 the Local-direction census over our own files ran and its hits are recorded verbatim",
         True, "%d hit(s)" % len(c1))

    # the claudeDev op VI names (a files-level fact: is there an Op*Local* / Op*Dir* / Op*Mode* at all?)
    try:
        ops = sorted(f for f in os.listdir(g.CLAUDEDEV) if f.lower().endswith(".vi"))
    except Exception as e:                                                         # noqa: BLE001
        ops = ["ERROR %s: %s" % (type(e).__name__, str(e)[:200])]
    K["claudedev_vi_names"] = ops
    interesting = [o for o in ops if re.search(r"local|dir|mode|write|name", o, re.I)]
    K["claudedev_names_matching_local_dir_mode_write_name"] = interesting
    fact("C1b claudeDev holds %d .vi; those whose NAME matches local|dir|mode|write|name: %r"
         % (len(ops), interesting))

    # --- C2: which op VIs WRITE a property?
    src = open(os.path.join(ROOT, "tools", "gscript.py"), encoding="utf-8").read()
    writers = []
    fn_pat = re.compile(r"^def\s+(\w+)\(", re.M)
    lines = src.splitlines()
    for m in fn_pat.finditer(src):
        name = m.group(1)
        start = src[:m.start()].count("\n")
        body = "\n".join(lines[start:start + 40])
        if not re.search(r"\bset_|write|Write", name + body):
            continue
        opref = re.findall(r"op\((OP_[A-Z0-9_]+)\)", body)
        if not opref:
            continue
        opname = re.findall(r"^%s\s*=\s*os\.path\.join\(CLAUDEDEV,\s*\"([^\"]+)\"\)" % opref[0], src, re.M)
        writers.append({"verb": name, "gscript_line": start + 1, "op_constant": opref[0],
                        "op_vi": opname[0] if opname else None,
                        "first_docline": next((l.strip() for l in lines[start:start + 6]
                                               if '"""' in l), "")[:240]})
    K["C2_property_writer_verbs"] = writers
    for w in writers:
        fact("C2 %s (tools/gscript.py:%d) -> %s   %s"
             % (w["verb"], w["gscript_line"], w["op_vi"], w["first_docline"]))
    # is ANY of them generic (class + property id taken as arguments)?
    generic = []
    for w in writers:
        start = w["gscript_line"] - 1
        body = "\n".join(lines[start:start + 40])
        if re.search(r"Class Name 3|props|property_unique_id|Properties", body):
            generic.append(w["verb"])
    K["C2_generic_property_writers"] = generic
    fact("C2b of those, the ones whose body passes a CLASS + PROPERTY-ID pair generically: %r "
         "(build_property is the generic CREATOR, tools/gscript.py:2194 - creating a node is not writing "
         "a property value)" % (generic,))
    gate("C2 the property-writing ops are enumerated with their op VI", bool(writers),
         "%d writer verb(s)" % len(writers))

    # --- C3: has this been asked of a peer? FILENAMES ONLY - bodies are NOT read.
    pdir = os.path.join(ROOT, "archive", "peer")
    try:
        names = sorted(os.listdir(pdir))
    except Exception as e:                                                         # noqa: BLE001
        names = ["ERROR %s: %s" % (type(e).__name__, str(e)[:200])]
    match = [n for n in names if re.search(r"local|direction|read-?write|write-?mode", n, re.I)]
    K["C3_peer_filenames_matching"] = match
    K["C3_peer_total_files"] = len(names)
    K["C3_bodies_read"] = False
    fact("C3 archive/peer/ holds %d files; FILENAMES matching local|direction|read-write|write-mode: %r "
         "(bodies NOT read)" % (len(names), match))
    gate("C3 archive/peer was listed by filename only and no body was read", True, "%d match(es)" % len(match))
    dump()


# ============================================================ PART B - the probes, on the scratch
def b_preexisting(K):
    print("\n---------- B4  node_terms on the 8 pre-existing Locals (51(h3)'s 3 READ / 5 WRITE, live)",
          flush=True)
    uids_now, err = uid_set(SCRATCH, "Local")
    K["local_uids_on_the_scratch"] = sorted(uids_now)
    K["uids_error_verbatim"] = err
    fact("B4 `Local` uids on the scratch: %r (census %r)" % (sorted(uids_now), count_of(SCRATCH, "Local")))
    readings = []
    for row in PANEL_MAP_TABLE:
        loc = locate(SCRATCH, row["uid"])
        tr = terms_of_uid(SCRATCH, loc)
        terms = tr.get("terms") or []
        rd = {"uid": row["uid"], "doc_control": row["control"], "doc_read": row["read"],
              "diagram_index": loc.get("diagram_index"), "node_index": tr.get("node_index"),
              "how": tr.get("how"), "n_terminals": len(terms),
              "terminal_rows_verbatim": term_rows_verbatim(terms),
              "terminal_name": terms[0]["name"] if len(terms) == 1 else None,
              "is_source": terms[0]["is_source"] if len(terms) == 1 else None,
              "wire": terms[0]["wire"] if len(terms) == 1 else None}
        rd["agrees_with_doc"] = (rd["terminal_name"] == row["control"]
                                 and rd["is_source"] == row["read"])
        readings.append(rd)
        fact("B4 Local #%s -> %d terminal(s); name %r, is_source %r (doc says control %r, READ %r) -> %s"
             % (rd["uid"], rd["n_terminals"], rd["terminal_name"], rd["is_source"], row["control"],
                row["read"], "AGREE" if rd["agrees_with_doc"] else "DIFFER"))
    K["readings"] = readings
    n_src = sum(1 for r in readings if r["is_source"] is True)
    n_sink = sum(1 for r in readings if r["is_source"] is False)
    K["is_source_split"] = {"True_READ": n_src, "False_WRITE": n_sink}
    fact("B4 the live is_source split over the 8 pre-existing Locals: True(READ)=%d False(WRITE)=%d"
         % (n_src, n_sink))
    gate("B_1 each of the 8 pre-existing Locals returns exactly ONE named terminal",
         all(r["n_terminals"] == 1 and r["terminal_name"] for r in readings),
         repr([(r["uid"], r["n_terminals"]) for r in readings]))
    gate("B_1b the live is_source split reads 3 READ / 5 WRITE, as 51(h3) states",
         n_src == 3 and n_sink == 5, "True=%d False=%d" % (n_src, n_sink))
    gate("B_1c every reading agrees with docs/main-vi-panel-map.md:409-416",
         all(r["agrees_with_doc"] for r in readings),
         repr([r["uid"] for r in readings if not r["agrees_with_doc"]]))
    return readings


def one_probe(K, pid, is_write, pos, tag):
    """Create ONE property node for (pid, is_write), read EVERYTHING off it, then DELETE it again."""
    print("\n---------- %s  build_property(%r, [(%r, %r)]) at %r" % (tag, LOCAL_CLASS, pid, is_write, pos),
          flush=True)
    rec = {"tag": tag, "class_string_verbatim": LOCAL_CLASS, "property_id": pid, "is_write_flag": is_write,
           "position": list(pos), "builds_nothing_permanent": True}
    rec["property_census_before"] = count_of(SCRATCH, "Property")
    before, _e = uid_set(SCRATCH, "Property")
    read_exec_state(rec, "%s before the probe" % tag, SCRATCH)
    try:
        new = g.build_property(SCRATCH, LOCAL_CLASS, [(pid, is_write)], pos)
        rec["resolves"] = True
        rec["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
        rec["error_column_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["resolves"] = False
        rec["new"] = None
        rec["error_column_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:800])
    after, _e2 = uid_set(SCRATCH, "Property")
    rec["property_census_after"] = count_of(SCRATCH, "Property")
    rec["property_uid_delta"] = sorted(after - before)
    fact("%s resolves=%r ; error column VERBATIM %r ; new %r ; Property census %r -> %r"
         % (tag, rec["resolves"], rec["error_column_verbatim"], rec["new"],
            rec["property_census_before"], rec["property_census_after"]))
    read_exec_state(rec, "%s after the probe node was created" % tag, SCRATCH)

    rec["terminal_tables"] = []
    for uid in rec["property_uid_delta"]:
        loc = locate(SCRATCH, uid, fresh=True)
        tr = terms_of_uid(SCRATCH, loc)
        terms = tr.get("terms") or []
        rows = term_rows_verbatim(terms)
        extra = [r for r in rows
                 if r["name"] not in ("reference", "reference out", "error in (no error)", "error out")]
        entry = {"uid": uid, "diagram_index": loc.get("diagram_index"), "node_index": tr.get("node_index"),
                 "how": tr.get("how"), "full_terminal_table_verbatim": rows,
                 "rows_beyond_the_standard_four": extra,
                 "resolved_short_names": [r["name"] for r in extra],
                 "sink_rows_beyond_the_standard_four": [r for r in extra if r["is_source"] is False],
                 "source_rows_beyond_the_standard_four": [r for r in extra if r["is_source"] is True]}
        rec["terminal_tables"].append(entry)
        fact("%s Property #%s at diagram %r node %r [%s] FULL TERMINAL TABLE: %r"
             % (tag, uid, entry["diagram_index"], entry["node_index"], entry["how"], rows))
        fact("%s rows BEYOND reference/reference out/error in/error out = %r ; resolved short name(s) %r ; "
             "of those, SINK rows (a value could be written into one) = %r"
             % (tag, extra, entry["resolved_short_names"], entry["sink_rows_beyond_the_standard_four"]))

    # --- delete every probe node again
    rec["deleted"] = []
    for uid in rec["property_uid_delta"]:
        try:
            cur = [o["uid"] for o in g.report_all(SCRATCH, "Property")]
            gone = g.delete_object(SCRATCH, "Property", cur.index(uid))
            rec["deleted"].append({"uid": uid, "gone": gone, "error_verbatim": ""})
            fact("%s probe node #%s DELETED again -> gone %r" % (tag, uid, gone))
        except Exception as e:                                                     # noqa: BLE001
            rec["deleted"].append({"uid": uid, "gone": None,
                                   "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:300])})
            fact("%s deleting probe node #%s raised %s: %s" % (tag, uid, type(e).__name__, str(e)[:200]))
    rec["property_census_after_delete"] = count_of(SCRATCH, "Property")
    read_exec_state(rec, "%s after the probe node was deleted" % tag, SCRATCH)
    rec["census_returned"] = rec["property_census_after_delete"] == rec["property_census_before"]
    fact("%s Property census after delete %r (pre-probe %r) -> returned=%r"
         % (tag, rec["property_census_after_delete"], rec["property_census_before"], rec["census_returned"]))
    K.setdefault("probes", []).append(rec)
    gate("%s the probe was made and its error column / terminal table / ExecState are recorded" % tag,
         "resolves" in rec, "resolves=%r error=%r" % (rec["resolves"], rec["error_column_verbatim"][:120]))
    gate("%s every probe node created was DELETED again and the Property census returned" % tag,
         rec["census_returned"], "%r -> %r -> %r" % (rec["property_census_before"],
                                                     rec["property_census_after"],
                                                     rec["property_census_after_delete"]))
    return rec


def hygiene(K, readings):
    print("\n---------- H  %d consecutive node_terms calls (handles +-100, refs 0 live)" % N_CONSECUTIVE,
          flush=True)
    anchor = next((r for r in (readings or []) if r.get("node_index") is not None), None)
    if not anchor:
        K["skipped"] = "no located Local to call repeatedly"
        gate("H_1 the hygiene block ran", False, "no anchor")
        return
    di, ni, uid = anchor["diagram_index"], anchor["node_index"], anchor["uid"]
    h0 = labview_handles()
    r0 = g.ref_counts()
    t0 = time.time()
    echoed = []
    for _ in range(N_CONSECUTIVE):
        try:
            nu, _rows = g.node_terms_uid(SCRATCH, di, ni)
            echoed.append(nu)
        except Exception as e:                                                     # noqa: BLE001
            echoed.append("ERROR %s" % type(e).__name__)
    dt = time.time() - t0
    h1 = labview_handles()
    r1 = g.ref_counts()
    K.update({"anchor_uid": uid, "diagram_index": di, "node_index": ni, "echoed": echoed,
              "seconds": round(dt, 2), "handles_before": h0, "handles_after": h1,
              "refs_before": r0, "refs_after": r1})
    fact("H %d calls in %.1f s; all echoed uid #%s: %r ; handles %r -> %r ; refs %r -> %r"
         % (N_CONSECUTIVE, dt, uid, all(e == uid for e in echoed), h0, h1, r0, r1))
    try:
        flat = abs(int(h1) - int(h0)) <= 100
    except Exception:                                                              # noqa: BLE001
        flat = False
    gate("H_1 %d consecutive node_terms calls ran and all echoed the anchor uid" % N_CONSECUTIVE,
         all(e == uid for e in echoed), repr(echoed[:5]))
    gate("H_1b the handle count is flat within +-100 across the %d calls" % N_CONSECUTIVE, flat,
         "%r -> %r" % (h0, h1))


def part_b():
    print("\n========== PART B  can a Local's direction be WRITTEN at all? PROBE ONLY, BUILD NOTHING",
          flush=True)
    K = R["B_probes"]
    es0 = read_exec_state(K, "the scratch, before any call", SCRATCH)
    gate("B_0 the scratch opens at ExecState 1", es0 == 1, "%r" % (es0,))
    readings = b_preexisting(K.setdefault("B4_preexisting", {}))
    one_probe(K, PROP_DIRECTION, True, PROBE_POS[0], "B_2 6355401 write=True")
    one_probe(K, PROP_DIRECTION, False, PROBE_POS[1], "B_3 6355401 write=False")
    one_probe(K, PROP_CTRLNAME, True, PROBE_POS[2], "B_4a 6355400 write=True (the CONTROL)")
    one_probe(K, PROP_CTRLNAME, False, PROBE_POS[3], "B_4b 6355400 write=False (the CONTROL)")
    hygiene(R["H_hygiene"], readings)
    fact("the scratch was NEVER SAVED (g.save is not called on it) and is deleted below.")
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c61_localdir  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== A: the required DIRECTION off the machine tables | B: can the direction be WRITTEN (probe "
          "only) | C: prior-art census", flush=True)
    print("=== NOTHING IS BUILT, NOTHING IS SAVED, NO VI IS RUN, NO OP VI IS CREATED OR SPLICED", flush=True)

    # --- Parts A and C need no LabVIEW at all: run them first, so they land even if COM misbehaves.
    try:
        part_a(R["A_direction"])
    except Stop as s:
        R["stopped_at_part_a"] = str(s)
        fact("PART A STOPPED: %s" % s)
    try:
        part_c(R["C_priorart"])
    except Exception as e:                                                         # noqa: BLE001
        R["C_priorart"]["raised"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("PART C RAISED %s: %s" % (type(e).__name__, str(e)[:300]))
    dump()

    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 the S3a artefact (the bed's SOURCE, never the bed)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    p = probe("B_0b the scratch at creation", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "at_creation": p}
    gate("B_0b the scratch copy is byte-identical to D1_s3a_focus_ind.vi at creation",
         p.get("md5") == S3A_MD5, "%s (expected %s)" % (p.get("md5", "?"), S3A_MD5))

    try:
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        part_b()
    except Stop as s:
        R["stopped_at"] = str(s)
        fact("STOPPED: %s" % s)
    except Exception as e:                                                         # noqa: BLE001
        R["stopped_at"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("RAISED %s: %s" % (type(e).__name__, str(e)[:600]))
    finally:
        close_quietly(SCRATCH)
    dump()

    # ---- Z: the closing facts
    print("\n--- Z: the closing facts", flush=True)
    removed = None
    if os.path.exists(SCRATCH):
        try:
            os.remove(SCRATCH)
            removed = True
        except Exception as e:                                                     # noqa: BLE001
            removed = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    R["scratch_removed"] = removed
    gate("Z_2 the scratch was DELETED in the same run", not os.path.exists(SCRATCH),
         "removed=%r, exists=%r" % (removed, os.path.exists(SCRATCH)))

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
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1b refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    gate("Z_1c no file was created under tools/recipes/ by this run", True,
         "this diagnostic writes only tools/bench/diag_c61_localdir.{log,json} and the scratch it deletes")
    fact("ARTEFACTS ON DISK: [] (this run builds and saves nothing; every probe node and the scratch "
         "are deleted)")

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
