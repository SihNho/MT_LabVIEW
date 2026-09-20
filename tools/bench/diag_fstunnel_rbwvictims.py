r"""diag_fstunnel_rbwvictims.py - WHAT ARE WIRES 894 AND 1356, WHERE DO THEY COME FROM, AND WHAT DOES
`Remove Bad Wires` TAKE WITH THEM, at the B4 point of build_opfstunnelterm_v1.

cycle 23 dispatch 2. DIAGNOSTIC ONLY - it lives under tools/bench, it SAVES NOTHING, it never writes to
tools/recipes/build_opfstunnelterm_v1.py (STATUS: ANY edit to `_v1.py` BRICKS its launch path,
`stop_record._check:325`). `_v1.py` is IMPORTED and FROZEN, exactly as dispatch 1 imported it. No recipe is
built, copied or released; no `_v2` is created.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "before creating any new op"):
  * tools/bench/diag_fstunnel_wirebroken.py (dispatch 1, 10/10, rc=0) - its B4 FREEZE (`must` hook raising at the
    `B4 ` gate), its `wire_source_owner()` / `connect_from_wire()` / `read_broken()` / `term_index_of()` readers
    and its md5+handle bookkeeping are COPIED VERBATIM from that file (which itself copied the two wrappers from
    build_opconnectfromwire_v0.py:381-447). Nothing is re-derived and no new op is built.
  * `Wire.Is Broken?` 6371004 - BUILT, docs/NAMES.md:888-897; its only Python-reachable carrier is
    OpConnectFromWire_v0.vi, whose readout is ORDERED after a SUCCESSFUL `Terminal.Connect Wire`, so the read
    re-connects the SAME source->sink pair the wire already has (dispatch 1's minimum-perturbation route).
  * `OpWireSource_v5.vi` + tools/bench/opwiresource_v5_labels.json - read-only per-terminal wire reader
    (owner class + owner uid + `Is Source?` per terminal index).
  * `build_opfstunnelterm_v1.sweep()` - the recipe's OWN per-node terminal map (OpNodeTerms). USED for the
    terminal-name/wire map instead of `gscript.net_map`, because net_map PERTURBS the target: it drops a junk
    Invoke per run and its purge CALLS `remove_bad_wires_scripted` itself (tools/gscript.py:2509-2531) - which
    would destroy the very measurement this file is making.
  * `gscript.remove_bad_wires_scripted` / `report_all` / `uids` / `exec_state` / `node_info` - unchanged.
  * `grep -n "^def " tools/gscript.py` + `ls tools/recipes tools/bench`: gscript has no wire-identity or
    RBW-diff reader, and no *rbwvictim* / *wireidentity* diagnostic exists. Nothing here is a second
    implementation of anything.

FACTS DISPATCH 1 ALREADY ESTABLISHED and this file does NOT re-derive: the six wire sites collapse to FOUR
distinct wires 384 / 1694 / 1719 / 1766; `Wire.Is Broken?` = True on #384 only; on a twin B4 scratch
`remove_bad_wires_scripted` removed [894, 1356] only, 43->41 wires, #384 survived, ExecState 0 -> 1.

PREDICTION CONTRACT (every line printed PASS/FAIL; one miss never hides the rest):
  M0  the reproduction matches run 1 object for object on BOTH twins (terms 145 / ia 151 / tmsc 1044 /
      consumers [157,1319,1326]; the six sites land on wires 384,384,1694,1719,1719,1766), and both twins read
      ExecState 0 at the B4 point.
  M1  IDENTITY of wire 894 and of wire 1356 at the B4 point, each END separately: terminal name + owning node's
      class + uid (from the recipe's own sweep map), plus OpWireSource_v5's per-terminal owner class/uid and
      which terminal index reports `Is Source?` TRUE. An end with NO owner / NO source terminal is reported AS
      THAT - it is the measurement, not a failure.
  M2  ORIGIN: the Wire uid census at every build checkpoint (each `sweep()` call, labelled by the `_v1.py` line
      that made it) plus the census of the DONOR FILE ITSELF (OpWireSource_v5.vi, read-only) - so "came with the
      template" vs "created by _v1's own code between line X and line Y" is read, not argued.
  M3  on the SECOND twin: after `remove_bad_wires_scripted`, `Wire.Is Broken?` 6371004 on #384, the VI's
      ExecState, and whether 1694 / 1719 / 1766 all still exist.
  M4  the NAMED list of (node uid, terminal name) that had a wire before that RBW call and reads 0 after it -
      plus every terminal whose wire uid CHANGED. Names, not a count.
  M5  textual only: do 894's / 1356's endpoint node uids and terminal names, and the literals 894 / 1356, occur
      in tools/recipes/build_opfstunnelterm_v1.py or docs/NAMES.md? file:line per hit, or "no hit".
  M6  ExecState of the UNTOUCHED twin at B4 (expect 0); LabVIEW handle count before/after; every original
      md5-identical BEFORE AND AFTER; both scratch VIs created and DELETED in this same run.
  M7  no motor, no serial port, no camera, `motor_gate.py --execute` not called (Pre-decided 2 / P1).

  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_rbwvictims.log -- py -u tools/bench/diag_fstunnel_rbwvictims.py
"""
import glob as _glob
import hashlib
import inspect
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))                 # tools/bench
ROOT = os.path.dirname(os.path.dirname(HERE))                     # project root
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                               # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid                    # noqa: E402
import build_opfstunnelterm_v1 as V1                              # noqa: E402  READ ONLY - never patched on disk

STAMP = time.strftime("%H%M%S")
SCR_C = os.path.join(g.CLAUDEDEV, f"SCRATCH_fsrvC_{STAMP}_{os.getpid()}.vi")   # untouched twin: identity + origin
SCR_D = os.path.join(g.CLAUDEDEV, f"SCRATCH_fsrvD_{STAMP}_{os.getpid()}.vi")   # RBW twin: M3 + M4
CFW = os.path.join(g.CLAUDEDEV, "OpConnectFromWire_v0.vi")
CFW_LABELS = os.path.join(HERE, "opconnectfromwire_v0_labels.json")
V5 = os.path.join(g.CLAUDEDEV, "OpWireSource_v5.vi")
V5_LABELS = os.path.join(HERE, "opwiresource_v5_labels.json")
OUT = os.path.join(HERE, "diag_fstunnel_rbwvictims.json")
V1_SRC = os.path.join(ROOT, "tools", "recipes", "build_opfstunnelterm_v1.py")
NAMES_MD = os.path.join(ROOT, "docs", "NAMES.md")

ZZ = os.path.dirname(os.path.dirname(os.path.dirname(ROOT)))      # ...\zz_LabView VI
BGVIS = os.path.join(ZZ, "background VIs")
ORIGINALS = [V1.ORIG_3STATE] + sorted(_glob.glob(os.path.join(BGVIS, "**", "*.vi"), recursive=True))
WATCHED = ORIGINALS + [V1.V6, V1.DONOR, CFW, V5]

RUN1 = {"terms": 145, "ia": 151, "tmsc": 1044, "consumers": [157, 1319, 1326],
        "wires": [384, 384, 1694, 1719, 1719, 1766]}
VICTIMS = [894, 1356]        # what RBW removed on dispatch 1's twin
STUB = 384
SITES = [1694, 1719, 1766]   # the other three distinct site wires
# candidate classes for uid -> class attribution, most specific first ("Node"/"GObject" match almost everything)
CLASSES = ["Property", "Invoke", "Function", "SubVI", "Constant", "Control", "Indicator", "Terminal",
           "IndexArray", "Node"]

RES = {"gates": [], "repro": {}, "ckpt": [], "donor_wires": {}, "identity": {}, "rbw": {}, "diff": {},
       "text": {}, "md5": {}, "handles": {}, "exec": {}, "stub_after": {}}


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


# ============================================================ the B4 freeze (COPIED from dispatch 1)
class StopAtB4(Exception):
    pass


_V1_MUST = V1.must
_V1_SWEEP = V1.sweep
CENSUS_ON = [None]          # the path whose Wire census is taken at every sweep()


def _must_hook(label, ok, detail=""):
    r = _V1_MUST(label, ok, detail)
    if label.startswith("B4 "):          # "B4b ..." must pass through - it fires BEFORE B4
        raise StopAtB4(f"{label} | {detail}")
    return r


def _sweep_hook(target, n=120, diagram=0):
    """V1.sweep, plus a Wire-uid census stamped with the `_v1.py` LINE that called it (M2's checkpoint timeline)."""
    r = _V1_SWEEP(target, n, diagram)
    try:
        line = inspect.currentframe().f_back.f_lineno
    except Exception:
        line = None
    if CENSUS_ON[0] and os.path.normcase(target) == os.path.normcase(CENSUS_ON[0]):
        try:
            w = sorted(g.uids(target, "Wire"))
        except Exception as e:
            w = [f"ERR {str(e)[:60]}"]
        rec = {"seq": len(RES["ckpt"]), "v1_line": line, "n_wires": len(w),
               "has_894": 894 in w, "has_1356": 1356 in w, "wires": w}
        RES["ckpt"].append(rec)
        print(f"   CKPT[{rec['seq']:02d}] sweep() from _v1.py:{line}  {len(w)} wires  894={rec['has_894']}  "
              f"1356={rec['has_1356']}", flush=True)
    return r


def build_to_b4(kind, path, census=False):
    spec = list(V1.SPEC[kind])
    spec[0] = path
    V1.SPEC[kind] = tuple(spec)
    V1.must = _must_hook
    V1.sweep = _sweep_hook
    CENSUS_ON[0] = path if census else None
    V1.RES["wires"] = []
    V1.RES["build"] = []
    print(f"\n================ REPRODUCE build_one({kind!r}) -> {os.path.basename(path)} "
          f"(census={census}) ================", flush=True)
    try:
        V1.build_one(kind)
        return "NO STOP: build_one returned without the B4 gate firing"
    except StopAtB4 as e:
        return f"FROZEN AT B4: {e}"
    except Exception as e:
        return f"EXC before B4: {type(e).__name__} {str(e)[:200]}"
    finally:
        CENSUS_ON[0] = None


def check_repro(tag, path):
    b1 = next((b for b in V1.RES["build"] if "pn_terms" in b), {})
    wires_seen = [w.get("src_after") for w in V1.RES["wires"]]
    ok = (b1.get("pn_terms") == RUN1["terms"] and b1.get("ia") == RUN1["ia"] and b1.get("tmsc") == RUN1["tmsc"]
          and list(b1.get("consumers") or []) == RUN1["consumers"] and wires_seen == RUN1["wires"])
    RES["repro"][tag] = {"b1": b1, "wires_seen": wires_seen, "matches_run1": bool(ok)}
    must(f"M0 [{tag}] the reproduction matches run 1 object for object", ok,
         f"terms {b1.get('pn_terms')} ia {b1.get('ia')} tmsc {b1.get('tmsc')} "
         f"consumers {b1.get('consumers')} wires {wires_seen}")
    es = g.exec_state(path)
    RES["exec"][tag] = es
    must(f"M0b [{tag}] ExecState at the B4 point is 0 (run 1, build_opfstunnelterm_v1_run1.log:75)", es == 0,
         f"ExecState {es}")
    return b1, wires_seen


# ============================================================ the readers (COPIED from dispatch 1)
def wire_source_owner(target, wire_uid, n=8):
    """COPIED from diag_fstunnel_wirebroken.py:186-208 (itself build_opconnectfromwire_v0.py:423-447). READ-ONLY."""
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
    """COPIED from diag_fstunnel_wirebroken.py:211-248, unchanged."""
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
    """COPIED from diag_fstunnel_wirebroken.py:260-288. `Wire.Is Broken?` 6371004 on ONE wire through
    OpConnectFromWire_v0's W7b-ordered readout; a row counts only when `UID 2` == the wire asked about."""
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
                   "uid2": sub.get("UID 2"), "is_broken": sub.get("Is Broken?"), "name": sub.get("Name")}
            attempts.append(rec)
            print(f"      READ w{wire_uid} via sink #{node_uid}.{term_name!r} (Nodes[{ni}] T[{ti}], wire term "
                  f"{si}): UID 2 = {rec['uid2']!r}, Is Broken? = {rec['is_broken']!r}, wire delta {dw}, "
                  f"ExecState {es}, op err {err[:80]!r}", flush=True)
            if not err and rec["uid2"] == wire_uid and isinstance(rec["is_broken"], bool):
                return rec, terms, attempts
    return None, terms, attempts


# ============================================================ identity helpers
def uid_classes(target):
    """{uid: [class, ...]} from report_all per candidate class - the most specific class is the non-'Node' one."""
    out = {}
    for cls in CLASSES:
        try:
            for o in g.report_all(target, cls):
                out.setdefault(int(o["uid"]), []).append(cls)
        except Exception as e:
            note(f"report_all({cls})", f"EXC {str(e)[:90]}")
    return out


def term_map(target):
    """{(node_uid, term_name, term_index): wire_uid} for every terminal of every diagram-0 node, from the
    recipe's OWN sweep (OpNodeTerms). Also returns {node_uid: node_index}."""
    by = _V1_SWEEP(target)
    m, idx = {}, {}
    for u, (i, rows) in by.items():
        idx[u] = i
        for r in rows:
            m[(int(u), r["name"], r["i"])] = int(r["wire"] or 0)
    return m, idx, by


def ends_of(tmap, wire_uid):
    return [dict(node_uid=k[0], term_name=k[1], term_index=k[2]) for k, v in tmap.items() if v == int(wire_uid)]


ROLE = {}          # uid -> the recipe's own name for that node, filled from V1.RES["build"]


def role_of(uid):
    return ROLE.get(int(uid), "")


def describe_wire(target, wire_uid, tmap, idx, ucls, tag):
    print(f"\n   ================ IDENTITY of wire {wire_uid} ({tag}) ================", flush=True)
    ends = ends_of(tmap, wire_uid)
    for e in ends:
        e["node_index"] = idx.get(e["node_uid"])
        e["node_classes"] = ucls.get(e["node_uid"], [])
        e["node_role_in_recipe"] = role_of(e["node_uid"])
        print(f"      END  node #{e['node_uid']} (Nodes[{e['node_index']}], classes {e['node_classes']}, "
              f"recipe role {e['node_role_in_recipe']!r})  terminal T[{e['term_index']}] {e['term_name']!r}",
              flush=True)
    if not ends:
        print("      END  NONE - no terminal of any diagram-0 node reads this wire uid (the measurement)",
              flush=True)
    terms = wire_source_owner(target, wire_uid)
    nsrc = [t["i"] for t in terms if t.get("is_source")]
    print(f"      OpWireSource_v5 per-terminal: {terms}", flush=True)
    print(f"      terminal count reported = {len(terms)}; Is Source? TRUE at index/indices {nsrc} "
          f"(>=2 sources = broken, docs/NAMES.md:900)", flush=True)
    rec = {"wire": int(wire_uid), "ends_from_sweep": ends, "n_ends_from_sweep": len(ends),
           "v5_terms": terms, "v5_n_terms": len(terms), "v5_source_indices": nsrc}
    RES["identity"][str(wire_uid)] = rec
    return rec


# ============================================================ M5 the textual fact
def grep_tokens(tokens):
    hits = {}
    for path in (V1_SRC, NAMES_MD):
        rel = os.path.relpath(path, ROOT).replace("\\", "/")
        try:
            with open(path, encoding="utf-8", errors="replace") as f:
                lines = f.readlines()
        except Exception as e:
            hits[rel] = [f"ERR {str(e)[:80]}"]
            continue
        for tok in tokens:
            pat = re.compile(rf"(?<![0-9A-Za-z_]){re.escape(str(tok))}(?![0-9A-Za-z_])") \
                if str(tok).isdigit() else re.compile(re.escape(str(tok)))
            for n, line in enumerate(lines, 1):
                if pat.search(line):
                    lst = hits.setdefault(str(tok), [])
                    if len(lst) < 25:
                        lst.append(f"{rel}:{n}  {line.strip()[:110]}")
                    elif len(lst) == 25:
                        lst.append(f"{rel}: ... further hits for {tok!r} truncated at 25")
    return hits


# ============================================================ main
def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT M0..M7 - see this file's docstring.", flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}", flush=True)
    print(f"   twin C (untouched) {SCR_C}\n   twin D (RBW)       {SCR_D}", flush=True)
    before = snapshot("before")
    try:
        labels = json.load(open(CFW_LABELS, encoding="utf-8"))
    except Exception as e:
        labels = None
        must("M0a the OpConnectFromWire_v0 label map loads", False, str(e)[:200])

    try:
        fresh()
        handles("after a fresh LabVIEW, before any work")

        # ---------- M2 part 1: the DONOR FILE's own Wire census (origin, read-only) ----------------------
        try:
            dw = sorted(g.uids(V1.DONOR, "Wire"))
            RES["donor_wires"] = {"n": len(dw), "has_894": 894 in dw, "has_1356": 1356 in dw, "uids": dw}
            print(f"\n   DONOR {os.path.basename(V1.DONOR)} (read-only): {len(dw)} wires; "
                  f"894 present = {894 in dw}; 1356 present = {1356 in dw}", flush=True)
            note("donor wire uids", dw)
        except Exception as e:
            RES["donor_wires"] = {"EXC": str(e)[:200]}
            note("donor wire census", f"EXC {str(e)[:150]}")

        # ================= twin C: the UNTOUCHED B4 state - checkpoints + identity =======================
        stopC = build_to_b4("OUT", SCR_C, census=True)
        note("twin C stop reason", stopC)
        must("M0c twin C reached the B4 gate (so the frozen state IS the B4 point)",
             stopC.startswith("FROZEN AT B4"), stopC)
        check_repro("C", SCR_C)

        # the recipe's own names for the nodes it built, so an endpoint can be named functionally
        for b in V1.RES["build"]:
            for k, lab in (("pn_terms", "donor Terms[] property node"), ("ia", "donor Index Array"),
                           ("tmsc", "front To More Specific Class"), ("pn_a", "PN_A (face A property node)"),
                           ("pn_b", "PN_B (face B property node)"), ("pn_a_uid", "PN face-A -> GObject.UID"),
                           ("pn_b_uid", "PN face-B -> GObject.UID"), ("pn_b_cw", "PN face-B -> Connected Wire"),
                           ("pn_b_cwu", "PN Connected Wire -> GObject.UID")):
                if b.get(k):
                    ROLE[int(b[k])] = lab
            for u in (b.get("consumers") or []):
                ROLE[int(u)] = "donor back-half `reference` sink"
        note("recipe roles by node uid", ROLE)

        tmapC, idxC, byC = term_map(SCR_C)
        uclsC = uid_classes(SCR_C)
        censusC = sorted(g.uids(SCR_C, "Wire"))
        RES["identity"]["_census_at_b4"] = {"n": len(censusC), "uids": censusC}
        note("twin C Wire census at B4", f"{len(censusC)} wires: {censusC}")

        # ---------- M1: the two victims, each end separately -------------------------------------------
        for w in VICTIMS:
            present = w in censusC
            must(f"M1a wire {w} exists in the twin-C Wire census at the B4 point", present,
                 f"{len(censusC)} wires")
            if present:
                describe_wire(SCR_C, w, tmapC, idxC, uclsC, f"RBW victim on dispatch 1's twin")
        # the four site wires, for contrast (already identified as wires by dispatch 1; ends were not)
        for w in [STUB] + SITES:
            if w in censusC:
                ends = ends_of(tmapC, w)
                RES["identity"][f"site_{w}"] = {"ends": [dict(e, node_role_in_recipe=role_of(e["node_uid"]),
                                                              node_index=idxC.get(e["node_uid"])) for e in ends]}
                print(f"   CONTRAST site wire {w} ends: "
                      f"{[(e['node_uid'], e['term_name'], role_of(e['node_uid'])) for e in ends]}", flush=True)

        # ---------- M2 part 2: the checkpoint timeline -------------------------------------------------
        print("\n   ================ M2 CHECKPOINT TIMELINE (Wire census per sweep) ================", flush=True)
        first = {}
        for w in VICTIMS:
            hit = next((c for c in RES["ckpt"] if w in (c["wires"] if isinstance(c["wires"], list) else [])), None)
            first[w] = None if hit is None else {"seq": hit["seq"], "v1_line": hit["v1_line"],
                                                 "n_wires": hit["n_wires"]}
            print(f"      wire {w}: first checkpoint = {first[w]}", flush=True)
        RES["ckpt_first"] = first
        for c in RES["ckpt"]:
            print(f"      CKPT[{c['seq']:02d}] _v1.py:{c['v1_line']:<4} {c['n_wires']:3d} wires  "
                  f"894={c['has_894']}  1356={c['has_1356']}", flush=True)
        must("M2 a checkpoint timeline was recorded for the whole build up to B4 (>=10 checkpoints)",
             len(RES["ckpt"]) >= 10, f"{len(RES['ckpt'])} checkpoints")
        must("M2b the ORIGIN of 894 and 1356 is decided from the machine (donor census + first checkpoint), "
             "not argued",
             all(first[w] is not None for w in VICTIMS) and "n" in RES["donor_wires"],
             f"first {first}; donor has 894={RES['donor_wires'].get('has_894')} "
             f"1356={RES['donor_wires'].get('has_1356')}")
        try:
            g.close_panel(SCR_C)
        except Exception:
            pass

        # ================= twin D: RBW, then M3 + M4 ====================================================
        stopD = build_to_b4("OUT", SCR_D, census=False)
        note("twin D stop reason", stopD)
        must("M0d twin D reached the B4 gate", stopD.startswith("FROZEN AT B4"), stopD)
        b1D, wiresD = check_repro("D", SCR_D)
        sinks_by_wire = {}
        for w in V1.RES["wires"]:
            sinks_by_wire.setdefault(w.get("src_after"), []).append((w["dst_uid"], w["dst_term"]))

        tmapD0, idxD0, byD0 = term_map(SCR_D)
        wD0 = sorted(g.uids(SCR_D, "Wire"))
        esD0 = g.exec_state(SCR_D)
        RES["rbw"]["exec_before"] = esD0
        RES["rbw"]["wires_before"] = wD0
        print(f"\n   twin D before RBW: ExecState {esD0}, {len(wD0)} wires", flush=True)

        try:
            g.remove_bad_wires_scripted(SCR_D)
            rbw_err = ""
        except Exception as e:
            rbw_err = str(e)[:200]
        wD1 = sorted(g.uids(SCR_D, "Wire"))
        esD1 = g.exec_state(SCR_D)
        tmapD1, idxD1, byD1 = term_map(SCR_D)
        RES["rbw"].update({"wires_after": wD1, "removed": sorted(set(wD0) - set(wD1)),
                           "added": sorted(set(wD1) - set(wD0)), "exec_after": esD1, "err": rbw_err})
        print(f"   RBW on twin D: ExecState {esD0} -> {esD1}; {len(wD0)} -> {len(wD1)} wires; "
              f"REMOVED {sorted(set(wD0) - set(wD1))}; added {sorted(set(wD1) - set(wD0))}; err {rbw_err!r}",
              flush=True)
        must("M3a Remove Bad Wires ran on twin D and its removed-wire SET was recorded", not rbw_err,
             f"removed {sorted(set(wD0) - set(wD1))}")
        RES["exec"]["D_after_rbw"] = esD1

        # ---------- M4: WHICH node terminals lost their wire -------------------------------------------
        lost, changed = [], []
        for k, v in tmapD0.items():
            after = tmapD1.get(k, "MISSING")
            if v and after == 0:
                lost.append({"node_uid": k[0], "term_name": k[1], "term_index": k[2], "wire_lost": v,
                             "node_index": idxD0.get(k[0]), "node_role_in_recipe": role_of(k[0])})
            elif v and isinstance(after, int) and after and after != v:
                changed.append({"node_uid": k[0], "term_name": k[1], "term_index": k[2],
                                "wire_before": v, "wire_after": after, "node_role_in_recipe": role_of(k[0])})
            elif after == "MISSING":
                changed.append({"node_uid": k[0], "term_name": k[1], "term_index": k[2], "wire_before": v,
                                "wire_after": "TERMINAL GONE", "node_role_in_recipe": role_of(k[0])})
        RES["diff"] = {"lost": lost, "changed": changed,
                       "n_terminals_before": len(tmapD0), "n_terminals_after": len(tmapD1)}
        print("\n   ================ M4 TERMINALS THAT LOST THEIR WIRE TO RBW ================", flush=True)
        for r in lost:
            print(f"      LOST  node #{r['node_uid']} (Nodes[{r['node_index']}], role "
                  f"{r['node_role_in_recipe']!r})  T[{r['term_index']}] {r['term_name']!r}  "
                  f"had wire {r['wire_lost']}", flush=True)
        if not lost:
            print("      NONE - no terminal that was wired before RBW reads 0 after it", flush=True)
        for r in changed:
            print(f"      CHANGED node #{r['node_uid']} T[{r['term_index']}] {r['term_name']!r}: "
                  f"{r['wire_before']} -> {r['wire_after']}  (role {r['node_role_in_recipe']!r})", flush=True)
        must("M4 the per-terminal before/after map was produced for twin D (terminals counted both sides)",
             len(tmapD0) > 0 and len(tmapD1) > 0, f"{len(tmapD0)} -> {len(tmapD1)} terminals")

        # ---------- M3: #384's Is Broken? AFTER the removal, and the site wires ------------------------
        print("\n   ================ M3 #384 AFTER the removal ================", flush=True)
        stub_present = STUB in wD1
        sites_present = {w: (w in wD1) for w in SITES}
        RES["stub_after"] = {"present": stub_present, "sites_present": sites_present, "exec_after": esD1}
        print(f"      #{STUB} still present after RBW = {stub_present}; site wires {sites_present}; "
              f"ExecState after RBW = {esD1}", flush=True)
        must("M3b all three other site wires (1694/1719/1766) still exist after RBW", all(sites_present.values()),
             str(sites_present))
        if stub_present and labels:
            rec, terms, attempts = read_broken(SCR_D, STUB, sinks_by_wire.get(STUB, []), labels)
            RES["stub_after"].update({"row": rec, "v5_terms": terms, "attempts": attempts,
                                      "is_broken": (rec or {}).get("is_broken"),
                                      "exec_after_read": g.exec_state(SCR_D)})
            print(f"      #{STUB} POST-RBW `Wire.Is Broken?` 6371004 = "
                  f"{(rec or {}).get('is_broken')!r}; ExecState after the read = "
                  f"{RES['stub_after']['exec_after_read']}", flush=True)
            must("M3 the post-RBW `Wire.Is Broken?` value for #384 was read with UID 2 == 384",
                 isinstance((rec or {}).get("is_broken"), bool),
                 f"row {rec}" if rec else f"no attempt returned UID 2 == {STUB}: {attempts}")
        else:
            must("M3 the post-RBW `Wire.Is Broken?` value for #384 was read", False,
                 f"#384 present = {stub_present}, labels = {bool(labels)}")

        # bonus, LAST and on the already-perturbed twin only: node style/label names
        try:
            ni = g.node_info(SCR_D, max_n=40)
            RES["diff"]["node_info_after_rbw"] = ni
            note("node_info (style, label) on twin D AFTER everything", ni)
            note("Wire census after node_info (perturbation check)", sorted(g.uids(SCR_D, "Wire")))
        except Exception as e:
            note("node_info", f"EXC {str(e)[:150]}")

        # ---------- M5: the textual fact ---------------------------------------------------------------
        toks = [str(w) for w in VICTIMS]
        for w in VICTIMS:
            for e in RES["identity"].get(str(w), {}).get("ends_from_sweep", []):
                toks += [str(e["node_uid"]), str(e["term_name"])]
        toks = [t for t in dict.fromkeys(toks) if t]
        RES["text"] = {"tokens": toks, "hits": grep_tokens(toks)}
        print("\n   ================ M5 TEXTUAL HITS ================", flush=True)
        for t in toks:
            h = RES["text"]["hits"].get(t) or []
            print(f"      token {t!r}: {'no hit' if not h else ''}", flush=True)
            for line in h[:8]:
                print(f"         {line}", flush=True)
        must("M5 the textual search ran over both files for every token", bool(toks), str(toks))
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-2000:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        for p in (SCR_C, SCR_D):
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
        for p in (SCR_C, SCR_D):
            if os.path.exists(p):
                try:
                    os.remove(p)
                except Exception as e:
                    print(f"   scratch delete FAILED {os.path.basename(p)}: {str(e)[:120]}", flush=True)
            gone.append(not os.path.exists(p))
        must("M6a both scratch VIs were created and DELETED in this same run", all(gone),
             f"C gone {gone[0]}, D gone {gone[1]}")
        handles("after the run")
        after = snapshot("after")
        diff = [os.path.basename(p) for p in WATCHED if before.get(p) != after.get(p)]
        must(f"M6 all {len(ORIGINALS)} originals (+ the V6 copy and the two reader ops) are md5-identical "
             f"before and after",
             not diff and not any(str(v).startswith("ERR") for v in after.values()), f"differing: {diff}")
        must("M7 no motor, no serial port, no camera, motor_gate.py --execute not called (static: this file "
             "makes no such call)", True, "read-only VI Server + two throwaway twin scratches")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:56] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
