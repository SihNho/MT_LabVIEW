r"""diag_queue_trial_census - Pre-decided 36(d): THE TRIAL CENSUS. "The donor is found BY CONSTRUCTION."

🔴 A DIAGNOSTIC under `tools/bench/`, NEVER a recipe and never to be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND PICKS NOTHING. 35(b)/36(d) reserve the choice of donor - and the writing of any queue
   stage - for the judgement session. Nothing here is a recommendation.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53). No motor, no ASI, no camera, no GUI action.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are NEVER opened for writing; their
   md5s are probed before and after. Every edit happens on a DATED SCRATCH copy of the S2 artefact.
🔴 `#637`'s outer terminals are BANNED as donors (35(a)) even though 36(a) measured them ACCEPTED. A FATAL gate
   below asserts uid 637 is absent from the donor list before a single attempt is made.

THE QUESTION (36(c)+36(d) verbatim). No built op reads `Terminal.DataType` and Pre-decided 2 forbids building
one, so a terminal's TYPE is measured BY CONSTRUCTION: `queue_node('obtain')` either accepts a donor or refuses
it, and what it creates is read back with ops that already exist. For each of the **18 nodes measured
independent of `#637`** (36(c)) and for EACH of that node's NAMED OUTPUT TERMINALS:
  1. attempt `queue_node('obtain')`;
  2. record ACCEPTED or REFUSED with the machine's VERBATIM error text and number;
  3. on acceptance record the created node's uid and everything the fleet CAN read - `node_terms`
     (name / is_source / wire per terminal) and `report_all` (class / uid / position / owner);
  4. record whether the scratch's `ExecState` changed across the attempt.

🔴 THE THING THIS RUN IS REALLY FOR, stated up front so it cannot be buried: 36(d) ASSUMES "a created
`Obtain Queue` can be read back". **This script MEASURES whether two acceptances on differently-typed donors are
DISTINGUISHABLE by any built op at all, or whether they read identically.** If they read identically that is the
first-class result, and a long acceptance table is the less useful half of this run.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `gscript.queue_node` `:1122` - the thing under test (unchanged). `gscript.report_all` `:488`,
    `node_terms`/`node_terms_uid` `:870`/`:925`, `uids`/`new_since` `:1017`/`:1024`, `count` `:1005`,
    `node_labels` `:587`, `exec_state` `:1977`, `save` `:2062`, `open_panel`/`close_panel`, `ref_counts`, `reset`.
  * `diag_queue_donor.attempt` `:185` - the ATTEMPT PATTERN (before/after Function uid sets; "accepted" means a
    node EXISTS, never that a call returned). Re-implemented here with the readback 36(d) asks for.
  * `diag_donor_census` - the SOURCE OF THE NODE LIST: `tools/bench/diag_donor_census.json` B3
    `independent_uids` and B1 `named_output_terminals`. Re-read LIVE here too (34(h)) and any difference is
    REPORTED, never silently preferred.
  * `diag_s2_scaffold.fresh` `:155` / `Preload` `:167` / `file_facts` `:142`; `build_d1_v0.diag_index` `:357` /
    `owner_of` `:338`; `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147`; `hash_probe.probe` (34(k));
    `bench_prep.labview_handles`.
Nothing new is built.

PREDICTION CONTRACT - every line below is a printed GATE, and **gates are REPORTED, not required** (the 34(j)
pattern of `diag_destidx_drift.py`): the READING is the deliverable, so only the file-safety gates are FATAL.
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                          FATAL
  T2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                              FATAL
  T3  the dated scratch is byte-identical to it.                                                       FATAL
  T4  uid 637 is ABSENT from the donor list (35(a)'s ban, enforced before any attempt).                 FATAL
  T5  the live walk of `Diagram #686` finds all 18 independent nodes of 36(c).                       REPORTED
  T6  the live named-output-terminal list equals `diag_donor_census.json`'s, node for node.          REPORTED
  T7  every donor is ATTEMPTED and SCORED (this asserts the attempt was made, not its outcome).      REPORTED
  T8  the baseline donor (#8486 'x+1', 36(a)'s measured ACCEPTED pair) is accepted - if it is not,
      no later refusal means anything and the log says so.                                           REPORTED
  T9  every acceptance is READ BACK: node_terms rows AND a report_all row.                           REPORTED
  T10 THE DISTINGUISHABILITY READING: the number of DISTINCT readable signatures across the
      acceptances is recorded. 1 distinct signature = indistinguishable by the built fleet.          REPORTED
  T11 `ExecState` before / after every attempt is recorded (any value legitimate).                   REPORTED
  T12 the save attempt is recorded, `allow_broken` stays False and `gui_save` is never called.       REPORTED
  T13 no live VI Server reference is left open.                                                      REPORTED
  T14 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are byte-unchanged at the end.                     FATAL

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_queue_trial_census.log \
      -- py -u tools/bench/diag_queue_trial_census.py
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
from build_d1_v0 import diag_index, owner_of                                      # noqa: E402
from build_opstopfromnode_v0 import walk as WALK, cls_of                          # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_queue_trial_census.json")
CENSUS_JSON = os.path.join(HERE, "diag_donor_census.json")

SIBLING_DIAG_UID = 686
FRAME_LOOP_UID = 637                      # 35(a): BANNED as a donor. Never attempted.
BASELINE_DONOR = (8486, "x+1")            # 36(a)'s measured ACCEPTED pair
# 36(c), verbatim, in that order. NOT re-derived (the brief forbids re-deriving it).
INDEPENDENT_UIDS = [8486, 7201, 781, 250, 6951, 6409, 8953, 9342, 9179, 28124, 27605, 28670,
                    25380, 25091, 25149, 23032, 10170, 23041]
# Traverse classes pre-censused once so a donor's addressable class is RESOLVED by membership, never guessed
# from its label (cls_of calls `#25380 'While Loop'` a "Function", which report_all may not agree with).
PROBE_CLASSES = ("Function", "SubVI", "Property", "Invoke", "IndexArray", "WhileLoop", "ForLoop", "Node")
MAX_RESTARTS = 2

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "Pre-decided 36(d): the queue-donor TRIAL CENSUS over the 18 nodes independent of #637",
     "no_vi_was_run": True, "picks_nothing": True, "no_new_op": True,
     "banned_donor_uid": FRAME_LOOP_UID, "independent_uids_36c": INDEPENDENT_UIDS,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratches": [], "donors": [], "attempts": [], "acceptances": [], "distinguishability": {},
     "exec_state": {}, "censuses": {}, "handles": {}, "hash_probe": [], "restarts": 0}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
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


def census(tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire", "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                    # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    R["censuses"][tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                        # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R["exec_state"].setdefault("timeline", []).append({"tag": tag, "value": es})
    return es


def class_membership(target):
    """uid -> the Traverse classes that CONTAIN it, measured once. No guessing from labels."""
    sets = {}
    for cls in PROBE_CLASSES:
        try:
            sets[cls] = {o["uid"] for o in g.report_all(target, cls)}
        except Exception as e:                                                    # noqa: BLE001
            sets[cls] = None
            fact("Traverse class %r is NOT readable on this target: %s: %s" % (cls, type(e).__name__,
                                                                               str(e)[:120]))
    return sets


def class_index(target, cls, uid):
    return [o["uid"] for o in g.report_all(target, cls)].index(uid)


def scan_nodes_from(target, d686, n_from, span=40):
    """Nodes[] of Diagram #686 from index `n_from` upward - the cheap way to find a node LabVIEW appended
    (gscript.py:2353-2356: new nodes go to the END of Nodes[]). Returns {uid: (node_index, rows)}, next index."""
    out, n = {}, n_from
    while n < n_from + span:
        try:
            u, rows = g.node_terms_uid(target, d686, n)
        except Exception as e:                                                    # noqa: BLE001
            fact("Nodes[%d] scan raised %s: %s" % (n, type(e).__name__, str(e)[:120]))
            break
        if not u:
            break
        out[u] = (n, rows)
        n += 1
    return out, n


def signature(rec):
    """Everything the BUILT fleet can read about a created node, canonicalised so two acceptances can be
    compared field for field. `wire` is excluded: every created node here is unwired, so it carries no
    information; it is kept in the record itself."""
    terms = tuple((t["i"], t["name"], bool(t["is_source"])) for t in (rec.get("node_terms") or []))
    ra = rec.get("report_all_row") or {}
    return json.dumps({"class": ra.get("class"), "owner": ra.get("owner"), "label": rec.get("label"),
                       "n_terms": len(terms), "terms": terms}, sort_keys=True, default=str)


def make_scratch(tag):
    path = os.path.join(g.CLAUDEDEV, "DIAG_qtrial_%s_%d.vi" % (STAMP, len(R["scratches"]) + 1))
    if os.path.exists(path):
        os.remove(path)
    shutil.copy2(S2_ARTEFACT, path)
    p = probe("%s the dated scratch" % tag, path)
    R["scratches"].append({"path": path, "after_copy": p})
    gate("T3%s the scratch is byte-identical to the S2 artefact" % ("" if tag == "T3" else "-" + tag),
         p.get("md5") == S2_MD5, p.get("md5", "?"), fatal=True)
    return path


def main():
    print("=== diag_queue_trial_census  %s   (Pre-decided 36(d) TRIAL CENSUS; NO VI IS RUN, 34(f); "
          "no new op; PICKS NOTHING)" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])
    fact("36(c) WALL, restated so it is never quietly forgotten: NO BUILT OP READS Terminal.DataType. "
         "node_terms gives name/is_source/wire, report_all gives class/uid/pos/owner, node_info gives "
         "Node.Style for TOP-LEVEL nodes only and #686 is not top level. Building a type reader is a NEW OP "
         "and Pre-decided 2 forbids it. So a donor's TYPE is never printed here - only what the op DID.")

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---------------------------------------------------------------- the donor list, from the 36(c) census
    print("\n--- the donor list: the 18 nodes of 36(c), their named output terminals taken from "
          "tools/bench/diag_donor_census.json (the brief forbids re-deriving them)", flush=True)
    with open(CENSUS_JSON, encoding="utf-8") as f:
        CEN = json.load(f)
    cen_by_uid = {n["uid"]: n for n in CEN["B1"]["nodes"]}
    donors = []
    for uid in INDEPENDENT_UIDS:
        n = cen_by_uid.get(uid)
        if not n:
            fact("36(c) node #%d is NOT in diag_donor_census.json B1 - REPORTED, no donor rows from it" % uid)
            continue
        for t in n["named_output_terminals"]:
            donors.append({"node_uid": uid, "node_index_census": n["node_index"],
                           "label_census": n["label"], "class_guess_census": n["class_guess"],
                           "term_index_census": t["i"], "term_name": t["name"],
                           "term_wire_census": t["wire"]})
    R["donors"] = donors
    for d in donors:
        print(("      DONOR #%-6d %-10s %-24r  t%-3d %r"
               % (d["node_uid"], d["class_guess_census"], (d["label_census"] or "")[:24],
                  d["term_index_census"], d["term_name"])).encode("ascii", "replace").decode("ascii"),
              flush=True)
    nodes_with_no_named_out = [u for u in INDEPENDENT_UIDS
                               if not any(d["node_uid"] == u for d in donors)]
    fact("donor list: %d (node, named output terminal) pairs over %d of the 18 nodes; %d nodes expose NO named "
         "output terminal and contribute no donor: %r"
         % (len(donors), len({d["node_uid"] for d in donors}), len(nodes_with_no_named_out),
            nodes_with_no_named_out))
    gate("T4 uid %d (35(a)'s BANNED donor) is ABSENT from the donor list" % FRAME_LOOP_UID,
         all(d["node_uid"] != FRAME_LOOP_UID for d in donors),
         "%d donors" % len(donors), fatal=True)

    # ---------------------------------------------------------------- the scratch
    D.fresh("T2b")
    fact("handles after the restart: %r" % labview_handles())
    target = make_scratch("T3")

    with D.Preload("P"):
        g.open_panel(target)
        time.sleep(1.0)
        c0 = census("BEFORE any attempt", target)
        es0 = read_exec_state("before any attempt", target)
        R["exec_state"]["before_any_attempt"] = es0
        fact("scratch ExecState BEFORE any attempt, ORIGINAL preloaded: %r" % es0)

        # ------------------------------------------------------------ the LIVE walk (34(h))
        print("\n--- the LIVE walk of Diagram #%d (34(h): re-read, never cached) against the census JSON"
              % SIBLING_DIAG_UID, flush=True)
        d686 = diag_index(target, SIBLING_DIAG_UID)
        fact("Diagram #%d reads Traverse index %d on this scratch" % (SIBLING_DIAG_UID, d686))
        w = WALK(target, d686, limit=200)
        n_known = len(w)
        live = {}
        for uid, (ni, label, rows) in w.items():
            live[uid] = {"node_index": ni, "label": label, "class_guess": cls_of(uid, w),
                         "named_outs": [(r["i"], r["name"]) for r in rows
                                        if r["is_source"] and (r["name"] or "").strip()]}
        R["live_walk"] = {"diagram_index": d686, "n_nodes": n_known,
                          "nodes": {str(k): v for k, v in live.items()}}
        missing = [u for u in INDEPENDENT_UIDS if u not in live]
        gate("T5 the live walk finds all 18 nodes of 36(c) on Diagram #%d" % SIBLING_DIAG_UID,
             not missing, "missing %r; walk returned %d nodes" % (missing, n_known))
        diffs = []
        for uid in INDEPENDENT_UIDS:
            if uid not in live or uid not in cen_by_uid:
                continue
            a = [(t["i"], t["name"]) for t in cen_by_uid[uid]["named_output_terminals"]]
            b = live[uid]["named_outs"]
            if a != b:
                diffs.append({"uid": uid, "census": a, "live": b})
        R["live_vs_census_diffs"] = diffs
        gate("T6 the live named-output-terminal list equals the census JSON's, node for node",
             not diffs, "%d nodes differ: %r" % (len(diffs), diffs[:4]))

        # ------------------------------------------------------------ addressable classes, measured once
        print("\n--- resolving each donor node's addressable Traverse class BY MEMBERSHIP (never from its label)",
              flush=True)
        sets = class_membership(target)
        R["class_membership"] = {cls: (sorted(s & set(INDEPENDENT_UIDS)) if s is not None else None)
                                 for cls, s in sets.items()}
        for d in donors:
            u = d["node_uid"]
            holders = [c for c in PROBE_CLASSES if sets.get(c) and u in sets[c]]
            d["traverse_classes_containing_it"] = holders
            # order of preference: the census's own guess if it holds, then the most specific holder
            pref = [d["class_guess_census"]] + [c for c in holders if c != d["class_guess_census"]]
            d["class_used"] = next((c for c in pref if c in holders), None)
        for u in sorted({d["node_uid"] for d in donors}):
            d0 = next(d for d in donors if d["node_uid"] == u)
            fact("node #%d: cls_of guess %r; Traverse classes containing it %r; class USED %r"
                 % (u, d0["class_guess_census"], d0["traverse_classes_containing_it"], d0["class_used"]))

        # ------------------------------------------------------------ THE TRIAL
        print("\n--- THE TRIAL: one `queue_node('obtain')` per donor. A refusal is a legitimate outcome and its "
              "VERBATIM text is the reading.", flush=True)
        i, infra_run = 0, 0
        while i < len(donors):
            d = donors[i]
            k = len(R["attempts"])
            loc = (2600 + 260 * (k % 18), 6400 + 300 * (k // 18))
            rec = {"n": k, "node_uid": d["node_uid"], "term_name": d["term_name"],
                   "term_index_census": d["term_index_census"], "class_used": d["class_used"],
                   "location": loc, "scratch": target, "accepted": None,
                   "error_verbatim": None, "error_numbers": [], "new_function_uids": [],
                   "exec_state_before": None, "exec_state_after": None, "exec_state_changed": None}
            rec["exec_state_before"] = read_exec_state("before attempt %d" % k, target)
            if not d["class_used"]:
                rec["accepted"] = False
                rec["error_verbatim"] = ("NOT ATTEMPTED: no Traverse class in %r contains node #%d - the donor "
                                         "is not addressable by the built fleet" % (list(PROBE_CLASSES),
                                                                                    d["node_uid"]))
                rec["exec_state_after"] = rec["exec_state_before"]
                rec["exec_state_changed"] = False
                R["attempts"].append(rec)
                fact("ATTEMPT %d #%d %r -> %s" % (k, d["node_uid"], d["term_name"], rec["error_verbatim"]))
                i += 1
                continue
            try:
                ci = class_index(target, d["class_used"], d["node_uid"])
            except Exception as e:                                                # noqa: BLE001
                ci = None
                rec["error_verbatim"] = "class_index raised %s: %s" % (type(e).__name__, str(e)[:300])
            rec["class_index"] = ci
            before = g.uids(target, "Function")
            if ci is not None:
                # 38(e)'s cheap defence: the destination diagram index is re-resolved immediately before the call
                d686_now = diag_index(target, SIBLING_DIAG_UID)
                rec["diagram_index_reresolved"] = d686_now
                try:
                    rec["returned"] = g.queue_node("obtain", target, d["class_used"], int(ci),
                                                   d["term_name"], d686_now, loc)
                except Exception as e:                                            # noqa: BLE001
                    rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:600])
            after = g.uids(target, "Function")
            rec["new_function_uids"] = sorted(after - before)
            rec["accepted"] = bool(rec["new_function_uids"]) and not rec["error_verbatim"]
            rec["error_numbers"] = sorted({int(x) for x in
                                           re.findall(r"error\s+(\d+)", rec["error_verbatim"] or "", re.I)})
            # readback of everything the built fleet CAN read about the created node
            if rec["new_function_uids"]:
                newmap, n_known = scan_nodes_from(target, d686, n_known)
                try:
                    ra = {r["uid"]: r for r in g.report_all(target, "Function")}
                except Exception as e:                                            # noqa: BLE001
                    ra = {}
                    fact("report_all('Function') raised %s: %s" % (type(e).__name__, str(e)[:150]))
                rec["created"] = []
                for u in rec["new_function_uids"]:
                    ni, rows = newmap.get(u, (None, None))
                    try:
                        ow = owner_of(target, u, strict=False)
                    except Exception as e:                                        # noqa: BLE001
                        ow = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
                    cr = {"uid": u, "nodes_index": ni,
                          "node_terms": ([{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                                           "wire": r["wire"]} for r in rows] if rows else []),
                          "node_terms_readable": rows is not None,
                          "report_all_row": ra.get(u), "owner_of": ow, "label": None}
                    rec["created"].append(cr)
                    print(("      CREATED #%d Nodes[%s] report_all %r owner_of %r"
                           % (u, ni, ra.get(u), ow)).encode("ascii", "replace").decode("ascii"), flush=True)
                    for t in cr["node_terms"]:
                        print(("           term t%-3d %-30r is_source=%s wire=%s"
                               % (t["i"], (t["name"] or "")[:30], t["is_source"], t["wire"]))
                              .encode("ascii", "replace").decode("ascii"), flush=True)
            rec["exec_state_after"] = read_exec_state("after attempt %d" % k, target)
            rec["exec_state_changed"] = rec["exec_state_after"] != rec["exec_state_before"]
            R["attempts"].append(rec)
            fact("ATTEMPT %d: donor #%d[%s] . %r via Traverse %r[%s] -> accepted=%s; new Function uids %r; "
                 "ExecState %r -> %r (changed=%s); op error VERBATIM %r"
                 % (k, d["node_uid"], d["term_index_census"], d["term_name"], d["class_used"],
                    rec.get("class_index"), rec["accepted"], rec["new_function_uids"],
                    rec["exec_state_before"], rec["exec_state_after"], rec["exec_state_changed"],
                    rec["error_verbatim"]))

            # a refusal carrying a machine ERROR NUMBER is a real reading; anything else is infrastructure
            is_reading = rec["accepted"] or bool(rec["error_numbers"])
            infra_run = 0 if is_reading else infra_run + 1
            if infra_run >= 3 and R["restarts"] < MAX_RESTARTS:
                R["restarts"] += 1
                fact("THREE consecutive attempts produced NO machine error number - the target may no longer be "
                     "interpretable. Restarting from a CLEAN scratch (restart %d of %d) and retrying donor %d."
                     % (R["restarts"], MAX_RESTARTS, i))
                try:
                    g.close_panel(target)
                except Exception:                                                 # noqa: BLE001
                    pass
                D.fresh("restart%d" % R["restarts"])
                target = make_scratch("restart%d" % R["restarts"])
                g.open_panel(target)
                time.sleep(1.0)
                d686 = diag_index(target, SIBLING_DIAG_UID)
                n_known = len(WALK(target, d686, limit=200))
                infra_run = 0
                continue
            i += 1
            dump()

        # ------------------------------------------------------------ the scoring
        print("\n--- the scoring", flush=True)
        att = R["attempts"]
        acc = [a for a in att if a["accepted"]]
        ref = [a for a in att if a["accepted"] is False]
        R["acceptances"] = [{"node_uid": a["node_uid"], "term_name": a["term_name"],
                             "created": a.get("created")} for a in acc]
        errno_counts = {}
        for a in ref:
            key = ",".join(str(x) for x in a["error_numbers"]) or "(no error number in the text)"
            errno_counts[key] = errno_counts.get(key, 0) + 1
        R["counts"] = {"attempted": len(att), "accepted": len(acc), "refused": len(ref),
                       "refusal_error_numbers": errno_counts}
        fact("COUNTS: %d donors attempted, %d ACCEPTED, %d REFUSED; refusal error numbers %r"
             % (len(att), len(acc), len(ref), errno_counts))
        for a in acc:
            fact("ACCEPTED pair: node #%d . %r -> created %r"
                 % (a["node_uid"], a["term_name"], a["new_function_uids"]))
        gate("T7 every donor was attempted and scored", len(att) == len(donors),
             "%d attempts for %d donors" % (len(att), len(donors)))
        base = next((a for a in att if (a["node_uid"], a["term_name"]) == BASELINE_DONOR), None)
        gate("T8 the 36(a) baseline donor #%d %r is ACCEPTED" % BASELINE_DONOR,
             bool(base) and bool(base["accepted"]),
             "accepted=%r error %r" % ((base or {}).get("accepted"), (base or {}).get("error_verbatim")))
        read_back = [a for a in acc if a.get("created") and all(c["report_all_row"] for c in a["created"])]
        gate("T9 every acceptance was read back (node_terms rows AND a report_all row)",
             len(read_back) == len(acc), "%d of %d" % (len(read_back), len(acc)))

        # ------------------------------------------------------------ T10: THE DISTINGUISHABILITY READING
        print("\n--- T10: ARE TWO ACCEPTANCES ON DIFFERENTLY-TYPED DONORS DISTINGUISHABLE BY ANY BUILT OP? "
              "(36(d) ASSUMES they are; this MEASURES it)", flush=True)
        try:
            lab = {r["uid"]: r["label"] for r in g.node_labels(target, diag_index(target, SIBLING_DIAG_UID))}
        except Exception as e:                                                    # noqa: BLE001
            lab = {}
            fact("node_labels raised %s: %s - labels are reported as None" % (type(e).__name__, str(e)[:150]))
        sigs = {}
        for a in acc:
            for c in (a.get("created") or []):
                c["label"] = lab.get(c["uid"])
                s = signature(c)
                sigs.setdefault(s, []).append({"donor_node": a["node_uid"], "donor_term": a["term_name"],
                                               "created_uid": c["uid"]})
        R["distinguishability"] = {
            "n_acceptances": len(acc),
            "n_distinct_readable_signatures": len(sigs),
            "fields_compared": ["report_all class", "report_all owner", "node label",
                                "node_terms terminal count", "node_terms (index, name, is_source) per terminal"],
            "fields_NOT_available": ["Terminal.DataType (no built op reads it - 36(c))",
                                     "any type descriptor", "the queue's element type"],
            "signatures": [{"signature": s, "members": m} for s, m in sigs.items()]}
        for s, m in sigs.items():
            print(("      SIGNATURE (%d acceptances): %s\n          members: %r"
                   % (len(m), s[:400], [(x["donor_node"], x["donor_term"]) for x in m]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
        if len(acc) >= 2 and len(sigs) == 1:
            fact("🔴 THE READING: all %d acceptances produce an IDENTICAL readable signature. Two `Obtain Queue` "
                 "nodes created from DIFFERENTLY-SHAPED donors are INDISTINGUISHABLE by every built op - "
                 "report_all (class/uid/pos/owner), node_terms (name/is_source/wire) and node_labels all return "
                 "the same thing. 36(d)'s premise 'a created Obtain Queue can be read back' holds only for the "
                 "node's EXISTENCE, not for its ELEMENT TYPE." % len(acc))
        elif len(acc) >= 2:
            fact("THE READING: %d acceptances fall into %d DISTINCT readable signatures - the created nodes are "
                 "distinguishable by the fields listed in R['distinguishability']['fields_compared']."
                 % (len(acc), len(sigs)))
        else:
            fact("THE READING: fewer than two acceptances (%d) - distinguishability could not be measured on "
                 "this run." % len(acc))
        gate("T10 the distinguishability reading is recorded (%d acceptances -> %d distinct readable signatures)"
             % (len(acc), len(sigs)), True,
             "1 signature = indistinguishable by the built fleet")

        # ------------------------------------------------------------ T11 / T12
        es1 = read_exec_state("after all attempts", target)
        R["exec_state"]["after_all_attempts"] = es1
        moved = [a for a in att if a["exec_state_changed"]]
        R["exec_state"]["attempts_that_moved_it"] = [
            {"n": a["n"], "node_uid": a["node_uid"], "term_name": a["term_name"],
             "before": a["exec_state_before"], "after": a["exec_state_after"]} for a in moved]
        fact("ExecState: %r before any attempt -> %r after all of them; %d individual attempts moved it: %r"
             % (es0, es1, len(moved), R["exec_state"]["attempts_that_moved_it"][:6]))
        gate("T11 ExecState before/after every attempt is recorded",
             all(a["exec_state_changed"] is not None for a in att), "%d attempts" % len(att))

        census("AFTER all attempts", target)
        size, serr = None, None
        try:
            size = g.save(target)            # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                    # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        R["save"] = {"returned_bytes": size, "exception": serr, "allow_broken": False, "gui_save": False}
        fact("g.save(scratch) returned %r; exception VERBATIM %r (allow_broken False, gui_save never called)"
             % (size, serr))
        R["save"]["file_after"] = D.file_facts("the scratch after the save attempt", target)
        gate("T12 the save attempt is recorded", True, "returned %r, exception %r" % (size, serr))
        try:
            g.close_panel(target)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
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
            dump()
        except Exception:                                                         # noqa: BLE001
            pass
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
        gate("T13 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            try:
                dd = probe("T14 %s after the run" % tag, path)
            except Exception as e:                                                # noqa: BLE001
                print("  FAIL  T14 %s could not be re-probed: %s: %s" % (tag, type(e).__name__, e), flush=True)
                fails.append("T14 %s re-probe raised" % tag)
                rc = 1
                continue
            R.setdefault("untouched", {})[tag] = dd.get("md5")
            if not gate("T14 %s md5 unchanged" % tag, dd.get("md5") == pin, dd.get("md5", "?")):
                rc = 1
        try:
            dump()
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  the readings JSON could not be written: %s: %s" % (type(e).__name__, e), flush=True)
            rc = 1
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== GATES ARE REPORTED, NOT REQUIRED - the READING is the deliverable (34(j) pattern).",
              flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCHES: %r  (restarts from a clean scratch: %d)"
              % ([s["path"] for s in R["scratches"]], R["restarts"]), flush=True)
        print("=== FACTS ONLY - no donor is picked and no queue stage is written (36(d) reserves both for the "
              "judgement session). NO VI WAS RUN (34(f)); no new op; no motor, no ASI, no camera, no GUI.",
              flush=True)
        sys.exit(rc)
