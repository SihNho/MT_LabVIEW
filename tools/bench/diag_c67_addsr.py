"""diag_c67_addsr - cycle 67 material #2 PART B: THE READER. Five legs, five fresh scratches, nothing saved.

A DIAGNOSTIC under tools/bench/, never a recipe (48(n)). It MEASURES why `g.add_shift_reg` returned a uid
and error '' while creating nothing on While Loop #23032 (tools/bench/diag_c67_m3a.log:61,:72,:83-100,:105).
NOTHING IS BUILT. NO DELIVERABLE `.vi` IS EDITED OR SAVED. NO ROUTE IS CHOSEN OR RECOMMENDED. Nothing found
here is repaired.

WHAT ALREADY EXISTED AND IS REUSED, NOT REBUILT (checked before a line was written:
`docs/toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`)
  - `tools/gscript.py:673` `add_shift_reg` (OpAddShiftReg_v0, INDEX row 37) - the creator under test.
  - `tools/gscript.py:753` `shift_reg` / `:786` `shift_reg_left` (OpShiftRegs_v0/v1) - the register READERS
    the brief's SR CENSUS is defined in terms of.
  - `tools/gscript.py:626` `loop_cast` (OpLoopCast_v1 / OpWhileCast_v0) - returns `Loop.Shift Registers[]`
    element UIDs for ONE loop in ONE op run. Used as the CHEAP arm of the census so that every WhileLoop AND
    every ForLoop can be covered inside the deadline (17 For loops + 6 While loops were measured in this VI:
    `docs/toolkit-capabilities.md:27`, `tools/bench/diag_c67_m3a.log:59`). It is a SUPERSET of what the
    0..7 probe reports for a loop, not a substitute for it: the 0..7 `shift_reg`/`shift_reg_left` probe the
    brief specifies is run in full on EVERY WhileLoop, which is where #23032 and the control #637 both live.
  - `tools/gscript.py:941` `tunnels` (OpTunnels_v0) - the only wrapped reader of a LoopTunnel's OUTSIDE
    terminal and its wire. Used for LEG 5 (ii).
  - `tools/recipes/build_opconnectfromwire_v0.py:423` `wire_source_owner` - OpWireSource_v5, the ONLY BY-UID
    walk of a WIRE's own Terms[], giving each terminal's OWNER class and uid. Used for LEG 5 (i) and (iii).
  - `tools/recipes/build_d1_v0.py:357` `diag_index` - uid -> Diagram traverse index.
  - `tools/bench/diag_s2_scaffold.py` - `fresh()` (the pre-batch restart), `file_facts`, the md5 pins.
  - `tools/bench/diag_c67_m3a.py` - every helper below (gate/fact/probe/dump/safe/read_es/counts/
    node_census/terms_at/term_state/find_node/node_view/loop_index_of) is REUSED IN SHAPE from it.
  - `tools/bench/c60c_astcheck.py` - the static gate, run with `--route owner` on THIS file before launch
    (this file calls NO `move_in`, so `owner` is the correct route). NOT edited; CYCLE_GUARD_OFF never set.
  NO new op, NO new verb, NO edit to tools/gscript.py, NO edit to any *_astcheck.py, NO recipe.

THE BED  `claudeDev\\D1_s3b_row2_20260921_160311.vi`, md5 26c54ff784cb5cea21edbd214d2cc3a0, 476,759 B.
  READ-ONLY and md5-pinned BEFORE and AFTER. EACH LEG TAKES ITS OWN FRESH SCRATCH DUPLICATE (the cycle-64
  three-scratch pattern) so no leg can contaminate another. Every scratch is removed;
  `THE FILES THIS RUN LEFT ON DISK: [...]` is printed and is expected to be `[]`.

THE ONE REUSABLE HELPER - **SR CENSUS** (`sr_census`). For every uid in `report_all('WhileLoop')` and
  `report_all('ForLoop')`:
    - `loop_cast(...)` once  -> the loop's `Loop.Shift Registers[]` element UIDs (cheap, whole list);
    - for every WhileLoop, `shift_reg(reg_index)` and `shift_reg_left(reg_index)` for reg_index 0..7 ->
      the count of slots that answer WITHOUT error 1055, and each pair's (right uid, left uid).
  Reported as a TABLE KEYED BY LOOP UID, so "which loop grew" is answered by SUBTRACTION, never by
  inference. The same function, with the same arguments, runs in every leg.

PREDICTION CONTRACT (machine-checkable; a failed prediction is REPORTED, never explained away)
  P0  The bed reopens COLD at ExecState 1 with Node 632 / Wire 1907 / ControlTerminal 116 / Local 10 /
      LoopTunnel 135 / Tunnel 471, and `report_all('WhileLoop')` has 6 rows one of which is #23032.
  L1  ONE `add_shift_reg(target, <index whose uid echoes 23032>, class_name='WhileLoop')`. The returned uid,
      the error string, the SR CENSUS before and after, and the `report_all('GObject')` uid-SET diff
      (`minted []` / `vanished []`). PREDICTION AS WRITTEN IN `tools/gscript.py:683-687`: a register is
      created and `ExecState` goes to 0. MEASURED LAST RUN: neither happened. This leg decides whether the
      register went SOMEWHERE ELSE or NOWHERE AT ALL - if any loop's census grew, it went somewhere else.
  L2  GEOMETRY. #23032's and #637's bounds as far as this fleet can read them, plus the POSITIONS of the
      existing LeftShiftRegister / RightShiftRegister objects, which give the y offset convention by
      MEASUREMENT rather than by assumption. Then, on a FRESH scratch, `add_shift_reg` with a y taken from
      that measurement, and LEG 1's after-census again.
  L3  IDENTITY. #23032's class exactly as the machine reports it; its index in `report_all('WhileLoop')`;
      the uid AT that index; and whether uid 23561 exists as an object in this VI at all (the whole-VI
      `GObject` uid set), with its class and owner if it resolves.
  L4  CONTROL. `add_shift_reg` on #637 - a loop the reader demonstrably sees three pairs on - then the SR
      CENSUS and ExecState. Reports whether #637's pair count grew and whether ExecState went 1 -> 0.
  L5  READ-ONLY, on an unmodified scratch, NO EDIT AT ALL.
      (i)   every terminal on the net of wire 9113 (#10407 t6 'position [internal units]'), each with owner
            uid, owner class and terminal name;
      (ii)  #9641 (the LoopTunnel feeding #10407 t1 '# slices in stack'): its OUTER-side source on #686 -
            node uid, class, terminal index, terminal name, wire uid;
      (iii) the inner terminals of #4194 and #3974 (the two FlatSequenceInnerTunnels feeding #4344/#4274's
            outer-left today): whatever is addressable - uid, class, wire uid - and a PLAIN statement of
            what is NOT readable and why.
  Y   The bed's md5 and the five other pins hold BEFORE and AFTER. Every scratch `exists=False`.
      `THE FILES THIS RUN LEFT ON DISK: []`. Refs opened == closed, 0 live. Handles either side.

THE PART A REVIEW, AND WHAT OF IT IS IN THIS FILE (`archive/peer/2026-09-21-c67-addsr-noop.md`,
claude / hypothesis, opus / effort max, ANSWERED 532 s, $3.8464). IMPLEMENTED, mechanically, because each
is a READING and none changes a step:
  - its s1: `LeftShiftRegister` 16442 and `RightShiftRegister` 16399 BOTH DERIVE FROM `Tunnel`
    (`docs/NAMES.md:263-264`) and a Traverse includes subclasses, so the whole-VI `Tunnel` count is a
    CREATION DETECTOR - +2 per register. Gates `L1c2` / `L2c2` / `L4c2`, plus a direct uid-SET diff of
    both register classes (`sr_class_uids` / `sr_class_diff`) in legs 1, 2 and 4.
  - its s7 bullet 3: this run supplies the OUT-OF-RANGE CONTROL the last one lacked - the SR census probes
    reg_index 0..7 on EVERY WhileLoop, #637 included, so "what index-past-the-end looks like on a loop
    KNOWN to have registers" is measured rather than assumed.
  - its s2 rival #2: whether uid 23561 is stale or a REUSED freed uid is answered by LEG 3's whole-VI
    `GObject` uid-set membership test, which is already in the brief.
  - its s4: `''` from `_err` is NOT proof the Invoke ran (the UID property node's own error chain is
    unread, the op VI is non-reentrant, and `_err` returns None on a read exception). Recorded in the log
    beside every returned uid; reading that second error chain would need a NEW OP, which is forbidden.
CORRECTION TO THE REVIEW, off the brief it was given: its s7 opens "It never calls `add_shift_reg`, so it
cannot discriminate between any of the causes above." That is FALSE of this file - legs 1, 2 and 4 each
call `add_shift_reg`, and legs 2 and 4 are its own s6 steps (c) and (d). Its s6 step (b) and its s8 "one
write leg" both require `g.open_panel`, which this dispatch FORBIDS: quoted verbatim, NOT acted on.
NOT ACTED ON, quoted verbatim to the judgement session in the review's own `## What was done with it`:
every `open_panel` proposal (s2 rival #1, s6 step b, s8), its "retire or null-control the `NOT
byte-identical to the bed` gate" (s9.3), and its reading of `:54`'s empty TopLevelDiagram as a broken
instrument rather than a fact.

FORBIDDEN AND ABSENT: no `g.open_panel`; no `move_in`; no `connect_nested_v1`; no `wire_indicators`; no
`wire_sr`; no `allow_broken`; no `gui_save`; no `remove_bad_wires*`; no GUI action; no new op VI; no new
verb; `tools/gscript.py` NOT edited; no `*_astcheck.py` edited; no recipe; no VI run (34(f)); no motor /
ASI / camera (rig ASSEMBLED); no new process device. `retrospective.py` / `audit_cycle.py` /
`violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run (54(a)). `docs/cycle27-plan.md` and
STATUS's `## NEXT` are NOT touched. NOTHING FOUND HERE IS REPAIRED.
VERIFICATION IS STRUCTURAL, NEVER FUNCTIONAL (34(f)).
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
A1_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
A1_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
A3_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
A3_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("D1_s2_loops", S2_ARTEFACT, S2_MD5), ("A1 D1_s3a_focus_ind", A1_ARTEFACT, A1_MD5),
        ("A2 THE BED", BED, BED_MD5), ("A3 D1_s3b_row1", A3_ARTEFACT, A3_MD5))

TOP = 0
D639 = 639
D639_RECORDED = 46
D686 = 686                       # the diagram that OWNS #23032 (diag_c67_m3a.log:53-55, traverse index 19)
D686_RECORDED = 19
LOOP_A_UID = 23032               # the NEW While Loop the no-op was measured on
LOOP637_UID = 637                # the ORIGINAL While Loop the reader demonstrably sees three pairs on
RETURNED_UID = 23561             # what BOTH add_shift_reg calls returned last run (diag_c67_m3a.log:61,:72)
CASE_UID = 10407
WIRE_T6 = 9113                   # #10407 t6 'position [internal units]' (cycle-66 review)
TUNNEL_T1_UID = 9641             # the LoopTunnel feeding #10407 t1 '# slices in stack'
FS_INNER = (4194, 3974)          # the two FlatSequenceInnerTunnels feeding #4344 / #4274's outer-left
LEFT_SRS = (4344, 4274)

BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}
BASE_TUNNEL = 471
WHILELOOP_ROWS_RECORDED = 6

REG_PROBE_MAX = 8
RUN_DEADLINE_S = 35 * 60.0
RESERVE_S = 150.0
LEG_MIN_S = 120.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c67_addsr.json")

# FIVE fresh scratches, one per leg. Created and removed inside THIS run (rule: scratch per run).
SCRATCH = {n: os.path.join(g.CLAUDEDEV, "WORK_C67ADDSR_L%d_%s.vi" % (n, STAMP)) for n in (1, 2, 3, 4, 5)}

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 67 material #2 PART B: THE READER - five legs, five fresh scratches, nothing saved. "
             "Why did add_shift_reg return uid 23561 with error '' and create nothing on #23032?",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "bed": {"path": BED, "md5_pin": BED_MD5, "size_pin": BED_SIZE,
             "never_overwritten": "the bed is only ever READ; each leg works on its OWN fresh copy"},
     "nothing_is_built": True, "no_deliverable_vi_edited_or_saved": True,
     "chooses_no_route": True, "recommends_no_route": True, "repairs_nothing": True,
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_open_panel_call_in_this_file": True, "no_move_in": True, "no_connect_nested_v1": True,
     "no_wire_indicators": True, "no_wire_sr": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run, the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "legs": {}}
K = R["legs"]


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


def counts(path, tag, classes=("Node", "Wire", "ControlTerminal", "Local", "LoopTunnel", "Tunnel")):
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s counts: %r" % (tag, rec))
    return rec


def gobject_uids(path, tag):
    rows, err = safe("%s report_all('GObject')" % tag, lambda: g.report_all(path, "GObject"), [])
    by_uid = {r["uid"]: r for r in (rows or [])}
    fact("%s GObject census: %d row(s)%s" % (tag, len(by_uid), ("  [%s]" % err) if err else ""))
    return by_uid, err


def sr_class_uids(path, tag):
    """THE PEER'S STRONGEST MECHANICAL CORRECTION, implemented (archive/peer/2026-09-21-c67-addsr-noop.md
    s1): `LeftShiftRegister` 16442 and `RightShiftRegister` 16399 BOTH DERIVE FROM `Tunnel`
    (docs/NAMES.md:263-264), and a Traverse includes subclasses - proved in our own log, where a `Diagram`
    traverse returned a `TopLevelDiagram` row. So the whole-VI `Tunnel` count IS a creation detector for a
    shift register, and the two register classes can be uid-SET diffed directly. This is a READING, not a
    route change: it adds a census, calls nothing new and alters no step."""
    out = {}
    for cls in ("RightShiftRegister", "LeftShiftRegister"):
        rows, err = safe("%s report_all(%r)" % (tag, cls), lambda c=cls: g.report_all(path, c), [])
        out[cls] = {r["uid"]: {"class": r["class"], "pos": list(r["pos"]), "owner": r["owner"]}
                    for r in (rows or [])}
        out[cls + "_error"] = err
        fact("%s report_all(%r): %d row(s) uids %r%s"
             % (tag, cls, len(out[cls]), sorted(out[cls]), ("  [%s]" % err) if err else ""))
    return out


def sr_class_diff(tag, before, after):
    rec = {}
    for cls in ("RightShiftRegister", "LeftShiftRegister"):
        b, a = before.get(cls, {}), after.get(cls, {})
        rec[cls] = {"count_before": len(b), "count_after": len(a),
                    "minted": sorted(set(a) - set(b)), "vanished": sorted(set(b) - set(a))}
        fact("%s %s: %d -> %d ; minted %r ; vanished %r"
             % (tag, cls, len(b), len(a), rec[cls]["minted"], rec[cls]["vanished"]))
    return rec


def uid_set_diff(tag, before, after):
    minted = sorted(set(after) - set(before))
    vanished = sorted(set(before) - set(after))
    rec = {"minted": minted, "vanished": vanished,
           "minted_rows": [after[u] for u in minted], "vanished_rows": [before[u] for u in vanished]}
    fact("%s GObject uid-SET diff: minted %r ; vanished %r" % (tag, minted, vanished))
    for u in minted:
        fact("%s     minted #%s class %r owner %r pos %r"
             % (tag, u, after[u]["class"], after[u]["owner"], after[u]["pos"]))
    return rec


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
    """WIRED / BARE / UNREAD for ONE terminal row (gscript.py:874 gives the one legitimate bare-terminal
    error pattern: wire 0 with conn_err/wire_err 1055 and name_err/src_err 0)."""
    ne, se, ce, we = [int(x or 0) for x in t.get("errs", [0, 0, 0, 0])]
    if t.get("wire"):
        return "UNREAD" if (ne or se or ce or we) else "WIRED"
    if ne or se:
        return "UNREAD"
    if (ce and ce != 1055) or (we and we != 1055):
        return "UNREAD"
    return "BARE"


def find_node(path, uid, hints, tag, budget_s=180.0, quiet=False):
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


def loop_index_of(path, uid, cls, tag, fatal=False):
    """Gate A7: resolve the loop's index in report_all(cls) FRESH, and ECHO that report_all(cls)[idx].uid ==
    uid, immediately before every call that takes a loop_index. An index is never carried across a call."""
    rows, err = safe("%s report_all(%r)" % (tag, cls), lambda: g.report_all(path, cls), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    rec = {"tag": tag, "class": cls, "want_uid": uid, "loop_index": idx, "echoed_uid": echo,
           "rows": len(rows or []), "error_verbatim": err}
    K.setdefault("loop_index_echoes", []).append(rec)
    fact("%s A7 ECHO: report_all(%r)[%r].uid == %r (want #%d; %d row(s))"
         % (tag, cls, idx, echo, uid, len(rows or [])))
    gate("A7 %s report_all(%r)[loop_index].uid == %d" % (tag, cls, uid), echo == uid,
         "loop_index %r echoed %r" % (idx, echo), fatal=fatal)
    return idx


# ============================================================ THE ONE REUSABLE HELPER: THE SR CENSUS
def sr_census(path, tag, probe_slots=True):
    """SR CENSUS, identical in every leg. For every WhileLoop and ForLoop uid in the VI:
         - `loop_cast` once -> the loop's `Loop.Shift Registers[]` element UIDs (the whole list, one run);
         - for every WhileLoop, `shift_reg(reg_index)` / `shift_reg_left(reg_index)` for reg_index 0..7 ->
           the count of slots that answer WITHOUT error 1055, plus each pair's (right uid, left uid).
       Returns {loop_uid: row}, so "which loop grew" is answered by SUBTRACTION, never by inference."""
    print("\n---------- %s SR CENSUS" % tag, flush=True)
    table = {}
    for cls in ("WhileLoop", "ForLoop"):
        rows, err = safe("%s report_all(%r)" % (tag, cls), lambda c=cls: g.report_all(path, c), [])
        fact("%s report_all(%r): %d row(s)%s" % (tag, cls, len(rows or []), ("  [%s]" % err) if err else ""))
        for r in (rows or []):
            uid, idx = r["uid"], r["i"]
            row = {"loop_uid": uid, "class": cls, "loop_index": idx, "pos": r["pos"],
                   "owner_class": r["owner"], "cast_shift_reg_uids": None, "cast_error": "",
                   "slots_without_1055": None, "pairs": [], "slot_probes": []}
            lc, cerr = safe("%s loop_cast(%r, index=%d)" % (tag, cls, idx),
                            lambda i=idx, c=cls: g.loop_cast(path, i, class_name=c))
            if lc:
                row["cast_shift_reg_uids"] = sorted(int(u) for u in lc.get("shift_reg_uids") or [])
                row["cast_errors"] = lc.get("errors")
                row["cast_loop_uid_echo"] = lc.get("loop_uid")
            row["cast_error"] = cerr
            if probe_slots and cls == "WhileLoop":
                ok_slots = 0
                for k in range(REG_PROBE_MAX):
                    sr, serr = safe("%s shift_reg(#%d, reg_index=%d)" % (tag, uid, k),
                                    lambda i=idx, kk=k: g.shift_reg(path, i, kk))
                    srl, lerr = safe("%s shift_reg_left(#%d, reg_index=%d)" % (tag, uid, k),
                                     lambda i=idx, kk=k: g.shift_reg_left(path, i, kk))
                    errs = dict((sr or {}).get("errors") or {})
                    has1055 = any("1055" in str(v) for v in errs.values()) or bool(serr)
                    p = {"reg_index": k, "right_uid": (sr or {}).get("uid"),
                         "left_uids": (srl or {}).get("left_uids"),
                         "left_uid": ((srl or {}).get("left") or {}).get("uid"),
                         "left_out": ((srl or {}).get("left") or {}).get("out"),
                         "right_out": (sr or {}).get("out"), "inside": (sr or {}).get("inside"),
                         "op_errors": errs, "left_op_errors": (srl or {}).get("errors"),
                         "call_error_verbatim": serr, "left_call_error_verbatim": lerr,
                         "answered_without_1055": not has1055}
                    row["slot_probes"].append(p)
                    if p["answered_without_1055"]:
                        ok_slots += 1
                        row["pairs"].append({"reg_index": k, "right_uid": p["right_uid"],
                                             "left_uid": p["left_uid"],
                                             "left_out_name": (p["left_out"] or {}).get("name"),
                                             "left_out_wire": (p["left_out"] or {}).get("wire")})
                row["slots_without_1055"] = ok_slots
            table[uid] = row
            fact("%s  loop #%-6d %-9s idx %-3d cast_srs %r ; slots_without_1055 %r ; pairs %r"
                 % (tag, uid, cls, idx, row["cast_shift_reg_uids"], row["slots_without_1055"],
                    [(p["reg_index"], p["right_uid"], p["left_uid"]) for p in row["pairs"]]))
    fact("%s SR CENSUS: %d loop(s) tabled" % (tag, len(table)))
    dump()
    return table


def census_diff(tag, before, after):
    """Which loop GREW - by subtraction over the SR CENSUS, never by inference."""
    grew, shrank, same = [], [], []
    for uid in sorted(set(before) | set(after)):
        b, a = before.get(uid), after.get(uid)
        nb = len((b or {}).get("cast_shift_reg_uids") or []) if b else None
        na = len((a or {}).get("cast_shift_reg_uids") or []) if a else None
        sb = (b or {}).get("slots_without_1055") if b else None
        sa = (a or {}).get("slots_without_1055") if a else None
        row = {"loop_uid": uid, "cast_srs_before": nb, "cast_srs_after": na,
               "slots_before": sb, "slots_after": sa,
               "cast_uids_before": (b or {}).get("cast_shift_reg_uids"),
               "cast_uids_after": (a or {}).get("cast_shift_reg_uids")}
        if (na or 0) > (nb or 0) or (sa or 0) > (sb or 0):
            grew.append(row)
        elif (na or 0) < (nb or 0) or (sa or 0) < (sb or 0):
            shrank.append(row)
        else:
            same.append(uid)
    fact("%s CENSUS DIFF: GREW %r ; SHRANK %r ; unchanged %d loop(s)" % (tag, grew, shrank, len(same)))
    return {"grew": grew, "shrank": shrank, "unchanged": same}


def make_scratch(n, tag):
    dest = SCRATCH[n]
    shutil.copy2(BED, dest)
    pr = probe("%s the fresh scratch for LEG %d" % (tag, n), dest)
    gate("%s LEG %d's scratch is byte-identical to the bed" % (tag, n), pr.get("md5") == BED_MD5,
         "%r" % (pr.get("md5"),))
    return dest


# ======================================================================= PHASE 0 - files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the six md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
        pr = probe("Y %s BEFORE" % tag, path)
        gate("Y %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe("Y THE BED size", BED)
    gate("Y the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))
    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


# ====================================================================== LEG 1 - WHERE DID IT GO?
def leg_1():
    print("\n========== LEG 1 - WHERE DID IT GO? one add_shift_reg on #%d" % LOOP_A_UID, flush=True)
    rec = K.setdefault("leg1", {})
    path = make_scratch(1, "[L1]")
    es0 = read_es("[L1] the scratch, COLD", path)
    rec["exec_state_before"] = es0
    gate("L1a the scratch reopens COLD at ExecState 1", es0 == 1, "%r" % (es0,))
    c0 = counts(path, "[L1] BEFORE")
    rec["counts_before"] = c0
    for k, v in BASE.items():
        gate("L1b %s == %d (the recorded baseline)" % (k, v), c0.get(k) == v, "%r" % (c0.get(k),))
    gate("L1b Tunnel == %d" % BASE_TUNNEL, c0.get("Tunnel") == BASE_TUNNEL, "%r" % (c0.get("Tunnel"),))

    gob0, _ = gobject_uids(path, "[L1] BEFORE")
    rec["gobject_rows_before"] = len(gob0)
    src0 = sr_class_uids(path, "[L1] BEFORE")
    cen0 = sr_census(path, "[L1] BEFORE")
    rec["census_before"] = cen0

    idx = loop_index_of(path, LOOP_A_UID, "WhileLoop", "[L1] before add_shift_reg")
    rec["loop_index_used"] = idx
    uid, err = safe("[L1] add_shift_reg(index=%r)" % idx,
                    lambda: g.add_shift_reg(path, idx, class_name="WhileLoop"))
    rec["returned_uid"] = uid
    rec["error_string_verbatim"] = err
    fact("[L1] *** add_shift_reg(target, loop_index=%r, class_name='WhileLoop') -> uid %r ; error %r ***"
         % (idx, uid, err))
    es1 = read_es("[L1] immediately after add_shift_reg", path)
    rec["exec_state_after"] = es1

    c1 = counts(path, "[L1] AFTER")
    rec["counts_after"] = c1
    rec["counts_changed"] = {k: (c0.get(k), c1.get(k)) for k in c1 if c0.get(k) != c1.get(k)}
    gate("L1c at least ONE whole-VI class count changed after add_shift_reg",
         bool(rec["counts_changed"]), "changed %r (before %r / after %r)"
         % (rec["counts_changed"], c0, c1))
    # The peer's s1 correction: both register classes descend from `Tunnel`, so a created register MUST
    # take the whole-VI `Tunnel` count up by 2 (one Left + one Right). This is the sharpest single gate.
    gate("L1c2 Tunnel went %r -> %r, i.e. +2 (a created register is a Left AND a Right, both Tunnel "
         "subclasses)" % (c0.get("Tunnel"), c1.get("Tunnel")),
         (c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0) == 2,
         "delta %r" % ((c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0),))
    src1 = sr_class_uids(path, "[L1] AFTER")
    rec["sr_class_diff"] = sr_class_diff("[L1]", src0, src1)
    gate("L1c3 a RightShiftRegister uid was MINTED",
         bool(rec["sr_class_diff"]["RightShiftRegister"]["minted"]),
         "%r" % (rec["sr_class_diff"]["RightShiftRegister"],))

    gob1, _ = gobject_uids(path, "[L1] AFTER")
    rec["gobject_rows_after"] = len(gob1)
    rec["gobject_diff"] = uid_set_diff("[L1]", gob0, gob1)
    gate("L1d the GObject uid SET gained at least one uid (an object was really created)",
         bool(rec["gobject_diff"]["minted"]), "minted %r ; vanished %r"
         % (rec["gobject_diff"]["minted"], rec["gobject_diff"]["vanished"]))
    gate("L1e the uid add_shift_reg returned (%r) is among the minted uids" % (uid,),
         uid is not None and uid in set(rec["gobject_diff"]["minted"]),
         "returned %r ; minted %r" % (uid, rec["gobject_diff"]["minted"]))

    cen1 = sr_census(path, "[L1] AFTER")
    rec["census_after"] = cen1
    rec["census_diff"] = census_diff("[L1]", cen0, cen1)
    gate("L1f SOME loop's shift-register census GREW", bool(rec["census_diff"]["grew"]),
         "grew %r" % (rec["census_diff"]["grew"],))
    a_before = (cen0.get(LOOP_A_UID) or {}).get("cast_shift_reg_uids")
    a_after = (cen1.get(LOOP_A_UID) or {}).get("cast_shift_reg_uids")
    rec["target_loop_shift_regs"] = {"before": a_before, "after": a_after}
    gate("L1g #%d's OWN shift-register list grew" % LOOP_A_UID,
         len(a_after or []) > len(a_before or []), "before %r -> after %r" % (a_before, a_after))
    fact("[L1] THE ANSWER THIS LEG EXISTS FOR: the register went %s"
         % ("SOMEWHERE ELSE (a different loop's census grew)"
            if (rec["census_diff"]["grew"] and not (len(a_after or []) > len(a_before or [])))
            else ("ONTO #%d" % LOOP_A_UID if len(a_after or []) > len(a_before or [])
                  else "NOWHERE AT ALL - no loop's census grew and no GObject uid was minted"
                       if not rec["gobject_diff"]["minted"]
                       else "NOWHERE VISIBLE AS A SHIFT REGISTER, although %d GObject uid(s) were minted"
                            % len(rec["gobject_diff"]["minted"]))))
    dump()
    return rec


# ====================================================================== LEG 2 - GEOMETRY
def leg_2():
    print("\n========== LEG 2 - GEOMETRY: does the y argument decide it?", flush=True)
    rec = K.setdefault("leg2", {})
    path = make_scratch(2, "[L2]")

    # BOUNDS AS FAR AS THIS FLEET CAN READ THEM. `report_all` returns GObject.Position (the top-left); a
    # GObject's Bounds (Width/Height) has NO wrapped VALUE reader on this COM path - cycle 66 measured that
    # reading any property VALUE needs a property node wired inside a SAVED op VI (docs/NAMES.md, the
    # 2026-09-21 "VALUE READ NEEDS A NEW OP" paragraph), and no new op is built here. So the vertical span
    # is derived BY MEASUREMENT from the EXISTING registers' own positions relative to their loop.
    geo = {}
    for cls in ("WhileLoop", "RightShiftRegister", "LeftShiftRegister"):
        rows, err = safe("[L2] report_all(%r)" % cls, lambda c=cls: g.report_all(path, c), [])
        geo[cls] = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": list(r["pos"]),
                     "owner_class": r["owner"]} for r in (rows or [])]
        geo[cls + "_error"] = err
        fact("[L2] report_all(%r): %d row(s)%s" % (cls, len(geo[cls]), ("  [%s]" % err) if err else ""))
        for r in geo[cls]:
            fact("[L2]     #%-6d %-22s pos %r owner %r" % (r["uid"], r["class"], r["pos"], r["owner_class"]))
    rec["geometry"] = geo
    rec["bounds_readability"] = ("GObject.Position (top-left) IS readable via report_all; GObject.Bounds "
                                 "(Width/Height) has NO wrapped VALUE reader on this COM path and building "
                                 "one is a NEW OP, which this dispatch forbids. The y used below is "
                                 "therefore derived from MEASURED register positions, not from a bounds read.")
    fact("[L2] %s" % rec["bounds_readability"])

    def pos_of(cls, uid):
        return next((r["pos"] for r in geo.get(cls, []) if r["uid"] == uid), None)

    a_pos = pos_of("WhileLoop", LOOP_A_UID)
    c_pos = pos_of("WhileLoop", LOOP637_UID)
    rec["loop_positions"] = {str(LOOP_A_UID): a_pos, str(LOOP637_UID): c_pos}
    fact("[L2] #%d pos %r ; #%d pos %r" % (LOOP_A_UID, a_pos, LOOP637_UID, c_pos))

    # The measured convention: how far BELOW its loop's Position.top do #637's own registers sit?
    offsets = []
    for r in geo.get("RightShiftRegister", []) + geo.get("LeftShiftRegister", []):
        if c_pos and len(r["pos"]) >= 2 and len(c_pos) >= 2:
            offsets.append(r["pos"][1] - c_pos[1])
    rec["measured_y_offsets_from_637_top"] = sorted(offsets)
    fact("[L2] MEASURED y offsets of the existing shift registers from #%d's Position top (%r): %r"
         % (LOOP637_UID, (c_pos or [None, None])[1] if c_pos else None, sorted(offsets)))
    if offsets and a_pos and len(a_pos) >= 2:
        med = sorted(offsets)[len(offsets) // 2]
        y_use = int(a_pos[1] + med)
        why = ("a_pos.top %r + the MEDIAN measured offset %r of #%d's existing registers from its own "
               "Position top" % (a_pos[1], med, LOOP637_UID))
    else:
        y_use = 120
        why = ("FALLBACK: no register position was readable, so the previous run's y=120 is repeated and "
               "this leg becomes a REPLICATION of it rather than a geometry test")
    rec["y_passed"] = y_use
    rec["y_rationale"] = why
    fact("[L2] y_position passed to add_shift_reg = %r, because %s" % (y_use, why))

    c0 = counts(path, "[L2] BEFORE")
    rec["counts_before"] = c0
    cen0 = sr_census(path, "[L2] BEFORE")
    rec["census_before"] = cen0
    gob0, _ = gobject_uids(path, "[L2] BEFORE")
    src0 = sr_class_uids(path, "[L2] BEFORE")
    idx = loop_index_of(path, LOOP_A_UID, "WhileLoop", "[L2] before add_shift_reg")
    uid, err = safe("[L2] add_shift_reg(index=%r, y=%r)" % (idx, y_use),
                    lambda: g.add_shift_reg(path, idx, y_position=y_use, class_name="WhileLoop"))
    rec["returned_uid"] = uid
    rec["error_string_verbatim"] = err
    fact("[L2] *** add_shift_reg(loop_index=%r, y_position=%r) -> uid %r ; error %r ***"
         % (idx, y_use, uid, err))
    rec["exec_state_after"] = read_es("[L2] immediately after add_shift_reg", path)
    c1 = counts(path, "[L2] AFTER")
    rec["counts_after"] = c1
    gate("L2c2 Tunnel went %r -> %r, i.e. +2" % (c0.get("Tunnel"), c1.get("Tunnel")),
         (c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0) == 2,
         "delta %r" % ((c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0),))
    gob1, _ = gobject_uids(path, "[L2] AFTER")
    rec["gobject_diff"] = uid_set_diff("[L2]", gob0, gob1)
    src1 = sr_class_uids(path, "[L2] AFTER")
    rec["sr_class_diff"] = sr_class_diff("[L2]", src0, src1)
    cen1 = sr_census(path, "[L2] AFTER")
    rec["census_after"] = cen1
    rec["census_diff"] = census_diff("[L2]", cen0, cen1)
    a_before = (cen0.get(LOOP_A_UID) or {}).get("cast_shift_reg_uids")
    a_after = (cen1.get(LOOP_A_UID) or {}).get("cast_shift_reg_uids")
    gate("L2a with a MEASURED in-span y, #%d's shift-register list grows" % LOOP_A_UID,
         len(a_after or []) > len(a_before or []), "y %r ; before %r -> after %r" % (y_use, a_before, a_after))
    dump()
    return rec


# ====================================================================== LEG 3 - IDENTITY
def leg_3():
    print("\n========== LEG 3 - IDENTITY: what is #%d, and does #%d exist?" % (LOOP_A_UID, RETURNED_UID),
          flush=True)
    rec = K.setdefault("leg3", {})
    path = make_scratch(3, "[L3]")
    rows, err = safe("[L3] report_all('WhileLoop')", lambda: g.report_all(path, "WhileLoop"), [])
    rec["whileloop_rows"] = [{"i": r["i"], "uid": r["uid"], "class": r["class"], "pos": list(r["pos"]),
                              "owner_class": r["owner"]} for r in (rows or [])]
    rec["whileloop_error"] = err
    fact("[L3] report_all('WhileLoop'): %d row(s)" % len(rec["whileloop_rows"]))
    for r in rec["whileloop_rows"]:
        fact("[L3]     [%d] #%-6d class %r owner %r pos %r"
             % (r["i"], r["uid"], r["class"], r["owner_class"], r["pos"]))
    gate("L3a report_all('WhileLoop') still has %d rows" % WHILELOOP_ROWS_RECORDED,
         len(rec["whileloop_rows"]) == WHILELOOP_ROWS_RECORDED, "%d" % len(rec["whileloop_rows"]))
    hit = next((r for r in rec["whileloop_rows"] if r["uid"] == LOOP_A_UID), None)
    rec["target_row"] = hit
    rec["target_class_as_the_machine_reports_it"] = (hit or {}).get("class")
    rec["target_index"] = (hit or {}).get("i")
    rec["uid_at_that_index"] = next((r["uid"] for r in rec["whileloop_rows"]
                                     if r["i"] == (hit or {}).get("i")), None)
    fact("[L3] #%d: class %r (exactly as the machine reports it), index %r in report_all('WhileLoop'), "
         "uid at that index %r" % (LOOP_A_UID, rec["target_class_as_the_machine_reports_it"],
                                   rec["target_index"], rec["uid_at_that_index"]))
    gate("L3b #%d's index and the uid at that index agree" % LOOP_A_UID,
         rec["uid_at_that_index"] == LOOP_A_UID, "%r" % (rec["uid_at_that_index"],))

    gob, gerr = gobject_uids(path, "[L3] whole-VI")
    rec["gobject_rows"] = len(gob)
    rec["gobject_error"] = gerr
    row = gob.get(RETURNED_UID)
    rec["returned_uid_exists_in_this_vi"] = row is not None
    rec["returned_uid_row"] = row
    if row:
        fact("[L3] *** uid %d DOES resolve in this VI: class %r, owner %r, pos %r ***"
             % (RETURNED_UID, row["class"], row["owner"], row["pos"]))
    else:
        fact("[L3] *** uid %d DOES NOT EXIST as a GObject in this VI (%d GObject rows searched) ***"
             % (RETURNED_UID, len(gob)))
    gate("L3c uid %d resolves to an object in this VI" % RETURNED_UID, row is not None,
         "%r" % (row,))

    # Where #23032 lives, re-read on this leg's own scratch rather than carried from an earlier log.
    di686, e686 = safe("[L3] diag_index(#%d)" % D686, lambda: diag_index(path, D686))
    rec["d686_traverse_index"] = di686
    rec["d686_error"] = e686
    diags, _ = safe("[L3] report_all('Diagram')", lambda: g.report_all(path, "Diagram"), [])
    zero = next((d for d in (diags or []) if d["i"] == 0), None)
    rec["diagram_index_0"] = zero
    rec["diagram_rows"] = len(diags or [])
    zero_nodes, _ = safe("[L3] node_labels(0)", lambda: g.node_labels(path, 0), [])
    rec["diagram_index_0_nodes"] = len(zero_nodes or [])
    # Gate 8 of the static checker: never test the literal 'Diagram' without accepting 'TopLevelDiagram'.
    rec["index_0_is_the_top_level_diagram"] = bool(zero) and zero["class"] in ("TopLevelDiagram", "Diagram")
    fact("[L3] Diagram #%d traverse index %r ; traverse index 0 is %r with %d node(s)"
         % (D686, di686, zero, rec["diagram_index_0_nodes"]))
    dump()
    return rec


# ====================================================================== LEG 4 - CONTROL (#637)
def leg_4():
    print("\n========== LEG 4 - CONTROL: the same call on #%d" % LOOP637_UID, flush=True)
    rec = K.setdefault("leg4", {})
    path = make_scratch(4, "[L4]")
    rec["exec_state_before"] = read_es("[L4] the scratch, COLD", path)
    c0 = counts(path, "[L4] BEFORE")
    rec["counts_before"] = c0
    cen0 = sr_census(path, "[L4] BEFORE")
    rec["census_before"] = cen0
    gob0, _ = gobject_uids(path, "[L4] BEFORE")
    src0 = sr_class_uids(path, "[L4] BEFORE")
    idx = loop_index_of(path, LOOP637_UID, "WhileLoop", "[L4] before add_shift_reg")
    rec["loop_index_used"] = idx
    uid, err = safe("[L4] add_shift_reg(index=%r)" % idx,
                    lambda: g.add_shift_reg(path, idx, class_name="WhileLoop"))
    rec["returned_uid"] = uid
    rec["error_string_verbatim"] = err
    fact("[L4] *** add_shift_reg on #%d (loop_index=%r) -> uid %r ; error %r ***"
         % (LOOP637_UID, idx, uid, err))
    rec["exec_state_after"] = read_es("[L4] immediately after add_shift_reg", path)
    c1 = counts(path, "[L4] AFTER")
    rec["counts_after"] = c1
    gate("L4c2 Tunnel went %r -> %r, i.e. +2" % (c0.get("Tunnel"), c1.get("Tunnel")),
         (c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0) == 2,
         "delta %r" % ((c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0),))
    gob1, _ = gobject_uids(path, "[L4] AFTER")
    rec["gobject_diff"] = uid_set_diff("[L4]", gob0, gob1)
    src1 = sr_class_uids(path, "[L4] AFTER")
    rec["sr_class_diff"] = sr_class_diff("[L4]", src0, src1)
    cen1 = sr_census(path, "[L4] AFTER")
    rec["census_after"] = cen1
    rec["census_diff"] = census_diff("[L4]", cen0, cen1)
    b = (cen0.get(LOOP637_UID) or {}).get("cast_shift_reg_uids")
    a = (cen1.get(LOOP637_UID) or {}).get("cast_shift_reg_uids")
    sb = (cen0.get(LOOP637_UID) or {}).get("slots_without_1055")
    sa = (cen1.get(LOOP637_UID) or {}).get("slots_without_1055")
    rec["loop637_shift_regs"] = {"before": b, "after": a, "slots_before": sb, "slots_after": sa}
    fact("[L4] #%d pair count: cast list %r -> %r ; slots_without_1055 %r -> %r ; ExecState %r -> %r"
         % (LOOP637_UID, b, a, sb, sa, rec["exec_state_before"], rec["exec_state_after"]))
    gate("L4a #%d's shift-register list GREW" % LOOP637_UID, len(a or []) > len(b or []),
         "%r -> %r" % (b, a))
    gate("L4b ExecState went 1 -> 0 (tools/gscript.py:683-687's prediction)",
         rec["exec_state_before"] == 1 and rec["exec_state_after"] == 0,
         "%r -> %r" % (rec["exec_state_before"], rec["exec_state_after"]))
    dump()
    return rec


# ====================================================================== LEG 5 - READ-ONLY, NO EDIT
def leg_5():
    print("\n========== LEG 5 - READ-ONLY on an unmodified scratch. NO EDIT AT ALL.", flush=True)
    rec = K.setdefault("leg5", {})
    rec["no_edit_in_this_leg"] = True
    path = make_scratch(5, "[L5]")
    d639, _ = safe("[L5] diag_index(#%d)" % D639, lambda: diag_index(path, D639))
    d686, _ = safe("[L5] diag_index(#%d)" % D686, lambda: diag_index(path, D686))
    hints = [h for h in (d639, d686, TOP) if isinstance(h, int)]
    rec["diagram_hints"] = hints
    fact("[L5] Diagram #%d -> traverse index %r ; Diagram #%d -> traverse index %r" % (D639, d639, D686, d686))

    # ---- (i) EVERY terminal on the net of wire 9113 (#10407 t6 'position [internal units]')
    print("\n---------- [L5 i] THE NET OF WIRE %d (#%d t6)" % (WIRE_T6, CASE_UID), flush=True)
    walk, werr = safe("[L5 i] wire_source_owner(%d)" % WIRE_T6,
                      lambda: WIRE_TERMS(path, WIRE_T6, n=12), [])
    rec["wire_%d_walk" % WIRE_T6] = walk
    rec["wire_%d_walk_error" % WIRE_T6] = werr
    fact("[L5 i] wire %d Terms[] walk: %r" % (WIRE_T6, walk))
    named = []
    for t in (walk or []):
        owner_uid, owner_cls = t.get("owner_uid"), t.get("owner_class")
        entry = {"terms_index": t.get("i"), "is_source": t.get("is_source"), "owner_uid": owner_uid,
                 "owner_class": owner_cls, "recip_wire": t.get("recip"), "terminal_name": None,
                 "terminal_index": None, "name_route": None}
        if owner_uid:
            loc, rows = node_view(path, owner_uid, hints, "[L5 i] owner #%s" % owner_uid, quiet=True)
            match = [r for r in rows if r.get("wire") == WIRE_T6]
            entry["found_on"] = (loc.get("found") or {})
            if match:
                entry["terminal_name"] = match[0]["name"]
                entry["terminal_index"] = match[0]["i"]
                entry["name_route"] = "node_terms row whose WireUID == %d" % WIRE_T6
            else:
                entry["name_route"] = ("NOT READABLE: #%s is not a Nodes[] entry on any scanned diagram, or "
                                       "carries no terminal on this wire - a TUNNEL / shift register is not "
                                       "a Node, so node_terms cannot name its terminals" % owner_uid)
        named.append(entry)
        fact("[L5 i]   owner #%r %-26r is_source=%-5r terminal %r (index %r) ; recip wire %r ; %s"
             % (owner_uid, owner_cls, entry["is_source"], entry["terminal_name"],
                entry["terminal_index"], entry["recip_wire"], entry["name_route"]))
    rec["wire_%d_terminals_named" % WIRE_T6] = named
    sinks = [e for e in named if e["owner_uid"] and not e["is_source"]]
    rec["wire_%d_sink_count" % WIRE_T6] = len(sinks)
    fact("[L5 i] *** RULE-1a FACT, READ NOT QUOTED: wire %d carries %d SOURCE and %d SINK terminal(s): %r ***"
         % (WIRE_T6, sum(1 for e in named if e["owner_uid"] and e["is_source"]), len(sinks),
            [(e["owner_uid"], e["owner_class"], e["terminal_name"]) for e in sinks]))

    # ---- (ii) #9641, the LoopTunnel feeding #10407 t1 '# slices in stack' - its OUTER-side source
    print("\n---------- [L5 ii] #%d's OUTER-SIDE SOURCE" % TUNNEL_T1_UID, flush=True)
    lt, lterr = safe("[L5 ii] report_all('LoopTunnel')", lambda: g.report_all(path, "LoopTunnel"), [])
    ti = next((r["i"] for r in (lt or []) if r["uid"] == TUNNEL_T1_UID), None)
    rec["tunnel_index"] = ti
    rec["looptunnel_rows"] = len(lt or [])
    rec["looptunnel_error"] = lterr
    fact("[L5 ii] report_all('LoopTunnel'): %d row(s) ; #%d is at index %r"
         % (len(lt or []), TUNNEL_T1_UID, ti))
    tun, terr = safe("[L5 ii] tunnels(index=%r)" % ti, lambda: g.tunnels(path, ti) if ti is not None else None)
    rec["tunnel_read"] = tun
    rec["tunnel_read_error"] = terr
    if tun:
        fact("[L5 ii] tunnels(%r) -> uid %r (echo of #%d: %r) ; OUTSIDE terminal name %r is_source %r "
             "wire %r (conn_err %r wire_err %r) ; INSIDE names %r wires %r"
             % (ti, tun.get("uid"), TUNNEL_T1_UID, tun.get("uid") == TUNNEL_T1_UID, tun.get("out_name"),
                tun.get("out_is_source"), tun.get("out_wire"), tun.get("out_conn_err"),
                tun.get("out_wire_err"), tun.get("in_names"), tun.get("in_wires")))
        gate("L5a tunnels() echoes uid %d at index %r" % (TUNNEL_T1_UID, ti),
             tun.get("uid") == TUNNEL_T1_UID, "%r" % (tun.get("uid"),))
        ow = tun.get("out_wire") or 0
        rec["outer_wire"] = ow
        if ow:
            w2, w2err = safe("[L5 ii] wire_source_owner(%d)" % ow,
                             lambda: WIRE_TERMS(path, ow, n=12), [])
            rec["outer_wire_walk"] = w2
            rec["outer_wire_walk_error"] = w2err
            src = next((t for t in (w2 or []) if t.get("is_source") and t.get("owner_uid")), None)
            rec["outer_source"] = src
            fact("[L5 ii] OUTER wire %d walk: %r ; SOURCE owner %r" % (ow, w2, src))
            if src and src.get("owner_uid"):
                loc, rows = node_view(path, src["owner_uid"], hints,
                                      "[L5 ii] outer source #%s" % src["owner_uid"], quiet=True)
                m = [r for r in rows if r.get("wire") == ow]
                rec["outer_source_node"] = {
                    "node_uid": src["owner_uid"], "class": src["owner_class"],
                    "found_on": (loc.get("found") or {}),
                    "terminal_index": m[0]["i"] if m else None,
                    "terminal_name": m[0]["name"] if m else None,
                    "wire_uid": ow,
                    "name_route": ("node_terms row whose WireUID == %d" % ow) if m else
                                  "NOT READABLE as a Nodes[] terminal (the owner is not a Node)"}
                fact("[L5 ii] *** #%d's OUTER-side source: node #%s class %r on %r, terminal index %r name "
                     "%r, wire uid %d ***"
                     % (TUNNEL_T1_UID, src["owner_uid"], src["owner_class"],
                        (loc.get("found") or {}).get("diagram_uid"),
                        rec["outer_source_node"]["terminal_index"],
                        rec["outer_source_node"]["terminal_name"], ow))
        else:
            fact("[L5 ii] #%d's OUTSIDE terminal carries NO wire (out_wire 0, wire_err %r) - so it has no "
                 "outer-side source to name" % (TUNNEL_T1_UID, tun.get("out_wire_err")))
    else:
        fact("[L5 ii] #%d was NOT reachable through tunnels(): index %r, error %r"
             % (TUNNEL_T1_UID, ti, terr))

    # ---- (iii) the inner terminals of #4194 and #3974 (FlatSequenceInnerTunnels)
    print("\n---------- [L5 iii] THE TWO FlatSequenceInnerTunnels #%d / #%d" % FS_INNER, flush=True)
    fsi, fserr = safe("[L5 iii] report_all('FlatSequenceInnerTunnel')",
                      lambda: g.report_all(path, "FlatSequenceInnerTunnel"), [])
    by_uid = {r["uid"]: r for r in (fsi or [])}
    rec["flatseq_inner_rows"] = len(by_uid)
    rec["flatseq_inner_error"] = fserr
    fact("[L5 iii] report_all('FlatSequenceInnerTunnel'): %d row(s)%s"
         % (len(by_uid), ("  [%s]" % fserr) if fserr else ""))
    out = {}
    for u, srwire in ((FS_INNER[0], 4185), (FS_INNER[1], 3968)):
        row = by_uid.get(u)
        e = {"uid": u, "in_census": row is not None,
             "class": (row or {}).get("class"), "pos": list((row or {}).get("pos") or []),
             "owner_class": (row or {}).get("owner"), "known_wire_uid": srwire}
        w, werr2 = safe("[L5 iii] wire_source_owner(%d)" % srwire,
                        lambda ww=srwire: WIRE_TERMS(path, ww, n=12), [])
        e["wire_walk"] = w
        e["wire_walk_error"] = werr2
        e["terminal_readability"] = (
            "NOT READABLE: this fleet's only wrapped tunnel-terminal reader is OpTunnels_v0 "
            "(`g.tunnels`), which traverses class 'LoopTunnel' ONLY (tools/gscript.py:941-948); a "
            "FlatSequenceInnerTunnel is a different class, and a tunnel is not a `Nodes[]` entry, so "
            "`node_terms`/`node_terms_uid` - whose ONLY addressing is Diagram[d].Nodes[n].Terminals[t] - "
            "cannot reach it either. What IS addressable is the uid, the class, the position and the wire "
            "uid, all printed above. Reading a tunnel terminal's index or NAME would need a NEW OP.")
        out[str(u)] = e
        fact("[L5 iii] #%d: in census %r ; class %r ; pos %r ; owner %r ; wire %d walk %r"
             % (u, e["in_census"], e["class"], e["pos"], e["owner_class"], srwire, w))
        fact("[L5 iii] #%d TERMINALS: %s" % (u, e["terminal_readability"]))
    rec["flatseq_inner"] = out
    rec["left_shift_registers_fed"] = list(LEFT_SRS)
    dump()
    return rec


def main():
    print("=== diag_c67_addsr  %s  (bgrun --material --max-min 35)" % STAMP, flush=True)
    print("=== PURE MEASUREMENT. NOTHING IS BUILT. NO DELIVERABLE .vi IS EDITED OR SAVED. NO ROUTE IS "
          "CHOSEN OR RECOMMENDED. NOTHING FOUND HERE IS REPAIRED.", flush=True)
    try:
        phase_0()
        for n, fn in ((1, leg_1), (2, leg_2), (3, leg_3), (4, leg_4), (5, leg_5)):
            if left_s() < LEG_MIN_S:
                gate("LEG %d had wall-clock left to run" % n, False,
                     "only %.0f s left before the reserve" % left_s())
                continue
            try:
                fn()
            except Stop:
                raise
            except Exception as e:                                                 # noqa: BLE001
                msg = "%s: %s" % (type(e).__name__, str(e)[:500])
                K.setdefault("leg%d" % n, {})["unexpected_exception"] = msg
                fact("LEG %d UNEXPECTED EXCEPTION: %s" % (n, msg))
                gate("LEG %d completed without an unexpected exception" % n, False, msg)
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        print("\n---------- [Y] SCRATCHES, THE SIX md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for n, p in sorted(SCRATCH.items()):
            safe("close_panel(LEG %d scratch)" % n, lambda pp=p: g.close_panel(pp))
            if os.path.exists(p):
                safe("remove LEG %d's scratch" % n, lambda pp=p: os.remove(pp))
            gate("Y LEG %d's scratch %s is gone (exists=False)" % (n, os.path.basename(p)),
                 not os.path.exists(p), "")
        for tag, path, pin in PINS:
            pr = probe("Y %s AFTER" % tag, path)
            gate("Y %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"]["after"], R["handles"].get("before")))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"]]
        R["files_left_on_disk"] = left
        print("\nTHE FILES THIS RUN LEFT ON DISK: %r" % (left,), flush=True)
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        gate("Y this run left NO file on disk (it is a reader)", not left, "%r" % (left,))
        dump()
        print("\n=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                    ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
