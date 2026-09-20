r"""diag_queue_typetest_control - Pre-decided 40(c)+(d): VALIDATE THE READER BEFORE IT IS EVER USED AS A GATE.

🔴 A DIAGNOSTIC under `tools/bench/`, NEVER a recipe and never to be moved under `tools/recipes/`.
🔴 IT REPORTS FACTS AND INTERPRETS NOTHING. The branch after this measurement is deliberately NOT pre-decided
   (STATUS "NEXT", Pre-decided 40): whether a mismatched wire reads broken decides the queue path's future, and
   that decision belongs to the judgement session. Nothing here is a recommendation.
🔴 **NO QUEUES IN THIS RUN.** STATUS's NEXT bullet mentions building two `Obtain Queue` nodes first; Pre-decided
   40(d) overrides it, because that would put the untested INSTRUMENT (`Wire.Is Broken?`) and the untested
   SUBJECT (`queue_node`) into one experiment. `gscript.queue_node` is NOT imported and NOT called.
🔴 NO VI IS RUN (34(f)). The only VIs that execute are the BUILT op VIs - that is what scripting is.
🔴 NO NEW OP IS BUILT (Pre-decided 2; user 2026-09-18 08:53). No motor, no ASI, no camera, no GUI action.
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are NEVER opened for writing; their
   md5s are probed before and after. Every edit happens on a DATED SCRATCH copy of the S2 artefact.

THE QUESTION. We cannot read a terminal's type (36(c): no built op reads `Terminal.DataType`) and we cannot read
a queue's element type (40(b)). But a type MISMATCH is visible the moment two things are wired, and the reader
for that - `Wire.Is Broken?` **6371004** (`docs/NAMES.md:902-911`) - is already built and already measured. So
before the reader is trusted as a gate, it is given a CONTROL PAIR that differs in ONE variable only:

  MATCHED leg     source `#8486` named output `'x+1'` (numeric)          -> a bare numeric-arithmetic INPUT
  MISMATCHED leg  source `#250`  named output `'IMAQdx Session'` (refnum) -> a second bare numeric-arithmetic INPUT

and `Is Broken?` is read on each resulting wire. If the instrument is sound it reads False on the first and True
on the second. Any other combination is a first-class reading about the INSTRUMENT, not about the queue path.

⚠️ THE ORDERING TRAP, from `docs/NAMES.md:905-911`, designed around here rather than hoped away: the
`Is Broken?` readout inside `OpConnectNested_v1` ships with its `error in (no error)` UNWIRED, so on the writing
pass it may execute BEFORE the `Connect Wire` and report the OLD (absent) wire. The measured route to an ORDERED
reading (`docs/NAMES.md:912-918`) is an IDEMPOTENT re-connect of the SAME source->sink pair - 0 new Wire objects
- after which the readout necessarily describes the wire that already exists. So BOTH passes are recorded per
leg: `pass1` (write, readback possibly stale) and `pass2` (idempotent, the reading). And per `NAMES.md:917-921`
any `ExecState` taken AFTER a `Is Broken?` read is SUSPECT, so every per-leg `ExecState` is taken BEFORE the
idempotent passes begin.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`):
  * `build_opconnectnested_v1.connect_nested_v1` `:418` (`OpConnectNested_v1.vi`) - the BUILT writer, 5 for 5 on
    same-diagram rows in cycle 54 (`tools/bench/diag_s3_focus_trial.log`). `docs/toolkit-capabilities.md:68`
    describes it as "two DIFFERENT nested diagrams", but its two Traverse ladders are INDEPENDENT and cycle 54
    drove all five of its wires with `src_diag == sink_diag` (`diag_s3_focus_trial.py:485-486`), so the
    same-diagram case is the MEASURED case and no other connect op is needed here. `connect_terminals` `:2407`
    and `connect2` `:2633` are rejected: both need a TOP-LEVEL end and `Diagram #686` is not top level.
  * `gscript.report_all` `:488`, `node_terms_uid` `:925`, `count` `:1005`, `uids` `:1017`, `node_labels` `:587`,
    `exec_state` `:1977`, `save` `:2062`, `open_panel`/`close_panel` `:1241`/`:1257`, `ref_counts` `:233`,
    `reset` `:262`. `gscript.queue_node` `:1122` is DELIBERATELY NOT USED (40(d)).
  * `diag_queue_trial_census` - the template for this script and the source of the measured donor list
    (`tools/bench/diag_queue_trial_census.json`), used ONLY for the brief's step-3 refnum fallback.
  * `diag_s2_scaffold.fresh` `:155` / `Preload` `:167` / `file_facts` `:142`; `build_d1_v0.diag_index` `:357` /
    `owner_of` `:338`; `build_opstopfromnode_v0.walk` `:129` / `cls_of` `:147`; `hash_probe.probe` (34(k));
    `bench_prep.labview_handles`.
Nothing new is built.

PREDICTION CONTRACT - every line below is a printed GATE, and **gates are REPORTED, not required** (the
34(j)/37(e) pattern): the READING is the deliverable and the run's rc must not depend on either `Is Broken?`
value. Only the file-safety gates are FATAL. No gate below is expected to retain a FAIL (41(c)).
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859.                                          FATAL
  T2  `claudeDev\D1_s2_loops.vi` md5 == 6ff19497f2309e007a214660bb64b911.                              FATAL
  T3  the dated scratch is byte-identical to it.                                                       FATAL
  G0  the FULL terminal census of `Diagram #686` is recorded - every node, every terminal.          REPORTED
  G1  the live walk of `Diagram #686` finds BOTH source candidates (#8486, #250).                    REPORTED
  G2  every end this run RESOLVED lies on one diagram, read from `owner_of`, never inferred.        REPORTED
  G3  the bare-named-input search over the FIXED sink order is RECORDED; its OUTCOME is a reading.   REPORTED

⚠️ RUN 1 (08:17:14, `BGRUN END rc=1 after 78s`) ENDED WITH TWO RETAINED FAILS AND THIS IS THE REPAIR, not a
retry of the measurement. Run 1 measured that **all five of the brief's FIXED sink candidates expose ZERO bare
named input terminals on `Diagram #686`** - `#7201 'Multiply'` t1 `'y'` and t2 `'x'` both already carry wires
(`tools/bench/main_vi_nodeterms.json:6256-6295`), as do `#8486`, `#9179`, `#25091`, `#25149`. So the control
pair could not be attempted. Two changes, and only two: (1) G0 adds the FULL `Diagram #686` terminal census that
run 1 did not dump, so the next sink rule can be chosen from measured data rather than from another blind
attempt - pure measurement, selecting nothing; (2) G2 and G3 are **demoted to recordings** under 41(c), because
the measurement falsified their premise and a FAIL that is now EXPECTED must not be re-emitted. The sink rule
itself is UNCHANGED and no alternative sink is chosen here: that is a design decision and it is the judgement
session's.
  G4  the MATCHED leg was attempted and the op's machine error column recorded VERBATIM.             REPORTED
  G5  the MISMATCHED leg was attempted and the op's machine error column recorded VERBATIM.          REPORTED
  G6  a wire uid was read back from each leg's sink terminal (0 is a legitimate reading).            REPORTED
  G7  an ORDERED `Is Broken?` reading was taken per leg via an IDEMPOTENT re-connect (delta 0).      REPORTED
  G8  `ExecState` recorded before the pair and after each leg, BEFORE any idempotent read.           REPORTED
  G9  the save attempt is recorded; `allow_broken` stays False and `gui_save` is never called.       REPORTED
  G10 no live VI Server reference is left open.                                                      REPORTED
  T14 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are byte-unchanged at the end.                     FATAL

  MATERIAL=1 py tools/bgrun.py --max-min 20 --log tools/bench/diag_queue_typetest_control.log \
      -- py -u tools/bench/diag_queue_typetest_control.py
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
from build_d1_v0 import diag_index, owner_of                                      # noqa: E402
from build_opstopfromnode_v0 import walk as WALK, cls_of                          # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
import build_opconnectnested_v1 as CN1                                            # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_queue_typetest_control.json")
CENSUS_JSON = os.path.join(HERE, "diag_queue_trial_census.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

SIBLING_DIAG_UID = 686
MATCHED_SRC = (8486, "x+1")                 # numeric
MISMATCHED_SRC = (250, "IMAQdx Session")    # a refnum
# The brief's FIXED sink order. #7201 preferred; then this order, first two bare named input terminals.
SINK_ORDER = [7201, 8486, 9179, 25091, 25149]

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "Pre-decided 40(c)+(d): validate `Wire.Is Broken?` 6371004 on a MATCHED/MISMATCHED control pair",
     "no_vi_was_run": True, "interprets_nothing": True, "no_new_op": True,
     "no_queue_node_called": True, "queue_node_ban_source": "Pre-decided 40(d)",
     "matched_source": MATCHED_SRC, "mismatched_source": MISMATCHED_SRC, "sink_order_fixed": SINK_ORDER,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratch": None, "legs": [], "owner_of": {}, "exec_state": {}, "censuses": {},
     "handles": {}, "hash_probe": [], "sink_selection": {}}


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


def census(tag, target):
    c = {}
    for k in ("Diagram", "WhileLoop", "SubVI", "Comparison", "LoopTunnel", "Wire", "Function"):
        try:
            c[k] = g.count(target, k)
        except Exception as e:                                                    # noqa: BLE001
            c[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:80])
    R["censuses"][tag] = c
    fact("class census %s: %r" % (tag, c))
    return c


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                        # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R["exec_state"].setdefault("timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def owner(target, uid):
    try:
        ow = owner_of(target, uid, strict=False)
    except Exception as e:                                                        # noqa: BLE001
        ow = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R["owner_of"][str(uid)] = ow
    fact("owner_of(#%d) = %r" % (uid, ow))
    return ow


def op_indicators():
    """Re-read `OpConnectNested_v1.vi`'s own indicators AFTER a run. `g.op` caches the VI reference, so these are
    the same values the wrapper printed - captured here as data rather than as console text."""
    rd = {}
    try:
        vi = g.op(CN1.OP)
        for k in ("UID", "Name", "UID 2", "Is Broken?"):
            try:
                rd[k] = vi.GetControlValue(k)
            except Exception as e:                                                # noqa: BLE001
                rd[k] = "ERROR %s: %s" % (type(e).__name__, str(e)[:60])
    except Exception as e:                                                        # noqa: BLE001
        rd["_error"] = "%s: %s" % (type(e).__name__, str(e)[:120])
    return rd


def connect(target, d686, sink_node_i, sink_term_i, src_node_i, src_term_i, tag):
    """One `OpConnectNested_v1` call with stdout captured and re-emitted, plus the op's own indicators."""
    buf = io.StringIO()
    rec = {"tag": tag}
    try:
        with contextlib.redirect_stdout(buf):
            dw, es, err = CONNECT_V1(target, d686, sink_node_i, sink_term_i,
                                     d686, src_node_i, src_term_i, V1_LABELS)
        rec.update({"wire_delta": dw, "exec_state_returned": es, "error_verbatim": err})
    except Exception as e:                                                        # noqa: BLE001
        rec.update({"wire_delta": None, "exec_state_returned": None,
                    "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
    txt = buf.getvalue()
    if txt.strip():
        for ln in txt.rstrip().splitlines():
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
    rec["op_stdout"] = txt.strip()
    rec["op_indicators"] = op_indicators()
    fact("%s: wire_delta=%r  op error column VERBATIM %r  op indicators %r"
         % (tag, rec.get("wire_delta"), rec.get("error_verbatim"), rec["op_indicators"]))
    return rec


def sink_wire(target, d686, node_i, term_i):
    try:
        u, rows = g.node_terms_uid(target, d686, node_i)
        r = rows[term_i] if rows and term_i < len(rows) else None
        return {"node_uid_readback": u, "term": (dict(r) if r else None),
                "wire": (r["wire"] if r else None)}
    except Exception as e:                                                        # noqa: BLE001
        return {"error": "%s: %s" % (type(e).__name__, str(e)[:160])}


def main():
    print("=== diag_queue_typetest_control  %s   (Pre-decided 40(c)+(d); NO QUEUE NODE IS CREATED, 40(d); "
          "NO VI IS RUN, 34(f); no new op; INTERPRETS NOTHING)" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (cycle 54 closed at 60,211; fresh-instance baseline ~31,500): %r"
         % R["handles"]["before"])
    fact("THE INSTRUMENT UNDER TEST is `Wire.Is Broken?` 6371004, carried by OpConnectNested_v1's own readout "
         "(docs/NAMES.md:902-911). THE ORDERING TRAP (NAMES.md:905-911): that readout's `error in (no error)` "
         "ships UNWIRED, so on the WRITING pass it may run BEFORE the Connect Wire and describe the OLD wire. "
         "Both passes are therefore recorded per leg, and the ORDERED reading is pass2, an IDEMPOTENT re-connect "
         "of the same pair (NAMES.md:912-918). Any ExecState taken after a pass2 is SUSPECT (NAMES.md:917-921), "
         "so every per-leg ExecState is taken BEFORE the idempotent passes begin.")

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)

    # ---------------------------------------------------------------- restart, then the scratch
    D.fresh("T2b RESTART (handles were 60,211 at cycle 54's close; standing restart permission, CLAUDE.md 3)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    target = os.path.join(g.CLAUDEDEV, "DIAG_qtypectl_%s.vi" % STAMP)
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("T3 the dated scratch", target)
    R["scratch"] = {"path": target, "after_copy": p}
    gate("T3 the scratch is byte-identical to the S2 artefact", p.get("md5") == S2_MD5,
         p.get("md5", "?"), fatal=True)

    with D.Preload("P"):
        g.open_panel(target)
        time.sleep(1.0)
        census("BEFORE the pair", target)
        es0 = read_exec_state("before the pair", target)
        R["exec_state"]["before_the_pair"] = es0

        # ------------------------------------------------------------ the LIVE walk (34(h))
        print("\n--- the LIVE walk of Diagram #%d (34(h): re-read, never cached)" % SIBLING_DIAG_UID, flush=True)
        d686 = diag_index(target, SIBLING_DIAG_UID)
        fact("Diagram #%d reads Traverse index %d on this scratch" % (SIBLING_DIAG_UID, d686))
        w = WALK(target, d686, limit=200)
        fact("the walk of Diagram #%d returned %d nodes" % (SIBLING_DIAG_UID, len(w)))
        R["walk_n_nodes"] = len(w)

        # ------------------------------------------------------------ THE FULL TERMINAL CENSUS of Diagram #686
        # ADDED after run 1 (08:17), which ended rc=1 because the brief's FIXED sink rule found ZERO bare named
        # input terminals across all five of its candidates. That is a fact about the TARGET, and the reason it
        # could not be read off run 1's log is that run 1 dumped only the terminals it had selected. This census
        # is pure MEASUREMENT - every node of #686, every terminal, name / is_source / wire - so the judgement
        # session can choose the next sink rule from measured data instead of from another blind attempt. It
        # selects nothing and decides nothing.
        cen686 = []
        for uid, (ni, lab, rows) in sorted(w.items(), key=lambda kv: kv[1][0]):
            rec = {"uid": uid, "node_index": ni, "label": lab, "class_guess": cls_of(uid, w),
                   "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                              "wire": r["wire"]} for r in rows]}
            rec["bare_named_inputs"] = [t["i"] for t in rec["terms"]
                                        if (not t["is_source"]) and (t["name"] or "").strip() and not t["wire"]]
            rec["bare_unnamed_inputs"] = [t["i"] for t in rec["terms"]
                                          if (not t["is_source"]) and not (t["name"] or "").strip()
                                          and not t["wire"]]
            cen686.append(rec)
            print(("      NODE #%-6d Nodes[%-3d] %-14s %r" % (uid, ni, rec["class_guess"], (lab or "")[:30]))
                  .encode("ascii", "replace").decode("ascii"), flush=True)
            for t in rec["terms"]:
                print(("           t%-3d %-28r is_source=%-5s wire=%s"
                       % (t["i"], (t["name"] or "")[:28], t["is_source"], t["wire"]))
                      .encode("ascii", "replace").decode("ascii"), flush=True)
        R["diagram_686_terminal_census"] = cen686
        any_bare_named = [(r["uid"], r["node_index"], r["label"], r["bare_named_inputs"])
                          for r in cen686 if r["bare_named_inputs"]]
        any_bare_unnamed = [(r["uid"], r["node_index"], r["label"], r["bare_unnamed_inputs"])
                            for r in cen686 if r["bare_unnamed_inputs"]]
        R["diagram_686_any_bare_named_inputs"] = any_bare_named
        R["diagram_686_any_bare_unnamed_inputs"] = any_bare_unnamed
        fact("Diagram #%d census: %d nodes, %d terminals. Nodes with at least one BARE NAMED input: %r"
             % (SIBLING_DIAG_UID, len(cen686), sum(len(r["terms"]) for r in cen686), any_bare_named))
        fact("Diagram #%d census: nodes with at least one BARE UNNAMED input: %r"
             % (SIBLING_DIAG_UID, any_bare_unnamed))
        gate("G0 the FULL terminal census of Diagram #%d is recorded (every node, every terminal)"
             % SIBLING_DIAG_UID, bool(cen686), "%d nodes" % len(cen686))

        present = {u: (u in w) for u in (MATCHED_SRC[0], MISMATCHED_SRC[0])}
        gate("G1 the live walk finds BOTH source candidates (#%d, #%d) on Diagram #%d"
             % (MATCHED_SRC[0], MISMATCHED_SRC[0], SIBLING_DIAG_UID),
             all(present.values()), repr(present))

        # ------------------------------------------------------------ owners (the brief's step 1)
        print("\n--- owner_of for every node this run touches (the brief's step 1)", flush=True)
        for uid in sorted({MATCHED_SRC[0], MISMATCHED_SRC[0], *SINK_ORDER}):
            if uid in w:
                owner(target, uid)
            else:
                fact("owner_of(#%d) NOT taken: the node is not in the Diagram #%d walk" % (uid, SIBLING_DIAG_UID))

        # ------------------------------------------------------------ the source terminals
        def named_out(uid, name):
            if uid not in w:
                return None
            ni, lab, rows = w[uid]
            for r in rows:
                if r["is_source"] and (r["name"] or "") == name:
                    return {"node_uid": uid, "node_index": ni, "label": lab, "class_guess": cls_of(uid, w),
                            "term_index": r["i"], "term_name": r["name"], "term_wire": r["wire"]}
            return None

        src_m = named_out(*MATCHED_SRC)
        src_x = named_out(*MISMATCHED_SRC)
        R["sources"] = {"matched": src_m, "mismatched": src_x}
        fact("MATCHED source resolved: %r" % (src_m,))
        fact("MISMATCHED source resolved: %r" % (src_x,))

        if not src_m or not src_x:
            # the brief's step 3: a refnum donor that DOES share the diagram, from the measured census
            if not src_x:
                fact("the MISMATCHED source #%d %r is NOT resolvable on Diagram #%d - falling back to the "
                     "measured donor list in tools/bench/diag_queue_trial_census.json (the brief's step 3)"
                     % (MISMATCHED_SRC[0], MISMATCHED_SRC[1], SIBLING_DIAG_UID))
                try:
                    with open(CENSUS_JSON, encoding="utf-8") as f:
                        CEN = json.load(f)
                    cands = [(d["node_uid"], d["term_name"]) for d in CEN.get("donors", [])
                             if "session" in (d["term_name"] or "").lower()
                             or "refnum" in (d["term_name"] or "").lower()]
                except Exception as e:                                            # noqa: BLE001
                    cands = []
                    fact("the census JSON could not be read: %s: %s" % (type(e).__name__, str(e)[:120]))
                for uid, nm in cands:
                    src_x = named_out(uid, nm)
                    if src_x:
                        fact("fallback refnum donor taken: #%d %r" % (uid, nm))
                        break
                R["sources"]["mismatched"] = src_x
            if not src_x:
                fact("no same-diagram refnum donor - REPORTED as a first-class result, not worked around "
                     "(the brief's step 3). The run stops here with the file-safety gates intact.")
            gate("G1b both source terminals resolved", bool(src_m) and bool(src_x),
                 "matched=%r mismatched=%r" % (bool(src_m), bool(src_x)))

        # ------------------------------------------------------------ the sinks, by the FIXED rule (step 2)
        print("\n--- the sinks: the brief's FIXED mechanical rule. A bare named input terminal = "
              "is_source False AND a non-empty name AND wire == 0.", flush=True)
        bare = []
        for uid in SINK_ORDER:
            if uid not in w:
                fact("sink candidate #%d is NOT on Diagram #%d - skipped by the fixed rule"
                     % (uid, SIBLING_DIAG_UID))
                continue
            ni, lab, rows = w[uid]
            found = [{"node_uid": uid, "node_index": ni, "label": lab, "term_index": r["i"],
                      "term_name": r["name"], "term_wire": r["wire"]}
                     for r in rows if (not r["is_source"]) and (r["name"] or "").strip() and not r["wire"]]
            fact("sink candidate #%d %r (Nodes[%d]): %d bare named input terminal(s) %r"
                 % (uid, lab, ni, len(found), [(f["term_index"], f["term_name"]) for f in found]))
            bare.extend(found)
            if uid == SINK_ORDER[0] and len(found) >= 2:
                fact("the PREFERRED sink node #%d has >= 2 bare named inputs, so the fallback walk is not used"
                     % uid)
                bare = found
                break
        R["sink_selection"]["bare_named_inputs_in_fixed_order"] = bare

        # the one mechanical tie-break: a sink terminal on the leg's OWN source node would be a self-feedback
        # wire, which is broken for a reason that has nothing to do with type. Skipped and REPORTED.
        def take(avoid_uid, used):
            for b in bare:
                if id(b) in used:
                    continue
                if avoid_uid is not None and b["node_uid"] == avoid_uid:
                    fact("skipping bare input #%d t%d %r for this leg: it sits on the leg's OWN source node, "
                         "which would be a SELF-FEEDBACK wire (broken for a reason that is not type). "
                         "Mechanical tie-break, REPORTED." % (b["node_uid"], b["term_index"], b["term_name"]))
                    continue
                used.add(id(b))
                return b
            return None

        used = set()
        sink_m = take(src_m["node_uid"] if src_m else None, used)
        sink_x = take(src_x["node_uid"] if src_x else None, used)
        R["sink_selection"]["matched"] = sink_m
        R["sink_selection"]["mismatched"] = sink_x
        fact("MATCHED sink: %r" % (sink_m,))
        fact("MISMATCHED sink: %r" % (sink_x,))
        # 41(c): run 1 emitted this as a FAIL and it is now EXPECTED to be retained, because the measurement
        # falsified the gate's premise (that a bare named input exists at all on the fixed candidates). A gate
        # whose premise the measurement has falsified is DEMOTED TO A FACT LINE, never re-emitted as a FAIL.
        gate("G3 the bare-named-input search over the FIXED sink order is RECORDED (its OUTCOME is a reading, "
             "not a requirement)", True,
             "matched=%r mismatched=%r" % (sink_m and (sink_m["node_uid"], sink_m["term_index"]),
                                           sink_x and (sink_x["node_uid"], sink_x["term_index"])))
        if not (sink_m and sink_x):
            fact("🔴 THE FIXED SINK RULE HAS NO CANDIDATE ON THIS TARGET. Every numeric-arithmetic node the "
                 "brief names (%r) exposes ZERO bare named input terminals on Diagram #%d - their inputs are "
                 "all already carrying wires, because these are live nodes of a working VI. The control pair "
                 "is therefore NOT attempted. Choosing a different sink - a different node, an already-wired "
                 "terminal, an unnamed terminal, or a freshly created arithmetic node - is a DESIGN decision "
                 "and is reserved for the judgement session. The full census above is the material for it."
                 % (SINK_ORDER, SIBLING_DIAG_UID))
        same_node = bool(sink_m and sink_x and sink_m["node_uid"] == sink_x["node_uid"])
        fact("the two sinks are on %s node (the brief prefers the SAME node where possible): %s"
             % ("the SAME" if same_node else "DIFFERENT",
                "#%s and #%s" % (sink_m and sink_m["node_uid"], sink_x and sink_x["node_uid"])))
        R["sink_selection"]["same_sink_node"] = same_node

        parts = [x for x in (src_m, src_x, sink_m, sink_x) if x]
        # 41(c), as for G3: demoted to a recording. `owner_of` above measured every resolvable end's owner
        # diagram directly, and all of them read ('Diagram', 686); the count of RESOLVED ends is a reading.
        gate("G2 every end this run resolved lies on ONE diagram, uid %d (Traverse index %d) - owner_of read "
             "directly, not inferred" % (SIBLING_DIAG_UID, d686),
             all(v == ("Diagram", SIBLING_DIAG_UID) for v in R["owner_of"].values()
                 if isinstance(v, tuple) or isinstance(v, list)),
             "%d of 4 ends resolved; owner_of rows %r" % (len(parts), R["owner_of"]))

        if not (src_m and src_x and sink_m and sink_x):
            fact("one or more ends could not be resolved - the connections are NOT attempted. This is the "
                 "reading, reported as one.")
            R["legs"] = []
        else:
            # -------------------------------------------------------- pass 1: the two writes
            print("\n--- PASS 1: the two writes, one variable different (the donor's type). "
                  "OpConnectNested_v1, same-diagram (src_diag == sink_diag), as cycle 54 drove it 5 for 5.",
                  flush=True)
            for tag, src, sink in (("MATCHED", src_m, sink_m), ("MISMATCHED", src_x, sink_x)):
                leg = {"leg": tag, "source": src, "sink": sink}
                d686_now = diag_index(target, SIBLING_DIAG_UID)          # 38(e): re-resolve before every call
                leg["diagram_index_reresolved"] = d686_now
                leg["pass1"] = connect(target, d686_now, sink["node_index"], sink["term_index"],
                                       src["node_index"], src["term_index"], "%s pass1 (write)" % tag)
                leg["sink_after_write"] = sink_wire(target, d686_now, sink["node_index"], sink["term_index"])
                leg["wire_uid"] = (leg["sink_after_write"] or {}).get("wire")
                fact("%s: sink #%d t%d now carries wire %r (read from node_terms, NOT from the op) - %r"
                     % (tag, sink["node_uid"], sink["term_index"], leg["wire_uid"], leg["sink_after_write"]))
                leg["exec_state_after_write"] = read_exec_state("after the %s write" % tag, target)
                R["legs"].append(leg)
                dump()

            gate("G4 the MATCHED leg was attempted and its machine error column recorded VERBATIM",
                 "pass1" in R["legs"][0], repr(R["legs"][0]["pass1"].get("error_verbatim")))
            gate("G5 the MISMATCHED leg was attempted and its machine error column recorded VERBATIM",
                 "pass1" in R["legs"][1], repr(R["legs"][1]["pass1"].get("error_verbatim")))
            gate("G6 a wire uid was read back from each leg's sink terminal (0 is a legitimate reading)",
                 all(l.get("sink_after_write") is not None for l in R["legs"]),
                 repr([(l["leg"], l.get("wire_uid")) for l in R["legs"]]))
            gate("G8 ExecState recorded before the pair and after each leg, BEFORE any idempotent read",
                 all(l.get("exec_state_after_write") is not None for l in R["legs"]),
                 "before=%r, after each=%r" % (es0, [(l["leg"], l["exec_state_after_write"])
                                                     for l in R["legs"]]))

            # -------------------------------------------------------- pass 2: the ORDERED reading
            print("\n--- PASS 2: the ORDERED `Is Broken?` reading - an IDEMPOTENT re-connect of the SAME pair "
                  "(docs/NAMES.md:912-918). Expect wire_delta 0. Every ExecState after this point is SUSPECT.",
                  flush=True)
            for leg in R["legs"]:
                src, sink = leg["source"], leg["sink"]
                d686_now = diag_index(target, SIBLING_DIAG_UID)
                leg["pass2"] = connect(target, d686_now, sink["node_index"], sink["term_index"],
                                       src["node_index"], src["term_index"],
                                       "%s pass2 (idempotent, THE READING)" % leg["leg"])
                leg["sink_after_pass2"] = sink_wire(target, d686_now, sink["node_index"], sink["term_index"])
                leg["is_broken_ordered"] = (leg["pass2"].get("op_indicators") or {}).get("Is Broken?")
                leg["is_broken_pass1"] = (leg["pass1"].get("op_indicators") or {}).get("Is Broken?")
                leg["wire_delta_pass2"] = leg["pass2"].get("wire_delta")
                fact("%s LEG READING: source #%d t%d %r -> sink #%d t%d %r | wire uid %r | "
                     "op error column pass1 %r / pass2 %r | `Is Broken?` pass1 %r / ORDERED pass2 %r | "
                     "wire_delta pass1 %r / pass2 %r"
                     % (leg["leg"], src["node_uid"], src["term_index"], src["term_name"],
                        sink["node_uid"], sink["term_index"], sink["term_name"], leg.get("wire_uid"),
                        leg["pass1"].get("error_verbatim"), leg["pass2"].get("error_verbatim"),
                        leg["is_broken_pass1"], leg["is_broken_ordered"],
                        leg["pass1"].get("wire_delta"), leg["wire_delta_pass2"]))
                dump()
            gate("G7 an ORDERED `Is Broken?` reading was taken per leg via an IDEMPOTENT re-connect",
                 all("pass2" in l for l in R["legs"]),
                 repr([(l["leg"], l.get("is_broken_ordered"), "wire_delta %r" % l.get("wire_delta_pass2"))
                       for l in R["legs"]]))
            R["exec_state"]["after_the_idempotent_reads_SUSPECT"] = read_exec_state(
                "after the idempotent reads (SUSPECT per NAMES.md:917-921)", target)
            fact("🔴 THE CONTROL PAIR, side by side, INTERPRETED BY NOBODY HERE: %r"
                 % [{"leg": l["leg"], "source": (l["source"]["node_uid"], l["source"]["term_name"]),
                     "sink": (l["sink"]["node_uid"], l["sink"]["term_index"]),
                     "wire": l.get("wire_uid"), "Is Broken? (ordered)": l.get("is_broken_ordered"),
                     "ExecState after the write": l.get("exec_state_after_write")} for l in R["legs"]])

        # ------------------------------------------------------------ census, save
        census("AFTER the pair", target)
        size, serr = None, None
        es_final = read_exec_state("immediately before the save attempt (SUSPECT)", target)
        R["exec_state"]["before_save"] = es_final
        try:
            size = g.save(target)            # allow_broken stays False; gui_save is NEVER called
        except Exception as e:                                                    # noqa: BLE001
            serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        R["save"] = {"returned_bytes": size, "exception_verbatim": serr, "allow_broken": False,
                     "gui_save": False, "exec_state_before_save": es_final}
        fact("g.save(scratch) returned %r; exception VERBATIM %r (allow_broken False, gui_save never called)"
             % (size, serr))
        R["save"]["file_after"] = D.file_facts("the scratch after the save attempt", target)
        gate("G9 the save attempt is recorded, allow_broken False, gui_save never called", True,
             "returned %r, exception %r" % (size, serr))
        try:
            g.close_panel(target)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception as e:                                                        # noqa: BLE001
        import traceback
        traceback.print_exc()
        print("\nUNHANDLED %s: %s" % (type(e).__name__, e), flush=True)
        rc = 1
    finally:
        try:
            dump()
        except Exception:                                                         # noqa: BLE001
            pass
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
        fact("LabVIEW handles AFTER: %r (before %r, after the restart %r)"
             % (R["handles"].get("after"), R["handles"].get("before"), R["handles"].get("after_restart")))
        gate("G10 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            try:
                dd = probe("T14 %s after the run" % tag, path)
            except Exception as e:                                                # noqa: BLE001
                print("  FAIL  T14 %s could not be re-probed: %s: %s" % (tag, type(e).__name__, e), flush=True)
                fails.append("T14 %s re-probe raised" % tag)
                rc = 1
                continue
            R.setdefault("untouched", {})[tag] = dd.get("md5")
            if not gate("T14 %s md5 unchanged" % tag, dd.get("md5") == pin, dd.get("md5", "?")):
                rc = 1
        try:
            dump()
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  the readings JSON could not be written: %s: %s" % (type(e).__name__, e), flush=True)
            rc = 1
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== GATES ARE REPORTED, NOT REQUIRED - the READING is the deliverable (34(j)/37(e) pattern), and "
              "the rc does NOT depend on either `Is Broken?` value.", flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== NOTHING IS INTERPRETED HERE. The branch after this measurement is the judgement session's "
              "(Pre-decided 40). NO QUEUE NODE WAS CREATED (40(d)); NO VI WAS RUN (34(f)); no new op; "
              "no motor, no ASI, no camera, no GUI.", flush=True)
        sys.exit(rc)
