"""diag_c62_negctrl - the NEGATIVE CONTROL named by archive/peer/2026-09-21-c62-movein-es0.md section 6.

THE QUESTION, AND NOTHING ELSE
  Does `OpConnectNested_v1.vi` alone drive THIS bed's `ExecState` 1 -> 0, with no edit at all?

  The forced review REFUTED my explanation of `diag_c62_s3b_movein.log:82` (`B1_f ExecState == 1 after the
  connect -> 0`) and named this as the cheapest test that separates the two live readings. It builds nothing,
  saves nothing, and mutates nothing that survives the run.

WHAT ALREADY EXISTS AND IS REUSED (checked before writing a line of this file)
  tools/bench/diag_c62_s3b_movein.py   this run's own scaffold; the helpers below are its helpers, minus
                                       everything that edits. `move_in` is NOT imported (nothing is moved).
  tools/recipes/build_opconnectnested_v1.py   `connect_nested_v1` - the op under test
  grep "^def " tools/gscript.py        node_labels / node_terms_uid / report_all / exec_state / open_panel /
                                       close_panel / count / op / ref_counts / reset
  NOTHING NEW IS BUILT: no op, no gscript verb, no recipe, no device, no edit to tools/gscript.py.

THE PROCEDURE (review section 6 verbatim, on a THROWAWAY scratch of D1_s3a_focus_ind.vi, deleted in this run)
  open the scratch                     -> exec_state   (expect 1; it is the bed, untouched)
  diag_index(#639) re-read live        -> 46
  resolve #10407 and #10686 to Nodes[] positions on that diagram, each VERIFIED by its own uid echo
    (NOT via owner_of: review section 5 caught owner_of returning the PREVIOUS query's object, silently)
  connect_nested_v1(46, <#10407 idx>, 0, 46, <#10686 idx>, 0)   -> wire_delta MUST be 0 (already wired)
  exec_state

  ExecState 0 + wire_delta 0  =>  the op alone poisons this bed; `B1_f` carries ZERO information.
  ExecState 1 + wire_delta 0  =>  the op does not poison this bed; the 0 at :82 was a genuine verdict.
  EITHER READING IS A RESULT. Nothing is decided here and no route is chosen.

WHAT THIS IS NOT
  No delete, no Local, no move_in, no save (`g.save` is never called), no VI run (34(f) - OP VIs are run, the
  fleet's normal mechanism), no GUI action, no motor / ASI / camera (rig assembled), no new process device.
  `remove_bad_wires_scripted` / `remove_bad_wires` / `gui_save` neither imported nor called; `allow_broken`
  never True. No route chosen or recommended; docs/cycle27-plan.md and STATUS `## NEXT` untouched.

PREDICTION CONTRACT
  N_a  the scratch opens COLD at ExecState 1
  N_b  #10407 and #10686 both resolve on Diagram #639 with their own uid echoed back
  N_c  #10407 t0 and #10686 t0 BOTH already carry wire 10799 (the pair is already joined)
  N_d  *** wire_delta == 0 *** (the connect is idempotent - nothing is added)
  N_e  *** THE READING: ExecState after the idempotent connect *** (no expected value is asserted; 0 and 1
       are both results, and the gate records which)
  Z_*  the four md5 pins hold; the donor is byte-unchanged; the scratch exists=False; refs/handles reported
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
from build_d1_v0 import diag_index                                                 # noqa: E402
from build_opconnectnested_v1 import connect_nested_v1 as CONNECT_V1               # noqa: E402
import build_opconnectnested_v1 as CN1                                             # noqa: E402
from hash_probe import probe as HASH                                               # noqa: E402

BENCH = os.path.join(ROOT, "tools", "bench")
ORIGINAL, ORIG_MD5 = D.ORIGINAL, D.ORIG_MD5
S1_ARTEFACT, S1_MD5 = D.S1_ARTEFACT, D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S3A_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s3a_focus_ind.vi")
S3A_MD5 = "eef91c1d91f16b034707e4d1285ca8cb"
DONOR = os.path.join(g.CLAUDEDEV, "OpCreateLocalRead_v0.vi")
DONOR_MD5 = "f695d97a36ae127cd2dd3ca6b1fc1089"

STAMP = time.strftime("%Y%m%d_%H%M%S")
OUT = os.path.join(BENCH, "diag_c62_negctrl.json")
V1_LABELS = json.load(open(os.path.join(BENCH, "opconnectnested_v1_labels.json"), encoding="utf-8"))
SCRATCH = os.path.join(g.CLAUDEDEV, "SCRATCH_C62NEG_%s.vi" % STAMP)

CASE_UID, SRC_UID, D639, WIRE_PIN = 10407, 10686, 639, 10799

T_START = time.time()
passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "task": "cycle 62 material #4: the NEGATIVE CONTROL from archive/peer/2026-09-21-c62-movein-es0.md s6",
     "no_new_verb": True, "no_new_op": True, "no_recipe": True, "no_new_device": True,
     "gscript_not_edited": True, "nothing_saved": True, "move_in": "not imported, not called",
     "no_gui_action": True, "no_vi_run": "no D1 artefact and no main VI is run (34(f))",
     "rig_state": "assembled - no motor, no ASI, no camera",
     "chooses_no_route": True, "recommends_no_route": True,
     "remove_bad_wires_scripted": "not imported, not called", "remove_bad_wires": "not imported, not called",
     "gui_save": "NEVER called", "allow_broken": "NEVER True",
     "handles": {}, "hash_probe": [], "exec_state_timeline": []}


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    print(("  %s  %s%s" % ("PASS" if ok else "FAIL", name, ("  " + detail) if detail else ""))
          .encode("ascii", "replace").decode("ascii"), flush=True)
    if not ok and fatal:
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


def read_exec_state(tag, target):
    try:
        es = g.exec_state(target)
    except Exception as e:                                                         # noqa: BLE001
        es = "ERROR %s: %s" % (type(e).__name__, str(e)[:120])
    R["exec_state_timeline"].append({"step": len(R["exec_state_timeline"]) + 1, "tag": tag, "value": es})
    fact("ExecState [%d %s] = %r" % (len(R["exec_state_timeline"]), tag, es))
    return es


def node_on_639(target, d639, uid, tag):
    """Nodes[] position of `uid` on Diagram #639, VERIFIED by the node's own uid echo.

    Deliberately NOT via owner_of: archive/peer/2026-09-21-c62-movein-es0.md section 5 caught owner_of
    answering a Local query with the PREVIOUS query's object, silently, on a file where the uid did not exist.
    """
    rec = {"uid": uid}
    try:
        rows = g.node_labels(target, int(d639))
        rec["nodes_on_639"] = len(rows)
    except Exception as e:                                                         # noqa: BLE001
        rows = []
        rec["node_labels_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
    n = next((i for i, r in enumerate(rows) if r["uid"] == uid), None)
    rec["nodes_index"] = n
    rec["label"] = next((r["label"] for r in rows if r["uid"] == uid), None)
    terms = []
    if n is not None:
        try:
            echo, trows = g.node_terms_uid(target, int(d639), n)
            rec["uid_echo"] = echo
            if echo == uid:
                terms = [{"i": t["i"], "name": t["name"], "is_source": t["is_source"], "wire": t["wire"],
                          "errs": [t["name_err"], t["src_err"], t["conn_err"], t["wire_err"]]}
                         for t in trows]
                rec["how"] = "node_labels position (verified by the node's own UID)"
            else:
                rec["how"] = "REJECTED: Nodes[%d] echoed %r, not %r" % (n, echo, uid)
        except Exception as e:                                                     # noqa: BLE001
            rec["how"] = "ERROR %s: %s" % (type(e).__name__, str(e)[:250])
    else:
        rec["how"] = "NOT IN Diagram.Nodes[] (%d nodes listed)" % len(rows)
    rec["terminal_rows"] = terms
    fact("%s #%d on Diagram #639: Nodes[%r] label %r [%s] ; t0 %r"
         % (tag, uid, n, rec.get("label"), rec.get("how"),
            next((t for t in terms if t["i"] == 0), None)))
    R.setdefault("nodes", {})[str(uid)] = rec
    return rec


def main():
    print("=== diag_c62_negctrl  %s" % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    print("=== THE NEGATIVE CONTROL: does OpConnectNested_v1 alone drive this bed 1 -> 0?", flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])

    o = probe("T1 ORIGINAL (read-only probe)", ORIGINAL)
    gate("T1 the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"), fatal=True)
    s1 = probe("T1b D1_s1_copy.vi", S1_ARTEFACT)
    gate("T1b D1_s1_copy.vi md5 == %s" % S1_MD5, s1.get("md5") == S1_MD5, s1.get("md5", "?"))
    s2 = probe("T2 D1_s2_loops.vi", S2_ARTEFACT)
    gate("T2 D1_s2_loops.vi md5 == %s" % S2_MD5, s2.get("md5") == S2_MD5, s2.get("md5", "?"), fatal=True)
    s3 = probe("T3 D1_s3a_focus_ind.vi (the bed, never written)", S3A_ARTEFACT)
    gate("T3 D1_s3a_focus_ind.vi md5 == %s" % S3A_MD5, s3.get("md5") == S3A_MD5, s3.get("md5", "?"),
         fatal=True)
    dn = probe("T4 the donor OpCreateLocalRead_v0.vi", DONOR)
    gate("T4 OpCreateLocalRead_v0.vi md5 == %s" % DONOR_MD5, dn.get("md5") == DONOR_MD5, dn.get("md5", "?"))

    D.fresh("T5 RESTART (pre-batch, 44(e))")
    R["handles"]["after_restart"] = labview_handles()
    fact("LabVIEW handles AFTER the pre-batch restart: %r" % R["handles"]["after_restart"])
    dump()

    shutil.copy2(S3A_ARTEFACT, SCRATCH)
    try:
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        es0 = read_exec_state("[0] the untouched scratch, cold", SCRATCH)
        gate("N_a the scratch opens COLD at ExecState 1", es0 == 1, "%r" % (es0,))

        try:
            d639 = diag_index(SCRATCH, D639)
            R["d639"] = d639
        except Exception as e:                                                     # noqa: BLE001
            d639 = None
            R["d639_error_verbatim"] = "%s: %s" % (type(e).__name__, str(e)[:250])
        fact("diag_index(#639) RE-READ off the machine = %r" % (d639,))

        sink = node_on_639(SCRATCH, d639, CASE_UID, "SINK") if isinstance(d639, int) else {}
        src = node_on_639(SCRATCH, d639, SRC_UID, "SOURCE") if isinstance(d639, int) else {}
        gate("N_b both #10407 and #10686 resolve on Diagram #639 with their own uid echoed back",
             sink.get("uid_echo") == CASE_UID and src.get("uid_echo") == SRC_UID,
             "sink Nodes[%r] echo %r ; source Nodes[%r] echo %r"
             % (sink.get("nodes_index"), sink.get("uid_echo"), src.get("nodes_index"),
                src.get("uid_echo")), fatal=True)
        st0 = next((t for t in sink.get("terminal_rows", []) if t["i"] == 0), {})
        sr0 = next((t for t in src.get("terminal_rows", []) if t["i"] == 0), {})
        gate("N_c #10407 t0 and #10686 t0 BOTH already carry wire %d" % WIRE_PIN,
             st0.get("wire") == WIRE_PIN and sr0.get("wire") == WIRE_PIN,
             "sink t0 %r ; source t0 %r" % (st0, sr0))

        wires_before = g.count(SCRATCH, "Wire")
        es_pre = read_exec_state("[1] immediately BEFORE the idempotent connect", SCRATCH)
        R["exec_state_before_connect"] = es_pre
        call = ("connect_nested_v1(target, %r, %r, 0, %r, %r, 0)"
                % (d639, sink.get("nodes_index"), d639, src.get("nodes_index")))
        R["call"] = call
        fact("THE ONE CALL: %s   (IDEMPOTENT - this pair is already joined by wire %d)" % (call, WIRE_PIN))
        buf = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf):
                dw, es_c, err_c = CONNECT_V1(SCRATCH, d639, sink.get("nodes_index"), 0,
                                             d639, src.get("nodes_index"), 0, V1_LABELS)
            R["connect_result"] = {"wire_delta": dw, "exec_state_returned": es_c, "error_verbatim": err_c}
        except Exception as e:                                                     # noqa: BLE001
            R["connect_result"] = {"wire_delta": None, "exec_state_returned": None,
                                   "error_verbatim": "EXCEPTION %s: %s" % (type(e).__name__, str(e)[:400])}
        op_out = buf.getvalue().rstrip().splitlines()
        for ln in op_out:
            print(("      [op stdout] " + ln).encode("ascii", "replace").decode("ascii"), flush=True)
        R["op_embedded_is_broken_lines"] = [ln.strip() for ln in op_out if "Is Broken?" in ln]
        fact("connect result: %r" % (R["connect_result"],))
        fact("the op's OWN embedded `Is Broken?` readback line(s) in this run: %r"
             % (R["op_embedded_is_broken_lines"],))

        wires_after = g.count(SCRATCH, "Wire")
        R["wire_census"] = {"before": wires_before, "after": wires_after}
        gate("N_d *** wire_delta == 0 (the connect added nothing; the Wire census is unchanged) ***",
             R["connect_result"].get("wire_delta") == 0 and wires_before == wires_after,
             "wire_delta %r ; Wire census %r -> %r"
             % (R["connect_result"].get("wire_delta"), wires_before, wires_after))

        es_post = read_exec_state("[2] immediately AFTER the idempotent connect", SCRATCH)
        R["exec_state_after_connect"] = es_post
        R["verdict"] = ("THE OP ALONE DRIVES THIS BED 1 -> 0: B1_f in diag_c62_s3b_movein.log carries ZERO "
                        "information about the construction"
                        if (es_pre == 1 and es_post == 0) else
                        "THE OP DOES NOT POISON THIS BED: the 0 in diag_c62_s3b_movein.log:82 is a genuine "
                        "verdict and a structural cause is worth hunting"
                        if (es_pre == 1 and es_post == 1) else
                        "NEITHER ROW OF THE REVIEW'S TABLE: es_pre=%r es_post=%r" % (es_pre, es_post))
        gate("N_e *** THE READING: ExecState %r -> %r across the idempotent connect ***" % (es_pre, es_post),
             True, R["verdict"])
        fact("VERDICT (a reading, not a decision): %s" % R["verdict"])
    finally:
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                     # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, str(e)[:160]))
        if os.path.exists(SCRATCH):
            try:
                os.remove(SCRATCH)
            except Exception as e:                                                 # noqa: BLE001
                fact("could not remove the scratch: %s" % (e,))
        R["scratch_exists"] = os.path.exists(SCRATCH)
        gate("Z_3 the scratch is deleted in the same run", not R["scratch_exists"], SCRATCH)

    R["ref_counts"] = g.ref_counts()
    fact("refs %r" % (R["ref_counts"],))
    try:
        g.reset()
    except Exception as e:                                                         # noqa: BLE001
        fact("g.reset raised %s: %s" % (type(e).__name__, e))
    R["handles"]["after"] = labview_handles()
    fact("LabVIEW handles AFTER everything: %r" % R["handles"]["after"])

    zo = probe("Z1 ORIGINAL after everything", ORIGINAL)
    z1 = probe("Z1b D1_s1_copy.vi after everything", S1_ARTEFACT)
    z2 = probe("Z1c D1_s2_loops.vi after everything", S2_ARTEFACT)
    z3 = probe("Z1d D1_s3a_focus_ind.vi after everything", S3A_ARTEFACT)
    z4 = probe("Z1e the donor OpCreateLocalRead_v0.vi after everything", DONOR)
    gate("Z_1 ORIGINAL / D1_s1_copy / D1_s2_loops / D1_s3a_focus_ind md5 ALL unchanged",
         zo.get("md5") == ORIG_MD5 and z1.get("md5") == S1_MD5 and z2.get("md5") == S2_MD5
         and z3.get("md5") == S3A_MD5,
         "%s / %s / %s / %s" % (zo.get("md5"), z1.get("md5"), z2.get("md5"), z3.get("md5")))
    gate("Z_1b the donor OpCreateLocalRead_v0.vi is byte-unchanged", z4.get("md5") == DONOR_MD5,
         "%s" % (z4.get("md5"),))
    rc = R["ref_counts"] or {}
    gate("Z_1c refs opened == closed, 0 live",
         isinstance(rc, dict) and rc.get("live", rc.get("open", 1)) in (0, None), repr(rc))
    fact("THE COMPLETE ExecState TIMELINE: %r" % (R["exec_state_timeline"],))

    dump()
    print("\n=== GATES %d pass / %d fail%s" % (len(passes), len(fails),
                                               ("; failing: " + ", ".join(fails)) if fails else ""),
          flush=True)
    print("=== readings -> %s" % OUT, flush=True)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
