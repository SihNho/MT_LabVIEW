r"""diag_movein_set - MEASUREMENT A of cycle 52's final round: can the 1.5 set move as ONE unit?

A DIAGNOSTIC, never a recipe (it lives under tools/bench/, not tools/recipes/). It answers three questions
with readings, and CHOOSES NOTHING: the S3 boundary is the judgement session's.

  A1  Does `move_in` take more than one node per call? - read from the PYTHON side and from the OP VI itself.
  A2  Does a wire INTERNAL to the moved set survive the move? - the real pair
      `#3529 '- Inc (PgDn)' t0` -> `#48 '-Inc reference' t0`, wire **4833**
      (`tools/bench/d1_rewire_sources.json:1919-1945`), moved into ONE new empty loop body, with a
      terminal-by-terminal and whole-VI-Wire-census reading BEFORE, BETWEEN and AFTER the calls.
  A3  `ExecState` after the move (in-instance under `Preload`, 34(l)), whether `g.save()` is reachable, md5.

🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 No new op (Pre-decided 2). No motor, no ASI, no camera, no GUI action.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are NEVER modified: every edit lands
   on a DATED SCRATCH copy of the S2 artefact, unique to this run (CLAUDE.md scratch rule).

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `build_d1_v0.move_in` `:318` - the BUILT mover (OpMoveIn_v0.vi). NOT in `tools/gscript.py`: gscript has only
    `move_out` `:2674` and `move_object` `:2299`. Nothing new is written for the move.
  * `build_d1_v0.owner_of` `:338` / `diag_index` `:357` - owner and Traverse index by uid.
  * `build_opstopfromnode_v0.walk` `:129` - the BUILT per-diagram terminal census (node_labels + node_terms_uid).
  * `gscript.node_terms_uid` `:925` - per-terminal {name, is_source, wire} + the node's own uid, with its four
    per-property error columns. This is the terminal-by-terminal instrument A2 asks for.
  * `build_opwiresource_v5` (`OpWireSource_v5.vi`, INDEX row 43, 12/12) + `diag_movein_p1_break.read_term` `:82`
    - a WIRE's `Terms[]` with, per terminal, Is Source?, the reciprocal wire and the OWNER's class/uid. This is
    how "did wire 4833 survive" is answered from the WIRE's side as well as the nodes' side.
  * `diag_s2_scaffold` `fresh` `:155` / `Preload` `:167` / `file_facts` `:142` / `read_state` `:343` /
    `try_save` `:351` - cycle 50's measured harness. Importing it runs no build.
  * `bench_prep.labview_handles`; `hash_probe.probe` (34(k), read-only md5/sha256/size).
Nothing new is built.

PREDICTION CONTRACT (each line is a printed GATE; a FAIL that is a READING is marked non-fatal and expected)
  P1  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859.                                        FATAL
  P2  `claudeDev\D1_s2_loops.vi` md5 6ff19497f2309e007a214660bb64b911 BEFORE the copy.                   FATAL
  P3  the dated scratch is byte-identical to it.                                                         FATAL
  P4  A1: `OpMoveIn_v0.vi` exposes the uid control `UID 3`, and its value round-trips as a SCALAR
      integer, not an array => one node per call.                                                        FATAL
  P5  baseline census on the scratch: WhileLoop 6, Diagram 173, Wire 1905 (the verified S2 numbers).      FATAL
  P6  #48 is on `Diagram #686` with 7 terminals carrying a wire; #3529 is on `Diagram #686` and its
      terminal 0 `- Inc (PgDn)` carries wire 4833.                                                   non-fatal
  P7  wire 4833 read from the WIRE side has exactly one source terminal, owner uid 3529.             non-fatal
  P8  after move 1 (#3529 into the body) the readings are recorded; NO outcome is predicted.        REPORTED
  P9  after move 2 (#48 into the same body) the readings are recorded; NO outcome is predicted.     REPORTED
  P10 the verdict line for wire 4833 is one of SURVIVED / SEVERED / RECREATED-UNDER-A-NEW-UID.       REPORTED
  P11 A3: ExecState after both moves, in-instance with the ORIGINAL preloaded (34(l)).               REPORTED
  P12 A3: `g.save()` with the DEFAULT allow_broken=False; `gui_save` is NEVER called. Whether it is
      reachable is the READING, not a requirement.                                                   REPORTED
  P13 no live VI Server reference is left open.                                                     non-fatal
  P14 the ORIGINAL's md5 is unchanged at the end; so are D1_s1_copy.vi and D1_s2_loops.vi.               FATAL

  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_movein_set.log \
      -- py -u tools/bench/diag_movein_set.py
"""
import json
import os
import shutil
import sys
import time

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:                                                             # noqa: BLE001
        pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
for _p in (os.path.join(ROOT, "tools"), os.path.join(ROOT, "tools", "bench"),
           os.path.join(ROOT, "tools", "recipes")):
    sys.path.insert(0, _p)
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import move_in, owner_of, diag_index, UID_LABEL                  # noqa: E402
from build_opstopfromnode_v0 import walk as WALK                                  # noqa: E402
from build_opwiresource_v5 import OP as OP_WS, MAP_OUT as MAP_WS                  # noqa: E402
from diag_movein_p1_break import read_term                                        # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"           # STATUS owner_c52m1, verified 23/0
S2_SIZE = 475707
STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_moveinset_%s.vi" % STAMP)
OPIN = os.path.join(g.CLAUDEDEV, "OpMoveIn_v0.vi")
OUT = os.path.join(HERE, "diag_movein_set.json")

SIBLING_DIAG_UID = 686
SINK_UID = 48                    # ASI_adjust focus-subvi.vi
SRC_UID = 3529                   # control reference `- Inc (PgDn)`, d1_rewire_sources.json:1919-1945
WIRE_UID = 4833                  # #3529 t0 -> #48 t0 `-Inc reference`
# The three S2 loops, by the labels the S2 recipe printed (tools/bench/stage_d1_s2_loops.log:47/61/75).
S2_LOOPS = {"a": {"loop": 23032, "body": 23058, "at": (2600, 2600)},
            "b": {"loop": 10170, "body": 23166, "at": (2600, 3400)},
            "c": {"loop": 23041, "body": 23405, "at": (2600, 4200)}}
USE_LOOP = "a"                   # A2 needs ONE body; which one is arbitrary and is REPORTED, not chosen for meaning
BASELINE = {"Diagram": 173, "WhileLoop": 6, "SubVI": 97, "Comparison": 17, "LoopTunnel": 135, "Wire": 1905}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "measurement": "A (move_in as a SET)",
     "no_vi_was_run": True, "chooses_nothing": True,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5}, "scratch": {"path": SCRATCH},
     "A0": {}, "A1": {}, "A2": {"stages": []}, "A3": {}, "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
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


def terms_by_uid(tag, target, uid):
    """Terminal-by-terminal reading of ONE node, addressed by uid and re-resolved at the call site (34(h)):
    owner -> Traverse index -> that diagram's walk -> the node's Nodes[] index -> `node_terms_uid` rows."""
    rec = {"tag": tag, "uid": uid, "owner_class": None, "owner_uid": None, "diagram_index": None,
           "node_index": None, "rows": None, "error": None}
    try:
        cls, own = owner_of(target, uid)
        rec["owner_class"], rec["owner_uid"] = cls, own
        di = diag_index(target, own)
        rec["diagram_index"] = di
        w = WALK(target, di, limit=80)
        if uid not in w:
            rec["error"] = ("#%d is NOT in AbstractDiagram.Nodes[] of its owner Diagram #%s (walk saw %d nodes)"
                            % (uid, own, len(w)))
        else:
            ni, label, rows = w[uid]
            rec["node_index"], rec["label"] = ni, label
            rec["rows"] = [{"i": r["i"], "name": r["name"], "is_source": r["is_source"], "wire": r["wire"],
                            "name_err": r["name_err"], "src_err": r["src_err"], "conn_err": r["conn_err"],
                            "wire_err": r["wire_err"]} for r in rows]
    except Exception as e:                                                        # noqa: BLE001
        rec["error"] = "%s: %s" % (type(e).__name__, e)
    R["A2"].setdefault("node_reads", []).append(rec)
    if rec["rows"] is None:
        fact("TERMS %s #%d: NOT READ - %s" % (tag, uid, rec["error"]))
    else:
        wired = [(r["i"], r["name"], r["wire"]) for r in rec["rows"] if r["wire"]]
        fact("TERMS %s #%d (owner %s #%s, Diagram index %s, Nodes[%s], label %r): %d terminals, %d carry a wire"
             % (tag, uid, rec["owner_class"], rec["owner_uid"], rec["diagram_index"], rec["node_index"],
                rec.get("label"), len(rec["rows"]), len(wired)))
        for r in rec["rows"]:
            print(("        t%-2d %-28r src=%-5s wire=%-6s errs(n/s/c/w)=%d/%d/%d/%d"
                   % (r["i"], (r["name"] or "")[:28], r["is_source"], r["wire"], r["name_err"], r["src_err"],
                      r["conn_err"], r["wire_err"])).encode("ascii", "replace").decode("ascii"), flush=True)
    return rec


def wire_side(tag, target, wire_uid, ws_vi, ws_labels):
    """The WIRE's own Terms[] (OpWireSource_v5): per terminal Is Source?, reciprocal wire, owner class/uid."""
    rows = []
    for i in range(8):
        r = read_term(ws_vi, ws_labels, target, wire_uid, i)
        if r["errs"] and r["owner_uid"] == 0 and not r["is_source"]:
            break
        rows.append(r)
    rec = {"tag": tag, "wire": wire_uid, "n_terms": len(rows), "rows": rows}
    R["A2"].setdefault("wire_reads", []).append(rec)
    srcs = [r for r in rows if r["is_source"] and r["recip_wire"] == wire_uid]
    fact("WIRE %s w%d: %d terminal(s) read; sources-that-point-back %s"
         % (tag, wire_uid, len(rows), [(r["owner_class"], r["owner_uid"]) for r in srcs]))
    return rec


def census(tag, target):
    c = {k: g.count(target, k) for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire")}
    R["A2"].setdefault("censuses", {})[tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


def wire_present(target, wire_uid):
    return wire_uid in {o["uid"] for o in g.report_all(target, "Wire")}


def main():
    print("=== diag_movein_set  %s   (MEASUREMENT A; NO VI IS RUN, 34(f); no new op)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])

    # ---------------------------------------------------------------- A0 (files only, zero LabVIEW)
    R["A0"] = {
        "loop_labels_from": "tools/bench/stage_d1_s2_loops.log:47,61,75 (the S2 recipe's own FACT lines)",
        "a": S2_LOOPS["a"], "b": S2_LOOPS["b"], "c": S2_LOOPS["c"],
        "mapping_to_plan_rows_1_1__1_5": "searched docs/ for 23032 / 10170 / 23041 - see the summary"}
    fact("A0 the S2 recipe labelled the loops: a = WhileLoop #23032 (body #23058, at 2600,2600); "
         "b = WhileLoop #10170 (body #23166, at 2600,3400); c = WhileLoop #23041 (body #23405, at 2600,4200)")

    o = probe("P1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("P1 the ORIGINAL exists and its md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("P2 the S2 artefact BEFORE the copy", S2_ARTEFACT)
    gate("P2 D1_s2_loops.vi md5 == %s and size == %d B" % (S2_MD5, S2_SIZE),
         s.get("md5") == S2_MD5 and s.get("size") == str(S2_SIZE),
         "md5 %s size %s" % (s.get("md5"), s.get("size")))

    D.fresh("P2b")
    fact("handles after the restart: %r" % labview_handles())
    shutil.copy2(S2_ARTEFACT, SCRATCH)
    t = probe("P3 the dated scratch", SCRATCH)
    gate("P3 the scratch is byte-identical to the S2 artefact", t.get("md5") == S2_MD5, t.get("md5", "?"))

    # ---------------------------------------------------------------- A1: the mover's signature
    print("\n--- A1: does `move_in` take more than one node per call?", flush=True)
    R["A1"]["python_side"] = {
        "in_gscript": False,
        "gscript_has": ["move_out(target, diagram_index, node_index, position)  # gscript.py:2674",
                        "move_object(target, cls, index, position)              # gscript.py:2299"],
        "definition": "build_d1_v0.move_in(target, uid, dest_diagram_index, position)  # build_d1_v0.py:318",
        "uid_parameter": "a single `int(uid)` written to the op control %r (build_d1_v0.py:332)" % UID_LABEL,
        "returns": "int(vi.GetControlValue('UID')) - ONE uid echoed back (build_d1_v0.py:335)"}
    fact("A1 python side: `move_in` is NOT in tools/gscript.py (which has only move_out :2674 / move_object "
         ":2299). It is build_d1_v0.py:318 `move_in(target, uid, dest_diagram_index, position)` and writes ONE "
         "int to the op control %r (:332), echoing ONE uid back (:335)." % UID_LABEL)
    ctls = []
    try:
        opvi = g.op(OPIN)
        for lab in [x[1] for x in g.fp_labels(OPIN, max_n=60)]:
            if not lab:
                continue
            try:
                v = opvi.GetControlValue(lab)
            except Exception as e:                                                # noqa: BLE001
                ctls.append({"label": lab, "value_type": "UNREADABLE", "note": str(e)[:60]})
                continue
            ctls.append({"label": lab, "value_type": type(v).__name__,
                         "is_sequence": isinstance(v, (list, tuple)), "repr": repr(v)[:60]})
    except Exception as e:                                                        # noqa: BLE001
        R["A1"]["op_read_error"] = "%s: %s" % (type(e).__name__, e)
        fact("A1 op-side read FAILED: %s: %s" % (type(e).__name__, e))
    R["A1"]["op_controls"] = ctls
    for c in ctls:
        print(("      OPCTL %-28r type=%-10s seq=%-5s %s"
               % (c["label"][:28], c["value_type"], c.get("is_sequence"), c.get("repr", "")))
              .encode("ascii", "replace").decode("ascii"), flush=True)
    uidc = [c for c in ctls if c["label"] == UID_LABEL]
    gate("P4 A1: OpMoveIn_v0.vi exposes %r and its value is a SCALAR, not a sequence => ONE node per call"
         % UID_LABEL, bool(uidc) and not uidc[0].get("is_sequence"),
         "control record %r" % (uidc[:1],))

    ws_labels = None
    with open(MAP_WS, encoding="utf-8") as f:
        ws_labels = json.load(f)

    with D.Preload("A"):
        g.open_panel(SCRATCH)                       # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        c0 = census("BEFORE any edit", SCRATCH)
        gate("P5 baseline census == the verified S2 numbers %r" % BASELINE,
             all(c0[k] == v for k, v in BASELINE.items()), repr(c0))

        # ------------------------------------------------------------ A2 BEFORE
        print("\n--- A2 BEFORE the moves: #%d and #%d, terminal by terminal" % (SINK_UID, SRC_UID), flush=True)
        b_sink = terms_by_uid("BEFORE", SCRATCH, SINK_UID)
        b_src = terms_by_uid("BEFORE", SCRATCH, SRC_UID)
        ws = g.op(OP_WS)
        b_wire = wire_side("BEFORE", SCRATCH, WIRE_UID, ws, ws_labels)
        R["A2"]["wire_present_before"] = wire_present(SCRATCH, WIRE_UID)
        fact("wire %d present in the whole-VI Wire list BEFORE: %s" % (WIRE_UID, R["A2"]["wire_present_before"]))
        n_wired_sink = len([r for r in (b_sink["rows"] or []) if r["wire"]])
        gate("P6 #%d is on Diagram #%s with 7 wired terminals; #%d t0 %r carries wire %d"
             % (SINK_UID, b_sink["owner_uid"], SRC_UID, "- Inc (PgDn)", WIRE_UID),
             b_sink["owner_uid"] == SIBLING_DIAG_UID and n_wired_sink == 7
             and any(r["wire"] == WIRE_UID for r in (b_src["rows"] or [])),
             "sink owner %s wired %d; src rows %r" % (b_sink["owner_uid"], n_wired_sink,
                                                      [(r["i"], r["name"], r["wire"])
                                                       for r in (b_src["rows"] or [])][:4]), fatal=False)
        srcs = [r for r in b_wire["rows"] if r["is_source"] and r["recip_wire"] == WIRE_UID]
        gate("P7 wire %d has exactly ONE source terminal and its owner uid is %d" % (WIRE_UID, SRC_UID),
             len(srcs) == 1 and srcs[0]["owner_uid"] == SRC_UID,
             "sources %r" % [(r["owner_class"], r["owner_uid"]) for r in srcs], fatal=False)

        # ------------------------------------------------------------ A2: the two calls
        body_uid = S2_LOOPS[USE_LOOP]["body"]
        loop_uid = S2_LOOPS[USE_LOOP]["loop"]
        R["A2"]["destination"] = {"loop_label": USE_LOOP, "loop_uid": loop_uid, "body_diagram_uid": body_uid,
                                  "note": "this body holds the S2 scaffold Comparison; it is otherwise empty"}
        R["A2"]["order"] = ["move 1 = the SOURCE node #%d" % SRC_UID, "move 2 = the SINK node #%d" % SINK_UID]
        fact("A2 order: A1 says ONE node per call, so TWO successive calls - move 1 = the SOURCE #%d, move 2 = "
             "the SINK #%d, both into the body Diagram #%d of loop %s (WhileLoop #%d)"
             % (SRC_UID, SINK_UID, body_uid, USE_LOOP, loop_uid))

        for step, (uid, at) in enumerate(((SRC_UID, (60, 260)), (SINK_UID, (60, 380))), start=1):
            print("\n--- A2 move %d of 2: #%d -> body Diagram #%d at %r" % (step, uid, body_uid, at), flush=True)
            bi = diag_index(SCRATCH, body_uid)                       # re-read immediately before use (34(h))
            stage = {"step": step, "moved_uid": uid, "body_diagram_uid": body_uid, "body_diagram_index": bi,
                     "position": list(at)}
            try:
                echoed = move_in(SCRATCH, uid, bi, at)
                stage["move_in_echoed_uid"] = echoed
                fact("move %d: move_in(#%d -> Diagram #%d [index %d] at %r) echoed uid %r"
                     % (step, uid, body_uid, bi, at, echoed))
            except Exception as e:                                                # noqa: BLE001
                stage["move_in_error"] = "%s: %s" % (type(e).__name__, e)
                fact("move %d RAISED %s: %s" % (step, type(e).__name__, e))
            stage["census_after"] = census("AFTER move %d" % step, SCRATCH)
            stage["wire_present_after"] = wire_present(SCRATCH, WIRE_UID)
            fact("wire %d present in the whole-VI Wire list AFTER move %d: %s"
                 % (WIRE_UID, step, stage["wire_present_after"]))
            stage["sink"] = terms_by_uid("AFTER move %d" % step, SCRATCH, SINK_UID)
            stage["src"] = terms_by_uid("AFTER move %d" % step, SCRATCH, SRC_UID)
            stage["wire"] = wire_side("AFTER move %d" % step, SCRATCH, WIRE_UID, ws, ws_labels)
            R["A2"]["stages"].append(stage)

        # ------------------------------------------------------------ A2: the verdict on wire 4833
        print("\n--- A2 verdict on wire %d" % WIRE_UID, flush=True)
        last = R["A2"]["stages"][-1]
        src_rows = last["src"]["rows"] or []
        sink_rows = last["sink"]["rows"] or []
        src_t0 = next((r for r in src_rows if r["i"] == 0), None)
        sink_t0 = next((r for r in sink_rows if r["i"] == 0), None)
        src_w = (src_t0 or {}).get("wire") or 0
        sink_w = (sink_t0 or {}).get("wire") or 0
        if last["wire_present_after"] and src_w == WIRE_UID and sink_w == WIRE_UID:
            verdict = "SURVIVED"
        elif src_w and sink_w and src_w == sink_w and src_w != WIRE_UID:
            verdict = "RECREATED-UNDER-A-NEW-UID (w%d)" % src_w
        else:
            verdict = "SEVERED"
        R["A2"]["verdict"] = {"wire": WIRE_UID, "verdict": verdict, "src_t0_wire": src_w, "sink_t0_wire": sink_w,
                              "wire_uid_still_in_the_VI": last["wire_present_after"],
                              "wire_delta": last["census_after"]["Wire"] - c0["Wire"]}
        fact("P10 VERDICT wire %d after BOTH nodes moved into one body: **%s** - #%d t0 wire %r, #%d t0 wire %r, "
             "uid %d still present in the VI: %s, whole-VI Wire %d -> %d (delta %+d)"
             % (WIRE_UID, verdict, SRC_UID, src_w, SINK_UID, sink_w, WIRE_UID, last["wire_present_after"],
                c0["Wire"], last["census_after"]["Wire"], last["census_after"]["Wire"] - c0["Wire"]))
        gate("P10 the verdict for wire %d is recorded (REPORTED, never a requirement): %s" % (WIRE_UID, verdict),
             True, "", fatal=False)

        # ------------------------------------------------------------ A3
        print("\n--- A3: ExecState in-instance under Preload (34(l)), then ONE save attempt", flush=True)
        es = D.read_state("A3_after_both_moves_in_instance_preloaded", SCRATCH)
        R["A3"]["exec_state_after_moves"] = es
        gate("P11 A3 ExecState after both moves = %r (1 = runnable, 0 = broken) - REPORTED" % es, True,
             "", fatal=False)
        sv = D.try_save("moveinset", SCRATCH)
        R["A3"]["save"] = sv
        R["A3"]["save_reachable"] = sv["exception"] is None and bool(sv["returned_bytes"])
        gate("P12 A3 g.save() reachable with allow_broken=False (gui_save NEVER called): %s - REPORTED"
             % R["A3"]["save_reachable"], True,
             "returned %r exception %r" % (sv["returned_bytes"], sv["exception"]), fatal=False)
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    probe("A3 the scratch on disk, final", SCRATCH)
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at the first FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
        try:
            g.reset()
        except Exception:                                                         # noqa: BLE001
            pass
        refs = None
        try:
            refs = g.ref_counts()
        except Exception:                                                         # noqa: BLE001
            pass
        R["ref_counts_end"] = refs
        try:
            R["handles"]["after"] = labview_handles()
        except Exception:                                                         # noqa: BLE001
            R["handles"]["after"] = None
        print("\n--- close-out", flush=True)
        fact("refs at end: %r" % (refs,))
        fact("LabVIEW handles AFTER: %r (before %r)" % (R["handles"].get("after"), R["handles"].get("before")))
        gate("P13 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        untouched = True
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            d = probe("P14 %s after the run" % tag, path)
            R.setdefault("untouched", {})[tag] = d.get("md5")
            if d.get("md5") != pin:
                untouched = False
                gate("P14 %s md5 unchanged" % tag, False, "%s != %s" % (d.get("md5"), pin), fatal=False)
                rc = 1
            else:
                gate("P14 %s md5 unchanged" % tag, True, d.get("md5", "?"), fatal=False)
        R["untouched_all"] = untouched
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== NO VI WAS RUN (34(f)); no new op; no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
