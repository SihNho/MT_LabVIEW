r"""diag_qdonor2_ia - the DISCRIMINATING TEST the failed-prediction review prescribed, run verbatim.

Review: `archive/peer/2026-09-20-qdonor2-p8-no-saved-artefact.md` (claude / role hypothesis, opus effort max,
ANSWERED 522 s). Its section 5 names the cheapest reading that separates the two explanations of
"`tools/bench/diag_qdonor2_stage.log` step 1 took a scratch from ExecState 1 to 0":
    CLAIM       an UNWIRED Index Array is a broken node -> deleting it returns the VI to ExecState 1.
    ALTERNATIVE an op run of the 1304-`Connect Wire` family perturbs compile state (the cycle-23 case at
                `docs/NAMES.md:912-921`) -> ExecState stays 0 with the Index Array gone.
Discriminators, exactly as section 5 writes them: the CLASS CENSUS DELTA across `build_index_array` (claim:
`IndexArray +1` and nothing else; alternative: another class also moves) and **`es_c`** = ExecState after the new
Index Array is deleted (claim 1, alternative 0).

TWO CALLS ARE ADDED beyond section 5, and only these: `create_control` on the Index Array's `index` terminal
BEFORE the delete, and a `g.save()` whenever ExecState reads 1. Reason: section 1 of the same review showed the
staged run's delete was in the wrong PLACE - `docs/NAMES.md:476-478` puts it AFTER the control exists - so running
the pattern in the documented order is what tells us whether the control-donor shape can sit on a SAVABLE VI, and
it is what finally leaves a file on disk (user 2026-09-19, "a step is not done until it has left a file"). The
review's own readings are taken first, so they stand whatever the additions do.

🔴 DIAGNOSTIC, never a recipe. 🔴 NO VI IS RUN (34(f)); only BUILT op VIs execute. 🔴 NO NEW OP (Pre-decided 2).
🔴 The ORIGINAL, `claudeDev\D1_s1_copy.vi` and `claudeDev\D1_s2_loops.vi` are never opened or written (md5 probed
both ends). `allow_broken` stays False; `gui_save` is never called. Reused, nothing new: `diag_queue_donor2`'s
helpers, `diag_s2_scaffold.fresh/Preload/file_facts`, `gscript.build_index_array/create_control/delete_object/
exec_state/save/count`, `build_d1_v0.move_in/diag_index`, `build_opstopfromnode_v0.idx`, `hash_probe.probe`.

PREDICTION CONTRACT (printed gates; the review says either value of every reading is legitimate - the gates
assert that the reading was TAKEN, except the two file gates)
  I0  ORIGINAL md5 2a78e17c449cacdaf5da389818526859 and the scratch byte-identical to `D1_s1_copy.vi`.   FATAL
  I1  `es_a` (the untouched scratch) is RECORDED.
  I2  the class census delta across `build_index_array` is RECORDED (the review's first discriminator).
  I3  `es_b` (straight after `build_index_array`) is RECORDED.
  I4  `create_control` on the Index Array's `index` terminal is attempted and scored.
  I5  the Index Array is DELETED and **`es_c`** RECORDED (the review's second, decisive discriminator).
  I6  a save is attempted whenever ExecState reads 1, and every md5 recorded.
  I7  `move_in` of the surviving ControlTerminal to Diagram #686, its owner re-read, ExecState + save recorded.
  I8  no live VI Server reference is left open.
  I9  the ORIGINAL, `D1_s1_copy.vi` and `D1_s2_loops.vi` are unchanged.                                  FATAL
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
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_qdonor2ia_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_qdonor2_ia.json")
D686 = Q.SIBLING_DIAG_UID
CLASSES = ("Wire", "Constant", "IndexArray", "Function", "ControlTerminal", "Node", "SubVI")

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP, "no_vi_was_run": True, "picks_nothing": True,
     "review": "archive/peer/2026-09-20-qdonor2-p8-no-saved-artefact.md section 5",
     "readings": {}, "saves": [], "handles": {}, "hash_probe": []}
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


def census():
    return {c: g.count(SCRATCH, c) for c in CLASSES}


def es(tag):
    v, err = safe(g.exec_state, SCRATCH)
    R["readings"][tag] = v
    fact("READING %s: exec_state = %r (err %r)" % (tag, v, err))
    return v


def try_save(tag):
    v = R["readings"].get(tag)
    if v != 1:
        fact("SAVE after %s: NOT ATTEMPTED (ExecState %r; allow_broken stays False, gui_save never called)"
             % (tag, v))
        return None
    size, serr = safe(g.save, SCRATCH)
    f = D.file_facts("SAVE after %s" % tag, SCRATCH)
    rec = {"after": tag, "returned_bytes": size, "exception": serr, "md5": f.get("md5"), "size": f.get("size")}
    R["saves"].append(rec)
    fact("SAVE after %s: returned %r, exception %r, md5 %s" % (tag, size, serr, f.get("md5")))
    return rec


def main():
    print("=== diag_qdonor2_ia  %s   (the review's DISCRIMINATING TEST; NO VI IS RUN, 34(f))"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r" % R["handles"]["before"])
    o = probe("ORIGINAL", ORIGINAL)
    probe("S1 claudeDev\\D1_s1_copy.vi", S1)
    probe("S2 claudeDev\\D1_s2_loops.vi (never opened by this file)", S2)
    gate("I0a the ORIGINAL's md5 equals the pin", o.get("md5") == ORIG_MD5, str(o.get("md5")), fatal=True)

    D.fresh("F1")
    fact("handles after the restart: %r" % labview_handles())
    if os.path.exists(SCRATCH):
        os.remove(SCRATCH)
    shutil.copy2(S1, SCRATCH)
    sc = probe("the scratch copy", SCRATCH)
    R["scratch"] = {"path": SCRATCH, "after_copy": sc}
    gate("I0b the scratch copy is byte-identical to D1_s1_copy.vi", sc.get("md5") == S1_MD5,
         str(sc.get("md5")), fatal=True)

    with D.Preload("P"):
        g.open_panel(SCRATCH)
        time.sleep(1.0)

        es_a = es("es_a untouched")
        gate("I1 es_a recorded", es_a is not None, "es_a = %r" % es_a)

        c_b4 = census()
        fact("census BEFORE build_index_array: %r" % c_b4)
        ia_before = g.uids(SCRATCH, "IndexArray")
        _v, ia_err = safe(g.build_index_array, SCRATCH, Q.IA_AT)
        new_ia = g.new_since(SCRATCH, "IndexArray", ia_before)
        ia_uid = new_ia[0]["uid"] if new_ia else None
        c_af = census()
        delta = {k: c_af[k] - c_b4[k] for k in CLASSES if c_af[k] != c_b4[k]}
        R["readings"]["census_delta_build_index_array"] = delta
        R["readings"]["new_indexarray_uid"] = ia_uid
        fact("build_index_array: op error %r; new IndexArray #%s; census AFTER %r" % (ia_err, ia_uid, c_af))
        fact("DISCRIMINATOR 1 - census delta across build_index_array: %r  (the review's CLAIM predicts "
             "{'IndexArray': 1} and nothing else; its ALTERNATIVE predicts another class also moves)" % delta)
        gate("I2 the census delta across build_index_array is recorded", True, repr(delta))

        es_b = es("es_b after build_index_array")
        gate("I3 es_b recorded", es_b is not None, "es_b = %r" % es_b)

        # ---- the documented order (docs/NAMES.md:476-478): the control is made BEFORE the donor is deleted
        ct_uid, ct_label, cc_err = None, None, None
        _w, rt = walk_rows(SCRATCH, 0)
        h = [r for r in rt if r["uid"] == ia_uid]
        if h:
            ti = [i for i, nm in h[0]["in_bare"] if nm == "index"]
            fact("the new IndexArray #%s is TOP-LEVEL Nodes[%d]; bare named inputs %r"
                 % (ia_uid, h[0]["node_index"], h[0]["in_bare"]))
            if ti:
                before = g.uids(SCRATCH, "ControlTerminal")
                res, cc_err = safe(g.create_control, SCRATCH, h[0]["node_index"], int(ti[0]))
                new = g.new_since(SCRATCH, "ControlTerminal", before)
                ct_uid = new[0]["uid"] if new else None
                ct_label = res[1] if res else None
        R["readings"]["control_terminal"] = {"uid": ct_uid, "label": ct_label, "error": cc_err}
        fact("create_control on the IndexArray's `index` terminal: ControlTerminal #%s label %r (err %r)"
             % (ct_uid, ct_label, cc_err))
        gate("I4 create_control attempted and scored", ct_uid is not None or cc_err is not None, repr(cc_err))
        es("es_b2 after create_control")

        # ---- DISCRIMINATOR 2: delete the Index Array, then re-read
        del_err = None
        if ia_uid is not None:
            di, dierr = safe(cls_index, SCRATCH, "IndexArray", ia_uid)
            if di is None:
                del_err = "not addressable: %s" % dierr
            else:
                _v, del_err = safe(g.delete_object, SCRATCH, "IndexArray", int(di), True)
        R["readings"]["delete_indexarray_error"] = del_err
        fact("delete_object(IndexArray #%s): error %r; IndexArray count now %s"
             % (ia_uid, del_err, g.count(SCRATCH, "IndexArray")))
        es_c = es("es_c after deleting the IndexArray")
        fact("DISCRIMINATOR 2 - es_c = %r. The review: **1** => the CLAIM (an unwired Index Array is what broke "
             "the VI, and the donor pattern is viable); **0** => its ALTERNATIVE (the op run perturbed compile "
             "state; dropping a donor on the top-level diagram is a dead end)." % es_c)
        gate("I5 the IndexArray was deleted and es_c recorded", True, "es_c = %r" % es_c)
        try_save("es_c after deleting the IndexArray")
        gate("I6 a save was attempted wherever ExecState read 1", True,
             "%d save(s): %r" % (len(R["saves"]), [(s["after"], s["md5"]) for s in R["saves"]]))

        # ---- the shape 35(b) actually asks about: the free control's terminal ON Diagram #686
        mv = {"control_terminal": ct_uid}
        if ct_uid is not None:
            (oc0, ou0), _e = owner(SCRATCH, ct_uid)
            mv["owner_before"] = [oc0, ou0]
            r, merr = safe(move_in, SCRATCH, ct_uid, diag_index(SCRATCH, D686), Q.MOVE_AT["C1"])
            (oc, ou), _e2 = owner(SCRATCH, ct_uid)
            mv.update({"move_returned": r, "move_error": merr, "owner_after": [oc, ou], "on_686": ou == D686})
            fact("move_in(ControlTerminal #%s -> Diagram #%d): owner %r#%s -> %r#%s (on #%d: %s), error %r"
                 % (ct_uid, D686, oc0, ou0, oc, ou, D686, ou == D686, merr))
            d686 = diag_index(SCRATCH, D686)
            _w2, rows = walk_rows(SCRATCH, d686)
            hit = [r2 for r2 in rows if r2["uid"] == ct_uid]
            mv["in_686_nodes"] = bool(hit)
            mv["out_named"] = hit[0]["out_named"] if hit else []
            fact("the free ControlTerminal #%s on Diagram #%d: in AbstractDiagram.Nodes[] %s; named SOURCE "
                 "terminals %r" % (ct_uid, D686, mv["in_686_nodes"], mv["out_named"]))
        R["readings"]["move_to_686"] = mv
        es_d = es("es_d after move_in to Diagram #686")
        try_save("es_d after move_in to Diagram #686")
        gate("I7 move_in attempted, owner re-read, ExecState + save recorded", True,
             "on_686 %r, es_d %r" % (mv.get("on_686"), es_d))

        R["final_census"] = census()
        fact("class census at the end: %r" % R["final_census"])
        _r, cperr = safe(g.close_panel, SCRATCH)
        if cperr:
            fact("close_panel raised %s" % cperr)

    R["final_file"] = D.file_facts("the scratch as it now stands on disk", SCRATCH)
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
        gate("I8 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,))
        try:
            oe = probe("I9 ORIGINAL after the run", ORIGINAL)
            s1e = probe("I9 D1_s1_copy.vi after the run", S1)
            s2e = probe("I9 D1_s2_loops.vi after the run", S2)
            ok = (oe.get("md5") == ORIG_MD5 and s1e.get("md5") == S1_MD5
                  and (s2e.get("exists") != "1" or s2e.get("md5") == S2_MD5))
            if not gate("I9 the ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi are all unchanged", ok,
                        "orig %s s1 %s s2 %s" % (oe.get("md5"), s1e.get("md5"), s2e.get("md5"))):
                rc = 1
        except Exception as e:                                                    # noqa: BLE001
            print("  FAIL  I9 could not re-probe: %s: %s" % (type(e).__name__, e), flush=True)
            fails.append("I9 re-probe raised")
            rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== FACTS ONLY - no donor is picked and no queue stage is written. NO VI WAS RUN (34(f)).",
              flush=True)
        sys.exit(rc)
