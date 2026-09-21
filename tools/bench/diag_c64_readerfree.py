"""diag_c64_readerfree - cycle 64 material #3. DOES A READER-FREE SCRIPTING EDIT PERTURB `ExecState`?

PURE MEASUREMENT. Nothing is built, no VI is saved, no route is chosen or recommended. The one write to
disk is the DELETION of `claudeDev\\OpConnectNested_v2.vi` (judgement's decision this cycle: it is still a
byte copy of v1, so the `connect_nested_v2` wrapper silently runs v1 WITH its reader - delete the file so
the wrapper fails loudly instead of answering wrongly). `tools/gscript.py` is NOT edited.

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT (checked before writing a line of this file):
  tools/bench/diag_c64_perturb_t1t3.py   the gate/fact/probe/timeline skeleton, `_drop_scratch`, the md5-pin
                                         block and the ARM shape - reused, minus its `g.open_panel` call
  tools/gscript.py:2445 connect_terminals -> OpConnect_v0.vi          the READER-FREE connect (ARM D1)
  tools/gscript.py:1005 count / :587 node_labels / :870 node_terms / :925 node_terms_uid / :488 report_all
                                         the read-only census verbs - NO new reader is built here
  tools/recipes/build_opconnectnested_v1.py:418 connect_nested_v1     the op that CARRIES the readback (ARM D3)
  tools/hash_probe.py probe / tools/bench/bench_prep.py labview_handles
No new op, no new gscript verb, no recipe, nothing under tools/recipes/ is written.

WHY THIS RUN EXISTS
  Dispatch #1's T3 table was a GREP OF BUILDER SCRIPTS and has a demonstrated false positive
  (`OpNodeTerms_v0` marked YES from the line that DELETES the reader). So the `YES` rows for
  `OpConnect2_v0` and `OpSetLabel_v0` are UNMEASURED, and the premise behind the whole route - "the
  embedded `Wire.Is Broken?` read is what drives ExecState 1 -> 0" - has never been tested against an op
  that provably carries no reader. The hypothesis peer on dispatch #2 named exactly this discriminating
  test. Leg C replaces the grep with a census taken OFF THE MACHINE.

  The item terminal of the `Wire.Is Broken?` 6371004 read prints as **`Broken?`**, NOT `Is Broken?`
  (dispatch #2's correction; `docs/NAMES.md:902-903` was itself wrong and has been corrected). This file
  therefore matches `Broken?` and records the exact bytes it saw.

🔴 NO `g.open_panel` CALL APPEARS IN THIS FILE. It is what poisoned dispatch #2's run 2 (246 s against
   gscript's 180 s `_invoke` cap). Every census leg below is read-only and works on a GetVIReference-only
   load (`tools/gscript.py:1328-1330`). ⚠️ ONE THING THE BRIEF COULD NOT HAVE BOTH WAYS, REPORTED AND NOT
   DECIDED HERE: an EDIT is silently declined on a target that is not panel-loaded, so
   `connect_terminals` and `connect_nested_v1` BOTH call `g.ensure_loaded(target)` INTERNALLY
   (`tools/gscript.py:1268-1337` -> `open_panel`). ARM D1 and ARM D3 are edits, so the internal call
   happens inside the wrapper; this file never calls it. The read-only legs run first as an ORDERING WITH
   NO MITIGATING VALUE CLAIMED - the cycle's peer review (archive/peer/2026-09-21-c64-openpanel-cap.md,
   ANSWERED) refuted the warm-up idea at its premise: a COLD `exec_state` on that same op in a
   just-restarted instance cost **0.42 s** (diag_c64_connect_v2.json:97-100), so there was never 180 s of
   loading to front-load, and a green run here must NOT be credited to warming. What the review DID
   establish is the hazard this file avoids by construction: run 2's stall followed
   `close_panel` (a load) -> `os.remove` -> `copyfile` -> `open_panel`, i.e. replacing a file under a path
   LabVIEW had already loaded. Every scratch below is a `copy2` to a FRESH `STAMP` name that LabVIEW has
   never seen, and no loaded path is ever removed-and-replaced. Each arm is wrapped so a COMPoisoned/stall
   is RECORDED and the closing gates still run, and every read records its OWN cost (`read_cost_s`,
   `call_cost_s`) - the review's §1: this project had been reading durations off timeline OFFSETS.

PREDICTION CONTRACT (a failed prediction here is a REVIEW trigger, not a retry)
  F   claudeDev\\OpConnectNested_v2.vi exists and is md5 b7a1bb56... ; after this run it does not exist
  C   each of the five ops yields a property-node table; at least OpConnectNested_v1 carries `Broken?`
      (dispatch #2 read it directly: #242 `Broken?` w676). NO other row is predicted - that is the point
  S   a bed is selected: the smallest claudeDev\\Op*.vi with cold ExecState 1 and, on its TOP-LEVEL
      diagram, a wire with exactly ONE source terminal and exactly ONE sink terminal
  D1  connect_terminals on that existing pair: `wire_delta` 0 and the wire census unchanged (idempotent).
      NO ExecState value is predicted - the reading IS the measurement
  D2  the no-edit control makes the same reads on an independent scratch; no value is predicted
  D3  connect_nested_v1 on the same pair: `wire_delta` 0; no ExecState value is predicted
  Z   four md5 pins hold before AND after (ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind);
      OpConnectNested_v1.vi and OpCreateLocalRead_v0.vi and the chosen bed op byte-unchanged; every
      scratch exists=False; refs opened == closed == 0 live; handles reported either side

FORBIDDEN AND ABSENT, by inspection and by tools/bench/c60c_astcheck.py:
  no save of any VI, no allow_broken, no gui_save, no GUI action, no new op, no edit to tools/gscript.py,
  no cast, no splice (51(h)), no recipe, nothing written under tools/recipes/, no VI run (34(f)), no
  motor/ASI/camera (rig ASSEMBLED - nothing is touched), no new process device. retrospective.py /
  audit_cycle.py / violations.py / doc_ingest.py / prior_art_review.py are NOT run (54(a)).
"""
import contextlib
import glob as globmod
import io
import json
import os
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
import shutil                                                                      # noqa: E402
import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"
OP_V1 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v1.vi")
OP_V1_MD5 = "b7a1bb56"                       # prefix only; the full value is measured and pinned at run time
OP_V2 = os.path.join(g.CLAUDEDEV, "OpConnectNested_v2.vi")

CENSUS_OPS = ["OpConnect2_v0.vi", "OpSetLabel_v0.vi", "OpConnectNested_v1.vi", "OpNodeTerms_v0.vi",
              "OpConnect_v0.vi"]
BROKEN_ITEM = "Broken?"                      # the ITEM terminal name; NOT "Is Broken?" (dispatch #2)
TOP = 0                                      # Traverse "Diagram" index 0 = the top-level diagram
MAX_CANDIDATES = 6                           # how many op VIs, smallest first, may be examined as a bed

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c64_readerfree.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
D1_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64D1_%s.vi" % STAMP)
D2_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64D2_%s.vi" % STAMP)
D3_SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C64D3_%s.vi" % STAMP)
SCRATCHES = (D1_SCRATCH, D2_SCRATCH, D3_SCRATCH)

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 64 material #3: does a READER-FREE scripting edit perturb ExecState?",
     "no_open_panel_call_in_this_file": True,
     "edits_reach_open_panel_through_the_wrapper": ("connect_terminals and connect_nested_v1 call "
                                                    "g.ensure_loaded internally (gscript.py:1268-1337); "
                                                    "this file never calls open_panel itself"),
     "no_save": "g.save is neither imported nor called anywhere in this file",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "no_gui_action": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "chooses_no_route": True, "recommends_no_route": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [],
     "f_delete_v2": {}, "c_census": {}, "bed": {}, "arm_d1": {}, "arm_d2": {}, "arm_d3": {}}


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
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "leg": leg, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s | %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], leg, tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def safe(label, fn, default=None):
    """Run one read, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def drop_scratch(path, leg):
    """close_panel (NOT open_panel) then delete. A scratch never outlives the run."""
    if os.path.exists(path):
        safe("%s close_panel" % leg, lambda: g.close_panel(path))
        try:
            os.remove(path)
        except Exception as e:                                                     # noqa: BLE001
            fact("%s could not delete %s: %s" % (leg, os.path.basename(path), e))
    return os.path.exists(path)


# ===================================================================== helpers: the top-level wire map
def top_nodes(path, tag):
    """[{i, uid, label}] for the TOP-LEVEL diagram of `path`, each verified by its own uid echo later."""
    rows, err = safe("%s node_labels(top)" % tag, lambda: g.node_labels(path, TOP), [])
    out = [{"i": i, "uid": r["uid"], "label": r["label"]} for i, r in enumerate(rows or [])]
    return out, err


def wire_map(path, nodes, tag):
    """{wire uid: {'src': [...], 'sink': [...]}} over every terminal of every top-level node.

    Each node's terminals are read with node_terms_uid so the Nodes[] position is confirmed by the node's
    OWN uid before any terminal of it is believed (Pre-decided 53(d8): owner_of can answer with the
    previous query's object; an index that is not uid-checked is not an address).
    """
    wires, term_rows, mismatches = {}, {}, []
    for n in nodes:
        echo, rows = None, []
        try:
            echo, rows = g.node_terms_uid(path, TOP, n["i"])
        except Exception as e:                                                     # noqa: BLE001
            mismatches.append({"i": n["i"], "uid": n["uid"], "error": "%s: %s" % (type(e).__name__,
                                                                                  str(e)[:160])})
            continue
        if echo != n["uid"]:
            mismatches.append({"i": n["i"], "uid": n["uid"], "echo": echo})
            continue
        term_rows[n["i"]] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                              "wire": t["wire"]} for t in rows]
        for t in rows:
            if t["wire"]:
                slot = wires.setdefault(int(t["wire"]), {"src": [], "sink": []})
                slot["src" if t["is_source"] else "sink"].append(
                    {"node_i": n["i"], "node_uid": n["uid"], "label": n["label"], "term_i": t["i"],
                     "term_name": t["name"]})
    fact("%s: %d top-level nodes, %d wires touched, %d uid-echo mismatches"
         % (tag, len(nodes), len(wires), len(mismatches)))
    return wires, term_rows, mismatches


def pick_pair(wires):
    """The first wire with EXACTLY one source terminal and EXACTLY one sink terminal, lowest uid first."""
    for uid in sorted(wires):
        s, k = wires[uid]["src"], wires[uid]["sink"]
        if len(s) == 1 and len(k) == 1:
            return {"wire_uid": uid, "src": s[0], "sink": k[0]}
    return None


# ===================================================================== F  delete OpConnectNested_v2.vi
def f_delete_v2(when):
    f = R["f_delete_v2"]
    f["path"] = OP_V2
    f["reason"] = ("judgement, cycle 64: the file is a BYTE COPY of v1, so gscript.connect_nested_v2 "
                   "silently runs v1 WITH its reader; deleting it makes the wrapper fail loudly. The "
                   "wrapper function itself (tools/gscript.py:2892) is left untouched.")
    if not os.path.exists(OP_V2):
        f.setdefault("attempts", []).append({"when": when, "existed": False})
        return True
    rec = {"when": when, "existed": True, "size": os.path.getsize(OP_V2)}
    try:
        rec["md5"] = probe("F OpConnectNested_v2.vi before deletion", OP_V2).get("md5")
    except Exception as e:                                                         # noqa: BLE001
        rec["md5"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    try:
        os.remove(OP_V2)
        rec["deleted"] = not os.path.exists(OP_V2)
    except Exception as e:                                                         # noqa: BLE001
        rec["deleted"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
    f.setdefault("attempts", []).append(rec)
    fact("F delete OpConnectNested_v2.vi [%s]: %r" % (when, rec))
    return not os.path.exists(OP_V2)


# ===================================================================== C  the property-node census
def c_census():
    print("\n=== C  PROPERTY NODES AND THEIR ITEM NAMES, READ OFF THE MACHINE (read-only; this replaces "
          "dispatch #1's grep of builder scripts)", flush=True)
    table = []
    for name in CENSUS_OPS:
        path = os.path.join(g.CLAUDEDEV, name)
        row = {"op": name, "exists": os.path.exists(path), "property_nodes": []}
        if not row["exists"]:
            table.append(row)
            fact("C %s: FILE DOES NOT EXIST" % name)
            continue
        row["size"] = os.path.getsize(path)
        row["exec_state"] = read_es("[C] %s (read-only)" % name, path, "C")
        row["node_count"], _ = safe("C %s count(Node)" % name, lambda p=path: g.count(p, "Node"))
        row["wire_count"], _ = safe("C %s count(Wire)" % name, lambda p=path: g.count(p, "Wire"))
        props, perr = safe("C %s report_all(Property)" % name,
                           lambda p=path: g.report_all(p, "Property"), [])
        row["property_census_error"] = perr
        row["property_count"] = len(props or [])
        nodes, nerr = top_nodes(path, "C %s" % name)
        row["top_level_nodes"] = len(nodes)
        row["node_labels_error"] = nerr
        by_uid = {n["uid"]: n for n in nodes}
        for p in (props or []):
            prec = {"uid": p["uid"], "pos": p["pos"], "owner_class": p["owner"],
                    "nodes_index": by_uid.get(p["uid"], {}).get("i"),
                    "label": by_uid.get(p["uid"], {}).get("label")}
            if prec["nodes_index"] is None:
                prec["items"] = None
                prec["note"] = "not addressable as a TOP-LEVEL Nodes[] position (nested, or class differs)"
            else:
                try:
                    echo, rows = g.node_terms_uid(path, TOP, prec["nodes_index"])
                    prec["uid_echo"] = echo
                    if echo == p["uid"]:
                        prec["items"] = [t["name"] for t in rows]
                        prec["item_rows"] = [{"i": t["i"], "name": t["name"],
                                              "is_source": t["is_source"], "wire": t["wire"]}
                                             for t in rows]
                    else:
                        prec["items"] = None
                        prec["note"] = "REJECTED: Nodes[%d] echoed %r" % (prec["nodes_index"], echo)
                except Exception as e:                                             # noqa: BLE001
                    prec["items"] = None
                    prec["note"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
            prec["carries_broken_read"] = bool(prec.get("items")
                                               and any(i == BROKEN_ITEM for i in prec["items"]))
            row["property_nodes"].append(prec)
        row["carries_broken_read"] = any(p.get("carries_broken_read") for p in row["property_nodes"])
        row["unreadable_property_nodes"] = sum(1 for p in row["property_nodes"] if p.get("items") is None)
        fact("C %s: %d Property nodes, %d top-level nodes, Node %r / Wire %r ; carries a %r read -> %r "
             "(%d property node(s) not readable as a top-level index)"
             % (name, row["property_count"], row["top_level_nodes"], row["node_count"],
                row["wire_count"], BROKEN_ITEM, row["carries_broken_read"],
                row["unreadable_property_nodes"]))
        for p in row["property_nodes"]:
            fact("   C %s  Property #%s @%s  Nodes[%s]  items=%r  %r -> %r%s"
                 % (name, p["uid"], p["pos"], p["nodes_index"], p.get("items"), BROKEN_ITEM,
                    p["carries_broken_read"], ("  [" + p["note"] + "]") if p.get("note") else ""))
        table.append(row)
    R["c_census"]["table"] = table
    R["c_census"]["item_terminal_name_used"] = BROKEN_ITEM
    print("\n  --- C TABLE: op VI | property node uid | items read | carries a %r read" % BROKEN_ITEM,
          flush=True)
    for row in table:
        for p in row["property_nodes"]:
            print(("    %-26s %-8s %-70s %s"
                   % (row["op"], p["uid"], repr(p.get("items"))[:70], p["carries_broken_read"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
    gate("C_a the census ran on all five ops and produced a table (no verdict is asserted here)",
         len(table) == len(CENSUS_OPS),
         "%d rows ; carries-Broken?: %r"
         % (len(table), {r["op"]: r.get("carries_broken_read") for r in table}))
    gate("C_b every property node of every censused op was either read or explained",
         all(all((p.get("items") is not None) or p.get("note") for p in r["property_nodes"])
             for r in table),
         "unreadable per op: %r" % {r["op"]: r.get("unreadable_property_nodes") for r in table})


# ===================================================================== S  choose the ARM D bed
def choose_bed():
    print("\n=== S  CHOOSE THE BED: the SMALLEST claudeDev\\Op*.vi whose TOP-LEVEL diagram carries a wired "
          "source->sink pair (read-only; the chosen file itself is never edited)", flush=True)
    cands = sorted((p for p in globmod.glob(os.path.join(g.CLAUDEDEV, "Op*.vi"))),
                   key=lambda p: os.path.getsize(p))
    R["bed"]["candidates_on_disk"] = len(cands)
    R["bed"]["examined"] = []
    for path in cands[:MAX_CANDIDATES]:
        name = os.path.basename(path)
        rec = {"op": name, "size": os.path.getsize(path)}
        rec["cold_exec_state"] = read_es("[S] candidate %s" % name, path, "S")
        nodes, nerr = top_nodes(path, "S %s" % name)
        rec["top_level_nodes"] = len(nodes)
        rec["node_labels_error"] = nerr
        rec["wire_count"], _ = safe("S %s count(Wire)" % name, lambda p=path: g.count(p, "Wire"))
        if nodes:
            wires, terms, mism = wire_map(path, nodes, "S %s" % name)
            rec["wires_touched"] = len(wires)
            rec["uid_echo_mismatches"] = len(mism)
            pair = pick_pair(wires)
            rec["pair"] = pair
        else:
            rec["wires_touched"], rec["pair"] = 0, None
        rec["accepted"] = bool(rec["cold_exec_state"] == 1 and rec.get("pair")
                               and rec["top_level_nodes"] >= 2)
        R["bed"]["examined"].append(rec)
        fact("S candidate %s (%d B): cold ExecState %r, %d top-level nodes, Wire %r, pair %r -> accepted %r"
             % (name, rec["size"], rec["cold_exec_state"], rec["top_level_nodes"], rec.get("wire_count"),
                (rec.get("pair") or {}).get("wire_uid"), rec["accepted"]))
        if rec["accepted"]:
            R["bed"]["chosen"] = rec
            R["bed"]["path"] = path
            R["bed"]["md5_before"] = probe("S the chosen bed %s" % name, path).get("md5")
            break
    ok = bool(R["bed"].get("chosen"))
    gate("S_a a bed op VI was chosen (cold ExecState 1, >=2 top-level nodes, one clean source->sink wire)",
         ok, "%r" % ({k: R["bed"]["chosen"][k] for k in ("op", "size", "top_level_nodes", "wire_count")}
                     if ok else "NONE of the %d smallest candidates qualified" % MAX_CANDIDATES),
         fatal=True)
    c = R["bed"]["chosen"]
    fact("S THE BED IS %s (%d B, md5 %s): top-level nodes %d, Wire %r, Node %r ; the pair is wire %r "
         "from %r Nodes[%d].Terminals[%d] %r  ->  %r Nodes[%d].Terminals[%d] %r"
         % (c["op"], c["size"], R["bed"]["md5_before"], c["top_level_nodes"], c.get("wire_count"),
            c.get("node_count"), c["pair"]["wire_uid"], c["pair"]["src"]["label"],
            c["pair"]["src"]["node_i"], c["pair"]["src"]["term_i"], c["pair"]["src"]["term_name"],
            c["pair"]["sink"]["label"], c["pair"]["sink"]["node_i"], c["pair"]["sink"]["term_i"],
            c["pair"]["sink"]["term_name"]))
    return R["bed"]["path"], c["pair"]


# ===================================================================== the three arms
def fresh_bed(src, dst, tag, leg):
    """Copy the bed to `dst` and read it COLD - WITHOUT open_panel (readers do not need it)."""
    shutil.copy2(src, dst)
    rec = {"path": dst, "src": os.path.basename(src)}
    rec["cold_exec_state"] = read_es("[cold] %s" % tag, dst, leg)
    rec["wire_count_before"], _ = safe("%s count(Wire)" % tag, lambda: g.count(dst, "Wire"))
    rec["node_count_before"], _ = safe("%s count(Node)" % tag, lambda: g.count(dst, "Node"))
    return rec


def verify_pair(path, pair, tag):
    """Re-verify, ON THIS SCRATCH, that the two Nodes[] positions still echo their own uids."""
    out = {}
    for end in ("src", "sink"):
        p = pair[end]
        try:
            echo, rows = g.node_terms_uid(path, TOP, p["node_i"])
            row = next((t for t in rows if t["i"] == p["term_i"]), None)
            out[end] = {"nodes_index": p["node_i"], "expected_uid": p["node_uid"], "uid_echo": echo,
                        "term_name": (row or {}).get("name"), "is_source": (row or {}).get("is_source"),
                        "wire": (row or {}).get("wire"), "ok": echo == p["node_uid"]}
        except Exception as e:                                                     # noqa: BLE001
            out[end] = {"nodes_index": p["node_i"], "error": "%s: %s" % (type(e).__name__, str(e)[:200]),
                        "ok": False}
    fact("%s pair check: src %r ; sink %r" % (tag, out.get("src"), out.get("sink")))
    return out


def arm_d1(bed, pair):
    print("\n=== ARM D1  THE EDIT: ONE idempotent `connect_terminals` (OpConnect_v0 - the connect op the "
          "census finds reader-free) re-connecting an EXISTING source->sink pair", flush=True)
    a = R["arm_d1"]
    a["op"] = "gscript.connect_terminals (tools/gscript.py:2445) -> OpConnect_v0.vi"
    a["caveat_from_the_wrapper_docstring"] = ("gscript.py:2448-2450 warns that an already-wired SINK is "
                                              "not safe (LabVIEW re-routes); this call is deliberately "
                                              "idempotent on an ALREADY-WIRED pair, on a throwaway "
                                              "scratch, and wire_delta 0 is the check that nothing moved")
    try:
        a.update(fresh_bed(bed, D1_SCRATCH, "ARM D1 scratch", "D1"))
        a["pair_check"] = verify_pair(D1_SCRATCH, pair, "ARM D1")
        a["exec_state_before"] = read_es("[D1] immediately BEFORE connect_terminals", D1_SCRATCH, "D1")
        a["call"] = ("connect_terminals(target, sink_node=%d, sink_term=%d, src_node=%d, src_term=%d)"
                     % (pair["sink"]["node_i"], pair["sink"]["term_i"],
                        pair["src"]["node_i"], pair["src"]["term_i"]))
        fact("ARM D1 THE ONE CALL: %s   [wire %r at both ends before]"
             % (a["call"], pair["wire_uid"]))
        buf = io.StringIO()
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_ret = g.connect_terminals(D1_SCRATCH, pair["sink"]["node_i"],
                                                 pair["sink"]["term_i"], pair["src"]["node_i"],
                                                 pair["src"]["term_i"])
            a["wire_delta"], a["exec_state_returned_by_the_wrapper"] = dw, es_ret
            a["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            a["wire_delta"], a["exec_state_returned_by_the_wrapper"] = None, None
            a["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        a["call_cost_s"] = round(time.time() - t0, 1)
        a["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
        for ln in a["op_stdout_verbatim"]:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        # the op's OWN error cluster, read straight off OpConnect_v0's front panel
        a["op_error_cluster"], _ = safe("ARM D1 OpConnect_v0 error out",
                                        lambda: g._err(g.op(g.OP_CONNECT), "error out"))
        a["wire_count_after"], _ = safe("ARM D1 count(Wire)", lambda: g.count(D1_SCRATCH, "Wire"))
        a["node_count_after"], _ = safe("ARM D1 count(Node)", lambda: g.count(D1_SCRATCH, "Node"))
        a["exec_state_after"] = read_es("[D1] immediately AFTER connect_terminals", D1_SCRATCH, "D1")
        a["pair_check_after"] = verify_pair(D1_SCRATCH, pair, "ARM D1 after")
        a["re_reads"] = []
        for k in range(3):
            time.sleep(2.0)
            a["re_reads"].append(read_es("[D1] bare re-read %d of 3 (~2 s apart)" % (k + 1),
                                         D1_SCRATCH, "D1"))
        fact("ARM D1: ExecState %r -> %r then %r ; wire_delta %r ; Wire %r -> %r ; Node %r -> %r ; "
             "op error cluster %r ; call cost %rs"
             % (a.get("exec_state_before"), a.get("exec_state_after"), a.get("re_reads"),
                a.get("wire_delta"), a.get("wire_count_before"), a.get("wire_count_after"),
                a.get("node_count_before"), a.get("node_count_after"), a.get("op_error_cluster"),
                a.get("call_cost_s")))
        gate("D1_a the edit ran and is recorded; the pair was uid-checked at both ends before it "
             "(NO ExecState value is asserted - the reading IS the measurement)",
             bool(a.get("pair_check", {}).get("src", {}).get("ok")
                  and a.get("pair_check", {}).get("sink", {}).get("ok")),
             "src ok=%r sink ok=%r ; error %r"
             % (a.get("pair_check", {}).get("src", {}).get("ok"),
                a.get("pair_check", {}).get("sink", {}).get("ok"), a.get("error_verbatim")))
        gate("D1_b the edit was IDEMPOTENT (wire_delta 0 and the wire census unchanged)",
             a.get("wire_delta") == 0 and a.get("wire_count_after") == a.get("wire_count_before"),
             "wire_delta %r ; Wire %r -> %r" % (a.get("wire_delta"), a.get("wire_count_before"),
                                                a.get("wire_count_after")))
    except Exception as e:                                                         # noqa: BLE001
        a["leg_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("ARM D1 LEG ABORTED: %s" % a["leg_error_verbatim"])
        gate("D1_a the edit ran and is recorded", False, a["leg_error_verbatim"])
    finally:
        a["scratch_exists"] = drop_scratch(D1_SCRATCH, "ARM D1")
        gate("Z_3a the ARM D1 scratch is deleted in the same run", not a["scratch_exists"], D1_SCRATCH)


def arm_d2(bed, pair):
    print("\n=== ARM D2  THE NO-EDIT CONTROL: the same reads on an independent scratch, NO edit at all",
          flush=True)
    a = R["arm_d2"]
    a["op"] = "no op is called; read-only census verbs only"
    try:
        a.update(fresh_bed(bed, D2_SCRATCH, "ARM D2 scratch", "D2"))
        a["pair_check"] = verify_pair(D2_SCRATCH, pair, "ARM D2")
        a["exec_state_before"] = read_es("[D2] after the pair check, BEFORE the census calls",
                                         D2_SCRATCH, "D2")
        a["census_calls"] = []
        for label, fn in (("count('Node')", lambda: g.count(D2_SCRATCH, "Node")),
                          ("count('Wire')", lambda: g.count(D2_SCRATCH, "Wire")),
                          ("node_labels(top)", lambda: g.node_labels(D2_SCRATCH, TOP)),
                          ("node_terms(src)", lambda: g.node_terms(D2_SCRATCH, TOP,
                                                                   pair["src"]["node_i"])),
                          ("node_terms(sink)", lambda: g.node_terms(D2_SCRATCH, TOP,
                                                                    pair["sink"]["node_i"])),
                          ("report_all('Property')", lambda: g.report_all(D2_SCRATCH, "Property"))):
            val, err = safe("ARM D2 %s" % label, fn)
            rec = {"call": label,
                   "returned": (("%d rows" % len(val)) if isinstance(val, (list, tuple)) else val),
                   "error_verbatim": err}
            rec["exec_state_after"] = read_es("[D2] after %s" % label, D2_SCRATCH, "D2")
            a["census_calls"].append(rec)
        a["wire_count_after"], _ = safe("ARM D2 count(Wire)", lambda: g.count(D2_SCRATCH, "Wire"))
        a["node_count_after"], _ = safe("ARM D2 count(Node)", lambda: g.count(D2_SCRATCH, "Node"))
        a["exec_state_after"] = read_es("[D2] at the end of the control leg", D2_SCRATCH, "D2")
        fact("ARM D2 (NO EDIT): ExecState %r -> %r ; after each census call %r ; Wire %r -> %r ; "
             "Node %r -> %r"
             % (a.get("cold_exec_state"), a.get("exec_state_after"),
                [c["exec_state_after"] for c in a["census_calls"]], a.get("wire_count_before"),
                a.get("wire_count_after"), a.get("node_count_before"), a.get("node_count_after")))
        gate("D2_a the no-edit control ran on its own scratch and every reading is recorded",
             len(a["census_calls"]) == 6,
             "%d census calls ; ExecState %r -> %r"
             % (len(a["census_calls"]), a.get("cold_exec_state"), a.get("exec_state_after")))
    except Exception as e:                                                         # noqa: BLE001
        a["leg_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("ARM D2 LEG ABORTED: %s" % a["leg_error_verbatim"])
        gate("D2_a the no-edit control ran", False, a["leg_error_verbatim"])
    finally:
        a["scratch_exists"] = drop_scratch(D2_SCRATCH, "ARM D2")
        gate("Z_3b the ARM D2 scratch is deleted in the same run", not a["scratch_exists"], D2_SCRATCH)


def arm_d3(bed, pair):
    print("\n=== ARM D3  THE POSITIVE CONTROL: the SAME idempotent pair through `connect_nested_v1` - the "
          "op MEASURED to carry the `%s` readback" % BROKEN_ITEM, flush=True)
    a = R["arm_d3"]
    a["op"] = "build_opconnectnested_v1.connect_nested_v1 (tools/recipes/...:418) -> OpConnectNested_v1.vi"
    a["census_verdict_for_this_op"] = next((r.get("carries_broken_read") for r in
                                            R["c_census"].get("table", [])
                                            if r["op"] == "OpConnectNested_v1.vi"), None)
    try:
        a.update(fresh_bed(bed, D3_SCRATCH, "ARM D3 scratch", "D3"))
        a["pair_check"] = verify_pair(D3_SCRATCH, pair, "ARM D3")
        a["exec_state_before"] = read_es("[D3] immediately BEFORE connect_nested_v1", D3_SCRATCH, "D3")
        a["call"] = ("connect_nested_v1(target, sink_diag=%d, sink_node=%d, sink_term=%d, src_diag=%d, "
                     "src_node=%d, src_term=%d)"
                     % (TOP, pair["sink"]["node_i"], pair["sink"]["term_i"], TOP,
                        pair["src"]["node_i"], pair["src"]["term_i"]))
        fact("ARM D3 THE ONE CALL: %s   [the SAME pair ARM D1 connects, through the op WITH the reader]"
             % a["call"])
        buf = io.StringIO()
        t0 = time.time()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_ret, err = CONNECT_V1(D3_SCRATCH, TOP, pair["sink"]["node_i"],
                                             pair["sink"]["term_i"], TOP, pair["src"]["node_i"],
                                             pair["src"]["term_i"], V1_LABELS)
            a["wire_delta"], a["exec_state_returned_by_the_wrapper"], a["op_error"] = dw, es_ret, err
            a["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            a["wire_delta"], a["exec_state_returned_by_the_wrapper"], a["op_error"] = None, None, None
            a["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        a["call_cost_s"] = round(time.time() - t0, 1)
        a["op_stdout_verbatim"] = [ln.strip() for ln in buf.getvalue().rstrip().splitlines()]
        for ln in a["op_stdout_verbatim"]:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        a["wire_count_after"], _ = safe("ARM D3 count(Wire)", lambda: g.count(D3_SCRATCH, "Wire"))
        a["node_count_after"], _ = safe("ARM D3 count(Node)", lambda: g.count(D3_SCRATCH, "Node"))
        a["exec_state_after"] = read_es("[D3] immediately AFTER connect_nested_v1", D3_SCRATCH, "D3")
        a["pair_check_after"] = verify_pair(D3_SCRATCH, pair, "ARM D3 after")
        fact("ARM D3: ExecState %r -> %r ; wire_delta %r ; Wire %r -> %r ; Node %r -> %r ; op error %r ; "
             "call cost %rs"
             % (a.get("exec_state_before"), a.get("exec_state_after"), a.get("wire_delta"),
                a.get("wire_count_before"), a.get("wire_count_after"), a.get("node_count_before"),
                a.get("node_count_after"), a.get("op_error"), a.get("call_cost_s")))
        gate("D3_a the positive control ran on its own scratch and is recorded (NO ExecState value is "
             "asserted)",
             bool(a.get("pair_check", {}).get("src", {}).get("ok")
                  and a.get("pair_check", {}).get("sink", {}).get("ok")),
             "wire_delta %r ; ExecState %r -> %r ; error %r"
             % (a.get("wire_delta"), a.get("exec_state_before"), a.get("exec_state_after"),
                a.get("error_verbatim")))
    except Exception as e:                                                         # noqa: BLE001
        a["leg_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        fact("ARM D3 LEG ABORTED: %s" % a["leg_error_verbatim"])
        gate("D3_a the positive control ran", False, a["leg_error_verbatim"])
    finally:
        a["scratch_exists"] = drop_scratch(D3_SCRATCH, "ARM D3")
        gate("Z_3c the ARM D3 scratch is deleted in the same run", not a["scratch_exists"], D3_SCRATCH)


# ===================================================================== main
def main():
    print("=== diag_c64_readerfree  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== cycle 64 material #3: does a READER-FREE scripting edit perturb ExecState? PURE "
          "MEASUREMENT - nothing is built, no VI is saved, no route is chosen.", flush=True)
    print("=== NO g.open_panel call appears in this file. The two EDIT arms reach it only through the "
          "wrappers' own g.ensure_loaded (gscript.py:1268-1337); the read-only legs run first.", flush=True)

    # ---- F: files only, before any COM call
    print("\n=== F  DELETE claudeDev\\OpConnectNested_v2.vi (judgement's decision; the wrapper in "
          "tools/gscript.py is NOT touched)", flush=True)
    f_delete_v2("before the restart")
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
    s3 = probe("Z0d D1_s3a_focus_ind.vi (FATAL pin, never written)", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("Z0e the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("Z_0e OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5,
         dn.get("md5", "?"))
    v1 = probe("Z0f OpConnectNested_v1.vi (the op ARM D3 uses)", OP_V1)
    R["op_v1_md5_before"] = v1.get("md5")
    gate("Z_0f OpConnectNested_v1.vi md5 starts with %s" % OP_V1_MD5,
         str(v1.get("md5", "")).startswith(OP_V1_MD5), v1.get("md5", "?"))

    # ---- the pre-batch restart (44(e)); handles stood at 54,669 at the end of dispatch #2
    D.fresh("Z_R RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    f_delete_v2("after the restart")          # a file LabVIEW still held open before the restart
    gate("F_a claudeDev\\OpConnectNested_v2.vi is GONE", not os.path.exists(OP_V2),
         "%r ; attempts: %r" % (os.path.exists(OP_V2), R["f_delete_v2"].get("attempts")))
    dump()

    try:
        c_census()
    finally:
        dump()

    bed, pair = choose_bed()
    dump()

    for armfn in (arm_d2, arm_d1, arm_d3):    # the no-edit control first, then the edit, then the reader
        try:
            armfn(bed, pair)
        finally:
            dump()

    R["ref_counts"] = g.ref_counts()
    fact("tracked VI Server refs AFTER: %r" % (R["ref_counts"],))
    safe("g.reset", g.reset)
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    z4 = probe("Z1e the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    z5 = probe("Z1f OpConnectNested_v1.vi after everything", OP_V1)
    z6 = probe("Z1g the chosen bed op after everything", R["bed"]["path"])
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5,
         "%s" % (z4.get("md5"),))
    gate("Z_1c OpConnectNested_v1.vi is byte-unchanged across the run",
         z5.get("md5") == R.get("op_v1_md5_before"),
         "%r -> %r" % (R.get("op_v1_md5_before"), z5.get("md5")))
    gate("Z_1d the chosen bed op %s is byte-unchanged" % R["bed"]["chosen"]["op"],
         z6.get("md5") == R["bed"].get("md5_before"),
         "%r -> %r" % (R["bed"].get("md5_before"), z6.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1e refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    left = [p for p in SCRATCHES if os.path.exists(p)]
    gate("Z_1f EVERY scratch is gone (nothing is left on disk by this run)", not left,
         "still on disk: %r" % ([os.path.basename(p) for p in left],))

    print("\n=== THE COMPLETE TIMESTAMPED ExecState TIMELINE", flush=True)
    print("  %-4s %-4s %-58s %-12s %-10s" % ("step", "leg", "call / tag", "ExecState", "wall"), flush=True)
    for row in R["exec_state_timeline"]:
        print(("  %-4d %-4s %-58s %-12r %-10s" % (row["step"], row["leg"], row["tag"][:58],
                                                  row["exec_state"], row["wall_clock"]))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    print("\n=== THE THREE ARMS SIDE BY SIDE (bed: %s)" % R["bed"]["chosen"]["op"], flush=True)
    print("  %-6s %-46s %-10s %-10s %-11s %s"
          % ("arm", "what it did", "cold ES", "ES before", "ES after", "wire_delta"), flush=True)
    for key, what in (("arm_d2", "NO EDIT (control): read-only census calls"),
                      ("arm_d1", "connect_terminals (OpConnect_v0, reader-free?)"),
                      ("arm_d3", "connect_nested_v1 (carries the Broken? read)")):
        a = R[key]
        print(("  %-6s %-46s %-10r %-10r %-11r %r"
               % (key[-2:].upper(), what, a.get("cold_exec_state"), a.get("exec_state_before"),
                  a.get("exec_state_after"), a.get("wire_delta")))
              .encode("ascii", "replace").decode("ascii"), flush=True)

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
