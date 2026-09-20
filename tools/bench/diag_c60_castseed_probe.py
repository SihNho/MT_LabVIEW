"""diag_c60_castseed_probe - cycle 60 (attempt 2) material #2, the DISCRIMINATING TEST the devil's-advocate
rule requires a failed prediction to end in. TWO MEASUREMENTS ONLY. Nothing is built, nothing is saved, no
op VI is created, no route is chosen.

WHY THIS FILE EXISTS. `tools/bench/diag_s3b_l0_localname_v2.log` ended 29 pass / 1 fail on
`S2_b10 ExecState == 1` and the forced hypothesis review
`archive/peer/2026-09-21-c60-cast-seed-execstate0.md` (claude/hypothesis, opus effort max, ANSWERED 643 s,
$4.8363) REFUTED this session's explanation and named the two tests below as "free, read-only, ~10 s" and
"the cheapest discriminating test, three calls, <20 s". Running a named cheapest separator is a MEASUREMENT,
not a route choice: this file draws NO conclusion, disposes nothing, and changes no plan.

  P1  (the peer's free prior, read-only) Point the S1 procedure of diag_s3b_l0_localname_v2.py at
      claudeDev\\OpLoopCast_v0.vi - a SHIPPED op whose TMSC is seeded by a typed CONTROL according to
      tools/recipes/build_oploopcast_v0.py:4-8 - and read WHICH OBJECT carries its `target class` wire.
      READ-ONLY: ensure_loaded, never open_panel, never save. Gate: the file is byte-unchanged.
  P2  (the peer's cheapest discriminator) On a THROWAWAY byte copy of claudeDev\\OpNodeLabels_v0.vi, isolate
      S2_b7 - the vestigial-chain detach, which touches neither `Local` nor the seed: read ExecState (expect
      1), delete the TMSC's output wire BY UID, create_control on the single orphaned sink, read ExecState
      again. No `Local`, no property node, no save; the copy is deleted in the same run.

PREDICTION CONTRACT
  T1..T3  the four md5 pins (ORIGINAL 2a78e17c FATAL, D1_s1_copy 3e3d23ce, D1_s2_loops 6ff19497 FATAL,
          D1_s3a_focus_ind eef91c1d FATAL) hold before AND after
  T4      claudeDev\\OpNodeLabels_v0.vi md5 376ff125... and claudeDev\\OpLoopCast_v0.vi exist; md5s recorded
  P1_a1   OpLoopCast_v0.vi's top-level diagram was dumped and exactly ONE TMSC node found by terminal name
  P1_a2   its `target class` wire uid was read, and every panel row of that VI was read with its wire uid
  P1_a3   WHICH object carries that wire is REPORTED VERBATIM - panel row, or none. A gate passes when the
          search RAN, never on a particular answer.
  P2_b1   the throwaway copy opens at ExecState 1 (this also discharges 14a: the instance is warm)
  P2_b2   its single TMSC's `specific class reference` wire feeds exactly ONE sink, read off the machine
  P2_b3   that wire was deleted BY UID; the gone-set is exactly that uid, no collateral
  P2_b4   create_control on the orphaned sink returned exactly one new ControlTerminal
  P2_b5   ExecState AFTER those two steps was READ and is REPORTED - 0 and 1 are both legitimate readings
  Z1      the four pins unchanged; Z2 refs 0 live; Z3 both op VIs byte-unchanged; Z4 the copy deleted

BOUNDS. No VI is run (34(f)). No GUI action. No motor / ASI / camera (rig 조립). No new process device, no
recipe, no new gscript verb, no new op VI. `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save`
neither imported nor called; `allow_broken` never True; `move_in` never called. NOTHING IS SAVED. No route is
chosen or recommended; no plan document and no STATUS `## NEXT` line is edited.
"""
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
from hash_probe import probe as HASH                                               # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpNodeLabels_v0.vi")
DONOR_MD5 = "376ff12569008ebac25a524e0887030b"
LOOPCAST = os.path.join(g.CLAUDEDEV, "OpLoopCast_v0.vi")

STAMP = time.strftime("%Y%m%d_%H%M%S")
COPY = os.path.join(g.CLAUDEDEV, "SCRATCH_B7_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_c60_castseed_probe.json")
T_CAST_IN = "target class"
T_CAST_OUT = "specific class reference"
SCAN_LIMIT = 60

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "the two measurements archive/peer/2026-09-21-c60-cast-seed-execstate0.md named as the free "
             "prior and the cheapest discriminating test. NOTHING IS BUILT OR SAVED.",
     "draws_no_conclusion": True, "chooses_no_route": True, "recommends_no_route": True,
     "disposes_nothing": True, "no_new_op_vi": True, "no_new_device": True, "no_recipe": True,
     "no_vi_was_run": True, "no_gui_action": True, "nothing_saved": True,
     "rig_state": "조립 / ASSEMBLED - no motor, no ASI, no camera",
     "handles": {}, "hash_probe": [], "P1_loopcast": {}, "P2_b7_isolated": {}}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
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
    R["elapsed_s"] = round(time.time() - T_START, 1)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def terms_table(rows):
    return [{"i": r["i"], "name": r["name"], "is_source": bool(r["is_source"]), "wire": r["wire"]}
            for r in rows]


def node_dump(target, diagram_index, tag):
    out = []
    for i in range(SCAN_LIMIT):
        try:
            u, rows = g.node_terms_uid(target, diagram_index, i)
        except Exception as e:                                                     # noqa: BLE001
            out.append({"i": i, "error_verbatim": "%s: %s" % (type(e).__name__, str(e)[:200])})
            break
        if not u:
            break
        out.append({"i": i, "uid": u, "terms": terms_table(rows)})
    try:
        labs = {r["uid"]: r["label"] for r in g.node_labels(target, diagram_index)}
    except Exception as e:                                                         # noqa: BLE001
        labs = {}
        fact("%s node_labels raised %s: %s" % (tag, type(e).__name__, str(e)[:160]))
    for row in out:
        if "uid" in row:
            row["node_label"] = labs.get(row["uid"])
        fact("%s Nodes[%s] uid %r label %r terms %r"
             % (tag, row.get("i"), row.get("uid"), row.get("node_label"), row.get("terms", row)))
    return out


def exec_read(rec, tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    rec.setdefault("exec_state_timeline", []).append({"tag": tag, "value": es})
    fact("ExecState [%s] = %r" % (tag, es))
    return es


def tmsc_of(shape):
    return [n for n in shape if any(t["name"] == T_CAST_IN for t in n.get("terms", []))
            and any(t["name"] == T_CAST_OUT for t in n.get("terms", []))]


# ============================================================ P1
def phase_p1():
    K = R["P1_loopcast"]
    print("\n=== P1  READ-ONLY: which object carries OpLoopCast_v0.vi's `%s` wire" % T_CAST_IN, flush=True)
    K["file_before"] = probe("P1 OpLoopCast_v0.vi before the read", LOOPCAST)
    g.ensure_loaded(LOOPCAST)                     # read-only: never open_panel, never save
    exec_read(K, "P1 OpLoopCast_v0.vi as found on disk", LOOPCAST)
    shape = node_dump(LOOPCAST, 0, "P1")
    K["shape"] = shape
    tm = tmsc_of(shape)
    K["tmsc_nodes"] = [{"uid": n.get("uid"), "nodes_index": n.get("i"), "label": n.get("node_label"),
                        "terms": n.get("terms")} for n in tm]
    w = next((t["wire"] for n in tm for t in n["terms"] if t["name"] == T_CAST_IN), None) if tm else None
    K["target_class_wire"] = w
    gate("P1_a1 OpLoopCast_v0.vi's diagram was dumped and exactly ONE TMSC found by terminal name",
         len(tm) == 1, "%d TMSC node(s)" % len(tm))
    try:
        pw = g.panel_wiring(LOOPCAST)
        K["panel_wiring_error"] = ""
    except Exception as e:                                                        # noqa: BLE001
        pw = []
        K["panel_wiring_error"] = "%s: %s" % (type(e).__name__, str(e)[:300])
        fact("P1 panel_wiring raised %s" % K["panel_wiring_error"])
    K["panel_wiring"] = pw
    for row in pw:
        fact("P1 panel row: label %r indicator=%r uid=%r is_source=%r wire=%r"
             % (row.get("label"), row.get("indicator"), row.get("uid"), row.get("is_source"),
                row.get("wire")))
    hits = [row for row in pw if row.get("wire") == w]
    K["panel_objects_carrying_the_target_class_wire"] = hits
    prod = [{"uid": n.get("uid"), "label": n.get("node_label"), "terminal": t["name"]}
            for n in shape for t in n.get("terms", []) if t["is_source"] and t["wire"] == w]
    K["node_producers"] = prod
    gate("P1_a2 its `%s` wire uid was read and every panel row was read with its wire uid" % T_CAST_IN,
         w is not None and bool(pw), "wire %r, %d panel rows" % (w, len(pw)))
    fact("P1_a3 THE ANSWER, REPORTED NOT INTERPRETED: OpLoopCast_v0.vi's `%s` wire is %r ; NODE producers "
         "%r ; PANEL rows carrying it %r" % (T_CAST_IN, w, prod, hits))
    gate("P1_a3 which object carries that wire was searched for and reported verbatim", True,
         "%d node producer(s), %d panel row(s)" % (len(prod), len(hits)))
    K["file_after"] = probe("P1 OpLoopCast_v0.vi after the read", LOOPCAST)
    gate("P1_a4 OpLoopCast_v0.vi is byte-unchanged by the read",
         K["file_after"].get("md5") == K["file_before"].get("md5"),
         "%s vs %s" % (K["file_after"].get("md5"), K["file_before"].get("md5")))
    dump()


# ============================================================ P2
def phase_p2():
    K = R["P2_b7_isolated"]
    print("\n=== P2  isolate S2_b7 on a THROWAWAY copy - no `Local`, no property node, no save", flush=True)
    shutil.copy2(DONOR, COPY)
    K["copy_at_creation"] = probe("P2 the throwaway copy at creation", COPY)
    g.open_panel(COPY)
    time.sleep(1.0)
    try:
        es0 = exec_read(K, "P2 the copy, untouched", COPY)
        gate("P2_b1 the throwaway copy opens at ExecState 1 (also discharges 14a: the instance is warm)",
             es0 == 1, "%r" % (es0,))
        shape = node_dump(COPY, 0, "P2")
        K["shape"] = shape
        tm = tmsc_of(shape)
        if len(tm) != 1:
            raise Stop("P2: %d TMSC nodes on the copy - nothing is improvised" % len(tm))
        out_wire = next((t["wire"] for t in tm[0]["terms"] if t["name"] == T_CAST_OUT), None)
        K["tmsc_uid"] = tm[0]["uid"]
        K["cast_output_wire"] = out_wire
        sinks = [{"uid": n.get("uid"), "nodes_index": n.get("i"), "label": n.get("node_label"),
                  "terminal": t["name"], "terminal_index": t["i"]}
                 for n in shape for t in n.get("terms", [])
                 if (not t["is_source"]) and t["wire"] == out_wire]
        K["sinks"] = sinks
        fact("P2_b2 the TMSC #%r output wire %r feeds these sinks: %r" % (K["tmsc_uid"], out_wire, sinks))
        gate("P2_b2 exactly ONE sink is fed by the cast output wire", len(sinks) == 1, "%r" % (sinks,))
        if len(sinks) != 1 or not out_wire:
            raise Stop("P2: the single-sink precondition does not hold - REPORTED, nothing improvised")
        order = [o["uid"] for o in g.report_all(COPY, "Wire")]
        idx = order.index(out_wire) if out_wire in order else None
        K["wire_report_index"] = idx
        try:
            gone = sorted(g.delete_object(COPY, "Wire", idx, verify=True))
            err = ""
        except Exception as e:                                                     # noqa: BLE001
            gone = None
            err = "%s: %s" % (type(e).__name__, str(e)[:400])
        after = [o["uid"] for o in g.report_all(COPY, "Wire")]
        K["delete"] = {"index": idx, "gone": gone, "error_verbatim": err,
                       "wire_count": [len(order), len(after)],
                       "collateral": sorted((set(order) - set(after)) - {out_wire})}
        fact("P2_b3 delete_object(Wire[%r]) for uid %r: gone %r ; Wire %d -> %d ; collateral %r ; error "
             "VERBATIM %r" % (idx, out_wire, gone, len(order), len(after), K["delete"]["collateral"], err))
        gate("P2_b3 the cast output wire was deleted by uid, gone-set exactly that uid, no collateral",
             gone == [out_wire] and not K["delete"]["collateral"], "gone %r" % (gone,))
        es1 = exec_read(K, "P2 after the wire delete, BEFORE the control", COPY)
        K["exec_state_after_delete_only"] = es1
        sink = sinks[0]
        cd = {"sink": sink, "control_terminal_before": g.count(COPY, "ControlTerminal")}
        try:
            new, lab = g.create_control(COPY, sink["nodes_index"], sink["terminal_index"])
            cd["new"] = [{"uid": o["uid"], "pos": o["pos"]} for o in new]
            cd["label_from_the_machine"] = lab
            cd["error_verbatim"] = ""
        except Exception as e:                                                     # noqa: BLE001
            cd["new"] = None
            cd["label_from_the_machine"] = None
            cd["error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:400])
        cd["control_terminal_after"] = g.count(COPY, "ControlTerminal")
        K["create_control"] = cd
        fact("P2_b4 create_control(Nodes[%r].Terminals[%r]) on the orphaned sink: new %r ; label READ OFF "
             "THE MACHINE %r ; ControlTerminal %r -> %r ; error VERBATIM %r"
             % (sink["nodes_index"], sink["terminal_index"], cd["new"], cd["label_from_the_machine"],
                cd["control_terminal_before"], cd["control_terminal_after"], cd["error_verbatim"]))
        gate("P2_b4 create_control returned exactly one new ControlTerminal",
             bool(cd["new"]) and len(cd["new"]) == 1, "%r" % (cd["new"],))
        es2 = exec_read(K, "P2 AFTER the isolated b7 (delete + control)", COPY)
        K["exec_state_after_b7"] = es2
        fact("P2_b5 THE ANSWER, REPORTED NOT INTERPRETED: ExecState %r (untouched) -> %r (wire deleted) -> "
             "%r (control created). NOTHING IS SAVED and no conclusion is drawn here." % (es0, es1, es2))
        gate("P2_b5 ExecState after the isolated b7 was READ (0 and 1 are both legitimate readings)",
             es2 in (0, 1), "%r" % (es2,))
    finally:
        try:
            g.close_panel(COPY)
        except Exception as e:                                                     # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    dump()


# ============================================================ MAIN
def main():
    print("=== diag_c60_castseed_probe  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    o = probe("T1 ORIGINAL", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == pin", s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == pin", s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == pin", s3.get("md5") == S3A_MD5, s3.get("md5", "?"), fatal=True)
    dn = probe("T4 the DONOR OpNodeLabels_v0.vi", DONOR)
    gate("T4 the donor is on disk at its recorded md5", dn.get("md5") == DONOR_MD5,
         "%r" % dn.get("md5"), fatal=True)
    lc = probe("T4b OpLoopCast_v0.vi", LOOPCAST)
    R["loopcast_md5_before"] = lc.get("md5")
    gate("T4b OpLoopCast_v0.vi is on disk", lc.get("exists") == "1", "%r" % lc.get("md5"), fatal=True)
    dump()

    for name, fn in (("P1", phase_p1), ("P2", phase_p2)):
        try:
            fn()
        except Stop as s:
            R["%s_stopped" % name] = str(s)
            fact("%s STOPPED: %s" % (name, s))
        except Exception as e:                                                     # noqa: BLE001
            R["%s_stopped" % name] = "%s: %s" % (type(e).__name__, str(e)[:500])
            fact("%s raised %s: %s" % (name, type(e).__name__, str(e)[:500]))
        dump()

    print("\n--- Z: the closing facts", flush=True)
    if os.path.exists(COPY):
        try:
            os.remove(COPY)
        except Exception as e:                                                     # noqa: BLE001
            fact("removing the throwaway copy FAILED %s: %s" % (type(e).__name__, e))
    gate("Z4 the throwaway copy was deleted in the same run", not os.path.exists(COPY),
         "exists=%r" % os.path.exists(COPY))
    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                         # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER: %r" % R["handles"]["after"])
    zo = probe("Z1 ORIGINAL after", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after", S2_ARTEFACT)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after", S3A_ARTEFACT)
    gate("Z1 all four md5 pins unchanged after everything",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    rc = R["ref_counts"] or {}
    gate("Z2 refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    zd = probe("Z3 the DONOR after", DONOR)
    zl = probe("Z3b OpLoopCast_v0.vi after", LOOPCAST)
    gate("Z3 OpNodeLabels_v0.vi and OpLoopCast_v0.vi are both byte-unchanged",
         zd.get("md5") == DONOR_MD5 and zl.get("md5") == R["loopcast_md5_before"],
         "%s / %s" % (zd.get("md5"), zl.get("md5")))
    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
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
