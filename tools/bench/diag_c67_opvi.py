"""diag_c67_opvi - cycle 67 material #3 PART B: IS THE OP VI ITSELF THE NO-OP? Five legs, four fresh
scratches, nothing saved.

A DIAGNOSTIC under tools/bench/, never a recipe (48(n)). It MEASURES whether `OpAddShiftReg_v0.vi` runs at
all, after `tools/bench/diag_c67_addsr.log` showed `g.add_shift_reg` returning the SAME uid 23561 with error
'' for THREE different While loops in THREE different scratch files, creating nothing in any of them
(`GObject` 10028 -> 10028, `Tunnel` 471 -> 471, both register classes 36 -> 36, `ExecState` 1 -> 1 where
`tools/gscript.py:683-687` predicts 0), with uid 23561 absent from the VI's 10,028 `GObject` rows.

NOTHING IS BUILT. NO DELIVERABLE `.vi` IS EDITED OR SAVED. NO ROUTE IS CHOSEN OR RECOMMENDED. NOTHING FOUND
HERE IS REPAIRED - if L0 shows the op is broken, this file SAYS SO AND STOPS.

WHAT ALREADY EXISTED AND IS REUSED, NOT REBUILT (checked before a line was written: `docs/
toolkit-capabilities.md`, `grep "^def " tools/gscript.py`, `ls tools/recipes tools/bench`)
  - `tools/gscript.py:673` `add_shift_reg` (OpAddShiftReg_v0, INDEX row 37) - the creator under test. Its
    own body is the thing L0 inspects: `op(path)` -> `SetControlValue` x4 -> `_run(vi)` -> `_err(vi,
    'error out 3')` -> `int(vi.GetControlValue('UID 2'))`.
  - `tools/gscript.py:2475` `fp_labels` (OpFPLabels_v0) - the ONLY wrapped reader of a VI's panel objects in
    tabbing order with the is-indicator flag. L0 runs it AGAINST THE OP VI AS A TARGET. Read-only.
  - `tools/gscript.py:210` `op` / `:1977` `exec_state` / `:1005` `count` / `:488` `report_all` /
    `:626` `loop_cast` / `:1241` `open_panel` / `:1268` `ensure_loaded` - all read/used as they are.
  - `tools/recipes/build_d1_v0.py:318` `move_in` (L2 only, exactly once).
  - `tools/bench/diag_c66b_s3b_m3.py:183-193` `SET[0]` - the FIRST move that file performs, reproduced here
    VERBATIM as L2's one write: uid 3529 `- Inc (PgDn)` -> Diagram #23058 at (40, 60).
  - `tools/bench/diag_s2_scaffold.py` - `fresh()` (the pre-batch restart, 44(e)), the md5 pins.
  - `tools/bench/diag_c67_addsr.py` - every helper below (gate/fact/probe/dump/safe/read_es/counts/
    sr_class_uids/sr_class_diff/loop_index_of/make_scratch) is REUSED IN SHAPE from it.
  - `tools/bench/c60c_astcheck.py` - the static gate, run on THIS file before launch. This file calls
    `move_in` ONCE (L2, mandated by the brief), so gate 7's `owner` route CANNOT pass by construction and
    the gate is run `--route movein` instead; the gate file is NOT edited and CYCLE_GUARD_OFF is never set.
  NO new op, NO new verb, NO edit to tools/gscript.py, NO edit to any *_astcheck.py, NO recipe.

PRIOR ART THAT BEARS DIRECTLY ON THE QUESTION, recorded so this run is not re-deriving it
  - `tools/gscript.py:1268-1322` `ensure_loaded`: scripting EDITS are SILENTLY DECLINED on a target that is
    not fully loaded, and the measured cure is `open_panel` (`tools/bench/diag_delete_matrix.log`,
    2026-09-16: the same op, same target, same class, same index removed NOTHING without `open_panel` and
    exactly one WITH it, across six object classes). The mechanism is explicitly NOT known.
  - `move_in` (`build_d1_v0.py:321`) calls `g.ensure_loaded(target)` as its first statement.
    `add_shift_reg` (`tools/gscript.py:699-707`) DOES NOT. That asymmetry is a FACT about the two wrappers,
    printed by this run as [L0f]; it is NOT a diagnosis and NOTHING here acts on it.

THE HANDLE RULE FOR THIS RUN, from the last one's measurement: six whole-VI `report_all('GObject')` censuses
took LabVIEW's handle count 34,602 -> 91,288. **THERE IS NO `GObject` CENSUS ANYWHERE IN THIS FILE.** The
narrow censuses answer the same question: `Tunnel` (both `LeftShiftRegister` 16442 and `RightShiftRegister`
16399 DERIVE from it, `docs/NAMES.md:263-264`, so a created register is +2 `Tunnel`) plus the two register
classes uid-SET diffed directly. Handles are read at entry and exit and the delta is reported.

THE BEDS
  A2 `claudeDev\\D1_s3b_row2_20260921_160311.vi`, md5 26c54ff784cb5cea21edbd214d2cc3a0, 476,759 B - the bed
     for L1, L2 and L3. READ-ONLY and md5-pinned BEFORE and AFTER.
  S2 `claudeDev\\D1_s2_loops.vi`, md5 6ff19497f2309e007a214660bb64b911 - L4's DIFFERENT target. READ-ONLY and
     md5-pinned BEFORE and AFTER.
  EVERY WRITE LEG TAKES ITS OWN FRESH SCRATCH DUPLICATE. Every scratch is removed;
  `THE FILES THIS RUN LEFT ON DISK: [...]` is printed and is expected to be `[]`.

THE LEGS
  L0  READ-ONLY, FIRST, AND IT MAY ANSWER THE WHOLE QUESTION. On `claudeDev\\OpAddShiftReg_v0.vi` ITSELF,
      without running it: path, size, md5, COLD `ExecState`; then its FULL panel control AND indicator list
      (`fp_labels`) with each one's CURRENT value AS LOADED, read with the very same
      `op(path).GetControlValue(name)` the wrapper uses. THE HEADLINE: is the loaded value of the indicator
      named by `tools/bench/opaddshiftreg_labels.json`'s `uid` key (`'UID 2'`) EQUAL TO 23561? Plus the
      op's `error out 3` cluster as loaded, and whether EVERY key in that labels file resolves to a panel
      object that exists. The same read is done for `OpAddShiftRegF_v0.vi`. NOTHING is run, set or saved.
      L0 RUNS BEFORE ANY `add_shift_reg` CALL IN THIS PROCESS, so the values it reads are the DISK DEFAULTS.
  L1  CONTROL, in this session. Fresh scratch of A2. ONE `add_shift_reg` on the loop whose uid echoes 23032.
      Immediately after, the OP VI's OWN `UID 2` indicator and its FULL `error out 3` cluster are read back
      raw - not only the wrapper's return. Then `Tunnel` + both register censuses + `ExecState`.
  L2  LOAD STATE. Fresh scratch. FIRST one `move_in` - exactly `diag_c66b_s3b_m3.py`'s first move, a write
      MEASURED to work on this bed - THEN `add_shift_reg` on the same loop, then the same readbacks.
  L3  OPEN PANEL. AUTHORISED FOR THIS LEG ONLY BY THE BRIEF. Fresh scratch. `g.open_panel(target)` first,
      then `add_shift_reg`, then the same readbacks, then `close_panel`. No file is replaced under a path
      LabVIEW has loaded and nothing is saved.
  L4  A DIFFERENT TARGET. Fresh scratch of S2. `add_shift_reg` on one of ITS While loops, uid echoed at that
      index immediately before the call. Same readbacks. Asks whether the no-op is bed-specific.

PREDICTION CONTRACT (machine-checkable; every prediction below is a MEASUREMENT, and a measurement that
comes back negative does NOT fail this run - see THE GATE RULE)
  P-L0  If the claim under review is true, `GetControlValue('UID 2')` on the freshly loaded op VI reads
        exactly 23561 and `error out 3` reads (False, 0, '').
  P-L1  `tools/gscript.py:683-687` predicts a register is created and `ExecState` goes to 0. Measured last
        run on this same loop: neither happened.
  P-L2  If the op declines because the target is not in the edit-ready state, the `move_in` that precedes it
        (which calls `ensure_loaded` -> `open_panel`) leaves the target in that state and the register
        appears. If the op never runs at all, L2 looks exactly like L1.
  P-L3  Same separator as L2 without the structural write.
  P-L4  If the no-op is bed-specific, L4 creates a register; if it is the op, L4 looks like L1.
  Y     Both md5 pins hold BEFORE and AFTER; every scratch `exists=False`; `THE FILES THIS RUN LEFT ON DISK:
        []`; refs opened == closed, 0 live; handles either side.

THE PART A REVIEW, AND WHAT OF IT IS IN THIS FILE (`archive/peer/2026-09-21-c67-addsr-opvi.md`, claude /
hypothesis, opus / effort max, ANSWERED 767 s, $5.4537). IT DID NOT CONCEDE. Implemented here, mechanically,
because each is a READING and none changes a step:
  - its R1: the loaded `UID 2` / `error out 3` read with ZERO VI runs - already L0's headline.
  - its R3: **md5 AND MTIME** of both op VIs, "the only way its default could have become 23561" being a
    re-save after 2026-09-14. `[L0d]` prints the mtime; the build's own acceptance test took uid **503**.
  - its R5, the ONLY proof of execution it accepts: a FULL PANEL SNAPSHOT of the op VI taken immediately
    BEFORE and immediately AFTER the one `add_shift_reg` call of each write leg, on the SAME loaded
    instance. ANY changed value proves the diagram executed. `panel_snapshot` / `snapshot_diff`, `[Lnh]`.
  - its correction that legs 1..4 share ONE CACHED op-VI reference (`tools/gscript.py:210-215`), so an
    indicator is STICKY across runs and later legs carry no independent information about the returned uid:
    recorded as `[L0e]`, and answered by taking each leg's baseline from its OWN before-snapshot rather
    than from the saved default.
  - its R7: "already ruled out" item 3 rests on #637 being on the TOP-LEVEL diagram, which was never
    measured. `[L1t]` asks exactly that with ONE `node_labels(0)` call - is #637 in the top-level Nodes[]?
  - its s4 warning that `_err` returns None on ANY read exception (`tools/gscript.py:443-446`), so `''`
    conflates three states: every `GetControlValue` here records its exception VERBATIM and a raise is
    reported as its own measurement outcome, never as an empty value.
NOT ACTED ON, quoted verbatim to judgement in the review's `## What was done with it` and in this session's
`OPEN:` - all of them new mechanisms, new verbs or writes this brief forbids: its **R6** (marshal `Run` to a
thread and poll the op VI's `ExecState` for 2/3), its one-line `SetControlValue("no such control", 0)` probe
(the brief says L0 sets NOTHING), its rival **A** (the UID property node's `error in` is unwired, so its own
error goes nowhere - `tools/recipes/build_opaddshiftreg_v0.py:236-259`), its rival **B** (the op carries TWO
`Open VI Reference` nodes, `tools/bench/build_opaddshiftreg_v0_run3.log:8,:12`, so the Invoke chain may
descend from the one the wrapper's `"vi path"` does NOT feed), and `g.revert(op VI)` as a way to restore a
contaminated baseline.

THE GATE RULE FOR THIS RUN (the brief, verbatim in intent): each leg's outcome is a FACT LINE, not a
pass/fail gate. A measurement that comes back negative must NOT mark this log as failing. ONLY HYGIENE
conditions are gates: the md5 pins, the scratches removed, the reference balance, and "this run left no file
on disk". The exit code is 0 when the hygiene gates all pass, whatever the measurements say. Measurement
outcomes are printed as `MEAS <name>: YES|NO  <detail>` so they can never be mistaken for a gate line.

FORBIDDEN AND ABSENT: no `connect_nested_v1`; no `wire_indicators`; no `wire_sr`; no `allow_broken`; no
`gui_save`; no `remove_bad_wires*`; no GUI action; no new op VI; no new verb; `tools/gscript.py` NOT edited;
no `*_astcheck.py` edited; no recipe; no VI run of any DELIVERABLE (34(f) - op VIs are run, that is the
fleet's mechanism, and the op VI under test is NOT run in L0); no motor / ASI / camera (rig ASSEMBLED); no
new process device. `move_in` ONLY in L2, exactly once. `g.open_panel` ONLY in L3 (plus whatever `move_in`
does for itself inside L2, which is `move_in`'s own body and is recorded as such).
`retrospective.py` / `audit_cycle.py` / `violations.py` / `doc_ingest.py` / `prior_art_review.py` NOT run
(54(a)). `docs/cycle27-plan.md` and STATUS's `## NEXT` are NOT touched.
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
from build_d1_v0 import move_in                                                    # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
BED_SIZE = 476759

PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5),
        ("A2 THE BED", BED, BED_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5))

# The two op VIs under inspection. READ ONLY - never run in L0, never edited, never saved.
OP_ADDSR = os.path.join(g.CLAUDEDEV, "OpAddShiftReg_v0.vi")
OP_ADDSRF = os.path.join(g.CLAUDEDEV, "OpAddShiftRegF_v0.vi")
LABELS_ADDSR = os.path.join(BENCH, "opaddshiftreg_labels.json")
LABELS_ADDSRF = os.path.join(BENCH, "opaddshiftregF_labels.json")
# The FOUR control names `add_shift_reg` writes before it runs the op (tools/gscript.py:700-702). Three are
# bare literals in the wrapper; the fourth comes from the labels file's `y_position` key.
WRAPPER_SETS = ("vi path", "Class Name", "index")

LOOP_A_UID = 23032               # the While loop the no-op was measured on, three times
LOOP637_UID = 637                # the loop that already carries 14 registers
RETURNED_UID = 23561             # what all three add_shift_reg calls returned (diag_c67_addsr.log:69,:238,:335)
BODY_A_UID = 23058               # L2's move destination (diag_c66b_s3b_m3.py:142)
MOVE_UID = 3529                  # diag_c66b_s3b_m3.py:184 - SET[0], the first move that file performs
MOVE_NAME = "- Inc (PgDn)"
MOVE_POS = (40, 60)

BASE = {"Node": 632, "Wire": 1907, "ControlTerminal": 116, "Local": 10, "LoopTunnel": 135}
BASE_TUNNEL = 471

RUN_DEADLINE_S = 35 * 60.0
RESERVE_S = 180.0
LEG_MIN_S = 150.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c67_opvi.json")

# FOUR fresh scratches, one per WRITE leg (L0 writes nothing and needs none).
SCRATCH = {n: os.path.join(g.CLAUDEDEV, "WORK_C67OPVI_L%d_%s.vi" % (n, STAMP)) for n in (1, 2, 3, 4)}
SCRATCH_BED = {1: BED, 2: BED, 3: BED, 4: S2_ARTEFACT}
SCRATCH_PIN = {1: BED_MD5, 2: BED_MD5, 3: BED_MD5, 4: S2_MD5}

T_START = time.time()
passes, fails, facts, meas = [], [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 67 material #3 PART B: is OpAddShiftReg_v0.vi itself the no-op? L0 reads the op VI's "
             "saved defaults; L1/L2/L3/L4 vary load state and target around one add_shift_reg call.",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gate_rule": "ONLY HYGIENE conditions are gates (md5 pins, scratches removed, refs balanced, no file "
                  "left on disk). Every leg outcome is a MEAS fact line and can never fail this run.",
     "no_gobject_census_anywhere": "six of them took handles 34,602 -> 91,288 last run",
     "nothing_is_built": True, "no_deliverable_vi_edited_or_saved": True,
     "chooses_no_route": True, "recommends_no_route": True, "repairs_nothing": True,
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "move_in_calls": "exactly one, in L2", "open_panel_calls": "L3 only (plus move_in's own ensure_loaded)",
     "no_connect_nested_v1": True, "no_wire_indicators": True, "no_wire_sr": True,
     "gscript_not_edited": True, "no_astcheck_gate_file_edited": True, "no_gui_action": True,
     "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); the op VI under test is NOT run in L0",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "measurements": [], "legs": {}}
K = R["legs"]


class Stop(Exception):
    pass


def gate(name, ok, detail=""):
    """HYGIENE ONLY. `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's anchor."""
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def measure(name, yes, detail=""):
    """A MEASUREMENT OUTCOME. Recorded, printed, never counted against the run's exit code."""
    rec = {"name": name, "outcome": bool(yes), "detail": detail}
    meas.append(rec)
    R["measurements"].append(rec)
    print(("  MEAS  %s: %s%s" % (name, "YES" if yes else "NO", ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return bool(yes)


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
    """NARROW censuses only. `count` is ONE op run per class (tools/gscript.py:1005) - it is NOT the
    whole-VI GObject traverse that took handles 34,602 -> 91,288 last run."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s counts: %r" % (tag, rec))
    return rec


def sr_class_uids(path, tag):
    """`LeftShiftRegister` 16442 and `RightShiftRegister` 16399 BOTH DERIVE FROM `Tunnel`
    (docs/NAMES.md:263-264) and a Traverse includes subclasses, so the whole-VI `Tunnel` count is itself a
    creation detector (+2 per register) and the two register classes can be uid-SET diffed directly. Carried
    forward from archive/peer/2026-09-21-c67-addsr-noop.md s1 - a READING, not a route."""
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


def loop_index_of(path, uid, cls, tag):
    """Resolve the loop's index in report_all(cls) FRESH and ECHO report_all(cls)[idx].uid == uid immediately
    before every call that takes a loop_index. An index is never carried across a call."""
    rows, err = safe("%s report_all(%r)" % (tag, cls), lambda: g.report_all(path, cls), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    rec = {"tag": tag, "class": cls, "want_uid": uid, "loop_index": idx, "echoed_uid": echo,
           "rows": len(rows or []), "error_verbatim": err}
    K.setdefault("loop_index_echoes", []).append(rec)
    fact("%s A7 ECHO: report_all(%r)[%r].uid == %r (want #%s; %d row(s))"
         % (tag, cls, idx, echo, uid, len(rows or [])))
    measure("%s the echoed uid at the index used IS #%s" % (tag, uid), echo == uid,
            "loop_index %r echoed %r" % (idx, echo))
    return idx


def make_scratch(n, tag):
    src, pin = SCRATCH_BED[n], SCRATCH_PIN[n]
    dest = SCRATCH[n]
    shutil.copy2(src, dest)
    pr = probe("%s the fresh scratch for LEG %d (from %s)" % (tag, n, os.path.basename(src)), dest)
    measure("%s LEG %d's scratch is byte-identical to its bed" % (tag, n), pr.get("md5") == pin,
            "%r vs pin %s" % (pr.get("md5"), pin[:8]))
    return dest


# ====================== R5: THE ONLY PROOF OF EXECUTION THE PART A REVIEW ACCEPTS - A PANEL SNAPSHOT DIFF
_PANEL_NAMES = []


def panel_snapshot(tag):
    """Every panel object of OpAddShiftReg_v0, by name, with its value AS IT STANDS ON THE LOADED INSTANCE.
    Taken immediately before and immediately after each leg's ONE `add_shift_reg` call. The review's R5:
    "ANY changed value proves the diagram executed", and the baseline must be the LOADED value, not the
    saved default and not a value a previous call in this process left. Read-only: no Run, no Set, no save."""
    rec = {"tag": tag, "values": {}, "errors": {}}
    ref, rerr = safe("%s op(OpAddShiftReg_v0)" % tag, lambda: g.op(OP_ADDSR))
    rec["ref_error"] = rerr
    if ref is None or not _PANEL_NAMES:
        rec["unavailable"] = "ref_error %r ; %d panel name(s) known" % (rerr, len(_PANEL_NAMES))
        fact("%s PANEL SNAPSHOT unavailable: %s" % (tag, rec["unavailable"]))
        return rec
    for name in _PANEL_NAMES:
        v, verr = safe("%s GetControlValue(%r)" % (tag, name), lambda nn=name: ref.GetControlValue(nn))
        rec["values"][name] = v if not isinstance(v, tuple) else list(v)
        if verr:
            rec["errors"][name] = verr
    fact("%s PANEL SNAPSHOT: %d value(s), %d read error(s)" % (tag, len(rec["values"]), len(rec["errors"])))
    return rec


def snapshot_diff(tag, before, after):
    b, a = (before or {}).get("values") or {}, (after or {}).get("values") or {}
    changed = {k: [b.get(k), a.get(k)] for k in sorted(set(b) | set(a)) if b.get(k) != a.get(k)}
    rec = {"changed": changed, "n_before": len(b), "n_after": len(a)}
    fact("%s PANEL DIFF across the one add_shift_reg call: %d value(s) changed -> %r"
         % (tag, len(changed), changed))
    return rec


# ============================================================ THE OP VI'S OWN READBACK, RAW
def op_readback(tag):
    """The OP VI's OWN `UID 2` indicator and its FULL `error out 3` cluster, read raw off the same cached
    reference the wrapper used - NOT the wrapper's return value. `add_shift_reg` collapses both into an int
    and a string; this prints what is actually on the op's panel after the run."""
    rec = {"tag": tag}
    ref, rerr = safe("%s op(OpAddShiftReg_v0)" % tag, lambda: g.op(OP_ADDSR))
    rec["ref_error"] = rerr
    if ref is None:
        fact("%s OP READBACK unavailable: %s" % (tag, rerr))
        return rec
    for key, name in (("uid_indicator", "UID 2"), ("error_cluster", "error out 3")):
        v, verr = safe("%s GetControlValue(%r)" % (tag, name), lambda nn=name: ref.GetControlValue(nn))
        rec[key] = v if not isinstance(v, tuple) else list(v)
        rec[key + "_error"] = verr
        fact("%s OP READBACK %-14r = %r%s" % (tag, name, rec[key], ("  [%s]" % verr) if verr else ""))
    for name in WRAPPER_SETS + ("Y Position",):
        v, verr = safe("%s GetControlValue(%r)" % (tag, name), lambda nn=name: ref.GetControlValue(nn))
        rec.setdefault("inputs_as_left", {})[name] = v if not isinstance(v, tuple) else list(v)
        fact("%s OP READBACK input %-12r = %r%s" % (tag, name, rec["inputs_as_left"][name],
                                                    ("  [%s]" % verr) if verr else ""))
    return rec


def write_leg(n, tag, target, loop_uid, loop_cls="WhileLoop"):
    """The IDENTICAL measurement block every write leg runs after whatever it does first."""
    rec = {}
    es0 = read_es("%s the scratch, before add_shift_reg" % tag, target)
    rec["exec_state_before"] = es0
    c0 = counts(target, "%s BEFORE" % tag)
    rec["counts_before"] = c0
    src0 = sr_class_uids(target, "%s BEFORE" % tag)
    rec["registers_before"] = {c: sorted(src0.get(c, {})) for c in
                               ("RightShiftRegister", "LeftShiftRegister")}

    idx = loop_index_of(target, loop_uid, loop_cls, "%s before add_shift_reg" % tag)
    rec["loop_index_used"] = idx
    rec["loop_uid"] = loop_uid
    snap0 = panel_snapshot("%s OP PANEL BEFORE the call" % tag)
    rec["op_panel_before"] = snap0
    t0 = time.time()
    uid, err = safe("%s add_shift_reg(index=%r)" % (tag, idx),
                    lambda: g.add_shift_reg(target, idx, class_name=loop_cls) if idx is not None else None)
    rec["call_cost_s"] = round(time.time() - t0, 2)
    rec["returned_uid"] = uid
    rec["wrapper_error_verbatim"] = err
    fact("%s *** add_shift_reg(target, loop_index=%r, class_name=%r) -> uid %r ; wrapper error %r "
         "(%.2f s) ***" % (tag, idx, loop_cls, uid, err, rec["call_cost_s"]))
    snap1 = panel_snapshot("%s OP PANEL AFTER the call" % tag)
    rec["op_panel_after"] = snap1
    rec["op_panel_diff"] = snapshot_diff(tag, snap0, snap1)
    measure("%s R5: SOME panel value of the op VI CHANGED across the call - the ONLY proof of execution "
            "the Part A review accepts" % tag, bool(rec["op_panel_diff"]["changed"]),
            "changed %r" % (rec["op_panel_diff"]["changed"],))
    rec["op_readback"] = op_readback("%s AFTER" % tag)
    measure("%s the returned uid is the constant %d again" % (tag, RETURNED_UID), uid == RETURNED_UID,
            "returned %r" % (uid,))

    es1 = read_es("%s immediately after add_shift_reg" % tag, target)
    rec["exec_state_after"] = es1
    c1 = counts(target, "%s AFTER" % tag)
    rec["counts_after"] = c1
    rec["counts_changed"] = {k: (c0.get(k), c1.get(k)) for k in c1 if c0.get(k) != c1.get(k)}
    dt = (c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0)
    rec["tunnel_delta"] = dt
    src1 = sr_class_uids(target, "%s AFTER" % tag)
    rec["register_diff"] = sr_class_diff(tag, src0, src1)
    minted = rec["register_diff"]["RightShiftRegister"]["minted"]

    measure("%s any whole-VI class count changed" % tag, bool(rec["counts_changed"]),
            "changed %r" % (rec["counts_changed"],))
    measure("%s Tunnel went +2 (a created register is a Left AND a Right, both Tunnel subclasses)" % tag,
            dt == 2, "delta %r (before %r / after %r)" % (dt, c0.get("Tunnel"), c1.get("Tunnel")))
    measure("%s a RightShiftRegister uid was MINTED" % tag, bool(minted),
            "%r" % (rec["register_diff"]["RightShiftRegister"],))
    measure("%s ExecState went 1 -> 0 as tools/gscript.py:683-687 predicts" % tag,
            es0 == 1 and es1 == 0, "%r -> %r" % (es0, es1))

    lc, lcerr = safe("%s loop_cast(#%s)" % (tag, loop_uid),
                     lambda: g.loop_cast(target, idx, class_name=loop_cls) if idx is not None else None)
    rec["loop_cast_after"] = lc
    rec["loop_cast_error"] = lcerr
    if lc:
        fact("%s loop_cast(#%s) AFTER: loop_uid echo %r ; shift_reg_uids %r ; errors %r"
             % (tag, loop_uid, lc.get("loop_uid"), sorted(int(u) for u in lc.get("shift_reg_uids") or []),
                lc.get("errors")))
    dump()
    return rec


# ======================================================================= PHASE 0 - files only, zero LabVIEW
def phase_0():
    print("\n---------- [0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    for tag, path, pin in PINS:
        pr = probe("Y %s BEFORE" % tag, path)
        gate("Y %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    pr = probe("Y THE BED size", BED)
    measure("Y the bed is %d B" % BED_SIZE, str(pr.get("size")) == str(BED_SIZE), "%r" % (pr.get("size"),))
    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


# ====================================================================== LEG 0 - READ THE OP VI ITSELF
def leg_0():
    print("\n========== LEG 0 - READ-ONLY: IS THE OP VI ITSELF THE ANSWER?  (nothing is run, set or saved)",
          flush=True)
    rec = K.setdefault("leg0", {})
    rec["runs_nothing"] = True

    for tag, opath, lpath in (("OpAddShiftReg_v0", OP_ADDSR, LABELS_ADDSR),
                              ("OpAddShiftRegF_v0", OP_ADDSRF, LABELS_ADDSRF)):
        print("\n---------- [L0] %s" % tag, flush=True)
        e = {"path": opath, "exists": os.path.exists(opath), "labels_file": lpath}
        if not e["exists"]:
            fact("[L0] %s IS NOT ON DISK at %s - nothing to read" % (tag, opath))
            rec[tag] = e
            continue
        pr = probe("[L0] %s ON DISK" % tag, opath)
        e["md5"], e["size"] = pr.get("md5"), pr.get("size")
        # R3: the MTIME. The op was built 2026-09-14 and its acceptance test minted uid 503, so a saved
        # default of 23561 would require a re-save AFTER that day by a session nobody has checked for.
        mt = os.path.getmtime(opath)
        e["mtime_epoch"] = mt
        e["mtime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mt))
        fact("[L0d] %s MTIME = %s (built 2026-09-14; its acceptance test minted uid 503, not %d)"
             % (tag, e["mtime"], RETURNED_UID))
        measure("[L0d] %s was LAST WRITTEN on its 2026-09-14 build date (no later re-save)" % tag,
                e["mtime"].startswith("2026-09-14"), "mtime %s" % e["mtime"])
        lab, lerr = safe("[L0] read %s" % os.path.basename(lpath),
                         lambda p=lpath: json.load(open(p, encoding="utf-8")), {})
        e["labels"] = lab
        e["labels_error"] = lerr
        fact("[L0] %s labels file %s = %r" % (tag, os.path.basename(lpath), lab))

        es = read_es("[L0] %s COLD ExecState (read-only)" % tag, opath)
        e["cold_exec_state"] = es
        measure("[L0a] %s reopens COLD at ExecState 1 (i.e. it is RUNNABLE, not broken)" % tag, es == 1,
                "ExecState %r" % (es,))

        rows, rerr = safe("[L0] fp_labels(%s)" % tag, lambda p=opath: g.fp_labels(p), [])
        e["panel_rows"] = [{"i": i, "label": t, "indicator": bool(ind)} for i, t, ind in (rows or [])]
        e["panel_read_error"] = rerr
        fact("[L0] %s panel: %d object(s)%s" % (tag, len(rows or []), ("  [%s]" % rerr) if rerr else ""))

        ref, referr = safe("[L0] op(%s)" % tag, lambda p=opath: g.op(p))
        e["ref_error"] = referr
        values = {}
        if ref is not None:
            for row in e["panel_rows"]:
                name = row["label"]
                v, verr = safe("[L0] %s GetControlValue(%r)" % (tag, name),
                               lambda nn=name: ref.GetControlValue(nn))
                row["value_as_loaded"] = v if not isinstance(v, tuple) else list(v)
                row["value_error"] = verr
                values[name] = row["value_as_loaded"]
                fact("[L0] %s  %-3d %-8s %-24r = %r%s"
                     % (tag, row["i"], "IND" if row["indicator"] else "CTL", name,
                        row["value_as_loaded"], ("  [%s]" % verr) if verr else ""))
        e["values_as_loaded"] = values
        if tag == "OpAddShiftReg_v0":
            _PANEL_NAMES[:] = [r["label"] for r in e["panel_rows"]]
            fact("[L0] the %d panel name(s) just read become the R5 SNAPSHOT SET used by every write leg: %r"
                 % (len(_PANEL_NAMES), _PANEL_NAMES))
        raised = sorted(n for n, r in ((row["label"], row) for row in e["panel_rows"])
                        if r.get("value_error"))
        e["names_whose_read_raised"] = raised
        measure("[L0e] %s: NO GetControlValue raised while reading the loaded panel (a raise would mean the "
                "label file is wrong and `_err` has been blind since 2026-09-14)" % tag, not raised,
                "raised on %r" % (raised,))

        # THE HEADLINE: does the `uid` key's indicator hold 23561 as its SAVED DEFAULT?
        uid_name = (lab or {}).get("uid")
        e["uid_indicator_name"] = uid_name
        uid_val = values.get(uid_name) if uid_name else None
        if uid_name and uid_name not in values and ref is not None:
            uid_val, uerr = safe("[L0] %s GetControlValue(%r) direct" % (tag, uid_name),
                                 lambda nn=uid_name: ref.GetControlValue(nn))
            e["uid_direct_read_error"] = uerr
        e["uid_indicator_value_as_loaded"] = uid_val
        fact("[L0] *** %s: the `uid` key names %r ; ITS VALUE AS LOADED FROM DISK IS %r ; the constant the "
             "wrapper returned three times is %d ***" % (tag, uid_name, uid_val, RETURNED_UID))
        hit = False
        try:
            hit = int(uid_val) == RETURNED_UID
        except Exception:                                                          # noqa: BLE001
            hit = False
        e["saved_default_is_23561"] = hit
        measure("[L0b] %s's SAVED DEFAULT for %r IS %d" % (tag, uid_name, RETURNED_UID), hit,
                "loaded value %r" % (uid_val,))

        err_name = (lab or {}).get("error")
        e["error_indicator_name"] = err_name
        err_val = values.get(err_name) if err_name else None
        if err_name and err_name not in values and ref is not None:
            err_val, eerr = safe("[L0] %s GetControlValue(%r) direct" % (tag, err_name),
                                 lambda nn=err_name: ref.GetControlValue(nn))
            e["error_direct_read_error"] = eerr
        e["error_cluster_as_loaded"] = err_val if not isinstance(err_val, tuple) else list(err_val)
        fact("[L0] %s: the error-cluster indicator %r reads %r AS LOADED"
             % (tag, err_name, e["error_cluster_as_loaded"]))

        panel_names = {r["label"] for r in e["panel_rows"]}
        want = list((lab or {}).values()) + list(WRAPPER_SETS)
        missing = [n for n in want if n not in panel_names]
        e["names_wanted"] = want
        e["names_missing_from_panel"] = missing
        fact("[L0] %s: every name the wrapper writes or reads, against the panel census -> MISSING %r"
             % (tag, missing))
        measure("[L0c] %s: every labels-file key AND every wrapper-written control exists on the panel"
                % tag, not missing, "missing %r ; panel has %d object(s)" % (missing, len(panel_names)))
        rec[tag] = e
        dump()

    # [L0f] the wrapper asymmetry, stated as a FACT about two files on disk, acted on by nothing here.
    rec["wrapper_asymmetry"] = (
        "tools/recipes/build_d1_v0.py:321 `move_in` calls g.ensure_loaded(target) as its FIRST statement; "
        "tools/gscript.py:699-707 `add_shift_reg` does NOT call ensure_loaded or open_panel at all. "
        "tools/gscript.py:1268-1322 records that scripting EDITS are SILENTLY DECLINED on a target that is "
        "not fully loaded and that open_panel is the measured cure (tools/bench/diag_delete_matrix.log, "
        "2026-09-16). THIS IS A FACT ABOUT TWO FILES, NOT A DIAGNOSIS; nothing here is repaired and no "
        "route is chosen. L2 and L3 are the legs that vary that state.")
    fact("[L0f] %s" % rec["wrapper_asymmetry"])
    rec["cached_reference_caveat"] = (
        "PART A REVIEW, CONCEDED AND RECORDED: legs 1..4 of this run share ONE CACHED op-VI reference "
        "(tools/gscript.py:210-215) against one LabVIEW instance, and a front-panel indicator is STICKY "
        "across runs of the same loaded VI. So a later leg's RETURNED UID carries no information "
        "independent of an earlier leg's. That is why every write leg takes its OWN panel snapshot "
        "immediately before its call and diffs it against the one taken immediately after: each leg's "
        "baseline is its own loaded state, never the saved default and never another leg's residue.")
    fact("[L0e2] %s" % rec["cached_reference_caveat"])
    dump()
    return rec


# ====================================================================== LEG 1 - CONTROL
def leg_1():
    print("\n========== LEG 1 - CONTROL: one add_shift_reg on #%d, nothing done first" % LOOP_A_UID,
          flush=True)
    rec = K.setdefault("leg1", {})
    path = make_scratch(1, "[L1]")
    rec["preparation"] = "none - the scratch is opened by add_shift_reg's own op run and nothing else"
    rec.update(write_leg(1, "[L1]", path, LOOP_A_UID))

    # [L1t] R7 from the Part A review: last run's "the top-level-diagram hypothesis is refuted by leg 4"
    # holds only if #637 IS on the top-level diagram, and that was NEVER measured. ONE node_labels(0) call
    # answers it. A READ; nothing is decided here and the hypothesis itself is not re-argued.
    print("\n---------- [L1t] IS #%d ON THE TOP-LEVEL DIAGRAM? (Part A review R7)" % LOOP637_UID, flush=True)
    top, terr = safe("[L1t] node_labels(0) - the TOP-LEVEL diagram", lambda: g.node_labels(path, 0), [])
    top_uids = [r["uid"] for r in (top or [])]
    hit = next((r for r in (top or []) if r["uid"] == LOOP637_UID), None)
    hit_a = next((r for r in (top or []) if r["uid"] == LOOP_A_UID), None)
    rec["top_level_nodes"] = len(top_uids)
    rec["top_level_census_error"] = terr
    rec["loop637_on_top_level"] = hit is not None
    rec["loop23032_on_top_level"] = hit_a is not None
    fact("[L1t] the TOP-LEVEL diagram (traverse index 0) lists %d node(s)%s ; #%d present: %r ; #%d "
         "present: %r" % (len(top_uids), ("  [%s]" % terr) if terr else "", LOOP637_UID, hit is not None,
                          LOOP_A_UID, hit_a is not None))
    measure("[L1t] #%d IS on the TOP-LEVEL diagram (the premise last run's 'refuted by leg 4' rested on)"
            % LOOP637_UID, hit is not None, "top-level lists %d node(s)" % len(top_uids))
    dump()
    return rec


# ====================================================================== LEG 2 - LOAD STATE (one move_in)
def leg_2():
    print("\n========== LEG 2 - LOAD STATE: ONE move_in first (diag_c66b_s3b_m3.py SET[0]), then "
          "add_shift_reg on #%d" % LOOP_A_UID, flush=True)
    rec = K.setdefault("leg2", {})
    path = make_scratch(2, "[L2]")
    rec["preparation"] = ("exactly ONE move_in - diag_c66b_s3b_m3.py:184 SET[0], uid %d %r -> Diagram #%d "
                          "at %r - a write MEASURED to work on this bed. move_in's own body calls "
                          "g.ensure_loaded(target) (build_d1_v0.py:321)."
                          % (MOVE_UID, MOVE_NAME, BODY_A_UID, MOVE_POS))
    fact("[L2] %s" % rec["preparation"])

    es_pre = read_es("[L2] the scratch, COLD before the move", path)
    rec["exec_state_cold"] = es_pre
    lst, lerr = safe("[L2] report_all('Diagram')", lambda: g.report_all(path, "Diagram"), [])
    uids = [o["uid"] for o in (lst or [])]
    dest = uids.index(BODY_A_UID) if BODY_A_UID in uids else None
    rec["dest_diagram_uid"] = BODY_A_UID
    rec["dest_index_resolved"] = dest
    rec["diagram_rows"] = len(uids)
    rec["diagram_census_error"] = lerr
    fact("[L2] DESTINDEX: Diagram #%d -> traverse index %r (array length %d)" % (BODY_A_UID, dest, len(uids)))
    measure("[L2] the freshly resolved index %r still owns Diagram #%d (38(e))" % (dest, BODY_A_UID),
            dest is not None and uids[dest] == BODY_A_UID, "traverse_len %d" % len(uids))

    if dest is None:
        fact("[L2] the destination diagram was NOT resolvable, so the ONE permitted move_in was NOT called; "
             "the leg continues with add_shift_reg on an unprepared scratch, which makes it a SECOND L1 and "
             "is reported as such.")
        rec["move_called"] = False
    else:
        t0 = time.time()
        echoed, merr = safe("[L2] move_in(#%d -> Diagram #%d at %r)" % (MOVE_UID, BODY_A_UID, MOVE_POS),
                            lambda: move_in(path, MOVE_UID, dest, MOVE_POS))
        rec["move_called"] = True
        rec["move_echoed_uid"] = echoed
        rec["move_error_verbatim"] = merr
        rec["move_cost_s"] = round(time.time() - t0, 2)
        fact("[L2] MOVE #%d %r -> Diagram #%d [traverse %r] at %r; the op echoed uid %r (37(d): the echo is "
             "NOT the moved object) ; error %r (%.2f s)"
             % (MOVE_UID, MOVE_NAME, BODY_A_UID, dest, MOVE_POS, echoed, merr, rec["move_cost_s"]))
        es_mid = read_es("[L2] after the one move_in, before add_shift_reg", path)
        rec["exec_state_after_move"] = es_mid
        c_mid = counts(path, "[L2] AFTER THE MOVE")
        rec["counts_after_move"] = c_mid
        measure("[L2] the move LANDED (some count moved, or ExecState left 1 as 37(d) severing predicts)",
                es_mid != es_pre or c_mid != BASE, "ExecState %r -> %r ; counts %r" % (es_pre, es_mid, c_mid))

    rec.update(write_leg(2, "[L2]", path, LOOP_A_UID))
    return rec


# ====================================================================== LEG 3 - OPEN PANEL
def leg_3():
    print("\n========== LEG 3 - OPEN PANEL (authorised for this leg only), then add_shift_reg on #%d"
          % LOOP_A_UID, flush=True)
    rec = K.setdefault("leg3", {})
    path = make_scratch(3, "[L3]")
    rec["preparation"] = ("g.open_panel(target) - authorised by the brief for THIS LEG ONLY. No file is "
                          "replaced under a path LabVIEW has loaded, and nothing is saved; the panel is "
                          "closed again in this leg and the scratch is removed at [Y].")
    fact("[L3] %s" % rec["preparation"])
    t0 = time.time()
    _v, operr = safe("[L3] open_panel(scratch)", lambda: g.open_panel(path))
    rec["open_panel_error_verbatim"] = operr
    rec["open_panel_cost_s"] = round(time.time() - t0, 2)
    fact("[L3] open_panel returned in %.2f s ; error %r" % (rec["open_panel_cost_s"], operr))
    measure("[L3] open_panel returned without raising", not operr, "%r" % (operr,))

    rec.update(write_leg(3, "[L3]", path, LOOP_A_UID))

    _c, cerr = safe("[L3] close_panel(scratch)", lambda: g.close_panel(path))
    rec["close_panel_error_verbatim"] = cerr
    fact("[L3] close_panel error %r" % (cerr,))
    dump()
    return rec


# ====================================================================== LEG 4 - A DIFFERENT TARGET
def leg_4():
    print("\n========== LEG 4 - A DIFFERENT TARGET: D1_s2_loops.vi (md5 %s)" % S2_MD5[:8], flush=True)
    rec = K.setdefault("leg4", {})
    path = make_scratch(4, "[L4]")
    rec["bed"] = S2_ARTEFACT
    rec["bed_md5_pin"] = S2_MD5
    rec["preparation"] = "none - the same shape as L1, on a different VI"

    es0 = read_es("[L4] the scratch, COLD", path)
    rec["exec_state_cold"] = es0
    rows, rerr = safe("[L4] report_all('WhileLoop')", lambda: g.report_all(path, "WhileLoop"), [])
    rec["whileloop_rows"] = [{"i": r["i"], "uid": r["uid"], "pos": list(r["pos"]), "owner": r["owner"]}
                             for r in (rows or [])]
    rec["whileloop_census_error"] = rerr
    fact("[L4] report_all('WhileLoop') on %s: %d row(s) -> %r"
         % (os.path.basename(S2_ARTEFACT), len(rows or []),
            [(r["i"], r["uid"]) for r in (rows or [])]))
    if not rows:
        fact("[L4] this target carries NO While loop that report_all can see, so add_shift_reg was NOT "
             "called here. Reported as a fact; nothing is substituted and no other class is tried.")
        rec["called"] = False
        dump()
        return rec
    chosen = rows[0]
    rec["called"] = True
    rec["chosen_loop"] = {"i": chosen["i"], "uid": chosen["uid"], "pos": list(chosen["pos"])}
    fact("[L4] the loop chosen is report_all('WhileLoop')[0] = uid #%d at %r"
         % (chosen["uid"], list(chosen["pos"])))
    rec.update(write_leg(4, "[L4]", path, chosen["uid"]))
    return rec


def main():
    print("=== diag_c67_opvi  %s  (bgrun --material --max-min 35)" % STAMP, flush=True)
    print("=== PURE MEASUREMENT. NOTHING IS BUILT. NO DELIVERABLE .vi IS EDITED OR SAVED. NO ROUTE IS "
          "CHOSEN OR RECOMMENDED. NOTHING FOUND HERE IS REPAIRED.", flush=True)
    print("=== ONLY HYGIENE IS GATED. Leg outcomes print as `MEAS <name>: YES|NO` and never fail this run.",
          flush=True)
    try:
        phase_0()
        for n, fn in ((0, leg_0), (1, leg_1), (2, leg_2), (3, leg_3), (4, leg_4)):
            if left_s() < LEG_MIN_S:
                fact("LEG %d WAS NOT RUN: only %.0f s left before the reserve" % (n, left_s()))
                K.setdefault("leg%d" % n, {})["not_run"] = "wall-clock"
                continue
            try:
                fn()
            except Stop:
                raise
            except Exception as e:                                                 # noqa: BLE001
                msg = "%s: %s" % (type(e).__name__, str(e)[:500])
                K.setdefault("leg%d" % n, {})["unexpected_exception"] = msg
                fact("LEG %d UNEXPECTED EXCEPTION: %s" % (n, msg))
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        print("\n---------- [Y] HYGIENE: SCRATCHES, THE md5 PINS AFTER, THE REFS AND THE HANDLES",
              flush=True)
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
        for tag, opath in (("OpAddShiftReg_v0", OP_ADDSR), ("OpAddShiftRegF_v0", OP_ADDSRF)):
            if os.path.exists(opath):
                pr = probe("Y %s AFTER (it was READ, never edited or saved)" % tag, opath)
                # Compare the PARSED md5/size fields, never the raw HASH line: `probe()` returns a dict of
                # exists/size/md5/sha256 and the raw line carries the path and `exists=` as well. The first
                # run of this file (2026-09-21 19:38, rc=1) compared the raw tail against a two-field string
                # and failed BOTH gates while every md5 was in fact identical - a defect in the comparison,
                # not in the files.
                b = next((h for h in R["hash_probe"] if h["tag"] == "[L0] %s ON DISK" % tag), None)
                bf = dict(kv.strip().split("=", 1) for kv in b["line"].split(" | ")[1:]) if b else None
                same = bf is not None and bf.get("md5") == pr.get("md5") and bf.get("size") == pr.get("size")
                gate("Y %s is byte-unchanged by this run" % tag, same or bf is None,
                     "before md5 %r size %r ; after md5 %r size %r"
                     % ((bf or {}).get("md5"), (bf or {}).get("size"), pr.get("md5"), pr.get("size")))
                # T2 FROM archive/peer/2026-09-21-c67-opvi-hyg.md, IMPLEMENTED: the md5 gate above spans
                # process-start -> process-still-running and is STRUCTURALLY BLIND to the only ways LabVIEW
                # writes a loaded .vi (reference release, unload, editor quit) - all of which happen AFTER
                # this `finally` block, with 8 cached op-VI references still held. MTIME is strictly more
                # sensitive than md5 (it catches an identical-content rewrite) and costs a stat. The op VIs
                # were BUILT 2026-09-14, so their mtime must still read that day.
                mt = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(os.path.getmtime(opath)))
                R.setdefault("op_vi_mtime_after", {})[tag] = mt
                b0 = (K.get("leg0") or {}).get(tag, {}).get("mtime")
                gate("Y %s MTIME is unmoved AND still its 2026-09-14 build date (rule 1)" % tag,
                     mt.startswith("2026-09-14") and (b0 is None or mt == b0),
                     "at [L0d] %r ; now %r" % (b0, mt))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("Y refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        try:
            R["handles"]["delta"] = int(R["handles"]["after"]) - int(R["handles"]["before"])
        except Exception:                                                          # noqa: BLE001
            R["handles"]["delta"] = None
        fact("LabVIEW handles AFTER: %r (before %r, delta %r) - NO GObject census was run anywhere in this "
             "file" % (R["handles"]["after"], R["handles"].get("before"), R["handles"].get("delta")))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"]]
        R["files_left_on_disk"] = left
        print("\nTHE FILES THIS RUN LEFT ON DISK: %r" % (left,), flush=True)
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        gate("Y this run left NO file on disk (it is a reader)", not left, "%r" % (left,))
        dump()
        yes = [m["name"] for m in meas if m["outcome"]]
        no = [m["name"] for m in meas if not m["outcome"]]
        print("\n=== MEASUREMENTS: %d YES / %d NO  (these NEVER fail the run)" % (len(yes), len(no)),
              flush=True)
        for m in meas:
            print(("    %-4s %s  %s" % ("YES" if m["outcome"] else "NO", m["name"], m["detail"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
        print("\n=== HYGIENE GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
