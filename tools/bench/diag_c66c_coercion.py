"""diag_c66c_coercion - cycle 66 material #4, PART C. THE COERCION / DATA-TYPE MEASUREMENT, READ-ONLY.

WHY THIS RUN EXISTS. `Wire.Is Broken?` 6371004 catches a type-INCOMPATIBLE connection. It does NOT catch a
LEGAL coercion (DBL->SGL, DBL->I32), which leaves `ExecState` 1, leaves every object census correct, passes
every gate this project has ever run - and changes the numbers. So the indicator+Local substitution that S3a/S3b
built could have silently coerced the focus path and nothing in the gate set would have seen it. That is a
rule-1a question, and it is half of the question now standing with the user.

WHAT IS BEING MEASURED, IN TWO SEPARABLE HALVES:
  R  DO THE TWO PROPERTY IDS RESOLVE ON THIS MACHINE? `Terminal.Coercion Dot?` 634A006 (short name claimed
     `Coerced?`, Boolean) and `Terminal.Data Type` 634A008. They come from `archive/peer/2026-09-21-c66-m3-
     movelocals.md`, which OVERTURNED dispatch #2's `TYPE READ UNREACHABLE` (`tools/bench/diag_c66_s3b_m3.log:133`)
     - correctly, because dispatch #2 enumerated the EIGHT properties this project had already WRAPPED and
     absence from our own wrappers is not absence from LabVIEW's property surface. They are registered in
     `docs/NAMES.md` as UNVERIFIED and this run is what settles that word. Resolution is done THE WAY THIS FLEET
     HAS ALWAYS RESOLVED A PROPERTY SHORT NAME (`docs/NAMES.md:365` "read off the machine (probe_castfree5.log)"):
     `gscript.build_property` creates the node with the ID and the class string, LabVIEW's own creator raises
     error 1077 on an ID it does not accept (`tools/gscript.py:2215-2223`), and the created node's TERMINAL NAMES
     are then read back off the machine with `node_terms_uid`. ONLY a scratch duplicate of `claudeDev\\OpReport_v0.vi`
     is touched; it is created and deleted in the same run and NOTHING IS SAVED.
  T  THE TERMINAL TABLE over the three artefacts, each opened READ-ONLY and md5-pinned BEFORE and AFTER:
     per terminal uid/owner, owning node, terminal name, is_source, connected wire, the four error codes - and
     the `Data Type` / `Coerced?` columns filled if and only if a VALUE route exists (see V).
  V  THE VALUE ROUTE, machine-checked rather than asserted. Creating a property node proves an ID RESOLVES; it
     does not read a value off a real terminal. Every terminal value this fleet reads comes back through
     `OpNodeTerms_v0.vi`, whose property items are FIXED AT BUILD TIME - `tools/bench/opnodeterms_labels.json` is
     read here and its column set printed, so "there is no type column" is an OBSERVATION in this log, not a
     claim. If no wrapped column carries a type, the verdict is `VALUE READ NEEDS A NEW OP`, recorded as a GAP,
     and the `Data Type` / `Coerced?` cells read `UNREAD` - never `False`, which would be an inference.

WHAT ALREADY EXISTS, CHECKED BEFORE A LINE OF THIS FILE WAS WRITTEN (CLAUDE.md: most of this project's cost has
been rebuilding what it already owned):
  - `grep "^def " tools/gscript.py` - every verb here is ALREADY THERE: `exec_state`, `count`, `report_all`,
    `node_labels`, `node_terms_uid`, `panel_wiring`, `build_property`, `close_panel`, `ref_counts`. NO new verb,
    NO new op, NO edit to `tools/gscript.py`, NO edit to any `*_astcheck.py`, NO recipe written.
  - `tools/recipes/build_d1_v0.py:357` `diag_index` - the uid-addressed diagram-index reader. `move_in` from the
    same file is NOT imported and NOT called (this file is gated `--route owner`).
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - `OpWireSource_v5`, the ONLY BY-UID
    walk of a WIRE's own `Terms[]`, giving each terminal's OWNER class and uid. It is how both ends of every
    watched wire are found here WITHOUT a diagram scan.
  - `tools/bench/diag_c66b_s3b_m3.py` / `diag_c65_s3b_row2c.py` - every helper below is reused IN SHAPE.
  - `tools/bench/c60c_astcheck.py --route owner` - the static gate, run on THIS file before launch. NOT edited.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  Y   THE PINS: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 / D1_s3a_focus_ind eef91c1d /
      D1_s3b_row1 72f0d47d / D1_s3b_row2 26c54ff7 all byte-unchanged BEFORE **and** AFTER; `OpReport_v0.vi`'s own
      md5 identical before and after; the scratch `exists=False`; refs opened == closed == 0 live.
  R1  `build_property(scratch, "VI Server:Terminal", [("634A006", False)])` either creates ONE Property node or
      raises. EITHER OUTCOME IS A RESULT: the raw error text is reported VERBATIM if it raises.
  R2  the same for ("634A008", False).
  R3  for each ID that resolved, the created node's terminal table is read back and its non-standard terminal
      name IS THE SHORT NAME. PREDICTED: `Coerced?` and `Data Type`. A different string is reported as measured.
  T1  each artefact reopens COLD at `ExecState` 1 and `diag_index(#639)` resolves.
  T2  every watched wire has its endpoints reported by `wire_source_owner`; every named node's full terminal
      table is dumped with its own uid ECHOED back before it is believed.
  V1  the wrapped-column census READS `opnodeterms_labels.json` and prints its column set; the verdict is
      `A MEASURED TYPE IS AVAILABLE` iff some wrapped column carries a type, else `VALUE READ NEEDS A NEW OP`.
      PREDICTED: `VALUE READ NEEDS A NEW OP`. The gate is that the census was read - gating on "a type column
      exists" would manufacture a failing log out of the result we expect, which is how gate 7 of
      `c60c_astcheck.py` became a false firefighter signal (`tools/bench/cycle_runner.log:97,:100`).

🔴 NOTHING IS BUILT. NO `.vi` IS EDITED OR SAVED. `move_in`, `connect_nested_v1` and `wire_indicators` are
NEITHER IMPORTED NOR CALLED. No `g.open_panel`, no `allow_broken`, no `gui_save`, no GUI action, no new op, no
new verb, no cast, no splice (51(h)), no recipe, no `CYCLE_GUARD_OFF`. `retrospective.py` / `audit_cycle.py` /
`violations.py` / `doc_ingest.py` / `prior_art_review.py` are NOT run (54(a)). No route is chosen and none is
recommended; `docs/cycle27-plan.md` and STATUS's `## NEXT` are untouched. **A COERCION OR A TYPE MISMATCH FOUND
HERE IS REPORTED AND LEFT ALONE - it is a rule-1a finding for judgement and the user, never a defect this run
repairs.** VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)). Rig ASSEMBLED: no motor, no ASI, no camera, no
VI run.
"""
import json
import os
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
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"

# ---- THE THREE ARTEFACTS, ALL READ-ONLY, ALL PINNED -------------------------------------------------
A1_PATH = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")          # the UNDIVIDED state = the reference type
A1_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
A2_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")               # row 2 divided
A2_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
A3_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")               # row 1 divided
A3_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
OPREPORT = os.path.join(g.CLAUDEDEV, "OpReport_v0.vi")              # the scratch DONOR - pinned, never written

D639 = 639                        # the nested diagram the 1.5 set lives on, in every one of the three
SRC_UID = 10757                   # `Index Array`; t1 'element' is the numeric SOURCE
CASE_UID = 10407                  # the CaseStructure the focus path feeds
AND_UID = 10686                   # row 1's boolean source; t0 is 'x .and. y?'
LOCAL_ROW1_UID = 23499
LOCAL_ROW2_UID = 23523
IND_ROW2_UID = 23525              # row 2's indicator, a PANEL control uid

A1_WIRE = 10990                   # #10757 t1 'element' -> #10407 t2 : THE UNDIVIDED NET
A2_WIRE_SRC = 23556               # #10757 t1 -> panel control 23525
A2_WIRE_SINK = 23540              # Local #23523 -> #10407 t2
A3_WIRE_SINK = 23502              # Local #23499 -> #10407 t0

# THE TWO IDS UNDER TEST. Source: archive/peer/2026-09-21-c66-m3-movelocals.md (NI 'Coercion Dot?' property
# page; NI 'Coercion Dots'; NI Community 'Finding coercion dots?'). NOT guessed, and NOT yet read off this
# machine - which is what R measures. 634A001 `Type Descriptor` is WRITE-ONLY/deprecated and is not attempted.
PROP_IDS = [("Terminal.Coercion Dot?", "634A006", "Coerced?", "Boolean - True if a coercion dot is drawn"),
            ("Terminal.Data Type", "634A008", "Data Type", "the terminal's data type as a Variant")]
PROP_CLASS = "VI Server:Terminal"          # docs/NAMES.md:369 - the class string that already works here

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c66c_coercion.json")
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C66C_%s.vi" % STAMP)

RUN_DEADLINE_S = 25 * 60.0
RESERVE_S = 180.0

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 66 material #4 PART C: resolve Terminal.Coercion Dot? 634A006 and Terminal.Data Type "
             "634A008 the way this fleet resolves any property short name, and read the terminal table of the "
             "divided and undivided focus paths - READ-ONLY, nothing built, nothing saved",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "nothing_is_built": True, "no_vi_edited_or_saved": True,
     "move_in_not_imported_not_called": True, "connect_nested_v1_not_called": True,
     "wire_indicators_not_called": True,
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "no_property_id_guessed": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "repairs_nothing": "a coercion or a type mismatch found here is REPORTED, never repaired - rule 1a is "
                        "judgement's call and the user's, not this session's",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [],
     "stage_R": {}, "stage_T": {}, "stage_V": {}}
SR, ST, SV = R["stage_R"], R["stage_T"], R["stage_V"]


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
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


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def safe(label, fn, default=None):
    """Run one read, record its error VERBATIM, never let it kill the run."""
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:300])
        fact("%s raised %s" % (label, msg))
        return default, msg


def read_es(tag, target):
    t0 = time.time()
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag,
           "target": os.path.basename(target), "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def terms_at(path, diagram_index, nodes_index, expect_uid, tag, quiet=False):
    """The FULL terminal table of one node, with the node's own uid ECHOED back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, int(diagram_index), int(nodes_index))
        rec["uid_echo"] = echo
        rec["ok"] = (expect_uid is None) or (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["ok"] = False
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        rec["terminals"] = []
    if not quiet:
        fact("%s terminal table of #%s (Diagram idx %r, Nodes[%r], echo %r): %d terminal(s)"
             % (tag, expect_uid, diagram_index, nodes_index, rec.get("uid_echo"), len(rec["terminals"])))
        for t in rec["terminals"]:
            fact("    %s t%-2d %-34r is_source=%-5r wire=%-7r errs=%r"
                 % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


# =========================================================== PHASE 0 - files only, then ONE restart
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; dispatch #3 ended at 38,183, so the "
         "pre-batch restart below is MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
        pr = probe("Y %s BEFORE" % tag, path)
        gate("Y %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe("Y OpReport_v0 BEFORE", OPREPORT)
    R["opreport_md5_before"] = pr.get("md5")
    fact("OpReport_v0.vi md5 BEFORE (the scratch DONOR, never written): %r" % (pr.get("md5"),))

    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("D1_s2_loops", S2_ARTEFACT, S2_MD5),
        ("A1 D1_s3a_focus_ind (UNDIVIDED)", A1_PATH, A1_MD5),
        ("A2 D1_s3b_row2 (row 2 divided)", A2_PATH, A2_MD5),
        ("A3 D1_s3b_row1 (row 1 divided)", A3_PATH, A3_MD5))


# =========================================================== STAGE R - do the two IDs resolve?
def stage_R():
    print("\n---------- [R] DO 634A006 AND 634A008 RESOLVE ON THIS MACHINE? - the fleet's own short-name route",
          flush=True)
    fact("THE ROUTE, verbatim from docs/NAMES.md:365 and tools/gscript.py:2194-2269: build_property() asks "
         "LabVIEW's own creator for a Property Node of class %r carrying the ID; an ID the creator does not "
         "accept raises error 1077 from Set Properties[] and gscript re-raises it as a RuntimeError naming the "
         "ID. The created node's TERMINAL NAMES are then the short names, read back off the machine." % PROP_CLASS)
    fact("ONLY a scratch duplicate of OpReport_v0.vi is touched. It is created and deleted in this run, it is "
         "NEVER saved, and none of the three artefacts is opened for edit at any point.")
    shutil.copy2(OPREPORT, SCRATCH)
    pr = probe("[R] the scratch", SCRATCH)
    gate("R0 the scratch is a byte copy of OpReport_v0", pr.get("md5") == R.get("opreport_md5_before"),
         "%r" % (pr.get("md5"),))
    es = read_es("[R] the scratch, COLD", SCRATCH)
    gate("R0b the scratch reopens COLD at ExecState 1", es == 1, "%r" % (es,))

    SR["class"] = PROP_CLASS
    SR["ids"] = []
    y = 40
    for name, pid, claimed, meaning in PROP_IDS:
        rec = {"identifier": name, "id": pid, "short_name_claimed": claimed, "meaning": meaning,
               "source": "archive/peer/2026-09-21-c66-m3-movelocals.md - NOT yet read off this machine"}
        before, _e = safe("[R] uids('Property') before %s" % pid, lambda: g.uids(SCRATCH, "Property"), [])
        rec["property_uids_before"] = len(before or [])
        new, err = safe("[R] build_property(%s)" % pid,
                        lambda p=pid, yy=y: g.build_property(SCRATCH, PROP_CLASS, [(p, False)], (40, yy)))
        rec["raw_error"] = err
        rec["resolved"] = bool(new) and not err
        gate("R1 %s %s RESOLVES (build_property accepted the ID)" % (name, pid), rec["resolved"],
             ("raw error: %s" % err) if err else "new Property node(s): %r" % (new,))
        if rec["resolved"]:
            rec["new_uid"] = new[0].get("uid")
            fact("[R] %s %s -> new Property node uid %r" % (name, pid, rec["new_uid"]))
            rows, lerr = safe("[R] node_labels(0) after %s" % pid, lambda: g.node_labels(SCRATCH, 0), [])
            rec["node_labels_error"] = lerr
            idx = next((i for i, r in enumerate(rows or []) if r.get("uid") == rec["new_uid"]), None)
            rec["nodes_index"] = idx
            if idx is None:
                gate("R3 %s the new node is addressable on Diagram[0]" % pid, False,
                     "uid %r not in the %d-row Nodes[] list" % (rec.get("new_uid"), len(rows or [])))
            else:
                t = terms_at(SCRATCH, 0, idx, rec["new_uid"], "[R %s]" % pid)
                rec["terminal_table"] = t
                standard = ("reference", "reference out", "error in (no error)", "error out")
                names = [x["name"] for x in t.get("terminals", []) if x["name"] not in standard]
                rec["short_names_measured"] = names
                gate("R3 %s the created node carries exactly ONE non-standard terminal" % pid, len(names) == 1,
                     "%r" % (names,))
                if names:
                    rec["short_name_measured"] = names[0]
                    gate("R4 %s the measured short name is the claimed %r" % (pid, claimed),
                         names[0] == claimed, "measured %r" % (names[0],))
        SR["ids"].append(rec)
        y += 150
        dump()
    SR["verdict"] = ("BOTH IDS RESOLVE" if all(r["resolved"] for r in SR["ids"])
                     else "AT LEAST ONE ID DID NOT RESOLVE - see raw_error")
    fact("[R] *** VERDICT: %s ***" % SR["verdict"])


# =========================================================== STAGE V - is there a VALUE route at all?
def stage_V():
    print("\n---------- [V] IS THERE A VALUE ROUTE? - the wrapped-column census, read off the files", flush=True)
    lab_path = os.path.join(BENCH, "opnodeterms_labels.json")
    with open(lab_path, encoding="utf-8") as f:
        lab = json.load(f)
    cols = sorted(lab.values())
    SV["opnodeterms_labels_path"] = lab_path
    SV["opnodeterms_columns"] = cols
    fact("OpNodeTerms_v0's property items, FIXED AT BUILD TIME (%s): %r" % (os.path.basename(lab_path), cols))
    typeish = [c for c in cols if ("type" in c.lower() or "coerc" in c.lower())]
    SV["type_columns"] = typeish
    SV["verdict"] = ("A MEASURED TYPE IS AVAILABLE" if typeish else "VALUE READ NEEDS A NEW OP")
    # NOT a pass/fail on "a type column exists" - the PREDICTION is that none does, and a gate written the
    # other way round would manufacture a failing log out of a result we expect (37(i) / 55(h)). The gate is
    # that the census was READ; the verdict is a FACT either way.
    gate("V1 the wrapped-column census was read off opnodeterms_labels.json", bool(cols), "%d column(s)" % len(cols))
    fact("[V] type-bearing wrapped column(s): %r" % (typeish,))
    fact("[V] *** VERDICT: %s ***" % SV["verdict"])
    if not typeish:
        fact("[V] MECHANISM, so this is not mistaken for a missing ID: an ID that RESOLVES gives a property "
             "NODE, not a value. A value off a real terminal needs that node WIRED to a Terminal reference "
             "inside a SAVED op VI - a new op, which this dispatch forbids. The `Data Type` / `Coerced?` cells "
             "below therefore read UNREAD. UNREAD IS NOT False: nothing here says the path is un-coerced.")
    dump()


# =========================================================== STAGE T - the terminal tables
def wire_ends(path, wire_uid, tag):
    rows, err = safe("%s wire_source_owner(%d)" % (tag, wire_uid), lambda: WIRE_TERMS(path, wire_uid), [])
    rec = {"wire": wire_uid, "error": err, "terms": rows or []}
    fact("%s wire %d Terms[]: %r" % (tag, wire_uid, rows))
    return rec


def artefact(tag, path, pin, nodes_wanted, wires_wanted, panel_uids):
    print("\n---------- [T] %s  %s" % (tag, os.path.basename(path)), flush=True)
    rec = {"tag": tag, "path": path, "md5_pin": pin, "nodes": {}, "wires": {}, "panel": []}
    ST[tag] = rec
    rec["exec_state_cold"] = read_es("[T] %s COLD" % tag, path)
    gate("T1 %s reopens COLD at ExecState 1" % tag, rec["exec_state_cold"] == 1,
         "%r" % (rec["exec_state_cold"],))
    di, derr = safe("[T] %s diag_index(#%d)" % (tag, D639), lambda: diag_index(path, D639))
    rec["d639_index"], rec["d639_index_error"] = di, derr
    gate("T1b %s diag_index(#%d) resolves" % (tag, D639), isinstance(di, int), "%r %s" % (di, derr))
    labels, lerr = safe("[T] %s node_labels(%r)" % (tag, di),
                        lambda: g.node_labels(path, int(di)) if isinstance(di, int) else [], [])
    rec["nodes_on_d639"] = len(labels or [])
    rec["node_labels_error"] = lerr
    fact("[T] %s Diagram #%d = traverse index %r, %d node(s)" % (tag, D639, di, len(labels or [])))
    by_uid = {r.get("uid"): i for i, r in enumerate(labels or [])}
    for uid, why in nodes_wanted:
        idx = by_uid.get(uid)
        if idx is None:
            rec["nodes"][str(uid)] = {"why": why, "nodes_index": None,
                                      "note": "uid not in Diagram #%d's Nodes[] on this artefact" % D639}
            gate("T2 %s #%d is on Diagram #%d" % (tag, uid, D639), False, why)
            continue
        t = terms_at(path, di, idx, uid, "[T %s #%d]" % (tag, uid))
        t["why"] = why
        rec["nodes"][str(uid)] = t
        gate("T2 %s #%d terminal table read, uid echo matches" % (tag, uid), bool(t.get("ok")),
             "echo %r, %d terminal(s)" % (t.get("uid_echo"), len(t.get("terminals", []))))
        dump()
    for w, why in wires_wanted:
        if not w:
            continue
        e = wire_ends(path, w, "[T %s]" % tag)
        e["why"] = why
        rec["wires"][str(w)] = e
        gate("T3 %s wire %d walked by uid" % (tag, w), bool(e["terms"]) and not e["error"],
             "%d Terms[] row(s)%s" % (len(e["terms"]), (" ; " + e["error"]) if e["error"] else ""))
        dump()
    if panel_uids:
        rows, perr = safe("[T] %s panel_wiring" % tag, lambda: g.panel_wiring(path), [])
        rec["panel_error"] = perr
        for r in (rows or []):
            if r["uid"] in panel_uids:
                rec["panel"].append(r)
                fact("[T %s] panel control #%d %r indicator=%r is_source=%r wire=%r errs=[%r,%r]"
                     % (tag, r["uid"], r["label"], r["indicator"], r["is_source"], r["wire"],
                        r["term_err"], r["wire_err"]))
        gate("T4 %s every named panel control was found" % tag, len(rec["panel"]) == len(panel_uids),
             "%d of %d" % (len(rec["panel"]), len(panel_uids)))
    safe("close_panel(%s)" % tag, lambda: g.close_panel(path))
    dump()
    return rec


def stage_T():
    artefact("A1_UNDIVIDED", A1_PATH, A1_MD5,
             [(SRC_UID, "the numeric SOURCE; t1 'element' is the reference type"),
              (CASE_UID, "the CaseStructure; t2 is the sink of the undivided net"),
              (AND_UID, "row 1's boolean source; t0 is 'x .and. y?'")],
             [(A1_WIRE, "THE UNDIVIDED NET: #10757 t1 'element' -> #10407 t2")],
             [])
    if left_s() <= 0:
        gate("T0 wall-clock left for A2", False, "%.0f s" % left_s())
        return
    artefact("A2_ROW2_DIVIDED", A2_PATH, A2_MD5,
             [(SRC_UID, "the same numeric SOURCE, now feeding the panel indicator"),
              (CASE_UID, "t2 is now fed by the Local, not by #10757"),
              (LOCAL_ROW2_UID, "row 2's Local carrier")],
             [(A2_WIRE_SRC, "#10757 t1 -> panel control 23525"),
              (A2_WIRE_SINK, "Local #23523 -> #10407 t2")],
             [IND_ROW2_UID])
    if left_s() <= 0:
        gate("T0 wall-clock left for A3", False, "%.0f s" % left_s())
        return
    a3 = artefact("A3_ROW1_DIVIDED", A3_PATH, A3_MD5,
                  [(CASE_UID, "t0 is now fed by the Local"),
                   (LOCAL_ROW1_UID, "row 1's Local carrier"),
                   (AND_UID, "row 1's SOURCE net starts at t0 'x .and. y?'")],
                  [(A3_WIRE_SINK, "Local #23499 -> #10407 t0")],
                  [])
    # row 1's SOURCE net: whatever wire #10686 t0 carries on this artefact, walked by uid off the machine.
    and_rec = a3["nodes"].get(str(AND_UID)) or {}
    t0 = next((t for t in and_rec.get("terminals", []) if t["i"] == 0), None)
    src_wire = t0["wire"] if t0 else 0
    a3["row1_source_wire"] = src_wire
    fact("[T A3] row 1's SOURCE net: #%d t0 %r carries wire %r" % (AND_UID, (t0 or {}).get("name"), src_wire))
    if src_wire:
        e = wire_ends(A3_PATH, src_wire, "[T A3_ROW1_DIVIDED]")
        e["why"] = "row 1's source net: #10686 t0 'x .and. y?' -> its indicator"
        a3["wires"][str(src_wire)] = e
        gate("T3 A3_ROW1_DIVIDED row-1 source wire %d walked by uid" % src_wire,
             bool(e["terms"]) and not e["error"], "%d Terms[] row(s)" % len(e["terms"]))
    else:
        gate("T3 A3_ROW1_DIVIDED #%d t0 carries a wire" % AND_UID, False, "wire %r" % (src_wire,))
    dump()


# =========================================================== THE TABLE THE BRIEF ASKED FOR
def stage_table():
    print("\n---------- [X] THE TABLE: uid . owning node . terminal name . Data Type . Coerced?", flush=True)
    unread = SV.get("verdict") != "A MEASURED TYPE IS AVAILABLE"
    cell = "UNREAD" if unread else "see stage_T"
    rows = []
    print("    %-18s %-10s %-12s %-30s %-8s %-9s %-14s %s"
          % ("artefact", "owner", "terminal", "name", "source?", "wire", "Data Type", "Coerced?"), flush=True)
    for tag, rec in ST.items():
        for uid, t in sorted(rec.get("nodes", {}).items()):
            for term in t.get("terminals", []):
                row = {"artefact": tag, "owner_node": int(uid), "terminal_index": term["i"],
                       "terminal_name": term["name"], "is_source": term["is_source"], "wire": term["wire"],
                       "errs": term["errs"], "data_type": cell, "coerced": cell}
                rows.append(row)
                print(("    %-18s #%-9s t%-11d %-30r %-8r %-9r %-14s %s"
                       % (tag, uid, term["i"], term["name"], term["is_source"], term["wire"], cell, cell))
                      .encode("ascii", "replace").decode("ascii"), flush=True)
    R["table"] = rows
    fact("[X] %d terminal row(s) tabulated across %d artefact(s)" % (len(rows), len(ST)))
    print("\n---------- [X2] THE PLAIN STATEMENT, PER ROW", flush=True)
    for tag in ("A1_UNDIVIDED", "A2_ROW2_DIVIDED", "A3_ROW1_DIVIDED"):
        if tag not in ST:
            fact("[X2] %s: NOT REACHED in this run" % tag)
            continue
        if unread:
            fact("[X2] %s: does ANY terminal on this path report Coerced? True -> **UNMEASURED**. No wrapped "
                 "column of this fleet carries a coercion flag or a data type, so the question is OPEN, not "
                 "answered False. Do the divided path's types match A1's reference type -> **UNMEASURED** for "
                 "the same reason. What IS measured for this artefact is every terminal's NAME, is_source, "
                 "connected wire and error codes, above." % tag)
        else:
            fact("[X2] %s: see the Data Type / Coerced? columns above." % tag)
    dump()


def main():
    print("=== diag_c66c_coercion  %s  (bgrun --material --max-min 25)" % STAMP, flush=True)
    try:
        phase_0()
        stage_V()
        stage_R()
        stage_T()
        stage_table()
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        for p in (SCRATCH, A1_PATH, A2_PATH, A3_PATH):
            safe("close_panel(%s)" % os.path.basename(p), lambda q=p: g.close_panel(q))
        if os.path.exists(SCRATCH):
            safe("remove the scratch", lambda: os.remove(SCRATCH))
        gate("Y the scratch is gone (exists=False)", not os.path.exists(SCRATCH), SCRATCH)
        print("\n---------- [Y] THE md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in PINS:
            pr = probe("Y %s AFTER" % tag, path)
            gate("Y %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        pr = probe("Y OpReport_v0 AFTER", OPREPORT)
        gate("Y OpReport_v0.vi md5 is unchanged", pr.get("md5") == R.get("opreport_md5_before"),
             "before %r after %r" % (R.get("opreport_md5_before"), pr.get("md5")))
        rc, _e = safe("ref_counts", lambda: g.ref_counts(), {})
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", (rc or {}).get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        fact("THE FILES THIS RUN LEFT ON DISK: [] (nothing is built and nothing is saved)")
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
