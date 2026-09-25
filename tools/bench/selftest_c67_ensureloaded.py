"""selftest_c67_ensureloaded - does Part A's repair make `add_shift_reg` and `wire_sr` actually land?

A SELF-TEST under tools/bench/, never a recipe (48(n)). It builds no deliverable, saves no deliverable `.vi`,
chooses no route and repairs nothing beyond what cycle 67 material #4 Part A already changed in
`tools/gscript.py`.

WHAT WAS ALREADY THERE, CHECKED BEFORE WRITING THIS (the standing "check what exists first" rule)
  - `tools/gscript.py` carries every verb this file calls: `count`, `report_all`, `node_labels`,
    `node_terms_uid`, `exec_state`, `add_shift_reg`, `wire_sr`, `loop_cast`, `shift_reg_left`,
    `close_panel`, `ref_counts`, `op`. NOTHING NEW IS BUILT HERE.
  - `tools/recipes/build_d1_v0.py` owns `move_in` / `owner_of` / `diag_index`;
    `tools/recipes/build_opconnectnested_v1.py` owns `connect_nested_v1`. Cell 4 uses them UNCHANGED.
  - The scaffolding (gate/fact/measure, `probe`, `D.fresh`, the [Y] hygiene block) is
    `tools/bench/diag_c67_opvi.py`'s, re-used rather than re-invented.
  - `tools/bench/c60c_astcheck.py` is the static gate; it is NOT edited here.

THE MEASUREMENT THAT MOTIVATES IT (cycle 67 material #3, `tools/bench/diag_c67_opvi.log`)
  `g.add_shift_reg` on a target whose front panel had not been opened RAN, returned a uid, wrote an empty
  error cluster and CREATED NOTHING (legs L1 on the bed and L4 on `D1_s2_loops.vi`). With `g.open_panel`
  first it minted the register and took `ExecState` 1 -> 0 (L3); one prior `move_in`, whose body calls
  `g.ensure_loaded` (`tools/recipes/build_d1_v0.py:321`), had the same effect (L2). Part A therefore made
  `add_shift_reg` (`tools/gscript.py:708`) and `wire_sr` (`:750`) call `ensure_loaded(target)` themselves.

PREDICTION CONTRACT - four cells, each on its OWN fresh scratch, every scratch removed
  CELL 1  `add_shift_reg` with NO preparation on a scratch of the S3b row-2 BED, loop `#23032`.
          PASS = a `RightShiftRegister` uid is MINTED, `Tunnel` goes +2 (a register is a Left AND a Right,
          both Tunnel subclasses), `loop_cast(#23032).shift_reg_uids` is non-empty, and `ExecState` 1 -> 0.
          This is the exact call that was a no-op in dispatch #3's L1.
  CELL 2  the same on a scratch of `D1_s2_loops.vi` (dispatch #3's L4, also a no-op). Same criterion.
  CELL 3  `wire_sr` with NO preparation on a fresh BED scratch, loop `#637`: `add_shift_reg`, then ONE
          `wire_sr('RightIn', ...)` from a BARE SOURCE terminal of a body node read with `node_terms_uid`
          immediately before the call. PASS = ONE new `Wire` and the SAME non-zero wire uid at BOTH ends
          (the register's inside terminal via `shift_reg_left`, and the body terminal via `node_terms_uid`).
          `#637` is a SCRATCH here and is discarded; nothing about the deliverable route is decided by it.
  CELL 4  REGRESSION: one `move_in` and one `connect_nested_v1`, made exactly as
          `tools/bench/diag_c66b_s3b_m3.py` makes them, to show the patch broke nothing that worked.
          PASS = the moved object's owner reads back as the destination diagram AND `connect_nested_v1`
          returns its (wire delta, ExecState, error) triple without raising.

GATE RULE. Cell outcomes are MEAS/FACT lines and never fail the run; ONLY HYGIENE is gated (md5 pins before
and after, scratches gone, refs balanced, no file left on disk). Exit 0 when the hygiene gates pass.

ROUTE NOTE, WRITTEN DOWN RATHER THAN LAUNDERED. Cell 4 mandates a `move_in`, so this file's truthful static
route is `--route movein`; `--route owner` (the brief's parenthetical) FAILS gate 7 BY CONSTRUCTION on this
file. Both invocations are run and both logged; no gate file is edited and CYCLE_GUARD_OFF is never set.

VERIFICATION LEVEL: STRUCTURAL, never functional (34(f)). No VI is run. No motor / ASI / camera (rig
ASSEMBLED). No new op, no new verb, no new process device, no GUI, no `allow_broken`, no `gui_save`,
no `GObject` census anywhere (dispatch #3 measured ~10k handles per census).
"""
# REQUIRES: labview   (declaration read by verifiers, e.g. lint_verify_20260925b.py: skipped under a labview=none card)
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
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
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

LOOP_A_UID = 23032               # the While loop the no-op was measured on (diag_c67_opvi L1/L2/L3)
LOOP637_UID = 637                # the loop that already carries 14 registers, so a body terminal exists
BODY_A_UID = 23058               # #23032's body diagram (diag_c66b_s3b_m3.py:142)
MOVE_UID = 3529                  # diag_c66b_s3b_m3.py:184 SET[0]
MOVE_NAME = "- Inc (PgDn)"
MOVE_POS = (40, 60)
CONNECT_SINK_UID = 48            # diag_c66b_s3b_m3.py:201 INTERNAL_JOBS[0] sink
CONNECT_SINK_T = 0               # '-Inc reference'
CONNECT_SRC_T = 0                # the moved constant's own output

BODY_SCAN_LIMIT = 30             # node_terms is ~0.8 s per node; this bounds cell 3's search

RUN_DEADLINE_S = 25 * 60.0
RESERVE_S = 150.0
CELL_MIN_S = 130.0

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "selftest_c67_ensureloaded.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SCRATCH = {n: os.path.join(g.CLAUDEDEV, "WORK_C67SELF_C%d_%s.vi" % (n, STAMP)) for n in (1, 2, 3, 4)}
SCRATCH_BED = {1: BED, 2: S2_ARTEFACT, 3: BED, 4: BED}
SCRATCH_PIN = {1: BED_MD5, 2: S2_MD5, 3: BED_MD5, 4: BED_MD5}

T_START = time.time()
passes, fails, facts, meas = [], [], [], []
CELLS = {}
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 67 material #4 PART C: self-test of Part A's ensure_loaded repair in add_shift_reg "
             "and wire_sr, plus a move_in / connect_nested_v1 regression",
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gate_rule": "ONLY HYGIENE is gated; every cell outcome is a MEAS/FACT line",
     "no_gobject_census_anywhere": True,
     "nothing_is_built": True, "no_deliverable_vi_edited_or_saved": True,
     "chooses_no_route": True, "recommends_no_route": True,
     "repairs_nothing_beyond_part_a": True,
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "no_gui_action": True, "allow_broken": "NEVER True", "gui_save": "NEVER called",
     "remove_bad_wires_scripted": "not imported, not called",
     "no_vi_run": "no deliverable and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "measurements": [], "cells": CELLS}


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
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1)}
    R["exec_state_timeline"].append(row)
    fact("ExecState [%02d %s] = %r" % (row["step"], tag, es))
    return es


def counts(path, tag, classes=("Node", "Wire", "Tunnel")):
    """NARROW censuses only - `count` is ONE op run per class. NO `GObject` traverse anywhere in this file."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(path, cc))
    fact("%s counts: %r" % (tag, rec))
    return rec


def sr_uids(path, tag):
    """`LeftShiftRegister` 16442 / `RightShiftRegister` 16399 both derive from `Tunnel` (docs/NAMES.md:263-264),
    so these two narrow censuses are a creation detector without any whole-VI traverse."""
    out = {}
    for cls in ("RightShiftRegister", "LeftShiftRegister"):
        rows, err = safe("%s report_all(%r)" % (tag, cls), lambda c=cls: g.report_all(path, c), [])
        out[cls] = sorted(r["uid"] for r in (rows or []))
        out[cls + "_error"] = err
        fact("%s report_all(%r): %d row(s)%s" % (tag, cls, len(out[cls]), ("  [%s]" % err) if err else ""))
    return out


def sr_diff(tag, before, after):
    rec = {}
    for cls in ("RightShiftRegister", "LeftShiftRegister"):
        b, a = set(before.get(cls) or ()), set(after.get(cls) or ())
        rec[cls] = {"before": len(b), "after": len(a),
                    "minted": sorted(a - b), "vanished": sorted(b - a)}
        fact("%s %s: %d -> %d ; minted %r ; vanished %r"
             % (tag, cls, len(b), len(a), rec[cls]["minted"], rec[cls]["vanished"]))
    return rec


def loop_index_of(path, uid, tag, cls="WhileLoop"):
    """Resolve the loop's index in report_all(cls) FRESH and ECHO report_all(cls)[idx].uid == uid immediately
    before the call that takes a loop_index. An index is never carried across a call."""
    rows, err = safe("%s report_all(%r)" % (tag, cls), lambda: g.report_all(path, cls), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    fact("%s A7 ECHO: report_all(%r)[%r].uid == %r (want #%s; %d row(s)) %s"
         % (tag, cls, idx, echo, uid, len(rows or []), err))
    measure("%s the echoed uid at the index used IS #%s" % (tag, uid), echo == uid,
            "loop_index %r echoed %r" % (idx, echo))
    return idx


def make_scratch(n, tag):
    src, pin = SCRATCH_BED[n], SCRATCH_PIN[n]
    dest = SCRATCH[n]
    shutil.copy2(src, dest)
    pr = probe("%s the fresh scratch for CELL %d (from %s)" % (tag, n, os.path.basename(src)), dest)
    measure("%s CELL %d's scratch is byte-identical to its bed" % (tag, n), pr.get("md5") == pin,
            "%r vs pin %s" % (pr.get("md5"), pin[:8]))
    return dest


def cell_result(n, name, ok, detail):
    CELLS.setdefault("cell%d" % n, {})["verdict"] = bool(ok)
    CELLS["cell%d" % n]["criterion"] = name
    CELLS["cell%d" % n]["detail"] = detail
    measure("CELL %d %s" % (n, name), ok, detail)
    return bool(ok)


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


# ======================================================= THE add_shift_reg BLOCK, SHARED BY CELLS 1, 2 AND 3
def add_sr(n, tag, path, loop_uid):
    """ONE `add_shift_reg` with NO preparation whatsoever - no open_panel, no move_in, nothing. Before
    Part A this returned a uid, wrote no error and created nothing."""
    rec = CELLS.setdefault("cell%d" % n, {})
    rec["preparation"] = "NONE - no open_panel, no move_in; the repaired wrapper must load the target itself"
    fact("%s %s" % (tag, rec["preparation"]))
    es0 = read_es("%s the scratch, COLD before add_shift_reg" % tag, path)
    c0 = counts(path, "%s BEFORE" % tag)
    s0 = sr_uids(path, "%s BEFORE" % tag)
    idx = loop_index_of(path, loop_uid, "%s before add_shift_reg" % tag)
    rec.update({"exec_state_before": es0, "counts_before": c0, "loop_uid": loop_uid, "loop_index": idx})
    if idx is None:
        fact("%s the loop index was NOT resolvable, so add_shift_reg was NOT called" % tag)
        rec["called"] = False
        return rec, None, None
    t0 = time.time()
    uid, err = safe("%s add_shift_reg(index=%r)" % (tag, idx), lambda: g.add_shift_reg(path, idx))
    rec["called"] = True
    rec["returned_uid"] = uid
    rec["wrapper_error_verbatim"] = err
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("%s *** add_shift_reg(target, loop_index=%r) -> uid %r ; wrapper error %r (%.2f s) ***"
         % (tag, idx, uid, err, rec["call_cost_s"]))
    es1 = read_es("%s immediately after add_shift_reg" % tag, path)
    c1 = counts(path, "%s AFTER" % tag)
    s1 = sr_uids(path, "%s AFTER" % tag)
    diff = sr_diff(tag, s0, s1)
    lc, lcerr = safe("%s loop_cast(#%s)" % (tag, loop_uid), lambda: g.loop_cast(path, idx, class_name="WhileLoop"))
    srl = sorted(int(u) for u in (lc or {}).get("shift_reg_uids") or [])
    dt = (c1.get("Tunnel") or 0) - (c0.get("Tunnel") or 0)
    rec.update({"exec_state_after": es1, "counts_after": c1, "register_diff": diff,
                "tunnel_delta": dt, "loop_cast_shift_reg_uids": srl, "loop_cast_error": lcerr,
                "loop_cast_loop_uid_echo": (lc or {}).get("loop_uid")})
    fact("%s loop_cast(#%s): loop_uid echo %r ; shift_reg_uids %r ; errors %r"
         % (tag, loop_uid, (lc or {}).get("loop_uid"), srl, (lc or {}).get("errors")))
    minted = diff["RightShiftRegister"]["minted"]
    measure("%s a RightShiftRegister uid was MINTED" % tag, bool(minted), "%r" % (minted,))
    measure("%s Tunnel went +2 (a register is a Left AND a Right, both Tunnel subclasses)" % tag,
            dt == 2, "delta %r (before %r / after %r)" % (dt, c0.get("Tunnel"), c1.get("Tunnel")))
    measure("%s loop_cast(#%s).shift_reg_uids is non-empty" % (tag, loop_uid), bool(srl), "%r" % (srl,))
    measure("%s ExecState went 1 -> 0 as tools/gscript.py predicts for an unwired register" % tag,
            es0 == 1 and es1 == 0, "%r -> %r" % (es0, es1))
    rec["pass_parts"] = {"minted": bool(minted), "tunnel_plus_2": dt == 2,
                         "shift_reg_uids_non_empty": bool(srl), "exec_state_1_to_0": es0 == 1 and es1 == 0}
    dump()
    return rec, idx, (minted[0] if minted else None)


def cell_1():
    print("\n========== CELL 1 - `add_shift_reg`, NO PREPARATION, on the BED scratch, loop #%d" % LOOP_A_UID,
          flush=True)
    path = make_scratch(1, "[C1]")
    rec, _idx, _m = add_sr(1, "[C1]", path, LOOP_A_UID)
    p = rec.get("pass_parts") or {}
    cell_result(1, "add_shift_reg LANDS with no preparation on the bed (dispatch #3's L1 was a no-op)",
                bool(p) and all(p.values()), "%r" % (p,))


def cell_2():
    print("\n========== CELL 2 - the same on a DIFFERENT target: D1_s2_loops.vi (dispatch #3's L4)",
          flush=True)
    path = make_scratch(2, "[C2]")
    rows, rerr = safe("[C2] report_all('WhileLoop')", lambda: g.report_all(path, "WhileLoop"), [])
    fact("[C2] report_all('WhileLoop') on %s: %d row(s) -> %r"
         % (os.path.basename(S2_ARTEFACT), len(rows or []), [(r["i"], r["uid"]) for r in (rows or [])]))
    CELLS.setdefault("cell2", {})["whileloop_census_error"] = rerr
    if not rows:
        fact("[C2] this target carries NO While loop report_all can see; add_shift_reg was NOT called here")
        cell_result(2, "add_shift_reg LANDS with no preparation on D1_s2_loops.vi", False,
                    "no WhileLoop row; census error %r" % (rerr,))
        return
    chosen = rows[0]
    fact("[C2] the loop chosen is report_all('WhileLoop')[0] = uid #%d at %r"
         % (chosen["uid"], list(chosen["pos"])))
    rec, _idx, _m = add_sr(2, "[C2]", path, chosen["uid"])
    p = rec.get("pass_parts") or {}
    cell_result(2, "add_shift_reg LANDS with no preparation on D1_s2_loops.vi (dispatch #3's L4 was a no-op)",
                bool(p) and all(p.values()), "%r" % (p,))


# ============================================================================== CELL 3 - wire_sr, no prep
def body_diagram_of(path, loop_uid, tag):
    """The traverse index of `loop_uid`'s own body diagram, resolved on the machine: every Diagram whose
    report_all `owner` field reads as a While loop is asked `owner_of`, and the one owned by this loop wins.
    NO whole-VI GObject traverse; `owner` here is the owner's CLASS NAME (tools/gscript.py:488-518)."""
    rows, err = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    cand = [r for r in (rows or []) if str(r.get("owner")) == "WhileLoop"]
    fact("%s report_all('Diagram'): %d row(s), %d owned by a WhileLoop %s"
         % (tag, len(rows or []), len(cand), err))
    for r in cand:
        oc, ou = (None, None)
        got, oerr = safe("%s owner_of(Diagram #%s)" % (tag, r["uid"]),
                         lambda u=r["uid"]: owner_of(path, u))
        if got:
            oc, ou = got
        fact("%s Diagram #%s [traverse %s] owner_of -> %r #%r %s" % (tag, r["uid"], r["i"], oc, ou, oerr))
        if ou == loop_uid:
            return r["i"], r["uid"]
    return None, None


def find_bare_source(path, diagram_index, tag):
    """The first BARE SOURCE terminal (wire == 0, is_source True) on the diagram, scanning Nodes[] in order.
    BARE matters: `Terminal.Connect Wire` onto an already-wired source is a BRANCH, which creates NO new Wire
    object, and cell 3's criterion is a new wire."""
    labels, lerr = safe("%s node_labels(%r)" % (tag, diagram_index),
                        lambda: g.node_labels(path, diagram_index), [])
    n_nodes = len(labels or [])
    fact("%s the body diagram carries %d node(s) %s" % (tag, n_nodes, lerr))
    for n in range(min(n_nodes, BODY_SCAN_LIMIT)):
        nuid, rows = (None, [])
        got, gerr = safe("%s node_terms_uid(d=%r, n=%d)" % (tag, diagram_index, n),
                         lambda nn=n: g.node_terms_uid(path, diagram_index, nn))
        if got:
            nuid, rows = got
        bare = [r for r in (rows or []) if r.get("is_source") and not r.get("wire")]
        if bare:
            r0 = bare[0]
            fact("%s Nodes[%d] (#%r) offers BARE SOURCE terminal t%d %r (of %d terminals)"
                 % (tag, n, nuid, r0["i"], r0["name"], len(rows)))
            return n, r0["i"], nuid, r0["name"]
    return None, None, None, None


def cell_3():
    print("\n========== CELL 3 - `wire_sr`, NO PREPARATION, on a fresh BED scratch, loop #%d" % LOOP637_UID,
          flush=True)
    rec = CELLS.setdefault("cell3", {})
    path = make_scratch(3, "[C3]")
    _r, idx, minted = add_sr(3, "[C3]", path, LOOP637_UID)
    if idx is None or minted is None:
        cell_result(3, "wire_sr LANDS with no preparation", False,
                    "the register was not created, so wire_sr was not attempted (idx %r minted %r)"
                    % (idx, minted))
        return
    lc, lcerr = safe("[C3] loop_cast(#%d) for the register index" % LOOP637_UID,
                     lambda: g.loop_cast(path, idx, class_name="WhileLoop"))
    srl = [int(u) for u in (lc or {}).get("shift_reg_uids") or []]
    reg_index = srl.index(minted) if minted in srl else None
    rec.update({"minted_register_uid": minted, "shift_reg_uids": srl, "reg_index": reg_index,
                "loop_cast_error": lcerr})
    fact("[C3] the minted register #%r sits at Loop.Shift Registers[%r] of %d" % (minted, reg_index, len(srl)))
    measure("[C3] the minted register uid is addressable as a reg_index", reg_index is not None,
            "minted %r in %r" % (minted, srl))
    if reg_index is None:
        cell_result(3, "wire_sr LANDS with no preparation", False, "no reg_index for the minted register")
        return

    bidx, buid = body_diagram_of(path, LOOP637_UID, "[C3]")
    rec.update({"body_diagram_index": bidx, "body_diagram_uid": buid})
    if bidx is None:
        cell_result(3, "wire_sr LANDS with no preparation", False,
                    "loop #%d's body diagram was not resolvable" % LOOP637_UID)
        return
    n_idx, t_idx, n_uid, t_name = find_bare_source(path, bidx, "[C3]")
    rec.update({"src_node_index": n_idx, "src_term_index": t_idx, "src_node_uid": n_uid,
                "src_term_name": t_name})
    if n_idx is None:
        cell_result(3, "wire_sr LANDS with no preparation", False,
                    "no BARE SOURCE terminal in the first %d body nodes; wire_sr was NOT attempted"
                    % BODY_SCAN_LIMIT)
        return

    w0 = counts(path, "[C3] BEFORE wire_sr", classes=("Wire",))
    t0 = time.time()
    _x, werr = safe("[C3] wire_sr('RightIn', reg_index=%r, node_index=%r, term_index=%r)"
                    % (reg_index, n_idx, t_idx),
                    lambda: g.wire_sr("RightIn", path, idx, reg_index, node_index=n_idx, term_index=t_idx))
    rec["wire_sr_error_verbatim"] = werr
    rec["wire_sr_cost_s"] = round(time.time() - t0, 2)
    fact("[C3] *** wire_sr('RightIn', target, loop_index=%r, reg_index=%r, node_index=%r, term_index=%r) "
         "-> error %r (%.2f s) ***" % (idx, reg_index, n_idx, t_idx, werr, rec["wire_sr_cost_s"]))
    w1 = counts(path, "[C3] AFTER wire_sr", classes=("Wire",))
    dw = (w1.get("Wire") or 0) - (w0.get("Wire") or 0)
    rec["wire_delta"] = dw

    srd, serr = safe("[C3] shift_reg_left(reg_index=%r)" % reg_index,
                     lambda: g.shift_reg_left(path, idx, reg_index, class_name="WhileLoop"))
    inside = [(r.get("name"), r.get("is_source"), r.get("wire")) for r in ((srd or {}).get("inside") or [])]
    reg_wires = sorted({int(w) for _n, _s, w in inside if w})
    rec.update({"register_inside_terminals": inside, "register_inside_wires": reg_wires,
                "shift_reg_left_error": serr})
    fact("[C3] shift_reg_left(reg %r) inside terminals: %r" % (reg_index, inside))

    back, berr = safe("[C3] node_terms_uid readback of the body source terminal",
                      lambda: g.node_terms_uid(path, bidx, n_idx))
    brows = (back or (None, []))[1]
    trow = next((r for r in (brows or []) if r["i"] == t_idx), None)
    term_wire = int((trow or {}).get("wire") or 0)
    rec.update({"source_terminal_wire_after": term_wire, "readback_error": berr,
                "source_terminal_row_after": trow})
    fact("[C3] the body source terminal t%r %r now carries wire %r" % (t_idx, t_name, term_wire))

    same = bool(term_wire) and term_wire in reg_wires
    measure("[C3] exactly ONE new Wire object", dw == 1, "delta %r" % (dw,))
    measure("[C3] the SAME non-zero wire uid at BOTH ends (register inside terminal and body terminal)",
            same, "terminal wire %r ; register inside wires %r" % (term_wire, reg_wires))
    cell_result(3, "wire_sr LANDS with no preparation (one new wire, same uid at both ends)",
                dw == 1 and same, "wire_delta %r ; terminal wire %r ; register wires %r"
                % (dw, term_wire, reg_wires))
    dump()


# ================================================================ CELL 4 - REGRESSION: move_in + connect_v1
def cell_4():
    print("\n========== CELL 4 - REGRESSION: one move_in and one connect_nested_v1, unchanged from "
          "diag_c66b_s3b_m3.py", flush=True)
    rec = CELLS.setdefault("cell4", {})
    path = make_scratch(4, "[C4]")
    es0 = read_es("[C4] the scratch, COLD", path)
    rec["exec_state_cold"] = es0

    dest, derr = safe("[C4] diag_index(Diagram #%d)" % BODY_A_UID, lambda: diag_index(path, BODY_A_UID))
    rec.update({"dest_diagram_uid": BODY_A_UID, "dest_index_resolved": dest, "dest_error": derr})
    fact("[C4] DESTINDEX: Diagram #%d -> traverse index %r %s" % (BODY_A_UID, dest, derr))
    if dest is None:
        cell_result(4, "the move_in / connect_nested_v1 regression", False,
                    "the destination diagram was not resolvable: %r" % (derr,))
        return
    t0 = time.time()
    echoed, merr = safe("[C4] move_in(#%d -> Diagram #%d at %r)" % (MOVE_UID, BODY_A_UID, MOVE_POS),
                        lambda: move_in(path, MOVE_UID, dest, MOVE_POS))
    rec.update({"move_echoed_uid": echoed, "move_error_verbatim": merr,
                "move_cost_s": round(time.time() - t0, 2)})
    fact("[C4] MOVE #%d %r -> Diagram #%d [traverse %r]; the op echoed uid %r (37(d): the echo is NOT the "
         "moved object) ; error %r" % (MOVE_UID, MOVE_NAME, BODY_A_UID, dest, echoed, merr))
    got, oerr = safe("[C4] owner_of(#%d) after the move" % MOVE_UID, lambda: owner_of(path, MOVE_UID))
    oc, ou = got if got else (None, None)
    rec.update({"moved_owner_class": oc, "moved_owner_uid": ou, "owner_error": oerr})
    fact("[C4] owner_of(#%d) reads %r #%r (want the destination diagram #%d)"
         % (MOVE_UID, oc, ou, BODY_A_UID))
    move_ok = ou == BODY_A_UID
    measure("[C4] the moved object's owner IS the destination diagram", move_ok, "%r #%r" % (oc, ou))
    read_es("[C4] after the one move_in (37(d): a move SEVERS every wire on the object)", path)

    # the connect: the INTERNAL_JOBS[0] row of diag_c66b_s3b_m3.py:201, addressed across the two diagrams
    # the two endpoints actually live on right now (this cell moves ONE object, not seven).
    sgot, serr = safe("[C4] owner_of(#%d) - the sink's diagram" % CONNECT_SINK_UID,
                      lambda: owner_of(path, CONNECT_SINK_UID))
    sink_owner = sgot[1] if sgot else None
    sink_diag, sderr = safe("[C4] diag_index(sink diagram #%r)" % sink_owner,
                            lambda: diag_index(path, sink_owner) if sink_owner else None)
    sink_n, snerr = safe("[C4] node index of #%d on its diagram" % CONNECT_SINK_UID,
                         lambda: [r["uid"] for r in g.node_labels(path, sink_diag)].index(CONNECT_SINK_UID)
                         if sink_diag is not None else None)
    src_n, srerr = safe("[C4] node index of #%d on Diagram #%d" % (MOVE_UID, BODY_A_UID),
                        lambda: [r["uid"] for r in g.node_labels(path, dest)].index(MOVE_UID))
    rec.update({"sink_owner_uid": sink_owner, "sink_diag_index": sink_diag, "sink_node_index": sink_n,
                "src_diag_index": dest, "src_node_index": src_n,
                "index_errors": [serr, sderr, snerr, srerr]})
    fact("[C4] the row: sink #%d = Diagram[%r].Nodes[%r].Terminals[%d]  <-  source #%d = "
         "Diagram[%r].Nodes[%r].Terminals[%d]"
         % (CONNECT_SINK_UID, sink_diag, sink_n, CONNECT_SINK_T, MOVE_UID, dest, src_n, CONNECT_SRC_T))
    if sink_diag is None or sink_n is None or src_n is None:
        cell_result(4, "the move_in / connect_nested_v1 regression", False,
                    "an endpoint index was not resolvable: %r" % (rec["index_errors"],))
        return
    w0 = counts(path, "[C4] BEFORE connect_nested_v1", classes=("Wire",))
    trip, cerr = safe("[C4] connect_nested_v1(...)",
                      lambda: CONNECT_V1(path, sink_diag, sink_n, CONNECT_SINK_T,
                                         dest, src_n, CONNECT_SRC_T, V1_LABELS))
    rec["connect_returned"] = list(trip) if trip else None
    rec["connect_exception_verbatim"] = cerr
    fact("[C4] *** connect_nested_v1 -> %r ; exception %r ***" % (trip, cerr))
    w1 = counts(path, "[C4] AFTER connect_nested_v1", classes=("Wire",))
    rec["wire_delta_measured"] = (w1.get("Wire") or 0) - (w0.get("Wire") or 0)
    fact("[C4] whole-VI Wire delta across the connect: %r" % (rec["wire_delta_measured"],))
    conn_ok = trip is not None and not cerr
    measure("[C4] connect_nested_v1 returned its triple without raising", conn_ok,
            "%r ; exception %r" % (trip, cerr))
    cell_result(4, "the move_in / connect_nested_v1 regression - both verbs still behave as before Part A",
                move_ok and conn_ok, "move_owner #%r ; connect %r" % (ou, trip))
    dump()


def main():
    print("=== selftest_c67_ensureloaded  %s  (bgrun --material --max-min 25)" % STAMP, flush=True)
    print("=== A SELF-TEST, NEVER A RECIPE. NOTHING IS BUILT. NO DELIVERABLE .vi IS EDITED OR SAVED. "
          "NO ROUTE IS CHOSEN OR RECOMMENDED.", flush=True)
    print("=== ONLY HYGIENE IS GATED. Cell outcomes print as `MEAS ...: YES|NO` and never fail this run.",
          flush=True)
    try:
        phase_0()
        for n, fn in ((1, cell_1), (2, cell_2), (3, cell_3), (4, cell_4)):
            if left_s() < CELL_MIN_S:
                fact("CELL %d WAS NOT RUN: only %.0f s left before the reserve" % (n, left_s()))
                CELLS.setdefault("cell%d" % n, {})["not_run"] = "wall-clock"
                continue
            try:
                fn()
            except Stop:
                raise
            except Exception as e:                                                 # noqa: BLE001
                msg = "%s: %s" % (type(e).__name__, str(e)[:500])
                CELLS.setdefault("cell%d" % n, {})["unexpected_exception"] = msg
                fact("CELL %d UNEXPECTED EXCEPTION: %s" % (n, msg))
    except Stop as e:
        fact("STOP: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        R["unexpected_exception"] = "%s: %s" % (type(e).__name__, str(e)[:600])
        fact("UNEXPECTED EXCEPTION: %s" % R["unexpected_exception"])
    finally:
        print("\n---------- [Y] HYGIENE: SCRATCHES, THE md5 PINS AFTER, THE REFS AND THE HANDLES", flush=True)
        for n, p in sorted(SCRATCH.items()):
            safe("close_panel(CELL %d scratch)" % n, lambda pp=p: g.close_panel(pp))
            if os.path.exists(p):
                safe("remove CELL %d's scratch" % n, lambda pp=p: os.remove(pp))
            gate("Y CELL %d's scratch %s is gone (exists=False)" % (n, os.path.basename(p)),
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
        try:
            R["handles"]["delta"] = int(R["handles"]["after"]) - int(R["handles"]["before"])
        except Exception:                                                          # noqa: BLE001
            R["handles"]["delta"] = None
        fact("LabVIEW handles AFTER: %r (before %r, delta %r) - NO GObject census was run anywhere in this "
             "file" % (R["handles"]["after"], R["handles"].get("before"), R["handles"].get("delta")))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size")) for a in R["artefacts_on_disk"]]
        R["files_left_on_disk"] = left
        print("\nTHE FILES THIS RUN LEFT ON DISK: %r" % (left,), flush=True)
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        gate("Y this run left NO file on disk", not left, "%r" % (left,))
        ok = sum(1 for k in sorted(CELLS) if (CELLS[k] or {}).get("verdict"))
        tot = 4
        R["selftest"] = {"pass": ok, "total": tot,
                         "verdicts": {k: (CELLS[k] or {}).get("verdict") for k in sorted(CELLS)}}
        dump()
        yes = [m["name"] for m in meas if m["outcome"]]
        no = [m["name"] for m in meas if not m["outcome"]]
        print("\n=== MEASUREMENTS: %d YES / %d NO  (these NEVER fail the run)" % (len(yes), len(no)),
              flush=True)
        for m in meas:
            print(("    %-4s %s  %s" % ("YES" if m["outcome"] else "NO", m["name"], m["detail"]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
        print("\n=== SELFTEST %d/%d cells" % (ok, tot), flush=True)
        print("=== HYGIENE GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
        print("=== JSON: %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
