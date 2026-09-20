r"""diag_s3a_ind_transport - cycle 56: MEASURE THE TWO TRANSPORT VERBS S3a NEEDS (Pre-decided 45(c)/(f)).

🔴 A DIAGNOSTIC under `tools/bench/`, NEVER a recipe and never to be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND INTERPRETS NOTHING. Which route S3a should use is a DESIGN decision reserved to the
   judgement session (the brief says so in as many words). Nothing here recommends a route.
🔴 NO VI IS RUN (Pre-decided 34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53 "no more devices"). No motor, no ASI, no camera,
   no GUI action. Rig state 조립/ASSEMBLED.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never opened for writing; their
   md5s are probed before and after. Every edit happens on a DATED SCRATCH copy of the S2 artefact, one per
   route, so neither route can contaminate the other (the cycle-55 file-name collision is not repeated: the
   route tag is IN the file name).

THE QUESTION. Pre-decided 45 routes 1.5 FOCUS's two 1.2-sourced inputs through LOCAL VARIABLES, whose panel
indicators must first be created and wired AT THE SOURCES, which live inside `WhileLoop #637`'s body. Two
mechanically different constructions are available from ALREADY-BUILT verbs, and nobody has measured either on
a nested source:
  Route A (no move)  `create_indicator` puts a ControlTerminal wherever it puts it; `wire_indicators` is then
                     asked to branch the nested source onto it BY LABEL, with the source addressed inside the
                     structure (`node_class` + `diagram_index`).
  Route B (moved in) on a FRESH copy, the ControlTerminal is `move_in`-ed into the diagram that holds the
                     source FIRST, and only then is `wire_indicators` called - now a same-diagram call.
THE SOURCE IS GIVEN BY THE BRIEF, not chosen here: `#10686` t0 `'x .and. y?'`, wire 10799, the every-25-frames
schedule boolean (Pre-decided 45(c)). It is ALREADY WIRED, which is what `wire_indicators`' contract requires
of a source (`gscript.py:1764-1770`).

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `gscript.create_indicator` `:2385` (OpCreateIndicator_v0, Terminal.Create Indicator 6349C02) and
    `gscript.wire_indicators` `:1756` (OpWireInd_v0, erdosmiller `Wire Indicators.vi`) - the two verbs the
    brief names. Their docstrings carry two constraints this script must respect and does:
      - create_control/create_indicator: "a wired terminal or an out-of-range index yields no control"
        (`gscript.py:2365`), and the ladder is "VI->Block Diagram->Nodes[]" (`:2362`), i.e. `node_index` may
        well be an index into the TOP-LEVEL diagram's Nodes[] only. #10686 t0 IS wired. So the brief's literal
        call is EXPECTED to create nothing, and a DECLARED, bounded fallback sweep (R1/R2/R3 below) finds a
        terminal that does yield one. Every attempt is recorded; none is a judgement.
      - wire_indicators: the indicator must ALREADY EXIST and is selected BY LABEL; a branch creates NO new
        Wire object, so a wire count can never verify it (`gscript.py:1766-1774`) - which is also 37(e).
  * `build_d1_v0.move_in` `:318`, `owner_of` `:338`, `diag_index` `:357`.
  * `build_opstopfromnode_v0.walk` `:129` (node_labels + node_terms_uid per node).
  * `build_opconnectnested_v1.connect_nested_v1` `:418` - used ONLY as the ORDERED `Is Broken?` READER, via an
    IDEMPOTENT re-connect of the same source->sink pair (42(b), binding: the writing pass reads False on a
    mismatched connection, so `Is Broken?` is NEVER read in the pass that makes the connection).
  * `diag_s2_scaffold.fresh` `:156` / `Preload` `:168` / `file_facts` `:143`; `hash_probe.probe`;
    `bench_prep.labview_handles`.
  * PRIOR ART, read before writing: `tools/bench/case_out_probe.py` asked almost exactly this pair of routes
    (its header names them A and B) for a CASE frame in 2026-09-10. Its log settles nothing: the scratch was
    already at `ExecState` 0 before either route ran (`tools/bench/case_out_probe.log`, "== A: case + inner
    subVI ... ExecState 0"), so both routes raised the same "target BROKEN after wiring" and neither reading is
    attributable. This run starts from an `ExecState` 1 target, which is the whole difference.
Nothing new is built.

PREDICTION CONTRACT - every line below is a printed GATE, and **gates are REPORTED, not required** (the
34(j)/37(e) pattern): the READING is the deliverable and the run's rc must not depend on either route's
outcome. Only the file-safety gates are FATAL. A route that refuses is a READING, not a failure.
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                          FATAL
  T2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                              FATAL
  T3  each route's dated scratch is byte-identical to it at creation.                                  FATAL
  M1  the offline reading of `#3191` is printed (files answer it; no live read is needed).           REPORTED
  G0  `owner_of(#10686)` is read live on each scratch and its Diagram uid recorded.                 REPORTED
  G1  `#10686` t0 is resolved on each route's OWN live walk: named 'x .and. y?', is_source, wire 10799. REPORTED
  G2  a ControlTerminal was created by `create_indicator`, and its uid + OWNER DIAGRAM are recorded. REPORTED
  G3  the label LabVIEW gave that indicator was read from the front-panel label delta.               REPORTED
  G4  route B's `move_in` destination index was RE-RESOLVED immediately before the call (38(e)).      REPORTED
  G5  route B's ControlTerminal is re-read by uid after the move and its owner recorded.              REPORTED
  G6  each route's `wire_indicators` error/exception column is recorded VERBATIM.                     REPORTED
  G7  WIRED-TERMINAL COUNTS on the source terminal and on the ControlTerminal, before and after, per
      route - never a whole-VI `Wire` delta, which 37(e) proves cannot detect a cut.                  REPORTED
  G8  `#637`'s own terminal count and the whole-VI LoopTunnel count, before and after, per route.     REPORTED
  G9  `ExecState` before and after, per route.                                                       REPORTED
  G10 an ORDERED `Is Broken?` reading was taken in a SEPARATE SECOND PASS, never in the writing pass. REPORTED
  G11 each route's save attempt is recorded; `allow_broken` stays False, `gui_save` never called.     REPORTED
  G12 no live VI Server reference is left open.                                                      REPORTED
  T14 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are byte-unchanged at the end.                      FATAL

  py tools/bgrun.py --material --max-min 25 --log tools/bench/diag_s3a_ind_transport.log \
      -- py -u tools/bench/diag_s3a_ind_transport.py
"""
import contextlib
import io
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
from bench_prep import labview_handles                                             # noqa: E402
from build_d1_v0 import diag_index, owner_of, move_in                              # noqa: E402
from build_opstopfromnode_v0 import walk as WALK                                    # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s3a_ind_transport.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SRC_UID = 10686                 # the schedule `And` - GIVEN by the brief
SRC_TERM_NAME = "x .and. y?"
SRC_WIRE_PIN = 10799
LOOP11_UID = 637                # WhileLoop 1.1; its border objects are watched for new tunnels
DIAG686_UID = 686               # the diagram that holds #637 (37(h) context)
MOVE_POS = (2200, 5200)         # empty area of the destination diagram; position is not functional
CT_CLASS = "ControlTerminal"

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "Pre-decided 45(c)/(f): measure the two transport verbs S3a needs - create_indicator + "
                 "wire_indicators with the source INSIDE WhileLoop #637 (route A), versus the same after "
                 "move_in of the ControlTerminal into the source's own diagram (route B)",
     "source_given": {"node_uid": SRC_UID, "term_name": SRC_TERM_NAME, "wire_pin": SRC_WIRE_PIN,
                      "authority": "the brief / Pre-decided 45(c)"},
     "no_vi_was_run": True, "interprets_nothing": True, "no_new_op": True, "no_gui_action": True,
     "chooses_no_route": "which route S3a uses is a DESIGN decision reserved to judgement",
     "is_broken_protocol": "42(b) binding: Is Broken? is read ONLY in a separate ordered second pass "
                           "(an idempotent re-connect, wire_delta expected 0); docs/NAMES.md:902-911",
     "prior_art": "tools/bench/case_out_probe.py (2026-09-10) asked the same A/B pair on a CASE frame; its "
                  "log settles nothing because the scratch was already at ExecState 0 before either route",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "m1_node_3191": {}, "routes": [], "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` - the documented emitter (37(i)); the bold form is invisible to guard_peer.
    line = "  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else "")
    print(line.encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        raise Stop(name)
    return ok


def fact(line):
    facts.append(line)
    print(("  FACT  %s" % line).encode("ascii", "replace").decode("ascii"), flush=True)


def probe(tag, path):
    line = HASH(path)
    R["hash_probe"].append({"tag": tag, "line": line})
    fact("%s: %s" % (tag, line))
    return dict(kv.strip().split("=", 1) for kv in line.split(" | ")[1:])


def dump():
    R["gates"] = {"pass": len(passes), "fail": len(fails), "failing": fails}
    R["facts"] = facts
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


# ============================================================ M1: what `#3191` is, ANSWERED FROM THE FILES
def m1_offline():
    """`#3191` - class, function name, every terminal, and whether wire 3747 is produced there. Files only:
    `tools/bench/main_vi_nodeterms.json` (the terminal census) and `tools/bench/diagram_tree_main.json`
    (the structures index). No live read is needed and none is taken."""
    print("\n=================== M1  what `#3191` is - FILES ONLY", flush=True)
    rec = R["m1_node_3191"]
    nt = json.load(open(os.path.join(HERE, "main_vi_nodeterms.json"), encoding="utf-8"))
    tr = json.load(open(os.path.join(HERE, "diagram_tree_main.json"), encoding="utf-8"))
    rows, owner_diag = None, None
    for dk, entry in (nt["diagrams"].items() if isinstance(nt["diagrams"], dict)
                      else enumerate(nt["diagrams"])):
        for nd in (entry.get("nodes") or []):
            if nd.get("uid") == 3191:
                rows, owner_diag = nd["terms"], dk
    rec["nodeterms_diagram_key"] = owner_diag
    rec["terms"] = [{"i": t["i"], "name": t["name"], "is_source": bool(t["is_source"]), "wire": t["wire"]}
                    for t in (rows or [])]
    rec["structure_class"] = [k for k, v in (tr.get("structures") or {}).items() if 3191 in v]
    fact("M1 #3191 sits on nodeterms diagram key %r with %d terminals; structures index says class %r "
         "(diagram_tree_main.json[structures]) - it is a STRUCTURE, so it has NO function name"
         % (owner_diag, len(rec["terms"]), rec["structure_class"]))
    for t in rec["terms"]:
        fact("M1   #3191 t%-2d name=%-24r is_source=%-5s wire=%s" % (t["i"], t["name"], t["is_source"], t["wire"]))
    # who SOURCES wire 3747 and wire 3268, over the whole census
    prod = {}
    for w in (3747, 3268):
        prod[w] = []
        for dk, entry in (nt["diagrams"].items() if isinstance(nt["diagrams"], dict)
                          else enumerate(nt["diagrams"])):
            for nd in (entry.get("nodes") or []):
                for t in nd["terms"]:
                    if t["wire"] == w:
                        prod[w].append({"diagram_key": dk, "node_uid": nd["uid"], "i": t["i"],
                                        "name": t["name"], "is_source": bool(t["is_source"])})
    rec["wire_endpoints"] = prod
    for w in (3747, 3268):
        srcs = [e for e in prod[w] if e["is_source"]]
        fact("M1 wire %d: %d endpoints in the census, of which %d are SOURCES -> %r"
             % (w, len(prod[w]), len(srcs), srcs))
    t2 = next((t for t in rec["terms"] if t["i"] == 2), None)
    rec["t2_is_source"] = (t2 or {}).get("is_source")
    rec["wire3747_sources"] = [e for e in prod[3747] if e["is_source"]]
    rec["wire3268_sources"] = [e for e in prod[3268] if e["is_source"]]
    gate("M1 the offline reading of #3191 is printed (class, all terminals, the producers of w3747/w3268)",
         bool(rec["terms"]) and bool(rec["structure_class"]),
         "t2 is_source=%r; w3747 sources=%r" % (rec["t2_is_source"], rec["wire3747_sources"]))
    dump()


# ============================================================ live helpers
def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire", CT_CLASS):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                     # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    rec.setdefault("censuses", {})[tag] = c
    fact("class census [%s] %r" % (tag, c))
    return c


def read_exec_state(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def owner(rec, target, uid, tag=""):
    try:
        ow = owner_of(target, uid, strict=False)
    except Exception as e:                                                         # noqa: BLE001
        ow = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("owner_of", {})["%s#%s" % (tag, uid)] = ow
    fact("owner_of(#%s)%s = %r" % (uid, (" " + tag) if tag else "", ow))
    return ow


def terms_of(rec, target, diag_i, node_i, tag):
    """Targeted re-read of ONE node's terminals + its WIRED-TERMINAL COUNT (37(e): counts of wired terminals,
    never a whole-VI Wire delta)."""
    try:
        u, rows = g.node_terms_uid(target, diag_i, node_i)
        wired = sum(1 for r in rows if r["wire"])
        out = {"node_uid_readback": u, "n_terms": len(rows), "wired_terminals": wired,
               "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                          "wire": r["wire"]} for r in rows]}
    except Exception as e:                                                         # noqa: BLE001
        out = {"error": "%s: %s" % (type(e).__name__, str(e)[:160])}
    rec.setdefault("terminal_reads", {})[tag] = out
    fact("terminal read [%s] node_uid %r  n_terms %r  WIRED TERMINALS %r"
         % (tag, out.get("node_uid_readback"), out.get("n_terms"), out.get("wired_terminals")))
    return out


def op_indicators():
    rd = {}
    try:
        vi = g.op(CN1.OP)
        for k in ("UID", "Name", "UID 2", "Is Broken?"):
            try:
                rd[k] = vi.GetControlValue(k)
            except Exception as e:                                                 # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                         # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return rd


def ordered_is_broken(rec, target, sink_diag, sink_node, sink_term, src_diag, src_node, src_term, tag):
    """THE SEPARATE SECOND PASS (42(b)). An IDEMPOTENT re-connect of the SAME source->sink pair through
    OpConnectNested_v1, whose `Is Broken?` readout then necessarily describes the wire that already exists.
    `wire_delta` is expected 0. This is a READER here, not the writer of the connection."""
    buf = io.StringIO()
    out = {"tag": tag}
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, sink_diag, sink_node, sink_term,
                                     src_diag, src_node, src_term, V1_LABELS)
        out.update({"wire_delta": dw, "exec_state_returned_by_wrapper": es, "error_verbatim": err})
    except Exception as e:                                                         # noqa: BLE001
        out.update({"wire_delta": None, "exec_state_returned_by_wrapper": None,
                    "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    txt = buf.getvalue()
    if txt.strip():
        for ln in txt.rstrip().splitlines():
            print(("      [reader stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    out["op_stdout"] = txt.strip()
    out["op_indicators"] = op_indicators()
    out["is_broken_ordered"] = out["op_indicators"].get("Is Broken?")
    rec["ordered_is_broken"] = out
    fact("ORDERED `Is Broken?` [%s]: %r  (wire_delta %r, expected 0; op error column VERBATIM %r; "
         "readouts %r)" % (tag, out["is_broken_ordered"], out.get("wire_delta"),
                           out.get("error_verbatim"), out["op_indicators"]))
    return out


def make_indicator(rec, target, diag_i, src_node_i):
    """The DECLARED, bounded, mechanical indicator-creation rule. No judgement: every attempt is recorded and
    the FIRST that yields a new ControlTerminal wins.
      R1 the brief's literal call - create_indicator(target, <#10686's Nodes[] index on its own diagram>, 0).
         EXPECTED to yield nothing: `gscript.py:2365` says a WIRED terminal yields no control and t0 carries
         wire 10799, and `:2362` says the op's ladder is VI->Block Diagram->Nodes[], i.e. the TOP-LEVEL array.
      R2 the same index, terminals 1..2 (the rest of #10686's pane).
      R3 a sweep over node indices 0..11 x terminals 0..7, first hit wins.
    The indicator's DATA TYPE follows whatever terminal LabVIEW wired it to; the type is NOT readable over this
    COM path (36(c) settled `Terminal.DataType` as unavailable), so booleanness is REPORTED as an open item,
    never asserted. The transport question this run measures does not depend on it."""
    attempts = []
    for tag, n, t in ([("R1 brief literal", src_node_i, 0)]
                      + [("R2 same index t%d" % t, src_node_i, t) for t in (1, 2)]
                      + [("R3 sweep n%d t%d" % (n, t), n, t) for n in range(12) for t in range(8)]):
        fp0 = {l for _, l, _ in g.fp_labels(target)}
        ct0 = g.uids(target, CT_CLASS)
        new, err = [], None
        try:
            new = g.create_indicator(target, n, t)
        except Exception as e:                                                     # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
        labs = [l for _, l, _ in g.fp_labels(target) if l not in fp0]
        a = {"rule": tag, "node_index": n, "terminal_index": t,
             "new_control_terminals": [{"uid": o["uid"], "pos": o.get("pos")} for o in (new or [])],
             "new_fp_labels": labs, "exception": err,
             "control_terminal_count_before": len(ct0)}
        attempts.append(a)
        fact("create_indicator(%d, %d) [%s] -> new ControlTerminals %r, new FP labels %r, exception %r"
             % (n, t, tag, a["new_control_terminals"], labs, err))
        if new:
            a["chosen"] = True
            rec["indicator_attempts"] = attempts
            return a
        if len(attempts) >= 20:          # bounded: the sweep never runs away inside the bgrun deadline
            fact("the indicator-creation sweep stopped at its declared bound of 20 attempts with no hit")
            break
    rec["indicator_attempts"] = attempts
    return None


# ============================================================ one route
def run_route(route, do_move):
    rec = {"route": route, "moves_the_control_terminal_in": bool(do_move)}
    target = os.path.join(g.CLAUDEDEV, "DIAG_s3aind_%s_%s.vi" % (STAMP, route))
    rec["scratch"] = target
    print("\n=================== ROUTE %s  (move_in first = %s)  scratch %s"
          % (route, do_move, os.path.basename(target)), flush=True)
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("T3 the route-%s scratch at creation" % route, target)
    rec["scratch_at_creation"] = p
    gate("T3 the route-%s scratch is byte-identical to the S2 artefact" % route, p.get("md5") == S2_MD5,
         p.get("md5", "?"), fatal=True)

    with D.Preload("P-route-%s" % route):
        g.open_panel(target)
        time.sleep(1.0)
        census(rec, "before", target)
        rec["exec_state_before"] = read_exec_state(rec, "route %s BEFORE anything" % route, target)

        # ---------------- the source's ADDRESS, read live and never inherited (34(h))
        ow = owner(rec, target, SRC_UID, "the source node")
        src_diag_uid = ow[1] if isinstance(ow, (tuple, list)) and ow[0] == "Diagram" else None
        rec["source_diagram_uid"] = src_diag_uid
        gate("G0 [%s] owner_of(#%d) reads a Diagram uid" % (route, SRC_UID), src_diag_uid is not None, repr(ow))
        if src_diag_uid is None:
            fact("route %s: the source's owning diagram could not be read - nothing further is attempted. "
                 "That is the reading." % route)
            return rec
        sdiag = diag_index(target, src_diag_uid)
        rec["source_diagram_index"] = sdiag
        fact("Diagram #%s (the source's owner) reads Traverse index %d on this scratch" % (src_diag_uid, sdiag))

        w = WALK(target, sdiag, limit=120)
        rec["walk_n_nodes"] = len(w)
        fact("the walk of Diagram #%s returned %d nodes" % (src_diag_uid, len(w)))
        src = None
        if SRC_UID in w:
            ni, lab, rows = w[SRC_UID]
            rec["source_node"] = {"node_index": ni, "label": lab}
            row = next((r for r in rows if r["is_source"] and (r["name"] or "") == SRC_TERM_NAME), None)
            if row is not None:
                src = {"node_uid": SRC_UID, "node_index": ni, "label": lab, "term_index": row["i"],
                       "term_name": row["name"], "wire_before": row["wire"]}
            rec["source_terms_live"] = [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                                         "wire": r["wire"]} for r in rows]
        rec["source"] = src
        gate("G1 [%s] #%d t? %r is resolved live as a SOURCE carrying wire %d"
             % (route, SRC_UID, SRC_TERM_NAME, SRC_WIRE_PIN),
             bool(src) and src.get("wire_before") == SRC_WIRE_PIN, repr(src))

        # ---------------- #637's border objects, BEFORE
        d686 = diag_index(target, DIAG686_UID)
        w686 = WALK(target, d686, limit=60)
        rec["diagram_686_index"] = d686
        rec["walk_686_n_nodes"] = len(w686)
        i637 = w686[LOOP11_UID][0] if LOOP11_UID in w686 else None
        rec["loop_637_node_index"] = i637
        if i637 is not None:
            terms_of(rec, target, d686, i637, "#637 BEFORE")
        rec["loop_tunnels_before"] = rec["censuses"]["before"].get("LoopTunnel")

        # ---------------- the indicator
        print("\n--- %s: create_indicator, by the declared bounded rule" % route, flush=True)
        ind = make_indicator(rec, target, sdiag, (src or {}).get("node_index", 0))
        rec["indicator"] = ind
        ct_uid = (ind or {}).get("new_control_terminals", [{}])[0].get("uid") if ind else None
        label = (ind or {}).get("new_fp_labels") or []
        rec["control_terminal_uid"] = ct_uid
        rec["indicator_label"] = label[-1] if label else None
        gate("G2 [%s] a ControlTerminal was created and its uid recorded" % route, ct_uid is not None,
             "uid %r by rule %r" % (ct_uid, (ind or {}).get("rule")))
        gate("G3 [%s] the label LabVIEW gave the new indicator was read" % route,
             bool(rec["indicator_label"]), repr(rec["indicator_label"]))
        if ct_uid is not None:
            owner(rec, target, ct_uid, "the new ControlTerminal AS CREATED")
        if ct_uid is None:
            fact("route %s: no ControlTerminal exists, so neither wire_indicators nor the move is attempted. "
                 "That is the reading, reported as one." % route)
            census(rec, "after", target)
            return rec

        # ---------------- route B only: move_in FIRST
        if do_move:
            print("\n--- %s: move_in the ControlTerminal into the source's own diagram FIRST" % route,
                  flush=True)
            dest = diag_index(target, src_diag_uid)          # 38(e): RE-RESOLVED immediately before the call
            rec["move_dest_index_reresolved"] = dest
            rec["move_dest_index_matches_earlier_read"] = (dest == sdiag)
            gate("G4 [%s] the move_in destination index was re-resolved immediately before the call (38(e))"
                 % route, True, "index %r for Diagram #%s (earlier read %r)" % (dest, src_diag_uid, sdiag))
            try:
                echoed = move_in(target, ct_uid, dest, MOVE_POS)
                rec["move_in"] = {"echoed_uid": echoed, "exception": None}
            except Exception as e:                                                 # noqa: BLE001
                rec["move_in"] = {"echoed_uid": None,
                                  "exception": "%s: %s" % (type(e).__name__, str(e)[:250])}
            fact("move_in(ControlTerminal #%s -> Diagram index %d) = %r  (37(d): a move SEVERS every wire on "
                 "the moved object, in either order)" % (ct_uid, dest, rec["move_in"]))
            ow2 = owner(rec, target, ct_uid, "the ControlTerminal AFTER the move")
            rec["control_terminal_owner_after_move"] = ow2
            gate("G5 [%s] the ControlTerminal was re-read by uid after the move and its owner recorded" % route,
                 "ERROR" not in repr(ow2), repr(ow2))
            read_exec_state(rec, "route %s after the move_in" % route, target)

        # ---------------- WIRED-TERMINAL COUNTS, BEFORE the wiring (37(e))
        sdiag_now = diag_index(target, src_diag_uid)
        rec["source_diagram_index_before_wiring"] = sdiag_now
        w_now = WALK(target, sdiag_now, limit=140)
        src_i_now = w_now[SRC_UID][0] if SRC_UID in w_now else src["node_index"]
        rec["source_node_index_before_wiring"] = src_i_now
        terms_of(rec, target, sdiag_now, src_i_now, "source #%d BEFORE wiring" % SRC_UID)
        ct_i_now = w_now[ct_uid][0] if ct_uid in w_now else None
        rec["control_terminal_node_index_on_source_diagram"] = ct_i_now
        if ct_i_now is not None:
            terms_of(rec, target, sdiag_now, ct_i_now, "ControlTerminal #%s BEFORE wiring" % ct_uid)
        else:
            fact("the ControlTerminal #%s is NOT in the walk of the source's diagram (%d nodes) - on this "
                 "route it lives elsewhere, so its terminal is read after the wiring only if it appears"
                 % (ct_uid, len(w_now)))

        # ---------------- the WRITE: wire_indicators
        print("\n--- %s: wire_indicators (the WRITE). Is Broken? is NOT read in this pass (42(b))." % route,
              flush=True)
        rec["wire_indicators_call"] = {"node_index": src_i_now, "src_terms": [SRC_TERM_NAME],
                                       "indicator_names": [rec["indicator_label"]],
                                       "diagram_index": sdiag_now, "node_class": None}
        # the source node's traverse CLASS, resolved BY MEMBERSHIP, never guessed
        cls_found = None
        for cand in ("Function", "Comparison", "SubVI", "Primitive", "Node"):
            try:
                if SRC_UID in [o["uid"] for o in g.report_all(target, cand)]:
                    cls_found = cand
                    break
            except Exception as e:                                                # noqa: BLE001
                fact("report_all(%r) raised %s: %s" % (cand, type(e).__name__, str(e)[:80]))
        rec["source_traverse_class"] = cls_found
        fact("#%d's traverse class BY MEMBERSHIP = %r" % (SRC_UID, cls_found))
        cls_idx = None
        if cls_found:
            try:
                cls_idx = [o["uid"] for o in g.report_all(target, cls_found)].index(SRC_UID)
            except Exception:                                                      # noqa: BLE001
                cls_idx = None
        rec["source_class_traverse_index"] = cls_idx
        fact("#%d's index in report_all(%r) = %r; its Nodes[] index on its own diagram = %r. wire_indicators' "
             "`index` convention is exactly what this route measures, so BOTH are recorded and the CLASS "
             "index is the one passed (case_out_probe.py:54 passed a class-traverse index)."
             % (SRC_UID, cls_found, cls_idx, src_i_now))
        use_i = cls_idx if cls_idx is not None else src_i_now
        rec["wire_indicators_call"].update({"node_index_passed": use_i, "node_class": cls_found or "Function"})
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                dt = g.wire_indicators(target, use_i, [SRC_TERM_NAME], [rec["indicator_label"]],
                                       diagram_index=sdiag_now, node_class=(cls_found or "Function"))
            rec["wire_indicators_result"] = {"returned": dt, "error_verbatim": ""}
        except Exception as e:                                                      # noqa: BLE001
            rec["wire_indicators_result"] = {"returned": None,
                                             "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:400])}
        txt = buf.getvalue()
        if txt.strip():
            for ln in txt.rstrip().splitlines():
                print(("      [wi stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        gate("G6 [%s] wire_indicators' error/exception column is recorded VERBATIM" % route,
             "error_verbatim" in rec["wire_indicators_result"],
             repr(rec["wire_indicators_result"]))

        # ---------------- ExecState immediately after, BEFORE any Is Broken? read (42(b))
        rec["exec_state_after"] = read_exec_state(
            rec, "route %s IMMEDIATELY AFTER wire_indicators (before any Is Broken? read)" % route, target)
        gate("G9 [%s] ExecState recorded before and after" % route,
             "exec_state_before" in rec and "exec_state_after" in rec,
             "%r -> %r" % (rec.get("exec_state_before"), rec.get("exec_state_after")))

        # ---------------- WIRED-TERMINAL COUNTS, AFTER (37(e)); and the new wire uid, or its absence
        sdiag_after = diag_index(target, src_diag_uid)
        w_after = WALK(target, sdiag_after, limit=140)
        src_i_after = w_after[SRC_UID][0] if SRC_UID in w_after else src_i_now
        ta = terms_of(rec, target, sdiag_after, src_i_after, "source #%d AFTER wiring" % SRC_UID)
        ct_i_after = w_after[ct_uid][0] if ct_uid in w_after else None
        rec["control_terminal_node_index_after"] = ct_i_after
        ct_after = terms_of(rec, target, sdiag_after, ct_i_after,
                            "ControlTerminal #%s AFTER wiring" % ct_uid) if ct_i_after is not None else None
        srow = next((r for r in (ta.get("terms") or []) if r["name"] == SRC_TERM_NAME and r["is_source"]), None)
        rec["source_term_wire_after"] = (srow or {}).get("wire")
        rec["control_terminal_wire_after"] = ((ct_after or {}).get("terms") or [{}])[0].get("wire") \
            if ct_after else None
        rec["new_wire_uid_or_absence"] = rec["control_terminal_wire_after"]
        fact("WIRED-TERMINAL COUNTS (37(e)) source before %r -> after %r; ControlTerminal before %r -> after "
             "%r. Source term wire %r -> %r. ControlTerminal's terminal wire AFTER = %r (a BRANCH creates NO "
             "new Wire object, gscript.py:1766-1768, so this uid - not a Wire delta - is the evidence)."
             % ((rec.get("terminal_reads", {}).get("source #%d BEFORE wiring" % SRC_UID) or {})
                .get("wired_terminals"),
                ta.get("wired_terminals"),
                (rec.get("terminal_reads", {}).get("ControlTerminal #%s BEFORE wiring" % ct_uid) or {})
                .get("wired_terminals"),
                (ct_after or {}).get("wired_terminals"),
                (src or {}).get("wire_before"), rec["source_term_wire_after"],
                rec["control_terminal_wire_after"]))
        gate("G7 [%s] wired-terminal counts recorded on the source terminal and on the ControlTerminal, "
             "before and after" % route,
             ("source #%d BEFORE wiring" % SRC_UID) in rec.get("terminal_reads", {})
             and ("source #%d AFTER wiring" % SRC_UID) in rec.get("terminal_reads", {}),
             repr(sorted(rec.get("terminal_reads", {}).keys())))

        # ---------------- #637's border objects, AFTER
        c_after = census(rec, "after", target)
        d686b = diag_index(target, DIAG686_UID)
        w686b = WALK(target, d686b, limit=60)
        i637b = w686b[LOOP11_UID][0] if LOOP11_UID in w686b else None
        if i637b is not None:
            terms_of(rec, target, d686b, i637b, "#637 AFTER")
        b, a = (rec.get("terminal_reads", {}).get("#637 BEFORE") or {}), \
               (rec.get("terminal_reads", {}).get("#637 AFTER") or {})
        rec["loop_637_terms_before_after"] = (b.get("n_terms"), a.get("n_terms"))
        rec["loop_tunnels_before_after"] = (rec["censuses"]["before"].get("LoopTunnel"),
                                            c_after.get("LoopTunnel"))
        gate("G8 [%s] #637's terminal count and the whole-VI LoopTunnel count recorded before and after"
             % route, True, "#637 terms %r; LoopTunnel %r"
             % (rec["loop_637_terms_before_after"], rec["loop_tunnels_before_after"]))

        # ---------------- THE SEPARATE SECOND PASS: the ORDERED `Is Broken?` (42(b))
        print("\n--- %s: the SEPARATE ORDERED `Is Broken?` pass - an IDEMPOTENT re-connect of the same pair "
              "through OpConnectNested_v1, used here as a READER only. Every ExecState after this is SUSPECT."
              % route, flush=True)
        if ct_i_after is not None:
            ordered_is_broken(rec, target, sdiag_after, ct_i_after, 0, sdiag_after, src_i_after,
                              (src or {}).get("term_index", 0), "route %s" % route)
        else:
            rec["ordered_is_broken"] = {
                "not_taken": "the ControlTerminal is not addressable as (diagram, node) on the source's "
                             "diagram on this route, so the idempotent re-connect has no sink address. "
                             "That is a reading, not a failure."}
            fact("ORDERED `Is Broken?` NOT TAKEN on route %s: %s" % (route, rec["ordered_is_broken"]["not_taken"]))
        gate("G10 [%s] the ordered `Is Broken?` pass is recorded (taken, or why not), and it was NEVER read in "
             "the writing pass" % route, "ordered_is_broken" in rec, repr(rec.get("ordered_is_broken", {}))[:300])

        # ---------------- the save (M3)
        es_final = read_exec_state(rec, "route %s immediately before the save attempt (SUSPECT)" % route, target)
        size, serr = None, None
        if isinstance(es_final, int) and es_final == 1:
            try:
                size = g.save(target)        # allow_broken stays False; gui_save is NEVER called
            except Exception as e:                                                 # noqa: BLE001
                serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        else:
            serr = ("NOT ATTEMPTED: ExecState is %r and the brief permits a save only at ExecState 1. A route "
                    "that ends at 0 is a legitimate outcome, not a failure to hide." % (es_final,))
        rec["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr,
                       "allow_broken": False, "gui_save": False, "exec_state_before_save": es_final}
        fact("route %s g.save(scratch) returned %r; exception/reason VERBATIM %r (allow_broken False, "
             "gui_save never called)" % (route, size, serr))
        rec["save"]["file_after"] = D.file_facts("route %s scratch after the save attempt" % route, target)
        rec["save"]["identical_to_S2"] = (rec["save"]["file_after"].get("md5") == S2_MD5)
        fact("route %s artefact md5 == the S2 artefact's md5 ? %r  (True would mean NOTHING was written)"
             % (route, rec["save"]["identical_to_S2"]))
        gate("G11 [%s] the save attempt is recorded; allow_broken False, gui_save never called" % route,
             "save" in rec, repr(rec["save"].get("returned_bytes")))
        try:
            g.close_panel(target)
        except Exception as e:                                                     # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    return rec


def main():
    print("=== diag_s3a_ind_transport  %s   (Pre-decided 45(c)/(f); NO VI IS RUN, 34(f); no new op, no new "
          "device; no GUI; INTERPRETS NOTHING and CHOOSES NO ROUTE)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (44(e): ~30,000 are added per scripting run and ref_counts cannot see it; "
         "fresh-instance baseline ~31,500): %r" % R["handles"]["before"])

    m1_offline()

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # the restart the brief ORDERS, mechanically (44(e))
    D.fresh("T2b RESTART before the batch - ORDERED by 44(e), ~30,000 handles per run are unexplained")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    for route, do_move in (("A-nomove", False), ("B-movedin", True)):
        R["routes"].append(run_route(route, do_move))
        dump()

    print("\n--- THE TWO ROUTES SIDE BY SIDE, INTERPRETED BY NOBODY HERE", flush=True)
    fact("ROUTE COMPARISON: %r"
         % [{"route": r["route"],
             "control_terminal_uid": r.get("control_terminal_uid"),
             "indicator_label": r.get("indicator_label"),
             "created_by_rule": (r.get("indicator") or {}).get("rule"),
             "ct_owner_as_created": (r.get("owner_of") or {}).get(
                 "the new ControlTerminal AS CREATED#%s" % r.get("control_terminal_uid")),
             "ct_owner_after_move": r.get("control_terminal_owner_after_move"),
             "wire_indicators_error": (r.get("wire_indicators_result") or {}).get("error_verbatim"),
             "new_wire_uid_or_absence": r.get("new_wire_uid_or_absence"),
             "ExecState before -> after": (r.get("exec_state_before"), r.get("exec_state_after")),
             "Is Broken? (ordered, 2nd pass)": (r.get("ordered_is_broken") or {}).get("is_broken_ordered"),
             "637 terms before/after": r.get("loop_637_terms_before_after"),
             "LoopTunnel before/after": r.get("loop_tunnels_before_after"),
             "saved_bytes": (r.get("save") or {}).get("returned_bytes"),
             "artefact_identical_to_S2": (r.get("save") or {}).get("identical_to_S2")}
            for r in R["routes"]])
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                         # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
        try:
            dump()
        except Exception:                                                          # noqa: BLE001
            pass
        try:
            g.reset()
        except Exception:                                                          # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                          # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                          # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r, after the restart %r)"
             % (R["handles"].get("after"), R["handles"].get("before"), R["handles"].get("after_restart")))
        gate("G12 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            try:
                dd = probe("T14 %s after the run" % tag, path)
            except Exception as e:                                                 # noqa: BLE001
                print("  FAIL  T14 %s could not be re-probed: %s: %s" % (tag, type(e).__name__, e), flush=True)
                fails.append("T14 %s re-probe raised" % tag)
                rc = 1
                continue
            R.setdefault("untouched", {})[tag] = dd.get("md5")
            if not gate("T14 %s md5 unchanged" % tag, dd.get("md5") == pin, dd.get("md5", "?")):
                rc = 1
        try:
            dump()
        except Exception as e:                                                     # noqa: BLE001
            print("  FAIL  the readings JSON could not be written: %s: %s" % (type(e).__name__, e), flush=True)
            rc = 1
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== GATES ARE REPORTED, NOT REQUIRED - the READING is the deliverable (34(j)/37(e) pattern). "
              "A route that refuses is a reading, not a failure.", flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== NOTHING IS INTERPRETED HERE and NO ROUTE IS CHOSEN - that is the judgement session's "
              "(Pre-decided 45). NO VI WAS RUN (34(f)); no new op; no new device; no motor, no ASI, no "
              "camera, no GUI.", flush=True)
        sys.exit(rc)
