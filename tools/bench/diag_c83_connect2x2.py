r"""diag_c83_connect2x2.py - cycle-83 MATERIAL, D-2b of M3a-3b.

ONE MEASUREMENT that separates the three surviving explanations for gate 4's silent decline
(`archive/peer/2026-09-22-c82-bare-source.md`):
  (a) the ROLES are inverted for CREATION (`Wire Source` is the wire's ORIGINAL SOURCE; the op passes the
      SINK #7488 as `Wire Source` while the Invoke sits on the SOURCE terminal),
  (b) `Auto Route?` is at its default FALSE and NO op in the fleet wires it,
  (c) the Invoke's OWN `error out` may never reach the op's `error out`, so "silent" is so far only "quiet".

    MATERIAL=1 py tools/bgrun.py --max-min 75 --log tools/bench/diag_c83_connect2x2.log \
        -- py -u tools/bench/diag_c83_connect2x2.py

WHAT ALREADY EXISTS - checked by READING the files before a line was written (CLAUDE.md "before creating
any new op, tool or recipe"):
  * `tools/recipes/build_opfsinnertunnelconnect_v0.py` - imported WHOLE as `C82`: its pins, bed constants,
    `md5`, `del_wire`, `resolve_triple`, `purge_junk`, `fsit_connect`. Nothing here re-implements them; the
    only new function is `fsit_call()`, which is `C82.fsit_connect` PARAMETERISED BY OP PATH (the module
    global `OP` is hard-wired there and this run drives three op variants).
  * `tools/recipes/build_opconnectnested_v1.py` - `walk` / `term` / `src_of` / `connect` / `del_net` / `Stop`.
  * `tools/recipes/build_opconnectfromwire_v0.py` - `wire_source_owner` = the REPAIRED `OpWireSource_v5`
    driver (uid-echo-checked), the only accepted identity reader.
  * `tools/gscript.py` - `create_control`:2468 (returns the LABEL LabVIEW gave), `create_indicator`:2496,
    `build_property`:2267, `node_terms_uid`:955, `count`:1035, `save`:2135, `exec_state`:2007,
    `remove_bad_wires_scripted`:2594, `ref_counts`:233. `connect_terminals`:2518 is the PRIMITIVE this run
    exercises on the trivial VI - driven through a scratch COPY of its op `OpConnect_v0.vi` so that
    `Auto Route?` can be SET (no op on disk exposes it: measured, not assumed - gate S1c).
  * `tools/recipes/build_empty_vi.py` - `EMPTY_v0.vi`, the empty runnable VI the trivial scratch is cut from.
  * PRIOR ART for the trivial cell: `tools/bench/build_harness_copyloop2.log:31-40` - 6349C03 CREATED a wire
    between two BARE terminals (census 9 -> 10) with the Invoke on the SINK. That is cell A2's configuration,
    and this run measures all four.

NOTHING NEW IS BUILT AND NOTHING IS LANDED. Three SCRATCH op variants are cut from ops already on disk,
used, and DELETED in this same run; they are instruments, not artefacts:
  S-AR    `C83ARCONN_<stamp>.vi`   = `OpConnect_v0.vi`               + an `Auto Route?` control + an Invoke
                                     `error out` indicator                       (STEP 1's four cells)
  S-ARF   `C83ARFSIT_<stamp>.vi`   = the PATCHED `OpFsInnerTunnelConnect_v0.vi` + an `Auto Route?` control
                                                                                 (STEP 2's B cells)
  S-SWAP  `C83SWAPFSIT_<stamp>.vi` = the PATCHED op with the Invoke's `reference` and `Wire Source` feeds
                                     EXCHANGED + an `Auto Route?` control        (STEP 2's A cells)
The ONLY file written on disk is `OpFsInnerTunnelConnect_v0.vi` itself, and only for STEP 0.

STEP 0 (unconditional, an INSTRUMENTATION repair, not a hypothesis): walk the op's Invoke `error out` chain
and make the Invoke's OWN error cluster reach a front-panel indicator, by `create_indicator` on the first
UNWIRED `error out` in that chain. Re-assert ExecState 1, re-save, report the new md5. The roles, the
`Auto Route?` terminal and the address route are NOT touched.

STEP 1 - the 2x2 on a TRIVIAL scratch VI, a FRESH one per cell (a successful connect mutates it):
  two bare `VI Server:GObject` Property nodes; SOURCE = node A's `reference out` (is_source True),
  SINK = node B's `reference` (is_source False).
    A1 Invoke on the SINK, SOURCE as `Wire Source`, Auto Route TRUE
    A2 Invoke on the SINK, SOURCE as `Wire Source`, Auto Route FALSE
    B1 Invoke on the SOURCE, SINK as `Wire Source`, Auto Route TRUE
    B2 Invoke on the SOURCE, SINK as `Wire Source`, Auto Route FALSE   <- what the op does today

STEP 2 - the SAME four cells on the REAL pair, each on its own dated scratch COPY of the bed with wire 7506
deleted: FSIT `#7468` LeftTerm `#7488` and `WhileLoop #23032` `Nodes[21]` `Terminals[1]` (uid `#23906`,
owner `RightShiftRegister #23868`). For any cell that CREATED a wire: the new net's SOURCE TERMINAL OWNER
read by `OpWireSource_v5`, whether `#4334` is off the net, PD85 violations, `Wire.Is Broken?`.

A CELL THAT REFUSES IS A RESULT: its raw error is recorded and the remaining cells still run. No fifth
configuration is improvised, no second op is built, no other method id is tried, and the winning
configuration is NOT applied to the op - that is the judgement session's call.

HYGIENE / CONSTRAINTS
 H1/H2 the bed's md5 `33ef524e...` BEFORE and UNCHANGED AFTER; the bed is NEVER opened for execution.
 H3    the five md5 pins hold.  H4 every scratch deleted.  H5 refs opened == closed.
 H6    THE FILES THIS RUN LEFT ON DISK == [] (the op is EDITED IN PLACE, not added).
 LabVIEW is restarted first; handles before/after; stray `Invoke` nodes counted and purged per cell.
 RIG STATE 조립: no motor, no ASI, no camera. VI Scripting and COM only.

VERIFICATION LEVEL: FUNCTIONAL for every cell (real data through a real op into a real VI), asserted by
terminal wire uids and owner identity - never by a wire count alone.
"""
import glob
import hashlib
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
from build_opconnectnested_v1 import walk, term, src_of, Stop                       # noqa: E402
from build_opconnectnested_v1 import connect as wire_by_name                        # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS              # noqa: E402
import build_opfsinnertunnelconnect_v0 as C82                                       # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
OUT = os.path.join(BENCH, "diag_c83_connect2x2.json")

OP = C82.OP                                     # claudeDev\OpFsInnerTunnelConnect_v0.vi - PATCHED in STEP 0
OP_CONNECT = g.OP_CONNECT                       # claudeDev\OpConnect_v0.vi - the trivial cells' primitive
EMPTY = os.path.join(g.CLAUDEDEV, "EMPTY_v0.vi")
V5 = C82.V5
MAP = C82.MAP_OUT

BED, BED_MD5, BED_BYTES = C82.BED, C82.BED_MD5, C82.BED_BYTES
PINS = C82.PINS
FSIT_UID, LEFT_TERM = C82.FSIT_UID, C82.LEFT_TERM_EXPECT
ROWD_WIRE, D686 = C82.ROWD_WIRE, C82.D686
LOOP_NEW, LOOP_NODES_IDX, LOOP_TERM_IDX = C82.LOOP_NEW, C82.LOOP_NODES_IDX, C82.LOOP_TERM_IDX
RSR_EXPECT, OLD_SOURCE = C82.RSR_EXPECT, C82.OLD_SOURCE

STAMP = time.strftime("%Y%m%d_%H%M%S")
S_AR = os.path.join(g.CLAUDEDEV, "C83ARCONN_%s.vi" % STAMP)
S_ARF = os.path.join(g.CLAUDEDEV, "C83ARFSIT_%s.vi" % STAMP)
S_SWAP = os.path.join(g.CLAUDEDEV, "C83SWAPFSIT_%s.vi" % STAMP)
SCRATCHES = [S_AR, S_ARF, S_SWAP]

# cell -> (which terminal the Invoke sits on, Auto Route?)
CELLS = [("A1", "sink", True), ("A2", "sink", False), ("B1", "source", True), ("B2", "source", False)]

RUN_DEADLINE_S = 62 * 60.0
RESERVE_S = 360.0
T0 = time.time()

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "op": OP, "bed": BED,
     "task": "D-2b of M3a-3b: STEP 0 error-propagation repair + the 2x2 role/Auto-Route separation",
     "verification_level": "FUNCTIONAL - real data through real ops into real VIs; asserted by terminal "
                           "wire uids and owner identity, never by a wire count alone",
     "S0": {}, "S1": {}, "S2": {}, "H": {}}
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
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


def invoke_node(target):
    """(Nodes[] index, uid, terminal rows) of the single `Invoke Node` on diagram 0."""
    w = walk(target, 0)
    for u, (n, lab, rows) in w.items():
        if lab == "Invoke Node":
            return n, u, rows, w
    raise Stop("no Invoke Node on %s" % os.path.basename(target))


def ind_labels(target):
    return [l for _i, l, ind in g.fp_labels(target) if ind]


def ctl_labels(target):
    return [l for _i, l, ind in g.fp_labels(target) if not ind]


def attach_error_indicator(target, tag):
    """STEP 0's repair, and the same repair on the scratch connect op: walk the Invoke's `error out` chain
    and put an indicator on the FIRST UNWIRED `error out` in it, so the Invoke's own error cluster reaches
    the panel. Returns (label or '', a description of what was found)."""
    n_inv, u_inv, rows, w = invoke_node(target)
    r = term(rows, "error out", True)
    if r is None:
        return "", "the Invoke node has no `error out` terminal (names: %r)" % [x["name"] for x in rows]
    chain = [("Invoke", n_inv, u_inv, r["wire"])]
    node_n, node_u, wire = n_inv, u_inv, r["wire"]
    for _hop in range(6):
        if not wire:
            break
        # follow the error wire to the node that SINKS it, then look at that node's own `error out`
        nxt = None
        for u2, (n2, _lab2, rows2) in w.items():
            for rr in rows2:
                if (not rr["is_source"]) and rr["wire"] == wire and u2 != node_u:
                    nxt = (n2, u2, rows2, rr["name"])
                    break
            if nxt:
                break
        if not nxt:
            break
        n2, u2, rows2, sink_name = nxt
        r2 = term(rows2, "error out", True)
        wire = (r2 or {}).get("wire", 0)
        node_n, node_u = n2, u2
        chain.append((w[u2][1], n2, u2, wire, sink_name))
        if not wire:
            break
    fact("%s the Invoke's `error out` CHAIN: %r" % (tag, chain))
    if wire:
        return "", "the chain's last `error out` is STILL WIRED (w%r) - no free terminal to indicate" % wire
    before = ind_labels(target)
    rows_now = g.node_terms_uid(target, 0, node_n)[1]
    rr = term(rows_now, "error out", True)
    if rr is None:
        return "", "the chain's last node #%s has no `error out`" % node_u
    if rr.get("wire"):
        return "", "the chain's last node #%s `error out` is wired w%r" % (node_u, rr["wire"])
    _new, _e = safe("%s create_indicator(#%s `error out`)" % (tag, node_u),
                    lambda: g.create_indicator(target, node_n, rr["i"]))
    after = ind_labels(target)
    fresh = [l for l in after if l not in before]
    if len(fresh) == 1:
        fact("%s NEW error indicator %r on Nodes[%d] #%s `error out` (t%d)"
             % (tag, fresh[0], node_n, node_u, rr["i"]))
        return fresh[0], "created on #%s (%d hop(s) from the Invoke)" % (node_u, len(chain) - 1)
    return "", "create_indicator added %r indicator(s), not exactly one" % (fresh,)


def attach_auto_route(target, tag):
    """A front-panel control on the Invoke's `Auto Route?` terminal. Returns (label or '', note)."""
    n_inv, u_inv, rows, _w = invoke_node(target)
    r = next((x for x in rows if str(x["name"]).startswith("Auto Route")), None)
    if r is None:
        return "", "no terminal whose name starts with 'Auto Route' (names: %r)" % [x["name"] for x in rows]
    if r.get("wire"):
        return "", "`%s` is already wired (w%r)" % (r["name"], r["wire"])
    (new, label), e = safe("%s create_control(%r)" % (tag, r["name"]),
                           lambda: g.create_control(target, n_inv, r["i"]), ([], None))
    if e or not new:
        return "", "create_control refused: %s" % (e or "no new ControlTerminal")
    fact("%s `%s` (t%d on Nodes[%d] #%s) now carries control %r"
         % (tag, r["name"], r["i"], n_inv, u_inv, label))
    return (label or ""), "created"


# ======================================================================= the parameterised caller
def fsit_call(op_path, labels, target, fsit_uid, sink_diag, sink_node, sink_term,
              ar_label="", auto_route=None, inv_err_label="", count_wires=True):
    """`C82.fsit_connect` PARAMETERISED BY OP PATH (that function hard-wires the module global `OP`).
    Every readout is POISONED before the run - a stale value can never be read as an answer."""
    w0 = g.count(target, "Wire") if count_wires else None
    i0 = g.count(target, "Invoke") if count_wires else None
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
    if count_wires:
        out["wire_delta"] = g.count(target, "Wire") - w0
        out["invoke_delta"] = g.count(target, "Invoke") - i0
    return out


def conn_call(op_path, target, inv_node, inv_term, ws_node, ws_term,
              ar_label="", auto_route=None, inv_err_label=""):
    """`gscript.connect_terminals`:2518 driven through an explicit op path - (index, index 2) is the
    terminal the Invoke SITS ON, (index 3, index 4) is the one handed to `Wire Source`."""
    w0 = g.count(target, "Wire")
    i0 = g.count(target, "Invoke")
    vi = g.op(op_path)
    for k in (inv_err_label, "error out"):
        if k:
            try:
                vi.SetControlValue(k, (True, 999999, "POISON - not overwritten by the run"))
            except Exception:                                                      # noqa: BLE001
                pass
    vi.SetControlValue("vi path", target)
    for k, v in (("Names", []), ("Names 2", []), ("Class Name", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:                                                          # noqa: BLE001
            pass
    vi.SetControlValue("index", int(inv_node))
    vi.SetControlValue("index 2", int(inv_term))
    vi.SetControlValue("index 3", int(ws_node))
    vi.SetControlValue("index 4", int(ws_term))
    if ar_label and auto_route is not None:
        vi.SetControlValue(ar_label, bool(auto_route))
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else "EXC %s" % str(e)[:140]
    return {"err": err, "op": os.path.basename(op_path), "auto_route": auto_route,
            "invoke_err": (g._err(vi, inv_err_label) or "") if inv_err_label else "NO INDICATOR",
            "wire_delta": g.count(target, "Wire") - w0,
            "invoke_delta": g.count(target, "Invoke") - i0}


# ======================================================================= [0] files + restart
def phase_files():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the five pins, the claudeDev listing")
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
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    R["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))
    for p, nm in ((OP, "OpFsInnerTunnelConnect_v0.vi (STEP 0's subject)"),
                  (OP_CONNECT, "OpConnect_v0.vi (the trivial cells' primitive)"),
                  (EMPTY, "EMPTY_v0.vi (the trivial scratch's source)"),
                  (V5, "OpWireSource_v5.vi (the identity reader)"),
                  (MAP, "the op's label map")):
        gate("F0 %s on disk" % nm, os.path.isfile(p), p, fatal=True)
    R["op_md5_before"] = md5(OP)
    R["opconnect_md5_before"] = md5(OP_CONNECT)
    R["empty_md5_before"] = md5(EMPTY)
    fact("OpFsInnerTunnelConnect_v0.vi md5 BEFORE the repair: %s (%d bytes)"
         % (R["op_md5_before"], os.path.getsize(OP)))
    gate("F0b the op's md5 is the one STATUS pins (c0d5efe3389b0dea388ee565433fb683)",
         R["op_md5_before"] == "c0d5efe3389b0dea388ee565433fb683", R["op_md5_before"])


def phase_restart():
    head("[1] RESTART LabVIEW (STATUS orders it; the instance was left at ~33,996 handles)")
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


# ======================================================================= [S0] the repair
def step0():
    head("[S0] REPAIR (c): make the Invoke's OWN error cluster reach the op's panel. NOTHING ELSE CHANGES")
    g.ensure_loaded(OP)
    n_inv, u_inv, rows, _w = invoke_node(OP)
    fact("S0 the op's Invoke node: Nodes[%d] #%s ; terminals %r"
         % (n_inv, u_inv, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]))
    R["S0"]["invoke_terminals"] = [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]
    gate("S0a the op's Invoke carries an `Auto Route?` terminal and it is UNWIRED (explanation (b)'s "
         "premise, measured not assumed)",
         any(str(x["name"]).startswith("Auto Route") and not x["wire"] for x in rows),
         "%r" % [(x["name"], x["wire"]) for x in rows if str(x["name"]).startswith("Auto")])
    label, note = attach_error_indicator(OP, "S0")
    R["S0"]["invoke_error_indicator"] = label
    R["S0"]["invoke_error_note"] = note
    gate("S0b the Invoke's own error cluster now reaches a front-panel indicator", bool(label),
         "indicator %r ; %s" % (label, note))
    es = g.exec_state(OP)
    R["S0"]["exec_state"] = es
    gate("S0c ExecState 1 after the edit (on this COM path ExecState 0 IS LabVIEW's 'broken' verdict)",
         es == 1, "ExecState %r" % es)
    if es != 1:
        fact("S0 NOT SAVED - the op is left exactly as it was on disk")
        return ""
    size = g.save(OP)
    g.reset()
    time.sleep(1.5)
    es2 = g.exec_state(OP)
    R["S0"]["exec_state_after_save"] = es2
    R["S0"]["op_md5_after"] = md5(OP)
    R["S0"]["op_bytes_after"] = size
    fact("S0 SAVED %s (%s bytes) md5 %s -> %s"
         % (os.path.basename(OP), size, R["op_md5_before"], R["S0"]["op_md5_after"]))
    gate("S0d ExecState 1 re-read AFTER the save", es2 == 1, "ExecState %r" % es2)
    lab = json.load(open(MAP, encoding="utf-8"))
    lab["err_invoke"] = label
    with open(MAP, "w", encoding="utf-8") as f:
        json.dump(lab, f, indent=1)
    fact("S0 label map updated with err_invoke=%r -> %s" % (label, MAP))
    return label


# ======================================================================= [S-op] the scratch op variants
def make_ar_connect():
    head("[S-AR] a SCRATCH copy of OpConnect_v0.vi with an `Auto Route?` control + an Invoke error "
         "indicator - the ONLY way to set `Auto Route?` (no op on disk exposes it)")
    shutil.copyfile(OP_CONNECT, S_AR)
    time.sleep(0.3)
    g.ensure_loaded(S_AR)
    n_inv, u_inv, rows, _w = invoke_node(S_AR)
    fact("S-AR OpConnect_v0's Invoke: Nodes[%d] #%s ; terminals %r"
         % (n_inv, u_inv, [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]))
    R["S1"]["opconnect_invoke_terminals"] = [(x["i"], x["name"], x["is_source"], x["wire"]) for x in rows]
    gate("S1c NO op on disk exposes `Auto Route?`: on OpConnect_v0 it is present and UNWIRED",
         any(str(x["name"]).startswith("Auto Route") and not x["wire"] for x in rows),
         "%r" % [(x["name"], x["wire"]) for x in rows if str(x["name"]).startswith("Auto")])
    ar, note = attach_auto_route(S_AR, "S-AR")
    ei, enote = attach_error_indicator(S_AR, "S-AR")
    es = g.exec_state(S_AR)
    R["S1"]["ar_op"] = {"path": S_AR, "auto_route_label": ar, "auto_route_note": note,
                        "err_label": ei, "err_note": enote, "exec_state": es}
    gate("S1d the scratch connect op is legal after the two additions (ExecState 1)", es == 1,
         "ExecState %r ; AR control %r ; error indicator %r" % (es, ar, ei))
    if es == 1:
        g.save(S_AR)
        g.reset()
        time.sleep(1.0)
    return ar, ei, es == 1 and bool(ar)


def make_ar_fsit():
    head("[S-ARF] a SCRATCH copy of the PATCHED op with an `Auto Route?` control (STEP 2's B cells)")
    shutil.copyfile(OP, S_ARF)
    time.sleep(0.3)
    g.ensure_loaded(S_ARF)
    ar, note = attach_auto_route(S_ARF, "S-ARF")
    es = g.exec_state(S_ARF)
    R["S2"]["arf_op"] = {"path": S_ARF, "auto_route_label": ar, "note": note, "exec_state": es}
    gate("S2a the AR copy of the op is legal (ExecState 1)", es == 1, "ExecState %r ; AR %r" % (es, ar))
    if es == 1 and ar:
        g.save(S_ARF)
        g.reset()
        time.sleep(1.0)
        return ar, True
    return ar, False


def make_swapped():
    head("[S-SWAP] a SCRATCH copy of the PATCHED op with the Invoke's `reference` and `Wire Source` feeds "
         "EXCHANGED - explanation (a)'s configuration on the REAL pair. NOT applied to the op on disk.")
    shutil.copyfile(OP, S_SWAP)
    time.sleep(0.3)
    g.ensure_loaded(S_SWAP)
    n_inv, u_inv, rows, w = invoke_node(S_SWAP)
    r_ref = term(rows, "reference", False)
    r_ws = term(rows, "Wire Source", False)
    if not (r_ref and r_ws and r_ref.get("wire") and r_ws.get("wire")):
        R["S2"]["swap_op"] = {"built": False,
                              "why": "reference/Wire Source rows %r / %r" % (r_ref, r_ws)}
        gate("S2b the swapped copy could be built", False, "reference %r Wire Source %r" % (r_ref, r_ws))
        return "", False
    w_ref, w_ws = r_ref["wire"], r_ws["wire"]
    u_src_ref, u_src_ws = src_of(w, w_ref), src_of(w, w_ws)

    def srcname(u, wire):
        return next((x["name"] for x in w[u][2] if x["is_source"] and x["wire"] == wire), None)

    n_ref, n_ws = srcname(u_src_ref, w_ref), srcname(u_src_ws, w_ws)
    fact("S-SWAP BEFORE: `reference` <- #%s.%r (w%s) ; `Wire Source` <- #%s.%r (w%s)"
         % (u_src_ref, n_ref, w_ref, u_src_ws, n_ws, w_ws))
    R["S2"]["swap_before"] = {"reference_from": (u_src_ref, n_ref, w_ref),
                              "wire_source_from": (u_src_ws, n_ws, w_ws)}
    ok = True
    for wu, tag in ((w_ref, "S-SWAP reference net"), (w_ws, "S-SWAP Wire Source net")):
        _r, e = safe(tag, lambda q=wu: C82.del_wire(S_SWAP, q, "S-SWAP "))
        ok = ok and not e
    g.remove_bad_wires_scripted(S_SWAP)
    for (u_src, nm, dst) in ((u_src_ref, n_ref, "Wire Source"), (u_src_ws, n_ws, "reference")):
        _r, e = safe("S-SWAP connect #%s.%r -> Invoke.%r" % (u_src, nm, dst),
                     lambda a=u_src, b=nm, c=dst: wire_by_name(S_SWAP, a, b, u_inv, c, tag="S-SWAP "))
        ok = ok and not e
    ar, note = attach_auto_route(S_SWAP, "S-SWAP")
    es = g.exec_state(S_SWAP)
    R["S2"]["swap_op"] = {"built": ok, "path": S_SWAP, "auto_route_label": ar, "note": note,
                          "exec_state": es}
    if es != 1:
        w2 = walk(S_SWAP, 0)
        orphans = [(u, r["name"]) for u in w2 for r in w2[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        fact("S-SWAP DIAGNOSTIC unwired non-error SINK terminals: %r" % orphans)
    gate("S2b the SWAPPED copy is legal (ExecState 1) - i.e. LabVIEW accepts the exchanged roles at "
         "EDIT time", es == 1, "ExecState %r ; rewire ok %r ; AR %r" % (es, ok, ar))
    if es == 1 and ok:
        g.save(S_SWAP)
        g.reset()
        time.sleep(1.0)
        return ar, True
    return ar, False


# ======================================================================= [S1] the trivial 2x2
def make_trivial(cell):
    """A FRESH trivial VI: two bare `VI Server:GObject` Property nodes. SOURCE = A.`reference out`,
    SINK = B.`reference`. Returns (path, A index, A term, B index, B term, description)."""
    p = os.path.join(g.CLAUDEDEV, "C83TRIV_%s_%s.vi" % (STAMP, cell))
    shutil.copyfile(EMPTY, p)
    time.sleep(0.3)
    g.ensure_loaded(p)
    for loc in ((100, 100), (500, 100)):
        g.build_property(p, "VI Server:GObject", [("632A813", False)], loc, 0)
    w = walk(p, 0)
    nodes = sorted((n, u, rows) for u, (n, _lab, rows) in w.items())
    if len(nodes) != 2:
        raise Stop("%s: expected 2 nodes on the trivial VI, got %d" % (cell, len(nodes)))
    (na, ua, ra), (nb, ub, rb) = nodes[0], nodes[1]
    ta = term(ra, "reference out", True)
    tb = term(rb, "reference", False)
    if not (ta and tb):
        raise Stop("%s: `reference out` %r / `reference` %r not both found" % (cell, ta, tb))
    desc = ("SOURCE = Nodes[%d] #%s `reference out` t%d is_source=%r wire=%r ; "
            "SINK = Nodes[%d] #%s `reference` t%d is_source=%r wire=%r"
            % (na, ua, ta["i"], ta["is_source"], ta["wire"],
               nb, ub, tb["i"], tb["is_source"], tb["wire"]))
    fact("%s trivial VI %s : %s" % (cell, os.path.basename(p), desc))
    if ta["wire"] or tb["wire"]:
        raise Stop("%s: the two terminals are NOT both bare (%r / %r)" % (cell, ta["wire"], tb["wire"]))
    return p, (na, ta["i"], ua), (nb, tb["i"], ub), desc


def read_pair(target, a, b):
    """The two terminals' own wire uids, re-read off the machine."""
    out = {}
    for tag, (n, ti, u) in (("source", a), ("sink", b)):
        _uu, rows = g.node_terms_uid(target, 0, n)
        row = next((x for x in rows if x["i"] == ti), None)
        out[tag] = {"node": n, "uid": u, "t": ti, "name": (row or {}).get("name"),
                    "is_source": (row or {}).get("is_source"), "wire": (row or {}).get("wire")}
    return out


def step1(ar_label, err_label, ar_ok):
    head("[S1] THE 2x2 ON A TRIVIAL SCRATCH VI - a FRESH VI per cell")
    R["S1"]["cells"] = {}
    for cell, where, auto in CELLS:
        if left_s() < 120:
            gate("S1 cell %s had time to run" % cell, False, "%.0f s left" % left_s())
            continue
        head("[S1 %s] Invoke on the %s terminal, Auto Route %s" % (cell, where.upper(), auto))
        rec = {"cell": cell, "invoke_on": where, "auto_route": auto}
        if auto and not ar_ok:
            rec["refused"] = "REFUSED BY CONSTRUCTION: no `Auto Route?` control could be created"
            fact("S1 %s %s" % (cell, rec["refused"]))
            R["S1"]["cells"][cell] = rec
            gate("S1 %s ran" % cell, False, rec["refused"])
            continue
        triv, a, b, desc = (None, None, None, "")
        try:
            triv, a, b, desc = make_trivial(cell)
            rec["terminals"] = desc
            rec["before"] = read_pair(triv, a, b)
            inv = b if where == "sink" else a
            ws = a if where == "sink" else b
            r = conn_call(S_AR, triv, inv[0], inv[1], ws[0], ws[1],
                          ar_label=ar_label, auto_route=auto, inv_err_label=err_label)
            rec.update(r)
            rec["after"] = read_pair(triv, a, b)
            src_w = rec["after"]["source"]["wire"]
            snk_w = rec["after"]["sink"]["wire"]
            rec["wire_created"] = bool(src_w) and src_w == snk_w
            rec["exec_state"] = g.exec_state(triv)
            fact("S1 %s RESULT: op_err=%r invoke_err=%r wire_delta=%r junk_Invoke=%r source_wire=%r "
                 "sink_wire=%r created=%r ExecState=%r"
                 % (cell, r.get("err"), r.get("invoke_err"), r.get("wire_delta"), r.get("invoke_delta"),
                    src_w, snk_w, rec["wire_created"], rec["exec_state"]))
            gate("S1 %s: a wire now joins the two terminals (SAME wire uid on both ends)" % cell,
                 rec["wire_created"], "source w%r / sink w%r ; wire_delta %r"
                 % (src_w, snk_w, r.get("wire_delta")))
        except Stop as e:
            rec["refused"] = "STOP %s" % e
            gate("S1 %s ran" % cell, False, str(e)[:160])
        except Exception as e:                                                     # noqa: BLE001
            rec["refused"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            gate("S1 %s ran" % cell, False, rec["refused"])
        finally:
            R["S1"]["cells"][cell] = rec
            if triv:
                safe("close_panel(%s)" % os.path.basename(triv), lambda q=triv: g.close_panel(q))
                for _att in range(5):
                    try:
                        if os.path.exists(triv):
                            os.remove(triv)
                        break
                    except Exception:                                              # noqa: BLE001
                        time.sleep(2.0)
                gate("S1 %s trivial scratch deleted" % cell, not os.path.exists(triv),
                     os.path.basename(triv))
            dump()


# ======================================================================= [S2] the real pair
def step2(labels, err_label, arf_label, arf_ok, swap_label, swap_ok):
    head("[S2] THE SAME FOUR CELLS ON THE REAL PAIR - a dated scratch COPY of the bed per cell")
    R["S2"]["cells"] = {}
    for cell, where, auto in CELLS:
        if left_s() < 240:
            gate("S2 cell %s had time to run" % cell, False, "%.0f s left" % left_s())
            continue
        head("[S2 %s] Invoke on the %s terminal, Auto Route %s" % (cell, where.upper(), auto))
        rec = {"cell": cell, "invoke_on": where, "auto_route": auto}
        # which op variant realises this cell
        if where == "sink":                       # Invoke on the FSIT terminal = the SWAPPED op
            op_path, ar_lab, ready = S_SWAP, swap_label, swap_ok
            rec["op_variant"] = "C83SWAPFSIT (roles EXCHANGED)"
        elif auto:                                # Invoke on the loop terminal, Auto Route settable
            op_path, ar_lab, ready = S_ARF, arf_label, arf_ok
            rec["op_variant"] = "C83ARFSIT (today's roles + an Auto Route control)"
        else:                                     # exactly what the op does today
            op_path, ar_lab, ready = OP, "", True
            rec["op_variant"] = "OpFsInnerTunnelConnect_v0 (today, Auto Route at its default FALSE)"
        if not ready:
            rec["refused"] = "REFUSED BY CONSTRUCTION: %s could not be built" % rec["op_variant"]
            fact("S2 %s %s" % (cell, rec["refused"]))
            R["S2"]["cells"][cell] = rec
            gate("S2 %s ran" % cell, False, rec["refused"])
            continue
        scratch = os.path.join(g.CLAUDEDEV, "C83BED_%s_%s.vi" % (STAMP, cell))
        try:
            shutil.copyfile(BED, scratch)
            time.sleep(0.4)
            gate("S2 %s the scratch is a byte-identical copy of the bed" % cell,
                 md5(scratch) == R["bed_md5_before"], os.path.basename(scratch), fatal=True)
            t = time.time()
            safe("ensure_loaded(%s)" % cell, lambda q=scratch: g.ensure_loaded(q))
            fact("S2 %s ensure_loaded took %.1f s" % (cell, time.time() - t))
            d_idx, trip = C82.resolve_triple(scratch, "S2 %s" % cell)
            rec["triple"] = trip
            C82.del_wire(scratch, ROWD_WIRE, "S2 %s " % cell)
            g.remove_bad_wires_scripted(scratch)
            _u, trows = g.node_terms_uid(scratch, d_idx, LOOP_NODES_IDX)
            bare = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
            rec["border_before"] = bare
            gate("S2 %s the border terminal is BARE before the connect" % cell,
                 (bare or {}).get("wire") == 0, "wire %r" % (bare or {}).get("wire"), fatal=True)
            r = fsit_call(op_path, labels, scratch, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX,
                          ar_label=ar_lab, auto_route=(auto if ar_lab else None),
                          inv_err_label=err_label)
            rec.update(r)
            _u, trows = g.node_terms_uid(scratch, d_idx, LOOP_NODES_IDX)
            after = next((x for x in (trows or []) if x["i"] == LOOP_TERM_IDX), None)
            neww = (after or {}).get("wire")
            rec["border_after"] = after
            rec["wire_created"] = bool(neww)
            fact("S2 %s RESULT: op_err=%r invoke_err=%r `UID 2`=%r border_wire=%r wire_delta=%r "
                 "junk_Invoke=%r term_uid=%r uid_back=%r is_broken=%r"
                 % (cell, r.get("err"), r.get("invoke_err"), r.get("sink_wire_uid"), neww,
                    r.get("wire_delta"), r.get("invoke_delta"), r.get("term_uid"), r.get("uid_back"),
                    r.get("is_broken")))
            gate("S2 %s: the border terminal went BARE -> NON-ZERO" % cell, bool(neww), "wire %r" % neww)
            if neww:
                walkr, werr = safe("S2 %s OpWireSource_v5(w%r)" % (cell, neww),
                                   lambda q=neww: WIRE_TERMS(scratch, int(q), n=8), [])
                M.print_walk("S2 %s" % cell, neww, walkr, werr)
                bad = M.pd85_violations(neww, walkr)
                owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid")))
                                 for t in (walkr or []) if t.get("owner_uid")})
                src_owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid")))
                                     for t in (walkr or []) if t.get("is_source") and t.get("owner_uid")})
                rec["source_owners"] = src_owners
                rec["all_owners"] = owners
                rec["pd85_violations"] = len(bad)
                rec["old_source_off_net"] = all(u != OLD_SOURCE for _c, u in owners)
                fact("S2 %s NEW NET w%r: source-terminal owners %r ; every owner %r ; PD85 %d ; "
                     "#%d off the net %r ; op `Is Broken?` %r"
                     % (cell, neww, src_owners, owners, len(bad), OLD_SOURCE,
                        rec["old_source_off_net"], r.get("is_broken")))
                gate("S2 %s the net's SOURCE TERMINAL OWNER is RightShiftRegister #%d and nothing else "
                     "is a source" % (cell, RSR_EXPECT),
                     src_owners == [("RightShiftRegister", RSR_EXPECT)], "%r" % (src_owners,))
        except Stop as e:
            rec["refused"] = "STOP %s" % e
            gate("S2 %s ran" % cell, False, str(e)[:160])
        except Exception as e:                                                     # noqa: BLE001
            rec["refused"] = "%s: %s" % (type(e).__name__, str(e)[:200])
            gate("S2 %s ran" % cell, False, rec["refused"])
        finally:
            R["S2"]["cells"][cell] = rec
            safe("close_panel(%s)" % os.path.basename(scratch), lambda q=scratch: g.close_panel(q))
            for _att in range(6):
                try:
                    if os.path.exists(scratch):
                        os.remove(scratch)
                    break
                except Exception:                                                  # noqa: BLE001
                    time.sleep(3.0)
            gate("S2 %s bed scratch deleted" % cell, not os.path.exists(scratch),
                 os.path.basename(scratch))
            dump()


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close panels, delete every scratch, re-read every pin, handles at both ends")
    for p in SCRATCHES + [OP, OP_CONNECT, EMPTY]:
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
    for p in SCRATCHES + sorted(glob.glob(os.path.join(g.CLAUDEDEV, "C83*_%s*.vi" % STAMP))):
        if not os.path.exists(p):
            continue
        for _att in range(6):
            try:
                os.remove(p)
                break
            except Exception as e:                                                 # noqa: BLE001
                fact("delete %s failed: %s" % (os.path.basename(p), str(e)[:110]))
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
        fact("PIN AFTER  %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    gate("H3 the five md5 pins all hold", allpins)
    for p, key in ((OP_CONNECT, "opconnect_md5_before"), (EMPTY, "empty_md5_before")):
        gate("H3b %s md5 unchanged (it was only COPIED)" % os.path.basename(p),
             md5(p) == R.get(key), "%s -> %s" % (R.get(key), md5(p)))
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6 THE FILES THIS RUN LEFT ON DISK == [] and nothing was removed (the op is EDITED IN PLACE)",
         not added and not gone, "added %r removed %r" % (added, gone))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    if os.path.isfile(OP):
        R["H"]["op_md5_final"] = md5(OP)
        fact("THE OP AFTER STEP 0: %s md5 %s (%d bytes) - was %s"
             % (os.path.basename(OP), R["H"]["op_md5_final"], os.path.getsize(OP),
                R.get("op_md5_before")))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def summary():
    head("THE 8-CELL TABLE")
    print("  %-4s %-8s %-6s %-46s %-9s %-9s %-9s %-6s" %
          ("cell", "where", "AR", "invoke error (raw)", "created?", "UID 2", "sink wire", "junk"), flush=True)
    for step, key in (("S1 trivial", "S1"), ("S2 real pair", "S2")):
        print("  -- %s" % step, flush=True)
        for cell, _w, _a in CELLS:
            c = (R.get(key, {}).get("cells") or {}).get(cell) or {}
            if c.get("refused"):
                print("  %-4s %-8s %-6s REFUSED: %s" % (cell, c.get("invoke_on"), c.get("auto_route"),
                                                        str(c["refused"])[:90]), flush=True)
                continue
            sink_w = (c.get("after", {}).get("sink", {}) or {}).get("wire") if key == "S1" \
                else (c.get("border_after") or {}).get("wire")
            print("  %-4s %-8s %-6s %-46s %-9s %-9s %-9s %-6s"
                  % (cell, c.get("invoke_on"), c.get("auto_route"),
                     str(c.get("invoke_err") or c.get("err") or "(none)")[:46],
                     c.get("wire_created"), c.get("sink_wire_uid", "-"), sink_w,
                     c.get("invoke_delta")), flush=True)
            if c.get("source_owners") is not None:
                print("        owners: source %r ; all %r ; PD85 %r ; #%d off net %r ; Is Broken? %r"
                      % (c.get("source_owners"), c.get("all_owners"), c.get("pd85_violations"),
                         OLD_SOURCE, c.get("old_source_off_net"), c.get("is_broken")), flush=True)


def main():
    print("=" * 100, flush=True)
    print("diag_c83_connect2x2 - D-2b of M3a-3b: STEP 0 error propagation + the 2x2 role/Auto-Route "
          "separation", flush=True)
    print("=" * 100, flush=True)
    try:
        g._lv = None
        phase_files()
        phase_restart()
        err_label = step0()
        dump()
        ar_label, ar_err_label, ar_ok = make_ar_connect()
        dump()
        step1(ar_label, ar_err_label, ar_ok)
        dump()
        labels = json.load(open(MAP, encoding="utf-8"))
        arf_label, arf_ok = make_ar_fsit()
        swap_label, swap_ok = make_swapped()
        dump()
        step2(labels, err_label, arf_label, arf_ok, swap_label, swap_ok)
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
