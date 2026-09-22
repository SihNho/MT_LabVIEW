r"""build_opfsinnertunnelconnect_v0.py - D-2 of M3a-3b (`docs/cycle27-plan.md` Pre-decided 127).

BUILD, SAVE AND EXERCISE ONE NEW OP: `OpFsInnerTunnelConnect_v0.vi`, the SMALLEST possible edit of
`OpConnectFromWire_v0.vi` in which ONLY THE SOURCE-HALF ACQUISITION CHANGES.

    MATERIAL=1 py tools/bgrun.py --max-min 55 --log tools/bench/build_opfsinnertunnelconnect_v0.log \
        -- py -u tools/recipes/build_opfsinnertunnelconnect_v0.py

WHAT ALREADY EXISTS - checked before a line was written (CLAUDE.md "before creating any new op, tool or
recipe"), by reading the files, not by remembering them:
  * `tools/recipes/build_opconnectfromwire_v0.py` - the DONOR's builder. Its source half is
    `UID to GObject Reference.vi` -> TMSC(Wire seed) -> `Wire.Terms[]` 6371003 -> Index Array -> the
    Invoke's `Wire Source`. Its sink half is the (diagram, Nodes[], Terminals[]) INDEX TRIPLE on which the
    `Terminal.Connect Wire` 6349C03 Invoke sits, plus the W7b ordering branch that forces the built-in
    `UID 2` / `Is Broken?` readback to run AFTER the write. IT SUPPLIES `wire_source_owner` (the REPAIRED,
    uid-echo-checked `OpWireSource_v5` driver) and is imported, not re-implemented.
  * `tools/recipes/build_opconnectnested_v1.py` - `walk` / `term` / `src_of` / `idx` / `del_net` / `Stop`,
    imported unchanged. Its `connect()` resolves the object class from the node LABEL, which is wrong for
    a freshly built Property node, so this file wires through its own `wire_named()` with EXPLICIT classes
    (the shape `build_opfstunnelterm_v2.wire_checked` uses).
  * `tools/recipes/build_opfstunnelterm_v2.py` - the builder of `OpFsInnerTunnelTerm_v0.vi`, i.e. THE
    READING HALF THIS OP REUSES: `VI Server:FlatSequenceInnerTunnel` + `1C3A9000` = `LeftTerm`, the typed
    SEED made by `create_control` on the property node's own `reference` terminal, and `VI Server:GObject`
    + `632A813` = `GObject.UID` for the uid echo. Constants are taken from that file (:202-212), measured.
  * `tools/recipes/build_d1_m3a1.py` - `print_walk` / `pd85_violations`, imported for gate 4.
  * `tools/bench/diag_c81_uidref.py` - the read-only hygiene skeleton (pins, restart, scratch, phase_hygiene)
    this file is cut from.
  * `tools/gscript.py` - `build_property`:2267, `create_control`:2468, `create_indicator`:2496,
    `delete_object`:2348, `wire`:1370, `wire_control`:1958, `remove_bad_wires_scripted`:2594,
    `set_auto_error_handling`:2728, `save`:2135, `exec_state`:2007, `ref_counts`:233, `node_terms_uid`:955.
  NOTHING HERE IS HAND-ROLLED and no second design is built.

THE EDIT, in one sentence: delete the `Wire.Terms[]` property node and its Index Array, put
`FlatSequenceInnerTunnel.LeftTerm` in their place behind the SAME `UID to GObject Reference.vi` and the SAME
To More Specific Class (re-seeded FlatSequenceInnerTunnel), and feed the SAME Invoke's `Wire Source` from it.
The Invoke still sits on the terminal named by the INDEX TRIPLE and still receives the other terminal as
`Wire Source` - the binding the machine already accepted (`tools/bench/c80_rowd_routeA_r2.log:244`,
Pre-decided 119). LEFT terminal only; no side selector; no second property.

TWO ADDITIONS BEYOND THE SWAP, BOTH MANDATED, NEITHER SPECULATIVE - `GObject.UID` (632A813) read TWICE:
  * **INPUT SIDE** - branched off the `UID to GObject Reference.vi`'s own `GObject` output, indicator
    `uid_back`. This is Pre-decided 125's rule LITERALLY: *"re-read the returned reference's own UID and
    assert it equals the uid passed in"* (`docs/cycle27-plan.md:3543-3545`), the negative control being
    `diag_c81_uidref.log:85`, where a never-allocated uid returned a DIFFERENT previously-resolved object
    with every error column empty. ADDED after the prior-art review's A3 (`contradicted`): the first cut
    echoed only the OUTPUT side against the literal 7488, which masks the hazard for `fsit_uid` 7468 and
    leaves it ungated for every other FSIT - and a stale echo of another `FlatSequenceInnerTunnel` (there
    are 518 in this VI) casts cleanly and yields a valid-looking `LeftTerm`. The shape copied is the one
    already on disk in `tools/bench/opfsinnertunnelterm_labels.json:7-9` (`uid_in` / `uid_back`).
  * **OUTPUT SIDE** - branched off `LeftTerm`, indicator `term_uid`. This is Pre-decided 127's acceptance
    gate (3), which asks for the LeftTerm's own uid (#7488).

INDEPENDENT CONFIRMATION OF THE BINDING, five days older than the run this plan first cited and added on
the review's A4: `docs/toolkit-capabilities.md:70` - the donor `OpConnectFromWire_v0` ACCEPTED a source
terminal owned by `FlatSequenceInnerTunnel` **#5818** (wire w5812) and created a wire, op error `''`,
sink 0 -> 1231, on a copy of the real VI. So `c80_rowd_routeA_r2.log:244` is the second measurement of
this capability, not the only one.

BUILD GATES (fatal unless said otherwise; nothing is saved on a miss; the donor is never written)
 B0  donor `OpConnectFromWire_v0.vi` on disk at ExecState 1; md5 recorded; every other op used on disk.
 B1  copy -> `OpFsInnerTunnelConnect_v0.vi`; the source ladder found BY WIRE TOPOLOGY from the Invoke's
     `Wire Source` (Invoke <- IA <- Wire PN <- TMSC <- UID-to-GObject subVI), never by uid; the copy is a
     CLEAN donor (no `LeftTerm` output anywhere = this build's own addition is absent).
 B2  the Invoke's `Wire Source` net deleted; that terminal reads 0.
 B3  the Index Array and the `Wire.Terms[]` property node deleted; the TMSC's `target class` AND
     `specific class reference` both read 0.
 B4  `build_property("VI Server:FlatSequenceInnerTunnel", 1C3A9000)` -> ONE new Property node whose single
     data output is `LeftTerm` (the name is READ BACK, not assumed).
 B5  `create_control` on its `reference` -> exactly ONE new control = the FSIT-TYPED SEED; its own wire
     deleted and the seed re-wired to the TMSC's `target class`.
 B6  TMSC `specific class reference` -> the FSIT node's `reference`.
 B7  the FSIT node's `LeftTerm` -> the Invoke's `Wire Source`.
 B8  TWO `build_property("VI Server:GObject", 632A813)` nodes: one branched off the subVI's `GObject`
     (the INPUT-side echo `uid_back`), one branched off `LeftTerm` (the OUTPUT-side echo `term_uid`);
     an indicator on each `UID` output and one on each new `error out`.
 B9  auto error handling OFF; ExecState 1; SAVE; labels JSON; donor md5 unchanged.

ACCEPTANCE (Pre-decided 127, all four, each printing the value it compared)
 G1  `ExecState` 1 on the SAVED op, re-read after the save. (On this COM path `ExecState` 0 IS LabVIEW's
     "this VI is broken" verdict; `Wire.Is Broken?` 6371004 is a WIRE property and is gate 4's.)
 G2  20 CONSECUTIVE CALLS leave LabVIEW's handle count flat +-100 (CLAUDE.md reference hygiene).
     SCOPE, set by the prior-art review's B4 (`already-measured`): this is a REGRESSION CHECK against the
     S0 baseline `docs/toolkit-capabilities.md:460-478` (traverse ops ACCEPTED without a `Close Reference`
     on measurement: +9 / -19 / -12 handles over 20 calls), NOT a hygiene proof - `:484-485` records that
     the kernel handle count is BLIND to VI Server refnums (`tools/gscript.py:227-228`), which is why the
     S0 criterion is a PAIR. The companion measurement, PRIVATE-BYTES DRIFT, is therefore REPORTED beside
     the handle delta (S0's own G-C was <= 5 MB against +34.6 MB of VI growth from 20 created Property
     nodes; this op creates none in the target). A failure is this dispatch's result - no improvised
     repair, per the recipe's own contract.
 G2b THE JUNK-NODE CHARACTERISATION, added on the review's B3 (`helper-exists`): every member of this
     writer family mints a stray `Invoke` in the TARGET (`c80_rowd_routeA_r2.log:275-276`; the delivered
     Row C purged one). The `Node` census is taken BEFORE the loop, AFTER call 1 and AFTER call 20, so the
     PER-CALL rate is measured, and the junk is purged with the imported `build_d1_m3a1.node_census` /
     `new_nodes` / `node_view` / `delete_by_uid` primitives - the shape `build_d1_m3a3.purge_junk` uses.
     (`M.census_and_purge` itself is NOT called: it writes M's own JSON sidecar and appends to M's `R`.)
     The same census brackets the G4 call, because D-3 writes to the BED, where an unpurged junk node
     would be saved into the artefact.
 G3  a call with `fsit_uid` = 7468 returns the LeftTerm reference whose OWN uid echoes #7488, AND the
     resolver's own `uid_back` echoes the uid passed IN (7468) - Pre-decided 125's rule, at BOTH ends.
 G4  ONE end-to-end exercise on a DATED SCRATCH COPY of the bed: delete wire 7506, call the op with
     `fsit_uid` 7468 and the index triple of the NEW loop's shift-register OUTER terminal
     (`WhileLoop #23032`, `Nodes[21]`, `Terminals[1]`), then assert with `OpWireSource_v5` that the net's
     SOURCE TERMINAL OWNER is `RightShiftRegister #23868` and that `#4334` is OFF the net, PD85 violations
     0, `Wire.Is Broken?` False. OWNER IDENTITY DECIDES - never a wire count, never a wire delta
     (Pre-decided 117 as corrected by 120). The scratch is deleted; nothing is saved from it.

HYGIENE (the only other things that can FAIL)
 H1/H2  the bed's md5 is `33ef524e...` BEFORE and UNCHANGED AFTER. The bed is NEVER opened for execution.
 H3     the five md5 pins hold.
 H4     both scratch copies deleted.
 H5     gscript's reference counter level (opened == closed) at exit.
 H6     THE FILES THIS RUN LEFT ON DISK == exactly [`OpFsInnerTunnelConnect_v0.vi`] - the op is the artefact.

RIG STATE 조립: no motor, no ASI, no camera. VI Scripting and COM only.
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
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"), HERE):
    if _p not in sys.path:
        sys.path.insert(0, _p)

import gscript as g                                                                # noqa: E402
import diag_s2_scaffold as D                                                       # noqa: E402
import build_d1_m3a1 as M                                                          # noqa: E402
from bench_prep import labview_handles, restart_labview                            # noqa: E402
from build_opconnectnested_v1 import walk, term, src_of, idx, Stop                  # noqa: E402
from build_opconnectfromwire_v0 import wire_source_owner as WIRE_TERMS              # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")

# ---------------------------------------------------------------- the op, the donor, the constants
DONOR = os.path.join(g.CLAUDEDEV, "OpConnectFromWire_v0.vi")
OP = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelConnect_v0.vi")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
MAP_OUT = os.path.join(BENCH, "opfsinnertunnelconnect_v0_labels.json")
OUT = os.path.join(BENCH, "build_opfsinnertunnelconnect_v0.json")

FSIT_CLASS = "VI Server:FlatSequenceInnerTunnel"   # build_opfstunnelterm_v2.py:203
P_LEFT = "1C3A9000"                                # FlatSequenceInnerTunnel.LeftTerm  (:207)
P_UID = "632A813"                                  # GObject.UID  (:210, docs/vi-server-ids.json:61)
METHOD = "6349C03"                                 # Terminal.Connect Wire (unchanged from the donor)

# ---------------------------------------------------------------- the bed and the md5 pins
BED = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a3_20260922_081056.vi")
BED_MD5 = "33ef524e0b6b193a158c9221474c68e3"
BED_BYTES = 306951
M3A2 = os.path.join(g.CLAUDEDEV, "D1_s3b_m3a2_20260922_023029.vi")
M3A2_MD5 = "3842f5e6f128226235dc78353f26ef44"
ROW2 = os.path.join(g.CLAUDEDEV, "D1_s3b_row2_20260921_160311.vi")
ROW2_MD5 = "26c54ff784cb5cea21edbd214d2cc3a0"
S2 = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
PINS = (("ORIGINAL", D.ORIGINAL, D.ORIG_MD5), ("S1 D1_s1_copy", D.S1_ARTEFACT, D.S1_MD5),
        ("S2 D1_s2_loops", S2, S2_MD5), ("ROW2 bed", ROW2, ROW2_MD5), ("M3a-2", M3A2, M3A2_MD5))

# ---------------------------------------------------------------- gate 4's topology (all re-measured live)
FSIT_UID = 7468          # Row D's sink OBJECT, a FlatSequenceInnerTunnel
LEFT_TERM_EXPECT = 7488  # its LeftTerm - the uid echo gate 3 asserts
ROWD_WIRE = 7506         # the wire deleted first
D686 = 686               # the diagram carrying the loop borders
LOOP_NEW = 23032         # the NEW WhileLoop
LOOP_NODES_IDX = 21      # its Nodes[] index on Diagram #686
LOOP_TERM_IDX = 1        # 'Outgoing Handle' - the register's OUTER terminal, BARE on the bed
RSR_EXPECT = 23868       # Pre-decided 120: the OWNER of that terminal is the REGISTER
OLD_SOURCE = 4334        # the OLD source register - must be OFF the net

HANDLE_CALLS = 20
HANDLE_TOL = 100

STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH_H = os.path.join(g.CLAUDEDEV, "C82SCRATCH_H_%s.vi" % STAMP)   # gates 2 + 3
SCRATCH_E = os.path.join(g.CLAUDEDEV, "C82SCRATCH_E_%s.vi" % STAMP)   # gate 4

RUN_DEADLINE_S = 50 * 60.0        # the bgrun --max-min is 58; this leaves the hygiene tail inside it
RESERVE_S = 420.0
T0 = time.time()

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "op": OP, "donor": DONOR, "bed": BED,
     "task": "D-2 of M3a-3b (Pre-decided 127): build, SAVE and EXERCISE OpFsInnerTunnelConnect_v0.vi",
     "verification_level": "STRUCTURAL for the op's legality; FUNCTIONAL for gate 4 (real data through "
                           "the op on a scratch copy of the bed, asserted by owner identity)",
     "B": {}, "G": {}, "H": {}}


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


def md5(p):
    h = hashlib.md5()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    R["elapsed_s"] = round(time.time() - T0, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def left_s():
    return RUN_DEADLINE_S - (time.time() - T0) - RESERVE_S


def private_bytes():
    """LabVIEW's private bytes - the COMPANION of the handle count, which
    `docs/toolkit-capabilities.md:484-485` records as BLIND to VI Server refnums. Same subprocess shape as
    `bench_prep.labview_handles`:64-71, which this file already imports."""
    import subprocess
    try:
        r = subprocess.run(
            ["powershell", "-NoProfile", "-Command",
             "(Get-Process LabVIEW -ErrorAction SilentlyContinue | Select-Object -First 1)"
             ".PrivateMemorySize64"],
            capture_output=True, text=True, timeout=60)
        return int((r.stdout or "").strip() or 0)
    except Exception:                                                              # noqa: BLE001
        return None


def purge_junk(target, nodes_before, tag, hints):
    """The measured junk shape of the OpConnect* family: a fresh `Invoke` node with ZERO wired terminals
    (`tools/bench/c80_rowd_routeA_r2.log:275-276`; the delivered Row C purged one). Anything else that is
    new is REPORTED VERBATIM and LEFT ALONE - deleting a node whose terminal table was never read is the
    one branch that could destroy the artefact. This is `build_d1_m3a3.purge_junk` re-bound to an explicit
    target; `M.census_and_purge` itself is not called because it writes M's own JSON sidecar."""
    nodes_after, _ = M.node_census(target, "%s AFTER" % tag)
    fresh = M.new_nodes(nodes_before, nodes_after)
    rec = {"tag": tag, "node_count_before": len(nodes_before), "node_count_after": len(nodes_after),
           "new_uids": [(n["uid"], n["class"], n["pos"]) for n in fresh], "deleted": [],
           "reported_not_deleted": []}
    fact("%s CENSUS DIFF: Node %d -> %d ; %d new uid(s): %r"
         % (tag, len(nodes_before), len(nodes_after), len(fresh), rec["new_uids"]))
    for n in fresh:
        loc, rows = M.node_view(target, n["uid"], hints, "%s new #%s" % (tag, n["uid"]))
        wired = [t for t in rows if t.get("has_wire")]
        entry = {"uid": n["uid"], "class": n["class"], "pos": n["pos"],
                 "label": (loc.get("found") or {}).get("label"),
                 "diagram_uid": (loc.get("found") or {}).get("diagram_uid"),
                 "n_terminals": len(rows), "n_wired": len(wired)}
        if n["class"] == "Invoke" and rows and not wired:
            fact("%s the junk node's FULL terminal table is printed above; %d terminal(s), %d WIRED - the "
                 "purge precondition (ZERO wired) HOLDS" % (tag, len(rows), len(wired)))
            entry["delete"] = M.delete_by_uid(target, "Node", n["uid"], "%s purge" % tag)
            rec["deleted"].append(entry)
        else:
            rec["reported_not_deleted"].append(entry)
            fact("%s NEW NODE NOT DELETED (not the measured junk shape, or its table could not be read): "
                 "#%s class %r label %r, %d terminal(s), %d wired - REPORTED, left alone"
                 % (tag, n["uid"], n["class"], entry["label"], entry["n_terminals"], entry["n_wired"]))
    final = nodes_after
    if rec["deleted"]:
        final, _ = M.node_census(target, "%s AFTER THE PURGE" % tag)
        fact("%s purge arithmetic: Node %d -> %d -> %d"
             % (tag, len(nodes_before), len(nodes_after), len(final)))
    rec["node_count_after_purge"] = len(final)
    return final, rec


def labels_of(target, indicators=False):
    return {l for _i, l, ind in g.fp_labels(target) if bool(ind) == indicators}


def new_labels(target, before, indicators=False):
    return [l for _i, l, ind in g.fp_labels(target) if bool(ind) == indicators and l not in before]


def wire_named(src_cls, src_uid, src_name, dst_cls, dst_uid, dst_name, branch=False, tag=""):
    """Wire by NAME with EXPLICIT traverse classes, verified by the SAME wire uid on BOTH ends.
    `build_opconnectnested_v1.connect` is NOT used here: it derives the class from the node LABEL, and a
    freshly built Property node's label is not 'Property Node' (build_opfstunnelterm_v2 wires the same
    shape with explicit classes for exactly this reason)."""
    g.wire(OP, src_cls, idx(OP, src_cls, src_uid), src_name,
           dst_cls, idx(OP, dst_cls, dst_uid), dst_name, branch=branch)
    w = walk(OP, 0)
    a = (term(w[src_uid][2], src_name, True) or {}).get("wire")
    b = (term(w[dst_uid][2], dst_name, False) or {}).get("wire")
    ok = bool(a) and a == b
    print("      %s#%s.%r -> #%s.%r: wire %r / %r %s"
          % (tag, src_uid, src_name, dst_uid, dst_name, a, b, "OK" if ok else "MISMATCH"), flush=True)
    if not ok:
        raise Stop("%swire #%s.%r -> #%s.%r not on both ends (%r vs %r)"
                   % (tag, src_uid, src_name, dst_uid, dst_name, a, b))
    return a


def data_out(rows):
    """The single NON-STANDARD source terminal of a property node = its data output. Read back, never
    assumed (the donor's W5b does the same for `Terms[]`)."""
    return [r["name"] for r in rows
            if r["is_source"] and r["name"] not in ("reference out", "error out")]


def del_wire(target, wire_uid, tag=""):
    order = [o["uid"] for o in g.report_all(target, "Wire")]
    if wire_uid not in order:
        fact("%s wire %r is not in the Wire traverse order - nothing deleted" % (tag, wire_uid))
        return False
    g.delete_object(target, "Wire", order.index(wire_uid), verify=False)
    print("      %sdeleted wire w%s" % (tag, wire_uid), flush=True)
    return True


def del_node(target, cls, uid, tag=""):
    order = [o["uid"] for o in g.report_all(target, cls)]
    if uid not in order:
        fact("%s %s #%r already gone" % (tag, cls, uid))
        return False
    before = set(order)
    g.delete_object(target, cls, order.index(uid), verify=False)
    gone = before - g.uids(target, cls)
    print("      %sdeleted %s #%s -> gone %r" % (tag, cls, uid, sorted(gone)), flush=True)
    return uid in gone


# ======================================================================= [0] files only, zero LabVIEW
def phase_files():
    head("[0] FILES ONLY - the bed's md5 BEFORE anything, the five pins, the claudeDev listing, the donors")
    got = md5(BED)
    R["bed_md5_before"] = got
    R["bed_bytes"] = os.path.getsize(BED)
    gate("H1 bed md5 before == %s (%d B)" % (BED_MD5, BED_BYTES), got == BED_MD5 and R["bed_bytes"] == BED_BYTES,
         "got %s, %d bytes" % (got, R["bed_bytes"]), fatal=True)
    R["pins_before"] = {}
    for label, path, want in PINS:
        have = md5(path) if os.path.exists(path) else "MISSING"
        R["pins_before"][label] = have
        fact("PIN BEFORE %-16s %s  (want %s) %s"
             % (label, have, want, ("OK" if have == want else "DIFFERS")))
    R["claudedev_before"] = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    fact("claudeDev holds %d .vi file(s) BEFORE the run" % len(R["claudedev_before"]))
    for p, nm in ((DONOR, "OpConnectFromWire_v0.vi (THE DONOR)"), (V5, "OpWireSource_v5.vi (gate 4's reader)")):
        gate("B0 %s on disk" % nm, os.path.isfile(p), p, fatal=True)
    R["donor_md5_before"] = md5(DONOR)
    fact("donor md5 %s" % R["donor_md5_before"])
    if os.path.exists(OP):
        fact("an OLD %s exists (md5 %s) - it is REPLACED by this build"
             % (os.path.basename(OP), md5(OP)))


# ======================================================================= [1] restart
def phase_restart():
    head("[1] RESTART LabVIEW (STATUS orders it; the instance was left at ~31,281 handles)")
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


# ======================================================================= [B] THE BUILD
def build():
    head("[B0] the donor at ExecState 1")
    g.open_panel(DONOR)
    es = g.exec_state(DONOR)
    gate("B0 donor OpConnectFromWire_v0 ExecState 1", es == 1, "ExecState %r" % es, fatal=True)
    g.close_panel(DONOR)

    head("[B1] the copy, and the SOURCE LADDER read BY WIRE TOPOLOGY - never by uid")
    if os.path.exists(OP):
        os.remove(OP)
    shutil.copyfile(DONOR, OP)
    time.sleep(0.4)
    g.report_all(OP, "SubVI")
    g.open_panel(OP)
    time.sleep(0.8)
    w = walk(OP, 0)
    es = g.exec_state(OP)
    stale = [u for u, (_n, _l, rows) in w.items() if "LeftTerm" in data_out(rows)]
    gate("B1 the copy is a CLEAN donor: ExecState 1 and NONE of this build's own additions present "
         "(no `LeftTerm` output anywhere)", es == 1 and not stale,
         "ExecState %r, LeftTerm-carrying nodes %r, %d nodes" % (es, stale, len(w)), fatal=True)
    inv = next((u for u, (_n, lab, _r) in w.items() if lab == "Invoke Node"), None)
    gate("B1b the Invoke node found", inv is not None, "#%r" % inv, fatal=True)
    ws_wire = (term(w[inv][2], "Wire Source", False) or {}).get("wire")
    gate("B1c the Invoke's `Wire Source` is currently fed", bool(ws_wire),
         "Invoke #%s w%r" % (inv, ws_wire), fatal=True)
    ia = src_of(w, ws_wire)
    w_arr = (term(w[ia][2], "array", False) or {}).get("wire") if ia else None
    pn_wire = src_of(w, w_arr) if w_arr else None
    w_ref = (term(w[pn_wire][2], "reference", False) or {}).get("wire") if pn_wire else None
    tmsc = src_of(w, w_ref) if w_ref else None
    w_tc = (term(w[tmsc][2], "target class", False) or {}).get("wire") if tmsc else None
    w_gobj = (term(w[tmsc][2], "reference", False) or {}).get("wire") if tmsc else None
    u_uid = src_of(w, w_gobj) if w_gobj else None
    fact("B1 LADDER: Invoke #%r <- IA #%r (w%r) <- WirePN #%r (w%r) <- TMSC #%r (target class w%r, "
         "reference w%r) <- subVI #%r %r"
         % (inv, ia, ws_wire, pn_wire, w_arr, tmsc, w_tc, w_gobj, u_uid,
            (w[u_uid][1] if u_uid in w else None)))
    gate("B1d every rung of the source ladder resolved by wire topology",
         all(x is not None for x in (ia, pn_wire, tmsc, u_uid)),
         "ia %r pn %r tmsc %r subvi %r" % (ia, pn_wire, tmsc, u_uid), fatal=True)
    gate("B1e the Wire property node's data output is `Terms[]`", data_out(w[pn_wire][2]) == ["Terms[]"],
         "%r" % data_out(w[pn_wire][2]), fatal=True)
    gate("B1f the ladder head is `UID to GObject Reference.vi`",
         "uid to gobject" in str(w[u_uid][1]).lower(), "%r" % (w[u_uid][1],), fatal=True)
    R["B"]["ladder"] = {"invoke": inv, "index_array": ia, "wire_pn": pn_wire, "tmsc": tmsc,
                        "uidvi": u_uid, "ws_wire": ws_wire, "arr_wire": w_arr, "ref_wire": w_ref,
                        "target_class_wire": w_tc, "gobject_wire": w_gobj}

    head("[B2] delete the Invoke's `Wire Source` net")
    del_wire(OP, ws_wire, "B2 ")
    g.remove_bad_wires_scripted(OP)
    w = walk(OP, 0)
    now = (term(w[inv][2], "Wire Source", False) or {}).get("wire")
    gate("B2 the Invoke's `Wire Source` reads 0", now == 0, "w%r" % now, fatal=True)

    head("[B3] delete the Index Array and the `Wire.Terms[]` property node")
    del_node(OP, "IndexArray", ia, "B3 ")
    del_node(OP, "Property", pn_wire, "B3 ")
    for wu in (w_arr, w_ref, w_tc):
        del_wire(OP, wu, "B3 ")
    g.remove_bad_wires_scripted(OP)
    w = walk(OP, 0)
    tc_now = (term(w[tmsc][2], "target class", False) or {}).get("wire")
    sc_now = (term(w[tmsc][2], "specific class reference", True) or {}).get("wire")
    gate("B3 the TMSC's `target class` AND `specific class reference` both read 0",
         tc_now == 0 and sc_now == 0, "target class w%r, specific class reference w%r" % (tc_now, sc_now),
         fatal=True)
    gate("B3b the Index Array and the Wire property node are gone",
         ia not in g.uids(OP, "IndexArray") and pn_wire not in g.uids(OP, "Property"),
         "IA #%s gone %r, WirePN #%s gone %r"
         % (ia, ia not in g.uids(OP, "IndexArray"), pn_wire, pn_wire not in g.uids(OP, "Property")),
         fatal=True)

    head("[B4] the FlatSequenceInnerTunnel.LeftTerm property node (1C3A9000)")
    pn0 = g.uids(OP, "Property")
    g.build_property(OP, FSIT_CLASS, [(P_LEFT, False)], (600, 2700))
    newpn = g.new_since(OP, "Property", pn0)
    gate("B4 exactly one new Property node", len(newpn) == 1, "%r" % [o["uid"] for o in newpn], fatal=True)
    pn_fsit = newpn[0]["uid"]
    w = walk(OP, 0)
    outs = data_out(w[pn_fsit][2])
    gate("B4b its single data output is `LeftTerm` (READ BACK from the machine)", outs == ["LeftTerm"],
         "#%s outputs %r" % (pn_fsit, outs), fatal=True)
    left_name = outs[0]

    head("[B5] the FSIT-TYPED SEED - create_control on that node's own `reference`")
    before = labels_of(OP)
    n_fsit = w[pn_fsit][0]
    ref_i = (term(w[pn_fsit][2], "reference", False) or {}).get("i")
    g.create_control(OP, n_fsit, ref_i)
    got = new_labels(OP, before)
    gate("B5 exactly ONE new control = the FlatSequenceInnerTunnel-typed seed", len(got) == 1,
         "%r (Nodes[%r] terminal %r)" % (got, n_fsit, ref_i), fatal=True)
    seed = got[0]
    w = walk(OP, 0)
    w_seed = (term(w[pn_fsit][2], "reference", False) or {}).get("wire")
    if w_seed:
        del_wire(OP, w_seed, "B5 ")
        g.remove_bad_wires_scripted(OP)
    g.wire_control(OP, [seed], "Function", idx(OP, "Function", tmsc), ["target class"])
    w = walk(OP, 0)
    pw = {r["label"]: r for r in g.panel_wiring(OP)}
    a = pw.get(seed, {}).get("wire")
    b = (term(w[tmsc][2], "target class", False) or {}).get("wire")
    gate("B5b the seed types the CAST: seed -> TMSC `target class` on both ends",
         bool(a) and a == b, "seed %r w%r / TMSC w%r" % (seed, a, b), fatal=True)

    head("[B6/B7] TMSC -> LeftTerm node -> the Invoke's `Wire Source`")
    wire_named("Function", tmsc, "specific class reference", "Property", pn_fsit, "reference", tag="B6 ")
    wire_named("Property", pn_fsit, left_name, "Invoke", inv, "Wire Source", tag="B7 ")

    head("[B8] the TWO UID ECHOES - GObject.UID (632A813) on the INPUT side (the resolver's own GObject, "
         "Pre-decided 125's rule LITERALLY) and on the OUTPUT side (LeftTerm, Pre-decided 127 gate 3)")
    echo_inds = {}
    for tag, src_cls, src_uid, src_name, pos, what in (
            ("uid_back", "SubVI", u_uid, "GObject", (1100, 2500),
             "the RESOLVED object's own uid - must equal the uid passed IN"),
            ("term_uid", "Property", pn_fsit, left_name, (1100, 2700),
             "the LeftTerm's own uid - Pre-decided 127's gate (3)")):
        pn0 = g.uids(OP, "Property")
        g.build_property(OP, "VI Server:GObject", [(P_UID, False)], pos)
        newpn = g.new_since(OP, "Property", pn0)
        gate("B8 %s: exactly one new Property node" % tag, len(newpn) == 1,
             "%r" % [o["uid"] for o in newpn], fatal=True)
        pn_e = newpn[0]["uid"]
        wire_named(src_cls, src_uid, src_name, "Property", pn_e, "reference", branch=True,
                   tag="B8 %s " % tag)
        w = walk(OP, 0)
        uid_out = data_out(w[pn_e][2])
        gate("B8b %s: its data output is `UID`" % tag, uid_out == ["UID"], "%r" % uid_out, fatal=True)
        before_i = labels_of(OP, indicators=True)
        g.create_indicator(OP, w[pn_e][0], (term(w[pn_e][2], "UID", True) or {}).get("i"))
        got_i = new_labels(OP, before_i, indicators=True)
        gate("B8c %s: exactly ONE new indicator = %s" % (tag, what), len(got_i) == 1, "%r" % got_i,
             fatal=True)
        echo_inds[tag] = (got_i[0], pn_e)
        fact("B8 %s echo: #%s.%r -> Property #%s -> indicator %r" % (tag, src_uid, src_name, pn_e, got_i[0]))
    uid_back_ind, pn_back = echo_inds["uid_back"]
    term_uid_ind, pn_uid = echo_inds["term_uid"]
    err_inds = {}
    for uid_, tag in ((pn_fsit, "fsit"), (pn_uid, "termuid"), (pn_back, "uidback")):
        w = walk(OP, 0)
        t = term(w[uid_][2], "error out", True)
        if not t or t["wire"]:
            fact("B8 #%s (%s) `error out` missing or already wired - skipped" % (uid_, tag))
            continue
        before_i = labels_of(OP, indicators=True)
        g.create_indicator(OP, w[uid_][0], t["i"])
        now_i = new_labels(OP, before_i, indicators=True)
        if len(now_i) == 1:
            err_inds[tag] = now_i[0]
        fact("B8 #%s (%s) error indicator %r" % (uid_, tag, now_i))
    gate("B8d all three new error outs carry an indicator", len(err_inds) == 3, "%r" % err_inds)

    head("[B9] auto error handling OFF, ExecState 1, SAVE")
    aeh_ok = True
    try:
        g.set_auto_error_handling(OP, False)
    except Exception as e:                                                         # noqa: BLE001
        aeh_ok = False
        fact("set_auto_error_handling failed (%s)" % str(e)[:80])
    gate("B9a auto error handling is OFF", aeh_ok, fatal=True)
    es = g.exec_state(OP)
    if es != 1:
        w = walk(OP, 0)
        orphans = [(u, r["name"]) for u in w for r in w[u][2]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        fact("B9 DIAGNOSTIC unwired non-error SINK terminals: %r" % orphans)
    gate("B9 ExecState 1 - the op is runnable", es == 1, "ExecState %r" % es, fatal=True)
    size = g.save(OP)
    R["B"]["op_md5"] = md5(OP)
    R["B"]["op_bytes"] = size
    fact("B9 SAVED %s (%s bytes) md5 %s" % (OP, size, R["B"]["op_md5"]))
    gate("B9b donor md5 unchanged", md5(DONOR) == R["donor_md5_before"], R["donor_md5_before"])

    labels = {"route": "fsit-leftterm-source",
              "vi_path": "vi path", "class_name": "Class Name",
              "sink_diag": "index", "sink_node": "index 2", "sink_term": "index 3",
              "dead_src_node": "index 4", "dead_src_term": "index 5", "dead_src_diag": "index 6",
              "dead_wire_term_index": "index 7",
              "fsit_uid": "UID 3", "seed": seed, "old_wire_seed": "reference 2",
              "err_uidvi": "error out 2", "err_fsit": err_inds.get("fsit", ""),
              "err_termuid": err_inds.get("termuid", ""), "err_uidback": err_inds.get("uidback", ""),
              "uid_back": uid_back_ind,
              "term_uid": term_uid_ind, "sink_wire_uid": "UID 2", "is_broken": "Is Broken?",
              "method": METHOD, "left_terminal_prop": P_LEFT, "uid_prop": P_UID, "class": FSIT_CLASS,
              "left_out_name": left_name,
              "panel": [(i, lbl, ind) for i, lbl, ind in g.fp_labels(OP)]}
    with open(MAP_OUT, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=1)
    fact("B9 labels -> %s" % MAP_OUT)
    R["B"]["labels"] = labels
    g.close_panel(OP)
    return labels


# ======================================================================= the wrapper
def fsit_connect(target, fsit_uid, sink_diag, sink_node, sink_term, labels, count_wires=False):
    """Wire `FlatSequenceInnerTunnel(uid=fsit_uid).LeftTerm` into
    Diagram[sink_diag].Nodes[sink_node].Terminals[sink_term] with `Terminal.Connect Wire` 6349C03.
    Every readout is POISONED before the run (Pre-decided 125): a stale value can never be read as an
    answer, and `Is Broken?` is poisoned to True so only a fresh write can make it False."""
    w0 = g.count(target, "Wire") if count_wires else None
    vi = g.op(OP)
    for k, v in ((labels["term_uid"], 0), (labels["uid_back"], 0), (labels["sink_wire_uid"], 0),
                 (labels["is_broken"], True), ("UID", 0), ("Name", "POISON")):
        try:
            vi.SetControlValue(k, v)
        except Exception:                                                          # noqa: BLE001
            pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["fsit_uid"], int(fsit_uid))
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
    out = {"err": err}
    for k in ("err_uidvi", "err_fsit", "err_termuid", "err_uidback"):
        if labels.get(k):
            out[k] = g._err(vi, labels[k]) or ""
    for k, lab in (("term_uid", labels["term_uid"]), ("uid_back", labels["uid_back"]),
                   ("sink_wire_uid", labels["sink_wire_uid"]),
                   ("is_broken", labels["is_broken"]), ("UID", "UID"), ("Name", "Name")):
        try:
            out[k] = vi.GetControlValue(lab)
        except Exception:                                                          # noqa: BLE001
            out[k] = "READ FAILED"
    if count_wires:
        out["wire_delta"] = g.count(target, "Wire") - w0
    return out


# ======================================================================= [G2/G3] handles + the uid echo
def gates_23(labels):
    head("[G2/G3] %d CONSECUTIVE CALLS on a dated scratch copy - handle count flat +-%d, and the uid echo"
         % (HANDLE_CALLS, HANDLE_TOL))
    shutil.copyfile(BED, SCRATCH_H)
    time.sleep(0.4)
    gate("G2a the handle-test scratch is a byte-identical copy of the bed",
         md5(SCRATCH_H) == R["bed_md5_before"], os.path.basename(SCRATCH_H), fatal=True)
    t = time.time()
    _, err = safe("ensure_loaded(SCRATCH_H)", lambda: g.ensure_loaded(SCRATCH_H))
    fact("ensure_loaded(handle scratch) took %.1f s%s" % (time.time() - t, ((" ERROR " + err) if err else "")))
    # the SINK address: the NEW loop's shift-register OUTER terminal, resolved LIVE (never carried)
    d_idx, trip_ok = resolve_triple(SCRATCH_H, "G2")
    hints = [d_idx]
    nodes0, _ = M.node_census(SCRATCH_H, "G2b BEFORE the 20 calls")
    handles_before, _ = safe("handles before the 20 calls", labview_handles)
    priv_before = private_bytes()
    rows = []
    for i in range(HANDLE_CALLS):
        r = fsit_connect(SCRATCH_H, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX, labels)
        r["call"] = i + 1
        rows.append(r)
        if i in (0, HANDLE_CALLS - 1) or r.get("err"):
            fact("G2 call %2d: uid_back=%r term_uid=%r sink_wire=%r is_broken=%r err=%r sub=%r"
                 % (i + 1, r.get("uid_back"), r.get("term_uid"), r.get("sink_wire_uid"),
                    r.get("is_broken"), str(r.get("err"))[:90],
                    {k: v for k, v in r.items() if k.startswith("err_") and v}))
    # NO census inside the loop, on purpose: a `report_all('Node')` on a 635-node VI moves the very handle
    # count this window is measuring. The junk rate is therefore read as TOTAL / 20 immediately after.
    handles_after, _ = safe("handles after the 20 calls", labview_handles)
    priv_after = private_bytes()
    R["G"]["handle_rows"] = rows
    R["G"]["handles_before_calls"] = handles_before
    R["G"]["handles_after_calls"] = handles_after
    R["G"]["private_bytes_before"] = priv_before
    R["G"]["private_bytes_after"] = priv_after
    delta = (handles_after - handles_before) if (isinstance(handles_before, int)
                                                 and isinstance(handles_after, int)) else None
    R["G"]["handle_delta"] = delta
    pdrift = None
    if isinstance(priv_before, int) and isinstance(priv_after, int):
        pdrift = round((priv_after - priv_before) / (1024.0 * 1024.0), 2)
    R["G"]["private_mb_drift"] = pdrift
    fact("G2 COMPANION MEASUREMENT (the review's B4; docs/toolkit-capabilities.md:484-485 - the kernel "
         "handle count is BLIND to VI Server refnums): LabVIEW private bytes %r -> %r, drift %r MB over "
         "%d calls. REPORTED, not gated: S0's own G-C was <= 5 MB against ops that CREATED 20 property "
         "nodes in the target; this op creates none." % (priv_before, priv_after, pdrift, HANDLE_CALLS))
    gate("G2 %d consecutive calls leave the handle count flat +-%d (a REGRESSION CHECK against the S0 "
         "baseline docs/toolkit-capabilities.md:460-478, not a hygiene proof)" % (HANDLE_CALLS, HANDLE_TOL),
         delta is not None and abs(delta) <= HANDLE_TOL,
         "before %r -> after %r, delta %r ; private-bytes drift %r MB"
         % (handles_before, handles_after, delta, pdrift))
    nodes20, _ = M.node_census(SCRATCH_H, "G2b AFTER the 20 calls")
    fact("G2b junk accumulation over %d calls: Node %d -> %d = %.2f new node(s) PER CALL (the OpConnect* "
         "family mints a stray `Invoke`, c80_rowd_routeA_r2.log:275-276; the delivered Row C purged one)"
         % (HANDLE_CALLS, len(nodes0), len(nodes20), (len(nodes20) - len(nodes0)) / float(HANDLE_CALLS)))
    _final, prec = purge_junk(SCRATCH_H, nodes0, "G2b", hints)
    R["G"]["g2_purge"] = prec
    echoes = sorted({int(r["term_uid"]) for r in rows if isinstance(r.get("term_uid"), (int, float))})
    backs = sorted({int(r["uid_back"]) for r in rows if isinstance(r.get("uid_back"), (int, float))})
    R["G"]["uid_echoes"] = echoes
    R["G"]["uid_back_echoes"] = backs
    gate("G3 a call with fsit_uid %d returns the LeftTerm whose OWN uid echoes #%d"
         % (FSIT_UID, LEFT_TERM_EXPECT),
         echoes == [LEFT_TERM_EXPECT],
         "distinct echoes across %d calls: %r (want [%d]); call 1 = %r"
         % (len(rows), echoes, LEFT_TERM_EXPECT, rows[0].get("term_uid") if rows else None))
    gate("G3a THE INPUT-SIDE ECHO (Pre-decided 125's rule, the review's A3): the resolver's own `uid_back` "
         "equals the uid passed IN (#%d) on every call" % FSIT_UID,
         backs == [FSIT_UID],
         "distinct uid_back across %d calls: %r (want [%d]); call 1 = %r"
         % (len(rows), backs, FSIT_UID, rows[0].get("uid_back") if rows else None))
    gate("G3b no op error on the FIRST call (the one gate 3 reads)",
         bool(rows) and not rows[0].get("err"),
         "err %r ; sub %r" % (rows[0].get("err") if rows else None,
                              {k: v for k, v in (rows[0] if rows else {}).items()
                               if k.startswith("err_") and v}))
    fact("G2/G3 triple resolution on the handle scratch: %s" % trip_ok)


def resolve_triple(target, tag):
    """The NEW loop's (diagram traverse index, Nodes[] index, Terminals[] index), resolved LIVE with a uid
    echo - an index is never carried from a census."""
    rows, e = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(target, "Diagram"), [])
    d_idx = next((r["i"] for r in (rows or []) if r["uid"] == D686), None)
    fact("%s Diagram census %d row(s); Diagram #%d at traverse index %r%s"
         % (tag, len(rows or []), D686, d_idx, ((" ERROR " + e) if e else "")))
    if d_idx is None:
        raise Stop("%s Diagram #%d not found in the traverse order" % (tag, D686))
    (echo, trows), e = safe("%s node_terms_uid(%r, %d)" % (tag, d_idx, LOOP_NODES_IDX),
                            lambda: g.node_terms_uid(target, d_idx, LOOP_NODES_IDX), (None, []))
    trow = next((t for t in (trows or []) if t["i"] == LOOP_TERM_IDX), None)
    fact("%s Diagram[%r].Nodes[%d] uid echo %r (want the NEW WhileLoop #%d -> %s); t%d row %r"
         % (tag, d_idx, LOOP_NODES_IDX, echo, LOOP_NEW, "MATCH" if echo == LOOP_NEW else "MISMATCH",
            LOOP_TERM_IDX, trow))
    if echo != LOOP_NEW:
        raise Stop("%s the Nodes[%d] uid echo is %r, not the NEW loop #%d - the address is NOT believed"
                   % (tag, LOOP_NODES_IDX, echo, LOOP_NEW))
    return d_idx, {"diagram_index": d_idx, "node_uid_echo": echo, "terminal_row": trow}


# ======================================================================= [G4] the end-to-end exercise
def gate4(labels):
    head("[G4] END-TO-END on a dated scratch COPY of the bed: delete w%d, connect, assert OWNER IDENTITY"
         % ROWD_WIRE)
    shutil.copyfile(BED, SCRATCH_E)
    time.sleep(0.4)
    gate("G4a the exercise scratch is a byte-identical copy of the bed",
         md5(SCRATCH_E) == R["bed_md5_before"], os.path.basename(SCRATCH_E), fatal=True)
    t = time.time()
    _, err = safe("ensure_loaded(SCRATCH_E)", lambda: g.ensure_loaded(SCRATCH_E))
    fact("ensure_loaded(exercise scratch) took %.1f s%s"
         % (time.time() - t, ((" ERROR " + err) if err else "")))
    es = g.exec_state(SCRATCH_E)
    fact("ExecState of the exercise scratch (= the bed) = %r - RECORDED, NEVER a criterion "
         "(Pre-decided 89/97; the bed is broken BY DESIGN)" % es)

    d_idx, trip = resolve_triple(SCRATCH_E, "G4")
    R["G"]["g4_triple"] = trip
    pre = trip["terminal_row"]
    fact("G4 BEFORE the delete: border t%d name=%r is_source=%r wire=%r"
         % (LOOP_TERM_IDX, (pre or {}).get("name"), (pre or {}).get("is_source"), (pre or {}).get("wire")))

    head("[G4] delete wire %d" % ROWD_WIRE)
    deleted = del_wire(SCRATCH_E, ROWD_WIRE, "G4 ")
    g.remove_bad_wires_scripted(SCRATCH_E)
    gate("G4b wire %d deleted" % ROWD_WIRE, deleted, "delete_object on the Wire traverse order",
         fatal=True)
    _, trows = g.node_terms_uid(SCRATCH_E, d_idx, LOOP_NODES_IDX)
    bare = next((t for t in (trows or []) if t["i"] == LOOP_TERM_IDX), None)
    fact("G4 AFTER the delete: border t%d wire=%r (BARE expected)" % (LOOP_TERM_IDX, (bare or {}).get("wire")))
    gate("G4c the border terminal is BARE before the connect", (bare or {}).get("wire") == 0,
         "wire %r" % (bare or {}).get("wire"), fatal=True)

    head("[G4] THE CALL - OpFsInnerTunnelConnect_v0(fsit_uid=%d, triple=(%r, %d, %d))"
         % (FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX))
    nodes0, _ = M.node_census(SCRATCH_E, "G4 BEFORE the call")
    r = fsit_connect(SCRATCH_E, FSIT_UID, d_idx, LOOP_NODES_IDX, LOOP_TERM_IDX, labels, count_wires=True)
    R["G"]["g4_call"] = r
    fact("G4 CALL RETURN: %s" % json.dumps(r, default=str)[:700])
    gate("G4d the op reported NO error", not r.get("err"),
         "err %r ; sub %r" % (r.get("err"),
                              {k: v for k, v in r.items() if k.startswith("err_") and v}))
    gate("G4e the LeftTerm uid echo is #%d on the exercise call" % LEFT_TERM_EXPECT,
         r.get("term_uid") == LEFT_TERM_EXPECT, "term_uid %r" % r.get("term_uid"))
    gate("G4e2 the INPUT-side echo is #%d on the exercise call (Pre-decided 125)" % FSIT_UID,
         r.get("uid_back") == FSIT_UID, "uid_back %r" % r.get("uid_back"))
    # the junk `Invoke` this writer family mints in the TARGET - measured and purged BEFORE the
    # acceptance walk, because D-3 writes to the BED where it would be saved into the artefact
    _final, prec4 = purge_junk(SCRATCH_E, nodes0, "G4", [d_idx])
    R["G"]["g4_purge"] = prec4

    _, trows = g.node_terms_uid(SCRATCH_E, d_idx, LOOP_NODES_IDX)
    after = next((t for t in (trows or []) if t["i"] == LOOP_TERM_IDX), None)
    neww = (after or {}).get("wire")
    fact("G4 AFTER the connect: border t%d wire=%r ; the op's own `UID 2` (ordered after the write) = %r ; "
         "wire_delta %r" % (LOOP_TERM_IDX, neww, r.get("sink_wire_uid"), r.get("wire_delta")))
    gate("G4f the border terminal went BARE -> NON-ZERO", bool(neww), "wire %r" % neww, fatal=True)
    gate("G4g the op's own `Wire.Is Broken?` 6371004 on the created wire reads FALSE "
         "(poisoned True before the run, so only a fresh write can make it False)",
         r.get("is_broken") is False, "Is Broken? %r" % r.get("is_broken"))

    head("[G4] THE ACCEPTANCE: OWNER IDENTITY on the new net (Pre-decided 117 as corrected by 120)")
    walkr, werr = safe("G4 OpWireSource_v5(UID 2 = %r)" % neww,
                       lambda: WIRE_TERMS(SCRATCH_E, int(neww), n=8), [])
    M.print_walk("G4", neww, walkr, werr)
    bad = M.pd85_violations(neww, walkr)
    srcs = [t for t in (walkr or []) if t.get("is_source") and t.get("owner_uid")]
    owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid"))) for t in (walkr or [])
                     if t.get("owner_uid")})
    src_owners = sorted({(str(t.get("owner_class")), int(t.get("owner_uid"))) for t in srcs})
    R["G"]["g4_walk"] = walkr
    R["G"]["g4_source_owners"] = src_owners
    R["G"]["g4_all_owners"] = owners
    R["G"]["g4_pd85_violations"] = len(bad)
    gate("G4h PD85 violations 0 on the walk (or the walk is not believed at all)", not bad,
         "%d violation(s) %r" % (len(bad), bad))
    gate("G4i the net's SOURCE TERMINAL OWNER is RightShiftRegister #%d, and nothing else is a source"
         % RSR_EXPECT,
         src_owners == [("RightShiftRegister", RSR_EXPECT)],
         "source-terminal owners %r (want [('RightShiftRegister', %d)])" % (src_owners, RSR_EXPECT))
    gate("G4j the OLD source #%d is OFF the net" % OLD_SOURCE,
         all(u != OLD_SOURCE for _c, u in owners),
         "every owner on the net: %r" % (owners,))


# ======================================================================= [H] hygiene
def phase_hygiene():
    head("[H] HYGIENE - close panels, delete both scratches, re-read every pin, handles at both ends")
    for p in (SCRATCH_H, SCRATCH_E, OP, DONOR):
        safe("close_panel(%s)" % os.path.basename(p), lambda q=p: g.close_panel(q))
    R["H"]["ref_counts"] = g.ref_counts()
    fact("gscript ref_counts (opened / closed / live / cached op VIs): %r" % R["H"]["ref_counts"])
    gate("H5 VI-Server reference counter level (opened == closed)",
         R["H"]["ref_counts"]["live"] == 0, "%r" % R["H"]["ref_counts"])
    handles, _ = safe("handles after the work", labview_handles)
    R["H"]["handles_after_work"] = handles
    fact("LabVIEW handle count AFTER the work: %r" % handles)
    _, err = safe("restart_labview before the deletes", restart_labview)
    g.reset()
    time.sleep(2.0)
    for p in (SCRATCH_H, SCRATCH_E):
        okdel = True
        for attempt in range(6):
            try:
                if os.path.exists(p):
                    os.remove(p)
                break
            except Exception as e:                                                 # noqa: BLE001
                okdel = False
                fact("delete attempt %d on %s failed: %s" % (attempt + 1, os.path.basename(p), str(e)[:120]))
                time.sleep(4.0)
        gate("H4 scratch deleted: %s" % os.path.basename(p), not os.path.exists(p),
             "%s%s" % (p, ("" if okdel else " (needed retries)")))
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
    after = sorted(os.path.basename(p) for p in glob.glob(os.path.join(g.CLAUDEDEV, "*.vi")))
    added = sorted(set(after) - set(R.get("claudedev_before") or []))
    gone = sorted(set(R.get("claudedev_before") or []) - set(after))
    R["H"]["claudedev_added"] = added
    R["H"]["claudedev_removed"] = gone
    gate("H6 THE FILES THIS RUN LEFT ON DISK == [%s] and nothing was removed" % os.path.basename(OP),
         added == [os.path.basename(OP)] and not gone,
         "added %r removed %r" % (added, gone))
    fact("THE FILES THIS RUN LEFT ON DISK: %r  (removed: %r)" % (added, gone))
    if os.path.isfile(OP):
        R["H"]["op_md5_final"] = md5(OP)
        R["H"]["op_bytes_final"] = os.path.getsize(OP)
        fact("ARTEFACT %s md5 %s (%d bytes)"
             % (OP, R["H"]["op_md5_final"], R["H"]["op_bytes_final"]))
    handles2, _ = safe("handles final", labview_handles)
    R["H"]["handles_final"] = handles2
    fact("LabVIEW handle count at exit: %r (baseline ~31,500)" % handles2)


def main():
    print("=" * 100, flush=True)
    print("build_opfsinnertunnelconnect_v0 - D-2 of M3a-3b (Pre-decided 127): build, SAVE and EXERCISE "
          "OpFsInnerTunnelConnect_v0.vi", flush=True)
    print("=" * 100, flush=True)
    labels = None
    try:
        phase_files()
        phase_restart()
        labels = build()
        dump()
        head("[G1] ExecState of the SAVED op, re-read")
        g.reset()
        time.sleep(1.0)
        es = g.exec_state(OP)
        R["G"]["exec_state_saved"] = es
        gate("G1 ExecState 1 on the SAVED op (ExecState 0 IS LabVIEW's 'this VI is broken' verdict on this "
             "COM path; `Wire.Is Broken?` 6371004 is a WIRE property and is gate 4's)", es == 1,
             "ExecState %r ; md5 %s" % (es, R["B"].get("op_md5")), fatal=True)
        gates_23(labels)
        dump()
        if left_s() < 240:
            gate("G4 the end-to-end exercise had time to run", False,
                 "only %.0f s left of the deadline reserve" % left_s())
        else:
            gate4(labels)
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
