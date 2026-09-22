r"""build_d1_m3a3b_d3.py - D-3 of M3a-3b. The judgement session's call, carried verbatim by the brief.

    MATERIAL=1 py tools/bgrun.py --max-min 75 --log tools/bench/build_d1_m3a3b_d3.log \
        -- py -u tools/recipes/build_d1_m3a3b_d3.py

WHAT c83 MEASURED AND IS NOT RE-DERIVED HERE: with wire 7506 DELETED, every cell returns `error 1055` from
`UID to GObject Reference.vi` on `#7468` and from the Invoke; the "err empty" readings before run 2 were an
UNWIRED indicator's default. The judgement session's call, carried by this dispatch, is therefore to run the
one configuration never fired: THE INVOKE ON THE SINK TERMINAL (the FSIT `LeftTerm` `#7488`) WITH WIRE 7506
LEFT ALIVE. Every wire-alive cell so far (R0/R0b) put the Invoke on the BARE loop-border terminal instead.

⚠️ THE PREMISE IS A HYPOTHESIS UNDER TEST, NOT EDITOR FACT - and this project's own files already record
TWO DIFFERENT outcomes for it, neither of them a clean replacement (prior-art review
`archive/peer/2026-09-22-priorart-c84-d3-rowd.md` A2/A3/A4/B4; failed-prediction review
`archive/peer/2026-09-22-c84-replace-vs-branch.md`, claude/hypothesis/opus max, ANSWERED):
  * `docs/keystone-op-spec.md:444-446` (§28, 2026-09-06, MEASURED): *"Connect Wire on a wired sink re-routes
    and breaks - only wire unwired sinks."*
  * `tools/bench/build_d1_m3a1.log:1147` + `:1174` (`:1875`, `:2593`, `:3311`; indexed at
    `docs/cycle27-plan.md:3295-3300`), FOUR TIMES ON THIS VERY VI through this op's own donor - the Invoke
    on an ALREADY-WIRED sink, the other terminal as `Wire Source`: *"sink terminal t1 of CaseStructure
    #12589 carries wire 9113 ; WIRED-terminal count 3 -> 3 ; `Wire.Is Broken?` False ; LANDED False"* -
    a SILENT NO-OP, `wire_delta 1` (a stray wire), the sink keeping its OLD wire.
  * `archive/2026-09-16-status-gate-a1-delete-regression.md:94-97` - four already-wired sinks written:
    *"an uncontrolled replacement, and 1444 is most likely a source-less fragment."*
  * `tools/gscript.py:2522-2523` (and the skill, `references/vi-scripting.md:603`, `:627`): *"an
    already-wired source is BRANCHED ...; an already-wired SINK is not safe (LabVIEW re-routes and the VI
    breaks) - wire only unwired sinks."*
  * The failed-prediction review adds the EDITOR fact with a citation: LabVIEW MERGES rather than switches
    (NI Idea Exchange, "When wiring to an already wired terminal -> replace wire"), and the scripting API
    has no replace and no disconnect at all.
WHAT IS GENUINELY DIFFERENT HERE, and the only honest reason to run the cell: every one of those sinks was
addressed by an INDEX TRIPLE; this one is a `FlatSequenceInnerTunnel` `LeftTerm` addressed BY UID through
`UID to GObject Reference.vi` -> TMSC -> `Left Terminal` 1C3A9000. Nothing on file says the addressing route
changes the method's behaviour once it holds a terminal reference, so the prior art PREDICTS a silent no-op
or a merge. GATE S is written to catch exactly that: (a) fails on a no-op (the net's source owner stays
`#4334`), (d) fails on a break or a source-less fragment. THE FALSIFICATION IS PRINTED EXPLICITLY per cell -
the review's own table: claim dies the moment the op's `UID 2` comes back 7506, or wire 7506 is still in the
Wire census afterwards. Both are measured and reported below whatever the outcome.

WHAT ALREADY EXISTS - checked by READING the files before a line was written (CLAUDE.md "before creating any
new op, tool or recipe"):
  * `tools/recipes/build_opfsinnertunnelconnect_v0.py` - the builder of the op this one SWAPS. Imported, not
    re-implemented: `md5`, `PINS`, `BED`/`BED_MD5`, `del_wire`, `purge_junk`, `resolve_triple`,
    `private_bytes`, the topology constants. `OpFsInnerTunnelConnect_v0.vi` is NEVER modified or deleted.
  * `tools/bench/diag_c83_connect2x2_r2.py:340` `make_swap` - the EXACT construction that already built a
    LEGAL swapped copy (`diag_c83_connect2x2_r2.log:36-46`: nets w572 `#239.'element'` and w1337
    `#183.'LeftTerm'` exchanged onto the Invoke, the two OTHER consumers `#241.reference` / `#187.reference`
    re-branched onto their original sources, Remove Bad Wires removed 0, ExecState 1). Re-cut here against
    the LIVE topology (nothing is addressed by a carried uid) so it can be SAVED as v1 instead of a scratch.
  * `tools/bench/diag_c83_connect2x2.py` - `invoke_node`:180 and `attach_auto_route`:249, imported.
  * `tools/recipes/build_opconnectnested_v1.py` - `walk` / `term` / `src_of` / `idx` / `Stop` / `connect`
    (as `wire_by_name`), imported unchanged.
  * `tools/recipes/build_opfstunnelterm_v2.py:745` `read_tunnel` + `tools/bench/opfsinnertunnelterm_labels.json`
    - the ONLY caller shape for `OpFsInnerTunnelTerm_v0`, which is how the FSIT's OWN two faces are read
    (gate S(a)'s wire and gate S(e)'s `Right Terminal` #7471 / wire 7448).
  * `tools/recipes/build_opconnectfromwire_v0.py` `wire_source_owner` - the repaired, uid-echo-checked
    `OpWireSource_v5` driver. Imported. Owner identity decides, never a wire count (Pre-decided 117/120).
  * `tools/recipes/build_d1_m3a1.py` - `print_walk`, `pd85_violations`, `node_census`, `new_nodes`,
    `node_view`, `delete_by_uid`.
  * `tools/gscript.py` - `remove_bad_wires_scripted`:2594 (VI method 410; returns the wire count AFTER, so
    "bad wires present" is measurable as a count DELTA), `save`:2135 (`allow_broken=True` diverts to
    `gui_save`:2012 = the approved broken-intermediate route), `count`, `exec_state`, `ref_counts`.
  * THE EVIDENCE THE FIRST CUT OF THIS AUDIT DID NOT REACH (prior-art review A4, accepted and read):
    `docs/keystone-op-spec.md:438-447` (§28 - where the already-wired-sink rule was MEASURED, terminal by
    terminal), `tools/bench/build_d1_m3a1.log:1147` + `:1174` (the four on-this-VI measurements of the exact
    act), `archive/2026-09-16-status-gate-a1-delete-regression.md:94-97` (what happened when four
    already-wired sinks were actually written), `tools/gscript.py:2522-2523` (the wrapper family's own
    docstring for this method), and `tools/bench/broken_probe2.py:12` (the count-delta broken-wire probe
    this file re-uses). All five are quoted where they bite, above and at GATE S(d).
NOTHING NEW IS INVENTED: no new verb, no new method id, no third configuration, no `Wire.Disconnect Terminal`.

STEP 1  BUILD AND SAVE `claudeDev\OpFsInnerTunnelConnect_v1.vi` - v0 with THE TWO ROLES EXCHANGED: the
        Invoke sits on the FSIT `LeftTerm` (uid -> `UID to GObject Reference.vi` -> TMSC
        `FlatSequenceInnerTunnel` -> `Left Terminal` 1C3A9000) and the terminal named by the (diagram,
        `Nodes[]`, `Terminals[]`) INDEX TRIPLE is passed as `Wire Source`. v0's repaired error path is kept
        (the Invoke's OWN error cluster reaches `error out 7`); `Auto Route?` is exposed as a control.
  B1  the copy of v0 is at ExecState 1 and both Invoke feeds are wired (else nothing is built).
  B2  both feeding nets deleted; the two crossed feeds made; every OTHER consumer re-branched.
  B3  the BROKEN-WIRE PROBE: Remove Bad Wires removes 0 -> the crossed wires are not type-broken.
  B4  `Auto Route?` carries a front-panel control.
  B5  ExecState 1, saved by script, ExecState 1 RE-READ after the save; md5 + labels JSON reported.
  G2  20 CONSECUTIVE CALLS leave the handle count flat +-100 (regression check against the S0 baseline
      `docs/toolkit-capabilities.md:460-478`; private-bytes drift REPORTED beside it, because the kernel
      handle count is blind to VI Server refnums, `:484-485`). Junk `Invoke` rate measured and purged.
  G3  both uid echoes on every call: `uid_back` == 7468 (INPUT side, Pre-decided 125) and `term_uid` == 7488.
  H5  gscript's reference counter level (opened == closed) at exit.

STEP 2  THE MISSING CELL, on dated scratch COPIES of the bed with wire 7506 LEFT ALIVE:
          S-T  `Auto Route?` TRUE      S-F  `Auto Route?` FALSE
        Each: one FRESH copy; v1 called with `fsit_uid` 7468 and the index triple of the NEW loop's
        shift-register OUTER terminal (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`, uid `#23906`,
        owner `RightShiftRegister #23868`).
  GATE S, all five, each printed with the value compared:
   (a) the FSIT LeftTerm's net has EXACTLY ONE source terminal and its OWNER is `RightShiftRegister #23868`
       (read by `OpWireSource_v5`; owner identity decides - Pre-decided 117 as corrected by 120);
   (b) `#4334` is OFF that net;
   (c) PD85 violations 0 on the walk;
   (d) `Wire.Is Broken?` False on that wire, AND the diagram-wide broken-wire count is NOT HIGHER than the
       same count on the same bytes BEFORE the call. The bed is broken BY DESIGN, so absolute `ExecState`
       is NOT a gate - the before/after comparison is. HOW THE COUNT IS TAKEN: the (wires before - wires
       after `remove_bad_wires_scripted`) delta. That construction is NOT new - it is already on disk at
       `tools/bench/broken_probe2.py:12` and is the stated method of `tools/bench/bool_wire_probe.py:12`;
       what this file adds is the mutate-only-on-a-throwaway discipline. ⚠️ TWO CAVEATS, both measured and
       both REPORTED rather than argued away: Remove Bad Wires is REFUSED on a deliverable as a rule-1a
       hazard (`docs/cycle27-plan.md:1860-1862`, citing
       `archive/2026-09-17-status-d1-route-b-2.md:44-46` - it DELETED A TUNNEL), and
       `docs/toolkit-capabilities.md:68` forbids citing RBW-survival as evidence a wire is good. So it runs
       ONLY on copies that are deleted in the same run, the BEFORE number is taken on its own byte-identical
       control copy of the bed which is then discarded, the AFTER number is the cell scratch's LAST act, and
       on the STEP-3 artefact the probe runs on a THROWAWAY COPY OF THE SAVED FILE - the artefact itself
       never passes through Remove Bad Wires. The NON-MUTATING companions (total Wire count before/after the
       call, `wire_delta`, `ExecState` before/after, and whether wire 7506 is still in the Wire census) are
       reported beside it for every cell.
   (e) nothing downstream was dropped: the FSIT `Right Terminal` `#7471` still carries its inner wire 7448
       (the Row C lesson - a dropped consumer is a silent failure).
  The raw Invoke error (code, source, description) is reported for each cell WHATEVER the outcome, plus the
  stray-`Invoke` junk count and its purge. Both scratch copies are deleted in this same run.

STEP 3  LAND IT - THE ONLY BRANCH IN THIS FILE. If at least one cell passes GATE S IN FULL, the same
        operation is repeated to produce the deliverable: work FROM THE BED into a NEW file
        `claudeDev\D1_s3b_m3a3b_<stamp>.vi`, leaving the bed byte-unchanged. If BOTH cells pass, the
        artefact uses `Auto Route?` TRUE and says so. On the saved artefact GATE S (a)-(e) is re-asserted
        PLUS the ORDERED IDEMPOTENT SECOND PASS of Pre-decided 106 (`wire_delta` 0 on a second, identical
        connect, and the identity read on THAT pass). Path, md5, size, `ExecState` and the SAVE ROUTE are
        reported. Script save when `ExecState` is 1; otherwise `save(allow_broken=True)` -> `gui_save`, the
        approved broken-intermediate route (CLAUDE.md §3 item 6, user 2026-09-22).
        IF NEITHER CELL PASSES: nothing is saved, the scratches are deleted, the raw values are reported and
        the run STOPS. No third configuration is improvised, no terminal is removed from a net, no tunnel is
        re-created, `Wire.Disconnect Terminal` is not touched - those are judgement's and none is authorised.

HYGIENE (the only other things that can FAIL)
 H1/H2  the bed's md5 is `33ef524e...` BEFORE and UNCHANGED AFTER. The bed is NEVER opened for EXECUTION.
 H3     the five md5 pins hold; `OpFsInnerTunnelConnect_v0.vi` md5 `50a1e58a...` unchanged.
 H4     every scratch deleted.
 H6     THE FILES THIS RUN LEFT ON DISK are named explicitly.

RIG STATE 조립: no motor, no ASI, no camera. VI Scripting and COM only.
VERIFICATION LEVEL: STRUCTURAL for v1's legality; FUNCTIONAL for every cell and for the artefact (real data
through a real op into real copies of the bed, asserted by terminal wire uids and OWNER IDENTITY).
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
from build_opconnectnested_v1 import walk, term, src_of, Stop                       # noqa: E402
from build_opconnectnested_v1 import connect as wire_by_name                        # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS              # noqa: E402
from build_opfstunnelterm_v2 import read_tunnel                                     # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                       # noqa: E402
import diag_c83_connect2x2 as R1                                                    # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "build_d1_m3a3b_d3.json")

md5 = C82.md5
OP0 = C82.OP                                            # OpFsInnerTunnelConnect_v0.vi - NEVER written
OP0_MD5 = "50a1e58a4825c2ce030ed9a41e204931"
OP1 = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelConnect_v1.vi")
MAP_OUT = os.path.join(BENCH, "opfsinnertunnelconnect_v1_labels.json")
MAP_IN = C82.MAP_OUT
OP_FSIT_READ = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
LABELS_FSIT = os.path.join(BENCH, "opfsinnertunnelterm_labels.json")
V5 = C82.V5

BED, BED_MD5, BED_BYTES = C82.BED, C82.BED_MD5, C82.BED_BYTES
PINS = C82.PINS

FSIT_UID = C82.FSIT_UID                 # 7468
LEFT_TERM = C82.LEFT_TERM_EXPECT        # 7488
RIGHT_TERM = 7471                       # the FSIT's Right Terminal (gate S(e))
RIGHT_WIRE = 7448                       # the inner wire it must still carry
ROWD_WIRE = C82.ROWD_WIRE               # 7506 - LEFT ALIVE in every cell of this file
LOOP_NEW = C82.LOOP_NEW                 # 23032
LOOP_NODES_IDX = C82.LOOP_NODES_IDX     # 21
LOOP_TERM_IDX = C82.LOOP_TERM_IDX       # 1
TERM_UID_EXPECT = 23906                 # that terminal's own uid (reported, not gateable over this path)
RSR_EXPECT = C82.RSR_EXPECT             # 23868
OLD_SOURCE = C82.OLD_SOURCE             # 4334

HANDLE_CALLS = 20
HANDLE_TOL = 100

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH_H = os.path.join(g.CLAUDEDEV, "C84H_%s.vi" % STAMP)
SCRATCH_B = os.path.join(g.CLAUDEDEV, "C84BASE_%s.vi" % STAMP)
ART = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3b_%s.vi" % STAMP)
SCRATCH_P = os.path.join(g.CLAUDEDEV, "C84PROBE_%s.vi" % STAMP)
SCRATCHES = [SCRATCH_H, SCRATCH_B, SCRATCH_P]

CELLS = [("S-T", True), ("S-F", False)]

RUN_DEADLINE_S = 66 * 60.0
RESERVE_S = 420.0
T0 = time.time()

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "op0": OP0, "op1": OP1, "bed": BED,
     "task": "D-3 of M3a-3b: build OpFsInnerTunnelConnect_v1 (roles exchanged), measure the missing cell "
             "(Invoke on the SINK terminal, wire 7506 ALIVE), and land Row D if it passes GATE S",
     "verification_level": "STRUCTURAL for v1's legality; FUNCTIONAL for the cells and the artefact",
     "B": {}, "G": {}, "cells": {}, "step3": {}, "H": {}}


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


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


def labels_of(target, indicators=False):
    return {l for _i, l, ind in g.fp_labels(target) if bool(ind) == indicators}


def bad_wire_count(target, tag):
    """The diagram-wide BROKEN-WIRE COUNT. `remove_bad_wires_scripted` runs LabVIEW's own
    Block Diagram:Remove Bad Wires (VI method 410) and returns the wire count AFTER it, so
    (wires before - wires after) is exactly how many bad wires the VI carried. IT MUTATES - only ever
    called on a copy that is about to be discarded."""
    before = g.count(target, "Wire")
    after, es = g.remove_bad_wires_scripted(target)
    n = before - after
    fact("%s BROKEN-WIRE COUNT: Wire %d -> %d after Remove Bad Wires = %d bad wire(s); ExecState after %r"
         % (tag, before, after, n, es))
    return n, before, after, es


# ---------------------------------------------------------------- the parameterised caller
def fsit_call(op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term,
              ar_label="", auto_route=None, inv_err_label="error out 7"):
    """One call of the connect op. Every readout is POISONED first (Pre-decided 125): a stale value can
    never be read as an answer, and `Is Broken?` is poisoned True so only a fresh write can make it False.
    c83 measured poison ON vs OFF as identical (R0 vs R0b), so it is kept on."""
    w0 = g.count(target, "Wire")
    i0 = g.count(target, "Invoke")
    vi = g.op(op_path)
    for k, v in ((labels["term_uid"], 0), (labels["uid_back"], 0), (labels["sink_wire_uid"], 0),
                 (labels["is_broken"], True), ("UID", 0), ("Name", "POISON")):
        try:
            vi.SetControlValue(k, v)
        except Exception:                                                          # noqa: BLE001
            pass
    for k in (inv_err_label, "error out"):
        if k:
            try:
                vi.SetControlValue(k, (True, 999999, "POISON - not overwritten by the run"))
            except Exception:                                                      # noqa: BLE001
                pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["fsit_uid"], int(fsit_uid))
    if ar_label and auto_route is not None:
        vi.SetControlValue(ar_label, bool(auto_route))
    for k in (labels["dead_src_node"], labels["dead_src_term"], labels["dead_src_diag"],
              labels["dead_wire_term_index"]):
        try:
            vi.SetControlValue(k, 0)
        except Exception:                                                          # noqa: BLE001
            pass
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:                                                          # noqa: BLE001
            pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else "EXC %s" % str(e)[:140]
    out = {"err": err, "op": os.path.basename(op_path), "auto_route": auto_route}
    out["invoke_err"] = (g._err(vi, inv_err_label) or "") if inv_err_label else "NO INDICATOR"
    for k in ("err_uidvi", "err_fsit", "err_termuid", "err_uidback"):
        if labels.get(k):
            out[k] = g._err(vi, labels[k]) or ""
    for k, lab in (("term_uid", labels["term_uid"]), ("uid_back", labels["uid_back"]),
                   ("sink_wire_uid", labels["sink_wire_uid"]), ("is_broken", labels["is_broken"]),
                   ("UID", "UID"), ("Name", "Name")):
        try:
            out[k] = vi.GetControlValue(lab)
        except Exception:                                                          # noqa: BLE001
            out[k] = "READ FAILED"
    out["wire_delta"] = g.count(target, "Wire") - w0
    out["invoke_delta"] = g.count(target, "Invoke") - i0
    return out


def fsit_read(target, uid, tag):
    """One read of a FlatSequenceInnerTunnel's two faces through `OpFsInnerTunnelTerm_v0`."""
    labs, e = safe("%s load %s" % (tag, os.path.basename(LABELS_FSIT)),
                   lambda: json.load(open(LABELS_FSIT, encoding="utf-8")), None)
    if not labs:
        return None
    vi, e = safe("%s g.op(OpFsInnerTunnelTerm_v0)" % tag, lambda: g.op(OP_FSIT_READ))
    if vi is None:
        return None
    rd, e = safe("%s read_tunnel(#%d)" % (tag, uid), lambda: read_tunnel(vi, labs, target, uid))
    if rd:
        fact("%s FSIT #%d: uid echo %r cls %r | %s #%r wire %r | %s #%r wire %r | err=%r err_a=%r err_b=%r"
             % (tag, uid, rd.get("uid_back"), rd.get("cls_back"), labs.get("face_a"), rd.get("term_a_uid"),
                rd.get("wire_a"), labs.get("face_b"), rd.get("term_b_uid"), rd.get("wire_b"),
                rd.get("err"), rd.get("err_a"), rd.get("err_b")))
    return rd


# ======================================================================= [0] files only
def phase_files():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the pins, the ops this run needs")
    got = md5(BED)
    R["bed_md5_before"] = got
    R["bed_bytes"] = os.path.getsize(BED)
    gate("H1 bed md5 before == %s (%d B)" % (BED_MD5, BED_BYTES),
         got == BED_MD5 and R["bed_bytes"] == BED_BYTES, "got %s, %d bytes" % (got, R["bed_bytes"]),
         fatal=True)
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s" % (label, have, want, ("OK" if have == want else "DIFFERS")))
    R["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))
    for p, nm in ((OP0, "OpFsInnerTunnelConnect_v0.vi (THE DONOR - never written)"),
                  (V5, "OpWireSource_v5.vi (the identity reader)"),
                  (OP_FSIT_READ, "OpFsInnerTunnelTerm_v0.vi (the FSIT face reader)")):
        gate("F0 %s on disk" % nm, os.path.isfile(p), p, fatal=True)
    R["op0_md5_before"] = md5(OP0)
    gate("F0b the donor v0 is the one c83 left on disk (%s)" % OP0_MD5, R["op0_md5_before"] == OP0_MD5,
         "got %s (%d bytes)" % (R["op0_md5_before"], os.path.getsize(OP0)), fatal=True)
    if os.path.exists(OP1):
        fact("an OLD %s exists (md5 %s) - it is REPLACED by this build"
             % (os.path.basename(OP1), md5(OP1)))


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


# ======================================================================= [B] STEP 1 - build v1
def build_v1():
    head("[B] STEP 1 - OpFsInnerTunnelConnect_v1.vi = v0 with the two Invoke feeds EXCHANGED "
         "(diag_c83_connect2x2_r2.make_swap, re-cut against the LIVE topology)")
    if os.path.exists(OP1):
        os.remove(OP1)
    shutil.copyfile(OP0, OP1)
    time.sleep(0.4)
    g.report_all(OP1, "SubVI")
    g.open_panel(OP1)
    time.sleep(0.8)
    es = g.exec_state(OP1)
    gate("B1 the copy of v0 is at ExecState 1", es == 1, "ExecState %r" % es, fatal=True)
    n_inv, u_inv, rows, w = R1.invoke_node(OP1)
    r_ref, r_ws = term(rows, "reference", False), term(rows, "Wire Source", False)
    gate("B1b the Invoke's `reference` AND `Wire Source` are both fed",
         bool(r_ref and r_ws and r_ref.get("wire") and r_ws.get("wire")),
         "reference %r ; Wire Source %r" % (r_ref, r_ws), fatal=True)
    w_ref, w_ws = r_ref["wire"], r_ws["wire"]

    def net(wire):
        su = src_of(w, wire)
        sn = next((x["name"] for x in w[su][2] if x["is_source"] and x["wire"] == wire), None)
        sinks = [(u, x["name"]) for u, (_n, _l, rr) in w.items() for x in rr
                 if (not x["is_source"]) and x["wire"] == wire]
        return su, sn, sinks

    su_ref, sn_ref, sk_ref = net(w_ref)
    su_ws, sn_ws, sk_ws = net(w_ws)
    fact("B2 net w%s (feeds `reference` today - the INDEX-TRIPLE half): source #%s.%r ; sinks %r"
         % (w_ref, su_ref, sn_ref, sk_ref))
    fact("B2 net w%s (feeds `Wire Source` today - the FSIT half): source #%s.%r ; sinks %r"
         % (w_ws, su_ws, sn_ws, sk_ws))
    R["B"]["before"] = {"invoke_uid": u_inv, "invoke_nodes_index": n_inv,
                        "reference_net": [w_ref, su_ref, sn_ref, sk_ref],
                        "wire_source_net": [w_ws, su_ws, sn_ws, sk_ws]}
    gate("B2a the `Wire Source` half is the FSIT `LeftTerm` property node (the half that becomes the "
         "Invoke's OWN object)", sn_ws == "LeftTerm", "source terminal name %r" % sn_ws, fatal=True)
    ok = True
    for wu in (w_ref, w_ws):
        _r, e = safe("B2 delete net w%r" % wu, lambda q=wu: C82.del_wire(OP1, q, "B2 "))
        ok = ok and not e
    safe("B2 remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(OP1))
    plan = [(su_ref, sn_ref, u_inv, "Wire Source", False), (su_ws, sn_ws, u_inv, "reference", False)]
    for (src_u, src_n, sinks) in ((su_ref, sn_ref, sk_ref), (su_ws, sn_ws, sk_ws)):
        for (du, dn) in sinks:
            if du == u_inv:
                continue
            plan.append((src_u, src_n, du, dn, True))
    for (su, sn, du, dn, br) in plan:
        _r, e = safe("B2 connect #%s.%r -> #%s.%r (branch=%r)" % (su, sn, du, dn, br),
                     lambda a=su, b=sn, c=du, d=dn, f=br: wire_by_name(OP1, a, b, c, d, branch=f, tag="B2 "))
        ok = ok and not e
    R["B"]["rewire_plan"] = plan
    gate("B2b every crossed feed and every re-branch was made and verified on BOTH ends", ok,
         "%d wiring step(s)" % len(plan), fatal=True)

    head("[B3] THE BROKEN-WIRE PROBE - a type mismatch would make Remove Bad Wires delete the crossed wires")
    wc0 = g.count(OP1, "Wire")
    safe("B3 remove_bad_wires probe", lambda: g.remove_bad_wires_scripted(OP1))
    wc1 = g.count(OP1, "Wire")
    R["B"]["broken_wire_probe"] = {"before": wc0, "after": wc1, "removed": wc0 - wc1}
    gate("B3 Remove Bad Wires removed 0 wires from v1 (the crossed feeds are NOT type-broken)",
         wc0 - wc1 == 0, "Wire %d -> %d (removed %d)" % (wc0, wc1, wc0 - wc1))

    head("[B4] `Auto Route?` as a front-panel control")
    ar, note = R1.attach_auto_route(OP1, "B4")
    R["B"]["auto_route_label"] = ar
    R["B"]["auto_route_note"] = note
    gate("B4 `Auto Route?` carries a control", bool(ar), "label %r (%s)" % (ar, note), fatal=True)

    head("[B5] auto error handling OFF, ExecState 1, SAVE, re-read")
    aeh_ok = True
    try:
        g.set_auto_error_handling(OP1, False)
    except Exception as e:                                                         # noqa: BLE001
        aeh_ok = False
        fact("set_auto_error_handling failed (%s)" % str(e)[:100])
    gate("B5a auto error handling is OFF", aeh_ok)
    es = g.exec_state(OP1)
    if es != 1:
        w2 = walk(OP1, 0)
        orphans = [(u, r["name"]) for u in w2 for r in w2[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        fact("B5 DIAGNOSTIC unwired non-error SINK terminals: %r" % orphans)
    gate("B5b ExecState 1 - the swapped op is legal", es == 1, "ExecState %r" % es, fatal=True)
    size = g.save(OP1)
    g.reset()
    time.sleep(1.5)
    es2 = g.exec_state(OP1)
    R["B"]["op1_md5"] = md5(OP1)
    R["B"]["op1_bytes"] = size
    R["B"]["exec_state_saved"] = es2
    fact("B5 SAVED %s (%s bytes) md5 %s" % (OP1, size, R["B"]["op1_md5"]))
    gate("B5c ExecState 1 RE-READ after the save", es2 == 1, "ExecState %r" % es2, fatal=True)
    gate("B5d the donor v0 md5 is UNCHANGED", md5(OP0) == R["op0_md5_before"], R["op0_md5_before"])

    labels = dict(json.load(open(MAP_IN, encoding="utf-8")))
    labels["route"] = "fsit-leftterm-SINK (roles exchanged: the Invoke sits on the FSIT LeftTerm; the "
    labels["route"] += "index-triple terminal is `Wire Source`)"
    labels["auto_route"] = ar
    labels["donor"] = os.path.basename(OP0)
    labels["donor_md5"] = R["op0_md5_before"]
    labels["panel"] = [(i, lbl, ind) for i, lbl, ind in g.fp_labels(OP1)]
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact("B5 labels -> %s" % MAP_OUT)
    R["B"]["labels"] = labels
    g.close_panel(OP1)
    return labels, ar


# ======================================================================= [G2/G3] handles + echoes
def gates_23(labels, ar):
    head("[G2/G3] %d CONSECUTIVE CALLS of v1 on a dated scratch copy of the bed - handle count flat +-%d, "
         "and BOTH uid echoes" % (HANDLE_CALLS, HANDLE_TOL))
    shutil.copyfile(BED, SCRATCH_H)
    time.sleep(0.4)
    gate("G2a the handle-test scratch is a byte-identical copy of the bed",
         md5(SCRATCH_H) == R["bed_md5_before"], os.path.basename(SCRATCH_H), fatal=True)
    t = time.time()
    _, err = safe("ensure_loaded(SCRATCH_H)", lambda: g.ensure_loaded(SCRATCH_H))
    fact("ensure_loaded(handle scratch) took %.1f s%s" % (time.time() - t, ((" ERROR " + err) if err else "")))
    d_idx, trip = C82.resolve_triple(SCRATCH_H, "G2")
    R["G"]["g2_triple"] = trip
    nodes0, _ = M.node_census(SCRATCH_H, "G2b BEFORE the %d calls" % HANDLE_CALLS)
    handles_before, _ = safe("handles before the calls", labview_handles)
    priv_before = C82.private_bytes()
    rows = []
    for i in range(HANDLE_CALLS):
        r = fsit_call(OP1, labels, SCRATCH_H, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                      ar_label=ar, auto_route=True)
        r["call"] = i + 1
        rows.append(r)
        if i in (0, 1, HANDLE_CALLS - 1) or r.get("invoke_err"):
            fact("G2 call %2d: uid_back=%r term_uid=%r `UID 2`=%r is_broken=%r wire_delta=%r "
                 "invoke_err=%r op_err=%r"
                 % (i + 1, r.get("uid_back"), r.get("term_uid"), r.get("sink_wire_uid"),
                    r.get("is_broken"), r.get("wire_delta"), str(r.get("invoke_err"))[:120],
                    str(r.get("err"))[:80]))
    handles_after, _ = safe("handles after the calls", labview_handles)
    priv_after = C82.private_bytes()
    delta = (handles_after - handles_before) if (isinstance(handles_before, int)
                                                 and isinstance(handles_after, int)) else None
    pdrift = None
    if isinstance(priv_before, int) and isinstance(priv_after, int):
        pdrift = round((priv_after - priv_before) / (1024.0 * 1024.0), 2)
    R["G"]["handle_rows"] = rows
    R["G"]["handles_before_calls"] = handles_before
    R["G"]["handles_after_calls"] = handles_after
    R["G"]["handle_delta"] = delta
    R["G"]["private_mb_drift"] = pdrift
    fact("G2 COMPANION MEASUREMENT (docs/toolkit-capabilities.md:484-485 - the kernel handle count is BLIND "
         "to VI Server refnums): private bytes %r -> %r, drift %r MB over %d calls"
         % (priv_before, priv_after, pdrift, HANDLE_CALLS))
    gate("G2 %d consecutive calls leave the handle count flat +-%d (a REGRESSION CHECK against the S0 "
         "baseline docs/toolkit-capabilities.md:460-478, not a hygiene proof)" % (HANDLE_CALLS, HANDLE_TOL),
         delta is not None and abs(delta) <= HANDLE_TOL,
         "before %r -> after %r, delta %r ; private-bytes drift %r MB"
         % (handles_before, handles_after, delta, pdrift))
    nodes20, _ = M.node_census(SCRATCH_H, "G2b AFTER the %d calls" % HANDLE_CALLS)
    fact("G2b junk accumulation over %d calls: Node %d -> %d = %.2f new node(s) PER CALL"
         % (HANDLE_CALLS, len(nodes0), len(nodes20), (len(nodes20) - len(nodes0)) / float(HANDLE_CALLS)))
    _final, prec = C82.purge_junk(SCRATCH_H, nodes0, "G2b", [d_idx])
    R["G"]["g2_purge"] = prec
    echoes = sorted({int(r["term_uid"]) for r in rows if isinstance(r.get("term_uid"), (int, float))})
    backs = sorted({int(r["uid_back"]) for r in rows if isinstance(r.get("uid_back"), (int, float))})
    R["G"]["uid_echoes"] = echoes
    R["G"]["uid_back_echoes"] = backs
    gate("G3 the OUTPUT-side echo: every call returns the LeftTerm whose OWN uid is #%d" % LEFT_TERM,
         echoes == [LEFT_TERM], "distinct `term_uid` across %d calls: %r (want [%d])"
         % (len(rows), echoes, LEFT_TERM))
    gate("G3a the INPUT-side echo (Pre-decided 125): `uid_back` == the uid passed IN (#%d) on every call"
         % FSIT_UID, backs == [FSIT_UID], "distinct `uid_back`: %r (want [%d])" % (backs, FSIT_UID))
    R["G"]["first_call"] = rows[0] if rows else None
    fact("G2/G3 FIRST CALL VERBATIM: %s" % json.dumps(rows[0] if rows else {}, default=str)[:900])


# ======================================================================= GATE S
def gate_s(tag, target, d_idx, before_read, r, baseline_bad, rec, probe_bad=True):
    """GATE S (a)-(e) on `target` after a call. Returns (all_passed, dict of the five outcomes)."""
    out = {}
    after_read = fsit_read(target, FSIT_UID, "%s AFTER" % tag)
    rec["fsit_after"] = after_read
    wire_a = (after_read or {}).get("wire_a")
    rec["fsit_left_wire_after"] = wire_a
    fact("%s the FSIT LeftTerm #%r carries wire %r AFTER the call (it carried %r before)"
         % (tag, (after_read or {}).get("term_a_uid"), wire_a, (before_read or {}).get("wire_a")))
    walkr, werr = safe("%s OpWireSource_v5(w%r)" % (tag, wire_a),
                       lambda: WIRE_TERMS(target, int(wire_a), n=8) if wire_a else [], [])
    M.print_walk(tag, wire_a, walkr, werr)
    bad = M.pd85_violations(wire_a, walkr) if wire_a else ["no wire on the LeftTerm"]
    owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid"))) for t in (walkr or [])
                     if t.get("owner_uid")})
    src_owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid"))) for t in (walkr or [])
                         if t.get("is_source") and t.get("owner_uid")})
    rec["source_owners"], rec["all_owners"], rec["pd85_violations"] = src_owners, owners, len(bad)
    fact("%s NET w%r: source-terminal owners %r ; every owner %r ; PD85 %d"
         % (tag, wire_a, src_owners, owners, len(bad)))
    out["a"] = gate("%s GATE S(a) the FSIT LeftTerm's net has EXACTLY ONE source terminal and its OWNER is "
                    "RightShiftRegister #%d" % (tag, RSR_EXPECT),
                    src_owners == [("RightShiftRegister", RSR_EXPECT)],
                    "source-terminal owners %r (want [('RightShiftRegister', %d)])" % (src_owners, RSR_EXPECT))
    out["b"] = gate("%s GATE S(b) the OLD source #%d is OFF that net" % (tag, OLD_SOURCE),
                    bool(owners) and all(u != OLD_SOURCE for _c, u in owners),
                    "every owner on the net: %r" % (owners,))
    out["c"] = gate("%s GATE S(c) PD85 violations 0 on the walk" % tag, not bad,
                    "%d violation(s) %r" % (len(bad), bad))
    same = (r.get("sink_wire_uid") == wire_a)
    out["d1"] = gate("%s GATE S(d1) `Wire.Is Broken?` False on THAT wire (the op's own 6371004 readback, "
                     "poisoned True before the run; its `UID 2` must be the same wire)" % tag,
                     r.get("is_broken") is False and same,
                     "Is Broken? %r ; op `UID 2` %r vs LeftTerm wire %r (same wire %r)"
                     % (r.get("is_broken"), r.get("sink_wire_uid"), wire_a, same))
    if probe_bad:
        n_bad, wb, wa, es_after = bad_wire_count(target, "%s (d2)" % tag)
        rec["bad_wires_after"] = n_bad
        rec["exec_state_after_rbw"] = es_after
        out["d2"] = gate("%s GATE S(d2) the diagram-wide broken-wire count is NOT HIGHER than the baseline "
                         "on the same bytes before the call" % tag, n_bad <= baseline_bad,
                         "after %d vs baseline %d (Wire %d -> %d)" % (n_bad, baseline_bad, wb, wa))
    else:
        out["d2"] = None
    tb_uid = (after_read or {}).get("term_b_uid")
    tb_wire = (after_read or {}).get("wire_b")
    out["e"] = gate("%s GATE S(e) nothing downstream was dropped: the FSIT `Right Terminal` #%d still "
                    "carries its inner wire %d" % (tag, RIGHT_TERM, RIGHT_WIRE),
                    tb_uid == RIGHT_TERM and tb_wire == RIGHT_WIRE,
                    "RightTerm #%r wire %r (want #%d / %d)" % (tb_uid, tb_wire, RIGHT_TERM, RIGHT_WIRE))
    rec["gate_s"] = out
    passed = all(v for k, v in out.items() if v is not None)
    fact("%s GATE S SUMMARY: %s -> %s"
         % (tag, {k: v for k, v in out.items()}, "PASS" if passed else "FAIL"))
    return passed, out


def one_call_and_gates(tag, target, d_idx, labels, ar, auto_route, baseline_bad, rec, probe_bad=True):
    before_read = fsit_read(target, FSIT_UID, "%s BEFORE" % tag)
    rec["fsit_before"] = before_read
    _u, trows = g.node_terms_uid(target, d_idx, LOOP_NODES_IDX)
    border_before = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
    rec["border_before"] = border_before
    fact("%s border t%d BEFORE: name=%r is_source=%r wire=%r error columns %r  (wire %d LEFT ALIVE)"
         % (tag, LOOP_TERM_IDX, (border_before or {}).get("name"), (border_before or {}).get("is_source"),
            (border_before or {}).get("wire"),
            {k: v for k, v in (border_before or {}).items() if k.endswith("_err")}, ROWD_WIRE))
    nodes0, _ = M.node_census(target, "%s BEFORE the call" % tag)
    wires0, _ = safe("%s Wire census before" % tag, lambda: sorted(g.uids(target, "Wire")), [])
    es0, _ = safe("%s exec_state before" % tag, lambda: g.exec_state(target))
    fact("%s NON-MUTATING BRACKET BEFORE: %d Wire object(s); wire %d present %r ; ExecState %r"
         % (tag, len(wires0 or []), ROWD_WIRE, ROWD_WIRE in (wires0 or []), es0))
    r = fsit_call(OP1, labels, target, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                  ar_label=ar, auto_route=auto_route)
    rec.update(r)
    fact("%s RAW INVOKE ERROR = %r" % (tag, r.get("invoke_err")))
    fact("%s RESULT: op_err=%r | term_uid=%r uid_back=%r | err_uidvi=%r err_fsit=%r err_termuid=%r "
         "err_uidback=%r | `UID 2`=%r is_broken=%r wire_delta=%r junk_Invoke=%r"
         % (tag, r.get("err"), r.get("term_uid"), r.get("uid_back"), r.get("err_uidvi"),
            r.get("err_fsit"), r.get("err_termuid"), r.get("err_uidback"), r.get("sink_wire_uid"),
            r.get("is_broken"), r.get("wire_delta"), r.get("invoke_delta")))
    _final, prec = C82.purge_junk(target, nodes0, "%s junk" % tag, [d_idx])
    rec["purge"] = prec
    _u, trows = g.node_terms_uid(target, d_idx, LOOP_NODES_IDX)
    border_after = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
    rec["border_after"] = border_after
    fact("%s border t%d AFTER: wire=%r (was %r) ; that terminal's expected uid is #%d (owner "
         "RightShiftRegister #%d)"
         % (tag, LOOP_TERM_IDX, (border_after or {}).get("wire"), (border_before or {}).get("wire"),
            TERM_UID_EXPECT, RSR_EXPECT))
    wires1, _ = safe("%s Wire census after" % tag, lambda: sorted(g.uids(target, "Wire")), [])
    es1, _ = safe("%s exec_state after" % tag, lambda: g.exec_state(target))
    rec["wire_census"] = {"before": len(wires0 or []), "after": len(wires1 or []),
                          "rowd_wire_present_before": ROWD_WIRE in (wires0 or []),
                          "rowd_wire_present_after": ROWD_WIRE in (wires1 or []),
                          "exec_state_before": es0, "exec_state_after": es1}
    fact("%s THE FALSIFICATION TABLE (archive/peer/2026-09-22-c84-replace-vs-branch.md §5 - the claim dies "
         "the moment either column reads the OLD wire): op `UID 2` = %r (claim: a NEW uid != %d ; prior art: "
         "%d) ; wire %d still in the Wire census: %r (claim: GONE ; prior art: PRESENT) ; Wire objects "
         "%d -> %d ; ExecState %r -> %r"
         % (tag, r.get("sink_wire_uid"), ROWD_WIRE, ROWD_WIRE, ROWD_WIRE,
            ROWD_WIRE in (wires1 or []), len(wires0 or []), len(wires1 or []), es0, es1))
    passed, out = gate_s(tag, target, d_idx, before_read, r, baseline_bad, rec, probe_bad=probe_bad)
    return passed, r


# ======================================================================= [S] STEP 2 - the two cells
def baseline_bad_wires():
    head("[S0] THE BASELINE broken-wire count, on its OWN byte-identical control copy of the bed, which is "
         "then DISCARDED (Remove Bad Wires mutates, so it never runs on a copy whose state is still needed)")
    shutil.copyfile(BED, SCRATCH_B)
    time.sleep(0.4)
    gate("S0a the baseline copy is byte-identical to the bed", md5(SCRATCH_B) == R["bed_md5_before"],
         os.path.basename(SCRATCH_B), fatal=True)
    safe("ensure_loaded(baseline)", lambda: g.ensure_loaded(SCRATCH_B))
    es = g.exec_state(SCRATCH_B)
    fact("S0 ExecState of an untouched copy of the bed = %r - RECORDED, NEVER a criterion (the bed is "
         "broken BY DESIGN, Pre-decided 89/97)" % es)
    n, wb, wa, es2 = bad_wire_count(SCRATCH_B, "S0 baseline")
    R["baseline_bad_wires"] = n
    R["baseline_exec_state"] = es
    R["baseline_exec_state_after_rbw"] = es2
    fact("S0 BASELINE broken-wire count on the bed's bytes = %d (Wire %d -> %d); ExecState %r -> %r"
         % (n, wb, wa, es, es2))
    safe("close_panel(baseline)", lambda: g.close_panel(SCRATCH_B))
    return n


def run_cells(labels, ar, baseline_bad):
    head("[CELLS] STEP 2 - THE MISSING CELL: Invoke on the SINK terminal, wire %d LEFT ALIVE" % ROWD_WIRE)
    results = {}
    for cell, auto in CELLS:
        if left_s() < 300:
            gate("cell %s had time to run" % cell, False, "%.0f s left of the deadline reserve" % left_s())
            continue
        head("[%s] `Auto Route?` %s - a FRESH copy of the bed, wire %d ALIVE" % (cell, auto, ROWD_WIRE))
        rec = {"cell": cell, "auto_route": auto, "delete_7506": False}
        scratch = os.path.join(g.CLAUDEDEV, "C84BED_%s_%s.vi" % (STAMP, cell.replace("-", "")))
        try:
            shutil.copyfile(BED, scratch)
            time.sleep(0.4)
            gate("%s the scratch is a byte-identical copy of the bed" % cell,
                 md5(scratch) == R["bed_md5_before"], os.path.basename(scratch), fatal=True)
            safe("ensure_loaded(%s)" % cell, lambda q=scratch: g.ensure_loaded(q))
            d_idx, trip = C82.resolve_triple(scratch, cell)
            rec["triple"] = trip
            passed, _r = one_call_and_gates(cell, scratch, d_idx, labels, ar, auto, baseline_bad, rec)
            rec["gate_s_passed"] = passed
            results[cell] = passed
            gate("%s GATE S passed IN FULL" % cell, passed, "%r" % rec.get("gate_s"))
        except Stop as e:
            rec["refused"] = "STOP %s" % e
            results[cell] = False
            gate("%s ran" % cell, False, str(e)[:160])
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            rec["refused"] = "%s: %s" % (type(e).__name__, str(e)[:250])
            rec["traceback"] = traceback.format_exc()[-1200:]
            results[cell] = False
            gate("%s ran" % cell, False, rec["refused"])
        finally:
            R["cells"][cell] = rec
            safe("close_panel(%s)" % os.path.basename(scratch), lambda q=scratch: g.close_panel(q))
            for _a in range(6):
                try:
                    if os.path.exists(scratch):
                        os.remove(scratch)
                    break
                except Exception:                                                  # noqa: BLE001
                    time.sleep(3.0)
            gate("%s scratch deleted" % cell, not os.path.exists(scratch), os.path.basename(scratch))
            dump()
    return results


# ======================================================================= [3] STEP 3 - land it
def step3(labels, ar, results, baseline_bad):
    head("[3] STEP 3 - the ONLY branch in this file")
    winners = [c for c, ok in results.items() if ok]
    R["step3"]["cells_passed"] = winners
    if not winners:
        gate("STEP 3 at least one cell passed GATE S in full (the brief's only branch)", False,
             "cells passed: %r - NOTHING IS SAVED, no third configuration is improvised" % (results,))
        fact("STEP 3 NOT TAKEN: neither cell passed GATE S. The raw values are above; the next move is "
             "judgement's. No file was written.")
        return
    if "S-T" in winners:
        auto = True
        why = ("BOTH cells passed - `Auto Route?` TRUE is used for the artefact, as the brief directs"
               if len(winners) == 2 else "S-T passed - `Auto Route?` TRUE")
    else:
        auto = False
        why = "only S-F passed - `Auto Route?` FALSE"
    R["step3"]["auto_route"] = auto
    R["step3"]["why"] = why
    fact("STEP 3 cells that passed: %r ; the artefact uses `Auto Route?` %r - %s" % (winners, auto, why))
    if left_s() < 240:
        gate("STEP 3 had time to run", False, "%.0f s left of the deadline reserve" % left_s())
        return
    head("[3] the artefact: a NEW file from the BED, which itself is left byte-unchanged")
    shutil.copyfile(BED, ART)
    time.sleep(0.4)
    gate("3a the artefact starts as a byte-identical copy of the bed", md5(ART) == R["bed_md5_before"],
         os.path.basename(ART), fatal=True)
    safe("ensure_loaded(artefact)", lambda: g.ensure_loaded(ART))
    d_idx, trip = C82.resolve_triple(ART, "3")
    R["step3"]["triple"] = trip
    rec1 = {"pass": "first"}
    p1, r1 = one_call_and_gates("3-P1", ART, d_idx, labels, ar, auto, baseline_bad, rec1, probe_bad=False)
    R["step3"]["pass1"] = rec1
    gate("3b GATE S (a)-(e, minus the d2 probe) on the FIRST pass", p1, "%r" % rec1.get("gate_s"))

    head("[3] THE ORDERED IDEMPOTENT SECOND PASS (Pre-decided 106): the SAME connect again, `wire_delta` 0, "
         "and the identity read on THAT pass")
    rec2 = {"pass": "second (ordered idempotent)"}
    p2, r2 = one_call_and_gates("3-P2", ART, d_idx, labels, ar, auto, baseline_bad, rec2, probe_bad=False)
    R["step3"]["pass2"] = rec2
    gate("3c the ordered SECOND pass is IDEMPOTENT: wire_delta 0", r2.get("wire_delta") == 0,
         "wire_delta %r (pass 1 was %r)" % (r2.get("wire_delta"), r1.get("wire_delta")))
    gate("3d GATE S (a)-(e, minus the d2 probe) RE-ASSERTED on the ordered second pass", p2,
         "%r" % rec2.get("gate_s"))

    head("[3] SAVE")
    es = g.exec_state(ART)
    R["step3"]["exec_state_before_save"] = es
    fact("3 ExecState of the artefact BEFORE the save = %r (the bed is broken BY DESIGN; this is RECORDED, "
         "never a criterion - 34(f): the artefact is NEVER run and never cold-loaded headless)" % es)
    if es == 1:
        size, serr = safe("3 g.save(ART) - script route", lambda: g.save(ART))
        route = "SCRIPT (COM SaveInstrument) - ExecState 1"
    else:
        size, serr = safe("3 g.save(ART, allow_broken=True) - the approved broken-intermediate route",
                          lambda: g.save(ART, allow_broken=True))
        route = ("GUI_SAVE (gscript.save -> gui_save: block-diagram window fronted, click-probed, Ctrl+S, "
                 "mtime verified; CLAUDE.md §3 item 6, user 2026-09-22 broken-intermediate save)")
    R["step3"]["save_route"] = route
    R["step3"]["save_error"] = serr
    gate("3e the artefact was SAVED (%s)" % route, bool(size) and not serr,
         "returned %r ; error %r" % (size, serr))
    if not os.path.isfile(ART):
        gate("3f the artefact is on disk", False, ART)
        return
    R["step3"]["path"] = ART
    R["step3"]["md5"] = md5(ART)
    R["step3"]["bytes"] = os.path.getsize(ART)
    g.reset()
    time.sleep(1.5)
    es2 = g.exec_state(ART)
    R["step3"]["exec_state_after_save"] = es2
    fact("3 ARTEFACT %s md5 %s (%d bytes) ExecState after the save %r ; save route: %s"
         % (ART, R["step3"]["md5"], R["step3"]["bytes"], es2, route))

    head("[3] GATE S(d2) on a THROWAWAY COPY of the SAVED artefact - the artefact itself never passes "
         "through Remove Bad Wires")
    shutil.copyfile(ART, SCRATCH_P)
    time.sleep(0.4)
    safe("ensure_loaded(probe copy)", lambda: g.ensure_loaded(SCRATCH_P))
    n_bad, wb, wa, es3 = bad_wire_count(SCRATCH_P, "3 (d2)")
    R["step3"]["bad_wires"] = n_bad
    gate("3g GATE S(d2) on the artefact: the diagram-wide broken-wire count is NOT HIGHER than the bed's "
         "baseline", n_bad <= baseline_bad,
         "artefact %d vs baseline %d (Wire %d -> %d on the probe copy; its ExecState after RBW %r)"
         % (n_bad, baseline_bad, wb, wa, es3))
    safe("close_panel(probe copy)", lambda: g.close_panel(SCRATCH_P))


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close panels, delete every scratch, re-read every pin, handles at both ends")
    for p in SCRATCHES + [OP0, OP1, ART] + sorted(glob.glob(os.path.join(g.CLAUDEDEV, "C84BED_%s_*.vi" % STAMP))):
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
    for p in SCRATCHES + sorted(glob.glob(os.path.join(g.CLAUDEDEV, "C84BED_%s_*.vi" % STAMP))):
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
    R["op0_md5_after"] = md5(OP0) if os.path.isfile(OP0) else "MISSING"
    gate("H3b OpFsInnerTunnelConnect_v0.vi md5 UNCHANGED (never modified, never deleted)",
         R["op0_md5_after"] == OP0_MD5, "%s" % R["op0_md5_after"])
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6 nothing was REMOVED from claudeDev", not gone, "removed %r" % (gone,))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    for p in (OP1, ART):
        if os.path.isfile(p):
            fact("ON DISK %s md5 %s (%d bytes)" % (p, md5(p), os.path.getsize(p)))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("build_d1_m3a3b_d3 - D-3 of M3a-3b: v1 (roles exchanged), the missing cell (wire 7506 ALIVE), "
          "and Row D if GATE S passes", flush=True)
    print("=" * 100, flush=True)
    try:
        phase_files()
        phase_restart()
        labels, ar = build_v1()
        dump()
        gates_23(labels, ar)
        dump()
        baseline = baseline_bad_wires()
        results = run_cells(labels, ar, baseline)
        dump()
        step3(labels, ar, results, baseline)
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
