"""diag_c64_row1_testa - the forced review's OWN discriminating test. READ-ONLY. NOTHING IS EDITED OR SAVED.

WHY THIS FILE EXISTS. `tools/bench/diag_c64_s3b_row1.log` ended 51 pass / 1 fail; the one failure, `K2`, was
a WIRE COUNT: expected 1905, measured 1906. The mandatory review
(archive/peer/2026-09-21-c64-row1-wirecount-k2.md, ANSWERED, claude/hypothesis) REFUTED the explanation I
formed ("the helper's docstring is wrong") and named a cheaper one: step [2] of that run DELETED wire 10799,
which left the source terminal `#10686` t0 BARE, so `wire_indicators`' documented precondition
(gscript.py:1765-1767, "Each source terminal MUST ALREADY BE WIRED") was false and it made a NEW wire instead
of branching. Its test, section 4, decides between the two by ONE read.

  TEST A  cold-open the STEP-7 artefact - saved AFTER the delete+connect and BEFORE wire_indicators - and
          read `#10686` t0's wire plus the Wire census.
            t0 wire == 0 and Wire == 1905  ->  the source was bare; the docstring stands; 1906 is the right
                                               number for what was built  (THE REVIEW'S explanation)
            t0 wire != 0                   ->  the helper branched AND still added a wire; the docstring is
                                               wrong                       (MY explanation)
          NO VALUE IS ASSERTED AS THE ANSWER HERE. The reading IS the measurement.

  TEST B  the review also found that `t3_separator` in the build script scans ONLY diagram #639's nodes plus
          the panel rows, so a second data source on ANY OTHER diagram was invisible to gate `I`. So: the
          net of wire 23502 AND the net of wire 23526 are re-censused across EVERY diagram of the finished
          artefact, bounded, and the source counts are reported.

WHAT ALREADY EXISTS AND IS REUSED, NOT REBUILT: tools/bench/diag_c64_s3b_row1.py's own gate/fact/probe/
find_node/terms_at skeleton; tools/gscript.py :488 report_all :587 node_labels :925 node_terms_uid :1005
count :826 panel_wiring :1977 exec_state :233 ref_counts; tools/recipes/build_d1_v0.py:357 diag_index;
tools/bench/diag_s2_scaffold.py fresh; tools/hash_probe.py probe; tools/bench/bench_prep.py labview_handles.
NO new verb, NO new op, NO recipe, NO edit to tools/gscript.py.

FORBIDDEN AND ABSENT: no `g.save` (neither imported nor called), no edit of any kind, no `open_panel`, no
`ensure_loaded`, no `move_in`, no `allow_broken`, no `gui_save`, no GUI action, no VI run (34(f)), no
motor/ASI/camera (rig 조립/ASSEMBLED), no new process device. Nothing under tools/recipes/ is written.

PREDICTION CONTRACT
  Z   the four md5 pins hold; both row-1 artefacts are byte-unchanged by this run (it only reads)
  TA  the STEP-7 artefact opens cold at ExecState 1; `#10686` t0's wire and the Wire census are REPORTED,
      no value predicted; the verdict line names which of the two explanations the reading selects
  TB  every diagram of the STEP-9 artefact is scanned (or the scan reports where its budget stopped) and the
      SOURCE COUNT of wire 23502 and of wire 23526 is reported, with every member terminal
"""
import json
import os
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
from build_d1_v0 import diag_index                                                 # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"

STEP7 = os.path.join(g.CLAUDEDEV, "D1_s3b_row1a_20260921_135932.vi")
STEP7_MD5 = "c7094f98324af3bb53755fef718f8e28"
STEP9 = os.path.join(g.CLAUDEDEV, "D1_s3b_row1_20260921_135932.vi")
STEP9_MD5 = "72f0d47d0b1cbd0834d50f1483e558c1"

SRC_UID, CASE_UID, D639, LOCAL_UID = 10686, 10407, 639, 23499
WIRE_CONNECT, WIRE_INDICATOR = 23502, 23526
OLD_CONTROL = 23555
TOP = 0
SCAN_BUDGET_S = 600.0
OUT = os.path.join(BENCH, "diag_c64_row1_testa.json")

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__),
     "task": "the forced review's own discriminating test (archive/peer/2026-09-21-c64-row1-wirecount-k2.md "
             "section 4) - READ-ONLY, nothing is edited or saved",
     "no_save": "g.save is neither imported nor called anywhere in this file",
     "no_edit_of_any_kind": True, "no_new_verb": True, "no_new_op": True, "no_recipe": True,
     "gscript_not_edited": True, "no_gui_action": True, "no_vi_run": "34(f)",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "chooses_no_route": True, "recommends_no_route": True,
     "handles": {}, "hash_probe": [], "test_a": {}, "test_b": {}}


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
        dump()
        raise SystemExit(1)
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
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def safe(label, fn, default=None):
    try:
        return fn(), ""
    except Exception as e:                                                         # noqa: BLE001
        msg = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("%s raised %s" % (label, msg))
        return default, msg


def read_es(tag, target):
    es, _ = safe("%s exec_state" % tag, lambda: g.exec_state(target))
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def find_node(path, uid, hints, tag, budget_s=240.0):
    t0 = time.time()
    rec = {"uid": uid, "scanned": [], "found": None}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    by_index = {d["i"]: d for d in (diags or [])}
    order = [i for i in hints if isinstance(i, int) and i in by_index]
    order += [i for i in sorted(by_index) if i not in order]
    for i in order:
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = "budget reached after %d diagrams" % len(rec["scanned"])
            break
        rows, err = safe("%s node_labels(%d)" % (tag, i), lambda k=i: g.node_labels(path, k), [])
        rec["scanned"].append(i)
        hit = next((k for k, r in enumerate(rows or []) if r["uid"] == uid), None)
        if hit is not None:
            rec["found"] = {"diagram_index": i, "diagram_uid": by_index[i]["uid"],
                            "nodes_index": hit, "label": rows[hit]["label"]}
            break
    fact("%s #%s lives at %r (%d diagram(s) scanned of %d)"
         % (tag, uid, rec["found"], len(rec["scanned"]), rec["diagram_rows"]))
    return rec


def terms_at(path, di, ni, expect_uid, tag):
    rec = {"diagram_index": di, "nodes_index": ni, "expected_uid": expect_uid, "terminals": []}
    try:
        echo, rows = g.node_terms_uid(path, int(di), int(ni))
        rec["uid_echo"] = echo
        rec["terminals"] = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"],
                             "wire": t["wire"],
                             "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                            for t in rows]
    except Exception as e:                                                         # noqa: BLE001
        rec["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    fact("%s terminal table of #%s (echo %r): %d terminal(s)"
         % (tag, expect_uid, rec.get("uid_echo"), len(rec["terminals"])))
    for t in rec["terminals"]:
        fact("    %s t%-2d %-30r is_source=%-5r wire=%-7r errs=%r"
             % (tag, t["i"], t["name"], t["is_source"], t["wire"], t["errs"]))
    return rec


# ============================================================ TEST A
def test_a():
    print("\n========== TEST A  the STEP-7 artefact (saved AFTER delete+connect, BEFORE wire_indicators)",
          flush=True)
    A = R["test_a"]
    A["file"] = STEP7
    D.fresh("TA RESTART before the cold read")
    A["exec_state_cold"] = read_es("TA cold %s" % os.path.basename(STEP7), STEP7)
    gate("TA_0 the STEP-7 artefact opens COLD at ExecState 1", A["exec_state_cold"] == 1,
         "%r" % (A["exec_state_cold"],))
    for c in ("Wire", "Node", "ControlTerminal", "Local"):
        A.setdefault("counts", {})[c], _ = safe("TA count(%r)" % c, lambda cc=c: g.count(STEP7, cc))
    fact("TA counts: %r" % (A["counts"],))
    d639, _e = safe("TA diag_index(#639)", lambda: diag_index(STEP7, D639))
    A["d639"] = d639
    loc = find_node(STEP7, SRC_UID, [d639, TOP], "TA SOURCE")
    A["source_loc"] = loc.get("found")
    f = loc.get("found") or {}
    tt = (terms_at(STEP7, f["diagram_index"], f["nodes_index"], SRC_UID, "TA SOURCE")
          if f.get("nodes_index") is not None else {"terminals": []})
    A["source_terminals"] = tt.get("terminals", [])
    t0 = next((t for t in A["source_terminals"] if t["i"] == 0), {})
    A["source_t0"] = t0
    A["source_t0_wire"] = t0.get("wire")
    # ALSO: the sink and the Local, so the step-7 state is on record whole
    for label, uid in (("#10407 the sink", CASE_UID), ("the Local", LOCAL_UID)):
        l2 = find_node(STEP7, uid, [d639, TOP], "TA %s" % label)
        g2 = l2.get("found") or {}
        A.setdefault("other_tables", {})[label] = (
            terms_at(STEP7, g2["diagram_index"], g2["nodes_index"], uid, "TA %s" % label).get("terminals")
            if g2.get("nodes_index") is not None else [])
    verdict = ("THE REVIEW'S EXPLANATION: the source terminal was BARE after step [2] deleted wire 10799, so "
               "wire_indicators could not branch and made a NEW wire; the docstring stands and 1906 is the "
               "right number"
               if (A["source_t0_wire"] in (0, None) and A["counts"].get("Wire") == 1905) else
               "MY EXPLANATION: the source terminal already carried a wire at step 7, so wire_indicators "
               "branched AND still added a Wire object - the docstring's 'NO new Wire object' is wrong"
               if A["source_t0_wire"] else
               "NEITHER CLEANLY: the reading does not match either arm - reported as-is")
    A["verdict"] = verdict
    fact("*** TEST A READING: #%d t0 wire = %r ; Wire census = %r  ->  %s ***"
         % (SRC_UID, A["source_t0_wire"], A["counts"].get("Wire"), verdict))
    gate("TA *** THE READING: #%d t0 wire %r, Wire census %r ***"
         % (SRC_UID, A["source_t0_wire"], A["counts"].get("Wire")), True, verdict)
    dump()


# ============================================================ TEST B
def net_of(path, wire_uid, tag, budget_s=SCAN_BUDGET_S):
    """EVERY terminal carrying `wire_uid`, across EVERY diagram - the hole the review found in gate I."""
    t0 = time.time()
    rec = {"wire": wire_uid, "members": [], "diagrams_scanned": 0, "nodes_scanned": 0}
    diags, derr = safe("%s report_all('Diagram')" % tag, lambda: g.report_all(path, "Diagram"), [])
    rec["diagram_rows"] = len(diags or [])
    rec["diagram_census_error"] = derr
    for d in (diags or []):
        if time.time() - t0 > budget_s:
            rec["scan_stopped"] = ("budget %.0f s reached after %d of %d diagrams"
                                   % (budget_s, rec["diagrams_scanned"], rec["diagram_rows"]))
            break
        rows, _e = safe("%s node_labels(%d)" % (tag, d["i"]), lambda k=d["i"]: g.node_labels(path, k), [])
        rec["diagrams_scanned"] += 1
        for ni in range(len(rows or [])):
            if time.time() - t0 > budget_s:
                rec["scan_stopped"] = "budget reached inside diagram index %d" % d["i"]
                break
            try:
                u, tr = g.node_terms_uid(path, int(d["i"]), ni)
            except Exception:                                                      # noqa: BLE001
                continue
            rec["nodes_scanned"] += 1
            for t in tr:
                if t["wire"] == wire_uid:
                    rec["members"].append({"where": "Diagram idx %d (#%s) Nodes[%d] = #%s"
                                                    % (d["i"], d["uid"], ni, u),
                                           "node_uid": u, "terminal": t["i"], "name": t["name"],
                                           "is_source": t["is_source"]})
    prows, _pe = safe("%s panel_wiring" % tag, lambda: g.panel_wiring(path), [])
    for r in (prows or []):
        if r.get("wire") == wire_uid:
            rec["members"].append({"where": "panel control uid %s" % r.get("uid"), "node_uid": r.get("uid"),
                                   "terminal": None, "name": r.get("label"),
                                   "is_source": r.get("is_source")})
    rec["sources"] = [m for m in rec["members"] if m.get("is_source") is True]
    rec["sinks"] = [m for m in rec["members"] if m.get("is_source") is False]
    rec["source_count"] = len(rec["sources"])
    rec["scan_cost_s"] = round(time.time() - t0, 1)
    fact("%s the WHOLE-VI net of wire %r: %d member(s) over %d diagram(s) / %d node(s) in %.1f s%s"
         % (tag, wire_uid, len(rec["members"]), rec["diagrams_scanned"], rec["nodes_scanned"],
            rec["scan_cost_s"], (" ; " + rec["scan_stopped"]) if rec.get("scan_stopped") else ""))
    for m in rec["members"]:
        fact("    %s  %s" % (tag, m))
    fact("%s SOURCES on that net: %d -> %r" % (tag, rec["source_count"], rec["sources"]))
    return rec


def test_b():
    print("\n========== TEST B  the WHOLE-VI net census of both wires on the finished artefact", flush=True)
    B = R["test_b"]
    B["file"] = STEP9
    D.fresh("TB RESTART before the cold read")
    B["exec_state_cold"] = read_es("TB cold %s" % os.path.basename(STEP9), STEP9)
    gate("TB_0 the STEP-9 artefact opens COLD at ExecState 1", B["exec_state_cold"] == 1,
         "%r" % (B["exec_state_cold"],))
    for c in ("Wire", "Node", "ControlTerminal", "Local"):
        B.setdefault("counts", {})[c], _ = safe("TB count(%r)" % c, lambda cc=c: g.count(STEP9, cc))
    fact("TB counts: %r" % (B["counts"],))
    B["net_connect"] = net_of(STEP9, WIRE_CONNECT, "TB wire %d (the Local -> Case selector)" % WIRE_CONNECT)
    B["net_indicator"] = net_of(STEP9, WIRE_INDICATOR,
                                "TB wire %d (the source -> indicator)" % WIRE_INDICATOR)
    gate("TB_1 *** wire %d has EXACTLY ONE source across the WHOLE VI ***" % WIRE_CONNECT,
         B["net_connect"]["source_count"] == 1,
         "%d source(s): %r ; sinks %r ; %s"
         % (B["net_connect"]["source_count"], B["net_connect"]["sources"],
            [m["node_uid"] for m in B["net_connect"]["sinks"]],
            B["net_connect"].get("scan_stopped", "the scan completed")))
    gate("TB_2 *** wire %d has EXACTLY ONE source across the WHOLE VI, and control %d is a sink ***"
         % (WIRE_INDICATOR, OLD_CONTROL),
         B["net_indicator"]["source_count"] == 1
         and OLD_CONTROL in [m["node_uid"] for m in B["net_indicator"]["sinks"]],
         "%d source(s): %r ; sinks %r ; %s"
         % (B["net_indicator"]["source_count"], B["net_indicator"]["sources"],
            [m["node_uid"] for m in B["net_indicator"]["sinks"]],
            B["net_indicator"].get("scan_stopped", "the scan completed")))
    shared = ({(m["node_uid"], m["terminal"]) for m in B["net_connect"]["members"]}
              & {(m["node_uid"], m["terminal"]) for m in B["net_indicator"]["members"]})
    B["terminals_on_both_nets"] = sorted(shared)
    gate("TB_3 no terminal appears on BOTH wires (the two nets are disjoint)", not shared,
         "%r" % (B["terminals_on_both_nets"],))
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c64_row1_testa  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== the forced review's own discriminating test. READ-ONLY: nothing is edited, nothing is saved.",
          flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("Z0 ORIGINAL", ORIGINAL)
    gate("Z_0 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s2 = probe("Z0c D1_s2_loops.vi", S2_ARTEFACT)
    gate("Z_0c D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("Z0d D1_s3a_focus_ind.vi (the bed, never written)", S3A_ARTEFACT)
    gate("Z_0d D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    a7 = probe("Z0e the STEP-7 artefact", STEP7)
    gate("Z_0e D1_s3b_row1a md5 == %s" % STEP7_MD5, a7.get("md5") == STEP7_MD5, a7.get("md5", "?"),
         fatal=True)
    a9 = probe("Z0f the STEP-9 artefact", STEP9)
    gate("Z_0f D1_s3b_row1 md5 == %s" % STEP9_MD5, a9.get("md5") == STEP9_MD5, a9.get("md5", "?"),
         fatal=True)

    for fn in (test_a, test_b):
        try:
            fn()
        except SystemExit:
            raise
        except Exception as e:                                                     # noqa: BLE001
            fact("%s RAISED %s: %s" % (fn.__name__, type(e).__name__, str(e)[:400]))
            gate("%s completed" % fn.__name__, False, "%s: %s" % (type(e).__name__, str(e)[:200]))
        finally:
            dump()

    R["ref_counts"] = g.ref_counts()
    fact("tracked VI Server refs AFTER: %r" % (R["ref_counts"],))
    safe("g.reset", g.reset)
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER: %r" % R["handles"]["after"])
    z0 = probe("Z1 ORIGINAL after", ORIGINAL)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after", S3A_ARTEFACT)
    z7 = probe("Z1e the STEP-7 artefact after", STEP7)
    z9 = probe("Z1f the STEP-9 artefact after", STEP9)
    gate("Z_1 the ORIGINAL and the bed are byte-unchanged",
         z0.get("md5") == ORIG_MD5 and z3.get("md5") == S3A_MD5,
         "%s / %s" % (z0.get("md5"), z3.get("md5")))
    gate("Z_1b BOTH row-1 artefacts are byte-unchanged by this READ-ONLY run",
         z7.get("md5") == STEP7_MD5 and z9.get("md5") == STEP9_MD5,
         "%s / %s" % (z7.get("md5"), z9.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
