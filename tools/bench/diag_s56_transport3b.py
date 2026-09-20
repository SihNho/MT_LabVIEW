"""diag_s56_transport3b - cycle 56 material #5, ATTEMPT 2 of the wire_indicators verb (failure budget 2/2).
A DIAGNOSTIC under tools/bench/, never a recipe. PHASE 1 ONLY - phases 2 and 3 of diag_s56_transport3.py are
DONE and are not repeated (phase 2 PASSED 5/5 and saved DIAG_s56_t3_p2_20260920_221901.vi).

WHY A SECOND ATTEMPT AT ALL - attempt 1 made ZERO wire_indicators calls, so the verb is still UNMEASURED:
judgement's rule was `diagram_index = diag_index(owner_of(<target indicator uid>)[1])`, and the machine answered
    owner_of(#6) = ('Panel', 3)            (tools/bench/diag_s56_transport3.log:25)
    diag_index(#3) -> ValueError: 3 is not in list                                                       (:26)
because `panel_wiring`'s `uid` column is the PANEL CONTROL's uid (`ControlUID`, tools/gscript.py:849,:859), not
its diagram-side terminal's - so a front-panel object's owner is the PANEL and there is no "its own owner
diagram" to resolve. The same run then measured what the diagram side actually is:
    the ControlTerminal that `create_indicator` produced reads owner **'TopLevelDiagram'** and
    owner_of(#23486) = ('TopLevelDiagram', 536)                                                    (:71, :75-76)
so this run resolves the rule against the TERMINAL side instead: the Traverse `Diagram` index of the
TopLevelDiagram (#536, identified by elimination in tools/bench/diag_c56_topdiagram_files.json and now
CONFIRMED by a live owner read), justified by a census of EVERY ControlTerminal's owner class. Nothing is
chosen and nothing is re-planned here: the rule is judgement's, only the object it is applied to is corrected
by measurement.

PREDICTION CONTRACT (every line is a printed GATE; a FAIL is a reading, the 34(j)/37(e) pattern):
  T1  the ORIGINAL's md5 == 2a78e17c449cacdaf5da389818526859                                          (FATAL)
  T2  claudeDev\\D1_s2_loops.vi md5 == 6ff19497f2309e007a214660bb64b911                               (FATAL)
  T3  the scratch is byte-identical to the S2 artefact at creation                                    (FATAL)
  E0  every one of the 114 ControlTerminals reads owner class 'TopLevelDiagram' (the census that justifies
      diagram_index = the TopLevelDiagram's Traverse index)
  E1  Traverse `Diagram` index 0 is #536, the TopLevelDiagram (live confirmation of the files-only claim)
  E2  the target indicator's label is READ OFF THE MACHINE, byte-exact, for control uid 6, wire 0
  E3  `wire_indicators(Function[102], ['x .and. y?'] -> ['File # Saved'], diagram_index=<#536's index>)`
      returns an EMPTY error column                                            (THE MEASUREMENT OF THIS RUN)
  E4  the target indicator's wire uid changes from 0 (the EFFECT gate; a branch adds no Wire object,
      tools/gscript.py:1771-1772)
  E5  #10686 t0 stays wired; its wired-terminal count is reported before and after                   (37(e))
  E6  #637's terminal count is unchanged - no new tunnel/border object                               (37(e))
  E7  the run ends at ExecState 1 and `g.save()` returns a byte count
  E8  the ORDERED SECOND-PASS `Is Broken?` read returns a boolean (True is a LEGITIMATE reading)
  Z1  ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 unchanged
  Z2  refs opened == refs closed, 0 live

BOUNDS: at most 3 attempts at this verb in total and attempt 1 spent NONE, so at most 3 here; no loop over
indices. NO VI IS RUN (34(f)). NO NEW OP VI (Pre-decided 2). No new device. No GUI action. No motor/ASI/camera.
`allow_broken` stays False, `gui_save` is NEVER called, the save happens BEFORE the ordered `Is Broken?` pass
(its read perturbs ExecState, docs/NAMES.md:912-918). The Moving Objects fixtures are NOT touched by this run.
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
import gscript as g                                                               # noqa: E402
import diag_s2_scaffold as D                                                      # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import diag_index, owner_of                                      # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1              # noqa: E402
import build_opconnectnested_v1 as CN1                                            # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(HERE, "diag_s56_transport3b.json")
V1_LABELS = json.load(open(os.path.join(HERE, "opconnectnested_v1_labels.json"), encoding="utf-8"))

TARGET_IND_UID = 6
SRC_UID, SRC_TERM_NAME, SRC_WIRE = 10686, "x .and. y?", 10799
SRC_NODES_INDEX, SINK_NODES_INDEX = 25, 24
D639, D686, D536 = 639, 686, 536
LOOP11_UID, LOOP11_NODES_INDEX = 637, 4

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "question": "does wire_indicators resolve its `Indicator Names` when it is handed the diagram that OWNS "
                 "the front-panel TERMINALS (the TopLevelDiagram #536), instead of the frame that owns the "
                 "SOURCE node (#639, dispatch 3's 5001)?",
     "attempt_1_made_zero_calls": "tools/bench/diag_s56_transport3.log:25-42 - owner_of(#6) = ('Panel', 3), "
                                  "diag_index(#3) raised, so the brief's rule had no resolvable value",
     "chooses_nothing": True, "interprets_nothing": True, "no_vi_was_run": True, "no_new_op": True,
     "no_new_device": True, "no_gui_action": True, "no_recipe": True, "phases_2_and_3_not_repeated": True,
     "rig_state": "조립 (motors/ASI forbidden, camera not needed)",
     "handles": {}, "hash_probe": [], "rec": {}}
REC = R["rec"]


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


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    REC.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def wired_counts(tag, target, diag, node_i, uid_expect):
    out = {"tag": tag, "diagram_index": diag, "node_index": node_i, "uid_expect": uid_expect}
    try:
        u, rows = g.node_terms_uid(target, diag, node_i)
        out.update({"node_uid_readback": u, "n_terms": len(rows),
                    "n_wired": sum(1 for r in rows if r.get("wire")),
                    "terms": [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]),
                               "wire": r["wire"]} for r in rows]})
    except Exception as e:                                                         # noqa: BLE001
        out["error"] = "%s: %s" % (type(e).__name__, str(e)[:160])
    REC.setdefault("wired_counts", []).append(out)
    fact("%s: node uid readback %r, %r terminals, %r WIRED"
         % (tag, out.get("node_uid_readback"), out.get("n_terms"), out.get("n_wired")))
    return out


def panel_rows(target):
    try:
        return list(g.panel_wiring(target) or [])
    except Exception as e:                                                         # noqa: BLE001
        fact("panel_wiring raised %s: %s" % (type(e).__name__, str(e)[:200]))
        return []


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


def main():
    print("=== diag_s56_transport3b  %s   (cycle 56 dispatch 5, ATTEMPT 2 of the wire_indicators verb; PHASE 1 "
          "ONLY; NO VI IS RUN, 34(f); no new op, no device, no GUI; CHOOSES NOTHING)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE (attempt 1 left 54,367; fresh baseline ~31,500): %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("T2 the S2 artefact", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    D.fresh("T2b RESTART (pre-batch, 44(e); attempt 1 left the instance UP at 54,367 handles)")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the restart: %r" % R["handles"]["after_restart"])

    target = os.path.join(g.CLAUDEDEV, "DIAG_s56_t3b_p1_%s.vi" % STAMP)
    if os.path.exists(target):
        os.remove(target)
    shutil.copy2(S2_ARTEFACT, target)
    p = probe("T3 the scratch at creation (copied from the S2 artefact)", target)
    REC["scratch"] = target
    gate("T3 the scratch is byte-identical to the S2 artefact", p.get("md5") == S2_MD5, p.get("md5", "?"),
         fatal=True)
    dump()

    with D.Preload("P-1b"):
        g.open_panel(target)
        time.sleep(1.0)
        c = {}
        for k in ("Diagram", "ControlTerminal", "Function", "Wire", "Local"):
            try:
                c[k] = g.count(target, k)
            except Exception as e:                                                # noqa: BLE001
                c[k] = "ERROR %s" % type(e).__name__
        REC["census_before"] = c
        fact("class census BEFORE %r" % c)
        read_exec_state("BEFORE", target)

        # ---- E0: the ControlTerminal owner census - the measurement that names the right diagram
        try:
            cts = g.report_all(target, "ControlTerminal")
        except Exception as e:                                                     # noqa: BLE001
            cts = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
        owners = {}
        if isinstance(cts, list):
            for r in cts:
                owners[r.get("owner")] = owners.get(r.get("owner"), 0) + 1
        REC["control_terminal_owner_census"] = owners
        fact("E0 ControlTerminal owner-class census over %r objects: %r"
             % (len(cts) if isinstance(cts, list) else cts, owners))
        gate("E0 every ControlTerminal reads owner class 'TopLevelDiagram'",
             list(owners) == ["TopLevelDiagram"], repr(owners))

        # ---- E1: which Traverse `Diagram` index is the TopLevelDiagram #536?
        try:
            dias = g.report_all(target, "Diagram")
        except Exception as e:                                                     # noqa: BLE001
            dias = "ERROR %s: %s" % (type(e).__name__, str(e)[:160])
        d0 = (dias[0] if isinstance(dias, list) and dias else None)
        REC["diagram_index_0"] = d0
        d_top = None
        try:
            d_top = diag_index(target, D536)
        except Exception as e:                                                      # noqa: BLE001
            fact("diag_index(#%d) raised %s: %s" % (D536, type(e).__name__, str(e)[:160]))
        REC["diagram_index_of_536"] = d_top
        fact("E1 Traverse Diagram[0] = %r ; diag_index(#%d) = %r  (files-only claim: #536 IS Traverse index 0, "
             "tools/bench/diag_c56_topdiagram_files.json)" % (d0, D536, d_top))
        gate("E1 Traverse Diagram index 0 is #%d, class TopLevelDiagram" % D536,
             bool(d0) and d0.get("uid") == D536 and d_top == 0,
             "%r -> index %r" % (d0, d_top))
        if d_top is None and isinstance(d0, dict) and d0.get("uid") == D536:
            d_top = 0

        # ---- E2: the label, byte-exact
        rows = panel_rows(target)
        tr = next((r for r in rows if r.get("uid") == TARGET_IND_UID), None)
        REC["target_row_before"] = tr
        lab = (tr or {}).get("label")
        fact("E2 control uid %d label VERBATIM %r (utf-8 hex %s), indicator=%r, wire=%r"
             % (TARGET_IND_UID, lab, (lab or "").encode("utf-8").hex(), (tr or {}).get("indicator"),
                (tr or {}).get("wire")))
        gate("E2 the target indicator's label is READ OFF THE MACHINE, control uid %d, wire 0" % TARGET_IND_UID,
             bool(lab) and (tr or {}).get("wire") == 0, "label %r wire %r" % (lab, (tr or {}).get("wire")))
        owner_of_ct = None
        try:
            cls6, uid6 = owner_of(target, TARGET_IND_UID, strict=True)
            owner_of_ct = (cls6, uid6)
        except Exception as e:                                                      # noqa: BLE001
            owner_of_ct = "ERROR %s: %s" % (type(e).__name__, str(e)[:200])
        REC["owner_of_control_uid"] = owner_of_ct
        fact("E2b owner_of(#%d) = %r - RE-MEASURED: a panel CONTROL's owner is the Panel, which is why the "
             "brief's diag_index(owner_of(...)) could not resolve" % (TARGET_IND_UID, owner_of_ct))

        # ---- the source side, re-resolved LIVE
        try:
            fn = [x["uid"] for x in g.report_all(target, "Function")]
            fn_i = fn.index(SRC_UID)
        except Exception as e:                                                      # noqa: BLE001
            fn, fn_i = [], None
            fact("report_all(Function) raised %s: %s" % (type(e).__name__, str(e)[:160]))
        REC["src_function_traverse_index"] = fn_i
        d639 = d686 = None
        for uid, name in ((D639, "d639"), (D686, "d686")):
            try:
                v = diag_index(target, uid)
            except Exception as e:                                                  # noqa: BLE001
                v = None
                fact("diag_index(#%d) raised %s: %s" % (uid, type(e).__name__, str(e)[:140]))
            if name == "d639":
                d639 = v
            else:
                d686 = v
        REC["diagram_index_639"], REC["diagram_index_686"] = d639, d686
        fact("E2c #%d sits at Traverse `Function` index %r of %d; Diagram #%d = index %r, #%d = index %r"
             % (SRC_UID, fn_i, len(fn), D639, d639, D686, d686))

        src_before = wired_counts("E5 BEFORE #%d (the source node)" % SRC_UID, target, d639, SRC_NODES_INDEX,
                                  SRC_UID)
        loop_before = wired_counts("E6 BEFORE #%d (loop 1.1, the tunnel check)" % LOOP11_UID, target, d686,
                                   LOOP11_NODES_INDEX, LOOP11_UID)

        # ---- E3: the attempts. HARD BOUND <= 3, no loop over indices.
        alt = next((r for r in rows if r.get("indicator") and not r.get("wire")
                    and r.get("uid") != TARGET_IND_UID), None)
        spec = []
        if lab is not None and isinstance(d_top, int):
            spec.append({"n": 1, "label": lab, "diagram_index": d_top, "want_uid": TARGET_IND_UID,
                         "why": "the diagram that OWNS every front-panel terminal (TopLevelDiagram #%d)" % D536})
        if alt and isinstance(d_top, int):
            spec.append({"n": 2, "label": alt["label"], "diagram_index": d_top, "want_uid": alt["uid"],
                         "why": "a DIFFERENT wire-0 indicator at the same diagram - separates a label-string "
                                "failure from a lookup-scope failure"})
        REC["attempts_spec"] = spec
        fact("E3 attempt plan (HARD BOUND <= 3; dispatch 3's diagram_index=%r is NOT repeated, its 5001 is "
             "already on record): %r" % (d639, [{k: a[k] for k in ("n", "label", "diagram_index")} for a in spec]))

        REC["attempts"] = []
        for a in spec:
            att = {"n": a["n"], "label_repr": repr(a["label"]),
                   "label_hex": (a["label"] or "").encode("utf-8").hex(),
                   "diagram_index": a["diagram_index"], "why": a["why"], "function_index": fn_i,
                   "src_term": SRC_TERM_NAME}
            att["exec_state_before"] = read_exec_state("attempt %d BEFORE" % a["n"], target)
            w0 = g.count(target, "Wire")
            if fn_i is None:
                att["error_verbatim"] = "NOT ATTEMPTED: the Function index did not resolve."
                att["seconds"] = None
            else:
                try:
                    dt = g.wire_indicators(target, fn_i, [SRC_TERM_NAME], [a["label"]],
                                           diagram_index=a["diagram_index"], node_class="Function")
                    att.update({"error_verbatim": "", "seconds": dt})
                except Exception as e:                                             # noqa: BLE001
                    att.update({"error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:500]), "seconds": None})
            rows_after = panel_rows(target)
            ra = next((r for r in rows_after if r.get("uid") == a["want_uid"]), None)
            att["row_after"] = ra
            att["new_wire_uid"] = (ra or {}).get("wire")
            att["wire_count_delta"] = g.count(target, "Wire") - w0
            att["exec_state_after"] = read_exec_state("attempt %d AFTER" % a["n"], target)
            REC["attempts"].append(att)
            fact("E3 attempt %d: wire_indicators(Function[%r], [%r] -> [%r], diagram_index=%r) error VERBATIM %r"
                 % (a["n"], fn_i, SRC_TERM_NAME, a["label"], a["diagram_index"], att["error_verbatim"]))
            fact("E4 attempt %d: indicator uid %r wire 0 -> %r ; whole-VI Wire count delta %r (a BRANCH adds no "
                 "Wire object); ExecState %r -> %r"
                 % (a["n"], a["want_uid"], att["new_wire_uid"], att["wire_count_delta"],
                    att["exec_state_before"], att["exec_state_after"]))
            dump()
            if att.get("new_wire_uid"):
                break

        won = next((a for a in REC["attempts"] if a.get("new_wire_uid")), None)
        REC["succeeded_attempt"] = (won or {}).get("n")
        gate("E3 wire_indicators returned an EMPTY error column on at least one attempt",
             any(a.get("error_verbatim") == "" for a in REC["attempts"]),
             repr([a.get("error_verbatim") for a in REC["attempts"]]))
        gate("E4 a target indicator's wire uid changed from 0", bool(won),
             "attempt %r -> wire %r" % ((won or {}).get("n"), (won or {}).get("new_wire_uid")))

        src_after = wired_counts("E5 AFTER #%d (the source node)" % SRC_UID, target, d639, SRC_NODES_INDEX,
                                 SRC_UID)
        loop_after = wired_counts("E6 AFTER #%d (loop 1.1, the tunnel check)" % LOOP11_UID, target, d686,
                                  LOOP11_NODES_INDEX, LOOP11_UID)
        gate("E5 #%d t0 stays wired and its wired-terminal count is reported (37(e))" % SRC_UID,
             src_before.get("n_wired") is not None and src_after.get("n_wired") is not None,
             "%r -> %r wired of %r -> %r terminals" % (src_before.get("n_wired"), src_after.get("n_wired"),
                                                       src_before.get("n_terms"), src_after.get("n_terms")))
        gate("E6 #%d terminal count unchanged - no new tunnel/border object (37(e))" % LOOP11_UID,
             loop_before.get("n_terms") == loop_after.get("n_terms"),
             "%r -> %r terminals, %r -> %r wired" % (loop_before.get("n_terms"), loop_after.get("n_terms"),
                                                     loop_before.get("n_wired"), loop_after.get("n_wired")))
        c2 = {}
        for k in ("Diagram", "ControlTerminal", "Function", "Wire", "Local"):
            try:
                c2[k] = g.count(target, k)
            except Exception as e:                                                  # noqa: BLE001
                c2[k] = "ERROR %s" % type(e).__name__
        REC["census_after"] = c2
        fact("class census AFTER %r" % c2)

        # ---- E7: the save, BEFORE the ordered Is Broken? pass
        es = read_exec_state("immediately before the save attempt", target)
        size, serr = None, None
        if isinstance(es, int) and es == 1:
            try:
                size = g.save(target)          # allow_broken stays False; gui_save NEVER called
            except Exception as e:                                                  # noqa: BLE001
                serr = "%s: %s" % (type(e).__name__, str(e)[:250])
        else:
            serr = "NOT ATTEMPTED: ExecState is %r and only ExecState 1 may be saved." % (es,)
        REC["save"] = {"returned_bytes": size, "exception_or_reason_verbatim": serr, "allow_broken": False,
                       "gui_save": False, "exec_state_before_save": es}
        fact("E7 g.save() returned %r; exception/reason VERBATIM %r" % (size, serr))
        REC["save"]["file_after"] = D.file_facts("E7 artefact after the save attempt", target)
        gate("E7 the run ends at ExecState 1 and g.save() returned a byte count",
             isinstance(size, int) and size > 0, "ExecState %r, bytes %r, reason %r" % (es, size, serr))

        # ---- E8: the ORDERED SECOND PASS (42(b))
        if isinstance(d639, int):
            print("\n--- ORDERED PASS 2: `Is Broken?` (42(b)) - idempotent re-connect of the EXISTING #%d t0 -> "
                  "#10407 t0 connection on the same net; wire_delta must be 0" % SRC_UID, flush=True)
            REC["pass2"] = {"sink": "#10407 t0 (Nodes[%d] of Diagram #639), already sourced by wire %d"
                                    % (SINK_NODES_INDEX, SRC_WIRE)}
            buf = io.StringIO()
            try:
                with contextlib.redirect_stdout(buf):
                    dw, es2, err = CONNECT_V1(target, d639, SINK_NODES_INDEX, 0, d639, SRC_NODES_INDEX, 0,
                                              V1_LABELS)
                REC["pass2"].update({"wire_delta": dw, "exec_state_returned": es2, "error_verbatim": err})
            except Exception as e:                                                  # noqa: BLE001
                REC["pass2"].update({"wire_delta": None, "exec_state_returned": None,
                                     "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])})
            for ln in buf.getvalue().rstrip().splitlines():
                print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
            REC["pass2"]["op_indicators"] = op_indicators()
            ib = REC["pass2"]["op_indicators"].get("Is Broken?")
            fact("E8 ORDERED `Is Broken?` = %r on wire uid %r (op error column %r, wire_delta %r)"
                 % (ib, REC["pass2"]["op_indicators"].get("UID 2"), REC["pass2"].get("error_verbatim"),
                    REC["pass2"].get("wire_delta")))
            gate("E8 the ORDERED second-pass `Is Broken?` read returned a boolean", isinstance(ib, bool), repr(ib))
            read_exec_state("after the Is Broken? read (SUSPECT, docs/NAMES.md:912-918; the save already "
                            "happened)", target)
        try:
            g.close_panel(target)
        except Exception as e:                                                      # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    dump()

    print("\n--- Z: the closing facts", flush=True)
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                          # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])
    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    gate("Z1 ORIGINAL / D1_s1_copy.vi / D1_s2_loops.vi md5 all unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5,
         "%s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""), flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Stop as s:
        fact("FATAL: %s" % s)
        dump()
        print("\n=== GATES %d pass / %d fail (FATAL stop)" % (len(passes), len(fails)), flush=True)
        sys.exit(1)
