r"""build_opfstunnelterm_v1.py - the UID-ADDRESSED FLAT-SEQUENCE TUNNEL READER (BOTH classes), and the LIVE READ
that docs/vi-server-ids.json:142 records as the one thing never measured.

  IN  : vi path + the UID of a FlatSequence*Tunnel
  OUT : for BOTH faces of that tunnel - the terminal reference (uid) and the terminal's CONNECTED WIRE - plus,
        for face A, `Is Source?`, its connected wire and its OWNER class + uid.

cycle 20 step 2, docs/cycle20-plan.md:36-48. Pre-decided 1 (no motor, no serial, originals read-only, md5 before
AND after), 3 (a thing that can refuse is proven to refuse on a deliberately bad input), 4 (prior-art with
--recipe), 5 (archive/peer/ checked first).

=== WHY THIS IS `_v1` AND NOT A RE-SAVE OF `_v0` (cycle-22 judgement session, 2026-09-18) ===
  `_v0`'s stop record (tools/bench/stop_records.json record 2) is RELEASED for sha `0cc9f6ca...`, and
  `tools/stop_record.py:325` (`_check`) refuses on the FIRST record whose recipe path matches - so once `_v0`'s
  bytes changed (the 09:52 `wire_checked` patch, on disk `5a0df508...`) NO command naming `_v0` can launch, and
  re-saving it cannot clear its own record. The patched bytes can therefore only run under a NEW path with its
  OWN stop record. `_v0` is SUPERSEDED and UNLAUNCHABLE; it is left on disk untouched as the reviewed artefact.
  Naming follows the project's existing convention (tools/recipes/build_opconnectnested_v0.py / _v1.py).

=== WHAT THE PRIOR-ART REVIEW CHANGED (archive/peer/2026-09-18-priorart-fstunnel-reader.md, 4 findings, 0 novel;
    all four ACCEPTED by the cycle-20 judgement session, 2026-09-18) ===
  A3 `contradicted`  -> the FSIT half below. 14 of the 18 measured non-node crossings are FlatSequenceInnerTunnel
     (Traverse counts on the V6 copy: FSIT 518 vs FSOT 58, probe_flatseq_outer.log:30-32), and 1C3A9000 is
     REFUSED by the OUTER class (error 1077, the discriminator) - so ONE cast cannot reach both. This recipe
     therefore builds the cast for EACH class, from the same donor and by the same proven route, in one run:
     `OpFsTunnelTerm_v0.vi` (FSOT: OuterTerminal 3195B800 / InnerTerminal 3195B801) and
     `OpFsInnerTunnelTerm_v0.vi` (FSIT: LeftTerm 1C3A9000 / RightTerm 1C3A9001). They are two VIs and not two
     casts inside one VI because a second `To More Specific Class` has no creator - it must be brought in with
     `copy_by_index` from the NI example (docs/toolkit-capabilities.md:69) - while a second COPY OF THE DONOR
     costs nothing and adds no new failure mode; the reader `read_any()` picks the op by the owner's class, so
     the CALLER sees one reader over both classes.
  A4 `unread-evidence` -> gate T2 (the face test both arms of the accepted dual review asked for,
     archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md:144) is now IN the contract, and the crossing
     REFUSES a non-advancing hop (falsifier (c), :130) instead of scoring it as CROSSED. To make the face test
     machine-checkable each op reads BOTH faces' terminal uid AND both faces' `Terminal.Connected Wire` 634A000
     -> `GObject.UID`: the face you arrived on is the one whose connected wire IS the arrival wire, and the
     other face's wire is the continuation. (The arrived terminal's own uid is not observable from
     OpWireSource_v5 - it reports the terminal's OWNER, not the terminal - so wire identity is the operational
     form of "the arrived terminal matches one of 3195B800 / 3195B801".)
  B3 `helper-exists` -> the L4 walk no longer has a hop loop of its own: it CALLS
     `tools/bench/diag_tunnelsource_onehop.resolve()` (:198-233), inheriting its cache-based owner lookup, its
     max-hops bound and its "tunnel ... does not advance the hop" refusal (:230). This file only supplies what
     resolve() cannot do - the crossing of a flat-sequence border - and hands the continuation wire back to it.
  B4 `already-measured` -> gate L1 reads `owner_uid` and the `errs` column as well as `ownercls`, so the
     measured silent mode (uid 0 + error 1055 at a FlatSequenceFrame, tools/bench/diag_ownerchain_hop.log:7)
     FAILS the gate instead of passing it.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "before creating any new op"):
  * `docs/vi-server-ids.json:133-141` - `FlatSequenceOuterTunnel` 3195B800 `OuterTerminal` / 3195B801
    `InnerTerminal`; `FlatSequenceInnerTunnel` 1C3A9000 `LeftTerm` / 1C3A9001 `RightTerm`. MEASURED
    (probe_flatseq_outer.log:18-25, probe_flatseq_walk_run2.log:47-56); NOT re-derived here.
  * `docs/vi-server-ids.json:33,155` - `Terminal.Connected Wire` **634A000**, short name `Wire`
    (docs/NAMES.md:355), and `Wire -> GObject.UID` is a legal upcast (docs/NAMES.md:867).
  * `:142` - "_NOT_YET_MEASURED: A LIVE READ ... needs UID -> To More Specific Class(FlatSequence*Tunnel) ->
    property node, i.e. a new op." That op is this file.
  * DONOR `OpWireSource_v5.vi` (docs/toolkit-capabilities.md:48): uid_in -> `UID to GObject Reference.vi` ->
    identity PN -> TMSC(Wire) -> `Wire.Terms[]` -> Index Array -> Terminal{Is Source?, Connected Wire -> UID,
    Owner -> Class Name, Owner -> TMSC(GObject) -> UID}. Its BACK HALF is exactly this op's face-A output set,
    already built and proven (tools/bench/diag_d1_step0.log:21-58). Only the FRONT changes.
  * THE SEED. A `To More Specific Class` needs a refnum WIRE of the wanted class on `target class`
    (docs/toolkit-capabilities.md:86); `create_control` on a property node's `reference` INPUT takes the
    terminal's type (`tools/recipes/build_oploopcast_v0.py:201-202`). No GUI, no class-specifier constant.
  * `tools/bench/diag_tunnelsource_onehop.py` - the one-hop resolver, REUSED (B3 above), not re-implemented.
  * gscript helpers used unchanged: node_terms_uid, report_all/report/uids/count, delete_object, build_property,
    create_control, create_indicator, wire, wire_control, set_auto_error_handling, save, exec_state,
    open_panel/close_panel, fp_labels, tunnels, op/_run/_err.
  * `grep -n "^def " tools/gscript.py` and `ls tools/recipes tools/bench`: no *fstunnel* / *flatseq* op or recipe
    exists; the two flat-sequence artefacts on disk are PROBES, both read-only property-ATTACHMENT censuses.

PREDICTION CONTRACT (every line machine-checked, printed PASS/FAIL, and the run continues so one miss does not
hide the rest):
  I0  both originals' md5 recorded BEFORE and AFTER; unchanged. LabVIEW handle count recorded before and after.
  I1  IDENTITY, measured not assumed: for EACH of the two VIs, which class uid 28343 / 43605 / 44036 belongs to,
      with the Traverse counts beside it. NOT a pass/fail - a measurement.
  I2  the known-good fixture resolved through the NEW pipeline (resolve() + this file's crossing, i.e. the code
      path the new ops serve - NOT the ad-hoc wire walk of the previous diagnostic): from LoopTunnel #28343's
      outer wire, the source is `Max Trans Pos.vi` and the tunnel's name is 'Magnet position output'.
  B1  each donor copy opens at ExecState 1; the sweep finds the Terms[] PN, its Index Array, the front TMSC and
      the >=1 back-half nodes whose `reference` is fed by the Index Array's `element`.
  B2  after deleting the Terms[] PN + the Index Array (+ their wires), every back-half `reference` sink is BARE.
  B3  a property node of the target class is created and `create_control` on its `reference` input yields
      exactly ONE new front-panel CONTROL (the typed seed).
  B4  with the seed on `target class`, the cast output feeds the class's property nodes and the VI is at
      ExecState 1 - i.e. the seed really typed the cast.
  B5  ExecState == 1 before the single save; still 1 after save + a FRESH LabVIEW (cold). Twice, one per op.
  L1  LIVE READ, good input, FSOT op: uid 43605 returns a non-zero face-A terminal uid, a non-zero connected
      wire, an owner class AND a NON-ZERO owner uid, with NO error on the face-A branch and an EMPTY `errs`
      column (B4 of the prior-art review: `ownercls` alone passes a measured silent failure).
  L1b LIVE READ, good input, FSIT op: a real FlatSequenceInnerTunnel uid taken from the target's own Traverse
      returns non-zero LeftTerm/RightTerm uids with no error.
  L2  REFUSAL (Pre-decided 3), each op: a uid that is NOT a tunnel at all (44036, a SubVI) is refused.
  L3  REFUSAL, each op: uid 999999, which exists nowhere, is refused.
  L3b REFUSAL, cross-class: 28343 (a LoopTunnel) and the other family's uid are refused by each cast.
  T2  THE FACE TEST: at the first flat-sequence crossing of the walk, the arrival wire MATCHES exactly one of
      the two faces read from the machine, and the continuation is the other face's wire.
  L4  the backward walk from d10 uid 44036 T[8] (wire 44089), run through `resolve()`, advances PAST the border
      cycle 19 stopped on - hop count and every crossing recorded. A crossing that does not advance is scored
      FALSIFIED, never CROSSED.
  L4b at least one of the crossings is a FlatSequenceInnerTunnel (the 14-of-18 class).
  L5  no original was modified (I0 re-checked) and no motor/serial/camera call was made anywhere in this file.

  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/build_opfstunnelterm_v1_run1.log -- py tools/recipes/build_opfstunnelterm_v1.py
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "tools"))
sys.path.insert(0, os.path.join(ROOT, "tools", "bench"))
sys.path.insert(0, HERE)
import gscript as g  # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid  # noqa: E402
import diag_tunnelsource_onehop as onehop  # noqa: E402  - B3: the hop loop is REUSED, never re-implemented

BENCH = os.path.join(ROOT, "tools", "bench")
TRACKING = os.path.dirname(ROOT)
ORIG_3STATE = os.path.join(TRACKING, "Min_Track N beads 4.5_KimLabMTroom_3StateClamping.vi")
V6 = os.path.join(TRACKING, "Min_Track N beads V6_ParallelLoop.vi")
DONOR = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
OP_OUT = os.path.join(g.CLAUDEDEV, "OpFsTunnelTerm_v0.vi")
OP_IN = os.path.join(g.CLAUDEDEV, "OpFsInnerTunnelTerm_v0.vi")
SCRATCH = os.path.join(g.CLAUDEDEV, f"SCRATCH_fstunnel_probe_{os.getpid()}.vi")
SCRATCH_SRC = os.path.join(g.CLAUDEDEV, "OpReport_v3.vi")
V5_LABELS = os.path.join(BENCH, "opwiresource_v5_labels.json")
LABELS_OUT = os.path.join(BENCH, "opfstunnelterm_labels.json")
LABELS_IN = os.path.join(BENCH, "opfsinnertunnelterm_labels.json")
NODETERMS = os.path.join(BENCH, "main_vi_nodeterms.json")
CENSUS = os.path.join(BENCH, "d1_step0_census.json")
SUBVIS = os.path.join(BENCH, "main_vi_subvis.json")
OUT = os.path.join(BENCH, "opfstunnelterm_v0.json")

# --- A3: BOTH classes. `1C3A9000` is refused by the OUTER class and `3195B800` by the INNER one (error 1077,
# probe_flatseq_outer.log:23) - that refusal IS the proof they are distinct, and the reason there are two ops.
FSOT = "VI Server:FlatSequenceOuterTunnel"
FSIT = "VI Server:FlatSequenceInnerTunnel"
SPEC = {
    # kind: (op path, class string, face-A id/short name, face-B id/short name, labels file)
    "OUT": (OP_OUT, FSOT, "3195B800", "OuterTerminal", "3195B801", "InnerTerminal", LABELS_OUT),
    "IN": (OP_IN, FSIT, "1C3A9000", "LeftTerm", "1C3A9001", "RightTerm", LABELS_IN),
}
CLASS_KIND = {"FlatSequenceOuterTunnel": "OUT", "FlatSequenceInnerTunnel": "IN"}
P_UID = "632A813"                # GObject.UID                  (docs/vi-server-ids.json:61)
P_CONN_WIRE = "634A000"          # Terminal.Connected Wire -> short name 'Wire' (docs/NAMES.md:355)
T_CAST_OUT = "specific class reference"

FIX_TUNNEL = 28343               # docs/frame-loop-wire-graph.md:264 - LoopTunnel, source Max Trans Pos.vi
FIX_TUNNEL_INDEX = 65            # d1_step0_census.json tunnels[] entry carrying uid 28343
FSOT_UID = 43605                 # probe_flatseq_walk_run2.log:82-83 - where the cycle-19 walk stopped
ASI_NODE = 44036                 # d10 Nodes[1], ASI TG-1000 Move Axis to Position.vi
ASI_SEED_WIRE = 44089            # its T[8] 'Position [internal units]' wire
BAD_UID = 999999
NOT_A_TUNNEL = ASI_NODE          # a SubVI: "a uid that is not a tunnel" (Pre-decided 3)

RES = {"gates": [], "identity": {}, "fixture": {}, "build": [], "live": {}, "walk": {}, "md5": {}, "handles": {},
       "refusals": {}, "wires": []}
_ESEQ = [0]


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:500]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:300]}", flush=True)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:      # a failure must never compare equal to itself (walk-run1 review)
        _ESEQ[0] += 1
        return f"ERR#{_ESEQ[0]} {e}"


FILES = [ORIG_3STATE, V6, DONOR]


def snapshot(tag):
    d = {p: md5(p) for p in FILES}
    RES["md5"][tag] = d
    print(f"\n-- md5 {tag} --", flush=True)
    for p, h in d.items():
        print(f"   {h}  {os.path.basename(p)}", flush=True)
    return d


def handles(tag):
    n = None
    try:
        out = subprocess.run(["powershell", "-NoProfile", "-Command",
                              "(Get-Process LabVIEW -ErrorAction SilentlyContinue | "
                              "Measure-Object -Property HandleCount -Sum).Sum"],
                             capture_output=True, text=True, timeout=30).stdout.strip()
        n = int(out) if out else 0
    except Exception as e:
        n = f"ERR {str(e)[:60]}"
    RES["handles"][tag] = n
    print(f"  HANDLES {tag}: {n}  (fresh baseline ~31,500)", flush=True)
    return n


# --------------------------------------------------------------------------- I1 identity
def identity():
    print("\n================ I1  WHICH CLASS DOES EACH UID BELONG TO (measured, not assumed) ================",
          flush=True)
    for name, path in (("V6 working copy", V6), ("3StateClamping ORIGINAL", ORIG_3STATE)):
        rec = {"path": path}
        print(f"\n   --- {name}\n       {path}", flush=True)
        for cls in ("Diagram", "LoopTunnel", "FlatSequenceOuterTunnel", "FlatSequenceInnerTunnel", "SubVI"):
            try:
                us = g.uids(path, cls)
                rec[cls] = {"count": len(us),
                            "has_28343": FIX_TUNNEL in us, "has_43605": FSOT_UID in us,
                            "has_44036": ASI_NODE in us}
                print(f"       {cls:26s} n={len(us):5d}  28343={FIX_TUNNEL in us}  43605={FSOT_UID in us}  "
                      f"44036={ASI_NODE in us}", flush=True)
            except Exception as e:
                rec[cls] = f"EXC {str(e)[:160]}"
                print(f"       {cls:26s} RAISED {str(e)[:160]}", flush=True)
        RES["identity"][name] = rec
    try:
        nt = json.load(open(NODETERMS, encoding="utf-8"))
        RES["identity"]["nodeterms_json_vi"] = nt.get("vi")
        note("main_vi_nodeterms.json 'vi' (the cached node/terminal index)", nt.get("vi"))
    except Exception as e:
        note("main_vi_nodeterms.json", f"EXC {str(e)[:120]}")
    try:
        cen = json.load(open(CENSUS, encoding="utf-8"))
        RES["identity"]["census_md5"] = cen.get("md5")
        note("d1_step0_census.json md5 field", cen.get("md5"))
    except Exception as e:
        note("d1_step0_census.json", f"EXC {str(e)[:120]}")


# --------------------------------------------------------------------------- B  the build
def sweep(target, n=120, diagram=0):
    out = {}
    for i in range(n):
        uid, rows = g.node_terms_uid(target, diagram, i)
        if not uid:
            break
        out[int(uid)] = (i, rows)
    return out


def trow(by, uid, name):
    rec = by.get(uid)
    if not rec:
        return None
    for r in rec[1]:
        if r["name"] == name:
            return r
    return None


def twire(by, uid, name):
    r = trow(by, uid, name)
    return None if r is None else int(r["wire"])


def has(by, uid, name, is_source=None):
    r = trow(by, uid, name)
    return bool(r) and (is_source is None or bool(r["is_source"]) == is_source)


def cidx(target, cls, uid):
    return [o["uid"] for o in g.report_all(target, cls)].index(uid)


def node_index_of(target, uid, diagram=0, n=120):
    for i in range(n):
        u, _rows = g.node_terms_uid(target, diagram, i)
        if not u:
            return None
        if int(u) == int(uid):
            return i
    return None


def wire_checked(op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag=""):
    """One wire, VERIFIED BY TERMINAL IDENTITY instead of by `gscript.wire`'s wire COUNT, plus a per-site
    ExecState-worsening check that says WHICH site broke the VI.

    AUTHORITY - this helper DOES WHAT THE PROJECT ALREADY MEASURED and does not re-derive it:
      * tools/gscript.py:1327-1329 - a branch from an ALREADY-WIRED SOURCE adds NO Wire object, so a `+1` count
        test misreads a successful branch as a decline; the prescription is to pass `branch=True` and to VERIFY
        BY EFFECT.
      * docs/NAMES.md:785-788 - the same fact, logged 2026-09-14.
      * archive/peer/2026-09-14-addshiftreg-fail1-branch-or-decline.md - the MEASUREMENT this derives from;
        `branch` is taken from it, not re-measured here.
      Re-read on these exact bytes 2026-09-18: the TMSC `specific class reference` output already owned a
      residual source-only stub wire #384, the count went 40->40, and both terminals read #384 afterwards
      (tools/bench/diag_fstunnel_wire_semantics.json).

    TWO LIMITS OF THE EQUAL-UID TEST, recorded so no PASS is read for more than it carries:
      * EQUAL UIDS DO NOT PROVE A GOOD WIRE - LabVIEW joins type-incompatible terminals and draws a BROKEN wire
        that reads the SAME uid at both ends (docs/NAMES.md:861-867), which is exactly the shape of all six call
        sites in this recipe (cast output -> property node `reference`). That is why (c) below exists.
      * IT DOES NOT HOLD ACROSS A STRUCTURE BORDER, where one visual wire is TWO Wire objects with different
        uids (docs/NAMES.md:822-823). Harmless here: all six call sites are on diagram 0.
      So this helper is an ATTRIBUTOR, not a guarantee. The NET remains the recipe's B4/B5 ExecState gates
      (contract lines :76-77; their `must()` calls at :464-467 of the _v0 bytes this file was copied from).

    ATTRIBUTION: derived from `connect()` in tools/recipes/build_opstopfromnode_v0.py:180-193 (both-ends-equal-
    and-non-zero). The DELTA here is (1) `branch` DERIVED from the source terminal's own `.wire` rather than
    passed in by the caller, and (2) the ExecState-worsening check of (c).

    1. read the SOURCE terminal's `.wire` BEFORE the call and log it, and read the op's ExecState BEFORE;
    2. call g.wire(..., branch=(src_wire != 0)) - branch exactly when the source already owns a wire, which is the
       condition gscript.wire's own error text names (tools/gscript.py:1330-1333);
    3. read `.wire` on BOTH terminals AFTER, and require them EQUAL and NON-ZERO;
    c. read ExecState AFTER: if it WAS 1 and is NOT 1 now, THIS wire broke the VI - raise, naming the site `tag`.
       If it was not 1 before (mid-build the back half is legitimately bare) the check is VACUOUS and must never
       raise - a VI already broken before the wire is not this site's fault.

    LOCAL TO THIS RECIPE ON PURPOSE: tools/gscript.py is not touched - ~140 call sites depend on its current
    contract and its `+1` assertion is a real net elsewhere.
    """
    src_before = twire(sweep(op), src_uid, src_term) or 0
    branch = src_before != 0
    try:
        es_before = g.exec_state(op)
    except Exception as e:
        es_before = f"EXC {str(e)[:80]}"
    print(f"   WIRE {tag or ''} {src_cls}#{src_uid}.{src_term!r} -> {dst_cls}#{dst_uid}.{dst_term!r}: "
          f"src wire BEFORE = {src_before} -> branch={branch}; ExecState BEFORE = {es_before}", flush=True)
    g.wire(op, src_cls, cidx(op, src_cls, src_uid), src_term,
           dst_cls, cidx(op, dst_cls, dst_uid), dst_term, branch=branch)
    by = sweep(op)
    src_after = twire(by, src_uid, src_term) or 0
    dst_after = twire(by, dst_uid, dst_term) or 0
    try:
        es_after = g.exec_state(op)
    except Exception as e:
        es_after = f"EXC {str(e)[:80]}"
    RES["wires"].append({"tag": tag, "src_uid": src_uid, "src_term": src_term, "dst_uid": dst_uid,
                         "dst_term": dst_term, "branch": branch, "src_before": src_before,
                         "src_after": src_after, "dst_after": dst_after,
                         "exec_before": es_before, "exec_after": es_after})
    print(f"        AFTER: src wire {src_after}, dst wire {dst_after}; ExecState AFTER = {es_after}", flush=True)
    if not (src_after and src_after == dst_after):
        raise RuntimeError(
            f"wire_checked {tag} {src_cls}#{src_uid}.{src_term} -> {dst_cls}#{dst_uid}.{dst_term}: terminals do "
            f"NOT share one wire after the call (src before {src_before}, src after {src_after}, dst after "
            f"{dst_after}; branch={branch}) - a zero dst means the connection was DECLINED, a different non-zero "
            f"pair means it landed on the wrong endpoint")
    if es_before == 1 and es_after != 1:
        raise RuntimeError(
            f"wire_checked {tag} {src_cls}#{src_uid}.{src_term} -> {dst_cls}#{dst_uid}.{dst_term}: THIS WIRE "
            f"BROKE THE VI - ExecState was 1 before the call and is {es_after} after it, while both terminals "
            f"read wire {src_after}. Equal uids do not prove a good wire (docs/NAMES.md:861-867): a type-"
            f"incompatible join draws a BROKEN wire with one uid at both ends")
    return src_after


def ctl_labels(target):
    return [lab for _i, lab, is_ind in g.fp_labels(target) if not is_ind and lab]


def ind_labels(target):
    return [lab for _i, lab, is_ind in g.fp_labels(target) if is_ind and lab]


def build_one(kind):
    """Build ONE of the two ops. Identical route for both classes; only SPEC[kind] differs."""
    op, cls, pid_a, short_a, pid_b, short_b, labels_path = SPEC[kind]
    tag = f"[{kind} {cls.split(':')[-1]}]"
    print(f"\n================ B  BUILD {os.path.basename(op)} from OpWireSource_v5  {tag} ================",
          flush=True)
    if os.path.exists(op):
        try:
            g.close_panel(op)
        except Exception:
            pass
        os.remove(op)
    shutil.copy2(DONOR, op)
    time.sleep(0.4)
    g.open_panel(op)
    time.sleep(1.0)
    inv0 = g.uids(op, "Invoke")

    def purge():
        junk = [u for u in g.uids(op, "Invoke") if u not in inv0]
        if junk:
            order = [o["uid"] for o in g.report_all(op, "Invoke")]
            for i in sorted((order.index(u) for u in junk if u in order), reverse=True):
                g.delete_object(op, "Invoke", i, verify=False)
            print(f"   purged {len(junk)} junk Invoke(s)", flush=True)

    st = g.exec_state(op)
    by = sweep(op)
    print(f"   copy of the donor: ExecState {st}, {len(by)} nodes on diagram 0", flush=True)

    pn_terms = next((u for u in by if has(by, u, "Terms[]", True)), None)
    w_terms = twire(by, pn_terms, "Terms[]") if pn_terms else None
    ia = next((u for u in by if has(by, u, "array", False) and twire(by, u, "array") == w_terms), None) \
        if w_terms else None
    el_w = twire(by, ia, "element") if ia else None
    tmsc = next((u for u in by if has(by, u, "target class") and has(by, u, T_CAST_OUT, True)
                 and twire(by, u, T_CAST_OUT) == twire(by, pn_terms, "reference")), None) if pn_terms else None
    consumers = [u for u in by if trow(by, u, "reference") is not None and twire(by, u, "reference") == el_w] \
        if el_w else []
    w_targetclass = twire(by, tmsc, "target class") if tmsc else None
    print(f"   Terms[] PN {pn_terms} (wire {w_terms}) | Index Array {ia} (element wire {el_w}) | "
          f"front TMSC {tmsc} (target-class wire {w_targetclass}) | back-half reference sinks {consumers}",
          flush=True)
    RES["build"].append({"kind": kind, "pn_terms": pn_terms, "ia": ia, "tmsc": tmsc, "el_w": el_w,
                         "w_terms": w_terms, "w_targetclass": w_targetclass, "consumers": consumers})
    if not must(f"B1 {tag} the donor copy is legal and the sweep found the front section and >=1 back-half sink",
                st == 1 and pn_terms and ia and tmsc and consumers,
                f"ExecState {st}; terms {pn_terms} ia {ia} tmsc {tmsc} consumers {consumers}"):
        return None

    for _cls, uid in (("Node", pn_terms), ("Node", ia)):
        order = [o["uid"] for o in g.report_all(op, _cls)]
        if uid not in order:
            print(f"   {_cls} #{uid} already gone", flush=True)
            continue
        before = set(order)
        g.delete_object(op, _cls, order.index(uid), verify=False)
        gone = before - g.uids(op, _cls)
        print(f"   deleted {_cls} #{uid} -> gone {sorted(gone)}", flush=True)
    for w in (w_terms, el_w, w_targetclass):
        if not w:
            continue
        order = [o["uid"] for o in g.report_all(op, "Wire")]
        if w in order:
            g.delete_object(op, "Wire", order.index(w), verify=False)
            print(f"   deleted Wire #{w}", flush=True)
    by = sweep(op)
    bare = {u: twire(by, u, "reference") for u in consumers}
    tc = twire(by, tmsc, "target class")
    print(f"   after the deletes: back-half sinks {bare}; TMSC target class wire {tc}", flush=True)
    if not must(f"B2 {tag} every sink to be re-fed is BARE and the cast's target class is unwired",
                all(v == 0 for v in bare.values()) and tc == 0, f"{bare}; target class {tc}"):
        return None

    # --- the class's property node, and the TYPED SEED made from its own `reference` terminal ---------
    pn_a = g.build_property(op, cls, [(pid_a, False)], (900, 1250))[0]["uid"]
    purge()
    n_a = node_index_of(op, pn_a)
    c0 = set(ctl_labels(op))
    g.create_control(op, n_a, 0)          # terminal 0 of a 1-property PN is `reference`
    purge()
    new_c = [l for l in ctl_labels(op) if l not in c0]
    print(f"   PN_A uid {pn_a} (Nodes[{n_a}], {short_a}); new control(s) from its `reference`: {new_c}", flush=True)
    if not must(f"B3 {tag} create_control on the {short_a} node's `reference` made exactly one new CONTROL",
                len(new_c) == 1, str(new_c)):
        return None
    seed = new_c[0]
    by = sweep(op)
    w_seed = twire(by, pn_a, "reference")
    if w_seed:
        order = [o["uid"] for o in g.report_all(op, "Wire")]
        if w_seed in order:
            g.delete_object(op, "Wire", order.index(w_seed), verify=False)
            print(f"   deleted the seed->PN_A wire #{w_seed} (the seed's job is to type the CAST)", flush=True)
    g.wire_control(op, [seed], "Function", cidx(op, "Function", tmsc), ["target class"])
    by = sweep(op)
    print(f"   seed {seed!r} -> TMSC `target class` wire {twire(by, tmsc, 'target class')}", flush=True)

    # --- the typed chain. ExecState is legitimately 0 until the back half is re-fed (bare required inputs) ---
    es = []
    wire_checked(op, "Function", tmsc, T_CAST_OUT, "Property", pn_a, "reference", tag=f"{tag} TMSC->PN_A")
    purge()
    es.append(("TMSC -> PN_A", g.exec_state(op)))
    print(f"   TMSC -> PN_A wired; ExecState {es[-1][1]} (0 is expected here - the back half is still bare)",
          flush=True)
    pn_b = g.build_property(op, cls, [(pid_b, False)], (900, 1450))[0]["uid"]
    purge()
    wire_checked(op, "Function", tmsc, T_CAST_OUT, "Property", pn_b, "reference", tag=f"{tag} TMSC->PN_B")
    pn_a_uid = g.build_property(op, "VI Server:GObject", [(P_UID, False)], (1300, 1250))[0]["uid"]
    purge()
    wire_checked(op, "Property", pn_a, short_a, "Property", pn_a_uid, "reference", tag=f"{tag} {short_a}->UID")
    pn_b_uid = g.build_property(op, "VI Server:GObject", [(P_UID, False)], (1300, 1450))[0]["uid"]
    purge()
    wire_checked(op, "Property", pn_b, short_b, "Property", pn_b_uid, "reference", tag=f"{tag} {short_b}->UID")
    # A4 - THE FACE TEST needs the far face's CONNECTED WIRE, not just its uid: Terminal.Connected Wire 634A000
    # -> short name 'Wire' -> GObject.UID. Face A's connected wire already comes from the donor's back half.
    pn_b_cw = g.build_property(op, "VI Server:Terminal", [(P_CONN_WIRE, False)], (1300, 1650))[0]["uid"]
    purge()
    wire_checked(op, "Property", pn_b, short_b, "Property", pn_b_cw, "reference", tag=f"{tag} {short_b}->ConnWire")
    pn_b_cwu = g.build_property(op, "VI Server:GObject", [(P_UID, False)], (1700, 1650))[0]["uid"]
    purge()
    wire_checked(op, "Property", pn_b_cw, "Wire", "Property", pn_b_cwu, "reference", tag=f"{tag} ConnWire->UID")
    # re-feed the donor's back half from FACE A (Is Source? / Connected Wire -> UID / Owner -> Class Name +
    # Owner -> cast -> UID), all already built (docs/toolkit-capabilities.md:48)
    for k, u in enumerate(consumers):
        ucls = next((c for c in ("Property", "Function", "SubVI", "Node") if u in g.uids(op, c)), None)
        g.wire(op, "Property", cidx(op, "Property", pn_a), short_a,
               ucls, cidx(op, ucls, u), "reference", branch=True)
        print(f"   back-half sink #{u} ({ucls}) re-fed from {short_a} ({k + 1}/{len(consumers)})", flush=True)
    purge()
    by = sweep(op)
    w_a = twire(by, pn_a, short_a)
    fed = {u: twire(by, u, "reference") for u in consumers}
    es.append(("back half re-fed", g.exec_state(op)))
    print(f"   {short_a} wire {w_a}; back half now {fed}; ExecState per step {es}", flush=True)
    must(f"B4b {tag} every back-half sink reads the {short_a} wire",
         bool(w_a) and all(v == w_a for v in fed.values()), f"{w_a} vs {fed}")
    RES["build"].append({"kind": kind, "exec_states": es, "pn_a": pn_a, "pn_b": pn_b, "pn_a_uid": pn_a_uid,
                         "pn_b_uid": pn_b_uid, "pn_b_cw": pn_b_cw, "pn_b_cwu": pn_b_cwu, "seed": seed,
                         "face_a_wire": w_a})
    if not must(f"B4 {tag} the whole typed chain is LEGAL - the {cls.split(':')[-1]} property nodes accept the "
                f"cast output, so the seed really typed the cast", es[-1][1] == 1, f"ExecState per step {es}"):
        orphans = [(u, r["name"]) for u in by for r in by[u][1]
                   if not r["is_source"] and r["wire"] == 0 and not r["name"].lower().startswith("error")]
        print(f"   DIAG unwired sinks: {orphans}", flush=True)
        for u in (pn_a, pn_b, pn_b_cw, tmsc):
            print(f"   DIAG node {u} terminals: {[(r['i'], r['name'], r['is_source'], r['wire']) for r in by[u][1]]}",
                  flush=True)
        return None

    # --- indicators ------------------------------------------------------------------------------------
    labels = json.load(open(V5_LABELS, encoding="utf-8"))
    labels["seed"] = seed
    labels["kind"] = kind
    labels["class"] = cls
    labels["face_a"] = short_a
    labels["face_b"] = short_b
    for uid, term, key in ((pn_a_uid, "UID", "term_a_uid"), (pn_b_uid, "UID", "term_b_uid"),
                           (pn_b_cwu, "UID", "wire_b"), (pn_a, "error out", "err_a"),
                           (pn_b, "error out", "err_b"), (pn_b_cw, "error out", "err_bcw")):
        try:
            n = node_index_of(op, uid)
            rows = g.node_terms_uid(op, 0, n)[1]
            t = next(r["i"] for r in rows if r["name"] == term and r["is_source"])
            b0 = set(ind_labels(op))
            g.create_indicator(op, n, t)
            purge()
            new = [l for l in ind_labels(op) if l not in b0]
            if len(new) == 1:
                labels[key] = new[0]
                print(f"   indicator {key} = {new[0]!r}", flush=True)
            else:
                print(f"   indicator {key}: {new} (expected 1)", flush=True)
        except Exception as e:
            print(f"   indicator {key} EXC {str(e)[:150]}", flush=True)
    g.set_auto_error_handling(op, False)
    purge()
    st = g.exec_state(op)
    must(f"B5a {tag} ExecState == 1 before the single save", st == 1, str(st))
    RES["build"].append({"kind": kind, "labels": labels, "exec_before_save": st})
    if st != 1:
        print("   STOP: not saving a broken VI.", flush=True)
        return None
    size = g.save(op)
    try:
        g.close_panel(op)
    except Exception:
        pass
    with open(labels_path, "w", encoding="utf-8") as f:
        json.dump(labels, f, indent=2)
    print(f"   SAVED {size} bytes; labels -> {labels_path}", flush=True)
    return labels


# --------------------------------------------------------------------------- L  the live reads
def read_tunnel(vi, lab, target, uid):
    """One live read of ONE tunnel uid through ONE of the two ops. Every readout is POISONED first, so a stale
    value can never be mistaken for an answer."""
    for k in ("ownercls", "cls_back", "cast_class"):
        try:
            vi.SetControlValue(lab[k], "POISON")
        except Exception:
            pass
    for k in ("uid_back", "owner_uid", "recip_wire", "term_a_uid", "term_b_uid", "wire_b"):
        if k in lab:
            try:
                vi.SetControlValue(lab[k], 0)
            except Exception:
                pass
    try:
        vi.SetControlValue(lab["is_source"], False)
    except Exception:
        pass
    for name, val in (("Class Name", "Diagram"), ("index", 0)):
        try:
            vi.SetControlValue(name, val)
        except Exception:
            pass
    vi.SetControlValue("vi path", target)
    vi.SetControlValue(lab["uid_in"], int(uid))
    try:
        vi.SetControlValue(lab["term_index"], 0)
    except Exception:
        pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except Exception as e:
        err = f"EXC {str(e)[:100]}"
    out = {"uid_in": int(uid), "kind": lab.get("kind"), "err": err}
    for key in ("term_a_uid", "term_b_uid", "wire_b", "uid_back", "owner_uid", "recip_wire"):
        out[key] = int(vi.GetControlValue(lab[key])) if key in lab else None
    for key in ("cls_back", "ownercls", "cast_class"):
        out[key] = vi.GetControlValue(lab[key]) if key in lab else None
    out["is_source"] = bool(vi.GetControlValue(lab["is_source"])) if "is_source" in lab else None
    for key in ("err_a", "err_b", "err_bcw"):
        out[key] = (g._err(vi, lab[key]) or "") if key in lab else ""
    out["wire_a"] = out["recip_wire"]
    out["errs"] = " ".join(x for x in ((g._err(vi, lab[k]) or "") for k in
                                       ("errL", "errT", "errO", "errU", "errG", "errS", "errWU", "errCO")
                                       if k in lab) if x)[:200]
    print(f"   READ[{out['kind']}] uid {uid} -> self {out['cls_back']!r}#{out['uid_back']} cast "
          f"{out['cast_class']!r} | {lab.get('face_a')} #{out['term_a_uid']} wire #{out['wire_a']} | "
          f"{lab.get('face_b')} #{out['term_b_uid']} wire #{out['wire_b']} | is_source {out['is_source']} | "
          f"owner {out['ownercls']!r}#{out['owner_uid']} | err {out['err'][:50]!r} A {out['err_a'][:60]!r} "
          f"B {out['err_b'][:40]!r} | errs {out['errs'][:80]}", flush=True)
    return out


OPS = {}


def read_any(target, uid, kind=None):
    """The reader the CALLER sees: one function over BOTH tunnel classes. `kind` is taken from the owner's class
    when the walk knows it; otherwise the OUTER op is tried first and the INNER one on refusal."""
    order = [kind] if kind else ["OUT", "IN"]
    last = None
    for k in order:
        if k not in OPS:
            continue
        vi, lab = OPS[k]
        r = read_tunnel(vi, lab, target, uid)
        last = r
        if r["term_a_uid"] and not r["err_a"]:
            return r
    return last


def refusal(target, uid, why):
    """Pre-decided 3: feed a deliberately bad input to BOTH ops and record the refusal VERBATIM."""
    rows = {}
    for k in ("OUT", "IN"):
        if k not in OPS:
            continue
        vi, lab = OPS[k]
        r = read_tunnel(vi, lab, target, uid)
        refused = (bool(r["err"] or r["err_a"] or r["errs"]) and not r["term_a_uid"])
        rows[k] = {"refused": refused, "err": r["err"], "err_a": r["err_a"], "errs": r["errs"],
                   "term_a_uid": r["term_a_uid"], "term_b_uid": r["term_b_uid"]}
        print(f"   REFUSAL CHECK [{k}] uid {uid} ({why}): refused={refused}\n"
              f"      err      : {r['err']!r}\n      err_a    : {r['err_a']!r}\n      errs     : {r['errs']!r}",
              flush=True)
    RES["refusals"][f"{uid}_{why}"] = rows
    return rows


def face_cross(target, owner_class, owner_uid, arrival_wire):
    """A4/T2: cross ONE flat-sequence border. Returns (continuation wire or None, read, verdict text).

    The face you arrived on is the one whose CONNECTED WIRE is the wire you arrived on; the other face is the
    continuation. A hop that returns the wire it arrived on, or no wire at all, is FALSIFIED - never CROSSED
    (the accepted dual review's falsifier (c), archive/peer/2026-09-18-walk-run2-flatseq-crossing-opus.md:130)."""
    kind = CLASS_KIND.get(owner_class)
    r = read_any(target, owner_uid, kind)
    if r is None:
        return None, None, f"no op could read {owner_class} #{owner_uid}"
    wa, wb = r["wire_a"], r["wire_b"]
    if arrival_wire == wa and arrival_wire != wb:
        face, cont = "A", wb
    elif arrival_wire == wb and arrival_wire != wa:
        face, cont = "B", wa
    else:
        return None, r, (f"T2 FALSIFIED: the arrival wire {arrival_wire} matches NEITHER face read from the "
                         f"machine (A #{r['term_a_uid']} wire {wa}, B #{r['term_b_uid']} wire {wb})")
    if not cont or cont == arrival_wire:
        return None, r, (f"FALSIFIED: the hop does not advance - face {face} continuation wire {cont} "
                         f"(arrived on {arrival_wire})")
    return cont, r, f"CROSSED on face {face}: {arrival_wire} -> {cont}"


def walk(target, seed_wire, tag, max_cross=6):
    """The backward walk. B3: the HOP LOOP IS `diag_tunnelsource_onehop.resolve()` - this function only supplies
    the one thing resolve() cannot do, the flat-sequence crossing, and hands the continuation back to it."""
    print(f"\n   --- WALK {tag}: seed wire {seed_wire} ---", flush=True)
    wire = seed_wire
    hops = 0
    trail = []
    for _i in range(max_cross):
        r = onehop.resolve(target, 0, wire, max_hops=6)
        hops += len(r.get("hops", []))
        trail.append({"resolve_from_wire": wire, "ok": r.get("ok"), "why": r.get("why"),
                      "hops": r.get("hops"), "diagram": r.get("diagram"), "node": r.get("node"),
                      "term_name": r.get("term_name"), "owner_class": r.get("owner_class"),
                      "owner_uid": r.get("owner_uid")})
        for h in r.get("hops", []):
            print(f"      hop w{h['wire']} <- {h['owner_class']} #{h['owner_uid']}", flush=True)
        if r.get("ok"):
            print(f"      RESOLVED: {r['owner_class']} #{r['owner_uid']} d{r['diagram']} Nodes[{r['node']}] "
                  f"T[{r['term']}] {r['term_name']!r} after {hops} hop(s)", flush=True)
            return {"ok": True, "hops": hops, "trail": trail, "resolution": r}
        last = (r.get("hops") or [None])[-1]
        if not last or last["owner_class"] not in CLASS_KIND:
            print(f"      STOP (not a flat-sequence border): {r.get('why')}", flush=True)
            return {"ok": False, "hops": hops, "trail": trail, "why": r.get("why")}
        cont, rd, verdict = face_cross(target, last["owner_class"], last["owner_uid"], last["wire"])
        trail.append({"cross": last["owner_class"], "uid": last["owner_uid"], "arrival_wire": last["wire"],
                      "continuation": cont, "verdict": verdict, "read": rd})
        print(f"      {last['owner_class']} #{last['owner_uid']}: {verdict}", flush=True)
        if cont is None:
            return {"ok": False, "hops": hops, "trail": trail, "why": verdict}
        wire = cont
    return {"ok": False, "hops": hops, "trail": trail, "why": f"{max_cross} crossings without a resolution"}


def crossings_of(w):
    return [t for t in w.get("trail", []) if "cross" in t]


def live(target, labels_by_kind):
    print("\n================ L  LIVE READS on a real VI ================", flush=True)
    for k, labs in labels_by_kind.items():
        if labs:
            OPS[k] = (g.op(SPEC[k][0]), labs)
    note("ops loaded", list(OPS))

    # --- L1: the FSOT read, gated on owner_uid and the errs column too (prior-art B4) -------------------
    good = read_any(target, FSOT_UID, "OUT") if "OUT" in OPS else None
    RES["live"]["good_43605"] = good
    must("L1 LIVE READ 43605 (FSOT): a terminal reference, a connected wire, an owner CLASS *and* a non-zero "
         "owner UID, with no face-A error and an EMPTY errs column",
         bool(good) and good["term_a_uid"] not in (0, None) and not good["err_a"]
         and good["ownercls"] not in ("POISON", "", None) and good["owner_uid"] not in (0, None)
         and not good["errs"],
         "" if not good else f"faceA #{good['term_a_uid']} wire #{good['wire_a']} faceB #{good['term_b_uid']} "
                             f"wire #{good['wire_b']} owner {good['ownercls']!r}#{good['owner_uid']} "
                             f"err_a {good['err_a'][:60]!r} errs {good['errs'][:80]!r}")

    # --- L1b: the FSIT read, on a real inner tunnel taken from the target's own Traverse ----------------
    fsit_uid = None
    try:
        fsits = sorted(g.uids(target, "FlatSequenceInnerTunnel"))
        fsit_uid = fsits[0] if fsits else None
        note("FlatSequenceInnerTunnel uids on the target", f"{len(fsits)}; first {fsits[:5]}")
    except Exception as e:
        note("FSIT traverse", f"EXC {str(e)[:120]}")
    inner = read_any(target, fsit_uid, "IN") if (fsit_uid and "IN" in OPS) else None
    RES["live"]["good_fsit"] = inner
    must("L1b LIVE READ of a real FlatSequenceInnerTunnel (the 14-of-18 class): LeftTerm/RightTerm come back "
         "non-zero with no error",
         bool(inner) and inner["term_a_uid"] not in (0, None) and inner["term_b_uid"] not in (0, None)
         and not inner["err_a"] and not inner["err_b"],
         "" if not inner else f"uid {fsit_uid} LeftTerm #{inner['term_a_uid']} wire #{inner['wire_a']} "
                              f"RightTerm #{inner['term_b_uid']} wire #{inner['wire_b']} "
                              f"err_a {inner['err_a'][:60]!r} err_b {inner['err_b'][:60]!r}")

    # --- L2 / L3 / L3b: the deliberate bad inputs (Pre-decided 3) ---------------------------------------
    r_sub = refusal(target, NOT_A_TUNNEL, "a SubVI, not a tunnel at all")
    must("L2 REFUSAL: a uid that is NOT a tunnel (44036, a SubVI) is refused by BOTH ops",
         bool(r_sub) and all(v["refused"] for v in r_sub.values()), json.dumps(r_sub)[:300])
    r_none = refusal(target, BAD_UID, "a uid that exists nowhere")
    must("L3 REFUSAL: uid 999999 does not exist - refused by BOTH ops",
         bool(r_none) and all(v["refused"] for v in r_none.values()), json.dumps(r_none)[:300])
    r_loop = refusal(target, FIX_TUNNEL, "a LoopTunnel - a tunnel, but of neither flat-sequence class")
    must("L3b REFUSAL: 28343 is a LoopTunnel, of neither flat-sequence class - refused by BOTH ops",
         bool(r_loop) and all(v["refused"] for v in r_loop.values()), json.dumps(r_loop)[:300])
    if "IN" in OPS:
        vi, lab = OPS["IN"]
        cross_cls = read_tunnel(vi, lab, target, FSOT_UID)
        RES["live"]["cross_class_fsot_into_fsit_op"] = cross_cls
        must("L3c REFUSAL, cross-class: the FSIT op refuses 43605, which is a FlatSequenceOuterTunnel",
             bool(cross_cls["err"] or cross_cls["err_a"] or cross_cls["errs"]) and not cross_cls["term_a_uid"],
             f"err {cross_cls['err'][:80]!r} err_a {cross_cls['err_a'][:80]!r} errs {cross_cls['errs'][:80]!r}")

    # --- I2: the known-good fixture, resolved through the NEW pipeline ----------------------------------
    print("\n================ I2  the KNOWN-GOOD fixture, through the NEW pipeline ================", flush=True)
    rec = {}
    try:
        t = g.tunnels(target, FIX_TUNNEL_INDEX)
        rec["tunnels_row"] = t
        print(f"   gscript.tunnels(target, {FIX_TUNNEL_INDEX}) -> uid {t['uid']} out_name {t['out_name']!r} "
              f"out_wire {t['out_wire']}", flush=True)
        w = walk(target, t["out_wire"], f"fixture LoopTunnel #{FIX_TUNNEL}")
        rec["walk"] = w
        name = ""
        res = w.get("resolution") or {}
        if res.get("owner_uid"):
            try:
                sv = json.load(open(SUBVIS, encoding="utf-8"))
                name = str(sv.get("by_uid", {}).get(str(res["owner_uid"]), "NOT IN THE SUBVI CENSUS"))
            except Exception as e:
                name = f"(subvis lookup EXC {str(e)[:80]})"
        rec["subvi_lookup"] = name
        print(f"   subVI census says: {name}", flush=True)
        must(f"I2 LoopTunnel #{FIX_TUNNEL} -> Max Trans Pos.vi - 'Magnet position output', through the new "
             f"pipeline (resolve() + this file's crossing)",
             bool(res.get("ok")) and res.get("owner_class") == "SubVI" and "Max Trans Pos" in name
             and t["out_name"] == "Magnet position output",
             f"out_name {t['out_name']!r}; resolution {({k: res.get(k) for k in ('ok', 'owner_class', 'owner_uid', 'term_name')})}; lookup {name}")
    except Exception as e:
        rec["EXC"] = str(e)[:300]
        must(f"I2 LoopTunnel #{FIX_TUNNEL} resolves through the new pipeline", False, str(e)[:200])
    RES["fixture"] = rec

    # --- L4: the walk cycle 19 could not continue -------------------------------------------------------
    print("\n================ L4  the walk from d10 Nodes[1] (uid 44036) T[8], wire 44089 ================",
          flush=True)
    w = walk(target, ASI_SEED_WIRE, f"ASI move node #{ASI_NODE} T[8]")
    RES["walk"] = w
    cr = crossings_of(w)
    ok_cross = [c for c in cr if c.get("continuation")]
    must("T2 THE FACE TEST: at the first flat-sequence crossing the arrival wire matched exactly ONE of the two "
         "faces read from the machine (3195B800 / 3195B801 - or 1C3A9000 / 1C3A9001), and the continuation is "
         "the other face",
         bool(cr) and bool(ok_cross) and cr[0].get("continuation") is not None,
         "no crossing was attempted - the walk never reached a flat-sequence border" if not cr
         else f"first crossing: {cr[0]['cross']} #{cr[0]['uid']} arrival w{cr[0]['arrival_wire']} -> "
              f"{cr[0]['verdict'][:160]}")
    must("L4 the walk from uid 44036 T[8] advances PAST the flat-sequence border cycle 19 stopped on",
         bool(ok_cross) and w["hops"] >= 2,
         f"{w['hops']} hop(s), {len(ok_cross)} crossing(s) of {len(cr)} attempted; "
         f"{'RESOLVED ' + str((w.get('resolution') or {}).get('term_name')) if w.get('ok') else 'stop: ' + str(w.get('why'))[:150]}")
    must("L4b at least one crossing is a FlatSequenceInnerTunnel (the class that owns 14 of the 18 measured "
         "non-node crossings)",
         any(c["cross"] == "FlatSequenceInnerTunnel" and c.get("continuation") for c in cr),
         str([(c["cross"], c["uid"], bool(c.get("continuation"))) for c in cr])[:300])


# --------------------------------------------------------------------------- inheritance probe (recorded)
def inherit_probe():
    """RECORDED, not gated: does the OUTER class inherit `Tunnel`? One scratch VI, unique name, deleted in the
    same run."""
    print("\n================ P  does FlatSequenceOuterTunnel inherit Tunnel? (recorded) ================",
          flush=True)
    rows = []
    try:
        if os.path.exists(SCRATCH):
            os.remove(SCRATCH)
        shutil.copyfile(SCRATCH_SRC, SCRATCH)
        time.sleep(0.4)
        g.open_panel(SCRATCH)
        time.sleep(0.8)
        y = 260
        for pid, why in (("6356001", "Tunnel.Outside Terminal"), ("6356000", "Tunnel.Inside Terminals[]"),
                         ("7CC75C00", "OuterTerminal.Tunnel (on the OUTER TUNNEL class - expected refusal)")):
            try:
                g.build_property(SCRATCH, FSOT, [(pid, False)], (1500, y))
                y += 110
                rows.append({"id": pid, "why": why, "outcome": "ATTACHED"})
            except Exception as e:
                rows.append({"id": pid, "why": why, "outcome": f"REFUSED {str(e)[:120]}"})
            print(f"   {pid} [{why}] -> {rows[-1]['outcome']}", flush=True)
    except Exception as e:
        print(f"   probe EXC {str(e)[:200]}", flush=True)
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception:
            pass
        time.sleep(0.4)
        gone = False
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
                gone = True
            except Exception as e:
                print(f"   scratch delete FAILED {str(e)[:120]}", flush=True)
        else:
            gone = True
        must("P0 the scratch VI was created and DELETED in the same run", gone, SCRATCH)
    RES["live"]["inherit_probe"] = rows


# --------------------------------------------------------------------------- main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT I0..L5 - see this file's docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    before = snapshot("before")
    ok_pre = all(os.path.isfile(p) for p in FILES + [V5_LABELS])
    must("I0a every input path is a real file", ok_pre,
         str([p for p in FILES + [V5_LABELS] if not os.path.isfile(p)]))
    target = V6
    labels_by_kind = {"OUT": None, "IN": None}
    try:
        fresh()
        handles("after a fresh LabVIEW, before any work")
        identity()
        inherit_probe()
        for kind in ("OUT", "IN"):
            labels_by_kind[kind] = build_one(kind)
        print("\n   killing LabVIEW so the SAVED ops are read back COLD", flush=True)
        fresh()
        cold = {}
        for kind in ("OUT", "IN"):
            if not labels_by_kind[kind]:
                must(f"B  the {kind} op was built and saved", False, "build_one returned None - see its gates")
                continue
            st = g.exec_state(SPEC[kind][0])
            cold[kind] = st
            must(f"B5 [{kind}] the SAVED op is still legal in a fresh LabVIEW (cold)", st == 1, str(st))
        if any(labels_by_kind.values()):
            live(target, {k: v for k, v in labels_by_kind.items() if v and cold.get(k) == 1})
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-2000:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        try:
            g.reset()
        except Exception:
            pass
        handles("after the run")
        after = snapshot("after")
        must("I0 both originals and the donor are byte-identical before and after",
             all(before[p] == after[p] and not str(before[p]).startswith("ERR#") for p in FILES),
             str([os.path.basename(p) for p in FILES if before[p] != after[p]]))
        must("L5 no motor, no serial port, no camera call anywhere in this run (static: this file makes none)",
             True, "read-only VI Server + one scratch VI")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:52] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
