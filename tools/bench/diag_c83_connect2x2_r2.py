r"""diag_c83_connect2x2_r2.py - cycle-83 MATERIAL, D-2b run 2. THE THREE COLUMNS RUN 1 COULD NOT FILL.

Run 1 (`tools/bench/diag_c83_connect2x2.log`, 37 pass / 5 fail, rc=1, 173 s) answered the trivial 2x2 and
refuted (b) on the real pair, and left exactly three holes. This run fills them and NOTHING ELSE. No new
op, no fifth configuration, no other method id, and the winning configuration is still NOT applied to the
op on disk.

 HOLE 1 - STEP 0's repair landed in the WRONG PLACE, measured: the Invoke's `error out` chain is
   `Invoke #757 -> Property #241 -> Property #242 -> Clear Errors.vi #399` (`diag_c83_connect2x2.log:29`),
   so the only FREE `error out` in it is Clear Errors' OWN output - i.e. run 1's new indicator
   `error out 7` sits AFTER the errors are cleared and can never show the Invoke's error. REPAIR: delete
   the Clear-Errors -> `error out 7` wire and BRANCH the Invoke's RAW `error out` (w1027) onto that same
   indicator with `gscript.wire_indicators`:1786, whose docstring describes exactly this topology
   ("wiring a node's already-sunk `error out` gives the indicator the error value while the Clear Errors
   sink stays attached"). Re-assert ExecState 1, re-save, report the md5.
 HOLE 2 - a NEW FACT run 1 produced and could not attribute: on the real pair the op's SOURCE HALF now
   RAISES `error 1055: To More Specific Class in UID to GObject Reference.vi` (+ 1055 on all three
   Property stages), `term_uid` and `uid_back` both stay at their poison 0 - where cycle 82 recorded
   `term_uid` 7488 / `uid_back` 7468 with every column empty. Run 1 changed TWO things at once (the op was
   edited, and wire 7506 was deleted before the call), so it cannot say which. THE CHEAPEST DISCRIMINATING
   TEST, and the only new cell here: cell R0 = the SAME call on a bed scratch with wire 7506 STILL ALIVE
   (cycle 82's arm 1, which returned 7488 on 20/20 calls). 1055 there too => the edit; 7488 there =>
   deleting 7506 is what makes the FSIT uid unresolvable.
 HOLE 3 - the A cells (Invoke on the FSIT terminal = explanation (a)) were REFUSED: the swapped scratch
   op came out ExecState 0. Run 1 measured why - deleting the two Invoke feed NETS also killed their OTHER
   consumers (`diag_c83_connect2x2.log:82`: `(241, 'reference')` and `(187, 'reference')` left unwired).
   REPAIR: record EVERY sink terminal on both nets first, and after the crosswise re-connect re-BRANCH
   each non-Invoke consumer onto its original source.

THE MANDATORY FAILED-PREDICTION REVIEW IS ANSWERED AND ITS TESTS ARE BUILT INTO THIS RUN
(`archive/peer/2026-09-22-c83-2x2-swap-1055-r2.md`, claude / role `hypothesis` / opus max, ANSWERED 403 s):
 * its STRONGEST point, accepted: the border-terminal row run 1 gated on carries `wire_err: 1055`, so
   `wire: 0` there is THE ERROR PATH'S DEFAULT, not a measurement - and it is already 1055 BEFORE the
   delete. Every cell here therefore GATES on `wire_err == 0` and prints every `*_err` field of the row.
 * its test 1 (rank 1), accepted: move the error tap UPSTREAM of Clear Errors - this run's [S0].
 * its claim-3 alternative, accepted as a variable: the POISON PASS itself may be what makes the op
   resolve UID 0 -> `error 1055` in `UID to GObject Reference.vi`. Cells R0 (poison ON) and R0b (poison
   OFF) are the same call and differ only in that.
 * its test 3 (claim 4's alternative), in the only form this fleet can run: after the crosswise re-wire,
   Remove Bad Wires is run and the Wire count compared - a type-broken `reference` feed would be removed.
 * NOT acted on (judgement's, recorded only): its warning that `Terminals[1]` being the register's outer
   terminal is confirmed only by the NODE uid echo, and that re-branching a consumer onto a convenient
   source can be legal without being equivalent (rule 1a).

CELLS (each on its OWN dated scratch COPY of the bed, deleted in this run; nothing saved from any of them)
  R0  control  op as on disk, wire 7506 ALIVE, no delete         - does the FSIT uid still resolve?
  R1  B2       op as on disk, 7506 deleted                       - today's configuration, RAW Invoke error
  R2  B1       C83ARFSIT (Auto Route TRUE), 7506 deleted
  R3  A2       C83SWAPFSIT (roles EXCHANGED, Auto Route FALSE), 7506 deleted
  R4  A1       C83SWAPFSIT (roles EXCHANGED, Auto Route TRUE), 7506 deleted
For any cell that creates a wire: the new net's SOURCE TERMINAL OWNER from `OpWireSource_v5`, whether
`#4334` is off the net, PD85 violations, `Wire.Is Broken?`.

WHAT ALREADY EXISTS: `tools/bench/diag_c83_connect2x2.py` (run 1) supplies `fsit_call`, `invoke_node`,
`attach_auto_route`, `ind_labels`; `tools/recipes/build_opfsinnertunnelconnect_v0.py` supplies the pins,
`md5`, `del_wire`, `resolve_triple`; `build_opconnectnested_v1` supplies `walk`/`term`/`src_of`/`idx`/
`connect`; `gscript.wire_indicators`:1786 is the branch primitive. Nothing is re-implemented.

HYGIENE: bed md5 pinned at entry AND exit; five pins; LabVIEW restarted first; every scratch deleted;
FILES LEFT ON DISK == []. RIG 조립 - no motor, no ASI, no camera.
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
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles, restart_labview                            # noqa: E402
from build_opconnectnested_v1 import walk, term, src_of, idx, Stop                  # noqa: E402
from build_opconnectnested_v1 import connect as wire_by_name                        # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS              # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                       # noqa: E402
import diag_c83_connect2x2 as R1                                                    # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "diag_c83_connect2x2_r2.json")

OP, V5, MAP = C82.OP, C82.V5, C82.MAP_OUT
BED, BED_MD5, BED_BYTES = C82.BED, C82.BED_MD5, C82.BED_BYTES
PINS = C82.PINS
FSIT_UID, LEFT_TERM = C82.FSIT_UID, C82.LEFT_TERM_EXPECT
ROWD_WIRE = C82.ROWD_WIRE
LOOP_NODES_IDX, LOOP_TERM_IDX = C82.LOOP_NODES_IDX, C82.LOOP_TERM_IDX
RSR_EXPECT, OLD_SOURCE = C82.RSR_EXPECT, C82.OLD_SOURCE
OP_MD5_IN = "cda1e36ee394ccd6bf0f1c1108d76249"      # what run 1's STEP 0 left on disk

STAMP = time.strftime("%Y%m%d_%H%M%S")
S_ARF = os.path.join(g.CLAUDEDEV, "C83bARFSIT_%s.vi" % STAMP)
S_SWAP = os.path.join(g.CLAUDEDEV, "C83bSWAP_%s.vi" % STAMP)
SCRATCHES = [S_ARF, S_SWAP]

# (cell, op selector, delete 7506?, auto route, poison the readouts?)
CELLS = [("R0", "op", False, None, True), ("R0b", "op", False, None, False),
         ("R1", "op", True, None, False), ("R2", "arf", True, True, False),
         ("R3", "swap", True, False, False), ("R4", "swap", True, True, False)]
CELL_NOTE = {"R0": "CONTROL - 7506 ALIVE, today's roles, POISON ON (cycle 82's arm 1)",
             "R0b": "CONTROL - 7506 ALIVE, today's roles, POISON OFF (the review's artefact test)",
             "R1": "B2 - today's roles, 7506 deleted, Auto Route default FALSE, poison OFF",
             "R2": "B1 - today's roles + Auto Route TRUE, poison OFF",
             "R3": "A2 - roles EXCHANGED (Invoke on the FSIT terminal), Auto Route FALSE",
             "R4": "A1 - roles EXCHANGED, Auto Route TRUE"}

RUN_DEADLINE_S = 32 * 60.0
RESERVE_S = 300.0
T0 = time.time()
passes, fails, facts = [], [], []
Rr = {"script": os.path.abspath(__file__), "stamp": STAMP, "op": OP, "bed": BED,
      "task": "D-2b run 2: the raw-Invoke-error repair, the 1055 control, and the A cells",
      "verification_level": "FUNCTIONAL - real data through real ops into real scratch copies of the bed",
      "S0": {}, "cells": {}, "H": {}}
md5 = C82.md5


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
    Rr["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    Rr["facts"] = facts
    Rr["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(Rr, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


def fsit_call2(op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term,
               ar_label="", auto_route=None, inv_err_label="", poison=True):
    """`diag_c83_connect2x2.fsit_call` with the POISON PASS made optional - the review
    (`archive/peer/2026-09-22-c83-2x2-swap-1055-r2.md`, claim 3) names the poison itself as the leading
    artefact candidate for the new `error 1055`, so it has to be a variable, not a constant."""
    w0 = g.count(target, "Wire")
    i0 = g.count(target, "Invoke")
    vi = g.op(op_path)
    if poison:
        for k, v in ((labels["term_uid"], 0), (labels["uid_back"], 0), (labels["sink_wire_uid"], 0),
                     (labels["is_broken"], True), ("UID", 0), ("Name", "POISON")):
            try:
                vi.SetControlValue(k, v)
            except Exception:                                                      # noqa: BLE001
                pass
        for k in (inv_err_label, "error out"):
            if k:
                try:
                    vi.SetControlValue(k, (True, 999999, "POISON - not overwritten by the run"))
                except Exception:                                                  # noqa: BLE001
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
    out = {"err": err, "op": os.path.basename(op_path), "auto_route": auto_route, "poisoned": poison}
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


# ======================================================================= [0] files + restart
def phase_files():
    head("[0] FILES ONLY - pins, the bed's md5, the op run 1 left on disk")
    got = md5(BED)
    Rr["bed_md5_before"] = got
    gate("H1 bed md5 before == %s (%d B)" % (BED_MD5, BED_BYTES),
         got == BED_MD5 and os.path.getsize(BED) == BED_BYTES, "got %s" % got, fatal=True)
    Rr["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        Rr["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    Rr["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    Rr["op_md5_before"] = md5(OP)
    fact("the op on disk: %s md5 %s (%d bytes)"
         % (os.path.basename(OP), Rr["op_md5_before"], os.path.getsize(OP)))
    gate("F0 the op on disk is the one run 1's STEP 0 saved (%s)" % OP_MD5_IN,
         Rr["op_md5_before"] == OP_MD5_IN, Rr["op_md5_before"])


def phase_restart():
    head("[1] RESTART LabVIEW")
    before, _ = safe("handles before restart", labview_handles)
    Rr["H"]["handles_before_restart"] = before
    fact("LabVIEW handle count BEFORE the restart: %r" % before)
    safe("restart_labview", restart_labview)
    g.reset()
    time.sleep(3.0)
    after, _ = safe("handles after restart", labview_handles)
    Rr["H"]["handles_after_restart"] = after
    fact("LabVIEW handle count AFTER the restart: %r" % after)


# ======================================================================= [S0] the RAW error repair
def step0_raw_error():
    head("[S0] HOLE 1 - move `error out 7` from AFTER Clear Errors to a BRANCH of the Invoke's RAW "
         "`error out`")
    g.ensure_loaded(OP)
    n_inv, u_inv, rows, w = R1.invoke_node(OP)
    r_eo = term(rows, "error out", True)
    Rr["S0"]["invoke"] = {"nodes_index": n_inv, "uid": u_inv, "error_out_wire": (r_eo or {}).get("wire")}
    fact("S0 the Invoke #%s `error out` carries w%r" % (u_inv, (r_eo or {}).get("wire")))
    # the Clear Errors node at the end of the chain, and the wire feeding `error out 7`
    ce = [u for u, (n, lab, rr) in w.items() if str(lab).startswith("Clear Errors")]
    fact("S0 Clear Errors node(s) on the op's diagram: %r" % ce)
    killed = []
    for u in ce:
        n, _lab, rr = w[u]
        t_out = term(rr, "error out", True)
        if t_out and t_out.get("wire"):
            ok, _e = safe("S0 delete Clear Errors #%s `error out` net w%r" % (u, t_out["wire"]),
                          lambda q=t_out["wire"]: C82.del_wire(OP, q, "S0 "))
            killed.append((u, t_out["wire"], bool(ok)))
    Rr["S0"]["cleared_wires"] = killed
    fact("S0 deleted the Clear-Errors -> indicator net(s): %r" % killed)
    safe("S0 remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(OP))
    inv_idx, e = safe("S0 idx(Invoke #%s)" % u_inv, lambda: idx(OP, "Invoke", u_inv), None)
    ok = False
    if inv_idx is not None:
        _r, e2 = safe("S0 wire_indicators(Invoke[%d].`error out` -> 'error out 7')" % inv_idx,
                      lambda: g.wire_indicators(OP, inv_idx, ["error out"], ["error out 7"],
                                                diagram_index=0, node_class="Invoke"))
        ok = not e2
    es = g.exec_state(OP)
    Rr["S0"]["exec_state"] = es
    # PROVE the branch: the indicator's wire must be the Invoke's own error-out wire
    rows2 = R1.invoke_node(OP)[2]
    r_eo2 = term(rows2, "error out", True)
    Rr["S0"]["invoke_error_out_wire_after"] = (r_eo2 or {}).get("wire")
    fact("S0 AFTER: the Invoke's `error out` carries w%r (it was w%r); ExecState %r"
         % ((r_eo2 or {}).get("wire"), (r_eo or {}).get("wire"), es))
    gate("S0a the raw-error branch was made", ok, "wire_indicators ok %r" % ok)
    gate("S0b ExecState 1 after the repair", es == 1, "ExecState %r" % es)
    if es != 1:
        fact("S0 NOT SAVED - the op is left exactly as run 1 saved it")
        return False
    size = g.save(OP)
    g.reset()
    time.sleep(1.5)
    es2 = g.exec_state(OP)
    Rr["S0"]["op_md5_after"] = md5(OP)
    Rr["S0"]["op_bytes_after"] = size
    fact("S0 SAVED %s (%s bytes) md5 %s -> %s"
         % (os.path.basename(OP), size, Rr["op_md5_before"], Rr["S0"]["op_md5_after"]))
    gate("S0c ExecState 1 re-read AFTER the save", es2 == 1, "ExecState %r" % es2)
    return es2 == 1


# ======================================================================= [S] the two op variants
def make_arf():
    head("[S-ARF] scratch copy of the op + an `Auto Route?` control")
    shutil.copyfile(OP, S_ARF)
    time.sleep(0.3)
    g.ensure_loaded(S_ARF)
    ar, note = R1.attach_auto_route(S_ARF, "S-ARF")
    es = g.exec_state(S_ARF)
    Rr["arf"] = {"auto_route_label": ar, "note": note, "exec_state": es}
    gate("S-ARF the AR copy is legal (ExecState 1)", es == 1, "ExecState %r ; AR %r" % (es, ar))
    if es == 1 and ar:
        g.save(S_ARF)
        g.reset()
        time.sleep(1.0)
        return ar, True
    return ar, False


def make_swap():
    head("[S-SWAP] scratch copy with the Invoke's `reference` and `Wire Source` feeds EXCHANGED - and "
         "EVERY OTHER CONSUMER of both nets re-branched (run 1's ExecState-0 cause)")
    shutil.copyfile(OP, S_SWAP)
    time.sleep(0.3)
    g.ensure_loaded(S_SWAP)
    n_inv, u_inv, rows, w = R1.invoke_node(S_SWAP)
    r_ref, r_ws = term(rows, "reference", False), term(rows, "Wire Source", False)
    if not (r_ref and r_ws and r_ref.get("wire") and r_ws.get("wire")):
        gate("S-SWAP the swapped copy could be built", False, "%r / %r" % (r_ref, r_ws))
        return "", False
    w_ref, w_ws = r_ref["wire"], r_ws["wire"]

    def net(wire):
        src_u = src_of(w, wire)
        src_n = next((x["name"] for x in w[src_u][2] if x["is_source"] and x["wire"] == wire), None)
        sinks = [(u, x["name"]) for u, (_n, _l, rr) in w.items() for x in rr
                 if (not x["is_source"]) and x["wire"] == wire]
        return src_u, src_n, sinks

    su_ref, sn_ref, sk_ref = net(w_ref)
    su_ws, sn_ws, sk_ws = net(w_ws)
    fact("S-SWAP net w%s: source #%s.%r ; sinks %r" % (w_ref, su_ref, sn_ref, sk_ref))
    fact("S-SWAP net w%s: source #%s.%r ; sinks %r" % (w_ws, su_ws, sn_ws, sk_ws))
    Rr["swap_before"] = {"reference_net": [w_ref, su_ref, sn_ref, sk_ref],
                         "wire_source_net": [w_ws, su_ws, sn_ws, sk_ws]}
    ok = True
    for wu in (w_ref, w_ws):
        _r, e = safe("S-SWAP delete net w%r" % wu, lambda q=wu: C82.del_wire(S_SWAP, q, "S-SWAP "))
        ok = ok and not e
    safe("S-SWAP remove_bad_wires_scripted", lambda: g.remove_bad_wires_scripted(S_SWAP))
    # 1) the CROSSED feeds into the Invoke
    plan = [(su_ref, sn_ref, u_inv, "Wire Source", False), (su_ws, sn_ws, u_inv, "reference", False)]
    # 2) every OTHER consumer back onto its original source, as a BRANCH
    for (src_u, src_n, sinks) in ((su_ref, sn_ref, sk_ref), (su_ws, sn_ws, sk_ws)):
        for (du, dn) in sinks:
            if du == u_inv:
                continue
            plan.append((src_u, src_n, du, dn, True))
    for (su, sn, du, dn, br) in plan:
        _r, e = safe("S-SWAP connect #%s.%r -> #%s.%r (branch=%r)" % (su, sn, du, dn, br),
                     lambda a=su, b=sn, c=du, d=dn, f=br:
                     wire_by_name(S_SWAP, a, b, c, d, branch=f, tag="S-SWAP "))
        ok = ok and not e
    ar, note = R1.attach_auto_route(S_SWAP, "S-SWAP")
    es = g.exec_state(S_SWAP)
    Rr["swap"] = {"rewire_ok": ok, "auto_route_label": ar, "note": note, "exec_state": es,
                  "plan": [(a, b, c, d, e2) for a, b, c, d, e2 in plan]}
    # THE REVIEW'S TEST 3 in the only form this fleet can run: if the crossed wires are BROKEN by a type
    # mismatch (`reference` is typed `Terminal`, `Wire Source` is the wide `GObject`), Remove Bad Wires
    # deletes them and the Wire count drops. A drop of 0 means they are legal wires.
    wc0 = g.count(S_SWAP, "Wire")
    safe("S-SWAP remove_bad_wires probe", lambda: g.remove_bad_wires_scripted(S_SWAP))
    wc1 = g.count(S_SWAP, "Wire")
    Rr["swap"]["broken_wire_probe"] = {"wires_before": wc0, "wires_after_remove_bad": wc1,
                                       "removed": wc0 - wc1}
    fact("S-SWAP BROKEN-WIRE PROBE (the review's claim-4 alternative): Remove Bad Wires took the Wire "
         "count %d -> %d (removed %d). 0 removed = the crossed wires are NOT type-broken."
         % (wc0, wc1, wc0 - wc1))
    es = g.exec_state(S_SWAP)
    Rr["swap"]["exec_state_after_probe"] = es
    if es != 1:
        w2 = walk(S_SWAP, 0)
        orphans = [(u, r["name"]) for u in w2 for r in w2[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        fact("S-SWAP DIAGNOSTIC unwired non-error SINK terminals: %r" % orphans)
    gate("S-SWAP the SWAPPED copy is legal (ExecState 1) - LabVIEW accepts the exchanged roles at EDIT "
         "time", es == 1, "ExecState %r ; rewire ok %r ; AR %r" % (es, ok, ar))
    if es == 1 and ok:
        g.save(S_SWAP)
        g.reset()
        time.sleep(1.0)
        return ar, True
    return ar, False


# ======================================================================= the cells
def run_cells(labels, arf_label, arf_ok, swap_label, swap_ok):
    head("[CELLS] each on its OWN dated scratch COPY of the bed")
    for cell, sel, do_del, auto, poison in CELLS:
        if left_s() < 150:
            gate("cell %s had time to run" % cell, False, "%.0f s left" % left_s())
            continue
        head("[%s] %s" % (cell, CELL_NOTE[cell]))
        rec = {"cell": cell, "note": CELL_NOTE[cell], "delete_7506": do_del, "auto_route": auto,
               "poison": poison}
        if sel == "op":
            op_path, ar_lab, ready = OP, "", True
        elif sel == "arf":
            op_path, ar_lab, ready = S_ARF, arf_label, arf_ok
        else:
            op_path, ar_lab, ready = S_SWAP, swap_label, swap_ok
        rec["op_variant"] = os.path.basename(op_path)
        if not ready:
            rec["refused"] = "REFUSED BY CONSTRUCTION: %s could not be built" % os.path.basename(op_path)
            fact("%s %s" % (cell, rec["refused"]))
            Rr["cells"][cell] = rec
            gate("%s ran" % cell, False, rec["refused"])
            continue
        scratch = os.path.join(g.CLAUDEDEV, "C83bBED_%s_%s.vi" % (STAMP, cell))
        try:
            shutil.copyfile(BED, scratch)
            time.sleep(0.4)
            gate("%s the scratch is a byte-identical copy of the bed" % cell,
                 md5(scratch) == Rr["bed_md5_before"], os.path.basename(scratch), fatal=True)
            safe("ensure_loaded(%s)" % cell, lambda q=scratch: g.ensure_loaded(q))
            d_idx, trip = C82.resolve_triple(scratch, cell)
            rec["triple"] = trip
            if do_del:
                C82.del_wire(scratch, ROWD_WIRE, "%s " % cell)
                g.remove_bad_wires_scripted(scratch)
            _u, trows = g.node_terms_uid(scratch, d_idx, LOOP_NODES_IDX)
            before = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
            rec["border_before"] = before
            rec["border_before_err"] = {k: v for k, v in (before or {}).items() if k.endswith("_err")}
            fact("%s border t%d BEFORE the call: wire=%r ERROR CODES %r (7506 deleted: %r)"
                 % (cell, LOOP_TERM_IDX, (before or {}).get("wire"), rec["border_before_err"], do_del))
            gate("%s the border terminal's own `Wire` property read returned NO error (the review's "
                 "strongest point: a 1055 there makes `wire 0` the error path's default, not a "
                 "measurement)" % cell, (before or {}).get("wire_err") == 0,
                 "wire_err %r" % (before or {}).get("wire_err"))
            r = fsit_call2(op_path, labels, scratch, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                           ar_label=ar_lab, auto_route=(auto if ar_lab else None),
                           inv_err_label="error out 7", poison=poison)
            rec.update(r)
            _u, trows = g.node_terms_uid(scratch, d_idx, LOOP_NODES_IDX)
            after = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
            neww = (after or {}).get("wire")
            rec["border_after"] = after
            rec["border_after_err"] = {k: v for k, v in (after or {}).items() if k.endswith("_err")}
            rec["wire_created"] = bool(neww) and neww != (before or {}).get("wire")
            fact("%s RESULT: RAW INVOKE ERROR=%r | op_err=%r | term_uid=%r uid_back=%r | "
                 "err_uidvi=%r err_fsit=%r | `UID 2`=%r border_wire=%r (was %r) wire_delta=%r "
                 "junk_Invoke=%r is_broken=%r"
                 % (cell, r.get("invoke_err"), r.get("err"), r.get("term_uid"), r.get("uid_back"),
                    r.get("err_uidvi"), r.get("err_fsit"), r.get("sink_wire_uid"), neww,
                    (before or {}).get("wire"), r.get("wire_delta"), r.get("invoke_delta"),
                    r.get("is_broken")))
            gate("%s the FSIT uid %d still resolves to LeftTerm #%d (term_uid echo)"
                 % (cell, FSIT_UID, LEFT_TERM), r.get("term_uid") == LEFT_TERM,
                 "term_uid %r ; err_uidvi %r" % (r.get("term_uid"), r.get("err_uidvi")))
            if do_del:
                gate("%s the border terminal went BARE -> NON-ZERO" % cell, bool(neww), "wire %r" % neww)
            if neww and do_del:
                walkr, werr = safe("%s OpWireSource_v5(w%r)" % (cell, neww),
                                   lambda q=neww: WIRE_TERMS(scratch, int(q), n=8), [])
                M.print_walk(cell, neww, walkr, werr)
                bad = M.pd85_violations(neww, walkr)
                owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid")))
                                 for t in (walkr or []) if t.get("owner_uid")})
                src_owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid")))
                                     for t in (walkr or []) if t.get("is_source") and t.get("owner_uid")})
                rec["source_owners"], rec["all_owners"] = src_owners, owners
                rec["pd85_violations"] = len(bad)
                rec["old_source_off_net"] = all(u != OLD_SOURCE for _c, u in owners)
                fact("%s NEW NET w%r: source-terminal owners %r ; every owner %r ; PD85 %d ; #%d off the "
                     "net %r ; op `Is Broken?` %r"
                     % (cell, neww, src_owners, owners, len(bad), OLD_SOURCE,
                        rec["old_source_off_net"], r.get("is_broken")))
                gate("%s the net's SOURCE TERMINAL OWNER is RightShiftRegister #%d and nothing else is a "
                     "source" % (cell, RSR_EXPECT),
                     src_owners == [("RightShiftRegister", RSR_EXPECT)], "%r" % (src_owners,))
        except Stop as e:
            rec["refused"] = "STOP %s" % e
            gate("%s ran" % cell, False, str(e)[:160])
        except Exception as e:                                                     # noqa: BLE001
            rec["refused"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            gate("%s ran" % cell, False, rec["refused"])
        finally:
            Rr["cells"][cell] = rec
            safe("close_panel(%s)" % os.path.basename(scratch), lambda q=scratch: g.close_panel(q))
            for _a in range(6):
                try:
                    if os.path.exists(scratch):
                        os.remove(scratch)
                    break
                except Exception:                                                  # noqa: BLE001
                    time.sleep(3.0)
            gate("%s bed scratch deleted" % cell, not os.path.exists(scratch), os.path.basename(scratch))
            dump()


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE")
    for p in SCRATCHES + [OP]:
        safe("close_panel(%s)" % os.path.basename(p), lambda q=p: g.close_panel(q))
    Rr["H"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts: %r" % Rr["H"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         Rr["H"]["ref_counts"]["live"] == 0, "%r" % Rr["H"]["ref_counts"])
    handles, _ = safe("handles after the work", labview_handles)
    Rr["H"]["handles_after_work"] = handles
    fact("LabVIEW handle count AFTER the work: %r" % handles)
    safe("restart_labview before the deletes", restart_labview)
    g.reset()
    time.sleep(2.0)
    for p in SCRATCHES + sorted(glob.glob(os.path.join(g.CLAUDEDEV, "C83b*_%s*.vi" % STAMP))):
        if not os.path.exists(p):
            continue
        for _a in range(6):
            try:
                os.remove(p)
                break
            except Exception as e:                                                 # noqa: BLE001
                fact("delete %s failed: %s" % (os.path.basename(p), str(e)[:110]))
                time.sleep(4.0)
        gate("H4 scratch deleted: %s" % os.path.basename(p), not os.path.exists(p), p)
    got = md5(BED)
    Rr["bed_md5_after"] = got
    gate("H2 bed md5 UNCHANGED after the run", got == Rr.get("bed_md5_before"),
         "before %s / after %s" % (Rr.get("bed_md5_before"), got))
    allpins = True
    Rr["pins_after"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        Rr["pins_after"][label] = have
        allpins = allpins and (have == want)
        fact("PIN AFTER  %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the five md5 pins all hold", allpins)
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(Rr.get("claudedev_before") or []))
    gone = sorted(set(Rr.get("claudedev_before") or []) - set(after))
    gate("H6 THE FILES THIS RUN LEFT ON DISK == [] and nothing was removed", not added and not gone,
         "added %r removed %r" % (added, gone))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    if os.path.isfile(OP):
        Rr["H"]["op_md5_final"] = md5(OP)
        fact("THE OP AT EXIT: %s md5 %s (%d bytes)"
             % (os.path.basename(OP), Rr["H"]["op_md5_final"], os.path.getsize(OP)))
    handles2, _ = safe("handles final", labview_handles)
    Rr["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r" % handles2)


def summary():
    head("THE CELL TABLE (run 2)")
    print("  %-4s %-52s %-30s %-9s %-9s %-9s %-5s"
          % ("cell", "note", "RAW Invoke error", "term_uid", "created?", "UID 2", "junk"), flush=True)
    for cell, _s, _d, _a, _p in CELLS:
        c = Rr["cells"].get(cell) or {}
        if c.get("refused"):
            print("  %-4s %-52s REFUSED: %s" % (cell, CELL_NOTE[cell][:52], str(c["refused"])[:70]),
                  flush=True)
            continue
        print("  %-4s %-52s %-30s %-9s %-9s %-9s %-5s"
              % (cell, CELL_NOTE[cell][:52], str(c.get("invoke_err") or "(no error)")[:30],
                 c.get("term_uid"), c.get("wire_created"), c.get("sink_wire_uid"),
                 c.get("invoke_delta")), flush=True)
        if c.get("source_owners") is not None:
            print("        owners: source %r ; PD85 %r ; #%d off net %r ; Is Broken? %r"
                  % (c.get("source_owners"), c.get("pd85_violations"), OLD_SOURCE,
                     c.get("old_source_off_net"), c.get("is_broken")), flush=True)
        print("        poison=%r | border BEFORE wire=%r err=%r | border AFTER wire=%r err=%r"
              % (c.get("poison"), (c.get("border_before") or {}).get("wire"), c.get("border_before_err"),
                 (c.get("border_after") or {}).get("wire"), c.get("border_after_err")), flush=True)
        print("        err_uidvi=%r err_fsit=%r err_termuid=%r err_uidback=%r"
              % (c.get("err_uidvi"), c.get("err_fsit"), c.get("err_termuid"), c.get("err_uidback")),
              flush=True)


def main():
    print("=" * 100, flush=True)
    print("diag_c83_connect2x2_r2 - the raw-Invoke-error repair, the 1055 control, and the A cells",
          flush=True)
    print("=" * 100, flush=True)
    try:
        g._lv = None
        phase_files()
        phase_restart()
        step0_raw_error()
        dump()
        labels = json.load(open(MAP, encoding="utf-8"))
        arf_label, arf_ok = make_arf()
        swap_label, swap_ok = make_swap()
        dump()
        run_cells(labels, arf_label, arf_ok, swap_label, swap_ok)
    except Stop as e:
        gate("STOP at gate: %s" % e, False)
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        Rr["fatal"] = traceback.format_exc()[-2500:]
        print("\nOBSERVED EXC %s\n%s" % (str(e)[:300], traceback.format_exc()[-2000:]), flush=True)
        gate("the run completed without an unhandled exception", False, str(e)[:160])
    finally:
        try:
            phase_hygiene()
        except Exception as e:                                                     # noqa: BLE001
            import traceback
            Rr["hygiene_fatal"] = traceback.format_exc()[-1500:]
            gate("H-HYGIENE the hygiene phase completed", False, str(e)[:150])
        try:
            summary()
        except Exception as e:                                                     # noqa: BLE001
            print("summary raised %s" % str(e)[:200], flush=True)
        dump()
    print("\n" + "=" * 100, flush=True)
    print("GATES: %d pass / %d fail%s"
          % (len(passes), len(fails), (("  FAILING: " + ", ".join(fails)) if fails else "")), flush=True)
    print("JSON: %s   elapsed %.1f s" % (OUT, time.time() - T0), flush=True)
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main())
