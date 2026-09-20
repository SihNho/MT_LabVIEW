r"""diag_s3a_ind_transport2 - cycle 56, ATTEMPT 2 of the S3a transport measurement (Pre-decided 45(c)/(f)).

🔴🔴 **NEVER RUN. WRITTEN, THEN DISARMED BY A MEASUREMENT TAKEN BEFORE IT COULD BE LAUNCHED.** This file was
authored while attempt 1 was still in flight, on the assumption that attempt 1's zero hits were SILENT DECLINES
caused by a blind candidate set. They were not. Two of the 113 watchdog screenshots from attempt 1's own window
were then read - `%TEMP%\gscript_dialog_1789905146.png` and `…_1789905137.png` - and the first of them shows
`OpCreateIndicator_v0.vi`'s OWN BLOCK DIAGRAM with its ladder head labelled **`TopLvlDiag`**, raising
**Error 1055, "Object reference is invalid"**. So the op addresses the VI's TOP-LEVEL block diagram's `Nodes[]`
and CANNOT reach `#10686` or any of the 33 bare source terminals, all of which live on `Diagram #639`. This
script's repaired candidate list is drawn from exactly that diagram, so it would fail identically, 9 more times.
Launching it would be a third grind against a wall the machine has already photographed (CLAUDE.md, failure
budget = 2). It is kept on disk as the record of what was tried and why it was not run; the fix belongs to the
judgement session.

🔴 A DIAGNOSTIC under `tools/bench/`, NEVER a recipe. 🔴 IT INTERPRETS NOTHING AND CHOOSES NO ROUTE - that is
the judgement session's (the brief says so in as many words). 🔴 NO VI IS RUN (34(f)). 🔴 NO NEW OP, no new
device (Pre-decided 2; user 2026-09-18 08:53). No motor, no ASI, no camera, no GUI. Rig state 조립/ASSEMBLED.
🔴 The ORIGINAL, `D1_s1_copy.vi` and `D1_s2_loops.vi` are never opened for writing; md5s probed before/after.

WHY THERE IS AN ATTEMPT 2, AND EXACTLY WHAT CHANGED. Attempt 1
(`tools/bench/diag_s3a_ind_transport.{py,log,json}`, kept on disk unmodified) never reached either route: its
indicator-creation rule swept `create_indicator(n, t)` over n = 0,1,25 x t = 0..7 under a 20-attempt bound and
every single call returned **no ControlTerminal and no exception**. The rule's candidate set was BLIND - it
walked node INDICES rather than the terminals the machine says are eligible - and `gscript.py:2365` states the
eligibility condition outright: *"a wired terminal or an out-of-range index yields no control"*. On a VI at
`ExecState` 1 almost every terminal is wired, which is the same wall cycle 55's attempt-1 sink rule hit
(*"no bare input is ENTAILED by ExecState == 1"*). Attempt 1 also cost ~35 s per attempt because it called
`fp_labels` (200 controls) twice per attempt, so its 25-minute deadline expired inside route B's sweep.

THE THREE MECHANICAL REPAIRS (no design decision is taken in any of them):
  1. **The candidate set is MEASURED, not swept.** From THIS scratch's own live walk of the source's diagram,
     the eligible candidates are the terminals with `is_source == True` and `wire` falsy - a BARE SOURCE is what
     an indicator can be created from. They are tried in walk order, capped at 8, and the brief's literal call
     (`#10686` t0) is still tried FIRST and recorded, for the record, even though its terminal carries wire
     10799 and is therefore expected to yield nothing.
     Offline corroboration that the set is non-empty (`tools/bench/main_vi_nodeterms.json`, diagram key 43 =
     `Diagram #639`): **33 bare source terminals**, e.g. `#2136` t0 `'floor(x/y)'`, `#10969` t1 `'max value'`,
     `#6104` t1 `'subarray'`. Offline is corroboration only; the run uses its own live walk.
  2. **Detection is by `uids(target,'ControlTerminal')` delta** (one op call), and `fp_labels` is called ONCE
     after a hit to read the label LabVIEW assigned - not twice per attempt.
  3. **One walk of the source diagram per route.** The ControlTerminal's Nodes[] index is found by probing from
     the walk's end upward (newly created nodes go to the END of Nodes[], `gscript.py:2353-2356`), bounded to 6
     probes, and every read is uid-verified through `node_terms_uid`'s echoed uid (34(h): never by index alone).

THE QUESTION IS UNCHANGED, and the source is GIVEN by the brief, not chosen here: `#10686` t0 `'x .and. y?'`,
wire 10799, the every-25-frames schedule boolean (Pre-decided 45(c)); measured on this target as
`owner_of(#10686) = ('Diagram', 639)`, label `'And'`, Nodes[] index 25 of 73 (attempt 1's log).
  Route A (no move)  the ControlTerminal stays where `create_indicator` put it; `wire_indicators` is asked to
                     branch the nested source onto it BY LABEL, source addressed with `node_class` +
                     `diagram_index`.
  Route B (moved in) on a FRESH copy, `move_in` puts the ControlTerminal into the source's own diagram FIRST
                     (destination index RE-RESOLVED immediately before the call, 38(e)), then the same
                     `wire_indicators` call - now same-diagram.

WHAT IS REUSED - checked before writing a line: `gscript.create_indicator` `:2385`, `wire_indicators` `:1756`
(its contract: the indicator must ALREADY EXIST and is picked BY LABEL; a branch creates NO new Wire object, so
a wire count can never verify it - `gscript.py:1766-1774`, which is also 37(e)), `build_d1_v0.move_in` `:318` /
`owner_of` `:338` / `diag_index` `:357`, `build_opstopfromnode_v0.walk` `:129`,
`build_opconnectnested_v1.connect_nested_v1` `:418` used ONLY as the ORDERED `Is Broken?` reader via an
IDEMPOTENT re-connect (42(b), binding), `diag_s2_scaffold.fresh`/`Preload`/`file_facts`, `hash_probe.probe`,
`bench_prep.labview_handles`. PRIOR ART: `tools/bench/case_out_probe.py` (2026-09-10) asked this same A/B pair
on a CASE frame and its log settles nothing - its scratch was already at `ExecState` 0 before either route ran.
Nothing new is built.

PREDICTION CONTRACT - gates are REPORTED, not required (34(j)/37(e)); only the file-safety gates are FATAL. A
route that refuses is a READING, not a failure.
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                          FATAL
  T2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                              FATAL
  T3  each route's dated scratch is byte-identical to it at creation.                                  FATAL
  G0  `owner_of(#10686)` is read live per route and its Diagram uid recorded.                        REPORTED
  G1  `#10686` t0 resolves live as a SOURCE carrying wire 10799.                                     REPORTED
  G1b the live walk offers at least one BARE SOURCE terminal (is_source, wire 0).                    REPORTED
  G2  a ControlTerminal was created; its uid and OWNER DIAGRAM are recorded.                         REPORTED
  G3  the label LabVIEW gave it was read.                                                            REPORTED
  G4  route B's `move_in` destination index was RE-RESOLVED immediately before the call (38(e)).      REPORTED
  G5  route B's ControlTerminal is re-read BY UID after the move and its owner recorded.              REPORTED
  G6  each route's `wire_indicators` error/exception column is recorded VERBATIM.                     REPORTED
  G7  WIRED-TERMINAL COUNTS on the source terminal and on the ControlTerminal, before and after -
      never a whole-VI `Wire` delta, which 37(e) proves cannot detect a cut.                          REPORTED
  G8  `#637`'s terminal count and the whole-VI LoopTunnel count, before and after.                    REPORTED
  G9  `ExecState` before and after, per route.                                                        REPORTED
  G10 an ORDERED `Is Broken?` reading taken in a SEPARATE SECOND PASS, never in the writing pass.     REPORTED
  G11 each save attempt recorded; `allow_broken` stays False, `gui_save` never called.                REPORTED
  G12 no live VI Server reference left open.                                                         REPORTED
  T14 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi byte-unchanged at the end.                          FATAL

  py tools/bgrun.py --material --max-min 30 --log tools/bench/diag_s3a_ind_transport2.log \
      -- py -u tools/bench/diag_s3a_ind_transport2.py
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
OUT = os.path.join(HERE, "diag_s3a_ind_transport2.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SRC_UID = 10686
SRC_TERM_NAME = "x .and. y?"
SRC_WIRE_PIN = 10799
LOOP11_UID = 637
DIAG686_UID = 686
MOVE_POS = (2200, 5200)
CT_CLASS = "ControlTerminal"
MAX_CANDIDATES = 8
MAX_CT_PROBES = 6

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "attempt": 2,
     "supersedes": "tools/bench/diag_s3a_ind_transport.py (attempt 1: blind index sweep, 0 hits in 16 calls, "
                   "deadline expired in route B)",
     "question": "Pre-decided 45(c)/(f): measure the two transport verbs S3a needs - create_indicator + "
                 "wire_indicators with the source INSIDE WhileLoop #637 (route A), versus the same after "
                 "move_in of the ControlTerminal into the source's own diagram (route B)",
     "source_given": {"node_uid": SRC_UID, "term_name": SRC_TERM_NAME, "wire_pin": SRC_WIRE_PIN,
                      "authority": "the brief / Pre-decided 45(c)"},
     "no_vi_was_run": True, "interprets_nothing": True, "no_new_op": True, "no_gui_action": True,
     "chooses_no_route": "which route S3a uses is a DESIGN decision reserved to judgement",
     "is_broken_protocol": "42(b) binding: Is Broken? is read ONLY in a separate ordered second pass "
                           "(idempotent re-connect, wire_delta expected 0); docs/NAMES.md:902-911",
     "indicator_rule": "candidates are the BARE SOURCE terminals of the source's own live walk (is_source and "
                       "wire falsy), in walk order, capped at %d; the brief's literal #10686 t0 call is tried "
                       "first and recorded even though that terminal is wired (gscript.py:2365)"
                       % MAX_CANDIDATES,
     "type_caveat": "the indicator's DATA TYPE follows whatever terminal LabVIEW wires it to; Terminal.DataType "
                    "is unavailable over this COM path (36(c)), so booleanness is REPORTED as open, never "
                    "asserted. The transport reading does not depend on it.",
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "routes": [], "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
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


def census(rec, tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "LoopTunnel", "Wire", CT_CLASS):
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


def terms_of(rec, target, diag_i, node_i, tag, expect_uid=None):
    """Targeted re-read of ONE node's terminals + its WIRED-TERMINAL COUNT (37(e)). The echoed node uid is
    always reported, and compared with `expect_uid` when one is given (34(h): an index is never trusted)."""
    try:
        u, rows = g.node_terms_uid(target, diag_i, node_i)
        wired = sum(1 for r in rows if r["wire"])
        out = {"diagram_index": diag_i, "node_index": node_i, "node_uid_readback": u,
               "uid_matches_expectation": (None if expect_uid is None else (u == expect_uid)),
               "n_terms": len(rows), "wired_terminals": wired,
               "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                          "wire": r["wire"]} for r in rows]}
    except Exception as e:                                                         # noqa: BLE001
        out = {"error": "%s: %s" % (type(e).__name__, str(e)[:160])}
    rec.setdefault("terminal_reads", {})[tag] = out
    fact("terminal read [%s] node_uid %r (expected %r, matches %r)  n_terms %r  WIRED TERMINALS %r"
         % (tag, out.get("node_uid_readback"), expect_uid, out.get("uid_matches_expectation"),
            out.get("n_terms"), out.get("wired_terminals")))
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


def ordered_is_broken(rec, target, diag, sink_node, sink_term, src_node, src_term, tag):
    """THE SEPARATE SECOND PASS (42(b)): an IDEMPOTENT re-connect of the same pair through
    OpConnectNested_v1, whose `Is Broken?` readout then describes the wire that already exists. Reader only."""
    buf = io.StringIO()
    out = {"tag": tag, "protocol": "idempotent re-connect, wire_delta expected 0"}
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, diag, sink_node, sink_term, diag, src_node, src_term, V1_LABELS)
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
    fact("ORDERED `Is Broken?` [%s] = %r  (wire_delta %r, expected 0; op error column VERBATIM %r; readouts %r)"
         % (tag, out["is_broken_ordered"], out.get("wire_delta"), out.get("error_verbatim"),
            out["op_indicators"]))
    return out


def make_indicator(rec, target, diag_i, walk):
    """The REPAIRED, declared, mechanical rule - see the module docstring, repair 1. Returns the winning
    attempt dict or None. No judgement: the candidate order is the walk's order and the first hit wins."""
    cands = [("C0 the brief's literal call (#%d t0, wired - expected to yield nothing)" % SRC_UID,
              walk[SRC_UID][0], 0)] if SRC_UID in walk else []
    bare = []
    for uid, (ni, lab, rows) in walk.items():
        for r in rows:
            if r["is_source"] and not r["wire"]:
                bare.append((uid, ni, lab, r["i"], r["name"]))
    rec["bare_source_candidates_found"] = len(bare)
    rec["bare_source_candidates"] = [{"node_uid": u, "node_index": n, "label": l, "term_index": i,
                                      "term_name": nm} for u, n, l, i, nm in bare[:20]]
    fact("the live walk offers %d BARE SOURCE terminals (is_source True, wire falsy); the first %d are the "
         "candidate list, in walk order: %r"
         % (len(bare), min(MAX_CANDIDATES, len(bare)),
            [(u, "Nodes[%d]" % n, "t%d" % i, nm) for u, n, l, i, nm in bare[:MAX_CANDIDATES]]))
    gate("G1b the live walk offers at least one BARE SOURCE terminal", bool(bare), "%d found" % len(bare))
    for uid, ni, lab, ti, tname in bare[:MAX_CANDIDATES]:
        cands.append(("C bare source #%d %r Nodes[%d] t%d %r" % (uid, lab, ni, ti, tname), ni, ti))
    attempts = []
    for tag, n, t in cands:
        ct0 = g.uids(target, CT_CLASS)
        new, err = [], None
        try:
            new = g.create_indicator(target, n, t)
        except Exception as e:                                                     # noqa: BLE001
            err = "%s: %s" % (type(e).__name__, str(e)[:200])
        a = {"rule": tag, "node_index": n, "terminal_index": t, "exception": err,
             "control_terminal_count_before": len(ct0),
             "new_control_terminals": [{"uid": o["uid"], "pos": o.get("pos")} for o in (new or [])]}
        attempts.append(a)
        fact("create_indicator(Nodes[%d], t%d) [%s] -> new ControlTerminals %r, exception %r"
             % (n, t, tag, a["new_control_terminals"], err))
        if new:
            labs = [l for _, l, _ in g.fp_labels(target)]          # ONE fp_labels call, only on a hit
            a["fp_labels_after_hit_tail"] = labs[-6:]
            a["chosen"] = True
            rec["indicator_attempts"] = attempts
            return a
    rec["indicator_attempts"] = attempts
    fact("no candidate yielded a ControlTerminal in %d attempts - that is the reading" % len(attempts))
    return None


def find_node_index(target, diag_i, uid, walk_len):
    """Locate `uid`'s Nodes[] index on `diag_i` by probing from the walk's end upward: newly created nodes go
    to the END of Nodes[] (`gscript.py:2353-2356`). Bounded, uid-verified, never guessed."""
    for n in range(max(0, walk_len - 1), walk_len + MAX_CT_PROBES):
        try:
            u, _rows = g.node_terms_uid(target, diag_i, n)
        except Exception:                                                          # noqa: BLE001
            continue
        if u == uid:
            return n
        if not u:
            break
    return None


def run_route(route, do_move):
    rec = {"route": route, "moves_the_control_terminal_in": bool(do_move)}
    target = os.path.join(g.CLAUDEDEV, "DIAG_s3aind2_%s_%s.vi" % (STAMP, route))
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

        ow = owner(rec, target, SRC_UID, "the source node")
        sdiag_uid = ow[1] if isinstance(ow, (tuple, list)) and ow[0] == "Diagram" else None
        rec["source_diagram_uid"] = sdiag_uid
        gate("G0 [%s] owner_of(#%d) reads a Diagram uid" % (route, SRC_UID), sdiag_uid is not None, repr(ow))
        if sdiag_uid is None:
            fact("route %s: the source's owning diagram could not be read - nothing further attempted." % route)
            return rec
        sdiag = diag_index(target, sdiag_uid)
        rec["source_diagram_index"] = sdiag
        fact("Diagram #%s (the source's owner) reads Traverse index %d on this scratch" % (sdiag_uid, sdiag))

        walk = WALK(target, sdiag, limit=120)
        rec["walk_n_nodes"] = len(walk)
        fact("the walk of Diagram #%s returned %d nodes" % (sdiag_uid, len(walk)))
        src = None
        if SRC_UID in walk:
            ni, lab, rows = walk[SRC_UID]
            row = next((r for r in rows if r["is_source"] and (r["name"] or "") == SRC_TERM_NAME), None)
            if row is not None:
                src = {"node_uid": SRC_UID, "node_index": ni, "label": lab, "term_index": row["i"],
                       "term_name": row["name"], "wire_before": row["wire"]}
        rec["source"] = src
        gate("G1 [%s] #%d %r resolves live as a SOURCE carrying wire %d"
             % (route, SRC_UID, SRC_TERM_NAME, SRC_WIRE_PIN),
             bool(src) and src.get("wire_before") == SRC_WIRE_PIN, repr(src))

        # #637's border objects, BEFORE
        d686 = diag_index(target, DIAG686_UID)
        w686 = WALK(target, d686, limit=40)
        rec["diagram_686_index"] = d686
        rec["walk_686_n_nodes"] = len(w686)
        i637 = w686[LOOP11_UID][0] if LOOP11_UID in w686 else None
        rec["loop_637_node_index"] = i637
        if i637 is not None:
            terms_of(rec, target, d686, i637, "#637 BEFORE", expect_uid=LOOP11_UID)

        # the indicator
        print("\n--- %s: create_indicator, by the REPAIRED measured candidate rule" % route, flush=True)
        ind = make_indicator(rec, target, sdiag, walk)
        rec["indicator"] = ind
        ct_uid = (ind or {}).get("new_control_terminals", [{}])[0].get("uid") if ind else None
        rec["control_terminal_uid"] = ct_uid
        tail = (ind or {}).get("fp_labels_after_hit_tail") or []
        rec["indicator_label"] = tail[-1] if tail else None
        gate("G2 [%s] a ControlTerminal was created and its uid recorded" % route, ct_uid is not None,
             "uid %r by rule %r" % (ct_uid, (ind or {}).get("rule")))
        gate("G3 [%s] the label LabVIEW gave the new indicator was read" % route,
             bool(rec["indicator_label"]),
             "%r (fp_labels tail %r)" % (rec["indicator_label"], tail))
        if ct_uid is not None:
            owner(rec, target, ct_uid, "the new ControlTerminal AS CREATED")
        if ct_uid is None:
            fact("route %s: no ControlTerminal exists, so neither wire_indicators nor the move is attempted. "
                 "That is the reading, reported as one." % route)
            census(rec, "after", target)
            return rec

        # route B only: move_in FIRST
        if do_move:
            print("\n--- %s: move_in the ControlTerminal into the source's own diagram FIRST" % route,
                  flush=True)
            dest = diag_index(target, sdiag_uid)         # 38(e): RE-RESOLVED immediately before the call
            rec["move_dest_index_reresolved"] = dest
            rec["move_dest_index_matches_earlier_read"] = (dest == sdiag)
            gate("G4 [%s] the move_in destination index was re-resolved immediately before the call (38(e))"
                 % route, True, "index %r for Diagram #%s (earlier read %r)" % (dest, sdiag_uid, sdiag))
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
            gate("G5 [%s] the ControlTerminal was re-read BY UID after the move and its owner recorded" % route,
                 "ERROR" not in repr(ow2), repr(ow2))
            read_exec_state(rec, "route %s after the move_in" % route, target)

        # WIRED-TERMINAL COUNTS, BEFORE the wiring (37(e))
        sdiag_now = diag_index(target, sdiag_uid)
        rec["source_diagram_index_before_wiring"] = sdiag_now
        src_i = src["node_index"] if src else 0
        terms_of(rec, target, sdiag_now, src_i, "source #%d BEFORE wiring" % SRC_UID, expect_uid=SRC_UID)
        ct_i = find_node_index(target, sdiag_now, ct_uid, len(walk))
        rec["control_terminal_node_index_on_source_diagram"] = ct_i
        if ct_i is not None:
            terms_of(rec, target, sdiag_now, ct_i, "ControlTerminal #%s BEFORE wiring" % ct_uid,
                     expect_uid=ct_uid)
        else:
            fact("the ControlTerminal #%s is NOT addressable as a Nodes[] index on the source's diagram "
                 "(probed %d..%d) - on this route it lives elsewhere"
                 % (ct_uid, max(0, len(walk) - 1), len(walk) + MAX_CT_PROBES - 1))

        # THE WRITE
        print("\n--- %s: wire_indicators (the WRITE). `Is Broken?` is NOT read in this pass (42(b))." % route,
              flush=True)
        cls_found = None
        for cand in ("Function", "Comparison", "SubVI", "Node"):
            try:
                if SRC_UID in [o["uid"] for o in g.report_all(target, cand)]:
                    cls_found = cand
                    break
            except Exception as e:                                                # noqa: BLE001
                fact("report_all(%r) raised %s: %s" % (cand, type(e).__name__, str(e)[:80]))
        rec["source_traverse_class"] = cls_found
        cls_idx = None
        if cls_found:
            try:
                cls_idx = [o["uid"] for o in g.report_all(target, cls_found)].index(SRC_UID)
            except Exception:                                                      # noqa: BLE001
                cls_idx = None
        rec["source_class_traverse_index"] = cls_idx
        fact("#%d's traverse class BY MEMBERSHIP = %r; its index in report_all(%r) = %r; its Nodes[] index on "
             "its own diagram = %r. `wire_indicators`' index convention is part of what this route measures, "
             "so BOTH are recorded and the CLASS index is the one passed (case_out_probe.py:54 passed a "
             "class-traverse index)." % (SRC_UID, cls_found, cls_found, cls_idx, src_i))
        use_i = cls_idx if cls_idx is not None else src_i
        rec["wire_indicators_call"] = {"node_index_passed": use_i, "node_class": cls_found or "Function",
                                      "src_terms": [SRC_TERM_NAME],
                                      "indicator_names": [rec["indicator_label"]],
                                      "diagram_index": sdiag_now}
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
             "error_verbatim" in rec["wire_indicators_result"], repr(rec["wire_indicators_result"]))

        rec["exec_state_after"] = read_exec_state(
            rec, "route %s IMMEDIATELY AFTER wire_indicators (before any Is Broken? read)" % route, target)
        gate("G9 [%s] ExecState recorded before and after" % route,
             "exec_state_before" in rec and "exec_state_after" in rec,
             "%r -> %r" % (rec.get("exec_state_before"), rec.get("exec_state_after")))

        # WIRED-TERMINAL COUNTS, AFTER (37(e))
        sdiag_after = diag_index(target, sdiag_uid)
        ta = terms_of(rec, target, sdiag_after, src_i, "source #%d AFTER wiring" % SRC_UID,
                      expect_uid=SRC_UID)
        ct_i_after = ct_i if ct_i is not None else find_node_index(target, sdiag_after, ct_uid, len(walk))
        rec["control_terminal_node_index_after"] = ct_i_after
        ct_after = terms_of(rec, target, sdiag_after, ct_i_after,
                            "ControlTerminal #%s AFTER wiring" % ct_uid,
                            expect_uid=ct_uid) if ct_i_after is not None else None
        srow = next((r for r in (ta.get("terms") or []) if r["name"] == SRC_TERM_NAME and r["is_source"]), None)
        rec["source_term_wire_after"] = (srow or {}).get("wire")
        rec["control_terminal_wire_after"] = (((ct_after or {}).get("terms") or [{}])[0].get("wire")
                                             if ct_after else None)
        rec["new_wire_uid_or_absence"] = rec["control_terminal_wire_after"]
        before_src = rec.get("terminal_reads", {}).get("source #%d BEFORE wiring" % SRC_UID) or {}
        before_ct = rec.get("terminal_reads", {}).get("ControlTerminal #%s BEFORE wiring" % ct_uid) or {}
        fact("WIRED-TERMINAL COUNTS (37(e)): source %r -> %r; ControlTerminal %r -> %r. Source term wire %r -> "
             "%r. The ControlTerminal's terminal wire AFTER = %r (a BRANCH creates NO new Wire object, "
             "gscript.py:1766-1768, so this uid - not a Wire delta - is the evidence)."
             % (before_src.get("wired_terminals"), ta.get("wired_terminals"),
                before_ct.get("wired_terminals"), (ct_after or {}).get("wired_terminals"),
                (src or {}).get("wire_before"), rec["source_term_wire_after"],
                rec["control_terminal_wire_after"]))
        gate("G7 [%s] wired-terminal counts recorded on the source terminal and on the ControlTerminal, before "
             "and after" % route,
             bool(before_src) and bool(ta), repr(sorted(rec.get("terminal_reads", {}).keys())))

        # #637 AFTER + tunnels
        c_after = census(rec, "after", target)
        if i637 is not None:
            terms_of(rec, target, diag_index(target, DIAG686_UID), i637, "#637 AFTER", expect_uid=LOOP11_UID)
        b = rec.get("terminal_reads", {}).get("#637 BEFORE") or {}
        a = rec.get("terminal_reads", {}).get("#637 AFTER") or {}
        rec["loop_637_terms_before_after"] = (b.get("n_terms"), a.get("n_terms"))
        rec["loop_637_wired_before_after"] = (b.get("wired_terminals"), a.get("wired_terminals"))
        rec["loop_tunnels_before_after"] = (rec["censuses"]["before"].get("LoopTunnel"),
                                            c_after.get("LoopTunnel"))
        gate("G8 [%s] #637's terminal count and the LoopTunnel count recorded before and after" % route, True,
             "#637 terms %r wired %r; LoopTunnel %r" % (rec["loop_637_terms_before_after"],
                                                        rec["loop_637_wired_before_after"],
                                                        rec["loop_tunnels_before_after"]))

        # THE SEPARATE SECOND PASS
        print("\n--- %s: the SEPARATE ORDERED `Is Broken?` pass - an IDEMPOTENT re-connect of the same pair "
              "through OpConnectNested_v1, READER ONLY. Every ExecState after this is SUSPECT." % route,
              flush=True)
        if ct_i_after is not None and src is not None:
            ordered_is_broken(rec, target, sdiag_after, ct_i_after, 0, src_i, src["term_index"],
                              "route %s" % route)
        else:
            rec["ordered_is_broken"] = {
                "not_taken": "the ControlTerminal is not addressable as (diagram, node) on the source's "
                             "diagram on this route, so the idempotent re-connect has no sink address. That "
                             "is a reading, not a failure."}
            fact("ORDERED `Is Broken?` NOT TAKEN on route %s: %s"
                 % (route, rec["ordered_is_broken"]["not_taken"]))
        gate("G10 [%s] the ordered `Is Broken?` pass is recorded (taken, or why not) and was NEVER read in the "
             "writing pass" % route, "ordered_is_broken" in rec,
             repr(rec.get("ordered_is_broken", {}))[:300])

        # the save (M3)
        es_final = read_exec_state(rec, "route %s immediately before the save attempt (SUSPECT)" % route, target)
        size, serr = None, None
        if isinstance(es_final, int) and es_final == 1:
            try:
                size = g.save(target)       # allow_broken stays False; gui_save is NEVER called
            except Exception as e:                                                 # noqa: BLE001
                serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        else:
            serr = ("NOT ATTEMPTED: ExecState is %r and the brief permits a save only at ExecState 1. A route "
                    "that ends at 0 is a legitimate outcome, not a failure to hide." % (es_final,))
        rec["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr,
                       "allow_broken": False, "gui_save": False, "exec_state_before_save": es_final}
        fact("route %s g.save(scratch) returned %r; exception/reason VERBATIM %r (allow_broken False, gui_save "
             "never called)" % (route, size, serr))
        rec["save"]["file_after"] = D.file_facts("route %s scratch after the save attempt" % route, target)
        rec["save"]["identical_to_S2"] = (rec["save"]["file_after"].get("md5") == S2_MD5)
        fact("route %s artefact md5 == the S2 artefact's md5 ? %r  (True would mean NOTHING was written to it)"
             % (route, rec["save"]["identical_to_S2"]))
        gate("G11 [%s] the save attempt is recorded; allow_broken False, gui_save never called" % route,
             "save" in rec, repr(rec["save"].get("returned_bytes")))
        try:
            g.close_panel(target)
        except Exception as e:                                                     # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    return rec


def main():
    print("=== diag_s3a_ind_transport2  %s   (ATTEMPT 2; Pre-decided 45(c)/(f); NO VI IS RUN, 34(f); no new "
          "op, no new device; no GUI; INTERPRETS NOTHING and CHOOSES NO ROUTE)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (44(e): ~30,000 added per scripting run, ref_counts cannot see it; fresh "
         "baseline ~31,500): %r" % R["handles"]["before"])
    fact("ATTEMPT 1 (`tools/bench/diag_s3a_ind_transport.{py,log,json}`, kept on disk) got 0 ControlTerminals "
         "in 16 blind index-sweep calls, every one with NO exception, and its deadline expired inside route B. "
         "Its M1 reading is complete and is NOT repeated here.")

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    D.fresh("T2b RESTART before the batch - ORDERED by 44(e)")
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
             "Is Broken? (ordered 2nd pass)": (r.get("ordered_is_broken") or {}).get("is_broken_ordered"),
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
