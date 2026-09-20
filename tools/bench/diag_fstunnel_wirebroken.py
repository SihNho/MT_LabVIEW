r"""diag_fstunnel_wirebroken.py - READ `Wire.Is Broken?` 6371004 ON THE SIX WIRE SITES OF
build_opfstunnelterm_v1.py AT THE B4 POINT, plus on the residual stub wire #384.

STATUS.md `## NEXT` cycle 23 dispatch 1. This is a DIAGNOSTIC, not a recipe build: it lives under tools/bench,
it saves nothing, and it never writes to tools/recipes/build_opfstunnelterm_v1.py (STATUS: ANY edit to `_v1.py`
BRICKS its launch path - `stop_record._check:325`). `_v1.py` is IMPORTED, never patched.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "before creating any new op"):
  * `Wire.Is Broken?` 6371004 IS BUILT (docs/NAMES.md:888-897). Its only carrier reachable from Python is
    `OpConnectFromWire_v0.vi` - its readout is a Property node that reads `Terminal.Connected Wire` off the SINK
    terminal reference and then that wire's `UID`+`Broken?`, surfaced as `UID 2` / `Is Broken?`, and ORDERED after
    the Invoke by gate W7b (`build_opconnectfromwire_v0.py:269-281`). Consequence, stated plainly: the reader can
    only be made to run by a SUCCESSFUL `Terminal.Connect Wire`, so the call below re-connects THE SAME
    source->sink pair the wire already has (the minimum possible perturbation) and the row is only accepted when
    the op's own `UID 2` equals the wire that was asked about. NO NEW OP IS BUILT.
  * wrappers `connect_from_wire()` / `wire_source_owner()` COPIED from build_opconnectfromwire_v0.py:381-447
    (a control-setting wrapper only) so this file does not import that recipe's chain
    (build_opconnectnested_v1 + bench_prep). Behaviour unchanged; label map read from
    tools/bench/opconnectfromwire_v0_labels.json, not re-derived.
  * `OpWireSource_v5.vi` + tools/bench/opwiresource_v5_labels.json - FULLY READ-ONLY per-terminal reader. Gives
    the independent brokenness indicator docs/NAMES.md:900-905 records: TWO terminals on one wire both reporting
    `Terminal.Is Source?` TRUE = the wire is broken.
  * `gscript.remove_bad_wires_scripted` - LabVIEW's OWN verdict on which wires are bad, read as a SET DIFFERENCE
    of Wire uids (NOT the uid-equality test §11u.1 refutes). Run on a SECOND, separate B4 scratch so it cannot
    perturb the primary reads.
  * `tools/hooks/guard_cycle.py` `newest_retrospective()` / `newest_build_log()` - the gate's own functions,
    imported and called instead of re-implementing the comparison.
  * `grep -n "^def " tools/gscript.py`: gscript has NO brokenness reader; `ls tools/recipes tools/bench`: no
    *wirebroken* / *isbroken* diagnostic exists. Nothing here is a second implementation of anything.

REPRODUCTION ROUTE (the measurement is worthless if this diverges - cycle-23 brief):
  `build_opfstunnelterm_v1.build_one(kind)` is CALLED, unmodified, with exactly two module-level patches:
    (1) SPEC[kind][0] -> a unique scratch path under user.lib\claudeDev (so nothing is written to the released
        op paths OpFsTunnelTerm_v0.vi / OpFsInnerTunnelTerm_v0.vi), and
    (2) `must` wrapped so the B4 gate RAISES `StopAtB4` instead of returning - which freezes the VI at exactly
        the B4 point (the `RES["build"]` append and the B4b gate happen BEFORE it, so the back-half re-feed is
        already done, and `create_indicator`/`set_auto_error_handling`/`save` never run).
  NOT run, and why it cannot affect the donor copy's diagram: `identity()` (Traverse counts on the ORIGINAL and
  the V6 copy - deliberately skipped so no original is opened at all) and `inherit_probe()` (its own scratch).

PREDICTION CONTRACT (every line printed PASS/FAIL; one miss never hides the rest):
  P1  the reproduction matches run 1 (tools/bench/build_opfstunnelterm_v1_run1.log:45-75) object for object:
      B1 finds terms 145 / ia 151 / tmsc 1044 / consumers [157,1319,1326], and the six sites land on wires
      384, 384, 1694, 1719, 1719, 1766.
  P2  ExecState at the B4 point == 0 (run 1 line 75).
  P3  for each of the six sites, ONE row: wire uid -> `Is Broken?` true/false, or could-not-read WITH the reason.
      A row counts only if the op's `UID 2` == the wire asked about.
  P4  #384 exists in the Wire census at the B4 point, and its row is reported (run 1 :57 says it is the wire
      sites 1 and 2 share, so it is not a separate seventh object - that is itself the measurement).
  P5  the read-only cross-check per wire: `OpWireSource_v5` terminal list, with the count of terminals reporting
      `Is Source?` TRUE (>=2 = broken, docs/NAMES.md:900).
  P6  on the SECOND scratch, `remove_bad_wires_scripted` removes a definite SET of wire uids - LabVIEW's own
      verdict - and ExecState before/after is recorded.
  P7  handle count before and after; both scratch VIs created and DELETED in this same run.
  P8  every original md5-identical BEFORE and AFTER (the 3StateClamping reference VI + every .vi under
      `zz_LabView VI\background VIs` + the V6 working copy + the two ops used as readers).
  P9  one file fact: guard_cycle's own newest_retrospective() vs newest_build_log().
  P10 no motor, no serial port, no camera, `motor_gate.py --execute` not called (Pre-decided 2 / P1).

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_wirebroken.log -- py -u tools/bench/diag_fstunnel_wirebroken.py
"""
import glob as _glob
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))                 # tools/bench
ROOT = os.path.dirname(os.path.dirname(HERE))                     # project root
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes"),
           os.path.join(ROOT, "tools", "hooks")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                               # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid                    # noqa: E402
import build_opfstunnelterm_v1 as V1                              # noqa: E402  READ ONLY - never patched on disk
import guard_cycle                                                # noqa: E402  the gate's own reader

STAMP = time.strftime("%H%M%S")
SCR_A = os.path.join(g.CLAUDEDEV, f"SCRATCH_fswbA_{STAMP}_{os.getpid()}.vi")
SCR_B = os.path.join(g.CLAUDEDEV, f"SCRATCH_fswbB_{STAMP}_{os.getpid()}.vi")
CFW = os.path.join(g.CLAUDEDEV, "OpConnectFromWire_v0.vi")
CFW_LABELS = os.path.join(HERE, "opconnectfromwire_v0_labels.json")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
V5_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
OUT = os.path.join(HERE, "diag_fstunnel_wirebroken.json")

ZZ = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))      # ...\zz_LabView VI
BGVIS = os.path.join(ZZ, "background VIs")
ORIGINALS = [V1.ORIG_3STATE] + sorted(_glob.glob(os.path.join(BGVIS, "**", "*.vi"), recursive=True))
WATCHED = ORIGINALS + [V1.V6, V1.DONOR, CFW, V5]

# run 1's numbers, so the reproduction is checked against the machine's record and not against memory
RUN1 = {"terms": 145, "ia": 151, "tmsc": 1044, "consumers": [157, 1319, 1326],
        "wires": [384, 384, 1694, 1719, 1719, 1766]}
# The six wire_checked() call sites IN THE ORDER build_one() executes them, as
# (line in tools/recipes/build_opfstunnelterm_v1.py, the line as the cycle-23 brief numbers it - a constant -45
# offset, because the brief's numbers are `_v0.py`'s, which lacks _v1's 45-line "WHY THIS IS _v1" header block).
# Matched BY POSITION, not by tag text: two sites both end in `->UID`.
SITE_LINES = [(476, 431), (483, 438), (486, 441), (489, 444), (494, 449), (497, 452)]
STUB = 384

RES = {"gates": [], "repro": {}, "sites": [], "wires_census": {}, "v5": {}, "rbw": {}, "md5": {},
       "handles": {}, "retro": {}, "exec": {}}


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:300]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:500]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:400]}", flush=True)


def md5(p):
    try:
        h = hashlib.md5()
        with open(p, "rb") as f:
            for b in iter(lambda: f.read(1 << 20), b""):
                h.update(b)
        return h.hexdigest()
    except Exception as e:
        return f"ERR {e}"


def snapshot(tag):
    d = {p: md5(p) for p in WATCHED}
    RES["md5"][tag] = d
    print(f"-- md5 {tag}: {len(d)} files ({len(ORIGINALS)} originals) --", flush=True)
    print(f"   {d[V1.ORIG_3STATE]}  {os.path.basename(V1.ORIG_3STATE)}", flush=True)
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


# ============================================================ the B4 freeze
class StopAtB4(Exception):
    pass


_V1_MUST = V1.must


def _must_hook(label, ok, detail=""):
    r = _V1_MUST(label, ok, detail)
    if label.startswith("B4 "):                 # "B4b ..." does NOT match - it fires before B4 and must pass through
        raise StopAtB4(f"{label} | {detail}")
    return r


def build_to_b4(kind, path):
    """Run build_opfstunnelterm_v1.build_one(kind) verbatim, onto `path`, and freeze it at the B4 gate."""
    spec = list(V1.SPEC[kind])
    spec[0] = path
    V1.SPEC[kind] = tuple(spec)
    V1.must = _must_hook
    print(f"\n================ REPRODUCE build_one({kind!r}) -> {os.path.basename(path)} ================",
          flush=True)
    try:
        V1.build_one(kind)
        return "NO STOP: build_one returned without the B4 gate firing"
    except StopAtB4 as e:
        return f"FROZEN AT B4: {e}"
    except Exception as e:
        return f"EXC before B4: {type(e).__name__} {str(e)[:200]}"


# ============================================================ the readers
def wire_source_owner(target, wire_uid, n=6):
    """COPIED from build_opconnectfromwire_v0.py:423-447. `OpWireSource_v5` per terminal of one wire. READ-ONLY."""
    with open(V5_LABELS, encoding="utf-8") as f:
        lab = json.load(f)
    vi = g.op(V5)
    out = []
    for i in range(n):
        try:
            vi.SetControlValue("vi path", target)
            vi.SetControlValue(lab["uid_in"], int(wire_uid))
            vi.SetControlValue(lab["term_index"], i)
            g._run(vi)
            r = dict(i=i, is_source=bool(vi.GetControlValue(lab["is_source"])),
                     owner_class=vi.GetControlValue(lab["ownercls"]),
                     owner_uid=int(vi.GetControlValue(lab["owner_uid"])),
                     recip=int(vi.GetControlValue(lab["recip_wire"])))
        except Exception as e:
            out.append(dict(i=i, err=str(e)[:70]))
            break
        out.append(r)
        if not r["owner_uid"] and not r["is_source"]:
            break
    return out


def connect_from_wire(target, wire_uid, term_index, sink_diag, sink_node, sink_term, labels):
    """COPIED from build_opconnectfromwire_v0.py:381-420, unchanged. Returns (wire delta, ExecState, err, sub)."""
    w0 = g.count(target, "Wire")
    vi = g.op(CFW)
    vi.SetControlValue("vi path", target)
    vi.SetControlValue("Class Name", "Diagram")
    vi.SetControlValue(labels["sink_diag"], int(sink_diag))
    vi.SetControlValue(labels["sink_node"], int(sink_node))
    vi.SetControlValue(labels["sink_term"], int(sink_term))
    vi.SetControlValue(labels["wire_uid"], int(wire_uid))
    vi.SetControlValue(labels["wire_term_index"], int(term_index))
    for k in (labels["dead_src_node"], labels["dead_src_term"], labels["dead_src_diag"]):
        try:
            vi.SetControlValue(k, 0)
        except Exception:
            pass
    for k, v in (("error in (no error)", (False, 0, "")), ("error in", (True, 1, "neutralised creator")),
                 ("Class Name 3", ""), ("Class Name 2", "")):
        try:
            vi.SetControlValue(k, v)
        except Exception:
            pass
    err = ""
    try:
        g._run(vi)
        err = g._err(vi, "error out") or ""
    except RuntimeError as e:
        err = "modal dialog (dismissed)" if "modal dialog" in str(e) else f"EXC {str(e)[:140]}"
    sub = {}
    for k in ("err_uidvi", "err_wirepn"):
        if labels.get(k):
            sub[k] = g._err(vi, labels[k]) or ""
    for k in ("UID 2", "Is Broken?", "Name"):
        try:
            sub[k] = vi.GetControlValue(k)
        except Exception:
            pass
    return g.count(target, "Wire") - w0, g.exec_state(target), err, sub


def term_index_of(target, node_uid, term_name, want_source=False):
    ni = V1.node_index_of(target, node_uid)
    if ni is None:
        return None, None
    rows = g.node_terms_uid(target, 0, ni)[1]
    t = next((r["i"] for r in rows if r["name"] == term_name and bool(r["is_source"]) == want_source), None)
    return ni, t


def read_broken(target, wire_uid, sinks, labels):
    """`Wire.Is Broken?` on ONE wire, through OpConnectFromWire_v0's own W7b-ordered readout.

    `sinks` = [(node_uid, term_name), ...] - every terminal this wire is known to sink into at the B4 point. The
    Invoke re-connects the wire's own source terminal into one of them (an IDEMPOTENT pair), because the readout
    is downstream of the Invoke's `error out` and cannot run otherwise. A row is only trusted when `UID 2`
    comes back equal to `wire_uid`."""
    terms = wire_source_owner(target, wire_uid)
    src_idx = [r["i"] for r in terms if r.get("is_source")]
    attempts = []
    for node_uid, term_name in sinks:
        ni, ti = term_index_of(target, node_uid, term_name)
        if ni is None or ti is None:
            attempts.append({"sink": [node_uid, term_name], "why": f"sink terminal not found (node index {ni})"})
            continue
        for si in (src_idx or [0, 1]):
            dw, es, err, sub = connect_from_wire(target, wire_uid, si, 0, ni, ti, labels)
            rec = {"sink": [node_uid, term_name], "sink_node_index": ni, "sink_term_index": ti,
                   "wire_term_index": si, "wire_delta": dw, "exec_after": es, "op_err": err[:200],
                   "uid2": sub.get("UID 2"), "is_broken": sub.get("Is Broken?"), "name": sub.get("Name"),
                   "err_uidvi": str(sub.get("err_uidvi", ""))[:120],
                   "err_wirepn": str(sub.get("err_wirepn", ""))[:120]}
            attempts.append(rec)
            print(f"      READ w{wire_uid} via sink #{node_uid}.{term_name!r} (Nodes[{ni}] T[{ti}], "
                  f"wire term {si}): UID 2 = {rec['uid2']!r}, Is Broken? = {rec['is_broken']!r}, "
                  f"wire delta {dw}, ExecState {es}, op err {err[:80]!r}", flush=True)
            if not err and rec["uid2"] == wire_uid and isinstance(rec["is_broken"], bool):
                return rec, terms, attempts
    return None, terms, attempts


# ============================================================ main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT P1..P10 - see this file's docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    print(f"   scratch A {SCR_A}\n   scratch B {SCR_B}", flush=True)
    before = snapshot("before")

    # ---- P9, no LabVIEW needed, done first so it is reported even if the rest dies ----------------------
    try:
        retro = guard_cycle.newest_retrospective()
        bl = guard_cycle.newest_build_log()

        def _fmt(x):
            return None if not x else {"file": os.path.relpath(x[0], ROOT).replace("\\", "/"),
                                       "stamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(x[1]))}
        RES["retro"] = {"newest_retrospective": _fmt(retro), "newest_build_log": _fmt(bl),
                        "retro_newer_than_build_log": bool(retro and bl and retro[1] > bl[1]),
                        "would_block_a_recipe_build": bool(bl and (retro is None or retro[1] <= bl[1]))}
        note("P9 guard_cycle.newest_retrospective()", RES["retro"]["newest_retrospective"])
        note("P9 guard_cycle.newest_build_log()", RES["retro"]["newest_build_log"])
        note("P9 retrospective NEWER than the newest build log", RES["retro"]["retro_newer_than_build_log"])
    except Exception as e:
        RES["retro"] = {"EXC": str(e)[:200]}
        note("P9 guard_cycle read", f"EXC {str(e)[:200]}")

    try:
        labels = json.load(open(CFW_LABELS, encoding="utf-8"))
    except Exception as e:
        labels = None
        must("P0 the OpConnectFromWire_v0 label map loads", False, str(e)[:200])

    try:
        fresh()
        handles("after a fresh LabVIEW, before any work")

        # ================= scratch B first: LabVIEW's OWN verdict, on an UNPERTURBED B4 state =============
        stopB = build_to_b4("OUT", SCR_B)
        note("scratch B stop reason", stopB)
        esB = g.exec_state(SCR_B)
        wB0 = g.uids(SCR_B, "Wire")
        RES["rbw"]["exec_before"] = esB
        RES["rbw"]["wires_before"] = sorted(wB0)
        try:
            g.remove_bad_wires_scripted(SCR_B)
            rbw_err = ""
        except Exception as e:
            rbw_err = str(e)[:200]
        wB1 = g.uids(SCR_B, "Wire")
        esB2 = g.exec_state(SCR_B)
        RES["rbw"].update({"wires_after": sorted(wB1), "removed": sorted(wB0 - wB1),
                           "added": sorted(wB1 - wB0), "exec_after": esB2, "err": rbw_err})
        print(f"   RBW on scratch B: ExecState {esB} -> {esB2}; {len(wB0)} -> {len(wB1)} wires; "
              f"REMOVED {sorted(wB0 - wB1)}; added {sorted(wB1 - wB0)}; err {rbw_err!r}", flush=True)
        must("P6 Remove Bad Wires ran on the B4 scratch and its removed-wire SET was recorded", not rbw_err,
             f"removed {sorted(wB0 - wB1)}")
        try:
            g.close_panel(SCR_B)
        except Exception:
            pass

        # ================= scratch A: the primary reads ====================================================
        V1.RES["wires"] = []
        V1.RES["build"] = []
        stopA = build_to_b4("OUT", SCR_A)
        note("scratch A stop reason", stopA)
        must("P2a the reproduction reached the B4 gate (so the frozen state IS the B4 point)",
             stopA.startswith("FROZEN AT B4"), stopA)

        b1 = next((b for b in V1.RES["build"] if "pn_terms" in b), {})
        RES["repro"] = {"b1": b1, "run1": RUN1}
        wires_seen = [w.get("src_after") for w in V1.RES["wires"]]
        RES["repro"]["wires_seen"] = wires_seen
        must("P1 the reproduction matches run 1 object for object (terms/ia/tmsc/consumers and all six wires)",
             b1.get("pn_terms") == RUN1["terms"] and b1.get("ia") == RUN1["ia"]
             and b1.get("tmsc") == RUN1["tmsc"] and list(b1.get("consumers") or []) == RUN1["consumers"]
             and wires_seen == RUN1["wires"],
             f"terms {b1.get('pn_terms')} ia {b1.get('ia')} tmsc {b1.get('tmsc')} "
             f"consumers {b1.get('consumers')} wires {wires_seen} vs run1 {RUN1['wires']}")

        esA = g.exec_state(SCR_A)
        RES["exec"]["at_b4"] = esA
        must("P2 ExecState at the B4 point is 0, as run 1 measured (build_opfstunnelterm_v1_run1.log:75)",
             esA == 0, f"ExecState {esA}")

        census = g.report_all(SCR_A, "Wire")
        wuids = sorted({int(o["uid"]) for o in census})
        RES["wires_census"] = {"n": len(wuids), "uids": wuids, "has_384": STUB in wuids}
        note("P4 Wire census at B4", f"{len(wuids)} wires; #384 present = {STUB in wuids}")
        must("P4 the residual stub wire #384 is present in the Wire census at the B4 point", STUB in wuids,
             f"{len(wuids)} wires")

        # sinks per wire, taken from the recipe's OWN six records
        by_wire = {}
        for w in V1.RES["wires"]:
            by_wire.setdefault(w.get("src_after"), []).append((w["dst_uid"], w["dst_term"]))
        for w_uid, sinks in by_wire.items():
            note(f"wire {w_uid} sinks at B4", sinks)

        # --- P5 read-only cross-check + P3 the property, once per DISTINCT wire ---------------------------
        per_wire = {}
        for w_uid in sorted(by_wire, key=lambda x: (x is None, x)):
            if not w_uid:
                continue
            print(f"\n   --- wire {w_uid} ---", flush=True)
            rec, terms, attempts = (None, [], [])
            if labels:
                rec, terms, attempts = read_broken(SCR_A, w_uid, by_wire[w_uid], labels)
            else:
                terms = wire_source_owner(SCR_A, w_uid)
            nsrc = sum(1 for t in terms if t.get("is_source"))
            RES["v5"][str(w_uid)] = {"terms": terms, "n_sources": nsrc}
            print(f"      OpWireSource_v5 (read-only) w{w_uid}: {terms}", flush=True)
            print(f"      terminals reporting Is Source? TRUE = {nsrc}  (>=2 = broken, docs/NAMES.md:900)",
                  flush=True)
            per_wire[w_uid] = {"row": rec, "n_sources": nsrc, "attempts": attempts,
                              "is_broken": (rec or {}).get("is_broken"),
                              "why": None if rec else "could-not-read: no attempt returned UID 2 == the wire "
                                                      "asked about with a boolean Is Broken? (see attempts)"}
        RES["per_wire"] = per_wire

        # --- the seven rows the brief asks for -----------------------------------------------------------
        print("\n================ THE SEVEN ROWS ================", flush=True)
        for si, w in enumerate(V1.RES["wires"]):
            tag = (w.get("tag") or "")
            v1line, brieflines = SITE_LINES[si] if si < len(SITE_LINES) else (None, None)
            pw = per_wire.get(w.get("src_after"), {})
            row = {"site_tag": tag.strip(), "v1_line": v1line, "brief_line": brieflines,
                   "src": f"#{w['src_uid']}.{w['src_term']}", "sink": f"#{w['dst_uid']}.{w['dst_term']}",
                   "wire": w.get("src_after"), "is_broken": pw.get("is_broken"),
                   "n_source_terminals": pw.get("n_sources"), "why": pw.get("why")}
            RES["sites"].append(row)
            print(f"   SITE _v1:{v1line} (brief :{brieflines}) {row['src']} -> {row['sink']} wire "
                  f"{row['wire']}: Is Broken? = {row['is_broken']!r}  (sources on that wire: "
                  f"{row['n_source_terminals']}){'  ' + str(row['why']) if row['why'] else ''}", flush=True)
        stub = per_wire.get(STUB, {})
        print(f"   STUB WIRE #{STUB}: Is Broken? = {stub.get('is_broken')!r}; sources "
              f"{stub.get('n_sources')}; sinks at B4 {by_wire.get(STUB)}"
              f"{'  ' + str(stub.get('why')) if stub.get('why') else ''}", flush=True)
        RES["stub_384"] = {"is_broken": stub.get("is_broken"), "n_sources": stub.get("n_sources"),
                           "sinks": by_wire.get(STUB), "why": stub.get("why")}
        read_ok = [k for k, v in per_wire.items() if isinstance(v.get("is_broken"), bool)]
        must("P3 every distinct wire at the six sites returned a boolean `Is Broken?` from the op's own "
             "6371004 readout with UID 2 == the wire asked about",
             len(read_ok) == len(per_wire), f"read {sorted(read_ok)} of {sorted(per_wire)}")
        must("P4b the stub wire #384 row was produced", STUB in per_wire,
             f"per_wire keys {sorted(per_wire)}")
        RES["exec"]["after_reads"] = g.exec_state(SCR_A)
        note("ExecState after all reads (perturbation check)", RES["exec"]["after_reads"])
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-2000:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        for p in (SCR_A, SCR_B):
            try:
                g.close_panel(p)
            except Exception:
                pass
        try:
            g.reset()
        except Exception:
            pass
        time.sleep(0.5)
        gone = []
        for p in (SCR_A, SCR_B):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"   scratch delete FAILED {os.path.basename(p)}: {str(e)[:120]}", flush=True)
            gone.append(not os.path.exists(p))
        must("P7 both scratch VIs were created and DELETED in this same run", all(gone),
             f"A gone {gone[0]}, B gone {gone[1]}")
        handles("after the run")
        after = snapshot("after")
        diff = [os.path.basename(p) for p in WATCHED if before.get(p) != after.get(p)]
        must(f"P8 all {len(ORIGINALS)} originals (+ the V6 copy and the two reader ops) are md5-identical "
             f"before and after", not diff and not any(str(v).startswith("ERR") for v in after.values()),
             f"differing: {diff}")
        must("P10 no motor, no serial port, no camera, motor_gate.py --execute not called (static: this file "
             "makes no such call)", True, "read-only VI Server + two scratch VIs")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:56] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
