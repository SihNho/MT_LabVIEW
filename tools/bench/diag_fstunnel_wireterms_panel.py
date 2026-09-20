r"""diag_fstunnel_wireterms_panel.py - WHAT IS ON THE OTHER END OF WIRES 894 AND 1356 AT `_v1.py:403`?

MEASUREMENT ONLY (cycle-24 firefighter, dispatch 1). Nothing is decided here, no recipe is launched, nothing is
saved, no original is opened, `tools/recipes/build_opfstunnelterm_v2.py` is neither imported nor run.
`build_opfstunnelterm_v1.py` is IMPORTED and hooked IN MEMORY ONLY - never edited on disk (STATUS: any edit
BRICKS its launch path).

WHY: STATUS OPEN 51(c). The node-side sweep (`OpNodeTerms.wire` column) gives each of 894/1356 exactly ONE node
terminal at `_v1.py:403`, and the opus arm of
`archive/peer/2026-09-18-fstunnel-orphans-empty-at-ckpt00-opus.md` argues the OTHER end is a front-panel object's
terminal, which a node-only sweep cannot see. That read - each wire's OWN `Wire.Terms[]` list, plus the panel
census - has never been run. This file runs it, and nothing else.

WHAT ALREADY EXISTS AND IS REUSED - checked before a line was written (CLAUDE.md "before creating any new op"):
  * `tools/bench/diag_fstunnel_orphan_timeline.py` (cycle 23 dispatch 4) - this file is a COPY of it with the
    deep reads added; its `sweep`/`must` hooks, the `StopAtB4` freeze and the T6..T9 hygiene gates are unchanged.
  * `tools/bench/diag_fstunnel_preclean_twins.py` - `orphan_wires()`, `nterms()`, `md5()`, `handles()`, `WATCHED`,
    `ORIGINALS` IMPORTED, not re-implemented.
  * `tools/bench/diag_fstunnel_rbwvictims.py` - `wire_source_owner()` (the `OpWireSource_v5.vi` per-terminal
    reader = `UID to GObject Reference` -> cast(Wire) -> `Wire.Terms[]`, i.e. the WIRE-SIDE list M1 asks for) and
    `uid_classes()` IMPORTED, not re-implemented.
  * `gscript.panel_wiring` (2026-09-14) / `gscript.node_labels` / `gscript.node_terms_uid` / `gscript.fp_labels`
    - already built; `grep "^def " tools/gscript.py` has NO wire-own-terminal reader and NO brokenness reader, so
    the only route to `Wire.Is Broken?` remains `OpConnectFromWire_v0`'s post-Invoke readout (docs/NAMES.md:888-911),
    which needs a SINK NODE TERMINAL and PERTURBS the target - see M6 below. NO NEW OP IS BUILT.
  * ALREADY MEASURED, so NOT re-run here: M7 (the B4-state `Wire.Is Broken?` read on the six sites + #384) is
    `tools/bench/diag_fstunnel_wirebroken.log:104-134`, 10/10 gates, rc=0, same reproduction verified object for
    object (`:95`). Repeating it would burn a LabVIEW run for a number already on disk.

PREDICTION CONTRACT (every line prints PASS/FAIL; a miss is a RESULT, not a failure):
  W1  at CKPT `_v1.py:403`, for EACH of 894 and 1356, `OpWireSource_v5` returns >=1 real terminal (owner_uid != 0),
      and every such terminal is resolved: owner class, owner label verbatim, owner uid, terminal index,
      source/sink, and the terminal NAME where a name exists.
  W2  every owner uid from W1 is classified as node / front-panel control-or-indicator terminal / tunnel /
      constant, from `uid_classes` + `panel_wiring` + `fp_labels` - never from a guess.
  W3  nodes #145 and #151 are identified at `:403`: class, label verbatim, and the FULL terminal-name list.
  W4  the M4 six wire sites are read from the TEXT of `_v1.py` (no LabVIEW): src object+terminal, sink
      object+terminal, as the recipe names them, with the TRUE line numbers.
  W5  the intersection of the W1/W2 owner set with the W4 endpoint set is printed with BOTH the matches and the
      non-matches at name level.
  W6  at CKPT `_v1.py:442`: `ExecState`, the Wire census, and for 894 / 1356 / 384 whether a SINK NODE TERMINAL
      exists (the precondition of the ONLY measured `Is Broken?` route). The read is performed only where that
      precondition holds, and the run records whether any perturbing connect was executed.
  W7  handle count before and after; the ONE scratch created and DELETED in this same run.
  W8  every original md5-identical BEFORE AND AFTER; no original opened.
  W9  no motor, no serial port, no camera; `motor_gate.py --execute` never called.

LAUNCH LINE:
  MATERIAL=1 py tools/bgrun.py --max-min 25 --log tools/bench/diag_fstunnel_wireterms_panel.log -- py -u tools/bench/diag_fstunnel_wireterms_panel.py MATERIAL=1
"""
import inspect
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), HERE, os.path.join(ROOT, "tools", "recipes")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
import gscript as g                                               # noqa: E402
from build_opconstvalue_v1 import fresh, lv_pid                    # noqa: E402
import build_opfstunnelterm_v1 as V1                              # noqa: E402  READ ONLY
import diag_fstunnel_preclean_twins as TW                         # noqa: E402  helpers REUSED
import diag_fstunnel_rbwvictims as RV                             # noqa: E402  helpers REUSED

STAMP = time.strftime("%H%M%S")
SCR = os.path.join(g.CLAUDEDEV, f"SCRATCH_fswtp_{STAMP}_{os.getpid()}.vi")
OUT = os.path.join(HERE, "diag_fstunnel_wireterms_panel.json")
V1_SRC = os.path.join(ROOT, "tools", "recipes", "build_opfstunnelterm_v1.py")
TRACK = [894, 1356]
STUB = 384
IDENT = [145, 151]
CKPT_LINES = (403, 442)
# most specific first; "Node"/"GObject" match almost everything, so they come last
CLASSES = ["Property", "Invoke", "Function", "SubVI", "Constant", "ControlTerminal", "Control", "Indicator",
           "Terminal", "LoopTunnel", "SelectorTunnel", "Tunnel", "IndexArray", "Diagram", "Node"]
RES = {"gates": [], "ckpt": [], "sites": [], "md5": {}, "handles": {}, "wireterms": {}, "identity": {},
       "m4": [], "m5": {}, "m6": {}, "perturbed": False}


def must(label, ok, detail=""):
    print(f"{'  PASS' if ok else '**FAIL'} {label}" + (f"  | {str(detail)[:320]}" if detail else ""), flush=True)
    RES["gates"].append({"label": label, "ok": bool(ok), "detail": str(detail)[:500]})
    return bool(ok)


def note(label, value):
    print(f"  NOTE {label}: {str(value)[:500]}", flush=True)


def carriers(by, wire_uid):
    """NODE-SIDE view (OpNodeTerms.wire column) - kept only so the two views can be compared."""
    out = []
    for u, (ni, rows) in by.items():
        for r in rows:
            if int(r["wire"] or 0) == int(wire_uid):
                out.append({"node": int(u), "node_index": ni, "term": r["name"], "term_index": r.get("i"),
                            "is_source": bool(r["is_source"])})
    return out


# ============================================================ M1/M2 - the WIRE-SIDE read
def context(target):
    """Everything needed to name an owner uid, in a handful of op runs."""
    ctx = {}
    try:
        ctx["classes"] = RV.uid_classes(target)                 # {uid: [class,...]} via report_all per class
    except Exception as e:
        ctx["classes"] = {}
        note("uid_classes", f"EXC {str(e)[:110]}")
    ctx["classes2"] = {}
    for cls in CLASSES:
        try:
            for o in g.report_all(target, cls):
                ctx["classes2"].setdefault(int(o["uid"]), []).append(cls)
        except Exception:
            pass
    try:
        ctx["node_labels"] = {int(r["uid"]): r["label"] for r in g.node_labels(target, 0, strict=False)[0]}
    except Exception as e:
        ctx["node_labels"] = {}
        note("node_labels", f"EXC {str(e)[:110]}")
    try:
        ctx["panel"] = g.panel_wiring(target)
    except Exception as e:
        ctx["panel"] = []
        note("panel_wiring", f"EXC {str(e)[:110]}")
    try:
        ctx["fp"] = g.fp_labels(target)
    except Exception as e:
        ctx["fp"] = []
        note("fp_labels", f"EXC {str(e)[:110]}")
    return ctx


def name_owner(ctx, by, owner_uid, wire_uid):
    """owner uid -> {classes, label, kind, term_name, term_index, is_source} using ONLY measured tables."""
    u = int(owner_uid)
    cls = ctx["classes2"].get(u) or ctx["classes"].get(u) or []
    lab = ctx["node_labels"].get(u)
    rec = {"owner_uid": u, "owner_classes": cls, "owner_label": lab, "kind": "", "term_name": None,
           "term_index": None, "term_is_source": None, "node_index": None, "panel_rows": []}
    # a node on diagram 0? then the terminal carrying this wire is nameable
    for nu, (ni, rows) in by.items():
        if int(nu) == u:
            rec["node_index"] = ni
            rec["kind"] = "block-diagram node"
            for r in rows:
                if int(r["wire"] or 0) == int(wire_uid):
                    rec["term_name"] = r["name"]
                    rec["term_index"] = r["i"]
                    rec["term_is_source"] = bool(r["is_source"])
            rec["all_term_names"] = [r["name"] for r in rows]
            break
    # a front-panel object whose TERMINAL carries this wire? (its Generic.Owner is the DIAGRAM - NAMES.md:885)
    pr = [p for p in ctx["panel"] if int(p.get("wire") or 0) == int(wire_uid)]
    rec["panel_rows"] = pr
    if pr and not rec["kind"]:
        rec["kind"] = "front-panel ControlTerminal (owner is the diagram, NAMES.md:885)"
    if not rec["kind"]:
        if any(c in ("Diagram",) for c in cls) or u == 0:
            rec["kind"] = "diagram / no object"
        elif "Constant" in cls:
            rec["kind"] = "constant"
        elif any("Tunnel" in c for c in cls):
            rec["kind"] = "structure tunnel"
        elif cls:
            rec["kind"] = f"other ({'/'.join(cls)})"
        else:
            rec["kind"] = "UNRESOLVED - no class table row for this uid"
    return rec


def read_wire_terms(target, wire_uid, by, ctx):
    terms = RV.wire_source_owner(target, wire_uid, n=12)
    rows = []
    for t in terms:
        r = dict(t)
        r["resolved"] = name_owner(ctx, by, t.get("owner_uid") or 0, wire_uid) if t.get("owner_uid") else None
        rows.append(r)
    # RUN-1 BUG (2026-09-18 13:14, KeyError 'resolved' at deep_403): `real` was built from `terms`, whose dicts
    # have no "resolved" key - the crash aborted the build before the :442 checkpoint. It must come from `rows`.
    real = [r for r in rows if r.get("owner_uid")]
    print(f"\n   ================ WIRE #{wire_uid} - its OWN Wire.Terms[] (OpWireSource_v5) ================",
          flush=True)
    for r in rows:
        if not r.get("owner_uid"):
            print(f"      T[{r.get('i')}] END OF LIST (owner_uid 0, is_source {r.get('is_source')!r}, "
                  f"err {r.get('err', '')!r})", flush=True)
            continue
        q = r["resolved"]
        print(f"      T[{r['i']}] {'SOURCE' if r['is_source'] else 'SINK  '}  owner class "
              f"{r['owner_class']!r}  owner uid {r['owner_uid']}  classes {q['owner_classes']}  "
              f"label {q['owner_label']!r}", flush=True)
        print(f"              kind: {q['kind']}; terminal name {q['term_name']!r} index {q['term_index']!r}; "
              f"reciprocal wire {r['recip']}", flush=True)
        for p in q["panel_rows"]:
            print(f"              PANEL ROW: label {p['label']!r} uid {p['uid']} "
                  f"{'indicator' if p['indicator'] else 'control'} is_source {p['is_source']} "
                  f"wire {p['wire']}", flush=True)
    RES["wireterms"][str(wire_uid)] = {"n_terms_total": len(terms), "n_terms_real": len(real), "rows": rows,
                                       "node_side_carriers": carriers(by, wire_uid)}
    return rows, real


# ============================================================ M3
def identify(target, by, ctx, uid):
    ni = V1.node_index_of(target, uid)
    rec = {"uid": uid, "node_index": ni, "classes": ctx["classes2"].get(uid) or ctx["classes"].get(uid) or [],
           "label": ctx["node_labels"].get(uid), "terms": []}
    if ni is not None:
        try:
            nu, rows = g.node_terms_uid(target, 0, ni)
            rec["node_uid_readback"] = nu
            rec["terms"] = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                             "wire": int(r["wire"] or 0)} for r in rows]
        except Exception as e:
            rec["EXC"] = str(e)[:140]
    print(f"\n   NODE #{uid}: Nodes[{rec['node_index']}]  classes {rec['classes']}  label {rec['label']!r}",
          flush=True)
    print(f"      terminals ({len(rec['terms'])}): "
          f"{[(t['i'], t['name'], 'src' if t['is_source'] else 'sink', t['wire']) for t in rec['terms']]}",
          flush=True)
    RES["identity"][str(uid)] = rec
    return rec


# ============================================================ M4 - from the TEXT of _v1.py
BRIEF_LINES = [431, 438, 441, 444, 449, 452]
MEASURED_SITES = {}          # _v1.py line -> the uids wire_checked was actually CALLED with


_V1_WIRE_CHECKED = V1.wire_checked


def _wire_checked_hook(op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag=""):
    """Records the uids each site is called with - so M4/M5 use MEASURED endpoints, not the recipe's variable
    names. Behaviour is otherwise the original's."""
    try:
        line = inspect.currentframe().f_back.f_lineno
    except Exception:
        line = None
    MEASURED_SITES[line] = {"src_class": src_cls, "src_uid": src_uid, "src_term": src_term,
                            "dst_class": dst_cls, "dst_uid": dst_uid, "dst_term": dst_term, "tag": tag.strip()}
    return _V1_WIRE_CHECKED(op, src_cls, src_uid, src_term, dst_cls, dst_uid, dst_term, tag=tag)


def m4_from_text():
    with open(V1_SRC, encoding="utf-8", errors="replace") as f:
        src = f.readlines()
    hits = []
    for i, line in enumerate(src, 1):
        if "wire_checked(" in line and not line.lstrip().startswith("#") and "def wire_checked" not in line:
            hits.append((i, line.rstrip()))
    print("\n================ M4 the six wire sites, from the TEXT of build_opfstunnelterm_v1.py ================",
          flush=True)
    for n, txt in hits:
        print(f"   _v1.py:{n}  {txt.strip()}", flush=True)
        RES["m4"].append({"line": n, "text": txt.strip()})
    note("M4 brief-quoted line numbers vs the file's real ones",
         f"brief {BRIEF_LINES} -> actual {[n for n, _ in hits]} "
         f"(offset {[n - b for (n, _), b in zip(hits, BRIEF_LINES)] if len(hits) == 6 else 'n/a'})")
    return hits


def m4_endpoints(hits, b1):
    """Resolve each site's (src obj+term -> sink obj+term) using the recipe's OWN variable names and the uids the
    reproduction measured for them."""
    kind = "OUT"
    _, _, _, short_a, _, short_b, _ = V1.SPEC[kind]
    cast_out = V1.T_CAST_OUT
    names = {"tmsc": b1.get("tmsc"), "pn_terms": b1.get("pn_terms"), "ia": b1.get("ia")}
    rows = []
    for n, txt in hits:
        # RUN-1 BUG: the 3rd positional is a BARE VAR at five sites but the QUOTED literal "Wire" at :497.
        m = re.search(r"wire_checked\(\s*op,\s*\"(\w+)\",\s*(\w+),\s*((?:\"[^\"]*\")|[A-Za-z_0-9]+),\s*"
                      r"\"(\w+)\",\s*(\w+),\s*\"([^\"]+)\"", txt)
        if not m:
            rows.append({"line": n, "PARSE": "no match", "text": txt.strip()})
            continue
        src_cls, src_var, src_term_var, dst_cls, dst_var, dst_term = m.groups()
        term = {"T_CAST_OUT": cast_out, "short_a": short_a, "short_b": short_b}.get(src_term_var,
                                                                                   src_term_var.strip('"'))
        rows.append({"line": n, "src_class": src_cls, "src_var": src_var, "src_uid": names.get(src_var),
                     "src_term": term, "dst_class": dst_cls, "dst_var": dst_var, "dst_term": dst_term,
                     "measured": MEASURED_SITES.get(n)})
    for r in rows:
        mm = r.get("measured") or {}
        print(f"   SITE _v1.py:{r['line']}: SRC {r.get('src_class')}#{r.get('src_var')}"
              f"(uid {mm.get('src_uid', r.get('src_uid'))}).{r.get('src_term')!r}  ->  SINK "
              f"{r.get('dst_class')}#{r.get('dst_var')}(uid {mm.get('dst_uid')}).{r.get('dst_term')!r}",
              flush=True)
    RES["m4_endpoints"] = rows
    return rows


class StopAtB4(Exception):
    pass


_V1_MUST = V1.must
_V1_SWEEP = V1.sweep
ARMED = [None]


def _must_hook(label, ok, detail=""):
    r = _V1_MUST(label, ok, detail)
    if label.startswith("B4 "):
        raise StopAtB4(f"{label} | {detail}")
    return r


def _sweep_hook(target, n=120, diagram=0):
    by = _V1_SWEEP(target, n, diagram)
    try:
        line = inspect.currentframe().f_back.f_lineno
    except Exception:
        line = None
    if ARMED[0] and os.path.normcase(target) == os.path.normcase(ARMED[0]):
        try:
            orph, census = TW.orphan_wires(target, by)
            es = g.exec_state(target)
            row = {"seq": len(RES["ckpt"]), "v1_line": line, "n_nodes": len(by), "n_terminals": TW.nterms(by),
                   "n_wires": len(census), "exec_state": es, "orphans": orph,
                   "present": {str(w): (w in census) for w in TRACK + [STUB]},
                   "carriers": {str(w): carriers(by, w) for w in TRACK + [STUB]}}
        except Exception as e:
            row = {"seq": len(RES["ckpt"]), "v1_line": line, "EXC": str(e)[:200]}
            census = []
        RES["ckpt"].append(row)
        print(f"   CKPT[{row['seq']:02d}] _v1.py:{row.get('v1_line')}  nodes {row.get('n_nodes')}  terminals "
              f"{row.get('n_terminals')}  wires {row.get('n_wires')}  ExecState {row.get('exec_state')}  "
              f"ORPHANS {row.get('orphans')}", flush=True)
        for w in TRACK + [STUB]:
            c = (row.get("carriers") or {}).get(str(w), [])
            short = [(x["node"], x["term"], x["term_index"], "src" if x["is_source"] else "sink") for x in c]
            print(f"        #{w}: present={(row.get('present') or {}).get(str(w))}  node-side carriers "
                  f"{short if short else 'NONE'}", flush=True)
        if line == 403 and "M1" not in RES["m5"]:
            deep_403(target, by, census)
        elif line == 442 and not RES["m6"]:
            deep_442(target, by, census)
    return by


def deep_403(target, by, census):
    print("\n================ M1/M2/M3 at _v1.py:403 (fresh copy, BEFORE the node deletes) ================",
          flush=True)
    ctx = context(target)
    note("panel census size", f"{len(ctx['panel'])} top-level panel objects; "
                             f"{sum(1 for p in ctx['panel'] if p['wire'])} with a wired terminal")
    reals = {}
    for w in TRACK:
        rows, real = read_wire_terms(target, w, by, ctx)
        reals[w] = real
    must("W1 each of 894/1356 returns >=1 REAL terminal (owner_uid != 0) from its own Wire.Terms[]",
         all(reals[w] for w in TRACK),
         {str(w): len(reals[w]) for w in TRACK})
    unres = [(w, r["owner_uid"]) for w in TRACK for r in reals[w]
             if (r.get("resolved") or {}).get("kind", "").startswith("UNRESOLVED")]
    must("W2 every owner uid found by W1 is classified from a measured table (no UNRESOLVED rows)",
         not unres, f"unresolved: {unres}")
    for u in IDENT:
        identify(target, by, ctx, u)
    must("W3 nodes #145 and #151 are identified with class, label and a full terminal list at :403",
         all(RES["identity"].get(str(u), {}).get("terms") for u in IDENT),
         {str(u): (RES["identity"].get(str(u), {}).get("classes"),
                   len(RES["identity"].get(str(u), {}).get("terms") or [])) for u in IDENT})
    RES["m5"]["M1"] = {str(w): [ (r["resolved"] or {}).get("owner_uid") for r in reals[w]] for w in TRACK}
    RES["m5"]["owner_names"] = {str(w): [{"uid": (r["resolved"] or {}).get("owner_uid"),
                                          "label": (r["resolved"] or {}).get("owner_label"),
                                          "kind": (r["resolved"] or {}).get("kind"),
                                          "term": (r["resolved"] or {}).get("term_name"),
                                          "classes": (r["resolved"] or {}).get("owner_classes")}
                                         for r in reals[w]] for w in TRACK}


def deep_442(target, by, census):
    print("\n================ M6 at _v1.py:442 (immediately after the two node deletes) ================",
          flush=True)
    es = g.exec_state(target)
    RES["m6"]["exec_state"] = es
    RES["m6"]["n_wires"] = len(census)
    print(f"   ExecState = {es}; {len(census)} wires; present "
          f"{ {str(w): (w in census) for w in TRACK + [STUB]} }", flush=True)
    for w in TRACK + [STUB]:
        ends = carriers(by, w)
        sinks = [(e["node"], e["term"]) for e in ends if not e["is_source"]]
        rec = {"present": w in census, "node_ends": ends, "sink_terminals": sinks, "is_broken": None,
               "why": ""}
        if not rec["present"]:
            rec["why"] = "wire absent from the census at this checkpoint"
        elif not sinks:
            rec["why"] = ("NO SINK NODE TERMINAL - the only measured `Wire.Is Broken?` route "
                          "(OpConnectFromWire_v0's post-Invoke readout) needs one; docs/NAMES.md:909-911")
        else:
            try:
                with open(os.path.join(HERE, "opconnectfromwire_v0_labels.json"), encoding="utf-8") as f:
                    labels = json.load(f)
                RES["perturbed"] = True
                row, terms, attempts = RV.read_broken(target, w, sinks, labels)
                rec["is_broken"] = (row or {}).get("is_broken")
                rec["read_row"] = row
                rec["why"] = "" if row else "the op never returned UID 2 == the wire asked about"
            except Exception as e:
                rec["why"] = f"EXC {str(e)[:140]}"
        print(f"   #{w}: present {rec['present']}, sinks {sinks or 'NONE'}, Is Broken? = {rec['is_broken']!r}"
              f"{'  (' + rec['why'][:150] + ')' if rec['why'] else ''}", flush=True)
        RES["m6"][str(w)] = rec
    must("W6 at :442 ExecState and the Wire census were read, and each of 894/1356/384 got either an "
         "`Is Broken?` value or a measured REASON it has no route",
         isinstance(es, int) and all(str(w) in RES["m6"] for w in TRACK + [STUB]),
         f"ExecState {es}; perturbing connect executed = {RES['perturbed']}")


def static_selfcheck():
    tok_rbw = "remove_bad_wires" + "_scripted("
    try:
        with open(os.path.abspath(__file__), encoding="utf-8", errors="replace") as f:
            src = f.readlines()
    except Exception as e:
        return [f"ERR {str(e)[:80]}"]
    return [i for i, l in enumerate(src, 1) if tok_rbw in l and not l.lstrip().startswith("#")]


def main():
    try:
        sys.stdout.reconfigure(errors="replace")
    except Exception:
        pass
    print("PREDICTION CONTRACT W1..W9 - see this file's docstring. MEASUREMENT ONLY; nothing is decided here.",
          flush=True)
    print(f"   LabVIEW pid before anything: {lv_pid()}\n   scratch {SCR}", flush=True)
    must("W0 STATIC: this file never calls remove_bad_wires_scripted", not static_selfcheck(),
         str(static_selfcheck()))
    before = {p: TW.md5(p) for p in TW.WATCHED}
    RES["md5"]["before"] = before
    print(f"-- md5 before: {len(before)} files ({len(TW.ORIGINALS)} originals) --", flush=True)

    hits = m4_from_text()
    must("W4a exactly six wire_checked sites were found in the text of _v1.py", len(hits) == 6,
         f"lines {[n for n, _ in hits]}")

    try:
        fresh()
        RES["handles"]["before"] = TW.handles("after a fresh LabVIEW, before any work")

        spec = list(V1.SPEC["OUT"])
        spec[0] = SCR
        V1.SPEC["OUT"] = tuple(spec)
        V1.must = _must_hook
        V1.sweep = _sweep_hook
        V1.wire_checked = _wire_checked_hook
        V1.RES["wires"] = []
        V1.RES["build"] = []
        ARMED[0] = SCR
        print(f"\n================ REPRODUCE build_one('OUT') -> {os.path.basename(SCR)} ================",
              flush=True)
        try:
            stop = "NO STOP: build_one returned without the B4 gate firing"
            V1.build_one("OUT")
        except StopAtB4 as e:
            stop = f"FROZEN AT B4: {e}"
        except Exception as e:
            stop = f"EXC before B4: {type(e).__name__} {str(e)[:260]}"
        finally:
            ARMED[0] = None
        note("stop reason", stop)
        RES["stop"] = stop

        b1 = next((b for b in V1.RES["build"] if "pn_terms" in b), {})
        RES["b1"] = b1
        must("W4b the reproduction found the same front section as run 1 (terms 145 / ia 151 / tmsc 1044 / "
             "consumers [157,1319,1326])",
             b1.get("pn_terms") == 145 and b1.get("ia") == 151 and b1.get("tmsc") == 1044
             and list(b1.get("consumers") or []) == [157, 1319, 1326],
             f"terms {b1.get('pn_terms')} ia {b1.get('ia')} tmsc {b1.get('tmsc')} "
             f"consumers {b1.get('consumers')}")
        ep = m4_endpoints(hits, b1)
        must("W4 all six sites were resolved to a src object+terminal and a sink object+terminal",
             len(ep) == 6 and all("PARSE" not in r for r in ep), f"{[r.get('PARSE') for r in ep]}")

        # ---- M5: do the M1/M2 owners appear as M4 endpoints?
        owners = {}
        for w in TRACK:
            for rec in (RES["m5"].get("owner_names") or {}).get(str(w), []):
                owners[rec["uid"]] = rec
        # EVERY M4 endpoint, by the recipe's own variable name AND the uid wire_checked was really called with
        endpoints = {}
        for r in ep:
            mm = r.get("measured") or {}
            for side in ("src", "dst"):
                v = r.get(f"{side}_var")
                u = mm.get(f"{side}_uid")
                if v:
                    endpoints.setdefault(v, set()).add(u)
        print("\n================ M5 do the wire-894/1356 owners appear as M4 endpoints? ================",
              flush=True)
        print(f"   M4 endpoint objects (recipe name -> measured uid): "
              f"{ {k: sorted(x for x in v if x is not None) for k, v in endpoints.items()} }", flush=True)
        print(f"   objects known at :403: tmsc #{b1.get('tmsc')}, the DELETED Terms[] PN #{b1.get('pn_terms')}, "
              f"the DELETED Index Array #{b1.get('ia')}. pn_a/pn_b/pn_a_uid/pn_b_uid/pn_b_cw/pn_b_cwu are "
              f"BUILT AFTER :442 and do not exist at :403.", flush=True)
        ep_uids = {u for v in endpoints.values() for u in v if u is not None}
        matches, nonmatches = [], []
        for u, rec in owners.items():
            names_hit = sorted(k for k, v in endpoints.items() if u in v)
            row = {"owner_uid": u, "label": rec["label"], "kind": rec["kind"], "m4_endpoint_names": names_hit}
            (matches if names_hit else nonmatches).append(row)
        for r in matches:
            print(f"   MATCH-BY-UID owner #{r['owner_uid']} ({r['label']!r}, {r['kind']}) shares its uid with "
                  f"M4 endpoint(s) {r['m4_endpoint_names']} - ⚠️ CHECK UID REUSE: those endpoints are nodes the "
                  f"recipe BUILDS after deleting #145/#151, so an equal uid is not the same object", flush=True)
        for r in nonmatches:
            print(f"   NO MATCH     owner #{r['owner_uid']} ({r['label']!r}, {r['kind']}) is NOT an endpoint of "
                  f"any of the six sites (endpoint uids {sorted(ep_uids)})", flush=True)
        RES["m5"]["matches"] = matches
        RES["m5"]["nonmatches"] = nonmatches
        RES["m5"]["endpoints"] = {k: sorted(x for x in v if x is not None) for k, v in endpoints.items()}
        must("W5 the owner set was compared against the six sites' MEASURED endpoints, with matches AND "
             "non-matches printed at name level", bool(owners) and bool(ep_uids),
             f"{len(matches)} match, {len(nonmatches)} non-match; endpoint uids {sorted(ep_uids)}")

        es_b4 = g.exec_state(SCR)
        RES["exec_at_b4"] = es_b4
        note("ExecState at the B4 freeze (SUSPECT if a perturbing connect ran at :442 - NAMES.md:898)",
             f"{es_b4}; perturbing connect executed = {RES['perturbed']}")
        note("M7 NOT re-run - already measured", "tools/bench/diag_fstunnel_wirebroken.log:104-134 (10/10, rc=0)")
        for i, w in enumerate(V1.RES["wires"]):
            RES["sites"].append({"site": i + 1, "tag": (w.get("tag") or "").strip(), "wire": w.get("src_after"),
                                 "exec_before": w.get("exec_before"), "exec_after": w.get("exec_after")})
        note("the six sites' wires in this reproduction", [r["wire"] for r in RES["sites"]])
    except Exception as e:
        import traceback
        print(f"\nOBSERVED EXC {str(e)[:300]}\n{traceback.format_exc()[-1500:]}", flush=True)
        must("Z the run completed without an unhandled exception", False, str(e)[:200])
    finally:
        try:
            g.close_panel(SCR)
        except Exception:
            pass
        try:
            g.reset()
        except Exception:
            pass
        time.sleep(0.5)
        if os.path.exists(SCR):
            try:
                os.remove(SCR)
            except Exception as e:
                print(f"   scratch delete FAILED: {str(e)[:120]}", flush=True)
        must("W7 the ONE scratch VI was created and DELETED in this same run", not os.path.exists(SCR), SCR)
        RES["handles"]["after"] = TW.handles("after the run")
        after = {p: TW.md5(p) for p in TW.WATCHED}
        RES["md5"]["after"] = after
        diff = [os.path.basename(p) for p in TW.WATCHED if before.get(p) != after.get(p)]
        must(f"W8 all {len(TW.ORIGINALS)} originals (+ the V6 copy and the donor) are md5-identical before and "
             f"after", not diff and not any(str(v).startswith("ERR") for v in after.values()),
             f"differing: {diff}")
        must("W9 no motor, no serial port, no camera, motor_gate.py --execute not called (static: this file "
             "makes no such call)", True, "read-only VI Server + one throwaway scratch VI")
        with open(OUT, "w", encoding="utf-8") as f:
            json.dump(RES, f, indent=1, default=str, ensure_ascii=False)
        npass = sum(1 for x in RES["gates"] if x["ok"])
        print(f"\nSUMMARY gates {npass}/{len(RES['gates'])} pass; failing: "
              f"{[x['label'][:56] for x in RES['gates'] if not x['ok']]}", flush=True)
        print(f"raw -> {OUT}", flush=True)
    return 0 if all(x["ok"] for x in RES["gates"]) else 1


if __name__ == "__main__":
    sys.exit(main())
