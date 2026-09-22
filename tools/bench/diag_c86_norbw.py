r"""diag_c86_norbw.py - THE D-3b MEASUREMENT of M3a-3b Row D. A DIAGNOSTIC: it measures, decides nothing,
builds nothing, saves nothing.

    MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_c86_norbw.log \
        -- py -u tools/bench/diag_c86_norbw.py

WHY IT IS A DIAGNOSTIC AND NOT A RECIPE: `guard_cycle` refuses `tools/recipes/*.py` until this cycle's
retrospective lands; CLAUDE.md exempts diagnostics. Cycle 66's `tools/recipes/build_d1_m3a3b_d3b.py` is
ASTCHECK-clean and NEVER RAN (no `tools/bench/build_d1_m3a3b_d3b.log` exists); THIS FILE REUSES ITS CODE -
above all its mechanical Remove-Bad-Wires ban - and drops its STEP B (the landing) entirely. Nothing is
saved, no artefact is produced, no op is edited.

WHAT ALREADY EXISTS - CHECKED BY READING BEFORE A LINE WAS WRITTEN (CLAUDE.md "before creating any new op,
tool or recipe"; nothing new is built here - no op, no verb, no device, no third cell):
  * `tools/recipes/build_d1_m3a3b_d3.py` (c84)  - `fsit_call` (the parameterised connect-op driver, every
    readout poisoned), `fsit_read` (one `OpFsInnerTunnelTerm_v0` read of an FSIT's two faces).
  * `tools/recipes/build_opfsinnertunnelconnect_v0.py` (c82) - `md5`, `PINS`, `BED`/`BED_MD5`/`BED_BYTES`,
    `del_wire`, `resolve_triple`, `private_bytes`, every topology constant.
  * `tools/recipes/build_opconnectfromwire_v0.py` - `wire_source_owner` = the repaired, uid-echo-checked
    `OpWireSource_v5` driver (owner identity decides, never a count - Pre-decided 117 as corrected by 120).
  * `tools/bench/diag_c81_uidref.py` (c81) - `probe_ownerchain` = `OpOwnerChain_v1` (UID to GObject
    Reference -> self class / self uid / owner class / owner uid), the ONLY reader on disk that can say
    what `#23906` IS.
  * `tools/recipes/build_d1_m3a1.py` - `pd85_violations`, `print_walk`.
  * `tools/recipes/build_d1_m3a3b_d3b.py` (c66, never run) - the RBW guard rebind, copied verbatim in shape.
  Ops used AS THEY ARE ON DISK and never written: `OpFsInnerTunnelConnect_v1.vi` (md5 5b4e5f0f...),
  `OpFsInnerTunnelConnect_v0.vi` (50a1e58a...), `OpFsInnerTunnelTerm_v0.vi`, `OpWireSource_v5.vi`,
  `OpOwnerChain_v1.vi`.

THE BED IS `claudeDev\D1_s3b_m3a3_20260922_081056.vi`, md5 33ef524e..., 306,951 B. It is NEVER written,
NEVER opened for execution, NEVER run; its md5 is pinned at entry AND at exit and both values are printed.

REMOVE BAD WIRES IS FORBIDDEN ANYWHERE IN THIS RUN, mechanically: at import time `gscript.remove_bad_wires`
and `.remove_bad_wires_scripted` are REBOUND to a function that RAISES. The rebind is PROVEN IN FORCE by
gate RB1, which calls the name once inside try/except and passes ONLY on the raise. (`gscript` calls the
name internally at :586 and :2705 - both inside `try/except Exception`, in `report_all(purge=True)` and
`net_map`; neither is called here, and any trip is recorded and reported.)

THE PREDICTION CONTRACT - per cell, on its own dated scratch COPY of the bed, no cell touching another:
  M0 (before anything)  the FSIT #7468 resolves with its uid echoing back; its LeftTerm is #7488 carrying
       wire 7506; its RightTerm is #7471 carrying wire 7448; `#23906` resolves as an `OuterTerminal` owned
       by `RightShiftRegister #23868` and the loop-border row t1 is BARE; the Wire census holds w7506.
       `Wire.Is Broken?` on 7506: the literal 6371004 read is a WRITE verb on this fleet (an idempotent
       re-connect, `build_s0beta_replicate.read_is_broken:184`) and w7506's only sink is the FSIT LeftTerm,
       which is not node-addressable - so it is NOT MEASURED here and the READ-ONLY source-count verdict
       (>= 2 source terminals = broken, docs/NAMES.md:900) is reported in its place, labelled as such.
  M1   `del_wire(7506)` and NOTHING else. Expect: the census loses exactly w7506 and gains nothing.
  M2   THE c83 CONFOUND CONTROL. c83 concluded the delete makes #7468 unresolvable (`error 1055`) - but
       every c83 deleting cell called `remove_bad_wires_scripted` ONE LINE after `del_wire`
       (`diag_c83_connect2x2_r2.py:449-450`). With RBW banned: does #7468 STILL resolve, is #7488 still its
       LeftTerm, is #7488 now BARE, is #23906 still bare? RAW error strings printed, never a boolean.
  M3   the cell's op called ONCE. Raw Invoke `error out`, `term_uid`, `uid_back`, `UID 2`, wire census
       before/after and the delta, the wire uid now on #7488, the wire uid now on #23906, SAME uid or not.
  M4   `OpWireSource_v5` on the resulting net: every source terminal with owner class + uid, PD85
       violations, and `Wire.Is Broken?` from the op's OWN poisoned 6371004 readback in M3.
  Then the scratch is DELETED.

EXACTLY TWO CELLS, IN THIS ORDER, NO THIRD AND NOTHING IMPROVISED:
  A = `OpFsInnerTunnelConnect_v1.vi` (Invoke on the FSIT LeftTerm; the index-triple terminal is
      `Wire Source`), `Auto Route?` TRUE.
  B = `OpFsInnerTunnelConnect_v0.vi` (Invoke on the index-triple terminal; the FSIT LeftTerm is
      `Wire Source`). B RUNS EVEN IF A SUCCEEDS - it is the controlled comparison, and c82's arm 2 read B's
      polarity in a script that ALSO called Remove Bad Wires, so this is the first clean read of it.

PRE-DECIDED 125 IS MANDATORY AND IS IMPLEMENTED AS NAMED GATES: every uid resolution re-reads the returned
reference's OWN uid and asserts it equals the uid passed in BEFORE any value it produces is used or
believed (a never-allocated uid returns a history echo with every error column empty,
`diag_c81_uidref.log:85`).

NOTHING IS SAVED: no op edited, no artefact written, no scratch kept. The literal line
`THE FILES THIS RUN LEFT ON DISK: [...]` is printed and must be empty.
RIG STATE 조립: no motor, no ASI, no camera. VI Scripting and COM only.
VERIFICATION LEVEL: FUNCTIONAL (real reads and one real write verb per cell, into real copies of the bed,
decided by uid echoes and owner identity). No claim of legality is made about anything: nothing is kept.
"""
import glob
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
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles, restart_labview                            # noqa: E402
from build_opconnectnested_v1 import Stop                                          # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                      # noqa: E402
import build_d1_m3a3b_d3 as C84                                                    # noqa: E402
import diag_c81_uidref as C81                                                      # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "diag_c86_norbw.json")

md5 = C82.md5
OP1 = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelConnect_v1.vi")
OP1_MD5 = "5b4e5f0fb3baae96361c33ce81bcd7b1"
OP0 = C82.OP
OP0_MD5 = "50a1e58a4825c2ce030ed9a41e204931"
MAP1 = os.path.join(BENCH, "opfsinnertunnelconnect_v1_labels.json")
MAP0 = C82.MAP_OUT
OP_FSIT_READ = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
OP_OWNER = C81.OP_OWNER
LAB_OWNER = C81.LAB_OWNER
V5 = C82.V5

BED, BED_MD5, BED_BYTES = C82.BED, C82.BED_MD5, C82.BED_BYTES
PINS = C82.PINS

FSIT_UID = C82.FSIT_UID                 # 7468
LEFT_TERM = C82.LEFT_TERM_EXPECT        # 7488
RIGHT_TERM = 7471
RIGHT_WIRE = 7448
ROWD_WIRE = C82.ROWD_WIRE               # 7506 - deleted on each scratch, and nothing else is done to it
LOOP_NEW = C82.LOOP_NEW                 # 23032
LOOP_NODES_IDX = C82.LOOP_NODES_IDX     # 21
LOOP_TERM_IDX = C82.LOOP_TERM_IDX       # 1
TERM_UID_EXPECT = 23906                 # the NEW register's OUTER terminal (c81 D-1)
RSR_EXPECT = C82.RSR_EXPECT             # 23868
OLD_SOURCE = C82.OLD_SOURCE             # 4334

STAMP = time.strftime("%Y%m%d_%H%M%S")
CELLS = [("A", OP1, MAP1, "Auto Route? (F)", True),
         ("B", OP0, MAP0, "", None)]
SCRATCHES = []

RUN_DEADLINE_S = 21 * 60.0
RESERVE_S = 260.0
T0 = time.time()

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "bed": BED,
     "task": "D-3b MEASUREMENT: delete wire 7506 with NO Remove Bad Wires anywhere, then measure whether "
             "FlatSequenceInnerTunnel #7468 still resolves to a BARE LeftTerm #7488 and whether either "
             "polarity of the connect op creates a wire between two bare terminals",
     "verification_level": "FUNCTIONAL",
     "rbw_ban": "gscript.remove_bad_wires_scripted / .remove_bad_wires rebound to a raising guard",
     "cells": {}, "H": {}}


# ---------------------------------------------------------------- THE MECHANICAL RBW BAN
class RBWForbidden(RuntimeError):
    pass


_RBW_TRIPS = []


def _rbw_guard(*a, **k):                                                           # noqa: ANN001
    import traceback
    _RBW_TRIPS.append({"args": repr(a)[:160], "stack": traceback.format_stack()[-3:-1]})
    raise RBWForbidden(
        "Remove Bad Wires is FORBIDDEN in this dispatch (it is the suspected cause of c83's error 1055 and "
        "a rule-1a hazard, docs/cycle27-plan.md:1860-1862). Called with %r" % (a,))


g.remove_bad_wires_scripted = _rbw_guard
g.remove_bad_wires = _rbw_guard


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "**FAIL**", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def head(t):
    print("\n---------- %s" % t, flush=True)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


# the imported helpers report through THIS file's counters
C84.gate, C84.fact, C84.safe, C84.R = gate, fact, safe, R
C82.gate, C82.fact, C82.safe = gate, fact, safe
C81.fact = fact
M.fact = fact


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["rbw_guard_trips"] = _RBW_TRIPS
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


def census(target, tag):
    """The NON-MUTATING bracket: the Wire uid set, the count, whether w7506 is present, and ExecState."""
    wires, e1 = safe("%s Wire census" % tag, lambda: sorted(g.uids(target, "Wire")), [])
    es, e2 = safe("%s exec_state" % tag, lambda: g.exec_state(target))
    rec = {"n_wires": len(wires or []), "rowd_present": ROWD_WIRE in (wires or []), "exec_state": es,
           "err": (e1 + " " + e2).strip()}
    fact("%s WIRE CENSUS: %d Wire object(s) ; wire %d present %r ; ExecState %r"
         % (tag, rec["n_wires"], ROWD_WIRE, rec["rowd_present"], es))
    return set(wires or []), rec


def raw_read(tag, rd):
    """Print EVERY error column of a read_tunnel result VERBATIM - the brief asks for raw error strings."""
    if not rd:
        fact("%s read returned NOTHING (the driver raised; see the line above)" % tag)
        return
    fact("%s RAW: uid_in=%r uid_back=%r cls_back=%r cast=%r | LeftTerm #%r wire=%r | RightTerm #%r wire=%r "
         "| is_source=%r owner=%r#%r"
         % (tag, rd.get("uid_in"), rd.get("uid_back"), rd.get("cls_back"), rd.get("cast_class"),
            rd.get("term_a_uid"), rd.get("wire_a"), rd.get("term_b_uid"), rd.get("wire_b"),
            rd.get("is_source"), rd.get("ownercls"), rd.get("owner_uid")))
    fact("%s RAW ERROR COLUMNS: `error out`=%r err_a=%r err_b=%r err_bcw=%r others=%r"
         % (tag, rd.get("err"), rd.get("err_a"), rd.get("err_b"), rd.get("err_bcw"), rd.get("errs")))


def border_row(target, d_idx, tag):
    """The loop-border row t1 - the terminal whose uid is #23906 (owner RightShiftRegister #23868)."""
    (res, e) = safe("%s node_terms_uid(d=%r, n=%d)" % (tag, d_idx, LOOP_NODES_IDX),
                    lambda: g.node_terms_uid(target, d_idx, LOOP_NODES_IDX), (None, []))
    echo, trows = res if res else (None, [])
    row = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
    fact("%s BORDER Nodes[%d] uid echo %r (want the NEW loop #%d -> %s) ; t%d row = %r"
         % (tag, LOOP_NODES_IDX, echo, LOOP_NEW, "MATCH" if echo == LOOP_NEW else "MISMATCH",
            LOOP_TERM_IDX, row))
    return echo, row, e


def owner_probe(target, uid, tag):
    """`OpOwnerChain_v1` on a uid: self class / self uid ECHO / owner class / owner uid. Pre-decided 125."""
    if not (os.path.isfile(OP_OWNER) and os.path.isfile(LAB_OWNER)):
        fact("%s OpOwnerChain_v1 or its label map is NOT on disk - #%d cannot be identified" % (tag, uid))
        return None
    labs, _ = safe("%s load the owner label map" % tag,
                   lambda: json.load(open(LAB_OWNER, encoding="utf-8")), None)
    vio, _ = safe("%s g.op(OpOwnerChain_v1)" % tag, lambda: g.op(OP_OWNER))
    if not (labs and vio):
        return None
    o, _ = safe("%s probe_ownerchain(#%d)" % (tag, uid),
                lambda: C81.probe_ownerchain(vio, labs, target, uid, quiet=False), None)
    return o


# ======================================================================= [0] files only
def phase_files():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the pins, the five ops this run READS")
    got = md5(BED)
    R["bed_md5_before"] = got
    R["bed_bytes"] = os.path.getsize(BED)
    print("  BED MD5 AT ENTRY: %s  (%d bytes)" % (got, R["bed_bytes"]), flush=True)
    gate("H1 bed md5 before == %s (%d B)" % (BED_MD5, BED_BYTES),
         got == BED_MD5 and R["bed_bytes"] == BED_BYTES,
         "got %s, %d bytes" % (got, R["bed_bytes"]), fatal=True)
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    R["claudedev_before"] = sorted(os.path.basename(p)
                                   for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))
    for p, nm in ((OP1, "OpFsInnerTunnelConnect_v1.vi (CELL A's op - READ ONLY, never rebuilt)"),
                  (OP0, "OpFsInnerTunnelConnect_v0.vi (CELL B's op - READ ONLY, never rebuilt)"),
                  (OP_FSIT_READ, "OpFsInnerTunnelTerm_v0.vi (the FSIT face reader)"),
                  (V5, "OpWireSource_v5.vi (the identity reader)"),
                  (OP_OWNER, "OpOwnerChain_v1.vi (the uid identity probe)"),
                  (MAP1, "the v1 label map"), (MAP0, "the v0 label map")):
        gate("F0 %s on disk" % nm, os.path.isfile(p), p, fatal=True)
    R["op1_md5_before"] = md5(OP1)
    R["op0_md5_before"] = md5(OP0)
    gate("F0b cell A's op is the v1 cycle 84 saved (%s)" % OP1_MD5, R["op1_md5_before"] == OP1_MD5,
         "got %s (%d bytes)" % (R["op1_md5_before"], os.path.getsize(OP1)))
    gate("F0c cell B's op is the v0 cycle 83 saved (%s)" % OP0_MD5, R["op0_md5_before"] == OP0_MD5,
         "got %s (%d bytes)" % (R["op0_md5_before"], os.path.getsize(OP0)))


def phase_rbw_proof():
    head("[RB] PROVE THE REMOVE-BAD-WIRES REBIND IS IN FORCE - the name is called once and must RAISE")
    tripped = False
    try:
        g.remove_bad_wires_scripted("PROOF-CALL-NO-TARGET")
    except RBWForbidden as e:
        tripped = True
        fact("RB the guard raised as designed: %s" % str(e)[:150])
    except Exception as e:                                                         # noqa: BLE001
        fact("RB the call raised the WRONG exception: %s: %s" % (type(e).__name__, str(e)[:150]))
    gate("RB1 `gscript.remove_bad_wires_scripted` IS REBOUND to the raising guard (proof call)", tripped,
         "guard is %r" % (getattr(g, "remove_bad_wires_scripted", None),))
    tripped2 = False
    try:
        g.remove_bad_wires("PROOF-CALL-NO-TARGET")
    except RBWForbidden:
        tripped2 = True
    except Exception:                                                              # noqa: BLE001
        pass
    gate("RB2 `gscript.remove_bad_wires` (the GUI form) IS REBOUND to the raising guard", tripped2,
         "guard is %r" % (getattr(g, "remove_bad_wires", None),))
    # the two proof calls are DELIBERATE trips - they must not be counted against H7
    R["H"]["proof_trips"] = len(_RBW_TRIPS)
    del _RBW_TRIPS[:]
    fact("RB the two proof trips are cleared from the trip list; H7 counts only UNINTENDED trips")


def phase_restart():
    head("[1] RESTART LabVIEW (STATUS orders it before the first batch)")
    before, _ = safe("handles before restart", labview_handles)
    R["H"]["handles_before_restart"] = before
    fact("LabVIEW handle count BEFORE the restart: %r (baseline ~31,500)" % before)
    _, err = safe("restart_labview", restart_labview)
    R["H"]["restart_error"] = err
    g.reset()
    time.sleep(3.0)
    after, _ = safe("handles after restart", labview_handles)
    R["H"]["handles_after_restart"] = after
    fact("LabVIEW handle count AFTER the restart: %r" % after)


# ======================================================================= ONE CELL
def run_cell(tag, op_path, map_path, ar_label, auto_route):
    head("[%s] CELL %s - op %s, Auto Route? %r, on its OWN dated scratch COPY of the bed"
         % (tag, tag, os.path.basename(op_path), auto_route))
    rec = {"cell": tag, "op": os.path.basename(op_path), "auto_route": auto_route}
    R["cells"][tag] = rec
    scratch = os.path.join(g.CLAUDEDEV, "SCRATCH_c86_%s_%s.vi" % (tag, STAMP))
    rec["scratch"] = scratch
    SCRATCHES.append(scratch)
    shutil.copyfile(BED, scratch)
    time.sleep(0.4)
    gate("%s0 the scratch is a byte-identical copy of the bed" % tag, md5(scratch) == R["bed_md5_before"],
         os.path.basename(scratch), fatal=True)
    labels, e = safe("%s load %s" % (tag, os.path.basename(map_path)),
                     lambda: json.load(open(map_path, encoding="utf-8")), None)
    if not labels:
        gate("%s0b the label map loaded" % tag, False, e)
        return
    t = time.time()
    _, err = safe("%s ensure_loaded(scratch)" % tag, lambda: g.ensure_loaded(scratch))
    fact("%s ensure_loaded took %.1f s%s" % (tag, time.time() - t, ((" ERROR " + err) if err else "")))
    d_idx, trip = C82.resolve_triple(scratch, "%s " % tag)
    rec["triple"] = trip

    # ------------------------------------------------------------------ M0
    head("[%s/M0] BEFORE ANYTHING" % tag)
    wires0, br0 = census(scratch, "%s M0" % tag)
    rec["m0_bracket"] = br0
    gate("%sM0a wire %d is in the Wire census BEFORE the delete" % (tag, ROWD_WIRE), br0["rowd_present"],
         "%d Wire objects" % br0["n_wires"], fatal=True)
    rd0 = C84.fsit_read(scratch, FSIT_UID, "%s M0" % tag)
    rec["m0_fsit"] = rd0
    raw_read("%s M0 FSIT #%d" % (tag, FSIT_UID), rd0)
    gate("%sM0b THE UID ECHO (Pre-decided 125): the FSIT read's `uid_back` == %d" % (tag, FSIT_UID),
         bool(rd0) and rd0.get("uid_back") == FSIT_UID,
         "uid_back=%r cls_back=%r" % ((rd0 or {}).get("uid_back"), (rd0 or {}).get("cls_back")),
         fatal=True)
    gate("%sM0c its LeftTerm is #%d carrying wire %d, its RightTerm #%d carrying wire %d"
         % (tag, LEFT_TERM, ROWD_WIRE, RIGHT_TERM, RIGHT_WIRE),
         rd0.get("term_a_uid") == LEFT_TERM and rd0.get("wire_a") == ROWD_WIRE
         and rd0.get("term_b_uid") == RIGHT_TERM and rd0.get("wire_b") == RIGHT_WIRE,
         "LeftTerm #%r wire %r ; RightTerm #%r wire %r"
         % (rd0.get("term_a_uid"), rd0.get("wire_a"), rd0.get("term_b_uid"), rd0.get("wire_b")))
    echo0, brow0, _ = border_row(scratch, d_idx, "%s M0" % tag)
    rec["m0_border"] = brow0
    o0 = owner_probe(scratch, TERM_UID_EXPECT, "%s M0" % tag)
    rec["m0_term_probe"] = o0
    fact("%s M0 TERMINAL #%d: self %r#%r (echo %s) | owner %r#%r | err %r | the loop-border row t%d says "
         "name=%r is_source=%r wire=%r"
         % (tag, TERM_UID_EXPECT, (o0 or {}).get("cls_back"), (o0 or {}).get("uid_back"),
            "OK" if (o0 or {}).get("uid_echo_ok") else "MISMATCH", (o0 or {}).get("ownercls"),
            (o0 or {}).get("owner_uid"), (o0 or {}).get("err"), LOOP_TERM_IDX,
            (brow0 or {}).get("name"), (brow0 or {}).get("is_source"), (brow0 or {}).get("wire")))
    gate("%sM0d THE UID ECHO on #%d, and its owner is RightShiftRegister #%d (Pre-decided 120/125)"
         % (tag, TERM_UID_EXPECT, RSR_EXPECT),
         bool(o0) and o0.get("uid_echo_ok") and o0.get("owner_uid") == RSR_EXPECT,
         "echo_ok=%r owner=%r#%r" % ((o0 or {}).get("uid_echo_ok"), (o0 or {}).get("ownercls"),
                                     (o0 or {}).get("owner_uid")))
    gate("%sM0e the loop-border terminal is BARE before the connect" % tag,
         bool(brow0) and brow0.get("wire") == 0, "border t%d wire=%r" % (LOOP_TERM_IDX,
                                                                        (brow0 or {}).get("wire")))
    walk0, werr0 = safe("%s M0 OpWireSource_v5(w%d)" % (tag, ROWD_WIRE),
                        lambda: WIRE_TERMS(scratch, ROWD_WIRE, n=8), [])
    M.print_walk("%s M0 w%d" % (tag, ROWD_WIRE), ROWD_WIRE, walk0, werr0)
    src0 = sorted({(str(x.get("owner_class")), int(x.get("owner_uid"))) for x in (walk0 or [])
                   if x.get("is_source") and x.get("owner_uid")})
    all0 = sorted({(str(x.get("owner_class")), int(x.get("owner_uid"))) for x in (walk0 or [])
                   if x.get("owner_uid")})
    rec["m0_wire7506_walk"] = walk0
    rec["m0_wire7506_sources"] = src0
    fact("%s M0 `Wire.Is Broken?` ON WIRE %d IS **NOT MEASURED**: the only 6371004 route in this fleet is a "
         "WRITE verb (an idempotent re-connect, build_s0beta_replicate.py:184-212) and w%d's only SINK is "
         "the FSIT LeftTerm, which is not node-addressable - taking it would contaminate M1. THE READ-ONLY "
         "SUBSTITUTE (docs/NAMES.md:900, >=2 source terminals = broken): net %d has %d source terminal(s) "
         "%r ; every owner on the net %r -> read-only verdict %r"
         % (tag, ROWD_WIRE, ROWD_WIRE, ROWD_WIRE, len(src0), src0, all0,
            "BROKEN by the source count" if len(src0) >= 2 else "not broken by the source count"))

    # ------------------------------------------------------------------ M1
    head("[%s/M1] THE DELETE - `del_wire(%d)` AND NOTHING ELSE. No Remove Bad Wires, before or after."
         % (tag, ROWD_WIRE))
    deleted, e = safe("%s M1 del_wire(%d)" % (tag, ROWD_WIRE),
                      lambda: C82.del_wire(scratch, ROWD_WIRE, "%s M1 " % tag))
    rec["m1_deleted"] = bool(deleted)
    rec["m1_error"] = e
    gate("%sM1a wire %d was deleted" % (tag, ROWD_WIRE), bool(deleted) and not e,
         "returned %r ; error %r" % (deleted, e), fatal=True)
    wires1, br1 = census(scratch, "%s M1 AFTER the delete" % tag)
    rec["m1_bracket"] = br1
    lost = sorted(wires0 - wires1)
    gained = sorted(wires1 - wires0)
    rec["m1_lost"], rec["m1_gained"] = lost, gained
    fact("%s M1 CENSUS DIFF across the delete: lost %r ; gained %r ; count %d -> %d ; ExecState %r -> %r"
         % (tag, lost, gained, br0["n_wires"], br1["n_wires"], br0["exec_state"], br1["exec_state"]))
    gate("%sM1b the delete removed EXACTLY wire %d and created nothing" % (tag, ROWD_WIRE),
         lost == [ROWD_WIRE] and not gained, "lost %r gained %r" % (lost, gained))

    # ------------------------------------------------------------------ M2
    head("[%s/M2] THE c83 CONFOUND CONTROL: with NO Remove Bad Wires, does #%d STILL resolve?"
         % (tag, FSIT_UID))
    rd1 = C84.fsit_read(scratch, FSIT_UID, "%s M2" % tag)
    rec["m2_fsit"] = rd1
    raw_read("%s M2 FSIT #%d" % (tag, FSIT_UID), rd1)
    m2a = gate("%sM2a *** #%d STILL RESOLVES after the delete (uid echo `uid_back` == %d - never an empty "
               "error column)" % (tag, FSIT_UID, FSIT_UID),
               bool(rd1) and rd1.get("uid_back") == FSIT_UID,
               "uid_back=%r cls_back=%r ; raw `error out`=%r"
               % ((rd1 or {}).get("uid_back"), (rd1 or {}).get("cls_back"), (rd1 or {}).get("err")))
    m2b = gate("%sM2b its `Left Terminal` still comes back as #%d" % (tag, LEFT_TERM),
               bool(rd1) and rd1.get("term_a_uid") == LEFT_TERM,
               "term_a_uid=%r ; err_a=%r" % ((rd1 or {}).get("term_a_uid"), (rd1 or {}).get("err_a")))
    m2c = gate("%sM2c #%d is now BARE (wire 0)" % (tag, LEFT_TERM),
               bool(rd1) and rd1.get("wire_a") == 0,
               "wire_a=%r (was %r)" % ((rd1 or {}).get("wire_a"), rd0.get("wire_a")))
    gate("%sM2d the inner wire %d on the `Right Terminal` #%d SURVIVES the delete"
         % (tag, RIGHT_WIRE, RIGHT_TERM),
         bool(rd1) and rd1.get("term_b_uid") == RIGHT_TERM and rd1.get("wire_b") == RIGHT_WIRE,
         "term_b_uid=%r wire_b=%r ; err_b=%r"
         % ((rd1 or {}).get("term_b_uid"), (rd1 or {}).get("wire_b"), (rd1 or {}).get("err_b")))
    echo1, brow1, _ = border_row(scratch, d_idx, "%s M2" % tag)
    rec["m2_border"] = brow1
    o1 = owner_probe(scratch, TERM_UID_EXPECT, "%s M2" % tag)
    rec["m2_term_probe"] = o1
    gate("%sM2e #%d is BARE after the delete too (the source end)" % (tag, TERM_UID_EXPECT),
         bool(brow1) and brow1.get("wire") == 0,
         "border t%d wire=%r ; #%d echo %r owner %r#%r"
         % (LOOP_TERM_IDX, (brow1 or {}).get("wire"), TERM_UID_EXPECT, (o1 or {}).get("uid_back"),
            (o1 or {}).get("ownercls"), (o1 or {}).get("owner_uid")))
    rec["m2_answer"] = {"resolves": m2a, "left_terminal": m2b, "bare": m2c}

    # ------------------------------------------------------------------ M3
    head("[%s/M3] THE CALL - %s ONCE, Auto Route? %r, on the two BARE terminals"
         % (tag, os.path.basename(op_path), auto_route))
    wires2, br2 = census(scratch, "%s M3 BEFORE the call" % tag)
    r = C84.fsit_call(op_path, labels, scratch, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                      ar_label=ar_label, auto_route=auto_route,
                      inv_err_label=labels.get("err_invoke") or "error out 7")
    rec["m3_call"] = r
    fact("%s M3 RAW INVOKE `error out` = %r" % (tag, r.get("invoke_err")))
    fact("%s M3 op-level `error out` = %r" % (tag, r.get("err")))
    fact("%s M3 PER-STAGE ERROR COLUMNS: err_uidvi=%r err_fsit=%r err_termuid=%r err_uidback=%r"
         % (tag, r.get("err_uidvi"), r.get("err_fsit"), r.get("err_termuid"), r.get("err_uidback")))
    fact("%s M3 ECHOES AND OUTPUTS: term_uid=%r (want #%d) uid_back=%r (want #%d) `UID 2`=%r "
         "`Is Broken?`=%r `Name`=%r wire_delta=%r junk_Invoke_delta=%r"
         % (tag, r.get("term_uid"), LEFT_TERM, r.get("uid_back"), FSIT_UID, r.get("sink_wire_uid"),
            r.get("is_broken"), r.get("Name"), r.get("wire_delta"), r.get("invoke_delta")))
    gate("%sM3a THE UID ECHOES HOLD ON THE CALL (Pre-decided 125): `term_uid` == #%d AND `uid_back` == #%d"
         % (tag, LEFT_TERM, FSIT_UID),
         r.get("term_uid") == LEFT_TERM and r.get("uid_back") == FSIT_UID,
         "term_uid=%r uid_back=%r" % (r.get("term_uid"), r.get("uid_back")))
    wires3, br3 = census(scratch, "%s M3 AFTER the call" % tag)
    rec["m3_bracket_before"], rec["m3_bracket_after"] = br2, br3
    lost3 = sorted(wires2 - wires3)
    gained3 = sorted(wires3 - wires2)
    rec["m3_lost"], rec["m3_gained"] = lost3, gained3
    fact("%s M3 CENSUS DIFF across the call: lost %r ; gained %r ; count %d -> %d (op's own wire_delta %r) "
         "; ExecState %r -> %r"
         % (tag, lost3, gained3, br2["n_wires"], br3["n_wires"], r.get("wire_delta"),
            br2["exec_state"], br3["exec_state"]))
    rd2 = C84.fsit_read(scratch, FSIT_UID, "%s M3 AFTER" % tag)
    rec["m3_fsit_after"] = rd2
    raw_read("%s M3 AFTER FSIT #%d" % (tag, FSIT_UID), rd2)
    echo2, brow2, _ = border_row(scratch, d_idx, "%s M3 AFTER" % tag)
    rec["m3_border_after"] = brow2
    w_sink = (rd2 or {}).get("wire_a")
    w_src = (brow2 or {}).get("wire")
    rec["m3_wire_on_7488"], rec["m3_wire_on_23906"] = w_sink, w_src
    same = bool(w_sink) and bool(w_src) and w_sink == w_src
    rec["m3_same_wire"] = same
    fact("%s M3 *** THE WIRE ON #%d = %r ; THE WIRE ON #%d (border t%d) = %r ; SAME UID? %r ***"
         % (tag, LEFT_TERM, w_sink, TERM_UID_EXPECT, LOOP_TERM_IDX, w_src, same))
    gate("%sM3b a wire now joins the two terminals (the SAME uid on #%d and on #%d)"
         % (tag, LEFT_TERM, TERM_UID_EXPECT), same,
         "#%d carries %r ; #%d carries %r" % (LEFT_TERM, w_sink, TERM_UID_EXPECT, w_src))

    # ------------------------------------------------------------------ M4
    head("[%s/M4] `OpWireSource_v5` ON THE RESULTING NET" % tag)
    if not w_sink:
        rec["m4"] = "no wire on #%d - M4 is not applicable" % LEFT_TERM
        gate("%sM4a there is a net to walk" % tag, False,
             "#%d carries wire %r after the call" % (LEFT_TERM, w_sink))
    else:
        walk4, werr4 = safe("%s M4 OpWireSource_v5(w%r)" % (tag, w_sink),
                            lambda: WIRE_TERMS(scratch, int(w_sink), n=8), [])
        M.print_walk("%s M4 w%r" % (tag, w_sink), w_sink, walk4, werr4)
        bad4 = M.pd85_violations(w_sink, walk4)
        src4 = sorted({(str(x.get("owner_class")), int(x.get("owner_uid"))) for x in (walk4 or [])
                       if x.get("is_source") and x.get("owner_uid")})
        all4 = sorted({(str(x.get("owner_class")), int(x.get("owner_uid"))) for x in (walk4 or [])
                       if x.get("owner_uid")})
        rec["m4_walk"], rec["m4_sources"], rec["m4_owners"] = walk4, src4, len(bad4)
        rec["m4_pd85"] = bad4
        fact("%s M4 NET w%r: SOURCE terminals %r ; every owner %r ; PD85 violations %d %r"
             % (tag, w_sink, src4, all4, len(bad4), bad4))
        fact("%s M4 `Wire.Is Broken?` ON THAT WIRE = %r (the op's OWN 6371004 readback, poisoned True "
             "before the run; its `UID 2` = %r, the wire walked here = %r, same %r)"
             % (tag, r.get("is_broken"), r.get("sink_wire_uid"), w_sink,
                r.get("sink_wire_uid") == w_sink))
        gate("%sM4a exactly ONE source terminal on the net and its OWNER is RightShiftRegister #%d "
             "(Pre-decided 106/117-as-corrected-by-120)" % (tag, RSR_EXPECT),
             src4 == [("RightShiftRegister", RSR_EXPECT)],
             "source-terminal owners %r" % (src4,))
        gate("%sM4b the OLD source #%d is OFF that net" % (tag, OLD_SOURCE),
             bool(all4) and all(u != OLD_SOURCE for _c, u in all4), "every owner: %r" % (all4,))
        gate("%sM4c PD85 violations 0 on the walk" % tag, not bad4, "%d: %r" % (len(bad4), bad4))
        gate("%sM4d `Wire.Is Broken?` False on that wire AND the op's `UID 2` IS that wire" % tag,
             r.get("is_broken") is False and r.get("sink_wire_uid") == w_sink,
             "Is Broken? %r ; UID 2 %r vs wire %r" % (r.get("is_broken"), r.get("sink_wire_uid"), w_sink))

    # ------------------------------------------------------------------ delete the scratch
    head("[%s] DELETE THE SCRATCH - nothing from this cell is kept" % tag)
    safe("%s close_panel(scratch)" % tag, lambda: g.close_panel(scratch))
    time.sleep(1.0)
    for _a in range(3):
        try:
            if os.path.exists(scratch):
                os.remove(scratch)
            break
        except Exception as ex:                                                    # noqa: BLE001
            fact("%s delete attempt on %s failed: %s"
                 % (tag, os.path.basename(scratch), str(ex)[:120]))
            time.sleep(3.0)
    rec["scratch_deleted_in_cell"] = not os.path.exists(scratch)
    fact("%s scratch deleted in the cell: %r (hygiene retries after the restart if not)"
         % (tag, rec["scratch_deleted_in_cell"]))
    dump()


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close panels, delete every scratch, re-read every pin, handles at both ends")
    for p in SCRATCHES + [OP0, OP1, OP_FSIT_READ, V5, OP_OWNER]:
        safe("close_panel(%s)" % os.path.basename(p), lambda q=p: g.close_panel(q))
    R["H"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts (opened / closed / live / cached op VIs): %r" % R["H"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed, live 0)",
         R["H"]["ref_counts"].get("live") == 0, "%r" % R["H"]["ref_counts"])
    handles, _ = safe("handles after the work", labview_handles)
    R["H"]["handles_after_work"] = handles
    fact("LabVIEW handle count AFTER the work: %r" % handles)
    safe("restart_labview before the deletes", restart_labview)
    g.reset()
    time.sleep(2.0)
    for p in SCRATCHES:
        for _a in range(6):
            try:
                if os.path.exists(p):
                    os.remove(p)
                break
            except Exception as e:                                                 # noqa: BLE001
                fact("delete attempt on %s failed: %s" % (os.path.basename(p), str(e)[:120]))
                time.sleep(4.0)
        gate("H4 scratch deleted: %s" % os.path.basename(p), not os.path.exists(p), p)
    got = md5(BED)
    R["bed_md5_after"] = got
    print("  BED MD5 AT EXIT:  %s  (%d bytes)" % (got, os.path.getsize(BED)), flush=True)
    gate("H2 bed md5 UNCHANGED after the run", got == R.get("bed_md5_before"),
         "before %s / after %s" % (R.get("bed_md5_before"), got))
    allpins = True
    R["pins_after"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_after"][label] = have
        allpins = allpins and (have == want)
        fact("PIN AFTER  %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the five md5 pins all hold", allpins)
    R["op1_md5_after"] = md5(OP1) if os.path.isfile(OP1) else "MISSING"
    R["op0_md5_after"] = md5(OP0) if os.path.isfile(OP0) else "MISSING"
    gate("H3b OpFsInnerTunnelConnect_v1.vi md5 UNCHANGED (read only)",
         R["op1_md5_after"] == OP1_MD5, "%s" % R["op1_md5_after"])
    gate("H3c OpFsInnerTunnelConnect_v0.vi md5 UNCHANGED (read only)",
         R["op0_md5_after"] == OP0_MD5, "%s" % R["op0_md5_after"])
    gate("H7 the Remove-Bad-Wires ban held: the guard was never tripped UNINTENTIONALLY", not _RBW_TRIPS,
         "trips: %r" % (_RBW_TRIPS,))
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6a nothing was REMOVED from claudeDev", not gone, "removed %r" % (gone,))
    gate("H6b nothing was LEFT on disk by this run", not added, "added %r" % (added,))
    print("\n  THE FILES THIS RUN LEFT ON DISK: %r   (removed: %r)" % (added, gone), flush=True)
    facts.append("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("diag_c86_norbw - the D-3b MEASUREMENT: delete wire 7506 with NO Remove Bad Wires, then measure "
          "BOTH connect polarities on the two bare terminals. NOTHING IS SAVED.", flush=True)
    print("=" * 100, flush=True)
    try:
        phase_files()
        phase_rbw_proof()
        phase_restart()
        for tag, op_path, map_path, ar_label, auto_route in CELLS:
            if left_s() < 150:
                gate("%s CELL %s had time to run" % (tag, tag), False,
                     "%.0f s left of the deadline reserve" % left_s())
                continue
            try:
                run_cell(tag, op_path, map_path, ar_label, auto_route)
            except Stop as e:
                R["cells"].setdefault(tag, {})["stopped"] = str(e)
                gate("%s CELL %s ran to the end" % (tag, tag), False, "STOP at %s" % str(e)[:160])
            except Exception as e:                                                 # noqa: BLE001
                import traceback
                R["cells"].setdefault(tag, {})["fatal"] = traceback.format_exc()[-1500:]
                gate("%s CELL %s ran to the end" % (tag, tag), False,
                     "%s: %s" % (type(e).__name__, str(e)[:200]))
            dump()
    except Stop as e:
        gate("STOP at gate: %s" % e, False)
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        R["fatal"] = traceback.format_exc()[-2500:]
        print("\nOBSERVED EXC %s\n%s" % (str(e)[:300], traceback.format_exc()[-2000:]), flush=True)
        gate("the run completed without an unhandled exception", False, str(e)[:160])
    finally:
        try:
            phase_hygiene()
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            R["hygiene_fatal"] = traceback.format_exc()[-1500:]
            gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES: %d pass / %d fail%s"
          % (len(passes), len(fails), (("  FAILING: " + ", ".join(fails)) if fails else "")), flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
