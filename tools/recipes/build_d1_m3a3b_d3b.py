r"""build_d1_m3a3b_d3b.py - D-3b of M3a-3b: REMOVE THE c83 CONFOUND, then land Row D if it is removed.

    MATERIAL=1 py tools/bgrun.py --max-min 45 --log tools/bench/build_d1_m3a3b_d3b.log \
        -- py -u tools/recipes/build_d1_m3a3b_d3b.py

WHAT IS SETTLED AND IS NOT RE-TESTED HERE (c84, measured 4/4 + a REFUTED review):
  * `Terminal.Connect Wire` 6349C03 MERGES nets - a terminal holds at most one wire, so connecting to a
    WIRED net always yields a multi-source net, in every role and `Auto Route?` combination
    (`tools/bench/build_d1_m3a3b_d3.log`, GATE S (a) FAIL / (b) FAIL / (d1) FAIL in BOTH cells;
    `archive/peer/2026-09-22-c84-replace-vs-branch.md` §2). Connect-with-the-wire-alive is DEAD for Row D.
  * Connecting TWO BARE terminals CREATES a wire (c83's trivial-VI cells, 4/4,
    `tools/bench/diag_c83_connect2x2_r2.log`).

THE CONFOUND THIS FILE REMOVES. c83 concluded that deleting wire 7506 makes FSIT `#7468` unresolvable
(`error 1055`). But every c83 deleting cell called `remove_bad_wires_scripted` ONE LINE after `del_wire`
(`tools/bench/diag_c83_connect2x2_r2.py:449-450`), and c82's own end-to-end arm did the same
(`tools/recipes/build_opfsinnertunnelconnect_v0.py:775`). Remove Bad Wires is on record DELETING A TUNNEL
(`archive/2026-09-17-status-d1-route-b-2.md:44-46`) and is refused as a rule-1a hazard
(`docs/cycle27-plan.md:1860-1862`). "GONE" and "UNRESOLVABLE" are different findings with the same symptom.

🔴 REMOVE BAD WIRES IS FORBIDDEN ANYWHERE IN THIS RUN, on the scratch copies and on the artefact alike.
   ENFORCED MECHANICALLY, not by discipline: at import time this file REBINDS
   `gscript.remove_bad_wires_scripted` and `gscript.remove_bad_wires` to a function that RAISES, so no
   imported helper can reach them behind my back (the helpers that DO call them -
   `build_d1_m3a3b_d3.bad_wire_count`, `.baseline_bad_wires`, `.build_v1`, `.step3`, `.phase_hygiene`,
   `build_opfsinnertunnelconnect_v0.gate4` - are never called; `del_wire`, `resolve_triple`, `purge_junk`,
   `read_tunnel` and `wire_source_owner` were READ and none of them calls it).

⚠️ ONE CONSEQUENCE OF THAT BAN, STATED UP FRONT AND REPORTED AS A FACT, NOT ARGUED AWAY: the brief's GATE
   S(d2) - "the diagram-wide broken-wire count is not higher than the pre-delete baseline" - HAS NO
   NON-MUTATING READER IN THIS FLEET. The only construction on disk is the Remove-Bad-Wires count delta
   (`tools/bench/broken_probe2.py:12`), which this dispatch forbids, and a per-wire `Wire.Is Broken?`
   6371004 walk is impossible twice over: no standalone reader op exists (`docs/toolkit-capabilities.md:68`
   - "the sound reader ... is NOT BUILT") and READING `Is Broken?` PERTURBS THE TARGET
   (`docs/NAMES.md:984-995`), on 1,9xx wires. So d2 is reported as **NOT MEASURED** and a strictly
   non-mutating substitute d2' is gated instead: the Wire-uid CENSUS (nothing vanished but w7506, nothing
   appeared but the one new wire) and `ExecState` non-regression on the same copy. d2' is WEAKER than d2
   and is labelled so everywhere it appears; it is not presented as the brief's gate.

WHAT ALREADY EXISTS - checked by READING before a line was written (CLAUDE.md "before creating any new op,
tool or recipe"; nothing new is built here - no op, no verb, no device, no third configuration):
  * `tools/recipes/build_d1_m3a3b_d3.py` (C84) - `fsit_call`, `fsit_read`, `gate_s`, `safe`. IMPORTED and
    its module-level `gate`/`fact`/`R` REBOUND to this file's, so its gates count here. `gate_s` is called
    only with `probe_bad=False`, the branch that never touches Remove Bad Wires.
  * `tools/recipes/build_opfsinnertunnelconnect_v0.py` (C82) - `md5`, `PINS`, `BED`/`BED_MD5`/`BED_BYTES`,
    `del_wire`, `purge_junk`, `resolve_triple`, `private_bytes`, every topology constant.
  * `tools/recipes/build_opfstunnelterm_v2.py:745` `read_tunnel` + `tools/bench/opfsinnertunnelterm_labels.json`
    - the only caller shape for `OpFsInnerTunnelTerm_v0`.
  * `tools/recipes/build_opconnectfromwire_v0.py` `wire_source_owner` - the repaired, uid-echo-checked
    `OpWireSource_v5` driver (owner identity decides, never a count - Pre-decided 117 as corrected by 120).
  * `tools/recipes/build_d1_m3a1.py` - `print_walk`, `pd85_violations`, `node_census`, `new_nodes`,
    `node_view`, `delete_by_uid`.
  * `claudeDev\OpFsInnerTunnelConnect_v1.vi` md5 5b4e5f0fb3baae96361c33ce81bcd7b1 - BUILT LAST CYCLE, used
    as-is, never rebuilt and never modified. `_v0.vi` md5 50a1e58a... is the fallback and is also never
    modified.

DOES THE READER PROPAGATE ITS OWN ERRORS? ANSWERED IN WRITING AND RE-MEASURED IN THIS RUN. c83 proved
`OpFsInnerTunnelConnect_v0`'s error indicator was UNWIRED, so an empty error column meant nothing. The
reader used here, `OpFsInnerTunnelTerm_v0` driven by `read_tunnel`, is a DIFFERENT VI and reads TWELVE
error columns per call (`error out`, `err_a`=`error out 11`, `err_b`=`error out 12`, `err_bcw`=`error out
13`, plus errL/errT/errO/errU/errG/errS/errWU/errCO). That is a claim about the label map, not about the
wiring, so it is NOT trusted: gate A7 runs c81's NEGATIVE CONTROL on this very copy - `read_tunnel` on a
never-allocated uid (999983) must come back with `uid_back != 999983` - and every gate below is decided by
the UID ECHO (`uid_back` == 7468, `term_a_uid` == 7488), never by an empty error column (Pre-decided 125).

STEP A - THE MEASUREMENT (a dated scratch COPY of the bed; NO Remove Bad Wires anywhere):
  A0   the copy is byte-identical to the bed; wire 7506 is in the Wire census; the FSIT reads
       LeftTerm #7488 wire 7506 / RightTerm #7471 wire 7448 with the uid echo 7468.
  A1   `del_wire(7506)` - and NOTHING else.
  A2   w7506 is gone from the Wire census; the total Wire count fell by exactly 1.
  A3   ⭐ THE QUESTION: does `#7468` still RESOLVE after the delete? (uid echo `uid_back` == 7468)
  A4   does its `Left Terminal` come back as `#7488`?
  A5   is that terminal BARE (wire 0)?
  A6   does the inner wire 7448 on the `Right Terminal` `#7471` survive?
  A7   the negative control: an unallocated uid is caught by the echo, on these same bytes.
  Raw error columns are printed verbatim for BOTH reads whatever the outcome, together with the Wire
  census counts and `ExecState` before and after the delete (the brief's "broken-wire count" as far as a
  non-mutating reader can take it - see the d2 note above).

STEP B - THE LANDING, the ONLY branch in this file. Taken ONLY if A3 AND A4 AND A5 pass.
  B1   on the SAME post-delete scratch, connect the NEW loop's shift-register OUTER terminal
       (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, uid `#23906`, owner `RightShiftRegister #23868`)
       into the now-BARE `#7488` with `OpFsInnerTunnelConnect_v1.vi` (the Invoke on the SINK, the true
       source passed as `Wire Source`). If v1 raises a REAL error it is recorded verbatim and
       `OpFsInnerTunnelConnect_v0.vi` is tried ONCE; both raw errors are reported.
  GATE S on the scratch: (a) the FSIT LeftTerm's net has EXACTLY ONE source terminal whose OWNER is
       `RightShiftRegister #23868`; (b) `#4334` is OFF that net; (c) PD85 violations 0; (d1)
       `Wire.Is Broken?` False on that wire and the op's `UID 2` IS that wire; (d2) NOT MEASURED, d2'
       instead; (e) the FSIT `Right Terminal` `#7471` still carries wire 7448.
  B2   if GATE S passes on the scratch, the IDENTICAL sequence is repeated FROM THE BED into a NEW file
       `claudeDev\D1_s3b_m3a3b_<stamp>.vi`, the bed left byte-unchanged; GATE S (a)-(e) re-asserted on the
       artefact PLUS the ORDERED IDEMPOTENT SECOND PASS of Pre-decided 106 (`wire_delta` 0 on a second,
       identical connect, and the identity read on THAT pass). Save by script at `ExecState` 1, otherwise
       `g.save(allow_broken=True)` -> `gui_save`, the approved broken-intermediate route (CLAUDE.md §3
       item 6). The artefact is NEVER run and never cold-loaded (34(f)).
  IF A3/A4/A5 FAIL, OR GATE S FAILS ON THE SCRATCH: nothing is saved, every scratch is deleted, the raw
  values are reported and the run STOPS. No Remove Bad Wires, no tunnel re-creation, no
  `Wire.Disconnect Terminal`, no third op, no improvisation. A negative STEP A is a FIRST-CLASS RESULT.

HYGIENE (the only other things that can FAIL)
 H1/H2  the bed's md5 is 33ef524e... BEFORE and UNCHANGED AFTER; the bed is NEVER opened for EXECUTION.
 H3     the five md5 pins hold; `OpFsInnerTunnelConnect_v1.vi` 5b4e5f0f... and `_v0.vi` 50a1e58a... unchanged.
 H4     every scratch deleted.   H5  refs opened == closed.   H6  the files this run left on disk, named.
 H7     the RBW ban held: the guard was never tripped (a trip would have raised and is reported).

RIG STATE 조립: no motor, no ASI, no camera. VI Scripting and COM only.
VERIFICATION LEVEL: FUNCTIONAL throughout (real reads and a real write into real copies of the bed,
asserted by uid echoes and OWNER IDENTITY); the artefact's legality is NOT claimed - it is broken BY
DESIGN and `ExecState` is RECORDED, never a criterion (Pre-decided 89/97).
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
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles, restart_labview                            # noqa: E402
from build_opconnectnested_v1 import Stop                                           # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                       # noqa: E402
import build_d1_m3a3b_d3 as C84                                                     # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "build_d1_m3a3b_d3b.json")

md5 = C82.md5
OP0 = C82.OP                                            # OpFsInnerTunnelConnect_v0.vi - never written
OP0_MD5 = "50a1e58a4825c2ce030ed9a41e204931"
OP1 = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelConnect_v1.vi")
OP1_MD5 = "5b4e5f0fb3baae96361c33ce81bcd7b1"
MAP1 = os.path.join(BENCH, "opfsinnertunnelconnect_v1_labels.json")
MAP0 = C82.MAP_OUT
OP_FSIT_READ = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
V5 = C82.V5

BED, BED_MD5, BED_BYTES = C82.BED, C82.BED_MD5, C82.BED_BYTES
PINS = C82.PINS

FSIT_UID = C82.FSIT_UID                 # 7468
LEFT_TERM = C82.LEFT_TERM_EXPECT        # 7488
RIGHT_TERM = 7471
RIGHT_WIRE = 7448
ROWD_WIRE = C82.ROWD_WIRE               # 7506 - DELETED here, and nothing else is done to it
LOOP_NEW = C82.LOOP_NEW                 # 23032
LOOP_NODES_IDX = C82.LOOP_NODES_IDX     # 21
LOOP_TERM_IDX = C82.LOOP_TERM_IDX       # 1
TERM_UID_EXPECT = 23906
RSR_EXPECT = C82.RSR_EXPECT             # 23868
OLD_SOURCE = C82.OLD_SOURCE             # 4334
GHOST_UID = 999983                      # c81's never-allocated uid, for the negative control
AUTO_ROUTE = True                       # c84 measured T and F identical; T is carried forward

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH_A = os.path.join(g.CLAUDEDEV, "C85A_%s.vi" % STAMP)
ART = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_%s.vi" % STAMP)
SCRATCHES = [SCRATCH_A]

RUN_DEADLINE_S = 40 * 60.0
RESERVE_S = 330.0
T0 = time.time()

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "op1": OP1, "bed": BED,
     "task": "D-3b of M3a-3b: delete wire 7506 WITHOUT Remove Bad Wires and ask whether FSIT #7468 still "
             "resolves and yields a BARE LeftTerm #7488; if so, connect #23868's outer terminal into it "
             "and land the artefact",
     "verification_level": "FUNCTIONAL",
     "rbw_ban": "gscript.remove_bad_wires_scripted / .remove_bad_wires rebound to a raising guard",
     "A": {}, "B": {}, "art": {}, "H": {}}


# ---------------------------------------------------------------- THE MECHANICAL RBW BAN
class RBWForbidden(RuntimeError):
    pass


_RBW_TRIPS = []


def _rbw_guard(*a, **k):                                                           # noqa: ANN001
    _RBW_TRIPS.append(repr(a)[:160])
    raise RBWForbidden(
        "Remove Bad Wires is FORBIDDEN in this dispatch (it is the suspected cause of c83's error 1055 "
        "and a rule-1a hazard, docs/cycle27-plan.md:1860-1862). Called with %r" % (a,))


g.remove_bad_wires_scripted = _rbw_guard
g.remove_bad_wires = _rbw_guard
C82.g.remove_bad_wires_scripted = _rbw_guard
C84.g.remove_bad_wires_scripted = _rbw_guard


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


# the imported helpers report through THIS file's gate/fact counters
C84.gate, C84.fact, C84.safe, C84.R = gate, fact, safe, R
C82.gate, C82.fact, C82.safe = gate, fact, safe


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
    fact("%s NON-MUTATING BRACKET: %d Wire object(s) ; wire %d present %r ; ExecState %r"
         % (tag, rec["n_wires"], ROWD_WIRE, rec["rowd_present"], es))
    return set(wires or []), rec


def raw_read(tag, rd):
    """Print EVERY error column of a read_tunnel result verbatim - the brief asks for raw errors."""
    if not rd:
        fact("%s read returned NOTHING (the driver raised; see the line above)" % tag)
        return
    fact("%s RAW: uid_in=%r uid_back=%r cls_back=%r | LeftTerm #%r wire(recip)=%r | RightTerm #%r "
         "wire=%r | is_source=%r owner=%r#%r cast=%r"
         % (tag, rd.get("uid_in"), rd.get("uid_back"), rd.get("cls_back"), rd.get("term_a_uid"),
            rd.get("wire_a"), rd.get("term_b_uid"), rd.get("wire_b"), rd.get("is_source"),
            rd.get("ownercls"), rd.get("owner_uid"), rd.get("cast_class")))
    fact("%s RAW ERROR COLUMNS: error out=%r err_a=%r err_b=%r err_bcw=%r others=%r"
         % (tag, rd.get("err"), rd.get("err_a"), rd.get("err_b"), rd.get("err_bcw"), rd.get("errs")))


# ======================================================================= [0] files only
def phase_files():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the pins, the ops this run needs")
    got = md5(BED)
    R["bed_md5_before"] = got
    R["bed_bytes"] = os.path.getsize(BED)
    gate("H1 bed md5 before == %s (%d B)" % (BED_MD5, BED_BYTES),
         got == BED_MD5 and R["bed_bytes"] == BED_BYTES,
         "got %s, %d bytes" % (got, R["bed_bytes"]), fatal=True)
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s" % (label, have, want, ("OK" if have == want else "DIFFERS")))
    R["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))
    for p, nm in ((OP1, "OpFsInnerTunnelConnect_v1.vi (the writer - used as-is, NEVER rebuilt)"),
                  (OP0, "OpFsInnerTunnelConnect_v0.vi (the fallback - used at most once)"),
                  (V5, "OpWireSource_v5.vi (the identity reader)"),
                  (OP_FSIT_READ, "OpFsInnerTunnelTerm_v0.vi (the FSIT face reader)"),
                  (MAP1, "the v1 label map")):
        gate("F0 %s on disk" % nm, os.path.isfile(p), p, fatal=True)
    R["op1_md5_before"] = md5(OP1)
    R["op0_md5_before"] = md5(OP0)
    gate("F0b the writer is the v1 cycle 84 saved (%s)" % OP1_MD5, R["op1_md5_before"] == OP1_MD5,
         "got %s (%d bytes)" % (R["op1_md5_before"], os.path.getsize(OP1)), fatal=True)
    gate("F0c the fallback v0 is unchanged (%s)" % OP0_MD5, R["op0_md5_before"] == OP0_MD5,
         "got %s" % R["op0_md5_before"])
    fact("THE READER'S ERROR SURFACE, from the label map itself (a claim about wiring is NOT trusted - "
         "gate A7 tests it on the machine): opfsinnertunnelterm_labels.json declares err_a/err_b/err_bcw "
         "plus errL/errT/errO/errU/errG/errS/errWU/errCO, and read_tunnel reads every one of them AND "
         "`error out`; c83's counter-example (OpFsInnerTunnelConnect_v0's UNWIRED error indicator) is why "
         "every gate below is decided by the UID ECHO instead.")


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


# ======================================================================= [A] THE MEASUREMENT
def step_a():
    head("[A] STEP A - delete wire %d on a dated scratch COPY, with NO Remove Bad Wires anywhere, and ask "
         "whether FlatSequenceInnerTunnel #%d still resolves" % (ROWD_WIRE, FSIT_UID))
    shutil.copyfile(BED, SCRATCH_A)
    time.sleep(0.4)
    gate("A0a the scratch is a byte-identical copy of the bed", md5(SCRATCH_A) == R["bed_md5_before"],
         os.path.basename(SCRATCH_A), fatal=True)
    t = time.time()
    _, err = safe("ensure_loaded(SCRATCH_A)", lambda: g.ensure_loaded(SCRATCH_A))
    fact("ensure_loaded(scratch A) took %.1f s%s" % (time.time() - t, ((" ERROR " + err) if err else "")))
    d_idx, trip = C82.resolve_triple(SCRATCH_A, "A")
    R["A"]["triple"] = trip

    wires0, br0 = census(SCRATCH_A, "A BEFORE the delete")
    R["A"]["bracket_before"] = br0
    gate("A0b wire %d is in the Wire census BEFORE the delete" % ROWD_WIRE, br0["rowd_present"],
         "%d Wire objects" % br0["n_wires"], fatal=True)
    before = C84.fsit_read(SCRATCH_A, FSIT_UID, "A BEFORE")
    R["A"]["fsit_before"] = before
    raw_read("A BEFORE", before)
    gate("A0c the PRECONDITION read: uid echo %d, LeftTerm #%d carrying wire %d, RightTerm #%d carrying "
         "wire %d" % (FSIT_UID, LEFT_TERM, ROWD_WIRE, RIGHT_TERM, RIGHT_WIRE),
         bool(before) and before.get("uid_back") == FSIT_UID and before.get("term_a_uid") == LEFT_TERM
         and before.get("wire_a") == ROWD_WIRE and before.get("term_b_uid") == RIGHT_TERM
         and before.get("wire_b") == RIGHT_WIRE,
         "uid_back=%r term_a=%r wire_a=%r term_b=%r wire_b=%r"
         % ((before or {}).get("uid_back"), (before or {}).get("term_a_uid"), (before or {}).get("wire_a"),
            (before or {}).get("term_b_uid"), (before or {}).get("wire_b")), fatal=True)

    head("[A1] THE DELETE - `del_wire(%d)` AND NOTHING ELSE. No Remove Bad Wires." % ROWD_WIRE)
    deleted, e = safe("A1 del_wire(%d)" % ROWD_WIRE, lambda: C82.del_wire(SCRATCH_A, ROWD_WIRE, "A1 "))
    R["A"]["delete_ok"] = bool(deleted)
    R["A"]["delete_error"] = e
    gate("A1 wire %d was deleted (del_wire found it in the traverse order and removed it)" % ROWD_WIRE,
         bool(deleted) and not e, "returned %r ; error %r" % (deleted, e), fatal=True)

    wires1, br1 = census(SCRATCH_A, "A AFTER the delete")
    R["A"]["bracket_after_delete"] = br1
    lost = sorted(wires0 - wires1)
    gained = sorted(wires1 - wires0)
    R["A"]["wires_lost_by_delete"] = lost
    R["A"]["wires_gained_by_delete"] = gained
    fact("A2 CENSUS DIFF across the delete: lost %r ; gained %r ; count %d -> %d ; ExecState %r -> %r  "
         "(THE BRIEF'S 'broken-wire count before and after' as far as a NON-MUTATING reader reaches - the "
         "Remove-Bad-Wires delta, the only true broken-wire count on disk, is FORBIDDEN in this dispatch)"
         % (lost, gained, br0["n_wires"], br1["n_wires"], br0["exec_state"], br1["exec_state"]))
    gate("A2 the delete removed EXACTLY wire %d and nothing else, and created nothing" % ROWD_WIRE,
         lost == [ROWD_WIRE] and not gained,
         "lost %r gained %r (count %d -> %d)" % (lost, gained, br0["n_wires"], br1["n_wires"]))

    head("[A3-A6] THE QUESTION: after the delete, and with NO Remove Bad Wires, does #%d still resolve?"
         % FSIT_UID)
    after = C84.fsit_read(SCRATCH_A, FSIT_UID, "A AFTER")
    R["A"]["fsit_after"] = after
    raw_read("A AFTER", after)
    a3 = gate("A3 *** #%d STILL RESOLVES after the delete (uid echo `uid_back` == %d - Pre-decided 125, "
              "NEVER an empty error column)" % (FSIT_UID, FSIT_UID),
              bool(after) and after.get("uid_back") == FSIT_UID,
              "uid_back=%r cls_back=%r ; raw `error out`=%r"
              % ((after or {}).get("uid_back"), (after or {}).get("cls_back"), (after or {}).get("err")))
    a4 = gate("A4 its `Left Terminal` comes back as #%d" % LEFT_TERM,
              bool(after) and after.get("term_a_uid") == LEFT_TERM,
              "term_a_uid=%r ; err_a=%r" % ((after or {}).get("term_a_uid"), (after or {}).get("err_a")))
    a5 = gate("A5 that terminal is BARE (wire 0)", bool(after) and after.get("wire_a") == 0,
              "wire_a=%r (was %r)" % ((after or {}).get("wire_a"), (before or {}).get("wire_a")))
    a6 = gate("A6 the inner wire %d on the `Right Terminal` #%d SURVIVES" % (RIGHT_WIRE, RIGHT_TERM),
              bool(after) and after.get("term_b_uid") == RIGHT_TERM and after.get("wire_b") == RIGHT_WIRE,
              "term_b_uid=%r wire_b=%r ; err_b=%r"
              % ((after or {}).get("term_b_uid"), (after or {}).get("wire_b"), (after or {}).get("err_b")))

    head("[A7] THE NEGATIVE CONTROL on these same bytes (c81, diag_c81_uidref.log:85): a never-allocated "
         "uid must be caught by the ECHO, because every error column can come back EMPTY")
    ghost = C84.fsit_read(SCRATCH_A, GHOST_UID, "A GHOST")
    R["A"]["ghost"] = ghost
    raw_read("A GHOST", ghost)
    gate("A7 the reader's uid echo CATCHES a never-allocated uid (%d)" % GHOST_UID,
         bool(ghost) and ghost.get("uid_back") != GHOST_UID,
         "uid_back=%r (must NOT be %d) ; every error column %s"
         % ((ghost or {}).get("uid_back"), GHOST_UID,
            "EMPTY - which is exactly why the echo decides"
            if not ((ghost or {}).get("err") or (ghost or {}).get("errs")) else "non-empty"))

    _u, trows = safe("A border read", lambda: g.node_terms_uid(SCRATCH_A, d_idx, LOOP_NODES_IDX),
                     (None, []))[0] or (None, [])
    brow = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
    R["A"]["border_after_delete"] = brow
    fact("A border t%d AFTER the delete: name=%r is_source=%r wire=%r (expected uid #%d, owner "
         "RightShiftRegister #%d)"
         % (LOOP_TERM_IDX, (brow or {}).get("name"), (brow or {}).get("is_source"),
            (brow or {}).get("wire"), TERM_UID_EXPECT, RSR_EXPECT))

    R["A"]["answer"] = {"resolves": a3, "left_terminal": a4, "bare": a5, "right_wire_survives": a6}
    return d_idx, (a3 and a4 and a5)


# ======================================================================= [B] the landing
def connect_and_gate(tag, target, d_idx, labels, ar, rec, allow_fallback=False):
    """ONE connect + GATE S. No Remove Bad Wires: `gate_s` is called with probe_bad=False, the branch
    that never touches it, and d2 is replaced by the non-mutating d2' below."""
    before_read = C84.fsit_read(target, FSIT_UID, "%s BEFORE" % tag)
    rec["fsit_before"] = before_read
    raw_read("%s BEFORE" % tag, before_read)
    wires0, br0 = census(target, "%s BEFORE the connect" % tag)
    nodes0, _ = M.node_census(target, "%s BEFORE the connect" % tag)
    r = C84.fsit_call(OP1, labels, target, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                      ar_label=ar, auto_route=AUTO_ROUTE)
    fact("%s v1 RAW INVOKE ERROR = %r ; op `error out` = %r" % (tag, r.get("invoke_err"), r.get("err")))
    fact("%s v1 RESULT: term_uid=%r uid_back=%r `UID 2`=%r is_broken=%r wire_delta=%r junk_Invoke=%r | "
         "err_uidvi=%r err_fsit=%r err_termuid=%r err_uidback=%r"
         % (tag, r.get("term_uid"), r.get("uid_back"), r.get("sink_wire_uid"), r.get("is_broken"),
            r.get("wire_delta"), r.get("invoke_delta"), r.get("err_uidvi"), r.get("err_fsit"),
            r.get("err_termuid"), r.get("err_uidback")))
    rec["v1"] = r
    if allow_fallback and (r.get("invoke_err") or r.get("err")) and r.get("wire_delta") == 0:
        head("[%s] v1 raised a REAL error and created nothing - ONE fallback call of "
             "OpFsInnerTunnelConnect_v0.vi, as the brief allows" % tag)
        labs0, e = safe("%s load the v0 label map" % tag,
                        lambda: json.load(open(MAP0, encoding="utf-8")), None)
        if labs0:
            r0 = C84.fsit_call(OP0, labs0, target, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                               ar_label="", auto_route=None,
                               inv_err_label=labs0.get("err_invoke") or "error out 7")
            rec["v0"] = r0
            fact("%s v0 RAW INVOKE ERROR = %r ; op `error out` = %r ; `UID 2`=%r wire_delta=%r"
                 % (tag, r0.get("invoke_err"), r0.get("err"), r0.get("sink_wire_uid"),
                    r0.get("wire_delta")))
            if r0.get("wire_delta"):
                r = r0
    _final, prec = C82.purge_junk(target, nodes0, "%s junk" % tag, [d_idx])
    rec["purge"] = prec
    wires1, br1 = census(target, "%s AFTER the connect" % tag)
    rec["bracket_before"], rec["bracket_after"] = br0, br1
    lost = sorted(wires0 - wires1)
    gained = sorted(wires1 - wires0)
    rec["wires_lost"], rec["wires_gained"] = lost, gained
    fact("%s CENSUS DIFF across the connect: lost %r ; gained %r ; count %d -> %d ; ExecState %r -> %r"
         % (tag, lost, gained, br0["n_wires"], br1["n_wires"], br0["exec_state"], br1["exec_state"]))
    _u2, trows = safe("%s border read" % tag,
                      lambda: g.node_terms_uid(target, d_idx, LOOP_NODES_IDX), (None, []))[0] or (None, [])
    brow = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
    rec["border_after"] = brow
    fact("%s border t%d AFTER the connect: wire=%r (that terminal's uid is #%d, owner #%d)"
         % (tag, LOOP_TERM_IDX, (brow or {}).get("wire"), TERM_UID_EXPECT, RSR_EXPECT))

    passed, out = C84.gate_s(tag, target, d_idx, before_read, r, None, rec, probe_bad=False)
    fact("%s GATE S(d2) IS NOT MEASURED: the brief forbids Remove Bad Wires, which is the only "
         "diagram-wide broken-wire count this fleet owns (docs/toolkit-capabilities.md:68 - the sound "
         "per-wire reader is NOT BUILT; docs/NAMES.md:984 - reading `Is Broken?` PERTURBS the target). "
         "d2' below is a WEAKER non-mutating substitute and is not the brief's gate." % tag)
    d2p = gate("%s GATE S(d2') NON-MUTATING SUBSTITUTE: the connect lost no wire and gained at most one, "
               "and `ExecState` did not regress" % tag,
               (not lost) and len(gained) <= 1 and not (br0["exec_state"] == 1 and br1["exec_state"] != 1),
               "lost %r gained %r ; ExecState %r -> %r"
               % (lost, gained, br0["exec_state"], br1["exec_state"]))
    rec["gate_s_d2_prime"] = d2p
    rec["gate_s_passed"] = bool(passed and d2p)
    return bool(passed and d2p), r


def step_b_scratch(d_idx, labels, ar):
    head("[B1] THE LANDING, on the SAME post-delete scratch: connect the NEW loop's shift-register OUTER "
         "terminal (#%d, owner RightShiftRegister #%d) into the now-BARE FSIT LeftTerm #%d"
         % (TERM_UID_EXPECT, RSR_EXPECT, LEFT_TERM))
    rec = {"where": "scratch"}
    try:
        passed, _r = connect_and_gate("B", SCRATCH_A, d_idx, labels, ar, rec, allow_fallback=True)
    except Stop as e:
        rec["refused"] = "STOP %s" % e
        passed = False
        gate("B the scratch cell ran (stopped at a fatal gate)", False, str(e)[:160])
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        rec["refused"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        rec["traceback"] = traceback.format_exc()[-1200:]
        passed = False
        gate("B the scratch cell ran", False, rec["refused"])
    R["B"] = rec
    gate("B GATE S passed IN FULL on the scratch (a)(b)(c)(d1)(d2')(e)", passed, "%r" % rec.get("gate_s"))
    return passed


# ======================================================================= [ART] the deliverable
def step_artefact(labels, ar):
    head("[ART] the deliverable: the IDENTICAL sequence FROM THE BED into a NEW file, the bed left "
         "byte-unchanged")
    if left_s() < 260:
        gate("ART had time to run", False, "%.0f s left of the deadline reserve" % left_s())
        return
    shutil.copyfile(BED, ART)
    time.sleep(0.4)
    gate("ART0 the artefact starts as a byte-identical copy of the bed", md5(ART) == R["bed_md5_before"],
         os.path.basename(ART), fatal=True)
    safe("ensure_loaded(artefact)", lambda: g.ensure_loaded(ART))
    d_idx, trip = C82.resolve_triple(ART, "ART")
    R["art"]["triple"] = trip
    wires0, br0 = census(ART, "ART BEFORE the delete")
    deleted, e = safe("ART del_wire(%d)" % ROWD_WIRE, lambda: C82.del_wire(ART, ROWD_WIRE, "ART "))
    gate("ART1 wire %d deleted on the artefact (no Remove Bad Wires)" % ROWD_WIRE, bool(deleted) and not e,
         "returned %r error %r" % (deleted, e), fatal=True)
    rd = C84.fsit_read(ART, FSIT_UID, "ART AFTER the delete")
    raw_read("ART AFTER the delete", rd)
    R["art"]["fsit_after_delete"] = rd
    gate("ART2 #%d resolves and its LeftTerm #%d is BARE on the artefact too" % (FSIT_UID, LEFT_TERM),
         bool(rd) and rd.get("uid_back") == FSIT_UID and rd.get("term_a_uid") == LEFT_TERM
         and rd.get("wire_a") == 0,
         "uid_back=%r term_a=%r wire_a=%r" % ((rd or {}).get("uid_back"), (rd or {}).get("term_a_uid"),
                                              (rd or {}).get("wire_a")), fatal=True)

    rec1 = {"pass": "first"}
    p1, r1 = connect_and_gate("ART-P1", ART, d_idx, labels, ar, rec1)
    R["art"]["pass1"] = rec1
    gate("ART3 GATE S on the FIRST pass of the artefact", p1, "%r" % rec1.get("gate_s"))

    head("[ART] THE ORDERED IDEMPOTENT SECOND PASS (Pre-decided 106): the SAME connect again, "
         "`wire_delta` 0, and the identity read on THAT pass")
    rec2 = {"pass": "second (ordered idempotent)"}
    p2, r2 = connect_and_gate("ART-P2", ART, d_idx, labels, ar, rec2)
    R["art"]["pass2"] = rec2
    gate("ART4 the ordered SECOND pass is IDEMPOTENT: wire_delta 0", r2.get("wire_delta") == 0,
         "wire_delta %r (pass 1 was %r)" % (r2.get("wire_delta"), r1.get("wire_delta")))
    gate("ART5 GATE S RE-ASSERTED on the ordered second pass", p2, "%r" % rec2.get("gate_s"))
    if not (p1 and p2):
        gate("ART6 the artefact is SAVED", False,
             "GATE S did not hold on both passes - NOTHING IS SAVED; the file is deleted")
        safe("close_panel(artefact)", lambda: g.close_panel(ART))
        SCRATCHES.append(ART)
        return

    head("[ART] SAVE")
    es = g.exec_state(ART)
    R["art"]["exec_state_before_save"] = es
    fact("ART ExecState BEFORE the save = %r - RECORDED, never a criterion (the bed is broken BY DESIGN, "
         "Pre-decided 89/97; the artefact is NEVER run and never cold-loaded, 34(f))" % es)
    if es == 1:
        size, serr = safe("ART g.save - script route", lambda: g.save(ART))
        route = "SCRIPT (COM SaveInstrument) - ExecState 1"
    else:
        size, serr = safe("ART g.save(allow_broken=True) - the approved broken-intermediate route",
                          lambda: g.save(ART, allow_broken=True))
        route = ("GUI_SAVE (gscript.save -> gui_save: block-diagram window fronted, click-probed, Ctrl+S, "
                 "mtime verified; CLAUDE.md §3 item 6, user 2026-09-22 broken-intermediate save)")
    R["art"]["save_route"] = route
    R["art"]["save_error"] = serr
    gate("ART6 the artefact was SAVED (%s)" % route, bool(size) and not serr,
         "returned %r ; error %r" % (size, serr))
    if not os.path.isfile(ART):
        gate("ART7 the artefact is on disk", False, ART)
        return
    R["art"]["path"] = ART
    R["art"]["md5"] = md5(ART)
    R["art"]["bytes"] = os.path.getsize(ART)
    g.reset()
    time.sleep(1.5)
    es2 = g.exec_state(ART)
    R["art"]["exec_state_after_save"] = es2
    gate("ART8 the artefact differs from the bed in BYTES", R["art"]["md5"] != R["bed_md5_before"],
         "artefact %s vs bed %s" % (R["art"]["md5"], R["bed_md5_before"]))
    fact("ART ARTEFACT %s md5 %s (%d bytes) ExecState after the save %r ; save route: %s"
         % (ART, R["art"]["md5"], R["art"]["bytes"], es2, route))


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close panels, delete every scratch, re-read every pin, handles at both ends")
    for p in SCRATCHES + [OP0, OP1, ART, OP_FSIT_READ, V5]:
        safe("close_panel(%s)" % os.path.basename(p), lambda q=p: g.close_panel(q))
    R["H"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts (opened / closed / live / cached op VIs): %r" % R["H"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         R["H"]["ref_counts"]["live"] == 0, "%r" % R["H"]["ref_counts"])
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
    gate("H2 bed md5 UNCHANGED after the run", got == R.get("bed_md5_before"),
         "before %s / after %s" % (R.get("bed_md5_before"), got))
    allpins = True
    R["pins_after"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_after"][label] = have
        allpins = allpins and (have == want)
        fact("PIN AFTER  %-16s %s  (want %s) %s" % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the five md5 pins all hold", allpins)
    R["op1_md5_after"] = md5(OP1) if os.path.isfile(OP1) else "MISSING"
    R["op0_md5_after"] = md5(OP0) if os.path.isfile(OP0) else "MISSING"
    gate("H3b OpFsInnerTunnelConnect_v1.vi md5 UNCHANGED (used as-is, never rebuilt)",
         R["op1_md5_after"] == OP1_MD5, "%s" % R["op1_md5_after"])
    gate("H3c OpFsInnerTunnelConnect_v0.vi md5 UNCHANGED", R["op0_md5_after"] == OP0_MD5,
         "%s" % R["op0_md5_after"])
    gate("H7 the Remove-Bad-Wires ban held: the guard was never tripped", not _RBW_TRIPS,
         "trips: %r" % (_RBW_TRIPS,))
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6 nothing was REMOVED from claudeDev", not gone, "removed %r" % (gone,))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    if os.path.isfile(ART):
        fact("ON DISK %s md5 %s (%d bytes)" % (ART, md5(ART), os.path.getsize(ART)))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("build_d1_m3a3b_d3b - STEP A: delete w7506 with NO Remove Bad Wires and ask whether FSIT #7468 "
          "still resolves; STEP B: land Row D if it does", flush=True)
    print("=" * 100, flush=True)
    labels, ar = None, None
    try:
        phase_files()
        labels = json.load(open(MAP1, encoding="utf-8"))
        ar = labels.get("auto_route") or ""
        fact("the v1 label map declares `Auto Route?` as %r ; this run uses %r (c84 measured TRUE and "
             "FALSE identical on the merge cell)" % (ar, AUTO_ROUTE))
        phase_restart()
        d_idx, answered = step_a()
        dump()
        if not answered:
            fact("STEP B IS NOT TAKEN, by the brief's own branch. STEP A answered %r - so NOTHING IS "
                 "SAVED, no Remove Bad Wires, no tunnel re-creation, no `Wire.Disconnect Terminal`, no "
                 "third op, no improvisation. A negative STEP A is a FIRST-CLASS RESULT: it converts "
                 "c83's confounded `error 1055` into a clean finding. (A3/A4/A5 above already carry the "
                 "gate arithmetic; this line is not a second failure.)" % (R["A"].get("answer"),))
        else:
            ok = step_b_scratch(d_idx, labels, ar)
            dump()
            if ok:
                step_artefact(labels, ar)
            else:
                fact("STEP B's artefact NOT produced: GATE S failed on the scratch. Nothing was saved.")
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
