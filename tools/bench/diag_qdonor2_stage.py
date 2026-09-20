r"""diag_qdonor2_stage - the SAVED-ARTEFACT half of Pre-decided 35(b) round 2.

WHY THIS EXISTS. `tools/bench/diag_queue_donor2.py` took every reading the brief asked for (16/0) but ended
`ExecState 0`, so `g.save()` refused and the run left no artefact anyone can open - the pinned rule "a step is not
done until it has left a file" (user, 2026-09-19) unmet, and no attribution of WHICH edit broke the copy. This
file replays ONLY the shape-1 edits, one at a time, reading `exec_state` and attempting a `g.save()` after each,
so (a) the last runnable state is ON DISK with its md5 and (b) the breaking step is named by measurement instead
of by inference. It adds no new measurement of its own and repeats none of round 2's queue/const attempts: the
positive control that mutates WhileLoop #637's body is deliberately NOT replayed.

🔴 DIAGNOSTIC, never a recipe. 🔴 NO VI IS RUN (34(f)); the only VIs that execute are BUILT op VIs. 🔴 NO NEW OP
(Pre-decided 2). 🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never opened or
written; md5s probed at both ends. `allow_broken` stays False and `gui_save` is never called.

REUSED, nothing new: `diag_queue_donor2.walk_rows/safe/owner`, `diag_s2_scaffold.fresh/Preload/file_facts`,
`gscript.build_index_array/create_control/drop_subvi/queue_node/exec_state/save`, `build_d1_v0.move_in/diag_index`,
`build_opstopfromnode_v0.idx`, `hash_probe.probe`, `bench_prep.labview_handles`.

PREDICTION CONTRACT (printed gates)
  P0  ORIGINAL md5 2a78e17c449cacdaf5da389818526859; the scratch is byte-identical to `D1_s1_copy.vi`.   FATAL
  P1..P7 each step is APPLIED and its `exec_state` + save outcome RECORDED (either value legitimate; the
      point is the reading, not a particular value).
  P8  at least one step left a SAVED file whose md5 differs from `D1_s1_copy.vi`'s (the artefact the rule wants).
  P9  no live VI Server reference is left open.
  P10 the ORIGINAL, `D1_s1_copy.vi` and `D1_s2_loops.vi` are unchanged.                                  FATAL
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
import diag_queue_donor2 as Q                                                     # noqa: E402
from bench_prep import labview_handles                                            # noqa: E402
from build_d1_v0 import move_in, diag_index                                       # noqa: E402
from build_opstopfromnode_v0 import idx as cls_index                              # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL, ORIG_MD5, S1, S1_MD5 = Q.ORIGINAL, Q.ORIG_MD5, Q.S1, Q.S1_MD5
S2, S2_MD5 = Q.S2, Q.S2_MD5
STAMP = time.strftime("%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_qdonor2s_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_qdonor2_stage.json")
D686 = Q.SIBLING_DIAG_UID

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "no_vi_was_run": True, "picks_nothing": True,
     "steps": [], "handles": {}, "hash_probe": []}
safe, owner, walk_rows = Q.safe, Q.owner, Q.walk_rows


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=False):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (2026-09-20, cycle 53): the bold form is invisible to guard_peer's FAILURE_RE anchor.
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
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(R, f, indent=1, default=str)


def step(tag, what, fn):
    """Apply one edit, then READ exec_state and TRY to save. Every outcome is a reading."""
    val, err = safe(fn)
    es, eerr = safe(g.exec_state, SCRATCH)
    size, serr = (None, None)
    md5 = None
    if es == 1:
        size, serr = safe(g.save, SCRATCH)
        md5 = (probe("%s saved artefact" % tag, SCRATCH) or {}).get("md5")
    rec = {"step": tag, "what": what, "returned": val, "edit_error": err, "exec_state": es,
           "exec_error": eerr, "saved_bytes": size, "save_error": serr, "md5_after_save": md5}
    R["steps"].append(rec)
    fact("STEP %s (%s): edit error %r -> ExecState %r; save %s"
         % (tag, what, err, es, ("returned %r, md5 %s" % (size, md5)) if es == 1
            else "NOT ATTEMPTED (ExecState != 1; allow_broken stays False)"))
    gate("P-%s applied and its ExecState + save outcome recorded" % tag, True,
         "ExecState %r, md5 %r" % (es, md5))
    return rec


def main():
    print("=== diag_qdonor2_stage  %s   (the SAVED-ARTEFACT half of 35(b) round 2; NO VI IS RUN, 34(f))"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    o = probe("ORIGINAL", ORIGINAL)
    s1 = probe("S1 claudeDev\\D1_s1_copy.vi", S1)
    probe("S2 claudeDev\\D1_s2_loops.vi (never opened by this file)", S2)
    gate("P0a the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, str(o.get("md5")), fatal=True)

    D.fresh("F1")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S1, SCRATCH)
    sc = probe("the scratch copy", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "after_copy": sc}
    gate("P0b the scratch copy is byte-identical to D1_s1_copy.vi", sc.get("md5") == S1_MD5,
         str(sc.get("md5")), fatal=True)

    state = {}
    with D.Preload("P"):
        g.open_panel(SCRATCH)
        time.sleep(1.0)
        es0, _e = safe(g.exec_state, SCRATCH)
        fact("the untouched scratch reads ExecState %r with the ORIGINAL preloaded" % es0)

        def s1_ia():
            before = g.uids(SCRATCH, "IndexArray")
            g.build_index_array(SCRATCH, Q.IA_AT)
            new = g.new_since(SCRATCH, "IndexArray", before)
            state["ia_uid"] = new[0]["uid"] if new else None
            return state["ia_uid"]
        step("1", "build_index_array on the TOP-LEVEL diagram (the scalar control's helper)", s1_ia)

        def s2_ctl():
            _w, rt = walk_rows(SCRATCH, 0)
            h = [r for r in rt if r["uid"] == state.get("ia_uid")]
            if not h:
                raise RuntimeError("the new IndexArray is not on the top-level Nodes[] walk")
            ti = [i for i, nm in h[0]["in_bare"] if nm == "index"]
            before = g.uids(SCRATCH, "ControlTerminal")
            _res, lab = g.create_control(SCRATCH, h[0]["node_index"], int(ti[0]))
            new = g.new_since(SCRATCH, "ControlTerminal", before)
            state["ct1"] = new[0]["uid"] if new else None
            return {"uid": state["ct1"], "label": lab, "node_index": h[0]["node_index"], "term": ti[:1]}
        step("2", "create_control on that IndexArray's `index` terminal (SCALAR I32 control)", s2_ctl)

        def s3_move():
            u = state.get("ct1")
            if not u:
                raise RuntimeError("no scalar ControlTerminal to move")
            r = move_in(SCRATCH, u, diag_index(SCRATCH, D686), Q.MOVE_AT["C1"])
            (oc, ou), _e = owner(SCRATCH, u)
            return {"move_returned": r, "owner_after": [oc, ou], "on_686": ou == D686}
        step("3", "move_in the SCALAR ControlTerminal into Diagram #%d" % D686, s3_move)

        def s4_drop():
            before = g.uids(SCRATCH, "SubVI")
            g.drop_subvi(SCRATCH, Q.NUMVI, 0, Q.SUBVI_AT)
            new = g.new_since(SCRATCH, "SubVI", before)
            state["sv_uid"] = new[0]["uid"] if new else None
            return state["sv_uid"]
        step("4", "drop_subvi(Error Cluster From Error Code.vi) on the TOP-LEVEL diagram", s4_drop)

        def s5_ctl2():
            _w, rt = walk_rows(SCRATCH, 0)
            h = [r for r in rt if r["uid"] == state.get("sv_uid")]
            if not h:
                raise RuntimeError("the dropped subVI is not on the top-level Nodes[] walk")
            ti = [i for i, nm in h[0]["in_bare"] if nm == "error in (no error)"]
            before = g.uids(SCRATCH, "ControlTerminal")
            _res, lab = g.create_control(SCRATCH, h[0]["node_index"], int(ti[0]))
            new = g.new_since(SCRATCH, "ControlTerminal", before)
            state["ct2"] = new[0]["uid"] if new else None
            return {"uid": state["ct2"], "label": lab, "node_index": h[0]["node_index"], "term": ti[:1]}
        step("5", "create_control on its `error in (no error)` terminal (NON-SCALAR cluster control)", s5_ctl2)

        def s6_move():
            u = state.get("ct2")
            if not u:
                raise RuntimeError("no cluster ControlTerminal to move")
            r = move_in(SCRATCH, u, diag_index(SCRATCH, D686), Q.MOVE_AT["C2"])
            (oc, ou), _e = owner(SCRATCH, u)
            return {"move_returned": r, "owner_after": [oc, ou], "on_686": ou == D686}
        step("6", "move_in the NON-SCALAR ControlTerminal into Diagram #%d" % D686, s6_move)

        def s7_queue():
            d686 = diag_index(SCRATCH, D686)
            _w, rows = walk_rows(SCRATCH, d686)
            base = [r for r in rows if r["uid"] == Q.BASELINE_OPERAND[0]]
            if not base:
                raise RuntimeError("the baseline donor #%d is not on Diagram #%d" % (Q.BASELINE_OPERAND[0], D686))
            ci = cls_index(SCRATCH, base[0]["class_guess"], Q.BASELINE_OPERAND[0])
            return g.queue_node("obtain", SCRATCH, base[0]["class_guess"], int(ci), Q.BASELINE_OPERAND[1],
                                d686, Q.QN_AT["BASE"])
        step("7", "the baseline Obtain Queue on Diagram #%d from #%d %r"
             % (D686, Q.BASELINE_OPERAND[0], Q.BASELINE_OPERAND[1]), s7_queue)

        R["final_census"] = {c: g.count(SCRATCH, c) for c in
                             ("Diagram", "WhileLoop", "SubVI", "Function", "Constant", "ControlTerminal",
                              "Wire", "IndexArray")}
        fact("class census at the end: %r" % R["final_census"])
        _r, cperr = safe(g.close_panel, SCRATCH)
        if cperr:
            fact("close_panel raised %s" % cperr)

    saved = [s for s in R["steps"] if s["md5_after_save"] and s["md5_after_save"] != S1_MD5]
    R["last_saved"] = saved[-1] if saved else None
    R["final_file"] = D.file_facts("the scratch as it now stands on disk", SCRATCH)
    broke = next((s for s in R["steps"] if s["exec_state"] != 1), None)
    R["first_breaking_step"] = broke
    fact("STEPS THAT SAVED: %r" % [(s["step"], s["md5_after_save"]) for s in saved])
    fact("FIRST step whose ExecState was not 1: %r"
         % ({k: broke[k] for k in ("step", "what", "exec_state", "edit_error")} if broke else None))
    gate("P8 at least one step left a SAVED artefact distinct from D1_s1_copy.vi", bool(saved),
         "saved steps %r" % [s["step"] for s in saved])
    dump()


if __name__ == "__main__":
    rc = 0
    try:
        main()
    except Stop as s:
        print("\nSTOPPED at a FATAL gate: %s" % s, flush=True)
        rc = 1
    except Exception:                                                             # noqa: BLE001
        import traceback
        traceback.print_exc()
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
        gate("P9 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        try:
            oe = probe("P10 ORIGINAL after the run", ORIGINAL)
            s1e = probe("P10 D1_s1_copy.vi after the run", S1)
            s2e = probe("P10 D1_s2_loops.vi after the run", S2)
            ok = (oe.get("md5") == ORIG_MD5 and s1e.get("md5") == S1_MD5
                  and (s2e.get("exists") != "1" or s2e.get("md5") == S2_MD5))
            if not gate("P10 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are all unchanged", ok,
                        "orig %s s1 %s s2 %s" % (oe.get("md5"), s1e.get("md5"), s2e.get("md5"))):
                rc = 1
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  P10 could not re-probe: %s: %s" % (type(e).__name__, e), flush=True)
            fails.append("P10 re-probe raised")
            rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== FACTS ONLY - no donor is picked and no queue stage is written. NO VI WAS RUN (34(f)).",
              flush=True)
        sys.exit(rc)
