"""STAGE M3a-2 - the INITIAL VALUES of the two shift registers M3a-1 created on WhileLoop #23032.

THE PINNED STATIC GATE, Pre-decided 98(3) (from now on the ONLY invocation, repeated here because the
finding's repeating class was "the astcheck invocation is hand-typed and unpinned"):

    py tools/bgrun.py --material --max-min 5 --log "tools/bench/c74_astcheck_m3a2.log" -- \
        py -u "tools/bench/c60c_astcheck.py" "<ABS path to this file>" --route owner

  `--route owner` and not `movein`, because Pre-decided 62 says the route declares what THE FILE DOES:
  this file calls `move_in` nowhere and does not import it - M3a-2 moves no object, it wires two rows.

THE LAUNCH LINE (NOT RUN BY THE SESSION THAT WROTE THIS FILE - the prior-art verdict is disposed by a
judgement session first, and `tools/hooks/guard_cycle.py` enforces that):

    py tools/bgrun.py --material --max-min 45 --log "tools/bench/build_d1_m3a2.log" -- \
        py -u "tools/recipes/build_d1_m3a2.py"

WHAT THIS STAGE IS, IN ONE SENTENCE. Loop #23032's two registers are uninitialised: their LEFT OUTER
terminals are bare. This stage wires each LEFT OUTER to the SAME source the ORIGINAL loop's register is
initialised from, so the two loops are fed identically. It is TWO rows (Pre-decided 91), it is NOT four.

PRIOR ART CHECKED BEFORE A LINE WAS WRITTEN (CLAUDE.md, "before creating any new op, tool or recipe").
NOTHING NEW IS BUILT - user, 2026-09-18 08:53 ("장치는 더 만들지 말고 계속 진행"):
  * `tools/gscript.py` - `shift_reg` :783 / `shift_reg_left` :816 (OpShiftRegs_v0/v1: a register's uid,
    class, OUTER terminal and INSIDE terminals, plus its LEFT partner); `node_terms_uid` :955;
    `report_all` :502; `node_labels`; `count` :1035; `exec_state` :2007; `ensure_loaded` :1298;
    `save` :2135 with the Pre-decided 88 `allow_broken` route; `ref_counts`; `close_panel`.
  * `connect_from_wire` (`OpConnectFromWire_v0.vi`, BUILT + SAVED 2026-09-17,
    `docs/toolkit-capabilities.md:70`) - THE writer whose SOURCE is a terminal of an existing WIRE rather
    than a `Nodes[]` entry. It wrote M3a-1's t1 row and its sixth row. Pre-decided 93.
  * `wire_source_owner` (`OpWireSource_v5`) - the only by-UID walk of a WIRE's terminals. REPAIRED
    2026-09-22 (indicators scrubbed per call, all 8 op error outs read, the op's uid echo required);
    acceptance `tools/bench/diag_c68_echo_accept.log` 8/0.
  * `owner_of` / `diag_index` (`OpOwnerChain_v1`, strict uid echo) in `build_d1_v0`.
  * `find_node` / `terms_at` / `term_state` / `node_view` / `node_census` / `new_nodes` / `delete_by_uid`
    / `wired_count` - all take their path as a parameter, all imported from `build_d1_m3a1` and NOT
    re-written here. `census_and_purge` is deliberately NOT imported: it writes M3a-1's own JSON.
  * `tools/bench/diag_c73_m3a2_rows.{log,json}` - the MEASUREMENT this stage is built on (rc=0, 5 hygiene
    gates pass / 0 fail, nothing mutated). Every uid below comes from it and every one is RE-MEASURED on
    the live target before it is used.
  * `tools/bench/build_d1_routeb_v0_run2.log:467-468` - the PREVIOUSLY UNREAD evidence (A4): bare
    register terminals on `Diagram #686` sit at ODD `Terminals[]` indices. Cited in `resolve_sink`,
    logged as an expectation beside the index found - never used as a criterion, never carried in.
  NO new op VI, NO new gscript verb, NO new checker, NO new process device.

WHY `wire_sr` IS THE WRONG VERB HERE (Pre-decided 93). `wire_sr('LeftOutNode')` takes its source as
Terminals[t] of a TOP-LEVEL `Nodes[]` entry, and `wire_sr('LeftOutCtl')` as a front-panel control. Both
of this stage's sources are `FlatSequenceInnerTunnel`s owned by `FlatSequence #681`; a tunnel is not a
`Nodes[]` member, so neither variant can address them. `connect_from_wire` addresses the WIRE, so it can.
This file calls `wire_sr` nowhere.

THE TWO ROWS AND THEIR PREDICTIONS, WRITTEN BEFORE THE RUN (Pre-decided 92):
  ROW A - VISA session. SOURCE = the ONE source terminal of wire 4185 = `FlatSequenceInnerTunnel` #4194.
          SINK = LEFT register #23880 OUTER (named 'VISA out'). 4185 also feeds the ORIGINAL's #4344 OUTER.
  ROW B - position.     SOURCE = the ONE source terminal of wire 3968 = `FlatSequenceInnerTunnel` #3974.
          SINK = LEFT register #23909 OUTER ('position [internal units]'). 3968 also feeds #4274 OUTER.
  Both are SAME-DIAGRAM rows on `Diagram #686` (both loop borders and all four wires are owned by #686
  under strict uid echo), so Pre-decided 66's border exemption does NOT apply and the ordinary one-net
  test does. Hop count is an output, never a criterion (Pre-decided 90).

PREDICTION CONTRACT - the gates. Everything else in this file is a FACT line (Pre-decided 63: a
measurement that comes back negative is a fact, not a failure; a MUTATOR CALL THE MACHINE REFUSED is a
failure).
  H1   the input artefact's md5 is 6b3c1f3c4ba80f1fa7411a55f0218bea BEFORE the run
  H2   it is UNCHANGED after the run (it is copied once and never opened, never edited, never run)
  H3   the four STATUS md5 pins (ORIGINAL, S1, S2, THE BED) all hold, before and after
  H4   the target starts byte-identical to the input (the copy landed)
  H5   `tools/gscript.py` and `tools/bench/c60c_astcheck.py` are byte-identical across the run
  H6   gscript's VI-Server reference counter is level (opened == closed, 0 live) at exit
  H7   the LabVIEW handle count is read at entry and at exit
  H8   no mutator call was REFUSED BY THE MACHINE (this file's refusals AND build_d1_m3a1's, since the
       imported helpers record theirs there). ⚠️ A MACHINE REFUSAL IS ONLY WHAT LabVIEW DECLINED.
       A Python exception raised by THIS SCRIPT is OUR DEFECT and is counted by H9, never by H8
       (Pre-decided 100 §2: on 2026-09-22 `main()`'s bare handler routed a `TypeError` in our own
       format string into `refusal()`, and H8 then reported that the machine had refused a mutator
       when no mutator was called - a falsehood the runner's 60-char truncation could turn into a
       firefighter cycle fired at a failure that never happened).
  H9   NO DEFECT IN OUR OWN PYTHON CODE: no exception raised inside this script's own logic
       (ADDED 2026-09-22, Pre-decided 100 §2). Each one is reported with its exception type and the
       `file:line` it was raised at, under its own clearly-worded FACT and FAIL line.
  A-A  ROW A ACCEPTANCE, twice: immediately after the write and again after the junk purge. The wire
       carried by the new sink terminal has EXACTLY ONE source terminal OF ANY OWNER CLASS (Pre-decided
       77 - count everything, filter nothing away before counting), that one is #4194, the ORIGINAL sink
       #4344 OUTER is STILL a terminal of that net, and the walk has ZERO Pre-decided 85 violations.
  A-B  ROW B ACCEPTANCE, the same, with #3974 / #4274.
  S1   the saved file's bytes DIFFER from the input's - the in-memory edits reached the disk
  S2   the saved path is the `claudeDev` target this run created
  S3   the BEFORE capture LANDED ON DISK, and S4 the AFTER capture did (ADDED 2026-09-22 by the B2
       disposition of Pre-decided 99): USER RULE 17:5x is only met if the captures exist, and in
       M3a-1 run 5 they did not (`tools/bench/build_d1_m3a1.log:3402`, "exists False, exists False")
       because the caller pre-quoted the path and `gscript.py:281-287`'s `q()` quoted it again
  A row that STOPS before its write (an empty source walk, an unresolvable sink, a source that is not the
  predicted one) writes a FACT line, wires NOTHING, substitutes NOTHING (Pre-decided 68) - and its
  acceptance gate FAILS, because a stage whose row never happened must not exit 0. That is the one place
  this file rules on gate discipline, and it follows Pre-decided 69's precedent ("the run must not exit 0
  with a silently dropped consumer") rather than 63's, which is about measurements.

WHAT THE PRIOR-ART REVIEW REMOVED (Pre-decided 99, A3 + B4 - ACCEPTED, NOT REFUTED):
  * THE #637 REGISTER CENSUS IS DELETED FROM THIS RECIPE. It is replaced by ONE CITATION:
    `tools/bench/diag_c73_m3a2_rows.log:42-57` already censused loop #637 on a BYTE-IDENTICAL
    artefact - it reads 15 slots, not 14, and :43-44 show #4256 INSIDE on wire 9113 and #4334 INSIDE
    on wire 7337, i.e. NOT bare. So Pre-decided 95's named "severed inside terminal" candidate is
    WITHDRAWN, and a wire-uid census cannot see "shift-register terminal unwired" in any case
    (Pre-decided 89). A step that is already measured and cannot answer its question is pure cost.
  * `ExecState 0`'s CAUSE IS FORMALLY OPEN and is not answerable with this fleet's readers
    (`VI.Get Errors` 452 is absent from the exported ActiveX interface). THIS RECIPE DOES NOT GATE
    ON `ExecState` AND CLAIMS NOTHING ABOUT IT. Pre-decided 95's surviving half is operative:
    M3a-2 is NOT required to reach `ExecState 1` and is NOT judged on it.

WHAT IS MEASURED AND NEVER GATED:
  * Pre-decided 94 - the TYPE CHECK. `Wire.Is Broken?` is read ONLY in a separate ordered pass after both
    rows are written: an idempotent re-connect of the same row, whose `wire_delta` is expected to be 0.
    It is NEVER read in the pass that makes the connection. `ExecState` is never a type discriminator
    (42(c)) and is never substituted for the identity test (Pre-decided 70).
    ⚠️ `OpConnectFromWire_v0` reads its own `Is Broken?` indicator internally, ordered after its write;
    that value is recorded VERBATIM as a FACT of the write pass and is NOT the type check. The type check
    is the second pass's reading, and only that one.
  * Pre-decided 91 - M3a-3, NAMED here with its uids and NOT WIRED by this stage: the two RIGHT OUTER
    terminals stay bare, which drops nothing, because the downstream consumers are still wired to the OLD
    loop's registers (#4256 OUTER -> wire 4859 -> `Global #7202` t0; #4334 OUTER -> wire 7506 ->
    `FlatSequenceInnerTunnel #7468`). A bare SOURCE is legal LabVIEW (Pre-decided 69).

RULE COMPLIANCE.
  rule 1  - the ORIGINAL, S1, S2 and the bed are READ ONLY; their md5s are gates at both ends. The input
            artefact is COPIED once with shutil and never opened over COM; H2 proves it.
  rule 1a - the artefact REMAINS NOT COMPUTATION-EQUIVALENT to the original and is NEVER RUN (34(f),
            Pre-decided 97). After M3a-2 both loops exist and the OLD one still feeds both downstream
            consumers. Equivalence is claimed at the end of the M3 chain, never at a stage boundary.
  rule 1b - rig 조립: no motor, no ASI, no camera. `tools/motor_gate.py` is not called.
  rule 1c - nothing here touches a frame path.
  GUI    - the ONLY GUI act reachable from this file is `gscript.gui_save`, entered through
            `save(allow_broken=True)` on a broken VI (Pre-decided 88). Its guards are the claudeDev-only
            path check, the clickprobe-MEASURED foreground before Ctrl+E/Ctrl+S, and the mtime move; this
            file adds the capture BEFORE and AFTER and makes the after-confirmation the file's own md5
            (Pre-decided 96), which is a stronger confirmation for a save than a screenshot.
  split  - the stage leaves a file whatever `ExecState` says (Pre-decided 88/96). The user's 2026-09-19
            rule: a step is not done until it has left a file.
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
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index                                                 # noqa: E402
from build_opconnectfromwire_v0 import connect_from_wire as CONNECT_FROM_WIRE      # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")

# ---------------------------------------------------------------- the pins, all read from files
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
BED_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
PINS = (("ORIGINAL", ORIGINAL, ORIG_MD5), ("S1 D1_s1_copy", S1_ARTEFACT, S1_MD5),
        ("S2 D1_s2_loops", S2_ARTEFACT, S2_MD5), ("THE BED", BED, BED_MD5))
TOOL_PINS = (os.path.join(ROOT, "tools", "gscript.py"),
             os.path.join(BENCH, "c60c_astcheck.py"))

# THE INPUT ARTEFACT - M3a-1's output. NEVER MODIFIED, NEVER OPENED, NEVER RUN (34(f) / Pre-decided 97).
INPUT = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a_BROKEN_20260922_005732.vi")
INPUT_MD5 = "6b3c1f3c4ba80f1fa7411a55f0218bea"

STAMP = time.strftime("%Y%m%d_%H%M%S")
TARGET = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_%s.vi" % STAMP)
OUT = os.path.join(BENCH, "build_d1_m3a2.json")
CFW_LABELS = json.load(open(os.path.join(BENCH, "opconnectfromwire_v0_labels.json"), encoding="utf-8"))

# ---------------------------------------------------------------- the topology, all RE-MEASURED live
TOP = 0
D686 = 686                       # the diagram that carries BOTH loop borders and all four wires
LOOP_A = 23032                   # the NEW WhileLoop - M3a-1's registers live on it
BODY_A = 23058                   # its body diagram
# The ORIGINAL WhileLoop #637 is NOT censused by this recipe (Pre-decided 99, A3 + B4): its register
# table is already on file for a byte-identical artefact - `tools/bench/diag_c73_m3a2_rows.log:42-57`,
# 15 slots, #4256 INSIDE on wire 9113 and #4334 INSIDE on wire 7337. No constant is needed.
REG_PROBE_MAX = 16

# (tag, source wire, predicted source owner, RIGHT reg uid, LEFT reg uid, register name, original sink)
ROWS = [
    {"tag": "A VISA", "source_wire": 4185, "source_owner": 4194,
     "right_uid": 23868, "left_uid": 23880, "reg_name": "VISA out", "original_sink": 4344,
     "why": "wire 4185 is what initialises the ORIGINAL loop's VISA register (#4344 OUTER); the new "
            "register must be fed from the SAME net or the two loops do not see the same session"},
    {"tag": "B POS", "source_wire": 3968, "source_owner": 3974,
     "right_uid": 23895, "left_uid": 23909, "reg_name": "position [internal units]",
     "original_sink": 4274,
     "why": "wire 3968 is what initialises the ORIGINAL loop's position register (#4274 OUTER)"},
]

# Pre-decided 91 - M3a-3. NAMED, NOT WIRED BY THIS STAGE. Discharging 69 by naming them, with their uids.
M3A3_CONSUMERS = [
    {"old_right_outer": 4256, "wire": 4859, "consumer": "Global #7202 'Global motor pos.vi' t0 "
                                                        "'Focus position'", "new_right_outer": 23868},
    {"old_right_outer": 4334, "wire": 7506, "consumer": "FlatSequenceInnerTunnel #7468",
     "new_right_outer": 23895},
]

RUN_DEADLINE_S = 45 * 60.0       # the `bgrun --max-min` this file is launched under
RESERVE_S = 420.0                # held back for the save and the hygiene tail
ROW_MIN_S = 240.0

T_START = time.time()
passes, fails, facts, refusals = [], [], [], []
# OUR-CODE DEFECTS - Python exceptions raised by THIS SCRIPT. Kept in a SEPARATE list from `refusals`
# (Pre-decided 100 §2) so a bug of ours is never reported as "a mutator call the machine refused".
defects = []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "target": TARGET, "input": INPUT,
     "task": "STAGE M3a-2: the initial values of the two shift registers on WhileLoop #23032 - TWO rows "
             "(Pre-decided 91/92), written with connect_from_wire off wires 4185 and 3968, each accepted "
             "by the one-net test of Pre-decided 92/77, with the Pre-decided 94 type check in a separate "
             "ordered pass. The #637 register census is DELETED and CITED (Pre-decided 99, A3 + B4) and "
             "ExecState is neither gated nor claimed about - its cause is formally OPEN.",
     "pinned_astcheck": 'py tools/bench/c60c_astcheck.py <this file> --route owner   (Pre-decided 98(3); '
                        'route `owner` because this file never calls move_in - Pre-decided 62)',
     "verification_level": "STRUCTURAL, never functional (34(f))",
     "gating_policy": "Pre-decided 63 + the row gates: hygiene, the two row acceptance gates, the md5 "
                      "pins and the save. A negative MEASUREMENT is a FACT line. A row that never "
                      "happened is a FAIL.",
     "artefact_is_not_computation_equivalent":
         "AFTER M3a-2 THE ARTEFACT IS STILL NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL (Pre-decided 97). "
         "Both loops exist and the OLD one still feeds both downstream consumers. It is NEVER RUN.",
     "m3a3_named_not_wired": M3A3_CONSUMERS,
     "no_new_op": True, "no_new_verb": True, "no_new_device": True, "no_new_checker": True,
     "wire_sr_not_called": "wire_sr('LeftOutNode'/'LeftOutCtl') is called NOWHERE in this file "
                           "(Pre-decided 93: it cannot address a FlatSequenceInnerTunnel source)",
     "move_in_not_called": "this file calls move_in nowhere and imports it nowhere - hence --route owner",
     "remove_bad_wires_scripted": "not imported, not called (BANNED since cycle 58)",
     "no_whole_vi_gobject_census": True,
     "no_vi_run": "no D1 artefact and no main VI is run (34(f)); OP VIs are run - the fleet's mechanism",
     "rig_state": "assembled - no motor, no ASI, no camera; tools/motor_gate.py is not called",
     "edits_no_plan_document": True, "edits_no_status_next": True, "cycle_guard_off_never_set": True,
     "handles": {}, "hash_probe": [], "exec_state_timeline": [], "artefacts_on_disk": [],
     "purges": [], "rows": {}, "facts_from_imported_helpers":
         "find_node / terms_at / node_view / delete_by_uid print through build_d1_m3a1's fact(), so their "
         "lines are in THIS LOG but in build_d1_m3a1's in-memory facts list, not in this JSON. Their "
         "machine refusals are folded into H8 by reading build_d1_m3a1.refusals at both ends.",
     "build": {}}
K = R["build"]


class Halt(Exception):
    pass


# ============================================================================== the reporting primitives
def gate(name, ok, detail=""):
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def refusal(where, msg):
    """A MUTATOR CALL **THE MACHINE** REFUSED - the one class of negative result that gates (Pre-decided 63).

    ⚠️ CALL THIS ONLY WHEN LabVIEW DECLINED SOMETHING. A Python exception raised by this script is NOT a
    refusal: it is OUR defect, it goes to `defect()` and it is counted by H9, not H8 (Pre-decided 100 §2).
    """
    refusals.append({"where": where, "error_verbatim": msg})
    fact("MACHINE REFUSAL at %s: %s" % (where, msg))


def defect(where, exc):
    """A DEFECT IN OUR OWN PYTHON CODE - an exception raised by THIS SCRIPT, not by LabVIEW.

    ADDED 2026-09-22 (Pre-decided 100 §2). Until now `main()`'s bare handler routed ANY exception into
    `refusal()`, whose docstring calls it "a mutator call the machine refused" - so a `TypeError` in one
    of our own format strings was reported as a machine refusal by H8 while no mutator had been called.
    The two are now counted separately and this one names the exception type AND the source line.
    """
    import traceback as _tb
    frames = _tb.extract_tb(exc.__traceback__)
    site = ("%s:%d in %s()" % (os.path.basename(frames[-1].filename), frames[-1].lineno, frames[-1].name)
            if frames else "source line unavailable")
    rec = {"where": where, "exception_type": type(exc).__name__, "message": str(exc)[:300],
           "source_line": site, "raised_by": "OUR OWN PYTHON CODE, not the machine"}
    defects.append(rec)
    fact("OUR-CODE DEFECT at %s: %s: %s  RAISED AT %s - this is a BUG IN THIS SCRIPT. The machine "
         "refused NOTHING here (Pre-decided 100 SS2); it is counted by H9, never by H8."
         % (where, rec["exception_type"], rec["message"], site))
    return rec


def head(t):
    print("\n---------- %s" % t, flush=True)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def probe_hash(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["machine_refusals"] = refusals
    R["our_code_defects"] = defects
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T_START) - RESERVE_S


def read_es(tag):
    t0 = time.time()
    try:
        es = g.exec_state(TARGET)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    row = {"step": len(R["exec_state_timeline"]) + 1, "tag": tag, "exec_state": es,
           "wall_clock": time.strftime("%H:%M:%S"), "t_since_start_s": round(t0 - T_START, 1),
           "read_cost_s": round(time.time() - t0, 2)}
    R["exec_state_timeline"].append(row)
    # FIVE specs, FIVE arguments. `read_cost_s` was missing until 2026-09-22 and raised `TypeError: not
    # enough arguments for format string` in phase 1 of run 1 (Pre-decided 100 §1); `c60c_astcheck` gate 10
    # now reads this statically before the launch.
    fact("ExecState [%02d %s] = %r   (+%.1f s, read cost %.2f s) - NEVER a type discriminator (42(c)), "
         "NEVER substituted for the identity test (Pre-decided 70)"
         % (row["step"], tag, es, row["t_since_start_s"], row["read_cost_s"]))
    return es


def counts(tag, classes=("Node", "Wire", "LoopTunnel", "Tunnel", "LeftShiftRegister",
                         "RightShiftRegister")):
    """NARROW CLASS CENSUSES ONLY - never a whole-VI GObject census (six of those took the handle count
    34,602 -> 91,288)."""
    rec = {}
    for c in classes:
        rec[c], _ = safe("%s count(%r)" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    K.setdefault("censuses", {})[tag] = rec
    fact("%s counts: %r" % (tag, rec))
    return rec


# ============================================================ the uid-ECHOED readers (the A7 pattern)
def loop_index_of(uid, tag):
    """A loop_index is ECHOED from a freshly-read traverse list, NEVER carried between calls."""
    rows, err = safe("%s report_all('WhileLoop')" % tag, lambda: g.report_all(TARGET, "WhileLoop"), [])
    idx = next((r["i"] for r in (rows or []) if r["uid"] == uid), None)
    echo = next((r["uid"] for r in (rows or []) if r["i"] == idx), None) if idx is not None else None
    fact("%s A7 ECHO: report_all('WhileLoop')[%r].uid == %r (want #%d ; %d WhileLoop row(s))%s"
         % (tag, idx, echo, uid, len(rows or []), (" ; " + err) if err else ""))
    if echo != uid:
        refusal("%s loop_index echo" % tag,
                "report_all('WhileLoop')[%r].uid == %r, not #%d" % (idx, echo, uid))
        return None
    return idx


def reg_table(loop_index, tag, cap=REG_PROBE_MAX):
    """Every shift register of one loop, READ: the RIGHT register's uid/class/OUTER/INSIDE terminals and
    the same for its LEFT partner (`shift_reg_left` = OpShiftRegs_v1). Stops at the first slot that
    errors, and reports WHY it stopped - never silently."""
    out = []
    for k in range(cap):
        sr, err = safe("%s shift_reg_left(reg_index=%d)" % (tag, k),
                       lambda kk=k: g.shift_reg_left(TARGET, loop_index, kk))
        if err or not sr:
            fact("%s reg_index=%d -> READ STOPS HERE: %s" % (tag, k, err or "no row returned"))
            break
        left = sr.get("left") or {}
        row = {"reg_index": k, "right_uid": sr.get("uid"), "right_class": sr.get("class"),
               "right_out": sr.get("out"), "right_inside": sr.get("inside"),
               "left_uids": sr.get("left_uids"), "left_uid": left.get("uid"),
               "left_class": left.get("class"), "left_out": left.get("out"),
               "left_inside": left.get("inside"), "op_errors": sr.get("errors")}
        out.append(row)
        fact("%s reg%-2d RIGHT #%-6r %-20r outer=%r inside=%r | LEFT #%-6r %-19r outer=%r inside=%r | "
             "errors=%r" % (tag, k, row["right_uid"], row["right_class"], row["right_out"],
                            row["right_inside"], row["left_uid"], row["left_class"], row["left_out"],
                            row["left_inside"], row["op_errors"]))
        if row["op_errors"] or row["right_uid"] in (None, 0):
            break
    return out


def bare_terminals_of(tbl):
    """Flatten a register table into one row per TERMINAL, marking the bare ones. `wire` 0 = bare; an
    uninitialised register's LEFT OUTER terminal is legitimately bare (gscript.py:788)."""
    flat = []
    for r in tbl:
        for side, uid, cls, o, ins in (
                ("RIGHT", r["right_uid"], r["right_class"], r["right_out"], r["right_inside"]),
                ("LEFT", r["left_uid"], r["left_class"], r["left_out"], r["left_inside"])):
            if o is not None:
                flat.append({"reg_index": r["reg_index"], "side": side, "uid": uid, "class": cls,
                             "terminal": "OUTER", "name": o.get("name"),
                             "is_source": o.get("is_source"), "wire": o.get("wire") or 0})
            for k, t in enumerate(ins or []):
                flat.append({"reg_index": r["reg_index"], "side": side, "uid": uid, "class": cls,
                             "terminal": "INSIDE[%d]" % k, "name": t.get("name"),
                             "is_source": t.get("is_source"), "wire": t.get("wire") or 0})
    return flat


def pd85_violations(wire_uid, walk):
    """PRE-DECIDED 85, THE READER PRECONDITION. Before any assertion built on an `OpWireSource_v5` walk
    can be believed, EVERY row with a REAL owner must satisfy `recip == queried_uid`. Rows with
    owner_uid 0 are the reader's NULL PADDING and are excluded (measured, diag_c68_pd86.log)."""
    return [t for t in (walk or []) if t.get("owner_uid") and t.get("recip") != wire_uid]


def wire_walk(tag, wire_uid):
    """`OpWireSource_v5(UID 2 = wire_uid)` on the LIVE target, printed terminal by terminal, with the
    Pre-decided 85 precondition reported per walk. A bare terminal has no wire to walk - that is a FACT,
    not an error."""
    if not wire_uid:
        fact("%s wire 0 - the terminal is BARE, there is no wire to walk" % tag)
        return [], ""
    walk, err = safe("%s OpWireSource_v5(UID 2 = %r)" % (tag, wire_uid),
                     lambda: WIRE_TERMS(TARGET, int(wire_uid), n=8), [])
    real = [t for t in (walk or []) if t.get("owner_uid")]
    fact("%s OpWireSource_v5(UID 2 = %r): %d row(s), %d with a REAL owner%s"
         % (tag, wire_uid, len(walk or []), len(real), (" ; " + err) if err else ""))
    for t in (walk or []):
        fact("    %s   t%-2r is_source=%-5r owner_class=%-26r owner_uid=%-7r recip=%r%s"
             % (tag, t.get("i"), t.get("is_source"), t.get("owner_class"), t.get("owner_uid"),
                t.get("recip"), ("  READ ERROR " + str(t["err"])) if t.get("err") else ""))
    bad = pd85_violations(wire_uid, walk)
    fact("%s PD85 PRECONDITION: %d real-owner row(s), %d violate recip==queried_uid%s"
         % (tag, len(real), len(bad),
            (" -> %r - THIS WALK IS NOT BELIEVED (Pre-decided 85)"
             % [(t.get("i"), t.get("owner_class"), t.get("owner_uid"), t.get("recip")) for t in bad])
            if bad else ""))
    K.setdefault("pd85_checks", []).append({"tag": tag, "wire": wire_uid, "real_rows": len(real),
                                            "violations": len(bad)})
    return walk or [], err


def purge_junk(nodes_before, tag, hints):
    """The measured junk shape of `OpConnectFromWire_v0`: a fresh `Invoke` node with ZERO wired terminals.
    Anything else that is new is REPORTED VERBATIM and LEFT ALONE - deleting a node whose terminal table
    was never read is the one branch that could destroy the artefact. (The body is build_d1_m3a1's
    `census_and_purge` logic; that function itself is NOT imported, because it writes M3a-1's own JSON.)"""
    nodes_after, _ = M.node_census(TARGET, "%s AFTER" % tag)
    fresh = M.new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh], "deleted": [],
           "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        loc, rows = M.node_view(TARGET, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "terminals": rows, "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s the junk node's FULL terminal table is printed above; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = M.delete_by_uid(TARGET, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape, or its table could not be read): "
                 "#%s class %r label %r, %d terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    final = nodes_after
    if rec["deleted"]:
        final, _ = M.node_census(TARGET, "%s AFTER THE PURGE" % tag)
        fact("%s purge arithmetic: Node %d -> %d -> %d"
             % (tag, len(nodes_before), len(nodes_after), len(final)))
    rec["node_count_after_purge"] = len(final)
    R["purges"].append(rec)
    dump()
    return final, rec


# ======================================================================= [0] files only, zero LabVIEW
def phase_0():
    head("[0] FILES ONLY, ZERO LabVIEW - the md5 pins BEFORE, then the pre-batch restart")
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500; the pre-batch restart below is "
         "MANDATORY - 44(e))" % R["handles"]["before"])
    pr = probe_hash("H INPUT the M3a-1 artefact BEFORE", INPUT)
    gate("H1 the input artefact's md5 == its pin %s" % INPUT_MD5[:8], pr.get("md5") == INPUT_MD5,
         "%r" % (pr.get("md5"),))
    R["input_md5_before"] = pr.get("md5")
    R["input_size_before"] = pr.get("size")
    for tag, path, pin in PINS:
        pr = probe_hash("H %s BEFORE" % tag, path)
        gate("H3 %s md5 == its pin %s" % (tag, pin[:8]), pr.get("md5") == pin, "%r" % (pr.get("md5"),))
    K["tool_pins_before"] = {}
    for p in TOOL_PINS:
        pr = probe_hash("H TOOL %s BEFORE" % os.path.basename(p), p)
        K["tool_pins_before"][p] = pr.get("md5")
    K["m3a1_refusals_at_entry"] = len(M.refusals)
    for c in M3A3_CONSUMERS:
        fact("M3a-3, NAMED AND NOT WIRED BY THIS STAGE (Pre-decided 91): the OLD RIGHT OUTER #%d -> wire "
             "%d -> %s stays exactly as it is; re-sourcing it from the NEW register #%d is M3a-3, and "
             "leaving the new RIGHT OUTER bare drops nothing (a bare SOURCE is legal LabVIEW, PD 69)"
             % (c["old_right_outer"], c["wire"], c["consumer"], c["new_right_outer"]))
    D.fresh("[0] pre-batch LabVIEW restart (44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])
    dump()


# ============================================== [1] the target copy and the pre-write FACT census
def phase_1_copy():
    head("[1] THE TARGET IS A COPY OF THE INPUT - the input is never opened, never edited, never run")
    shutil.copy2(INPUT, TARGET)
    time.sleep(0.4)
    pr = probe_hash("[1] the target, straight after the copy", TARGET)
    gate("H4 the target starts byte-identical to the input artefact", pr.get("md5") == INPUT_MD5,
         "%r vs %r" % (pr.get("md5"), INPUT_MD5))
    fact("[1] the target is %s - the STAGE'S OWN OUTPUT NAME; every edit below is made on THIS file and "
         "the input artefact is not touched again until H2 re-reads its md5" % os.path.basename(TARGET))
    t0 = time.time()
    _, err = safe("[1] ensure_loaded(target)", lambda: g.ensure_loaded(TARGET))
    fact("[1] ensure_loaded(target) took %.1f s%s (edits are SILENTLY DECLINED on a target that is not "
         "fully loaded - the measured cause of add_shift_reg's no-op, gscript.py:764)"
         % (time.time() - t0, (" ERROR " + err) if err else ""))
    read_es("[1] the target, COLD")
    K["counts_before"] = counts("[1] COLD")
    di, derr = safe("[1] diag_index(#%d)" % D686, lambda: diag_index(TARGET, D686))
    K["d686_index"] = di
    fact("[1] Diagram #%d -> traverse index %r%s (the diagram that carries BOTH loop borders and all "
         "four wires - measured by diag_c73, RE-RESOLVED here)" % (D686, di, (" ; " + derr) if derr else ""))
    if di is None:
        raise Halt("Diagram #%d does not resolve on the target" % D686)
    dump()
    return [di, TOP]


def cite_pd95_withdrawn():
    """A3 + B4 (Pre-decided 99), ACCEPTED: THE #637 REGISTER CENSUS IS DELETED FROM THIS RECIPE AND
    REPLACED BY THIS CITATION. It is already measured on a byte-identical artefact, and it cannot
    answer the question it was added for. One line, no COM call, no handle cost."""
    head("[95] THE OLD LOOP #637 REGISTER CENSUS - DELETED, CITED (Pre-decided 99, A3 + B4)")
    fact("[95] CITATION, not a measurement: `tools/bench/diag_c73_m3a2_rows.log:42-57` already "
         "censused loop #637 on a BYTE-IDENTICAL artefact (md5 6b3c1f3c...) - it reads 15 slots, not "
         "14 (slot 14 is the probe past the end, error 1055), and :43-44 show #4256 INSIDE on wire "
         "9113 and #4334 INSIDE on wire 7337, i.e. NOT bare. Pre-decided 95's named 'severed inside "
         "terminal' candidate is therefore WITHDRAWN, and a wire-uid census cannot see "
         "'shift-register terminal unwired' in any case (Pre-decided 89).")
    fact("[95] ExecState 0's CAUSE IS FORMALLY OPEN and is not answerable with the readers this "
         "fleet owns (`VI.Get Errors` 452 is absent from the exported ActiveX interface). This "
         "recipe does NOT gate on ExecState and claims NOTHING about it; 95's surviving half is the "
         "operative one - M3a-2 is not required to reach ExecState 1 and is not judged on it.")
    K["pd95_census"] = {"status": "DELETED from the recipe (Pre-decided 99, A3 + B4)",
                        "citation": "tools/bench/diag_c73_m3a2_rows.log:42-57",
                        "slots_read": 15,
                        "execstate_0_cause": "OPEN - not answerable with this fleet's readers"}
    dump()


def phase_1_loop_a(tag, hints):
    """The NEW loop's registers and the loop node's FULL terminal table - the table the sink index is read
    from. FACT ONLY: it is the raw material of the sink resolution, which has its own gate."""
    head("[A %s] THE NEW LOOP #%d - its two registers and its full border terminal table" % (tag, LOOP_A))
    rec = {"tag": tag}
    li = loop_index_of(LOOP_A, "[A %s]" % tag)
    rec["loop_index"] = li
    if li is not None:
        tbl = reg_table(li, "[A %s] loop#%d" % (tag, LOOP_A))
        rec["registers"] = tbl
        flat = bare_terminals_of(tbl)
        rec["bare"] = [t for t in flat if not t["wire"]]
        fact("[A %s] loop #%d carries %d register(s); RIGHT uids %r ; LEFT uids %r ; %d bare terminal(s) "
             "%r" % (tag, LOOP_A, len(tbl), [r["right_uid"] for r in tbl],
                     [r["left_uid"] for r in tbl], len(rec["bare"]),
                     [(b["side"], b["uid"], b["terminal"]) for b in rec["bare"]]))
    loc, rows = M.node_view(TARGET, LOOP_A, hints, "[A %s] the loop border #%d" % (tag, LOOP_A))
    rec["border_diagram_uid"] = (loc.get("found") or {}).get("diagram_uid")
    rec["border_nodes_index"] = (loc.get("found") or {}).get("nodes_index")
    rec["border_terminals"] = rows
    fact("[A %s] the loop border #%d sits on Diagram #%r at Nodes[%r] with %d terminal(s); is that #%d? %r"
         % (tag, LOOP_A, rec["border_diagram_uid"], rec["border_nodes_index"], len(rows), D686,
            rec["border_diagram_uid"] == D686))
    K.setdefault("loop_a", {})[tag] = rec
    dump()
    return rec


# ================================================================================ [2] ONE ROW
def resolve_sink(row, hints, tag):
    """THE SINK INDEX IS RE-READ ON THE LIVE TARGET, never carried from a census (T2c2's recorded cause of
    failure). Two independent readings must agree:
      (i)  `shift_reg_left` names the LEFT register's uid and its OUTER terminal's name / is_source / wire;
      (ii) the loop BORDER node's `Terminals[]` table carries that same terminal as a row with an INDEX -
           and an index is what `connect_from_wire` needs, because it addresses
           Diagram[d].Nodes[n].Terminals[t].
    The row is selected by (name, is_source False, BARE) and must be UNIQUE. Anything else - zero
    candidates, two candidates, a left uid that is not the predicted one - STOPS THE ROW. Nothing is
    substituted and no index is guessed (Pre-decided 68).

    A4 (prior-art finding `unread-evidence`, Pre-decided 99), ACCEPTED - THE UNREAD EVIDENCE, NOW
    CITED: `tools/bench/build_d1_routeb_v0_run2.log:467-468` already measured bare register
    terminals on this same `Diagram #686`, with the register terminals INTERLEAVED AT ODD INDICES -
        BARE  diagram 19 #686 Diagram[19] Nodes[22].T[1] 'position [internal units]'
        BARE  diagram 19 #686 Diagram[19] Nodes[22].T[3] 'VISA out'
    So an ODD `Terminals[]` index is the EXPECTATION for this sink. It is an expectation logged as
    a FACT beside the index actually found, NEVER a criterion and NEVER a value carried into the
    write: the index used is resolved LIVE, by register uid, on this run's own target. Carrying an
    index from a census is the recorded cause of T2c2's failure."""
    rec = {"predicted_left_uid": row["left_uid"], "name": row["reg_name"]}
    li = loop_index_of(LOOP_A, "%s sink" % tag)
    rec["loop_index"] = li
    if li is None:
        rec["stop"] = "the loop index did not echo"
        return rec
    tbl = reg_table(li, "%s sink loop#%d" % (tag, LOOP_A))
    hit = next((r for r in tbl if r["right_uid"] == row["right_uid"]), None)
    rec["reg_row"] = hit
    if hit is None:
        rec["stop"] = ("RightShiftRegister #%d is not in the live register table (right uids %r)"
                       % (row["right_uid"], [r["right_uid"] for r in tbl]))
        return rec
    rec["left_uid_live"] = hit["left_uid"]
    rec["left_uid_matches_prediction"] = (hit["left_uid"] == row["left_uid"])
    lo = hit["left_out"] or {}
    rec["left_outer_reading"] = lo
    fact("%s SINK (i) shift_reg_left: reg_index %d, RIGHT #%r, LEFT #%r (predicted #%d, match %r); the "
         "LEFT OUTER terminal reads name=%r is_source=%r wire=%r  <- THE INITIAL-VALUE SINK"
         % (tag, hit["reg_index"], hit["right_uid"], hit["left_uid"], row["left_uid"],
            rec["left_uid_matches_prediction"], lo.get("name"), lo.get("is_source"), lo.get("wire")))
    if not rec["left_uid_matches_prediction"]:
        rec["stop"] = ("the LIVE left register uid is #%r, not the predicted #%d - the row STOPS rather "
                       "than wire a register this stage cannot name" % (hit["left_uid"], row["left_uid"]))
        return rec
    if lo.get("wire"):
        rec["stop"] = ("the LEFT OUTER terminal already carries wire %r - it is NOT bare, so this row has "
                       "already been written or the register is fed from somewhere else. Nothing is "
                       "overwritten." % lo.get("wire"))
        return rec
    loc, rows = M.node_view(TARGET, LOOP_A, hints, "%s sink border #%d" % (tag, LOOP_A))
    f = loc.get("found") or {}
    rec["sink_diag_index"] = f.get("diagram_index")
    rec["sink_diag_uid"] = f.get("diagram_uid")
    rec["sink_nodes_index"] = f.get("nodes_index")
    rec["border_terminal_count"] = len(rows)
    cands = [t for t in rows if t.get("name") == row["reg_name"] and t.get("is_source") is False
             and M.term_state(t) == "BARE"]
    rec["candidates"] = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t)) for t in cands]
    same_name = [(t["i"], t["name"], t["is_source"], t["wire"], M.term_state(t))
                 for t in rows if t.get("name") == row["reg_name"]]
    rec["all_same_name_rows"] = same_name
    fact("%s SINK (ii) the loop border's Terminals[] table has %d row(s); %d named %r -> %r ; of those %d "
         "are BARE SINKS -> %r" % (tag, len(rows), len(same_name), row["reg_name"], same_name,
                                   len(cands), rec["candidates"]))
    if len(cands) != 1:
        rec["stop"] = ("the LEFT OUTER terminal is not UNIQUELY addressable on the border node: %d bare "
                       "sink row(s) named %r among %d terminal(s). No index is guessed and nothing is "
                       "wired." % (len(cands), row["reg_name"], len(rows)))
        return rec
    rec["sink_term_index"] = cands[0]["i"]
    rec["sink_terminal_before"] = cands[0]
    fact("%s SINK RESOLVED on the LIVE target: Diagram idx %r (uid #%r) . Nodes[%r] . Terminals[%r] - the "
         "LEFT register #%d's OUTER terminal, name %r, is_source %r, BARE"
         % (tag, rec["sink_diag_index"], rec["sink_diag_uid"], rec["sink_nodes_index"],
            rec["sink_term_index"], row["left_uid"], cands[0]["name"], cands[0]["is_source"]))
    # A4 (Pre-decided 99): the index FOUND, logged beside the odd-index EXPECTATION taken from the
    # evidence that had never been read. An output, never a criterion - the row is not stopped by it.
    ti = rec["sink_term_index"]
    rec["index_is_odd"] = (isinstance(ti, int) and ti % 2 == 1)
    rec["odd_index_expectation"] = ("build_d1_routeb_v0_run2.log:467-468 - bare register terminals "
                                    "on Diagram #686 sit at ODD Terminals[] indices "
                                    "(Nodes[22].T[1] 'position [internal units]', T[3] 'VISA out')")
    fact("%s SINK INDEX FACT (A4): the index resolved LIVE BY REGISTER UID #%d is Terminals[%r]; "
         "odd? %r. EXPECTATION from the previously unread evidence "
         "`tools/bench/build_d1_routeb_v0_run2.log:467-468` (Diagram[19] #686 Nodes[22].T[1] "
         "'position [internal units]' / T[3] 'VISA out') is an ODD index. This is an OUTPUT, never a "
         "criterion, and no index is ever carried from a census (T2c2's recorded cause of failure)."
         % (tag, row["left_uid"], ti, rec["index_is_odd"]))
    return rec


def resolve_source(row, tag):
    """THE SOURCE IS MEASURED ON THE LIVE TARGET IMMEDIATELY BEFORE THE WRITE (Pre-decided 68). An empty
    walk is a FACT line and THE ROW STOPS - nothing is wired, nothing is substituted, no Local (rule 1a).
    Pre-decided 77: ALL `is_source=True` terminals are counted, of EVERY owner class, BEFORE any filter."""
    rec = {"wire": row["source_wire"], "predicted_owner": row["source_owner"]}
    walk, err = wire_walk("%s SOURCE wire %d IMMEDIATELY BEFORE THE WRITE" % (tag, row["source_wire"]),
                          row["source_wire"])
    rec["walk"] = walk
    rec["walk_error"] = err
    rec["pd85_violations"] = len(pd85_violations(row["source_wire"], walk))
    srcs = [t for t in walk if t.get("is_source") and t.get("owner_uid")]
    rec["all_source_terminals"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid")) for t in srcs]
    rec["sinks_before"] = [(t.get("i"), t.get("owner_class"), t.get("owner_uid")) for t in walk
                           if t.get("owner_uid") and t.get("is_source") is False]
    fact("%s SOURCE wire %d: %d source terminal(s) OF ANY CLASS %r ; %d sink terminal(s) %r ; PD85 "
         "violations %d" % (tag, row["source_wire"], len(srcs), rec["all_source_terminals"],
                            len(rec["sinks_before"]), rec["sinks_before"], rec["pd85_violations"]))
    if not srcs:
        rec["stop"] = ("wire %d came back with NO source terminal on the live target. Nothing is wired, "
                       "nothing is substituted (Pre-decided 68)." % row["source_wire"])
        return rec
    if len(srcs) != 1:
        rec["stop"] = ("wire %d has %d source terminals %r - the prediction is exactly ONE, and a row "
                       "whose source is ambiguous is not written." % (row["source_wire"], len(srcs),
                                                                      rec["all_source_terminals"]))
        return rec
    if rec["pd85_violations"]:
        rec["stop"] = ("the source walk violates the Pre-decided 85 reader precondition (%d row(s) whose "
                       "recip is not the queried uid) - this walk is NOT believed, so the row is not "
                       "written on it." % rec["pd85_violations"])
        return rec
    one = srcs[0]
    rec["term_index"] = one["i"]
    rec["owner_uid"] = one.get("owner_uid")
    rec["owner_class"] = one.get("owner_class")
    rec["owner_matches_prediction"] = (one.get("owner_uid") == row["source_owner"])
    fact("%s SOURCE RESOLVED: wire %d Terms[%r], owner %r #%r (predicted #%d, match %r)"
         % (tag, row["source_wire"], one["i"], one.get("owner_class"), one.get("owner_uid"),
            row["source_owner"], rec["owner_matches_prediction"]))
    if not rec["owner_matches_prediction"]:
        rec["stop"] = ("the ONE source terminal of wire %d is owned by #%r, not the predicted #%d. A "
                       "differently-owned source is a DIFFERENT VALUE (rule 1a) - the row STOPS."
                       % (row["source_wire"], one.get("owner_uid"), row["source_owner"]))
    return rec


def acceptance(row, tag, when, sink_wire, mandatory):
    """PRE-DECIDED 92, THE WHOLE ACCEPTANCE TEST, READ OFF THE MACHINE AND NOTHING ELSE.
      (1) the wire carried by the NEW SINK terminal has EXACTLY ONE source terminal OF ANY OWNER CLASS
          (Pre-decided 77 - every class is counted BEFORE any filter; the recorded pathology is broken
          wire w1231, whose two is_source terminals are of DIFFERENT classes and which a class filter
          would have reduced to one);
      (2) that one terminal's owner is the predicted source (#4194 / #3974);
      (3) the ORIGINAL sink (#4344 OUTER / #4274 OUTER) is STILL a terminal of that net - the rule-1a
          invariant: this row BRANCHES the initial-value net, it does not steal it;
      (4) the walk has ZERO Pre-decided 85 violations, or it is not believed at all.
    `ExecState`, `wire_delta` and `Is Broken?` are NEVER substituted for this test."""
    walk, err = wire_walk("%s ACCEPTANCE %s - the SINK net %r" % (tag, when, sink_wire), sink_wire)
    all_src = [t for t in walk if t.get("is_source") and t.get("owner_uid")]
    classes = [(t.get("owner_class"), t.get("owner_uid")) for t in all_src]
    the_one = all_src[0] if len(all_src) == 1 else None
    owners = [t.get("owner_uid") for t in walk if t.get("owner_uid")]
    bad = pd85_violations(sink_wire, walk)
    rec = {"tag": tag, "when": when, "sink_wire": sink_wire, "walk_error": err,
           "ALL_source_terminals": classes, "ALL_source_terminal_count": len(all_src),
           "the_one_is_the_predicted_source": bool(the_one is not None
                                                   and the_one.get("owner_uid") == row["source_owner"]),
           "original_sink_still_on_the_net": row["original_sink"] in owners,
           "every_owner_on_the_net": sorted({int(o) for o in owners}),
           "pd85_violations": len(bad),
           "counted_before_filtering": "Pre-decided 77 - every owner class is counted before any filter"}
    ok = (bool(sink_wire) and len(all_src) == 1 and rec["the_one_is_the_predicted_source"]
          and rec["original_sink_still_on_the_net"] and not bad)
    rec["pass"] = ok
    fact("%s ACCEPTANCE %s: sink net %r has %d source terminal(s) of ANY class %r (want exactly 1, owned "
         "by #%d) ; the ORIGINAL sink #%d is on the net: %r ; every owner on the net %r ; PD85 violations "
         "%d" % (tag, when, sink_wire, len(all_src), classes, row["source_owner"], row["original_sink"],
                 rec["original_sink_still_on_the_net"], rec["every_owner_on_the_net"], len(bad)))
    if mandatory:
        gate("%s ROW ACCEPTANCE %s (Pre-decided 92): ONE source of any class == #%d, and the ORIGINAL "
             "sink #%d is still on the net" % (tag, when, row["source_owner"], row["original_sink"]), ok,
             "sink wire %r ; sources %r ; original sink on net %r ; PD85 %d"
             % (sink_wire, classes, rec["original_sink_still_on_the_net"], len(bad)))
    K.setdefault("acceptance", []).append(rec)
    return rec


def sink_row_now(row, sink, hints, tag, when):
    """RE-LOCATE the sink terminal on the LIVE target. An index is NEVER carried across a mutation: a
    border write can add a terminal to the loop node (M3a-1 measured `loop_23032_terminals` 5 -> 6 on its
    t1 row), which renumbers `Terminals[]`. So the terminal is found again BY NAME among the border's sink
    rows, and the index it lands at is compared against the stored one and reported either way. The stored
    index is used only when the by-name reading is not unique, and that case is stated in the log."""
    rec = {"when": when, "stored_index": sink.get("sink_term_index")}
    loc, rows = M.node_view(TARGET, LOOP_A, hints, "%s sink %s" % (tag, when), quiet=True)
    rec["nodes_index"] = (loc.get("found") or {}).get("nodes_index")
    rec["diagram_index"] = (loc.get("found") or {}).get("diagram_index")
    rec["diagram_uid"] = (loc.get("found") or {}).get("diagram_uid")
    rec["border_terminal_count"] = len(rows)
    named = [t for t in rows if t.get("name") == row["reg_name"] and t.get("is_source") is False]
    rec["named_sink_rows"] = [(t["i"], t["name"], t["wire"], M.term_state(t)) for t in named]
    if len(named) == 1:
        hit, rec["how"] = named[0], "BY NAME (unique among the border's sink rows)"
    else:
        hit = next((t for t in rows if t["i"] == rec["stored_index"]), None)
        rec["how"] = ("BY THE STORED INDEX - the by-name reading was not unique (%d row(s) named %r)"
                      % (len(named), row["reg_name"]))
    rec["term_index"] = (hit or {}).get("i")
    rec["name"] = (hit or {}).get("name")
    rec["wire"] = (hit or {}).get("wire") or 0
    rec["index_moved"] = (rec["term_index"] != rec["stored_index"])
    fact("%s the sink terminal %s: Nodes[%r].Terminals[%r] (stored index %r ; moved %r), name %r, carries "
         "wire %r ; the border now has %d terminal(s) ; rows named %r -> %r"
         % (tag, when, rec["nodes_index"], rec["term_index"], rec["stored_index"], rec["index_moved"],
            rec["name"], rec["wire"], len(rows), row["reg_name"], rec["named_sink_rows"]))
    return rec


def one_row(row, hints):
    tag = "[ROW %s]" % row["tag"]
    head("%s %s -> LEFT register #%d OUTER, off wire %d (source #%d)"
         % (tag, row["reg_name"], row["left_uid"], row["source_wire"], row["source_owner"]))
    fact("%s WHY: %s" % (tag, row["why"]))
    rec = {"row": row, "writer": "connect_from_wire / OpConnectFromWire_v0.vi "
                                 "(docs/toolkit-capabilities.md:70) - Pre-decided 93",
           "never_a_local": "a Local is NEVER substituted for this row (rule 1a)"}
    R["rows"][row["tag"]] = rec

    sink = resolve_sink(row, hints, tag)
    rec["sink"] = sink
    src = resolve_source(row, tag)
    rec["source"] = src
    stop = sink.get("stop") or src.get("stop")
    if stop:
        rec["result"] = "ROW STOPPED BEFORE THE WRITE: %s" % stop
        fact("%s *** %s Nothing was wired and nothing was substituted (Pre-decided 68). ***"
             % (tag, rec["result"]))
        gate("%s ROW ACCEPTANCE (Pre-decided 92) - the row was WRITTEN at all" % tag, False, stop)
        dump()
        return rec

    nodes_before, _ = M.node_census(TARGET, "%s before the write" % tag)
    before = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        before[c], _ = safe("%s count(%r) before" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_before"] = before
    fact("%s baselines before the write: %r" % (tag, before))

    t0 = time.time()
    try:
        dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, row["source_wire"], src["term_index"],
                                             sink["sink_diag_index"], sink["sink_nodes_index"],
                                             sink["sink_term_index"], CFW_LABELS)
        rec["connect"] = {"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250],
                          "op_readback": sub}
        if err:
            refusal("%s connect_from_wire" % tag, str(err)[:250])
    except Exception as e:                                                         # noqa: BLE001
        rec["connect"] = {"call_error": "%s: %s" % (type(e).__name__, str(e)[:250])}
        refusal("%s connect_from_wire(wire %d t%r -> D[%r].N[%r].T[%r])"
                % (tag, row["source_wire"], src["term_index"], sink["sink_diag_index"],
                   sink["sink_nodes_index"], sink["sink_term_index"]), rec["connect"]["call_error"])
    rec["call_cost_s"] = round(time.time() - t0, 2)
    fact("%s connect_from_wire(wire=%d, wire_term=%r, sink_diag=%r, sink_node=%r, sink_term=%r) -> %r "
         "(%.2f s)" % (tag, row["source_wire"], src["term_index"], sink["sink_diag_index"],
                       sink["sink_nodes_index"], sink["sink_term_index"], rec["connect"],
                       rec["call_cost_s"]))
    fact("%s *** THE OP'S OWN `Is Broken?` READBACK IS %r. IT IS A FACT OF THE WRITE PASS AND IT IS NOT "
         "THE TYPE CHECK (Pre-decided 94): the type check is the SEPARATE ORDERED PASS at [94] below, and "
         "only that one. ***" % (tag, (rec["connect"].get("op_readback") or {}).get("Is Broken?")))

    after = {}
    for c in ("Wire", "LoopTunnel", "Tunnel"):
        after[c], _ = safe("%s count(%r) after" % (tag, c), lambda cc=c: g.count(TARGET, cc))
    rec["counts_after"] = after
    fact("%s counts %r -> %r (wire_delta %r) - FACT lines, never the acceptance test (Pre-decided 70)"
         % (tag, before, after, (rec["connect"] or {}).get("wire_delta")))

    # ---- ACCEPTANCE (a): immediately after the write, BEFORE the purge (the purge deletes objects).
    s_a = sink_row_now(row, sink, hints, tag, "IMMEDIATELY AFTER THE WRITE")
    rec["sink_after_write"] = s_a
    rec["acceptance_after_write"] = acceptance(row, tag, "(a) IMMEDIATELY AFTER THE WRITE",
                                               s_a["wire"], True)

    # ---- the junk purge, then ACCEPTANCE (b) on the state the artefact actually keeps.
    _nodes, purge = purge_junk(nodes_before, "%s after the write" % tag, hints)
    rec["purge"] = {"new_uids": purge["new_uids"], "deleted": [d["uid"] for d in purge["deleted"]],
                    "reported_not_deleted": [d["uid"] for d in purge["reported_not_deleted"]]}
    s_b = sink_row_now(row, sink, hints, tag, "AFTER THE JUNK PURGE")
    rec["sink_after_purge"] = s_b
    rec["acceptance_after_purge"] = acceptance(row, tag, "(b) AFTER THE JUNK PURGE", s_b["wire"], True)
    rec["result"] = "WRITTEN"
    dump()
    return rec


# ======================================================== [94] THE TYPE CHECK, A SEPARATE ORDERED PASS
def phase_type_check(hints):
    """PRE-DECIDED 94, AND THIS IS THE SHAPE 42 VALIDATED. `Wire.Is Broken?` is read ONLY here: an
    ordered, idempotent RE-CONNECT of each row that has already been written, whose `wire_delta` is
    expected to be 0 because the connection already exists. Both rows are BRANCHES of an existing net read
    in a separate ordered pass - 42(d)'s binding-scope limit, met exactly, so the instrument is used where
    it was validated and not where it was not. These are FACT lines: the acceptance of a row is Pre-decided
    92's one-net test, never this reading (Pre-decided 89 - `Is Broken?` reports WIRE state only)."""
    head("[94] THE TYPE CHECK - `Wire.Is Broken?` READ IN A SEPARATE ORDERED PASS, NEVER IN THE WRITE PASS")
    K["type_check"] = []
    for row in ROWS:
        tag = "[94 %s]" % row["tag"]
        rec = {"row": row["tag"]}
        st = R["rows"].get(row["tag"]) or {}
        if st.get("result") != "WRITTEN":
            rec["skipped"] = "the row was not written, so there is nothing to re-connect"
            fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
            K["type_check"].append(rec)
            continue
        sink = st["sink"]
        src = resolve_source(row, "%s re-measure" % tag)
        rec["source"] = {k: src.get(k) for k in ("term_index", "owner_uid", "owner_class", "stop")}
        if src.get("stop"):
            rec["skipped"] = "the source no longer resolves: %s" % src["stop"]
            fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
            K["type_check"].append(rec)
            continue
        # The SINK INDEX IS RE-READ HERE TOO - never carried across the other row's mutation.
        now = sink_row_now(row, sink, hints, tag, "AT THE TYPE CHECK")
        rec["sink"] = now
        if now.get("term_index") is None:
            rec["skipped"] = "the sink terminal no longer resolves on the live target"
            fact("%s SKIPPED - %s" % (tag, rec["skipped"]))
            K["type_check"].append(rec)
            continue
        wires_before, _ = safe("%s count('Wire') before" % tag, lambda: g.count(TARGET, "Wire"))
        try:
            dw, es, err, sub = CONNECT_FROM_WIRE(TARGET, row["source_wire"], src["term_index"],
                                                 now["diagram_index"], now["nodes_index"],
                                                 now["term_index"], CFW_LABELS)
            rec.update({"wire_delta": dw, "exec_state": es, "op_error": str(err)[:250],
                        "is_broken": (sub or {}).get("Is Broken?"), "uid_2": (sub or {}).get("UID 2"),
                        "name": (sub or {}).get("Name")})
        except Exception as e:                                                     # noqa: BLE001
            rec["call_error"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            fact("%s the idempotent re-connect raised %s" % (tag, rec["call_error"]))
            K["type_check"].append(rec)
            continue
        wires_after, _ = safe("%s count('Wire') after" % tag, lambda: g.count(TARGET, "Wire"))
        rec["wire_census"] = [wires_before, wires_after]
        rec["idempotent"] = (rec.get("wire_delta") == 0)
        fact("%s IDEMPOTENT RE-CONNECT: wire_delta %r (expected 0 - the connection already exists) ; Wire "
             "census %r -> %r ; `Wire.Is Broken?` = %r ; the op's `UID 2` = %r ; `Name` = %r ; op error %r"
             % (tag, rec.get("wire_delta"), wires_before, wires_after, rec.get("is_broken"),
                rec.get("uid_2"), rec.get("name"), rec.get("op_error")))
        # 🔴 THIS GUARD IS WRONG FOR THE `OpConnect*` FAMILY - REVERSED 2026-09-22 16:1x (prior-art
        # `archive/peer/2026-09-22-priorart-c87b-rowd-clean.md` B1, ACCEPTED; the identical pair sits at
        # `tools/recipes/build_d1_m3a3.py:1432`, where the full reasoning and the measured consequence are
        # written). In short: the stray `Invoke` is minted by the CALL, not by the wire delta (1.00 per
        # call, `tools/stagekit.py:467-468`), so an IDEMPOTENT second pass mints one and this `if` skips
        # the purge. `tools/recipes/stage_d1_m3a3_rowD.py` purges UNCONDITIONALLY instead. This file is a
        # delivered stage's record and is not re-run, so the code is left exactly as it ran (34(h)).
        if not rec["idempotent"]:
            fact("%s *** wire_delta is NOT 0, so this pass CHANGED the diagram instead of re-reading it. "
                 "That is reported, and the junk census below runs. It does not retroactively alter the "
                 "row's acceptance, which was measured on the state the row left. ***" % tag)
            nodes_now, _ = M.node_census(TARGET, "%s after a non-idempotent re-connect" % tag)
            purge_junk(nodes_now, "%s re-connect" % tag, hints)
        K["type_check"].append(rec)
        dump()
    return K["type_check"]


# ==================================================================================== [S] THE SAVE
def phase_save():
    """PRE-DECIDED 96 - THE STAGE ALWAYS LEAVES A FILE. `ExecState` 1 => an ordinary SaveInstrument;
    otherwise `save(allow_broken=True)` diverts to the `gui_save` route with USER RULE 17:5x in full:
    locate in a capture taken just before, act, and confirm after. For a SAVE the after-confirmation is
    THE FILE ITSELF - size and md5 read back off disk and required to differ from the input - with the
    saved path verified to be the claudeDev target and all four md5 pins re-read at [H]."""
    head("[S] THE SAVE - the stage always leaves a file (Pre-decided 88/96)")
    rec = {"dest": TARGET, "save_error_verbatim": "",
           "NOT_COMPUTATION_EQUIVALENT": "THE M3a-2 ARTEFACT IS NOT COMPUTATION-EQUIVALENT TO THE "
                                         "ORIGINAL (Pre-decided 97). It is never run (34(f))."}
    rec["exec_state_at_save"] = read_es("[S] immediately before the save")
    rec["route"] = ("ordinary SaveInstrument" if rec["exec_state_at_save"] == 1
                    else "the Pre-decided 88 broken-VI route -> gui_save")
    fact("[S] ExecState at the save is %r, so the route is: %s"
         % (rec["exec_state_at_save"], rec["route"]))
    # ---- B2, the prior-art finding `already-failed` (Pre-decided 99), ACCEPTED and repaired here.
    # THE CALLER MUST NOT PRE-QUOTE THE PATH. `gscript.py:281-287`'s `q()` quotes any argument
    # carrying spaces/parentheses exactly once; a pre-quoted "'%s'" arrives starting with "'" and
    # not '"', so `q()` fails its pre-quoted test and quotes it AGAIN ("''C:\...''"). lv_gui.ps1
    # then writes no file. MEASURED, not argued: `tools/bench/build_d1_m3a1.log:3402` reads
    # "before 'm3a1_save_before_...png' (exists False), after '...' (exists False)" - M3a-1's save
    # therefore ran with USER RULE 17:5x formally UNMET on that one act.
    # And each capture is now ASSERTED to exist - a GATE, not a hope: capture -> act -> capture is
    # only a confirmation if the captures land.
    shot_b = os.path.join(BENCH, "m3a2_save_before_%s.png" % STAMP)
    shot_a = os.path.join(BENCH, "m3a2_save_after_%s.png" % STAMP)
    out_b, err_b = safe("[S] capture BEFORE the save",
                        lambda: g._lv_gui("-Action", "shot", "-Out", shot_b))
    rec["capture_before_stdout"] = (out_b or "")[-400:]
    gate("S3 the BEFORE capture LANDED ON DISK (USER RULE 17:5x - locate in a capture taken just "
         "before; B2 repair)", os.path.exists(shot_b),
         "%s%s ; lv_gui said %r" % (shot_b, (" ; " + err_b) if err_b else "",
                                    (out_b or "")[-160:]))
    try:
        rec["save_returned_size"] = g.save(TARGET, allow_broken=True)
    except Exception as e:                                                         # noqa: BLE001
        rec["save_returned_size"] = None
        rec["save_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
    out_a, err_a = safe("[S] capture AFTER the save",
                        lambda: g._lv_gui("-Action", "shot", "-Out", shot_a))
    rec["capture_after_stdout"] = (out_a or "")[-400:]
    gate("S4 the AFTER capture LANDED ON DISK (USER RULE 17:5x - capture after and confirm; B2 "
         "repair)", os.path.exists(shot_a),
         "%s%s ; lv_gui said %r" % (shot_a, (" ; " + err_a) if err_a else "",
                                    (out_a or "")[-160:]))
    rec["captures"] = {
        "before": shot_b, "before_exists": os.path.exists(shot_b),
        "before_size": (os.path.getsize(shot_b) if os.path.exists(shot_b) else None),
        "after": shot_a, "after_exists": os.path.exists(shot_a),
        "after_size": (os.path.getsize(shot_a) if os.path.exists(shot_a) else None),
        "quoting": "the path is passed RAW - gscript.q() quotes it exactly once (B2)"}
    fact("[S] capture -> act -> capture: before %r (exists %r, %r B), after %r (exists %r, %r B) - "
         "the path is passed RAW so gscript.q() quotes it exactly once (B2, build_d1_m3a1.log:3402)"
         % (os.path.basename(shot_b), rec["captures"]["before_exists"], rec["captures"]["before_size"],
            os.path.basename(shot_a), rec["captures"]["after_exists"], rec["captures"]["after_size"]))
    if rec["save_error_verbatim"]:
        fact("[S] THE SAVE WAS REFUSED, VERBATIM: %s" % rec["save_error_verbatim"])
        refusal("[S] g.save(TARGET, allow_broken=True)", rec["save_error_verbatim"])
    # THE AFTER-CONFIRMATION IS THE FILE ITSELF (Pre-decided 96), read off disk, not a screenshot.
    ff = D.file_facts("[S] the M3a-2 artefact", TARGET)
    rec.update({"exists": bool(ff.get("exists")), "md5": ff.get("md5"), "size": ff.get("size"),
                "version_candidates": ff.get("version_candidates")})
    rec["bytes_equal_to_the_input"] = (ff.get("md5") == INPUT_MD5)
    rec["size_equal_to_the_input"] = (str(ff.get("size")) == str(R.get("input_size_before")))
    gate("S1 the saved artefact's bytes DIFFER from the input artefact - the in-memory edits reached "
         "the disk", rec["exists"] and not rec["bytes_equal_to_the_input"],
         "md5 %r vs input %r ; size %r vs input %r" % (rec.get("md5"), INPUT_MD5, rec.get("size"),
                                                       R.get("input_size_before")))
    gate("S2 the saved path IS the claudeDev target this run created",
         os.path.normcase(os.path.dirname(TARGET)) == os.path.normcase(g.CLAUDEDEV)
         and os.path.basename(TARGET).startswith("D1_s3b_m3a2_") and rec["exists"], TARGET)
    fact("[S] FILE ON DISK: %s  md5 %r  size %r  (input md5 %s size %r ; bytes equal %r)"
         % (TARGET, rec["md5"], rec["size"], INPUT_MD5, R.get("input_size_before"),
            rec["bytes_equal_to_the_input"]))
    fact("[S] *** %s IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL (Pre-decided 97): both loops exist and "
         "the OLD one still feeds both downstream consumers. IT IS NEVER RUN (34(f)). The two RIGHT OUTER "
         "terminals stay bare by design - re-sourcing their consumers is M3a-3. ***"
         % os.path.basename(TARGET))
    R["artefacts_on_disk"].append(rec)
    # NO COLD REOPEN AT ExecState 0 - the labview-automation skill's rule: never cold-load a broken-saved
    # VI headless (recompile spin).
    fact("[S] NO COLD REOPEN IS ATTEMPTED at ExecState %r%s"
         % (rec["exec_state_at_save"],
            " - the skill's rule: never cold-load a broken-saved VI headless (recompile spin)"
            if rec["exec_state_at_save"] != 1 else " - the stage is done and the file is on disk"))
    dump()
    return rec


# ============================================================================================== main
def main():
    print("=" * 100, flush=True)
    print("=== build_d1_m3a2  %s  - STAGE M3a-2, THE TWO INITIAL-VALUE ROWS (Pre-decided 91/92)" % STAMP,
          flush=True)
    print("=== THE ARTEFACT THIS RUN SAVES IS **NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL** AND IS "
          "NEVER RUN (34(f), Pre-decided 97).", flush=True)
    print("=" * 100, flush=True)
    hints = [TOP]
    try:
        phase_0()
        hints = phase_1_copy()
        cite_pd95_withdrawn()
        phase_1_loop_a("BEFORE", hints)
        for row in ROWS:
            if left_s() < ROW_MIN_S:
                fact("HALTED before row %s: only %.0f s left before the reserve; a row needs %.0f s"
                     % (row["tag"], left_s(), ROW_MIN_S))
                gate("[ROW %s] ROW ACCEPTANCE (Pre-decided 92) - the row was WRITTEN at all" % row["tag"],
                     False, "no wall-clock left")
                break
            one_row(row, hints)
        phase_type_check(hints)
        phase_1_loop_a("AFTER", hints)
        K["counts_final"] = counts("[F] final, in memory")
        phase_save()
    except Halt as e:
        fact("HALTED: %s" % e)
    except Exception as e:                                                         # noqa: BLE001
        # Pre-decided 100 §2: OUR bug, NOT a machine refusal. `refusal()` is not called here.
        import traceback
        R["unexpected_exception"] = traceback.format_exc()[-2500:]
        defect("main", e)
    finally:
        head("[H] HYGIENE - panels closed, the md5 pins AFTER, the tool pins, the refs and the handles")
        safe("close_panel(TARGET)", lambda: g.close_panel(TARGET))
        pr = probe_hash("H INPUT the M3a-1 artefact AFTER", INPUT)
        gate("H2 the input artefact's md5 is UNCHANGED after the run", pr.get("md5") == INPUT_MD5,
             "before %r / after %r" % (R.get("input_md5_before"), pr.get("md5")))
        for tag, path, pin in PINS:
            pr = probe_hash("H %s AFTER" % tag, path)
            gate("H3 %s md5 is STILL its pin %s" % (tag, pin[:8]), pr.get("md5") == pin,
                 "%r" % (pr.get("md5"),))
        for p in TOOL_PINS:
            pr = probe_hash("H TOOL %s AFTER" % os.path.basename(p), p)
            gate("H5 TOOL %s is byte-identical before and after" % os.path.basename(p),
                 pr.get("md5") == (K.get("tool_pins_before") or {}).get(p),
                 "%r vs %r" % (pr.get("md5"), (K.get("tool_pins_before") or {}).get(p)))
        rc = g.ref_counts()
        R["ref_counts"] = rc
        fact("refs: %r" % (rc,))
        gate("H6 refs opened == closed and 0 live", rc.get("live") == 0, "%r" % (rc,))
        R["handles"]["after"] = labview_handles()
        fact("LabVIEW handles AFTER: %r (before %r, after the restart %r)"
             % (R["handles"].get("after"), R["handles"].get("before"),
                R["handles"].get("after_restart")))
        gate("H7 the LabVIEW handle count was read at entry and at exit",
             isinstance(R["handles"].get("before"), int) and isinstance(R["handles"].get("after"), int),
             "%r -> %r" % (R["handles"].get("before"), R["handles"].get("after")))
        # H8 folds in the refusals recorded by the IMPORTED helpers, which keep theirs in build_d1_m3a1.
        imported = M.refusals[K.get("m3a1_refusals_at_entry", 0):]
        R["imported_helper_refusals"] = imported
        gate("H8 no mutator call was REFUSED BY THE MACHINE (this file's refusals and the imported "
             "helpers'; a Python exception of OURS is NOT one - it is H9)", not refusals and not imported,
             "%d machine refusal(s) here %r ; %d in the imported helpers %r"
             % (len(refusals), [r["where"] for r in refusals], len(imported),
                [r.get("where") for r in imported]))
        # H9 - ADDED 2026-09-22 (Pre-decided 100 §2). A bug in our own script gets its own gate, its own
        # wording and its own source line, so it can never again be reported as a refusal by the machine.
        gate("H9 NO DEFECT IN OUR OWN PYTHON CODE - no exception was raised by this script itself "
             "(a bug of ours is NEVER a machine refusal)", not defects,
             "%d our-code defect(s): %r"
             % (len(defects), [("%s at %s: %s" % (d["exception_type"], d["source_line"], d["where"]))
                               for d in defects]))
        left = [(os.path.basename(a["dest"]), a.get("md5"), a.get("size"))
                for a in R["artefacts_on_disk"] if a.get("exists")]
        R["files_left_on_disk"] = left
        fact("THE FILES THIS RUN LEFT ON DISK: %r" % (left,))
        if left:
            fact("*** EVERY FILE NAMED ABOVE IS NOT COMPUTATION-EQUIVALENT TO THE ORIGINAL AND IS NEVER "
                 "RUN (34(f), Pre-decided 97). ***")
        dump()
        print("\n" + "=" * 100, flush=True)
        print("=== GATES: %d pass / %d fail%s" % (len(passes), len(fails),
                                                  ("; failing: " + ", ".join(fails)) if fails else ""),
              flush=True)
        print("=== JSON: %s   elapsed %.1f s" % (OUT, time.time() - T_START), flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
