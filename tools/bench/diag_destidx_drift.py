r"""diag_destidx_drift - CYCLE 53 TEST B: does `dest_diagram_index` DRIFT inside one script?

A DIAGNOSTIC, never a recipe (it lives under tools/bench/, not tools/recipes/). It MEASURES and
CHOOSES NOTHING: no boundary, no decomposition, no disposition.

THE QUESTION.  `move_in(target, uid, dest_diagram_index, position)` (`tools/recipes/build_d1_v0.py:318`,
line :325 `vi.SetControlValue("index", int(dest_diagram_index))`) addresses its DESTINATION by TRAVERSE
INDEX, not by uid.  If relocating a structure renumbers the `Traverse for GObjects` Diagram array, every
later `dest_diagram_index` in a multi-move script is silently wrong and the op cannot report it.  That is
34(h)'s address-invalidation hypothesis located in an op signature; this run measures it.

WHAT ALREADY EXISTS AND IS REUSED - checked before writing a line (`grep "^def " tools/gscript.py`,
`ls tools/recipes tools/bench`, `docs/toolkit-capabilities.md`).  NOTHING NEW IS BUILT:
  * `build_d1_v0.move_in` :318 / `owner_of` :338 / `diag_index` :357  - the BUILT mover and the two
    uid-addressed readers.  `move_in` is NOT in tools/gscript.py (which has only `move_out` :2674 and
    `move_object` :2299).
  * `gscript.report_all(target, "Diagram")` :488  - the whole Diagram traverse array in ONE op run;
    `diag_index` is literally `[o["uid"] for o in report_all(...)].index(uid)` (:358), so reading that
    list IS reading the address space `move_in` uses.
  * `gscript.count` :1005, `gscript.open_panel` :1241, `gscript.close_panel` :1257, `gscript.save` :2062.
  * `diag_s2_scaffold.fresh` :155 / `.Preload` :167 / `.read_state` :343 / `.try_save` :351 - cycle 50's
    measured harness (in-instance ExecState under Preload, 34(l); save with allow_broken=False).
  * `bench_prep.labview_handles`; `hash_probe.probe` (34(k), read-only md5/sha256/size).
  * `diag_movein_set.py` (cycle 52) is the pattern this file follows; its gate() prints `FAIL`, not
    `**FAIL**` (37(i)), and so does this one.

PREDICTION CONTRACT - every line is a printed GATE; the DRIFT readings are REPORTED, never predicted.
  B1  the ORIGINAL exists, md5 2a78e17c449cacdaf5da389818526859.                                   FATAL
  B2  `claudeDev\D1_s2_loops.vi` md5 6ff19497f2309e007a214660bb64b911 BEFORE the copy.             FATAL
  B3  the dated scratch is byte-identical to it.                                                   FATAL
  B4  baseline census on the scratch == the verified S2 numbers (Diagram 173, WhileLoop 6, ...).    FATAL
  B5  both #23058 (loop a's body) and #639 (WhileLoop #637's body) are IN the Diagram traverse list,
      and `owner_of(#3529)` reads #639 before any move.                                        non-fatal
  B6  move 1 (#3529 -> #23058) is CALLED; its echoed uid is recorded.  No outcome predicted.    REPORTED
  B7  after move 1: the whole traverse list, the two indices, owner_of(#3529), Diagram count.   REPORTED
  B8  what the STALE pre-move index of #23058 would now address, if a script had cached it.     REPORTED
  B9  move 2 (#3560 -> #23058, index RE-READ at the call site per 34(h)) and the same three reads. REPORTED
  B10 ExecState in-instance with the ORIGINAL preloaded (34(l)).                                REPORTED
  B11 ONE g.save() attempt with the DEFAULT allow_broken=False; `gui_save` is NEVER called.
      Whether it is reachable is the READING.  The scratch is NEVER named D1_s3_loop15.vi.      REPORTED
  B12 no live VI Server reference is left open.                                                non-fatal
  B13 ORIGINAL, D1_s1_copy.vi and D1_s2_loops.vi md5s unchanged at the end.                        FATAL

NO VI IS RUN (34(f)).  No new op (Pre-decided 2; user 2026-09-18 08:53).  No motor, no ASI, no camera,
no GUI action.  Every edit lands on a DATED SCRATCH copy unique to this run.

  py tools/bgrun.py --material --max-min 15 --log tools/bench/diag_destidx_drift.log \
      -- py -u tools/bench/diag_destidx_drift.py
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
from build_d1_v0 import move_in, owner_of                                         # noqa: E402
from hash_probe import probe as HASH                                              # noqa: E402

ORIGINAL = D.ORIGINAL
ORIG_MD5 = D.ORIG_MD5
S1_ARTEFACT = D.S1_ARTEFACT
S1_MD5 = D.S1_MD5
S2_ARTEFACT = os.path.join(g.CLAUDEDEV, "D1_s2_loops.vi")
S2_MD5 = "6ff19497f2309e007a214660bb64b911"
S2_SIZE = 475707
STAMP = time.strftime("%Y%m%d_%H%M%S")
SCRATCH = os.path.join(g.CLAUDEDEV, "DIAG_destidx_%s.vi" % STAMP)
OUT = os.path.join(HERE, "diag_destidx_drift.json")

DEST_BODY = 23058          # loop a's body Diagram (37(h)); loop a is WhileLoop #23032
FRAME_BODY = 639           # WhileLoop #637's body - where the whole 1.5 FOCUS set lives
MOVE_1 = 3529              # ControlReferenceConstant `- Inc (PgDn)` - 1 wired terminal, the cheapest
MOVE_2 = 3560              # ControlReferenceConstant `+ Inc (PgUp)` - 1 wired terminal
BASELINE = {"Diagram": 173, "WhileLoop": 6, "SubVI": 97, "Comparison": 17, "LoopTunnel": 135, "Wire": 1905}

passes, fails, facts = [], [], []
R = {"script": os.path.abspath(__file__), "stamp": STAMP,
     "measurement": "B (does dest_diagram_index drift inside one script?)",
     "no_vi_was_run": True, "chooses_nothing": True,
     "original": {"path": ORIGINAL, "md5_pin": ORIG_MD5},
     "s2_artefact": {"path": S2_ARTEFACT, "md5_pin": S2_MD5},
     "scratch": {"path": SCRATCH},
     "stages": [], "handles": {}, "hash_probe": []}


class Stop(Exception):
    pass


def gate(name, ok, detail="", fatal=True):
    (passes if ok else fails).append(name)
    # `FAIL`, NOT `**FAIL**` (37(i)): the bold form is invisible to guard_peer's FAILURE_RE anchor.
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


def diagram_list(target):
    """The WHOLE Diagram traverse array, in the exact order `diag_index`/`move_in` address it."""
    return [int(o["uid"]) for o in g.report_all(target, "Diagram")]


def idx_of(lst, uid):
    return lst.index(uid) if uid in lst else None


def owner_read(target, uid):
    try:
        cls, own = owner_of(target, uid)
        return {"uid": uid, "owner_class": cls, "owner_uid": int(own), "error": None}
    except Exception as e:                                                        # noqa: BLE001
        return {"uid": uid, "owner_class": None, "owner_uid": None,
                "error": "%s: %s" % (type(e).__name__, e)}


def reading(tag, target, prev_list=None, stale=None):
    """The three things the brief asks for after every move, plus the whole list for the diff."""
    lst = diagram_list(target)
    n = g.count(target, "Diagram")
    rec = {"tag": tag, "diagram_class_count": n, "traverse_len": len(lst),
           "idx_%d" % DEST_BODY: idx_of(lst, DEST_BODY),
           "idx_%d" % FRAME_BODY: idx_of(lst, FRAME_BODY),
           "owner_of_%d" % MOVE_1: owner_read(target, MOVE_1),
           "owner_of_%d" % MOVE_2: owner_read(target, MOVE_2),
           "traverse_list": lst}
    fact("%s: Diagram class count %d, traverse array length %d, index(#%d)=%s, index(#%d)=%s"
         % (tag, n, len(lst), DEST_BODY, rec["idx_%d" % DEST_BODY], FRAME_BODY, rec["idx_%d" % FRAME_BODY]))
    fact("%s: owner_of(#%d) = %s #%s%s | owner_of(#%d) = %s #%s%s"
         % (tag, MOVE_1, rec["owner_of_%d" % MOVE_1]["owner_class"], rec["owner_of_%d" % MOVE_1]["owner_uid"],
            (" ERR " + str(rec["owner_of_%d" % MOVE_1]["error"])[:60])
            if rec["owner_of_%d" % MOVE_1]["error"] else "",
            MOVE_2, rec["owner_of_%d" % MOVE_2]["owner_class"], rec["owner_of_%d" % MOVE_2]["owner_uid"],
            (" ERR " + str(rec["owner_of_%d" % MOVE_2]["error"])[:60])
            if rec["owner_of_%d" % MOVE_2]["error"] else ""))
    if prev_list is not None:
        moved = [(i, p, c) for i, (p, c) in enumerate(zip(prev_list, lst)) if p != c]
        added = [u for u in lst if u not in prev_list]
        removed = [u for u in prev_list if u not in lst]
        rec["diff_vs_prev"] = {"n_positions_changed": len(moved), "first_10_changed": moved[:10],
                               "added_uids": added, "removed_uids": removed,
                               "same_set": sorted(prev_list) == sorted(lst),
                               "same_order": prev_list == lst}
        fact("%s vs previous: same_set=%s same_order=%s positions_changed=%d added=%s removed=%s"
             % (tag, rec["diff_vs_prev"]["same_set"], rec["diff_vs_prev"]["same_order"],
                len(moved), added, removed))
    if stale is not None:
        was_idx, was_uid = stale
        now = lst[was_idx] if (was_idx is not None and 0 <= was_idx < len(lst)) else "OUT-OF-RANGE"
        rec["stale_index_probe"] = {"cached_index": was_idx, "meant_diagram_uid": was_uid,
                                    "that_index_now_addresses": now,
                                    "still_correct": now == was_uid}
        fact("%s STALE-INDEX PROBE: a script that cached dest_diagram_index=%s (meaning Diagram #%s) would "
             "now address Diagram #%s -> still correct: %s"
             % (tag, was_idx, was_uid, now, now == was_uid))
    R["stages"].append(rec)
    return rec


def main():
    print("=== diag_destidx_drift  %s   (TEST B; NO VI IS RUN, 34(f); no new op)"
          % time.strftime("%Y-%m-%d %H:%M:%S"), flush=True)
    R["handles"]["before"] = labview_handles()
    fact("LabVIEW handles BEFORE: %r (fresh-instance baseline ~31,500)" % R["handles"]["before"])
    fact("move_in addresses its DESTINATION by TRAVERSE INDEX: build_d1_v0.py:325 "
         "`vi.SetControlValue(\"index\", int(dest_diagram_index))`; diag_index :358 is "
         "`[o['uid'] for o in report_all(target,'Diagram')].index(uid)`.")

    o = probe("B1 ORIGINAL (read-only probe, 34(k))", ORIGINAL)
    gate("B1 the ORIGINAL exists and its md5 equals the pin", o.get("md5") == ORIG_MD5, o.get("md5", "?"))
    s = probe("B2 the S2 artefact BEFORE the copy", S2_ARTEFACT)
    gate("B2 D1_s2_loops.vi md5 == %s and size == %d B" % (S2_MD5, S2_SIZE),
         s.get("md5") == S2_MD5 and s.get("size") == str(S2_SIZE),
         "md5 %s size %s" % (s.get("md5"), s.get("size")))

    D.fresh("B2b")
    fact("handles after the restart: %r" % labview_handles())
    shutil.copy2(S2_ARTEFACT, SCRATCH)
    t = probe("B3 the dated scratch", SCRATCH)
    gate("B3 the scratch is byte-identical to the S2 artefact", t.get("md5") == S2_MD5, t.get("md5", "?"))

    with D.Preload("B"):
        g.open_panel(SCRATCH)                       # required before ANY scripting edit (skill rule)
        time.sleep(1.0)
        c0 = {k: g.count(SCRATCH, k) for k in BASELINE}
        R["census_before"] = c0
        fact("class census BEFORE any edit: %r" % c0)
        gate("B4 baseline census == the verified S2 numbers %r" % BASELINE,
             all(c0[k] == v for k, v in BASELINE.items()), repr(c0))

        print("\n--- step 1: the FULL Diagram traverse list, BEFORE any move", flush=True)
        r0 = reading("BEFORE", SCRATCH)
        i0_dest = r0["idx_%d" % DEST_BODY]
        i0_frame = r0["idx_%d" % FRAME_BODY]
        gate("B5 #%d and #%d are both in the Diagram traverse list, and owner_of(#%d) reads #%d"
             % (DEST_BODY, FRAME_BODY, MOVE_1, FRAME_BODY),
             i0_dest is not None and i0_frame is not None
             and r0["owner_of_%d" % MOVE_1]["owner_uid"] == FRAME_BODY,
             "idx(#%d)=%s idx(#%d)=%s owner_of(#%d)=%s#%s"
             % (DEST_BODY, i0_dest, FRAME_BODY, i0_frame, MOVE_1,
                r0["owner_of_%d" % MOVE_1]["owner_class"], r0["owner_of_%d" % MOVE_1]["owner_uid"]),
             fatal=False)

        # ------------------------------------------------------------------ move 1
        print("\n--- step 2: move 1 of 2  #%d -> Diagram #%d (traverse index %s, re-read now, 34(h))"
              % (MOVE_1, DEST_BODY, i0_dest), flush=True)
        m1 = {"step": "move1", "moved_uid": MOVE_1, "dest_uid": DEST_BODY,
              "dest_index_used": i0_dest, "position": [60, 500]}
        try:
            m1["echoed_uid"] = move_in(SCRATCH, MOVE_1, i0_dest, (60, 500))
            fact("move 1: move_in(#%d -> Diagram #%d [index %s] at (60,500)) echoed uid %r"
                 % (MOVE_1, DEST_BODY, i0_dest, m1["echoed_uid"]))
        except Exception as e:                                                    # noqa: BLE001
            m1["error"] = "%s: %s" % (type(e).__name__, e)
            fact("move 1 RAISED %s: %s" % (type(e).__name__, e))
        R.setdefault("moves", []).append(m1)
        gate("B6 move 1 was CALLED and its result recorded (REPORTED, no outcome predicted)", True,
             repr(m1.get("echoed_uid", m1.get("error"))), fatal=False)

        print("\n--- step 3: RE-READ the whole traverse list and both indices", flush=True)
        r1 = reading("AFTER move 1", SCRATCH, prev_list=r0["traverse_list"], stale=(i0_dest, DEST_BODY))
        gate("B7 the three post-move-1 readings are recorded (REPORTED)", True,
             "idx(#%d) %s -> %s ; idx(#%d) %s -> %s ; Diagram count %d -> %d"
             % (DEST_BODY, i0_dest, r1["idx_%d" % DEST_BODY], FRAME_BODY, i0_frame,
                r1["idx_%d" % FRAME_BODY], r0["diagram_class_count"], r1["diagram_class_count"]),
             fatal=False)
        drift1 = (r1["idx_%d" % DEST_BODY] != i0_dest) or (r1["idx_%d" % FRAME_BODY] != i0_frame)
        gate("B8 DRIFT after move 1 = %s (REPORTED, never a requirement)" % drift1, True,
             "stale probe: %r" % (r1.get("stale_index_probe"),), fatal=False)

        # ------------------------------------------------------------------ move 2
        i1_dest = r1["idx_%d" % DEST_BODY]
        print("\n--- step 4: move 2 of 2  #%d -> Diagram #%d (traverse index %s, RE-READ at the call site)"
              % (MOVE_2, DEST_BODY, i1_dest), flush=True)
        m2 = {"step": "move2", "moved_uid": MOVE_2, "dest_uid": DEST_BODY,
              "dest_index_used": i1_dest, "stale_index_a_script_would_have_used": i0_dest,
              "position": [60, 620]}
        try:
            m2["echoed_uid"] = move_in(SCRATCH, MOVE_2, i1_dest, (60, 620))
            fact("move 2: move_in(#%d -> Diagram #%d [index %s] at (60,620)) echoed uid %r"
                 % (MOVE_2, DEST_BODY, i1_dest, m2["echoed_uid"]))
        except Exception as e:                                                    # noqa: BLE001
            m2["error"] = "%s: %s" % (type(e).__name__, e)
            fact("move 2 RAISED %s: %s" % (type(e).__name__, e))
        R["moves"].append(m2)
        r2 = reading("AFTER move 2", SCRATCH, prev_list=r1["traverse_list"], stale=(i0_dest, DEST_BODY))
        gate("B9 the three post-move-2 readings are recorded (REPORTED)", True,
             "idx(#%d) %s -> %s ; idx(#%d) %s -> %s ; Diagram count %d -> %d ; owner_of(#%d)=#%s owner_of(#%d)=#%s"
             % (DEST_BODY, i1_dest, r2["idx_%d" % DEST_BODY], FRAME_BODY, r1["idx_%d" % FRAME_BODY],
                r2["idx_%d" % FRAME_BODY], r1["diagram_class_count"], r2["diagram_class_count"],
                MOVE_1, r2["owner_of_%d" % MOVE_1]["owner_uid"], MOVE_2, r2["owner_of_%d" % MOVE_2]["owner_uid"]),
             fatal=False)

        R["verdict"] = {
            "idx_dest_body": [i0_dest, r1["idx_%d" % DEST_BODY], r2["idx_%d" % DEST_BODY]],
            "idx_frame_body": [i0_frame, r1["idx_%d" % FRAME_BODY], r2["idx_%d" % FRAME_BODY]],
            "diagram_class_count": [r0["diagram_class_count"], r1["diagram_class_count"],
                                    r2["diagram_class_count"]],
            "traverse_len": [r0["traverse_len"], r1["traverse_len"], r2["traverse_len"]],
            "same_order_after_move1": r1.get("diff_vs_prev", {}).get("same_order"),
            "same_order_after_move2": r2.get("diff_vs_prev", {}).get("same_order"),
            "stale_index_still_correct_after_move1": (r1.get("stale_index_probe") or {}).get("still_correct"),
            "stale_index_still_correct_after_move2": (r2.get("stale_index_probe") or {}).get("still_correct"),
        }
        fact("VERDICT idx(#%d) across the run: %r ; idx(#%d): %r ; Diagram count: %r ; traverse order unchanged "
             "after move1/move2: %r/%r"
             % (DEST_BODY, R["verdict"]["idx_dest_body"], FRAME_BODY, R["verdict"]["idx_frame_body"],
                R["verdict"]["diagram_class_count"], R["verdict"]["same_order_after_move1"],
                R["verdict"]["same_order_after_move2"]))

        # ------------------------------------------------------------------ ExecState + one save attempt
        print("\n--- step 5: ExecState in-instance under Preload (34(l)), then ONE save attempt", flush=True)
        es = D.read_state("B10_after_two_moves_in_instance_preloaded", SCRATCH)
        R["exec_state_after_moves"] = es
        gate("B10 ExecState after the two moves = %r (1 = runnable, 0 = broken) - REPORTED" % es, True,
             "", fatal=False)
        sv = D.try_save("destidx", SCRATCH)
        R["save"] = sv
        R["save_reachable"] = sv["exception"] is None and bool(sv["returned_bytes"])
        gate("B11 g.save() reachable with allow_broken=False (gui_save NEVER called): %s - REPORTED"
             % R["save_reachable"], True,
             "returned %r exception %r" % (sv["returned_bytes"], sv["exception"]), fatal=False)
        try:
            g.close_panel(SCRATCH)
        except Exception as e:                                                    # noqa: BLE001
            fact("close_panel raised %s: %s" % (type(e).__name__, e))
    probe("B11 the scratch on disk, final", SCRATCH)
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
        gate("B12 no live VI Server reference is left open", bool(refs) and not refs.get("live"),
             "ref_counts %r" % (refs,), fatal=False)
        for tag, path, pin in (("ORIGINAL", ORIGINAL, ORIG_MD5), ("D1_s1_copy.vi", S1_ARTEFACT, S1_MD5),
                               ("D1_s2_loops.vi", S2_ARTEFACT, S2_MD5)):
            d = probe("B13 %s after the run" % tag, path)
            R.setdefault("untouched", {})[tag] = d.get("md5")
            ok = d.get("md5") == pin
            gate("B13 %s md5 unchanged" % tag, ok, d.get("md5", "?") if ok else "%s != %s" % (d.get("md5"), pin),
                 fatal=False)
            if not ok:
                rc = 1
        dump()
        print("\n=== GATES: %d pass / %d fail%s"
              % (len(passes), len(fails), ("; failing: " + "; ".join(fails)) if fails else ""), flush=True)
        print("=== READINGS json: %s" % OUT, flush=True)
        print("=== SCRATCH: %s" % SCRATCH, flush=True)
        print("=== NO VI WAS RUN (34(f)); no new op; no motor, no ASI, no camera, no GUI action.", flush=True)
        sys.exit(rc)
