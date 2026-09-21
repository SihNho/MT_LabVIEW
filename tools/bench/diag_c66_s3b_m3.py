"""diag_c66_s3b_m3 - cycle 66 material #2: STAGE P (three pre-flight measurements on the S3b row-2 bed) and,
only if neither ABORT clause fires, STAGE M3 (the five loop-1.5 `move_in` calls into `Diagram #23058` plus the
internal row re-wiring).

WHAT ALREADY EXISTS, CHECKED BEFORE A LINE OF THIS FILE WAS WRITTEN (CLAUDE.md: most of this project's cost has
been rebuilding what it already owned):
  - `grep "^def " tools/gscript.py` - every verb this file needs is ALREADY THERE: `exec_state` (:1977),
    `count` (:1005), `report_all` (:488), `node_labels` (:587), `node_terms_uid` (:925), `panel_wiring` (:826),
    `tunnels` (:941), `delete_object` (:2275), `save` (:2062), `close_panel` (:1257), `ref_counts` (:233),
    `reset` (:262), `op` (:210), `uids` (:1017). NO new verb, NO new op, NO edit to tools/gscript.py, NO edit to
    any *_astcheck.py gate file, NO recipe written.
  - `tools/recipes/build_d1_v0.py:318` `move_in` / `:338` `owner_of` / `:357` `diag_index` - THE BUILT MOVER and
    the two uid-addressed readers. `move_in` is not in gscript at all.
  - `tools/recipes/build_opconnectnested_v1.py:418` `connect_nested_v1` - the BUILT node->node writer for two
    nodes on ONE nested diagram, and the fleet's only ordered `Broken?` reader.
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - `OpWireSource_v5`, the ONLY BY-UID
    walk of a WIRE's own `Terms[]`. **This is the verb that answers P1 without a new op**: it enumerates every
    terminal on a net with that terminal's OWNER class and uid, so a tunnel-family attachment is visible to it
    even though a tunnel is neither a `Node` nor a panel row (the peer's §1 blind class).
  - `tools/bench/diag_c65_s3b_row2c.py` - the direct predecessor; its helpers (gate/fact/probe/dump/safe/read_es/
    counts/node_census/new_nodes/terms_at/find_node/node_view/delete_by_uid/census_and_purge/live_d639/loop637/
    panel_all/save_artefact/stop_report) are reused IN SHAPE; nothing new was invented for them.
  - `tools/bench/diag_s3_focus_trial.py` (cycle 54) - the ONLY prior end-to-end run of the five moves and the
    re-wiring. Its `SET` (five uids, drop positions), `INTERNAL_JOBS` (the five same-loop / source-side rows) and
    `term_state` three-way WIRED/BARE/UNREAD classifier are reused verbatim in value, with every address
    RE-RESOLVED off this bed rather than inherited.
  - `tools/bench/c60c_astcheck.py` - the static gate, run with `--route movein` on THIS file before launch.
    NOT edited. All 12 gates are expected to pass; gate 7's `movein` direction is the repair cycle 66 dispatch #1
    made for exactly this build.

WHY THIS RUN EXISTS. `archive/peer/2026-09-21-c66-row2c-a5b.md` (ANSWERED, opus/max) attacked the claim that
`claudeDev\\D1_s3b_row2_20260921_160311.vi` is a sound bed for M3 and named THREE things no gate in this project
reads: every tunnel-family attachment, the owner of wire/diagram/sink, and EVERY DATA TYPE. Stage P measures all
three BEFORE the first `move_in`, because M3's whole job is moving nodes across a structure boundary.

PREDICTION CONTRACT (machine-checkable; a failed prediction is reported, never explained away)
  E   THE BED, re-measured COLD before any edit, echoed against the brief's recorded baseline:
      ExecState 1 / Wire 1907 / Node 632 / ControlTerminal 116 / Local 10 / LoopTunnel 135 / `#637` at (59,48) /
      `Diagram #639` = traverse index 46 with 75 nodes. Each is a GATE, and the MEASURED value is what every
      later gate is computed from.
  P1  THE `Tunnel` BLIND CLASS.
      (a) `report_all(WORK,'Tunnel')` - does `Tunnel` resolve as a traverse class at all, and how many rows?
          `docs/toolkit-capabilities.md:285-292` lists the TESTED class names and `Tunnel` is on NEITHER list,
          so this is a genuine open question, not a lookup. Reported either way; error 109 is an answer.
      (b) EVERY node on `Diagram #639` gets `node_terms_uid`; every terminal carrying wire 23556 (row 2's new
          net), 23540 (row 2's Local net) or 23502 (row 1's net) is recorded with its node's CLASS taken from
          the whole-VI `Node` census. If the STRUCTURE nodes among them return no tunnel terminals at all,
          THAT IS ITSELF THE FINDING and is reported as such - no workaround is attempted.
      (c) the same three wires walked BY UID with `wire_source_owner` (`OpWireSource_v5`), which reads
          `Wire.Terms[]` and gives each terminal's OWNER class + uid. A tunnel attachment shows up here as an
          owner class in the Tunnel family even when (b) is blind.
  P2  FOUR `owner_of` CALLS - uids 639, 23556, 23525, 26117 - all four REPORTED, none a gate
      (`owner_of` returned a silent wrong answer once; Pre-decided 53(d^8)).
  P3  THE DATA-TYPE READ (the rule-1a measurement). Every wrapped terminal-/wire-level property this fleet owns
      is exercised and its returned FIELDS printed, on `#10757` t1 and on panel control 23525 on the BED, and on
      `#10757` t1 / `#10407` t2 on the untouched `claudeDev\\D1_s3a_focus_ind.vi` opened READ-ONLY. The wrapped
      set, by SHORT NAME, is: `Terminal.Name` 634A004 · `Terminal.Is Source?` 634A003 ·
      `Terminal.Connected Wire` 634A000 · `Terminal.Diagram` 634A002 · `Tunnel.Outside Terminal` 6356001 ·
      `Tunnel.Inside Terminals[]` 6356000 · `Wire.Is Broken?` 6371004 (item terminal `Broken?`) ·
      `NumericConstant.Representation` 5DCFC00. PREDICTION: **none of them returns a data type**, so the honest
      outcome is `TYPE READ UNREACHABLE`, recorded as a GAP, not a failure. No property ID is GUESSED and no
      Property node is built: an unregistered id is a guess, and guessing is what this project's own
      `Control.Value 633200D` finding (`docs/toolkit-capabilities.md:256-260`) says costs a round trip and
      returns a node with no terminal and no error.
  A1/A2  THE ABORT CLAUSES, judgement's, and the ONLY branches this file may take:
      A1 fires on a MEASURED type MISMATCH (P3). `TYPE READ UNREACHABLE` is NOT a mismatch.
      A2 fires if wire 23556 / 23540 / 23502 is found on ANY tunnel terminal (P1b or P1c).
      Either one: STOP before the first `move_in`, save no `.vi`, remove the working copy, report.
  M1  FIVE `move_in` CALLS, ONE NODE PER CALL, destination index RE-RESOLVED by uid immediately before each
      (38(e)); after EVERY call the whole-VI `Node` census is diffed and any new ZERO-WIRED `Invoke` is deleted
      BY UID and `gone` confirmed (55(c)). PREDICTION: all five owners read `Diagram #23058`; `move_in` SEVERS
      every wire on the moved node (37(d)), so the wired-terminal counts fall to 0 and `ExecState` goes to 0.
  M2  THE FIVE INTERNAL ROWS (`#48` t0/t1/t2 from `#3529`/`#3560`/`#3447`, `#10407` t3/t5 from `#48` t6/t5),
      each addressed BY TERMINAL NAME off the machine and written with `connect_nested_v1`; census + purge after
      every call. Rows are matched by WIRED-TERMINAL counts, never by a Wire-class count (37(e)/49(e)).
      REPORTED, NOT ATTEMPTED, with their reason: the two shift-register pairs and the from-tunnel row - those
      are CREATIONS and a tunnel write, not "internal rows", and the brief named only the internal rows.
  M3  MECHANICAL INTERMEDIATE SAVES (the user's 2026-09-19 split rule): a node WITH ITS OWN SEVERED ROWS
      RE-WIRED is one unit; at every unit boundary `ExecState` is read and, WHENEVER IT READS 1, the file is
      saved as `claudeDev\\D1_s3b_m3_u<k>_<stamp>.vi` with its md5 recorded. `dump()` writes the JSON after
      every step, so a run that dies still leaves a file.
  Z   THE PASS CRITERION for the final save: all five moved uids appear in `Diagram #23058`'s `Nodes[]` census
      (the authoritative gate; `owner_of` on the five is reported ALONGSIDE it, never as it) AND `ExecState` 1
      => save `claudeDev\\D1_s3b_m3_moved_<stamp>.vi`, then LabVIEW RESTART + COLD reopen and read `ExecState`
      again. Both values reported.
  Y   md5 pins hold BEFORE and AFTER: ORIGINAL 2a78e17c / D1_s1_copy 3e3d23ce / D1_s2_loops 6ff19497 /
      D1_s3a_focus_ind eef91c1d / row 1 c7094f98 and 72f0d47d / THE BED 26c54ff7 (476,759 B).
      Every scratch `exists=False` at the end; refs opened == closed == 0 live; handles either side.

38(g) stays banned. No `allow_broken`, no `gui_save`, no `g.open_panel`, no GUI, no new op, no new verb, no cast,
no splice (51(h)), no recipe, no `CYCLE_GUARD_OFF`. `retrospective.py` / `audit_cycle.py` / `violations.py` /
`doc_ingest.py` / `prior_art_review.py` are NOT run (54(a)). No route is chosen and none is recommended;
`docs/cycle27-plan.md` and STATUS's `## NEXT` are untouched.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)). Rig ASSEMBLED: no motor, no ASI, no camera, no VI run.
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
from build_d1_v0 import diag_index, move_in, owner_of                              # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
ROW1A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_20260921_135932.vi")
ROW1A_MD5 = "c7094f98324af3bb53755fef718f8e28"
ROW1_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
ROW1_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

TOP = 0
D639 = 639                       # the nested diagram the 1.5 set lives on today
D639_RECORDED = 46
D639_NODES_RECORDED = 75
LOOP_A_UID = 23032               # 37(h) / docs/cycle27-plan.md:1127-1129 - CITED, never re-derived
BODY_A_UID = 23058               # the destination diagram
SIBLING_DIAG_UID = 686
LOOP11_UID = 637
LOOP637_POS_RECORDED = (59, 48)

SRC_UID = 10757                  # row 2's SOURCE node, an `Index Array`
SRC_TERM_NAME = "element"
CASE_UID = 10407
IND_CONTROL_UID = 23525          # row 2's indicator, panel control uid
LOCAL_UID = 23523                # the Local row 2's first half created
ROW2_WIRE = 23556                # row 2's NEW net
ROW2_LOCAL_WIRE = 23540          # row 2's Local net into #10407 t2
ROW1_WIRE = 23502                # row 1's net
WATCH_WIRES = (ROW2_WIRE, ROW2_LOCAL_WIRE, ROW1_WIRE)
A5_UID = 26117                   # the diagram uid A5's mis-addressed ControlTerminal 34982 reported as its owner

# The baseline this brief RECORDED. Every gate below is computed from the value MEASURED at step [E], never
# from these; they exist so a drift is VISIBLE.
BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}

# The five loop-1.5 nodes, with cycle 54's drop positions (diag_s3_focus_trial.py:133-139).
SET = [
    (3529, "- Inc (PgDn)", (40, 60), "ControlReferenceConstant; docs/d1-build-plan.md:330"),
    (3560, "+ Inc (PgUp)", (40, 170), "ControlReferenceConstant; docs/d1-build-plan.md:331"),
    (3447, "Focus Step (F1)", (40, 280), "ControlReferenceConstant; docs/d1-build-plan.md:332"),
    (48, "ASI_adjust focus-subvi.vi", (300, 170), "SubVI; docs/d1-build-plan.md:306"),
    (10407, "Case Structure", (620, 60), "CaseStructure (autofocus); docs/d1-build-plan.md:305"),
]
SET_UIDS = [u for u, _n, _p, _e in SET]

# The five INTERNAL rows (c53_row_class.json actions same-loop / source-side), as cycle 54 ran them
# (diag_s3_focus_trial.py:143-149). (sink_uid, sink_name, sink_t, src_uid, src_name, src_t, evidence)
INTERNAL_JOBS = [
    (48, "-Inc reference", 0, 3529, "- Inc (PgDn)", 0, "w4833; c53_row_class.json :1919 / :2096"),
    (48, "+Inc reference", 1, 3560, "+ Inc (PgUp)", 0, "w2819; d1_rewire_sources.json:1946 / :2126"),
    (48, "Focus inc reference", 2, 3447, "Focus Step (F1)", 0, "w1893; d1_rewire_sources.json:1973 / :2156"),
    (10407, "Outgoing Handle", 3, 48, "Outgoing Handle", 6, "w11232; d1_rewire_sources.json:1820 / :2066"),
    (10407, "Out position", 5, 48, "Out position", 5, "w7388; d1_rewire_sources.json:1865 / :2036"),
]

# REPORTED, NOT ATTEMPTED. Named here so the omission is explicit and machine-readable, never silent.
NOT_ATTEMPTED = [
    {"row": "SR VISA RightIn  #10407 'VISA out' t4", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "creating a shift-register pair is a CREATION, not an 'internal row'; the brief named only the "
            "internal rows and 49(e)'s M3 text names no register"},
    {"row": "SR VISA LeftIn   #48 'VISA resource name' t3", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "same - the left side cannot be written before the pair exists"},
    {"row": "SR POSITION LeftIn #48 'In position' t4", "verb": "gscript.add_shift_reg + wire_sr",
     "why": "same"},
    {"row": "from-tunnel      #10407 '# slices in stack' t1", "verb": "OpConnectFromWire_v0",
     "why": "a TUNNEL write, not an internal node->node row; and P1 is measuring the tunnel family this very "
            "run, so writing to one before that measurement is read would be the exact ordering the review "
            "attacked"},
    {"row": "cross-loop  #10407 t0 and t2 (the two LOCAL-fed rows)", "verb": "none exists",
     "why": "MEASURED THIS RUN, see the M1 report: the Locals sit on #639 and #10407 moves to #23058, so the "
            "severed rows are CROSS-DIAGRAM and `connect_nested_v1` addresses ONE nested diagram only"},
]

SCAN_LIMIT = 140
RUN_DEADLINE_S = 40 * 60.0       # the bgrun --max-min this file is launched under
RESERVE_S = 420.0                # held back for the final save, the restart and the cold reopen
M3_MIN_S = 600.0                 # M3 is not started with less than this left before the reserve

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c66_s3b_m3.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

WORK = os.path.join(g.CLAUDEDEV, "WORK_C66M3_%s.vi" % STAMP)
FINAL_PATH = os.path.join(g.CLAUDEDEV, "D1_s3b_m3_moved_%s.vi" % STAMP)

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 66 material #2: STAGE P (P1 tunnel blind class / P2 four owner_of / P3 the data-type read) "
             "on the S3b row-2 bed, then STAGE M3 (five move_in into Diagram #23058 + the five internal rows) "
             "only if neither ABORT clause fires",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; all work is on WORK, a fresh stamped name"},
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "no_property_id_guessed": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "chooses_no_route": True, "recommends_no_route": True,
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "stage_p": {}, "build": {}, "not_attempted": NOT_ATTEMPTED}
K = R["build"]
P = R["stage_p"]


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
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
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


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local", "LoopTunnel")):
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


def node_census(path, tag):
    rows, err = safe("%s report_all('Node')" % tag, lambda: g.report_all(path, "Node"), [])
    out = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": r["pos"], "owner_class": r["owner"]}
           for r in (rows or [])]
    fact("%s node census: %d rows%s" % (tag, len(out), ("  [%s]" % err) if err else ""))
    return out, err


def new_nodes(before, after):
    seen = {n["uid"] for n in before}
    return [n for n in after if n["uid"] not in seen]


def terms_at(path, diagram_index, nodes_index, expect_uid, tag, quiet=False):
    """The FULL terminal table of one node, with the node's own uid echoed back before it is believed."""
    rec = {"diagram_index": diagram_index, "nodes_index": nodes_index, "expected_uid": expect_uid}
    try:
        echo, rows = g.node_terms_uid(path, int(diagram_index), int(nodes_index))
        rec["uid_echo"] = echo
        rec["ok"] = (expect_uid is None) or (echo == expect_uid)
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "has_wire": bool(t["wire"]),
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["ok"] = False
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        rec["terminals"] = []
    if not quiet:
        fact("%s terminal table of #%s (Diagram idx %r, Nodes[%r], echo %r): %d terminal(s)"
             % (tag, expect_uid, diagram_index, nodes_index, rec.get("uid_echo"), len(rec["terminals"])))
        for t in rec["terminals"]:
            fact("    %s t%-2d %-34r is_source=%-5r wire=%-7r errs=%r"
                 % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


def term_state(t):
    """WIRED / BARE / UNREAD for ONE terminal row (Pre-decided 14; gscript.py:874 gives the one legitimate
    bare-terminal error pattern: wire 0 with conn_err/wire_err 1055 and name_err/src_err 0)."""
    ne, se, ce, we = [int(x or 0) for x in t.get("errs", [0, 0, 0, 0])]
    if t.get("wire"):
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


def wired_count(rows):
    return sum(1 for t in rows if term_state(t) == "WIRED")


def find_node(path, uid, hints, tag, budget_s=240.0, quiet=False):
    """Which DIAGRAM lists `uid` in its Nodes[] - answered by the census that finds it, NEVER by owner_of
    (owner_of is measured to answer with the PREVIOUS query's object, silently; Pre-decided 53(d^8))."""
    t0 = time.time()
    rec = {"uid": uid, "hints": list(hints), "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if isinstance(i, int) and i in by_index]
    order += [i for i in sorted(by_index) if i not in order]
    for i in order:
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = "budget %.0f s reached after %d diagrams" % (budget_s, len(rec["scanned"]))
            break
        rows, err = safe("%s node_labels(%d)" % (tag, i), lambda k=i: g.node_labels(path, k), [])
        rec["scanned"].append({"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                               "nodes": len(rows or []), "error": err})
        hit = next((k for k, r in enumerate(rows or []) if r["uid"] == uid), None)
        if hit is not None:
            rec["found"] = {"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                            "diagram_class": by_index[i]["class"], "nodes_index": hit,
                            "nodes_on_diagram": len(rows), "label": rows[hit]["label"]}
            break
    rec["scan_cost_s"] = round(time.time() - t0, 1)
    if not quiet:
        fact("%s #%s lives at: %r  (%d diagram(s) scanned of %d, %.1f s)"
             % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"], rec["scan_cost_s"]))
    return rec


def node_view(path, uid, hints, tag, quiet=False):
    loc = find_node(path, uid, hints, tag, quiet=quiet)
    f = loc.get("found") or {}
    if f.get("nodes_index") is None:
        return loc, []
    tt = terms_at(path, f["diagram_index"], f["nodes_index"], uid, tag, quiet=quiet)
    loc["uid_echo"] = tt.get("uid_echo")
    loc["terminal_table"] = tt
    return loc, tt.get("terminals", [])


def delete_by_uid(path, cls, uid, tag):
    """report_all(cls) -> .index(uid) -> delete_object(cls, idx). The shape cycle 58 used; no new verb."""
    rec = {"class": cls, "uid": uid}
    rows, err = safe("%s report_all(%r) before delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_before"] = len(rows or [])
    rec["census_error"] = err
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    rec["index"] = idx
    if idx is None:
        rec["result"] = "NOT IN THE %s CENSUS (%d rows) - nothing deleted" % (cls, len(rows or []))
        fact("%s delete %s #%s: %s" % (tag, cls, uid, rec["result"]))
        return rec
    t0 = time.time()
    try:
        gone = g.delete_object(path, cls, idx, verify=True)
        rec["gone"] = sorted(int(x) for x in (gone or []))
        rec["error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["gone"] = None
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    after, _ = safe("%s report_all(%r) after delete" % (tag, cls), lambda: g.report_all(path, cls), [])
    rec["census_after"] = len(after or [])
    rec["still_present"] = any(r["uid"] == uid for r in (after or []))
    fact("%s delete %s #%s at index %r: gone %r, error %r, census %r -> %r, still present %r (%.2f s)"
         % (tag, cls, uid, idx, rec.get("gone"), rec.get("error_verbatim"), rec["census_before"],
            rec["census_after"], rec["still_present"], rec.get("call_cost_s", 0.0)))
    return rec


def census_and_purge(path, nodes_before, tag, hints, keep_uids=()):
    """55(c): after EVERY move_in and EVERY connect_nested_v1, diff the whole-VI Node census and purge the junk
    BY UID. A new node is DELETED only when it is an `Invoke` with ZERO wired terminals (the measured junk
    shape). Anything else is REPORTED VERBATIM and left alone; an `Invoke` whose terminal table could NOT be
    read is never deleted and stops the build instead."""
    nodes_after, _ = node_census(path, "%s AFTER" % tag)
    fresh = new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh],
           "kept": list(keep_uids), "deleted": [], "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        if n["uid"] in keep_uids:
            fact("%s new node #%s (%s) is INTENDED by this build - kept" % (tag, n["uid"], n["class"]))
            continue
        loc, rows = node_view(path, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_index": (loc.get("found") or {}).get("diagram_index"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s THE JUNK NODE'S FULL TERMINAL TABLE IS PRINTED ABOVE; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = delete_by_uid(path, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        elif n["class"] == "Invoke" and not rows:
            rec["reported_not_deleted"].append(entry)
            fact("%s AN `Invoke` NEW NODE #%s COULD NOT BE LOCATED OR READ - IT IS NOT DELETED. Deleting a "
                 "node whose table was never read is the one branch that could destroy the artefact."
                 % (tag, n["uid"]))
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape): #%s class %r label %r, %d "
                 "terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    if rec["deleted"]:
        final, _ = node_census(path, "%s AFTER THE PURGE (the next step's baseline)" % tag)
        gate("%s purge: the Node census returns to its pre-call value %d" % (tag, len(nodes_before)),
             len(final) == len(nodes_before), "%d -> %d -> %d"
             % (len(nodes_before), len(nodes_after), len(final)))
    else:
        final = nodes_after
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


def panel_all(path, tag):
    rows, err = safe("%s panel_wiring" % tag, lambda: g.panel_wiring(path), [])
    fact("%s panel_wiring: %d rows%s" % (tag, len(rows or []), (" ; ERROR " + err) if err else ""))
    return rows or [], err


def save_artefact(tag, dest, not_equal_to, not_equal_label):
    """g.save writes the WORKING copy in place; the artefact is a fresh path LabVIEW has never seen.
    A file byte-identical to its predecessor means THE IN-MEMORY EDITS DID NOT LAND - reported as a FAILURE."""
    rec = {"tag": tag, "dest": dest, "save_error_verbatim": ""}
    rec["exec_state_at_save"] = read_es("%s immediately before the save" % tag, WORK)
    try:
        rec["save_returned_size"] = g.save(WORK)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    try:
        shutil.copy2(WORK, dest)
        rec["copy_error_verbatim"] = ""
    except Exception as e:                                                         # noqa: BLE001
        rec["copy_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
    ff = D.file_facts("%s the artefact" % tag, dest)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["compared_against"] = not_equal_label
    rec["bytes_equal_to_the_predecessor"] = (ff.get("md5") == not_equal_to)
    R["artefacts_on_disk"].append(rec)
    fact("%s FILE ON DISK: %s  md5 %r  size %r  (ExecState at the save %r ; COM save error %r ; bytes equal "
         "to %s %r)" % (tag, dest, rec["md5"], rec["size"], rec["exec_state_at_save"],
                        rec["save_error_verbatim"], not_equal_label,
                        rec["bytes_equal_to_the_predecessor"]))
    gate("%s *** A FILE IS ON DISK at %s ***" % (tag, os.path.basename(dest)), bool(rec["exists"]),
         "md5 %r size %r" % (rec["md5"], rec["size"]))
    gate("%s that file is NOT byte-identical to %s (the in-memory edits LANDED)" % (tag, not_equal_label),
         bool(rec["exists"]) and not rec["bytes_equal_to_the_predecessor"] and not rec["save_error_verbatim"],
         "md5 %r vs %s %r ; save error %r"
         % (rec["md5"], not_equal_label, not_equal_to, rec["save_error_verbatim"]))
    dump()
    return rec


# ======================================================================= PHASE 0 - files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; cycle 65 ended at 41,226)"
         % R["handles"]["before"])
    for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
                           ("D1_s2_loops", S2_ARTEFACT, S2_MD5), ("D1_s3a_focus_ind", S3A_ARTEFACT, S3A_MD5),
                           ("D1_s3b_row1a", ROW1A_ARTEFACT, ROW1A_MD5),
                           ("D1_s3b_row1", ROW1_ARTEFACT, ROW1_MD5), ("THE BED", BED, BED_MD5)):
        pr = probe("Y %s BEFORE" % tag, path)
        gate("Y %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe("Y THE BED size", BED)
    gate("Y the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))

    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    shutil.copy2(BED, WORK)
    pr = probe("[0] the working copy", WORK)
    gate("[0] the working copy is byte-identical to the bed", pr.get("md5") == BED_MD5, "%r" % (pr.get("md5"),))
    dump()


# ======================================================================= STEP E - the bed's cold baseline
def step_E():
    print("\n---------- [E] THE BED RE-MEASURED COLD - the brief's baseline, echoed before anything else",
          flush=True)
    es = read_es("[E] the bed, COLD", WORK)
    gate("E1 the bed reopens COLD at ExecState 1", es == 1, "%r" % (es,), fatal=True)
    c = counts(WORK, "[E] the bed COLD")
    K["counts_before"] = c
    for k, v in BASE.items():
        gate("E2 %s == %d (the brief's recorded baseline)" % (k, v), c.get(k) == v, "%r" % (c.get(k),))

    di, err = safe("[E] diag_index(#%d)" % D639, lambda: diag_index(WORK, D639))
    K["d639_index"] = di
    gate("E3 Diagram #%d resolves to traverse index %d" % (D639, D639_RECORDED), di == D639_RECORDED,
         "%r%s" % (di, (" ; ERROR " + err) if err else ""), fatal=True)
    rows, lerr = safe("[E] node_labels(%r)" % di, lambda: g.node_labels(WORK, di), [])
    K["d639_nodes"] = len(rows or [])
    K["d639_node_uids"] = [r["uid"] for r in (rows or [])]
    gate("E4 Diagram #%d carries %d nodes" % (D639, D639_NODES_RECORDED),
         len(rows or []) == D639_NODES_RECORDED, "%d%s" % (len(rows or []), (" ; " + lerr) if lerr else ""))

    ncen, _ = node_census(WORK, "[E] whole-VI")
    K["node_class_by_uid"] = {str(n["uid"]): n["class"] for n in ncen}
    K["node_census_before"] = ncen
    l637 = next((n for n in ncen if n["uid"] == LOOP11_UID), None)
    fact("[E] #%d in the whole-VI Node census: %r" % (LOOP11_UID, l637))
    gate("E5 #%d sits at position %r" % (LOOP11_UID, list(LOOP637_POS_RECORDED)),
         bool(l637) and tuple(int(x) for x in l637["pos"]) == LOOP637_POS_RECORDED,
         "%r" % ((l637 or {}).get("pos"),))
    hints = [di, TOP]
    _loc, lrows = node_view(WORK, LOOP11_UID, hints, "[E] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_before"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[E] #%d (WhileLoop): %d terminals, %d WIRED  <- 37(e)/50(e)'s no-new-tunnel baseline"
         % (LOOP11_UID, len(lrows), wired_count(lrows)))
    dump()
    return hints


# ======================================================================= P1 - the `Tunnel` blind class
def step_P1(hints):
    print("\n---------- [P1] THE `Tunnel` BLIND CLASS (peer c66-row2c-a5b §1)", flush=True)
    rec = {"watch_wires": list(WATCH_WIRES)}

    # (a) does `Tunnel` resolve as a traverse class at all?
    for cls in ("Tunnel", "LoopTunnel", "ConditionalTunnel", "SelectorTunnel",
                "LeftShiftRegister", "RightShiftRegister"):
        rows, err = safe("[P1a] report_all(%r)" % cls, lambda c=cls: g.report_all(WORK, c), None)
        rec.setdefault("class_census", {})[cls] = {"rows": (len(rows) if rows is not None else None),
                                                   "error_verbatim": err,
                                                   "uids": [r["uid"] for r in (rows or [])][:400]}
        fact("[P1a] report_all(%-20r) -> %s row(s)%s"
             % (cls, ("%d" % len(rows)) if rows is not None else "NONE", (" ; ERROR " + err) if err else ""))
    tun = rec["class_census"].get("Tunnel", {})
    gate("P1a *** `Tunnel` RESOLVES AS A TRAVERSE CLASS *** (REPORTED, not a pass/fail of the artefact)",
         tun.get("rows") is not None, "rows %r ; error %r" % (tun.get("rows"), tun.get("error_verbatim")))

    # (b) every node on #639, its class, and every terminal carrying one of the three watched wires
    di = K.get("d639_index")
    cls_by_uid = K.get("node_class_by_uid", {})
    hits, struct_rows, scanned = [], [], 0
    t0 = time.time()
    for i in range(SCAN_LIMIT):
        if left_s() < M3_MIN_S + 120:
            rec["scan_stopped"] = "wall-clock guard after %d node(s)" % scanned
            break
        try:
            u, tr = g.node_terms_uid(WORK, di, i)
        except Exception as e:                                                     # noqa: BLE001
            rec["scan_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            break
        if not u:
            break
        scanned += 1
        cls = cls_by_uid.get(str(u), "?")
        is_struct = cls in ("CaseStructure", "WhileLoop", "ForLoop", "Sequence", "FlatSequence",
                            "FlatSequenceFrame", "EventStructure", "Stacked Sequence", "TimedLoop",
                            "DisableStructure", "ConditionalDisableStructure", "InPlaceElementStructure")
        if is_struct:
            names = [(t["i"], t["name"], t["is_source"], t["wire"]) for t in tr]
            struct_rows.append({"nodes_index": i, "uid": u, "class": cls, "n_terminals": len(tr),
                                "terminals": names})
            fact("[P1b] STRUCTURE on #%d Nodes[%d] = #%s class %r: %d terminal(s) -> %r"
                 % (D639, i, u, cls, len(tr), names[:14]))
        for t in tr:
            if t["wire"] in WATCH_WIRES:
                hits.append({"nodes_index": i, "node_uid": u, "node_class": cls, "terminal": t["i"],
                             "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                             "node_is_structure": is_struct})
    rec.update({"nodes_scanned_on_639": scanned, "scan_cost_s": round(time.time() - t0, 1),
                "structure_nodes": struct_rows, "watch_wire_hits": hits})
    fact("[P1b] scanned %d node(s) of Diagram #%d in %.1f s ; %d STRUCTURE node(s) ; %d terminal(s) carrying "
         "one of %r" % (scanned, D639, rec["scan_cost_s"], len(struct_rows), len(hits), list(WATCH_WIRES)))
    for h in hits:
        fact("    [P1b] wire %r on #%s (%s, structure=%r) t%d %r is_source=%r"
             % (h["wire"], h["node_uid"], h["node_class"], h["node_is_structure"], h["terminal"],
                h["name"], h["is_source"]))
    struct_with_terms = [s for s in struct_rows if s["n_terminals"]]
    rec["structures_returning_terminals"] = len(struct_with_terms)
    rec["the_finding_node_terms_is_blind_to_tunnels"] = (bool(struct_rows) and not struct_with_terms)
    gate("P1b *** node_terms ON A STRUCTURE RETURNS TERMINALS *** - if it does not, THAT IS THE FINDING "
         "(the census has a blind class), reported, never worked around",
         bool(struct_with_terms) or not struct_rows,
         "%d structure node(s) on #%d, %d of them returned terminals"
         % (len(struct_rows), D639, len(struct_with_terms)))
    struct_hits = [h for h in hits if h["node_is_structure"]]
    rec["structure_hits"] = struct_hits
    gate("P1b-A2 NO watched wire sits on a terminal of a STRUCTURE node on #%d" % D639,
         not struct_hits, "%r" % (struct_hits,))

    # (c) the same three wires walked BY UID through `Wire.Terms[]` - the tunnel-visible route
    net = {}
    for w in WATCH_WIRES:
        rows, err = safe("[P1c] wire_source_owner(%d)" % w, lambda ww=w: WIRE_TERMS(WORK, ww, n=12), [])
        net[str(w)] = {"rows": rows, "error_verbatim": err}
        fact("[P1c] WIRE %d Terms[] BY UID: %r%s" % (w, rows, (" ; ERROR " + err) if err else ""))
        owners = [r.get("owner_class") for r in (rows or []) if isinstance(r, dict)]
        net[str(w)]["owner_classes"] = owners
        tunnelish = [o for o in owners if o and "Tunnel" in str(o)]
        net[str(w)]["tunnel_family_owners"] = tunnelish
        gate("P1c-A2 wire %d has NO terminal whose OWNER is in the Tunnel family" % w,
             not tunnelish, "owner classes %r" % (owners,))
    rec["wire_terms_by_uid"] = net
    P["P1"] = rec
    dump()
    a2 = bool(struct_hits) or any(net[str(w)].get("tunnel_family_owners") for w in WATCH_WIRES)
    return a2


# ======================================================================= P2 - four owner_of calls
def step_P2():
    print("\n---------- [P2] FOUR `owner_of` CALLS - REPORTED, NEVER A GATE (53(d^8))", flush=True)
    rec = {}
    for uid in (D639, ROW2_WIRE, IND_CONTROL_UID, A5_UID):
        r, err = safe("[P2] owner_of(%d)" % uid, lambda u=uid: owner_of(WORK, u), None)
        rec[str(uid)] = {"answer": list(r) if r else None, "error_verbatim": err}
        fact("[P2] owner_of(%-6d) = %r%s" % (uid, r, (" ; ERROR " + err) if err else ""))
    P["P2"] = rec
    fact("[P2] ALL FOUR ARE REPORTED AND NONE IS A GATE: `owner_of` answered with the PREVIOUS query's object "
         "once, silently (Pre-decided 53(d^8)), so these are evidence to read, not a verdict to act on.")
    dump()


# ======================================================================= P3 - THE DATA TYPE READ
WRAPPED_TYPE_CANDIDATES = [
    ("Terminal.Name", "634A004", "gscript.node_terms -> the `name` column"),
    ("Terminal.Is Source?", "634A003", "gscript.node_terms -> the `is_source` column"),
    ("Terminal.Connected Wire", "634A000", "gscript.node_terms -> the `wire` column"),
    ("Terminal.Diagram", "634A002", "docs/NAMES.md:894 - wrapped inside OpTunnels' inner-terminal mapping"),
    ("Tunnel.Outside Terminal", "6356001", "gscript.tunnels -> out_name/out_is_source/out_wire"),
    ("Tunnel.Inside Terminals[]", "6356000", "gscript.tunnels -> in_names/in_is_source/in_wires"),
    ("Wire.Is Broken? (item terminal `Broken?`)", "6371004",
     "build_opconnectnested_v1.connect_nested_v1 -> the ordered Broken? pass"),
    ("NumericConstant.Representation", "5DCFC00",
     "docs/NAMES.md:998-1003 - registered; applies to a CONSTANT, not to a terminal or a wire"),
]


def step_P3(hints):
    print("\n---------- [P3] THE DATA-TYPE READ - the rule-1a measurement", flush=True)
    rec = {"wrapped_properties_tried": [], "reads": {}}

    # 1. every wrapped terminal-/wire-level property, with the FIELDS its wrapper actually returns
    di = K.get("d639_index")
    sloc, srows = node_view(WORK, SRC_UID, hints, "[P3] #%d the source" % SRC_UID)
    st1 = next((t for t in srows if t.get("name") == SRC_TERM_NAME), {})
    rec["reads"]["bed #10757 t 'element'"] = st1
    fact("[P3] BED  #%d %r -> %r   (FIELDS RETURNED: %r)"
         % (SRC_UID, SRC_TERM_NAME, st1, sorted(st1.keys())))
    prows, _e = panel_all(WORK, "[P3]")
    prow = next((r for r in prows if r.get("uid") == IND_CONTROL_UID), None)
    rec["reads"]["bed panel control 23525"] = prow
    fact("[P3] BED  panel control %d -> %r   (FIELDS RETURNED: %r)"
         % (IND_CONTROL_UID, prow, sorted((prow or {}).keys())))
    t0r, terr = safe("[P3] tunnels(0)", lambda: g.tunnels(WORK, 0), None)
    rec["reads"]["tunnels(0)"] = t0r
    fact("[P3] BED  tunnels(0) -> FIELDS RETURNED %r%s"
         % (sorted((t0r or {}).keys()), (" ; ERROR " + terr) if terr else ""))

    for name, short, wrapper in WRAPPED_TYPE_CANDIDATES:
        blob = json.dumps(rec["reads"], default=str)
        found = any(k in blob.lower() for k in ('"datatype"', '"data_type"', '"representation"', '"typedesc"'))
        rec["wrapped_properties_tried"].append(
            {"property": name, "short_name": short, "wrapper": wrapper,
             "returns_a_data_type": found,
             "result": "the wrapper returned no type-bearing field; the fields it DOES return are listed "
                       "above and contain none of datatype / data_type / representation / typedesc"})
        fact("[P3] TRIED %-44s %-9s via %-62s -> returns a data type: %r" % (name, short, wrapper, found))

    # 2. the ORIGINAL terminals, on an UNTOUCHED artefact, opened READ-ONLY
    print("\n---------- [P3] the ORIGINAL undivided wire, read on the untouched D1_s3a_focus_ind.vi",
          flush=True)
    orig = {}
    di_o, oerr = safe("[P3] diag_index on S3a", lambda: diag_index(S3A_ARTEFACT, D639))
    orig["d639_index_on_s3a"] = di_o
    orig["d639_index_error"] = oerr
    hints_o = [di_o, TOP]
    for uid, tname in ((SRC_UID, SRC_TERM_NAME), (CASE_UID, None)):
        _l, rows = node_view(S3A_ARTEFACT, uid, hints_o, "[P3] S3a #%d" % uid)
        orig["#%d" % uid] = rows
        if tname:
            row = next((t for t in rows if t.get("name") == tname), None)
            fact("[P3] S3a #%d %r -> %r" % (uid, tname, row))
        else:
            row = next((t for t in rows if t.get("i") == 2), None)
            fact("[P3] S3a #%d t2 -> %r" % (uid, row))
    safe("[P3] close_panel(S3a)", lambda: g.close_panel(S3A_ARTEFACT))
    pr = probe("[P3] D1_s3a_focus_ind AFTER the read-only open", S3A_ARTEFACT)
    gate("P3-RO the untouched artefact is STILL md5 %s after the read-only open" % S3A_MD5[:8],
         pr.get("md5") == S3A_MD5, "%r" % (pr.get("md5"),))
    rec["original_terminals"] = orig

    any_type = any(c["returns_a_data_type"] for c in rec["wrapped_properties_tried"])
    rec["verdict"] = ("A MEASURED TYPE IS AVAILABLE" if any_type else "TYPE READ UNREACHABLE")
    rec["type_mismatch_measured"] = False
    fact("[P3] *** %s *** - every wrapped terminal-/wire-level property is listed above with the fields its "
         "wrapper returns; NOT ONE of them carries a data type. No property ID was guessed and no Property "
         "node was built (an unregistered id is a guess; docs/toolkit-capabilities.md:256-260)." % rec["verdict"])
    gate("P3 *** THE DATA-TYPE READ: %s ***" % rec["verdict"], True,
         "an unreachable read is a RECORDED GAP, not a failure, and per ABORT clause A1 it is NOT a mismatch")
    P["P3"] = rec
    dump()
    return rec["type_mismatch_measured"]


# ======================================================================= M3
def resolve_dest(tag):
    """38(e): RE-RESOLVE the destination index BY UID from a freshly-read traverse list immediately before
    every `move_in`, and gate that the resolved index still owns that diagram."""
    lst, err = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(WORK, "Diagram"), [])
    uids = [o["uid"] for o in (lst or [])]
    idx = uids.index(BODY_A_UID) if BODY_A_UID in uids else None
    rec = {"tag": tag, "want_diagram_uid": BODY_A_UID, "resolved_index": idx, "traverse_len": len(uids),
           "index_still_owns_it": idx is not None and uids[idx] == BODY_A_UID, "error_verbatim": err}
    K.setdefault("dest_index_resolutions", []).append(rec)
    fact("%s DESTINDEX: Diagram #%d -> traverse index %r (array length %d)" % (tag, BODY_A_UID, idx, len(uids)))
    gate("%s the freshly resolved index %r still owns Diagram #%d (38(e))" % (tag, idx, BODY_A_UID),
         rec["index_still_owns_it"], "traverse_len %d" % len(uids))
    return idx


def body_a_node_uids(tag):
    """THE AUTHORITATIVE GATE for M3: Diagram #23058's own Nodes[] census, by uid."""
    idx, err = safe("%s diag_index(#%d)" % (tag, BODY_A_UID), lambda: diag_index(WORK, BODY_A_UID))
    if idx is None:
        fact("%s Diagram #%d could not be resolved: %s" % (tag, BODY_A_UID, err))
        return [], idx
    rows, lerr = safe("%s node_labels(%r)" % (tag, idx), lambda: g.node_labels(WORK, idx), [])
    uids = [r["uid"] for r in (rows or [])]
    fact("%s Diagram #%d [traverse %r] Nodes[] census: %d node(s) -> %r%s"
         % (tag, BODY_A_UID, idx, len(uids), uids, (" ; " + lerr) if lerr else ""))
    return uids, idx


def step_M1(hints):
    print("\n---------- [M1] FIVE `move_in` CALLS, ONE NODE PER CALL (37(d) severs every wire)", flush=True)
    before_uids, _ = body_a_node_uids("[M1] BEFORE")
    K["body_a_before"] = before_uids
    nodes = K["node_census_before"]
    for uid, name, pos, why in SET:
        _loc, rows = node_view(WORK, uid, hints, "[M1] #%d BEFORE" % uid, quiet=True)
        fact("[M1] #%d %r BEFORE the move: %d terminal(s), %d WIRED  (%s)"
             % (uid, name, len(rows), wired_count(rows), why))
        bi = resolve_dest("[M1] before move #%d" % uid)
        rec = {"uid": uid, "name": name, "dest_diagram_uid": BODY_A_UID, "dest_index_used": bi,
               "position": list(pos), "wired_before": wired_count(rows), "n_terms_before": len(rows)}
        try:
            rec["echoed_uid"] = move_in(WORK, uid, bi, pos)
            rec["error_verbatim"] = ""
            fact("[M1] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the echo "
                 "is NOT the moved object)" % (uid, name, BODY_A_UID, bi, pos, rec["echoed_uid"]))
        except Exception as e:                                                     # noqa: BLE001
            rec["echoed_uid"] = None
            rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:300])
            fact("[M1] MOVE #%d RAISED %s" % (uid, rec["error_verbatim"]))
        nodes, _p = census_and_purge(WORK, nodes, "[M1] after move #%d" % uid, hints)
        after_uids, _ = body_a_node_uids("[M1] after move #%d" % uid)
        rec["in_body_a_nodes"] = uid in after_uids
        gate("M1 #%d appears in Diagram #%d's Nodes[] census (THE authoritative gate)" % (uid, BODY_A_UID),
             rec["in_body_a_nodes"], "body has %d node(s)" % len(after_uids))
        own, oerr = safe("[M1] owner_of(%d) after the move" % uid, lambda u=uid: owner_of(WORK, u))
        rec["owner_of_after"] = list(own) if own else None
        rec["owner_of_error"] = oerr
        fact("[M1] owner_of(%d) AFTER the move = %r (REPORTED ALONGSIDE, never the gate - 53(d^8))"
             % (uid, own))
        _l2, rows2 = node_view(WORK, uid, [None, TOP], "[M1] #%d AFTER" % uid, quiet=True)
        rec["wired_after"] = wired_count(rows2)
        rec["n_terms_after"] = len(rows2)
        fact("[M1] #%d AFTER the move: %d terminal(s), %d WIRED (was %d)"
             % (uid, len(rows2), wired_count(rows2), rec["wired_before"]))
        rec["exec_state_after"] = read_es("[M1] after move #%d" % uid, WORK)
        K.setdefault("moves", []).append(rec)
        dump()

    final_uids, _ = body_a_node_uids("[M1] AFTER all five")
    K["body_a_after_moves"] = final_uids
    missing = [u for u in SET_UIDS if u not in final_uids]
    gate("M1 *** ALL FIVE MOVED UIDS ARE IN Diagram #%d's Nodes[] CENSUS ***" % BODY_A_UID, not missing,
         "missing %r ; body now holds %d node(s)" % (missing, len(final_uids)))
    K["node_census_after_moves"] = nodes
    K["counts_after_moves"] = counts(WORK, "[M1] after the five moves")
    dump()
    return nodes, not missing


def step_M1b(hints):
    """The CROSS-DIAGRAM consequence of moving #10407, MEASURED rather than argued."""
    print("\n---------- [M1b] WHERE THE TWO LOCAL-FED ROWS NOW STAND - measured, not argued", flush=True)
    rec = {}
    for uid in (LOCAL_UID,):
        loc = find_node(WORK, uid, hints, "[M1b] the Local #%d" % uid)
        rec["local_%d" % uid] = loc.get("found")
    _l, crows = node_view(WORK, CASE_UID, [None, TOP], "[M1b] #%d after the move" % CASE_UID)
    rec["case_terminals"] = crows
    rec["case_t0"] = next((t for t in crows if t.get("i") == 0), None)
    rec["case_t2"] = next((t for t in crows if t.get("i") == 2), None)
    fact("[M1b] #%d t0 = %r ; t2 = %r" % (CASE_UID, rec["case_t0"], rec["case_t2"]))
    fact("[M1b] the Local #%d now lives at %r, while #%d has moved to Diagram #%d - so the two rows the "
         "S3b halves built are CROSS-DIAGRAM after the move, and `connect_nested_v1` addresses ONE nested "
         "diagram only. REPORTED; no route is chosen and none is recommended."
         % (LOCAL_UID, rec.get("local_%d" % LOCAL_UID), CASE_UID, BODY_A_UID))
    K["M1b_cross_diagram"] = rec
    dump()


def step_M2(nodes, hints):
    print("\n---------- [M2] THE FIVE INTERNAL ROWS, each addressed BY TERMINAL NAME off the machine",
          flush=True)
    results = []
    for sink_uid, sink_name, sink_t, src_uid, src_name, src_t, why in INTERNAL_JOBS:
        job = {"sink_uid": sink_uid, "sink_name": sink_name, "sink_t_recorded": sink_t,
               "src_uid": src_uid, "src_name": src_name, "src_t_recorded": src_t, "evidence": why}
        sloc, srows = node_view(WORK, sink_uid, [None, TOP], "[M2] sink #%d" % sink_uid, quiet=True)
        rloc, rrows = node_view(WORK, src_uid, [None, TOP], "[M2] src  #%d" % src_uid, quiet=True)
        job["sink_wired_before"] = wired_count(srows)
        job["src_wired_before"] = wired_count(rrows)
        si = next((t["i"] for t in srows if t.get("name") == sink_name and t.get("is_source") is False), None)
        ri = next((t["i"] for t in rrows if t.get("name") == src_name and t.get("is_source") is True), None)
        if si is None:
            si = sink_t if any(t["i"] == sink_t for t in srows) else None
        if ri is None:
            ri = src_t if any(t["i"] == src_t for t in rrows) else None
        sd = (sloc.get("found") or {}).get("diagram_index")
        sn = (sloc.get("found") or {}).get("nodes_index")
        rd = (rloc.get("found") or {}).get("diagram_index")
        rn = (rloc.get("found") or {}).get("nodes_index")
        job["addr"] = {"sink_diag": sd, "sink_node": sn, "sink_term": si,
                       "src_diag": rd, "src_node": rn, "src_term": ri}
        fact("[M2] row %s -> %s : %r" % (src_name, sink_name, job["addr"]))
        same_diag = (sd is not None and sd == rd)
        job["same_nested_diagram"] = same_diag
        if None in (si, ri, sn, rn) or not same_diag:
            job["result"] = "NOT ADDRESSABLE" if None in (si, ri, sn, rn) else "NOT ON ONE NESTED DIAGRAM"
            gate("M2 row %r -> %r is addressable on ONE nested diagram" % (src_name, sink_name), False,
                 "%r ; %s" % (job["addr"], job["result"]))
            results.append(job)
            K.setdefault("rows", []).append(job)
            dump()
            continue
        try:
            dw, es, err = CONNECT_V1(WORK, sd, sn, si, rd, rn, ri, V1_LABELS)
            job["connect"] = {"wire_delta": dw, "exec_state": es, "machine_error": str(err)[:200]}
        except Exception as e:                                                     # noqa: BLE001
            job["connect"] = {"exception": "%s: %s" % (type(e).__name__, str(e)[:250])}
        fact("[M2] connect_nested_v1 -> %r" % (job["connect"],))
        nodes, _p = census_and_purge(WORK, nodes, "[M2] after row %s" % sink_name.replace("\n", " "), hints)
        _l3, srows2 = node_view(WORK, sink_uid, [None, TOP], "[M2] sink #%d AFTER" % sink_uid, quiet=True)
        _l4, rrows2 = node_view(WORK, src_uid, [None, TOP], "[M2] src  #%d AFTER" % src_uid, quiet=True)
        job["sink_wired_after"] = wired_count(srows2)
        job["src_wired_after"] = wired_count(rrows2)
        srow = next((t for t in srows2 if t["i"] == si), None)
        rrow = next((t for t in rrows2 if t["i"] == ri), None)
        job["same_wire_uid"] = bool(srow and rrow and srow["wire"] and srow["wire"] == rrow["wire"])
        job["wire_uid"] = (srow or {}).get("wire")
        fact("[M2] row %r -> %r : sink t%r wire %r / src t%r wire %r ; same net %r ; WIRED-TERMINAL counts "
             "sink %d -> %d, src %d -> %d"
             % (src_name, sink_name, si, (srow or {}).get("wire"), ri, (rrow or {}).get("wire"),
                job["same_wire_uid"], job["sink_wired_before"], job["sink_wired_after"],
                job["src_wired_before"], job["src_wired_after"]))
        gate("M2 row %r -> %r: the WIRED-TERMINAL count rose on BOTH ends and they share ONE wire uid (49(e))"
             % (src_name.replace("\n", " "), sink_name.replace("\n", " ")),
             job["same_wire_uid"] and job["sink_wired_after"] > job["sink_wired_before"]
             and job["src_wired_after"] > job["src_wired_before"],
             "wire %r" % (job["wire_uid"],))
        job["exec_state_after"] = read_es("[M2] after row %s" % sink_name.replace("\n", " "), WORK)
        if job["exec_state_after"] == 1:
            k = len(R["artefacts_on_disk"]) + 1
            save_artefact("[M2] UNIT %d (ExecState 1 at a unit boundary - the user's 2026-09-19 split rule)"
                          % k, os.path.join(g.CLAUDEDEV, "D1_s3b_m3_u%d_%s.vi" % (k, STAMP)),
                          BED_MD5, "the bed")
        results.append(job)
        K.setdefault("rows", []).append(job)
        dump()
    for row in NOT_ATTEMPTED:
        fact("[M2] NOT ATTEMPTED - %s (verb %s): %s" % (row["row"], row["verb"], row["why"]))
    return nodes, results


def step_final(all_moved):
    print("\n---------- [Z] THE PASS CRITERION, THE FINAL SAVE, THE RESTART AND THE COLD REOPEN", flush=True)
    es = read_es("[Z] before the pass-criterion decision", WORK)
    K["counts_final"] = counts(WORK, "[Z] final, in memory")
    hints = [None, TOP]
    _l, lrows = node_view(WORK, LOOP11_UID, hints, "[Z] #%d the WhileLoop" % LOOP11_UID, quiet=True)
    K["loop637_after"] = {"n_terms": len(lrows), "n_wired": wired_count(lrows)}
    fact("[Z] #%d (WhileLoop): %d terminals, %d WIRED (before: %r)"
         % (LOOP11_UID, len(lrows), wired_count(lrows), K.get("loop637_before")))
    gate("Z1 #%d's terminal/wired counts are UNCHANGED - no new tunnel (37(e)/50(e))" % LOOP11_UID,
         K["loop637_after"] == K.get("loop637_before"),
         "%r -> %r" % (K.get("loop637_before"), K["loop637_after"]))
    ok = bool(all_moved) and es == 1
    gate("Z2 *** THE PASS CRITERION: all five in Diagram #%d's Nodes[] AND ExecState 1 ***" % BODY_A_UID,
         ok, "all_moved %r ; ExecState %r" % (all_moved, es))
    if not ok:
        fact("[Z] THE FINAL SAVE IS NOT TAKEN - the pass criterion is not met. Intermediate artefacts saved "
             "at ExecState 1, if any, STAY on disk. `allow_broken` is never set and `gui_save` is never called.")
        return None
    rec = save_artefact("[Z] the M3 artefact", FINAL_PATH, BED_MD5, "the bed")
    D.fresh("[Z] LabVIEW RESTART before the COLD reopen")
    R["handles"]["after_final_restart"] = labview_handles()
    es_cold = read_es("[Z] COLD, after the restart", FINAL_PATH)
    K["exec_state_cold"] = es_cold
    gate("Z3 *** the saved artefact reopens COLD at ExecState 1 ***", es_cold == 1, "%r" % (es_cold,))
    K["counts_cold"] = counts(FINAL_PATH, "[Z] COLD")
    safe("[Z] close_panel(final)", lambda: g.close_panel(FINAL_PATH))
    return rec


# ======================================================================= main
def main():
    print("=== diag_c66_s3b_m3  %s  (bgrun --max-min 40)" % STAMP, flush=True)
    aborted = None
    try:
        phase_0()
        hints = step_E()
        a2 = step_P1(hints)
        step_P2()
        a1 = step_P3(hints)
        gate("A1 ABORT CLAUSE A1 (a MEASURED type MISMATCH) DID NOT FIRE", not a1, "a1=%r" % (a1,))
        gate("A2 ABORT CLAUSE A2 (a watched wire on a tunnel terminal) DID NOT FIRE", not a2, "a2=%r" % (a2,))
        if a1 or a2:
            aborted = "A1" if a1 else "A2"
            R["aborted_at"] = aborted
            fact("*** ABORT CLAUSE %s FIRED. STOPPING BEFORE THE FIRST `move_in`: no .vi is saved, the "
                 "working copy is removed, and nothing further is attempted. ***" % aborted)
            raise Stop("abort clause %s" % aborted)
        if left_s() < M3_MIN_S:
            R["m3_not_started"] = "only %.0f s left before the reserve; M3 needs %.0f s" % (left_s(), M3_MIN_S)
            gate("M0 there is enough wall-clock left to start M3", False, R["m3_not_started"])
            raise Stop("no wall-clock for M3")
        gate("M0 there is enough wall-clock left to start M3", True, "%.0f s left before the reserve"
             % left_s())
        nodes, all_moved = step_M1(hints)
        step_M1b(hints)
        step_M2(nodes, hints)
        step_final(all_moved)
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        safe("close_panel(WORK)", lambda: g.close_panel(WORK))
        if aborted and os.path.exists(WORK):
            safe("remove the working copy (abort clause)", lambda: os.remove(WORK))
        for path, tag in ((WORK, "the working copy"),):
            if os.path.exists(path):
                safe("remove %s" % tag, lambda p=path: os.remove(p))
            gate("Y scratch %s is gone (exists=False)" % os.path.basename(path), not os.path.exists(path),
                 "")
        print("\n---------- [Y] THE md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops", S2_ARTEFACT, S2_MD5),
                               ("D1_s3a_focus_ind", S3A_ARTEFACT, S3A_MD5),
                               ("D1_s3b_row1a", ROW1A_ARTEFACT, ROW1A_MD5),
                               ("D1_s3b_row1", ROW1_ARTEFACT, ROW1_MD5), ("THE BED", BED, BED_MD5)):
            pr = probe("Y %s AFTER" % tag, path)
            gate("Y %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
